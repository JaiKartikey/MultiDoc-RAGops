from pathlib import Path

from app.rag.ingest import ingest_document
from app.rag.rag_pipeline import ask_question
from app.core.logger import get_logger
from app.core.config import settings
from app.rag.vector_store import VectorStore


logger = get_logger(__name__)


def load_or_create_vector_store():

    storage_path = Path(settings.storage_dir)

    chunks_path = storage_path / "chunks.json"
    index_path = storage_path / "index.faiss"

    # Check whether saved vector store exists
    if chunks_path.exists() and index_path.exists():

        logger.info("Existing vector store found.")
        logger.info("Loading vector store from storage.")

        vector_store = VectorStore()

        vector_store.load(
            settings.storage_dir
        )

        return vector_store

    # If storage does not exist, initialize a clean empty vector store
    logger.info("No existing vector store found.")
    logger.info("Initializing new empty vector store (startup auto-load disabled).")

    return VectorStore()


def main():

    logger.info("Starting RAG system")

    vector_store = load_or_create_vector_store()

    print("RAG system ready!")

    while True:

        question = input(
            "\nAsk a question "
            "(type 'exit' to quit): "
        )

        if question.lower() == "exit":
            break

        answer, results, ret_lat, gen_lat = ask_question(
            vector_store,
            question
        )

        print("\n===== ANSWER =====")
        print(answer)

        print("\n===== SOURCES =====")

        for i, result in enumerate(results):

            print(
                f"\nSource {i + 1} "
                f"(score = {result['score']})"
            )

            print(result["chunk"])


if __name__ == "__main__":
    main()