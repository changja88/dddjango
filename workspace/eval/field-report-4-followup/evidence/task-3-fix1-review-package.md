# task-3-fix1 review package

No commit was authorized. This package compares owned-file snapshots before this task with current bytes.

## dddjango/scripts/check-public-surface-annotation.py

Before SHA256: 60696373a2717f59128b8281896545be085bf8585616a859d9d38cb641ce8635
After SHA256: 47afd19d407adc3318a68bb799841b368f860a7b703880d522d14108e78d6e06

```diff
--- before/dddjango/scripts/check-public-surface-annotation.py
+++ after/dddjango/scripts/check-public-surface-annotation.py
@@ -892,21 +892,22 @@
             while isinstance(root, ast.Attribute):
                 root = root.value
             if isinstance(root, ast.Name) and root.id in shadowed[fn] and root.id != "self":
                 return False
             name = _dotted(call.func, origins)
             if name in {"django.template.response.TemplateResponse", "django.shortcuts.render"}:
                 return True
             if isinstance(call.func, ast.Attribute):
                 receiver = call.func.value
                 if isinstance(receiver, ast.Call) and isinstance(receiver.func, ast.Name) and receiver.func.id == "super":
-                    return "super" not in shadowed[fn] and (call.func.attr == fn.name or call.func.attr == "render_change_form")
+                    return "super" not in shadowed[fn] and "super" not in module_shadowed \
+                        and (call.func.attr == fn.name or call.func.attr == "render_change_form")
                 return isinstance(receiver, ast.Name) and receiver.id == "self" and call.func.attr == "render_change_form"
             return False
 
         def each_context(expr: ast.AST | None) -> bool:
             return isinstance(expr, ast.Call) and _dotted(expr.func, {}) == "self.admin_site.each_context"
 
         def helper_of(expr: ast.AST | None) -> ast.FunctionDef | ast.AsyncFunctionDef | None:
             if isinstance(expr, ast.Call) and isinstance(expr.func, ast.Attribute) and isinstance(expr.func.value, ast.Name) \
                     and expr.func.value.id == "self" and expr.func.attr.startswith("_") and counts.get(expr.func.attr) == 1:
                 return methods[expr.func.attr]
@@ -1001,21 +1002,23 @@
 
         for (fn, name) in list(states):
             if name == "<return>":
                 continue
             for node in bodies[fn]:
                 if not isinstance(node, ast.Name) or node.id != name or not isinstance(node.ctx, ast.Load):
                     continue
                 parent = parents.get(node)
                 status = "allow"
                 if isinstance(parent, ast.Subscript) and parent.value is node:
-                    status = "allow" if isinstance(parent.ctx, ast.Store) and isinstance(parent.slice, ast.Constant) and isinstance(parent.slice.value, str) else "ordinary"
+                    ui_write = isinstance(parent.ctx, ast.Store) and isinstance(parent.slice, ast.Constant) \
+                        and isinstance(parent.slice.value, str) and not isinstance(parents.get(parent), ast.AugAssign)
+                    status = "allow" if ui_write else "ordinary"
                 elif isinstance(parent, (ast.BinOp, ast.UnaryOp, ast.AugAssign)):
                     status = "ordinary"
                 elif isinstance(parent, ast.Compare):
                     status = "allow" if len(parent.ops) == 1 and isinstance(parent.ops[0], (ast.Is, ast.IsNot)) and any(isinstance(n, ast.Constant) and n.value is None for n in [parent.left, *parent.comparators]) else "ordinary"
                 else:
                     current: ast.AST = node
                     while parents.get(current) is not None and not isinstance(parents[current], ast.stmt):
                         current = parents[current]
                         if isinstance(current, ast.Call):
                             call = current

```

## dddjango/scripts/design_pregate.py

Before SHA256: 50b530a0fa498fdb3d19650e790d758ae2cae2740a6bd914a132362e1902dabd
After SHA256: 50b530a0fa498fdb3d19650e790d758ae2cae2740a6bd914a132362e1902dabd

```diff

```

## codex-dddjango/skills/dddjango/scripts/check-public-surface-annotation.py

Before SHA256: 60696373a2717f59128b8281896545be085bf8585616a859d9d38cb641ce8635
After SHA256: 47afd19d407adc3318a68bb799841b368f860a7b703880d522d14108e78d6e06

