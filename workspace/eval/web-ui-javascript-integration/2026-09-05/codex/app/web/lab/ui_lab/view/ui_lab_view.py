from typing import Literal

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET

from web.lab.ui_lab.state.ui_lab_state import UiLabState
from web.lab.ui_lab.view_model.ui_lab_view_model import UiLabViewModel


@never_cache
@require_GET
def ui_lab_view(
    request: HttpRequest,
    panel_key: str = "",
    fragment: Literal["panel", "preview_body", "note"] | None = None,
) -> HttpResponse:
    """Render the page or a fixed, route-selected fixture fragment."""
    view_model: UiLabViewModel = UiLabViewModel()
    if fragment is None:
        state: UiLabState = view_model.build()
        return render(request, "lab/ui_lab/view/ui_lab.html", {"state": state})
    templates: dict[str, str] = {
        "panel": "lab/ui_lab/section/ui_lab_panel.html",
        "preview_body": "lab/ui_lab/section/ui_lab_preview_body.html",
        "note": "lab/ui_lab/section/ui_lab_note.html",
    }
    panel: UiLabState.Panel = view_model.build_panel(panel_key)
    return render(request, templates[fragment], {"state": panel})
