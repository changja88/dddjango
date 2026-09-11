# task-4-fix1 review package

No commit was authorized. This package compares owned-file snapshots before this task with current bytes.

## dddjango/scripts/check-context-isolation.py

Before SHA256: f15ae6fc8fc35a434419c6f7617bf7db916de26ab934b53f9a8c17b9b5b86131
After SHA256: 5c64e9f1b0a0ccbde4e918a0660d6fd40e8f442e45138bd1e0e85208e42750dd

```diff
--- before/dddjango/scripts/check-context-isolation.py
+++ after/dddjango/scripts/check-context-isolation.py
@@ -490,23 +490,26 @@
                     for item in st.items:
                         inspect(item.context_expr, env)
                     branch = dict(env)
                     for item in st.items:
                         if item.optional_vars:
                             for n in ast.walk(item.optional_vars):
                                 if isinstance(n, ast.Name): branch[n.id] = ""
                     block(st.body, branch)
                     branches = [branch, env]
                 else:
+                    condition_before = count
                     for field in ("test", "iter"):
                         value = getattr(st, field, None)
                         if value is not None: inspect(value, env)
+                    if isinstance(st, ast.While) and count != condition_before:
+                        unknown = True
                     branch = dict(env)
                     if isinstance(st, (ast.For, ast.AsyncFor)):
                         for n in ast.walk(st.target):
                             if isinstance(n, ast.Name): branch[n.id] = ""
                     before = count
                     block(st.body, branch)
                     if isinstance(st, (ast.For, ast.AsyncFor, ast.While)) and count != before:
                         unknown = True
                     other = dict(env)
                     block(st.orelse, other)

```

## codex-dddjango/skills/dddjango/scripts/check-context-isolation.py

Before SHA256: f15ae6fc8fc35a434419c6f7617bf7db916de26ab934b53f9a8c17b9b5b86131
After SHA256: 5c64e9f1b0a0ccbde4e918a0660d6fd40e8f442e45138bd1e0e85208e42750dd

```diff
--- before/codex-dddjango/skills/dddjango/scripts/check-context-isolation.py
+++ after/codex-dddjango/skills/dddjango/scripts/check-context-isolation.py
@@ -490,23 +490,26 @@
                     for item in st.items:
                         inspect(item.context_expr, env)
                     branch = dict(env)
                     for item in st.items:
                         if item.optional_vars:
                             for n in ast.walk(item.optional_vars):
                                 if isinstance(n, ast.Name): branch[n.id] = ""
                     block(st.body, branch)
                     branches = [branch, env]
                 else:
+                    condition_before = count
                     for field in ("test", "iter"):
                         value = getattr(st, field, None)
                         if value is not None: inspect(value, env)
+                    if isinstance(st, ast.While) and count != condition_before:
+                        unknown = True
                     branch = dict(env)
                     if isinstance(st, (ast.For, ast.AsyncFor)):
                         for n in ast.walk(st.target):
                             if isinstance(n, ast.Name): branch[n.id] = ""
                     before = count
                     block(st.body, branch)
                     if isinstance(st, (ast.For, ast.AsyncFor, ast.While)) and count != before:
                         unknown = True
                     other = dict(env)
                     block(st.orelse, other)

```

## dddjango/scripts/check-domain-model.py

Before SHA256: 117a2c52e8a22a2c7661ceaac3263d2fde072f37ff19188519dbf11bf2a2e208
After SHA256: 3da1f13672f5da6fd73c1284152939b1239f57202fe00eb2d07aa3d68b50a9ac

