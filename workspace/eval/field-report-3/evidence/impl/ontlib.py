"""fr3 온톨로지 편집 헬퍼 — 수리 2 edit.py 판형 + 날짜 접미(b)·kind 지정·새 섹션·LEDGER·소스 미러."""
import sys, csv, hashlib, pathlib, subprocess
sys.path.insert(0, "workspace/tools")
from rdflib import Graph, URIRef, Literal, Namespace, RDF
from rdflib.namespace import SKOS, XSD
from ontology_canon import canon_turtle, load_prefix_registry
from ontology_census import parse_sections
from ontology_render_sync import strip_marker
reg = load_prefix_registry()
DJR = Namespace("https://numchida.com/ns/djr#"); PROV = Namespace("http://www.w3.org/ns/prov#")
DATE = "2026-09-04"
MAN = "workspace/design/2026-08-19-ontology-t1-census/corpus-manifest.tsv"
PATHS = {r["doc_key"]: r["path"] for r in csv.DictReader(open(MAN, encoding="utf-8"), delimiter="\t")}

def S(p): return URIRef("https://numchida.com/ns/djr#s/" + p)
def D(p): return URIRef("https://numchida.com/ns/djr#d/" + p)
def load(rel):
    p = pathlib.Path("ontology")/rel; g = Graph(); g.parse(data=p.read_text(encoding="utf-8"), format="turtle"); return p, g
def save(p, g): p.write_text(canon_turtle(g, reg, allow_lists=False), encoding="utf-8")
def text_of(g, b): return str(next(g.objects(b, DJR.text)))
def _lit(text, lang): return Literal(text, lang="ko") if lang else Literal(text, datatype=XSD.string) if False else Literal(text)
def set_text(g, b, new):
    old = next(g.objects(b, DJR.text)); g.remove((b, DJR.text, old))
    g.add((b, DJR.text, Literal(new, lang="ko") if old.language == "ko" else Literal(new)))
def replace_in(g, b, old, new):
    t = text_of(g, b); assert t.count(old) == 1, (str(b)[-40:], old[:50], t.count(old)); set_text(g, b, t.replace(old, new))
def expr_iri(rid, date=DATE, suffix=""): return URIRef(f"https://numchida.com/ns/djr#{rid}@{date}{suffix}")
def new_work(g, rid, kind, label, date=DATE):
    w = DJR[rid]; assert (w, None, None) not in g, rid
    g.add((w, RDF.type, DJR[kind])); g.add((w, SKOS.prefLabel, Literal(label, lang="ko")))
    e = expr_iri(rid, date); g.add((w, DJR.currentExpression, e)); g.add((e, RDF.type, DJR.Expression)); g.add((e, PROV.specializationOf, w)); g.add((e, DJR.revision, Literal(1)))
def revise(g, rid, label, kind="amendment", date=DATE):
    """같은 날 2차 개정이면 접미 b(선례 @2026-09-03b)."""
    w = DJR[rid]; cur = next(g.objects(w, DJR.currentExpression)); rev = int(next(g.objects(cur, DJR.revision)))
    e = expr_iri(rid, date)
    if (e, None, None) in g or str(cur) == str(e): e = expr_iri(rid, date, "b"); assert (e, None, None) not in g, e
    g.add((e, RDF.type, DJR.Expression)); g.add((e, PROV.specializationOf, w)); g.add((e, PROV.wasRevisionOf, cur)); g.add((e, DJR.revision, Literal(rev+1))); g.add((e, DJR.revisionKind, DJR["revision-"+kind]))
    g.remove((w, DJR.currentExpression, cur)); g.add((w, DJR.currentExpression, e))
    old = next(g.objects(w, SKOS.prefLabel)); g.remove((w, SKOS.prefLabel, old)); g.add((w, SKOS.prefLabel, Literal(label, lang="ko")))
    print(f"  {rid}: rev {rev} -> {rev+1} ({kind}) {str(e).rsplit('@',1)[1]}")
