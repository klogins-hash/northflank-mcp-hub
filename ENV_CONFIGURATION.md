# Environment Variables Configuration Guide

## Strategy: Project Shared vs Service-Specific

**Project Shared** = Credentials and config used by MULTIPLE services
**Service-Specific** = URLs, ports, and config unique to ONE service

---

## 📦 PROJECT SHARED VARIABLES
*Set at: Project Settings → Environment*

These are shared across LibreChat, MCP Hub, MS Agent Team, etc.

### API Keys (Shared by all services)
```bash
OPENAI_API_KEY=sk-proj-y0STQyYfM3ERKbj0INLh...
ANTHROPIC_API_KEY=sk-ant-api03-vPED0ydNeFhU...
GROQ_API_KEY=gsk_tJQnZOUODPqop1xXCTmM...
PERPLEXITY_API_KEY=pplx-M6Ec5fjVUhIlWfhF...
CARTESIA_API_KEY=sk_car_9fM7KFZEfqeEfiET...
COHERE_API_KEY=Dffh3Z805ajKM2JpMoTw...
GOOGLE_KEY=user_provided
```

### Database Credentials (Shared by all services)
```bash
MONGO_URI=mongodb://058fd6e729a03a44:11233119620e33b09775db1f9a846fb1@mongo-0.mongodb-librechat--5d689c8h7r47.addon.code.run:27017/deedd2b3db59?replicaSet=rs0&authSource=deedd2b3db59&tls=true

REDIS_URI=redis://default:f95e10448ca2ab8a6a8dfb97972bbca8@master.redis-cache--5d689c8h7r47.addon.code.run:6379

# MinIO/S3 Storage
AWS_ENDPOINT_URL=https://minio.minio--5d689c8h7r47.addon.code.run:9000
AWS_ACCESS_KEY_ID=f60f12df1ab4ff6772
AWS_SECRET_ACCESS_KEY=c181d15155018105f038f0d58b8e183a68d80d
AWS_REGION=us-east-1
AWS_BUCKET_NAME=librechat-files
```

### Security Keys (Shared)
```bash
CREDS_KEY=f34be427ebb29de8d88c107a71546019685ed8b241d8f2ed00c3df97ad2566f0
CREDS_IV=e2341419ec3dd3d19b13a1a87fafcbfb
JWT_SECRET=16f8c0ef4a5d391b26034086c628469d3f9f497f08163ab9b40137092f2909ef
JWT_REFRESH_SECRET=eaa5191f2914e30b9387fd84e254e4ba6fc51b4654968a9b0803b456a54b8418
```

### Search (Shared if using MeiliSearch)
```bash
MEILI_NO_ANALYTICS=true
MEILI_HOST=http://0.0.0.0:7700
MEILI_MASTER_KEY=DrhYf7zENyR6AlUCKmnz0eYASOQdl6zxH7s7MKFSfFCt
```

**Total Project Shared Variables**: ~20

---

## 🌐 LIBRECHAT SERVICE-SPECIFIC VARIABLES
*Set at: LibreChat Service → Environment*

### Service Configuration
```bash
NODE_ENV=production
PORT=3080
HOST=0.0.0.0

# LibreChat specific domains
DOMAIN_CLIENT=https://web--librechat--5d689c8h7r47.code.run
DOMAIN_SERVER=https://web--librechat--5d689c8h7r47.code.run

# App Configuration
APP_TITLE=LibreChat
HELP_AND_FAQ_URL=https://librechat.ai
```

### Service URLs (LibreChat needs to know where other services are)
```bash
# Internal Northflank URLs (use these for production)
MS_AGENT_TEAM_URL=http://ms-agent-team:8080
MCP_HUB_URL=http://mcp-hub:8080

# OR Public URLs (use these for local dev)
# MS_AGENT_TEAM_URL=https://p01--ms-agent-team--5d689c8h7r47.code.run
# MCP_HUB_URL=https://mcp--mcp-hub--5d689c8h7r47.code.run
```

### Redis Configuration
```bash
USE_REDIS=true
```

### Search Configuration
```bash
SEARCH=true
```

### Debug/Logging
```bash
DEBUG_LOGGING=true
DEBUG_CONSOLE=false
DEBUG_PLUGINS=true
DEBUG_OPENAI=false
```

### Rate Limiting & Security
```bash
NO_INDEX=true
TRUST_PROXY=1

BAN_VIOLATIONS=true
BAN_DURATION=7200000
BAN_INTERVAL=20

LOGIN_VIOLATION_SCORE=1
REGISTRATION_VIOLATION_SCORE=1
CONCURRENT_VIOLATION_SCORE=1
MESSAGE_VIOLATION_SCORE=1
NON_BROWSER_VIOLATION_SCORE=20

LOGIN_MAX=7
LOGIN_WINDOW=5
REGISTER_MAX=5
REGISTER_WINDOW=60

LIMIT_CONCURRENT_MESSAGES=true
CONCURRENT_MESSAGE_MAX=2

LIMIT_MESSAGE_IP=true
MESSAGE_IP_MAX=40
MESSAGE_IP_WINDOW=1

LIMIT_MESSAGE_USER=false
MESSAGE_USER_MAX=40
MESSAGE_USER_WINDOW=1
```

