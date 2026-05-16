import asyncio
import subprocess
import sys

import click
import cognee
from openai import OpenAI


# ── helpers ───────────────────────────────────────────────────────────────────


def _run(coro):
    return asyncio.run(coro)


def _detect_gaps(question: str, recall_results: list) -> list[str]:
    """Ask an LLM what concepts are missing from the recall results."""
    context = "\n".join(r.text for r in recall_results if hasattr(r, "text"))
    if not context.strip():
        return []

    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a knowledge-gap detector. Given a question and the retrieved "
                    "context, list up to 3 short facts that are missing and would improve "
                    "the answer. Return one fact per line. Return nothing if the context is complete."
                ),
            },
            {
                "role": "user",
                "content": f"Question: {question}\n\nRetrieved context:\n{context}",
            },
        ],
        max_tokens=200,
    )
    raw = response.choices[0].message.content or ""
    return [line.strip() for line in raw.splitlines() if line.strip()]


# ── commands ──────────────────────────────────────────────────────────────────


@click.command()
@click.argument("text", required=False)
@click.option("--file", "-f", type=click.Path(exists=True), help="Ingest from a file.")
def ingest(text, file):
    """Store knowledge in the wiki."""
    if file:
        with open(file) as fh:
            text = fh.read()
    if not text:
        raise click.UsageError("Provide TEXT or --file.")

    click.echo("Ingesting…")
    _run(cognee.remember(text))
    click.echo("Stored.")


@click.command()
@click.argument("question")
@click.option(
    "--improve/--no-improve",
    default=True,
    show_default=True,
    help="Run cognee.improve() after recall.",
)
def query(question, improve):
    """Query the wiki and optionally self-improve."""
    click.echo(f"Querying: {question}")
    results = _run(cognee.recall(query_text=question))

    if results:
        for r in results:
            click.echo(f"  • {getattr(r, 'text', r)}")
    else:
        click.echo("  (no results)")

    if improve:
        click.echo("Improving knowledge graph…")
        _run(cognee.improve())
        click.echo("Improved.")

        gaps = _detect_gaps(question, results)
        if gaps:
            click.echo(f"Filling {len(gaps)} knowledge gap(s)…")
            for gap in gaps:
                _run(cognee.remember(gap))
                click.echo(f"  + {gap}")


@click.command()
@click.option(
    "--knowledge/--no-knowledge",
    default=True,
    show_default=True,
    help="Also audit knowledge graph quality.",
)
def lint(knowledge):
    """Lint code and optionally audit the knowledge graph."""
    click.echo("── Code lint (black) ──")
    result = subprocess.run(
        [sys.executable, "-m", "black", "--check", "."],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        click.echo("  Code is clean.")
    else:
        click.echo(result.stdout or result.stderr)
        click.echo("  Run `make lint` to auto-fix.", err=True)

    if knowledge:
        click.echo("── Knowledge audit ──")
        results = _run(cognee.recall(query_text="What topics are covered in this wiki?"))
        count = len(results) if results else 0
        click.echo(f"  Knowledge nodes returned: {count}")
        if count == 0:
            click.echo("  Warning: wiki appears empty. Run `ingest` first.")
