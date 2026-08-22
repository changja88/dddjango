"""T3 트리 좌표 처분안 A(펜스 행 분해) byte 등가 실측 — 저장소 무변경 스크래치."""
import sys
from pathlib import Path
sys.path.insert(0, "/Users/hyun/Desktop/dddjango/workspace/tools")
from rdflib import Graph, Namespace, URIRef, Literal
from ontology_canon import REPO_ROOT
from ontology_census import parse_sections
import ontology_render as R

DJR = R.DJR
djr = Namespace(DJR)
path = "dddjango/skills/discipline-houserules/references/final.md"
g = Graph(); g.parse(REPO_ROOT / "ontology/rules/discipline-houserules-final.ttl", format="turtle")

sec = URIRef(f"{DJR}s/{__import__('ontology_canon').frag_encode(path)}/s004-1")
blocks = []
for b in g.subjects(djr.inSection, sec):
    blocks.append((int(next(g.objects(b, djr.order))), b))
blocks.sort()
print("현행 블록 수:", len(blocks))
b3 = dict((o, b) for o, b in blocks)[3]
code = str(next(g.objects(b3, djr.text)))
lines = code.splitlines(keepends=True)
print("펜스 라인 수(개폐 포함):", len(lines))
print("byte 등가(단순 연결):", "".join(lines) == code)

# 분해본 그래프 구성
g2 = Graph(); g2 += g
for o, b in blocks:
    if o == 3:
        g2.remove((b, None, None))
    elif o > 3:
        g2.remove((b, djr.order, None))
newblocks = []
for i, ln in enumerate(lines):
    iri = URIRef(f"{sec}/b{3+i}")
    g2.add((iri, URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"), djr.Block))
    g2.add((iri, djr.inSection, sec))
    g2.add((iri, djr.kind, djr["kind-code"]))
    g2.add((iri, djr.order, Literal(3+i)))
    g2.add((iri, djr.text, Literal(ln)))
    newblocks.append(iri)
shift = len(lines) - 1
for o, b in blocks:
    if o > 3:
        g2.add((b, djr.order, Literal(o + shift)))
rendered = R.graph_sections(g2, path)
cur = {s["section_key"]: s for s in parse_sections((REPO_ROOT/path).read_bytes())}
span = cur["s004-1"]["span"]
print("분해본 렌더 == 현행 절 스팬 byte:", rendered["s004-1"].encode("utf-8") == span)
print("분해 후 s004-1 블록 수:", 6 + len(lines))

base = R.graph_sections(g, path)
print("원본 렌더 == 현행 절 스팬:", base["s004-1"].encode("utf-8") == span)
print("원본 렌더 == 분해본 렌더:", base["s004-1"] == rendered["s004-1"])
a=base["s004-1"].encode(); b=span
print("len", len(a), len(b))
for i,(x,y) in enumerate(zip(a,b)):
    if x!=y:
        print("first diff at", i, a[max(0,i-60):i+60], "||", b[max(0,i-60):i+60]); break