### Authentication
```bash
ALLOW_EMAIL_LOGIN=true
ALLOW_REGISTRATION=true
ALLOW_SOCIAL_LOGIN=false
ALLOW_SOCIAL_REGISTRATION=false
ALLOW_PASSWORD_RESET=false
ALLOW_UNVERIFIED_EMAIL_LOGIN=true

SESSION_EXPIRY=900000
REFRESH_TOKEN_EXPIRY=604800000
```

### Shared Links
```bash
ALLOW_SHARED_LINKS=true
ALLOW_SHARED_LINKS_PUBLIC=true
```

### Moderation
```bash
OPENAI_MODERATION=false
```

**Total LibreChat Variables**: ~50

---

## 🤖 MCP HUB SERVICE-SPECIFIC VARIABLES
*Set at: MCP Hub Service → Environment*

```bash
# Service Configuration
PORT=8080
NODE_ENV=production

# MCP Server Config
MCP_SERVER_NAME=northflank-mcp-hub
MCP_SERVER_VERSION=1.0.0
LOG_LEVEL=INFO

# Service URLs
LIBRECHAT_URL=http://web--librechat:3080
MCP_HUB_URL=http://mcp-hub:8080

# OR for external access:
# LIBRECHAT_URL=https://web--librechat--5d689c8h7r47.code.run
# MCP_HUB_URL=https://mcp--mcp-hub--5d689c8h7r47.code.run

# CORS
ALLOWED_ORIGINS=http://localhost:3080,https://web--librechat--5d689c8h7r47.code.run,http://web--librechat:3080
```

**Total MCP Hub Variables**: ~8

**Note**: MCP Hub gets database credentials from Project Shared automatically.

---

## 👥 MS AGENT TEAM SERVICE-SPECIFIC VARIABLES
*Set at: MS Agent Team Service → Environment*

```bash
# Service Configuration
PORT=8080
NODE_ENV=production

# Logging
LOG_LEVEL=INFO

# Service URLs (if needed)
MS_AGENT_TEAM_URL=http://ms-agent-team:8080

# OR for external access:
# MS_AGENT_TEAM_URL=https://p01--ms-agent-team--5d689c8h7r47.code.run
```

**Total MS Agent Team Variables**: ~4

**Note**: MS Agent Team gets API keys from Project Shared automatically.

---

## 🔄 Migration Steps

### Step 1: Clean Up Project Shared
Remove service-specific variables from Project Shared:
- Remove `PORT` (each service has its own)
- Remove `HOST`
- Remove `DOMAIN_CLIENT`
- Remove `DOMAIN_SERVER`
- Remove service-specific `URL` variables
- Remove rate limiting configs
- Remove LibreChat-specific settings

Keep only:
- API keys
- Database credentials
- Security keys
- Shared storage config

### Step 2: Add Service-Specific Variables

For each service in Northflank:

**LibreChat**:
1. Go to LibreChat service → Environment
2. Add all LibreChat-specific variables listed above
3. Restart service

**MCP Hub**:
1. Go to MCP Hub service → Environment
2. Add all MCP Hub-specific variables listed above
3. Restart service

**MS Agent Team**:
1. Go to MS Agent Team service → Environment
2. Add all MS Agent Team-specific variables listed above
3. Restart service

### Step 3: Test Each Service
```bash
# Test LibreChat
curl https://web--librechat--5d689c8h7r47.code.run/health

# Test MCP Hub
curl https://mcp--mcp-hub--5d689c8h7r47.code.run/health

# Test MS Agent Team
curl https://p01--ms-agent-team--5d689c8h7r47.code.run/health
```

---

## ✅ Benefits of This Approach

1. **Clear Separation**: Easy to see what's shared vs service-specific
2. **Better Security**: Services only access what they need
3. **Easier Debugging**: Know exactly where to look for config issues
4. **Scalability**: Easy to add new services
5. **No Conflicts**: Services don't override each other's settings

---

## 🚨 Common Issues & Fixes

### Issue: Service can't find shared variables
**Fix**: Ensure Project Shared variables are properly set and service is restarted

### Issue: Services can't talk to each other
**Fix**: Use internal URLs (`http://service-name:port`) in production, not public URLs

### Issue: CORS errors in LibreChat
**Fix**: Ensure `ALLOWED_ORIGINS` in MCP Hub includes LibreChat's URL

---

## 📝 Quick Reference

| Variable Type | Location | Example |
|--------------|----------|---------|
| API Keys | Project Shared | `OPENAI_API_KEY` |
| Database | Project Shared | `MONGO_URI` |
| Port | Service-Specific | `PORT=8080` |
| Service URLs | Service-Specific | `LIBRECHAT_URL` |
| Domain | Service-Specific | `DOMAIN_CLIENT` |

---

**Updated**: $(date)
**Project**: gerry-adams-revolt
**Services**: LibreChat, MCP Hub, MS Agent Team
