#!/usr/bin/env python3
"""design-spec «pre-gate» 예보 실행기 — G1 승인 전 결정적 검증 게이트 (관찰 모드).

왜 있나(설계 정본: workspace/design/2026-09-01-pregate-design.md v3 — §3 D1~D4·§4):
승인된 설계 명세가 registry 결정 계약과 조인되지 않은 채 동결되어 G1 «이후»에
반송되는 ③형 손실(레인당 평균 ≈34분)을, 명세의 기계가독 블록을 팬텀 스텁으로
실체화한 격리 사본 위에서 registry 27종을 미리 돌려 «G1 승인 전 결정적 예보»로
제거한다. 기존 검사기 27종은 한 줄도 수정·복제하지 않는다 — 같은 폴더의
`registry_gate.py`(판정 차분 N∖L)를 그대로 부른다(D1).

무엇을 하나:
  1) 파싱   — 명세의 기계 블록 5종(§4)을 문법대로 전사한다. 산문 추론 재료는 0이다.
              채널에 없으면 «부재»로 전사한다(fail-closed) — 부재가 위반이면 red 가
              나는 것이 정답이다.
  2) 사본   — 저장소 트리 밖 스크래치에 `git archive <BASE>` 사본 + dirty overlay
              (non-ignored 미커밋·미추적 실물 겹침 — D1-1) → `git init`+전량 commit
              (이 커밋이 앵커). 모든 git 호출은 이 스크립트 내부에서만, 훅은 전 호출
              `core.hooksPath=` 억제.
  3) 실체화 — 조치 태그 의미론(D2)대로 팬텀 스텁을 겹친다. 자동 삽입은 닫힌
              화이트리스트(②상수-배선형)뿐: 신규 BC 표준 골격 전량(`standard_tree`
              재사용)·apps.py 정형(#329/#535~#538)·e2e client 입구 상수(#390)·
              베이스 토큰 import 합성. 본문은 전부 `...`/`raise NotImplementedError`
              — C급은 판정 대상이 아님을 형태로 보증.
  4) 예보   — `registry_gate.py <사본> --anchor HEAD` 의 귀속(N∖L)이 «팬텀 유발
              위반»이다. `DJR_FINDINGS_JSON` 은 스크래치로 격리(실 저장소
              `.dddjango/violations/` 오염 금지).
  5) 리포트 — `--report` 경로에 append(D4): 기준선 SHA·프로필·모드 헤더, 예보
              항목별 안정 ID(sha256(규칙#+경로)[:12]), 사각 목록 상시 병기,
              already-built·미시뮬레이션 목록.

기계 블록 정본 문법(§4 — 이 문법이 곧 규범이다):
  file-plan        `<!-- machine: file-plan -->` 직후 ```paths 펜스.
                   1행 = `<add|update|remove[@Ln]|empty><공백|탭><경로>` + 선택 `#` 주석.
                   브레이스·와일드카드·`<placeholder>`·동일 경로 이중 서술 = 형식 red.
  symbols          `<!-- machine: symbols -->` + ```symbols 펜스.
                   1행 = `경로::Symbol[(Base)][ {필드, …}]`
                       | `경로::Symbol.method(파라미터)[ -> 반환]`   (선행 클래스 행 필수)
                       | `경로::snake_함수[(파라미터)][ -> 반환]`
                   필드 = `name: Type[ = default]` | `NAME = "literal"`(enum 멤버).
                   미등재 파일 = 심볼 부재(fail-closed).
  boundary-imports `<!-- machine: boundary-imports -->` + ```imports 펜스.
                   1행 = `<소비 파일 경로><탭|2+공백><import 문 그대로>`.
  physical-signals 영구 테스트 입장 표(6열 정본 header)의 owner/path 셀 안 정형
                   어노테이션 `[markers: a,b] [base: X] [client: yes]` — 무기재 = 부재.
  exception-map    `<!-- machine: exception-map -->` + ```exceptions 펜스.
                   1행 = `<예외 이름><탭|2+공백><raise 창구 파일 경로>` — 창구 스텁에
                   `raise <예외>()` 1줄 합성(#456 — 번역표에 없는 예외 = 죽은 계약 = 진탐 보존).

무엇이 아닌가: 예보는 Phase 2 step 6(G2 registry 게이트)의 실행·증거 요구를 어떤
형태로도 대체·축약하지 않는다(D4 대체 금지). green 은 «설계 검증됨»이 아니라
«P/S/I급 결정 계약 위반 예보 0»이다. 예보 기준선은 «스텁 제외 현재 상태»이며
`build_anchor` 를 읽지도 쓰지도 않는다(앵커 의미론).

사용: design_pregate.py <design-spec.md> <저장소 루트> [--base <git ref, 기본 HEAD>]
                        [--report <경로>] [--python <검사기 인터프리터>] [--keep]
exit 0 = 예보 green · 2 = 예보 red · 3 = 형식 red(파싱 오류·add 실존 충돌·금지 경로·
태그 이중 서술) · 4 = skip(machine 블록 부재 또는 실체화 0 — 사유 명시) ·
1 = 실행 불능(venv/인터프리터·git 실패). 어느 경우도 침묵 없음.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

SCRIPTS_DIR: Path = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))
try:
    import standard_tree as tree  # noqa: E402  — 신규 BC 골격 전량(D2 ② 화이트리스트)의 유일 트리 데이터
except ImportError:  # 데이터 모듈 없이는 골격 실체화 불가 — fail-closed(실행 불능)
    print("실행 불능: standard_tree.py 를 찾지 못했다 — 실행기와 같은 폴더에 있어야 한다", file=sys.stderr)
    sys.exit(1)

MODE: str = "observe"  # 관찰 모드 상수(설계 §10 M2) — red 는 기록·권고이며 레인을 막지 않는다
NO_SUBSTITUTE: str = ("예보는 Phase 2 step 6(G2 registry 게이트)의 실행·증거 요구를 "
                      "어떤 형태로도 대체·축약하지 않는다.")
COVER_NOTE: str = ("커버: P/S/I급 결정 계약 표면(보수 추정 — 유일한 판정자는 백테스트·"
                   "관찰 실측이다). C급·④형은 표면 밖.")
# 계획 경로 선검증(D3) — `_IGNORE_COPY` 조용 소실 방지 + 숨김 세그먼트 전면 거절.
FORBIDDEN_SEGMENTS: "frozenset[str]" = frozenset({
    "build", "dist", "staticfiles", "node_modules", "site-packages", "venv", ".dddjango",
})
# 기계 블록 마커 → 펜스 언어(§4). 이 어휘 밖의 machine 마커는 형식 red(fail-closed).
MACHINE_FENCES: "dict[str, str]" = {
    "file-plan": "paths",
    "symbols": "symbols",
    "boundary-imports": "imports",
    "exception-map": "exceptions",
}
# 영구 테스트 입장 표 정본 header 6열(조임 a — 영문 고정·셀 내 raw `|` 금지).
SIGNALS_HEADER: "tuple[str, ...]" = (
    "candidate", "protected contract/evidence", "unique production failure",
    "existing authoritative coverage", "decision", "owner/path",
)
# 베이스 토큰 → import 문 합성(D2 ②상수-배선형 — 정보-무함유 규약 상수만).
BASE_IMPORTS: "dict[str, str]" = {
    "ABC": "from abc import ABC, abstractmethod",
    "TestCase": "from django.test import TestCase",
    "TransactionTestCase": "from django.test import TransactionTestCase",
    "LiveServerTestCase": "from django.test import LiveServerTestCase",
    "StrEnum": "from enum import StrEnum",
    "IntEnum": "from enum import IntEnum",
    "Enum": "from enum import Enum",
    "Schema": "from ninja import Schema",
    "BaseModel": "from pydantic import BaseModel",
    "Exception": "",
    "AppConfig": "from django.apps import AppConfig",
    "Model": "from django.db import models",
    "Protocol": "from typing import Protocol",
    "DjangoModelFactory": "import factory",
}

_TAG_RE: "re.Pattern[str]" = re.compile(r"^(add|update|remove(?:@L\d+)?|empty)[ \t]+(\S+)\s*$")
_MARKER_RE: "re.Pattern[str]" = re.compile(r"<!--\s*machine:\s*([a-z-]+)\s*-->")
_FENCE_OPEN_RE: "re.Pattern[str]" = re.compile(r"^```([A-Za-z-]*)\s*$")
_SYM_LINE_RE: "re.Pattern[str]" = re.compile(r"^(\S+?)::(.+)$")
_METHOD_RE: "re.Pattern[str]" = re.compile(
    r"^([A-Z]\w*)\.([A-Za-z_]\w*)\((.*)\)\s*(?:->\s*(\S.*?))?\s*$")
_FUNC_RE: "re.Pattern[str]" = re.compile(
    r"^([a-z_]\w*)\s*(?:\((.*)\))?\s*(?:->\s*(\S.*?))?\s*$")
_CLASS_HEAD_RE: "re.Pattern[str]" = re.compile(r"^([A-Z]\w*)\s*(?:\((.*)\))?\s*$")
_FIELD_RE: "re.Pattern[str]" = re.compile(r"^[A-Za-z_]\w*\s*[:=]\s*\S.*$")
_IMPORT_ROW_RE: "re.Pattern[str]" = re.compile(
    r"^(\S+)(?:\t+| {2,})((?:from\s+\S+\s+import\s+.+|import\s+\S.*))$")
_EXC_ROW_RE: "re.Pattern[str]" = re.compile(r"^([A-Za-z_]\w*)(?:\t+| {2,})(\S+)\s*$")
_ANN_MARKERS_RE: "re.Pattern[str]" = re.compile(r"\[markers:\s*([^\]]*)\]")
_ANN_BASE_RE: "re.Pattern[str]" = re.compile(r"\[base:\s*([^\]]*)\]")
_ANN_CLIENT_RE: "re.Pattern[str]" = re.compile(r"\[client:\s*(yes|no)\s*\]")
_ATTR_LINE_RE: "re.Pattern[str]" = re.compile(r"\[#([\w-]+)\]\s+(\S+)")
_REQ_PY_RE: "re.Pattern[str]" = re.compile(r'requires-python\s*=\s*"[^"]*>=\s*(\d+)\.(\d+)')


class FormError(Exception):
    """형식 red(exit 3) — 파싱 오류·add 실존 충돌·금지 경로·태그 이중 서술."""


class RunError(Exception):
    """실행 불능(exit 1) — venv/인터프리터·git 실패·재료 결손."""


@dataclass
class Method:
    """클래스 스텁의 메서드 서술 — `Symbol.method(파라미터) -> 반환` 전사."""
    name: str
    params: str
    ret: str


@dataclass
class Symbol:
    """[신규 2] 공개 심볼 1행의 전사 — 필드 라인은 문법 검증된 원문 그대로 싣는다."""
    name: str
    base: str
    fields: "list[str]" = field(default_factory=list)
    methods: "list[Method]" = field(default_factory=list)
    kind: str = "class"  # class | function
    params: str = ""     # function 전용
    ret: str = ""        # function 전용


@dataclass
class Signals:
    """[신규 4] 물리 신호 어노테이션 — 무기재 = «물리 신호 없음»(fail-closed)."""
    markers: "list[str]" = field(default_factory=list)
    base: str = ""
    client: bool = False


@dataclass
class PlanEntry:
    """[신규 1] 파일 계획 1행 + 타 채널에서 결합된 실체화 재료."""
    path: str
    tag: str                     # add | update | remove | empty
    deferred_remove: bool = False  # `remove@Ln` — G1 승인 시점 상태 유지(후행 제거 격리)
    symbols: "list[Symbol]" = field(default_factory=list)
    imports: "list[str]" = field(default_factory=list)
    raises: "list[str]" = field(default_factory=list)
    signals: "Signals | None" = None


@dataclass
class Plan:
    """명세 1부의 전사 결과 — 실체화 입력의 전부(산문 추론 재료 0)."""
    entries: "dict[str, PlanEntry]" = field(default_factory=dict)
    notes: "list[str]" = field(default_factory=list)  # 고아 채널 행·미반영 결합(침묵 금지)


class _UsageParser(argparse.ArgumentParser):
    """usage 오류를 exit 1(실행 불능)로 — argparse 기본 exit 2 는 «예보 red»와 겹친다."""

    def error(self, message: str) -> None:
        print(f"실행 불능(사용 오류): {message}", file=sys.stderr)
        raise SystemExit(1)


# ── 파서 — 기계 블록 5종 ────────────────────────────────────────────────────

def _path_reject_reason(path: str) -> "str | None":
    """계획 경로 선검증(D3) — 거절 사유를 돌려준다(적법하면 None)."""
    if path.startswith(("/", "~")) or "\\" in path:
        return "절대 경로·역슬래시 금지(project-relative posix 경로만)"
    for ch in ("{", "}", "*", "…"):
        if ch in path:
            return f"브레이스·와일드카드 `{ch}` 금지"
    if "<" in path or ">" in path:
        return "미해소 `<placeholder>` 금지"
    parts: "tuple[str, ...]" = PurePosixPath(path).parts
    if ".." in parts:
        return "`..` 세그먼트 금지"
    for seg in parts:
        if seg.startswith("."):
            return f"숨김 세그먼트 `{seg}` 금지(도구·하네스 영역 — 검사 표면 아님)"
        if seg in FORBIDDEN_SEGMENTS:
            return f"금지 세그먼트 `{seg}` (`_IGNORE_COPY` 조용 소실 방지)"
    return None


def _machine_blocks(text: str, errors: "list[str]") -> "dict[str, list[str]]":
    """`<!-- machine: … -->` 마커 직후의 펜스 본문을 블록 이름별로 모은다.

    마커는 있는데 펜스가 없거나, 언어 태그가 어긋나거나, 어휘 밖 마커면 형식 red 재료다.
    같은 이름의 블록이 여러 번 나오면 행을 이어 붙인다(경로 중복은 파일 계획 파서가 잡는다).
    """
    lines: "list[str]" = text.splitlines()
    out: "dict[str, list[str]]" = {}
    i: int = 0
    while i < len(lines):
        m = _MARKER_RE.search(lines[i])
        if m is None:
            i += 1
            continue
        name: str = m.group(1)
        if name not in MACHINE_FENCES:
            errors.append(f"machine 마커 어휘 밖: `{name}` (허용: {sorted(MACHINE_FENCES)})")
            i += 1
            continue
        j: int = i + 1
        while j < len(lines) and not lines[j].strip():
            j += 1
        fm = _FENCE_OPEN_RE.match(lines[j].strip()) if j < len(lines) else None
        if fm is None or fm.group(1) != MACHINE_FENCES[name]:
            errors.append(f"machine 마커 `{name}` 직후에 ```{MACHINE_FENCES[name]} 펜스가 없다")
            i += 1
            continue
        body: "list[str]" = []
        j += 1
        while j < len(lines) and lines[j].strip() != "```":
            body.append(lines[j])
            j += 1
        if j >= len(lines):
            errors.append(f"machine 블록 `{name}` 의 펜스가 닫히지 않았다")
        out.setdefault(name, []).extend(body)
        i = j + 1
    return out


def _split_top(spec: str) -> "list[str]":
    """괄호·브래킷·중괄호·따옴표 깊이를 보는 최상위 콤마 분리(제네릭 타입 안 콤마 보존)."""
    out: "list[str]" = []
    cur: "list[str]" = []
    depth: int = 0
    quote: str = ""
    for ch in spec:
        if quote:
            cur.append(ch)
            if ch == quote:
                quote = ""
            continue
        if ch in "\"'":
            quote = ch
        elif ch in "{[(":
            depth += 1
        elif ch in "}])":
            depth -= 1
        if ch == "," and depth == 0:
            out.append("".join(cur).strip())
            cur = []
        else:
            cur.append(ch)
    if cur:
        out.append("".join(cur).strip())
    return [x for x in out if x]


def _parse_file_plan(rows: "list[str]", errors: "list[str]") -> "dict[str, PlanEntry]":
    """```paths 펜스 → 경로별 PlanEntry. 이중 서술·태그 불명·금지 경로 = 형식 red."""
    entries: "dict[str, PlanEntry]" = {}
    for raw in rows:
        hash_at: int = raw.find("#")
        line: str = (raw[:hash_at] if hash_at >= 0 else raw).strip()
        if not line:
            continue
        m = _TAG_RE.match(line)
        if m is None:
            errors.append(f"file-plan 행 파싱 불가: `{raw.strip()}`")
            continue
        tag_raw: str = m.group(1)
        path: str = m.group(2)
        reason: "str | None" = _path_reject_reason(path)
        if reason is not None:
            errors.append(f"경로 거절: {path} — {reason}")
            continue
        if path in entries:
            errors.append(f"태그 이중 서술: {path} ({entries[path].tag} ↔ {tag_raw}) — "
                          "동일 경로는 한 번만 서술한다")
            continue
        deferred: bool = tag_raw.startswith("remove@")
        tag: str = "remove" if deferred else tag_raw
        entries[path] = PlanEntry(path=path, tag=tag, deferred_remove=deferred)
    return entries


def _strip_receiver(params: str) -> str:
    """선행 수신자 청크(무어노테이션 `self`/`cls` **완전 일치**)만 벗긴다 — 렌더가 수신자를 합성하므로
    명세의 표기·무표기 양 관용을 같은 계획으로 정규화한다. 접두 유사 이름(`self_x`)·어노테이션
    수신자(`self: Self`)는 건드리지 않는다(후자는 중복 합성 → compile 형식 red로 정직하게 귀결)."""
    chunks: "list[str]" = _split_top(params)
    if chunks and chunks[0] in ("self", "cls"):
        return ", ".join(chunks[1:])
    return params


def _parse_symbol_rest(rest: str, errors: "list[str]", where: str) -> "Symbol | Method | None":
    """`::` 뒤 본문을 클래스/함수(Symbol) 또는 메서드(Method)로 파싱한다."""
    rest = rest.strip()
    mm = _METHOD_RE.match(rest)
    if mm is not None and "." in rest.split("(", 1)[0]:
        return Method(name=f"{mm.group(1)}.{mm.group(2)}",
                      params=_strip_receiver((mm.group(3) or "").strip()),
                      ret=(mm.group(4) or "").strip())
    fields_part: "str | None" = None
    head: str = rest
    if rest.endswith("}"):
        brace_at: int = rest.find("{")
        if brace_at < 0:
            errors.append(f"symbols 행 파싱 불가({where}): 필드 중괄호가 열리지 않았다")
            return None
        fields_part = rest[brace_at + 1:-1]
        head = rest[:brace_at].strip()
    if head[:1].islower() or head[:1] == "_":
        if fields_part is not None:
            errors.append(f"symbols 행 파싱 불가({where}): 함수에 필드 목록을 쓸 수 없다")
            return None
        fm = _FUNC_RE.match(head)
        if fm is None:
            errors.append(f"symbols 행 파싱 불가({where}): `{head}`")
            return None
        return Symbol(name=fm.group(1), base="", kind="function",
                      params=(fm.group(2) or "").strip(), ret=(fm.group(3) or "").strip())
    cm = _CLASS_HEAD_RE.match(head)
    if cm is None:
        errors.append(f"symbols 행 파싱 불가({where}): `{head}`")
        return None
    sym: Symbol = Symbol(name=cm.group(1), base=(cm.group(2) or "").strip())
    for chunk in _split_top(fields_part or ""):
        if _FIELD_RE.match(chunk) is None:
            errors.append(f"symbols 필드 파싱 불가({where}): `{chunk}` — "
                          "`name: Type[ = default]` 또는 `NAME = \"literal\"` 만 허용")
            continue
        sym.fields.append(chunk)
    return sym


