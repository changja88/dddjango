import json, re, sys, collections
S="/private/tmp/claude-501/-Users-hyun-Desktop-dddjango/d31bf8ef-f45e-4609-badc-3add1039bdb0/scratchpad/fr3"
LOC=re.compile(r'(\S+\.py):(\d+)')
def lines(path, tag):
    out=[]
    for l in open(path, encoding="utf-8"):
        l=l.rstrip("\n"); s=l.strip()
        if s.startswith(f"[{tag}]"): out.append(s)
    return out
def loc(s):
    m=LOC.search(s); return (m.group(1), int(m.group(2))) if m else None
for repo in ("spring","kkebi"):
    old=f"{S}/rv3C/out/{repo}.old.check-public-surface-annotation.py.out"; new=f"{S}/impl/run-{repo}.txt"
    o645=set(lines(old,"#645")); n645=set(lines(new,"#645"))
    print(f"== {repo}: #645 v old={len(o645)} new={len(n645)} byte-identical={o645==n645} | only-old={len(o645-n645)} only-new={len(n645-o645)}")
    for s in list(o645-n645)[:2]+list(n645-o645)[:2]: print("   Δ", s[:140])
    o645c=set(lines(old,"ⓓ#645")); n645c=set(lines(new,"ⓓ#645")); n647v=lines(new,"#647"); n647v_loc={loc(s) for s in n647v}
    gone=o645c-n645c; matched=sum(1 for s in gone if loc(s) in n647v_loc); print(f"   ⓓ#645 old={len(o645c)} new={len(n645c)} gone={len(gone)} matched-to-#647={matched} unmatched={len(gone)-matched} newonly={len(n645c-o645c)}")
    for s in [s for s in gone if loc(s) not in n647v_loc][:3]: print("   unmatched:", s[:140])
    C=[json.loads(l) for l in open(f"{S}/rv3C/c647_{repo}.jsonl")]
    cb={(r["file"],r["line"]) for r in C if r["verdict"]=="blocker" and r["in_roots"]}
    cc={(r["file"],r["line"]) for r in C if r["verdict"]=="cand" and r["in_roots"]}
    nb={loc(s) for s in n647v}; nc={loc(s) for s in lines(new,"ⓓ#647") if "자리표시" not in s}; nret={loc(s) for s in lines(new,"ⓓ#647") if "자리표시" in s}
    print(f"   #647 v 줄: C={len(cb)} new={len(nb)} · C-only={len(cb-nb)} new-only={len(nb-cb)}")
    for x in sorted(cb-nb)[:6]: print("     C-only:", x, [r['text']+'/'+r['site']+'/'+r['reason'] for r in C if (r['file'],r['line'])==x and r['verdict']=='blocker'][:2])
    for x in sorted(nb-cb)[:6]: print("     new-only:", x, [s[:110] for s in n647v if loc(s)==x][:1])
    print(f"   #647 ⓓ(입구) 줄: C={len(cc)} new={len(nc)} · C-only={len(cc-nc)} new-only={len(nc-cc)} · 자리표시 ⓓ new={len(nret)}")
    for x in sorted(cc-nc)[:4]: print("     C-only:", x, [r['text']+'/'+r['site'] for r in C if (r['file'],r['line'])==x and r['verdict']=='cand'][:1])
    for x in sorted(nc-cc)[:4]: print("     new-only:", x)
    print(f"   #650 new={len(lines(new,'ⓓ#650'))} · #646 v={len(lines(new,'#646'))} ⓓ={len(lines(new,'ⓓ#646'))}")
