import re, sys, pathlib
ROOT = pathlib.Path.home()/"Desktop/spring_dream_server/.dddjango"
LANES = ["20260830-1809-fortune-record","20260902-1842-notification-email-template","20260902-1458-notification-bc","20260831-2331-fortune-reading","20260903-2202-chat-relay-2a-generate-port-identity","20260902-0128-media-library","20260903-1214-fortune-catalog"]
out = []
for lane in LANES:
    p = ROOT/lane/"design-spec.md"
    lines = p.read_text().splitlines()
    i = next(k for k,l in enumerate(lines) if "<!-- machine: boundary-imports -->" in l)
    j = i+1
    assert lines[j].startswith("```imports"), (lane, lines[j])
    k = j+1
    while not lines[k].startswith("```"): k += 1
    rows = lines[j+1:k]
    out.append(f"=== {lane}  (block L{i+1}-L{k+1}, {len(rows)} rows)")
    for n,r in enumerate(rows, start=j+2):
        out.append(f"  L{n}: {r}")
    # rows importing from application_layer/port or application_layer.port
    port_rows = [r for r in rows if re.search(r"application_layer[./]port", r)]
    out.append(f"  -> rows importing application_layer/port: {len(port_rows)}")
    for r in port_rows: out.append(f"     PORT: {r}")
    exc_rows = [r for r in rows if re.search(r"(Error|Exception|exception)", r)]
    out.append(f"  -> rows naming *Error/*Exception/exception: {len(exc_rows)}")
    for r in exc_rows: out.append(f"     EXC: {r}")
    out.append("")
txt = "\n".join(out)
(pathlib.Path(sys.argv[1])/"blocks.txt").write_text(txt)
print(txt)
