#!/bin/bash

echo "===== Neural Search Engine Diagnostics ====="
echo ""

echo "1. Checking Docker containers..."
docker-compose ps
echo ""

echo "2. Checking Kafka health..."
docker exec kafka kafka-broker-api-versions --bootstrap-server localhost:9092 2>/dev/null && echo "✓ Kafka is healthy" || echo "✗ Kafka is not responding"
echo ""

echo "3. Listing Kafka topics..."
docker exec kafka kafka-topics --bootstrap-server localhost:9092 --list
echo ""

echo "4. Checking if news_stream topic has data..."
MESSAGE_COUNT=$(docker exec kafka kafka-run-class kafka.tools.GetOffsetShell \
  --broker-list localhost:9092 \
  --topic news_stream 2>/dev/null | awk -F: '{sum += $3} END {print sum}')
echo "Messages in topic: ${MESSAGE_COUNT:-0}"
echo ""

echo "5. Sampling 3 messages from news_stream..."
docker exec kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic news_stream \
  --from-beginning \
  --max-messages 3 \
  --timeout-ms 5000 2>/dev/null || echo "No messages found or timeout"
echo ""

echo "6. Checking producer logs (last 10 lines)..."
docker-compose logs --tail=10 producer
echo ""

echo "7. Checking spark-dev container status..."
docker exec spark-dev python --version 2>/dev/null && echo "✓ Python is available" || echo "✗ Cannot access Python"
docker exec spark-dev bash -c "pip list | grep -E '(pyspark|sentence-transformers|kafka)'" 2>/dev/null
echo ""

echo "===== Diagnostics Complete ====="
echo ""
echo "Next steps:"
echo "1. If everything looks good, run: docker exec -it spark-dev bash"
echo "2. Then inside container: spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0 stream_processor.py"