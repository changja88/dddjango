import re, sys, pathlib
ROOT = pathlib.Path.home()/"Desktop/spring_dream_server/.dddjango"
S = pathlib.Path(sys.argv[1])
SPECS = {
 "fortune-record": ROOT/"20260830-1809-fortune-record/design-spec.md",
 "notification-email-template": ROOT/"20260902-1842-notification-email-template/design-spec.md",
 "notification-bc": ROOT/"20260902-1458-notification-bc/design-spec.md",
 "fortune-reading(current)": ROOT/"20260831-2331-fortune-reading/design-spec.md",
 "fortune-reading(P4@919440c)": S/"reading-spec-P4-919440c.md",
 "chat-relay-2a": ROOT/"20260903-2202-chat-relay-2a-generate-port-identity/design-spec.md",
 "media-library": ROOT/"20260902-0128-media-library/design-spec.md",
 "fortune-catalog(G1@9ee721e)": S/"catalog-spec-G1-9ee721e.md",
 "fortune-catalog(current)": ROOT/"20260903-1214-fortune-catalog/design-spec.md",
}
LEAF = r"(controller|컨트롤러|OHS|open_host_service|driving 잎|driving leaf|잎|_service\.py)"
EXC  = r"([A-Z][A-Za-z]*(Error|Exception|Mismatch|Failed|Invalid|Rejected|Unavailable|Failure)\b|exception\.py|포트 예외|port 예외|port exception)"
ACT  = r"(import|catch|except|잡|소비|분기|번역)"
out=[]
for name,p in SPECS.items():
    txt=p.read_text().splitlines()
    # mask machine blocks
    inblk=False; rows=[]
    for i,l in enumerate(txt,1):
        if l.startswith("```") and inblk: inblk=False; continue
        if re.match(r"```(imports|paths|symbols|exceptions)",l): inblk=True; continue
        if inblk: continue
        if re.search(LEAF,l) and re.search(EXC,l) and re.search(ACT,l) and re.search(r"port|포트",l):
            rows.append((i,l))
    out.append(f"=== {name}: prose lines (leaf+exception+act+port, outside blocks) = {len(rows)}")
    for i,l in rows[:8]:
        out.append(f"   L{i}: {l[:300]}")
t="\n".join(out); (S/"prose_classify.txt").write_text(t); print(t)
