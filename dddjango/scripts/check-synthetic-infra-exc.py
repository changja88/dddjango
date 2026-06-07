#!/usr/bin/env python3
"""dddjango 인프라 예외 *합성* 결정적 백스톱 (ACL-EX2).

좁은 **고정밀·저-recall** 게이트다. `infra_layer`(ACL·리포지토리 등 인프라 경계)가
*계산된* transient/경합(낙관락·CAS 재시도 소진 등 — 드라이버가 던진 게 아니라 코드가
스스로 판정한 결과)을 신호하려고 raw 인프라 DB 예외(`OperationalError`/`DatabaseError`/
`IntegrityError`)를 **`from` 없이 새로 생성(Call)해 raise**한 정확한 형태(ACL-EX2 — 라이브에서
난 형태: ACL CAS 소진 시 `raise OperationalError(f"재고 차감 CAS 경합이 ...")`)만 차단한다.

왜 차단하나: presentation 경계의 transient recognizer(`_is_retryable_db_error`)는 *실 드라이버*
예외의 메시지/시그니처·`__cause__` SQLSTATE 로 retryable 을 가린다. 코드가 *합성*한 인프라
예외는 실 메시지·`__cause__` 가 없어 recognizer 사각 → 영구장애로 오분류돼 503 의도가 500 으로
샌다(과소매핑). 계산된 transient 는 협력 포트가 선언한 **도메인 transient-마커 예외 타입**으로
raise 해 핸들러가 *타입* 으로 매핑해야 한다(implementation-django-ninja §6.2).

`from` 절은 면제한다 — 실 드라이버 예외를 잡아 재시도하다 *그 원본을 보존*해 되던지는
`raise OperationalError(...) from driver_exc` 는 `__cause__` 가 살아 recognizer 가 SQLSTATE 로
인식하므로 정당한 대안이다(node.cause 가 None 이 아니면 통과).

저-recall(일부러 안 잡음 — discipline-reviewer 의미 렌즈가 담당):
  - 헬퍼·변수 우회 합성(`exc = OperationalError(...); raise exc`, `raise _make_transient()`),
  - `infra_layer` 밖(application·domain) 합성,
  - `raise OperationalError(...) from None`(명시 cause 억제).
거짓 양성을 내면 정당한 도메인 타입 번역(`raise StockContention(...) from exc`)·`from` 보존
재던지기·테스트 더블을 막으므로, **infra_layer 경로 + raw 인프라 예외 *생성*(Call) + `from`
부재 + 비테스트 + git-touched 의 AND** 로만 차단한다.

AND 조건(전부 참이어야 blocker):
  1) 파일 경로에 `infra_layer` 디렉터리 포함(ACL·리포지토리 등 인프라 경계). 도메인 타입
     (`StockContention` 등)은 TARGET_EXC 가 아니라 매칭 자체가 안 됨.
  2) `raise` 의 예외가 **Call** 이고 그 생성 타입이 `OperationalError`/`DatabaseError`/
     `IntegrityError` — 변수 재던지기(`raise e`)·bare 클래스는 Call 이 아니라 제외(정당 전파).
  3) `raise ... from X` 의 cause 가 **부재**(`node.cause is None`) — `from` 보존 재던지기는 제외.
  4) (git 레포면) 그 파일이 이번 변경에서 새로 추가/수정됨 — 기존 커밋 코드는 존중.

사용법: check-synthetic-infra-exc.py [TARGET_DIR]   (기본 TARGET_DIR=현재 디렉터리)
종료코드: 0=clean, 2=blocker(발견 출력), 1=사용 오류.
"""
from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

SKIP_DIRS = {".venv", "venv", "site-packages", "node_modules", ".git", "__pycache__"}
TEST_DIR_NAMES = {"test", "tests"}
INFRA_DIR_NAME = "infra_layer"

TARGET_EXC = {"OperationalError", "DatabaseError", "IntegrityError"}


def _call_name(node: ast.AST) -> str | None:
    """Call 의 func 가 가리키는 이름 — `OperationalError(...)` 든 `db.OperationalError(...)` 든."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def _synthesis_raises(tree: ast.AST) -> list[tuple[int, str]]:
    """`from` 없이 인프라 DB 예외를 *생성*(Call)해 raise 하는 지점 — (lineno, exc_name)."""
    out: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Raise):
            continue
        if node.cause is not None:           # `raise ... from X` → 원본 보존(면제).
            continue
        exc = node.exc
        if not isinstance(exc, ast.Call):    # 변수 재던지기·bare 클래스 → 정당 전파(면제).
            continue
        nm = _call_name(exc.func)
        if nm in TARGET_EXC:
            out.append((node.lineno, nm))
    return out


def _find_infra_files(root: Path) -> list[Path]:
    out: list[Path] = []
    for path in root.rglob("*.py"):
        parts = set(path.parts)
        if parts & SKIP_DIRS:
            continue
        if parts & TEST_DIR_NAMES or path.name.startswith("test_") or path.name == "conftest.py":
            continue
        if INFRA_DIR_NAME not in path.parts:   # 인프라 경계 한정(고정밀).
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
        print(f"[check-synthetic-infra-exc] 사용 오류: 디렉터리 아님 {root}", file=sys.stderr)
        return 1

    findings: list[str] = []
    for infra_file in _find_infra_files(root):
        try:
            tree = ast.parse(infra_file.read_text(encoding="utf-8", errors="replace"))
        except (OSError, SyntaxError):
            continue
        hits = _synthesis_raises(tree)
        if hits and _is_new_or_modified(root, infra_file):
            for lineno, exc_name in hits:
                findings.append(
                    f"  - {infra_file.relative_to(root)}:{lineno} "
                    f"raise {exc_name}(...) — `from` 없이 인프라 예외 합성"
                )

    if findings:
        print(
            "[check-synthetic-infra-exc] BLOCKER — infra_layer 가 계산된 transient/경합을 raw "
            "인프라 예외로 *합성*해 raise 함(ACL-EX2):"
        )
        for f in findings:
            print(f)
        print(
            "  근거: implementation-django-ninja §6.2. presentation transient recognizer 는 "
            "*실 드라이버* 예외의 메시지/SQLSTATE(`__cause__`)로 retryable 을 가리므로, 코드가 "
            "합성한 인프라 예외는 사각 → 영구장애로 오분류돼 503 의도가 500 으로 샌다(과소매핑). "
            "계산된 transient 는 협력 포트가 선언한 도메인 transient-마커 예외 *타입*으로 raise 해 "
            "핸들러가 타입 매핑하라(Codex 대안 B). 실 드라이버 예외를 잡아 재시도하다 소진했다면 "
            "원본을 `raise ... from driver_exc` 로 보존하면 recognizer 가 `__cause__` 로 인식한다. "
            "설계로 반송하라."
        )
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
