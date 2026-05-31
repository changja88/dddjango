#!/usr/bin/env python3
"""dddjango API 오류 중앙화 결정적 백스톱 (P1a).

좁은 **고정밀·저-recall** 게이트다. 4계층 DDD에서 코더가 **application 계층이
오류→HTTP status 매핑을 직접 수행**한 정확한 형태(P1a 라이브-파이어에서 실제로
난 Codex 형태 — application service 가 status code 를 골라 problem body 를 조립)만
차단한다. status 맵을 모듈 밖으로 추출하거나 변수로 우회하는 *의미적* 회피,
presentation operation 본문의 수제 응답은 **일부러 잡지 않는다** — 그건
② design-architect 생산자 예방(명세에 "오류→status = presentation 단일 소유")과
③ discipline-reviewer 의미 체크(operation 수제·부분 중앙화·우회)가 담당한다.
여기서 거짓 양성을 내면 정당한 도메인 outcome·성공 응답·plain Django/DRF·기존
코드를 막으므로, **경로·신호·diff 의 AND 합성으로만** 차단한다.

AND 조건(전부 참이어야 blocker):
  1) 파일 경로가 4계층 **application 계층**(`application_layer/`)이고 테스트가
     아님(`test/`·`tests/`·`test_*.py`·`conftest.py` 제외) — presentation·domain·
     infra 계층은 제외(operation 본문 수제는 ③ discipline-reviewer 몫).
  2) 그 파일이 HTTP 오류 응답을 **직접 생성/의존**: `JsonResponse(`/`HttpResponse(`
     호출, `status_code=4xx|5xx`/`status=4xx|5xx` 오류 status 대입, ninja
     `HttpError(4xx|5xx`, 또는 `from ninja…` import. application 은 HTTP 를 몰라야
     하므로(도메인 예외 raise·결과 반환만) 이 신호 자체가 책임 누수다
     (`implementation-django-ninja` §2.2·§6.2).
  3) (git 레포면) 그 파일이 이번 변경에서 새로 추가/수정됨 — 기존에 커밋된
     코드는 존중. git 아니면 이 가드는 건너뛴다.

사용법: check-error-centralization.py [TARGET_DIR]   (기본 TARGET_DIR=현재 디렉터리)
종료코드: 0=clean, 2=blocker(발견 출력), 1=사용 오류.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

SKIP_DIRS = {".venv", "venv", "site-packages", "node_modules", ".git", "__pycache__"}
TEST_DIR_NAMES = {"test", "tests"}

# application 계층이 HTTP 오류 응답을 직접 만드는 신호(전부 책임 누수).
# 호출은 paren 을 요구해 dead-import 를 배제하고, status 는 4xx/5xx 리터럴 대입만
# 봐서 외부 응답의 status 읽기·성공 status(2xx)·도메인 enum 을 배제한다.
RESPONSE_CALL_RE = re.compile(
    r"\b(?:JsonResponse|HttpResponse|HttpResponseBadRequest|HttpResponseForbidden"
    r"|HttpResponseNotFound|HttpResponseNotAllowed|HttpResponseServerError)\s*\("
)
ERROR_STATUS_RE = re.compile(r"\bstatus(?:_code)?\s*=\s*[45]\d\d\b")
HTTP_ERROR_RE = re.compile(r"\bHttpError\s*\(\s*[45]\d\d\b")
NINJA_IMPORT_RE = re.compile(r"^\s*from\s+ninja(?:\.\w+)*\s+import\b", re.MULTILINE)

SIGNAL_CHECKS = (
    (RESPONSE_CALL_RE, "수제 HTTP 응답 객체 생성(JsonResponse/HttpResponse)"),
    (ERROR_STATUS_RE, "오류 status code 직접 선택(status[_code]=4xx/5xx)"),
    (HTTP_ERROR_RE, "ninja HttpError 를 status 와 함께 raise"),
    (NINJA_IMPORT_RE, "ninja(web 프레임워크) import — application 은 web 을 모른다"),
)


def _find_application_layer_files(root: Path) -> list[Path]:
    """4계층 application 계층의 프로덕션 .py 후보(venv·테스트 제외)."""
    out: list[Path] = []
    for path in root.rglob("*.py"):
        parts = set(path.parts)
        if parts & SKIP_DIRS:
            continue
        if "application_layer" not in parts:
            continue
        # application 계층 안의 테스트는 프로덕션 누수가 아니다 → 제외.
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
        # 추적되지 않으면(신규) error-unmatch 가 non-zero → 신규로 간주.
        tracked = subprocess.run(
            ["git", "-C", str(root), "ls-files", "--error-unmatch", str(rel)],
            capture_output=True,
        )
        if tracked.returncode != 0:
            return True  # 신규 파일.
        # 추적 중이면 HEAD 대비 변경됐는지.
        changed = subprocess.run(
            ["git", "-C", str(root), "diff", "--quiet", "HEAD", "--", str(rel)],
        )
        return changed.returncode != 0
    except (OSError, subprocess.SubprocessError):
        return True  # git 판단 불가 시 안전하게 가드 통과(나머지 AND 가 좁힌다).


def main(argv: list[str]) -> int:
    root = Path(argv[1]).resolve() if len(argv) > 1 else Path.cwd()
    if not root.is_dir():
        print(f"[check-error-centralization] 사용 오류: 디렉터리 아님 {root}", file=sys.stderr)
        return 1

    findings: list[str] = []
    for app_file in _find_application_layer_files(root):
        try:
            body = app_file.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        signals = [label for rx, label in SIGNAL_CHECKS if rx.search(body)]
        if not signals:
            continue
        # 조건 3: 이번 변경에서 추가/수정.
        if not _is_new_or_modified(root, app_file):
            continue
        findings.append(f"  - {app_file.relative_to(root)}: {'; '.join(signals)}")

    if findings:
        print(
            "[check-error-centralization] BLOCKER — application 계층이 오류→HTTP "
            "status 변환을 직접 수행함(presentation 경계 밖 = API 오류 중앙화·책임 배치 위반):"
        )
        for f in findings:
            print(f)
        print(
            "  근거: implementation-django-ninja §2.2·§6.2. 오류→HTTP status 매핑은 "
            "presentation 의 단일 소유자(@api.exception_handler + problem 헬퍼, 또는 "
            "create_response 오버라이드)가 갖는다 — application/domain 은 도메인 예외를 raise "
            "하거나 결과(outcome/Result)를 반환하고 HTTP 를 모른다. 설계로 반송하라."
        )
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
