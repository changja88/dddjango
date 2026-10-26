"""code_mark 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class CodeMark:
    value: str
