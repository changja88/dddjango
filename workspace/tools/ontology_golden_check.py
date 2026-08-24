"""골든 페어 red/green 하네스 (T0 A6 — verify-ontology [5]).

shapes/golden/*.ttl 각각을 데이터 그래프(골든+vocab+wiring 병합)로 SHACL 검증하고,
파일명 접미(-valid/-invalid)가 선언한 기대 판정과 대조한다(E4 — 골든은 ④ 대신 기대 판정 대조).
판정 = 리포트 그래프의 sh:Violation 계수(0 == green).

사용: .venv/bin/python workspace/tools/ontology_golden_check.py [--root <온톨로지 루트>]
exit 0 = 전 골든 기대 일치 / 1 = 불일치 존재
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from ontology_gate import DEFAULT_ROOT, SEVERITY_QUERY, merged_data_graph, shapes_graph


def violation_count(report_graph) -> int:
    for severity, n in report_graph.query(SEVERITY_QUERY):
        if str(severity).endswith("#Violation"):
            return int(n)
    return 0


def _golden_job(job: tuple) -> bool:
    """프로세스 풀 워커 — 골든 1건의 SHACL 판정(green 여부)을 돌려준다."""
    path_str, root_str = job
    from pyshacl import validate
    from rdflib import Graph

    path, root = Path(path_str), Path(root_str)
    g = Graph()
    g.parse(path, format="turtle")
    data = merged_data_graph(g, path, root)
    _, report_graph, _ = validate(
        data_graph=data, shacl_graph=shapes_graph(root), inference="none", advanced=True
    )
    return violation_count(report_graph) == 0


def main() -> int:
    ap = argparse.ArgumentParser(description="골든 페어 red/green 하네스")
    ap.add_argument("--root", default=str(DEFAULT_ROOT))
    args = ap.parse_args()
    root = Path(args.root).resolve()

    shp = shapes_graph(root)
    if shp is None:
        print("[ontology-golden] 도구 오류: shapes/ 비어 있음")
        return 2

    goldens = sorted((root / "shapes" / "golden").glob("*.ttl"))
    if not goldens:
        print("[ontology-golden] 도구 오류: golden 페어 없음")
        return 2

    expectations: list[tuple[Path, bool | None]] = []
    for path in goldens:
        name = path.stem
        if name.endswith("-valid"):
            expectations.append((path, True))
        elif name.endswith("-invalid"):
            expectations.append((path, False))
        else:
            expectations.append((path, None))

    # 골든은 서로 독립 — 파일 단위 병렬(결과는 제출 순서로 수집 → 출력 결정론 유지).
    # 소수 골든이면 풀 기동 비용이 더 커서 순차.
    jobs = [(str(p), str(root)) for p, expect in expectations if expect is not None]
    workers = min(len(jobs), os.cpu_count() or 1)
    if workers < 2 or len(jobs) < 4:
        verdicts = [_golden_job(j) for j in jobs]
    else:
        from concurrent.futures import ProcessPoolExecutor

        with ProcessPoolExecutor(max_workers=workers) as ex:
            verdicts = list(ex.map(_golden_job, jobs))

    verdict_iter = iter(verdicts)
    mismatches = 0
    for path, expect_green in expectations:
        if expect_green is None:
            print(f"[ontology-golden] RED   {path.name}: 접미 규약(-valid/-invalid) 위반")
            mismatches += 1
            continue
        actual_green = next(verdict_iter)
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
