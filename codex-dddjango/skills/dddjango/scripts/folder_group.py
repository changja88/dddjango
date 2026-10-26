"""의미 묶음 폴더 — 배치 함수 · 이 실행의 이동 · 묶음 창 판정 (2.28.0 · #654~#656 · D60).

묶음 허용 칸(트리 64 · 66 · 68 · 71 · 73 · 75행 — `standard_tree.Row.groupable`)의 파일을 부모 바로 아래 묶음
폴더 한 계층으로 나눈다. 자리는 파일 이름 · AST(반환 주석 · import · 클래스 기반) · 묶음 폴더 목록만으로 정한다
(`place` — 결정적 · 프로젝트 설정 없음). 검사기 · 게이트 · pre-gate · 감사가 같은 함수를 부른다.

라이브러리: `place` · `lines` · `recognize` · `group_members` · `scan_tree` · `placed_tree` · `rewrite_source` ·
`base_tree` · `expected_moves` · `actual_moves` · `apply_to_copy`.

명령:
  folder_group.py draft <루트> --bc <bc>… [--spec <명세>] [--run <산출물 폴더>] [--legacy-debt-file <목록>] [--summary]
  folder_group.py apply <루트> --run <산출물 폴더> (--debt | --run-moves) [--legacy-debt-file <목록>]
  folder_group.py verify <루트> --run <산출물 폴더> [--window <n>] [--legacy-debt-file <목록>]

코드를 실행하지 않는다(`ast.parse` 만). git 은 읽기만 한다(`apply` 의 `git mv` 밖).
종료: 0 정상(판정 결과는 출력 줄) · 1 사용 · 분석 실패 · 2 `verify` red.
"""
import argparse
import ast
import base64
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Mapping, NamedTuple, Optional, Set, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
import business_vocab  # noqa: E402  — 불용어(STOPWORDS)는 가져다 쓰고 고치지 않는다
import checker_target  # noqa: E402  — 캐시만 남은 인스턴스 술어
import standard_tree  # noqa: E402  — 묶음 허용 칸 · 트리 고정 폴더 이름

# ── 낱말 목록(데이터 — 플러그인 상수 · 프로젝트 설정 없음 · 설계 4.3) ─────────────────────────────
# 손으로 쓴 목록끼리는 겹치지 않는다(러너 시험). 가져온 집합(STOPWORDS · 거절 목록 복사 · 트리 이름)과 겹치면
# 종류 차례 KIND > VERBS > TECH > FORBIDDEN > GENERAL > MODIFIER 로 하나만 남는다(`word_kind`).

# 애매한 20 — 언제나 업무 낱말(C8′). 최종 GENERAL · VERBS 에서 뺀다(STOPWORDS 를 합친 뒤).
AMBIGUOUS: "frozenset[str]" = frozenset({
    "part", "reading", "line", "text", "entry", "share", "slot", "edition", "reference", "snapshot", "check", "code",
    "setting", "title", "body", "message", "draft", "summary", "order", "plan"})
KIND_PREFIX: "frozenset[str]" = frozenset({"invalid", "unknown", "nonexistent", "unsupported"})
KIND_SUFFIX: "frozenset[str]" = frozenset({"mismatch"})
KIND: "frozenset[str]" = KIND_PREFIX | KIND_SUFFIX
# 서비스 앞 동사(v4 27 에서 order · plan 을 뺀 25) ∪ need · apply · use · follow · close.
VERBS: "frozenset[str]" = frozenset({
    "resolve", "compose", "judge", "arrange", "validate", "decide", "assemble", "match", "build", "select", "read",
    "fill", "admit", "rank", "inspect", "fold", "count", "collect", "assign", "locate", "interpret", "derive",
    "calculate", "score", "search", "need", "apply", "use", "follow", "close"})
# 고정 복사 — check-business-vocabulary.py `CURATED_TECH`(하이픈 이름 검사기라 import 불가 · 러너 동기 시험).
CURATED_TECH: "frozenset[str]" = frozenset({
    "django", "ninja", "celery", "redis", "kafka", "smtp", "stripe", "postgres", "postgresql", "mysql", "sqlite",
    "boto3", "s3", "sqs", "grpc", "drf", "rest", "pydantic", "rest_framework"})
TECH_EXTRA: "frozenset[str]" = frozenset({"llm", "rag", "json", "html", "token", "mime", "utc", "idempotency"})
TECH: "frozenset[str]" = CURATED_TECH | TECH_EXTRA
# 고정 복사 — check-naming.py `ABBREV_DENY` · `DEGREE_DENY` · check-domain-model.py `KIND_DENY` · `KIND_SOFT`.
ABBREV_DENY: "frozenset[str]" = frozenset({
    "repo", "uow", "acl", "vo", "ohs", "agg", "spec", "svc", "ctrl", "impl", "mgr", "cfg"})
DEGREE_DENY: "frozenset[str]" = frozenset({
    "common", "shared", "base", "core", "util", "utils", "helper", "helpers", "misc", "etc", "general", "lib",
    "support"})
KIND_DENY: "frozenset[str]" = frozenset({
    "entity", "entities", "value_object", "value_objects", "event", "events", "exception", "exceptions", "model",
    "models", "service", "services", "repository", "repositories", "dto", "dtos", "util", "utils", "helper",
    "helpers", "manager", "managers", "handler", "handlers", "validator", "validators", "factory", "factories",
    "aggregate", "aggregates"})
KIND_SOFT: "frozenset[str]" = frozenset({"data", "objects", "types", "classes", "logic", "rules"})
FORBIDDEN_EXTRA: "frozenset[str]" = frozenset({"service", "gateway", "specification", "framework", "misc"})
# 일반어(손 목록) — 3차 일반어 ∪ v4 작은말 · 상태 · 실패말 · 일반어. 애매한 20 · 동사(match · count) · 종류(invalid ·
# unknown) · 꾸밈말(allowed) · 금지(specification)는 넣지 않는다.
GENERAL: "frozenset[str]" = frozenset({
    # 3차 일반어
    "kind", "table", "pair", "period", "position", "state", "group", "direction", "name", "type", "value", "item",
    "status", "id", "list", "step", "ratio", "distribution", "registry", "date", "time", "day", "month", "year",
    "hour", "moment", "clock", "range", "window", "offset", "number", "notation", "word", "source", "mark", "basis",
    "hit", "release", "span", "axis", "network", "presence", "weight", "ref", "digest", "absence", "classification",
    "stretch", "column", "role", "reason", "definition", "vocabulary", "timeline", "place", "zone", "by",
    # v4 작은말
    "not", "of", "out", "up", "for", "in", "and", "to", "on", "no", "with", "at", "all", "own",
    # v4 상태 · 실패말
    "already", "found", "too", "large", "long", "taken", "rejected", "accepted", "malformed", "unreadable",
    "unavailable", "required", "missing", "duplicate", "empty", "exceeded", "conflict", "corrupted", "failed",
    "failure", "refused", "unreachable", "expired", "used", "full", "soon", "exhausted", "unchanged", "incomplete",
    "regression", "forbidden", "violation", "integrity", "persistence", "hydration", "contention", "insufficient",
    "negative", "mismatched", "removed", "unexpected", "undeliverable", "consumed", "confirmed", "active",
    "suspended", "withdrawn", "registered", "opened", "pending", "started", "stopped", "completed", "generated",
    "calculated", "composed", "ready", "immutable", "unsearchable", "searchable", "suspendable", "reportable",
    "runnable", "claimed", "issued", "closed", "finished", "continue", "corrupt", "rejection", "error", "timeout",
    # v4 일반어
    "result", "save", "data", "info", "payload", "document", "format", "size", "hash", "file", "key", "set", "page",
    "view", "mode", "label", "detail", "amount", "option", "total", "index", "meta", "map", "row", "ids", "max",
    "min", "minimum", "maximum", "lookup", "bundle", "settlement", "variant", "version"})
NUMBER_WORDS: "frozenset[str]" = frozenset({
    "zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve",
    "twenty", "sixty", "hundred", "thousand"})
# 꾸밈말(손 목록) — 3차 48(search 는 동사라 뺌) ∪ v4 49 ∪ 숫자 낱말. 숫자만인 낱말도 꾸밈말이다(`word_kind`).
MODIFIER: "frozenset[str]" = frozenset({
    "annual", "major", "natal", "lunar", "special", "virtual", "hidden", "useful", "viewing", "anchor", "solar",
    "heavenly", "earthly", "daily", "hourly", "monthly", "today", "half", "directional", "principal", "precise",
    "pre", "assumed", "supported", "resolved", "local", "dated", "middle", "absent", "commanding", "scored",
    "summoned", "cut", "road", "counterpart", "favorable", "wall", "noble", "tie", "break", "leap", "cardinal",
    "conception",
    "deep", "english", "korean", "display", "visual", "recommended", "editing", "fixed", "received", "uploaded",
    "linked", "shared", "stored", "retrieved", "digested", "chosen", "allowed", "popular", "current", "effective",
    "historical", "localized", "default", "original", "planned", "assembled", "serialized", "naive", "true",
    "whole", "remaining", "limited", "superseded", "selected", "paired", "carried", "moved", "requested",
    "additional", "balancing", "needle", "first", "later", "new", "last", "next", "previous", "single", "multiple",
}) | NUMBER_WORDS
# 복수 꼴이 아닌 -s 낱말 — 접지 않는다.
NOT_PLURAL: "frozenset[str]" = frozenset({
    "sales", "status", "basis", "series", "news", "analysis", "species", "means", "lens", "gas", "bias", "atlas",
    "chaos", "canvas", "alias", "physics", "ethics", "mathematics", "economics", "statistics", "logistics",
    "analytics"})
# 서비스 이름의 역할 낱말 — 서비스 칸에서 어디서든 뗀다.
ROLE: "frozenset[str]" = frozenset({
    "service", "policy", "resolver", "renderer", "reader", "composer", "filler", "estimator"})


def _tree_folder_names() -> "frozenset[str]":
    """트리 고정 폴더 이름 가운데 밑줄 없는 것(여러 낱말 이름은 자르지 않는다 — `unit_of_work` 는 `work` 를 막지 않음)."""
    out: "set[str]" = set()
    for row in standard_tree.ROWS:
        segs: "list[str]" = row.name.rstrip("/").split("/")
        for seg in (segs if row.name.endswith("/") else segs[:-1]):
            if "<" not in seg and "_" not in seg:
                out.add(seg)
    return frozenset(out)


STOPWORDS: "frozenset[str]" = frozenset(business_vocab.STOPWORDS)
FORBIDDEN: "frozenset[str]" = (_tree_folder_names() | ABBREV_DENY | DEGREE_DENY | KIND_DENY | KIND_SOFT
                               | FORBIDDEN_EXTRA)
# 최종 목록 — 애매한 20 은 STOPWORDS 를 합친 «뒤»에 뺀다(code · message 는 STOPWORDS 에도 있다).
FINAL_GENERAL: "frozenset[str]" = (GENERAL | STOPWORDS) - AMBIGUOUS
FINAL_VERBS: "frozenset[str]" = VERBS - AMBIGUOUS

FORM_MIN: int = 3   # 형성 — 같은 단위 이름 셋(W1)
KEEP_MIN: int = 2   # 유지 — 있는 묶음 둘(W2)

# ── 칸 ─────────────────────────────────────────────────────────────────────────

LAYER: str = "domain_layer"
AGG_KINDS: "dict[str, int]" = {"entity": 64, "value_object": 66, "event": 68, "exception": 71}
SHARED: str = "shared_value_object"
SERVICE: str = "domain_service"
SERVICE_ROW: int = 75
VO_RETURN_ROWS: "frozenset[int]" = frozenset({66, 73})
GROUPABLE_ROWS: "frozenset[int]" = frozenset(r.r for r in standard_tree.ROWS if r.groupable)
_SKIP_DIRS: "frozenset[str]" = frozenset(business_vocab.SKIP_DIRS)


class FolderGroupError(Exception):
    """사용 · 분석 실패 — exit 1."""


class Slot(NamedTuple):
    bc: str            # BC 이름
    parent: str        # 묶음 부모 경로(루트 상대 posix)
    row: int           # 트리 행(64 · 66 · 68 · 71 · 73 · 75)
    agg: "Optional[str]"  # 애그리거트 칸이면 그 애그리거트 이름

    @property
    def service(self) -> bool:
        return self.row == SERVICE_ROW


def slot_of(path: str) -> "Optional[Tuple[Slot, List[str]]]":
    """경로의 묶음 허용 칸과 그 부모 아래 나머지 조각 — 칸 밖이면 None."""
    parts: "list[str]" = path.split("/")
    for i in range(1, len(parts) - 1):
        if parts[i] != LAYER:
            continue
        bc: str = parts[i - 1]
        rest: "list[str]" = parts[i + 1:]
        head: str = "/".join(parts[:i + 1])
        if len(rest) >= 2 and rest[0] == SHARED:
            return Slot(bc, f"{head}/{SHARED}", 73, None), rest[1:]
        if len(rest) >= 2 and rest[0] == SERVICE:
            return Slot(bc, f"{head}/{SERVICE}", SERVICE_ROW, None), rest[1:]
        if len(rest) >= 3 and rest[0] not in (SHARED, SERVICE) and rest[1] in AGG_KINDS:
            return Slot(bc, f"{head}/{rest[0]}/{rest[1]}", AGG_KINDS[rest[1]], rest[0]), rest[2:]
        return None
    return None


