# task-4-fix2 review package

No commit was authorized. This package compares owned-file snapshots before this task with current bytes.

## dddjango/scripts/check-context-isolation.py

Before SHA256: 5c64e9f1b0a0ccbde4e918a0660d6fd40e8f442e45138bd1e0e85208e42750dd
After SHA256: 5c64e9f1b0a0ccbde4e918a0660d6fd40e8f442e45138bd1e0e85208e42750dd

```diff

```

## codex-dddjango/skills/dddjango/scripts/check-context-isolation.py

Before SHA256: 5c64e9f1b0a0ccbde4e918a0660d6fd40e8f442e45138bd1e0e85208e42750dd
After SHA256: 5c64e9f1b0a0ccbde4e918a0660d6fd40e8f442e45138bd1e0e85208e42750dd

```diff

```

## dddjango/scripts/check-domain-model.py

Before SHA256: 3da1f13672f5da6fd73c1284152939b1239f57202fe00eb2d07aa3d68b50a9ac
After SHA256: 3da1f13672f5da6fd73c1284152939b1239f57202fe00eb2d07aa3d68b50a9ac

```diff

```

## codex-dddjango/skills/dddjango/scripts/check-domain-model.py

Before SHA256: 3da1f13672f5da6fd73c1284152939b1239f57202fe00eb2d07aa3d68b50a9ac
After SHA256: 3da1f13672f5da6fd73c1284152939b1239f57202fe00eb2d07aa3d68b50a9ac

```diff

```

## dddjango/scripts/check-port-adapter-pairing.py

Before SHA256: 682823f8599339f50fede9a9f23d6b0557b2c252a619885571970432ddabace4
After SHA256: 0facb9d3bfbdf9b8e7fc9a9325ab58a2d3a3e0959f8410312c7549a63dc3d77f

```diff
--- before/dddjango/scripts/check-port-adapter-pairing.py
+++ after/dddjango/scripts/check-port-adapter-pairing.py
@@ -1209,28 +1209,36 @@
 
     def parameters(fn, env):
         for arg in (*fn.args.posonlyargs, *fn.args.args, *fn.args.kwonlyargs):
             env[arg.arg] = origin(address(arg.annotation, env))
         for arg in (fn.args.vararg, fn.args.kwarg):
             if arg: env[arg.arg] = ""
 
     # 최초 정적 별칭은 보존한다. 이미 바인딩된 모듈 이름의 재대입은 함수에서 불명이다.
     rebound = set()
     bound = set()
-    for st in mod.body:
+    pending = list(reversed(mod.body))
+    while pending:
+        st = pending.pop()
         if isinstance(st, (ast.Import, ast.ImportFrom)):
             names = set(imported(st, py))
         elif isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
             names = {st.name}
         elif isinstance(st, (ast.Assign, ast.AnnAssign, ast.AugAssign, ast.Delete)):
             targets = st.targets if isinstance(st, (ast.Assign, ast.Delete)) else [st.target]
             names = {key(t) for t in targets}
+        elif isinstance(st, (ast.Name, ast.Attribute)) and isinstance(st.ctx, (ast.Store, ast.Del)):
+            names = {key(st)}
+        elif isinstance(st, (ast.If, ast.For, ast.AsyncFor, ast.While, ast.Try, ast.With, ast.AsyncWith, ast.ExceptHandler)):
+            # 모듈 실행 구간만 펼친다. 위의 함수/클래스 정의는 이름만 바인딩한다.
+            pending.extend(reversed(list(ast.iter_child_nodes(st))))
+            names = {st.name} if isinstance(st, ast.ExceptHandler) and st.name else set()
         else:
             continue
         rebound.update(names & bound)
         bound.update(names)
 
     def block(body, env):
         for st in body:
             if isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef)):
                 local = dict(env)
                 for name in rebound: local[name] = ""

```

## codex-dddjango/skills/dddjango/scripts/check-port-adapter-pairing.py

Before SHA256: 682823f8599339f50fede9a9f23d6b0557b2c252a619885571970432ddabace4
After SHA256: 0facb9d3bfbdf9b8e7fc9a9325ab58a2d3a3e0959f8410312c7549a63dc3d77f

