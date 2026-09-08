# MultiDoc-RAGOps

An end-to-end RAG application built to understand and implement the engineering side of **Retrieval-Augmented Generation (RAG)** and **RAGOps/LLMOps**.

The project currently supports document ingestion, chunking, Gemini embeddings, FAISS-based retrieval, Gemini generation, FastAPI APIs, evaluation, evaluation caching, and failure analysis.

The project is being built incrementally, with the goal of moving from a basic RAG pipeline toward a more production-oriented LLM application.

---

## Overview

A basic RAG system can be represented as:

```text
Documents
    ↓
Chunking
    ↓
Embeddings
    ↓
Vector Store
    ↓
Retrieval
    ↓
LLM
    ↓
Answer
```

MultiDoc-RAGOps adds engineering and evaluation components around this pipeline:

```text
                         ┌───────────────┐
                         │   Documents   │
                         └───────┬───────┘
                                 │
                                 ▼
                         ┌───────────────┐
                         │   Chunking    │
                         └───────┬───────┘
                                 │
                                 ▼
                         ┌───────────────┐
                         │   Embeddings  │
                         └───────┬───────┘
                                 │
                                 ▼
                         ┌───────────────┐
                         │     FAISS     │
                         │ Vector Store  │
                         └───────┬───────┘
                                 │
                                 ▼
                         ┌───────────────┐
                         │   Retrieval   │
                         └───────┬───────┘
                                 │
                                 ▼
                         ┌───────────────┐
                         │    Gemini     │
                         │  Generation   │
                         └───────┬───────┘
                                 │
                                 ▼
                              Answer
                                 │
                    ┌────────────┴────────────┐
                    │                         │
                    ▼                         ▼
              Evaluation               FastAPI API
                    │
          ┌─────────┼──────────┐
          ▼         ▼          ▼
       Metrics    Caching   Failure Analysis
```

---

# Features

### RAG

* Document ingestion
* Text chunking
* Configurable chunk overlap
* Gemini embeddings
* FAISS vector search
* Top-K retrieval
* Context construction
* Gemini-based answer generation

### API

* FastAPI application
* `/ask` endpoint
* `/health` endpoint
* Request/response validation
* Application lifespan management
* Startup/shutdown handling
* Request latency tracking

### Evaluation

* Evaluation dataset
* Context Recall
* Context Precision
* Faithfulness
* Answer Correctness
* Evaluation caching
* Evaluation result handling
* Failure analysis

### Development

* Modular Python structure
* Configuration management
* Logging
* Persistent FAISS index
* Pytest tests
* `uv` dependency management
* Docker support

---

# Tech Stack

| Component            | Technology        |
| -------------------- | ----------------- |
| Language             | Python            |
| API                  | FastAPI           |
| LLM                  | Google Gemini     |
| Embeddings           | Gemini Embeddings |
| Vector Search        | FAISS             |
| Numerical Processing | NumPy             |
| Configuration        | Pydantic Settings |
| Testing              | Pytest            |
| Package Manager      | uv                |
| Containerization     | Docker            |

---

# Project Structure

```text
MultiDoc-RAGops/
│
├── app/
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   └── schema.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   └── logger.py
│   │
│   ├── evaluation/
│   │   ├── evaluator.py
│   │   ├── metrics.py
│   │   ├── run_evaluation.py
│   │   ├── evaluation_cache.py
│   │   ├── evaluation_results.py
│   │   └── failure_analysis.py
│   │
│   ├── rag/
│   │   ├── chunker.py
│   │   ├── embeddings.py
│   │   ├── ingest.py
│   │   ├── main.py
│   │   ├── rag_pipeline.py
│   │   ├── similarity.py
│   │   ├── vector_store.py
│   │   ├── text_chunker.py
│   │   ├── test_embeddings.py
│   │   └── test_vector_store.py
│   │
│   └── llm_test.py
│
├── data/
│   ├── company.txt
│   └── evaluation.json
│
├── Dockerfile
├── .dockerignore
├── pyproject.toml
├── uv.lock
├── .python-version
├── .gitignore
└── README.md
```

---

# How the RAG Pipeline Works

## 1. Document Ingestion

The ingestion pipeline reads the source document and prepares it for indexing.

Currently, the project primarily works with text files.

