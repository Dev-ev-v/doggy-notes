from math import ceil

from rich.console import Console as RichConsole
from rich.columns import Columns
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.tree import Tree
from rich.theme import Theme
from rich.box import ROUNDED
from rich.align import Align

from doggy_notes.domain.entities.node import Node

custom_theme = Theme({
    "warning":  "bold yellow3",
    "error":    "bold red1",
    "success":  "bold green3",
    "path":     "dark_orange",
    "info":     "light_cyan1",
    "title":  "bold gray100",
    "subtitle":  "white",
    "tag":      "bold deep_sky_blue1",
    "id":       "bold magenta",
    "date": "blue",
    "file":  "yellow4",
    "directory": "yellow2",
})


class Console:
    def __init__(
        self,
        console: RichConsole | None = None,
    ):
        self.console = console or RichConsole(
            theme=custom_theme
        )
        self.e_console = RichConsole(
            theme=custom_theme,
            stderr=True,
        )

    # =========================
    # Base
    # =========================

    def write(self, *content, **kwargs):
        self.console.print(*content, **kwargs)

    
    def write_e(self, *content, **kwargs):
        self.e_console.print(*content, **kwargs)

    # =========================
    # Status Messages
    # =========================

    def success(self, text: str):
        self._status("✓", text, "success")

    
    def error(self, text: str):
        self._status("✗", text, "error", stderr=True)

    
    def warning(self, text: str):
        self._status("!", text, "warning")
        
    
    def info(self, text: str):
    	self._status(text=text, style="info")

    
    def _status(
        self,
        label: str = None,
        text: str = None,
        style: str = None,
        stderr: bool = False,
    ):
        if label:
        	message = f"[bold][{label}][/bold] {text}"
        else:
        	message=text
        	
        if stderr:
            self.write_e(message, style=style)
        else:
            self.write(message, style=style)

    # =========================
    # Panels
    # =========================

    def panel(
        self,
        text: str,
        title: str | None = None,
    ):
        self.write(
            Panel(
                text,
                title=title,
                border_style="bright_blue",
                box=ROUNDED,
            )
        )

    
    def read(self, text: Text, title: str | None = None):
        content = Panel(
            text,
            title=title,
            border_style="bright_blue",
            box=ROUNDED,
        )
        with self.console.pager(styles=True):
            self.console.print(content)
            
    
    def build_rich_tree(self, node: Node) -> Tree:
    	tree = Tree(node.path.name)
    	
    	def add_children(branch, current):
    	    for child in current.children:
    	        child_branch = branch.add(child.path.name)
    	        add_children(child_branch, child)
    	
    	add_children(tree, node)    	    
    	return tree
    	

    # =========================
    # Tables
    # =========================

    def list_notes(
        self,
        items: list[str] | None = None,
        title: str = "Notes",
        groups: dict[str, list[str]] | None = None,
        filters: dict[str, any] | None = None,
        tables_per_row: int = 1,
    ):
     
        if groups:
            items_to_show = [item for group in groups.values() for item in group]
        else:
            items_to_show = items or []

        if not items_to_show:
            self.warning("No notes found.")
            return

        if groups:
            rendered_tables = []
            for group_name, group_items in groups.items():
                filtered_items = self._apply_filters(group_items, filters)
                if filtered_items:
                    table = self._create_table(
                        filtered_items,
                        title=f"Tag: {group_name}",
                    )
                    rendered_tables.append(table)

            if rendered_tables:
                columns = Columns(rendered_tables, equal=True, expand=False)
                self.write("")
                self.write(Align.center(columns))
                self.write("")
            return

        filtered_items = self._apply_filters(items_to_show, filters)
        if not filtered_items:
            self.warning("No notes match the filters.")
            return

        items_per_table = ceil(len(filtered_items) / tables_per_row)
        tables = []

        for start in range(0, len(filtered_items), items_per_table):
            chunk = filtered_items[start:start + items_per_table]
            table = self._create_table(chunk, title=title, start_index=start + 1)
            tables.append(table)

        columns = Columns(tables, equal=True, expand=False)
        self.write("")
        self.write(Align.center(columns))
        self.write("")

    
    def _create_table(self, items: list[str], title: str, start_index: int = 1):
        table = Table(
            title=title,
            expand=True,
            box=ROUNDED,
            border_style="bright_blue",
            header_style="bold magenta",
            row_styles=["none", "dim"],
        )
        table.add_column("#", justify="right", style="cyan", width=4)
        table.add_column("Item", style="white", overflow="fold")

        for index, item in enumerate(items, start=start_index):
            table.add_row(str(index), item)

        return table

    
    def _apply_filters(self, items: list[str], filters: dict | None) -> list[str]:
        if not filters:
            return items
            
        if "limit" in filters:
            return items[:filters["limit"]]

        return items

    # =========================
    # Input
    # =========================

    
    def confirm(self, text: str) -> bool:
        self.warning(text)
        answer = input(
            "[y/n]: "
        ).strip().lower()
        return answer in {
            "y",
            "yes",
        }