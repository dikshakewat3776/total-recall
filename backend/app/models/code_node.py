"""Unified schema for extracted code entities."""

from pydantic import BaseModel, Field


class CodeNode(BaseModel):
    """Represents a function or class extracted from source code."""

    id: str = Field(description="Stable identifier for the code node.")
    name: str = Field(description="Function or class name.")
    type: str = Field(description="Node type, e.g. function or class.")
    file_path: str = Field(description="Path to file relative to repository root.")
    repo: str = Field(description="Repository name.")
    calls: list[str] = Field(default_factory=list, description="Called symbols from this node.")
    imports: list[str] = Field(default_factory=list, description="Imports used in this file.")
    content: str = Field(description="Raw source code segment for this node.")

