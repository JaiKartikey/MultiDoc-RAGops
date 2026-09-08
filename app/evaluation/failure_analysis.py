def analyze_failure(metrics):

    failures = []

    if metrics["recall"] < 0.80:
        failures.append(
            "Low context recall: relevant information may be missing from retrieved chunks."
        )

    if metrics["precision"] < 0.80:
        failures.append(
            "Low context precision: retrieved chunks may contain too much irrelevant information."
        )

    if metrics["faithfulness"] < 0.80:
        failures.append(
            "Low faithfulness: the generated answer may not be fully supported by the retrieved context."
        )

    if metrics["correctness"] < 0.80:
        failures.append(
            "Low answer correctness: the generated answer may not correctly answer the question."
        )

    return failures