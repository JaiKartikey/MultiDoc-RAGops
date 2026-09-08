# MultiDoc-RAGOps

> **An end-to-end Retrieval-Augmented Generation (RAG) system built with FastAPI, Gemini, FAISS, and an evaluation pipeline — designed as a practical introduction to RAGOps / LLMOps.**

MultiDoc-RAGOps is a modular RAG application that ingests documents, splits them into overlapping chunks, generates embeddings, stores them in a FAISS vector index, retrieves relevant context for user queries, and uses Google Gemini to generate grounded answers.

The project also includes an evaluation layer for measuring retrieval quality and answer quality, making it more than a basic RAG demo — it is designed as a foundation for experimenting with **RAG reliability, evaluation, observability, and productionization**.

---

## 🚀 Project Overview

Traditional LLM applications can hallucinate when they are asked about information that was not included in their training data.

RAG solves this by giving the LLM relevant external context at query time.

MultiDoc-RAGOps follows this pipeline:

```text
                    DOCUMENTS
                       │
                       ▼
              ┌─────────────────┐
              │ Document Ingest │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │    Chunking     │
              │ 300 chars / 50  │
              │    overlap      │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │   Embeddings    │
              │ Gemini Embedding│
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │      FAISS      │
              │  Vector Index   │
              └────────┬────────┘
                       │
                       │
                 USER QUESTION
                       │
                       ▼
              ┌─────────────────┐
              │ Query Embedding │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │    Retrieval    │
              │      Top-K      │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │ Context + Query │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │     Gemini      │
              │   Generation    │
              └────────┬────────┘
                       │
                       ▼
                  FINAL ANSWER
                       │
                       ▼
              ┌─────────────────┐
              │   Evaluation    │
              │ Recall /        │
              │ Precision /     │
              │ Faithfulness /  │
              │ Correctness     │
              └─────────────────┘
```

---

# ✨ Key Features

* 📄 Document ingestion pipeline
* ✂️ Configurable text chunking with overlap
* 🧠 Gemini-based text embeddings
* 🔎 FAISS vector similarity search
* 🎯 Top-K context retrieval
* 🤖 Gemini-powered answer generation
* 🛡️ Context-grounded prompting to reduce hallucination
* ⚡ FastAPI REST API
* 🚦 Application startup/shutdown lifecycle management
* 📝 Structured application logging
* ⏱️ Request latency tracking
* 🧪 Retrieval and generation evaluation
* 📊 Context Recall
* 📊 Context Precision
* 📊 Faithfulness evaluation
* 📊 Answer Correctness evaluation
* 💾 Persistent FAISS index and chunk storage
* 🧰 Pytest-based testing
* 📦 `uv` dependency management

---

# 🏗️ Architecture

The project is divided into four main layers:

```text
app/
│
├── api/
│       └── REST API / FastAPI
│
├── core/
│       └── Configuration + Logging
│
├── rag/
│       └── Ingestion + Chunking + Embeddings
│           + Vector Store + Retrieval + Generation
│
└── evaluation/
        └── Metrics + Evaluation Pipeline
```

### High-level architecture

```text
                   ┌──────────────────────┐
                   │      FastAPI API     │
                   └──────────┬───────────┘
                              │
                              ▼
                   ┌──────────────────────┐
                   │     RAG Pipeline     │
                   └──────────┬───────────┘
                              │
                 ┌────────────┴────────────┐
                 │                         │
                 ▼                         ▼
          ┌─────────────┐          ┌─────────────┐
          │  Retrieval  │          │  Generation │
          └──────┬──────┘          └──────┬──────┘
                 │                         │
                 ▼                         ▼
          ┌─────────────┐          ┌─────────────┐
          │    FAISS    │          │    Gemini   │
          │ Vector Store│          │     LLM     │
          └─────────────┘          └─────────────┘
                 ▲
                 │
          ┌──────┴──────┐
          │  Embeddings │
          └──────┬──────┘
                 │
          ┌──────┴──────┐
          │  Documents  │
          └─────────────┘
```

