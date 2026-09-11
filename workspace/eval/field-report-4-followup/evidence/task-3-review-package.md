# task-3 review package

No commit was authorized. This package compares owned-file snapshots before this task with current bytes.

## dddjango/scripts/check-public-surface-annotation.py

Before SHA256: 788c9b1513ebab27e0ca2ae1d30cef0d4354f2bea873129fccaebc66c0c8074b
After SHA256: 60696373a2717f59128b8281896545be085bf8585616a859d9d38cb641ce8635

```diff
--- before/dddjango/scripts/check-public-surface-annotation.py
+++ after/dddjango/scripts/check-public-surface-annotation.py
@@ -705,41 +705,412 @@
     if cls is None or fn.name not in FRAMEWORK_OVERRIDE_EXEMPT:
         return False
     want = FRAMEWORK_OVERRIDE_EXEMPT[fn.name]
     for b in cls.bases:
         for base in _resolved_bases(b, bindings, aliases):  # 별칭 정의 전부(mixin-first 중간 ClassDef 포함) — `_is_declarative_class` 와 같은 해소
             if base in want or (fn.name == "deconstruct" and base.endswith("Field")):
                 return True
     return False
 
 
+# Closed origins verified from Django admin and Parler's admin inheritance.
+_ADMIN_BASES = {f"django.contrib.admin{module}.{name}"
+                for module in ("", ".options")
+                for name in ("ModelAdmin", "InlineModelAdmin", "TabularInline", "StackedInline")}
+_ADMIN_BASES |= {f"parler.admin.{name}" for name in (
+    "TranslatableAdmin", "TranslatableInlineModelAdmin", "TranslatableStackedInline", "TranslatableTabularInline")}
+_ADMIN_CONTEXT = {"changeform_view": "extra_context", "change_view": "extra_context",
+                  "add_view": "extra_context", "changelist_view": "extra_context", "render_change_form": "context"}
+_ADMIN_KWARGS = {"get_form", "get_formset", "get_fieldsets", "get_readonly_fields"}
+
+
+def _admin_classes(mod: ast.Module) -> dict[ast.ClassDef, str]:
+    """Resolve only static module origins/aliases and local bases; never execute an MRO."""
+    origins = _origin_bindings(mod)
+    aliases = _alias_defs(mod)
+    definitions: dict[str, ast.AST] = {}
+
+    def collect(stmts: list[ast.stmt]) -> None:
+        for st in stmts:
+            if isinstance(st, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
+                definitions[st.name] = st
+            elif isinstance(st, (ast.Assign, ast.AnnAssign)):
+                for target in st.targets if isinstance(st, ast.Assign) else [st.target]:
+                    for name in ast.walk(target):
+                        if isinstance(name, ast.Name):
+                            definitions[name.id] = st.value or st
+            elif isinstance(st, (ast.If, ast.Try)):
+                collect(st.body)
+                collect(st.orelse)
+                if isinstance(st, ast.Try):
+                    for handler in st.handlers:
+                        collect(handler.body)
+                    collect(st.finalbody)
+    collect(mod.body)
+    # Only current runtime alias plus TYPE_CHECKING alternatives are relevant.
+    aliases = {name: [(value, tc) for value, tc in values if tc or value is definitions.get(name)]
+               for name, values in aliases.items()}
+
+    def resolve(node: ast.AST, seen: frozenset[str]) -> str:
+        if isinstance(node, ast.Subscript):
+            return resolve(node.value, seen)
+        origin = _dotted(node, origins)
+        if origin in _ADMIN_BASES:
+            return "allow"
+        if isinstance(node, ast.Name) and node.id not in origins:
+            if node.id in seen:
+                return "candidate"
+            seen = seen | {node.id}
+            definition = definitions.get(node.id)
+            if isinstance(definition, ast.ClassDef):
+                statuses = [resolve(base, seen) for base in definition.bases]
+                return "allow" if "allow" in statuses else ("candidate" if "candidate" in statuses else "ordinary")
+            if isinstance(definition, (ast.Name, ast.Attribute, ast.Subscript)):
+                statuses = [resolve(value, seen) for value, _ in aliases.get(node.id, [(definition, False)])]
+                return "allow" if statuses and all(s == "allow" for s in statuses) else (
+                    "candidate" if any(s != "ordinary" for s in statuses) else "ordinary")
+            if definition is not None or node.id == "object":
+                return "ordinary"
+        return "candidate"
+
+    result: dict[ast.ClassDef, str] = {}
+    for cls in (n for n in mod.body if isinstance(n, ast.ClassDef)):
+        statuses = [resolve(base, frozenset({cls.name})) for base in cls.bases]
+        result[cls] = "allow" if "allow" in statuses else ("candidate" if "candidate" in statuses else "ordinary")
+    return result
+
+
+def _admin_context_policy(mod: ast.Module, rel: Path) -> dict[int, tuple[str, str]]:
+    """Annotation identity policy for connected admin UI bindings, not entire functions.
+
+    A context component includes copies/merges and directly passed private-helper
+    bindings. Consumption dominates unknown escapes, which dominate UI transport.
+    This is deliberately bounded AST analysis; it does not infer arbitrary callees.
+    """
+    policy: dict[int, tuple[str, str]] = {}
+    origins = _origin_bindings(mod)
+    module_shadowed: set[str] = set(origins)
+    pending: list[ast.AST] = list(mod.body)
+    while pending:
+        node = pending.pop()
+        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
+            module_shadowed.add(node.name)
+            continue
+        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
+            module_shadowed.add(node.id)
+        pending.extend(ast.iter_child_nodes(node))
+    rank = {"allow": 0, "candidate": 1, "ordinary": 2}
+    for cls, origin_status in _admin_classes(mod).items():
+        if origin_status == "ordinary":
+            continue
+        methods = {st.name: st for st in cls.body if isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef))}
+        # Duplicate/rebound methods cannot prove direct helper dispatch.
+        counts = {name: sum(isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef)) and st.name == name
+                            for st in cls.body) for name in methods}
+        for st in cls.body:
+            if isinstance(st, (ast.Assign, ast.AnnAssign)):
+                for target in st.targets if isinstance(st, ast.Assign) else [st.target]:
+                    if isinstance(target, ast.Name) and target.id in counts:
+                        counts[target.id] += 1
+        states: dict[tuple[ast.AST, str], str] = {}
+        edges: dict[tuple[ast.AST, str], set[tuple[ast.AST, str]]] = {}
+        annotations: dict[tuple[ast.AST, str], list[ast.AST]] = {}
+        active: set[ast.AST] = set()
+        parents: dict[ast.AST, ast.AST] = {}
+        bodies: dict[ast.AST, list[ast.AST]] = {}
+        shadowed: dict[ast.AST, set[str]] = {}
+
+        def put(fn: ast.AST, name: str, status: str = "allow") -> tuple[ast.AST, str]:
+            key = (fn, name)
+            states[key] = max(states.get(key, origin_status), status, key=rank.get)
+            return key
+
+        def link(left: tuple[ast.AST, str], right: tuple[ast.AST, str]) -> None:
+            edges.setdefault(left, set()).add(right)
+            edges.setdefault(right, set()).add(left)
+
+        def fixed(ann: ast.AST | None, *, kwargs: bool = False) -> None:
+            if ann is not None and (kwargs or any(isinstance(n, ast.Subscript) and _dotted(n.value, origins) in _ADMIN_BASES
+                                                 for n in ast.walk(_unstring(ann)))):
+                policy[id(ann)] = (origin_status, "확인된 admin framework override 슬롯" if origin_status == "allow" else "admin base 출처 불명")
+
+        for fn in methods.values():
+            if fn.name in _ADMIN_CONTEXT:
+                active.add(fn)
+            nodes: list[ast.AST] = []
+            def walk(node: ast.AST) -> None:
+                nodes.append(node)
+                for child in ast.iter_child_nodes(node):
+                    parents[child] = node
+                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)):
+                        continue
+                    walk(child)
+            for st in fn.body:
+                walk(st)
+            bodies[fn] = nodes
+            local_bindings: set[str] = set()
+            for st in fn.body:
+                _record_syntax_bindings(st, local_bindings)
+                if isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
+                    local_bindings.add(st.name)
+            local_bindings.update(a.arg for a in [*fn.args.posonlyargs, *fn.args.args, *fn.args.kwonlyargs])
+            local_bindings.update(a.arg for a in (fn.args.vararg, fn.args.kwarg) if a is not None)
+            shadowed[fn] = local_bindings
+            for arg in [*fn.args.posonlyargs, *fn.args.args, *fn.args.kwonlyargs]:
+                if arg.annotation is not None:
+                    annotations.setdefault((fn, arg.arg), []).append(arg.annotation)
+                if arg.arg == _ADMIN_CONTEXT.get(fn.name):
+                    put(fn, arg.arg)
+                    active.add(fn)
+            if fn.name in _ADMIN_KWARGS and fn.args.kwarg:
+                fixed(fn.args.kwarg.annotation, kwargs=True)
+            if fn.name == "get_inline_instances":
+                fixed(fn.returns)
+            for node in nodes:
+                if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
+                    annotations.setdefault((fn, node.target.id), []).append(node.annotation)
+        for st in cls.body:
+            if isinstance(st, ast.AnnAssign) and isinstance(st.target, ast.Name) and st.target.id == "inlines":
+                fixed(st.annotation)
+
+        def context_names(expr: ast.AST | None) -> set[str]:
+            if isinstance(expr, ast.Name):
+                return {expr.id}
+            if isinstance(expr, ast.BoolOp) and isinstance(expr.op, ast.Or) and len(expr.values) == 2 \
+                    and isinstance(expr.values[1], ast.Dict) and not expr.values[1].keys:
+                return context_names(expr.values[0])
+            if isinstance(expr, ast.Dict):
+                return set().union(*(context_names(v) for k, v in zip(expr.keys, expr.values) if k is None))
+            if isinstance(expr, ast.Call):
+                if isinstance(expr.func, ast.Name) and expr.func.id == "dict":
+                    return set().union(*(context_names(a) for a in expr.args))
+                if isinstance(expr.func, ast.Attribute) and expr.func.attr == "copy" and not expr.args and not expr.keywords:
+                    return context_names(expr.func.value)
+            return set()
+
+        def sink(call: ast.Call, fn: ast.AST) -> bool:
+            root = call.func
+            while isinstance(root, ast.Attribute):
+                root = root.value
+            if isinstance(root, ast.Name) and root.id in shadowed[fn] and root.id != "self":
+                return False
+            name = _dotted(call.func, origins)
+            if name in {"django.template.response.TemplateResponse", "django.shortcuts.render"}:
+                return True
+            if isinstance(call.func, ast.Attribute):
+                receiver = call.func.value
+                if isinstance(receiver, ast.Call) and isinstance(receiver.func, ast.Name) and receiver.func.id == "super":
+                    return "super" not in shadowed[fn] and (call.func.attr == fn.name or call.func.attr == "render_change_form")
+                return isinstance(receiver, ast.Name) and receiver.id == "self" and call.func.attr == "render_change_form"
+            return False
+
+        def each_context(expr: ast.AST | None) -> bool:
+            return isinstance(expr, ast.Call) and _dotted(expr.func, {}) == "self.admin_site.each_context"
+
+        def helper_of(expr: ast.AST | None) -> ast.FunctionDef | ast.AsyncFunctionDef | None:
+            if isinstance(expr, ast.Call) and isinstance(expr.func, ast.Attribute) and isinstance(expr.func.value, ast.Name) \
+                    and expr.func.value.id == "self" and expr.func.attr.startswith("_") and counts.get(expr.func.attr) == 1:
+                return methods[expr.func.attr]
+            return None
+
+        def reaches(start: ast.AST, target: ast.AST, visited: set[ast.AST]) -> bool:
+            if start is target:
+                return True
+            if start in visited:
+                return False
+            visited.add(start)
+            return any(callee is not None and reaches(callee, target, visited)
+                       for node in bodies[start] if isinstance(node, ast.Call) for callee in [helper_of(node)])
+
+        # Monotone reachability terminates on finite function/binding identities.
+        changed = True
+        while changed:
+            before = (len(states), len(active), sum(map(len, edges.values())))
+            for fn in list(active):
+                for node in bodies[fn]:
+                    if isinstance(node, (ast.Assign, ast.AnnAssign)):
+                        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
+                        sources = context_names(node.value)
+                        for target in targets:
+                            if isinstance(target, ast.Name) and each_context(node.value):
+                                put(fn, target.id)
+                        for target in targets:
+                            if isinstance(target, ast.Name):
+                                for source in sources:
+                                    link((fn, target.id), (fn, source))
+                    if isinstance(node, ast.Call) and sink(node, fn):
+                        # The context position is owned by the resolved framework sink.
+                        if _dotted(node.func, origins) in {"django.template.response.TemplateResponse", "django.shortcuts.render"}:
+                            arguments = node.args[2:3] + [kw.value for kw in node.keywords if kw.arg == "context"]
+                        elif isinstance(node.func, ast.Attribute) and node.func.attr == "render_change_form":
+                            arguments = node.args[1:2] + [kw.value for kw in node.keywords if kw.arg == "context"]
+                        else:
+                            arguments = [kw.value for kw in node.keywords if kw.arg == _ADMIN_CONTEXT.get(fn.name)]
+                        for value in arguments:
+                            for name in context_names(value):
+                                put(fn, name)
+                    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
+                        receiver = node.func.value
+                        if node.func.attr == "update":
+                            for source in set().union(*(context_names(a) for a in node.args)):
+                                for dest in context_names(receiver):
+                                    link((fn, dest), (fn, source))
+                        if isinstance(receiver, ast.Name) and receiver.id == "self" and node.func.attr.startswith("_"):
+                            helper = methods.get(node.func.attr)
+                            if helper is None or counts[node.func.attr] != 1:
+                                continue
+                            args = [*helper.args.posonlyargs, *helper.args.args][1:]
+                            passed = [(arg.arg, value) for arg, value in zip(args, node.args)]
+                            passed += [(kw.arg, kw.value) for kw in node.keywords if kw.arg]
+                            for label, value in passed:
+                                for source in context_names(value):
+                                    if (fn, source) in states:
+                                        active.add(helper)
+                                        put(helper, label)
+                                        link((fn, source), (helper, label))
+                            if helper in active:
+                                parent = parents.get(node)
+                                if isinstance(parent, (ast.Assign, ast.AnnAssign)) and parent.value is node:
+                                    targets = parent.targets if isinstance(parent, ast.Assign) else [parent.target]
+                                    for target in targets:
+                                        if isinstance(target, ast.Name):
+                                            link((helper, "<return>"), (fn, target.id))
+                                elif isinstance(parent, ast.Return):
+                                    link((helper, "<return>"), (fn, "<return>"))
+                                if reaches(helper, fn, set()):
+                                    put(helper, "<return>", "candidate")
+                    if isinstance(node, ast.Return):
+                        for source in context_names(node.value):
+                            link((fn, "<return>"), (fn, source))
+                        if fn.returns is not None:
+                            annotations[(fn, "<return>")] = [fn.returns]
+                for left, rights in list(edges.items()):
+                    if left in states:
+                        for right in rights:
+                            put(*right, states[left])
+            changed = before != (len(states), len(active), sum(map(len, edges.values())))
+
+        for fn in active:
+            for node in bodies[fn]:
+                if isinstance(node, (ast.Assign, ast.AnnAssign)) and node.value is not None:
+                    targets = node.targets if isinstance(node, ast.Assign) else [node.target]
+                    for target in targets:
+                        if isinstance(target, ast.Name) and (fn, target.id) in states:
+                            if not (context_names(node.value) or isinstance(node.value, ast.Dict) or each_context(node.value)
+                                    or (helper_of(node.value), "<return>") in states):
+                                put(fn, target.id, "candidate")
+
+        for (fn, name) in list(states):
+            if name == "<return>":
+                continue
+            for node in bodies[fn]:
+                if not isinstance(node, ast.Name) or node.id != name or not isinstance(node.ctx, ast.Load):
+                    continue
+                parent = parents.get(node)
+                status = "allow"
+                if isinstance(parent, ast.Subscript) and parent.value is node:
+                    status = "allow" if isinstance(parent.ctx, ast.Store) and isinstance(parent.slice, ast.Constant) and isinstance(parent.slice.value, str) else "ordinary"
+                elif isinstance(parent, (ast.BinOp, ast.UnaryOp, ast.AugAssign)):
+                    status = "ordinary"
+                elif isinstance(parent, ast.Compare):
+                    status = "allow" if len(parent.ops) == 1 and isinstance(parent.ops[0], (ast.Is, ast.IsNot)) and any(isinstance(n, ast.Constant) and n.value is None for n in [parent.left, *parent.comparators]) else "ordinary"
+                else:
+                    current: ast.AST = node
+                    while parents.get(current) is not None and not isinstance(parents[current], ast.stmt):
+                        current = parents[current]
+                        if isinstance(current, ast.Call):
+                            call = current
+                            if sink(call, fn):
+                                break
+                            if isinstance(call.func, ast.Name) and call.func.id in {"len", "sum", "min", "max", "sorted", "any", "all"}:
+                                status = "ordinary"
+                                break
+                            if isinstance(call.func, ast.Name) and call.func.id == "dict":
+                                if "dict" in shadowed[fn] or "dict" in module_shadowed:
+                                    status = "candidate"
+                                    break
+                                continue
+                            if isinstance(call.func, ast.Attribute):
+                                recv, method = call.func.value, call.func.attr
+                                if context_names(recv) & {name} and method in {"get", "pop", "popitem", "items", "values", "keys", "setdefault"}:
+                                    status = "ordinary"
+                                    break
+                                if method in {"copy", "update"} and context_names(recv) & {n for f, n in states if f is fn}:
+                                    continue
+                                if isinstance(recv, ast.Name) and recv.id == "self" and method in methods and methods[method] in active and method.startswith("_"):
+                                    # Recursion cannot prove a framework endpoint.
+                                    status = "candidate" if reaches(methods[method], fn, set()) else "allow"
+                                    break
+                            status = "candidate"
+                            break
+                    else:
+                        statement = parents.get(current)
+                        if isinstance(statement, (ast.Assign, ast.AnnAssign)):
+                            targets = statement.targets if isinstance(statement, ast.Assign) else [statement.target]
+                            if any(not isinstance(t, ast.Name) for t in targets):
+                                status = "ordinary"
+                        elif not isinstance(statement, (ast.Return, ast.Expr, ast.If)):
+                            status = "candidate"
+                put(fn, name, status)
+        # Consumption or escape propagates through connected aliases and helper parameters.
+        changed = True
+        while changed:
+            changed = False
+            for left, rights in edges.items():
+                if left not in states:
+                    continue
+                for right in rights:
+                    if right in states and rank[states[right]] < rank[states[left]]:
+                        states[right] = states[left]
+                        changed = True
+        for key, status in states.items():
+            reason = {"allow": "admin UI context 조립·framework 전달", "candidate": "admin context 흐름/호출 출처 불명", "ordinary": "context 값의 실제 소비"}[status]
+            for ann in annotations.get(key, []):
+                policy[id(ann)] = (status, reason)
+    return policy
+
+
 def _check_explicit_any(mod: ast.Module, rel: Path, out: Findings, cands: Candidates,
                         bindings: "dict[str, str] | None" = None,
                         aliases: "dict[str, list[tuple[ast.AST, bool]]] | None" = None) -> None:
     """#645 — 시그니처 bare `Any` 는 위반 · 시그니처 nested 와 변수/속성/클래스 필드의 `Any` 는 ⓓ 후보.
     #647 — 같은 애너테이션에서 먼저 판정한다: `dict/Mapping` 값 자리 `Any` 는 전 자리 차단 · `object` 는
     반환/클래스 속성 차단 · 매개변수/변수 ⓓ(면제 = `TypeIs/TypeGuard` 루트 · 스텁 강제 오버라이드).
     #647 위반이 난 애너테이션은 #645 nested ⓓ 를 생략한다(bare 는 유지 — 슬롯이 다르다). #647 은
     `application/`·`framework/` 루트만. #493 과 독립이다(«존재»는 #493 · «내용»은 #645/#647)."""
     names, mods = _any_bindings(mod)
     bindings = bindings if bindings is not None else _module_bindings(mod)
     in_roots = _in_rule_roots(rel)
+    admin_policy = _admin_context_policy(mod, rel)
     parent: dict[ast.AST, ast.AST] = {}
     for node in ast.walk(mod):
         for child in ast.iter_child_nodes(node):
             parent[child] = node
     hits: list[tuple[int, str, str, str, str, str]] = []  # (lineno, kind, rule, where, msg, question)
 
     def judge(ann: "ast.AST | None", site: str, where: str, label: str, lineno: int,
               exempt_object: bool, bare_msg: str, nested_msg: str) -> None:
         """한 애너테이션에 #647 → #645 순으로 판정한다(#645 문면·심각도는 종전 그대로 — 시그니처 bare 만 위반)."""
         v645 = _explicit_any(ann, names, mods)
+        status, reason = admin_policy.get(id(ann), ("ordinary", ""))
+        value, _ = _record_value(ann, names, mods, bindings)
+        fixed_slot = reason == "확인된 admin framework override 슬롯"
+        if status == "allow" and ((value is not None and v645 != "bare") or (fixed_slot and (v645 == "nested" or site == "sig-star"))):
+            return
+        if status == "candidate" and ann is not None:
+            value, _ = _record_value(ann, names, mods, bindings)
+            if in_roots and value is not None and v645 != "bare":
+                hits.append((lineno, "c", "#647", where, f"{label}의 열린 admin context — {reason}", RECORD_Q))
+                return
+            if v645 == "nested":
+                hits.append((lineno, "c", "#645", where, nested_msg, ANY_Q))
+                return
         blocked647 = False
         if in_roots and ann is not None:
             value, _top = _record_value(ann, names, mods, bindings)
             root = _unstring(ann)
             guard_root = isinstance(root, ast.Subscript) and _resolved_name(root.value, bindings) in TYPE_GUARDS
             if value == "Any":
                 hits.append((lineno, "v", "#647", where, f"{label}의 " + RECORD_MSG.format(v="Any"), ""))
                 blocked647 = True
             elif value == "object" and not (site == "sig-return" and (guard_root or exempt_object)):
                 if site in ("sig-return", "class-attr"):

```

