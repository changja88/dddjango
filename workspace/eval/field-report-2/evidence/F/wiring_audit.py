"""composition root 주입 지점 추출 + 정적 시그니처 대조 (AST 전용, 실행 없음)."""
from __future__ import annotations
import ast, sys, json
from pathlib import Path

REPO = Path(sys.argv[1]).resolve()
LABEL = sys.argv[2] if len(sys.argv) > 2 else REPO.name
_cache: dict[Path, ast.Module] = {}

def parse(path: Path) -> ast.Module | None:
    if path in _cache: return _cache[path]
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except Exception:
        return None
    _cache[path] = tree
    return tree

def module_to_path(modname: str) -> Path | None:
    p = REPO / modname.replace(".", "/")
    if (p / "__init__.py").exists(): return p / "__init__.py"
    if p.with_suffix(".py").exists(): return p.with_suffix(".py")
    return None

def import_map(tree: ast.Module) -> dict[str, tuple[str, str | None]]:
    """local name -> (module, attr|None)"""
    m: dict[str, tuple[str, str | None]] = {}
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.module:
            for a in node.names:
                m[a.asname or a.name] = (node.module, a.name)
        elif isinstance(node, ast.Import):
            for a in node.names:
                m[a.asname or a.name.split(".")[0]] = (a.name, None)
    return m

def find_def(tree: ast.Module, name: str):
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.name == name:
            return node
    for node in tree.body:
        if type(node).__name__ == "TypeAlias" and isinstance(node.name, ast.Name) and node.name.id == name:
            return node
    # module-level assignment (object reference)
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == name: return node
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id == name:
            return node
    return None

def resolve_symbol(tree: ast.Module, name: str):
    """returns (node, defining_tree, modname) for a local name (import-following)."""
    local = find_def(tree, name)
    if local is not None:
        return local, tree, "<local>"
    im = import_map(tree)
    if name not in im: return None, None, None
    mod, attr = im[name]
    if attr is None:
        return ("module", mod), None, mod
    path = module_to_path(mod)
    if path is None:
        # maybe `from pkg import submodule`
        sub = module_to_path(f"{mod}.{attr}")
        if sub is not None: return ("module", f"{mod}.{attr}"), None, f"{mod}.{attr}"
        return None, None, mod
    t = parse(path)
    if t is None: return None, None, mod
    node = find_def(t, attr)
    if node is None:
        # re-export? try submodule
        sub = module_to_path(f"{mod}.{attr}")
        if sub is not None: return ("module", f"{mod}.{attr}"), None, f"{mod}.{attr}"
        # follow re-export in __init__
        im2 = import_map(t)
        if attr in im2:
            return resolve_symbol(t, attr)
        return None, t, mod
    return node, t, mod

def resolve_attr_chain(tree: ast.Module, expr: ast.expr):
    """Attribute chain a.b.c -> (node, tree, qualname)"""
    parts = []
    cur = expr
    while isinstance(cur, ast.Attribute):
        parts.append(cur.attr); cur = cur.value
    if not isinstance(cur, ast.Name):
        return None, None, ast.unparse(expr), "비단순 속성 체인(인스턴스 메서드 등)"
    parts.append(cur.id); parts.reverse()
    node, t, mod = resolve_symbol(tree, parts[0])
    if node is None:
        return None, None, ".".join(parts), f"이름 해석 실패: {parts[0]}"
    rest = parts[1:]
    while rest:
        if isinstance(node, tuple) and node[0] == "module":
            modname = node[1]
            path = module_to_path(modname)
            t = parse(path) if path else None
            if t is None: return None, None, ".".join(parts), f"모듈 파싱 실패: {modname}"
            nxt = find_def(t, rest[0])
            if nxt is None:
                sub = module_to_path(f"{modname}.{rest[0]}")
                if sub is not None:
                    node = ("module", f"{modname}.{rest[0]}"); rest = rest[1:]; continue
                im2 = import_map(t)
                if rest[0] in im2:
                    node, t, mod = resolve_symbol(t, rest[0]); rest = rest[1:]; continue
                return None, t, ".".join(parts), f"모듈 {modname} 에 {rest[0]} 없음"
            node = nxt; rest = rest[1:]
        elif isinstance(node, ast.ClassDef):
            meth = next((n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == rest[0]), None)
            if meth is None: return None, t, ".".join(parts), f"클래스 {node.name} 에 메서드 {rest[0]} 없음"
            node = meth; rest = rest[1:]
        else:
            return None, t, ".".join(parts), "속성 체인 해석 불가"
    return node, t, ".".join(parts), None

