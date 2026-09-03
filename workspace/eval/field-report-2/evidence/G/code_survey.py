import re, pathlib, sys
ROOT = pathlib.Path.home()/"Desktop/spring_dream_server/application"
BCS = {"fortune-record":["fortune_record"],"notification-email-template":["notification"],"notification-bc":["notification","accounts"],
       "fortune-reading":["fortune_reading"],"chat-relay-2a":["chat_relay"],"media-library":["media_library"],"fortune-catalog":["fortune_catalog"]}
DRIVING = ("driving_layer",)
out=[]
tot=0; exc_tot=0
for lane,bcs in BCS.items():
    for bc in bcs:
        base = ROOT/bc
        if not base.exists():
            out.append(f"=== {lane} / {bc}: BC dir MISSING"); continue
        dl = base/"driving_layer"
        out.append(f"=== {lane} / {bc}  driving_layer exists={dl.exists()}  subdirs={[p.name for p in dl.iterdir() if p.is_dir()] if dl.exists() else None}")
        n=0; e=0
        for py in sorted(dl.rglob("*.py")) if dl.exists() else []:
            for i,line in enumerate(py.read_text().splitlines(),1):
                s=line.strip()
                if re.match(r"(from|import)\s", s) and re.search(r"application_layer\.port\b", s):
                    isexc = bool(re.search(r"\.exception\b|Error\b|Exception\b|Mismatch\b|Failed\b|Invalid\b|Rejected\b|Unavailable\b", s))
                    n+=1; e+=isexc
                    out.append(f"  {py.relative_to(ROOT.parent)}:{i}  {s}   {'[EXC]' if isexc else ''}")
        out.append(f"  -> driving_layer imports from application_layer.port: {n} (exception-class rows: {e})")
        tot+=n; exc_tot+=e
out.append(f"TOTAL port-imports in driving leaves: {tot} (exception rows {exc_tot})")
t="\n".join(out); (pathlib.Path(sys.argv[1])/"code_survey.txt").write_text(t); print(t)
