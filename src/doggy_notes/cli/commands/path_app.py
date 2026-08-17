import json
import sys
from enum import Enum
from pathlib import Path
from typing import Optional

import typer

from doggy_notes.infra.paths import build_paths
from doggy_notes.domain.entities.node import build_tree
from doggy_notes.cli.dependencies import get_dependencies
from doggy_notes.infra.path_resolver import PathResolver, PathKeyError
from doggy_notes.domain.exceptions.note_errors import AppError


class OutputMode(str, Enum):
    human = "human"
    raw = "raw"
    json_ = "json"


def path_app(
    path: Optional[str] = typer.Argument(
        None, help="Path to explore (e.g. 'notes_dir' or 'notes_dir/subfolder')"
    ),
    show_size: bool = typer.Option(False, "--size", help="Show file/directory sizes (human mode only)"),
    raw: bool = typer.Option(False, "--raw", "-r", help="Print plain path, no decoration. Requires PATH."),
    as_json: bool = typer.Option(False, "--json", help="Output as JSON"),
    list_contents: bool = typer.Option(False, "--list", help="Include directory contents in JSON output (non-recursive)"),
):
    if raw and as_json:
        deps.console.write("--raw and --json are mutually exclusive", err=True)
        raise typer.Exit(1)
    if raw and not path:
        deps.console.write("--raw requires a PATH argument (e.g. doggy path exports_dir --raw)", err=True)
        raise typer.Exit(1)

    mode = OutputMode.raw if raw else OutputMode.json_ if as_json else OutputMode.human

    deps = get_dependencies()
    resolver = PathResolver(build_paths())

    try:
        if path:
            resolved = resolver.resolve(path)
            _emit_single(resolved, path, mode, show_size, list_contents, deps)
        else:
            _emit_all(resolver, mode, show_size, list_contents, deps)
    except (AppError, PathKeyError) as e:
        if mode is OutputMode.human:
            deps.console.error(deps.error_presenter.format(e))
        else:
            deps.console.write(str(e), err=True)
        raise typer.Exit(1)


def _emit_single(resolved: Path, label: str, mode: OutputMode, show_size: bool, list_contents: bool, deps):
    if mode is OutputMode.raw:
        deps.console.write(str(resolved))
        return

    if mode is OutputMode.json_:
        deps.console.write(json.dumps(_describe(resolved, label, show_size, list_contents)))
        return

    deps.console.write(f"Path: {resolved}", style="path")
    if resolved.is_dir():
        _display_dir(resolved, label=label, show_size=show_size, deps=deps)
    elif resolved.is_file():
        _display_file(resolved, show_size=show_size, deps=deps)


def _emit_all(resolver: PathResolver, mode: OutputMode, show_size: bool, list_contents: bool, deps):
    dirs = resolver.all_dirs()

    if mode is OutputMode.raw:
        for key, resolved in dirs.items():
            deps.console.write(f"{key}={resolved}", style="path")
        return

    if mode is OutputMode.json_:
        payload = {key: _describe(resolved, key, show_size, list_contents) for key, resolved in dirs.items()}
        deps.console.write(json.dumps(payload))
        return

    for key, resolved in dirs.items():
        deps.console.write("")
        deps.console.write(f"Path: {resolved}", style="path")
        _display_dir(resolved, label=key, show_size=show_size, deps=deps)


def _describe(resolved: Path, label: str, show_size: bool, list_contents: bool) -> dict:
    data = {
        "key": label,
        "path": str(resolved),
        "exists": resolved.exists(),
        "type": "dir" if resolved.is_dir() else "file" if resolved.is_file() else None,
    }
    if show_size and resolved.exists():
        data["size_bytes"] = (
            _calc_dir_size(resolved) if resolved.is_dir() else resolved.stat().st_size
        )
    if list_contents and resolved.is_dir():
        data["contents"] = [
            {"name": c.name, "type": "dir" if c.is_dir() else "file"}
            for c in sorted(resolved.iterdir())
        ]
    return data


def _display_dir(resolved: Path, label: str, show_size: bool, deps):
    children = list(resolved.iterdir())
    if not children:
        deps.console.info(f"Contents of {label}: (empty)")
        return
    deps.console.info(f"Contents of {label}:")
    node = build_tree(resolved)
    deps.console.write(deps.console.build_rich_tree(node))
    if show_size:
        size = _calc_dir_size(resolved)
        deps.console.info(f"Total size: {deps.file_presenter.bytes_to_size(size)}")


def _display_file(resolved: Path, show_size: bool, deps):
    deps.console.info(f"Reading: {resolved.name}")
    try:
        deps.console.read(resolved.read_text())
    except UnicodeDecodeError:
        size = deps.file_presenter.bytes_to_size(resolved.stat().st_size)
        deps.console.warning(f"Binary file — cannot display contents ({size})")
        return
    if show_size:
        size = deps.file_presenter.bytes_to_size(resolved.stat().st_size)
        deps.console.info(f"Size: {size}")


def _calc_dir_size(path: Path) -> int:
    return sum(f.stat().st_size for f in path.rglob("*") if f.is_file())