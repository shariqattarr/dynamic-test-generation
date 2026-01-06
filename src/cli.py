import subprocess
import sys
from pathlib import Path
import typer
from rich.console import Console
from src.loader import load_config
from src.generator import generate_tests

app = typer.Typer(help="Generate and run smoke tests from API definitions")
console = Console()

DEFAULT_CONFIG = """base_url: https://api.example.com
tests:
  - name: Get Users
    path: /users
    method: GET
    expect_status: 200
    expect_body_schema:
      id: "int"
      name: "str"

  - name: Get Single User
    path: /users/1
    method: GET
    expect_status: 200
    expect_body_schema:
      id: "int"
      name: "str"
      email: "str"
"""


@app.command()
def init(
    path: str = typer.Option("smoke.yml", "--path", "-p", help="Path to create config")
):
    """Create a sample smoke.yml configuration file"""
    config_path = Path(path)
    
    if config_path.exists():
        console.print(f"[yellow]File already exists:[/yellow] {config_path}")
        raise typer.Exit(1)
    
    config_path.write_text(DEFAULT_CONFIG)
    console.print(f"[green]Created:[/green] {config_path}")


@app.command()
def generate(
    config: str = typer.Option("smoke.yml", "--config", "-c", help="Path to smoke.yml"),
    output: str = typer.Option("tests/test_smoke.py", "--output", "-o", help="Output test file"),
):
    """Generate test file from smoke.yml"""
    try:
        cfg = load_config(config)
    except (FileNotFoundError, ValueError) as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    
    out_path = generate_tests(cfg, output)
    console.print(f"[green]Generated:[/green] {out_path}")
    console.print(f"[dim]Tests: {len(cfg.tests)}[/dim]")


@app.command()
def run(
    config: str = typer.Option("smoke.yml", "--config", "-c", help="Path to smoke.yml"),
    output: str = typer.Option("tests/test_smoke.py", "--output", "-o", help="Output test file"),
):
    """Generate tests and run them with pytest"""
    try:
        cfg = load_config(config)
    except (FileNotFoundError, ValueError) as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    
    out_path = generate_tests(cfg, output)
    console.print(f"[green]Generated:[/green] {out_path}")
    console.print()
    
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-s", str(out_path.parent)],
        cwd=Path.cwd(),
    )
    raise typer.Exit(result.returncode)


if __name__ == "__main__":
    app()
