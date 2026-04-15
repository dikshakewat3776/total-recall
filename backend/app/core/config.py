"""Application configuration management."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings for the backend services."""

    model_config = SettingsConfigDict(env_prefix="TOTAL_RECALL_", env_file=".env", extra="ignore")

    repositories_dir: str = Field(default="data/repos", description="Local directory for cloned repositories.")
    metadata_path: str = Field(
        default="data/repo_metadata.json",
        description="JSON file path where repository sync metadata is stored.",
    )


settings = Settings()

