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
    # 기술 낱말 `event` — 표준 트리의 고정 칸(`event/`)이고 브로커 봉투의 식별 수단(`event_id` — #533)이라 framework 가
    # 일반 뜻으로 쓴다(`message`·`request`·`error` 와 같은 부류). 받아들인 한계: `event` 를 업무 명사로 쓰는 영역의
    # `event_id` 꼴 누설은 이 낱말로는 못 잡는다 — 그 영역의 다른 낱말이 함께 새면 잡는다. 감수가 짚을 수는 있지만
    # 따로 보게 하는 규칙은 없다(`message` 와 같은 처지).
    # 같은 칸 낱말 `entity`·`object` 는 현장 근거가 없어 넣지 않았다(`object` 는 넣으면 기존 #518 줄 글자가 바뀐다).
    "event",
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


def server_bc_dirs(root: Path) -> list[Path]:
    """뿌리 `application/` 컨테이너의 BC — BC 마다 도는 검사의 대상이자 «어느 BC 든» 을 묻는 framework · `<project>/` 쪽 검사의 재료.

    뿌리 밖 `application/`(자매 플러그인 dddjango-web 의 `web/application/<단위>` · `web_test/application/<단위>` · 기록 사본
    `.dddjango-web/**/application/<bc>`)은 서버 BC 가 아니다 — 고르면 화면 구역을 서버 BC 규율로 재고, 같은 이름 사본이 서버 BC 를
    «타 BC» 로 만든다(#505 · #331).
    """
    c: Path = root / "application"
    if not c.is_dir() or set(c.parts) & SKIP_DIRS:
        return []
    return [p for p in sorted(c.iterdir()) if p.is_dir() and not p.name.startswith(".")]


# framework 쪽 동음 낱말 — BC 이름에도 나오지만 framework 능력 · 순수 계산이 기술 뜻으로 쓰는 낱말(#628 · predicates ⓑ — 저장소가
# 유지하는 데이터 · 닫지 않는다). 영역이 서른 개쯤 되면 BC 어휘 합집합이 일반 영어를 덮어, 업무 낱말 0 인 framework 계약이 붉어진다.
# BC 마다 도는 검사(bc_vocab)와 전역 STOPWORDS 는 그대로다 — 합집합(all_vocab)에서만 뺀다. 등재는 현장 근거가 있는 낱말만, 그때의
# 합집합 출처를 대조해 사유를 남긴다. 받아들인 한계: 그 낱말을 업무 뜻으로 쓰는 영역(work · register 는 실제로 그렇다)의 framework
# 누설은 이 낱말로는 못 잡는다 — 그 영역의 다른 낱말이 함께 새면 잡는다(`event` 와 같은 처지).
FRAMEWORK_HOMONYMS = frozenset({
    # 식별 · 사전 키 — BC 의 멱등 키 · 키로 찾기 · 물은 항목 키 이름 ↔ framework 의 키 · 사전 키 정렬(RFC 8785 JCS).
    "key", "keys",
    # 병렬 작업 능력의 낱말 — BC 의 «작업 풀 없음» 열거 값 · «…없음» 예외 · 남은 초 · 기다림 · 다 씀 · «이내» 조건 ↔ framework
    # 병렬 작업 능력의 시한 실행 · 풀 없음 예외 · 대기 초.
    "pool", "unavailable", "seconds", "wait", "run", "within",
    # 업무 뜻과 겹치는 낱말 — BC 의 문헌 식별 값(work) · 가입(register) ↔ framework 병렬 작업 · 작업 등록.
    "work", "register",
    # JSON 값 · 컨테이너 영어 — BC 의 JSON 문서 값 · 범위 수열 ↔ pure/ JSON 값 별칭 · `collections.abc` 의 `Mapping` · `Sequence`
    # (mapping 은 2026-10-03 현장 보고(F4-42)의 합집합 출처 — 2026-10-26 현장 합집합에는 출처가 없다).
    "json", "mapping", "sequence",
})


def all_vocab(root: Path) -> set[str]:
    """서버 BC 합집합 — framework · broker 쪽 업무 어휘 검사(#47·#587·#617·#562·#518 · 후보 #448·#425 · ⓓ#36)의 재료.

    framework 쪽 동음 낱말(`FRAMEWORK_HOMONYMS`)은 뺀다."""
    out: set[str] = set()
    for bc in server_bc_dirs(root):
        out |= bc_vocab(bc)
    return out - FRAMEWORK_HOMONYMS


def bc_names(root: Path) -> set[str]:
    """서버 BC 이름 — framework · celery 쪽 «BC 이름 0» 검사(#52·#416·#426·#444)와 ACL 상대 «우리 BC» 판정(#365)의 재료."""
    return {bc.name for bc in server_bc_dirs(root)}


def container_bc_names(bc: Path) -> set[str]:
    """`bc` 가 든 `application/` 컨테이너의 BC 이름(자기 포함) — «타 BC 이름» 낱말 검사(#151·#233·#364)의 재료.

    다른 컨테이너(자매 플러그인 dddjango-web 의 `web/application/<단위>` 등)의 폴더 이름은 이 BC 의
    공급자가 아니다 — 저장소 전체 이름(`bc_names`)으로 세면 화면 구역 이름이 서버 포트 이름을 붉게 잡는다.
    """
    return {p.name for p in bc.parent.iterdir() if p.is_dir() and not p.name.startswith(".")}


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
