#!/usr/bin/env python3
"""설치본 트리 loop probe + 런타임 행동 parity + tree hash 봉인 (T2-3 exit · 적대 리뷰 AN#13/AO 과제 3).

**왜 필요한가**: 루프 코어를 `dddjango/scripts/` 로 옮긴 것만으로는 «설치본에서 실제로 돈다»가
증명되지 않는다. 그렇다고 live 설치 cache 를 갱신하는 것은 비가역·외부 행위라 사용자 요청이
필요하다(자율 규약 R3-3). 그래서 **source 트리를 임시 디렉터리로 materialize** 해 그것을 설치본처럼
쓰고, 거기서 게이트→sidecar 를 실제로 돌린다. live cache 는 건드리지 않는다.

실측 배경(2026-08-20): source manifest `2.12.0` ↔ 설치 cache `2.11.0` · `.py` diff 30건 ·
**`findings.py` 가 cache 에 아예 없다**. 즉 지금 설치본에는 T2-1 공용 출력 모듈 자체가 없다.
cache 갱신·재검증은 T2-0b hard blocker 로 등재돼 있고, 이 probe 는 그 전 단계의 artifact 검증이다.

검사:
  P1 Claude 트리 materialize → loop probe(게이트 red → 귀속 sidecar 산출)
  P2 Codex  트리 materialize → 같은 probe
  P3 두 런타임 **행동 parity** — 같은 픽스처에 같은 귀속 집합·같은 레코드 수
  P4 tree hash 봉인값 출력(T2-0b manifest fragment 재료)

exit 0 = 전건 통과 / 2 = 실패 / 1 = 재료 결손.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT: Path = Path(__file__).resolve().parents[2]
CLAUDE_SCRIPTS: Path = ROOT / "dddjango" / "scripts"
CODEX_SCRIPTS: Path = ROOT / "codex-dddjango" / "skills" / "dddjango" / "scripts"

sys.path.insert(0, str(ROOT / "workspace" / "tools"))
import registry_gate_smoke as G  # noqa: E402


def tree_hash(root: Path) -> str:
    """디렉터리의 결정적 해시 — 경로+내용(정렬·`__pycache__` 제외)."""
    h = hashlib.sha256()
    for p in sorted(root.rglob("*")):
        if not p.is_file() or "__pycache__" in p.parts:
            continue
        h.update(str(p.relative_to(root)).encode("utf-8"))
        h.update(p.read_bytes())
    return h.hexdigest()


def materialize(src: Path, dest: Path) -> Path:
    """설치본처럼 쓸 임시 트리 — live cache 를 건드리지 않는다."""
    shutil.copytree(src, dest, ignore=shutil.ignore_patterns("__pycache__"))
    return dest


def probe(scripts: Path, repo: Path, anchor: str, side: Path) -> "tuple[int, dict]":
    """materialize 한 트리의 registry_gate 로 게이트를 돌려 귀속 sidecar 를 얻는다."""
    proc = subprocess.run(
        [sys.executable, str(scripts / "registry_gate.py"), str(repo),
         "--anchor", anchor, "--introduced-json", str(side)],
        capture_output=True, text=True, env=G._scrubbed_env())
    payload: dict = json.loads(side.read_text(encoding="utf-8")) if side.is_file() else {}
    return proc.returncode, payload


def main() -> int:
    if not CLAUDE_SCRIPTS.is_dir() or not CODEX_SCRIPTS.is_dir():
        print("재료 결손: 런타임 scripts 트리 없음", file=sys.stderr)
        return 1
    rows: "list[tuple[str, str, bool]]" = []

    with tempfile.TemporaryDirectory() as td_s:
        td: Path = Path(td_s)
        # 공통 red 픽스처 — 위반 1건이 있는 git 저장소
        repo, anchor = G._make_repo(td, "probe-repo")
        f: Path = repo / "application" / "orders" / "domain_layer" / "probe_svc.py"
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text("PROBECACHE = {}\n", encoding="utf-8")

        results: "dict[str, dict]" = {}
        for name, src in (("claude", CLAUDE_SCRIPTS), ("codex", CODEX_SCRIPTS)):
            tree: Path = materialize(src, td / f"plugin-{name}" / "scripts")
            side: Path = td / f"{name}.json"
            code, payload = probe(tree, repo, anchor, side)
            ok: bool = (code == 2 and bool(payload.get("records"))
                        and not payload.get("unmatched_lines"))
            results[name] = payload
            rows.append((f"P{1 if name == 'claude' else 2} {name} 트리 loop probe",
                         f"exit {code} · 레코드 {len(payload.get('records', []))} · "
                         f"대응없음 {len(payload.get('unmatched_lines', []))}", ok))

        a, b = results["claude"], results["codex"]
        parity: bool = (sorted(a.get("attributed_lines", [])) == sorted(b.get("attributed_lines", []))
                        and len(a.get("records", [])) == len(b.get("records", [])))
        rows.append(("P3 런타임 행동 parity",
                     f"귀속 {len(a.get('attributed_lines', []))} ↔ "
                     f"{len(b.get('attributed_lines', []))} · 레코드 "
                     f"{len(a.get('records', []))} ↔ {len(b.get('records', []))}", parity))

    seal_c: str = tree_hash(CLAUDE_SCRIPTS)
    seal_x: str = tree_hash(CODEX_SCRIPTS)
    rows.append(("P4 tree hash 봉인", f"claude {seal_c[:16]} · codex {seal_x[:16]}", True))

    print("| 검사 | 실측 | 판정 |")
    print("|---|---|---|")
    bad: int = 0
    for name, detail, ok in rows:
        bad += 0 if ok else 1
        print(f"| {name} | {detail} | {'✓' if ok else '✗'} |")
    print(f"\n검사 {len(rows)} · 통과 {len(rows) - bad} · 실패 {bad}")
    print(f"\n# T2-0b manifest fragment 재료(봉인값)\n"
          f"claude_scripts_tree_sha256: {seal_c}\ncodex_scripts_tree_sha256: {seal_x}")
    print("# 주의: live 설치 cache 는 이 probe 가 건드리지 않는다 — cache 갱신·재검증은 "
          "T2-0b hard blocker(사용자 승인 필요)다.")
    return 0 if not bad else 2


if __name__ == "__main__":
    sys.exit(main())
