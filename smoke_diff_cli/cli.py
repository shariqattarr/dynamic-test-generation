import os
import subprocess
import sys
from pathlib import Path
import typer
from rich.console import Console

app = typer.Typer(help="Generate and run smoke tests from API definitions")
console = Console()

# verbose mode flag (set by callback)
VERBOSE = False

DEFAULT_CONFIG = """base_url: https://jsonplaceholder.typicode.com
timeout: 30

tests:
  - name: Get All Users
    path: /users
    method: GET
    expect_status: 200

  - name: Get Single User
    path: /users/1
    method: GET
    expect_status: 200
    expect_body_schema:
      id: "int"
      name: "str"
      email: "str"
"""


def _check_package_installed():
    """Make sure the package is installed, otherwise imports will fail"""
    try:
        import smoke_diff_cli
        return True
    except ImportError:
        return False


def _log(msg: str):
    """Print only if verbose mode is on"""
    if VERBOSE:
        console.print(f"[dim]{msg}[/dim]")


@app.callback()
def main(verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output")):
    """smoke-diff-cli: Generate and run smoke tests from API definitions"""
    global VERBOSE
    VERBOSE = verbose


@app.command()
def init(
    path: str = typer.Option("smoke.yml", "--path", "-p", help="Path to create config"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing file"),
):
    """Create a sample smoke.yml configuration file"""
    config_path = Path(path)
    
    if config_path.exists() and not force:
        console.print(f"[yellow]File already exists:[/yellow] {config_path}")
        console.print("[dim]Use --force to overwrite[/dim]")
        raise typer.Exit(1)
    
    config_path.write_text(DEFAULT_CONFIG)
    console.print(f"[green]✓ Created:[/green] {config_path}")
    console.print(f"[dim]Edit the file and run: smoke-diff run[/dim]")


@app.command()
def generate(
    config: str = typer.Option("smoke.yml", "--config", "-c", help="Path to smoke.yml"),
    output: str = typer.Option("tests/test_smoke.py", "--output", "-o", help="Output test file"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Print generated tests without writing"),
):
    """Generate test file from smoke.yml"""
    # lazy import so we get nice error if package not installed
    try:
        from smoke_diff_cli.loader import load_config
        from smoke_diff_cli.generator import generate_tests
    except ImportError as e:
        console.print(f"[red]Error:[/red] Package not installed properly. Run: pip install -e .")
        console.print(f"[dim]{e}[/dim]")
        raise typer.Exit(1)
    
    config_path = Path(config).resolve()
    _log(f"Loading config from: {config_path}")
    
    try:
        cfg = load_config(config_path)
    except (FileNotFoundError, ValueError) as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    
    _log(f"Found {len(cfg.tests)} tests")
    _log(f"Base URL: {cfg.base_url}")
    
    out_path, content = generate_tests(cfg, output, dry_run=dry_run)
    
    if dry_run:
        console.print("[yellow]Dry run - generated content:[/yellow]")
        console.print()
        console.print(content)
        return
    
    console.print(f"[green]✓ Generated:[/green] {out_path}")
    console.print(f"[dim]Tests: {len(cfg.tests)}[/dim]")


@app.command()
def run(
    config: str = typer.Option("smoke.yml", "--config", "-c", help="Path to smoke.yml"),
    output: str = typer.Option("tests/test_smoke.py", "--output", "-o", help="Output test file"),
):
    """Generate tests and run them with pytest"""
    # check package is installed first
    if not _check_package_installed():
        console.print("[red]Error:[/red] Package not installed. Run: pip install -e .")
        raise typer.Exit(1)
    
    try:
        from smoke_diff_cli.loader import load_config
        from smoke_diff_cli.generator import generate_tests
    except ImportError as e:
        console.print(f"[red]Error:[/red] Package not installed properly.")
        console.print(f"[dim]{e}[/dim]")
        raise typer.Exit(1)
    
    config_path = Path(config).resolve()
    _log(f"Loading config from: {config_path}")
    
    try:
        cfg = load_config(config_path)
    except (FileNotFoundError, ValueError) as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    
    out_path, _ = generate_tests(cfg, output)
    console.print(f"[green]✓ Generated:[/green] {out_path}")
    console.print(f"[dim]Running {len(cfg.tests)} tests...[/dim]")
    console.print()
    
    # set PYTHONPATH so pytest can find smoke_diff_cli package
    # this is the key fix - without this, imports fail in generated tests
    env = os.environ.copy()
    project_root = Path(__file__).parent.parent.resolve()
    existing_path = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = f"{project_root}:{existing_path}" if existing_path else str(project_root)
    
    _log(f"PYTHONPATH={env['PYTHONPATH']}")
    
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-s", "-v", str(out_path)],
        cwd=project_root,
        env=env,
    )
    
    if result.returncode == 0:
        console.print()
        console.print("[green]✓ All tests passed![/green]")
    else:
        console.print()
        console.print("[red]✗ Some tests failed[/red]")
    
    raise typer.Exit(result.returncode)


if __name__ == "__main__":
    app()
