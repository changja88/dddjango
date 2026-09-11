# task-2 review package

No commit was authorized. This package compares owned-file snapshots before this task with current bytes.

## dddjango/scripts/design_pregate.py

Before SHA256: 377645c3a4d1de37b1be8243e06d4754d34a92d327317929c412fdb6eec8f723
After SHA256: 48f4445ed454d6b55a4a3a7793af57308e73c6eda13bc81379ac900f91dbceae

```diff
--- before/dddjango/scripts/design_pregate.py
+++ after/dddjango/scripts/design_pregate.py
@@ -119,32 +119,38 @@
 import json
 import os
 import re
 import shutil
 import subprocess
 import sys
 import tarfile
 import tempfile
 from dataclasses import dataclass, field, replace
 from datetime import datetime, timezone
+from typing import TypedDict
 from pathlib import Path, PurePosixPath
 
 SCRIPTS_DIR: Path = Path(__file__).resolve().parent
 sys.path.insert(0, str(SCRIPTS_DIR))
 try:
+    import registry_gate as registry
+    import findings
     import standard_tree as tree  # noqa: E402  — 신규 BC 골격 전량(D2 ② 화이트리스트)의 유일 트리 데이터
     import checker_target as ct  # noqa: E402  — 자리표시자 술어·슬롯 실현(계약 실존 ⑵ — 재구현 금지)
 except ImportError:  # 데이터·술어 모듈 없이는 골격 실체화·실존 판정 불가 — fail-closed(실행 불능)
     print("실행 불능: standard_tree.py / checker_target.py 를 찾지 못했다 — 실행기와 같은 폴더에 있어야 한다",
           file=sys.stderr)
     sys.exit(1)
 
+FILE_PLAN_NOTE: str = ("file-plan은 승인 제품 변경의 경로다. coordinator 작업 기록·gate report·임시 로그는 계획 재료 밖이다. "
+                      "작업기록 오편입 사례는 경로의 역할을 검토할 근거이며 파일명만으로 삭제하지 않는다. "
+                      "docs/**와 비-Python 제품 파일도 승인 범위이면 포함할 수 있다.")
 MODE: str = "enforce"  # 차단 모드 상수(설계 §10 M2 · 2026-09-03 승격) — red 는 architect 반송 의무(Coordinator 규범)
 NO_SUBSTITUTE: str = ("예보는 Phase 2 step 6(G2 registry 게이트)의 실행·증거 요구를 "
                       "어떤 형태로도 대체·축약하지 않는다.")
 COVER_NOTE: str = ("커버: P/S/I급 결정 계약 표면(보수 추정 — 유일한 판정자는 백테스트·"
                    "관찰 실측이다). C급·④형은 표면 밖.")
 # 계획 경로 선검증(D3) — `_IGNORE_COPY` 조용 소실 방지 + 숨김 세그먼트 전면 거절.
 FORBIDDEN_SEGMENTS: "frozenset[str]" = frozenset({
     "build", "dist", "staticfiles", "node_modules", "site-packages", "venv", ".dddjango",
 })
 # 기계 블록 마커 → 펜스 언어(§4). 이 어휘 밖의 machine 마커는 형식 red(fail-closed).
@@ -192,20 +198,45 @@
 _ALIAS_RE: "re.Pattern[str]" = re.compile(
     r"^alias(?:\[(TYPE_CHECKING|else)\]\s+|\s+(?=[A-Za-z_]\w*\s*[:=]))(.+)$")
 _IMPORT_ROW_RE: "re.Pattern[str]" = re.compile(
     r"^(\S+)(?:\t+| {2,})((?:from\s+\S+\s+import\s+.+|import\s+\S.*))$")
 _EXC_ROW_RE: "re.Pattern[str]" = re.compile(r"^([A-Za-z_]\w*)(?:\t+| {2,})(\S+)\s*$")
 _ANN_MARKERS_RE: "re.Pattern[str]" = re.compile(r"\[markers:\s*([^\]]*)\]")
 _ANN_BASE_RE: "re.Pattern[str]" = re.compile(r"\[base:\s*([^\]]*)\]")
 _ANN_CLIENT_RE: "re.Pattern[str]" = re.compile(r"\[client:\s*(yes|no)\s*\]")
 _ATTR_LINE_RE: "re.Pattern[str]" = re.compile(r"\[#([\w-]+)\]\s+(\S+)")
 _REQ_PY_RE: "re.Pattern[str]" = re.compile(r'requires-python\s*=\s*"[^"]*>=\s*(\d+)\.(\d+)')
+
+
+class GeneratedMethod(TypedDict):
+    owner: str
+    method: str
+    lineno: int
+    end_lineno: int
+
+
+class MaterializationReport(TypedDict):
+    materialized: list[str]
+    already_built: list[str]
+    unsimulated: list[str]
+    pruned_dirs: list[str]
+    generated_methods: dict[str, list[GeneratedMethod]]
+
+
+class GateResult(TypedDict):
+    raw_exit: int
+    raw_stdout: str
+    attributed_lines: list[str]
+    records: list[dict]
+    unmatched_lines: list[str]
+    candidate_lines: list[str]
+    candidate_records: list[dict]
 
 
 class FormError(Exception):
     """형식 red(exit 3) — 파싱 오류·add 실존 충돌·금지 경로·태그 이중 서술."""
 
 
 class RunError(Exception):
     """실행 불능(exit 1) — venv/인터프리터·git 실패·재료 결손."""
 
 
@@ -1735,55 +1766,71 @@
                         elif _is_repo_target(copy, origin.split(".")[0], plan):
                             uncertain.append(f"타입 `{origin}.{symbol}` 필드 선언/출처 보완 필요")
             walk(module, owner, values[0])
             if confirmed:
                 add("#202", entry.path, owner, "DTO 필드에서 domain aggregate/entity 도달: " + ", ".join(sorted(set(confirmed))), True)
             if uncertain:
                 add("#202", entry.path, owner, "; ".join(sorted(set(uncertain))) + " — 출처 보완 검토 질문", False)
     return findings
 
 
+def _generated_methods(module: ast.Module) -> list[GeneratedMethod]:
+    """이번 렌더의 함수·메서드 범위만 기록한다(기존 실물의 스텁 문구는 근거가 아니다)."""
+    result: list[GeneratedMethod] = []
+    def collect(nodes: list[ast.stmt], owner: str = "") -> None:
+        for node in nodes:
+            if isinstance(node, ast.ClassDef):
+                collect(node.body, f"{owner}.{node.name}" if owner else node.name)
+            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
+                result.append(dict(owner=owner, method=node.name, lineno=node.lineno, end_lineno=node.end_lineno))
+    collect(module.body)
+    return result
+
+
 def materialize(copy: Path, plan: Plan, *, realized: "frozenset[str]" = frozenset(),
-                base_short: str = "", promoted: "frozenset[str]" = frozenset()) -> "dict[str, list[str]]":
+                base_short: str = "", promoted: "frozenset[str]" = frozenset()) -> MaterializationReport:
     """태그 의미론(D2)대로 사본 위에 팬텀을 겹친다 — add 실존 충돌은 FormError.
 
     `promoted` = `baseline_form_errors` 가 승격 형태 예외로 통과시킨 update 경로(미시뮬레이션 문면만 다르다).
 
     **재발화 판형(`--base` 명시 — Phase 2 진입 후 명세 개정 재실행)**: `realized` 는 `lift_realized_adds` 가
     앵커 커밋 전에 사본에서 걷어낸 «기실현 add» 경로다 — 여기서는 다른 add 와 똑같이 스텁으로 실체화하고
     (materialized 에 계수) already-built 에도 «기실현 — 스텁 대체 예보»로 기록한다(이중 기재는 의도 —
     `empty(기실현)` 은 materialized 에 안 실리는 것과 구별). 사본에 실존하는 add 는 기준선 트리 실존(계획↔실물
     모순)뿐이므로 여전히 형식 red 다. `--base` 미지정 경로는 판정(exit·귀속·ID) 동일이다 — 리포트의 집계 행 문면
     (계약 실존 «자기 update 해소» 열 등)은 판과 함께 변한다.
 
     반환: materialized / already_built / unsimulated / pruned_dirs 목록(리포트 재료).
     빈 부모 정리는 Git 파일 차분이 아니므로 materialized 건수에 넣지 않는다.
     """
-    report: "dict[str, list[str]]" = {"materialized": [], "already_built": [], "unsimulated": []}
+    report: MaterializationReport = {"materialized": [], "already_built": [], "unsimulated": [],
+                                     "pruned_dirs": [], "generated_methods": {}}
     for entry in plan.entries.values():
         target: Path = copy / entry.path
         if entry.tag == "add":
             if target.exists():
-                raise FormError(f"add 충돌(실존): {entry.path} — 계획과 실물의 모순은 그 자체가 발견이다")
+                raise FormError(f"add 충돌(실존): {entry.path} — 기준선 부재·오버레이 실존: "
+                                "초기 예보의 새 파일 자리와 실물이 충돌한다. 구현 후 명세 개정은 승인 기준선을 명시한 재예보 목적을 검토한다")
             if entry.path in realized:
                 report["already_built"].append(
                     f"add(기실현 — 기준선 {base_short} 부재·오버레이 실존 → 앵커 스냅숏에서 제외·스텁 대체 예보 · "
                     f"실체화 목록에도 계수): {entry.path}")
             stub: str = render_stub(entry)
             try:
                 compile(stub, entry.path, "exec")  # symtable까지 — 중복 인자류는 ast.parse 가 못 잡는다
             except (SyntaxError, ValueError) as exc:
                 detail: str = getattr(exc, "msg", None) or str(exc)
                 raise FormError(f"스텁 렌더 파싱 불가: {entry.path} — {detail} "
                                 f"(기계 블록 전사 내용이 파이썬 문법 밖이다){_compile_hint(entry)}")
             target.parent.mkdir(parents=True, exist_ok=True)
             target.write_text(stub, encoding="utf-8")
+            report["generated_methods"][entry.path] = _generated_methods(ast.parse(stub))
             report["materialized"].append(entry.path)
         elif entry.tag == "empty":
             # add 와 같은 «새 파일» 태그 — 기준선 실존은 baseline_form_errors 가 앞서 형식 red 로 세우고, `--base` 재발화의
             # 오버레이 실존(기실현)은 lift_realized_adds 가 걷어내 여기서 빈 파일로 다시 쓴다(실체화 계수 · 도피 봉쇄).
             if target.exists():
                 raise FormError(f"empty 충돌(실존): {entry.path} — 계획과 실물의 모순은 그 자체가 발견이다")
             if entry.path in realized:
                 report["already_built"].append(
                     f"empty(기실현 — 기준선 {base_short} 부재·오버레이 실존 → 앵커 스냅숏에서 제외·빈 파일 대체 · "
                     f"실체화 목록에도 계수): {entry.path}")
@@ -1796,20 +1843,24 @@
             elif target.is_file():
                 target.unlink()
                 report["materialized"].append(f"removed {entry.path}")
             else:
                 report["unsimulated"].append(f"remove(실존 없음): {entry.path}")
         elif entry.tag == "update":
             updated: "bytes | None"
             detail: str
             updated, detail = _render_service_update(copy, entry)
             if updated is not None:
+                prior_names = {node.name for node in ast.parse(target.read_bytes()).body
+                               if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
+                report["generated_methods"][entry.path] = [item for item in _generated_methods(ast.parse(updated))
+                    if not item["owner"] and item["method"] not in prior_names]
                 target.write_bytes(updated)
             marker_update, marker_detail = _render_marker_update(copy, entry)
             if marker_update is not None:
                 updated = marker_update
             detail += "; " + marker_detail
             if updated is not None:
                 target.write_bytes(updated)
                 report["materialized"].append(entry.path)
             if entry.path in promoted:
                 report["unsimulated"].append(
@@ -1859,39 +1910,90 @@
     m: "re.Match[str] | None" = _REQ_PY_RE.search(pyproject.read_text(encoding="utf-8", errors="replace"))
     if m is None:
         return None
     lo: "tuple[int, int]" = (int(m.group(1)), int(m.group(2)))
     if cur >= lo:
         return None
     return (f"대상은 python >={lo[0]}.{lo[1]} 선언(pyproject.toml)인데 인터프리터는 "
             f"{cur[0]}.{cur[1]} 다 — fail-open 침묵 clean 위험. 대상 venv 인터프리터를 --python 으로 넘겨라")
 
 
-def run_gate(copy: Path, scratch: Path, python_bin: str) -> "tuple[int, list[str], str]":
-    """registry_gate(판정 차분) 실행 — (exit, 귀속 라인, stdout)을 돌려준다."""
+def run_gate(copy: Path, scratch: Path, python_bin: str) -> GateResult:
+    """registry 원 exit/stdout과 전체 귀속/원본 레코드 재료를 보존한다."""
     introduced: Path = scratch / "introduced.json"
     env: "dict[str, str]" = dict(os.environ)
     env["DJR_FINDINGS_JSON"] = str(scratch / "findings.jsonl")  # 스크래치 격리(D3)
     env.pop("DJR_VIOLATIONS_DIR", None)
     env.pop("DJR_SOURCE_GIT_ROOT", None)
     proc: "subprocess.CompletedProcess[str]" = subprocess.run(
         [python_bin, str(SCRIPTS_DIR / "registry_gate.py"), str(copy),
          "--anchor", "HEAD", "--introduced-json", str(introduced)],
         capture_output=True, text=True, env=env)
     if proc.returncode not in (0, 2):
         raise RunError(f"registry_gate 실행 불능(exit {proc.returncode}): "
                        f"{(proc.stderr or proc.stdout).strip()[-600:]}")
     if not introduced.is_file():
         raise RunError("registry_gate 가 introduced.json 을 남기지 않았다 — 재료 결손(fail-closed)")
-    payload: "dict[str, object]" = json.loads(introduced.read_text(encoding="utf-8"))
-    attributed: "list[str]" = [str(x) for x in payload.get("attributed_lines", [])]
-    return proc.returncode, attributed, proc.stdout
+    try:
+        payload = json.loads(introduced.read_text(encoding="utf-8"))
+    except (OSError, ValueError) as exc:
+        raise RunError(f"registry_gate introduced.json 읽기 불능 — 재료 결손: {exc}") from exc
+    if not isinstance(payload, dict):
+        raise RunError("registry_gate introduced.json 객체 부재 — 재료 결손")
+    for key, item_type in (("attributed_lines", str), ("records", dict), ("unmatched_lines", str)):
+        if not isinstance(payload.get(key), list) or any(not isinstance(x, item_type) for x in payload[key]):
+            raise RunError(f"registry_gate introduced.json {key} 결손/형식 불비(fail-closed)")
+    # 신규 후보가 0인 registry는 이 두 optional key를 모두 생략한다.
+    if ("candidate_lines" in payload) != ("candidate_records" in payload):
+        raise RunError("registry_gate 후보 채널 재료 결손(fail-closed)")
+    for key, item_type in (("candidate_lines", str), ("candidate_records", dict)):
+        value = payload.get(key, [])
+        if not isinstance(value, list) or any(not isinstance(x, item_type) for x in value):
+            raise RunError(f"registry_gate introduced.json {key} 형식 불비(fail-closed)")
+    if proc.returncode == 2 and not payload["attributed_lines"]:
+        raise RunError("registry_gate raw exit 2를 설명할 귀속 항목 부재(fail-closed)")
+    return GateResult(raw_exit=proc.returncode, raw_stdout=proc.stdout,
+        attributed_lines=payload["attributed_lines"], records=payload["records"],
+        unmatched_lines=payload["unmatched_lines"], candidate_lines=payload.get("candidate_lines", []),
+        candidate_records=payload.get("candidate_records", []))
+
+
+def partition_generated_findings(gate_result: GateResult,
+                                 generated_methods: dict[str, list[GeneratedMethod]]) -> tuple[list[str], list[str]]:
+    """전체 정규화 key의 모든 원본 위치가 생성 after_commit인 #376만 S1로 분리한다."""
+    cohorts: dict[str, list[dict]] = {}
+    for record in gate_result["records"]:
+        key = f"{record.get('checker')} :: {registry._normalize(findings.line_of_record(record), ())}"
+        cohorts.setdefault(key, []).append(record)
+    # A raw record that cannot be joined signals incomplete attribution evidence.
+    # Do not guess its cohort from rule/path or silently drop it to make a green result.
+    if any(key not in gate_result["attributed_lines"] for key in cohorts):
+        return list(gate_result["attributed_lines"]), []
+    def generated(record: dict) -> bool:
+        if record.get("rule") != "#376":
+            return False
+        location = re.fullmatch(r"(.+):(\d+)", str(record.get("file", "")))
+        if location is None:
+            return False
+        path, number = location.group(1), int(location.group(2))
+        return any(item["method"] == "after_commit" and item["owner"]
+                   and item["lineno"] <= number <= item["end_lineno"]
+                   for item in generated_methods.get(path, []))
+    retained: list[str] = []
+    deferred: list[str] = []
+    for line in gate_result["attributed_lines"]:
+        records = cohorts.get(line, [])
+        if line not in gate_result["unmatched_lines"] and records and all(generated(r) for r in records):
+            deferred.append(f"S1: 생성한 after_commit 본문 — on_commit 구현 미검증 · {line}")
+        else:
+            retained.append(line)
+    return retained, deferred
 
 
 def _stable_id(line: str) -> str:
     """예보 항목 안정 ID — sha256(규칙#+경로)[:12] (D4 처분 라벨 추적 키)."""
     m: "re.Match[str] | None" = _ATTR_LINE_RE.search(line)
     rule: str = m.group(1) if m else "?"
     where: str = m.group(2).split(":", 1)[0] if m else line
     return hashlib.sha256(f"#{rule}+{where}".encode("utf-8")).hexdigest()[:12]
 
 
@@ -2337,42 +2439,50 @@
             grouped.setdefault(line, []).append(f"{item.owner}: {item.detail}")
         lines += ["", f"### {title} ({len(grouped)}건)", ""]
         for line, details in grouped.items():
             lines.append(f"- `{_stable_id(line)}` {line} — " + "; ".join(dict.fromkeys(details)))
         if not grouped:
             lines.append("- (없음)")
     return lines
 
 
 def write_report(report_path: Path, spec: Path, base_ref: str, base_sha: str, verdict: str,
-                 attributed: "list[str]", mat: "dict[str, list[str]]",
+                 attributed: "list[str]", mat: MaterializationReport,
                  notes: "list[str]", blk_hash: str, existence: ExistenceReport,
-                 declarations: list[DeclarationFinding] | tuple[DeclarationFinding, ...] = ()) -> None:
+                 declarations: list[DeclarationFinding] | tuple[DeclarationFinding, ...] = (),
+                 *, execution_mode: str = "", raw_summary: str = "",
+                 deferred: list[str] | tuple[str, ...] = ()) -> None:
     """예보 리포트 append(D4) — 헤더 상시 문구·안정 ID·계약 실존 절(상시)·사각 목록 병기."""
     now: str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
     lines: "list[str]" = [
         "",
         f"## pre-gate 예보 — {now} · {spec.name}",
         "",
         f"- 기준선 SHA: `{base_sha}` (--base {base_ref}) — «스텁 제외 현재 상태» · "
         f"프로필: auto · 모드: 차단({MODE}) · {_executor_stamp(blk_hash)}",
         f"- {NO_SUBSTITUTE}",
         f"- {COVER_NOTE}",
+        f"- 실행 모드: {execution_mode}",
+        f"- {FILE_PLAN_NOTE}",
         f"- 판정: {verdict}",
         "",
         f"### 예보 항목 ({len(attributed)}건 · 안정 ID = sha256(규칙#+경로)[:12])",
         "",
     ]
     if attributed:
         lines.extend(f"- `{_stable_id(line)}` {line}" for line in attributed)
     else:
         lines.append("- (없음) — green 은 «설계 검증됨»이 아니라 «P/S/I급 위반 예보 0»이다.")
+    lines += ["", f"- {raw_summary}", "", f"### 생성 본문 S1 미검증 ({len(deferred)}건)", ""]
+    lines.extend(f"- {item}" for item in deferred)
+    if not deferred:
+        lines.append("- (없음)")
     lines.extend(_declaration_lines(declarations))
     lines.extend(_existence_lines(existence))
     lines += ["", f"### already-built ({len(mat.get('already_built', []))}건) · "
                   f"미시뮬레이션 ({len(mat.get('unsimulated', []))}건)", ""]
     for item in mat.get("already_built", []):
         lines.append(f"- already-built: {item}")
     for item in mat.get("unsimulated", []):
         lines.append(f"- 미시뮬레이션: {item}")
     for item in mat.get("pruned_dirs", []):
         lines.append(f"- remove 빈 부모 정리: {item}")
@@ -2385,33 +2495,36 @@
     lines.append("")
     report_path.parent.mkdir(parents=True, exist_ok=True)
     with report_path.open("a", encoding="utf-8") as fp:
         fp.write("\n".join(lines))
     print(f"\n예보 리포트 append → {report_path}")
 
 
 def write_report_stub(report_path: "Path | None", spec: Path, base_ref: str, base_sha: str,
                       verdict: str, detail: "list[str]", blk_hash: str,
                       existence: "ExistenceReport | None" = None,
-                      declarations: list[DeclarationFinding] | tuple[DeclarationFinding, ...] = ()) -> None:
+                      declarations: list[DeclarationFinding] | tuple[DeclarationFinding, ...] = (),
+                      *, execution_mode: str = "") -> None:
     """형식 red·skip 도 리포트에 사유를 남긴다(침묵 금지) — 예보 항목 없는 축약판. 실체화-0 skip 은 계약 실존 절을
     싣는다(결손 ≥1 이면 exit 5 의 근거 — kkebi S2 판형: update 소비자만의 명세)."""
     if report_path is None:
         return
     now: str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
     lines: "list[str]" = [
         "",
         f"## pre-gate 예보 — {now} · {spec.name}",
         "",
         f"- 기준선 SHA: `{base_sha}` (--base {base_ref}) · 프로필: auto · 모드: 차단({MODE}) · "
         f"{_executor_stamp(blk_hash)}",
         f"- {NO_SUBSTITUTE}",
+        f"- 실행 모드: {execution_mode}",
+        f"- {FILE_PLAN_NOTE}",
         f"- 판정: {verdict}",
         "",
     ]
     lines.extend(f"- {item}" for item in detail)
     lines.extend(_declaration_lines(declarations))
     if existence is not None:
         lines.extend(_existence_lines(existence))
     lines.append("")
     report_path.parent.mkdir(parents=True, exist_ok=True)
     with report_path.open("a", encoding="utf-8") as fp:
@@ -2442,29 +2555,31 @@
     판정에 넣지 않는다(미커밋 기실현 add 의 재라벨도 기준선 부재라 red). 기준선 이후 HEAD 실존은 사유행을 나눈다
     (자기 기실현 add 면 add 로 복원 · 타 레인 유입이면 STOP — 기준선 이동 금지) — `in_head` 는 부재 행에서만 부른다.
 
     반환: (오류 목록 — 전건, 승격 형태 예외로 통과한 update 경로 집합).
     """
     errors: "list[str]" = []
     promoted: "set[str]" = set()
     for path, entry in plan.entries.items():
         present: bool = path in in_baseline
         if entry.tag == "add" and present:
-            errors.append(f"add 충돌(실존): {path} — 계획과 실물의 모순은 그 자체가 발견이다")
+            errors.append(f"add 충돌(실존): {path} — 기준선 실존: 새 파일 add와 기준선 {base_short}의 실물이 충돌한다")
         elif entry.tag == "update" and not present:
             if _promoted_form(copy, path):
                 promoted.add(path)
             elif in_head(path):
                 errors.append(f"update 대상 기준선 이후 실존: {path} — 기준선 {base_short} 에 없고 HEAD 에 있다: "
-                              f"자기 기실현 add 면 add 로 복원 · 타 레인 유입이면 STOP(기준선 이동 금지)")
+                              f"자기 기실현 add 면 add 로 복원 · 타 레인 유입이면 STOP(기준선 이동 금지). "
+                              "초기 예보는 구현 전 계획, 명시 재예보는 승인 기준선에 대한 구현 후 명세 개정에 쓴다")
             else:
-                errors.append(f"update 대상 부재: {path} — 기준선 {base_short} 에 없는 경로는 add 다(재라벨 도피 금지)")
+                errors.append(f"update 대상 부재: {path} — 기준선 {base_short} 에 없는 경로는 add 다(재라벨 도피 금지). "
+                              "초기 예보는 구현 전 계획, 명시 재예보는 승인 기준선에 대한 구현 후 명세 개정에 쓴다")
         elif entry.tag == "remove" and not entry.deferred_remove and not present:
             errors.append(f"remove 대상 부재: {path} — 기준선 {base_short} 에 없는 경로는 제거할 수 없다"
                           f"(고정 기준선에서 기실현 remove 는 실존이다 — 이미 지워진 경로는 행을 거둔다)")
         elif entry.tag == "empty" and present:
             # `empty` 는 add 와 같은 «새 파일» 태그다 — 기준선 실존을 already-built 로 통과시키면 기실현 add 를 empty 로
             # 재라벨해 실체화 0 으로 도피하는 경로가 update 재라벨과 동형으로 남는다(6단계 감사 MAJOR-1).
             errors.append(f"empty 충돌(실존): {path} — 새 빈 파일 자리가 기준선 {base_short} 에 이미 있다: "
                           f"기실현이면 update 다(재라벨 도피 금지)")
     return errors, frozenset(promoted)
 
@@ -2535,20 +2650,22 @@
     if hash_m is None:
         problems.append("최신성 증명 불가 — 마지막 헤더에 블록 해시 토큰이 없다(구판 리포트) · 재발화")
     elif report_hash != spec_hash:
         problems.append(f"stale — 명세 블록 해시 {spec_hash} ≠ 마지막 예보 {report_hash} · 재발화")
     count_m: "re.Match[str] | None" = _REPORT_COUNT_RE.search(verdict)
     defect_m: "re.Match[str] | None" = _REPORT_DEFECT_RE.search(verdict)
     attributed: int = int(count_m.group(1)) if count_m else 0
     defects: int = int(defect_m.group(1)) if defect_m else 0
     declarations: int = len(set(_REPORT_ID_RE.findall(_subsection(section, "선언 확정"))))
     candidates: int = len(set(_REPORT_ID_RE.findall(_subsection(section, "선언 후보"))))
+    deferred_section = _subsection(section, "생성 본문 S1 미검증")
+    deferred_count = sum(line.startswith("- S1:") for line in deferred_section.splitlines())
     short: str
     if verdict.startswith("형식 red"):
         problems.append(f"형식 red 미해소 — 마지막 판정 «{verdict}» · architect 반송")
         short = "형식 red"
     elif verdict.startswith("예보 red"):
         ids: "list[str]" = list(dict.fromkeys(_REPORT_ID_RE.findall(_subsection(section, "예보 항목"))
                     + _REPORT_ID_RE.findall(_subsection(section, "선언 확정"))))
         missing: "list[str]" = [i for i in ids if not _disposed(section, i)]
         if missing:
             problems.append(f"처분 미기재 {len(missing)}건(ignored|filtered 행 없음 — corrected 는 재실행이 최종본): "
@@ -2561,21 +2678,21 @@
         if "<!-- machine:" not in spec_text:
             # 구형 명세 + 관찰기(≤2.17.16)의 «블록 부재 skip» 스텁이 마지막 절로 남은 레인 — 블록 해시가 불변이라 캐시 skip 으로
             # 재실행 없이 G2 가 열리는 좁은 경로를 닫는다(5단계 리뷰 C · 결정 잔여 1): 차단 모드에서 블록 부재는 형식 red 다.
             problems.append("블록 부재 — 마지막 판정이 관찰 모드 skip 이고 명세에 machine 마커가 없다: 소급 블록 작성 후 재발화")
     else:
         problems.append(f"판정 문면 불명 — «{verdict}»")
         short = verdict[:24]
     info: "dict[str, str]" = {
         "spec_hash": spec_hash, "report_hash": report_hash, "short": short,
         "attributed": str(attributed), "defects": str(defects),
-        "declarations": str(declarations), "candidates": str(candidates),
+        "declarations": str(declarations), "candidates": str(candidates), "deferred": str(deferred_count),
         "base": base_m.group(1)[:12] if base_m else "-",
     }
     return (3 if problems else 0), problems, info
 
 
 def run_check_report(spec_text: str, report_path: Path, blk_hash: str) -> int:
     """`--check-report` 진입 — 배너(G1/G1′)·G2 근거 대조의 유일한 기계 출처(`요약:` 행)."""
     print(f"# design_pregate --check-report · 모드 차단({MODE}) · {_executor_stamp(blk_hash)}")
     if not report_path.is_file():
         print(f"실행 불능: 리포트 부재 — {report_path} (pre-gate 가 이 레인에서 한 번도 실행되지 않았다 · 구형 명세·"
@@ -2587,21 +2704,21 @@
     problems: "list[str]" = result[1]
     info: "dict[str, str]" = result[2]
     if code == 1:
         print(f"실행 불능: {problems[0]}", file=sys.stderr)
         return 1
     for p in problems:
         print(f"  불비: {p}")
     status: str = "정합" if code == 0 else f"불비 {len(problems)}건"
     print(f"\n요약: check-report {status} · 블록 해시 {info['spec_hash']}={info['report_hash']} · "
           f"마지막 판정 {info['short']} · 귀속 {info['attributed']}건 · 선언 확정 {info['declarations']}건 · "
-          f"선언 후보 {info['candidates']}건 · 실존 결손 {info['defects']}건 · "
+          f"선언 후보 {info['candidates']}건 · S1 미검증 {info['deferred']}건 · 실존 결손 {info['defects']}건 · "
           f"기준선 {info['base']}")
     return code
 
 
 # ── main ────────────────────────────────────────────────────────────────────
 
 def main(argv: "list[str]") -> int:
     ap: _UsageParser = _UsageParser(add_help=True, description="design-spec pre-gate 예보 실행기")
     ap.add_argument("spec", help="설계 명세 markdown(기계 블록 §4 포함)")
     ap.add_argument("target", help="대상 저장소 루트(git)")
@@ -2632,59 +2749,62 @@
         print(f"블록 해시 {blk_hash}")
         return 0
     if ns.check_report is not None:
         return run_check_report(text, Path(ns.check_report).resolve(), blk_hash)
     if not (repo / ".git").exists():
         print(f"실행 불능: git 저장소가 아니다 — {repo} (차분 예보는 git 앵커가 전제다)", file=sys.stderr)
         return 1
 
     base_ref: str = ns.base or "HEAD"
     explicit_base: bool = ns.base is not None
+    execution_mode = f"명시 재예보(--base {base_ref})" if explicit_base else "초기 예보(기준선 기본 HEAD)"
+    print(f"실행 모드: {execution_mode}")
+    print(FILE_PLAN_NOTE)
     rev: "subprocess.CompletedProcess[bytes]" = _git(repo, "rev-parse", "--verify",
                                                      f"{base_ref}^{{commit}}", check=False)
     if rev.returncode != 0:
         print(f"실행 불능: --base {base_ref!r} resolve 불능 — "
               f"{rev.stderr.decode('utf-8', 'replace').strip()}", file=sys.stderr)
         return 1
     base_sha: str = rev.stdout.decode("ascii").strip()
 
     gap: "str | None" = _interpreter_gap_reason(repo, ns.python_bin)
     if gap is not None:
         print(f"실행 불능: {gap}", file=sys.stderr)
         return 1
 
     plan_result: "tuple[Plan | None, list[str]]" = parse_spec(text)
     plan: "Plan | None" = plan_result[0]
     errors: "list[str]" = plan_result[1]
     if errors:
         print(f"형식 red — {len(errors)}건 (기계 블록이 규범 문법 밖이다 · architect 반송 재료):")
         for err in errors:
             print(f"  {err}")
-        write_report_stub(report_path, spec_path, base_ref, base_sha, "형식 red", errors, blk_hash)
+        write_report_stub(report_path, spec_path, base_ref, base_sha, "형식 red", errors, blk_hash, execution_mode=execution_mode)
         print(f"\n요약: 형식 red {len(errors)}건(문법) · 기준선 {base_sha[:12]} · 모드 차단")
         return 3
     if plan is None:
         reason: str = ("형식 red — machine 블록 부재(<!-- machine: file-plan --> 없음): 차단 모드는 블록이 의무다 — "
                        "구형 명세(형식 규범 이전 승인)는 개정 시점에 블록을 소급 작성한다"
                        "(기준선 실존 경로는 update · 부재 경로만 add)")
         print(reason)
-        write_report_stub(report_path, spec_path, base_ref, base_sha, "형식 red(블록 부재)", [reason], blk_hash)
+        write_report_stub(report_path, spec_path, base_ref, base_sha, "형식 red(블록 부재)", [reason], blk_hash, execution_mode=execution_mode)
         print(f"\n요약: 형식 red 1건(블록 부재) · 기준선 {base_sha[:12]} · 모드 차단")
         return 3
     if not plan.entries:
         reason = ("형식 red — file-plan 0행(블록 공허): 변경 파일이 없는 명세는 pre-gate 대상이 아니라 산문이다 — "
                   "update 대상이라도 적는다(빈 펜스로 블록 의무를 채울 수 없다)")
         print(reason)
         for note in plan.notes:  # 고아 채널 행(symbols/imports 만 있는 명세)은 버려졌음을 남긴다(침묵 금지)
             print(f"  채널 메모: {note}")
         write_report_stub(report_path, spec_path, base_ref, base_sha, "형식 red(블록 공허)",
-                          [reason] + [f"채널 메모: {n}" for n in plan.notes], blk_hash)
+                          [reason] + [f"채널 메모: {n}" for n in plan.notes], blk_hash, execution_mode=execution_mode)
         print(f"\n요약: 형식 red 1건(블록 공허) · 기준선 {base_sha[:12]} · 모드 차단")
         return 3
 
     scratch: Path = Path(tempfile.mkdtemp(prefix="design-pregate-"))
     copy: Path = scratch / "copy"
     try:
         copy.mkdir(parents=True)
         _extract_archive(repo, base_sha, copy)
         # archive == 기준선 트리 — 오버레이 «전»에 계획 경로의 실존을 재서 «기준선 실존 add»(형식 red 유지)와
         # «오버레이 실존 add»(재발화 판형의 기실현)를 가른다(git 추가 호출 0·결정적).
@@ -2697,37 +2817,37 @@
             (lambda p: _git(repo, "cat-file", "-e", f"HEAD:{p}", check=False).returncode == 0)
             if explicit_base else (lambda p: False))
         form_errors: "list[str]" = form_result[0]
         promoted: "frozenset[str]" = form_result[1]
         if form_errors:
             print(f"형식 red — {len(form_errors)}건 (계획↔기준선 모순 · architect 반송 재료):")
             for err in form_errors:
                 print(f"  {err}")
             if promoted:
                 print(f"  승격 형태 예외 통과 {len(promoted)}건: " + " ".join(sorted(promoted)))
-            write_report_stub(report_path, spec_path, base_ref, base_sha, "형식 red", form_errors, blk_hash)
+            write_report_stub(report_path, spec_path, base_ref, base_sha, "형식 red", form_errors, blk_hash, execution_mode=execution_mode)
             print(f"\n요약: 형식 red {len(form_errors)}건({_error_kinds(form_errors)}) · "
                   f"기준선 {base_sha[:12]} · 모드 차단")
             return 3
         overlaid: "list[str]" = _overlay_dirty(repo, copy)
         # 기실현 add 는 앵커 커밋 «전»에 걷어낸다 — 앵커 스냅숏(L)에 실물이 남으면 스텁 진단이 잔존으로 빠진다.
         realized: "frozenset[str]" = lift_realized_adds(copy, plan, explicit_base, in_baseline)
         _git(copy, "init", "-q")
         _git(copy, "add", "-A")
         _git(copy, "commit", "-q", "-m", "pregate-anchor", "--allow-empty")
 
         try:
-            mat: "dict[str, list[str]]" = materialize(copy, plan, realized=realized, base_short=base_sha[:12],
+            mat: MaterializationReport = materialize(copy, plan, realized=realized, base_short=base_sha[:12],
                                                       promoted=promoted)
         except FormError as exc:
             print(f"형식 red — {exc}")
-            write_report_stub(report_path, spec_path, base_ref, base_sha, "형식 red", [str(exc)], blk_hash)
+            write_report_stub(report_path, spec_path, base_ref, base_sha, "형식 red", [str(exc)], blk_hash, execution_mode=execution_mode)
             print(f"\n요약: 형식 red 1건({_error_kinds([str(exc)])}) · 기준선 {base_sha[:12]} · 모드 차단")
             return 3
 
         # 계약 실존 — materialize(+골격·`__init__` 체인) 뒤 · 실체화-0 분기 앞(update 소비자만의 명세도 판정한다).
         declarations = check_declarations(plan, copy)
         declaration_count = len({(item.rule, item.path) for item in declarations if item.confirmed})
         for line in _declaration_lines(declarations):
             print(line)
         existence: ExistenceReport = check_import_existence(copy, plan)
         own_note: "str | None" = _own_interpreter_note(repo)
@@ -2745,51 +2865,57 @@
             print(reason)
             for note in plan.notes:
                 print(f"  채널 메모: {note}")
             for item in mat["unsimulated"]:
                 print(f"  미시뮬레이션: {item}")
             _print_existence(existence)
             print(f"\n요약: 실체화 0 · 실존 결손 {defects}건 · 선언 확정 {declaration_count}건 · 기준선 {base_sha[:12]} · 모드 차단")
             write_report_stub(report_path, spec_path, base_ref, base_sha, verdict_stub,
                               [reason] + [f"미시뮬레이션: {x}" for x in mat["unsimulated"]] + cleanup_notes
                               + [f"채널 메모: {n}" for n in plan.notes], blk_hash,
-                              existence=existence, declarations=declarations)
+                              existence=existence, declarations=declarations, execution_mode=execution_mode)
             return 2 if declaration_count else (5 if defects else 4)
 
         print(f"# design_pregate — 예보 실행 · 기준선 {base_sha[:12]} (--base {base_ref}) · "
               f"모드 차단({MODE}) · {_executor_stamp(blk_hash)}")
         print(f"({NO_SUBSTITUTE})")
         print(f"실체화 {len(mat['materialized'])}건 · dirty overlay {len(overlaid)}건 · "
               f"미시뮬레이션 {len(mat['unsimulated'])}건 · already-built {len(mat['already_built'])}건")
 
-        gate_result: "tuple[int, list[str], str]" = run_gate(copy, scratch, ns.python_bin)
-        gate_exit: int = gate_result[0]
-        attributed: "list[str]" = gate_result[1]
-        print("\n" + gate_result[2].rstrip())
+        gate_result = run_gate(copy, scratch, ns.python_bin)
+        attributed, deferred = partition_generated_findings(gate_result, mat["generated_methods"])
+        print("\n== 원 registry 결과 ==\n" + gate_result["raw_stdout"].rstrip())
+        raw_summary = (f"원 registry 결과: exit {gate_result['raw_exit']} · 귀속 {len(gate_result['attributed_lines'])}건 · "
+                       f"유지 {len(attributed)}건 · S1 미검증 {len(deferred)}건")
+        print(raw_summary)
+        print(f"\n== 생성 본문 S1 미검증 ({len(deferred)}건) ==")
+        for line in deferred:
+            print(f"  {line}")
 
         verdict: str = ("예보 green — P/S/I급 결정 계약 위반 예보 0(«설계 검증됨» 아님)"
-                        if gate_exit == 0 and not declaration_count else
+                        if not attributed and not declaration_count else
                         f"예보 red — P/S/I급 결정 계약 위반 예보 {len(attributed)}건")
         verdict += f" · 선언 확정 {declaration_count}건"
         verdict += f" · 계약 실존 결손 {defects}건(권고·비차단)"
         print(f"\n== 예보 항목 {len(attributed)}건 ==")
         for line in attributed:
             print(f"  `{_stable_id(line)}` {line}")
         for note in plan.notes:
             print(f"  채널 메모: {note}")
         _print_existence(existence)
         print(f"\n판정: {verdict}")
         print(f"요약: 귀속 {len(attributed)}건 · 실존 결손 {defects}건 · 기준선 {base_sha[:12]} · 모드 차단")
         if report_path is not None:
             write_report(report_path, spec_path, base_ref, base_sha, verdict,
-                         attributed, mat, plan.notes, blk_hash, existence, declarations)
-        if gate_exit != 0 or declaration_count:
+                         attributed, mat, plan.notes, blk_hash, existence, declarations,
+                         execution_mode=execution_mode, raw_summary=raw_summary, deferred=deferred)
+        if attributed or declaration_count:
             return 2
         return 5 if defects else 0
     except RunError as exc:
         print(f"실행 불능: {exc}", file=sys.stderr)
         return 1
     finally:
         if ns.keep:
             print(f"(--keep) 격리 사본 보존: {scratch}")
         else:
             shutil.rmtree(scratch, ignore_errors=True)

```