---

# 🔄 RAG Pipeline

## 1. Document Ingestion

Documents are loaded into the application and converted into plain text.

Current ingestion is primarily text-file based.

```text
Document
   ↓
Read text
   ↓
Normalize content
   ↓
Chunk document
```

The ingestion logic is located in:

```text
app/rag/ingest.py
```

---

## 2. Text Chunking

Large documents are divided into smaller pieces before generating embeddings.

The current configuration uses:

```text
Chunk size:    300 characters
Overlap:        50 characters
```

The overlap helps preserve context across chunk boundaries.

For example:

```text
Chunk 1
──────────────────────────────
A company generated revenue
of $10 million during 2025.
The company expanded into...
                 ▲
                 │
              overlap
                 │
                 ▼
Chunk 2
──────────────────────────────
The company expanded into
new markets during 2025...
```

Chunking logic:

```text
app/rag/chunker.py
```

---

# 🧠 Embeddings

Each chunk is converted into a numerical vector using Google's Gemini embedding model.

```text
Text
 │
 ▼
Gemini Embedding Model
 │
 ▼
[0.012, -0.42, 0.83, ...]
```

These vectors represent the semantic meaning of the text.

The same embedding process is applied to the user's query.

```text
Document Chunk ──► Vector
User Question ───► Vector
                     │
                     ▼
              Similarity Search
```

Embedding implementation:

```text
app/rag/embeddings.py
```

---

# 🔎 Vector Search with FAISS

The project uses **FAISS (Facebook AI Similarity Search)** for efficient vector similarity search.

The vector store uses:

```text
FAISS IndexFlatIP
```

with normalized vectors.

This allows inner-product similarity to behave like cosine similarity.

The process is:

```text
Question
   │
   ▼
Question Embedding
   │
   ▼
FAISS Similarity Search
   │
   ▼
Top-K Similar Chunks
```

Vector store implementation:

```text
app/rag/vector_store.py
```

---

# 💾 Vector Store Persistence

The project persists both the FAISS index and the original chunks.

Conceptually:

```text
storage/
│
├── index.faiss
└── chunks.json
```

Why both are needed:

```text
FAISS
  │
  └── Vector #17 is similar
              │
              ▼
        chunks.json
              │
              ▼
        Actual text
```

The FAISS index provides the similarity search while the chunk mapping allows the application to recover the original text.

---

# 🤖 Answer Generation

After retrieving relevant chunks, the application constructs a context containing the retrieved information.

The LLM receives:

```text
Question
+
Retrieved Context
        │
        ▼
      Gemini
        │
        ▼
      Answer
```

The generation prompt is designed to keep the answer grounded in the retrieved context.

If the required information is not present in the context, the model is instructed not to invent an answer.

This is an important component of reducing hallucinations in RAG systems.

Generation pipeline:

```text
app/rag/rag_pipeline.py
```

---

# 🌐 FastAPI API

The application exposes the RAG system through FastAPI.

Current endpoints include:

```text
GET  /
GET  /health
POST /ask
```

## Health Check

```http
GET /health
```

Used to verify that the application is running.

---

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

The API processes the question through the complete RAG pipeline.

Conceptually:

```text
POST /ask
     │
     ▼
Question validation
     │
     ▼
Embedding
     │
     ▼
FAISS retrieval
     │
     ▼
Context construction
     │
     ▼
Gemini generation
     │
     ▼
Response
```

The response includes information such as:

```json
{
  "question": "What is the company's revenue?",
  "answer": "...",
  "sources": [],
  "latency": 1.72
}
```

The latency field makes it possible to begin monitoring application performance.

---

# ⚡ FastAPI Lifespan Management

The API uses FastAPI's application lifespan mechanism to handle startup and shutdown logic.

At startup:

