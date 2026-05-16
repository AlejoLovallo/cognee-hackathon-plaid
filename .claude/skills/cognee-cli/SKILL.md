---
name: cognee-cli
description: Use when working with the Cognee LLM Knowledge Wiki — ingesting data, querying the knowledge graph, or linting. Covers all three wiki CLI operations and when to reach for each one.
---

# Cognee Wiki CLI

The wiki is a Click-based CLI at `wiki.py` backed by Cognee's memory engine. Run all commands with `uv run python wiki.py <command>`.

## Commands

### ingest — store knowledge

```bash
# From text
uv run python wiki.py ingest "Attention is all you need"

# From a file
uv run python wiki.py ingest --file data/sample.txt
```

Calls `cognee.remember()` under the hood: chunks, extracts entities, builds a knowledge graph.

### query — recall + self-improve

```bash
# Full cycle (default): recall → improve → gap detection
uv run python wiki.py query "How does self-attention work?"

# Skip improvement (faster, read-only)
uv run python wiki.py query "What is a transformer?" --no-improve
```

With `--improve` (default on):
1. `cognee.recall()` — retrieves relevant nodes
2. `cognee.improve()` — enriches the knowledge graph
3. Gap detection — asks GPT-4o-mini what's missing, re-ingests gaps automatically

### lint — code + knowledge audit

```bash
# Both code lint and knowledge audit (default)
uv run python wiki.py lint

# Code only
uv run python wiki.py lint --no-knowledge
```

Runs Black `--check` on the codebase and reports knowledge node count. If node count is 0, the wiki is empty — run `ingest` first.

## Make shortcuts

```bash
make wiki ARGS="ingest 'text here'"
make wiki ARGS="query 'your question'"
make wiki ARGS="lint"
make lint          # auto-fix code formatting with Black
```

## Quick decision guide

| Situation | Command |
|-----------|---------|
| Adding new content | `ingest` |
| Asking a question and want the graph to grow | `query` (default) |
| Asking a question, read-only | `query --no-improve` |
| Checking code style or graph health | `lint` |
| Graph seems stale or empty | `lint`, then `ingest` |

## Source files

- Entry point: [wiki.py](../../wiki.py)
- Commands: [src/cognee_cli/commands.py](../../src/cognee_cli/commands.py)
- CLI group: [src/cognee_cli/cli.py](../../src/cognee_cli/cli.py)
- Dataset files: [data/](../../data/)
