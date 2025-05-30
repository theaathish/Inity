import typer
import questionary
import os
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from pathlib import Path
from typing import Optional, List, Dict
from ..core.project_creator import ProjectCreator
from ..templates.registry import TemplateRegistry
from ..utils.python_version import PythonVersionManager
from ..utils.package_search import PackageSearcher

app = typer.Typer()
console = Console()

@app.command()
def project(
    name: Optional[str] = typer.Argument(None, help="Project name"),
    template: Optional[str] = typer.Option(None, "--template", "-t", help="Project template"),
    directory: Optional[str] = typer.Option(".", "--dir", "-d", help="Parent directory"),
    python_version: Optional[str] = typer.Option(None, "--python", "-p", help="Python version (e.g., 3.11)"),
    no_venv: bool = typer.Option(False, "--no-venv", help="Skip virtual environment creation"),
    no_git: bool = typer.Option(False, "--no-git", help="Skip Git initialization"),
    interactive: bool = typer.Option(True, "--interactive/--no-interactive", help="Interactive mode"),
    add_packages: bool = typer.Option(False, "--add-packages", help="Search and add additional packages"),
    use_conda: bool = typer.Option(False, "--conda", help="Use conda environment instead of venv")
):
    """Create a new Python project with smart defaults."""
    
    registry = TemplateRegistry()
    python_mgr = PythonVersionManager()
    package_searcher = PackageSearcher()
    
    # Interactive prompts if not provided
    if interactive:
        console.print("\n🚀 [bold blue]Welcome to Inity![/bold blue] Let's create your Python project.\n")
        
        # Project name
        if not name:
            name = questionary.text(
                "📁 Project name:",
                validate=lambda text: len(text) > 0 or "Project name cannot be empty"
            ).ask()
            if not name:
                console.print("[red]Project name is required![/red]")
                raise typer.Exit(1)
        
        # Project description
        description = questionary.text(
            "📝 Project description (optional):",
            default=f"A Python project created with Inity"
        ).ask()
        
        # Python version and environment management
        python_version, use_conda, conda_env_name = _select_python_environment(python_mgr, python_version, use_conda)
        
        # Template selection
        if not template:
            templates = registry.get_available_templates()
            template_choices = []
            for name_key, tmpl in templates.items():
                template_choices.append(
                    questionary.Choice(
                        title=f"{name_key} - {tmpl.description}",
                        value=name_key
                    )
                )
            
            template = questionary.select(
                "🎯 Choose a project template:",
                choices=template_choices
            ).ask()
        
        # Additional configuration
        config_options = questionary.checkbox(
            "⚙️ Additional configuration:",
            choices=[
                questionary.Choice("Create virtual environment", value="venv", checked=not no_venv and not use_conda),
                questionary.Choice("Use conda environment", value="conda", checked=use_conda),
                questionary.Choice("Initialize Git repository", value="git", checked=not no_git),
                questionary.Choice("Search and add packages", value="packages", checked=add_packages),
                questionary.Choice("Add development dependencies", value="dev_deps", checked=False),
                questionary.Choice("Create Docker configuration", value="docker", checked=False),
            ]
        ).ask()
        
        no_venv = "venv" not in config_options and "conda" not in config_options
        use_conda = "conda" in config_options
        no_git = "git" not in config_options
        add_packages = "packages" in config_options
        add_dev_deps = "dev_deps" in config_options
        add_docker = "docker" in config_options
    
    # Validate inputs
    if not name:
        console.print("[red]Project name is required![/red]")
        raise typer.Exit(1)
    
    if not template:
        template = "basic"
    
    if not python_version:
        python_version = python_mgr.get_system_version()
    
    # Get template and additional packages
    template_obj = registry.get_template(template)
    if not template_obj:
        console.print(f"[red]Template '{template}' not found![/red]")
        raise typer.Exit(1)
    
    additional_packages = []
    dev_dependencies = []
    
    # Package search and selection
    if add_packages and interactive:
        additional_packages = _search_and_select_packages(package_searcher)
    
    # Development dependencies
    if interactive and 'add_dev_deps' in locals() and add_dev_deps:
        dev_dependencies = _select_dev_dependencies()
    
    # Create project
    creator = ProjectCreator(
        project_name=name,
        template_name=template,
        parent_dir=Path(directory),
        python_version=python_version,
        description=description if 'description' in locals() else None,
        additional_packages=additional_packages,
        dev_dependencies=dev_dependencies,
        create_venv=not no_venv and not use_conda,
        use_conda=use_conda,
        conda_env_name=conda_env_name if 'conda_env_name' in locals() else None,
        init_git=not no_git,
        add_docker='add_docker' in locals() and add_docker
    )
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Creating project...", total=None)
        
        try:
            project_path = creator.create()
            progress.update(task, description="✅ Project created successfully!")
            
            # Show success message and next steps
            _show_success_message(name, project_path, python_version, not no_venv)
            
        except Exception as e:
            progress.update(task, description=f"❌ Error: {str(e)}")
            console.print(f"[red]Error creating project: {str(e)}[/red]")
            raise typer.Exit(1)

