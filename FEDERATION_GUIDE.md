# MCP Federation Guide

## Universal MCP Gateway with Intelligent Routing

The Northflank MCP Hub now supports **MCP Federation** - a single MCP connection that intelligently routes to multiple backend MCP servers across all your projects.

### Architecture

```
┌────────────────────────────────────────────────────────────┐
│                   Claude Desktop / Client                   │
│                  (Single MCP Connection)                    │
└────────────────────┬───────────────────────────────────────┘
                     │
            ┌────────▼────────┐
            │   MCP Hub       │
            │   (Federation)  │
            │                 │
            │  ┌───────────┐  │
            │  │   Groq    │  │ ← Llama 3.3 70B
            │  │ Intelligent│  │   Ultra-fast routing
            │  │  Router    │  │
            │  └───────────┘  │
            └─────┬───┬───┬───┘
                  │   │   │
      ┌───────────┘   │   └───────────┐
      │               │               │
  ┌───▼───┐      ┌───▼───┐      ┌───▼───┐
  │Project│      │Project│      │ Local │
  │   A   │      │   B   │      │ Tools │
  │  MCP  │      │  MCP  │      │  MCP  │
  └───────┘      └───────┘      └───────┘
```

### Key Features

1. **Intelligent Routing** - Groq-powered agent automatically routes requests to the right server
2. **Namespaced Tools** - Tools are prefixed: `projectA.tool_name`, `projectB.tool_name`
3. **Automatic Discovery** - Fetches tools/resources from each registered server
4. **Health Monitoring** - Tracks server health and disables failing servers
5. **Multi-Step Workflows** - Agent can coordinate operations across multiple servers

---

## Quick Start

### 1. Environment Variables

Add these to your Northflank service or `.env` file:

```bash
# Required for intelligent routing
GROQ_API_KEY=gsk_...

# Optional: For agent team (use at least one)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Existing variables
MONGO_URI=mongodb://...
REDIS_URI=redis://...
```

### 2. Register External MCP Servers

Register any MCP server from other projects:

```bash
curl -X POST https://mcp--mcp-hub--5d689c8h7r47.code.run/federation/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "project_a",
    "url": "https://project-a-mcp.example.com/mcp",
    "description": "Project A MCP Server",
    "auth_type": "bearer",
    "auth_token": "your-token-here"
  }'
```

### 3. Use Intelligent Routing

Send natural language requests - the agent figures out which server to use:

```bash
curl -X POST https://mcp--mcp-hub--5d689c8h7r47.code.run/federation/route \
  -H "Content-Type: application/json" \
  -d '{
    "request": "Query user data from project A database"
  }'
```

The Groq-powered agent will:
1. Understand your request
2. Determine the best MCP server
3. Select the appropriate tool
4. Execute and return results

---

## API Endpoints

### Federation Management

#### Register MCP Server
```http
POST /federation/register
Content-Type: application/json

{
  "name": "server_name",
  "url": "https://mcp-server.example.com/mcp",
  "description": "Human-readable description",
  "auth_type": "bearer",  // Optional: "bearer", "basic", "api_key"
  "auth_token": "token",  // Optional: auth token
  "metadata": {}          // Optional: extra metadata
}
```

#### List All Servers
```http
GET /federation/servers

Response:
{
  "servers": [
    {
      "name": "project_a",
      "url": "https://...",
      "is_healthy": true,
      "tools_count": 15,
      "resources_count": 3
    }
  ],
  "stats": {
    "total_servers": 3,
    "healthy_servers": 2,
    "total_tools": 42,
    "total_resources": 8
  }
}
```

#### Get Server Info
```http
GET /federation/servers/{server_name}
```

#### Unregister Server
```http
DELETE /federation/servers/{server_name}
```

### Intelligent Routing

#### Route Request
```http
POST /federation/route
Content-Type: application/json

{
  "request": "Your natural language request here",
  "context": {
    "user_id": "123",  // Optional context
    "project": "my-project"
  }
}

Response:
{
  "success": true,
  "routing": {
    "server": "project_a",
    "tool": "query_database",
    "arguments": {...},
    "reasoning": "Request requires database query from Project A",
    "confidence": 0.95
  },
  "result": {...}
}
```

### Tool & Resource Discovery

#### List All Federated Tools
```http
GET /federation/tools

Response:
{
  "tools": [
    {
      "name": "project_a.query_users",
      "description": "[project_a] Query user database",
      "server": "project_a",
      "original_name": "query_users",
      "inputSchema": {...}
    },
    {
      "name": "project_b.deploy_service",
      "description": "[project_b] Deploy a service",
      "server": "project_b",
      "original_name": "deploy_service",
      "inputSchema": {...}
    }
  ],
  "total": 42
}
```

#### List All Federated Resources
```http
GET /federation/resources

Response:
{
  "resources": [
    {
      "uri": "project_a://database/schema",
      "name": "[project_a] Database Schema",
      "server": "project_a",
      "original_uri": "database://schema",
      "mimeType": "application/json"
    }
  ],
  "total": 8
}
```

---

## MCP Client Configuration

### Claude Desktop

Add this to your Claude Desktop MCP configuration:

```json
{
  "mcpServers": {
    "universal-hub": {
      "command": "node",
      "args": ["/path/to/mcp-client.js"],
      "env": {
        "MCP_SERVER_URL": "https://mcp--mcp-hub--5d689c8h7r47.code.run/mcp"
      }
    }
  }
}
```

### LibreChat

Add to `librechat.yaml`:

