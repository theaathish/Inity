import subprocess
import sys
import os
from pathlib import Path
from typing import Optional, List
from rich.console import Console
from ..templates.registry import TemplateRegistry
from ..utils.python_version import PythonVersionManager
from ..utils.env_generator import EnvGenerator
from ..utils.git_utils import GitUtils

console = Console()

class ProjectCreator:
    def __init__(
        self,
        project_name: str,
        template_name: str,
        parent_dir: Path,
        python_version: Optional[str] = None,
        description: Optional[str] = None,
        additional_packages: List[str] = None,
        dev_dependencies: List[str] = None,
        create_venv: bool = True,
        use_conda: bool = False,
        conda_env_name: Optional[str] = None,
        init_git: bool = True,
        add_docker: bool = False,
        existing_dir: bool = False
    ):
        self.project_name = project_name
        self.template_name = template_name
        self.parent_dir = Path(parent_dir).resolve()  # Resolve to absolute path
        self.python_version = python_version
        self.description = description or f"A Python project created with Inity"
        self.additional_packages = additional_packages or []
        self.dev_dependencies = dev_dependencies or []
        self.create_venv = create_venv
        self.use_conda = use_conda
        self.conda_env_name = conda_env_name
        self.init_git = init_git
        self.add_docker = add_docker
        self.existing_dir = existing_dir
        
        # Fix: Ensure absolute project path
        self.project_path = (self.parent_dir / project_name).resolve()
        self.template_registry = TemplateRegistry()
        self.python_mgr = PythonVersionManager()
    
    def create(self) -> Path:
        """Create the complete project."""
        console.print(f"📁 Creating project directory: {self.project_path}")
        
        # Create project directory with absolute path
        if not self.existing_dir:
            self.project_path.mkdir(parents=True, exist_ok=True)
            console.print(f"✅ Project directory created: {self.project_path}")
        
        # Verify project directory exists
        if not self.project_path.exists():
            raise ValueError(f"Failed to create project directory: {self.project_path}")
        
        # Get template
        template = self.template_registry.get_template(self.template_name)
        if not template:
            raise ValueError(f"Template '{self.template_name}' not found")
        
        # Create virtual environment or conda environment
        if self.use_conda:
            console.print("🐍 Setting up conda environment...")
            self._setup_conda_environment()
        elif self.create_venv:
            console.print("🐍 Creating virtual environment...")
            self._create_virtual_environment()
        
        # Generate project files
        console.print("📄 Generating project files...")
        self._generate_files(template)
        
        # Create requirements files
        console.print("📦 Creating requirements files...")
        self._create_requirements_files(template)
        
        # Auto-install dependencies immediately after creating requirements
        if self.create_venv:
            all_deps = template.dependencies + self.additional_packages
            if all_deps:
                console.print("⬇️ Auto-installing dependencies...")
                self._auto_install_dependencies(all_deps)
            
            if self.dev_dependencies:
                console.print("🛠️ Auto-installing development dependencies...")
                self._auto_install_dev_dependencies()
        
        # Initialize Git LAST
        if self.init_git:
            console.print("🗂️ Initializing Git repository...")
            GitUtils.init_repository(self.project_path)
        
        return self.project_path
    
    def _setup_conda_environment(self):
        """Setup conda environment for the project."""
        if not self.conda_env_name:
            self.conda_env_name = f"{self.project_name.replace('-', '_')}_env"
        
        # Check if environment already exists
        existing_envs = self.python_mgr.get_conda_environments()
        
        if self.conda_env_name not in existing_envs:
            # Create new conda environment
            python_version = self.python_version or "3.11"
            success = self.python_mgr.create_conda_environment(
                self.conda_env_name, 
                python_version
            )
            if not success:
                raise Exception(f"Failed to create conda environment: {self.conda_env_name}")
        else:
            console.print(f"✅ Using existing conda environment: {self.conda_env_name}")
        
        # Create activation script
        self._create_conda_activation_script()
    
    def _create_conda_activation_script(self):
        """Create script to activate conda environment."""
        if os.name == 'nt':  # Windows
            script_content = f"""@echo off
conda activate {self.conda_env_name}
"""
            script_path = self.project_path / "activate.bat"
        else:  # Unix/Linux/macOS
            script_content = f"""#!/bin/bash
conda activate {self.conda_env_name}
"""
            script_path = self.project_path / "activate.sh"
        
        script_path.write_text(script_content, encoding='utf-8')
        
        if os.name != 'nt':
            # Make script executable on Unix systems
            os.chmod(script_path, 0o755)
        
        console.print(f"✅ Created conda activation script: {script_path.name}")
    
    def _create_virtual_environment(self):
        """Create a Python virtual environment in the project directory."""
        # Use absolute path for virtual environment
        venv_path = self.project_path / ".venv"
        console.print(f"Creating .venv at: {venv_path}")
        
        if venv_path.exists():
            console.print("✅ Virtual environment already exists")
            return
        
        try:
            # Get the appropriate Python executable
            python_executable = sys.executable
            if self.python_version:
                python_executable = self.python_mgr.get_python_executable(self.python_version)
            
            console.print(f"Using Python: {python_executable}")
            
            # Change to project directory before creating venv
            original_cwd = Path.cwd()
            os.chdir(self.project_path)
            
            try:
                # Create virtual environment with absolute paths
                result = subprocess.run([
                    python_executable, "-m", "venv", str(venv_path.resolve())
                ], check=True, capture_output=True, text=True)
                
                console.print("✅ Virtual environment creation command completed")
                
            finally:
                # Always change back to original directory
                os.chdir(original_cwd)
            
            # Verify virtual environment was created
            if not venv_path.exists():
                console.print(f"❌ Virtual environment directory not found at: {venv_path}")
                console.print("Attempting alternative creation method...")
                
                # Alternative method: try creating with relative path from project directory
                result = subprocess.run([
                    python_executable, "-m", "venv", ".venv"
                ], check=True, cwd=self.project_path, capture_output=True, text=True)
                
                if not venv_path.exists():
                    raise Exception(f"Virtual environment directory was not created at: {venv_path}")
            
            console.print(f"✅ Virtual environment created successfully at: {venv_path}")
            
            # Check for pip executable
            pip_path = self._get_pip_executable()
            if not pip_path.exists():
                console.print(f"⚠️ Warning: Pip executable not found at: {pip_path}")
                # Try to find pip in alternative locations
                alternative_pip_paths = [
                    venv_path / "bin" / "pip3",
                    venv_path / "Scripts" / "pip3.exe",
                    venv_path / "bin" / "python" / "-m" / "pip",
                ]
                for alt_pip in alternative_pip_paths:
                    if alt_pip.exists():
                        console.print(f"✅ Found pip at alternative location: {alt_pip}")
                        break
                else:
                    console.print("⚠️ Warning: Could not locate pip executable, package installation may fail")
            else:
                console.print(f"✅ Pip available at: {pip_path}")
            
        except subprocess.CalledProcessError as e:
            console.print(f"❌ Failed to create virtual environment: {e}")
            console.print(f"Command output: {e.stdout}")
            console.print(f"Error output: {e.stderr}")
            raise
        except Exception as e:
            console.print(f"❌ Virtual environment creation error: {e}")
            raise
    
    def _generate_files(self, template):
        """Generate all project files from template."""
        context = {
            "project_name": self.project_name,
            "project_name_snake": self.project_name.lower().replace("-", "_").replace(" ", "_"),
            "project_name_title": self.project_name.replace("-", " ").replace("_", " ").title(),
            "description": self.description,
            "python_version": self.python_version or self.python_mgr.get_system_version(),
        }
        
        # Generate files from template
        for file_path, content in template.files.items():
            full_path = self.project_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            try:
                # Render template content
                rendered_content = content.format(**context)
                full_path.write_text(rendered_content, encoding='utf-8')
                console.print(f"✅ Created: {file_path}")
            except Exception as e:
                console.print(f"❌ Failed to create {file_path}: {e}")
        
        # Generate .env file
        if template.env_vars:
            env_generator = EnvGenerator(self.project_path)
            env_generator.generate_env_file(template.env_vars)
            console.print("✅ Created: .env")
        
        # Create .gitignore
        gitignore_content = """# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# Virtual environments
.venv/
venv/
ENV/

# Environment variables
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Distribution / packaging
build/
dist/
*.egg-info/
"""
        gitignore_path = self.project_path / ".gitignore"
        gitignore_path.write_text(gitignore_content, encoding='utf-8')
        console.print("✅ Created: .gitignore")
    
    def _create_requirements_files(self, template):
        """Create requirements.txt and requirements-dev.txt files."""
        # Main requirements
        all_deps = template.dependencies + self.additional_packages
        if all_deps:
            requirements_path = self.project_path / "requirements.txt"
            requirements_content = "\n".join(sorted(set(all_deps))) + "\n"
            requirements_path.write_text(requirements_content, encoding='utf-8')
            console.print(f"✅ Created: requirements.txt with {len(all_deps)} packages")
        
        # Development requirements
        if self.dev_dependencies:
            dev_requirements_path = self.project_path / "requirements-dev.txt"
            dev_content = "\n".join(sorted(set(self.dev_dependencies))) + "\n"
            dev_requirements_path.write_text(dev_content, encoding='utf-8')
            console.print(f"✅ Created: requirements-dev.txt with {len(self.dev_dependencies)} packages")
    
    def _install_dependencies(self, dependencies):
        """Install Python dependencies in virtual environment."""
        if not dependencies:
            return
        
        pip_path = self._get_pip_executable()
        
        if not pip_path.exists():
            console.print(f"❌ Pip executable not found at: {pip_path}")
            return
        
        try:
            # Upgrade pip first
            console.print("🔄 Upgrading pip...")
            result = subprocess.run([
                str(pip_path), "install", "--upgrade", "pip"
            ], check=True, cwd=self.project_path, capture_output=True, text=True)
            
            # Install dependencies
            console.print(f"📦 Installing {len(dependencies)} packages...")
            for dep in dependencies:
                console.print(f"  - {dep}")
            
            result = subprocess.run([
                str(pip_path), "install"] + dependencies,
                check=True, cwd=self.project_path, capture_output=True, text=True
            )
            
            console.print("✅ Dependencies installed successfully")
            
        except subprocess.CalledProcessError as e:
            console.print(f"❌ Failed to install dependencies: {e}")
            console.print(f"Error output: {e.stderr}")
            raise
    
    def _install_dev_dependencies(self):
        """Install development dependencies."""
        if not self.dev_dependencies:
            return
        
        pip_path = self._get_pip_executable()
        
        try:
            console.print(f"🛠️ Installing {len(self.dev_dependencies)} dev packages...")
            for dep in self.dev_dependencies:
                console.print(f"  - {dep}")
            
            result = subprocess.run([
                str(pip_path), "install"] + self.dev_dependencies,
                check=True, cwd=self.project_path, capture_output=True, text=True
            )
            
            console.print("✅ Development dependencies installed successfully")
            
        except subprocess.CalledProcessError as e:
            console.print(f"❌ Failed to install dev dependencies: {e}")
            console.print(f"Error output: {e.stderr}")
    
    def _auto_install_dependencies(self, dependencies):
        """Install dependencies in virtual environment or conda environment."""
        if not dependencies:
            return
        
        if self.use_conda:
            self._install_with_conda_run(dependencies)
        else:
            pip_path = self._get_pip_executable()
            
            # Try multiple pip locations
            possible_pip_paths = [
                pip_path,
                self.project_path / ".venv" / "bin" / "pip3",
                self.project_path / ".venv" / "Scripts" / "pip3.exe",
            ]
            
            working_pip = None
            for possible_pip in possible_pip_paths:
                if possible_pip.exists():
                    working_pip = possible_pip
                    break
            
            if not working_pip:
                console.print(f"❌ No pip executable found. Tried:")
                for pip_attempt in possible_pip_paths:
                    console.print(f"  - {pip_attempt}")
                console.print("Skipping package installation")
                console.print("You can install packages manually with:")
                console.print(f"  cd {self.project_name}")
                console.print("  source .venv/bin/activate  # or .venv\\Scripts\\activate on Windows")
                console.print("  pip install -r requirements.txt")
                return
            
            console.print(f"Using pip: {working_pip}")
            
            try:
                # Upgrade pip first
                console.print("🔄 Upgrading pip...")
                result = subprocess.run([
                    str(working_pip), "install", "--upgrade", "pip"
                ], check=True, cwd=self.project_path, capture_output=True, text=True)
                console.print("✅ Pip upgraded successfully")
                
                # Install dependencies one by one for better error tracking
                console.print(f"📦 Auto-installing {len(dependencies)} packages...")
                
                successful_installs = []
                failed_installs = []
                
                for dep in dependencies:
                    try:
                        console.print(f"  📥 Installing {dep}...")
                        result = subprocess.run([
                            str(working_pip), "install", dep
                        ], check=True, cwd=self.project_path, capture_output=True, text=True)
                        successful_installs.append(dep)
                        console.print(f"  ✅ {dep} installed successfully")
                        
                    except subprocess.CalledProcessError as e:
                        failed_installs.append(dep)
                        console.print(f"  ❌ Failed to install {dep}: {e}")
                        console.print(f"     Error: {e.stderr}")
                
                # Summary
                if successful_installs:
                    console.print(f"✅ Successfully installed: {', '.join(successful_installs)}")
                
                if failed_installs:
                    console.print(f"❌ Failed to install: {', '.join(failed_installs)}")
                    console.print("You can install them manually later with:")
                    for dep in failed_installs:
                        console.print(f"  pip install {dep}")
                
            except subprocess.CalledProcessError as e:
                console.print(f"❌ Failed during package installation: {e}")
                console.print(f"Error output: {e.stderr}")
                console.print("You can install packages manually with:")
                console.print(f"  cd {self.project_name}")
                console.print("  source .venv/bin/activate  # or .venv\\Scripts\\activate on Windows")
                console.print("  pip install -r requirements.txt")
    
    def _auto_install_dev_dependencies(self):
        """Automatically install development dependencies."""
        if not self.dev_dependencies:
            return
        
        pip_path = self._get_pip_executable()
        
        try:
            console.print(f"🛠️ Auto-installing {len(self.dev_dependencies)} dev packages...")
            
            successful_installs = []
            failed_installs = []
            
            for dep in self.dev_dependencies:
                try:
                    console.print(f"  📥 Installing {dep}...")
                    result = subprocess.run([
                        str(pip_path), "install", dep
                    ], check=True, cwd=self.project_path, capture_output=True, text=True)
                    successful_installs.append(dep)
                    console.print(f"  ✅ {dep} installed successfully")
                    
                except subprocess.CalledProcessError as e:
                    failed_installs.append(dep)
                    console.print(f"  ❌ Failed to install {dep}: {e}")
            
            if successful_installs:
                console.print(f"✅ Dev dependencies installed: {', '.join(successful_installs)}")
            
            if failed_installs:
                console.print(f"❌ Failed dev dependencies: {', '.join(failed_installs)}")
            
        except Exception as e:
            console.print(f"❌ Error installing dev dependencies: {e}")
    
    def _get_pip_executable(self) -> Path:
        """Get the pip executable path for the virtual environment or conda."""
        if self.use_conda:
            # For conda environments, pip should be available in the environment
            conda_python = self.python_mgr._get_conda_python_executable(self.conda_env_name)
            conda_pip = Path(conda_python).parent / "pip"
            if conda_pip.exists():
                return conda_pip
            
            # Fallback: try to get pip from conda environment
            try:
                result = subprocess.run([
                    "conda", "run", "-n", self.conda_env_name, "which", "pip"
                ], capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    return Path(result.stdout.strip())
            except:
                pass
        
        # Default venv pip location
        if os.name == 'nt':  # Windows
            return self.project_path / ".venv" / "Scripts" / "pip.exe"
        else:  # Unix/Linux/macOS
            return self.project_path / ".venv" / "bin" / "pip"
    
    def _install_with_conda_run(self, dependencies):
        """Install packages using conda run."""
        try:
            console.print(f"📦 Installing {len(dependencies)} packages with conda...")
            
            # Install packages one by one
            successful_installs = []
            failed_installs = []
            
            for dep in dependencies:
                try:
                    console.print(f"  📥 Installing {dep}...")
                    result = subprocess.run([
                        "conda", "run", "-n", self.conda_env_name, "pip", "install", dep
                    ], check=True, cwd=self.project_path, capture_output=True, text=True)
                    successful_installs.append(dep)
                    console.print(f"  ✅ {dep} installed successfully")
                    
                except subprocess.CalledProcessError as e:
                    failed_installs.append(dep)
                    console.print(f"  ❌ Failed to install {dep}: {e}")
            
            if successful_installs:
                console.print(f"✅ Successfully installed: {', '.join(successful_installs)}")
            
            if failed_installs:
                console.print(f"❌ Failed to install: {', '.join(failed_installs)}")
            
        except Exception as e:
            console.print(f"❌ Error installing with conda: {e}")
