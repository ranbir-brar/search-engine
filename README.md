# Atlas Academic Search Engine

Semantic search for academic resources: research papers, lectures, textbooks, and course materials.

## Data Sources (7 Collectors)

| Source           | Content                                               |
| ---------------- | ----------------------------------------------------- |
| **arXiv**        | 45 categories (CS, Math, Physics, Biology, Economics) |
| **MIT OCW**      | 52 courses across all departments                     |
| **Stanford SEE** | 9 engineering courses                                 |
| **Harvard CS50** | Intro CS (11 weeks)                                   |
| **Open Yale**    | 8 interdisciplinary courses                           |
| **Khan Academy** | 35 topics, 100+ lessons                               |
| **OpenStax**     | 19 textbooks, 216 chapters                            |

**Expected: 10,000+ resources**

## Quick Start

```bash
# Start infrastructure
docker-compose up -d

# Run producer (collects resources)
python producer.py

# Run stream processor (indexes to Qdrant)
docker-compose exec spark-dev python stream_processor.py

# Start API
uvicorn search_api:app --reload --port 8000

# Start frontend
cd search-ui && npm run dev
```

## Access

| Service   | URL                             |
| --------- | ------------------------------- |
| Search UI | http://localhost:3000           |
| API Docs  | http://localhost:8000/docs      |
| Qdrant    | http://localhost:6333/dashboard |

## Architecture

```
Collectors → Kafka → Spark (embeddings) → Qdrant ← FastAPI ← Next.js
```

## Tech Stack

- **Streaming**: Kafka, Spark
- **Vector DB**: Qdrant
- **Embeddings**: sentence-transformers (all-MiniLM-L6-v2)
- **API**: FastAPI
- **Frontend**: Next.js
