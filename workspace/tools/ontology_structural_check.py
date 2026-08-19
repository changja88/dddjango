"""구조 검증 — SPARQL 조인 5종 + order 유일성 + kind↔datatype 정합 (T1-6, .venv 전용).

«구조화 이득»의 실물 증명(게이트 2 항목 2): 산문일 때 불가능했던 조인 질의가
그래프 정본 위에서 성립함을 상시 검증한다. 데이터 = rules+wiring+vocab 전량 병합.

① 규칙→담당(enforcedBy∨delegatedTo — 무소유 0) ② 검사기/에이전트→집행 규칙(역조인)
③ 절→블록 순서(절 내 1..n 연속·유일) ④ 규칙→블록→절→문서 역참조(+parentSection 허용)
⑤ Work→현행 Expression 왕복(revision·specializationOf 정합 — 위반 왕복은 골든 Violation로 실증)

사용: PYTHONPATH=workspace/tools .venv/bin/python workspace/tools/ontology_structural_check.py [--report]
exit 0 정합 / 1 위반 / 2 도구 오류
"""
from __future__ import annotations

import argparse
import sys

from ontology_canon import REPO_ROOT

DJR = "https://numchida.com/ns/djr#"
P = f"PREFIX djr: <{DJR}>\nPREFIX prov: <http://www.w3.org/ns/prov#>\nPREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\n"


