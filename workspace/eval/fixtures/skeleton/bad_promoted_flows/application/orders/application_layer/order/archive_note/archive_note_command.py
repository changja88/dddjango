from dataclasses import dataclass


@dataclass(frozen=True)
class ArchiveNoteCommand:
    target_id: int
