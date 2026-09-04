#!/usr/bin/env python3
"""#647 시제품 dry-run — 주석의 `(dict|Dict|Mapping|MutableMapping)[…, object|Any]` 스캔 + `json.load(s)` ⓓ 후보.

check-public-surface-annotation.py 의 대상 파일 선별(_is_target_file · 숨김 디렉터리 제외)을 흉내 낸다.
  - 시그니처(인자·*args/**kwargs·반환) · AnnAssign 변수(모듈/함수 본문) · 클래스 속성(ClassDef 직계 AnnAssign)
  - 최상위(annotation 루트가 그 Subscript) vs 중첩(list[…]·Optional[…]·X | None·TypeIs[…]·Callable[…] 안)
  - 문자열 주석은 재파싱(_unstring 판형) · `from __future__ import annotations` 는 AST 가 이미 표현식이라 무관(기록만)
  - 컨테이너 이름은 모듈 수준 import 바인딩으로 해소(`from typing import Mapping as M` · `typing.Mapping` ·
    `collections.abc.Mapping` · `import typing as t; t.Mapping`) · `Any` 도 같은 방식 · `object` 는 builtins 이름
  - 변종 계수: 마지막 인자가 `object | None`·`X | Any` 같은 합집합인 경우는 «union-값 변종»으로 따로 센다(위반 아님)
사용: proto_647.py <TARGET_DIR> [--findings <#645 jsonl>] [--out <jsonl>] [--label <name>]
"""
from __future__ import annotations

import argparse
import ast
import collections
import json
import sys
from pathlib import Path

SKIP_DIRS = {".venv", "venv", "site-packages", "node_modules", ".git", "__pycache__", ".dddjango",
             "build", "dist", ".tox", ".mypy_cache", ".pytest_cache", ".eggs"}
SCAFFOLD_FILES = {"manage.py", "wsgi.py", "asgi.py"}
TEST_DIR_NAMES = {"test", "tests"}
TEST_FREE_DIRS = {"unit", "integration", "e2e"}
MATERIAL_DIRS = {"factories", "fake"}

CONTAINER_NAMES = {"dict", "Dict", "Mapping", "MutableMapping"}
CONTAINER_MODULES = {"typing", "typing_extensions", "collections.abc", "builtins"}
ANY_MODULES = {"typing", "typing_extensions"}
PARSER_METHODS = {"validate_python", "validate_json", "model_validate", "model_validate_json", "validate_strings"}


def is_target_file(path: Path, root: Path) -> bool:
    rel = path.relative_to(root)
    parts = set(rel.parts)
    if parts & SKIP_DIRS or "migrations" in parts:
        return False
    if any(seg.startswith(".") for seg in rel.parts[:-1]):
        return False
    if path.name in SCAFFOLD_FILES:
        return False
    if path.name.startswith("test_") or path.name == "conftest.py":
        return False
    if parts & TEST_DIR_NAMES:
        if not (parts & MATERIAL_DIRS):
            return False
        if parts & TEST_FREE_DIRS:
            return False
    return True


