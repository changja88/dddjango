#!/usr/bin/env python3
"""S-5 시제품 — AST 바인딩만으로 세 형상을 판정한다(현장 보고 3 ⓪ 실측용 · 검사기 아님).

  ⓐ status_union   함수 반환 주석에 ninja.Status Subscript 가 2개 이상
  ⓑ response_base  route 데코레이터 response={…} 값이 같은 BC bc_error_schema.py 안에서
                    하위 클래스를 가진 base 클래스 (union 이면 각 항 판정)
  ⓒ schema_rootmodel 클래스가 ninja.Schema 와 pydantic.RootModel 을 함께 상속

부가 관측(정보성 · 위반 아님):
  rootmodel_only   RootModel 단독 상속 클래스(파일 위치 포함 — schema_out.py 밖이면 표시)
  status_union_test 테스트 파일의 ⓐ 형태(운영 경로 밖)
  response_base_justified ⓑ 자리에서 같은 함수 본문이 그 status 로 base 자체를 생성해 반환(명시값 base)

사용: proto_ninja3.py --root <프로젝트 루트> [--label L] [--jsonl out] [--include-tests]
  루트는 여러 번 줄 수 있다. 루트 밑 application/** 의 .py 전부를 읽되, 운영/테스트를 구분한다.
"""
from __future__ import annotations

import argparse
import ast
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

TEST_DIRS = {"test", "tests"}
SKIP_DIRS = {".venv", "venv", "node_modules", "__pycache__", ".git", "migrations", ".dddjango"}
STATUS_ORIGINS = {"ninja.Status", "ninja.responses.Status"}
SCHEMA_ORIGINS = {"ninja.Schema", "ninja.schema.Schema"}
ROOTMODEL_ORIGINS = {"pydantic.RootModel", "pydantic.root_model.RootModel"}
ROUTE_DECOS = {"get", "post", "put", "patch", "delete", "head", "options", "api_operation", "route"}


@dataclass
class Module:
    root: Path
    path: Path
    rel: Path
    module: str
    tree: ast.Module
    bindings: dict[str, str] = field(default_factory=dict)  # local name -> dotted origin
    classes: dict[str, ast.ClassDef] = field(default_factory=dict)
    is_test: bool = False


def module_name(rel: Path) -> str:
    parts = list(rel.with_suffix("").parts)
    if parts and parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def is_test_path(rel: Path) -> bool:
    return bool(set(rel.parts) & TEST_DIRS) or rel.name.startswith("test_") or rel.name.endswith("_test.py") or rel.name == "conftest.py"


def collect_bindings(mod: Module) -> None:
    pkg = mod.module.rsplit(".", 1)[0] if "." in mod.module else ""
    if mod.path.name == "__init__.py":
        pkg = mod.module
    for node in mod.tree.body:
        if isinstance(node, ast.Import):
            for a in node.names:
                mod.bindings[(a.asname or a.name).split(".")[0]] = a.name if a.asname else a.name.split(".")[0]
        elif isinstance(node, ast.ImportFrom):
            base = node.module or ""
            if node.level:
                up = pkg.split(".") if pkg else []
                up = up[: len(up) - (node.level - 1)] if node.level - 1 else up
                base = ".".join([*up, base]) if base else ".".join(up)
            for a in node.names:
                mod.bindings[a.asname or a.name] = f"{base}.{a.name}"
        elif isinstance(node, ast.ClassDef):
            mod.classes[node.name] = node
            mod.bindings[node.name] = f"{mod.module}.{node.name}"
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            # 단순 재별칭: X = Y  (Y 가 이미 바인딩된 이름이면 따라간다)
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            value = node.value
            if isinstance(value, ast.Name) and value.id in mod.bindings:
                for t in targets:
                    if isinstance(t, ast.Name):
                        mod.bindings[t.id] = mod.bindings[value.id]


def origin_of(expr: ast.AST, mod: Module) -> str | None:
    """Name/Attribute 표현의 dotted origin(모듈 import 바인딩 해소)."""
    if isinstance(expr, ast.Name):
        return mod.bindings.get(expr.id, expr.id)
    if isinstance(expr, ast.Attribute):
        head = origin_of(expr.value, mod)
        return f"{head}.{expr.attr}" if head else None
    if isinstance(expr, ast.Constant) and isinstance(expr.value, str):
        try:
            return origin_of(ast.parse(expr.value, mode="eval").body, mod)
        except SyntaxError:
            return None
    return None


def norm_status(origin: str | None) -> bool:
    return origin in STATUS_ORIGINS


