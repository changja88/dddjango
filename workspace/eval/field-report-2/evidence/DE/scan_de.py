#!/usr/bin/env python3
"""scan_de.py — D(always-raise helper declared `-> None`) · E(explicit `Any`) AST census.

usage: scan_de.py <repo_root> <label> <out_dir>
Writes <out_dir>/<label>_d.jsonl, <label>_noreturn.jsonl, <label>_any.jsonl, <label>_files.json
and prints a markdown summary to stdout.
"""
from __future__ import annotations

import ast
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

SKIP_DIRS = {
    ".venv", "venv", "node_modules", ".git", "__pycache__", "migrations", "site-packages",
    ".mypy_cache", ".pytest_cache", ".ruff_cache", ".worktrees", ".playwright-mcp",
    ".idea", ".claude", ".codex", ".serena", ".dddjango", ".dddjango-web", ".superpowers",
}
TEST_DIRS = {"test", "tests"}
EXIT_ATTR_CALLS = {("sys", "exit"), ("os", "_exit")}
TYPING_MODULES = {"typing", "typing_extensions"}


# ── file enumeration ────────────────────────────────────────────────────────

def iter_py(root: Path):
    for p in sorted(root.rglob("*.py")):
        rel = p.relative_to(root)
        if set(rel.parts[:-1]) & SKIP_DIRS:
            continue
        yield p, rel


def group_of(rel: Path) -> tuple[str, str]:
    parts = rel.parts
    if len(parts) == 1:
        return "(root)", "(root)"
    top = parts[0]
    if top in ("application", "framework", "web", "scripts") and len(parts) > 2:
        return top, f"{top}/{parts[1]}"
    return top, top


def is_test_file(rel: Path) -> bool:
    if set(rel.parts[:-1]) & TEST_DIRS:
        return True
    n = rel.name
    return n.startswith("test_") or n.endswith("_test.py") or n == "conftest.py" or n == "tests.py"


# ── D: always-raise helpers ─────────────────────────────────────────────────

def _is_exit_stmt(st: ast.stmt) -> bool:
    if not (isinstance(st, ast.Expr) and isinstance(st.value, ast.Call)):
        return False
    f = st.value.func
    if isinstance(f, ast.Name) and f.id in ("exit", "quit"):
        return True
    if isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name) and (f.value.id, f.attr) in EXIT_ATTR_CALLS:
        return True
    return False


def terminates(stmts: list[ast.stmt]) -> bool:
    """Every terminal path of `stmts` ends in raise / sys.exit()/exit() (heuristic, last-statement based)."""
    if not stmts:
        return False
    last = stmts[-1]
    if isinstance(last, ast.Raise) or _is_exit_stmt(last):
        return True
    if isinstance(last, ast.If):
        return terminates(last.body) and terminates(last.orelse)
    if isinstance(last, (ast.Try, ast.TryStar)):
        if terminates(last.finalbody):
            return True
        return (terminates(last.body) or terminates(last.orelse)) and all(terminates(h.body) for h in last.handlers)
    if isinstance(last, (ast.With, ast.AsyncWith)):
        return terminates(last.body)
    if isinstance(last, ast.Match):
        if not last.cases:
            return False
        irrefutable = any(
            isinstance(c.pattern, ast.MatchAs) and c.pattern.pattern is None and c.guard is None
            for c in last.cases
        )
        return irrefutable and all(terminates(c.body) for c in last.cases)
    return False


def _own_body_nodes(fn: ast.AST):
    """Walk a function body without descending into nested defs/classes/lambdas."""
    stack = list(ast.iter_child_nodes(fn))
    while stack:
        n = stack.pop()
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)):
            continue
        yield n
        stack.extend(ast.iter_child_nodes(n))


def _ann_text(node: ast.AST | None) -> str:
    if node is None:
        return ""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value.strip()
    try:
        return ast.unparse(node)
    except Exception:
        return "?"


