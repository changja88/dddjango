"""setting_theme 값."""
from dataclasses import dataclass


@dataclass(frozen=True)
class SettingTheme:
    value: str
