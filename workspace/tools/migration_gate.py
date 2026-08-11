#!/usr/bin/env python3
"""리빌드 실측기 — 대상 저장소에 V1 옛 이름 폴더가 남아 있는지 잰다.

역사: 8번 ㉡(V1 옛 기계·이중 수용 걷기)의 게이트 판정기였다. ㉡ 는 2026-08-12
사용자 결정(「플러그인 먼저 걷고 broccoli-server 는 새 트리로 리빌드한다」)으로
실행됐고, 이후 이 도구의 역할은 «리빌드가 새 트리에 실제로 닿았는지» 실측하는
것이다 — 잔존 0 이 아니면 그 저장소에서 skeleton 검사(#81·#490)가 같은 폴더들을
위반으로 문다.

옛 이름 목록은 2026-08-12 §4 개명 표의 «역사적 상수»다 — 플러그인은 더 이상
이 이름들을 모른다(standard_tree 에서 걷었다). 여기 고정본만 남는다.

판정(대상 저장소마다):
  · `application/*/` 아래(깊이 무관) 이름이 옛 별칭(presentation_layer·infra_layer·
    published_service·acl)인 디렉터리 수
  · BC 루트 직계의 옛 `common/`(→framework) · 저장소 루트의 `common/`
  잔존 합 = 0 이어야 리빌드 완료다.

exit 0 = 전 대상 잔존 0(리빌드 완료) · 2 = 잔존 있음(목록 출력)
     · 1 = 사용 오류/대상 아님(`application/` 없는 저장소).

사용: python3 workspace/tools/migration_gate.py <대상 저장소> [<대상 저장소> …]
"""
from __future__ import annotations

import sys
from pathlib import Path

SKIP_DIRS: set[str] = {".git", ".venv", "venv", "node_modules", "__pycache__", ".dddjango"}
# 2026-08-12 이관 종료 시점의 옛 이름 고정본 — standard_tree 가 아니라 여기가 출처다.
LEGACY_DIR_NAMES: set[str] = {"presentation_layer", "infra_layer", "published_service", "acl"}


def scan(target: Path) -> "tuple[list[str], bool]":
    """(잔존 목록, 채택 저장소인가). 잔존 = 옛 별칭 이름 디렉터리 경로들."""
    app = target / "application"
    leftovers: list[str] = []
    if not app.is_dir():
        return leftovers, False
    for bc in sorted(p for p in app.iterdir() if p.is_dir() and p.name not in SKIP_DIRS):
        for d in sorted(bc.rglob("*")):
            if not d.is_dir() or set(d.relative_to(target).parts) & SKIP_DIRS:
                continue
            if d.name in LEGACY_DIR_NAMES:
                leftovers.append(str(d.relative_to(target)))
            elif d.name == "common" and d.parent == bc:
                leftovers.append(str(d.relative_to(target)))
    if (target / "common").is_dir():
        leftovers.append("common (저장소 루트 — →framework)")
    return leftovers, True


def main(argv: "list[str]") -> int:
    if not argv:
        print(__doc__, file=sys.stderr)
        return 1
    total: int = 0
    adopted_any: bool = False
    for raw in argv:
        target = Path(raw).resolve()
        if not target.is_dir():
            print(f"사용 오류: 디렉터리가 아니다 — {target}", file=sys.stderr)
            return 1
        leftovers, adopted = scan(target)
        if not adopted:
            print(f"{target.name}: `application/` 없음 — 표준 채택 저장소가 아니라 게이트 대상 밖")
            continue
        adopted_any = True
        if leftovers:
            total += len(leftovers)
            print(f"{target.name}: 옛 이름 잔존 {len(leftovers)}건 — 리빌드 «미완»")
            for p in leftovers:
                print(f"  {p}")
        else:
            print(f"{target.name}: 옛 이름 잔존 0 — 이 저장소는 이관 완료")
    if total:
        print(f"\n리빌드 미완 — 잔존 합 {total}건. 이 폴더들은 새 트리에서 skeleton(#81·#490) 위반으로 잡힌다.")
        return 2
    if adopted_any:
        print("\n리빌드 완료 — 전 대상 잔존 0.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
