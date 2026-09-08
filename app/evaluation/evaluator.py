from app.core.logger import get_logger
from app.evaluation.metrics import (
    context_Recall,
    context_Precision,
    faithfulness,
    answer_correctness
)

from app.evaluation.evaluation_cache import (
    load_cache,
    save_cache,
    get_cache_key
)
import time

from app.rag.rag_pipeline import generate_answer

logger = get_logger(__name__)

def evaluate_retrieval( vector_store, question, expected_answer, top_k=5):

# ------------------------------------------------------------------------- retrieve and combine
    # Load existing cache
    cache = load_cache()

    # Create unique key for this question
    cache_key = get_cache_key(
        question,
        expected_answer
    )

    #Retrieve chunks from the question
    results = vector_store.search( question, top_k = top_k)

    # Precision ki liye -------chunks
    retrieved_chunks = [
        result["chunk"]
        for result in results
    ]

    # Recall ke liye
    #combine retrieval chunks into 1 string
    retrieved_context = " ".join( 
        result["chunk"] 
        for result in results
        )

# -------------------------------------------------------------------------

    recall = context_Recall(
        retrieved_context,
        expected_answer
    )

    precision = context_Precision(
        retrieved_chunks,
        expected_answer
    )

    # -----------------------------
    # Generate Answer
    # -----------------------------

    if cache_key in cache and "answer" in cache[cache_key]:

        generated_answer = cache[cache_key]["answer"]

        print("Using cached generated answer.")

    else:

        print("Generating new answer...")

        generated_answer = generate_answer(
            question,
            retrieved_context
        )

        if cache_key not in cache:
            cache[cache_key] = {}

        cache[cache_key]["answer"] = generated_answer

        save_cache(cache)

    # -----------------------------
    # Faithfulness
    # -----------------------------

    if cache_key in cache and "faithfulness" in cache[cache_key]:

        faithfulness_score = cache[cache_key]["faithfulness"]

        print("Using cached faithfulness score.")

    else:

        print("Calculating faithfulness...")

        faithfulness_score = faithfulness(
            retrieved_context,
            generated_answer
        )

        cache[cache_key]["faithfulness"] = faithfulness_score

        save_cache(cache)

    # -----------------------------
    # Answer Correctness
    # -----------------------------

    if cache_key in cache and "correctness" in cache[cache_key]:

        correctness = cache[cache_key]["correctness"]

        print("Using cached correctness score.")

    else:

        print("Calculating answer correctness...")

        correctness = answer_correctness(
            question,
            expected_answer,
            generated_answer
        )

        cache[cache_key]["correctness"] = correctness

        save_cache(cache)

    # -----------------------------
    # Logging
    # -----------------------------

    logger.info(
        "Context Recall: %.2f",
        recall
    )

    logger.info(
        "Context Precision: %.2f",
        precision
    )

    logger.info(
        "Faithfulness: %.2f",
        faithfulness_score
    )

    logger.info(
        "Correctness: %.2f",
        correctness
    )

    return {
        "recall": recall,
        "precision": precision,
        "faithfulness": faithfulness_score,
        "correctness": correctness,
        "answer": generated_answer
    }