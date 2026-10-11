from fastapi import FastAPI, HTTPException
from app.api.schema import (
    AskRequest,AskResponse,Source
    )
from app.rag.rag_pipeline import ask_question
from app.rag.main import load_or_create_vector_store

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


@app.get("/health")
def health_check():
    return{
        "status":"healthy"
    }


# using the asynccontextmanager here



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

    