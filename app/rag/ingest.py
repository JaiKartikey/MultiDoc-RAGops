from pathlib import Path

from app.rag.chunker import chunk_text
from app.rag.vector_store import VectorStore

from app.core.logger import get_logger
from app.core.config import settings


logger = get_logger(__name__)


def load_document(file_path: str):
    """ read document """

    logger.info("Loading Document: %s", file_path)

    return Path(file_path).read_text(encoding="utf8")

def ingest_document(file_path: str):
    """ Document - text - chunks -embedding -vector store"""

    text = load_document(file_path)

    chunks = chunk_text( text, chunk_size=300, chunk_overlap=50 )

    vector_store = VectorStore()
    vector_store.build(chunks)

    vector_store.save(
        settings.storage_dir
    )
    logger.info("Document ingestion complete.")
    return vector_store