class Member(NamedTuple):
    """묶음 칸의 파일 하나 — 서비스 칸 승격(`D/D.py`)은 본체 하나로 센다."""

    path: str                # 지금 경로(승격이면 본체 경로)
    slot: Slot
    group: "Optional[str]"   # 지금 묶음 이름(부모 직계면 None)
    name: str                # 묶음 밖 이름 — `f.py` 또는 승격 `D/D.py`
    stem: str

    @property
    def flat(self) -> str:
        return f"{self.slot.parent}/{self.name}"

    def at(self, group: "Optional[str]") -> str:
        return f"{self.slot.parent}/{group}/{self.name}" if group else self.flat

    @property
    def unit_dir(self) -> "Optional[str]":
        """승격이면 지금 승격 폴더 경로(통째로 옮긴다)."""
        if "/" not in self.name:
            return None
        return self.path.rsplit("/", 1)[0]


def members_of(paths: "Iterable[str]") -> "List[Member]":
    """경로 집합에서 묶음 칸 파일을 고른다(정렬). 서비스 칸 `D/D.py` 는 승격 본체 · 그 밖 `D/*` 는 승격 부품(파일 아님)."""
    pathset: "set[str]" = set(paths)
    out: "list[Member]" = []
    for path in sorted(pathset):
        if not path.endswith(".py"):
            continue
        hit = slot_of(path)
        if hit is None:
            continue
        slot, rest = hit
        p: str = slot.parent
        if len(rest) == 1:
            if rest[0] != "__init__.py":
                out.append(Member(path, slot, None, rest[0], rest[0][:-3]))
            continue
        first: str = rest[0]
        if first.startswith((".", "_")) and first != "__init__.py":
            if first == "__pycache__" or first.startswith("."):
                continue
        promoted: bool = slot.service and f"{p}/{first}/{first}.py" in pathset
        if len(rest) == 2:
            if promoted:
                if rest[1] == f"{first}.py":
                    out.append(Member(path, slot, None, f"{first}/{first}.py", first))
                continue
            if rest[1] != "__init__.py":
                out.append(Member(path, slot, first, rest[1], rest[1][:-3]))
            continue
        if len(rest) == 3 and slot.service and not promoted:
            inner: str = rest[1]
            if f"{p}/{first}/{inner}/{inner}.py" in pathset and rest[2] == f"{inner}.py":
                out.append(Member(path, slot, first, f"{inner}/{inner}.py", inner))
    return out


def group_dirs_of(paths: "Iterable[str]") -> "Set[str]":
    """경로 집합(git 트리 · 사본)에서 묶음 폴더를 읽는다 — 파일이 있는 하위 폴더 가운데 서비스 칸 승격이 아닌 것."""
    pathset: "set[str]" = set(paths)
    out: "set[str]" = set()
    for path in pathset:
        hit = slot_of(path)
        if hit is None or len(hit[1]) < 2:
            continue
        slot, rest = hit
        first: str = rest[0]
        if first == "__pycache__" or first.startswith("."):
            continue
        if slot.service and f"{slot.parent}/{first}/{first}.py" in pathset:
            continue
        out.add(f"{slot.parent}/{first}")
    return out


# ── 파일 시스템 ─────────────────────────────────────────────────────────────────

def recognize(d: Path, row: int) -> str:
    """묶음 부모의 하위 폴더 — `cache`(캐시만 남음 · 건너뜀) · `promotion`(서비스 칸 `D/D.py`) · `group`(설계 7.1)."""
    if checker_target.cache_only_instance(d):
        return "cache"
    if row == SERVICE_ROW and (d / f"{d.name}.py").is_file():
        return "promotion"
    return "group"


def _subdirs(d: Path) -> "List[Path]":
    if not d.is_dir():
        return []
    return [c for c in sorted(d.iterdir()) if c.is_dir() and not c.name.startswith(".") and c.name != "__pycache__"]


def group_members(parent: Path, pattern: str = "*.py", *, promotable: bool) -> "List[Path]":
    """묶음 칸의 파일 — 부모 직계 파일 + (승격 허용이면) 직계 승격 본체 + 묶음마다 직계 파일(`__init__.py` 밖)과
    (승격 허용이면) 묶음 안 승격 본체. 캐시만 남은 폴더는 건너뛴다(설계 7.4 공통 도구)."""
    out: "list[Path]" = sorted(p for p in parent.glob(pattern) if p.is_file()) if parent.is_dir() else []
    row: int = SERVICE_ROW if promotable else 73
    groups: "list[Path]" = []
    for d in _subdirs(parent):
        kind: str = recognize(d, row)
        if kind == "promotion":
            body: Path = d / f"{d.name}.py"
            if _fnmatch(body.name, pattern):
                out.append(body)
        elif kind == "group":
            groups.append(d)
    for g in groups:
        out.extend(sorted(p for p in g.glob(pattern) if p.is_file() and p.name != "__init__.py"))
        if promotable:
            for d in _subdirs(g):
                body = d / f"{d.name}.py"
                if body.is_file() and _fnmatch(body.name, pattern):
                    out.append(body)
    return out


def _fnmatch(name: str, pattern: str) -> bool:
    import fnmatch
    return fnmatch.fnmatch(name, pattern)


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def _bc_dirs(root: Path) -> "List[Path]":
    return [bc for bc in business_vocab.server_bc_dirs(root) if (bc / LAYER).is_dir()]


def scan_tree(root: Path, bcs: "Optional[Iterable[str]]" = None) -> "Tuple[Dict[str, str], Set[str]]":
    """작업 트리의 domain_layer `.py`(경로 → 글)와 묶음 폴더(경로)를 읽는다 — 경로는 루트 상대 posix."""
    want: "Optional[set[str]]" = set(bcs) if bcs is not None else None
    files: "dict[str, str]" = {}
    dirs: "set[str]" = set()
    for bc in _bc_dirs(root):
        if want is not None and bc.name not in want:
            continue
        layer: Path = bc / LAYER
        for py in sorted(layer.rglob("*.py")):
            rel_parts = py.relative_to(root).parts
            if set(rel_parts) & _SKIP_DIRS or any(part.startswith(".") for part in rel_parts):
                continue
            files[py.relative_to(root).as_posix()] = _read_text(py)
        for parent, row in _groupable_parents(layer):
            for d in _subdirs(parent):
                if recognize(d, row) == "group":
                    dirs.add(d.relative_to(root).as_posix())
    return files, dirs


def _groupable_parents(layer: Path) -> "List[Tuple[Path, int]]":
    out: "list[tuple[Path, int]]" = [(layer / SHARED, 73), (layer / SERVICE, SERVICE_ROW)]
    for agg in _subdirs(layer):
        if agg.name in (SHARED, SERVICE):
            continue
        for kind, row in AGG_KINDS.items():
            out.append((agg / kind, row))
    return [(p, r) for p, r in out if p.is_dir()]


# ── 낱말 ───────────────────────────────────────────────────────────────────────

def _is_verb(word: str) -> bool:
    forms: "set[str]" = {word}
    if word.endswith("ies"):
        forms.add(word[:-3] + "y")
    if word.endswith("es"):
        forms.add(word[:-2])
    if word.endswith("s"):
        forms.add(word[:-1])
    return bool(forms & FINAL_VERBS)


def word_kind(word: str, domain: "frozenset[str]") -> str:
    """낱말 종류 — domain · kind · verb · tech · forbidden · general · modifier · business(업무 낱말)."""
    if word in domain:
        return "domain"
    if word in KIND:
        return "kind"
    if _is_verb(word):
        return "verb"
    if word in TECH:
        return "tech"
    if word in FORBIDDEN:
        return "forbidden"
    if word in FINAL_GENERAL:
        return "general"
    if word in MODIFIER or word.isdigit():
        return "modifier"
    return "business"


def _fold(word: str, words: "frozenset[str]") -> str:
    """복수 접기 — 단수가 그 부모 아래 이름에 낱말로 있을 때만(설계 4.2 의 2)."""
    if word in NOT_PLURAL or word in FORBIDDEN:
        return word
    if word.endswith("ies") and len(word) > 3 and word[:-3] + "y" in words:
        return word[:-3] + "y"
    if word.endswith("s") and len(word) >= 4 and not word.endswith(("ss", "us", "is")) and word[:-1] in words:
        return word[:-1]
    return word


MEANINGFUL: "frozenset[str]" = frozenset({"business", "domain", "forbidden", "verb", "tech"})
EMPTY_KINDS: "frozenset[str]" = frozenset({"general", "modifier", "kind"})


class Ctx(NamedTuple):
    """한 묶음 부모의 셈 재료(설계 4.1 — 범위는 그 부모 아래 모든 묶음 칸 파일)."""

    slot: Slot
    words: "frozenset[str]"     # 그 부모 아래 파일 이름의 낱말(접기 재료)
    domain: "frozenset[str]"    # 영역 낱말(BC · 그 애그리거트)
    phrases: "frozenset[Tuple[str, ...]]"  # 알려진 구(같은 BC 의 여러 낱말 애그리거트 · 자기 애그리거트 밖)


class Words(NamedTuple):
    tokens: "Tuple[str, ...]"
    kinds: "Tuple[str, ...]"


def _domain_words(slot: Slot, words: "frozenset[str]") -> "frozenset[str]":
    raw: "list[str]" = slot.bc.split("_") + (slot.agg.split("_") if slot.agg else [])
    return frozenset(raw) | frozenset(_fold(w, words) for w in raw)


def words_of(stem: str, ctx: Ctx) -> Words:
    """이름 낱말(설계 4.2) — 자르기 · 복수 접기 · 종류 접두 · 접미 떼기 · (서비스 칸) 앞 동사 · 역할 낱말 떼기."""
    t: "list[str]" = [_fold(w, ctx.words) for w in stem.split("_") if w]
    while t and t[0] in KIND_PREFIX:
        t = t[1:]
    while t and t[-1] in KIND_SUFFIX:
        t = t[:-1]
    if ctx.slot.service:
        if t and word_kind(t[0], ctx.domain) == "verb":
            t = t[1:]
        t = [w for w in t if w not in ROLE]
    return Words(tuple(t), tuple(word_kind(w, ctx.domain) for w in t))


def _bare(kinds: "Tuple[str, ...]", i: int) -> bool:
    """맨 자리 — 바로 앞 낱말이 꾸밈말이 아니다(첫 낱말 포함). 꾸밈말 바로 뒤는 머리 자리."""
    return i == 0 or kinds[i - 1] != "modifier"


def _combo_ok(seq: "Tuple[str, ...]", kinds: "Tuple[str, ...]") -> bool:
    """조합 구(설계 4.5 의 2) — 앞은 꾸밈말 · 영역 낱말, 머리는 업무 낱말 · 일반어 · 영역 낱말, ⓐ ⓑ ⓒ 아님 · 금지 낱말 없음."""
    pre, head = kinds[:-1], kinds[-1]
    if not all(k in ("modifier", "domain") for k in pre) or head not in ("business", "general", "domain"):
        return False
    if all(k == "domain" for k in pre) and head == "business":
        return False
    if all(k == "modifier" for k in kinds) or all(k == "domain" for k in kinds):
        return False
    return not any(w in FORBIDDEN for w in seq)


def _contains(tokens: "Tuple[str, ...]", seq: "Tuple[str, ...]") -> bool:
    n: int = len(seq)
    return any(tokens[i:i + n] == seq for i in range(len(tokens) - n + 1))


def _candidates(named: "List[Words]", ctx: Ctx) -> "Set[Tuple[str, ...]]":
    """후보 단위(설계 4.5) — 이름 셋 이상(그 부모 아래 모든 파일)."""
    single: "dict[Tuple[str, ...], int]" = {}
    combo: "dict[Tuple[str, ...], int]" = {}
    for w in named:
        seen_s: "set[Tuple[str, ...]]" = set()
        seen_c: "set[Tuple[str, ...]]" = set()
        for i, word in enumerate(w.tokens):
            if w.kinds[i] == "business" and _bare(w.kinds, i):
                seen_s.add((word,))
        for k in (2, 3):
            for i in range(len(w.tokens) - k + 1):
                seq = w.tokens[i:i + k]
                if _combo_ok(seq, w.kinds[i:i + k]):
                    seen_c.add(seq)
        for u in seen_s:
            single[u] = single.get(u, 0) + 1
        for u in seen_c:
            combo[u] = combo.get(u, 0) + 1
    out: "set[Tuple[str, ...]]" = {u for u, c in single.items() if c >= FORM_MIN}
    out |= {u for u, c in combo.items() if c >= FORM_MIN}
    for phrase in ctx.phrases:
        if not any(x in FORBIDDEN for x in phrase) and sum(1 for w in named if _contains(w.tokens, phrase)) >= FORM_MIN:
            out.add(phrase)
    return out


def _valid_dir_unit(name: str, ctx: Ctx) -> bool:
    """있는 묶음 폴더 이름이 단위 꼴인가(금지 꼴 — 금지 낱말 · 영역 낱말만 · 일반어 · 꾸밈말 홀로 — 이면 아니다)."""
    seq: "Tuple[str, ...]" = tuple(name.split("_"))
    if not all(seq) or any(w in FORBIDDEN for w in seq):
        return False
    kinds = tuple(word_kind(w, ctx.domain) for w in seq)
    if len(seq) == 1:
        return kinds[0] == "business"
    if seq in ctx.phrases:
        return True
    return len(seq) <= 3 and _combo_ok(seq, kinds)


def _gname(unit: "Tuple[str, ...]") -> str:
    return "_".join(unit)


# ── AST 재료 (import · 클래스 · 반환) ──────────────────────────────────────────

def module_of(path: str) -> str:
    mod: str = path[:-3] if path.endswith(".py") else path
    mod = mod.replace("/", ".")
    return mod[: -len(".__init__")] if mod.endswith(".__init__") else mod


def package_of(path: str) -> str:
    mod: str = module_of(path)
    return mod if path.endswith("/__init__.py") else mod.rpartition(".")[0]


def _resolve_from(package: str, level: int, module: "Optional[str]") -> str:
    if level == 0:
        return module or ""
    parts: "list[str]" = package.split(".") if package else []
    base: "list[str]" = parts[: len(parts) - (level - 1)] if level - 1 <= len(parts) else []
    return ".".join(base + ([module] if module else []))


