# Task 1 fix round 1 scoped review package

No commits. Baseline is task-1-fix1-before snapshots. Review M1/M2 repairs and newly introduced defects only.

## dddjango/scripts/design_pregate.py

Before SHA256: 48530e08a5a532e1210513234c8560609249190381a618f5bd4d6968fcaea71d
After SHA256: 377645c3a4d1de37b1be8243e06d4754d34a92d327317929c412fdb6eec8f723

```diff
--- before/dddjango/scripts/design_pregate.py
+++ after/dddjango/scripts/design_pregate.py
@@ -1388,50 +1388,60 @@
     except (OSError, UnicodeError, SyntaxError) as exc:
         return None, f"marker 기존 파일 파싱 불가: {exc}"
     bindings, open_surface = _update_bindings(module)
     if open_surface:
         return None, "marker 동적/star/class global 표면"
     pytest_aliases = {name for name, origins in bindings.items() if origins == {"import pytest"}}
     mark_aliases = {name for name, origins in bindings.items() if origins == {"from pytest import mark"}}
     if "pytest" in bindings and "pytest" not in pytest_aliases:
         return None, "pytest 이름 재바인딩/충돌"
     stores: list[ast.AST] = []
+    mutations: list[ast.Subscript] = []
     def visit(node: ast.AST) -> None:
         if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
             if node.name == "pytestmark":
                 stores.append(node)
             return
         if isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Del)) and node.id == "pytestmark":
             stores.append(node)
+        if isinstance(node, ast.Subscript) and isinstance(node.ctx, (ast.Store, ast.Del)):
+            root: ast.expr = node.value
+            while isinstance(root, (ast.Subscript, ast.Attribute)):
+                root = root.value
+            if isinstance(root, ast.Name) and root.id == "pytestmark":
+                mutations.append(node)
         for child in ast.iter_child_nodes(node):
             visit(child)
     visit(module)
+    if mutations:
+        return None, "module pytestmark subscript mutation — 최종 목록 미해소"
     assignments = [node for node in module.body if
         isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name)
         and node.targets[0].id == "pytestmark" or isinstance(node, ast.AnnAssign)
         and isinstance(node.target, ast.Name) and node.target.id == "pytestmark"]
     if "pytestmark" in bindings and bindings["pytestmark"] != {""}:
         return None, "module pytestmark import 바인딩 충돌"
     if stores and (len(stores) != 1 or len(assignments) != 1):
         return None, "module pytestmark 중복/동적/조건부 대입"
     def simple(node: ast.AST | None) -> bool:
         if isinstance(node, (ast.List, ast.Tuple)):
             return all(simple(item) for item in node.elts)
         if not isinstance(node, ast.Attribute):
             return False
         mark = node.value
         return (isinstance(mark, ast.Attribute) and mark.attr == "mark" and isinstance(mark.value, ast.Name)
                 and mark.value.id in pytest_aliases or isinstance(mark, ast.Name) and mark.id in mark_aliases)
     if assignments and not simple(assignments[0].value):
         return None, "module pytestmark 호출/동적 표현 — 전사 미지원"
     statement = "pytestmark = [" + ", ".join("pytest.mark." + name for name in entry.signals.markers) + "]"
-    import_needed = bool(entry.signals.markers) and "pytest" not in pytest_aliases
+    # 새 목록은 기존 일반 import 앞에 삽입되므로 그 위치에서 쓸 pytest binding을 함께 만든다.
+    import_needed = bool(entry.signals.markers) and ("pytest" not in pytest_aliases or not assignments)
     lines = original.splitlines(keepends=True)
     def offset(line: int, column: int = 0) -> int:
         return sum(len(part) for part in lines[:line - 1]) + column
     changed = original
     if assignments:
         node = assignments[0]
         start, end = offset(node.lineno, node.col_offset), offset(node.end_lineno, node.end_col_offset)
         changed = original[:start] + statement.encode("utf-8") + original[end:]
     # Insert imports/list after module docstring and future statements, preserving every other byte.
     prefix_nodes = []

```

## codex-dddjango/skills/dddjango/scripts/design_pregate.py

