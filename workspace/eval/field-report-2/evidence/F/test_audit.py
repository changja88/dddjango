"""테스트 실태: build_* 팩토리 monkeypatch/patch 건수 vs 진짜 build_*() 호출·실행 건수 (AST)."""
from __future__ import annotations
import ast, sys, json, collections
from pathlib import Path
REPO = Path(sys.argv[1]).resolve()
LABEL = sys.argv[2]
files = [p for p in REPO.rglob("*.py") if "__pycache__" not in p.parts and (p.name.startswith("test_") or p.name == "conftest.py" or "test" in p.parts or "tests" in p.parts)]
files = [p for p in files if ".venv" not in p.parts and "node_modules" not in p.parts]
def bc_of(p):
    parts = p.relative_to(REPO).parts
    return parts[1] if parts[0] == "application" and len(parts) > 1 else parts[0]
PATCH_FUNCS = {"setattr", "patch", "object"}  # monkeypatch.setattr / mock.patch / patch.object / mocker.patch
def mentions_build(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, str) and "build_" in node.value: return node.value
    if isinstance(node, ast.Attribute) and node.attr.startswith("build_"): return node.attr
    if isinstance(node, ast.Name) and node.id.startswith("build_"): return node.id
    return None
rows = []
for p in files:
    try: tree = ast.parse(p.read_text(encoding="utf-8"))
    except Exception: continue
    local_builds = {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name.startswith("build_")}
    patched, real_calls, real_exec = [], [], []
    src = p.read_text(encoding="utf-8")
    for n in ast.walk(tree):
        if not isinstance(n, ast.Call): continue
        fname = n.func.attr if isinstance(n.func, ast.Attribute) else (n.func.id if isinstance(n.func, ast.Name) else "")
        if fname in PATCH_FUNCS or fname.startswith("patch"):
            for a in list(n.args) + [k.value for k in n.keywords]:
                m = mentions_build(a)
                if m and m not in local_builds:
                    patched.append((n.lineno, m)); break
        # direct build_* call
        bn = n.func.attr if isinstance(n.func, ast.Attribute) and n.func.attr.startswith("build_") else (n.func.id if isinstance(n.func, ast.Name) and n.func.id.startswith("build_") else None)
        if bn and bn not in local_builds and bn.endswith(("use_case", "_query", "_command", "_service", "_handler", "_projector")) or (bn and bn not in local_builds and "use_case" in bn):
            real_calls.append((n.lineno, bn))
    patched_names = {m for _, m in patched}
    # execution: build call whose result is .execute(d)/called directly (line-level heuristic)
    for ln, bn in real_calls:
        line = src.splitlines()[ln-1]
        if ".execute(" in line or bn in patched_names:
            real_exec.append((ln, bn, "same-line execute" if ".execute(" in line else "NAME PATCHED IN FILE"))
    if patched or real_calls:
        rows.append({"repo": LABEL, "bc": bc_of(p), "file": str(p.relative_to(REPO)), "patched": patched, "real_calls": real_calls, "real_calls_not_patched": [(l,b) for l,b in real_calls if b not in patched_names], "has_execute": ".execute(" in src})
json.dump(rows, open(f"{sys.argv[3]}", "w"), ensure_ascii=False, indent=1)
tp = sum(len(r["patched"]) for r in rows); tf = sum(1 for r in rows if r["patched"])
rc = sum(len(r["real_calls_not_patched"]) for r in rows); rf = [r for r in rows if r["real_calls_not_patched"]]
print(f"== {LABEL}: test files scanned={len(files)} | build_* patched: {tp} sites in {tf} files | real build_*() (name not patched in same file): {rc} sites in {len(rf)} files")
bybc = collections.defaultdict(lambda: [0,0,0,0])
for r in rows:
    b = bybc[r["bc"]]; b[0] += len(r["patched"]); b[1] += 1 if r["patched"] else 0; b[2] += len(r["real_calls_not_patched"]); b[3] += 1 if r["real_calls_not_patched"] else 0
print("BC | patched sites | patched files | real-call sites | real-call files")
for bc, v in sorted(bybc.items()): print(f"{bc} | {v[0]} | {v[1]} | {v[2]} | {v[3]}")
print("-- real build_*() files (not patched) --")
for r in rf: print(f"  {r['bc']} {r['file']} calls={[(l,b) for l,b in r['real_calls_not_patched']]} has_execute={r['has_execute']}")
