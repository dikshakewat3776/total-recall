"""Example runner for Phase 2 and 3 pipeline."""

from pathlib import Path

from app.core.config import settings
from app.core.logging import configure_logging
from app.embeddings.embedding_service import CodeEmbeddingService
from app.ingestion.repo_manager import RepoManager
from app.parser.code_parser import TreeSitterCodeParser
from app.vector_store.faiss_store import FaissCodeIndex


def main() -> None:
    """Run parse + embedding + FAISS indexing for synced repositories."""
    configure_logging()
    repo_manager = RepoManager(
        repositories_dir=Path(settings.repositories_dir),
        metadata_path=Path(settings.metadata_path),
    )
    parser = TreeSitterCodeParser()
    embedder = CodeEmbeddingService(model_name=settings.embedding_model_name)
    index = FaissCodeIndex(
        index_path=Path(settings.faiss_index_path),
        mapping_path=Path(settings.faiss_mapping_path),
    )

    all_nodes = []
    for record in repo_manager.list_repositories():
        repo_path = Path(record.local_path)
        all_nodes.extend(parser.parse_repository(repo_path=repo_path, repo_name=record.name))

    if not all_nodes:
        print("No code nodes found. Run Phase 1 sync first.")
        return

    vectors = embedder.embed_nodes(all_nodes)
    index.build(vectors, all_nodes)
    index.save()
    index.load()

    sample_query = "retry logic with exponential backoff"
    query_vector = embedder.model.encode([sample_query], show_progress_bar=False)
    results = index.search(query_vector=query_vector, top_k=5)

    print(f"Parsed nodes: {len(all_nodes)}")
    print("Top semantic matches:")
    for node in results:
        print(f"- {node.repo} :: {node.file_path} :: {node.type} {node.name}")


if __name__ == "__main__":
    main()

