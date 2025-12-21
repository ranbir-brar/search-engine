import os
from typing import Iterator

import pandas as pd
import requests
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, from_unixtime, pandas_udf, to_timestamp
from pyspark.sql.types import ArrayType, FloatType, LongType, StringType, StructField, StructType
from sentence_transformers import SentenceTransformer

KAFKA_BOOTSTRAP_SERVERS = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
TOPIC = os.environ.get("KAFKA_TOPIC", "news_stream")
CHECKPOINT_DIR = os.environ.get("CHECKPOINT_DIR", "checkpoints/stream_processor")
VECTOR_API_URL = os.environ.get("VECTOR_API_URL", "")
_MODEL = None


def build_spark_session() -> SparkSession:
    return (
        SparkSession.builder.appName("neural-search-stream-processor")
        .config("spark.sql.execution.arrow.pyspark.enabled", "true")
        .getOrCreate()
    )


@pandas_udf(ArrayType(FloatType()))
def embed_texts(texts_iter: Iterator[pd.Series]) -> Iterator[pd.Series]:
    global _MODEL
    if _MODEL is None:
        _MODEL = SentenceTransformer("all-MiniLM-L6-v2")
    for texts in texts_iter:
        embeddings = _MODEL.encode(
            texts.fillna("").tolist(),
            show_progress_bar=False,
            convert_to_numpy=True,
        )
        yield pd.Series([vector.tolist() for vector in embeddings])


def write_to_sinks(batch_df, batch_id: int) -> None:
    print(f"Writing batch {batch_id} to Snowflake...")

    if not VECTOR_API_URL:
        print("Vector sink skipped; set VECTOR_API_URL to enable indexing.")
        return

    records = batch_df.select("id", "embedding_vector").collect()
    if not records:
        return

    payload = {
        "items": [
            {"id": record["id"], "vector": record["embedding_vector"]}
            for record in records
        ]
    }

    try:
        response = requests.post(
            f"{VECTOR_API_URL.rstrip('/')}/index/batch", json=payload, timeout=10
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        print(f"Vector sink error: {exc}")


def main() -> None:
    spark = build_spark_session()

    schema = StructType(
        [
            StructField("id", StringType(), True),
            StructField("title", StringType(), True),
            StructField("content", StringType(), True),
            StructField("timestamp", LongType(), True),
            StructField("category", StringType(), True),
        ]
    )

    raw_df = (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS)
        .option("subscribe", TOPIC)
        .option("startingOffsets", "latest")
        .load()
    )

    parsed_df = (
        raw_df.selectExpr("CAST(value AS STRING) AS json_str")
        .select(from_json(col("json_str"), schema).alias("data"))
        .select("data.*")
    )

    with_time = parsed_df.withColumn(
        "event_time", to_timestamp(from_unixtime(col("timestamp")))
    )

    with_watermark = with_time.withWatermark("event_time", "10 minutes")

    embedded_df = with_watermark.withColumn(
        "embedding_vector", embed_texts(col("content"))
    )

    query = (
        embedded_df.writeStream.outputMode("append")
        .foreachBatch(write_to_sinks)
        .option("checkpointLocation", CHECKPOINT_DIR)
        .start()
    )

    query.awaitTermination()


if __name__ == "__main__":
    main()
