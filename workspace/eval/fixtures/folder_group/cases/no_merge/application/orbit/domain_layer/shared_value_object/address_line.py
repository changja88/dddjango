"""address_line 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class AddressLine:
    value: str
