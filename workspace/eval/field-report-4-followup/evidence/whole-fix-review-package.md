# whole-fix review package

No commit was authorized. This package compares owned-file snapshots before this task with current bytes.

## codex-dddjango/skills/dddjango-design-architect/SKILL.md

Before SHA256: 7ae9c454bc3fcb8b4156d79207f2b50e5a5dd081fbb9a9e75de9681e24ea5ba7
After SHA256: 7ae9c454bc3fcb8b4156d79207f2b50e5a5dd081fbb9a9e75de9681e24ea5ba7

```diff

```

## codex-dddjango/skills/dddjango-design-review-api/SKILL.md

Before SHA256: 255c67d1c85643ed841f978c3a7c6e2e8537c6686fb8fa44fc65eb83ba5f2ce4
After SHA256: 255c67d1c85643ed841f978c3a7c6e2e8537c6686fb8fa44fc65eb83ba5f2ce4

```diff

```

## codex-dddjango/skills/dddjango-discipline-houserules/SKILL.md

Before SHA256: f0f81d47b30246c6eadf8eeb991017c286f2bf585b7b2293bf525842a18f4e0c
After SHA256: f0f81d47b30246c6eadf8eeb991017c286f2bf585b7b2293bf525842a18f4e0c

```diff

```

## codex-dddjango/skills/dddjango-discipline-houserules/references/final.md

Before SHA256: 768db015552547977d941d638c54a90ff5922229d70e1cbe99e6558bdc47cde1
After SHA256: 768db015552547977d941d638c54a90ff5922229d70e1cbe99e6558bdc47cde1

```diff

```

## codex-dddjango/skills/dddjango-discipline-reviewer/SKILL.md

Before SHA256: 1a9c7ce4f52c1ac2f3fbfdbeb77017792764d3ff4673134648b8f0425df19f3f
After SHA256: 1a9c7ce4f52c1ac2f3fbfdbeb77017792764d3ff4673134648b8f0425df19f3f

```diff

```

## codex-dddjango/skills/dddjango/SKILL.md

Before SHA256: 231ee7dae528430291e0b2ad695f03e731655c88170cc06773584edfab758a41
After SHA256: 231ee7dae528430291e0b2ad695f03e731655c88170cc06773584edfab758a41

```diff

```

## codex-dddjango/skills/dddjango/scripts/check-context-isolation.py

Before SHA256: 9248add559f8f27481284a1c451db45aba991e32e62eeb7545bc668046b4c075
After SHA256: bb68853338db1326575c954040bc8bdb1006440a855036e4fac3b8f8838389b5

```diff
--- before/codex-dddjango/skills/dddjango/scripts/check-context-isolation.py
+++ after/codex-dddjango/skills/dddjango/scripts/check-context-isolation.py
@@ -403,20 +403,22 @@
             if isinstance(st, ast.Import):
                 for a in st.names:
                     result[a.asname or a.name.split(".")[0]] = a.name if a.asname else a.name.split(".")[0]
             elif isinstance(st, ast.ImportFrom):
                 module = st.module or ""
                 if st.level:
                     parts = source.relative_to(root).with_suffix("").parts[:-1]
                     module = ".".join((*parts[:len(parts) - st.level + 1], *module.split(".")))
                 for a in st.names:
                     result[a.asname or a.name] = module + "." + a.name
+            elif isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
+                result.pop(st.name, None)
             elif isinstance(st, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
                 for t in st.targets if isinstance(st, ast.Assign) else [st.target]:
                     for n in ast.walk(t):
                         if isinstance(n, ast.Name):
                             result.pop(n.id, None)
         return result
 
     def address(expr, env):
         if isinstance(expr, ast.Constant) and isinstance(expr.value, str):
             try:

```

## codex-dddjango/skills/dddjango/scripts/check-domain-model.py

Before SHA256: 1dc8871ef71255e22c586e540a07a0f3d8b258a6fe2f26e4e1cb1cbe2bdde428
After SHA256: ded715d2026c7556b7ad35a125951eadc7239b9ff04913d52912e2987592e3a4

```diff
--- before/codex-dddjango/skills/dddjango/scripts/check-domain-model.py
+++ after/codex-dddjango/skills/dddjango/scripts/check-domain-model.py
@@ -830,20 +830,22 @@
         parts = name.split(".")
         return (".application_layer.port.unit_of_work." in name and len(parts) > 1
                 and parts[-2].endswith("_unit_of_work") and parts[-1].endswith("UnitOfWork"))
 
     module_env = {}
     for st in mod.body:
         if isinstance(st, (ast.Import, ast.ImportFrom)):
             module_env.update(imports([st]))
         elif isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef)):
             module_env[st.name] = "@uow" if is_uow(address(st.returns, module_env)) else ""
+        elif isinstance(st, ast.ClassDef):
+            module_env[st.name] = ""
         elif isinstance(st, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
             for target in st.targets if isinstance(st, ast.Assign) else [st.target]:
                 module_env[key(target)] = ""
 
     def origin(expr, env):
         if isinstance(expr, ast.Call):
             name = address(expr.func, env)
             if is_uow(name) or name == "@uow": return "@uow"
             parts = name.split(".")
             source = root.joinpath(*parts[:-1]).with_suffix(".py")

```

## codex-dddjango/skills/dddjango/scripts/check-layer-skeleton.py

Before SHA256: 9f2ea08ec409ed8e52340067685b3a828235b68d35347903cf09492f5355a645
After SHA256: 32810abb897f3dfc580c2880457fe894a68ea5e080ec6e71d4fef9b814425924

```diff
--- before/codex-dddjango/skills/dddjango/scripts/check-layer-skeleton.py
+++ after/codex-dddjango/skills/dddjango/scripts/check-layer-skeleton.py
@@ -17,21 +17,21 @@
   #395  `framework/` 의 자식은 다섯(고정 셋 + `<capability>/`·`<technology>/`) — 고정 셋의
         서브트리 존재는 #488 로 본다. 인스턴스 «내용»은 content 검사기 몫.
 
 가드 계약 (명세 조각 ⓐ):
   - 대상 0건 가드: 채택 신호는 있는데 검사할 BC 가 0이면 exit 2 (#74). 가드는 어떤
     필터보다 먼저 선다(#75).
   - 채택 신호원은 둘이다(#78): ⑴ 층 폴더 glob ⑵ Django 앱 마커.
 
 등록 순서: 이 검사는 다른 모든 검사보다 «먼저» 돌고, 걸리면 나머지를 돌리지 않는다(#487).
 내용 판정(#10·#628 등 ast 규칙)은 Phase 3 편입분이다 — 여기는 «존재·폐쇄»와 동명 폴더
-승격 실현의 형태 검증(#638~#643 · ⓓ#644 후보 신호 — 2026-09-01)만 본다.
+승격 실현의 형태 검증(#638~#641·#643 · ⓓ#644 후보 신호 — 2026-09-01)만 본다.
 
 사용법: check-layer-skeleton.py [TARGET_DIR]   (기본: 현재 디렉터리)
 종료코드: 0=clean(또는 표준 미채택) · 1=사용/분석 오류 · 2=blocker(발견 출력)
 구조화 레코드: DJR_FINDINGS_JSON=<경로> 지정 시 findings.py(공용 모듈)가 JSON lines 를
 추가 방출한다 — 라인 출력·exit 의미론 무변(T0 B2).
 
 그래프 좌표(T2-2): 규범 정본 = 온톨로지 그래프(`ontology/rules/`) · 이 검사기의 #N ↔ Work 조인은
   alias 대장(`ontology/wiring/aliases.ttl`)이 소유한다. 조인 확정: rule#10 → djr:R-3196 · rule#58 → djr:R-3210 ·
   rule#74 → djr:R-3229 · rule#314 → djr:R-3212 · rule#436 → djr:R-3220 · rule#487 → djr:R-3178 ·
   rule#488 → djr:R-3181 · rule#489 → djr:R-3182 · rule#491 → djr:R-3186.
@@ -79,21 +79,21 @@
 
 def _has_adoption_signal(bc_dir: Path) -> bool:
     """채택 신호원 둘(#78): 층 폴더 또는 Django 앱 마커."""
     has_layer = any((bc_dir / n).is_dir() for n in NEW_LAYERS)
     has_marker = any((bc_dir / m).is_file() for m in DJANGO_APP_MARKERS) or any(
         p.is_dir() and p.name.startswith("django_") for p in bc_dir.iterdir()
     )
     return has_layer or has_marker
 
 
-# ── 동명 폴더 승격(#490 교체형) — #638~#643 + ⓓ#644 ─────────────────────────
+# ── 동명 폴더 승격(#490 교체형) — #638~#641·#643 + ⓓ#644 ─────────────────────────
 
 # ⓓ#644 행위 칸 로스터 — 승격 허용 표기(swappable) 중 schema 4행(14·15·20·21) 제외
 # (houserules SKILL §1 감사 주도 배정 — 신호는 무조건 방출, 판정 의무의 diff 한정은 감사자 몫)
 PROMO_ACTION_ROWS = frozenset({12, 18, 24, 41, 61, 74, 92, 94, 96})
 PROMO_SIGNAL_LINES = 200   # ⓓ#644 후보 문턱(물리 행·빈 줄 제외)
 JUNK_DRAWER_NAMES = frozenset({"utils.py", "helpers.py", "util.py", "helper.py", "common.py", "misc.py"})
 _CASCADE_Q = "역할 밖 응집 단위가 있는가 — ①이동/②동명 폴더 승격/③유지 (houserules §1 캐스케이드)"
 
 
 def _phys_lines(path: Path) -> int:
@@ -120,21 +120,21 @@
                 isinstance(tg, _ast.Name) and tg.id == "__all__" for tg in node.targets):
             continue
         if isinstance(node, _ast.AnnAssign) and isinstance(node.target, _ast.Name) \
                 and node.target.id == "__all__":
             continue
         return False
     return True
 
 
 def _check_promoted(dir_path: Path, crow: "tree.Row", out: Findings, cand: Candidates) -> None:
-    """유효한 동명 폴더 승격의 형태 검증(#638~#643) + 행위 칸 ⓓ#644 신호."""
+    """유효한 동명 폴더 승격의 형태 검증(#638~#641·#643) + 행위 칸 ⓓ#644 신호."""
     body = dir_path / (dir_path.name + ".py")
     init = dir_path / "__init__.py"
     if not body.is_file():
         out.add("#638", dir_path, f"승격 폴더에 본체 `{dir_path.name}.py` 가 없다 — 위장 (트리 {crow.r}행)")
     if not init.is_file():
         out.add("#638", init, "승격 폴더에 재수출 전용 `__init__.py` 가 없다")
     elif not _init_reexport_only(init):
         out.add("#640", init, "`__init__.py` 는 재수출 전용이다 — from-as 재수출·`__all__`·docstring 밖 코드 동거 금지")
     subdirs, files = _entries(dir_path)
     for sd in subdirs:
@@ -236,21 +236,21 @@
             missing = sub / "__init__.py" if checker_target.adapter_bundle(dir_path) else sub
             out.add("#488", missing, "고정 칸 폴더에 `__init__.py` 가 없다")
         _check_level(sub, crow, bindings, out, cand)
     for name, crow in fixed_files.items():
         target = dir_path / name
         promo = dir_path / name[:-3] if name.endswith(".py") else None
         if target.is_file():
             continue
         if getattr(crow, "swappable", False) and promo is not None and promo.is_dir() \
                 and (promo / name).is_file():
-            continue  # 유효한 승격 실현이 #488 충족이다(형태 검증은 dir 루프의 #638~#643)
+            continue  # 유효한 승격 실현이 #488 충족이다(형태 검증은 dir 루프의 #638~#641·#643)
         out.add("#488", target, f"고정 파일 부재 — 비면 빈 파일로 만든다 (트리 {crow.r}행)")
 
     # #490 — 폴더 폐쇄: 칸이 아닌 폴더는 위반. 자리표시자 폴더가 있으면 나머지는 인스턴스다.
     if row.name.startswith("migrations"):
         for p in dirs:  # <migration>.py 는 파일 자리 — 폴더는 트리에 없는 경로다
             out.add("#490", p, "`migrations/` 아래 폴더는 트리에 없는 경로다")
         return
     for p in dirs:
         if p.name in fixed_dirs:
             continue

```

