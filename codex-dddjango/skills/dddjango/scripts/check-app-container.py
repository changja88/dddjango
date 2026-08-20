#!/usr/bin/env python3
"""dddjango 앱 컨테이너 위치 결정적 백스톱 (discipline-houserules §0-1 집행).

`check-layer-skeleton`(§0-2)이 *`application/` 안* BC 의 4계층 깊이를 보는 데 비해, 이건
*`application/` 밖*(루트·`src/` 등)에 방치된 Django 앱을 적출한다 — houserules §0-1
"앱은 루트 평면이 아니라 `application/<app>/` 아래에 둔다". 회귀(smoke4·smoke6: 기존
`catalog/` 가 루트 평면 + 새 마이그레이션/판정 적재인데 `application/` 로 이주 안 함)를 막는다.

*왜 결정적 백스톱인가* — 이주 여부는 architect 설계 단계 결정이고(`design-architect` 판정
소유→구조 배치), 루트 평면 앱은 빈 폴더가 아니라 *작동하는 앱* 이라 4계층 골격 백스톱
(`check-layer-skeleton`)에도 안 걸린다. `architecture-ddd` §3.2 «판정 소유→구조 이주» 항-(2) 2026-06-08 개정 — 데이터소스 면제는
*판정 실내용(.py)* 에 한정하고 위치·4계층·애그리거트 골격은 무조건이다; 이 스크립트는 그중
*위치* 한 축만 본다(위치는 항상 §0-1). 이 좁은 결정적 그물이 "위치" 한 축을 모델 무관하게
집행한다 — 판정-소유 형태(빈혈) 같은 *의미* 변종은 범위 밖(discipline-reviewer 몫).

거짓양성 ≈ 0 — AND 합성으로만 차단(check-layer-skeleton 철학 계승):
  G1) 레포 루트 직속 `application/` 존재 = 표준 채택. (`rglob` 아님 — 테스트 미러 트리의
      중첩 `application` 이나 가짜 `vendor/application/` 오인 차단.) 없으면 exit 0
      (§1.1 기존 확립 규약 존중 — 전체 평면·비표준 프로젝트는 이 불변식 대상 아님).
  후보 D = `application/` 밖 디렉터리 중 다음을 *모두* 만족:
      - `__init__.py` 보유 (PEP 420 namespace·빌드 산출물·잡동사니 배제)
      - Django 앱 마커: `apps.py` | `models.py` | `models/`(디렉터리) | `migrations/`(디렉터리)
      - 프로젝트 설정 패키지 아님 (`settings.py`, 또는 `urls.py`+(`wsgi.py`|`asgi.py`) 보유 → 제외)
  차단하려면 후보 D 가 추가로 *모두* 만족:
    G2) *이번 변경* 이 D 에 새 도메인 작업을 더했다 = D 가 신규(untracked) 디렉터리이거나,
        `D/migrations/` 아래 신규(untracked/added) 마이그레이션 파일이 있다. git 이 아니거나
        판정 불가면 **스킵(차단 아님)** — 무관 레거시의 단순 수정은 새 마이그레이션이 없어 스킵.
        (reviewer-FP: 비-git 전면 차단·무관 앱 단순 touch 차단 회피.)
    G3) `application/` 하위에 D 의 *실질 이주 대응 앱이 없다* — 디렉터리 `application/<D>/`
        존재만으론 면제 안 됨(빈 껍데기 `__init__.py` 토큰 회피 차단). `application/**/
        django_<D>/` 또는 `application/<D>/` 가 *실제 모델/마이그레이션 내용* 을 보유해야 면제.
  G1 ∧ ∃D(후보 ∧ G2 ∧ G3) → exit 2(blocker). 아니면 exit 0.

사용법: check-app-container.py [TARGET_DIR]   (기본 TARGET_DIR=현재 디렉터리)
종료코드: 0=clean(또는 표준 미적용), 2=blocker(발견 출력), 1=사용 오류.
구조화 레코드: DJR_FINDINGS_JSON=<경로> 지정 시 findings.py(공용 모듈)가 JSON lines 를
추가 방출한다. 위반 라인은 공용 포매터의 계약 문법 `- {where}: {msg}` 로 방출하며
record 순서 = stdout 위반 라인 순서다(T2-1 출력 계약 v2).

그래프 좌표(T2-2): 규범 정본 = 온톨로지 그래프(`ontology/rules/`) · 이 검사기의 #N ↔ Work 조인은
  alias 대장(`ontology/wiring/aliases.ttl`)이 소유한다. 조인 확정: 없음(대장 미등재 — T3 이월).
  미확정 #N 은 T3 이관에서 해소한다(현행 조인 3종 — 판단표
  `workspace/design/2026-08-20-ontology-t2-2-alias-ledger.md` §2·§5).
"""
from __future__ import annotations

