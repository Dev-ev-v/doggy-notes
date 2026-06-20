from dataclasses import dataclass
from pathlib import Path

@dataclass
class Node:
    path: Path
    children: list["Node"]

def build_tree(path: Path) -> Node:
    children = []

    if path.is_dir():
        children = [
            build_tree(child)
            for child in sorted(path.iterdir())
        ]

    return Node(path, children)