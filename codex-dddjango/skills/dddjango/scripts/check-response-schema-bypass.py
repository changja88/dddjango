#!/usr/bin/env python3
"""dddjango API 성공 응답 schema 우회 결정적 백스톱 (G3).

`check-error-centralization.py`(P1a 오류경로)의 **성공경로 거울**이다. 좁은
**고정밀·저-recall** 게이트로, presentation 의 ninja operation 이 데코레이터에
**2xx 성공 schema 를 선언(`response=...`)해 놓고 그 operation 본문에서 수제 raw
`JsonResponse`/`HttpResponse`(2xx)로 응답을 직조립**해 선언 계약을 우회한 정확한
형태(스모크에서 실제로 난 Codex 형태 — `@router.post(..., response={201: OrderOut})`
인데 본문이 `return JsonResponse({...}, status=201)`)만 차단한다. 그러면 OpenAPI 가
광고하는 schema 와 실제 응답 본문이 드리프트한다(선언 contract ≠ 실본문).

여기서 거짓 양성을 내면 정당한 코드를 막으므로 **AND 합성으로만** 차단한다.
operation 이 `response=` 를 *선언하지 않은* 경우(우회할 선언 계약이 없음·NJ-4 몫),
중앙 `@api.exception_handler`·`create_response`·`problem()` 헬퍼의 응답 조립(presentation
단일 소유자라 정당), download·stream·redirect·`204 No Content` 같은 *선언 schema 없는*
성공, plain Django/DRF 코드는 **일부러 잡지 않는다** — 그건 ② design-architect 생산자
예방(명세에 "성공 직렬화 = presentation 단일 소유")과 ③ discipline-reviewer 의미
체크(helper 경유 우회·부분 드리프트)가 담당한다.

AND 조건(전부 참이어야 blocker):
  1) 파일 경로가 4계층 **presentation 계층**(`presentation_layer/`)이고 테스트가
     아님(`test/`·`tests/`·`test_*.py`·`conftest.py` 제외)이며 파일이 ninja 를
     import(`from ninja…`) — plain Django view·DRF 는 제외.
  2) 그 파일에 **`response=` 를 선언한 데코레이터를 가진 operation 함수**가 있고,
     그 함수 본문이 수제 raw 성공 응답을 조립 — `JsonResponse(...)` 또는
     `HttpResponse(...)` 호출의 `status` 가 2xx(200·201·202·203) 또는 생략(기본
     200)이다. 204/3xx/4xx/5xx·`FileResponse`·`StreamingHttpResponse`·redirect 는
     제외(선언 schema 없는 정당한 성공). operation 은 선언한 schema 객체/튜플을
     return 해야 하므로(`implementation-django-ninja` §2.2·§6.2) 이 직조립이 우회다.
  3) (git 레포면) 그 파일이 이번 변경에서 새로 추가/수정됨 — 기존에 커밋된 코드는
     존중. git 아니면 이 가드는 건너뛴다.

사용법: check-response-schema-bypass.py [TARGET_DIR]   (기본 TARGET_DIR=현재 디렉터리)
종료코드: 0=clean, 2=blocker(발견 출력), 1=사용 오류.
"""
from __future__ import annotations

import ast
import re
import subprocess
import sys
from pathlib import Path

SKIP_DIRS = {".venv", "venv", "site-packages", "node_modules", ".git", "__pycache__"}
TEST_DIR_NAMES = {"test", "tests"}

NINJA_IMPORT_RE = re.compile(
    r"^\s*(?:from\s+ninja(?:_extra)?(?:\.\w+)*\s+import|import\s+ninja(?:_extra)?)\b",
    re.MULTILINE,
)

# 선언 schema 를 우회하는 *본문 있는* 성공 응답 클래스. FileResponse·
# StreamingHttpResponse·HttpResponseRedirect 등은 이름이 달라 자연히 제외된다.
RAW_RESPONSE_NAMES = {"JsonResponse", "HttpResponse"}
# schema-bearing 성공(본문 동반). 204(No Content)·205·206·3xx 는 제외.
SUCCESS_BODY_STATUSES = {200, 201, 202, 203}


