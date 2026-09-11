# task-5-fix1 review package

No commit was authorized. This package compares owned-file snapshots before this task with current bytes.

## dddjango/scripts/checker_target.py

Before SHA256: 2efb7adbe792ddf4fadc9527699bb130ef1953481acdff70ad01e469ebdd0112
After SHA256: 2efb7adbe792ddf4fadc9527699bb130ef1953481acdff70ad01e469ebdd0112

```diff

```

## codex-dddjango/skills/dddjango/scripts/checker_target.py

Before SHA256: 2efb7adbe792ddf4fadc9527699bb130ef1953481acdff70ad01e469ebdd0112
After SHA256: 2efb7adbe792ddf4fadc9527699bb130ef1953481acdff70ad01e469ebdd0112

```diff

```

## dddjango/scripts/check-layer-skeleton.py

Before SHA256: 9f2ea08ec409ed8e52340067685b3a828235b68d35347903cf09492f5355a645
After SHA256: 9f2ea08ec409ed8e52340067685b3a828235b68d35347903cf09492f5355a645

```diff

```

## codex-dddjango/skills/dddjango/scripts/check-layer-skeleton.py

Before SHA256: 9f2ea08ec409ed8e52340067685b3a828235b68d35347903cf09492f5355a645
After SHA256: 9f2ea08ec409ed8e52340067685b3a828235b68d35347903cf09492f5355a645

```diff

```

## dddjango/scripts/check-port-adapter-pairing.py

Before SHA256: b6bcf57161a163e072fd9fb18a47bd11f1122ef2792ffc0d1f48a1cc215c522a
After SHA256: b6bcf57161a163e072fd9fb18a47bd11f1122ef2792ffc0d1f48a1cc215c522a

```diff

```

## codex-dddjango/skills/dddjango/scripts/check-port-adapter-pairing.py

Before SHA256: b6bcf57161a163e072fd9fb18a47bd11f1122ef2792ffc0d1f48a1cc215c522a
After SHA256: b6bcf57161a163e072fd9fb18a47bd11f1122ef2792ffc0d1f48a1cc215c522a

```diff

```

## dddjango/scripts/check-domain-model.py

Before SHA256: d789b50b2fa78caa5ae73892e042d5a721ca2b5e85459233c9ea92bd354527cc
After SHA256: 0bdf4f1212c535d83dc634ff34f0ea9d482cefb70144e6da2266870c4dd7586d

```diff
--- before/dddjango/scripts/check-domain-model.py
+++ after/dddjango/scripts/check-domain-model.py
@@ -1063,22 +1063,24 @@
                 has_coll = any(
                     isinstance(n, ast.AnnAssign) and _ann_names(n.annotation) & {"list", "List", "Sequence"}
                     for n in ast.walk(mod)) if mod else False
                 if has_coll:
                     cand.add("#547", _rel(root, root_py),
                              f"엔티티 {len(ents)}개 + 무제한 컬렉션 필드 — 루트가 비대하다",
                              "이 둘이 «동시에» 일어나면 업무가 정말 막아야 하나")
     # #565 후보 — 도메인 Enum 값 ∩ 유스케이스·서비스 이름.
     uc_names: set[str] = set()
     for area in app.iterdir() if app.is_dir() else []:
-        if area.is_dir() and area.name not in ("port", "__pycache__"):
-            uc_names |= {d.name for d in area.iterdir() if d.is_dir()}
+        if area.is_dir() and area.name not in ("port", "__pycache__") \
+                and not checker_target.cache_only_instance(area):
+            uc_names |= {d.name for d in area.iterdir() if d.is_dir() and d.name != "__pycache__"
+                         and not checker_target.cache_only_instance(d)}
     if domain.is_dir() and uc_names:
         for py in _py_files(domain):
             mod = _parse(py)
             for cls in [n for n in ast.walk(mod) if isinstance(n, ast.ClassDef)] if mod else []:
                 bases = {b.id if isinstance(b, ast.Name) else getattr(b, "attr", "") for b in cls.bases}
                 if not bases & {"Enum", "StrEnum", "IntEnum", "TextChoices", "Choices"}:
                     continue
                 for st in cls.body:
                     if isinstance(st, ast.Assign) and isinstance(st.value, ast.Constant) \
                             and isinstance(st.value.value, str) and st.value.value in uc_names:

```

## codex-dddjango/skills/dddjango/scripts/check-domain-model.py

Before SHA256: d789b50b2fa78caa5ae73892e042d5a721ca2b5e85459233c9ea92bd354527cc
After SHA256: 0bdf4f1212c535d83dc634ff34f0ea9d482cefb70144e6da2266870c4dd7586d

