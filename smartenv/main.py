import typer
from rich.console import Console
from rich.panel import Panel
from typing import Optional
from .commands import create, init, templates, package

app = typer.Typer(
    name="inity",
    help="🚀 Intelligent Python project environment setup tool by Strucureo",
    add_completion=False
)

console = Console()

# Add commands
app.add_typer(create.app, name="create", help="Create a new Python project")
app.add_typer(templates.app, name="templates", help="Manage project templates")
app.add_typer(package.app, name="package", help="Package management (install, search, update)")
app.command()(init.init_project)

@app.callback()
def main():
    """Inity - Setup Python projects with ease!"""
    pass

@app.command()
def version():
    """Show version information."""
    from . import __version__, __author__, __company__
    console.print(Panel(
        f"[bold blue]Inity[/bold blue] v{__version__}\n"
        "🐍 Python Project Environment Setup Tool\n\n"
        f"[dim]Developed by {__author__} at {__company__}[/dim]",
        title="Version Info"
    ))

if __name__ == "__main__":
    app()
