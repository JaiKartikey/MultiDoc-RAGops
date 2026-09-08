import json
from pathlib import Path
from datetime import datetime

from app.core.config import settings


RESULTS_FILE = Path(settings.storage_dir) / "evaluation_results.json"


def load_results():
    if not RESULTS_FILE.exists():
        return []

    with open(RESULTS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_result(question, metrics, failures):
    results = load_results()

    result = {
        "timestamp": datetime.now().isoformat(),
        "question": question,
        "recall": metrics["recall"],
        "precision": metrics["precision"],
        "faithfulness": metrics["faithfulness"],
        "correctness": metrics["correctness"],
        "answer": metrics["answer"],
        "failures": failures
    }

    results.append(result)

    RESULTS_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        RESULTS_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            results,
            file,
            indent=4
        )