```diff
--- before/codex-dddjango/skills/dddjango/scripts/check-domain-model.py
+++ after/codex-dddjango/skills/dddjango/scripts/check-domain-model.py
@@ -1063,22 +1063,24 @@
                 has_coll = any(
                     isinstance(n, ast.AnnAssign) and _ann_names(n.annotation) & {"list", "List", "Sequence"}
                     for n in ast.walk(mod)) if mod else False
                 if has_coll:
                     cand.add("#547", _rel(root, root_py),
                              f"엔티티 {len(ents)}개 + 무제한 컬렉션 필드 — 루트가 비대하다",
                              "이 둘이 «동시에» 일어나면 업무가 정말 막아야 하나")
     # #565 후보 — 도메인 Enum 값 ∩ 유스케이스·서비스 이름.
     uc_names: set[str] = set()
     for area in app.iterdir() if app.is_dir() else []:
-        if area.is_dir() and area.name not in ("port", "__pycache__"):
-            uc_names |= {d.name for d in area.iterdir() if d.is_dir()}
+        if area.is_dir() and area.name not in ("port", "__pycache__") \
+                and not checker_target.cache_only_instance(area):
+            uc_names |= {d.name for d in area.iterdir() if d.is_dir() and d.name != "__pycache__"
+                         and not checker_target.cache_only_instance(d)}
     if domain.is_dir() and uc_names:
         for py in _py_files(domain):
             mod = _parse(py)
             for cls in [n for n in ast.walk(mod) if isinstance(n, ast.ClassDef)] if mod else []:
                 bases = {b.id if isinstance(b, ast.Name) else getattr(b, "attr", "") for b in cls.bases}
                 if not bases & {"Enum", "StrEnum", "IntEnum", "TextChoices", "Choices"}:
                     continue
                 for st in cls.body:
                     if isinstance(st, ast.Assign) and isinstance(st.value, ast.Constant) \
                             and isinstance(st.value.value, str) and st.value.value in uc_names:

```

## dddjango/scripts/check-usecase-dto-placement.py

Before SHA256: dc80a76963f3dd912ef9696173312be2ad0a7612f0006b725bdbff1148a0455b
After SHA256: 4a51b80b722d516c3d94423bb2cdec832a7c4cf7c0be3102b882a9ddbbe7bbb7

```diff
--- before/dddjango/scripts/check-usecase-dto-placement.py
+++ after/dddjango/scripts/check-usecase-dto-placement.py
@@ -275,29 +275,37 @@
 
 
 def _check_structure(root: Path, bc: Path, bc_rel: Path, out: Findings) -> list[Path]:
     """구조 규칙 검사 후 <use_case>/ 폴더 목록을 돌려준다."""
     app = _app_layer(bc)
     if app is None:
         return []
     rel = bc_rel / app.name
     dirs, _ = _entries(app)
     areas: list[Path] = []
+    cache_instances: set[Path] = set()
     for p in dirs:
-        if p.name == "port" or checker_target.cache_only_instance(p):
-            continue
+        if p.name == "port":
+            continue
+        if checker_target.cache_only_instance(p):
+            cache_instances.add(p)
+            continue
+        instance_dirs, _ = _entries(p)
+        cache_instances.update(child for child in instance_dirs if checker_target.cache_only_instance(child))
         if p.name in KIND_FOLDER_NAMES:
             out.add("#182", rel / p.name, "`application_layer/` 직계는 `<area>/`·`port/` 둘뿐이다 — 종류 폴더는 자리가 없다(`domain_bypass_query/`·`unit_of_work/` 는 `port/` 안이다)")
         else:
             areas.append(p)
 
     for p in app.rglob("*"):
+        if p in cache_instances or any(parent in cache_instances for parent in p.parents):
+            continue
         if set(p.relative_to(app).parts) & SKIP_DIRS:
             continue
         if p.is_dir() and p.name in ("validation", "validators"):
             out.add("#183", rel / p.relative_to(app), "`application_layer/` 아래에 `validation/` 폴더를 두지 않는다 — 검사 자리는 입구(schema_in)와 도메인 둘뿐이다")
         elif p.is_file() and p.name.endswith("_validation.py"):
             out.add("#183", rel / p.relative_to(app), "`*_validation.py` 를 두지 않는다 — 검사 자리는 입구(schema_in)와 도메인 둘뿐이다")
 
     api = _driving_api(bc)
     if api is not None and _has_concrete_api_surface(root, api, bc.name):
         api_dirs, _ = _entries(api)
@@ -664,21 +672,22 @@
     findings = Findings(defer=True)
     cand = Candidates(defer=True)
     scanned_layers = 0
     for bc in bcs:
         bc_rel = bc.relative_to(target)
         app = _app_layer(bc)
         agg_names: set[str] = set()
         dl = bc / "domain_layer"
         if dl.is_dir():
             agg_dirs, _ = _entries(dl)
-            agg_names = {p.name for p in agg_dirs if p.name not in ("shared_value_object", "domain_service")}
+            agg_names = {p.name for p in agg_dirs if p.name not in ("shared_value_object", "domain_service")
+                         and not checker_target.cache_only_instance(p)}
 
         if app is not None:
             scanned_layers += 1
             ucs = _check_structure(target, bc, bc_rel, findings)
             for uc in ucs:
                 uc_rel = bc_rel / "application_layer" / uc.parent.name / uc.name
                 _check_use_case(uc, uc_rel, agg_names, findings, cand)
                 for suffix in ("_command.py", "_query.py", "_result.py"):
                     f = uc / f"{uc.name}{suffix}"
                     if f.is_file():

```

