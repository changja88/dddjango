"""english_address_note 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class EnglishAddressNote:
    value: str
