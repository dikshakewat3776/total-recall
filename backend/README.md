# Total Recall

A scalable, open-source system to transform multiple code repositories into a unified engineering knowledge graph with semantic search capabilities.

This project builds a developer “second brain” by understanding:

```text
Code structure (functions, classes, APIs)
Relationships (calls, imports, dependencies)
Reusable patterns (retry logic, auth, logging)
Semantic similarity across repositories
```

## Phase 1 Implemented: Repo Ingestion

`RepoManager` handles:
- cloning new repositories
- pulling updates for existing local checkouts
- persisting sync metadata (`repo name`, `url`, `local path`, `last commit`, `sync timestamp`)

## Folder Placement (Current)

```text
backend/
  app/
    api/
    core/
    embeddings/
    graph/
    ingestion/
    models/
    parser/
    query/
    utils/
    vector_store/
    workers/
  tests/
  scripts/
  docker/
  docker-compose.yml
  requirements.txt
  README.md
```

## Quick Start

1. Create a virtual environment and install dependencies:
   - `python3 -m venv .venv`
   - `source .venv/bin/activate`
   - `pip install -r requirements.txt`
2. Run the ingestion example:
   - `PYTHONPATH=. python scripts/run_ingestion.py`

## Sample Input

```python
repositories = [
    "https://github.com/psf/requests.git",
    "https://github.com/pallets/flask.git",
]
```

## Sample Output

```text
Synced repositories:
- data/repos/requests
- data/repos/flask
```

Metadata file (`data/repo_metadata.json`) stores sync records for each repository.

