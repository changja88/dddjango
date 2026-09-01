#!/usr/bin/env python3
import json
import sys
from pathlib import Path

from pregate_proto import run
import transcript_parser

here = Path(__file__).parent
src = Path.home() / ".herdr/worktrees/spring_dream_server/feat-fortune-reading"
for name, sha in (("2d44743", "2d44743"), ("e152e57", "e152e57")):
    files, notes = transcript_parser.parse(here.parent / f"transcript-{name}.md")
    rep = run(src, sha, files, here / f"run-{name}", sys.executable, keep=True, reconcile=True)
    (here / f"run-{name}").mkdir(exist_ok=True)
    (here / f"run-{name}" / "report.json").write_text(json.dumps({"notes": notes, **rep}, ensure_ascii=False, indent=1))
    print(f"== {name}: status={rep.get('status')} exit={rep.get('exit')} "
          f"already_built={len(rep.get('already_built', []))} unsim={len(rep.get('unsimulated', []))} "
          f"errors={rep.get('errors', '')}")