## codex-dddjango/skills/dddjango/scripts/design_pregate.py

Before SHA256: 377645c3a4d1de37b1be8243e06d4754d34a92d327317929c412fdb6eec8f723
After SHA256: 48f4445ed454d6b55a4a3a7793af57308e73c6eda13bc81379ac900f91dbceae

```diff
--- before/codex-dddjango/skills/dddjango/scripts/design_pregate.py
+++ after/codex-dddjango/skills/dddjango/scripts/design_pregate.py
@@ -119,32 +119,38 @@
 import json
 import os
 import re
 import shutil
 import subprocess
 import sys
 import tarfile
 import tempfile
 from dataclasses import dataclass, field, replace
 from datetime import datetime, timezone
+from typing import TypedDict
 from pathlib import Path, PurePosixPath
 
 SCRIPTS_DIR: Path = Path(__file__).resolve().parent
 sys.path.insert(0, str(SCRIPTS_DIR))
 try:
+    import registry_gate as registry
+    import findings
     import standard_tree as tree  # noqa: E402  — 신규 BC 골격 전량(D2 ② 화이트리스트)의 유일 트리 데이터
     import checker_target as ct  # noqa: E402  — 자리표시자 술어·슬롯 실현(계약 실존 ⑵ — 재구현 금지)
 except ImportError:  # 데이터·술어 모듈 없이는 골격 실체화·실존 판정 불가 — fail-closed(실행 불능)
     print("실행 불능: standard_tree.py / checker_target.py 를 찾지 못했다 — 실행기와 같은 폴더에 있어야 한다",
           file=sys.stderr)
     sys.exit(1)
 
+FILE_PLAN_NOTE: str = ("file-plan은 승인 제품 변경의 경로다. coordinator 작업 기록·gate report·임시 로그는 계획 재료 밖이다. "
+                      "작업기록 오편입 사례는 경로의 역할을 검토할 근거이며 파일명만으로 삭제하지 않는다. "
+                      "docs/**와 비-Python 제품 파일도 승인 범위이면 포함할 수 있다.")
 MODE: str = "enforce"  # 차단 모드 상수(설계 §10 M2 · 2026-09-03 승격) — red 는 architect 반송 의무(Coordinator 규범)
 NO_SUBSTITUTE: str = ("예보는 Phase 2 step 6(G2 registry 게이트)의 실행·증거 요구를 "
                       "어떤 형태로도 대체·축약하지 않는다.")
 COVER_NOTE: str = ("커버: P/S/I급 결정 계약 표면(보수 추정 — 유일한 판정자는 백테스트·"
                    "관찰 실측이다). C급·④형은 표면 밖.")
 # 계획 경로 선검증(D3) — `_IGNORE_COPY` 조용 소실 방지 + 숨김 세그먼트 전면 거절.
 FORBIDDEN_SEGMENTS: "frozenset[str]" = frozenset({
     "build", "dist", "staticfiles", "node_modules", "site-packages", "venv", ".dddjango",
 })
 # 기계 블록 마커 → 펜스 언어(§4). 이 어휘 밖의 machine 마커는 형식 red(fail-closed).
@@ -192,20 +198,45 @@
 _ALIAS_RE: "re.Pattern[str]" = re.compile(
     r"^alias(?:\[(TYPE_CHECKING|else)\]\s+|\s+(?=[A-Za-z_]\w*\s*[:=]))(.+)$")
 _IMPORT_ROW_RE: "re.Pattern[str]" = re.compile(
     r"^(\S+)(?:\t+| {2,})((?:from\s+\S+\s+import\s+.+|import\s+\S.*))$")
 _EXC_ROW_RE: "re.Pattern[str]" = re.compile(r"^([A-Za-z_]\w*)(?:\t+| {2,})(\S+)\s*$")
 _ANN_MARKERS_RE: "re.Pattern[str]" = re.compile(r"\[markers:\s*([^\]]*)\]")
 _ANN_BASE_RE: "re.Pattern[str]" = re.compile(r"\[base:\s*([^\]]*)\]")
 _ANN_CLIENT_RE: "re.Pattern[str]" = re.compile(r"\[client:\s*(yes|no)\s*\]")
 _ATTR_LINE_RE: "re.Pattern[str]" = re.compile(r"\[#([\w-]+)\]\s+(\S+)")
 _REQ_PY_RE: "re.Pattern[str]" = re.compile(r'requires-python\s*=\s*"[^"]*>=\s*(\d+)\.(\d+)')
+
+
+class GeneratedMethod(TypedDict):
+    owner: str
+    method: str
+    lineno: int
+    end_lineno: int
+
+
+class MaterializationReport(TypedDict):
+    materialized: list[str]
+    already_built: list[str]
+    unsimulated: list[str]
+    pruned_dirs: list[str]
+    generated_methods: dict[str, list[GeneratedMethod]]
+
+
+class GateResult(TypedDict):
+    raw_exit: int
+    raw_stdout: str
+    attributed_lines: list[str]
+    records: list[dict]
+    unmatched_lines: list[str]
+    candidate_lines: list[str]
+    candidate_records: list[dict]
 
 
 class FormError(Exception):
     """형식 red(exit 3) — 파싱 오류·add 실존 충돌·금지 경로·태그 이중 서술."""
 
 
 class RunError(Exception):
     """실행 불능(exit 1) — venv/인터프리터·git 실패·재료 결손."""
 
 
@@ -1735,55 +1766,71 @@
                         elif _is_repo_target(copy, origin.split(".")[0], plan):
                             uncertain.append(f"타입 `{origin}.{symbol}` 필드 선언/출처 보완 필요")
             walk(module, owner, values[0])
             if confirmed:
                 add("#202", entry.path, owner, "DTO 필드에서 domain aggregate/entity 도달: " + ", ".join(sorted(set(confirmed))), True)
             if uncertain:
                 add("#202", entry.path, owner, "; ".join(sorted(set(uncertain))) + " — 출처 보완 검토 질문", False)
     return findings
 
 
+def _generated_methods(module: ast.Module) -> list[GeneratedMethod]:
+    """이번 렌더의 함수·메서드 범위만 기록한다(기존 실물의 스텁 문구는 근거가 아니다)."""
+    result: list[GeneratedMethod] = []
+    def collect(nodes: list[ast.stmt], owner: str = "") -> None:
+        for node in nodes:
+            if isinstance(node, ast.ClassDef):
+                collect(node.body, f"{owner}.{node.name}" if owner else node.name)
+            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
+                result.append(dict(owner=owner, method=node.name, lineno=node.lineno, end_lineno=node.end_lineno))
+    collect(module.body)
+    return result
+
+
 def materialize(copy: Path, plan: Plan, *, realized: "frozenset[str]" = frozenset(),
-                base_short: str = "", promoted: "frozenset[str]" = frozenset()) -> "dict[str, list[str]]":
+                base_short: str = "", promoted: "frozenset[str]" = frozenset()) -> MaterializationReport:
     """태그 의미론(D2)대로 사본 위에 팬텀을 겹친다 — add 실존 충돌은 FormError.
 
     `promoted` = `baseline_form_errors` 가 승격 형태 예외로 통과시킨 update 경로(미시뮬레이션 문면만 다르다).
 
     **재발화 판형(`--base` 명시 — Phase 2 진입 후 명세 개정 재실행)**: `realized` 는 `lift_realized_adds` 가
     앵커 커밋 전에 사본에서 걷어낸 «기실현 add» 경로다 — 여기서는 다른 add 와 똑같이 스텁으로 실체화하고
     (materialized 에 계수) already-built 에도 «기실현 — 스텁 대체 예보»로 기록한다(이중 기재는 의도 —
     `empty(기실현)` 은 materialized 에 안 실리는 것과 구별). 사본에 실존하는 add 는 기준선 트리 실존(계획↔실물
     모순)뿐이므로 여전히 형식 red 다. `--base` 미지정 경로는 판정(exit·귀속·ID) 동일이다 — 리포트의 집계 행 문면
     (계약 실존 «자기 update 해소» 열 등)은 판과 함께 변한다.
 
     반환: materialized / already_built / unsimulated / pruned_dirs 목록(리포트 재료).
     빈 부모 정리는 Git 파일 차분이 아니므로 materialized 건수에 넣지 않는다.
     """
-    report: "dict[str, list[str]]" = {"materialized": [], "already_built": [], "unsimulated": []}
+    report: MaterializationReport = {"materialized": [], "already_built": [], "unsimulated": [],
+                                     "pruned_dirs": [], "generated_methods": {}}
     for entry in plan.entries.values():
         target: Path = copy / entry.path
         if entry.tag == "add":
             if target.exists():
-                raise FormError(f"add 충돌(실존): {entry.path} — 계획과 실물의 모순은 그 자체가 발견이다")
+                raise FormError(f"add 충돌(실존): {entry.path} — 기준선 부재·오버레이 실존: "
+                                "초기 예보의 새 파일 자리와 실물이 충돌한다. 구현 후 명세 개정은 승인 기준선을 명시한 재예보 목적을 검토한다")
             if entry.path in realized:
                 report["already_built"].append(
                     f"add(기실현 — 기준선 {base_short} 부재·오버레이 실존 → 앵커 스냅숏에서 제외·스텁 대체 예보 · "
                     f"실체화 목록에도 계수): {entry.path}")
             stub: str = render_stub(entry)
             try:
                 compile(stub, entry.path, "exec")  # symtable까지 — 중복 인자류는 ast.parse 가 못 잡는다
             except (SyntaxError, ValueError) as exc:
                 detail: str = getattr(exc, "msg", None) or str(exc)
                 raise FormError(f"스텁 렌더 파싱 불가: {entry.path} — {detail} "
                                 f"(기계 블록 전사 내용이 파이썬 문법 밖이다){_compile_hint(entry)}")
             target.parent.mkdir(parents=True, exist_ok=True)
             target.write_text(stub, encoding="utf-8")
+            report["generated_methods"][entry.path] = _generated_methods(ast.parse(stub))
             report["materialized"].append(entry.path)
         elif entry.tag == "empty":
             # add 와 같은 «새 파일» 태그 — 기준선 실존은 baseline_form_errors 가 앞서 형식 red 로 세우고, `--base` 재발화의
             # 오버레이 실존(기실현)은 lift_realized_adds 가 걷어내 여기서 빈 파일로 다시 쓴다(실체화 계수 · 도피 봉쇄).
             if target.exists():
                 raise FormError(f"empty 충돌(실존): {entry.path} — 계획과 실물의 모순은 그 자체가 발견이다")
             if entry.path in realized:
                 report["already_built"].append(
                     f"empty(기실현 — 기준선 {base_short} 부재·오버레이 실존 → 앵커 스냅숏에서 제외·빈 파일 대체 · "
                     f"실체화 목록에도 계수): {entry.path}")
@@ -1796,20 +1843,24 @@
             elif target.is_file():
                 target.unlink()
                 report["materialized"].append(f"removed {entry.path}")
             else:
                 report["unsimulated"].append(f"remove(실존 없음): {entry.path}")
         elif entry.tag == "update":
             updated: "bytes | None"
             detail: str
             updated, detail = _render_service_update(copy, entry)
             if updated is not None:
+                prior_names = {node.name for node in ast.parse(target.read_bytes()).body
+                               if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
+                report["generated_methods"][entry.path] = [item for item in _generated_methods(ast.parse(updated))
+                    if not item["owner"] and item["method"] not in prior_names]
                 target.write_bytes(updated)
             marker_update, marker_detail = _render_marker_update(copy, entry)
             if marker_update is not None:
                 updated = marker_update
             detail += "; " + marker_detail
             if updated is not None:
                 target.write_bytes(updated)
                 report["materialized"].append(entry.path)
             if entry.path in promoted:
                 report["unsimulated"].append(
@@ -1859,39 +1910,90 @@
     m: "re.Match[str] | None" = _REQ_PY_RE.search(pyproject.read_text(encoding="utf-8", errors="replace"))
     if m is None:
         return None
     lo: "tuple[int, int]" = (int(m.group(1)), int(m.group(2)))
     if cur >= lo:
         return None
     return (f"대상은 python >={lo[0]}.{lo[1]} 선언(pyproject.toml)인데 인터프리터는 "
             f"{cur[0]}.{cur[1]} 다 — fail-open 침묵 clean 위험. 대상 venv 인터프리터를 --python 으로 넘겨라")
 
 
-def run_gate(copy: Path, scratch: Path, python_bin: str) -> "tuple[int, list[str], str]":
-    """registry_gate(판정 차분) 실행 — (exit, 귀속 라인, stdout)을 돌려준다."""
+def run_gate(copy: Path, scratch: Path, python_bin: str) -> GateResult:
+    """registry 원 exit/stdout과 전체 귀속/원본 레코드 재료를 보존한다."""
     introduced: Path = scratch / "introduced.json"
     env: "dict[str, str]" = dict(os.environ)
     env["DJR_FINDINGS_JSON"] = str(scratch / "findings.jsonl")  # 스크래치 격리(D3)
     env.pop("DJR_VIOLATIONS_DIR", None)
     env.pop("DJR_SOURCE_GIT_ROOT", None)
     proc: "subprocess.CompletedProcess[str]" = subprocess.run(
         [python_bin, str(SCRIPTS_DIR / "registry_gate.py"), str(copy),
          "--anchor", "HEAD", "--introduced-json", str(introduced)],
         capture_output=True, text=True, env=env)
     if proc.returncode not in (0, 2):
         raise RunError(f"registry_gate 실행 불능(exit {proc.returncode}): "
                        f"{(proc.stderr or proc.stdout).strip()[-600:]}")
     if not introduced.is_file():
         raise RunError("registry_gate 가 introduced.json 을 남기지 않았다 — 재료 결손(fail-closed)")
-    payload: "dict[str, object]" = json.loads(introduced.read_text(encoding="utf-8"))
-    attributed: "list[str]" = [str(x) for x in payload.get("attributed_lines", [])]
-    return proc.returncode, attributed, proc.stdout
+    try:
+        payload = json.loads(introduced.read_text(encoding="utf-8"))
+    except (OSError, ValueError) as exc:
+        raise RunError(f"registry_gate introduced.json 읽기 불능 — 재료 결손: {exc}") from exc
+    if not isinstance(payload, dict):
+        raise RunError("registry_gate introduced.json 객체 부재 — 재료 결손")
+    for key, item_type in (("attributed_lines", str), ("records", dict), ("unmatched_lines", str)):
+        if not isinstance(payload.get(key), list) or any(not isinstance(x, item_type) for x in payload[key]):
+            raise RunError(f"registry_gate introduced.json {key} 결손/형식 불비(fail-closed)")
+    # 신규 후보가 0인 registry는 이 두 optional key를 모두 생략한다.
+    if ("candidate_lines" in payload) != ("candidate_records" in payload):
+        raise RunError("registry_gate 후보 채널 재료 결손(fail-closed)")
+    for key, item_type in (("candidate_lines", str), ("candidate_records", dict)):
+        value = payload.get(key, [])
+        if not isinstance(value, list) or any(not isinstance(x, item_type) for x in value):
+            raise RunError(f"registry_gate introduced.json {key} 형식 불비(fail-closed)")
+    if proc.returncode == 2 and not payload["attributed_lines"]:
+        raise RunError("registry_gate raw exit 2를 설명할 귀속 항목 부재(fail-closed)")
+    return GateResult(raw_exit=proc.returncode, raw_stdout=proc.stdout,
+        attributed_lines=payload["attributed_lines"], records=payload["records"],
+        unmatched_lines=payload["unmatched_lines"], candidate_lines=payload.get("candidate_lines", []),
+        candidate_records=payload.get("candidate_records", []))
+
+
+def partition_generated_findings(gate_result: GateResult,
+                                 generated_methods: dict[str, list[GeneratedMethod]]) -> tuple[list[str], list[str]]:
+    """전체 정규화 key의 모든 원본 위치가 생성 after_commit인 #376만 S1로 분리한다."""
+    cohorts: dict[str, list[dict]] = {}
+    for record in gate_result["records"]:
+        key = f"{record.get('checker')} :: {registry._normalize(findings.line_of_record(record), ())}"
+        cohorts.setdefault(key, []).append(record)
+    # A raw record that cannot be joined signals incomplete attribution evidence.
+    # Do not guess its cohort from rule/path or silently drop it to make a green result.
+    if any(key not in gate_result["attributed_lines"] for key in cohorts):
+        return list(gate_result["attributed_lines"]), []
+    def generated(record: dict) -> bool:
+        if record.get("rule") != "#376":
+            return False
+        location = re.fullmatch(r"(.+):(\d+)", str(record.get("file", "")))
+        if location is None:
+            return False
+        path, number = location.group(1), int(location.group(2))
+        return any(item["method"] == "after_commit" and item["owner"]
+                   and item["lineno"] <= number <= item["end_lineno"]
+                   for item in generated_methods.get(path, []))
+    retained: list[str] = []
+    deferred: list[str] = []
+    for line in gate_result["attributed_lines"]:
+        records = cohorts.get(line, [])
+        if line not in gate_result["unmatched_lines"] and records and all(generated(r) for r in records):
+            deferred.append(f"S1: 생성한 after_commit 본문 — on_commit 구현 미검증 · {line}")
+        else:
+            retained.append(line)
+    return retained, deferred
 
 
 def _stable_id(line: str) -> str:
     """예보 항목 안정 ID — sha256(규칙#+경로)[:12] (D4 처분 라벨 추적 키)."""
     m: "re.Match[str] | None" = _ATTR_LINE_RE.search(line)
     rule: str = m.group(1) if m else "?"
     where: str = m.group(2).split(":", 1)[0] if m else line
     return hashlib.sha256(f"#{rule}+{where}".encode("utf-8")).hexdigest()[:12]
 
 
@@ -2337,42 +2439,50 @@
             grouped.setdefault(line, []).append(f"{item.owner}: {item.detail}")
         lines += ["", f"### {title} ({len(grouped)}건)", ""]
         for line, details in grouped.items():
             lines.append(f"- `{_stable_id(line)}` {line} — " + "; ".join(dict.fromkeys(details)))
         if not grouped:
             lines.append("- (없음)")
     return lines
 
 
 def write_report(report_path: Path, spec: Path, base_ref: str, base_sha: str, verdict: str,
-                 attributed: "list[str]", mat: "dict[str, list[str]]",
+                 attributed: "list[str]", mat: MaterializationReport,
                  notes: "list[str]", blk_hash: str, existence: ExistenceReport,
-                 declarations: list[DeclarationFinding] | tuple[DeclarationFinding, ...] = ()) -> None:
+                 declarations: list[DeclarationFinding] | tuple[DeclarationFinding, ...] = (),
+                 *, execution_mode: str = "", raw_summary: str = "",
+                 deferred: list[str] | tuple[str, ...] = ()) -> None:
     """예보 리포트 append(D4) — 헤더 상시 문구·안정 ID·계약 실존 절(상시)·사각 목록 병기."""
     now: str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
     lines: "list[str]" = [
         "",
         f"## pre-gate 예보 — {now} · {spec.name}",
         "",
         f"- 기준선 SHA: `{base_sha}` (--base {base_ref}) — «스텁 제외 현재 상태» · "
         f"프로필: auto · 모드: 차단({MODE}) · {_executor_stamp(blk_hash)}",
         f"- {NO_SUBSTITUTE}",
         f"- {COVER_NOTE}",
+        f"- 실행 모드: {execution_mode}",
+        f"- {FILE_PLAN_NOTE}",
         f"- 판정: {verdict}",
         "",
         f"### 예보 항목 ({len(attributed)}건 · 안정 ID = sha256(규칙#+경로)[:12])",
         "",
     ]
     if attributed:
         lines.extend(f"- `{_stable_id(line)}` {line}" for line in attributed)
     else:
         lines.append("- (없음) — green 은 «설계 검증됨»이 아니라 «P/S/I급 위반 예보 0»이다.")
+    lines += ["", f"- {raw_summary}", "", f"### 생성 본문 S1 미검증 ({len(deferred)}건)", ""]
+    lines.extend(f"- {item}" for item in deferred)
+    if not deferred:
+        lines.append("- (없음)")
     lines.extend(_declaration_lines(declarations))
     lines.extend(_existence_lines(existence))
     lines += ["", f"### already-built ({len(mat.get('already_built', []))}건) · "
                   f"미시뮬레이션 ({len(mat.get('unsimulated', []))}건)", ""]
     for item in mat.get("already_built", []):
         lines.append(f"- already-built: {item}")
     for item in mat.get("unsimulated", []):
         lines.append(f"- 미시뮬레이션: {item}")
     for item in mat.get("pruned_dirs", []):
         lines.append(f"- remove 빈 부모 정리: {item}")
@@ -2385,33 +2495,36 @@
     lines.append("")
     report_path.parent.mkdir(parents=True, exist_ok=True)
     with report_path.open("a", encoding="utf-8") as fp:
         fp.write("\n".join(lines))
     print(f"\n예보 리포트 append → {report_path}")
 
 
 def write_report_stub(report_path: "Path | None", spec: Path, base_ref: str, base_sha: str,
                       verdict: str, detail: "list[str]", blk_hash: str,
                       existence: "ExistenceReport | None" = None,
-                      declarations: list[DeclarationFinding] | tuple[DeclarationFinding, ...] = ()) -> None:
+                      declarations: list[DeclarationFinding] | tuple[DeclarationFinding, ...] = (),
+                      *, execution_mode: str = "") -> None:
     """형식 red·skip 도 리포트에 사유를 남긴다(침묵 금지) — 예보 항목 없는 축약판. 실체화-0 skip 은 계약 실존 절을
     싣는다(결손 ≥1 이면 exit 5 의 근거 — kkebi S2 판형: update 소비자만의 명세)."""
     if report_path is None:
         return
     now: str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
     lines: "list[str]" = [
         "",
         f"## pre-gate 예보 — {now} · {spec.name}",
         "",
         f"- 기준선 SHA: `{base_sha}` (--base {base_ref}) · 프로필: auto · 모드: 차단({MODE}) · "
         f"{_executor_stamp(blk_hash)}",
         f"- {NO_SUBSTITUTE}",
+        f"- 실행 모드: {execution_mode}",
+        f"- {FILE_PLAN_NOTE}",
         f"- 판정: {verdict}",
         "",
     ]
     lines.extend(f"- {item}" for item in detail)
     lines.extend(_declaration_lines(declarations))
     if existence is not None:
         lines.extend(_existence_lines(existence))
     lines.append("")
     report_path.parent.mkdir(parents=True, exist_ok=True)
     with report_path.open("a", encoding="utf-8") as fp:
@@ -2442,29 +2555,31 @@
     판정에 넣지 않는다(미커밋 기실현 add 의 재라벨도 기준선 부재라 red). 기준선 이후 HEAD 실존은 사유행을 나눈다
     (자기 기실현 add 면 add 로 복원 · 타 레인 유입이면 STOP — 기준선 이동 금지) — `in_head` 는 부재 행에서만 부른다.
 
     반환: (오류 목록 — 전건, 승격 형태 예외로 통과한 update 경로 집합).
     """
     errors: "list[str]" = []
     promoted: "set[str]" = set()
     for path, entry in plan.entries.items():
         present: bool = path in in_baseline
         if entry.tag == "add" and present:
-            errors.append(f"add 충돌(실존): {path} — 계획과 실물의 모순은 그 자체가 발견이다")
+            errors.append(f"add 충돌(실존): {path} — 기준선 실존: 새 파일 add와 기준선 {base_short}의 실물이 충돌한다")
         elif entry.tag == "update" and not present:
             if _promoted_form(copy, path):
                 promoted.add(path)
             elif in_head(path):
                 errors.append(f"update 대상 기준선 이후 실존: {path} — 기준선 {base_short} 에 없고 HEAD 에 있다: "
-                              f"자기 기실현 add 면 add 로 복원 · 타 레인 유입이면 STOP(기준선 이동 금지)")
+                              f"자기 기실현 add 면 add 로 복원 · 타 레인 유입이면 STOP(기준선 이동 금지). "
+                              "초기 예보는 구현 전 계획, 명시 재예보는 승인 기준선에 대한 구현 후 명세 개정에 쓴다")
             else:
-                errors.append(f"update 대상 부재: {path} — 기준선 {base_short} 에 없는 경로는 add 다(재라벨 도피 금지)")
+                errors.append(f"update 대상 부재: {path} — 기준선 {base_short} 에 없는 경로는 add 다(재라벨 도피 금지). "
+                              "초기 예보는 구현 전 계획, 명시 재예보는 승인 기준선에 대한 구현 후 명세 개정에 쓴다")
         elif entry.tag == "remove" and not entry.deferred_remove and not present:
             errors.append(f"remove 대상 부재: {path} — 기준선 {base_short} 에 없는 경로는 제거할 수 없다"
                           f"(고정 기준선에서 기실현 remove 는 실존이다 — 이미 지워진 경로는 행을 거둔다)")
         elif entry.tag == "empty" and present:
             # `empty` 는 add 와 같은 «새 파일» 태그다 — 기준선 실존을 already-built 로 통과시키면 기실현 add 를 empty 로
             # 재라벨해 실체화 0 으로 도피하는 경로가 update 재라벨과 동형으로 남는다(6단계 감사 MAJOR-1).
             errors.append(f"empty 충돌(실존): {path} — 새 빈 파일 자리가 기준선 {base_short} 에 이미 있다: "
                           f"기실현이면 update 다(재라벨 도피 금지)")
     return errors, frozenset(promoted)
 
@@ -2535,20 +2650,22 @@
     if hash_m is None:
         problems.append("최신성 증명 불가 — 마지막 헤더에 블록 해시 토큰이 없다(구판 리포트) · 재발화")
     elif report_hash != spec_hash:
         problems.append(f"stale — 명세 블록 해시 {spec_hash} ≠ 마지막 예보 {report_hash} · 재발화")
     count_m: "re.Match[str] | None" = _REPORT_COUNT_RE.search(verdict)
     defect_m: "re.Match[str] | None" = _REPORT_DEFECT_RE.search(verdict)
     attributed: int = int(count_m.group(1)) if count_m else 0
     defects: int = int(defect_m.group(1)) if defect_m else 0
     declarations: int = len(set(_REPORT_ID_RE.findall(_subsection(section, "선언 확정"))))
     candidates: int = len(set(_REPORT_ID_RE.findall(_subsection(section, "선언 후보"))))
+    deferred_section = _subsection(section, "생성 본문 S1 미검증")
+    deferred_count = sum(line.startswith("- S1:") for line in deferred_section.splitlines())
     short: str
     if verdict.startswith("형식 red"):
         problems.append(f"형식 red 미해소 — 마지막 판정 «{verdict}» · architect 반송")
         short = "형식 red"
     elif verdict.startswith("예보 red"):
         ids: "list[str]" = list(dict.fromkeys(_REPORT_ID_RE.findall(_subsection(section, "예보 항목"))
                     + _REPORT_ID_RE.findall(_subsection(section, "선언 확정"))))
         missing: "list[str]" = [i for i in ids if not _disposed(section, i)]
         if missing:
             problems.append(f"처분 미기재 {len(missing)}건(ignored|filtered 행 없음 — corrected 는 재실행이 최종본): "
@@ -2561,21 +2678,21 @@
         if "<!-- machine:" not in spec_text:
             # 구형 명세 + 관찰기(≤2.17.16)의 «블록 부재 skip» 스텁이 마지막 절로 남은 레인 — 블록 해시가 불변이라 캐시 skip 으로
             # 재실행 없이 G2 가 열리는 좁은 경로를 닫는다(5단계 리뷰 C · 결정 잔여 1): 차단 모드에서 블록 부재는 형식 red 다.
             problems.append("블록 부재 — 마지막 판정이 관찰 모드 skip 이고 명세에 machine 마커가 없다: 소급 블록 작성 후 재발화")
     else:
         problems.append(f"판정 문면 불명 — «{verdict}»")
         short = verdict[:24]
     info: "dict[str, str]" = {
         "spec_hash": spec_hash, "report_hash": report_hash, "short": short,
         "attributed": str(attributed), "defects": str(defects),
-        "declarations": str(declarations), "candidates": str(candidates),
+        "declarations": str(declarations), "candidates": str(candidates), "deferred": str(deferred_count),
         "base": base_m.group(1)[:12] if base_m else "-",
     }
     return (3 if problems else 0), problems, info
 
 
 def run_check_report(spec_text: str, report_path: Path, blk_hash: str) -> int:
     """`--check-report` 진입 — 배너(G1/G1′)·G2 근거 대조의 유일한 기계 출처(`요약:` 행)."""
     print(f"# design_pregate --check-report · 모드 차단({MODE}) · {_executor_stamp(blk_hash)}")
     if not report_path.is_file():
         print(f"실행 불능: 리포트 부재 — {report_path} (pre-gate 가 이 레인에서 한 번도 실행되지 않았다 · 구형 명세·"
@@ -2587,21 +2704,21 @@
     problems: "list[str]" = result[1]
     info: "dict[str, str]" = result[2]
     if code == 1:
         print(f"실행 불능: {problems[0]}", file=sys.stderr)
         return 1
     for p in problems:
         print(f"  불비: {p}")
     status: str = "정합" if code == 0 else f"불비 {len(problems)}건"
     print(f"\n요약: check-report {status} · 블록 해시 {info['spec_hash']}={info['report_hash']} · "
           f"마지막 판정 {info['short']} · 귀속 {info['attributed']}건 · 선언 확정 {info['declarations']}건 · "
-          f"선언 후보 {info['candidates']}건 · 실존 결손 {info['defects']}건 · "
+          f"선언 후보 {info['candidates']}건 · S1 미검증 {info['deferred']}건 · 실존 결손 {info['defects']}건 · "
           f"기준선 {info['base']}")
     return code
 
 
 # ── main ────────────────────────────────────────────────────────────────────
 
 def main(argv: "list[str]") -> int:
     ap: _UsageParser = _UsageParser(add_help=True, description="design-spec pre-gate 예보 실행기")
     ap.add_argument("spec", help="설계 명세 markdown(기계 블록 §4 포함)")
     ap.add_argument("target", help="대상 저장소 루트(git)")
@@ -2632,59 +2749,62 @@
         print(f"블록 해시 {blk_hash}")
         return 0
     if ns.check_report is not None:
         return run_check_report(text, Path(ns.check_report).resolve(), blk_hash)
     if not (repo / ".git").exists():
         print(f"실행 불능: git 저장소가 아니다 — {repo} (차분 예보는 git 앵커가 전제다)", file=sys.stderr)
         return 1
 
     base_ref: str = ns.base or "HEAD"
     explicit_base: bool = ns.base is not None
+    execution_mode = f"명시 재예보(--base {base_ref})" if explicit_base else "초기 예보(기준선 기본 HEAD)"
+    print(f"실행 모드: {execution_mode}")
+    print(FILE_PLAN_NOTE)
     rev: "subprocess.CompletedProcess[bytes]" = _git(repo, "rev-parse", "--verify",
                                                      f"{base_ref}^{{commit}}", check=False)
     if rev.returncode != 0:
         print(f"실행 불능: --base {base_ref!r} resolve 불능 — "
               f"{rev.stderr.decode('utf-8', 'replace').strip()}", file=sys.stderr)
         return 1
     base_sha: str = rev.stdout.decode("ascii").strip()
 
     gap: "str | None" = _interpreter_gap_reason(repo, ns.python_bin)
     if gap is not None:
         print(f"실행 불능: {gap}", file=sys.stderr)
         return 1
 
     plan_result: "tuple[Plan | None, list[str]]" = parse_spec(text)
     plan: "Plan | None" = plan_result[0]
     errors: "list[str]" = plan_result[1]
     if errors:
         print(f"형식 red — {len(errors)}건 (기계 블록이 규범 문법 밖이다 · architect 반송 재료):")
         for err in errors:
             print(f"  {err}")
-        write_report_stub(report_path, spec_path, base_ref, base_sha, "형식 red", errors, blk_hash)
+        write_report_stub(report_path, spec_path, base_ref, base_sha, "형식 red", errors, blk_hash, execution_mode=execution_mode)
         print(f"\n요약: 형식 red {len(errors)}건(문법) · 기준선 {base_sha[:12]} · 모드 차단")
         return 3
     if plan is None:
         reason: str = ("형식 red — machine 블록 부재(<!-- machine: file-plan --> 없음): 차단 모드는 블록이 의무다 — "
                        "구형 명세(형식 규범 이전 승인)는 개정 시점에 블록을 소급 작성한다"
                        "(기준선 실존 경로는 update · 부재 경로만 add)")
         print(reason)
-        write_report_stub(report_path, spec_path, base_ref, base_sha, "형식 red(블록 부재)", [reason], blk_hash)
+        write_report_stub(report_path, spec_path, base_ref, base_sha, "형식 red(블록 부재)", [reason], blk_hash, execution_mode=execution_mode)
         print(f"\n요약: 형식 red 1건(블록 부재) · 기준선 {base_sha[:12]} · 모드 차단")
         return 3
     if not plan.entries:
         reason = ("형식 red — file-plan 0행(블록 공허): 변경 파일이 없는 명세는 pre-gate 대상이 아니라 산문이다 — "
                   "update 대상이라도 적는다(빈 펜스로 블록 의무를 채울 수 없다)")
         print(reason)
         for note in plan.notes:  # 고아 채널 행(symbols/imports 만 있는 명세)은 버려졌음을 남긴다(침묵 금지)
             print(f"  채널 메모: {note}")
         write_report_stub(report_path, spec_path, base_ref, base_sha, "형식 red(블록 공허)",
-                          [reason] + [f"채널 메모: {n}" for n in plan.notes], blk_hash)
+                          [reason] + [f"채널 메모: {n}" for n in plan.notes], blk_hash, execution_mode=execution_mode)
         print(f"\n요약: 형식 red 1건(블록 공허) · 기준선 {base_sha[:12]} · 모드 차단")
         return 3
 
     scratch: Path = Path(tempfile.mkdtemp(prefix="design-pregate-"))
     copy: Path = scratch / "copy"
     try:
         copy.mkdir(parents=True)
         _extract_archive(repo, base_sha, copy)
         # archive == 기준선 트리 — 오버레이 «전»에 계획 경로의 실존을 재서 «기준선 실존 add»(형식 red 유지)와
         # «오버레이 실존 add»(재발화 판형의 기실현)를 가른다(git 추가 호출 0·결정적).
@@ -2697,37 +2817,37 @@
             (lambda p: _git(repo, "cat-file", "-e", f"HEAD:{p}", check=False).returncode == 0)
             if explicit_base else (lambda p: False))
         form_errors: "list[str]" = form_result[0]
         promoted: "frozenset[str]" = form_result[1]
         if form_errors:
             print(f"형식 red — {len(form_errors)}건 (계획↔기준선 모순 · architect 반송 재료):")
             for err in form_errors:
                 print(f"  {err}")
             if promoted:
                 print(f"  승격 형태 예외 통과 {len(promoted)}건: " + " ".join(sorted(promoted)))
-            write_report_stub(report_path, spec_path, base_ref, base_sha, "형식 red", form_errors, blk_hash)
+            write_report_stub(report_path, spec_path, base_ref, base_sha, "형식 red", form_errors, blk_hash, execution_mode=execution_mode)
             print(f"\n요약: 형식 red {len(form_errors)}건({_error_kinds(form_errors)}) · "
                   f"기준선 {base_sha[:12]} · 모드 차단")
             return 3
         overlaid: "list[str]" = _overlay_dirty(repo, copy)
         # 기실현 add 는 앵커 커밋 «전»에 걷어낸다 — 앵커 스냅숏(L)에 실물이 남으면 스텁 진단이 잔존으로 빠진다.
         realized: "frozenset[str]" = lift_realized_adds(copy, plan, explicit_base, in_baseline)
         _git(copy, "init", "-q")
         _git(copy, "add", "-A")
         _git(copy, "commit", "-q", "-m", "pregate-anchor", "--allow-empty")
 
         try:
-            mat: "dict[str, list[str]]" = materialize(copy, plan, realized=realized, base_short=base_sha[:12],
+            mat: MaterializationReport = materialize(copy, plan, realized=realized, base_short=base_sha[:12],
                                                       promoted=promoted)
         except FormError as exc:
             print(f"형식 red — {exc}")
-            write_report_stub(report_path, spec_path, base_ref, base_sha, "형식 red", [str(exc)], blk_hash)
+            write_report_stub(report_path, spec_path, base_ref, base_sha, "형식 red", [str(exc)], blk_hash, execution_mode=execution_mode)
             print(f"\n요약: 형식 red 1건({_error_kinds([str(exc)])}) · 기준선 {base_sha[:12]} · 모드 차단")
             return 3
 
         # 계약 실존 — materialize(+골격·`__init__` 체인) 뒤 · 실체화-0 분기 앞(update 소비자만의 명세도 판정한다).
         declarations = check_declarations(plan, copy)
         declaration_count = len({(item.rule, item.path) for item in declarations if item.confirmed})
         for line in _declaration_lines(declarations):
             print(line)
         existence: ExistenceReport = check_import_existence(copy, plan)
         own_note: "str | None" = _own_interpreter_note(repo)
@@ -2745,51 +2865,57 @@
             print(reason)
             for note in plan.notes:
                 print(f"  채널 메모: {note}")
             for item in mat["unsimulated"]:
                 print(f"  미시뮬레이션: {item}")
             _print_existence(existence)
             print(f"\n요약: 실체화 0 · 실존 결손 {defects}건 · 선언 확정 {declaration_count}건 · 기준선 {base_sha[:12]} · 모드 차단")
             write_report_stub(report_path, spec_path, base_ref, base_sha, verdict_stub,
                               [reason] + [f"미시뮬레이션: {x}" for x in mat["unsimulated"]] + cleanup_notes
                               + [f"채널 메모: {n}" for n in plan.notes], blk_hash,
-                              existence=existence, declarations=declarations)
+                              existence=existence, declarations=declarations, execution_mode=execution_mode)
             return 2 if declaration_count else (5 if defects else 4)
 
         print(f"# design_pregate — 예보 실행 · 기준선 {base_sha[:12]} (--base {base_ref}) · "
               f"모드 차단({MODE}) · {_executor_stamp(blk_hash)}")
         print(f"({NO_SUBSTITUTE})")
         print(f"실체화 {len(mat['materialized'])}건 · dirty overlay {len(overlaid)}건 · "
               f"미시뮬레이션 {len(mat['unsimulated'])}건 · already-built {len(mat['already_built'])}건")
 
-        gate_result: "tuple[int, list[str], str]" = run_gate(copy, scratch, ns.python_bin)
-        gate_exit: int = gate_result[0]
-        attributed: "list[str]" = gate_result[1]
-        print("\n" + gate_result[2].rstrip())
+        gate_result = run_gate(copy, scratch, ns.python_bin)
+        attributed, deferred = partition_generated_findings(gate_result, mat["generated_methods"])
+        print("\n== 원 registry 결과 ==\n" + gate_result["raw_stdout"].rstrip())
+        raw_summary = (f"원 registry 결과: exit {gate_result['raw_exit']} · 귀속 {len(gate_result['attributed_lines'])}건 · "
+                       f"유지 {len(attributed)}건 · S1 미검증 {len(deferred)}건")
+        print(raw_summary)
+        print(f"\n== 생성 본문 S1 미검증 ({len(deferred)}건) ==")
+        for line in deferred:
+            print(f"  {line}")
 
         verdict: str = ("예보 green — P/S/I급 결정 계약 위반 예보 0(«설계 검증됨» 아님)"
-                        if gate_exit == 0 and not declaration_count else
+                        if not attributed and not declaration_count else
                         f"예보 red — P/S/I급 결정 계약 위반 예보 {len(attributed)}건")
         verdict += f" · 선언 확정 {declaration_count}건"
         verdict += f" · 계약 실존 결손 {defects}건(권고·비차단)"
         print(f"\n== 예보 항목 {len(attributed)}건 ==")
         for line in attributed:
             print(f"  `{_stable_id(line)}` {line}")
         for note in plan.notes:
             print(f"  채널 메모: {note}")
         _print_existence(existence)
         print(f"\n판정: {verdict}")
         print(f"요약: 귀속 {len(attributed)}건 · 실존 결손 {defects}건 · 기준선 {base_sha[:12]} · 모드 차단")
         if report_path is not None:
             write_report(report_path, spec_path, base_ref, base_sha, verdict,
-                         attributed, mat, plan.notes, blk_hash, existence, declarations)
-        if gate_exit != 0 or declaration_count:
+                         attributed, mat, plan.notes, blk_hash, existence, declarations,
+                         execution_mode=execution_mode, raw_summary=raw_summary, deferred=deferred)
+        if attributed or declaration_count:
             return 2
         return 5 if defects else 0
     except RunError as exc:
         print(f"실행 불능: {exc}", file=sys.stderr)
         return 1
     finally:
         if ns.keep:
             print(f"(--keep) 격리 사본 보존: {scratch}")
         else:
             shutil.rmtree(scratch, ignore_errors=True)

```

