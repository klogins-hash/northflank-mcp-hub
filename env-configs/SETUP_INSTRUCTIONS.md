# Environment Variables Setup Instructions

## Quick Setup Guide

Follow these steps to properly configure environment variables in Northflank.

---

## Step 1: Configure Project Shared Variables (5 min)

**Location**: Northflank → Projects → gerry-adams-revolt → Settings → Environment

1. Go to https://app.northflank.com
2. Select project: **gerry-adams-revolt**
3. Click **Settings** (gear icon)
4. Click **Environment** tab
5. **Remove ALL existing variables** (we'll add back only what's needed)
6. Click **"Add Variable"** and add these:

### Copy from `project-shared.env`:
- All API keys (OpenAI, Anthropic, Groq, etc.)
- Database credentials (MONGO_URI, REDIS_URI)
- Storage config (AWS_*)
- Security keys (CREDS_KEY, JWT_SECRET, etc.)
- MeiliSearch config

**Total**: ~20 variables

7. Click **"Save"**

---

## Step 2: Configure LibreChat Service Variables (5 min)

**Location**: Northflank → gerry-adams-revolt → Services → web--librechat → Environment

1. Navigate to **LibreChat service**
2. Click **"Environment"** tab
3. **Remove ALL existing variables** (they'll inherit from Project Shared)
4. Click **"Add Variable"** and add from `librechat-service.env`:

### Service Config:
```
NODE_ENV=production
PORT=3080
HOST=0.0.0.0
```

### Domains:
```
DOMAIN_CLIENT=https://web--librechat--5d689c8h7r47.code.run
DOMAIN_SERVER=https://web--librechat--5d689c8h7r47.code.run
```

### Service URLs (Internal):
```
MS_AGENT_TEAM_URL=http://ms-agent-team:8080
MCP_HUB_URL=http://mcp-hub:8080
```

### App Config:
```
APP_TITLE=LibreChat
HELP_AND_FAQ_URL=https://librechat.ai
USE_REDIS=true
SEARCH=true
```

### Debug:
```
DEBUG_LOGGING=true
DEBUG_CONSOLE=false
DEBUG_PLUGINS=true
DEBUG_OPENAI=false
```

### Security (Rate Limiting):
```
NO_INDEX=true
TRUST_PROXY=1
BAN_VIOLATIONS=true
BAN_DURATION=7200000
BAN_INTERVAL=20
... (see librechat-service.env for all rate limiting variables)
```

### Authentication:
```
ALLOW_EMAIL_LOGIN=true
ALLOW_REGISTRATION=true
ALLOW_SOCIAL_LOGIN=false
ALLOW_SOCIAL_REGISTRATION=false
ALLOW_PASSWORD_RESET=false
ALLOW_UNVERIFIED_EMAIL_LOGIN=true
SESSION_EXPIRY=900000
REFRESH_TOKEN_EXPIRY=604800000
```

### Other:
```
ALLOW_SHARED_LINKS=true
ALLOW_SHARED_LINKS_PUBLIC=true
OPENAI_MODERATION=false
TTS_API_KEY=sk_car_9fM7KFZEfqeEfiETkHXwaH
```

**Total**: ~50 variables

5. Click **"Save"**
6. Service will automatically restart

---

## Step 3: Configure MCP Hub Service Variables (2 min)

**Location**: Northflank → gerry-adams-revolt → Services → mcp-hub → Environment

1. Navigate to **mcp-hub service**
2. Click **"Environment"** tab
3. Add from `mcp-hub-service.env`:

```
PORT=8080
NODE_ENV=production
MCP_SERVER_NAME=northflank-mcp-hub
MCP_SERVER_VERSION=1.0.0
LOG_LEVEL=INFO
LIBRECHAT_URL=http://web--librechat:3080
MCP_HUB_URL=http://mcp-hub:8080
ALLOWED_ORIGINS=http://localhost:3080,https://web--librechat--5d689c8h7r47.code.run,http://web--librechat:3080
```

**Total**: 8 variables

4. Click **"Save"**
5. Service will automatically restart

---

## Step 4: Configure MS Agent Team Service Variables (2 min)

**Location**: Northflank → gerry-adams-revolt → Services → ms-agent-team → Environment

1. Navigate to **ms-agent-team service**
2. Click **"Environment"** tab
3. Add from `ms-agent-team-service.env`:

```
PORT=8080
NODE_ENV=production
LOG_LEVEL=INFO
MS_AGENT_TEAM_URL=http://ms-agent-team:8080
```

**Total**: 4 variables

4. Click **"Save"**
5. Service will automatically restart

---

## Step 5: Verify All Services (3 min)

Wait 2-3 minutes for all services to restart, then test:

### Test LibreChat:
```bash
curl https://web--librechat--5d689c8h7r47.code.run/health
# Should return service health
```

### Test MCP Hub:
```bash
curl https://mcp--mcp-hub--5d689c8h7r47.code.run/health
# Should return: {"status":"healthy","agents_ready":true,...}
```

### Test MS Agent Team:
```bash
curl https://p01--ms-agent-team--5d689c8h7r47.code.run/health
# Should return service health
```

### Test MCP Integration:
```bash
curl -X POST https://mcp--mcp-hub--5d689c8h7r47.code.run/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/list","id":1}'
# Should return list of tools
```

---

## ✅ Benefits

After this reconfiguration:

1. **No Variable Conflicts**: Each service has its own config
2. **Shared Credentials**: API keys and database creds in one place
3. **Internal Networking**: Services use `http://service-name:port` for communication
4. **Easy Debugging**: Know exactly where each variable is set
5. **Scalable**: Easy to add new services

---

## 🚨 Troubleshooting

### Service won't start after reconfiguration?

**Check**:
1. All required Project Shared variables are set (especially API keys)
2. Service-specific PORT matches service configuration
3. Internal URLs use `http://service-name:port` format
4. No typos in variable names (case-sensitive!)

### Services can't communicate?

**Fix**: Ensure using internal URLs like:
- `http://web--librechat:3080` (not `https://web--librechat--5d689c8h7r47.code.run`)
- `http://mcp-hub:8080`
- `http://ms-agent-team:8080`

### MCP Hub can't connect to LibreChat?

**Fix**: Check CORS in MCP Hub includes LibreChat URLs (both internal and external)

---

## 📊 Summary

| Service | Project Shared | Service-Specific | Total |
|---------|---------------|------------------|-------|
| **All Services** | 20 variables | - | 20 |
| **LibreChat** | - | ~50 variables | ~50 |
| **MCP Hub** | - | 8 variables | 8 |
| **MS Agent Team** | - | 4 variables | 4 |

**Grand Total**: ~82 variables properly organized

---

## 🎯 Next Steps

After completing this setup:

1. ✅ All services will restart automatically
2. ✅ LibreChat will connect to MCP Hub
3. ✅ MCP Hub tools will be available in LibreChat
4. ✅ Services will communicate via internal Northflank network

**Try it**: Open LibreChat and say "Check the health of all services"!

---

**Updated**: $(date)
**Project**: gerry-adams-revolt
**Total Setup Time**: ~15 minutes
