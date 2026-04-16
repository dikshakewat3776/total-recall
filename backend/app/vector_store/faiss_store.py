"""FAISS vector store for semantic retrieval."""

from __future__ import annotations

import json
from pathlib import Path

import faiss
import numpy as np
import structlog

from app.models.code_node import CodeNode

logger = structlog.get_logger(__name__)


class FaissCodeIndex:
    """Store and query code node embeddings using FAISS."""

    def __init__(self, index_path: Path, mapping_path: Path) -> None:
        """Initialize disk paths for index and metadata mapping."""
        self.index_path = index_path
        self.mapping_path = mapping_path
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        self.mapping_path.parent.mkdir(parents=True, exist_ok=True)
        self._index: faiss.Index | None = None
        self._mapping: list[CodeNode] = []

    def build(self, vectors: np.ndarray, nodes: list[CodeNode]) -> None:
        """Build new index from vectors and associated code nodes."""
        if len(vectors) == 0 or len(nodes) == 0:
            raise ValueError("Vectors and nodes must be non-empty.")
        if len(vectors) != len(nodes):
            raise ValueError("Vectors and nodes length mismatch.")

        dim = int(vectors.shape[1])
        index = faiss.IndexFlatL2(dim)
        index.add(np.asarray(vectors, dtype=np.float32))
        self._index = index
        self._mapping = nodes
        logger.info("faiss_index_built", size=len(nodes), dimensions=dim)

    def save(self) -> None:
        """Persist FAISS index and vector-to-node mapping."""
        if self._index is None:
            raise ValueError("Index is not built.")

        faiss.write_index(self._index, str(self.index_path))
        payload = [node.model_dump(mode="json") for node in self._mapping]
        with self.mapping_path.open("w", encoding="utf-8") as mapping_file:
            json.dump(payload, mapping_file, indent=2)
        logger.info("faiss_index_saved", index_path=str(self.index_path), mapping_path=str(self.mapping_path))

    def load(self) -> None:
        """Load FAISS index and mapping from disk."""
        self._index = faiss.read_index(str(self.index_path))
        with self.mapping_path.open("r", encoding="utf-8") as mapping_file:
            payload = json.load(mapping_file)
        self._mapping = [CodeNode(**item) for item in payload]
        logger.info("faiss_index_loaded", size=len(self._mapping))

    def search(self, query_vector: np.ndarray, top_k: int = 5) -> list[CodeNode]:
        """Search nearest code nodes for a single query vector."""
        if self._index is None:
            raise ValueError("Index is not loaded.")
        query = np.asarray(query_vector, dtype=np.float32)
        if query.ndim == 1:
            query = query.reshape(1, -1)

        _, indices = self._index.search(query, top_k)
        results: list[CodeNode] = []
        for idx in indices[0]:
            if idx < 0 or idx >= len(self._mapping):
                continue
            results.append(self._mapping[int(idx)])
        return results