def _parse_symbols(rows: "list[str]", plan: Plan, errors: "list[str]") -> None:
    """```symbols 펜스 → PlanEntry.symbols 결합. 메서드 행은 선행 클래스 행이 필수다."""
    for raw in rows:
        line: str = raw.strip()
        if not line or line.startswith("#"):
            continue
        m = _SYM_LINE_RE.match(line)
        if m is None:
            errors.append(f"symbols 행 파싱 불가: `{line}`")
            continue
        path: str = m.group(1)
        parsed: "Symbol | Method | None" = _parse_symbol_rest(m.group(2), errors, path)
        if parsed is None:
            continue
        entry: "PlanEntry | None" = plan.entries.get(path)
        if entry is None:
            plan.notes.append(f"symbols 고아 행(file-plan 미등재 — 미반영): {path}::{m.group(2).strip()}")
            continue
        if entry.tag != "add":
            plan.notes.append(f"symbols 미반영(비-add `{entry.tag}` 칸): {path}")
            continue
        if isinstance(parsed, Method):
            cls_name: str = parsed.name.split(".", 1)[0]
            owner: "Symbol | None" = next(
                (s for s in entry.symbols if s.kind == "class" and s.name == cls_name), None)
            if owner is None:
                errors.append(f"symbols 메서드 행의 선행 클래스 부재: {path}::{parsed.name}")
                continue
            owner.methods.append(Method(name=parsed.name.split(".", 1)[1],
                                        params=parsed.params, ret=parsed.ret))
        else:
            entry.symbols.append(parsed)


