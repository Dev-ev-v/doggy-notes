import os
import subprocess
import tempfile


class EditorService:

    @staticmethod
    def open_editor(initial_text: str = "") -> str:
        editor = (
            os.environ.get("VISUAL")
            or os.environ.get("EDITOR")
            or ("notepad" if os.name == "nt" else "nano")
        )

        with tempfile.NamedTemporaryFile(
            suffix=".txt",
            mode="w+",
            delete=False,
            encoding="utf-8",
        ) as temp_file:
            temp_file.write(initial_text)
            temp_file.flush()
            temp_path = temp_file.name

        try:
            subprocess.run([editor, temp_path], check=True)

            with open(temp_path, "r", encoding="utf-8") as file:
                edited_text = file.read()
        finally:
            os.unlink(temp_path)

        return edited_text
