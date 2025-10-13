# Northflank MCP Hub

**Universal MCP Integration Hub for Northflank Projects**

Powered by Python, Microsoft Agent Framework, and Model Context Protocol.

## Overview

This MCP hub enables all services in your Northflank project to communicate seamlessly through the Model Context Protocol. It provides:

- **MCP Server**: Standards-compliant MCP server with HTTP transport
- **Microsoft Agent Team**: Specialized agents for coordination and orchestration
- **Service Integration**: Connect LibreChat, databases, APIs, and more
- **Resource Management**: Access and manage Northflank resources via MCP
- **Tool Orchestration**: Coordinate complex multi-step operations

## Architecture

```
LibreChat ──┐
            │
Services ───┼──> MCP Hub ──> Microsoft Agent Team
            │                      │
APIs ───────┘                      ├─> Database Ops
                                   ├─> Service Coordination
                                   ├─> Resource Management
                                   └─> Workflow Orchestration
```

## Features

### MCP Server Capabilities
- **Tools**: 20+ tools for service coordination, database operations, and workflow management
- **Resources**: Dynamic access to Northflank services, databases, and configurations
- **Prompts**: Pre-built templates for common operations
- **HTTP Transport**: RESTful API with JSON-RPC 2.0

### Microsoft Agent Team
- **MCP Coordinator**: Orchestrates MCP operations across services
- **Database Agent**: Manages MongoDB, Redis, and PostgreSQL operations
- **Service Agent**: Coordinates between LibreChat and other services
- **Workflow Agent**: Handles complex multi-step processes
- **Integration Agent**: Connects external APIs and services

## Quick Start

### Prerequisites
```bash
# Python 3.11+
python --version

# API Keys (at least one required)
export OPENAI_API_KEY="your-key"
# or
export ANTHROPIC_API_KEY="your-key"
```

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run server
python server.py

# Server starts on http://localhost:8080
# MCP endpoint: http://localhost:8080/mcp
```

### Test MCP Server
```bash
# List available tools
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/list","id":1}'

# Call a tool
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc":"2.0",
    "method":"tools/call",
    "id":2,
    "params":{
      "name":"coordinate_services",
      "arguments":{"operation":"health_check"}
    }
  }'
```

## Deployment to Northflank

### 1. Create New Service
```bash
# Project: gerry-adams-revolt
# Service Name: mcp-hub
# Build Method: Dockerfile
# Port: 8080
```

### 2. Environment Variables
```bash
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key

# Northflank services
MONGO_URI=mongodb://...
REDIS_URI=redis://...
LIBRECHAT_URL=https://web--librechat--5d689c8h7r47.code.run

# MCP Configuration
MCP_SERVER_NAME=northflank-mcp-hub
MCP_SERVER_VERSION=1.0.0
```

### 3. Link to LibreChat

Add to LibreChat's `librechat.yaml`:
```yaml
mcpServers:
  northflank-hub:
    url: "https://mcp-hub--gerry-adams-revolt--5d689c8h7r47.code.run/mcp"
    name: "Northflank MCP Hub"
    description: "Universal service coordinator for Northflank project"
    enabled: true