## codex-dddjango/skills/dddjango/scripts/check-port-adapter-pairing.py

Before SHA256: 9fe24b4df8df90a6cdfdf53d735a805db830c02830a50f7ec6ae791b007c5b5b
After SHA256: 9fe24b4df8df90a6cdfdf53d735a805db830c02830a50f7ec6ae791b007c5b5b

```diff

```

## codex-dddjango/skills/dddjango/scripts/check-public-surface-annotation.py

Before SHA256: 47afd19d407adc3318a68bb799841b368f860a7b703880d522d14108e78d6e06
After SHA256: b94b4101403d59926bdbdbe3aa64595afcb1547330215cd4e33cb4128555954b

```diff
--- before/codex-dddjango/skills/dddjango/scripts/check-public-surface-annotation.py
+++ after/codex-dddjango/skills/dddjango/scripts/check-public-surface-annotation.py
@@ -855,21 +855,26 @@
             local_bindings.update(a.arg for a in [*fn.args.posonlyargs, *fn.args.args, *fn.args.kwonlyargs])
             local_bindings.update(a.arg for a in (fn.args.vararg, fn.args.kwarg) if a is not None)
             shadowed[fn] = local_bindings
             for arg in [*fn.args.posonlyargs, *fn.args.args, *fn.args.kwonlyargs]:
                 if arg.annotation is not None:
                     annotations.setdefault((fn, arg.arg), []).append(arg.annotation)
                 if arg.arg == _ADMIN_CONTEXT.get(fn.name):
                     put(fn, arg.arg)
                     active.add(fn)
             if fn.name in _ADMIN_KWARGS and fn.args.kwarg:
-                fixed(fn.args.kwarg.annotation, kwargs=True)
+                kwarg = fn.args.kwarg
+                fixed(kwarg.annotation, kwargs=True)
+                if kwarg.annotation is not None:
+                    annotations.setdefault((fn, kwarg.arg), []).append(kwarg.annotation)
+                put(fn, kwarg.arg)
+                active.add(fn)
             if fn.name == "get_inline_instances":
                 fixed(fn.returns)
             for node in nodes:
                 if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                     annotations.setdefault((fn, node.target.id), []).append(node.annotation)
         for st in cls.body:
             if isinstance(st, ast.AnnAssign) and isinstance(st.target, ast.Name) and st.target.id == "inlines":
                 fixed(st.annotation)
 
         def context_names(expr: ast.AST | None) -> set[str]:
@@ -1061,20 +1066,22 @@
             for left, rights in edges.items():
                 if left not in states:
                     continue
                 for right in rights:
                     if right in states and rank[states[right]] < rank[states[left]]:
                         states[right] = states[left]
                         changed = True
         for key, status in states.items():
             reason = {"allow": "admin UI context 조립·framework 전달", "candidate": "admin context 흐름/호출 출처 불명", "ordinary": "context 값의 실제 소비"}[status]
             for ann in annotations.get(key, []):
+                if status == "allow" and id(ann) in policy:
+                    continue  # 소비가 없을 때만 확인된 framework 고정 슬롯을 유지한다.
                 policy[id(ann)] = (status, reason)
     return policy
 
 
 def _check_explicit_any(mod: ast.Module, rel: Path, out: Findings, cands: Candidates,
                         bindings: "dict[str, str] | None" = None,
                         aliases: "dict[str, list[tuple[ast.AST, bool]]] | None" = None) -> None:
     """#645 — 시그니처 bare `Any` 는 위반 · 시그니처 nested 와 변수/속성/클래스 필드의 `Any` 는 ⓓ 후보.
     #647 — 같은 애너테이션에서 먼저 판정한다: `dict/Mapping` 값 자리 `Any` 는 전 자리 차단 · `object` 는
     반환/클래스 속성 차단 · 매개변수/변수 ⓓ(면제 = `TypeIs/TypeGuard` 루트 · 스텁 강제 오버라이드).
@@ -1097,22 +1104,22 @@
         status, reason = admin_policy.get(id(ann), ("ordinary", ""))
         value, _ = _record_value(ann, names, mods, bindings)
         fixed_slot = reason == "확인된 admin framework override 슬롯"
         if status == "allow" and ((value is not None and v645 != "bare") or (fixed_slot and (v645 == "nested" or site == "sig-star"))):
             return
         if status == "candidate" and ann is not None:
             value, _ = _record_value(ann, names, mods, bindings)
             if in_roots and value is not None and v645 != "bare":
                 hits.append((lineno, "c", "#647", where, f"{label}의 열린 admin context — {reason}", RECORD_Q))
                 return
-            if v645 == "nested":
-                hits.append((lineno, "c", "#645", where, nested_msg, ANY_Q))
+            if v645 == "nested" or (v645 == "bare" and site == "sig-star"):
+                hits.append((lineno, "c", "#645", where, bare_msg if v645 == "bare" else nested_msg, ANY_Q))
                 return
         blocked647 = False
         if in_roots and ann is not None:
             value, _top = _record_value(ann, names, mods, bindings)
             root = _unstring(ann)
             guard_root = isinstance(root, ast.Subscript) and _resolved_name(root.value, bindings) in TYPE_GUARDS
             if value == "Any":
                 hits.append((lineno, "v", "#647", where, f"{label}의 " + RECORD_MSG.format(v="Any"), ""))
                 blocked647 = True
             elif value == "object" and not (site == "sig-return" and (guard_root or exempt_object)):

```

## codex-dddjango/skills/dddjango/scripts/check-usecase-dto-placement.py

Before SHA256: 4a51b80b722d516c3d94423bb2cdec832a7c4cf7c0be3102b882a9ddbbe7bbb7
After SHA256: 4a51b80b722d516c3d94423bb2cdec832a7c4cf7c0be3102b882a9ddbbe7bbb7

```diff

```

## codex-dddjango/skills/dddjango/scripts/checker_target.py