import subprocess
import sys

import checker_target
from findings import ContractFindings, emit_all
from pathlib import Path

# rule-owner-map 규칙 0건 — 선행 규약 소유(reverse_coverage PRIOR_CONTRACT_SCRIPTS 등재).
CONTRACT_REF = "선행 규약(표준 트리 전신 — application/ 컨테이너 위치) 소유"

SKIP_DIRS = {
    ".venv", "venv", "site-packages", "node_modules", ".git", "__pycache__", ".dddjango",
    "build", "dist", ".tox", ".mypy_cache", ".pytest_cache", ".eggs",
}

APP_MARKER_FILES = ("apps.py", "models.py")
APP_MARKER_DIRS = ("models", "migrations")


def _root_application(root: Path) -> Path | None:
    """레포 루트 *직속* `application/` 컨테이너(있으면). rglob 금지 — 중첩 오인 차단."""
    cand = root / "application"
    return cand if cand.is_dir() else None


def _is_settings_package(d: Path) -> bool:
    """Django 프로젝트 설정 패키지인가(커스텀 User 모델 등 앱마커 보유해도 제외)."""
    if (d / "settings.py").is_file():
        return True
    if (d / "urls.py").is_file() and (
        (d / "wsgi.py").is_file() or (d / "asgi.py").is_file()
    ):
        return True
    return False


def _has_app_marker(d: Path) -> bool:
    if any((d / m).is_file() for m in APP_MARKER_FILES):
        return True
    return any((d / m).is_dir() for m in APP_MARKER_DIRS)


def _iter_candidate_apps(root: Path, app_container: Path):
    """`application/` 밖에서 Django 앱으로 보이는 디렉터리(후보)를 yield."""
    for path in root.rglob("*"):
        if not path.is_dir():
            continue
        parts = set(path.parts)
        if parts & SKIP_DIRS:
            continue
        # `application/` 컨테이너 자체와 그 하위는 이 백스톱 범위 밖(§0-2가 봄).
        if path == app_container or app_container in path.parents:
            continue
        if not (path / "__init__.py").is_file():
            continue  # namespace package·잡동사니 배제
        if _is_settings_package(path):
            continue  # 프로젝트 설정 패키지 면제
        if not _has_app_marker(path):
            continue
        # `migrations/`·`models/` 같은 앱 *내부* 폴더 자체가 후보로 잡히지 않게:
        # 부모가 이미 앱 마커를 가진 앱이면 건너뛴다(앱은 앱을 중첩하지 않음).
        if path.name in APP_MARKER_DIRS and _has_app_marker(path.parent):
            continue
        yield path


def _git_available(root: Path) -> bool:
    return (root / ".git").exists()


