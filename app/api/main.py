from pathlib import Path
from fastapi import FastAPI, HTTPException, UploadFile, File
from app.api.schema import (
    AskRequest, AskResponse, Source, UploadResponse
)
from app.rag.rag_pipeline import ask_question
from app.rag.main import load_or_create_vector_store
from app.rag.ingest import ingest_text, extract_text_from_bytes
from app.rag.vector_store import VectorStore
from app.core.config import settings

import uuid

from contextlib import asynccontextmanager
# manage the lifespan of your application, specifically handling startup and shutdown logic.
# what is lifespan----- everything that happens from the moment your application starts until the moment it shuts down.
        # @asynccontextmanager
        # async def lifespan(app):

        #       STARTUP
        #         │
        #         │
        #         ↓
        #    initialize resources
        #         │
        #         │
        #       yield
        #         │
        #         ↓
        #     APPLICATION RUNNING
        #         │
        #         │
        #     requests handled
        #         │
        #         │
        #         ↓
        #       SHUTDOWN
        #         │
        #         ↓
        #     cleanup resources


import time

from app.core.logger import get_logger

logger = get_logger(__name__)


# ----------------------------------------------------------------------

vector_store = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global vector_store

    logger.info("starting the RAG: ")
    vector_store = load_or_create_vector_store()

    logger.info("Successfullly loaded the vector_store")

    yield

    logger.info("Shutting down RAG System")


# ----------------------------------------------------------------------


app = FastAPI(
    title="MultiDoc RAGOps",
    description="API for the MultiDoc RAGOps system ",
    version="1.0.0",
    lifespan=lifespan
)


from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
def home():
    return FileResponse("app/static/index.html")


@app.get("/style.css")
def get_style():
    return FileResponse("app/static/style.css")


@app.get("/script.js")
def get_script():
    return FileResponse("app/static/script.js")


@app.get("/health")
def health_check():
    return{
        "status":"healthy"
    }




@app.post("/ask", response_model=AskResponse)
def ask_endpoint(request: AskRequest):

    request_id = str(uuid.uuid4())

    start_time = time.perf_counter() #-----------------------------------  T1

    try:
            
        logger.info(f"[{request_id}] Question Recieved: {request.question}")

        answer, results, retrieval_latency, generation_latency = ask_question(
            vector_store,
            request.question
        )

        latency = time.perf_counter() - start_time #---------------------------T2

        logger.info(f"[{request_id}]The latency is {latency:.2f} seconds")

        return{
            "request_id":request_id,
            "question": request.question,
            "answer": answer,
            "sources": results,
            "latency": latency,
            "retrieval_latency": retrieval_latency,
            "generation_latency": generation_latency
        }

    except Exception as e:
        logger.error(f"[{request_id}] RAG Request Failed: {str(e)}")

        raise HTTPException(
            status_code=500,
            detail="An error occured"
        )


@app.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    global vector_store

    if not file.filename:
        raise HTTPException(status_code=400, detail="No file selected")

    allowed_extensions = {".txt", ".md", ".pdf", ".docx", ".csv"}
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{file_ext}'. Allowed formats: {', '.join(sorted(allowed_extensions))}"
        )

    try:
        content = await file.read()
        text = extract_text_from_bytes(content, file.filename)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error reading/processing uploaded file '{file.filename}': {str(e)}")
        raise HTTPException(status_code=400, detail=f"Failed to process file: {str(e)}")

    if not text.strip():
        raise HTTPException(status_code=400, detail="Uploaded file is empty or contains no extractable text.")

    try:
        if vector_store is None:
            vector_store = load_or_create_vector_store()

        chunks_added = ingest_text(text, vector_store)
        logger.info(f"Ingested '{file.filename}': added {chunks_added} chunks.")

        return {
            "filename": file.filename,
            "chunks_added": chunks_added,
            "total_chunks": len(vector_store.chunks),
            "message": f"Successfully ingested {file.filename} ({chunks_added} chunks added)."
        }
    except Exception as e:
        logger.error(f"Ingestion failed for {file.filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to ingest document: {str(e)}")


@app.post("/clear")
def clear_knowledge_base():
    global vector_store
    vector_store = VectorStore()

    storage_path = Path(settings.storage_dir)
    chunks_path = storage_path / "chunks.json"
    index_path = storage_path / "index.faiss"

    if chunks_path.exists():
        try:
            chunks_path.unlink()
        except Exception:
            pass

    if index_path.exists():
        try:
            index_path.unlink()
        except Exception:
            pass

    logger.info("Knowledge base has been cleared.")
    return {"message": "Knowledge base cleared successfully."}

    