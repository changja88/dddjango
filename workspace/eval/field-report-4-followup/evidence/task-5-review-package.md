# task-5 review package

No commit was authorized. This package compares owned-file snapshots before this task with current bytes.

## dddjango/scripts/checker_target.py

Before SHA256: b2798af6c552e98c384d2c445ba358deed81d10d71021a1e3348b2d1f1fe2ea6
After SHA256: 2efb7adbe792ddf4fadc9527699bb130ef1953481acdff70ad01e469ebdd0112

```diff
--- before/dddjango/scripts/checker_target.py
+++ after/dddjango/scripts/checker_target.py
@@ -15,25 +15,54 @@
 근거)을 만들었다. 27종 전부가 이 모듈을 거치므로 여기 한 곳이 직접 실행
 채널까지 봉인한다. fixture 는 pyproject 가 없어 게이트 무발화(판정 무변).
 
 이 모듈은 수기 소유다(standard_tree.py 는 tree_mirror_check --write 가 전체
 재생성하는 기계 사본이라 여기 두지 않는다).
 """
 from __future__ import annotations
 
 import ast
 import re
+import stat
 import sys
 import fnmatch
 from pathlib import Path
 
 _BC_LAYER_DIRS: "tuple[str, ...]" = ("domain_layer", "application_layer", "driving_layer", "driven_layer")
+
+
+def cache_only_instance(path: Path) -> bool:
+    """실파일 없이 __pycache__ 아래 캐시만 남은 선택 인스턴스인가.
+
+    빈 디렉터리는 허용하지만 캐시 파일 하나는 필요하다. 링크·읽기 불능은
+    제외 근거가 아니므로 False로 남긴다. Git 추적 상태는 사용하지 않는다.
+    """
+    found = False
+    pending = [(path, False)]
+    try:
+        while pending:
+            current, in_cache = pending.pop()
+            mode = current.lstat().st_mode
+            if stat.S_ISLNK(mode):
+                return False
+            if stat.S_ISDIR(mode):
+                cached = in_cache or current.name == "__pycache__"
+                pending.extend((child, cached) for child in current.iterdir())
+            elif stat.S_ISREG(mode) and in_cache and current.suffix in (".pyc", ".pyo"):
+                with current.open("rb") as stream:
+                    stream.read(1)
+                found = True
+            else:
+                return False
+    except OSError:
+        return False
+    return found
 
 
 def skeleton_placeholder(path: Path) -> bool:
     """빈 골격 파일인가 — docstring 밖 문장이 0개(0바이트·공백·주석-only·docstring-only).
 
     표준 트리가 자리만 요구해 만들어 둔 파일은 aggregate·구현 의무의 대상이 아니다
     (판정 ④ 2026-08-25 — #256·#351 이 이 술어로 건너뛴다). 의미는 #114 렌더 계약의
     `_skeleton_placeholder_module`(check-error-centralization — 그쪽은 root 상대 경로
     서명이라 별도 실체)과 같다. `pass` 등 문장이 실재하거나 읽기·파싱 불능이면
     placeholder 가 아니다(fail-closed — 기존 진단 유지).

```

## codex-dddjango/skills/dddjango/scripts/checker_target.py

Before SHA256: b2798af6c552e98c384d2c445ba358deed81d10d71021a1e3348b2d1f1fe2ea6
After SHA256: 2efb7adbe792ddf4fadc9527699bb130ef1953481acdff70ad01e469ebdd0112

```diff
--- before/codex-dddjango/skills/dddjango/scripts/checker_target.py
+++ after/codex-dddjango/skills/dddjango/scripts/checker_target.py
@@ -15,25 +15,54 @@
 근거)을 만들었다. 27종 전부가 이 모듈을 거치므로 여기 한 곳이 직접 실행
 채널까지 봉인한다. fixture 는 pyproject 가 없어 게이트 무발화(판정 무변).
 
 이 모듈은 수기 소유다(standard_tree.py 는 tree_mirror_check --write 가 전체
 재생성하는 기계 사본이라 여기 두지 않는다).
 """
 from __future__ import annotations
 
 import ast
 import re
+import stat
 import sys
 import fnmatch
 from pathlib import Path
 
 _BC_LAYER_DIRS: "tuple[str, ...]" = ("domain_layer", "application_layer", "driving_layer", "driven_layer")
+
+
+def cache_only_instance(path: Path) -> bool:
+    """실파일 없이 __pycache__ 아래 캐시만 남은 선택 인스턴스인가.
+
+    빈 디렉터리는 허용하지만 캐시 파일 하나는 필요하다. 링크·읽기 불능은
+    제외 근거가 아니므로 False로 남긴다. Git 추적 상태는 사용하지 않는다.
+    """
+    found = False
+    pending = [(path, False)]
+    try:
+        while pending:
+            current, in_cache = pending.pop()
+            mode = current.lstat().st_mode
+            if stat.S_ISLNK(mode):
+                return False
+            if stat.S_ISDIR(mode):
+                cached = in_cache or current.name == "__pycache__"
+                pending.extend((child, cached) for child in current.iterdir())
+            elif stat.S_ISREG(mode) and in_cache and current.suffix in (".pyc", ".pyo"):
+                with current.open("rb") as stream:
+                    stream.read(1)
+                found = True
+            else:
+                return False
+    except OSError:
+        return False
+    return found
 
 
 def skeleton_placeholder(path: Path) -> bool:
     """빈 골격 파일인가 — docstring 밖 문장이 0개(0바이트·공백·주석-only·docstring-only).
 
     표준 트리가 자리만 요구해 만들어 둔 파일은 aggregate·구현 의무의 대상이 아니다
     (판정 ④ 2026-08-25 — #256·#351 이 이 술어로 건너뛴다). 의미는 #114 렌더 계약의
     `_skeleton_placeholder_module`(check-error-centralization — 그쪽은 root 상대 경로
     서명이라 별도 실체)과 같다. `pass` 등 문장이 실재하거나 읽기·파싱 불능이면
     placeholder 가 아니다(fail-closed — 기존 진단 유지).

```

## dddjango/scripts/check-layer-skeleton.py

Before SHA256: f2bdf8e26f9e48462e434f1a5f917643de8f46165081dfe603558fa37318e0eb
After SHA256: 9f2ea08ec409ed8e52340067685b3a828235b68d35347903cf09492f5355a645

```diff
--- before/dddjango/scripts/check-layer-skeleton.py
+++ after/dddjango/scripts/check-layer-skeleton.py
@@ -85,21 +85,20 @@
     )
     return has_layer or has_marker
 
 
 # ── 동명 폴더 승격(#490 교체형) — #638~#643 + ⓓ#644 ─────────────────────────
 
 # ⓓ#644 행위 칸 로스터 — 승격 허용 표기(swappable) 중 schema 4행(14·15·20·21) 제외
 # (houserules SKILL §1 감사 주도 배정 — 신호는 무조건 방출, 판정 의무의 diff 한정은 감사자 몫)
 PROMO_ACTION_ROWS = frozenset({12, 18, 24, 41, 61, 74, 92, 94, 96})
 PROMO_SIGNAL_LINES = 200   # ⓓ#644 후보 문턱(물리 행·빈 줄 제외)
-PROMO_PART_MIN_LINES = 50  # #642 부품 출생 하한
 JUNK_DRAWER_NAMES = frozenset({"utils.py", "helpers.py", "util.py", "helper.py", "common.py", "misc.py"})
 _CASCADE_Q = "역할 밖 응집 단위가 있는가 — ①이동/②동명 폴더 승격/③유지 (houserules §1 캐스케이드)"
 
 
 def _phys_lines(path: Path) -> int:
     try:
         text = path.read_text(encoding="utf-8")
     except (UnicodeDecodeError, OSError):
         return 0
     return sum(1 for line in text.splitlines() if line.strip())
@@ -138,22 +137,20 @@
     elif not _init_reexport_only(init):
         out.add("#640", init, "`__init__.py` 는 재수출 전용이다 — from-as 재수출·`__all__`·docstring 밖 코드 동거 금지")
     subdirs, files = _entries(dir_path)
     for sd in subdirs:
         out.add("#641", sd, "승격 폴더 내부는 1단 평평이다 — 부품 군집의 폴더 요구는 트리 개정 신호이지 중첩 근거가 아니다")
     parts = [f for f in files if f.name not in ("__init__.py", dir_path.name + ".py")]
     for f in parts:
         if f.name in JUNK_DRAWER_NAMES:
             out.add("#640", f, "승격 폴더 안 정크드로어 이름 — 부품은 응집 단위의 이름을 가진다")
         n = _phys_lines(f)
-        if n < PROMO_PART_MIN_LINES:
-            out.add("#642", f, f"부품 {n}행 — 출생 하한 50행 미만(신규 여부는 게이트 앵커 차분이 가른다 · 기존분은 잔존 보고)")
         if crow.r in PROMO_ACTION_ROWS and n > PROMO_SIGNAL_LINES:
             cand.add("#644", f, f"행위 칸 승격 부품 {n}행(>{PROMO_SIGNAL_LINES}) — 캐스케이드 판정 의무 (트리 {crow.r}행)", _CASCADE_Q)
     if body.is_file():
         if not parts:
             out.add("#643", dir_path, "부품 0개(본체+`__init__.py` 뿐)인 승격 폴더 — 환원 신호(파일 실현으로 되돌린다)")
         if crow.r in PROMO_ACTION_ROWS:
             n = _phys_lines(body)
             if n > PROMO_SIGNAL_LINES:
                 cand.add("#644", body, f"행위 칸 실현 {n}행(>{PROMO_SIGNAL_LINES}) — 캐스케이드 판정 의무 (트리 {crow.r}행)", _CASCADE_Q)
 
@@ -270,20 +267,23 @@
             if getattr(kan_row, "swappable", False):
                 if (dir_path / (p.name + ".py")).is_file():
                     out.add("#639", p, f"형제 `{p.name}.py` 와 승격 폴더의 공존 — import 는 패키지가 이겨 조용한 위장 중복이다")
                 _check_promoted(p, kan_row, out, cand)
             else:
                 out.add("#490", p, f"승격 배제 칸의 동명 폴더 — 이 칸은 파일 실현만 갖는다 (트리 {kan_row.r}행)")
             continue
         if dir_placeholder is not None:
             inst_bind = dict(bindings)
             pattern = dir_placeholder.name.rstrip("/")
+            if (not pattern.endswith("_adapter") or _file_pattern_ok(p.name, pattern)) \
+                    and checker_target.cache_only_instance(p):
+                continue
             if pattern.endswith("_adapter"):
                 if not _file_pattern_ok(p.name, pattern):
                     out.add("#490", p, "어댑터 패키지 이름은 `<이름>_adapter/` 다")
                     continue
                 if not (p / "__init__.py").is_file():
                     out.add("#488", p / "__init__.py", "어댑터 패키지에 `__init__.py` 가 없다")
             for tok in set(TOKEN.findall(dir_placeholder.name)):
                 inst_bind[tok] = p.name.removesuffix("_adapter") if pattern.endswith("_adapter") else p.name
             _check_level(p, dir_placeholder, inst_bind, out, cand)
         elif p.name == "commands" and dir_path.name == "management":

```

