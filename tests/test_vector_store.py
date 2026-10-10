import pytest
import os
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from app.rag.vector_store import VectorStore
import numpy as np

@patch("app.rag.vector_store.create_embedding")
def test_vector_store_build_and_search(mock_create_embedding):
    # Mock the embedding function to return deterministic vectors
    mock_create_embedding.side_effect = [
        np.array([1.0, 0.0, 0.0], dtype="float32"),
        np.array([0.0, 1.0, 0.0], dtype="float32"),
    ]
    
    vs = VectorStore()
    chunks = ["Chunk 1", "Chunk 2"]
    vs.build(chunks)
    
    assert vs.index is not None
    assert len(vs.chunks) == 2
    
    # Mock embedding for search
    mock_create_embedding.side_effect = [
        np.array([1.0, 0.1, 0.0], dtype="float32")
    ]
    
    results = vs.search("Query", top_k=1)
    assert len(results) == 1
    assert results[0]["chunk"] == "Chunk 1"
    
def test_vector_store_save_and_load(tmp_path):
    vs = VectorStore()
    # Mock data
    vs.chunks = ["Chunk A", "Chunk B"]
    import faiss
    vs.index = faiss.IndexFlatIP(3)
    
    storage_dir = tmp_path / "storage"
    vs.save(str(storage_dir))
    
    assert (storage_dir / "index.faiss").exists()
    assert (storage_dir / "chunks.json").exists()
    
    vs_loaded = VectorStore()
    vs_loaded.load(str(storage_dir))
    
    assert vs_loaded.chunks == ["Chunk A", "Chunk B"]
    assert vs_loaded.index.ntotal == 0 # we didn't add any vectors, just testing load
