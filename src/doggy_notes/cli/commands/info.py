import sys
import typer
from importlib.metadata import metadata, version, PackageNotFoundError
from pathlib import Path

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
    """Show detailed information about the installation and environment."""

    try:
        pkg = metadata(APP_NAME)
        pkg_version = version(APP_NAME)
    except PackageNotFoundError:
        typer.secho("Package not installed correctly.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    urls = _get_project_urls(pkg)

    config_dir = Path.home() / ".config" / APP_NAME
    config_file = config_dir / "config.toml"
    data_dir = Path.home() / f".local/share/{APP_NAME}"
    cache_dir = Path.home() / f".cache/{APP_NAME}"

    typer.secho("Doggy Notes - Environment Info\n", bold=True)

    typer.echo("Package")
    typer.echo(f"  Name:        {pkg['Name']}")
    typer.echo(f"  Version:     {pkg_version}")
    typer.echo(f"  Python req:  {pkg['Requires-Python']}")
    typer.echo(f"  Python exec: {sys.version.split()[0]}")
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