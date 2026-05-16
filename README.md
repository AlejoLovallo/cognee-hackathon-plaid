# Cognee LLM Knowledge Wiki

An LLM Knowledge Wiki built on [Cognee](https://docs.cognee.ai/), with three core operations: **Ingest**, **Query + Self-improve**, and **Lint**.

## How it works

Cognee's v1.0 memory engine turns documents into a queryable knowledge graph:

- `remember` — ingests text, runs chunking, entity extraction, and graph building
- `recall` — retrieves from the graph using the best-fit retrieval strategy
- `improve` — enriches and refines the knowledge graph after queries
- `forget` — resets memory (useful for a clean slate)

## Setup

```bash
uv sync
cp .env.example .env  # add your LLM_API_KEY
```

## Usage

```bash
# Ingest raw text
uv run python wiki.py ingest "Transformers are the backbone of modern LLMs"

# Ingest from a file
uv run python wiki.py ingest --file data/sample.txt

# Query the wiki (triggers recall → improve → gap detection)
uv run python wiki.py query "How do attention mechanisms work?"

# Skip self-improvement
uv run python wiki.py query "What is a transformer?" --no-improve

# Lint: Black check + knowledge graph audit
uv run python wiki.py lint
```

Or via `make`:

```bash
make wiki ARGS="ingest 'Attention is all you need'"
make wiki ARGS="query 'What is self-attention?'"
make wiki ARGS="lint"
```

## Project structure

```
src/cognee_cli/
  cli.py        # Click group entry point
  commands.py   # ingest, query, lint command implementations
wiki.py         # entry point shim
data/           # drop your dataset files here
main.py         # Cognee quickstart reference
```

## Operations

| Command | Cognee calls | What it does |
|---------|-------------|--------------|
| `ingest` | `remember()` | Stores text or file content in the knowledge graph |
| `query` | `recall()` + `improve()` | Retrieves results, refines the graph, fills knowledge gaps via LLM |
| `lint` | `recall()` | Checks code formatting (Black) + audits knowledge graph node count |
