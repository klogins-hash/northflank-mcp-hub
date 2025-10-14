# Northflank MCP Hub - Full Federation Setup

## Overview

The MCP Hub now supports **full federation** with **auto-discovery** of all services in your Northflank project. This means:

✅ **Single endpoint** for all your services
✅ **Auto-discovery** of new services (no manual configuration needed)
✅ **20+ tools** across all service types
✅ **Dynamic tool generation** for each discovered service

## Architecture

```
Claude Desktop
     ↓
[Northflank MCP Hub]  ← Single federated endpoint
     ↓
├─ Auto-Discovery (via Northflank CLI)
├─ MongoDB Tools
├─ Redis Tools
├─ PostgreSQL Tools (+ pgvector)
├─ RabbitMQ Tools
├─ MinIO Tools
├─ Generic Service Caller
└─ Dynamic Service Tools
     ↓
[All Services & Addons]
├─ Addons:
│   ├─ mongodb-librechat ✅
│   ├─ redis-cache ✅
│   ├─ postgres-db (needs env var)
│   ├─ rabbitmq (needs env var)
│   └─ minio (needs env var)
└─ Services:
    ├─ librechat ✅
    ├─ ms-agent-team ✅
    ├─ voice-agent-revolt ✅
    ├─ mattermost ✅
    ├─ mattermost-app ✅
    ├─ token-server ✅
    └─ ...any new services auto-discovered!
```

## Current Status

### ✅ Already Configured
- MongoDB (mongodb-librechat)
- Redis (redis-cache)
- LibreChat service
- Auto-discovery mechanism
- All core tools deployed

### ⚠️ Needs Configuration
Add these environment variables to the `mcp-hub` service in Northflank:

1. **PostgreSQL** (for postgres-db addon)
   ```
   POSTGRES_URI = <connection string from postgres-db addon>
   ```

2. **RabbitMQ** (for rabbitmq addon)
   ```
   RABBITMQ_URI = <connection string from rabbitmq addon>
   ```

3. **MinIO** (for minio addon)
   ```
   MINIO_URL = <MinIO URL from addon>
   MINIO_ACCESS_KEY = <access key from addon>
   MINIO_SECRET_KEY = <secret key from addon>
   ```

### How to Set Environment Variables in Northflank

1. Go to [Northflank Dashboard](https://app.northflank.com)
2. Navigate to project: `gerry-adams-revolt`
3. Open service: `mcp-hub`
4. Go to "Environment" tab
5. Click "Link Addon" for each addon:
   - postgres-db
   - rabbitmq
   - minio
6. Northflank will automatically create the environment variables
7. Redeploy the service

## Available Tools

### Service Discovery & Coordination (3 tools)
- `discover_services` - Auto-discover all services and addons
- `coordinate_services` - Coordinate operations between services
- `health_check_all` - Check health of all services
- `call_service` - Call any service by name

### Database Tools (7 tools)
- `mongo_query` - MongoDB queries
- `redis_get` / `redis_set` - Redis cache operations
- `postgres_query` - PostgreSQL queries
- `postgres_vector_search` - pgvector similarity search

### Message Queue (4 tools)
- `rabbitmq_publish` - Publish messages
- `rabbitmq_consume` - Consume messages
- `rabbitmq_queue_info` - Queue information
- `rabbitmq_declare_queue` - Create queues

### Object Storage (4 tools)
- `minio_list_buckets` - List buckets
- `minio_list_objects` - List objects in bucket
- `minio_get_object` - Get object
- `minio_put_object` - Upload object

### Application Integration (2 tools)
- `librechat_send_message` - Send message to LibreChat
- `librechat_get_config` - Get LibreChat configuration

### Workflows (2 tools)
- `create_workflow` - Create multi-step workflows
- `execute_workflow` - Execute defined workflows

### Dynamic Service Tools (6+ tools, auto-generated)
For each discovered service, a tool is dynamically generated:
- `call_ms_agent_team` - Call MS Agent Team service
- `call_voice_agent_revolt` - Call Voice Agent service
- `call_mattermost` - Call Mattermost service
- `call_mattermost_app` - Call Mattermost App service
- `call_token_server` - Call Token Server
- ...and more as services are added!

## Testing the Federation

Once environment variables are set and deployment completes:

### 1. Test Health
```bash
curl https://mcp--mcp-hub--5d689c8h7r47.code.run/health
```

### 2. Test Discovery
```bash
curl -X POST https://mcp--mcp-hub--5d689c8h7r47.code.run/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "discover_services",
      "arguments": {}
    }
  }'
```

### 3. Test Service Call
```bash
curl -X POST https://mcp--mcp-hub--5d689c8h7r47.code.run/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "call_service",
      "arguments": {
        "service_name": "librechat",
        "endpoint": "/health",
        "method": "GET"
      }
    }
  }'
```

## Auto-Discovery Details

The MCP Hub automatically discovers services by:

1. **Using Northflank CLI** - Runs `northflank list services` to get all services
2. **Extracting service info** - Gets name, status, DNS, description
3. **Generating tools** - Creates a `call_<service_name>` tool for each service
4. **Caching results** - Caches discovery for performance
5. **Refreshing on demand** - Can be refreshed via `discover_services` tool

**No manual configuration needed!** Just deploy new services to Northflank and they'll be automatically available through the MCP Hub.

## Claude Desktop Configuration

Use this configuration in Claude Desktop:

```json
{
  "mcpServers": {
    "northflank-mcp-hub": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "https://mcp--mcp-hub--5d689c8h7r47.code.run/mcp",
        "--allow-http",
        "--no-oauth",
        "--timeout",
        "30000"
      ]
    }
  }
}
```

This single endpoint gives you access to **ALL** your Northflank services!

## Benefits

### 🚀 Performance
- Connection pooling for all databases
- Caching layer for repeated queries
- Async operations throughout

### 🔄 Auto-Scaling
- Discovers new services automatically
- No code changes needed for new services
- Dynamic tool generation

### 🛡️ Reliability
- Circuit breakers for resilience
- Retry logic with exponential backoff
- Health checks for all services

### 🎯 Simplicity
- Single MCP endpoint
- Unified tool interface
- Consistent error handling

## What's Next?

1. **Set the environment variables** (see "Needs Configuration" above)
2. **Wait for deployment** (~2-3 minutes)
3. **Test the federation** (use the test commands above)
4. **Connect Claude Desktop** (use the config above)
5. **Start using all your services** through one unified interface!

## Troubleshooting

### Services not discovered
- Check Northflank CLI is installed in the container
- Verify northflank is authenticated
- Check container logs for discovery errors

### Database connections failing
- Verify environment variables are set correctly
- Check addon is running and healthy
- Test connection strings manually

### Service calls timing out
- Increase timeout in Claude Desktop config
- Check target service is running
- Verify network connectivity

## Support

For issues or questions, check:
- Container logs: `northflank get service mcp-hub --project gerry-adams-revolt logs`
- Health endpoint: `https://mcp--mcp-hub--5d689c8h7r47.code.run/health`
- Service discovery: `https://mcp--mcp-hub--5d689c8h7r47.code.run/`
