#!/usr/bin/env python3
"""dddjango 4계층 골격 결정적 백스톱 (구조 — houserules §0-2 집행).

기존 백스톱(mechanism-ownership·error-centralization·response-schema-bypass)이
*행위/계약*을 보는 데 비해, 이건 **구조**를 본다. 표준 레이아웃(`application/<bc>/`)을
적용한 프로젝트에서 각 바운디드 컨텍스트(BC)는 4계층 폴더(`domain_layer`·
`application_layer`·`infra_layer`·`presentation_layer`)를 **내용이 없어도 빈
패키지(`__init__.py`)로라도 모두** 가져야 한다(houserules §0-2). 네 위반 형태를 차단한다:
  - **부분 평면**: 일부 계층만 있고 하나를 생략(스모크 SH-2 — HTTP 없이 ACL·
    published_service 로만 소비되는 내부 전용 BC 가 `presentation_layer` 를 생략).
  - **완전 평면**: Django 앱 산출물은 있는데 4계층으로 전혀 분리 안 함(`application/<bc>/`
    루트에 `models.py`·`views.py` 등을 직접 둔 startapp 직후 평면 상태).
  - **종류 폴더 누락**: 4계층은 있으나 고정명 종류 폴더(`presentation_layer/api`·
    `presentation_layer/schema`·`infra_layer/acl`)를 빈 패키지로라도 만들지 않음(§0-4 개정
    2026-06-08: 이들은 표현/통합 내용이 없어도 무조건 생성). 더해 *이미 존재하는*
    `domain_layer/<aggregate>/` 의 코어 종류(`entity`·`value_object`·`repository` + `exception.py`)
    누락도 잡는다(coder 가 `domain_layer/product/` 만들고 `value_object/` 를 빠뜨린 경우).
  - **외래 port/(협력 포트 오배치 — SH-7)**: `application_layer`/`infra_layer` 하위의 `port/`
    디렉터리가 비-`__init__` `.py` 를 담음. 협력 포트(타 BC 소비용 역할 추상 ABC)는
    `domain_layer/<aggregate>/port/` 소유다(houserules §2 — "도메인은 협력 포트로만 의존"·
    §3 표·"command 는 domain port 의존" DIP). application_layer 의 종류 폴더는
    command/query/dto 뿐이고 ACL *구현*은 `infra_layer/acl/` 직속이라, 그 계층들 밑 `port/` 는
    표준 트리에 존재하지 않는 외래 구조다(라이브 형태 N=2·둘 다 Codex: design-spec 이
    포트를 "use-case dependency" 로 재분류해 `application_layer/place_order/port/` 에 배치 —
    reviewer 가 명세-부합을 이유로 권고로 강등해 게이트를 통과했다). **빈 `port/` 패키지는
    면제**(위반의 전조일 뿐·골격 잔재). 경로에 test/tests 가 끼면 스킵. 폴더 개명 변종
    (`contract/`·`ports/` 복수형·평면 `port.py`)과 `presentation_layer` 배치는 안 잡는다
    (저-recall — 채점 결정 레인(`find -type d -name port`)과 동일 사각·reviewer 의미 레인 몫).

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
  위 셋이 참인 BC 에서:
    - (b)면 4계층 전부 미분리 = blocker.
    - (a)면 4계층 중 하나라도 (폴더가 없거나 / 폴더는 있으나 `__init__.py` 가 없어 git 에
      존속 안 되면) blocker.
    - 4계층이 다 있어도 고정명 종류 폴더(`presentation_layer/api`·`presentation_layer/schema`·
      `infra_layer/acl`)가 빈 패키지로 없으면 blocker — 고정명이라 거짓 양성 없다(§0-4 무조건).
    - *이미 존재하는* `domain_layer/<aggregate>/` 가 *애그리거트로 보이면*(루트 파일
      `<X>/<X>.py` 또는 `entity/`·`value_object/` 하나라도 보유) 그 안의 코어 종류
      (`entity`·`value_object`·`repository` 폴더 + `exception.py`)가 빠지면 blocker. **ORM 에서
      애그리거트 이름을 추론하지 않는다** — 디스크에 실재하는 `domain_layer/<X>/` 만 검사한다.
      `domain_layer/` 직하에 cross-aggregate 공용 `domain_service/`(final.md §3) 가 와도
      애그리거트 신호(루트 파일/entity/value_object)가 없으면 애그리거트로 보지 않고 스킵한다.
      `[선택]` 종류 폴더(`port`·`domain_service`·`event`·`specification`)는 *존재만* 확인하고
      누락은 잡지 않는다(저-recall — reviewer 의미 레인 몫; 거짓 양성 회피 우선).
    - `application_layer`/`infra_layer` 하위 `port/` 가 비-`__init__` `.py` 를 담으면 blocker
      (외래 port — 위 네 번째 위반 형태. 빈 패키지·test 경로는 면제).
  통과 조건: 4계층 + 고정명 종류 폴더(api/schema/acl)가 빈 패키지로 있고, 존재하는
  애그리거트의 코어 종류가 채워져 있으면 통과. `domain_layer/` 에 애그리거트가 *0개* 면(예:
  데이터소스 골격 미생성) 이 스크립트는 **안 잡고 reviewer 의미 레인에 맡긴다**(저-recall
  수용). `application_layer` 는 feature(`<feature>/`) 0개면 빈 계층 정당이라 검사하지 않는다.
  내용 적정성(채운 게 옳은지)은 항상 discipline-reviewer 의미 체크 몫이다.

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

# 고정명 종류 폴더 — §0-4 개정(2026-06-08)으로 표현/통합 내용이 없어도 무조건 빈 패키지.
# 고정명이라 거짓 양성 없음(BC 마다 동일 골격). (계층, 종류폴더 상대경로) 쌍.
REQUIRED_KIND_DIRS = (
    ("presentation_layer", "api"),
    ("presentation_layer", "schema"),
    ("infra_layer", "acl"),
)

# 애그리거트 *코어* 종류 — `domain_layer/<aggregate>/` 가 애그리거트로 보일 때 빠지면 잡는다.
# `[선택]`(port/domain_service/event/specification)은 의도적으로 제외(저-recall·거짓 양성 회피).
AGG_CORE_KIND_DIRS = ("entity", "value_object", "repository")
AGG_CORE_FILE = "exception.py"
# 애그리거트 신호 — 이 중 하나라도 있으면 `<X>/` 를 애그리거트로 보고 코어 완비를 검사한다.
# 없으면(예: cross-aggregate 공용 `domain_service/`) 애그리거트가 아니므로 스킵(거짓 양성 회피).
AGG_SIGNAL_KIND_DIRS = ("entity", "value_object")

# 외래 port 검사 대상 계층 — 협력 포트는 domain_layer 소유라 이 계층들 밑 port/ 는 표준 트리에
# 없는 외래 구조다(SH-7·houserules §2·§3 표). presentation_layer 는 채점 결정 레인(SH-7 FAIL =
# application_layer/infra_layer)과 정합하게 제외(관측 0·reviewer 의미 레인 몫).
FOREIGN_PORT_LAYERS = ("application_layer", "infra_layer")
TEST_DIR_NAMES = {"test", "tests"}


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


def _is_empty_package_dir(d: Path) -> bool:
    """디렉터리이고 `__init__.py` 를 가진 regular package인가(빈 골격 허용 판정)."""
    return d.is_dir() and (d / "__init__.py").exists()


def _kind_dir_issues(bc_dir: Path) -> list[str]:
    """고정명 종류 폴더(api/schema/acl) 누락/비-패키지를 설명 리스트로. 고정명=거짓 양성 0."""
    issues: list[str] = []
    for layer, kind in REQUIRED_KIND_DIRS:
        d = bc_dir / layer / kind
        if not d.is_dir():
            issues.append(f"{layer}/{kind}/ 폴더 없음")
        elif not (d / "__init__.py").exists():
            issues.append(f"{layer}/{kind}/ 에 __init__.py 없음(git 미추적·골격 소실)")
    return issues


def _looks_like_aggregate(agg_dir: Path) -> bool:
    """`domain_layer/<X>/` 가 애그리거트인가 — 루트 파일 `<X>/<X>.py` 또는 entity/value_object
    하나라도 보유. 신호가 없으면(예: cross-aggregate 공용 `domain_service/`) 애그리거트가
    아니므로 코어 완비 검사에서 제외(거짓 양성 회피)."""
    if (agg_dir / f"{agg_dir.name}.py").is_file():
        return True
    return any((agg_dir / kind).is_dir() for kind in AGG_SIGNAL_KIND_DIRS)


def _aggregate_issues(bc_dir: Path) -> list[str]:
    """*이미 존재하는* `domain_layer/<X>/`(애그리거트로 보이는) 의 코어 종류 누락을 설명
    리스트로. ORM 에서 이름 추론 안 함 — 디스크 실재 애그리거트만. 코어=entity/value_object/
    repository 폴더 + exception.py. `[선택]` 종류는 잡지 않는다(저-recall)."""
    domain_layer = bc_dir / "domain_layer"
    if not domain_layer.is_dir():
        return []
    issues: list[str] = []
    for agg_dir in sorted(domain_layer.iterdir()):
        if not agg_dir.is_dir() or agg_dir.name in SKIP_DIRS:
            continue
        if not _looks_like_aggregate(agg_dir):
            continue  # 애그리거트 신호 없음(공용 domain_service 등) → 스킵.
        for kind in AGG_CORE_KIND_DIRS:
            d = agg_dir / kind
            if not d.is_dir():
                issues.append(f"domain_layer/{agg_dir.name}/{kind}/ 폴더 없음")
            elif not (d / "__init__.py").exists():
                issues.append(
                    f"domain_layer/{agg_dir.name}/{kind}/ 에 __init__.py 없음(골격 소실)"
                )
        if not (agg_dir / AGG_CORE_FILE).is_file():
            issues.append(f"domain_layer/{agg_dir.name}/{AGG_CORE_FILE} 없음")
    return issues


def _foreign_port_issues(bc_dir: Path) -> list[str]:
    """`application_layer`/`infra_layer` 하위 `port/` 의 협력 포트 오배치(SH-7)를 설명 리스트로.

    협력 포트(ABC)는 `domain_layer/<aggregate>/port/` 소유(houserules §2·§3 표) — 호출자가
    application 유스케이스(command)여도 'use-case dependency' 재분류로 위치가 바뀌지 않는다.
    빈 `port/` 패키지(비-`__init__` .py 0개)·test 경로는 면제. 폴더 개명 변종은 안 잡는다(저-recall)."""
    issues: list[str] = []
    for layer in FOREIGN_PORT_LAYERS:
        layer_dir = bc_dir / layer
        if not layer_dir.is_dir():
            continue
        for port_dir in sorted(layer_dir.rglob("port")):
            if not port_dir.is_dir():
                continue
            rel_parts = set(port_dir.relative_to(bc_dir).parts)
            if rel_parts & SKIP_DIRS or rel_parts & TEST_DIR_NAMES:
                continue
            payload = sorted(
                p.name for p in port_dir.rglob("*.py") if p.name != "__init__.py"
            )
            if payload:
                rel = port_dir.relative_to(bc_dir)
                issues.append(
                    f"{rel}/ 에 협력 포트 추정 코드({', '.join(payload[:3])}) — "
                    f"협력 포트(ABC)는 domain_layer/<aggregate>/port/ 소유(§2), "
                    f"{layer} 하위 port/ 는 표준 트리에 없는 외래 구조(SH-7)"
                )
    return issues


def _is_bc_to_check(bc_dir: Path) -> bool:
    """4계층을 따라야 할 앱: 계층을 하나라도 가졌거나(부분), Django 산출물 평면(완전)."""
    return _has_any_layer(bc_dir) or _has_django_app_marker(bc_dir)


def _layer_issues(bc_dir: Path) -> list[str]:
    """누락/비-패키지 계층 + 고정명 종류 폴더 + 존재 애그리거트 코어 종류를 설명 리스트로."""
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
    # 고정명 종류 폴더(api/schema/acl) — §0-4 개정 무조건(데이터소스 BC 포함). 고정명=거짓 양성 0.
    issues.extend(_kind_dir_issues(bc_dir))
    # 존재하는 애그리거트의 코어 종류 완비 — ORM 추론 없이 디스크 실재만. 부재(0개)는 reviewer 몫.
    issues.extend(_aggregate_issues(bc_dir))
    # 외래 port/ — 협력 포트 오배치(SH-7). application_layer/infra_layer 밑 port/ 에 실코드.
    issues.extend(_foreign_port_issues(bc_dir))
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
            "[check-layer-skeleton] BLOCKER — 4계층 BC 가 계층/종류 골격을 생략했거나 "
            "협력 포트를 도메인 밖 계층(`application_layer`/`infra_layer` 하위 `port/`)에 두었다"
            "(houserules §0-2·§0-4·§2):"
        )
        for f in findings:
            print(f)
        print(
            "  근거: discipline-houserules §0-2·§0-4·§2. 표현/도메인 관심사가 없다는 판단으로 "
            "계층·종류 폴더 자체를 생략하지 않는다 — 빈 `presentation_layer` 라도 `__init__.py` 만 "
            "둔 빈 패키지로 만든다(예: ACL·published_service 로만 소비되는 내부 전용 BC). "
            "고정명 종류 폴더(`presentation_layer/api`·`presentation_layer/schema`·`infra_layer/acl`)는 "
            "§0-4 개정(2026-06-08)으로 표현/통합이 없어도 무조건 빈 패키지로 둔다 — 데이터소스 BC 도 "
            "예외 없다(`architecture-ddd` §632-(2) 면제는 *판정 실내용(.py)*에 한정). 이미 만든 "
            "`domain_layer/<aggregate>/` 는 코어 종류(`entity`·`value_object`·`repository` + "
            "`exception.py`)를 빠짐없이 갖춘다. 완전 평면 앱은 4계층으로 분리하라. "
            "외래 port 발견이면: 협력 포트(타 BC 소비용 역할 추상 ABC)는 "
            "`domain_layer/<aggregate>/port/` 로 옮긴다 — 포트를 호출하는 것이 application "
            "유스케이스(command)이고 애그리거트가 직접 import 하지 않아도, 'use-case dependency' "
            "재분류로 `application_layer/<feature>/port/` 에 두지 않는다(§2 — command 가 "
            "*domain-owned* port 에 의존하는 것이 DIP 다). ACL *구현*(어댑터)은 `infra_layer/acl/` "
            "직속이다(port/ 하위 아님). 네트워크/시리얼 '포트' 같은 기술 유틸이면 `port/` 는 이 "
            "표준에서 협력 포트 전용 명칭이니 의미에 맞는 다른 폴더명을 쓴다. 접을/옮길 수 없는 "
            "실질 사유가 있으면 코드로 박지 말고 설계(G1 트레이드오프)로 반송하라."
        )
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
