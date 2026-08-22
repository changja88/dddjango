import sys, glob
sys.path.insert(0,"/Users/hyun/Desktop/dddjango/workspace/tools")
from rdflib import Graph, Namespace
from ontology_canon import REPO_ROOT
djr = Namespace("https://numchida.com/ns/djr#")
g = Graph()
for p in sorted(glob.glob(str(REPO_ROOT/"ontology/rules/*.ttl"))):
    g.parse(p, format="turtle")
tot=0; nonorm=0; codek=0
for s,_,o in g.triples((None, djr.restates, None)):
    tot+=1
    if not list(g.objects(o, djr.statesNorm)): nonorm+=1
    if (o, djr.kind, djr["kind-code"]) in g: codek+=1
print("restates 총", tot, "· 대상 블록이 statesNorm 0인 건:", nonorm, "· 대상이 kind-code:", codek)
# 코드 블록 전수
codes = list(g.subjects(djr.kind, djr["kind-code"]))
print("코퍼스 전체 kind-code 블록:", len(codes), "· 그중 statesNorm 보유:", sum(1 for c in codes if list(g.objects(c, djr.statesNorm))))
print("전체 Block:", len(set(g.subjects(djr.inSection, None))))