```text
Document
    ↓
Read text
    ↓
Chunk text
    ↓
Generate embeddings
    ↓
Build vector index
```

Implementation:

```text
app/rag/ingest.py
```

---

## 2. Chunking

Large documents need to be split into smaller pieces before embedding them.

The current ingestion configuration uses:

```text
Chunk size:    300 characters
Overlap:        50 characters
```

The overlap helps retain some context between neighboring chunks.

Example:

```text
Chunk 1
────────────────────────────────
The company generated $10M in
revenue during the 2025 financial
year and expanded into new markets.
                         │
                         │ overlap
                         ▼
Chunk 2
────────────────────────────────
...expanded into new markets during
2025 and increased its workforce...
```

Chunking implementation:

```text
app/rag/chunker.py
```

---

## 3. Embeddings

Each document chunk is converted into a numerical vector using Gemini embeddings.

For example:

```text
Text
 ↓
Embedding Model
 ↓
[0.12, -0.43, 0.77, ...]
```

The user's question is also converted into an embedding.

This makes it possible to compare the question with document chunks based on semantic similarity.

Implementation:

```text
app/rag/embeddings.py
```

---

## 4. FAISS Vector Store

The generated embeddings are stored in a FAISS index.

The project currently uses:

```text
FAISS IndexFlatIP
```

The vectors are normalized before indexing, allowing inner-product similarity to behave as cosine similarity.

The retrieval flow is:

```text
User Question
     ↓
Question Embedding
     ↓
FAISS Similarity Search
     ↓
Top-K Relevant Chunks
```

Implementation:

```text
app/rag/vector_store.py
```

---

## 5. Retrieval

When a user asks a question, the question embedding is compared against the document embeddings.

For example:

```text
Question:
"What was the company's revenue?"

              ↓

       Similarity Search

              ↓

Chunk 1 → Revenue was $10M       ✓
Chunk 2 → Company headquarters   ✗
Chunk 3 → Annual revenue was...  ✓
Chunk 4 → Employee count...      ✗
```

The relevant chunks are then passed to the generation step.

---

## 6. Generation

The retrieved chunks are combined into a context and sent to Gemini along with the original question.

```text
Question
   +
Retrieved Context
   ↓
 Gemini
   ↓
 Answer
```

The generation prompt is designed to keep the answer grounded in the retrieved context and avoid inventing information that isn't available.

Implementation:

```text
app/rag/rag_pipeline.py
```

---

# FastAPI

The RAG pipeline is exposed through a FastAPI application.

Current endpoints:

```text
GET  /
GET  /health
POST /ask
```

## Health Check

```http
GET /health
```

Used to check whether the application is running.

## Ask a Question

```http
POST /ask
```

Example request:

```json
{
  "question": "What is the company's revenue?"
}
```

The API runs the question through the RAG pipeline and returns the generated answer along with retrieved source information and latency.

Example response:

```json
{
  "question": "What is the company's revenue?",
  "answer": "...",
  "sources": [],
  "latency": 1.72
}
```

---

# FastAPI Lifespan

The application uses FastAPI's lifespan mechanism to handle startup and shutdown logic.

At startup, the vector store is loaded so it is ready before requests arrive.

```text
Application starts
       ↓
Load configuration
       ↓
Load vector store
       ↓
Application ready
       ↓
Handle requests
       ↓
Shutdown
```

This avoids repeatedly initializing the vector store for every request.

---

# Evaluation

One of the main goals of this project is to evaluate the RAG system instead of only checking whether an answer "looks correct."

A RAG failure can happen at different stages.

For example:

```text
Question
   ↓
Poor Retrieval
   ↓
Wrong Context
   ↓
Wrong Answer
```

Or:

```text
Question
   ↓
Good Retrieval
   ↓
Correct Context
   ↓
Poor Generation
   ↓
Wrong Answer
```

The evaluation layer helps identify these differences.

Evaluation code:

```text
app/evaluation/
```

---

# Evaluation Metrics

## Context Recall

Measures whether the information required to answer a question was retrieved.

```text
Required Information
        ↓
Was it retrieved?
        ↓
Recall Score
```

A low recall score usually points toward a retrieval, chunking, or indexing problem.

---

## Context Precision

Measures how much of the retrieved context is actually relevant.