```

## Available MCP Tools

### Service Coordination
- `coordinate_services` - Coordinate operations between multiple services
- `health_check_all` - Check health of all connected services
- `service_status` - Get detailed status of specific service

### Database Operations
- `mongo_query` - Execute MongoDB queries
- `redis_get` - Get values from Redis
- `redis_set` - Set values in Redis
- `db_health_check` - Check database connectivity

### LibreChat Integration
- `librechat_chat` - Send messages to LibreChat
- `librechat_config` - Get LibreChat configuration
- `librechat_users` - Manage LibreChat users

### Workflow Orchestration
- `create_workflow` - Define multi-step workflows
- `execute_workflow` - Run defined workflows
- `workflow_status` - Check workflow execution status

### Resource Management
- `list_resources` - List available Northflank resources
- `get_resource_info` - Get detailed resource information
- `manage_resource` - Perform operations on resources

## Microsoft Agent Team

### MCP Coordinator Agent
**Role**: Primary orchestrator for all MCP operations
**Expertise**:
- MCP protocol implementation
- Tool coordination
- Service communication
- Error handling and recovery

### Database Agent
**Role**: Database operations specialist
**Expertise**:
- MongoDB queries and operations
- Redis caching strategies
- PostgreSQL when needed
- Data synchronization

### Service Integration Agent
**Role**: Connects and coordinates services
**Expertise**:
- LibreChat API integration
- Service health monitoring
- API endpoint management
- Request/response handling

### Workflow Orchestration Agent
**Role**: Manages complex multi-step processes
**Expertise**:
- Workflow design and execution
- State management
- Error recovery
- Parallel operations

## API Endpoints

### MCP Endpoint
- **URL**: `/mcp`
- **Method**: POST
- **Content-Type**: application/json
- **Protocol**: JSON-RPC 2.0

### Health Check
- **URL**: `/health`
- **Method**: GET
- **Response**: Service health status

### Agent Team
- **URL**: `/team/consult`
- **Method**: POST
- **Body**: `{"question": "your question", "specialist": "mcp_coordinator"}`

## Configuration

### Environment Variables
```bash
# Required
OPENAI_API_KEY=           # OpenAI API key
ANTHROPIC_API_KEY=        # Anthropic API key (alternative)

# Northflank Services
MONGO_URI=                # MongoDB connection string
REDIS_URI=                # Redis connection string
POSTGRES_URI=             # PostgreSQL (if used)
LIBRECHAT_URL=            # LibreChat base URL

# MCP Server
MCP_SERVER_NAME=          # Server name (default: northflank-mcp-hub)
MCP_SERVER_VERSION=       # Version (default: 1.0.0)
PORT=                     # Server port (default: 8080)

# CORS
ALLOWED_ORIGINS=          # Comma-separated origins
```

## Development

### Project Structure
```
northflank-mcp-hub/
├── server.py              # Main FastAPI server
├── mcp_server.py          # MCP server implementation
├── agents/                # Microsoft Agent Framework team
│   ├── mcp_coordinator.py
│   ├── database_agent.py
│   ├── service_agent.py
│   ├── workflow_agent.py
│   └── integration_agent.py
├── tools/                 # MCP tool implementations
│   ├── service_tools.py
│   ├── database_tools.py
│   ├── librechat_tools.py
│   └── workflow_tools.py
├── resources/             # MCP resource providers
│   └── northflank_resources.py
├── prompts/               # MCP prompt templates
│   └── templates.py
├── config/                # Configuration
│   └── settings.py
├── Dockerfile
├── requirements.txt
└── README.md
```

### Running Tests
```bash
# Run all tests
pytest

# Run specific test
pytest tests/test_mcp_server.py

# With coverage
pytest --cov=. --cov-report=html
```

## Monitoring

### Logs
```bash
# View logs in Northflank
# Services > mcp-hub > Logs

# Or use CLI
northflank logs get --project gerry-adams-revolt --service mcp-hub
```

### Metrics
- Request latency
- Tool execution times
- Error rates
- Active connections

## Troubleshooting

### MCP Connection Issues
1. Verify MCP endpoint URL is correct
2. Check CORS configuration
3. Ensure JSON-RPC 2.0 format
4. Validate tool/resource names

### Agent Team Issues
1. Check API keys are set
2. Verify agent initialization logs
3. Test individual agents via `/team/consult`
4. Review agent-specific error messages

### Database Connectivity
1. Verify connection strings
2. Check Northflank internal networking
3. Test database health endpoints
4. Review firewall/security settings

## Resources

- [Model Context Protocol Spec](https://spec.modelcontextprotocol.io/)
- [Microsoft Agent Framework](https://github.com/microsoft/agent-framework)
- [Northflank Documentation](https://northflank.com/docs)
- [LibreChat MCP Guide](https://www.librechat.ai/docs/configuration/mcp)

## License

MIT License - See LICENSE file

---

**Created**: 2025-10-13
**Project**: gerry-adams-revolt (Northflank)
**Purpose**: Universal MCP integration hub for seamless service communication
