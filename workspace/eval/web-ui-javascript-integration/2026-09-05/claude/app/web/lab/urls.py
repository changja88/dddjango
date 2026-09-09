"""lab 영역의 path·name 리터럴 단일 출처."""

from django.urls import URLPattern, path

from web.lab.ui_lab.view.ui_lab_view import (
    ui_lab_note_fragment,
    ui_lab_panel_fragment,
    ui_lab_preview_fragment,
    ui_lab_view,
)

app_name = "lab"

urlpatterns: list[URLPattern] = [
    path("ui-lab/", ui_lab_view, name="ui_lab"),
    path("ui-lab/fragment/panel/", ui_lab_panel_fragment, name="ui_lab_panel"),
    path("ui-lab/fragment/preview/", ui_lab_preview_fragment, name="ui_lab_preview"),
    path("ui-lab/fragment/note/", ui_lab_note_fragment, name="ui_lab_note"),
]
