"""Generic tools for calling any Northflank service"""
import httpx
from typing import Dict, Any
from .service_discovery import get_discovery

class GenericServiceTools:
    """Tools for calling any discovered service."""

    @staticmethod
    async def handle(name: str, arguments: Dict[str, Any]) -> str:
        """Handle generic service tool calls."""

        if name == "call_service":
            return await GenericServiceTools.call_service(
                arguments.get("service_name"),
                arguments.get("endpoint", "/"),
                arguments.get("method", "GET"),
                arguments.get("data")
            )
        elif name.startswith("call_"):
            # Extract service name from tool name (e.g., call_ms_agent_team -> ms-agent-team)
            service_name = name[5:].replace("_", "-")
            return await GenericServiceTools.call_service(
                service_name,
                arguments.get("endpoint", "/"),
                arguments.get("method", "GET"),
                arguments.get("data")
            )

        return f"Unknown generic service tool: {name}"

    @staticmethod
    async def call_service(
        service_name: str,
        endpoint: str = "/",
        method: str = "GET",
        data: dict = None
    ) -> str:
        """Call any service by name."""
        try:
            # Discover service URL
            discovery = get_discovery()
            service_url = await discovery.get_service_url(service_name)

            if not service_url:
                return f"Service '{service_name}' not found. Available services: {[s['name'] for s in await discovery.discover_services()]}"

            # Make the call
            full_url = f"{service_url}{endpoint}"

            async with httpx.AsyncClient(timeout=30.0) as client:
                if method == "GET":
                    response = await client.get(full_url)
                elif method == "POST":
                    response = await client.post(full_url, json=data or {})
                elif method == "PUT":
                    response = await client.put(full_url, json=data or {})
                elif method == "DELETE":
                    response = await client.delete(full_url)
                else:
                    return f"Unsupported method: {method}"

                # Return response
                if response.status_code == 200:
                    try:
                        return f"Success: {response.json()}"
                    except:
                        return f"Success: {response.text[:500]}"
                else:
                    return f"Service returned {response.status_code}: {response.text[:200]}"

        except httpx.TimeoutException:
            return f"Service '{service_name}' timed out"
        except Exception as e:
            return f"Error calling service '{service_name}': {str(e)}"

    @staticmethod
    async def get_service_health(service_name: str) -> str:
        """Check health of a specific service."""
        return await GenericServiceTools.call_service(service_name, "/health", "GET")

    @staticmethod
    async def list_available_services() -> str:
        """List all available services that can be called."""
        discovery = get_discovery()
        services = await discovery.discover_services()

        service_list = []
        for svc in services:
            service_list.append(
                f"- {svc['name']}: {svc.get('description', 'No description')} ({svc.get('status', 'unknown')})"
            )

        return "\n".join(service_list)
