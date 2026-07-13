#!/usr/bin/env python3
"""dddjango catch-all/HttpError 오류 핸들러 부재·되던지기 결정적 백스톱 (NJ-7).

좁은 **고정밀·저-recall** 게이트다. ninja API 경계가 도메인·인프라 예외 핸들러를
등록하면서 ① **최후방 catch-all(`@api.exception_handler(Exception)`)을 빠뜨리거나**,
② 핸들러가 예외를 problem+json 으로 변환하지 않고 **되던지거나(`raise exc`/bare `raise`)**,
③ **`HttpError` problem 변환 핸들러(`@api.exception_handler(HttpError)`)를 빠뜨린**
정확한 형태만 차단한다(NJ-7 — 라이브에서 난 형태: ①은 Claude `api.py` 6핸들러에
Exception 최후방 부재 / ②는 Codex `order_api_router.py:117` permanent 시 `raise exc` /
③은 finallive-claude `config/api.py` 7핸들러[catch-all 포함]에 HttpError 부재 →
깨진 본문이 400 `application/json` `{"detail"}` 로 새 EP-1 problem+json 미달).

왜 차단하나: presentation 단일 변환점은 등록된 구체 핸들러로 *식별된* 예외만 덮는다.
최후방 `@api.exception_handler(Exception)` 가 없으면 식별 안 된 예외(프로그래밍 오류·
서드파티 예외)가 ninja 기본 traceback 핸들러로 가 본문에 스택을 노출한다(§6.2:368-371).
핸들러가 `raise` 로 되던지면 그 예외는 catch-all 로 안 가고 Django 로 전파돼 같은 누출이
난다(§6.2:477-479). **대안 B(`create_response` 오버라이드)는 면제가 아니다** — 그건
status 가 부여된 응답의 content-type 만 통일하고, 핸들러 없는 미식별 예외는 여전히
`create_response` 를 거치지 않고 Django 로 샌다(§6.2:479-480).

③의 근거: ninja 1.6.x 는 깨진 본문·파싱 실패를 `HttpError(400)` 으로 재포장해 raise
하고(`ninja/params/models.py` — 원본 `JSONDecodeError` 는 `__cause__` 로만 보존되며
핸들러 디스패치는 raised 타입의 MRO 만 본다), `Exception`·`HttpError` 의 **기본 핸들러를
선등록**하므로 사용자 catch-all(Exception)이 있어도 MRO 상 더 구체인 기본 HttpError
핸들러(`{"detail"}` plain body)가 먼저 잡는다 — **catch-all 은 HttpError 누수를 못
막는다**(§6.2:581-583). 임의 status `raise HttpError(...)`·auth 401/403(`AuthenticationError`
등 HttpError 서브클래스가 plain HttpError 흐름을 공유) 경로 때문에 요청 본문 없는 API 에도
적용된다(§6.3:663-667 — "대안 B 사용 여부와 무관하게 HttpError 핸들러가 필요"). 대안 B 는
기본 HttpError 응답의 content-type 만 바꾸고 body(`{"detail"}`)는 유지하므로 대체 불가
(§6.2:607-609). (RFC 9457 자체는 모든 멤버가 optional 이나, 표준 §6.2 problem 헬퍼의
카탈로그 body 형태가 프로젝트 계약 정본이라 ninja 기본 `{"detail"}` body 는 미달이다.)

분석 단위 = **NinjaAPI 인스턴스(데코 변수명)** — `@<var>.exception_handler(...)` 의
`<var>` 로 핸들러를 그룹핑한다. 핸들러가 여러 파일(`api.py`/`api_order.py`)로 분산돼도
같은 인스턴스면 합산하므로, "이 파일엔 catch-all 이 없다"는 분산-파일 거짓양성을 막는다.

등록 인정(거짓양성 방지 — 인정-전용 확장이라 차단 표면을 넓히지 않는다):
  - register call-form `<var>.add_exception_handler(Exception|HttpError, fn)` 도 등록으로
    인정한다(데코와 기능 동일한 ninja 공개 API). **충족 인정에만 쓰고 차단 트리거
    핸들러 수에는 산입하지 않는다**,
  - `from <어디든> import HttpError as Y` 별칭은 **출처-불문** 인정(re-export·rename 모두),
    `errors.HttpError` 류 Attribute 인자는 끝 이름으로 인정.

저-recall(일부러 안 잡음 — discipline-reviewer 의미 렌즈가 담당):
  - 핸들러 0개 + `create_response`-only(alt-B 단독) 미식별 누수,
  - 핸들러가 `return {}`/`return None` 등 비-problem 객체 반환(되던지기 아님),
  - 자작 동명 `HttpError` 클래스의 위장 등록(끝 이름 매치라 충족으로 오인 — 거짓음성 방향),
  - 동적 인자 등록(`getattr(errors, "HttpError")` 류 Call 인자) 미인식 — 부재로 오판할 수
    있으나 표준 레시피(plain import + 데코)에서 비실존(기존 조건과 동일 한계).
거짓 양성을 내면 정당한 분산 핸들러·도메인 타입 번역(`raise X(...) from exc`)·대안 B+
catch-all 공존을 막으므로, **데코 핸들러 ≥1 + (catch-all 부재 OR HttpError 핸들러 부재
OR 핸들러 되던지기) + 비테스트 + git-touched 의 AND** 로만 차단한다.

차단 조건(셋 중 하나라도; git-touched 한정 — (1)·(3)은 인스턴스 그룹, (2)는 파일별):
  (1) catch-all 부재 — 한 인스턴스(`<var>`)에 `@<var>.exception_handler(...)` 핸들러가
      1개 이상인데 `@<var>.exception_handler(Exception|BaseException)` 최후방이 없음.
  (2) 핸들러 되던지기 — 임의 핸들러 본문이 bare `raise` 또는 `raise <name>`(cause 없음·
      Call 아님)로 예외를 되던짐. `raise NewType(...)`(도메인 번역)·`raise ... from x`
      (원본 보존)는 정당이라 면제.
  (3) HttpError 핸들러 부재 — 한 인스턴스(`<var>`)에 데코 핸들러가 1개 이상인데
      `HttpError`(별칭·register call-form 포함) problem 변환 핸들러 등록이 없음.

사용법: check-catch-all-handler.py [TARGET_DIR]   (기본 TARGET_DIR=현재 디렉터리)
종료코드: 0=clean, 2=blocker(발견 출력), 1=사용 오류.
"""
from __future__ import annotations

