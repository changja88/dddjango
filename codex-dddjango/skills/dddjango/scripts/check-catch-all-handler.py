#!/usr/bin/env python3
"""dddjango catch-all 오류 핸들러 부재/되던지기 결정적 백스톱 (NJ-7).

좁은 **고정밀·저-recall** 게이트다. ninja API 경계가 도메인·인프라 예외 핸들러를
등록하면서 **최후방 catch-all(`@api.exception_handler(Exception)`)을 빠뜨리거나**,
핸들러가 예외를 problem+json 으로 변환하지 않고 **되던져(`raise exc`/bare `raise`)**
미식별(`KeyError`·`ValueError`)·비-retryable 예외를 Django 기본 500(DEBUG traceback
누출)으로 새게 한 정확한 형태(NJ-7 — 라이브에서 난 형태: Claude `api.py` 6핸들러에
Exception 최후방 부재 / Codex `order_api_router.py:117` permanent 시 `raise exc`)만
차단한다.

왜 차단하나: presentation 단일 변환점은 등록된 구체 핸들러로 *식별된* 예외만 덮는다.
최후방 `@api.exception_handler(Exception)` 가 없으면 식별 안 된 예외(프로그래밍 오류·
서드파티 예외)가 ninja 기본 traceback 핸들러로 가 본문에 스택을 노출한다(§6.2:368-371).
핸들러가 `raise` 로 되던지면 그 예외는 catch-all 로 안 가고 Django 로 전파돼 같은 누출이
난다(§6.2:477-479). **대안 B(`create_response` 오버라이드)는 면제가 아니다** — 그건
status 가 부여된 응답의 content-type 만 통일하고, 핸들러 없는 미식별 예외는 여전히
`create_response` 를 거치지 않고 Django 로 샌다(§6.2:479-480).

분석 단위 = **NinjaAPI 인스턴스(데코 변수명)** — `@<var>.exception_handler(...)` 의
`<var>` 로 핸들러를 그룹핑한다. 핸들러가 여러 파일(`api.py`/`api_order.py`)로 분산돼도
같은 인스턴스면 합산하므로, "이 파일엔 catch-all 이 없다"는 분산-파일 거짓양성을 막는다.

저-recall(일부러 안 잡음 — discipline-reviewer 의미 렌즈가 담당):
  - 핸들러 0개 + `create_response`-only(alt-B 단독) 미식별 누수,
  - catch-all 을 `api.add_exception_handler(Exception, fn)`(register 방식)로 등록,
  - 핸들러가 `return {}`/`return None` 등 비-problem 객체 반환(되던지기 아님),
  - `from builtins import Exception as Exc` 같은 rename 별칭.
거짓 양성을 내면 정당한 분산 핸들러·도메인 타입 번역(`raise X(...) from exc`)·대안 B+
catch-all 공존을 막으므로, **데코 핸들러 ≥1 + (catch-all 부재 OR 핸들러 되던지기) +
비테스트 + git-touched 의 AND** 로만 차단한다.

차단 조건(둘 중 하나라도, git-touched 그룹 한정):
  (1) catch-all 부재 — 한 인스턴스(`<var>`)에 `@<var>.exception_handler(...)` 핸들러가
      1개 이상인데 `@<var>.exception_handler(Exception|BaseException)` 최후방이 없음.
  (2) 핸들러 되던지기 — 임의 핸들러 본문이 bare `raise` 또는 `raise <name>`(cause 없음·
      Call 아님)로 예외를 되던짐. `raise NewType(...)`(도메인 번역)·`raise ... from x`
      (원본 보존)는 정당이라 면제.

사용법: check-catch-all-handler.py [TARGET_DIR]   (기본 TARGET_DIR=현재 디렉터리)
종료코드: 0=clean, 2=blocker(발견 출력), 1=사용 오류.
"""
from __future__ import annotations

import ast
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

SKIP_DIRS = {".venv", "venv", "site-packages", "node_modules", ".git", "__pycache__"}
TEST_DIR_NAMES = {"test", "tests"}

CATCH_ALL = {"Exception", "BaseException"}


