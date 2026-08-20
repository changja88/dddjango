"""구조 검증 — SPARQL 조인 5종 + order 유일성 + kind↔datatype 정합 (T1-6, .venv 전용).

«구조화 이득»의 실물 증명(게이트 2 항목 2): 산문일 때 불가능했던 조인 질의가
그래프 정본 위에서 성립함을 상시 검증한다. 데이터 = rules+wiring+vocab 전량 병합.

① 규칙→담당(enforcedBy∨delegatedTo — 무소유 0) ② 검사기/에이전트→집행 규칙(역조인)
③ 절→블록 순서(절 내 1..n 연속·유일) ④ 규칙→블록→절→문서 역참조(+parentSection 허용)
⑤ Work→현행 Expression 왕복(revision·specializationOf 정합 — 위반 왕복은 골든 Violation로 실증)
⑥ alias 함수성(동일 aliasText → 복수 Work 금지) ⑥′ 해소 4조건(채번 형식·ISSUED 발행·
  currentExpression 1·Expression 왕복) ⑥″ 문법(`rule#N` 동결 문법+규칙 원장 실재) — 전부 fail-closed

⑥ 는 SHACL 로 대체 불가다 — `AliasEntryShape-aliasFor maxCount 1` 은 **노드 단위**라 «같은
aliasText 를 가진 AliasEntry 두 노드»를 보지 못한다(교차 노드 유일성 미지원). 판정 근거는
T2-2 귀속 판단표(`workspace/design/2026-08-20-ontology-t2-2-alias-ledger.md`) §4.

사용: PYTHONPATH=workspace/tools .venv/bin/python workspace/tools/ontology_structural_check.py
        [--report] [--self-test] [--root <저장소 루트>]
exit 0 정합 / 1 위반 / 2 도구 오류
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from ontology_canon import REPO_ROOT

DJR = "https://numchida.com/ns/djr#"
P = f"PREFIX djr: <{DJR}>\nPREFIX prov: <http://www.w3.org/ns/prov#>\nPREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\n"


def load_graph(with_golden: bool, root: "Path | None" = None):
    from rdflib import Graph

    base: Path = root or REPO_ROOT
    g = Graph()
    for sub in ("rules", "wiring", "vocab"):
        for f in sorted((base / "ontology" / sub).glob("*.ttl")):
            g.parse(f, format="turtle")
    if with_golden:
        for f in sorted((base / "ontology" / "shapes" / "golden").glob("*-valid.ttl")):
            g.parse(f, format="turtle")
    return g


def _namespaces():
    from rdflib import Namespace
    from rdflib.namespace import PROV, RDF

    return Namespace(DJR), RDF, PROV


_DJR_NS, _RDF_NS, _PROV_NS = _namespaces()


_ALIAS_TEXT_RE = re.compile(r"^rule#[1-9][0-9]*$")   # v2 동결 문법(비한정 «#N»·전치 0 금지)
_WORK_IRI_RE = re.compile(r"#R-\d{4}$")              # 채번 대장 형식
_OWNER_ROW_RE = re.compile(r"^\|\s*(\d+)\s*\|", re.MULTILINE)


def _issued_ids(root: Path) -> "set[str]":
    f = root / "ontology" / "ISSUED"
    if not f.is_file():
        raise FileNotFoundError(f"재료 결손: {f} 부재 — alias 해소 검사 불가")
    return {ln.split("\t", 1)[0] for ln in f.read_text(encoding="utf-8").splitlines() if ln.strip()}


def _rule_numbers(root: Path) -> "set[str]":
    f = root / "workspace" / "plan" / "2026-08-11-rule-owner-map.md"
    if not f.is_file():
        raise FileNotFoundError(f"재료 결손: {f} 부재 — alias 문법 대조 불가")
    return set(_OWNER_ROW_RE.findall(f.read_text(encoding="utf-8")))


def alias_errors(g, issued: "set[str]", rule_numbers: "set[str]") -> "list[str]":
    """⑥·⑥′·⑥″ — alias 대장 무결성(T2-2 · 리뷰 레인 AL 중재 반영).

    **골든 이름 기반 제외를 쓰지 않는다**(AL-5 blocker — `golden` 부분문자열이 생산
    위반의 우회구였다·실증). 호출자가 `load_graph(with_golden=False)` 로 «생산 그래프»를
    넘긴다. 해소 판정은 폐포 소속이 아니라 **채번·발행·판본 왕복**을 요구한다(AL-6).
    """
    out: "list[str]" = []
    # ⑥ 함수성: 같은 aliasText 가 서로 다른 Work 를 가리키면 위반(v3 E6 «모순 카탈로그»).
    q6 = P + """SELECT ?t (COUNT(DISTINCT ?w) AS ?n) WHERE {
      ?a a djr:AliasEntry ; djr:aliasText ?t ; djr:aliasFor ?w .
    } GROUP BY ?t HAVING (COUNT(DISTINCT ?w) > 1)"""
    dup = list(g.query(q6))
    if dup:
        out.append("⑥ alias 함수성 위반 %d건: %s"
                   % (len(dup), ", ".join(f"{r[0]}→{int(r[1])}Work" for r in dup[:5])))
    # ⑥′ 해소 4조건 · ⑥″ 문법 — 엔트리 단위 순회(질의보다 사유가 또렷하다).
    q_all = P + """SELECT ?a ?t ?w WHERE { ?a a djr:AliasEntry ; djr:aliasText ?t ; djr:aliasFor ?w }"""
    bad_res: "list[str]" = []
    bad_syn: "list[str]" = []
    for a, t, w in g.query(q_all):
        name = str(a).rsplit("#", 1)[-1]
        text, work = str(t), str(w)
        if not _ALIAS_TEXT_RE.match(text):
            bad_syn.append(f"{name}:{text!r}(문법)")
        elif text.split("#", 1)[1] not in rule_numbers:
            bad_syn.append(f"{name}:{text!r}(원장 미실재)")
        m = _WORK_IRI_RE.search(work)
        if m is None:
            bad_res.append(f"{name}→{work.rsplit('#', 1)[-1]}(채번 형식 아님)")
            continue
        rid = m.group(0).lstrip("#")
        if rid not in issued:
            bad_res.append(f"{name}→{rid}(ISSUED 미발행)")
            continue
        exprs = list(g.objects(w, _DJR_NS.currentExpression))
        if len(exprs) != 1:
            bad_res.append(f"{name}→{rid}(currentExpression {len(exprs)}개)")
            continue
        e = exprs[0]
        if (e, _RDF_NS.type, _DJR_NS.Expression) not in g \
                or (e, _PROV_NS.specializationOf, w) not in g \
                or not list(g.objects(e, _DJR_NS.revision)):
            bad_res.append(f"{name}→{rid}(Expression 왕복 단절)")
    if bad_res:
        out.append(f"⑥′ 미해소 alias {len(bad_res)}건: {bad_res[:5]}")
    if bad_syn:
        out.append(f"⑥″ alias 문법 위반 {len(bad_syn)}건: {bad_syn[:5]}")
    return out


# ── end-to-end red-first 하네스(리뷰 AL-8) ──────────────────────────────────
# 메모리 그래프가 아니라 «임시 정본 트리»(ontology/{rules,wiring,vocab}+ISSUED+원장)를
# 만들고 결함 fixture 를 넣어 **프로그램 exit** 를 단언한다 — 검사가 실제 실행 경로에서
# 무는지의 증명(helper 단위 호출만으로는 병합 범위·재료 로딩을 통과하지 못한다).
_ST_WORKS = """@prefix djr: <{ns}> .
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .

