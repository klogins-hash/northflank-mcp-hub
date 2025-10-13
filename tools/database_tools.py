"""Database operation tools for MCP"""
import os
from typing import Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient
import redis.asyncio as redis

class DatabaseTools:
    """Tools for database operations."""

    mongo_client = None
    redis_client = None

    @classmethod
    async def get_mongo_client(cls):
        """Get or create MongoDB client."""
        if cls.mongo_client is None:
            mongo_uri = os.getenv("MONGO_URI")
            if mongo_uri:
                cls.mongo_client = AsyncIOMotorClient(mongo_uri)
        return cls.mongo_client

    @classmethod
    async def get_redis_client(cls):
        """Get or create Redis client."""
        if cls.redis_client is None:
            redis_uri = os.getenv("REDIS_URI")
            if redis_uri:
                cls.redis_client = await redis.from_url(redis_uri)
        return cls.redis_client

    @staticmethod
    async def handle(name: str, arguments: Dict[str, Any]) -> str:
        """Handle database tool calls."""

        if name == "mongo_query":
            return await DatabaseTools.mongo_query(
                arguments.get("collection"),
                arguments.get("operation"),
                arguments.get("query", {}),
                arguments.get("options", {})
            )
        elif name == "redis_get":
            return await DatabaseTools.redis_get(arguments.get("key"))
        elif name == "redis_set":
            return await DatabaseTools.redis_set(
                arguments.get("key"),
                arguments.get("value"),
                arguments.get("ttl")
            )

        return f"Unknown database tool: {name}"

    @staticmethod
    async def mongo_query(collection: str, operation: str, query: dict, options: dict) -> str:
        """Execute MongoDB query."""
        try:
            client = await DatabaseTools.get_mongo_client()
            if not client:
                return "MongoDB not configured. Set MONGO_URI environment variable."

            db = client.get_default_database()
            coll = db[collection]

            if operation == "find":
                limit = options.get("limit", 10)
                cursor = coll.find(query).limit(limit)
                results = await cursor.to_list(length=limit)
                return f"Found {len(results)} documents"
            elif operation == "findOne":
                result = await coll.find_one(query)
                return f"Found: {result is not None}"
            elif operation == "count":
                count = await coll.count_documents(query)
                return f"Count: {count}"
            else:
                return f"Unsupported operation: {operation}"

        except Exception as e:
            return f"MongoDB error: {str(e)}"

    @staticmethod
    async def redis_get(key: str) -> str:
        """Get value from Redis."""
        try:
            client = await DatabaseTools.get_redis_client()
            if not client:
                return "Redis not configured. Set REDIS_URI environment variable."

            value = await client.get(key)
            return f"Value: {value.decode() if value else 'null'}"
        except Exception as e:
            return f"Redis error: {str(e)}"

    @staticmethod
    async def redis_set(key: str, value: str, ttl: int = None) -> str:
        """Set value in Redis."""
        try:
            client = await DatabaseTools.get_redis_client()
            if not client:
                return "Redis not configured. Set REDIS_URI environment variable."

            if ttl:
                await client.setex(key, ttl, value)
            else:
                await client.set(key, value)

            return f"Set {key} = {value}" + (f" (TTL: {ttl}s)" if ttl else "")
        except Exception as e:
            return f"Redis error: {str(e)}"
