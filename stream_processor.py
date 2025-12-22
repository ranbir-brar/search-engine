import os
from typing import Iterator

import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, pandas_udf
from pyspark.sql.types import ArrayType, FloatType, LongType, StringType, StructField, StructType
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

# --- Configuration ---
KAFKA_BOOTSTRAP_SERVERS = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "kafka:29092")
TOPIC = os.environ.get("KAFKA_TOPIC", "news_stream")
CHECKPOINT_DIR = os.environ.get("CHECKPOINT_DIR", "checkpoints/stream_processor")
QDRANT_URL = os.environ.get("VECTOR_API_URL", "http://qdrant:6333")
COLLECTION_NAME = "news_articles"

# Global model variable for the UDF
_MODEL = None

def build_spark_session() -> SparkSession:
    return (
        SparkSession.builder
        .appName("neural-search-stream-processor")
        .config("spark.sql.execution.arrow.pyspark.enabled", "true")
        .config("spark.driver.memory", "2g")
        .config("spark.executor.memory", "2g")
        .getOrCreate()
    )

@pandas_udf(ArrayType(FloatType()))
def embed_texts(texts_iter: Iterator[pd.Series]) -> Iterator[pd.Series]:
    global _MODEL
    if _MODEL is None:
        print("Loading Model inside Executor...")
        _MODEL = SentenceTransformer("all-MiniLM-L6-v2")
        print("Model loaded successfully!")
    
    for texts in texts_iter:
        text_list = texts.fillna("").tolist()
        print(f"Embedding {len(text_list)} texts...")
        embeddings = _MODEL.encode(
            text_list,
            show_progress_bar=False,
            convert_to_numpy=True,
        )
        yield pd.Series([vector.tolist() for vector in embeddings])

def initialize_qdrant():
    """Create Qdrant collection if it doesn't exist"""
    try:
        client = QdrantClient(url=QDRANT_URL)
        
        # Check if collection exists
        collections = client.get_collections().collections
        if COLLECTION_NAME not in [c.name for c in collections]:
            print(f"Creating collection: {COLLECTION_NAME}")
            client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE),
            )
            print("Collection created successfully!")
        else:
            print(f"Collection {COLLECTION_NAME} already exists")
    except Exception as e:
        print(f"Error initializing Qdrant: {e}")

def write_to_qdrant(batch_df, batch_id: int) -> None:
    count = batch_df.count() 
    print(f">>> Processing batch {batch_id} with {count} records...")

    if count == 0:
        print(">>> Empty batch, skipping.")
        return

    # Show some data for debugging
    print(">>> Sample records:")
    batch_df.select("id", "title", "category").show(5, truncate=False)

    try:
        client = QdrantClient(url=QDRANT_URL)
        
        # Collect all records
        records = batch_df.select("id", "title", "content", "category", "timestamp", "embedding_vector").collect()
        
        # Prepare points for Qdrant
        points = []
        for record in records:
            points.append(
                PointStruct(
                    id=record["id"],
                    vector=record["embedding_vector"],
                    payload={
                        "title": record["title"],
                        "content": record["content"],
                        "category": record["category"],
                        "timestamp": record["timestamp"]
                    }
                )
            )
        
        # Upload to Qdrant
        client.upsert(
            collection_name=COLLECTION_NAME,
            points=points
        )
        print(f">>> Successfully indexed {len(points)} items to Qdrant!")
        
    except Exception as exc:
        print(f">>> Qdrant error: {exc}")

def main() -> None:
    print("Starting Spark session...")
    spark = build_spark_session()
    spark.sparkContext.setLogLevel("ERROR")  # Changed to ERROR to reduce noise

    print("Initializing Qdrant collection...")
    initialize_qdrant()

    schema = StructType([
        StructField("id", StringType(), True),
        StructField("title", StringType(), True),
        StructField("content", StringType(), True),
        StructField("timestamp", LongType(), True),
        StructField("category", StringType(), True),
    ])

    print(f"Connecting to Kafka at {KAFKA_BOOTSTRAP_SERVERS}, topic: {TOPIC}")
    
    raw_df = (
        spark.readStream
        .format("kafka")
        .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS)
        .option("subscribe", TOPIC)
        .option("startingOffsets", "earliest")
        .option("failOnDataLoss", "false")
        .option("kafka.consumer.timeout.ms", "5000")
        .load()
    )

    parsed_df = (
        raw_df.selectExpr("CAST(value AS STRING) AS json_str")
        .select(from_json(col("json_str"), schema).alias("data"))
        .select("data.*")
    )

    print("Creating embedding column...")
    embedded_df = parsed_df.withColumn(
        "embedding_vector", embed_texts(col("content"))
    )

    print("Starting streaming query...")
    query = (
        embedded_df.writeStream
        .outputMode("append")
        .foreachBatch(write_to_qdrant)
        .option("checkpointLocation", CHECKPOINT_DIR)
        .trigger(processingTime="5 seconds")
        .start()
    )

    print("Stream processor is running. Press Ctrl+C to stop.")
    query.awaitTermination()

if __name__ == "__main__":
    main()