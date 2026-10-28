from __future__ import annotations

from typing import Callable

from .print_label_frame import PrintLabelFrame


class LabelPrint:
    def __init__(self, frame: PrintLabelFrame) -> None:
        self._frame: PrintLabelFrame = frame

    def run(self, target_id: int, on_retry: Callable[[], None]) -> None:
        self._frame.record_done(target_id)
        on_retry()
