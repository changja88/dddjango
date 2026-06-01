#!/usr/bin/env python3
"""dddjango 4계층 골격 결정적 백스톱 (구조 — houserules §0-2 집행).

기존 백스톱(mechanism-ownership·error-centralization·response-schema-bypass)이
*행위/계약*을 보는 데 비해, 이건 **구조**를 본다. 표준 레이아웃(`application/<bc>/`)을
적용한 프로젝트에서 각 바운디드 컨텍스트(BC)는 4계층 폴더(`domain_layer`·
`application_layer`·`infra_layer`·`presentation_layer`)를 **내용이 없어도 빈
패키지(`__init__.py`)로라도 모두** 가져야 한다(houserules §0-2). 두 위반 형태를 차단한다:
  - **부분 평면**: 일부 계층만 있고 하나를 생략(스모크 SH-2 — HTTP 없이 ACL·
    published_service 로만 소비되는 내부 전용 BC 가 `presentation_layer` 를 생략).
  - **완전 평면**: Django 앱 산출물은 있는데 4계층으로 전혀 분리 안 함(`application/<bc>/`
    루트에 `models.py`·`views.py` 등을 직접 둔 startapp 직후 평면 상태).

*왜 결정적 백스톱인가* — 빈 계층 폴더엔 테스트가 걸리지 않아 TDD Red 로 안 잡힌다(coder 가
누락해도 `manage.py test` 는 Green). discipline-reviewer 의미 게이트 한 점에만 의존하면
LLM 이 프로즈 규칙을 회피하는 표면이 된다 — 이 스크립트가 그 절반을 결정적으로 메운다
(고정밀·저-recall, 거짓 양성 ≈0).

거짓 양성 회피 — AND 합성으로만 차단:
  1) 프로젝트가 *표준 레이아웃*을 쓴다 = 레포에 `application/` 컨테이너 디렉터리가 있다.
     없으면 기존 확립 규약(§1.1)이라 이 불변식은 적용 대상이 아니다 → exit 0.
  2) `application/<bc>/` 가 *4계층을 따라야 할 앱* 이다 — 둘 중 하나:
       (a) 4계층 폴더 중 하나라도 이미 디렉터리로 존재(자신을 4계층 앱으로 선언), 또는
       (b) Django 앱 산출물(`models.py`·`apps.py`·`views.py`·`admin.py`·`migrations/`)을
           BC 루트에 직접 가진 *완전 평면* 앱(계층 0개).
     둘 다 아닌 디렉터리(계층도 Django 산출물도 없는 컨테이너 잡동사니·비-앱 패키지)는
     건너뛴다 → 거짓 양성 0.
  3) (git 레포면) 그 BC 하위에 이번 변경에서 새로 추가/수정/미추적된 파일이 있다 = 이번
     작업이 건드린 BC. 기존에 커밋된 채 안 건드린 BC 는 존중(brownfield) → 건너뜀.
  위 셋이 참인 BC 에서: (b)면 4계층 전부 미분리 = blocker, (a)면 4계층 중 하나라도 (폴더가
  없거나 / 폴더는 있으나 `__init__.py` 가 없어 git 에 존속 안 되면) blocker. 계층 폴더가
  빈 패키지로라도 4개 다 있으면 통과 — 계층 *내부* 깊이(presentation 의 `api/`·`schema/`
  등 종류 2차 폴더)는 검사하지 않는다(§0-4상 표현 종류 폴더는 표현 내용이 생길 때 생성 —
  깊이·내용 적정성은 discipline-reviewer 의미 체크 몫).

사용법: check-layer-skeleton.py [TARGET_DIR]   (기본 TARGET_DIR=현재 디렉터리)
종료코드: 0=clean(또는 표준 레이아웃 미적용), 2=blocker(발견 출력), 1=사용 오류.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SKIP_DIRS = {".venv", "venv", "site-packages", "node_modules", ".git", "__pycache__"}

# 4계층 — houserules §0-2. 순서 고정(보고 가독성).
LAYER_DIRS = ("domain_layer", "application_layer", "infra_layer", "presentation_layer")

# "이 디렉터리는 4계층을 따라야 할 Django 앱이다"의 강한 신호(BC 루트에 직접 존재 시).
# 정상 4계층 앱은 이들을 `infra_layer/django_<app>/`에 두므로 루트엔 없다 — 루트에 있으면
# startapp 직후 평면 상태(완전 평면)다. 잡동사니 util 패키지엔 이들이 없어 거짓 양성 0.
DJANGO_APP_MARKERS = ("models.py", "apps.py", "views.py", "admin.py")


def _find_application_containers(root: Path) -> list[Path]:
    """표준 앱 컨테이너(`application/`) 디렉터리들. 계층 `application_layer` 와 이름이
    달라 자연히 구분된다."""
    out: list[Path] = []
    for path in root.rglob("application"):
        if not path.is_dir():
            continue
        if set(path.parts) & SKIP_DIRS:
            continue
        out.append(path)
    return out


def _find_bc_dirs(root: Path) -> list[Path]:
    """각 `application/` 컨테이너의 직속 하위 디렉터리(= BC 후보)."""
    out: list[Path] = []
    for container in _find_application_containers(root):
        for child in sorted(container.iterdir()):
            if not child.is_dir():
                continue
            if child.name in SKIP_DIRS:
                continue
            out.append(child)
    return out


def _has_any_layer(bc_dir: Path) -> bool:
    """4계층 폴더 중 하나라도 디렉터리로 존재 = 자신을 4계층 앱으로 선언한 것."""
    return any((bc_dir / layer).is_dir() for layer in LAYER_DIRS)


def _has_django_app_marker(bc_dir: Path) -> bool:
    """BC 루트에 Django 앱 산출물이 직접 있는가(완전 평면 앱의 신호)."""
    if any((bc_dir / marker).is_file() for marker in DJANGO_APP_MARKERS):
        return True
    return (bc_dir / "migrations").is_dir()


def _is_bc_to_check(bc_dir: Path) -> bool:
    """4계층을 따라야 할 앱: 계층을 하나라도 가졌거나(부분), Django 산출물 평면(완전)."""
    return _has_any_layer(bc_dir) or _has_django_app_marker(bc_dir)


def _layer_issues(bc_dir: Path) -> list[str]:
    """누락/비-패키지 계층을 사람이 읽을 설명 리스트로."""
    if not _has_any_layer(bc_dir):
        # 완전 평면 — 계층이 0개인데 Django 앱 산출물 보유.
        return ["4계층 전부 없음(완전 평면 앱 — `_layer` 분리 안 됨)"]
    issues: list[str] = []
    for layer in LAYER_DIRS:
        d = bc_dir / layer
        if not d.is_dir():
            issues.append(f"{layer}/ 폴더 없음")
        elif not (d / "__init__.py").exists():
            issues.append(f"{layer}/ 에 __init__.py 없음(git 미추적·골격 소실)")
    return issues


def _is_new_or_modified(root: Path, bc_dir: Path) -> bool:
    """git 레포면 이 BC 하위에 이번 변경(신규/수정/미추적)이 있는지. git 아니면 True."""
    if not (root / ".git").exists():
        return True
    try:
        rel = bc_dir.relative_to(root)
    except ValueError:
        return True
    try:
        res = subprocess.run(
            ["git", "-C", str(root), "status", "--porcelain", "--", str(rel)],
            capture_output=True,
            text=True,
        )
        if res.returncode != 0:
            return True  # git 판단 불가 → 안전하게 가드 통과(나머지 AND 가 좁힌다).
        return bool(res.stdout.strip())
    except (OSError, subprocess.SubprocessError):
        return True


def main(argv: list[str]) -> int:
    root = Path(argv[1]).resolve() if len(argv) > 1 else Path.cwd()
    if not root.is_dir():
        print(f"[check-layer-skeleton] 사용 오류: 디렉터리 아님 {root}", file=sys.stderr)
        return 1

    if not _find_application_containers(root):
        return 0  # 표준 레이아웃(`application/`) 미적용 → 해당 없음.

    findings: list[str] = []
    for bc in _find_bc_dirs(root):
        if not _is_bc_to_check(bc):
            continue
        if not _is_new_or_modified(root, bc):
            continue
        issues = _layer_issues(bc)
        if issues:
            findings.append(f"  - {bc.relative_to(root)}: {'; '.join(issues)}")

    if findings:
        print(
            "[check-layer-skeleton] BLOCKER — 4계층 BC 가 계층 폴더를 생략했다"
            "(houserules §0-2: 내용이 없어도 빈 패키지로라도 4계층 전부 생성):"
        )
        for f in findings:
            print(f)
        print(
            "  근거: discipline-houserules §0-2. 표현/도메인 관심사가 없다는 판단으로 "
            "계층 폴더 자체를 생략하지 않는다 — 빈 `presentation_layer` 라도 `__init__.py` 만 "
            "둔 빈 패키지로 만든다(예: ACL·published_service 로만 소비되는 내부 전용 BC). "
            "완전 평면 앱은 4계층으로 분리하라. 접을 실질 사유가 있으면 코드에서 생략하지 말고 "
            "설계(G1 트레이드오프)로 반송하라."
        )
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