class Bindings:
    """모듈 수준 import 바인딩 — 컨테이너/Any 로컬 이름과 모듈 별칭."""

    def __init__(self, mod: ast.Module) -> None:
        self.container: dict[str, str] = {n: n for n in CONTAINER_NAMES}  # 로컬 이름 → 원명(builtins dict 포함)
        self.any_names: set[str] = {"Any"}
        self.mods: dict[str, str] = {}  # 로컬 별칭 → 모듈 원명(typing / collections.abc / json …)
        self.future_annotations = False
        self.json_names: set[str] = set()  # `from json import load(s)` 로컬 이름
        self.walk(mod.body)

    def shadow(self, name: str) -> None:
        self.container.pop(name, None)
        self.any_names.discard(name)
        self.mods.pop(name, None)
        self.json_names.discard(name)

    def walk(self, stmts: list[ast.stmt]) -> None:
        for st in stmts:
            if isinstance(st, ast.ImportFrom):
                if st.module == "__future__" and any(a.name == "annotations" for a in st.names):
                    self.future_annotations = True
                for a in st.names:
                    local = a.asname or a.name
                    self.shadow(local)
                    if st.module in CONTAINER_MODULES and a.name in CONTAINER_NAMES:
                        self.container[local] = a.name
                    if st.module in ANY_MODULES and a.name == "Any":
                        self.any_names.add(local)
                    if st.module == "collections" and a.name == "abc":
                        self.mods[local] = "collections.abc"
                    if st.module == "json" and a.name in ("load", "loads"):
                        self.json_names.add(local)
            elif isinstance(st, ast.Import):
                for a in st.names:
                    local = a.asname or a.name.split(".")[0]
                    self.shadow(local)
                    if a.name in CONTAINER_MODULES | ANY_MODULES | {"json", "collections"}:
                        self.mods[local] = a.name if a.asname else a.name.split(".")[0]
                        if a.name == "collections.abc" and a.asname:
                            self.mods[local] = "collections.abc"
            elif isinstance(st, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                self.shadow(st.name)
            elif isinstance(st, ast.Assign):
                for tg in st.targets:
                    if isinstance(tg, ast.Name):
                        self.shadow(tg.id)
            elif isinstance(st, ast.AnnAssign) and isinstance(st.target, ast.Name):
                self.shadow(st.target.id)
            elif isinstance(st, ast.If):
                self.walk(st.body)
                self.walk(st.orelse)
            elif isinstance(st, ast.Try):
                self.walk(st.body)
                for h in st.handlers:
                    self.walk(h.body)
                self.walk(st.orelse)
                self.walk(st.finalbody)

    def dotted(self, node: ast.AST) -> str | None:
        if isinstance(node, ast.Name):
            return self.mods.get(node.id, node.id)
        if isinstance(node, ast.Attribute):
            base = self.dotted(node.value)
            return None if base is None else f"{base}.{node.attr}"
        return None

    def container_name(self, node: ast.AST) -> str | None:
        if isinstance(node, ast.Name):
            return self.container.get(node.id)
        if isinstance(node, ast.Attribute) and node.attr in CONTAINER_NAMES:
            base = self.dotted(node.value)
            if base in CONTAINER_MODULES or base == "collections":
                return node.attr
        return None

    def value_kind(self, node: ast.AST) -> str | None:
        """마지막 슬라이스 원소가 object/Any 면 그 이름, 아니면 None."""
        if isinstance(node, ast.Name):
            if node.id in self.any_names:
                return "Any"
            if node.id == "object":
                return "object"
            return None
        if isinstance(node, ast.Attribute):
            base = self.dotted(node.value)
            if node.attr == "Any" and base in ANY_MODULES:
                return "Any"
            if node.attr == "object" and base == "builtins":
                return "object"
        return None


def unstring(node: ast.AST) -> ast.AST:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        try:
            return ast.parse(node.value, mode="eval").body
        except SyntaxError:
            return node
    return node


def deep_unstring(node: ast.AST) -> ast.AST:
    """주석 안 모든 문자열 조각을 재파싱한 트리로 치환(복사)."""
    class T(ast.NodeTransformer):
        def visit_Constant(self, n: ast.Constant) -> ast.AST:
            if isinstance(n.value, str):
                inner = unstring(n)
                if inner is not n:
                    return self.visit(inner)
            return n
    return T().visit(unstring(node))


def union_members(node: ast.AST) -> list[ast.AST] | None:
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
        out: list[ast.AST] = []
        for side in (node.left, node.right):
            m = union_members(side)
            out.extend(m if m is not None else [side])
        return out
    if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name) and node.value.id in ("Optional", "Union"):
        sl = node.slice
        elts = list(sl.elts) if isinstance(sl, ast.Tuple) else [sl]
        out = []
        for e in elts:
            m = union_members(e)
            out.extend(m if m is not None else [e])
        return out
    return None


