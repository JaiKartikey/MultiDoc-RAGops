from app.core.logger import get_logger
from app.evaluation.metrics import (
    context_Recall,
    context_Precision,
    faithfulness,
    answer_correctness
    
)
from app.rag.rag_pipeline import generate_answer

logger = get_logger(__name__)

def evaluate_retrieval( vector_store, question, expected_answer, top_k=5):

# ------------------------------------------------------------------------- retrieve and combine

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

# ------------------------------------------------------------------------- making set of words

    recall = context_Recall(
        retrieved_context,
        expected_answer
    )

    precision = context_Precision(
        retrieved_chunks,
        expected_answer
    )

    generated_answer = generate_answer(
        question,
        retrieved_context
    )

    faithfulness_score = faithfulness(
        retrieved_context,
        generated_answer
    )
    correctness = answer_correctness(
        question,
        expected_answer,
        generated_answer
    )

    logger.info("Final score %.2f", recall)

    logger.info("Final score %.2f", precision)

    logger.info("Faithfulness: %.2f", faithfulness_score)

    logger.info("Faithfulness: %.2f", correctness)

    return {
        "recall": recall,
        "precision": precision,
        "faithfulness": faithfulness_score,
        "correctness": correctness,
        "answer": generated_answer

    }
