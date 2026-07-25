from rich.text import Text
from doggy_notes.domain.exceptions.note_errors import (
    NoteEmptyStorageError,
    SearchFilterError,
    NoteNotFoundError,
    NoteValidationError,
)

class ErrorPresenter:

    @staticmethod
    def format(error) -> Text:
        text = Text()
        match error:

            case SearchFilterError():
                text.append(f"{error}:\n\n", style="underline")
                text.append("Filter: ", style="bold red")
                text.append(f"{error.filter}\n", style="green")
                text.append("Invalid values: ", style="bold red")

                if error.value == "ids":
                    style = "id"
                elif error.value == "tags":
                    style = "tag"
                else:
                    style = "white"
                text.append(str(error.value), style=style)

            case NoteNotFoundError():
                text.append(f"{error.message}\n")

                for key, value in error.filters.items():
                    text.append(f"\n{key}: ", style="bold red")

                    if key == "ids":
                        style = "id"
                    elif key == "tags":
                        style = "tag"
                    else:
                        style = "white"
                    text.append(", ".join(value), style=style)

            case NoteEmptyStorageError():
                text.append(str(error))

            case _:
                text.append(str(error))

        return text