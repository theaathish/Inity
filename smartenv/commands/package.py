import typer
import questionary
import os
import subprocess
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from pathlib import Path
from typing import Optional, List, Dict
from ..utils.package_manager import PackageManager
from ..utils.package_search import PackageSearcher

app = typer.Typer()
console = Console()

@app.command()
def search(
    query: str = typer.Argument(..., help="Package name or keyword to search"),
    limit: int = typer.Option(10, "--limit", "-l", help="Number of results to show"),
    source: str = typer.Option("pypi", "--source", "-s", help="Package source (pypi, conda)")
):
    """Search for packages in PyPI or other sources."""
    searcher = PackageSearcher()
    
    console.print(f"🔍 Searching for '{query}' in {source}...")
    
    if source.lower() == "pypi":
        results = searcher.search_packages_realtime(query, limit)
    else:
        console.print(f"[yellow]Source '{source}' not yet supported[/yellow]")
        return
    
    if not results:
        console.print(f"[yellow]No packages found for '{query}'[/yellow]")
        return
    
    # Display results
    table = Table(title=f"📦 Search Results for '{query}'")
    table.add_column("Package", style="cyan", min_width=15)
    table.add_column("Version", style="green", width=12)
    table.add_column("Description", style="white")
    table.add_column("Author", style="yellow", width=15)
    
    for pkg in results:
        description = pkg.get("description", "No description")[:60] + "..."
        author = pkg.get("author", "Unknown")[:12] + "..."
        table.add_row(pkg["name"], pkg["version"], description, author)
    
    console.print(table)

@app.command()
def install(
    packages: List[str] = typer.Argument(..., help="Package names or git URLs to install"),
    global_install: bool = typer.Option(False, "--global", "-g", help="Install globally"),
    environment: Optional[str] = typer.Option(None, "--env", "-e", help="Target environment"),
    from_git: bool = typer.Option(False, "--git", help="Install from git repository"),
    editable: bool = typer.Option(False, "--editable", help="Install in editable mode"),
    upgrade: bool = typer.Option(False, "--upgrade", "-U", help="Upgrade if already installed"),
    force: bool = typer.Option(False, "--force", help="Force installation"),
    interactive: bool = typer.Option(True, "--interactive/--no-interactive", help="Interactive mode")
):
    """Install packages with various options."""
    manager = PackageManager()
    
    if interactive:
        packages, install_options = _interactive_package_install(manager, packages)
    else:
        install_options = {
            "global": global_install,
            "environment": environment,
            "from_git": from_git,
            "editable": editable,
            "upgrade": upgrade,
            "force": force
        }
    
    if not packages:
        console.print("[yellow]No packages specified[/yellow]")
        return
    
    # Install packages
    success = manager.install_packages(packages, **install_options)
    
    if success:
        console.print("✅ [green]All packages installed successfully[/green]")
    else:
        console.print("❌ [red]Some packages failed to install[/red]")

