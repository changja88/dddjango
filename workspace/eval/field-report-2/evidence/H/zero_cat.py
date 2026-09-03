import subprocess, sys, re
from collections import Counter
from pathlib import Path
R = Path(sys.argv[1])
files = subprocess.run(["git","-C",str(R),"ls-files","--","*.py"],capture_output=True,text=True).stdout.split()
empty = [f for f in files if (R/f).is_file() and (R/f).stat().st_size==0 and not f.endswith("__init__.py")]
SANCTIONED = re.compile(r"(_command|_query|_result)\.py$|/exception\.py$|/event_wiring\.py$|/event_router\.py$|/api_router\.py$|/bc_error_schema\.py$|/schema_(in|out)\.py$|_published_error\.py$|_exception\.py$")
cat = Counter(); decl = []
for f in empty:
    if SANCTIONED.search(f): cat["sanctioned-slot(빈 파일 허용 칸)"] += 1
    elif f.endswith("_port.py"): cat["_port.py"] += 1; decl.append(f)
    elif f.endswith("_use_case.py"): cat["_use_case.py"] += 1; decl.append(f)
    elif f.endswith("_repository.py"): cat["_repository.py"] += 1; decl.append(f)
    elif "/test/" in f: cat["test/*"] += 1; decl.append(f)
    else: cat["other"] += 1; decl.append(f)
print(f"{R.name}: tracked 0-byte .py (excl __init__) = {len(empty)}")
for k,v in cat.most_common(): print(f"  {k}: {v}")
for f in decl: print("   *", f)