def _parse_imports(rows: "list[str]", plan: Plan, errors: "list[str]") -> None:
    """```imports 펜스 → PlanEntry.imports 결합(import 문 원문 그대로)."""
    for raw in rows:
        line: str = raw.strip()
        if not line or line.startswith("#"):
            continue
        m = _IMPORT_ROW_RE.match(line)
        if m is None:
            errors.append(f"boundary-imports 행 파싱 불가: `{line}` — "
                          "`<경로><탭|2+공백><import 문>` 형식이어야 한다")
            continue
        path: str = m.group(1)
        stmt: str = m.group(2).strip()
        entry: "PlanEntry | None" = plan.entries.get(path)
        if entry is None:
            plan.notes.append(f"boundary-imports 고아 행(file-plan 미등재 — 미반영): {path}")
            continue
        if entry.tag != "add":
            plan.notes.append(f"boundary-imports 미반영(비-add `{entry.tag}` 칸): {path}")
            continue
        if stmt not in entry.imports:
            entry.imports.append(stmt)


def _parse_exception_map(rows: "list[str]", plan: Plan, errors: "list[str]") -> None:
    """```exceptions 펜스 → raise 창구 스텁에 `raise <예외>()` 1줄 합성 재료(#456 처분)."""
    for raw in rows:
        line: str = raw.strip()
        if not line or line.startswith("#"):
            continue
        m = _EXC_ROW_RE.match(line)
        if m is None:
            errors.append(f"exception-map 행 파싱 불가: `{line}` — "
                          "`<예외 이름><탭|2+공백><창구 파일 경로>` 형식이어야 한다")
            continue
        exc: str = m.group(1)
        path: str = m.group(2)
        entry: "PlanEntry | None" = plan.entries.get(path)
        if entry is None:
            plan.notes.append(f"exception-map 고아 행(file-plan 미등재 — 미반영): {exc} → {path}")
            continue
        if entry.tag != "add":
            plan.notes.append(f"exception-map 미반영(비-add `{entry.tag}` 창구): {exc} → {path}")
            continue
        if exc not in entry.raises:
            entry.raises.append(exc)