## workspace/tools/pregate_field_report_smoke.py

Before SHA256: 58372ea10464d45a2af681b8284b4c343c553746b15411c982eac454b3fa8b29
After SHA256: 762f87d073fa774035fe15eeaa4fdd9a17834ddd9e66a2585c82fa327f66b0e0

```diff
--- before/workspace/tools/pregate_field_report_smoke.py
+++ after/workspace/tools/pregate_field_report_smoke.py
@@ -1,27 +1,29 @@
 #!/usr/bin/env python3
 """실제 전사·checker 회귀: OHS update의 명시 새 함수와 입장 표 첫 Python artifact.
 
 update 전사 유실, 기존 바인딩 덮기, 무명시 raise 추론, support로 marker 전파를 잡는다.
 """
 from __future__ import annotations
 
 import ast
 import os
+import json
+from unittest.mock import patch
 import shutil
 import subprocess
 import sys
 import tempfile
 import unittest
 from pathlib import Path
 
-from pregate_fixture_run import _git, _load_module
+from pregate_fixture_run import _git, _load_module, _make_repo
 
 ROOT = Path(__file__).resolve().parents[2]
 SCRIPTS = ROOT / "dddjango/scripts"
 pg = _load_module(SCRIPTS / "design_pregate.py", "field_report_pregate")
 SERVICE_DIR = "application/garden/driving_layer/open_host_service/catalog"
 SERVICE = f"{SERVICE_DIR}/catalog_service.py"
 RESPONSE = f"{SERVICE_DIR}/contract/response/list_books_response.py"
 EXCEPTION = f"{SERVICE_DIR}/contract/exception/invalid_selection.py"
 TEST = "application/garden/test/integration/test_catalog.py"
 SUPPORT = "application/garden/test/integration/test_support.py"
@@ -400,20 +402,178 @@
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
+    def uow_fixture(self):
+        shutil.rmtree(self.source)
+        self.source = _make_repo(self.root, 'uow-source')
+        pg.materialize_skeleton(self.source, 'orders')
+        port = 'application/orders/application_layer/port/unit_of_work/order_unit_of_work.py'
+        impl = 'application/orders/driven_layer/adapter/persistence/unit_of_work/order_unit_of_work.py'
+        self.write(self.source, port, 'from abc import ABC, abstractmethod\nclass OrdersUnitOfWork(ABC):\n'
+                   '    @abstractmethod\n    def __enter__(self): ...\n'
+                   '    @abstractmethod\n    def __exit__(self, *args): ...\n'
+                   '    @abstractmethod\n    def after_commit(self, callback): ...\n')
+        self.write(self.source, impl, 'class DjangoOrdersUnitOfWork:\n'
+                   '    def after_commit(self, callback):\n'
+                   '        transaction.on_commit(callback, robust=True)\n')
+        _git(self.source, 'add', '-A')
+        _git(self.source, 'commit', '-qm', 'uow baseline')
+        return port, impl
+
+    def test_generated_uow_cli_defers_only_generated_body_and_preserves_original(self):
+        port, impl = self.uow_fixture()
+        # Baseline port exists, while a newly planned implementation is generated.
+        _git(self.source, 'rm', impl)
+        _git(self.source, 'commit', '-qm', 'implementation pending')
+        text = spec_text([f'add {impl}'], [f'{impl}::DjangoOrdersUnitOfWork',
+            f'{impl}::DjangoOrdersUnitOfWork.after_commit(callback: object) -> None'])
+        before = {p.relative_to(self.source): p.read_bytes() for p in self.source.rglob('*.py')}
+        run, report = self.cli(text)
+        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
+        self.assertIn('생성 본문 S1 미검증 (1건)', report)
+        self.assertIn('원 registry 결과: exit 2 · 귀속 1건 · 유지 0건 · S1 미검증 1건', report)
+        self.assertIn('[#376]', report)
+        self.assertEqual({p.relative_to(self.source): p.read_bytes() for p in self.source.rglob('*.py')}, before)
+        checked = subprocess.run([sys.executable, '-B', str(SCRIPTS / 'design_pregate.py'),
+            str(self.root / 'design.md'), str(self.source), '--check-report', str(self.root / 'report.md')],
+            capture_output=True, text=True, env=self.env)
+        self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)
+        self.assertIn('S1 미검증 1건', checked.stdout)
+        # Declaration-confirmed errors still block when the only registry finding is deferred.
+        response = 'application/orders/application_layer/orders/read_orders/read_orders_result.py'
+        self.write(self.source, response, 'class ReadOrdersResult: pass\n')
+        _git(self.source, 'add', '-A')
+        _git(self.source, 'commit', '-qm', 'declaration fixture')
+        combined = self.effects(text.replace('```paths\n', f'```paths\nupdate {response}\n')
+                                .replace('```symbols\n', f'```symbols\n{response}::ReadOrdersResult\n'),
+                                f'{response}::ReadOrdersResult  read-only  uow=OrdersUnitOfWork')
+        run, report = self.cli(combined)
+        self.assertEqual(run.returncode, 2, run.stdout + run.stderr)
+        self.assertIn('생성 본문 S1 미검증 (1건)', report)
+        self.assertIn('선언 확정 (1건)', report)
+        self.assertEqual(pg.check_report(combined, report)[0], 3)
+
+    def test_real_uow_cli_retains_bad_body_and_missing_robust_even_stub_text(self):
+        port, impl = self.uow_fixture()
+        added = 'application/orders/domain_layer/shared_value_object/lane_marker.py'
+        text = spec_text([f'update {impl}', f'add {added}'], [f'{added}::LaneMarker {{value: str}}'])
+        for body, rule in [('raise NotImplementedError', '#376'),
+                           ('transaction.on_commit(callback)', '#566')]:
+            original = ('"""pre-gate 팬텀 스텁."""\nclass DjangoOrdersUnitOfWork:\n'
+                        '    def after_commit(self, callback):\n        ' + body + '\n')
+            self.write(self.source, impl, original)
+            result = pg.run_gate(self.source, self.root, sys.executable)
+            self.assertEqual(result['raw_exit'], 2, result['raw_stdout'])
+            retained, deferred = pg.partition_generated_findings(result, {})
+            self.assertTrue(any(f'[{rule}]' in line for line in retained), retained)
+            self.assertEqual(deferred, [])
+            self.assertEqual((self.source / impl).read_text(), original)
+            # Pregate's ordinary dirty update is in its own anchor: it remains legacy.
+            run, report = self.cli(text)
+            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
+            self.assertIn('생성 본문 S1 미검증 (0건)', report)
+            self.assertEqual((self.source / impl).read_text(), original)
+
+    def test_provenance_records_only_current_render_ast_ranges(self):
+        path = 'application/garden/driven_layer/adapter/persistence/unit_of_work/garden_unit_of_work.py'
+        text = spec_text([f'add {path}', f'update {SERVICE}'], [f'{path}::DjangoGardenUnitOfWork',
+            f'{path}::DjangoGardenUnitOfWork.after_commit(callback: object) -> None',
+            f'{path}::DjangoGardenUnitOfWork.__enter__() -> None', f'{SERVICE}::new_query() -> str'])
+        _, report = self.materialize(text)
+        generated = report['generated_methods']
+        module = ast.parse((self.copy / path).read_text())
+        cls = next(node for node in module.body if isinstance(node, ast.ClassDef))
+        methods = [node for node in cls.body if isinstance(node, ast.FunctionDef)]
+        self.assertEqual(generated[path], [dict(owner='DjangoGardenUnitOfWork', method=node.name,
+            lineno=node.lineno, end_lineno=node.end_lineno) for node in methods])
+        self.assertEqual([item['method'] for item in generated[SERVICE]], ['new_query'])
+        new_node = next(node for node in ast.parse((self.copy / SERVICE).read_text()).body
+                        if isinstance(node, ast.FunctionDef) and node.name == 'new_query')
+        self.assertEqual(generated[SERVICE][0]['lineno'], new_node.lineno)
+        self.assertEqual(generated[SERVICE][0]['end_lineno'], new_node.end_lineno)
+        self.assertTrue((self.copy / SERVICE).read_bytes().startswith(ORIGINAL.encode()))
+        self.write(self.source, path, 'class DjangoGardenUnitOfWork:\n'
+                   '    def after_commit(self, callback):\n        raise NotImplementedError\n')
+        _, report = self.materialize(spec_text([f'update {path}']))
+        self.assertNotIn(path, report['generated_methods'])
+
+    def test_generated_partition_uses_full_normalized_cohort_and_all_raw_locations(self):
+        path = 'application/orders/driven_layer/adapter/persistence/unit_of_work/order_unit_of_work.py'
+        message = 'after_commit 구현이 transaction.on_commit 으로 채워지지 않았다'
+        line = f'check-port-adapter-pairing.py :: [#376] {path}:N: {message}'
+        records = [dict(checker='check-port-adapter-pairing.py', rule='#376', severity='error',
+                        file=f'{path}:{n}', message=message) for n in (5, 15)]
+        generated = {path: [dict(owner='First', method='after_commit', lineno=5, end_lineno=6),
+                            dict(owner='Second', method='after_commit', lineno=15, end_lineno=16)]}
+        def gate(rows, unmatched=(), lines=None):
+            return dict(raw_exit=2, raw_stdout='raw', attributed_lines=lines or [line], records=rows,
+                        unmatched_lines=list(unmatched), candidate_lines=[], candidate_records=[])
+        for rows, provenance, unmatched, want in [
+            (records, generated, [], (0, 1)),
+            (records, {path: generated[path][:1]}, [], (1, 0)),
+            ([records[0], dict(records[1], file=path)], generated, [], (1, 0)),
+            ([records[0], dict(records[1], file=f'{path}:N', file_raw=f'/tmp/raw/{path}:15')],
+             generated, [], (1, 0)),
+            ([], generated, [], (1, 0)),
+            (records, generated, [line], (1, 0)),
+            (records, {}, [], (1, 0)),
+            (records, {path: [dict(generated[path][0], method='other')]}, [], (1, 0)),
+        ]:
+            with self.subTest(rows=rows, provenance=provenance, unmatched=unmatched):
+                retained, deferred = pg.partition_generated_findings(gate(rows, unmatched), provenance)
+                self.assertEqual((len(retained), len(deferred)), want)
+        # Same rule/path with a different message is a different attribution key.
+        other = dict(records[1], file=f'{path}:25', message='other diagnostic')
+        other_line = f'check-port-adapter-pairing.py :: [#376] {path}:N: other diagnostic'
+        retained, deferred = pg.partition_generated_findings(gate(records + [other], lines=[line, other_line]), generated)
+        self.assertEqual(retained, [other_line])
+        self.assertEqual(len(deferred), 1)
+        robust = dict(records[0], rule='#566')
+        robust_line = line.replace('#376', '#566')
+        self.assertEqual(pg.partition_generated_findings(gate([robust], lines=[robust_line]), generated), ([robust_line], []))
+
+    def test_run_gate_preserves_complete_material_and_optional_candidates(self):
+        record = dict(checker='checker.py', rule='#376', severity='error', file='sample.py:5', message='bad')
+        line = 'checker.py :: [#376] sample.py:N: bad'
+        payload = dict(attributed_lines=[line], records=[record], unmatched_lines=[])
+        for candidates in ({}, dict(candidate_lines=['candidate'], candidate_records=[dict(record, severity='info')])):
+            (self.root / 'introduced.json').write_text(json.dumps(dict(payload, **candidates)))
+            proc = subprocess.CompletedProcess([], 2, 'raw stdout untouched', '')
+            with patch.object(pg.subprocess, 'run', return_value=proc):
+                result = pg.run_gate(self.source, self.root, sys.executable)
+            self.assertEqual(result['raw_exit'], 2)
+            self.assertEqual(result['raw_stdout'], 'raw stdout untouched')
+            self.assertEqual(result['attributed_lines'], [line])
+            self.assertEqual(result['records'], [record])
+            self.assertEqual(result['unmatched_lines'], [])
+            self.assertEqual(result['candidate_lines'], candidates.get('candidate_lines', []))
+            self.assertEqual(result['candidate_records'], candidates.get('candidate_records', []))
+
+    def test_run_gate_rejects_missing_material_and_unexplained_raw_red(self):
+        complete = dict(attributed_lines=[], records=[], unmatched_lines=[])
+        for code, payload in [(1, complete), (2, complete), (0, {}),
+                (0, dict(complete, records=None)), (0, dict(complete, candidate_lines=[])),
+                (0, dict(complete, unmatched_lines=None)), (0, dict(complete, attributed_lines=None))]:
+            with self.subTest(code=code, payload=payload):
+                (self.root / 'introduced.json').write_text(json.dumps(payload))
+                proc = subprocess.CompletedProcess([], code, 'raw stdout', '')
+                with patch.object(pg.subprocess, 'run', return_value=proc):
+                    with self.assertRaises(pg.RunError):
+                        pg.run_gate(self.source, self.root, sys.executable)
 
     def test_declaration_only_cli_and_report_dispositions(self):
         text = self.effects(spec_text([f'update {SERVICE}'], [f'{SERVICE}::ReadBooks']),
                             f'{SERVICE}::ReadBooks  read-only  uow=BookUnitOfWork')
         run, report = self.cli(text)
         self.assertEqual(run.returncode, 2, run.stdout + run.stderr)
         self.assertIn('선언 확정', report)
         self.assertEqual(pg.check_report(text, report)[0], 3)
         stable = pg._stable_id(f'[#197] {SERVICE}')
         disposed = report + f'\n- `{stable}` **ignored** 명시 검토\n'

```

