import asyncio
import json
import os
import random
import time
import uuid

from confluent_kafka import Producer
from faker import Faker

TOPIC = os.environ.get("KAFKA_TOPIC", "news_stream")
BOOTSTRAP_SERVERS = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
RATE_PER_SEC = int(os.environ.get("PRODUCER_RATE", "10"))

CATEGORIES = ["AI", "Crypto", "Cloud", "Security", "Mobile", "Startups", "Hardware"]

faker = Faker()


def delivery_report(err, msg):
    if err is not None:
        print(f"Delivery failed: {err}")


def generate_article():
    category = random.choice(CATEGORIES)
    return {
        "id": str(uuid.uuid4()),
        "title": faker.sentence(nb_words=8),
        "content": faker.paragraph(nb_sentences=5),
        "timestamp": int(time.time()),
        "category": category,
    }


async def produce_loop(producer: Producer) -> None:
    interval = 1.0 / max(RATE_PER_SEC, 1)
    while True:
        article = generate_article()
        producer.produce(
            TOPIC,
            key=article["category"].encode("utf-8"),
            value=json.dumps(article).encode("utf-8"),
            on_delivery=delivery_report,
        )
        producer.poll(0)
        await asyncio.sleep(interval)


def main() -> None:
    producer = Producer(
        {
            "bootstrap.servers": BOOTSTRAP_SERVERS,
            "client.id": "tech-news-producer",
        }
    )
    try:
        asyncio.run(produce_loop(producer))
    except KeyboardInterrupt:
        print("Stopping producer...")
    finally:
        producer.flush(5)


if __name__ == "__main__":
    main()
