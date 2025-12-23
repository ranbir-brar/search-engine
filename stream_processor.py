import sys
import json
import uuid
import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct, VectorParams, Distance

# --- Configuration ---
KAFKA_BOOTSTRAP_SERVERS = "kafka:9092"
KAFKA_TOPIC = "news_stream"
QDRANT_HOST = "qdrant"
QDRANT_PORT = 6333
COLLECTION_NAME = "news_articles"
KAFKA_BOOTSTRAP_SERVERS = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "kafka:29092")
KAFKA_TOPIC = "news_stream"

schema = StructType([
    StructField("title", StringType()),
    StructField("url", StringType()),
    StructField("source", StringType()),
    StructField("content", StringType()),
    StructField("published", StringType())
])

def chunk_text(text, words_per_chunk=150, overlap=30):
    """
    Splits long text into overlapping chunks.
    Overlap ensures we don't cut a sentence in half at a crucial boundary.
    """
    words = text.split()
    chunks = []
    if len(words) <= words_per_chunk:
        return [text]
        
    for i in range(0, len(words), words_per_chunk - overlap):
        chunk = " ".join(words[i:i + words_per_chunk])
        chunks.append(chunk)
    return chunks

def process_batch(df, epoch_id):
    # Materialize the batch to a list of rows
    rows = df.collect()
    if not rows:
        return

    print(f"Processing batch {epoch_id} with {len(rows)} articles...")
    sys.stdout.flush()

    # Initialize clients inside the executor/worker context
    try:
        model = SentenceTransformer("all-MiniLM-L6-v2")
        client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
        
        # Ensure collection exists (only create if not exists)
        try:
             client.get_collection(COLLECTION_NAME)
        except:
             print("Creating collection...")
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
            
        # 1. Chunk the article
        chunks = chunk_text(row.content)
        print(f"Article '{row.title}' split into {len(chunks)} chunks.")
        
        for i, chunk_text_str in enumerate(chunks):
            try:
                # 2. Embed the chunk
                vector = model.encode(chunk_text_str).tolist()
                
                # 3. Create Payload (Metadata)
                payload = {
                    "title": row.title,
                    "url": row.url,
                    "source": row.source,
                    "content": chunk_text_str, 
                    "full_article_preview": row.content[:200], # Context
                    "chunk_index": i
                }

                # 4. Create Point
                points.append(PointStruct(
                    id=str(uuid.uuid4()),
                    vector=vector,
                    payload=payload
                ))
            except Exception as e:
                print(f"Error embedding chunk: {e}")
    
    # 5. Upsert to Qdrant
    if points:
        try:
            client.upsert(
                collection_name=COLLECTION_NAME,
                points=points
            )
            print(f"Successfully upserted {len(points)} chunks to Qdrant.")
            sys.stdout.flush()
        except Exception as e:
            print(f"Failed to upsert to Qdrant: {e}")

def main():
    spark = SparkSession.builder \
        .appName("TechBlogStreamProcessor") \
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0") \
        .getOrCreate()

    spark.sparkContext.setLogLevel("WARN")

    # Read from Kafka
    df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS) \
        .option("subscribe", KAFKA_TOPIC) \
        .option("startingOffsets", "earliest") \
        .load()

    # Parse JSON
    parsed_df = df.select(from_json(col("value").cast("string"), schema).alias("data")).select("data.*")

    # Process
    query = parsed_df.writeStream \
        .foreachBatch(process_batch) \
        .start()

    query.awaitTermination()

if __name__ == "__main__":
    main()