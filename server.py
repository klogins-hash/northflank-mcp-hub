"""
Northflank MCP Hub - Main Server

FastAPI server that exposes MCP endpoints and agent team for service coordination.
"""

import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import uvicorn

from config.settings import PORT, ALLOWED_ORIGINS, SERVER_NAME, SERVER_VERSION
from agents.mcp_coordinator import MCPCoordinatorAgent
from agents.database_agent import DatabaseAgent
from agents.service_agent import ServiceAgent
from agents.workflow_agent import WorkflowAgent
from agents.integration_agent import IntegrationAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global agent team
agent_team = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle."""
    global agent_team

    logger.info("🚀 Starting Northflank MCP Hub...")

    # Initialize agent team
    try:
        agent_team["mcp_coordinator"] = MCPCoordinatorAgent()
        agent_team["database"] = DatabaseAgent()
        agent_team["service"] = ServiceAgent()
        agent_team["workflow"] = WorkflowAgent()
        agent_team["integration"] = IntegrationAgent()
        logger.info("✅ Agent team initialized")
    except Exception as e:
        logger.error(f"❌ Error initializing agents: {e}")

    # Check for API keys
    has_openai = os.getenv("OPENAI_API_KEY")
    has_anthropic = os.getenv("ANTHROPIC_API_KEY")

    if not has_openai and not has_anthropic:
        logger.warning("⚠️  No AI API keys found - agents will use fallback mode")
    else:
        logger.info("✅ AI API keys configured")

    logger.info(f"🎯 MCP Hub ready on port {PORT}")

    yield

    logger.info("Shutting down Northflank MCP Hub...")


# Create FastAPI app
app = FastAPI(
    title="Northflank MCP Hub",
    description="Universal MCP integration hub for Northflank services",
    version=SERVER_VERSION,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response models
class MCPRequest(BaseModel):
    """MCP JSON-RPC 2.0 request."""
    jsonrpc: str = "2.0"
    method: str
    params: Optional[dict] = None
    id: Optional[int] = None


class ConsultRequest(BaseModel):
    """Agent consultation request."""
    question: str
    specialist: Optional[str] = None


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with hub information."""
    return {
        "name": SERVER_NAME,
        "version": SERVER_VERSION,
        "description": "Universal MCP integration hub for Northflank",
        "endpoints": {
            "/": "Hub information",
            "/health": "Health check",
            "/mcp": "MCP JSON-RPC endpoint (POST)",
            "/agents": "List agent specialists",
            "/agents/consult": "Consult agent team (POST)",
            "/docs": "Interactive API docs"
        },
        "capabilities": {
            "tools": 12,
            "resources": 4,
            "prompts": 3,
            "agents": 5
        },
        "services": [
            "LibreChat", "MongoDB", "Redis", "MinIO", "MS-Agent-Team"
        ]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "server": SERVER_NAME,
        "version": SERVER_VERSION,
        "agents_ready": len(agent_team) == 5,
        "api_keys_configured": bool(
            os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
        ),
        "databases_configured": bool(
            os.getenv("MONGO_URI") and os.getenv("REDIS_URI")
        )
    }


