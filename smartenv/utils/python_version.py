import subprocess
import sys
import re
import os
from typing import List, Optional, Dict
from pathlib import Path
from rich.console import Console

console = Console()

class PythonVersionManager:
    """Manage Python version detection, installation, and selection."""
    
    def __init__(self):
        self.conda_available = self._check_conda_available()
        self.pyenv_available = self._check_pyenv_available()
    
    def get_system_version(self) -> str:
        """Get the current Python version."""
        return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    
    def get_available_versions(self) -> List[str]:
        """Get available Python versions on the system."""
        versions = {}
        
        # Add current Python version
        current = self.get_system_version()
        versions[current] = f"{current} (current system)"
        
        # Check for other system Python installations
        system_versions = self._find_system_python_versions()
        for version, path in system_versions.items():
            if version not in versions:
                versions[version] = f"{version} (system: {path})"
        
        # Check for Conda environments
        if self.conda_available:
            conda_versions = self._get_conda_python_versions()
            for version, env_name in conda_versions.items():
                if version not in versions:
                    versions[version] = f"{version} (conda: {env_name})"
        
        # Check for pyenv versions
        if self.pyenv_available:
            pyenv_versions = self._get_pyenv_versions()
            for version in pyenv_versions:
                if version not in versions:
                    versions[version] = f"{version} (pyenv)"
        
        # Convert to list of choices
        choices = []
        for version, description in versions.items():
            choices.append(description)
        
        return choices
    
    def get_installable_versions(self) -> List[str]:
        """Get Python versions that can be installed."""
        installable = []
        
        # Popular Python versions that can be installed
        popular_versions = [
            "3.12.1", "3.12.0",
            "3.11.7", "3.11.6", "3.11.5",
            "3.10.13", "3.10.12", "3.10.11",
            "3.9.18", "3.9.17",
            "3.8.18", "3.8.17"
        ]
        
        if self.conda_available:
            installable.extend([f"{v} (via conda)" for v in popular_versions])
        
        if self.pyenv_available:
            installable.extend([f"{v} (via pyenv)" for v in popular_versions])
        
        return installable
    
    def install_python_version(self, version: str, method: str = "auto") -> bool:
        """Install a specific Python version."""
        clean_version = version.split(" ")[0]  # Remove extra info
        
        if method == "auto":
            if self.conda_available:
                method = "conda"
            elif self.pyenv_available:
                method = "pyenv"
            else:
                console.print("[yellow]No Python version manager available for installation[/yellow]")
                return False
        
        try:
            if method == "conda":
                return self._install_with_conda(clean_version)
            elif method == "pyenv":
                return self._install_with_pyenv(clean_version)
            else:
                console.print(f"[red]Unknown installation method: {method}[/red]")
                return False
        except Exception as e:
            console.print(f"[red]Failed to install Python {clean_version}: {e}[/red]")
            return False
    
    def create_conda_environment(self, env_name: str, python_version: str) -> bool:
        """Create a new conda environment with specific Python version."""
        if not self.conda_available:
            console.print("[red]Conda is not available[/red]")
            return False
        
        try:
            console.print(f"🐍 Creating conda environment '{env_name}' with Python {python_version}")
            
            result = subprocess.run([
                "conda", "create", "-n", env_name, f"python={python_version}", "-y"
            ], check=True, capture_output=True, text=True)
            
            console.print(f"✅ Conda environment '{env_name}' created successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            console.print(f"❌ Failed to create conda environment: {e}")
            console.print(f"Error output: {e.stderr}")
            return False
    
    def get_conda_environments(self) -> Dict[str, str]:
        """Get list of available conda environments."""
        if not self.conda_available:
            return {}
        
        try:
            result = subprocess.run([
                "conda", "env", "list", "--json"
            ], check=True, capture_output=True, text=True)
            
            import json
            data = json.loads(result.stdout)
            
            environments = {}
            for env_path in data.get("envs", []):
                env_name = Path(env_path).name
                # Get Python version for each environment
                python_path = Path(env_path) / "bin" / "python"
                if not python_path.exists():
                    python_path = Path(env_path) / "Scripts" / "python.exe"
                
                if python_path.exists():
                    try:
                        version_result = subprocess.run([
                            str(python_path), "--version"
                        ], capture_output=True, text=True, timeout=5)
                        
                        version_match = re.search(r'Python (\d+\.\d+\.\d+)', version_result.stdout)
                        if version_match:
                            environments[env_name] = version_match.group(1)
                    except:
                        environments[env_name] = "unknown"
            
            return environments
            
        except Exception:
            return {}
    
    def get_default_version(self) -> str:
        """Get the default recommended Python version."""
        versions = self.get_available_versions()
        return versions[0] if versions else self.get_system_version()
    
    def get_python_executable(self, version_description: str) -> str:
        """Get the executable path for a specific Python version."""
        # Extract version and source from description
        if "conda:" in version_description:
            # Extract conda environment name
            env_match = re.search(r'conda: ([^)]+)', version_description)
            if env_match:
                env_name = env_match.group(1)
                return self._get_conda_python_executable(env_name)
        
        elif "pyenv" in version_description:
            # Extract version for pyenv
            version_match = re.search(r'(\d+\.\d+\.\d+)', version_description)
            if version_match:
                version = version_match.group(1)
                return self._get_pyenv_python_executable(version)
        
        elif "system:" in version_description:
            # Extract system path
            path_match = re.search(r'system: ([^)]+)', version_description)
            if path_match:
                return path_match.group(1)
        
        # Fallback to system python
        return sys.executable
    
    def _check_conda_available(self) -> bool:
        """Check if conda is available."""
        try:
            subprocess.run(["conda", "--version"], 
                         check=True, capture_output=True, timeout=5)
            return True
        except:
            return False
    
    def _check_pyenv_available(self) -> bool:
        """Check if pyenv is available."""
        try:
            subprocess.run(["pyenv", "--version"], 
                         check=True, capture_output=True, timeout=5)
            return True
        except:
            return False
    
    def _find_system_python_versions(self) -> Dict[str, str]:
        """Find Python installations on the system."""
        versions = {}
        
        # Common Python executable patterns
        patterns = [
            "python3.12", "python3.11", "python3.10", "python3.9", "python3.8",
            "python312", "python311", "python310", "python39", "python38"
        ]
        
        for pattern in patterns:
            try:
                result = subprocess.run([pattern, "--version"], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    version_match = re.search(r'Python (\d+\.\d+\.\d+)', result.stdout)
                    if version_match:
                        version = version_match.group(1)
                        # Find full path
                        path_result = subprocess.run(["which", pattern], 
                                                   capture_output=True, text=True, timeout=5)
                        if path_result.returncode == 0:
                            versions[version] = path_result.stdout.strip()
            except:
                continue
        
        return versions
    
    def _get_conda_python_versions(self) -> Dict[str, str]:
        """Get Python versions from conda environments."""
        environments = self.get_conda_environments()
        return {version: env_name for env_name, version in environments.items()}
    
    def _get_pyenv_versions(self) -> List[str]:
        """Get Python versions available through pyenv."""
        try:
            result = subprocess.run(["pyenv", "versions", "--bare"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                versions = []
                for line in result.stdout.strip().split('\n'):
                    if line and re.match(r'^\d+\.\d+\.\d+$', line.strip()):
                        versions.append(line.strip())
                return versions
        except:
            pass
        return []
    
    def _install_with_conda(self, version: str) -> bool:
        """Install Python version using conda."""
        try:
            console.print(f"📦 Installing Python {version} with conda...")
            
            result = subprocess.run([
                "conda", "install", f"python={version}", "-y"
            ], check=True, capture_output=True, text=True)
            
            console.print(f"✅ Python {version} installed successfully with conda")
            return True
            
        except subprocess.CalledProcessError as e:
            console.print(f"❌ Failed to install with conda: {e.stderr}")
            return False
    
    def _install_with_pyenv(self, version: str) -> bool:
        """Install Python version using pyenv."""
        try:
            console.print(f"📦 Installing Python {version} with pyenv...")
            
            result = subprocess.run([
                "pyenv", "install", version
            ], check=True, capture_output=True, text=True)
            
            console.print(f"✅ Python {version} installed successfully with pyenv")
            return True
            
        except subprocess.CalledProcessError as e:
            console.print(f"❌ Failed to install with pyenv: {e.stderr}")
            return False
    
    def _get_conda_python_executable(self, env_name: str) -> str:
        """Get Python executable for a conda environment."""
        try:
            result = subprocess.run([
                "conda", "info", "--envs", "--json"
            ], capture_output=True, text=True, timeout=5)
            
            import json
            data = json.loads(result.stdout)
            
            for env_path in data.get("envs", []):
                if Path(env_path).name == env_name:
                    # Try different possible Python paths
                    python_paths = [
                        Path(env_path) / "bin" / "python",
                        Path(env_path) / "Scripts" / "python.exe"
                    ]
                    
                    for python_path in python_paths:
                        if python_path.exists():
                            return str(python_path)
        except:
            pass
        
        return sys.executable
    
    def _get_pyenv_python_executable(self, version: str) -> str:
        """Get Python executable for a pyenv version."""
        try:
            result = subprocess.run([
                "pyenv", "prefix", version
            ], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                prefix = result.stdout.strip()
                python_path = Path(prefix) / "bin" / "python"
                if python_path.exists():
                    return str(python_path)
        except:
            pass
        
        return sys.executable
