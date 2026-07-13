#!/usr/bin/env python3
"""dddjango ninja 경계 미들웨어 결정적 백스톱 (implementation-django-ninja §6 집행).

BC 의 `presentation_layer/` 에서 *자가 정의* 한 Django 미들웨어가 전역
`settings.MIDDLEWARE` 에 **자가등록** 되면 적출한다. 이는 코덱스가 3런(smoke3
`OrderJsonContentTypeMiddleware`·smoke6 `OrderApiContentNegotiationMiddleware`·
final `OrdersApiContentNegotiationMiddleware`) 반복한 안티패턴 — 406/415 콘텐츠 협상을
`request.path` 하드코딩한 전역 미들웨어로 자작한 것. django-ninja 는 협상/임의 status 를
*경계 안* 에서 네이티브로 낸다(§6.3: `Parser.parse_body` 안 content_type 검사→415·
경계 `Accept` 검사→`HttpError(406)`·`HttpError(status)`→임의). BC presentation 이 전역
미들웨어 체인을 점유하면 라우팅 중복·BC 격리 침범·`request.path` 변경 시 silent 깨짐 = 순손해.

*왜 결정적 백스톱인가* — "협상/HTTP 관심사를 미들웨어로 자작" 은 코더가 표준의 *네이티브
경계* 대신 무거운 메커니즘으로 새는 회귀이고, 양성 레시피(가이드)만으로는 라이브 재발을 못
막은 선례가 있다(DEVLOG: 양성 레시피 + 집행 게이트). *BC presentation 모듈을 가리키는
MIDDLEWARE 항목* 은 모델 무관 신호다. 협상의 *의미* 정합(올바른 406/415 본문 등)은 범위
밖(reviewer 몫).

거짓양성 ≈ 0 — *BC presentation 을 가리키는 전역 미들웨어 등록* 만 차단:
  G1) 레포 루트 직속 `application/` 존재 = 표준 채택. 없으면 exit 0(§1.1 비표준 존중).
  G2) 프로젝트 settings 의 `MIDDLEWARE`(리스트/튜플/`+=`/`.append`/`.insert`/`.extend`/`+`
      concat — **AST 로 추출해 주석·docstring 은 무시**) 항목 중 점 표기 경로가
      `application(.<app>...).presentation_layer.…` 인 것이 있다 = BC 표현 계층이 전역
      미들웨어 체인을 점유. Django 기본(`django.middleware.*`)·서드파티(`corsheaders.*`)·
      프로젝트 레벨(`<project>.*`)·횡단(`common.*`) 미들웨어는 이 경로가 아니라 제외된다.
  G1 ∧ ∃(그런 MIDDLEWARE 항목) → exit 2(blocker). 아니면 exit 0.

사용법: check-ninja-boundary-middleware.py [TARGET_DIR]   (기본=현재 디렉터리)
종료코드: 0=clean(또는 표준 미적용), 2=blocker(발견 출력), 1=사용 오류.
"""
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

from migration_scope import (
    is_migration_owned_path,
    iter_non_migration_files,
    validate_migration_scope,
)

SKIP_DIRS = {
    ".venv", "venv", "site-packages", "node_modules", ".git", "__pycache__",
    "build", "dist", ".tox", ".mypy_cache", ".pytest_cache", ".eggs",
    "docs", "examples",  # 비-런타임 settings 예시 스캔 회피(reviewer-FP S·T).
}

# 점 표기 모듈 경로가 BC presentation 코드를 가리키는가:
#   application[.<무엇이든>].presentation_layer[.<무엇이든>].<Class>
_BC_PRESENTATION_PATH = re.compile(
    r"^application(?:\.[A-Za-z_]\w*)*\.presentation_layer(?:\.[A-Za-z_]\w*)+$"
)


def _root_application(root: Path) -> Path | None:
    """레포 루트 *직속* `application/` 컨테이너(있으면). rglob 금지 — 중첩 오인 차단."""
    cand = root / "application"
    return cand if not is_migration_owned_path(root, cand) and cand.is_dir() else None