Before SHA256: 2efb7adbe792ddf4fadc9527699bb130ef1953481acdff70ad01e469ebdd0112
After SHA256: 2efb7adbe792ddf4fadc9527699bb130ef1953481acdff70ad01e469ebdd0112

```diff

```

## codex-dddjango/skills/dddjango/scripts/design_pregate.py

Before SHA256: 4d0dcb064ee6a7b49dfb7b7a1b8dd15fb707b2179a17601d4d29b2f58e8b66a8
After SHA256: 7a16f052b671c8dc6a605293aae3a0786d3daa1a7e71c14c4931fc5020d099fe

```diff
--- before/codex-dddjango/skills/dddjango/scripts/design_pregate.py
+++ after/codex-dddjango/skills/dddjango/scripts/design_pregate.py
@@ -1421,36 +1421,42 @@
         return None, f"marker 기존 파일 파싱 불가: {exc}"
     bindings, open_surface = _update_bindings(module)
     if open_surface:
         return None, "marker 동적/star/class global 표면"
     pytest_aliases = {name for name, origins in bindings.items() if origins == {"import pytest"}}
     mark_aliases = {name for name, origins in bindings.items() if origins == {"from pytest import mark"}}
     if "pytest" in bindings and "pytest" not in pytest_aliases:
         return None, "pytest 이름 재바인딩/충돌"
     stores: list[ast.AST] = []
     mutations: list[ast.Subscript] = []
+    method_calls: list[ast.Call] = []
     def visit(node: ast.AST) -> None:
         if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
             if node.name == "pytestmark":
                 stores.append(node)
             return
         if isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Del)) and node.id == "pytestmark":
             stores.append(node)
         if isinstance(node, ast.Subscript) and isinstance(node.ctx, (ast.Store, ast.Del)):
             root: ast.expr = node.value
             while isinstance(root, (ast.Subscript, ast.Attribute)):
                 root = root.value
             if isinstance(root, ast.Name) and root.id == "pytestmark":
                 mutations.append(node)
+        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
+                and isinstance(node.func.value, ast.Name) and node.func.value.id == "pytestmark":
+            method_calls.append(node)
         for child in ast.iter_child_nodes(node):
             visit(child)
     visit(module)
+    if method_calls:
+        return None, "module pytestmark method 호출 — 최종 목록 미해소"
     if mutations:
         return None, "module pytestmark subscript mutation — 최종 목록 미해소"
     assignments = [node for node in module.body if
         isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name)
         and node.targets[0].id == "pytestmark" or isinstance(node, ast.AnnAssign)
         and isinstance(node.target, ast.Name) and node.target.id == "pytestmark"]
     if "pytestmark" in bindings and bindings["pytestmark"] != {""}:
         return None, "module pytestmark import 바인딩 충돌"
     if stores and (len(stores) != 1 or len(assignments) != 1):
         return None, "module pytestmark 중복/동적/조건부 대입"
@@ -1587,103 +1593,109 @@
                                  f"{' -> ' + method.ret if method.ret else ''}: ..."]
                     if len(body) == 1:
                         body.append("    pass")
                     node = ast.parse("\n".join(body)).body[0]
                 except (SyntaxError, ValueError):
                     node = None
                 declared.setdefault(symbol.name, []).append(node)
             table.update(declared)
         return table
 
-    def resolve(self, module: str, expression: ast.expr, seen: frozenset[tuple[str, str]] = frozenset()
+    def resolve(self, module: str, expression: ast.expr, seen: frozenset[tuple[str, str]] = frozenset(),
+                referenced_names: set[str] | None = None
                 ) -> tuple[list[tuple[str, str, ast.ClassDef | None]], list[str]]:
         """컨테이너·alias·forward 타입을 identity로 해소한다. 미해소는 후보 근거다."""
         if isinstance(expression, ast.Constant):
             if isinstance(expression.value, str):
                 try:
-                    return self.resolve(module, ast.parse(expression.value, mode="eval").body, seen)
+                    return self.resolve(module, ast.parse(expression.value, mode="eval").body, seen, referenced_names)
                 except SyntaxError:
                     return [], [f"forward annotation 파싱 불가: {expression.value}"]
             return [], []
         if isinstance(expression, (ast.Tuple, ast.List)):
             nodes = expression.elts
         elif isinstance(expression, ast.BinOp) and isinstance(expression.op, ast.BitOr):
             nodes = [expression.left, expression.right]
         elif isinstance(expression, ast.Subscript):
             head = ast.unparse(expression.value)
-            identity, issues = self.resolve(module, expression.value, seen)
+            identity, issues = self.resolve(module, expression.value, seen, referenced_names)
             names = {(m, n) for m, n, _ in identity}
             if ("typing", "Literal") in names:
                 return [], []
             supported = {"list", "tuple", "set", "frozenset", "dict", "Mapping", "Sequence", "Optional", "Union"}
             builtin_container = head in {"list", "tuple", "set", "frozenset", "dict"} and head not in self.load(module)
             if builtin_container or any(m in ("typing", "collections.abc", "builtins") and n in supported for m, n in names):
-                return self.resolve(module, expression.slice, seen)
+                return self.resolve(module, expression.slice, seen, referenced_names)
             # Unknown generic semantics cannot prove contained field identity.
             return [], issues or [f"타입 컨테이너 출처/필드 의미 미해소: {head}"]
         else:
             nodes = []
         if nodes:
             identities, issues = [], []
             for node in nodes:
-                found, uncertain = self.resolve(module, node, seen)
+                found, uncertain = self.resolve(module, node, seen, referenced_names)
                 identities.extend(found)
                 issues.extend(uncertain)
             return identities, issues
         if not isinstance(expression, (ast.Name, ast.Attribute)):
             return [], [f"타입식 미지원: {ast.unparse(expression)}"]
         name = ast.unparse(expression)
+        if referenced_names is not None:
+            referenced_names.add(name)
         primitive = {"str", "int", "float", "bool", "bytes", "bytearray", "object", "None", "complex"}
         if name in primitive:
             return [], []
         key = (module, name)
         if key in seen:
             return [], [f"alias cycle: {module}.{name}"]
         seen = seen | {key}
         if isinstance(expression, ast.Attribute):
             pieces = name.split(".")
             table = self.load(module)
             root = table.get(pieces[0], [])
             if len(root) == 1 and isinstance(root[0], tuple):
                 origin, symbol = root[0]
                 qualified = [origin] + ([symbol] if symbol else []) + pieces[1:]
                 target = ".".join(qualified[:-1])
-                return self.identity(target, pieces[-1], seen)
+                return self.identity(target, pieces[-1], seen, referenced_names=referenced_names)
             if root:
                 return [], [f"qualified 타입 출처 중복/미해소: {name}"]
             if self._known_root(pieces[0]):
-                return self.identity(".".join(pieces[:-1]), pieces[-1], seen)
+                return self.identity(".".join(pieces[:-1]), pieces[-1], seen, referenced_names=referenced_names)
             return [], [f"qualified 타입 출처 미해소: {name}"]
-        return self.identity(module, name, seen, local=True)
+        return self.identity(module, name, seen, local=True, referenced_names=referenced_names)
 
     def _known_root(self, name: str) -> bool:
         return name in ("typing", "builtins", "collections") or _is_repo_target(self.copy, name, self.plan)
 
-    def identity(self, module: str, name: str, seen: frozenset[tuple[str, str]], local: bool = False
+    def identity(self, module: str, name: str, seen: frozenset[tuple[str, str]], local: bool = False,
+                 referenced_names: set[str] | None = None
                  ) -> tuple[list[tuple[str, str, ast.ClassDef | None]], list[str]]:
+        if referenced_names is not None:
+            referenced_names.add(name)
         values = self.load(module).get(name, [])
         if len(values) > 1 or values == [None]:
             return [], [f"타입 선언 중복/분기 불일치: {module}.{name}"]
         if values:
             value = values[0]
             if isinstance(value, ast.ClassDef):
                 return [(module, name, value)], []
             if isinstance(value, tuple):
                 origin, imported = value
                 if not imported:
                     return [], [f"모듈 자체는 필드 타입 미확정: {module}.{name}"]
                 key = (origin, imported)
                 if key in seen:
                     return [], [f"alias cycle: {origin}.{imported}"]
-                return self.identity(origin, imported, seen | {key})
+                return self.identity(origin, imported, seen | {key}, referenced_names=referenced_names)
             if isinstance(value, ast.expr):
-                return self.resolve(module, value, seen)
+                return self.resolve(module, value, seen, referenced_names)
             return [], [f"타입 출처 미해소: {module}.{name}"]
         if local:
             return [], [f"bare 타입 `{name}` 출처 미해소 — 명시 import/별칭 출처를 보완해 주세요"]
         # An explicit import/qualified module identity proves provenance; it does not prove existence.
         return [(module, name, None)], []
 
 
 def check_declarations(plan: Plan, copy: Path) -> list[DeclarationFinding]:
     """효과·DTO 명시 선언의 확정/후보 근거를 반환한다. 사본 파일을 변경하지 않는다."""
     types = _DeclarationTypes(plan, copy)
@@ -1706,23 +1718,24 @@
 
     for effect in plan.effects:
         if effect.effect == "read-only" and effect.uow != "none":
             add("#197", effect.path, effect.owner, f"read-only + uow={effect.uow} 명시 모순", True)
             continue
         module = types.module(effect.path)
         values = types.load(module).get(effect.owner, [])
         injected, unknown = [], []
         if len(values) == 1 and isinstance(values[0], ast.ClassDef):
             for annotation in annotations(values[0], True):
-                identities, issues = types.resolve(module, annotation)
+                referenced_names: set[str] = set()
+                identities, issues = types.resolve(module, annotation, referenced_names=referenced_names)
                 injected += [f"{m}.{n}" for m, n, _ in identities if ".application_layer.port.unit_of_work." in m + "."]
-                if "UnitOfWork" in ast.unparse(annotation):
+                if "UnitOfWork" in ast.unparse(annotation) or any("UnitOfWork" in name for name in referenced_names):
                     unknown += issues
         else:
             unknown.append("클래스 선언 중복/파싱 불가")
         if effect.effect == "read-only":
             if injected:
                 add("#197", effect.path, effect.owner, "read-only + uow=none에 명시 UoW port 주입: " + ", ".join(injected), True)
             elif unknown:
                 add("#197", effect.path, effect.owner, "; ".join(unknown), False)
         elif effect.uow == "none" and injected:
             note = f"채널 불일치(비차단): {effect.path}::{effect.owner} write/uow=none + 주입 {', '.join(injected)}"

```

