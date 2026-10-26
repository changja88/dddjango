"""code_seal 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class CodeSeal:
    value: str