Before SHA256: 48530e08a5a532e1210513234c8560609249190381a618f5bd4d6968fcaea71d
After SHA256: 377645c3a4d1de37b1be8243e06d4754d34a92d327317929c412fdb6eec8f723

```diff
--- before/codex-dddjango/skills/dddjango/scripts/design_pregate.py
+++ after/codex-dddjango/skills/dddjango/scripts/design_pregate.py
@@ -1388,50 +1388,60 @@
     except (OSError, UnicodeError, SyntaxError) as exc:
         return None, f"marker 기존 파일 파싱 불가: {exc}"
     bindings, open_surface = _update_bindings(module)
     if open_surface:
         return None, "marker 동적/star/class global 표면"
     pytest_aliases = {name for name, origins in bindings.items() if origins == {"import pytest"}}
     mark_aliases = {name for name, origins in bindings.items() if origins == {"from pytest import mark"}}
     if "pytest" in bindings and "pytest" not in pytest_aliases:
         return None, "pytest 이름 재바인딩/충돌"
     stores: list[ast.AST] = []
+    mutations: list[ast.Subscript] = []
     def visit(node: ast.AST) -> None:
         if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
             if node.name == "pytestmark":
                 stores.append(node)
             return
         if isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Del)) and node.id == "pytestmark":
             stores.append(node)
+        if isinstance(node, ast.Subscript) and isinstance(node.ctx, (ast.Store, ast.Del)):
+            root: ast.expr = node.value
+            while isinstance(root, (ast.Subscript, ast.Attribute)):
+                root = root.value
+            if isinstance(root, ast.Name) and root.id == "pytestmark":
+                mutations.append(node)
         for child in ast.iter_child_nodes(node):
             visit(child)
     visit(module)
+    if mutations:
+        return None, "module pytestmark subscript mutation — 최종 목록 미해소"
     assignments = [node for node in module.body if
         isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name)
         and node.targets[0].id == "pytestmark" or isinstance(node, ast.AnnAssign)
         and isinstance(node.target, ast.Name) and node.target.id == "pytestmark"]
     if "pytestmark" in bindings and bindings["pytestmark"] != {""}:
         return None, "module pytestmark import 바인딩 충돌"
     if stores and (len(stores) != 1 or len(assignments) != 1):
         return None, "module pytestmark 중복/동적/조건부 대입"
     def simple(node: ast.AST | None) -> bool:
         if isinstance(node, (ast.List, ast.Tuple)):
             return all(simple(item) for item in node.elts)
         if not isinstance(node, ast.Attribute):
             return False
         mark = node.value
         return (isinstance(mark, ast.Attribute) and mark.attr == "mark" and isinstance(mark.value, ast.Name)
                 and mark.value.id in pytest_aliases or isinstance(mark, ast.Name) and mark.id in mark_aliases)
     if assignments and not simple(assignments[0].value):
         return None, "module pytestmark 호출/동적 표현 — 전사 미지원"
     statement = "pytestmark = [" + ", ".join("pytest.mark." + name for name in entry.signals.markers) + "]"
-    import_needed = bool(entry.signals.markers) and "pytest" not in pytest_aliases
+    # 새 목록은 기존 일반 import 앞에 삽입되므로 그 위치에서 쓸 pytest binding을 함께 만든다.
+    import_needed = bool(entry.signals.markers) and ("pytest" not in pytest_aliases or not assignments)
     lines = original.splitlines(keepends=True)
     def offset(line: int, column: int = 0) -> int:
         return sum(len(part) for part in lines[:line - 1]) + column
     changed = original
     if assignments:
         node = assignments[0]
         start, end = offset(node.lineno, node.col_offset), offset(node.end_lineno, node.end_col_offset)
         changed = original[:start] + statement.encode("utf-8") + original[end:]
     # Insert imports/list after module docstring and future statements, preserving every other byte.
     prefix_nodes = []

```

## workspace/tools/pregate_field_report_smoke.py

Before SHA256: bc62b670fa7dfe4b88444d8ee63a2bd8b56bf6b8953d05dc5493f5805f084a69
After SHA256: 58372ea10464d45a2af681b8284b4c343c553746b15411c982eac454b3fa8b29

