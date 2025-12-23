"""
Atlas Academic Search Engine - Producer
Orchestrates multiple collectors to ingest academic resources into Kafka.
"""
import os
import json
import time
from kafka import KafkaProducer
from collectors.arxiv_collector import ArxivCollector
from collectors.ocw_collector import OCWCollector
from collectors.stanford_collector import StanfordCollector
from collectors.harvard_collector import HarvardCollector
from collectors.yale_collector import YaleCollector


# --- Kafka Configuration ---
KAFKA_BOOTSTRAP_SERVERS = os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
KAFKA_TOPIC = 'atlas_resources'

# --- Collection Configuration ---
COLLECTION_INTERVAL = 300  # 5 minutes between collection runs
ITEMS_PER_COLLECTOR = 100  # Max items per collector per run


def main():
    print("Starting Atlas Academic Resource Collector...")
    print(f"   Kafka: {KAFKA_BOOTSTRAP_SERVERS}")
    print(f"   Topic: {KAFKA_TOPIC}")
    print(f"   Interval: {COLLECTION_INTERVAL}s")
    print()

    # Initialize Kafka Producer
    producer = KafkaProducer(
        bootstrap_servers=[KAFKA_BOOTSTRAP_SERVERS],
        value_serializer=lambda x: json.dumps(x).encode('utf-8')
    )

    # Initialize Collectors
    collectors = [
        ArxivCollector(),
        OCWCollector(),
        StanfordCollector(),
        HarvardCollector(),
        YaleCollector(),
    ]
    
    print(f"Loaded {len(collectors)} collectors:")
    for c in collectors:
        print(f"   - {c.name}")
    print()

    while True:
        total_collected = 0
        
        for collector in collectors:
            try:
                print(f"\nRunning {collector.name} collector...")
                payloads = collector.collect(limit=ITEMS_PER_COLLECTOR)
                
                for payload in payloads:
                    try:
                        future = producer.send(KAFKA_TOPIC, payload)
                        future.get(timeout=10)  # Block to ensure send
                        total_collected += 1
                    except Exception as ke:
                        print(f"   Kafka send error: {ke}")
                
                print(f"   {collector.name}: Sent {len(payloads)} resources")
                
            except Exception as e:
                print(f"   {collector.name} error: {e}")
        
        producer.flush()
        print(f"\nTotal resources collected this run: {total_collected}")
        print(f"Sleeping for {COLLECTION_INTERVAL // 60} minutes...")
        time.sleep(COLLECTION_INTERVAL)


if __name__ == "__main__":
    main()