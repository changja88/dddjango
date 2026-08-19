"""렌더 동기 검증기 (T1-4 — .venv 전용).

그래프 소유 절 전건에 대해 «코퍼스 투영물 == render(그래프)»를 byte 단위로 단언한다.
등가 판정(게이트 2-1 통과 조건): **마커 라인 제거 후 byte 잔차 0** — 등급 분류는
실패 진단 전용(통과 대체물 아님).

- SyncDebt 등재 절(rules 그래프의 djr:SyncDebt·djr:debtSection): 불일치를 경고로 강등.
- --release: SyncDebt 잔량 0까지 요구(릴리즈 별도 단 — D1 단일 출처 불훼손).

사용: PYTHONPATH=workspace/tools .venv/bin/python workspace/tools/ontology_render_sync.py [--release]
exit 0 동기 / 1 불일치(red) 또는 --release 시 SyncDebt 잔량>0 / 2 도구 오류
"""
from __future__ import annotations

import argparse
import sys

from ontology_canon import REPO_ROOT
from ontology_census import parse_sections
from ontology_render import DJR, MARKER, graph_sections, load_doc_graph, manifest_paths


def strip_marker(span: bytes) -> bytes:
    lines = span.split(b"\n")
    kept = [ln for ln in lines if ln != MARKER.encode("utf-8")]
    return b"\n".join(kept)


def smoke() -> int:
    """골든 2건(T1-4): ① 그래프 소유 절 투영물 수기 수정 → red ② 산문 소유 절 정상 편집 →
    렌더 동기는 green(오탐 없음 — 산문 편집은 원장 재기준선 절차의 소관이지 동기 위반이 아님).
    실파일을 바이트 백업 후 수정·검사·복원한다(finally 복원 보장)."""
    import subprocess
    from pathlib import Path

    ninja = REPO_ROOT / "dddjango/skills/implementation-django-ninja/references/final.md"
    ddd_skill = REPO_ROOT / "dddjango/skills/architecture-ddd/SKILL.md"
    backup = {p: p.read_bytes() for p in (ninja, ddd_skill)}

    def run_sync() -> int:
        proc = subprocess.run(
            [sys.executable, str(Path(__file__).resolve())],
            capture_output=True, text=True,
            env={**__import__("os").environ, "PYTHONPATH": str(Path(__file__).resolve().parent)})
        return proc.returncode

    try:
        assert run_sync() == 0, "전제: 현재 동기 green이어야 스모크 성립"
        # ① 그래프 소유 절(s022-6.1) 본문 1행 수기 수정 → red
        ninja.write_bytes(backup[ninja].replace("`409`: conflict".encode(), "`409`: CONFLICT-TAMPERED".encode(), 1))
        rc1 = run_sync()
        ninja.write_bytes(backup[ninja])
        # ② 산문 소유 절(architecture-ddd SKILL) 정상 편집 → 렌더 동기는 green
        ddd_skill.write_bytes(backup[ddd_skill] + "\n(smoke: benign prose edit)\n".encode())
        rc2 = run_sync()
        ddd_skill.write_bytes(backup[ddd_skill])
        ok1, ok2 = rc1 == 1, rc2 == 0
        print(f"[render-sync-smoke] ① 그래프 절 수기 수정 → {'red ✓' if ok1 else f'FAIL(rc={rc1})'}")
        print(f"[render-sync-smoke] ② 산문 절 정상 편집 → {'동기 green ✓(오탐 없음)' if ok2 else f'FAIL(rc={rc2})'}")
        return 0 if (ok1 and ok2) else 1
    finally:
        for p, b in backup.items():
            p.write_bytes(b)


def main() -> int:
    ap = argparse.ArgumentParser(description="렌더 동기 검증기")
    ap.add_argument("--release", action="store_true", help="SyncDebt 잔량 0 요구")
    ap.add_argument("--smoke", action="store_true", help="골든 2건(red/green) 실증")
    args = ap.parse_args()
    if args.smoke:
        return smoke()

    import csv
    import hashlib

    from rdflib import Namespace

    djr = Namespace(DJR)
    paths = manifest_paths()
    rules_dir = REPO_ROOT / "ontology" / "rules"
    # 원장 유효 행(마지막 행 유효) — baseline 검사(#9)·소유 대조(#13) 재료
    ledger_eff: dict[tuple[str, str], dict] = {}
    ledger_path = REPO_ROOT / "ontology" / "LEDGER.tsv"
    if ledger_path.is_file():
        with open(ledger_path, encoding="utf-8") as f:
            for r in csv.DictReader(f, delimiter="\t"):
                ledger_eff[(r["doc_key"], r["section_key"])] = r
    red, warn, debt_total, checked = 0, 0, 0, 0
    for ttl in sorted(rules_dir.glob("*.ttl")):
        dk = ttl.stem
        if dk not in paths:
            print(f"[render-sync] {dk}: manifest에 없음", file=sys.stderr)
            return 2
        g = load_doc_graph(dk)
        rendered = graph_sections(g, paths[dk])
        debt_iris = {str(s) for s in g.objects(None, djr.debtSection)}  # 전체 IRI 비교(L-H #15)
        debt_total += len(debt_iris)
        # L-H #13: 소유권 이중 정본(LEDGER owner ↔ rules sectionOwner) 정합
        ledger_graph_keys = {sk for (d, sk), r in ledger_eff.items() if d == dk and r["owner"] == "graph"}
        if ledger_graph_keys != set(rendered):
            print(f"[render-sync] RED {dk}: 소유권 불일치 — LEDGER graph {sorted(ledger_graph_keys)} ≠ rules owner-graph {sorted(rendered)}")
            red += 1
        data = (REPO_ROOT / paths[dk]).read_bytes()
        secs = {s["section_key"]: s for s in parse_sections(data)}
        from ontology_canon import frag_encode
        for skey, text in sorted(rendered.items()):
            checked += 1
            if skey not in secs:
                print(f"[render-sync] RED {dk}/{skey}: 현재 분할에 절 없음(구조 훼손)")
                red += 1
                continue
            cur = secs[skey]["span"]
            expect = text.encode("utf-8")
            s_iri = f"{DJR}s/{frag_encode(paths[dk])}/{frag_encode(skey)}"
            is_debt = s_iri in debt_iris
            problems = []
            if cur != expect:
                problems.append("마커 부재(투영 미적용)" if MARKER.encode("utf-8") not in cur
                                else "본문 불일치(무단 수정 또는 그래프 미반영)")
            # L-H #9: 마커 제거 후 == 이관 시점 원문(baseline) — 게이트 2-1 조건의 상시화
            row = ledger_eff.get((dk, skey))
            if row and hashlib.sha256(strip_marker(cur)).hexdigest() != row["baseline_sha256"]:
                problems.append("마커 제거 후 baseline 불일치(원문 변형)")
            for reason in problems:
                if is_debt:
                    print(f"[render-sync] warn {dk}/{skey}: {reason} — SyncDebt 등재(경고 강등)")
                    warn += 1
                else:
                    print(f"[render-sync] RED {dk}/{skey}: {reason}")
                    red += 1
    print(f"[render-sync] 그래프 소유 절 {checked} — red {red} · warn {warn} · SyncDebt {debt_total}")
    if args.release and debt_total:
        print(f"[render-sync] --release: SyncDebt 잔량 {debt_total} > 0")
        return 1
    return 1 if red else 0


if __name__ == "__main__":
    sys.exit(main())