def flatten_union(expr: ast.AST, mod: Module) -> list[ast.AST]:
    """A | B · Union[A, B] · Optional[A] · 문자열 주석을 항 목록으로 평탄화한다."""
    if isinstance(expr, ast.Constant) and isinstance(expr.value, str):
        try:
            return flatten_union(ast.parse(expr.value, mode="eval").body, mod)
        except SyntaxError:
            return [expr]
    if isinstance(expr, ast.BinOp) and isinstance(expr.op, ast.BitOr):
        return [*flatten_union(expr.left, mod), *flatten_union(expr.right, mod)]
    if isinstance(expr, ast.Subscript):
        head = origin_of(expr.value, mod)
        if head in {"typing.Union", "Union", "typing.Optional", "Optional"}:
            parts = expr.slice.elts if isinstance(expr.slice, ast.Tuple) else [expr.slice]
            out: list[ast.AST] = []
            for p in parts:
                out.extend(flatten_union(p, mod))
            return out
    return [expr]


def count_status_boxes(annotation: ast.AST, mod: Module) -> tuple[int, list[str]]:
    terms = flatten_union(annotation, mod)
    boxes = 0
    rendered: list[str] = []
    for t in terms:
        if isinstance(t, ast.Subscript) and norm_status(origin_of(t.value, mod)):
            boxes += 1
        rendered.append(ast.unparse(t))
    return boxes, rendered


def iter_functions(tree: ast.Module):
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            yield node


def is_route_decorator(deco: ast.AST, mod: Module) -> bool:
    target = deco.func if isinstance(deco, ast.Call) else deco
    if isinstance(target, ast.Attribute):
        return target.attr in ROUTE_DECOS
    if isinstance(target, ast.Name):
        return target.id in ROUTE_DECOS
    return False


def response_keyword(deco: ast.AST) -> ast.AST | None:
    if isinstance(deco, ast.Call):
        for kw in deco.keywords:
            if kw.arg == "response":
                return kw.value
    return None


def literal_status(key: ast.AST) -> int | str | None:
    if isinstance(key, ast.Constant) and isinstance(key.value, (int, str)):
        return key.value
    return ast.unparse(key)


@dataclass
class ErrorHierarchy:
    """BC 별 bc_error_schema.py 상속 그래프(파일 안에서만)."""
    classes: dict[str, list[str]]  # class -> direct bases(같은 파일 이름 · 아니면 origin)
    children: dict[str, list[str]]


def build_hierarchy(mod: Module) -> ErrorHierarchy:
    classes: dict[str, list[str]] = {}
    children: dict[str, list[str]] = {}
    for name, node in mod.classes.items():
        bases = []
        for b in node.bases:
            o = origin_of(b, mod) or ast.unparse(b)
            bases.append(o)
        classes[name] = bases
    for name, bases in classes.items():
        for b in bases:
            short = b.rsplit(".", 1)[-1]
            if short in classes and b.startswith(mod.module):
                children.setdefault(short, []).append(name)
    return ErrorHierarchy(classes, children)


