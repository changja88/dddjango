# task-2-fix1 review package

No commit was authorized. This package compares owned-file snapshots before this task with current bytes.

## dddjango/scripts/design_pregate.py

Before SHA256: 48f4445ed454d6b55a4a3a7793af57308e73c6eda13bc81379ac900f91dbceae
After SHA256: 05ed0358661e03cab1cec658c4e2bb5bdbe63fda2572aa8bc32646ace0a454ea

```diff
--- before/dddjango/scripts/design_pregate.py
+++ after/dddjango/scripts/design_pregate.py
@@ -1841,33 +1841,38 @@
             if entry.deferred_remove:
                 report["unsimulated"].append(f"후행 remove(@Ln — G1 승인 시점 상태 유지): {entry.path}")
             elif target.is_file():
                 target.unlink()
                 report["materialized"].append(f"removed {entry.path}")
             else:
                 report["unsimulated"].append(f"remove(실존 없음): {entry.path}")
         elif entry.tag == "update":
             updated: "bytes | None"
             detail: str
+            generated_identities: set[tuple[str, str]] = set()
             updated, detail = _render_service_update(copy, entry)
             if updated is not None:
                 prior_names = {node.name for node in ast.parse(target.read_bytes()).body
                                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
-                report["generated_methods"][entry.path] = [item for item in _generated_methods(ast.parse(updated))
-                    if not item["owner"] and item["method"] not in prior_names]
+                generated_identities = {(item["owner"], item["method"])
+                    for item in _generated_methods(ast.parse(updated))
+                    if not item["owner"] and item["method"] not in prior_names}
                 target.write_bytes(updated)
             marker_update, marker_detail = _render_marker_update(copy, entry)
             if marker_update is not None:
                 updated = marker_update
             detail += "; " + marker_detail
             if updated is not None:
                 target.write_bytes(updated)
+                if generated_identities:
+                    report["generated_methods"][entry.path] = [item for item in _generated_methods(ast.parse(updated))
+                        if (item["owner"], item["method"]) in generated_identities]
                 report["materialized"].append(entry.path)
             if entry.path in promoted:
                 report["unsimulated"].append(
                     f"S5 update(승격 형태 실존 — 예외 통과 · 파일 `<칸>.py` 는 기준선 부재 · 실존 채널은 ⑴ 판정; {detail}): {entry.path}")
             else:
                 report["unsimulated"].append(f"S5 update({detail}): {entry.path}")
     report["pruned_dirs"] = _prune_removed_parents(copy, plan)
     # 신규 BC 골격 전량 — add/empty가 있으며 앵커에 없던 BC만. remove로 전멸한 BC는 재생하지 않는다.
     new_bcs: "set[str]" = set()
     for entry in plan.entries.values():

```

## codex-dddjango/skills/dddjango/scripts/design_pregate.py

Before SHA256: 48f4445ed454d6b55a4a3a7793af57308e73c6eda13bc81379ac900f91dbceae
After SHA256: 05ed0358661e03cab1cec658c4e2bb5bdbe63fda2572aa8bc32646ace0a454ea

```diff
--- before/codex-dddjango/skills/dddjango/scripts/design_pregate.py
+++ after/codex-dddjango/skills/dddjango/scripts/design_pregate.py
@@ -1841,33 +1841,38 @@
             if entry.deferred_remove:
                 report["unsimulated"].append(f"후행 remove(@Ln — G1 승인 시점 상태 유지): {entry.path}")
             elif target.is_file():
                 target.unlink()
                 report["materialized"].append(f"removed {entry.path}")
             else:
                 report["unsimulated"].append(f"remove(실존 없음): {entry.path}")
         elif entry.tag == "update":
             updated: "bytes | None"
             detail: str
+            generated_identities: set[tuple[str, str]] = set()
             updated, detail = _render_service_update(copy, entry)
             if updated is not None:
                 prior_names = {node.name for node in ast.parse(target.read_bytes()).body
                                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
-                report["generated_methods"][entry.path] = [item for item in _generated_methods(ast.parse(updated))
-                    if not item["owner"] and item["method"] not in prior_names]
+                generated_identities = {(item["owner"], item["method"])
+                    for item in _generated_methods(ast.parse(updated))
+                    if not item["owner"] and item["method"] not in prior_names}
                 target.write_bytes(updated)
             marker_update, marker_detail = _render_marker_update(copy, entry)
             if marker_update is not None:
                 updated = marker_update
             detail += "; " + marker_detail
             if updated is not None:
                 target.write_bytes(updated)
+                if generated_identities:
+                    report["generated_methods"][entry.path] = [item for item in _generated_methods(ast.parse(updated))
+                        if (item["owner"], item["method"]) in generated_identities]
                 report["materialized"].append(entry.path)
             if entry.path in promoted:
                 report["unsimulated"].append(
                     f"S5 update(승격 형태 실존 — 예외 통과 · 파일 `<칸>.py` 는 기준선 부재 · 실존 채널은 ⑴ 판정; {detail}): {entry.path}")
             else:
                 report["unsimulated"].append(f"S5 update({detail}): {entry.path}")
     report["pruned_dirs"] = _prune_removed_parents(copy, plan)
     # 신규 BC 골격 전량 — add/empty가 있으며 앵커에 없던 BC만. remove로 전멸한 BC는 재생하지 않는다.
     new_bcs: "set[str]" = set()
     for entry in plan.entries.values():

```