@app.command()
def uninstall(
    packages: List[str] = typer.Argument(..., help="Package names to uninstall"),
    global_uninstall: bool = typer.Option(False, "--global", "-g", help="Uninstall globally"),
    environment: Optional[str] = typer.Option(None, "--env", "-e", help="Target environment"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation")
):
    """Uninstall packages."""
    manager = PackageManager()
    
    if not yes:
        confirm = questionary.confirm(
            f"Are you sure you want to uninstall {len(packages)} packages?"
        ).ask()
        if not confirm:
            console.print("Cancelled")
            return
    
    success = manager.uninstall_packages(
        packages, 
        global_scope=global_uninstall,
        environment=environment
    )
    
    if success:
        console.print("✅ [green]Packages uninstalled successfully[/green]")
    else:
        console.print("❌ [red]Some packages failed to uninstall[/red]")

@app.command()
def list(
    environment: Optional[str] = typer.Option(None, "--env", "-e", help="List packages in specific environment"),
    global_packages: bool = typer.Option(False, "--global", "-g", help="List global packages"),
    outdated: bool = typer.Option(False, "--outdated", help="Show outdated packages"),
    format: str = typer.Option("table", "--format", help="Output format (table, json)")
):
    """List installed packages."""
    manager = PackageManager()
    
    if global_packages:
        packages = manager.list_global_packages(outdated=outdated)
        title = "Global Packages"
    elif environment:
        packages = manager.list_environment_packages(environment, outdated=outdated)
        title = f"Packages in '{environment}'"
    else:
        packages = manager.list_current_packages(outdated=outdated)
        title = "Current Environment Packages"
    
    if format == "json":
        import json
        console.print(json.dumps(packages, indent=2))
        return
    
    # Display as table
    table = Table(title=title)
    table.add_column("Package", style="cyan")
    table.add_column("Version", style="green")
    table.add_column("Latest", style="yellow") if outdated else None
    table.add_column("Location", style="dim")
    
    for pkg in packages:
        if outdated:
            table.add_row(
                pkg["name"], 
                pkg["version"], 
                pkg.get("latest", "unknown"),
                pkg.get("location", "")
            )
        else:
            table.add_row(
                pkg["name"], 
                pkg["version"], 
                pkg.get("location", "")
            )
    
    console.print(table)

@app.command()
def update(
    packages: Optional[List[str]] = typer.Argument(None, help="Specific packages to update"),
    all_packages: bool = typer.Option(False, "--all", "-a", help="Update all packages"),
    environment: Optional[str] = typer.Option(None, "--env", "-e", help="Target environment"),
    global_update: bool = typer.Option(False, "--global", "-g", help="Update global packages"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be updated")
):
    """Update packages to their latest versions."""
    manager = PackageManager()
    
    if all_packages:
        if global_update:
            outdated = manager.list_global_packages(outdated=True)
        elif environment:
            outdated = manager.list_environment_packages(environment, outdated=True)
        else:
            outdated = manager.list_current_packages(outdated=True)
        
        packages = [pkg["name"] for pkg in outdated]
    
    if not packages:
        console.print("[yellow]No packages specified for update[/yellow]")
        return
    
    if dry_run:
        console.print("📋 [bold]Packages that would be updated:[/bold]")
        for pkg in packages:
            console.print(f"  - {pkg}")
        return
    
    success = manager.update_packages(
        packages,
        global_scope=global_update,
        environment=environment
    )
    
    if success:
        console.print("✅ [green]Packages updated successfully[/green]")
    else:
        console.print("❌ [red]Some packages failed to update[/red]")

@app.command() 
def info(
    package: str = typer.Argument(..., help="Package name to get info about"),
    environment: Optional[str] = typer.Option(None, "--env", "-e", help="Check in specific environment")
):
    """Get detailed information about a package."""
    manager = PackageManager()
    searcher = PackageSearcher()
    
    # Get local package info
    local_info = manager.get_package_info(package, environment)
    
    # Get PyPI info
    pypi_info = searcher.get_package_info_detailed(package)
    
    console.print(f"\n📦 [bold cyan]{package}[/bold cyan]")
    
    if local_info:
        console.print(f"📍 [green]Installed Version:[/green] {local_info['version']}")
        console.print(f"📂 [green]Location:[/green] {local_info.get('location', 'Unknown')}")
    else:
        console.print("📍 [red]Not installed locally[/red]")
    
    if pypi_info:
        console.print(f"🌐 [yellow]Latest Version:[/yellow] {pypi_info['version']}")
        console.print(f"📝 [white]Description:[/white] {pypi_info['description']}")
        console.print(f"👤 [white]Author:[/white] {pypi_info['author']}")
        console.print(f"📄 [white]License:[/white] {pypi_info['license']}")
        
        if pypi_info.get('home_page'):
            console.print(f"🌐 [white]Homepage:[/white] {pypi_info['home_page']}")
        
        if pypi_info.get('requires_dist'):
            console.print(f"📦 [white]Dependencies:[/white] {len(pypi_info['requires_dist'])} packages")

def _interactive_package_install(manager: PackageManager, initial_packages: List[str]) -> tuple:
    """Interactive package installation with advanced options."""
    
    packages = list(initial_packages) if initial_packages else []
    
    # Package selection/addition
    while True:
        if packages:
            console.print(f"\n📦 [green]Current packages:[/green] {', '.join(packages)}")
        
        action = questionary.select(
            "What would you like to do?",
            choices=[
                "Add package by name",
                "Add package from Git repository", 
                "Search and add packages",
                "Remove a package from list",
                "Continue with installation" if packages else None,
                "Cancel"
            ]
        ).ask()
        
        if action == "Add package by name":
            pkg_name = questionary.text("Package name (with optional version):").ask()
            if pkg_name:
                packages.append(pkg_name)
        
        elif action == "Add package from Git repository":
            git_url = questionary.text(
                "Git repository URL:",
                instruction="(e.g., https://github.com/user/repo.git)"
            ).ask()
            
            if git_url:
                # Validate git URL format
                if not any(git_url.startswith(prefix) for prefix in ['http', 'git@', 'ssh://']):
                    console.print("[yellow]Invalid git URL format[/yellow]")
                    continue
                
                editable = questionary.confirm("Install in editable mode?", default=False).ask()
                
                git_package = f"git+{git_url}"
                if editable:
                    git_package = f"-e {git_package}"
                
                packages.append(git_package)
        
        elif action == "Search and add packages":
            searcher = PackageSearcher()
            query = questionary.text("Search packages:").ask()
            if query:
                results = searcher.search_packages_realtime(query, 10)
                if results:
                    choices = [
                        questionary.Choice(f"{pkg['name']} - {pkg['description'][:50]}...", value=pkg['name'])
                        for pkg in results
                    ]
                    selected = questionary.checkbox("Select packages:", choices=choices).ask()
                    packages.extend(selected)
        
        elif action == "Remove a package from list":
            if packages:
                to_remove = questionary.select("Remove package:", choices=packages).ask()
                packages.remove(to_remove)
        
        elif action == "Continue with installation":
            break
        
        elif action == "Cancel":
            return [], {}
    
    if not packages:
        return [], {}
    
    # Installation options
    console.print("\n⚙️ [bold]Installation Options[/bold]")
    
    # Environment selection
    environments = manager.get_available_environments()
    env_choices = [
        "Current environment",
        "Global (system-wide)",
    ]
    
    if environments.get("conda"):
        env_choices.extend([f"Conda: {env}" for env in environments["conda"]])
    
    if environments.get("venv"):
        env_choices.extend([f"Venv: {env}" for env in environments["venv"]])
    
    target_env = questionary.select(
        "Installation target:",
        choices=env_choices,
        default="Current environment"
    ).ask()
    
    # Additional options
    options = questionary.checkbox(
        "Additional options:",
        choices=[
            questionary.Choice("Upgrade if already installed", value="upgrade"),
            questionary.Choice("Force reinstall", value="force"),
            questionary.Choice("Install with all extras", value="extras"),
        ]
    ).ask()
    
    # Parse options
    install_options = {
        "global": target_env == "Global (system-wide)",
        "environment": target_env.split(": ")[1] if ": " in target_env else None,
        "upgrade": "upgrade" in options,
        "force": "force" in options,
        "extras": "extras" in options,
        "from_git": any("git+" in pkg for pkg in packages),
        "editable": any(pkg.startswith("-e") for pkg in packages)
    }
    
    return packages, install_options
