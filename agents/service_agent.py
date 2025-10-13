"""Service Integration Agent - Coordinates between services"""
import os

class ServiceAgent:
    def __init__(self, chat_client=None):
        self.name = "Service Agent"
        self.system_message = """You coordinate service-to-service communication in Northflank.

Expertise:
- HTTP/REST API integration
- Service health monitoring
- Load balancing and failover
- API authentication"""

    async def run(self, task: str) -> str:
        return f"{self.name}: Coordinating services - {task}"