```text
Application starts
       ↓
Load configuration
       ↓
Load vector store
       ↓
Initialize application state
       ↓
Accept requests
```

This prevents the vector store from unnecessarily being loaded for every request.

---

# 📊 Evaluation Framework

A RAG system should not only be evaluated by asking:

> "Does the answer look correct?"

It should also measure retrieval quality and generation quality separately.

The project contains:

```text
app/evaluation/
│
├── evaluator.py
├── metrics.py
└── run_evaluation.py
```

---

# 📈 Evaluation Metrics

## Context Recall

Measures whether the retrieved context contains the information needed to answer the question.

```text
Ground Truth
     │
     ▼
Required information
     │
     ▼
Was it retrieved?
```

High recall means the retriever is successfully finding relevant information.

---

## Context Precision

Measures how much of the retrieved context is actually relevant.

Example:

```text
Retrieved chunks:

Chunk 1 → Relevant ✓
Chunk 2 → Relevant ✓
Chunk 3 → Irrelevant ✗
Chunk 4 → Relevant ✓
Chunk 5 → Irrelevant ✗
```

The goal is to retrieve useful context without flooding the LLM with unrelated information.

---

## Faithfulness

Measures whether the generated answer is supported by the retrieved context.

Example:

```text
Context:
"The company generated $10 million."

Answer:
"The company generated $10 million."

Result:
Faithful ✓
```

Whereas:

```text
Context:
"The company generated $10 million."

Answer:
"The company generated $50 million."

Result:
Not Faithful ✗
```

The project uses an LLM-based evaluation approach for this metric.

---

## Answer Correctness

Measures whether the generated answer matches the expected/ground-truth answer.

The evaluator considers:

```text
Question
   +
Ground Truth
   +
Generated Answer
```

and produces a correctness score.

---

# 🧪 Evaluation Pipeline

The evaluation process can be represented as:

```text
Evaluation Dataset
       │
       ▼
Run RAG Pipeline
       │
       ▼
Retrieve Context
       │
       ▼
Generate Answer
       │
       ├──────────────┐
       │              │
       ▼              ▼
Retrieval Metrics   Generation Metrics
       │              │
       ├── Recall     ├── Faithfulness
       └── Precision  └── Correctness
              │
              ▼
       Evaluation Results
```

---

# 📁 Project Structure

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
│   │   └── run_evaluation.py
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
├── pyproject.toml
├── uv.lock
├── .python-version
├── .gitignore
└── README.md
```

---

# 🛠️ Tech Stack

| Category              | Technology        |
| --------------------- | ----------------- |
| Language              | Python            |
| API Framework         | FastAPI           |
| ASGI Server           | Uvicorn           |
| LLM                   | Google Gemini     |
| Embeddings            | Gemini Embeddings |
| Vector Search         | FAISS             |
| Numerical Processing  | NumPy             |
| Configuration         | Pydantic Settings |
| Environment Variables | python-dotenv     |
| Testing               | Pytest            |
| Package Management    | uv                |

---

# ⚙️ Installation

## Prerequisites

Make sure you have:

* Python 3.12+
* `uv`
* Google Gemini API key

---

## Clone the repository

```bash
git clone https://github.com/JaiKartikey/MultiDoc-RAGops.git

cd MultiDoc-RAGops
```

---

## Create the environment

Using `uv`:

```bash
uv sync
```

Activate the virtual environment if required.

### Windows PowerShell

```powershell
.venv\Scripts\Activate.ps1
```

### Linux/macOS

```bash
source .venv/bin/activate
```

---

# 🔐 Environment Variables

Create a `.env` file in the project root.

Example:

```env
GOOGLE_API_KEY=your_api_key_here
```

Do not commit your API key to GitHub.

The `.env` file should remain ignored by Git.

---

# ▶️ Running the Project

## Run the RAG pipeline

The RAG components can be executed through the modules under:

```text
app/rag/
```

---

## Start the FastAPI application

Run:

```bash
uvicorn app.api.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