```diff
--- before/dddjango/scripts/check-domain-model.py
+++ after/dddjango/scripts/check-domain-model.py
@@ -446,24 +446,28 @@
         f.add("#543", _rel(root, py, cls.lineno),
               "이벤트 기록은 있는데 pull_events() 가 없다 — 꺼내는 창구는 그 하나다")
 
 
 def _closed_standard_enum(mod: ast.Module, cls: ast.ClassDef) -> tuple[bool, bool]:
     """정확한 표준 enum 기저 + 정적 멤버만 면제한다. 동적 확장은 후보다."""
     origins = {}
     for st in mod.body:
         if st is cls:
             break
-        if isinstance(st, ast.ImportFrom) and st.module == "enum" and not st.level:
-            origins.update({a.asname or a.name: "enum." + a.name for a in st.names})
+        if isinstance(st, ast.ImportFrom):
+            for a in st.names:
+                origins.pop(a.asname or a.name, None)
+            if st.module == "enum" and not st.level:
+                origins.update({a.asname or a.name: "enum." + a.name for a in st.names})
         elif isinstance(st, ast.Import):
             for a in st.names:
+                origins.pop(a.asname or a.name.split(".")[0], None)
                 if a.name == "enum": origins[a.asname or a.name] = "enum"
         else:
             for n in ast.walk(st):
                 if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store): origins.pop(n.id, None)
                 if isinstance(n, ast.Attribute) and isinstance(n.ctx, (ast.Store, ast.Del)):
                     base = n.value
                     while isinstance(base, ast.Attribute): base = base.value
                     if isinstance(base, ast.Name): origins.pop(base.id, None)
             if isinstance(st, (ast.FunctionDef, ast.ClassDef)): origins.pop(st.name, None)
     def name(expr):
@@ -814,29 +818,29 @@
         if isinstance(expr, ast.Attribute):
             base = address(expr.value, env)
             return base + "." + expr.attr if base else ""
         return ""
 
     def is_uow(name):
         parts = name.split(".")
         return (".application_layer.port.unit_of_work." in name and len(parts) > 1
                 and parts[-2].endswith("_unit_of_work") and parts[-1].endswith("UnitOfWork"))
 
-    module_env = imports(mod.body)
-    factories = {}
+    module_env = {}
     for st in mod.body:
-        if isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef)) and is_uow(address(st.returns, module_env)):
-            factories[st.name] = "@uow"
+        if isinstance(st, (ast.Import, ast.ImportFrom)):
+            module_env.update(imports([st]))
+        elif isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef)):
+            module_env[st.name] = "@uow" if is_uow(address(st.returns, module_env)) else ""
         elif isinstance(st, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
             for target in st.targets if isinstance(st, ast.Assign) else [st.target]:
                 module_env[key(target)] = ""
-    module_env.update(factories)
 
     def origin(expr, env):
         if isinstance(expr, ast.Call):
             name = address(expr.func, env)
             if is_uow(name) or name == "@uow": return "@uow"
             parts = name.split(".")
             source = root.joinpath(*parts[:-1]).with_suffix(".py")
             declaration = _parse(source) if source.is_file() else None
             if declaration:
                 target = next((st for st in declaration.body if isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef)) and st.name == parts[-1]), None)
@@ -854,20 +858,24 @@
         init = next((st for st in cls.body if isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef)) and st.name == "__init__"), None)
         if init:
             init_env = dict(module_env)
             params(init, init_env)
             # 생성자 직접 주입/별칭만 지원한다. 분기·helper는 확정하지 않는다.
             for st in init.body:
                 if isinstance(st, (ast.Assign, ast.AnnAssign)):
                     value = origin(st.value, init_env)
                     for target in st.targets if isinstance(st, ast.Assign) else [st.target]:
                         init_env[key(target)] = value
+                elif not isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
+                    for target in _function_nodes(st):
+                        if isinstance(target, (ast.Name, ast.Attribute)) and isinstance(target.ctx, (ast.Store, ast.Del)):
+                            init_env[key(target)] = ""
             env.update({k: v for k, v in init_env.items() if k.startswith("self.")})
     params(fn, env)
     regions = {0: set()}
     unknown = False
 
     def atomic(expr, local):
         target = expr.func if isinstance(expr, ast.Call) else expr
         return address(target, local) == "django.db.transaction.atomic"
 
     def scan(expr, local, region):

```

## codex-dddjango/skills/dddjango/scripts/check-domain-model.py

Before SHA256: 117a2c52e8a22a2c7661ceaac3263d2fde072f37ff19188519dbf11bf2a2e208
After SHA256: 3da1f13672f5da6fd73c1284152939b1239f57202fe00eb2d07aa3d68b50a9ac

