import time
import json
import feedparser
from kafka import KafkaProducer
from bs4 import BeautifulSoup

# A curated list of high-quality engineering blogs
RSS_FEEDS = [
    "https://netflixtechblog.com/feed",
    "https://eng.uber.com/feed/",
    "https://airbnb.io/feed.xml",
    "https://instagram-engineering.com/feed",
    "https://engineering.atspotify.com/feed/",
    "https://github.blog/category/engineering/feed/",
    "https://discord.com/blog/rss",
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
                feed = feedparser.parse(feed_url)
                
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
                        
                        producer.send('news_stream', payload)
                        print(f"Sent: {entry.title}")
                        seen_links.add(entry.link)
                        
            except Exception as e:
                print(f"Error parsing {feed_url}: {e}")
        
        print("Sleeping for 5 minutes...")
        time.sleep(300) # Poll every 5 mins

if __name__ == "__main__":
    main()