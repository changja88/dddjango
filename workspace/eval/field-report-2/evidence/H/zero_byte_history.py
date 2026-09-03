#!/usr/bin/env python3
"""repo — git 이력에서 같은 경로가 0바이트로 A → D → A 된 패턴 계수(전 브랜치·--all)."""
import subprocess, sys
from collections import defaultdict
repo = sys.argv[1]
EMPTY = "e69de29bb2d1d6434b8b29ae775ad8c2e48c5391"
# --raw: :<old> <new> <oldsha> <newsha> <status>\t<path>
log = subprocess.run(["git", "-C", repo, "log", "--all", "--reverse", "--raw", "--no-renames",
                      "--format=@@%h %ci %s"], capture_output=True, text=True).stdout
events = defaultdict(list)  # path -> [(status, commit, subject)]
cur = None
for line in log.splitlines():
    if line.startswith("@@"):
        cur = line[2:]; continue
    if not line.startswith(":"): continue
    meta, path = line.split("\t", 1)
    parts = meta.split()
    old_sha, new_sha, status = parts[2], parts[3], parts[4][0]
    if not path.endswith(".py"): continue
    if status == "A" and new_sha.startswith(EMPTY[:7]):
        events[path].append(("A0", cur))
    elif status == "D" and old_sha.startswith(EMPTY[:7]):
        events[path].append(("D0", cur))
    elif status == "M" and old_sha.startswith(EMPTY[:7]):
        events[path].append(("M+", cur))  # 빈 파일이 내용으로 채워짐
n_ada = 0
for path, ev in sorted(events.items()):
    seq = "".join({"A0": "A", "D0": "D", "M+": "M"}[s] for s, _ in ev)
    if "ADA" in seq:
        n_ada += 1
        print(f"ADA  {path}")
        for s, c in ev: print(f"      {s}  {c[:60]}")
print(f"TOTAL paths with 0-byte A→D→A: {n_ada}   (0-byte .py paths tracked: {len(events)})")
