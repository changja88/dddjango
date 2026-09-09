from django.urls import URLPattern, path, re_path

from web.lab.ui_lab.view.ui_lab_view import ui_lab_view

app_name: str = "lab"

urlpatterns: list[URLPattern] = [
    path("lab/ui-lab/", ui_lab_view, name="ui_lab"),
    re_path(
        r"^lab/ui-lab/(?P<panel_key>a|b)/panel/$",
        ui_lab_view,
        {"fragment": "panel"},
        name="ui_lab_panel",
    ),
    re_path(
        r"^lab/ui-lab/(?P<panel_key>a|b)/preview-body/$",
        ui_lab_view,
        {"fragment": "preview_body"},
        name="ui_lab_preview_body",
    ),
    re_path(
        r"^lab/ui-lab/(?P<panel_key>a|b)/note/$",
        ui_lab_view,
        {"fragment": "note"},
        name="ui_lab_note",
    ),
]
