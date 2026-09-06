import json

from app.core.config import settings
from app.core.logger import get_logger
from app.rag.main import load_or_create_vector_store

from app.evaluation.evaluator import evaluate_retrieval

def main():

    # -------------------------------------------------------------------------loading evaluation dataset

    with open( "data/evaluation.json", "r", encoding="utf-8") as file:
        dataset = json.load(file)

    
    # -------------------------------------------------------------------------loading Faiss vector

    vector_store = load_or_create_vector_store()
    recall_scores =[]
    precision_scores =[]
    faithfulness_scores = []
    correctness_scores = []

    # ------------------------------------RAG EVALUATION---------------------------------------------

    for item in dataset:
        question = item["question"]
        expected_answer = item["answer"]


        metrics = evaluate_retrieval(vector_store, question, expected_answer, top_k=settings.top_k)

        recall_scores.append(metrics["recall"])
        precision_scores.append(metrics["precision"])
        faithfulness_scores.append(metrics["faithfulness"])
        correctness_scores.append(metrics["correctness"])


#----------------------------------------------------------printinggggggggggg---------------
        print(f"\nQuestion: {question}")

        print(
            f"Context Recall: "
            f"{metrics['recall']:.2f}"
        )

        print(
            f"Context Precision: "
            f"{metrics['precision']:.2f}"
        )

        print(
            f"Faithfulness: "
            f"{metrics['faithfulness']:.2f}"
        )

        print(
            f"Answer Correctness: "
            f"{metrics['correctness']:.2f}"
        )
#---------------------------------------------------------

    average_recall = (
        sum(recall_scores) /
        len(recall_scores)
    )

    average_precision = (
        sum(precision_scores) /
        len(precision_scores)
    )
    average_faithfulness = (
        sum(faithfulness_scores) /
        len(faithfulness_scores)
    )
    average_correctness = (
        sum(correctness_scores) /
        len(correctness_scores)
    )
#---------------------------------------------------------printinggggggggggg---------------

    print("\n===== AVERAGE =====")

    print(
        f"Context Recall: "
        f"{average_recall:.2f}"
    )

    print(
        f"Context Precision: "
        f"{average_precision:.2f}"
    )
    print(
        f"Faithfulness: "
        f"{average_faithfulness:.2f}"
    )
    print(
        f"Answer Correctness: "
        f"{average_correctness:.2f}"
    )


if __name__ == "__main__":
    main()