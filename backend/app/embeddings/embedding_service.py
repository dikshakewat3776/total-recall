"""Embedding service for code nodes."""

from __future__ import annotations

from typing import Protocol

import numpy as np
import structlog
from sentence_transformers import SentenceTransformer

from app.models.code_node import CodeNode

logger = structlog.get_logger(__name__)


class EmbeddingModel(Protocol):
    """Protocol for pluggable embedding model implementations."""

    def encode(self, sentences: list[str], show_progress_bar: bool = False) -> np.ndarray:
        """Encode text sentences into vector representations."""


class CodeEmbeddingService:
    """Generate embeddings for extracted code nodes."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2", model: EmbeddingModel | None = None) -> None:
        """Initialize with default sentence-transformer model."""
        self.model = model or SentenceTransformer(model_name)

    def embed_nodes(self, nodes: list[CodeNode]) -> np.ndarray:
        """Convert code nodes into a normalized embedding matrix."""
        if not nodes:
            return np.array([], dtype=np.float32)

        texts = [self._serialize_node(node) for node in nodes]
        vectors = self.model.encode(texts, show_progress_bar=False)
        matrix = np.asarray(vectors, dtype=np.float32)
        logger.info("embeddings_generated", node_count=len(nodes), dimensions=matrix.shape[1])
        return matrix

    @staticmethod
    def _serialize_node(node: CodeNode) -> str:
        """Create semantic text representation for embedding model."""
        calls = ", ".join(node.calls)
        imports = ", ".join(node.imports)
        return (
            f"repo={node.repo}\n"
            f"file={node.file_path}\n"
            f"type={node.type}\n"
            f"name={node.name}\n"
            f"imports={imports}\n"
            f"calls={calls}\n"
            f"content:\n{node.content}"
        )

