from __future__ import annotations


def headings(rows: dict[str, object]) -> list[str]:
    return [row.title() for _, row in rows.items()]