def _parse(text: str) -> "Optional[ast.Module]":
    try:
        return ast.parse(text)
    except (SyntaxError, ValueError):
        return None


class Source:
    """한 파일의 AST 재료 — 묶임 이름 · import 대상 · 클래스."""

    def __init__(self, path: str, text: str) -> None:
        self.path: str = path
        self.tree: "Optional[ast.Module]" = _parse(text)
        self.package: str = package_of(path)
        self.classes: "dict[str, ast.ClassDef]" = {}
        self.bindings: "dict[str, Tuple[str, Optional[str]]]" = {}   # 이름 → (모듈, 그 모듈의 이름 | None)
        self.targets: "list[Tuple[str, Optional[str]]]" = []          # import 대상 (모듈, 이름 | None)
        if self.tree is None:
            return
        for node in self.tree.body:
            if isinstance(node, ast.ClassDef):
                self.classes[node.name] = node
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Import):
                for a in node.names:
                    self.targets.append((a.name, None))
                    if a.asname:
                        self.bindings[a.asname] = (a.name, None)
                    else:
                        top: str = a.name.split(".")[0]
                        self.bindings[top] = (top, None)
            elif isinstance(node, ast.ImportFrom):
                base: str = _resolve_from(self.package, node.level, node.module)
                for a in node.names:
                    if a.name == "*":
                        self.targets.append((base, None))
                        continue
                    self.targets.append((base, a.name))
                    self.bindings[a.asname or a.name] = (base, a.name)


class BcIndex:
    """한 BC 의 모듈 색인 — import 이름 → 파일(접두가 다른 뿌리 · `<bc>.domain_layer.` 꼬리로도 찾는다)."""

    def __init__(self, bc: str, sources: "Dict[str, Source]") -> None:
        self.bc: str = bc
        self.sources: "Dict[str, Source]" = sources
        self.full: "dict[str, str]" = {}
        self.tail: "dict[str, str]" = {}
        key: str = f"{bc}.{LAYER}"
        for path in sources:
            mod: str = module_of(path)
            self.full[mod] = path
            at: int = mod.find(key)
            if at == 0 or (at > 0 and mod[at - 1] == "."):
                self.tail[mod[at:]] = path

    def file(self, dotted: str) -> "Optional[str]":
        if dotted in self.full:
            return self.full[dotted]
        key: str = f"{self.bc}.{LAYER}"
        at: int = dotted.find(key)
        if at == 0 or (at > 0 and dotted[at - 1] == "."):
            return self.tail.get(dotted[at:])
        return None

    def symbol(self, path: str, name: str, depth: int = 0) -> "Optional[Tuple[str, str]]":
        """이름 → (정의 파일, 클래스) — 재수출을 다섯 단계까지 따라간다."""
        src: "Optional[Source]" = self.sources.get(path)
        if src is None or depth > 5:
            return None
        if name in src.classes:
            return path, name
        bound = src.bindings.get(name)
        if bound is None or bound[1] is None:
            return None
        module, attr = bound
        if self.file(f"{module}.{attr}") is not None:
            return None  # 모듈을 묶은 이름 — 클래스가 아니다
        target: "Optional[str]" = self.file(module)
        return self.symbol(target, attr, depth + 1) if target is not None else None

    def module_binding(self, path: str, name: str) -> "Optional[str]":
        """이름이 모듈을 묶었으면 그 모듈 파일."""
        src: "Optional[Source]" = self.sources.get(path)
        if src is None or name not in src.bindings:
            return None
        module, attr = src.bindings[name]
        return self.file(f"{module}.{attr}" if attr else module)

    def used_files(self, path: str) -> "Set[str]":
        """파일이 import 로 쓰는 BC 파일(모듈 import · 이름 import 의 정의 파일 — 재수출을 따라감)."""
        src: "Optional[Source]" = self.sources.get(path)
        out: "set[str]" = set()
        if src is None:
            return out
        for module, name in src.targets:
            if name is not None:
                sub: "Optional[str]" = self.file(f"{module}.{name}")
                if sub is not None:
                    out.add(sub)
                    continue
                target: "Optional[str]" = self.file(module)
                if target is None:
                    continue
                found = self.symbol(target, name)
                out.add(found[0] if found is not None else target)
            else:
                target = self.file(module)
                if target is not None:
                    out.add(target)
        out.discard(path)
        return out

    def refs(self, path: str, node: "Optional[ast.expr]") -> "List[Tuple[str, str]]":
        """반환 주석 → (정의 파일, 클래스) 목록 — Optional · Union · 원소 · 값 타입 · 그 밖 제네릭 인자 · 따옴표 주석."""
        out: "list[Tuple[str, str]]" = []
        self._refs(path, node, out, 0)
        return out

    def _refs(self, path: str, node: "Optional[ast.expr]", out: "list", depth: int) -> None:
        if node is None or depth > 12:
            return
        if isinstance(node, ast.Constant):
            if isinstance(node.value, str):
                try:
                    inner = ast.parse(node.value, mode="eval").body
                except (SyntaxError, ValueError):
                    return
                self._refs(path, inner, out, depth + 1)
            return
        if isinstance(node, ast.Name):
            found = self.symbol(path, node.id)
            if found is not None:
                out.append(found)
            return
        if isinstance(node, ast.Attribute):
            chain: "list[str]" = []
            cur: ast.expr = node
            while isinstance(cur, ast.Attribute):
                chain.append(cur.attr)
                cur = cur.value
            if not isinstance(cur, ast.Name):
                return
            chain.reverse()
            module_file: "Optional[str]" = self.module_binding(path, cur.id)
            if module_file is None:
                return
            mod: str = module_of(module_file)
            for attr in chain[:-1]:
                nxt: "Optional[str]" = self.file(f"{mod}.{attr}")
                if nxt is None:
                    return
                mod = module_of(nxt)
                module_file = nxt
            found = self.symbol(module_file, chain[-1])
            if found is not None:
                out.append(found)
            return
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
            self._refs(path, node.left, out, depth + 1)
            self._refs(path, node.right, out, depth + 1)
            return
        if isinstance(node, ast.Subscript):
            base: str = node.value.id if isinstance(node.value, ast.Name) else (
                node.value.attr if isinstance(node.value, ast.Attribute) else "")
            sl: ast.expr = node.slice
            if sys.version_info < (3, 9) and isinstance(sl, getattr(ast, "Index", ())):  # pragma: no cover
                sl = sl.value  # type: ignore[attr-defined]
            args: "list[ast.expr]" = list(sl.elts) if isinstance(sl, ast.Tuple) else [sl]
            if base == "Literal":
                return
            if base in ("dict", "Dict", "Mapping", "MutableMapping", "OrderedDict", "defaultdict", "DefaultDict"):
                args = args[-1:]
            elif base == "Annotated":
                args = args[:1]
            for a in args:
                if isinstance(a, ast.List):
                    for e in a.elts:
                        self._refs(path, e, out, depth + 1)
                else:
                    self._refs(path, a, out, depth + 1)

    def is_exception(self, path: str, name: str, depth: int = 0) -> bool:
        src: "Optional[Source]" = self.sources.get(path)
        if src is None or depth > 8 or name not in src.classes:
            return False
        for base in src.classes[name].bases:
            text: str = base.id if isinstance(base, ast.Name) else (base.attr if isinstance(base, ast.Attribute) else "")
            if text in ("Exception", "BaseException") or text.endswith(("Error", "Exception")):
                return True
            if isinstance(base, ast.Name):
                found = self.symbol(path, base.id)
                if found is not None and found != (path, name) and self.is_exception(found[0], found[1], depth + 1):
                    return True
        return False


def _decision_functions(tree: "Optional[ast.Module]", stem: str) -> "List[ast.AST]":
    """결정 함수(설계 4.7 의 1) — ① stem 이름 함수 ② 하나뿐인 공개 정의 ③ 클래스면 `__call__` · 하나뿐인 공개 메서드
    ④ 여럿이면 모든 공개 함수 · 메서드."""
    if tree is None:
        return []
    fdefs = (ast.FunctionDef, ast.AsyncFunctionDef)
    public: "list[ast.AST]" = [n for n in tree.body if isinstance(n, fdefs + (ast.ClassDef,))
                               and not n.name.startswith("_")]  # type: ignore[attr-defined]
    same: "list[ast.AST]" = [n for n in public if isinstance(n, fdefs) and n.name == stem]  # type: ignore
    if same:
        return same
    if len(public) == 1:
        only = public[0]
        if not isinstance(only, ast.ClassDef):
            return [only]
        methods = [m for m in only.body if isinstance(m, fdefs)]
        call = [m for m in methods if m.name == "__call__"]
        if call:
            return call
        return [m for m in methods if not m.name.startswith("_")]
    out: "list[ast.AST]" = []
    for n in public:
        if isinstance(n, ast.ClassDef):
            out += [m for m in n.body if isinstance(m, fdefs) and not m.name.startswith("_")]
        else:
            out.append(n)
    return out


# ── 배치 ───────────────────────────────────────────────────────────────────────

class FilePlace(NamedTuple):
    member: Member
    target: str               # 목표 경로
    group: "Optional[str]"    # 목표 묶음 이름(부모면 None)
    reason: str


class Placement(NamedTuple):
    files: "Dict[str, FilePlace]"                 # 지금 경로 → 자리
    final: "Dict[str, Set[str]]"                  # 묶음 부모 → 서는 묶음 이름
    existing: "Dict[str, Set[str]]"               # 묶음 부모 → 있는 묶음 이름
    died: "List[Tuple[str, str, str, int]]"       # (부모, 이름, 까닭, 셈) — 죽은 차례
    tree: "Set[str]"                              # 계산에 쓴 파일 경로 전부


class _Assign(NamedTuple):
    group: "Optional[str]"
    anchor: str      # bare · phrase · head · return · users · none
    reason: str


def _match(w: Words, units: "Iterable[Tuple[str, ...]]") -> "Optional[Tuple[Tuple[str, ...], str, List[str]]]":
    """왼쪽부터 그 자리에서 시작하는 살아 있는 단위 가운데 가장 긴 것 — 처음 잡힌 단위가 주인(설계 4.6)."""
    pool: "list[Tuple[str, ...]]" = sorted(set(units), key=lambda u: (-len(u), u))
    matches: "list[Tuple[Tuple[str, ...], int]]" = []
    i: int = 0
    while i < len(w.tokens):
        hit: "Optional[Tuple[str, ...]]" = None
        for u in pool:
            if _starts_at(w.tokens, i, u):
                hit = u
                break
        if hit is None:
            i += 1
            continue
        matches.append((hit, i))
        i += len(hit)
    if not matches:
        return None
    owner, at = matches[0]
    anchor: str = "phrase" if len(owner) > 1 else ("bare" if _bare(w.kinds, at) else "head")
    return owner, anchor, [_gname(u) for u, _ in matches if u != owner]


def _starts_at(tokens: "Tuple[str, ...]", i: int, unit: "Tuple[str, ...]") -> bool:
    return tokens[i:i + len(unit)] == unit


def _no_match_reason(w: Words) -> str:
    if "business" in w.kinds:
        return "부모 3미만"
    return "부모 뜻낱말"


def place(files: "Mapping[str, str]", dirs: "Iterable[str]" = ()) -> Placement:
    """묶음 자리(설계 4) — files: 루트 상대 경로 → 글(domain_layer `.py`) · dirs: 있는 묶음 폴더 경로."""
    members: "list[Member]" = members_of(files)
    dirset: "set[str]" = set(dirs)
    by_bc: "dict[str, list[Member]]" = {}
    for m in members:
        by_bc.setdefault(m.slot.bc, []).append(m)
    out_files: "dict[str, FilePlace]" = {}
    final: "dict[str, set[str]]" = {}
    existing: "dict[str, set[str]]" = {}
    died: "list[Tuple[str, str, str, int]]" = []
    for bc in sorted(by_bc):
        bc_files: "dict[str, str]" = {p: t for p, t in files.items() if _bc_of(p) == bc}
        _place_bc(bc, by_bc[bc], bc_files, dirset, out_files, final, existing, died)
    return Placement(out_files, final, existing, died, set(files))


def _bc_of(path: str) -> "Optional[str]":
    parts: "list[str]" = path.split("/")
    for i in range(1, len(parts)):
        if parts[i] == LAYER:
            return parts[i - 1]
    return None


def _aggregates(members: "List[Member]", files: "Mapping[str, str]") -> "Set[str]":
    out: "set[str]" = set()
    for p in files:
        parts: "list[str]" = p.split("/")
        if LAYER in parts:
            i: int = parts.index(LAYER)
            if len(parts) > i + 2 and parts[i + 1] not in (SHARED, SERVICE) and parts[i + 1] != "__pycache__":
                out.add(parts[i + 1])
    out |= {m.slot.agg for m in members if m.slot.agg}
    return out


