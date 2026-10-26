"""english_address_line 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class EnglishAddressLine:
    value: str
