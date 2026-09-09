"""ui_lab 화면의 표시 판정·조립 — revision marker와 패널별 교체 제어 판정의 유일한 자리."""

from uuid import uuid4

from web.lab.ui_lab.state.ui_lab_state import (
    UiLabNoteState,
    UiLabPanelState,
    UiLabPasswordState,
    UiLabPreviewState,
    UiLabState,
)

PANEL_A_SUFFIX: str = "a"
PANEL_B_SUFFIX: str = "b"


class UiLabViewModel:
    """요청마다 새 revision marker로 ui_lab 표시 상태를 조립한다(상주 상태 없음)."""

    def build_state(self) -> UiLabState:
        """페이지 전체 표시 상태를 조립한다."""
        return UiLabState(
            page_title="UI 실험실",
            disclosure_summary="이 화면 사용 안내",
            disclosure_body=(
                "비밀번호는 표시 버튼으로 잠깐 확인할 수 있고, "
                "고른 이미지는 브라우저 안에서만 미리 보이며 서버로 올라가지 않습니다."
            ),
            panel_a=self.build_panel_a_state(),
            panel_b=self.build_panel_b_state(),
        )

    def build_panel_a_state(self) -> UiLabPanelState:
        """패널 A — root 교체 제어 없음, 자식 교체 제어 있음."""
        return self._build_panel_state(
            suffix=PANEL_A_SUFFIX,
            heading="패널 A",
            root_swap_enabled=False,
            child_swap_enabled=True,
        )

    def build_panel_b_state(self) -> UiLabPanelState:
        """패널 B — root 교체 제어 있음, 자식 교체 제어 없음."""
        return self._build_panel_state(
            suffix=PANEL_B_SUFFIX,
            heading="패널 B",
            root_swap_enabled=True,
            child_swap_enabled=False,
        )

    def build_preview_a_state(self) -> UiLabPreviewState:
        """패널 A의 미리보기(종속 자식 교체 단위) 표시 상태."""
        return self._build_preview_state(
            suffix=PANEL_A_SUFFIX,
            child_swap_enabled=True,
        )

    def build_note_a_state(self) -> UiLabNoteState:
        """패널 A 미리보기 안 노트(독립 자식 교체 단위) 표시 상태."""
        return self._build_note_state(suffix=PANEL_A_SUFFIX, swap_enabled=True)

    def _build_panel_state(
        self,
        suffix: str,
        heading: str,
        root_swap_enabled: bool,
        child_swap_enabled: bool,
    ) -> UiLabPanelState:
        return UiLabPanelState(
            dom_id=f"ui-lab-panel-{suffix}",
            heading=heading,
            revision_marker=self._new_revision_marker(),
            root_swap_enabled=root_swap_enabled,
            root_swap_label="패널 교체",
            password=self._build_password_state(suffix=suffix),
            preview=self._build_preview_state(
                suffix=suffix,
                child_swap_enabled=child_swap_enabled,
            ),
        )

    def _build_password_state(self, suffix: str) -> UiLabPasswordState:
        return UiLabPasswordState(
            dom_id=f"ui-lab-password-{suffix}",
            input_dom_id=f"ui-lab-password-{suffix}-input",
            input_name=f"ui_lab_password_{suffix}",
            label="비밀번호",
            show_label="비밀번호 표시",
            hide_label="비밀번호 숨김",
            autocomplete="new-password",
        )

    def _build_preview_state(
        self,
        suffix: str,
        child_swap_enabled: bool,
    ) -> UiLabPreviewState:
        return UiLabPreviewState(
            dom_id=f"ui-lab-preview-{suffix}",
            input_dom_id=f"ui-lab-preview-{suffix}-input",
            input_name=f"ui_lab_preview_{suffix}",
            label="이미지 고르기",
            clear_label="선택 비우기",
            empty_message="아직 고른 이미지가 없습니다.",
            error_message="이 파일은 이미지로 표시할 수 없습니다.",
            revision_marker=self._new_revision_marker(),
            child_swap_enabled=child_swap_enabled,
            child_swap_label="미리보기 교체",
            note=self._build_note_state(
                suffix=suffix,
                swap_enabled=child_swap_enabled,
            ),
        )

    def _build_note_state(self, suffix: str, swap_enabled: bool) -> UiLabNoteState:
        return UiLabNoteState(
            dom_id=f"ui-lab-note-{suffix}",
            text="고른 이미지는 브라우저를 떠나지 않습니다.",
            revision_marker=self._new_revision_marker(),
            swap_enabled=swap_enabled,
            swap_label="노트 교체",
        )

    def _new_revision_marker(self) -> str:
        return f"rev-{uuid4().hex[:12]}"