## codex-dddjango/skills/dddjango/scripts/check-layer-skeleton.py

Before SHA256: f2bdf8e26f9e48462e434f1a5f917643de8f46165081dfe603558fa37318e0eb
After SHA256: 9f2ea08ec409ed8e52340067685b3a828235b68d35347903cf09492f5355a645

```diff
--- before/codex-dddjango/skills/dddjango/scripts/check-layer-skeleton.py
+++ after/codex-dddjango/skills/dddjango/scripts/check-layer-skeleton.py
@@ -85,21 +85,20 @@
     )
     return has_layer or has_marker
 
 
 # ── 동명 폴더 승격(#490 교체형) — #638~#643 + ⓓ#644 ─────────────────────────
 
 # ⓓ#644 행위 칸 로스터 — 승격 허용 표기(swappable) 중 schema 4행(14·15·20·21) 제외
 # (houserules SKILL §1 감사 주도 배정 — 신호는 무조건 방출, 판정 의무의 diff 한정은 감사자 몫)
 PROMO_ACTION_ROWS = frozenset({12, 18, 24, 41, 61, 74, 92, 94, 96})
 PROMO_SIGNAL_LINES = 200   # ⓓ#644 후보 문턱(물리 행·빈 줄 제외)
-PROMO_PART_MIN_LINES = 50  # #642 부품 출생 하한
 JUNK_DRAWER_NAMES = frozenset({"utils.py", "helpers.py", "util.py", "helper.py", "common.py", "misc.py"})
 _CASCADE_Q = "역할 밖 응집 단위가 있는가 — ①이동/②동명 폴더 승격/③유지 (houserules §1 캐스케이드)"
 
 
 def _phys_lines(path: Path) -> int:
     try:
         text = path.read_text(encoding="utf-8")
     except (UnicodeDecodeError, OSError):
         return 0
     return sum(1 for line in text.splitlines() if line.strip())
@@ -138,22 +137,20 @@
     elif not _init_reexport_only(init):
         out.add("#640", init, "`__init__.py` 는 재수출 전용이다 — from-as 재수출·`__all__`·docstring 밖 코드 동거 금지")
     subdirs, files = _entries(dir_path)
     for sd in subdirs:
         out.add("#641", sd, "승격 폴더 내부는 1단 평평이다 — 부품 군집의 폴더 요구는 트리 개정 신호이지 중첩 근거가 아니다")
     parts = [f for f in files if f.name not in ("__init__.py", dir_path.name + ".py")]
     for f in parts:
         if f.name in JUNK_DRAWER_NAMES:
             out.add("#640", f, "승격 폴더 안 정크드로어 이름 — 부품은 응집 단위의 이름을 가진다")
         n = _phys_lines(f)
-        if n < PROMO_PART_MIN_LINES:
-            out.add("#642", f, f"부품 {n}행 — 출생 하한 50행 미만(신규 여부는 게이트 앵커 차분이 가른다 · 기존분은 잔존 보고)")
         if crow.r in PROMO_ACTION_ROWS and n > PROMO_SIGNAL_LINES:
             cand.add("#644", f, f"행위 칸 승격 부품 {n}행(>{PROMO_SIGNAL_LINES}) — 캐스케이드 판정 의무 (트리 {crow.r}행)", _CASCADE_Q)
     if body.is_file():
         if not parts:
             out.add("#643", dir_path, "부품 0개(본체+`__init__.py` 뿐)인 승격 폴더 — 환원 신호(파일 실현으로 되돌린다)")
         if crow.r in PROMO_ACTION_ROWS:
             n = _phys_lines(body)
             if n > PROMO_SIGNAL_LINES:
                 cand.add("#644", body, f"행위 칸 실현 {n}행(>{PROMO_SIGNAL_LINES}) — 캐스케이드 판정 의무 (트리 {crow.r}행)", _CASCADE_Q)
 
@@ -270,20 +267,23 @@
             if getattr(kan_row, "swappable", False):
                 if (dir_path / (p.name + ".py")).is_file():
                     out.add("#639", p, f"형제 `{p.name}.py` 와 승격 폴더의 공존 — import 는 패키지가 이겨 조용한 위장 중복이다")
                 _check_promoted(p, kan_row, out, cand)
             else:
                 out.add("#490", p, f"승격 배제 칸의 동명 폴더 — 이 칸은 파일 실현만 갖는다 (트리 {kan_row.r}행)")
             continue
         if dir_placeholder is not None:
             inst_bind = dict(bindings)
             pattern = dir_placeholder.name.rstrip("/")
+            if (not pattern.endswith("_adapter") or _file_pattern_ok(p.name, pattern)) \
+                    and checker_target.cache_only_instance(p):
+                continue
             if pattern.endswith("_adapter"):
                 if not _file_pattern_ok(p.name, pattern):
                     out.add("#490", p, "어댑터 패키지 이름은 `<이름>_adapter/` 다")
                     continue
                 if not (p / "__init__.py").is_file():
                     out.add("#488", p / "__init__.py", "어댑터 패키지에 `__init__.py` 가 없다")
             for tok in set(TOKEN.findall(dir_placeholder.name)):
                 inst_bind[tok] = p.name.removesuffix("_adapter") if pattern.endswith("_adapter") else p.name
             _check_level(p, dir_placeholder, inst_bind, out, cand)
         elif p.name == "commands" and dir_path.name == "management":

```

## dddjango/scripts/check-port-adapter-pairing.py

Before SHA256: 16d0ef643ec7f7514b79a4f680d065071c080443fc5e43d3f380896649fd979e
After SHA256: b6bcf57161a163e072fd9fb18a47bd11f1122ef2792ffc0d1f48a1cc215c522a