def params_of(fn, drop_self: bool) -> list[dict]:
    a = fn.args
    out = []
    pos = list(a.posonlyargs) + list(a.args)
    n_defaults = len(a.defaults)
    for i, p in enumerate(pos):
        has_default = i >= len(pos) - n_defaults
        out.append({"name": p.arg, "default": has_default, "kind": "posonly" if p in a.posonlyargs else "pos"})
    for p, d in zip(a.kwonlyargs, a.kw_defaults):
        out.append({"name": p.arg, "default": d is not None, "kind": "kwonly"})
    if a.vararg: out.append({"name": "*" + a.vararg.arg, "default": True, "kind": "vararg"})
    if a.kwarg: out.append({"name": "**" + a.kwarg.arg, "default": True, "kind": "varkw"})
    if drop_self and out and out[0]["kind"] in ("pos", "posonly") and out[0]["name"] in ("self", "cls"):
        out = out[1:]
    return out

def fmt_params(ps: list[dict]) -> str:
    return "(" + ", ".join(p["name"] + ("=…" if p["default"] and not p["name"].startswith("*") else "") for p in ps) + ")"

def receiver_param_annotation(cls: ast.ClassDef, cls_tree: ast.Module, param: str):
    """find annotation expr for param in __init__ or dataclass field; follow one base level."""
    init = next((n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == "__init__"), None)
    if init is not None:
        for p in init.args.posonlyargs + init.args.args + init.args.kwonlyargs:
            if p.arg == param: return p.annotation, cls_tree, "__init__"
        return None, cls_tree, "__init__에 해당 매개변수 없음"
    for n in cls.body:
        if isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name) and n.target.id == param:
            return n.annotation, cls_tree, "dataclass field"
    for b in cls.bases:
        node, t, q, err = resolve_attr_chain(cls_tree, b)
        if isinstance(node, ast.ClassDef):
            r = receiver_param_annotation(node, t, param)
            if r[0] is not None: return r
    return None, cls_tree, "생성자 매개변수 미발견"

def annotation_target(ann, tree):
    """annotation expr -> (kind, payload). kind: protocol_call / callable / class / unknown"""
    if ann is None: return "unknown", "주석 없음"
    if isinstance(ann, ast.Constant) and isinstance(ann.value, str):
        try: ann = ast.parse(ann.value, mode="eval").body
        except Exception: return "unknown", "문자열 주석 파싱 실패"
    if isinstance(ann, ast.Subscript):
        base = ast.unparse(ann.value)
        if base.split(".")[-1] == "Callable":
            sl = ann.slice
            if isinstance(sl, ast.Tuple) and sl.elts and isinstance(sl.elts[0], ast.List):
                return "callable", len(sl.elts[0].elts)
            return "callable", None
        return annotation_target(ann.value, tree)
    if isinstance(ann, ast.BinOp):  # X | None
        return annotation_target(ann.left, tree)
    node, t, q, err = resolve_attr_chain(tree, ann)
    if type(node).__name__ == "TypeAlias":
        return annotation_target(node.value, t)
    if isinstance(node, ast.ClassDef):
        bases = [ast.unparse(b) for b in node.bases]
        call = next((n for n in node.body if isinstance(n, ast.FunctionDef) and n.name == "__call__"), None)
        is_proto = any(b.split(".")[-1] == "Protocol" for b in bases)
        if call is not None:
            return "protocol_call", (q, params_of(call, True), is_proto)
        meths = [n.name for n in node.body if isinstance(n, ast.FunctionDef) and not n.name.startswith("_")]
        return "class", (q, is_proto, meths)
    return "unknown", f"주석 해석 실패 {ast.unparse(ann)}: {err}"

