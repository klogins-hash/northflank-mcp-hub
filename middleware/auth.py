"""Authentication middleware for MCP Hub"""
import os
import secrets
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable

class APIKeyMiddleware(BaseHTTPMiddleware):
    """Middleware to enforce API key authentication."""

    def __init__(self, app, api_key: str = None):
        super().__init__(app)
        # Use provided API key or generate one from env
        self.api_key = api_key or os.getenv("MCP_API_KEY")

        # Public endpoints that don't require auth
        self.public_paths = ["/health", "/", "/docs", "/openapi.json", "/redoc"]

    async def dispatch(self, request: Request, call_next: Callable):
        # Allow public endpoints
        if request.url.path in self.public_paths:
            return await call_next(request)

        # Check for API key if configured
        if self.api_key:
            # Check Authorization header (Bearer token)
            auth_header = request.headers.get("Authorization")
            api_key_header = request.headers.get("X-API-Key")

            valid = False

            # Support both Bearer token and X-API-Key header
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header[7:]
                valid = secrets.compare_digest(token, self.api_key)
            elif api_key_header:
                valid = secrets.compare_digest(api_key_header, self.api_key)

            if not valid:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid or missing API key",
                    headers={"WWW-Authenticate": "Bearer"}
                )

        response = await call_next(request)
        return response


def generate_api_key(length: int = 32) -> str:
    """Generate a secure random API key."""
    return secrets.token_urlsafe(length)
