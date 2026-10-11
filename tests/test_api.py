import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.api.main import app

client = TestClient(app)

@pytest.fixture(autouse=True)
def mock_vector_store_fixture():
    mock_vs = MagicMock()
    mock_vs.chunks = ["chunk1", "chunk2", "chunk3"]
    with patch("app.api.main.load_or_create_vector_store", return_value=mock_vs):
        import app.api.main
        app.api.main.vector_store = mock_vs
        yield mock_vs

def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

def test_static_assets():
    for path in ["/style.css", "/static/style.css"]:
        res = client.get(path)
        assert res.status_code == 200
        assert "text/css" in res.headers["content-type"]

    for path in ["/script.js", "/static/script.js"]:
        res = client.get(path)
        assert res.status_code == 200
        assert "javascript" in res.headers["content-type"]

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_ask_invalid_request():
    # Empty question
    response = client.post("/ask", json={"question": ""})
    assert response.status_code == 422  # Validation error

    # Missing question
    response = client.post("/ask", json={})
    assert response.status_code == 422

@patch("app.api.main.ask_question")
def test_ask_valid_request(mock_ask_question):
    # Mock the return value of ask_question
    mock_ask_question.return_value = (
        "This is a mocked answer.",
        [{"chunk": "Mocked chunk 1", "score": 0.89}, {"chunk": "Mocked chunk 2", "score": 0.75}],
        0.1,  # retrieval_latency
        0.5   # generation_latency
    )

    response = client.post("/ask", json={"question": "What is the company name?"})
    assert response.status_code == 200
    data = response.json()
    assert "request_id" in data
    assert data["question"] == "What is the company name?"
    assert data["answer"] == "This is a mocked answer."
    assert len(data["sources"]) == 2
    assert data["sources"][0]["chunk"] == "Mocked chunk 1"
    assert "latency" in data
    assert "retrieval_latency" in data
    assert "generation_latency" in data


@patch("app.api.main.ingest_text")
def test_upload_valid_file(mock_ingest_text):
    mock_ingest_text.return_value = 3
    file_content = b"This is a test document with useful knowledge for the RAG pipeline."
    response = client.post(
        "/upload",
        files={"file": ("knowledge.txt", file_content, "text/plain")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "knowledge.txt"
    assert data["chunks_added"] == 3
    assert "total_chunks" in data
    assert "Successfully ingested" in data["message"]


@patch("app.api.main.ingest_text")
def test_upload_valid_docx(mock_ingest_text):
    import io
    from docx import Document
    doc = Document()
    doc.add_paragraph("Architecture overview for multi-document RAG operations.")
    buf = io.BytesIO()
    doc.save(buf)

    mock_ingest_text.return_value = 2
    response = client.post(
        "/upload",
        files={"file": ("spec.docx", buf.getvalue(), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "spec.docx"
    assert data["chunks_added"] == 2


@patch("app.api.main.extract_text_from_bytes")
@patch("app.api.main.ingest_text")
def test_upload_valid_pdf(mock_ingest_text, mock_extract):
    mock_extract.return_value = "Extracted content from PDF document."
    mock_ingest_text.return_value = 1
    response = client.post(
        "/upload",
        files={"file": ("paper.pdf", b"%PDF-1.4...", "application/pdf")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "paper.pdf"
    assert data["chunks_added"] == 1


def test_upload_invalid_extension():
    response = client.post(
        "/upload",
        files={"file": ("malware.exe", b"MZ...", "application/x-msdownload")}
    )
    assert response.status_code == 400
    assert "Unsupported file format" in response.json()["detail"]


def test_upload_empty_file():
    response = client.post(
        "/upload",
        files={"file": ("empty.txt", b"   ", "text/plain")}
    )
    assert response.status_code == 400
    assert "Uploaded file is empty" in response.json()["detail"]