def _place_bc(bc: str, members: "List[Member]", files: "Mapping[str, str]", dirset: "Set[str]",
              out_files: "dict", final: "dict", existing: "dict", died: "list") -> None:
    sources: "dict[str, Source]" = {p: Source(p, t) for p, t in files.items()}
    index = BcIndex(bc, sources)
    aggs: "set[str]" = _aggregates(members, files)
    slots: "dict[str, Slot]" = {}
    by_parent: "dict[str, list[Member]]" = {}
    for m in members:
        slots[m.slot.parent] = m.slot
        by_parent.setdefault(m.slot.parent, []).append(m)
    for d in sorted(dirset):
        hit = slot_of(d + "/x.py")
        if hit is not None and hit[0].bc == bc and len(hit[1]) == 2:
            slots.setdefault(hit[0].parent, hit[0])
            by_parent.setdefault(hit[0].parent, [])
    ctxs: "dict[str, Ctx]" = {}
    words: "dict[str, Words]" = {}
    for parent, slot in slots.items():
        raw: "frozenset[str]" = frozenset(x for m in by_parent[parent] for x in m.stem.split("_") if x)
        phrases: "frozenset[Tuple[str, ...]]" = frozenset(
            tuple(a.split("_")) for a in aggs if "_" in a and a != slot.agg)
        ctxs[parent] = Ctx(slot, raw, _domain_words(slot, raw), phrases)
        for m in by_parent[parent]:
            words[m.path] = words_of(m.stem, ctxs[parent])
    existing_bc: "dict[str, set[str]]" = {p: {d.rsplit("/", 1)[1] for d in dirset if d.rsplit("/", 1)[0] == p}
                                          for p in slots}
    universe: "dict[str, set[Tuple[str, ...]]]" = {}
    for parent, ctx in ctxs.items():
        named: "list[Words]" = [words[m.path] for m in by_parent[parent]]
        u: "set[Tuple[str, ...]]" = _candidates(named, ctx)
        u |= {tuple(g.split("_")) for g in existing_bc[parent] if _valid_dir_unit(g, ctx)}
        universe[parent] = u
    vo_side: "set[Tuple[str, ...]]" = set()
    for parent, ctx in ctxs.items():
        if ctx.slot.row in VO_RETURN_ROWS:
            vo_side |= universe[parent]
    for parent, ctx in ctxs.items():
        if ctx.slot.service:
            universe[parent] |= vo_side
    # 서비스 반환 · 쓰는 곳 재료(바퀴와 상관없이 한 번)
    member_by_path: "dict[str, Member]" = {m.path: m for m in members}
    vo_class: "dict[Tuple[str, str], Member]" = {}
    returns: "dict[str, list[Tuple[str, str]]]" = {}
    for m in members:
        if m.slot.service:
            refs: "list[Tuple[str, str]]" = []
            src: "Optional[Source]" = sources.get(m.path)
            for fdef in _decision_functions(src.tree if src else None, m.stem):
                refs += index.refs(m.path, getattr(fdef, "returns", None))
            vo_refs: "list[Tuple[str, str]]" = []
            for ref in refs:
                owner: "Optional[Member]" = member_by_path.get(ref[0])
                if owner is not None and owner.slot.row in VO_RETURN_ROWS and not index.is_exception(*ref):
                    vo_refs.append(ref)
                    vo_class[ref] = owner
            returns[m.path] = sorted(set(vo_refs))
    users: "dict[str, list[Member]]" = {}
    for u in members:
        for used in index.used_files(u.path):
            if used in member_by_path:
                users.setdefault(used, []).append(u)
    live: "dict[str, set[Tuple[str, ...]]]" = {p: set(u) for p, u in universe.items()}
    svc_stems: "dict[str, set[str]]" = {p: {m.stem for m in by_parent[p]} for p in slots if slots[p].service}
    while True:
        assign: "dict[str, _Assign]" = _assign_round(members, words, live, returns, vo_class, users, ctxs)
        bad: "list[Tuple[int, str, str, Tuple[str, ...], str]]" = []
        for parent in sorted(slots):
            entries: "dict[str, list[_Assign]]" = {}
            parent_count: int = 0
            for m in by_parent[parent]:
                a: _Assign = assign[m.path]
                if a.group is None:
                    parent_count += 1
                else:
                    entries.setdefault(a.group, []).append(a)
            realized: "list[str]" = sorted({_gname(u) for u in live[parent]
                                            if entries.get(_gname(u)) or _gname(u) in existing_bc[parent]})
            for g in realized:
                got: "list[_Assign]" = entries.get(g, [])
                n: int = len(got)
                why: "Optional[str]" = None
                if g not in existing_bc[parent]:
                    anchored: int = sum(1 for a in got if a.anchor in ("bare", "phrase", "return"))
                    if anchored < FORM_MIN:
                        why, n = "셋 미만", anchored
                else:
                    if n < KEEP_MIN:
                        why = "둘 미만"
                    elif not any(a.anchor in ("bare", "phrase", "head", "return") for a in got):
                        why = "닻 없음"
                if why is None and len(realized) == 1 and parent_count == 0:
                    why = "통째(E3)"
                if why is None and slots[parent].service and g in svc_stems.get(parent, set()):
                    why = "같은 이름(M3)"
                if why is not None:
                    bad.append((n, parent, g, tuple(g.split("_")), why))
        if not bad:
            break
        worst = min(bad, key=lambda b: (b[0], b[1], b[2]))
        live[worst[1]].discard(worst[3])
        died.append((worst[1], worst[2], worst[4], worst[0]))
    for parent in slots:
        final[parent] = set()
        existing[parent] = set(existing_bc[parent])
    for m in members:
        a = assign[m.path]
        out_files[m.path] = FilePlace(m, m.at(a.group), a.group, a.reason)
        if a.group is not None:
            final[m.slot.parent].add(a.group)
    for parent in slots:
        for g in existing_bc[parent]:
            if tuple(g.split("_")) in live[parent] and any(
                    fp.group == g for fp in out_files.values() if fp.member.slot.parent == parent):
                final[parent].add(g)


def _assign_round(members: "List[Member]", words: "Dict[str, Words]", live: "Dict[str, Set[Tuple[str, ...]]]",
                  returns: "Dict[str, List[Tuple[str, str]]]", vo_class: "Dict[Tuple[str, str], Member]",
                  users: "Dict[str, List[Member]]", ctxs: "Dict[str, Ctx]") -> "Dict[str, _Assign]":
    """한 바퀴의 배정 — 값 객체 칸 이름 배정(고정) 뒤 서비스(반환) ↔ 쓰는 곳을 고정점까지(설계 4.9)."""
    assign: "dict[str, _Assign]" = {}
    c7: "list[Member]" = []
    services: "list[Member]" = []
    for m in members:
        if m.slot.service:
            services.append(m)
            continue
        w: Words = words[m.path]
        hit = _match(w, live[m.slot.parent])
        if hit is not None:
            assign[m.path] = _named(hit)
        elif any(k in MEANINGFUL for k in w.kinds):
            assign[m.path] = _Assign(None, "none", _no_match_reason(w))
        else:
            assign[m.path] = _Assign(None, "users", "쓰는 곳 부모")
            c7.append(m)
    ret_g: "dict[str, Optional[str]]" = {}
    for _ in range(len(members) + 2):
        changed: bool = False
        for m in services:
            new, rg = _service_assign(m, words[m.path], live[m.slot.parent], returns[m.path], vo_class, assign)
            ret_g[m.path] = rg
            if assign.get(m.path) != new:
                assign[m.path] = new
                changed = True
        for m in c7:
            locs: "set[Optional[str]]" = set()
            for u in users.get(m.path, []):
                if u.slot.service and m.path in {vo_class[r].path for r in returns.get(u.path, []) if r in vo_class}:
                    continue  # 그 파일을 돌려주는 서비스 자신은 뺀다
                locs.add(ret_g.get(u.path) if u.slot.service else assign[u.path].group)
            g: "Optional[str]" = next(iter(locs)) if len(locs) == 1 else None
            if g is not None and tuple(g.split("_")) in live[m.slot.parent]:
                new = _Assign(g, "users", f"쓰는 곳 {g}")
            else:
                new = _Assign(None, "users", "쓰는 곳 부모")
            if assign[m.path] != new:
                assign[m.path] = new
                changed = True
        if not changed:
            break
    return assign


def _named(hit: "Tuple[Tuple[str, ...], str, List[str]]") -> _Assign:
    owner, anchor, pushed = hit
    g: str = _gname(owner)
    if pushed:
        return _Assign(g, anchor, f"왼쪽 {g} 밀림 {' '.join(pushed)}")
    return _Assign(g, anchor, f"{'머리' if anchor == 'head' else '이름'} {g}")


def _service_assign(m: Member, w: Words, live: "Set[Tuple[str, ...]]", refs: "List[Tuple[str, str]]",
                    vo_class: "Dict[Tuple[str, str], Member]",
                    assign: "Dict[str, _Assign]") -> "Tuple[_Assign, Optional[str]]":
    """서비스 자리(설계 4.7) — 돌려주는 값 객체의 묶음 · 없으면 이름 맞추기. 둘째 값은 쓰는 곳 셈의 자리."""
    if refs:
        locs: "set[Optional[str]]" = set()
        for ref in refs:
            owner: Member = vo_class[ref]
            a: "Optional[_Assign]" = assign.get(owner.path)
            locs.add(a.group if a is not None else owner.group)
        if len(locs) == 1 and None not in locs:
            g: str = min(x for x in locs if x is not None)
            if tuple(g.split("_")) in live:
                return _Assign(g, "return", f"반환 {refs[0][1]} {g}"), g
            return _Assign(None, "none", "반환 부모"), g
        return _Assign(None, "none", "반환 부모"), None
    hit = _match(w, live)
    if hit is not None:
        a2: _Assign = _named(hit)
        return a2, a2.group
    return _Assign(None, "none", _no_match_reason(w)), None


# ── #656 줄 ───────────────────────────────────────────────────────────────────

MAKE: str = "묶음 `{}/` 을(를) 만든다"
UNDO: str = "묶음 `{}/` 을(를) 푼다"
PUT: str = "묶음 `{}/` 에 둔다"
TO_PARENT: str = "부모에 둔다"


def lines(placement: Placement) -> "List[Tuple[str, str]]":
    """#656 줄(주어, 메시지) — 만들 묶음(부모 `__init__.py` 한 줄) · 풀 묶음(그 `__init__.py`) · 옮길 파일(설계 7.3)."""
    out: "list[Tuple[str, str]]" = []
    for parent in sorted(placement.final):
        fin: "set[str]" = placement.final[parent]
        ex: "set[str]" = placement.existing.get(parent, set())
        for g in sorted(fin - ex):
            out.append((f"{parent}/__init__.py", MAKE.format(g)))
        for g in sorted(ex - fin):
            init: str = f"{parent}/{g}/__init__.py"
            inside: "list[str]" = sorted(p for p in placement.tree if p.startswith(f"{parent}/{g}/"))
            subject: str = init if init in placement.tree else (inside[0] if inside else f"{parent}/{g}/")
            out.append((subject, UNDO.format(g)))
    for path, fp in sorted(placement.files.items()):
        if fp.group == fp.member.group:
            continue
        parent = fp.member.slot.parent
        if fp.group is None:
            out.append((path, TO_PARENT))
        elif fp.group in placement.existing.get(parent, set()) and fp.group in placement.final.get(parent, set()):
            out.append((path, PUT.format(fp.group)))
    return sorted(out)


# ── 옮긴 트리(메모리) · import 치환 ────────────────────────────────────────────

def placement_moves(placement: Placement) -> "List[Tuple[str, str]]":
    """자리대로 옮길 경로 쌍 — 승격은 폴더 통째(부품 포함)."""
    pairs: "list[Tuple[str, str]]" = []
    for path, fp in sorted(placement.files.items()):
        if fp.target == path:
            continue
        unit: "Optional[str]" = fp.member.unit_dir
        if unit is None:
            pairs.append((path, fp.target))
            continue
        new_unit: str = fp.target.rsplit("/", 1)[0]
        for p in sorted(placement.tree):
            if p.startswith(unit + "/"):
                pairs.append((p, new_unit + p[len(unit):]))
    return pairs


def module_moves(pairs: "Iterable[Tuple[str, str]]") -> "Dict[str, str]":
    out: "dict[str, str]" = {}
    for old, new in pairs:
        if old.endswith(".py") and new.endswith(".py"):
            out[module_of(old)] = module_of(new)
    return out


def _fq(dotted: str, moves: "Mapping[str, str]") -> str:
    parts: "list[str]" = dotted.split(".")
    for i in range(len(parts), 0, -1):
        key: str = ".".join(parts[:i])
        if key in moves:
            return moves[key] + "".join("." + x for x in parts[i:])
    return dotted


def _relative(package: str, target: str) -> "Tuple[int, str]":
    """package 에서 target 모듈을 부르는 상대 꼴 (점 수, 모듈) — 공통 접두가 가장 긴 꼴."""
    n: "list[str]" = package.split(".") if package else []
    t: "list[str]" = target.split(".") if target else []
    c: int = 0
    while c < len(n) and c < len(t) and n[c] == t[c]:
        c += 1
    return len(n) - c + 1, ".".join(t[c:])


_FROM_RE: "re.Pattern[bytes]" = re.compile(rb"\Afrom\s+((?:\.\s*)*[\w.\s\\]*?)\s+import\b")


def _alias_text(a: ast.alias) -> str:
    return f"{a.name} as {a.asname}" if a.asname else a.name


