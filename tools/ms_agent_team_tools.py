"""MS Agent Team interaction tools for MCP"""
import aiohttp
import os
from typing import Dict, Any
import json

class MSAgentTeamTools:
    """Tools for interacting with the MS Agent Team service."""

    BASE_URL = "https://p01--ms-agent-team--5d689c8h7r47.code.run"

    @staticmethod
    async def handle(name: str, arguments: Dict[str, Any]) -> str:
        """Handle MS Agent Team tool calls."""

        if name == "agent_team_chat":
            return await MSAgentTeamTools.chat(
                arguments.get("message"),
                arguments.get("context", {})
            )
        elif name == "agent_team_status":
            return await MSAgentTeamTools.get_status()
        elif name == "agent_team_list_agents":
            return await MSAgentTeamTools.list_agents()
        elif name == "agent_team_query":
            return await MSAgentTeamTools.query_agent(
                arguments.get("agent_name"),
                arguments.get("query")
            )

        return f"Unknown MS Agent Team tool: {name}"

    @staticmethod
    async def chat(message: str, context: dict = None) -> str:
        """
        Send a message to the agent team and get a response.
        """
        try:
            if not message:
                return "Error: Message is required"

            async with aiohttp.ClientSession() as session:
                # Try different possible endpoints
                endpoints = [
                    "/chat",
                    "/api/chat",
                    "/message",
                    "/api/message",
                    "/",
                ]

                payload = {
                    "message": message,
                    "context": context or {}
                }

                last_error = None

                for endpoint in endpoints:
                    url = f"{MSAgentTeamTools.BASE_URL}{endpoint}"

                    try:
                        # Try POST request
                        async with session.post(
                            url,
                            json=payload,
                            timeout=aiohttp.ClientTimeout(total=30)
                        ) as response:
                            if response.status == 200:
                                result = await response.json()
                                return f"Agent Team Response (via {endpoint}):\n\n{json.dumps(result, indent=2)}"
                            elif response.status == 404:
                                continue  # Try next endpoint
                            else:
                                text = await response.text()
                                last_error = f"HTTP {response.status}: {text[:200]}"
                    except Exception as e:
                        last_error = str(e)
                        continue

                # If all endpoints failed, try GET on root to see what's available
                try:
                    async with session.get(
                        MSAgentTeamTools.BASE_URL,
                        timeout=aiohttp.ClientTimeout(total=10)
                    ) as response:
                        info = await response.text()
                        return f"Could not find chat endpoint. Service responded with:\n\n{info[:500]}\n\nLast error: {last_error}\n\nTried endpoints: {', '.join(endpoints)}"
                except Exception as e:
                    return f"Error: Service unreachable. Last error: {last_error}\nConnection error: {str(e)}"

        except Exception as e:
            return f"Error chatting with agent team: {str(e)}"

    @staticmethod
    async def get_status() -> str:
        """Get the status of the agent team service."""
        try:
            async with aiohttp.ClientSession() as session:
                endpoints = ["/health", "/status", "/api/health", "/"]

                for endpoint in endpoints:
                    url = f"{MSAgentTeamTools.BASE_URL}{endpoint}"

                    try:
                        async with session.get(
                            url,
                            timeout=aiohttp.ClientTimeout(total=10)
                        ) as response:
                            if response.status == 200:
                                try:
                                    result = await response.json()
                                    return f"Agent Team Status (via {endpoint}):\n{json.dumps(result, indent=2)}"
                                except:
                                    text = await response.text()
                                    return f"Agent Team Status (via {endpoint}):\n{text[:500]}"
                    except:
                        continue

                return "Error: Could not reach agent team service status endpoint"

        except Exception as e:
            return f"Error getting status: {str(e)}"

    @staticmethod
    async def list_agents() -> str:
        """List all available agents in the team."""
        try:
            async with aiohttp.ClientSession() as session:
                endpoints = ["/agents", "/api/agents", "/agents/list", "/list"]

                for endpoint in endpoints:
                    url = f"{MSAgentTeamTools.BASE_URL}{endpoint}"

                    try:
                        async with session.get(
                            url,
                            timeout=aiohttp.ClientTimeout(total=10)
                        ) as response:
                            if response.status == 200:
                                result = await response.json()
                                return f"Available Agents:\n{json.dumps(result, indent=2)}"
                    except:
                        continue

                return "Error: Could not find agents list endpoint"

        except Exception as e:
            return f"Error listing agents: {str(e)}"

    @staticmethod
    async def query_agent(agent_name: str, query: str) -> str:
        """Query a specific agent by name."""
        try:
            if not agent_name or not query:
                return "Error: Both agent_name and query are required"

            async with aiohttp.ClientSession() as session:
                endpoints = [
                    f"/agents/{agent_name}",
                    f"/api/agents/{agent_name}",
                    f"/agent/{agent_name}",
                ]

                payload = {"query": query}

                for endpoint in endpoints:
                    url = f"{MSAgentTeamTools.BASE_URL}{endpoint}"

                    try:
                        async with session.post(
                            url,
                            json=payload,
                            timeout=aiohttp.ClientTimeout(total=30)
                        ) as response:
                            if response.status == 200:
                                result = await response.json()
                                return f"Agent '{agent_name}' Response:\n{json.dumps(result, indent=2)}"
                    except:
                        continue

                return f"Error: Could not query agent '{agent_name}'"

        except Exception as e:
            return f"Error querying agent: {str(e)}"
