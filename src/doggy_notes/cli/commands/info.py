import typer
from importlib.metadata import metadata, version
from pathlib import Path

app = typer.Typer()

@app.command(help="Shows more information than --version or -v about the project")
def info():
    pkg = metadata("doggy-notes")
    
    config_path = Path.home() / ".config" / "doggy-notes" / "pyproject.toml"
	
    print("Name:", pkg["Name"])
    print("Python:", pkg["Requires-Python"])
    print("Version:", version("doggy-notes"))
    print("Config:", config_path)
    print("Repository:", pkg.get("Project-URL"))