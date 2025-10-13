"""Northflank resource providers for MCP"""
import json

class NorthflankResources:
    """Provides access to Northflank resources."""

    @staticmethod
    async def read(uri: str) -> str:
        """Read a resource by URI."""

        if uri == "northflank://project/info":
            return json.dumps({
                "name": "gerry-adams-revolt",
                "region": "europe-west-netherlands",
                "services": 6,
                "addons": 3
            })

        elif uri == "northflank://services/list":
            return json.dumps({
                "services": [
                    {"name": "LibreChat", "status": "running"},
                    {"name": "MCP-Hub", "status": "running"},
                    {"name": "MS-Agent-Team", "status": "running"}
                ]
            })

        elif uri == "northflank://databases/config":
            return json.dumps({
                "mongodb": {"addon": "mongodb-librechat", "version": "8.0.10"},
                "redis": {"addon": "redis-cache", "version": "7.2.4"},
                "minio": {"addon": "minio", "version": "2025.9.7"}
            })

        elif uri == "northflank://librechat/config":
            return json.dumps({
                "url": "https://web--librechat--5d689c8h7r47.code.run",
                "mcp_enabled": True,
                "models": ["gpt-4", "claude-3-opus"]
            })

        return json.dumps({"error": f"Unknown resource: {uri}"})
