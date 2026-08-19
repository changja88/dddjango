"""meta-SHACL 2층 게이트 (T0 A6 — verify-ontology [2], 블루프린트 E3).

1층 = 표준 SHACL-SHACL(문법 — REC 부록 C, pySHACL meta_shacl. 커버리지는 SHACL 문법의
부분집합임을 자인 — T0 적대 리뷰 L1-1).
2층 = 하우스 메타셰이프(ontology/shapes/meta-house.ttl — E3·E4 규율: sh:closed 말단 한정·
closed 의 ignoredProperties(rdf:type) 의무·셰이프 노드 IRI 의무). 데이터 그래프 =
shapes 전체 + vocab 병합(클래스 계층 조회 — E2와 동일 규칙).

사용: .venv/bin/python workspace/tools/ontology_meta_shacl.py [--root <온톨로지 루트>]
exit 0 = 2층 전부 green / 1 = red / 2 = 도구 오류
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ontology_gate import DEFAULT_ROOT, SEVERITY_QUERY


def main() -> int:
    ap = argparse.ArgumentParser(description="meta-SHACL 2층 게이트")
    ap.add_argument("--root", default=str(DEFAULT_ROOT))
    args = ap.parse_args()
    root = Path(args.root).resolve()

    from pyshacl import validate
    from rdflib import Graph

    shape_files = sorted((root / "shapes").glob("*.ttl"))
    if not shape_files:
        print("[meta-shacl] 도구 오류: shapes/ 비어 있음")
        return 2

    all_shapes = Graph()
    for f in shape_files:
        all_shapes.parse(f, format="turtle")

    failed = False

    try:
        validate(
            data_graph=Graph(),
            shacl_graph=all_shapes,
            inference="none",
            meta_shacl=True,
        )
        print(f"[meta-shacl] 1층(SHACL-SHACL) green — 셰이프 파일 {len(shape_files)}개")
    except Exception as exc:
        print(f"[meta-shacl] 1층(SHACL-SHACL) RED — {exc}")
        failed = True

    meta_house = root / "shapes" / "meta-house.ttl"
    if not meta_house.exists():
        print("[meta-shacl] 도구 오류: meta-house.ttl 부재(2층 하우스 메타셰이프)")
        return 2
    house = Graph()
    house.parse(meta_house, format="turtle")

    data = Graph()
    for triple in all_shapes:
        data.add(triple)
    for vf in sorted((root / "vocab").glob("*.ttl")):
        data.parse(vf, format="turtle")

    _, report_graph, _ = validate(
        data_graph=data, shacl_graph=house, inference="none", advanced=True
    )
    violations = 0
    for severity, n in report_graph.query(SEVERITY_QUERY):
        if str(severity).endswith("#Violation"):
            violations = int(n)
    if violations:
        print(f"[meta-shacl] 2층(하우스) RED — sh:Violation {violations}건")
        for line in report_graph.serialize(format="nt").splitlines():
            if "resultMessage" in line:
                print(f"    {line.strip()}")
        failed = True
    else:
        print("[meta-shacl] 2층(하우스) green")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
