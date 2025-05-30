import typer
from rich.console import Console

app = typer.Typer()
console = Console()

@app.command()
def list():
    """List available project templates."""
    console.print("Templates list - placeholder")
