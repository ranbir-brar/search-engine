"""
Migration script to copy data from local Qdrant to Qdrant Cloud.
"""
from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance, PointStruct

# Local Qdrant
LOCAL_URL = "http://localhost:6333"

# Qdrant Cloud
CLOUD_URL = "https://d4f85829-4e76-4f3f-b18e-d1479a36fd44.us-west-1-0.aws.cloud.qdrant.io"
CLOUD_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.UvwY-OLlY_Di9imBqoEsQaFM2lKVtyexbWI_YJAQuWA"

COLLECTION_NAME = "atlas_resources"
BATCH_SIZE = 100


def migrate():
    print("🔄 Connecting to local Qdrant...")
    local = QdrantClient(url=LOCAL_URL)
    
    print("☁️ Connecting to Qdrant Cloud...")
    cloud = QdrantClient(url=CLOUD_URL, api_key=CLOUD_API_KEY)
    
    # Check local collection
    try:
        local_info = local.get_collection(COLLECTION_NAME)
        total_points = local_info.points_count
        print(f"📊 Found {total_points} points in local Qdrant")
    except Exception as e:
        print(f"❌ Error accessing local collection: {e}")
        return
    
    # Create collection in cloud
    try:
        cloud.get_collection(COLLECTION_NAME)
        print(f"⚠️ Collection already exists in cloud, will add data to it")
    except:
        print(f"✨ Creating collection '{COLLECTION_NAME}' in cloud...")
        cloud.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE)
        )
    
    # Migrate data in batches
    print(f"\n📤 Migrating data in batches of {BATCH_SIZE}...")
    offset = None
    migrated = 0
    
    while True:
        # Scroll through local data
        results, next_offset = local.scroll(
            collection_name=COLLECTION_NAME,
            limit=BATCH_SIZE,
            offset=offset,
            with_vectors=True,
            with_payload=True
        )
        
        if not results:
            break
        
        # Convert Record to PointStruct
        points = []
        for record in results:
            points.append(PointStruct(
                id=record.id,
                vector=record.vector,
                payload=record.payload
            ))
        
        # Upsert to cloud
        cloud.upsert(
            collection_name=COLLECTION_NAME,
            points=points
        )
        
        migrated += len(results)
        print(f"   ✅ Migrated {migrated}/{total_points} points...")
        
        if next_offset is None:
            break
        offset = next_offset
    
    print(f"\n🎉 Migration complete! {migrated} points migrated to cloud.")
    
    # Verify
    cloud_info = cloud.get_collection(COLLECTION_NAME)
    print(f"☁️ Cloud collection now has {cloud_info.points_count} points")


if __name__ == "__main__":
    migrate()
