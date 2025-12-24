# Atlas: A Semantic Search Engine for Course Materials

## Motivation

I set out to build a search engine. It seemed like an interesting challenge—crawling the web, building an index, ranking results. But I quickly realized something: **I can't beat Google at being Google.**

Google has decades of engineering, petabytes of data, and thousands of engineers optimizing PageRank. Competing head-to-head would be naive.

So I pivoted. Instead of building a general search engine, I asked: _What problem do I actually face?_

As a student, I constantly struggle to find supplementary course materials. I want:

- **Practice exams** from other universities teaching the same course
- **Lecture notes** that explain concepts differently than my professor
- **Problem sets with solutions** to test my understanding
- **Cheatsheets** that distill a course into key formulas

This content exists—scattered across MIT OCW, GitHub repos, professor websites, and course archives. But finding it is painful. Google doesn't understand "I want Linear Algebra exams from top CS schools."

**Atlas does.**

---

## Current Coverage

| Metric              | Value                                                        |
| ------------------- | ------------------------------------------------------------ |
| **Total Documents** | 5,739                                                        |
| **Sources**         | 8 institutions                                               |
| **Resource Types**  | Lecture Slides, Course Notes, Exams, Problem Sets, Solutions |

### Sources Indexed

| Source             | Type       | Content                                                 |
| ------------------ | ---------- | ------------------------------------------------------- |
| MIT OpenCourseWare | Deep Crawl | Calculus, Linear Algebra, Diff Eq, Physics, Biology, CS |
| Stanford SEE       | Deep Crawl | Convex Optimization, ML, Robotics, Signal Processing    |
| Harvard CS50       | Deep Crawl | Intro Computer Science course materials                 |
| Yale OYC           | Deep Crawl | Open Yale Courses across departments                    |
| CMU OLI            | Deep Crawl | Statistics, Chemistry, Psychology modules               |
| GitHub (Stanford)  | Repos      | CS229/230/221 cheatsheets                               |
| GitHub (MIT)       | Repos      | 18S191, 18335 math course notes                         |
| GitHub (Various)   | Repos      | Student notes from Waterloo, Berkeley                   |

---

## The Tech Stack

### Architecture Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                        DATA COLLECTION                           │
├──────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │  MIT OCW    │  │  Yale OYC   │  │  CMU OLI    │  Bucket A    │
│  │  Collector  │  │  Collector  │  │  Collector  │  (Deep Crawl)│
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘              │
│         │                │                │                      │
│  ┌──────┴────────────────┴────────────────┴──────┐              │
│  │              GitHub Notes Collector           │  Bucket B    │
│  │     (Waterloo, Stanford, MIT, Berkeley)       │  (Repos)     │
│  └──────────────────────┬────────────────────────┘              │
└─────────────────────────┼────────────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────────────┐
│                      MESSAGE BROKER                              │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                     Apache Kafka                            │ │
│  │              Topic: atlas_resources                         │ │
│  └──────────────────────────┬─────────────────────────────────┘ │
└─────────────────────────────┼────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│                    STREAM PROCESSING                             │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                    Apache Spark                             │ │
│  │  • Consumes from Kafka                                      │ │
│  │  • Generates embeddings (SentenceTransformer)               │ │
│  │  • Upserts to Qdrant                                        │ │
│  └──────────────────────────┬─────────────────────────────────┘ │
└─────────────────────────────┼────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│                     VECTOR DATABASE                              │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                      Qdrant                                 │ │
│  │  • Stores 384-dimensional vectors                          │ │
│  │  • Cosine similarity search                                 │ │
│  │  • Payload filtering (source, type)                         │ │
│  └──────────────────────────┬─────────────────────────────────┘ │
└─────────────────────────────┼────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│                       API + FRONTEND                             │
│  ┌─────────────────────┐    ┌──────────────────────────────────┐│
│  │      FastAPI        │◄──►│           Next.js                ││
│  │  • /search endpoint │    │  • React + Tailwind              ││
│  │  • Query embedding  │    │  • Semantic search UI            ││
│  └─────────────────────┘    └──────────────────────────────────┘│
└──────────────────────────────────────────────────────────────────┘
```

### Why Each Technology?

| Component            | Technology          | Why?                                                                       |
| -------------------- | ------------------- | -------------------------------------------------------------------------- |
| **Message Broker**   | Apache Kafka        | Decouples collection from processing; handles backpressure; enables replay |
| **Stream Processor** | Apache Spark        | Distributed processing; integrates with Kafka; scales horizontally         |
| **Vector DB**        | Qdrant              | Purpose-built for vectors; fast cosine similarity; payload filtering       |
| **Embeddings**       | SentenceTransformer | Pre-trained on semantic similarity; 384-dim vectors; runs locally          |
| **API**              | FastAPI             | Async Python; automatic OpenAPI docs; fast                                 |
| **Frontend**         | Next.js             | React with SSR; great DX; production-ready                                 |

---

## Data Collection

### The Two-Bucket Strategy

I discovered that not all universities are created equal when it comes to open courseware:

**Bucket A: Centralized Portals (Deep Crawl)**

- MIT OCW, Yale OYC, CMU OLI have _structured_ content
- Stable URLs, consistent formats, official syllabi
- Strategy: Systematically crawl every course

**Bucket B: Distributed Content (GitHub Repos)**

- Student notes, professor repos, community resources
- Scattered but often higher quality (curated, battle-tested)
- Strategy: Crawl curated list of GitHub repos

### Collector Architecture

Each collector extends a `BaseCollector` class:

```python
class BaseCollector(ABC):
    RESOURCE_TYPES = ["Lecture Slides", "Course Notes", "Exam",
                      "Problem Set", "Solutions", "Syllabus"]

    def create_payload(self, title, summary, authors, url,
                       source, resource_type):
        return {
            "title": title,
            "summary": summary,
            "authors": authors,
            "url": url,
            "source": source,
            "resource_type": resource_type,
            "content": f"{title}\n\n{summary}"  # For embedding
        }
