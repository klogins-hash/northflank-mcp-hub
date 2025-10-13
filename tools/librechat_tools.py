"""LibreChat integration tools for MCP"""
import httpx
import os
from typing import Dict, Any

class LibreChatTools:
    """Tools for LibreChat integration."""

    @staticmethod
    async def handle(name: str, arguments: Dict[str, Any]) -> str:
        """Handle LibreChat tool calls."""

        if name == "librechat_send_message":
            return await LibreChatTools.send_message(
                arguments.get("message"),
                arguments.get("conversation_id"),
                arguments.get("model")
            )
        elif name == "librechat_get_config":
            return await LibreChatTools.get_config()

        return f"Unknown LibreChat tool: {name}"

    @staticmethod
    async def send_message(message: str, conversation_id: str = None, model: str = None) -> str:
        """Send message to LibreChat."""
        librechat_url = os.getenv("LIBRECHAT_URL", "https://web--librechat--5d689c8h7r47.code.run")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{librechat_url}/api/ask",
                    json={
                        "text": message,
                        "conversationId": conversation_id,
                        "model": model or "gpt-4"
                    },
                    timeout=30.0
                )

                if response.status_code == 200:
                    return f"Message sent successfully to LibreChat"
                else:
                    return f"Error: {response.status_code}"

        except Exception as e:
            return f"LibreChat connection error: {str(e)}"

    @staticmethod
    async def get_config() -> str:
        """Get LibreChat configuration."""
        librechat_url = os.getenv("LIBRECHAT_URL", "https://web--librechat--5d689c8h7r47.code.run")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{librechat_url}/api/config",
                    timeout=10.0
                )

                if response.status_code == 200:
                    config = response.json()
                    return f"LibreChat config loaded: {len(config)} settings"
                else:
                    return f"Error: {response.status_code}"

        except Exception as e:
            return f"LibreChat connection error: {str(e)}"
