"""SHACL 본검증 — 코퍼스 전량 병합 1회 (T0 A8 — verify-ontology [3]).

게이트 ④(파일 단위+vocab/wiring 병합)와 달리 vocab+rules+wiring 전량을 한 데이터
그래프로 병합해 검증한다 — rules/ 파일 사이의 교차 참조가 있는 T1 이후에 파일 단위
검증이 놓치는 결손(참조 대상 부재 등)을 잡는 자리. 판정은 리포트 그래프 질의(E3).

사용: .venv/bin/python workspace/tools/ontology_shacl_full.py [--root R]
exit 0 = sh:Violation 0 / 1 = 위반 존재 / 2 = 도구 오류
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ontology_gate import DEFAULT_ROOT, SEVERITY_QUERY, shapes_graph


def main() -> int:
    ap = argparse.ArgumentParser(description="SHACL 본검증(전량 병합)")
    ap.add_argument("--root", default=str(DEFAULT_ROOT))
    args = ap.parse_args()
    root = Path(args.root).resolve()

    from pyshacl import validate
    from rdflib import Graph

    shp = shapes_graph(root)
    if shp is None:
        print("[shacl-full] 도구 오류: shapes/ 비어 있음")
        return 2

    data = Graph()
    n_files = 0
    for sub in ("vocab", "rules", "wiring"):
        d = root / sub
        if d.is_dir():
            for f in sorted(d.glob("*.ttl")):
                data.parse(f, format="turtle")
                n_files += 1

    _, report_graph, _ = validate(
        data_graph=data, shacl_graph=shp, inference="none", advanced=True
    )
    counts = {}
    for severity, n in report_graph.query(SEVERITY_QUERY):
        counts[str(severity).rsplit("#", 1)[-1]] = int(n)
    violations = counts.get("Violation", 0)
    summary = " · ".join(f"{k} {v}" for k, v in sorted(counts.items())) or "위반 없음"
    print(f"[shacl-full] 데이터 {n_files}파일 병합 — {summary}")
    return 1 if violations else 0


if __name__ == "__main__":
    sys.exit(main())