## dddjango/scripts/design_pregate.py

Before SHA256: 05ed0358661e03cab1cec658c4e2bb5bdbe63fda2572aa8bc32646ace0a454ea
After SHA256: 50b530a0fa498fdb3d19650e790d758ae2cae2740a6bd914a132362e1902dabd

```diff
--- before/dddjango/scripts/design_pregate.py
+++ after/dddjango/scripts/design_pregate.py
@@ -108,20 +108,21 @@
 스텁으로 실체화해 already-built 에 «기실현 — 스텁 대체 예보»로 기록한다(커밋된 add 와 같은 예보 —
 같은 ID·같은 exit). 기준선 트리에 실존하는 add 는 여전히 형식 red. 미지정(HEAD 기본)은 종전과 판정
 (exit·귀속·ID) 동일 — 집계 행 문면은 판과 함께 변한다.
 """
 from __future__ import annotations
 
 import argparse
 import ast
 import errno
 import hashlib
+import importlib.util
 import io
 import json
 import os
 import re
 import shutil
 import subprocess
 import sys
 import tarfile
 import tempfile
 from dataclasses import dataclass, field, replace
@@ -1955,48 +1956,106 @@
         if not isinstance(value, list) or any(not isinstance(x, item_type) for x in value):
             raise RunError(f"registry_gate introduced.json {key} 형식 불비(fail-closed)")
     if proc.returncode == 2 and not payload["attributed_lines"]:
         raise RunError("registry_gate raw exit 2를 설명할 귀속 항목 부재(fail-closed)")
     return GateResult(raw_exit=proc.returncode, raw_stdout=proc.stdout,
         attributed_lines=payload["attributed_lines"], records=payload["records"],
         unmatched_lines=payload["unmatched_lines"], candidate_lines=payload.get("candidate_lines", []),
         candidate_records=payload.get("candidate_records", []))
 
 
+def _generated_admin_slots(root: Path, generated_methods: dict[str, list[GeneratedMethod]]) -> set[tuple[str, int, str]]:
+    """Join generated final AST slots, using the checker's closed admin origin policy.
+
+    Loading our bundled checker does not import or execute inspected project code.
+    Open helper annotations are only body-unverified evidence; names imply no role.
+    """
+    spec = importlib.util.spec_from_file_location("_pregate_public_surface", SCRIPTS_DIR / "check-public-surface-annotation.py")
+    if spec is None or spec.loader is None:
+        return set()
+    checker = importlib.util.module_from_spec(spec)
+    spec.loader.exec_module(checker)
+    slots: set[tuple[str, int, str]] = set()
+    for path, generated in generated_methods.items():
+        try:
+            mod = ast.parse((root / path).read_text(encoding="utf-8"))
+        except (OSError, UnicodeDecodeError, SyntaxError):
+            continue
+        names, modules = checker._any_bindings(mod)
+        bindings = checker._module_bindings(mod)
+        for cls, status in checker._admin_classes(mod).items():
+            if status != "allow":
+                continue
+            for fn in cls.body:
+                if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)) or not fn.name.startswith("_") or fn.name.startswith("__"):
+                    continue
+                matches = [item for item in generated if item["owner"] == cls.name and item["method"] == fn.name
+                           and item["lineno"] == fn.lineno and item["end_lineno"] == fn.end_lineno]
+                if len(matches) != 1:
+                    continue
+                annotations: list[tuple[int, str, ast.AST | None]] = [
+                    (fn.lineno, f"`{fn.name}()` 반환 타입", fn.returns)]
+                for arg in [*fn.args.posonlyargs, *fn.args.args, *fn.args.kwonlyargs]:
+                    annotations.append((fn.lineno, f"`{fn.name}()` 매개변수 `{arg.arg}`", arg.annotation))
+                for arg in (fn.args.vararg, fn.args.kwarg):
+                    if arg is not None:
+                        annotations.append((fn.lineno, f"`{fn.name}()` 매개변수 `*{arg.arg}`", arg.annotation))
+                for node in ast.walk(fn):
+                    if isinstance(node, ast.AnnAssign):
+                        annotations.append((node.lineno, f"`{ast.unparse(node.target)}` 주석", node.annotation))
+                for line, label, ann in annotations:
+                    value, _ = checker._record_value(ann, names, modules, bindings)
+                    if value is not None and checker._explicit_any(ann, names, modules) != "bare":
+                        if sum((other_line, other_label) == (line, label) for other_line, other_label, _ in annotations) == 1:
+                            slots.add((path, line, label))
+    return slots
+
+
 def partition_generated_findings(gate_result: GateResult,
-                                 generated_methods: dict[str, list[GeneratedMethod]]) -> tuple[list[str], list[str]]:
-    """전체 정규화 key의 모든 원본 위치가 생성 after_commit인 #376만 S1로 분리한다."""
+                                 generated_methods: dict[str, list[GeneratedMethod]],
+                                 root: Path | None = None) -> tuple[list[str], list[str]]:
+    """Defer only complete full-key cohorts with exact generated body/slot evidence."""
     cohorts: dict[str, list[dict]] = {}
-    for record in gate_result["records"]:
+    all_lines = [*gate_result["attributed_lines"], *gate_result["candidate_lines"]]
+    for record in [*gate_result["records"], *gate_result["candidate_records"]]:
         key = f"{record.get('checker')} :: {registry._normalize(findings.line_of_record(record), ())}"
         cohorts.setdefault(key, []).append(record)
-    # A raw record that cannot be joined signals incomplete attribution evidence.
-    # Do not guess its cohort from rule/path or silently drop it to make a green result.
-    if any(key not in gate_result["attributed_lines"] for key in cohorts):
+    # Unjoinable raw evidence may hide a mixed generated/non-generated cohort.
+    if any(key not in all_lines for key in cohorts):
         return list(gate_result["attributed_lines"]), []
-    def generated(record: dict) -> bool:
-        if record.get("rule") != "#376":
-            return False
+    slots = _generated_admin_slots(root, generated_methods) if root is not None else set()
+
+    def generated(record: dict) -> str | None:
         location = re.fullmatch(r"(.+):(\d+)", str(record.get("file", "")))
         if location is None:
-            return False
+            return None
         path, number = location.group(1), int(location.group(2))
-        return any(item["method"] == "after_commit" and item["owner"]
-                   and item["lineno"] <= number <= item["end_lineno"]
-                   for item in generated_methods.get(path, []))
+        if record.get("rule") == "#376" and record.get("checker") == "check-port-adapter-pairing.py":
+            if any(item["method"] == "after_commit" and item["owner"]
+                   and item["lineno"] <= number <= item["end_lineno"] for item in generated_methods.get(path, [])):
+                return "생성한 after_commit 본문 — on_commit 구현 미검증"
+        if record.get("rule") not in {"#645", "#647"} or record.get("checker") != "check-public-surface-annotation.py":
+            return None
+        message = str(record.get("message", ""))
+        label = re.match(r"^(`[^`]+\(\)` (?:매개변수 `[^`]+`|반환 타입)|`[^`]+` 주석)(?=의 | 의 |이 | 안에 | 가 |에 )", message)
+        if label is not None and (path, number, label.group(1)) in slots:
+            return "생성한 admin helper 열린 annotation — 실제 context 소비 흐름 미검증"
+        return None
+
     retained: list[str] = []
     deferred: list[str] = []
-    for line in gate_result["attributed_lines"]:
+    for line in dict.fromkeys(all_lines):
         records = cohorts.get(line, [])
-        if line not in gate_result["unmatched_lines"] and records and all(generated(r) for r in records):
-            deferred.append(f"S1: 생성한 after_commit 본문 — on_commit 구현 미검증 · {line}")
-        else:
+        reasons = [generated(record) for record in records]
+        if line not in gate_result["unmatched_lines"] and reasons and all(reasons):
+            deferred.append(f"S1: {reasons[0]} · {line}")
+        elif line in gate_result["attributed_lines"]:
             retained.append(line)
     return retained, deferred
 
 
 def _stable_id(line: str) -> str:
     """예보 항목 안정 ID — sha256(규칙#+경로)[:12] (D4 처분 라벨 추적 키)."""
     m: "re.Match[str] | None" = _ATTR_LINE_RE.search(line)
     rule: str = m.group(1) if m else "?"
     where: str = m.group(2).split(":", 1)[0] if m else line
     return hashlib.sha256(f"#{rule}+{where}".encode("utf-8")).hexdigest()[:12]
@@ -2880,21 +2939,21 @@
                               existence=existence, declarations=declarations, execution_mode=execution_mode)
             return 2 if declaration_count else (5 if defects else 4)
 
         print(f"# design_pregate — 예보 실행 · 기준선 {base_sha[:12]} (--base {base_ref}) · "
               f"모드 차단({MODE}) · {_executor_stamp(blk_hash)}")
         print(f"({NO_SUBSTITUTE})")
         print(f"실체화 {len(mat['materialized'])}건 · dirty overlay {len(overlaid)}건 · "
               f"미시뮬레이션 {len(mat['unsimulated'])}건 · already-built {len(mat['already_built'])}건")
 
         gate_result = run_gate(copy, scratch, ns.python_bin)
