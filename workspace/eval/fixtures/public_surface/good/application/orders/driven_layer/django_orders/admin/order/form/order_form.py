from __future__ import annotations

from collections.abc import Mapping
from typing import TypeIs

from django import forms


def _is_mapping(value: object) -> TypeIs[Mapping[str, object]]:
    """경계 입력은 `object` 로 받아 받는 즉시 좁힌다(R-3448) — `Any` 없이."""
    return isinstance(value, Mapping)


class OrderForm(forms.Form):
    note = forms.CharField(max_length=64)

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)

    def clean(self) -> dict[str, object]:  # 스텁이 강제하는 오버라이드 — `dict[str, object]` 반환은 #647 면제
        raw: object = (super().clean() or {}).get("note")
        note: str = str(raw.get("text", "")) if _is_mapping(raw) else ""
        return {"note": note}