```diff
--- before/dddjango/scripts/check-port-adapter-pairing.py
+++ after/dddjango/scripts/check-port-adapter-pairing.py
@@ -178,21 +178,21 @@
             if py.stem.endswith("_unit_of_work") and "unit_of_work" not in parts:
                 f.add("#240", _rel(root, py),
                       "UnitOfWork 선언이 port/unit_of_work/ 밖에 있다")
     if not port.is_dir():
         return
     for p in sorted(port.iterdir()):
         if p.is_file() and p.suffix == ".py" and p.name != "__init__.py":
             f.add("#215", _rel(root, p),
                   "port/ 직계 파일 — 능력 하나 = 폴더 하나다(포트를 파일 하나로 두지 않는다)")
     for cap in sorted(p for p in port.iterdir() if p.is_dir() and p.name != "__pycache__"):
-        if cap.name in ("domain_bypass_query", "unit_of_work"):
+        if cap.name in ("domain_bypass_query", "unit_of_work") or checker_target.cache_only_instance(cap):
             continue
         _check_capability_folder(root, bc, cap, bc_vocab_set, tech, f, cand)
     bypass = port / "domain_bypass_query"
     if bypass.is_dir():
         _check_bypass(root, bypass, tech, f, cand)
     uow = port / "unit_of_work"
     if uow.is_dir():
         _check_uow_port(root, uow, f)
 
 
@@ -308,20 +308,22 @@
                      "이 자료를 원시값 인자로 «펴서» 넘길 수 있나")
 
 
 # ── domain_bypass_query — #229~#239 · #465 ─────────────────────────────────
 
 def _check_bypass(root: Path, bypass: Path, tech: set, f: Findings, cand: Candidates) -> None:
     for p in sorted(bypass.iterdir()):
         if p.is_file() and p.suffix == ".py" and p.name != "__init__.py":
             f.add("#232", _rel(root, p), "domain_bypass_query/ 직계 파일 — 능력 하나 = 폴더 하나다")
     for cap in sorted(p for p in bypass.iterdir() if p.is_dir() and p.name != "__pycache__"):
+        if checker_target.cache_only_instance(cap):
+            continue
         toks = set(cap.name.split("_"))
         if toks & (TECH_EXACT | vocab.bc_names(root)):
             f.add("#233", _rel(root, cap),
                   f"`{cap.name}/` — 「무엇을 알고 싶은가」로 짓고 «누가 주는지»는 이름에 넣지 않는다")
         elif "_" not in cap.name:
             cand.add("#233", _rel(root, cap), f"`{cap.name}/` 이 명사 하나뿐이다",
                      "Q1 — 무엇을 알고 싶은가가 이름에 있나")
         expected = f"{cap.name}_query.py"
         queries = list(cap.glob("*_query.py"))
         if not (cap / expected).is_file() or len(queries) > 1:
@@ -697,21 +699,22 @@
         for missing in sorted(decl_stems - impl_stems):
             f.add("#351", _rel(root, repo_dir),
                   f"선언 `{missing}.py` 의 구현이 없다 — 선언마다 구현이 «정확히 하나» 있다")
         for orphan in sorted(impl_stems - decl_stems):
             f.add("#351", _rel(root, repo_dir / f"{orphan}.py"),
                   "선언 없는 리포지토리 구현 — 1:1 은 양방향이다(#583)")
     # persistence/domain_bypass_query — #356 · #359 · #583.
     thin = persistence / "domain_bypass_query"
     port_bypass = bc / "application_layer" / "port" / "domain_bypass_query"
     if thin.is_dir():
-        contract_caps = {p.name for p in port_bypass.iterdir() if p.is_dir()} \
+        contract_caps = {p.name for p in port_bypass.iterdir() if p.is_dir()
+                         and p.name != "__pycache__" and not checker_target.cache_only_instance(p)} \
             if port_bypass.is_dir() else set()
         for py in checker_target.slot_glob(thin, "*_query.py"):
             capname = py.stem[: -len("_query")]
             if contract_caps and capname not in contract_caps:
                 f.add("#583", _rel(root, py),
                       "계약 없는 Thin Read 구현 — repository·unit_of_work·domain_bypass_query "
                       "셋은 1:1 이 «양방향»이다")
             mod = _parse(py)
             if mod is None:
                 continue
@@ -872,56 +875,61 @@
         if target_mod is None:
             return False
         if not any(isinstance(s, ast.ClassDef) and s.name == symbol for s in target_mod.body):
             return False
     return True
 
 
 def _check_adapter_families(root: Path, bc: Path, adapter: Path, agg_names: set,
                             bc_vocab_set: set, f: Findings, cand: Candidates) -> None:
     for bundle in sorted(adapter.rglob("*_adapter")):
-        if not bundle.is_dir() or not checker_target.adapter_bundle(bundle):
+        if not bundle.is_dir() or not checker_target.adapter_bundle(bundle) \
+                or checker_target.cache_only_instance(bundle):
             continue
         for role in checker_target.ADAPTER_ROLES:
             for py in sorted((bundle / role).glob("*.py")):
                 if py.name == "__init__.py" or checker_target.skeleton_placeholder(py):
                     continue
                 mod = _parse(py)
                 if mod is None:
                     continue
                 classes = [n for n in ast.walk(mod) if isinstance(n, ast.ClassDef)]
                 if (role == "constant" and classes) or (role != "constant" and len(classes) != 1):
                     f.add("#651", _rel(root, py),
                           "어댑터 역할 파일은 클래스 하나당 파일 하나다(비공개 포함); constant 파일에는 상수를 둔다")
     acl = adapter / "anticorruption_layer"
     if acl.is_dir():
         bcs = vocab.bc_names(root)
         for d in sorted(p for p in acl.iterdir() if p.is_dir() and p.name != "__pycache__"):
+            if checker_target.cache_only_instance(d):
+                continue
             if d.name not in bcs:
                 # 스펙 대장 #365 부칙(2026-08-25) — «우리 BC»는 병렬 워크트리 개발로 이
                 # 스냅숏에 없는 자사 BC 를 포함한다. 대상 부재 시 구조 순수성(통신 축
                 # import 0 — 자기 BC·framework·비통신 stdlib 뿐)이면 후보로 강등하고,
                 # 통신 축이 하나라도 있으면 위반 유지(외부 시스템의 ACL 위장 차단).
                 if _acl_target_pure(root, bc, d):
                     cand.add("#365", _rel(root, d),
                              f"acl/{d.name}/ — 이 스냅숏에 없는 대상(순수 스텁 — 통신 import 0)",
                              "병렬 워크트리에서 개발 중인 «우리 BC»인가, 외부 시스템인가")
                 else:
                     f.add("#365", _rel(root, d),
                           f"acl/{d.name}/ — 우리가 못 고치고 계약이 저장소 밖인 상대는 "
                           "external_system/ 이다(anticorruption_layer 는 «우리 다른 BC» 전용)")
     ext = adapter / "external_system"
     if ext.is_dir():
         for p in sorted(ext.iterdir()):
             if p.is_file() and p.suffix == ".py" and p.name != "__init__.py":
                 f.add("#369", _rel(root, p), "external_system/ 직계 파일 — 벤더 하나 = 폴더 하나다")
         for system in sorted(p for p in ext.iterdir() if p.is_dir() and p.name != "__pycache__"):
+            if checker_target.cache_only_instance(system):
+                continue
             for py in checker_target.adapter_implementations(system):
                 if py.name == "__init__.py":
                     continue
                 mod = _parse(py)
                 if mod is None:
                     continue
                 for cls in [n for n in mod.body if isinstance(n, ast.ClassDef) and not n.name.startswith("_")]:
                     if not (cls.name.endswith("Adapter") and cls.name.startswith(_camel(system.name))):
                         f.add("#370", _rel(root, py, cls.lineno),
                               f"`{cls.name}` — 바깥 시스템 어댑터는 `<System><Capability>Adapter` 다")

```

## codex-dddjango/skills/dddjango/scripts/check-port-adapter-pairing.py

Before SHA256: 16d0ef643ec7f7514b79a4f680d065071c080443fc5e43d3f380896649fd979e
After SHA256: b6bcf57161a163e072fd9fb18a47bd11f1122ef2792ffc0d1f48a1cc215c522a

```diff
--- before/codex-dddjango/skills/dddjango/scripts/check-port-adapter-pairing.py
+++ after/codex-dddjango/skills/dddjango/scripts/check-port-adapter-pairing.py
@@ -178,21 +178,21 @@
             if py.stem.endswith("_unit_of_work") and "unit_of_work" not in parts:
                 f.add("#240", _rel(root, py),
                       "UnitOfWork 선언이 port/unit_of_work/ 밖에 있다")
     if not port.is_dir():
         return
     for p in sorted(port.iterdir()):
         if p.is_file() and p.suffix == ".py" and p.name != "__init__.py":
             f.add("#215", _rel(root, p),
                   "port/ 직계 파일 — 능력 하나 = 폴더 하나다(포트를 파일 하나로 두지 않는다)")
     for cap in sorted(p for p in port.iterdir() if p.is_dir() and p.name != "__pycache__"):
-        if cap.name in ("domain_bypass_query", "unit_of_work"):
+        if cap.name in ("domain_bypass_query", "unit_of_work") or checker_target.cache_only_instance(cap):
             continue
         _check_capability_folder(root, bc, cap, bc_vocab_set, tech, f, cand)
     bypass = port / "domain_bypass_query"
     if bypass.is_dir():
         _check_bypass(root, bypass, tech, f, cand)
     uow = port / "unit_of_work"
     if uow.is_dir():
         _check_uow_port(root, uow, f)
 
 
@@ -308,20 +308,22 @@
                      "이 자료를 원시값 인자로 «펴서» 넘길 수 있나")
 
 
 # ── domain_bypass_query — #229~#239 · #465 ─────────────────────────────────
 
 def _check_bypass(root: Path, bypass: Path, tech: set, f: Findings, cand: Candidates) -> None:
     for p in sorted(bypass.iterdir()):
         if p.is_file() and p.suffix == ".py" and p.name != "__init__.py":
             f.add("#232", _rel(root, p), "domain_bypass_query/ 직계 파일 — 능력 하나 = 폴더 하나다")
     for cap in sorted(p for p in bypass.iterdir() if p.is_dir() and p.name != "__pycache__"):
+        if checker_target.cache_only_instance(cap):
+            continue
         toks = set(cap.name.split("_"))
         if toks & (TECH_EXACT | vocab.bc_names(root)):
             f.add("#233", _rel(root, cap),
                   f"`{cap.name}/` — 「무엇을 알고 싶은가」로 짓고 «누가 주는지»는 이름에 넣지 않는다")
         elif "_" not in cap.name:
             cand.add("#233", _rel(root, cap), f"`{cap.name}/` 이 명사 하나뿐이다",
                      "Q1 — 무엇을 알고 싶은가가 이름에 있나")
         expected = f"{cap.name}_query.py"
         queries = list(cap.glob("*_query.py"))
         if not (cap / expected).is_file() or len(queries) > 1:
@@ -697,21 +699,22 @@
         for missing in sorted(decl_stems - impl_stems):
             f.add("#351", _rel(root, repo_dir),
                   f"선언 `{missing}.py` 의 구현이 없다 — 선언마다 구현이 «정확히 하나» 있다")
         for orphan in sorted(impl_stems - decl_stems):
             f.add("#351", _rel(root, repo_dir / f"{orphan}.py"),
                   "선언 없는 리포지토리 구현 — 1:1 은 양방향이다(#583)")
     # persistence/domain_bypass_query — #356 · #359 · #583.
     thin = persistence / "domain_bypass_query"
     port_bypass = bc / "application_layer" / "port" / "domain_bypass_query"
     if thin.is_dir():
-        contract_caps = {p.name for p in port_bypass.iterdir() if p.is_dir()} \
+        contract_caps = {p.name for p in port_bypass.iterdir() if p.is_dir()
+                         and p.name != "__pycache__" and not checker_target.cache_only_instance(p)} \
             if port_bypass.is_dir() else set()
         for py in checker_target.slot_glob(thin, "*_query.py"):
             capname = py.stem[: -len("_query")]
             if contract_caps and capname not in contract_caps:
                 f.add("#583", _rel(root, py),
                       "계약 없는 Thin Read 구현 — repository·unit_of_work·domain_bypass_query "
                       "셋은 1:1 이 «양방향»이다")
             mod = _parse(py)
             if mod is None:
                 continue
@@ -872,56 +875,61 @@
         if target_mod is None:
             return False
         if not any(isinstance(s, ast.ClassDef) and s.name == symbol for s in target_mod.body):
             return False
     return True
 
 
 def _check_adapter_families(root: Path, bc: Path, adapter: Path, agg_names: set,
                             bc_vocab_set: set, f: Findings, cand: Candidates) -> None:
     for bundle in sorted(adapter.rglob("*_adapter")):
-        if not bundle.is_dir() or not checker_target.adapter_bundle(bundle):
+        if not bundle.is_dir() or not checker_target.adapter_bundle(bundle) \
+                or checker_target.cache_only_instance(bundle):
             continue
         for role in checker_target.ADAPTER_ROLES:
             for py in sorted((bundle / role).glob("*.py")):
                 if py.name == "__init__.py" or checker_target.skeleton_placeholder(py):
                     continue
                 mod = _parse(py)
                 if mod is None:
                     continue
                 classes = [n for n in ast.walk(mod) if isinstance(n, ast.ClassDef)]
                 if (role == "constant" and classes) or (role != "constant" and len(classes) != 1):
                     f.add("#651", _rel(root, py),
                           "어댑터 역할 파일은 클래스 하나당 파일 하나다(비공개 포함); constant 파일에는 상수를 둔다")
     acl = adapter / "anticorruption_layer"
     if acl.is_dir():
         bcs = vocab.bc_names(root)
         for d in sorted(p for p in acl.iterdir() if p.is_dir() and p.name != "__pycache__"):
+            if checker_target.cache_only_instance(d):
+                continue
             if d.name not in bcs:
                 # 스펙 대장 #365 부칙(2026-08-25) — «우리 BC»는 병렬 워크트리 개발로 이
                 # 스냅숏에 없는 자사 BC 를 포함한다. 대상 부재 시 구조 순수성(통신 축
                 # import 0 — 자기 BC·framework·비통신 stdlib 뿐)이면 후보로 강등하고,
                 # 통신 축이 하나라도 있으면 위반 유지(외부 시스템의 ACL 위장 차단).
                 if _acl_target_pure(root, bc, d):
                     cand.add("#365", _rel(root, d),
                              f"acl/{d.name}/ — 이 스냅숏에 없는 대상(순수 스텁 — 통신 import 0)",
                              "병렬 워크트리에서 개발 중인 «우리 BC»인가, 외부 시스템인가")
                 else:
                     f.add("#365", _rel(root, d),
                           f"acl/{d.name}/ — 우리가 못 고치고 계약이 저장소 밖인 상대는 "
                           "external_system/ 이다(anticorruption_layer 는 «우리 다른 BC» 전용)")
     ext = adapter / "external_system"
     if ext.is_dir():
         for p in sorted(ext.iterdir()):
             if p.is_file() and p.suffix == ".py" and p.name != "__init__.py":
                 f.add("#369", _rel(root, p), "external_system/ 직계 파일 — 벤더 하나 = 폴더 하나다")
         for system in sorted(p for p in ext.iterdir() if p.is_dir() and p.name != "__pycache__"):
+            if checker_target.cache_only_instance(system):
+                continue
             for py in checker_target.adapter_implementations(system):
                 if py.name == "__init__.py":
                     continue
                 mod = _parse(py)
                 if mod is None:
                     continue
                 for cls in [n for n in mod.body if isinstance(n, ast.ClassDef) and not n.name.startswith("_")]:
                     if not (cls.name.endswith("Adapter") and cls.name.startswith(_camel(system.name))):
                         f.add("#370", _rel(root, py, cls.lineno),
                               f"`{cls.name}` — 바깥 시스템 어댑터는 `<System><Capability>Adapter` 다")

```

