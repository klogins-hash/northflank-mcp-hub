"""Northflank service execution tools for MCP"""
import subprocess
import os
from typing import Dict, Any
import json

class NorthflankExecTools:
    """Tools for executing commands on Northflank services."""

    DEFAULT_PROJECT_ID = "gerry-adams-revolt"
    DEFAULT_SERVICE_ID = "ms-agent-team"

    @staticmethod
    async def handle(name: str, arguments: Dict[str, Any]) -> str:
        """Handle Northflank exec tool calls."""

        if name == "northflank_exec":
            return await NorthflankExecTools.exec_command(
                arguments.get("command"),
                arguments.get("project_id", NorthflankExecTools.DEFAULT_PROJECT_ID),
                arguments.get("service_id", NorthflankExecTools.DEFAULT_SERVICE_ID)
            )
        elif name == "northflank_chat":
            return await NorthflankExecTools.chat_with_service(
                arguments.get("message"),
                arguments.get("project_id", NorthflankExecTools.DEFAULT_PROJECT_ID),
                arguments.get("service_id", NorthflankExecTools.DEFAULT_SERVICE_ID)
            )
        elif name == "northflank_get_logs":
            return await NorthflankExecTools.get_service_logs(
                arguments.get("project_id", NorthflankExecTools.DEFAULT_PROJECT_ID),
                arguments.get("service_id", NorthflankExecTools.DEFAULT_SERVICE_ID),
                arguments.get("lines", 100)
            )
        elif name == "northflank_service_info":
            return await NorthflankExecTools.get_service_info(
                arguments.get("project_id", NorthflankExecTools.DEFAULT_PROJECT_ID),
                arguments.get("service_id", NorthflankExecTools.DEFAULT_SERVICE_ID)
            )

        return f"Unknown Northflank exec tool: {name}"

    @staticmethod
    async def exec_command(
        command: str,
        project_id: str = DEFAULT_PROJECT_ID,
        service_id: str = DEFAULT_SERVICE_ID
    ) -> str:
        """Execute a command on a Northflank service."""
        try:
            if not command:
                return "Error: Command is required"

            # Build the northflank exec command
            nf_command = [
                "northflank", "exec", "service",
                "--projectId", project_id,
                "--serviceId", service_id,
                "--"
            ] + command.split()

            result = subprocess.run(
                nf_command,
                capture_output=True,
                text=True,
                timeout=60
            )

            output = result.stdout if result.returncode == 0 else result.stderr
            return f"Command: {command}\nExit Code: {result.returncode}\n\nOutput:\n{output}"

        except subprocess.TimeoutExpired:
            return f"Command timed out after 60 seconds"
        except FileNotFoundError:
            return "Error: Northflank CLI not found. Please install it first."
        except Exception as e:
            return f"Error executing command: {str(e)}"

    @staticmethod
    async def chat_with_service(
        message: str,
        project_id: str = DEFAULT_PROJECT_ID,
        service_id: str = DEFAULT_SERVICE_ID
    ) -> str:
        """Send a message/command to the agent team service and get response."""
        try:
            if not message:
                return "Error: Message is required"

            # For agent team, we'll try to execute a Python command that sends the message
            # Assuming the service has a chat interface or API

            # First, let's try a simple echo to test connectivity
            command = f'echo "{message}"'

            nf_command = [
                "northflank", "exec", "service",
                "--projectId", project_id,
                "--serviceId", service_id,
                "--",
                "sh", "-c", command
            ]

            result = subprocess.run(
                nf_command,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                return f"Service response:\n{result.stdout}"
            else:
                return f"Error communicating with service:\n{result.stderr}"

        except subprocess.TimeoutExpired:
            return "Request timed out after 60 seconds"
        except Exception as e:
            return f"Error chatting with service: {str(e)}"

    @staticmethod
    async def get_service_logs(
        project_id: str = DEFAULT_PROJECT_ID,
        service_id: str = DEFAULT_SERVICE_ID,
        lines: int = 100
    ) -> str:
        """Get recent logs from a Northflank service."""
        try:
            command = [
                "northflank", "logs", "service",
                "--projectId", project_id,
                "--serviceId", service_id,
                "--lines", str(lines)
            ]

            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                return f"Last {lines} log lines from {service_id}:\n\n{result.stdout}"
            else:
                return f"Error getting logs:\n{result.stderr}"

        except subprocess.TimeoutExpired:
            return "Log request timed out"
        except Exception as e:
            return f"Error getting logs: {str(e)}"

    @staticmethod
    async def get_service_info(
        project_id: str = DEFAULT_PROJECT_ID,
        service_id: str = DEFAULT_SERVICE_ID
    ) -> str:
        """Get information about a Northflank service."""
        try:
            command = [
                "northflank", "get", "service",
                "--projectId", project_id,
                "--serviceId", service_id,
                "--output", "json"
            ]

            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                data = json.loads(result.stdout)
                info = {
                    "id": data.get("data", {}).get("id"),
                    "name": data.get("data", {}).get("name"),
                    "status": data.get("data", {}).get("status"),
                    "buildpack": data.get("data", {}).get("buildpack"),
                    "buildConfiguration": data.get("data", {}).get("buildConfiguration"),
                }
                return f"Service info:\n{json.dumps(info, indent=2)}"
            else:
                return f"Error getting service info:\n{result.stderr}"

        except Exception as e:
            return f"Error getting service info: {str(e)}"
