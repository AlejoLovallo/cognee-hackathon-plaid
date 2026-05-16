import asyncio
import subprocess
import sys
from pathlib import Path

import click
import cognee
from openai import OpenAI

from .skills import (
    detect_agent_dir,
    get_skill_content,
    install_skill,
    list_skills,
    skill_names,
)


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


# ── skills commands ───────────────────────────────────────────────────────────


@click.group("skills", help="Browse and install agent skill instructions")
def skills():
    """Browse and install agent skill instructions."""
    pass


@skills.command("list", help="List all available skills")
def skills_list():
    """List all available skills."""
    skills_data = list_skills()

    # Detect installed skills
    agent_dir = detect_agent_dir()
    installed_names: set[str] = set()
    if agent_dir:
        installed_names = {
            d.name
            for d in agent_dir.iterdir()
            if d.is_dir() and (d / "SKILL.md").is_file()
        }

    click.echo(f"\n{len(skills_data)} Available Skills:\n")
    for skill in skills_data:
        status = " [installed]" if skill["name"] in installed_names else ""
        click.echo(f"  {skill['name']}{status}")
        if skill["description"]:
            # Truncate long descriptions
            desc = skill["description"]
            if len(desc) > 100:
                desc = desc[:97] + "..."
            click.echo(f"    {desc}")
        click.echo()


@skills.command("show", help="Print the SKILL.md for a skill")
@click.argument("skill_name", required=False)
def skills_show(skill_name: str | None):
    """Print the SKILL.md for a skill."""
    available = skill_names()
    if not skill_name:
        raise click.UsageError(
            "Missing skill name. Run 'wiki skills list' to see available skills."
        )
    skill_name = skill_name.lower()
    if skill_name not in available:
        raise click.UsageError(
            f"Unknown skill: {skill_name}. Run 'wiki skills list' to see available skills."
        )
    content = get_skill_content(skill_name)
    click.echo(content)


@skills.command("install", help="Install skills into an agent skill directory")
@click.argument("name", required=False)
@click.option("--all", "install_all", is_flag=True, help="Install all available skills")
@click.option(
    "--target",
    type=click.Path(file_okay=False, path_type=Path),
    help="Target directory (default: auto-detect agent skill directory)",
)
def skills_install(
    name: str | None,
    install_all: bool,
    target: Path | None,
):
    """Install skills into an agent skill directory."""
    if not name and not install_all:
        raise click.UsageError(
            "Provide a skill name or use --all to install all skills."
        )

    # Resolve target directory
    if target is None:
        target = detect_agent_dir()
        if target is None:
            raise click.UsageError(
                "No agent skill directory found. Use --target to specify one, e.g.:\n"
                "  wiki skills install --all --target .claude/skills"
            )

    available = skill_names()

    if install_all:
        names = available
    else:
        assert name is not None  # guaranteed by the early check above
        if name not in available:
            raise click.BadParameter(
                f"Unknown skill: {name}. Available: {', '.join(available)}",
                param_hint="'NAME'",
            )
        names = [name]

    for skill_name_val in names:
        status = install_skill(skill_name_val, target)
        click.echo(
            f"  {status.capitalize()} {skill_name_val} → {target / skill_name_val}/"
        )

    click.echo(f"\n  {len(names)} skill(s) installed to {target}")

