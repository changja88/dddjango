#!/usr/bin/env python3
import json
import sys
from pathlib import Path

from pregate_proto import run
from transcript_parser import parse

here = Path(__file__).parent
files, notes = parse(here.parent / "transcript-b5392f0.md")
rep = run(Path.home() / ".herdr/worktrees/spring_dream_server/feat-fortune-reading",
          "b5392f0", files, here / "run-p1", sys.executable, keep=True)
out = here / "run-p1" / "report.json"
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps({"notes": notes, **rep}, ensure_ascii=False, indent=1))
print("status:", rep.get("status"), "exit:", rep.get("exit"))
print("unsimulated:", len(rep.get("unsimulated", [])))
tail = rep.get("stdout_tail", "")
i = tail.find("== 귀속")
print(tail[i:i + 3500] if i >= 0 else tail[-2500:])
