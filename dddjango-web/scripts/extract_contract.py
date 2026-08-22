#!/usr/bin/env python3
"""extract_contract — G1 승인 직후 server-contract.json 기계 절단 (architecture-web §6).

명세가 인용한 엔드포인트 paths를 동결본(openapi-full.json)에서 정확 일치로
선별하고 `$ref` 전이 폐쇄까지 추적해 경량본을 만든다. '관련' 판단이 명세 인용으로
치환돼 LLM 재량이 소멸하고, 손절단의 dangling `$ref`를 막는다.

사용:
  python extract_contract.py <openapi-full.json> --paths <paths-file> --out <server-contract.json>

paths-file: 한 줄에 `GET /api/v1/members/{id}` (메서드 생략 시 그 path 전 메서드).
종료코드: 0=성공 / 1=인용 누락·파싱 실패.

게이트 도구가 아니다 — blocker 의미론 없음. exit 1은 차단 판정이 아니라 발견의 신호다:
인용 path 부재("인용 path가 동결본에 없음")는 architect 임의 가정 → 설계 반송,
파싱 실패(비JSON·Swagger 2.0)는 동결본 자체 불량 → G0 계약 출처 재해소.
[warn](dangling ref·비복사 항목)은 stderr로 낸다 — 경량본 불완전 신호로
Coordinator가 배너에 표면화한다. 요약 1줄만 stdout이다.
"""
from __future__ import annotations

import copy
import json
import re
import sys
from typing import Any, Dict, Iterable, List, Optional, Set

HTTP_METHODS: Set[str] = {"get", "put", "post", "delete", "options", "head", "patch", "trace"}

USAGE: str = (
    "사용: python extract_contract.py <openapi-full.json> --paths <paths-file> --out <server-contract.json>"
)


def _deep_copy(value: Any) -> Any:
    """JSON 값 심층 복사 — 동결본 원본 구조를 절대 변형하지 않는다."""
    return copy.deepcopy(value)


def _unescape(segment: str) -> str:
    """JSON Pointer 세그먼트 이스케이프 해제(~1 → / 먼저, 그다음 ~0 → ~)."""
    return segment.replace("~1", "/").replace("~0", "~")


def _near_matches(want: str, have: Iterable[str]) -> List[str]:
    """근사 후보: 대소문자·trailing slash·경로 파라미터명 차이를 무시한 일치(최대 3개)."""

    def norm(p: str) -> str:
        return re.sub(r"/+$", "", re.sub(r"\{[^}]*\}", "{}", p.lower()))

    w: str = norm(want)
    return [h for h in have if norm(h) == w][:3]


def _collect_refs(node: Any, queue: List[str]) -> None:
    """`$ref` 문자열을 큐에 수집한다 — discriminator.mapping 값 포함."""
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "$ref" and isinstance(value, str):
                queue.append(value)
            elif key == "discriminator" and isinstance(value, dict) and isinstance(value.get("mapping"), dict):
                for mapped in value["mapping"].values():
                    if isinstance(mapped, str):
                        queue.append(mapped)
                _collect_refs(value, queue)
            else:
                _collect_refs(value, queue)
    elif isinstance(node, list):
        for item in node:
            _collect_refs(item, queue)


def _parse_argv(argv: List[str]) -> Optional[Dict[str, str]]:
    """인자 파싱 — <input> --paths <file> --out <file>. 셋 중 하나라도 없으면 None."""
    input_file: Optional[str] = None
    paths_file: Optional[str] = None
    out_file: Optional[str] = None
    i: int = 0
    while i < len(argv):
        arg: str = argv[i]
        if arg == "--paths":
            i += 1
            paths_file = argv[i] if i < len(argv) else None
        elif arg == "--out":
            i += 1
            out_file = argv[i] if i < len(argv) else None
        else:
            input_file = arg
        i += 1
    if input_file is None or paths_file is None or out_file is None:
        return None
    return {"input": input_file, "paths": paths_file, "out": out_file}


