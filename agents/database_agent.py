"""Database Operations Agent - MongoDB, Redis specialist"""
import os

class DatabaseAgent:
    def __init__(self, chat_client=None):
        self.name = "Database Agent"
        self.system_message = """You are a database operations expert for MongoDB and Redis.

Expertise:
- MongoDB queries, aggregations, indexes
- Redis caching strategies, pub/sub
- Data modeling and optimization
- Connection management"""

    async def run(self, task: str) -> str:
        return f"{self.name}: Handling database operation - {task}"