def rewrite_source(text: str, old_path: str, new_path: str, moves: "Mapping[str, str]",
                   string_sub: "Optional[Callable[[str], str]]" = None) -> str:
    """import 기계 치환(설계 8 — ⓐ 점 경로 · ⓑ `from 패키지 import 모듈` 나눔 · ⓒ 상대 꼴 지킴 · ⓓ 모듈 속성 사슬 ·
    ⓔ 문자열 속 점 경로). moves 는 옛 모듈 → 새 모듈. 파싱 불능이면 글을 그대로 돌려준다."""
    tree: "Optional[ast.Module]" = _parse(text)
    if tree is None:
        return text
    data: bytes = text.encode("utf-8")
    starts: "list[int]" = [0] + [i + 1 for i, b in enumerate(data) if b == 10]

    def off(line: int, col: int) -> int:
        return starts[line - 1] + col

    old_pkg: str = package_of(old_path)
    new_pkg: str = package_of(new_path)
    moved_file: bool = old_path != new_path
    edits: "list[Tuple[int, int, bytes]]" = []
    bindings: "dict[str, str]" = {}
    skip: "set[int]" = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.JoinedStr):
            skip |= {id(x) for x in ast.walk(node)}
        if isinstance(node, ast.Import):
            for a in node.names:
                if a.asname:
                    bindings[a.asname] = a.name
                else:
                    bindings[a.name.split(".")[0]] = a.name.split(".")[0]
            new_names = [ast.alias(name=_fq(a.name, moves), asname=a.asname) for a in node.names]
            if [x.name for x in new_names] != [a.name for a in node.names]:
                stmt = "import " + ", ".join(_alias_text(a) for a in new_names)
                edits.append((off(node.lineno, node.col_offset), off(node.end_lineno, node.end_col_offset),
                              stmt.encode("utf-8")))
        elif isinstance(node, ast.ImportFrom):
            base: str = _resolve_from(old_pkg, node.level, node.module)
            for a in node.names:
                if a.name != "*":
                    bindings[a.asname or a.name] = f"{base}.{a.name}"
            groups: "dict[str, list[ast.alias]]" = {}
            for a in node.names:
                full: str = f"{base}.{a.name}"
                nb: str = moves[full].rpartition(".")[0] if a.name != "*" and full in moves else _fq(base, moves)
                groups.setdefault(nb, []).append(a)
            if list(groups) == [base] and not (moved_file and node.level > 0):
                continue

            def modtext(nb: str) -> str:
                if node.level == 0:
                    return nb
                level, mod = _relative(new_pkg, nb)
                return "." * level + mod

            seg_start: int = off(node.lineno, node.col_offset)
            seg_end: int = off(node.end_lineno, node.end_col_offset)
            if len(groups) == 1:
                nb = next(iter(groups))
                m = _FROM_RE.match(data[seg_start:seg_end])
                new_mod: bytes = modtext(nb).encode("utf-8")
                if m is not None and m.group(1).replace(b" ", b"") != new_mod:
                    edits.append((seg_start + m.start(1), seg_start + m.end(1), new_mod))
                continue
            line_start: int = starts[node.lineno - 1]
            indent: bytes = data[line_start:seg_start]
            stmts: "list[str]" = [f"from {modtext(nb)} import {', '.join(_alias_text(a) for a in al)}"
                                  for nb, al in groups.items()]
            edits.append((seg_start, seg_end, (b"\n" + indent).join(s.encode("utf-8") for s in stmts)))
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and id(node) not in skip:
            chain: "list[str]" = []
            cur: ast.expr = node
            while isinstance(cur, ast.Attribute):
                chain.append(cur.attr)
                cur = cur.value
            if not isinstance(cur, ast.Name) or cur.id not in bindings:
                continue
            chain.reverse()
            bound: str = bindings[cur.id]
            full = bound + "." + ".".join(chain)
            if full in moves and moves[full].startswith(bound + "."):
                new_text: str = cur.id + moves[full][len(bound):]
                edits.append((off(node.lineno, node.col_offset), off(node.end_lineno, node.end_col_offset),
                              new_text.encode("utf-8")))
        elif (string_sub is not None and isinstance(node, ast.Constant) and isinstance(node.value, str)
              and id(node) not in skip):
            a0, b0 = off(node.lineno, node.col_offset), off(node.end_lineno, node.end_col_offset)
            raw: str = data[a0:b0].decode("utf-8")
            sub: str = string_sub(raw)
            if sub != raw:
                edits.append((a0, b0, sub.encode("utf-8")))
    if not edits:
        return text
    edits.sort()
    result: bytes = b""
    pos: int = 0
    for a, b, rep in edits:
        if a < pos:
            continue  # 겹친 고침(바깥 사슬이 이미 고침) — 앞의 것을 쓴다
        result += data[pos:a] + rep
        pos = b
    result += data[pos:]
    return result.decode("utf-8")


def string_substituter(pairs: "Iterable[Tuple[str, str]]") -> "Callable[[str], str]":
    """문자열 · 설정 파일 속 옛 점 경로 · 슬래시 경로 치환 — 식별자 경계 · 가장 긴 키 한 번(`behavior_guard._sub_string`)."""
    import behavior_guard
    maps = behavior_guard.Maps()
    for old, new in pairs:
        maps.pair(old, new)
    return lambda s: behavior_guard._sub_string(s, maps)


def move_texts(files: "Mapping[str, str]", pairs: "Iterable[Tuple[str, str]]") -> "Dict[str, str]":
    """경로 → 글 트리에 이동 쌍을 적용한다(설계 8 — `apply` · `apply_to_copy` · 창 판정 · 불변식이 같은 함수를 쓴다).
    옮긴 파일과 옮긴 모듈 이름이 든 파일만 import 를 기계 치환하고, 새 묶음에 빈 `__init__.py` 를 만들고, 이번 이동으로
    비워진 묶음의 빈 `__init__.py` 를 지운다(내용이 있는 `__init__.py` 는 남긴다)."""
    pair_list: "list[Tuple[str, str]]" = list(pairs)
    moves: "dict[str, str]" = module_moves(pair_list)
    sub: "Optional[Callable[[str], str]]" = string_substituter(pair_list) if pair_list else None
    where: "dict[str, str]" = dict(pair_list)
    names: "set[str]" = {old.rsplit("/", 1)[1][:-3] for old, _ in pair_list if old.endswith(".py")}
    names |= {old.rsplit("/", 2)[1] for old, _ in pair_list if old.endswith("/__init__.py")}
    out: "dict[str, str]" = {}
    for path, text in files.items():
        new: str = where.get(path, path)
        if path.endswith(".py") and (path in where or any(n in text for n in names)):
            text = rewrite_source(text, path, new, moves, sub)
        out[new] = text
    before: "set[str]" = group_dirs_of(files)
    for d in sorted(group_dirs_of(out) - before):
        out.setdefault(f"{d}/__init__.py", "")
    for d in sorted(before):
        rest: "list[str]" = [q for q in out if q.startswith(d + "/")]
        if rest == [f"{d}/__init__.py"] and out[rest[0]] == "" and any(old.startswith(d + "/") for old in where):
            del out[rest[0]]
    return out


def placed_tree(files: "Mapping[str, str]", dirs: "Iterable[str]",
                placement: Placement) -> "Tuple[Dict[str, str], Set[str]]":
    """자리대로 옮긴 트리(메모리) — 불변식 1 · 2 의 재료."""
    out: "dict[str, str]" = move_texts(files, placement_moves(placement))
    kept: "set[str]" = {d for d in dirs if any(q.startswith(d + "/") for q in out)}
    return out, kept | group_dirs_of(out)


# ── git (읽기만) ───────────────────────────────────────────────────────────────

GIT_PINS: "tuple[str, ...]" = (
    "-c", "core.quotePath=false", "-c", "color.ui=false", "-c", "core.autocrlf=false", "-c", "diff.external=",
    "-c", "log.showSignature=false", "-c", "core.fsmonitor=false")


def _git(root: Path, *args: str, check: bool = True, data: "Optional[bytes]" = None) -> bytes:
    proc = subprocess.run(["git", "-C", str(root), *GIT_PINS, *args], capture_output=True, input=data)
    if check and proc.returncode != 0:
        raise FolderGroupError(f"git {' '.join(args)} 실패 — {proc.stderr.decode('utf-8', 'replace').strip()}")
    return proc.stdout


def git_prefix(root: Path) -> str:
    """프로젝트 루트가 git 뿌리 아래 하위 폴더면 그 접두(`proj/`) — 뿌리면 빈 글."""
    return _git(root, "rev-parse", "--show-prefix").decode("utf-8").strip()


def tree_oids(root: Path, rev: str, prefix: str) -> "Dict[str, str]":
    """커밋 트리의 blob(프로젝트 상대 경로 → oid) — 접두 밖 경로는 뺀다."""
    out: "dict[str, str]" = {}
    for rec in _git(root, "ls-tree", "--full-tree", "-r", "-z", rev).split(b"\0"):
        meta, _, raw = rec.partition(b"\t")
        fields: "list[bytes]" = meta.split()
        if len(fields) < 3 or fields[1] != b"blob":
            continue
        path: str = raw.decode("utf-8", "surrogateescape")
        if path.startswith(prefix):
            out[path[len(prefix):]] = fields[2].decode("ascii")
    return out


def blob_bytes(root: Path, oids: "Iterable[str]") -> "Dict[str, bytes]":
    want: "list[str]" = sorted(set(oids))
    if not want:
        return {}
    raw: bytes = _git(root, "cat-file", "--batch", data=("\n".join(want) + "\n").encode("ascii"))
    out: "dict[str, bytes]" = {}
    pos: int = 0
    while pos < len(raw):
        end: int = raw.index(b"\n", pos)
        head: "list[bytes]" = raw[pos:end].split()
        pos = end + 1
        if len(head) < 3 or head[1] == b"missing":
            continue
        size: int = int(head[2])
        out[head[0].decode("ascii")] = raw[pos:pos + size]
        pos += size + 1
    return out


def blob_oid(data: bytes) -> str:
    """git blob 지문(작업 트리 파일과 커밋 트리를 같은 자로 견준다)."""
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def _decode(data: bytes) -> str:
    return data.decode("utf-8", "replace")


def base_tree(root: Path, anchor: str, merges: "Iterable[object]" = ()) -> "Dict[str, str]":
    """T₀′(설계 5절) — 앵커 트리에 승인 병합 유입을 덮은 트리(프로젝트 상대 경로 → blob oid).

    앵커..HEAD 첫 부모 사슬의 승인 병합 M 마다(사슬 차례): M 이 p 를 레인 쪽에서 바꿨고(blob(M^1:p) ≠ blob(M:p)) 그 판이
    상류판 그대로(= blob(M^2:p))면 p 는 blob(M:p)(없음이면 지움). HEAD 조건은 없다 — 병합이 지운 옛 경로는 T₀′ 에 남지 않는다.
    충돌 해소분(blob(M:p) ≠ blob(M^2:p))은 앵커 판 그대로다."""
    prefix: str = git_prefix(root)  # 하위 폴더 프로젝트 접두(검토 M5)
    tree: "dict[str, str]" = tree_oids(root, anchor, prefix)
    joined = [m for m in merges if getattr(m, "position", None) is not None]
    for m in sorted(joined, key=lambda x: getattr(x, "position")):
        t1: "dict[str, str]" = tree_oids(root, getattr(m, "parent1"), prefix)
        tm: "dict[str, str]" = tree_oids(root, getattr(m, "sha"), prefix)
        t2: "dict[str, str]" = tree_oids(root, getattr(m, "parent2"), prefix)
        for p in sorted(set(t1) | set(tm)):
            after: "Optional[str]" = tm.get(p)
            if t1.get(p) != after and after == t2.get(p):
                if after is None:
                    tree.pop(p, None)
                else:
                    tree[p] = after
    return tree


def worktree_bytes(root: Path) -> "Dict[str, bytes]":
    """작업 트리 파일(추적 + 무시되지 않은 미추적 · 지금 디스크에 있는 것) — 프로젝트 상대 경로."""
    out: "dict[str, bytes]" = {}
    raw: bytes = _git(root, "ls-files", "-co", "--exclude-standard", "-z")
    for rec in raw.split(b"\0"):
        if not rec:
            continue
        rel: str = rec.decode("utf-8", "surrogateescape")
        if _excluded(rel):
            continue
        f: Path = root / rel
        if f.is_file() and not f.is_symlink():
            out[rel] = f.read_bytes()
    return out


_EXCLUDED: "tuple[str, ...]" = (".dddjango/", ".git/", ".venv/", "venv/", "node_modules/")


def _excluded(rel: str) -> bool:
    return rel.startswith(_EXCLUDED) or "/__pycache__/" in f"/{rel}"


# ── 실제 이동 · 이 실행의 이동 (설계 5 · 8) ───────────────────────────────────────

def _key(m: Member) -> "Tuple[str, str]":
    """파일의 정체 — 묶음 부모와 묶음 밖 이름(이동은 묶음 칸만 바꾼다)."""
    return m.slot.parent, m.name


def actual_moves(old: "Mapping[str, object]", new: "Mapping[str, object]") -> "Dict[str, str]":
    """두 트리(경로 → 지문) 사이의 묶음 이동 쌍 — 같은 묶음 부모 · 같은 파일 이름 · 묶음 칸만 다름(옛 경로는 앞에만 ·
    새 경로는 뒤에만). 한쪽 후보가 둘 이상이면 짝 없음(fail-closed). 내용은 보지 않는다(git 유사도 이름 바꿈을 쓰지 않음 —
    많이 고친 파일도 같은 쌍). 승격 폴더는 통째로 짝짓는다. 레인 이동 · 병합 몫 · 게이트 · verify 가 이 함수 하나를 쓴다."""
    gone: "set[str]" = {p for p in old if p not in new}
    came: "set[str]" = {p for p in new if p not in old}
    left: "dict[Tuple[str, str], list[Member]]" = {}
    right: "dict[Tuple[str, str], list[Member]]" = {}
    for m in members_of(old):
        if m.path in gone:
            left.setdefault(_key(m), []).append(m)
    for m in members_of(new):
        if m.path in came:
            right.setdefault(_key(m), []).append(m)
    pairs: "dict[str, str]" = {}
    for k in sorted(left):
        olds, news = left[k], right.get(k, [])
        if len(olds) == 1 and len(news) == 1 and olds[0].group != news[0].group:
            o, n = olds[0], news[0]
            pairs[o.path] = n.path
            if o.unit_dir is not None and n.unit_dir is not None:
                for p in sorted(gone):
                    if p.startswith(o.unit_dir + "/") and p != o.path and n.unit_dir + p[len(o.unit_dir):] in came:
                        pairs[p] = n.unit_dir + p[len(o.unit_dir):]
    return dict(sorted(pairs.items()))


_DECISION_RE: "re.Pattern[str]" = re.compile(r"^\s*[-*]?\s*(.+?)\s*·\s*결정\s*=\s*([^\s·—-]\S*)")


