# Atlas Course Materials Search Engine

A semantic search engine for university course materials including lecture notes, exams, problem sets, and solutions from top US and Canadian universities.

## Features

- **Semantic Search**: Find relevant course materials using natural language queries
- **8 University Sources**: MIT, Stanford, Harvard, Yale + Waterloo, UofT, UBC, McGill
- **Resource Types**: Lecture slides, course notes, exams, problem sets, solutions

## Architecture

```
┌─────────────┐     ┌─────────┐     ┌───────────────┐     ┌────────┐
│  Collectors │────▶│  Kafka  │────▶│ Spark Stream  │────▶│ Qdrant │
│  (8 schools)│     │         │     │  (Embeddings) │     │(Vector)│
└─────────────┘     └─────────┘     └───────────────┘     └────────┘
                                                               │
┌─────────────┐     ┌─────────┐                                │
│   Next.js   │◀───▶│ FastAPI │◀───────────────────────────────┘
│   Frontend  │     │   API   │
└─────────────┘     └─────────┘
```

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

## Universities Covered

### US Schools

- **MIT OCW** - Full courses with exams and problem sets
- **Stanford SEE** - Engineering courses
- **Harvard CS50** - Intro to Computer Science
- **Yale OYC** - Open Yale Courses

### Canadian Schools

- **UWaterloo** - CS and Math courses
- **UofT** - Computer Science
- **UBC** - CS and Math
- **McGill** - CS and Math

## Tech Stack

- **Frontend**: Next.js, React, Tailwind CSS
- **Backend**: FastAPI, Python
- **Search**: Qdrant (vector database), SentenceTransformers
- **Streaming**: Apache Kafka, Apache Spark
- **Infrastructure**: Docker Compose

## License

MIT
