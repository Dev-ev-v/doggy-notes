from rich.text import Text
from dataclasses import dataclass
from doggy_notes.presentation.formatters.date_formatter import DateFormatter

from doggy_notes.domain.entities.note import Note


class NotePresenter:

    @staticmethod
    def separate(width: int=115, color: str="Yellow", format: str="—"):
        text = Text()
        text.append("\n\n")
        text.append(format * width, style=color)
        text.append("\n\n")
        return text


    @staticmethod
    def format_detail(note: Note) -> Text:
        text = Text()
        text.append("ID: ", style="dim")
        text.append(note.id, style="id")
        text.append("\n")
        text.append("Title: ", style="dim")
        text.append(note.title)
        text.append("\n")
        text.append("Created: ", style="dim")
        text.append(str(note.date), style="date")
        text.append("\n")
        text.append("Tags: ", style="dim")
        tags = ", ".join(note.tags) if note.tags else "No tags"
        text.append(tags, style="tags")
        text.append("\n" * 2)
        text.append("Description: ", style="dim")
        text.append(note.description or "No description")
        text.append("\n" * 2)
        text.append("Content: ", style="dim")
        text.append(note.content)

        return text


    @staticmethod
    def format_values(note, fields):
        text = Text()
        
        text.append(NotePresenter._resume_note(note))
        text.append("\n\n")
        
        for field in fields:
            value = getattr(note, field, None)

            if isinstance(value, list):
                value = ", ".join(value)

            if isinstance(value, str):
                value = value.strip()

            if not value:
                value = f"No {field}"

            text.append(f"{field.capitalize()}: ", style="dim")
            text.append(str(value))
            text.append("\n")

        return text


    @staticmethod
    def _resume_note(note: Note) -> Text:
        short_id = note.id[:8]
        title = note.title or "Untitled"
        date = DateFormatter.format(str(note.date))
        text = Text()

        text.append("[", style="dim")
        text.append(short_id, style="id")
        text.append("] ", style="dim")
        text.append(title)
        text.append(" (", style="dim")
        text.append(date, style="date")
        text.append(")", style="dim")

        return text