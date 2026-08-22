import sys, glob
sys.path.insert(0,"/Users/hyun/Desktop/dddjango/workspace/tools")
from rdflib import Graph, Namespace
from ontology_canon import REPO_ROOT
djr = Namespace("https://numchida.com/ns/djr#")
g = Graph()
for p in sorted(glob.glob(str(REPO_ROOT/"ontology/rules/*.ttl"))):
    g.parse(p, format="turtle")
for s,_,o in g.triples((None, djr.restates, None)):
    if (o, djr.kind, djr["kind-code"]) in g:
        print("restates→code 선례:", s, "→", o)
    if not list(g.objects(o, djr.statesNorm)):
        print("restates→statesNorm0:", s, "→", o)
tot=0
for c in g.subjects(djr.kind, djr["kind-code"]):
    t = str(next(g.objects(c, djr.text)))
    tot += len(t.splitlines())
print("코드 펜스 총 라인 수(일반화 시 블록 증가분):", tot)