-        attributed, deferred = partition_generated_findings(gate_result, mat["generated_methods"])
+        attributed, deferred = partition_generated_findings(gate_result, mat["generated_methods"], copy)
         print("\n== 원 registry 결과 ==\n" + gate_result["raw_stdout"].rstrip())
         raw_summary = (f"원 registry 결과: exit {gate_result['raw_exit']} · 귀속 {len(gate_result['attributed_lines'])}건 · "
                        f"유지 {len(attributed)}건 · S1 미검증 {len(deferred)}건")
         print(raw_summary)
         print(f"\n== 생성 본문 S1 미검증 ({len(deferred)}건) ==")
         for line in deferred:
             print(f"  {line}")
 
         verdict: str = ("예보 green — P/S/I급 결정 계약 위반 예보 0(«설계 검증됨» 아님)"
                         if not attributed and not declaration_count else

```

## codex-dddjango/skills/dddjango/scripts/check-public-surface-annotation.py

Before SHA256: 788c9b1513ebab27e0ca2ae1d30cef0d4354f2bea873129fccaebc66c0c8074b
After SHA256: 60696373a2717f59128b8281896545be085bf8585616a859d9d38cb641ce8635

```diff
--- before/codex-dddjango/skills/dddjango/scripts/check-public-surface-annotation.py
+++ after/codex-dddjango/skills/dddjango/scripts/check-public-surface-annotation.py
@@ -705,41 +705,412 @@
     if cls is None or fn.name not in FRAMEWORK_OVERRIDE_EXEMPT:
         return False
     want = FRAMEWORK_OVERRIDE_EXEMPT[fn.name]
     for b in cls.bases:
         for base in _resolved_bases(b, bindings, aliases):  # 별칭 정의 전부(mixin-first 중간 ClassDef 포함) — `_is_declarative_class` 와 같은 해소
             if base in want or (fn.name == "deconstruct" and base.endswith("Field")):
                 return True
     return False
 
 
+# Closed origins verified from Django admin and Parler's admin inheritance.
+_ADMIN_BASES = {f"django.contrib.admin{module}.{name}"
+                for module in ("", ".options")
+                for name in ("ModelAdmin", "InlineModelAdmin", "TabularInline", "StackedInline")}
+_ADMIN_BASES |= {f"parler.admin.{name}" for name in (
+    "TranslatableAdmin", "TranslatableInlineModelAdmin", "TranslatableStackedInline", "TranslatableTabularInline")}
+_ADMIN_CONTEXT = {"changeform_view": "extra_context", "change_view": "extra_context",
+                  "add_view": "extra_context", "changelist_view": "extra_context", "render_change_form": "context"}
+_ADMIN_KWARGS = {"get_form", "get_formset", "get_fieldsets", "get_readonly_fields"}
+
+
+def _admin_classes(mod: ast.Module) -> dict[ast.ClassDef, str]:
+    """Resolve only static module origins/aliases and local bases; never execute an MRO."""
+    origins = _origin_bindings(mod)
+    aliases = _alias_defs(mod)
+    definitions: dict[str, ast.AST] = {}
+
+    def collect(stmts: list[ast.stmt]) -> None:
+        for st in stmts:
+            if isinstance(st, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
+                definitions[st.name] = st
+            elif isinstance(st, (ast.Assign, ast.AnnAssign)):
+                for target in st.targets if isinstance(st, ast.Assign) else [st.target]:
+                    for name in ast.walk(target):
+                        if isinstance(name, ast.Name):
+                            definitions[name.id] = st.value or st
+            elif isinstance(st, (ast.If, ast.Try)):
+                collect(st.body)
+                collect(st.orelse)
+                if isinstance(st, ast.Try):
+                    for handler in st.handlers:
+                        collect(handler.body)
+                    collect(st.finalbody)
+    collect(mod.body)
+    # Only current runtime alias plus TYPE_CHECKING alternatives are relevant.
+    aliases = {name: [(value, tc) for value, tc in values if tc or value is definitions.get(name)]
+               for name, values in aliases.items()}
+
+    def resolve(node: ast.AST, seen: frozenset[str]) -> str:
+        if isinstance(node, ast.Subscript):
+            return resolve(node.value, seen)
+        origin = _dotted(node, origins)
+        if origin in _ADMIN_BASES:
+            return "allow"
+        if isinstance(node, ast.Name) and node.id not in origins:
+            if node.id in seen:
+                return "candidate"
+            seen = seen | {node.id}
+            definition = definitions.get(node.id)
+            if isinstance(definition, ast.ClassDef):
+                statuses = [resolve(base, seen) for base in definition.bases]
+                return "allow" if "allow" in statuses else ("candidate" if "candidate" in statuses else "ordinary")
+            if isinstance(definition, (ast.Name, ast.Attribute, ast.Subscript)):
+                statuses = [resolve(value, seen) for value, _ in aliases.get(node.id, [(definition, False)])]
+                return "allow" if statuses and all(s == "allow" for s in statuses) else (
+                    "candidate" if any(s != "ordinary" for s in statuses) else "ordinary")
+            if definition is not None or node.id == "object":
+                return "ordinary"
+        return "candidate"
+
+    result: dict[ast.ClassDef, str] = {}
+    for cls in (n for n in mod.body if isinstance(n, ast.ClassDef)):
+        statuses = [resolve(base, frozenset({cls.name})) for base in cls.bases]
+        result[cls] = "allow" if "allow" in statuses else ("candidate" if "candidate" in statuses else "ordinary")
+    return result
+
+
+def _admin_context_policy(mod: ast.Module, rel: Path) -> dict[int, tuple[str, str]]:
+    """Annotation identity policy for connected admin UI bindings, not entire functions.
+
+    A context component includes copies/merges and directly passed private-helper
+    bindings. Consumption dominates unknown escapes, which dominate UI transport.
+    This is deliberately bounded AST analysis; it does not infer arbitrary callees.
+    """
+    policy: dict[int, tuple[str, str]] = {}
+    origins = _origin_bindings(mod)
+    module_shadowed: set[str] = set(origins)
+    pending: list[ast.AST] = list(mod.body)
+    while pending:
+        node = pending.pop()
+        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
+            module_shadowed.add(node.name)
+            continue
+        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
+            module_shadowed.add(node.id)
+        pending.extend(ast.iter_child_nodes(node))
+    rank = {"allow": 0, "candidate": 1, "ordinary": 2}
+    for cls, origin_status in _admin_classes(mod).items():
+        if origin_status == "ordinary":
+            continue
+        methods = {st.name: st for st in cls.body if isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef))}
+        # Duplicate/rebound methods cannot prove direct helper dispatch.
+        counts = {name: sum(isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef)) and st.name == name
+                            for st in cls.body) for name in methods}
+        for st in cls.body:
+            if isinstance(st, (ast.Assign, ast.AnnAssign)):
+                for target in st.targets if isinstance(st, ast.Assign) else [st.target]:
+                    if isinstance(target, ast.Name) and target.id in counts:
+                        counts[target.id] += 1
+        states: dict[tuple[ast.AST, str], str] = {}
+        edges: dict[tuple[ast.AST, str], set[tuple[ast.AST, str]]] = {}
+        annotations: dict[tuple[ast.AST, str], list[ast.AST]] = {}
+        active: set[ast.AST] = set()
+        parents: dict[ast.AST, ast.AST] = {}
+        bodies: dict[ast.AST, list[ast.AST]] = {}
+        shadowed: dict[ast.AST, set[str]] = {}
+
+        def put(fn: ast.AST, name: str, status: str = "allow") -> tuple[ast.AST, str]:
+            key = (fn, name)
+            states[key] = max(states.get(key, origin_status), status, key=rank.get)
+            return key
+
+        def link(left: tuple[ast.AST, str], right: tuple[ast.AST, str]) -> None:
+            edges.setdefault(left, set()).add(right)
+            edges.setdefault(right, set()).add(left)
+
+        def fixed(ann: ast.AST | None, *, kwargs: bool = False) -> None:
+            if ann is not None and (kwargs or any(isinstance(n, ast.Subscript) and _dotted(n.value, origins) in _ADMIN_BASES
+                                                 for n in ast.walk(_unstring(ann)))):
+                policy[id(ann)] = (origin_status, "확인된 admin framework override 슬롯" if origin_status == "allow" else "admin base 출처 불명")
+
+        for fn in methods.values():
+            if fn.name in _ADMIN_CONTEXT:
+                active.add(fn)
+            nodes: list[ast.AST] = []
+            def walk(node: ast.AST) -> None:
+                nodes.append(node)
+                for child in ast.iter_child_nodes(node):
+                    parents[child] = node
+                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)):
+                        continue
+                    walk(child)
+            for st in fn.body:
+                walk(st)
+            bodies[fn] = nodes
+            local_bindings: set[str] = set()
+            for st in fn.body:
+                _record_syntax_bindings(st, local_bindings)
+                if isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
+                    local_bindings.add(st.name)
+            local_bindings.update(a.arg for a in [*fn.args.posonlyargs, *fn.args.args, *fn.args.kwonlyargs])
+            local_bindings.update(a.arg for a in (fn.args.vararg, fn.args.kwarg) if a is not None)
+            shadowed[fn] = local_bindings
+            for arg in [*fn.args.posonlyargs, *fn.args.args, *fn.args.kwonlyargs]:
+                if arg.annotation is not None:
+                    annotations.setdefault((fn, arg.arg), []).append(arg.annotation)
+                if arg.arg == _ADMIN_CONTEXT.get(fn.name):
+                    put(fn, arg.arg)
+                    active.add(fn)
+            if fn.name in _ADMIN_KWARGS and fn.args.kwarg:
+                fixed(fn.args.kwarg.annotation, kwargs=True)
+            if fn.name == "get_inline_instances":
+                fixed(fn.returns)
+            for node in nodes:
+                if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
+                    annotations.setdefault((fn, node.target.id), []).append(node.annotation)
+        for st in cls.body:
+            if isinstance(st, ast.AnnAssign) and isinstance(st.target, ast.Name) and st.target.id == "inlines":
+                fixed(st.annotation)
+
+        def context_names(expr: ast.AST | None) -> set[str]:
+            if isinstance(expr, ast.Name):
+                return {expr.id}
+            if isinstance(expr, ast.BoolOp) and isinstance(expr.op, ast.Or) and len(expr.values) == 2 \
+                    and isinstance(expr.values[1], ast.Dict) and not expr.values[1].keys:
+                return context_names(expr.values[0])
+            if isinstance(expr, ast.Dict):
+                return set().union(*(context_names(v) for k, v in zip(expr.keys, expr.values) if k is None))
+            if isinstance(expr, ast.Call):
+                if isinstance(expr.func, ast.Name) and expr.func.id == "dict":
+                    return set().union(*(context_names(a) for a in expr.args))
+                if isinstance(expr.func, ast.Attribute) and expr.func.attr == "copy" and not expr.args and not expr.keywords:
+                    return context_names(expr.func.value)
+            return set()
+
+        def sink(call: ast.Call, fn: ast.AST) -> bool:
+            root = call.func
+            while isinstance(root, ast.Attribute):
+                root = root.value
+            if isinstance(root, ast.Name) and root.id in shadowed[fn] and root.id != "self":
+                return False
+            name = _dotted(call.func, origins)
+            if name in {"django.template.response.TemplateResponse", "django.shortcuts.render"}:
+                return True
+            if isinstance(call.func, ast.Attribute):
+                receiver = call.func.value
+                if isinstance(receiver, ast.Call) and isinstance(receiver.func, ast.Name) and receiver.func.id == "super":
+                    return "super" not in shadowed[fn] and (call.func.attr == fn.name or call.func.attr == "render_change_form")
+                return isinstance(receiver, ast.Name) and receiver.id == "self" and call.func.attr == "render_change_form"
+            return False
+
+        def each_context(expr: ast.AST | None) -> bool:
+            return isinstance(expr, ast.Call) and _dotted(expr.func, {}) == "self.admin_site.each_context"
+
+        def helper_of(expr: ast.AST | None) -> ast.FunctionDef | ast.AsyncFunctionDef | None:
+            if isinstance(expr, ast.Call) and isinstance(expr.func, ast.Attribute) and isinstance(expr.func.value, ast.Name) \
+                    and expr.func.value.id == "self" and expr.func.attr.startswith("_") and counts.get(expr.func.attr) == 1:
+                return methods[expr.func.attr]
+            return None
+
+        def reaches(start: ast.AST, target: ast.AST, visited: set[ast.AST]) -> bool:
+            if start is target:
+                return True
+            if start in visited:
+                return False
+            visited.add(start)
+            return any(callee is not None and reaches(callee, target, visited)
+                       for node in bodies[start] if isinstance(node, ast.Call) for callee in [helper_of(node)])
+
+        # Monotone reachability terminates on finite function/binding identities.
+        changed = True
+        while changed:
+            before = (len(states), len(active), sum(map(len, edges.values())))
+            for fn in list(active):
+                for node in bodies[fn]:
+                    if isinstance(node, (ast.Assign, ast.AnnAssign)):
+                        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
+                        sources = context_names(node.value)
+                        for target in targets:
+                            if isinstance(target, ast.Name) and each_context(node.value):
+                                put(fn, target.id)
+                        for target in targets:
+                            if isinstance(target, ast.Name):
+                                for source in sources:
+                                    link((fn, target.id), (fn, source))
+                    if isinstance(node, ast.Call) and sink(node, fn):
+                        # The context position is owned by the resolved framework sink.
+                        if _dotted(node.func, origins) in {"django.template.response.TemplateResponse", "django.shortcuts.render"}:
+                            arguments = node.args[2:3] + [kw.value for kw in node.keywords if kw.arg == "context"]
+                        elif isinstance(node.func, ast.Attribute) and node.func.attr == "render_change_form":
+                            arguments = node.args[1:2] + [kw.value for kw in node.keywords if kw.arg == "context"]
+                        else:
+                            arguments = [kw.value for kw in node.keywords if kw.arg == _ADMIN_CONTEXT.get(fn.name)]
+                        for value in arguments:
+                            for name in context_names(value):
+                                put(fn, name)
+                    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
+                        receiver = node.func.value
+                        if node.func.attr == "update":
+                            for source in set().union(*(context_names(a) for a in node.args)):
+                                for dest in context_names(receiver):
+                                    link((fn, dest), (fn, source))
+                        if isinstance(receiver, ast.Name) and receiver.id == "self" and node.func.attr.startswith("_"):
+                            helper = methods.get(node.func.attr)
+                            if helper is None or counts[node.func.attr] != 1:
+                                continue
+                            args = [*helper.args.posonlyargs, *helper.args.args][1:]
+                            passed = [(arg.arg, value) for arg, value in zip(args, node.args)]
+                            passed += [(kw.arg, kw.value) for kw in node.keywords if kw.arg]
+                            for label, value in passed:
+                                for source in context_names(value):
+                                    if (fn, source) in states:
+                                        active.add(helper)
+                                        put(helper, label)
+                                        link((fn, source), (helper, label))
+                            if helper in active:
+                                parent = parents.get(node)
+                                if isinstance(parent, (ast.Assign, ast.AnnAssign)) and parent.value is node:
+                                    targets = parent.targets if isinstance(parent, ast.Assign) else [parent.target]
+                                    for target in targets:
+                                        if isinstance(target, ast.Name):
+                                            link((helper, "<return>"), (fn, target.id))
+                                elif isinstance(parent, ast.Return):
+                                    link((helper, "<return>"), (fn, "<return>"))
+                                if reaches(helper, fn, set()):
+                                    put(helper, "<return>", "candidate")
+                    if isinstance(node, ast.Return):
+                        for source in context_names(node.value):
+                            link((fn, "<return>"), (fn, source))
+                        if fn.returns is not None:
+                            annotations[(fn, "<return>")] = [fn.returns]
+                for left, rights in list(edges.items()):
+                    if left in states:
+                        for right in rights:
+                            put(*right, states[left])
+            changed = before != (len(states), len(active), sum(map(len, edges.values())))
+
+        for fn in active:
+            for node in bodies[fn]:
+                if isinstance(node, (ast.Assign, ast.AnnAssign)) and node.value is not None:
+                    targets = node.targets if isinstance(node, ast.Assign) else [node.target]
+                    for target in targets:
+                        if isinstance(target, ast.Name) and (fn, target.id) in states:
+                            if not (context_names(node.value) or isinstance(node.value, ast.Dict) or each_context(node.value)
+                                    or (helper_of(node.value), "<return>") in states):
+                                put(fn, target.id, "candidate")
+
+        for (fn, name) in list(states):
+            if name == "<return>":
+                continue
+            for node in bodies[fn]:
+                if not isinstance(node, ast.Name) or node.id != name or not isinstance(node.ctx, ast.Load):
+                    continue
+                parent = parents.get(node)
+                status = "allow"
+                if isinstance(parent, ast.Subscript) and parent.value is node:
+                    status = "allow" if isinstance(parent.ctx, ast.Store) and isinstance(parent.slice, ast.Constant) and isinstance(parent.slice.value, str) else "ordinary"
+                elif isinstance(parent, (ast.BinOp, ast.UnaryOp, ast.AugAssign)):
+                    status = "ordinary"
+                elif isinstance(parent, ast.Compare):
+                    status = "allow" if len(parent.ops) == 1 and isinstance(parent.ops[0], (ast.Is, ast.IsNot)) and any(isinstance(n, ast.Constant) and n.value is None for n in [parent.left, *parent.comparators]) else "ordinary"
+                else:
+                    current: ast.AST = node
+                    while parents.get(current) is not None and not isinstance(parents[current], ast.stmt):
+                        current = parents[current]
+                        if isinstance(current, ast.Call):
+                            call = current
+                            if sink(call, fn):
+                                break
+                            if isinstance(call.func, ast.Name) and call.func.id in {"len", "sum", "min", "max", "sorted", "any", "all"}:
+                                status = "ordinary"
+                                break
+                            if isinstance(call.func, ast.Name) and call.func.id == "dict":
+                                if "dict" in shadowed[fn] or "dict" in module_shadowed:
+                                    status = "candidate"
+                                    break
+                                continue
+                            if isinstance(call.func, ast.Attribute):
+                                recv, method = call.func.value, call.func.attr
+                                if context_names(recv) & {name} and method in {"get", "pop", "popitem", "items", "values", "keys", "setdefault"}:
+                                    status = "ordinary"
+                                    break
+                                if method in {"copy", "update"} and context_names(recv) & {n for f, n in states if f is fn}:
+                                    continue
+                                if isinstance(recv, ast.Name) and recv.id == "self" and method in methods and methods[method] in active and method.startswith("_"):
+                                    # Recursion cannot prove a framework endpoint.
+                                    status = "candidate" if reaches(methods[method], fn, set()) else "allow"
+                                    break
+                            status = "candidate"
+                            break
+                    else:
+                        statement = parents.get(current)
+                        if isinstance(statement, (ast.Assign, ast.AnnAssign)):
+                            targets = statement.targets if isinstance(statement, ast.Assign) else [statement.target]
+                            if any(not isinstance(t, ast.Name) for t in targets):
+                                status = "ordinary"
+                        elif not isinstance(statement, (ast.Return, ast.Expr, ast.If)):
+                            status = "candidate"
+                put(fn, name, status)
+        # Consumption or escape propagates through connected aliases and helper parameters.
+        changed = True
+        while changed:
+            changed = False
+            for left, rights in edges.items():
+                if left not in states:
+                    continue
+                for right in rights:
+                    if right in states and rank[states[right]] < rank[states[left]]:
+                        states[right] = states[left]
+                        changed = True
+        for key, status in states.items():
+            reason = {"allow": "admin UI context 조립·framework 전달", "candidate": "admin context 흐름/호출 출처 불명", "ordinary": "context 값의 실제 소비"}[status]
+            for ann in annotations.get(key, []):
+                policy[id(ann)] = (status, reason)
+    return policy
+
+
 def _check_explicit_any(mod: ast.Module, rel: Path, out: Findings, cands: Candidates,
                         bindings: "dict[str, str] | None" = None,
                         aliases: "dict[str, list[tuple[ast.AST, bool]]] | None" = None) -> None:
     """#645 — 시그니처 bare `Any` 는 위반 · 시그니처 nested 와 변수/속성/클래스 필드의 `Any` 는 ⓓ 후보.
     #647 — 같은 애너테이션에서 먼저 판정한다: `dict/Mapping` 값 자리 `Any` 는 전 자리 차단 · `object` 는
     반환/클래스 속성 차단 · 매개변수/변수 ⓓ(면제 = `TypeIs/TypeGuard` 루트 · 스텁 강제 오버라이드).
     #647 위반이 난 애너테이션은 #645 nested ⓓ 를 생략한다(bare 는 유지 — 슬롯이 다르다). #647 은
     `application/`·`framework/` 루트만. #493 과 독립이다(«존재»는 #493 · «내용»은 #645/#647)."""
     names, mods = _any_bindings(mod)
     bindings = bindings if bindings is not None else _module_bindings(mod)
     in_roots = _in_rule_roots(rel)