```diff
--- before/codex-dddjango/skills/dddjango/scripts/check-domain-model.py
+++ after/codex-dddjango/skills/dddjango/scripts/check-domain-model.py
@@ -446,24 +446,28 @@
         f.add("#543", _rel(root, py, cls.lineno),
               "이벤트 기록은 있는데 pull_events() 가 없다 — 꺼내는 창구는 그 하나다")
 
 
 def _closed_standard_enum(mod: ast.Module, cls: ast.ClassDef) -> tuple[bool, bool]:
     """정확한 표준 enum 기저 + 정적 멤버만 면제한다. 동적 확장은 후보다."""
     origins = {}
     for st in mod.body:
         if st is cls:
             break
-        if isinstance(st, ast.ImportFrom) and st.module == "enum" and not st.level:
-            origins.update({a.asname or a.name: "enum." + a.name for a in st.names})
+        if isinstance(st, ast.ImportFrom):
+            for a in st.names:
+                origins.pop(a.asname or a.name, None)
+            if st.module == "enum" and not st.level:
+                origins.update({a.asname or a.name: "enum." + a.name for a in st.names})
         elif isinstance(st, ast.Import):
             for a in st.names:
+                origins.pop(a.asname or a.name.split(".")[0], None)
                 if a.name == "enum": origins[a.asname or a.name] = "enum"
         else:
             for n in ast.walk(st):
                 if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store): origins.pop(n.id, None)
                 if isinstance(n, ast.Attribute) and isinstance(n.ctx, (ast.Store, ast.Del)):
                     base = n.value
                     while isinstance(base, ast.Attribute): base = base.value
                     if isinstance(base, ast.Name): origins.pop(base.id, None)
             if isinstance(st, (ast.FunctionDef, ast.ClassDef)): origins.pop(st.name, None)
     def name(expr):
@@ -814,29 +818,29 @@
         if isinstance(expr, ast.Attribute):
             base = address(expr.value, env)
             return base + "." + expr.attr if base else ""
         return ""
 
     def is_uow(name):
         parts = name.split(".")
         return (".application_layer.port.unit_of_work." in name and len(parts) > 1
                 and parts[-2].endswith("_unit_of_work") and parts[-1].endswith("UnitOfWork"))
 
-    module_env = imports(mod.body)
-    factories = {}
+    module_env = {}
     for st in mod.body:
-        if isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef)) and is_uow(address(st.returns, module_env)):
-            factories[st.name] = "@uow"
+        if isinstance(st, (ast.Import, ast.ImportFrom)):
+            module_env.update(imports([st]))
+        elif isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef)):
+            module_env[st.name] = "@uow" if is_uow(address(st.returns, module_env)) else ""
         elif isinstance(st, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
             for target in st.targets if isinstance(st, ast.Assign) else [st.target]:
                 module_env[key(target)] = ""
-    module_env.update(factories)
 
     def origin(expr, env):
         if isinstance(expr, ast.Call):
             name = address(expr.func, env)
             if is_uow(name) or name == "@uow": return "@uow"
             parts = name.split(".")
             source = root.joinpath(*parts[:-1]).with_suffix(".py")
             declaration = _parse(source) if source.is_file() else None
             if declaration:
                 target = next((st for st in declaration.body if isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef)) and st.name == parts[-1]), None)
@@ -854,20 +858,24 @@
         init = next((st for st in cls.body if isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef)) and st.name == "__init__"), None)
         if init:
             init_env = dict(module_env)
             params(init, init_env)
             # 생성자 직접 주입/별칭만 지원한다. 분기·helper는 확정하지 않는다.
             for st in init.body:
                 if isinstance(st, (ast.Assign, ast.AnnAssign)):
                     value = origin(st.value, init_env)
                     for target in st.targets if isinstance(st, ast.Assign) else [st.target]:
                         init_env[key(target)] = value
+                elif not isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
+                    for target in _function_nodes(st):
+                        if isinstance(target, (ast.Name, ast.Attribute)) and isinstance(target.ctx, (ast.Store, ast.Del)):
+                            init_env[key(target)] = ""
             env.update({k: v for k, v in init_env.items() if k.startswith("self.")})
     params(fn, env)
     regions = {0: set()}
     unknown = False
 
     def atomic(expr, local):
         target = expr.func if isinstance(expr, ast.Call) else expr
         return address(target, local) == "django.db.transaction.atomic"
 
     def scan(expr, local, region):

```

## dddjango/scripts/check-port-adapter-pairing.py

