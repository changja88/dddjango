from __future__ import annotations


class Order:
    """driven 조회 레코드 — 도메인 `Order` 와 이름만 같다(#195 도메인 출처 가드 · R8-D2)."""

    @classmethod
    def open_rows(cls) -> tuple["Order", ...]:
        return tuple(cls._model.objects.filter(status="open"))
