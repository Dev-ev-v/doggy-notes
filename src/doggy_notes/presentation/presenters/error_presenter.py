from rich.text import Text
from doggy_notes.domain.exceptions.note_errors import (
    AppError,
    ErrorCode,
    SearchFilterError,
    NoteNotFoundError,
    NoteEmptyStorageError,
)


class ErrorPresenter:

    @staticmethod
    def format(error: AppError) -> Text:
        text = Text()
        match error:

            case SearchFilterError():
                text.append("Filter: ", style="bold red")
                text.append(f"{error.context['filter']}\n", style="green")
                text.append("Invalid values: ", style="bold red")

                value = error.context["value"]
                if value == "ids":
                    style = "id"
                elif value == "tags":
                    style = "tag"
                else:
                    style = "white"
                text.append(str(value), style=style)

            case NoteNotFoundError():
                text.append(f"{error.message}\n")

                for key, value in error.context["filters"].items():
                    text.append(f"\n{key}: ", style="bold red")

                    if key == "ids":
                        style = "id"
                    elif key == "tags":
                        style = "tag"
                    else:
                        style = "white"
                    text.append(", ".join(value), style=style)

            case NoteEmptyStorageError():
                text.append(error.message)

            case _:
                text.append(str(error))

        return text