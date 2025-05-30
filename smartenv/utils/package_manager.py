import subprocess
import sys
import os
import json
import re
from pathlib import Path
from typing import List, Dict, Optional, Union
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

class PackageManager:
    """Comprehensive package management for Python environments."""
    
    def __init__(self):
        self.conda_available = self._check_conda_available()
        self.pip_available = self._check_pip_available()
    
    def install_packages(
        self,
        packages: List[str],
        global_scope: bool = False,
        environment: Optional[str] = None,
        from_git: bool = False,
        editable: bool = False,
        upgrade: bool = False,
        force: bool = False,
        extras: bool = False
    ) -> bool:
        """Install packages with various options."""
        
        console.print(f"📦 Installing {len(packages)} packages...")
        
        success_count = 0
        total_count = len(packages)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            
            for package in packages:
                task = progress.add_task(f"Installing {package}...", total=None)
                
                try:
                    success = self._install_single_package(
                        package,
                        global_scope=global_scope,
                        environment=environment,
                        from_git=from_git,
                        editable=editable,
                        upgrade=upgrade,
                        force=force,
                        extras=extras
                    )
                    
                    if success:
                        success_count += 1
                        progress.update(task, description=f"✅ {package} installed")
                    else:
                        progress.update(task, description=f"❌ {package} failed")
                
                except Exception as e:
                    progress.update(task, description=f"❌ {package} error: {e}")
                
                progress.remove_task(task)
        
        console.print(f"📊 Installation complete: {success_count}/{total_count} packages installed")
        return success_count == total_count
    
    def _install_single_package(
        self,
        package: str,
        global_scope: bool = False,
        environment: Optional[str] = None,
        from_git: bool = False,
        editable: bool = False,
        upgrade: bool = False,
        force: bool = False,
        extras: bool = False
    ) -> bool:
        """Install a single package."""
        
        # Build pip command
        cmd = []
        
        # Determine pip executable
        if environment and environment.startswith("conda:"):
            # Conda environment
            env_name = environment.replace("conda:", "")
            cmd = ["conda", "run", "-n", env_name, "pip"]
        elif environment and environment.startswith("venv:"):
            # Virtual environment
            venv_path = environment.replace("venv:", "")
            if os.name == 'nt':
                pip_path = Path(venv_path) / "Scripts" / "pip.exe"
            else:
                pip_path = Path(venv_path) / "bin" / "pip"
            cmd = [str(pip_path)]
        elif global_scope:
            # Global installation
            cmd = [sys.executable, "-m", "pip"]
        else:
            # Current environment
            cmd = ["pip"]
        
        cmd.append("install")
        
        # Add options
        if upgrade:
            cmd.append("--upgrade")
        
        if force:
            cmd.extend(["--force-reinstall", "--no-deps"])
        
        # Handle git repositories
        if from_git or "git+" in package:
            if editable and not package.startswith("-e"):
                cmd.append("-e")
            cmd.append(package)
        else:
            # Regular package
            if extras:
                # Add common extras
                if "[" not in package:
                    package += "[all]"
            cmd.append(package)
        
        try:
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            return True
            
        except subprocess.CalledProcessError as e:
            console.print(f"[red]Failed to install {package}: {e.stderr}[/red]")
            return False
        except subprocess.TimeoutExpired:
            console.print(f"[red]Installation of {package} timed out[/red]")
            return False
    
    def uninstall_packages(
        self,
        packages: List[str],
        global_scope: bool = False,
        environment: Optional[str] = None
    ) -> bool:
        """Uninstall packages."""
        
        console.print(f"🗑️ Uninstalling {len(packages)} packages...")
        
        success_count = 0
        
        for package in packages:
            try:
                # Build uninstall command
                cmd = self._get_pip_command(global_scope, environment)
                cmd.extend(["uninstall", package, "-y"])
                
                result = subprocess.run(
                    cmd,
                    check=True,
                    capture_output=True,
                    text=True
                )
                
                console.print(f"✅ Uninstalled: {package}")
                success_count += 1
                
            except subprocess.CalledProcessError as e:
                console.print(f"❌ Failed to uninstall {package}: {e.stderr}")
        
        return success_count == len(packages)
    
    def list_current_packages(self, outdated: bool = False) -> List[Dict]:
        """List packages in current environment."""
        return self._list_packages_with_pip(["pip", "list"], outdated)
    
    def list_global_packages(self, outdated: bool = False) -> List[Dict]:
        """List globally installed packages."""
        cmd = [sys.executable, "-m", "pip", "list"]
        return self._list_packages_with_pip(cmd, outdated)
    
    def list_environment_packages(self, environment: str, outdated: bool = False) -> List[Dict]:
        """List packages in specific environment."""
        cmd = self._get_pip_command(False, environment)
        cmd.append("list")
        return self._list_packages_with_pip(cmd, outdated)
    
    def _list_packages_with_pip(self, base_cmd: List[str], outdated: bool = False) -> List[Dict]:
        """List packages using pip list command."""
        try:
            # Get installed packages
            cmd = base_cmd + ["--format=json"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            packages = json.loads(result.stdout)
            
            if outdated:
                # Get outdated packages
                outdated_cmd = base_cmd + ["--outdated", "--format=json"]
                try:
                    outdated_result = subprocess.run(outdated_cmd, capture_output=True, text=True, check=True)
                    outdated_packages = json.loads(outdated_result.stdout)
                    outdated_dict = {pkg["name"]: pkg["latest_version"] for pkg in outdated_packages}
                    
                    # Add latest version info
                    for pkg in packages:
                        pkg["latest"] = outdated_dict.get(pkg["name"], pkg["version"])
                        
                except:
                    pass
            
            return packages
            
        except Exception as e:
            console.print(f"[red]Failed to list packages: {e}[/red]")
            return []
    
    def update_packages(
        self,
        packages: List[str],
        global_scope: bool = False,
        environment: Optional[str] = None
    ) -> bool:
        """Update packages to latest versions."""
        
        return self.install_packages(
            packages,
            global_scope=global_scope,
            environment=environment,
            upgrade=True
        )
    
    def get_package_info(self, package: str, environment: Optional[str] = None) -> Optional[Dict]:
        """Get detailed information about an installed package."""
        try:
            cmd = self._get_pip_command(False, environment)
            cmd.extend(["show", package])
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Parse pip show output
            info = {}
            for line in result.stdout.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    info[key.strip().lower().replace('-', '_')] = value.strip()
            
            return info
            
        except subprocess.CalledProcessError:
            return None
    
    def get_available_environments(self) -> Dict[str, List[str]]:
        """Get list of available Python environments."""
        environments = {
            "conda": [],
            "venv": []
        }
        
        # Get conda environments
        if self.conda_available:
            try:
                result = subprocess.run(
                    ["conda", "env", "list", "--json"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                data = json.loads(result.stdout)
                environments["conda"] = [Path(env).name for env in data.get("envs", [])]
            except:
                pass
        
        # Look for virtual environments in common locations
        venv_locations = [
            Path.home() / ".virtualenvs",
            Path.cwd() / ".venv",
            Path.cwd() / "venv",
        ]
        
        for location in venv_locations:
            if location.exists() and location.is_dir():
                if location.name in [".venv", "venv"]:
                    environments["venv"].append(str(location))
                else:
                    # Check subdirectories
                    for subdir in location.iterdir():
                        if subdir.is_dir() and (subdir / "pyvenv.cfg").exists():
                            environments["venv"].append(str(subdir))
        
        return environments
    
    def install_from_git(
        self,
        git_url: str,
        editable: bool = False,
        global_scope: bool = False,
        environment: Optional[str] = None
    ) -> bool:
        """Install package directly from git repository."""
        
        console.print(f"📥 Installing from git: {git_url}")
        
        # Validate git URL
        if not self._validate_git_url(git_url):
            console.print(f"[red]Invalid git URL: {git_url}[/red]")
            return False
        
        # Prepare git package specification
        if not git_url.startswith("git+"):
            git_url = f"git+{git_url}"
        
        return self._install_single_package(
            git_url,
            global_scope=global_scope,
            environment=environment,
            from_git=True,
            editable=editable
        )
    
    def _validate_git_url(self, url: str) -> bool:
        """Validate git repository URL."""
        git_patterns = [
            r'^https://github\.com/[\w\-\.]+/[\w\-\.]+(?:\.git)?$',
            r'^https://gitlab\.com/[\w\-\.]+/[\w\-\.]+(?:\.git)?$',
            r'^https://bitbucket\.org/[\w\-\.]+/[\w\-\.]+(?:\.git)?$',
            r'^git@[\w\.\-]+:[\w\-\.]+/[\w\-\.]+(?:\.git)?$',
            r'^ssh://git@[\w\.\-]+/[\w\-\.]+/[\w\-\.]+(?:\.git)?$'
        ]
        
        return any(re.match(pattern, url) for pattern in git_patterns)
    
    def _get_pip_command(self, global_scope: bool, environment: Optional[str]) -> List[str]:
        """Get appropriate pip command for the target environment."""
        if environment and environment.startswith("conda:"):
            env_name = environment.replace("conda:", "")
            return ["conda", "run", "-n", env_name, "pip"]
        elif environment and environment.startswith("venv:"):
            venv_path = environment.replace("venv:", "")
            if os.name == 'nt':
                pip_path = Path(venv_path) / "Scripts" / "pip.exe"
            else:
                pip_path = Path(venv_path) / "bin" / "pip"
            return [str(pip_path)]
        elif global_scope:
            return [sys.executable, "-m", "pip"]
        else:
            return ["pip"]
    
    def _check_conda_available(self) -> bool:
        """Check if conda is available."""
        try:
            subprocess.run(["conda", "--version"], 
                         check=True, capture_output=True, timeout=5)
            return True
        except:
            return False
    
    def _check_pip_available(self) -> bool:
        """Check if pip is available."""
        try:
            subprocess.run(["pip", "--version"], 
                         check=True, capture_output=True, timeout=5)
            return True
        except:
            return False
