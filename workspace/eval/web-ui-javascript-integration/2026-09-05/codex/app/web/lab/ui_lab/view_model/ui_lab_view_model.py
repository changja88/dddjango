from uuid import uuid4

from web.lab.ui_lab.state.ui_lab_state import UiLabState


class UiLabViewModel:
    """Assemble request-local display fixtures without persistent state."""

    def build(self) -> UiLabState:
        """Return both fixtures in their initial reading order."""
        return UiLabState(panels=(self.build_panel("a"), self.build_panel("b")))

    def build_panel(self, panel_key: str) -> UiLabState.Panel:
        """Create a fresh revision for a route-validated fixture key."""
        return UiLabState.Panel(
            key=panel_key,
            label=f"Panel {panel_key.upper()}",
            revision=uuid4().hex,
        )
