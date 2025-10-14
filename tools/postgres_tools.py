"""PostgreSQL operation tools for MCP"""
import os
import asyncpg
from typing import Dict, Any, Optional

class PostgresTools:
    """Tools for PostgreSQL operations."""

    pool: Optional[asyncpg.Pool] = None

    @classmethod
    async def get_pool(cls) -> Optional[asyncpg.Pool]:
        """Get or create PostgreSQL connection pool."""
        if cls.pool is None:
            postgres_uri = os.getenv("POSTGRES_URI")
            if postgres_uri:
                try:
                    cls.pool = await asyncpg.create_pool(
                        postgres_uri,
                        min_size=2,
                        max_size=10,
                        timeout=10
                    )
                except Exception as e:
                    print(f"PostgreSQL pool creation failed: {e}")
                    return None
        return cls.pool

    @staticmethod
    async def handle(name: str, arguments: Dict[str, Any]) -> str:
        """Handle PostgreSQL tool calls."""

        if name == "postgres_query":
            return await PostgresTools.postgres_query(
                arguments.get("query"),
                arguments.get("params", [])
            )
        elif name == "postgres_execute":
            return await PostgresTools.postgres_execute(
                arguments.get("query"),
                arguments.get("params", [])
            )
        elif name == "postgres_vector_search":
            return await PostgresTools.vector_search(
                arguments.get("table"),
                arguments.get("vector"),
                arguments.get("limit", 10)
            )

        return f"Unknown PostgreSQL tool: {name}"

    @staticmethod
    async def postgres_query(query: str, params: list = None) -> str:
        """Execute PostgreSQL query."""
        try:
            pool = await PostgresTools.get_pool()
            if not pool:
                return "PostgreSQL not configured. Set POSTGRES_URI environment variable."

            async with pool.acquire() as conn:
                results = await conn.fetch(query, *(params or []))
                return f"Found {len(results)} rows: {[dict(r) for r in results][:5]}"

        except Exception as e:
            return f"PostgreSQL error: {str(e)}"

    @staticmethod
    async def postgres_execute(query: str, params: list = None) -> str:
        """Execute PostgreSQL command (INSERT, UPDATE, DELETE)."""
        try:
            pool = await PostgresTools.get_pool()
            if not pool:
                return "PostgreSQL not configured. Set POSTGRES_URI environment variable."

            async with pool.acquire() as conn:
                result = await conn.execute(query, *(params or []))
                return f"Executed: {result}"

        except Exception as e:
            return f"PostgreSQL error: {str(e)}"

    @staticmethod
    async def vector_search(table: str, vector: list, limit: int = 10) -> str:
        """Perform pgvector similarity search."""
        try:
            pool = await PostgresTools.get_pool()
            if not pool:
                return "PostgreSQL not configured. Set POSTGRES_URI environment variable."

            # pgvector similarity search using cosine distance
            query = f"""
                SELECT id, content, embedding <=> $1::vector AS distance
                FROM {table}
                ORDER BY distance
                LIMIT $2
            """

            async with pool.acquire() as conn:
                results = await conn.fetch(query, vector, limit)
                return f"Found {len(results)} similar items: {[dict(r) for r in results]}"

        except Exception as e:
            return f"Vector search error: {str(e)}"

    @classmethod
    async def close(cls):
        """Close the connection pool."""
        if cls.pool:
            await cls.pool.close()
            cls.pool = None
