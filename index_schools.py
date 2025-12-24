"""
Direct indexer for specific schools - bypasses Kafka/Spark.
Collects from GitHub repos and writes directly to Qdrant Cloud.
Includes duplicate detection via URL checking.
"""
import os
import uuid
import hashlib
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Filter, FieldCondition, MatchValue, PayloadSchemaType
from collectors.github_notes_collector import GitHubNotesCollector

# Qdrant Cloud config (from environment)
QDRANT_URL = os.environ.get("QDRANT_URL")
QDRANT_API_KEY = os.environ.get("QDRANT_API_KEY")
COLLECTION_NAME = "atlas_resources"

# Schools to collect
TARGET_SCHOOLS = ["Waterloo", "UofT", "Berkeley", "McGill"]


def get_existing_urls(client) -> set:
    """Fetch all existing URLs from Qdrant to avoid duplicates."""
    print("Loading existing URLs from Qdrant...")
    existing_urls = set()
    offset = None
    
    while True:
        result = client.scroll(
            collection_name=COLLECTION_NAME,
            limit=100,
            offset=offset,
            with_payload=["url"]
        )
        points, offset = result
        
        if not points:
            break
        
        for p in points:
            url = p.payload.get("url")
            if url:
                existing_urls.add(url)
        
        if offset is None:
            break
    
    print(f"  Found {len(existing_urls)} existing URLs")
    return existing_urls


def main():
    print("🎓 Direct Indexer - Waterloo, UofT, Berkeley, McGill")
    print("=" * 50)
    
    # Check credentials
    if not QDRANT_URL or not QDRANT_API_KEY:
        print("❌ Set QDRANT_URL and QDRANT_API_KEY environment variables")
        return
    
    # Initialize
    print("Loading embedding model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    print(f"Connecting to Qdrant Cloud...")
    client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
    
    # Get existing URLs to avoid duplicates
    existing_urls = get_existing_urls(client)
    
    # Filter repos for target schools
    collector = GitHubNotesCollector()
    original_repos = collector.COURSE_REPOS
    collector.COURSE_REPOS = [
        r for r in original_repos 
        if r["school"] in TARGET_SCHOOLS
    ]
    
    print(f"\nCollecting from {len(collector.COURSE_REPOS)} repos...")
    for r in collector.COURSE_REPOS:
        print(f"  - {r['owner']}/{r['repo']} ({r['school']})")
    
    # Collect (increase limit since we're filtering dupes)
    payloads = collector.collect(limit=5000)
    
    # Filter out duplicates
    new_payloads = []
    skipped = 0
    for p in payloads:
        if p["url"] not in existing_urls:
            new_payloads.append(p)
        else:
            skipped += 1
    
    print(f"\n📊 Collected {len(payloads)} items, {skipped} already exist, {len(new_payloads)} new")
    
    if not new_payloads:
        print("No new items to index.")
        return
    
    # Index to Qdrant
    print(f"\nIndexing {len(new_payloads)} new items to Qdrant Cloud...")
    points = []
    
    for payload in new_payloads:
        # Create embedding
        text = f"{payload['title']} {payload['summary']}"
        embedding = model.encode(text).tolist()
        
        # Use URL hash as ID for idempotent upserts
        url_hash = hashlib.md5(payload["url"].encode()).hexdigest()
        
        point = PointStruct(
            id=url_hash,
            vector=embedding,
            payload=payload
        )
        points.append(point)
    
    # Upsert in batches
    batch_size = 100
    for i in range(0, len(points), batch_size):
        batch = points[i:i+batch_size]
        client.upsert(collection_name=COLLECTION_NAME, points=batch)
        print(f"  Indexed {min(i+batch_size, len(points))}/{len(points)}")
    
    print(f"\n🎉 Done! Added {len(points)} new items to Qdrant Cloud")
    
    # Verify
    info = client.get_collection(COLLECTION_NAME)
    print(f"📊 Total points in cloud: {info.points_count}")


if __name__ == "__main__":
    main()
