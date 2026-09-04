"""#647 아래 적법 주석이 있는가 — 프레임워크 오버라이드·경계 입력 자리 mypy 탐침."""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, TypedDict

from django import forms

type JsonScalar = bool | int | float | str | None
type JsonValue = JsonScalar | Sequence[JsonValue] | Mapping[str, JsonValue]


class Cleaned(TypedDict, total=False):
    note: str


class F1(forms.Form):
    def clean(self) -> Cleaned:  # (1) TypedDict 반환으로 오버라이드
        return {"note": "x"}


class F2(forms.Form):
    def clean(self) -> dict[str, object]:  # (2) R-3447 처방(object) — #647 은 위반
        return dict(super().clean() or {})


class F3(forms.Form):
    def clean(self) -> Mapping[str, object]:  # (3) Mapping[str, object] 반환
        return dict(super().clean() or {})


class F4(forms.Form):
    def clean(self) -> dict[str, JsonValue]:  # (4) JsonValue 값 dict
        return {}


def takes_mapping(value: Mapping[str, object]) -> None: ...
def takes_dict_obj(value: dict[str, object]) -> None: ...
def takes_json(value: JsonValue) -> None: ...


def caller(c: Cleaned) -> None:
    takes_mapping(c)      # (5) TypedDict → Mapping[str, object] 호환?
    takes_dict_obj(c)     # (6) TypedDict → dict[str, object]?
    takes_json(c)         # (7) TypedDict → JsonValue?


import json


def load_raw(path: str) -> Cleaned:
    return json.loads(path)  # (8) json.loads → TypedDict 반환 (no-any-return?)


def load_obj(path: str) -> object:
    raw: object = json.loads(path)  # (9) object 로 받기
    return raw
