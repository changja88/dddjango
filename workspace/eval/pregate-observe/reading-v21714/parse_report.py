import re,sys,json,collections
path=sys.argv[1]
txt=open(path,encoding='utf-8').read()
runs=re.split(r'^## pre-gate 예보 — ',txt,flags=re.M)[1:]
item_re=re.compile(r'^- `([0-9a-f]{12})` (check-[\w-]+\.py) :: \[#(\d+)\] ([^:]+?): (.*)$',re.M)
out=[]
rule_tot=collections.Counter(); rule_runs=collections.defaultdict(set); ids=collections.defaultdict(lambda:{'rule':None,'path':None,'runs':[],'msg':None,'checker':None})
form_red=[]
for i,r in enumerate(runs,1):
    head=r.split('\n',1)[0]
    ts=head.split(' · ')[0]
    verdict=re.search(r'^- 판정: (.*)$',r,re.M)
    verdict=verdict.group(1) if verdict else '?'
    base=re.search(r'기준선 SHA: `([0-9a-f]+)`',r)
    items=item_re.findall(r)
    for sid,chk,rule,pth,msg in items:
        rule_tot[rule]+=1; rule_runs[rule].add(i)
        d=ids[sid]; d['rule']=rule; d['path']=pth.strip(); d['runs'].append(i); d['msg']=msg[:140]; d['checker']=chk
    if verdict.startswith('형식 red'):
        # capture the lines after 판정 that explain
        m=re.search(r'^- 판정: 형식 red\s*\n((?:- .*\n?)+)',r,re.M)
        form_red.append((i,ts,(m.group(1).strip()[:400] if m else '')))
    out.append({'run':i,'ts':ts,'verdict':verdict,'base':base.group(1)[:8] if base else None,'n_items':len(items),'rules':sorted(set(x[2] for x in items))})
for o in out: print(f"{o['run']:2d} {o['ts']} base={o['base']} n={o['n_items']:2d} rules={','.join('#'+x for x in o['rules'])} :: {o['verdict'][:40]}")
print('\n== rule totals (item-occurrences, runs-with-rule, unique ids) ==')
uniq=collections.Counter(d['rule'] for d in ids.values())
for rule,c in rule_tot.most_common(): print(f"#{rule:<4} occ={c:3d} runs={len(rule_runs[rule]):2d} uniq_ids={uniq[rule]}")
print('\n== unique ids by rule ==')
for sid,d in sorted(ids.items(),key=lambda kv:(kv[1]['rule'],kv[0])):
    print(f"#{d['rule']} {sid} runs={len(d['runs'])}({d['runs'][0]}-{d['runs'][-1]}) {d['path']} :: {d['msg'][:90]}")
print('\n== 형식 red ==')
for i,ts,m in form_red: print(f"run {i} {ts}\n  {m}\n")
json.dump({'runs':out,'ids':ids,'form_red':form_red},open('reading_parsed.json','w'),ensure_ascii=False,indent=1,default=list)