## codex-dddjango/skills/dddjango/scripts/check-usecase-dto-placement.py

Before SHA256: dc80a76963f3dd912ef9696173312be2ad0a7612f0006b725bdbff1148a0455b
After SHA256: 4a51b80b722d516c3d94423bb2cdec832a7c4cf7c0be3102b882a9ddbbe7bbb7

```diff
--- before/codex-dddjango/skills/dddjango/scripts/check-usecase-dto-placement.py
+++ after/codex-dddjango/skills/dddjango/scripts/check-usecase-dto-placement.py
@@ -275,29 +275,37 @@
 
 
 def _check_structure(root: Path, bc: Path, bc_rel: Path, out: Findings) -> list[Path]:
     """구조 규칙 검사 후 <use_case>/ 폴더 목록을 돌려준다."""
     app = _app_layer(bc)
     if app is None:
         return []
     rel = bc_rel / app.name
     dirs, _ = _entries(app)
     areas: list[Path] = []
+    cache_instances: set[Path] = set()
     for p in dirs:
-        if p.name == "port" or checker_target.cache_only_instance(p):
-            continue
+        if p.name == "port":
+            continue
+        if checker_target.cache_only_instance(p):
+            cache_instances.add(p)
+            continue
+        instance_dirs, _ = _entries(p)
+        cache_instances.update(child for child in instance_dirs if checker_target.cache_only_instance(child))
         if p.name in KIND_FOLDER_NAMES:
             out.add("#182", rel / p.name, "`application_layer/` 직계는 `<area>/`·`port/` 둘뿐이다 — 종류 폴더는 자리가 없다(`domain_bypass_query/`·`unit_of_work/` 는 `port/` 안이다)")
         else:
             areas.append(p)
 
     for p in app.rglob("*"):
+        if p in cache_instances or any(parent in cache_instances for parent in p.parents):
+            continue
         if set(p.relative_to(app).parts) & SKIP_DIRS:
             continue
         if p.is_dir() and p.name in ("validation", "validators"):
             out.add("#183", rel / p.relative_to(app), "`application_layer/` 아래에 `validation/` 폴더를 두지 않는다 — 검사 자리는 입구(schema_in)와 도메인 둘뿐이다")
         elif p.is_file() and p.name.endswith("_validation.py"):
             out.add("#183", rel / p.relative_to(app), "`*_validation.py` 를 두지 않는다 — 검사 자리는 입구(schema_in)와 도메인 둘뿐이다")
 
     api = _driving_api(bc)
     if api is not None and _has_concrete_api_surface(root, api, bc.name):
         api_dirs, _ = _entries(api)
@@ -664,21 +672,22 @@
     findings = Findings(defer=True)
     cand = Candidates(defer=True)
     scanned_layers = 0
     for bc in bcs:
         bc_rel = bc.relative_to(target)
         app = _app_layer(bc)
         agg_names: set[str] = set()
         dl = bc / "domain_layer"
         if dl.is_dir():
             agg_dirs, _ = _entries(dl)
-            agg_names = {p.name for p in agg_dirs if p.name not in ("shared_value_object", "domain_service")}
+            agg_names = {p.name for p in agg_dirs if p.name not in ("shared_value_object", "domain_service")
+                         and not checker_target.cache_only_instance(p)}
 
         if app is not None:
             scanned_layers += 1
             ucs = _check_structure(target, bc, bc_rel, findings)
             for uc in ucs:
                 uc_rel = bc_rel / "application_layer" / uc.parent.name / uc.name
                 _check_use_case(uc, uc_rel, agg_names, findings, cand)
                 for suffix in ("_command.py", "_query.py", "_result.py"):
                     f = uc / f"{uc.name}{suffix}"
                     if f.is_file():

```

