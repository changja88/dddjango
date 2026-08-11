#!/usr/bin/env python3
"""openapi.json 을 «이름을 지운 모양»으로 정규화한다 — 클린룸 리빌드 라운드의 A축.

왜: 리빌드는 클래스·모듈·router 이름을 바꾼다(예: ErrorOut→FrameworkErrorSchema).
이름이 남은 원본 openapi 를 그대로 diff 하면 개명이 전부 잡음이 되고, 삭제 전
덤프를 파이프라인에 주면 옛 이름이 누출돼 클린룸이 깨진다. $ref 를 인라인하고
이름·산문 유래 키를 지우면 «계약의 모양»(경로·메서드·파라미터·페이로드 구조·
상태 코드)만 남는다 — 이 모양의 diff 0 이 스팩 등가의 기계 판정이다.

지우는 키: operationId(모듈 경로 유래) · title(클래스 이름 유래) · tags(router 이름)
· summary/description/example(s)(문서 표면 — 모양 아님. 중요한 값은 spec.md 가 요구로 적는다).
security 요구의 스킴 «이름»은 securitySchemes 의 실물 모양으로 치환한다.
순환 $ref 는 {"$cycle": true} 로 닫는다(이름을 남기지 않으려고 깊이만 끊는다).

사용: python3 openapi_shape.py <openapi.json>   # stdout 으로 정렬 JSON — 파일로 리다이렉트
exit 0 = 정상 / exit 1 = 재료 결손(파일 없음·JSON 아님).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

DROP_KEYS: "frozenset[str]" = frozenset(
    {"operationId", "title", "tags", "summary", "description", "example", "examples"}
)
_ORDERLESS_LIST_KEYS: "frozenset[str]" = frozenset({"required", "anyOf", "oneOf", "allOf", "enum"})


def _canon(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False)


def _resolve(node: Any, defs: "dict[str, Any]", stack: "tuple[str, ...]", key: str = "") -> Any:
    if isinstance(node, dict):
        ref = node.get("$ref")
        if isinstance(ref, str):
            name: str = ref.rsplit("/", 1)[-1]
            if name in stack:
                return {"$cycle": True}
            target = defs.get(name)
            if target is None:  # 밖을 가리키는 $ref — 모양만 남기고 이름은 지운다
                return {"$cycle": True}
            return _resolve(target, defs, stack + (name,), key)
        out: "dict[str, Any]" = {}
        for k in sorted(node):
            # DROP 은 «메타데이터 키»에만 — properties/ 밑의 k 는 페이로드 필드 이름이라
            # 같은 철자(title·description·example)여도 계약의 실물이다. 지우면 모양이 준다.
            if k in DROP_KEYS and key != "properties":
                continue
            if k == "mapping" and isinstance(node[k], dict):
                # discriminator.mapping 값은 스키마 이름 $ref — 키(wire 값)→변형 «모양» 결합은
                # 계약이므로 이름 대신 실물로 치환한다(이름 누출 차단·결합 보존).
                out[k] = {
                    mk: _resolve({"$ref": mv}, defs, stack, k) if isinstance(mv, str) and "#/" in mv else _resolve(mv, defs, stack, k)
                    for mk, mv in sorted(node[k].items())
                }
                continue
            out[k] = _resolve(node[k], defs, stack, k)
        return out
    if isinstance(node, list):
        items = [_resolve(v, defs, stack, key) for v in node]
        if key in _ORDERLESS_LIST_KEYS or key == "security":
            items.sort(key=_canon)
        if key == "parameters":
            items.sort(key=lambda p: (str(p.get("in", "")), str(p.get("name", ""))) if isinstance(p, dict) else ("", _canon(p)))
        return items
    return node


def shape(doc: "dict[str, Any]") -> "dict[str, Any]":
    components = doc.get("components") or {}
    defs: "dict[str, Any]" = dict(components.get("schemas") or {})
    schemes: "dict[str, Any]" = dict(components.get("securitySchemes") or {})

    paths = _resolve(doc.get("paths") or {}, defs, ())

    def swap_security(node: Any) -> Any:
        # {"AuthBearer": []} 같은 스킴 이름을 실물 모양으로 치환한다(이름 누출 차단)
        if isinstance(node, dict):
            if "security" in node and isinstance(node["security"], list):
                reqs = []
                for req in node["security"]:
                    if isinstance(req, dict):
                        reqs.append([_resolve(schemes.get(k, {"$cycle": True}), defs, (), "security") for k in sorted(req)])
                    else:
                        reqs.append(req)
                node = dict(node)
                node["security"] = sorted(reqs, key=_canon)
            return {k: swap_security(v) for k, v in node.items()}
        if isinstance(node, list):
            return [swap_security(v) for v in node]
        return node

    return {"paths": swap_security(paths)}


def main(argv: "list[str]") -> int:
    if len(argv) != 1:
        print("사용: openapi_shape.py <openapi.json>", file=sys.stderr)
        return 1
    src = Path(argv[0])
    if not src.is_file():
        print(f"재료 결손: {src} 없음", file=sys.stderr)
        return 1
    try:
        doc = json.loads(src.read_text(encoding="utf-8"))
    except ValueError as e:
        print(f"재료 결손: JSON 아님 — {e}", file=sys.stderr)
        return 1
    print(json.dumps(shape(doc), sort_keys=True, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
