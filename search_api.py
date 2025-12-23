import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware  # <--- IMPORT THIS
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http import models
from typing import List, Optional

app = FastAPI(title="Neural Search API")

# ### NEW CODE: ENABLE CORS ###
# This tells the browser: "Allow requests from anywhere (like Next.js on port 3000)"
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, set this to ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# #############################

# --- Configuration ---
QDRANT_URL = os.environ.get("QDRANT_URL", "http://qdrant:6333")
COLLECTION_NAME = "news_articles"

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
    url:str

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
        info = client.get_collection(COLLECTION_NAME)
        return {
            "collection": COLLECTION_NAME,
            "points_count": info.points_count,
            "status": info.status
        }
    except Exception as e:
        return {"collection": COLLECTION_NAME, "points_count": 0, "status": "not_found"}

@app.get("/categories")
def get_categories():
    try:
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
        print(f"Received Query: {query.query}") # Debug Log
        query_vector = model.encode(query.query).tolist()
        
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
        
        search_result = client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_vector,
            query_filter=query_filter,
            limit=query.limit
        )
        
        results = []
        for point in search_result.points:
            results.append(
                SearchResult(
                    id=str(point.id),
                    title=point.payload.get("title", "No Title"),
                    url=point.payload.get("url", "#"), # <--- ADD THIS
                    content=point.payload.get("content", ""), # This is now the specific chunk!
                    category=point.payload.get("source", "Unknown"), # Changed from category to source
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