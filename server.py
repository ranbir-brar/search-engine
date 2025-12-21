import json
import os
import threading
from pathlib import Path
from typing import List

import faiss
import numpy as np
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field, validator
from sentence_transformers import SentenceTransformer

EMBED_DIM = int(os.environ.get("EMBED_DIM", "384"))
INDEX_PATH = os.environ.get("FAISS_INDEX_PATH", "data/index.faiss")
IDS_PATH = os.environ.get("FAISS_IDS_PATH", "data/index_ids.json")

app = FastAPI(title="Neural Search API")

model = None
index = None
id_map: List[str] = []
lock = threading.Lock()


class IndexItem(BaseModel):
    id: str = Field(..., min_length=1)
    vector: List[float]

    @validator("vector")
    def validate_vector(cls, value: List[float]) -> List[float]:
        if len(value) != EMBED_DIM:
            raise ValueError(f"vector must be length {EMBED_DIM}")
        return value


class IndexBatch(BaseModel):
    items: List[IndexItem] = Field(..., min_items=1)


def load_index() -> faiss.Index:
    path = Path(INDEX_PATH)
    if path.exists():
        return faiss.read_index(str(path))
    return faiss.IndexFlatL2(EMBED_DIM)


def load_id_map() -> List[str]:
    path = Path(IDS_PATH)
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def persist_state() -> None:
    index_path = Path(INDEX_PATH)
    index_path.parent.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(index_path))

    ids_path = Path(IDS_PATH)
    ids_path.parent.mkdir(parents=True, exist_ok=True)
    with ids_path.open("w", encoding="utf-8") as handle:
        json.dump(id_map, handle)


@app.on_event("startup")
def startup() -> None:
    global model, index, id_map
    model = SentenceTransformer("all-MiniLM-L6-v2")
    index = load_index()
    id_map = load_id_map()

    if index.ntotal != len(id_map):
        print("ID map length does not match index size; repairing map.")
        id_map = id_map[: index.ntotal]
        if len(id_map) < index.ntotal:
            id_map.extend([f"unknown-{i}" for i in range(len(id_map), index.ntotal)])


@app.post("/index")
def index_vector(item: IndexItem):
    added = add_items([item])
    return {"indexed": added, "total": index.ntotal}


@app.post("/index/batch")
def index_batch(batch: IndexBatch):
    added = add_items(batch.items)
    return {"indexed": added, "total": index.ntotal}


def add_items(items: List[IndexItem]) -> int:
    if index is None:
        raise HTTPException(status_code=503, detail="Service not ready")

    vectors = np.asarray([item.vector for item in items], dtype="float32")
    with lock:
        index.add(vectors)
        id_map.extend([item.id for item in items])
        persist_state()
    return len(items)


@app.get("/search")
def search(q: str = Query(..., min_length=1), k: int = Query(5, ge=1, le=50)):
    if model is None or index is None:
        raise HTTPException(status_code=503, detail="Service not ready")

    query_vec = model.encode([q], convert_to_numpy=True)
    query_vec = np.asarray(query_vec, dtype="float32")

    with lock:
        if index.ntotal == 0:
            return {"results": []}
        k_use = min(k, index.ntotal)
        distances, indices = index.search(query_vec, k_use)

    results = []
    for idx, distance in zip(indices[0], distances[0]):
        doc_id = id_map[idx] if idx < len(id_map) else str(idx)
        results.append({"id": doc_id, "distance": float(distance)})

    return {"results": results}
