"""계층 병합 검사 + 셰이프별 적용 대상 계수 회귀 (T0 A7 — 블루프린트 E2, verify-ontology [4]).

vocab+rules+wiring(+옵션: 골든)을 병합한 데이터 그래프에서 각 NodeShape 의
sh:targetClass 적용 대상 수(rdf:type + rdfs:subClassOf* 폐포)를 세어 기대표와 대조한다.
계층 트리플 병합 누락·타깃 오타에 의한 침묵 미적용을 계수 급감으로 검출한다(E2 처방).

T0 시점 rules/ 가 비어 있어 --with-golden 으로 골든 그래프를 데이터로 병합해
기전을 증명한다(계수 기대표 실가동은 T1부터 — T0 계획 A7).
기대표: workspace/eval/fixtures/ontology_gate/target-counts.json (의도 변경 시 함께 갱신).

사용: .venv/bin/python workspace/tools/ontology_hierarchy_check.py [--root R] [--with-golden]
exit 0 = 기대 일치 / 1 = 불일치 / 2 = 도구 오류
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from ontology_canon import REPO_ROOT
from ontology_gate import DEFAULT_ROOT

EXPECTED_JSON = REPO_ROOT / "workspace" / "eval" / "fixtures" / "ontology_gate" / "target-counts.json"

SH = "http://www.w3.org/ns/shacl#"
RDF_TYPE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
SUBCLASS = "http://www.w3.org/2000/01/rdf-schema#subClassOf"

COUNT_QUERY = f"""
SELECT ?shape ?cls (COUNT(DISTINCT ?node) AS ?n) WHERE {{
    ?shape <{SH}targetClass> ?cls .
    OPTIONAL {{ ?node <{RDF_TYPE}>/<{SUBCLASS}>* ?cls . }}
}} GROUP BY ?shape ?cls
"""


def main() -> int:
    ap = argparse.ArgumentParser(description="계층 병합·적용 대상 계수 회귀")
    ap.add_argument("--root", default=str(DEFAULT_ROOT))
    ap.add_argument("--with-golden", action="store_true", help="골든 그래프를 데이터로 병합(T0 기전 증명)")
    ap.add_argument("--emit", action="store_true", help="기대표 JSON 을 stdout 으로 방출(갱신용)")
    ap.add_argument("--expected", default=str(EXPECTED_JSON))
    args = ap.parse_args()
    root = Path(args.root).resolve()

    from rdflib import Graph

    shapes = Graph()
    for f in sorted((root / "shapes").glob("*.ttl")):
        shapes.parse(f, format="turtle")

    data = Graph()
    for sub in ("vocab", "rules", "wiring"):
        d = root / sub
        if d.is_dir():
            for f in sorted(d.glob("*.ttl")):
                data.parse(f, format="turtle")
    if args.with_golden:
        for f in sorted((root / "shapes" / "golden").glob("*.ttl")):
            data.parse(f, format="turtle")

    merged = Graph()
    for t in shapes:
        merged.add(t)
    for t in data:
        merged.add(t)

    counts: dict[str, int] = {}
    for shape, _cls, n in merged.query(COUNT_QUERY):
        local = str(shape).rsplit("#", 1)[-1]
        counts[local] = counts.get(local, 0) + int(n)

    if args.emit:
        print(json.dumps(dict(sorted(counts.items())), ensure_ascii=False, indent=2))
        return 0

    expected_path = Path(args.expected)
    if not expected_path.exists():
        print(f"[hierarchy] 도구 오류: 기대표 부재 — {expected_path} (--emit 으로 생성)")
        return 2
    expected = json.loads(expected_path.read_text(encoding="utf-8"))

    mismatches = []
    for shape_name in sorted(set(expected) | set(counts)):
        exp, got = expected.get(shape_name), counts.get(shape_name)
        if exp != got:
            mismatches.append((shape_name, exp, got))
    for shape_name, exp, got in mismatches:
        print(f"[hierarchy] RED {shape_name}: 기대 {exp} → 실제 {got}")
    status = f"[hierarchy] 셰이프 {len(counts)}종 — 불일치 {len(mismatches)}"
    print(status + ("" if mismatches else " (계층 병합·타깃 계수 green)"))
    return 1 if mismatches else 0


if __name__ == "__main__":
    sys.exit(main())