Before SHA256: 5e00306b107ac4876a3e0fb94048b85e9a9ace793dd96fc763c5b5a72bbb21cf
After SHA256: 682823f8599339f50fede9a9f23d6b0557b2c252a619885571970432ddabace4

```diff
--- before/dddjango/scripts/check-port-adapter-pairing.py
+++ after/dddjango/scripts/check-port-adapter-pairing.py
@@ -1206,26 +1206,35 @@
                     elif provenance != "@domain":
                         cand.add("#557", where, "code/errno/status_code 수신자 출처 불명 — 벤더 코드인지 계약 값인지 확인 필요", "이 값의 실제 선언과 정규화 소유자는 어디인가")
         for child in ast.iter_child_nodes(expr): inspect(child, env)
 
     def parameters(fn, env):
         for arg in (*fn.args.posonlyargs, *fn.args.args, *fn.args.kwonlyargs):
             env[arg.arg] = origin(address(arg.annotation, env))
         for arg in (fn.args.vararg, fn.args.kwarg):
             if arg: env[arg.arg] = ""
 
-    # 모듈의 사후 재바인딩도 함수 실행 시 출처를 바꾼다. 순서 의존 호출은 확정하지 않는다.
+    # 최초 정적 별칭은 보존한다. 이미 바인딩된 모듈 이름의 재대입은 함수에서 불명이다.
     rebound = set()
+    bound = set()
     for st in mod.body:
-        if isinstance(st, (ast.Assign, ast.AnnAssign, ast.AugAssign, ast.Delete)):
+        if isinstance(st, (ast.Import, ast.ImportFrom)):
+            names = set(imported(st, py))
+        elif isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
+            names = {st.name}
+        elif isinstance(st, (ast.Assign, ast.AnnAssign, ast.AugAssign, ast.Delete)):
             targets = st.targets if isinstance(st, (ast.Assign, ast.Delete)) else [st.target]
-            rebound.update(key(t) for t in targets)
+            names = {key(t) for t in targets}
+        else:
+            continue
+        rebound.update(names & bound)
+        bound.update(names)
 
     def block(body, env):
         for st in body:
             if isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef)):
                 local = dict(env)
                 for name in rebound: local[name] = ""
                 parameters(st, local)
                 block(st.body, local)
                 env[st.name] = ""
                 continue
@@ -1234,20 +1243,29 @@
                 fields = {}
                 init = next((n for n in st.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == "__init__"), None)
                 if init:
                     local = dict(env)
                     parameters(init, local)
                     for n in init.body:
                         if isinstance(n, (ast.Assign, ast.AnnAssign)):
                             value = value_origin(n.value, local)
                             for target in n.targets if isinstance(n, ast.Assign) else [n.target]:
                                 local[key(target)] = value
+                        else:
+                            pending = [n]
+                            while pending:
+                                target = pending.pop()
+                                if isinstance(target, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)):
+                                    continue
+                                if isinstance(target, (ast.Name, ast.Attribute)) and isinstance(target.ctx, (ast.Store, ast.Del)):
+                                    local[key(target)] = ""
+                                pending.extend(ast.iter_child_nodes(target))
                     fields = {k: v for k, v in local.items() if k.startswith("self.")}
                 block(st.body, dict(env, **fields))
                 env[st.name] = ".".join((*py.relative_to(root).with_suffix("").parts, st.name))
                 continue
             if isinstance(st, (ast.If, ast.For, ast.AsyncFor, ast.While, ast.Try, ast.With, ast.AsyncWith)):
                 branches = []
                 if isinstance(st, (ast.With, ast.AsyncWith)):
                     local = dict(env)
                     for item in st.items:
                         inspect(item.context_expr, env)

```

## codex-dddjango/skills/dddjango/scripts/check-port-adapter-pairing.py

Before SHA256: 5e00306b107ac4876a3e0fb94048b85e9a9ace793dd96fc763c5b5a72bbb21cf
After SHA256: 682823f8599339f50fede9a9f23d6b0557b2c252a619885571970432ddabace4

