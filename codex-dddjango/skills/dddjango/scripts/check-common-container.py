#!/usr/bin/env python3
"""dddjango 횡단 `common/` 컨테이너 레벨 결정적 백스톱 (discipline-houserules §1 집행).

표준 트리에서 `common/`(앱 횡단 공용 — `enum/`·`django/`·`ninja/`·`<project>/` 기술축)은
*프로젝트 루트* 에 둔다 = `application/` 의 *형제*. 그런데 `application/common/` 처럼
`application/`(= feature 앱 컨테이너) *안* 에 넣으면 §1 위반이다. 회귀(smoke6-claude:
problem+json 헬퍼를 `application/common/ninja/problem.py` 에 둠 = 단일 BC 인데 횡단 버킷
조기 승격 + 레벨 오류)를 막는다.

*왜 결정적 백스톱인가* — 헬퍼 위치는 코더 구현 결정이고(설계 명세가 "presentation 경계"라
해도 코더가 common/ 으로 승격), `check-app-container`(§0-1, 앱이 `application/` *밖*)나
`check-layer-skeleton`(§0-2, BC 4계층 깊이)에 안 걸린다(common 은 앱이 아니라 잡히지 않음).
이 좁은 그물이 "common 레벨" 한 축을 모델 무관하게 집행한다 — 단일 BC 면 헬퍼를 그 BC
`presentation_layer/` 에 두라는 *예방* 은 ninja §6.2 가이드 몫이고, 이건 그 보조 백스톱이다.

거짓양성 ≈ 0 — *feature 앱이 아닌* `application/common/` 만 차단:
  G1) 레포 루트 직속 `application/` 존재 = 표준 채택. 없으면 exit 0(§1.1 존중).
  G2) `application/common/` 디렉터리가 존재하고, (a) 4계층 앱이 *아니며*(`domain_layer/`·
      `application_layer/`·`infra_layer/`·`presentation_layer/` 중 하나도 없음 — 'common'
      이라는 *진짜 feature 앱* 은 제외) (b) 내용이 있다(서브디렉터리 또는 `__init__.py` 아닌
      `.py`). 이러면 루트에 둘 횡단 버킷(`ninja/`·`django/`·`enum/`·`<project>/` 기술축이든
      평면 `problem.py` 든)을 `application/` 안에 잘못 넣은 것이다(reviewer 회피 C1·C2 포함).
  G1 ∧ G2 → exit 2(blocker). 아니면 exit 0.

사용법: check-common-container.py [TARGET_DIR]   (기본=현재 디렉터리)
종료코드: 0=clean(또는 표준 미적용), 2=blocker(발견 출력), 1=사용 오류.
"""
from __future__ import annotations

import sys
from pathlib import Path

# 4계층 앱 마커 — 이게 있으면 'common' 이라는 *feature 앱* 이라 횡단 버킷 오배치 아님.
LAYER_DIRS = ("domain_layer", "application_layer", "infra_layer", "presentation_layer")


def _root_application(root: Path) -> Path | None:
    cand = root / "application"
    return cand if cand.is_dir() else None


def _has_content(d: Path) -> bool:
    """빈 stray 디렉터리(예: `__init__.py` 만) 제외 — 서브디렉터리 또는 실질 `.py` 보유."""
    for p in d.iterdir():
        if p.is_dir() and p.name != "__pycache__":
            return True
        if p.suffix == ".py" and p.name != "__init__.py":
            return True
    return False


def _is_misplaced_common(common_dir: Path) -> bool:
    """`application/common/` 이 (feature 앱이 아닌) 오배치 횡단 버킷인가."""
    if not common_dir.is_dir():
        return False
    if any((common_dir / layer).is_dir() for layer in LAYER_DIRS):
        return False  # 4계층 'common' feature 앱 → 이 백스톱 대상 아님(§0-2 영역).
    return _has_content(common_dir)


def main(argv: list[str]) -> int:
    root = Path(argv[1]).resolve() if len(argv) > 1 else Path.cwd()
    if not root.is_dir():
        print(f"[check-common-container] 사용 오류: 디렉터리 아님 {root}", file=sys.stderr)
        return 1

    app_container = _root_application(root)
    if app_container is None:
        return 0  # 표준 레이아웃 미적용 → §1.1 존중, 해당 없음.

    common_under_app = app_container / "common"
    if _is_misplaced_common(common_under_app):
        inside = sorted(
            p.name + ("/" if p.is_dir() else "")
            for p in common_under_app.iterdir()
            if p.name != "__pycache__"
        )
        print(
            "[check-common-container] BLOCKER — 횡단 `common/` 버킷이 `application/` 안에 있다"
            "(discipline-houserules §1: `common/` 은 프로젝트 루트 = `application/` 의 형제):"
        )
        print(f"  - {common_under_app.relative_to(root).as_posix()}/  (내용: {', '.join(inside)})")
        print(
            "  근거: `common/`(앱 횡단 공용)은 *프로젝트 루트* 에 두고 `application/` 안에 넣지 "
            "않는다 — `application/` 은 feature 앱 컨테이너다. 또한 단일 BC 면 헬퍼(problem 등)를 "
            "그 BC `application/<app>/presentation_layer/` 에 두고, 2개 이상 BC 가 실제 공유할 때만 "
            "루트 `common/ninja/` 로 승격한다(YAGNI; ninja §6.2·§6.3·houserules §1). `common/` 을 "
            "루트로 옮기거나, 단일 BC 면 그 BC presentation_layer 로 내려라."
        )
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
