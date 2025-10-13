# Deployment Guide - Northflank MCP Hub

## Quick Deploy to Northflank

### Step 1: Push to GitHub

```bash
cd ~/northflank-mcp-hub
git init
git add .
git commit -m "Initial commit: Northflank MCP Hub"
gh repo create northflank-mcp-hub --public --source=. --push
```

### Step 2: Create Service in Northflank

1. Go to https://northflank.com
2. Select project: **gerry-adams-revolt**
3. Click "Add Service" → "Combined service"
4. Configure:
   - **Name**: mcp-hub
   - **Source**: GitHub repository (northflank-mcp-hub)
   - **Branch**: main
   - **Build Type**: Dockerfile
   - **Port**: 8080

### Step 3: Set Environment Variables

In Northflank service settings, add:

```bash
# Required: API Keys
OPENAI_API_KEY=sk-...
# OR
ANTHROPIC_API_KEY=sk-ant-...

# Database connections (get from Northflank addons)
MONGO_URI=mongodb://...
REDIS_URI=redis://...

# LibreChat URL
LIBRECHAT_URL=https://web--librechat--5d689c8h7r47.code.run

# MCP Config
MCP_SERVER_NAME=northflank-mcp-hub
PORT=8080

# CORS
ALLOWED_ORIGINS=http://localhost:3080,https://web--librechat--5d689c8h7r47.code.run
```

### Step 4: Deploy

Click "Deploy" in Northflank. Service will be available at:
```
https://mcp-hub--gerry-adams-revolt--5d689c8h7r47.code.run
```

### Step 5: Connect to LibreChat

Add to LibreChat's `librechat.yaml`:

```yaml
mcpServers:
  northflank-hub:
    url: "https://mcp-hub--gerry-adams-revolt--5d689c8h7r47.code.run/mcp"
    name: "Northflank MCP Hub"
    description: "Universal service coordinator"
    enabled: true
    transport: "http"
```

Restart LibreChat service in Northflank.

### Step 6: Test

```bash
# Test MCP endpoint
curl -X POST https://mcp-hub--gerry-adams-revolt--5d689c8h7r47.code.run/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/list","id":1}'

# Test health
curl https://mcp-hub--gerry-adams-revolt--5d689c8h7r47.code.run/health

# Test agent
curl -X POST https://mcp-hub--gerry-adams-revolt--5d689c8h7r47.code.run/agents/consult \
  -H "Content-Type: application/json" \
  -d '{"question":"Check service health","specialist":"mcp_coordinator"}'
```

## Verification

In LibreChat:
1. Open chat
2. Click on tools/plugins icon
3. You should see "Northflank MCP Hub" available
4. Tools from MCP Hub should be listed
5. Try: "Check health of all services"

## Troubleshooting

### MCP Connection Issues
- Verify URL is correct in librechat.yaml
- Check CORS settings include LibreChat URL
- Review MCP Hub logs in Northflank

### Tools Not Appearing
- Ensure MCP Hub is healthy: `/health` endpoint
- Check LibreChat logs for MCP errors
- Verify librechat.yaml syntax

### Database Connection Errors
- Verify MONGO_URI and REDIS_URI are correct
- Check Northflank internal networking
- Test database connectivity from MCP Hub

## Monitoring

View logs:
```bash
# Via Northflank UI
Services > mcp-hub > Logs

# Or CLI
northflank logs get --project gerry-adams-revolt --service mcp-hub
```

## Updates

To update MCP Hub:
```bash
git add .
git commit -m "Update: description"
git push
```

Northflank will auto-deploy on push to main branch.