@app.post("/mcp")
async def mcp_endpoint(request: MCPRequest):
    """
    MCP JSON-RPC 2.0 endpoint.

    Handles MCP protocol requests for tools, resources, and prompts.
    """
    logger.info(f"MCP request: {request.method}")

    try:
        # Handle different MCP methods
        if request.method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": request.id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {"listChanged": True},
                        "resources": {"subscribe": False, "listChanged": False},
                        "prompts": {"listChanged": False}
                    },
                    "serverInfo": {
                        "name": SERVER_NAME,
                        "version": SERVER_VERSION
                    }
                }
            }

        elif request.method == "tools/list":
            # Import tool list from MCP server
            from tools.service_tools import ServiceTools
            from tools.database_tools import DatabaseTools
            from tools.librechat_tools import LibreChatTools
            from tools.workflow_tools import WorkflowTools

            tools = [
                {
                    "name": "coordinate_services",
                    "description": "Coordinate operations between multiple services",
                    "inputSchema": {"type": "object", "properties": {"operation": {"type": "string"}}}
                },
                {
                    "name": "health_check_all",
                    "description": "Check health of all services",
                    "inputSchema": {"type": "object"}
                },
                {
                    "name": "mongo_query",
                    "description": "Execute MongoDB query",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "collection": {"type": "string"},
                            "operation": {"type": "string"}
                        },
                        "required": ["collection", "operation"]
                    }
                },
                {
                    "name": "redis_get",
                    "description": "Get value from Redis",
                    "inputSchema": {
                        "type": "object",
                        "properties": {"key": {"type": "string"}},
                        "required": ["key"]
                    }
                },
                {
                    "name": "redis_set",
                    "description": "Set value in Redis",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "key": {"type": "string"},
                            "value": {"type": "string"}
                        },
                        "required": ["key", "value"]
                    }
                },
                {
                    "name": "librechat_send_message",
                    "description": "Send message to LibreChat",
                    "inputSchema": {
                        "type": "object",
                        "properties": {"message": {"type": "string"}},
                        "required": ["message"]
                    }
                },
                {
                    "name": "create_workflow",
                    "description": "Create multi-step workflow",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "steps": {"type": "array"}
                        },
                        "required": ["name", "steps"]
                    }
                }
            ]

            return {
                "jsonrpc": "2.0",
                "id": request.id,
                "result": {"tools": tools}
            }

        elif request.method == "tools/call":
            # Execute tool
            tool_name = request.params.get("name")
            tool_args = request.params.get("arguments", {})

            logger.info(f"Calling tool: {tool_name}")

            # Route to appropriate tool handler
            from tools.service_tools import ServiceTools
            from tools.database_tools import DatabaseTools
            from tools.librechat_tools import LibreChatTools
            from tools.workflow_tools import WorkflowTools

            if tool_name in ["coordinate_services", "health_check_all", "list_northflank_services", "get_service_info"]:
                result = await ServiceTools.handle(tool_name, tool_args)
            elif tool_name in ["mongo_query", "redis_get", "redis_set"]:
                result = await DatabaseTools.handle(tool_name, tool_args)
            elif tool_name in ["librechat_send_message", "librechat_get_config"]:
                result = await LibreChatTools.handle(tool_name, tool_args)
            elif tool_name in ["create_workflow", "execute_workflow"]:
                result = await WorkflowTools.handle(tool_name, tool_args)
            else:
                result = f"Unknown tool: {tool_name}"

            return {
                "jsonrpc": "2.0",
                "id": request.id,
                "result": {
                    "content": [{"type": "text", "text": str(result)}]
                }
            }

        elif request.method == "resources/list":
            return {
                "jsonrpc": "2.0",
                "id": request.id,
                "result": {
                    "resources": [
                        {
                            "uri": "northflank://project/info",
                            "name": "Project Info",
                            "mimeType": "application/json"
                        },
                        {
                            "uri": "northflank://services/list",
                            "name": "Services List",
                            "mimeType": "application/json"
                        }
                    ]
                }
            }

        elif request.method == "resources/read":
            uri = request.params.get("uri")
            from resources.northflank_resources import NorthflankResources
            content = await NorthflankResources.read(uri)

            return {
                "jsonrpc": "2.0",
                "id": request.id,
                "result": {
                    "contents": [{"uri": uri, "mimeType": "application/json", "text": content}]
                }
            }

        else:
            raise HTTPException(status_code=400, detail=f"Unknown MCP method: {request.method}")

    except Exception as e:
        logger.error(f"MCP error: {e}")
        return {
            "jsonrpc": "2.0",
            "id": request.id,
            "error": {
                "code": -32603,
                "message": str(e)
            }
        }


@app.get("/agents")
async def list_agents():
    """List all agent specialists."""
    return {
        "agents": [
            {
                "name": "mcp_coordinator",
                "title": "MCP Coordinator",
                "description": "Primary orchestrator for MCP operations"
            },
            {
                "name": "database",
                "title": "Database Agent",
                "description": "MongoDB and Redis specialist"
            },
            {
                "name": "service",
                "title": "Service Agent",
                "description": "Service integration and coordination"
            },
            {
                "name": "workflow",
                "title": "Workflow Agent",
                "description": "Multi-step process orchestration"
            },
            {
                "name": "integration",
                "title": "Integration Agent",
                "description": "External API and service connections"
            }
        ]
    }


@app.post("/agents/consult")
async def consult_agents(request: ConsultRequest):
    """Consult the agent team."""
    specialist = request.specialist or "mcp_coordinator"

    if specialist not in agent_team:
        raise HTTPException(status_code=404, detail=f"Specialist '{specialist}' not found")

    try:
        agent = agent_team[specialist]
        result = await agent.run(request.question)

        return {
            "answer": result,
            "specialist": specialist
        }
    except Exception as e:
        logger.error(f"Agent consultation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    logger.info(f"🚀 Starting Northflank MCP Hub on port {PORT}")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=PORT,
        log_level="info"
    )
