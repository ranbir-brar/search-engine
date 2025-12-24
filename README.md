# Atlas Course Materials Search Engine

A semantic search engine for university course materials: lecture notes, exams, problem sets, and solutions.

## Architecture

```
┌─────────────┐     ┌─────────┐     ┌───────────────┐     ┌────────┐
│  Collectors │────▶│  Kafka  │────▶│ Spark Stream  │────▶│ Qdrant │
│  (6 total)  │     │         │     │  (Embeddings) │     │(Vector)│
└─────────────┘     └─────────┘     └───────────────┘     └────────┘
                                                               │
┌─────────────┐     ┌─────────┐                                │
│   Next.js   │◀───▶│ FastAPI │◀───────────────────────────────┘
│   Frontend  │     │   API   │
└─────────────┘     └─────────┘
```

## Data Sources

### Bucket A: Centralized Open Courseware (Deep Crawl)

These have stable portals for systematic crawling:

| Source           | Content                                      |
| ---------------- | -------------------------------------------- |
| **MIT OCW**      | 1800+ courses with PDFs, exams, problem sets |
| **Yale OYC**     | ~40 courses with lectures, transcripts       |
| **CMU OLI**      | Free learning modules (stats, CS, chemistry) |
| **Stanford SEE** | Engineering courses                          |
| **Harvard CS50** | Intro CS course materials                    |

### Bucket B: GitHub Repos (Course Notes)

Curated repos with student/professor notes:

- Stanford CS229/230/221 cheatsheets
- MIT math courses (18S191, 18335, 18065)
- Berkeley CS61A/B notes
- Waterloo/UofT course notes

## Quick Start

```bash
# Start infrastructure
docker-compose up -d

# Start API
uvicorn search_api:app --port 8000

# Start frontend
cd search-ui && npm run dev

# Start data collection
python producer.py
```

## Tech Stack

- **Frontend**: Next.js, React, Tailwind CSS
- **Backend**: FastAPI, Python
- **Search**: Qdrant (vector database), SentenceTransformers
- **Streaming**: Apache Kafka, Apache Spark
- **Infrastructure**: Docker Compose

## License

MIT
