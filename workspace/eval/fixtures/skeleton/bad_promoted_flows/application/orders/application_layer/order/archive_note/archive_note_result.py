from dataclasses import dataclass


@dataclass(frozen=True)
class ArchiveNoteResult:
    target_id: int
    done: bool