def _search_and_select_packages(package_searcher: PackageSearcher) -> List[str]:
    """Interactive package search and selection with real-time PyPI integration."""
    packages = []
    
    console.print("\n🔍 [bold blue]Package Search & Selection[/bold blue]")
    console.print("Search for packages from PyPI and add them to your project.\n")
    
    while True:
        search_more = questionary.confirm(
            "🔍 Search for packages to add?",
            default=len(packages) == 0
        ).ask()
        
        if not search_more:
            break
        
        # Get search query
        query = questionary.text(
            "Package name or keyword:",
            instruction="(e.g., 'fastapi', 'database', 'testing')"
        ).ask()
        
        if not query or len(query.strip()) < 2:
            console.print("[yellow]Please enter at least 2 characters[/yellow]")
            continue
        
        # Search packages in real-time
        try:
            search_results = package_searcher.search_packages_realtime(query, limit=15)
        except Exception as e:
            console.print(f"[red]Search failed: {e}[/red]")
            continue
        
        if not search_results:
            console.print(f"[yellow]No packages found for '{query}'[/yellow]")
            continue
        
        # Display search results in a table
        _display_package_results(search_results)
        
        # Package selection with detailed info
        selected_packages = _select_packages_from_results(search_results, package_searcher)
        
        # Add selected packages
        packages.extend(selected_packages)
        
        if packages:
            console.print(f"\n✅ [green]Selected packages:[/green] {', '.join(packages)}")
    
    # Final validation of all selected packages
    if packages:
        console.print("\n🔍 Validating selected packages...")
        valid_packages, invalid_packages = package_searcher.validate_packages(packages)
        
        if invalid_packages:
            console.print(f"[yellow]Warning: Invalid packages removed: {', '.join(invalid_packages)}[/yellow]")
        
        if valid_packages:
            console.print(f"✅ [green]Final package list:[/green] {', '.join(valid_packages)}")
        
        return valid_packages
    
    return packages

def _select_dev_dependencies() -> List[str]:
    """Select common development dependencies."""
    dev_choices = [
        questionary.Choice("pytest - Testing framework", value="pytest", checked=True),
        questionary.Choice("black - Code formatter", value="black", checked=True),
        questionary.Choice("flake8 - Linting", value="flake8", checked=True),
        questionary.Choice("mypy - Type checking", value="mypy", checked=False),
        questionary.Choice("pre-commit - Git hooks", value="pre-commit", checked=False),
        questionary.Choice("pytest-cov - Coverage testing", value="pytest-cov", checked=False),
        questionary.Choice("bandit - Security linting", value="bandit", checked=False),
        questionary.Choice("isort - Import sorting", value="isort", checked=False),
    ]
    
    selected = questionary.checkbox(
        "🛠️ Select development dependencies:",
        choices=dev_choices
    ).ask()
    
    return selected

def _display_package_results(search_results: List[Dict]) -> None:
    """Display search results in a formatted table."""
    table = Table(title="📦 Search Results")
    table.add_column("#", style="dim", width=3)
    table.add_column("Package", style="cyan", min_width=15)
    table.add_column("Version", style="green", width=10)
    table.add_column("Description", style="white")
    table.add_column("Downloads", style="yellow", width=10)
    
    for i, pkg in enumerate(search_results, 1):
        description = pkg.get("description", "No description")
        if len(description) > 50:
            description = description[:47] + "..."
        
        downloads = pkg.get("download_count", 0)
        download_str = f"{downloads:,}" if downloads > 0 else "-"
        
        table.add_row(
            str(i),
            pkg["name"],
            pkg["version"],
            description,
            download_str
        )
    
    console.print(table)

