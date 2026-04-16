"""Unit tests for FAISS vector store."""

from pathlib import Path

import numpy as np

from app.models.code_node import CodeNode
from app.vector_store.faiss_store import FaissCodeIndex


def test_faiss_build_save_load_and_search(tmp_path: Path) -> None:
    """FAISS index persists and returns expected nearest node."""
    nodes = [
        CodeNode(
            id="n1",
            name="alpha",
            type="function",
            file_path="a.py",
            repo="repo1",
            calls=[],
            imports=[],
            content="def alpha(): pass",
        ),
        CodeNode(
            id="n2",
            name="beta",
            type="function",
            file_path="b.py",
            repo="repo1",
            calls=[],
            imports=[],
            content="def beta(): pass",
        ),
    ]
    vectors = np.array([[0.0, 0.0], [10.0, 10.0]], dtype=np.float32)
    store = FaissCodeIndex(
        index_path=tmp_path / "code.index",
        mapping_path=tmp_path / "mapping.json",
    )
    store.build(vectors, nodes)
    store.save()
    store.load()

    results = store.search(np.array([0.2, 0.1], dtype=np.float32), top_k=1)
    assert len(results) == 1
    assert results[0].name == "alpha"

