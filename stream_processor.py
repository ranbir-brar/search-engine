"""
Atlas Academic Search Engine - Spark Stream Processor
Consumes academic resources from Kafka, embeds them, and stores in Qdrant.
"""
import sys
import json
import uuid
import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType, ArrayType
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct, VectorParams, Distance

# --- Configuration ---
KAFKA_BOOTSTRAP_SERVERS = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "kafka:29092")
KAFKA_TOPIC = "news_stream"
QDRANT_HOST = "qdrant"
QDRANT_PORT = 6333
COLLECTION_NAME = "atlas_resources"  # Renamed for Atlas

# Updated schema for Atlas academic resources
schema = StructType([
    StructField("title", StringType()),
    StructField("summary", StringType()),
    StructField("authors", ArrayType(StringType())),
    StructField("url", StringType()),
    StructField("source", StringType()),
    StructField("resource_type", StringType()),
    StructField("published", StringType()),
    StructField("content", StringType())  # Combined title + summary for embedding
])


def chunk_text(text, words_per_chunk=150, overlap=30):
    """
    Splits long text into overlapping chunks.
    """
    if not text:
        return []
    words = text.split()
    if len(words) <= words_per_chunk:
        return [text]
        
    chunks = []
    for i in range(0, len(words), words_per_chunk - overlap):
        chunk = " ".join(words[i:i + words_per_chunk])
        chunks.append(chunk)
    return chunks


def process_batch(df, epoch_id):
    rows = df.collect()
    if not rows:
        return

    print(f"📚 Processing batch {epoch_id} with {len(rows)} resources...")
    sys.stdout.flush()

    try:
        model = SentenceTransformer("all-MiniLM-L6-v2")
        client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
        
        # Ensure collection exists
        try:
            client.get_collection(COLLECTION_NAME)
        except:
            print("Creating Atlas collection...")
            client.recreate_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE),
            )
    except Exception as e:
        print(f"Error initializing resources: {e}")
        return

    points = []
    
    for row in rows:
        if not row.content or not row.title:
            continue
        
        # Chunk the content
        chunks = chunk_text(row.content)
        resource_type = row.resource_type or "Paper"
        
        print(f"[{resource_type}] '{row.title[:50]}...' -> {len(chunks)} chunks")
        
        for i, chunk_text_str in enumerate(chunks):
            try:
                vector = model.encode(chunk_text_str).tolist()
                
                # Store all Atlas metadata for filtering
                payload = {
                    "title": row.title,
                    "url": row.url,
                    "source": row.source,
                    "resource_type": resource_type,
                    "authors": row.authors or [],
                    "published": row.published,
                    "content": chunk_text_str,
                    "summary_preview": (row.summary or "")[:300],
                    "chunk_index": i
                }

                points.append(PointStruct(
                    id=str(uuid.uuid4()),
                    vector=vector,
                    payload=payload
                ))
            except Exception as e:
                print(f"Error embedding chunk: {e}")
    
    if points:
        try:
            client.upsert(
                collection_name=COLLECTION_NAME,
                points=points
            )
            print(f"✅ Upserted {len(points)} chunks to Qdrant.")
            sys.stdout.flush()
        except Exception as e:
            print(f"❌ Failed to upsert to Qdrant: {e}")


def main():
    spark = SparkSession.builder \
        .appName("AtlasStreamProcessor") \
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0") \
        .getOrCreate()

    spark.sparkContext.setLogLevel("WARN")

    print("🎓 Atlas Stream Processor Starting...")
    print(f"   Kafka: {KAFKA_BOOTSTRAP_SERVERS}")
    print(f"   Topic: {KAFKA_TOPIC}")
    print(f"   Qdrant: {QDRANT_HOST}:{QDRANT_PORT}")

    df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS) \
        .option("subscribe", KAFKA_TOPIC) \
        .option("startingOffsets", "earliest") \
        .load()

    parsed_df = df.select(from_json(col("value").cast("string"), schema).alias("data")).select("data.*")

    query = parsed_df.writeStream \
        .foreachBatch(process_batch) \
        .start()

    query.awaitTermination()


if __name__ == "__main__":
    main()