## dddjango/scripts/check-domain-model.py

Before SHA256: 3da1f13672f5da6fd73c1284152939b1239f57202fe00eb2d07aa3d68b50a9ac
After SHA256: d789b50b2fa78caa5ae73892e042d5a721ca2b5e85459233c9ea92bd354527cc

```diff
--- before/dddjango/scripts/check-domain-model.py
+++ after/dddjango/scripts/check-domain-model.py
@@ -164,21 +164,22 @@
                 out |= _ann_names(ast.parse(n.value, mode="eval").body)
             except SyntaxError:
                 pass
     return out
 
 
 # ── 층 구조 — #249 · #252 · #17/#18 · #289 · #290 · #300 · #459 · #315 ─────
 
 def _aggregate_dirs(domain: Path) -> list[Path]:
     return [p for p in sorted(domain.iterdir())
-            if p.is_dir() and p.name not in DOMAIN_FIXED and p.name != "__pycache__"]
+            if p.is_dir() and p.name not in DOMAIN_FIXED and p.name != "__pycache__"
+            and not checker_target.cache_only_instance(p)]
 
 
 def _check_layout(root: Path, bc: Path, f: Findings, cand: Candidates) -> None:
     domain = bc / "domain_layer"
     app = bc / "application_layer"
     if domain.is_dir():
         for p in sorted(domain.iterdir()):
             if p.is_file() and p.suffix == ".py" and p.name != "__init__.py":
                 f.add("#249", _rel(root, p),
                       "domain_layer 직계 파일 — 자식은 애그리거트 폴더와 shared_value_object/·"
@@ -210,21 +211,21 @@
                           "shared_value_object/ 하위 폴더 — 파일 규칙은 애그리거트 안 값 객체와 "
                           "똑같고 다른 것은 «사는 폴더»뿐이다")
             _check_shared_imports(root, bc, shared, f)
             for py in sorted(shared.glob("*.py")):
                 _check_value_object_file(root, py, f, cand)
         ds = domain / "domain_service"
         if ds.is_dir():
             _check_domain_services(root, bc, ds, f, cand)
     if app.is_dir():
         for d in sorted(p for p in app.iterdir() if p.is_dir() and p.name != "__pycache__"):
-            if d.name == "port":
+            if d.name == "port" or checker_target.cache_only_instance(d):
                 continue
             if d.name in KIND_DENY:
                 f.add("#17", _rel(root, d),
                       f"application_layer 1차 `{d.name}/` — 1차 축은 도메인 이름(<area>/)이다")
             elif d.name in KIND_SOFT:
                 cand.add("#17", _rel(root, d), f"종류 인접 낱말 `{d.name}/`",
                          "Q1 — 이 이름이 업무의 낱말인가")
 
 
 # ── 애그리거트 한 폴더 — #256 · #260~#276 · #289 · #290 · #300 · #315 · #543 ──

```

## codex-dddjango/skills/dddjango/scripts/check-domain-model.py

Before SHA256: 3da1f13672f5da6fd73c1284152939b1239f57202fe00eb2d07aa3d68b50a9ac
After SHA256: d789b50b2fa78caa5ae73892e042d5a721ca2b5e85459233c9ea92bd354527cc

```diff
--- before/codex-dddjango/skills/dddjango/scripts/check-domain-model.py
+++ after/codex-dddjango/skills/dddjango/scripts/check-domain-model.py
@@ -164,21 +164,22 @@
                 out |= _ann_names(ast.parse(n.value, mode="eval").body)
             except SyntaxError:
                 pass
     return out
 
 
 # ── 층 구조 — #249 · #252 · #17/#18 · #289 · #290 · #300 · #459 · #315 ─────
 
 def _aggregate_dirs(domain: Path) -> list[Path]:
     return [p for p in sorted(domain.iterdir())
-            if p.is_dir() and p.name not in DOMAIN_FIXED and p.name != "__pycache__"]
+            if p.is_dir() and p.name not in DOMAIN_FIXED and p.name != "__pycache__"
+            and not checker_target.cache_only_instance(p)]
 
 
 def _check_layout(root: Path, bc: Path, f: Findings, cand: Candidates) -> None:
     domain = bc / "domain_layer"
     app = bc / "application_layer"
     if domain.is_dir():
         for p in sorted(domain.iterdir()):
             if p.is_file() and p.suffix == ".py" and p.name != "__init__.py":
                 f.add("#249", _rel(root, p),
                       "domain_layer 직계 파일 — 자식은 애그리거트 폴더와 shared_value_object/·"
@@ -210,21 +211,21 @@
                           "shared_value_object/ 하위 폴더 — 파일 규칙은 애그리거트 안 값 객체와 "
                           "똑같고 다른 것은 «사는 폴더»뿐이다")
             _check_shared_imports(root, bc, shared, f)
             for py in sorted(shared.glob("*.py")):
                 _check_value_object_file(root, py, f, cand)
         ds = domain / "domain_service"
         if ds.is_dir():
             _check_domain_services(root, bc, ds, f, cand)
     if app.is_dir():
         for d in sorted(p for p in app.iterdir() if p.is_dir() and p.name != "__pycache__"):
-            if d.name == "port":
+            if d.name == "port" or checker_target.cache_only_instance(d):
                 continue
             if d.name in KIND_DENY:
                 f.add("#17", _rel(root, d),
                       f"application_layer 1차 `{d.name}/` — 1차 축은 도메인 이름(<area>/)이다")
             elif d.name in KIND_SOFT:
                 cand.add("#17", _rel(root, d), f"종류 인접 낱말 `{d.name}/`",
                          "Q1 — 이 이름이 업무의 낱말인가")
 
 
 # ── 애그리거트 한 폴더 — #256 · #260~#276 · #289 · #290 · #300 · #315 · #543 ──

```

## dddjango/scripts/check-usecase-dto-placement.py

Before SHA256: e2fec2b3edb3f740e34a16013b08bf717b8ac7a29d75ad009b5735ceee2ae6d6
After SHA256: dc80a76963f3dd912ef9696173312be2ad0a7612f0006b725bdbff1148a0455b

