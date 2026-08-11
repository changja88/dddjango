"""#628 «업무 어휘» 데이터 모듈 — 검사기 공유 재료 (진단 0 · standard_tree 와 같은 부류).

명세 #628: 한 BC 의 업무 어휘는 `domain_layer/**` 아래 공개 심볼(모듈·클래스·함수·
Enum 값) 이름의 토큰 집합이다 — 폴더 이름만이 아니다. #47·#52·#372·#463·#518·#562·
#587·#617 이 이 집합 «하나»를 재료로 쓴다. 별도의 용어집 파일은 두지 않는다.

불용어 목록도 «저장소가 유지하는 데이터»다(#628 · predicates ⓑ) — `Id`·`Status` 처럼
어느 BC 에나 나오는 낱말을 안 빼면 framework 검사가 대량 오탐을 낸다. 목록은 닫지
않는다(predicates ⓒ — #367 방식).

공유가 «옆»(검사기 간 import)이 아니라 «아래»(데이터 모듈)로 가는 이유: 같은 집합을
검사기마다 다시 쓰면 드리프트가 조용히 갈린다(T61 ⓑ).
"""
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

SKIP_DIRS = {
    ".venv", "venv", "site-packages", "node_modules", ".git", "__pycache__", ".dddjango",
    "build", "dist", ".tox", ".mypy_cache", ".pytest_cache", ".eggs",
}

# 불용어 — 어느 BC 에나 나오는 낱말(#628 축자 여섯 + 같은 부류). 닫지 않는다.
STOPWORDS = frozenset({
    "id", "status", "name", "item", "type", "value",
    "get", "set", "list", "all", "new", "create", "update", "delete", "add", "remove",
    "save", "find", "count", "exists", "data", "info", "result", "request", "response",
    "error", "exception", "base", "main", "init", "self", "none", "true", "false",
    "str", "int", "bool", "float", "dict", "code", "message", "at", "of", "to", "in",
    "is", "has", "can", "not", "and", "or", "for", "with", "by", "on", "from",
})

_TOKEN_RE = re.compile(r"[A-Z][a-z0-9]*|[a-z][a-z0-9]*|[0-9]+")


def tokens(name: str) -> set[str]:
    """camelCase·snake_case 를 함께 갈라 소문자 토큰으로 — 불용어·두 글자 이하는 뺀다."""
    return {t.lower() for t in _TOKEN_RE.findall(name)
            if len(t) >= 3 and t.lower() not in STOPWORDS}


def _iter_py(base: Path) -> list[Path]:
    return [p for p in sorted(base.rglob("*.py")) if not set(p.parts) & SKIP_DIRS]


def bc_vocab(bc_dir: Path) -> set[str]:
    """한 BC 의 업무 어휘 — `domain_layer/**` 공개 심볼(모듈·클래스·함수·Enum 값) 토큰."""
    out: set[str] = set()
    domain = bc_dir / "domain_layer"
    if not domain.is_dir():
        return out
    for py in _iter_py(domain):
        if py.name != "__init__.py":
            out |= tokens(py.stem)
        try:
            mod = ast.parse(py.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, SyntaxError):
            continue
        for node in ast.walk(mod):
            if isinstance(node, ast.ClassDef) and not node.name.startswith("_"):
                out |= tokens(node.name)
                bases = {b.id if isinstance(b, ast.Name) else getattr(b, "attr", "") for b in node.bases}
                if bases & {"Enum", "StrEnum", "IntEnum", "TextChoices", "IntChoices", "Choices"}:
                    for st in node.body:
                        if isinstance(st, ast.Assign) and isinstance(st.value, ast.Constant) \
                                and isinstance(st.value.value, str):
                            out |= tokens(st.value.value)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and not node.name.startswith("_"):
                out |= tokens(node.name)
    # 폴더 이름(애그리거트·종류 밖 이름)도 어휘다 — 트리 고정 칸은 어휘가 아니다.
    fixed = {"entity", "value_object", "event", "exception", "domain_service",
             "shared_value_object", "__pycache__"}
    for d in domain.rglob("*"):
        if d.is_dir() and d.name not in fixed and not set(d.parts) & SKIP_DIRS:
            out |= tokens(d.name)
    return out


def bc_dirs(root: Path) -> list[Path]:
    out: list[Path] = []
    for c in root.rglob("application"):
        if not c.is_dir() or set(c.parts) & SKIP_DIRS:
            continue
        out.extend(p for p in sorted(c.iterdir()) if p.is_dir() and not p.name.startswith("."))
    return out


def all_vocab(root: Path) -> set[str]:
    """전 BC 합집합 — framework·broker 쪽 검사(#47·#52·#518·#617)의 재료."""
    out: set[str] = set()
    for bc in bc_dirs(root):
        out |= bc_vocab(bc)
    return out


def bc_names(root: Path) -> set[str]:
    return {bc.name for bc in bc_dirs(root)}


# python3.9 에는 sys.stdlib_module_names 가 없다 — 기본 목록으로 메운다.
STDLIB_FALLBACK = frozenset({
    "abc", "ast", "asyncio", "base64", "bisect", "calendar", "collections", "contextlib",
    "copy", "csv", "dataclasses", "datetime", "decimal", "email", "enum", "fractions",
    "functools", "hashlib", "heapq", "hmac", "html", "http", "importlib", "inspect", "io",
    "itertools", "json", "logging", "math", "numbers", "operator", "os", "pathlib", "queue",
    "random", "re", "secrets", "socket", "sqlite3", "statistics", "string", "struct", "sys",
    "test", "textwrap", "threading", "time", "traceback", "types", "typing", "unicodedata",
    "unittest", "uuid", "warnings", "weakref", "xml", "zoneinfo", "__future__",
})


def tech_names() -> set[str]:
    """#19 기술 이름 집합 — stdlib 모듈명 ∪ 설치 배포판 최상위 모듈명(정확 일치용)."""
    names: set[str] = set(getattr(sys, "stdlib_module_names", ())) | set(STDLIB_FALLBACK)
    try:
        from importlib.metadata import packages_distributions
        names |= set(packages_distributions())
    except Exception:  # 메타데이터가 없는 환경 — stdlib 만으로 진행
        pass
    # 파이썬 밖에서 오는 흔한 기술 낱말 — 배포판 이름에 안 잡히는 것(데이터 목록 · 닫지 않는다).
    names |= {"smtp", "http", "grpc", "kafka", "redis", "rabbitmq", "celery", "postgres",
              "postgresql", "mysql", "sqlite", "s3", "sqs", "sns", "stripe", "django",
              "ninja", "drf", "rest"}
    return names
