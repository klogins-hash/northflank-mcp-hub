"""
MCP Server Implementation for Northflank Hub

Implements Model Context Protocol server with tools, resources, and prompts
for coordinating services in Northflank project.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional
from mcp import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    Resource,
    Prompt,
    PromptArgument,
    PromptMessage
)

logger = logging.getLogger(__name__)


class NorthflankMCPServer:
    """MCP Server for Northflank service coordination."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the MCP server."""
        self.config = config or {}
        self.server = Server(self.config.get("name", "northflank-mcp-hub"))

        # Register handlers
        self._register_tool_handlers()
        self._register_resource_handlers()
        self._register_prompt_handlers()

        logger.info("Northflank MCP Server initialized")

    def _register_tool_handlers(self):
        """Register all tool handlers."""

        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """List all available tools."""
            return [
                # Service Coordination Tools
                Tool(
                    name="coordinate_services",
                    description="Coordinate operations between multiple services in Northflank project",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "operation": {
                                "type": "string",
                                "description": "Operation to perform: health_check, status, restart, sync",
                            },
                            "services": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of service names (empty for all)",
                            },
                        },
                        "required": ["operation"],
                    },
                ),
                Tool(
                    name="health_check_all",
                    description="Check health status of all services in the Northflank project",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "detailed": {
                                "type": "boolean",
                                "description": "Include detailed health information",
                                "default": False,
                            }
                        },
                    },
                ),

                # Database Tools
                Tool(
                    name="mongo_query",
                    description="Execute MongoDB query on LibreChat database",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "collection": {
                                "type": "string",
                                "description": "Collection name",
                            },
                            "operation": {
                                "type": "string",
                                "enum": ["find", "findOne", "count", "aggregate"],
                                "description": "Operation type",
                            },
                            "query": {
                                "type": "object",
                                "description": "Query filter",
                            },
                            "options": {
                                "type": "object",
                                "description": "Query options (limit, sort, etc)",
                            },
                        },
                        "required": ["collection", "operation"],
                    },
                ),
                Tool(
                    name="redis_get",
                    description="Get value from Redis cache",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "key": {
                                "type": "string",
                                "description": "Redis key to retrieve",
                            }
                        },
                        "required": ["key"],
                    },
                ),
                Tool(
                    name="redis_set",
                    description="Set value in Redis cache",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "key": {"type": "string", "description": "Redis key"},
                            "value": {"type": "string", "description": "Value to store"},
                            "ttl": {
                                "type": "integer",
                                "description": "Time to live in seconds (optional)",
                            },
                        },
                        "required": ["key", "value"],
                    },
                ),

                # LibreChat Integration
                Tool(
                    name="librechat_send_message",
                    description="Send a message to LibreChat and get response",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "message": {
                                "type": "string",
                                "description": "Message to send",
                            },
                            "conversation_id": {
                                "type": "string",
                                "description": "Conversation ID (optional)",
                            },
                            "model": {
                                "type": "string",
                                "description": "Model to use (optional)",
                            },
                        },
                        "required": ["message"],
                    },
                ),
                Tool(
                    name="librechat_get_config",
                    description="Get LibreChat configuration and available models",
                    inputSchema={"type": "object", "properties": {}},
                ),

                # Workflow Tools
                Tool(
                    name="create_workflow",
                    description="Create a multi-step workflow for complex operations",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "Workflow name"},
                            "steps": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "tool": {"type": "string"},
                                        "arguments": {"type": "object"},
                                        "depends_on": {
                                            "type": "array",
                                            "items": {"type": "string"},
                                        },
                                    },
                                },
                                "description": "Workflow steps",
                            },
                        },
                        "required": ["name", "steps"],
                    },
                ),
                Tool(
                    name="execute_workflow",
                    description="Execute a defined workflow",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "workflow_id": {
                                "type": "string",
                                "description": "Workflow ID to execute",
                            }
                        },
                        "required": ["workflow_id"],
                    },
                ),

                # Resource Management
                Tool(
                    name="list_northflank_services",
                    description="List all services in the Northflank project",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "status_filter": {
                                "type": "string",
                                "enum": ["all", "running", "stopped", "building"],
                                "default": "all",
                            }
                        },
                    },
                ),
                Tool(
                    name="get_service_info",
                    description="Get detailed information about a specific Northflank service",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "service_name": {
                                "type": "string",
                                "description": "Name of the service",
                            }
                        },
                        "required": ["service_name"],
                    },
                ),
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle tool calls."""
            logger.info(f"Tool called: {name} with args: {arguments}")

            try:
                # Import tool implementations
                from tools.service_tools import ServiceTools
                from tools.database_tools import DatabaseTools
                from tools.librechat_tools import LibreChatTools
                from tools.workflow_tools import WorkflowTools

                # Route to appropriate tool handler
                if name in ["coordinate_services", "health_check_all", "list_northflank_services", "get_service_info"]:
                    result = await ServiceTools.handle(name, arguments)
                elif name in ["mongo_query", "redis_get", "redis_set"]:
                    result = await DatabaseTools.handle(name, arguments)
                elif name in ["librechat_send_message", "librechat_get_config"]:
                    result = await LibreChatTools.handle(name, arguments)
                elif name in ["create_workflow", "execute_workflow"]:
                    result = await WorkflowTools.handle(name, arguments)
                else:
                    result = f"Unknown tool: {name}"

                return [TextContent(type="text", text=str(result))]

            except Exception as e:
                logger.error(f"Error executing tool {name}: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]

    def _register_resource_handlers(self):
        """Register resource handlers."""

        @self.server.list_resources()
        async def list_resources() -> List[Resource]:
            """List available resources."""
            return [
                Resource(
                    uri="northflank://project/info",
                    name="Northflank Project Info",
                    mimeType="application/json",
                    description="Information about the gerry-adams-revolt project",
                ),
                Resource(
                    uri="northflank://services/list",
                    name="Services List",
                    mimeType="application/json",
                    description="List of all services in the project",
                ),
                Resource(
                    uri="northflank://databases/config",
                    name="Database Configuration",
                    mimeType="application/json",
                    description="MongoDB, Redis configuration details",
                ),
                Resource(
                    uri="northflank://librechat/config",
                    name="LibreChat Configuration",
                    mimeType="application/json",
                    description="LibreChat service configuration",
                ),
            ]

        @self.server.read_resource()
        async def read_resource(uri: str) -> str:
            """Read a resource."""
            logger.info(f"Reading resource: {uri}")

            from resources.northflank_resources import NorthflankResources

            return await NorthflankResources.read(uri)

    def _register_prompt_handlers(self):
        """Register prompt handlers."""

        @self.server.list_prompts()
        async def list_prompts() -> List[Prompt]:
            """List available prompts."""
            return [
                Prompt(
                    name="service-coordination",
                    description="Coordinate operations across multiple services",
                    arguments=[
                        PromptArgument(
                            name="task",
                            description="Task to coordinate",
                            required=True,
                        )
                    ],
                ),
                Prompt(
                    name="database-operation",
                    description="Perform database operations with guidance",
                    arguments=[
                        PromptArgument(
                            name="operation",
                            description="Database operation to perform",
                            required=True,
                        )
                    ],
                ),
                Prompt(
                    name="workflow-builder",
                    description="Build a multi-step workflow",
                    arguments=[
                        PromptArgument(
                            name="goal",
                            description="Workflow goal",
                            required=True,
                        )
                    ],
                ),
            ]

        @self.server.get_prompt()
        async def get_prompt(name: str, arguments: Dict[str, str]) -> PromptMessage:
            """Get a prompt template."""
            from prompts.templates import PromptTemplates

            return await PromptTemplates.get(name, arguments)

    async def run(self):
        """Run the MCP server."""
        logger.info("Starting Northflank MCP Server...")
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


async def main():
    """Main entry point."""
    logging.basicConfig(level=logging.INFO)

    config = {
        "name": "northflank-mcp-hub",
        "version": "1.0.0",
    }

    server = NorthflankMCPServer(config)
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