```diff
--- before/dddjango/scripts/check-usecase-dto-placement.py
+++ after/dddjango/scripts/check-usecase-dto-placement.py
@@ -276,63 +276,68 @@
 
 def _check_structure(root: Path, bc: Path, bc_rel: Path, out: Findings) -> list[Path]:
     """구조 규칙 검사 후 <use_case>/ 폴더 목록을 돌려준다."""
     app = _app_layer(bc)
     if app is None:
         return []
     rel = bc_rel / app.name
     dirs, _ = _entries(app)
     areas: list[Path] = []
     for p in dirs:
-        if p.name == "port":
+        if p.name == "port" or checker_target.cache_only_instance(p):
             continue
         if p.name in KIND_FOLDER_NAMES:
             out.add("#182", rel / p.name, "`application_layer/` 직계는 `<area>/`·`port/` 둘뿐이다 — 종류 폴더는 자리가 없다(`domain_bypass_query/`·`unit_of_work/` 는 `port/` 안이다)")
         else:
             areas.append(p)
 
     for p in app.rglob("*"):
         if set(p.relative_to(app).parts) & SKIP_DIRS:
             continue
         if p.is_dir() and p.name in ("validation", "validators"):
             out.add("#183", rel / p.relative_to(app), "`application_layer/` 아래에 `validation/` 폴더를 두지 않는다 — 검사 자리는 입구(schema_in)와 도메인 둘뿐이다")
         elif p.is_file() and p.name.endswith("_validation.py"):
             out.add("#183", rel / p.relative_to(app), "`*_validation.py` 를 두지 않는다 — 검사 자리는 입구(schema_in)와 도메인 둘뿐이다")
 
     api = _driving_api(bc)
     if api is not None and _has_concrete_api_surface(root, api, bc.name):
         api_dirs, _ = _entries(api)
-        api_areas = {p.name for p in api_dirs if p.name != "webhook"}
+        api_areas = {p.name for p in api_dirs if p.name != "webhook"
+                     and not checker_target.cache_only_instance(p)}
         app_areas = {p.name for p in areas}
         for name in sorted(app_areas - api_areas):
             out.add("#188", rel / name, f"`<area>` 는 `driving_layer/api/<area>` 와 1:1 이다 — api 쪽에 `{name}/` 이 없다")
         for name in sorted(api_areas - app_areas):
             out.add("#188", bc_rel / api.relative_to(bc) / name, f"`<area>` 는 `application_layer/<area>` 와 1:1 이다 — application_layer 쪽에 `{name}/` 이 없다")
 
     ucs: list[Path] = []
     for area in areas:
         a_dirs, _ = _entries(area)
         for p in a_dirs:
+            if checker_target.cache_only_instance(p):
+                continue
             if p.name in KIND_FOLDER_NAMES:
                 out.add("#192", rel / area.name / p.name, "절차 조각은 `<use_case>_use_case.py` 안 `_` 사설 함수로 둔다 — `service/` 같은 종류 폴더를 만들지 않는다")
             else:
                 ucs.append(p)
     return ucs
 
 
 # ── <use_case>/ — #190 · #193 · #201 · #569 · #570 · #571 · #635 · #211 ────
 
 def _top_public_classes(mod: ast.Module) -> list[ast.ClassDef]:
     return [n for n in mod.body if isinstance(n, ast.ClassDef) and not n.name.startswith("_")]
 
 
 def _check_use_case(uc: Path, uc_rel: Path, agg_names: set[str], out: Findings, cand: Candidates) -> None:
+    if checker_target.cache_only_instance(uc):
+        return
     name = uc.name
     dirs, files = _entries(uc)
 
     for d in dirs:
         if d.name == "dto":
             out.add("#201", uc_rel / d.name, "유스케이스 자료는 세 파일(`_command`·`_query`·`_result`)이다 — `dto/` 겹을 만들지 않는다")
 
     entry_name = f"{name}_use_case.py"
     # 진입점 칸의 실현은 파일 또는 동명 폴더 승격(#490 교체형)의 본체다 — slot_file 이 판독한다.
     entry = checker_target.slot_file(uc / entry_name)

```

## codex-dddjango/skills/dddjango/scripts/check-usecase-dto-placement.py

Before SHA256: e2fec2b3edb3f740e34a16013b08bf717b8ac7a29d75ad009b5735ceee2ae6d6
After SHA256: dc80a76963f3dd912ef9696173312be2ad0a7612f0006b725bdbff1148a0455b

```diff
--- before/codex-dddjango/skills/dddjango/scripts/check-usecase-dto-placement.py
+++ after/codex-dddjango/skills/dddjango/scripts/check-usecase-dto-placement.py
@@ -276,63 +276,68 @@
 
 def _check_structure(root: Path, bc: Path, bc_rel: Path, out: Findings) -> list[Path]:
     """구조 규칙 검사 후 <use_case>/ 폴더 목록을 돌려준다."""
     app = _app_layer(bc)
     if app is None:
         return []
     rel = bc_rel / app.name
     dirs, _ = _entries(app)
     areas: list[Path] = []
     for p in dirs:
-        if p.name == "port":
+        if p.name == "port" or checker_target.cache_only_instance(p):
             continue
         if p.name in KIND_FOLDER_NAMES:
             out.add("#182", rel / p.name, "`application_layer/` 직계는 `<area>/`·`port/` 둘뿐이다 — 종류 폴더는 자리가 없다(`domain_bypass_query/`·`unit_of_work/` 는 `port/` 안이다)")
         else:
             areas.append(p)
 
     for p in app.rglob("*"):
         if set(p.relative_to(app).parts) & SKIP_DIRS:
             continue
         if p.is_dir() and p.name in ("validation", "validators"):
             out.add("#183", rel / p.relative_to(app), "`application_layer/` 아래에 `validation/` 폴더를 두지 않는다 — 검사 자리는 입구(schema_in)와 도메인 둘뿐이다")
         elif p.is_file() and p.name.endswith("_validation.py"):
             out.add("#183", rel / p.relative_to(app), "`*_validation.py` 를 두지 않는다 — 검사 자리는 입구(schema_in)와 도메인 둘뿐이다")
 
     api = _driving_api(bc)
     if api is not None and _has_concrete_api_surface(root, api, bc.name):
         api_dirs, _ = _entries(api)
-        api_areas = {p.name for p in api_dirs if p.name != "webhook"}
+        api_areas = {p.name for p in api_dirs if p.name != "webhook"
+                     and not checker_target.cache_only_instance(p)}
         app_areas = {p.name for p in areas}
         for name in sorted(app_areas - api_areas):
             out.add("#188", rel / name, f"`<area>` 는 `driving_layer/api/<area>` 와 1:1 이다 — api 쪽에 `{name}/` 이 없다")
         for name in sorted(api_areas - app_areas):
             out.add("#188", bc_rel / api.relative_to(bc) / name, f"`<area>` 는 `application_layer/<area>` 와 1:1 이다 — application_layer 쪽에 `{name}/` 이 없다")
 
     ucs: list[Path] = []
     for area in areas:
         a_dirs, _ = _entries(area)
         for p in a_dirs:
+            if checker_target.cache_only_instance(p):
+                continue
             if p.name in KIND_FOLDER_NAMES:
                 out.add("#192", rel / area.name / p.name, "절차 조각은 `<use_case>_use_case.py` 안 `_` 사설 함수로 둔다 — `service/` 같은 종류 폴더를 만들지 않는다")
             else:
                 ucs.append(p)
     return ucs
 
 
 # ── <use_case>/ — #190 · #193 · #201 · #569 · #570 · #571 · #635 · #211 ────
 
 def _top_public_classes(mod: ast.Module) -> list[ast.ClassDef]:
     return [n for n in mod.body if isinstance(n, ast.ClassDef) and not n.name.startswith("_")]
 
 
 def _check_use_case(uc: Path, uc_rel: Path, agg_names: set[str], out: Findings, cand: Candidates) -> None:
+    if checker_target.cache_only_instance(uc):
+        return
     name = uc.name
     dirs, files = _entries(uc)
 
     for d in dirs:
         if d.name == "dto":
             out.add("#201", uc_rel / d.name, "유스케이스 자료는 세 파일(`_command`·`_query`·`_result`)이다 — `dto/` 겹을 만들지 않는다")
 
     entry_name = f"{name}_use_case.py"
     # 진입점 칸의 실현은 파일 또는 동명 폴더 승격(#490 교체형)의 본체다 — slot_file 이 판독한다.
     entry = checker_target.slot_file(uc / entry_name)

```

## dddjango/scripts/check-context-isolation.py

Before SHA256: 5c64e9f1b0a0ccbde4e918a0660d6fd40e8f442e45138bd1e0e85208e42750dd
After SHA256: 8c9afbf7931975c16a023152865c3a8246e7beece36217cc4e98383437dbfc4d

```diff
--- before/dddjango/scripts/check-context-isolation.py
+++ after/dddjango/scripts/check-context-isolation.py
@@ -343,20 +343,22 @@
 
 def _check_ohs(ohs: Path, bc: Path, bc_rel: Path, agg_names: set[str], all_bcs: set[str],
                out: Findings, cand: Candidates) -> None:
     rel0 = bc_rel / ohs.relative_to(bc)
     dirs, files = _entries(ohs)
     for f in files:
         if f.name != "__init__.py":
             out.add("#150", rel0 / f.name, "`open_host_service/` 의 1차 축은 `<service>/` 폴더다 — 평면 `.py` 를 두지 않는다")
 
     for svc in dirs:
+        if checker_target.cache_only_instance(svc):
+            continue
         srel = rel0 / svc.name
         tokens = set(svc.name.split("_"))
         if tokens & TECH_NAME_TOKENS or tokens & (all_bcs - {bc.name}):
             out.add("#151", srel, "창구 이름은 「무엇을 해 주는가」로 짓는다 — 기술·타 BC 이름 토큰이 들어 있다")
         elif svc.name.removesuffix("_service") in agg_names or svc.name in agg_names:
             cand.add("#151", srel, f"창구 이름 `{svc.name}` 이 애그리거트 이름과 같다", "Q1(이 이름이 «무엇을 해 주는가»를 말하나)")
 
         entry_name = f"{svc.name}_service.py"
         # 진입점 칸은 동명 폴더 승격 가능 — entry 는 실현(파일 또는 `<svc>_service/` 본체)이다.
         entry = checker_target.slot_file(svc / entry_name)

```