```diff
--- before/codex-dddjango/skills/dddjango/scripts/check-port-adapter-pairing.py
+++ after/codex-dddjango/skills/dddjango/scripts/check-port-adapter-pairing.py
@@ -1206,26 +1206,35 @@
                     elif provenance != "@domain":
                         cand.add("#557", where, "code/errno/status_code 수신자 출처 불명 — 벤더 코드인지 계약 값인지 확인 필요", "이 값의 실제 선언과 정규화 소유자는 어디인가")
         for child in ast.iter_child_nodes(expr): inspect(child, env)
 
     def parameters(fn, env):
         for arg in (*fn.args.posonlyargs, *fn.args.args, *fn.args.kwonlyargs):
             env[arg.arg] = origin(address(arg.annotation, env))
         for arg in (fn.args.vararg, fn.args.kwarg):
             if arg: env[arg.arg] = ""
 
-    # 모듈의 사후 재바인딩도 함수 실행 시 출처를 바꾼다. 순서 의존 호출은 확정하지 않는다.
+    # 최초 정적 별칭은 보존한다. 이미 바인딩된 모듈 이름의 재대입은 함수에서 불명이다.
     rebound = set()
+    bound = set()
     for st in mod.body:
-        if isinstance(st, (ast.Assign, ast.AnnAssign, ast.AugAssign, ast.Delete)):
+        if isinstance(st, (ast.Import, ast.ImportFrom)):
+            names = set(imported(st, py))
+        elif isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
+            names = {st.name}
+        elif isinstance(st, (ast.Assign, ast.AnnAssign, ast.AugAssign, ast.Delete)):
             targets = st.targets if isinstance(st, (ast.Assign, ast.Delete)) else [st.target]
-            rebound.update(key(t) for t in targets)
+            names = {key(t) for t in targets}
+        else:
+            continue
+        rebound.update(names & bound)
+        bound.update(names)
 
     def block(body, env):
         for st in body:
             if isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef)):
                 local = dict(env)
                 for name in rebound: local[name] = ""
                 parameters(st, local)
                 block(st.body, local)
                 env[st.name] = ""
                 continue
@@ -1234,20 +1243,29 @@
                 fields = {}
                 init = next((n for n in st.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == "__init__"), None)
                 if init:
                     local = dict(env)
                     parameters(init, local)
                     for n in init.body:
                         if isinstance(n, (ast.Assign, ast.AnnAssign)):
                             value = value_origin(n.value, local)
                             for target in n.targets if isinstance(n, ast.Assign) else [n.target]:
                                 local[key(target)] = value
+                        else:
+                            pending = [n]
+                            while pending:
+                                target = pending.pop()
+                                if isinstance(target, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)):
+                                    continue
+                                if isinstance(target, (ast.Name, ast.Attribute)) and isinstance(target.ctx, (ast.Store, ast.Del)):
+                                    local[key(target)] = ""
+                                pending.extend(ast.iter_child_nodes(target))
                     fields = {k: v for k, v in local.items() if k.startswith("self.")}
                 block(st.body, dict(env, **fields))
                 env[st.name] = ".".join((*py.relative_to(root).with_suffix("").parts, st.name))
                 continue
             if isinstance(st, (ast.If, ast.For, ast.AsyncFor, ast.While, ast.Try, ast.With, ast.AsyncWith)):
                 branches = []
                 if isinstance(st, (ast.With, ast.AsyncWith)):
                     local = dict(env)
                     for item in st.items:
                         inspect(item.context_expr, env)

```

## workspace/tools/field_report_checker_smoke.py

Before SHA256: 4b7f1bd5d068d7c0e23680b19e035a4c6cf13ca47d6a0998f93b7c1ff66dd9b7
After SHA256: de7bb136f1abd67b528f75c87c5715a6e980d33b19dc0362a12de62c03ff2de8

