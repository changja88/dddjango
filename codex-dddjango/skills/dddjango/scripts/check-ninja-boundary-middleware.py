#!/usr/bin/env python3
"""dddjango ninja 경계 미들웨어 결정적 백스톱 (implementation-django-ninja §6 집행).

BC 의 driving 층(`driving_layer/`)에서 *자가 정의*
한 Django 미들웨어가 전역 `settings.MIDDLEWARE` 에 **자가등록** 되면 적출한다. 대표
회귀는 406/415 콘텐츠 협상을 `request.path` 하드코딩한 전역 미들웨어로 자작한 것 —
django-ninja 는 협상/임의 status 를 *경계 안* 에서 네이티브로 낸다(§6.3). BC 입구가
전역 미들웨어 체인을 점유하면 라우팅 중복·BC 격리 침범·경로 변경 시 silent 깨짐이다.

판정 — 프로젝트 settings 의 `MIDDLEWARE`(리스트/튜플/`+=`/`.append`/`.insert`/`.extend`/
`+` concat — AST 로 추출해 주석·docstring 은 무시) 항목 중 점 표기 경로가
`application(.<bc>...).driving_layer.…` 인 것이 있으면
blocker. Django 기본(`django.middleware.*`)·서드파티·프로젝트 레벨·framework 레벨
미들웨어는 이 경로가 아니라 제외된다.

가드 계약 (명세 조각 ⓐ):
  - 대상 0건 가드(#74): 채택 신호는 있는데 settings 파일이 0건이면 exit 2.

사용법: check-ninja-boundary-middleware.py [TARGET_DIR]   (기본: 현재 디렉터리)
종료코드: 0=clean(또는 표준 미채택) · 1=사용/분석 오류 · 2=blocker(발견 출력)
구조화 레코드: DJR_FINDINGS_JSON=<경로> 지정 시 findings.py(공용 모듈)가 JSON lines 를
추가 방출한다. 위반 라인은 공용 포매터의 계약 문법 `- {where}: {msg}` 로 방출하며
record 순서 = stdout 위반 라인 순서다(T2-1 출력 계약 v2).

그래프 좌표(T2-2): 규범 정본 = 온톨로지 그래프(`ontology/rules/`) · 이 검사기의 #N ↔ Work 조인은
  alias 대장(`ontology/wiring/aliases.ttl`)이 소유한다. 조인 확정: 없음(대장 미등재 — T3 이월).
  미확정 #N 은 T3 이관에서 해소한다(현행 조인 3종 — 판단표
  `workspace/design/2026-08-20-ontology-t2-2-alias-ledger.md` §2·§5).
"""
from __future__ import annotations

import ast
import re
import sys

import checker_target
from findings import ContractFindings, emit_all, zero_target_guard
from pathlib import Path

try:
    import standard_tree as tree
except ImportError:  # 데이터 모듈 없이는 판정 불가 — fail-closed(분석 오류)
    print("분석 오류: standard_tree.py 를 찾지 못했다 — 검사기와 같은 폴더에 있어야 한다", file=sys.stderr)
    sys.exit(1)

# rule-owner-map 규칙 0건 — 선행 계약 소유(reverse_coverage PRIOR_CONTRACT_SCRIPTS 등재).
CONTRACT_REF = "선행 계약(08-04 API-error) 소유"

SKIP_DIRS = {
    ".venv", "venv", "site-packages", "node_modules", ".git", "__pycache__", ".dddjango",
    "build", "dist", ".tox", ".mypy_cache", ".pytest_cache", ".eggs",
    "docs", "examples",  # 비-런타임 settings 예시 스캔 회피.
}
DJANGO_APP_MARKERS = ("models.py", "apps.py", "views.py", "admin.py")
NEW_LAYERS = {"driving_layer", "application_layer", "domain_layer", "driven_layer"}

DRIVING = "driving_layer"

# 점 표기 모듈 경로가 BC driving 코드를 가리키는가:
#   application[.<무엇이든>].driving_layer[.<무엇이든>].<Class>
_BC_DRIVING_PATH = re.compile(
    r"^application(?:\.[A-Za-z_]\w*)*\." + DRIVING + r"(?:\.[A-Za-z_]\w*)+$"
)


