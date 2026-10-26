"""code_lock 값."""
from dataclasses import dataclass
from .generated_part import GeneratedPart


@dataclass(frozen=True)
class CodeLock:
    value: str
