"""term_c 값."""
from dataclasses import dataclass
from django.db import models


@dataclass(frozen=True)
class TermC:
    value: str
