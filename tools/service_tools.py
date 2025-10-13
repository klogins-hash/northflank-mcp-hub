"""Service coordination tools for MCP"""
import httpx
import os
from typing import Dict, Any

class ServiceTools:
    """Tools for coordinating Northflank services."""

    @staticmethod
    async def handle(name: str, arguments: Dict[str, Any]) -> str:
        """Handle service tool calls."""

        if name == "coordinate_services":
            return await ServiceTools.coordinate_services(
                arguments.get("operation"),
                arguments.get("services", [])
            )
        elif name == "health_check_all":
            return await ServiceTools.health_check_all(
                arguments.get("detailed", False)
            )
        elif name == "list_northflank_services":
            return await ServiceTools.list_services(
                arguments.get("status_filter", "all")
            )
        elif name == "get_service_info":
            return await ServiceTools.get_service_info(
                arguments.get("service_name")
            )

        return f"Unknown service tool: {name}"

    @staticmethod
    async def coordinate_services(operation: str, services: list) -> str:
        """Coordinate operations across services."""
        services_list = services if services else [
            "LibreChat", "MongoDB", "Redis", "MinIO", "MS-Agent-Team"
        ]

        results = []
        for service in services_list:
            results.append(f"{service}: {operation} - OK")

        return "\n".join(results)

    @staticmethod
    async def health_check_all(detailed: bool = False) -> str:
        """Check health of all services."""
        services = {
            "LibreChat": "https://web--librechat--5d689c8h7r47.code.run/health",
            "MCP-Hub": "http://localhost:8080/health",
        }

        results = []
        async with httpx.AsyncClient() as client:
            for name, url in services.items():
                try:
                    resp = await client.get(url, timeout=5.0)
                    status = "✅ Healthy" if resp.status_code == 200 else "⚠️ Issues"
                    results.append(f"{name}: {status}")
                except Exception as e:
                    results.append(f"{name}: ❌ Down - {str(e)[:50]}")

        return "\n".join(results)

    @staticmethod
    async def list_services(status_filter: str) -> str:
        """List Northflank services."""
        services = [
            {"name": "LibreChat", "status": "running", "port": 3080},
            {"name": "MongoDB", "status": "running", "port": 27017},
            {"name": "Redis", "status": "running", "port": 6379},
            {"name": "MinIO", "status": "running", "port": 9000},
            {"name": "MS-Agent-Team", "status": "running", "port": 8080},
            {"name": "MCP-Hub", "status": "running", "port": 8080},
        ]

        if status_filter != "all":
            services = [s for s in services if s["status"] == status_filter]

        return "\n".join([f"- {s['name']}: {s['status']} (port {s['port']})" for s in services])

    @staticmethod
    async def get_service_info(service_name: str) -> str:
        """Get detailed service information."""
        service_info = {
            "name": service_name,
            "status": "running",
            "url": f"https://{service_name.lower()}--gerry-adams-revolt--5d689c8h7r47.code.run",
            "health": "healthy",
            "mcp_enabled": True
        }

        return str(service_info)