def _exc_name(node: ast.AST) -> str | None:
    """예외 타입 이름 — `Exception` 든 `builtins.Exception` 든 끝 이름."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def _handler_decorator(func: ast.FunctionDef | ast.AsyncFunctionDef) -> tuple[str | None, str | None] | None:
    """`@<var>.exception_handler(<Exc>)` 데코면 (var_name, exc_name). 아니면 None."""
    for dec in func.decorator_list:
        if isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute):
            if dec.func.attr == "exception_handler":
                var = dec.func.value.id if isinstance(dec.func.value, ast.Name) else None
                exc = _exc_name(dec.args[0]) if dec.args else None
                return (var, exc)
    return None


def _reraise_lineno(func: ast.FunctionDef | ast.AsyncFunctionDef) -> int | None:
    """핸들러가 bare `raise`/`raise <name>`(cause 없음·Call 아님)로 되던지는 첫 lineno.

    `raise NewType(...)`(도메인 타입 번역)·`raise ... from x`(원본 보존)는 정당 → 면제."""
    for node in ast.walk(func):
        if isinstance(node, ast.Raise):
            if node.cause is not None:           # raise ... from x → 보존(면제).
                continue
            exc = node.exc
            if exc is None:                      # bare raise → 되던지기.
                return node.lineno
            if isinstance(exc, ast.Name):        # raise exc → 되던지기.
                return node.lineno
            # ast.Call(`raise NewType(...)`) → 새 예외 생성(번역·면제).
    return None


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
        print(f"[check-catch-all-handler] 사용 오류: 디렉터리 아님 {root}", file=sys.stderr)
        return 1

    # NinjaAPI 인스턴스(변수)별로 핸들러를 합산 — 분산-파일 거짓양성 차단.
    groups: dict[str | None, dict] = defaultdict(
        lambda: {"has_catchall": False, "handlers": [], "files": set()}
    )
    for prod_file in _find_production_files(root):
        try:
            tree = ast.parse(prod_file.read_text(encoding="utf-8", errors="replace"))
        except (OSError, SyntaxError):
            continue
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            hv = _handler_decorator(node)
            if hv is None:
                continue
            var, exc = hv
            g = groups[var]
            g["files"].add(prod_file)
            if exc in CATCH_ALL:
                g["has_catchall"] = True
            g["handlers"].append((prod_file, node.lineno, node.name, _reraise_lineno(node)))

    findings: list[str] = []
    for var, g in groups.items():
        if not g["handlers"]:
            continue
        if not any(_is_new_or_modified(root, f) for f in g["files"]):
            continue  # 기존 커밋 코드는 존중.
        label = f"@{var}.exception_handler" if var else "exception_handler"
        # 조건 (1) catch-all 부재.
        if not g["has_catchall"]:
            f0, ln0, _, _ = g["handlers"][0]
            findings.append(
                f"  - {f0.relative_to(root)}:{ln0} ({label}, 핸들러 {len(g['handlers'])}개): "
                f"최후방 catch-all `{label}(Exception)` 부재 — 미식별 예외가 problem+json "
                "단일변환점을 우회해 Django 기본 500(DEBUG traceback)으로 누출"
            )
        # 조건 (2) 핸들러 되던지기.
        for prod_file, _, name, reraise_ln in g["handlers"]:
            if reraise_ln is not None:
                findings.append(
                    f"  - {prod_file.relative_to(root)}:{reraise_ln} {name}(): "
                    "핸들러가 예외를 `raise` 로 되던짐 — problem+json 단일변환점을 우회해 "
                    "Django 로 전파(`raise X(...) from exc` 로 번역·보존하거나 직접 problem 반환하라)"
                )

    if findings:
        print(
            "[check-catch-all-handler] BLOCKER — ninja 오류 변환의 catch-all 완전성 위반"
            "(catch-all 부재 또는 핸들러 되던지기·NJ-7):"
        )
        for f in findings:
            print(f)
        print(
            "  근거: implementation-django-ninja §6.2(368-371·469-485). 식별 안 된 예외는 "
            "최후방 `@api.exception_handler(Exception)` 가 500 problem+json 으로 변환하고 스택은 "
            "`logger.exception` 으로만 남긴다(본문 노출 차단). 핸들러는 problem 을 *반환*해야지 "
            "`raise` 로 되던지면 Django 로 누출된다. 대안 B(`create_response`)는 미식별 예외를 "
            "덮지 못하므로 catch-all 을 대체하지 못한다. 설계로 반송하라."
        )
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
