from dataclasses import dataclass

@dataclass(frozen=True)
class Criterion:
    value: str
    exclude: bool = False