def _cells(row: str) -> "list[str]":
    """markdown 표 1행 → 셀 목록(조임 a — 셀 내 raw `|` 금지 전제의 단순 분리)."""
    return [c.strip() for c in row.strip().strip("|").split("|")]


def _parse_signals(text: str, plan: Plan) -> None:
    """영구 테스트 입장 표(정본 6열 header)의 owner/path 셀에서 [신규 4] 어노테이션 전사.

    어노테이션이 하나도 없는 행은 «물리 신호 없음»과 같으므로 결합하지 않는다(fail-closed).
    """
    lines: "list[str]" = text.splitlines()
    i: int = 0
    while i < len(lines):
        row: str = lines[i].strip()
        if row.startswith("|") and tuple(c.lower() for c in _cells(row)) == SIGNALS_HEADER:
            i += 1
            if i < len(lines) and re.fullmatch(r"[|\s:-]+", lines[i].strip() or "x"):
                i += 1  # 구분선
            while i < len(lines) and lines[i].strip().startswith("|"):
                cells: "list[str]" = _cells(lines[i])
                i += 1
                if len(cells) != len(SIGNALS_HEADER):
                    plan.notes.append(f"입장 표 행 열 수 불일치(무시): {cells[:1]}")
                    continue
                cell: str = cells[5]
                markers_m = _ANN_MARKERS_RE.search(cell)
                base_m = _ANN_BASE_RE.search(cell)
                client_m = _ANN_CLIENT_RE.search(cell)
                if markers_m is None and base_m is None and client_m is None:
                    continue  # 무기재 = 물리 신호 없음
                tick = re.search(r"`([^`]+)`", cell)
                path: "str | None" = tick.group(1) if tick else next(
                    (t for t in cell.split() if "/" in t and not t.startswith("[")), None)
                if path is None:
                    plan.notes.append(f"physical-signals 경로 해소 불가(owner/path 셀): {cell!r}")
                    continue
                entry: "PlanEntry | None" = plan.entries.get(path)
                if entry is None or entry.tag != "add":
                    plan.notes.append(f"physical-signals 미반영(미등재 또는 비-add): {path}")
                    continue
                sig: Signals = Signals()
                if markers_m is not None:
                    sig.markers = [t.strip() for t in markers_m.group(1).split(",") if t.strip()]
                if base_m is not None:
                    sig.base = base_m.group(1).strip()
                sig.client = client_m is not None and client_m.group(1) == "yes"
                entry.signals = sig
            continue
        i += 1


def parse_spec(text: str) -> "tuple[Plan | None, list[str]]":
    """명세 전문 → (Plan, 형식 오류 목록). file-plan 블록 부재면 (None, []) — skip 재료."""
    errors: "list[str]" = []
    blocks: "dict[str, list[str]]" = _machine_blocks(text, errors)
    if "file-plan" not in blocks and not errors:
        return None, []
    plan: Plan = Plan()
    plan.entries = _parse_file_plan(blocks.get("file-plan", []), errors)
    _parse_symbols(blocks.get("symbols", []), plan, errors)
    _parse_imports(blocks.get("boundary-imports", []), plan, errors)
    _parse_exception_map(blocks.get("exception-map", []), plan, errors)
    _parse_signals(text, plan)
    # apps.py 정형(② 화이트리스트): django_* apps.py 심볼의 무기재 베이스는 AppConfig 규약 상수이고,
    # 결손 필드(name/label)는 정형 값으로 보충한다 — 전사된 필드는 유지(전사 우선·일탈은 예보에 실린다).
    for entry in plan.entries.values():
        if entry.path.endswith("/apps.py") and "django_" in entry.path:
            parent: PurePosixPath = PurePosixPath(entry.path).parent
            parts: "tuple[str, ...]" = parent.parts
            bc: str = parts[1] if len(parts) >= 2 and parts[0] == "application" else ""
            dotted: str = ".".join(parts)
            for sym in entry.symbols:
                if sym.kind != "class":
                    continue
                if not sym.base:
                    sym.base = "AppConfig"
                if (sym.base or "").strip() != "AppConfig":
                    continue
                heads: "set[str]" = {f.split("=")[0].split(":")[0].strip() for f in sym.fields}
                if "name" not in heads:
                    sym.fields.append(f'name = "{dotted}"')
                if "label" not in heads and bc:
                    sym.fields.append(f'label = "{bc}"')
    return plan, errors