def classify_value(v: ast.expr):
    if isinstance(v, ast.Lambda): return "lambda", v, [], 0
    if isinstance(v, ast.Call):
        fn = ast.unparse(v.func)
        if fn.split(".")[-1] == "partial" and v.args:
            return "partial", v.args[0], [k.arg for k in v.keywords], len(v.args) - 1
        return None, None, [], 0
    if isinstance(v, ast.Name): return "name", v, [], 0
    if isinstance(v, ast.Attribute): return "attr", v, [], 0
    return None, None, [], 0

STDLIB_OK = {"uuid", "time", "datetime", "secrets", "random", "os", "json", "functools", "itertools", "pathlib"}
def stdlib_sig(tree, target):
    import importlib, inspect
    parts=[]; cur=target
    while isinstance(cur, ast.Attribute): parts.append(cur.attr); cur=cur.value
    if not isinstance(cur, ast.Name): return None
    parts.append(cur.id); parts.reverse()
    im=import_map(tree)
    if parts[0] not in im: return None
    mod, attr = im[parts[0]]
    top = mod.split(".")[0]
    if top not in STDLIB_OK: return None
    try:
        obj = importlib.import_module(mod)
        chain = ([attr] if attr else []) + parts[1:]
        for c in chain: obj = getattr(obj, c)
        sig = inspect.signature(obj)
    except Exception: return None
    ps=[]
    for name,p in sig.parameters.items():
        kind={p.POSITIONAL_ONLY:"posonly",p.POSITIONAL_OR_KEYWORD:"pos",p.KEYWORD_ONLY:"kwonly",p.VAR_POSITIONAL:"vararg",p.VAR_KEYWORD:"varkw"}[p.kind]
        nm = name if kind not in ("vararg","varkw") else ("*"+name if kind=="vararg" else "**"+name)
        ps.append({"name":nm,"default":p.default is not p.empty or kind in ("vararg","varkw"),"kind":kind})
    return f"{mod}.{'.'.join(chain)}(stdlib)", ps

