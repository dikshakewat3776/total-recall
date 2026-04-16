# Total Recall Backend

Cross-repository knowledge graph and semantic code search backend.

## Implemented Phases

### Phase 1: Repo Ingestion

`RepoManager` handles:
- cloning new repositories
- pulling updates for existing local checkouts
- persisting sync metadata (`repo name`, `url`, `local path`, `last commit`, `sync timestamp`)

### Phase 2: Tree-sitter Parsing

`TreeSitterCodeParser` extracts (Python + JavaScript):
- functions
- classes
- method calls
- imports

Unified extracted schema: `CodeNode`
- `id`
- `name`
- `type` (`function` or `class`)
- `file_path`
- `repo`
- `calls`
- `imports`
- `content`

### Phase 3: Embeddings + FAISS

`CodeEmbeddingService`:
- generates embeddings using `sentence-transformers` (`all-MiniLM-L6-v2` by default)

`FaissCodeIndex`:
- builds FAISS index from embeddings
- stores vector-to-`CodeNode` mapping in JSON
- supports load + top-k similarity search

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
2. Run Phase 1 ingestion:
   - `PYTHONPATH=. python scripts/run_ingestion.py`
3. Run Phase 2 + 3 pipeline:
   - `PYTHONPATH=. python scripts/run_phase2_phase3.py`

## Sample Input

```python
repositories = [
    "https://github.com/psf/requests.git",
    "https://github.com/pallets/flask.git",
]
```

## Sample Output (Phase 1)

```text
Synced repositories:
- data/repos/requests
- data/repos/flask
```

Metadata file (`data/repo_metadata.json`) stores sync records for each repository.

## Sample Output (Phase 2 + 3)

```text
Parsed nodes: 412
Top semantic matches:
- requests :: requests/sessions.py :: function request
- flask :: src/flask/app.py :: function wsgi_app
- ...
```

## Tests

Run:
- `PYTHONPATH=. pytest -q`

Current tests:
- `tests/test_repo_manager.py`
- `tests/test_code_parser.py`
- `tests/test_embedding_service.py`
- `tests/test_faiss_store.py`