## workspace/tools/pregate_field_report_smoke.py

Before SHA256: 762f87d073fa774035fe15eeaa4fdd9a17834ddd9e66a2585c82fa327f66b0e0
After SHA256: ceab87ff2c0bcbfb08d8604a34b75407dd89670efb43c5d4cbae8ef610418295

```diff
--- before/workspace/tools/pregate_field_report_smoke.py
+++ after/workspace/tools/pregate_field_report_smoke.py
@@ -496,20 +496,44 @@
         self.assertEqual([item['method'] for item in generated[SERVICE]], ['new_query'])
         new_node = next(node for node in ast.parse((self.copy / SERVICE).read_text()).body
                         if isinstance(node, ast.FunctionDef) and node.name == 'new_query')
         self.assertEqual(generated[SERVICE][0]['lineno'], new_node.lineno)
         self.assertEqual(generated[SERVICE][0]['end_lineno'], new_node.end_lineno)
         self.assertTrue((self.copy / SERVICE).read_bytes().startswith(ORIGINAL.encode()))
         self.write(self.source, path, 'class DjangoGardenUnitOfWork:\n'
                    '    def after_commit(self, callback):\n        raise NotImplementedError\n')
         _, report = self.materialize(spec_text([f'update {path}']))
         self.assertNotIn(path, report['generated_methods'])
+
+    def test_generated_ranges_follow_final_marker_composition(self):
+        originals = [ORIGINAL, ORIGINAL.replace('from decimal import Decimal\n',
+            'from decimal import Decimal\nimport pytest\npytestmark = [\n    pytest.mark.fast,\n]\n')]
+        for original in originals:
+            with self.subTest(original=original):
+                self.write(self.source, SERVICE, original)
+                text = spec_text([f'update {SERVICE}'], [f'{SERVICE}::new_query() -> str'],
+                                 owner=f'{SERVICE} [markers: slow]')
+                _, report = self.materialize(text)
+                final = (self.copy / SERVICE).read_text()
+                module = ast.parse(final)
+                generated = report['generated_methods'][SERVICE]
+                self.assertEqual([(item['owner'], item['method']) for item in generated], [('', 'new_query')])
+                new_query = next(node for node in module.body
+                                 if isinstance(node, ast.FunctionDef) and node.name == 'new_query')
+                self.assertEqual((generated[0]['lineno'], generated[0]['end_lineno']),
+                                 (new_query.lineno, new_query.end_lineno))
+                self.assertIn('pytestmark = [pytest.mark.slow]', final)
+                old_query = next(node for node in module.body
+                                 if isinstance(node, ast.FunctionDef) and node.name == 'old_query')
+                self.assertEqual(ast.get_source_segment(final, old_query),
+                                 'def old_query() -> str:\n    return "unchanged"')
+                self.assertEqual((self.source / SERVICE).read_text(), original)
 
     def test_generated_partition_uses_full_normalized_cohort_and_all_raw_locations(self):
         path = 'application/orders/driven_layer/adapter/persistence/unit_of_work/order_unit_of_work.py'
         message = 'after_commit 구현이 transaction.on_commit 으로 채워지지 않았다'
         line = f'check-port-adapter-pairing.py :: [#376] {path}:N: {message}'
         records = [dict(checker='check-port-adapter-pairing.py', rule='#376', severity='error',
                         file=f'{path}:{n}', message=message) for n in (5, 15)]
         generated = {path: [dict(owner='First', method='after_commit', lineno=5, end_lineno=6),
                             dict(owner='Second', method='after_commit', lineno=15, end_lineno=16)]}
         def gate(rows, unmatched=(), lines=None):

```

## workspace/tools/pregate_fixture_run.py

Before SHA256: 29a1aa46ea7a8979c04230fc8afb2adc31745eecde2b059abd7edb3578e43539
After SHA256: 29a1aa46ea7a8979c04230fc8afb2adc31745eecde2b059abd7edb3578e43539

```diff

```