## codex-dddjango/skills/dddjango/scripts/registry_gate.py

Before SHA256: bcc7db98fe1f209f330d6c2ffb92239792580207f0d4bad317d6130fa60d273a
After SHA256: bcc7db98fe1f209f330d6c2ffb92239792580207f0d4bad317d6130fa60d273a

```diff

```

## codex-dddjango/skills/dddjango/scripts/rulepack.json

Before SHA256: eca32486b4c7f9eda77e58c86e8b6a690289d80990037d714bb65088e477bb55
After SHA256: eca32486b4c7f9eda77e58c86e8b6a690289d80990037d714bb65088e477bb55

```diff

```

## codex-dddjango/skills/implementation-django-ninja/SKILL.md

Before SHA256: fbc91023e3326b394a69064435188eac0193004e14adac2eaa8b2cba891f3338
After SHA256: fbc91023e3326b394a69064435188eac0193004e14adac2eaa8b2cba891f3338

```diff

```

## codex-dddjango/skills/implementation-django-ninja/references/final.md

Before SHA256: f6276de920006a6caf6c9eca74e23e81099e8a3a10ffb2fc829298eb339642f2
After SHA256: f6276de920006a6caf6c9eca74e23e81099e8a3a10ffb2fc829298eb339642f2

```diff

```

## dddjango/agents/design-architect.md

Before SHA256: 6814957c64d98e04d21475516c871c10e3ab8d75e1754e1719337f6160638a13
After SHA256: 6814957c64d98e04d21475516c871c10e3ab8d75e1754e1719337f6160638a13

```diff

```

## dddjango/agents/design-review-api.md

Before SHA256: 7db60d7a67888d2fd2874ead2d59f6bafd7f3d05e8fdc47efcdb8ed2ccf503be
After SHA256: 7db60d7a67888d2fd2874ead2d59f6bafd7f3d05e8fdc47efcdb8ed2ccf503be

```diff

```

## dddjango/agents/discipline-reviewer.md

Before SHA256: c6cf298c7a61a76473a0ddca945dd338bff4660dd74eb393e2f85dbad252bb05
After SHA256: c6cf298c7a61a76473a0ddca945dd338bff4660dd74eb393e2f85dbad252bb05

```diff

```

## dddjango/commands/dddjango.md

Before SHA256: 25fb90b6acd0211de2d441f2af96a428614f00a168e4ddd06985e6883d0621d0
After SHA256: 25fb90b6acd0211de2d441f2af96a428614f00a168e4ddd06985e6883d0621d0

```diff

```

## dddjango/scripts/check-context-isolation.py

Before SHA256: 9248add559f8f27481284a1c451db45aba991e32e62eeb7545bc668046b4c075
After SHA256: bb68853338db1326575c954040bc8bdb1006440a855036e4fac3b8f8838389b5

```diff
--- before/dddjango/scripts/check-context-isolation.py
+++ after/dddjango/scripts/check-context-isolation.py
@@ -403,20 +403,22 @@
             if isinstance(st, ast.Import):
                 for a in st.names:
                     result[a.asname or a.name.split(".")[0]] = a.name if a.asname else a.name.split(".")[0]
             elif isinstance(st, ast.ImportFrom):
                 module = st.module or ""
                 if st.level:
                     parts = source.relative_to(root).with_suffix("").parts[:-1]
                     module = ".".join((*parts[:len(parts) - st.level + 1], *module.split(".")))
                 for a in st.names:
                     result[a.asname or a.name] = module + "." + a.name
+            elif isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
+                result.pop(st.name, None)
             elif isinstance(st, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
                 for t in st.targets if isinstance(st, ast.Assign) else [st.target]:
                     for n in ast.walk(t):
                         if isinstance(n, ast.Name):
                             result.pop(n.id, None)
         return result
 
     def address(expr, env):
         if isinstance(expr, ast.Constant) and isinstance(expr.value, str):
             try:

```

## dddjango/scripts/check-domain-model.py

Before SHA256: 1dc8871ef71255e22c586e540a07a0f3d8b258a6fe2f26e4e1cb1cbe2bdde428
After SHA256: ded715d2026c7556b7ad35a125951eadc7239b9ff04913d52912e2987592e3a4

```diff
--- before/dddjango/scripts/check-domain-model.py
+++ after/dddjango/scripts/check-domain-model.py
@@ -830,20 +830,22 @@
         parts = name.split(".")
         return (".application_layer.port.unit_of_work." in name and len(parts) > 1
                 and parts[-2].endswith("_unit_of_work") and parts[-1].endswith("UnitOfWork"))
 
     module_env = {}
     for st in mod.body:
         if isinstance(st, (ast.Import, ast.ImportFrom)):
             module_env.update(imports([st]))
         elif isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef)):
             module_env[st.name] = "@uow" if is_uow(address(st.returns, module_env)) else ""
+        elif isinstance(st, ast.ClassDef):
+            module_env[st.name] = ""
         elif isinstance(st, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
             for target in st.targets if isinstance(st, ast.Assign) else [st.target]:
                 module_env[key(target)] = ""
 
     def origin(expr, env):
         if isinstance(expr, ast.Call):
             name = address(expr.func, env)
             if is_uow(name) or name == "@uow": return "@uow"
             parts = name.split(".")
             source = root.joinpath(*parts[:-1]).with_suffix(".py")

```

## dddjango/scripts/check-layer-skeleton.py

Before SHA256: 9f2ea08ec409ed8e52340067685b3a828235b68d35347903cf09492f5355a645
After SHA256: 32810abb897f3dfc580c2880457fe894a68ea5e080ec6e71d4fef9b814425924

