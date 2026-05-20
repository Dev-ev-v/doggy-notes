import sys
import typer
from importlib.metadata import metadata, version, PackageNotFoundError
from pathlib import Path
from doggy_notes.infra.paths import build_paths

APP_NAME = "doggy-notes"

def _get_project_urls(pkg):
    urls = {}
    for key, value in pkg.items():
        if key == "Project-URL":
            try:
                name, url = value.split(", ", 1)
                urls[name] = url
            except ValueError:
                continue
    return urls

def _status(path: Path) -> str:
    return "✓" if path.exists() else "✗"

def info():
    """[bold cyan]Show detailed information about the installation and environment[/bold cyan]"""

    try:
        pkg = metadata(APP_NAME)
        pkg_version = version(APP_NAME)
    except PackageNotFoundError:
        typer.secho("Package not installed correctly.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    urls = _get_project_urls(pkg)

    Paths = build_paths()    
    config_dir = Paths.config_dir
    config_file = Paths.config_file
    data_dir = Paths.data_dir
    cache_dir = Paths.cache_dir    

    typer.secho("Doggy Notes - Runtime Info\n", bold=True)

    typer.echo("Runtime")
    typer.echo(f"  Name:        {pkg['Name']}")
    typer.echo(f"  Version:     {pkg_version}")
    typer.echo(f"  Python req:  {pkg['Requires-Python']}")
    typer.echo(f"  Python ver:  {sys.version.split()[0]}")
    typer.echo(f"  Python exec: {sys.executable}")
    typer.echo()

    typer.echo("Paths")
    typer.echo(f"  Config dir:  {config_dir} [{_status(config_dir)}]")
    typer.echo(f"  Config file: {config_file} [{_status(config_file)}]")
    typer.echo(f"  Data dir:    {data_dir} [{_status(data_dir)}]")
    typer.echo(f"  Cache dir:   {cache_dir} [{_status(cache_dir)}]")
    typer.echo()

    typer.echo("Project")
    typer.echo(f"  Homepage:    {urls.get('Homepage', 'N/A')}")
    typer.echo(f"  Repository:  {urls.get('Repository', 'N/A')}")
    typer.echo(f"  Issues:      {urls.get('Issues', 'N/A')}")
    typer.echo(f"  Docs:        {urls.get('Documentation', 'N/A')}")
    typer.echo(f"  Changelog:   {urls.get('Changelog', 'N/A')}")
    typer.echo()

    typer.echo("Dependencies")
    requires = pkg.get_all("Requires-Dist") or []
    if requires:
        for dep in requires:
            typer.echo(f"  - {dep}")
    else:
        typer.echo("  None declared")