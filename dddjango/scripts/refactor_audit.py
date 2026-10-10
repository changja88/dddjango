#!/usr/bin/env python3
"""리팩토링 모드 결정적 도구 — BC 점검(R2)·판정(R3)·G2 잔존의 기계 판정(표준 라이브러리 전용).

Coordinator «리팩토링 모드» 절이 이 도구를 부른다. 리뷰어·architect 에게는 Bash 가 없다 —
도구는 Coordinator 만 돌리고, 산출은 파일로 쓰고 경로만 넘긴다.

정규화(`normalize`)는 규칙 팩 생성기(`workspace/tools/ontology_rulepack.py`)가 블록 해시를
계산할 때 그대로 빌려 쓴다 — 설치본의 결속 대조와 팩의 해시가 한 함수에서 나온다.

사용(대상 프로젝트 루트에서):
  refactor_audit.py plan <bc> --out <audit 폴더> [--stage <운영 전 출처>]
                                                        렌즈·조각·점검 절 → plan.md(`운영 단계: 운영 전 <출처>` 줄 — R0′)
  refactor_audit.py outline <bc> --out <audit 폴더>     파일별 정의·행 → outline.md
  refactor_audit.py check <audit 폴더>                  리뷰어 표 인용·위치 검사 + 블록 결속 → check.md
  refactor_audit.py sections <audit 폴더>               판정 입력(절 원문·규범 주석·Override 둘) → sections.md
  refactor_audit.py check-verdict <audit 폴더> [--feedback <파일>] [--final]
                                                        verdict.md 검사 → verdict-log.md append · (exit 0) verdict-final.md · `요약:` 1행
  refactor_audit.py resolution <산출물 폴더> [--gate]    명세 «슬라이스 0 해소 판정» 표 검사(커버 · 판정 값 해소·변경·불가 ·
                                                        불가 범주 · 막는 것 · 처방 앵커 · 인용 밖 반대 규칙 증거) + 렌즈별
                                                        M 목록 — --gate 는 부분·불가의 재상정 결정 줄 · 요지 축소 번호 일치까지
  refactor_audit.py changes <산출물 폴더> [--candidate | --applied <후보 스냅숏> | --gate] [--baseline <창 open 기록>]
                                                        명세 «바뀌는 것 목록» · «다른 BC 편집 목록» 검사 — --candidate 는
                                                        g1/<UTC>-candidate.json + 후보 digest · --applied 는 반영 대조 ·
                                                        --gate 는 G1 결정 줄 정합 + 최종 digest
  refactor_audit.py deps <bc> --out <산출물 폴더>/deps/<시각>/
                                                        BC 의존(SCC · 받는 쪽 · HTTP 소비 · 공유 표면 · 레인 겹침 · 보류)
  refactor_audit.py residual <산출물 폴더> [--candidates <검사기 출력>] [--finalize <시각>]
                                                        G2 의미 항목 잔존(결정적 바닥 → 리뷰어 재확인 묶음) — 리뷰어 확인
                                                        대상이 남은 첫 호출은 exit 0 + `M_m 미정`(판정은 --finalize) ·
                                                        요지 축소 항목은 남긴 요지로 확인
  refactor_audit.py --self-test                         점검 절 실재 · 경로 사상 · 적용 한정 어구·불가 범주·재상정 어휘
                                                        상수 = 규범 문면 · 운영 전 예외 블록 결속(①~④)
공통: --platform claude|codex(기본: 자기 위치로 판별) · --plugin-root <경로> · --rulepack <경로>
exit 0 = 통과 · 2 = red(검사 실패·잔존) · 1 = 실행 불능. 모든 하위 명령이 `요약:` 1행을 낸다.
"""
from __future__ import annotations

import argparse
import ast
import base64
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

_QUOTE_HEAD: "re.Pattern[str]" = re.compile(r"^[ \t]*>[ \t]?", re.M)
_SPACE: "re.Pattern[str]" = re.compile(r"\s+")


def normalize(text: str) -> str:
    """강조(`**`·`*`)·백틱·인용 줄머리(`> `)를 지우고 공백류(줄바꿈 포함)를 전부 지운다.

    인용·문서 양쪽에 같은 정규화를 쓴다 — 문장 중간 강제 줄바꿈에 걸린 인용도 맞는다.
    """
    text = _QUOTE_HEAD.sub("", text)
    text = text.replace("**", "").replace("*", "").replace("`", "")
    return _SPACE.sub("", text)


def block_hash(text: str) -> str:
    """블록 본문의 정규화 sha256 앞 16자 — 팩 `blocks[*].h`."""
    return hashlib.sha256(normalize(text).encode("utf-8")).hexdigest()[:16]


def line_count(text: str) -> int:
    """블록 본문의 행 수 — 팩 `blocks[*].n`(끝 개행은 행을 늘리지 않는다)."""
    return text.count("\n") if text.endswith("\n") else text.count("\n") + 1


# ── 상수 ─────────────────────────────────────────────────────────────────────

EXIT_OK, EXIT_ERR, EXIT_RED = 0, 1, 2
# 조각 순서 — 층 «이름»은 standard_tree 의 BC 직계 칸, «순서»는 여기서 정한다(standard_tree.ROWS 순서와 다르다).
LAYER_ORDER: "tuple[str, ...]" = ("driving_layer", "application_layer", "domain_layer", "driven_layer",
                                  "composition_root", "published_event", "test")
OUTSIDE: str = "트리 밖"
CHUNK_LINES: int = 5000
LENSES: "tuple[str, ...]" = ("ddd", "api", "db", "discipline")
# 두 플러그인의 실행 산출물 폴더(프로젝트 상대) — 그 아래 파일은 residual 해소 근거가 아니다.
OUTPUT_ROOTS: "tuple[str, ...]" = (".dddjango/", ".dddjango-web/")

# 렌즈별 점검 절(토큰 `<문서 키> §<절>` — 문서 키 = 팩 document 에서 `dddjango/` 를 뗀 경로 ·
# 절 = 번호 있는 제목이면 번호, 없으면 제목 원문). 절은 하위 절을 포함한다. 목록 근거·제외 사유는
# workspace/plan/2026-09-26-refactor-path-repair/step5-lens-sections.md(진단 5B §1-4 분류).
_DDD_FINAL: str = "skills/architecture-ddd/references/final.md"
_API_FINAL: str = "skills/architecture-api/references/final.md"
_DB_FINAL: str = "skills/architecture-db/references/final.md"
_NINJA_FINAL: str = "skills/implementation-django-ninja/references/final.md"
_DJANGO_FINAL: str = "skills/implementation-django/references/final.md"
_CLEAN_FINAL: str = "skills/discipline-cleancode/references/final.md"
_HOUSE_SKILL: str = "skills/discipline-houserules/SKILL.md"
_HOUSE_FINAL: str = "skills/discipline-houserules/references/final.md"
_PY_FINAL: str = "skills/implementation-python/references/final.md"


def _sections(doc: str, numbers: "tuple[str | int, ...]") -> "tuple[str, ...]":
    return tuple(f"{doc} §{n}" for n in numbers)


LENS_SECTIONS: "dict[str, tuple[str, ...]]" = {
    "ddd": ("agents/design-review-ddd.md §점검 항목 (도메인 lens만)",
            *_sections(_DDD_FINAL, (1, 2, 3, 4, 5, 6, 7, 8, 9))),
    "api": ("agents/design-review-api.md §점검 항목 (계약 lens만)",
            *_sections(_API_FINAL, (3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14)),
            *_sections(_NINJA_FINAL, (1, 2, 3, 4, 5, 6, 7, 8, 10, 11)),
            *_sections(_DJANGO_FINAL, (8,))),
    "db": ("agents/design-review-db.md §점검 항목 (데이터 lens만)",
           *_sections(_DB_FINAL, (1, 2, 4, 5, 7, 8, 9, 10, 11, 12, 13)),
           *_sections(_DJANGO_FINAL, (1, 2, 3, 4, 5, 9, 10, 11, 12, 15, 16, 17, 18))),
    "discipline": ("agents/discipline-reviewer.md §Phase 2 점검 항목 (클린코드·TDD 규율만)",
                   *_sections(_CLEAN_FINAL, (1, 2, 3, 4, 5, 6, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18)),
                   f"{_CLEAN_FINAL} §핵심 요약 체크리스트",
                   *_sections(_HOUSE_SKILL, (1, 2, 3, 4, 5)),
                   *_sections(_HOUSE_FINAL, (0, 1, 2, 3, 4, 5)),
                   *_sections(_PY_FINAL, (1, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 15, 16, 17, 19, 21, 22, 23,
                                          25, 26))),
}
# 보안 절(결정 12 의 ORM·보안 몫 가운데 보안) — db 렌즈가 켜지면 db, 아니면 api, 둘 다 꺼지면 discipline.
SECURITY_SECTIONS: "tuple[str, ...]" = _sections(_DJANGO_FINAL, (13,))

# 적용 한정 어구 닫힌 목록(적용 범위 규범 문면 «…» 와 같아야 한다 — `--self-test`).
SCOPE_PHRASES: "tuple[str, ...]" = (
    "touched", "grandfather", "이번 작업", "이번 diff", "새로 들어온", "기존 코드 존중", "만들었거나 키운",
    "판정 의무의 주어만", "범위 밖 legacy", "빚 보고 채널", "승인 스코프의 산출물", "승인 스코프가 낳는 산출물",
    "신규 산출물", "추가·변경되는 줄", "기존 줄은 고치지", "옮기지도 고치지도", "이 작업의 것이 아니다",
    "낳는 근거가 승인 스코프", "자동 이동하지 않", "이동 권한이 생기지", "무관·미관여", "새로 얹", "판정을 얹는",
    "얹게 되면", "처음 생기는 슬라이스", "손대는 줄", "손대지 않는", "소급 대상이 아니", "새로 쓰는 값 객체",
    "새로 만드는 자료", "기존 _out 자료", "신규 표준 presentation 표면", "신규 표면", "새 Ninja surface",
    "신규 BC마다", "신규 managed", "레거시 경로", "레거시면", "기존 형태를 보존", "확립된 표면을 유지할 때",
    "자동 변환하지 않", "form을 바꾸지 않", "평면 Django(기존 관례", "평면 Django 맥락", "새 코드", "새 모듈",
    "그 명세만", "구현 코드를 보지 않", "네 몫이 아니", "여전히 보지 않", "Phase 2 implementation에서만",
    "ⓓ 신규(N′∖L′)",
)
PHRASE_MARK: str = "적용 한정 어구"
DUTY_KINDS: "frozenset[str]" = frozenset({"Obligation", "Prohibition"})
ALLOW_KINDS: "frozenset[str]" = frozenset({"Permission", "Exception"})
OTHER_BC: str = "다른 BC 몫"
VERDICTS: "tuple[str, ...]" = ("채택", "병합", "제외", "오탐", "사용자 판단", OTHER_BC)
PROXY_FREE: "tuple[str, ...]" = ("본인 직접", "사용자 원문")
SEPARATE_TYPES: "tuple[str, ...]" = ("타 BC",)
# 리뷰어 표 6번 칸 «바뀌는 것» 닫힌 값(여럿이면 ` + ` · 뒤 `— 한 구`) — 형식 밖은 경고다(판정을 막지 않는다).
CHANGE_COLUMN: str = "바뀌는 것"
CHANGE_NONE: str = "없음"
CHANGE_KINDS: "tuple[str, ...]" = (CHANGE_NONE, "내부 약속", "밖 동작", "DB 구조", "다른 BC 파일")
CHANGE_SHORT: "dict[str, str]" = {"내부 약속": "안", "밖 동작": "밖", "DB 구조": "DB", "다른 BC 파일": "다른 BC"}
# 대상 있는 Override 의 역할 표(한 곳) — 팩의 «norm_kind == Override ∧ overrides ≠ ∅» 집합이 이 값들과 다르면 실행 불능.
SCOPE_ROLE: str = "적용 범위"
OPSAFE_ROLE: str = "운영 전 예외"
OVERRIDE_ROLES: "dict[str, str]" = {SCOPE_ROLE: "R-3526", OPSAFE_ROLE: "R-3620"}
# plan.md 운영 단계 줄(R0′ 기록 — `plan --stage`) · check-verdict 는 이 줄이 없으면 실행 불능이다.
STAGE_LINE: str = "운영 단계"
STAGE_PRE: str = "운영 전"
# `ⓐ 재상정` 절 결정 칸 첫 낱말 닫힌 어휘(Coordinator Phase 1 «슬라이스 0 과 비위반 이동의 STOP» 문면 — `--self-test`).
# 밖이면 실행 불능이다 — 표기가 흔들려 `M<n>` 이 조용히 빠지는(fail-open) 길을 막는다.
RECONSIDER_TOKENS: "tuple[str, ...]" = ("별도", "선행", "ⓑ", "플러그인", "작업", "요지")
RECONSIDER_MARK: str = "결정 칸의 첫 낱말은"
REDUCE_TOKEN: str = "요지"
REDUCE_BASIS: "tuple[str, ...]" = ("해소 판정 표", "사용자 선택")
# 명세 «슬라이스 0 해소 판정» 표(Coordinator 리팩토링 모드 절 문면 — 불가 범주 상수는 `--self-test` 가 대조한다).
# «정리» = 해소 ∪ 변경 — 변경 행은 처방 앵커 필수 · 막는 것 칸 = `V<n>[ · V<m>]` · 불가 범주 칸 `—`.
CHANGE_VERDICT: str = "변경"
CLEANED_VERDICTS: "tuple[str, ...]" = ("해소", CHANGE_VERDICT)
RESOLUTION_VERDICTS: "tuple[str, ...]" = ("해소", CHANGE_VERDICT, "불가")
REMOVED_CATEGORY: str = "재상정 제외"          # 재상정 결정으로 항목 전체를 뺀 뒤 해소이던 요지(전체 제외 줄이 있어야 한다)
OPPOSITE_CATEGORY: str = "반대 방향 규칙"
UNAPPROVED_CATEGORY: str = "변경 미승인"       # G1 에서 고르지 않은 밖 동작 V 의 요지
RESOLUTION_CATEGORIES: "tuple[str, ...]" = ("편집 범위 밖", OPPOSITE_CATEGORY, "검사기 오탐", REMOVED_CATEGORY,
                                            UNAPPROVED_CATEGORY, "지원 안 함")
CATEGORY_MARK: str = "불가 범주(닫힌 목록)"
RESOLUTION_COLUMNS: int = 8
ANCHOR_MIN: int = 8                            # 처방 앵커 정규화 최소 길이
OPP_QUOTE_MIN, OPP_QUOTE_MAX = 20, 60          # 인용 밖 반대 규칙의 원문 인용 길이(자)
_RESOLUTION_HEADING: "re.Pattern[str]" = re.compile(r"^(#{1,6})\s+(?:§?[0-9][0-9.]*[.)]?\s+)?슬라이스 0 해소 판정")
_EMPTY: "tuple[str, ...]" = ("", "—", "-", "없음")


def _standing_mention(text: str) -> bool:
    """상시 답 출처를 적은 줄인가 — 공백·강조·백틱 변형까지 잡는다(상시 답은 걷혔다 — 이번 실행 몫에 있으면 실행 불능)."""
    return "출처=상시답" in re.sub(r"[\s*`]", "", text)


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


class ToolError(RuntimeError):
    """실행 불능(exit 1) — 입력·재료 결손(공개 함수 `changes_snapshot` 등의 RuntimeError 계열 예외)."""


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise ToolError(f"파일 없음 — {path}") from None


# ── 문서 색인(절·블록·문장) ─────────────────────────────────────────────────

_FENCE: "re.Pattern[str]" = re.compile(r"^ {0,3}(`{3,}|~{3,})")
_HEADING: "re.Pattern[str]" = re.compile(r"^(#{1,6})\s+(.*)$")
_ANCHOR: "re.Pattern[str]" = re.compile(r"^§?([0-9]+(?:[.\-][0-9A-Za-z]+)*)[.)]?(?=\s|$)")
_LIST_HEAD: "re.Pattern[str]" = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s")
_CIRCLED: str = "①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳"


def _inline(text: str) -> str:
    """줄머리가 아닌 조각의 정규화 — `normalize` 에서 줄머리 규칙만 뺀 것."""
    return _SPACE.sub("", text.replace("*", "").replace("`", ""))


class DocIndex:
    """설치본 문서 하나 — 행·정규화 본문·절·블록 창 결속."""

    def __init__(self, path: Path) -> None:
        self.path: Path = path
        raw: str = _read(path)
        self.lines: "list[str]" = raw.split("\n")
        if self.lines and self.lines[-1] == "":
            self.lines.pop()
        self.norm: "list[str]" = [normalize(ln) for ln in self.lines]
        self.off: "list[int]" = [0]
        for piece in self.norm:
            self.off.append(self.off[-1] + len(piece))
        self.text: str = "".join(self.norm)
        self.headings: "list[tuple[int, int, str, str]]" = self._headings()
        self._windows: "dict[int, dict[str, list[int]]]" = {}

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
                    continue
                if marker[0] == fence[0] and len(marker) >= len(fence) and ln.strip() == marker:
                    fence = None
                    continue
            if fence is not None:
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
            if (anchor and anchor == token.lstrip("§")) or normalize(text) == want:
                end: int = len(self.lines)
                for line2, level2, _t, _a in self.headings[idx + 1:]:
                    if level2 <= level:
                        end = line2
                        break
                return line, end
        return None

    def line_of(self, offset: int) -> int:
        """정규화 본문 오프셋 → 행 번호(0 기준)."""
        lo, hi = 0, len(self.lines)
        while lo < hi:
            mid = (lo + hi) // 2
            if self.off[mid + 1] <= offset:
                lo = mid + 1
            else:
                hi = mid
        return lo

    def occurrences(self, quote_norm: str, a: int = 0, b: "int | None" = None) -> "list[tuple[int, int]]":
        """행 범위 [a, b) 안의 인용 출현(정규화 오프셋 [s, e))."""
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

    def windows(self, n: int) -> "dict[str, list[int]]":
        """n 행 창의 정규화 해시 → 시작 행 목록."""
        if n not in self._windows:
            table: "dict[str, list[int]]" = {}
            for i in range(0, max(0, len(self.lines) - n + 1)):
                h: str = hashlib.sha256(self.text[self.off[i]:self.off[i + n]].encode("utf-8")).hexdigest()[:16]
                table.setdefault(h, []).append(i)
            self._windows[n] = table
        return self._windows[n]

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
            if not raw.strip():
                close(pos)
                continue
            if _LIST_HEAD.match(raw):
                close(pos)
            pieces: "list[tuple[str, bool]]" = []   # (조각, 조각 뒤 경계)
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
            lengths: "list[int]" = [len(normalize(p)) if i == 0 else len(_inline(p)) for i, (p, _b) in enumerate(pieces)]
            if sum(lengths) != len(self.norm[k]):     # 조각 정규화가 행 정규화와 어긋나면 행 하나를 한 조각으로
                pieces, lengths = [(raw, False)], [len(self.norm[k])]
            for (piece, boundary), length in zip(pieces, lengths):
                if cur is None and length:
                    cur = pos
                pos += length
                if boundary:
                    close(pos)
        close(pos)
        return spans


class Corpus:
    """설치본(플랫폼) · 규칙 팩 · 문서 색인."""

    def __init__(self, platform: "str | None" = None, root: "Path | None" = None,
                 rulepack: "Path | None" = None) -> None:
        here: Path = Path(__file__).resolve().parent
        if platform is None:
            if (here.parent / "commands" / "dddjango.md").is_file():
                platform = "claude"
            elif (here.parent / "SKILL.md").is_file():
                platform = "codex"
            else:
                raise ToolError("플랫폼 판별 불가 — --platform claude|codex 와 --plugin-root 를 준다")
        self.platform: str = platform
        if root is None:
            root = here.parent if platform == "claude" else here.parent.parent
        self.root: Path = root
        pack_path: Path = rulepack or here / "rulepack.json"
        self.rp: dict = json.loads(_read(pack_path))
        for key in ("works", "blocks"):
            if key not in self.rp:
                raise ToolError(f"규칙 팩에 `{key}` 가 없다 — 팩이 로드맵 5 투영 이전 판이다({pack_path})")
        self.works: "dict[str, dict]" = self.rp["works"]
        self.blocks: "dict[str, dict]" = self.rp["blocks"]
        self._docs: "dict[str, DocIndex]" = {}
        self._doc_blocks: "dict[str, list[str]]" = {}
        for bid in self.blocks:
            self._doc_blocks.setdefault(bid.rsplit("/", 2)[0], []).append(bid)
        self._spans: "dict[str, dict[str, list[tuple[int, int]]]]" = {}

    # 경로 사상 ------------------------------------------------------------
    @staticmethod
    def key_of(document: str) -> str:
        return document[len("dddjango/"):] if document.startswith("dddjango/") else document

    def canon_key(self, raw: str) -> str:
        """리뷰어가 쓴 문서 표기 → 문서 키(Claude 표기). Codex 표기도 받는다."""
        key: str = raw.strip().strip("`").strip()
        if key.startswith("dddjango/"):
            key = key[len("dddjango/"):]
        m = re.fullmatch(r"skills/dddjango/SKILL\.md", key)
        if m:
            return "commands/dddjango.md"
        m = re.fullmatch(r"skills/dddjango-([\w-]+)/(.+)", key)
        if m:
            name, rest = m.group(1), m.group(2)
            if rest == "SKILL.md" and f"dddjango/agents/{name}.md" in self._doc_blocks:
                return f"agents/{name}.md"
            return f"skills/{name}/{rest}"
        return key

    def path_of(self, key: str) -> Path:
        if self.platform == "claude":
            return self.root / key
        m = re.fullmatch(r"agents/([\w-]+)\.md", key)
        if m:
            return self.root / f"dddjango-{m.group(1)}" / "SKILL.md"
        if key == "commands/dddjango.md":
            return self.root / "dddjango" / "SKILL.md"
        m = re.fullmatch(r"skills/([\w-]+)/(.+)", key)
        if m:
            prefixed: Path = self.root / f"dddjango-{m.group(1)}" / m.group(2)
            return prefixed if prefixed.is_file() else self.root / m.group(1) / m.group(2)
        return self.root / key

    def doc(self, key: str) -> DocIndex:
        if key not in self._docs:
            self._docs[key] = DocIndex(self.path_of(key))
        return self._docs[key]

    # 블록 결속 ------------------------------------------------------------
    def block_spans(self, key: str) -> "dict[str, list[tuple[int, int]]]":
        """문서의 규범 블록 → 해시가 맞는 행 범위 [i, i+n) 목록(겹친 창 여럿이면 전부)."""
        if key not in self._spans:
            index: DocIndex = self.doc(key)
            spans: "dict[str, list[tuple[int, int]]]" = {}
            for bid in self._doc_blocks.get(f"dddjango/{key}", []):
                meta: dict = self.blocks[bid]
                starts: "list[int]" = index.windows(int(meta["n"])).get(meta["h"], [])
                if starts:
                    spans[bid] = [(i, i + int(meta["n"])) for i in starts]
            self._spans[key] = spans
        return self._spans[key]

    def bind(self, key: str, quote: str, rng: "tuple[int, int] | None" = None) -> "tuple[str | None, str]":
        """인용 → 결속 블록 id(없으면 None) · 사유. 서로 다른 블록 둘 이상 적중은 결속 실패."""
        index: DocIndex = self.doc(key)
        a, b = rng if rng else (0, len(index.lines))
        occ = index.occurrences(normalize(quote), a, b)
        if not occ:
            return None, "인용이 문서에 없다"
        hit: "set[str]" = set()
        for s, e in occ:
            li, lj = index.line_of(s), index.line_of(e - 1)
            for bid, spans in self.block_spans(key).items():
                if any(i <= li and lj < j for i, j in spans):
                    hit.add(bid)
        if not hit:
            return None, "결속 실패(인용이 규범 블록 밖)"
        if len(hit) > 1:
            return None, f"결속 실패(서로 다른 블록 {len(hit)}개 적중 — 더 긴 인용)"
        return hit.pop(), ""

    def quote_span(self, key: str, bid: str, quote: str) -> "list[tuple[int, int]]":
        """결속 블록 안의 인용 출현(정규화 오프셋)."""
        index: DocIndex = self.doc(key)
        out: "list[tuple[int, int]]" = []
        for i, j in self.block_spans(key).get(bid, []):
            out.extend(index.occurrences(normalize(quote), i, j))
        return sorted(set(out))

    def quote_sentences(self, key: str, bid: str, quote: str) -> str:
        """인용이 든 문장(들)의 정규화 본문 — 출현 전부의 걸친 문장 합."""
        index: DocIndex = self.doc(key)
        found: "list[str]" = []
        for i, j in self.block_spans(key).get(bid, []):
            sents = index.sentences(i, j)
            for s, e in index.occurrences(normalize(quote), i, j):
                found.extend(index.text[a:b] for a, b in sents if a < e and s < b)
        return "".join(found)

    def kinds(self, bid: str) -> "set[str]":
        return {self.works[w]["norm_kind"] for w in self.blocks[bid]["works"] if w in self.works}

    # 대상 있는 Override(적용 범위 · 운영 전 예외) --------------------------
    def override_norms(self) -> "dict[str, tuple[str, set[str]]]":
        """역할 → (R-ID, 대상 목록) — 팩의 «norm_kind == Override ∧ overrides ≠ ∅» 집합이 역할 표와 같아야 한다."""
        found: "set[str]" = {r for r, w in self.works.items() if w.get("norm_kind") == "Override" and w.get("overrides")}
        want: "set[str]" = set(OVERRIDE_ROLES.values())
        if found != want:
            raise ToolError(f"대상 있는 Override 집합 ≠ 역할 표 — 팩 {sorted(found)[:5]} · 역할 표 "
                            + " · ".join(f"{k} {v}" for k, v in OVERRIDE_ROLES.items()))
        return {role: (rid, set(self.works[rid]["overrides"])) for role, rid in OVERRIDE_ROLES.items()}

    def blocked_norms(self) -> "tuple[dict[str, tuple[str, set[str]]], set[str]]":
        """(역할 표, 근거가 될 수 없는 R-ID — 두 Override 자신과 그 대상 · 조건부 대상 전부)."""
        roles = self.override_norms()
        out: "set[str]" = set()
        for rid, targets in roles.values():
            out |= {rid} | targets
        return roles, out

    def phrase_hit(self, sentences_norm: str) -> "list[str]":
        return [p for p in SCOPE_PHRASES if normalize(p) in sentences_norm]


# ── 대상 프로젝트 ────────────────────────────────────────────────────────────

def _bc_dir(project: Path, bc: str) -> Path:
    path: Path = project / "application" / bc
    if not path.is_dir():
        raise ToolError(f"대상 BC 없음 — {path}")
    return path


def _bc_files(project: Path, bc: str) -> "list[str]":
    base: Path = _bc_dir(project, bc)
    out: "list[str]" = []
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = sorted(d for d in dirnames if d != "__pycache__")
        for name in sorted(filenames):
            if name.endswith(".py"):
                out.append((Path(dirpath) / name).relative_to(project).as_posix())
    return sorted(out)


def _lines_of(project: Path, rel: str) -> int:
    try:
        return len((project / rel).read_text(encoding="utf-8", errors="replace").splitlines())
    except OSError:
        return 0


def _layer(rel: str, bc: str) -> str:
    parts: "list[str]" = rel.split("/")
    if rel == f"application/{bc}/__init__.py":      # BC 패키지 자신 — 트리 안(첫 층 조각에 싣는다)
        return LAYER_ORDER[0]
    head: str = parts[2] if len(parts) > 3 else ""
    return head if head in LAYER_ORDER else OUTSIDE


def _is_adapter(project: Path, rel: str) -> bool:
    if "/driving_layer/api/" in rel:
        return True
    text: str = (project / rel).read_text(encoding="utf-8", errors="replace")
    return bool(re.search(r"^\s*from ninja(?:_extra)?\b|^\s*import ninja|@api_controller", text, re.M))