## dddjango/scripts/check-context-isolation.py

Before SHA256: 8c9afbf7931975c16a023152865c3a8246e7beece36217cc4e98383437dbfc4d
After SHA256: c87498928cc0f23103c8b3b35a6b2d7f01b2dbc3825021ae1ca9e371d5256e0e

```diff
--- before/dddjango/scripts/check-context-isolation.py
+++ after/dddjango/scripts/check-context-isolation.py
@@ -1276,21 +1276,22 @@
     findings = Findings(defer=True)
     cand = Candidates(defer=True)
     acl_partners: dict[str, set[str]] = {}
 
     for bc in bcs:
         bc_rel = bc.relative_to(target)
         dl = bc / "domain_layer"
         agg_names: set[str] = set()
         if dl.is_dir():
             agg_dirs, _ = _entries(dl)
-            agg_names = {p.name for p in agg_dirs if p.name not in ("shared_value_object", "domain_service")}
+            agg_names = {p.name for p in agg_dirs if p.name not in ("shared_value_object", "domain_service")
+                         and not checker_target.cache_only_instance(p)}
 
         for f in sorted(bc.rglob("*.py")):
             if set(f.relative_to(bc).parts) & SKIP_DIRS:
                 continue
             _scan_imports(f, bc, bc_rel, all_bcs, findings)
 
         ohs = bc / "driving_layer" / "open_host_service"
         if ohs.is_dir():
             _check_ohs(ohs, bc, bc_rel, agg_names, all_bcs, findings, cand)
 

```

## codex-dddjango/skills/dddjango/scripts/check-context-isolation.py

Before SHA256: 8c9afbf7931975c16a023152865c3a8246e7beece36217cc4e98383437dbfc4d
After SHA256: c87498928cc0f23103c8b3b35a6b2d7f01b2dbc3825021ae1ca9e371d5256e0e

```diff
--- before/codex-dddjango/skills/dddjango/scripts/check-context-isolation.py
+++ after/codex-dddjango/skills/dddjango/scripts/check-context-isolation.py
@@ -1276,21 +1276,22 @@
     findings = Findings(defer=True)
     cand = Candidates(defer=True)
     acl_partners: dict[str, set[str]] = {}
 
     for bc in bcs:
         bc_rel = bc.relative_to(target)
         dl = bc / "domain_layer"
         agg_names: set[str] = set()
         if dl.is_dir():
             agg_dirs, _ = _entries(dl)
-            agg_names = {p.name for p in agg_dirs if p.name not in ("shared_value_object", "domain_service")}
+            agg_names = {p.name for p in agg_dirs if p.name not in ("shared_value_object", "domain_service")
+                         and not checker_target.cache_only_instance(p)}
 
         for f in sorted(bc.rglob("*.py")):
             if set(f.relative_to(bc).parts) & SKIP_DIRS:
                 continue
             _scan_imports(f, bc, bc_rel, all_bcs, findings)
 
         ohs = bc / "driving_layer" / "open_host_service"
         if ohs.is_dir():
             _check_ohs(ohs, bc, bc_rel, agg_names, all_bcs, findings, cand)
 

```

## dddjango/scripts/registry_gate.py

Before SHA256: bcc7db98fe1f209f330d6c2ffb92239792580207f0d4bad317d6130fa60d273a
After SHA256: bcc7db98fe1f209f330d6c2ffb92239792580207f0d4bad317d6130fa60d273a

```diff

```

## codex-dddjango/skills/dddjango/scripts/registry_gate.py

Before SHA256: bcc7db98fe1f209f330d6c2ffb92239792580207f0d4bad317d6130fa60d273a
After SHA256: bcc7db98fe1f209f330d6c2ffb92239792580207f0d4bad317d6130fa60d273a

```diff

```

## workspace/tools/field_report_checker_smoke.py

Before SHA256: f17cb80d86db51f5e6122d72a4364651648189933b576b285cc21ecceab79cb6
After SHA256: 37a22b3cb4d5148b4da32c2d483264c9acb6b83f79702753c7e076f830e988ee

