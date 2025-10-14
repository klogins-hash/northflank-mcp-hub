"""MinIO object storage tools for MCP"""
import os
import httpx
from typing import Dict, Any
import base64

class MinIOTools:
    """Tools for MinIO object storage operations."""

    @staticmethod
    async def handle(name: str, arguments: Dict[str, Any]) -> str:
        """Handle MinIO tool calls."""

        if name == "minio_list_buckets":
            return await MinIOTools.list_buckets()
        elif name == "minio_list_objects":
            return await MinIOTools.list_objects(
                arguments.get("bucket")
            )
        elif name == "minio_get_object":
            return await MinIOTools.get_object(
                arguments.get("bucket"),
                arguments.get("object_key")
            )
        elif name == "minio_put_object":
            return await MinIOTools.put_object(
                arguments.get("bucket"),
                arguments.get("object_key"),
                arguments.get("data")
            )

        return f"Unknown MinIO tool: {name}"

    @staticmethod
    async def list_buckets() -> str:
        """List all MinIO buckets."""
        minio_url = os.getenv("MINIO_URL")
        access_key = os.getenv("MINIO_ACCESS_KEY")
        secret_key = os.getenv("MINIO_SECRET_KEY")

        if not all([minio_url, access_key, secret_key]):
            return "MinIO not configured. Set MINIO_URL, MINIO_ACCESS_KEY, MINIO_SECRET_KEY."

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{minio_url}/",
                    auth=(access_key, secret_key),
                    timeout=10.0
                )

                if response.status_code == 200:
                    return f"MinIO connected. Response: {response.text[:200]}"
                else:
                    return f"MinIO status: {response.status_code}"

        except Exception as e:
            return f"MinIO error: {str(e)}"

    @staticmethod
    async def list_objects(bucket: str) -> str:
        """List objects in a MinIO bucket."""
        minio_url = os.getenv("MINIO_URL")
        access_key = os.getenv("MINIO_ACCESS_KEY")
        secret_key = os.getenv("MINIO_SECRET_KEY")

        if not all([minio_url, access_key, secret_key]):
            return "MinIO not configured."

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{minio_url}/{bucket}/",
                    auth=(access_key, secret_key),
                    timeout=10.0
                )

                return f"Bucket '{bucket}' objects: {response.text[:500]}"

        except Exception as e:
            return f"MinIO error: {str(e)}"

    @staticmethod
    async def get_object(bucket: str, object_key: str) -> str:
        """Get an object from MinIO."""
        minio_url = os.getenv("MINIO_URL")
        access_key = os.getenv("MINIO_ACCESS_KEY")
        secret_key = os.getenv("MINIO_SECRET_KEY")

        if not all([minio_url, access_key, secret_key]):
            return "MinIO not configured."

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{minio_url}/{bucket}/{object_key}",
                    auth=(access_key, secret_key),
                    timeout=10.0
                )

                if response.status_code == 200:
                    # Return size info instead of full content
                    return f"Object '{object_key}': {len(response.content)} bytes"
                else:
                    return f"Error getting object: {response.status_code}"

        except Exception as e:
            return f"MinIO error: {str(e)}"

    @staticmethod
    async def put_object(bucket: str, object_key: str, data: str) -> str:
        """Put an object into MinIO."""
        minio_url = os.getenv("MINIO_URL")
        access_key = os.getenv("MINIO_ACCESS_KEY")
        secret_key = os.getenv("MINIO_SECRET_KEY")

        if not all([minio_url, access_key, secret_key]):
            return "MinIO not configured."

        try:
            async with httpx.AsyncClient() as client:
                response = await client.put(
                    f"{minio_url}/{bucket}/{object_key}",
                    content=data.encode() if isinstance(data, str) else data,
                    auth=(access_key, secret_key),
                    timeout=30.0
                )

                if response.status_code in [200, 201]:
                    return f"Object '{object_key}' uploaded successfully"
                else:
                    return f"Error uploading: {response.status_code}"

        except Exception as e:
            return f"MinIO error: {str(e)}"
