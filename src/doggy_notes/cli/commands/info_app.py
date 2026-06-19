import sys
import typer
import os
from typing import Optional
from dataclasses import fields
from importlib.metadata import metadata, version, PackageNotFoundError
from pathlib import Path

from doggy_notes.infra.paths import build_paths
from doggy_notes.cli.dependencies import get_dependencies

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
    

def info_app():
    
    Paths = build_paths()
    deps = get_dependencies()

    try:
        pkg = metadata(APP_NAME)
        pkg_version = version(APP_NAME)
    except PackageNotFoundError:
        deps.console.error("Package not installed correctly.")
        raise typer.Exit(code=1)

    urls = _get_project_urls(pkg)

    deps.console.write("Doggy Notes - Runtime Info\n", style="title")

    deps.console.write("Runtime", style="subtitle")
    deps.console.info(f"  Name:        {pkg['Name']}")
    deps.console.info(f"  Version:     {pkg_version}")
    deps.console.info(f"  Python req:  {pkg['Requires-Python']}")
    deps.console.info(f"  Python ver:  {sys.version.split()[0]}")
    deps.console.info(f"  Python exec: {sys.executable}")
    deps.console.info("")

    deps.console.write("Paths", style="subtitle")
    for field in fields(Paths):
        value = getattr(Paths, field.name)
        deps.console.write(f"  {field.name}:  {value} [{_status(value)}]", style="path")
    deps.console.info("")

    deps.console.write("Project", style="subtitle")
    deps.console.info(f"  Homepage:    {urls.get('Homepage', 'N/A')}")
    deps.console.info(f"  Repository:  {urls.get('Repository', 'N/A')}")
    deps.console.info(f"  Issues:      {urls.get('Issues', 'N/A')}")
    deps.console.info(f"  Docs:        {urls.get('Documentation', 'N/A')}")
    deps.console.info(f"  Changelog:   {urls.get('Changelog', 'N/A')}")
    deps.console.info("")

    deps.console.write("Dependencies", style="subtitle")
    requires = pkg.get_all("Requires-Dist") or []
    if requires:
        for dep in requires:
            deps.console.info(f"  - {dep}")
    else:
        deps.console.info("  None declared")