```diff
--- before/workspace/tools/field_report_checker_smoke.py
+++ after/workspace/tools/field_report_checker_smoke.py
@@ -718,20 +718,83 @@
                         self.assertEqual(any(rule in line for line in hits), extra is not None, output)
                     if extra:
                         (path / extra).unlink()
             shutil.rmtree(path)
             path.mkdir()
             output = self.run_checker(script)
             for rule in rules:
                 self.assertTrue(any(rule in line and "vanished" in line for line in output.splitlines()), output)
             shutil.rmtree(path)
 
+    def direct_and_snapshot_results(self, script):
+        gate = _load_module(SCRIPTS / "registry_gate.py", "field_cache_snapshot")
+        with tempfile.TemporaryDirectory(prefix="field-cache-copy-") as temp:
+            snapshot = Path(temp) / "snapshot"
+            gate._snapshot_current(self.root, snapshot)
+            results = []
+            for target in (self.root, snapshot):
+                result = subprocess.run([sys.executable, "-B", str(SCRIPTS / script), str(target)],
+                                        capture_output=True, text=True, env=self.env)
+                results.append((result.returncode, result.stdout + result.stderr))
+            return results
+
+    def test_validation_scan_respects_owning_cache_only_area_and_usecase(self):
+        for relative in ("order/vanished", "vanished_area/vanished"):
+            for banned in ("validation", "validators"):
+                path = self.plant("application/orders/application_layer/" + relative)
+                (path / banned).mkdir()
+                for source in (None, "__init__.py", "real.py"):
+                    with self.subTest(instance=relative, banned=banned, source=source):
+                        if source:
+                            (path / source).write_text("pass\n" if source == "real.py" else "")
+                        results = self.direct_and_snapshot_results("check-usecase-dto-placement.py")
+                        for channel, (code, output) in zip(("direct", "snapshot"), results):
+                            with self.subTest(channel=channel):
+                                self.assertEqual(code, 2 if source else 0, output)
+                                self.assertEqual(any("#183" in line and banned in line for line in output.splitlines()),
+                                                 source is not None, output)
+                        if source:
+                            (path / source).unlink()
+                shutil.rmtree(path)
+                if relative.startswith("vanished_area"):
+                    shutil.rmtree(path.parent)
+
+    def test_cache_only_names_do_not_change_real_usecase_service_or_enum_candidates(self):
+        cases = (
+            ("domain_layer/place_order", "check-usecase-dto-placement.py", "#191"),
+            ("domain_layer/order_lookup", "check-context-isolation.py", "#151"),
+            ("application_layer/order/vanished", "check-domain-model.py", "#565"),
+            ("application_layer/vanished_area/vanished", "check-domain-model.py", "#565"),
+        )
+        enum = self.root / "application/orders/domain_layer/order/value_object/workflow.py"
+        enum.write_text("from enum import Enum\nclass Workflow(Enum):\n    VANISHED = 'vanished'\n")
+        for relative, script, rule in cases:
+            path = self.plant("application/orders/" + relative)
+            for source in (None, "__init__.py", "real.py", "empty_instance"):
+                with self.subTest(instance=relative, source=source, rule=rule):
+                    if source == "empty_instance":
+                        shutil.rmtree(path)
+                        path.mkdir()
+                    elif source:
+                        (path / source).write_text("pass\n" if source == "real.py" else "")
+                    results = self.direct_and_snapshot_results(script)
+                    for channel, (code, output) in zip(("direct", "snapshot"), results):
+                        with self.subTest(channel=channel):
+                            self.assertIn(code, (0, 2), output)
+                            hits = [line for line in output.splitlines() if "[ⓓ" + rule + "]" in line]
+                            self.assertEqual(len(hits), 1 if source else 0, output)
+                    if source and source != "empty_instance":
+                        (path / source).unlink()
+            shutil.rmtree(path)
+            if relative.startswith("application_layer/vanished_area"):
+                shutil.rmtree(path.parent)
+
     def test_cache_cannot_hide_fixed_skeleton_and_promoted_parts_have_no_floor(self):
         fixed = self.root / "application/orders/application_layer/port/unit_of_work"
         shutil.rmtree(fixed)
         self.plant(str(fixed.relative_to(self.root)))
         output = self.run_checker("check-layer-skeleton.py")
         self.assertTrue(any("#488" in line and "unit_of_work" in line for line in output.splitlines()), output)
         shutil.rmtree(self.root)
         shutil.copytree(FIXTURES / "skeleton/good_promoted", self.root)
         promoted = self.root / "application/orders/driving_layer/api/order/order_controller"
         part = promoted / "order_sse_renderer.py"

```

## workspace/tools/registry_gate_smoke.py

Before SHA256: ff22017079c33a4b568720b7f28e6a7cee909de3cb5e65309d9167447804ce7c
After SHA256: ff22017079c33a4b568720b7f28e6a7cee909de3cb5e65309d9167447804ce7c

```diff

```
