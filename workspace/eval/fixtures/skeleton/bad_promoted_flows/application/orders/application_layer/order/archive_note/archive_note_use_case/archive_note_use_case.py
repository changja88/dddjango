from __future__ import annotations

from typing import Callable

from application.orders.application_layer.order.archive_note.archive_note_command import ArchiveNoteCommand
from application.orders.application_layer.order.archive_note.archive_note_result import ArchiveNoteResult
from application.orders.application_layer.port.unit_of_work.order_unit_of_work import OrderUnitOfWork

from .archive_note_frame import ArchiveNoteFrame
from .note_memory import NoteMemory


class ArchiveNoteUseCase:
    def __init__(self, new_unit_of_work: Callable[[], OrderUnitOfWork]) -> None:
        self._frame: ArchiveNoteFrame = ArchiveNoteFrame(new_unit_of_work)

    def execute(self, command: ArchiveNoteCommand) -> ArchiveNoteResult:
        memory: NoteMemory = NoteMemory(note_id=command.target_id)
        self._frame.record_archive(memory)
        return ArchiveNoteResult(target_id=command.target_id, done=True)
