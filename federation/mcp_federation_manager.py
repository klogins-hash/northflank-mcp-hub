"""
MCP Federation Manager

Manages connections to multiple external MCP servers and provides
unified tool/resource access across all registered servers.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime
import httpx
import json

logger = logging.getLogger(__name__)


@dataclass
class MCPServerConfig:
    """Configuration for an external MCP server."""
    name: str
    url: str
    description: str = ""
    auth_type: Optional[str] = None  # "bearer", "basic", "api_key"
    auth_token: Optional[str] = None
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Runtime state
    last_health_check: Optional[datetime] = None
    is_healthy: bool = False
    tools: List[Dict] = field(default_factory=list)
    resources: List[Dict] = field(default_factory=list)
    error_count: int = 0


class MCPFederationManager:
    """
    Manages federation of multiple MCP servers.

    Features:
    - Dynamic server registration
    - Automatic tool/resource discovery
    - Health monitoring
    - Intelligent routing
    - Namespaced tool access
    """

    def __init__(self, config_file: Optional[str] = None):
        """Initialize the federation manager."""
        self.servers: Dict[str, MCPServerConfig] = {}
        self._http_client: Optional[httpx.AsyncClient] = None
        self._health_check_task: Optional[asyncio.Task] = None
        self._health_check_interval = 30  # seconds

        logger.info("MCP Federation Manager initialized")

    async def start(self):
        """Start the federation manager."""
        self._http_client = httpx.AsyncClient(timeout=30.0)

        # Start background health monitoring
        self._health_check_task = asyncio.create_task(self._health_monitor())

        logger.info("Federation manager started")

    async def stop(self):
        """Stop the federation manager."""
        if self._health_check_task:
            self._health_check_task.cancel()

        if self._http_client:
            await self._http_client.aclose()

        logger.info("Federation manager stopped")

    async def register_server(
        self,
        name: str,
        url: str,
        description: str = "",
        auth_type: Optional[str] = None,
        auth_token: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> bool:
        """
        Register an external MCP server.

        Args:
            name: Unique identifier for the server
            url: MCP endpoint URL
            description: Human-readable description
            auth_type: Authentication type (bearer, basic, api_key)
            auth_token: Authentication token
            metadata: Additional metadata

        Returns:
            True if registration successful
        """
        try:
            config = MCPServerConfig(
                name=name,
                url=url,
                description=description,
                auth_type=auth_type,
                auth_token=auth_token,
                metadata=metadata or {}
            )

            # Test connection and discover capabilities
            await self._discover_server_capabilities(config)

            self.servers[name] = config
            logger.info(f"Registered MCP server: {name} ({url})")
            logger.info(f"  - {len(config.tools)} tools discovered")
            logger.info(f"  - {len(config.resources)} resources discovered")

            return True

        except Exception as e:
            logger.error(f"Failed to register server {name}: {e}")
            return False

    async def unregister_server(self, name: str) -> bool:
        """Unregister an MCP server."""
        if name in self.servers:
            del self.servers[name]
            logger.info(f"Unregistered MCP server: {name}")
            return True
        return False

    async def _discover_server_capabilities(self, config: MCPServerConfig):
        """Discover tools and resources from an MCP server."""
        # List tools
        tools_response = await self._call_mcp_method(
            config,
            "tools/list",
            {}
        )
        if tools_response and "tools" in tools_response:
            config.tools = tools_response["tools"]

        # List resources
        try:
            resources_response = await self._call_mcp_method(
                config,
                "resources/list",
                {}
            )
            if resources_response and "resources" in resources_response:
                config.resources = resources_response["resources"]
        except:
            # Resources might not be supported
            pass

        config.is_healthy = True
        config.last_health_check = datetime.now()

    async def _call_mcp_method(
        self,
        config: MCPServerConfig,
        method: str,
        params: Dict[str, Any]
    ) -> Optional[Dict]:
        """Call an MCP method on a remote server."""
        if not self._http_client:
            raise RuntimeError("HTTP client not initialized")

        headers = {"Content-Type": "application/json"}

        # Add authentication if configured
        if config.auth_type == "bearer" and config.auth_token:
            headers["Authorization"] = f"Bearer {config.auth_token}"
        elif config.auth_type == "api_key" and config.auth_token:
            headers["X-API-Key"] = config.auth_token

        request_data = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": 1
        }

        try:
            response = await self._http_client.post(
                config.url,
                json=request_data,
                headers=headers
            )
            response.raise_for_status()

            data = response.json()

            if "error" in data:
                raise Exception(f"MCP error: {data['error']}")

            return data.get("result")

        except Exception as e:
            logger.error(f"Error calling {method} on {config.name}: {e}")
            config.error_count += 1
            raise

    async def call_tool(
        self,
        server_name: str,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Any:
        """
        Call a tool on a specific MCP server.

        Args:
            server_name: Name of the MCP server
            tool_name: Name of the tool to call
            arguments: Tool arguments

        Returns:
            Tool execution result
        """
        if server_name not in self.servers:
            raise ValueError(f"Unknown MCP server: {server_name}")

        config = self.servers[server_name]

        if not config.is_healthy:
            raise RuntimeError(f"MCP server {server_name} is not healthy")

        result = await self._call_mcp_method(
            config,
            "tools/call",
            {"name": tool_name, "arguments": arguments}
        )

        return result

    async def read_resource(
        self,
        server_name: str,
        uri: str
    ) -> Any:
        """Read a resource from a specific MCP server."""
        if server_name not in self.servers:
            raise ValueError(f"Unknown MCP server: {server_name}")

        config = self.servers[server_name]

        result = await self._call_mcp_method(
            config,
            "resources/read",
            {"uri": uri}
        )

        return result

    def get_all_tools(self) -> List[Dict]:
        """
        Get all tools from all registered servers with namespacing.

        Returns list of tools in format:
        {
            "name": "server_name.tool_name",
            "description": "...",
            "server": "server_name",
            "original_name": "tool_name",
            "inputSchema": {...}
        }
        """
        all_tools = []

        for server_name, config in self.servers.items():
            if not config.enabled or not config.is_healthy:
                continue

            for tool in config.tools:
                namespaced_tool = {
                    "name": f"{server_name}.{tool['name']}",
                    "description": f"[{server_name}] {tool.get('description', '')}",
                    "server": server_name,
                    "original_name": tool["name"],
                    "inputSchema": tool.get("inputSchema", {})
                }
                all_tools.append(namespaced_tool)

        return all_tools

    def get_all_resources(self) -> List[Dict]:
        """Get all resources from all registered servers with namespacing."""
        all_resources = []

        for server_name, config in self.servers.items():
            if not config.enabled or not config.is_healthy:
                continue

            for resource in config.resources:
                namespaced_resource = {
                    "uri": f"{server_name}://{resource.get('uri', '')}",
                    "name": f"[{server_name}] {resource.get('name', '')}",
                    "server": server_name,
                    "original_uri": resource.get("uri", ""),
                    "mimeType": resource.get("mimeType", "application/json")
                }
                all_resources.append(namespaced_resource)

        return all_resources

    def get_server_info(self, name: str) -> Optional[Dict]:
        """Get information about a specific server."""
        if name not in self.servers:
            return None

        config = self.servers[name]
        return {
            "name": config.name,
            "url": config.url,
            "description": config.description,
            "enabled": config.enabled,
            "is_healthy": config.is_healthy,
            "last_health_check": config.last_health_check.isoformat() if config.last_health_check else None,
            "tools_count": len(config.tools),
            "resources_count": len(config.resources),
            "error_count": config.error_count,
            "metadata": config.metadata
        }

    def list_servers(self) -> List[Dict]:
        """List all registered servers."""
        return [self.get_server_info(name) for name in self.servers.keys()]

    async def _health_monitor(self):
        """Background task to monitor server health."""
        while True:
            try:
                await asyncio.sleep(self._health_check_interval)

                for name, config in self.servers.items():
                    if not config.enabled:
                        continue

                    try:
                        # Try to list tools as health check
                        await self._discover_server_capabilities(config)
                        config.is_healthy = True
                        config.error_count = 0
                        logger.debug(f"Health check passed: {name}")

                    except Exception as e:
                        config.is_healthy = False
                        config.error_count += 1
                        logger.warning(f"Health check failed for {name}: {e}")

                        # Disable server after too many failures
                        if config.error_count > 5:
                            config.enabled = False
                            logger.error(f"Disabled server {name} after repeated failures")

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in health monitor: {e}")

    def get_stats(self) -> Dict:
        """Get federation statistics."""
        healthy_servers = sum(1 for s in self.servers.values() if s.is_healthy)
        total_tools = sum(len(s.tools) for s in self.servers.values() if s.is_healthy)
        total_resources = sum(len(s.resources) for s in self.servers.values() if s.is_healthy)

        return {
            "total_servers": len(self.servers),
            "healthy_servers": healthy_servers,
            "total_tools": total_tools,
            "total_resources": total_resources,
            "servers": self.list_servers()
        }