# ── 스텁 렌더러 — D2 규약(본문은 `...`/`raise NotImplementedError` 뿐) ─────────

_SNAKE_ACRONYM_RE = re.compile(r"([A-Z]+)([A-Z][a-z])")
_SNAKE_BOUNDARY_RE = re.compile(r"([a-z\d])([A-Z])")
_MODEL_DIR_RE = re.compile(r"^application/([^/]+)/driven_layer/django_[^/]+/models/[^/]+\.py$")


def _snake(name: str) -> str:
    """CamelCase → snake_case — check-db-table.py `_snake` 의 2-pass regex 문자 복제.
    유도값의 byte 동치가 계약이다(재구현 드리프트 = 신규 #630 아티팩트)."""
    s: str = _SNAKE_ACRONYM_RE.sub(r"\1_\2", name)
    s = _SNAKE_BOUNDARY_RE.sub(r"\1_\2", s)
    return s.lower()


def _derived_db_table(path: str, class_name: str) -> "str | None":
    """모델 칸의 `*Model` 클래스 → #630 유도 규칙의 기대 db_table. 그 외 None.
    label 은 경로 bc(정형 label)와 동일 가정 — 커스텀 label 계획의 유도 불일치는 사각 병기."""
    m = _MODEL_DIR_RE.match(path)
    if m is None or not class_name.endswith("Model") or class_name == "Model":
        return None
    base: str = class_name[: -len("Model")]
    return f"{m.group(1)}_{_snake(base)}"

def _class_stub(sym: Symbol, meta_db_table: "str | None" = None) -> "list[str]":
    """클래스 스텁 — 필드·enum 멤버는 전사 원문, 메서드 본문은 NotImplementedError.

    base 가 정확히 `ABC`(원문 완전 일치)면 선언형으로 렌더한다: `@abstractmethod` + `...` —
    #212/#283 판정은 데코레이터 유일 조건이라 실코드 선언 관례와 같은 판정 경로를 탄다.
    `meta_db_table` 이 주어지고 필드에 `db_table` 전사가 없으면 `class Meta` 를 합성한다(#630
    유도 규칙과 byte 동치 — 결손 시만·전사 우선)."""
    head: str = f"class {sym.name}({sym.base}):" if sym.base else f"class {sym.name}:"
    lines: "list[str]" = [head, '    """계획 스텁."""']
    body: "list[str]" = [f"    {chunk}" for chunk in sym.fields]
    field_heads: "set[str]" = {f.split("=")[0].split(":")[0].strip() for f in sym.fields}
    if meta_db_table is not None and "db_table" not in field_heads:
        body.append("    class Meta:")
        body.append(f'        db_table = "{meta_db_table}"')
    declarative_abc: bool = (sym.base or "").strip() == "ABC"
    for meth in sym.methods:
        sig: str = f"self, {meth.params}" if meth.params else "self"
        ret: str = meth.ret or "object"
        if declarative_abc:
            body.append("    @abstractmethod")
            body.append(f"    def {meth.name}({sig}) -> {ret}:")
            body.append("        ...")
        else:
            body.append(f"    def {meth.name}({sig}) -> {ret}:")
            body.append("        raise NotImplementedError")
    lines.extend(body if body else ["    ..."])
    return lines


def render_stub(entry: PlanEntry) -> str:
    """PlanEntry 하나 → 팬텀 스텁 본문. 산문 추론 재료 0 — 전사·상수·처분표뿐이다."""
    lines: "list[str]" = ['"""pre-gate 팬텀 스텁."""', "from __future__ import annotations", ""]
    emitted: "set[str]" = set()
    sig: Signals = entry.signals or Signals()
    # [신규 4] base 채널 — 무기재 클래스에만 결합(전사 우선·fail-closed). import 합성 «전»에
    # 치환해야 신호 베이스도 화이트리스트 import 를 받는다.
    symbols: "list[Symbol]" = [
        Symbol(name=s.name, base=sig.base, fields=s.fields, methods=s.methods)
        if (s.kind == "class" and not s.base and sig.base) else s
        for s in entry.symbols
    ]
    for sym in symbols:
        token: str = (sym.base or "").split(".")[-1].split("[")[0]
        stmt: str = BASE_IMPORTS.get(token, "")
        if stmt and stmt not in emitted and stmt not in entry.imports:
            lines.append(stmt)
            emitted.add(stmt)
    for stmt in entry.imports:
        if stmt.startswith("from __future__"):
            continue  # 최상단 하드코딩 1회가 유일한 자리 — 전사 재방출은 위치 오류(compile red)가 된다
        if stmt not in emitted:
            lines.append(stmt)
            emitted.add(stmt)
    if sig.markers:
        lines.append("import pytest")
    lines.append("")
    if sig.markers:
        marks: str = ", ".join(f"pytest.mark.{m}" for m in sig.markers)
        lines.append(f"pytestmark: list = [{marks}]")
        lines.append("")
    for sym in symbols:
        if sym.kind == "function":
            ret: str = sym.ret or "object"
            lines.append(f"def {sym.name}({sym.params}) -> {ret}:")
            lines.append('    """계획 스텁."""')
            lines.append("    raise NotImplementedError")
        else:
            lines.extend(_class_stub(sym, _derived_db_table(entry.path, sym.name)))
        lines.append("")
    for exc in entry.raises:
        lines.append(f"def _pregate_raise_{exc.lower()}() -> None:")
        lines.append('    """예외 번역표 합성(D2 ③처분표 — #456 진탐 보존)."""')
        lines.append(f"    raise {exc}()")
        lines.append("")
    if sig.client or "/test/e2e/" in entry.path:
        lines.append("def test_planned_client_flow(client) -> None:")
        lines.append('    """계획 스텁 — 입구 통과 규약 상수(#390)."""')
        lines.append('    client.get("/")')
        lines.append("    raise NotImplementedError")
        lines.append("")
    return "\n".join(lines) + "\n"


# ── 격리 사본 — archive + dirty overlay + init (D1) ─────────────────────────

def _git(cwd: Path, *args: str, check: bool = True) -> "subprocess.CompletedProcess[bytes]":
    """훅 억제·서명 억제 git 호출 — 실패는 RunError(실행 불능)."""
    argv: "list[str]" = ["git", "-C", str(cwd), "-c", "core.hooksPath=",
                         "-c", "commit.gpgsign=false",
                         "-c", "user.email=pregate@local", "-c", "user.name=pregate"] + list(args)
    proc: "subprocess.CompletedProcess[bytes]" = subprocess.run(argv, capture_output=True)
    if check and proc.returncode != 0:
        raise RunError(f"git {' '.join(args[:2])} 실패: "
                       f"{proc.stderr.decode('utf-8', 'replace').strip()[:400]}")
    return proc


