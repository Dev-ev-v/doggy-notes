import sys
import typer
import os
from typing import Optional
from dataclasses import fields
from importlib.metadata import metadata, version, PackageNotFoundError
from pathlib import Path

from doggy_notes.infra.paths import build_paths
from doggy_notes.cli.console import Console

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

def _show_path(console: Console, path: str, Paths) -> None:
    field_map = {f.name: getattr(Paths, f.name) for f in fields(Paths)}

    parts = Path(path).parts
    root_name = parts[0]

    if root_name not in field_map:
        console.write(f"{root_name!r} not found. Available: {', '.join(field_map)}")
        return

    value = Path(field_map[root_name]).joinpath(*parts[1:])

    if not value.exists():
        console.write(f"{value} (not found)")
        return

    console.info(f"Path: {value}")

    if value.is_dir():
        children = list(value.iterdir())
        if not children:
            console.write("No children found")
            return
        console.info(f"Children of {path}:")
        console.write(path)
        for child in sorted(children):
            console.write(f"  |  {child.name}")
            if child.is_dir():
                for grandchild in sorted(child.iterdir()):
                    console.write(f"    |  {grandchild.name}")

    elif value.is_file():
        console.info(f"Reading {path}")
        console.read(value.read_text())

def info(
    path: Optional[str] = typer.Option(
    	None,
        "--path",
        help="Search a path in doggy-notes",
    ),
):
    """[bold cyan]Show detailed information about the installation and environment[/bold cyan]"""
    
    console = Console()
    
    Paths = build_paths()

    try:
        if path:
        	_show_path(console, path, Paths)
        	return
        pkg = metadata(APP_NAME)
        pkg_version = version(APP_NAME)
    except PackageNotFoundError:
        typer.secho("Package not installed correctly.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    urls = _get_project_urls(pkg)

    typer.secho("Doggy Notes - Runtime Info\n", bold=True)

    typer.echo("Runtime")
    typer.echo(f"  Name:        {pkg['Name']}")
    typer.echo(f"  Version:     {pkg_version}")
    typer.echo(f"  Python req:  {pkg['Requires-Python']}")
    typer.echo(f"  Python ver:  {sys.version.split()[0]}")
    typer.echo(f"  Python exec: {sys.executable}")
    typer.echo()

    typer.echo("Paths")
    for field in fields(Paths):
        value = getattr(Paths, field.name)
        typer.echo(f"  {field.name}:  {value} [{_status(value)}]")
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