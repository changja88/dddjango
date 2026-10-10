#!/usr/bin/env python3
"""dddjango-web 리팩토링 모드 결정적 도구 — 단위 점검(R2)·판정(R3)·G2 잔존의 기계 판정(표준 라이브러리 전용).

Coordinator «리팩토링 모드» 절이 이 도구를 부른다. 리뷰어·architect 에게는 이 도구가 없다 — 도구는
Coordinator 만 돌리고, 산출은 파일로 쓰고 경로만 넘긴다. 규칙 팩이 없다(web 은 산문 정본) — 빼는 출구
검사는 설치본 문서의 절·문장·문단과 문면 규칙(긍정 술어·부정형·적용 한정 어구)으로 한다.

단위(Coordinator Phase 0 step 4′ 단위 목록 — v1.3.1 목록을 새 트리에 1:1 로 옮긴 것): BC `web/application/[<area>/]<bc>`
(그 BC 의 `web/static/application/[<area>/]<bc>/` 미러 CSS 와 그 BC 만 참조하는 정적 파일 포함) · `web/root`(+ `web/static/root/`) ·
`web/common` · `web/design_system` · `web/static/<칸>`(js · images · fonts · htmx …) · 컨테이너 `web/*.py` · 표준 트리 밖 옛 배치
최상위 폴더 `web/<옛 폴더>`. 외부 JS 고정 사본(`web/static/vendor/`)과 등재 목록(`web/sdk_registry.json`)은 어느 단위도 아니다.
제품 선언(`web/product_registry.json` — 2.3.0)도 어느 단위가 아니다(사용자 결정으로만 바뀐다). 선언 오류면 `plan` 은 실행 불능이다(exit 1).

사용(대상 프로젝트 루트에서):
  refactor_audit.py plan <단위> --debt <debt-g0.json> --out <audit 폴더>
                                      범위 파일·경계 교차·줄 편집·범위 안 키·렌즈 × 조각 → plan.md
                                      (문서 자리 `docs/` 의 옛 경로 글은 판정 밖 — «문서 글 적중» 절에 알림으로만)
  refactor_audit.py plan <단위> --debt <debt-g0.json> --against <audit 폴더>/plan.md
                                      G0 정지 재개 조건 ①~④ 대조(기록 plan 무미커밋 · 그 HEAD 이후 범위 파일 무변 ·
                                      범위 미추적 0 · 여섯 목록 같음 — 쓰지 않는다)
  refactor_audit.py plan <단위> --debt <debt-g0.json> --out <audit 폴더> --names <design-spec.md>
                                      명세 `## 슬라이스 0` 절의 쌍 → 명세 참조 줄 (나) · 문서 글 적중(알림) → plan-names.md
  refactor_audit.py check <audit 폴더>                리뷰어 표 인용·위치 검사 → check.md
  refactor_audit.py check-verdict <audit 폴더> [--feedback <파일>] [--final]
                                      verdict.md 검사 → verdict-log.md append · (exit 0) verdict-final.md · g0-lists.md
  refactor_audit.py residual <산출물 폴더> [--finalize <시각>]
                                      G2 의미 항목 잔존(결정적 바닥 → 리뷰어 재확인 묶음)
  refactor_audit.py standing [<산출물 폴더> --gate]
                                      상시 답 인식(`.dddjango/standing-answer.md` — core 와 같은 파일) ·
                                      --gate: `refactor-scope.md` 상시 답 결정 줄 검사(마지막 `## G0` 뒤)
  refactor_audit.py --self-test       점검 절 실재 · 경로 사상 · 적용 한정 어구 목록 · pathspec · 극성 표본 · 상시 답 문면
공통: --platform claude|codex(기본: 구조로 판별) · --plugin-root <경로> · --project <대상 루트>
exit 0 = 통과 · 2 = red(검사 실패·잔존·불일치) · 1 = 실행 불능. 모든 하위 명령이 `요약:` 1행을 낸다.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import re
import subprocess
import sys
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.debt import (DebtError, DOC_PATHSPEC, SPEC_SLICE0_HEAD, REF_GREP_OPTIONS, REF_PATHSPEC,  # noqa: E402
                      debt_universe, doc_reference_lines, module_of, parse_spec_pairs, reference_lines,
                      residual_m_sets, tail_of)

from src.products import REGISTRY as PRODUCT_REGISTRY, declaration_error  # noqa: E402

_QUOTE_HEAD: "re.Pattern[str]" = re.compile(r"^[ \t]*>[ \t]?", re.M)
_SPACE: "re.Pattern[str]" = re.compile(r"\s+")


def normalize(text: str) -> str:
    """강조(`**`·`*`)·백틱·인용 줄머리(`> `)를 지우고 공백류(줄바꿈 포함)를 전부 지운다(dddjango 판과 같다)."""
    text = _QUOTE_HEAD.sub("", text)
    text = text.replace("**", "").replace("*", "").replace("`", "")
    return _SPACE.sub("", text)


def normalize_spaced(text: str) -> str:
    """`normalize` 와 같은 삭제를 하되 공백류(줄바꿈 포함)는 한 칸으로 접는다 — 긍정 술어·부정형·무효 접미·«만» 판정용
    (낱말 경계가 남아 «예외 다른»이 `예외다` 로 붙지 않는다). 공백을 지우면 `normalize` 결과와 같다."""
    text = _QUOTE_HEAD.sub("", text)
    text = text.replace("**", "").replace("*", "").replace("`", "")
    return _SPACE.sub(" ", text).strip()


def _inline(text: str) -> str:
    return _SPACE.sub("", text.replace("*", "").replace("`", ""))


# ── 상수 ─────────────────────────────────────────────────────────────────────

EXIT_OK, EXIT_ERR, EXIT_RED = 0, 1, 2
CHUNK_LINES: int = 5000
# 렌즈 = 설계 리뷰 4축(dddart G1 «4축 전부 병렬» — 활성 렌즈를 추론하지 않는다) + 코드 규율 1. 조각마다 다섯 렌즈를 전부 부른다.
LENSES: "tuple[str, ...]" = ("ddd", "ui", "state", "data", "discipline")
REVIEWERS: "dict[str, str]" = {"ddd": "design-review-ddd-web", "ui": "design-review-ui-web",
                               "state": "design-review-state-web", "data": "design-review-data-web",
                               "discipline": "discipline-reviewer-web"}
# 두 플러그인의 실행 산출물 폴더(프로젝트 상대) — 그 아래 파일은 residual 해소 근거가 아니다.
OUTPUT_ROOTS: "tuple[str, ...]" = (".dddjango/", ".dddjango-web/")
CONTAINER: str = "*.py"
LAYERS: "frozenset[str]" = frozenset({"domain_layer", "application_layer", "infra_layer", "presentation_layer"})
CODE_SUFFIXES: "frozenset[str]" = frozenset({".py", ".html", ".css", ".js"})
# 외부 JS 고정 사본과 등재 목록 — 외부 JS 승인 절차가 맡는다(리팩토링 단위 · 범위 · 소유 판정 밖).
EXCLUDED_PREFIXES: "tuple[str, ...]" = ("static/vendor/",)
EXCLUDED_FILES: "frozenset[str]" = frozenset({"sdk_registry.json", PRODUCT_REGISTRY})  # + 제품 선언(사용자 결정 — 단위 밖)

_DDD: str = "skills/architecture-ddd/references/final.md"
_UIA: str = "skills/architecture-ui/references/final.md"
_STATE: str = "skills/architecture-state/references/final.md"
_DATA: str = "skills/architecture-data/references/final.md"
_DJANGO: str = "skills/implementation-django/references/final.md"
_HTMX: str = "skills/implementation-htmx/references/final.md"
_JS: str = "skills/implementation-javascript/references/final.md"
_CLEAN: str = "skills/discipline-cleancode/references/final.md"
_HOUSE_SKILL: str = "skills/discipline-houserules/SKILL.md"
_HOUSE: str = "skills/discipline-houserules/references/final.md"
_UNDECIDABLE: str = "skills/discipline-houserules/references/undecidable.md"
COORDINATOR: str = "commands/dddjango-web.md"
ARCHITECT: str = "agents/design-architect-web.md"


def _sections(doc: str, numbers: "tuple[int, ...] | range") -> "tuple[str, ...]":
    return tuple(f"{doc} §{n}" for n in numbers)


# 렌즈별 점검 절(`<문서 키> §<절>` — 절은 번호 또는 제목 원문 · 하위 절 포함). 배정: 각 리뷰어 본문의 점검 항목 절 +
# 그 렌즈의 architecture 스킬 전 절 + 그 렌즈가 검증하는 undecidable 절(리뷰어 본문의 «기계 판별 불가 판별» 목록) +
# 구현 표기 중 그 렌즈 몫. 표기 규율(템플릿 · CSS · JS · hx-*)은 discipline 렌즈. houserules §7(drift 교정 표)은 뺀다(v1.3.1 그대로).
LENS_SECTIONS: "dict[str, tuple[str, ...]]" = {
    "ddd": ("agents/design-review-ddd-web.md §점검 항목 (도메인 lens만)",
            *_sections(_DDD, range(1, 12)),
            *_sections(_UNDECIDABLE, (3, 4, 8))),
    "ui": ("agents/design-review-ui-web.md §점검 항목 (화면 lens만)",
           *_sections(_UIA, range(1, 9)),
           *_sections(_DJANGO, (2, 8, 9, 10)),
           *_sections(_UNDECIDABLE, (1, 2))),
    "state": ("agents/design-review-state-web.md §점검 항목 (상태 lens만)",
              *_sections(_STATE, range(1, 11)),
              *_sections(_HTMX, (3, 5, 6)),
              *_sections(_UNDECIDABLE, (5, 6, 7, 10))),
    "data": ("agents/design-review-data-web.md §점검 항목 (데이터 lens만)",
             *_sections(_DATA, range(1, 9)),
             *_sections(_DJANGO, (4,)),
             *_sections(_UNDECIDABLE, (12,))),
    "discipline": ("agents/discipline-reviewer-web.md §점검 항목",
                   *_sections(_CLEAN, range(1, 19)),
                   *_sections(_HOUSE_SKILL, (1, 2, 3)),
                   *_sections(_HOUSE, (1, 2, 3, 4, 5, 6, 8)),
                   *_sections(_UNDECIDABLE, (1, 6, 7, 8, 9, 10, 11, 13)),
                   *_sections(_JS, range(1, 8)),
                   *_sections(_HTMX, (4, 9)),
                   *_sections(_DJANGO, (6,))),
}

# 적용 한정 어구 닫힌 목록은 상수로 두지 않는다 — 설치본 Coordinator «리팩토링 모드» 절 적용 범위 규범
# 문단의 «…» 목록(«적용 한정 어구» 뒤)을 그때그때 읽는다(산문 정본 한 곳 · 비면 실행 불능).
PHRASE_MARK: str = "적용 한정 어구"
NORM_HEAD: str = "적용 범위 규범"

# 제외 근거 문장의 긍정 술어 · 무효 접미 · 부정형(설계 6b §5-3). 술어는 공백을 한 칸으로 접은 문장(`normalize_spaced`)에
# 건다 — 줄을 넘는 문장도 한 칸으로 이어지고, 띄어 쓸 수 있는 자리만 `\s?` 로 받는다(분류 F4). 전수 분류: phrase-classification.md §4.
POSITIVE: "tuple[str, ...]" = (
    r"허용(?:한다|된다|이다|하되|하며|하고)",
    r"(?<!널)(?<!널 )허용\)",
    r"허용:",
    r"예외(?:다|이다|로\s?둔다)",
    r"[아어여해]도\s?(?:된다|좋다)",
    r"무방",
    r"위반이\s?아니(?:다|며)",
    r"정당하다",
    r"강제하지\s?않는다",
    r"충분하다",
    r"허용\s?목록",
)
# `(쓸|둘|할) 수 있다` 는 이 문서들에서만 허용 술어다 — discipline-cleancode 의 같은 모양은 능력·효과 서술이다
# (언어 · 테스트 표기 문서 implementation-python · implementation-test · discipline-test 도 같은 까닭으로 뺀다).
CAN_PREDICATE: str = r"(?:쓸|둘|할)\s?수\s?있다"
CAN_DOCS: "frozenset[str]" = frozenset({
    *(f"skills/{s}/SKILL.md" for s in ("architecture-ddd", "architecture-ui", "architecture-state", "architecture-data",
                                       "implementation-django", "implementation-htmx", "implementation-javascript")),
    _DDD, _UIA, _STATE, _DATA, _DJANGO, _HTMX, _JS, _HOUSE_SKILL, _HOUSE, _UNDECIDABLE,
    *(f"agents/{a}.md" for a in REVIEWERS.values()),
})
INVALID_SUFFIX: "re.Pattern[str]" = re.compile(r"(?:는|고|라는|라고|면)")
# 술어 바로 앞이 «만» 이면 제한형이다(«기능 JS만 허용하며») — 허용 근거가 아니다.
RESTRICTIVE_BEFORE: str = "만"
NEGATIONS: "tuple[str, ...]" = ("허용하지않", "허용되지않", "예외가아니", "예외없", "예외를두지않", "무방하지않")
# 제외 근거가 될 수 있는 문서 — 규칙 문서(스킬·에이전트). Coordinator(`commands/`)·요청 가이드·스크립트 주석은 절차라
# 허용 근거가 아니다(설계 6b §5-2 «제외는 허용 문장만» — dddjango Permission/Exception 규범 대응).
RULE_DOC_PREFIXES: "tuple[str, ...]" = ("skills/", "agents/")
EXCEPTION_COLON: str = "예외:"

VERDICTS: "tuple[str, ...]" = ("채택", "병합", "제외", "오탐", "사용자 판단", "별도 요청")
PROXY_FREE: "tuple[str, ...]" = ("본인 직접", "사용자 원문")
SEPARATE_TYPES: "tuple[str, ...]" = ("외부 동작", "API 계약", "경계 교차", "web/ 밖")
# 개명·이동이 교정인 검사(커맨드 Phase 0 step 4′ «개명·이동 묶음» — ST4 골격 · NM4 «삼총사 미완» · NM18 «짝 미완»은 생성이라 제외).
RENAME_CHECKS: "frozenset[str]" = frozenset({*(f"ST{n}" for n in (0, 1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 12)),
                                             "NM1", "NM2", "NM3", "NM5", "NM6", "NM12", "NM15", "NM19", "NM20"})
# 편집 줄에 걸리면 편집 줄 키가 되는 패밀리(import 방향 · 출력 안전).
EDIT_LINE_FAMILIES: "tuple[str, ...]" = ("IM", "PU")
LOAD_LINE: "re.Pattern[str]" = re.compile(r"<script\b|<link\b|\{%\s*include\b")
CONSUMER_LINE: "re.Pattern[str]" = re.compile(r"\{%\s*(?:include|extends)\b")
AGAINST_LISTS: "tuple[str, ...]" = ("범위 파일", "경계 교차", "경계 교차 소비자", "줄 편집", "참조 치환 줄", "범위 안 키")
# 문서 글 적중(알림) 절 머리 — plan.md · plan-names.md 가 같은 머리를 쓴다. 판정 목록(AGAINST_LISTS)·편집 허용 줄이 아니다.
DOC_SECTION: str = "문서 글 적중(알림 — 이동을 막지 않음)"
# Coordinator 문면에서 참조 완전성 명령이 적히는 두 자리(문단 표지 → 이름) — self-test 가 자리마다 판정 pathspec 과
# 알림 명령 꼴(조회 옵션 + pathspec)을 대조한다.
REF_COMMAND_PARAGRAPHS: "tuple[tuple[str, str], ...]" = (("**개명·이동 묶음**", "G0 개명·이동 묶음"),
                                                        ("**슬라이스 0 호출**", "슬라이스 0 끝 green ③"))
# Coordinator 문면의 알림 명령이 꼬리 자리에 적는 표기.
DOC_COMMAND_NEEDLE: str = "<꼬리>…"


def _pathspec_text(spec: "tuple[str, ...] | list[str]") -> str:
    """pathspec 을 커맨드 문면의 꼴로 — 셸이 읽는 글자(`*`·`:`·괄호)가 있는 토큰만 작은따옴표로 감싼다."""
    return "-- " + " ".join(f"'{p}'" if re.search(r"[*:()]", p) else p for p in spec)


def _grep_command(needle: str, spec: "tuple[str, ...] | list[str]", word: bool = False) -> str:
    """참조 조회 한 번을 프로젝트 루트에서 다시 돌리는 명령 — 옵션은 도구의 실제 조회(`reference_lines`)와 같은 상수다."""
    return " ".join(["git", "grep", *REF_GREP_OPTIONS, *(["-w"] if word else []), "-e", needle, _pathspec_text(spec)])


# 극성 표본(설계 6b §5-2) — (문장, 유효한 허용 술어가 있는가).
POLARITY_SAMPLES: "tuple[tuple[str, bool], ...]" = (
    ("이 경우 예외를 허용하지 않는다.", False),
    ("그 목록은 설명할 수 있다는 사실만 보인다.", False),
    ("다른 함수를 추출할 수 있다면, 그 함수는 여러 작업을 하고 있다.", False),
    ("값이 없으면 `null` 을 쓴다(널 허용).", False),
    ("사용자 장래의 계약 변경 가능성을 G0 의 예외 승인으로 취급하지 않는다.", False),
    ("그 규칙은 허용된다면 따로 적는다.", False),
    ("그 표기는 무방하지 않다.", False),
    ("예외 다른 경로는 금지다.", False),
    ("짧은 이름은 허용하되 뜻이 드러나야 한다.", True),
    ("반복문 변수는 짧아도 된다.", True),
    ("공용 헬퍼는 금지다(단일 화면 전속은 허용).", True),
    ("이것은 «직속 파일 금지»의 명시 예외다.", True),
    ("승인된 기능 JS만 허용하며 native로 충분하면 파일을 만들지 않는다.", False),
    ("범용 scripts block 은 화면 어휘 금지 위반이 아니다.", True),
    ("사슬 밖 사용은 그대로 정당하다.", True),
    ("감수 때 정답 형태로 강제하지 않는다.", True),
    ("감수 때 정답 형태로 강제하지 않는다고 적는다.", False),
    ("단순 동작은 이벤트 위임으로 충분하다.", True),
)


class ToolError(Exception):
    """실행 불능(exit 1) — 입력·재료 결손."""


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise ToolError(f"파일 없음 — {path}") from None


def _git(project: Path, *args: str) -> str:
    result = subprocess.run(["git", "-C", str(project), "-c", "core.quotePath=false", *args],
                            capture_output=True, text=True)
    if result.returncode != 0:
        raise ToolError(f"git {' '.join(args[:2])} 실패 — {result.stderr.strip()[:200]}")
    return result.stdout


# ── 문서 색인(절·문장·문단) ─────────────────────────────────────────────────

_FENCE: "re.Pattern[str]" = re.compile(r"^ {0,3}(`{3,}|~{3,})")
_HEADING: "re.Pattern[str]" = re.compile(r"^(#{1,6})\s+(.*)$")
_ANCHOR: "re.Pattern[str]" = re.compile(r"^§?([0-9]+(?:[.\-][0-9A-Za-z]+)*)[.)]?(?=\s|$)")
_LIST_HEAD: "re.Pattern[str]" = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s")
_CIRCLED: str = "①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳"


class DocIndex:
    """설치본 문서 하나 — 행·정규화 본문·절·문장·문단."""

    def __init__(self, path: Path) -> None:
        self.path: Path = path
        self.lines: "list[str]" = _read(path).split("\n")
        if self.lines and self.lines[-1] == "":
            self.lines.pop()
        self.norm: "list[str]" = [normalize(ln) for ln in self.lines]
        self.off: "list[int]" = [0]
        for piece in self.norm:
            self.off.append(self.off[-1] + len(piece))
        self.text: str = "".join(self.norm)
        # 공백 한 칸 접은 병렬 본문과 정규화 위치 → 병렬 위치 사상(줄 사이는 한 칸)
        self.spaced: str = ""
        self.n2s: "list[int]" = []
        for ln in self.lines:
            piece: str = normalize_spaced(ln)
            base: int = len(self.spaced)
            self.n2s += [base + j for j, ch in enumerate(piece) if ch != " "]
            self.spaced += piece + " "
        self.fenced: "set[int]" = set()
        self.headings: "list[tuple[int, int, str, str]]" = self._headings()

    def _headings(self) -> "list[tuple[int, int, str, str]]":
        out: "list[tuple[int, int, str, str]]" = []
        start: int = 0
        if self.lines and self.lines[0] == "---":
            for i in range(1, len(self.lines)):
                if self.lines[i] in ("---", "..."):
                    start = i + 1
                    break
        fence: "str | None" = None
        for i in range(start, len(self.lines)):
            ln: str = self.lines[i]
            m = _FENCE.match(ln)
            if m:
                marker: str = m.group(1)
                if fence is None:
                    fence = marker
                    self.fenced.add(i)
                    continue
                if marker[0] == fence[0] and len(marker) >= len(fence) and ln.strip() == marker:
                    fence = None
                    self.fenced.add(i)
                    continue
            if fence is not None:
                self.fenced.add(i)
                continue
            hm = _HEADING.match(ln)
            if hm:
                text: str = hm.group(2).rstrip()
                am = _ANCHOR.match(text)
                out.append((i, len(hm.group(1)), text, am.group(1) if am else ""))
        return out

    def section(self, token: str) -> "tuple[int, int] | None":
        """절 토큰(번호 또는 제목 원문) → 행 범위 [a, b) — 같은 수준 이상의 다음 제목 전까지(하위 절 포함)."""
        token = token.strip()
        want: str = normalize(token)
        for idx, (line, level, text, anchor) in enumerate(self.headings):
            if (anchor and anchor == token.lstrip("§").rstrip(".")) or normalize(text) == want:
                end: int = len(self.lines)
                for line2, level2, _t, _a in self.headings[idx + 1:]:
                    if level2 <= level:
                        end = line2
                        break
                return line, end
        return None

    def occurrences(self, quote_norm: str, a: int = 0, b: "int | None" = None) -> "list[tuple[int, int]]":
        if not quote_norm:
            return []
        b = len(self.lines) if b is None else b
        lo, hi = self.off[a], self.off[b]
        out: "list[tuple[int, int]]" = []
        pos: int = self.text.find(quote_norm, lo)
        while pos != -1 and pos + len(quote_norm) <= hi:
            out.append((pos, pos + len(quote_norm)))
            pos = self.text.find(quote_norm, pos + 1)
        return out

    def sentences(self, a: int, b: int) -> "list[tuple[int, int]]":
        """행 범위 [a, b) 의 문장(정규화 오프셋 구간) — `다.`·`.`+공백·목록 머리·표 칸·원숫자·빈 줄 경계."""
        spans: "list[tuple[int, int]]" = []
        cur: "int | None" = None
        pos: int = self.off[a]

        def close(at: int) -> None:
            nonlocal cur
            if cur is not None and at > cur:
                spans.append((cur, at))
            cur = None

        for k in range(a, b):
            raw: str = self.lines[k]
            if not raw.strip() or _HEADING.match(raw):
                close(pos)
                pos += len(self.norm[k])
                close(pos)
                continue
            if _LIST_HEAD.match(raw):
                close(pos)
            pieces: "list[tuple[str, bool]]" = []
            buf: str = ""
            for j, ch in enumerate(raw):
                if ch == "|" or ch in _CIRCLED:
                    if buf:
                        pieces.append((buf, True))
                    buf = ""
                    if ch == "|":
                        pieces.append(("|", True))
                        continue
                buf += ch
                if ch == "." and (j + 1 == len(raw) or raw[j + 1].isspace()):
                    pieces.append((buf, True))
                    buf = ""
            if buf:
                pieces.append((buf, False))
            lengths: "list[int]" = [len(normalize(p)) if i == 0 else len(_inline(p))
                                    for i, (p, _b) in enumerate(pieces)]
            if sum(lengths) != len(self.norm[k]):
                pieces, lengths = [(raw, False)], [len(self.norm[k])]
            for (_piece, boundary), length in zip(pieces, lengths):
                if cur is None and length:
                    cur = pos
                pos += length
                if boundary:
                    close(pos)
        close(pos)
        return spans

    def paragraph_of(self, line: int) -> "tuple[int, int]":
        """행이 든 문단 [a, b) — 빈 줄 · 목록 머리 · 표 행 · 제목으로 끊긴다."""
        def boundary(k: int) -> bool:
            raw: str = self.lines[k]
            return (not raw.strip() or bool(_HEADING.match(raw)) or bool(_LIST_HEAD.match(raw))
                    or raw.lstrip().startswith("|"))
        a: int = line
        if not (self.lines[line].lstrip().startswith("|") or _HEADING.match(self.lines[line])):
            while a > 0 and not boundary(a) and not (a - 1 >= 0 and not self.lines[a - 1].strip()):
                if _LIST_HEAD.match(self.lines[a]) or self.lines[a - 1].lstrip().startswith("|") \
                        or _HEADING.match(self.lines[a - 1]):
                    break
                a -= 1
        b: int = line + 1
        while b < len(self.lines) and not boundary(b):
            b += 1
        return a, b

    def spaced_of(self, a: int, b: int) -> str:
        """정규화 구간 [a, b) 의 공백 한 칸 본문."""
        return self.spaced[self.n2s[a]:self.n2s[b - 1] + 1] if a < b else ""

    def line_of(self, offset: int) -> int:
        lo, hi = 0, len(self.lines)
        while lo < hi:
            mid = (lo + hi) // 2
            if self.off[mid + 1] <= offset:
                lo = mid + 1
            else:
                hi = mid
        return lo


class Corpus:
    """설치본(플랫폼) 문서 색인과 경로 사상."""

    def __init__(self, platform: "str | None" = None, root: "Path | None" = None) -> None:
        here: Path = Path(__file__).resolve().parent
        if platform is None:
            # 경로 문자열이 아니라 구조로 판별한다 — Codex 설치본 경로에는 `codex-dddjango-web` 성분이 없다.
            if (here.parent / "commands" / "dddjango-web.md").is_file():
                platform = "claude"
            elif (here.parent / "SKILL.md").is_file():
                platform = "codex"
            else:
                raise ToolError("플랫폼 판별 불가 — --platform claude|codex 와 --plugin-root 를 준다")
        self.platform: str = platform
        if root is None:
            root = here.parent if platform == "claude" else here.parent.parent.parent
        self.root: Path = root
        self._docs: "dict[str, DocIndex]" = {}

    @staticmethod
    def canon_key(raw: str) -> str:
        """리뷰어가 쓴 문서 표기 → 문서 키(Claude 표기). Codex 표기도 받는다 — Codex 는 역할 스킬
        `dddjango-web-<에이전트>`(이름이 `-web` 으로 끝남)와 지식 스킬 `dddjango-web-<스킬>` 이 모두 접두를 단다."""
        key: str = raw.strip().strip("`").strip()
        for prefix in ("dddjango-web/", "codex-dddjango-web/"):
            if key.startswith(prefix):
                key = key[len(prefix):]
        if key == "skills/dddjango-web/SKILL.md":
            return COORDINATOR
        m = re.fullmatch(r"skills/dddjango-web-([\w-]+-web)/SKILL\.md", key)
        if m:
            return f"agents/{m.group(1)}.md"
        m = re.fullmatch(r"skills/dddjango-web-([\w-]+)/(.+)", key)
        if m:
            return f"skills/{m.group(1)}/{m.group(2)}"
        return key

    def path_of(self, key: str) -> Path:
        if self.platform == "claude":
            return self.root / key
        if key == COORDINATOR:
            return self.root / "skills" / "dddjango-web" / "SKILL.md"
        m = re.fullmatch(r"agents/([\w-]+)\.md", key)
        if m:
            return self.root / "skills" / f"dddjango-web-{m.group(1)}" / "SKILL.md"
        m = re.fullmatch(r"skills/([\w-]+)/(.+)", key)
        if m:
            return self.root / "skills" / f"dddjango-web-{m.group(1)}" / m.group(2)
        return self.root / key

    def doc(self, key: str) -> DocIndex:
        if key not in self._docs:
            self._docs[key] = DocIndex(self.path_of(key))
        return self._docs[key]

    # 적용 범위 규범 문단 --------------------------------------------------
    def norm_paragraph(self) -> "tuple[int, int]":
        """Coordinator «리팩토링 모드» 절의 `**적용 범위 규범` 문단 행 범위."""
        index: DocIndex = self.doc(COORDINATOR)
        rng: "tuple[int, int] | None" = None
        for _line, _level, text, _anchor in index.headings:
            if normalize(text).startswith(normalize("리팩토링 모드")):
                rng = index.section(text)
                break
        if rng is None:
            raise ToolError("Coordinator 에 «리팩토링 모드» 절이 없다")
        for k in range(*rng):
            if normalize(index.lines[k]).startswith(normalize(f"**{NORM_HEAD}")):
                return index.paragraph_of(k)
        raise ToolError("«리팩토링 모드» 절에 적용 범위 규범 문단이 없다")

    def scope_phrases(self) -> "tuple[str, ...]":
        if not hasattr(self, "_phrases"):
            a, b = self.norm_paragraph()
            body: str = "\n".join(self.doc(COORDINATOR).lines[a:b])
            tail: str = body.split(PHRASE_MARK, 1)[1] if PHRASE_MARK in body else ""
            found: "tuple[str, ...]" = tuple(re.findall(r"«([^«»]+)»", tail))
            if not found:
                raise ToolError("적용 범위 규범 문단에 적용 한정 어구 «…» 목록이 없다")
            self._phrases: "tuple[str, ...]" = found
        return self._phrases

    def phrase_hit(self, sentence_norm: str) -> "list[str]":
        return [p for p in self.scope_phrases() if normalize(p) in sentence_norm]


def positive_hits(sentence: str, key: str) -> "list[str]":
    """문장(`normalize_spaced`)의 유효한 긍정 술어(무효 접미·`널 허용)`·앞 «만» 제외). 부정형이 있으면 빈 목록."""
    compact: str = sentence.replace(" ", "")
    if any(n in compact for n in NEGATIONS):
        return []
    patterns: "list[str]" = list(POSITIVE) + ([CAN_PREDICATE] if key in CAN_DOCS else [])
    out: "list[str]" = []
    for pat in patterns:
        for m in re.finditer(pat, sentence):
            if INVALID_SUFFIX.match(sentence, m.end()):
                continue
            if sentence[:m.start()].rstrip().endswith(RESTRICTIVE_BEFORE):
                continue
            out.append(m.group(0))
    return out


def _sentences_with(index: DocIndex, quote: str, rng: "tuple[int, int]") -> "list[tuple[int, int, int, int]]":
    """인용 출현마다 걸친 문장 — (문장 시작, 끝, 인용 시작, 끝) 정규화 오프셋."""
    sents = index.sentences(*rng)
    out: "list[tuple[int, int, int, int]]" = []
    for s, e in index.occurrences(normalize(quote), *rng):
        hit = [(a, b) for a, b in sents if a < e and s < b]
        if hit:
            out.append((hit[0][0], hit[-1][1], s, e))
    return out


# ── 대상 프로젝트 ────────────────────────────────────────────────────────────

def areas_of(files: "list[str]") -> "frozenset[str]":
    """`application/` 직속 area — 적극 증명될 때만(백스톱 area 판별과 같은 규칙): 직속 코드 파일이 없고(`__init__.py` 제외),
    자신이 4계층 폴더를 직속 보유하지 않으며, 자식 폴더가 1개 이상이고 전부 4계층 폴더를 직속 보유할 때."""
    children: "dict[str, set[str]]" = {}
    layered: "set[tuple[str, str]]" = set()
    has_file: "set[str]" = set()
    for f in files:
        s: "list[str]" = f.split("/")
        if s[0] != "application" or len(s) < 3:
            continue
        if len(s) == 3:
            if s[2] != "__init__.py" and Path(s[2]).suffix in CODE_SUFFIXES:
                has_file.add(s[1])
            continue
        children.setdefault(s[1], set()).add(s[2])
        if len(s) >= 5 and s[3] in LAYERS:
            layered.add((s[1], s[2]))
    return frozenset(x for x, ys in children.items()
                     if x not in has_file and x not in LAYERS and not (ys & LAYERS)
                     and all((x, y) in layered for y in ys))


def _bc_unit(rest: "list[str]", areas: "frozenset[str]") -> str:
    """`application/` 뒤 성분(또는 `static/application/` 뒤 성분) → BC 단위 id · BC 밖 표지 파일은 빈 문자열."""
    if rest and rest[0] in areas:
        return f"application/{rest[0]}/{rest[1]}" if len(rest) > 2 else ""
    return f"application/{rest[0]}" if len(rest) > 1 else ""


def unit_of(rel: str, areas: "frozenset[str]") -> str:
    """web 기준 상대 경로 → 단위 id(`application/[<area>/]<bc>` · `root` · `common` · `design_system` · `static/<칸>` ·
    `*.py` · 옛 배치 최상위 폴더). BC 의 미러 CSS(`static/application/…`)는 그 BC, `static/root/` 는 `root` 가 소유한다.
    외부 JS 고정 사본 · 등재 목록 · 제품 선언 · 단위 밖 표지 파일은 빈 문자열(어느 단위도 아니다)."""
    if rel in EXCLUDED_FILES or rel.startswith(EXCLUDED_PREFIXES):
        return ""
    parts: "list[str]" = rel.split("/")
    if len(parts) == 1:
        return CONTAINER
    head: str = parts[0]
    if head == "application":
        return _bc_unit(parts[1:], areas)
    if head == "static":
        if len(parts) < 3:
            return ""
        if parts[1] == "application":
            return _bc_unit(parts[2:], areas)
        return "root" if parts[1] == "root" else f"static/{parts[1]}"
    return head


def is_bc(unit: str) -> bool:
    return unit.startswith("application/")


def _unit_arg(raw: str, files: "list[str]", areas: "frozenset[str]") -> str:
    """단위 인자 → 단위 id. 단위 목록(파일 우주에서 계산)에 있어야 한다 — 단위 안쪽 경로 · area · vendor 는 받지 않는다."""
    text: str = raw.strip().rstrip("/")
    if text in ("web/*.py", "*.py"):
        return CONTAINER
    if text.startswith("web/"):
        text = text[len("web/"):]
    if not text or text.startswith("/") or ".." in text.split("/"):
        raise ToolError(f"단위 표기 오류 — {raw}")
    if (text + "/").startswith(EXCLUDED_PREFIXES) or text in EXCLUDED_FILES:
        owner: str = "사용자 결정으로만 바뀌는 제품 선언이다" if text == PRODUCT_REGISTRY else "외부 JS 승인 절차가 맡는다"
        raise ToolError(f"단위가 아니다 — `web/{text}` 는 {owner}(리팩토링 단위 밖)")
    units: "set[str]" = {unit_of(f, areas) for f in files} - {""}
    if text in units:
        return text
    if any(text.startswith(u + "/") for u in units if u != CONTAINER):
        raise ToolError(f"단위가 아니다(단위 안쪽 경로 또는 모양 오류) — {raw}")
    if any(u.startswith(text + "/") for u in units):
        raise ToolError(f"단위가 아니다(area 또는 상위 폴더 — 단위는 그 아래 BC · 칸) — {raw}")
    raise ToolError(f"단위 없음 — web/{text}")


def _lines_of(project: Path, rel: str) -> int:
    try:
        return len((project / rel).read_text(encoding="utf-8").splitlines())
    except (OSError, UnicodeDecodeError):
        return 0


def _parse_location(text: str) -> "tuple[str, int, int] | None":
    m = re.fullmatch(r"`?([^\s`:]+):(\d+)(?:-(\d+))?`?", text.strip())
    if not m:
        return None
    a: int = int(m.group(2))
    return m.group(1), a, int(m.group(3) or a)


def _locations(cell: str) -> "list[str]":
    return [t for t in re.split(r"\s*[,·]\s*|\s+", cell.strip()) if t and ":" in t]


def _ground(cell: str) -> "tuple[list[tuple[str, int, int]], str]":
    """해소 근거 칸 `<새 파일:행>[ · …] — <한 구>` 의 머리(첫 `—` 앞) 위치와 첫 불량 토큰(비면 판형) — 꼬리는 읽지 않는다.

    머리는 모든 토큰이 위치여야 한다(산문·조사가 섞이면 판형 아님 · 조용히 버리지 않는다). 절대·`..` 경로도 판형 아님.
    """
    toks: "list[str]" = [t for t in re.split(r"\s*[,·]\s*|\s+", cell.partition("—")[0].strip()) if t]
    if not toks:
        return [], "(머리 없음)"
    locs: "list[tuple[str, int, int]]" = []
    for t in toks:
        loc = _parse_location(t)
        norm: str = os.path.normpath(loc[0]).replace(os.sep, "/") if loc else ""
        if loc is None or os.path.isabs(loc[0]) or norm == ".." or norm.startswith("../"):
            return [], t
        locs.append(loc)
    return locs, ""


def _answer_state(cell: str) -> str:
    """잔존 확인 판정 칸 — `*`·백틱을 벗긴 뒤 `해소`·`판단 불가` 는 정확히, `잔존` 은 접두어로(`잔존(일부)`) 읽는다 · 그 밖 = 판단 불가."""
    text: str = re.sub(r"[*`]", "", cell).strip()
    return "잔존" if text.startswith("잔존") else text if text in ("해소", "판단 불가") else "판단 불가"


def _same_stamp(path: Path) -> "tuple[dict[str, str], list[str], dict[str, dict[str, str | None]]]":
    """같은 시각 앞 확정 판(`result.json`) — (M → 판정, 판형 아님 이력 M, 해소 지문). 없으면 빈 값 · 모양이 틀리면 실행 불능."""
    if not path.is_file():
        return {}, [], {}
    try:                                                    # 문자열 아닌 값의 `.strip`·dict 아닌 값의 `.items`·목록 아닌 redo 의 `+` 가 실패한다
        data = json.loads(path.read_text(encoding="utf-8"))
        states: "dict[str, str]" = {k: v.strip() for k, v in data.get("states", {}).items()}
        redo: "list[str]" = [m.strip() for m in data.get("redo", []) + []]
        solved: "dict[str, dict[str, str | None]]" = {m: dict(v.items()) for m, v in data.get("solved", {}).items()}
    except (TypeError, AttributeError, ValueError):
        raise ToolError(f"{path} 의 states·redo·solved 가 residual 확정 판 모양이 아니다 — 같은 시각 재확정 불가") from None
    return states, redo, solved


def _repo_path(project: Path, rel: str) -> str:
    """리뷰어 위치 경로 → 저장소 상대 경로(`web/` 없이 쓴 web 경로도 받는다)."""
    norm: str = os.path.normpath(rel).replace(os.sep, "/")
    if norm.startswith("/") or norm.startswith(".."):
        return norm
    if not (project / norm).is_file() and (project / "web" / norm).is_file():
        return "web/" + norm
    return norm


def _location_ok(project: Path, loc: "tuple[str, int, int]") -> bool:
    rel, a, b = loc
    return (project / rel).is_file() and 1 <= a <= b <= _lines_of(project, rel)


def _findings(debt: dict) -> "list[dict]":
    return list(debt.get("findings", []))


def _key_ids(debt: dict) -> "dict[str, str]":
    return {key: cid for cid, key in debt.get("ids", {}).items()}


# ── plan ─────────────────────────────────────────────────────────────────────

class PlanData:
    """plan 계산 결과(여섯 목록 + 조각)."""

    def __init__(self) -> None:
        self.unit: str = ""
        self.scope: "dict[str, str]" = {}                # web-상대 파일 → 사유
        self.cross: "dict[str, str]" = {}                # 정적 파일 → 소유 BC 들
        self.consumers: "list[str]" = []                  # `web/…:행`
        self.line_edits: "dict[str, str]" = {}           # `web/…:행` → (가)|(다)
        self.ref_lines: "list[str]" = []                  # `web/…:행`
        self.keys: "dict[str, str]" = {}                 # 키 → 표시(C<n> · 편집 줄 키)
        self.outside_refs: "list[str]" = []               # web/ 밖 `경로:행`
        self.doc_refs: "list[str]" = []                   # 문서 글 적중(알림) `docs/…:행` — 판정 목록 밖
        self.verdicts: "list[tuple[str, str, str]]" = []  # (정적 파일, 판정, 참조 줄 요약)

    def lists(self) -> "dict[str, set[str]]":
        return {"범위 파일": {"web/" + f for f in self.scope}, "경계 교차": {"web/" + f for f in self.cross},
                "경계 교차 소비자": set(self.consumers), "줄 편집": set(self.line_edits),
                "참조 치환 줄": set(self.ref_lines), "범위 안 키": set(self.keys)}


# git grep -w 의 낱말 문자(ASCII 영숫자·밑줄 — 바이트 0x80 이상은 낱말 문자가 아니다)
_WORD_EDGE: str = "A-Za-z0-9_"


class _Refs:
    """web-상대 파일의 참조 줄(6a 꼬리 grep) — 자기 자신 제외 · 저장소 상대 경로 · 파일마다 한 번만 센다.

    `warm` 이 파일 여럿의 꼬리를 git grep 두 번(경로 꼬리 -F 한 번 · 점 경로 -F -w 한 번)으로 모으고 Python 에서 파일별로
    나눈다 — 경로 꼬리는 부분 문자열, 점 경로는 앞뒤가 낱말 문자가 아닌 적중(`web.a.q` 가 `web.a.q2` 를 잡지 않는다).
    문서 글 적중(알림 pathspec)은 `warm_docs` 가 같은 꼴 두 번으로 따로 모아 `doc_memo` 에 둔다 — 판정 `memo` 와 섞지 않는다."""

    def __init__(self, project: Path) -> None:
        self.project: Path = project
        self.memo: "dict[str, list[tuple[str, int, str]]]" = {}
        self.doc_memo: "dict[str, list[tuple[str, int, str]]]" = {}

    def _gather(self, rels: "list[str]", memo: "dict[str, list[tuple[str, int, str]]]",
                lookup: "Callable[..., list[tuple[str, int, str]]]") -> None:
        tails: "dict[str, list[str]]" = {r: tail_of(r) for r in rels if r not in memo}
        if not tails:
            return
        plain = lookup(self.project, sorted({t[0] for t in tails.values()}))
        dotted = lookup(self.project, sorted({t[1] for t in tails.values() if len(t) > 1}), word=True)
        for rel, t in tails.items():
            hits: "set[tuple[str, int, str]]" = {h for h in plain if t[0] in h[2]}
            if len(t) > 1:
                edge = re.compile(rf"(?<![{_WORD_EDGE}]){re.escape(t[1])}(?![{_WORD_EDGE}])")
                hits |= {h for h in dotted if edge.search(h[2])}
            memo[rel] = sorted(h for h in hits if h[0] != "web/" + rel)

    def warm(self, rels: "list[str]") -> None:
        self._gather(rels, self.memo, reference_lines)

    def warm_docs(self, rels: "list[str]") -> None:
        self._gather(rels, self.doc_memo, doc_reference_lines)

    def __call__(self, rel: str) -> "list[tuple[str, int, str]]":
        self.warm([rel])
        return self.memo[rel]

    def docs(self, rel: str) -> "list[tuple[str, int, str]]":
        self.warm_docs([rel])
        return self.doc_memo[rel]


def _owners(refs: _Refs, rel: str, areas: "frozenset[str]", memo: "dict[str, frozenset[str]]",
            stack: "set[str]") -> "frozenset[str]":
    """정적 칸 파일의 소유자 집합 — BC 단위 id · «비BC». 순환·무참조는 빈 집합(정적 칸 단위 몫)."""
    if rel in memo:
        return memo[rel]
    if rel in stack:
        return frozenset()
    stack.add(rel)
    found: "set[str]" = set()
    for path, _line, _text in refs(rel):
        if not path.startswith("web/"):
            continue
        r: str = path[len("web/"):]
        unit: str = unit_of(r, areas)
        if is_bc(unit):
            found.add(unit)
        elif unit.startswith("static/"):
            found |= _owners(refs, r, areas, memo, stack)
        elif unit:
            found.add("비BC")
    stack.discard(rel)
    memo[rel] = frozenset(found)
    return memo[rel]


def compute_plan(project: Path, unit: str, debt: dict, files: "list[str]", areas: "frozenset[str]") -> PlanData:
    data: PlanData = PlanData()
    data.unit = unit
    for f in files:
        if unit_of(f, areas) == unit:
            data.scope[f] = "단위"
    refs: _Refs = _Refs(project)
    statics: "list[str]" = [f for f in files if unit_of(f, areas).startswith("static/")] if is_bc(unit) else []
    refs.warm(sorted(data.scope) + statics)
    if is_bc(unit):
        memo: "dict[str, frozenset[str]]" = {}
        for f in statics:                                 # 정적 칸(js · images · fonts …) — 외부 JS 고정 사본은 단위 밖
            owners: "frozenset[str]" = _owners(refs, f, areas, memo, set())
            lines: "list[str]" = [f"{p}:{n}" for p, n, _t in refs(f) if p.startswith("web/")]
            bcs: "set[str]" = {o for o in owners if o != "비BC"}
            if not owners:
                verdict = "무참조"
            elif "비BC" in owners:
                verdict = "비BC 참조"
            elif len(bcs) > 1:
                verdict = "경계 교차"
            else:
                verdict = "BC 전속"
            if unit in bcs:
                data.verdicts.append((f, verdict, " · ".join(lines[:6]) + (" …" if len(lines) > 6 else "")))
                if verdict == "BC 전속":
                    data.scope[f] = "BC 전속 정적"
                elif verdict == "경계 교차":
                    data.cross[f] = "·".join(sorted(bcs))
    scope_paths: "set[str]" = {"web/" + f for f in data.scope}
    # 경계 교차 소비자 · 줄 편집 (가) — 범위 파일을 가리키는 범위 밖 web/ 줄(소비자 = 정적 로드만 하는 줄 밖 전부)
    for f in sorted(data.scope):
        for path, line, text in refs(f):
            if not path.startswith("web/") or path in scope_paths:
                if not path.startswith("web/") and path not in scope_paths:
                    data.outside_refs.append(f"{path}:{line}")
                continue
            where: str = f"{path}:{line}"
            load: bool = bool(LOAD_LINE.search(text))
            if CONSUMER_LINE.search(text) or not load:      # 정적 로드 줄(<script>·<link>)만 빼고 모양과 무관 — import·render·문자열 포함
                data.consumers.append(where)
            if load:
                data.line_edits[where] = "(가)"
    findings: "list[dict]" = _findings(debt)
    ids: "dict[str, str]" = _key_ids(debt)

    def key_in_scope(path: str) -> bool:
        if unit == CONTAINER:
            return path == "" or (unit_of(path, areas) == CONTAINER and path in data.scope)
        # 단위 디렉터리 키(ST4 단위 키 · ST0 옛 배치 폴더 키 — 끝 `/` 유무 무관) · 단위 안 경로 · 끌어온 범위 파일
        return path.rstrip("/") == unit or path.startswith(unit + "/") or path in data.scope

    for row in findings:
        if key_in_scope(row["path"]):
            data.keys.setdefault(row["key"], ids.get(row["key"], ""))
    # 참조 치환 줄 — 범위 안 개명·이동 교정 키의 파일(폴더 키면 그 아래 파일 전부) 꼬리 적중(범위 밖 web/ 줄)
    targets: "set[str]" = set()
    for key in data.keys:
        check, path = key.split("|", 1)
        base: str = path.rstrip("/")
        if check not in RENAME_CHECKS or not base:
            continue
        targets |= {f for f in files if f == base or f.startswith(base + "/")}
    refs.warm(sorted(targets))
    for f in sorted(targets):
        for path, line, _text in refs(f):
            where = f"{path}:{line}"
            if path.startswith("web/"):
                if path not in scope_paths:
                    data.ref_lines.append(where)
            else:
                data.outside_refs.append(where)
    # 문서 글 적중(알림) — 범위 파일과 개명·이동 대상의 옛 경로 글 가운데 문서 자리(DOC_PATHSPEC) 줄. 한 묶음으로 조회한다.
    noted: "list[str]" = sorted(set(data.scope) | targets)
    refs.warm_docs(noted)
    data.doc_refs = sorted({f"{path}:{line}" for f in noted for path, line, _text in refs.docs(f)})
    # 편집 줄 키 · 키 전체 줄 (다)
    edit_lines: "set[tuple[str, int]]" = set()
    for where in list(data.line_edits) + data.ref_lines:
        path, _s, line = where.rpartition(":")
        edit_lines.add((path[len("web/"):], int(line)))
    _edit_line_keys(data, findings, ids, edit_lines)
    data.consumers = sorted(set(data.consumers))
    data.ref_lines = sorted(set(data.ref_lines))
    data.outside_refs = sorted(set(data.outside_refs))
    return data


def _edit_line_keys(data: PlanData, findings: "list[dict]", ids: "dict[str, str]",
                    edit_lines: "set[tuple[str, int]]") -> "list[str]":
    """편집 줄에 걸린 IM·PU 발견 → 편집 줄 키 · 그 키의 발견 줄 전부를 (다) 로. 새로 더한 키를 돌려준다."""
    added: "list[str]" = []
    for row in findings:
        if row["check"][:2] in EDIT_LINE_FAMILIES and (row["path"], row["line"]) in edit_lines:
            if row["key"] not in data.keys or "편집 줄 키" not in data.keys[row["key"]]:
                mark: str = (ids.get(row["key"], "") + " · 편집 줄 키").strip(" ·")
                if row["key"] not in data.keys:
                    added.append(row["key"])
                data.keys[row["key"]] = mark
    for row in findings:
        if row["key"] in data.keys and "편집 줄 키" in data.keys[row["key"]] and row["line"]:
            where: str = f"web/{row['path']}:{row['line']}"
            if row["path"] not in data.scope:
                data.line_edits.setdefault(where, "(다)")
    return added


def _chunks(project: Path, scope: "list[str]") -> "list[tuple[str, list[str], int]]":
    """계층 폴더(`…/<bc>/<계층>`)로 묶고(계층 밖은 부모 폴더) 종류 순서로 쌓아 5,000행 문턱으로 끊는다."""
    def folder(f: str) -> str:
        parts = f.split("/")
        for i, part in enumerate(parts[:-1]):
            if part in LAYERS:
                return "/".join(parts[:i + 1])
        return "/".join(parts[:-1]) or parts[0]

    def kind(f: str) -> int:
        if f.endswith(".py"):
            return 0
        return {".html": 1, ".css": 2, ".js": 3}.get(Path(f).suffix, 4)

    groups: "dict[str, list[str]]" = {}
    for f in sorted(scope, key=lambda x: (folder(x), kind(x), x)):
        groups.setdefault(folder(f), []).append(f)
    out: "list[tuple[str, list[str], int]]" = []
    cur: "list[str]" = []
    size: int = 0

    def flush() -> None:
        nonlocal cur, size
        if cur:
            out.append((f"{len(out) + 1:02d}", cur, size))
        cur, size = [], 0

    for _name, members in groups.items():
        n: int = sum(_lines_of(project, "web/" + f) for f in members)
        if cur and size + n > CHUNK_LINES:
            flush()
        if n > CHUNK_LINES:
            for f in members:
                m: int = _lines_of(project, "web/" + f)
                if cur and size + m > CHUNK_LINES:
                    flush()
                cur.append(f)
                size += m
            flush()
            continue
        cur += members
        size += n
    flush()
    return out


def _item(token: str, note: str = "") -> str:
    return f"- `{token}`" + (f" — {note}" if note else "")


def _write_plan(project: Path, data: PlanData, out: Path) -> "tuple[int, int]":
    head: str = _git(project, "rev-parse", "HEAD").strip()
    unit_path: str = "web/*.py" if data.unit == CONTAINER else f"web/{data.unit}"
    pathspec: "list[str]" = sorted({"web/" + f for f in data.scope}) or ["web/"]
    dirty: int = len([ln for ln in _git(project, "status", "--porcelain", "--untracked-files=all", "--",
                                        *pathspec).splitlines() if ln.strip()])
    chunks = _chunks(project, sorted(data.scope))
    lines: "list[str]" = ["# refactor_audit plan", "", f"- 단위: `{unit_path}`", f"- HEAD {head}",
                          f"- 범위 미커밋 변경 {dirty}",
                          f"- 범위 파일 {len(data.scope)} · 행 {sum(c[2] for c in chunks)} · 조각 {len(chunks)} · "
                          f"조각 문턱 {CHUNK_LINES}행", ""]
    lines += ["## 범위 파일", ""] + [_item("web/" + f, why) for f, why in sorted(data.scope.items())] + [""]
    if data.verdicts:
        lines += ["### 정적 파일 판정(이 BC 가 참조하는 것)", "", "| 정적 파일 | 판정 | 참조 줄 |", "|---|---|---|"]
        lines += [f"| web/{f} | {v} | {r} |" for f, v, r in data.verdicts] + [""]
    lines += ["## 경계 교차", ""] + ([_item("web/" + f, "소유 " + o) for f, o in sorted(data.cross.items())]
                                   or ["- 없음"]) + [""]
    lines += ["## 경계 교차 소비자", ""] + ([_item(w) for w in data.consumers] or ["- 없음"]) + [""]
    lines += ["## 줄 편집", ""] + ([_item(w, t) for w, t in sorted(data.line_edits.items())] or ["- 없음"]) + [""]
    lines += ["## 참조 치환 줄", ""] + ([_item(w) for w in data.ref_lines] or ["- 없음"]) + [""]
    lines += ["## 범위 안 키", ""] + ([_item(k, v) for k, v in sorted(data.keys.items())] or ["- 없음"]) + [""]
    lines += ["## web/ 밖 참조 줄(치환 후보)", ""] + ([_item(w) for w in data.outside_refs] or ["- 없음"]) + [""]
    lines += [f"## {DOC_SECTION}", ""] + ([_item(w) for w in data.doc_refs] or ["- 없음"]) + [""]
    lines += ["## 조각", "", "| 조각 | 파일 수 | 행 수 |", "|---|---|---|"]
    lines += [f"| {cid} | {len(g)} | {n} |" for cid, g, n in chunks]
    for cid, group, _n in chunks:
        lines += ["", f"### 조각 {cid} 파일", ""] + [f"- web/{f}" for f in group]
    lines += ["", "## 파견", "", "| 산출 파일 | 렌즈 | 조각 | 리뷰어 |", "|---|---|---|---|"]
    lines += [f"| {lens}-{cid}.md | {lens} | {cid} | dddjango-web:{REVIEWERS[lens]} |"
              for lens in LENSES for cid, _g, _n in chunks]
    lines += ["", "## 렌즈별 점검 절", ""]
    for lens in LENSES:
        lines += [f"### {lens}"] + [f"- {t}" for t in LENS_SECTIONS[lens]] + [""]
    out.mkdir(parents=True, exist_ok=True)
    (out / "plan.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return len(chunks), dirty


def _parse_lists(text: str) -> "dict[str, set[str]]":
    out: "dict[str, set[str]]" = {}
    for name in AGAINST_LISTS:
        m = re.search(rf"^## {re.escape(name)}\n(.*?)(?=^## |\Z)", text, re.M | re.S)
        body: str = m.group(1) if m else ""
        out[name] = set(re.findall(r"^- `([^`]+)`", body, re.M))
    return out


def _load_debt(path: Path) -> dict:
    try:
        return json.loads(_read(path))
    except json.JSONDecodeError as exc:
        raise ToolError(f"debt-g0.json 파싱 실패 — {exc}") from None


def _against_state(project: Path, unit: str, text: str, files: "list[str]") -> "list[str]":
    """G0 정지 재개 조건 ①~③ — 기록 plan 의 `범위 미커밋 변경 0` · 기록 HEAD 이후 범위 파일 무변(작업 트리 포함) ·
    범위 미추적 0. git 을 인자 목록으로 불러 경로가 셸에서 갈라지거나 합쳐지지 않는다."""
    out: "list[str]" = []
    dirty = re.search(r"^- 범위 미커밋 변경 (\d+)$", text, re.M)
    if not dirty or dirty.group(1) != "0":
        print(f"  다름: ① 기록 plan 의 범위 미커밋 변경 — {dirty.group(1) if dirty else '행 없음'}")
        out.append("①")
    head = re.search(r"^- HEAD ([0-9a-f]{7,40})$", text, re.M)
    if not head:
        print("  다름: ② 기록 plan 에 HEAD 가 없다")
        out.append("②")
    elif files:
        changed: "list[str]" = [f for f in _git(project, "diff", "--name-only", head.group(1), "--", *files).splitlines() if f]
        if changed:
            print(f"  다름: ② 기록 HEAD {head.group(1)[:9]} 이후 범위 파일 변경 {changed[:3]}")
            out.append("②")
    roots: "list[str]" = files + ([] if unit == CONTAINER else [f"web/{unit}"]) + \
        ([f"web/static/{unit}"] if is_bc(unit) else ["web/static/root"] if unit == "root" else [])
    untracked: "list[str]" = [f for f in _git(project, "ls-files", "--others", "--exclude-standard", "--",
                                              *roots).splitlines() if f] if roots else []
    if untracked:
        print(f"  다름: ③ 범위 미추적 파일 {untracked[:3]}")
        out.append("③")
    return out


def cmd_plan(project: Path, raw_unit: str, debt_path: Path, out: "Path | None", against: "Path | None",
             names: "Path | None") -> int:
    decl_error: "str | None" = declaration_error(project)  # 제품 선언 preflight — 오류면 판정 불가(exit 1)
    if decl_error is not None:
        raise ToolError(f"판정 불가 — {decl_error}")
    files: "list[str]" = debt_universe(project)
    areas: "frozenset[str]" = areas_of(files)
    unit: str = _unit_arg(raw_unit, files, areas)
    debt: dict = _load_debt(debt_path)
    data: PlanData = compute_plan(project, unit, debt, files, areas)
    if against is not None:
        text: str = _read(against)
        stored: "dict[str, set[str]]" = _parse_lists(text)
        now: "dict[str, set[str]]" = data.lists()
        diff: "list[str]" = [n for n in AGAINST_LISTS if stored[n] != now[n]]
        for n in diff:
            print(f"  다름: {n} — 기록만 {sorted(stored[n] - now[n])[:3]} · 지금만 {sorted(now[n] - stored[n])[:3]}")
        diff += _against_state(project, unit, text, sorted(stored["범위 파일"]))
        print(f"요약: plan --against {'같음' if not diff else '다름 ' + '·'.join(diff)} → {against}")
        return EXIT_RED if diff else EXIT_OK
    if out is None:
        raise ToolError("--out 또는 --against 가 필요하다")
    if names is not None:
        return _plan_names(project, data, debt, names, out)
    if (out / "plan.md").exists():
        raise ToolError(f"{out / 'plan.md'} 가 이미 있다 — 덮지 않는다(재개 대조는 --against)")
    chunks, dirty = _write_plan(project, data, out)
    print(f"요약: plan 단위 {raw_unit} · 범위 파일 {len(data.scope)} · 경계 교차 {len(data.cross)} · "
          f"소비자 {len(data.consumers)} · 줄 편집 {len(data.line_edits)} · 참조 치환 줄 {len(data.ref_lines)} · "
          f"범위 안 키 {len(data.keys)} · 조각 {chunks} · 파견 {chunks * len(LENSES)} · 미커밋 {dirty} · "
          f"문서 글 적중 {len(data.doc_refs)} → {out / 'plan.md'}")
    return EXIT_OK


def _plan_names(project: Path, data: PlanData, debt: dict, names: Path, out: Path) -> int:
    """명세 `## 슬라이스 0` 절의 `경로:`·`이름:` → 명세 참조 줄 (나) · 편집 줄 키 · 키 전체 줄."""
    try:
        paths, pairs = parse_spec_pairs(_read(names), require=True)
    except DebtError as exc:
        raise ToolError(str(exc)) from None
    scope_paths: "set[str]" = {"web/" + f for f in data.scope}
    files: "list[str]" = debt_universe(project)
    commands: "list[str]" = []
    found: "dict[str, str]" = {}
    docs: "dict[str, str]" = {}                       # 문서 글 적중(알림) `경로:행` → 사유 — (나) 줄이 아니다

    def keep(hits: "list[tuple[str, int, str]]", why: str) -> None:
        for path, line, _text in hits:
            if path.startswith("web/") and path not in scope_paths:
                found.setdefault(f"{path}:{line}", why)

    def note(hits: "list[tuple[str, int, str]]", why: str) -> None:
        for path, line, _text in hits:                # 같은 줄이 여러 꼬리에 걸려도 한 번만
            docs.setdefault(f"{path}:{line}", why)

    for old, _new in paths:                           # 한 쌍의 구성원은 표지가 같다 — 쌍마다 -F 한 번 · -F -w 한 번(합집합)
        members: "list[str]" = [f for f in files if f.startswith(old)] if old.endswith("/") else [old]
        plain: "list[str]" = []
        dotted: "list[str]" = []
        for f in members:
            tails = tail_of(f)
            plain.append(tails[0])
            commands += [_grep_command(tails[0], REF_PATHSPEC), _grep_command(tails[0], DOC_PATHSPEC)]
            if len(tails) > 1:
                dotted.append(tails[1])
                commands += [_grep_command(tails[1], REF_PATHSPEC, word=True),
                             _grep_command(tails[1], DOC_PATHSPEC, word=True)]
        keep(reference_lines(project, plain), f"경로 `{old}`")
        keep(reference_lines(project, dotted, word=True), f"경로 `{old}`")
        note(doc_reference_lines(project, plain), f"경로 `{old}`")       # 알림 조회도 쌍마다 같은 꼴 두 번
        note(doc_reference_lines(project, dotted, word=True), f"경로 `{old}`")
    for old, _new in pairs:
        module, name = old.rsplit(".", 1)
        module_hits = reference_lines(project, [module], word=True)
        commands += [_grep_command(module, REF_PATHSPEC, word=True), _grep_command(module, DOC_PATHSPEC, word=True)]
        keep(module_hits, f"이름 `{old}`(모듈)")
        note(doc_reference_lines(project, [module], word=True), f"이름 `{old}`(모듈)")
        importers: "list[str]" = sorted({p for p, _l, _t in module_hits if p.startswith("web/")})
        if importers:
            # 맨 이름은 옛 모듈을 참조하는 파일에서만 — BC 마다 같은 이름 helper 를 두는 정형(반복 > 상속).
            keep(reference_lines(project, [name], word=True, paths=importers), f"이름 `{old}`")
            commands.append(_grep_command(name, importers, word=True))
    findings: "list[dict]" = _findings(debt)
    ids: "dict[str, str]" = _key_ids(debt)
    before: "set[str]" = set(data.line_edits)
    lines_set: "set[tuple[str, int]]" = {(w.rpartition(":")[0][len("web/"):], int(w.rpartition(":")[2]))
                                         for w in found}
    new_keys: "list[str]" = _edit_line_keys(data, findings, ids, lines_set)
    key_full: "list[str]" = sorted(w for w in data.line_edits if w not in before)
    body: "list[str]" = [f"# plan --names — {_now()}", "", f"- 명세: `{names}`",
                         f"- 쌍: 경로 {len(paths)} · 이름 {len(pairs)}", "", "## 명세 참조 줄 (나)", ""]
    body += [_item(w, why) for w, why in sorted(found.items())] or ["- 없음"]
    body += ["", "## 편집 줄 키(G0 재승인 대상)", ""]
    body += [_item(k, data.keys[k]) for k in sorted(new_keys)] or ["- 없음"]
    body += ["", "## 키 전체 줄 (다)", ""] + ([_item(w) for w in key_full] or ["- 없음"])
    body += ["", f"## {DOC_SECTION}", ""] + ([_item(w, why) for w, why in sorted(docs.items())] or ["- 없음"])
    body += ["", "## grep 명령", ""] + [f"- `{c}`" for c in commands] + [""]
    out.mkdir(parents=True, exist_ok=True)
    (out / "plan-names.md").write_text("\n".join(body), encoding="utf-8")
    print(f"요약: plan --names 쌍 경로 {len(paths)} · 이름 {len(pairs)} · (나) 줄 {len(found)} · "
          f"편집 줄 키 {len(new_keys)} · 키 전체 줄 {len(key_full)} · 문서 글 적중 {len(docs)} → {out / 'plan-names.md'}")
    return EXIT_OK


# ── audit 폴더 읽기 ──────────────────────────────────────────────────────────

def _table_rows(text: str) -> "list[list[str]]":
    """표 행 → 칸. 칸 안의 `\\|`(키 문자열 `검사|경로`)는 구분자가 아니다."""
    rows: "list[list[str]]" = []
    for ln in text.splitlines():
        s: str = ln.strip()
        if not s.startswith("|") or re.fullmatch(r"\|[\s:|-]*\|", s):
            continue
        inner: str = s[1:-1] if s.endswith("|") and not s.endswith("\\|") else s[1:]
        rows.append([c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", inner)])
    return rows


class Plan:
    """plan.md(+ plan-names.md) 에서 읽는 판정 재료."""

    def __init__(self, audit: Path) -> None:
        text: str = _read(audit / "plan.md")
        m = re.search(r"^- 단위: `([^`]+)`", text, re.M)
        if not m:
            raise ToolError("plan.md 에 단위 줄이 없다")
        self.unit: str = m.group(1)
        lists: "dict[str, set[str]]" = _parse_lists(text)
        self.scope: "set[str]" = lists["범위 파일"]
        self.keys: "set[str]" = lists["범위 안 키"]
        self.allowed: "dict[str, set[int]]" = {}
        for name in ("줄 편집", "참조 치환 줄"):
            for w in lists[name]:
                path, _s, line = w.rpartition(":")
                self.allowed.setdefault(path, set()).add(int(line))
        names: Path = audit / "plan-names.md"
        if names.is_file():
            for w in set(re.findall(r"^- `([^`]+:\d+)`", _read(names), re.M)):
                path, _s, line = w.rpartition(":")
                if path.startswith("web/"):            # (나)·(다) 는 web/ 줄뿐이다 — 문서 글 적중 절의 줄은 편집 허용 줄이 아니다
                    self.allowed.setdefault(path, set()).add(int(line))
        sec: str = text.split("## 파견", 1)[1].split("\n## ", 1)[0] if "## 파견" in text else ""
        self.dispatch: "list[tuple[str, str, str]]" = [(r[0], r[1], r[2]) for r in _table_rows(sec)
                                                      if len(r) >= 3 and r[0].endswith(".md")]
        if not self.dispatch:
            raise ToolError("plan.md 에 파견 표가 없다")

    def in_scope(self, loc: "tuple[str, int, int]") -> bool:
        rel, a, b = loc
        return rel in self.scope or all(k in self.allowed.get(rel, set()) for k in range(a, b + 1))


class Row:
    """리뷰어 표 한 행 — `행# | 규칙 | 반대 방향 규칙 | 파일:행 | 위반 요지 | 동작 불변 정리 가능 | 편집할 곳 | 같은 검사기 키`."""

    def __init__(self, rid: str, lens: str, cells: "list[str]", short: bool = False) -> None:
        self.rid: str = rid
        self.short: bool = short
        self.lens: str = lens
        self.cells: "list[str]" = cells
        self.rule: str = cells[1]
        self.opposite: str = cells[2] if cells[2] not in ("", "—", "-", "없음") else ""
        self.where: str = cells[3]
        self.gist: str = cells[4]
        self.fixable: str = cells[5]
        self.edit_at: str = cells[6]
        self.same_key: str = cells[7]
        self.status: str = ""
        self.reason: str = ""
        self.key: str = ""
        self.section: "tuple[int, int] | None" = None
        self.quote: str = ""

    @property
    def no_rule(self) -> bool:
        return bool(re.search(r"근거 없음\s*\(\s*불편", self.rule))


_CITE: "re.Pattern[str]" = re.compile(r"^(?:규칙\s*=\s*)?`?(?P<doc>[^\s§`]+)`?\s*§\s*(?P<sec>[^«]+?)\s*«(?P<q>.*)»\s*$")


def _cite(cell: str) -> "tuple[str, str, str] | None":
    m = _CITE.match(cell.strip())
    return (m.group("doc"), m.group("sec"), m.group("q")) if m else None


_ROW_LOCATION: "re.Pattern[str]" = re.compile(r"(?<![\w/.-])web/[^\s|`,·]+:\d+")


def _load_rows(audit: Path, plan: Plan) -> "list[Row]":
    rows: "list[Row]" = []
    for name, lens, _cid in plan.dispatch:
        path: Path = audit / name
        if not path.is_file():
            raise ToolError(f"리뷰어 산출 누락 — {path}")
        for k, cells in enumerate(_table_rows(path.read_text(encoding="utf-8")), 1):
            if cells and (cells[0] in ("행#", "행") or cells[0].startswith("행#")):
                continue
            numbered: bool = bool(re.fullmatch(r"\d+", cells[0])) if cells else False
            located: bool = any(_ROW_LOCATION.search(c) for c in cells)
            if len(cells) < 6 and not numbered and not located:
                continue
            short: bool = len(cells) < 6
            while len(cells) < 8:
                cells.append("")
            no: str = cells[0] if numbered else str(k)
            rows.append(Row(f"{name[:-3]}#{no}", lens, cells, short))
    return rows


def _resolve_cite(corpus: Corpus, cell: str) -> "tuple[str, tuple[int, int], str] | str":
    """인용 칸 → (문서 키, 절 범위, 인용) 또는 실패 사유."""
    cite = _cite(cell)
    if not cite:
        return "규칙 칸 형식(`<문서> §<절> «인용»`) 아님"
    key: str = corpus.canon_key(cite[0])
    if not corpus.path_of(key).is_file():
        return f"문서 없음 `{cite[0]}`"
    rng = corpus.doc(key).section(cite[1])
    if rng is None:
        return f"절 없음 `{cite[0]} §{cite[1]}`"
    if not corpus.doc(key).occurrences(normalize(cite[2]), *rng):
        return f"인용이 `{cite[0]} §{cite[1]}` 본문에 없다"
    return key, rng, cite[2]


def _check_rows(corpus: Corpus, project: Path, plan: Plan, rows: "list[Row]") -> None:
    for row in rows:
        if row.short:
            row.status, row.reason = "인용 불일치", "칸 부족(산출 표 8칸 형식 아님)"
            continue
        if row.no_rule:
            row.status = "불편"
            continue
        got = _resolve_cite(corpus, row.rule)
        if isinstance(got, str):
            row.status, row.reason = "인용 불일치", got
            continue
        locs = [_parse_location(t) for t in _locations(row.where)]
        if not locs or any(loc is None for loc in locs):
            row.status, row.reason = "인용 불일치", f"파일:행 형식 아님 `{row.where}`"
            continue
        fixed = [(_repo_path(project, l[0]), l[1], l[2]) for l in locs if l]
        bad = [f"{l[0]}:{l[1]}" for l in fixed if not (_location_ok(project, l) and plan.in_scope(l))]
        if bad:
            row.status, row.reason = "인용 불일치", f"위치가 작업 트리에 없거나 범위 밖: {', '.join(bad[:3])}"
            continue
        row.status = "통과"
        row.key, row.section, row.quote = got


# ── check ────────────────────────────────────────────────────────────────────

def cmd_check(corpus: Corpus, project: Path, audit: Path) -> int:
    plan: Plan = Plan(audit)
    rows: "list[Row]" = _load_rows(audit, plan)
    _check_rows(corpus, project, plan, rows)
    passed = [r for r in rows if r.status == "통과"]
    bad = [r for r in rows if r.status == "인용 불일치"]
    no_rule = [r for r in rows if r.status == "불편"]
    lines: "list[str]" = [f"# check — `{plan.unit}` · {_now()}", "", "| 원 행 | 상태 | 문서 | 파일:행 | 사유 |",
                          "|---|---|---|---|---|"]
    lines += [f"| {r.rid} | {r.status} | {r.key or '—'} | {r.where} | {r.reason} |" for r in rows]
    lines += ["", "## 인용 불일치(원 리뷰어 재인용 대상 — 행 목록만)", ""]
    lines += [f"- {r.rid}: {r.reason}" for r in bad] or ["- 없음"]
    (audit / "check.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"요약: check 행 {len(rows)} · 통과 {len(passed)} · 인용 불일치 {len(bad)} · 규칙 근거 없는 불편 "
          f"{len(no_rule)} → {audit / 'check.md'}")
    return EXIT_RED if bad else EXIT_OK


# ── check-verdict ────────────────────────────────────────────────────────────

class Verdict:
    """판정 표 한 행 — `M<n> | 원 행 | 판정 | 근거 | 파일:행 목록`."""

    def __init__(self, cells: "list[str]") -> None:
        self.mid: str = cells[0].strip()
        self.origin: "list[str]" = [t for t in re.split(r"\s*[,·]\s*|\s+", cells[1].strip()) if t]
        raw: str = re.sub(r"\s+", " ", cells[2].strip())
        m = re.fullmatch(r"병합\s*(?:→|->)\s*(\S+)", raw)
        self.kind: str = "병합" if m else raw if not raw.startswith("병합") else f"{raw}(대상 없음)"
        self.merge_to: str = m.group(1).strip("`") if m else ""
        self.ground: str = cells[3].strip() if len(cells) > 3 else ""
        self.where: str = cells[4].strip() if len(cells) > 4 else ""

    @property
    def label(self) -> str:
        if self.kind == "병합" and self.merge_to:
            return "병합→M" if re.fullmatch(r"M\d+", self.merge_to) else "병합→검사기"
        return self.kind


VERDICT_FINAL: str = "verdict-final.md"


def _load_verdicts(audit: Path, name: str = "verdict.md") -> "list[Verdict]":
    return [Verdict(c) for c in _table_rows(_read(audit / name))
            if c and re.fullmatch(r"M\d+", c[0].strip()) and len(c) >= 3]


def _write_final(audit: Path, verdicts: "list[Verdict]", final: bool) -> None:
    """exit 0 판의 확정 표 — G0 목록·잇기·G2 residual 이 읽는 한 목록(`--final` 재분류 포함)."""
    def cell(text: str) -> str:
        return text.replace("|", "\\|")

    out: "list[str]" = [f"# verdict-final — check-verdict exit 0 {_now()}{' · final' if final else ''}", "",
                        "| M | 원 행 | 판정 | 근거 | 파일:행 목록 |", "|---|---|---|---|---|"]
    for v in verdicts:
        kind: str = f"병합 → {v.merge_to}" if v.kind == "병합" else v.kind
        out.append(f"| {v.mid} | {' · '.join(v.origin)} | {cell(kind)} | {cell(v.ground)} | {cell(v.where)} |")
    (audit / VERDICT_FINAL).write_text("\n".join(out) + "\n", encoding="utf-8")


def _previous(log: Path) -> "tuple[dict[str, str], dict[str, str]]":
    """verdict-log.md 의 마지막 확정(exit 0) 판 — (M → 판정, 원 행 → M)."""
    if not log.is_file():
        return {}, {}
    parts: "list[str]" = re.split(r"(?m)^## check-verdict ", log.read_text(encoding="utf-8"))[1:]
    for part in reversed(parts):
        if not re.search(r"· exit 0\b", part.splitlines()[0]):
            continue
        kinds: "dict[str, str]" = {}
        origin: "dict[str, str]" = {}
        for cells in _table_rows(part):
            if len(cells) >= 3 and re.fullmatch(r"M\d+", cells[0]):
                kinds[cells[0]] = cells[2]
                for o in re.split(r"\s*[,·]\s*|\s+", cells[1]):
                    if o:
                        origin[o] = cells[0]
        return kinds, origin
    return {}, {}


def _proxy_source(source: str) -> bool:
    m = re.match(r"\s*출처\s*=\s*(.*)$", source)
    return not (m and m.group(1).strip().startswith(PROXY_FREE))


def _source(feedback: "Path | None") -> str:
    if feedback is None:
        return ""
    first: str = next((ln.strip() for ln in _read(feedback).splitlines() if ln.strip()), "")
    if not first:
        raise ToolError(f"--feedback 첫 줄에 결정 출처가 없다 — {feedback}")
    return first


def _in_norm(corpus: Corpus, key: str, spans: "list[tuple[int, int]]") -> bool:
    """인용이 적용 범위 규범 문단 자신인가."""
    if key != COORDINATOR:
        return False
    try:
        a, b = corpus.norm_paragraph()
    except ToolError:
        return False
    index: DocIndex = corpus.doc(key)
    lo, hi = index.off[a], index.off[b]
    return any(lo <= s and e <= hi for s, e in spans)


def _wrapped(sentence: str, rel: int) -> bool:
    """문장 안 인용 위치가 괄호 부속절 `(…)` 안이거나 `예외:` 뒤인가."""
    before: str = sentence[:rel]
    return before.count("(") > before.count(")") or EXCEPTION_COLON in before


def _exclusion(corpus: Corpus, row: Row, v: Verdict) -> str:
    got = _resolve_cite(corpus, v.ground)
    if isinstance(got, str):
        return f"① {got}"
    key, rng, quote = got
    index: DocIndex = corpus.doc(key)
    found = _sentences_with(index, quote, rng)
    if _in_norm(corpus, key, [(s, e) for _a, _b, s, e in found]):
        return "③ 인용이 적용 범위 규범 문단 자신이다"
    if not key.startswith(RULE_DOC_PREFIXES):
        return f"① 근거 문서가 규칙 문서(skills/·agents/)가 아니다 — `{key}`"
    valid: bool = False
    for a, b, s, e in found:
        sentence: str = index.text[a:b]
        if corpus.phrase_hit(sentence):
            return f"③ 인용이 든 문장에 적용 한정 어구 «{corpus.phrase_hit(sentence)[0]}»"
        if positive_hits(index.spaced_of(a, b), key):
            valid = True
    if not valid:
        return "② 인용이 든 문장에 유효한 긍정 술어가 없다(또는 부정형이 있다)"
    if row.key == key and row.section is not None:
        mine = [(s, e) for _a, _b, s, e in found]
        theirs = _sentences_with(index, row.quote, row.section)
        if any(s < d and c < e for s, e in mine for _x, _y, c, d in theirs):
            return "④ 제외 인용이 위반 인용 구간과 겹친다"
        for a, b, s, _e in found:
            if any(a == x and b == y for x, y, _c, _d in theirs) and not _wrapped(index.text[a:b], s - a):
                return "⑤ 제외 인용과 위반 인용이 같은 문장이다(괄호 부속절·`예외:` 뒤가 아니다)"
    return ""


def _false_positive(corpus: Corpus, row: Row, v: Verdict) -> str:
    m = re.search(r"«(.*)»", v.ground)
    if not m:
        return "오탐 근거 형식(`«요건 문구»`) 아님"
    if row.section is None:
        return "위반 행 인용을 찾을 수 없다"
    index: DocIndex = corpus.doc(row.key)
    theirs = index.occurrences(normalize(row.quote), *row.section)
    paras = {index.paragraph_of(index.line_of(s)) for s, _e in theirs}
    for a, b in paras:
        found = _sentences_with(index, m.group(1), (a, b))
        if found:
            if any(s < d and c < e for _sa, _sb, s, e in found for c, d in theirs):
                return "오탐 인용이 위반 인용 구간과 겹친다(요건 문구가 아니라 위반 문구다)"
            for sa, sb, _s, _e in found:
                hit = corpus.phrase_hit(index.text[sa:sb])
                if hit:
                    return f"오탐 인용이 든 문장에 적용 한정 어구 «{hit[0]}»"
            return ""
    return "오탐 인용이 위반으로 인용된 그 문단에 없다(같은 절 다른 문단 불가)"


def _user_judgment(corpus: Corpus, row: Row) -> str:
    if not row.opposite:
        return "사용자 판단인데 리뷰어 행에 반대 방향 규칙이 없다"
    got = _resolve_cite(corpus, row.opposite)
    if isinstance(got, str):
        return f"반대 방향 규칙 — {got}"
    key, rng, quote = got
    index: DocIndex = corpus.doc(key)
    found = _sentences_with(index, quote, rng)
    if _in_norm(corpus, key, [(s, e) for _a, _b, s, e in found]):
        return "반대 방향 규칙이 적용 범위 규범 자신이다"
    for a, b, _s, _e in found:
        hit = corpus.phrase_hit(index.text[a:b])
        if hit:
            return f"반대 방향 규칙 인용이 든 문장에 적용 한정 어구 «{hit[0]}» — 결정 18 이 가른 충돌"
    return ""


def _call_spans(tree: ast.AST, names: "tuple[str, ...]") -> "list[tuple[int, int, ast.Call]]":
    out: "list[tuple[int, int, ast.Call]]" = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            fn = node.func
            name: str = fn.id if isinstance(fn, ast.Name) else fn.attr if isinstance(fn, ast.Attribute) else ""
            if name in names:
                out.append((node.lineno, getattr(node, "end_lineno", node.lineno), node))
    return out


def _module_strings(tree: ast.Module) -> "dict[str, str]":
    out: "dict[str, str]" = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            for t in node.targets:
                if isinstance(t, ast.Name):
                    out[t.id] = node.value.value
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and \
                isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            out[node.target.id] = node.value.value
    return out


def _external_behavior(project: Path, locs: "list[tuple[str, int, int]]") -> bool:
    for rel, a, b in locs:
        path: Path = project / rel
        if not path.is_file():
            continue
        text: str = path.read_text(encoding="utf-8", errors="replace")
        body: "list[str]" = text.splitlines()[a - 1:b]
        if rel.endswith(".html") and any("{% url " in ln for ln in body):
            return True
        if not rel.endswith(".py"):
            continue
        try:
            tree = ast.parse(text)
        except SyntaxError:
            continue
        if Path(rel).name == "urls.py" or Path(rel).name.endswith("_router.py"):
            if any(s <= b and a <= e for s, e, _n in _call_spans(tree, ("path", "re_path"))):
                return True
        if "/view/" in rel:
            if any("HX-" in ln for ln in body):
                return True
            consts: "dict[str, str]" = _module_strings(tree)
            for s, e, call in _call_spans(tree, ("render", "TemplateResponse")):
                if not (s <= b and a <= e):
                    continue
                arg = call.args[1] if len(call.args) > 1 else next(
                    (k.value for k in call.keywords if k.arg == "template_name"), None)
                value: "str | None" = (arg.value if isinstance(arg, ast.Constant) and isinstance(arg.value, str)
                                       else consts.get(arg.id) if isinstance(arg, ast.Name) else None)
                if value and ("/section/" in value or value.startswith("section/")):
                    return True
    return False


# JSON 키 리터럴 — `.get("k")` · `["k"]` · `json_field(data, "k", …)`·`f(payload, "k")`(쉼표 뒤 리터럴 다음이 `,` 또는 `)`)
_KEY_LITERAL: "re.Pattern[str]" = re.compile(r"""\.get\(\s*(["'])([^"']+)\1|\[\s*(["'])([^"']+)\3\s*\]|,\s*(["'])([^"']+)\5\s*[,)]""")
_URL_LITERAL: "re.Pattern[str]" = re.compile(r"""(["'])(/[^"']*)\1""")
_ASSIGN_NAME: "re.Pattern[str]" = re.compile(r"^\s*([A-Za-z_]\w*)\s*(?::[^=]+)?=(?!=)")


def _contract_kind(rel: str) -> str:
    """계약을 소비하는 자리 — infra_layer · common/network(URL · JSON 키) · domain_layer(모델 `from_json` 의 JSON 키)."""
    if not (rel.startswith("web/") and rel.endswith(".py")):
        return ""
    if "/infra_layer/" in rel or rel.startswith("web/common/network/"):
        return "url"
    return "key" if "/domain_layer/" in rel else ""


def _api_contract(project: Path, locs: "list[tuple[str, int, int]]", ground: str) -> bool:
    for rel, a, b in locs:
        kind: str = _contract_kind(rel)
        if not kind or not (project / rel).is_file():
            continue
        for ln in (project / rel).read_text(encoding="utf-8", errors="replace").splitlines()[a - 1:b]:
            literals: "list[str]" = [g for m in _KEY_LITERAL.finditer(ln) for g in (m.group(2), m.group(4), m.group(6)) if g]
            if kind == "url":
                literals += [m.group(2) for m in _URL_LITERAL.finditer(ln)]
            assigned = _ASSIGN_NAME.match(ln)
            kwarg = re.match(r"^\s*([A-Za-z_]\w*)\s*=", ln)
            target: str = (assigned or kwarg).group(1) if (assigned or kwarg) else ""
            for lit in literals:
                if lit == target:
                    continue   # 속성 이름 = 키 — 이름 정리와 가를 수 없다(채택 → ⓑ 로 fail-closed)
                if f'"{lit}"' in ground or f"'{lit}'" in ground:
                    return True
    return False


def _separate(corpus: Corpus, project: Path, plan: Plan, row: Row, v: Verdict) -> str:
    """별도 요청 근거 — 실패 사유(비면 통과). 실패는 채택 재분류다."""
    if not row.fixable.startswith("아니오"):
        return "리뷰어 «동작 불변 정리 가능 = 아니오» 없음"
    kind = next((t for t in SEPARATE_TYPES if t in v.ground), None)
    if kind is None:
        return "근거 유형(외부 동작 · API 계약 · 경계 교차 · web/ 밖) 없음"
    locs = [(_repo_path(project, l[0]), l[1], l[2]) for l in
            (_parse_location(t) for t in _locations(row.where)) if l]
    if kind == "외부 동작":
        return "" if _external_behavior(project, locs) else \
            "항목 위치가 urls `path(` 구간 · `{% url` · view `HX-` · section 템플릿 render 호출이 아니다"
    if kind == "API 계약":
        return "" if _api_contract(project, locs, v.ground) else \
            "DataSource·모델 from_json 의 JSON 키·URL 리터럴 행과 근거 칸의 같은 리터럴이 없다(속성 이름 = 키 행 제외)"
    edits = [(_repo_path(project, l[0]), l[1], l[2]) for l in
             (_parse_location(t) for t in _locations(row.edit_at)) if l]
    edits = [l for l in edits if _location_ok(project, l)]
    if not edits:
        return "편집할 곳 `파일:행` 이 없거나 실재하지 않는다"
    if kind == "web/ 밖":
        from src.debt import is_test_path  # noqa: PLC0415
        return "" if any(not l[0].startswith("web/") and not is_test_path(l[0]) for l in edits) else \
            "편집할 곳이 web/ 밖 비테스트 파일이 아니다"
    own: "set[str]" = {m for l in locs if l[0].startswith("web/") for m in [module_of(l[0][len("web/"):])] if m}
    for rel, a, b in edits:
        if not rel.startswith("web/") or rel in plan.scope or plan.in_scope((rel, a, b)):
            continue
        body = (project / rel).read_text(encoding="utf-8", errors="replace").splitlines()[a - 1:b]
        if any(re.match(r"\s*(from|import)\s+web\.", ln) and any(re.search(rf"\b{re.escape(m)}\b", ln) for m in own)
               for ln in body):
            continue   # 정의 이동·모듈 개명의 소비 import 줄 — (나) 가 편집 범위로 연다
        return ""
    return "편집할 곳이 범위 밖 web/ 줄 편집 목록 밖이 아니다(또는 항목 모듈의 import 줄)"


def _judge(corpus: Corpus, project: Path, plan: Plan, verdicts: "list[Verdict]", by_id: "dict[str, Row]",
           passed: "set[str]") -> "tuple[list[tuple[str, str, str]], list[tuple[str, str]]]":
    reds: "list[tuple[str, str, str]]" = []
    reclass: "list[tuple[str, str]]" = []
    seen_m: "set[str]" = set()
    covered: "dict[str, str]" = {}
    for v in verdicts:
        if v.mid in seen_m:
            reds.append((v.mid, "구조", "M 번호 중복"))
        seen_m.add(v.mid)
        if v.kind not in VERDICTS:
            reds.append((v.mid, "판정", f"판정 범주 밖 `{v.kind}`"))
        for o in v.origin:
            if o not in passed:
                reds.append((v.mid, "구조", f"원 행 {o} 이 check 통과 행이 아니다"))
            elif o in covered:
                reds.append((v.mid, "구조", f"원 행 {o} 이 {covered[o]} 와 두 번 판정됐다"))
            else:
                covered[o] = v.mid
    for o in sorted(passed - set(covered)):
        reds.append((o, "판정 없음", f"통과 행 {o} 에 판정이 없다"))
    kinds: "dict[str, str]" = {v.mid: v.kind for v in verdicts}
    for v in verdicts:
        row_list: "list[Row]" = [by_id[o] for o in v.origin if o in by_id and o in passed]
        if not row_list or v.kind not in VERDICTS:
            continue
        why: str = ""
        if v.kind == "제외":
            why = next((w for w in (_exclusion(corpus, r, v) for r in row_list) if w), "")
        elif v.kind == "오탐":
            why = next((w for w in (_false_positive(corpus, r, v) for r in row_list) if w), "")
        elif v.kind == "사용자 판단":
            why = next((w for w in (_user_judgment(corpus, r) for r in row_list) if w), "")
        elif v.kind == "병합":
            if re.fullmatch(r"M\d+", v.merge_to):
                if kinds.get(v.merge_to) != "채택":
                    why = f"병합 대상 {v.merge_to} 이 채택 항목이 아니다"
            elif v.merge_to not in plan.keys:
                why = f"병합 대상 키 `{v.merge_to}` 가 범위 안 키가 아니다"
            elif not all(v.merge_to in r.same_key for r in row_list):
                why = f"리뷰어가 같은 검사기 키 `{v.merge_to}` 를 적지 않은 행의 M→검사기 병합"
        elif v.kind == "별도 요청":
            fail = next((w for w in (_separate(corpus, project, plan, r, v) for r in row_list) if w), "")
            if fail:
                reclass.append((v.mid, f"별도 요청 → 채택({fail})"))
                v.kind = "채택"
                kinds[v.mid] = "채택"
        if why:
            reds.append((v.mid, "판정", f"{v.kind} — {why}"))
    return reds, reclass


def _finalize_verdicts(verdicts: "list[Verdict]", reds: "list[tuple[str, str, str]]", passed: "set[str]",
                       reclass: "list[tuple[str, str]]") -> "list[Verdict]":
    used: "set[str]" = {v.mid for v in verdicts}
    next_n: int = max([int(m[1:]) for m in used] + [0]) + 1

    def fresh() -> str:
        nonlocal next_n
        while f"M{next_n}" in used:
            next_n += 1
        used.add(f"M{next_n}")
        return f"M{next_n}"

    red_ids: "set[str]" = {k for k, kind, _w in reds if kind == "판정"}
    out: "list[Verdict]" = []
    seen_m: "set[str]" = set()
    covered: "dict[str, str]" = {}
    for v in verdicts:
        keep: "list[str]" = []
        for o in v.origin:
            if o not in passed:
                reclass.append((v.mid, f"원 행 {o} 는 check 통과 행이 아니라 판정에서 뺀다"))
            elif o in covered:
                reclass.append((v.mid, f"원 행 {o} 는 {covered[o]} 판정으로 둔다"))
            else:
                keep.append(o)
                covered[o] = v.mid
        if not keep:
            reclass.append((v.mid, "원 행이 없는 판정 — 기록에서 뺀다"))
            continue
        v.origin = keep
        if v.mid in seen_m:
            old: str = v.mid
            v.mid = fresh()
            reclass.append((old, f"M 번호 중복 → {v.mid}"))
        seen_m.add(v.mid)
        if (v.mid in red_ids or v.kind not in VERDICTS) and v.kind != "채택":
            reclass.append((v.mid, f"{v.label} → 채택(재호출 뒤에도 red — 채택으로 기록)"))
            v.kind, v.merge_to = "채택", ""
        out.append(v)
    for o in sorted(passed - set(covered)):
        mid: str = fresh()
        out.append(Verdict([mid, o, "채택", "", ""]))
        reclass.append((mid, f"판정 없는 통과 행 {o} → 채택(새 번호)"))
    adopted_m: "set[str]" = {v.mid for v in out if v.kind == "채택"}
    for v in out:                                   # 대상이 기록에서 빠진 병합 → 채택(고아 병합 금지)
        if v.kind == "병합" and re.fullmatch(r"M\d+", v.merge_to) and v.merge_to not in adopted_m:
            reclass.append((v.mid, f"병합 대상 {v.merge_to} 이 확정 기록의 채택 항목이 아니다 → 채택"))
            v.kind, v.merge_to = "채택", ""
    return out


def _g0_lists(corpus: Corpus, audit: Path, verdicts: "list[Verdict]", by_id: "dict[str, Row]",
              rows: "list[Row]") -> None:
    """G0 표시 목록 — 제외 행은 «위반 인용 ↔ 제외 인용» 나란히."""
    out: "list[str]" = [f"# G0 목록 — {_now()}", ""]
    for label in ("사용자 판단", "별도 요청", "제외", "오탐", "병합→검사기", "병합→M"):
        picked = [v for v in verdicts if v.label == label]
        out += [f"## {label} {len(picked)}", ""]
        for v in picked:
            for o in v.origin:
                r = by_id.get(o)
                if r is None:
                    continue
                if label == "제외":
                    out.append(f"- {v.mid} `{o}` {r.where} — 위반 {r.rule} ↔ 제외 {v.ground}")
                else:
                    out.append(f"- {v.mid} `{o}` {r.where} — {r.gist} · 근거 {v.ground or v.merge_to or '—'}")
        out.append("")
    out += ["## 인용 불일치", ""] + [f"- `{r.rid}` {r.reason}" for r in rows if r.status == "인용 불일치"] + [""]
    out += ["## 규칙 근거 없는 불편", ""] + [f"- `{r.rid}` {r.gist}" for r in rows if r.status == "불편"] + [""]
    (audit / "g0-lists.md").write_text("\n".join(out), encoding="utf-8")


def cmd_check_verdict(corpus: Corpus, project: Path, audit: Path, feedback: "Path | None", final: bool) -> int:
    plan: Plan = Plan(audit)
    rows: "list[Row]" = _load_rows(audit, plan)
    _check_rows(corpus, project, plan, rows)
    by_id: "dict[str, Row]" = {r.rid: r for r in rows}
    passed: "set[str]" = {r.rid for r in rows if r.status == "통과"}
    verdicts: "list[Verdict]" = _load_verdicts(audit)
    reds, reclass = _judge(corpus, project, plan, verdicts, by_id, passed)
    kinds: "dict[str, str]" = {v.mid: v.kind for v in verdicts}
    prev_kinds, prev_origin = _previous(audit / "verdict-log.md")
    covered: "dict[str, str]" = {o: v.mid for v in verdicts for o in v.origin}
    for o, m in covered.items():
        if o in prev_origin and prev_origin[o] != m:
            reds.append((m, "판정", f"R3 재실행이 원 행 {o} 의 번호를 {prev_origin[o]} → {m} 로 바꿨다(기존 M 번호 유지)"))
    source: str = _source(feedback)
    proxy: bool = _proxy_source(source) if source else bool(prev_kinds)
    if proxy:
        for m, before in prev_kinds.items():
            if before == "채택" and kinds.get(m) not in (None, "채택"):
                reds.append((m, "판정", f"대리 출처{'' if source else '(출처 없는 재실행)'}의 채택 축소(채택 → {kinds[m]}) — "
                                       "대리 출처는 채택 수를 줄일 수 없다"))
    if final and reds:
        verdicts = _finalize_verdicts(verdicts, reds, passed, reclass)
        reds = []
    counts: "dict[str, int]" = {k: 0 for k in ("채택", "사용자 판단", "별도 요청", "제외", "오탐", "병합→검사기", "병합→M")}
    for v in verdicts:
        if v.label in counts:
            counts[v.label] += 1
    q: int = sum(1 for r in rows if r.status == "인용 불일치")
    f: int = sum(1 for r in rows if r.status == "불편")
    code: int = EXIT_RED if reds else EXIT_OK
    summary: str = (f"요약: 채택 {counts['채택']} · 사용자 판단 {counts['사용자 판단']} · 별도 요청 {counts['별도 요청']} · "
                    f"제외 {counts['제외']} · 오탐 {counts['오탐']} · 병합→검사기 {counts['병합→검사기']} · "
                    f"병합→M {counts['병합→M']} · 인용 불일치 {q} · 규칙 근거 없는 불편 {f} · red {len(reds)}")
    log: "list[str]" = [f"## check-verdict {_now()} · 출처 {source or '없음'} · {'final · ' if final else ''}exit {code}",
                        "", "| M | 원 행 | 판정 |", "|---|---|---|"]
    log += [f"| {v.mid} | {' · '.join(v.origin)} | {v.label if v.kind != '병합' else '병합 → ' + v.merge_to} |"
            for v in verdicts]
    log.append("")
    log += [f"- 재분류: {m} {w}" for m, w in reclass]
    log += [f"- red: {m} {w}" for m, _k, w in reds]
    log += [summary, ""]
    with (audit / "verdict-log.md").open("a", encoding="utf-8") as fh:
        fh.write("\n".join(log) + "\n")
    if code == EXIT_OK:
        _write_final(audit, verdicts, final)
        _g0_lists(corpus, audit, verdicts, by_id, rows)
    for m, _k, w in reds:
        print(f"  red: {m} {w}")
    for m, w in reclass:
        print(f"  재분류: {m} {w}")
    print(summary)
    return code


# ── residual ─────────────────────────────────────────────────────────────────

def _changed_since(project: Path, anchor: str) -> "set[str]":
    changed: "set[str]" = {p for p in _git(project, "diff", "--no-renames", "--name-only", anchor).splitlines() if p}
    return changed | {p for p in _git(project, "ls-files", "--others", "--exclude-standard").splitlines() if p}


def _renamed_since(project: Path, anchor: str) -> "dict[str, str]":
    out: "dict[str, str]" = {}
    for ln in _git(project, "diff", "-M", "--name-status", anchor).splitlines():
        parts: "list[str]" = ln.split("\t")
        if parts and parts[0].startswith("R") and len(parts) == 3:
            out[parts[1]] = parts[2]
    return out


def _file_sha(project: Path, rel: str) -> "str | None":
    path: Path = project / rel
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16] if path.is_file() else None


def _stamp_dir(folder: Path, finalize: "str | None") -> "tuple[str, Path]":
    base: Path = folder / "residual"
    if finalize is not None:
        if not (base / finalize).is_dir():
            raise ToolError(f"residual 시각 {finalize} 폴더가 없다 — 먼저 --finalize 없이 돈다")
        return finalize, base / finalize
    stamp: str = datetime.now().strftime("%Y%m%d-%H%M")
    k: int = 1
    while (base / (stamp if k == 1 else f"{stamp}-{k}")).exists():
        k += 1
    stamp = stamp if k == 1 else f"{stamp}-{k}"
    return stamp, base / stamp


def _stamp_key(name: str) -> "tuple[int, ...]":
    parts: "list[str]" = name.split("-")
    return tuple(int(x) if x.isdigit() else -1 for x in parts) + ((1,) if len(parts) == 2 else ())


def _carried(folder: Path, stamp: str, audit_ts: str, anchor: str) -> "tuple[str, dict[str, dict[str, str | None]]]":
    """직전 확정의 해소 — 같은 `의미 audit`·같은 `git_snapshot` 판만 잇는다(재사용 폴더의 새 점검은 M 번호가 다시
    매겨지므로 앞 실행의 해소를 이어받지 않는다)."""
    base: Path = folder / "residual"
    done: "list[str]" = sorted((d.name for d in base.iterdir() if d.is_dir() and _stamp_key(d.name) < _stamp_key(stamp)
                                and (d / "result.json").is_file()), key=_stamp_key) if base.is_dir() else []
    for name in reversed(done):
        data: dict = json.loads((base / name / "result.json").read_text(encoding="utf-8"))
        if data.get("audit") == audit_ts and data.get("snapshot") == anchor:
            return name, data.get("solved", {})
    return "", {}


def cmd_residual(project: Path, folder: Path, finalize: "str | None") -> int:
    debt: dict = _load_debt(folder / "debt-g0.json")
    if debt.get("mode") != "refactor":
        raise ToolError("debt-g0.json mode 가 refactor 가 아니다 — 리팩토링 실행의 폴더가 아니다")
    try:
        _when, audit_ts, adopted, removed = residual_m_sets(_read(folder / "refactor-scope.md"))
    except DebtError as exc:
        raise ToolError(str(exc)) from None
    items: "set[str]" = adopted - removed
    audit: Path = folder / "audit" / audit_ts
    if not (audit / VERDICT_FINAL).is_file():
        raise ToolError(f"의미 audit {audit_ts} 의 {VERDICT_FINAL} 이 없다(check-verdict exit 0 판 없음) — {audit}")
    verdicts: "dict[str, Verdict]" = {v.mid: v for v in _load_verdicts(audit, VERDICT_FINAL)}
    plan: Plan = Plan(audit)
    rows: "dict[str, Row]" = {r.rid: r for r in _load_rows(audit, plan)}
    state: dict = json.loads(_read(folder / "build-state.json"))
    anchor: str = str(state.get("git_snapshot") or "").strip()
    if not anchor:
        raise ToolError("build-state.json 에 git_snapshot 이 없다")
    changed: "set[str]" = _changed_since(project, anchor)
    mapping: "dict[str, str]" = _renamed_since(project, anchor)
    stamp, out_dir = _stamp_dir(folder, finalize)
    prev_stamp, prev_solved = _carried(folder, stamp, audit_ts, anchor)
    floor: "dict[str, str]" = {}
    carried: "list[str]" = []
    to_review: "dict[str, list[str]]" = {}
    origins: "dict[str, list[tuple[str, str]]]" = {}
    watched: "dict[str, list[str]]" = {}
    for mid in sorted(items, key=lambda k: int(k[1:])):
        v = verdicts.get(mid)
        if v is None:
            raise ToolError(f"ⓐ 항목 {mid} 이 {VERDICT_FINAL} 에 없다")
        merged = [x for x in verdicts.values() if x.kind == "병합" and x.merge_to == mid]
        origins[mid] = [(o, "") for o in v.origin] + [(o, x.mid) for x in merged for o in x.origin]
        origin: "list[str]" = [o for o, _m in origins[mid]]
        files: "list[str]" = sorted({_repo_path(project, l[0]) for o in origin if o in rows
                                     for l in (_parse_location(t) for t in _locations(rows[o].where)) if l})
        watched[mid] = sorted(set(files) | {mapping.get(f, f) for f in files})
        before: "dict[str, str | None] | None" = prev_solved.get(mid)
        if before is not None and before == {p: _file_sha(project, p) for p in before}:
            carried.append(mid)
            continue
        if files and not any(f in changed for f in files):
            floor[mid] = "파일 무변(git_snapshot..작업 트리)"
            continue
        for o in origin:
            if o in rows:
                to_review.setdefault(rows[o].lens, []).append(mid)
    out_dir.mkdir(parents=True, exist_ok=True)
    lines: "list[str]" = [f"# residual 결정적 바닥 — {stamp}", "", "| M | 판정 | 사유 |", "|---|---|---|"]
    lines += [f"| {m} | 잔존 | {w} |" for m, w in floor.items()]
    lines += [f"| {m} | 해소 유지 | 직전 확정 {prev_stamp} 뒤 항목 파일·대응 경로 무변 |" for m in carried]
    (out_dir / "bottom.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    pending_ids: "list[str]" = sorted({m for ms in to_review.values() for m in ms}, key=lambda k: int(k[1:]))
    if finalize is None:
        for lens, mids in to_review.items():
            body: "list[str]" = [f"# 잔존 확인 — {lens} · {stamp}", "",
                                 "결과 표(`result-<렌즈>.md`): `M<n> | 해소|잔존|판단 불가 | 근거`", "",
                                 "해소의 근거 칸 판형: `<새 파일:행[-행]>[ · <새 파일:행[-행]>…] — <무엇이 어떻게 사라졌는지 한 구>`. "
                                 "` — ` 앞에는 저장소 루트 기준 새 위치만 적는다(조사·괄호·설명 없이 — 이 위치만 근거로 센다). "
                                 "위치마다 경로:행을 전부 적는다(`:16`·`15·16` 줄임 없이) · 구분은 ` · `. 남은 것·제외 범주·설계 근거 같은 "
                                 "맥락 위치는 ` — ` 뒤에만 적는다. 판형이 아니면 그 행을 다시 요청받는다.",
                                 "예: `M3 | 해소 | web/application/<bc>/application_layer/view_model/<화면>_vm.py:15-16 — "
                                 "탭 키 철자를 정의부 한 곳에만 둔다`",
                                 "", "## 항목", ""]
            for mid in sorted(set(mids), key=lambda k: int(k[1:])):
                body.append(f"### {mid}")
                for o, via in origins[mid]:
                    if o in rows:
                        body.append(f"- 원 행 {o}{f' (병합 {via})' if via else ''}: {' | '.join(rows[o].cells)}")
                body.append("")
            body += ["## 슬라이스 0 개명 쌍(옛 경로 → 새 경로)", ""]
            body += [f"- {a} → {b}" for a, b in sorted(mapping.items())] or ["- 없음"]
            (out_dir / f"review-{lens}.md").write_text("\n".join(body) + "\n", encoding="utf-8")
        tail: str = f" · 해소 유지 {len(carried)}" if carried else ""
        if pending_ids:
            print(f"요약: residual 결정적 잔존 {len(floor)}{tail} · 리뷰어 확인 대상 {len(pending_ids)}"
                  f"({'·'.join(sorted(to_review))}) · M_m 미정 — --finalize {stamp} → {out_dir}")
            return EXIT_OK
        print(f"요약: residual M_m={len(floor)}(결정적 잔존 {len(floor)}){tail} · 리뷰어 확인 대상 0 → {out_dir}")
        (out_dir / "result.json").write_text(json.dumps(
            {"stamp": stamp, "audit": audit_ts, "snapshot": anchor, "solved": {m: prev_solved[m] for m in carried}},
            ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
        return EXIT_RED if floor else EXIT_OK
    results: "dict[str, list[tuple[str, str, str]]]" = {}     # M → (렌즈, 판정 칸, 근거 칸)
    for lens in to_review:
        path: Path = out_dir / f"result-{lens}.md"
        for cells in _table_rows(path.read_text(encoding="utf-8")) if path.is_file() else []:
            if len(cells) >= 2 and re.fullmatch(r"M\d+", cells[0]):
                results.setdefault(cells[0], []).append((lens, cells[1], cells[2] if len(cells) > 2 else ""))
    # 같은 시각 재확정 — 동결은 좋아지는 쪽만 막는다. 앞 판이 판형 아님·답 없음이면 다시 판정하고, 그 밖에는 이번 행이
    # 있으면 이번 판정을 쓰되 앞 판이 잔존·잔존(반복)·판단 불가면 해소·판형 아님·답 없음(다시 판정 쪽)으로 가지 않는다
    # (앞 판 해소의 강등은 모두 받는다 · 행이 없으면 앞 판 판정·지문 유지).
    # 판형 아님 이력(`redo`)은 판정과 따로 쌓는다 — 이력 있는 M 이 다시 판형 아님이면 잔존(반복)이다.
    before_states, redo_before, kept = _same_stamp(out_dir / "result.json")
    code_changed: "set[str]" = {p for p in changed if not p.startswith(OUTPUT_ROOTS)}   # 산출물 파일은 해소 근거가 아니다
    states: "dict[str, str]" = {}
    unformatted: "dict[str, list[tuple[str, str]]]" = {}     # M → [(렌즈, 불량 토큰)]
    grounds: "dict[str, set[str]]" = {}                      # M → 해소로 받은 근거 경로(확정 지문에 원 발견 경로와 함께 든다)
    for mid in pending_ids:
        was: str = before_states.get(mid, "")
        answers = results.get(mid, [])
        if was and was not in ("판형 아님", "답 없음") and not answers:
            states[mid] = was                               # 행 없음 — 앞 판 판정·지문 유지
            continue
        allowed: "set[str]" = code_changed | set(watched[mid])
        answered: "set[str]" = {lens for lens, _c, _g in answers}
        got: "list[str]" = ["답 없음" for lens, ms in to_review.items() if mid in ms and lens not in answered]
        for lens, cell, ground in answers:
            st: str = _answer_state(cell)
            if st == "해소":
                heads, bad = _ground(ground)
                locs = [(_repo_path(project, l[0]), l[1], l[2]) for l in heads]
                bad = bad or next((f"{h[0]}:{h[1]}" + (f"-{h[2]}" if h[2] != h[1] else "")
                                   for h, l in zip(heads, locs) if not _location_ok(project, l)), "")
                if bad:
                    got.append("판형 아님")
                    unformatted.setdefault(mid, []).append((lens, bad))
                elif all(l[0] in allowed for l in locs):
                    got.append("해소")
                    grounds.setdefault(mid, set()).update(l[0] for l in locs)
                else:
                    got.append("잔존")
            else:
                got.append(st)
        verdict: str = ("해소" if got and all(g == "해소" for g in got) else "잔존" if "잔존" in got
                        else "판형 아님" if "판형 아님" in got else "답 없음" if "답 없음" in got else "판단 불가")
        now: str = "잔존(반복)" if verdict == "판형 아님" and mid in redo_before else verdict
        held: bool = was in ("잔존", "잔존(반복)", "판단 불가") and now not in ("잔존", "잔존(반복)", "판단 불가")
        states[mid] = was if held else now
    redo: "list[str]" = sorted(set(redo_before) | {m for m, s in states.items() if s == "판형 아님"},
                               key=lambda k: int(k[1:]))
    solved: "list[str]" = [m for m in pending_ids if states[m] == "해소"]
    reviewer_left: "list[str]" = [m for m in pending_ids if states[m] in ("잔존", "잔존(반복)")]
    unformed: "list[str]" = [m for m in pending_ids if states[m] == "판형 아님"]
    unknown: "list[str]" = [m for m in pending_ids if states[m] in ("판단 불가", "답 없음")]
    m_m: int = len(floor) + len(reviewer_left) + len(unformed) + len(unknown)
    lines = [f"# residual 결과 — {stamp}", "", "| M | 판정 |", "|---|---|"]
    lines += [f"| {m} | 잔존(결정적) |" for m in floor]
    lines += [f"| {m} | {'잔존(근거 판형 아님 반복)' if states[m] == '잔존(반복)' else '잔존(리뷰어 · 근거 없는 해소 포함)'} |"
              for m in reviewer_left]
    lines += [f"| {m} | 근거 판형 아님({'·'.join(sorted({lens for lens, _t in unformatted[m]}))}) |" for m in unformed]
    lines += [f"| {m} | 판단 불가 |" for m in unknown] + [f"| {m} | 해소 |" for m in solved]
    lines += [f"| {m} | 해소(직전 {prev_stamp} 이월) |" for m in carried]
    (out_dir / "result.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    # 해소 지문 = 원 발견 경로(+ 개명 대응) ∪ 해소로 받은 근거 경로 — 근거 파일만 뒤에 바뀌어도 이월하지 않고 다시 묻는다.
    # 같은 시각 재확정에서 앞 판 해소를 유지하면 앞 판 지문을 그대로 두고, 이번에 새로 받은 근거 경로만 지금 지문으로 더한다.
    snapshot: "dict[str, dict[str, str | None]]" = {}
    for m in solved:
        held_fp: "dict[str, str | None]" = dict(kept[m]) if m in kept and before_states.get(m) == "해소" else {}
        paths: "set[str]" = (set() if held_fp else set(watched[m])) | grounds.get(m, set())
        snapshot[m] = {**{p: _file_sha(project, p) for p in sorted(paths - set(held_fp))}, **held_fp}
    snapshot.update({m: prev_solved[m] for m in carried})
    (out_dir / "result.json").write_text(json.dumps({"stamp": stamp, "audit": audit_ts, "snapshot": anchor,
                                                     "solved": snapshot, "states": states, "redo": redo},
                                                    ensure_ascii=False,
                                                    sort_keys=True) + "\n", encoding="utf-8")
    print(f"요약: residual M_m={m_m}(결정적 잔존 {len(floor)} · 리뷰어 잔존 {len(reviewer_left)} · 근거 판형 아님 "
          f"{len(unformed)} · 판단 불가 {len(unknown)}) · 해소 {len(solved) + len(carried)}"
          f"{f'(이월 {len(carried)})' if carried else ''} → {out_dir / 'result.md'}")
    if unformed:                                            # `요약:` 뒤 — 재기재 안내(슬라이스 0 재개봉·새 시각이 아니다)
        notes_redo: str = " · ".join(m + "(" + ", ".join(f"{lens}: `{tok}`" for lens, tok in unformatted[m]) + ")"
                                      for m in unformed)
        print(f"  근거 판형 아님: {notes_redo} — 그 행만 같은 렌즈 리뷰어에게 묶음 머리의 판형대로 다시 받아 result-<렌즈>.md 에 "
              f"고쳐 쓰고 --finalize {stamp} 한 번 더(코드 재개봉·새 시각 아님 · 다시 판형 아님이면 잔존)")
    return EXIT_RED if m_m else EXIT_OK


# ── 상시 답(standing) ─────────────────────────────────────────────────────────

# ── 상시 답 인식 블록 시작(core·web byte 동일 — verify-web 이 대조한다 · 모듈의 다른 함수를 부르지 않는다) ──
# Coordinator 리팩토링 모드 절 «상시 답» 문단 — 덮는 범주·문장·경로는 `--self-test` 가 문면과 대조한다.
STANDING_FILE: str = ".dddjango/standing-answer.md"
STANDING_SENTENCE: str = "동작 변경이나 테스트 수정이 필요해 이번에 못 끝내는 항목은 별도 요청으로"
STANDING_CATEGORIES: "tuple[str, ...]" = ("외부 관찰 동작", "테스트 본문 동반", "테스트 새 판정")
STANDING_MARK: str = "상시 답이 덮는 범주"
STANDING_SECTION: str = "상시 답 적용"
STANDING_EXPECT: str = f"기대 문장: {STANDING_SENTENCE}"


def _standing_rows(text: str) -> "list[int]":
    """상시 답 인식 줄의 행 번호(1 기준) — 문장만 본다(공백·강조·백틱·인용·목록 머리·감싼 따옴표/괄호·끝 문장부호 무시)."""
    want: str = re.sub(r"[\s*`]", "", STANDING_SENTENCE)
    rows: "list[int]" = []
    for no, line in enumerate(text.split("\n"), 1):
        s: str = re.sub(r"^\s*(?:>\s*)*(?:(?:[-*+]|\d+[.)])\s+)?", "", line).strip()
        prev: "str | None" = None
        while s != prev:
            prev = s
            s = s.rstrip(".。!").strip()
            for a, b in ("«»", "‹›", '""', "''", "“”", "‘’", "「」", "()"):
                if len(s) >= 2 and s[0] == a and s[-1] == b:
                    s = s[1:-1].strip()
        if s and re.sub(r"[\s*`]", "", s) == want:
            rows.append(no)
    return rows


def _standing_verdict(text: str) -> "tuple[int | None, str]":
    """(인식 행, 인식 안 함 사유) — 인식 줄은 정확히 하나여야 한다(없거나 둘 이상이면 인식 안 함)."""
    rows: "list[int]" = _standing_rows(text)
    if len(rows) == 1:
        return rows[0], ""
    return None, ("문장 없음" if not rows else f"인식 줄 {len(rows)}개")
# ── 상시 답 인식 블록 끝 ──


_STANDING_SRC: "re.Pattern[str]" = re.compile(r"출처\s*=\s*상시 답\s+(\S+?):(\d+)@([0-9a-f]{12})(?![0-9a-f])")
_USER_SRC: "re.Pattern[str]" = re.compile(r"출처\s*=\s*(?:본인 직접|사용자 원문)")
_SCOPE_HEAD: "re.Pattern[str]" = re.compile(r"^## (G0 재승인|G0 정지|G0|ⓐ 재상정) \S")
_SCOPE_KEY_ROW: "re.Pattern[str]" = re.compile(r"^(?:- )?(의미 재상정 키|재상정 키):[ \t]*(.*?)\s*$")
_FIELD: "re.Pattern[str]" = re.compile(r"·\s*(결정|사유|출처)\s*=\s*")
_STANDING_MARK_LINE: "re.Pattern[str]" = re.compile(rf"^-?\s*{STANDING_SECTION}\s*\d+\s*건\s*$")
_STANDING_REASON: "re.Pattern[str]" = re.compile(r"^동작 불변 불가\((.*)\)$")
_ASK: str = " — 묻는다(재상정 STOP)"
_FIX: str = " — 고친 줄을 새 `ⓐ 재상정` 절에 적는다"


def _git_try(project: Path, *args: str) -> "tuple[int, str]":
    p = subprocess.run(["git", "-C", str(project), *args], capture_output=True, text=True)
    return p.returncode, p.stdout


def _standing(project: Path) -> "dict[str, str] | None":
    """상시 답 파일 — 없으면 None · 인식이면 {row, commit, when} · 아니면 {why}(실행 불능으로 가지 않는다)."""
    path: Path = project / STANDING_FILE
    if not path.is_file():
        return None
    if _git_try(project, "ls-files", "--error-unmatch", STANDING_FILE)[0] != 0:
        return {"why": "미추적"}
    if _git_try(project, "diff", "--quiet", "HEAD", "--", STANDING_FILE)[0] != 0:
        return {"why": "커밋되지 않은 수정"}
    row, why = _standing_verdict(path.read_text(encoding="utf-8", errors="replace"))
    if row is None:
        return {"why": why}
    code, out = _git_try(project, "log", "-1", "--format=%H %cI", "--", STANDING_FILE)
    if code != 0 or len(out.split()) < 2:
        return {"why": "커밋 없음"}
    commit, when = out.split()[:2]
    return {"row": str(row), "commit": commit[:12], "when": when}


def _standing_source_ok(project: Path, path: str, row: int, commit: str) -> str:
    """상시 답 출처 값의 커밋·행 — 사유(비면 통과). 적용 뒤 파일이 바뀌어도 그 커밋 판으로 본다."""
    if path != STANDING_FILE:
        return f"경로 `{path}` 가 `{STANDING_FILE}` 가 아니다"
    code, full = _git_try(project, "rev-parse", "--verify", "--quiet", f"{commit}^{{commit}}")
    if code != 0:
        return f"커밋 {commit} 이 없다"
    if _git_try(project, "merge-base", "--is-ancestor", full.strip(), "HEAD")[0] != 0:
        return f"커밋 {commit} 이 HEAD 의 조상이 아니다"
    code, body = _git_try(project, "show", f"{full.strip()}:{STANDING_FILE}")
    if code != 0:
        return f"커밋 {commit} 판에 파일이 없다"
    if _standing_verdict(body)[0] != row:
        return f"커밋 {commit} 판의 {row}행이 유일한 인식 줄이 아니다"
    return ""


def _scope_decisions(text: str) -> "tuple[list[dict], list[dict]]":
    """`refactor-scope.md` 의 마지막 `## G0` 절부터 — (절 [{kind, mark, rows}], 결정 줄 [{no, sec, keys, fields, …}]).
    결정 줄 = `· 결정 =` 칸이 있는 줄. 칸 값은 다음 칸 이름(`· 사유 =`·`· 출처 =`) 앞까지다. 머리 `결정 줄:` 은 떼고,
    병합 괄호 `(+M<k>)` 안은 키가 아니다."""
    sections: "list[dict]" = []
    decisions: "list[dict]" = []
    fenced: bool = False
    for no, line in enumerate(text.split("\n"), 1):
        if re.match(r"^\s*(```|~~~)", line):
            fenced = not fenced
            continue
        if fenced:
            continue
        if line.startswith("## "):
            head = _SCOPE_HEAD.match(line)
            sections.append({"kind": head.group(1) if head else "", "body": [], "rows": {}})
            continue
        if not sections:
            continue
        sec: dict = sections[-1]
        sec["body"].append(line)
        row = _SCOPE_KEY_ROW.match(line)
        if row:
            sec["rows"].setdefault(row.group(1), []).append(row.group(2))
        cells = list(_FIELD.finditer(line))
        standing: bool = bool(re.search(r"출처\s*=\s*상시 답", line))
        if not standing and (not cells or cells[0].group(1) != "결정"):    # 상시 답 줄은 모양이 틀려도 검사 대상
            continue
        fields: "dict[str, str]" = {}
        for k, m in enumerate(cells):
            fields.setdefault(m.group(1), line[m.end():cells[k + 1].start() if k + 1 < len(cells) else len(line)].strip())
        head_text: str = re.sub(r"^\s*(?:-\s*)?(?:결정 줄\s*:\s*)?", "", line[:cells[0].start()] if cells else line)
        keys: "list[str]" = re.findall(r"(?<![A-Za-z0-9])([MC][1-9]\d*)(?!\d)", re.sub(r"\(\+[^)]*\)", "", head_text))
        decisions.append({"no": no, "sec": len(sections) - 1, "keys": keys, "fields": fields, "standing": standing,
                          "user": bool(_USER_SRC.search(line)), "text": line})
    for sec in sections:
        first: str = next((l for l in sec["body"] if l.strip()), "")
        sec["mark"] = bool(_STANDING_MARK_LINE.match(first.strip()))
    start: int = max((i for i, s in enumerate(sections) if s["kind"] == "G0"), default=0)
    return sections[start:], [dict(d, sec=d["sec"] - start) for d in decisions if d["sec"] >= start]


def _snapshot_lines(project: Path, snap: str, rel: str, memo: "dict[str, int | None]") -> "int | None":
    """`git_snapshot` 판의 줄 수(`web/` 없이 쓴 web 경로도 받는다) — 없으면 None."""
    if rel not in memo:
        memo[rel] = None
        for cand in (rel, "web/" + rel) if not rel.startswith("web/") else (rel,):
            try:
                code, out = _git_try(project, "cat-file", "blob", f"{snap}:{cand}")     # 디렉터리(트리)는 실패
            except UnicodeDecodeError:
                code, out = 0, ""                                                       # 비UTF-8 은 0행(`_lines_of` 와 같다)
            if code == 0:
                memo[rel] = len(out.splitlines())
                break
    return memo[rel]


def _standing_gate(project: Path, folder: Path) -> "tuple[list[str], int, int]":
    """`standing --gate` — 상시 답 줄의 ① 출처 커밋·행 ② 처분 ③ 항목·범주·위치 ④ 자리 ⑤ 키 행 결속 · 대체."""
    text: str = _read(folder / "refactor-scope.md")
    try:
        _when, _audit, adopted, _gone = residual_m_sets(text)
    except DebtError as exc:
        raise ToolError(str(exc)) from None
    sections, decisions = _scope_decisions(text)
    standing: "list[dict]" = [d for d in decisions if d["standing"]]
    reds: "list[str]" = []
    snap: str = ""
    memo: "dict[str, int | None]" = {}
    replaced: int = 0
    for d in standing:
        tag: str = f"{' · '.join(d['keys']) or '(키 없음)'} 상시 답 줄({d['no']}행)"
        live: "set[str]" = {k for k in d["keys"] if not any(         # 뒤 재상정 절 줄(사용자 답·고친 상시 답)이 대체한 키
            o["sec"] > d["sec"] and sections[o["sec"]]["kind"] == "ⓐ 재상정" and (o["user"] or o["standing"])
            and k in o["keys"] for o in decisions)}
        if d["keys"] and not live:
            replaced += 1
            continue
        sec: dict = sections[d["sec"]]
        if sec["kind"] != "ⓐ 재상정" or not sec["mark"]:
            reds.append(f"{tag} ④ 첫 줄 `- {STANDING_SECTION} k건` 이 있는 `ⓐ 재상정` 절 밖이다{_FIX}")
        sm = _STANDING_SRC.search(d["text"])
        why: str = (_standing_source_ok(project, sm.group(1), int(sm.group(2)), sm.group(3)) if sm
                    else "출처 값이 `상시 답 <파일>:<행>@<커밋 12자>` 정형이 아니다")
        if why:
            reds.append(f"{tag} ① {why}{_FIX}")
        if d["fields"].get("결정") != "별도 요청":
            reds.append(f"{tag} ② 처분이 «별도 요청»이 아니다{_FIX}")
        mkeys: "list[str]" = [k for k in d["keys"] if k.startswith("M")]
        if any(k.startswith("C") for k in d["keys"]):
            reds.append(f"{tag} ③ `C<n>` 에는 상시 답을 쓰지 않는다{_ASK}")
        elif len(mkeys) != 1:
            reds.append(f"{tag} ③ 키가 `M<n>` 하나가 아니다(항목마다 한 줄){_FIX}")
        for mid in (k for k in mkeys if k in live):
            if mid not in adopted:
                reds.append(f"{tag} ③ {mid} 이 마지막 `## G0` 의 의미 ⓐ 항목이 아니다{_FIX}")
            if any(o["user"] and o["sec"] < d["sec"] and sections[o["sec"]]["kind"] == "ⓐ 재상정" and mid in o["keys"]
                   for o in decisions):
                reds.append(f"{tag} ④ {mid} 의 앞선 재상정 사용자 답 줄보다 뒤다 — 사용자 답이 이긴다(그 답을 새 절에 다시 적는다){_FIX}")
        rm = _STANDING_REASON.match(d["fields"].get("사유", ""))
        cats_part, sep, locs_part = rm.group(1).partition(" — ") if rm else ("", "", "")
        if not sep:
            reds.append(f"{tag} ③ 사유가 `동작 불변 불가(<범주>[ · <범주>] — <파일:행>[ · <파일:행>])` 정형이 아니다{_FIX}")
            continue
        cats: "list[str]" = [c.strip().strip("`").strip() for c in re.split(r"[·,]", cats_part) if c.strip()]
        if not cats or not set(cats) <= set(STANDING_CATEGORIES):
            reds.append(f"{tag} ③ 범주 {cats} 가 {' · '.join(STANDING_CATEGORIES)} 셋 안이 아니다{_ASK}")
        locs: "list[str]" = [t.strip() for t in re.split(r"\s*·\s*", locs_part) if t.strip()]
        if not locs:
            reds.append(f"{tag} ③ 막는 `파일:행` 이 없다{_FIX}")
        for tok in locs:
            loc = _parse_location(tok)
            if not loc or loc[0].startswith("/") or not 1 <= loc[1] <= loc[2]:
                reds.append(f"{tag} ③ 위치 `{tok}` 가 `파일:행[-행]`(저장소 상대 · 1 ≤ 시작 ≤ 끝) 정형이 아니다"
                            f"(맨 `:행`·행만 적은 것은 받지 않는다){_FIX}")
                continue
            if not snap:
                state: dict = json.loads(_read(folder / "build-state.json"))
                snap = str(state.get("git_snapshot") or "").strip()
                if not snap:
                    raise ToolError("build-state.json 에 git_snapshot 이 없다 — `standing --gate` 는 Phase 2 진입 준비의 "
                                    "`git_snapshot` 기록 뒤에 돈다")
            n = _snapshot_lines(project, snap, loc[0], memo)
            if n is None or loc[2] > n:
                reds.append(f"{tag} ③ 위치 `{tok}` 가 git_snapshot 판({snap[:12]})의 파일·줄 범위에 없다{_FIX}")
    for i, sec in enumerate(sections):
        if sec["kind"] != "ⓐ 재상정" or not sec["mark"]:
            continue
        mine: "list[dict]" = [d for d in decisions if d["sec"] == i]
        for d in mine:
            if not d["standing"]:
                reds.append(f"{' · '.join(d['keys']) or '(키 없음)'} 결정 줄({d['no']}행) ④ 상시 답 절에 상시 답 아닌 "
                            f"결정 줄이 있다 — 고친 줄을 새 `ⓐ 재상정` 절에 적는다")
        keys: "set[str]" = {k for d in mine if d["standing"] for k in d["keys"] if k.startswith("M")}
        rows: "list[str]" = sec["rows"].get("의미 재상정 키", [])
        listed: "set[str]" = set(rows[0].split()) - {"-"} if len(rows) == 1 else set()
        if len(rows) != 1 or listed != keys:
            reds.append(f"상시 답 절 ⑤ `의미 재상정 키:` {sorted(listed)} ≠ 상시 답 줄 키 {sorted(keys)} — "
                        f"고친 절을 새로 적는다")
        if sec["rows"].get("재상정 키", []) != ["-"]:
            reds.append("상시 답 절 ⑤ `재상정 키:` 가 `-` 한 행이 아니다 — 고친 절을 새로 적는다")
    return reds, len(standing), replaced


def cmd_standing(project: Path, folder: "Path | None", gate: bool) -> int:
    if gate:
        if folder is None:
            raise ToolError("standing --gate 는 <산출물 폴더> 를 받는다")
        reds, count, replaced = _standing_gate(project, folder)
        for r in reds:
            print(f"  red: {r}")
        print(f"요약: standing gate · 상시 답 줄 {count} · 대체 {replaced} · red {len(reds)}")
        return EXIT_RED if reds else EXIT_OK
    found: "dict[str, str] | None" = _standing(project)
    if found is None:
        print("  상시 답: 없음")
        print("요약: standing 없음 — 적용 0")
    elif "row" in found:
        print(f"  상시 답: 인식 — {STANDING_FILE}:{found['row']}(커밋 {found['commit']} · {found['when']})")
        print(f"  상시 답 출처: 상시 답 {STANDING_FILE}:{found['row']}@{found['commit']}")
        print("요약: standing 인식")
    else:
        print(f"  상시 답: 인식 안 함({found['why']}) — 적용 0")
        print(f"  {STANDING_EXPECT}")
        print("요약: standing 인식 안 함 — 적용 0")
    return EXIT_OK


# ── self-test ────────────────────────────────────────────────────────────────

def cmd_self_test(corpus: Corpus) -> int:
    reds: "list[str]" = []
    tokens: "list[str]" = [t for ts in LENS_SECTIONS.values() for t in ts]
    for t in tokens:
        key, _s, sec = t.partition(" §")
        if not corpus.path_of(key).is_file():
            reds.append(f"점검 절 문서 없음: {t} → {corpus.path_of(key)}")
        elif corpus.doc(key).section(sec) is None:
            reds.append(f"점검 절 없음: {t}")
    for key in (COORDINATOR, ARCHITECT):
        if not corpus.path_of(key).is_file():
            reds.append(f"경로 사상 실패: {key} → {corpus.path_of(key)}")
    for doc in sorted(CAN_DOCS):
        if not corpus.path_of(doc).is_file():
            reds.append(f"`할 수 있다` 적용 문서 없음: {doc}")
    phrases: "tuple[str, ...]" = ()
    try:
        phrases = corpus.scope_phrases()
        bare = [p for p in phrases if p.strip() in ("기존", "신규", "새", "레거시")]
        if bare:
            reds.append(f"적용 한정 어구에 맨 낱말 {bare} — 결합형으로만 싣는다")
    except (ToolError, OSError) as exc:
        reds.append(str(exc))
    if corpus.path_of(COORDINATOR).is_file():
        coord: str = _read(corpus.path_of(COORDINATOR))
        for mark, place in REF_COMMAND_PARAGRAPHS:       # 문면 어딘가가 아니라 명령이 적히는 자리마다 본다
            found: "list[str]" = [ln for ln in coord.splitlines() if mark in ln]
            if len(found) != 1:
                reds.append(f"Coordinator «{place}» 문단(표지 {mark})이 {len(found)}개다 — 하나여야 grep 명령을 대조한다")
                continue
            if _pathspec_text(REF_PATHSPEC) not in found[0]:
                reds.append(f"참조 완전성 pathspec 상수가 Coordinator «{place}» 문단의 grep 명령과 다르다: "
                            f"{_pathspec_text(REF_PATHSPEC)}")
            notice: str = _grep_command(DOC_COMMAND_NEEDLE, DOC_PATHSPEC)   # 알림은 조회 옵션까지 글자 그대로
            if notice not in found[0]:
                reds.append(f"문서 글 적중(알림) 명령이 Coordinator «{place}» 문단에 글자 그대로 없다"
                            f"(도구의 조회 옵션 · pathspec 과 같아야 한다): {notice}")
        if STANDING_MARK not in coord:
            reds.append(f"상시 답 범주 문면(«{STANDING_MARK}»)을 Coordinator 에서 찾지 못했다")
        else:
            listed: "list[str]" = re.findall(r"`([^`]+)`", coord.split(STANDING_MARK, 1)[1].split("셋뿐", 1)[0])
            if listed != list(STANDING_CATEGORIES):
                reds.append(f"상시 답 범주 상수 ≠ 규범 문면: 상수 {list(STANDING_CATEGORIES)} · 문면 {listed}")
        for const, name in ((STANDING_SENTENCE, "상시 답 문장"), (STANDING_FILE, "상시 답 파일")):
            if const not in coord:
                reds.append(f"{name} 상수 ≠ 규범 문면: «{const}» 가 Coordinator 에 없다")
    if corpus.path_of(ARCHITECT).is_file() and f"`{SPEC_SLICE0_HEAD}`" not in _read(corpus.path_of(ARCHITECT)):
        reds.append(f"architect 문면에 슬라이스 0 절 머리 `{SPEC_SLICE0_HEAD}` 가 없다")
    for sentence, want in POLARITY_SAMPLES:
        got: bool = bool(positive_hits(normalize_spaced(sentence), ""))
        if got != want:
            reds.append(f"극성 표본 어긋남({'유효' if want else '무효'} 기대): {sentence}")
    for r in reds:
        print(f"  red: {r}")
    print(f"요약: self-test {corpus.platform} · 점검 절 {len(tokens)} · 어구 {len(phrases)} · "
          f"극성 표본 {len(POLARITY_SAMPLES)} · red {len(reds)}")
    return EXIT_RED if reds else EXIT_OK


# ── main ─────────────────────────────────────────────────────────────────────

def main(argv: "list[str]") -> int:
    ap = argparse.ArgumentParser(prog="refactor_audit.py", description="dddjango-web 리팩토링 모드 결정적 도구")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--platform", choices=("claude", "codex"))
    ap.add_argument("--plugin-root")
    ap.add_argument("--project", default=".", help="대상 프로젝트 루트(기본 .)")
    sub = ap.add_subparsers(dest="command")
    p = sub.add_parser("plan")
    p.add_argument("unit")
    p.add_argument("--debt", required=True)
    p.add_argument("--out")
    p.add_argument("--against")
    p.add_argument("--names")
    for name in ("check",):
        sub.add_parser(name).add_argument("audit")
    p = sub.add_parser("check-verdict")
    p.add_argument("audit")
    p.add_argument("--feedback")
    p.add_argument("--final", action="store_true")
    p = sub.add_parser("residual")
    p.add_argument("folder")
    p.add_argument("--finalize")
    p = sub.add_parser("standing")
    p.add_argument("folder", nargs="?")
    p.add_argument("--gate", action="store_true")
    try:
        ns = ap.parse_args(argv)
    except SystemExit as exc:
        if exc.code == 0:
            return EXIT_OK
        print("요약: refactor_audit 실행 불능 — 인자 오류(위 사용법)")
        return EXIT_ERR
    project: Path = Path(ns.project).resolve()
    try:
        if ns.command == "plan":
            if (ns.against is None) == (ns.out is None) or (ns.against and ns.names):
                raise ToolError("plan 은 --out(선택 --names) 또는 --against 중 하나만 받는다")
            return cmd_plan(project, ns.unit, Path(ns.debt), Path(ns.out) if ns.out else None,
                            Path(ns.against) if ns.against else None, Path(ns.names) if ns.names else None)
        if ns.command == "residual":
            return cmd_residual(project, Path(ns.folder), ns.finalize)
        if ns.command == "standing":
            return cmd_standing(project, Path(ns.folder) if ns.folder else None, ns.gate)
        corpus: Corpus = Corpus(ns.platform, Path(ns.plugin_root).resolve() if ns.plugin_root else None)
        if ns.self_test:
            return cmd_self_test(corpus)
        if ns.command == "check":
            return cmd_check(corpus, project, Path(ns.audit))
        if ns.command == "check-verdict":
            return cmd_check_verdict(corpus, project, Path(ns.audit),
                                     Path(ns.feedback) if ns.feedback else None, ns.final)
        ap.print_usage()
        print("요약: refactor_audit 실행 불능 — 하위 명령 없음")
        return EXIT_ERR
    except (ToolError, DebtError, OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"실행 불능: {type(exc).__name__}: {exc}", file=sys.stderr)
        print(f"요약: refactor_audit {ns.command or 'self-test'} 실행 불능 — {str(exc)[:160]}")
        return EXIT_ERR


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
