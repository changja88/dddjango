import sys
sys.path.insert(0,"/Users/hyun/Desktop/dddjango/workspace/tools")
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF
from ontology_canon import REPO_ROOT, frag_encode, canon_turtle, load_prefix_registry
DJR="https://numchida.com/ns/djr#"; djr=Namespace(DJR)
p = REPO_ROOT/"scratchpad/ont-x/rules/discipline-houserules-final.ttl"
g=Graph(); g.parse(p, format="turtle")
path="dddjango/skills/discipline-houserules/references/final.md"
sec=URIRef(f"{DJR}s/{frag_encode(path)}/s004-1")
old=sorted(((int(next(g.objects(b,djr.order))),b) for b in g.subjects(djr.inSection,sec)))
recs=[(o,str(next(g.objects(b,djr.text))),next(g.objects(b,djr.kind)),list(g.objects(b,djr.statesNorm))) for o,b in old]
for _,b in old: g.remove((b,None,None))
new=[]
for o,t,k,sn in recs:
    if o==3: new.extend((ln,k,[]) for ln in t.splitlines(keepends=True))
    else: new.append((t,k,sn))
for i,(t,k,sn) in enumerate(new,1):
    iri=URIRef(f"{sec}/b{i}")
    g.add((iri,RDF.type,djr.Block)); g.add((iri,djr.inSection,sec))
    g.add((iri,djr.kind,k)); g.add((iri,djr.order,Literal(i)))
    g.add((iri,djr.text, Literal(t) if k==djr["kind-code"] else Literal(t,lang="ko")))
    for w in sn: g.add((iri,djr.statesNorm,w))
p.write_text(canon_turtle(g, load_prefix_registry(), False), encoding="utf-8")
print("wrote", p, "blocks", len(new))
