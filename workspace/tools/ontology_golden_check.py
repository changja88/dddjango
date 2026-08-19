"""골든 페어 red/green 하네스 (T0 A6 — verify-ontology [5]).

shapes/golden/*.ttl 각각을 데이터 그래프(골든+vocab+wiring 병합)로 SHACL 검증하고,
파일명 접미(-valid/-invalid)가 선언한 기대 판정과 대조한다(E4 — 골든은 ④ 대신 기대 판정 대조).
판정 = 리포트 그래프의 sh:Violation 계수(0 == green).

사용: .venv/bin/python workspace/tools/ontology_golden_check.py [--root <온톨로지 루트>]
exit 0 = 전 골든 기대 일치 / 1 = 불일치 존재
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ontology_gate import DEFAULT_ROOT, SEVERITY_QUERY, merged_data_graph, shapes_graph


def violation_count(report_graph) -> int:
    for severity, n in report_graph.query(SEVERITY_QUERY):
        if str(severity).endswith("#Violation"):
            return int(n)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="골든 페어 red/green 하네스")
    ap.add_argument("--root", default=str(DEFAULT_ROOT))
    args = ap.parse_args()
    root = Path(args.root).resolve()

    from pyshacl import validate
    from rdflib import Graph

    shp = shapes_graph(root)
    if shp is None:
        print("[ontology-golden] 도구 오류: shapes/ 비어 있음")
        return 2

    goldens = sorted((root / "shapes" / "golden").glob("*.ttl"))
    if not goldens:
        print("[ontology-golden] 도구 오류: golden 페어 없음")
        return 2

    mismatches = 0
    for path in goldens:
        name = path.stem
        if name.endswith("-valid"):
            expect_green = True
        elif name.endswith("-invalid"):
            expect_green = False
        else:
            print(f"[ontology-golden] RED   {path.name}: 접미 규약(-valid/-invalid) 위반")
            mismatches += 1
            continue

        g = Graph()
        g.parse(path, format="turtle")
        data = merged_data_graph(g, path, root)
        _, report_graph, _ = validate(
            data_graph=data, shacl_graph=shp, inference="none", advanced=True
        )
        actual_green = violation_count(report_graph) == 0
        ok = actual_green == expect_green
        mark = "ok " if ok else "RED"
        detail = "green" if actual_green else "red"
        print(f"[ontology-golden] {mark}  {path.name}: 기대 {'green' if expect_green else 'red'} → 실제 {detail}")
        if not ok:
            mismatches += 1

    print(f"[ontology-golden] {len(goldens)}골든 — 불일치 {mismatches}")
    return 1 if mismatches else 0


if __name__ == "__main__":
    sys.exit(main())