def _find_presentation_layer_files(root: Path) -> list[Path]:
    """4계층 presentation 계층의 프로덕션 .py 후보(venv·테스트 제외)."""
    out: list[Path] = []
    for path in root.rglob("*.py"):
        parts = set(path.parts)
        if parts & SKIP_DIRS:
            continue
        if "presentation_layer" not in parts:
            continue
        if parts & TEST_DIR_NAMES or path.name.startswith("test_") or path.name == "conftest.py":
            continue
        out.append(path)
    return out


def _decorator_declares_response(func: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """operation 데코레이터(`@router.post(..., response=...)`)가 응답 schema 를 선언했나."""
    for dec in func.decorator_list:
        if isinstance(dec, ast.Call) and any(kw.arg == "response" for kw in dec.keywords):
            return True
    return False


def _call_name(node: ast.Call) -> str | None:
    """호출 대상 이름(`JsonResponse` 또는 `django.http.JsonResponse`의 끝 attr)."""
    func = node.func
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return None


def _success_body_status(node: ast.Call) -> int | None:
    """raw 응답 호출이 schema-bearing 성공(2xx 본문)이면 그 status, 아니면 None."""
    for kw in node.keywords:
        if kw.arg == "status":
            if isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, int):
                return kw.value.value if kw.value.value in SUCCESS_BODY_STATUSES else None
            # status 가 변수·표현식이면 성공/오류 판별 불가 → 보수적으로 제외(③ 몫).
            return None
    # status 생략 → 기본 200(성공 본문).
    return 200


def _bypass_lines_in_operation(func: ast.FunctionDef | ast.AsyncFunctionDef) -> list[int]:
    """operation 본문에서 수제 2xx raw 응답을 조립한 줄번호들."""
    lines: list[int] = []
    for node in ast.walk(func):
        if not isinstance(node, ast.Call):
            continue
        name = _call_name(node)
        if name not in RAW_RESPONSE_NAMES:
            continue
        if _success_body_status(node) is not None:
            lines.append(node.lineno)
    return lines


def _scan_file(body: str) -> list[str]:
    """파일에서 (response= 선언 operation × 수제 2xx 응답) 위반을 찾아 설명 리스트로."""
    if not NINJA_IMPORT_RE.search(body):
        return []
    try:
        tree = ast.parse(body)
    except SyntaxError:
        return []  # 파싱 불가 파일은 안전하게 건너뜀(저-recall 허용).
    out: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if not _decorator_declares_response(node):
            continue
        for lineno in _bypass_lines_in_operation(node):
            out.append(f"operation '{node.name}' (:{lineno} 수제 2xx 응답)")
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
        print(f"[check-response-schema-bypass] 사용 오류: 디렉터리 아님 {root}", file=sys.stderr)
        return 1

    findings: list[str] = []
    for pres_file in _find_presentation_layer_files(root):
        try:
            body = pres_file.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        hits = _scan_file(body)
        if not hits:
            continue
        if not _is_new_or_modified(root, pres_file):
            continue
        findings.append(f"  - {pres_file.relative_to(root)}: {'; '.join(hits)}")

    if findings:
        print(
            "[check-response-schema-bypass] BLOCKER — presentation operation 이 선언한 "
            "2xx 성공 schema 를 수제 raw HttpResponse/JsonResponse 로 우회함(선언 contract ≠ 실본문):"
        )
        for f in findings:
            print(f)
        print(
            "  근거: implementation-django-ninja §2.2·§6.2. operation 은 선언한 2xx "
            "`response` schema 를 schema 객체/튜플로 return 한다 — 수제 HttpResponse/"
            "JsonResponse 로 본문을 직조립하면 OpenAPI 광고 schema 와 실응답이 드리프트한다. "
            "download·stream·redirect 등 선언 schema 없는 성공은 예외다. 설계로 반송하라."
        )
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