FastAPI automatically provides interactive documentation at:

```text
http://127.0.0.1:8000/docs
```

and:

```text
http://127.0.0.1:8000/redoc
```

---

# 🧪 Running Tests

Run the complete test suite:

```bash
pytest
```

You can also run individual tests:

```bash
pytest app/rag/test_embeddings.py
```

```bash
pytest app/rag/test_vector_store.py
```

---

# 🔬 Example RAG Flow

Suppose the document contains:

```text
Acme Corporation generated $10 million in revenue
during the 2025 financial year.
```

The user asks:

```text
What was Acme Corporation's revenue in 2025?
```

The system performs:

```text
Question
   │
   ▼
"what was Acme Corporation's revenue?"
   │
   ▼
Generate question embedding
   │
   ▼
FAISS similarity search
   │
   ▼
Retrieve:
"Acme Corporation generated $10 million..."
   │
   ▼
Construct context
   │
   ▼
Gemini
   │
   ▼
"$10 million"
```

The important part is that Gemini is not expected to memorize this information.

It receives the relevant information at query time through retrieval.

---

# 🧩 Why This Project Is RAGOps

A basic RAG project typically looks like:

```text
Documents
   ↓
Embeddings
   ↓
Vector DB
   ↓
LLM
   ↓
Answer
```

This project extends that architecture with engineering and operational concerns:

```text
                    RAG SYSTEM
                       │
       ┌───────────────┼────────────────┐
       │               │                │
       ▼               ▼                ▼
     API          Evaluation        Configuration
       │               │                │
       ▼               ▼                ▼
   FastAPI       Metrics           Pydantic
       │               │
       └───────┬───────┘
               ▼
          Observability
               │
               ▼
         RAGOps / LLMOps
```

The goal is to understand not only **how to build RAG**, but also how to measure, test, monitor, and eventually deploy it reliably.

---

# 🎯 Current Capabilities

### RAG

* [x] Document ingestion
* [x] Text chunking
* [x] Chunk overlap
* [x] Embedding generation
* [x] FAISS vector store
* [x] Similarity search
* [x] Top-K retrieval
* [x] Context construction
* [x] Gemini generation

### Backend

* [x] FastAPI
* [x] Request schemas
* [x] Health endpoint
* [x] Ask endpoint
* [x] Application lifespan
* [x] Startup/shutdown handling
* [x] Latency measurement

### Evaluation

* [x] Evaluation dataset
* [x] Context Recall
* [x] Context Precision
* [x] Faithfulness
* [x] Answer Correctness
* [x] LLM-as-a-Judge evaluation

### Engineering

* [x] Modular project structure
* [x] Configuration management
* [x] Logging
* [x] Persistent vector store
* [x] Unit tests
* [x] Dependency locking with `uv.lock`

---

# 🚧 Roadmap

The project is intentionally being developed incrementally toward a more production-oriented RAGOps system.

## Phase 1 — RAG Foundation

* [x] Chunking
* [x] Embeddings
* [x] FAISS
* [x] Retrieval
* [x] Gemini generation

## Phase 2 — Evaluation

* [x] Evaluation dataset
* [x] Context Recall
* [x] Context Precision
* [x] Faithfulness
* [x] Answer Correctness
* [ ] Evaluation result tracking
* [ ] Evaluation caching
* [ ] Automated failure analysis

## Phase 3 — API & Backend

* [x] FastAPI
* [x] Lifespan management
* [x] Request validation
* [x] Health endpoint
* [x] Latency measurement
* [ ] Authentication
* [ ] Rate limiting
* [ ] Request IDs

## Phase 4 — Better RAG

* [ ] Multi-format document ingestion
* [ ] PDF support
* [ ] DOCX support
* [ ] PPTX support
* [ ] CSV support
* [ ] Document metadata
* [ ] Source/page-level citations
* [ ] Hybrid search
* [ ] Reranking
* [ ] Improved chunking strategies

