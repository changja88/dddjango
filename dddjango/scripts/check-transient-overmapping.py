#!/usr/bin/env python3
"""dddjango transient 인프라 예외 과잉매핑 결정적 백스톱 (maj1).

좁은 **고정밀·저-recall** 게이트다. API 경계에서 `OperationalError`/`DatabaseError`
(transient 인프라 예외)를 처리하는 핸들러가 **영구장애 변종을 구별하는 분기 없이**
클래스 통째를 retryable status(503/409)로 *무조건* 매핑한 정확한 형태(maj1 — 라이브에서
난 형태: `@api.exception_handler(OperationalError)` 본문이 시그니처 판별 없이 `status=503`
을 무조건 반환)만 차단한다. disk I/O·`no such table`·`database is malformed` 같은 영구
장애를 retryable 로 오분류해 클라이언트·재시도 루프가 영원히 못 고치는 장애를 두드리게 한다.

이 판정은 G1에서 이미 승인된 `preserve-established` brownfield handler를 보존할 때 그 handler가
인프라 오류 전체를 retryable로 넓히지 않게 지키는 방어선이다. `dddjango-code-json`에서는 custom
handler/recognizer 자체가 controller 직접 오류 경계 계약에 독립적으로 위배되므로, 이 checker가
발화하지 않아도 새 handler/recognizer를 만들 근거가 되지 않는다.

헬퍼 무조건-True 위장(`if self._retryable(exc): ...` 이나 헬퍼가 항상 True)·register-only
+무어노테이션 핸들러는 **일부러 잡지 않는다**(저-recall) — 그건 ② design-architect 생산자
예방(명세에 "transient 변종만 retryable")과 ③ discipline-reviewer 의미 체크(transient
과잉매핑 렌즈)가 담당한다. 거짓 양성을 내면 정당한 분기 핸들러(sqlstate 로 가르는 형태)·
도메인 503(StockContention 등)·IntegrityError 500·이미 승인된 preserve handler의 정당한
분기를 막으므로, **핸들러 타입 + 분기 부재 + retryable 반환의 AND** 로만 차단한다.

AND 조건(전부 참이어야 blocker):
  1) 함수가 transient 인프라 예외 핸들러 — `@*.exception_handler(OperationalError|
     DatabaseError)` 데코, 또는 파라미터 `exc: OperationalError|DatabaseError` 어노테이션
     (데코/register 방식 독립). StockContention·InsufficientStock 등 *도메인* 예외 핸들러는
     대상 타입이 아니라 제외(정당한 도메인 503).
  2) 본문에 영구장애 구별 분기가 **부재** — `if`/조건식 없음, retryable·sqlstate·pgcode
     판정 호출 없음, `__cause__`/`__context__`/sqlstate/pgcode 속성 접근 없음.
  3) 본문이 retryable status(503/409)를 반환 — `status[_code]=503|409` 키워드 또는 그
     리터럴 인자. 500-only 핸들러(IntegrityError 등)는 retryable 아니라 제외.
  4) (git 레포면) 그 파일이 이번 변경에서 새로 추가/수정됨 — 기존 커밋 코드는 존중.

사용법: check-transient-overmapping.py [TARGET_DIR]   (기본 TARGET_DIR=현재 디렉터리)
종료코드: 0=clean, 2=blocker(발견 출력), 1=사용 오류.
"""
from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

SKIP_DIRS = {".venv", "venv", "site-packages", "node_modules", ".git", "__pycache__"}
TEST_DIR_NAMES = {"test", "tests"}

RETRYABLE_STATUSES = {503, 409}
TARGET_EXC = {"OperationalError", "DatabaseError"}
BRANCH_CALL_HINTS = ("retryable", "sqlstate", "pgcode")
BRANCH_ATTRS = {"__cause__", "__context__", "sqlstate", "pgcode"}