def scan_annotation(ann: ast.AST | None, b: Bindings) -> list[dict]:
    """주석 하나에서 컨테이너[…, object|Any] 히트 목록 — position: top | nested · variant: exact | union-value."""
    if ann is None:
        return []
    root = deep_unstring(ann)
    hits: list[dict] = []
    literal_ids: set[int] = set()
    for n in ast.walk(root):
        if isinstance(n, ast.Subscript) and isinstance(n.value, ast.Name) and n.value.id == "Literal":
            literal_ids |= {id(v) for v in ast.walk(n.slice)}
    for n in ast.walk(root):
        if id(n) in literal_ids or not isinstance(n, ast.Subscript):
            continue
        cname = b.container_name(n.value)
        if cname is None:
            continue
        sl = n.slice
        elts = list(sl.elts) if isinstance(sl, ast.Tuple) else [sl]
        if not elts:
            continue
        last = elts[-1]
        key = ast.unparse(elts[0]) if len(elts) >= 2 else "?"
        vk = b.value_kind(last)
        variant = "exact"
        if vk is None:
            members = union_members(last)
            if members is not None:
                kinds = [b.value_kind(m) for m in members]
                if any(k is not None for k in kinds):
                    vk = next(k for k in kinds if k is not None)
                    variant = "union-value"
        if vk is None:
            continue
        hits.append({
            "container": cname, "value": vk, "key": key, "variant": variant,
            "position": "top" if n is root else "nested",
            "text": ast.unparse(n),
        })
    return hits


def bc_of(rel: Path) -> str:
    parts = rel.parts
    if len(parts) >= 2 and parts[0] == "application":
        return f"application/{parts[1]}"
    if len(parts) >= 3 and parts[0] == "framework":
        return "/".join(parts[:3])
    return parts[0] if parts else "?"


