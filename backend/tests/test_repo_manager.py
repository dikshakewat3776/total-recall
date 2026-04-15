"""Unit tests for repository ingestion manager."""

from pathlib import Path
import subprocess

from app.ingestion.repo_manager import RepoManager


def _run(command: list[str], cwd: Path | None = None) -> str:
    """Run shell command and return stripped stdout."""
    completed = subprocess.run(
        command,
        cwd=str(cwd) if cwd else None,
        text=True,
        capture_output=True,
        check=True,
    )
    return completed.stdout.strip()


def _create_remote_repository(remote_bare: Path, source_worktree: Path, file_name: str, content: str) -> None:
    """Create or update a local bare repository from a source worktree."""
    source_worktree.mkdir(parents=True, exist_ok=True)
    _run(["git", "init"], source_worktree)
    _run(["git", "config", "user.email", "test@example.com"], source_worktree)
    _run(["git", "config", "user.name", "Test User"], source_worktree)
    (source_worktree / file_name).write_text(content, encoding="utf-8")
    _run(["git", "add", file_name], source_worktree)
    _run(["git", "commit", "-m", "initial"], source_worktree)
    _run(["git", "init", "--bare", str(remote_bare)])
    _run(["git", "remote", "add", "origin", str(remote_bare)], source_worktree)
    _run(["git", "push", "-u", "origin", "master"], source_worktree)


def test_sync_repositories_clones_and_writes_metadata(tmp_path: Path) -> None:
    """RepoManager clones repositories and records commit metadata."""
    remote_bare = tmp_path / "remote.git"
    source_worktree = tmp_path / "source"
    _create_remote_repository(remote_bare, source_worktree, "hello.py", "print('hello')\n")

    repos_dir = tmp_path / "repos"
    metadata_path = tmp_path / "repo_metadata.json"
    manager = RepoManager(repositories_dir=repos_dir, metadata_path=metadata_path)

    synced = manager.sync_repositories([str(remote_bare)])
    assert len(synced) == 1

    cloned_path = synced[0]
    assert cloned_path.exists()
    assert (cloned_path / "hello.py").exists()

    records = manager.list_repositories()
    assert len(records) == 1
    assert records[0].name == "remote"
    assert records[0].last_synced_commit


def test_sync_repositories_pulls_new_changes(tmp_path: Path) -> None:
    """RepoManager pulls updates when repository already exists locally."""
    remote_bare = tmp_path / "remote.git"
    source_worktree = tmp_path / "source"
    _create_remote_repository(remote_bare, source_worktree, "a.py", "print('v1')\n")

    repos_dir = tmp_path / "repos"
    metadata_path = tmp_path / "repo_metadata.json"
    manager = RepoManager(repositories_dir=repos_dir, metadata_path=metadata_path)
    manager.sync_repositories([str(remote_bare)])

    (source_worktree / "a.py").write_text("print('v2')\n", encoding="utf-8")
    _run(["git", "add", "a.py"], source_worktree)
    _run(["git", "commit", "-m", "update"], source_worktree)
    _run(["git", "push"], source_worktree)

    manager.sync_repositories([str(remote_bare)])
    assert (repos_dir / "remote" / "a.py").read_text(encoding="utf-8") == "print('v2')\n"

