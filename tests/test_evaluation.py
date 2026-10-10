import pytest
from unittest.mock import patch, MagicMock
from app.evaluation.evaluator import evaluate_retrieval
from app.evaluation.failure_analysis import analyze_failure

@patch("app.evaluation.evaluator.context_Recall")
@patch("app.evaluation.evaluator.context_Precision")
@patch("app.evaluation.evaluator.faithfulness")
@patch("app.evaluation.evaluator.answer_correctness")
@patch("app.evaluation.evaluator.generate_answer")
@patch("app.evaluation.evaluator.load_cache")
@patch("app.evaluation.evaluator.save_cache")
def test_evaluate_retrieval(mock_save_cache, mock_load_cache, mock_generate_answer, mock_correctness, mock_faithfulness, mock_precision, mock_recall):
    mock_load_cache.return_value = {}
    mock_generate_answer.return_value = "Mocked answer"
    mock_recall.return_value = 1.0
    mock_precision.return_value = 1.0
    mock_faithfulness.return_value = 1.0
    mock_correctness.return_value = 1.0

    mock_vector_store = MagicMock()
    mock_vector_store.search.return_value = [{"chunk": "Mock chunk 1", "score": 0.9}]

    result = evaluate_retrieval(mock_vector_store, "Test question", "Test expected answer")

    assert result["recall"] == 1.0
    assert result["precision"] == 1.0
    assert result["faithfulness"] == 1.0
    assert result["correctness"] == 1.0
    assert result["answer"] == "Mocked answer"
    
def test_failure_analysis():
    metrics_retrieval_fail = {"recall": 0.5, "precision": 0.4, "faithfulness": 0.9, "correctness": 0.5}
    failures_retrieval = analyze_failure(metrics_retrieval_fail)
    
    assert any("Low context recall" in f for f in failures_retrieval)
    assert any("Low context precision" in f for f in failures_retrieval)
    assert any("Low answer correctness" in f for f in failures_retrieval)

    metrics_gen_fail = {"recall": 0.9, "precision": 0.8, "faithfulness": 0.4, "correctness": 0.9}
    failures_gen = analyze_failure(metrics_gen_fail)
    
    assert any("Low faithfulness" in f for f in failures_gen)
    assert not any("Low context recall" in f for f in failures_gen)
