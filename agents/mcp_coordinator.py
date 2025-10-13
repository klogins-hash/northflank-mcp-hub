"""
MCP Coordinator Agent

Primary orchestrator for all MCP operations across Northflank services.
Specializes in service coordination, tool routing, and error handling.
"""

import os
from typing import Optional
from azure.ai.agent import AssistantAgent


class MCPCoordinatorAgent:
    """Agent specialized in MCP protocol coordination."""

    def __init__(self, chat_client=None):
        """Initialize the MCP coordinator agent."""
        self.name = "MCP Coordinator"
        self.role = "MCP Protocol Expert & Service Orchestrator"

        system_message = """You are the MCP Coordinator for the Northflank MCP Hub.

**Your Expertise:**
- Model Context Protocol (MCP) implementation and standards
- Service orchestration across Northflank infrastructure
- Tool routing and coordination
- Error handling and recovery strategies
- Performance optimization for MCP operations

**Your Responsibilities:**
1. Coordinate MCP tool calls across multiple services
2. Route requests to appropriate specialists
3. Handle errors gracefully with fallback strategies
4. Optimize tool execution for performance
5. Monitor and report service health

**Available Services:**
- LibreChat (web--librechat)
- MongoDB (mongodb-librechat)
- Redis (redis-cache)
- MinIO (minio)
- MS Agent Team (ms-agent-team)

**MCP Tools You Coordinate:**
- Service tools: health checks, status, coordination
- Database tools: MongoDB queries, Redis operations
- LibreChat tools: messaging, configuration
- Workflow tools: multi-step orchestration

**Best Practices:**
- Always validate inputs before tool execution
- Use parallel execution when possible
- Implement retries for transient failures
- Cache frequently accessed data
- Log all operations for debugging

When coordinating operations:
1. Analyze the request
2. Determine required tools and sequence
3. Execute with error handling
4. Aggregate and format results
5. Return clear, actionable responses"""

        # Create agent with system message
        if chat_client:
            self.agent = AssistantAgent(
                name=self.name,
                model=chat_client,
                system_message=system_message
            )
        else:
            # Initialize with OpenAI or Anthropic
            api_key = os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("No API key found. Set OPENAI_API_KEY or ANTHROPIC_API_KEY")

            # Simple fallback for demo
            self.agent = None
            self.system_message = system_message

    async def coordinate_operation(self, operation: str, context: dict) -> str:
        """
        Coordinate a complex operation across services.

        Args:
            operation: Type of operation to coordinate
            context: Operation context and parameters

        Returns:
            str: Coordination result
        """
        if self.agent:
            prompt = f"""Coordinate this operation:

Operation: {operation}
Context: {context}

Provide:
1. Analysis of requirements
2. Tools needed (in order)
3. Execution plan
4. Expected outcomes"""

            result = await self.agent.run(prompt)
            return result
        else:
            # Fallback coordination logic
            return await self._fallback_coordinate(operation, context)

    async def _fallback_coordinate(self, operation: str, context: dict) -> str:
        """Fallback coordination when agent unavailable."""
        return f"""MCP Coordination Plan for: {operation}

Context: {context}

Recommended Steps:
1. Validate inputs and service availability
2. Execute primary operation with error handling
3. Verify results and update state
4. Return formatted response

Note: Full AI coordination requires API keys."""

    async def run(self, task: str) -> str:
        """Run the agent with a task."""
        if self.agent:
            return await self.agent.run(task)
        return f"{self.name}: {task}\n\n{self.system_message[:200]}..."

    async def run_stream(self, task: str):
        """Run agent with streaming output."""
        if self.agent:
            async for event in self.agent.run_stream(task):
                yield event
        else:
            yield f"{self.name}: Processing {task}"
