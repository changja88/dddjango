#!/usr/bin/env python3
"""dddjango 코퍼스 미러 동기 검사·동기 도구 (메인테이너/빌드타임 — 런타임 게이트 아님).

배경: 스킬 지식은 여러 계층에 복제된다. 소스 미러가 stale해지면 다음 재저작이
stale 소스를 신뢰원으로 삼아 과거 수정(DR)을 조용히 되돌린다(회귀 메커니즘, DIAGNOSIS R5).
이 도구는 그 drift를 결정적으로 *탐지*(--check)하고 *해소*(--write)한다.

세 불변식 (검사 스코프 = reference와 SKILL.md를 함께 가진 11개 스킬):
  불변식1  소스 본문 ≡ 배포 본문
    소스   workspace/reference/<skill>/reference/final.md   (P1 Source Sufficiency 블록 보유 가능)
    배포   dddjango/skills/<skill>/references/final.md
    본문   첫 비-P1 '## ' 헤딩 ~ EOF (byte-exact). title·P1·출처 blockquote·--- 등
           attribution 영역은 비교 대상 아님(소스/배포 구조가 의도적으로 다름).
  불변식2  배포(Claude) ≡ 배포(Codex)  전체 파일 byte-exact
    codex  codex-dddjango/skills/<skill>/references/final.md
  불변식3  Claude SKILL ≡ Codex SKILL  플랫폼 frontmatter 정규화 뒤 byte-exact
    Claude 전용 `user-invocable: false` 한 줄만 비교에서 제거한다.

스코프 밖(플랫폼별 역할 프롬프트): agents/*.md · commands/*.md · dddjango-* 역할 SKILL.md.

배치: workspace/tools/ (배포 경계 밖). 19개 런타임 게이트(dddjango/scripts/check-*.py)는
  *사용자 생성 코드*를 검사하지만 이 도구는 *플러그인 자체 코퍼스*를 검사한다 — 다른 부류다.
  그래서 dddjango/scripts/에 두지 않고 check- 접두사도 쓰지 않는다.

fail-CLOSED: 파일 부재·앵커 실패·파싱 실패는 비-0 종료(exit 3). 런타임 게이트의 fail-open을
  베끼지 않는다 — 메인테이너 무결성 검사에서 fail-open은 drift를 은폐하기 때문.

exit:  0 = in-sync
       2 = drift (불변식1·2·3 위반 — `--write`로 해소 가능)
       3 = 구조 전제 깨짐 (파일 부재·앵커 실패 등 — 사람 개입 필요)
       1 = usage error

사용:
  python3 workspace/tools/corpus_mirror_sync.py             # --check (기본): 검사만
  python3 workspace/tools/corpus_mirror_sync.py --write     # 재동기: 소스←배포(본문 splice), codex←배포(복사)
  python3 workspace/tools/corpus_mirror_sync.py --format json
  python3 workspace/tools/corpus_mirror_sync.py --root /path/to/repo
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

EXIT_IN_SYNC = 0
EXIT_DRIFT = 2
EXIT_STRUCTURE = 3
EXIT_USAGE = 1

P1_HEADING = "## P1 Source Sufficiency"


class StructureError(Exception):
    """구조 전제 위반 (앵커 없음·preamble 오염 등) → fail-closed(exit 3)."""


def split_at_body(path: Path) -> tuple[list[str], list[str]]:
    """(preamble_lines, body_lines) 반환.

    본문 = 첫 비-P1 '## ' 헤딩부터 EOF. 그 앞(preamble)에는 attribution 라인만 허용한다:
    빈 줄 · '# ' h1 title · '## P1 Source Sufficiency' · '>' blockquote · '|' 표 · '---' hr.
    그 외 라인이 본문 헤딩 앞에 있으면(= 본문이 '## '로 시작하지 않으면) StructureError.
    """
    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")

    anchor = None
    for i, ln in enumerate(lines):
        if ln.startswith("## ") and ln.strip() != P1_HEADING:
            anchor = i
            break
    if anchor is None:
        raise StructureError(f"{path}: 비-P1 '## ' 본문 헤딩을 찾지 못함")

    for ln in lines[:anchor]:
        s = ln.strip()
        if s == "":
            continue
        if s.startswith("# ") and not s.startswith("## "):  # h1 title
            continue
        if s == P1_HEADING:
            continue
        if s.startswith(">"):  # 출처 blockquote
            continue
        if s.startswith("|"):  # P1 표
            continue
        if s == "---":  # hr
            continue
        raise StructureError(
            f"{path}: 본문 헤딩 앞에 attribution 아닌 라인이 있음 → 앵커 신뢰 불가: {ln!r}"
        )

    return lines[:anchor], lines[anchor:]


def discover_skills(root: Path) -> list[str]:
    """배포본(Claude)에서 references/final.md를 가진 스킬 목록(권위). 정렬해 결정적."""
    base = root / "dddjango" / "skills"
    skills = []
    for d in sorted(base.iterdir()):
        if (d / "references" / "final.md").is_file():
            skills.append(d.name)
    return skills


def paths_for(root: Path, skill: str) -> dict[str, Path]:
    return {
        "src": root / "workspace" / "reference" / skill / "reference" / "final.md",
        "dep": root / "dddjango" / "skills" / skill / "references" / "final.md",
        "codex": root / "codex-dddjango" / "skills" / skill / "references" / "final.md",
        "dep_skill": root / "dddjango" / "skills" / skill / "SKILL.md",
        "codex_skill": root / "codex-dddjango" / "skills" / skill / "SKILL.md",
    }


def normalized_skill_text(path: Path) -> str:
    """YAML frontmatter 안의 Claude 전용 한 줄만 제거한 SKILL 본문."""
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        raise StructureError(f"{path}: SKILL.md YAML frontmatter 시작 구분자 없음")
    try:
        end = next(index for index, line in enumerate(lines[1:], start=1) if line.strip() == "---")
    except StopIteration as error:
        raise StructureError(f"{path}: SKILL.md YAML frontmatter 종료 구분자 없음") from error
    return "".join(
        line
        for index, line in enumerate(lines)
        if not (
            index < end
            and line.rstrip("\r\n") == "user-invocable: false"
        )
    )


def check_skill(root: Path, skill: str) -> dict:
    """한 스킬의 세 불변식 검사. 반환 dict: status in {in_sync, drift, structure}."""
    p = paths_for(root, skill)
    result = {
        "skill": skill,
        "inv1": "in_sync",
        "inv2": "in_sync",
        "inv3": "in_sync",
        "notes": [],
    }

    # 불변식1: 소스 본문 ≡ 배포 본문
    if not p["src"].is_file():
        result["inv1"] = "structure"
        result["notes"].append(f"소스 미러 부재: {p['src']}")
    else:
        try:
            _, dep_body = split_at_body(p["dep"])
            _, src_body = split_at_body(p["src"])
        except StructureError as e:
            result["inv1"] = "structure"
            result["notes"].append(str(e))
        else:
            if "\n".join(src_body) != "\n".join(dep_body):
                result["inv1"] = "drift"
                result["notes"].append("소스 본문 ≠ 배포 본문 (소스 stale)")

    # 불변식2: 배포(Claude) ≡ 배포(Codex) 전체 파일
    if not p["codex"].is_file():
        result["inv2"] = "structure"
        result["notes"].append(f"codex 미러 부재: {p['codex']}")
    else:
        if p["dep"].read_text(encoding="utf-8") != p["codex"].read_text(encoding="utf-8"):
            result["inv2"] = "drift"
            result["notes"].append("배포(Claude) ≠ 배포(Codex)")

    # 불변식3: SKILL.md 플랫폼 frontmatter 정규화 뒤 semantic byte parity
    if not p["dep_skill"].is_file() or not p["codex_skill"].is_file():
        result["inv3"] = "structure"
        result["notes"].append("Claude/Codex SKILL.md 중 하나가 없다")
    else:
        try:
            dep_skill = normalized_skill_text(p["dep_skill"])
            codex_skill = normalized_skill_text(p["codex_skill"])
        except StructureError as error:
            result["inv3"] = "structure"
            result["notes"].append(str(error))
        else:
            if dep_skill != codex_skill:
                result["inv3"] = "drift"
                result["notes"].append(
                    "Claude SKILL ≠ Codex SKILL (frontmatter 정규화 후)"
                )

    invariant_states = (result["inv1"], result["inv2"], result["inv3"])
    if "structure" in invariant_states:
        result["status"] = "structure"
    elif "drift" in invariant_states:
        result["status"] = "drift"
    else:
        result["status"] = "in_sync"
    return result


def write_skill(root: Path, skill: str, result: dict) -> list[str]:
    """drift를 해소(--write). 반환: 수행한 동작 설명 리스트. structure 상태면 건너뜀."""
    actions = []
    p = paths_for(root, skill)
    if result["status"] == "structure":
        return [f"{skill}: 구조 깨짐 → 자동 동기 불가, 건너뜀"]

    if result["inv1"] == "drift":
        src_preamble, _ = split_at_body(p["src"])
        _, dep_body = split_at_body(p["dep"])
        new_src = "\n".join(src_preamble + dep_body)
        p["src"].write_text(new_src, encoding="utf-8")
        actions.append(f"{skill}: 불변식1 소스 본문 ← 배포 본문 (preamble 보존)")

    if result["inv2"] == "drift":
        p["codex"].write_text(p["dep"].read_text(encoding="utf-8"), encoding="utf-8")
        actions.append(f"{skill}: 불변식2 codex ← 배포 (전체 복사)")

    if result["inv3"] == "drift":
        p["codex_skill"].write_text(
            normalized_skill_text(p["dep_skill"]),
            encoding="utf-8",
        )
        actions.append(f"{skill}: 불변식3 Codex SKILL ← Claude SKILL (frontmatter 정규화)")

    return actions


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="dddjango 코퍼스 미러 동기 검사·동기")
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="검사만 (기본)")
    mode.add_argument("--write", action="store_true", help="drift 해소(소스←배포, codex←배포)")
    ap.add_argument("--format", choices=["text", "json"], default="text")
    ap.add_argument("--root", default=None, help="레포 루트 (기본: 이 스크립트 기준 자동)")
    args = ap.parse_args(argv[1:])

    if args.root:
        root = Path(args.root).resolve()
    else:
        root = Path(__file__).resolve().parents[2]  # workspace/tools/ → repo root

    if not (root / "dddjango" / "skills").is_dir():
        print(f"usage error: 레포 루트가 아님(dddjango/skills 없음): {root}", file=sys.stderr)
        return EXIT_USAGE

    skills = discover_skills(root)
    if not skills:
        print(f"usage error: references/final.md를 가진 스킬 없음: {root}", file=sys.stderr)
        return EXIT_USAGE

    results = [check_skill(root, s) for s in skills]

    written = []
    if args.write:
        for r in results:
            written += write_skill(root, r["skill"], r)
        # 동기 후 재검사
        results = [check_skill(root, s) for s in skills]

    has_structure = any(r["status"] == "structure" for r in results)
    has_drift = any(r["status"] == "drift" for r in results)

    if args.format == "json":
        print(json.dumps({
            "root": str(root),
            "skills": len(skills),
            "written": written,
            "results": results,
            "exit": EXIT_STRUCTURE if has_structure else (EXIT_DRIFT if has_drift else EXIT_IN_SYNC),
        }, ensure_ascii=False, indent=2))
    else:
        for r in results:
            mark = {"in_sync": "✓", "drift": "✗ DRIFT", "structure": "‼ STRUCTURE"}[r["status"]]
            print(
                f"  {mark:<12} {r['skill']:<28} inv1={r['inv1']} "
                f"inv2={r['inv2']} inv3={r['inv3']}"
            )
            for n in r["notes"]:
                print(f"               · {n}")
        if written:
            print("\n  [--write 수행]")
            for a in written:
                print(f"    + {a}")
        total = len(skills)
        n_sync = sum(1 for r in results if r["status"] == "in_sync")
        print(f"\n  {n_sync}/{total} in-sync"
              + (" · STRUCTURE 위반 있음(exit3)" if has_structure else "")
              + (" · DRIFT 있음(exit2)" if has_drift and not has_structure else ""))

    if has_structure:
        return EXIT_STRUCTURE
    if has_drift:
        return EXIT_DRIFT
    return EXIT_IN_SYNC


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