def _select_packages_from_results(search_results: List[Dict], package_searcher: PackageSearcher) -> List[str]:
    """Allow user to select packages from search results with version options."""
    if not search_results:
        return []
    
    # Create choices for package selection
    choices = []
    for i, pkg in enumerate(search_results, 1):
        choice_title = f"{i}. {pkg['name']} ({pkg['version']}) - {pkg['description'][:40]}..."
        choices.append(questionary.Choice(title=choice_title, value=pkg))
    
    # Multi-select packages
    selected_packages_info = questionary.checkbox(
        "Select packages to add (use Space to select, Enter to confirm):",
        choices=choices
    ).ask()
    
    if not selected_packages_info:
        return []
    
    selected_packages = []
    
    # For each selected package, offer version selection
    for pkg_info in selected_packages_info:
        package_name = pkg_info["name"]
        console.print(f"\n🔧 [bold]Configuring {package_name}[/bold]")
        
        # Show detailed package info
        _show_package_details(pkg_info)
        
        # Get available versions
        console.print("🔍 Fetching available versions...")
        versions = package_searcher.get_package_versions_realtime(package_name, limit=8)
        
        if len(versions) <= 1:
            selected_packages.append(package_name)
            console.print(f"✅ Added: {package_name} (latest)")
            continue
        
        # Version selection
        version_choice = _select_package_version(package_name, versions)
        selected_packages.append(version_choice)
        console.print(f"✅ Added: {version_choice}")
    
    return selected_packages

def _show_package_details(pkg_info: Dict) -> None:
    """Display detailed information about a package."""
    console.print(f"📦 [bold cyan]{pkg_info['name']}[/bold cyan] v{pkg_info['version']}")
    console.print(f"📝 {pkg_info.get('description', 'No description available')}")
    
    if pkg_info.get('author'):
        console.print(f"👤 Author: {pkg_info['author']}")
    
    if pkg_info.get('home_page'):
        console.print(f"🌐 Homepage: {pkg_info['home_page']}")
    
    if pkg_info.get('license') and pkg_info['license'] != 'Unknown':
        console.print(f"📄 License: {pkg_info['license']}")
    
    if pkg_info.get('python_requires'):
        console.print(f"🐍 Python: {pkg_info['python_requires']}")

def _select_package_version(package_name: str, versions: List[str]) -> str:
    """Allow user to select a specific version of a package."""
    version_choices = [
        questionary.Choice(title=f"Latest ({versions[0]})", value=package_name),
        questionary.Choice(title="Custom version constraint", value="custom")
    ]
    
    # Add recent versions
    for version in versions[1:6]:  # Show up to 5 recent versions
        version_choices.append(
            questionary.Choice(title=f"Version {version}", value=f"{package_name}=={version}")
        )
    
    selected_version = questionary.select(
        f"Choose version for {package_name}:",
        choices=version_choices
    ).ask()
    
    if selected_version == "custom":
        custom_constraint = questionary.text(
            f"Enter version constraint for {package_name}:",
            instruction="(e.g., >=1.0.0, ~=2.1.0, >=1.0,<2.0)"
        ).ask()
        
        if custom_constraint:
            # Validate constraint format
            if any(op in custom_constraint for op in [">=", "<=", "==", "~=", ">", "<"]):
                return f"{package_name}{custom_constraint}"
            else:
                return f"{package_name}>={custom_constraint}"
        else:
            return package_name
    
    return selected_version