def _row_id(row: str) -> "Optional[str]":
    s: str = row.strip()
    if s.startswith("|"):
        return s.strip("|").split("|")[0].strip() or None
    m = re.match(r"[-*]?\s*(\S+)", s)
    return m.group(1) if m else None


def chosen_debt_lines(scope_text: str, candidates: "Iterable[Tuple[str, str]]") -> "Set[Tuple[str, str]]":
    """G0 ⓐ 로 고른 #656 줄 — `refactor-scope.md` 이번 실행 몫(`# 앞 실행` 절 앞)의 `… · 결정 = ⓐ` 줄이 그 줄 글자를
    인용하거나, 그 줄이 든 표 행 · 목록 행의 첫 칸(항목 ID)을 든 것. ⓐ′ · ⓑ 는 고르지 않는다."""
    current: "list[str]" = scope_text.split("# 앞 실행", 1)[0].splitlines()
    heads: "list[str]" = []
    ids: "set[str]" = set()
    for row in current:
        m = _DECISION_RE.match(row)
        if m is None or m.group(2) != "ⓐ":
            continue
        heads.append(m.group(1))
        ids |= {t for t in re.split(r"[,\s]+", m.group(1)) if t}
    out: "set[Tuple[str, str]]" = set()
    for where, msg in candidates:
        text: str = f"{where}: {msg}"
        if any(text in h for h in heads) or any(text in row and _row_id(row) in ids for row in current):
            out.add((where, msg))
    return out


def legacy_entries(path: "Optional[Path]") -> "List[str]":
    """이관 빚 목록의 #656 부분 문자열(`anchor_diff.load_debt` 형식)."""
    if path is None:
        return []
    import anchor_diff
    try:
        return [sub for tag, sub in anchor_diff.load_debt(path) if tag == "#656"]
    except anchor_diff.AnchorDiffUsage as exc:
        raise FolderGroupError(str(exc))


class RunPlan(NamedTuple):
    """5절 계산 — 파일 정체(묶음 부모, 이름)마다 자리."""

    anchor: "Dict[Tuple[str, str], str]"    # T₀
    base: "Dict[Tuple[str, str], str]"      # T₀′
    debt: "Dict[Tuple[str, str], str]"      # B
    current: "Dict[Tuple[str, str], str]"   # 지금(설계 때는 T₀′ + file-plan)
    final: "Dict[Tuple[str, str], str]"     # R
    formed: "Set[Tuple[str, str]]"          # 이 실행의 형성(부모, 묶음)
    dissolved: "Set[Tuple[str, str]]"       # 이 실행의 해체
    lines_now: "List[Tuple[str, str]]"      # place(지금 내용, B 묶음) 의 #656 줄
    debt_lines: "Set[Tuple[str, str]]"      # ⓐ 로 고른 줄

    def pairs(self, start: "Dict[Tuple[str, str], str]", end: "Dict[Tuple[str, str], str]") -> "List[Tuple[str, str]]":
        return sorted((start[k], end[k]) for k in start if k in end and start[k] != end[k])


def _keyed(placement: Placement) -> "Dict[Tuple[str, str], FilePlace]":
    return {_key(fp.member): fp for fp in placement.files.values()}


def _groups(placement: Placement) -> "Set[Tuple[str, str]]":
    return {(parent, g) for parent, gs in placement.final.items() for g in gs}


def compute_plan(t0: "Mapping[str, str]", t0p: "Mapping[str, str]", now: "Mapping[str, str]",
                 chosen: "Callable[[List[Tuple[str, str]]], Set[Tuple[str, str]]]",
                 legacy: "Iterable[str]" = ()) -> RunPlan:
    """이 실행의 이동(설계 5절) — t0 · t0p · now 는 domain_layer `.py` 의 경로 → 글."""
    p0p: Placement = place(t0p, group_dirs_of(t0p))
    lines0p: "list[Tuple[str, str]]" = lines(p0p)
    picked: "set[Tuple[str, str]]" = chosen(lines0p)
    made: "set[Tuple[str, str]]" = {(w.rsplit("/", 1)[0], m) for w, m in picked if m.startswith("묶음 ") and "만든다" in m}
    undone: "set[str]" = {w for w, m in picked if "푼다" in m}
    debt_pairs: "list[Tuple[str, str]]" = []
    for path, fp in p0p.files.items():
        if fp.target == path:
            continue
        parent: str = fp.member.slot.parent
        own: bool = any(w == path for w, _ in picked)
        make: bool = fp.group is not None and (parent, MAKE.format(fp.group)) in made
        undo: bool = fp.member.group is not None and any(
            w in (f"{parent}/{fp.member.group}/__init__.py", path) or w.startswith(f"{parent}/{fp.member.group}/")
            for w in undone)
        if own or make or undo:
            debt_pairs.append((path, fp.target))
    b_paths: "dict[str, str]" = move_texts({p: "" for p in t0p}, _expand(debt_pairs, t0p))
    b_dirs: "set[str]" = group_dirs_of(b_paths)
    p1: Placement = place(now, b_dirs)
    g0p, g1 = _groups(p0p), _groups(p1)
    bset: "set[Tuple[str, str]]" = {(d.rsplit("/", 1)[0], d.rsplit("/", 1)[1]) for d in b_dirs}
    s_groups: "set[Tuple[str, str]]" = (bset | (g1 - g0p)) - ((bset & g0p) - g1)
    base_m: "dict[Tuple[str, str], Member]" = {_key(m): m for m in members_of(t0p)}
    debt_m: "dict[Tuple[str, str], Member]" = {_key(m): m for m in members_of(b_paths)}
    p0p_k, p1_k = _keyed(p0p), _keyed(p1)
    lines_now: "list[Tuple[str, str]]" = lines(p1)
    legacy_list: "list[str]" = list(legacy)
    final: "dict[Tuple[str, str], str]" = {}
    for k, fp in p1_k.items():
        m: Member = fp.member
        own_lines = [f"{w}: {msg}" for w, msg in lines_now
                     if w == m.path or (fp.group is not None and w == f"{m.slot.parent}/__init__.py"
                                        and msg == MAKE.format(fp.group))]
        if k in debt_m and any(sub in ln for sub in legacy_list for ln in own_lines):
            final[k] = debt_m[k].path                                  # ⓪ 이관 빚
            continue
        b_group: "Optional[str]" = debt_m[k].group if k in debt_m else None
        moved_by_run: bool = (k not in base_m or k not in p0p_k or fp.group != p0p_k[k].group
                              or (b_group is not None and (m.slot.parent, b_group) not in s_groups))
        if moved_by_run:                                               # ①
            final[k] = m.at(fp.group) if fp.group is not None and (m.slot.parent, fp.group) in s_groups else m.flat
        else:
            final[k] = debt_m[k].path  # ② B 자리 그대로
    return RunPlan(
        anchor={_key(m): m.path for m in members_of(t0)}, base={k: m.path for k, m in base_m.items()},
        debt={k: m.path for k, m in debt_m.items()}, current={k: fp.member.path for k, fp in p1_k.items()},
        final=final, formed=(g1 - g0p) & s_groups, dissolved=(bset & g0p) - g1,
        lines_now=lines_now, debt_lines=picked)


def _expand(pairs: "Iterable[Tuple[str, str]]", paths: "Iterable[str]") -> "List[Tuple[str, str]]":
    """승격 본체 쌍(`…/D/D.py`)을 그 폴더의 모든 파일 쌍으로 넓힌다."""
    pathset: "list[str]" = sorted(paths)
    out: "dict[str, str]" = {}
    for old, new in pairs:
        out[old] = new
        o_dir, o_name = old.rsplit("/", 1)
        if o_name == o_dir.rsplit("/", 1)[-1] + ".py":
            hit = slot_of(old)
            if hit is not None and hit[0].service and len(hit[1]) >= 2 and hit[1][-2] + ".py" == hit[1][-1]:
                n_dir: str = new.rsplit("/", 1)[0]
                for p in pathset:
                    if p.startswith(o_dir + "/"):
                        out[p] = n_dir + p[len(o_dir):]
    return sorted(out.items())


# ── 명령 재료 ─────────────────────────────────────────────────────────────────

CONFIG_FILES: "tuple[str, ...]" = ("pyproject.toml", "setup.cfg", "mypy.ini", ".importlinter", ".coveragerc",
                                   "pytest.ini", "tox.ini")
MIGRATION_RE: "re.Pattern[str]" = re.compile(r"(?:^|/)migrations/\d{4}_[^/]+\.py$")


def _is_layer_py(path: str) -> bool:
    return path.endswith(".py") and f"/{LAYER}/" in f"/{path}" and not _excluded(path)


class RunInput(NamedTuple):
    t0: "Dict[str, str]"
    t0p: "Dict[str, str]"
    now: "Dict[str, str]"
    t0_oids: "Dict[str, str]"
    t0p_oids: "Dict[str, str]"
    scope: str


def _bc_filter(files: "Mapping[str, str]", bcs: "Optional[Set[str]]") -> "Dict[str, str]":
    return {p: t for p, t in files.items() if _is_layer_py(p) and (bcs is None or _bc_of(p) in bcs)}


def _read_folder(folder: "Optional[Path]", name: str) -> str:
    if folder is None or not (folder / name).is_file():
        return ""
    return (folder / name).read_text(encoding="utf-8")


def load_run(root: Path, folder: "Optional[Path]", bcs: "Optional[Set[str]]",
             now_files: "Optional[Mapping[str, str]]" = None) -> RunInput:
    """5절 재료 — 산출물 폴더에 `build_anchor` 가 있으면 git 앵커 · 승인 병합으로 T₀ · T₀′, 없으면 작업 트리가 곧 T₀ = T₀′."""
    anchor: str = _read_folder(folder, "build_anchor").strip()
    if not anchor:
        files, _dirs = scan_tree(root)
        cur = _bc_filter(files, bcs)
        oids = {p: blob_oid(t.encode("utf-8")) for p, t in cur.items()}
        return RunInput(cur, cur, _bc_filter(now_files, bcs) if now_files is not None else cur, oids, oids,
                        _read_folder(folder, "refactor-scope.md"))
    import anchor_diff
    head: str = _git(root, "rev-parse", "--verify", "HEAD^{commit}").decode("ascii").strip()
    anchor_sha: str = _git(root, "rev-parse", "--verify", f"{anchor}^{{commit}}").decode("ascii").strip()
    merges: "list[object]" = []
    approved: Path = folder / "approved-merges.txt"  # type: ignore[operator]
    if approved.is_file():
        try:
            merges = list(anchor_diff.load_approved_merges(approved, root, anchor_sha, head)[0])
        except anchor_diff.AnchorDiffUsage as exc:
            raise FolderGroupError(str(exc))
    t0_all: "dict[str, str]" = tree_oids(root, anchor_sha, git_prefix(root))
    t0p_all: "dict[str, str]" = base_tree(root, anchor_sha, merges)
    t0_oids = {p: o for p, o in t0_all.items() if _is_layer_py(p) and (bcs is None or _bc_of(p) in bcs)}
    t0p_oids = {p: o for p, o in t0p_all.items() if _is_layer_py(p) and (bcs is None or _bc_of(p) in bcs)}
    blobs: "dict[str, bytes]" = blob_bytes(root, list(t0_oids.values()) + list(t0p_oids.values()))
    t0 = {p: _decode(blobs.get(o, b"")) for p, o in t0_oids.items()}
    t0p = {p: _decode(blobs.get(o, b"")) for p, o in t0p_oids.items()}
    if now_files is None:
        now_files = {p: _decode(b) for p, b in worktree_bytes(root).items() if _is_layer_py(p)}
    return RunInput(t0, t0p, _bc_filter(now_files, bcs), t0_oids, t0p_oids, _read_folder(folder, "refactor-scope.md"))


def plan_for(run: RunInput, legacy: "Iterable[str]" = ()) -> RunPlan:
    return compute_plan(run.t0, run.t0p, run.now, lambda cands: chosen_debt_lines(run.scope, cands), legacy)


def expected_moves(root: Path, folder: Path, legacy_debt_file: "Optional[Path]" = None,
                   bcs: "Optional[Iterable[str]]" = None) -> "Dict[str, str]":
    """앵커 자리 → R(설계 5절 · 9.4 — 게이트가 다시 낸다). 앵커에 없던 파일은 싣지 않는다."""
    plan: RunPlan = plan_for(load_run(root, folder, set(bcs) if bcs is not None else None),
                             legacy_entries(legacy_debt_file))
    return dict(plan.pairs(plan.anchor, plan.final))


# ── 이동 하기(디스크) ─────────────────────────────────────────────────────────

def _project_texts(root: Path) -> "Dict[str, str]":
    """프로젝트의 `.py` 와 루트 설정 파일 — 경로 → 글(읽기 불능 · 링크는 뺀다)."""
    out: "dict[str, str]" = {}
    for dirpath, dirnames, filenames in os.walk(root):
        rel_dir: str = os.path.relpath(dirpath, root)
        dirnames[:] = sorted(d for d in dirnames if d not in _SKIP_DIRS and not d.startswith("."))
        for name in sorted(filenames):
            rel: str = name if rel_dir == "." else f"{Path(rel_dir).as_posix()}/{name}"
            if not (name.endswith(".py") or (rel_dir == "." and name in CONFIG_FILES)):
                continue
            f: Path = root / rel
            if f.is_symlink():
                continue
            try:
                out[rel] = f.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
    return out


def rewrite_tree(texts: "Mapping[str, str]", pairs: "List[Tuple[str, str]]") -> "Dict[str, str]":
    """이동 뒤 트리 — `.py` 는 `move_texts`, 루트 설정 파일은 같은 자의 경로 치환."""
    py: "dict[str, str]" = {p: t for p, t in texts.items() if p.endswith(".py")}
    out: "dict[str, str]" = move_texts(py, pairs)
    sub = string_substituter(pairs) if pairs else None
    for p, t in texts.items():
        if not p.endswith(".py"):
            out[p] = sub(t) if sub is not None and p in CONFIG_FILES else t
    return out