def _extract_archive(repo: Path, base_sha: str, copy: Path) -> None:
    """`git archive <BASE>` 를 사본 디렉터리로 푼다(훅 억제·저장소 트리 밖)."""
    proc: "subprocess.CompletedProcess[bytes]" = _git(repo, "archive", base_sha)
    with tarfile.open(fileobj=io.BytesIO(proc.stdout), mode="r:") as tf:
        try:
            tf.extractall(copy, filter="data")
        except TypeError:  # python < 3.12 — filter 미지원
            tf.extractall(copy)


def _overlay_dirty(repo: Path, copy: Path) -> "list[str]":
    """dirty overlay(D1-1) — non-ignored 미커밋·미추적 실물을 사본 위에 겹친다.

    porcelain v1 -z 기준: 수정·신규는 working tree 실물 복사, 삭제는 사본에서 제거,
    rename 은 to 복사 + from 제거로 수렴한다(실물 존재 여부가 판정 기준).
    """
    proc: "subprocess.CompletedProcess[bytes]" = _git(
        repo, "status", "--porcelain=v1", "-z", "--untracked-files=all")
    tokens: "list[str]" = proc.stdout.decode("utf-8", "replace").split("\0")
    touched: "list[str]" = []
    idx: int = 0
    while idx < len(tokens):
        token: str = tokens[idx]
        idx += 1
        if len(token) < 4:
            continue
        status: str = token[:2]
        rels: "list[str]" = [token[3:]]
        if status[0] in "RC" and idx < len(tokens) and tokens[idx]:
            rels.append(tokens[idx])  # rename/copy 의 origin 경로
            idx += 1
        for rel in rels:
            src: Path = repo / rel
            dst: Path = copy / rel
            if src.is_file() or src.is_symlink():
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst, follow_symlinks=False)
                touched.append(rel)
            elif src.is_dir():
                shutil.copytree(src, dst, dirs_exist_ok=True, symlinks=True)
                touched.append(rel + "/")
            elif dst.is_file() or dst.is_symlink():
                dst.unlink()
                touched.append(f"removed {rel}")
    return touched


# ── 팬텀 실체화 — 태그 의미론(D2) + 신규 BC 골격 전량(② 화이트리스트) ────────

def _write_apps_py(target: Path, bc: str, app_dir_name: str) -> None:
    """apps.py 정형 골격(#329~#332·#535~#538 규약 상수 — 정보-무함유)."""
    cls: str = "".join(w.title() for w in bc.split("_")) + "Config"
    target.write_text(
        "from django.apps import AppConfig\n\n\n"
        f"class {cls}(AppConfig):\n"
        '    """pre-gate 팬텀 정형 골격."""\n\n'
        f'    name = "application.{bc}.driven_layer.{app_dir_name}"\n'
        f'    label = "{bc}"\n',
        encoding="utf-8",
    )


def materialize_skeleton(copy: Path, bc_name: str) -> None:
    """신규 BC 의 fixed/reappear 골격 전량 실체화(D2 ②상수-배선형 — #488/#486 대응).

    `standard_tree` 를 재사용해 고정·재등장 칸을 빈 파일/`__init__.py` 폴더로 채운다.
    자리표시자 칸은 실존 인스턴스 폴더에만 재귀한다(빈 개념은 만들지 않는다 — #489).
    """
    bc_dir: Path = copy / "application" / bc_name
    if not bc_dir.exists():
        return
    (bc_dir / "__init__.py").touch()

    def walk(row: "tree.Row", dirpath: Path, bindings: "dict[str, str]") -> None:
        kids: "tuple[tree.Row, ...]" = tree.children(row)
        fixed_claimed: "set[str]" = set()
        for c in kids:
            if c.kind in ("fixed", "reappear"):
                name: str = tree.concrete_name(c, bindings)
                if "<" in name:
                    continue  # 미해소 재등장 — 이 수준에서 바인딩 없음
                name = name.rstrip("/")
                fixed_claimed.add(name)
                tgt: Path = dirpath / name
                if tree.is_dir(c):
                    tgt.mkdir(parents=True, exist_ok=True)
                    (tgt / "__init__.py").touch()
                    walk(c, tgt, bindings)
                elif not tgt.exists():
                    if name == "apps.py" and dirpath.name.startswith("django_"):
                        _write_apps_py(tgt, bindings.get("bounded_context", ""), dirpath.name)
                    else:
                        tgt.touch()
        for c in kids:
            if c.kind == "placeholder" and tree.is_dir(c) and dirpath.exists():
                token: str = c.name.rstrip("/").strip("<>")
                for p in sorted(dirpath.iterdir()):
                    if p.is_dir() and p.name not in fixed_claimed and p.name != "__pycache__":
                        inner: "dict[str, str]" = dict(bindings)
                        inner[token] = p.name
                        walk(c, p, inner)

    walk(tree.bc_root(), bc_dir, {"bounded_context": bc_name})


def materialize(copy: Path, plan: Plan) -> "dict[str, list[str]]":
    """태그 의미론(D2)대로 사본 위에 팬텀을 겹친다 — add 실존 충돌은 FormError.

    반환: materialized / already_built / unsimulated 목록(리포트 재료 — 침묵 금지).
    """
    report: "dict[str, list[str]]" = {"materialized": [], "already_built": [], "unsimulated": []}
    for entry in plan.entries.values():
        target: Path = copy / entry.path
        if entry.tag == "add":
            if target.exists():
                raise FormError(f"add 충돌(실존): {entry.path} — 계획과 실물의 모순은 그 자체가 발견이다")
            stub: str = render_stub(entry)
            try:
                compile(stub, entry.path, "exec")  # symtable까지 — 중복 인자류는 ast.parse 가 못 잡는다
            except (SyntaxError, ValueError) as exc:
                detail: str = getattr(exc, "msg", None) or str(exc)
                raise FormError(f"스텁 렌더 파싱 불가: {entry.path} — {detail} "
                                "(기계 블록 전사 내용이 파이썬 문법 밖이다)")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(stub, encoding="utf-8")
            report["materialized"].append(entry.path)
        elif entry.tag == "empty":
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists():
                report["already_built"].append(f"empty(기실현): {entry.path}")
            else:
                target.write_text("", encoding="utf-8")
                report["materialized"].append(entry.path)
        elif entry.tag == "remove":
            if entry.deferred_remove:
                report["unsimulated"].append(f"후행 remove(@Ln — G1 승인 시점 상태 유지): {entry.path}")
            elif target.is_file():
                target.unlink()
                report["materialized"].append(f"removed {entry.path}")
            else:
                report["unsimulated"].append(f"remove(실존 없음): {entry.path}")
        elif entry.tag == "update":
            report["unsimulated"].append(f"update(시뮬레이션 밖 — ② 화이트리스트 정형 append 한정): {entry.path}")
    # 신규 BC 골격 전량 — 앵커 커밋에 없던 BC 만(② 화이트리스트 · #488 오탐 형태 소멸).
    new_bcs: "set[str]" = set()
    for entry in plan.entries.values():
        parts: "tuple[str, ...]" = PurePosixPath(entry.path).parts
        if len(parts) >= 2 and parts[0] == "application":
            new_bcs.add(parts[1])
    for bc in sorted(new_bcs):
        listed: "subprocess.CompletedProcess[bytes]" = _git(
            copy, "ls-tree", "HEAD", f"application/{bc}", check=False)
        if not listed.stdout.strip():
            materialize_skeleton(copy, bc)
    # `__init__.py` 체인 보강 — 패키지 인식(골격 최소).
    for entry in plan.entries.values():
        if entry.tag in ("add", "empty"):
            parent: Path = Path(entry.path).parent
            while parent.parts and str(parent) != ".":
                init_file: Path = copy / parent / "__init__.py"
                if not init_file.exists() and (copy / parent).is_dir():
                    init_file.write_text("", encoding="utf-8")
                parent = parent.parent
    return report