```diff
--- before/dddjango/scripts/check-layer-skeleton.py
+++ after/dddjango/scripts/check-layer-skeleton.py
@@ -17,21 +17,21 @@
   #395  `framework/` 의 자식은 다섯(고정 셋 + `<capability>/`·`<technology>/`) — 고정 셋의
         서브트리 존재는 #488 로 본다. 인스턴스 «내용»은 content 검사기 몫.
 
 가드 계약 (명세 조각 ⓐ):
   - 대상 0건 가드: 채택 신호는 있는데 검사할 BC 가 0이면 exit 2 (#74). 가드는 어떤
     필터보다 먼저 선다(#75).
   - 채택 신호원은 둘이다(#78): ⑴ 층 폴더 glob ⑵ Django 앱 마커.
 
 등록 순서: 이 검사는 다른 모든 검사보다 «먼저» 돌고, 걸리면 나머지를 돌리지 않는다(#487).
 내용 판정(#10·#628 등 ast 규칙)은 Phase 3 편입분이다 — 여기는 «존재·폐쇄»와 동명 폴더
-승격 실현의 형태 검증(#638~#643 · ⓓ#644 후보 신호 — 2026-09-01)만 본다.
+승격 실현의 형태 검증(#638~#641·#643 · ⓓ#644 후보 신호 — 2026-09-01)만 본다.
 
 사용법: check-layer-skeleton.py [TARGET_DIR]   (기본: 현재 디렉터리)
 종료코드: 0=clean(또는 표준 미채택) · 1=사용/분석 오류 · 2=blocker(발견 출력)
 구조화 레코드: DJR_FINDINGS_JSON=<경로> 지정 시 findings.py(공용 모듈)가 JSON lines 를
 추가 방출한다 — 라인 출력·exit 의미론 무변(T0 B2).
 
 그래프 좌표(T2-2): 규범 정본 = 온톨로지 그래프(`ontology/rules/`) · 이 검사기의 #N ↔ Work 조인은
   alias 대장(`ontology/wiring/aliases.ttl`)이 소유한다. 조인 확정: rule#10 → djr:R-3196 · rule#58 → djr:R-3210 ·
   rule#74 → djr:R-3229 · rule#314 → djr:R-3212 · rule#436 → djr:R-3220 · rule#487 → djr:R-3178 ·
   rule#488 → djr:R-3181 · rule#489 → djr:R-3182 · rule#491 → djr:R-3186.
@@ -79,21 +79,21 @@
 
 def _has_adoption_signal(bc_dir: Path) -> bool:
     """채택 신호원 둘(#78): 층 폴더 또는 Django 앱 마커."""
     has_layer = any((bc_dir / n).is_dir() for n in NEW_LAYERS)
     has_marker = any((bc_dir / m).is_file() for m in DJANGO_APP_MARKERS) or any(
         p.is_dir() and p.name.startswith("django_") for p in bc_dir.iterdir()
     )
     return has_layer or has_marker
 
 
-# ── 동명 폴더 승격(#490 교체형) — #638~#643 + ⓓ#644 ─────────────────────────
+# ── 동명 폴더 승격(#490 교체형) — #638~#641·#643 + ⓓ#644 ─────────────────────────
 
 # ⓓ#644 행위 칸 로스터 — 승격 허용 표기(swappable) 중 schema 4행(14·15·20·21) 제외
 # (houserules SKILL §1 감사 주도 배정 — 신호는 무조건 방출, 판정 의무의 diff 한정은 감사자 몫)
 PROMO_ACTION_ROWS = frozenset({12, 18, 24, 41, 61, 74, 92, 94, 96})
 PROMO_SIGNAL_LINES = 200   # ⓓ#644 후보 문턱(물리 행·빈 줄 제외)
 JUNK_DRAWER_NAMES = frozenset({"utils.py", "helpers.py", "util.py", "helper.py", "common.py", "misc.py"})
 _CASCADE_Q = "역할 밖 응집 단위가 있는가 — ①이동/②동명 폴더 승격/③유지 (houserules §1 캐스케이드)"
 
 
 def _phys_lines(path: Path) -> int:
@@ -120,21 +120,21 @@
                 isinstance(tg, _ast.Name) and tg.id == "__all__" for tg in node.targets):
             continue
         if isinstance(node, _ast.AnnAssign) and isinstance(node.target, _ast.Name) \
                 and node.target.id == "__all__":
             continue
         return False
     return True
 
 
 def _check_promoted(dir_path: Path, crow: "tree.Row", out: Findings, cand: Candidates) -> None:
-    """유효한 동명 폴더 승격의 형태 검증(#638~#643) + 행위 칸 ⓓ#644 신호."""
+    """유효한 동명 폴더 승격의 형태 검증(#638~#641·#643) + 행위 칸 ⓓ#644 신호."""
     body = dir_path / (dir_path.name + ".py")
     init = dir_path / "__init__.py"
     if not body.is_file():
         out.add("#638", dir_path, f"승격 폴더에 본체 `{dir_path.name}.py` 가 없다 — 위장 (트리 {crow.r}행)")
     if not init.is_file():
         out.add("#638", init, "승격 폴더에 재수출 전용 `__init__.py` 가 없다")
     elif not _init_reexport_only(init):
         out.add("#640", init, "`__init__.py` 는 재수출 전용이다 — from-as 재수출·`__all__`·docstring 밖 코드 동거 금지")
     subdirs, files = _entries(dir_path)
     for sd in subdirs:
@@ -236,21 +236,21 @@
             missing = sub / "__init__.py" if checker_target.adapter_bundle(dir_path) else sub
             out.add("#488", missing, "고정 칸 폴더에 `__init__.py` 가 없다")
         _check_level(sub, crow, bindings, out, cand)
     for name, crow in fixed_files.items():
         target = dir_path / name
         promo = dir_path / name[:-3] if name.endswith(".py") else None
         if target.is_file():
             continue
         if getattr(crow, "swappable", False) and promo is not None and promo.is_dir() \
                 and (promo / name).is_file():
-            continue  # 유효한 승격 실현이 #488 충족이다(형태 검증은 dir 루프의 #638~#643)
+            continue  # 유효한 승격 실현이 #488 충족이다(형태 검증은 dir 루프의 #638~#641·#643)
         out.add("#488", target, f"고정 파일 부재 — 비면 빈 파일로 만든다 (트리 {crow.r}행)")
 
     # #490 — 폴더 폐쇄: 칸이 아닌 폴더는 위반. 자리표시자 폴더가 있으면 나머지는 인스턴스다.
     if row.name.startswith("migrations"):
         for p in dirs:  # <migration>.py 는 파일 자리 — 폴더는 트리에 없는 경로다
             out.add("#490", p, "`migrations/` 아래 폴더는 트리에 없는 경로다")
         return
     for p in dirs:
         if p.name in fixed_dirs:
             continue

```

## dddjango/scripts/check-port-adapter-pairing.py

Before SHA256: 9fe24b4df8df90a6cdfdf53d735a805db830c02830a50f7ec6ae791b007c5b5b
After SHA256: 9fe24b4df8df90a6cdfdf53d735a805db830c02830a50f7ec6ae791b007c5b5b

```diff

```

## dddjango/scripts/check-public-surface-annotation.py

Before SHA256: 47afd19d407adc3318a68bb799841b368f860a7b703880d522d14108e78d6e06
After SHA256: b94b4101403d59926bdbdbe3aa64595afcb1547330215cd4e33cb4128555954b

```diff
--- before/dddjango/scripts/check-public-surface-annotation.py
+++ after/dddjango/scripts/check-public-surface-annotation.py
@@ -855,21 +855,26 @@
             local_bindings.update(a.arg for a in [*fn.args.posonlyargs, *fn.args.args, *fn.args.kwonlyargs])
             local_bindings.update(a.arg for a in (fn.args.vararg, fn.args.kwarg) if a is not None)
             shadowed[fn] = local_bindings
             for arg in [*fn.args.posonlyargs, *fn.args.args, *fn.args.kwonlyargs]:
                 if arg.annotation is not None:
                     annotations.setdefault((fn, arg.arg), []).append(arg.annotation)
                 if arg.arg == _ADMIN_CONTEXT.get(fn.name):
                     put(fn, arg.arg)
                     active.add(fn)
             if fn.name in _ADMIN_KWARGS and fn.args.kwarg:
-                fixed(fn.args.kwarg.annotation, kwargs=True)
+                kwarg = fn.args.kwarg
+                fixed(kwarg.annotation, kwargs=True)
+                if kwarg.annotation is not None:
+                    annotations.setdefault((fn, kwarg.arg), []).append(kwarg.annotation)
+                put(fn, kwarg.arg)
+                active.add(fn)
             if fn.name == "get_inline_instances":
                 fixed(fn.returns)
             for node in nodes:
                 if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                     annotations.setdefault((fn, node.target.id), []).append(node.annotation)
         for st in cls.body:
             if isinstance(st, ast.AnnAssign) and isinstance(st.target, ast.Name) and st.target.id == "inlines":
                 fixed(st.annotation)
 
         def context_names(expr: ast.AST | None) -> set[str]:
@@ -1061,20 +1066,22 @@
             for left, rights in edges.items():
                 if left not in states:
                     continue
                 for right in rights:
                     if right in states and rank[states[right]] < rank[states[left]]:
                         states[right] = states[left]
                         changed = True
         for key, status in states.items():
             reason = {"allow": "admin UI context 조립·framework 전달", "candidate": "admin context 흐름/호출 출처 불명", "ordinary": "context 값의 실제 소비"}[status]
             for ann in annotations.get(key, []):
+                if status == "allow" and id(ann) in policy:
+                    continue  # 소비가 없을 때만 확인된 framework 고정 슬롯을 유지한다.
                 policy[id(ann)] = (status, reason)
     return policy
 
 
 def _check_explicit_any(mod: ast.Module, rel: Path, out: Findings, cands: Candidates,
                         bindings: "dict[str, str] | None" = None,
                         aliases: "dict[str, list[tuple[ast.AST, bool]]] | None" = None) -> None:
     """#645 — 시그니처 bare `Any` 는 위반 · 시그니처 nested 와 변수/속성/클래스 필드의 `Any` 는 ⓓ 후보.
     #647 — 같은 애너테이션에서 먼저 판정한다: `dict/Mapping` 값 자리 `Any` 는 전 자리 차단 · `object` 는
     반환/클래스 속성 차단 · 매개변수/변수 ⓓ(면제 = `TypeIs/TypeGuard` 루트 · 스텁 강제 오버라이드).
@@ -1097,22 +1104,22 @@
         status, reason = admin_policy.get(id(ann), ("ordinary", ""))
         value, _ = _record_value(ann, names, mods, bindings)
         fixed_slot = reason == "확인된 admin framework override 슬롯"
         if status == "allow" and ((value is not None and v645 != "bare") or (fixed_slot and (v645 == "nested" or site == "sig-star"))):
             return
         if status == "candidate" and ann is not None:
             value, _ = _record_value(ann, names, mods, bindings)
             if in_roots and value is not None and v645 != "bare":
                 hits.append((lineno, "c", "#647", where, f"{label}의 열린 admin context — {reason}", RECORD_Q))
                 return
-            if v645 == "nested":
-                hits.append((lineno, "c", "#645", where, nested_msg, ANY_Q))
+            if v645 == "nested" or (v645 == "bare" and site == "sig-star"):
+                hits.append((lineno, "c", "#645", where, bare_msg if v645 == "bare" else nested_msg, ANY_Q))
                 return
         blocked647 = False
         if in_roots and ann is not None:
             value, _top = _record_value(ann, names, mods, bindings)
             root = _unstring(ann)
             guard_root = isinstance(root, ast.Subscript) and _resolved_name(root.value, bindings) in TYPE_GUARDS
             if value == "Any":
                 hits.append((lineno, "v", "#647", where, f"{label}의 " + RECORD_MSG.format(v="Any"), ""))
                 blocked647 = True
             elif value == "object" and not (site == "sig-return" and (guard_root or exempt_object)):

```

