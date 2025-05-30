import subprocess
from pathlib import Path
from rich.console import Console

console = Console()

class GitUtils:
    """Utilities for Git operations."""
    
    @staticmethod
    def init_repository(project_path: Path):
        """Initialize a Git repository in the project directory."""
        try:
            # Check if git is available
            subprocess.run(
                ["git", "--version"],
                check=True,
                capture_output=True
            )
            
            # Initialize git repository
            result = subprocess.run(
                ["git", "init"],
                cwd=project_path,
                check=True,
                capture_output=True,
                text=True
            )
            console.print("✅ Git repository initialized")
            
            # Configure git if needed (basic setup)
            try:
                subprocess.run(
                    ["git", "config", "user.name"],
                    cwd=project_path,
                    check=True,
                    capture_output=True
                )
            except subprocess.CalledProcessError:
                # No global git config, set basic ones
                subprocess.run(
                    ["git", "config", "user.name", "Inity User"],
                    cwd=project_path,
                    check=True,
                    capture_output=True
                )
                subprocess.run(
                    ["git", "config", "user.email", "user@strucureo.dev"],
                    cwd=project_path,
                    check=True,
                    capture_output=True
                )
            
            # Add all files
            subprocess.run(
                ["git", "add", "."],
                cwd=project_path,
                check=True,
                capture_output=True
            )
            
            # Initial commit
            subprocess.run(
                ["git", "commit", "-m", "Initial commit - Created with Inity by Strucureo"],
                cwd=project_path,
                check=True,
                capture_output=True
            )
            console.print("✅ Initial commit created")
            
        except subprocess.CalledProcessError as e:
            console.print(f"⚠️ Git initialization failed: {e}")
        except FileNotFoundError:
            console.print("⚠️ Git not found - skipping repository initialization")