def _show_success_message(name: str, project_path: Path, python_version: str, has_venv: bool) -> None:
    """Show success message and next steps."""
    console.print(f"\n🎉 [green]Project '{name}' created successfully![/green]")
    console.print(f"📁 Location: {project_path}")
    console.print(f"🐍 Python version: {python_version}")
    
    # Show virtual environment info
    if has_venv:
        venv_path = project_path / ".venv"
        console.print(f"🐍 Virtual environment: {venv_path}")
    
    console.print("\n[bold]Next steps:[/bold]")
    console.print(f"  [cyan]cd {name}[/cyan]")
    
    if has_venv:
        if os.name == 'nt':  # Windows
            console.print(f"  [cyan].venv\\Scripts\\activate[/cyan]")
        else:  # Unix/Linux/macOS
            console.print(f"  [cyan]source .venv/bin/activate[/cyan]")
    
    console.print("  [cyan]python main.py[/cyan]")
    
    # Show package installation info
    console.print("\n[bold]Package Management:[/bold]")
    console.print("  📦 Dependencies are auto-installed in the virtual environment")
    console.print("  🔄 To add more packages: pip install <package-name>")
    console.print("  📋 To see installed packages: pip list")
    
    # Template-specific info
    console.print("\n[bold]Project Info:[/bold]")
    console.print("  📄 All project files have been generated")
    console.print("  🔐 Environment variables are in .env file")
    console.print("  📝 Documentation is in README.md")

def _select_python_environment(python_mgr: PythonVersionManager, python_version: Optional[str], use_conda: bool) -> tuple:
    """Handle Python version and environment selection."""
    
    # Check available environment managers
    has_conda = python_mgr.conda_available
    has_pyenv = python_mgr.pyenv_available
    
    if has_conda or has_pyenv:
        env_choice = questionary.select(
            "🐍 Choose Python environment management:",
            choices=[
                questionary.Choice("Use system venv (recommended)", value="venv"),
                questionary.Choice("Use conda environment", value="conda") if has_conda else None,
                questionary.Choice("Install new Python version", value="install") if (has_conda or has_pyenv) else None,
            ],
            default="venv"
        ).ask()
    else:
        env_choice = "venv"
    
    conda_env_name = None
    
    if env_choice == "conda" and has_conda:
        use_conda = True
        
        # Show existing conda environments
        existing_envs = python_mgr.get_conda_environments()
        if existing_envs:
            console.print("\n📦 [bold]Existing Conda Environments:[/bold]")
            for env_name, py_version in existing_envs.items():
                console.print(f"  {env_name} (Python {py_version})")
        
        env_action = questionary.select(
            "Conda environment action:",
            choices=[
                "Create new conda environment",
                "Use existing conda environment" if existing_envs else None,
            ]
        ).ask()
        
        if env_action == "Create new conda environment":
            conda_env_name = questionary.text(
                "Environment name:",
                default=f"{name.replace('-', '_')}_env"
            ).ask()
            
            # Select Python version for conda environment
            if not python_version:
                python_choices = ["3.12", "3.11", "3.10", "3.9", "3.8"]
                python_version = questionary.select(
                    "Python version for conda environment:",
                    choices=python_choices,
                    default="3.11"
                ).ask()
        
        elif env_action == "Use existing conda environment":
            env_choices = [f"{env} (Python {ver})" for env, ver in existing_envs.items()]
            selected_env = questionary.select(
                "Select conda environment:",
                choices=env_choices
            ).ask()
            conda_env_name = selected_env.split(" ")[0]
            python_version = existing_envs[conda_env_name]
    
    elif env_choice == "install":
        # Install new Python version
        install_method = questionary.select(
            "Install Python using:",
            choices=[
                "conda" if has_conda else None,
                "pyenv" if has_pyenv else None,
            ]
        ).ask()
        
        installable_versions = python_mgr.get_installable_versions()
        if installable_versions:
            version_to_install = questionary.select(
                "Select Python version to install:",
                choices=installable_versions[:10]  # Show top 10
            ).ask()
            
            clean_version = version_to_install.split(" ")[0]
            
            if python_mgr.install_python_version(clean_version, install_method):
                python_version = clean_version
                console.print(f"✅ Python {clean_version} installed successfully")
            else:
                console.print("❌ Installation failed, using system Python")
                python_version = python_mgr.get_system_version()
    
    else:
        # Regular venv with version selection
        if not python_version:
            available_versions = python_mgr.get_available_versions()
            if available_versions:
                python_version = questionary.select(
                    "🐍 Choose Python version:",
                    choices=available_versions,
                    default=python_mgr.get_default_version()
                ).ask()
            else:
                python_version = python_mgr.get_system_version()
                console.print(f"Using system Python version: {python_version}")
    
    return python_version, use_conda, conda_env_name
