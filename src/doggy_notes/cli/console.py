from math import ceil

from rich.console import Console as RichConsole
from rich.columns import Columns
from rich.panel import Panel
from rich.table import Table
from rich.theme import Theme
from rich.box import ROUNDED


custom_theme = Theme({
    "info": "dim cyan",
    "warning": "bold yellow",
    "error": "bold red",
    "success": "bold green",
    "title": "bold bright_blue",
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
        self._status("OK", text, "success")

    def error(self, text: str):
        self._status("ERROR", text, "error", stderr=True)

    def warning(self, text: str):
        self._status("WARNING", text, "warning")

    def info(self, text: str):
        self._status("INFO", text, "info")

    def _status(
        self,
        label: str,
        text: str,
        style: str,
        stderr: bool = False,
    ):
        message = f"[bold][{label}][/bold] {text}"

        if stderr:
            self.write_e(message, style=style)
        else:
            self.write(message, style=style)

    # =========================
    # Panels
    # =========================

    def note(
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

    # =========================
    # Tables
    # =========================

    def list_notes(
        self,
        title: str,
        items: list[str],
        tables_per_row: int = 1,
    ):
        if not items:
            self.warning("No notes found.")
            return

        items_per_table = ceil(
            len(items) / tables_per_row
        )

        tables = []

        for start in range(
            0,
            len(items),
            items_per_table,
        ):
            chunk = items[start:start + items_per_table]

            table = Table(
                title=title,
                expand=True,
                box=ROUNDED,
                border_style="bright_blue",
                header_style="bold magenta",
                row_styles=["none", "dim"],
            )

            table.add_column(
                "#",
                justify="right",
                style="cyan",
                width=4,
            )

            table.add_column(
                "Item",
                style="white",
                overflow="fold",
            )

            for index, item in enumerate(
                chunk,
                start=start + 1,
            ):
                table.add_row(str(index), item)

            tables.append(table)

        self.write(
        	"\n",
            Columns(
                tables,
                equal=True,
                expand=True,
            )
        )

    # =========================
    # Input
    # =========================

    def confirm(self, text: str) -> bool:
        answer = input(
            f"{text} [y/n]: "
        ).strip().lower()

        return answer in {
            "y",
            "yes",
        }