from dataclasses import dataclass


@dataclass(frozen=True)
class ArchiveNoteQuery:
    target_id: int