class Hazards(NamedTuple):
    blocked: "List[str]"     # 기계 이동 불가 `file:line 무엇`
    bindings: "List[str]"    # 경로 결속 `file:line 꼴`
    other_bc: "List[str]"    # 다른 BC import `file:line 모듈`


def _consts(node: ast.AST) -> "List[str]":
    return [n.value for n in ast.walk(node) if isinstance(n, ast.Constant) and isinstance(n.value, str)]


def _call_name(node: ast.Call) -> str:
    f = node.func
    return f.id if isinstance(f, ast.Name) else (f.attr if isinstance(f, ast.Attribute) else "")


def hazards(texts: "Mapping[str, str]", pairs: "List[Tuple[str, str]]", bc_names: "Iterable[str]") -> Hazards:
    """옮길 모듈을 계산된 이름으로 부르는 곳(기계 이동 불가) · 경로에 묶인 값(경로 결속) · 다른 BC 의 import."""
    moves: "dict[str, str]" = module_moves(pairs)
    moved_mods: "set[str]" = set(moves)
    packages: "set[str]" = {m.rpartition(".")[0] for m in moved_mods} | moved_mods
    moved_paths: "set[str]" = {o for o, _ in pairs}
    bcs: "set[str]" = set(bc_names)
    blocked: "list[str]" = []
    bindings: "list[str]" = []
    other: "list[str]" = []

    def hits_package(consts: "List[str]") -> bool:
        for c in consts:
            c2: str = c.strip().rstrip("./").replace("/", ".")
            if c2 and any(pk == c2 or pk.startswith(c2 + ".") or c2.startswith(pk + ".") for pk in packages):
                return True
        return False

    for path in sorted(texts):
        if not path.endswith(".py"):
            continue
        text: str = texts[path]
        if not any(pk.rsplit(".", 1)[-1] in text for pk in packages) and path not in moved_paths:
            continue
        tree: "Optional[ast.Module]" = _parse(text)
        if tree is None:
            continue
        src = Source(path, text)
        imports_moved: bool = any((mod in moved_mods) or (name is not None and f"{mod}.{name}" in moved_mods)
                                  or any(mod.endswith("." + mm) or mod == mm for mm in moved_mods)
                                  for mod, name in src.targets)
        bound_pk: "set[str]" = {nm for nm, (mod, attr) in src.bindings.items()
                                if (f"{mod}.{attr}" if attr else mod) in packages}
        consts_by_name: "dict[str, List[str]]" = {}
        for node in tree.body:
            if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                consts_by_name[node.targets[0].id] = _consts(node.value)
        migration: bool = MIGRATION_RE.search(path) is not None
        for node in ast.walk(tree):
            line: int = getattr(node, "lineno", 0)
            if isinstance(node, ast.Call):
                name: str = _call_name(node)
                arg = node.args[0] if node.args else None
                if name in ("import_module", "__import__") and arg is not None and not (
                        isinstance(arg, ast.Constant) and isinstance(arg.value, str)):
                    pieces: "list[str]" = _consts(arg) + [c for n in ast.walk(arg) if isinstance(n, ast.Name)
                                                          for c in consts_by_name.get(n.id, [])]
                    if hits_package(pieces):
                        blocked.append(f"{path}:{line} 계산된 import")
                elif name == "getattr" and len(node.args) >= 2 and isinstance(node.args[0], ast.Name) \
                        and node.args[0].id in bound_pk and not isinstance(node.args[1], ast.Constant):
                    blocked.append(f"{path}:{line} 계산된 getattr({node.args[0].id}, …)")
                elif imports_moved or path in moved_paths:
                    if name in ("getsource", "getsourcefile", "getfile"):
                        bindings.append(f"{path}:{line} 소스 지문")
                    elif name in ("glob", "rglob", "iterdir", "iter_modules", "walk_packages"):
                        bindings.append(f"{path}:{line} 패키지 훑기")
                    elif name in ("dump", "dumps", "load", "loads") and isinstance(node.func, ast.Attribute) \
                            and isinstance(node.func.value, ast.Name) and node.func.value.id == "pickle":
                        bindings.append(f"{path}:{line} pickle")
            elif migration and isinstance(node, (ast.JoinedStr, ast.BinOp)) and hits_package(_consts(node)):
                blocked.append(f"{path}:{line} 마이그레이션 계산된 점 경로")
            elif (imports_moved or path in moved_paths) and isinstance(node, ast.Name) and node.id == "__file__":
                bindings.append(f"{path}:{line} 경로 지문(__file__)")
            elif (imports_moved or path in moved_paths) and isinstance(node, ast.Attribute) \
                    and node.attr in ("__module__", "__qualname__"):
                bindings.append(f"{path}:{line} 모듈 이름 값({node.attr})")
            elif path in moved_paths and isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for dec in node.decorator_list:
                    call = dec if isinstance(dec, ast.Call) else None
                    target = dec.func if call is not None else dec
                    dname: str = target.id if isinstance(target, ast.Name) else (
                        target.attr if isinstance(target, ast.Attribute) else "")
                    if dname in ("shared_task", "task") and not (
                            call is not None and any(k.arg == "name" for k in call.keywords)):
                        bindings.append(f"{path}:{line} Celery 기본 작업 이름")
        owner: "Optional[str]" = _bc_of(path) if f"/{LAYER}/" in f"/{path}" else _bc_under(path, bcs)
        for node in ast.walk(tree):
            if not isinstance(node, (ast.Import, ast.ImportFrom)):
                continue
            mods: "list[str]" = []
            if isinstance(node, ast.Import):
                mods = [a.name for a in node.names]
            else:
                base: str = _resolve_from(src.package, node.level, node.module)
                mods = [base] + [f"{base}.{a.name}" for a in node.names]
            for mod in mods:
                if mod in moved_mods and owner is not None and owner != _bc_of(module_path(mod)):
                    other.append(f"{path}:{node.lineno} {mod}")
    return Hazards(sorted(set(blocked)), sorted(set(bindings)), sorted(set(other)))


def module_path(mod: str) -> str:
    return mod.replace(".", "/") + ".py"


def _bc_under(path: str, bcs: "Set[str]") -> "Optional[str]":
    parts: "list[str]" = path.split("/")
    if len(parts) > 2 and parts[0] == "application" and parts[1] in bcs:
        return parts[1]
    return None


def perform(root: Path, pairs: "List[Tuple[str, str]]", use_git: bool) -> "List[str]":
    """디스크에서 옮긴다 — 파일 이동(`git mv` · 미추적은 이름 바꿈) · import · 설정 파일 치환 · 새 묶음 빈 `__init__.py` ·
    비워진 묶음 지움. 돌려주는 값은 고친 파일(새 경로)."""
    texts: "dict[str, str]" = _project_texts(root)
    after: "dict[str, str]" = rewrite_tree(texts, pairs)
    tracked: "set[str]" = set()
    if use_git:
        tracked = {r.decode("utf-8", "surrogateescape") for r in _git(root, "ls-files", "-z").split(b"\0") if r}
    for old, new in pairs:
        (root / new).parent.mkdir(parents=True, exist_ok=True)
        if use_git and old in tracked:
            _git(root, "mv", "--", old, new)
        else:
            os.replace(root / old, root / new)
    changed: "list[str]" = []
    moved_to: "dict[str, str]" = dict(pairs)
    for old_path, text in texts.items():
        new_path: str = moved_to.get(old_path, old_path)
        if new_path not in after:
            (root / new_path).unlink()
            changed.append(new_path)
            continue
        if after[new_path] != text:
            (root / new_path).write_text(after[new_path], encoding="utf-8")
            changed.append(new_path)
    for p in sorted(set(after) - {moved_to.get(o, o) for o in texts}):
        (root / p).parent.mkdir(parents=True, exist_ok=True)
        (root / p).write_text(after[p], encoding="utf-8")
        changed.append(p)
    for old, _new in pairs:
        d: Path = (root / old).parent
        while d != root and d.is_dir():
            cache: Path = d / "__pycache__"
            if cache.is_dir() and not [c for c in d.iterdir() if c.name != "__pycache__"]:
                shutil.rmtree(cache)
            if any(d.iterdir()):
                break
            d.rmdir()
            d = d.parent
    return sorted(set(changed))


def apply_to_copy(root: Path, pairs: "Iterable[Tuple[str, str]]") -> "List[Tuple[str, str]]":
    """격리 사본(git 아님)에서 이동 쌍을 그대로 한다 — pre-gate 가 앵커 커밋 전에 부른다(설계 9.3). 넓힌 쌍을 돌려준다."""
    full: "list[Tuple[str, str]]" = _expand(pairs, _all_files(root))
    perform(root, full, use_git=False)
    return full


def _all_files(root: Path) -> "List[str]":
    out: "list[str]" = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in _SKIP_DIRS and not d.startswith("."))
        rel_dir: str = os.path.relpath(dirpath, root)
        for name in sorted(filenames):
            out.append(name if rel_dir == "." else f"{Path(rel_dir).as_posix()}/{name}")
    return out


# ── 명령 ──────────────────────────────────────────────────────────────────────

def _fmt_line(where: str, msg: str) -> str:
    return f"[#656] {where}: {msg}"


def _parse_spec(spec: Path) -> "Tuple[List[str], List[str]]":
    """명세 machine file-plan(`<태그> <경로>`) 의 add · remove 경로."""
    text: str = spec.read_text(encoding="utf-8")
    rows: "list[str]" = []
    lines_: "list[str]" = text.split("\n")
    for i, ln in enumerate(lines_):
        if "<!-- machine: file-plan -->" not in ln:
            continue
        j: int = i + 1
        while j < len(lines_) and not lines_[j].strip():
            j += 1
        if j < len(lines_) and lines_[j].strip().startswith("```"):
            for k in range(j + 1, len(lines_)):
                if lines_[k].strip().startswith("```"):
                    break
                rows.append(lines_[k].split("#", 1)[0].strip())
        break
    adds: "list[str]" = []
    removes: "list[str]" = []
    for row in rows:
        parts: "list[str]" = row.split()
        if len(parts) >= 2 and parts[0] == "add":
            adds.append(parts[1])
        elif len(parts) >= 2 and parts[0].startswith("remove"):
            removes.append(parts[1])
    return adds, removes


def _import_estimate(texts: "Mapping[str, str]", pairs: "List[Tuple[str, str]]") -> int:
    moved: "set[str]" = set(module_moves(pairs))
    n: int = 0
    for path, text in texts.items():
        if not path.endswith(".py") or not any(m.rsplit(".", 1)[-1] in text for m in moved):
            continue
        src = Source(path, text)
        if src.tree is None:
            continue
        for node in ast.walk(src.tree):
            if isinstance(node, ast.Import) and any(a.name in moved for a in node.names):
                n += 1
            elif isinstance(node, ast.ImportFrom):
                base: str = _resolve_from(src.package, node.level, node.module)
                if base in moved or any(f"{base}.{a.name}" in moved for a in node.names):
                    n += 1
    return n


def _run_paths(folder: "Optional[Path]") -> "Optional[Path]":
    return folder.resolve() if folder is not None else None


def cmd_draft(args: argparse.Namespace) -> int:
    root: Path = Path(args.root).resolve()
    folder: "Optional[Path]" = _run_paths(Path(args.run) if args.run else None)
    bcs: "set[str]" = set(args.bc)
    now_override: "Optional[dict[str, str]]" = None
    adds: "list[str]" = []
    if args.spec:
        files, _dirs = scan_tree(root)
        adds, removes = _parse_spec(Path(args.spec))
        now_override = {p: t for p, t in files.items() if p not in set(removes)}
        for a in adds:
            if _is_layer_py(a):
                now_override.setdefault(a, "")
    run: RunInput = load_run(root, folder, bcs, now_override)
    plan: RunPlan = plan_for(run, legacy_entries(Path(args.legacy_debt_file) if args.legacy_debt_file else None))
    texts: "dict[str, str]" = _project_texts(root)
    remaining: "list[Tuple[str, str]]" = plan.pairs(plan.current, plan.final)
    hz: Hazards = hazards(texts, _expand(remaining, texts), [d.name for d in business_vocab.server_bc_dirs(root)])
    out: "list[str]" = [f"줄 {_fmt_line(w, m)}" for w, m in plan.lines_now]
    out += [f"빚 이동 {a} -> {b}" for a, b in plan.pairs(plan.base, plan.debt)]
    this_run: "list[Tuple[str, str]]" = plan.pairs(plan.debt, plan.final)
    out += [f"이 실행 이동 {a} -> {b}" for a, b in this_run]
    expected: "list[Tuple[str, str]]" = plan.pairs(plan.anchor, plan.final)
    out += [f"예상 이동 {a} -> {b}" for a, b in expected]
    out += [f"남은 이동 {a} -> {b}" for a, b in remaining]
    new_keys: "list[Tuple[str, str]]" = sorted(k for k in plan.current if k not in plan.base)
    out += [f"새 파일 {plan.current[k]} -> {plan.final[k]}" for k in new_keys]
    out += [f"기계 이동 불가 {x}" for x in hz.blocked]
    out += [f"경로 결속 {x}" for x in hz.bindings]
    out += [f"다른 BC import {x}" for x in hz.other_bc]
    if folder is not None and _read_folder(folder, "build_anchor").strip():
        sub = string_substituter(remaining) if remaining else None
        dirty: "set[str]" = _dirty_paths(root)
        for name in CONFIG_FILES:
            if name in dirty and name in texts and sub is not None and sub(texts[name]) != texts[name]:
                out.append(f"미커밋 설정 {name}")
    g1: str = _read_folder(folder, "group-moves.txt")
    if g1:
        then: "set[str]" = {ln.strip() for ln in g1.splitlines() if ln.startswith("예상 이동 ")}
        now_set: "set[str]" = {f"예상 이동 {a} -> {b}" for a, b in expected}
        out += [f"G1 목록 차이 + {ln}" for ln in sorted(now_set - then)]
        out += [f"G1 목록 차이 - {ln}" for ln in sorted(then - now_set)]
    moved_keys: "set[Tuple[str, str]]" = {k for k in plan.debt if k in plan.final and plan.debt[k] != plan.final[k]}
    formed_files: int = sum(1 for k in moved_keys if (k[0], _group_of(plan.final[k])) in plan.formed)
    dissolved_files: int = sum(1 for k in moved_keys if (k[0], _group_of(plan.debt[k])) in plan.dissolved)
    out.append(f"알림 묶음: 새 파일 {len(new_keys)} · 이 실행의 이동 {len(moved_keys)}(형성 {len(plan.formed)} · "
               f"해체 {len(plan.dissolved)} · 다시 놓기 {len(moved_keys) - formed_files - dissolved_files}) · "
               f"경로 결속 {len(hz.bindings)} · 다른 BC import {len(hz.other_bc)}")
    if args.summary:
        for bc in sorted(bcs):
            files, dirs = scan_tree(root, [bc])
            pl: Placement = place(files, dirs)
            moves: "list[Tuple[str, str]]" = placement_moves(pl)
            folders: int = sum(1 for _w, m in lines(pl) if "만든다" in m or "푼다" in m)
            out.append(f"요약 {bc}: 묶음 빚: 폴더 {folders} · 파일 {len([p for p in moves if p[0].endswith('.py')])}"
                       f" · import 줄 어림 {_import_estimate(texts, moves)}")
    for ln in out:
        print(ln)
    return 0