def new_block(g, sec, n, text, norms=(), kind="norm"):
    """kind: norm(@ko) · code(@ko) · prose(@ko) · table-row(xsd:string)."""
    b = URIRef(str(sec)+f"/b{n}"); assert (b, None, None) not in g, b
    prev = URIRef(str(sec)+f"/b{n-1}"); assert n == 1 or (prev, DJR.order, Literal(n-1)) in g, ("order 불연속", b)
    g.add((b, RDF.type, DJR.Block)); g.add((b, DJR.inSection, sec)); g.add((b, DJR.kind, DJR["kind-"+kind])); g.add((b, DJR.order, Literal(n)))
    for r in norms: g.add((b, DJR.statesNorm, DJR[r]))
    g.add((b, DJR.text, Literal(text) if kind == "table-row" else Literal(text, lang="ko")))
    return b
def new_section(g, doc_path, key, heading, number=None):
    """문서 말미 새 절 — 9ef6c4f 선례(headingSnapshot·inDocument·sectionOwner[·sectionNumber])."""
    sec = S(doc_path + "/" + key); assert (sec, None, None) not in g, sec
    g.add((sec, RDF.type, DJR.Section)); g.add((sec, DJR.headingSnapshot, Literal(heading, lang="ko")))
    g.add((sec, DJR.inDocument, D(doc_path))); g.add((sec, DJR.sectionOwner, DJR["owner-graph"]))
    if number: g.add((sec, DJR.sectionNumber, Literal(number)))
    return sec
def wire(rel, triples):
    p, g = load("wiring/"+rel)
    for s, pred, o in triples:
        t = (DJR[s], DJR[pred], URIRef("https://numchida.com/ns/djr#"+o)); assert t not in g, t; g.add(t)
    save(p, g); print("wiring", rel, "+", len(triples))
def issued(rows, date=DATE):
    f = pathlib.Path("ontology/ISSUED"); s = f.read_text(encoding="utf-8"); assert s.endswith("\n")
    for r, _ in rows: assert f"\n{r}\t" not in s and not s.startswith(f"{r}\t"), r
    f.write_text(s + "".join(f"{r}\t{date}\t{fp}\n" for r, fp in rows), encoding="utf-8"); print("ISSUED +", len(rows))
def _span(data, sk):
    secs = [s for s in parse_sections(data) if (f"s{s['ordinal']:03d}" + (f"-{s['anchor']}" if s.get('anchor') else "")) == sk]
    assert len(secs) == 1, (sk, [(s['ordinal'], s.get('anchor')) for s in parse_sections(data)][-6:]); return strip_marker(secs[0]["span"])
def ledger(targets, tag="rebaseline", batch="현장 보고 3", date=DATE):
    """targets: [(doc_key, section_key, kind('graph'|'prose'), why)]"""
    led = pathlib.Path("ontology/LEDGER.tsv"); out = []
    for dk, sk, kind, why in targets:
        h = hashlib.sha256(_span(pathlib.Path(PATHS[dk]).read_bytes(), sk)).hexdigest()
        out.append(f"{dk}\t{sk}\t{h}\t{kind}\t-\t-\t-\t-\t{tag}:{date} {batch} — {why}\n"); print(dk, sk, kind, h[:12])
    led.write_text(led.read_text(encoding="utf-8") + "".join(out), encoding="utf-8"); print("LEDGER +", len(out))
def srcmirror(targets):
    """targets: [(skill, section_key)] — 배포 final.md 의 HEAD span → 현재 span 으로 소스 미러 교체."""
    for skill, sk in targets:
        dep = f"dddjango/skills/{skill}/references/final.md"
        old = _span(subprocess.run(["git","show",f"HEAD:{dep}"],capture_output=True,check=True).stdout, sk)
        new = _span(pathlib.Path(dep).read_bytes(), sk)
        src = pathlib.Path(f"workspace/reference/{skill}/reference/final.md"); data = src.read_bytes()
        assert data.count(old) == 1, (skill, sk, data.count(old)); src.write_bytes(data.replace(old, new)); print("swap", skill, sk, len(old), "->", len(new))