djr:R-9001 a djr:Obligation ;
    skos:prefLabel "자기검사 규범 1"@ko ;
    djr:currentExpression <{ns}R-9001@2026-08-20> .

<{ns}R-9001@2026-08-20> a djr:Expression ;
    djr:revision "2026-08-20" ;
    prov:specializationOf djr:R-9001 .

djr:R-9002 a djr:Prohibition ;
    skos:prefLabel "자기검사 규범 2"@ko ;
    djr:currentExpression <{ns}R-9002@2026-08-20> .

<{ns}R-9002@2026-08-20> a djr:Expression ;
    djr:revision "2026-08-20" ;
    prov:specializationOf djr:R-9002 .

djr:R-9003 a djr:Obligation ;
    skos:prefLabel "판본 없는 규범"@ko .
"""


def _st_alias(local: str, work: str, text: str) -> str:
    return (f"@prefix djr: <{DJR}> .\n\ndjr:{local} a djr:AliasEntry ;\n"
            f"    djr:aliasFor djr:{work} ;\n    djr:aliasText \"{text}\" ;\n"
            f"    djr:aliasType djr:alias-unique .\n")


_ST_CASES: "tuple[tuple[str, str, bool], ...]" = (
    # (이름, wiring 에 추가할 alias ttl, red 기대)
    ("정상 대조군(rule#3→R-9001)", _st_alias("st-ok", "R-9001", "rule#3"), False),
    ("⑥ 함수성 — 같은 텍스트 두 Work",
     _st_alias("st-d1", "R-9001", "rule#5") + "\n" + _st_alias("st-d2", "R-9002", "rule#5"), True),
    ("⑥ 우회 시도 — IRI 에 golden 포함",
     _st_alias("alias-golden-bypass", "R-9001", "rule#5") + "\n" + _st_alias("st-plain", "R-9002", "rule#5"),
     True),
    ("⑥′ 미발행 Work(ISSUED 밖)", _st_alias("st-bare", "R-9002", "rule#3"), True),
    ("⑥′ 판본 없는 Work(currentExpression 0)", _st_alias("st-noexpr", "R-9003", "rule#3"), True),
    ("⑥′ 채번 형식 아님", _st_alias("st-notwork", "not-a-work", "rule#3"), True),
    ("⑥″ 비한정 문법(#10)", _st_alias("st-bare-hash", "R-9001", "#10"), True),
    ("⑥″ 전치 0(rule#010)", _st_alias("st-zero", "R-9001", "rule#010"), True),
    ("⑥″ 원장 미실재 번호(rule#99999)", _st_alias("st-ghost", "R-9001", "rule#99999"), True),
)


def _st_tree(td: "Path", alias_ttl: "str | None") -> "Path":
    root = td / "repo"
    for sub in ("rules", "wiring", "vocab"):
        (root / "ontology" / sub).mkdir(parents=True, exist_ok=True)
    for f in sorted((REPO_ROOT / "ontology" / "vocab").glob("*.ttl")):
        (root / "ontology" / "vocab" / f.name).write_text(f.read_text(encoding="utf-8"), encoding="utf-8")
    (root / "ontology" / "rules" / "st.ttl").write_text(_ST_WORKS.format(ns=DJR), encoding="utf-8")
    if alias_ttl:
        (root / "ontology" / "wiring" / "aliases.ttl").write_text(alias_ttl, encoding="utf-8")
    # ISSUED — R-9001·R-9003 만 발행(R-9002 는 «미발행 Work» 축의 재료)
    (root / "ontology" / "ISSUED").write_text(
        "R-9001\t2026-08-20\trules/st.ttl\nR-9003\t2026-08-20\trules/st.ttl\n", encoding="utf-8")
    plan = root / "workspace" / "plan"
    plan.mkdir(parents=True, exist_ok=True)
    (plan / "2026-08-11-rule-owner-map.md").write_text(
        "| 3 | path | x |\n| 5 | path | x |\n| 10 | path | x |\n", encoding="utf-8")
    return root


def self_test() -> int:
    import tempfile

    rows: "list[tuple[str, bool, str]]" = []
    with tempfile.TemporaryDirectory() as td:
        for name, ttl, want_red in _ST_CASES:
            root = _st_tree(Path(td) / name.replace(" ", "_")[:24], ttl)
            g = load_graph(with_golden=False, root=root)
            errs = alias_errors(g, _issued_ids(root), _rule_numbers(root))
            ok = bool(errs) == want_red
            rows.append((name, ok, ("red: " + "; ".join(errs)[:70]) if errs else "green"))
    print("| self-test 단언(임시 정본 트리 end-to-end) | 판정 | 실측 |")
    print("|---|---|---|")
    for name, ok, detail in rows:
        print(f"| {name} | {'✓' if ok else '✗'} | {detail} |")
    failed = [n for n, ok, _d in rows if not ok]
    if failed:
        print(f"[structural] self-test 실패: {failed}", file=sys.stderr)
        return 2
    print(f"[structural] self-test 통과: ⑥·⑥′·⑥″ 검출력 {len(rows)}/{len(rows)} 실증"
          " (golden 이름 우회·미발행·판본 부재·문법 전건)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--report", action="store_true", help="질의 결과 실물 출력(게이트 2 자료)")
    ap.add_argument("--self-test", action="store_true",
                    help="임시 정본 트리 end-to-end 로 ⑥·⑥′·⑥″ 검출력 실증(정본 무접촉)")
    ap.add_argument("--root", default="", help="검사 대상 저장소 루트(기본: 이 저장소)")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    root = Path(args.root).resolve() if args.root else REPO_ROOT
    g = load_graph(with_golden=True, root=root)
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

    # ⑥·⑥′·⑥″ alias 대장 무결성(T2-2 — fail-closed). 생산 그래프(골든 제외)에서 잰다:
    # 이름 기반 골든 필터는 우회구였다(리뷰 AL-5 실증) — 병합 자체를 하지 않는다.
    g_prod = load_graph(with_golden=False, root=root)
    errors += alias_errors(g_prod, _issued_ids(root), _rule_numbers(root))
    q_alias = P + """SELECT ?t ?w WHERE { ?a a djr:AliasEntry ; djr:aliasText ?t ; djr:aliasFor ?w }"""
    alias_rows = sorted((str(r[0]), str(r[1]).rsplit("#", 1)[-1]) for r in g_prod.query(q_alias))

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
        print(f"[structural] ⑥ alias 대장 {len(alias_rows)}건 · 해소 Work {len({w for _t, w in alias_rows})}종"
              f" — 미등재 #N(조인 불가·T3 이월)은 판단표 §2·§5 소유"
              f"{': ' + ', '.join(f'{t}→{w}' for t, w in alias_rows[:8]) if alias_rows else ''}")

    for e in errors:
        print(f"[structural] 위반: {e}", file=sys.stderr)
    print(f"[structural] {'정합 — 6종 조인·순서·datatype·alias 전부 성립' if not errors else f'위반 {len(errors)}건'}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