# ── 실행 계약(D3) — 인터프리터·게이트·exit 매핑 ─────────────────────────────

def _interpreter_gap_reason(repo: Path, python_bin: str) -> "str | None":
    """대상 `requires-python` 하한을 검사기 인터프리터가 못 미치면 «실행 불능» 사유."""
    try:
        probe: "subprocess.CompletedProcess[str]" = subprocess.run(
            [python_bin, "-c", "import sys; print('%d.%d' % sys.version_info[:2])"],
            capture_output=True, text=True)
    except OSError as exc:  # 인터프리터 경로 자체가 없다/실행 불가 — traceback 아닌 문면 계약으로
        return f"검사기 인터프리터 실행 불가: {python_bin} — {exc}"
    if probe.returncode != 0:
        return f"검사기 인터프리터 실행 불가: {python_bin}"
    cur: "tuple[int, ...]" = tuple(int(x) for x in probe.stdout.strip().split("."))
    pyproject: Path = repo / "pyproject.toml"
    if not pyproject.is_file():
        return None
    m = _REQ_PY_RE.search(pyproject.read_text(encoding="utf-8", errors="replace"))
    if m is None:
        return None
    lo: "tuple[int, int]" = (int(m.group(1)), int(m.group(2)))
    if cur >= lo:
        return None
    return (f"대상은 python >={lo[0]}.{lo[1]} 선언(pyproject.toml)인데 인터프리터는 "
            f"{cur[0]}.{cur[1]} 다 — fail-open 침묵 clean 위험. 대상 venv 인터프리터를 --python 으로 넘겨라")


def run_gate(copy: Path, scratch: Path, python_bin: str) -> "tuple[int, list[str], str]":
    """registry_gate(판정 차분) 실행 — (exit, 귀속 라인, stdout)을 돌려준다."""
    introduced: Path = scratch / "introduced.json"
    env: "dict[str, str]" = dict(os.environ)
    env["DJR_FINDINGS_JSON"] = str(scratch / "findings.jsonl")  # 스크래치 격리(D3)
    env.pop("DJR_VIOLATIONS_DIR", None)
    env.pop("DJR_SOURCE_GIT_ROOT", None)
    proc: "subprocess.CompletedProcess[str]" = subprocess.run(
        [python_bin, str(SCRIPTS_DIR / "registry_gate.py"), str(copy),
         "--anchor", "HEAD", "--introduced-json", str(introduced)],
        capture_output=True, text=True, env=env)
    if proc.returncode not in (0, 2):
        raise RunError(f"registry_gate 실행 불능(exit {proc.returncode}): "
                       f"{(proc.stderr or proc.stdout).strip()[-600:]}")
    if not introduced.is_file():
        raise RunError("registry_gate 가 introduced.json 을 남기지 않았다 — 재료 결손(fail-closed)")
    payload: "dict[str, object]" = json.loads(introduced.read_text(encoding="utf-8"))
    attributed: "list[str]" = [str(x) for x in payload.get("attributed_lines", [])]
    return proc.returncode, attributed, proc.stdout


def _stable_id(line: str) -> str:
    """예보 항목 안정 ID — sha256(규칙#+경로)[:12] (D4 처분 라벨 추적 키)."""
    m = _ATTR_LINE_RE.search(line)
    rule: str = m.group(1) if m else "?"
    where: str = m.group(2).split(":", 1)[0] if m else line
    return hashlib.sha256(f"#{rule}+{where}".encode("utf-8")).hexdigest()[:12]


BLIND_SPOTS: "tuple[str, ...]" = (
    "C급(함수 본문·행위 규칙): 스텁 본문이 `...` 뿐이라 예보 표면 밖이다.",
    "④형(명세 내부 의미 모순·규범 과잉결정): 검출 대상이 아니다.",
    "BC 내부 계층 의존 오설계(#92/#93류): 유도 삽입은 정의상 규약 준수형 — 원리적 예보 불가.",
    "앵커·상태 축: 예보 기준선은 «스텁 제외 현재 상태»다 — G2 build_anchor 차분과 다르며, "
    "HEAD 판형 게이트 결과의 G2 증거 유용은 차분 세탁으로 금지된다.",
    "미시뮬레이션: update 계획·후행 remove(@Ln)는 실체화하지 않는다 — 위 목록 병기.",
    "정형 보충(apps.py name/label·모델 Meta.db_table): 결손 시 규약 유도값을 합성한다 — 기계 블록 "
    "전사가 있으면 전사 우선이지만, «산문»으로만 규약 밖 값을 계획한 일탈은 예보 표면 밖이다.",
)


def write_report(report_path: Path, spec: Path, base_ref: str, base_sha: str, verdict: str,
                 attributed: "list[str]", mat: "dict[str, list[str]]",
                 notes: "list[str]") -> None:
    """예보 리포트 append(D4) — 헤더 상시 문구·안정 ID·사각 목록 병기."""
    now: str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines: "list[str]" = [
        "",
        f"## pre-gate 예보 — {now} · {spec.name}",
        "",
        f"- 기준선 SHA: `{base_sha}` (--base {base_ref}) — «스텁 제외 현재 상태» · "
        f"프로필: auto · 모드: 관찰({MODE}) · 실행기: design_pregate.py",
        f"- {NO_SUBSTITUTE}",
        f"- {COVER_NOTE}",
        f"- 판정: {verdict}",
        "",
        f"### 예보 항목 ({len(attributed)}건 · 안정 ID = sha256(규칙#+경로)[:12])",
        "",
    ]
    if attributed:
        lines.extend(f"- `{_stable_id(line)}` {line}" for line in attributed)
    else:
        lines.append("- (없음) — green 은 «설계 검증됨»이 아니라 «P/S/I급 위반 예보 0»이다.")
    lines += ["", f"### already-built ({len(mat.get('already_built', []))}건) · "
                  f"미시뮬레이션 ({len(mat.get('unsimulated', []))}건)", ""]
    for item in mat.get("already_built", []):
        lines.append(f"- already-built: {item}")
    for item in mat.get("unsimulated", []):
        lines.append(f"- 미시뮬레이션: {item}")
    for note in notes:
        lines.append(f"- 채널 메모: {note}")
    if not (mat.get("already_built") or mat.get("unsimulated") or notes):
        lines.append("- (없음)")
    lines += ["", "### 사각 목록(상시 병기)", ""]
    lines.extend(f"- {spot}" for spot in BLIND_SPOTS)
    lines.append("")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with report_path.open("a", encoding="utf-8") as fp:
        fp.write("\n".join(lines))
    print(f"\n예보 리포트 append → {report_path}")