```diff
--- before/workspace/tools/field_report_checker_smoke.py
+++ after/workspace/tools/field_report_checker_smoke.py
@@ -297,20 +297,70 @@
         isolation._check_ohs_service(py, str(py), f, c)
         self.assertIn("#153", [e.rule for e in c.entries])
         self.assertIn("#153", self.ohs_rules("from application.lesson.application_layer.books.read.absent_use_case import Missing\ndef read_query(request: Missing): request.execute()\n")[1])
 
     def test_custom_enum_validation_does_not_prove_closed_members(self):
         self.assertIn("#268", self.enum_rules("from enum import Enum\nclass Kind(Enum):\n    ONE = 1\n    def __init__(self, value):\n        if value < 0: raise ValueError()\n")[1])
 
     def test_nested_repository_parameters_do_not_retype_outer_bindings(self):
         f, c = self.application_rules("with uow:\n        books.save(a)\n        loans.save(b)\n    def unused(books: LoanRepository): pass")
         self.assertIn("#546", f)
+
+    def test_while_guard_execute_repeats_but_for_iterable_executes_once(self):
+        header = "from application.lesson.composition_root.books import build_read_use_case as prepare\n"
+        for statement, candidate in [("while unit.execute(): pass", True),
+                                     ("for item in unit.execute(): pass", False)]:
+            with self.subTest(statement=statement):
+                _, c = self.ohs_rules(header + "def read_query(request):\n    unit = prepare()\n    " + statement + "\n")
+                self.assertEqual("#153" in c, candidate)
+
+    def test_later_import_shadow_invalidates_standard_enum_origin(self):
+        for header, base in [
+            ("from enum import Enum\nfrom custom import Enum", "Enum"),
+            ("import enum as standard\nimport custom as standard", "standard.Enum"),
+        ]:
+            with self.subTest(header=header):
+                self.assertIn("#268", self.enum_rules(header + f"\nclass Kind({base}):\n    ONE = 1\n")[1])
+
+    def test_rebound_annotated_factory_is_not_revived(self):
+        body = "with make():\n        books.save(a)\n    with make():\n        loans.save(b)"
+        f, c = self.application_rules(body, "def make() -> Work: return Work()\nmake = dynamic")
+        self.assertNotIn("#546", f)
+        self.assertIn("#546", c)
+
+    def test_constructor_branch_invalidates_uow_field_origin(self):
+        self.application_rules("pass")
+        source = "from application.lesson.application_layer.port.unit_of_work.lesson_unit_of_work import LessonUnitOfWork as Work\nclass Run:\n    def __init__(self, context: Work, books: BookRepository, loans: LoanRepository):\n        self.context = context\n        self.books = books\n        self.loans = loans\n        if flag: self.context = dynamic()\n    def execute(self):\n        with self.context:\n            self.books.save(a)\n        with self.context:\n            self.loans.save(b)\n"
+        self.write("application/lesson/application_layer/books/run/run_use_case.py", source)
+        f, c = domain.Findings(defer=True), domain.Candidates(defer=True)
+        domain._check_application_side(self.root, self.root / "application/lesson", f, c)
+        self.assertNotIn("#546", [e.rule for e in f.entries])
+        self.assertIn("#546", [e.rule for e in c.entries])
+
+    def test_constructor_branch_invalidates_contract_field_origin(self):
+        source = "from application.lesson.domain_layer.book.kind import Kind\nclass Run:\n    def __init__(self, value: Kind):\n        self.value = value\n        if flag: self.value = dynamic()\n    def execute(self): return self.value.code == 1\n"
+        f, c = self.property_rules(source)
+        self.assertNotIn("#557", f)
+        self.assertIn("#557", c)
+
+    def test_initial_static_module_alias_preserves_origin_but_rebinding_does_not(self):
+        for imported, comparison, expected in [
+            ("from requests import Response as Source", "value.status_code == 200", "violation"),
+            ("from application.lesson.domain_layer.book.kind import Kind as Source", "value.code == 1", None),
+        ]:
+            for suffix, wanted in [("", expected), ("Alias = dynamic\n", "candidate"),
+                                   ("if flag: Alias = dynamic\n", "candidate")]:
+                with self.subTest(imported=imported, suffix=suffix):
+                    source = imported + "\nAlias = Source\n" + suffix + "def run(value: Alias): return " + comparison + "\n"
+                    f, c = self.property_rules(source)
+                    self.assertEqual("#557" in f, wanted == "violation")
+                    self.assertEqual("#557" in c, wanted == "candidate")
 
     def admin_records(self, source):
         self.write("framework/admin/book.py", source)
         records = self.root / "findings.jsonl"
         records.unlink(missing_ok=True)
         run = subprocess.run([sys.executable, '-B', str(SCRIPTS / 'check-public-surface-annotation.py'),
                               str(self.root)], env=self.env, text=True, capture_output=True)
         self.assertIn(run.returncode, (0, 2), run.stdout + run.stderr)
         return [json.loads(line) for line in records.read_text().splitlines()] if records.exists() else []
 

```
