"""Models for repository ingestion metadata."""

from datetime import datetime, timezone

from pydantic import BaseModel, Field


class RepoMetadata(BaseModel):
    """Metadata captured for each synced repository."""

    name: str = Field(description="Repository name derived from URL.")
    url: str = Field(description="Repository clone URL.")
    local_path: str = Field(description="Absolute local checkout path.")
    last_synced_commit: str = Field(description="Most recent local HEAD commit hash.")
    last_synced_at: str = Field(description="UTC timestamp for latest successful sync.")

    @classmethod
    def build(
        cls,
        *,
        name: str,
        url: str,
        local_path: str,
        last_synced_commit: str,
    ) -> "RepoMetadata":
        """Build a metadata object with current UTC sync timestamp."""
        return cls(
            name=name,
            url=url,
            local_path=local_path,
            last_synced_commit=last_synced_commit,
            last_synced_at=datetime.now(timezone.utc).isoformat(),
        )