def write_report_stub(report_path: "Path | None", spec: Path, base_ref: str, base_sha: str,
                      verdict: str, detail: "list[str]") -> None:
    """형식 red·skip 도 리포트에 사유를 남긴다(침묵 금지) — 예보 항목 없는 축약판."""
    if report_path is None:
        return
    now: str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines: "list[str]" = [
        "",
        f"## pre-gate 예보 — {now} · {spec.name}",
        "",
        f"- 기준선 SHA: `{base_sha}` (--base {base_ref}) · 프로필: auto · 모드: 관찰({MODE})",
        f"- {NO_SUBSTITUTE}",
        f"- 판정: {verdict}",
        "",
    ]
    lines.extend(f"- {item}" for item in detail)
    lines.append("")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with report_path.open("a", encoding="utf-8") as fp:
        fp.write("\n".join(lines))


# ── main ────────────────────────────────────────────────────────────────────

def main(argv: "list[str]") -> int:
    ap: _UsageParser = _UsageParser(add_help=True, description="design-spec pre-gate 예보 실행기")
    ap.add_argument("spec", help="설계 명세 markdown(기계 블록 §4 포함)")
    ap.add_argument("target", help="대상 저장소 루트(git)")
    ap.add_argument("--base", default="HEAD", help="사본 기준 git ref(기본 HEAD)")
    ap.add_argument("--report", default=None, help="예보 리포트 append 경로(D4)")
    ap.add_argument("--python", dest="python_bin", default=sys.executable,
                    help="검사기 인터프리터(대상 venv — 기본 sys.executable)")
    ap.add_argument("--keep", action="store_true", help="격리 사본·스크래치 보존(디버그)")
    ns: argparse.Namespace = ap.parse_args(argv)

    spec_path: Path = Path(ns.spec).resolve()
    repo: Path = Path(ns.target).resolve()
    report_path: "Path | None" = Path(ns.report).resolve() if ns.report else None
    if not spec_path.is_file():
        print(f"실행 불능: 명세 파일 없음 — {spec_path}", file=sys.stderr)
        return 1
    if not (repo / ".git").exists():
        print(f"실행 불능: git 저장소가 아니다 — {repo} (차분 예보는 git 앵커가 전제다)", file=sys.stderr)
        return 1

    rev: "subprocess.CompletedProcess[bytes]" = _git(repo, "rev-parse", "--verify",
                                                     f"{ns.base}^{{commit}}", check=False)
    if rev.returncode != 0:
        print(f"실행 불능: --base {ns.base!r} resolve 불능 — "
              f"{rev.stderr.decode('utf-8', 'replace').strip()}", file=sys.stderr)
        return 1
    base_sha: str = rev.stdout.decode("ascii").strip()

    gap: "str | None" = _interpreter_gap_reason(repo, ns.python_bin)
    if gap is not None:
        print(f"실행 불능: {gap}", file=sys.stderr)
        return 1

    text: str = spec_path.read_text(encoding="utf-8")
    plan_result: "tuple[Plan | None, list[str]]" = parse_spec(text)
    plan: "Plan | None" = plan_result[0]
    errors: "list[str]" = plan_result[1]
    if errors:
        print(f"형식 red — {len(errors)}건 (기계 블록이 규범 문법 밖이다 · architect 반송 재료):")
        for err in errors:
            print(f"  {err}")
        write_report_stub(report_path, spec_path, ns.base, base_sha, "형식 red", errors)
        return 3
    if plan is None:
        reason: str = "skip — machine 블록 부재(<!-- machine: file-plan --> 없음): 구형 명세 한정 조항"
        print(reason)
        write_report_stub(report_path, spec_path, ns.base, base_sha, "skip", [reason])
        return 4

    scratch: Path = Path(tempfile.mkdtemp(prefix="design-pregate-"))
    copy: Path = scratch / "copy"
    try:
        copy.mkdir(parents=True)
        _extract_archive(repo, base_sha, copy)
        overlaid: "list[str]" = _overlay_dirty(repo, copy)
        _git(copy, "init", "-q")
        _git(copy, "add", "-A")
        _git(copy, "commit", "-q", "-m", "pregate-anchor", "--allow-empty")

        try:
            mat: "dict[str, list[str]]" = materialize(copy, plan)
        except FormError as exc:
            print(f"형식 red — {exc}")
            write_report_stub(report_path, spec_path, ns.base, base_sha, "형식 red", [str(exc)])
            return 3

        if not mat["materialized"]:
            reason = ("skip — 실체화 0건(add/empty/remove 실효 조치 없음): "
                      "게이트를 부르지 않는다(공허 차분 가드 · 사유 명시)")
            print(reason)
            for item in mat["unsimulated"]:
                print(f"  미시뮬레이션: {item}")
            write_report_stub(report_path, spec_path, ns.base, base_sha, "skip",
                              [reason] + [f"미시뮬레이션: {x}" for x in mat["unsimulated"]])
            return 4

        print(f"# design_pregate — 예보 실행 · 기준선 {base_sha[:12]} (--base {ns.base}) · "
              f"모드 관찰({MODE})")
        print(f"({NO_SUBSTITUTE})")
        print(f"실체화 {len(mat['materialized'])}건 · dirty overlay {len(overlaid)}건 · "
              f"미시뮬레이션 {len(mat['unsimulated'])}건 · already-built {len(mat['already_built'])}건")

        gate_result: "tuple[int, list[str], str]" = run_gate(copy, scratch, ns.python_bin)
        gate_exit: int = gate_result[0]
        attributed: "list[str]" = gate_result[1]
        print("\n" + gate_result[2].rstrip())

        verdict: str = ("예보 green — P/S/I급 결정 계약 위반 예보 0(«설계 검증됨» 아님)"
                        if gate_exit == 0 else
                        f"예보 red — P/S/I급 결정 계약 위반 예보 {len(attributed)}건")
        print(f"\n== 예보 항목 {len(attributed)}건 ==")
        for line in attributed:
            print(f"  `{_stable_id(line)}` {line}")
        for note in plan.notes:
            print(f"  채널 메모: {note}")
        print(f"\n판정: {verdict}")
        if report_path is not None:
            write_report(report_path, spec_path, ns.base, base_sha, verdict,
                         attributed, mat, plan.notes)
        return 0 if gate_exit == 0 else 2
    except RunError as exc:
        print(f"실행 불능: {exc}", file=sys.stderr)
        return 1
    finally:
        if ns.keep:
            print(f"(--keep) 격리 사본 보존: {scratch}")
        else:
            shutil.rmtree(scratch, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
