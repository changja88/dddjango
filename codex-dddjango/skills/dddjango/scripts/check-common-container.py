#!/usr/bin/env python3
"""dddjango 횡단 `framework/` 컨테이너 레벨 결정적 백스톱.

표준 트리에서 `framework/`(저장소 횡단 공용 — 트리 112~134행)는 *프로젝트 루트* 에 둔다
= `application/` 의 *형제*. `common` 은 옛 이름이다 — 이관 종료(2026-08-12) 후 수용하지
않고, 오배치 버킷 «검출»(#49)로만 알아본다. 그런데 `application/framework/`
(또는 `application/common/`)처럼 `application/`(= BC 컨테이너) *안* 에 넣으면 위반이다.
회귀(smoke6: clock/identifier 같은 횡단 utility 를 `application/common/utility.py` 에 둠 =
횡단 버킷의 컨테이너 레벨 오류)를 막는다.

*왜 결정적 백스톱인가* — 헬퍼 위치는 코더 구현 결정이고, `check-app-container`(앱이
`application/` *밖*)나 `check-layer-skeleton`(BC 층 골격)에 안 걸린다(횡단 버킷은 앱이
아니라 잡히지 않음). 이 좁은 그물이 "framework 레벨" 한 축을 집행한다 — 승격의 자는
「이 낱말의 뜻을 누가 정하나」(D38)이고, BC 하나가 뜻을 정하는 것은 그 BC 소유 층에 남는다.

거짓양성 ≈ 0 — *BC 가 아닌* `application/{framework|common}/` 만 차단:
  G1) 레포 루트 직속 `application/` 존재 = 표준 채택. 없으면 exit 0.
  G2) `application/framework/`(또는 `application/common/`) 디렉터리가 존재하고,
      (a) 층 폴더 앱이 *아니며*(새·옛 층 이름 어느 것도 없음 — 'common' 이라는 *진짜
      BC* 는 제외) (b) 내용이 있다(서브디렉터리 또는 `__init__.py` 아닌 `.py`).
  G1 ∧ G2 → exit 2(blocker). 아니면 exit 0.

사용법: check-common-container.py [TARGET_DIR]   (기본: 현재 디렉터리)
종료코드: 0=clean(또는 표준 미적용) · 1=사용/분석 오류 · 2=blocker(발견 출력)
"""
from __future__ import annotations

import sys

import checker_target
from pathlib import Path

try:
    import standard_tree as tree
except ImportError:  # 데이터 모듈 없이는 판정 불가 — fail-closed(분석 오류)
    print("분석 오류: standard_tree.py 를 찾지 못했다 — 검사기와 같은 폴더에 있어야 한다", file=sys.stderr)
    sys.exit(1)

# 층 폴더 마커 — 이게 있으면 그 이름의 *진짜 BC* 라 횡단 버킷 오배치가 아니다.
NEW_LAYERS = ("driving_layer", "application_layer", "domain_layer", "driven_layer")
LAYER_DIRS = NEW_LAYERS

# 루트 횡단 버킷의 이름 — `common` 은 역사적 버킷 낱말이다(#49 검출 리터럴 · 수용 아님).
BUCKET_NAMES = ("framework", "common")


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


def _is_misplaced_bucket(bucket_dir: Path) -> bool:
    """`application/{framework|common}/` 이 (BC 가 아닌) 오배치 횡단 버킷인가."""
    if not bucket_dir.is_dir():
        return False
    if any((bucket_dir / layer).is_dir() for layer in LAYER_DIRS):
        return False  # 층 폴더를 가진 '진짜 BC' → check-layer-skeleton 영역.
    return _has_content(bucket_dir)


def main(argv: list[str]) -> int:
    if len(argv) > 1:
        print(f"사용법: {Path(sys.argv[0]).name} [TARGET_DIR]", file=sys.stderr)
        return 1
    root = Path(argv[0]).resolve() if argv else Path.cwd()
    bad_target_reason = checker_target.bc_shaped_target_reason(root)
    if bad_target_reason is not None:
        print(f"사용 오류: {bad_target_reason}", file=sys.stderr)
        return 1
    if not root.is_dir():
        print(f"사용 오류: 디렉터리가 아니다 — {root}", file=sys.stderr)
        return 1

    app_container = _root_application(root)
    if app_container is None:
        return 0  # 표준 레이아웃 미적용 → 기존 규약 존중, 해당 없음.

    findings: list[str] = []
    for name in BUCKET_NAMES:
        bucket = app_container / name
        if not _is_misplaced_bucket(bucket):
            continue
        inside = sorted(
            p.name + ("/" if p.is_dir() else "")
            for p in bucket.iterdir()
            if p.name != "__pycache__"
        )
        findings.append(f"  [컨테이너] {bucket.relative_to(root).as_posix()}/  (내용: {', '.join(inside)})")

    if findings:
        print("blocker — 횡단 `framework/` 버킷이 `application/` 안에 있다 (트리 112행: `framework/` 는 프로젝트 루트 = `application/` 의 형제)")
        for f in findings:
            print(f)
        print(
            "  근거: `framework/`(저장소 횡단 공용 — 옛 이름 `common/` 도 같은 버킷이다)는 "
            "프로젝트 루트에 두고 `application/` 안에 넣지 않는다 — `application/` 은 BC "
            "컨테이너다. 승격의 자는 「이 낱말의 뜻을 누가 정하나」(D38): BC 하나가 뜻을 "
            "정하면 그 BC 의 소유 층에 두고, 어느 BC 도 뜻을 정하지 않는 기계 부품만 루트 "
            "`framework/<capability|technology>/` 로 올린다. 내용의 소유에 따라 루트 "
            "`framework/` 또는 소유 BC 층으로 옮겨라."
        )
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