## dddjango/scripts/check-usecase-dto-placement.py

Before SHA256: 4a51b80b722d516c3d94423bb2cdec832a7c4cf7c0be3102b882a9ddbbe7bbb7
After SHA256: 4a51b80b722d516c3d94423bb2cdec832a7c4cf7c0be3102b882a9ddbbe7bbb7

```diff

```

## dddjango/scripts/checker_target.py

Before SHA256: 2efb7adbe792ddf4fadc9527699bb130ef1953481acdff70ad01e469ebdd0112
After SHA256: 2efb7adbe792ddf4fadc9527699bb130ef1953481acdff70ad01e469ebdd0112

```diff

```

## dddjango/scripts/design_pregate.py

Before SHA256: 4d0dcb064ee6a7b49dfb7b7a1b8dd15fb707b2179a17601d4d29b2f58e8b66a8
After SHA256: 7a16f052b671c8dc6a605293aae3a0786d3daa1a7e71c14c4931fc5020d099fe

```diff
--- before/dddjango/scripts/design_pregate.py
+++ after/dddjango/scripts/design_pregate.py
@@ -1421,36 +1421,42 @@
         return None, f"marker 기존 파일 파싱 불가: {exc}"
     bindings, open_surface = _update_bindings(module)
     if open_surface:
         return None, "marker 동적/star/class global 표면"
     pytest_aliases = {name for name, origins in bindings.items() if origins == {"import pytest"}}
     mark_aliases = {name for name, origins in bindings.items() if origins == {"from pytest import mark"}}
     if "pytest" in bindings and "pytest" not in pytest_aliases:
         return None, "pytest 이름 재바인딩/충돌"
     stores: list[ast.AST] = []
     mutations: list[ast.Subscript] = []
+    method_calls: list[ast.Call] = []
     def visit(node: ast.AST) -> None:
         if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
             if node.name == "pytestmark":
                 stores.append(node)
             return
         if isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Del)) and node.id == "pytestmark":
             stores.append(node)
         if isinstance(node, ast.Subscript) and isinstance(node.ctx, (ast.Store, ast.Del)):
             root: ast.expr = node.value
             while isinstance(root, (ast.Subscript, ast.Attribute)):
                 root = root.value
             if isinstance(root, ast.Name) and root.id == "pytestmark":
                 mutations.append(node)
+        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
+                and isinstance(node.func.value, ast.Name) and node.func.value.id == "pytestmark":
+            method_calls.append(node)
         for child in ast.iter_child_nodes(node):
             visit(child)
     visit(module)
+    if method_calls:
+        return None, "module pytestmark method 호출 — 최종 목록 미해소"
     if mutations:
         return None, "module pytestmark subscript mutation — 최종 목록 미해소"
     assignments = [node for node in module.body if
         isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name)
         and node.targets[0].id == "pytestmark" or isinstance(node, ast.AnnAssign)
         and isinstance(node.target, ast.Name) and node.target.id == "pytestmark"]
     if "pytestmark" in bindings and bindings["pytestmark"] != {""}:
         return None, "module pytestmark import 바인딩 충돌"
     if stores and (len(stores) != 1 or len(assignments) != 1):
         return None, "module pytestmark 중복/동적/조건부 대입"
@@ -1587,103 +1593,109 @@
                                  f"{' -> ' + method.ret if method.ret else ''}: ..."]
                     if len(body) == 1:
                         body.append("    pass")
                     node = ast.parse("\n".join(body)).body[0]
                 except (SyntaxError, ValueError):
                     node = None
                 declared.setdefault(symbol.name, []).append(node)
             table.update(declared)
         return table
 
-    def resolve(self, module: str, expression: ast.expr, seen: frozenset[tuple[str, str]] = frozenset()
+    def resolve(self, module: str, expression: ast.expr, seen: frozenset[tuple[str, str]] = frozenset(),
+                referenced_names: set[str] | None = None
                 ) -> tuple[list[tuple[str, str, ast.ClassDef | None]], list[str]]:
         """컨테이너·alias·forward 타입을 identity로 해소한다. 미해소는 후보 근거다."""
         if isinstance(expression, ast.Constant):
             if isinstance(expression.value, str):
                 try:
-                    return self.resolve(module, ast.parse(expression.value, mode="eval").body, seen)
+                    return self.resolve(module, ast.parse(expression.value, mode="eval").body, seen, referenced_names)
                 except SyntaxError:
                     return [], [f"forward annotation 파싱 불가: {expression.value}"]
             return [], []
         if isinstance(expression, (ast.Tuple, ast.List)):
             nodes = expression.elts
         elif isinstance(expression, ast.BinOp) and isinstance(expression.op, ast.BitOr):
             nodes = [expression.left, expression.right]
         elif isinstance(expression, ast.Subscript):
             head = ast.unparse(expression.value)
-            identity, issues = self.resolve(module, expression.value, seen)
+            identity, issues = self.resolve(module, expression.value, seen, referenced_names)
             names = {(m, n) for m, n, _ in identity}
             if ("typing", "Literal") in names:
                 return [], []
             supported = {"list", "tuple", "set", "frozenset", "dict", "Mapping", "Sequence", "Optional", "Union"}
             builtin_container = head in {"list", "tuple", "set", "frozenset", "dict"} and head not in self.load(module)
             if builtin_container or any(m in ("typing", "collections.abc", "builtins") and n in supported for m, n in names):
-                return self.resolve(module, expression.slice, seen)
+                return self.resolve(module, expression.slice, seen, referenced_names)
             # Unknown generic semantics cannot prove contained field identity.
             return [], issues or [f"타입 컨테이너 출처/필드 의미 미해소: {head}"]
         else:
             nodes = []
         if nodes:
             identities, issues = [], []
             for node in nodes:
-                found, uncertain = self.resolve(module, node, seen)
+                found, uncertain = self.resolve(module, node, seen, referenced_names)
                 identities.extend(found)
                 issues.extend(uncertain)
             return identities, issues
         if not isinstance(expression, (ast.Name, ast.Attribute)):
             return [], [f"타입식 미지원: {ast.unparse(expression)}"]
         name = ast.unparse(expression)
+        if referenced_names is not None:
+            referenced_names.add(name)
         primitive = {"str", "int", "float", "bool", "bytes", "bytearray", "object", "None", "complex"}
         if name in primitive:
             return [], []
         key = (module, name)
         if key in seen:
             return [], [f"alias cycle: {module}.{name}"]
         seen = seen | {key}
         if isinstance(expression, ast.Attribute):
             pieces = name.split(".")
             table = self.load(module)
             root = table.get(pieces[0], [])
             if len(root) == 1 and isinstance(root[0], tuple):
                 origin, symbol = root[0]
                 qualified = [origin] + ([symbol] if symbol else []) + pieces[1:]
                 target = ".".join(qualified[:-1])
-                return self.identity(target, pieces[-1], seen)
+                return self.identity(target, pieces[-1], seen, referenced_names=referenced_names)
             if root:
                 return [], [f"qualified 타입 출처 중복/미해소: {name}"]
             if self._known_root(pieces[0]):
-                return self.identity(".".join(pieces[:-1]), pieces[-1], seen)
+                return self.identity(".".join(pieces[:-1]), pieces[-1], seen, referenced_names=referenced_names)
             return [], [f"qualified 타입 출처 미해소: {name}"]
-        return self.identity(module, name, seen, local=True)
+        return self.identity(module, name, seen, local=True, referenced_names=referenced_names)
 
     def _known_root(self, name: str) -> bool:
         return name in ("typing", "builtins", "collections") or _is_repo_target(self.copy, name, self.plan)
 
-    def identity(self, module: str, name: str, seen: frozenset[tuple[str, str]], local: bool = False
+    def identity(self, module: str, name: str, seen: frozenset[tuple[str, str]], local: bool = False,
+                 referenced_names: set[str] | None = None
                  ) -> tuple[list[tuple[str, str, ast.ClassDef | None]], list[str]]:
+        if referenced_names is not None:
+            referenced_names.add(name)
         values = self.load(module).get(name, [])
         if len(values) > 1 or values == [None]:
             return [], [f"타입 선언 중복/분기 불일치: {module}.{name}"]
         if values:
             value = values[0]
             if isinstance(value, ast.ClassDef):
                 return [(module, name, value)], []
             if isinstance(value, tuple):
                 origin, imported = value
                 if not imported:
                     return [], [f"모듈 자체는 필드 타입 미확정: {module}.{name}"]
                 key = (origin, imported)
                 if key in seen:
                     return [], [f"alias cycle: {origin}.{imported}"]
-                return self.identity(origin, imported, seen | {key})
+                return self.identity(origin, imported, seen | {key}, referenced_names=referenced_names)
             if isinstance(value, ast.expr):
-                return self.resolve(module, value, seen)
+                return self.resolve(module, value, seen, referenced_names)
             return [], [f"타입 출처 미해소: {module}.{name}"]
         if local:
             return [], [f"bare 타입 `{name}` 출처 미해소 — 명시 import/별칭 출처를 보완해 주세요"]
         # An explicit import/qualified module identity proves provenance; it does not prove existence.
         return [(module, name, None)], []
 
 
 def check_declarations(plan: Plan, copy: Path) -> list[DeclarationFinding]:
     """효과·DTO 명시 선언의 확정/후보 근거를 반환한다. 사본 파일을 변경하지 않는다."""
     types = _DeclarationTypes(plan, copy)
@@ -1706,23 +1718,24 @@
 
     for effect in plan.effects:
         if effect.effect == "read-only" and effect.uow != "none":
             add("#197", effect.path, effect.owner, f"read-only + uow={effect.uow} 명시 모순", True)
             continue
         module = types.module(effect.path)
         values = types.load(module).get(effect.owner, [])
         injected, unknown = [], []
         if len(values) == 1 and isinstance(values[0], ast.ClassDef):
             for annotation in annotations(values[0], True):
-                identities, issues = types.resolve(module, annotation)
+                referenced_names: set[str] = set()
+                identities, issues = types.resolve(module, annotation, referenced_names=referenced_names)
                 injected += [f"{m}.{n}" for m, n, _ in identities if ".application_layer.port.unit_of_work." in m + "."]
-                if "UnitOfWork" in ast.unparse(annotation):
+                if "UnitOfWork" in ast.unparse(annotation) or any("UnitOfWork" in name for name in referenced_names):
                     unknown += issues
         else:
             unknown.append("클래스 선언 중복/파싱 불가")
         if effect.effect == "read-only":
             if injected:
                 add("#197", effect.path, effect.owner, "read-only + uow=none에 명시 UoW port 주입: " + ", ".join(injected), True)
             elif unknown:
                 add("#197", effect.path, effect.owner, "; ".join(unknown), False)
         elif effect.uow == "none" and injected:
             note = f"채널 불일치(비차단): {effect.path}::{effect.owner} write/uow=none + 주입 {', '.join(injected)}"

```

