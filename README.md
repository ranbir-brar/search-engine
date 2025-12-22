# Neural Search Engine Setup Guide

## Key Changes Made

### 1. **Fixed Kafka Connection**

- Changed default `KAFKA_BOOTSTRAP_SERVERS` from `localhost:9092` to `kafka:29092`
- This is the internal Docker network address that containers use to communicate

### 2. **Added Docker Networking**

- All services now share a `search-network` bridge network
- Added health checks for Kafka to ensure it's ready before dependent services start

### 3. **Improved Debugging**

- Added verbose logging throughout the stream processor
- Added delivery confirmations in the producer
- Shows sample records being processed

### 4. **Added Processing Trigger**

- Set `processingTime="5 seconds"` to ensure batches are processed regularly
- This prevents the streaming job from appearing stuck

## Setup Instructions

### Step 1: Prepare Your Files

Make sure you have these files in your project directory:

```
your-project/
├── docker-compose.yml
├── Dockerfile.producer
├── producer.py
├── stream_processor.py
└── README.md (this file)
```

### Step 2: Start the Infrastructure

```bash
# Start Kafka and Zookeeper
docker-compose up -d zookeeper kafka

# Wait about 30 seconds for Kafka to be fully ready
sleep 30

# Start Spark dev container
docker-compose up -d spark-dev

# Start the producer (generates fake news articles)
docker-compose up -d producer
```

### Step 3: Verify Everything is Running

```bash
# Check all containers are running
docker-compose ps

# You should see:
# - zookeeper (healthy)
# - kafka (healthy)
# - spark-dev (running)
# - producer (running)
```

### Step 4: Check the Producer

```bash
# View producer logs to see articles being generated
docker-compose logs -f producer

# You should see messages like:
# [1] Producing: Exactly morning forget station...
# ✓ Delivered to news_stream [0] @ offset 0
```

### Step 5: Run the Stream Processor

```bash
# Enter the Spark container
docker exec -it spark-dev bash

# Inside the container, run the stream processor
spark-submit \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0 \
  stream_processor.py
```

### What You Should See

The stream processor will:

1. Connect to Kafka: `Connecting to Kafka at kafka:29092, topic: news_stream`
2. Load the embedding model: `Loading Model inside Executor...`
3. Start processing batches every 5 seconds:
   ```
   >>> Processing batch 0 with 25 records...
   >>> Sample records:
   +--------------------+--------------------+---------+
   |id                  |title               |category |
   +--------------------+--------------------+---------+
   |uuid-here           |Some news title...  |AI       |
   ```

## Troubleshooting

### If Kafka Connection Fails

```bash
# Check if Kafka is accessible from spark-dev
docker exec -it spark-dev bash
apt-get update && apt-get install -y kafkacat
kafkacat -b kafka:29092 -L
```

### If the Model Loading Takes Too Long

The first time you run this, it will download the sentence-transformers model (~90MB). This is normal and only happens once.

### If You See "No DataFrame in Result"

This means no data is flowing. Check:

1. Producer is running: `docker-compose logs producer`
2. Kafka has data: `docker exec -it kafka kafka-console-consumer --bootstrap-server localhost:9092 --topic news_stream --from-beginning --max-messages 5`

### Check Kafka Topics

```bash
# List all topics
docker exec -it kafka kafka-topics --bootstrap-server localhost:9092 --list

# Read from the topic
docker exec -it kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic news_stream \
  --from-beginning \
  --max-messages 10
```

## Testing Different Rates

```bash
# Increase production rate to 20 messages/sec
docker-compose stop producer
PRODUCER_RATE=20 docker-compose up -d producer
```

## Cleanup

```bash
# Stop all services
docker-compose down

# Remove all data (including checkpoints)
docker-compose down -v
rm -rf checkpoints/
```

## Next Steps

### Add a Vector Database

Once this is working, you can add a vector database like:

- **Qdrant**: Lightweight vector search
- **Milvus**: Scalable vector database
- **Weaviate**: Cloud-native vector search

Example with Qdrant:

```yaml
# Add to docker-compose.yml
qdrant:
  image: qdrant/qdrant:latest
  ports:
    - "6333:6333"
  networks:
    - search-network
```

Then set: `VECTOR_API_URL=http://qdrant:6333`

### Add a Search API

Create a FastAPI service that:

1. Takes user queries
2. Embeds them using the same model
3. Searches the vector database
4. Returns relevant articles

## Architecture Overview

```
Producer → Kafka → Spark Streaming → Embeddings → Vector DB
                                                        ↓
                                    User Query → Search API → Results
```

## Performance Tips

1. **Batch Size**: Adjust trigger interval based on data volume
2. **Parallelism**: Increase Spark executors for higher throughput
3. **Checkpointing**: The checkpoint directory enables exactly-once processing
4. **Memory**: Increase driver/executor memory if processing large batches
