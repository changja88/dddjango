"""english_address_zip 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class EnglishAddressZip:
    value: str