## dddjango/scripts/registry_gate.py

Before SHA256: bcc7db98fe1f209f330d6c2ffb92239792580207f0d4bad317d6130fa60d273a
After SHA256: bcc7db98fe1f209f330d6c2ffb92239792580207f0d4bad317d6130fa60d273a

```diff

```

## dddjango/scripts/rulepack.json

Before SHA256: eca32486b4c7f9eda77e58c86e8b6a690289d80990037d714bb65088e477bb55
After SHA256: eca32486b4c7f9eda77e58c86e8b6a690289d80990037d714bb65088e477bb55

```diff

```

## dddjango/skills/discipline-houserules/SKILL.md

Before SHA256: 1c1fc1f8d1e39e9ebe246b91c71d4051ca4c442a3026f65092c3e42fa8f8dfce
After SHA256: 1c1fc1f8d1e39e9ebe246b91c71d4051ca4c442a3026f65092c3e42fa8f8dfce

```diff

```

## dddjango/skills/discipline-houserules/references/final.md

Before SHA256: 768db015552547977d941d638c54a90ff5922229d70e1cbe99e6558bdc47cde1
After SHA256: 768db015552547977d941d638c54a90ff5922229d70e1cbe99e6558bdc47cde1

```diff

```

## dddjango/skills/implementation-django-ninja/SKILL.md

Before SHA256: ee52e8f2556c873d824797ca90ac270cf344f57b0a59b04e036b2791bf579e67
After SHA256: ee52e8f2556c873d824797ca90ac270cf344f57b0a59b04e036b2791bf579e67

```diff

```

## dddjango/skills/implementation-django-ninja/references/final.md

Before SHA256: f6276de920006a6caf6c9eca74e23e81099e8a3a10ffb2fc829298eb339642f2
After SHA256: f6276de920006a6caf6c9eca74e23e81099e8a3a10ffb2fc829298eb339642f2

```diff

```

## docs/file_tree.html

Before SHA256: 62cefa2c055b9a02653f52c2fd5fc9e2615a0b8a02faba7602d82590bd314fe0
After SHA256: 62cefa2c055b9a02653f52c2fd5fc9e2615a0b8a02faba7602d82590bd314fe0

```diff

```

## docs/mkrev2.py

Before SHA256: 6192fe66215f6f38f87b279cfc9282adb30bb5c2c31716a82cfa492b6848491d
After SHA256: 6192fe66215f6f38f87b279cfc9282adb30bb5c2c31716a82cfa492b6848491d

```diff

```

## ontology/LEDGER.tsv

Before SHA256: 6697fe96cd028983be6c78125107a0af8ac74870626c0eb18b06dfa54bfcbf82
After SHA256: 6697fe96cd028983be6c78125107a0af8ac74870626c0eb18b06dfa54bfcbf82

```diff

```

## ontology/rules/agent-design-architect.ttl

Before SHA256: 9865c8f5787809d3e0cd6e5cdcb119b859d20615a524d7fde1322330a4213f0a
After SHA256: 9865c8f5787809d3e0cd6e5cdcb119b859d20615a524d7fde1322330a4213f0a

```diff

```

## ontology/rules/agent-design-review-api.ttl

Before SHA256: 59106ddea0462475988cbcfdd1839f06c5d1a6ef8f72e6a4730ee5f275a32ba7
After SHA256: 59106ddea0462475988cbcfdd1839f06c5d1a6ef8f72e6a4730ee5f275a32ba7

```diff

```

## ontology/rules/agent-discipline-reviewer.ttl

Before SHA256: f95d45237c92e1ea22f799327de15b88b08677c6a20f371769b42e0b0ad4479b
After SHA256: f95d45237c92e1ea22f799327de15b88b08677c6a20f371769b42e0b0ad4479b

```diff

```

## ontology/rules/command-dddjango.ttl

Before SHA256: 454d396ab85aa5fa52b7c6172f197abc9605afd99e96691f3d93661ec6ee1f27
After SHA256: 454d396ab85aa5fa52b7c6172f197abc9605afd99e96691f3d93661ec6ee1f27

```diff

```

## ontology/rules/discipline-houserules-final.ttl

Before SHA256: bb03b9469a1fcef876db4f1c31287c0c34cea9585aeeda45cea886268835306a
After SHA256: bb03b9469a1fcef876db4f1c31287c0c34cea9585aeeda45cea886268835306a

```diff

```

## ontology/rules/discipline-houserules-skill.ttl

Before SHA256: 9f05cfd377fd819ac9e7abed29aee1283e9c5d9afa9144a7e6a58ca5c43f8a6a
After SHA256: 9f05cfd377fd819ac9e7abed29aee1283e9c5d9afa9144a7e6a58ca5c43f8a6a

```diff

```

## ontology/rules/implementation-django-ninja-final.ttl

Before SHA256: b184ade4fccfa20554614d3460e2841ea800eb731ce54553d1f4adbf9d1339a9
After SHA256: b184ade4fccfa20554614d3460e2841ea800eb731ce54553d1f4adbf9d1339a9

```diff

```

## ontology/rules/implementation-django-ninja-skill.ttl

Before SHA256: 85fcd3471eeb56cecb0d99509941f44ed651c52bb2dda76ac549c7a057d6130a
After SHA256: 85fcd3471eeb56cecb0d99509941f44ed651c52bb2dda76ac549c7a057d6130a

```diff

```

## workspace/design/2026-08-08-tree-revision-spec.md

Before SHA256: 6558beb0ff00947a226751d2de9883f05d41e8b3cc8eeb2152c1af687aa1d375
After SHA256: 6558beb0ff00947a226751d2de9883f05d41e8b3cc8eeb2152c1af687aa1d375

```diff

```

## workspace/design/2026-08-11-predicates.md

Before SHA256: 2176d4e20b464ee7fa7f1f1c56431ac088d3d430f5ce51afd5e7bb8ad92c2ce0
After SHA256: 2176d4e20b464ee7fa7f1f1c56431ac088d3d430f5ce51afd5e7bb8ad92c2ce0

```diff

```

## workspace/plan/2026-08-11-rule-owner-map.md

Before SHA256: f059d7380d62a249d2c4922c2e432c8e723222ec7930226d92f89160b6d01317
After SHA256: f059d7380d62a249d2c4922c2e432c8e723222ec7930226d92f89160b6d01317

