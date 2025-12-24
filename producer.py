"""
Atlas Course Materials Search Engine - Producer
Two-bucket architecture for collecting course materials.
"""
import os
import json
import time
from kafka import KafkaProducer
from collectors.ocw_collector import OCWCollector
from collectors.stanford_collector import StanfordCollector
from collectors.harvard_collector import HarvardCollector
from collectors.yale_collector import YaleCollector
from collectors.cmu_collector import CMUCollector
from collectors.github_notes_collector import GitHubNotesCollector


# --- Kafka Configuration ---
KAFKA_BOOTSTRAP_SERVERS = os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
KAFKA_TOPIC = 'atlas_resources'

# --- Collection Configuration ---
COLLECTION_INTERVAL = 300  # 5 minutes between collection runs
ITEMS_PER_COLLECTOR = 500  # Max items per collector per run


def main():
    print("Starting Atlas Course Materials Collector...")
    print(f"   Kafka: {KAFKA_BOOTSTRAP_SERVERS}")
    print(f"   Topic: {KAFKA_TOPIC}")
    print()

    # Initialize Kafka Producer
    producer = KafkaProducer(
        bootstrap_servers=[KAFKA_BOOTSTRAP_SERVERS],
        value_serializer=lambda x: json.dumps(x).encode('utf-8')
    )

    # Two-Bucket Architecture
    collectors = [
        # Bucket A: Deep Crawl - Centralized Open Courseware
        OCWCollector(),        # MIT OpenCourseWare
        YaleCollector(),       # Yale Open Yale Courses
        CMUCollector(),        # CMU Open Learning Initiative
        StanfordCollector(),   # Stanford SEE
        HarvardCollector(),    # Harvard CS50
        
        # Bucket B: GitHub Course Notes
        GitHubNotesCollector(),  # Waterloo, UofT, Stanford, MIT, Berkeley
    ]
    
    print(f"Loaded {len(collectors)} collectors:")
    print("   Bucket A (Centralized Portals):")
    for c in collectors[:5]:
        print(f"      - {c.name}")
    print("   Bucket B (GitHub Repos):")
    for c in collectors[5:]:
        print(f"      - {c.name}")
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
                        future.get(timeout=10)
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