#!/usr/bin/env python3
"""dddjango 컴포지션 루트(DI 배선) 위치 결정적 백스톱 (discipline-houserules §0 집행).

표준 트리에서 DI 조립(컴포지션 루트)은 BC 루트의 *단일 파일* `application/<app>/composition_root.py`가
소유한다(houserules §0 트리·파일표; `implementation-django-ninja` "컴포지션 루트" 절). presentation은
그 `build_<usecase>_command()` 팩토리를 매요청 호출만 하고, operation 본문에서
`Django…Repository()`/`…Adapter()`를 직접 생성하지 않는다(Q-7). 이 백스톱은 배선이 그 단일 파일을
벗어나거나 부재인 *구조적* 변종 셋을 차단한다:
  - **off-tree `composition/` 폴더(V1)**: `application/<app>/composition/`에 배선 코드(provider 등)를
    폴더로 둠 = 정본 트리에 없는 노드(루트가 폴더로 분열). 라이브 관측 변종(Codex `composition/
    place_order_provider.py`).
  - **`composition_root.py` 오배치(V2)**: `composition_root.py`가 BC 루트가 아니라 계층/하위 폴더
    (`presentation_layer/`·`infra_layer/` 등)에 묻힘 = 위치 위반(BC 루트 소유여야).
  - **정본 부재(V3)**: application 로직(command/query/service 등)을 가진 BC인데 BC 루트
    `composition_root.py`가 *아예 없음* = 배선이 `di/`·`wiring/`·라우터·config 등으로 흩어졌거나
    미생성(긍정 의무 미이행). 정본 파일의 존재를 무조건이 아니라 *application 로직이 있을 때* 요구해
    데이터소스 BC(빈 `application_layer`)는 면제한다.

*왜 결정적 백스톱인가* — 배선 위치는 코더 구현 결정이고 테스트가 안 걸려 TDD Red로 안 잡힌다.
discipline-reviewer 의미 게이트 한 점에만 의존하면 off-tree 폴더가 'Q-7 준수(어댑터를 operation
밖으로 뺌)'로 *칭찬*받아 통과할 수 있다 — 이 스크립트가 그 구조 절반을 결정적으로 메운다
(고정밀·저-recall, 거짓 양성 ≈0). `config/api.py` 내장·`<app>_api_router.py` 접힘 같은 *in-tree
파일 내장* 변종은 그 파일이 적법히 존재해 형태로 못 가르므로 discipline-reviewer 의미 레인 몫이다.

거짓 양성 회피 — AND 합성으로만 차단:
  1) 프로젝트가 *표준 레이아웃*을 쓴다 = 레포에 `application/` 컨테이너가 있다. 없으면 기존
     확립 규약(§1.1)이라 적용 대상이 아니다 → exit 0.
  2) `application/<bc>/`가 *4계층 앱*이다(계층 폴더 하나라도 보유) — 비-앱 잡동사니 패키지 제외.
  3) (git 레포면) 그 BC 하위에 이번 변경(신규/수정/미추적)이 있다 = 이번 작업이 건드린 BC.
     기존 커밋된 채 안 건드린 BC는 존중(brownfield) → 건너뜀.
  위 셋이 참인 BC에서:
    - BC 루트 직속 `composition/`(`<bc>/composition/`)가 비-`__init__` `.py`를 담으면 blocker
      (off-tree 폴더·V1). 빈 패키지·test 경로는 면제. 도메인 애그리거트 `domain_layer/composition/`은
      BC 루트 직속이 아니라 애초에 대상이 아니다(거짓 양성 0).
    - `composition_root.py`가 BC 루트(`<bc>/composition_root.py`)가 아닌 계층/하위 폴더에 있으면
      blocker(오배치·V2). test 경로·`composition/` 안의 것(위 V1이 이미 잡음)은 면제. BC 루트의 것은 정상.
    - `application_layer`에 실 application 로직(비-`__init__` `.py`; `dto/`·test 제외)이 있는데 BC 루트
      `composition_root.py`가 없으면 blocker(부재·V3). command/query 만이 아니라 `service/`·`handler/`
      등 application_layer 실 로직 전체가 신호다(빈 `command/` 만 남기고 `service/` 로 fold 하는 우회
      봉쇄). 데이터소스 BC(§632 상 `application_layer` 가 빈 계층)는 로직이 없어 면제(거짓 양성 0).
      정본이 존재하되 *비어 있고 실배선이 딴 곳에* fold 된 알리바이는 형태로 못 가르므로
      discipline-reviewer 의미 레인 몫이다(이 V3는 *부재*만 결정적으로 잡는다).

사용법: check-composition-root.py [TARGET_DIR]   (기본 TARGET_DIR=현재 디렉터리)
종료코드: 0=clean(또는 표준 레이아웃 미적용), 2=blocker(발견 출력), 1=사용 오류.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SKIP_DIRS = {".venv", "venv", "site-packages", "node_modules", ".git", "__pycache__"}

# 4계층 — houserules §0-2. "이 BC가 4계층 앱인가"의 신호(하나라도 폴더면 검사 대상).
LAYER_DIRS = ("domain_layer", "application_layer", "infra_layer", "presentation_layer")

TEST_DIR_NAMES = {"test", "tests"}

# 정본 배선 노드 — BC 루트의 단일 파일. 폴더 변종(아래)은 off-tree.
COMPOSITION_FILE = "composition_root.py"
COMPOSITION_DIR = "composition"


def _find_application_containers(root: Path) -> list[Path]:
    """표준 앱 컨테이너(`application/`) 디렉터리들."""
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
            if not child.is_dir() or child.name in SKIP_DIRS:
                continue
            out.append(child)
    return out


def _has_any_layer(bc_dir: Path) -> bool:
    """4계층 폴더 중 하나라도 있으면 4계층 앱(이 백스톱 검사 대상)."""
    return any((bc_dir / layer).is_dir() for layer in LAYER_DIRS)


def _has_real_py(d: Path) -> bool:
    """디렉터리가 비-`__init__.py` `.py`를 (재귀로) 담는가 — 빈 골격 패키지 제외."""
    for p in d.rglob("*.py"):
        if set(p.relative_to(d).parts) & SKIP_DIRS:
            continue
        if p.name != "__init__.py":
            return True
    return False


def _needs_composition_root(bc_dir: Path) -> bool:
    """이 BC가 컴포지션 루트를 필요로 하는가 — `application_layer`에 *실 application 로직*
    (비-`__init__` `.py`)이 있으면 True. command/query 유스케이스뿐 아니라 `service/`·`handler/`
    오케스트레이션 등 application_layer 의 어떤 실 로직이라도 배선(구체 infra 주입)을 요구하므로
    신호로 본다 — 빈 `command/` 만 남기고 `service/` 로 로직을 fold 하는 우회를 봉쇄한다.
    `dto/`(입력 데이터 형태일 뿐 배선 대상 아님)·test 경로·SKIP_DIRS 는 제외.

    데이터소스 BC 는 `architecture-ddd` §632 상 `application_layer` 가 *빈 계층*(feature 0개·
    `__init__.py` 만)이라 실 로직이 없어 False → 면제(거짓 양성 0)."""
    app_layer = bc_dir / "application_layer"
    if not app_layer.is_dir():
        return False
    for p in app_layer.rglob("*.py"):
        if p.name == "__init__.py":
            continue
        rel_parts = set(p.relative_to(app_layer).parts)
        if rel_parts & SKIP_DIRS or rel_parts & TEST_DIR_NAMES:
            continue
        if "dto" in rel_parts:
            continue  # dto = 입력 데이터 형태, 배선 대상 아님.
        return True
    return False


def _composition_issues(bc_dir: Path) -> list[str]:
    """BC의 컴포지션 루트 구조 위반(off-tree 폴더·오배치 파일)을 설명 리스트로."""
    issues: list[str] = []

    # V1 — off-tree `composition/` 폴더 (BC 루트 직속, 실코드 보유).
    comp_dir = bc_dir / COMPOSITION_DIR
    if comp_dir.is_dir() and _has_real_py(comp_dir):
        payload = sorted(
            p.name
            for p in comp_dir.rglob("*.py")
            if p.name != "__init__.py"
            and not set(p.relative_to(comp_dir).parts) & SKIP_DIRS
        )
        issues.append(
            f"{COMPOSITION_DIR}/ 폴더에 배선 코드({', '.join(payload[:3])}) — DI 조립은 "
            f"BC 루트 단일 파일 `{COMPOSITION_FILE}`가 소유(폴더로 분열 금지)"
        )

    # V2 — `composition_root.py` 오배치 (BC 루트가 아닌 계층/하위 폴더).
    for f in bc_dir.rglob(COMPOSITION_FILE):
        rel_parts = f.relative_to(bc_dir).parts
        rel_set = set(rel_parts)
        if rel_set & SKIP_DIRS or rel_set & TEST_DIR_NAMES:
            continue
        if COMPOSITION_DIR in rel_set:
            continue  # `composition/` 안의 것은 V1이 이미 잡음(이중 보고 회피).
        if f.parent != bc_dir:
            issues.append(
                f"{f.relative_to(bc_dir).as_posix()} — `{COMPOSITION_FILE}`는 BC 루트"
                f"(`<app>/{COMPOSITION_FILE}`)가 소유, 계층/하위 폴더에 두지 않는다"
            )
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
        print(f"[check-composition-root] 사용 오류: 디렉터리 아님 {root}", file=sys.stderr)
        return 1

    if not _find_application_containers(root):
        return 0  # 표준 레이아웃(`application/`) 미적용 → 해당 없음.

    findings: list[str] = []
    for bc in _find_bc_dirs(root):
        if not _has_any_layer(bc):
            continue
        if not _is_new_or_modified(root, bc):
            continue
        issues = _composition_issues(bc)  # V1(off-tree 폴더)·V2(오배치).
        # V3 — application 로직이 있는데 정본 파일이 *부재*. command/query 만이 아니라 service/handler
        # 등 application_layer 실 로직 전체를 신호로 본다(빈 command/ 만 남기고 service 로 fold 하는 우회
        # 봉쇄). 데이터소스 BC(빈 application_layer)는 _needs_composition_root=False 로 면제.
        if _needs_composition_root(bc) and not (bc / COMPOSITION_FILE).is_file():
            issues.insert(
                0,
                f"`{COMPOSITION_FILE}` 부재 — application 로직(command/query/service 등)을 가진 BC는 "
                f"DI 조립을 BC 루트 단일 파일 `{COMPOSITION_FILE}`가 소유한다(배선을 `di/`·`wiring/`·"
                f"라우터·config 에 두지 말고 정본 파일을 만들어 `build_<usecase>_command()` 팩토리를 둬라)",
            )
        for issue in issues:
            findings.append(f"  - {bc.relative_to(root)}: {issue}")

    if findings:
        print(
            "[check-composition-root] BLOCKER — DI 조립(컴포지션 루트)이 BC 루트 단일 파일 "
            "`composition_root.py`를 벗어났거나 부재다(off-tree `composition/` 폴더·오배치·부재):"
        )
        for f in findings:
            print(f)
        print(
            "  근거: discipline-houserules §0(트리·파일표). DI 조립은 BC 루트 "
            "`application/<app>/composition_root.py` 단일 파일이 소유하고, presentation은 "
            "`build_<usecase>_command()` 팩토리를 매요청 호출만 한다 — feature별 `composition/` "
            "폴더로 쪼개(루트 분열)거나 계층 하위에 묻지 않는다(operation 본문에서 "
            "`Django…Repository()`/`…Adapter()`를 직접 생성하지 않는 Q-7의 짝). `composition/` "
            "폴더의 provider들을 BC 루트 `composition_root.py` 한 파일로 합치거나, 묻힌 "
            "`composition_root.py`를 BC 루트로 올려라. application 로직(command/query/service 등)을 "
            "가졌는데 정본이 아예 없으면(부재) BC 루트에 `composition_root.py`를 만들어 "
            "`build_<usecase>_command()` 팩토리를 둬라(데이터소스 BC는 해당 없음)."
        )
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
