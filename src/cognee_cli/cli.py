import click

from .commands import ingest, query, lint


@click.group()
def cli():
    """Cognee LLM Knowledge Wiki — ingest, query, and lint your knowledge base."""


cli.add_command(ingest)
cli.add_command(query)
cli.add_command(lint)