def ret_kind(fn: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    if fn.returns is None:
        return "missing"
    t = _ann_text(fn.returns)
    if t == "None":
        return "None"
    tail = t.split(".")[-1]
    if tail in ("NoReturn", "Never"):
        return "NoReturn"
    return "other"


def _exc_name(exc: ast.AST | None) -> str:
    if exc is None:
        return "<bare re-raise>"
    target = exc.func if isinstance(exc, ast.Call) else exc
    if isinstance(target, ast.Name):
        return target.id
    if isinstance(target, ast.Attribute):
        return target.attr
    return "<expr>"


def _deco_names(fn: ast.AST) -> set[str]:
    out = set()
    for d in fn.decorator_list:
        n = d.func if isinstance(d, ast.Call) else d
        if isinstance(n, ast.Name):
            out.add(n.id)
        elif isinstance(n, ast.Attribute):
            out.add(n.attr)
    return out


def scan_d(mod: ast.Module, rel: Path, label: str, records: list, class_stack: list[str] | None = None) -> None:
    class_stack = class_stack or []
    for node in ast.walk(mod):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        body_nodes = list(_own_body_nodes(node))
        if any(isinstance(n, (ast.Return, ast.Yield, ast.YieldFrom)) for n in body_nodes):
            continue
        if not terminates(node.body):
            continue
        raised = sorted({_exc_name(n.exc) for n in body_nodes if isinstance(n, ast.Raise)})
        exits = any(_is_exit_stmt(n) for n in body_nodes if isinstance(n, ast.stmt))
        decos = _deco_names(node)
        records.append({
            "repo": label,
            "file": str(rel),
            "line": node.lineno,
            "func": node.name,
            "ret_kind": ret_kind(node),
            "ret_text": _ann_text(node.returns),
            "raised": raised,
            "uses_exit": exits,
            "abstract": "abstractmethod" in decos,
            "notimpl_only": bool(raised) and set(raised) <= {"NotImplementedError"},
            "is_method": any(a.arg in ("self", "cls") for a in node.args.args[:1]),
            "is_test": is_test_file(rel),
            "group": group_of(rel)[1],
            "top": group_of(rel)[0],
        })


# ── NoReturn census ─────────────────────────────────────────────────────────

def scan_noreturn(mod: ast.Module, rel: Path, label: str, records: list) -> None:
    for node in ast.walk(mod):
        if isinstance(node, ast.ImportFrom) and node.module in TYPING_MODULES:
            for a in node.names:
                if a.name in ("NoReturn", "Never"):
                    records.append({"repo": label, "file": str(rel), "line": node.lineno, "kind": "import",
                                    "name": a.name, "group": group_of(rel)[1], "top": group_of(rel)[0],
                                    "is_test": is_test_file(rel)})
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.returns is not None:
            t = _ann_text(node.returns)
            if t.split(".")[-1] in ("NoReturn", "Never"):
                records.append({"repo": label, "file": str(rel), "line": node.lineno, "kind": "annotation",
                                "name": t, "func": node.name, "group": group_of(rel)[1], "top": group_of(rel)[0],
                                "is_test": is_test_file(rel)})


# ── E: explicit Any ─────────────────────────────────────────────────────────

class AnyResolver:
    def __init__(self, mod: ast.Module) -> None:
        self.any_names: set[str] = set()
        self.typing_mods: set[str] = set()
        self.imported_any = False
        for node in ast.walk(mod):
            if isinstance(node, ast.ImportFrom) and node.module in TYPING_MODULES:
                for a in node.names:
                    if a.name == "Any":
                        self.any_names.add(a.asname or "Any")
                        self.imported_any = True
                    elif a.name == "*":
                        self.any_names.add("Any")
                        self.imported_any = True
            elif isinstance(node, ast.Import):
                for a in node.names:
                    if a.name in TYPING_MODULES:
                        self.typing_mods.add(a.asname or a.name)
        self.unresolved_any_seen = False

    def is_any(self, node: ast.AST) -> bool:
        if isinstance(node, ast.Name):
            if node.id in self.any_names:
                return True
            if node.id == "Any":
                self.unresolved_any_seen = True
                return True
            return False
        if isinstance(node, ast.Attribute) and node.attr == "Any" and isinstance(node.value, ast.Name):
            if node.value.id in self.typing_mods or node.value.id in TYPING_MODULES or node.value.id == "t":
                return True
        return False


def _unwrap_string_ann(node: ast.AST) -> ast.AST:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        try:
            return ast.parse(node.value, mode="eval").body
        except SyntaxError:
            return node
    return node


def _is_none(n: ast.AST) -> bool:
    return isinstance(n, ast.Constant) and n.value is None


def classify_any(ann: ast.AST, res: AnyResolver) -> tuple[str | None, str]:
    """Returns (kind, shape): kind ∈ {bare, bare_optional, nested, None}."""
    node = _unwrap_string_ann(ann)
    if res.is_any(node):
        return "bare", "Any"
    # Any | None  /  Optional[Any]  /  Union[Any, None]
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
        parts = []
        stack = [node]
        while stack:
            x = stack.pop()
            if isinstance(x, ast.BinOp) and isinstance(x.op, ast.BitOr):
                stack.extend([x.left, x.right])
            else:
                parts.append(x)
        if any(res.is_any(p) for p in parts) and all(res.is_any(p) or _is_none(p) for p in parts):
            return "bare_optional", ast.unparse(node)
    if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name) and node.value.id in ("Optional", "Union"):
        elts = node.slice.elts if isinstance(node.slice, ast.Tuple) else [node.slice]
        if any(res.is_any(p) for p in elts) and all(res.is_any(p) or _is_none(p) for p in elts):
            return "bare_optional", ast.unparse(node)
    for n in ast.walk(node):
        if n is not node and res.is_any(n):
            try:
                return "nested", ast.unparse(node)
            except Exception:
                return "nested", "?"
    return None, ""


