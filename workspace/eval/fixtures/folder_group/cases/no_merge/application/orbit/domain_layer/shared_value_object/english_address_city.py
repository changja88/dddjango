"""english_address_city 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class EnglishAddressCity:
    value: str
