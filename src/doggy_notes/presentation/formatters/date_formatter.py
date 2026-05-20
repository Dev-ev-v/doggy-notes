from datetime import datetime, timezone
from typing import Optional

class DateFormatter:

    @staticmethod
    def format(date_str: str, now: Optional[datetime] = None) -> str:
        try:
            date = datetime.fromisoformat(date_str)
        except ValueError as e:
            raise ValueError(f"Invalid date format: {date_str}") from e
        now = now or datetime.now(timezone.utc)
        if date.tzinfo is None:
        	date = date.replace(tzinfo=timezone.utc)
        if now.tzinfo is None:
       	 now = now.replace(tzinfo=timezone.utc)
        delta = now - date
        seconds = int(delta.total_seconds())
        if seconds < 0:
            return "In the future"
        if seconds < 3:
            return "Now"
        intervals = [
            ("y", 31536000),
            ("mo", 2592000),
            ("d", 86400),
            ("h", 3600),
            ("m", 60),
            ("s", 1),
        ]
        parts = []
        for suffix, unit_seconds in intervals:
            value = seconds // unit_seconds
            if value:
                seconds %= unit_seconds
                parts.append(f"{value}{suffix}")

            if len(parts) == 2:
                break
        return f"{' '.join(parts)} ago"