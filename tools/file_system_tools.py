"""File system tools for MCP"""
import os
import glob
import shutil
from typing import Dict, Any, List
from pathlib import Path
import json

class FileSystemTools:
    """Tools for file system operations."""

    # Safety limits
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS = {'.txt', '.json', '.yaml', '.yml', '.md', '.py', '.js', '.ts', '.html', '.css', '.xml', '.csv', '.log'}

    @staticmethod
    async def handle(name: str, arguments: Dict[str, Any]) -> str:
        """Handle file system tool calls."""

        if name == "read_file":
            return await FileSystemTools.read_file(
                arguments.get("path"),
                arguments.get("encoding", "utf-8")
            )
        elif name == "write_file":
            return await FileSystemTools.write_file(
                arguments.get("path"),
                arguments.get("content"),
                arguments.get("encoding", "utf-8")
            )
        elif name == "list_directory":
            return await FileSystemTools.list_directory(
                arguments.get("path", "."),
                arguments.get("recursive", False)
            )
        elif name == "search_files":
            return await FileSystemTools.search_files(
                arguments.get("pattern"),
                arguments.get("path", "."),
                arguments.get("content_search", None)
            )
        elif name == "delete_file":
            return await FileSystemTools.delete_file(
                arguments.get("path")
            )
        elif name == "create_directory":
            return await FileSystemTools.create_directory(
                arguments.get("path")
            )
        elif name == "copy_file":
            return await FileSystemTools.copy_file(
                arguments.get("source"),
                arguments.get("destination")
            )
        elif name == "move_file":
            return await FileSystemTools.move_file(
                arguments.get("source"),
                arguments.get("destination")
            )
        elif name == "get_file_info":
            return await FileSystemTools.get_file_info(
                arguments.get("path")
            )

        return f"Unknown file system tool: {name}"

    @staticmethod
    def _is_safe_path(path: str) -> bool:
        """Check if path is safe to access."""
        # Prevent directory traversal
        abs_path = os.path.abspath(path)
        # Allow access to /tmp and current working directory
        allowed_dirs = ['/tmp', os.getcwd()]
        return any(abs_path.startswith(os.path.abspath(d)) for d in allowed_dirs)

    @staticmethod
    def _is_safe_extension(path: str) -> bool:
        """Check if file extension is allowed."""
        ext = Path(path).suffix.lower()
        return ext in FileSystemTools.ALLOWED_EXTENSIONS or ext == ''

    @staticmethod
    async def read_file(path: str, encoding: str = "utf-8") -> str:
        """Read contents of a file."""
        try:
            if not FileSystemTools._is_safe_path(path):
                return "Error: Access denied - path outside allowed directories"

            if not os.path.exists(path):
                return f"Error: File not found: {path}"

            if not os.path.isfile(path):
                return f"Error: Path is not a file: {path}"

            file_size = os.path.getsize(path)
            if file_size > FileSystemTools.MAX_FILE_SIZE:
                return f"Error: File too large ({file_size} bytes, max {FileSystemTools.MAX_FILE_SIZE})"

            with open(path, 'r', encoding=encoding) as f:
                content = f.read()

            return f"File: {path}\nSize: {file_size} bytes\n\nContent:\n{content}"

        except UnicodeDecodeError:
            return f"Error: Unable to decode file with {encoding} encoding"
        except Exception as e:
            return f"Error reading file: {str(e)}"

    @staticmethod
    async def write_file(path: str, content: str, encoding: str = "utf-8") -> str:
        """Write content to a file."""
        try:
            if not FileSystemTools._is_safe_path(path):
                return "Error: Access denied - path outside allowed directories"

            if not FileSystemTools._is_safe_extension(path):
                return f"Error: File extension not allowed. Allowed: {FileSystemTools.ALLOWED_EXTENSIONS}"

            # Create parent directory if needed
            parent_dir = os.path.dirname(path)
            if parent_dir and not os.path.exists(parent_dir):
                os.makedirs(parent_dir, exist_ok=True)

            with open(path, 'w', encoding=encoding) as f:
                f.write(content)

            file_size = os.path.getsize(path)
            return f"Successfully wrote {file_size} bytes to {path}"

        except Exception as e:
            return f"Error writing file: {str(e)}"

    @staticmethod
    async def list_directory(path: str = ".", recursive: bool = False) -> str:
        """List contents of a directory."""
        try:
            if not FileSystemTools._is_safe_path(path):
                return "Error: Access denied - path outside allowed directories"

            if not os.path.exists(path):
                return f"Error: Directory not found: {path}"

            if not os.path.isdir(path):
                return f"Error: Path is not a directory: {path}"

            results = []

            if recursive:
                for root, dirs, files in os.walk(path):
                    # Add directories
                    for d in dirs:
                        full_path = os.path.join(root, d)
                        results.append({
                            "path": full_path,
                            "type": "directory",
                            "name": d
                        })
                    # Add files
                    for f in files:
                        full_path = os.path.join(root, f)
                        size = os.path.getsize(full_path)
                        results.append({
                            "path": full_path,
                            "type": "file",
                            "name": f,
                            "size": size
                        })
            else:
                for item in os.listdir(path):
                    full_path = os.path.join(path, item)
                    item_type = "directory" if os.path.isdir(full_path) else "file"
                    item_info = {
                        "path": full_path,
                        "type": item_type,
                        "name": item
                    }
                    if item_type == "file":
                        item_info["size"] = os.path.getsize(full_path)
                    results.append(item_info)

            return f"Found {len(results)} items in {path}:\n\n{json.dumps(results, indent=2)}"

        except Exception as e:
            return f"Error listing directory: {str(e)}"

    @staticmethod
    async def search_files(pattern: str, path: str = ".", content_search: str = None) -> str:
        """Search for files by pattern and optionally by content."""
        try:
            if not FileSystemTools._is_safe_path(path):
                return "Error: Access denied - path outside allowed directories"

            # Search by filename pattern
            search_path = os.path.join(path, "**", pattern)
            matching_files = glob.glob(search_path, recursive=True)

            results = []
            for file_path in matching_files:
                if not os.path.isfile(file_path):
                    continue

                result = {
                    "path": file_path,
                    "size": os.path.getsize(file_path)
                }

                # If content search is specified, search within file
                if content_search:
                    try:
                        if os.path.getsize(file_path) <= FileSystemTools.MAX_FILE_SIZE:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                                if content_search in content:
                                    # Find line numbers where content appears
                                    lines = content.split('\n')
                                    matches = [i+1 for i, line in enumerate(lines) if content_search in line]
                                    result["content_matches"] = matches
                                    results.append(result)
                    except:
                        pass  # Skip files that can't be read
                else:
                    results.append(result)

            return f"Found {len(results)} matching files:\n\n{json.dumps(results, indent=2)}"

        except Exception as e:
            return f"Error searching files: {str(e)}"

    @staticmethod
    async def delete_file(path: str) -> str:
        """Delete a file or directory."""
        try:
            if not FileSystemTools._is_safe_path(path):
                return "Error: Access denied - path outside allowed directories"

            if not os.path.exists(path):
                return f"Error: Path not found: {path}"

            if os.path.isfile(path):
                os.remove(path)
                return f"Successfully deleted file: {path}"
            elif os.path.isdir(path):
                shutil.rmtree(path)
                return f"Successfully deleted directory: {path}"
            else:
                return f"Error: Unknown file type: {path}"

        except Exception as e:
            return f"Error deleting: {str(e)}"

    @staticmethod
    async def create_directory(path: str) -> str:
        """Create a directory."""
        try:
            if not FileSystemTools._is_safe_path(path):
                return "Error: Access denied - path outside allowed directories"

            os.makedirs(path, exist_ok=True)
            return f"Successfully created directory: {path}"

        except Exception as e:
            return f"Error creating directory: {str(e)}"

    @staticmethod
    async def copy_file(source: str, destination: str) -> str:
        """Copy a file."""
        try:
            if not FileSystemTools._is_safe_path(source) or not FileSystemTools._is_safe_path(destination):
                return "Error: Access denied - path outside allowed directories"

            if not os.path.exists(source):
                return f"Error: Source file not found: {source}"

            if os.path.isfile(source):
                shutil.copy2(source, destination)
                return f"Successfully copied {source} to {destination}"
            elif os.path.isdir(source):
                shutil.copytree(source, destination)
                return f"Successfully copied directory {source} to {destination}"
            else:
                return f"Error: Unknown source type: {source}"

        except Exception as e:
            return f"Error copying: {str(e)}"

    @staticmethod
    async def move_file(source: str, destination: str) -> str:
        """Move a file or directory."""
        try:
            if not FileSystemTools._is_safe_path(source) or not FileSystemTools._is_safe_path(destination):
                return "Error: Access denied - path outside allowed directories"

            if not os.path.exists(source):
                return f"Error: Source not found: {source}"

            shutil.move(source, destination)
            return f"Successfully moved {source} to {destination}"

        except Exception as e:
            return f"Error moving: {str(e)}"

    @staticmethod
    async def get_file_info(path: str) -> str:
        """Get detailed information about a file or directory."""
        try:
            if not FileSystemTools._is_safe_path(path):
                return "Error: Access denied - path outside allowed directories"

            if not os.path.exists(path):
                return f"Error: Path not found: {path}"

            stat = os.stat(path)
            info = {
                "path": path,
                "type": "directory" if os.path.isdir(path) else "file",
                "size": stat.st_size,
                "created": stat.st_ctime,
                "modified": stat.st_mtime,
                "accessed": stat.st_atime,
                "permissions": oct(stat.st_mode)[-3:]
            }

            if os.path.isfile(path):
                info["extension"] = Path(path).suffix

            return f"File info:\n{json.dumps(info, indent=2)}"

        except Exception as e:
            return f"Error getting file info: {str(e)}"