def _exc_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def _is_target_handler(func: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """OperationalError/DatabaseError 핸들러인가 — 데코 또는 exc 어노테이션."""
    for dec in func.decorator_list:
        if isinstance(dec, ast.Call):
            fn = dec.func
            nm = fn.attr if isinstance(fn, ast.Attribute) else getattr(fn, "id", None)
            if nm == "exception_handler" and any(_exc_name(a) in TARGET_EXC for a in dec.args):
                return True
    for arg in func.args.args:
        if arg.annotation is not None and _exc_name(arg.annotation) in TARGET_EXC:
            return True
    return False


def _has_branch(func: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """영구장애 구별 분기(조건문·시그니처 판별 호출/속성)가 본문에 있는가."""
    for node in ast.walk(func):
        if isinstance(node, (ast.If, ast.IfExp)):
            return True
        if isinstance(node, ast.Call):
            fn = node.func
            nm = (fn.attr if isinstance(fn, ast.Attribute) else getattr(fn, "id", "")) or ""
            if any(h in nm.lower() for h in BRANCH_CALL_HINTS):
                return True
        if isinstance(node, ast.Attribute) and node.attr in BRANCH_ATTRS:
            return True
    return False


def _returns_retryable(func: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """retryable status(503/409)를 반환하는가 — 키워드 또는 리터럴 인자."""
    for node in ast.walk(func):
        if isinstance(node, ast.keyword) and node.arg in ("status", "status_code"):
            if isinstance(node.value, ast.Constant) and node.value.value in RETRYABLE_STATUSES:
                return True
        if isinstance(node, ast.Call):
            for a in node.args:
                if isinstance(a, ast.Constant) and a.value in RETRYABLE_STATUSES:
                    return True
    return False


def _find_production_files(root: Path) -> list[Path]:
    out: list[Path] = []
    for path in root.rglob("*.py"):
        parts = set(path.parts)
        if parts & SKIP_DIRS:
            continue
        if parts & TEST_DIR_NAMES or path.name.startswith("test_") or path.name == "conftest.py":
            continue
        out.append(path)
    return out


def _is_new_or_modified(root: Path, file_path: Path) -> bool:
    """git 레포면 이번 변경에서 추가/수정됐는지. git 아니면 True(가드 통과)."""
    if not (root / ".git").exists():
        return True
    try:
        rel = file_path.relative_to(root)
    except ValueError:
        return True
    try:
        tracked = subprocess.run(
            ["git", "-C", str(root), "ls-files", "--error-unmatch", str(rel)],
            capture_output=True,
        )
        if tracked.returncode != 0:
            return True  # 신규 파일.
        changed = subprocess.run(
            ["git", "-C", str(root), "diff", "--quiet", "HEAD", "--", str(rel)],
        )
        return changed.returncode != 0
    except (OSError, subprocess.SubprocessError):
        return True  # git 판단 불가 시 안전하게 가드 통과(나머지 AND 가 좁힌다).


def main(argv: list[str]) -> int:
    root = Path(argv[1]).resolve() if len(argv) > 1 else Path.cwd()
    if not root.is_dir():
        print(f"[check-transient-overmapping] 사용 오류: 디렉터리 아님 {root}", file=sys.stderr)
        return 1

    findings: list[str] = []
    for prod_file in _find_production_files(root):
        try:
            tree = ast.parse(prod_file.read_text(encoding="utf-8", errors="replace"))
        except (OSError, SyntaxError):
            continue
        hits = [
            (node.name, node.lineno)
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and _is_target_handler(node)
            and _returns_retryable(node)
            and not _has_branch(node)
        ]
        if hits and _is_new_or_modified(root, prod_file):
            for name, lineno in hits:
                findings.append(
                    f"  - {prod_file.relative_to(root)}:{lineno} {name}(): "
                    "영구장애 구별 분기 없이 OperationalError/DatabaseError 를 "
                    "통째 retryable(503/409)로 매핑"
                )

    if findings:
        print(
            "[check-transient-overmapping] BLOCKER — transient 인프라 예외 핸들러가 "
            "영구장애 변종을 구별하는 분기 없이 클래스 통째를 retryable 로 과잉매핑함(maj1):"
        )
        for f in findings:
            print(f)
        print(
            "  근거: 이 predicate는 G1에서 이미 승인된 `preserve-established` handler가 "
            "OperationalError/DatabaseError 전체를 retryable로 넓히지 않게 지킨다. 보존된 handler는 "
            "락·deadlock·serialization 같은 재시도성 시그니처와 disk I/O·malformed 같은 영구장애를 "
            "구별해야 한다. `dddjango-code-json`에서는 custom handler/recognizer 자체가 controller 직접 "
            "오류 경계 계약에 독립적으로 위배되며, 이 checker의 발화 여부는 새 handler/recognizer "
            "생성을 허가하지 않는다. 설계로 반송하라."
        )
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