def _has_adoption_signal(bc_dir: Path) -> bool:
    """채택 신호원 둘(#78) — check-layer-skeleton 과 같은 판."""
    has_layer = any((bc_dir / n).is_dir() for n in NEW_LAYERS)
    has_marker = any((bc_dir / m).is_file() for m in DJANGO_APP_MARKERS) or any(
        p.is_dir() and p.name.startswith("django_") for p in bc_dir.iterdir()
    )
    return has_layer or has_marker


def _adopted(target: Path) -> bool:
    for c in target.rglob("application"):
        if not c.is_dir() or set(c.parts) & SKIP_DIRS:
            continue
        for bc in sorted(c.iterdir()):
            if bc.is_dir() and not bc.name.startswith(".") and _has_adoption_signal(bc):
                return True
    return False


def _find_settings_files(root: Path) -> list[Path]:
    out: list[Path] = []
    for path in root.rglob("*.py"):
        if set(path.parts) & SKIP_DIRS:
            continue
        if any(seg.startswith(".") for seg in path.relative_to(root).parts[:-1]):
            continue  # 숨김 디렉터리 = 도구·하네스 영역(F-C 2026-08-14)
        if path.name == "settings.py" or path.parent.name == "settings":
            out.append(path)
    return sorted(out)


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
    """AST 로 `MIDDLEWARE` 할당/증강/`.append|insert|extend` 의 문자열 항목을 추출."""
    try:
        mod = ast.parse(text)
    except SyntaxError:
        return []
    entries: list[str] = []
    for node in ast.walk(mod):
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


def main(argv: list[str]) -> int:
    if len(argv) > 1:
        print(f"사용법: {Path(sys.argv[0]).name} [TARGET_DIR]", file=sys.stderr)
        return 1
    target = Path(argv[0]).resolve() if argv else Path.cwd()
    bad_target_reason = checker_target.bc_shaped_target_reason(target)
    if bad_target_reason is not None:
        print(f"사용 오류: {bad_target_reason}", file=sys.stderr)
        return 1
    if not target.is_dir():
        print(f"사용 오류: 디렉터리가 아니다 — {target}", file=sys.stderr)
        return 1

    settings_files = _find_settings_files(target)

    # 대상 0건 가드(#74) — 채택 신호는 있는데 settings 가 0건이면 경로 계약이 어긋난 것.
    if not settings_files:
        if _adopted(target):
            guard = zero_target_guard(
                "blocker: 채택 신호는 있는데 settings 파일이 0건이다 — 조용한 무동작을 금지한다(#74)"
            )
            emit_all(guard, printer=print, indent="")
            return 2
        print("표준 레이아웃 미채택 — 검사 대상 없음 (clean)")
        return 0

    # 라인 = 레코드 필드의 순수 함수(계약 문법 `- {where}: {msg}`) — emit_all 이
    # 인쇄와 레코드 방출을 같은 순서로 수행한다(출력 계약 v2).
    findings = ContractFindings(CONTRACT_REF, defer=True)
    for settings_path in settings_files:
        try:
            text = settings_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        rel = settings_path.relative_to(target).as_posix()
        for entry in _middleware_entries(text):
            if _BC_DRIVING_PATH.match(entry):
                # where 는 파일 단위 — _middleware_entries 가 lineno 를 보존하지 않는다
                # (정밀화는 T2-2 정비 후보 · 개작 원칙 = 재료 불변).
                findings.add(
                    where=rel,
                    msg=f"BC driving 층 미들웨어 {entry} 가 전역 MIDDLEWARE 에 자가등록됐다 — "
                        f"협상·임의 status 는 ninja 경계 안에서 낸다(§6.3)",
                    symbol=entry,
                )

    if findings:
        print(f"blocker {len(findings)}건 — BC driving 층 코드가 전역 MIDDLEWARE 에 자가등록됐다")
        emit_all(findings, printer=print)
        print(
            "  근거: BC 입구는 전역 미들웨어 체인을 점유하지 않는다 — 협상·임의 status 는 "
            "ninja 경계 안에서 낸다(`Parser.parse_body` 415 · `HttpError(406)` · `HttpError(status)`). "
            "해당 처리를 operation/Parser 로 옮겨라."
        )
        return 2
    print(f"clean — settings {len(settings_files)}개 규율 일치 (standard_tree {tree.SOURCE_SHA})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