+    admin_policy = _admin_context_policy(mod, rel)
     parent: dict[ast.AST, ast.AST] = {}
     for node in ast.walk(mod):
         for child in ast.iter_child_nodes(node):
             parent[child] = node
     hits: list[tuple[int, str, str, str, str, str]] = []  # (lineno, kind, rule, where, msg, question)
 
     def judge(ann: "ast.AST | None", site: str, where: str, label: str, lineno: int,
               exempt_object: bool, bare_msg: str, nested_msg: str) -> None:
         """한 애너테이션에 #647 → #645 순으로 판정한다(#645 문면·심각도는 종전 그대로 — 시그니처 bare 만 위반)."""
         v645 = _explicit_any(ann, names, mods)
+        status, reason = admin_policy.get(id(ann), ("ordinary", ""))
+        value, _ = _record_value(ann, names, mods, bindings)
+        fixed_slot = reason == "확인된 admin framework override 슬롯"
+        if status == "allow" and ((value is not None and v645 != "bare") or (fixed_slot and (v645 == "nested" or site == "sig-star"))):
+            return
+        if status == "candidate" and ann is not None:
+            value, _ = _record_value(ann, names, mods, bindings)
+            if in_roots and value is not None and v645 != "bare":
+                hits.append((lineno, "c", "#647", where, f"{label}의 열린 admin context — {reason}", RECORD_Q))
+                return
+            if v645 == "nested":
+                hits.append((lineno, "c", "#645", where, nested_msg, ANY_Q))
+                return
         blocked647 = False
         if in_roots and ann is not None:
             value, _top = _record_value(ann, names, mods, bindings)
             root = _unstring(ann)
             guard_root = isinstance(root, ast.Subscript) and _resolved_name(root.value, bindings) in TYPE_GUARDS
             if value == "Any":
                 hits.append((lineno, "v", "#647", where, f"{label}의 " + RECORD_MSG.format(v="Any"), ""))
                 blocked647 = True
             elif value == "object" and not (site == "sig-return" and (guard_root or exempt_object)):
                 if site in ("sig-return", "class-attr"):