```diff

```

## workspace/tools/field_report_checker_smoke.py

Before SHA256: c3864f94a996ff8e345a7d35854d95219e0fad6ae94239b61052f116fd1b2ab2
After SHA256: c8b3eed3de9b63cb50dbc715dba123a55884a48ae3188fd6934739436bf7989b

```diff
--- before/workspace/tools/field_report_checker_smoke.py
+++ after/workspace/tools/field_report_checker_smoke.py
@@ -408,20 +408,63 @@
                 self.assertIn("#557", c)
 
     def admin_records(self, source):
         self.write("framework/admin/book.py", source)
         records = self.root / "findings.jsonl"
         records.unlink(missing_ok=True)
         run = subprocess.run([sys.executable, '-B', str(SCRIPTS / 'check-public-surface-annotation.py'),
                               str(self.root)], env=self.env, text=True, capture_output=True)
         self.assertIn(run.returncode, (0, 2), run.stdout + run.stderr)
         return [json.loads(line) for line in records.read_text().splitlines()] if records.exists() else []
+
+
+    def test_admin_kwargs_actual_consumption_and_unknown_escape(self):
+        prefix = ("from typing import Any\nfrom django.contrib.admin import ModelAdmin\n"
+                  "from django.http import HttpResponse\nclass BookAdmin(ModelAdmin):\n"
+                  "    def get_form(self, request: object, **kwargs: Any) -> HttpResponse:\n")
+        for body, expected in [
+            ("return super().get_form(request, **kwargs)", []),
+            ("...", []),
+            ("if kwargs['amount'] > 10:\n            charge(kwargs['amount'])\n        return super().get_form(request, **kwargs)", ['violation']),
+            ("options = kwargs\n        charge(options['amount'])\n        return super().get_form(request, **kwargs)", ['violation']),
+            ("unknown(kwargs)\n        return super().get_form(request, **kwargs)", ['info']),
+        ]:
+            with self.subTest(body=body):
+                rows = self.admin_records(prefix + '        ' + body + '\n')
+                self.assertEqual([r['severity'] for r in rows if r['rule'] == '#645'], expected, rows)
+                self.assertTrue(any(r['rule'] == '#646' for r in rows), rows)
+                self.assertFalse(any(r['rule'] == '#647' for r in rows), rows)
+        rows = self.admin_records(prefix + "        import json\n        decoded: dict[str, object] = json.loads(request.body)\n        return super().get_form(request, **kwargs)\n")
+        self.assertTrue(any(r['rule'] == '#650' for r in rows), rows)
+
+    def test_ohs_module_definitions_invalidate_imported_builder(self):
+        header = "from application.lesson.composition_root.books import build_read_use_case as _prepare\n"
+        for definition, expected in [
+            ('', False), ('def _prepare(): return cursor\n', True),
+            ('async def _prepare(): return cursor\n', True), ('class _prepare: pass\n', True),
+            ('def _unused():\n    def _prepare(): return cursor\n', False),
+            ('class _Unused:\n    class _prepare: pass\n', False),
+        ]:
+            with self.subTest(definition=definition):
+                f, c = self.ohs_rules(header + definition + 'def read_query(request):\n    _prepare().execute()\n')
+                self.assertNotIn('#153', f)
+                self.assertEqual('#153' in c, expected)
+
+    def test_uow_module_class_shadow_keeps_unknown_region_candidate(self):
+        body = "with uow:\n        books.save(a)\n    with uow:\n        loans.save(b)"
+        for header, expected in [('', False), ('class Work: pass\n', True),
+                                 ('class Other: pass\n', False),
+                                 ('def unused():\n    class Work: pass\n', False)]:
+            with self.subTest(header=header):
+                f, c = self.application_rules(body, header)
+                self.assertNotIn('#546', f)
+                self.assertEqual('#546' in c, expected)
 
     def test_admin_context_real_parler_helper_and_business_opposite(self):
         source = """from typing import Any
 from parler.admin import TranslatableAdmin
 class BookAdmin(TranslatableAdmin):
     def changeform_view(self, request: object, extra_context: dict[str, Any] | None = None) -> HttpResponse:
         return self._render_failed_submission(request, extra_context)
     def _render_failed_submission(self, request: object, extra_context: dict[str, Any] | None) -> HttpResponse:
         form = self.get_form(request)(request.POST)
         inline_instances = self.get_inline_instances(request)

```

## workspace/tools/pregate_field_report_smoke.py

Before SHA256: f50bbe33afb4e94becaedd9a6b548fa7c353eff38f4d5ce758ca3caeb8dcb809
After SHA256: ec2ec71b40f855587a93abac85e40091e944fa3a510a6c89f470a79c9cc56604

```diff
--- before/workspace/tools/pregate_field_report_smoke.py
+++ after/workspace/tools/pregate_field_report_smoke.py
@@ -854,13 +854,57 @@
                     with patch.dict(sys.modules, {'pytest': fake_pytest}):
                         exec(compile(original, TEST, 'exec'), namespace)
                     if mutation == 'pytestmark[0] = pytest.mark.django_db':
                         self.assertEqual(namespace['pytestmark'], ['django_db'])
                     _, report = self.materialize(spec_text([f'update {TEST}'], owner=f'{TEST} [markers: {markers}]'))
                     self.assertEqual((self.copy / TEST).read_bytes(), original.encode())
                     self.assertEqual((self.source / TEST).read_bytes(), original.encode())
                     self.assertEqual(report['materialized'], [])
                     self.assertTrue(any('S5' in note and 'subscript' in note for note in report['unsimulated']), report)
 
+    def test_marker_method_mutations_preserve_bytes_and_report_s5(self):
+        for mutation in ['pytestmark.append(pytest.mark.django_db)', 'pytestmark.pop()',
+                         'if True:\n    pytestmark.extend([pytest.mark.django_db])']:
+            for markers in ['', 'slow']:
+                with self.subTest(mutation=mutation, markers=markers):
+                    original = 'import pytest\npytestmark = [pytest.mark.slow]\n' + mutation + '\n'
+                    self.write(self.source, TEST, original)
+                    text = spec_text([f'update {TEST}'], owner=f'{TEST} [markers: {markers}]')
+                    _, report = self.materialize(text)
+                    self.assertEqual((self.copy / TEST).read_bytes(), original.encode())
+                    self.assertEqual((self.source / TEST).read_bytes(), original.encode())
+                    self.assertEqual(report['materialized'], [])
+                    self.assertTrue(any('S5' in note and 'method' in note for note in report['unsimulated']), report)
+        _git(self.source, 'add', '-A')
+        _git(self.source, 'commit', '-qm', 'synthetic marker mutation fixture')
+        run, report = self.cli(text)
+        self.assertEqual(run.returncode, 4, run.stdout + run.stderr)
+        self.assertIn('S5', report)
+        self.assertIn('method', report)
+        self.assertEqual(pg.check_report(text, report)[0], 0)
+        self.assertEqual((self.source / TEST).read_bytes(), original.encode())
+
+    def test_unresolved_named_uow_alias_keeps_declaration_candidate(self):
+        path = 'application/garden/application_layer/books/list_books/list_books_use_case.py'
+        for effect in ['read-only', 'write']:
+            for annotation, aliases, expected in [
+                ('StrangeUnitOfWork', [], [('#197', False)]),
+                ('U', ['alias U = StrangeUnitOfWork'], [('#197', False)]),
+                ('U', ['alias U = V', 'alias V = StrangeUnitOfWork'], [('#197', False)]),
+                ('U', ['alias U = list[StrangeUnitOfWork]'], [('#197', False)]),
+                ('U', ['alias U = P'], []),
+                ('U', ['alias U = int'], []),
+                ('U', ['alias U = StrangeUnitOfWork', 'StrangeUnitOfWork {value: int}'], []),
+            ]:
+                with self.subTest(effect=effect, aliases=aliases):
+                    text = self.effects(spec_text([f'update {path}'], [
+                        *[f'{path}::{alias}' for alias in aliases], f'{path}::ListBooks',
+                        f'{path}::ListBooks.__init__(self, uow: {annotation})']),
+                        f'{path}::ListBooks {effect} uow=none')
+                    plan, errors = pg.parse_spec(text)
+                    self.assertEqual(errors, [])
+                    found = pg.check_declarations(plan, self.source)
+                    self.assertEqual([(f.rule, f.confirmed) for f in found], expected if effect == 'read-only' else [])
+
 
 if __name__ == "__main__":
     unittest.main(verbosity=2)

```

## workspace/tools/pregate_fixture_run.py

Before SHA256: 29a1aa46ea7a8979c04230fc8afb2adc31745eecde2b059abd7edb3578e43539
After SHA256: 29a1aa46ea7a8979c04230fc8afb2adc31745eecde2b059abd7edb3578e43539

```diff

```

## workspace/tools/registry_gate_smoke.py

Before SHA256: ff22017079c33a4b568720b7f28e6a7cee909de3cb5e65309d9167447804ce7c
After SHA256: ff22017079c33a4b568720b7f28e6a7cee909de3cb5e65309d9167447804ce7c

```diff

```