## codex-dddjango/skills/dddjango/scripts/check-context-isolation.py

Before SHA256: 5c64e9f1b0a0ccbde4e918a0660d6fd40e8f442e45138bd1e0e85208e42750dd
After SHA256: 8c9afbf7931975c16a023152865c3a8246e7beece36217cc4e98383437dbfc4d

```diff
--- before/codex-dddjango/skills/dddjango/scripts/check-context-isolation.py
+++ after/codex-dddjango/skills/dddjango/scripts/check-context-isolation.py
@@ -343,20 +343,22 @@
 
 def _check_ohs(ohs: Path, bc: Path, bc_rel: Path, agg_names: set[str], all_bcs: set[str],
                out: Findings, cand: Candidates) -> None:
     rel0 = bc_rel / ohs.relative_to(bc)
     dirs, files = _entries(ohs)
     for f in files:
         if f.name != "__init__.py":
             out.add("#150", rel0 / f.name, "`open_host_service/` 의 1차 축은 `<service>/` 폴더다 — 평면 `.py` 를 두지 않는다")
 
     for svc in dirs:
+        if checker_target.cache_only_instance(svc):
+            continue
         srel = rel0 / svc.name
         tokens = set(svc.name.split("_"))
         if tokens & TECH_NAME_TOKENS or tokens & (all_bcs - {bc.name}):
             out.add("#151", srel, "창구 이름은 「무엇을 해 주는가」로 짓는다 — 기술·타 BC 이름 토큰이 들어 있다")
         elif svc.name.removesuffix("_service") in agg_names or svc.name in agg_names:
             cand.add("#151", srel, f"창구 이름 `{svc.name}` 이 애그리거트 이름과 같다", "Q1(이 이름이 «무엇을 해 주는가»를 말하나)")
 
         entry_name = f"{svc.name}_service.py"
         # 진입점 칸은 동명 폴더 승격 가능 — entry 는 실현(파일 또는 `<svc>_service/` 본체)이다.
         entry = checker_target.slot_file(svc / entry_name)

```

## dddjango/scripts/registry_gate.py

Before SHA256: 037b5088bd0884b9e41efedd6455fec95a80c1e0527b4ef09405ab041a9450df
After SHA256: bcc7db98fe1f209f330d6c2ffb92239792580207f0d4bad317d6130fa60d273a

```diff
--- before/dddjango/scripts/registry_gate.py
+++ after/dddjango/scripts/registry_gate.py
@@ -84,20 +84,21 @@
 import subprocess
 import sys
 import tempfile
 from dataclasses import dataclass, field
 from pathlib import Path
 
 _SCRIPTS_DIR: Path = Path(__file__).resolve().parent
 sys.path.insert(0, str(_SCRIPTS_DIR))
 import anchor_diff  # noqa: E402  — git·앵커 스냅숏·빚 로더·빚 매칭 공용(복제 통합)
 import checker_target  # noqa: E402
+import standard_tree as tree  # noqa: E402
 import findings  # noqa: E402  — sink 환경변수 이름·라인 재구성 문법의 단일 출처
 from checker_registry import REGISTRY, checker_argv  # noqa: E402
 
 _FINDING_RE: "re.Pattern[str]" = re.compile(r"^\s*(\[#\d+\].*)$")
 _CANDIDATE_RE: "re.Pattern[str]" = re.compile(r"^\s*(\[ⓓ#\d+\].*)$")  # ⓓ 후보 — 앵커 차분만(exit 불산입)
 _LINENO_RE: "re.Pattern[str]" = re.compile(r":\d+")
 _IGNORE_COPY: "tuple[str, ...]" = (
     ".git", ".venv", "venv", "__pycache__", "*.pyc", "node_modules",
     "graphify-out", ".mypy_cache", ".pytest_cache", ".ruff_cache", "staticfiles",
     # F-C(2026-08-14): 숨김 디렉터리 전부 = 도구·하네스 영역(`.codex/`·`.dddjango/` 등) —
@@ -108,23 +109,77 @@
 
 class _UsageParser(argparse.ArgumentParser):
     """usage 오류를 문면 계약(exit 1)으로 — argparse 기본 exit 2 는 «위반»과 겹친다
     (check-composition-root `_UsageParser` 패턴 이식)."""
 
     def error(self, message: str) -> None:
         print(f"사용 오류: {message}", file=sys.stderr)
         raise SystemExit(1)
 
 
+def _snapshot_cache_instances(root: Path) -> set[Path]:
+    """골격의 BC 내부 선택 폴더 칸만 원 작업 트리에서 수집한다."""
+    omitted: set[Path] = set()
+    token = re.compile(r"<([a-z_]+)>")
+
+    def walk(directory: Path, row: tree.Row, bindings: dict[str, str]) -> None:
+        if directory.is_symlink() or not directory.is_dir():
+            return
+        children = tree.children(row)
+        fixed = {tree.concrete_name(c, bindings).rstrip("/"): c for c in children
+                 if tree.is_dir(c) and c.kind in ("fixed", "reappear")}
+        optional = next((c for c in children if tree.is_dir(c) and c.kind == "placeholder"
+                         and "/" not in c.name.rstrip("/")), None)
+        files = [tree.concrete_name(c, bindings) for c in children if not tree.is_dir(c)]
+        for child in sorted(directory.iterdir()):
+            if not child.is_dir() or child.is_symlink() or child.name.startswith(".") or child.name == "__pycache__":
+                continue
+            if child.name in fixed:
+                walk(child, fixed[child.name], bindings)
+                continue
+            # 파일의 승격 실현은 선택 폴더 인스턴스가 아니다.
+            if any(re.fullmatch(token.sub(".+", name), child.name + ".py") for name in files):
+                continue
+            if optional is None:
+                continue
+            pattern = optional.name.rstrip("/")
+            if not re.fullmatch(token.sub(".+", pattern), child.name):
+                continue
+            if checker_target.cache_only_instance(child):
+                omitted.add(child.relative_to(root))
+                continue
+            values = dict(bindings)
+            for name in token.findall(pattern):
+                values[name] = child.name.removesuffix("_adapter") if pattern.endswith("_adapter") else child.name
+            walk(child, optional, values)
+
+    ignore = shutil.ignore_patterns(*_IGNORE_COPY)
+    for application in sorted(root.rglob("application")):
+        if not application.is_dir() or application.is_symlink() \
+                or ignore(str(root), list(application.relative_to(root).parts)):
+            continue
+        for bc in sorted(application.iterdir()):
+            if not bc.name.startswith("."):
+                walk(bc, tree.ROWS[0], {"bounded_context": bc.name})
+    return omitted
+
+
 def _snapshot_current(root: Path, dest: Path) -> None:
     """working tree 를 비-git 사본으로 복사한다(무거운 비-소스 디렉터리 제외)."""
-    shutil.copytree(root, dest, ignore=shutil.ignore_patterns(*_IGNORE_COPY))
+    omitted = _snapshot_cache_instances(root)
+    ignore = shutil.ignore_patterns(*_IGNORE_COPY)
+
+    def ignore_current(directory: str, names: list[str]) -> set[str]:
+        parent = Path(directory).relative_to(root)
+        return ignore(directory, names) | {name for name in names if parent / name in omitted}
+
+    shutil.copytree(root, dest, ignore=ignore_current)
 
 
 def _parse_fail_findings(target: Path) -> "set[str]":
     """이 인터프리터로 파싱 불가한 검사 대상 — fail-open(침묵 스킵) 방지 합성 귀속(F-A 2026-08-14).
 
     앵커·현재 «양쪽» 스냅숏에 같은 스캔을 걸어 차분 원리를 태운다 — 앵커에도 있던
     깨진 파일은 legacy(L∩N), 새로 생긴 것만 귀속(N∖L). 고의 투입으로 red 를
     «판정 불능(exit 1)»으로 바꾸는 우회(적대 리뷰 A1)가 성립하지 않는다.
     """
     out: "set[str]" = set()

```

## codex-dddjango/skills/dddjango/scripts/registry_gate.py

Before SHA256: 037b5088bd0884b9e41efedd6455fec95a80c1e0527b4ef09405ab041a9450df
After SHA256: bcc7db98fe1f209f330d6c2ffb92239792580207f0d4bad317d6130fa60d273a