```

## codex-dddjango/skills/dddjango/scripts/design_pregate.py

Before SHA256: 05ed0358661e03cab1cec658c4e2bb5bdbe63fda2572aa8bc32646ace0a454ea
After SHA256: 50b530a0fa498fdb3d19650e790d758ae2cae2740a6bd914a132362e1902dabd

```diff
--- before/codex-dddjango/skills/dddjango/scripts/design_pregate.py
+++ after/codex-dddjango/skills/dddjango/scripts/design_pregate.py
@@ -108,20 +108,21 @@
 스텁으로 실체화해 already-built 에 «기실현 — 스텁 대체 예보»로 기록한다(커밋된 add 와 같은 예보 —
 같은 ID·같은 exit). 기준선 트리에 실존하는 add 는 여전히 형식 red. 미지정(HEAD 기본)은 종전과 판정
 (exit·귀속·ID) 동일 — 집계 행 문면은 판과 함께 변한다.
 """
 from __future__ import annotations
 
 import argparse
 import ast
 import errno
 import hashlib
+import importlib.util
 import io
 import json
 import os
 import re
 import shutil
 import subprocess
 import sys
 import tarfile
 import tempfile
 from dataclasses import dataclass, field, replace
@@ -1955,48 +1956,106 @@
         if not isinstance(value, list) or any(not isinstance(x, item_type) for x in value):
             raise RunError(f"registry_gate introduced.json {key} 형식 불비(fail-closed)")
     if proc.returncode == 2 and not payload["attributed_lines"]:
         raise RunError("registry_gate raw exit 2를 설명할 귀속 항목 부재(fail-closed)")
     return GateResult(raw_exit=proc.returncode, raw_stdout=proc.stdout,
         attributed_lines=payload["attributed_lines"], records=payload["records"],
         unmatched_lines=payload["unmatched_lines"], candidate_lines=payload.get("candidate_lines", []),
         candidate_records=payload.get("candidate_records", []))
 
 
+def _generated_admin_slots(root: Path, generated_methods: dict[str, list[GeneratedMethod]]) -> set[tuple[str, int, str]]:
+    """Join generated final AST slots, using the checker's closed admin origin policy.
+
+    Loading our bundled checker does not import or execute inspected project code.
+    Open helper annotations are only body-unverified evidence; names imply no role.
+    """
+    spec = importlib.util.spec_from_file_location("_pregate_public_surface", SCRIPTS_DIR / "check-public-surface-annotation.py")
+    if spec is None or spec.loader is None:
+        return set()
+    checker = importlib.util.module_from_spec(spec)
+    spec.loader.exec_module(checker)
+    slots: set[tuple[str, int, str]] = set()
+    for path, generated in generated_methods.items():
+        try:
+            mod = ast.parse((root / path).read_text(encoding="utf-8"))
+        except (OSError, UnicodeDecodeError, SyntaxError):
+            continue
+        names, modules = checker._any_bindings(mod)
+        bindings = checker._module_bindings(mod)
+        for cls, status in checker._admin_classes(mod).items():
+            if status != "allow":
+                continue
+            for fn in cls.body:
+                if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)) or not fn.name.startswith("_") or fn.name.startswith("__"):
+                    continue
+                matches = [item for item in generated if item["owner"] == cls.name and item["method"] == fn.name
+                           and item["lineno"] == fn.lineno and item["end_lineno"] == fn.end_lineno]
+                if len(matches) != 1:
+                    continue
+                annotations: list[tuple[int, str, ast.AST | None]] = [
+                    (fn.lineno, f"`{fn.name}()` 반환 타입", fn.returns)]
+                for arg in [*fn.args.posonlyargs, *fn.args.args, *fn.args.kwonlyargs]:
+                    annotations.append((fn.lineno, f"`{fn.name}()` 매개변수 `{arg.arg}`", arg.annotation))
+                for arg in (fn.args.vararg, fn.args.kwarg):
+                    if arg is not None:
+                        annotations.append((fn.lineno, f"`{fn.name}()` 매개변수 `*{arg.arg}`", arg.annotation))
+                for node in ast.walk(fn):
+                    if isinstance(node, ast.AnnAssign):
+                        annotations.append((node.lineno, f"`{ast.unparse(node.target)}` 주석", node.annotation))
+                for line, label, ann in annotations:
+                    value, _ = checker._record_value(ann, names, modules, bindings)
+                    if value is not None and checker._explicit_any(ann, names, modules) != "bare":
+                        if sum((other_line, other_label) == (line, label) for other_line, other_label, _ in annotations) == 1:
+                            slots.add((path, line, label))
+    return slots
+
+
 def partition_generated_findings(gate_result: GateResult,
-                                 generated_methods: dict[str, list[GeneratedMethod]]) -> tuple[list[str], list[str]]:
-    """전체 정규화 key의 모든 원본 위치가 생성 after_commit인 #376만 S1로 분리한다."""
+                                 generated_methods: dict[str, list[GeneratedMethod]],
+                                 root: Path | None = None) -> tuple[list[str], list[str]]:
+    """Defer only complete full-key cohorts with exact generated body/slot evidence."""
     cohorts: dict[str, list[dict]] = {}