def scan(root: Path, label: str, include_tests: bool) -> list[dict]:
    root = root.resolve()
    findings: list[dict] = []
    mods: dict[Path, Module] = {}
    app = root / "application"
    if not app.is_dir():
        return [{"kind": "no_application_dir", "label": label, "root": str(root)}]
    for p in sorted(app.rglob("*.py")):
        rel = p.relative_to(root)
        if set(rel.parts) & SKIP_DIRS:
            continue
        try:
            tree = ast.parse(p.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError) as exc:
            findings.append({"kind": "parse_error", "label": label, "file": str(rel), "detail": str(exc)})
            continue
        m = Module(root, p, rel, module_name(rel), tree, is_test=is_test_path(rel))
        collect_bindings(m)
        mods[rel] = m

    hierarchies: dict[str, ErrorHierarchy] = {}  # module -> hierarchy
    for rel, m in mods.items():
        if rel.name == "bc_error_schema.py":
            hierarchies[m.module] = build_hierarchy(m)

    for rel, m in mods.items():
        # ⓐ / ⓐ-test
        for fn in iter_functions(m.tree):
            if fn.returns is None:
                continue
            boxes, terms = count_status_boxes(fn.returns, m)
            if boxes >= 2:
                routed = any(is_route_decorator(d, m) for d in fn.decorator_list)
                findings.append({
                    "kind": "status_union" if not m.is_test else "status_union_test",
                    "label": label, "file": str(rel), "line": fn.lineno, "name": fn.name,
                    "boxes": boxes, "terms": terms, "routed": routed,
                })
        # 변수 주석의 상자 둘(테스트 포함 · 정보성)
        for node in ast.walk(m.tree):
            if isinstance(node, ast.AnnAssign) and node.annotation is not None:
                boxes, terms = count_status_boxes(node.annotation, m)
                if boxes >= 2:
                    findings.append({
                        "kind": "status_union_annassign" + ("_test" if m.is_test else ""),
                        "label": label, "file": str(rel), "line": node.lineno,
                        "name": ast.unparse(node.target), "boxes": boxes, "terms": terms,
                    })
        if m.is_test and not include_tests:
            pass
        # ⓑ
        if not m.is_test:
            for fn in iter_functions(m.tree):
                for deco in fn.decorator_list:
                    resp = response_keyword(deco)
                    if resp is None or not isinstance(resp, ast.Dict):
                        if resp is not None and not isinstance(resp, ast.Dict):
                            findings.append({"kind": "response_non_dict", "label": label, "file": str(rel),
                                             "line": fn.lineno, "name": fn.name, "value": ast.unparse(resp)})
                        continue
                    for key, value in zip(resp.keys, resp.values):
                        if key is None:
                            findings.append({"kind": "response_splat", "label": label, "file": str(rel),
                                             "line": fn.lineno, "name": fn.name})
                            continue
                        status = literal_status(key)
                        for term in flatten_union(value, m):
                            o = origin_of(term, m)
                            if o is None:
                                continue
                            mod_part, _, cls = o.rpartition(".")
                            h = hierarchies.get(mod_part)
                            if h is None or cls not in h.classes:
                                continue
                            kids = h.children.get(cls, [])
                            if not kids:
                                continue
                            # 정당 base 판정: 본문에서 Status(<status>, Base(...)) 또는 x: Base = Base(...) 후 반환
                            justified = _base_constructed_for_status(fn, m, status, term)
                            findings.append({
                                "kind": "response_base_justified" if justified else "response_base",
                                "label": label, "file": str(rel), "line": fn.lineno, "name": fn.name,
                                "status": status, "base": cls, "children": kids,
                                "value_is_union": len(flatten_union(value, m)) > 1,
                                "error_status": isinstance(status, int) and 400 <= status <= 599,
                            })
        # ⓒ + RootModel 관측
        for cname, node in m.classes.items():
            base_origins = []
            for b in node.bases:
                head = b.value if isinstance(b, ast.Subscript) else b
                base_origins.append((origin_of(head, m), isinstance(b, ast.Subscript)))
            has_schema = any(o in SCHEMA_ORIGINS for o, _ in base_origins)
            has_root = any(o in ROOTMODEL_ORIGINS for o, _ in base_origins)
            if has_schema and has_root:
                findings.append({"kind": "schema_rootmodel", "label": label, "file": str(rel), "line": node.lineno,
                                 "name": cname, "bases": [ast.unparse(b) for b in node.bases],
                                 "in_schema_out": rel.name == "schema_out.py", "is_test": m.is_test})
            elif has_root:
                findings.append({"kind": "rootmodel_only", "label": label, "file": str(rel), "line": node.lineno,
                                 "name": cname, "bases": [ast.unparse(b) for b in node.bases],
                                 "in_schema_out": rel.name == "schema_out.py", "in_driving": "driving_layer" in rel.parts,
                                 "is_test": m.is_test})
    findings.append({"kind": "scan_summary", "label": label, "root": str(root), "modules": len(mods),
                     "production_modules": sum(1 for m in mods.values() if not m.is_test),
                     "bc_error_schema_files": len(hierarchies)})
    return findings


def _base_constructed_for_status(fn: ast.AST, m: Module, status: int | str | None, base_term: ast.AST) -> bool:
    base_origin = origin_of(base_term, m)
    # 지역 변수 주석 x: T = T(...) 을 추적
    local_types: dict[str, str | None] = {}
    local_ctor: dict[str, str | None] = {}
    for node in ast.walk(fn):
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            local_types[node.target.id] = origin_of(node.annotation, m)
            if isinstance(node.value, ast.Call):
                local_ctor[node.target.id] = origin_of(node.value.func, m)
        elif isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            if isinstance(node.value, ast.Call):
                local_ctor[node.targets[0].id] = origin_of(node.value.func, m)
    for node in ast.walk(fn):
        if isinstance(node, ast.Return) and isinstance(node.value, ast.Call):
            call = node.value
            if not norm_status(origin_of(call.func, m)) or len(call.args) != 2:
                continue
            st = call.args[0]
            st_val = st.value if isinstance(st, ast.Constant) else None
            if isinstance(status, int) and st_val != status:
                continue
            val = call.args[1]
            if isinstance(val, ast.Call) and origin_of(val.func, m) == base_origin:
                return True
            if isinstance(val, ast.Name) and local_ctor.get(val.id) == base_origin:
                return True
    return False


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", action="append", required=True)
    ap.add_argument("--label", action="append", default=[])
    ap.add_argument("--jsonl")
    ap.add_argument("--include-tests", action="store_true")
    ns = ap.parse_args(argv)
    labels = ns.label + [Path(r).name for r in ns.root[len(ns.label):]]
    all_findings: list[dict] = []
    for root, label in zip(ns.root, labels):
        all_findings.extend(scan(Path(root), label, ns.include_tests))
    if ns.jsonl:
        with open(ns.jsonl, "w", encoding="utf-8") as f:
            for item in all_findings:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
    for item in all_findings:
        print(json.dumps(item, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
