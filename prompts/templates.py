"""MCP prompt templates"""
from mcp.types import PromptMessage, TextContent

class PromptTemplates:
    """Provides MCP prompt templates."""

    @staticmethod
    async def get(name: str, arguments: dict) -> PromptMessage:
        """Get a prompt template."""

        if name == "service-coordination":
            task = arguments.get("task", "coordinate services")
            return PromptMessage(
                role="user",
                content=TextContent(
                    type="text",
                    text=f"""Coordinate the following task across Northflank services:

Task: {task}

Available services:
- LibreChat (web interface)
- MongoDB (database)
- Redis (cache)
- MinIO (storage)
- MS-Agent-Team (AI agents)
- MCP-Hub (this service)

Plan the coordination steps and execute."""
                )
            )

        elif name == "database-operation":
            operation = arguments.get("operation", "query")
            return PromptMessage(
                role="user",
                content=TextContent(
                    type="text",
                    text=f"""Perform the following database operation:

Operation: {operation}

Available databases:
- MongoDB: User data, conversations, settings
- Redis: Sessions, cache

Guide me through the operation safely."""
                )
            )

        elif name == "workflow-builder":
            goal = arguments.get("goal", "build workflow")
            return PromptMessage(
                role="user",
                content=TextContent(
                    type="text",
                    text=f"""Build a workflow to achieve:

Goal: {goal}

Available tools:
- Service coordination
- Database operations
- LibreChat integration
- Multi-step orchestration

Design the workflow steps."""
                )
            )

        return PromptMessage(
            role="user",
            content=TextContent(type="text", text=f"Unknown prompt: {name}")
        )
