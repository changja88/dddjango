"""ui_lab 화면의 표시 상태 — 템플릿이 아는 유일한 모양."""

from dataclasses import dataclass


@dataclass(frozen=True)
class UiLabNoteState:
    """미리보기 안에 있으나 자원 비종속인 독립 자식 노트의 표시 상태."""

    dom_id: str
    text: str
    revision_marker: str
    swap_enabled: bool
    swap_label: str


@dataclass(frozen=True)
class UiLabPasswordState:
    """비밀번호 필드 그룹의 표시 상태."""

    dom_id: str
    input_dom_id: str
    input_name: str
    label: str
    show_label: str
    hide_label: str
    autocomplete: str


@dataclass(frozen=True)
class UiLabPreviewState:
    """로컬 이미지 미리보기 그룹의 표시 상태."""

    dom_id: str
    input_dom_id: str
    input_name: str
    label: str
    clear_label: str
    empty_message: str
    error_message: str
    revision_marker: str
    child_swap_enabled: bool
    child_swap_label: str
    note: UiLabNoteState


@dataclass(frozen=True)
class UiLabPanelState:
    """패널 root(교체 단위)의 표시 상태."""

    dom_id: str
    heading: str
    revision_marker: str
    root_swap_enabled: bool
    root_swap_label: str
    password: UiLabPasswordState
    preview: UiLabPreviewState


@dataclass(frozen=True)
class UiLabState:
    """ui_lab 페이지 전체의 표시 상태."""

    page_title: str
    disclosure_summary: str
    disclosure_body: str
    panel_a: UiLabPanelState
    panel_b: UiLabPanelState