def _outer_generic(shape: str) -> str:
    """Outermost container name of a nested shape (`dict[str, Any] | None` → dict)."""
    s = shape.split("|")[0].strip()
    return s.split("[")[0].strip() if "[" in s else s


def scan_any(mod: ast.Module, rel: Path, label: str, records: list) -> AnyResolver:
    res = AnyResolver(mod)
    top, group = group_of(rel)
    test = is_test_file(rel)

    def add(ann, site, name, func, cls, lineno):
        if ann is None:
            return
        kind, shape = classify_any(ann, res)
        if kind is None:
            return
        records.append({
            "repo": label, "file": str(rel), "line": lineno, "site": site, "kind": kind,
            "shape": shape, "outer": _outer_generic(shape) if kind == "nested" else "",
            "name": name, "func": func, "cls": cls, "group": group, "top": top, "is_test": test,
        })

    def walk(stmts, scope, func, cls):
        for st in stmts:
            if isinstance(st, ast.ClassDef):
                walk(st.body, "class", None, st.name)
            elif isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef)):
                a = st.args
                for arg in list(a.posonlyargs) + list(a.args) + list(a.kwonlyargs):
                    add(arg.annotation, "sig-arg", arg.arg, st.name, cls, st.lineno)
                for arg in (a.vararg, a.kwarg):
                    if arg is not None:
                        add(arg.annotation, "sig-star", arg.arg, st.name, cls, st.lineno)
                add(st.returns, "sig-ret", "", st.name, cls, st.lineno)
                walk(st.body, "function", st.name, cls)
            elif isinstance(st, ast.AnnAssign):
                if isinstance(st.target, ast.Attribute):
                    site = "var-attr"
                    nm = ast.unparse(st.target)
                else:
                    site = {"module": "var-module", "class": "var-class", "function": "var-local"}[scope]
                    nm = ast.unparse(st.target)
                add(st.annotation, site, nm, func, cls, st.lineno)
            elif isinstance(st, (ast.If, ast.While)):
                walk(st.body, scope, func, cls); walk(st.orelse, scope, func, cls)
            elif isinstance(st, (ast.For, ast.AsyncFor)):
                walk(st.body, scope, func, cls); walk(st.orelse, scope, func, cls)
            elif isinstance(st, (ast.With, ast.AsyncWith)):
                walk(st.body, scope, func, cls)
            elif isinstance(st, (ast.Try, ast.TryStar)):
                walk(st.body, scope, func, cls)
                for h in st.handlers:
                    walk(h.body, scope, func, cls)
                walk(st.orelse, scope, func, cls); walk(st.finalbody, scope, func, cls)
            elif isinstance(st, ast.Match):
                for c in st.cases:
                    walk(c.body, scope, func, cls)

    walk(mod.body, "module", None, None)
    return res


