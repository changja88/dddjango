#!/usr/bin/env python3
"""사전 검증 질의 카탈로그 골든 — Q1~Q4 양성·음성 쌍 (T2-4 V1 · .venv 전용).

**공허 통과를 막는 것이 목적이다**(적대 리뷰 AQ-05): Q2 골든이 「run B 조회가 0건」 하나뿐이면
`FILTER(false)` 나 잘못된 조인으로 **항상 빈 결과**를 내는 구현도 통과한다. 그래서 같은 픽스처에서
**양성(기대 행·계수)과 음성(0건)을 함께** 단언한다.

**run 격리는 fail-closed 다**: Q2 는 `$RUN` 바인딩 없이 실행하면 도구가 거부한다. 바인딩 없이
돌면 전역 스캔이 되어 T2-0a 실런 격리가 깨진다.

사용: PYTHONPATH=workspace/tools .venv/bin/python workspace/tools/query_golden_check.py [--emit]
exit 0 = 전건 일치 / 2 = 불일치 / 1 = 재료 결손
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from ontology_canon import REPO_ROOT

QUERIES: Path = REPO_ROOT / "workspace" / "tools" / "queries"
FIXTURES: Path = REPO_ROOT / "workspace" / "eval" / "fixtures" / "rulepack"
GOLDEN: Path = FIXTURES / "query-golden.json"
DJR: str = "https://numchida.com/ns/djr#"


def _graph(extra: "list | None" = None):
    from rdflib import Graph
    g = Graph()
    for sub in ("rules", "wiring", "vocab"):
        for f in sorted((REPO_ROOT / "ontology" / sub).glob("*.ttl")):
            g.parse(f, format="turtle")
    for f in extra or []:
        g.parse(f, format="turtle")
    return g


def _local(value: str) -> str:
    return str(value).rsplit("#", 1)[-1]


def observe() -> "dict":
    from rdflib import Literal

    prod = _graph()
    # Q2 재료는 **어댑터가 굽는다**(사후 리뷰 AS-10): 손으로 쓴 TTL 을 읽으면 findings →
    # 어댑터 → 질의 사슬이 실제로 이어지는지 검증되지 않는다. 여기서 findings/0 레코드에
    # `experiment_run_id` 를 실어 어댑터를 태우고, 그 산출 TTL 로 Q2 를 돈다.
    import violation_adapter as va
    base_rec = {"schema": "findings/0", "ts": "2026-08-20T00:00:00Z", "severity": "violation",
                "sentinel": None, "contract_ref": None, "symbol": None, "expression": None}
    recs = [
        dict(base_rec, run_id="p-1", record_id="a:1", rule="#3", experiment_run_id="exp-A",
             checker="check-context-isolation.py", file="application/a/x.py:12",
             message="A런 전용 위반"),
        dict(base_rec, run_id="p-2", record_id="a:2", rule="#488", experiment_run_id="exp-A",
             checker="check-layer-skeleton.py", file="application/b/__init__.py",
             message="두 런에 재발(A)"),
        dict(base_rec, run_id="p-3", record_id="b:1", rule="#488", experiment_run_id="exp-B",
             checker="check-layer-skeleton.py", file="application/b/__init__.py",
             message="두 런에 재발(B)"),
    ]
    ttl, tally = va.convert(recs, va.load_alias_map())
    from rdflib import Graph
    runs = _graph()
    runs.parse(data=("@prefix djr: <https://numchida.com/ns/djr#> .\n"
                     "@prefix sh: <http://www.w3.org/ns/shacl#> .\n"
                     "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n" + ttl),
               format="turtle")
    out: "dict" = {"adapter": {"joined": tally["joined"],
                               "nodes": ttl.count(" a djr:Violation")}}

    # Q1 — 경로 축(처치 밖 카탈로그). 양성: 글롭 4건. 음성: 절이 아닌 주어 0건.
    rows = list(prod.query((QUERIES / "q1-path-to-norms.rq").read_text(encoding="utf-8")))
    out["q1"] = {"globs": sorted({str(r.glob) for r in rows}), "rows": len(rows)}

    # Q2 — **양성 + 음성 동시**. exp-A 는 2 Work, exp-B 는 1 Work,
    #      두 런에 재발한 R-0120 은 **양쪽 모두 1건**으로 보여야 한다(런 간 재발 보존).
    q2 = (QUERIES / "q2-violations-to-norms.rq").read_text(encoding="utf-8")
    for run in ("exp-A", "exp-B", "exp-없음"):
        res = list(runs.query(q2, initBindings={"RUN": Literal(run)}))
        out[f"q2:{run}"] = sorted(f"{_local(r.work)}×{int(r.violationCount)}" for r in res)
    # 바인딩 **없이** 돌면 전역 스캔이 되어야 위험한데, `FILTER(STR(?run) = STR($RUN))` 의
    # 미바인딩 비교는 오류가 되어 행을 **배제**한다 — 문법 차원에서 fail-closed 임을 고정한다.
    out["q2:미바인딩"] = sorted(f"{_local(r.work)}×{int(r.violationCount)}"
                              for r in runs.query(q2))

    # Q3 — 절 묶음. **블록 1개당 1행**(Work 행 복제 금지 — AQ-01) + **입력 필수**(AS-15).
    q3 = (QUERIES / "q3-section-bundle.rq").read_text(encoding="utf-8")
    for number in ("6.1", "3.2"):
        rows3 = list(prod.query(q3, initBindings={"SECTION_NUMBER": Literal(number)}))
        out[f"q3:{number}"] = {"rows": len(rows3),
                               "sections": sorted({str(r.sectionNumber) for r in rows3})}
    out["q3:미바인딩"] = len(list(prod.query(q3)))

    # Q4 — 주입 조립 정렬 키. Work 1건당 1행.
    rows4 = list(prod.query((QUERIES / "q4-injection-order.rq").read_text(encoding="utf-8")))
    out["q4"] = {"rows": len(rows4),
                 "distinct_works": len({str(r.work) for r in rows4}),
                 "with_alias": sorted(_local(r.work) for r in rows4 if str(r.aliases))}
    return out


def main(argv: "list[str] | None" = None) -> int:
    ap = argparse.ArgumentParser(description="질의 카탈로그 골든(T2-4)")
    ap.add_argument("--emit", action="store_true", help="관측값을 골든으로 기록")
    args = ap.parse_args(argv)

    try:
        got = observe()
    except Exception as exc:                                   # noqa: BLE001
        print(f"[query-golden] 재료 결손·질의 실패: {exc}", file=sys.stderr)
        return 1

    if args.emit:
        GOLDEN.write_text(json.dumps(got, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                          encoding="utf-8")
        print(f"[query-golden] 기록 {GOLDEN.relative_to(REPO_ROOT)}")
        return 0

    if not GOLDEN.is_file():
        print(f"[query-golden] 골든 부재: {GOLDEN} — `--emit` 미실행", file=sys.stderr)
        return 1
    want = json.loads(GOLDEN.read_text(encoding="utf-8"))

    diffs: "list[str]" = []
    for key in sorted(set(want) | set(got)):
        if want.get(key) != got.get(key):
            diffs.append(f"{key}: 기대 {want.get(key)} ≠ 실측 {got.get(key)}")

    # 공허 통과 방지 — 양성 절반이 비어 있으면 골든 자체가 무의미하다.
    if not got.get("q2:exp-A"):
        diffs.append("q2:exp-A 가 비었다 — 양성 단언이 성립하지 않는다(공허 통과)")
    if got.get("q2:exp-없음"):
        diffs.append("q2 미등록 런이 결과를 냈다 — run 격리 파손")
    if got.get("q2:미바인딩"):
        diffs.append("q2 가 $RUN 미바인딩에서 결과를 냈다 — 전역 스캔(격리 파손)")
    if got.get("q3:미바인딩"):
        diffs.append("q3 가 $SECTION_NUMBER 미바인딩에서 결과를 냈다 — 전량 반환(입력 계약 파손)")
    if got.get("q3:6.1") == got.get("q3:3.2"):
        diffs.append("q3 가 입력에 따라 다른 부분집합을 내지 않는다(공허 통과)")
    if (got.get("adapter") or {}).get("nodes") != 3:
        diffs.append(f"어댑터가 실런 3사건을 3노드로 굽지 않았다: {got.get('adapter')}")
    if "R-0120×1" not in got.get("q2:exp-A", []) or "R-0120×1" not in got.get("q2:exp-B", []):
        diffs.append("런 간 재발이 양쪽에 보존되지 않는다(어댑터 사건 노드 축 파손)")

    for d in diffs:
        print(f"[query-golden] RED {d}")
    if diffs:
        return 2
    print(f"[query-golden] 질의 {len([k for k in want if not k.startswith('q2:')]) + 1}종 · "
          f"양성·음성 전건 일치 (Q2 런 격리 실증 포함)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