import ast
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

from migration_scope import iter_non_migration_files, validate_migration_scope

SKIP_DIRS = {".venv", "venv", "site-packages", "node_modules", ".git", "__pycache__"}
TEST_DIR_NAMES = {"test", "tests"}

CATCH_ALL = {"Exception", "BaseException"}
HTTP_ERROR = "HttpError"


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


def _http_error_local_names(tree: ast.Module) -> set[str]:
    """이 모듈에서 `HttpError` 를 가리키는 로컬 이름 집합 — 별칭 거짓양성 방지(출처-불문).

    `from ninja.errors import HttpError as NinjaHttpError` → {"HttpError", "NinjaHttpError"}.
    re-export(`from common.errors import HttpError`)는 끝 이름이 그대로라 기본 집합이 덮는다."""
    names: set[str] = {HTTP_ERROR}
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.name == HTTP_ERROR and alias.asname:
                    names.add(alias.asname)
    return names


def _register_call_registrations(tree: ast.Module) -> list[tuple[str | None, str | None]]:
    """register call-form `<var>.add_exception_handler(<Exc>, fn)` 등록 — (var, exc 끝이름) 목록.

    데코와 기능 동일한 ninja 공개 API 라 **충족 인정에만** 쓴다(차단 트리거 핸들러 수에
    미산입 — 인정-전용이라 차단 표면을 넓히지 않는다)."""
    out: list[tuple[str | None, str | None]] = []
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "add_exception_handler"
            and node.args
        ):
            var = node.func.value.id if isinstance(node.func.value, ast.Name) else None
            out.append((var, _exc_name(node.args[0])))
    return out


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
    for path in iter_non_migration_files(root, name_pattern="*.py"):
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
    if not validate_migration_scope(root, "check-catch-all-handler"):
        return 1

    # NinjaAPI 인스턴스(변수)별로 핸들러를 합산 — 분산-파일 거짓양성 차단.
    groups: dict[str | None, dict] = defaultdict(
        lambda: {"has_catchall": False, "has_httperror": False, "handlers": [], "files": set()}
    )
    for prod_file in _find_production_files(root):
        try:
            tree = ast.parse(prod_file.read_text(encoding="utf-8", errors="replace"))
        except (OSError, SyntaxError):
            continue
        http_error_names = _http_error_local_names(tree)
        for var, exc in _register_call_registrations(tree):
            g = groups[var]
            g["files"].add(prod_file)
            if exc in CATCH_ALL:
                g["has_catchall"] = True
            if exc in http_error_names:
                g["has_httperror"] = True
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
            if exc in http_error_names:
                g["has_httperror"] = True
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
        # 조건 (3) HttpError problem 핸들러 부재.
        if not g["has_httperror"]:
            f0, ln0, _, _ = g["handlers"][0]
            findings.append(
                f"  - {f0.relative_to(root)}:{ln0} ({label}, 핸들러 {len(g['handlers'])}개): "
                f"`{label}(HttpError)` problem 변환 핸들러 부재 — 깨진 본문·파싱 실패·임의 status 를 "
                "ninja 가 `HttpError` 로 표면화하면 catch-all(Exception) 이 있어도 ninja 선등록 기본 "
                "HttpError 핸들러가 MRO 상 먼저 잡아 `{\"detail\"}`(application/json) 로 응답 — "
                "problem+json 단일변환점 우회(EP-1 형태)"
            )
        # 조건 (2) 핸들러 되던지기 — 파일-로컬 위반이라 *그 파일*이 이번에 touched 일 때만 본다
        # (catch-all·HttpError 부재는 인스턴스 속성이라 그룹 게이트를 쓰지만, 되던지기는 미변경
        # 커밋된 형제까지 차단하면 brownfield 존중 위반이므로 파일별로 좁힌다).
        for prod_file, _, name, reraise_ln in g["handlers"]:
            if reraise_ln is not None and _is_new_or_modified(root, prod_file):
                findings.append(
                    f"  - {prod_file.relative_to(root)}:{reraise_ln} {name}(): "
                    "핸들러가 예외를 `raise` 로 되던짐 — problem+json 단일변환점을 우회해 "
                    "Django 로 전파(`raise X(...) from exc` 로 번역·보존하거나 직접 problem 반환하라)"
                )

    if findings:
        print(
            "[check-catch-all-handler] BLOCKER — ninja 오류 변환의 완전성 위반"
            "(catch-all 부재·HttpError 핸들러 부재·핸들러 되던지기 — NJ-7):"
        )
        for f in findings:
            print(f)
        print(
            "  근거: implementation-django-ninja §6.2(368-371·469-485·527-535·607-609)·§6.3(663-667). "
            "식별 안 된 예외는 최후방 `@api.exception_handler(Exception)` 가 500 problem+json 으로 "
            "변환하고 스택은 `logger.exception` 으로만 남긴다(본문 노출 차단). 깨진 본문·임의 status 의 "
            "`HttpError` 는 `@api.exception_handler(HttpError)` 가 RFC9457 body 로 변환한다 — catch-all "
            "은 ninja 선등록 기본 HttpError 핸들러에 가로채여 이를 대체하지 못하고, 대안 B"
            "(`create_response`)도 기본 body(`{\"detail\"}`)를 못 바꾼다(B로 대체 불가). 핸들러는 "
            "problem 을 *반환*해야지 `raise` 로 되던지면 Django 로 누출된다. 설계로 반송하라."
        )
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