```diff
--- before/codex-dddjango/skills/dddjango/scripts/registry_gate.py
+++ after/codex-dddjango/skills/dddjango/scripts/registry_gate.py
@@ -84,20 +84,21 @@
 import subprocess
 import sys
 import tempfile
 from dataclasses import dataclass, field
 from pathlib import Path
 
 _SCRIPTS_DIR: Path = Path(__file__).resolve().parent
 sys.path.insert(0, str(_SCRIPTS_DIR))
 import anchor_diff  # noqa: E402  — git·앵커 스냅숏·빚 로더·빚 매칭 공용(복제 통합)
 import checker_target  # noqa: E402
+import standard_tree as tree  # noqa: E402
 import findings  # noqa: E402  — sink 환경변수 이름·라인 재구성 문법의 단일 출처
 from checker_registry import REGISTRY, checker_argv  # noqa: E402
 
 _FINDING_RE: "re.Pattern[str]" = re.compile(r"^\s*(\[#\d+\].*)$")
 _CANDIDATE_RE: "re.Pattern[str]" = re.compile(r"^\s*(\[ⓓ#\d+\].*)$")  # ⓓ 후보 — 앵커 차분만(exit 불산입)
 _LINENO_RE: "re.Pattern[str]" = re.compile(r":\d+")
 _IGNORE_COPY: "tuple[str, ...]" = (
     ".git", ".venv", "venv", "__pycache__", "*.pyc", "node_modules",
     "graphify-out", ".mypy_cache", ".pytest_cache", ".ruff_cache", "staticfiles",
     # F-C(2026-08-14): 숨김 디렉터리 전부 = 도구·하네스 영역(`.codex/`·`.dddjango/` 등) —
@@ -108,23 +109,77 @@
 
 class _UsageParser(argparse.ArgumentParser):
     """usage 오류를 문면 계약(exit 1)으로 — argparse 기본 exit 2 는 «위반»과 겹친다
     (check-composition-root `_UsageParser` 패턴 이식)."""
 
     def error(self, message: str) -> None:
         print(f"사용 오류: {message}", file=sys.stderr)
         raise SystemExit(1)
 
 
+def _snapshot_cache_instances(root: Path) -> set[Path]:
+    """골격의 BC 내부 선택 폴더 칸만 원 작업 트리에서 수집한다."""
+    omitted: set[Path] = set()
+    token = re.compile(r"<([a-z_]+)>")
+
+    def walk(directory: Path, row: tree.Row, bindings: dict[str, str]) -> None:
+        if directory.is_symlink() or not directory.is_dir():
+            return
+        children = tree.children(row)
+        fixed = {tree.concrete_name(c, bindings).rstrip("/"): c for c in children
+                 if tree.is_dir(c) and c.kind in ("fixed", "reappear")}
+        optional = next((c for c in children if tree.is_dir(c) and c.kind == "placeholder"
+                         and "/" not in c.name.rstrip("/")), None)
+        files = [tree.concrete_name(c, bindings) for c in children if not tree.is_dir(c)]
+        for child in sorted(directory.iterdir()):
+            if not child.is_dir() or child.is_symlink() or child.name.startswith(".") or child.name == "__pycache__":
+                continue
+            if child.name in fixed:
+                walk(child, fixed[child.name], bindings)
+                continue
+            # 파일의 승격 실현은 선택 폴더 인스턴스가 아니다.
+            if any(re.fullmatch(token.sub(".+", name), child.name + ".py") for name in files):
+                continue
+            if optional is None:
+                continue
+            pattern = optional.name.rstrip("/")
+            if not re.fullmatch(token.sub(".+", pattern), child.name):
+                continue
+            if checker_target.cache_only_instance(child):
+                omitted.add(child.relative_to(root))
+                continue
+            values = dict(bindings)
+            for name in token.findall(pattern):
+                values[name] = child.name.removesuffix("_adapter") if pattern.endswith("_adapter") else child.name
+            walk(child, optional, values)
+
+    ignore = shutil.ignore_patterns(*_IGNORE_COPY)
+    for application in sorted(root.rglob("application")):
+        if not application.is_dir() or application.is_symlink() \
+                or ignore(str(root), list(application.relative_to(root).parts)):
+            continue
+        for bc in sorted(application.iterdir()):
+            if not bc.name.startswith("."):
+                walk(bc, tree.ROWS[0], {"bounded_context": bc.name})
+    return omitted
+
+
 def _snapshot_current(root: Path, dest: Path) -> None:
     """working tree 를 비-git 사본으로 복사한다(무거운 비-소스 디렉터리 제외)."""
-    shutil.copytree(root, dest, ignore=shutil.ignore_patterns(*_IGNORE_COPY))
+    omitted = _snapshot_cache_instances(root)
+    ignore = shutil.ignore_patterns(*_IGNORE_COPY)
+
+    def ignore_current(directory: str, names: list[str]) -> set[str]:
+        parent = Path(directory).relative_to(root)
+        return ignore(directory, names) | {name for name in names if parent / name in omitted}
+
+    shutil.copytree(root, dest, ignore=ignore_current)
 
 
 def _parse_fail_findings(target: Path) -> "set[str]":
     """이 인터프리터로 파싱 불가한 검사 대상 — fail-open(침묵 스킵) 방지 합성 귀속(F-A 2026-08-14).
 
     앵커·현재 «양쪽» 스냅숏에 같은 스캔을 걸어 차분 원리를 태운다 — 앵커에도 있던
     깨진 파일은 legacy(L∩N), 새로 생긴 것만 귀속(N∖L). 고의 투입으로 red 를
     «판정 불능(exit 1)»으로 바꾸는 우회(적대 리뷰 A1)가 성립하지 않는다.
     """
     out: "set[str]" = set()

```

## workspace/tools/field_report_checker_smoke.py

Before SHA256: 5a4e2a86620ecba82372bd310322b4917df660bf0e4cb870237746a38b54546a
After SHA256: f17cb80d86db51f5e6122d72a4364651648189933b576b285cc21ecceab79cb6

```diff
--- before/workspace/tools/field_report_checker_smoke.py
+++ after/workspace/tools/field_report_checker_smoke.py
@@ -631,20 +631,139 @@
         with patch.object(controller, "_run", return_value=([issue], [finding])), \
                 patch.object(controller.anchor_diff, "partition_exit") as partition, \
                 patch.dict(os.environ, self.env), contextlib.redirect_stdout(io.StringIO()), \
                 contextlib.redirect_stderr(io.StringIO()) as stderr:
             code = controller.main(["checker", str(self.root), *SELECTORS, "--anchor-baseline"])
         self.assertEqual(code, 1)
         self.assertIn(issue, stderr.getvalue())
         partition.assert_not_called()
 
 
+class CacheInstanceRegression(unittest.TestCase):
+    def setUp(self):
+        self.tmp = tempfile.TemporaryDirectory(prefix="field-cache-")
+        self.addCleanup(self.tmp.cleanup)
+        self.root = Path(self.tmp.name) / "project"
+        shutil.copytree(FIXTURES / "skeleton/good_bc", self.root)
+        self.env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1",
+                        DJR_FINDINGS_JSON=str(Path(self.tmp.name) / "records.jsonl"),
+                        DJR_VIOLATIONS_DIR=str(Path(self.tmp.name) / "violations"))
+
+    def plant(self, relative, extra=None):
+        path = self.root / relative
+        (path / "nested/__pycache__").mkdir(parents=True, exist_ok=True)
+        (path / "nested/__pycache__/old.cpython-314.pyc").write_bytes(b"cache")
+        (path / "empty").mkdir(exist_ok=True)
+        if extra is not None:
+            (path / extra).write_text("", encoding="utf-8")
+        return path
+
+    def run_checker(self, script):
+        result = subprocess.run([sys.executable, "-B", str(SCRIPTS / script), str(self.root)],
+                                capture_output=True, text=True, env=self.env)
+        self.assertIn(result.returncode, (0, 2), result.stdout + result.stderr)
+        return result.stdout + result.stderr
+
+    def test_cache_predicate_requires_cache_and_rejects_actual_files_links_and_read_errors(self):
+        import checker_target
+        predicate = checker_target.cache_only_instance
+        path = self.plant("scratch")
+        self.assertTrue(predicate(path))
+        (path / "nested").rename(path / "deep")
+        self.assertTrue(predicate(path))
+        direct = self.root / "direct/__pycache__"
+        direct.mkdir(parents=True)
+        self.assertFalse(predicate(direct.parent))
+        (direct / "cached.pyc").write_bytes(b"cache")
+        self.assertTrue(predicate(direct.parent))
+        (direct / "real.py").write_text("pass\n")
+        self.assertFalse(predicate(direct.parent))
+        for extra in ("real.py", "__init__.py", ".hidden", "notes.txt", "loose.pyc"):
+            with self.subTest(extra=extra):
+                (path / extra).write_bytes(b"")
+                self.assertFalse(predicate(path))
+                (path / extra).unlink()
+        for name in ("link", "__pycache__/linked.pyc"):
+            link = path / name
+            link.parent.mkdir(exist_ok=True)
+            link.symlink_to(path / "deep")
+            self.assertFalse(predicate(path))
+            link.unlink()
+        with patch.object(Path, "iterdir", side_effect=PermissionError("denied")):
+            self.assertFalse(predicate(path))
+        with patch.object(Path, "open", side_effect=PermissionError("denied")):
+            self.assertFalse(predicate(path))
+        empty = self.root / "empty_only/nested"
+        empty.mkdir(parents=True)
+        self.assertFalse(predicate(empty.parent))
+        self.assertFalse(predicate(self.root / "missing"))
+
+    def test_optional_instances_skip_only_cache_and_keep_real_and_empty_diagnostics(self):
+        cases = [
+            ("domain_layer/vanished", "check-domain-model.py", ("#299", "#256")),
+            ("application_layer/order/vanished", "check-usecase-dto-placement.py", ("#193", "#570", "#569")),
+            ("driving_layer/open_host_service/vanished", "check-context-isolation.py", ("#152",)),
+            ("application_layer/port/vanished", "check-port-adapter-pairing.py", ("#218", "#225")),
+            ("application_layer/port/domain_bypass_query/vanished", "check-port-adapter-pairing.py", ("#234", "#238")),
+            ("driven_layer/adapter/email_sender/vanished_adapter", "check-layer-skeleton.py", ("#488",)),
+        ]
+        for relative, script, rules in cases:
+            path = self.plant("application/orders/" + relative)
+            for extra in (None, "__init__.py", "source.py", ".hidden"):
+                with self.subTest(slot=relative, extra=extra):
+                    if extra:
+                        (path / extra).write_text("pass\n" if extra == "source.py" else "")
+                    output = self.run_checker(script)
+                    hits = [line for line in output.splitlines() if "vanished" in line]
+                    for rule in rules:
+                        self.assertEqual(any(rule in line for line in hits), extra is not None, output)
+                    if extra:
+                        (path / extra).unlink()
+            shutil.rmtree(path)
+            path.mkdir()
+            output = self.run_checker(script)
+            for rule in rules:
+                self.assertTrue(any(rule in line and "vanished" in line for line in output.splitlines()), output)
+            shutil.rmtree(path)
+
+    def test_cache_cannot_hide_fixed_skeleton_and_promoted_parts_have_no_floor(self):
+        fixed = self.root / "application/orders/application_layer/port/unit_of_work"
+        shutil.rmtree(fixed)
+        self.plant(str(fixed.relative_to(self.root)))
+        output = self.run_checker("check-layer-skeleton.py")
+        self.assertTrue(any("#488" in line and "unit_of_work" in line for line in output.splitlines()), output)
+        shutil.rmtree(self.root)
+        shutil.copytree(FIXTURES / "skeleton/good_promoted", self.root)
+        promoted = self.root / "application/orders/driving_layer/api/order/order_controller"
+        part = promoted / "order_sse_renderer.py"
+        for lines in (1, 49, 201):
+            part.write_text("pass\n" * lines)
+            output = self.run_checker("check-layer-skeleton.py")
+            self.assertNotIn("#642", output)
+            self.assertEqual(any("#644" in line and "order_sse_renderer.py" in line for line in output.splitlines()), lines == 201, output)
+        part.unlink()
+        self.assertIn("#643", self.run_checker("check-layer-skeleton.py"))
+        part.write_text("pass\n")
+        for change, rule in (("missing", "#638"), ("nested", "#641"), ("junk", "#640"), ("sibling", "#639")):
+            with self.subTest(change=change):
+                if change == "missing":
+                    victim = promoted / "order_controller.py"
+                    victim.unlink()
+                elif change == "nested":
+                    (promoted / "nested").mkdir()
+                elif change == "junk":
+                    (promoted / "utils.py").write_text("pass\n")
+                else:
+                    (promoted.parent / "order_controller.py").write_text("pass\n")
+                self.assertIn(rule, self.run_checker("check-layer-skeleton.py"))
+
+
 class SourceMirrorRegression(unittest.TestCase):
     """규범 개정 뒤에도 이관 원문 주소와 현재 렌더 주소를 혼동하지 않는다."""
 
     def setUp(self) -> None:
         self.tmp = tempfile.TemporaryDirectory(prefix="field-mirror-")
         self.addCleanup(self.tmp.cleanup)
         self.root = Path(self.tmp.name)
         self.paths = corpus.paths_for(self.root, "architecture-ddd")
         old = "## Policy\n\nOriginal approved policy.\n"
         current = "## Policy\n\nAmended approved policy.\n"

```

