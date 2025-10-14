"""Code execution tools for MCP"""
import subprocess
import tempfile
import os
from typing import Dict, Any
import asyncio

class CodeExecutionTools:
    """Tools for executing code in various languages."""

    @staticmethod
    async def handle(name: str, arguments: Dict[str, Any]) -> str:
        """Handle code execution tool calls."""

        if name == "execute_python":
            return await CodeExecutionTools.execute_python(
                arguments.get("code"),
                arguments.get("timeout", 30)
            )
        elif name == "execute_javascript":
            return await CodeExecutionTools.execute_javascript(
                arguments.get("code"),
                arguments.get("timeout", 30)
            )
        elif name == "execute_shell":
            return await CodeExecutionTools.execute_shell(
                arguments.get("command"),
                arguments.get("timeout", 30)
            )

        return f"Unknown code execution tool: {name}"

    @staticmethod
    async def execute_python(code: str, timeout: int = 30) -> str:
        """Execute Python code safely."""
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name

            try:
                # Execute with timeout
                result = subprocess.run(
                    ['python3', temp_file],
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )

                output = result.stdout if result.returncode == 0 else result.stderr
                return f"Exit code: {result.returncode}\n\nOutput:\n{output}"

            finally:
                # Cleanup
                if os.path.exists(temp_file):
                    os.remove(temp_file)

        except subprocess.TimeoutExpired:
            return f"Execution timed out after {timeout} seconds"
        except Exception as e:
            return f"Execution error: {str(e)}"

    @staticmethod
    async def execute_javascript(code: str, timeout: int = 30) -> str:
        """Execute JavaScript/Node.js code safely."""
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
                f.write(code)
                temp_file = f.name

            try:
                # Execute with timeout
                result = subprocess.run(
                    ['node', temp_file],
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )

                output = result.stdout if result.returncode == 0 else result.stderr
                return f"Exit code: {result.returncode}\n\nOutput:\n{output}"

            finally:
                # Cleanup
                if os.path.exists(temp_file):
                    os.remove(temp_file)

        except subprocess.TimeoutExpired:
            return f"Execution timed out after {timeout} seconds"
        except FileNotFoundError:
            return "Node.js not installed"
        except Exception as e:
            return f"Execution error: {str(e)}"

    @staticmethod
    async def execute_shell(command: str, timeout: int = 30) -> str:
        """Execute shell command safely."""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            output = result.stdout if result.returncode == 0 else result.stderr
            return f"Exit code: {result.returncode}\n\nOutput:\n{output}"

        except subprocess.TimeoutExpired:
            return f"Command timed out after {timeout} seconds"
        except Exception as e:
            return f"Execution error: {str(e)}"
