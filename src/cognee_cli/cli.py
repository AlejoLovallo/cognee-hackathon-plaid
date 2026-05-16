import click
from cognee_community_vector_adapter_redis import register
from cognee import config

config.set_vector_db_config({
    "vector_db_provider": "redis",
    "vector_db_url": "redis://localhost:6379",
})
from .commands import ingest, query, lint


@click.group()
def cli():
    """Cognee LLM Knowledge Wiki — ingest, query, and lint your knowledge base."""


cli.add_command(ingest)
cli.add_command(query)
cli.add_command(lint)