```yaml
mcpServers:
  universal-hub:
    url: "https://mcp--mcp-hub--5d689c8h7r47.code.run/mcp"
    name: "Universal MCP Hub"
    description: "Federated access to all MCP servers"
    enabled: true
```

---

## How Intelligent Routing Works

### 1. Request Analysis

The Groq agent (Llama 3.3 70B) analyzes your request:

```
User: "Get the latest deployment status from production"

Agent analyzes:
- Keywords: "deployment", "status", "production"
- Available servers: project_a, project_b, devops_tools
- Available tools in each server
```

### 2. Routing Decision

```json
{
  "server": "devops_tools",
  "tool": "get_deployment_status",
  "arguments": {
    "environment": "production"
  },
  "reasoning": "Request requires deployment status, best handled by devops_tools server",
  "confidence": 0.92
}
```

### 3. Execution

- Hub calls `devops_tools.get_deployment_status(environment="production")`
- Returns result to you

### Multi-Step Workflows

For complex requests spanning multiple servers:

```
User: "Deploy the latest code to staging and run tests"

Agent creates multi-step workflow:
1. project_a.get_latest_commit
2. devops_tools.deploy_to_staging
3. test_runner.run_integration_tests
```

---

## Examples

### Example 1: Database Query Across Projects

```bash
# Register database servers from different projects
curl -X POST .../federation/register -d '{
  "name": "users_db",
  "url": "https://users-mcp.example.com/mcp",
  "description": "User database MCP"
}'

curl -X POST .../federation/register -d '{
  "name": "orders_db",
  "url": "https://orders-mcp.example.com/mcp",
  "description": "Orders database MCP"
}'

# Natural language query - agent routes correctly
curl -X POST .../federation/route -d '{
  "request": "Get all orders for user ID 12345"
}'

# Agent automatically:
# 1. Routes to orders_db
# 2. Calls orders_db.query_orders
# 3. Returns results
```

### Example 2: Cross-Project Workflow

```bash
curl -X POST .../federation/route -d '{
  "request": "Create a new user in the auth system and initialize their profile"
}'

# Agent creates workflow:
# Step 1: auth_service.create_user
# Step 2: profile_service.initialize_profile
# Executes in sequence, passing data between steps
```

### Example 3: Service Coordination

```bash
curl -X POST .../federation/route -d '{
  "request": "Check health of all microservices and restart any that are down"
}'

# Agent:
# 1. Calls monitoring_service.health_check_all
# 2. Identifies unhealthy services
# 3. Calls devops_tools.restart_service for each
```

---

## Advanced Configuration

### Pre-register Servers via Environment

```bash
MCP_SERVERS='[
  {
    "name": "project_a",
    "url": "https://project-a.example.com/mcp",
    "description": "Project A MCP",
    "auth_type": "bearer",
    "auth_token": "${PROJECT_A_TOKEN}"
  },
  {
    "name": "project_b",
    "url": "https://project-b.example.com/mcp",
    "description": "Project B MCP"
  }
]'
```

### Custom Routing Logic

The intelligent router agent can be extended with custom routing logic. See `agents/intelligent_router_agent.py`.

### Fallback Routing

If Groq API is unavailable, the system uses keyword-based fallback routing to ensure availability.

---

## Monitoring

### Check Federation Status

```bash
curl https://mcp--mcp-hub--5d689c8h7r47.code.run/federation/servers
```

### Health Monitoring

The federation manager automatically:
- Checks server health every 30 seconds
- Disables servers after 5 consecutive failures
- Logs all health check results

### Logs

```bash
# View logs in Northflank
northflank logs get --project gerry-adams-revolt --service mcp-hub

# Look for:
# ✅ Federation manager initialized
# ✅ Intelligent router agent initialized
# ✅ Groq API key configured - intelligent routing enabled
```

---

## Troubleshooting

### Router returns fallback responses

**Cause**: No GROQ_API_KEY configured

**Solution**:
```bash
# Add to Northflank environment variables
GROQ_API_KEY=gsk_your_groq_api_key_here
```

### Server registration fails

**Causes**:
1. MCP server URL is incorrect
2. MCP server is not responding
3. Authentication failed

**Debug**:
```bash
# Test MCP server directly
curl -X POST https://target-server.com/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/list","id":1}'
```

### Tools not appearing

**Cause**: Server is registered but unhealthy

**Check**:
```bash
curl https://mcp--mcp-hub--5d689c8h7r47.code.run/federation/servers/your_server_name
```

Look for `"is_healthy": false`

---

## Performance

### Groq Llama 3.3 70B

- **Speed**: ~300 tokens/second
- **Latency**: <500ms for routing decisions
- **Cost**: Significantly lower than GPT-4

### Caching

Federation manager caches:
- Tool lists from each server (refreshed on health checks)
- Resource lists
- Server metadata

---

## Security

### Authentication

Supports multiple auth types:
- Bearer tokens
- API keys
- Basic auth

### Best Practices

1. Use environment variables for auth tokens
2. Enable HTTPS for all MCP servers
3. Implement rate limiting on federation endpoints
4. Rotate auth tokens regularly

---

## Next Steps

1. **Register your MCP servers** from other projects
2. **Configure GROQ_API_KEY** for intelligent routing
3. **Test routing** with natural language requests
4. **Monitor federation** via `/federation/servers`

Need help? Check the logs or consult the agent team via `/agents/consult`.

---

**Created**: 2025-10-13
**MCP Hub Version**: 1.0.0
**Groq Model**: llama-3.3-70b-versatile