Example:

```text
5 retrieved chunks

3 relevant
2 irrelevant

Precision = 3 / 5
```

High precision means the retriever is returning more useful context instead of unnecessary information.

---

## Faithfulness

Measures whether the generated answer is supported by the retrieved context.

Example:

```text
Context:
"The company generated $10M."

Answer:
"The company generated $10M."

→ Faithful
```

If the model produces information that is not supported by the retrieved context, the faithfulness score should decrease.

---

## Answer Correctness

Measures whether the generated answer agrees with the expected answer in the evaluation dataset.

The evaluation considers:

```text
Question
   +
Expected Answer
   +
Generated Answer
```

and produces a correctness score.

---

# Evaluation Cache

LLM-based evaluation can be expensive to run repeatedly.

The project therefore includes evaluation caching.

The basic flow is:

```text
Evaluation Request
       ↓
Already evaluated?
    ↙       ↘
  Yes        No
   ↓          ↓
Return      Run evaluation
cached          ↓
result      Save result
```

Implementation:

```text
app/evaluation/evaluation_cache.py
```

This avoids unnecessarily repeating the same evaluation.

Generated cache files are kept outside version control.

---

# Evaluation Results

Evaluation result handling is separated from the evaluation logic.

Implementation:

```text
app/evaluation/evaluation_results.py
```

The results can contain values such as:

```text
Recall
Precision
Faithfulness
Correctness
Answer
```

Separating result handling from the evaluator makes it easier to extend the evaluation system later.

---

# Failure Analysis

Metrics tell us that a problem exists.

Failure analysis is intended to help understand **why** it happened.

For example:

```text
Low Recall
    ↓
Required information was not retrieved
    ↓
Possible retrieval/chunking problem
```

Another example:

```text
Good Recall
    +
Good Precision
    ↓
Low Faithfulness
    ↓
Possible generation/prompting problem
```

Implementation:

```text
app/evaluation/failure_analysis.py
```

This is useful when improving the RAG pipeline because different failures require different fixes.

---

# Docker

The application can be containerized using Docker.

Docker provides a consistent environment for running the application without depending on the exact local Python environment.

Basic flow:

```text
Dockerfile
    ↓
Build Image
    ↓
Run Container
    ↓
FastAPI
    ↓
RAG Application
```

## Build the image

```bash
docker build -t multidoc-ragops .
```

## Run the container

```bash
docker run --env-file .env -p 8000:8000 multidoc-ragops
```

The API will then be available at:

```text
http://localhost:8000
```

Swagger documentation:

```text
http://localhost:8000/docs
```

Make sure the required Gemini API key is available through `.env`.

Do not commit `.env` or API keys to Git.

---

# Local Setup

## Requirements

* Python 3.12+
* Git
* uv
* Google Gemini API key
* Docker (optional)

---

## Clone

```bash
git clone https://github.com/JaiKartikey/MultiDoc-RAGops.git

cd MultiDoc-RAGops
```

---

## Install Dependencies

Using `uv`:

```bash
uv sync
```

### Windows PowerShell

```powershell
.venv\Scripts\Activate.ps1
```

### Linux/macOS

```bash
source .venv/bin/activate
```

---

# Environment Variables

Create a `.env` file in the project root.

```env
GOOGLE_API_KEY=your_api_key_here
```

Keep the `.env` file out of version control.

---

# Run the Application

Start the FastAPI server:

```bash
uvicorn app.api.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

---

# Run Tests

Run all tests:

```bash
pytest
```

Run the embedding tests:

```bash
pytest app/rag/test_embeddings.py
```

Run the vector store tests:

```bash
pytest app/rag/test_vector_store.py
```

---

# Example

Suppose the document contains:

```text
Acme Corporation generated $10 million in revenue
during the 2025 financial year.
```

The user asks:

```text
What was Acme Corporation's revenue in 2025?
```

The application performs:

```text
Question
   ↓
Generate Question Embedding
   ↓
Search FAISS
   ↓
Retrieve Relevant Chunk
   ↓
Build Context
   ↓
Send Context + Question to Gemini
   ↓
