from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from typing import Literal, TypedDict

from pydantic import TypeAdapter


class LedgerLine(TypedDict):
    kind: Literal["line"]
    sku: str
    quantity: int


class LedgerNote(TypedDict):
    kind: Literal["note"]
    text: str


type LedgerRecord = LedgerLine | LedgerNote  # 판별 키 union — 내부 리터럴 생성엔 검증 불요
type JsonScalar = bool | int | float | str | None
type JsonValue = JsonScalar | Sequence[JsonValue] | Mapping[str, JsonValue]  # 구조 없는 통과·직렬화용

_LEDGER_RECORD: TypeAdapter[LedgerRecord] = TypeAdapter(LedgerRecord)


def load_ledger_record(raw: str) -> LedgerRecord:
    return _LEDGER_RECORD.validate_json(raw, strict=True)  # 파싱한 JSON 은 검증하며 받는다(R-3448)


def read_ledger_document(raw: str) -> LedgerRecord:
    document: object = json.loads(raw)  # 입구 object → 즉시 검증(#650 후보 아님)
    return _LEDGER_RECORD.validate_python(document, strict=True)


def ledger_summary(record: LedgerRecord) -> dict[str, JsonValue]:
    return {"kind": record["kind"], "fields": len(record)}
