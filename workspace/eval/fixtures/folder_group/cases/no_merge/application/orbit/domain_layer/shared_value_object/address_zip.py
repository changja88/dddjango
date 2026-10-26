"""address_zip 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class AddressZip:
    value: str