def scan_file(path: Path, root: Path, out: list[dict], jl: list[dict]) -> None:
    try:
        mod = ast.parse(path.read_text(encoding="utf-8"))
    except (SyntaxError, OSError, UnicodeDecodeError):
        return
    rel = path.relative_to(root)
    b = Bindings(mod)
    parent: dict[ast.AST, ast.AST] = {}
    for node in ast.walk(mod):
        for child in ast.iter_child_nodes(node):
            parent[child] = node

    def emit(site: str, lineno: int, label: str, ann: ast.AST | None, fn: str | None, own_line: int | None = None) -> None:
        # `line` 은 #645 와 같은 좌표(시그니처는 def 줄) · `own_line` 은 인자 자신의 줄(다중 행 시그니처 대조용)
        for h in scan_annotation(ann, b):
            out.append({"file": str(rel), "line": lineno, "own_line": own_line or lineno, "bc": bc_of(rel),
                        "site": site, "label": label, "fn": fn, "future": b.future_annotations, **h})

    for node in ast.walk(mod):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            a = node.args
            for arg in list(a.posonlyargs) + list(a.args) + list(a.kwonlyargs):
                emit("sig-param", node.lineno, arg.arg, arg.annotation, node.name, arg.lineno)
            for star, arg in (("*", a.vararg), ("**", a.kwarg)):
                if arg is not None:
                    emit("sig-star", node.lineno, f"{star}{arg.arg}", arg.annotation, node.name, arg.lineno)
            emit("sig-return", node.lineno, "->", node.returns, node.name, node.returns.lineno if node.returns is not None else None)
        elif isinstance(node, ast.AnnAssign):
            p = parent.get(node)
            site = "class-attr" if isinstance(p, ast.ClassDef) else "variable"
            emit(site, node.lineno, ast.unparse(node.target), node.annotation, None)

    # ── json.load(s) ⓓ 후보 ──
    def is_json_load(call: ast.Call) -> str | None:
        f = call.func
        if isinstance(f, ast.Attribute) and f.attr in ("load", "loads") and b.dotted(f.value) == "json":
            return f"json.{f.attr}"
        if isinstance(f, ast.Name) and f.id in b.json_names:
            return f"json.{f.id}"
        return None

    def sibling_after(stmt: ast.AST) -> ast.AST | None:
        p = parent.get(stmt)
        if p is None:
            return None
        for field in ("body", "orelse", "finalbody"):
            body = getattr(p, field, None)
            if isinstance(body, list) and stmt in body:
                i = body.index(stmt)
                return body[i + 1] if i + 1 < len(body) else None
        return None

    def names_in(node: ast.AST) -> set[str]:
        return {n.id for n in ast.walk(node) if isinstance(n, ast.Name)}

    for node in ast.walk(mod):
        if not isinstance(node, ast.Call):
            continue
        kind = is_json_load(node)
        if kind is None:
            continue
        p = parent.get(node)
        # 부모가 파서 호출의 인자인가
        consumer = "?"
        candidate = True
        if isinstance(p, ast.Call) and node in p.args:
            pf = p.func
            if isinstance(pf, ast.Attribute) and pf.attr in PARSER_METHODS:
                consumer, candidate = f"parser-method:{pf.attr}", False
            elif isinstance(pf, ast.Name):
                consumer, candidate = f"named-call:{pf.id}", pf.id in {"dict", "list", "tuple", "set", "str", "cast"}
            elif isinstance(pf, ast.Attribute):
                consumer, candidate = f"method-call:{pf.attr}", pf.attr in {"append", "extend", "update", "get"}
        elif isinstance(p, ast.Call) and any(kw.value is node for kw in p.keywords):
            pf = p.func
            consumer = f"kw-arg:{ast.unparse(pf)}"
            candidate = not (isinstance(pf, ast.Attribute) and pf.attr in PARSER_METHODS)
        elif isinstance(p, (ast.Assign, ast.AnnAssign)):
            consumer = "assign"
            ann = ast.unparse(p.annotation) if isinstance(p, ast.AnnAssign) else None
            nxt = sibling_after(p)
            tg = p.targets[0] if isinstance(p, ast.Assign) else p.target
            tnames = names_in(tg)
            if isinstance(nxt, ast.If) and any(
                isinstance(c, ast.Call) and isinstance(c.func, ast.Name) and c.func.id == "isinstance"
                and names_in(c) & tnames for c in ast.walk(nxt.test)
            ):
                consumer = "assign+next-isinstance"
            elif nxt is not None and any(
                isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute) and c.func.attr in PARSER_METHODS
                and names_in(c) & tnames for c in ast.walk(nxt)
            ):
                consumer = "assign+next-parser"
            elif nxt is not None and any(
                isinstance(c, ast.Call) and isinstance(c.func, ast.Name) and names_in(c) & tnames
                and c.func.id not in {"isinstance", "len", "print", "str", "list", "dict", "sorted"}
                for c in ast.walk(nxt)
            ):
                consumer = "assign+next-named-call"
            if ann:
                consumer += f" [{ann}]"
        elif isinstance(p, ast.Return):
            consumer = "return"
        elif isinstance(p, ast.Subscript):
            consumer = "subscript"
        elif isinstance(p, ast.Attribute):
            consumer = f"attr:.{p.attr}"
        elif isinstance(p, ast.Expr):
            consumer = "expr-stmt"
        else:
            consumer = type(p).__name__
        fn = None
        q: ast.AST | None = node
        while q is not None:
            q = parent.get(q)
            if isinstance(q, (ast.FunctionDef, ast.AsyncFunctionDef)):
                fn = q.name
                break
        jl.append({"file": str(rel), "line": node.lineno, "bc": bc_of(rel), "kind": kind, "consumer": consumer,
                   "candidate": candidate, "fn": fn, "src": ast.unparse(p)[:140] if p is not None else ""})


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("target")
    ap.add_argument("--findings")
    ap.add_argument("--out")
    ap.add_argument("--label", default="")
    ns = ap.parse_args()
    root = Path(ns.target).resolve()
    files = [p for p in sorted(root.rglob("*.py")) if is_target_file(p, root)]
    hits: list[dict] = []
    jl: list[dict] = []
    for f in files:
        scan_file(f, root, hits, jl)
    if ns.out:
        with open(ns.out, "w", encoding="utf-8") as fh:
            for h in hits:
                fh.write(json.dumps({"rule": "#647", **h}, ensure_ascii=False) + "\n")
            for j in jl:
                fh.write(json.dumps({"rule": "json-load", **j}, ensure_ascii=False) + "\n")
    exact = [h for h in hits if h["variant"] == "exact"]
    print(f"== {ns.label or root.name}: 파일 {len(files)} · #647 exact 히트 {len(exact)} (union-값 변종 {len(hits) - len(exact)}) · 줄 {len({(h['file'], h['line']) for h in exact})}")
    C = collections.Counter
    print("  자리:", dict(C(h["site"] for h in exact)))
    print("  위치:", dict(C(h["position"] for h in exact)))
    print("  값:", dict(C(h["value"] for h in exact)), " 컨테이너:", dict(C(h["container"] for h in exact)))
    print("  키:", dict(C(h["key"] for h in exact).most_common(6)))
    print("  자리×위치:", dict(C((h["site"], h["position"]) for h in exact)))
    print("  future-annotations 파일 비율(히트 기준):", dict(C(h["future"] for h in exact)))
    print("  BC별(줄):")
    per_bc: dict[str, set] = collections.defaultdict(set)
    per_bc_site: dict[str, C] = collections.defaultdict(C)
    for h in exact:
        per_bc[h["bc"]].add((h["file"], h["line"]))
        per_bc_site[h["bc"]][h["site"]] += 1
    for bc, s in sorted(per_bc.items(), key=lambda kv: -len(kv[1])):
        print(f"    {len(s):5d}  {bc}  {dict(per_bc_site[bc])}")
    star = [h for h in hits if h["site"] == "sig-star"]
    print("  별표 인자 히트(dict[…] 주석을 단 *args/**kwargs):", len(star))
    print("  Mapping[str, object] 매개변수(top) — R-3448 취지 자리 후보:",
          len([h for h in exact if h["site"] == "sig-param" and h["container"] == "Mapping" and h["value"] == "object" and h["position"] == "top"]))
    print(f"== json.load(s) 호출 {len(jl)} · ⓓ 후보 {sum(1 for j in jl if j['candidate'])}")
    print("  소비자:", dict(C(j["consumer"].split(' [')[0] for j in jl).most_common(12)))
    print("  후보 BC별:", dict(C(j["bc"] for j in jl if j["candidate"])))
    if ns.findings:
        info645: set[tuple[str, int]] = set()
        viol645: set[tuple[str, int]] = set()
        for line in open(ns.findings, encoding="utf-8"):
            r = json.loads(line)
            if r.get("rule") != "#645":
                continue
            f, _, ln = r["file"].rpartition(":")
            (info645 if r.get("severity") == "info" else viol645).add((f, int(ln)))
        any_lines = {(h["file"], h["line"]) for h in exact if h["value"] == "Any"}
        obj_lines = {(h["file"], h["line"]) for h in exact if h["value"] == "object"}
        print(f"== #645 겹침: #645 ⓓ 후보 줄 {len(info645)} · #647 Any 줄 {len(any_lines)} · 교집합(이중 보고) {len(any_lines & info645)}"
              f" · #647 Any 줄 중 #645 미보고 {len(any_lines - info645 - viol645)} · #647 object 줄(#645 무관) {len(obj_lines)}"
              f" · #645 위반(bare)과 같은 줄 {len(any_lines & viol645)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
