"""
Auto-discovery for Northflank services and addons
"""
import os
import subprocess
import json
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class ServiceDiscovery:
    """Automatically discover and register Northflank services."""

    def __init__(self, project_id: str = "gerry-adams-revolt"):
        self.project_id = project_id
        self._services_cache = None
        self._addons_cache = None

    async def discover_all(self) -> Dict[str, Any]:
        """Discover all services and addons in the project."""
        try:
            services = await self.discover_services()
            addons = await self.discover_addons()

            return {
                "services": services,
                "addons": addons,
                "total_services": len(services),
                "total_addons": len(addons)
            }
        except Exception as e:
            logger.error(f"Discovery failed: {e}")
            return {"error": str(e)}

    async def discover_services(self) -> List[Dict[str, Any]]:
        """Discover all services in the project."""
        if self._services_cache:
            return self._services_cache

        try:
            # Use northflank CLI to list services
            result = subprocess.run(
                ["northflank", "list", "services", "--project", self.project_id, "--output", "json"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                data = json.loads(result.stdout)
                services = data.get("data", {}).get("services", [])

                # Extract useful service info
                service_list = []
                for svc in services:
                    service_info = {
                        "id": svc.get("id"),
                        "name": svc.get("name"),
                        "description": svc.get("description", ""),
                        "type": svc.get("serviceType", "unknown"),
                        "status": svc.get("status", {}).get("deployment", {}).get("status"),
                        "ports": svc.get("ports", []),
                        "dns": None
                    }

                    # Extract DNS from ports
                    if service_info["ports"]:
                        for port in service_info["ports"]:
                            if port.get("dns"):
                                service_info["dns"] = f"https://{port['dns']}"
                                break

                    service_list.append(service_info)

                self._services_cache = service_list
                return service_list
            else:
                logger.warning(f"Failed to list services: {result.stderr}")
                return []

        except Exception as e:
            logger.error(f"Service discovery error: {e}")
            return []

    async def discover_addons(self) -> List[Dict[str, Any]]:
        """Discover all addons (databases, caches, etc.) in the project."""
        if self._addons_cache:
            return self._addons_cache

        try:
            result = subprocess.run(
                ["northflank", "list", "addons", "--project", self.project_id, "--output", "json"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                data = json.loads(result.stdout)
                addons = data.get("data", {}).get("addons", [])

                addon_list = []
                for addon in addons:
                    addon_info = {
                        "id": addon.get("id"),
                        "name": addon.get("name"),
                        "type": addon.get("spec", {}).get("type"),
                        "status": addon.get("status"),
                        "description": addon.get("description", "")
                    }
                    addon_list.append(addon_info)

                self._addons_cache = addon_list
                return addon_list
            else:
                logger.warning(f"Failed to list addons: {result.stderr}")
                return []

        except Exception as e:
            logger.error(f"Addon discovery error: {e}")
            return []

    async def get_service_url(self, service_name: str) -> Optional[str]:
        """Get the URL for a specific service."""
        services = await self.discover_services()

        for svc in services:
            if svc["name"] == service_name or svc["id"] == service_name:
                return svc.get("dns")

        return None

    async def get_addon_type(self, addon_name: str) -> Optional[str]:
        """Get the type of a specific addon."""
        addons = await self.discover_addons()

        for addon in addons:
            if addon["name"] == addon_name or addon["id"] == addon_name:
                return addon.get("type")

        return None

    def clear_cache(self):
        """Clear the discovery cache to force refresh."""
        self._services_cache = None
        self._addons_cache = None

    async def get_service_health_urls(self) -> Dict[str, str]:
        """Get health check URLs for all services."""
        services = await self.discover_services()
        health_urls = {}

        for svc in services:
            if svc.get("dns"):
                # Common health check patterns
                health_urls[svc["name"]] = f"{svc['dns']}/health"

        return health_urls

    async def generate_service_tools(self) -> List[Dict[str, Any]]:
        """Generate MCP tools dynamically based on discovered services."""
        services = await self.discover_services()
        tools = []

        for svc in services:
            # Generate a tool for each service
            tool = {
                "name": f"call_{svc['name'].replace('-', '_')}",
                "description": f"Interact with {svc['name']} service - {svc.get('description', '')}",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "endpoint": {
                            "type": "string",
                            "description": "API endpoint to call"
                        },
                        "method": {
                            "type": "string",
                            "enum": ["GET", "POST", "PUT", "DELETE"],
                            "default": "GET"
                        },
                        "data": {
                            "type": "object",
                            "description": "Request body (for POST/PUT)"
                        }
                    },
                    "required": ["endpoint"]
                }
            }
            tools.append(tool)

        return tools


# Singleton instance
_discovery = None

def get_discovery() -> ServiceDiscovery:
    """Get the singleton service discovery instance."""
    global _discovery
    if _discovery is None:
        _discovery = ServiceDiscovery()
    return _discovery