```diff
--- before/codex-dddjango/skills/dddjango/scripts/check-public-surface-annotation.py
+++ after/codex-dddjango/skills/dddjango/scripts/check-public-surface-annotation.py
@@ -892,21 +892,22 @@
             while isinstance(root, ast.Attribute):
                 root = root.value
             if isinstance(root, ast.Name) and root.id in shadowed[fn] and root.id != "self":
                 return False
             name = _dotted(call.func, origins)
             if name in {"django.template.response.TemplateResponse", "django.shortcuts.render"}:
                 return True
             if isinstance(call.func, ast.Attribute):
                 receiver = call.func.value
                 if isinstance(receiver, ast.Call) and isinstance(receiver.func, ast.Name) and receiver.func.id == "super":
-                    return "super" not in shadowed[fn] and (call.func.attr == fn.name or call.func.attr == "render_change_form")
+                    return "super" not in shadowed[fn] and "super" not in module_shadowed \
+                        and (call.func.attr == fn.name or call.func.attr == "render_change_form")
                 return isinstance(receiver, ast.Name) and receiver.id == "self" and call.func.attr == "render_change_form"
             return False
 
         def each_context(expr: ast.AST | None) -> bool:
             return isinstance(expr, ast.Call) and _dotted(expr.func, {}) == "self.admin_site.each_context"
 
         def helper_of(expr: ast.AST | None) -> ast.FunctionDef | ast.AsyncFunctionDef | None:
             if isinstance(expr, ast.Call) and isinstance(expr.func, ast.Attribute) and isinstance(expr.func.value, ast.Name) \
                     and expr.func.value.id == "self" and expr.func.attr.startswith("_") and counts.get(expr.func.attr) == 1:
                 return methods[expr.func.attr]
@@ -1001,21 +1002,23 @@
 
         for (fn, name) in list(states):
             if name == "<return>":
                 continue
             for node in bodies[fn]:
                 if not isinstance(node, ast.Name) or node.id != name or not isinstance(node.ctx, ast.Load):
                     continue
                 parent = parents.get(node)
                 status = "allow"
                 if isinstance(parent, ast.Subscript) and parent.value is node:
-                    status = "allow" if isinstance(parent.ctx, ast.Store) and isinstance(parent.slice, ast.Constant) and isinstance(parent.slice.value, str) else "ordinary"
+                    ui_write = isinstance(parent.ctx, ast.Store) and isinstance(parent.slice, ast.Constant) \
+                        and isinstance(parent.slice.value, str) and not isinstance(parents.get(parent), ast.AugAssign)
+                    status = "allow" if ui_write else "ordinary"
                 elif isinstance(parent, (ast.BinOp, ast.UnaryOp, ast.AugAssign)):
                     status = "ordinary"
                 elif isinstance(parent, ast.Compare):
                     status = "allow" if len(parent.ops) == 1 and isinstance(parent.ops[0], (ast.Is, ast.IsNot)) and any(isinstance(n, ast.Constant) and n.value is None for n in [parent.left, *parent.comparators]) else "ordinary"
                 else:
                     current: ast.AST = node
                     while parents.get(current) is not None and not isinstance(parents[current], ast.stmt):
                         current = parents[current]
                         if isinstance(current, ast.Call):
                             call = current

```

## codex-dddjango/skills/dddjango/scripts/design_pregate.py

Before SHA256: 50b530a0fa498fdb3d19650e790d758ae2cae2740a6bd914a132362e1902dabd
After SHA256: 50b530a0fa498fdb3d19650e790d758ae2cae2740a6bd914a132362e1902dabd

```diff

```

## workspace/tools/field_report_checker_smoke.py

Before SHA256: d2e2f3dcb151746cdab3ca15951d638991e96f231f84338d8a14333e28ec9936
After SHA256: aa45b0134d4c3b2c57ace15b529ab893c5b006d8b41d2520107c347a9f6e5890

```diff
--- before/workspace/tools/field_report_checker_smoke.py
+++ after/workspace/tools/field_report_checker_smoke.py
@@ -232,20 +232,43 @@
         bag: dict[str, Any] = dict(extra_context)
         return Response(request, 'book.html', bag)
 """
         variants = [source.replace('        bag:', insertion + '        bag:')
                     for insertion in ['        Response = unknown\n', '        dict = unknown\n']]
         variants.append(source.replace('class BookAdmin', 'dict = unknown\nclass BookAdmin'))
         for variant in variants:
             rows = self.admin_records(variant)
             self.assertTrue(any(r['rule'] == '#647' and r['severity'] == 'info' for r in rows), rows)
             self.assertFalse(any(r['rule'] == '#647' and r['severity'] == 'violation' for r in rows), rows)
+
+    def test_admin_augmented_write_and_module_super_shadow_preserve_diagnostics(self):
+        source = """from typing import Any
+from parler.admin import TranslatableAdmin
+class BookAdmin(TranslatableAdmin):
+    def changeform_view(self, request: object, extra_context: dict[str, Any]) -> HttpResponse:
+        extra_context['title'] = 'Books'
+        return super().changeform_view(request, extra_context=extra_context)
+"""
+        cases = [
+            ('plain UI assignment', source, []),
+            ('ordinary read', source.replace("extra_context['title'] = 'Books'", "total = extra_context['amount'] + 1"), ['violation']),
+            ('augmented write', source.replace("extra_context['title'] = 'Books'", "extra_context['amount'] += 1"), ['violation']),
+            ('module super shadow', source.replace('class BookAdmin', 'super = unknown\nclass BookAdmin'), ['info']),
+        ]
+        for label, variant, expected in cases:
+            with self.subTest(case=label):
+                rows = self.admin_records(variant)
+                context_rows = [r for r in rows if r['rule'] in ('#645', '#647')]
+                self.assertEqual([r['severity'] for r in context_rows], expected, context_rows)
+                if expected:
+                    self.assertEqual([r['rule'] for r in context_rows], ['#647'])
+                    self.assertIn('매개변수 `extra_context`', context_rows[0]['message'])
 
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

Before SHA256: f50bbe33afb4e94becaedd9a6b548fa7c353eff38f4d5ce758ca3caeb8dcb809
After SHA256: f50bbe33afb4e94becaedd9a6b548fa7c353eff38f4d5ce758ca3caeb8dcb809

```diff

```
