"""Git operation tools for MCP"""
import subprocess
import os
from typing import Dict, Any
import json

class GitTools:
    """Tools for Git operations."""

    @staticmethod
    async def handle(name: str, arguments: Dict[str, Any]) -> str:
        """Handle Git tool calls."""

        if name == "git_clone":
            return await GitTools.git_clone(
                arguments.get("repository"),
                arguments.get("destination", None),
                arguments.get("branch", None)
            )
        elif name == "git_status":
            return await GitTools.git_status(
                arguments.get("path", ".")
            )
        elif name == "git_add":
            return await GitTools.git_add(
                arguments.get("path", "."),
                arguments.get("files", [])
            )
        elif name == "git_commit":
            return await GitTools.git_commit(
                arguments.get("path", "."),
                arguments.get("message")
            )
        elif name == "git_push":
            return await GitTools.git_push(
                arguments.get("path", "."),
                arguments.get("remote", "origin"),
                arguments.get("branch", None)
            )
        elif name == "git_pull":
            return await GitTools.git_pull(
                arguments.get("path", "."),
                arguments.get("remote", "origin"),
                arguments.get("branch", None)
            )
        elif name == "git_diff":
            return await GitTools.git_diff(
                arguments.get("path", "."),
                arguments.get("cached", False)
            )
        elif name == "git_log":
            return await GitTools.git_log(
                arguments.get("path", "."),
                arguments.get("limit", 10)
            )
        elif name == "git_branch":
            return await GitTools.git_branch(
                arguments.get("path", "."),
                arguments.get("action", "list"),
                arguments.get("branch_name", None)
            )
        elif name == "git_checkout":
            return await GitTools.git_checkout(
                arguments.get("path", "."),
                arguments.get("branch")
            )
        elif name == "git_remote":
            return await GitTools.git_remote(
                arguments.get("path", "."),
                arguments.get("action", "list")
            )

        return f"Unknown git tool: {name}"

    @staticmethod
    def _run_git_command(command: list, cwd: str = None, timeout: int = 30) -> Dict[str, Any]:
        """Run a git command and return result."""
        try:
            result = subprocess.run(
                command,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
                "exit_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Command timed out after {timeout} seconds",
                "exit_code": -1
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "exit_code": -1
            }

    @staticmethod
    async def git_clone(repository: str, destination: str = None, branch: str = None) -> str:
        """Clone a Git repository."""
        try:
            command = ["git", "clone"]

            if branch:
                command.extend(["--branch", branch])

            command.append(repository)

            if destination:
                command.append(destination)

            result = GitTools._run_git_command(command, timeout=120)

            if result["success"]:
                return f"Successfully cloned {repository}\n\n{result['stdout']}"
            else:
                return f"Error cloning repository:\n{result['stderr']}"

        except Exception as e:
            return f"Error: {str(e)}"

    @staticmethod
    async def git_status(path: str = ".") -> str:
        """Get git status of repository."""
        try:
            result = GitTools._run_git_command(["git", "status", "--porcelain"], cwd=path)

            if not result["success"]:
                return f"Error: {result['stderr']}"

            if not result["stdout"]:
                return "Working tree is clean"

            # Parse status output
            lines = result["stdout"].split('\n')
            modified = []
            untracked = []
            staged = []

            for line in lines:
                if not line:
                    continue
                status = line[:2]
                filepath = line[3:]

                if status[0] in ['M', 'A', 'D', 'R', 'C']:
                    staged.append(f"{status[0]} {filepath}")
                if status[1] == 'M':
                    modified.append(filepath)
                elif status == '??':
                    untracked.append(filepath)

            output = []
            if staged:
                output.append(f"Staged files ({len(staged)}):\n  " + "\n  ".join(staged))
            if modified:
                output.append(f"Modified files ({len(modified)}):\n  " + "\n  ".join(modified))
            if untracked:
                output.append(f"Untracked files ({len(untracked)}):\n  " + "\n  ".join(untracked))

            return "\n\n".join(output) if output else "Working tree is clean"

        except Exception as e:
            return f"Error: {str(e)}"

    @staticmethod
    async def git_add(path: str = ".", files: list = None) -> str:
        """Stage files for commit."""
        try:
            if not files:
                files = ["."]

            command = ["git", "add"] + files
            result = GitTools._run_git_command(command, cwd=path)

            if result["success"]:
                return f"Successfully staged files: {', '.join(files)}"
            else:
                return f"Error staging files:\n{result['stderr']}"

        except Exception as e:
            return f"Error: {str(e)}"

    @staticmethod
    async def git_commit(path: str = ".", message: str = None) -> str:
        """Commit staged changes."""
        try:
            if not message:
                return "Error: Commit message is required"

            command = ["git", "commit", "-m", message]
            result = GitTools._run_git_command(command, cwd=path)

            if result["success"]:
                return f"Successfully committed:\n{result['stdout']}"
            else:
                return f"Error committing:\n{result['stderr']}"

        except Exception as e:
            return f"Error: {str(e)}"

    @staticmethod
    async def git_push(path: str = ".", remote: str = "origin", branch: str = None) -> str:
        """Push commits to remote."""
        try:
            command = ["git", "push", remote]

            if branch:
                command.append(branch)

            result = GitTools._run_git_command(command, cwd=path, timeout=60)

            if result["success"]:
                return f"Successfully pushed to {remote}\n{result['stdout']}"
            else:
                return f"Error pushing:\n{result['stderr']}"

        except Exception as e:
            return f"Error: {str(e)}"

    @staticmethod
    async def git_pull(path: str = ".", remote: str = "origin", branch: str = None) -> str:
        """Pull changes from remote."""
        try:
            command = ["git", "pull", remote]

            if branch:
                command.append(branch)

            result = GitTools._run_git_command(command, cwd=path, timeout=60)

            if result["success"]:
                return f"Successfully pulled from {remote}\n{result['stdout']}"
            else:
                return f"Error pulling:\n{result['stderr']}"

        except Exception as e:
            return f"Error: {str(e)}"

    @staticmethod
    async def git_diff(path: str = ".", cached: bool = False) -> str:
        """Show git diff."""
        try:
            command = ["git", "diff"]

            if cached:
                command.append("--cached")

            result = GitTools._run_git_command(command, cwd=path)

            if result["success"]:
                if not result["stdout"]:
                    return "No changes to show"
                return f"Diff:\n{result['stdout'][:5000]}"  # Limit output size
            else:
                return f"Error getting diff:\n{result['stderr']}"

        except Exception as e:
            return f"Error: {str(e)}"

    @staticmethod
    async def git_log(path: str = ".", limit: int = 10) -> str:
        """Show git commit history."""
        try:
            command = [
                "git", "log",
                f"-{limit}",
                "--pretty=format:%h|%an|%ae|%ad|%s",
                "--date=short"
            ]

            result = GitTools._run_git_command(command, cwd=path)

            if result["success"]:
                if not result["stdout"]:
                    return "No commits found"

                commits = []
                for line in result["stdout"].split('\n'):
                    parts = line.split('|')
                    if len(parts) == 5:
                        commits.append({
                            "hash": parts[0],
                            "author": parts[1],
                            "email": parts[2],
                            "date": parts[3],
                            "message": parts[4]
                        })

                return f"Last {len(commits)} commits:\n{json.dumps(commits, indent=2)}"
            else:
                return f"Error getting log:\n{result['stderr']}"

        except Exception as e:
            return f"Error: {str(e)}"

    @staticmethod
    async def git_branch(path: str = ".", action: str = "list", branch_name: str = None) -> str:
        """Manage git branches."""
        try:
            if action == "list":
                command = ["git", "branch", "-a"]
            elif action == "create" and branch_name:
                command = ["git", "branch", branch_name]
            elif action == "delete" and branch_name:
                command = ["git", "branch", "-d", branch_name]
            else:
                return "Error: Invalid action or missing branch name"

            result = GitTools._run_git_command(command, cwd=path)

            if result["success"]:
                return f"Branch operation successful:\n{result['stdout']}"
            else:
                return f"Error with branch operation:\n{result['stderr']}"

        except Exception as e:
            return f"Error: {str(e)}"

    @staticmethod
    async def git_checkout(path: str = ".", branch: str = None) -> str:
        """Checkout a branch."""
        try:
            if not branch:
                return "Error: Branch name is required"

            command = ["git", "checkout", branch]
            result = GitTools._run_git_command(command, cwd=path)

            if result["success"]:
                return f"Successfully checked out {branch}\n{result['stdout']}"
            else:
                return f"Error checking out branch:\n{result['stderr']}"

        except Exception as e:
            return f"Error: {str(e)}"

    @staticmethod
    async def git_remote(path: str = ".", action: str = "list") -> str:
        """Manage git remotes."""
        try:
            if action == "list":
                command = ["git", "remote", "-v"]
            else:
                return "Error: Invalid action"

            result = GitTools._run_git_command(command, cwd=path)

            if result["success"]:
                if not result["stdout"]:
                    return "No remotes configured"
                return f"Remotes:\n{result['stdout']}"
            else:
                return f"Error getting remotes:\n{result['stderr']}"

        except Exception as e:
            return f"Error: {str(e)}"