-    for record in gate_result["records"]:
+    all_lines = [*gate_result["attributed_lines"], *gate_result["candidate_lines"]]
+    for record in [*gate_result["records"], *gate_result["candidate_records"]]:
         key = f"{record.get('checker')} :: {registry._normalize(findings.line_of_record(record), ())}"
         cohorts.setdefault(key, []).append(record)
-    # A raw record that cannot be joined signals incomplete attribution evidence.
-    # Do not guess its cohort from rule/path or silently drop it to make a green result.
-    if any(key not in gate_result["attributed_lines"] for key in cohorts):
+    # Unjoinable raw evidence may hide a mixed generated/non-generated cohort.
+    if any(key not in all_lines for key in cohorts):
         return list(gate_result["attributed_lines"]), []
-    def generated(record: dict) -> bool:
-        if record.get("rule") != "#376":
-            return False
+    slots = _generated_admin_slots(root, generated_methods) if root is not None else set()
+
+    def generated(record: dict) -> str | None:
         location = re.fullmatch(r"(.+):(\d+)", str(record.get("file", "")))
         if location is None:
-            return False
+            return None
         path, number = location.group(1), int(location.group(2))
-        return any(item["method"] == "after_commit" and item["owner"]
-                   and item["lineno"] <= number <= item["end_lineno"]
-                   for item in generated_methods.get(path, []))
+        if record.get("rule") == "#376" and record.get("checker") == "check-port-adapter-pairing.py":
+            if any(item["method"] == "after_commit" and item["owner"]
+                   and item["lineno"] <= number <= item["end_lineno"] for item in generated_methods.get(path, [])):
+                return "생성한 after_commit 본문 — on_commit 구현 미검증"
+        if record.get("rule") not in {"#645", "#647"} or record.get("checker") != "check-public-surface-annotation.py":
+            return None
+        message = str(record.get("message", ""))
+        label = re.match(r"^(`[^`]+\(\)` (?:매개변수 `[^`]+`|반환 타입)|`[^`]+` 주석)(?=의 | 의 |이 | 안에 | 가 |에 )", message)
+        if label is not None and (path, number, label.group(1)) in slots:
+            return "생성한 admin helper 열린 annotation — 실제 context 소비 흐름 미검증"
+        return None
+
     retained: list[str] = []
     deferred: list[str] = []
-    for line in gate_result["attributed_lines"]:
+    for line in dict.fromkeys(all_lines):
         records = cohorts.get(line, [])
-        if line not in gate_result["unmatched_lines"] and records and all(generated(r) for r in records):
-            deferred.append(f"S1: 생성한 after_commit 본문 — on_commit 구현 미검증 · {line}")
-        else:
+        reasons = [generated(record) for record in records]
+        if line not in gate_result["unmatched_lines"] and reasons and all(reasons):
+            deferred.append(f"S1: {reasons[0]} · {line}")
+        elif line in gate_result["attributed_lines"]:
             retained.append(line)
     return retained, deferred
 
 
 def _stable_id(line: str) -> str:
     """예보 항목 안정 ID — sha256(규칙#+경로)[:12] (D4 처분 라벨 추적 키)."""
     m: "re.Match[str] | None" = _ATTR_LINE_RE.search(line)
     rule: str = m.group(1) if m else "?"
     where: str = m.group(2).split(":", 1)[0] if m else line
     return hashlib.sha256(f"#{rule}+{where}".encode("utf-8")).hexdigest()[:12]