## workspace/tools/pregate_fixture_run.py

Before SHA256: 5a6daf354bd6b57147a69ac22f03d00086756a34cb591116d4b1778efc1b229d
After SHA256: 29a1aa46ea7a8979c04230fc8afb2adc31745eecde2b059abd7edb3578e43539

```diff
--- before/workspace/tools/pregate_fixture_run.py
+++ after/workspace/tools/pregate_fixture_run.py
@@ -925,31 +925,69 @@
             code, problems, info = dp.check_report(noblock_text, head(dp.block_hash(noblock_text), "skip"))
         else:
             code, problems, info = dp.check_report(spec_text, text)
         blob: str = " ".join(problems) + " " + " ".join(info.values())
         if code != want_code or needle not in blob or (want_n is not None and len(problems) != want_n):
             out.append(f"check_report[{label}] = exit {code} · {problems} · {info.get('short')} ≠ 기대 exit {want_code}·«{needle}»"
                        + (f"·사유 {want_n}" if want_n is not None else ""))
     return out
 
 
+def _run_execution_modes_bundle(scratch: Path, failures: list[str]) -> None:
+    """12 CLI combinations retain tag semantics and explain initial versus explicit reforecast."""
+    for baseline in (False, True):
+        repo = _make_repo(scratch, f'modes-{baseline}')
+        target = repo / MID_ADD
+        target.parent.mkdir(parents=True, exist_ok=True)
+        original = 'class LaneMarker:\n    value: str\n'
+        target.write_text(original)
+        if baseline:
+            _git(repo, 'add', '-A')
+            _git(repo, 'commit', '-qm', 'mode baseline')
+        for tag in ('add', 'empty', 'update'):
+            for explicit in (False, True):
+                spec = scratch / 'mode-spec.md'
+                spec.write_text('<!-- machine: file-plan -->\n```paths\n' + f'{tag} {MID_ADD}\n```\n'
+                    '<!-- machine: symbols -->\n```symbols\n' + (f'{MID_ADD}::LaneMarker {{value: str}}\n'
+                    if tag == 'add' else '') + '```\n')
+                report = scratch / f'mode-{baseline}-{tag}-{explicit}.md'
+                run = _run_pregate(spec, repo, report, ['--base', 'HEAD'] if explicit else [])
+                expected = (4 if tag == 'update' else 3) if baseline else (3 if tag == 'update' or not explicit else 0)
+                label = f'mode baseline={baseline} tag={tag} explicit={explicit}'
+                text = report.read_text() if report.exists() else ''
+                mode = '명시 재예보(--base HEAD)' if explicit else '초기 예보(기준선 기본 HEAD)'
+                cause = ('기준선 실존' if baseline else '기준선 부재·오버레이 실존') if tag == 'add' else ''
+                if run.returncode != expected or mode not in run.stdout or mode not in text:
+                    failures.append(f'{label}: exit {run.returncode} != {expected} or missing execution mode\n{run.stdout}{run.stderr}')
+                if expected == 3 and cause and cause not in text:
+                    failures.append(f'{label}: missing specific cause {cause}')
+                if tag == 'update' and not baseline and not all(x in text for x in ('초기 예보', '재예보')):
+                    failures.append(f'{label}: absent update needs both execution purposes')
+                if '승인 제품 변경' not in text or '작업 기록' not in text:
+                    failures.append(f'{label}: file-plan scope guidance absent')
+                if target.read_text() != original:
+                    failures.append(f'{label}: source bytes changed')
+                print(f'{label}: exit {run.returncode} (expected {expected})')
+
+
 def main(argv: "list[str]") -> int:
     ap: argparse.ArgumentParser = argparse.ArgumentParser(description="pre-gate 픽스처 러너")
     ap.add_argument("--keep", action="store_true", help="합성 저장소 보존(디버그)")
     ns: argparse.Namespace = ap.parse_args(argv)
 
     scratch: Path = Path(tempfile.mkdtemp(prefix="pregate-fixture-"))
     failures: "list[str]" = []
     failures.extend(_unit_checks())
     failures.extend(_existence_unit_checks())
     failures.extend(_enforce_unit_checks())
     try:
+        _run_execution_modes_bundle(scratch, failures)
         _run_base_bundle(scratch, failures)
         _run_p1_bundle(scratch, failures)
         _run_mid_bundle(scratch, failures)
         _run_imports_bundle(scratch, failures)
         _run_enforce_bundle(scratch, failures)
         _run_checkreport_bundle(scratch, failures)
 
         if failures:
             print("\nFAIL — pre-gate 픽스처 기대 불일치:")
             for f in failures:

```