# ── driver ──────────────────────────────────────────────────────────────────

def main() -> int:
    root = Path(sys.argv[1]).resolve()
    label = sys.argv[2]
    out = Path(sys.argv[3])
    out.mkdir(parents=True, exist_ok=True)

    d_recs: list = []
    nr_recs: list = []
    any_recs: list = []
    files_by_group: Counter = Counter()
    test_files_by_group: Counter = Counter()
    parse_fail: list[str] = []
    unresolved_any_files: list[str] = []
    n_files = 0

    for p, rel in iter_py(root):
        n_files += 1
        top, group = group_of(rel)
        files_by_group[group] += 1
        if is_test_file(rel):
            test_files_by_group[group] += 1
        try:
            mod = ast.parse(p.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError, ValueError) as e:
            parse_fail.append(f"{rel}: {type(e).__name__}")
            continue
        scan_d(mod, rel, label, d_recs)
        scan_noreturn(mod, rel, label, nr_recs)
        res = scan_any(mod, rel, label, any_recs)
        if res.unresolved_any_seen and not res.imported_any:
            unresolved_any_files.append(str(rel))

    for name, recs in (("d", d_recs), ("noreturn", nr_recs), ("any", any_recs)):
        with (out / f"{label}_{name}.jsonl").open("w", encoding="utf-8") as fh:
            for r in recs:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    (out / f"{label}_files.json").write_text(json.dumps({
        "root": str(root), "n_files": n_files, "files_by_group": files_by_group,
        "test_files_by_group": test_files_by_group, "parse_fail": parse_fail,
        "unresolved_any_files": unresolved_any_files,
    }, ensure_ascii=False, indent=1), encoding="utf-8")

    # ── markdown summary ────────────────────────────────────────────────
    P = print
    P(f"# {label} — root={root}")
    P(f"- .py files scanned: {n_files} (parse failures: {len(parse_fail)}) — skip dirs: {sorted(SKIP_DIRS)}")
    if parse_fail:
        for x in parse_fail[:20]:
            P(f"  - parse fail: {x}")
    P(f"- files using bare `Any` name without a typing import (heuristic counted anyway): {len(unresolved_any_files)}")

    # D tables
    P("\n## D — always-raise functions by return-annotation kind")
    kinds = Counter((r["ret_kind"]) for r in d_recs)
    P(f"- total always-raise functions: {len(d_recs)} → " + ", ".join(f"{k}={v}" for k, v in sorted(kinds.items())))
    core = [r for r in d_recs if r["ret_kind"] == "None" and not r["notimpl_only"] and not r["abstract"]]
    stub = [r for r in d_recs if r["ret_kind"] == "None" and (r["notimpl_only"] or r["abstract"])]
    P(f"- `-> None` always-raise: {len(core) + len(stub)} = core(helper-like, non-NotImplementedError) {len(core)} + stub(NotImplementedError/abstract) {len(stub)}")
    P("\n### D `-> None` core — per group (files | prod | test)")
    P("| group | files | core -> None | of which test | NotImpl/abstract -> None | -> NoReturn always-raise | -> missing always-raise |")
    P("|---|---|---|---|---|---|---|")
    groups = sorted(files_by_group)
    for g in groups:
        c = [r for r in core if r["group"] == g]
        s = [r for r in stub if r["group"] == g]
        nr = [r for r in d_recs if r["group"] == g and r["ret_kind"] == "NoReturn"]
        ms = [r for r in d_recs if r["group"] == g and r["ret_kind"] == "missing"]
        if c or s or nr or ms:
            P(f"| {g} | {files_by_group[g]} | {len(c)} | {sum(r['is_test'] for r in c)} | {len(s)} | {len(nr)} | {len(ms)} |")
    P("\n### D core list (`file:line func` — raised — test?)")
    for r in sorted(core, key=lambda r: (r["file"], r["line"])):
        P(f"- {r['file']}:{r['line']} {r['func']} — raise {', '.join(r['raised']) or ('exit' if r['uses_exit'] else '?')}{' [test]' if r['is_test'] else ''}")
    P("\n### D stub list (NotImplementedError/abstract with -> None)")
    for r in sorted(stub, key=lambda r: (r["file"], r["line"])):
        P(f"- {r['file']}:{r['line']} {r['func']}{' [abstract]' if r['abstract'] else ''}{' [test]' if r['is_test'] else ''}")
    P("\n### D always-raise with `-> NoReturn` (correctly typed)")
    for r in sorted((x for x in d_recs if x["ret_kind"] == "NoReturn"), key=lambda r: (r["file"], r["line"])):
        P(f"- {r['file']}:{r['line']} {r['func']} — raise {', '.join(r['raised'])}")
    P("\n### D always-raise with missing return annotation")
    for r in sorted((x for x in d_recs if x["ret_kind"] == "missing"), key=lambda r: (r["file"], r["line"])):
        P(f"- {r['file']}:{r['line']} {r['func']} — raise {', '.join(r['raised'])}{' [test]' if r['is_test'] else ''}")

    # NoReturn table
    P("\n## NoReturn / Never usage (import + annotation)")
    P("| group | imports | annotations |")
    P("|---|---|---|")
    for g in groups:
        im = sum(1 for r in nr_recs if r["group"] == g and r["kind"] == "import")
        an = sum(1 for r in nr_recs if r["group"] == g and r["kind"] == "annotation")
        if im or an:
            P(f"| {g} | {im} | {an} |")
    P(f"- total: imports={sum(1 for r in nr_recs if r['kind']=='import')} annotations={sum(1 for r in nr_recs if r['kind']=='annotation')}")
    for r in nr_recs:
        if r["kind"] == "annotation":
            P(f"  - {r['file']}:{r['line']} {r['func']} -> {r['name']}")

    # E tables
    P("\n## E — explicit `Any` occurrences")
    def cnt(pred):
        return sum(1 for r in any_recs if pred(r))
    P(f"- total: {len(any_recs)} · bare={cnt(lambda r: r['kind']=='bare')} · bare_optional={cnt(lambda r: r['kind']=='bare_optional')} · nested={cnt(lambda r: r['kind']=='nested')}")
    P(f"- by site: " + ", ".join(f"{k}={v}" for k, v in sorted(Counter(r["site"] for r in any_recs).items())))
    P(f"- by site×kind: " + ", ".join(f"{k[0]}/{k[1]}={v}" for k, v in sorted(Counter((r["site"], r["kind"]) for r in any_recs).items())))
    P("\n### E per group (sig = signature arg/star/ret · var = AnnAssign module/class/local/attr)")
    P("| group | files | sig bare(+opt) | sig nested | var bare(+opt) | var nested | total | of which in test files |")
    P("|---|---|---|---|---|---|---|---|")
    tot = Counter()
    for g in groups:
        rs = [r for r in any_recs if r["group"] == g]
        if not rs:
            continue
        sb = sum(1 for r in rs if r["site"].startswith("sig") and r["kind"] == "bare")
        so = sum(1 for r in rs if r["site"].startswith("sig") and r["kind"] == "bare_optional")
        sn = sum(1 for r in rs if r["site"].startswith("sig") and r["kind"] == "nested")
        vb = sum(1 for r in rs if r["site"].startswith("var") and r["kind"] == "bare")
        vo = sum(1 for r in rs if r["site"].startswith("var") and r["kind"] == "bare_optional")
        vn = sum(1 for r in rs if r["site"].startswith("var") and r["kind"] == "nested")
        t = sum(1 for r in rs if r["is_test"])
        P(f"| {g} | {files_by_group[g]} | {sb}(+{so}) | {sn} | {vb}(+{vo}) | {vn} | {len(rs)} | {t} |")
    P("\n### E per top-level (application vs rest)")
    P("| top | files | sig bare(+opt) | sig nested | var bare(+opt) | var nested | total | in test files |")
    P("|---|---|---|---|---|---|---|---|")
    for top in sorted({r["top"] for r in any_recs}):
        rs = [r for r in any_recs if r["top"] == top]
        sb = sum(1 for r in rs if r["site"].startswith("sig") and r["kind"] == "bare")
        so = sum(1 for r in rs if r["site"].startswith("sig") and r["kind"] == "bare_optional")
        sn = sum(1 for r in rs if r["site"].startswith("sig") and r["kind"] == "nested")
        vb = sum(1 for r in rs if r["site"].startswith("var") and r["kind"] == "bare")
        vo = sum(1 for r in rs if r["site"].startswith("var") and r["kind"] == "bare_optional")
        vn = sum(1 for r in rs if r["site"].startswith("var") and r["kind"] == "nested")
        nf = sum(v for k, v in files_by_group.items() if (k.split("/")[0] == top))
        P(f"| {top} | {nf} | {sb}(+{so}) | {sn} | {vb}(+{vo}) | {vn} | {len(rs)} | {sum(1 for r in rs if r['is_test'])} |")
    P("\n### E top 10 files")
    for f, n in Counter(r["file"] for r in any_recs).most_common(10):
        rs = [r for r in any_recs if r["file"] == f]
        P(f"- {n:3d}  {f}  (bare {sum(1 for r in rs if r['kind']!='nested')} / nested {sum(1 for r in rs if r['kind']=='nested')})")
    P("\n### E top 10 files — production only (non-test)")
    for f, n in Counter(r["file"] for r in any_recs if not r["is_test"]).most_common(10):
        rs = [r for r in any_recs if r["file"] == f]
        P(f"- {n:3d}  {f}  (bare {sum(1 for r in rs if r['kind']!='nested')} / nested {sum(1 for r in rs if r['kind']=='nested')})")
    P("\n### E nested shapes — top 12 (with up to 3 examples each: file:line site name @func/cls)")
    shapes = Counter(r["shape"] for r in any_recs if r["kind"] == "nested")
    for shape, n in shapes.most_common(12):
        P(f"- {n:3d}  `{shape}`")
        ex = [r for r in any_recs if r["kind"] == "nested" and r["shape"] == shape]
        # prefer production examples
        ex.sort(key=lambda r: (r["is_test"], r["file"], r["line"]))
        for r in ex[:3]:
            P(f"    - {r['file']}:{r['line']} {r['site']} {r['name']} @{r['cls'] or '-'}.{r['func'] or '-'}")
    P("\n### E nested — outermost container tally")
    P(", ".join(f"{k}={v}" for k, v in Counter(r["outer"] for r in any_recs if r["kind"] == "nested").most_common()))
    P("\n### E nested — enclosing function-name tally (top 15, production only)")
    P(", ".join(f"{k or '<module/class>'}={v}" for k, v in Counter(r["func"] for r in any_recs if r["kind"] == "nested" and not r["is_test"]).most_common(15)))
    P("\n### E bare(+optional) — production list, by site (top 40)")
    for r in sorted((x for x in any_recs if x["kind"] != "nested" and not x["is_test"]), key=lambda r: (r["file"], r["line"]))[:40]:
        P(f"- {r['file']}:{r['line']} {r['site']} {r['name']} `{r['shape']}` @{r['cls'] or '-'}.{r['func'] or '-'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