```

---

## The Embedding Process

### What is Semantic Search?

Traditional keyword search:

- Query: "linear algebra exam"
- Matches: Documents containing those exact words

Semantic search:

- Query: "linear algebra exam"
- Matches: Documents about matrix theory finals, eigenvalue tests, LA assessments

### The Math: Sentence Embeddings

I use `all-MiniLM-L6-v2`, a SentenceTransformer model that maps text to 384-dimensional vectors.

Given a text $t$, the model produces an embedding:

$$\vec{e} = f_\theta(t) \in \mathbb{R}^{384}$$

where $f_\theta$ is a transformer network with learned parameters $\theta$.

### Cosine Similarity

To find relevant documents, I compute cosine similarity between the query embedding $\vec{q}$ and each document embedding $\vec{d}$:

$$\text{sim}(\vec{q}, \vec{d}) = \frac{\vec{q} \cdot \vec{d}}{||\vec{q}|| \cdot ||\vec{d}||} = \cos(\theta)$$

This measures the angle between vectors:

- $\text{sim} = 1$: Identical meaning
- $\text{sim} = 0$: Unrelated
- $\text{sim} = -1$: Opposite meaning

### Approximate Nearest Neighbor (ANN)

Computing similarity against all documents is $O(n)$. With thousands of documents, this is slow.

Qdrant uses **HNSW** (Hierarchical Navigable Small World) graphs for approximate nearest neighbor search:

$$\text{Time complexity: } O(\log n)$$

The tradeoff: Slight accuracy loss for massive speed gains.

---

## Stream Processing Pipeline

### Why Streaming?

Course materials are collected continuously. A batch approach would:

1. Wait for all collectors to finish
2. Process everything at once
3. Update the index

This introduces latency. With streaming:

1. Each document flows through immediately
2. Index updates in near real-time
3. New content is searchable within seconds

### The Spark Pipeline

```python
# Consume from Kafka
df = spark.readStream \
    .format("kafka") \
    .option("subscribe", "atlas_resources") \
    .load()

# Parse JSON, extract fields
parsed = df.select(from_json(col("value").cast("string"), schema))

# Generate embeddings
def embed(text):
    return model.encode(text).tolist()

# Upsert to Qdrant
def upsert_batch(batch):
    qdrant.upsert(collection="atlas_resources", points=batch)
```

### Data Flow

```
Collector → Kafka → Spark → SentenceTransformer → Qdrant → API → User
    |          |        |            |              |
    |          |        |            |              └─ <1ms query time
    |          |        |            └─ 384-dim vector
    |          |        └─ Distributed processing
    |          └─ Decoupling + replay
    └─ Web scraping
```

---

## The Search API

### Query Flow

1. User submits query: "calculus problem sets with solutions"
2. FastAPI receives request
3. Query is embedded: $\vec{q} = f_\theta(\text{query})$
4. Qdrant finds nearest neighbors
5. Results filtered by score threshold ($\geq 0.2$)
6. Deduplicated by URL
7. Returned as JSON

### Filtering

Users can filter by:

- **Resource Type**: Exam, Problem Set, Lecture Slides, etc.
- **Source**: MIT, Stanford, Waterloo, etc.

Qdrant handles this at the database level:

```python
query_filter = models.Filter(
    must=[
        models.FieldCondition(
            key="resource_type",
            match=models.MatchValue(value="Exam")
        )
    ]
)
```

---

## What I Learned

1. **Domain focus beats general purpose**: A niche search engine can outperform Google in its domain
2. **Streaming is worth the complexity**: Real-time updates make the system feel alive
3. **Curated data beats crawled data**: GitHub repos with student notes are often better than official sources
4. **Vector search is magic**: Semantic similarity captures intent in ways keywords can't

---

## Future Work

- [ ] Add more GitHub repos as sources
- [ ] Implement RAG for AI-powered summaries
- [ ] User accounts for saved searches
- [ ] Course recommendations based on search history
