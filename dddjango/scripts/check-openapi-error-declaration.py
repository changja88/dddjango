#!/usr/bin/env python3
"""dddjango NJ-4 결정적 백스톱 — 오류 status 를 openapi_extra 로 선언하고 response= 엔 누락.

`check-response-schema-bypass.py`(성공경로 schema 우회)의 형제다. presentation 의 ninja
operation 이 오류 status(4xx/5xx)를 데코레이터 `openapi_extra={"responses": {...}}` 로만
선언하고 `response={...}` 엔 안 넣은 정확한 형태(스모크에서 실제로 난 Codex 형태 —
`@router.post(..., response={201: Out}, openapi_extra={"responses": {"404": ...}})`)만 차단한다.
그러면 Swagger 문서엔 드러나지만 ninja 는 그 status 를 응답 타입으로 인지하지 못해(§2.2 line111)
검증·직렬화 계약 밖이 된다(문서 가시성 ≠ 타입 인지).

*왜 결정적 백스톱인가* — `openapi_extra` 로 선언하면 OpenAPI 문서엔 보이므로 "선언했다"는
착시가 생기고, 테스트도 green(성공 경로만 검사). discipline-reviewer 가 데코레이터 keyword 를
일일이 대조하지 않으면 샌다 — 이 스크립트가 그 형태를 결정적으로 잡는다(고정밀·저-recall,
거짓 양성 ≈0).

거짓 양성 회피 — AND 합성으로만 차단:
  1) `presentation_layer/` 프로덕션 .py(test 제외) + `from ninja…` import.
  2) operation 데코레이터의 `openapi_extra={"responses": {…}}` 에 4xx/5xx status 가 리터럴
     키로 있고, 같은 데코레이터 `response={…}` 엔 그 status 가 없다.
  3) (git 레포면) 신규/수정 파일.
  `openapi_extra` 가 security/examples 등 responses 아닌 용도거나, responses 에 2xx 만 있거나,
  그 status 가 이미 response= 에 이중선언이면 제외 → 거짓양성 0.

*저-recall 한계(정직)* — `responses` dict 가 변수/spread(`{**EXTRA}`·`responses=_ERR`)면 AST
가 리터럴이 아니라 못 본다(보수적 제외). `get_openapi_schema` 오버라이드로 사후 주입하는
우회도 미포착 — 둘 다 "문서엔 보이나 ninja 미인지" 동일 결함을 유지하나 의미 레인
(discipline-reviewer)이 담당한다. 이 스크립트는 *흔한 형태*를 결정적으로 막고 변종은 레그3
몫이다(②design-architect 생산자 예방 + ③discipline-reviewer 의미 체크와의 3레그 분담).

사용법: check-openapi-error-declaration.py [TARGET_DIR]   (기본 TARGET_DIR=현재 디렉터리)
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
NINJA_IMPORT_RE = re.compile(r"^\s*from\s+ninja(?:\.\w+)*\s+import\b", re.MULTILINE)


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


def _status_to_int(node: ast.expr) -> int | None:
    """ast 상수 키(`"400"` 또는 `400`)를 int status 로. 비-상수/비-숫자는 None."""
    if isinstance(node, ast.Constant):
        if isinstance(node.value, bool):
            return None
        if isinstance(node.value, int):
            return node.value
        if isinstance(node.value, str) and node.value.isdigit():
            return int(node.value)
    return None


def _response_statuses(func: ast.FunctionDef | ast.AsyncFunctionDef) -> set[int]:
    """데코레이터 `response={...}` 의 status 키 집합. dict 아니거나 없으면 빈 집합."""
    for dec in func.decorator_list:
        if not isinstance(dec, ast.Call):
            continue
        for kw in dec.keywords:
            if kw.arg != "response":
                continue
            if isinstance(kw.value, ast.Dict):
                out: set[int] = set()
                for k in kw.value.keys:
                    s = _status_to_int(k) if k is not None else None
                    if s is not None:
                        out.add(s)
                return out
            return set()  # response=Schema(단일 성공) → status 키 없음
    return set()


def _openapi_extra_error_statuses(func: ast.FunctionDef | ast.AsyncFunctionDef) -> set[int]:
    """데코레이터 `openapi_extra={"responses": {...}}` 의 4xx/5xx status 키(리터럴만)."""
    out: set[int] = set()
    for dec in func.decorator_list:
        if not isinstance(dec, ast.Call):
            continue
        for kw in dec.keywords:
            if kw.arg != "openapi_extra" or not isinstance(kw.value, ast.Dict):
                continue
            for k, v in zip(kw.value.keys, kw.value.values):
                if isinstance(k, ast.Constant) and k.value == "responses" and isinstance(v, ast.Dict):
                    for sk in v.keys:
                        s = _status_to_int(sk) if sk is not None else None
                        if s is not None and 400 <= s <= 599:
                            out.add(s)
    return out


def _scan_file(body: str) -> list[str]:
    """(openapi_extra 오류선언 ∧ response= 누락) operation 을 찾아 설명 리스트로."""
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
        extra_errors = _openapi_extra_error_statuses(node)
        if not extra_errors:
            continue
        missing = sorted(extra_errors - _response_statuses(node))
        if missing:
            out.append(f"operation '{node.name}' (오류 {missing} 가 openapi_extra 에만·response= 누락)")
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
        changed = subprocess.run(["git", "-C", str(root), "diff", "--quiet", "HEAD", "--", str(rel)])
        return changed.returncode != 0
    except (OSError, subprocess.SubprocessError):
        return True  # git 판단 불가 시 안전하게 가드 통과(나머지 AND 가 좁힌다).


def main(argv: list[str]) -> int:
    root = Path(argv[1]).resolve() if len(argv) > 1 else Path.cwd()
    if not root.is_dir():
        print(f"[check-openapi-error-declaration] 사용 오류: 디렉터리 아님 {root}", file=sys.stderr)
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
            "[check-openapi-error-declaration] BLOCKER — 오류 status 를 openapi_extra 로만 선언하고 "
            "response={...} 엔 누락함(ninja 가 타입으로 미인지 = 선언 계약 밖):"
        )
        for f in findings:
            print(f)
        print(
            "  근거: implementation-django-ninja §2.2 line111. 가능한 모든 status(404·409·422 등)를 "
            "response={...} 에 선언한다 — openapi_extra/get_openapi_schema 수동 선언은 Swagger 가시성만 "
            "달성하고 ninja 응답 타입엔 안 들어간다. 오류 schema 를 response= 로 옮겨라. 설계로 반송하라."
        )
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
