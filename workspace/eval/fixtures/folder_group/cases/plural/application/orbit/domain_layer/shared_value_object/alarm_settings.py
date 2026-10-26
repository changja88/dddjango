"""alarm_settings 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class AlarmSettings:
    value: str
