"""
Atlas Academic Search Engine - FastAPI Backend
Provides semantic search across academic resources with filtering.
"""
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http import models
from typing import List, Optional

app = FastAPI(
    title="Atlas Academic Search API",
    description="Semantic search for academic resources: papers, lectures, and course materials"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Configuration ---
QDRANT_URL = os.environ.get("QDRANT_URL", "http://qdrant:6333")
COLLECTION_NAME = "atlas_resources"

# Valid resource types for filtering
RESOURCE_TYPES = ["Paper", "Lecture Slides", "Course Notes", "Syllabus"]

print("🎓 Atlas API Starting...")
print("Loading SentenceTransformer model...")
model = SentenceTransformer("all-MiniLM-L6-v2")
print("Model loaded!")

client = QdrantClient(url=QDRANT_URL)


# --- Data Models ---
class SearchQuery(BaseModel):
    query: str
    limit: int = 10
    resource_type: Optional[str] = None  # Filter by type
    source: Optional[str] = None  # Filter by source (e.g., "arXiv", "MIT OCW")


class SearchResult(BaseModel):
    id: str
    title: str
    content: str
    source: str
    resource_type: str
    authors: List[str]
    url: str
    score: float
    summary_preview: Optional[str] = None


# --- Endpoints ---
@app.get("/")
def root():
    return {
        "message": "Atlas Academic Search API",
        "version": "1.0",
        "resource_types": RESOURCE_TYPES
    }


@app.get("/health")
def health():
    try:
        collections = client.get_collections()
        return {
            "status": "healthy",
            "qdrant": "connected",
            "collections": [c.name for c in collections.collections]
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Qdrant error: {str(e)}")


@app.get("/stats")
def stats():
    try:
        info = client.get_collection(COLLECTION_NAME)
        return {
            "collection": COLLECTION_NAME,
            "points_count": info.points_count,
            "status": info.status
        }
    except Exception as e:
        return {"collection": COLLECTION_NAME, "points_count": 0, "status": "not_found"}


@app.get("/resource-types")
def get_resource_types():
    """Get available resource types for filtering."""
    return {"resource_types": RESOURCE_TYPES}


@app.get("/sources")
def get_sources():
    """Get available sources for filtering."""
    try:
        results = client.scroll(
            collection_name=COLLECTION_NAME,
            limit=1000,
            with_payload=True
        )[0]
        sources = set()
        for point in results:
            if point.payload and "source" in point.payload:
                sources.add(point.payload["source"])
        return {"sources": sorted(list(sources))}
    except Exception as e:
        return {"sources": []}


@app.post("/search", response_model=List[SearchResult])
def search(query: SearchQuery):
    try:
        print(f"🔍 Search: '{query.query}' | Type: {query.resource_type} | Source: {query.source}")
        query_vector = model.encode(query.query).tolist()
        
        # Build filter conditions
        filter_conditions = []
        
        if query.resource_type and query.resource_type != "All":
            filter_conditions.append(
                models.FieldCondition(
                    key="resource_type",
                    match=models.MatchValue(value=query.resource_type)
                )
            )
        
        if query.source and query.source != "All":
            filter_conditions.append(
                models.FieldCondition(
                    key="source",
                    match=models.MatchValue(value=query.source)
                )
            )
        
        query_filter = None
        if filter_conditions:
            query_filter = models.Filter(must=filter_conditions)
        
        # Search Qdrant
        search_result = client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_vector,
            query_filter=query_filter,
            limit=query.limit * 3,  # Fetch extra for deduplication
            score_threshold=0.35
        )
        
        results = []
        seen_urls = set()
        
        for point in search_result.points:
            url = point.payload.get("url", "#")
            
            # Skip duplicates
            if url in seen_urls:
                continue
                
            seen_urls.add(url)
            
            if len(results) >= query.limit:
                break
            
            results.append(
                SearchResult(
                    id=str(point.id),
                    title=point.payload.get("title", "Untitled"),
                    content=point.payload.get("content", ""),
                    source=point.payload.get("source", "Unknown"),
                    resource_type=point.payload.get("resource_type", "Paper"),
                    authors=point.payload.get("authors", []),
                    url=url,
                    score=point.score,
                    summary_preview=point.payload.get("summary_preview", "")
                )
            )
        
        print(f"   ✅ Returning {len(results)} results")
        return results
        
    except Exception as e:
        print(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)