def _porcelain(root: Path, relpath: str) -> str | None:
    try:
        res = subprocess.run(
            ["git", "-C", str(root), "status", "--porcelain", "--", relpath],
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if res.returncode != 0:
        return None
    return res.stdout


def _touched_with_new_domain(root: Path, d: Path) -> bool:
    """이번 변경이 D 에 새 도메인 작업을 더했나.

    git 이 없거나 판정이 불가하면 True — «전부 이번 작업으로 간주»한다(fail-closed ·
    명세 조각 ⓐ). 비-git 스킵은 검사가 꺼진 것이지 깨끗한 것이 아니다."""
    if not _git_available(root):
        return True
    rel = d.relative_to(root).as_posix()
    out = _porcelain(root, rel)
    if out is None:
        return True
    for line in out.splitlines():
        if len(line) < 4:
            continue
        flag = line[:2]
        path = line[3:].strip().strip('"')
        is_new = flag.startswith("??") or flag.strip().startswith("A")
        if not is_new:
            continue
        # D 전체가 신규(untracked 디렉터리) — 새 앱.
        if path == rel or path == rel + "/":
            return True
        base = path.rsplit("/", 1)[-1]
        # 신규 마이그레이션 파일(= 새 스키마/도메인 작업 신호).
        if f"{rel}/migrations/" in (path + "/") and base.endswith(".py") and base != "__init__.py":
            return True
        # 신규 앱 골격 파일(apps.py/models.py 가 untracked = 새로 만든 앱).
        if path in (f"{rel}/apps.py", f"{rel}/models.py"):
            return True
    return False


def _has_real_app_content(app_dir: Path) -> bool:
    """이 디렉터리가 *실질* Django 앱인가(빈 껍데기 토큰 배제) — 모델/마이그레이션 내용 보유."""
    models_py = app_dir / "models.py"
    if models_py.is_file() and models_py.stat().st_size > 0:
        return True
    models_pkg = app_dir / "models"
    if models_pkg.is_dir() and any(
        p.suffix == ".py" and p.name != "__init__.py" for p in models_pkg.iterdir()
    ):
        return True
    migrations = app_dir / "migrations"
    if migrations.is_dir() and any(
        p.suffix == ".py" and p.name != "__init__.py" for p in migrations.iterdir()
    ):
        return True
    return False


def _has_migrated_counterpart(app_container: Path, name: str) -> bool:
    """`application/` 하위에 D 의 *실질* 이주 대응 앱이 있나(있으면 면제=G3 거짓)."""
    # 표준 위치: application/<name>/driven_layer/django_<name>/
    for django_pkg in app_container.rglob(f"django_{name}"):
        if django_pkg.is_dir() and _has_real_app_content(django_pkg):
            return True
    # 데이터소스 flat 이주: application/<name>/ 자신이 실질 내용 보유.
    direct = app_container / name
    if direct.is_dir() and _has_real_app_content(direct):
        return True
    # 혹은 application/<name>/ 아래 어디든 실질 앱 산출물.
    if direct.is_dir():
        for sub in direct.rglob("*"):
            if sub.is_dir() and _has_real_app_content(sub):
                return True
    return False


def main(argv: list[str]) -> int:
    root = Path(argv[1]).resolve() if len(argv) > 1 else Path.cwd()
    bad_target_reason = checker_target.bc_shaped_target_reason(root)
    if bad_target_reason is not None:
        print(f"사용 오류: {bad_target_reason}", file=sys.stderr)
        return 1
    if not root.is_dir():
        print(f"[check-app-container] 사용 오류: 디렉터리 아님 {root}", file=sys.stderr)
        return 1

    app_container = _root_application(root)
    if app_container is None:
        return 0  # 표준 레이아웃(`application/`) 미적용 → §1.1 존중, 해당 없음.

    if not _git_available(root):
        print("주의: git 저장소가 아니다 — touched 식별이 불가해 «전 후보»를 검사한다(fail-closed)")

    # 라인 = 레코드 필드의 순수 함수(계약 문법 `- {where}: {msg}`) — emit_all 이
    # 인쇄와 레코드 방출을 같은 순서로 수행한다(출력 계약 v2).
    findings = ContractFindings(CONTRACT_REF, defer=True)
    for d in _iter_candidate_apps(root, app_container):
        if not _touched_with_new_domain(root, d):
            continue  # git 판정 가능 + 미touch → 존중(§1.1 — touched 만 본다)
        if _has_migrated_counterpart(app_container, d.name):
            continue  # 이미 application/ 로 이주됨(빈 껍데기 아닌 실질) → orphan/정리 영역.
        rel = d.relative_to(root).as_posix()
        findings.add(
            where=rel,
            msg="Django 앱이 `application/` 밖 평면에 있다 — 앱은 `application/<app>/` 아래(houserules §0-1)",
            symbol=d.name,
        )

    if findings:
        print(
            "[check-app-container] BLOCKER — Django 앱이 `application/` 밖 평면에 있다"
            "(houserules §0-1: 앱은 `application/<app>/` 아래):"
        )
        emit_all(findings, printer=print)
        print(
            "  근거: discipline-houserules §0-1. 이번 작업이 건드린(새 마이그레이션/판정) "
            "기존 앱도 위치는 `application/<bc>/`(장고 앱이면 `driven_layer/django_<bc>/`)로 "
            "이주한다 — `architecture-ddd` §3.2 «판정 소유→구조 이주» 항-(2) 2026-06-08 개정으로 데이터소스 면제는 *판정 "
            "실내용(.py)*에 한정하고 위치·4계층·애그리거트 골격은 무조건이다; 이 스크립트는 그중 "
            "*위치* 한 축만 본다. 기존 0001 보존은 `implementation-django` §10.4(label/db_table 유지·state-only "
            "0002). 루트 평면 유지가 정말 필요하면 코드에서 방치하지 말고 설계(G1 트레이드오프)로 "
            "반송하라. (무관·미관여 기존 앱은 이 백스톱이 건드리지 않는다 — §1.1 존중.)"
        )
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
