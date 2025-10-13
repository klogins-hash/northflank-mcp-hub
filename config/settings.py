"""Configuration settings for MCP Hub"""
import os
from dotenv import load_dotenv

load_dotenv()

# Server settings
SERVER_NAME = os.getenv("MCP_SERVER_NAME", "northflank-mcp-hub")
SERVER_VERSION = os.getenv("MCP_SERVER_VERSION", "1.0.0")
PORT = int(os.getenv("PORT", 8080))

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Northflank Services
MONGO_URI = os.getenv("MONGO_URI")
REDIS_URI = os.getenv("REDIS_URI")
POSTGRES_URI = os.getenv("POSTGRES_URI")
LIBRECHAT_URL = os.getenv("LIBRECHAT_URL", "https://web--librechat--5d689c8h7r47.code.run")

# CORS
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3080,https://web--librechat--5d689c8h7r47.code.run").split(",")

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
