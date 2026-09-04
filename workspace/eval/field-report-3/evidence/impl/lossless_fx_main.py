#!/usr/bin/env python3
"""픽스처 케이스 실행기 — fixture_matrix.build_cases() 의 argv 를 그대로 쓰되 검사기 경로만 old/new 트리로 치환.

사용: lossless_fx.py <old|new> <scripts-dir> <out-dir> <checker…>
산출: <out>/fx.<케이스>.<ver>.<검사기>.{jsonl,out,exit}
"""
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path("/Users/hyun/Desktop/dddjango")
sys.path.insert(0, str(ROOT / "workspace" / "tools"))
sys.path.insert(0, str(ROOT / "dddjango" / "scripts"))
import fixture_matrix as FM  # noqa: E402
FM.F = Path("/private/tmp/claude-501/-Users-hyun-Desktop-dddjango/d31bf8ef-f45e-4609-badc-3add1039bdb0/scratchpad/fr3/rv3C/fixtures-main")

ver, scripts_dir, out_dir = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
checkers = set(sys.argv[4:])
env = dict(os.environ)
env.pop("DJR_VIOLATIONS_DIR", None)
env.pop("DJR_SOURCE_GIT_ROOT", None)
n = 0
for label, argv, fixture, want in FM.build_cases():
    script = Path(argv[1]).name
    if script not in checkers:
        continue
    key = label.replace("/", "_")
    sink = out_dir / f"fx.{key}.{ver}.{script}.jsonl"
    sink.unlink(missing_ok=True)
    env["DJR_FINDINGS_JSON"] = str(sink)
    new_argv = [sys.executable, str(scripts_dir / script)] + argv[2:]
    proc = subprocess.run(new_argv, capture_output=True, text=True, env=env, cwd=str(ROOT))
    (out_dir / f"fx.{key}.{ver}.{script}.out").write_text(proc.stdout + proc.stderr, encoding="utf-8")
    (out_dir / f"fx.{key}.{ver}.{script}.exit").write_text(f"{proc.returncode}\n", encoding="utf-8")
    n += 1
print(f"fixtures {ver}: {n} matrix cases (main fixture tree)")