def _group_of(path: str) -> "Optional[str]":
    m = members_of([path])
    return m[0].group if m else None


def _dirty_paths(root: Path) -> "Set[str]":
    prefix: str = git_prefix(root)
    out: "set[str]" = set()
    toks: "list[str]" = _git(root, "status", "--porcelain=v1", "-z", "--untracked-files=all").decode(
        "utf-8", "surrogateescape").split("\0")
    i: int = 0
    while i < len(toks):
        tok: str = toks[i]
        if len(tok) > 3:
            path: str = tok[3:]
            if path.startswith(prefix):
                out.add(path[len(prefix):])
            if tok[0] in "RC":
                i += 1
        i += 1
    return out


def cmd_apply(args: argparse.Namespace) -> int:
    root: Path = Path(args.root).resolve()
    folder: Path = Path(args.run).resolve()
    if not _read_folder(folder, "build_anchor").strip():
        raise FolderGroupError(f"{folder}/build_anchor 없음 — apply 는 Phase 2 묶음 창 안에서만 돈다")
    run: RunInput = load_run(root, folder, None)
    plan: RunPlan = plan_for(run, legacy_entries(Path(args.legacy_debt_file) if args.legacy_debt_file else None))
    if args.debt:
        pairs = [(plan.current[k], plan.debt[k]) for k in sorted(plan.debt)
                 if k in plan.base and plan.debt[k] != plan.base[k] and plan.current.get(k) == plan.base[k]]
    else:
        pairs = plan.pairs(plan.current, plan.final)
    full: "list[Tuple[str, str]]" = _expand(pairs, _all_files(root))
    texts: "dict[str, str]" = _project_texts(root)
    hz: Hazards = hazards(texts, full, [d.name for d in business_vocab.server_bc_dirs(root)])
    if hz.blocked:
        for x in hz.blocked:
            print(f"기계 이동 불가 {x}")
        print(f"요약: apply 멈춤 — 기계 이동 불가 {len(hz.blocked)}건(옮기지 않았다)")
        return 1
    changed: "list[str]" = perform(root, full, use_git=True)
    for a, b in full:
        print(f"이동 {a} -> {b}")
    for c in changed:
        print(f"고침 {c}")
    for x in hz.other_bc:
        print(f"다른 BC import {x}")
    print(f"요약: apply {'빚' if args.debt else '이 실행'} 이동 {len(full)} · 고친 파일 {len(changed)}")
    return 0


def _window_paths(folder: Path) -> "Tuple[object, Path]":
    import behavior_guard
    return behavior_guard, behavior_guard._run_dir(folder)


def _then_tree(root: Path, record: "Mapping[str, object]") -> "Tuple[Dict[str, str], Dict[str, str], Set[str]]":
    """창 기준 트리 — (경로 → 지문, 경로 → 글(필요한 것), 원문 없이 sha 만 남은 경로)."""
    prefix: str = git_prefix(root)
    oids: "dict[str, str]" = tree_oids(root, str(record["head"]), prefix)
    texts: "dict[str, str]" = {}
    sha_only: "set[str]" = set()
    dirty: "Mapping[str, Mapping[str, object]]" = record.get("dirty", {})  # type: ignore[assignment]
    for repo_path, entry in dirty.items():
        if not repo_path.startswith(prefix):
            continue
        p: str = repo_path[len(prefix):]
        if entry.get("sha") is None:
            oids.pop(p, None)
        elif "b64" in entry:
            data: bytes = base64.b64decode(str(entry["b64"]))
            oids[p] = blob_oid(data)
            texts[p] = _decode(data)
        else:
            oids[p] = f"sha256:{entry['sha']}"
            sha_only.add(p)
    return oids, texts, sha_only


def cmd_verify_window(root: Path, folder: Path, n: int) -> int:
    bg, run_dir = _window_paths(folder)
    found = [w for w in bg._windows(run_dir) if w[0] == n]  # type: ignore[attr-defined]
    if not found:
        raise FolderGroupError(f"창 w{n} 기록 없음 — {run_dir}")
    _n, opened, closes = found[0]
    if not closes:
        raise FolderGroupError(f"창 w{n} 이 닫히지 않았다 — behavior_guard close 뒤에 판정한다")
    prefix: str = git_prefix(root)
    merged: "set[str]" = {p[len(prefix):] for p in closes[-1].get("merged_excluded", []) if p.startswith(prefix)}
    then_oids, then_texts, sha_only = _then_tree(root, opened)
    now_bytes: "dict[str, bytes]" = worktree_bytes(root)
    now_oids: "dict[str, str]" = {p: blob_oid(b) for p, b in now_bytes.items()}
    for p in sha_only:
        if p in now_bytes and bg._sha(now_bytes[p]) == then_oids[p][len("sha256:"):]:  # type: ignore[attr-defined]
            now_oids[p] = then_oids[p]
    changed: "set[str]" = {p for p in set(then_oids) | set(now_oids)
                           if then_oids.get(p) != now_oids.get(p) and p not in merged and not _excluded(p)}
    pairs: "dict[str, str]" = actual_moves({p: o for p, o in then_oids.items() if p in changed or p not in now_oids},
                                           {p: o for p, o in now_oids.items() if p in changed or p not in then_oids})
    need: "set[str]" = {p for p in changed if p in then_oids and p not in then_texts and p not in sha_only}
    blobs: "dict[str, bytes]" = blob_bytes(root, [then_oids[p] for p in need])
    for p in need:
        then_texts[p] = _decode(blobs.get(then_oids[p], b""))
    pair_list: "list[Tuple[str, str]]" = sorted(pairs.items())
    moves: "dict[str, str]" = module_moves(pair_list)
    sub = string_substituter(pair_list) if pair_list else None
    now_dirs: "set[str]" = group_dirs_of(now_oids)
    reds: "list[str]" = []
    done: "set[str]" = set()
    for old, new in pair_list:
        done |= {old, new}
        if new.endswith(".py"):
            want: str = rewrite_source(then_texts.get(old, ""), old, new, moves, sub)
            if _decode(now_bytes[new]) != want:
                reds.append(f"이동한 파일 내용이 import 치환만이 아니다 `{old}` -> `{new}`")
        elif then_oids.get(old) != now_oids.get(new):
            reds.append(f"이동한 파일 내용이 바뀌었다 `{old}` -> `{new}`")
    for p in sorted(changed - done):
        if p in sha_only:
            reds.append(f"판정 불가 `{p}` — 창 열 때 미커밋이고 원문이 sha 로만 남았다(그 파일을 먼저 커밋하고 창을 다시 연다)")
            continue
        before: "Optional[str]" = then_texts.get(p) if p in then_oids else None
        after: "Optional[str]" = _decode(now_bytes[p]) if p in now_bytes else None
        d: str = p.rsplit("/", 1)[0] if "/" in p else ""
        if p.endswith("/__init__.py") and before is None and after == "" and d in now_dirs:
            continue
        if p.endswith("/__init__.py") and after is None and before == "" and d not in now_dirs:
            continue
        if before is not None and after is not None:
            if p.endswith(".py") and rewrite_source(before, p, p, moves, sub) == after:
                continue
            if p in CONFIG_FILES and sub is not None and sub(before) == after:
                continue
        reds.append(f"창 안 다른 변화 `{p}` — 묶음 창은 이동 · import 치환 · 빈 묶음 `__init__` · 설정 파일 경로 치환만 받는다")
    verdict: str = "red" if reds else "green"
    log: Path = folder / "group-windows.json"
    history: "list[dict]" = json.loads(log.read_text(encoding="utf-8")) if log.is_file() else []
    history.append({"window": n, "verdict": verdict, "pairs": dict(pair_list), "reds": reds,
                    "time": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")})
    log.write_text(json.dumps(history, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    for a, b in pair_list:
        print(f"쌍 {a} -> {b}")
    for r in reds:
        print(f"red: {r}")
    print(f"요약: 묶음 창 w{n} {verdict} · 쌍 {len(pair_list)} · red {len(reds)}")
    return 2 if reds else 0


def _windows_green(folder: Path) -> "Tuple[List[Dict[str, str]], List[int]]":
    log: Path = folder / "group-windows.json"
    history: "list[dict]" = json.loads(log.read_text(encoding="utf-8")) if log.is_file() else []
    last: "dict[int, dict]" = {}
    for rec in history:
        last[int(rec["window"])] = rec
    green: "list[Dict[str, str]]" = [last[n]["pairs"] for n in sorted(last) if last[n]["verdict"] == "green"]
    red: "list[int]" = [n for n in sorted(last) if last[n]["verdict"] != "green"]
    return green, red


def cmd_verify_run(root: Path, folder: Path, legacy: "Optional[Path]") -> int:
    if not _read_folder(folder, "build_anchor").strip():
        raise FolderGroupError(f"{folder}/build_anchor 없음")
    run: RunInput = load_run(root, folder, None)
    plan: RunPlan = plan_for(run, legacy_entries(legacy))
    reds: "list[str]" = []
    for k in sorted(plan.current):
        if plan.current[k] != plan.final[k]:
            reds.append(f"자리 다름 `{plan.current[k]}` — 끝 자리 `{plan.final[k]}`(끝 맞춤 묶음 창을 다시 돈다)")
    now_oids: "dict[str, str]" = {p: blob_oid(b) for p, b in worktree_bytes(root).items() if _is_layer_py(p)}
    lane: "dict[str, str]" = actual_moves(run.t0p_oids, now_oids)
    merge_share: "dict[str, str]" = actual_moves(run.t0_oids, run.t0p_oids)
    green, red_windows = _windows_green(folder)
    for a, c in sorted(lane.items()):
        pos: str = a
        for pairs in green:
            pos = pairs.get(pos, pos)
        if pos != c:
            reds.append(f"창 밖 이동 `{a}` -> `{c}` — green 묶음 창의 쌍으로 이어지지 않는다(되돌리고 끝 맞춤 다시)")
    for n in red_windows:
        reds.append(f"red 묶음 창 w{n} — 그 창을 철회하고 다시 연다")
    for a, b in sorted(lane.items()):
        print(f"이동 {a} -> {b}")
    for a, b in sorted(merge_share.items()):
        print(f"병합 몫 {a} -> {b}")
    for r in reds:
        print(f"red: {r}")
    print(f"요약: 묶음 verify {'red' if reds else 'green'} · 이동 {len(lane)} · 병합 몫 {len(merge_share)} · red {len(reds)}")
    return 2 if reds else 0


def main(argv: "Optional[List[str]]" = None) -> int:
    ap = argparse.ArgumentParser(prog="folder_group.py", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd")
    d = sub.add_parser("draft")
    d.add_argument("root")
    d.add_argument("--bc", nargs="+", required=True)
    d.add_argument("--spec")
    d.add_argument("--run")
    d.add_argument("--legacy-debt-file")
    d.add_argument("--summary", action="store_true")
    a = sub.add_parser("apply")
    a.add_argument("root")
    a.add_argument("--run", required=True)
    a.add_argument("--legacy-debt-file")
    g = a.add_mutually_exclusive_group(required=True)
    g.add_argument("--debt", action="store_true")
    g.add_argument("--run-moves", action="store_true")
    v = sub.add_parser("verify")
    v.add_argument("root")
    v.add_argument("--run", required=True)
    v.add_argument("--window", type=int)
    v.add_argument("--legacy-debt-file")
    try:
        args = ap.parse_args(argv)
    except SystemExit as exc:
        return 1 if exc.code else 0
    try:
        if args.cmd == "draft":
            return cmd_draft(args)
        if args.cmd == "apply":
            return cmd_apply(args)
        if args.cmd == "verify":
            root: Path = Path(args.root).resolve()
            folder: Path = Path(args.run).resolve()
            if args.window is not None:
                return cmd_verify_window(root, folder, args.window)
            return cmd_verify_run(root, folder, Path(args.legacy_debt_file) if args.legacy_debt_file else None)
    except FolderGroupError as exc:
        print(f"요약: 실행 불능 — {exc}")
        return 1
    ap.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
