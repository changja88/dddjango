"""mypy 출력(c20f525)을 대장 줄 표(P1a~e·P2·…)와 file:line 으로 대조해 패턴별 계수."""
import re, sys
from pathlib import Path
S = Path("/private/tmp/claude-501/-Users-hyun-Desktop-dddjango/d31bf8ef-f45e-4609-badc-3add1039bdb0/scratchpad/fr3")
ledger = (S / "spring-c20f525/docs/superpowers/plans/2026-09-04-mypy-debt-ledger.md").read_text(encoding="utf-8")
ABBR = {"fw/rag/": "framework/technology/rag/runtime/",
        "reading/api/": "application/fortune_reading/driving_layer/api/evidence_provisioning/",
        "reading/": "application/fortune_reading/"}
pattern = None
table: dict[str, str] = {}
for line in ledger.splitlines():
    m = re.match(r"^### (P\d[a-z]?) ", line)
    if m:
        pattern = m.group(1); continue
    m = re.match(r"^\| `([^`]+):(\d+)` \|", line)
    if m and pattern:
        f, ln = m.group(1), m.group(2)
        for k, v in ABBR.items():
            if f.startswith(k):
                f = v + f[len(k):]; break
        table[f"{f}:{ln}"] = pattern
out = (S / "S4/mypy_c20f525.txt").read_text(encoding="utf-8")
counts: dict[str, int] = {}
unmatched = []
codes_by_pat: dict[str, dict[str, int]] = {}
for line in out.splitlines():
    m = re.match(r"^([^:]+):(\d+): error: (.*)\s+\[([a-z-]+)\]$", line)
    if not m: continue
    key = f"{m.group(1)}:{m.group(2)}"
    pat = table.get(key)
    if pat is None:
        unmatched.append(line); pat = "?"
    counts[pat] = counts.get(pat, 0) + 1
    codes_by_pat.setdefault(pat, {}).setdefault(m.group(4), 0)
    codes_by_pat[pat][m.group(4)] += 1
print("ledger entries:", len(table))
for p in sorted(counts): print(p, counts[p], codes_by_pat[p])
p1 = sum(v for k, v in counts.items() if k.startswith("P1")); p2 = counts.get("P2", 0)
print("P1 total", p1, "P2", p2, "P1+P2", p1 + p2, "all", sum(counts.values()))
print("unmatched", len(unmatched)); print("\n".join(unmatched[:10]))
# object-기인 메시지 계수(대장 무관 · 메시지 문면)
obj = [l for l in out.splitlines() if re.search(r'"object"|type "object"|expected "list\[dict\[str, object\]\]"|Mapping\[str, object\]|dict\[str, object\]', l)]
print("object-mention lines", len(obj))
