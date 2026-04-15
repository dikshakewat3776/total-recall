"""Repository cloning and synchronization service."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Callable

import structlog

from app.models.repo_metadata import RepoMetadata

logger = structlog.get_logger(__name__)

CommandRunner = Callable[[list[str], Path | None], str]


def default_command_runner(command: list[str], cwd: Path | None = None) -> str:
    """Execute a shell command and return stdout."""
    completed = subprocess.run(
        command,
        cwd=str(cwd) if cwd else None,
        text=True,
        capture_output=True,
        check=True,
    )
    return completed.stdout.strip()


class RepoManager:
    """Manage cloning, pulling, and metadata tracking for repositories."""

    def __init__(
        self,
        *,
        repositories_dir: Path,
        metadata_path: Path,
        command_runner: CommandRunner = default_command_runner,
    ) -> None:
        """Initialize repository manager with configurable dependencies."""
        self.repositories_dir = repositories_dir
        self.metadata_path = metadata_path
        self.command_runner = command_runner

        self.repositories_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_path.parent.mkdir(parents=True, exist_ok=True)

    def sync_repositories(self, repo_urls: list[str]) -> list[Path]:
        """Clone or update a list of repositories and persist metadata."""
        synced_paths: list[Path] = []
        metadata = self.load_metadata()

        for repo_url in repo_urls:
            repo_path = self._clone_or_pull(repo_url)
            commit = self._current_commit(repo_path)
            repo_name = repo_path.name
            metadata[repo_name] = RepoMetadata.build(
                name=repo_name,
                url=repo_url,
                local_path=str(repo_path.resolve()),
                last_synced_commit=commit,
            )
            synced_paths.append(repo_path)
            logger.info(
                "repository_synced",
                repo_name=repo_name,
                url=repo_url,
                local_path=str(repo_path),
                commit=commit,
            )

        self.save_metadata(metadata)
        return synced_paths

    def list_repositories(self) -> list[RepoMetadata]:
        """Return all known repositories from metadata storage."""
        return list(self.load_metadata().values())

    def load_metadata(self) -> dict[str, RepoMetadata]:
        """Load metadata from JSON file, returning empty mapping when absent."""
        if not self.metadata_path.exists():
            return {}

        with self.metadata_path.open("r", encoding="utf-8") as metadata_file:
            raw = json.load(metadata_file)

        return {name: RepoMetadata(**record) for name, record in raw.items()}

    def save_metadata(self, metadata: dict[str, RepoMetadata]) -> None:
        """Persist metadata as JSON, ensuring deterministic key ordering."""
        serialized = {
            name: model.model_dump(mode="json")
            for name, model in sorted(metadata.items(), key=lambda item: item[0])
        }
        with self.metadata_path.open("w", encoding="utf-8") as metadata_file:
            json.dump(serialized, metadata_file, indent=2, sort_keys=True)

    def _clone_or_pull(self, repo_url: str) -> Path:
        """Clone missing repository or pull latest changes if present."""
        repo_name = self._repo_name_from_url(repo_url)
        local_path = self.repositories_dir / repo_name

        if local_path.exists():
            logger.info("repository_updating", repo_name=repo_name, path=str(local_path))
            self.command_runner(["git", "pull"], local_path)
        else:
            logger.info("repository_cloning", repo_name=repo_name, url=repo_url)
            self.command_runner(["git", "clone", repo_url, str(local_path)], None)

        return local_path

    def _current_commit(self, repo_path: Path) -> str:
        """Read current HEAD commit hash for a repository."""
        return self.command_runner(["git", "rev-parse", "HEAD"], repo_path)

    @staticmethod
    def _repo_name_from_url(repo_url: str) -> str:
        """Derive canonical repository directory name from URL."""
        normalized = repo_url.rstrip("/")
        name = normalized.split("/")[-1]
        if name.endswith(".git"):
            name = name[:-4]
        return name

