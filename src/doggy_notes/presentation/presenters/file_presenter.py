class FilePresenter:

    @staticmethod
    def bytes_to_size(size: int) -> str:
        for unit in ("B", "KB", "MB", "GB"):
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    @staticmethod
    def size_to_bytes(size_str: str) -> int:
        units = {"B": 1, "KB": 1024, "MB": 1024**2, "GB": 1024**3, "TB": 1024**4}
        number, unit = size_str.strip().split()

        return int(float(number) * units[unit])