```diff
--- before/codex-dddjango/skills/dddjango/scripts/check-port-adapter-pairing.py
+++ after/codex-dddjango/skills/dddjango/scripts/check-port-adapter-pairing.py
@@ -1209,28 +1209,36 @@
 
     def parameters(fn, env):
         for arg in (*fn.args.posonlyargs, *fn.args.args, *fn.args.kwonlyargs):
             env[arg.arg] = origin(address(arg.annotation, env))
         for arg in (fn.args.vararg, fn.args.kwarg):
             if arg: env[arg.arg] = ""
 
     # 최초 정적 별칭은 보존한다. 이미 바인딩된 모듈 이름의 재대입은 함수에서 불명이다.
     rebound = set()
     bound = set()
-    for st in mod.body:
+    pending = list(reversed(mod.body))
+    while pending:
+        st = pending.pop()
         if isinstance(st, (ast.Import, ast.ImportFrom)):
             names = set(imported(st, py))
         elif isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
             names = {st.name}
         elif isinstance(st, (ast.Assign, ast.AnnAssign, ast.AugAssign, ast.Delete)):
             targets = st.targets if isinstance(st, (ast.Assign, ast.Delete)) else [st.target]
             names = {key(t) for t in targets}
+        elif isinstance(st, (ast.Name, ast.Attribute)) and isinstance(st.ctx, (ast.Store, ast.Del)):
+            names = {key(st)}
+        elif isinstance(st, (ast.If, ast.For, ast.AsyncFor, ast.While, ast.Try, ast.With, ast.AsyncWith, ast.ExceptHandler)):
+            # 모듈 실행 구간만 펼친다. 위의 함수/클래스 정의는 이름만 바인딩한다.
+            pending.extend(reversed(list(ast.iter_child_nodes(st))))
+            names = {st.name} if isinstance(st, ast.ExceptHandler) and st.name else set()
         else:
             continue
         rebound.update(names & bound)
         bound.update(names)
 
     def block(body, env):
         for st in body:
             if isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef)):
                 local = dict(env)
                 for name in rebound: local[name] = ""

```

## workspace/tools/field_report_checker_smoke.py

Before SHA256: de7bb136f1abd67b528f75c87c5715a6e980d33b19dc0362a12de62c03ff2de8
After SHA256: 044d628fd7e4cafdb4090082374f333c9db5fd45a27d8a079e1022779df0b2ae

```diff
--- before/workspace/tools/field_report_checker_smoke.py
+++ after/workspace/tools/field_report_checker_smoke.py
@@ -347,20 +347,46 @@
             ("from requests import Response as Source", "value.status_code == 200", "violation"),
             ("from application.lesson.domain_layer.book.kind import Kind as Source", "value.code == 1", None),
         ]:
             for suffix, wanted in [("", expected), ("Alias = dynamic\n", "candidate"),
                                    ("if flag: Alias = dynamic\n", "candidate")]:
                 with self.subTest(imported=imported, suffix=suffix):
                     source = imported + "\nAlias = Source\n" + suffix + "def run(value: Alias): return " + comparison + "\n"
                     f, c = self.property_rules(source)
                     self.assertEqual("#557" in f, wanted == "violation")
                     self.assertEqual("#557" in c, wanted == "candidate")
+
+    def test_later_module_compound_rebinding_invalidates_function_constructor(self):
+        for imported, comparison in [
+            ("from requests import Response as Source", "value.status_code == 200"),
+            ("from application.lesson.domain_layer.book.kind import Kind as Source", "value.code == 1"),
+        ]:
+            for later in ["if flag: Alias = dynamic", "while flag: Alias = dynamic",
+                          "for item in items: Alias = dynamic", "with context: Alias = dynamic",
+                          "try: Alias = dynamic\nexcept Exception: pass"]:
+                with self.subTest(imported=imported, later=later):
+                    source = imported + "\nAlias = Source\ndef run():\n    value = Alias()\n    return " + comparison + "\n" + later + "\n"
+                    f, c = self.property_rules(source)
+                    self.assertNotIn("#557", f)
+                    self.assertIn("#557", c)
+
+    def test_nested_definition_bindings_do_not_rebind_module_constructor_alias(self):
+        for imported, comparison, vendor in [
+            ("from requests import Response as Source", "value.status_code == 200", True),
+            ("from application.lesson.domain_layer.book.kind import Kind as Source", "value.code == 1", False),
+        ]:
+            for definition in ["def unused():", "class Unused:"]:
+                with self.subTest(imported=imported, definition=definition):
+                    source = imported + "\nAlias = Source\ndef run():\n    value = Alias()\n    return " + comparison + "\nif flag:\n    " + definition + "\n        Alias = dynamic\n"
+                    f, c = self.property_rules(source)
+                    self.assertEqual("#557" in f, vendor)
+                    self.assertNotIn("#557", c)
 
     def admin_records(self, source):
         self.write("framework/admin/book.py", source)
         records = self.root / "findings.jsonl"
         records.unlink(missing_ok=True)
         run = subprocess.run([sys.executable, '-B', str(SCRIPTS / 'check-public-surface-annotation.py'),
                               str(self.root)], env=self.env, text=True, capture_output=True)
         self.assertIn(run.returncode, (0, 2), run.stdout + run.stderr)
         return [json.loads(line) for line in records.read_text().splitlines()] if records.exists() else []
 

```
