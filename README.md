# Cognee LLM Wiki Hackathon

The code demonstrates Cognee’s two primary v1.0 operations:
.remember — Stores data in memory. Under the hood it runs ingestion, chunking, entity extraction, graph building, and a follow-up enrichment pass. The result is a fully queryable knowledge graph.
.recall — Retrieves from memory. It auto-routes the query to the best retrieval strategy and returns contextual results from the knowledge graph.

Main operations in Cognee v1.0 are remember, recall, improve, and forget, with legacy add, cognify, memify, and search still available as lower-level building blocks.

### Setup