def _defines_model(project: Path, rel: str) -> bool:
    try:
        tree = ast.parse((project / rel).read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:
        return False
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for base in node.bases:
                if (isinstance(base, ast.Attribute) and base.attr == "Model"
                        and isinstance(base.value, ast.Name) and base.value.id == "models"):
                    return True
                if isinstance(base, ast.Name) and base.id == "Model":
                    return True
    return False


def _parse_location(text: str) -> "tuple[str, int, int] | None":
    m = re.fullmatch(r"`?([^\s`:]+):(\d+)(?:-(\d+))?`?", text.strip())
    if not m:
        return None
    a: int = int(m.group(2))
    return m.group(1), a, int(m.group(3) or a)


def _in_bc(rel: str, bc: str) -> bool:
    """`..`·절대 경로로 BC 밖을 가리키지 않는가 — normpath 뒤 접두 검사."""
    norm: str = os.path.normpath(rel).replace(os.sep, "/")
    return not os.path.isabs(rel) and norm.startswith(f"application/{bc}/")


def _location_ok(project: Path, loc: "tuple[str, int, int]") -> bool:
    rel, a, b = loc
    path: Path = project / rel
    if not path.is_file() or a < 1 or b < a:
        return False
    return b <= _lines_of(project, rel)


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


# ── plan ─────────────────────────────────────────────────────────────────────

def _lens_state(project: Path, files: "list[str]") -> "dict[str, str]":
    api = next((f for f in files if _is_adapter(project, f)), None)
    db = next((f for f in files if _defines_model(project, f)), None)
    return {"ddd": "항상", "discipline": "항상",
            "api": f"켜짐 — HTTP 어댑터 `{api}`" if api else "꺼짐 — HTTP 어댑터 없음",
            "db": f"켜짐 — Django 모델 `{db}`" if db else "꺼짐 — Django 모델 없음"}


def _stack(project: Path, files: "list[str]") -> "list[tuple[list[str], int]]":
    """파일을 순서대로 쌓아 문턱에서 끊는다 — 문턱 넘는 단일 파일은 단독 조각."""
    groups: "list[tuple[list[str], int]]" = []
    cur: "list[str]" = []
    size: int = 0
    for f in files:
        n: int = _lines_of(project, f)
        if n > CHUNK_LINES:
            if cur:
                groups.append((cur, size))
            groups.append(([f], n))
            cur, size = [], 0
            continue
        if cur and size + n > CHUNK_LINES:
            groups.append((cur, size))
            cur, size = [], 0
        cur.append(f)
        size += n
    if cur:
        groups.append((cur, size))
    return groups


def _chunks(project: Path, bc: str, files: "list[str]") -> "list[tuple[str, str, list[str], int]]":
    """(조각 id, 층 표기, 파일, 행 수) — 층 순서로 쌓아 문턱에서 끊는다 · 트리 밖은 따로(같은 문턱)."""
    ordered: "list[str]" = sorted((f for f in files if _layer(f, bc) != OUTSIDE),
                                  key=lambda f: (LAYER_ORDER.index(_layer(f, bc)), f))
    outside: "list[str]" = [f for f in files if _layer(f, bc) == OUTSIDE]
    out: "list[tuple[str, str, list[str], int]]" = []
    for group, n in _stack(project, ordered):
        layers: "list[str]" = sorted({_layer(f, bc) for f in group}, key=LAYER_ORDER.index)
        out.append((f"{len(out) + 1:02d}", "·".join(layers), group, n))
    for group, n in _stack(project, outside):
        out.append((f"{len(out) + 1:02d}", OUTSIDE, group, n))
    return out


def _stage_source(raw: str) -> str:
    """`plan --stage <R0′ 기록>` → 운영 전 출처 — 앞의 `운영 전`(구분 `—`·`·`·`:`)은 떼고, 출처는 본인 직접 · 사용자 원문만(대리 불가)."""
    text: str = raw.strip()
    if text.startswith("운영 중"):
        raise ToolError("운영 단계가 «운영 중»이다 — 이 실행은 G0 정지(정의 재결정 대기)이고 plan 을 만들지 않는다")
    if text.startswith(STAGE_PRE):
        text = text[len(STAGE_PRE):].lstrip(" \t—·:-").strip()
    if not text.startswith(PROXY_FREE):
        raise ToolError(f"--stage 출처 `{raw.strip()[:80]}` 가 본인 직접 · 사용자 원문이 아니다(운영 단계는 대리 답을 받지 않는다)")
    return text


def _plan_stage(text: str) -> "str | None":
    """plan.md 의 `운영 단계: 운영 전 <출처>` 줄의 출처(없으면 None)."""
    m = re.search(rf"^\s*[-*]?\s*{STAGE_LINE}:\s*{STAGE_PRE}\s+(\S.*)$", text, re.M)
    return m.group(1).strip() if m else None


def cmd_plan(project: Path, bc: str, out: Path, stage: "str | None" = None) -> int:
    source: "str | None" = _stage_source(stage) if stage is not None else None
    files: "list[str]" = _bc_files(project, bc)
    if not files:
        raise ToolError(f"대상 BC 에 .py 파일이 없다 — application/{bc}/")
    state: "dict[str, str]" = _lens_state(project, files)
    lenses: "list[str]" = [l for l in LENSES if not state[l].startswith("꺼짐")]
    security: str = "db" if "db" in lenses else "api" if "api" in lenses else "discipline"
    chunks = _chunks(project, bc, files)
    shown: "dict[str, str]" = {l: f"{l}+보안" if l == security else l for l in LENSES}  # 파견 입력 렌즈 이름(파일명은 기본 렌즈)
    out.mkdir(parents=True, exist_ok=True)
    try:
        head: str = _git(project, "rev-parse", "HEAD").strip()
    except (subprocess.CalledProcessError, OSError):
        raise ToolError("대상 프로젝트가 git 저장소가 아니다(audit 앵커 HEAD 를 기록할 수 없다)") from None
    # R2 시점 BC 의 미커밋 변경 수 — 0 이 아니면 이 audit 은 HEAD 로 되짚을 수 없다(G0 정지 재개의 재사용 조건).
    dirty: int = len([ln for ln in _git(project, "status", "--porcelain", "--untracked-files=all", "--",
                                        f"application/{bc}/").splitlines() if ln.strip()])
    lines: "list[str]" = ["# refactor_audit plan", "", f"- BC: `{bc}`", f"- HEAD {head}", f"- BC 미커밋 변경 {dirty}",
                          f"- 파일 {len(files)} · 행 {sum(c[3] for c in chunks)} · 조각 {len(chunks)} · 조각 문턱 {CHUNK_LINES}행",
                          f"- 보안 절 담당: {security}"]
    if source is not None:
        lines.append(f"- {STAGE_LINE}: {STAGE_PRE} {source}")
    lines += ["", "## 렌즈", ""]
    lines += [f"- {shown[l]}: {state[l]}" for l in LENSES]
    lines += ["", "## 조각", "", "| 조각 | 층 | 파일 수 | 행 수 |", "|---|---|---|---|"]
    lines += [f"| {cid} | {layer} | {len(group)} | {n} |" for cid, layer, group, n in chunks]
    for cid, _layer, group, _n in chunks:
        lines += ["", f"### 조각 {cid} 파일", ""] + [f"- {f}" for f in group]
    lines += ["", "## 파견", "", "| 산출 파일 | 렌즈 | 조각 |", "|---|---|---|"]
    for lens in lenses:
        for cid, _layer_name, _g, _n in chunks:
            lines.append(f"| {lens}-{cid}.md | {shown[lens]} | {cid} |")
    lines += ["", "## 렌즈별 점검 절", ""]
    for lens in lenses:
        lines.append(f"### {shown[lens]}")
        lines += [f"- {t}" for t in LENS_SECTIONS[lens]]
        if lens == security:
            lines += [f"- {t}" for t in SECURITY_SECTIONS]
        lines.append("")
    (out / "plan.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    print(f"| 렌즈 | 상태 |\n|---|---|\n" + "\n".join(f"| {shown[l]} | {state[l]} |" for l in LENSES))
    stage_tail: str = f" · {STAGE_LINE} {STAGE_PRE}" if source is not None else ""
    print(f"요약: plan BC {bc} · 렌즈 {len(lenses)}({'·'.join(shown[l] for l in lenses)}) · 조각 {len(chunks)} · "
          f"파견 {len(lenses) * len(chunks)} · 보안 {security} · 파일 {len(files)}{stage_tail} → {out / 'plan.md'}")
    return EXIT_OK


# ── outline ──────────────────────────────────────────────────────────────────

def cmd_outline(project: Path, bc: str, out: Path) -> int:
    files: "list[str]" = _bc_files(project, bc)
    lines: "list[str]" = [f"# outline — `{bc}`", ""]
    defs: int = 0
    for rel in files:
        source: str = (project / rel).read_text(encoding="utf-8", errors="replace")
        lines.append(f"## {rel} ({len(source.splitlines())}행)")
        try:
            tree = ast.parse(source)
        except SyntaxError as exc:
            lines += [f"- 파싱 불가: {exc.msg} ({exc.lineno}행)", ""]
            continue
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                kind: str = "class" if isinstance(node, ast.ClassDef) else "def"
                lines.append(f"- {node.lineno} {kind} {node.name}")
                defs += 1
                if isinstance(node, ast.ClassDef):
                    for sub in node.body:
                        if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            lines.append(f"  - {sub.lineno} def {sub.name}")
                            defs += 1
        lines.append("")
    out.mkdir(parents=True, exist_ok=True)
    (out / "outline.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    print(f"요약: outline BC {bc} · 파일 {len(files)} · 정의 {defs} → {out / 'outline.md'}")
    return EXIT_OK


# ── audit 폴더 읽기 ──────────────────────────────────────────────────────────

def _cells(line: str) -> "list[str]":
    """표 행 → 칸 — 이스케이프(`\\|`)되지 않은 `|` 에서만 가르고 `\\|` 는 `|` 로 되돌린다."""
    s: str = line.strip()
    s = s[1:] if s.startswith("|") else s
    s = s[:-1] if s.endswith("|") and not s.endswith("\\|") else s
    return [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", s)]


def _table_rows(text: str) -> "list[list[str]]":
    rows: "list[list[str]]" = []
    for ln in text.splitlines():
        s: str = ln.strip()
        if not s.startswith("|") or re.fullmatch(r"\|[\s:|-]*\|", s):
            continue
        rows.append(_cells(s))
    return rows


class Plan:
    def __init__(self, audit: Path) -> None:
        text: str = _read(audit / "plan.md")
        m = re.search(r"^- BC: `([^`]+)`", text, re.M)
        if not m:
            raise ToolError("plan.md 에 BC 줄이 없다")
        self.bc: str = m.group(1)
        self.stage: "str | None" = _plan_stage(text)
        sec: str = text.split("## 파견", 1)[1].split("\n## ", 1)[0] if "## 파견" in text else ""
        self.dispatch: "list[tuple[str, str, str]]" = [(r[0], r[1].split("+", 1)[0], r[2]) for r in _table_rows(sec)
                                                      if len(r) >= 3 and r[0].endswith(".md")]
        if not self.dispatch:
            raise ToolError("plan.md 에 파견 표가 없다")


def _change_kinds(cell: str) -> "frozenset[str] | None":
    """«바뀌는 것» 칸 → 값 집합(형식 밖이면 None) — `없음` 은 혼자 · 나머지는 ` + ` 로 겹침 · 첫 `—` 뒤는 한 구."""
    head: str = re.sub(r"[*`]", "", cell).partition("—")[0].strip()
    parts: "list[str]" = [p.strip() for p in head.split("+")]
    if not head or any(p not in CHANGE_KINDS for p in parts) or len(set(parts)) != len(parts):
        return None
    if CHANGE_NONE in parts and len(parts) > 1:
        return None
    return frozenset(parts)


class Row:
    """리뷰어 표 한 행."""

    def __init__(self, rid: str, lens: str, cells: "list[str]", short: bool = False) -> None:
        self.rid: str = rid
        self.short: bool = short          # 번호 행인데 칸이 모자라다(형식 — 무언 삭제 대신 인용 불일치)
        self.lens: str = lens
        self.cells: "list[str]" = cells
        self.rule: str = cells[1]
        self.opposite: str = cells[2] if cells[2] not in ("", "—", "-", "없음") else ""
        self.where: str = cells[3]
        self.gist: str = cells[4]
        self.fixable: str = cells[5]                       # 6번 칸 «바뀌는 것»(닫힌 값 — `_change_kinds`)
        self.changes: "frozenset[str] | None" = _change_kinds(cells[5])
        self.same_c: str = cells[6] if len(cells) > 6 else ""
        self.status: str = ""
        self.reason: str = ""
        self.key: str = ""
        self.bid: "str | None" = None
        self.quote: str = ""
        self.opp_key: str = ""
        self.opp_bid: "str | None" = None
        self.opp_quote: str = ""

    @property
    def no_rule(self) -> bool:
        return bool(re.search(r"근거 없음\s*\(\s*불편", self.rule))


_CITE: "re.Pattern[str]" = re.compile(r"^(?:규칙\s*=\s*)?`?(?P<doc>[^\s§`]+)`?\s*§\s*(?P<sec>[^«]+?)\s*«(?P<q>.*)»\s*$")


def _cite(cell: str) -> "tuple[str, str, str] | None":
    m = _CITE.match(cell.strip())
    return (m.group("doc"), m.group("sec"), m.group("q")) if m else None


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
            if len(cells) < 6 and not numbered:
                continue
            short: bool = len(cells) < 6
            while len(cells) < 7:
                cells.append("")
            no: str = cells[0] if numbered else str(k)
            rows.append(Row(f"{name[:-3]}#{no}", lens, cells, short))
    return rows


def _check_rows(corpus: Corpus, project: Path, bc: str, rows: "list[Row]") -> None:
    for row in rows:
        if row.short:
            row.status, row.reason = "인용 불일치", "칸 부족(산출 표 7칸 형식 아님)"
            continue
        if row.no_rule:
            row.status = "불편"
            continue
        cite = _cite(row.rule)
        if not cite:
            row.status, row.reason = "인용 불일치", "규칙 칸 형식(`<문서 키> §<절> «인용»`) 아님"
            continue
        key: str = corpus.canon_key(cite[0])
        if not corpus.path_of(key).is_file():
            row.status, row.reason = "인용 불일치", f"문서 없음 `{cite[0]}`"
            continue
        index: DocIndex = corpus.doc(key)
        rng = index.section(cite[1])
        if rng is None:
            row.status, row.reason = "인용 불일치", f"절 없음 `{cite[0]} §{cite[1]}`"
            continue
        if not index.occurrences(normalize(cite[2]), *rng):
            row.status, row.reason = "인용 불일치", f"인용이 `{cite[0]} §{cite[1]}` 본문에 없다"
            continue
        locs = [_parse_location(t) for t in _locations(row.where)]
        if not locs or any(loc is None for loc in locs):
            row.status, row.reason = "인용 불일치", f"파일:행 형식 아님 `{row.where}`"
            continue
        bad = [f"{l[0]}:{l[1]}" for l in locs if not (_in_bc(l[0], bc)  # type: ignore[index]
                                                     and _location_ok(project, l))]  # type: ignore[arg-type]
        if bad:
            row.status, row.reason = "인용 불일치", f"위치가 작업 트리에 없거나 BC 밖: {', '.join(bad[:3])}"
            continue
        row.status, row.key, row.quote = "통과", key, cite[2]
        row.bid, why = corpus.bind(key, cite[2], rng)
        if row.bid is None:
            row.reason = why
        if row.opposite:
            opp = _cite(row.opposite)
            if opp:
                row.opp_key, row.opp_quote = corpus.canon_key(opp[0]), opp[2]
                if corpus.path_of(row.opp_key).is_file():
                    orng = corpus.doc(row.opp_key).section(opp[1])
                    if orng is not None:           # 없는 절이면 결속하지 않는다(근거 불가 — fail-closed)
                        row.opp_bid, _w = corpus.bind(row.opp_key, opp[2], orng)


def _change_warnings(rows: "list[Row]") -> "list[str]":
    """«바뀌는 것» 칸이 닫힌 값 밖인 행(칸 부족 행은 인용 불일치가 이미 잡는다)."""
    return [f"{r.rid} «{CHANGE_COLUMN}» 칸 `{r.fixable}` 이 닫힌 값({' · '.join(CHANGE_KINDS)} — 여럿이면 ` + `) 밖"
            for r in rows if not r.short and r.changes is None]


def _loose_tail(loose: "list[str]") -> str:
    return f" · {CHANGE_COLUMN} 형식 밖 {len(loose)}(경고)" if loose else ""


def _works_text(corpus: Corpus, bid: "str | None") -> str:
    if bid is None:
        return "—"
    return " · ".join(f"{w}({corpus.works[w]['norm_kind']})" for w in corpus.blocks[bid]["works"] if w in corpus.works)


# ── check ────────────────────────────────────────────────────────────────────

def cmd_check(corpus: Corpus, project: Path, audit: Path) -> int:
    plan: Plan = Plan(audit)
    rows: "list[Row]" = _load_rows(audit, plan)
    _check_rows(corpus, project, plan.bc, rows)
    passed = [r for r in rows if r.status == "통과"]
    bad = [r for r in rows if r.status == "인용 불일치"]
    no_rule = [r for r in rows if r.status == "불편"]
    unbound = [r for r in passed if r.bid is None]
    loose = _change_warnings(rows)
    lines: "list[str]" = [f"# check — `{plan.bc}` · {_now()}", "",
                          "| 원 행 | 상태 | 블록 | 규범(종류) | 반대 방향 블록 | 파일:행 | 사유 |",
                          "|---|---|---|---|---|---|---|"]
    for r in rows:
        lines.append(f"| {r.rid} | {r.status} | {r.bid or '—'} | {_works_text(corpus, r.bid)} | "
                     f"{r.opp_bid or ('—' if not r.opposite else '결속 실패')} | {r.where} | {r.reason} |")
    lines += ["", "## 인용 불일치(원 리뷰어 재인용 대상 — 행 목록만)", ""]
    lines += [f"- {r.rid}: {r.reason}" for r in bad] or ["- 없음"]
    lines += ["", f"## «{CHANGE_COLUMN}» 칸 형식 밖(경고 — 판정을 막지 않는다)", ""]
    lines += [f"- {w}" for w in loose] or ["- 없음"]
    (audit / "check.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    for w in loose:
        print(f"  경고: {w}")
    print(f"요약: check 행 {len(rows)} · 통과 {len(passed)} · 인용 불일치 {len(bad)} · 규칙 근거 없는 불편 {len(no_rule)} · "
          f"결속 실패 {len(unbound)}(제외·오탐 근거 불가){_loose_tail(loose)} → {audit / 'check.md'}")
    return EXIT_RED if bad else EXIT_OK


# ── sections ─────────────────────────────────────────────────────────────────

def _annotated_section(corpus: Corpus, key: str, rng: "tuple[int, int]") -> "list[str]":
    index: DocIndex = corpus.doc(key)
    starts: "dict[int, list[str]]" = {}
    for bid, spans in corpus.block_spans(key).items():
        i, _j = spans[0]
        if rng[0] <= i < rng[1]:
            starts.setdefault(i, []).append(bid)
    out: "list[str]" = []
    for k in range(*rng):
        for bid in starts.get(k, []):
            notes = "; ".join(f"{w} · {corpus.works[w]['norm_kind']} · {corpus.works[w]['label']}"
                              for w in corpus.blocks[bid]["works"] if w in corpus.works)
            out.append(f"〔블록 {bid.rsplit('/', 2)[1]}/{bid.rsplit('/', 1)[1]} — {notes}〕")
        out.append(index.lines[k])
    return out


def cmd_sections(corpus: Corpus, project: Path, audit: Path) -> int:
    plan: Plan = Plan(audit)
    rows: "list[Row]" = _load_rows(audit, plan)
    _check_rows(corpus, project, plan.bc, rows)
    wanted: "dict[tuple[str, str], None]" = {}
    for r in rows:
        if r.status != "통과":
            continue
        for cell in (r.rule, r.opposite):
            cite = _cite(cell) if cell else None
            if cite:
                wanted[(corpus.canon_key(cite[0]), cite[1].strip())] = None
    roles = corpus.override_norms()
    lines: "list[str]" = [f"# sections — `{plan.bc}` · {_now()}", "",
                          "판정 근거는 이 파일이 공급한 것뿐이다(자기 스킬 밖 규범을 스스로 찾아 읽지 않는다).", ""]
    notes: "dict[str, str]" = {SCOPE_ROLE: "제외·오탐·반대 방향 근거가 될 수 없다",
                               OPSAFE_ROLE: "대상 · 조건부 대상 — 제외·반대 방향 근거가 될 수 없다"}
    for role, (rid, targets) in roles.items():
        lines += [f"## {role} 규범", ""]
        nkey: str = corpus.key_of(corpus.works[rid]["document"])
        nspans = corpus.block_spans(nkey).get(corpus.works[rid]["block"])
        if not nspans:
            raise ToolError(f"{role} 규범 {rid} 블록을 설치본에서 찾지 못했다(`{nkey}`)")
        i, j = nspans[0]
        lines += [f"〔{rid} · Override · {corpus.works[rid]['label']}〕", *corpus.doc(nkey).lines[i:j], ""]
        lines += [f"### 대상 목록({notes[role]})", "", "| R-ID | 종류 | 라벨 |", "|---|---|---|"]
        for w in sorted(targets):
            meta: dict = corpus.works.get(w, {})
            lines.append(f"| {w} | {meta.get('norm_kind', '?')} | {meta.get('label', '(팩에 없음)')} |")
        lines.append("")
    for key, token in list(wanted):
        if not corpus.path_of(key).is_file():
            del wanted[(key, token)]
            continue
        index: DocIndex = corpus.doc(key)
        rng = index.section(token)
        if rng is None:                    # 반대 방향 칸의 없는 절 — 문서 전체로 대체하지 않는다
            del wanted[(key, token)]
            continue
        lines += [f"## {key} §{token}", ""]
        lines += _annotated_section(corpus, key, rng)
        lines.append("")
    (audit / "sections.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    roles_text: str = " · ".join(f"{role} 규범 {rid} · 대상 {len(t)}" for role, (rid, t) in roles.items())
    print(f"요약: sections 절 {len(wanted)} · {roles_text} → {audit / 'sections.md'}")
    return EXIT_OK


# ── check-verdict ────────────────────────────────────────────────────────────

class Verdict:
    def __init__(self, cells: "list[str]") -> None:
        self.mid: str = cells[0].strip()
        self.origin: "list[str]" = [t for t in re.split(r"\s*[,·]\s*|\s+", cells[1].strip()) if t]
        raw: str = re.sub(r"\s+", " ", cells[2].strip())
        m = re.fullmatch(r"병합\s*(?:→|->)\s*([MC]\d+)", raw)
        self.kind: str = "병합" if m else raw if not raw.startswith("병합") else f"{raw}(대상 없음)"
        self.merge_to: str = m.group(1) if m else ""
        self.ground: str = cells[3].strip() if len(cells) > 3 else ""
        self.where: str = cells[4].strip() if len(cells) > 4 else ""

    @property
    def label(self) -> str:
        if self.kind == "병합" and self.merge_to:
            return f"병합→{self.merge_to[0]}"
        return self.kind


VERDICT_FINAL: str = "verdict-final.md"


def _load_verdicts(audit: Path, name: str = "verdict.md") -> "list[Verdict]":
    out: "list[Verdict]" = []
    for cells in _table_rows(_read(audit / name)):
        if cells and re.fullmatch(r"M\d+", cells[0].strip()) and len(cells) >= 3:
            out.append(Verdict(cells))
    return out


def _write_final(audit: Path, verdicts: "list[Verdict]", final: bool) -> None:
    """exit 0 판의 확정 표 — resolution·residual 이 읽는 한 목록(`--final`·다른 BC 몫 재분류 반영 · verdict.md 는 원문 보존)."""
    def cell(text: str) -> str:
        return text.replace("|", "\\|")

    out: "list[str]" = [f"# verdict-final — check-verdict exit 0 {_now()}{' · final' if final else ''}", "",
                        "| M | 원 행 | 판정 | 근거 | 파일:행 목록 |", "|---|---|---|---|---|"]
    for v in verdicts:
        kind: str = f"병합 → {v.merge_to}" if v.kind == "병합" else v.kind
        out.append(f"| {v.mid} | {' · '.join(v.origin)} | {cell(kind)} | {cell(v.ground)} | {cell(v.where)} |")
    (audit / VERDICT_FINAL).write_text("\n".join(out) + "\n", encoding="utf-8")


def _final_verdicts(audit: Path) -> "dict[str, Verdict]":
    """G0 확정 판정(`verdict-final.md`) — 없으면 실행 불능(재실행 안내는 대상 BC 무변일 때만 · 바뀌었으면 멈춤)."""
    if not (audit / VERDICT_FINAL).is_file():
        raise ToolError(f"의미 audit 의 {VERDICT_FINAL} 이 없다(check-verdict exit 0 판 없음) — 대상 BC 가 그 plan.md 의 "
                        f"HEAD 뒤 바뀌지 않았을 때만(G0 정지 재개 조건) `check-verdict {audit}` 를 다시 돌린다(앞 확정 판이 final "
                        f"이면 --final). 바뀌었으면 다시 돌리지 않고 멈춘다 — 재실행은 바뀐 코드로 원 행을 다시 검사해 G0 확정 표를 바꾼다")
    return {v.mid: v for v in _load_verdicts(audit, VERDICT_FINAL)}


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
    """결정 출처 값 머리가 «본인 직접»·«사용자 원문» 이 아니면 대리 출처다(부분 문자열 판정 금지)."""
    m = re.match(r"\s*출처\s*=\s*(.*)$", source)
    return not (m and m.group(1).strip().startswith(PROXY_FREE))


def _source(feedback: "Path | None") -> str:
    if feedback is None:
        return ""
    first: str = next((ln.strip() for ln in _read(feedback).splitlines() if ln.strip()), "")
    if not first:
        raise ToolError(f"--feedback 첫 줄에 결정 출처가 없다 — {feedback}")
    return first


class Overrides:
    """대상 있는 Override 둘(역할 표 — `Corpus.override_norms`) — 근거 금지 판정의 한 출처."""

    def __init__(self, roles: "dict[str, tuple[str, set[str]]]") -> None:
        self.scope_rid, self.scope = roles[SCOPE_ROLE]
        self.opsafe_rid, self.opsafe = roles[OPSAFE_ROLE]

    def own_role(self, rid: str) -> str:
        """R-ID 가 Override 자신이면 그 역할 이름(아니면 빈 값)."""
        return SCOPE_ROLE if rid == self.scope_rid else OPSAFE_ROLE if rid == self.opsafe_rid else ""


def _exclusion(corpus: Corpus, row: Row, v: Verdict, ov: Overrides) -> str:
    m = re.match(r"\s*`?(R-\d{4})`?\s*«(.*)»\s*$", v.ground)
    if not m:
        return "제외 근거 형식(`R-ID «인용»`) 아님"
    rid, quote = m.group(1), m.group(2)
    if ov.own_role(rid):
        return f"③ {ov.own_role(rid)} 규범 {rid} 는 제외 근거가 아니다"
    if rid in ov.scope:
        return f"③ 대상 목록 규범 {rid}({corpus.works.get(rid, {}).get('label', '')}) 는 제외 근거가 아니다"
    if rid in ov.opsafe:
        return f"③ {OPSAFE_ROLE} 대상 규범 {rid}({corpus.works.get(rid, {}).get('label', '')}) 는 제외 근거가 아니다"
    meta: "dict | None" = corpus.works.get(rid)
    if meta is None:
        return f"① 규범 {rid} 가 팩에 없다"
    key: str = corpus.key_of(meta["document"])
    bid, why = corpus.bind(key, quote)
    if bid is None:
        return f"① {why}"
    if rid not in corpus.blocks[bid]["works"]:
        return f"② {rid} 가 결속 블록({bid.rsplit('/', 1)[1]}) 의 규범이 아니다"
    opp_ok: bool = row.opp_bid is not None and rid in corpus.blocks[row.opp_bid]["works"]
    if meta.get("norm_kind") not in ALLOW_KINDS:
        if not opp_ok:
            return f"② {rid} 종류 {meta.get('norm_kind')} — 허용·예외도 리뷰어 반대 방향 규칙도 아니다"
        blocked: str = _opposite_blocked(corpus, row, ov)   # 반대 방향 경로로만 서는 제외
        if blocked:
            return f"② {blocked}"
    if set(corpus.blocks[bid]["works"]) & ov.scope:
        hit = corpus.phrase_hit(corpus.quote_sentences(key, bid, quote))
        if hit:
            return f"③ 인용이 든 문장에 적용 한정 어구 «{hit[0]}»"
    if row.bid == bid and (corpus.kinds(bid) & DUTY_KINDS) and (corpus.kinds(bid) & ALLOW_KINDS):
        mine = corpus.quote_span(key, bid, quote)
        theirs = corpus.quote_span(row.key, bid, row.quote)
        if any(a < d and c < b for a, b in mine for c, d in theirs):
            return "④ 혼합 블록 — 제외 인용이 위반 인용과 겹친다"
    return ""


def _false_positive(corpus: Corpus, row: Row, v: Verdict, ov: Overrides) -> str:
    m = re.search(r"«(.*)»", v.ground)
    if not m:
        return "오탐 근거 형식(`«요건 문구»`) 아님"
    quote: str = m.group(1)
    if row.bid is None:
        return "위반 행이 결속되지 않아 같은 블록 요건을 확인할 수 없다"
    if not corpus.quote_span(row.key, row.bid, quote):
        return "오탐 인용이 위반으로 인용된 그 블록에 없다(같은 절의 다른 문장 불가)"
    if set(corpus.blocks[row.bid]["works"]) & ov.scope:
        hit = corpus.phrase_hit(corpus.quote_sentences(row.key, row.bid, quote))
        if hit:
            return f"오탐 인용이 든 문장에 적용 한정 어구 «{hit[0]}»"
    return ""


def _opposite_blocked(corpus: Corpus, row: Row, ov: Overrides) -> str:
    """리뷰어 반대 방향 인용이 근거가 될 수 없는 사유(비면 근거 가능) — 사용자 판단·반대 방향 경로 제외 공통."""
    works: "set[str]" = set(corpus.blocks[row.opp_bid]["works"])  # type: ignore[index]
    for rid in (ov.scope_rid, ov.opsafe_rid):
        if rid in works:
            return f"반대 방향 규칙이 {ov.own_role(rid)} 규범 {rid} 다"
    if works & ov.opsafe:
        return f"반대 방향 규칙이 {OPSAFE_ROLE} 대상 규범 {sorted(works & ov.opsafe)[0]} 다"
    if works & ov.scope:
        hit = corpus.phrase_hit(corpus.quote_sentences(row.opp_key, row.opp_bid, row.opp_quote))
        if hit:
            return f"반대 방향 규칙 인용이 든 문장에 적용 한정 어구 «{hit[0]}» — 결정 18 이 가른 충돌"
    return ""


def _user_judgment(corpus: Corpus, row: Row, ov: Overrides) -> str:
    if not row.opposite:
        return "사용자 판단인데 리뷰어 행에 반대 방향 규칙이 없다"
    if row.opp_bid is None:
        return "반대 방향 규칙이 결속되지 않는다"
    return _opposite_blocked(corpus, row, ov)


def _separate(project: Path, bc: str, row: Row, v: Verdict, lane_paths: "Callable[[], dict[str, tuple[str, ...]]]") -> str:
    """다른 BC 몫 근거 — 실패 사유(비면 통과). 실패는 채택 재분류다.

    리뷰어 «바뀌는 것» 칸 `다른 BC 파일` ∧ 근거 `타 BC application/<다른 bc>/…:행` 실재 ∧ 그 자리가 이 레인이 고치는
    갈래(받는 쪽 어댑터 · 받는 쪽 시험 · 직접 import 자리 · HTTP 소비자 — `deps` 와 같은 계산) 밖.
    """
    if row.changes is None or "다른 BC 파일" not in row.changes:
        return f"리뷰어 «{CHANGE_COLUMN}» 칸에 `다른 BC 파일` 없음"
    if not any(t in v.ground for t in SEPARATE_TYPES):
        return f"근거 유형({' · '.join(SEPARATE_TYPES)}) 없음"
    evid = [l for l in (_parse_location(t) for t in _locations(v.ground)) if l]
    real = [(rel, a, b) for rel, a, b in evid
            if (m := re.match(r"application/([^/]+)/", os.path.normpath(rel).replace(os.sep, "/"))) and m.group(1) != bc
            and not os.path.isabs(rel) and _location_ok(project, (rel, a, b))]
    if not real:
        return "타 BC 근거 `application/<다른 bc>/…:행` 이 없거나 실재하지 않는다"
    owned: "dict[str, tuple[str, ...]]" = lane_paths()
    outside = [rel for rel, _a, _b in real if os.path.normpath(rel).replace(os.sep, "/") not in owned]
    if outside:
        return ""
    rel = os.path.normpath(real[0][0]).replace(os.sep, "/")
    return f"근거 `{rel}` 는 이 레인이 고치는 갈래({' · '.join(owned[rel])})다"


def _judge(corpus: Corpus, project: Path, bc: str, verdicts: "list[Verdict]", by_id: "dict[str, Row]",
           passed: "set[str]", ov: Overrides) -> "tuple[list[tuple[str, str, str]], list[tuple[str, str]]]":
    """판정 표 검사 → (red 목록 `(M|원 행, 종류, 사유)`, 재분류). 종류: 구조(M 중복·두 번·통과 밖) · 판정 없음 · 판정."""
    reds: "list[tuple[str, str, str]]" = []
    reclass: "list[tuple[str, str]]" = []
    seen_m: "set[str]" = set()
    covered: "dict[str, str]" = {}
    lane_cache: "dict[str, dict[str, tuple[str, ...]]]" = {}

    def lane_paths() -> "dict[str, tuple[str, ...]]":
        if "paths" not in lane_cache:
            lane_cache["paths"] = _lane_edit_paths(project, bc)
        return lane_cache["paths"]

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
            why = next((w for w in (_exclusion(corpus, r, v, ov) for r in row_list) if w), "")
        elif v.kind == "오탐":
            why = next((w for w in (_false_positive(corpus, r, v, ov) for r in row_list) if w), "")
        elif v.kind == "사용자 판단":
            why = next((w for w in (_user_judgment(corpus, r, ov) for r in row_list) if w), "")
        elif v.kind == "병합":
            if v.merge_to.startswith("M"):
                if kinds.get(v.merge_to) != "채택":
                    why = f"병합 대상 {v.merge_to} 이 채택 항목이 아니다"
            elif not all(re.search(rf"\b{re.escape(v.merge_to)}\b", r.same_c) for r in row_list):
                why = f"리뷰어가 «{v.merge_to} 과 같음»을 적지 않은 행의 M→C 병합"
        elif v.kind == OTHER_BC:
            fail = next((w for w in (_separate(project, bc, r, v, lane_paths) for r in row_list) if w), "")
            if fail:
                reclass.append((v.mid, f"{OTHER_BC} → 채택({fail})"))
                v.kind = "채택"
                kinds[v.mid] = "채택"
        if why:
            reds.append((v.mid, "판정", f"{v.kind} — {why}"))
    return reds, reclass


def _finalize_verdicts(verdicts: "list[Verdict]", reds: "list[tuple[str, str, str]]", passed: "set[str]",
                       reclass: "list[tuple[str, str]]") -> "list[Verdict]":
    """`--final` — 남은 red 판정 행과 판정 없는 통과 행을 채택으로 기록한다(구조 red 는 기록 정리)."""
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
        if v.kind == "병합" and v.merge_to.startswith("M") and v.merge_to not in adopted_m:
            reclass.append((v.mid, f"병합 대상 {v.merge_to} 이 확정 기록의 채택 항목이 아니다 → 채택"))
            v.kind, v.merge_to = "채택", ""
    return out


def cmd_check_verdict(corpus: Corpus, project: Path, audit: Path, feedback: "Path | None", final: bool) -> int:
    plan: Plan = Plan(audit)
    rows: "list[Row]" = _load_rows(audit, plan)
    _check_rows(corpus, project, plan.bc, rows)
    by_id: "dict[str, Row]" = {r.rid: r for r in rows}
    passed: "set[str]" = {r.rid for r in rows if r.status == "통과"}
    if plan.stage is None:
        raise ToolError(f"plan.md 에 `{STAGE_LINE}: {STAGE_PRE} <출처>` 줄이 없다 — R0′ 기록으로 `plan <bc> --out <audit 폴더> "
                        f"--stage <출처>` 를 다시 돌린다({OPSAFE_ROLE} 대상 · 조건부 대상을 근거에서 막는 결속)")
    ov: Overrides = Overrides(corpus.override_norms())
    verdicts: "list[Verdict]" = _load_verdicts(audit)
    reds, reclass = _judge(corpus, project, plan.bc, verdicts, by_id, passed, ov)
    kinds: "dict[str, str]" = {v.mid: v.kind for v in verdicts}
    prev_kinds, prev_origin = _previous(audit / "verdict-log.md")
    covered: "dict[str, str]" = {o: v.mid for v in verdicts for o in v.origin}
    for o, m in covered.items():
        if o in prev_origin and prev_origin[o] != m:
            reds.append((m, "판정", f"R3 재실행이 원 행 {o} 의 번호를 {prev_origin[o]} → {m} 로 바꿨다(기존 M 번호 유지)"))
    source: str = _source(feedback)
    # 대리 출처 — 출처 값 머리가 본인 직접·사용자 원문이 아니면 대리. 앞 확정 판이 있는데 출처 없이 재실행해도 대리로 본다.
    proxy: bool = _proxy_source(source) if source else bool(prev_kinds)
    if proxy:
        for m, before in prev_kinds.items():
            if before == "채택" and kinds.get(m) not in (None, "채택"):
                reds.append((m, "판정", f"대리 출처{'' if source else '(출처 없는 재실행)'}의 채택 축소(채택 → {kinds[m]}) — "
                                       "대리 출처는 채택 수를 줄일 수 없다"))
    if final and reds:
        verdicts = _finalize_verdicts(verdicts, reds, passed, reclass)
        reds = []
    counts: "dict[str, int]" = {k: 0 for k in ("채택", "사용자 판단", OTHER_BC, "제외", "오탐", "병합→C", "병합→M")}
    for v in verdicts:
        if v.label in counts:
            counts[v.label] += 1
    loose: "list[str]" = _change_warnings(rows)
    change_text: str = " · ".join(f"{CHANGE_SHORT[k]} {n}" for k, n in _change_counts(verdicts, by_id).items())
    mixed: "list[str]" = []
    for v in verdicts:
        if v.kind == "제외":
            for o in v.origin:
                r = by_id.get(o)
                if r and r.bid and (corpus.kinds(r.bid) & DUTY_KINDS) and (corpus.kinds(r.bid) & ALLOW_KINDS):
                    mixed.append(v.mid)
    q: int = sum(1 for r in rows if r.status == "인용 불일치")
    f: int = sum(1 for r in rows if r.status == "불편")
    code: int = EXIT_RED if reds else EXIT_OK
    summary: str = (f"요약: 채택 {counts['채택']} · 사용자 판단 {counts['사용자 판단']} · {OTHER_BC} {counts[OTHER_BC]} · "
                    f"제외 {counts['제외']} · 오탐 {counts['오탐']} · 병합→C {counts['병합→C']} · 병합→M {counts['병합→M']} · "
                    f"인용 불일치 {q} · 규칙 근거 없는 불편 {f} · 혼합 블록 제외 {len(set(mixed))} · "
                    f"{CHANGE_COLUMN} 동반 {change_text}{_loose_tail(loose)} · red {len(reds)}")
    log: "list[str]" = [f"## check-verdict {_now()} · 출처 {source or '없음'} · {'final · ' if final else ''}exit {code}", "",
                        "| M | 원 행 | 판정 |", "|---|---|---|"]
    log += [f"| {v.mid} | {' · '.join(v.origin)} | {v.label} |" for v in verdicts]
    log.append("")
    log += [f"- 재분류: {m} {w}" for m, w in reclass]
    log += [f"- red: {m} {w}" for m, _k, w in reds]
    if mixed:
        log.append(f"- 혼합 블록 제외: {', '.join(sorted(set(mixed)))}")
    log += [summary, ""]
    with (audit / "verdict-log.md").open("a", encoding="utf-8") as fh:
        fh.write("\n".join(log) + "\n")
    if code == EXIT_OK:
        _write_final(audit, verdicts, final)
    for m, _k, w in reds:
        print(f"  red: {m} {w}")
    for m, w in reclass:
        print(f"  재분류: {m} {w}")
    for w in loose:
        print(f"  경고: {w}")
    print(summary)
    return code


def _change_counts(verdicts: "list[Verdict]", by_id: "dict[str, Row]") -> "dict[str, int]":
    """채택 항목(그 항목으로 병합된 행 포함)마다 리뷰어 «바뀌는 것» 값 — 값별 항목 수(G0 배너 «바뀌는 것 동반»)."""
    out: "dict[str, int]" = {k: 0 for k in CHANGE_SHORT}
    for v in verdicts:
        if v.kind != "채택":
            continue
        origin: "list[str]" = list(v.origin) + [o for x in verdicts if x.kind == "병합" and x.merge_to == v.mid
                                               for o in x.origin]
        kinds: "set[str]" = set()
        for o in origin:
            row: "Row | None" = by_id.get(o)
            if row is not None and row.changes:
                kinds |= set(row.changes)
        for k in out:
            out[k] += int(k in kinds)
    return out


# ── residual ─────────────────────────────────────────────────────────────────

def _git(project: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(project), *args], capture_output=True, text=True, check=True).stdout


class Reduction:
    """`ⓐ 재상정` 절의 요지 축소 결정 줄 — 항목 하나의 남긴·뺀 요지 번호(명세 해소 판정 표의 `요지#`)."""

    def __init__(self, mid: str, kept: "list[int]", dropped: "list[int]", disposition: str, stamp: str,
                 line: str) -> None:
        self.mid: str = mid
        self.kept: "list[int]" = kept
        self.dropped: "list[int]" = dropped
        self.disposition: str = disposition
        self.stamp: str = stamp
        self.line: str = line


def _refs(segment: str) -> "list[int]":
    return sorted({int(x) for x in re.findall(r"#\s*(\d+)", segment)})


def _reduction(head: str, line: str, stamp: str) -> Reduction:
    """요지 축소 줄 정형 — `M<n> · 결정 = 요지 축소 · 남긴 요지 = #k… · 뺀 요지 = #j… → <처분> · 남김 근거 = … · 출처 = …`.

    정형이 아니면 실행 불능이다(남긴 요지를 모르면 residual 이 무엇을 확인할지 모른다 — fail-closed).
    """
    keys: "list[str]" = re.findall(r"\bM\d+\b", re.sub(r"\([^)]*\)", "", head))   # 괄호 안 = 병합 항목 표기
    where: str = f"재상정 {stamp or '(시각 없음)'} 요지 축소 줄"
    if len(keys) != 1:
        raise ToolError(f"{where}은 항목 하나(`M<n>`)여야 한다 — {line.strip()[:160]}")
    # 칸 값은 다음 칸 이름 앞까지다 — 번호 목록 안의 `·`(`#1·#3`·`#1 · #3`)를 칸 구분으로 읽지 않는다.
    nxt: str = r"(?=\s*·\s*(?:남긴 요지|뺀 요지|남김 근거|출처|사유)\s*=|$)"
    kept_m = re.search(r"남긴 요지\s*=\s*(.*?)" + nxt, line)
    drop_m = re.search(r"뺀 요지\s*=\s*([^→]*?)\s*→\s*(.*?)" + nxt, line)
    basis_m = re.search(r"남김 근거\s*=\s*(.*?)" + nxt, line)
    kept: "list[int]" = _refs(kept_m.group(1)) if kept_m else []
    dropped: "list[int]" = _refs(drop_m.group(1)) if drop_m else []
    disposition: str = drop_m.group(2).strip() if drop_m else ""
    basis: str = basis_m.group(1).strip() if basis_m else ""
    problems: "list[str]" = []
    if not kept:
        problems.append("`남긴 요지 = #<k>` 없음")
    if not dropped:
        problems.append("`뺀 요지 = #<j> → <처분>` 없음")
    elif not disposition.startswith(RECONSIDER_TOKENS) or disposition.startswith(REDUCE_TOKEN):
        problems.append(f"뺀 요지 처분 `{disposition}` 이 닫힌 어휘({' · '.join(RECONSIDER_TOKENS[:-1])}) 밖")
    if set(kept) & set(dropped):
        problems.append(f"남긴·뺀 요지 번호 겹침 {sorted(set(kept) & set(dropped))}")
    if not basis.startswith(REDUCE_BASIS):
        problems.append(f"`남김 근거 = {' | '.join(REDUCE_BASIS)}` 아님")
    if problems:
        raise ToolError(f"{where}({keys[0]})이 정형이 아니다 — {' · '.join(problems)}: {line.strip()[:160]}")
    return Reduction(keys[0], kept, dropped, disposition, stamp, line.strip())


class DecisionLine:
    """`refactor-scope.md` 결정 줄 하나 — 줄 번호 · 절 머리(재상정 절이면 그 제목) · 키 · 결정 칸 첫 낱말 · 원문."""

    def __init__(self, no: int, heading: str, reconsider: bool, head: str, token: str, text: str,
                 decision: bool = True) -> None:
        self.no: int = no
        self.heading: str = heading
        self.reconsider: bool = reconsider
        bare: str = re.sub(r"\([^)]*\)", "", head)          # `M1(+M44)` 의 괄호 = 병합 항목 표기(줄의 키가 아니다)
        self.mkeys: "set[str]" = set(re.findall(r"\bM\d+\b", bare))
        self.ckeys: "set[str]" = set(re.findall(r"\bC\d+\b", bare))
        self.token: str = token
        self.text: str = text
        self.decision: bool = decision                       # 거짓 = `결정 =` 없는 줄(사용자 판단 줄 등)의 상시 답 출처


def _scope(folder: Path) -> "tuple[str, set[str], set[str], dict[str, Reduction], list[DecisionLine]]":
    """(audit 시각, 이번 실행 ⓐ M 키, 재상정으로 뺀 키, 요지 축소, 결정 줄) — `refactor-scope.md` 의 앞 실행 절 앞까지.

    재상정 절의 `M<n>` 결정 줄은 첫 낱말이 닫힌 어휘여야 한다(밖이면 실행 불능). `요지` 줄은 빼지 않고
    요지 축소로 싣는다(같은 항목의 뒤 줄이 이긴다) — 같은 항목에 전체 제외 줄이 있으면 제외가 이긴다.
    재상정 절 제목보다 깊은 제목(하위 제목)은 절을 끊지 않는다.
    G0 확정 판정(`verdict-final.md`)의 병합 항목은 대상 항목을 따르므로 결정 줄 표기와 무관하게 ⓐ 키에서 뺀다 — 대상
    `M<n>` 이 ⓐ 키이거나 대상 `C<n>` 이 ⓐ 결정 줄에 있을 때만(확정 표가 없으면 실행 불능).
    """
    text: str = re.split(r"(?m)^#+\s*앞 실행", _read(folder / "refactor-scope.md"))[0]
    m = re.search(r"^\s*실행 · G0 승인 \S+ · 모드 리팩토링 · audit (\S+)", text, re.M)
    if not m:
        raise ToolError("refactor-scope.md 에 리팩토링 실행 줄(`실행 · G0 승인 <값> · 모드 리팩토링 · audit <시각>`)이 없다")
    adopted: "set[str]" = set()
    adopted_c: "set[str]" = set()
    removed: "set[str]" = set()
    reductions: "dict[str, Reduction]" = {}
    lines: "list[DecisionLine]" = []
    in_reconsider: bool = False
    level: int = 0
    heading: str = ""
    stamp: str = ""
    for no, ln in enumerate(text.splitlines(), 1):
        hm = re.match(r"^(#+)\s", ln)
        if hm:
            if in_reconsider and len(hm.group(1)) > level:
                continue                                   # 재상정 절 안의 하위 제목
            in_reconsider = "ⓐ 재상정" in ln
            level, heading = len(hm.group(1)), ln.strip() if in_reconsider else ""
            sm = re.search(r"ⓐ 재상정\s+(\S+)", ln)
            stamp = sm.group(1) if sm else ""
            continue
        # 결정 값이 빈 자리표시(`결정 = · …` — 답을 받기 전의 STOP 기록)면 결정이 아니다.
        dm = re.match(r"^\s*[-*]?\s*(.+?)\s*·\s*결정\s*=\s*([^\s·—-]\S*)", ln)
        if not dm:
            if _standing_mention(ln):
                lines.append(DecisionLine(no, heading, in_reconsider, ln, "", ln.strip(), decision=False))
            continue
        lines.append(DecisionLine(no, heading, in_reconsider, dm.group(1), dm.group(2), ln.strip()))
        keys: "set[str]" = set(re.findall(r"\bM\d+\b", dm.group(1)))
        token: str = dm.group(2)
        if in_reconsider:
            if not keys:
                continue
            if not token.startswith(RECONSIDER_TOKENS):
                raise ToolError(f"재상정 {stamp or '(시각 없음)'} 결정 칸 첫 낱말 `{token}` 이 닫힌 어휘"
                                f"({' · '.join(RECONSIDER_TOKENS)}) 밖이다 — {ln.strip()[:160]}")
            if token.startswith(REDUCE_TOKEN):
                red: Reduction = _reduction(dm.group(1), ln, stamp)
                reductions[red.mid] = red
            else:
                removed |= keys
        elif token.startswith("ⓐ") and not token.startswith("ⓐ′"):
            adopted |= keys
            adopted_c |= set(re.findall(r"\bC\d+\b", re.sub(r"\([^)]*\)", "", dm.group(1))))   # 괄호 안 C 는 ⓐ 가 아니다
    merged: "set[str]" = {v.mid for v in _final_verdicts(folder / "audit" / m.group(1)).values() if v.kind == "병합"
                          and v.merge_to in (adopted_c if v.merge_to.startswith("C") else adopted)}
    return m.group(1), adopted - merged, removed, reductions, lines


# ── resolution(명세 «슬라이스 0 해소 판정» 표) ──────────────────────────────

class ResolutionRow:
    """판정 표 한 행 — `M<n> | 요지# | 요지 | 판정 | 불가 범주 | 막는 것 | 처방 앵커 | 되돌리지 않는 이유`."""

    def __init__(self, mid: str, cells: "list[str]") -> None:
        self.mid: str = mid
        self.no_raw: str = cells[1].strip("`*# ")
        self.no: int = int(self.no_raw) if self.no_raw.isdigit() else -1
        self.gist: str = cells[2]
        self.verdict: str = cells[3].strip("`* ")
        self.category: str = cells[4].strip("`* ")
        self.blocker: str = cells[5]
        self.anchor: str = cells[6]
        self.why: str = cells[7]


def _resolution_table(spec: Path) -> "tuple[list[ResolutionRow], str, list[str]]":
    """(판정 표 행, 표 밖 명세 본문(정규화), 형식 red) — `슬라이스 0 해소 판정` 제목 아래 표."""
    lines: "list[str]" = _read(spec).split("\n")
    heads: "list[tuple[int, int]]" = []
    all_heads: "list[tuple[int, int]]" = []
    fence: "str | None" = None
    for i, ln in enumerate(lines):
        fm = _FENCE.match(ln)
        if fm:
            fence = None if fence is not None and fm.group(1)[0] == fence[0] else (fence or fm.group(1))
            continue
        if fence is not None:
            continue
        hm = _HEADING.match(ln)
        if hm:
            all_heads.append((i, len(hm.group(1))))
            rm = _RESOLUTION_HEADING.match(ln.replace("*", "").replace("`", ""))   # 제목 강조 표기는 벗겨 대조한다
            if rm:
                heads.append((i, len(rm.group(1))))
    reds: "list[str]" = []
    if len(heads) != 1:
        reds.append("명세에 `슬라이스 0 해소 판정` 제목이 없다(기대 형태 `## [번호] 슬라이스 0 해소 판정`)" if not heads
                    else f"`슬라이스 0 해소 판정` 제목이 {len(heads)}개다(하나여야 한다)")
        return [], normalize("\n".join(lines)), reds
    start, level = heads[0]
    end: int = next((i for i, lv in all_heads if i > start and lv <= level), len(lines))
    rows: "list[ResolutionRow]" = []
    table_lines: "set[int]" = set()
    for i in range(start + 1, end):
        s: str = lines[i].strip()
        if not s.startswith("|"):
            continue
        table_lines.add(i)
        if re.fullmatch(r"\|[\s:|-]*\|", s):
            continue
        cells: "list[str]" = _cells(s)
        mm = re.match(r"(M\d+)(?!\d)", cells[0].strip("`* "))     # `M1(+M44)` 의 괄호 = 병합 항목 표기
        if not mm:
            continue                                   # 머리 행
        if len(cells) < RESOLUTION_COLUMNS:
            reds.append(f"판정 표 행 칸 부족({len(cells)} < {RESOLUTION_COLUMNS}): {s[:80]}")
            continue
        rows.append(ResolutionRow(mm.group(1), cells))
    if not rows and not reds:
        reds.append("`슬라이스 0 해소 판정` 표에 행이 없다")
    body: str = normalize("\n".join(ln for i, ln in enumerate(lines) if i not in table_lines))
    return rows, body, reds


def _item_class(rows: "list[ResolutionRow]") -> str:
    """항목 판정 — 요지가 모두 «정리»(해소 ∪ 변경)면 해소 · 모두 불가면 불가 · 그 밖은 부분."""
    kinds: "set[str]" = {r.verdict for r in rows}
    if kinds <= set(CLEANED_VERDICTS):
        return "해소"
    if kinds == {"불가"}:
        return "불가"
    return "부분"


def _origins(verdicts: "dict[str, Verdict]", mid: str) -> "list[tuple[str, str]]":
    """M → (원 행, 병합해 온 M 또는 "") — 채택 행과 그 항목으로 병합된 행 전부."""
    v = verdicts.get(mid)
    if v is None:
        raise ToolError(f"ⓐ 항목 {mid} 이 {VERDICT_FINAL} 에 없다")
    merged = [x for x in verdicts.values() if x.kind == "병합" and x.merge_to == mid]
    return [(o, "") for o in v.origin] + [(o, x.mid) for x in merged for o in x.origin]


def _m_order(key: str) -> int:
    return int(key[1:])


def _no_standing(lines: "list[DecisionLine]", where: str) -> None:
    """상시 답은 걷혔다 — 이번 실행 몫(`# 앞 실행` 절 앞)에 `출처 = 상시 답` 줄이 있으면 실행 불능."""
    hit: "DecisionLine | None" = next((dl for dl in lines if _standing_mention(dl.text)), None)
    if hit is not None:
        raise ToolError(f"{where}: refactor-scope.md 이번 실행 몫 {hit.no}행에 옛 `출처 = 상시 답` 줄이 있다 — 상시 답은 걷혔다"
                        f"(G1 재상정은 사용자 직접 답만) · 그 기록은 «앞 실행» 절에만 남긴다: {hit.text[:120]}")


def _v_refs(cell: str) -> "list[str] | None":
    """변경 행 막는 것 칸 `V<n>[ · V<m>]` → V 목록(형식 밖이면 None)."""
    toks: "list[str]" = [t for t in re.split(r"\s*[,·]\s*|\s+", re.sub(r"[*`]", "", cell).strip()) if t]
    if not toks or any(not re.fullmatch(r"V\d+", t) for t in toks) or len(set(toks)) != len(toks):
        return None
    return toks


def _opposite_evidence(cell: str, corpus_fn: "Callable[[], Corpus]") -> "tuple[bool, str]":
    """막는 것 칸의 인용 밖 반대 규칙 증거 — (증거 칸이 있는가, 실패 사유(비면 통과)).

    판형: `<파일:행> — <한 구> · 반대 규칙 R-<n> «원문 인용 20~60자»[ · 검사기 <이름> red] · 함께 지킬 배치 없음 — <한 구>`.
    R-ID 팩 실재 · 두 Override(적용 범위 · 운영 전 예외)의 규범 · 대상 · 조건부 대상 아님 · 인용이 그 규범 블록에 결속(R3
    제외 근거와 같은 `corpus.bind`).
    """
    if "반대 규칙" not in cell:
        return False, ""
    m = re.search(r"·\s*반대 규칙\s+`?(R-\d{4})`?\s*«([^«»]*)»", cell)
    if not m:
        return True, "증거 칸 `· 반대 규칙 R-<n> «원문 인용»` 판형이 아니다"
    rid, quote = m.group(1), m.group(2).strip()
    if not OPP_QUOTE_MIN <= len(quote) <= OPP_QUOTE_MAX:
        return True, f"반대 규칙 원문 인용이 {len(quote)}자다({OPP_QUOTE_MIN}~{OPP_QUOTE_MAX}자)"
    tail: str = cell[m.end():]
    if "검사기" in tail and not re.search(r"·\s*검사기\s+\S+\s+red\b", tail):
        return True, "`· 검사기 <이름> red` 판형이 아니다"
    nm = re.search(r"·\s*함께 지킬 배치 없음\s*—\s*(.*)$", tail)
    if not nm or nm.group(1).strip() in _EMPTY:
        return True, "`· 함께 지킬 배치 없음 — <한 구>` 가 없다"
    corpus: Corpus = corpus_fn()
    meta: "dict | None" = corpus.works.get(rid)
    if meta is None:
        return True, f"반대 규칙 {rid} 가 팩에 없다"
    roles, blocked = corpus.blocked_norms()
    if rid in blocked:
        role: str = next(r for r, (oid, t) in roles.items() if rid == oid or rid in t)
        return True, f"반대 규칙 {rid} 가 {role} Override 의 규범·대상이다(반대 방향 근거가 될 수 없다)"
    bid, why = corpus.bind(corpus.key_of(meta["document"]), quote)
    if bid is None:
        return True, f"반대 규칙 {rid} 인용 — {why}"
    if rid not in corpus.blocks[bid]["works"]:
        return True, f"반대 규칙 인용의 결속 블록({bid.rsplit('/', 1)[1]})이 {rid} 의 블록이 아니다"
    return True, ""


def _cite_binds(corpus: Corpus, cell: str) -> bool:
    """`<문서 키> §<절> «인용»` 이 그 절의 한 규범 블록에 결속되나(check 의 반대 방향 결속과 같은 길)."""
    cite = _cite(cell)
    if cite is None:
        return False
    key: str = corpus.canon_key(cite[0])
    if not corpus.path_of(key).is_file():
        return False
    rng = corpus.doc(key).section(cite[1])
    return rng is not None and corpus.bind(key, cite[2], rng)[0] is not None


def _resolution_reds(project: Path, folder: Path, by_m: "dict[str, list[ResolutionRow]]", adopted: "set[str]",
                     removed: "set[str]", body: str, vids: "set[str]", corpus_fn: "Callable[[], Corpus]",
                     cited: "Callable[[str], bool]") -> "tuple[list[str], dict[str, str], int]":
    """판정 표 행 검사 → (red, 항목 판정, 인용 밖 반대 규칙 수). 막는 것의 맨 `refactor-scope.md:<행>` 은 산출물 폴더의 그 파일이다."""
    scope_rel: str = os.path.relpath(folder.resolve() / "refactor-scope.md", project)
    reds: "list[str]" = []
    classes: "dict[str, str]" = {}
    outside: int = 0
    for mid in sorted(set(by_m) & adopted, key=_m_order):
        rs: "list[ResolutionRow]" = by_m[mid]
        nos: "list[int]" = [r.no for r in rs]
        if any(n < 1 for n in nos) or len(set(nos)) != len(nos):
            reds.append(f"{mid} 요지# 가 1 이상 정수가 아니거나 항목 안에서 겹친다: {[r.no_raw for r in rs]}")
        bad = [r for r in rs if r.verdict not in RESOLUTION_VERDICTS]
        for r in bad:
            reds.append(f"{mid} #{r.no_raw} 판정 `{r.verdict}` 이 {' · '.join(f'`{v}`' for v in RESOLUTION_VERDICTS)} 밖")
        if bad:
            continue
        cls: str = _item_class(rs)
        classes[mid] = cls
        for r in rs:
            if r.verdict == "불가":
                if r.category not in RESOLUTION_CATEGORIES:
                    reds.append(f"{mid} #{r.no_raw} 불가 범주 `{r.category}` 가 닫힌 목록({' · '.join(RESOLUTION_CATEGORIES)}) 밖")
                elif r.category == REMOVED_CATEGORY and mid not in removed:
                    reds.append(f"{mid} #{r.no_raw} 범주 `{REMOVED_CATEGORY}` 인데 재상정 절에 이 항목의 전체 제외 줄이 없다")
                where, dash, phrase = r.blocker.partition("—")
                locs = [_parse_location(t) for t in _locations(where)]
                if not locs or any(loc is None for loc in locs):
                    reds.append(f"{mid} #{r.no_raw} 막는 것이 `파일:행 — 한 구` 형식이 아니다: `{r.blocker}`")
                else:
                    locs = [(scope_rel, l[1], l[2]) if l[0] == "refactor-scope.md" else l for l in locs]  # type: ignore[index]
                    missing = [f"{l[0]}:{l[1]}" for l in locs if not _location_ok(project, l)]  # type: ignore[index,arg-type]
                    if missing:
                        reds.append(f"{mid} #{r.no_raw} 막는 것이 대상 프로젝트에 없다: {', '.join(missing[:3])}")
                    if not dash or phrase.strip() in _EMPTY:
                        reds.append(f"{mid} #{r.no_raw} 막는 것에 «— 무엇이 바뀌어야 하는지 한 구»가 없다")
                has_evidence, why = _opposite_evidence(r.blocker, corpus_fn)
                if has_evidence and r.category != OPPOSITE_CATEGORY:
                    reds.append(f"{mid} #{r.no_raw} 반대 규칙 증거 칸은 범주 `{OPPOSITE_CATEGORY}` 에만 쓴다(지금 `{r.category}`)")
                elif has_evidence and why:
                    reds.append(f"{mid} #{r.no_raw} 인용 밖 반대 규칙 — {why}")
                elif has_evidence:
                    outside += 1
                elif r.category == OPPOSITE_CATEGORY and not cited(mid):
                    reds.append(f"{mid} #{r.no_raw} `{OPPOSITE_CATEGORY}` 불가 행인데 원 행 · verdict 가 인용한 반대 방향 규칙이 없다 — "
                                f"인용 밖 규칙이면 막는 것에 `· 반대 규칙 R-<n> «원문 인용»` · (있으면) `· 검사기 <이름> red` · "
                                f"`· 함께 지킬 배치 없음 — <한 구>` 를 잇는다")
                if r.anchor.strip() not in _EMPTY or r.why.strip() not in _EMPTY:
                    reds.append(f"{mid} #{r.no_raw} 불가 행의 처방 앵커·되돌리지 않는 이유는 `—` 로 둔다")
                continue
            if r.anchor.strip() in _EMPTY:
                reds.append(f"{mid} #{r.no_raw} {r.verdict} 행에 처방 앵커가 없다")
            elif len(normalize(r.anchor)) < ANCHOR_MIN:
                reds.append(f"{mid} #{r.no_raw} 처방 앵커가 너무 짧다(정규화 {ANCHOR_MIN}자 이상): «{r.anchor}»")
            elif normalize(r.anchor) not in body:
                reds.append(f"{mid} #{r.no_raw} 처방 앵커 원문이 표 밖 명세 본문에 없다: «{r.anchor[:60]}»")
            if cls == "부분" and r.why.strip() in _EMPTY:
                reds.append(f"{mid} #{r.no_raw} 부분 항목의 {r.verdict} 행에 «되돌리지 않는 이유»가 없다")
            if r.verdict == CHANGE_VERDICT:
                refs: "list[str] | None" = _v_refs(r.blocker)
                if r.category.strip() not in _EMPTY:
                    reds.append(f"{mid} #{r.no_raw} 변경 행의 불가 범주는 `—` 로 둔다")
                if refs is None:
                    reds.append(f"{mid} #{r.no_raw} 변경 행의 막는 것 칸이 `V<n>[ · V<m>]` 가 아니다: `{r.blocker}`")
                else:
                    gone = [v for v in refs if v not in vids]
                    if gone:
                        reds.append(f"{mid} #{r.no_raw} 변경 행의 {' · '.join(gone)} 이 `바뀌는 것 목록` 에 없다")
            elif r.category.strip() not in _EMPTY or r.blocker.strip() not in _EMPTY:
                reds.append(f"{mid} #{r.no_raw} 해소 행의 불가 범주·막는 것은 `—` 로 둔다")
    return reds, classes, outside


def _gate_reds(by_m: "dict[str, list[ResolutionRow]]", classes: "dict[str, str]", removed: "set[str]",
               reductions: "dict[str, Reduction]") -> "list[str]":
    """`--gate` — 부분·불가의 재상정 결정 줄 · 요지 축소 번호 · 전체 제외 항목의 표(«정리» = 해소 ∪ 변경)."""
    reds: "list[str]" = []
    for mid, cls in sorted(classes.items(), key=lambda kv: _m_order(kv[0])):
        red: "Reduction | None" = reductions.get(mid)
        if mid in removed:
            if any(r.verdict in CLEANED_VERDICTS for r in by_m[mid]):
                reds.append(f"{mid} 전체 제외 항목의 판정 표에 정리(해소·변경) 요지가 남아 있다 — 부분만 뺀 답이면 결정 줄을 요지 "
                            f"축소 정형으로, 전체를 뺀 답이면 표의 행을 모두 불가(정리이던 요지는 `{REMOVED_CATEGORY}`)로 고친다")
            continue
        solved: "list[int]" = sorted(r.no for r in by_m[mid] if r.verdict in CLEANED_VERDICTS)
        blocked: "list[int]" = sorted(r.no for r in by_m[mid] if r.verdict == "불가")
        if cls == "불가":
            reds.append(f"{mid} 불가 항목에 " + ("요지 축소 줄이 걸렸다(남길 요지가 없다)" if red
                                                 else "재상정 결정 줄이 없다"))
        elif cls == "부분":
            if red is None:
                reds.append(f"{mid} 부분 항목에 재상정 결정 줄(요지 축소 · 뺀 요지 처분)이 없다")
            elif red.kept != solved or red.dropped != blocked:
                reds.append(f"{mid} 요지 축소 줄 번호가 표와 다르다 — 줄 남긴 {red.kept} · 뺀 {red.dropped} / "
                            f"표 정리 {solved} · 불가 {blocked}")
        elif red is not None:
            reds.append(f"{mid} 표가 해소인데 요지 축소 줄이 있다 — 표를 요지 축소 결정대로 고친다(G1′)")
    for mid in sorted(set(reductions) - set(by_m) - removed, key=_m_order):
        reds.append(f"{mid} 요지 축소 줄 항목이 판정 표에 없다")
    return reds


def cmd_resolution(project: Path, folder: Path, gate: bool, corpus_fn: "Callable[[], Corpus]") -> int:
    audit_ts, adopted, removed, reductions, lines = _scope(folder)
    if gate:
        _no_standing(lines, "resolution --gate")
    audit: Path = folder / "audit" / audit_ts
    verdicts: "dict[str, Verdict]" = _final_verdicts(audit)
    rows: "dict[str, Row]" = {r.rid: r for r in _load_rows(audit, Plan(audit))}
    spec: Path = folder / "design-spec.md"
    table, body, reds = _resolution_table(spec)
    vids: "set[str]" = {v.vid for v in _v_section(_read(spec))[0]}
    by_m: "dict[str, list[ResolutionRow]]" = {}
    for r in table:
        by_m.setdefault(r.mid, []).append(r)
    items: "set[str]" = adopted - removed
    for mid in sorted(items - set(by_m), key=_m_order):
        reds.append(f"{mid} 판정 없음 — 범위 안 ⓐ 항목에 판정 표 행이 없다")
    for mid in sorted(set(by_m) - adopted, key=_m_order):
        reds.append(f"{mid} 범위 밖 — G0 ⓐ 항목이 아니다(병합 항목은 병합 대상 `M<n>` 의 요지로 적는다)")
    cache: "dict[str, bool]" = {}

    def cited(mid: str) -> bool:
        """그 항목의 원 행(병합 행 포함) · verdict 근거 가운데 결속되는 반대 방향 규칙 인용이 있나(설계 :249 · :253)."""
        if mid not in cache:
            cells: "list[str]" = [rows[o].opposite for o, _v in _origins(verdicts, mid) if o in rows]
            cells.append(verdicts[mid].ground if mid in verdicts else "")
            cache[mid] = any(_cite_binds(corpus_fn(), c) for c in cells if c and _cite(c))
        return cache[mid]

    row_reds, classes, outside = _resolution_reds(project, folder, by_m, adopted, removed, body, vids, corpus_fn, cited)
    reds += row_reds
    if gate:
        reds += _gate_reds(by_m, classes, removed, reductions)
    counts: "dict[str, int]" = {k: sum(1 for c in classes.values() if c == k) for k in ("해소", "부분", "불가")}
    changed: int = sum(1 for mid in classes for r in by_m[mid] if r.verdict == CHANGE_VERDICT)
    lens_of: "dict[str, list[str]]" = {}
    for mid in sorted(set(by_m) & items, key=_m_order):
        for lens in sorted({rows[o].lens for o, _v in _origins(verdicts, mid) if o in rows}):
            lens_of.setdefault(lens, []).append(mid)
    for lens in (l for l in LENSES if l in lens_of):
        print(f"  렌즈 {lens}: {' · '.join(lens_of[lens])}")
    for w in reds:
        print(f"  red: {w}")
    print(f"요약: 해소 판정: 해소 {counts['해소']} · 부분 {counts['부분']} · 불가 {counts['불가']} · 항목 {len(classes)} · "
          f"요지 행 {len(table)} · 변경 요지 {changed} · 인용 밖 반대 규칙 {outside} · red {len(reds)}{' · gate' if gate else ''}")
    return EXIT_RED if reds else EXIT_OK


MAP_KINDS: "tuple[str, ...]" = ("code", "follow", "change")   # 대응표를 갖는 창(0C · 0F · 변경 슬라이스)


def _window_no(path: Path) -> "tuple[int, str]":
    m = re.match(r"w(\d+)-", path.name)
    return (int(m.group(1)) if m else -1, path.name)


def _map_items(folder: Path, run_value: str) -> "dict[str, str]":
    """0C · 0F · 변경 창 close 기록의 대응 원소(옛 경로 → 새 경로) — 창마다 마지막 판정."""
    run_dir: Path = folder / "behavior" / re.sub(r"[^\w.-]", "_", run_value)
    mapping: "dict[str, str]" = {}
    closes: "list[Path]" = sorted(run_dir.glob("w*-close.json"), key=_window_no) if run_dir.is_dir() else []
    for close in closes:                                   # 창 차례(w2 < w10) — 뒤 창의 대응이 이긴다
        opened: Path = close.with_name(close.name.replace("-close", "-open"))
        if opened.is_file() and json.loads(opened.read_text(encoding="utf-8")).get("kind") not in MAP_KINDS:
            continue
        records: "list[dict]" = json.loads(close.read_text(encoding="utf-8"))
        items: dict = (records[-1].get("map_items") or {}) if records else {}
        for part in ("fm", "pairs", "dirs"):
            mapping.update(items.get(part) or {})
    return mapping


def _moved(path: str, mapping: "dict[str, str]") -> str:
    if path in mapping:
        return mapping[path]
    for old in sorted(mapping, key=len, reverse=True):
        if path.startswith(old.rstrip("/") + "/"):
            return mapping[old] + path[len(old.rstrip("/")):]
    return path


def _changed_since(project: Path, anchor: str) -> "set[str]":
    """앵커 이후 바뀐 경로(작업 트리 포함) — 이동은 옛·새 경로 둘 다(`--no-renames` · behavior_guard 와 같다)."""
    changed: "set[str]" = {p for p in _git(project, "diff", "--no-renames", "--name-only", anchor).splitlines() if p}
    return changed | {p for p in _git(project, "ls-files", "--others", "--exclude-standard").splitlines() if p}


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
    while (base / (stamp if k == 1 else f"{stamp}-{k}")).exists():   # 같은 분의 재실행 — 앞 판을 덮지 않는다
        k += 1
    stamp = stamp if k == 1 else f"{stamp}-{k}"
    return stamp, base / stamp


def _stamp_key(name: str) -> "tuple[int, ...]":
    """residual 시각 폴더 순서 — `YYYYmmdd-HHMM[-k]` 를 수로(같은 분의 `-10` 이 `-9` 뒤에 오게)."""
    parts: "list[str]" = name.split("-")
    return tuple(int(x) if x.isdigit() else -1 for x in parts) + ((1,) if len(parts) == 2 else ())


def _carried(folder: Path, stamp: str) -> "tuple[str, dict[str, dict[str, str | None]]]":
    """직전(이 시각보다 앞) 확정 판의 해소 항목과 그때의 파일 지문 — 재측정 이월 재료."""
    base: Path = folder / "residual"
    done: "list[str]" = sorted((d.name for d in base.iterdir() if d.is_dir() and _stamp_key(d.name) < _stamp_key(stamp)
                                and (d / "result.json").is_file()), key=_stamp_key) if base.is_dir() else []
    if not done:
        return "", {}
    data: dict = json.loads((base / done[-1] / "result.json").read_text(encoding="utf-8"))
    return done[-1], data.get("solved", {})


def _reduction_notes(folder: Path, reduced: "dict[str, Reduction]") -> "dict[str, str]":
    """요지 축소 항목 → 묶음 줄(남긴·뺀 요지 원문은 명세 해소 판정 표) — 번호가 표에 없으면 실행 불능."""
    if not reduced:
        return {}
    table, _body, reds = _resolution_table(folder / "design-spec.md")
    gist: "dict[tuple[str, int], str]" = {(r.mid, r.no): r.gist for r in table}
    notes: "dict[str, str]" = {}
    for mid, red in reduced.items():
        missing = [n for n in red.kept + red.dropped if (mid, n) not in gist]
        if missing:
            why: str = f" · 표 형식: {reds[0]}" if reds else ""
            raise ToolError(f"요지 축소 {mid} 의 요지 #{', #'.join(map(str, missing))} 이 명세 해소 판정 표에 없다{why}")
        kept: str = " · ".join(f"#{n} «{gist[(mid, n)]}»" for n in red.kept)
        dropped: str = " · ".join(f"#{n} «{gist[(mid, n)]}»" for n in red.dropped)
        notes[mid] = (f"- 요지 축소(재상정 {red.stamp}): 남긴 요지 {kept} — 이 요지만 확인한다 · "
                      f"뺀 요지 {dropped} → {red.disposition}")
    return notes


def cmd_residual(project: Path, folder: Path, candidates: "Path | None", finalize: "str | None") -> int:
    audit_ts, adopted, removed, reductions, lines = _scope(folder)
    _no_standing(lines, "residual")
    items: "set[str]" = adopted - removed
    reduced: "dict[str, Reduction]" = {m: r for m, r in reductions.items() if m in items}
    notes: "dict[str, str]" = _reduction_notes(folder, reduced)
    red_tail: str = f" · 요지 축소 {len(reduced)}" if reduced else ""
    audit: Path = folder / "audit" / audit_ts
    verdicts: "dict[str, Verdict]" = _final_verdicts(audit)
    plan: Plan = Plan(audit)
    rows: "dict[str, Row]" = {r.rid: r for r in _load_rows(audit, plan)}
    run_value: str = re.search(r"실행 · G0 승인 (\S+)", _read(folder / "refactor-scope.md")).group(1)  # type: ignore[union-attr]
    anchor: str = _read(folder / "build_anchor").strip()
    changed: "set[str]" = _changed_since(project, anchor)
    mapping: "dict[str, str]" = _map_items(folder, run_value)
    cand_lines: "list[str]" = _read(candidates).splitlines() if candidates else []
    stamp, out_dir = _stamp_dir(folder, finalize)
    prev_stamp, prev_solved = _carried(folder, stamp)
    floor: "dict[str, str]" = {}
    carried: "list[str]" = []
    to_review: "dict[str, list[str]]" = {}
    origins: "dict[str, list[tuple[str, str]]]" = {}      # M → (원 행, 병합해 온 M 또는 "")
    watched: "dict[str, list[str]]" = {}                    # M → 지문을 잴 경로(항목 파일 · 대응 새 경로)
    for mid in sorted(items, key=lambda k: int(k[1:])):
        origins[mid] = _origins(verdicts, mid)
        v: Verdict = verdicts[mid]
        origin: "list[str]" = [o for o, _m in origins[mid]]
        files: "list[str]" = sorted({os.path.normpath(l[0]) for o in origin if o in rows
                                     for l in (_parse_location(t) for t in _locations(rows[o].where)) if l})
        watched[mid] = sorted(set(files) | {_moved(f, mapping) for f in files})
        before: "dict[str, str | None] | None" = prev_solved.get(mid)
        if before is not None and before == {p: _file_sha(project, p) for p in before}:
            carried.append(mid)                  # 직전 확정 판의 해소 — 그 뒤 항목 파일·대응 경로가 그대로면 유지
            continue
        marks: "set[str]" = set(re.findall(r"ⓓ#\d+", " ".join([v.ground, v.where] + [rows[o].gist for o in origin if o in rows])))
        if files and not any(f in changed for f in files):
            floor[mid] = "파일 무변(build_anchor..작업 트리)"
            continue
        if marks:
            if candidates is None:
                raise ToolError(f"{mid} 이 ⓓ 겹침 항목({', '.join(sorted(marks))})이다 — --candidates <G2 검사기 출력> 필요")
            moved = {_moved(f, mapping) for f in files}
            still = [c for c in cand_lines for mk in marks for p in moved if f"[{mk}]" in c and p in c]
            if still:
                floor[mid] = f"대응표로 옮긴 경로에 {sorted(marks)[0]} 이 남았다"
                continue
        for o in origin:
            if o in rows:
                to_review.setdefault(rows[o].lens, []).append(mid)
    out_dir.mkdir(parents=True, exist_ok=True)          # 실행 불능(ToolError)이면 빈 시각 폴더를 남기지 않는다
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
                                 "맥락 위치는 ` — ` 뒤에만 적는다. 판형이 아니면 그 행을 다시 요청받는다. "
                                 "` — ` 앞에는 `build_anchor` 이후 바뀐 파일(산출물 폴더 제외) 또는 이 항목의 원 발견 · 대응 경로에 속하는 "
                                 "지금 있는 `파일:행[-행]`만 적는다. 지워서 푼 항목도 같은 조건을 따르며, 삭제 사실과 허용 집합 밖 주변 위치는 "
                                 "` — ` 뒤에 적는다.",
                                 "예: `M3 | 해소 | application/<bc>/domain_layer/x/x.py:12-18 · "
                                 "application/<bc>/application_layer/y/y_use_case.py:40 — 판정을 루트 메서드 한 곳으로 옮겼다`", ""]
            if any(m in notes for m in mids):
                body += ["요지 축소 항목은 남긴 요지만 본다 — 뺀 요지는 재상정 처분 몫이라 잔존으로 세지 않는다. "
                         "원 규칙의 처방이 아닌 대체 형태는 해소가 아니다.", ""]
            body += ["## 항목", ""]
            for mid in sorted(set(mids), key=lambda k: int(k[1:])):
                body.append(f"### {mid}")
                for o, via in origins[mid]:
                    if o in rows:
                        tag: str = f" (병합 {via})" if via else ""
                        body.append(f"- 원 행 {o}{tag}: {' | '.join(rows[o].cells)}")
                if mid in notes:
                    body.append(notes[mid])
                body.append("")
            body += ["## 0C 대응표(옛 경로 → 새 경로)", ""]
            body += [f"- {a} → {b}" for a, b in sorted(mapping.items())] or ["- 없음"]
            (out_dir / f"review-{lens}.md").write_text("\n".join(body) + "\n", encoding="utf-8")
        tail: str = (f" · 해소 유지 {len(carried)}" if carried else "") + red_tail
        if pending_ids:
            print(f"요약: residual 결정적 잔존 {len(floor)}{tail} · 리뷰어 확인 대상 {len(pending_ids)}"
                  f"({'·'.join(sorted(to_review))}) · M_m 미정 — --finalize {stamp} → {out_dir}")
            return EXIT_OK
        print(f"요약: residual M_m={len(floor)}(결정적 잔존 {len(floor)}){tail} · 리뷰어 확인 대상 0 → {out_dir}")
        (out_dir / "result.json").write_text(json.dumps(
            {"stamp": stamp, "solved": {m: prev_solved[m] for m in carried}}, ensure_ascii=False, sort_keys=True)
            + "\n", encoding="utf-8")
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
        allowed: "set[str]" = code_changed | set(watched[mid])   # 해소 근거 = 앵커 이후 바뀐 코드 파일 ∪ 대응 새 경로
        answered: "set[str]" = {lens for lens, _c, _g in answers}
        got: "list[str]" = ["답 없음" for lens, ms in to_review.items() if mid in ms and lens not in answered]
        for lens, cell, ground in answers:
            state: str = _answer_state(cell)
            if state == "해소":
                locs, bad = _ground(ground)
                bad = bad or next((f"{l[0]}:{l[1]}" + (f"-{l[2]}" if l[2] != l[1] else "")
                                   for l in locs if not _location_ok(project, l)), "")
                if bad:
                    got.append("판형 아님")
                    unformatted.setdefault(mid, []).append((lens, bad))
                elif all(os.path.normpath(l[0]) in allowed for l in locs):
                    got.append("해소")
                    grounds.setdefault(mid, set()).update(os.path.normpath(l[0]) for l in locs)
                else:
                    got.append("잔존")
            else:
                got.append(state)
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
    lines += [f"| {m} | 판단 불가 |" for m in unknown]
    lines += [f"| {m} | 해소{'(요지 축소 — 남긴 요지)' if m in reduced else ''} |" for m in solved]
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
    (out_dir / "result.json").write_text(json.dumps({"stamp": stamp, "solved": snapshot, "states": states, "redo": redo},
                                                    ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(f"요약: residual M_m={m_m}(결정적 잔존 {len(floor)} · 리뷰어 잔존 {len(reviewer_left)} · 근거 판형 아님 {len(unformed)} · "
          f"판단 불가 {len(unknown)}) · 해소 {len(solved) + len(carried)}{f'(이월 {len(carried)})' if carried else ''}{red_tail} "
          f"→ {out_dir / 'result.md'}")
    if unformed:                                            # `요약:` 뒤 — 재기재 안내(코드 재개봉·새 시각이 아니다)
        notes_redo: str = " · ".join(m + "(" + ", ".join(f"{lens}: `{tok}`" for lens, tok in unformatted[m]) + ")"
                                      for m in unformed)
        print(f"  근거 판형 아님: {notes_redo} — 그 행만 같은 렌즈 리뷰어에게 묶음 머리의 판형대로 다시 받아 result-<렌즈>.md 에 "
              f"고쳐 쓰고 --finalize {stamp} 한 번 더(코드 재개봉·새 시각 아님 · 다시 판형 아님이면 잔존)")
    return EXIT_RED if m_m else EXIT_OK


# ── changes(명세 «바뀌는 것 목록» · G1 후보/반영/확정 digest) ──────────────

V_KINDS: "tuple[str, ...]" = ("내부 약속", "밖 동작", "DB 구조")
TEST_VERBS: "tuple[str, ...]" = ("update", "add", "remove")
TEST_OWNERS: "tuple[str, ...]" = ("coder", "acceptance-tester")
OUTSIDE_OWNER: str = "acceptance-tester"           # 밖 동작 = acceptance-tester · 안(내부 약속 · DB 구조) = coder
OTHER_EDIT_KINDS: "tuple[str, ...]" = ("받는 쪽 어댑터", "받는 쪽 시험", "직접 import 자리", "HTTP 소비자", "공유 표면",
                                       "프로젝트 합성")
DEPS_EDIT_KINDS: "tuple[str, ...]" = OTHER_EDIT_KINDS[:5]   # `deps` 출력과 대조하는 갈래(프로젝트 합성 제외)
OTHER_EDIT_REFS: "tuple[str, ...]" = ("0C", "0F")
MIGRATION_OPS: "tuple[str, ...]" = (
    "CreateModel", "DeleteModel", "RenameModel", "AlterModelTable", "AlterModelOptions", "AlterModelManagers",
    "AddField", "RemoveField", "AlterField", "RenameField", "AddIndex", "RemoveIndex", "RenameIndex",
    "AddConstraint", "RemoveConstraint", "AlterUniqueTogether", "AlterIndexTogether")
FORBIDDEN_OPS: "tuple[str, ...]" = ("RunPython", "RunSQL", "SeparateDatabaseAndState")
ADMISSION_HEADER: "tuple[str, ...]" = ("candidate", "protected contract/evidence", "unique production failure",
                                       "existing authoritative coverage", "decision", "owner/path")
# `retain` 행 가운데 «명시적으로 승인한 의미 보존 move/split/rename/reorganization» — candidate 칸의 표지(소문자 대조).
REORG_MARKS: "tuple[str, ...]" = ("재조직",)          # 문면(Coordinator «재조직» 낱말)과 같게 한 낱말 — 리뷰 B #9
G1_DECISION_HEAD: str = "G1 변경 결정"
G1_CONFIRMED: str = "G1 변경판 확정"
G1_DIR: str = "g1"
CANDIDATE_SUFFIX: str = "-candidate.json"
SIDECAR_SUFFIX: str = "-resolution.json"       # 후보 파일 줄기 뒤 — 후보 시점 해소 판정 표 · 입장 표 · 슬라이스 계획(digest 밖)
ROWS_BINDING: str = "resolution_rows_digest"    # 후보 스냅숏에만 — 곁 자료 해소 판정 표 `rows` 의 정규 JSON sha256(64자)
SUPPORT_VERDICT: str = "지원"
# 승인 전 지원 확인 기록 폴더 이름(`%Y%m%dT%H%M%SZ`) — behavior_support.SUPPORT_STAMP_RE 와 같은 규칙(k0 §4-3 · 판형 밖은 무시).
SUPPORT_STAMP: "re.Pattern[str]" = re.compile(r"^\d{8}T\d{6}Z$")
# G1 기록의 `<시각>` — ` · ` 앞까지(저장소 기록 관례는 공백 든 꼴 `2026-09-27 10:00` 도 쓴다) · 빈 시각은 못 읽는다.
_G1_TIME: str = r"[^\s·][^·\n]*?"
_HEAD_V: "re.Pattern[str]" = re.compile(
    r"^[-*]\s+V(\d+)\s*·\s*(.+?)\s*·\s*근거\s+(M\d+)\s*#\s*(\d+)\s*·\s*슬라이스\s+(S\d+)\s*$")
_SUB_V: "re.Pattern[str]" = re.compile(r"^[-*]\s+[*`]*(전\s*(?:→|->)\s*후|시험|바뀌는 기대|연산|데이터|영향)[*`]*\s*:\s*(.*)$")
_TEST_LINE: "re.Pattern[str]" = re.compile(
    r"^(?P<row>.+?)\s+(?P<verb>[a-z]+)\((?P<owner>[a-z-]+)\)\s+`?(?P<case>[^\s`]+)`?\s*$")
_CASE: "re.Pattern[str]" = re.compile(r"^(?P<path>[\w./-]+\.py)::(?P<name>[A-Za-z_]\w*(?:::[A-Za-z_]\w*)?)$")
_FILE_ADDR: "re.Pattern[str]" = re.compile(r"(?<![\w./-])([\w./-]+\.\w+)(::[A-Za-z_][\w:]*)?(?=[\s`\],;)]|$)")
# 입장 표 owner/path 칸의 케이스 주소 `경로.py::케이스`(클래스면 `Class::method` · 매개변수 id `[…]` 는 싣지 않는다).
_CASE_ADDR: "re.Pattern[str]" = re.compile(r"(?<![\w./-])([\w./-]+\.py)::([A-Za-z_]\w*(?:::[A-Za-z_]\w*)*)")
_ROW_OWNER: "re.Pattern[str]" = re.compile(r"(?<![\w-])(acceptance-tester|coder)(?![\w-])")
UPDATE_DECISION: str = "update"
REMOVE_DECISION: str = "remove"


def _digest(obj: object) -> str:
    """k0 공통 digest — 정규 JSON(ensure_ascii=False · sort_keys · 구분자 최소)의 sha256 앞 12.

    surrogateescape 로 바이트를 낸다(behavior_support 와 같다 — 동결 환경 값이 UTF-8 아닌 바이트를 담을 수 있다 · 보통 글은 같은 값).
    """
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":")).encode("utf-8", "surrogateescape")).hexdigest()[:12]


def snapshot_digest(snap: dict) -> str:
    """G1 스냅숏 digest — 스냅숏 전체의 k0 digest."""
    return _digest(snap)


def _heading_section(lines: "list[str]", title: str) -> "tuple[list[tuple[int, str]] | None, list[str]]":
    """`## [번호] <title>` 절의 (행 번호 1 기준, 원문) — 절이 없으면 None · 둘 이상이면 red. 펜스 표지 줄은 건너뛴다."""
    pat: "re.Pattern[str]" = re.compile(rf"^(#{{1,6}})\s+(?:§?[0-9][0-9.]*[.)]?\s+)?{re.escape(title)}\s*$")
    heads: "list[tuple[int, int]]" = []
    all_heads: "list[tuple[int, int]]" = []
    fence: "str | None" = None
    for i, ln in enumerate(lines):
        fm = _FENCE.match(ln)
        if fm:
            fence = None if fence is not None and fm.group(1)[0] == fence[0] else (fence or fm.group(1))
            continue
        if fence is not None:
            continue
        hm = _HEADING.match(ln)
        if hm:
            all_heads.append((i, len(hm.group(1))))
            if pat.match(ln.replace("*", "").replace("`", "")):
                heads.append((i, len(hm.group(1))))
    if not heads:
        return None, []
    if len(heads) > 1:
        return None, [f"`{title}` 제목이 {len(heads)}개다(하나여야 한다)"]
    start, level = heads[0]
    end: int = next((i for i, lv in all_heads if i > start and lv <= level), len(lines))
    body = [(i + 1, lines[i]) for i in range(start + 1, end) if not _FENCE.match(lines[i])]
    return body, []


class VTest:
    """V 의 시험 줄 하나 — `시험: <입장 행> <verb>(<owner>) <경로::케이스>` + `바뀌는 기대:`."""

    def __init__(self, no: int, row: str, verb: str, owner: str, case: str) -> None:
        self.no: int = no
        self.row: str = row
        self.verb: str = verb
        self.owner: str = owner
        self.case: str = case
        self.expect_old: "list[str]" = []
        self.expect_add: int = 0
        self.expect_seen: int = 0

    def as_dict(self) -> dict:
        return {"row": self.row, "verb": self.verb, "owner": self.owner, "case": self.case,
                "expect_old": list(self.expect_old), "expect_add": self.expect_add}


class VEntry:
    """`바뀌는 것 목록` 의 V 하나(머리 줄 + 하위 줄)."""

    def __init__(self, no: int, vid: str, kinds: "list[str]", basis: str, slice_: str) -> None:
        self.no: int = no
        self.vid: str = vid
        self.kinds: "list[str]" = kinds
        self.basis: str = basis
        self.slice: str = slice_
        self.before_after: "list[str]" = []
        self.tests: "list[VTest]" = []
        self.ops: "list[dict]" = []
        self.data: "list[str]" = []
        self.impact: "list[str]" = []

    def as_dict(self) -> dict:
        return {"id": self.vid, "kinds": list(self.kinds), "basis": self.basis, "slice": self.slice,
                "before_after": self.before_after[0] if self.before_after else "",
                "tests": [t.as_dict() for t in self.tests], "ops": [dict(o) for o in self.ops],
                "data": self.data[0] if self.data else None, "impact": self.impact[0] if self.impact else None}


def _op_entry(raw: str) -> "tuple[dict | None, str]":
    """`<app_label> · <연산 호출식>` → ({app, call, op, key}, 사유) — 파싱되는 호출식 · 허용 연산(makemigrations 산출 17)만."""
    app, sep, call = raw.partition("·")
    app, call = app.strip().strip("`"), call.strip().strip("`").strip()
    if not sep or not re.fullmatch(r"[A-Za-z_]\w*", app) or not call:
        return None, f"연산 줄이 `<app_label> · <연산 호출식>` 이 아니다: `{raw.strip()[:80]}`"
    try:
        node = ast.parse(call, mode="eval").body
    except SyntaxError as exc:
        return None, f"연산 호출식이 파싱되지 않는다({exc.msg}): `{call[:80]}`"
    if not isinstance(node, ast.Call):
        return None, f"연산 줄이 호출식이 아니다: `{call[:80]}`"
    func = node.func
    name: str = func.attr if isinstance(func, ast.Attribute) else func.id if isinstance(func, ast.Name) else ""
    owner_ok: bool = isinstance(func, ast.Name) or (isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name)
                                                    and func.value.id == "migrations")
    if name in FORBIDDEN_OPS:
        return None, f"연산 `{name}` 은 허용 연산이 아니다(데이터 마이그레이션 · 상태 분리는 만들지 않는다)"
    if name not in MIGRATION_OPS or not owner_ok:
        return None, f"연산 `{name or call[:40]}` 이 makemigrations 산출 연산({len(MIGRATION_OPS)}) 밖"
    key: str = f"{app} · " + ast.dump(node, annotate_fields=True, include_attributes=False)
    return {"app": app, "call": call, "op": name, "key": key}, ""


def _expectations(text: str) -> "tuple[list[str], int, str]":
    """`바뀌는 기대:` 칸 → (옛 원소 원문 목록, 기대 추가 수, 사유)."""
    olds: "list[str]" = re.findall(r"«(.*?)»", text)
    rest: str = re.sub(r"«.*?»", "", text)
    adds: "list[str]" = re.findall(r"기대 추가\s+(\d+)", rest)
    rest = re.sub(r"기대 추가\s+\d+", "", rest)
    if re.sub(r"[\s·,]", "", rest):
        return olds, 0, f"바뀌는 기대 칸에 «…» · `기대 추가 k` 밖 글이 있다: `{text.strip()[:80]}`"
    if len(adds) > 1:
        return olds, 0, "`기대 추가 k` 가 둘 이상이다"
    add: int = int(adds[0]) if adds else 0
    if not olds and add == 0:
        return olds, 0, "바뀌는 기대가 비었다(옛 원소 «…» 또는 `기대 추가 k` ≥ 1)"
    if any(not o.strip() for o in olds):
        return olds, add, "빈 «» 원소가 있다"
    return olds, add, ""


def _v_section(text: str) -> "tuple[list[VEntry], list[str]]":
    """명세 `바뀌는 것 목록` → (V 목록, 형식 red) — 절이 없으면 V 0(형식 red 없음 · 변경 행이 V 를 가리키면 해소 표가 잡는다)."""
    body, reds = _heading_section(text.split("\n"), "바뀌는 것 목록")
    out: "list[VEntry]" = []
    if body is None:
        return out, reds
    cur: "VEntry | None" = None
    test: "VTest | None" = None
    seen: "set[str]" = set()
    for no, raw in body:
        s: str = raw.strip()
        if not s or not s.startswith(("-", "*")):
            continue
        if s.lstrip("-* ").strip() in ("없음", "V 없음"):
            continue
        hm = _HEAD_V.match(s[:1] + re.sub(r"[*`]", "", s[1:]))        # 머리 줄의 강조 · 백틱은 벗긴다(목록 표지는 둔다)
        if hm and len(raw) - len(raw.lstrip()) < 2:
            vid: str = f"V{hm.group(1)}"
            kinds: "list[str]" = [k.strip() for k in hm.group(2).split("+")]
            if any(k not in V_KINDS for k in kinds) or len(set(kinds)) != len(kinds):
                reds.append(f"{vid}({no}행) 종류 `{hm.group(2)}` 가 {' · '.join(V_KINDS)}(` + ` 로 겹침) 밖")
            if vid in seen:
                reds.append(f"{vid}({no}행) V 번호 중복")
            seen.add(vid)
            cur, test = VEntry(no, vid, kinds, f"{hm.group(3)} #{hm.group(4)}", hm.group(5)), None
            out.append(cur)
            continue
        sm = _SUB_V.match(s)
        if cur is None or sm is None:
            reds.append(f"{no}행 `바뀌는 것 목록` 형식 밖 줄: `{s[:80]}`")
            continue
        field, value = sm.group(1), sm.group(2).strip()
        if field.startswith("전"):
            cur.before_after.append(value)
        elif field == "시험":
            tm = _TEST_LINE.match(value)
            if not tm or tm.group("verb") not in TEST_VERBS or tm.group("owner") not in TEST_OWNERS \
                    or not _CASE.match(tm.group("case")):
                reds.append(f"{cur.vid} {no}행 시험 줄이 `<입장 행> update|add|remove(coder|acceptance-tester) "
                            f"<경로.py::케이스>` 가 아니다: `{value[:80]}`")
                test = None
                continue
            test = VTest(no, tm.group("row").strip(), tm.group("verb"), tm.group("owner"), tm.group("case"))
            cur.tests.append(test)
        elif field == "바뀌는 기대":
            if test is None:
                reds.append(f"{cur.vid} {no}행 `바뀌는 기대` 앞에 시험 줄이 없다")
                continue
            test.expect_seen += 1
            olds, add, why = _expectations(value)
            if why:
                reds.append(f"{cur.vid} {no}행 {why}")
            test.expect_old, test.expect_add = olds, add
        elif field == "연산":
            op, why = _op_entry(value)
            if why:
                reds.append(f"{cur.vid} {no}행 {why}")
            else:
                cur.ops.append(op)  # type: ignore[arg-type]
        elif field == "데이터":
            cur.data.append(value)
        else:
            cur.impact.append(value)
    for v in out:
        reds += _v_shape(v)
    return out, reds


def _v_shape(v: VEntry) -> "list[str]":
    """V 하나의 판형 — 전 → 후 하나 · 종류 ↔ 하위 줄 · 시험 줄 owner ↔ 종류 · 바뀌는 기대 하나."""
    reds: "list[str]" = []
    tag: str = f"{v.vid}({v.no}행)"
    if len(v.before_after) != 1 or not v.before_after[0]:
        reds.append(f"{tag} `전 → 후:` 줄이 정확히 하나가 아니다")
    for name, vals in (("데이터", v.data), ("영향", v.impact)):
        if len(vals) > 1:
            reds.append(f"{tag} `{name}:` 줄이 둘 이상이다")
    if "DB 구조" in v.kinds and not v.ops:
        reds.append(f"{tag} DB 구조 V 에 `연산:` 줄이 없다")
    if v.ops and "DB 구조" not in v.kinds:
        reds.append(f"{tag} `연산:` 줄은 DB 구조 V 에만 쓴다")
    if "DB 구조" in v.kinds and not v.data:
        reds.append(f"{tag} DB 구조 V 에 `데이터:` 줄이 없다")
    if "밖 동작" in v.kinds and not v.impact:
        reds.append(f"{tag} 밖 동작 V 에 `영향:` 줄이 없다")
    for t in v.tests:
        if t.expect_seen != 1:
            reds.append(f"{tag} 시험 {t.case}({t.no}행)의 `바뀌는 기대:` 줄이 {t.expect_seen}개다(하나)")
        if t.owner == OUTSIDE_OWNER and "밖 동작" not in v.kinds:
            reds.append(f"{tag} 시험 {t.case} owner `{t.owner}` 는 밖 동작 V 에만(지금 {' + '.join(v.kinds)})")
        if t.owner != OUTSIDE_OWNER and not ({"내부 약속", "DB 구조"} & set(v.kinds)):
            reds.append(f"{tag} 시험 {t.case} owner `{t.owner}` 는 내부 약속 · DB 구조 V 에만(밖 동작은 {OUTSIDE_OWNER})")
        if t.verb == "add" and t.expect_old:
            reds.append(f"{tag} add 시험 {t.case} 에 옛 원소 «…» 가 있다(새 케이스는 `기대 추가 k` 만)")
    return reds


def _other_edits(text: str, vids: "set[str]") -> "tuple[list[dict], list[str]]":
    """명세 `다른 BC 편집 목록` → ([{path, kind, ref}], 형식 red) — 줄 `<경로> · <갈래> · <V<n> | 0C | 0F>`(표지 `- ` · `* ` 있든 없든).

    절 안(머리 · 펜스 밖)의 비어 있지 않은 줄 가운데 표지를 뗀 뒤 `·` 로 세 칸이 되는 줄을 읽는다. 세 칸이 안 되는데 ` · ` 를
    품은 줄은 판형 밖 red · ` · ` 없는 산문 줄(«없음» 따위)은 무시한다.
    """
    lines: "list[str]" = text.split("\n")
    body, reds = _heading_section(lines, "다른 BC 편집 목록")
    out: "list[dict]" = []
    if not body:
        return out, reds
    first: int = body[0][0] - 1
    while first > 0 and _FENCE.match(lines[first - 1]) and not _HEADING.match(lines[first - 1]):
        first -= 1                                            # 절 머리 바로 뒤의 펜스 표지 줄(본문에서 빠진 줄)부터
    fence: "tuple[str, int] | None" = None
    for idx in range(first, body[-1][0]):
        raw: str = lines[idx]
        no: int = idx + 1
        fm = _FENCE_LINE.match(raw)
        if fence is None and fm and not (fm.group(1)[0] == "`" and "`" in fm.group(2)):
            fence = (fm.group(1)[0], len(fm.group(1)))
            continue
        if fence is not None:
            if fm and fm.group(1)[0] == fence[0] and len(fm.group(1)) >= fence[1] and not fm.group(2).strip():
                fence = None
            continue
        s: str = raw.strip()
        if not s or _HEADING.match(raw):
            continue
        s = re.sub(r"^[-*]\s+", "", s).strip()
        if s == "없음" or "·" not in s:
            continue
        parts: "list[str]" = [p.strip().strip("`").strip() for p in s.split("·")]
        if len(parts) != 3:
            if " · " in s:
                reds.append(f"다른 BC 편집 줄 판형 밖 — {no}행 `<경로> · <갈래> · <V<n> | 0C | 0F>` 가 아니다: `{s[:80]}`")
            continue
        path, kind, ref = parts
        norm: str = os.path.normpath(path).replace(os.sep, "/")
        if os.path.isabs(path) or norm == ".." or norm.startswith("../") or not path:
            reds.append(f"{no}행 다른 BC 편집 경로 `{path}` 가 저장소 상대 경로가 아니다")
            continue
        if kind not in OTHER_EDIT_KINDS:
            reds.append(f"{no}행 다른 BC 편집 갈래 `{kind}` 가 {' · '.join(OTHER_EDIT_KINDS)} 밖")
        if ref not in OTHER_EDIT_REFS and not (re.fullmatch(r"V\d+", ref) and ref in vids):
            reds.append(f"{no}행 다른 BC 편집 연결 `{ref}` 가 0C · 0F · 목록의 V 가 아니다")
        out.append({"path": norm, "kind": kind, "ref": ref})
    return out, reds


class AdmissionRow:
    """영구 테스트 입장 표(정본 6열) 한 행."""

    def __init__(self, cells: "list[str]") -> None:
        self.cells: "list[str]" = [c.strip() for c in cells]
        self.candidate: str = self.cells[0]
        self.evidence: str = self.cells[1]
        self.decision: str = re.sub(r"[*`]", "", self.cells[4]).strip().lower()
        self.owner_path: str = self.cells[5]
        m = _FILE_ADDR.search(self.owner_path.replace("`", " "))
        self.path: "str | None" = m.group(1) if m else None
        self.case: "str | None" = m.group(2)[2:] if m and m.group(2) else None

    @property
    def text(self) -> str:
        return "| " + " | ".join(c.replace("|", "\\|") for c in self.cells) + " |"


def _admission(text: str) -> "list[AdmissionRow]":
    """명세의 영구 테스트 입장 표 행 전부(정본 6열 머리 아래 · 여러 표면 모두)."""
    rows: "list[AdmissionRow]" = []
    inside: bool = False
    for ln in text.split("\n"):
        s: str = ln.strip()
        if not s.startswith("|"):
            inside = False
            continue
        cells: "list[str]" = _cells(s)
        if [re.sub(r"[*`]", "", c).strip().lower() for c in cells] == list(ADMISSION_HEADER):
            inside = True
            continue
        if not inside or re.fullmatch(r"\|[\s:|-]*\|", s) or len(cells) != len(ADMISSION_HEADER):
            continue
        rows.append(AdmissionRow(cells))
    return rows


def _reorg(row: AdmissionRow) -> bool:
    low: str = row.candidate.lower()
    return row.decision == "retain" and any(mark in low for mark in REORG_MARKS)


def _row_v(row_text: str, case: str, links: "list[tuple[str, str, str]]") -> "str | None":
    """입장 행(표 행 원문)이 딸린 V — 그 행을 가리키는 `시험:` 줄(V id, 입장 행, 케이스) 가운데 케이스가 같은 것이 먼저,
    없으면 그 행을 가리키는 첫 V · 어느 V 도 가리키지 않으면 None."""
    name: str = normalize(_cells(row_text)[0])
    attached: "list[tuple[str, str]]" = [(vid, c) for vid, row, c in links if normalize(row) == name]
    return next((vid for vid, c in attached if c == case), attached[0][0] if attached else None)


def _update_items(rows: "list[AdmissionRow]", links: "list[tuple[str, str, str]]") -> "list[dict]":
    """decision `update` · `remove` 행 → `update_rows` · `remove_rows` 항목(표 차례 · 케이스 주소마다 한 항목) — 0T close 의 D 확정
    처분 · remove 예외 · 케이스 감소 허용 자료.

    `case` = owner/path 칸에 적힌 `경로.py::케이스` 글자 그대로(백틱만 벗김). 케이스 주소가 없는 행은 파일 주소(없으면 빈
    값)로 한 항목을 싣는다 — 케이스 글자 일치에 걸리지 않아 그 파일의 D 확정은 허용되지 않는다(행은 digest 에 남는다).
    """
    out: "list[dict]" = []
    for r in rows:
        cell: str = r.owner_path.replace("`", " ")
        cases: "list[str]" = []
        for m in _CASE_ADDR.finditer(cell):
            case: str = f"{m.group(1)}::{m.group(2)}"
            if case not in cases:
                cases.append(case)
        om = _ROW_OWNER.search(re.sub(r"\S*(?:/|\.py)\S*", " ", cell))
        for case in cases or [r.path or ""]:
            out.append({"case": case, "owner": om.group(1) if om else "", "row": r.text, "v": _row_v(r.text, case, links)})
    return out


def _read_json_escaped(path: Path) -> object:
    """기록 JSON — surrogateescape 로 읽는다(behavior_support 가 그렇게 쓴다)."""
    return json.loads(path.read_text(encoding="utf-8", errors="surrogateescape"))


def _latest_support(folder: Path) -> "Path | None":
    """g0-collect.json 의 verdict 가 «지원»인 가장 새 시각 폴더 — `behavior_support.latest_support` 와 같은 규칙(k0 §4-3).

    이름이 `%Y%m%dT%H%M%SZ` 판형인 폴더만 본다 · 이름 내림차순 · g0-collect 를 못 읽거나 판정이 «지원»이 아니면 건너뛴다.
    """
    root: Path = Path(folder) / "behavior" / "support"
    if not root.is_dir():
        return None
    for d in sorted((p for p in root.iterdir() if p.is_dir() and SUPPORT_STAMP.match(p.name)), reverse=True):
        collect: Path = d / "g0-collect.json"
        if collect.is_file():
            try:
                if _read_json_escaped(collect).get("verdict") == SUPPORT_VERDICT:  # type: ignore[union-attr]
                    return d
            except (OSError, ValueError, AttributeError):
                continue
    return None


def _support_binding(folder: Path) -> "tuple[str, str]":
    """(지원 기록 이름, 실행 정의 digest) — 가장 새 «지원» 기록의 `run-definition.json` 을 k0 digest 규칙으로 잰다.

    그 기록의 실행 정의가 없거나 깨졌으면(JSON 아님 · `argvs` · `env` 칸 없음) 더 오래된 기록으로 내려가지 않고 실행 불능이다.
    """
    rec: "Path | None" = _latest_support(folder)
    if rec is None:
        raise ToolError(f"승인 전 지원 확인 기록(판정 «{SUPPORT_VERDICT}»)이 없다 — {Path(folder) / 'behavior' / 'support'} · G0 의 "
                        f"`behavior_guard.py support <폴더> --collect` 가 먼저다")
    try:
        definition = _read_json_escaped(rec / "run-definition.json")
        bound: dict = {"argvs": definition["argvs"], "env": definition["env"]}  # type: ignore[index,call-overload]
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise ToolError(f"가장 새 지원 기록 {rec.name} 의 run-definition.json 을 읽지 못한다({type(exc).__name__}) — 더 오래된 "
                        f"기록으로 내려가지 않는다(지원 확인을 새 시각 폴더로 다시 돈다)") from None
    return rec.name, _digest(bound)


class SpecChanges:
    """명세(승인판)에서 읽은 G1 결속 재료 — V · 다른 BC 편집 · 입장 표 · retain 재조직 행 · update 행."""

    def __init__(self, folder: Path) -> None:
        self.spec: Path = folder / "design-spec.md"
        self.text: str = _read(self.spec)
        self.v, self.reds = _v_section(self.text)
        self.vids: "set[str]" = {v.vid for v in self.v}
        self.edits, edit_reds = _other_edits(self.text, self.vids)
        self.reds += edit_reds
        self.rows: "list[AdmissionRow]" = _admission(self.text)
        self.retain: "list[dict]" = []
        for r in self.rows:
            if _reorg(r):
                if r.path is None:
                    self.reds.append(f"retain 재조직 행 «{r.candidate[:40]}» owner/path 에 파일 주소가 없다")
                    continue
                self.retain.append({"path": r.path, "case": r.case, "why": r.evidence})

    def linked(self, tests: "list[VTest]") -> "list[str]":
        """시험 줄이 가리키는 입장 행(원문 표 행) — 처음 나온 차례."""
        out: "list[str]" = []
        for t in tests:
            for r in self.rows:
                if normalize(r.candidate) == normalize(t.row) and r.text not in out:
                    out.append(r.text)
        return out

    def decision_rows(self, decision: str) -> "list[dict]":
        """입장 표의 decision 이 `decision` 인 행 전부(k0 §4-4 `update_rows` · `remove_rows` — `v` = 그 행이 딸린 V · 없으면 None)."""
        links: "list[tuple[str, str, str]]" = [(v.vid, t.row, t.case) for v in self.v for t in v.tests]
        return _update_items([r for r in self.rows if r.decision == decision], links)

    def update_rows(self) -> "list[dict]":
        return self.decision_rows(UPDATE_DECISION)

    def snapshot(self, folder: Path) -> dict:
        record, run_digest = _support_binding(folder)
        tests: "list[VTest]" = [t for v in self.v for t in v.tests]
        return {"version": 1, "V": [v.as_dict() for v in self.v], "other_bc_edits": [dict(e) for e in self.edits],
                "linked_rows": self.linked(tests), "retain_rows": [dict(r) for r in self.retain],
                "update_rows": self.update_rows(), "remove_rows": self.decision_rows(REMOVE_DECISION),
                "run_definition_digest": run_digest, "support_record": record}


def changes_snapshot(folder: Path, project: Path) -> dict:
    """지금 명세(승인판) 기준 G1 스냅숏(k0 §4-4 판형) — 명세 · 지원 기록을 못 읽거나 형식 red 면 ToolError(RuntimeError)."""
    del project                                          # 스냅숏은 명세 · 지원 기록만 — 서명은 k0 고정
    spec: SpecChanges = SpecChanges(Path(folder))
    if spec.reds:
        raise ToolError(f"명세 «바뀌는 것 목록» · «다른 BC 편집 목록» 형식 red {len(spec.reds)}: {spec.reds[0]}")
    return spec.snapshot(Path(folder))


def _current_scope(folder: Path) -> "tuple[str, list[str]]":
    """refactor-scope.md 이번 실행 몫(`# 앞 실행` 절 앞) — (본문, 줄)."""
    text: str = re.split(r"(?m)^#+\s*앞 실행", _read(Path(folder) / "refactor-scope.md"))[0]
    return text, text.split("\n")


_G1_HEAD: "re.Pattern[str]" = re.compile(
    rf"^(#+)\s+{G1_DECISION_HEAD}\s+({_G1_TIME})\s*·\s*후보 digest\s+([0-9a-f]{{12}})\s*$")
_G1_CONF: "re.Pattern[str]" = re.compile(
    rf"^(?:[-*]\s+)?{G1_CONFIRMED}[ \t]+({_G1_TIME})[ \t]*·\s*digest\s+([0-9a-f]{{12}})\s*·\s*후보\s+([0-9a-f]{{12}})\s*$")


_FENCE_LINE: "re.Pattern[str]" = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")


def _indent_width(raw: str) -> int:
    """줄머리 공백 폭(탭 = 다음 4의 배수)."""
    width: int = 0
    for ch in raw:
        if ch == " ":
            width += 1
        elif ch == "\t":
            width += 4 - width % 4
        else:
            break
    return width


def _g1_like(line: str) -> bool:
    """G1 기록 꼴(결정 절 머리 · 확정 줄 · 결정 줄)인가 — 판형과 무관하게 넓게."""
    s: str = line.strip()
    return _is_g1_head(s) or _is_g1_conf(s) or bool(re.match(r"^[-*]?\s*V\d+\s*·\s*결정\s*=", s))


def _g1_lines(folder: Path) -> "list[tuple[int, str]]":
    """이번 실행 몫의 실제 기록 줄(1 기준 행 번호 = 파일 행 번호, 앞뒤 공백 걷은 원문) — 코드 펜스 안(예시)은 뺀다.

    펜스는 CommonMark 규칙으로 읽는다: 여는 펜스(들여쓰기 0~3칸 · ``` 또는 ~~~ 3개 이상 · 백틱 펜스의 정보 문자열에 백틱 없음)의
    종류와 길이를 보존하고, 같은 종류 · 여는 길이 이상 · 뒤에 공백만 있는 줄만 닫힘이다. 판독을 지원하지 않는 꼴에 G1 기록 꼴 줄이
    걸리면 실행 불능(ToolError)이다 — 닫히지 않은 펜스 뒤의 G1 기록 꼴 줄 · 펜스 밖에서 4칸 이상 들여 쓴 G1 기록 꼴 줄(들여쓴 코드
    블록인지 목록 안 줄인지 가리지 않는다).
    """
    out: "list[tuple[int, str]]" = []
    fence: "tuple[str, int, int] | None" = None              # (문자, 길이, 연 행)
    inside: "list[int]" = []
    for no, raw in enumerate(_current_scope(folder)[1], 1):
        fm = _FENCE_LINE.match(raw)
        if fence is None:
            if fm and not (fm.group(1)[0] == "`" and "`" in fm.group(2)):
                fence, inside = (fm.group(1)[0], len(fm.group(1)), no), []
                continue
            if _indent_width(raw) >= 4 and _g1_like(raw):
                raise ToolError(f"refactor-scope.md {no}행 G1 기록 꼴 줄이 4칸 이상 들여 쓰여 있다(들여쓴 코드 블록 · 목록 안 줄 — "
                                f"판독 지원 밖): {raw.strip()[:80]}")
            out.append((no, raw.strip()))
            continue
        if fm and fm.group(1)[0] == fence[0] and len(fm.group(1)) >= fence[1] and not fm.group(2).strip():
            fence = None
            continue
        if _g1_like(raw):
            inside.append(no)
    if fence is not None and inside:
        raise ToolError(f"refactor-scope.md {fence[2]}행 코드 펜스(`{fence[0] * fence[1]}`)가 닫히지 않았는데 그 뒤 {inside[0]}행에 "
                        f"G1 기록 꼴 줄이 있다 — 판독 지원 밖")
    return out


def _is_g1_head(line: str) -> bool:
    """`#` 제목 줄이고 `G1 변경 결정` 을 담았나(판형과 무관 — 판형 밖이면 실행 불능을 내려고 넓게 잡는다)."""
    return bool(re.match(r"^#+\s", line)) and G1_DECISION_HEAD in line


def _is_g1_conf(line: str) -> bool:
    """줄머리(목록 표지 뒤)가 `G1 변경판 확정` 인가 — 문장 중간의 언급은 기록이 아니다."""
    return re.sub(r"^[-*]\s+", "", line).startswith(G1_CONFIRMED)


def _g1_head_at(lines: "list[tuple[int, str]]", upto: "int | None" = None) -> "tuple[int, int, str, str] | None":
    """`upto` 행 앞(없으면 끝까지)의 가장 최근 `## G1 변경 결정` 절 머리 → (행, 제목 수준, 시각, 후보 digest) · 없으면 None.

    가장 최근 머리가 판형 밖이면 앞 절로 내려가지 않고 실행 불능(ToolError)이다.
    """
    heads: "list[tuple[int, str]]" = [(no, ln) for no, ln in lines if _is_g1_head(ln) and (upto is None or no < upto)]
    if not heads:
        return None
    no, line = heads[-1]
    m = _G1_HEAD.match(line)
    if not m:
        raise ToolError(f"refactor-scope.md {no}행 최신 `{G1_DECISION_HEAD}` 절 머리가 판형(`## {G1_DECISION_HEAD} <시각> · 후보 "
                        f"digest <12자>`) 밖이다 — 앞 절로 내려가지 않는다: {line[:120]}")
    return no, len(m.group(1)), m.group(2).strip(), m.group(3)


def g1_confirmed(folder: Path) -> "tuple[str, str, str] | None":
    """이번 실행 몫의 마지막 `G1 변경판 확정 <시각> · digest <d> · 후보 <c>` 줄 → (시각, d, c) · 그런 줄이 없으면 None.

    실제 기록 줄만 본다(줄머리 · 코드 펜스 밖). 가장 최근 확정 줄이 판형 밖이거나, 그 줄 앞의 가장 최근 `## G1 변경 결정` 절이
    없거나 판형 밖이거나 그 절의 후보 digest 가 확정 줄의 `후보` 와 다르면 실행 불능(ToolError — RuntimeError 계열)이다.
    """
    path: Path = Path(folder) / "refactor-scope.md"
    if not path.is_file():
        return None
    lines: "list[tuple[int, str]]" = _g1_lines(Path(folder))
    confs: "list[tuple[int, str]]" = [(no, ln) for no, ln in lines if _is_g1_conf(ln)]
    if not confs:
        return None
    no, line = confs[-1]
    m = _G1_CONF.match(line)
    if not m:
        raise ToolError(f"refactor-scope.md {no}행 최신 `{G1_CONFIRMED}` 줄이 판형(`{G1_CONFIRMED} <시각> · digest <12자> · 후보 "
                        f"<12자>`) 밖이다 — 앞 확정 줄로 내려가지 않는다: {line[:120]}")
    head = _g1_head_at(lines, no)
    if head is None:
        raise ToolError(f"refactor-scope.md {no}행 `{G1_CONFIRMED}` 줄 앞에 `## {G1_DECISION_HEAD}` 절이 없다(결속할 후보가 없다)")
    cut = next(((hn, hl) for hn, hl in lines if head[0] < hn < no and re.match(r"^(#+)\s", hl)
                and len(re.match(r"^(#+)\s", hl).group(1)) <= head[1]), None)
    if cut is not None:                                       # 문면 ⑥ «같은 절에» — `###` 이하는 절 안
        raise ToolError(f"refactor-scope.md {no}행 `{G1_CONFIRMED}` 줄이 {G1_DECISION_HEAD} 절({head[0]}행) 밖이다 — {cut[0]}행 "
                        f"머리 `{cut[1][:40]}` 뒤(판형 밖 — 확정 줄은 그 절 안에)")
    if head[3] != m.group(3):
        raise ToolError(f"refactor-scope.md {no}행 `{G1_CONFIRMED}` 의 후보 {m.group(3)} ≠ 그 앞 `{G1_DECISION_HEAD}`({head[0]}행)의 "
                        f"후보 digest {head[3]}")
    return m.group(1).strip(), m.group(2), m.group(3)


def load_candidate(folder: Path, candidate_digest: str) -> dict:
    """`<폴더>/g1/*-candidate.json` 가운데 digest 가 같은 후보 스냅숏(가장 새 것) — 없으면 ToolError."""
    base: Path = Path(folder) / G1_DIR
    for path in sorted(base.glob(f"*{CANDIDATE_SUFFIX}"), reverse=True) if base.is_dir() else []:
        try:
            snap = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if isinstance(snap, dict) and snapshot_digest(snap) == candidate_digest:
            return snap
    raise ToolError(f"후보 digest {candidate_digest} 인 후보 스냅숏이 {base} 에 없다")


def _baseline_reader(project: Path, record: "Path | None") -> "Callable[[str], bytes | None]":
    """«바뀌는 기대» 기준 판 읽기 — 창 open 기록이면 head 블롭 + dirty0(b64) · 아니면 지금 파일."""
    if record is None:
        return lambda rel: (project / rel).read_bytes() if (project / rel).is_file() else None
    try:
        opened: dict = json.loads(_read(record))
        head: str = opened["head"]
        dirty: dict = opened.get("dirty") or {}
    except (ValueError, KeyError, TypeError):
        raise ToolError(f"창 open 기록 `{record}` 에 head · dirty 가 없다") from None

    def read(rel: str) -> "bytes | None":
        if rel in dirty:
            b64 = (dirty[rel] or {}).get("b64")
            return base64.b64decode(b64) if b64 is not None else None
        p = subprocess.run(["git", "-C", str(project), "cat-file", "blob", f"{head}:{rel}"], capture_output=True)
        return p.stdout if p.returncode == 0 else None
    return read


def _case_source(data: "bytes | None", name: str) -> "str | None":
    """파일 원문에서 케이스(`함수` · `클래스::메서드`) 정의 원문(decorator 포함) — 없으면 None."""
    if data is None:
        return None
    try:
        source: str = data.decode("utf-8")
        tree = ast.parse(source)
    except (UnicodeDecodeError, SyntaxError, ValueError):
        return None
    names: "list[str]" = name.split("::")
    scope: "list[ast.stmt]" = tree.body
    node: "ast.AST | None" = None
    for k, part in enumerate(names):
        want = (ast.FunctionDef, ast.AsyncFunctionDef) if k == len(names) - 1 else (ast.ClassDef,)
        hits = [n for n in scope if isinstance(n, want) and n.name == part]
        if len(hits) != 1:
            return None
        node = hits[0]
        scope = getattr(node, "body", [])
    if node is None:
        return None
    lines: "list[str]" = re.split(r"\r\n|\r|\n", source)
    start: int = min([node.lineno] + [d.lineno for d in getattr(node, "decorator_list", [])])
    return "\n".join(lines[start - 1:node.end_lineno])  # type: ignore[attr-defined]


CLOSED_VERDICTS: "tuple[str, ...]" = ("green", "audit")   # behavior_guard 의 닫힌 창(마지막 close 판정 — 그 밖 · close 없음은 열린 창)


def _guard_module():  # noqa: ANN202
    try:
        import behavior_guard  # noqa: PLC0415 — 함수 안 import(k0 §4-1) · 창 허용 표 `allow_table` 을 장치와 같은 정의로
    except Exception as exc:  # noqa: BLE001
        raise ToolError(f"behavior_guard 를 불러오지 못했다 — {type(exc).__name__}: {exc}") from exc
    return behavior_guard


def _utc(value: object) -> "datetime | None":
    try:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ") if isinstance(value, str) else None
    except ValueError:
        return None


class _PastWindow:
    """닫힌 변경 창 하나의 증거(F-B1R-5) — 번호 · open 기록 · 그 창에서 집행이 결속된 원소 {(V id, 갈래, 케이스, 동사, o): 덧값}."""

    def __init__(self, n: int, opened: dict, where: str, executed: "dict[tuple, object]") -> None:
        self.n: int = n
        self.opened: dict = opened
        self.where: str = where
        self.executed: "dict[tuple, object]" = executed


def _window_elements(snap: dict) -> "dict[tuple, list[tuple[str, object]]]":
    """스냅숏 V 의 시험 원소 {(갈래, 케이스, 동사, o): [(V id, 덧값)]} — 갈래 `old`(옛 원문 o) · `add` · `remove`(케이스) ·
    `plus`(기대 추가 k — o 자리에 None · 덧값 k)."""
    out: "dict[tuple, list[tuple[str, object]]]" = {}
    for v in snap.get("V", []):
        for t in v.get("tests", []):
            case, verb = t["case"], t["verb"]
            for o in t.get("expect_old", []):
                out.setdefault(("old", case, verb, o), []).append((v["id"], None))
            if verb in ("add", "remove"):
                out.setdefault((verb, case, verb, None), []).append((v["id"], None))
            elif int(t.get("expect_add", 0) or 0) > 0:
                out.setdefault(("plus", case, verb, None), []).append((v["id"], int(t["expect_add"])))
    return out


def _closed_windows(folder: Path, upto: "int | None") -> "list[_PastWindow]":
    """이 실행의 쓸 수 있는 닫힌 변경 창(F-B1R-5 · 설계 v2 §1-1 · §1-2) — 번호(정수) 차례 · 열린 창(그리고 `upto`) 앞만.

    닫힌 창 = 마지막 close 판정 green · audit · 그 마지막 close 가 마지막 rebind 보다 엄격히 뒤(시각을 못 읽으면 안 씀). 그 창
    `g1_digest` 의 `G1 변경판 확정` 줄 → 후보 → `_expected_applied` 로 결속 판을 되살려 `allow_table` 이 open allow 와 같을 때만
    쓴다(다르면 · 못 찾으면 안 씀). 증거로 쓰려던 open · close 가 JSON 이 아니거나 필수 칸 자료형이 틀리면 실행 불능이다."""
    m = re.search(r"실행 · G0 승인 (\S+)", _read(Path(folder) / "refactor-scope.md"))
    if not m:
        return []
    run_dir: Path = Path(folder) / "behavior" / re.sub(r"[^\w.-]", "_", m.group(1))
    opens: "list[tuple[int, Path]]" = []
    for p in run_dir.glob("w*-open.json") if run_dir.is_dir() else []:
        nm = re.fullmatch(r"w(\d+)-open\.json", p.name)
        if nm:
            opens.append((int(nm.group(1)), p))
    confirmed: "list[tuple[str, str]]" = []
    out: "list[_PastWindow]" = []
    guard = None
    for n, open_path in sorted(opens):
        if upto is not None and n >= upto:
            break
        try:
            opened = json.loads(open_path.read_text(encoding="utf-8"))
        except (OSError, ValueError, UnicodeDecodeError):
            raise ToolError(f"창 기록 `{open_path.name}` 이 JSON 이 아니다 — 닫힌 창 기준선을 고를 수 없다") from None
        close_path: Path = open_path.with_name(f"w{n}-close.json")
        closes: object = []
        if close_path.is_file():
            try:
                closes = json.loads(close_path.read_text(encoding="utf-8"))
            except (OSError, ValueError, UnicodeDecodeError):
                raise ToolError(f"창 기록 `{close_path.name}` 이 JSON 이 아니다 — 닫힌 창 기준선을 고를 수 없다") from None
        if not isinstance(opened, dict) or not isinstance(closes, list) or (closes and not isinstance(closes[-1], dict)):
            raise ToolError(f"창 기록 `{open_path.name}` · `{close_path.name}` 의 꼴이 틀리다(open = 객체 · close = 판정 목록)")
        last: "dict | None" = closes[-1] if closes else None
        if last is None or last.get("verdict") not in CLOSED_VERDICTS:
            break                                            # 열린 창 — 그 뒤 창은 보지 않는다
        if opened.get("kind") != "change":
            continue
        need: "list[tuple[str, dict, str, type]]" = [
            (open_path.name, opened, "head", str), (open_path.name, opened, "dirty", dict),
            (open_path.name, opened, "g1_digest", str), (open_path.name, opened, "allow", dict),
            (close_path.name, last, "verdict", str), (close_path.name, last, "closed", str),
            (close_path.name, last, "approved_hits", dict), (close_path.name, last, "cases_added", list),
            (close_path.name, last, "cases_removed", list)]
        for fname, rec, key, kind in need:
            if not isinstance(rec.get(key), kind):
                raise ToolError(f"창 기록 `{fname}` 의 칸 `{key}` 가 없거나 자료형이 틀리다 — 닫힌 창 기준선을 고를 수 없다")
        for case, hit in last["approved_hits"].items():
            if not (isinstance(hit, dict) and isinstance(hit.get("old", []), list) and isinstance(hit.get("add", 0), int)):
                raise ToolError(f"창 기록 `{close_path.name}` 의 칸 `approved_hits[{case}]` 자료형이 틀리다")
        rebinds: object = opened.get("rebinds") or []
        closed_at = _utc(last["closed"])
        if not isinstance(rebinds, list) or closed_at is None:
            continue
        if rebinds:
            at = _utc(rebinds[-1].get("at")) if isinstance(rebinds[-1], dict) else None
            if at is None or not closed_at > at:
                continue                                     # rebind 뒤 판정이 아니다 — 증거로 쓰지 않는다
        if not confirmed:
            confirmed = [(cm.group(2), cm.group(3)) for _no, ln in _g1_lines(Path(folder))
                         for cm in [_G1_CONF.match(ln)] if cm]
        snap: "dict | None" = None
        for d, c in confirmed:
            if d != opened["g1_digest"]:
                continue
            try:
                cand: dict = load_candidate(Path(folder), c)
            except ToolError:
                continue
            removed: "set[str]" = {v["id"] for v in cand.get("V", [])} - set(opened["allow"].get("V", []))
            rebuilt: dict = _expected_applied(cand, removed)
            guard = guard or _guard_module()
            if guard.allow_table(rebuilt) == opened["allow"]:
                snap = rebuilt
                break
        if snap is None:
            continue                                         # 결속 판을 되살리지 못함 — 증거로 쓰지 않는다
        hits: dict = last["approved_hits"]
        executed: "dict[tuple, object]" = {}
        for (kind, case, verb, o), owners in _window_elements(snap).items():
            if len(owners) != 1:
                continue                                     # 같은 원소를 둘 이상 V 가 적음 — 모호 · 결속하지 않는다
            vid, extra = owners[0]
            hit: dict = hits.get(case) or {}
            done: bool = ((kind == "old" and o in hit.get("old", [])) or (kind == "add" and case in last["cases_added"])
                          or (kind == "remove" and case in last["cases_removed"])
                          or (kind == "plus" and int(hit.get("add", 0)) >= 1))
            if done:
                executed[(vid, kind, case, verb, o)] = extra
        out.append(_PastWindow(n, opened, open_path.name, executed))
    return out


def _past_reader(project: Path, w: _PastWindow) -> "Callable[[str], bytes | None]":
    """닫힌 창 기준선 읽기(F-B1R-5 · 설계 v2 §1-5) — «없음»(dirty 지운 표식 · head 에 경로 없음)과 «읽지 못함»(head 조회 실패 ·
    dirty b64 누락 · b64 깨짐 · blob 조회 실패)을 가른다. 읽지 못함은 실행 불능이다(쓰려던 증거)."""
    head: str = w.opened["head"]
    dirty: dict = w.opened["dirty"]
    if subprocess.run(["git", "-C", str(project), "cat-file", "-e", f"{head}^{{commit}}"], capture_output=True).returncode != 0:
        raise ToolError(f"창 기록 `{w.where}` 의 head {head[:12]} 를 읽지 못한다 — 닫힌 창 기준선")

    def read(rel: str) -> "bytes | None":
        if rel in dirty:
            entry: object = dirty[rel]
            if not isinstance(entry, dict):
                raise ToolError(f"창 기록 `{w.where}` 의 칸 `dirty[{rel}]` 자료형이 틀리다 — 닫힌 창 기준선")
            if entry.get("b64") is not None:
                try:
                    return base64.b64decode(entry["b64"], validate=True)
                except (ValueError, TypeError):
                    raise ToolError(f"창 기록 `{w.where}` 의 칸 `dirty[{rel}].b64` 를 풀지 못한다 — 닫힌 창 기준선") from None
            if entry.get("sha") is None:
                return None                                  # 창 기준선에서 지워진 파일
            raise ToolError(f"창 기록 `{w.where}` 의 칸 `dirty[{rel}]` 에 b64 가 없다 — 닫힌 창 기준선 원문을 읽지 못한다")
        listed = subprocess.run(["git", "-C", str(project), "ls-tree", "-z", head, "--", rel], capture_output=True)
        if listed.returncode != 0:
            raise ToolError(f"창 기록 `{w.where}` 의 head {head[:12]} 에서 `{rel}` 을 찾지 못한다(git ls-tree 실패)")
        if not listed.stdout:
            return None
        blob = subprocess.run(["git", "-C", str(project), "cat-file", "blob", f"{head}:{rel}"], capture_output=True)
        if blob.returncode != 0:
            raise ToolError(f"창 기록 `{w.where}` 의 head {head[:12]} 에서 `{rel}` 블롭을 읽지 못한다")
        return blob.stdout
    return read


def _past_case_source(data: "bytes | None", name: str, where: str, rel: str) -> "str | None":
    """닫힌 창 기준선의 케이스 원문 — 파일이 없으면 None · 풀거나 파싱하지 못하면 실행 불능."""
    if data is None:
        return None
    try:
        ast.parse(data.decode("utf-8"))
    except (UnicodeDecodeError, SyntaxError, ValueError):
        raise ToolError(f"창 기록 `{where}` 기준선의 `{rel}` 을 파싱하지 못한다 — 닫힌 창 기준선") from None
    return _case_source(data, name)


def _semantic_reds(project: Path, folder: Path, spec: SpecChanges,
                   baseline: "Path | None") -> "tuple[list[str], list[int]]":
    """시험 줄 입장 행 실재 · decision = 동사 · owner/path 파일 = 케이스 파일 · «바뀌는 기대» 원문 실재(기준 판) ·
    다른 BC 편집 목록 ⊆ deps(앞 다섯 갈래) · 대상 BC 밖 → (red, 닫힌 창 기준선으로 본 원소의 창 번호 목록).

    기준 판은 원소마다 고른다(F-B1R-5 · 설계 v2 §1-3): 닫힌 변경 창에서 집행이 결속된 원소(같은 V id · 케이스 · 동사 · 옛 원문 —
    그 창 결속 판에서 모호하지 않고 그 창 마지막 close 가 소비함)는 번호가 가장 큰 그 창의 기준선 — ① 옛 원문 실재 ② add 케이스
    없음 ③ remove 케이스 있음 ④ 기대 추가의 케이스 있음. 그 밖은 `--baseline`(열린 창 open 기록 — 없으면 지금 시험). 쓸 수 있는
    닫힌 창에서 집행된 원소는 지금 명세에 같은 꼴로 남아 있어야 한다(§1-4)."""
    reds: "list[str]" = []
    read = _baseline_reader(project, baseline)
    upto: "int | None" = None
    if baseline is not None:
        um = re.fullmatch(r"w(\d+)-open\.json", Path(baseline).name)
        upto = int(um.group(1)) if um else None
    past: "list[_PastWindow]" = _closed_windows(folder, upto)
    readers: "dict[int, Callable[[str], bytes | None]]" = {}
    routed: "list[int]" = []
    now_elements: "set[tuple]" = set()

    def bound(vid: str, kind: str, case: str, verb: str, o: "str | None", extra: object = None) -> "_PastWindow | None":
        for w in reversed(past):                             # 번호가 가장 큰 창
            key: tuple = (vid, kind, case, verb, o)
            if key in w.executed and (kind != "plus" or w.executed[key] == extra):
                return w
        return None

    def past_read(w: _PastWindow) -> "Callable[[str], bytes | None]":
        if w.n not in readers:
            readers[w.n] = _past_reader(project, w)
        return readers[w.n]
    for v in spec.v:
        for t in v.tests:
            tag: str = f"{v.vid} 시험 {t.case}"
            rows = [r for r in spec.rows if normalize(r.candidate) == normalize(t.row)]
            if not rows:
                reds.append(f"{tag} 입장 행 «{t.row[:60]}» 이 영구 테스트 입장 표에 없다")
            else:
                path: str = t.case.split("::", 1)[0]
                if not any(r.decision == t.verb and r.path == path for r in rows):
                    got = " · ".join(f"{r.decision} {r.path}" for r in rows)
                    reds.append(f"{tag} 입장 행의 decision · owner/path 첫 파일({got})이 시험 줄 `{t.verb}` · `{path}` 와 다르다")
            path, name = t.case.split("::", 1)
            elements: "list[tuple[str, str | None, object]]" = [("old", o, None) for o in t.expect_old]
            if t.verb in ("add", "remove"):
                elements.append((t.verb, None, None))
            elif t.expect_add > 0:
                elements.append(("plus", None, t.expect_add))
            for kind, o, extra in elements:
                now_elements.add((v.vid, kind, t.case, t.verb, o, extra))
            if t.verb == "add":
                w = bound(v.vid, "add", t.case, "add", None)
                if w is not None:
                    routed.append(w.n)
                    if _past_case_source(past_read(w)(path), name, w.where, path) is not None:
                        reds.append(f"{tag} add 케이스가 기준 판에 이미 있다(닫힌 창 w{w.n} 기준선)")
                elif _case_source(read(path), name) is not None:
                    reds.append(f"{tag} add 케이스가 기준 판에 이미 있다")
                continue
            groups: "dict[int, list[str | None]]" = {}       # 창 번호(0 = 지금 기준 판) → 그 판에서 볼 옛 원문(None = 케이스만)
            wins: "dict[int, _PastWindow]" = {}
            for kind, o, extra in elements or [("case", None, None)]:
                w = bound(v.vid, kind, t.case, t.verb, o, extra) if kind != "case" else None
                key = w.n if w is not None else 0
                if w is not None:
                    wins[key] = w
                    routed.append(w.n)
                groups.setdefault(key, []).append(o if kind == "old" else None)
            for key, olds in sorted(groups.items()):
                if key:
                    body = _past_case_source(past_read(wins[key])(path), name, wins[key].where, path)
                    where: str = f"닫힌 창 w{key} 기준선"
                else:
                    body = _case_source(read(path), name)
                    where = "창 기준선" if baseline else "지금 시험"
                if body is None:
                    reds.append(f"{tag} 케이스가 기준 판에 없다({where})")
                    continue
                flat: str = _SPACE.sub("", body)
                for old in olds:
                    if old is not None and _SPACE.sub("", old) not in flat:
                        reds.append(f"{tag} 바뀌는 기대 «{old[:60]}» 원문이 기준 판 케이스에 없다" + (f"({where})" if key else ""))
    for w in past:                                           # §1-4 집행된 원소의 보존
        for (vid, kind, case, verb, o), extra in sorted(w.executed.items(), key=lambda kv: str(kv[0])):
            if (vid, kind, case, verb, o, extra) not in now_elements:
                what: str = (f"«{o}»" if kind == "old" else "add 케이스" if kind == "add" else "remove 케이스" if kind == "remove"
                             else f"기대 추가 {extra}")
                reds.append(f"닫힌 창 w{w.n} 에서 집행된 {vid} 원소({case} · {what})가 지금 명세에 없다 — 집행된 원소는 다시 쓰지 않는다")
    bc: str = _run_bc(folder)
    owned: "dict[str, tuple[str, ...]]" = (_lane_edit_paths(project, bc)
                                           if any(e["kind"] in DEPS_EDIT_KINDS for e in spec.edits) else {})
    for e in spec.edits:
        if e["path"] == f"application/{bc}" or e["path"].startswith(f"application/{bc}/"):
            reds.append(f"다른 BC 편집 `{e['path']}` 가 대상 BC({bc}) 안이다")
        elif e["kind"] in DEPS_EDIT_KINDS and e["kind"] not in owned.get(e["path"], ()):
            got: str = " · ".join(owned.get(e["path"], ())) or "deps 에 없음"
            reds.append(f"다른 BC 편집 `{e['path']} · {e['kind']}` 가 deps 출력과 다르다({got})")
    return reds, routed


def _run_bc(folder: Path) -> str:
    """이 실행의 대상 BC — 실행 줄의 audit plan.md `BC:` 줄."""
    audit_ts: str = _scope(folder)[0]
    return Plan(folder / "audit" / audit_ts).bc


def _g1_decisions(folder: Path) -> "tuple[str | None, dict[str, tuple[str, str, int]], list[str]]":
    """마지막 `## G1 변경 결정 <시각> · 후보 digest <12>` 절 → (후보 digest, V → (결정, 출처, 행), 형식 red).

    실제 기록 줄만 본다(코드 펜스 밖). 절이 없으면 red · 가장 최근 절 머리가 판형 밖이면 실행 불능(앞 절로 내려가지 않는다).
    """
    lines: "list[tuple[int, str]]" = _g1_lines(folder)
    head = _g1_head_at(lines)
    if head is None:
        return None, {}, [f"refactor-scope.md 이번 실행 몫에 `## {G1_DECISION_HEAD} <시각> · 후보 digest <12자>` 절이 없다"]
    start, level, _at, cand = head
    out: "dict[str, tuple[str, str, int]]" = {}
    reds: "list[str]" = []
    for no, ln in lines:
        if no <= start:
            continue
        hm = re.match(r"^(#+)\s", ln)
        if hm and len(hm.group(1)) <= level:
            break
        if not re.match(r"^[-*]?\s*V\d+\b", ln):
            continue
        m = re.match(r"^[-*]?\s*(V\d+)\s*·\s*결정\s*=\s*(바꾼다|안 바꾼다)\s*·\s*출처\s*=\s*(\S.*)$", ln)
        if not m:
            reds.append(f"refactor-scope.md {no}행 G1 결정 줄이 `V<n> · 결정 = 바꾼다 | 안 바꾼다 · 출처 = …` 가 아니다")
            continue
        if m.group(1) in out:
            reds.append(f"refactor-scope.md {no}행 {m.group(1)} 결정 줄이 둘 이상이다")
        out[m.group(1)] = (m.group(2), m.group(3).strip(), no)
        if not m.group(3).strip().startswith(PROXY_FREE):
            reds.append(f"{m.group(1)} G1 결정 출처 `{m.group(3).strip()[:40]}` 가 본인 직접 · 사용자 원문이 아니다(밖 동작 V 는 대리 불가)")
    return cand, out, reds


def _resolution_cells(spec: Path) -> "list[list[str]]":
    table, _body, _reds = _resolution_table(spec)
    return [[r.mid, r.no_raw, r.gist, r.verdict, r.category, r.blocker, r.anchor, r.why] for r in table]


def _slice_rows(text: str) -> "list[list[str]]":
    """명세 `## 슬라이스 계획` 표의 행(칸 목록 · 머리 행 뺌) — 절이 없으면 빈 목록."""
    body, _reds = _heading_section(text.split("\n"), "슬라이스 계획")
    rows: "list[list[str]]" = []
    for _no, ln in body or []:
        s: str = ln.strip()
        if not s.startswith("|") or re.fullmatch(r"\|[\s:|-]*\|", s):
            continue
        cells: "list[str]" = _cells(s)
        if cells and normalize(cells[0]) == "슬라이스":
            continue
        rows.append(cells)
    return rows


def _slice_id(cell: str) -> str:
    return re.sub(r"[*`\s]", "", cell)


def _row_items(cell: str) -> "list[str]":
    """슬라이스 계획의 인수 행 · 내부 행 칸 → 입장 행 원문 목록(정규화 · `·` · `,` · `;` · `<br>` 로 나눔 · 빈 값 뺌)."""
    parts: "list[str]" = re.split(r"\s*(?:·|,|;|<br\s*/?>)\s*", cell)
    return [normalize(p) for p in parts if p.strip() and p.strip() not in _EMPTY]


def _slice_key(cells: "list[str]", drop: "set[str]") -> tuple:
    """슬라이스 계획 행의 대조 키 — 인수 행 · 내부 행(3 · 4번 칸)은 입장 행 목록으로(안 바꾼 V 에만 딸린 행은 `drop`), 그 밖 칸은 글자 그대로."""
    fixed: "tuple[str, ...]" = tuple(c for k, c in enumerate(cells) if k not in (2, 3))
    items: "tuple[tuple[str, ...], ...]" = tuple(tuple(i for i in _row_items(cells[k]) if i not in drop) if k < len(cells) else ()
                                                for k in (2, 3))
    return fixed + items


def _sidecar_path(candidate: Path) -> Path:
    """후보 스냅숏 파일과 1:1 인 곁 파일 `<후보 파일 줄기>-resolution.json`(`*-candidate.json` 글롭에 안 걸린다)."""
    return candidate.with_name(candidate.name[:-len(".json")] + SIDECAR_SUFFIX)


def _expected_applied(cand: dict, removed: "set[str]") -> dict:
    """후보 − (안 바꾼 V 와 그 V 에만 딸린 입장 행 · 다른 BC 편집 줄) — `update_rows` · `remove_rows` 도 안 바꾼 V 에만 딸린 행만 빠진다."""
    out: dict = json.loads(json.dumps(cand, ensure_ascii=False))
    out.pop(ROWS_BINDING, None)                          # 결속 칸은 후보에만 — 지금 스냅숏에는 없다(반영 뒤 표는 바뀐다)
    out["V"] = [v for v in cand["V"] if v["id"] not in removed]
    out["other_bc_edits"] = [e for e in cand["other_bc_edits"] if e["ref"] not in removed]
    keep: "set[str]" = {normalize(t["row"]) for v in out["V"] for t in v["tests"]}
    out["linked_rows"] = [r for r in cand["linked_rows"] if normalize(_cells(r)[0]) in keep]
    before: "list[tuple[str, str, str]]" = [(v["id"], t["row"], t["case"]) for v in cand["V"] for t in v["tests"]]
    after: "list[tuple[str, str, str]]" = [link for link in before if link[0] not in removed]
    for key in ("update_rows", "remove_rows"):
        if key in cand:
            out[key] = [dict(it, v=_row_v(it["row"], it["case"], after)) for it in cand[key]
                        if _row_v(it["row"], it["case"], before) is None or _row_v(it["row"], it["case"], after) is not None]
    return out


def _only_removed_rows(cand: dict, removed: "set[str]") -> "set[str]":
    """안 바꾼 V 에만 딸린 입장 행(candidate 정규화) — 그 행을 가리키는 시험 줄의 V 가 모두 안 바꾼 V 일 때(공유 행은 남는다)."""
    owners: "dict[str, set[str]]" = {}
    for v in cand["V"]:
        for t in v["tests"]:
            owners.setdefault(normalize(t["row"]), set()).add(v["id"])
    return {row for row, vs in owners.items() if vs and vs <= removed}


def _rows_digest(rows: object) -> str:
    """곁 자료 해소 판정 표 `rows` 의 결속 값 — 정규 JSON(ensure_ascii=False · sort_keys · 구분자 최소)의 UTF-8 sha256 hex 64자."""
    return hashlib.sha256(json.dumps(rows, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def _g1_partial_items(before_rows: "list[list[str]]", after_rows: "list[list[str]]",
                      affected: "dict[tuple[str, str], set[int]]") -> "set[str]":
    """G1 이 «부분»으로 만든 항목(B1R 수리 §1-1 조건 1 · 2 · 4) — 후보 곁 자료 행과 지금 표 행(원 행 목록)에서 계산.

    1 후보 행 판정이 모두 정리(해소 · 변경) · 2 지금 행에 정리 행과 `불가` 행이 함께 있음(`_item_class` 결과값을 쓰지 않음) ·
    4 지금 `불가` 행 키 집합 = 그 항목의 영향 행 키 집합(비지 않음) · 후보 · 지금 각각 키 유일 · 행 수와 키 집합이 같음.
    """
    out: "set[str]" = set()
    for mid in sorted({c[0] for c in before_rows} | {c[0] for c in after_rows}):
        cand_m: "list[list[str]]" = [c for c in before_rows if c[0] == mid]
        now_m: "list[list[str]]" = [c for c in after_rows if c[0] == mid]
        cand_keys: "list[tuple[str, str]]" = [(c[0], c[1]) for c in cand_m]
        now_keys: "list[tuple[str, str]]" = [(c[0], c[1]) for c in now_m]
        hit: "set[tuple[str, str]]" = {k for k in affected if k[0] == mid}
        if not cand_m or not hit or len(set(cand_keys)) != len(cand_keys) or len(set(now_keys)) != len(now_keys):
            continue
        if len(cand_m) != len(now_m) or set(cand_keys) != set(now_keys):
            continue
        if not {c[3] for c in cand_m} <= set(CLEANED_VERDICTS):
            continue
        verdicts_now: "set[str]" = {c[3] for c in now_m}
        if not (verdicts_now & set(CLEANED_VERDICTS) and "불가" in verdicts_now):
            continue
        if {(c[0], c[1]) for c in now_m if c[3] == "불가"} != hit:
            continue
        out.add(mid)
    return out


def _applied_table_reds(cand: dict, side: dict, removed: "set[str]", decisions: "dict[str, tuple[str, str, int]]",
                        spec: SpecChanges, bound: bool) -> "tuple[list[str], int]":
    """입장 표 · 슬라이스 계획 · 해소 판정 표를 후보 시점 곁 자료와 대조(§3-4-5 «그 밖은 한 글자도 같은지») → (red, G1 이 부분으로
    만든 항목 수). 해소 판정 표의 예외 하나(B1R 수리 §1-1): G1 이 «부분»으로 만든 항목의 남은 정리 행은 «되돌리지 않는 이유» 칸만
    빈 칸에서 채울 수 있다 — 후보에 곁 자료 결속(`resolution_rows_digest`)이 있고 대조가 섰을 때(`bound`)만 · 옛 후보는 예외 끔."""
    reds: "list[str]" = []
    gone_rows: "set[str]" = _only_removed_rows(cand, removed)
    want_adm: "list[str]" = [r for r in side.get("admission", []) if normalize(_cells(r)[0]) not in gone_rows]
    now_adm: "list[str]" = [r.text for r in spec.rows]
    if want_adm != now_adm:
        left: "list[str]" = [r for r in now_adm if r not in want_adm]
        lost: "list[str]" = [r for r in want_adm if r not in now_adm]
        reds.append(f"반영 대조 다름 — 입장 표(후보 − 안 바꾼 V 에만 딸린 행 {len(gone_rows)}): 남거나 바뀐 행 "
                    f"{' · '.join(_cells(r)[0][:30] for r in left[:3]) or '없음'} · 빠진 행 "
                    f"{' · '.join(_cells(r)[0][:30] for r in lost[:3]) or '없음'}")
    v_slices: "dict[str, set[str]]" = {}
    for v in cand["V"]:
        v_slices.setdefault(_slice_id(v["slice"]), set()).add(v["id"])
    gone_slices: "set[str]" = {s for s, vs in v_slices.items() if vs <= removed}
    want_sl: "list[tuple]" = [_slice_key(c, gone_rows) for c in side.get("slices", []) if _slice_id(c[0]) not in gone_slices]
    now_sl: "list[tuple]" = [_slice_key(c, set()) for c in _slice_rows(spec.text)]
    if want_sl != now_sl:
        want_ids: "list[str]" = [_slice_id(c[0]) for c in want_sl]
        now_ids: "list[str]" = [_slice_id(c[0]) for c in now_sl]                # 키의 첫 칸 = 슬라이스 칸
        reds.append(f"반영 대조 다름 — 슬라이스 계획(후보 − 안 바꾼 V 에만 딸린 슬라이스 {sorted(gone_slices) or '없음'}): "
                    f"기대 {' · '.join(want_ids) or '없음'} · 지금 {' · '.join(now_ids) or '없음'}"
                    f"{' — 남은 슬라이스의 칸이 다르다' if want_ids == now_ids else ''}"
                    f" — 남은 슬라이스 행은 글자 그대로 둔다(목적 칸의 안 바꾼 V 이름도 지우지 않는다 — ④)")
    before_rows: "list[list[str]]" = list(side.get("rows", []))
    after_rows: "list[list[str]]" = _resolution_cells(spec.spec)
    for label, rows_list, tail in (("후보 곁 자료 해소 판정 표", before_rows, " — 새 후보로 재상정한다"),
                                   ("지금 해소 판정 표", after_rows, "")):
        seen: "dict[tuple[str, str], int]" = {}
        for c in rows_list:
            seen[(c[0], c[1])] = seen.get((c[0], c[1]), 0) + 1
        for (mid, no), n in sorted(seen.items()):
            if n > 1:
                reds.append(f"{label} {mid} #{no} 가 둘 이상이다 — 반영 대조를 할 수 없다{tail}")
    before: "dict[tuple[str, str], list[str]]" = {(c[0], c[1]): c for c in before_rows}
    after: "dict[tuple[str, str], list[str]]" = {(c[0], c[1]): c for c in after_rows}
    scope_rel: str = "refactor-scope.md"
    affected: "dict[tuple[str, str], set[int]]" = {}
    for k, c in before.items():
        refs: "set[str]" = set(_v_refs(c[5]) or []) if c[3] == CHANGE_VERDICT else set()
        if refs & removed:
            affected[k] = {decisions[v][2] for v in refs & removed if v in decisions}
    partial: "set[str]" = _g1_partial_items(before_rows, after_rows, affected)
    base_msg: str = f"바뀔 수 있는 행은 안 바꾼 V 요지의 `불가 · {UNAPPROVED_CATEGORY}` 뿐"
    for key in sorted(set(before) | set(after)):
        old, new = before.get(key), after.get(key)
        tag: str = f"{key[0]} #{key[1]}"
        if key not in affected:
            if old == new:
                continue
            if old is None or new is None:                                       # 행 증감 — 줄 단위로 드러낸다
                reds.append(f"해소 판정 표 {tag} 가 후보 뒤 바뀌었다 — "
                            f"{'후보에 없던 행이 생겼다' if old is None else '후보에 있던 행이 빠졌다'} · {base_msg}")
                continue
            only_why: bool = new[:7] == old[:7]
            cond: bool = key[0] in partial and old[7].strip() in _EMPTY             # 조건 1 · 2 · 4(항목) + 3(그 행)
            if cond and bound and only_why and new[7].strip() not in _EMPTY:
                continue                                                          # 받는 변경 하나 — 이유 칸 빈 칸 → 채움
            if cond and bound:
                reds.append(f"해소 판정 표 {tag} 가 후보 뒤 바뀌었다 — G1 이 «부분»으로 만든 항목의 남은 정리 행은 "
                            f"«되돌리지 않는 이유» 칸만 빈 칸에서 채울 수 있다")
            elif cond and only_why:
                reds.append(f"해소 판정 표 {tag} 가 후보 뒤 바뀌었다 — {base_msg} — 이 후보에는 곁 자료 결속이 없다(옛 후보): "
                            f"새 후보로 재상정한다")
            elif only_why:
                reds.append(f"해소 판정 표 {tag} 가 후보 뒤 바뀌었다 — {base_msg} — «되돌리지 않는 이유»는 G1 이 이 항목을 "
                            f"«부분»으로 만들었을 때(후보 = 해소 · 지금 = 부분 · 까닭 = 안 바꾼 V 요지뿐) 빈 칸을 채우는 것만 받는다")
            else:
                reds.append(f"해소 판정 표 {tag} 가 후보 뒤 바뀌었다 — {base_msg}")
            continue
        if new is None:
            reds.append(f"안 바꾼 V 의 요지 {tag} 가 해소 판정 표에서 빠졌다(`불가 · {UNAPPROVED_CATEGORY}` 로 남아야 한다)")
            continue
        why: "list[str]" = []
        if new[:3] != old[:3]:                                                    # type: ignore[index]
            why.append("항목 · 요지 번호 · 요지 원문이 후보와 다르다")
        if new[3] != "불가" or new[4] != UNAPPROVED_CATEGORY:
            why.append(f"판정 · 범주가 `불가 · {UNAPPROVED_CATEGORY}` 가 아니다")
        where, dash, phrase = new[5].partition("—")
        locs = [_parse_location(t) for t in _locations(where)]
        lines: "set[int]" = affected[key]
        if (len(locs) != 1 or locs[0] is None or locs[0][0] != scope_rel or locs[0][1] != locs[0][2]
                or locs[0][1] not in lines or not dash or phrase.strip() in _EMPTY):
            why.append(f"막는 것이 그 G1 변경 결정 줄 `refactor-scope.md:{'|'.join(map(str, sorted(lines))) or '?'} — <한 구>` 가 아니다")
        if new[6].strip() not in _EMPTY or new[7].strip() not in _EMPTY:
            why.append("처방 앵커 · 되돌리지 않는 이유는 `—` 로 둔다")
        if why:
            reds.append(f"안 바꾼 V 의 요지 {tag} — {' · '.join(why)}")
    return reds, (len(partial) if bound else 0)


def _applied_reds(folder: Path, cand_path: Path, cand: dict, cand_digest: str, now: dict,
                  spec: SpecChanges) -> "tuple[list[str], int]":
    """반영 대조(§3-4-5) — 지금 = 후보 − 안 바꾼 V 몫(스냅숏 · 입장 표 · 슬라이스 계획) · 해소 판정 표에서 바뀐 행은
    안 바꾼 V 요지의 `불가 · 변경 미승인`(항목 · 요지 원문 그대로 · 막는 것 = 그 G1 결정 줄)과 G1 이 «부분»으로 만든 항목의
    남은 정리 행 «되돌리지 않는 이유»(빈 칸 → 채움) 뿐 → (red, G1 이 부분으로 만든 항목 수).

    후보 스냅숏에 결속 칸 `resolution_rows_digest` 가 있으면 곁 자료 `rows` 의 sha256 을 다시 계산해 대조한다 — 다르면 실행 불능
    (곁 자료를 고치지 말고 새 후보로 재상정). 칸이 없으면(옛 후보) 곁 자료를 믿거나 보충하지 않고 위 예외를 끈다."""
    side_path: Path = _sidecar_path(cand_path)
    try:
        side: dict = json.loads(_read(side_path))
    except ValueError:
        raise ToolError(f"후보 곁 자료 `{side_path.name}` 가 JSON 이 아니다") from None
    if side.get("candidate") != cand_digest:
        raise ToolError(f"후보 곁 자료 `{side_path.name}` 의 후보 digest {side.get('candidate')} ≠ 후보 스냅숏 {cand_digest}")
    reds: "list[str]" = []
    dcand, decisions, dreds = _g1_decisions(folder)
    reds += dreds
    if dcand is not None and dcand != cand_digest:
        reds.append(f"마지막 `{G1_DECISION_HEAD}` 절의 후보 digest {dcand} ≠ 대조 후보 {cand_digest}")
    bound: bool = ROWS_BINDING in cand
    if bound and (not isinstance(cand[ROWS_BINDING], str) or _rows_digest(side.get("rows")) != cand[ROWS_BINDING]):
        raise ToolError(f"후보 곁 자료의 해소 판정 표가 후보 결속 {str(cand[ROWS_BINDING])[:12]} 와 다르다 — 곁 자료를 고치지 말고 "
                        f"새 후보로 재상정한다")
    removed: "set[str]" = {v for v, (d, _s, _n) in decisions.items() if d == "안 바꾼다"}
    unknown: "list[str]" = sorted(set(decisions) - {v["id"] for v in cand["V"]}, key=lambda k: int(k[1:]))
    if unknown:
        reds.append(f"G1 결정 줄의 {' · '.join(unknown)} 이 후보 스냅숏에 없다")
    expected: dict = _expected_applied(cand, removed)
    for key in sorted(set(expected) | set(now)):
        if expected.get(key) != now.get(key):
            reds.append(f"반영 대조 다름 — `{key}`(후보 − 안 바꾼 V {sorted(removed) or '없음'} 과 지금 승인판이 다르다)")
    table_reds, partial = _applied_table_reds(cand, side, removed, decisions, spec, bound)
    return reds + table_reds, partial


def _gate_changes_reds(folder: Path, spec: SpecChanges) -> "list[str]":
    """`changes --gate` — G1 결정 줄과 후보 · V 표 · 해소 표 양방향 정합: 후보의 밖 동작 V 집합 = 결정 줄 집합 · `바꾼다` V 는
    지금 목록에 있다 · `안 바꾼다` V 는 없고 그 요지가 `불가 · 변경 미승인` · 지금 밖 동작 V 마다 `바꾼다` · V 근거 = `변경` 행."""
    reds: "list[str]" = []
    cand_digest, decisions, dreds = _g1_decisions(folder)
    reds += dreds
    cand: "dict | None" = None
    if cand_digest is not None:
        try:
            cand = load_candidate(folder, cand_digest)
        except ToolError as exc:
            reds.append(str(exc))
    if cand is not None:
        outward: "set[str]" = {v["id"] for v in cand["V"] if "밖 동작" in v["kinds"]}
        for vid in sorted(outward - set(decisions), key=lambda k: int(k[1:])):
            reds.append(f"후보의 밖 동작 {vid} 에 G1 결정 줄이 없다")
        for vid in sorted(set(decisions) - outward, key=lambda k: int(k[1:])):
            reds.append(f"G1 결정 줄 {vid} 이 후보의 밖 동작 V 가 아니다")
    table, _body, _treds = _resolution_table(spec.spec)
    rows: "dict[tuple[str, int], ResolutionRow]" = {(r.mid, r.no): r for r in table}
    for v in spec.v:
        dec = decisions.get(v.vid)
        if "밖 동작" in v.kinds and (dec is None or dec[0] != "바꾼다"):
            reds.append(f"{v.vid} 밖 동작 V 에 G1 결정 `바꾼다` 줄이 없다")
        m = re.fullmatch(r"(M\d+) #(\d+)", v.basis)
        r = rows.get((m.group(1), int(m.group(2)))) if m else None
        if r is None or r.verdict != CHANGE_VERDICT or v.vid not in (_v_refs(r.blocker) or []):
            reds.append(f"{v.vid} 근거 {v.basis} 가 이 V 를 가리키는 해소 판정 표 `변경` 행이 아니다")
    for vid, (dec, _src, _no) in sorted(decisions.items(), key=lambda kv: int(kv[0][1:])):
        if dec == "바꾼다":
            if vid not in spec.vids:
                reds.append(f"{vid} 는 G1 결정 `바꾼다` 인데 바뀌는 것 목록에 없다")
            continue
        if vid in spec.vids:
            reds.append(f"{vid} 는 G1 결정 `안 바꾼다` 인데 바뀌는 것 목록에 남아 있다(architect 반영)")
        basis: "str | None" = next((x["basis"] for x in (cand or {}).get("V", []) if x["id"] == vid), None)
        m = re.fullmatch(r"(M\d+) #(\d+)", basis or "")
        r = rows.get((m.group(1), int(m.group(2)))) if m else None
        if r is None or r.verdict != "불가" or r.category != UNAPPROVED_CATEGORY:
            reds.append(f"{vid} 는 G1 결정 `안 바꾼다` 인데 그 요지({basis or '후보에 없음'})가 `불가 · {UNAPPROVED_CATEGORY}` 가 아니다")
    for r in table:
        for vid in (_v_refs(r.blocker) or []) if r.verdict == CHANGE_VERDICT else []:
            if vid not in spec.vids:
                reds.append(f"해소 판정 표 {r.mid} #{r.no_raw} 변경 행의 {vid} 가 바뀌는 것 목록에 없다")
    return reds


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _write_candidate(folder: Path, snap: dict, digest: str, spec: SpecChanges, rows: "list[list[str]]") -> Path:
    """후보 스냅숏 `g1/<UTC>-candidate.json` + 곁 자료 `g1/<UTC>-candidate-resolution.json`(해소 판정 표 · 입장 표 · 슬라이스
    계획 — 후보 파일과 1:1) — 둘 다 덮어쓰지 않는다(있으면 실행 불능). `snap` 은 결속 칸을 이미 담은 후보 스냅숏 · `digest` 는 그
    전체의 digest · 곁 자료 `rows` 는 결속을 계산한 그 `rows` 그대로(여기서 칸을 뒤늦게 더하지 않는다). 입장 표 · 슬라이스 계획
    곁 자료는 결속 밖이다."""
    base: Path = folder / G1_DIR
    base.mkdir(parents=True, exist_ok=True)
    stamp: str = _utc_stamp()
    path: Path = base / f"{stamp}{CANDIDATE_SUFFIX}"
    k: int = 2
    while path.exists() or _sidecar_path(path).exists():
        path = base / f"{stamp}-{k}{CANDIDATE_SUFFIX}"
        k += 1
    side: Path = _sidecar_path(path)
    data: dict = {"version": 1, "candidate": digest, "candidate_file": path.name,
                  "rows": rows, "admission": [r.text for r in spec.rows],
                  "slices": _slice_rows(spec.text)}
    with path.open("x", encoding="utf-8") as fh:
        fh.write(json.dumps(snap, ensure_ascii=False, sort_keys=True, indent=1) + "\n")
    try:
        with side.open("x", encoding="utf-8") as fh:
            fh.write(json.dumps(data, ensure_ascii=False, sort_keys=True, indent=1) + "\n")
    except FileExistsError:
        raise ToolError(f"후보 곁 자료 `{side.name}` 가 이미 있다 — 덮어쓰지 않는다") from None
    return path


def cmd_changes(project: Path, folder: Path, mode: str, applied: "Path | None", baseline: "Path | None") -> int:
    """`changes <폴더> [--candidate | --applied <후보> | --gate] [--baseline <창 open 기록>]`.

    `--candidate` 의 후보 스냅숏 = 지금 스냅숏 + 결속 칸 `resolution_rows_digest`(곁 자료 해소 판정 표 `rows` 의 정규 JSON sha256 —
    도구의 무결성 칸 · 승인 후보의 내용 목록 아님) · 후보 digest 는 그 후보 스냅숏 전체로 센다. 지금 스냅숏 · `--gate` 최종 digest ·
    공개 함수 `changes_snapshot` 에는 그 칸이 없다."""
    spec: SpecChanges = SpecChanges(folder)
    reds: "list[str]" = list(spec.reds)
    semantic, routed = _semantic_reds(project, folder, spec, baseline)
    reds += semantic
    tail: str = ""
    if mode == "gate":
        _no_standing(_scope(folder)[4], "changes --gate")
        reds += _gate_changes_reds(folder, spec)
    if mode in ("candidate", "applied", "gate"):
        snap: dict = spec.snapshot(folder)
        digest: str = snapshot_digest(snap)
        if mode == "applied":
            cand: dict = json.loads(_read(applied))  # type: ignore[arg-type]
            cand_digest: str = snapshot_digest(cand)
            applied_reds, partial = _applied_reds(folder, applied, cand, cand_digest, snap, spec)  # type: ignore[arg-type]
            reds += applied_reds
            tail = f" · G1 이 부분으로 만든 항목 {partial} · 후보 {cand_digest} → 지금 {digest}"
        elif mode == "gate":
            tail = f" · 최종 digest {digest}"
        elif not reds:
            rows: "list[list[str]]" = _resolution_cells(spec.spec)                  # ⓐ 한 번 구한 rows
            cand_snap: dict = dict(snap, **{ROWS_BINDING: _rows_digest(rows)})       # ⓑ 결속 칸
            cand_digest = snapshot_digest(cand_snap)                                # ⓒ 후보 스냅숏 전체 digest
            path: Path = _write_candidate(folder, cand_snap, cand_digest, spec, rows)  # ⓓ 같은 rows 로 곁 자료
            tail = f" · 후보 digest {cand_digest} → {path}"
    for w in reds:
        print(f"  red: {w}")
    retained: int = sum(1 for r in spec.rows if r.decision == "retain")
    if mode != "applied" and retained and not any(_reorg(r) for r in spec.rows):
        print(f"  알림: retain 행 {retained} 가운데 재조직 표지 0 — 0F 허용 파일 없음(candidate 칸에 재조직 낱말이 있어야 재조직 행이다)")
    kinds: "dict[str, int]" = {k: sum(1 for v in spec.v if k in v.kinds) for k in V_KINDS}
    ops: int = sum(len(v.ops) for v in spec.v)
    expect: int = sum(len(t.expect_old) for v in spec.v for t in v.tests)
    base_text: str = " · 기준선 창 open 기록" if baseline else ""
    if routed:
        base_text += f" · 닫힌 창 기준선 {len(routed)}({', '.join(f'w{n}' for n in sorted(set(routed)))})"
    updates: "list[dict]" = spec.update_rows()
    removes: "list[dict]" = spec.decision_rows(REMOVE_DECISION)
    print(f"요약: changes V {len(spec.v)}({' · '.join(f'{k} {n}' for k, n in kinds.items())}) · 시험 줄 "
          f"{sum(len(v.tests) for v in spec.v)} · 바뀌는 기대 {expect} · 연산 {ops} · 다른 BC 편집 {len(spec.edits)} · "
          f"retain 재조직 {len(spec.retain)} · update 케이스 {len(updates)}(V 밖 {sum(1 for u in updates if u['v'] is None)})"
          f" · remove 케이스 {len(removes)}(V 밖 {sum(1 for u in removes if u['v'] is None)})"
          f"{base_text} · red {len(reds)}{' · ' + mode if mode != 'check' else ''}"
          f"{tail if not reds or mode == 'applied' else ''}")
    return EXIT_RED if reds else EXIT_OK


# ── deps(BC 경계 규칙 — 의존 그래프 · SCC · 받는 쪽 · HTTP 소비 · 레인 겹침) ──────────────
# 출발 재료: workspace/plan/2026-10-03-refactor-definition/bc-map.py(읽기 전용 재현 스크립트)의 참조 수집 · Tarjan.
# 다른 작업 트리에서는 git status · 작업 트리 대 diff 를 돌리지 않는다(그 트리 index 를 쓸 수 있다) — 커밋 개체 읽기와
# 파일 읽기만 · 모든 git 호출은 GIT_OPTIONAL_LOCKS=0.

PROD_CATS: "tuple[str, ...]" = ("ohs_acl", "ohs_wiring", "ohs_bypass", "event", "platform_auth", "internal")
WINDOW_SPOTS: "frozenset[str]" = frozenset({"ohs", "ohs_contract", "published_event"})   # 창구 · 이벤트
_DOTTED: "re.Pattern[str]" = re.compile(r"\bapplication\.([a-z_][a-z0-9_]*)((?:\.[A-Za-z_][A-Za-z0-9_]*)*)")
_SLASH: "re.Pattern[str]" = re.compile(r"\bapplication/([a-z_][a-z0-9_]*)((?:/[A-Za-z0-9_.\-]+)*)")
_LABEL_MODEL: "re.Pattern[str]" = re.compile(r"^([a-z_][a-z0-9_]*)\.([A-Za-z][A-Za-z0-9_]*)$")
_MIGRATION_NAME: "re.Pattern[str]" = re.compile(r"^(\d{4}_\w+|__first__|__latest__)$")
_URL_SEG_END: str = r"(?![A-Za-z0-9\-._~%])"                # 경로 조각 끝 — 뒤는 `/` · `?` · `#` · URL 문자열 끝(조각 글자 아님)
_URL_TOKEN_STOP: str = " \t\"'`<>()[],;"                     # 계획된 소비 표기용 — URL 문자열 앞뒤 경계


def _static_prefix(raw: str) -> str:
    """`api_controller` 접두 → 경로 변수(`{…}` · `<…>`) 앞까지의 고정 조각 `/a/b` — 비었거나 `/` 뿐이면 빈 글."""
    head: "list[str]" = []
    for seg in raw.strip("/").split("/"):
        if not seg or "{" in seg or "<" in seg:
            break
        head.append(seg)
    return "/" + "/".join(head) if head else ""


def _end_name(node: ast.AST) -> str:
    return getattr(node, "id", getattr(node, "attr", ""))


API_SKELETON_FILES: "frozenset[str]" = frozenset({"api_router.py", "bc_error_schema.py"})   # 정본 트리 `api/` 바로 밑 뼈대
_ROUTE_SIGN: "re.Pattern[str]" = re.compile(r"\bRouter\(|\b(?:NinjaAPI|NinjaExtraAPI)\(|\.add_router\(|\.add_api_operation\(|api_controller")
_ROUTE_DECORATORS: "frozenset[str]" = frozenset({"get", "post", "put", "patch", "delete", "api_operation", "http_get", "http_post",
                                                 "http_put", "http_patch", "http_delete", "api_view"})


def _function_routes(tree: ast.Module) -> "list[int]":
    """모듈 수준 함수의 경로 데코레이터(`@router.get(…)` · `@http_get(…)` · `@api_view(…)`) 줄 — api_controller 클래스 메서드는 아니다."""
    return [st.lineno for st in tree.body if isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef))
            and any(isinstance(d, ast.Call) and _end_name(d.func) in _ROUTE_DECORATORS for d in st.decorator_list)]


def _json_strings(obj: object) -> "list[str]":
    """파싱한 JSON 값의 문자열 전부(키 · 값 · 재귀)."""
    out: "list[str]" = []
    stack: "list[object]" = [obj]
    while stack:
        cur = stack.pop()
        if isinstance(cur, str):
            out.append(cur)
        elif isinstance(cur, dict):
            for k, v in cur.items():
                out.append(str(k))
                stack.append(v)
        elif isinstance(cur, list):
            stack.extend(cur)
    return out
DEPS_STOP_EXIT: int = EXIT_RED


def _git_ro(project: Path, *args: str) -> str:
    env: "dict[str, str]" = {**os.environ, "GIT_OPTIONAL_LOCKS": "0"}
    return subprocess.run(["git", "-C", str(project), *args], capture_output=True, text=True, check=True, env=env).stdout


def _spot(parts: "tuple[str, ...]") -> str:
    """BC 안 자리 — check-context-isolation._spot 과 같은 판정(+ django_<bc> 세분 · 시험 쪽)."""
    if not parts:
        return "bc_root"
    head: str = parts[0]
    if parts[-1] == "conftest.py" or parts[-1].startswith("test_") or head in ("test", "tests"):
        return "test"
    if head in ("__init__.py", "__init__"):
        return "bc_root"
    if head == "driving_layer":
        sub: str = parts[1] if len(parts) > 1 else ""
        if sub == "open_host_service":
            return "ohs_contract" if "contract" in parts else "ohs"
        return sub if sub in ("api", "cron_job", "event_subscription") else "driving"
    if head == "application_layer":
        return "app_port" if len(parts) > 1 and parts[1] == "port" else "app"
    if head == "domain_layer":
        return "domain"
    if head == "driven_layer":
        sub = parts[1] if len(parts) > 1 else ""
        if sub.startswith("django_"):
            return "migration" if "migrations" in parts else "django"
        return "acl" if "anticorruption_layer" in parts else "driven"
    if head == "composition_root":
        return "composition"
    if head == "published_event":
        return "published_event"
    return "other"


def _classify(src_spot: str, dst_spot: str, kind: str) -> str:
    if src_spot == "test":
        return "test"
    if src_spot == "migration":
        return "migration"
    if kind == "auth_user_model":
        return "platform_auth"
    if dst_spot == "published_event":
        return "event"
    if dst_spot in ("ohs", "ohs_contract"):
        return "ohs_acl" if src_spot == "acl" else "ohs_wiring" if src_spot == "composition" else "ohs_bypass"
    return "internal"


def _is_test_path(rel: str) -> bool:
    parts: "list[str]" = rel.split("/")
    return (parts[-1] == "conftest.py" or parts[-1].startswith("test_") or parts[-1].endswith("_test.py")
            or any(p in ("test", "tests") for p in parts[:-1]))


def _module_of(rel: str) -> str:
    p: "list[str]" = rel[:-3].split("/")
    return ".".join(p[:-1] if p[-1] == "__init__" else p)


class DepsScan:
    """저장소 파일(추적 + 미추적 · 무시 제외 · 점 폴더 제외)의 교차 BC 참조 · HTTP 소비 · 그래프."""

    def __init__(self, project: Path) -> None:
        self.project: Path = project
        raw: "list[str]" = [p for p in _git_ro(project, "ls-files", "-co", "--exclude-standard", "-z").split("\0") if p]
        self.files: "list[str]" = sorted({p for p in raw if not p.startswith(".") and "/__pycache__/" not in f"/{p}"
                                          and (project / p).is_file()})
        self.py: "list[str]" = [f for f in self.files if f.endswith(".py")]
        self.bcs: "list[str]" = sorted({f.split("/")[1] for f in self.py if f.startswith("application/") and f.count("/") >= 2})
        self._texts: "dict[str, str | None]" = {}
        self.modules: "set[str]" = set()
        for f in self.py:
            parts = _module_of(f).split(".")
            for i in range(1, len(parts) + 1):
                self.modules.add(".".join(parts[:i]))
        self.labels: "dict[str, str]" = self._labels()
        self.auth_label: "str | None" = self._auth_label()
        self.refs: "list[dict]" = []
        self.parse_errors: "list[str]" = []
        self.imports: "dict[str, set[str]]" = {}           # 파일 → 참조 모듈(같은 주인 포함 — 받는 쪽 시험 계산)
        for f in self.py:
            self._scan(f)
        self.prefixes: "dict[str, set[str]]"                  # BC → api_controller 고정 접두(`/thing`) — 마운트는 결속하지 않는다
        self.prefixes, reasons = self._api_prefixes()
        for bc, whys in self._surface_blind().items():      # 표면마다 — 접두를 찾은 컨트롤러가 따로 있어도 남는다
            known: "list[str]" = reasons.setdefault(bc, [])
            known.extend([w for w in whys if w not in known])
        self.url_patterns: "dict[str, re.Pattern[str]]" = {   # BC → 경로 조각 경계에서 `/<접두>` 로 시작하는 조각
            bc: re.compile("(?:" + "|".join(re.escape(p) for p in sorted(ps, key=len, reverse=True)) + ")" + _URL_SEG_END)
            for bc, ps in self.prefixes.items()}
        self.unread: "list[str]" = []                         # 소비 스캔에서 읽기 · 디코딩 · 파싱 못 한 파일
        self.http: "list[dict]" = self._http_consumers()
        if self.unread:
            more: str = " …" if len(self.unread) > 3 else ""
            for bc in self.prefixes:
                reasons.setdefault(bc, []).append(f"소비 파일 읽기 실패 {len(self.unread)}({' · '.join(self.unread[:3])}{more})")
        self.http_blind_reasons: "dict[str, list[str]]" = {bc: ws for bc, ws in reasons.items() if ws}
        self.http_blind_why: "dict[str, str]" = {bc: " · ".join(ws) for bc, ws in self.http_blind_reasons.items()}
        self.http_blind: "set[str]" = set(self.http_blind_why)

    # 재료 -----------------------------------------------------------------
    def _text(self, rel: str) -> "str | None":
        if rel not in self._texts:
            try:
                self._texts[rel] = (self.project / rel).read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                self._texts[rel] = None
        return self._texts[rel]

    def _labels(self) -> "dict[str, str]":
        labels: "dict[str, str]" = {}
        for f in self.py:
            if not (f.startswith("application/") and f.endswith("/apps.py")):
                continue
            text = self._text(f)
            try:
                tree = ast.parse(text or "")
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                if isinstance(node, (ast.Assign, ast.AnnAssign)):
                    tgt = node.targets[0] if isinstance(node, ast.Assign) else node.target
                    if isinstance(tgt, ast.Name) and tgt.id == "label" and isinstance(node.value, ast.Constant) \
                            and isinstance(node.value.value, str):
                        labels[node.value.value] = f.split("/")[1]
        for bc in self.bcs:
            labels.setdefault(bc, bc)
        return labels

    def _auth_label(self) -> "str | None":
        for f in self.py:
            if f.startswith("application/") or "settings" not in f:
                continue
            m = re.search(r"AUTH_USER_MODEL[^=\n]*=\s*[\"']([a-z_]+)\.", self._text(f) or "")
            if m:
                return m.group(1)
        return None

    def _owner(self, rel: str) -> "tuple[str | None, str]":
        parts: "list[str]" = rel.split("/")
        if parts[0] == "application" and len(parts) >= 3 and parts[1] in self.bcs:
            return parts[1], _spot(tuple(parts[2:]))
        return None, parts[0] if len(parts) > 1 else "<root>"

    def _scan(self, f: str) -> None:
        text = self._text(f)
        try:
            tree = ast.parse(text if text is not None else "")
        except SyntaxError as exc:
            self.parse_errors.append(f"{f}: {exc.msg}")
            return
        if text is None:
            self.parse_errors.append(f"{f}: 읽기 실패")
            return
        parts: "list[str]" = f.split("/")
        src_bc, src_spot = self._owner(f)
        src_owner: str = src_bc or f"@{src_spot}"
        docs: "set[int]" = set()                           # 문장 자리의 문자열(docstring · 주석 대용)은 참조가 아니다
        for holder in ast.walk(tree):
            body = getattr(holder, "body", None)
            for st in body if isinstance(body, list) else []:
                if isinstance(st, ast.Expr) and isinstance(st.value, ast.Constant) and isinstance(st.value.value, str):
                    docs.add(id(st.value))
        mods: "set[str]" = self.imports.setdefault(f, set())

        def emit(node: ast.AST, kind: str, tp: "list[str]") -> None:
            """다른 BC 를 가리키는 참조만 싣는다(주인이 같으면 버린다) — BC 밖 파일이 부르면 `surface_in`."""
            if not (tp and tp[0] == "application" and len(tp) >= 2 and tp[1] in self.bcs) or tp[1] == src_owner:
                return
            dst_spot: str = _spot(tuple(tp[2:]))
            category: str = _classify(src_spot, dst_spot, kind) if src_bc else "surface_in"
            self.refs.append({"file": f, "line": getattr(node, "lineno", 0), "src": src_owner, "src_spot": src_spot,
                              "dst": tp[1], "dst_spot": dst_spot, "kind": kind, "category": category,
                              "target": ".".join(tp)})

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for a in node.names:
                    mods.add(a.name)
                    emit(node, "import", a.name.split("."))
            elif isinstance(node, ast.ImportFrom):
                if node.level:
                    pkg: "list[str]" = parts[:-1]
                    up: int = node.level - 1
                    if up > len(pkg):
                        continue
                    base: "list[str]" = pkg[:len(pkg) - up] + (node.module.split(".") if node.module else [])
                else:
                    base = (node.module or "").split(".")
                for a in node.names:
                    cand: "list[str]" = base + [a.name]
                    tp = cand if ".".join(cand) in self.modules else base
                    mods.add(".".join(tp))
                    emit(node, "import", tp)
            elif isinstance(node, ast.Constant) and isinstance(node.value, str) and id(node) not in docs:
                s: str = node.value
                for m in _DOTTED.finditer(s):
                    if m.group(1) in self.bcs:
                        tp = ["application", m.group(1)] + [x for x in m.group(2).split(".") if x]
                        mods.add(".".join(tp))
                        emit(node, "string_dotted", tp)
                for m in _SLASH.finditer(s):
                    if m.group(1) in self.bcs:
                        emit(node, "string_path", ["application", m.group(1)]
                             + [x.removesuffix(".py") for x in m.group(2).split("/") if x])
                lm = _LABEL_MODEL.match(s)
                if lm and lm.group(1) in self.labels and (src_spot == "migration" or lm.group(2)[0].isupper()):
                    lab: str = self.labels[lm.group(1)]
                    emit(node, "model_label", ["application", lab, "driven_layer", f"django_{lab}", "models"])
            elif isinstance(node, ast.Call) and getattr(node.func, "attr", getattr(node.func, "id", "")) == "get_model" \
                    and len(node.args) >= 2 and isinstance(node.args[0], ast.Constant) and node.args[0].value in self.labels:
                lab = self.labels[node.args[0].value]
                emit(node, "model_label", ["application", lab, "driven_layer", f"django_{lab}", "models"])
            elif isinstance(node, ast.Tuple) and len(node.elts) == 2 and all(
                    isinstance(e, ast.Constant) and isinstance(e.value, str) for e in node.elts):
                lab0, name = node.elts[0].value, node.elts[1].value  # type: ignore[attr-defined]
                if lab0 in self.labels and _MIGRATION_NAME.match(name):
                    lab = self.labels[lab0]
                    emit(node, "migration_dep", ["application", lab, "driven_layer", f"django_{lab}", "migrations"])
            elif self.auth_label and ((isinstance(node, ast.Attribute) and node.attr == "AUTH_USER_MODEL")
                                      or (isinstance(node, ast.Call) and isinstance(node.func, (ast.Name, ast.Attribute))
                                          and getattr(node.func, "id", getattr(node.func, "attr", "")) == "get_user_model")):
                lab = self.labels.get(self.auth_label, self.auth_label)
                emit(node, "auth_user_model", ["application", lab, "driven_layer", f"django_{lab}", "models"])

    def _surface_blind(self) -> "dict[str, list[str]]":
        """API 표면마다(설계 :1275) — api_controller 밖 API 표면(urls.py path() · Router() · NinjaAPI · add_router · 함수형 경로
        데코레이터) · 컨트롤러 없는 API 영역(`driving_layer/api/<영역>/` · `webhook/<공급자>/`) · api_controller 없는 BC 의 API 파일 ·
        읽기 · 파싱 못 한 API 표면 파일(원문에 api_controller 가 없어도) → BC 마다 사유 목록. 접두를 찾은 컨트롤러가 따로 있어도 남는다.

        영역은 코드가 있는 `.py` 가 하나라도 있을 때만 센다 — «코드 없음»은 이름이 `__init__.py` 이고 AST 몸이 비었거나 docstring 식
        하나뿐인 파일뿐이다(0바이트 · 공백 · 주석만 · docstring 만 — 정본 트리의 빈 패키지 표지). `__init__.py` 라도 import · 대입 ·
        def 가 있으면 코드 있음 · `__init__.py` 아닌 `.py` 는 비어 있어도 코드 있는 파일로 친다.

        `driving_layer/api/` 바로 밑의 정본 뼈대 두 이름(`api_router.py` · `bc_error_schema.py`)은 경로를 만들지 않으므로 그것만으로는
        «api_controller 없는 API 표면»이 아니다(낱개 판정 — Router( · NinjaAPI( · add_router · 함수형 경로 데코레이터 · 읽기 · 파싱
        실패 — 은 그대로 걸린다). 컨트롤러 없는 BC 의 `api_router.py` 가 인자 있는 `register_controllers(…)` 를 부르면 밖에서
        들여온 컨트롤러를 붙이는 것이므로 관찰 못 함이다."""
        out: "dict[str, list[str]]" = {}
        areas: "dict[tuple[str, str], list[bool]]" = {}      # (BC, 영역) → [api_controller 있음, 코드 있는 .py 있음]
        ctrl_bcs: "set[str]" = set()
        api_bcs: "set[str]" = set()
        registrars: "dict[str, str]" = {}                    # BC → `api_router.py` 의 인자 있는 register_controllers 자리
        for f in self.py:
            parts = f.split("/")
            if parts[0] != "application" or len(parts) < 3:
                continue
            bc: str = parts[1]
            text: "str | None" = self._text(f)
            in_api: bool = "/driving_layer/api/" in f
            if not (in_api or parts[-1] == "urls.py" or (text is not None and _ROUTE_SIGN.search(text))):
                continue
            whys: "list[str]" = out.setdefault(bc, [])
            if text is None:
                whys.append(f"{f} API 표면 파일 읽기 실패")
                continue
            try:
                tree = ast.parse(text)
            except SyntaxError:
                whys.append(f"{f} API 표면 파일 파싱 실패")
                continue
            has_ctrl: bool = "api_controller" in text
            ctrl_bcs |= {bc} if has_ctrl else set()
            rest: "list[str]" = f.split("/driving_layer/api/", 1)[1].split("/") if in_api else []
            if in_api and parts[-1] != "__init__.py" and not (len(rest) == 1 and rest[0] in API_SKELETON_FILES):
                api_bcs.add(bc)
            if rest == ["api_router.py"]:
                site = next((n.lineno for n in ast.walk(tree) if isinstance(n, ast.Call)
                             and _end_name(n.func) == "register_controllers" and (n.args or n.keywords)), None)
                if site is not None:
                    registrars[bc] = f"{f}:{site}"
            if parts[-1] == "urls.py" and re.search(r"\b(?:re_)?path\(", text):
                whys.append(f"{f} 의 path() — api_controller 밖 API 표면")
            if re.search(r"\bRouter\(", text):
                whys.append(f"{f} 의 Router() — api_controller 밖 API 표면")
            if re.search(r"\b(?:NinjaAPI|NinjaExtraAPI)\(|\.add_router\(|\.add_api_operation\(", text):
                whys.append(f"{f} 의 NinjaAPI · add_router — api_controller 밖 API 표면")
            routes: "list[int]" = _function_routes(tree)
            if routes:
                whys.append(f"{f}:{routes[0]} 함수형 경로 데코레이터 — api_controller 밖 API 표면")
            if len(rest) >= 2:
                area: str = f"webhook/{rest[1]}" if rest[0] == "webhook" and len(rest) >= 3 else rest[0]
                codeless: bool = parts[-1] == "__init__.py" and (not tree.body or (
                    len(tree.body) == 1 and isinstance(tree.body[0], ast.Expr)
                    and isinstance(tree.body[0].value, ast.Constant) and isinstance(tree.body[0].value.value, str)))
                state: "list[bool]" = areas.setdefault((bc, area), [False, False])
                state[0] = state[0] or has_ctrl
                state[1] = state[1] or not codeless
        for (bc, area), (ok, code) in sorted(areas.items()):
            if code and not ok:
                out.setdefault(bc, []).append(f"application/{bc}/driving_layer/api/{area}/ — 컨트롤러 없는 API 영역")
        for bc in sorted(api_bcs - ctrl_bcs):
            out.setdefault(bc, []).append("api_controller 없는 API 표면")
        for bc, site in sorted(registrars.items()):
            if bc not in ctrl_bcs:
                out.setdefault(bc, []).append(f"{site} registrar 가 등록하는 컨트롤러의 접두를 이 BC 에서 못 찾음")
        return {bc: ws for bc, ws in out.items() if ws}

    def _api_prefixes(self) -> "tuple[dict[str, set[str]], dict[str, list[str]]]":
        """`api_controller("<접두>")` → BC 마다 고정 접두 · 접두를 못 읽거나 비었거나 `/` 뿐인 컨트롤러가 있는 BC → 사유(설계 :1275)."""
        prefixes: "dict[str, set[str]]" = {}
        blind: "dict[str, list[str]]" = {}
        for f in self.py:
            parts = f.split("/")
            text = self._text(f) or ""
            if parts[0] != "application" or len(parts) < 3 or "api_controller" not in text:
                continue
            bc = parts[1]
            try:
                tree = ast.parse(text)
            except SyntaxError:
                blind.setdefault(bc, []).append(f"{f} 를 파싱 못 함(api_controller 접두 모름)")
                continue
            called: "set[int]" = set()
            for node in ast.walk(tree):
                if not (isinstance(node, ast.Call) and _end_name(node.func) == "api_controller"):
                    continue
                called.add(id(node.func))
                arg = node.args[0] if node.args else next((k.value for k in node.keywords if k.arg == "prefix_or_class"), None)
                if arg is not None and not (isinstance(arg, ast.Constant) and isinstance(arg.value, str)):
                    blind.setdefault(bc, []).append(f"{f}:{node.lineno} api_controller 접두를 못 읽음")
                    continue
                prefix: str = _static_prefix(arg.value if arg is not None else "")
                if not prefix:
                    blind.setdefault(bc, []).append(f"{f}:{node.lineno} api_controller 접두가 비었거나 `/` 뿐(조각 일치가 무의미)")
                    continue
                prefixes.setdefault(bc, set()).add(prefix)
            for node in ast.walk(tree):                      # 맨 데코레이터 `@api_controller` — 기본 접두(빈 글)
                if isinstance(node, (ast.Name, ast.Attribute)) and _end_name(node) == "api_controller" \
                        and id(node) not in called and isinstance(node.ctx, ast.Load):
                    blind.setdefault(bc, []).append(f"{f}:{node.lineno} api_controller 를 접두 없이 씀(조각 일치가 무의미)")
        return prefixes, blind

    def _http_consumers(self) -> "list[dict]":
        """URL 문자열(.py · .js · .html · 공급 BC 밖) + 추적된 `.dddjango-web/*/server-contract.json` 가운데 경로 조각 경계에서
        `/<api_controller 접두>` 로 시작하는 조각을 품은 줄 — 앞에 어떤 마운트 접두가 와도 센다(마운트를 결속하지 않는 상위 집합).
        소스는 원문 줄과 `\\/` → `/` 로 푼 줄 둘 다 · 계약은 원문 줄 + `json.loads` 결과의 문자열 전부(키 · 값 · 재귀). 읽기 ·
        디코딩 · 계약 파싱을 못 한 파일은 건너뛰지 않고 `self.unread` 에 올린다(→ 관찰 못 함)."""
        out: "list[dict]" = []
        if not self.url_patterns:
            return out
        targets: "list[str]" = [f for f in self.files if f.endswith((".py", ".js", ".html"))]
        contracts: "list[str]" = [p for p in _git_ro(self.project, "ls-files", "-z", "--", ".dddjango-web").split("\0")
                                  if p.endswith("/server-contract.json") and p.count("/") == 2]
        for f in targets + contracts:
            text = self._text(f)
            if text is None:
                self.unread.append(f)
                continue
            owner: str = self._http_owner(f)
            contract: bool = f.endswith("server-contract.json")
            found: "set[str]" = set()
            for i, line in enumerate(text.splitlines(), 1):
                alt: str = line.replace("\\/", "/")
                for provider, pattern in sorted(self.url_patterns.items()):
                    if owner == provider or not (pattern.search(line) or pattern.search(alt)):
                        continue
                    found.add(provider)
                    out.append({"file": f, "line": i, "provider": provider, "owner": owner,
                                "test": _is_test_path(f), "contract": contract})
            if not contract:
                continue
            try:
                values: "list[str]" = _json_strings(json.loads(text))
            except ValueError:
                self.unread.append(f)
                continue
            for provider, pattern in sorted(self.url_patterns.items()):
                if owner != provider and provider not in found and any(pattern.search(s) for s in values):
                    out.append({"file": f, "line": 0, "provider": provider, "owner": owner, "test": False, "contract": True})
        return out

    def url_hits(self, text: str, bc: str, values: "list[str] | tuple[str, ...]" = ()) -> "list[str]":
        """글 속(원문 · `\\/` 를 푼 글)에서 이 BC 접두 조각을 품은 URL 문자열(앞뒤 경계까지) + 그 조각을 품은 파싱된 값 — 차례 · 한 번씩."""
        pattern = self.url_patterns.get(bc)
        out: "list[str]" = []
        if pattern is None:
            return out
        for src in (text, text.replace("\\/", "/")):
            for m in pattern.finditer(src):
                start, end = m.start(), m.end()
                while start > 0 and src[start - 1] not in _URL_TOKEN_STOP and src[start - 1] != "\n":
                    start -= 1
                while end < len(src) and src[end] not in _URL_TOKEN_STOP and src[end] != "\n":
                    end += 1
                if src[start:end] not in out:
                    out.append(src[start:end])
        for s in values:
            if pattern.search(s) and s not in out:
                out.append(s)
        return out

    @staticmethod
    def _http_owner(rel: str) -> str:
        parts: "list[str]" = rel.split("/")
        if parts[0] == "application" and len(parts) >= 3:
            return parts[1]
        if parts[0] == "web" and len(parts) >= 3:
            return f"web/{parts[1]}"
        if parts[0] == ".dddjango-web" and len(parts) >= 3:
            return f".dddjango-web/{parts[1]}"
        return rel

    # 그래프 ---------------------------------------------------------------
    def adjacency(self, with_test: bool) -> "dict[str, set[str]]":
        cats: "tuple[str, ...]" = PROD_CATS + (("test", "migration") if with_test else ())
        adj: "dict[str, set[str]]" = {bc: set() for bc in self.bcs}
        for r in self.refs:
            if r["category"] in cats and r["src"] in adj and r["dst"] in adj:
                adj[r["src"]].add(r["dst"])
        for h in self.http:
            if h["owner"] in adj and (with_test or not h["test"]) and not h["contract"]:
                adj[h["owner"]].add(h["provider"])
        return adj


def _tarjan(nodes: "list[str]", adj: "dict[str, set[str]]") -> "list[list[str]]":
    index: "dict[str, int]" = {}
    low: "dict[str, int]" = {}
    on: "set[str]" = set()
    stack: "list[str]" = []
    out: "list[list[str]]" = []
    counter: "list[int]" = [0]

    def strong(v: str) -> None:                          # 재귀 깊이 = BC 수(작다)
        index[v] = low[v] = counter[0]
        counter[0] += 1
        stack.append(v)
        on.add(v)
        for w in sorted(adj.get(v, ())):
            if w not in index:
                strong(w)
                low[v] = min(low[v], low[w])
            elif w in on:
                low[v] = min(low[v], index[w])
        if low[v] == index[v]:
            comp: "list[str]" = []
            while True:
                w = stack.pop()
                on.discard(w)
                comp.append(w)
                if w == v:
                    break
            out.append(sorted(comp))

    for v in nodes:
        if v not in index:
            strong(v)
    return out


def _lane_paths_of(scan: DepsScan, bc: str) -> "dict[str, tuple[str, ...]]":
    """이 레인이 고치는 다른 BC · 표면 파일 → 갈래들(받는 쪽 어댑터 · 받는 쪽 시험 · 직접 import 자리 · HTTP 소비자 · 공유 표면
    — 한 파일이 여러 갈래에 들 수 있다 · 차례는 이 순서)."""
    mine: str = f"application/{bc}/"
    found: "dict[str, list[str]]" = {}

    def add(path: str, kind: str) -> None:
        if kind not in found.setdefault(path, []):
            found[path].append(kind)

    def test_files_using(mods: "set[str]") -> "list[str]":
        return [f for f in scan.py if not f.startswith(mine) and _is_test_path(f)
                and any(m == t or m.startswith(t + ".") for m in scan.imports.get(f, set()) for t in mods)]

    receivers: "set[str]" = {f for f in scan.files if f.startswith("application/") and not f.startswith(mine)
                             and f"/anticorruption_layer/{bc}/" in f"/{f}"}
    receivers |= {r["file"] for r in scan.refs if r["dst"] == bc and r["src_spot"] == "event_subscription"
                  and r["dst_spot"] == "published_event"}
    for f in sorted(receivers):
        add(f, "받는 쪽 어댑터")
    recv_mods: "set[str]" = {_module_of(f) for f in receivers if f.endswith(".py")}
    window_mods: "set[str]" = {_module_of(f) for f in scan.py if f.startswith(mine)
                               and _spot(tuple(f.split("/")[2:])) in WINDOW_SPOTS}
    for f in test_files_using(recv_mods | window_mods):
        if f not in receivers:
            add(f, "받는 쪽 시험")
    for r in scan.refs:
        if r["dst"] == bc and r["category"] == "internal":
            add(r["file"], "직접 import 자리")
    callers: "set[str]" = {h["file"] for h in scan.http if h["provider"] == bc and not h["contract"]}
    for f in sorted(callers):
        add(f, "HTTP 소비자")
    for f in test_files_using({_module_of(f) for f in callers if f.endswith(".py")}):    # 그 호출 자리의 시험
        add(f, "HTTP 소비자")
    for r in scan.refs:
        if r["dst"] == bc and r["category"] == "surface_in":
            add(r["file"], "공유 표면")
    order: "dict[str, int]" = {k: i for i, k in enumerate(DEPS_EDIT_KINDS)}
    return {f: tuple(sorted(ks, key=order.__getitem__)) for f, ks in found.items()}


def _lane_edit_paths(project: Path, bc: str) -> "dict[str, tuple[str, ...]]":
    """`deps` 와 같은 계산의 «이 레인이 고치는 갈래» 경로표(check-verdict 의 다른 BC 몫 · changes 의 다른 BC 편집 대조)."""
    return _lane_paths_of(DepsScan(project), bc)


def _file_plan(text: str) -> "list[str] | None":
    """명세 machine file-plan 블록의 경로(없으면 None)."""
    return _machine_lines(text, "file-plan", lambda ln: (ln.split("#", 1)[0].split() + ["", ""])[1] or None)


def _boundary_imports(text: str) -> "list[str]":
    return _machine_lines(text, "boundary-imports", lambda ln: ln.strip() or None) or []


def _machine_lines(text: str, name: str, pick: "Callable[[str], str | None]") -> "list[str] | None":
    lines: "list[str]" = text.split("\n")
    for i, ln in enumerate(lines):
        if f"<!-- machine: {name} -->" not in ln:
            continue
        j: int = i + 1
        while j < len(lines) and not lines[j].strip():
            j += 1
        if j >= len(lines) or not _FENCE.match(lines[j]):
            return []
        out: "list[str]" = []
        for k in range(j + 1, len(lines)):
            if _FENCE.match(lines[k]):
                break
            got = pick(lines[k]) if lines[k].strip() else None
            if got:
                out.append(got)
        return out
    return None


class ActiveRun:
    """같은 저장소의 다른 활성 실행(이 작업 트리의 다른 폴더 · 다른 작업 트리) 하나."""

    def __init__(self, label: str, kind: str, where: str = "") -> None:
        self.label: str = label
        self.kind: str = kind                            # dddjango | dddjango-web | worktree
        self.where: str = where or label                 # 확인할 자료의 자리(폴더 · 작업 트리 경로)
        self.bcs: "set[str]" = set()
        self.paths: "set[str]" = set()
        self.units: "set[str]" = set()
        self.consumes: "list[str]" = []
        self.hold: str = ""


def _run_line(scope_text: str) -> "str | None":
    current: str = re.split(r"(?m)^#+\s*앞 실행", scope_text)[0]
    m = re.search(r"^\s*[-*]?\s*실행 · G0 승인 .*$", current, re.M)
    return m.group(0) if m else None


def _scope_run_line(folder: Path) -> "str | None":
    try:
        return _run_line((folder / "refactor-scope.md").read_text(encoding="utf-8"))
    except OSError:
        return None


def _dddjango_run(folder: Path, label: str, bc: str) -> "ActiveRun | None":
    """dddjango 실행 폴더 — 실행 줄에 G2 승인이 없을 때만 활성(실행 줄 없음 = 끝난 것)."""
    scope: Path = folder / "refactor-scope.md"
    try:
        text: str = scope.read_text(encoding="utf-8") if scope.is_file() else ""
    except OSError:
        text = ""
    line: "str | None" = _run_line(text)
    if line is None or "G2 승인" in line:
        return None
    run: ActiveRun = ActiveRun(label, "dddjango", str(folder))
    am = re.search(r"모드 리팩토링 · audit (\S+)", line)
    if am:
        try:
            plan_text: str = (folder / "audit" / am.group(1) / "plan.md").read_text(encoding="utf-8")
            pm = re.search(r"^- BC: `([^`]+)`", plan_text, re.M)
            if pm:
                run.bcs.add(pm.group(1))
        except OSError:
            pass
        fm = re.search(r"-refactor-([a-z0-9-]+)$", folder.name)
        if not run.bcs and fm:
            run.bcs.add(fm.group(1).replace("-", "_"))
    for fl in re.findall(r"^.*대상 BC 경로 필터.*$", re.split(r"(?m)^#+\s*앞 실행", text)[0], re.M):
        run.bcs |= set(re.findall(r"application/([a-z_][a-z0-9_]*)", fl))
    spec_text: str = ""
    try:
        spec_text = (folder / "design-spec.md").read_text(encoding="utf-8")
    except OSError:
        pass
    plan: "list[str] | None" = _file_plan(spec_text) if spec_text else None
    if plan:
        run.paths |= set(plan)
        run.bcs |= {p.split("/")[1] for p in plan if p.startswith("application/") and p.count("/") >= 2}
    run.consumes = [ln for ln in _boundary_imports(spec_text) if f"application.{bc}." in ln or ln.endswith(f"application.{bc}")]
    if not run.bcs:
        run.hold = "대상 BC 를 모른다(리팩토링 실행 줄 · 경로 필터 줄 · 명세 file-plan 없음)"
    elif not plan:
        run.hold = "명세 file-plan 이 아직 없다"           # 판정 단계에서 «겹칠 수 있음»일 때만 보류로 쓴다
    return run


def _web_run(folder: Path, label: str, scan: "DepsScan", bc: str) -> "ActiveRun | None":
    """dddjango-web 실행 폴더 — build-state `g2_approved` 가 참이 아니면 활성 · 단위 · 계약을 못 읽으면 보류(G1 승인 여부 무관)."""
    run: ActiveRun = ActiveRun(label, "dddjango-web", str(folder))
    try:
        state: dict = json.loads((folder / "build-state.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        run.hold = "build-state.json 을 못 읽는다(활성 여부 · 단위 · 계약 모름)"
        return run
    if state.get("g2_approved") is True:
        return None
    spec_text: str = ""
    try:
        spec_text = (folder / "design-spec.md").read_text(encoding="utf-8")
    except OSError:
        pass
    files: "list[str]" = list(_file_plan(spec_text) or []) if spec_text else []
    for sl in state.get("slices") or []:
        files += [f for f in (sl.get("files") or []) if isinstance(f, str)] if isinstance(sl, dict) else []
    run.paths |= set(files)
    run.units |= {"/".join(f.split("/")[:2]) for f in files if f.startswith("web/") and f.count("/") >= 2}
    contract: Path = folder / "server-contract.json"
    text: "str | None" = None
    values: "list[str]" = []
    try:
        text = contract.read_text(encoding="utf-8") if contract.is_file() else None
        if text is not None:
            values = _json_strings(json.loads(text))
    except (OSError, UnicodeDecodeError, ValueError):
        run.hold = "server-contract.json 을 읽지 못한다(계약 모름)"
        text = None
    if text is None and not run.hold:
        run.hold = "server-contract.json 이 없다(계약 모름)"
    for hit in scan.url_hits(text or "", bc, values):
        run.consumes.append(f"server-contract.json {hit}")
    if not run.units and not run.hold:
        run.hold = "web 단위를 모른다(명세 file-plan · build-state slices 에 web/<단위>/ 경로 없음)"
    return run


def _worktrees(project: Path) -> "list[tuple[Path, str]]":
    """같은 저장소의 다른 작업 트리 (경로, HEAD) — `git worktree list --porcelain`(메타데이터 읽기만)."""
    out: "list[tuple[Path, str]]" = []
    me: Path = project.resolve()
    cur: "dict[str, str]" = {}
    for ln in _git_ro(project, "worktree", "list", "--porcelain").splitlines() + [""]:
        if not ln.strip():
            if cur.get("worktree") and "bare" not in cur:
                path = Path(cur["worktree"]).resolve()
                if path != me:
                    out.append((path, cur.get("HEAD", "")))
            cur = {}
            continue
        key, _sp, val = ln.partition(" ")
        cur[key] = val
    return out


def _active_runs(project: Path, own: "Path | None", bc: str, scan: "DepsScan") -> "tuple[list[ActiveRun], int, int]":
    """(활성 실행, 본 작업 트리 수, 본 web 실행 수)."""
    runs: "list[ActiveRun]" = []
    trees: "list[tuple[Path, str, set[str] | None]]" = [(project, "", None)]
    for path, head in _worktrees(project):
        diff: "set[str] | None" = None
        try:
            ours: str = _git_ro(project, "rev-parse", "HEAD").strip()
            base: str = _git_ro(project, "merge-base", ours, head).strip()
            diff = {p for p in _git_ro(project, "diff", "--no-renames", "--name-only", base, head).splitlines() if p}
        except (subprocess.CalledProcessError, OSError):
            diff = None
        trees.append((path, head, diff))
    webs: int = 0
    own_line: "str | None" = _scope_run_line(own) if own is not None else None
    for root, head, diff in trees:
        where: str = "이 작업 트리" if root == project else f"작업 트리 {root}"
        if root != project and diff is None:
            r = ActiveRun(f"{where}(HEAD {head[:12]})", "worktree", str(root))
            r.hold = "커밋 차분(merge-base..그 트리 HEAD)을 못 읽는다"
            runs.append(r)
        for kind, base_dir in (("dddjango", root / ".dddjango"), ("dddjango-web", root / ".dddjango-web")):
            try:
                dirs: "list[Path]" = sorted(p for p in base_dir.iterdir() if p.is_dir()) if base_dir.is_dir() else []
            except OSError:
                r = ActiveRun(f"{where} {base_dir.name}/", kind, str(base_dir))
                r.hold = f"{base_dir} 를 읽지 못한다"
                runs.append(r)
                continue
            for d in dirs:
                if own is not None and d.resolve() == own.resolve():
                    continue
                if own is not None and d.name == own.name and own_line and _scope_run_line(d) == own_line:
                    continue                               # 다른 작업 트리에 든 이 실행의 사본(같은 폴더 · 같은 실행 줄)
                label: str = f"{where} {base_dir.name}/{d.name}"
                if kind == "dddjango-web":
                    if d.name == "private":
                        continue
                    webs += 1
                    run = _web_run(d, label, scan, bc)
                else:
                    run = _dddjango_run(d, label, bc)
                if run is None:
                    continue
                if diff:
                    run.paths |= diff
                    run.bcs |= {p.split("/")[1] for p in diff if p.startswith("application/") and p.count("/") >= 2}
                runs.append(run)
    return runs, len(trees), webs


def _path_hit(ours: "set[str]", theirs: "set[str]") -> "list[str]":
    """경로 단위 교집합(접두 포함 — 한쪽이 다른 쪽의 폴더 접두)."""
    hits: "list[str]" = []
    for t in sorted(theirs):
        for o in ours:
            if t == o or t.startswith(o.rstrip("/") + "/") or o.startswith(t.rstrip("/") + "/"):
                hits.append(t)
                break
    return hits


def _supplier_state(project: Path, supplier: str) -> str:
    """직접 공급자의 정리 상태 — `.dddjango/*refactor-<케밥>/refactor-scope.md` 의 G2 승인 리팩토링 실행 · 남은 재상정 수."""
    kebab: str = supplier.replace("_", "-")
    base: Path = project / ".dddjango"
    folders: "list[Path]" = sorted({*base.glob(f"*-refactor-{kebab}"), *base.glob(f"refactor-{kebab}")}) if base.is_dir() else []
    for folder in folders:
        try:
            text: str = (folder / "refactor-scope.md").read_text(encoding="utf-8")
        except OSError:
            continue
        if re.search(r"^.*실행 · G0 승인 .*모드 리팩토링.*G2 승인.*$", text, re.M):
            current: str = re.split(r"(?m)^#+\s*앞 실행", text)[0]
            left: "set[str]" = set()
            for sec in re.split(r"(?m)^#+\s", current):
                if sec.startswith("ⓐ 재상정") or "ⓐ 재상정" in sec.split("\n", 1)[0]:
                    left |= set(re.findall(r"\bM\d+\b", sec))
            return f"정리(재상정 {len(left)})"
    return "미정리"


def cmd_deps(project: Path, bc: str, out: Path) -> int:
    _bc_dir(project, bc)
    scan: DepsScan = DepsScan(project)
    if bc not in scan.bcs:
        raise ToolError(f"대상 BC 에 .py 파일이 없다 — application/{bc}/")
    prod: "dict[str, set[str]]" = scan.adjacency(with_test=False)
    full: "dict[str, set[str]]" = scan.adjacency(with_test=True)
    comps: "list[list[str]]" = _tarjan(scan.bcs, prod)
    comp: "list[str]" = next(c for c in comps if bc in c)
    suppliers: "list[str]" = sorted(prod.get(bc, set()) - set(comp))
    states: "dict[str, str]" = {s: _supplier_state(project, s) for s in suppliers}
    lane: "dict[str, tuple[str, ...]]" = _lane_paths_of(scan, bc)
    by_kind: "dict[str, list[str]]" = {k: sorted(p for p, ks in lane.items() if k in ks) for k in DEPS_EDIT_KINDS}
    receiver_bcs: "list[str]" = sorted({p.split("/")[1] for p in by_kind["받는 쪽 어댑터"] + by_kind["받는 쪽 시험"]
                                        if p.startswith("application/")})
    http_owners: "list[str]" = sorted({h["owner"] for h in scan.http if h["provider"] == bc})
    neighbors: "set[str]" = {b for b in full.get(bc, set())} | {a for a, ds in full.items() if bc in ds}
    neighbors |= {o for o in http_owners if o in scan.bcs}
    our_bcs: "set[str]" = {bc} | neighbors
    our_units: "set[str]" = {o for o in http_owners if o.startswith("web/")}
    target: Path = out.resolve()
    own: "Path | None" = next((p for p in [target, *target.parents] if p.parent.name == ".dddjango"), None)
    our_paths: "set[str]" = {f"application/{bc}/"} | set(lane)
    if own is not None and (own / "design-spec.md").is_file():     # G1 뒤 — 이 실행의 다른 BC 편집 목록도 우리 경로다
        our_paths |= {e["path"] for e in _other_edits(_read(own / "design-spec.md"), set())[0]}
    runs, trees, webs = _active_runs(project, own, bc, scan)
    overlaps: "list[str]" = []
    holds: "list[str]" = []
    http_blind: bool = bc in scan.http_blind
    for run in runs:
        why: "list[str]" = []
        if run.bcs & our_bcs:
            why.append(f"BC {' · '.join(sorted(run.bcs & our_bcs))}")
        hit: "list[str]" = _path_hit(our_paths, run.paths)
        if hit:
            why.append(f"경로 {' · '.join(hit[:3])}{' …' if len(hit) > 3 else ''}")
        if run.units & our_units:
            why.append(f"web 단위 {' · '.join(sorted(run.units & our_units))}")
        if run.consumes:
            why.append(f"계획된 소비 {run.consumes[0][:80]}")
        if why:
            overlaps.append(f"{run.label} — {' · '.join(why)} → 순서: 그 레인 착륙 뒤")
            continue
        maybe: bool = (run.kind != "dddjango" or not run.bcs
                       or bool((run.bcs | {b for x in run.bcs for b in full.get(x, set())}
                                | {a for a, ds in full.items() if run.bcs & ds}) & our_bcs))
        if run.hold and maybe:
            holds.append(f"{run.label} — 보류({run.hold}) · 확인할 자료: {run.where} 의 scope · 명세 file-plan · "
                         f"재개 조건: 그 레인이 G1 명세를 내거나 G2 로 끝난 뒤 다시 시작")
        elif http_blind:                                    # 우리 BC · 경로 집합이 덜 셈일 수 있다 — 관찰 못 한 충돌 후보
            holds.append(f"{run.label} — 보류(이 BC 의 HTTP 소비 관찰 못 함 — {scan.http_blind_why.get(bc, '')} — HTTP 소비자를 "
                         f"다 못 봐 겹침을 가를 수 없다) · 확인할 자료: 이 BC 의 API 표면(`api_controller(\"<접두>\")` 밖 표면 · 빈 접두) · "
                         f"{run.where} 의 명세 file-plan · 재개 조건: 그 표면의 접두를 api_controller 로 읽을 수 있게 되거나 "
                         f"그 레인이 G2 로 끝난 뒤 다시 시작")
    planned: "list[str]" = [f"{r.label}: {r.consumes[0][:60]}" for r in runs if r.consumes]
    cyc: bool = len(comp) > 1
    unsettled: "list[str]" = [s for s in suppliers if states[s] == "미정리"]
    data: dict = {"version": 1, "bc": bc, "scc": comp, "scc_all": [c for c in comps if len(c) > 1],
                  "suppliers": {s: states[s] for s in suppliers}, "edit_paths": {p: ks[0] for p, ks in lane.items()},
                  "edit_kinds": {p: list(ks) for p, ks in lane.items()},
                  "receiver_bcs": receiver_bcs, "http_owners": http_owners, "http_blind": http_blind,
                  "http_blind_why": scan.http_blind_reasons.get(bc, []), "http_prefixes": sorted(scan.prefixes.get(bc, set())),
                  "http_unread": scan.unread,
                  "our_bcs": sorted(our_bcs), "our_units": sorted(our_units), "planned": planned,
                  "overlaps": overlaps, "holds": holds, "worktrees": trees, "web_runs": webs,
                  "parse_errors": scan.parse_errors}
    out.mkdir(parents=True, exist_ok=True)
    (out / "deps.json").write_text(json.dumps(data, ensure_ascii=False, sort_keys=True, indent=1) + "\n", encoding="utf-8")
    md: "list[str]" = [f"# deps — `{bc}` · {_now()}", "",
                       f"- 순환 성분(운영): {' · '.join(comp)}{' — 지원 안 함(순환 묶음 · 묶음 계획을 먼저)' if cyc else ' (단독)'}",
                       "- 내주는 쪽: " + (" · ".join(f"{s}({states[s]})" for s in suppliers) or "없음"),
                       "- 받는 쪽: " + (" · ".join(receiver_bcs) or "없음"),
                       "- HTTP 소비: " + (" · ".join(http_owners) or "없음")
                       + (f" · 관찰 못 함({scan.http_blind_why.get(bc, '')})" if http_blind else ""),
                       "- 계획된 소비: " + (" · ".join(planned) or "없음"), ""]
    for kind in DEPS_EDIT_KINDS:
        md += [f"## {kind} {len(by_kind[kind])}", ""] + [f"- {p}" for p in by_kind[kind]] + [""]
    md += ["## 레인 겹침", ""] + ([f"- {o}" for o in overlaps] or ["- 없음"]) + [""]
    md += ["## 보류", ""] + ([f"- {h}" for h in holds] or ["- 없음"]) + [""]
    md += [f"- 본 범위: 작업 트리 {trees} · web 실행 {webs} · 저장소 밖은 보지 않는다", ""]
    (out / "deps.md").write_text("\n".join(md), encoding="utf-8")
    for o in overlaps:
        print(f"  겹침: {o}")
    for h in holds:
        print(f"  보류: {h}")
    if cyc:
        print(f"  지원 안 함: 순환 묶음 {' · '.join(comp)} — 묶음 계획을 먼저(운영자 의존 지도)")
    print(f"요약: deps {bc} · 순환 성분 {'크기 ' + str(len(comp)) if cyc else '단독'} · 내주는 쪽 "
          f"{' · '.join(f'{s}({states[s]})' for s in suppliers) or '없음'} · 미정리 공급자 {len(unsettled)} · 받는 쪽 "
          f"{' · '.join(receiver_bcs) or '없음'} · 직접 import 자리 {len(by_kind['직접 import 자리'])} · HTTP 소비 "
          f"{' · '.join(http_owners) or '없음'}{' · HTTP 소비 관찰 못 함' if http_blind else ''} · 공유 표면 "
          f"{len(by_kind['공유 표면'])} · 계획된 소비 {len(planned) or '없음'} · 레인 겹침 {len(overlaps) or '없음'} · "
          f"보류 {len(holds)} · 본 범위: 작업 트리 {trees} · web 실행 {webs} · 관찰 못 한 활성 실행 {len(holds)}"
          f"{' · 파싱 못 한 파일 ' + str(len(scan.parse_errors)) if scan.parse_errors else ''} → {out}")
    return DEPS_STOP_EXIT if cyc or overlaps or holds else EXIT_OK


# ── self-test ────────────────────────────────────────────────────────────────

_OPSAFE_LABEL: "re.Pattern[str]" = re.compile(r"(?m)^\s*(?:[-*]\s*)?(조건부\s*대상|대상|유지)\s*[:：]")


def _rid_list(text: str) -> "list[str]":
    """본문 조각의 R-ID — `R-2056~R-2062` 범위는 펼친다."""
    out: "list[str]" = []
    for m in re.finditer(r"R-(\d{4})(?:\s*[~∼–-]\s*R-(\d{4}))?", text):
        a: int = int(m.group(1))
        b: int = int(m.group(2)) if m.group(2) else a
        out += [f"R-{n:04d}" for n in range(a, b + 1)] if b >= a else [f"R-{a:04d}"]
    return out


def _opsafe_lists(body: str) -> "dict[str, set[str]]":
    """«운영 전 예외» Override 블록 본문 → {대상, 조건부, 유지} R-ID — 줄 머리 `- 대상:` · `- 조건부 대상:` · `- 유지:` 뒤 다음 표지까지."""
    marks = [(m.start(), m.end(), re.sub(r"\s+", "", m.group(1))) for m in _OPSAFE_LABEL.finditer(body)]
    out: "dict[str, set[str]]" = {"대상": set(), "조건부": set(), "유지": set()}
    for k, (_s, e, label) in enumerate(marks):
        end: int = marks[k + 1][0] if k + 1 < len(marks) else len(body)
        out["조건부" if label.startswith("조건부") else label] |= set(_rid_list(body[e:end]))
    return out


def _opsafe_binding(corpus: Corpus, rid: str, overrides: "set[str]") -> "tuple[list[str], dict[str, int]]":
    """§6-2 ① ② ③ — 운영 전 예외 블록 본문 · 팩 overrides · 렌더 md 블록 해시 결속. (red, 수)."""
    reds: "list[str]" = []
    meta: "dict | None" = corpus.works.get(rid)
    if meta is None:
        return [f"③ {OPSAFE_ROLE} 규범 {rid} 가 팩에 없다"], {}
    key: str = corpus.key_of(meta["document"])
    spans = corpus.block_spans(key).get(meta["block"])
    if not spans:
        return [f"③ {OPSAFE_ROLE} 규범 {rid} 블록이 렌더 md({key} · {corpus.platform})의 팩 블록 해시와 결속되지 않는다"], {}
    i, j = spans[0]
    lists = _opsafe_lists("\n".join(corpus.doc(key).lines[i:j]))
    listed: "set[str]" = lists["대상"] | lists["조건부"]
    if not listed or listed != overrides:
        reds.append(f"① 블록 본문 대상 ∪ 조건부 ≠ 팩 overrides — 본문만 {sorted(listed - overrides)[:4]} · "
                    f"팩만 {sorted(overrides - listed)[:4]}")
    missing: "list[str]" = sorted(r for r in lists["유지"] if r not in corpus.works)
    if not lists["유지"]:
        reds.append("② 블록 본문에 유지 R-ID 가 없다")
    if missing:
        reds.append(f"② 유지 R-ID 가 팩에 없다: {missing[:4]}")
    both: "list[str]" = sorted(lists["유지"] & overrides)
    if both:
        reds.append(f"② 유지 R-ID 가 overrides 와 겹친다: {both[:4]}")
    return reds, {k: len(v) for k, v in lists.items()}


def cmd_self_test(corpus: Corpus) -> int:
    reds: "list[str]" = []
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import standard_tree  # noqa: PLC0415
        bc_children = {r.name.rstrip("/") for r in standard_tree.children(standard_tree.bc_root())}
        stray = [l for l in LAYER_ORDER if l not in bc_children]
        if stray:
            reds.append(f"조각 층 이름이 표준 트리 BC 직계에 없다: {stray}")
    except ImportError as exc:
        reds.append(f"standard_tree 적재 불가: {exc}")
    tokens: "list[str]" = [t for ts in LENS_SECTIONS.values() for t in ts] + list(SECURITY_SECTIONS)
    for t in tokens:
        key, _s, sec = t.partition(" §")
        if not corpus.path_of(key).is_file():
            reds.append(f"점검 절 문서 없음: {t}")
        elif corpus.doc(key).section(sec) is None:
            reds.append(f"점검 절 없음: {t}")
    for document in sorted({w["document"] for w in corpus.works.values()}):
        if not corpus.path_of(corpus.key_of(document)).is_file():
            reds.append(f"경로 사상 실패: {document} → {corpus.path_of(corpus.key_of(document))}")
    try:                                                   # ④ 역할 표 = 팩 «대상 있는 Override» 집합
        roles = corpus.override_norms()
    except ToolError as exc:
        reds.append(f"④ {exc}")
        roles = {role: (rid, set(corpus.works.get(rid, {}).get("overrides") or [])) for role, rid in OVERRIDE_ROLES.items()}
    counts: "dict[str, int]" = {}
    try:
        nov, targets = roles[SCOPE_ROLE]
        missing = sorted(t for t in targets if t not in corpus.works)
        if missing:
            reds.append(f"대상 목록에 팩 밖 규범: {missing[:5]}")
        if nov not in corpus.works:
            raise ToolError(f"{SCOPE_ROLE} 규범 {nov} 가 팩에 없다")
        key = corpus.key_of(corpus.works[nov]["document"])
        spans = corpus.block_spans(key).get(corpus.works[nov]["block"])
        if not spans:
            reds.append(f"{SCOPE_ROLE} 규범 {nov} 블록을 설치본에서 찾지 못했다({corpus.platform})")
        else:
            i, j = spans[0]
            body: str = "\n".join(corpus.doc(key).lines[i:j])
            tail: str = body.split(PHRASE_MARK, 1)[1] if PHRASE_MARK in body else ""
            listed = {normalize(p) for p in re.findall(r"«([^«»]+)»", tail)}
            const = {normalize(p) for p in SCOPE_PHRASES}
            if listed != const:
                reds.append(f"적용 한정 어구 상수 ≠ 규범 문면: 상수만 {sorted(const - listed)[:4]} · "
                            f"문면만 {sorted(listed - const)[:4]}")
        orid, otargets = roles[OPSAFE_ROLE]
        bind_reds, counts = _opsafe_binding(corpus, orid, otargets)
        reds += bind_reds
    except ToolError as exc:
        reds.append(str(exc))
    try:
        coord: str = "\n".join(corpus.doc("commands/dddjango.md").lines)
        for mark, end, const, name in ((CATEGORY_MARK, "가운데 하나", RESOLUTION_CATEGORIES, "불가 범주"),
                                       (RECONSIDER_MARK, "가운데 하나", RECONSIDER_TOKENS, "재상정 결정 어휘")):
            if mark not in coord:
                reds.append(f"{name} 문면(«{mark}»)을 Coordinator 에서 찾지 못했다({corpus.platform})")
                continue
            listed_seq: "list[str]" = re.findall(r"`([^`]+)`", coord.split(mark, 1)[1].split(end, 1)[0])
            if listed_seq != list(const):
                reds.append(f"{name} 상수 ≠ 규범 문면: 상수 {list(const)} · 문면 {listed_seq}")
    except ToolError as exc:
        reds.append(str(exc))
    for r in reds:
        print(f"  red: {r}")
    opsafe: str = (f"{OPSAFE_ROLE} 대상 {counts.get('대상', 0)} · 조건부 {counts.get('조건부', 0)} · 유지 {counts.get('유지', 0)}"
                   if counts else f"{OPSAFE_ROLE} 결속 안 됨")
    print(f"요약: self-test {corpus.platform} · 점검 절 {len(tokens)} · 문서 {len({w['document'] for w in corpus.works.values()})} · "
          f"어구 {len(SCOPE_PHRASES)} · 불가 범주 {len(RESOLUTION_CATEGORIES)} · 재상정 어휘 {len(RECONSIDER_TOKENS)} · "
          f"{opsafe} · red {len(reds)}")
    return EXIT_RED if reds else EXIT_OK


# ── main ─────────────────────────────────────────────────────────────────────

def main(argv: "list[str]") -> int:
    ap = argparse.ArgumentParser(prog="refactor_audit.py", description="리팩토링 모드 결정적 도구")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--platform", choices=("claude", "codex"))
    ap.add_argument("--plugin-root")
    ap.add_argument("--rulepack")
    ap.add_argument("--project", default=".", help="대상 프로젝트 루트(기본 .)")
    sub = ap.add_subparsers(dest="command")
    for name in ("plan", "outline", "deps"):
        p = sub.add_parser(name)
        p.add_argument("bc")
        p.add_argument("--out", required=True)
        if name == "plan":
            p.add_argument("--stage", help="R0′ 기록 — 운영 전 출처(본인 직접(<시각>) | 사용자 원문 <파일:행>(<시각>))")
    for name in ("check", "sections"):
        sub.add_parser(name).add_argument("audit")
    p = sub.add_parser("check-verdict")
    p.add_argument("audit")
    p.add_argument("--feedback")
    p.add_argument("--final", action="store_true")
    p = sub.add_parser("resolution")
    p.add_argument("folder")
    p.add_argument("--gate", action="store_true")
    p = sub.add_parser("residual")
    p.add_argument("folder")
    p.add_argument("--candidates")
    p.add_argument("--finalize")
    p = sub.add_parser("changes")
    p.add_argument("folder")
    group = p.add_mutually_exclusive_group()
    group.add_argument("--candidate", action="store_true")
    group.add_argument("--applied")
    group.add_argument("--gate", action="store_true")
    p.add_argument("--baseline", help="창 open 기록(w<n>-open.json) — «바뀌는 기대» 실재를 창 기준선에서 본다")
    try:
        ns = ap.parse_args(argv)
    except SystemExit as exc:
        if exc.code == 0:
            return EXIT_OK
        print("요약: refactor_audit 실행 불능 — 인자 오류(위 사용법)")
        return EXIT_ERR
    project: Path = Path(ns.project).resolve()
    loaded: "list[Corpus]" = []

    def corpus_fn() -> Corpus:
        if not loaded:
            loaded.append(Corpus(ns.platform, Path(ns.plugin_root).resolve() if ns.plugin_root else None,
                                 Path(ns.rulepack).resolve() if ns.rulepack else None))
        return loaded[0]

    try:
        if ns.command == "plan":
            return cmd_plan(project, ns.bc, Path(ns.out), ns.stage)
        if ns.command == "outline":
            return cmd_outline(project, ns.bc, Path(ns.out))
        if ns.command == "deps":
            return cmd_deps(project, ns.bc, Path(ns.out))
        if ns.command == "residual":
            return cmd_residual(project, Path(ns.folder), Path(ns.candidates) if ns.candidates else None, ns.finalize)
        if ns.command == "resolution":
            return cmd_resolution(project, Path(ns.folder), ns.gate, corpus_fn)
        if ns.command == "changes":
            mode: str = "candidate" if ns.candidate else "applied" if ns.applied else "gate" if ns.gate else "check"
            return cmd_changes(project, Path(ns.folder), mode, Path(ns.applied) if ns.applied else None,
                               Path(ns.baseline) if ns.baseline else None)
        corpus: Corpus = corpus_fn()
        if ns.self_test:
            return cmd_self_test(corpus)
        if ns.command == "check":
            return cmd_check(corpus, project, Path(ns.audit))
        if ns.command == "sections":
            return cmd_sections(corpus, project, Path(ns.audit))
        if ns.command == "check-verdict":
            return cmd_check_verdict(corpus, project, Path(ns.audit),
                                     Path(ns.feedback) if ns.feedback else None, ns.final)
        ap.print_usage()
        print("요약: refactor_audit 실행 불능 — 하위 명령 없음")
        return EXIT_ERR
    except (ToolError, OSError, ValueError, KeyError, json.JSONDecodeError, subprocess.CalledProcessError) as exc:
        print(f"실행 불능: {type(exc).__name__}: {exc}", file=sys.stderr)
        print(f"요약: refactor_audit {ns.command or 'self-test'} 실행 불능 — {str(exc)[:160]}")
        return EXIT_ERR


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