def main(argv: List[str]) -> int:
    args: Optional[Dict[str, str]] = _parse_argv(argv)
    if args is None:
        print(USAGE, file=sys.stderr)
        return 1

    # ── OpenAPI 3.x JSON 파싱(YAML·Swagger 2.0은 범위 밖)
    doc: Any
    try:
        with open(args["input"], encoding="utf-8") as f:
            doc = json.load(f)
    except (OSError, ValueError, UnicodeDecodeError) as e:
        print(
            f"[extract-contract] 파싱 실패: {e} — OpenAPI 3.x JSON 전제"
            "(YAML·Swagger 2.0은 범위 밖, architecture-web §6)",
            file=sys.stderr,
        )
        return 1
    if not isinstance(doc, dict):
        print(
            "[extract-contract] 파싱 실패: 최상위가 JSON 객체가 아님 — OpenAPI 3.x JSON 전제"
            "(architecture-web §6)",
            file=sys.stderr,
        )
        return 1
    if "swagger" in doc:
        print(
            "[extract-contract] Swagger 2.0 문서 — OpenAPI 3.x만 지원. "
            "서버에 3.x 엔드포인트를 확인하라.",
            file=sys.stderr,
        )
        return 1
    paths: Dict[str, Any] = doc.get("paths") if isinstance(doc.get("paths"), dict) else {}

    # ── 인용 목록 파싱 (path → 메서드 집합, 빈 집합 = 전 메서드)
    cited: Dict[str, Set[str]] = {}
    try:
        with open(args["paths"], encoding="utf-8") as f:
            cited_lines: List[str] = f.read().splitlines()
    except OSError as e:
        print(f"[extract-contract] paths-file 읽기 실패: {e}", file=sys.stderr)
        return 1
    for raw in cited_lines:
        line: str = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts: List[str] = line.split()
        if len(parts) >= 2 and parts[0].lower() in HTTP_METHODS:
            cited.setdefault(parts[1], set()).add(parts[0].lower())
        else:
            cited.setdefault(parts[-1], set())  # 전 메서드
    if not cited:
        print("[extract-contract] 인용 path 0개 — paths-file이 비었다.", file=sys.stderr)
        return 1

    # ── 정확 일치 검증 + 근사 후보 병기(trailing slash·파라미터명 차이의 오귀책 방지)
    missing: List[str] = [p for p in cited if p not in paths]
    if missing:
        print(
            "[extract-contract] 인용 path가 동결본에 없음 — "
            "명세의 임의 가정 여부를 확인하라(architecture-web §6):",
            file=sys.stderr,
        )
        for p in missing:
            near: List[str] = _near_matches(p, paths.keys())
            suffix: str = f"  (유사 path 존재: {', '.join(near)})" if near else ""
            print(f"  - {p}{suffix}", file=sys.stderr)
        return 1

    # ── path item 통째 복사 후 비인용 메서드 키만 제거(공유 parameters·servers 보존)
    out_paths: Dict[str, Any] = {}
    for path_key, methods in cited.items():
        item: Any = _deep_copy(paths[path_key])
        if methods and isinstance(item, dict):
            for k in [k for k in item if k in HTTP_METHODS and k not in methods]:
                del item[k]
        out_paths[path_key] = item

    # ── $ref 전이 폐쇄 (visited 집합 — 순환 스키마 대비)
    components: Dict[str, Any] = doc.get("components") if isinstance(doc.get("components"), dict) else {}
    kept_components: Dict[str, Dict[str, Any]] = {}
    visited: Set[str] = set()
    warnings: List[str] = []
    queue: List[str] = []

    _collect_refs(out_paths, queue)
    while queue:
        ref: str = queue.pop()
        if ref in visited:
            continue
        visited.add(ref)
        if ref.startswith("#/components/"):
            segs: List[str] = ref[len("#/components/"):].split("/")
            if len(segs) < 2:
                warnings.append(f"해석 불가 components ref: {ref}")
                continue
            section: str = segs[0]
            name: str = _unescape(segs[1])
            section_map: Any = components.get(section)
            src: Any = section_map.get(name) if isinstance(section_map, dict) else None
            if src is None:
                warnings.append(f"dangling ref: {ref} — 동결본 자체가 비자기완결")
                continue
            copied: Any = _deep_copy(src)
            kept_components.setdefault(section, {})[name] = copied
            _collect_refs(copied, queue)
        elif ref.startswith("#/paths/"):
            # operation 재사용 관례 — 경고 + 해당 path item 동반 복사(dangling 침묵 금지)
            ref_path_key: str = _unescape(ref[len("#/paths/"):].split("/")[0])
            if ref_path_key in paths and ref_path_key not in out_paths:
                companion: Any = _deep_copy(paths[ref_path_key])
                out_paths[ref_path_key] = companion
                _collect_refs(companion, queue)
            warnings.append(f"#/paths/ 로컬 ref 동반 복사: {ref}")
        elif ref.startswith("#/"):
            warnings.append(f"components 외 로컬 ref(원문 보존): {ref}")
        else:
            warnings.append(f"비로컬 ref(원문 보존 — 동결본 비자기완결 신호): {ref}")

    # ── 보존 목록: openapi·info·servers·루트 security·securitySchemes 전체
    out: Dict[str, Any] = {}
    for preserved_key in ("openapi", "info", "servers", "security"):
        if doc.get(preserved_key) is not None:
            out[preserved_key] = doc[preserved_key]
    out["paths"] = out_paths
    sec_schemes: Any = components.get("securitySchemes")
    if kept_components or sec_schemes is not None:
        merged: Dict[str, Any] = dict(kept_components)
        if sec_schemes is not None:
            merged["securitySchemes"] = _deep_copy(sec_schemes)
        out["components"] = merged
    if "webhooks" in doc:
        warnings.append("webhooks 비복사(무음 드롭 금지 — 필요하면 수동 확인)")
    if "pathItems" in components:
        warnings.append("components.pathItems는 ref로 닿은 것만 복사")

    # ── 산출(2-space·결정론 — 문서 등장 순서 보존) + [warn]은 stderr, 요약 1줄만 stdout
    try:
        with open(args["out"], "w", encoding="utf-8") as f:
            f.write(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
    except OSError as e:
        print(f"[extract-contract] 산출 쓰기 실패: {e}", file=sys.stderr)
        return 1
    for w in warnings:
        print(f"[warn] {w}", file=sys.stderr)
    comp_count: int = sum(len(m) for m in kept_components.values())
    print(f"[extract-contract] paths {len(out_paths)}개 · components {comp_count}개 → {args['out']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