```diff
--- before/workspace/tools/pregate_field_report_smoke.py
+++ after/workspace/tools/pregate_field_report_smoke.py
@@ -523,13 +523,58 @@
             ('list[Book]', [f'{result}::alias list = Mapping'], [], [('#202', False)]),
             ('LiteralName["Book"]', [], [f'{result}  from typing import Literal as LiteralName'], []),
             ('Mapping[str, Book]', [], [f'{result}  from typing import Mapping'], [('#202', True)]),
             ('Mapping[str, Book]', [], [], [('#202', False)])]:
             with self.subTest(annotation=annotation, imports=imports):
                 plan, errors = pg.parse_spec(spec_text([f'update {result}'], [*symbols,
                     f'{result}::ListBooksResult {{value: {annotation}}}'], [domain_import, *imports]))
                 self.assertEqual(errors, [])
                 self.assertEqual([(f.rule, f.confirmed) for f in pg.check_declarations(plan, self.source)], expected)
 
+    def test_marker_new_list_evaluates_after_pytest_binding(self):
+        from types import ModuleType, SimpleNamespace
+        from unittest.mock import patch
+        fake_pytest = ModuleType('pytest')
+        fake_pytest.mark = SimpleNamespace(slow='slow', django_db='django_db')
+        for prefix in ['', '"""기존 문서."""\nfrom __future__ import annotations\n']:
+            with self.subTest(prefix=prefix):
+                original = prefix + 'import pytest\ndef test_case():\n    return "original body"\n'
+                self.write(self.source, TEST, original)
+                _, report = self.materialize(spec_text([f'update {TEST}'], owner=f'{TEST} [markers: slow]'))
+                updated = (self.copy / TEST).read_text()
+                namespace = {}
+                with patch.dict(sys.modules, {'pytest': fake_pytest}):
+                    exec(compile(updated, TEST, 'exec'), namespace)
+                self.assertEqual(namespace['pytestmark'], ['slow'])
+                self.assertEqual(namespace['test_case'](), 'original body')
+                self.assertIn('import pytest\ndef test_case():\n    return "original body"\n', updated)
+                self.assertTrue(updated.startswith(prefix))
+                self.assertEqual((self.source / TEST).read_bytes(), original.encode())
+                self.assertEqual(report['materialized'], [TEST])
+
+    def test_marker_subscript_mutations_remain_s5_without_writes(self):
+        from types import ModuleType, SimpleNamespace
+        from unittest.mock import patch
+        fake_pytest = ModuleType('pytest')
+        fake_pytest.mark = SimpleNamespace(slow='slow', django_db='django_db')
+        for mutation in ['pytestmark[0] = pytest.mark.django_db', 'del pytestmark[0]',
+                         'pytestmark[:] = [pytest.mark.django_db]',
+                         'pytestmark[0] += pytest.mark.django_db',
+                         'if True:\n    pytestmark[0] = pytest.mark.django_db']:
+            for markers in ['', 'slow']:
+                with self.subTest(mutation=mutation, markers=markers):
+                    original = 'import pytest\npytestmark = [pytest.mark.slow]\n' + mutation + '\n'
+                    self.write(self.source, TEST, original)
+                    namespace = {}
+                    with patch.dict(sys.modules, {'pytest': fake_pytest}):
+                        exec(compile(original, TEST, 'exec'), namespace)
+                    if mutation == 'pytestmark[0] = pytest.mark.django_db':
+                        self.assertEqual(namespace['pytestmark'], ['django_db'])
+                    _, report = self.materialize(spec_text([f'update {TEST}'], owner=f'{TEST} [markers: {markers}]'))
+                    self.assertEqual((self.copy / TEST).read_bytes(), original.encode())
+                    self.assertEqual((self.source / TEST).read_bytes(), original.encode())
+                    self.assertEqual(report['materialized'], [])
+                    self.assertTrue(any('S5' in note and 'subscript' in note for note in report['unsimulated']), report)
+
 
 if __name__ == "__main__":
     unittest.main(verbosity=2)

```