def impl_signature(tree, target, kind, factory=None):
    """-> (qualname, params, note)"""
    if kind == "lambda":
        return "<lambda>", params_of(target, False), None
    # local nested def / local assignment inside the factory
    if factory is not None:
        base = target
        while isinstance(base, ast.Attribute): base = base.value
        if isinstance(base, ast.Name):
            for n in ast.walk(factory):
                if isinstance(n, ast.FunctionDef) and n.name == base.id and n is not factory and not isinstance(target, ast.Attribute):
                    return f"{factory.name}.<local>{n.name}", params_of(n, False), "팩토리 내부 지역 함수"
            for n in ast.walk(factory):
                if isinstance(n, (ast.Assign, ast.AnnAssign)):
                    tg = n.targets[0] if isinstance(n, ast.Assign) else n.target
                    if isinstance(tg, ast.Name) and tg.id == base.id:
                        val = n.value
                        if isinstance(target, ast.Attribute) and isinstance(val, ast.Call):
                            cn, ct, cq, ce = resolve_attr_chain(tree, val.func)
                            if isinstance(cn, ast.ClassDef):
                                meth = next((m for m in cn.body if isinstance(m, ast.FunctionDef) and m.name == target.attr), None)
                                if meth: return f"{cq}().{meth.name}", params_of(meth, True), "지역 인스턴스 메서드"
                        inner = val
                        if isinstance(inner, ast.Call) and ast.unparse(inner.func).split(".")[-1] == "cast" and len(inner.args) == 2:
                            inner = inner.args[1]
                        if isinstance(inner, (ast.Name, ast.Attribute)) and not isinstance(target, ast.Attribute):
                            cn, ct, cq, ce = resolve_attr_chain(tree, inner)
                            if isinstance(cn, ast.ClassDef):
                                init = next((m for m in cn.body if isinstance(m, ast.FunctionDef) and m.name == "__init__"), None)
                                if init: return f"{cq}(class)", params_of(init, True), "지역 대입된 클래스(생성자 시그니처)"
                                return f"{cq}(class)", [], "지역 대입된 클래스(__init__ 없음→무인자)"
                            if isinstance(cn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                                return cq, params_of(cn, False), "지역 대입된 함수"
                        return f"{factory.name}.<local>{base.id}", None, f"팩토리 내부 지역 대입: {ast.unparse(val)[:60]}"
    # X().method
    if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Call):
        cn, ct, cq, ce = resolve_attr_chain(tree, target.value.func)
        if isinstance(cn, ast.ClassDef):
            meth = next((m for m in cn.body if isinstance(m, ast.FunctionDef) and m.name == target.attr), None)
            if meth: return f"{cq}().{meth.name}", params_of(meth, True), "인스턴스 메서드"
            return f"{cq}().{target.attr}", None, "클래스에 메서드 미발견(상속?)"
    sl = stdlib_sig(tree, target)
    if sl: return sl[0], sl[1], "표준 라이브러리(inspect)"
    node, t, q, err = resolve_attr_chain(tree, target)
    if node is None: return q, None, err or "해석 실패"
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        # method? (defined inside class -> drop self) : we only get class methods via chain when class resolved
        is_method = any(isinstance(d, ast.Name) and d.id in ("staticmethod",) for d in node.decorator_list)
        drop = node.args.args and node.args.args[0].arg in ("self", "cls")
        return q, params_of(node, bool(drop)), None
    if isinstance(node, ast.ClassDef):
        init = next((n for n in node.body if isinstance(n, ast.FunctionDef) and n.name == "__init__"), None)
        if init: return q + "(class)", params_of(init, True), "클래스 주입(생성자 시그니처)"
        decos = [ast.unparse(d) for d in node.decorator_list]; bases = [ast.unparse(b) for b in node.bases]
        if any("dataclass" in d for d in decos) or any(b.split(".")[-1] in ("NamedTuple","BaseModel") for b in bases):
            kw_only = any("kw_only=True" in d for d in decos) or any(b.split(".")[-1]=="BaseModel" for b in bases)
            ps=[{"name":n.target.id,"default":n.value is not None,"kind":"kwonly" if kw_only else "pos"} for n in node.body if isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name)]
            return q + "(dataclass)", ps, "클래스 주입(dataclass/NamedTuple 필드)"
        return q + "(class)", None, "클래스 주입·__init__ 미발견"
    if isinstance(node, tuple): return q, None, "모듈 참조"
    return q, None, "함수가 아닌 모듈 수준 객체 참조(인스턴스)"

def compare(proto_params, impl_params, bound_kw, bound_pos):
    proto_names = {p["name"] for p in proto_params if not p["name"].startswith("*")}
    proto_varkw = any(p["kind"] == "varkw" for p in proto_params)
    impl = [p for p in impl_params]
    # consume positional bound
    consumed = 0
    for p in list(impl):
        if consumed >= bound_pos: break
        if p["kind"] in ("pos", "posonly"): impl.remove(p); consumed += 1
    impl = [p for p in impl if p["name"] not in bound_kw]
    impl_names = {p["name"] for p in impl if not p["name"].startswith("*")}
    impl_varkw = any(p["kind"] == "varkw" for p in impl)
    missing = sorted(p["name"] for p in impl if not p["default"] and p["name"] not in proto_names and not p["name"].startswith("*"))
    unaccepted = sorted(n for n in proto_names if n not in impl_names) if not impl_varkw else []
    posonly_clash = sorted(p["name"] for p in impl if p["kind"] == "posonly" and p["name"] in proto_names)
    issues = []
    if missing: issues.append("주입 함수 필수 인자 미공급: " + ",".join(missing))
    if unaccepted: issues.append("Protocol 인자 미수용: " + ",".join(unaccepted))
    if posonly_clash: issues.append("positional-only 충돌: " + ",".join(posonly_clash))
    return ("일치" if not issues else "불일치"), "; ".join(issues)

