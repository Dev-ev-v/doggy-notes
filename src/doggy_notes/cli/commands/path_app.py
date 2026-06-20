import typer
from pathlib import Path
from dataclasses import fields

from doggy_notes.infra.paths import build_paths
from doggy_notes.domain.entities.node import build_tree
from doggy_notes.cli.dependencies import get_dependencies
from doggy_notes.domain.exceptions.note_errors import SearchFilterError


def path_app(
    path: str = typer.Argument(
        None,
        help="Path to explore (e.g. 'notes_dir' or 'notes_dir/subfolder')"
    ),
    show_size: bool = typer.Option(
        False,
        "--size",
        help="Show file/directory sizes"
    ),
):
    deps = get_dependencies()
    paths = build_paths()

    try:
        if path:
            _handle_single_path(path, paths, show_size, deps)
        else:
            _handle_all_dirs(paths, show_size, deps)
    except SearchFilterError as e:
        deps.console.error(deps.error_presenter.format(e))


def _resolve_path(path: str, paths, deps) -> Path | None:
    field_map = {f.name: getattr(paths, f.name) for f in fields(paths)}
    parts = Path(path).parts
    root_name = parts[0]

    if root_name not in field_map:
        available = ", ".join(field_map)
        deps.console.error(f"{root_name!r} not found. Available: {available}")
        return None

    resolved = Path(field_map[root_name]).joinpath(*parts[1:])

    if not resolved.exists():
        raise SearchFilterError(f"Path does not exist: {resolved}")

    return resolved


def _handle_all_dirs(paths, show_size, deps):
    dir_fields = [f.name for f in fields(paths) if f.name.endswith("_dir")]

    for dir_name in dir_fields:
        resolved = _resolve_path(dir_name, paths, deps)
        if resolved is None:
            continue

        deps.console.write("")
        _display_dir(resolved, label=dir_name, show_size=show_size, deps=deps)


def _handle_single_path(path: str, paths, show_size, deps):
    resolved = _resolve_path(path, paths, deps)
    if resolved is None:
        return

    deps.console.write(f"Path: {resolved}", style="path")

    if resolved.is_dir():
        _display_dir(resolved, label=path, show_size=show_size, deps=deps)
    elif resolved.is_file():
        _display_file(resolved, show_size=show_size, deps=deps)


def _display_dir(resolved: Path, label: str, show_size: bool, deps):
    children = list(resolved.iterdir())

    if not children:
        deps.console.info(f"{label}: (empty)")
        return

    deps.console.info(f"Contents of {label}:")
    node = build_tree(resolved)
    rich_tree = deps.console.build_rich_tree(node)
    deps.console.write(rich_tree)

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