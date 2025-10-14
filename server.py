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
from agents.intelligent_router_agent import IntelligentRouterAgent
from federation.mcp_federation_manager import MCPFederationManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global agent team and federation
agent_team = {}
federation_manager: Optional[MCPFederationManager] = None
router_agent: Optional[IntelligentRouterAgent] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle."""
    global agent_team, federation_manager, router_agent

    logger.info("🚀 Starting Northflank MCP Hub...")

    # Initialize federation manager
    try:
        federation_manager = MCPFederationManager()
        await federation_manager.start()
        logger.info("✅ Federation manager initialized")
    except Exception as e:
        logger.error(f"❌ Error initializing federation manager: {e}")

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

    # Initialize intelligent router agent
    try:
        router_agent = IntelligentRouterAgent(federation_manager)
        agent_team["router"] = router_agent
        logger.info("✅ Intelligent router agent initialized")
    except Exception as e:
        logger.error(f"❌ Error initializing router agent: {e}")

    # Check for API keys
    has_openai = os.getenv("OPENAI_API_KEY")
    has_anthropic = os.getenv("ANTHROPIC_API_KEY")
    has_groq = os.getenv("GROQ_API_KEY")

    if not has_openai and not has_anthropic:
        logger.warning("⚠️  No OpenAI/Anthropic API keys found - agents will use fallback mode")
    else:
        logger.info("✅ AI API keys configured")

    if has_groq:
        logger.info("✅ Groq API key configured - intelligent routing enabled")
    else:
        logger.warning("⚠️  No Groq API key - using fallback routing")

    logger.info(f"🎯 MCP Hub ready on port {PORT}")

    yield

    # Shutdown
    logger.info("Shutting down Northflank MCP Hub...")
    if federation_manager:
        await federation_manager.stop()


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
            "tools": "20+ (with auto-discovery)",
            "resources": 4,
            "prompts": 3,
            "agents": 5,
            "auto_discovery": True
        },
        "services": [
            "LibreChat", "MongoDB", "Redis", "PostgreSQL", "MinIO", "RabbitMQ",
            "MS-Agent-Team", "Voice-Agent-Revolt", "Mattermost", "Token-Server",
            "...and auto-discovered services"
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
            from tools.service_discovery import get_discovery

            # Get dynamically discovered services
            discovery = get_discovery()
            dynamic_tools = await discovery.generate_service_tools()

            tools = [
                # Service Coordination
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
                    "name": "discover_services",
                    "description": "Discover all available services and addons in the project",
                    "inputSchema": {"type": "object"}
                },
                {
                    "name": "call_service",
                    "description": "Call any service by name with custom endpoint",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "service_name": {"type": "string", "description": "Service name"},
                            "endpoint": {"type": "string", "description": "API endpoint", "default": "/"},
                            "method": {"type": "string", "enum": ["GET", "POST", "PUT", "DELETE"], "default": "GET"},
                            "data": {"type": "object", "description": "Request body"}
                        },
                        "required": ["service_name"]
                    }
                },
                # MongoDB
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
                # Redis
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
                # PostgreSQL
                {
                    "name": "postgres_query",
                    "description": "Execute PostgreSQL query",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string"},
                            "params": {"type": "array"}
                        },
                        "required": ["query"]
                    }
                },
                {
                    "name": "postgres_vector_search",
                    "description": "Perform pgvector similarity search",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "table": {"type": "string"},
                            "vector": {"type": "array"},
                            "limit": {"type": "integer", "default": 10}
                        },
                        "required": ["table", "vector"]
                    }
                },
                # MinIO
                {
                    "name": "minio_list_buckets",
                    "description": "List all MinIO buckets",
                    "inputSchema": {"type": "object"}
                },
                {
                    "name": "minio_list_objects",
                    "description": "List objects in a MinIO bucket",
                    "inputSchema": {
                        "type": "object",
                        "properties": {"bucket": {"type": "string"}},
                        "required": ["bucket"]
                    }
                },
                # RabbitMQ
                {
                    "name": "rabbitmq_publish",
                    "description": "Publish message to RabbitMQ queue",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "queue": {"type": "string"},
                            "message": {"type": "object"}
                        },
                        "required": ["queue", "message"]
                    }
                },
                {
                    "name": "rabbitmq_consume",
                    "description": "Consume messages from RabbitMQ queue",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "queue": {"type": "string"},
                            "count": {"type": "integer", "default": 1}
                        },
                        "required": ["queue"]
                    }
                },
                # LibreChat
                {
                    "name": "librechat_send_message",
                    "description": "Send message to LibreChat",
                    "inputSchema": {
                        "type": "object",
                        "properties": {"message": {"type": "string"}},
                        "required": ["message"]
                    }
                },
                # Workflows
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

            # Add dynamically discovered service tools
            tools.extend(dynamic_tools)

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
            from tools.postgres_tools import PostgresTools
            from tools.minio_tools import MinIOTools
            from tools.rabbitmq_tools import RabbitMQTools
            from tools.generic_service_tools import GenericServiceTools
            from tools.service_discovery import get_discovery

            # Service coordination and discovery
            if tool_name in ["coordinate_services", "health_check_all", "list_northflank_services", "get_service_info"]:
                result = await ServiceTools.handle(tool_name, tool_args)
            elif tool_name == "discover_services":
                discovery = get_discovery()
                discovery_result = await discovery.discover_all()
                result = f"Discovered {discovery_result['total_services']} services and {discovery_result['total_addons']} addons"
            # MongoDB & Redis
            elif tool_name in ["mongo_query", "redis_get", "redis_set"]:
                result = await DatabaseTools.handle(tool_name, tool_args)
            # PostgreSQL
            elif tool_name in ["postgres_query", "postgres_execute", "postgres_vector_search"]:
                result = await PostgresTools.handle(tool_name, tool_args)
            # MinIO
            elif tool_name in ["minio_list_buckets", "minio_list_objects", "minio_get_object", "minio_put_object"]:
                result = await MinIOTools.handle(tool_name, tool_args)
            # RabbitMQ
            elif tool_name in ["rabbitmq_publish", "rabbitmq_consume", "rabbitmq_queue_info", "rabbitmq_declare_queue"]:
                result = await RabbitMQTools.handle(tool_name, tool_args)
            # LibreChat
            elif tool_name in ["librechat_send_message", "librechat_get_config"]:
                result = await LibreChatTools.handle(tool_name, tool_args)
            # Workflows
            elif tool_name in ["create_workflow", "execute_workflow"]:
                result = await WorkflowTools.handle(tool_name, tool_args)
            # Generic service calls (including dynamically discovered services)
            elif tool_name == "call_service" or tool_name.startswith("call_"):
                result = await GenericServiceTools.handle(tool_name, tool_args)
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


# ============================================================================
# FEDERATION ENDPOINTS
# ============================================================================

class RegisterServerRequest(BaseModel):
    """Request to register an external MCP server."""
    name: str
    url: str
    description: str = ""
    auth_type: Optional[str] = None
    auth_token: Optional[str] = None
    metadata: Optional[dict] = None


class RouteRequest(BaseModel):
    """Request for intelligent routing."""
    request: str
    context: Optional[dict] = None


@app.post("/federation/register")
async def register_mcp_server(req: RegisterServerRequest):
    """Register an external MCP server for federation."""
    if not federation_manager:
        raise HTTPException(status_code=503, detail="Federation manager not initialized")

    success = await federation_manager.register_server(
        name=req.name,
        url=req.url,
        description=req.description,
        auth_type=req.auth_type,
        auth_token=req.auth_token,
        metadata=req.metadata
    )

    if success:
        return {
            "success": True,
            "message": f"Server {req.name} registered successfully",
            "server": federation_manager.get_server_info(req.name)
        }
    else:
        raise HTTPException(status_code=400, detail="Failed to register server")


@app.delete("/federation/servers/{server_name}")
async def unregister_mcp_server(server_name: str):
    """Unregister an MCP server."""
    if not federation_manager:
        raise HTTPException(status_code=503, detail="Federation manager not initialized")

    success = await federation_manager.unregister_server(server_name)

    if success:
        return {"success": True, "message": f"Server {server_name} unregistered"}
    else:
        raise HTTPException(status_code=404, detail="Server not found")


@app.get("/federation/servers")
async def list_federated_servers():
    """List all registered MCP servers."""
    if not federation_manager:
        raise HTTPException(status_code=503, detail="Federation manager not initialized")

    return {
        "servers": federation_manager.list_servers(),
        "stats": federation_manager.get_stats()
    }


@app.get("/federation/servers/{server_name}")
async def get_server_info(server_name: str):
    """Get detailed information about a specific MCP server."""
    if not federation_manager:
        raise HTTPException(status_code=503, detail="Federation manager not initialized")

    info = federation_manager.get_server_info(server_name)
    if info:
        return info
    else:
        raise HTTPException(status_code=404, detail="Server not found")


@app.post("/federation/route")
async def intelligent_route(req: RouteRequest):
    """
    Intelligently route a request to the appropriate MCP server.
    Uses Groq-powered agent to determine routing.
    """
    if not router_agent:
        raise HTTPException(status_code=503, detail="Router agent not initialized")

    try:
        result = await router_agent.run(req.request, req.context)
        return result
    except Exception as e:
        logger.error(f"Routing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/federation/tools")
async def list_all_federated_tools():
    """List all tools from all federated servers (with namespacing)."""
    if not federation_manager:
        raise HTTPException(status_code=503, detail="Federation manager not initialized")

    return {
        "tools": federation_manager.get_all_tools(),
        "total": len(federation_manager.get_all_tools())
    }


@app.get("/federation/resources")
async def list_all_federated_resources():
    """List all resources from all federated servers (with namespacing)."""
    if not federation_manager:
        raise HTTPException(status_code=503, detail="Federation manager not initialized")

    return {
        "resources": federation_manager.get_all_resources(),
        "total": len(federation_manager.get_all_resources())
    }


if __name__ == "__main__":
    logger.info(f"🚀 Starting Northflank MCP Hub on port {PORT}")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=PORT,
        log_level="info"
    )
