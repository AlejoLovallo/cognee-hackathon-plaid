import cognee
import asyncio
# from dotenv import load_dotenv
from cognee_community_vector_adapter_redis import register
from cognee import config

config.set_vector_db_config({
    "vector_db_provider": "redis",
    "vector_db_url": "redis://localhost:6379",
})

async def main():
    # Create a clean slate for cognee -- reset data and system state
    await cognee.forget(everything=True)

    # Store content in memory (ingests, builds knowledge graph, enriches)
    text = "Cognee turns documents into AI memory."
    await cognee.remember(text)

    # Retrieve from memory
    results = await cognee.recall(
        query_text="What does Cognee do?"
    )

    # Print
    for result in results:
        print(result.text)

if __name__ == '__main__':
    asyncio.run(main())