#!/usr/bin/env python3
"""design-spec «pre-gate» 예보 실행기 — G1 승인 전 결정적 검증 게이트 (차단 모드).

왜 있나(설계 정본: workspace/design/2026-09-01-pregate-design.md v4 — §3 D1~D4·§4·§8 ⑷):
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
  3′) 실존  — boundary-imports 행 **전부**를 실체화 뒤의 사본 위에서 3단 판정한다(읽기
              전용 — 스텁·게이트 무접촉): ⑴ 모듈 부재 · ⑵ 자리표시자 · ⑶ 심볼 미정의.
              결손은 registry 규칙 귀속이 아니라 별도 채널(안정 ID `e-…`)로 보고한다.
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
                   1행 = `경로::Symbol[(Base)][ {필드, …}]`     (Symbol = 대문자 또는 `_`+대문자
                                                              선두 — 사설 보조 타입 `_Symbol` 도 클래스)
                       | `경로::Symbol.method(파라미터)[ -> 반환]`   (선행 클래스 행 필수)
                       | `경로::snake_함수[(파라미터)][ -> 반환]`   (소문자 선두 — `_helper` 포함)
                   필드 = `name: Type[ = default]` | `NAME = "literal"`(enum 멤버)
                        | `name = <식>`(Django 필드 대입식 등) — bare 이름은 형식 red.
                   미등재 파일 = 심볼 부재(fail-closed).
                   마이그레이션 칸(`migrations/NNNN_*.py`)은 symbols 결손 시 정형(Migration 클래스 1 ·
                   `0001_` 만 `initial = True`)으로 보충하고 `migrations/__init__.py` 는 빈 파일이다.
  boundary-imports `<!-- machine: boundary-imports -->` + ```imports 펜스.
                   1행 = `<소비 파일 경로><탭|2+공백><import 문 그대로>`.
                   행 전부가 «계약 실존» 3단 판정을 받는다 — 소비 파일의 태그·등재 여부와
                   무관(update 소비자 포함 · 스텁 전사는 add 소비자만). 판정 기준은 **이 브랜치**의
                   격리 사본(기준선 + dirty overlay + 이 명세의 add)이다: 저장소 밖(표준·서드파티)은
                   검사 밖 · 이 명세가 add 하는 대상은 자기 해소(⑶ 생략 — symbols 채널 소관 · 승격
                   폴더 부품 포함) · file-plan `update` 대상의 이름은 그 칸의 symbols 선언이면 자기
                   update 해소(S′)·현재 표면에 있으면 실존 확인·둘 다 아니면 판정 불능(표면은 이
                   명세 이후 상태 — ⑵⑶ 비적용) · ⑵ 는 이름 import(`from M import n`)의 대상 M 이 모듈
                   실현일 때만(모듈 import·패키지 `__init__` 은 ImportError 가 아니다). 세미콜론 복합행은
                   문 전부 판정. 결손은 권고·비차단.
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
                        [--report <경로>] [--python <검사기 인터프리터>] [--keep] [--block-hash]
                        [--check-report <pregate-report.md>]
exit 0 = 예보 green · 2 = 예보 red(계약 실존 결손은 병기) · 3 = 형식 red(파싱 오류 · machine 블록
부재·공허 · add/empty 충돌 · update/remove 대상 기준선 부재 · 금지 경로 · 태그 이중 서술) · 4 = skip(실체화 0·
결손 0 — 공허 차분 가드 · 사유 명시) · 5 = 계약 실존 결손 ≥1 ∧ (귀속 0 ∨ 실체화 0)(권고·비차단 —
실존 채널의 차단 여부는 별도 게이트) · 1 = 실행 불능(venv/인터프리터·git 실패). 어느 경우도 침묵 없음 —
모든 exit 0/2/3/4/5 경로가 `요약:` 1행을 낸다(배너 1행의 기계 출처).
차단 모드(2026-09-03 승격): 판정·exit 는 모드에 의존하지 않는다 — 차단의 실체는 Coordinator 규범(red 는
architect 반송 의무)과 아래 `--check-report`(그 의무 이행의 결정적 대조)·회피 경로 봉쇄(블록 부재·공허 =
형식 red · update 대상 기준선 부재 = 형식 red — «add 를 update 로 재라벨해 실체화 0 으로 도피» 봉쇄)다.
`--block-hash` 는 기계가독 블록 해시(sha256[:12] — 파서와 같은 추출)만 출력하고 exit 0 —
Coordinator 의 캐시 skip 대조 전용(판정 무접촉). 매 실행 리포트 헤더가 같은 값을 병기한다.
`--check-report <리포트>` 는 리포트 최신성·처분 완결을 대조만 한다(출력 전용 · git 0회 · 판정 무접촉):
마지막 `## pre-gate 예보 — ` 절의 헤더 블록 해시 = 이 명세의 해시 ∧ 그 판정이 형식 red 가 아님 ∧ 예보 red 면
`### 예보 항목` 의 안정 ID 전건에 그 절 이후 `` `<ID>` `` + `**ignored**`|`**filtered**` 처분 행이 있음
(`corrected` 는 불인정 — 재실행 결과가 곧 최종본). exit 0 = 정합(배너·G2 근거 가능) · 3 = 불비(stale ·
형식 red 미해소 · 처분 미기재 · 해시 토큰 없는 구판 헤더) · 1 = 리포트 부재·절 부재·헤더 행 부재.
`--base` 명시(재발화 판형 — Phase 2 진입 후 명세 개정 재실행): 기준선 트리에 없던 계획 add 가
오버레이에 실존하면 «기실현 add»다 — 앵커 커밋 «전»에 사본에서 걷어내고(앵커 스냅숏 L 무오염)
스텁으로 실체화해 already-built 에 «기실현 — 스텁 대체 예보»로 기록한다(커밋된 add 와 같은 예보 —
같은 ID·같은 exit). 기준선 트리에 실존하는 add 는 여전히 형식 red. 미지정(HEAD 기본)은 종전과 판정
(exit·귀속·ID) 동일 — 집계 행 문면은 판과 함께 변한다.
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
    import checker_target as ct  # noqa: E402  — 자리표시자 술어·슬롯 실현(계약 실존 ⑵ — 재구현 금지)
except ImportError:  # 데이터·술어 모듈 없이는 골격 실체화·실존 판정 불가 — fail-closed(실행 불능)
    print("실행 불능: standard_tree.py / checker_target.py 를 찾지 못했다 — 실행기와 같은 폴더에 있어야 한다",
          file=sys.stderr)
    sys.exit(1)

MODE: str = "enforce"  # 차단 모드 상수(설계 §10 M2 · 2026-09-03 승격) — red 는 architect 반송 의무(Coordinator 규범)
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
    r"^(_?[A-Z]\w*)\.([A-Za-z_]\w*)\((.*)\)\s*(?:->\s*(\S.*?))?\s*$")
_FUNC_RE: "re.Pattern[str]" = re.compile(
    r"^([a-z_]\w*)\s*(?:\((.*)\))?\s*(?:->\s*(\S.*?))?\s*$")
_CLASS_HEAD_RE: "re.Pattern[str]" = re.compile(r"^(_?[A-Z]\w*)\s*(?:\((.*)\))?\s*$")
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
    # symbols 채널이 이 경로에 선언한 최상위 이름(클래스·함수·메서드 행의 owner) — 태그 무관 기록. `update` 칸은
    # 스텁 전사 밖이지만 계약 실존의 «자기 update 해소»(S′) 근거가 된다(5단계 리뷰 MAJOR B).
    declared: "list[str]" = field(default_factory=list)


@dataclass
class ImportRow:
    """boundary-imports 1행 원문 — 소비 파일의 태그·등재 여부와 무관하게 보존한다(계약 실존 판정의 입력)."""
    consumer: str
    stmt: str


@dataclass
class Plan:
    """명세 1부의 전사 결과 — 실체화 입력의 전부(산문 추론 재료 0)."""
    entries: "dict[str, PlanEntry]" = field(default_factory=dict)
    notes: "list[str]" = field(default_factory=list)  # 고아 채널 행·미반영 결합(침묵 금지)
    import_rows: "list[ImportRow]" = field(default_factory=list)  # 계약 실존 판정 입력(전 행 — 스텁 전사와 별개)


@dataclass
class ExistenceDefect:
    """계약 실존 결손 1항목 — 정체성은 (모듈, 이름)이고 단계(⑴⑵⑶)는 현재 상태다(소비자는 합친다)."""
    stage: str    # ⑴ | ⑵ | ⑶
    module: str   # 절대 점 경로(상대 import 는 소비 파일 기준 해소)
    name: str     # import 한 이름 — 모듈 import 는 ""
    detail: str   # 문면: 모듈 부재 · 자리표시자(형태 — 출처) · 심볼 미정의 `n`
    consumers: "list[str]" = field(default_factory=list)


@dataclass
class ExistenceReport:
    """계약 실존 집계 — 행 R · 이름 판정 T = K + S + S′ + X + U + 결손.

    T 는 **이름 단위**다(`import a, b` = 2 · `from M import x, y` = 2 · `import *` = 1) — 이름을 셀 수 없는 행(문법 불량·
    비-import 문)만 행당 1 로 센다. 세미콜론 복합행은 문 전부를 순회한다.
    """
    rows: int = 0         # R
    judged: int = 0       # T
    confirmed: int = 0    # K 실존 확인
    self_add: int = 0     # S 자기 add 해소(⑶ 생략 — symbols 채널 소관)
    self_update: int = 0  # S′ 자기 update 해소(update 대상 칸의 symbols 선언 이름 — 표면은 이 명세 이후 상태)
    outside: int = 0      # X 저장소 밖(검사 밖)
    undecidable: int = 0  # U 판정 불능(사유 병기)
    defective: int = 0    # 결손(이름 단위 — 항목은 (모듈, 이름) 합치기)
    undecidable_notes: "list[str]" = field(default_factory=list)
    defects: "list[ExistenceDefect]" = field(default_factory=list)


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
        m: "re.Match[str] | None" = _MARKER_RE.search(lines[i])
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
        fm: "re.Match[str] | None" = _FENCE_OPEN_RE.match(lines[j].strip()) if j < len(lines) else None
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
        m: "re.Match[str] | None" = _TAG_RE.match(line)
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
    mm: "re.Match[str] | None" = _METHOD_RE.match(rest)
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
    # 분류식: 소문자 선두 = 함수 · 대문자 또는 `_`+대문자 선두 = 클래스(사설 보조 타입도 클래스다 —
    # `_Item {…}`·`_Item(Base)` 를 함수로 흡수하면 무경고 함수 스텁이 검사기의 사설 면제 경로를 비껴간다).
    is_function: bool = head[:1].islower() or (head[:1] == "_" and not head[1:2].isupper())
    if is_function:
        if fields_part is not None:
            errors.append(f"symbols 행 파싱 불가({where}): 함수에 필드 목록을 쓸 수 없다"
                          "(클래스는 대문자 또는 `_`+대문자 선두)")
            return None
        fm: "re.Match[str] | None" = _FUNC_RE.match(head)
        if fm is None:
            errors.append(f"symbols 행 파싱 불가({where}): `{head}`")
            return None
        return Symbol(name=fm.group(1), base="", kind="function",
                      params=(fm.group(2) or "").strip(), ret=(fm.group(3) or "").strip())
    cm: "re.Match[str] | None" = _CLASS_HEAD_RE.match(head)
    if cm is None:
        errors.append(f"symbols 행 파싱 불가({where}): `{head}`")
        return None
    sym: Symbol = Symbol(name=cm.group(1), base=(cm.group(2) or "").strip())
    for chunk in _split_top(fields_part or ""):
        if _FIELD_RE.match(chunk) is None:
            errors.append(f"symbols 필드 파싱 불가({where}): `{chunk}` — "
                          "`name: Type[ = default]` · `NAME = \"literal\"` · `name = <식>`"
                          "(Django 필드 대입식 등)만 허용 — 타입도 값도 없는 bare 이름 불가")
            continue
        sym.fields.append(chunk)
    return sym


def _parse_symbols(rows: "list[str]", plan: Plan, errors: "list[str]") -> None:
    """```symbols 펜스 → PlanEntry.symbols 결합. 메서드 행은 선행 클래스 행이 필수다."""
    for raw in rows:
        line: str = raw.strip()
        if not line or line.startswith("#"):
            continue
        m: "re.Match[str] | None" = _SYM_LINE_RE.match(line)
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
        declared_name: str = parsed.name.split(".", 1)[0]  # 메서드 행은 owner 클래스 이름
        if declared_name not in entry.declared:
            entry.declared.append(declared_name)
        if entry.tag != "add":
            plan.notes.append(f"symbols 미반영(비-add `{entry.tag}` 칸 — 스텁 전사 밖 · update 대상이면 계약 실존의 "
                              f"«자기 update 해소» 근거로만 쓴다): {path}")
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
    """```imports 펜스 → Plan.import_rows 전 행 보존(계약 실존 판정 입력) + PlanEntry.imports 결합(add 소비자만 —
    스텁 전사 원문 그대로). 비-add·미등재 소비자의 행은 스텁에 실리지 않을 뿐 실존 판정에는 포함된다(kkebi S2 —
    update 소비자가 상류 계약을 소비하는 판형)."""
    for raw in rows:
        line: str = raw.strip()
        if not line or line.startswith("#"):
            continue
        m: "re.Match[str] | None" = _IMPORT_ROW_RE.match(line)
        if m is None:
            errors.append(f"boundary-imports 행 파싱 불가: `{line}` — "
                          "`<경로><탭|2+공백><import 문>` 형식이어야 한다")
            continue
        path: str = m.group(1)
        stmt: str = m.group(2).strip()
        plan.import_rows.append(ImportRow(consumer=path, stmt=stmt))
        entry: "PlanEntry | None" = plan.entries.get(path)
        if entry is None:
            plan.notes.append(f"boundary-imports 스텁 미반영(file-plan 미등재 — 실존 판정에는 포함): {path}")
            continue
        if entry.tag != "add":
            plan.notes.append(f"boundary-imports 스텁 미반영(비-add `{entry.tag}` 칸 — 실존 판정에는 포함): {path}")
            continue
        if stmt not in entry.imports:
            entry.imports.append(stmt)


def _parse_exception_map(rows: "list[str]", plan: Plan, errors: "list[str]") -> None:
    """```exceptions 펜스 → raise 창구 스텁에 `raise <예외>()` 1줄 합성 재료(#456 처분)."""
    for raw in rows:
        line: str = raw.strip()
        if not line or line.startswith("#"):
            continue
        m: "re.Match[str] | None" = _EXC_ROW_RE.match(line)
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


def _signals_rows(text: str) -> "list[str]":
    """영구 테스트 입장 표(정본 6열 header) 데이터 행의 원문 목록 — 파서와 블록 해시가 같은 스캔을 쓴다.

    header 행·구분선은 제외하고 그 뒤 연속하는 `|` 행을 문서 순서로 모은다(표가 여럿이면 이어 붙인다).
    """
    lines: "list[str]" = text.splitlines()
    rows: "list[str]" = []
    i: int = 0
    while i < len(lines):
        row: str = lines[i].strip()
        if row.startswith("|") and tuple(c.lower() for c in _cells(row)) == SIGNALS_HEADER:
            i += 1
            if i < len(lines) and re.fullmatch(r"[|\s:-]+", lines[i].strip() or "x"):
                i += 1  # 구분선
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(lines[i])
                i += 1
            continue
        i += 1
    return rows


def _parse_signals(text: str, plan: Plan) -> None:
    """영구 테스트 입장 표(정본 6열 header)의 owner/path 셀에서 [신규 4] 어노테이션 전사.

    어노테이션이 하나도 없는 행은 «물리 신호 없음»과 같으므로 결합하지 않는다(fail-closed).
    """
    for raw in _signals_rows(text):
        cells: "list[str]" = _cells(raw)
        if len(cells) != len(SIGNALS_HEADER):
            plan.notes.append(f"입장 표 행 열 수 불일치(무시): {cells[:1]}")
            continue
        cell: str = cells[5]
        markers_m: "re.Match[str] | None" = _ANN_MARKERS_RE.search(cell)
        base_m: "re.Match[str] | None" = _ANN_BASE_RE.search(cell)
        client_m: "re.Match[str] | None" = _ANN_CLIENT_RE.search(cell)
        if markers_m is None and base_m is None and client_m is None:
            continue  # 무기재 = 물리 신호 없음
        tick: "re.Match[str] | None" = re.search(r"`([^`]+)`", cell)
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


def block_hash(text: str) -> str:
    """기계가독 블록 해시 — 기계 블록 4종 + 영구 테스트 입장 표를 **파서와 같은 정규식·스캔**으로
    추출해 문서 순서 원문(verbatim)으로 이어 붙인 sha256[:12]. 출력 전용(판정 무접촉·git 0회·OS 무관).

    Coordinator 의 캐시 skip 판형(pre-gate 문단): `--block-hash` 값이 직전 실행 리포트 헤더의
    `블록 해시` 와 같을 때만 재실행을 skip 할 수 있다 — 같은 입력이면 같은 값, 산문만 바뀌면 같은 값,
    블록 한 글자가 바뀌면 다른 값이다(원문 기준이라 공백 변경도 재실행 쪽으로 기운다 — 안전 방향).
    """
    blocks: "dict[str, list[str]]" = _machine_blocks(text, [])
    parts: "list[str]" = []
    for name in MACHINE_FENCES:
        parts.append(f"<!-- machine: {name} -->")
        parts.extend(blocks.get(name, []))
    parts.append("<!-- physical-signals -->")
    parts.extend(_signals_rows(text))
    return hashlib.sha256("\n".join(parts).encode("utf-8")).hexdigest()[:12]


def plugin_version() -> str:
    """플러그인 버전 probe — 설치 레이아웃 2경로(Claude `<plugin>/.claude-plugin/plugin.json` ·
    Codex `<plugin>/skills/dddjango/scripts` 기준 `parents[2]/.codex-plugin/plugin.json`).
    실패는 `(unknown)` — 판정 영향 0(리포트 헤더 스탬프 전용). registry_gate.py 도 같은 probe 를
    각자 보유한다(두 스크립트는 독립 파일 — 러너 유닛이 동치를 가드한다)."""
    candidates: "list[Path]" = [SCRIPTS_DIR.parent / ".claude-plugin" / "plugin.json"]
    if len(SCRIPTS_DIR.parents) > 2:
        candidates.append(SCRIPTS_DIR.parents[2] / ".codex-plugin" / "plugin.json")
    for manifest in candidates:
        try:
            version: object = json.loads(manifest.read_text(encoding="utf-8")).get("version")
        except (OSError, ValueError, AttributeError):
            continue
        if isinstance(version, str) and version:
            return version
    return "(unknown)"


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
    # 마이그레이션 정형 보충(값 축 유도 3행째): `__init__.py` 는 빈 파일이라 어떤 채널 전사도 싣지
    # 않고, `NNNN_*.py` 는 symbols 결손일 때만 정형으로 보충한다 — 그 경우 imports/raises 전사는
    # 정형에 실리지 않으므로 채널 메모로 남기고 비운다(침묵 금지). symbols 전사가 있으면 전사 우선.
    for entry in plan.entries.values():
        if entry.tag != "add":
            continue
        is_init: bool = _MIGRATION_INIT_RE.match(entry.path) is not None
        is_file: bool = _MIGRATION_FILE_RE.match(entry.path) is not None
        if not (is_init or is_file):
            continue
        dropped: "list[str]" = []
        if is_init and entry.symbols:
            dropped.append(f"symbols {len(entry.symbols)}")
        if (is_init or not entry.symbols) and entry.imports:
            dropped.append(f"imports {len(entry.imports)}")
        if (is_init or not entry.symbols) and entry.raises:
            dropped.append(f"raises {len(entry.raises)}")
        if not dropped:
            continue
        what: str = "빈 파일" if is_init else "정형 보충(symbols 결손)"
        plan.notes.append(f"마이그레이션 {what} — 채널 전사 무시(도구 산출물 #593 · {', '.join(dropped)}): {entry.path}")
        if is_init:
            entry.symbols = []
        entry.imports = []
        entry.raises = []
    return plan, errors


# ── 스텁 렌더러 — D2 규약(본문은 `...`/`raise NotImplementedError` 뿐) ─────────

_SNAKE_ACRONYM_RE: "re.Pattern[str]" = re.compile(r"([A-Z]+)([A-Z][a-z])")
_SNAKE_BOUNDARY_RE: "re.Pattern[str]" = re.compile(r"([a-z\d])([A-Z])")
_MODEL_DIR_RE: "re.Pattern[str]" = re.compile(r"^application/([^/]+)/driven_layer/django_[^/]+/models/[^/]+\.py$")
# 마이그레이션 칸 — 위치 무관(오배치 진탐은 경로 기반 검사기 #336/#325/#81 소유 — 내용 불문이라 보존).
# 파일 이름 꼴은 check-mechanism-ownership `MIGRATION_NAME_RE`(`^\d{4}_\w+\.py$`)와 동형.
_MIGRATION_INIT_RE: "re.Pattern[str]" = re.compile(r"^(?:.+/)?migrations/__init__\.py$")
_MIGRATION_FILE_RE: "re.Pattern[str]" = re.compile(r"^(?:.+/)?migrations/(\d{4}_\w+)\.py$")


def _snake(name: str) -> str:
    """CamelCase → snake_case — check-db-table.py `_snake` 의 2-pass regex 문자 복제.
    유도값의 byte 동치가 계약이다(재구현 드리프트 = 신규 #630 아티팩트)."""
    s: str = _SNAKE_ACRONYM_RE.sub(r"\1_\2", name)
    s = _SNAKE_BOUNDARY_RE.sub(r"\1_\2", s)
    return s.lower()


def _derived_db_table(path: str, class_name: str) -> "str | None":
    """모델 칸의 `*Model` 클래스 → #630 유도 규칙의 기대 db_table. 그 외 None.
    label 은 경로 bc(정형 label)와 동일 가정 — 커스텀 label 계획의 유도 불일치는 사각 병기."""
    m: "re.Match[str] | None" = _MODEL_DIR_RE.match(path)
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


def _migration_stub(entry: PlanEntry) -> "str | None":
    """마이그레이션 칸의 정형 보충(값 축 유도 3행째 — 결손 시만·전사 우선). 그 외 칸은 None.

    `migrations/__init__.py` 는 진짜 빈 파일이다(#593 — 도구가 빈 파일로 만든다 · 헤더도 방출하지
    않는다). `migrations/NNNN_*.py` 는 symbols 전사가 없을 때만 makemigrations 산출물의 부분집합
    모양으로 보충한다 — `Migration` 클래스 정확히 1 · 무어노테이션 `Assign`(검사기는 `AnnAssign`
    을 #593 으로 본다) · `initial = True` 는 `0001_` 에만 · `django.db` import 는 비-저장소.
    symbols 전사가 있으면 기존 렌더러가 전사 그대로 싣는다(`migrations.Migration` base 는
    BASE_IMPORTS 밖이라 import 합성 0 — compile 은 이름을 해소하지 않는다).
    """
    if _MIGRATION_INIT_RE.match(entry.path):
        return ""
    m: "re.Match[str] | None" = _MIGRATION_FILE_RE.match(entry.path)
    if m is None or entry.symbols:
        return None
    body: "list[str]" = ['"""pre-gate 팬텀 스텁 — 마이그레이션 정형(도구 산출물 모양 · #593)."""',
                         "from django.db import migrations", "", "",
                         "class Migration(migrations.Migration):"]
    if m.group(1).startswith("0001_"):
        body.append("    initial = True")
    body += ["    dependencies = []", "    operations = []"]
    return "\n".join(body) + "\n"


def render_stub(entry: PlanEntry) -> str:
    """PlanEntry 하나 → 팬텀 스텁 본문. 산문 추론 재료 0 — 전사·상수·처분표뿐이다."""
    canonical: "str | None" = _migration_stub(entry)
    if canonical is not None:
        return canonical
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


def _compile_hint(entry: PlanEntry) -> str:
    """compile 실패의 흔한 원인 힌트 — `_`+대문자 선두는 클래스로 분류되므로 `_Helper(x: int)` 처럼
    파라미터를 base 자리에 적으면 `class _Helper(x: int):` 가 되어 문법 밖이다(사설 함수는 소문자 선두)."""
    if any(sym.kind == "class" and sym.name.startswith("_") and ":" in sym.base
           for sym in entry.symbols):
        return " · 힌트: `_`+대문자 선두는 클래스로 분류된다 — 사설 함수는 소문자 선두로 적는다"
    return ""


def lift_realized_adds(copy: Path, plan: Plan, explicit_base: bool,
                       in_baseline: "frozenset[str]") -> "frozenset[str]":
    """재발화 판형(`--base` 명시)의 «기실현 add» — 오버레이 «뒤»·앵커 커밋 «전»에 사본에서 걷어낸다.

    기실현 add = `explicit_base ∧ tag add ∧ 기준선 트리 부재 ∧ 오버레이(worktree−HEAD) 실존`. 실물이 앵커
    스냅숏(L)에 남으면 그 자리의 스텁 진단이 N∖L 이 아니라 L∩N(잔존)으로 빠져 예보가 사라진다 — 커밋된 add
    (사본 밖 → 스텁)와 미커밋 add(오버레이)의 예보를 같게 만드는 유일한 자리다(5단계 리뷰 MAJOR A). 걷어낸
    경로는 `materialize` 가 스텁으로 실체화하고 already-built 에 «기실현»으로 기록한다. `--base` 미지정이면
    공집합(기본 경로 판정 동일).
    """
    if not explicit_base:
        return frozenset()
    lifted: "set[str]" = set()
    for path, entry in plan.entries.items():
        target: Path = copy / path
        if entry.tag in ("add", "empty") and path not in in_baseline and (target.is_file() or target.is_symlink()):
            target.unlink()
            lifted.add(path)
    return frozenset(lifted)


def materialize(copy: Path, plan: Plan, *, realized: "frozenset[str]" = frozenset(),
                base_short: str = "", promoted: "frozenset[str]" = frozenset()) -> "dict[str, list[str]]":
    """태그 의미론(D2)대로 사본 위에 팬텀을 겹친다 — add 실존 충돌은 FormError.

    `promoted` = `baseline_form_errors` 가 승격 형태 예외로 통과시킨 update 경로(미시뮬레이션 문면만 다르다).

    **재발화 판형(`--base` 명시 — Phase 2 진입 후 명세 개정 재실행)**: `realized` 는 `lift_realized_adds` 가
    앵커 커밋 전에 사본에서 걷어낸 «기실현 add» 경로다 — 여기서는 다른 add 와 똑같이 스텁으로 실체화하고
    (materialized 에 계수) already-built 에도 «기실현 — 스텁 대체 예보»로 기록한다(이중 기재는 의도 —
    `empty(기실현)` 은 materialized 에 안 실리는 것과 구별). 사본에 실존하는 add 는 기준선 트리 실존(계획↔실물
    모순)뿐이므로 여전히 형식 red 다. `--base` 미지정 경로는 판정(exit·귀속·ID) 동일이다 — 리포트의 집계 행 문면
    (계약 실존 «자기 update 해소» 열 등)은 판과 함께 변한다.

    반환: materialized / already_built / unsimulated 목록(리포트 재료 — 침묵 금지).
    """
    report: "dict[str, list[str]]" = {"materialized": [], "already_built": [], "unsimulated": []}
    for entry in plan.entries.values():
        target: Path = copy / entry.path
        if entry.tag == "add":
            if target.exists():
                raise FormError(f"add 충돌(실존): {entry.path} — 계획과 실물의 모순은 그 자체가 발견이다")
            if entry.path in realized:
                report["already_built"].append(
                    f"add(기실현 — 기준선 {base_short} 부재·오버레이 실존 → 앵커 스냅숏에서 제외·스텁 대체 예보 · "
                    f"실체화 목록에도 계수): {entry.path}")
            stub: str = render_stub(entry)
            try:
                compile(stub, entry.path, "exec")  # symtable까지 — 중복 인자류는 ast.parse 가 못 잡는다
            except (SyntaxError, ValueError) as exc:
                detail: str = getattr(exc, "msg", None) or str(exc)
                raise FormError(f"스텁 렌더 파싱 불가: {entry.path} — {detail} "
                                f"(기계 블록 전사 내용이 파이썬 문법 밖이다){_compile_hint(entry)}")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(stub, encoding="utf-8")
            report["materialized"].append(entry.path)
        elif entry.tag == "empty":
            # add 와 같은 «새 파일» 태그 — 기준선 실존은 baseline_form_errors 가 앞서 형식 red 로 세우고, `--base` 재발화의
            # 오버레이 실존(기실현)은 lift_realized_adds 가 걷어내 여기서 빈 파일로 다시 쓴다(실체화 계수 · 도피 봉쇄).
            if target.exists():
                raise FormError(f"empty 충돌(실존): {entry.path} — 계획과 실물의 모순은 그 자체가 발견이다")
            if entry.path in realized:
                report["already_built"].append(
                    f"empty(기실현 — 기준선 {base_short} 부재·오버레이 실존 → 앵커 스냅숏에서 제외·빈 파일 대체 · "
                    f"실체화 목록에도 계수): {entry.path}")
            target.parent.mkdir(parents=True, exist_ok=True)
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
            if entry.path in promoted:
                report["unsimulated"].append(
                    f"update(승격 형태 실존 — 예외 통과 · 파일 `<칸>.py` 는 기준선 부재 · 실존 채널은 ⑴ 판정): {entry.path}")
            else:
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
    m: "re.Match[str] | None" = _REQ_PY_RE.search(pyproject.read_text(encoding="utf-8", errors="replace"))
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
    m: "re.Match[str] | None" = _ATTR_LINE_RE.search(line)
    rule: str = m.group(1) if m else "?"
    where: str = m.group(2).split(":", 1)[0] if m else line
    return hashlib.sha256(f"#{rule}+{where}".encode("utf-8")).hexdigest()[:12]


# ── 계약 실존 — boundary-imports 3단 판정(읽기 전용 · 스텁·게이트 무접촉) ─────────

_TYPE_ALIAS_NODE: "type | None" = getattr(ast, "TypeAlias", None)  # PEP 695 `type X = …` — py3.12+
_TRY_NODES: "tuple[type, ...]" = tuple(t for t in (ast.Try, getattr(ast, "TryStar", None)) if t is not None)


def _repo_root_packages() -> "frozenset[str]":
    """표준 트리 최상위(depth-0) 칸의 첫 세그먼트 중 미해소 `<…>` 가 아닌 것 → {application, framework}.
    `<project>/`(settings 패키지)는 사본 실존으로 잡는다(`_is_repo_target`). 하드코딩 아님 — `standard_tree` 재사용."""
    out: "set[str]" = set()
    for row in tree.children(None):
        first: str = row.name.split("/", 1)[0]
        if not first.startswith("<"):
            out.add(first)
    return frozenset(out)


def _is_repo_target(copy: Path, top: str, plan: Plan) -> bool:
    """import 최상위 세그먼트가 이 저장소의 것인가 — 표준 트리 최상위 ∨ 사본 실존(폴더·`.py`) ∨ file-plan 첫 세그먼트.
    거짓 = «저장소 밖(표준 라이브러리·서드파티) — 검사 밖»(X 계수만)."""
    if top in _repo_root_packages():
        return True
    if (copy / top).is_dir() or (copy / f"{top}.py").is_file():
        return True
    return any(PurePosixPath(p).parts[:1] == (top,) for p in plan.entries)


def _resolve_relative(file_parts: "tuple[str, ...]", level: int,
                      module: "str | None") -> "tuple[str, ...] | None":
    """상대 import → 소비 파일 기준 절대 마디(check-context-isolation `_resolve_relative` 와 같은 산식).
    None = 저장소 루트 밖 탈출(level 과다)."""
    pkg: "list[str]" = list(file_parts[:-1])
    up: int = level - 1
    if up > len(pkg):
        return None
    base: "list[str]" = pkg[: len(pkg) - up]
    if module:
        base.extend(module.split("."))
    return tuple(base)


def _realize_module(copy: Path, parts: "list[str]", plan: Plan) -> "tuple[str, Path | None]":
    """점 경로 마디 → (실현 종류, 실현 파일). 종류 ∈ planned-add | planned-update | planned-empty | package | module |
    namespace-dir | missing.

    순서: file-plan 조회(`<parts>.py`·`<parts>/__init__.py` 두 표기 — add = 자기 add · update = 자기 update(실현 파일 =
    사본의 현재 실물 — 표면은 이 명세 이후 상태라 이름 판정은 `judge_name` 이 symbols 선언으로 가른다 · **사본에 실물이
    없으면 missing 그대로** — update 는 파일을 만들지 않으므로 부재는 ⑴ 이지 자기 해소가 아니다) · empty = 자기
    empty · 비지연 remove = missing · `remove@Ln` 은 G1 시점 상태 유지라 사본 실물로 판정) → **승격 폴더 부품**(상위
    `<parts[:-1]>.py` 가 planned-add 슬롯이면 이 마디는 그 슬롯의 승격 폴더 부품 — R-3424 «경로는 언제나 <칸>.py»
    표기의 부품이라 자기 add 해소) → `__init__.py`(패키지 — Python 은 패키지가 모듈보다 우선 · 기존 실물의 승격
    폴더도 여기: 이름 표면 = `__init__` 재수출) → `checker_target.slot_file`(슬롯 경로 → 파일 실현의 단일 술어 —
    재구현 금지) → 디렉터리만(네임스페이스 패키지 — ⑴ 통과·이름 판정 불능) → missing.
    """
    rel: str = "/".join(parts)
    for cand in (f"{rel}.py", f"{rel}/__init__.py"):
        entry: "PlanEntry | None" = plan.entries.get(cand)
        if entry is None:
            continue
        if entry.tag == "add":
            return "planned-add", None
        if entry.tag == "update":
            if (copy / cand).is_file():
                return "planned-update", copy / cand
            return "missing", None  # update 대상이 사본에 부재 = 계획↔실물 모순 — ⑴ 방향 유지(S′·K 로 세탁 금지)
        if entry.tag == "empty":
            return "planned-empty", copy / cand
        if entry.tag == "remove" and not entry.deferred_remove:
            return "missing", None
    if len(parts) >= 2:
        slot: "PlanEntry | None" = plan.entries.get("/".join(parts[:-1]) + ".py")
        if slot is not None and slot.tag == "add":
            return "planned-add", None
    init_file: Path = copy / rel / "__init__.py"
    if init_file.is_file():
        return "package", init_file
    realized: "Path | None" = ct.slot_file(copy / f"{rel}.py")
    if realized is not None:
        return "module", realized
    if (copy / rel).is_dir():
        return "namespace-dir", None
    return "missing", None


def _missing_detail(module: str, plan: Plan) -> str:
    """⑴ 문면 — 부재 모듈이 file-plan `update` 대상이면 «update 대상 부재(계획↔실물 모순)» 로 병기(update 는 파일을 만들지 않는다)."""
    rel: str = module.replace(".", "/")
    for cand in (f"{rel}.py", f"{rel}/__init__.py"):
        entry: "PlanEntry | None" = plan.entries.get(cand)
        if entry is not None and entry.tag == "update":
            return "모듈 부재 — update 대상 부재(계획↔실물 모순)"
    return "모듈 부재"


def _all_literal_names(value: "ast.expr | None") -> "set[str]":
    """`__all__ = [...]`/`(...)` 의 문자열 상수 — 승격 폴더 `__init__` 재수출 선언 2형 중 하나(mypy strict 인정)."""
    if isinstance(value, (ast.List, ast.Tuple)):
        return {e.value for e in value.elts if isinstance(e, ast.Constant) and isinstance(e.value, str)}
    return set()


def _top_level_names(path: Path) -> "tuple[set[str], bool] | None":
    """모듈 최상위 바인딩 이름 집합 + «표면 열림» 플래그 — None = 읽기·파싱 실패(판정 불능).

    바인딩: ClassDef/FunctionDef/AsyncFunctionDef · Assign(튜플 풀기 — `ast.walk` 로 Name 전부)/AnnAssign/AugAssign(`__all__ +=`) ·
    Import(`import a.b` → `a`)/ImportFrom alias(`asname or name` — 승격 폴더 `__init__` 의 `from .m import X as X` 재수출 인정) ·
    `__all__` 문자열 · `type X = …`(PEP 695 · py3.12+). 최상위 If/Try/With 본문은 재귀(`TYPE_CHECKING` 가드·try-import 관용) —
    함수·클래스 본문은 비재귀. 표면 열림 = `from … import *` 또는 모듈 `__getattr__` — 명시 바인딩에 없는 이름은 ⑶ 이 아니라
    판정 불능이다(동적 표면은 표면 밖 — 사각 병기).
    """
    try:
        module: ast.Module = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, SyntaxError, ValueError):
        return None
    names: "set[str]" = set()
    open_surface: bool = False

    def visit(body: "list[ast.stmt]") -> None:
        nonlocal open_surface
        for node in body:
            if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                names.add(node.name)
                if node.name == "__getattr__":
                    open_surface = True
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    names.update(n.id for n in ast.walk(target) if isinstance(n, ast.Name))
                if any(isinstance(t, ast.Name) and t.id == "__all__" for t in node.targets):
                    names.update(_all_literal_names(node.value))
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                names.add(node.target.id)
                if node.target.id == "__all__":
                    names.update(_all_literal_names(node.value))
            elif isinstance(node, ast.AugAssign) and isinstance(node.target, ast.Name) and node.target.id == "__all__":
                names.update(_all_literal_names(node.value))
            elif isinstance(node, ast.Import):
                names.update((a.asname or a.name).split(".", 1)[0] for a in node.names)
            elif isinstance(node, ast.ImportFrom):
                for a in node.names:
                    if a.name == "*":
                        open_surface = True
                    else:
                        names.add(a.asname or a.name)
            elif _TYPE_ALIAS_NODE is not None and isinstance(node, _TYPE_ALIAS_NODE):
                if isinstance(node.name, ast.Name):
                    names.add(node.name.id)
            elif isinstance(node, ast.If):
                visit(node.body)
                visit(node.orelse)
            elif isinstance(node, _TRY_NODES):
                visit(node.body)
                visit(node.orelse)
                visit(node.finalbody)
                for handler in node.handlers:
                    visit(handler.body)
            elif isinstance(node, (ast.With, ast.AsyncWith)):
                visit(node.body)

    visit(module.body)
    return names, open_surface


def _existence_id(module: str, name: str) -> str:
    """계약 실존 결손 안정 ID — `e-` + sha256(모듈+이름)[:12]. 단계(⑴⑵⑶)는 키 밖(⑴→⑵→해소로 변해도 ID 유지 —
    처분 라벨 추적 키). 접두 `e-` 는 예보 ID(순수 12hex)·러너 정규식과 육안·기계 모두 불충돌."""
    return "e-" + hashlib.sha256(f"{module}+{name}".encode("utf-8")).hexdigest()[:12]


def _tracked_paths(copy: Path) -> "frozenset[str] | None":
    """앵커 커밋에 실린 경로 집합(⑵ 출처 «기존 실물» 판별) — git 저장소가 아니면 None(유닛 합성 사본)."""
    if not (copy / ".git").exists():
        return None
    proc: "subprocess.CompletedProcess[bytes]" = _git(copy, "ls-files", "-z", check=False)
    if proc.returncode != 0:
        return None
    return frozenset(p for p in proc.stdout.decode("utf-8", "replace").split("\0") if p)


def _placeholder_detail(copy: Path, kind: str, file: Path, tracked: "frozenset[str] | None") -> str:
    """⑵ 문면 — 형태(0B | docstring/주석-only) + 출처(자기 `empty` | 기존 실물 | 골격 빈 칸)."""
    shape: str = "0B" if file.stat().st_size == 0 else "docstring/주석-only"
    if kind == "planned-empty":
        origin: str = "자기 `empty`"
    elif tracked is None or file.relative_to(copy).as_posix() in tracked:
        origin = "기존 실물"
    else:
        origin = "골격 빈 칸(도구 산출 — file-plan 미등재)"
    return f"자리표시자({shape} — {origin})"


def check_import_existence(copy: Path, plan: Plan) -> ExistenceReport:
    """boundary-imports 행 전부의 3단 실존 판정(읽기 전용) — materialize 뒤(자기 add 스텁·골격·`__init__` 체인·empty 가
    실존하는 상태)·실체화-0 분기 앞에 부른다.

    행마다 `ast.parse(stmt)` → `import a.b.c [as x]` 는 대상 모듈에 ⑴만(모듈 import 는 자리표시자여도 ImportError 가 아니다) ·
    `from M import n…`(level>0 은 소비 파일 기준 상대 해소)은 이름마다 **서브모듈 우선**(`M.n` 이 실현되면 모듈 import 와
    같다 — ⑴ 통과·⑵ 비적용) → 아니면 `M` 에 ⑴ → ⑵(`M` 이 모듈 실현이고 `checker_target.skeleton_placeholder` — 0B·공백·
    주석/docstring-only · 패키지 `__init__` 은 제외) → ⑶(`n ∉ _top_level_names(M)`). **planned-add 대상은 ⑴⑵⑶ 전부
    생략**(«자기 add 해소» S — symbols 문법이 모듈 상수·재수출을 표현 못 하므로 ⑶ 을 걸면 오차단 채널이 된다 · R-3426 소관).
    **planned-update 대상**(file-plan `update` 칸 — **사본에 실물이 있을 때만**; 부재면 update 는 파일을 만들지 않으므로 ⑴ 유지)은
    표면이 «이 명세 이후 상태»다 — 그 칸의 symbols 선언 이름은 «자기
    update 해소» S′(스텁 전사는 없지만 선언이 곧 계약), 미선언이면 현재 실물 표면에 있을 때만 K(update 가 그 이름을 지우는
    경우는 미탐 방향·관대 — 사각 병기), 둘 다 아니면 U(«update 대상 — 표면은 이 명세 이후 상태»); ⑵ 자리표시자는 update
    대상에 비적용(5단계 리뷰 MAJOR B — 오차단 폐쇄). 저장소 밖 최상위는 X(검사 밖). 판정 불능 U = 문법 불량 stmt(비-add
    소비자 — add 소비자는 compile 형식 red 가 별도로 잡는다) · `import *` · 상대 import 루트 탈출 · 네임스페이스
    폴더+비서브모듈 이름 · 표면 열림(`*` 재수출·`__getattr__`) · 파싱 실패 · 소비자 planned-remove · update 대상의
    미선언·미실존 이름. 세미콜론 복합행(`import a; import b`)은 문 전부를 순회한다. 결손은 (모듈, 이름) 쌍으로 합쳐
    소비자를 병기한다.
    """
    rep: ExistenceReport = ExistenceReport(rows=len(plan.import_rows))
    merged: "dict[tuple[str, str], ExistenceDefect]" = {}
    tracked: "frozenset[str] | None" = _tracked_paths(copy)

    def defect(stage: str, module: str, name: str, detail: str, consumer: str) -> None:
        rep.defective += 1
        key: "tuple[str, str]" = (module, name)
        item: "ExistenceDefect | None" = merged.get(key)
        if item is None:
            item = ExistenceDefect(stage=stage, module=module, name=name, detail=detail)
            merged[key] = item
            rep.defects.append(item)
        if consumer not in item.consumers:
            item.consumers.append(consumer)

    def undecidable(reason: str, names: int = 1) -> None:
        """U 계수는 이름 단위(T 항등식 유지) — 사유 메모는 행당 1."""
        rep.undecidable += names
        rep.undecidable_notes.append(reason)

    def judge_update_target(file: Path, module: str, name: str, consumer: str) -> None:
        """planned-update 대상의 이름 판정 — symbols 선언 S′ → 현재 표면 K → U(⑵·⑶ 비적용)."""
        entry: PlanEntry = plan.entries[file.relative_to(copy).as_posix()]
        if name in entry.declared:
            rep.self_update += 1
            return
        surface: "tuple[set[str], bool] | None" = _top_level_names(file) if file.is_file() else None
        if surface is not None and name in surface[0]:
            rep.confirmed += 1  # 현재 실물 표면 — update 가 지우는 경우는 미탐 방향(관대) 사각
            return
        undecidable(f"update 대상 — 표면은 이 명세 이후 상태(symbols 미선언·현재 표면에도 없음): "
                    f"{module} import {name} ← 소비 {consumer}")

    def judge_name(parts: "list[str]", module: str, name: str, consumer: str) -> None:
        sub_kind: str = _realize_module(copy, parts + [name], plan)[0]
        if sub_kind == "planned-add":
            rep.self_add += 1
            return
        if sub_kind != "missing":
            rep.confirmed += 1  # 서브모듈 실현(update 대상 포함) — 모듈 import 와 같다(⑵ 비적용)
            return
        kind, file = _realize_module(copy, parts, plan)
        if kind == "planned-add":
            rep.self_add += 1
            return
        if kind == "missing":
            defect("⑴", module, name, _missing_detail(module, plan), consumer)
            return
        if kind == "namespace-dir" or file is None:
            undecidable(f"네임스페이스 폴더(`__init__.py` 없음)의 비서브모듈 이름: {module} import {name} ← 소비 {consumer}")
            return
        if kind == "planned-update":
            judge_update_target(file, module, name, consumer)
            return
        if file.name != "__init__.py" and ct.skeleton_placeholder(file):
            defect("⑵", module, name, _placeholder_detail(copy, kind, file, tracked), consumer)
            return
        surface: "tuple[set[str], bool] | None" = _top_level_names(file)
        if surface is None:
            undecidable(f"파싱·읽기 실패(실행기 py{sys.version_info[0]}.{sys.version_info[1]} — 대상 requires-python "
                        f"하한 확인): {module} ← 소비 {consumer}")
            return
        if name in surface[0]:
            rep.confirmed += 1
            return
        if surface[1]:
            undecidable(f"이름 표면 열림(`import *` 재수출 또는 `__getattr__`): {module} import {name} ← 소비 {consumer}")
            return
        defect("⑶", module, name, f"심볼 미정의 `{name}`", consumer)

    def name_count(node: ast.stmt) -> int:
        """T 의 이름 단위 — import 문은 alias 수(`*` 도 1) · 그 밖의 문은 1."""
        return len(node.names) if isinstance(node, (ast.Import, ast.ImportFrom)) else 1

    def judge_stmt(node: ast.stmt, row: ImportRow) -> None:
        if isinstance(node, ast.Import):
            for alias in node.names:
                rep.judged += 1
                parts: "list[str]" = alias.name.split(".")
                if not _is_repo_target(copy, parts[0], plan):
                    rep.outside += 1
                    continue
                kind: str = _realize_module(copy, parts, plan)[0]
                if kind == "planned-add":
                    rep.self_add += 1
                elif kind == "missing":
                    defect("⑴", alias.name, "", _missing_detail(alias.name, plan), row.consumer)
                else:
                    rep.confirmed += 1  # planned-update 포함 — 모듈 import 는 실물 실존으로 족하다
            return
        if not isinstance(node, ast.ImportFrom):
            rep.judged += 1
            undecidable(f"import 문이 아니다: {row.consumer} :: {row.stmt}")
            return
        if node.level:
            resolved: "tuple[str, ...] | None" = _resolve_relative(
                PurePosixPath(row.consumer).parts, node.level, node.module)
            if not resolved:
                rep.judged += len(node.names)
                undecidable(f"상대 import 가 저장소 루트 밖으로 탈출: {row.consumer} :: {row.stmt}", len(node.names))
                return
            parts = list(resolved)
        else:
            parts = (node.module or "").split(".")
        module: str = ".".join(parts)
        if not _is_repo_target(copy, parts[0], plan):
            rep.judged += len(node.names)
            rep.outside += len(node.names)
            return
        for alias in node.names:
            rep.judged += 1
            if alias.name == "*":
                undecidable(f"`import *` — 이름 판정 밖: {row.consumer} :: {row.stmt}")
                continue
            judge_name(parts, module, alias.name, row.consumer)

    for row in plan.import_rows:
        try:
            body: "list[ast.stmt]" = ast.parse(row.stmt).body
        except (SyntaxError, ValueError):
            body = []
        consumer_entry: "PlanEntry | None" = plan.entries.get(row.consumer)
        if consumer_entry is not None and consumer_entry.tag == "remove" and not consumer_entry.deferred_remove:
            names: int = sum(name_count(n) for n in body) or 1
            rep.judged += names
            undecidable(f"소비자 제거(remove) — 판정 밖: {row.consumer} :: {row.stmt}", names)
            continue
        if not body:
            rep.judged += 1
            undecidable(f"문법 — import 문 파싱 불가(add 소비자는 compile 형식 red 가 별도로 잡는다): "
                        f"{row.consumer} :: {row.stmt}")
            continue
        for node in body:  # 세미콜론 복합행 — 문 전부(첫 문만 보면 뒤 문이 침묵 통과한다)
            judge_stmt(node, row)
    return rep


def _existence_lines(existence: ExistenceReport) -> "list[str]":
    """리포트 «계약 실존» 절 — 행 0 이어도 상시 출력(침묵 금지). 예보 항목 절과 already-built 절 사이.

    집계 행은 행 수 R 을 언제나 싣는다 — 직전 리포트 대비 «결손 소멸 ∧ R 감소»(행 삭제·소비 철회)의 대조는 Coordinator 몫
    (R-3433: 처분 `corrected(철회: <근거>)` 근거 병기 의무)."""
    e: ExistenceReport = existence
    lines: "list[str]" = [
        "",
        f"### 계약 실존 (boundary-imports 3단 · 결손 {len(e.defects)}건 · 안정 ID = e-sha256(모듈+이름)[:12])",
        "",
    ]
    for d in e.defects:
        target: str = f"{d.module} import {d.name}" if d.name else f"import {d.module}"
        lines.append(f"- `{_existence_id(d.module, d.name)}` {d.stage} {d.detail} :: {target} ← 소비 {', '.join(d.consumers)}")
    lines.append(f"- 집계: 행 {e.rows} · 이름 판정 {e.judged} · 실존 확인 {e.confirmed} · 자기 add 해소 {e.self_add} · "
                 f"자기 update 해소 {e.self_update} · 저장소 밖(검사 밖) {e.outside} · 판정 불능 {e.undecidable} · "
                 f"결손 {e.defective}(항목 {len(e.defects)})")
    for note in e.undecidable_notes:
        lines.append(f"- 판정 불능: {note}")
    if not e.defects:
        lines.append(f"- (없음) — 명세가 선언한 경계 import 계약 전건 실존(저장소 밖 {e.outside}건은 검사 밖·"
                     f"자기 add {e.self_add}건은 symbols 채널 소관·자기 update {e.self_update}건은 update 칸 symbols 선언)")
    return lines


def _print_existence(existence: ExistenceReport) -> None:
    """stdout 블록 — 리포트 절과 같은 항목·집계(배너 재료)."""
    print(f"\n== 계약 실존 결손 {len(existence.defects)}건 (boundary-imports 3단) ==")
    for line in _existence_lines(existence)[3:]:
        print(f"  {line[2:]}")


def _own_interpreter_note(repo: Path) -> "str | None":
    """실행기 자체 인터프리터 하한 검사 — 대상 `requires-python` 하한보다 낮으면 ⑶ AST 파싱이 3.12+ 문법 파일을 판정 불능으로
    흘린다(침묵은 아니다 — U 로 병기). `--python` 은 검사기 인터프리터라 별도 게이트(`_interpreter_gap_reason`)다."""
    pyproject: Path = repo / "pyproject.toml"
    if not pyproject.is_file():
        return None
    m: "re.Match[str] | None" = _REQ_PY_RE.search(pyproject.read_text(encoding="utf-8", errors="replace"))
    if m is None:
        return None
    lo: "tuple[int, int]" = (int(m.group(1)), int(m.group(2)))
    if sys.version_info[:2] >= lo:
        return None
    return (f"실행기 인터프리터 py{sys.version_info[0]}.{sys.version_info[1]} < 대상 하한 {lo[0]}.{lo[1]} — 계약 실존 ⑶ 판정의 "
            f"파싱 실패는 판정 불능으로 병기된다(실행기를 대상 venv 인터프리터로 실행하면 사라진다)")


BLIND_SPOTS: "tuple[str, ...]" = (
    "S1 C급(함수 본문·행위 규칙): 스텁 본문이 `...` 뿐이라 예보 표면 밖이다.",
    "S2 ④형(명세 내부 의미 모순·규범 과잉결정): 검출 대상이 아니다.",
    "S3 BC 내부 계층 의존(#92/#93류): 유도 삽입은 규약 준수형이라 예보 불가 · 블록에 기재된 경계 import 는 스텁에 "
    "방출되어 예보된다 — 산문에만 적힌 경계 import(블록 미기재)는 전사되지 않아 표면 밖이다.",
    "S4 앵커·상태 축: 예보 기준선은 «스텁 제외 현재 상태»다 — G2 build_anchor 차분과 다르며, "
    "HEAD 판형 게이트 결과의 G2 증거 유용은 차분 세탁으로 금지된다.",
    "S5 미시뮬레이션: update 계획·후행 remove(@Ln)는 실체화하지 않는다 — 위 목록 병기.",
    "S6 정형 보충(apps.py name/label·모델 Meta.db_table·마이그레이션 칸): 결손 시 규약 유도값을 합성한다 — 기계 블록 "
    "전사가 있으면 전사 우선이지만, «산문»으로만 규약 밖 값을 계획한 일탈은 예보 표면 밖이다.",
    "S7 기실현 add(`--base` 명시 시 — 명시 `--base HEAD` 포함): 사본 = 기준선 트리 + (worktree−HEAD) 오버레이 — 기준선 "
    "이후 커밋분은 사본에 없다. 오버레이 실존 add 는 앵커 커밋 전에 걷어내고 스텁으로 실체화해 예보하므로(앵커 스냅숏 "
    "무오염·실물 판정 혼입 0 — 커밋된 add 와 같은 ID·exit) 실물이 스텁과 다른 위반은 예보 표면 밖이고, 유일 판정자는 "
    "G2 앵커 차분이다.",
    "S8 계약 실존(boundary-imports 3단): 판정 기준은 **이 브랜치**의 격리 사본(기준선 + dirty overlay + 이 명세의 add — "
    "`--base` 명시 시 기준선 이후 커밋분은 사본에 없다: 재발화 판형)이다 — 다른 워크트리·미머지 브랜치의 실물은 보지 "
    "않는다(부재 = 결손 · 상류 소유 계약의 선행 대기는 `deferred` 처분으로 명세가 소유 레인·해소 조건을 명시한다). "
    "자기 add 대상의 이름 정의(⑶)는 symbols 채널 소관이라 생략하고, update 대상은 symbols 선언 이름을 자기 update 해소로 "
    "본다(표면은 이 명세 이후 상태). 결손은 권고·비차단(exit 5)이며 G0 선행 조건 확인·상류 머지 판단을 대체하지 않는다.",
    "S9 계약 실존 표면 밖·판정 경계(결과별): 판정 불능 U = `import *`(소비 행·재수출 표면)·`__getattr__` 표면·네임스페이스 "
    "폴더의 비서브모듈 이름·AST 파싱 실패·문법 불량 행·소비자 remove·update 대상의 미선언·미실존 이름 / 관대 K(미탐 "
    "방향) = `TYPE_CHECKING` 가드 안 바인딩(런타임 부재여도 최상위 바인딩으로 센다)·update 대상의 현재 표면 이름(update "
    "가 지우는 경우) / 검사 밖 X = 저장소 밖 패키지(표준·서드파티) / 결손 ⑴ 방향 = gitignore 된 실물(사본 밖 — 이 브랜치 "
    "추적 기준)·승격 형태 예외로 통과한 `update` 대상(update 는 파일을 만들지 않는다 — 그 외 기준선 부재 update 는 형식 "
    "red 로 앞서 선다) / 행 자체가 없다 = 동적 import"
    "(`importlib` 리터럴).",
)


def _executor_stamp(blk_hash: str) -> str:
    """리포트 헤더 스탬프 — 버전 판별(행 수 휴리스틱 폐기)과 캐시 skip 대조(블록 해시)의 단일 자리."""
    return f"실행기: design_pregate.py · dddjango v{plugin_version()} · 블록 해시 {blk_hash}"


def write_report(report_path: Path, spec: Path, base_ref: str, base_sha: str, verdict: str,
                 attributed: "list[str]", mat: "dict[str, list[str]]",
                 notes: "list[str]", blk_hash: str, existence: ExistenceReport) -> None:
    """예보 리포트 append(D4) — 헤더 상시 문구·안정 ID·계약 실존 절(상시)·사각 목록 병기."""
    now: str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines: "list[str]" = [
        "",
        f"## pre-gate 예보 — {now} · {spec.name}",
        "",
        f"- 기준선 SHA: `{base_sha}` (--base {base_ref}) — «스텁 제외 현재 상태» · "
        f"프로필: auto · 모드: 차단({MODE}) · {_executor_stamp(blk_hash)}",
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
    lines.extend(_existence_lines(existence))
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
                      verdict: str, detail: "list[str]", blk_hash: str,
                      existence: "ExistenceReport | None" = None) -> None:
    """형식 red·skip 도 리포트에 사유를 남긴다(침묵 금지) — 예보 항목 없는 축약판. 실체화-0 skip 은 계약 실존 절을
    싣는다(결손 ≥1 이면 exit 5 의 근거 — kkebi S2 판형: update 소비자만의 명세)."""
    if report_path is None:
        return
    now: str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines: "list[str]" = [
        "",
        f"## pre-gate 예보 — {now} · {spec.name}",
        "",
        f"- 기준선 SHA: `{base_sha}` (--base {base_ref}) · 프로필: auto · 모드: 차단({MODE}) · "
        f"{_executor_stamp(blk_hash)}",
        f"- {NO_SUBSTITUTE}",
        f"- 판정: {verdict}",
        "",
    ]
    lines.extend(f"- {item}" for item in detail)
    if existence is not None:
        lines.extend(_existence_lines(existence))
    lines.append("")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with report_path.open("a", encoding="utf-8") as fp:
        fp.write("\n".join(lines))


# ── 차단 모드 — 계획↔기준선 모순(형식 red) · 리포트 최신성 대조(--check-report) ──────────────────

def _promoted_form(copy: Path, path: str) -> bool:
    """유효 승격 형태 — `<stem>/__init__.py` ∧ `<stem>/<name>.py`(check-layer-skeleton #638 동형). architect 경로 표기는
    언제나 `<칸>.py` 이므로(동명 폴더 승격은 구현 캐스케이드 소유) update 대상의 «실존» 은 이 형태까지다 — 폴더만 있는
    경우(비승격 하위 패키지·정크)는 실존이 아니다(폴더 예외가 새 도피 경로가 되지 않게 · 3단계 리뷰 A1)."""
    if not path.endswith(".py"):
        return False
    stem: Path = copy / path[:-3]
    return (stem / "__init__.py").is_file() and (stem / f"{stem.name}.py").is_file()


def baseline_form_errors(plan: Plan, copy: Path, in_baseline: "frozenset[str]", base_short: str,
                         in_head: "Callable[[str], bool]") -> "tuple[list[str], frozenset[str]]":
    """계획↔기준선 모순의 전건 열거(차단 모드 · 오버레이 «전» 판정 · 1회 일괄 반송 재료).

    태그의 뜻은 기준선 기준이다(architect R-3425): `add` = 기준선 부재(실존이면 «add 충돌») · `update` = 기준선 실존
    (부재면 «update 대상 부재» — 그 경로는 add 다 · 유효 승격 형태 실존은 예외) · 비후행 `remove` = 기준선 실존(부재면
    «remove 대상 부재» — 고정 기준선에서 기실현 remove 는 실존이다) · `empty`·후행 `remove@Ln` 은 판정 밖.
    왜 — 차단은 «add 를 update 로 재라벨해 실체화 0(skip)으로 도피» 할 유인을 키우고(reading run 36 red 8 → run 37
    green 0 · 24경로 재라벨 실측), update 는 파일을 만들지 않으므로 그 도피는 검출 집합을 줄인다. 오버레이 실존은
    판정에 넣지 않는다(미커밋 기실현 add 의 재라벨도 기준선 부재라 red). 기준선 이후 HEAD 실존은 사유행을 나눈다
    (자기 기실현 add 면 add 로 복원 · 타 레인 유입이면 STOP — 기준선 이동 금지) — `in_head` 는 부재 행에서만 부른다.

    반환: (오류 목록 — 전건, 승격 형태 예외로 통과한 update 경로 집합).
    """
    errors: "list[str]" = []
    promoted: "set[str]" = set()
    for path, entry in plan.entries.items():
        present: bool = path in in_baseline
        if entry.tag == "add" and present:
            errors.append(f"add 충돌(실존): {path} — 계획과 실물의 모순은 그 자체가 발견이다")
        elif entry.tag == "update" and not present:
            if _promoted_form(copy, path):
                promoted.add(path)
            elif in_head(path):
                errors.append(f"update 대상 기준선 이후 실존: {path} — 기준선 {base_short} 에 없고 HEAD 에 있다: "
                              f"자기 기실현 add 면 add 로 복원 · 타 레인 유입이면 STOP(기준선 이동 금지)")
            else:
                errors.append(f"update 대상 부재: {path} — 기준선 {base_short} 에 없는 경로는 add 다(재라벨 도피 금지)")
        elif entry.tag == "remove" and not entry.deferred_remove and not present:
            errors.append(f"remove 대상 부재: {path} — 기준선 {base_short} 에 없는 경로는 제거할 수 없다"
                          f"(고정 기준선에서 기실현 remove 는 실존이다 — 이미 지워진 경로는 행을 거둔다)")
        elif entry.tag == "empty" and present:
            # `empty` 는 add 와 같은 «새 파일» 태그다 — 기준선 실존을 already-built 로 통과시키면 기실현 add 를 empty 로
            # 재라벨해 실체화 0 으로 도피하는 경로가 update 재라벨과 동형으로 남는다(6단계 감사 MAJOR-1).
            errors.append(f"empty 충돌(실존): {path} — 새 빈 파일 자리가 기준선 {base_short} 에 이미 있다: "
                          f"기실현이면 update 다(재라벨 도피 금지)")
    return errors, frozenset(promoted)


def _error_kinds(errors: "list[str]") -> str:
    """`요약:` 행의 사유 종류 계수 — 메시지 접두(«: » 앞)별 건수."""
    counts: "dict[str, int]" = {}
    for err in errors:
        kind: str = err.split(":", 1)[0].split("(", 1)[0].strip()
        counts[kind] = counts.get(kind, 0) + 1
    return " · ".join(f"{k} {n}" for k, n in counts.items())


# 절 앵커 = 실행기 자기 형식(`## pre-gate 예보 — <UTC> · <spec>`) — 코디네이터가 «## pre-gate 예보 …» 로 시작하는 제목을
# 쓰더라도 타임스탬프 없이는 절이 아니다(문면 의존 0 · 5단계 리뷰 A3).
_REPORT_SECTION_RE: "re.Pattern[str]" = re.compile(r"^## pre-gate 예보 — \d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z · ", re.M)
_REPORT_HASH_RE: "re.Pattern[str]" = re.compile(r"블록 해시 ([0-9a-f]{12})")
_REPORT_BASE_RE: "re.Pattern[str]" = re.compile(r"`([0-9a-f]{40})`")
_REPORT_ID_RE: "re.Pattern[str]" = re.compile(r"^- `([0-9a-f]{12})` ", re.M)
_REPORT_COUNT_RE: "re.Pattern[str]" = re.compile(r"예보 (\d+)건")
_REPORT_DEFECT_RE: "re.Pattern[str]" = re.compile(r"결손 (\d+)건")


def _subsection(section: str, header: str) -> str:
    """절 안의 `### <header>` 소절 본문(다음 `### ` 까지) — 없으면 빈 문자열."""
    idx: int = section.find(f"### {header}")
    if idx < 0:
        return ""
    rest: str = section[idx + len(header) + 4:]
    nxt: int = rest.find("\n### ")
    return rest if nxt < 0 else rest[:nxt]


def _disposed(section: str, stable_id: str) -> bool:
    """처분 행(R-3438 정형 — `` - `<ID>` … → **<라벨>**(<증거>) ``)이 이 절 이후에 있는가 — 라벨은 ignored|filtered 만
    (corrected 는 재실행이 곧 최종본 · 증거 토큰은 사람 감사용이라 읽지 않는다)."""
    token: str = f"`{stable_id}`"
    for line in section.split("\n"):
        if token in line and ("**ignored**" in line or "**filtered**" in line):
            return True
    return False


def check_report(spec_text: str, report_text: str) -> "tuple[int, list[str], dict[str, str]]":
    """리포트 최신성·처분 완결 대조(출력 전용 · 판정 무접촉).

    ⑴ 마지막 `## pre-gate 예보 — ` 절(앵커 접두 일치 금지 — «## pre-gate 처분 라벨» 류 코디네이터 절·skip 행은 절이
    아니다) ⑵ 그 절의 첫 `- 기준선 SHA:` 행의 블록 해시 = `block_hash(spec)` ⑶ 첫 `- 판정:` 이 형식 red 가 아님
    ⑷ 예보 red 면 `### 예보 항목` 소절의 안정 ID 전건에 그 절 이후(EOF 까지) 처분 행 — 이전 절의 처분은 불인정
    (red 절마다 재기재 — R-3433) ⑸ green·skip·결손 판정은 통과.
    반환: (exit — 0 정합 · 3 불비 · 1 절/헤더 부재, 사유 목록, 요약 재료).
    """
    starts: "list[int]" = [m.start() for m in _REPORT_SECTION_RE.finditer(report_text)]
    if not starts:
        return 1, ["예보 절 부재 — `## pre-gate 예보 — ` 헤더가 없다(pre-gate 미실행 리포트)"], {}
    section: str = report_text[starts[-1]:]
    lines: "list[str]" = section.split("\n")
    base_line: "str | None" = next((ln for ln in lines if ln.startswith("- 기준선 SHA:")), None)
    verdict_line: "str | None" = next((ln for ln in lines if ln.startswith("- 판정:")), None)
    if base_line is None or verdict_line is None:
        return 1, ["헤더 행 부재 — 마지막 예보 절에 `- 기준선 SHA:` 또는 `- 판정:` 행이 없다"], {}
    verdict: str = verdict_line[len("- 판정:"):].strip()
    spec_hash: str = block_hash(spec_text)
    hash_m: "re.Match[str] | None" = _REPORT_HASH_RE.search(base_line)
    base_m: "re.Match[str] | None" = _REPORT_BASE_RE.search(base_line)
    problems: "list[str]" = []
    report_hash: str = hash_m.group(1) if hash_m else "-"
    if hash_m is None:
        problems.append("최신성 증명 불가 — 마지막 헤더에 블록 해시 토큰이 없다(구판 리포트) · 재발화")
    elif report_hash != spec_hash:
        problems.append(f"stale — 명세 블록 해시 {spec_hash} ≠ 마지막 예보 {report_hash} · 재발화")
    count_m: "re.Match[str] | None" = _REPORT_COUNT_RE.search(verdict)
    defect_m: "re.Match[str] | None" = _REPORT_DEFECT_RE.search(verdict)
    attributed: int = int(count_m.group(1)) if count_m else 0
    defects: int = int(defect_m.group(1)) if defect_m else 0
    short: str
    if verdict.startswith("형식 red"):
        problems.append(f"형식 red 미해소 — 마지막 판정 «{verdict}» · architect 반송")
        short = "형식 red"
    elif verdict.startswith("예보 red"):
        ids: "list[str]" = _REPORT_ID_RE.findall(_subsection(section, "예보 항목"))
        missing: "list[str]" = [i for i in ids if not _disposed(section, i)]
        if missing:
            problems.append(f"처분 미기재 {len(missing)}건(ignored|filtered 행 없음 — corrected 는 재실행이 최종본): "
                            + " ".join(f"`{i}`" for i in missing))
        short = f"red {attributed}({'처분 전건' if not missing else f'미기재 {len(missing)}'}) · 실존 결손 {defects}"
    elif verdict.startswith("예보 green"):
        short = "green" + (f" · 실존 결손 {defects}" if defects else "")
    elif verdict.startswith("skip"):
        short = "skip" + (f" · 실존 결손 {defects}" if defects else "")
        if "<!-- machine:" not in spec_text:
            # 구형 명세 + 관찰기(≤2.17.16)의 «블록 부재 skip» 스텁이 마지막 절로 남은 레인 — 블록 해시가 불변이라 캐시 skip 으로
            # 재실행 없이 G2 가 열리는 좁은 경로를 닫는다(5단계 리뷰 C · 결정 잔여 1): 차단 모드에서 블록 부재는 형식 red 다.
            problems.append("블록 부재 — 마지막 판정이 관찰 모드 skip 이고 명세에 machine 마커가 없다: 소급 블록 작성 후 재발화")
    else:
        problems.append(f"판정 문면 불명 — «{verdict}»")
        short = verdict[:24]
    info: "dict[str, str]" = {
        "spec_hash": spec_hash, "report_hash": report_hash, "short": short,
        "attributed": str(attributed), "defects": str(defects),
        "base": base_m.group(1)[:12] if base_m else "-",
    }
    return (3 if problems else 0), problems, info


def run_check_report(spec_text: str, report_path: Path, blk_hash: str) -> int:
    """`--check-report` 진입 — 배너(G1/G1′)·G2 근거 대조의 유일한 기계 출처(`요약:` 행)."""
    print(f"# design_pregate --check-report · 모드 차단({MODE}) · {_executor_stamp(blk_hash)}")
    if not report_path.is_file():
        print(f"실행 불능: 리포트 부재 — {report_path} (pre-gate 가 이 레인에서 한 번도 실행되지 않았다 · 구형 명세·"
              f"변경 0 레인이면 최신성 행은 «미실행(구형 명세 · 변경 0)» — 블록이 있는 명세는 실행이 의무다)",
              file=sys.stderr)
        return 1
    result: "tuple[int, list[str], dict[str, str]]" = check_report(spec_text, report_path.read_text(encoding="utf-8"))
    code: int = result[0]
    problems: "list[str]" = result[1]
    info: "dict[str, str]" = result[2]
    if code == 1:
        print(f"실행 불능: {problems[0]}", file=sys.stderr)
        return 1
    for p in problems:
        print(f"  불비: {p}")
    status: str = "정합" if code == 0 else f"불비 {len(problems)}건"
    print(f"\n요약: check-report {status} · 블록 해시 {info['spec_hash']}={info['report_hash']} · "
          f"마지막 판정 {info['short']} · 귀속 {info['attributed']}건 · 실존 결손 {info['defects']}건 · "
          f"기준선 {info['base']}")
    return code


# ── main ────────────────────────────────────────────────────────────────────

def main(argv: "list[str]") -> int:
    ap: _UsageParser = _UsageParser(add_help=True, description="design-spec pre-gate 예보 실행기")
    ap.add_argument("spec", help="설계 명세 markdown(기계 블록 §4 포함)")
    ap.add_argument("target", help="대상 저장소 루트(git)")
    ap.add_argument("--base", default=None,
                    help="사본 기준 git ref(기본 HEAD). 명시하면 재발화 판형 — 기준선 트리에 없던 계획 add 의 "
                         "오버레이 실존은 «기실현 add»로 기록하고 앵커 커밋 전에 걷어내 스텁으로 실체화한다"
                         "(명시 `--base HEAD` 포함)")
    ap.add_argument("--report", default=None, help="예보 리포트 append 경로(D4)")
    ap.add_argument("--python", dest="python_bin", default=sys.executable,
                    help="검사기 인터프리터(대상 venv — 기본 sys.executable)")
    ap.add_argument("--keep", action="store_true", help="격리 사본·스크래치 보존(디버그)")
    ap.add_argument("--block-hash", action="store_true",
                    help="기계가독 블록 해시만 출력하고 끝낸다(출력 전용·판정 무접촉 — 캐시 skip 대조용)")
    ap.add_argument("--check-report", default=None,
                    help="pregate-report.md 의 최신성·처분 완결만 대조하고 끝낸다(출력 전용·git 0회 — "
                         "배너·G2 근거 대조용: exit 0 정합 · 3 불비 · 1 리포트/절 부재)")
    ns: argparse.Namespace = ap.parse_args(argv)

    spec_path: Path = Path(ns.spec).resolve()
    repo: Path = Path(ns.target).resolve()
    report_path: "Path | None" = Path(ns.report).resolve() if ns.report else None
    if not spec_path.is_file():
        print(f"실행 불능: 명세 파일 없음 — {spec_path}", file=sys.stderr)
        return 1
    text: str = spec_path.read_text(encoding="utf-8")
    blk_hash: str = block_hash(text)
    if ns.block_hash:
        print(f"블록 해시 {blk_hash}")
        return 0
    if ns.check_report is not None:
        return run_check_report(text, Path(ns.check_report).resolve(), blk_hash)
    if not (repo / ".git").exists():
        print(f"실행 불능: git 저장소가 아니다 — {repo} (차분 예보는 git 앵커가 전제다)", file=sys.stderr)
        return 1

    base_ref: str = ns.base or "HEAD"
    explicit_base: bool = ns.base is not None
    rev: "subprocess.CompletedProcess[bytes]" = _git(repo, "rev-parse", "--verify",
                                                     f"{base_ref}^{{commit}}", check=False)
    if rev.returncode != 0:
        print(f"실행 불능: --base {base_ref!r} resolve 불능 — "
              f"{rev.stderr.decode('utf-8', 'replace').strip()}", file=sys.stderr)
        return 1
    base_sha: str = rev.stdout.decode("ascii").strip()

    gap: "str | None" = _interpreter_gap_reason(repo, ns.python_bin)
    if gap is not None:
        print(f"실행 불능: {gap}", file=sys.stderr)
        return 1

    plan_result: "tuple[Plan | None, list[str]]" = parse_spec(text)
    plan: "Plan | None" = plan_result[0]
    errors: "list[str]" = plan_result[1]
    if errors:
        print(f"형식 red — {len(errors)}건 (기계 블록이 규범 문법 밖이다 · architect 반송 재료):")
        for err in errors:
            print(f"  {err}")
        write_report_stub(report_path, spec_path, base_ref, base_sha, "형식 red", errors, blk_hash)
        print(f"\n요약: 형식 red {len(errors)}건(문법) · 기준선 {base_sha[:12]} · 모드 차단")
        return 3
    if plan is None:
        reason: str = ("형식 red — machine 블록 부재(<!-- machine: file-plan --> 없음): 차단 모드는 블록이 의무다 — "
                       "구형 명세(형식 규범 이전 승인)는 개정 시점에 블록을 소급 작성한다"
                       "(기준선 실존 경로는 update · 부재 경로만 add)")
        print(reason)
        write_report_stub(report_path, spec_path, base_ref, base_sha, "형식 red(블록 부재)", [reason], blk_hash)
        print(f"\n요약: 형식 red 1건(블록 부재) · 기준선 {base_sha[:12]} · 모드 차단")
        return 3
    if not plan.entries:
        reason = ("형식 red — file-plan 0행(블록 공허): 변경 파일이 없는 명세는 pre-gate 대상이 아니라 산문이다 — "
                  "update 대상이라도 적는다(빈 펜스로 블록 의무를 채울 수 없다)")
        print(reason)
        for note in plan.notes:  # 고아 채널 행(symbols/imports 만 있는 명세)은 버려졌음을 남긴다(침묵 금지)
            print(f"  채널 메모: {note}")
        write_report_stub(report_path, spec_path, base_ref, base_sha, "형식 red(블록 공허)",
                          [reason] + [f"채널 메모: {n}" for n in plan.notes], blk_hash)
        print(f"\n요약: 형식 red 1건(블록 공허) · 기준선 {base_sha[:12]} · 모드 차단")
        return 3

    scratch: Path = Path(tempfile.mkdtemp(prefix="design-pregate-"))
    copy: Path = scratch / "copy"
    try:
        copy.mkdir(parents=True)
        _extract_archive(repo, base_sha, copy)
        # archive == 기준선 트리 — 오버레이 «전»에 계획 경로의 실존을 재서 «기준선 실존 add»(형식 red 유지)와
        # «오버레이 실존 add»(재발화 판형의 기실현)를 가른다(git 추가 호출 0·결정적).
        in_baseline: "frozenset[str]" = frozenset(
            p for p in plan.entries if (copy / p).exists() or (copy / p).is_symlink())
        # 계획↔기준선 모순 전건(차단 모드): add 충돌 · update/remove 대상 기준선 부재 — 오버레이 «전»·1회 일괄 반송.
        # «기준선 부재 ∧ HEAD 실존» 은 `--base` 명시 경로에서만 가능하다(기본 기준선 = HEAD 트리) — git 호출도 그때만.
        form_result: "tuple[list[str], frozenset[str]]" = baseline_form_errors(
            plan, copy, in_baseline, base_sha[:12],
            (lambda p: _git(repo, "cat-file", "-e", f"HEAD:{p}", check=False).returncode == 0)
            if explicit_base else (lambda p: False))
        form_errors: "list[str]" = form_result[0]
        promoted: "frozenset[str]" = form_result[1]
        if form_errors:
            print(f"형식 red — {len(form_errors)}건 (계획↔기준선 모순 · architect 반송 재료):")
            for err in form_errors:
                print(f"  {err}")
            if promoted:
                print(f"  승격 형태 예외 통과 {len(promoted)}건: " + " ".join(sorted(promoted)))
            write_report_stub(report_path, spec_path, base_ref, base_sha, "형식 red", form_errors, blk_hash)
            print(f"\n요약: 형식 red {len(form_errors)}건({_error_kinds(form_errors)}) · "
                  f"기준선 {base_sha[:12]} · 모드 차단")
            return 3
        overlaid: "list[str]" = _overlay_dirty(repo, copy)
        # 기실현 add 는 앵커 커밋 «전»에 걷어낸다 — 앵커 스냅숏(L)에 실물이 남으면 스텁 진단이 잔존으로 빠진다.
        realized: "frozenset[str]" = lift_realized_adds(copy, plan, explicit_base, in_baseline)
        _git(copy, "init", "-q")
        _git(copy, "add", "-A")
        _git(copy, "commit", "-q", "-m", "pregate-anchor", "--allow-empty")

        try:
            mat: "dict[str, list[str]]" = materialize(copy, plan, realized=realized, base_short=base_sha[:12],
                                                      promoted=promoted)
        except FormError as exc:
            print(f"형식 red — {exc}")
            write_report_stub(report_path, spec_path, base_ref, base_sha, "형식 red", [str(exc)], blk_hash)
            print(f"\n요약: 형식 red 1건({_error_kinds([str(exc)])}) · 기준선 {base_sha[:12]} · 모드 차단")
            return 3

        # 계약 실존 — materialize(+골격·`__init__` 체인) 뒤 · 실체화-0 분기 앞(update 소비자만의 명세도 판정한다).
        existence: ExistenceReport = check_import_existence(copy, plan)
        own_note: "str | None" = _own_interpreter_note(repo)
        if own_note is not None:
            existence.undecidable_notes.append(own_note)
        defects: int = len(existence.defects)

        if not mat["materialized"]:
            reason = ("skip — 실체화 0건(add/empty/remove 실효 조치 없음): "
                      "게이트를 부르지 않는다(공허 차분 가드 · 사유 명시)")
            verdict_stub: str = "skip" + (f" · 계약 실존 결손 {defects}건(권고·비차단)" if defects else "")
            print(reason)
            for item in mat["unsimulated"]:
                print(f"  미시뮬레이션: {item}")
            _print_existence(existence)
            print(f"\n요약: 실체화 0 · 실존 결손 {defects}건 · 기준선 {base_sha[:12]} · 모드 차단")
            write_report_stub(report_path, spec_path, base_ref, base_sha, verdict_stub,
                              [reason] + [f"미시뮬레이션: {x}" for x in mat["unsimulated"]], blk_hash,
                              existence=existence)
            return 5 if defects else 4

        print(f"# design_pregate — 예보 실행 · 기준선 {base_sha[:12]} (--base {base_ref}) · "
              f"모드 차단({MODE}) · {_executor_stamp(blk_hash)}")
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
        verdict += f" · 계약 실존 결손 {defects}건(권고·비차단)"
        print(f"\n== 예보 항목 {len(attributed)}건 ==")
        for line in attributed:
            print(f"  `{_stable_id(line)}` {line}")
        for note in plan.notes:
            print(f"  채널 메모: {note}")
        _print_existence(existence)
        print(f"\n판정: {verdict}")
        print(f"요약: 귀속 {len(attributed)}건 · 실존 결손 {defects}건 · 기준선 {base_sha[:12]} · 모드 차단")
        if report_path is not None:
            write_report(report_path, spec_path, base_ref, base_sha, verdict,
                         attributed, mat, plan.notes, blk_hash, existence)
        if gate_exit != 0:
            return 2
        return 5 if defects else 0
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
