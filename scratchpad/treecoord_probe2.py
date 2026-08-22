"""처분안 A 재실측 — 블록 IRI 충돌 회피(전 블록 재구성)."""
import sys
sys.path.insert(0, "/Users/hyun/Desktop/dddjango/workspace/tools")
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF
from ontology_canon import REPO_ROOT, frag_encode
from ontology_census import parse_sections
import ontology_render as R

DJR = R.DJR; djr = Namespace(DJR)
path = "dddjango/skills/discipline-houserules/references/final.md"
g = Graph(); g.parse(REPO_ROOT/"ontology/rules/discipline-houserules-final.ttl", format="turtle")
sec = URIRef(f"{DJR}s/{frag_encode(path)}/s004-1")
old = sorted(((int(next(g.objects(b, djr.order))), b) for b in g.subjects(djr.inSection, sec)))
texts = [(o, str(next(g.objects(b, djr.text))), next(g.objects(b, djr.kind))) for o, b in old]
lines = texts[2][1].splitlines(keepends=True)

g2 = Graph(); g2 += g
for _, b in old:
    g2.remove((b, None, None))
new = []
for o, t, k in texts:
    if o == 3:
        new.extend((ln, djr["kind-code"]) for ln in lines)
    else:
        new.append((t, k))
for i, (t, k) in enumerate(new, start=1):
    iri = URIRef(f"{sec}/b{i}")
    g2.add((iri, RDF.type, djr.Block)); g2.add((iri, djr.inSection, sec))
    g2.add((iri, djr.kind, k)); g2.add((iri, djr.order, Literal(i)))
    g2.add((iri, djr.text, Literal(t, lang="ko") if k != djr["kind-code"] else Literal(t)))
r2 = R.graph_sections(g2, path); r1 = R.graph_sections(g, path)
span = {s["section_key"]: s for s in parse_sections((REPO_ROOT/path).read_bytes())}["s004-1"]["span"]
print("원본 렌더 == 절 스팬:", r1["s004-1"].encode() == span)
print("분해본 렌더 == 절 스팬:", r2["s004-1"].encode() == span)
print("블록 수 7 →", len(new), " (BlockShape 2881 →", 2881 + len(new) - 7, ")")
print("재번호되는 후행 블록 IRI:", [f"b{o}→b{o+len(lines)-1}" for o,_ ,_ in texts if o>3])
