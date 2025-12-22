import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http import models  # Needed for filters
from typing import List, Optional

app = FastAPI(title="Neural Search API")

# --- Configuration ---
QDRANT_URL = os.environ.get("QDRANT_URL", "http://qdrant:6333")
COLLECTION_NAME = "news_articles"

# --- Startup: Load Model & Connect ---
print("Loading SentenceTransformer model...")
model = SentenceTransformer("all-MiniLM-L6-v2")
print("Model loaded!")

client = QdrantClient(url=QDRANT_URL)

# --- Data Models ---
class SearchQuery(BaseModel):
    query: str
    limit: int = 10
    category: Optional[str] = None

class SearchResult(BaseModel):
    id: str
    title: str
    content: str
    category: str
    score: float

# --- Endpoints ---

@app.get("/")
def root():
    return {"message": "Neural Search API (Qdrant Backend)"}

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
        # This is the endpoint the frontend is looking for!
        info = client.get_collection(COLLECTION_NAME)
        return {
            "collection": COLLECTION_NAME,
            "points_count": info.points_count,
            "status": info.status
        }
    except Exception as e:
        # Returns 0 stats if collection doesn't exist yet
        return {"collection": COLLECTION_NAME, "points_count": 0, "status": "not_found"}

@app.get("/categories")
def get_categories():
    try:
        # This allows the dropdown filter to work
        results = client.scroll(
            collection_name=COLLECTION_NAME,
            limit=1000,
            with_payload=True
        )[0]
        
        categories = set()
        for point in results:
            if point.payload and "category" in point.payload:
                categories.add(point.payload["category"])
        
        return {"categories": sorted(list(categories))}
    except Exception as e:
        return {"categories": []}

@app.post("/search", response_model=List[SearchResult])
def search(query: SearchQuery):
    try:
        # 1. Vectorize query
        query_vector = model.encode(query.query).tolist()
        
        # 2. Build Filter
        query_filter = None
        if query.category and query.category != "All":
            query_filter = models.Filter(
                must=[
                    models.FieldCondition(
                        key="category",
                        match=models.MatchValue(value=query.category)
                    )
                ]
            )
        
        # 3. Search (Using the fixed query_points method)
        search_result = client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_vector,
            query_filter=query_filter,
            limit=query.limit
        )
        
        # 4. Format Results
        results = []
        for point in search_result.points:
            results.append(
                SearchResult(
                    id=str(point.id),
                    title=point.payload.get("title", "No Title"),
                    content=point.payload.get("content", ""),
                    category=point.payload.get("category", "Uncategorized"),
                    score=point.score
                )
            )
        return results
        
    except Exception as e:
        print(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)