# Atlas Academic Search Engine

A real-time semantic search engine for academic resources including research papers, university lectures, textbooks, and course materials.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

## Features

- **Semantic Search** - Find resources by meaning, not just keywords
- **7 Data Sources** - arXiv, MIT OCW, Stanford, Harvard, Yale, Khan Academy, OpenStax
- **Real-time Ingestion** - Continuous data pipeline via Kafka and Spark
- **10,000+ Resources** - Papers, lectures, textbooks, and course materials

## Data Sources

| Source           | Content                                               |
| ---------------- | ----------------------------------------------------- |
| **arXiv**        | 45 categories (CS, Math, Physics, Biology, Economics) |
| **MIT OCW**      | 52 courses across all departments                     |
| **Stanford SEE** | 9 engineering courses                                 |
| **Harvard CS50** | Intro CS (11 weeks)                                   |
| **Open Yale**    | 8 interdisciplinary courses                           |
| **Khan Academy** | 35 topics, 100+ lessons                               |
| **OpenStax**     | 19 textbooks, 216 chapters                            |

## Architecture

```
Collectors → Kafka → Spark (embeddings) → Qdrant ← FastAPI ← Next.js
```

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.10+
- Node.js 18+

### Full Pipeline

```bash
# Start all services
docker-compose up -d

# Run data collection
python producer.py

# Start stream processor
docker-compose exec spark-dev python stream_processor.py

# Start frontend
cd search-ui && npm run dev
```

### Search Only (minimal resources)

```bash
docker-compose up -d qdrant search-api
cd search-ui && npm run dev
```

## Access

| Service          | URL                             |
| ---------------- | ------------------------------- |
| Search UI        | http://localhost:3000           |
| API Docs         | http://localhost:8000/docs      |
| Qdrant Dashboard | http://localhost:6333/dashboard |

## Project Structure

```
├── collectors/          # Data collectors (7 sources)
│   ├── arxiv_collector.py
│   ├── ocw_collector.py
│   ├── stanford_collector.py
│   ├── harvard_collector.py
│   ├── yale_collector.py
│   ├── khan_collector.py
│   └── openstax_collector.py
├── producer.py          # Orchestrates collectors → Kafka
├── stream_processor.py  # Spark: Kafka → Embeddings → Qdrant
├── search_api.py        # FastAPI search backend
├── search-ui/           # Next.js frontend
└── docker-compose.yml   # Infrastructure
```

## Tech Stack

| Component  | Technology                               |
| ---------- | ---------------------------------------- |
| Streaming  | Apache Kafka, Apache Spark               |
| Vector DB  | Qdrant                                   |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| API        | FastAPI                                  |
| Frontend   | Next.js, TypeScript, Tailwind CSS        |

## License

MIT License - see [LICENSE](LICENSE) for details.
