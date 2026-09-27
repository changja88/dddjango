#!/usr/bin/env python3
"""리팩토링 모드 결정적 도구 — BC 점검(R2)·판정(R3)·G2 잔존의 기계 판정(표준 라이브러리 전용).

Coordinator «리팩토링 모드» 절이 이 도구를 부른다. 리뷰어·architect 에게는 Bash 가 없다 —
도구는 Coordinator 만 돌리고, 산출은 파일로 쓰고 경로만 넘긴다.

정규화(`normalize`)는 규칙 팩 생성기(`workspace/tools/ontology_rulepack.py`)가 블록 해시를
계산할 때 그대로 빌려 쓴다 — 설치본의 결속 대조와 팩의 해시가 한 함수에서 나온다.

사용(대상 프로젝트 루트에서):
  refactor_audit.py plan <bc> --out <audit 폴더>        렌즈·조각·점검 절 → plan.md
  refactor_audit.py outline <bc> --out <audit 폴더>     파일별 정의·행 → outline.md
  refactor_audit.py check <audit 폴더>                  리뷰어 표 인용·위치 검사 + 블록 결속 → check.md
  refactor_audit.py sections <audit 폴더>               판정 입력(절 원문·규범 주석·적용 범위 규범) → sections.md
  refactor_audit.py check-verdict <audit 폴더> [--feedback <파일>] [--final]
                                                        verdict.md 검사 → verdict-log.md append · `요약:` 1행
  refactor_audit.py residual <산출물 폴더> [--candidates <검사기 출력>] [--finalize <시각>]
                                                        G2 의미 항목 잔존(결정적 바닥 → 리뷰어 재확인 묶음) — 리뷰어 확인
                                                        대상이 남은 첫 호출은 exit 0 + `M_m 미정`(판정은 --finalize)
  refactor_audit.py --self-test                         점검 절 실재 · 경로 사상 · 적용 한정 어구 상수 = 규범 문면
공통: --platform claude|codex(기본: 자기 위치로 판별) · --plugin-root <경로> · --rulepack <경로>
exit 0 = 통과 · 2 = red(검사 실패·잔존) · 1 = 실행 불능. 모든 하위 명령이 `요약:` 1행을 낸다.
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
from datetime import datetime, timezone
from pathlib import Path

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
VERDICTS: "tuple[str, ...]" = ("채택", "병합", "제외", "오탐", "사용자 판단", "별도 요청")
PROXY_FREE: "tuple[str, ...]" = ("본인 직접", "사용자 원문")
SEPARATE_TYPES: "tuple[str, ...]" = ("모델 필드", "응답·예외 경로", "타 BC")
_ADAPTER_TOKENS: "tuple[str, ...]" = ("response", "status", "Schema", "HttpError", "exception", "Exception",
                                      "errors", "raise")


class ToolError(Exception):
    """실행 불능(exit 1) — 입력·재료 결손."""


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

    # 적용 범위 규범 -------------------------------------------------------
    def scope_norm(self) -> "tuple[str, set[str]]":
        """적용 범위 Override(N-OV) R-ID 와 대상 목록 — `norm_kind == Override ∧ overrides ≠ ∅` 이 정확히 1개."""
        found: "list[str]" = sorted(r for r, w in self.works.items()
                                    if w.get("norm_kind") == "Override" and w.get("overrides"))
        if len(found) != 1:
            raise ToolError(f"적용 범위 규범이 {len(found)}개다(정확히 1개여야 한다): {found[:5]}")
        return found[0], set(self.works[found[0]]["overrides"])

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


def cmd_plan(project: Path, bc: str, out: Path) -> int:
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
                          f"- 보안 절 담당: {security}", "", "## 렌즈", ""]
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
    print(f"요약: plan BC {bc} · 렌즈 {len(lenses)}({'·'.join(shown[l] for l in lenses)}) · 조각 {len(chunks)} · "
          f"파견 {len(lenses) * len(chunks)} · 보안 {security} · 파일 {len(files)} → {out / 'plan.md'}")
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

def _table_rows(text: str) -> "list[list[str]]":
    rows: "list[list[str]]" = []
    for ln in text.splitlines():
        s: str = ln.strip()
        if not s.startswith("|") or re.fullmatch(r"\|[\s:|-]*\|", s):
            continue
        rows.append([c.strip() for c in s.strip("|").split("|")])
    return rows


class Plan:
    def __init__(self, audit: Path) -> None:
        text: str = _read(audit / "plan.md")
        m = re.search(r"^- BC: `([^`]+)`", text, re.M)
        if not m:
            raise ToolError("plan.md 에 BC 줄이 없다")
        self.bc: str = m.group(1)
        sec: str = text.split("## 파견", 1)[1].split("\n## ", 1)[0] if "## 파견" in text else ""
        self.dispatch: "list[tuple[str, str, str]]" = [(r[0], r[1].split("+", 1)[0], r[2]) for r in _table_rows(sec)
                                                      if len(r) >= 3 and r[0].endswith(".md")]
        if not self.dispatch:
            raise ToolError("plan.md 에 파견 표가 없다")


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
        self.fixable: str = cells[5]
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
    lines: "list[str]" = [f"# check — `{plan.bc}` · {_now()}", "",
                          "| 원 행 | 상태 | 블록 | 규범(종류) | 반대 방향 블록 | 파일:행 | 사유 |",
                          "|---|---|---|---|---|---|---|"]
    for r in rows:
        lines.append(f"| {r.rid} | {r.status} | {r.bid or '—'} | {_works_text(corpus, r.bid)} | "
                     f"{r.opp_bid or ('—' if not r.opposite else '결속 실패')} | {r.where} | {r.reason} |")
    lines += ["", "## 인용 불일치(원 리뷰어 재인용 대상 — 행 목록만)", ""]
    lines += [f"- {r.rid}: {r.reason}" for r in bad] or ["- 없음"]
    (audit / "check.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"요약: check 행 {len(rows)} · 통과 {len(passed)} · 인용 불일치 {len(bad)} · 규칙 근거 없는 불편 {len(no_rule)} · "
          f"결속 실패 {len(unbound)}(제외·오탐 근거 불가) → {audit / 'check.md'}")
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
    nov, targets = corpus.scope_norm()
    lines: "list[str]" = [f"# sections — `{plan.bc}` · {_now()}", "",
                          "판정 근거는 이 파일이 공급한 것뿐이다(자기 스킬 밖 규범을 스스로 찾아 읽지 않는다).", ""]
    lines += ["## 적용 범위 규범", ""]
    nkey: str = corpus.key_of(corpus.works[nov]["document"])
    nspans = corpus.block_spans(nkey).get(corpus.works[nov]["block"])
    if not nspans:
        raise ToolError(f"적용 범위 규범 {nov} 블록을 설치본에서 찾지 못했다(`{nkey}`)")
    i, j = nspans[0]
    lines += [f"〔{nov} · Override · {corpus.works[nov]['label']}〕", *corpus.doc(nkey).lines[i:j], ""]
    lines += ["### 대상 목록(제외·오탐·반대 방향 근거가 될 수 없다)", "", "| R-ID | 종류 | 라벨 |", "|---|---|---|"]
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
    print(f"요약: sections 절 {len(wanted)} · 적용 범위 규범 {nov} · 대상 {len(targets)} → {audit / 'sections.md'}")
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


def _load_verdicts(audit: Path) -> "list[Verdict]":
    out: "list[Verdict]" = []
    for cells in _table_rows(_read(audit / "verdict.md")):
        if cells and re.fullmatch(r"M\d+", cells[0].strip()) and len(cells) >= 3:
            out.append(Verdict(cells))
    return out


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


def _exclusion(corpus: Corpus, row: Row, v: Verdict, nov: str, targets: "set[str]") -> str:
    m = re.match(r"\s*`?(R-\d{4})`?\s*«(.*)»\s*$", v.ground)
    if not m:
        return "제외 근거 형식(`R-ID «인용»`) 아님"
    rid, quote = m.group(1), m.group(2)
    if rid == nov:
        return f"③ 적용 범위 규범 {rid} 는 제외 근거가 아니다"
    if rid in targets:
        return f"③ 대상 목록 규범 {rid}({corpus.works.get(rid, {}).get('label', '')}) 는 제외 근거가 아니다"
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
        blocked: str = _opposite_blocked(corpus, row, nov, targets)   # 반대 방향 경로로만 서는 제외
        if blocked:
            return f"② {blocked}"
    if set(corpus.blocks[bid]["works"]) & targets:
        hit = corpus.phrase_hit(corpus.quote_sentences(key, bid, quote))
        if hit:
            return f"③ 인용이 든 문장에 적용 한정 어구 «{hit[0]}»"
    if row.bid == bid and (corpus.kinds(bid) & DUTY_KINDS) and (corpus.kinds(bid) & ALLOW_KINDS):
        mine = corpus.quote_span(key, bid, quote)
        theirs = corpus.quote_span(row.key, bid, row.quote)
        if any(a < d and c < b for a, b in mine for c, d in theirs):
            return "④ 혼합 블록 — 제외 인용이 위반 인용과 겹친다"
    return ""


def _false_positive(corpus: Corpus, row: Row, v: Verdict, targets: "set[str]") -> str:
    m = re.search(r"«(.*)»", v.ground)
    if not m:
        return "오탐 근거 형식(`«요건 문구»`) 아님"
    quote: str = m.group(1)
    if row.bid is None:
        return "위반 행이 결속되지 않아 같은 블록 요건을 확인할 수 없다"
    if not corpus.quote_span(row.key, row.bid, quote):
        return "오탐 인용이 위반으로 인용된 그 블록에 없다(같은 절의 다른 문장 불가)"
    if set(corpus.blocks[row.bid]["works"]) & targets:
        hit = corpus.phrase_hit(corpus.quote_sentences(row.key, row.bid, quote))
        if hit:
            return f"오탐 인용이 든 문장에 적용 한정 어구 «{hit[0]}»"
    return ""


def _opposite_blocked(corpus: Corpus, row: Row, nov: str, targets: "set[str]") -> str:
    """리뷰어 반대 방향 인용이 근거가 될 수 없는 사유(비면 근거 가능) — 사용자 판단·반대 방향 경로 제외 공통."""
    works: "set[str]" = set(corpus.blocks[row.opp_bid]["works"])  # type: ignore[index]
    if nov in works:
        return f"반대 방향 규칙이 적용 범위 규범 {nov} 다"
    if works & targets:
        hit = corpus.phrase_hit(corpus.quote_sentences(row.opp_key, row.opp_bid, row.opp_quote))
        if hit:
            return f"반대 방향 규칙 인용이 든 문장에 적용 한정 어구 «{hit[0]}» — 결정 18 이 가른 충돌"
    return ""


def _user_judgment(corpus: Corpus, row: Row, nov: str, targets: "set[str]") -> str:
    if not row.opposite:
        return "사용자 판단인데 리뷰어 행에 반대 방향 규칙이 없다"
    if row.opp_bid is None:
        return "반대 방향 규칙이 결속되지 않는다"
    return _opposite_blocked(corpus, row, nov, targets)


def _separate(project: Path, bc: str, row: Row, v: Verdict) -> str:
    """별도 요청 근거 — 실패 사유(비면 통과). 실패는 채택 재분류다."""
    if not row.fixable.startswith("아니오"):
        return "리뷰어 «동작 불변 정리 가능 = 아니오» 없음"
    kind = next((t for t in SEPARATE_TYPES if t in v.ground), None)
    if kind is None:
        return "근거 유형(모델 필드 · 응답·예외 경로 · 타 BC) 없음"
    locs = [l for l in (_parse_location(t) for t in _locations(row.where)) if l]
    if kind == "모델 필드":
        return "" if any(_defines_model(project, l[0]) for l in locs) else "항목 위치가 ORM 모델 파일이 아니다"
    if kind == "응답·예외 경로":
        for rel, a, b in locs:
            if "/driving_layer/api/" not in rel:
                continue
            body = (project / rel).read_text(encoding="utf-8", errors="replace").splitlines()[a - 1:b]
            if any(tok in ln for ln in body for tok in _ADAPTER_TOKENS):
                return ""
        return "항목 위치가 HTTP 어댑터의 응답·상태 코드·예외 매핑 행이 아니다"
    evid = [l for l in (_parse_location(t) for t in _locations(v.ground)) if l]
    for rel, a, b in evid:
        m = re.match(r"application/([^/]+)/", rel)
        if m and m.group(1) != bc and _location_ok(project, (rel, a, b)):
            return ""
    return "타 BC 근거 `application/<다른 bc>/…:행` 이 없거나 실재하지 않는다"


def _judge(corpus: Corpus, project: Path, bc: str, verdicts: "list[Verdict]", by_id: "dict[str, Row]",
           passed: "set[str]", nov: str, targets: "set[str]") -> "tuple[list[tuple[str, str, str]], list[tuple[str, str]]]":
    """판정 표 검사 → (red 목록 `(M|원 행, 종류, 사유)`, 재분류). 종류: 구조(M 중복·두 번·통과 밖) · 판정 없음 · 판정."""
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
            why = next((w for w in (_exclusion(corpus, r, v, nov, targets) for r in row_list) if w), "")
        elif v.kind == "오탐":
            why = next((w for w in (_false_positive(corpus, r, v, targets) for r in row_list) if w), "")
        elif v.kind == "사용자 판단":
            why = next((w for w in (_user_judgment(corpus, r, nov, targets) for r in row_list) if w), "")
        elif v.kind == "병합":
            if v.merge_to.startswith("M"):
                if kinds.get(v.merge_to) != "채택":
                    why = f"병합 대상 {v.merge_to} 이 채택 항목이 아니다"
            elif not all(re.search(rf"\b{re.escape(v.merge_to)}\b", r.same_c) for r in row_list):
                why = f"리뷰어가 «{v.merge_to} 과 같음»을 적지 않은 행의 M→C 병합"
        elif v.kind == "별도 요청":
            fail = next((w for w in (_separate(project, bc, r, v) for r in row_list) if w), "")
            if fail:
                reclass.append((v.mid, f"별도 요청 → 채택({fail})"))
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
    return out


def cmd_check_verdict(corpus: Corpus, project: Path, audit: Path, feedback: "Path | None", final: bool) -> int:
    plan: Plan = Plan(audit)
    rows: "list[Row]" = _load_rows(audit, plan)
    _check_rows(corpus, project, plan.bc, rows)
    by_id: "dict[str, Row]" = {r.rid: r for r in rows}
    passed: "set[str]" = {r.rid for r in rows if r.status == "통과"}
    nov, targets = corpus.scope_norm()
    verdicts: "list[Verdict]" = _load_verdicts(audit)
    reds, reclass = _judge(corpus, project, plan.bc, verdicts, by_id, passed, nov, targets)
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
    counts: "dict[str, int]" = {k: 0 for k in ("채택", "사용자 판단", "별도 요청", "제외", "오탐", "병합→C", "병합→M")}
    for v in verdicts:
        if v.label in counts:
            counts[v.label] += 1
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
    summary: str = (f"요약: 채택 {counts['채택']} · 사용자 판단 {counts['사용자 판단']} · 별도 요청 {counts['별도 요청']} · "
                    f"제외 {counts['제외']} · 오탐 {counts['오탐']} · 병합→C {counts['병합→C']} · 병합→M {counts['병합→M']} · "
                    f"인용 불일치 {q} · 규칙 근거 없는 불편 {f} · 혼합 블록 제외 {len(set(mixed))} · red {len(reds)}")
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
    for m, _k, w in reds:
        print(f"  red: {m} {w}")
    for m, w in reclass:
        print(f"  재분류: {m} {w}")
    print(summary)
    return code


# ── residual ─────────────────────────────────────────────────────────────────

def _git(project: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(project), *args], capture_output=True, text=True, check=True).stdout


def _scope(folder: Path) -> "tuple[str, set[str], set[str]]":
    """(audit 시각, 이번 실행 ⓐ M 키, 재상정으로 뺀 키) — `refactor-scope.md` 의 앞 실행 절 앞까지."""
    text: str = re.split(r"(?m)^#+\s*앞 실행", _read(folder / "refactor-scope.md"))[0]
    m = re.search(r"^\s*실행 · G0 승인 \S+ · 모드 리팩토링 · audit (\S+)", text, re.M)
    if not m:
        raise ToolError("refactor-scope.md 에 리팩토링 실행 줄(`실행 · G0 승인 <값> · 모드 리팩토링 · audit <시각>`)이 없다")
    adopted: "set[str]" = set()
    removed: "set[str]" = set()
    in_reconsider: bool = False
    for ln in text.splitlines():
        if re.match(r"^#+\s", ln):
            in_reconsider = "ⓐ 재상정" in ln
            continue
        # 결정 값이 빈 자리표시(`결정 = · …` — 답을 받기 전의 STOP 기록)면 결정이 아니다.
        dm = re.match(r"^\s*[-*]?\s*(.+?)\s*·\s*결정\s*=\s*([^\s·—-]\S*)", ln)
        if not dm:
            continue
        keys: "set[str]" = set(re.findall(r"\bM\d+\b", dm.group(1)))
        if in_reconsider:
            removed |= keys
        elif dm.group(2).startswith("ⓐ") and not dm.group(2).startswith("ⓐ′"):
            adopted |= keys
    return m.group(1), adopted, removed


def _map_items(folder: Path, run_value: str) -> "dict[str, str]":
    """0C 창 close 기록의 대응 원소(옛 경로 → 새 경로) — 창마다 마지막 판정."""
    run_dir: Path = folder / "behavior" / re.sub(r"[^\w.-]", "_", run_value)
    mapping: "dict[str, str]" = {}
    for close in sorted(run_dir.glob("w*-close.json")) if run_dir.is_dir() else []:
        opened: Path = close.with_name(close.name.replace("-close", "-open"))
        if opened.is_file() and json.loads(opened.read_text(encoding="utf-8")).get("kind") != "code":
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


def cmd_residual(project: Path, folder: Path, candidates: "Path | None", finalize: "str | None") -> int:
    audit_ts, adopted, removed = _scope(folder)
    items: "set[str]" = adopted - removed
    audit: Path = folder / "audit" / audit_ts
    verdicts: "dict[str, Verdict]" = {v.mid: v for v in _load_verdicts(audit)}
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
        v = verdicts.get(mid)
        if v is None:
            raise ToolError(f"ⓐ 항목 {mid} 이 verdict.md 에 없다")
        merged = [x for x in verdicts.values() if x.kind == "병합" and x.merge_to == mid]
        origins[mid] = [(o, "") for o in v.origin] + [(o, x.mid) for x in merged for o in x.origin]
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
                                 "결과 표(`result-<렌즈>.md`): `M<n> | 해소|잔존|판단 불가 | 근거(해소면 새 파일:행 필수)`", "",
                                 "## 항목", ""]
            for mid in sorted(set(mids), key=lambda k: int(k[1:])):
                body.append(f"### {mid}")
                for o, via in origins[mid]:
                    if o in rows:
                        tag: str = f" (병합 {via})" if via else ""
                        body.append(f"- 원 행 {o}{tag}: {' | '.join(rows[o].cells)}")
                body.append("")
            body += ["## 0C 대응표(옛 경로 → 새 경로)", ""]
            body += [f"- {a} → {b}" for a, b in sorted(mapping.items())] or ["- 없음"]
            (out_dir / f"review-{lens}.md").write_text("\n".join(body) + "\n", encoding="utf-8")
        tail: str = f" · 해소 유지 {len(carried)}" if carried else ""
        if pending_ids:
            print(f"요약: residual 결정적 잔존 {len(floor)}{tail} · 리뷰어 확인 대상 {len(pending_ids)}"
                  f"({'·'.join(sorted(to_review))}) · M_m 미정 — --finalize {stamp} → {out_dir}")
            return EXIT_OK
        print(f"요약: residual M_m={len(floor)}(결정적 잔존 {len(floor)}){tail} · 리뷰어 확인 대상 0 → {out_dir}")
        (out_dir / "result.json").write_text(json.dumps(
            {"stamp": stamp, "solved": {m: prev_solved[m] for m in carried}}, ensure_ascii=False, sort_keys=True)
            + "\n", encoding="utf-8")
        return EXIT_RED if floor else EXIT_OK
    results: "dict[str, list[tuple[str, str]]]" = {}
    for lens in to_review:
        path: Path = out_dir / f"result-{lens}.md"
        for cells in _table_rows(path.read_text(encoding="utf-8")) if path.is_file() else []:
            if len(cells) >= 2 and re.fullmatch(r"M\d+", cells[0]):
                results.setdefault(cells[0], []).append((cells[1], cells[2] if len(cells) > 2 else ""))
    reviewer_left: "list[str]" = []
    unknown: "list[str]" = []
    solved: "list[str]" = []
    for mid in pending_ids:
        answers = results.get(mid, [])
        if not answers:
            unknown.append(mid)
            continue
        allowed: "set[str]" = changed | set(watched[mid])      # 해소 근거 = 앵커 이후 바뀐 파일 ∪ 대응 새 경로
        states = []
        for state, ground in answers:
            if state.startswith("해소"):
                locs = [l for l in (_parse_location(t) for t in _locations(ground)) if l]
                states.append("해소" if locs and all(_location_ok(project, l) and os.path.normpath(l[0]) in allowed
                                                    for l in locs) else "잔존")
            elif state.startswith("잔존"):
                states.append("잔존")
            else:
                states.append("판단 불가")
        if all(st == "해소" for st in states):
            solved.append(mid)
        elif "잔존" in states:
            reviewer_left.append(mid)
        else:
            unknown.append(mid)
    m_m: int = len(floor) + len(reviewer_left) + len(unknown)
    lines = [f"# residual 결과 — {stamp}", "", "| M | 판정 |", "|---|---|"]
    lines += [f"| {m} | 잔존(결정적) |" for m in floor] + [f"| {m} | 잔존(리뷰어 · 근거 없는 해소 포함) |" for m in reviewer_left]
    lines += [f"| {m} | 판단 불가 |" for m in unknown] + [f"| {m} | 해소 |" for m in solved]
    lines += [f"| {m} | 해소(직전 {prev_stamp} 이월) |" for m in carried]
    (out_dir / "result.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    snapshot: "dict[str, dict[str, str | None]]" = {m: {p: _file_sha(project, p) for p in watched[m]} for m in solved}
    snapshot.update({m: prev_solved[m] for m in carried})
    (out_dir / "result.json").write_text(json.dumps({"stamp": stamp, "solved": snapshot}, ensure_ascii=False,
                                                    sort_keys=True) + "\n", encoding="utf-8")
    print(f"요약: residual M_m={m_m}(결정적 잔존 {len(floor)} · 리뷰어 잔존 {len(reviewer_left)} · 판단 불가 {len(unknown)}) · "
          f"해소 {len(solved) + len(carried)}{f'(이월 {len(carried)})' if carried else ''} → {out_dir / 'result.md'}")
    return EXIT_RED if m_m else EXIT_OK


# ── self-test ────────────────────────────────────────────────────────────────

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
    try:
        nov, targets = corpus.scope_norm()
        missing = sorted(t for t in targets if t not in corpus.works)
        if missing:
            reds.append(f"대상 목록에 팩 밖 규범: {missing[:5]}")
        key: str = corpus.key_of(corpus.works[nov]["document"])
        spans = corpus.block_spans(key).get(corpus.works[nov]["block"])
        if not spans:
            reds.append(f"적용 범위 규범 {nov} 블록을 설치본에서 찾지 못했다({corpus.platform})")
        else:
            i, j = spans[0]
            body: str = "\n".join(corpus.doc(key).lines[i:j])
            tail: str = body.split(PHRASE_MARK, 1)[1] if PHRASE_MARK in body else ""
            listed = {normalize(p) for p in re.findall(r"«([^«»]+)»", tail)}
            const = {normalize(p) for p in SCOPE_PHRASES}
            if listed != const:
                reds.append(f"적용 한정 어구 상수 ≠ 규범 문면: 상수만 {sorted(const - listed)[:4]} · "
                            f"문면만 {sorted(listed - const)[:4]}")
    except ToolError as exc:
        reds.append(str(exc))
    for r in reds:
        print(f"  red: {r}")
    print(f"요약: self-test {corpus.platform} · 점검 절 {len(tokens)} · 문서 {len({w['document'] for w in corpus.works.values()})} · "
          f"어구 {len(SCOPE_PHRASES)} · red {len(reds)}")
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
    for name in ("plan", "outline"):
        p = sub.add_parser(name)
        p.add_argument("bc")
        p.add_argument("--out", required=True)
    for name in ("check", "sections"):
        sub.add_parser(name).add_argument("audit")
    p = sub.add_parser("check-verdict")
    p.add_argument("audit")
    p.add_argument("--feedback")
    p.add_argument("--final", action="store_true")
    p = sub.add_parser("residual")
    p.add_argument("folder")
    p.add_argument("--candidates")
    p.add_argument("--finalize")
    try:
        ns = ap.parse_args(argv)
    except SystemExit as exc:
        if exc.code == 0:
            return EXIT_OK
        print("요약: refactor_audit 실행 불능 — 인자 오류(위 사용법)")
        return EXIT_ERR
    project: Path = Path(ns.project).resolve()
    try:
        if ns.command in ("plan", "outline"):
            fn = cmd_plan if ns.command == "plan" else cmd_outline
            return fn(project, ns.bc, Path(ns.out))
        if ns.command == "residual":
            return cmd_residual(project, Path(ns.folder), Path(ns.candidates) if ns.candidates else None, ns.finalize)
        corpus: Corpus = Corpus(ns.platform, Path(ns.plugin_root).resolve() if ns.plugin_root else None,
                                Path(ns.rulepack).resolve() if ns.rulepack else None)
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