@@ -2880,21 +2939,21 @@
                               existence=existence, declarations=declarations, execution_mode=execution_mode)
             return 2 if declaration_count else (5 if defects else 4)
 
         print(f"# design_pregate — 예보 실행 · 기준선 {base_sha[:12]} (--base {base_ref}) · "
               f"모드 차단({MODE}) · {_executor_stamp(blk_hash)}")
         print(f"({NO_SUBSTITUTE})")
         print(f"실체화 {len(mat['materialized'])}건 · dirty overlay {len(overlaid)}건 · "
               f"미시뮬레이션 {len(mat['unsimulated'])}건 · already-built {len(mat['already_built'])}건")
 
         gate_result = run_gate(copy, scratch, ns.python_bin)
-        attributed, deferred = partition_generated_findings(gate_result, mat["generated_methods"])
+        attributed, deferred = partition_generated_findings(gate_result, mat["generated_methods"], copy)
         print("\n== 원 registry 결과 ==\n" + gate_result["raw_stdout"].rstrip())
         raw_summary = (f"원 registry 결과: exit {gate_result['raw_exit']} · 귀속 {len(gate_result['attributed_lines'])}건 · "
                        f"유지 {len(attributed)}건 · S1 미검증 {len(deferred)}건")
         print(raw_summary)
         print(f"\n== 생성 본문 S1 미검증 ({len(deferred)}건) ==")
         for line in deferred:
             print(f"  {line}")
 
         verdict: str = ("예보 green — P/S/I급 결정 계약 위반 예보 0(«설계 검증됨» 아님)"
                         if not attributed and not declaration_count else

```

## workspace/tools/field_report_checker_smoke.py

Before SHA256: 9c60eeca4c726232ce8478cf84d940b6e4d4bbf16126de9afb42b5e55878bdcc
After SHA256: d2e2f3dcb151746cdab3ca15951d638991e96f231f84338d8a14333e28ec9936

```diff
--- before/workspace/tools/field_report_checker_smoke.py
+++ after/workspace/tools/field_report_checker_smoke.py
@@ -1,18 +1,19 @@
 #!/usr/bin/env python3
 """현장 F4/F7/F8 회귀: 골격·의미 후보·앵커 전체 수집의 반대 대조를 고정한다."""
 from __future__ import annotations
 
 import contextlib
 import csv
 import hashlib
 import io
+import json
 import os
 import shutil
 import subprocess
 import sys
 import tempfile
 import unittest
 from pathlib import Path
 from unittest.mock import patch
 
 from pregate_fixture_run import _git, _load_module
@@ -96,20 +97,155 @@
                 found, candidates = self.result_rules(f"class {name}:\n    {field}\n")
                 self.assertEqual(found, [])
                 self.assertEqual(candidates, ["#571"])
 
     def test_multiple_shapes_stay_blocked_and_field_words_stay_neutral(self) -> None:
         found, _ = self.result_rules("class Completed: pass\nclass Rejected: pass\n")
         self.assertEqual(found, ["#571"])
         for field in ("code: str", "error: float", "outcome: str"):
             with self.subTest(field=field):
                 self.assertEqual(self.result_rules(f"class RecordedResult:\n    {field}\n"), ([], []))
+
+    def admin_records(self, source):
+        self.write("framework/admin/book.py", source)
+        records = self.root / "findings.jsonl"
+        records.unlink(missing_ok=True)
+        run = subprocess.run([sys.executable, '-B', str(SCRIPTS / 'check-public-surface-annotation.py'),
+                              str(self.root)], env=self.env, text=True, capture_output=True)
+        self.assertIn(run.returncode, (0, 2), run.stdout + run.stderr)
+        return [json.loads(line) for line in records.read_text().splitlines()] if records.exists() else []
+
+    def test_admin_context_real_parler_helper_and_business_opposite(self):
+        source = """from typing import Any
+from parler.admin import TranslatableAdmin
+class BookAdmin(TranslatableAdmin):
+    def changeform_view(self, request: object, extra_context: dict[str, Any] | None = None) -> HttpResponse:
+        return self._render_failed_submission(request, extra_context)
+    def _render_failed_submission(self, request: object, extra_context: dict[str, Any] | None) -> HttpResponse:
+        form = self.get_form(request)(request.POST)
+        inline_instances = self.get_inline_instances(request)
+        media = self.media + form.media
+        context: dict[str, Any] = self.admin_site.each_context(request)
+        context.update({'form': form, 'inline_admin_formsets': inline_instances, 'media': media,
+                        'is_popup': request.GET.get('_popup'), 'source_model': request.POST.get('source_model'),
+                        'to_field': request.GET.get('_to_field')})
+        context.update(extra_context or {})
+        return self.render_change_form(request, context)
+"""
+        rows = self.admin_records(source)
+        self.assertEqual([r for r in rows if r['rule'] in ('#645', '#647')], [])
+        for consumption in ["charge(context['amount'])", "context['amount'] > 10", "self.total = context['amount']"]:
+            with self.subTest(consumption=consumption):
+                rows = self.admin_records(source.replace('        return self.render_change_form',
+                                                         '        ' + consumption + '\n        return self.render_change_form'))
+                self.assertTrue(any(r['rule'] == '#647' and r['severity'] == 'violation' for r in rows), rows)
+        rows = self.admin_records(source.replace('        return self.render_change_form',
+                                                 '        unknown(context)\n        return self.render_change_form'))
+        self.assertTrue(any(r['rule'] == '#647' and r['severity'] == 'info' for r in rows), rows)
+        self.assertFalse(any(r['rule'] == '#647' and r['severity'] == 'violation' for r in rows), rows)
+
+    def test_admin_context_origin_alias_fixed_slots_and_local_business(self):
+        source = """from typing import Any, TYPE_CHECKING
+from django.contrib import admin as adm
+if TYPE_CHECKING:
+    Base = adm.ModelAdmin[Book]
+else:
+    Base = adm.ModelAdmin
+class BookAdmin(Base):
+    inlines: list[type[adm.TabularInline[Any]]] = []
+    def get_form(self, request: object, **kwargs: Any) -> HttpResponse: ...
+    def get_inline_instances(self, request: object) -> list[adm.InlineModelAdmin[Any]]: ...
+    def render_change_form(self, request: object, context: dict[str, Any]) -> HttpResponse:
+        copied: dict[str, Any] = {**context, 'title': 'edit'}
+        copied = dict(copied)
+        copied = copied.copy()
+        if context is not None:
+            copied['subtitle'] = 'book'
+        return super().render_change_form(request, copied)
+"""
+        rows = self.admin_records(source)
+        self.assertEqual([r for r in rows if r['rule'] in ('#645', '#647')], [])
+        for prefix in ['class Base: pass\n', 'from unrelated import Base\n',
+                       'from django.contrib.admin import ModelAdmin as Base\nBase = object\n']:
+            rows = self.admin_records("from typing import Any\n" + prefix + source[source.index('class BookAdmin'):])
+            self.assertTrue(any(r['rule'] == '#647' for r in rows), rows)
+        rows = self.admin_records(source.replace("        copied: dict", "        payload: dict[str, Any] = {'amount': 10}\n        charge(payload['amount'])\n        copied: dict"))
+        self.assertTrue(any(r['rule'] == '#647' and '`payload`' in r['message'] and r['severity'] == 'violation' for r in rows), rows)
+        rows = self.admin_records(source.replace('class BookAdmin(Base):', 'class BookAdmin(adm.ModelAdmin[Book]):'))
+        self.assertTrue(any(r['rule'] == '#646' for r in rows), rows)
+        rows = self.admin_records(source.replace('request: object, context:', 'request, context:'))
+        self.assertTrue(any(r['rule'] == '#493' for r in rows), rows)
+        rows = self.admin_records(source.replace('        copied: dict', '        import json\n        decoded: dict[str, object] = json.loads(request.body)\n        copied: dict'))
+        self.assertTrue(any(r['rule'] == '#650' for r in rows), rows)
+
+    def test_admin_context_sources_consumption_rebind_and_bare_slots(self):
+        source = """from typing import Any
+from django.contrib.admin import ModelAdmin as Admin
+from django.template.response import TemplateResponse as Response
+class BookAdmin(Admin):
+    def changelist_view(self, request: object) -> HttpResponse:
+        bag: dict[str, Any] = self.admin_site.each_context(request)
+        bag.update({'title': 'books'})
+        return Response(request, 'book.html', bag)
+"""
+        for value in ["self.admin_site.each_context(request)", "{'title': 'books'}"]:
+            rows = self.admin_records(source.replace('self.admin_site.each_context(request)', value))
+            self.assertEqual([r for r in rows if r['rule'] in ('#645', '#647')], [], rows)
+        for consumption in ["charge(bag.get('amount'))", "amount = len(bag)", "bag + other", "self.saved = bag"]:
+            rows = self.admin_records(source.replace("        return Response", '        ' + consumption + '\n        return Response'))
+            self.assertTrue(any(r['rule'] == '#647' and r['severity'] == 'violation' for r in rows), rows)
+        rows = self.admin_records(source.replace('self.admin_site.each_context(request)', 'unknown()'))
+        self.assertTrue(any(r['rule'] == '#647' and r['severity'] == 'info' for r in rows), rows)
+        rows = self.admin_records(source + "\nclass Bare(Admin):\n    def render_change_form(self, request: object, context: Any) -> Any: ...\n")
+        self.assertTrue(any(r['rule'] == '#645' and '매개변수 `context`' in r['message'] and r['severity'] == 'violation' for r in rows), rows)
+        # A once-valid alias that is rebound to a local fake cannot preserve origin.
+        rows = self.admin_records(source.replace('class BookAdmin(Admin):', 'Alias = Admin\nAlias = object\nclass BookAdmin(Alias):'))
+        self.assertTrue(any(r['rule'] == '#647' and r['severity'] == 'violation' for r in rows), rows)
+
+    def test_admin_helper_return_cycles_and_mixed_bare_annotation(self):
+        source = """from typing import Any
+from parler.admin import TranslatableAdmin
+class BookAdmin(TranslatableAdmin):
+    def changeform_view(self, request: object, extra_context: dict[str, Any]) -> HttpResponse:
+        bag: dict[str, Any] = self._first(extra_context)
+        return super().changeform_view(request, extra_context=bag)
+    def _first(self, value: dict[str, Any]) -> dict[str, Any]:
+        return self._second(value)
+    def _second(self, value: dict[str, Any]) -> dict[str, Any]:
+        return dict(value)
+"""
+        rows = self.admin_records(source)
+        self.assertEqual([r for r in rows if r['rule'] in ('#645', '#647')], [], rows)
+        rows = self.admin_records(source.replace('return dict(value)', 'return self._first(value)'))
+        self.assertTrue(any(r['rule'] == '#647' and r['severity'] == 'info' for r in rows), rows)
+        self.assertFalse(any(r['rule'] == '#647' and r['severity'] == 'violation' for r in rows), rows)
+        rows = self.admin_records(source.replace('extra_context: dict[str, Any]', 'extra_context: dict[str, Any] | Any'))
+        self.assertTrue(any(r['rule'] == '#645' and r['severity'] == 'violation' for r in rows), rows)
+        rows = self.admin_records(source.replace('class BookAdmin(TranslatableAdmin):', 'class BookAdmin(TranslatableAdmin):\n    inlines: list[Any] = []'))
+        self.assertTrue(any(r['rule'] == '#645' and '`inlines`' in r['message'] for r in rows), rows)
+
+    def test_admin_context_shadowed_transport_names_are_not_framework_proof(self):
+        source = """from typing import Any
+from parler.admin import TranslatableAdmin
+from django.template.response import TemplateResponse as Response
+class BookAdmin(TranslatableAdmin):
+    def changeform_view(self, request: object, extra_context: dict[str, Any]) -> HttpResponse:
+        bag: dict[str, Any] = dict(extra_context)
+        return Response(request, 'book.html', bag)
+"""
+        variants = [source.replace('        bag:', insertion + '        bag:')
+                    for insertion in ['        Response = unknown\n', '        dict = unknown\n']]
+        variants.append(source.replace('class BookAdmin', 'dict = unknown\nclass BookAdmin'))
+        for variant in variants:
+            rows = self.admin_records(variant)
+            self.assertTrue(any(r['rule'] == '#647' and r['severity'] == 'info' for r in rows), rows)
+            self.assertFalse(any(r['rule'] == '#647' and r['severity'] == 'violation' for r in rows), rows)
 
     def mixed_fixture(self, *, tree: bool = True) -> None:
         shutil.copytree(FIXTURES / "api_error_controller_code/bad_rules", self.root, dirs_exist_ok=True)
         if tree:
             self.write(TREE, (FIXTURES / "api_error_controller/bad_rules" / TREE).read_text())
 
     def commit(self) -> str:
         _git(self.root, "init", "-q")
         _git(self.root, "add", "-A")
         _git(self.root, "commit", "-qm", "fixture anchor")

```

## workspace/tools/pregate_field_report_smoke.py

Before SHA256: ceab87ff2c0bcbfb08d8604a34b75407dd89670efb43c5d4cbae8ef610418295
After SHA256: f50bbe33afb4e94becaedd9a6b548fa7c353eff38f4d5ce758ca3caeb8dcb809

```diff
--- before/workspace/tools/pregate_field_report_smoke.py
+++ after/workspace/tools/pregate_field_report_smoke.py
@@ -402,20 +402,122 @@
             self.assertEqual([(x.rule, x.confirmed) for x in pg.check_declarations(plan, self.source)], [('#202', False)])
 
     def cli(self, text):
         spec = self.root / 'design.md'
         spec.write_text(text)
         report = self.root / 'report.md'
         if report.exists(): report.unlink()
         run = subprocess.run([sys.executable, '-B', str(SCRIPTS / 'design_pregate.py'), str(spec),
                               str(self.source), '--report', str(report)], capture_output=True, text=True, env=self.env)
         return run, report.read_text() if report.exists() else ''
+
+    def test_generated_admin_cli_defers_open_slots_but_keeps_bare_any(self):
+        path = 'framework/admin/book.py'
+        text = spec_text([f'add {path}'], [f'{path}::BookAdmin(admin.ModelAdmin)',
+            f'{path}::BookAdmin._context(context: dict[str, Any], payload: dict[str, object], opaque: Any) -> dict[str, object]',
+            f'{path}::OtherAdmin(admin.ModelAdmin)',
+            f'{path}::OtherAdmin._context(context: dict[str, Any]) -> dict[str, object]'],
+            [f'{path}  from django.contrib import admin', f'{path}  from typing import Any'])
+        run, report = self.cli(text)
+        self.assertEqual(run.returncode, 2, run.stdout + run.stderr)
+        section = report.split('### 생성 본문 S1 미검증', 1)[1].split('###', 1)[0]
+        self.assertIn('S1:', section)
+        self.assertIn('매개변수 `context`', section)
+        self.assertIn('매개변수 `payload`', section)  # original #647 candidate must remain visible
+        self.assertIn('반환 타입', section)
+        self.assertNotIn('매개변수 `opaque`', section)
+        self.assertIn('매개변수 `opaque`', report)
+        checked = subprocess.run([sys.executable, '-B', str(SCRIPTS / 'design_pregate.py'),
+            str(self.root / 'design.md'), str(self.source), '--check-report', str(self.root / 'report.md')],
+            capture_output=True, text=True, env=self.env)
+        self.assertEqual(checked.returncode, 3, checked.stdout + checked.stderr)
+        self.assertIn('S1 미검증', checked.stdout)
+
+    def test_generated_admin_exact_multiline_slots_and_mixed_cohorts(self):
+        path = 'framework/admin/book.py'
+        self.write(self.source, path, """from typing import Any
+from parler.admin import TranslatableAdmin
+class First(TranslatableAdmin):
+    def _context(
+        self,
+        renamed: dict[str, Any],
+        payload: dict[str, object],
+        opaque: Any,
+        nested: list[Any],
+    ) -> dict[str, object]:
+        raise NotImplementedError
+class Second(TranslatableAdmin):
+    def _context(self, renamed: dict[str, Any]) -> dict[str, object]:
+        raise NotImplementedError
+""")
+        records_path = self.root / 'findings.jsonl'
+        run = subprocess.run([sys.executable, '-B', str(SCRIPTS / 'check-public-surface-annotation.py'), str(self.source)],
+            capture_output=True, text=True, env=self.env)
+        self.assertEqual(run.returncode, 2, run.stdout + run.stderr)
+        rows = [json.loads(line) for line in records_path.read_text().splitlines()]
+        rows = [r for r in rows if r['file'].startswith(path + ':')]
+        lines = lambda records: list(dict.fromkeys(f"{r['checker']} :: {pg.registry._normalize(pg.findings.line_of_record(r), ())}" for r in records))
+        violations = [r for r in rows if r['severity'] == 'violation']
+        candidates = [r for r in rows if r['severity'] == 'info']
+        gate = dict(raw_exit=2, raw_stdout=run.stdout, attributed_lines=lines(violations), records=violations,
+                    unmatched_lines=[], candidate_lines=lines(candidates), candidate_records=candidates)
+        generated = {path: [dict(owner='First', method='_context', lineno=4, end_lineno=11),
+                            dict(owner='Second', method='_context', lineno=13, end_lineno=14)]}
+        retained, deferred = pg.partition_generated_findings(gate, generated, self.source)
+        self.assertEqual(len(retained), 1, retained)
+        self.assertIn('`opaque`', retained[0])
+        self.assertEqual(len(deferred), 3, deferred)
+        self.assertTrue(any('`renamed`' in line for line in deferred))
+        self.assertTrue(any('`payload`' in line for line in deferred))
+        self.assertFalse(any('`nested`' in line for line in deferred))
+        # Same normalized key spans both classes. One non-generated location retains all of it.
+        retained, deferred = pg.partition_generated_findings(gate, {path: generated[path][:1]}, self.source)
+        self.assertEqual(len(retained), 3, retained)
+        self.assertEqual(len(deferred), 1, deferred)
+        # A signature diagnostic at the argument line is not def-line evidence.
+        shifted = dict(gate, records=[dict(r, file=f'{path}:6') if '매개변수 `renamed`' in r['message'] else r for r in violations])
+        retained, deferred = pg.partition_generated_findings(shifted, generated, self.source)
+        self.assertTrue(any('`renamed`' in line for line in retained), retained)
+        # Neither free prose nor file_raw nor a normalized :N can recover a slot.
+        for changes in [dict(message='context must be typed'), dict(file=f'{path}:N', file_raw=f'/tmp/{path}:4'),
+                        dict(checker='other-checker.py')]:
+            altered = [dict(violations[0], **changes), *violations[1:]]
+            bad = dict(gate, records=altered, attributed_lines=lines(altered))
+            retained, deferred = pg.partition_generated_findings(bad, generated, self.source)
+            self.assertIn(lines(altered)[0], retained)
+        self.assertEqual(pg.partition_generated_findings(gate, {}, self.source), (gate['attributed_lines'], []))
+
+    def test_admin_source_business_body_is_legacy_not_generated_s1(self):
+        path = 'framework/admin/book.py'
+        original = """from typing import Any
+from parler.admin import TranslatableAdmin
+class BookAdmin(TranslatableAdmin):
+    def changeform_view(self, request: object, extra_context: dict[str, Any]) -> HttpResponse:
+        return self._context(extra_context)
+    def _context(self, payload: dict[str, Any]) -> dict[str, Any]:
+        charge(payload['amount'])
+        return payload
+"""
+        self.write(self.source, path, original)
+        _git(self.source, 'add', '-A')
+        _git(self.source, 'commit', '-qm', 'actual admin baseline')
+        text = spec_text([f'update {path}'], [f'{path}::BookAdmin(TranslatableAdmin)',
+                            f'{path}::BookAdmin._context(payload: dict[str, Any]) -> dict[str, Any]'])
+        run, report = self.cli(text)
+        self.assertEqual(run.returncode, 4, run.stdout + run.stderr)
+        self.assertIn('실체화 0건', run.stdout)
+        self.assertNotIn('S1:', report)
+        self.assertEqual((self.source / path).read_text(), original)
+        records = subprocess.run([sys.executable, '-B', str(SCRIPTS / 'check-public-surface-annotation.py'), str(self.source)],
+            capture_output=True, text=True, env=self.env)
+        self.assertEqual(records.returncode, 2, records.stdout + records.stderr)
+        self.assertIn('[#647]', records.stdout)
 
     def uow_fixture(self):
         shutil.rmtree(self.source)
         self.source = _make_repo(self.root, 'uow-source')
         pg.materialize_skeleton(self.source, 'orders')
         port = 'application/orders/application_layer/port/unit_of_work/order_unit_of_work.py'
         impl = 'application/orders/driven_layer/adapter/persistence/unit_of_work/order_unit_of_work.py'
         self.write(self.source, port, 'from abc import ABC, abstractmethod\nclass OrdersUnitOfWork(ABC):\n'
                    '    @abstractmethod\n    def __enter__(self): ...\n'
                    '    @abstractmethod\n    def __exit__(self, *args): ...\n'

```
