# Quick Start Guide - Deploy in 5 Minutes

## Step 1: Create Service in Northflank (2 min)

1. Go to https://app.northflank.com
2. Select project: **gerry-adams-revolt**
3. Click **"Create Service"** → **"Combined service"**
4. Fill in:
   - **Name**: `mcp-hub`
   - **Source**: Select GitHub → `klogins-hash/northflank-mcp-hub`
   - **Branch**: `master`
   - **Build Type**: Dockerfile
   - **Dockerfile Path**: `/Dockerfile`
5. Scroll to **Ports**:
   - Port: `8080`
   - Protocol: HTTP
   - Check "Publicly expose"
   - Check "Generate domain"
6. Click **"Create Service"**

## Step 2: Add Environment Variables (1 min)

In the service settings, go to **Environment** tab and add:

### Required (at least one AI API key):
```
OPENAI_API_KEY=your-key-here
```
OR
```
ANTHROPIC_API_KEY=your-key-here
```

### Database Connections (get from Northflank Addons):
```
MONGO_URI=mongodb://058fd6e729a03a44:11233119620e33b09775db1f9a846fb1@mongo-0.mongodb-librechat--5d689c8h7r47.addon.code.run:27017/deedd2b3db59?replicaSet=rs0&authSource=deedd2b3db59&tls=true

REDIS_URI=redis://default:f95e10448ca2ab8a6a8dfb97972bbca8@master.redis-cache--5d689c8h7r47.addon.code.run:6379
```

### LibreChat URL:
```
LIBRECHAT_URL=https://web--librechat--5d689c8h7r47.code.run
```

### Optional Config:
```
PORT=8080
MCP_SERVER_NAME=northflank-mcp-hub
ALLOWED_ORIGINS=http://localhost:3080,https://web--librechat--5d689c8h7r47.code.run
```

Click **"Save"** - service will auto-redeploy.

## Step 3: Connect to LibreChat (2 min)

### Option A: Via librechat.yaml (Recommended)

1. Go to LibreChat service in Northflank
2. Click **"Files"** tab → Navigate to `/librechat.yaml`
3. Add this configuration:

```yaml
mcpServers:
  northflank-hub:
    url: "https://mcp-hub--gerry-adams-revolt--5d689c8h7r47.code.run/mcp"
    name: "Northflank MCP Hub"
    description: "Universal service coordinator with 12+ tools for databases, services, and workflows"
    enabled: true
    transport: "http"
```

4. Save and **Restart LibreChat service**

### Option B: Via Environment Variable

Add to LibreChat environment:
```
MCP_SERVERS={"northflank-hub":{"url":"https://mcp-hub--gerry-adams-revolt--5d689c8h7r47.code.run/mcp","enabled":true}}
```

## Step 4: Test (30 seconds)

### Test MCP Hub is running:
```bash
curl https://mcp-hub--gerry-adams-revolt--5d689c8h7r47.code.run/health
```

Should return:
```json
{
  "status": "healthy",
  "agents_ready": true,
  "api_keys_configured": true
}
```

### Test MCP endpoint:
```bash
curl -X POST https://mcp-hub--gerry-adams-revolt--5d689c8h7r47.code.run/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/list","id":1}'
```

### Test in LibreChat:

1. Open LibreChat: https://web--librechat--5d689c8h7r47.code.run
2. Start a new conversation
3. Look for tools/plugins icon
4. You should see **"Northflank MCP Hub"** with available tools
5. Try asking: "Check the health of all services"

## Available Tools

Once connected, you'll have access to:

### Service Tools
- `coordinate_services` - Coordinate operations across services
- `health_check_all` - Check health of all Northflank services
- `list_northflank_services` - List all services with status
- `get_service_info` - Get detailed service information

### Database Tools
- `mongo_query` - Execute MongoDB queries
- `redis_get` - Get values from Redis cache
- `redis_set` - Set values in Redis cache

### LibreChat Tools
- `librechat_send_message` - Send messages to LibreChat
- `librechat_get_config` - Get LibreChat configuration

### Workflow Tools
- `create_workflow` - Create multi-step workflows
- `execute_workflow` - Execute defined workflows

## Troubleshooting

### Tools not appearing in LibreChat?
1. Check MCP Hub health: `/health` endpoint
2. Verify librechat.yaml syntax (YAML is indent-sensitive!)
3. Restart LibreChat service
4. Check LibreChat logs for MCP connection errors

### "Service Unavailable" errors?
1. Verify API keys are set (OPENAI_API_KEY or ANTHROPIC_API_KEY)
2. Check service is running in Northflank
3. Review MCP Hub logs

### Database connection errors?
1. Verify MONGO_URI and REDIS_URI are correct
2. Check Northflank internal networking
3. Test from MCP Hub logs

## What's Next?

Now that MCP Hub is connected, you can:

1. **Ask LibreChat to coordinate services**:
   - "Check health of all services"
   - "List all Northflank services"

2. **Query databases**:
   - "Query MongoDB for recent conversations"
   - "Get value from Redis cache"

3. **Create workflows**:
   - "Create a workflow to backup database and notify me"

4. **Integrate with agents**:
   - The 5 specialized agents handle intelligent coordination

## Support

- **Logs**: Northflank → Services → mcp-hub → Logs
- **Docs**: See README.md and DEPLOY.md
- **Issues**: https://github.com/klogins-hash/northflank-mcp-hub/issues

---

**Total Time**: ~5 minutes
**Difficulty**: Easy
**Result**: All Northflank services talking via MCP!
