# Total Recall

Cross-Repository Knowledge Graph + Semantic Code Search system designed to build a unified engineering brain across 50-60 repositories.

## What This Project Builds

`Total Recall` analyzes multiple repositories and links:
- code structure (functions, classes, APIs)
- relationships (calls, imports, dependencies)
- reusable patterns (auth, retry, logging, etc.)
- semantic similarity across repositories

## Architecture (Planned)

1. Repo Ingestion Service
2. Code Parsing & AST Extraction (Tree-sitter)
3. Semantic Enrichment (sentence-transformers)
4. Knowledge Graph Builder (Neo4j)
5. Vector Search Layer (FAISS)
6. Hybrid Query Engine (Graph + Vector)
7. FastAPI API Layer

## Tech Stack

- Python 3.11+
- FastAPI
- Neo4j Python driver
- FAISS (local)
- Tree-sitter
- sentence-transformers
- Celery + Redis
- pydantic-settings
- structlog

## Current Status

- Phase 1 complete: repository ingestion (clone, pull, metadata persistence)
- Active implementation lives in `backend/`
- Backend details: see `backend/README.md`

## Repository Layout

```text
total-recall/
  backend/
    app/
    tests/
    scripts/
    docker/
    docker-compose.yml
    requirements.txt
    README.md
```

## Quick Start (Backend)

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=. python scripts/run_ingestion.py
```

