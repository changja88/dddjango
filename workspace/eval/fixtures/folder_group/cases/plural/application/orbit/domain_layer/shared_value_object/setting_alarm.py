"""setting_alarm 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class SettingAlarm:
    value: str