## workspace/tools/registry_gate_smoke.py

Before SHA256: 14fe3ee63b654db6b916f89acbccb4c1c208e14d2e53cb7471414ae38abbb8b6
After SHA256: ff22017079c33a4b568720b7f28e6a7cee909de3cb5e65309d9167447804ce7c

```diff
--- before/workspace/tools/registry_gate_smoke.py
+++ after/workspace/tools/registry_gate_smoke.py
@@ -48,20 +48,21 @@
 """
 from __future__ import annotations
 
 import json
 import os
 import re
 import shutil
 import subprocess
 import sys
 import tempfile
+import unittest
 from pathlib import Path
 
 ROOT: Path = Path(__file__).resolve().parents[2]
 GATE: Path = ROOT / "dddjango" / "scripts" / "registry_gate.py"
 BASE_FIXTURE: Path = ROOT / "workspace" / "eval" / "fixtures" / "skeleton" / "good_bc"
 
 _GIT_ID: "list[str]" = ["-c", "user.email=smoke@dddjango", "-c", "user.name=smoke"]
 # 결정적 SHA — 모든 커밋의 저자·커미터 시각 고정(provenance 케이스의 사슬·머지 SHA 가 런마다 같다).
 _GIT_DATE: str = "2026-09-03T00:00:00+0900"
 # P0′ 수리 전 사본 — 수리 배치 2 Part 1 tip(provenance 채널 도입 직전 실행기 트리).
@@ -243,21 +244,108 @@
     old_gate: "subprocess.CompletedProcess[bytes]" = subprocess.run(
         ["git", "-C", str(ROOT), "show", f"{_PRE_REPAIR_COMMIT}:dddjango/scripts/registry_gate.py"],
         capture_output=True)
     if old_gate.returncode != 0:
         return None
     gate: Path = dest / "dddjango" / "scripts" / "registry_gate.py"
     gate.write_bytes(old_gate.stdout)
     return gate
 
 
+
+class CacheSnapshotRegression(unittest.TestCase):
+    def test_snapshot_gate_skips_only_optional_cache_and_preserves_original_bytes(self):
+        from pregate_fixture_run import _load_module
+        sys.path.insert(0, str(GATE.parent))
+        gate = _load_module(GATE, "cache_snapshot_gate")
+        slots = (
+            "domain_layer/vanished",
+            "application_layer/order/vanished",
+            "driving_layer/open_host_service/vanished",
+            "application_layer/port/vanished",
+            "driven_layer/adapter/email_sender/vanished_adapter",
+        )
+        with tempfile.TemporaryDirectory(prefix="cache-snapshot-") as temp:
+            td = Path(temp)
+            repo, anchor = _make_repo(td, "repo")
+            for relative in slots:
+                _write(repo, "application/orders/" + relative + "/deep/__pycache__/old.pyc", "cache bytes")
+            _write(repo, "harmless.txt", "working change")
+            before = {str(p.relative_to(repo)): p.read_bytes() for p in repo.rglob("*")
+                      if p.is_file() and ".git" not in p.relative_to(repo).parts}
+            snapshot = td / "snapshot"
+            gate._snapshot_current(repo, snapshot)
+            code, out = _gate(repo, anchor)
+            self.assertEqual(code, 0, out)
+            self.assertNotIn("vanished", out)
+            for relative in slots:
+                self.assertFalse((snapshot / "application/orders" / relative).exists(), relative)
+            for relative in slots:
+                _write(repo, "application/orders/" + relative + "/__init__.py", "")
+            code, out = _gate(repo, anchor)
+            self.assertEqual(code, 2, out)
+            for rule in ("#299", "#256", "#193", "#570", "#569", "#152", "#218", "#225"):
+                self.assertTrue(any(rule in line and "vanished" in line for line in out.splitlines()), (rule, out))
+            for relative in slots:
+                (repo / "application/orders" / relative / "__init__.py").unlink()
+            after = {str(p.relative_to(repo)): p.read_bytes() for p in repo.rglob("*")
+                     if p.is_file() and ".git" not in p.relative_to(repo).parts
+                     and ".dddjango" not in p.relative_to(repo).parts}
+            self.assertEqual(after, before)
+
+    def test_snapshot_keeps_fixed_parents_hidden_files_empty_instances_and_other_parents(self):
+        from pregate_fixture_run import _load_module
+        sys.path.insert(0, str(GATE.parent))
+        gate = _load_module(GATE, "cache_boundary_gate")
+        with tempfile.TemporaryDirectory(prefix="cache-boundary-") as temp:
+            td = Path(temp)
+            repo = td / "repo"
+            shutil.copytree(BASE_FIXTURE, repo)
+            fixed = repo / "application/orders/application_layer/port/unit_of_work"
+            shutil.rmtree(fixed)
+            _write(repo, str(fixed.relative_to(repo)) + "/__pycache__/old.pyc", "cache")
+            _write(repo, "other/domain_layer/vanished/__pycache__/old.pyc", "cache")
+            _write(repo, "application/orders/driving_layer/api/order/order_controller/__pycache__/old.pyc", "cache")
+            _write(repo, "application/orders/domain_layer/hidden/__pycache__/old.pyc", "cache")
+            _write(repo, "application/orders/domain_layer/hidden/.real", "hidden source")
+            (repo / "application/orders/domain_layer/empty").mkdir()
+            _write(repo, "application/cache_bc/domain_layer/__pycache__/old.pyc", "cache")
+            snapshot = td / "snapshot"
+            gate._snapshot_current(repo, snapshot)
+            for relative in (str(fixed.relative_to(repo)), "other/domain_layer/vanished",
+                             "application/orders/domain_layer/hidden", "application/orders/domain_layer/empty",
+                             "application/cache_bc/domain_layer",
+                             "application/orders/driving_layer/api/order/order_controller"):
+                self.assertTrue((snapshot / relative).is_dir(), relative)
+            proc = subprocess.run([sys.executable, "-B", str(GATE.parent / "check-layer-skeleton.py"),
+                                   str(snapshot)], capture_output=True, text=True, env=_scrubbed_env())
+            self.assertEqual(proc.returncode, 2, proc.stdout + proc.stderr)
+            self.assertTrue(any("#488" in line and "unit_of_work" in line for line in proc.stdout.splitlines()))
+
+    def test_nested_application_container_uses_same_optional_slots_as_direct_checker(self):
+        from pregate_fixture_run import _load_module
+        sys.path.insert(0, str(GATE.parent))
+        gate = _load_module(GATE, "nested_cache_gate")
+        with tempfile.TemporaryDirectory(prefix="nested-cache-") as temp:
+            td = Path(temp)
+            root = td / "repo"
+            shutil.copytree(BASE_FIXTURE, root / "src")
+            relative = "src/application/orders/domain_layer/vanished"
+            _write(root, relative + "/__pycache__/old.pyc", "cache")
+            snapshot = td / "snapshot"
+            gate._snapshot_current(root, snapshot)
+            self.assertFalse((snapshot / relative).exists())
+
 def main() -> int:
+    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(CacheSnapshotRegression))
+    if not result.wasSuccessful():
+        return 2
     if not GATE.is_file() or not BASE_FIXTURE.is_dir():
         print("재료 결손: registry_gate.py 또는 skeleton/good_bc fixture 없음", file=sys.stderr)
         return 1
     rows: "list[tuple[str, int, int, bool, str]]" = []  # (케이스, 기대, 실측, 내용검사, 비고)
 
     with tempfile.TemporaryDirectory() as td_s:
         td: Path = Path(td_s)
 
         # V — 공허 차분: 앵커=HEAD·clean → exit 1
         repo, anchor = _make_repo(td, "vacuous")

```
