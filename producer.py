import time
import json
import feedparser
from kafka import KafkaProducer
from bs4 import BeautifulSoup
import ssl

if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

# A curated list of high-quality engineering blogs
RSS_FEEDS = [
    "https://netflixtechblog.com/feed",
    "https://www.uber.com/blog/engineering/rss/",
    "https://medium.com/airbnb-engineering/feed",
    "https://instagram-engineering.com/feed",
    "https://engineering.atspotify.com/feed/",
    "https://github.blog/category/engineering/feed/",
    "https://discord.com/blog/rss.xml",
    "https://aws.amazon.com/blogs/architecture/feed/"
]

def clean_html(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    return soup.get_text(separator=" ", strip=True)

def main():
    producer = KafkaProducer(
        bootstrap_servers=['localhost:9092'],
        value_serializer=lambda x: json.dumps(x).encode('utf-8')
    )
    
    seen_links = set()

    print("🚀 Starting Tech Blog Crawler...")

    while True:
        for feed_url in RSS_FEEDS:
            try:
                print(f"Checking {feed_url}...")
                # Add User-Agent to avoid blocking
                feed = feedparser.parse(feed_url, agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
                
                for entry in feed.entries[:5]: # Check latest 5 entries per feed
                    if entry.link not in seen_links:
                        
                        # Clean the content (RSS often has HTML)
                        raw_content = entry.get("content", [{"value": ""}])[0]["value"] or entry.get("summary", "")
                        clean_text = clean_html(raw_content)

                        # Skip empty articles
                        if len(clean_text) < 100:
                            continue

                        payload = {
                            "title": entry.title,
                            "url": entry.link,
                            "published": entry.get("published", ""),
                            "source": feed.feed.get("title", "Tech Blog"),
                            "content": clean_text,
                            # Important: We will chunk this in the Spark job
                        }
                        
                        try:
                            future = producer.send('news_stream', payload)
                            future.get(timeout=10) # Block to ensure send
                            print(f"Sent: {entry.title}")
                            seen_links.add(entry.link)
                        except Exception as k_err:
                            print(f"ERROR: Kafka send failed: {k_err}")
                        
            except Exception as e:
                print(f"Error parsing {feed_url}: {e}")
        
        producer.flush()
        print("Sleeping for 5 minutes...")
        time.sleep(300) # Poll every 5 mins


if __name__ == "__main__":
    main()