from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class UiLabState:
    """Immutable fixture identities and server-rendered revision markers."""

    @dataclass(frozen=True)
    class Panel:
        """One fixture's identity, display label and current render revision."""

        key: str
        label: str
        revision: str

    panels: tuple[UiLabState.Panel, ...]
