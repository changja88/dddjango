"""void_a 값."""
from dataclasses import dataclass
from django.db import models


@dataclass(frozen=True)
class VoidA:
    value: str