def _iter_settings_files(root: Path):
    """프로젝트 설정 파일(`settings.py` 또는 `settings/` 패키지의 `*.py`)을 yield."""
    for path in iter_non_migration_files(root, name_pattern="*.py"):
        if set(path.parts) & SKIP_DIRS:
            continue
        if path.name == "settings.py" or path.parent.name == "settings":
            yield path


def _collect_str_constants(node: ast.AST, out: list[str]) -> None:
    """리스트/튜플/집합/`+` concat 안의 문자열 리터럴을 재귀 수집(변수 참조는 건너뜀)."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        out.append(node.value)
    elif isinstance(node, (ast.List, ast.Tuple, ast.Set)):
        for elt in node.elts:
            _collect_str_constants(elt, out)
    elif isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        _collect_str_constants(node.left, out)
        _collect_str_constants(node.right, out)


def _middleware_entries(text: str) -> list[str]:
    """AST 로 `MIDDLEWARE` 할당/증강/`.append|insert|extend` 의 문자열 항목을 추출.

    주석·docstring·다른 변수의 문자열은 자연히 제외된다(reviewer-FP A·F·G). 리스트뿐 아니라
    튜플·`+=`·`.append`·`+` concat 도 포착한다(reviewer 회피 E1·E2·E6·E14)."""
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return []
    entries: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            if any(isinstance(t, ast.Name) and t.id == "MIDDLEWARE" for t in node.targets):
                _collect_str_constants(node.value, entries)
        elif isinstance(node, ast.AnnAssign):
            if (
                isinstance(node.target, ast.Name)
                and node.target.id == "MIDDLEWARE"
                and node.value is not None
            ):
                _collect_str_constants(node.value, entries)
        elif isinstance(node, ast.AugAssign):
            if isinstance(node.target, ast.Name) and node.target.id == "MIDDLEWARE":
                _collect_str_constants(node.value, entries)
        elif isinstance(node, ast.Call):
            func = node.func
            if (
                isinstance(func, ast.Attribute)
                and func.attr in ("append", "insert", "extend")
                and isinstance(func.value, ast.Name)
                and func.value.id == "MIDDLEWARE"
            ):
                for arg in node.args:
                    _collect_str_constants(arg, entries)
    return entries


def _offending_entries(settings_text: str) -> list[str]:
    return [e for e in _middleware_entries(settings_text) if _BC_PRESENTATION_PATH.match(e)]


def main(argv: list[str]) -> int:
    root = Path(argv[1]).resolve() if len(argv) > 1 else Path.cwd()
    if not root.is_dir():
        print(f"[check-ninja-boundary-middleware] 사용 오류: 디렉터리 아님 {root}", file=sys.stderr)
        return 1
    if not validate_migration_scope(root, "check-ninja-boundary-middleware"):
        return 1

    if _root_application(root) is None:
        return 0  # 표준 레이아웃 미적용 → §1.1 존중, 해당 없음.

    findings: list[tuple[str, str]] = []
    for settings_path in _iter_settings_files(root):
        try:
            text = settings_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        rel = settings_path.relative_to(root).as_posix()
        for entry in _offending_entries(text):
            findings.append((rel, entry))

    if findings:
        print(
            "[check-ninja-boundary-middleware] BLOCKER — BC `presentation_layer` 코드가 전역 "
            "`MIDDLEWARE` 에 자가등록됐다(implementation-django-ninja §6):"
        )
        for rel, entry in findings:
            print(f"  - {rel}: {entry}")
        print(
            "  근거: BC 의 표현 계층은 전역 Django 미들웨어 체인을 점유하지 않는다(라우팅 중복·BC "
            "격리 침범·`request.path` 하드코딩 시 경로 변경에 silent 깨짐). 대표 회귀는 406/415 "
            "콘텐츠 협상을 미들웨어로 자작한 것 — 협상·임의 status 는 ninja 경계 안에서 낸다"
            "(§6.3: `Parser.parse_body` 안 content_type 검사→415 · 경계 `Accept` 검사→"
            "`HttpError(406)` · `raise HttpError(status)`). 해당 처리를 operation/Parser 로 옮겨라. "
            "(Django 기본·서드파티·프로젝트 레벨·횡단 미들웨어는 이 백스톱 대상 아님.)"
        )
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