Generate Answer
```

The expected answer would be:

```text
Acme Corporation generated $10 million in revenue
during the 2025 financial year.
```

---

# Development Progress

This project is being developed as a hands-on RAGOps/LLMOps learning project.

## Day 1 — RAG Fundamentals

* [x] Project setup
* [x] Document ingestion
* [x] Text chunking
* [x] Chunk size and overlap

## Day 2 — Embeddings & Vector Search

* [x] Gemini embeddings
* [x] FAISS vector store
* [x] Similarity search
* [x] Vector store persistence
* [x] Embedding tests
* [x] Vector store tests

## Day 3 — RAG Evaluation

* [x] Evaluation dataset
* [x] Context Recall
* [x] Context Precision
* [x] Faithfulness
* [x] Answer Correctness
* [x] Evaluation runner

## Day 4 — FastAPI

* [x] FastAPI application
* [x] `/ask` endpoint
* [x] `/health` endpoint
* [x] Request/response schemas
* [x] Application lifespan
* [x] Startup/shutdown handling
* [x] Latency tracking

## Day 5 — Evaluation Tracking

* [x] Evaluation result handling
* [x] Evaluation caching
* [x] Avoid repeated evaluations
* [x] Separate evaluation logic from result handling

## Day 6 — Failure Analysis

* [x] Failure analysis
* [x] Retrieval vs generation failure investigation
* [x] Structured evaluation failure handling

## Day 7 — RAGOps Foundation

* [x] Integrated RAG and FastAPI components
* [x] Evaluation caching
* [x] Evaluation result handling
* [x] Failure analysis
* [x] Improved API integration
* [x] Project documentation
* [x] Docker setup

### Day 7 checkpoint

At this stage, the project has moved beyond a simple RAG demo.

The current system contains:

```text
RAG
 +
Evaluation
 +
Caching
 +
Failure Analysis
 +
FastAPI
 +
Docker
```

The remaining work is focused more on production-oriented concerns such as observability, experiment tracking, CI/CD, and deployment.

---

# Roadmap

## RAG Improvements

* [ ] PDF ingestion
* [ ] DOCX ingestion
* [ ] PPTX ingestion
* [ ] CSV ingestion
* [ ] Document metadata
* [ ] Page-level citations
* [ ] Improved chunking strategies
* [ ] Hybrid search
* [ ] Reranking

## Evaluation

* [ ] Evaluation run history
* [ ] Experiment comparison
* [ ] Better failure categorization
* [ ] Automated evaluation thresholds
* [ ] RAG regression tests

## Observability

* [ ] Request IDs
* [ ] Retrieval latency
* [ ] Embedding latency
* [ ] LLM latency
* [ ] Token usage
* [ ] Cost tracking
* [ ] Tracing
* [ ] Evaluation dashboard

## LLMOps / Deployment

* [ ] Semantic caching
* [ ] Prompt versioning
* [ ] Model/version tracking
* [ ] CI/CD
* [ ] Automated quality gates
* [ ] Docker Compose
* [ ] Cloud deployment
* [ ] Production monitoring

---

# Why RAGOps?

A basic RAG implementation answers:

> "Can I retrieve information and generate an answer?"

RAGOps adds another set of questions:

> "Was the right information retrieved?"

> "Was the answer grounded in the retrieved information?"

> "How accurate is the system?"

> "Why did a particular query fail?"

> "How long does a request take?"

> "Can I reproduce the environment?"

> "Can I test changes without breaking retrieval quality?"

This project is being developed around those questions.

The goal is to understand the complete lifecycle of an LLM application rather than only the model call.

---

# Current Status

**Day 7 completed — RAGOps foundation in place.**

The current system has:

```text
Document Ingestion
        ↓
Chunking
        ↓
Gemini Embeddings
        ↓
FAISS
        ↓
Retrieval
        ↓
Gemini Generation
        ↓
FastAPI
        ↓
Evaluation
        ↓
Caching
        ↓
Failure Analysis
        ↓
Docker
```

The project is still under active development, with the next focus being observability, experiment tracking, CI/CD, and deployment.

---

# Author

**Jai Kartikey**

GitHub:
https://github.com/JaiKartikey

Project:
https://github.com/JaiKartikey/MultiDoc-RAGops

---

## Status

🚧 **Work in Progress**

Built as a practical project for learning and implementing **RAG, RAGOps, and LLMOps** concepts step by step.
