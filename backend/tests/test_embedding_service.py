"""Unit tests for embedding service."""

import numpy as np

from app.embeddings.embedding_service import CodeEmbeddingService
from app.models.code_node import CodeNode


class FakeEmbeddingModel:
    """Deterministic fake embedding model for tests."""

    def encode(self, sentences: list[str], show_progress_bar: bool = False) -> np.ndarray:
        del show_progress_bar
        return np.array([[float(len(text)), 1.0, 2.0] for text in sentences], dtype=np.float32)


def test_embed_nodes_returns_expected_shape() -> None:
    """Embedding service returns a matrix aligned with node count."""
    service = CodeEmbeddingService(model=FakeEmbeddingModel())
    nodes = [
        CodeNode(
            id="1",
            name="a",
            type="function",
            file_path="x.py",
            repo="repo",
            calls=["print"],
            imports=["import os"],
            content="def a():\n  print('x')",
        ),
        CodeNode(
            id="2",
            name="B",
            type="class",
            file_path="y.py",
            repo="repo",
            calls=[],
            imports=[],
            content="class B:\n  pass",
        ),
    ]
    matrix = service.embed_nodes(nodes)
    assert matrix.shape == (2, 3)
    assert matrix.dtype == np.float32

