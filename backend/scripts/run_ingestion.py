"""Example runner for Phase 1 repository ingestion."""

from pathlib import Path

from app.core.config import settings
from app.core.logging import configure_logging
from app.ingestion.repo_manager import RepoManager


def main() -> None:
    """Run repository sync for a small sample list."""
    configure_logging()
    manager = RepoManager(
        repositories_dir=Path(settings.repositories_dir),
        metadata_path=Path(settings.metadata_path),
    )

    # Replace with your real repositories.
    repositories = [
        "https://github.com/psf/requests.git",
        "https://github.com/pallets/flask.git",
    ]
    synced_paths = manager.sync_repositories(repositories)

    print("Synced repositories:")
    for path in synced_paths:
        print(f"- {path}")


if __name__ == "__main__":
    main()

