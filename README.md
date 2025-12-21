# Distributed Real-Time Neural Search Engine

This is a minimal, end-to-end scaffold for a Kafka -> Spark -> FAISS streaming semantic search pipeline.

## Quick start

1) Start Kafka, Zookeeper, and Spark:

```bash
docker compose up -d
```

2) Install Python deps in a virtualenv, then run the producer:

```bash
python producer.py
```

3) Start the FastAPI server (used for vector indexing and search):

```bash
uvicorn server:app --reload --port 8000
```

4) Run the Spark stream processor (requires the Kafka connector):

```bash
spark-submit \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0 \
  stream_processor.py
```

## Environment variables

- `KAFKA_BOOTSTRAP_SERVERS` (default `localhost:9092`)
- `KAFKA_TOPIC` (default `news_stream`)
- `PRODUCER_RATE` (default `10`)
- `VECTOR_API_URL` (default empty; set to `http://localhost:8000` to enable indexing)
- `CHECKPOINT_DIR` (default `checkpoints/stream_processor`)
- `FAISS_INDEX_PATH` (default `data/index.faiss`)
- `FAISS_IDS_PATH` (default `data/index_ids.json`)

## Example search

```bash
curl "http://localhost:8000/search?q=latest+ai+chips"
```