def load_graph(with_golden: bool):
    from rdflib import Graph

    g = Graph()
    for sub in ("rules", "wiring", "vocab"):
        for f in sorted((REPO_ROOT / "ontology" / sub).glob("*.ttl")):
            g.parse(f, format="turtle")
    if with_golden:
        for f in sorted((REPO_ROOT / "ontology" / "shapes" / "golden").glob("*-valid.ttl")):
            g.parse(f, format="turtle")
    return g


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--report", action="store_true", help="질의 결과 실물 출력(게이트 2 자료)")
    args = ap.parse_args()
    g = load_graph(with_golden=True)
    errors: list[str] = []

    # ① 무소유 Norm 0 (Norm 하위 5클래스 인스턴스 전수)
    q1 = P + """SELECT ?w WHERE {
      ?w a ?cls . ?cls rdfs:subClassOf djr:Norm .
      FILTER NOT EXISTS { ?w djr:enforcedBy ?c } FILTER NOT EXISTS { ?w djr:delegatedTo ?a }
    }"""
    q1 = "PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n" + q1
    unowned = list(g.query(q1))
    if unowned:
        errors.append(f"① 무소유 규범 {len(unowned)}건: {[str(r[0]) for r in unowned[:5]]}")

    # ② 역조인 — 담당별 집행 규칙 수 (질의 성립 자체+report)
    q2 = P + """SELECT ?owner (COUNT(?w) AS ?n) WHERE {
      { ?w djr:enforcedBy ?owner } UNION { ?w djr:delegatedTo ?owner }
    } GROUP BY ?owner ORDER BY DESC(?n)"""
    owners = list(g.query(q2))
    if not owners:
        errors.append("② 역조인 결과 0 — 배선 부재")

    # ③ 절→블록 순서: 절 내 order 유일·1..n 연속
    q3 = P + "SELECT ?s ?o WHERE { ?b djr:inSection ?s ; djr:order ?o }"
    per_section: dict[str, list[int]] = {}
    for s, o in g.query(q3):
        per_section.setdefault(str(s), []).append(int(o))
    for s, orders in sorted(per_section.items()):
        if sorted(orders) != list(range(1, len(orders) + 1)):
            errors.append(f"③ 블록 순서 위반 {s}: {sorted(orders)[:8]}…")

    # ④ 규칙→블록→절→문서 역참조: statesNorm 보유 블록 전부가 문서까지 닿는가
    q4 = P + """SELECT ?w WHERE {
      ?b djr:statesNorm ?w .
      FILTER NOT EXISTS { ?b djr:inSection ?s . ?s djr:inDocument ?d . ?d a djr:Document }
    }"""
    orphan = list(g.query(q4))
    if orphan:
        errors.append(f"④ 문서 역참조 단절 {len(orphan)}건")
    # ④′ 고아 Work: 어떤 블록도 가리키지 않는 Norm 인스턴스(L-H #18 — Work 출발 방향)
    q4b = "PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n" + P + """SELECT ?w WHERE {
      ?w a ?cls . ?cls rdfs:subClassOf djr:Norm .
      FILTER NOT EXISTS { ?b djr:statesNorm ?w }
    }"""
    orphan_w = [r for r in g.query(q4b) if "golden" not in str(r[0])]
    if orphan_w:
        errors.append(f"④′ 고아 Work(블록 미연결) {len(orphan_w)}건: {[str(r[0]).rsplit('#',1)[-1] for r in orphan_w[:5]]}")
    # ⑤′ currentExpression 부재 Work(L-H #19 — 이관 공정 ② 의무)
    q5b = "PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n" + P + """SELECT ?w WHERE {
      ?w a ?cls . ?cls rdfs:subClassOf djr:Norm .
      FILTER NOT EXISTS { ?w djr:currentExpression ?e }
    }"""
    noexpr = [r for r in g.query(q5b) if "golden" not in str(r[0])]
    if noexpr:
        errors.append(f"⑤′ currentExpression 부재 Work {len(noexpr)}건: {[str(r[0]).rsplit('#',1)[-1] for r in noexpr[:5]]}")

    # ⑤ Work→currentExpression 왕복 정합
    q5 = P + """SELECT ?w ?e WHERE {
      ?w djr:currentExpression ?e .
      FILTER NOT EXISTS { ?e a djr:Expression ; djr:revision ?r ; prov:specializationOf ?w }
    }"""
    broken = list(g.query(q5))
    if broken:
        errors.append(f"⑤ Expression 왕복 단절 {len(broken)}건: {[str(r[0]) for r in broken[:5]]}")
    qv = P + """SELECT ?v ?w ?e WHERE {
      ?v a djr:Violation ; djr:violatesWork ?w ; djr:violatesExpression ?e .
      ?e prov:specializationOf ?w }"""
    violations_roundtrip = list(g.query(qv))

    # kind↔datatype 정합 (§16 저작 규약)
    from rdflib import Namespace
    from rdflib.namespace import RDF, XSD
    djr = Namespace(DJR)
    LANG_KINDS = {djr["kind-norm"], djr["kind-prose"], djr["kind-checklist-item"]}
    STR_KINDS = {djr["kind-code"], djr["kind-table-row"]}
    for b in g.subjects(RDF.type, djr.Block):
        kind = next(g.objects(b, djr.kind), None)
        text = next(g.objects(b, djr.text), None)
        if text is None or kind is None:
            continue
        if kind not in LANG_KINDS | STR_KINDS:
            # kind 5종 폐쇄 집합 — 미지 kind 침묵 통과 금지(L-H #20)
            errors.append(f"kind↔datatype: {b} — 미지 kind {kind}(폐쇄 5종 밖)")
            continue
        if kind in LANG_KINDS and text.language != "ko":
            errors.append(f"kind↔datatype: {b} — {kind} 인데 @ko 아님")
        # RDF 1.1: 무표기 문자열 리터럴 ≡ xsd:string (rdflib은 datatype=None으로 정규화)
        if kind in STR_KINDS and not (text.datatype in (None, XSD.string) and text.language is None):
            errors.append(f"kind↔datatype: {b} — {kind} 인데 xsd:string 아님({text.datatype}/{text.language})")

    if args.report:
        n_work = len(set(g.subjects(djr.currentExpression, None)))
        print(f"[structural] Work {n_work} · 절 {len(per_section)} · 담당 개체 {len(owners)}")
        print("[structural] ② 담당별 집행 규칙 수(상위 8):")
        for owner, n in owners[:8]:
            print(f"    {str(owner).replace(DJR, 'djr:')} — {n}")
        print(f"[structural] ⑤ Violation→Work→Expression 왕복(골든 포함): {len(violations_roundtrip)}건 성립")

    for e in errors:
        print(f"[structural] 위반: {e}", file=sys.stderr)
    print(f"[structural] {'정합 — 5종 조인·순서·datatype 전부 성립' if not errors else f'위반 {len(errors)}건'}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