## Phase 5 — RAG Observability

* [ ] Retrieval latency
* [ ] Embedding latency
* [ ] LLM latency
* [ ] Token usage
* [ ] Cost tracking
* [ ] Retrieval score monitoring
* [ ] Evaluation dashboards
* [ ] Structured tracing

## Phase 6 — Production / LLMOps

* [ ] Semantic caching
* [ ] Experiment tracking
* [ ] Model/version tracking
* [ ] Prompt versioning
* [ ] Automated evaluation gates
* [ ] CI/CD
* [ ] Dockerization
* [ ] Deployment
* [ ] Monitoring
* [ ] Production logging

---

# 📚 What I Learned From This Project

This project is also a hands-on exploration of several important AI engineering concepts:

### RAG

Understanding the complete retrieval → context → generation workflow.

### Vector Search

Understanding embeddings, vector similarity, cosine similarity, and FAISS.

### LLM Evaluation

Understanding why evaluating a RAG application requires more than traditional software tests.

### LLM-as-a-Judge

Using an LLM to evaluate qualitative properties such as faithfulness and correctness.

### FastAPI

Building a production-style API around an ML/LLM pipeline.

### Application Lifecycle

Understanding startup and shutdown behavior through FastAPI lifespan management.

### LLMOps / RAGOps

Moving from:

> "The model gives an answer."

toward:

> "I can measure whether the system retrieves the right information, produces a grounded answer, measure latency, analyze failures, and improve the pipeline systematically."

---

# 📌 Design Philosophy

The project is intentionally built incrementally.

Instead of immediately introducing complex infrastructure, the system starts with understandable building blocks:

```text
Python
  ↓
RAG
  ↓
FAISS
  ↓
FastAPI
  ↓
Evaluation
  ↓
Observability
  ↓
LLMOps
```

This makes it easier to understand the engineering decisions behind each layer before introducing additional infrastructure.

---

# 📊 RAG Quality Model

The project evaluates the system from two major perspectives:

```text
                  RAG QUALITY
                       │
             ┌─────────┴─────────┐
             │                   │
             ▼                   ▼
        RETRIEVAL            GENERATION
             │                   │
       ┌─────┴─────┐       ┌─────┴──────┐
       │           │       │            │
       ▼           ▼       ▼            ▼
    Recall      Precision Faithfulness Correctness
```

A strong RAG system requires both:

```text
Good Retrieval
      +
Good Generation
      =
Reliable RAG
```

A powerful LLM cannot compensate for consistently poor retrieval.

Likewise, excellent retrieval does not guarantee a correct answer if the generation layer ignores or misinterprets the context.

---

# 🤝 Future Vision

The long-term goal of MultiDoc-RAGOps is to evolve the project into a complete RAGOps platform capable of:

```text
                DOCUMENTS
                    │
                    ▼
              INGESTION PIPELINE
                    │
                    ▼
                INDEXING
                    │
                    ▼
               RETRIEVAL
                    │
                    ▼
                RERANKING
                    │
                    ▼
                GENERATION
                    │
                    ▼
                  API
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
     OBSERVABILITY        EVALUATION
          │                   │
          └─────────┬─────────┘
                    ▼
             EXPERIMENTATION
                    │
                    ▼
                 CI/CD
                    │
                    ▼
               DEPLOYMENT
```

The objective is to build a system where every stage of the RAG lifecycle can be **tested, measured, monitored, and improved**.

---

# 👨‍💻 Author

**Jai Kartikey**

GitHub: [@JaiKartikey](https://github.com/JaiKartikey)

Repository: [MultiDoc-RAGOps](https://github.com/JaiKartikey/MultiDoc-RAGops)

---

# ⭐ Project Status

🚧 **Active Development**

MultiDoc-RAGOps is an evolving learning and engineering project focused on understanding the complete lifecycle of production-oriented RAG systems.

More RAGOps and LLMOps capabilities will be added progressively.
