#!/usr/bin/env python3
"""역방향 커버리지 — 플러그인 전 파일 → 닿는 규칙·존재 근거 (5번 계획 Phase 4-1).

정방향(spec_lint ⑧)은 「규칙마다 소유자가 있나」를 묻고, 여기는 거꾸로
「플러그인의 파일마다 그 파일을 설명하는 규칙·근거가 있나」를 묻는다 —
완료 자: **미설명 파일 0** (계획 §2 완료 자 4).

판정:
  ⑴ dddjango/ 아래 모든 파일이 아래 범주 중 하나에 들어야 한다.
      · scripts/check-*.py           — 매핑표 ⓒ 소유 규칙 ≥ 1
      · scripts/standard_tree.py     — 트리 140행 단일 출처(전 검사기 import)
      · scripts/business_vocab.py    — #628 실체(업무 어휘 재료)
      · scripts/checker_target.py    — 호출 계약 공용 모듈(전 검사기 import · 라운드 1 P2)
      · skills/discipline-houserules — ⓐ 정본(final.md)·ⓑ SKILL(값 0)
      · 나머지 skills 10             — 책 코퍼스(corpus_mirror 11 · 치환 부류)
      · agents/*.md                  — 매핑표 ⓓ 소유 규칙(0이면 파이프라인 절차)
      · commands/dddjango.md         — flow 정본 + registry 렌더(ⓒ⑥⑦)
      · .claude-plugin/plugin.json   — 플러그인 매니페스트
  ⑵ 매핑표 ⓒ·ⓓ 컬럼이 가리키는 경로가 전부 실재해야 한다(죽은 소유자 0).

exit 0 = 미설명 0 · 죽은 소유자 0 / exit 2 = 위반 / exit 1 = 재료 결손(fail-closed).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT: Path = Path(__file__).resolve().parents[2]
PLUGIN: Path = ROOT / "dddjango"
OWNER_MAP: Path = ROOT / "workspace" / "plan" / "2026-08-11-rule-owner-map.md"

CORPUS_SKILLS: set[str] = {
    "architecture-api", "architecture-db", "architecture-ddd",
    "discipline-cleancode", "discipline-tdd",
    "implementation-django", "implementation-django-ninja",
    "implementation-django-web", "implementation-python", "implementation-test",
}
PIPELINE_ONLY_AGENTS: set[str] = {
    "acceptance-tester.md", "design-review-api.md",
    "design-review-db.md", "design-review-ddd.md",
}
# ⓓ 규칙은 없지만 계획이 절차·의무를 명시한 에이전트.
FLOW_DUTY_AGENTS: dict[str, str] = {
    "coder.md": "파이프라인 절차 + 골격 실현 의무(계획 ⑹ T56㉮ — 값은 final.md §0·§1 포인터)",
}
# 538규칙(트리 개정 명세) «밖» 선행 계약이 소유하는 검사기 — 문면 소유는 각 계약
# 문서·registry 설명문이 진다. 트리 규칙과의 겹침 재검토는 8번 이관 몫.
PRIOR_CONTRACT_SCRIPTS: dict[str, str] = {
    "check-response-schema-bypass.py": "선행 계약(08-04 API-error) 소유 — JSON 성공 raw-response bypass",
    "check-transient-overmapping.py": "선행 계약(08-04 API-error) 소유 — preserve handler overmapping 가드",
    "check-ninja-boundary-middleware.py": "선행 계약(08-04 API-error) 소유 — BC HTTP concern 의 global middleware 자기등록",
    "check-idempotency-scope-creep.py": "선행 계약(architecture-api §13 멱등 스코프) 소유 — 승인 범위 밖 멱등 산출물",
    "check-choices-literal-consumption.py": "선행 계약(2026-07-06 상수 승격) 소유 — Enum/choices 리터럴 소비",
    "check-app-container.py": "선행 규약(표준 트리 전신 — application/ 컨테이너 위치) 소유·비-git fail-closed",
    "check-common-container.py": "선행 규약(D38 승격/강등 — 루트 framework/ 배치) 소유·트리 규칙 몫은 business-vocabulary 가 진다",
}


def load_owner_map() -> "tuple[dict[str, list[int]], dict[str, list[int]]]":
    """매핑표에서 ⓒ(경로→규칙들)·ⓓ(경로→규칙들)를 뽑는다."""
    if not OWNER_MAP.is_file():
        print(f"재료 결손: {OWNER_MAP} 없음", file=sys.stderr)
        sys.exit(1)
    by_c: dict[str, list[int]] = {}
    by_d: dict[str, list[int]] = {}
    row_re = re.compile(r"^\|\s*(\d+)\s*\|\s*\S+\s*\|\s*([^|]*)\|\s*([^|]*)\|")
    for line in OWNER_MAP.read_text(encoding="utf-8").splitlines():
        m = row_re.match(line)
        if not m:
            continue
        num: int = int(m.group(1))
        c_cell: str = m.group(2).strip()
        d_cell: str = m.group(3).strip()
        for cell, bucket in ((c_cell, by_c), (d_cell, by_d)):
            path = re.sub(r"\s*\((신설|재작성)\)\s*$", "", cell).strip()
            if path in ("", "—") or path.startswith("메타("):
                continue
            bucket.setdefault(path, []).append(num)
    return by_c, by_d


def plugin_files() -> "list[Path]":
    out: list[Path] = []
    for p in sorted(PLUGIN.rglob("*")):
        if p.is_file() and "__pycache__" not in p.parts:
            out.append(p)
    return out


def main() -> int:
    by_c, by_d = load_owner_map()
    problems: list[str] = []
    rows: list[tuple[str, str]] = []

    # ⑵ 죽은 소유자 — 매핑표가 가리키는 파일이 실재하나
    for path in sorted(set(by_c) | set(by_d)):
        base = ROOT / path if path.startswith("workspace/") else PLUGIN / path
        if not base.is_file():
            problems.append(f"죽은 소유자: 매핑표가 가리키는 `{path}` 가 없다")

    # ⑴ 전 파일 분류
    for f in plugin_files():
        rel = f.relative_to(PLUGIN)
        key = str(rel)
        parts = rel.parts
        why: "str | None" = None
        if parts[0] == "scripts":
            if rel.name == "standard_tree.py":
                why = "트리 140행 단일 출처 — 전 검사기 import·#79 ROWS 구동·tree_mirror 삼중 동기"
            elif rel.name == "business_vocab.py":
                why = "#628 실체 — 업무 어휘 재료(도메인 공개 심볼 토큰·불용어·기술 이름)"
            elif rel.name == "checker_target.py":
                why = "호출 계약 공용 모듈 — 전 검사기 import(BC 모양 TARGET 거절 · 라운드 1 P2 · fixture_matrix 호출 계약 레인 27케이스가 행동 고정)"
            else:
                nums = by_c.get(key, [])
                if nums:
                    why = f"ⓒ 규칙 {len(nums)}건 (#{nums[0]}…#{nums[-1]})"
                elif rel.name in PRIOR_CONTRACT_SCRIPTS:
                    why = PRIOR_CONTRACT_SCRIPTS[rel.name]
                else:
                    problems.append(f"미설명: `{key}` — 매핑표 ⓒ 에 규칙 0건")
        elif parts[0] == "agents":
            nums = by_d.get(key, [])
            if nums:
                why = f"ⓓ 규칙 {len(nums)}건 (물음·human)"
            elif rel.name in FLOW_DUTY_AGENTS:
                why = FLOW_DUTY_AGENTS[rel.name]
            elif rel.name in PIPELINE_ONLY_AGENTS:
                why = "파이프라인 절차(ⓓ 규칙 0 — flow 소유·무변)"
            else:
                problems.append(f"미설명: `{key}` — ⓓ 규칙 0건인데 절차 전용 목록에도 없다")
        elif parts[0] == "commands":
            why = "flow 정본 — 게이트·registry 렌더·ⓒ⑥⑦(빚 스캔·유일 flow 예외)"
        elif parts[0] == "skills":
            skill = parts[1]
            if skill == "discipline-houserules":
                why = "ⓐ 정본(references/final.md — 전 규칙 값 소유)" if rel.name != "SKILL.md" else "ⓑ SKILL(값 0 — 체크리스트)"
            elif skill in CORPUS_SKILLS:
                why = "책 코퍼스(corpus_mirror 11 — 치환 부류)"
            else:
                problems.append(f"미설명: `{key}` — 알 수 없는 스킬 `{skill}`")
        elif parts[0] == ".claude-plugin":
            why = "플러그인 매니페스트"
        else:
            problems.append(f"미설명: `{key}` — 어느 범주에도 없다")
        if why is not None:
            rows.append((key, why))

    # ⓒ 규칙 합계가 registry 전체를 덮는지(정보 표시용)
    script_rules: int = sum(len(v) for k, v in by_c.items() if k.startswith("scripts/"))
    agent_rules: int = sum(len(v) for v in by_d.values())

    print(f"플러그인 파일 {len(rows) + 0}건 분류 · ⓒ 규칙 {script_rules} · ⓓ 규칙 {agent_rules}")
    for key, why in rows:
        print(f"  {key} — {why}")
    if problems:
        print(f"\n위반 {len(problems)}건:")
        for p in problems:
            print(f"  {p}")
        return 2
    print("\n미설명 파일 0 · 죽은 소유자 0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
