"""ui_lab 화면의 진입점 — VM 호출과 render만 한다."""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from web.lab.ui_lab.view_model.ui_lab_view_model import UiLabViewModel

PAGE_TEMPLATE: str = "lab/ui_lab/view/ui_lab.html"
PANEL_TEMPLATE: str = "lab/ui_lab/section/ui_lab_panel.html"
PREVIEW_TEMPLATE: str = "lab/ui_lab/section/ui_lab_preview.html"
NOTE_TEMPLATE: str = "lab/ui_lab/section/ui_lab_note.html"


def ui_lab_view(request: HttpRequest) -> HttpResponse:
    """ui_lab 페이지 전체를 렌더한다."""
    state = UiLabViewModel().build_state()
    return render(request, PAGE_TEMPLATE, {"state": state})


def ui_lab_panel_fragment(request: HttpRequest) -> HttpResponse:
    """패널 B root 교체용 fragment를 렌더한다."""
    panel = UiLabViewModel().build_panel_b_state()
    return render(request, PANEL_TEMPLATE, {"panel": panel})


def ui_lab_preview_fragment(request: HttpRequest) -> HttpResponse:
    """패널 A의 미리보기(종속 자식) 교체용 fragment를 렌더한다."""
    preview = UiLabViewModel().build_preview_a_state()
    return render(request, PREVIEW_TEMPLATE, {"preview": preview})


def ui_lab_note_fragment(request: HttpRequest) -> HttpResponse:
    """패널 A 미리보기 안 노트(독립 자식) 교체용 fragment를 렌더한다."""
    note = UiLabViewModel().build_note_a_state()
    return render(request, NOTE_TEMPLATE, {"note": note})
