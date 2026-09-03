#!/usr/bin/env python3
"""label scripts_dir root outdir — 27종 실행 → 다섯 규칙 × fortune_catalog 레코드 집계."""
import json, os, subprocess, sys
from collections import defaultdict
from pathlib import Path
label, scripts, root, outdir = sys.argv[1:5]
RULES = ("#219", "#635", "#218", "#193", "#576")
out = Path(outdir); out.mkdir(parents=True, exist_ok=True)
jl = out / f"{label}.jsonl"
if jl.exists(): jl.unlink()
sys.path.insert(0, scripts)
import checker_registry as cr
env = dict(os.environ); env.pop("DJR_VIOLATIONS_DIR", None); env["DJR_FINDINGS_JSON"] = str(jl)
log = out / f"{label}.log"
with log.open("w") as lf:
    only = os.environ.get("ONLY")
    for name, auto in cr.REGISTRY:
        if only and name not in only.split(","): continue
        argv = cr.checker_argv(sys.executable, name, root, auto)
        p = subprocess.run(argv, capture_output=True, text=True, env=env, cwd=root)
        lf.write(f"### {name} exit={p.returncode}\n{p.stdout}\n{p.stderr}\n")
recs = [json.loads(l) for l in jl.read_text().splitlines()] if jl.exists() else []
hits = defaultdict(list)
for r in recs:
    if r.get("rule") in RULES and "fortune_catalog" in (r.get("file") or ""):
        hits[r["rule"]].append((r["file"], r["message"]))
print(f"## {label}  (records={len(recs)})")
for rule in RULES:
    files = hits.get(rule, [])
    print(f"{rule}: {len(files)}건")
    for f, m in files:
        print(f"    {f} — {m[:70]}")