rows = []
roots = sorted(REPO.glob("application/*/composition_root/dependency_wiring.py"))
for wf in roots:
    bc = wf.parts[wf.parts.index("application") + 1]
    tree = parse(wf)
    if tree is None: continue
    for fn in [n for n in tree.body if isinstance(n, ast.FunctionDef)]:
        for call in ast.walk(fn):
            if not isinstance(call, ast.Call): continue
            if ast.unparse(call.func).split(".")[-1] == "partial": continue
            for kw in call.keywords:
                if kw.arg is None: continue
                kind, target, bkw, bpos = classify_value(kw.value)
                if kind is None: continue
                row = {"repo": LABEL, "bc": bc, "loc": f"{wf.relative_to(REPO)}:{kw.value.lineno}", "factory": fn.name,
                       "receiver": ast.unparse(call.func), "param": kw.arg, "expr": ast.unparse(kw.value), "kind": kind}
                # receiver class
                rnode, rtree, rq, rerr = resolve_attr_chain(tree, call.func)
                if not isinstance(rnode, ast.ClassDef):
                    row.update(verdict="판정 불가", detail=f"수신 클래스 해석 실패: {rerr}"); rows.append(row); continue
                ann, ann_tree, where = receiver_param_annotation(rnode, rtree, kw.arg)
                akind, payload = annotation_target(ann, ann_tree)
                iq, iparams, inote = impl_signature(tree, target, kind, fn)
                row["impl"] = f"{iq}{fmt_params(iparams) if iparams is not None else ''}"
                row["akind"] = akind; row["impl_resolved"] = iparams is not None
                row["scope"] = "callable" if (akind in ("protocol_call","callable") or iparams is not None or kind in ("partial","lambda")) else "value"
                if kind == "partial": row["impl"] += f" [bound kw={bkw} pos={bpos}]"
                if akind == "protocol_call":
                    q, pparams, is_proto = payload
                    row["proto"] = f"{q}.__call__{fmt_params(pparams)}" + ("" if is_proto else " (non-Protocol class)")
                    if iparams is None:
                        row.update(verdict="판정 불가", detail=f"주입 표현식 해석 불가: {inote}")
                    else:
                        v, d = compare(pparams, iparams, bkw, bpos)
                        row.update(verdict=v, detail=d or ("" if inote is None else inote))
                elif akind == "callable":
                    row["proto"] = f"Callable[{payload} args]"
                    if iparams is None: row.update(verdict="판정 불가", detail=f"주입 표현식 해석 불가: {inote}")
                    else:
                        ip = [p for p in iparams if p["name"] not in bkw]
                        posl = [p for p in ip if p["kind"] in ("pos","posonly")][bpos:]
                        req_pos = [p for p in posl if not p["default"]]
                        req_kw = [p for p in ip if p["kind"]=="kwonly" and not p["default"]]
                        has_var = any(p["kind"]=="vararg" for p in ip)
                        if payload is None: row.update(verdict="판정 불가", detail="Callable[..., R] 인자 불명")
                        elif req_kw: row.update(verdict="불일치", detail=f"필수 keyword-only 인자 미공급: {[p['name'] for p in req_kw]}")
                        elif len(req_pos) <= payload and (has_var or len(posl) >= payload):
                            row.update(verdict="일치", detail=f"Callable 위치 인자 {payload} ⊇ 필수 {len(req_pos)} ≤ 수용 {len(posl)}{'+*' if has_var else ''}" + (f" · {inote}" if inote else ""))
                        else: row.update(verdict="불일치", detail=f"Callable 위치 인자 {payload} vs 구현 필수 {len(req_pos)}/수용 {len(posl)}")
                elif akind == "class":
                    q, is_proto, meths = payload
                    row["proto"] = f"{q}{' (Protocol)' if is_proto else ''} 메서드 {meths}"
                    if iparams is not None and kind in ("name","attr","partial","lambda") and not (iq or "").endswith("(class)"):
                        row.update(verdict="불일치", detail=f"수신 타입은 __call__ 없는 {'Protocol' if is_proto else '클래스'}인데 함수 주입")
                    else:
                        row.update(verdict="판정 불가", detail=f"주입값이 인스턴스/클래스 참조 — 메서드 대조 범위 밖 ({inote})")
                else:
                    row["proto"] = "?"
                    row.update(verdict="판정 불가", detail=f"수신 주석 해석 불가 ({where}): {payload}")
                rows.append(row)
print(json.dumps(rows, ensure_ascii=False, indent=1))
