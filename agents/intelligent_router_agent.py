"""
Intelligent Router Agent

Uses Groq's ultra-fast Llama 3.3 70B model to intelligently route
requests to the appropriate MCP server based on natural language input.
"""

import os
import logging
import json
from typing import Dict, List, Optional, Any
from groq import Groq

logger = logging.getLogger(__name__)


class IntelligentRouterAgent:
    """
    Intelligent agent that routes requests to appropriate MCP servers.

    Uses Groq's Llama 3.3 70B model for:
    - Understanding natural language requests
    - Determining which MCP server(s) to use
    - Decomposing complex requests into multiple tool calls
    - Coordinating multi-server operations
    """

    def __init__(self, federation_manager=None):
        """Initialize the router agent."""
        self.federation_manager = federation_manager

        # Initialize Groq client
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            logger.warning("No GROQ_API_KEY found - router will use fallback logic")
            self.groq_client = None
        else:
            self.groq_client = Groq(api_key=api_key)
            logger.info("Groq client initialized with Llama 3.3 70B")

        self.model = "llama-3.3-70b-versatile"  # Ultra-fast model

    async def route_request(
        self,
        user_request: str,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Route a user request to appropriate MCP server(s).

        Args:
            user_request: Natural language request from user
            context: Additional context about the request

        Returns:
            Routing decision with server, tool, and arguments
        """
        if not self.groq_client:
            return await self._fallback_routing(user_request)

        # Get available servers and their capabilities
        servers_info = self._get_servers_context()

        # Build prompt for Groq
        system_prompt = self._build_system_prompt(servers_info)
        user_prompt = self._build_user_prompt(user_request, context)

        try:
            # Call Groq for intelligent routing
            response = self.groq_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,  # Low temperature for consistent routing
                max_tokens=1000,
                response_format={"type": "json_object"}
            )

            # Parse routing decision
            decision = json.loads(response.choices[0].message.content)

            logger.info(f"Routing decision: {decision}")
            return decision

        except Exception as e:
            logger.error(f"Error in intelligent routing: {e}")
            return await self._fallback_routing(user_request)

    def _get_servers_context(self) -> List[Dict]:
        """Get context about available MCP servers and their tools."""
        if not self.federation_manager:
            return []

        servers = []
        for server_name, config in self.federation_manager.servers.items():
            if not config.is_healthy or not config.enabled:
                continue

            server_info = {
                "name": server_name,
                "description": config.description,
                "tools": [
                    {
                        "name": tool["name"],
                        "description": tool.get("description", "")
                    }
                    for tool in config.tools
                ],
                "resources": [
                    {
                        "uri": res.get("uri", ""),
                        "description": res.get("name", "")
                    }
                    for res in config.resources
                ]
            }
            servers.append(server_info)

        return servers

    def _build_system_prompt(self, servers_info: List[Dict]) -> str:
        """Build system prompt for Groq."""
        servers_description = "\n\n".join([
            f"**{s['name']}**: {s['description']}\n"
            f"Tools: {', '.join([t['name'] for t in s['tools']])}\n"
            f"Resources: {len(s['resources'])} available"
            for s in servers_info
        ])

        return f"""You are an intelligent MCP routing agent. Your job is to analyze user requests and determine which MCP server and tool to use.

Available MCP Servers:
{servers_description}

Your task:
1. Understand the user's request
2. Determine which MCP server is most appropriate
3. Select the specific tool to call
4. Extract or infer the required arguments

Respond with a JSON object in this format:
{{
  "server": "server_name",
  "tool": "tool_name",
  "arguments": {{"arg1": "value1", "arg2": "value2"}},
  "reasoning": "Brief explanation of routing decision",
  "confidence": 0.95,
  "multi_step": false,
  "steps": []
}}

If the request requires multiple steps across servers, set multi_step: true and provide steps array.

Be precise and always provide valid JSON."""

    def _build_user_prompt(
        self,
        user_request: str,
        context: Optional[Dict]
    ) -> str:
        """Build user prompt for Groq."""
        prompt = f"User Request: {user_request}"

        if context:
            prompt += f"\n\nContext:\n{json.dumps(context, indent=2)}"

        prompt += "\n\nPlease route this request to the appropriate MCP server and tool."

        return prompt

    async def _fallback_routing(self, user_request: str) -> Dict[str, Any]:
        """Fallback routing logic when Groq is not available."""
        logger.info("Using fallback routing logic")

        # Simple keyword-based routing
        request_lower = user_request.lower()

        # Database operations
        if any(word in request_lower for word in ["database", "mongo", "redis", "query", "cache"]):
            return {
                "server": "local",
                "tool": "mongo_query" if "mongo" in request_lower else "redis_get",
                "arguments": {},
                "reasoning": "Detected database-related keywords",
                "confidence": 0.6,
                "multi_step": False
            }

        # Service coordination
        if any(word in request_lower for word in ["service", "health", "status", "coordinate"]):
            return {
                "server": "local",
                "tool": "health_check_all",
                "arguments": {},
                "reasoning": "Detected service coordination keywords",
                "confidence": 0.6,
                "multi_step": False
            }

        # Default fallback
        return {
            "server": "local",
            "tool": "coordinate_services",
            "arguments": {"operation": "help"},
            "reasoning": "No specific routing match, using default",
            "confidence": 0.3,
            "multi_step": False
        }

    async def execute_routing(self, routing_decision: Dict[str, Any]) -> Any:
        """
        Execute the routing decision by calling the appropriate MCP server.

        Args:
            routing_decision: Output from route_request()

        Returns:
            Result from the MCP tool execution
        """
        server = routing_decision.get("server")
        tool = routing_decision.get("tool")
        arguments = routing_decision.get("arguments", {})
        multi_step = routing_decision.get("multi_step", False)

        if not self.federation_manager:
            raise RuntimeError("Federation manager not configured")

        if multi_step:
            # Execute multi-step routing
            return await self._execute_multi_step(routing_decision.get("steps", []))

        # Single step execution
        if server == "local":
            # Handle local tools
            from tools.service_tools import ServiceTools
            from tools.database_tools import DatabaseTools

            if tool in ["coordinate_services", "health_check_all"]:
                return await ServiceTools.handle(tool, arguments)
            elif tool in ["mongo_query", "redis_get", "redis_set"]:
                return await DatabaseTools.handle(tool, arguments)

        else:
            # Route to external MCP server
            result = await self.federation_manager.call_tool(
                server_name=server,
                tool_name=tool,
                arguments=arguments
            )
            return result

    async def _execute_multi_step(self, steps: List[Dict]) -> List[Any]:
        """Execute multiple routing steps in sequence."""
        results = []

        for step in steps:
            result = await self.execute_routing(step)
            results.append({
                "step": step,
                "result": result
            })

        return results

    async def run(self, request: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Main entry point: route and execute request.

        Args:
            request: Natural language request
            context: Optional context

        Returns:
            Execution result with routing metadata
        """
        # Get routing decision
        routing = await self.route_request(request, context)

        # Execute the routing
        try:
            result = await self.execute_routing(routing)

            return {
                "success": True,
                "routing": routing,
                "result": result
            }

        except Exception as e:
            logger.error(f"Error executing routing: {e}")
            return {
                "success": False,
                "routing": routing,
                "error": str(e)
            }
