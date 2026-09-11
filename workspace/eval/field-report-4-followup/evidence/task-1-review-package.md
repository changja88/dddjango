# Task1 review package
Base HEAD: 3355710dcbaf023a16856cb2f307aa2a03fc0996
Commits: none (authorized uncommitted task). Baseline bytes are task-1-before/.

## Changed files / SHA-256
- dddjango/scripts/design_pregate.py: 88a34edc871c4a196adf8fca4e9d00f0ee01d144cba848b1e033e6e75fd3b252 -> 48530e08a5a532e1210513234c8560609249190381a618f5bd4d6968fcaea71d
- codex-dddjango/skills/dddjango/scripts/design_pregate.py: 88a34edc871c4a196adf8fca4e9d00f0ee01d144cba848b1e033e6e75fd3b252 -> 48530e08a5a532e1210513234c8560609249190381a618f5bd4d6968fcaea71d
- workspace/tools/pregate_field_report_smoke.py: 7ae26bffa9e8dbe3aa027a66faf3c6c3c7b74fc183cd80d0e5ede8ff86a5c9fa -> bc62b670fa7dfe4b88444d8ee63a2bd8b56bf6b8953d05dc5493f5805f084a69

## Full diff (10 lines context)
```diff
--- a/dddjango/scripts/design_pregate.py
+++ b/dddjango/scripts/design_pregate.py
@@ -60,23 +60,27 @@
                    1행 = `<소비 파일 경로><탭|2+공백><import 문 그대로>`.
                    행 전부가 «계약 실존» 3단 판정을 받는다 — 소비 파일의 태그·등재 여부와
                    무관(update 소비자 포함 · update 전사는 실존 OHS 서비스의 새 함수 추가 때만 충돌 검사 후).
                    판정 기준은 **이 브랜치**의 격리 사본(기준선 + dirty overlay + 명시 전사)이다: 저장소 밖(표준·서드파티)은
                    검사 밖 · 이 명세가 add 하는 대상은 자기 해소(⑶ 생략 — symbols 채널 소관 · 승격
                    폴더 부품 포함) · file-plan `update` 대상의 이름은 그 칸의 symbols 선언이면 자기
                    update 해소(S′)·현재 표면에 있으면 실존 확인·둘 다 아니면 판정 불능(표면은 이
                    명세 이후 상태 — ⑵⑶ 비적용) · ⑵ 는 이름 import(`from M import n`)의 대상 M 이 모듈
                    실현일 때만(모듈 import·패키지 `__init__` 은 ImportError 가 아니다). 세미콜론 복합행은
                    문 전부 판정. 결손은 권고·비차단.
+  use-case-effects 선택형 `<!-- machine: use-case-effects -->` + ```effects 펜스.
+                   `<파일>::<클래스>  <read-only|write>  uow=<none|타입식>`.
+                   add/update 클래스의 효과·DTO 선언은 소스 차분과 독립적으로 검증한다.
   physical-signals 영구 테스트 입장 표(6열 정본 header)의 owner/path 셀 첫 Python artifact에 정형
                    어노테이션 `[markers: a,b] [base: X] [client: yes]` — 무기재 = 부재.
-                   code span/bare token의 `.py::case`는 파일 부분만 결합한다. 뒤 support/coverage
+                   add의 code span/bare token `.py::case`는 파일 부분만 결합한다.
+                   update의 [markers:]는 module pytestmark 최종 목록이다(무기재 유지·nodeid는 S5). 뒤 support/coverage
                    주소는 대상이 아니며 첫 주소가 미등재여도 뒤 등재 파일로 건너뛰지 않는다.
   exception-map    `<!-- machine: exception-map -->` + ```exceptions 펜스.
                    1행 = `<예외 이름><탭|2+공백><raise 창구 파일 경로>` — 창구 스텁에
                    `raise <예외>()` 파일 수준 helper 합성(#456 — 번역표에 없는 예외 = 죽은 계약 = 진탐 보존).
                    update는 새 함수가 실제 전사되는 OHS 서비스만 해당하며 함수별 raise 위치는 추론하지 않는다.
 
 무엇이 아닌가: 예보는 Phase 2 step 6(G2 registry 게이트)의 실행·증거 요구를 어떤
 형태로도 대체·축약하지 않는다(D4 대체 금지). green 은 «설계 검증됨»이 아니라
 «P/S/I급 결정 계약 위반 예보 0»이다. 예보 기준선은 «스텁 제외 현재 상태»이며
 `build_anchor` 를 읽지도 쓰지도 않는다(앵커 의미론).
@@ -142,20 +146,21 @@
 # 계획 경로 선검증(D3) — `_IGNORE_COPY` 조용 소실 방지 + 숨김 세그먼트 전면 거절.
 FORBIDDEN_SEGMENTS: "frozenset[str]" = frozenset({
     "build", "dist", "staticfiles", "node_modules", "site-packages", "venv", ".dddjango",
 })
 # 기계 블록 마커 → 펜스 언어(§4). 이 어휘 밖의 machine 마커는 형식 red(fail-closed).
 MACHINE_FENCES: "dict[str, str]" = {
     "file-plan": "paths",
     "symbols": "symbols",
     "boundary-imports": "imports",
     "exception-map": "exceptions",
+    "use-case-effects": "effects",
 }
 # 영구 테스트 입장 표 정본 header 6열(조임 a — 영문 고정·셀 내 raw `|` 금지).
 SIGNALS_HEADER: "tuple[str, ...]" = (
     "candidate", "protected contract/evidence", "unique production failure",
     "existing authoritative coverage", "decision", "owner/path",
 )
 # 베이스 토큰 → import 문 합성(D2 ②상수-배선형 — 정보-무함유 규약 상수만).
 BASE_IMPORTS: "dict[str, str]" = {
     "ABC": "from abc import ABC, abstractmethod",
     "TestCase": "from django.test import TestCase",
@@ -233,50 +238,71 @@
     type_checking: bool = False
     runtime: str = ""
 
 
 @dataclass
 class Signals:
     """[신규 4] 물리 신호 어노테이션 — 무기재 = «물리 신호 없음»(fail-closed)."""
     markers: "list[str]" = field(default_factory=list)
     base: str = ""
     client: bool = False
+    markers_explicit: bool = False
 
 
 @dataclass
 class PlanEntry:
     """[신규 1] 파일 계획 1행 + 타 채널에서 결합된 실체화 재료."""
     path: str
     tag: str                     # add | update | remove | empty
     deferred_remove: bool = False  # `remove@Ln` — G1 승인 시점 상태 유지(후행 제거 격리)
     symbols: "list[Symbol]" = field(default_factory=list)
     imports: "list[str]" = field(default_factory=list)
     raises: "list[str]" = field(default_factory=list)
     signals: "Signals | None" = None
     # symbols 채널이 이 경로에 선언한 최상위 이름(클래스·함수·메서드 행의 owner) — 태그 무관 기록. `update` 칸은
     # 새 OHS 모듈 함수의 제한 전사와 별개로 계약 실존의 «자기 update 해소»(S′) 근거가 된다.
     declared: "list[str]" = field(default_factory=list)
     aliases: "list[ModuleAlias]" = field(default_factory=list)
+    declarations: list[Symbol] = field(default_factory=list)
+    declaration_aliases: list[ModuleAlias] = field(default_factory=list)
 
 
 @dataclass
 class ImportRow:
     """boundary-imports 1행 원문 — 소비 파일의 태그·등재 여부와 무관하게 보존한다(계약 실존 판정의 입력)."""
     consumer: str
     stmt: str
 
 
 @dataclass
+class UseCaseEffect:
+    path: str
+    owner: str
+    effect: str
+    uow: str
+
+
+@dataclass
+class DeclarationFinding:
+    rule: str
+    path: str
+    owner: str
+    detail: str
+    confirmed: bool
+
+
+@dataclass
 class Plan:
     """명세 1부의 전사 결과 — 실체화 입력의 전부(산문 추론 재료 0)."""
     entries: "dict[str, PlanEntry]" = field(default_factory=dict)
     notes: "list[str]" = field(default_factory=list)  # 고아 채널 행·미반영 결합(침묵 금지)
+    effects: list[UseCaseEffect] = field(default_factory=list)
     import_rows: "list[ImportRow]" = field(default_factory=list)  # 계약 실존 판정 입력(전 행 — 스텁 전사와 별개)
 
 
 @dataclass
 class ExistenceDefect:
     """계약 실존 결손 1항목 — 정체성은 (모듈, 이름)이고 단계(⑴⑵⑶)는 현재 상태다(소비자는 합친다)."""
     stage: str    # ⑴ | ⑵ | ⑶
     module: str   # 절대 점 경로(상대 import 는 소비 파일 기준 해소)
     name: str     # import 한 이름 — 모듈 import 는 ""
     detail: str   # 문면: 모듈 부재 · 자리표시자(형태 — 출처) · 심볼 미정의 `n`
@@ -515,21 +541,21 @@
     if not isinstance(target, ast.Name) or not isinstance(value, (ast.Name, ast.Attribute, ast.Subscript)):
         return None
     allowed: tuple = (ast.Name, ast.Attribute, ast.Subscript, ast.Load, ast.Tuple, ast.List,
                       ast.Constant, ast.BinOp, ast.BitOr)
     if any(not isinstance(node, allowed) for node in ast.walk(value)):
         return None
     return target.id
 
 
 def _parse_symbols(rows: "list[str]", plan: Plan, errors: "list[str]") -> None:
-    """symbols 전사. update는 모듈 함수 후보만 보존하고 모든 선언 이름은 종전대로 S′에 쓴다."""
+    """add/update 명시 선언은 검증용으로 보존하며 update 렌더 재료는 모듈 함수만 싣는다."""
     classes: "dict[tuple[str, str], Symbol]" = {}
     seen_symbols: "set[str]" = set()
     alias_names: "dict[str, set[str]]" = {}
     pending: "tuple[str, ModuleAlias] | None" = None
     for raw in rows:
         line: str = raw.strip()
         if not line or line.startswith("#"):
             continue
         m: "re.Match[str] | None" = _SYM_LINE_RE.match(line)
         if m is None:
@@ -563,20 +589,22 @@
                 pending = None
             else:
                 alias = ModuleAlias(name, statement, type_checking=branch == "TYPE_CHECKING")
                 if alias.type_checking:
                     pending = (path, alias)
                     continue
             alias_names.setdefault(path, set()).add(name)
             if entry is not None:
                 if name not in entry.declared:
                     entry.declared.append(name)
+                if entry.tag in ("add", "update"):
+                    entry.declaration_aliases.append(alias)
                 if entry.tag == "add":
                     entry.aliases.append(alias)
         elif decorator:
             owner: "Symbol | None" = classes.get((path, decorator.group(1)))
             expression: str = decorator.group(2)
             if owner is None or not _decorator_expr(expression):
                 errors.append(f"symbols decorator는 선행 클래스와 이름/호출 식이 필요하다: {path}::{rest}")
                 continue
             owner.decorators.append(expression)
         else:
@@ -585,32 +613,32 @@
                 continue
             declared_name: str = parsed.name.split(".", 1)[0]
             if declared_name in alias_names.get(path, set()):
                 errors.append(f"symbols alias와 심볼 이름 중복: {path}::{declared_name}")
                 continue
             seen_symbols.add(path)
             if entry is not None and declared_name not in entry.declared:
                 entry.declared.append(declared_name)
             if isinstance(parsed, Symbol) and parsed.kind == "class":
                 classes[(path, parsed.name)] = parsed
-            if entry is not None and entry.tag == "add":
-                if isinstance(parsed, Method):
-                    owner = classes.get((path, declared_name))
-                    if owner is None:
-                        errors.append(f"symbols 메서드 행의 선행 클래스 부재: {path}::{parsed.name}")
-                        continue
-                    owner.methods.append(Method(name=parsed.name.split(".", 1)[1],
-                                                params=parsed.params, ret=parsed.ret))
-                else:
+            if isinstance(parsed, Method):
+                owner = classes.get((path, declared_name))
+                if owner is None:
+                    errors.append(f"symbols 메서드 행의 선행 클래스 부재: {path}::{parsed.name}")
+                    continue
+                owner.methods.append(Method(name=parsed.name.split(".", 1)[1],
+                                            params=parsed.params, ret=parsed.ret))
+            elif entry is not None and entry.tag in ("add", "update"):
+                entry.declarations.append(parsed)
+                if entry.tag == "add" or parsed.kind == "function":
                     entry.symbols.append(parsed)
-            elif entry is not None and entry.tag == "update" and isinstance(parsed, Symbol) and parsed.kind == "function":
-                entry.symbols.append(parsed)
+
         if entry is None:
             plan.notes.append(f"symbols 고아 행(file-plan 미등재 — 미반영): {path}::{rest}")
             continue
         if entry.tag != "add":
             plan.notes.append(f"symbols 비-add `{entry.tag}` 칸 — update의 새 OHS 모듈 함수만 실물 대조 후 제한 전사; "
                               f"그 밖은 S5 · 선언 이름의 계약 실존 «자기 update 해소»는 별도: {path}")
     if pending:
         errors.append(f"symbols alias TYPE_CHECKING의 인접 else 부재: {pending[0]}::{pending[1].name}")
 
 
@@ -683,21 +711,21 @@
             if i < len(lines) and re.fullmatch(r"[|\s:-]+", lines[i].strip() or "x"):
                 i += 1  # 구분선
             while i < len(lines) and lines[i].strip().startswith("|"):
                 rows.append(lines[i])
                 i += 1
             continue
         i += 1
     return rows
 
 
-def _parse_signals(text: str, plan: Plan) -> None:
+def _parse_signals(text: str, plan: Plan, errors: list[str]) -> None:
     """영구 테스트 입장 표(정본 6열 header)의 owner/path 셀에서 [신규 4] 어노테이션 전사.
 
     code span/bare token에 나온 첫 Python 파일 주소가 owner artifact다. nodeid의 `.py::case`는
     파일 부분만 결합하며 뒤 support/coverage 주소로 신호를 전파하지 않는다(첫 주소 미등재도 동일).
     어노테이션이 하나도 없는 행은 «물리 신호 없음»과 같으므로 결합하지 않는다(fail-closed).
     """
     for raw in _signals_rows(text):
         cells: "list[str]" = _cells(raw)
         if len(cells) != len(SIGNALS_HEADER):
             plan.notes.append(f"입장 표 행 열 수 불일치(무시): {cells[:1]}")
@@ -708,47 +736,103 @@
         client_m: "re.Match[str] | None" = _ANN_CLIENT_RE.search(cell)
         if markers_m is None and base_m is None and client_m is None:
             continue  # 무기재 = 물리 신호 없음
         artifact: "re.Match[str] | None" = re.search(
             r"(?<![\w./-])([\w./-]+\.py)(?=::|[\s`\],;)]|$)", cell)
         path: "str | None" = artifact.group(1) if artifact else None
         if path is None:
             plan.notes.append(f"physical-signals 경로 해소 불가(owner/path 셀): {cell!r}")
             continue
         entry: "PlanEntry | None" = plan.entries.get(path)
-        if entry is None or entry.tag != "add":
-            plan.notes.append(f"physical-signals 미반영(미등재 또는 비-add): {path}")
+        if entry is None or entry.tag not in ("add", "update"):
+            plan.notes.append(f"physical-signals 미반영(미등재 또는 비-add/update): {path}")
+            continue
+        if entry.tag == "update" and cell[artifact.end():].startswith("::"):
+            plan.notes.append(f"S5 physical-signals nodeid/class는 module marker로 승격하지 않는다: {path}")
             continue
         sig: Signals = Signals()
         if markers_m is not None:
+            sig.markers_explicit = True
             sig.markers = [t.strip() for t in markers_m.group(1).split(",") if t.strip()]
+            if any(not re.fullmatch(r"[A-Za-z_]\w*", token) for token in sig.markers):
+                plan.notes.append(f"S5 physical-signals markers는 단순 identifier만 지원: {path}")
+                continue
+            if entry.signals and entry.signals.markers_explicit and entry.signals.markers != sig.markers:
+                errors.append(f"physical-signals 최종 module markers 상충: {path}")
+                continue
         if base_m is not None:
             sig.base = base_m.group(1).strip()
         sig.client = client_m is not None and client_m.group(1) == "yes"
+        if entry.tag == "update" and (base_m is not None or client_m is not None):
+            plan.notes.append(f"S5 physical-signals update base/client 미지원: {path}")
+        if entry.signals and not sig.markers_explicit:
+            sig.markers = entry.signals.markers
+            sig.markers_explicit = entry.signals.markers_explicit
         entry.signals = sig
+
+
+def _parse_effects(rows: list[str] | None, plan: Plan, errors: list[str]) -> None:
+    """선택형 효과 채널은 명시한 클래스에만 결합한다."""
+    if rows is None:
+        plan.notes.append("S5 use-case-effects 무기재 — 읽기/쓰기 효과 미검증")
+        return
+    seen: set[tuple[str, str]] = set()
+    for raw in rows:
+        if not raw.strip() or raw.lstrip().startswith("#"):
+            continue
+        match = re.fullmatch(r"(\S+)::([A-Za-z_]\w*)\s+(read-only|write)\s+uow=(.+)", raw.strip())
+        if not match:
+            errors.append(f"use-case-effects 행 파싱 불가: {raw}")
+            continue
+        path, owner, effect, uow = match.groups()
+        entry = plan.entries.get(path)
+        if (entry is None or entry.tag not in ("add", "update")
+                or not any(s.name == owner and s.kind == "class" for s in entry.declarations)):
+            errors.append(f"use-case-effects add/update 선행 클래스 부재: {path}::{owner}")
+            continue
+        if (path, owner) in seen:
+            errors.append(f"use-case-effects 중복/상충: {path}::{owner}")
+            continue
+        seen.add((path, owner))
+        uow = uow.strip()
+        try:
+            if uow != "none":
+                ast.parse(f"value: {uow}")
+                annotation = ast.parse(uow, mode="eval").body
+                if any(isinstance(n, (ast.Call, ast.NamedExpr, ast.Lambda)) for n in ast.walk(annotation)):
+                    raise ValueError("타입 표현식 밖")
+        except (SyntaxError, ValueError):
+            errors.append(f"use-case-effects uow 타입식 파싱 불가: {raw}")
+            continue
+        plan.effects.append(UseCaseEffect(path, owner, effect, uow))
 
 
 def block_hash(text: str) -> str:
     """기계가독 블록 해시 — 기계 블록 4종 + 영구 테스트 입장 표를 **파서와 같은 정규식·스캔**으로
     추출해 문서 순서 원문(verbatim)으로 이어 붙인 sha256[:12]. 출력 전용(판정 무접촉·git 0회·OS 무관).
 
     Coordinator 의 캐시 skip 판형(pre-gate 문단): `--block-hash` 값이 직전 실행 리포트 헤더의
     `블록 해시` 와 같을 때만 재실행을 skip 할 수 있다 — 같은 입력이면 같은 값, 산문만 바뀌면 같은 값,
     블록 한 글자가 바뀌면 다른 값이다(원문 기준이라 공백 변경도 재실행 쪽으로 기운다 — 안전 방향).
     """
     blocks: "dict[str, list[str]]" = _machine_blocks(text, [])
     parts: "list[str]" = []
     for name in MACHINE_FENCES:
+        if name == "use-case-effects":
+            continue
         parts.append(f"<!-- machine: {name} -->")
         parts.extend(blocks.get(name, []))
     parts.append("<!-- physical-signals -->")
     parts.extend(_signals_rows(text))
+    if "use-case-effects" in blocks:
+        parts.append("<!-- machine: use-case-effects -->")
+        parts.extend(blocks["use-case-effects"])
     return hashlib.sha256("\n".join(parts).encode("utf-8")).hexdigest()[:12]
 
 
 def plugin_version() -> str:
     """플러그인 버전 probe — 설치 레이아웃 2경로(Claude `<plugin>/.claude-plugin/plugin.json` ·
     Codex `<plugin>/skills/dddjango/scripts` 기준 `parents[2]/.codex-plugin/plugin.json`).
     실패는 `(unknown)` — 판정 영향 0(리포트 헤더 스탬프 전용). registry_gate.py 도 같은 probe 를
     각자 보유한다(두 스크립트는 독립 파일 — 러너 유닛이 동치를 가드한다)."""
     candidates: "list[Path]" = [SCRIPTS_DIR.parent / ".claude-plugin" / "plugin.json"]
     if len(SCRIPTS_DIR.parents) > 2:
@@ -767,21 +851,22 @@
     """명세 전문 → (Plan, 형식 오류 목록). file-plan 블록 부재면 (None, []) — skip 재료."""
     errors: "list[str]" = []
     blocks: "dict[str, list[str]]" = _machine_blocks(text, errors)
     if "file-plan" not in blocks and not errors:
         return None, []
     plan: Plan = Plan()
     plan.entries = _parse_file_plan(blocks.get("file-plan", []), errors)
     _parse_symbols(blocks.get("symbols", []), plan, errors)
     _parse_imports(blocks.get("boundary-imports", []), plan, errors)
     _parse_exception_map(blocks.get("exception-map", []), plan, errors)
-    _parse_signals(text, plan)
+    _parse_signals(text, plan, errors)
+    _parse_effects(blocks.get("use-case-effects"), plan, errors)
     # apps.py 정형(② 화이트리스트): django_* apps.py 심볼의 무기재 베이스는 AppConfig 규약 상수이고,
     # 결손 필드(name/label)는 정형 값으로 보충한다 — 전사된 필드는 유지(전사 우선·일탈은 예보에 실린다).
     for entry in plan.entries.values():
         if entry.path.endswith("/apps.py") and "django_" in entry.path:
             parent: PurePosixPath = PurePosixPath(entry.path).parent
             parts: "tuple[str, ...]" = parent.parts
             bc: str = parts[1] if len(parts) >= 2 and parts[0] == "application" else ""
             dotted: str = ".".join(parts)
             for sym in entry.symbols:
                 if sym.kind != "class":
@@ -1283,20 +1368,377 @@
             if any(isinstance(part, ast.NamedExpr) for expr in signature for part in ast.walk(expr)):
                 return None, "새 함수 signature의 NamedExpr는 모듈 바인딩을 바꿀 수 있어 전사하지 않는다"
         addition: str = "\n\n".join(ast.get_source_segment(stub, node) or "" for node in stub_module.body[2:])
         combined: bytes = original + ("\n\n" + addition + "\n").encode("utf-8")
         compile(combined, entry.path, "exec")  # 합성 전체의 symtable까지 검증(중복 인자 포함)
     except (SyntaxError, ValueError) as exc:
         return None, f"합성 compile 실패: {getattr(exc, 'msg', None) or str(exc)}"
     return combined, "새 모듈 함수만 전사; 기존 signature/body·decorator/alias/class update는 미시뮬레이션"
 
 
+def _render_marker_update(copy: Path, entry: PlanEntry) -> tuple[bytes | None, str]:
+    """단일 정적 module pytestmark statement만 byte 범위 치환한다."""
+    if entry.signals is None or not entry.signals.markers_explicit:
+        return None, "marker 후상태 무기재 — 유지"
+    target = copy / entry.path
+    if not target.is_file() or any(p.is_symlink() for p in (target, *target.parents) if p != copy and copy in p.parents):
+        return None, "marker 대상 부재/symlink"
+    try:
+        original = target.read_bytes()
+        module = ast.parse(original.decode("utf-8"))
+    except (OSError, UnicodeError, SyntaxError) as exc:
+        return None, f"marker 기존 파일 파싱 불가: {exc}"
+    bindings, open_surface = _update_bindings(module)
+    if open_surface:
+        return None, "marker 동적/star/class global 표면"
+    pytest_aliases = {name for name, origins in bindings.items() if origins == {"import pytest"}}
+    mark_aliases = {name for name, origins in bindings.items() if origins == {"from pytest import mark"}}
+    if "pytest" in bindings and "pytest" not in pytest_aliases:
+        return None, "pytest 이름 재바인딩/충돌"
+    stores: list[ast.AST] = []
+    def visit(node: ast.AST) -> None:
+        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
+            if node.name == "pytestmark":
+                stores.append(node)
+            return
+        if isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Del)) and node.id == "pytestmark":
+            stores.append(node)
+        for child in ast.iter_child_nodes(node):
+            visit(child)
+    visit(module)
+    assignments = [node for node in module.body if
+        isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name)
+        and node.targets[0].id == "pytestmark" or isinstance(node, ast.AnnAssign)
+        and isinstance(node.target, ast.Name) and node.target.id == "pytestmark"]
+    if "pytestmark" in bindings and bindings["pytestmark"] != {""}:
+        return None, "module pytestmark import 바인딩 충돌"
+    if stores and (len(stores) != 1 or len(assignments) != 1):
+        return None, "module pytestmark 중복/동적/조건부 대입"
+    def simple(node: ast.AST | None) -> bool:
+        if isinstance(node, (ast.List, ast.Tuple)):
+            return all(simple(item) for item in node.elts)
+        if not isinstance(node, ast.Attribute):
+            return False
+        mark = node.value
+        return (isinstance(mark, ast.Attribute) and mark.attr == "mark" and isinstance(mark.value, ast.Name)
+                and mark.value.id in pytest_aliases or isinstance(mark, ast.Name) and mark.id in mark_aliases)
+    if assignments and not simple(assignments[0].value):
+        return None, "module pytestmark 호출/동적 표현 — 전사 미지원"
+    statement = "pytestmark = [" + ", ".join("pytest.mark." + name for name in entry.signals.markers) + "]"
+    import_needed = bool(entry.signals.markers) and "pytest" not in pytest_aliases
+    lines = original.splitlines(keepends=True)
+    def offset(line: int, column: int = 0) -> int:
+        return sum(len(part) for part in lines[:line - 1]) + column
+    changed = original
+    if assignments:
+        node = assignments[0]
+        start, end = offset(node.lineno, node.col_offset), offset(node.end_lineno, node.end_col_offset)
+        changed = original[:start] + statement.encode("utf-8") + original[end:]
+    # Insert imports/list after module docstring and future statements, preserving every other byte.
+    prefix_nodes = []
+    for index, node in enumerate(module.body):
+        if (index == 0 and isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant)
+                and isinstance(node.value.value, str)) or isinstance(node, ast.ImportFrom) and node.module == "__future__":
+            prefix_nodes.append(node)
+        else:
+            break
+    insert_at = offset(prefix_nodes[-1].end_lineno + 1) if prefix_nodes else 0
+    additions = (["import pytest"] if import_needed else []) + ([] if assignments else [statement])
+    if additions:
+        newline = b"\r\n" if b"\r\n" in original else b"\n"
+        addition = newline.join(x.encode() for x in additions) + newline
+        if insert_at and original[insert_at - 1:insert_at] != b"\n":
+            addition = newline + addition
+        changed = changed[:insert_at] + addition + changed[insert_at:]
+    try:
+        compile(changed, entry.path, "exec")
+    except (SyntaxError, ValueError) as exc:
+        return None, f"marker 합성 compile 실패: {exc}"
+    if changed == original:
+        return None, "module marker 후상태가 현재와 동일 — 실효 조치 없음"
+    return changed, "module marker 후상태만 전사; 함수/class decorator·본문 변경은 S5"
+
+
+class _DeclarationTypes:
+    """사본의 타입 표면에 명시 클래스 후상태만 겹치는 읽기 전용 그래프."""
+
+    def __init__(self, plan: Plan, copy: Path) -> None:
+        self.plan = plan
+        self.copy = copy
+        self.modules: dict[str, dict[str, list[object]]] = {}
+
+    @staticmethod
+    def module(path: str) -> str:
+        parts = list(PurePosixPath(path).with_suffix("").parts)
+        if parts[-1] == "__init__":
+            parts.pop()
+        return ".".join(parts)
+
+    def load(self, module: str) -> dict[str, list[object]]:
+        if module in self.modules:
+            return self.modules[module]
+        table: dict[str, list[object]] = {}
+        self.modules[module] = table
+        path = module.replace(".", "/") + ".py"
+        actual = self.copy / path
+        if not actual.is_file():
+            path = module.replace(".", "/") + "/__init__.py"
+            actual = self.copy / path
+        entries = [e for e in self.plan.entries.values() if self.module(e.path) == module]
+        if entries:
+            path = entries[0].path
+        def put(name: str, value: object) -> None:
+            values = table.setdefault(name, [])
+            # Repeated identical explicit imports are one provenance; duplicate declarations are ambiguous.
+            if isinstance(value, tuple) and value in values:
+                return
+            values.append(value)
+        def collect(node: ast.AST, conditional: bool = False) -> None:
+            if isinstance(node, ast.ImportFrom):
+                resolved = (_resolve_relative(PurePosixPath(path).parts, node.level, node.module)
+                            if node.level else tuple((node.module or "").split(".")))
+                origin = ".".join(resolved or ())
+                for alias in node.names:
+                    put(alias.asname or alias.name, None if conditional else (origin, alias.name))
+            elif isinstance(node, ast.Import):
+                for alias in node.names:
+                    put(alias.asname or alias.name.split(".")[0], None if conditional else
+                        (alias.name if alias.asname else alias.name.split(".")[0], ""))
+            elif isinstance(node, ast.ClassDef):
+                put(node.name, None if conditional else node)
+            elif isinstance(node, (ast.Assign, ast.AnnAssign)):
+                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
+                for target in targets:
+                    if isinstance(target, ast.Name):
+                        put(target.id, None if conditional else node.value)
+            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
+                put(node.name, None)
+            else:
+                for child in ast.iter_child_nodes(node):
+                    if isinstance(child, ast.stmt):
+                        collect(child, True)
+        if actual.is_file():
+            try:
+                for node in ast.parse(actual.read_text(encoding="utf-8")).body:
+                    collect(node)
+            except (OSError, UnicodeError, SyntaxError):
+                table["*"] = [None]
+        for entry in entries:
+            # Spec import rows can supplement current imports, but conflicting sources stay ambiguous.
+            for statement in entry.imports:
+                try:
+                    for node in ast.parse(statement).body:
+                        collect(node)
+                except SyntaxError:
+                    table["*"] = [None]
+            declared: dict[str, list[object]] = {}
+            for alias in entry.declaration_aliases:
+                first = ast.parse(alias.statement).body[0].value
+                other = ast.parse(alias.runtime).body[0].value if alias.type_checking else first
+                declared.setdefault(alias.name, []).append(first if ast.dump(first) == ast.dump(other) else None)
+            for symbol in entry.declarations:
+                if symbol.kind != "class":
+                    continue
+                try:
+                    body = [f"class {symbol.name}:"] + ["    " + f for f in symbol.fields]
+                    for method in symbol.methods:
+                        body += [f"    def {method.name}(self{', ' if method.params else ''}{method.params})"
+                                 f"{' -> ' + method.ret if method.ret else ''}: ..."]
+                    if len(body) == 1:
+                        body.append("    pass")
+                    node = ast.parse("\n".join(body)).body[0]
+                except (SyntaxError, ValueError):
+                    node = None
+                declared.setdefault(symbol.name, []).append(node)
+            table.update(declared)
+        return table
+
+    def resolve(self, module: str, expression: ast.expr, seen: frozenset[tuple[str, str]] = frozenset()
+                ) -> tuple[list[tuple[str, str, ast.ClassDef | None]], list[str]]:
+        """컨테이너·alias·forward 타입을 identity로 해소한다. 미해소는 후보 근거다."""
+        if isinstance(expression, ast.Constant):
+            if isinstance(expression.value, str):
+                try:
+                    return self.resolve(module, ast.parse(expression.value, mode="eval").body, seen)
+                except SyntaxError:
+                    return [], [f"forward annotation 파싱 불가: {expression.value}"]
+            return [], []
+        if isinstance(expression, (ast.Tuple, ast.List)):
+            nodes = expression.elts
+        elif isinstance(expression, ast.BinOp) and isinstance(expression.op, ast.BitOr):
+            nodes = [expression.left, expression.right]
+        elif isinstance(expression, ast.Subscript):
+            head = ast.unparse(expression.value)
+            identity, issues = self.resolve(module, expression.value, seen)
+            names = {(m, n) for m, n, _ in identity}
+            if ("typing", "Literal") in names:
+                return [], []
+            supported = {"list", "tuple", "set", "frozenset", "dict", "Mapping", "Sequence", "Optional", "Union"}
+            builtin_container = head in {"list", "tuple", "set", "frozenset", "dict"} and head not in self.load(module)
+            if builtin_container or any(m in ("typing", "collections.abc", "builtins") and n in supported for m, n in names):
+                return self.resolve(module, expression.slice, seen)
+            # Unknown generic semantics cannot prove contained field identity.
+            return [], issues or [f"타입 컨테이너 출처/필드 의미 미해소: {head}"]
+        else:
+            nodes = []
+        if nodes:
+            identities, issues = [], []
+            for node in nodes:
+                found, uncertain = self.resolve(module, node, seen)
+                identities.extend(found)
+                issues.extend(uncertain)
+            return identities, issues
+        if not isinstance(expression, (ast.Name, ast.Attribute)):
+            return [], [f"타입식 미지원: {ast.unparse(expression)}"]
+        name = ast.unparse(expression)
+        primitive = {"str", "int", "float", "bool", "bytes", "bytearray", "object", "None", "complex"}
+        if name in primitive:
+            return [], []
+        key = (module, name)
+        if key in seen:
+            return [], [f"alias cycle: {module}.{name}"]
+        seen = seen | {key}
+        if isinstance(expression, ast.Attribute):
+            pieces = name.split(".")
+            table = self.load(module)
+            root = table.get(pieces[0], [])
+            if len(root) == 1 and isinstance(root[0], tuple):
+                origin, symbol = root[0]
+                qualified = [origin] + ([symbol] if symbol else []) + pieces[1:]
+                target = ".".join(qualified[:-1])
+                return self.identity(target, pieces[-1], seen)
+            if root:
+                return [], [f"qualified 타입 출처 중복/미해소: {name}"]
+            if self._known_root(pieces[0]):
+                return self.identity(".".join(pieces[:-1]), pieces[-1], seen)
+            return [], [f"qualified 타입 출처 미해소: {name}"]
+        return self.identity(module, name, seen, local=True)
+
+    def _known_root(self, name: str) -> bool:
+        return name in ("typing", "builtins", "collections") or _is_repo_target(self.copy, name, self.plan)
+
+    def identity(self, module: str, name: str, seen: frozenset[tuple[str, str]], local: bool = False
+                 ) -> tuple[list[tuple[str, str, ast.ClassDef | None]], list[str]]:
+        values = self.load(module).get(name, [])
+        if len(values) > 1 or values == [None]:
+            return [], [f"타입 선언 중복/분기 불일치: {module}.{name}"]
+        if values:
+            value = values[0]
+            if isinstance(value, ast.ClassDef):
+                return [(module, name, value)], []
+            if isinstance(value, tuple):
+                origin, imported = value
+                if not imported:
+                    return [], [f"모듈 자체는 필드 타입 미확정: {module}.{name}"]
+                key = (origin, imported)
+                if key in seen:
+                    return [], [f"alias cycle: {origin}.{imported}"]
+                return self.identity(origin, imported, seen | {key})
+            if isinstance(value, ast.expr):
+                return self.resolve(module, value, seen)
+            return [], [f"타입 출처 미해소: {module}.{name}"]
+        if local:
+            return [], [f"bare 타입 `{name}` 출처 미해소 — 명시 import/별칭 출처를 보완해 주세요"]
+        # An explicit import/qualified module identity proves provenance; it does not prove existence.
+        return [(module, name, None)], []
+
+
+def check_declarations(plan: Plan, copy: Path) -> list[DeclarationFinding]:
+    """효과·DTO 명시 선언의 확정/후보 근거를 반환한다. 사본 파일을 변경하지 않는다."""
+    types = _DeclarationTypes(plan, copy)
+    findings: list[DeclarationFinding] = []
+
+    def add(rule: str, path: str, owner: str, detail: str, confirmed: bool) -> None:
+        finding = DeclarationFinding(rule, path, owner, detail, confirmed)
+        if finding not in findings:
+            findings.append(finding)
+
+    def annotations(cls: ast.ClassDef, constructor: bool = False) -> list[ast.expr]:
+        result = [n.annotation for n in cls.body if isinstance(n, ast.AnnAssign)]
+        if constructor:
+            for node in cls.body:
+                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "__init__":
+                    args = [*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs]
+                    args += [a for a in (node.args.vararg, node.args.kwarg) if a is not None]
+                    result += [a.annotation for a in args if a.annotation is not None]
+        return result
+
+    for effect in plan.effects:
+        if effect.effect == "read-only" and effect.uow != "none":
+            add("#197", effect.path, effect.owner, f"read-only + uow={effect.uow} 명시 모순", True)
+            continue
+        module = types.module(effect.path)
+        values = types.load(module).get(effect.owner, [])
+        injected, unknown = [], []
+        if len(values) == 1 and isinstance(values[0], ast.ClassDef):
+            for annotation in annotations(values[0], True):
+                identities, issues = types.resolve(module, annotation)
+                injected += [f"{m}.{n}" for m, n, _ in identities if ".application_layer.port.unit_of_work." in m + "."]
+                if "UnitOfWork" in ast.unparse(annotation):
+                    unknown += issues
+        else:
+            unknown.append("클래스 선언 중복/파싱 불가")
+        if effect.effect == "read-only":
+            if injected:
+                add("#197", effect.path, effect.owner, "read-only + uow=none에 명시 UoW port 주입: " + ", ".join(injected), True)
+            elif unknown:
+                add("#197", effect.path, effect.owner, "; ".join(unknown), False)
+        elif effect.uow == "none" and injected:
+            note = f"채널 불일치(비차단): {effect.path}::{effect.owner} write/uow=none + 주입 {', '.join(injected)}"
+            if note not in plan.notes:
+                plan.notes.append(note)
+
+    for entry in plan.entries.values():
+        if entry.tag not in ("add", "update"):
+            continue
+        if not ((entry.path.endswith("_result.py") and "/application_layer/" in entry.path)
+                or (entry.path.endswith("_response.py") and "/open_host_service/" in entry.path)):
+            continue
+        module = types.module(entry.path)
+        for owner, values in types.load(module).items():
+            if owner.startswith("_") or not owner.endswith(("Result", "Out", "Response")):
+                continue
+            if len(values) != 1 or not isinstance(values[0], ast.ClassDef):
+                if owner in entry.declared:
+                    add("#202", entry.path, owner, "DTO 선언 중복/미해소 — 출처 보완 필요", False)
+                continue
+            visited: set[tuple[str, str]] = set()
+            confirmed: list[str] = []
+            uncertain: list[str] = []
+            def walk(current: str, name: str, cls: ast.ClassDef) -> None:
+                key = (current, name)
+                if key in visited:
+                    return
+                visited.add(key)
+                for annotation in annotations(cls):
+                    identities, issues = types.resolve(current, annotation)
+                    uncertain.extend(issues)
+                    for origin, symbol, child in identities:
+                        segments = origin.split(".")
+                        domain = segments[segments.index("domain_layer") + 1:] if "domain_layer" in segments else []
+                        if domain and any(s in domain for s in ("value_object", "shared_value_object")):
+                            continue
+                        elif domain and ("entity" in domain or "aggregate" in domain
+                                         or len(domain) >= 2 and domain[0] == domain[1]):
+                            confirmed.append(f"{origin}.{symbol}")
+                        elif child is not None:
+                            walk(origin, symbol, child)
+                        elif _is_repo_target(copy, origin.split(".")[0], plan):
+                            uncertain.append(f"타입 `{origin}.{symbol}` 필드 선언/출처 보완 필요")
+            walk(module, owner, values[0])
+            if confirmed:
+                add("#202", entry.path, owner, "DTO 필드에서 domain aggregate/entity 도달: " + ", ".join(sorted(set(confirmed))), True)
+            if uncertain:
+                add("#202", entry.path, owner, "; ".join(sorted(set(uncertain))) + " — 출처 보완 검토 질문", False)
+    return findings
+
+
 def materialize(copy: Path, plan: Plan, *, realized: "frozenset[str]" = frozenset(),
                 base_short: str = "", promoted: "frozenset[str]" = frozenset()) -> "dict[str, list[str]]":
     """태그 의미론(D2)대로 사본 위에 팬텀을 겹친다 — add 실존 충돌은 FormError.
 
     `promoted` = `baseline_form_errors` 가 승격 형태 예외로 통과시킨 update 경로(미시뮬레이션 문면만 다르다).
 
     **재발화 판형(`--base` 명시 — Phase 2 진입 후 명세 개정 재실행)**: `realized` 는 `lift_realized_adds` 가
     앵커 커밋 전에 사본에서 걷어낸 «기실현 add» 경로다 — 여기서는 다른 add 와 똑같이 스텁으로 실체화하고
     (materialized 에 계수) already-built 에도 «기실현 — 스텁 대체 예보»로 기록한다(이중 기재는 의도 —
     `empty(기실현)` 은 materialized 에 안 실리는 것과 구별). 사본에 실존하는 add 는 기준선 트리 실존(계획↔실물
@@ -1345,20 +1787,26 @@
                 target.unlink()
                 report["materialized"].append(f"removed {entry.path}")
             else:
                 report["unsimulated"].append(f"remove(실존 없음): {entry.path}")
         elif entry.tag == "update":
             updated: "bytes | None"
             detail: str
             updated, detail = _render_service_update(copy, entry)
             if updated is not None:
                 target.write_bytes(updated)
+            marker_update, marker_detail = _render_marker_update(copy, entry)
+            if marker_update is not None:
+                updated = marker_update
+            detail += "; " + marker_detail
+            if updated is not None:
+                target.write_bytes(updated)
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
@@ -1860,42 +2308,62 @@
     "red 로 앞서 선다) / 행 자체가 없다 = 동적 import"
     "(`importlib` 리터럴).",
 )
 
 
 def _executor_stamp(blk_hash: str) -> str:
     """리포트 헤더 스탬프 — 버전 판별(행 수 휴리스틱 폐기)과 캐시 skip 대조(블록 해시)의 단일 자리."""
     return f"실행기: design_pregate.py · dddjango v{plugin_version()} · 블록 해시 {blk_hash}"
 
 
+def _declaration_lines(findings: list[DeclarationFinding] | tuple[DeclarationFinding, ...]) -> list[str]:
+    """확정 처분 ID와 후보 검토 ID는 같은 rule/path 단위를 유지하되 채널을 분리한다."""
+    lines: list[str] = []
+    for confirmed, title in ((True, "선언 확정"), (False, "선언 후보")):
+        grouped: dict[str, list[str]] = {}
+        for item in findings:
+            if item.confirmed != confirmed:
+                continue
+            line = f"[{item.rule}] {item.path}"
+            grouped.setdefault(line, []).append(f"{item.owner}: {item.detail}")
+        lines += ["", f"### {title} ({len(grouped)}건)", ""]
+        for line, details in grouped.items():
+            lines.append(f"- `{_stable_id(line)}` {line} — " + "; ".join(dict.fromkeys(details)))
+        if not grouped:
+            lines.append("- (없음)")
+    return lines
+
+
 def write_report(report_path: Path, spec: Path, base_ref: str, base_sha: str, verdict: str,
                  attributed: "list[str]", mat: "dict[str, list[str]]",
-                 notes: "list[str]", blk_hash: str, existence: ExistenceReport) -> None:
+                 notes: "list[str]", blk_hash: str, existence: ExistenceReport,
+                 declarations: list[DeclarationFinding] | tuple[DeclarationFinding, ...] = ()) -> None:
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
         f"- 판정: {verdict}",
         "",
         f"### 예보 항목 ({len(attributed)}건 · 안정 ID = sha256(규칙#+경로)[:12])",
         "",
     ]
     if attributed:
         lines.extend(f"- `{_stable_id(line)}` {line}" for line in attributed)
     else:
         lines.append("- (없음) — green 은 «설계 검증됨»이 아니라 «P/S/I급 위반 예보 0»이다.")
+    lines.extend(_declaration_lines(declarations))
     lines.extend(_existence_lines(existence))
     lines += ["", f"### already-built ({len(mat.get('already_built', []))}건) · "
                   f"미시뮬레이션 ({len(mat.get('unsimulated', []))}건)", ""]
     for item in mat.get("already_built", []):
         lines.append(f"- already-built: {item}")
     for item in mat.get("unsimulated", []):
         lines.append(f"- 미시뮬레이션: {item}")
     for item in mat.get("pruned_dirs", []):
         lines.append(f"- remove 빈 부모 정리: {item}")
     for note in notes:
@@ -1906,37 +2374,39 @@
     lines.extend(f"- {spot}" for spot in BLIND_SPOTS)
     lines.append("")
     report_path.parent.mkdir(parents=True, exist_ok=True)
     with report_path.open("a", encoding="utf-8") as fp:
         fp.write("\n".join(lines))
     print(f"\n예보 리포트 append → {report_path}")
 
 
 def write_report_stub(report_path: "Path | None", spec: Path, base_ref: str, base_sha: str,
                       verdict: str, detail: "list[str]", blk_hash: str,
-                      existence: "ExistenceReport | None" = None) -> None:
+                      existence: "ExistenceReport | None" = None,
+                      declarations: list[DeclarationFinding] | tuple[DeclarationFinding, ...] = ()) -> None:
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
         f"- 판정: {verdict}",
         "",
     ]
     lines.extend(f"- {item}" for item in detail)
+    lines.extend(_declaration_lines(declarations))
     if existence is not None:
         lines.extend(_existence_lines(existence))
     lines.append("")
     report_path.parent.mkdir(parents=True, exist_ok=True)
     with report_path.open("a", encoding="utf-8") as fp:
         fp.write("\n".join(lines))
 
 
 # ── 차단 모드 — 계획↔기준선 모순(형식 red) · 리포트 최신성 대조(--check-report) ──────────────────
 
@@ -2053,45 +2523,49 @@
     problems: "list[str]" = []
     report_hash: str = hash_m.group(1) if hash_m else "-"
     if hash_m is None:
         problems.append("최신성 증명 불가 — 마지막 헤더에 블록 해시 토큰이 없다(구판 리포트) · 재발화")
     elif report_hash != spec_hash:
         problems.append(f"stale — 명세 블록 해시 {spec_hash} ≠ 마지막 예보 {report_hash} · 재발화")
     count_m: "re.Match[str] | None" = _REPORT_COUNT_RE.search(verdict)
     defect_m: "re.Match[str] | None" = _REPORT_DEFECT_RE.search(verdict)
     attributed: int = int(count_m.group(1)) if count_m else 0
     defects: int = int(defect_m.group(1)) if defect_m else 0
+    declarations: int = len(set(_REPORT_ID_RE.findall(_subsection(section, "선언 확정"))))
+    candidates: int = len(set(_REPORT_ID_RE.findall(_subsection(section, "선언 후보"))))
     short: str
     if verdict.startswith("형식 red"):
         problems.append(f"형식 red 미해소 — 마지막 판정 «{verdict}» · architect 반송")
         short = "형식 red"
     elif verdict.startswith("예보 red"):
-        ids: "list[str]" = _REPORT_ID_RE.findall(_subsection(section, "예보 항목"))
+        ids: "list[str]" = list(dict.fromkeys(_REPORT_ID_RE.findall(_subsection(section, "예보 항목"))
+                    + _REPORT_ID_RE.findall(_subsection(section, "선언 확정"))))
         missing: "list[str]" = [i for i in ids if not _disposed(section, i)]
         if missing:
             problems.append(f"처분 미기재 {len(missing)}건(ignored|filtered 행 없음 — corrected 는 재실행이 최종본): "
                             + " ".join(f"`{i}`" for i in missing))
         short = f"red {attributed}({'처분 전건' if not missing else f'미기재 {len(missing)}'}) · 실존 결손 {defects}"
     elif verdict.startswith("예보 green"):
         short = "green" + (f" · 실존 결손 {defects}" if defects else "")
     elif verdict.startswith("skip"):
         short = "skip" + (f" · 실존 결손 {defects}" if defects else "")
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
+        "declarations": str(declarations), "candidates": str(candidates),
         "base": base_m.group(1)[:12] if base_m else "-",
     }
     return (3 if problems else 0), problems, info
 
 
 def run_check_report(spec_text: str, report_path: Path, blk_hash: str) -> int:
     """`--check-report` 진입 — 배너(G1/G1′)·G2 근거 대조의 유일한 기계 출처(`요약:` 행)."""
     print(f"# design_pregate --check-report · 모드 차단({MODE}) · {_executor_stamp(blk_hash)}")
     if not report_path.is_file():
         print(f"실행 불능: 리포트 부재 — {report_path} (pre-gate 가 이 레인에서 한 번도 실행되지 않았다 · 구형 명세·"
@@ -2102,21 +2576,22 @@
     code: int = result[0]
     problems: "list[str]" = result[1]
     info: "dict[str, str]" = result[2]
     if code == 1:
         print(f"실행 불능: {problems[0]}", file=sys.stderr)
         return 1
     for p in problems:
         print(f"  불비: {p}")
     status: str = "정합" if code == 0 else f"불비 {len(problems)}건"
     print(f"\n요약: check-report {status} · 블록 해시 {info['spec_hash']}={info['report_hash']} · "
-          f"마지막 판정 {info['short']} · 귀속 {info['attributed']}건 · 실존 결손 {info['defects']}건 · "
+          f"마지막 판정 {info['short']} · 귀속 {info['attributed']}건 · 선언 확정 {info['declarations']}건 · "
+          f"선언 후보 {info['candidates']}건 · 실존 결손 {info['defects']}건 · "
           f"기준선 {info['base']}")
     return code
 
 
 # ── main ────────────────────────────────────────────────────────────────────
 
 def main(argv: "list[str]") -> int:
     ap: _UsageParser = _UsageParser(add_help=True, description="design-spec pre-gate 예보 실행기")
     ap.add_argument("spec", help="설계 명세 markdown(기계 블록 §4 포함)")
     ap.add_argument("target", help="대상 저장소 루트(git)")
@@ -2233,70 +2708,78 @@
         try:
             mat: "dict[str, list[str]]" = materialize(copy, plan, realized=realized, base_short=base_sha[:12],
                                                       promoted=promoted)
         except FormError as exc:
             print(f"형식 red — {exc}")
             write_report_stub(report_path, spec_path, base_ref, base_sha, "형식 red", [str(exc)], blk_hash)
             print(f"\n요약: 형식 red 1건({_error_kinds([str(exc)])}) · 기준선 {base_sha[:12]} · 모드 차단")
             return 3
 
         # 계약 실존 — materialize(+골격·`__init__` 체인) 뒤 · 실체화-0 분기 앞(update 소비자만의 명세도 판정한다).
+        declarations = check_declarations(plan, copy)
+        declaration_count = len({(item.rule, item.path) for item in declarations if item.confirmed})
+        for line in _declaration_lines(declarations):
+            print(line)
         existence: ExistenceReport = check_import_existence(copy, plan)
         own_note: "str | None" = _own_interpreter_note(repo)
         if own_note is not None:
             existence.undecidable_notes.append(own_note)
         defects: int = len(existence.defects)
         cleanup_notes: "list[str]" = [f"remove 빈 부모 정리: {p}" for p in mat["pruned_dirs"]]
         for note in cleanup_notes:
             print(note)
 
         if not mat["materialized"]:
             reason = ("skip — 실체화 0건(add/empty/remove 및 제한 update 실효 조치 없음): "
                       "게이트를 부르지 않는다(공허 차분 가드 · 사유 명시)")
-            verdict_stub: str = "skip" + (f" · 계약 실존 결손 {defects}건(권고·비차단)" if defects else "")
+            verdict_stub: str = (f"예보 red — 선언 확정 {declaration_count}건" if declaration_count else "skip") + (f" · 계약 실존 결손 {defects}건(권고·비차단)" if defects else "")
             print(reason)
+            for note in plan.notes:
+                print(f"  채널 메모: {note}")
             for item in mat["unsimulated"]:
                 print(f"  미시뮬레이션: {item}")
             _print_existence(existence)
-            print(f"\n요약: 실체화 0 · 실존 결손 {defects}건 · 기준선 {base_sha[:12]} · 모드 차단")
+            print(f"\n요약: 실체화 0 · 실존 결손 {defects}건 · 선언 확정 {declaration_count}건 · 기준선 {base_sha[:12]} · 모드 차단")
             write_report_stub(report_path, spec_path, base_ref, base_sha, verdict_stub,
-                              [reason] + [f"미시뮬레이션: {x}" for x in mat["unsimulated"]] + cleanup_notes, blk_hash,
-                              existence=existence)
-            return 5 if defects else 4
+                              [reason] + [f"미시뮬레이션: {x}" for x in mat["unsimulated"]] + cleanup_notes
+                              + [f"채널 메모: {n}" for n in plan.notes], blk_hash,
+                              existence=existence, declarations=declarations)
+            return 2 if declaration_count else (5 if defects else 4)
 
         print(f"# design_pregate — 예보 실행 · 기준선 {base_sha[:12]} (--base {base_ref}) · "
               f"모드 차단({MODE}) · {_executor_stamp(blk_hash)}")
         print(f"({NO_SUBSTITUTE})")
         print(f"실체화 {len(mat['materialized'])}건 · dirty overlay {len(overlaid)}건 · "
               f"미시뮬레이션 {len(mat['unsimulated'])}건 · already-built {len(mat['already_built'])}건")
 
         gate_result: "tuple[int, list[str], str]" = run_gate(copy, scratch, ns.python_bin)
         gate_exit: int = gate_result[0]
         attributed: "list[str]" = gate_result[1]
         print("\n" + gate_result[2].rstrip())
 
         verdict: str = ("예보 green — P/S/I급 결정 계약 위반 예보 0(«설계 검증됨» 아님)"
-                        if gate_exit == 0 else
+                        if gate_exit == 0 and not declaration_count else
                         f"예보 red — P/S/I급 결정 계약 위반 예보 {len(attributed)}건")
+        verdict += f" · 선언 확정 {declaration_count}건"
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
-                         attributed, mat, plan.notes, blk_hash, existence)
-        if gate_exit != 0:
+                         attributed, mat, plan.notes, blk_hash, existence, declarations)
+        if gate_exit != 0 or declaration_count:
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
--- a/codex-dddjango/skills/dddjango/scripts/design_pregate.py
+++ b/codex-dddjango/skills/dddjango/scripts/design_pregate.py
@@ -60,23 +60,27 @@
                    1행 = `<소비 파일 경로><탭|2+공백><import 문 그대로>`.
                    행 전부가 «계약 실존» 3단 판정을 받는다 — 소비 파일의 태그·등재 여부와
                    무관(update 소비자 포함 · update 전사는 실존 OHS 서비스의 새 함수 추가 때만 충돌 검사 후).
                    판정 기준은 **이 브랜치**의 격리 사본(기준선 + dirty overlay + 명시 전사)이다: 저장소 밖(표준·서드파티)은
                    검사 밖 · 이 명세가 add 하는 대상은 자기 해소(⑶ 생략 — symbols 채널 소관 · 승격
                    폴더 부품 포함) · file-plan `update` 대상의 이름은 그 칸의 symbols 선언이면 자기
                    update 해소(S′)·현재 표면에 있으면 실존 확인·둘 다 아니면 판정 불능(표면은 이
                    명세 이후 상태 — ⑵⑶ 비적용) · ⑵ 는 이름 import(`from M import n`)의 대상 M 이 모듈
                    실현일 때만(모듈 import·패키지 `__init__` 은 ImportError 가 아니다). 세미콜론 복합행은
                    문 전부 판정. 결손은 권고·비차단.
+  use-case-effects 선택형 `<!-- machine: use-case-effects -->` + ```effects 펜스.
+                   `<파일>::<클래스>  <read-only|write>  uow=<none|타입식>`.
+                   add/update 클래스의 효과·DTO 선언은 소스 차분과 독립적으로 검증한다.
   physical-signals 영구 테스트 입장 표(6열 정본 header)의 owner/path 셀 첫 Python artifact에 정형
                    어노테이션 `[markers: a,b] [base: X] [client: yes]` — 무기재 = 부재.
-                   code span/bare token의 `.py::case`는 파일 부분만 결합한다. 뒤 support/coverage
+                   add의 code span/bare token `.py::case`는 파일 부분만 결합한다.
+                   update의 [markers:]는 module pytestmark 최종 목록이다(무기재 유지·nodeid는 S5). 뒤 support/coverage
                    주소는 대상이 아니며 첫 주소가 미등재여도 뒤 등재 파일로 건너뛰지 않는다.
   exception-map    `<!-- machine: exception-map -->` + ```exceptions 펜스.
                    1행 = `<예외 이름><탭|2+공백><raise 창구 파일 경로>` — 창구 스텁에
                    `raise <예외>()` 파일 수준 helper 합성(#456 — 번역표에 없는 예외 = 죽은 계약 = 진탐 보존).
                    update는 새 함수가 실제 전사되는 OHS 서비스만 해당하며 함수별 raise 위치는 추론하지 않는다.
 
 무엇이 아닌가: 예보는 Phase 2 step 6(G2 registry 게이트)의 실행·증거 요구를 어떤
 형태로도 대체·축약하지 않는다(D4 대체 금지). green 은 «설계 검증됨»이 아니라
 «P/S/I급 결정 계약 위반 예보 0»이다. 예보 기준선은 «스텁 제외 현재 상태»이며
 `build_anchor` 를 읽지도 쓰지도 않는다(앵커 의미론).
@@ -142,20 +146,21 @@
 # 계획 경로 선검증(D3) — `_IGNORE_COPY` 조용 소실 방지 + 숨김 세그먼트 전면 거절.
 FORBIDDEN_SEGMENTS: "frozenset[str]" = frozenset({
     "build", "dist", "staticfiles", "node_modules", "site-packages", "venv", ".dddjango",
 })
 # 기계 블록 마커 → 펜스 언어(§4). 이 어휘 밖의 machine 마커는 형식 red(fail-closed).
 MACHINE_FENCES: "dict[str, str]" = {
     "file-plan": "paths",
     "symbols": "symbols",
     "boundary-imports": "imports",
     "exception-map": "exceptions",
+    "use-case-effects": "effects",
 }
 # 영구 테스트 입장 표 정본 header 6열(조임 a — 영문 고정·셀 내 raw `|` 금지).
 SIGNALS_HEADER: "tuple[str, ...]" = (
     "candidate", "protected contract/evidence", "unique production failure",
     "existing authoritative coverage", "decision", "owner/path",
 )
 # 베이스 토큰 → import 문 합성(D2 ②상수-배선형 — 정보-무함유 규약 상수만).
 BASE_IMPORTS: "dict[str, str]" = {
     "ABC": "from abc import ABC, abstractmethod",
     "TestCase": "from django.test import TestCase",
@@ -233,50 +238,71 @@
     type_checking: bool = False
     runtime: str = ""
 
 
 @dataclass
 class Signals:
     """[신규 4] 물리 신호 어노테이션 — 무기재 = «물리 신호 없음»(fail-closed)."""
     markers: "list[str]" = field(default_factory=list)
     base: str = ""
     client: bool = False
+    markers_explicit: bool = False
 
 
 @dataclass
 class PlanEntry:
     """[신규 1] 파일 계획 1행 + 타 채널에서 결합된 실체화 재료."""
     path: str
     tag: str                     # add | update | remove | empty
     deferred_remove: bool = False  # `remove@Ln` — G1 승인 시점 상태 유지(후행 제거 격리)
     symbols: "list[Symbol]" = field(default_factory=list)
     imports: "list[str]" = field(default_factory=list)
     raises: "list[str]" = field(default_factory=list)
     signals: "Signals | None" = None
     # symbols 채널이 이 경로에 선언한 최상위 이름(클래스·함수·메서드 행의 owner) — 태그 무관 기록. `update` 칸은
     # 새 OHS 모듈 함수의 제한 전사와 별개로 계약 실존의 «자기 update 해소»(S′) 근거가 된다.
     declared: "list[str]" = field(default_factory=list)
     aliases: "list[ModuleAlias]" = field(default_factory=list)
+    declarations: list[Symbol] = field(default_factory=list)
+    declaration_aliases: list[ModuleAlias] = field(default_factory=list)
 
 
 @dataclass
 class ImportRow:
     """boundary-imports 1행 원문 — 소비 파일의 태그·등재 여부와 무관하게 보존한다(계약 실존 판정의 입력)."""
     consumer: str
     stmt: str
 
 
 @dataclass
+class UseCaseEffect:
+    path: str
+    owner: str
+    effect: str
+    uow: str
+
+
+@dataclass
+class DeclarationFinding:
+    rule: str
+    path: str
+    owner: str
+    detail: str
+    confirmed: bool
+
+
+@dataclass
 class Plan:
     """명세 1부의 전사 결과 — 실체화 입력의 전부(산문 추론 재료 0)."""
     entries: "dict[str, PlanEntry]" = field(default_factory=dict)
     notes: "list[str]" = field(default_factory=list)  # 고아 채널 행·미반영 결합(침묵 금지)
+    effects: list[UseCaseEffect] = field(default_factory=list)
     import_rows: "list[ImportRow]" = field(default_factory=list)  # 계약 실존 판정 입력(전 행 — 스텁 전사와 별개)
 
 
 @dataclass
 class ExistenceDefect:
     """계약 실존 결손 1항목 — 정체성은 (모듈, 이름)이고 단계(⑴⑵⑶)는 현재 상태다(소비자는 합친다)."""
     stage: str    # ⑴ | ⑵ | ⑶
     module: str   # 절대 점 경로(상대 import 는 소비 파일 기준 해소)
     name: str     # import 한 이름 — 모듈 import 는 ""
     detail: str   # 문면: 모듈 부재 · 자리표시자(형태 — 출처) · 심볼 미정의 `n`
@@ -515,21 +541,21 @@
     if not isinstance(target, ast.Name) or not isinstance(value, (ast.Name, ast.Attribute, ast.Subscript)):
         return None
     allowed: tuple = (ast.Name, ast.Attribute, ast.Subscript, ast.Load, ast.Tuple, ast.List,
                       ast.Constant, ast.BinOp, ast.BitOr)
     if any(not isinstance(node, allowed) for node in ast.walk(value)):
         return None
     return target.id
 
 
 def _parse_symbols(rows: "list[str]", plan: Plan, errors: "list[str]") -> None:
-    """symbols 전사. update는 모듈 함수 후보만 보존하고 모든 선언 이름은 종전대로 S′에 쓴다."""
+    """add/update 명시 선언은 검증용으로 보존하며 update 렌더 재료는 모듈 함수만 싣는다."""
     classes: "dict[tuple[str, str], Symbol]" = {}
     seen_symbols: "set[str]" = set()
     alias_names: "dict[str, set[str]]" = {}
     pending: "tuple[str, ModuleAlias] | None" = None
     for raw in rows:
         line: str = raw.strip()
         if not line or line.startswith("#"):
             continue
         m: "re.Match[str] | None" = _SYM_LINE_RE.match(line)
         if m is None:
@@ -563,20 +589,22 @@
                 pending = None
             else:
                 alias = ModuleAlias(name, statement, type_checking=branch == "TYPE_CHECKING")
                 if alias.type_checking:
                     pending = (path, alias)
                     continue
             alias_names.setdefault(path, set()).add(name)
             if entry is not None:
                 if name not in entry.declared:
                     entry.declared.append(name)
+                if entry.tag in ("add", "update"):
+                    entry.declaration_aliases.append(alias)
                 if entry.tag == "add":
                     entry.aliases.append(alias)
         elif decorator:
             owner: "Symbol | None" = classes.get((path, decorator.group(1)))
             expression: str = decorator.group(2)
             if owner is None or not _decorator_expr(expression):
                 errors.append(f"symbols decorator는 선행 클래스와 이름/호출 식이 필요하다: {path}::{rest}")
                 continue
             owner.decorators.append(expression)
         else:
@@ -585,32 +613,32 @@
                 continue
             declared_name: str = parsed.name.split(".", 1)[0]
             if declared_name in alias_names.get(path, set()):
                 errors.append(f"symbols alias와 심볼 이름 중복: {path}::{declared_name}")
                 continue
             seen_symbols.add(path)
             if entry is not None and declared_name not in entry.declared:
                 entry.declared.append(declared_name)
             if isinstance(parsed, Symbol) and parsed.kind == "class":
                 classes[(path, parsed.name)] = parsed
-            if entry is not None and entry.tag == "add":
-                if isinstance(parsed, Method):
-                    owner = classes.get((path, declared_name))
-                    if owner is None:
-                        errors.append(f"symbols 메서드 행의 선행 클래스 부재: {path}::{parsed.name}")
-                        continue
-                    owner.methods.append(Method(name=parsed.name.split(".", 1)[1],
-                                                params=parsed.params, ret=parsed.ret))
-                else:
+            if isinstance(parsed, Method):
+                owner = classes.get((path, declared_name))
+                if owner is None:
+                    errors.append(f"symbols 메서드 행의 선행 클래스 부재: {path}::{parsed.name}")
+                    continue
+                owner.methods.append(Method(name=parsed.name.split(".", 1)[1],
+                                            params=parsed.params, ret=parsed.ret))
+            elif entry is not None and entry.tag in ("add", "update"):
+                entry.declarations.append(parsed)
+                if entry.tag == "add" or parsed.kind == "function":
                     entry.symbols.append(parsed)
-            elif entry is not None and entry.tag == "update" and isinstance(parsed, Symbol) and parsed.kind == "function":
-                entry.symbols.append(parsed)
+
         if entry is None:
             plan.notes.append(f"symbols 고아 행(file-plan 미등재 — 미반영): {path}::{rest}")
             continue
         if entry.tag != "add":
             plan.notes.append(f"symbols 비-add `{entry.tag}` 칸 — update의 새 OHS 모듈 함수만 실물 대조 후 제한 전사; "
                               f"그 밖은 S5 · 선언 이름의 계약 실존 «자기 update 해소»는 별도: {path}")
     if pending:
         errors.append(f"symbols alias TYPE_CHECKING의 인접 else 부재: {pending[0]}::{pending[1].name}")
 
 
@@ -683,21 +711,21 @@
             if i < len(lines) and re.fullmatch(r"[|\s:-]+", lines[i].strip() or "x"):
                 i += 1  # 구분선
             while i < len(lines) and lines[i].strip().startswith("|"):
                 rows.append(lines[i])
                 i += 1
             continue
         i += 1
     return rows
 
 
-def _parse_signals(text: str, plan: Plan) -> None:
+def _parse_signals(text: str, plan: Plan, errors: list[str]) -> None:
     """영구 테스트 입장 표(정본 6열 header)의 owner/path 셀에서 [신규 4] 어노테이션 전사.
 
     code span/bare token에 나온 첫 Python 파일 주소가 owner artifact다. nodeid의 `.py::case`는
     파일 부분만 결합하며 뒤 support/coverage 주소로 신호를 전파하지 않는다(첫 주소 미등재도 동일).
     어노테이션이 하나도 없는 행은 «물리 신호 없음»과 같으므로 결합하지 않는다(fail-closed).
     """
     for raw in _signals_rows(text):
         cells: "list[str]" = _cells(raw)
         if len(cells) != len(SIGNALS_HEADER):
             plan.notes.append(f"입장 표 행 열 수 불일치(무시): {cells[:1]}")
@@ -708,47 +736,103 @@
         client_m: "re.Match[str] | None" = _ANN_CLIENT_RE.search(cell)
         if markers_m is None and base_m is None and client_m is None:
             continue  # 무기재 = 물리 신호 없음
         artifact: "re.Match[str] | None" = re.search(
             r"(?<![\w./-])([\w./-]+\.py)(?=::|[\s`\],;)]|$)", cell)
         path: "str | None" = artifact.group(1) if artifact else None
         if path is None:
             plan.notes.append(f"physical-signals 경로 해소 불가(owner/path 셀): {cell!r}")
             continue
         entry: "PlanEntry | None" = plan.entries.get(path)
-        if entry is None or entry.tag != "add":
-            plan.notes.append(f"physical-signals 미반영(미등재 또는 비-add): {path}")
+        if entry is None or entry.tag not in ("add", "update"):
+            plan.notes.append(f"physical-signals 미반영(미등재 또는 비-add/update): {path}")
+            continue
+        if entry.tag == "update" and cell[artifact.end():].startswith("::"):
+            plan.notes.append(f"S5 physical-signals nodeid/class는 module marker로 승격하지 않는다: {path}")
             continue
         sig: Signals = Signals()
         if markers_m is not None:
+            sig.markers_explicit = True
             sig.markers = [t.strip() for t in markers_m.group(1).split(",") if t.strip()]
+            if any(not re.fullmatch(r"[A-Za-z_]\w*", token) for token in sig.markers):
+                plan.notes.append(f"S5 physical-signals markers는 단순 identifier만 지원: {path}")
+                continue
+            if entry.signals and entry.signals.markers_explicit and entry.signals.markers != sig.markers:
+                errors.append(f"physical-signals 최종 module markers 상충: {path}")
+                continue
         if base_m is not None:
             sig.base = base_m.group(1).strip()
         sig.client = client_m is not None and client_m.group(1) == "yes"
+        if entry.tag == "update" and (base_m is not None or client_m is not None):
+            plan.notes.append(f"S5 physical-signals update base/client 미지원: {path}")
+        if entry.signals and not sig.markers_explicit:
+            sig.markers = entry.signals.markers
+            sig.markers_explicit = entry.signals.markers_explicit
         entry.signals = sig
+
+
+def _parse_effects(rows: list[str] | None, plan: Plan, errors: list[str]) -> None:
+    """선택형 효과 채널은 명시한 클래스에만 결합한다."""
+    if rows is None:
+        plan.notes.append("S5 use-case-effects 무기재 — 읽기/쓰기 효과 미검증")
+        return
+    seen: set[tuple[str, str]] = set()
+    for raw in rows:
+        if not raw.strip() or raw.lstrip().startswith("#"):
+            continue
+        match = re.fullmatch(r"(\S+)::([A-Za-z_]\w*)\s+(read-only|write)\s+uow=(.+)", raw.strip())
+        if not match:
+            errors.append(f"use-case-effects 행 파싱 불가: {raw}")
+            continue
+        path, owner, effect, uow = match.groups()
+        entry = plan.entries.get(path)
+        if (entry is None or entry.tag not in ("add", "update")
+                or not any(s.name == owner and s.kind == "class" for s in entry.declarations)):
+            errors.append(f"use-case-effects add/update 선행 클래스 부재: {path}::{owner}")
+            continue
+        if (path, owner) in seen:
+            errors.append(f"use-case-effects 중복/상충: {path}::{owner}")
+            continue
+        seen.add((path, owner))
+        uow = uow.strip()
+        try:
+            if uow != "none":
+                ast.parse(f"value: {uow}")
+                annotation = ast.parse(uow, mode="eval").body
+                if any(isinstance(n, (ast.Call, ast.NamedExpr, ast.Lambda)) for n in ast.walk(annotation)):
+                    raise ValueError("타입 표현식 밖")
+        except (SyntaxError, ValueError):
+            errors.append(f"use-case-effects uow 타입식 파싱 불가: {raw}")
+            continue
+        plan.effects.append(UseCaseEffect(path, owner, effect, uow))
 
 
 def block_hash(text: str) -> str:
     """기계가독 블록 해시 — 기계 블록 4종 + 영구 테스트 입장 표를 **파서와 같은 정규식·스캔**으로
     추출해 문서 순서 원문(verbatim)으로 이어 붙인 sha256[:12]. 출력 전용(판정 무접촉·git 0회·OS 무관).
 
     Coordinator 의 캐시 skip 판형(pre-gate 문단): `--block-hash` 값이 직전 실행 리포트 헤더의
     `블록 해시` 와 같을 때만 재실행을 skip 할 수 있다 — 같은 입력이면 같은 값, 산문만 바뀌면 같은 값,
     블록 한 글자가 바뀌면 다른 값이다(원문 기준이라 공백 변경도 재실행 쪽으로 기운다 — 안전 방향).
     """
     blocks: "dict[str, list[str]]" = _machine_blocks(text, [])
     parts: "list[str]" = []
     for name in MACHINE_FENCES:
+        if name == "use-case-effects":
+            continue
         parts.append(f"<!-- machine: {name} -->")
         parts.extend(blocks.get(name, []))
     parts.append("<!-- physical-signals -->")
     parts.extend(_signals_rows(text))
+    if "use-case-effects" in blocks:
+        parts.append("<!-- machine: use-case-effects -->")
+        parts.extend(blocks["use-case-effects"])
     return hashlib.sha256("\n".join(parts).encode("utf-8")).hexdigest()[:12]
 
 
 def plugin_version() -> str:
     """플러그인 버전 probe — 설치 레이아웃 2경로(Claude `<plugin>/.claude-plugin/plugin.json` ·
     Codex `<plugin>/skills/dddjango/scripts` 기준 `parents[2]/.codex-plugin/plugin.json`).
     실패는 `(unknown)` — 판정 영향 0(리포트 헤더 스탬프 전용). registry_gate.py 도 같은 probe 를
     각자 보유한다(두 스크립트는 독립 파일 — 러너 유닛이 동치를 가드한다)."""
     candidates: "list[Path]" = [SCRIPTS_DIR.parent / ".claude-plugin" / "plugin.json"]
     if len(SCRIPTS_DIR.parents) > 2:
@@ -767,21 +851,22 @@
     """명세 전문 → (Plan, 형식 오류 목록). file-plan 블록 부재면 (None, []) — skip 재료."""
     errors: "list[str]" = []
     blocks: "dict[str, list[str]]" = _machine_blocks(text, errors)
     if "file-plan" not in blocks and not errors:
         return None, []
     plan: Plan = Plan()
     plan.entries = _parse_file_plan(blocks.get("file-plan", []), errors)
     _parse_symbols(blocks.get("symbols", []), plan, errors)
     _parse_imports(blocks.get("boundary-imports", []), plan, errors)
     _parse_exception_map(blocks.get("exception-map", []), plan, errors)
-    _parse_signals(text, plan)
+    _parse_signals(text, plan, errors)
+    _parse_effects(blocks.get("use-case-effects"), plan, errors)
     # apps.py 정형(② 화이트리스트): django_* apps.py 심볼의 무기재 베이스는 AppConfig 규약 상수이고,
     # 결손 필드(name/label)는 정형 값으로 보충한다 — 전사된 필드는 유지(전사 우선·일탈은 예보에 실린다).
     for entry in plan.entries.values():
         if entry.path.endswith("/apps.py") and "django_" in entry.path:
             parent: PurePosixPath = PurePosixPath(entry.path).parent
             parts: "tuple[str, ...]" = parent.parts
             bc: str = parts[1] if len(parts) >= 2 and parts[0] == "application" else ""
             dotted: str = ".".join(parts)
             for sym in entry.symbols:
                 if sym.kind != "class":
@@ -1283,20 +1368,377 @@
             if any(isinstance(part, ast.NamedExpr) for expr in signature for part in ast.walk(expr)):
                 return None, "새 함수 signature의 NamedExpr는 모듈 바인딩을 바꿀 수 있어 전사하지 않는다"
         addition: str = "\n\n".join(ast.get_source_segment(stub, node) or "" for node in stub_module.body[2:])
         combined: bytes = original + ("\n\n" + addition + "\n").encode("utf-8")
         compile(combined, entry.path, "exec")  # 합성 전체의 symtable까지 검증(중복 인자 포함)
     except (SyntaxError, ValueError) as exc:
         return None, f"합성 compile 실패: {getattr(exc, 'msg', None) or str(exc)}"
     return combined, "새 모듈 함수만 전사; 기존 signature/body·decorator/alias/class update는 미시뮬레이션"
 
 
+def _render_marker_update(copy: Path, entry: PlanEntry) -> tuple[bytes | None, str]:
+    """단일 정적 module pytestmark statement만 byte 범위 치환한다."""
+    if entry.signals is None or not entry.signals.markers_explicit:
+        return None, "marker 후상태 무기재 — 유지"
+    target = copy / entry.path
+    if not target.is_file() or any(p.is_symlink() for p in (target, *target.parents) if p != copy and copy in p.parents):
+        return None, "marker 대상 부재/symlink"
+    try:
+        original = target.read_bytes()
+        module = ast.parse(original.decode("utf-8"))
+    except (OSError, UnicodeError, SyntaxError) as exc:
+        return None, f"marker 기존 파일 파싱 불가: {exc}"
+    bindings, open_surface = _update_bindings(module)
+    if open_surface:
+        return None, "marker 동적/star/class global 표면"
+    pytest_aliases = {name for name, origins in bindings.items() if origins == {"import pytest"}}
+    mark_aliases = {name for name, origins in bindings.items() if origins == {"from pytest import mark"}}
+    if "pytest" in bindings and "pytest" not in pytest_aliases:
+        return None, "pytest 이름 재바인딩/충돌"
+    stores: list[ast.AST] = []
+    def visit(node: ast.AST) -> None:
+        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
+            if node.name == "pytestmark":
+                stores.append(node)
+            return
+        if isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Del)) and node.id == "pytestmark":
+            stores.append(node)
+        for child in ast.iter_child_nodes(node):
+            visit(child)
+    visit(module)
+    assignments = [node for node in module.body if
+        isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name)
+        and node.targets[0].id == "pytestmark" or isinstance(node, ast.AnnAssign)
+        and isinstance(node.target, ast.Name) and node.target.id == "pytestmark"]
+    if "pytestmark" in bindings and bindings["pytestmark"] != {""}:
+        return None, "module pytestmark import 바인딩 충돌"
+    if stores and (len(stores) != 1 or len(assignments) != 1):
+        return None, "module pytestmark 중복/동적/조건부 대입"
+    def simple(node: ast.AST | None) -> bool:
+        if isinstance(node, (ast.List, ast.Tuple)):
+            return all(simple(item) for item in node.elts)
+        if not isinstance(node, ast.Attribute):
+            return False
+        mark = node.value
+        return (isinstance(mark, ast.Attribute) and mark.attr == "mark" and isinstance(mark.value, ast.Name)
+                and mark.value.id in pytest_aliases or isinstance(mark, ast.Name) and mark.id in mark_aliases)
+    if assignments and not simple(assignments[0].value):
+        return None, "module pytestmark 호출/동적 표현 — 전사 미지원"
+    statement = "pytestmark = [" + ", ".join("pytest.mark." + name for name in entry.signals.markers) + "]"
+    import_needed = bool(entry.signals.markers) and "pytest" not in pytest_aliases
+    lines = original.splitlines(keepends=True)
+    def offset(line: int, column: int = 0) -> int:
+        return sum(len(part) for part in lines[:line - 1]) + column
+    changed = original
+    if assignments:
+        node = assignments[0]
+        start, end = offset(node.lineno, node.col_offset), offset(node.end_lineno, node.end_col_offset)
+        changed = original[:start] + statement.encode("utf-8") + original[end:]
+    # Insert imports/list after module docstring and future statements, preserving every other byte.
+    prefix_nodes = []
+    for index, node in enumerate(module.body):
+        if (index == 0 and isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant)
+                and isinstance(node.value.value, str)) or isinstance(node, ast.ImportFrom) and node.module == "__future__":
+            prefix_nodes.append(node)
+        else:
+            break
+    insert_at = offset(prefix_nodes[-1].end_lineno + 1) if prefix_nodes else 0
+    additions = (["import pytest"] if import_needed else []) + ([] if assignments else [statement])
+    if additions:
+        newline = b"\r\n" if b"\r\n" in original else b"\n"
+        addition = newline.join(x.encode() for x in additions) + newline
+        if insert_at and original[insert_at - 1:insert_at] != b"\n":
+            addition = newline + addition
+        changed = changed[:insert_at] + addition + changed[insert_at:]
+    try:
+        compile(changed, entry.path, "exec")
+    except (SyntaxError, ValueError) as exc:
+        return None, f"marker 합성 compile 실패: {exc}"
+    if changed == original:
+        return None, "module marker 후상태가 현재와 동일 — 실효 조치 없음"
+    return changed, "module marker 후상태만 전사; 함수/class decorator·본문 변경은 S5"
+
+
+class _DeclarationTypes:
+    """사본의 타입 표면에 명시 클래스 후상태만 겹치는 읽기 전용 그래프."""
+
+    def __init__(self, plan: Plan, copy: Path) -> None:
+        self.plan = plan
+        self.copy = copy
+        self.modules: dict[str, dict[str, list[object]]] = {}
+
+    @staticmethod
+    def module(path: str) -> str:
+        parts = list(PurePosixPath(path).with_suffix("").parts)
+        if parts[-1] == "__init__":
+            parts.pop()
+        return ".".join(parts)
+
+    def load(self, module: str) -> dict[str, list[object]]:
+        if module in self.modules:
+            return self.modules[module]
+        table: dict[str, list[object]] = {}
+        self.modules[module] = table
+        path = module.replace(".", "/") + ".py"
+        actual = self.copy / path
+        if not actual.is_file():
+            path = module.replace(".", "/") + "/__init__.py"
+            actual = self.copy / path
+        entries = [e for e in self.plan.entries.values() if self.module(e.path) == module]
+        if entries:
+            path = entries[0].path
+        def put(name: str, value: object) -> None:
+            values = table.setdefault(name, [])
+            # Repeated identical explicit imports are one provenance; duplicate declarations are ambiguous.
+            if isinstance(value, tuple) and value in values:
+                return
+            values.append(value)
+        def collect(node: ast.AST, conditional: bool = False) -> None:
+            if isinstance(node, ast.ImportFrom):
+                resolved = (_resolve_relative(PurePosixPath(path).parts, node.level, node.module)
+                            if node.level else tuple((node.module or "").split(".")))
+                origin = ".".join(resolved or ())
+                for alias in node.names:
+                    put(alias.asname or alias.name, None if conditional else (origin, alias.name))
+            elif isinstance(node, ast.Import):
+                for alias in node.names:
+                    put(alias.asname or alias.name.split(".")[0], None if conditional else
+                        (alias.name if alias.asname else alias.name.split(".")[0], ""))
+            elif isinstance(node, ast.ClassDef):
+                put(node.name, None if conditional else node)
+            elif isinstance(node, (ast.Assign, ast.AnnAssign)):
+                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
+                for target in targets:
+                    if isinstance(target, ast.Name):
+                        put(target.id, None if conditional else node.value)
+            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
+                put(node.name, None)
+            else:
+                for child in ast.iter_child_nodes(node):
+                    if isinstance(child, ast.stmt):
+                        collect(child, True)
+        if actual.is_file():
+            try:
+                for node in ast.parse(actual.read_text(encoding="utf-8")).body:
+                    collect(node)
+            except (OSError, UnicodeError, SyntaxError):
+                table["*"] = [None]
+        for entry in entries:
+            # Spec import rows can supplement current imports, but conflicting sources stay ambiguous.
+            for statement in entry.imports:
+                try:
+                    for node in ast.parse(statement).body:
+                        collect(node)
+                except SyntaxError:
+                    table["*"] = [None]
+            declared: dict[str, list[object]] = {}
+            for alias in entry.declaration_aliases:
+                first = ast.parse(alias.statement).body[0].value
+                other = ast.parse(alias.runtime).body[0].value if alias.type_checking else first
+                declared.setdefault(alias.name, []).append(first if ast.dump(first) == ast.dump(other) else None)
+            for symbol in entry.declarations:
+                if symbol.kind != "class":
+                    continue
+                try:
+                    body = [f"class {symbol.name}:"] + ["    " + f for f in symbol.fields]
+                    for method in symbol.methods:
+                        body += [f"    def {method.name}(self{', ' if method.params else ''}{method.params})"
+                                 f"{' -> ' + method.ret if method.ret else ''}: ..."]
+                    if len(body) == 1:
+                        body.append("    pass")
+                    node = ast.parse("\n".join(body)).body[0]
+                except (SyntaxError, ValueError):
+                    node = None
+                declared.setdefault(symbol.name, []).append(node)
+            table.update(declared)
+        return table
+
+    def resolve(self, module: str, expression: ast.expr, seen: frozenset[tuple[str, str]] = frozenset()
+                ) -> tuple[list[tuple[str, str, ast.ClassDef | None]], list[str]]:
+        """컨테이너·alias·forward 타입을 identity로 해소한다. 미해소는 후보 근거다."""
+        if isinstance(expression, ast.Constant):
+            if isinstance(expression.value, str):
+                try:
+                    return self.resolve(module, ast.parse(expression.value, mode="eval").body, seen)
+                except SyntaxError:
+                    return [], [f"forward annotation 파싱 불가: {expression.value}"]
+            return [], []
+        if isinstance(expression, (ast.Tuple, ast.List)):
+            nodes = expression.elts
+        elif isinstance(expression, ast.BinOp) and isinstance(expression.op, ast.BitOr):
+            nodes = [expression.left, expression.right]
+        elif isinstance(expression, ast.Subscript):
+            head = ast.unparse(expression.value)
+            identity, issues = self.resolve(module, expression.value, seen)
+            names = {(m, n) for m, n, _ in identity}
+            if ("typing", "Literal") in names:
+                return [], []
+            supported = {"list", "tuple", "set", "frozenset", "dict", "Mapping", "Sequence", "Optional", "Union"}
+            builtin_container = head in {"list", "tuple", "set", "frozenset", "dict"} and head not in self.load(module)
+            if builtin_container or any(m in ("typing", "collections.abc", "builtins") and n in supported for m, n in names):
+                return self.resolve(module, expression.slice, seen)
+            # Unknown generic semantics cannot prove contained field identity.
+            return [], issues or [f"타입 컨테이너 출처/필드 의미 미해소: {head}"]
+        else:
+            nodes = []
+        if nodes:
+            identities, issues = [], []
+            for node in nodes:
+                found, uncertain = self.resolve(module, node, seen)
+                identities.extend(found)
+                issues.extend(uncertain)
+            return identities, issues
+        if not isinstance(expression, (ast.Name, ast.Attribute)):
+            return [], [f"타입식 미지원: {ast.unparse(expression)}"]
+        name = ast.unparse(expression)
+        primitive = {"str", "int", "float", "bool", "bytes", "bytearray", "object", "None", "complex"}
+        if name in primitive:
+            return [], []
+        key = (module, name)
+        if key in seen:
+            return [], [f"alias cycle: {module}.{name}"]
+        seen = seen | {key}
+        if isinstance(expression, ast.Attribute):
+            pieces = name.split(".")
+            table = self.load(module)
+            root = table.get(pieces[0], [])
+            if len(root) == 1 and isinstance(root[0], tuple):
+                origin, symbol = root[0]
+                qualified = [origin] + ([symbol] if symbol else []) + pieces[1:]
+                target = ".".join(qualified[:-1])
+                return self.identity(target, pieces[-1], seen)
+            if root:
+                return [], [f"qualified 타입 출처 중복/미해소: {name}"]
+            if self._known_root(pieces[0]):
+                return self.identity(".".join(pieces[:-1]), pieces[-1], seen)
+            return [], [f"qualified 타입 출처 미해소: {name}"]
+        return self.identity(module, name, seen, local=True)
+
+    def _known_root(self, name: str) -> bool:
+        return name in ("typing", "builtins", "collections") or _is_repo_target(self.copy, name, self.plan)
+
+    def identity(self, module: str, name: str, seen: frozenset[tuple[str, str]], local: bool = False
+                 ) -> tuple[list[tuple[str, str, ast.ClassDef | None]], list[str]]:
+        values = self.load(module).get(name, [])
+        if len(values) > 1 or values == [None]:
+            return [], [f"타입 선언 중복/분기 불일치: {module}.{name}"]
+        if values:
+            value = values[0]
+            if isinstance(value, ast.ClassDef):
+                return [(module, name, value)], []
+            if isinstance(value, tuple):
+                origin, imported = value
+                if not imported:
+                    return [], [f"모듈 자체는 필드 타입 미확정: {module}.{name}"]
+                key = (origin, imported)
+                if key in seen:
+                    return [], [f"alias cycle: {origin}.{imported}"]
+                return self.identity(origin, imported, seen | {key})
+            if isinstance(value, ast.expr):
+                return self.resolve(module, value, seen)
+            return [], [f"타입 출처 미해소: {module}.{name}"]
+        if local:
+            return [], [f"bare 타입 `{name}` 출처 미해소 — 명시 import/별칭 출처를 보완해 주세요"]
+        # An explicit import/qualified module identity proves provenance; it does not prove existence.
+        return [(module, name, None)], []
+
+
+def check_declarations(plan: Plan, copy: Path) -> list[DeclarationFinding]:
+    """효과·DTO 명시 선언의 확정/후보 근거를 반환한다. 사본 파일을 변경하지 않는다."""
+    types = _DeclarationTypes(plan, copy)
+    findings: list[DeclarationFinding] = []
+
+    def add(rule: str, path: str, owner: str, detail: str, confirmed: bool) -> None:
+        finding = DeclarationFinding(rule, path, owner, detail, confirmed)
+        if finding not in findings:
+            findings.append(finding)
+
+    def annotations(cls: ast.ClassDef, constructor: bool = False) -> list[ast.expr]:
+        result = [n.annotation for n in cls.body if isinstance(n, ast.AnnAssign)]
+        if constructor:
+            for node in cls.body:
+                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "__init__":
+                    args = [*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs]
+                    args += [a for a in (node.args.vararg, node.args.kwarg) if a is not None]
+                    result += [a.annotation for a in args if a.annotation is not None]
+        return result
+
+    for effect in plan.effects:
+        if effect.effect == "read-only" and effect.uow != "none":
+            add("#197", effect.path, effect.owner, f"read-only + uow={effect.uow} 명시 모순", True)
+            continue
+        module = types.module(effect.path)
+        values = types.load(module).get(effect.owner, [])
+        injected, unknown = [], []
+        if len(values) == 1 and isinstance(values[0], ast.ClassDef):
+            for annotation in annotations(values[0], True):
+                identities, issues = types.resolve(module, annotation)
+                injected += [f"{m}.{n}" for m, n, _ in identities if ".application_layer.port.unit_of_work." in m + "."]
+                if "UnitOfWork" in ast.unparse(annotation):
+                    unknown += issues
+        else:
+            unknown.append("클래스 선언 중복/파싱 불가")
+        if effect.effect == "read-only":
+            if injected:
+                add("#197", effect.path, effect.owner, "read-only + uow=none에 명시 UoW port 주입: " + ", ".join(injected), True)
+            elif unknown:
+                add("#197", effect.path, effect.owner, "; ".join(unknown), False)
+        elif effect.uow == "none" and injected:
+            note = f"채널 불일치(비차단): {effect.path}::{effect.owner} write/uow=none + 주입 {', '.join(injected)}"
+            if note not in plan.notes:
+                plan.notes.append(note)
+
+    for entry in plan.entries.values():
+        if entry.tag not in ("add", "update"):
+            continue
+        if not ((entry.path.endswith("_result.py") and "/application_layer/" in entry.path)
+                or (entry.path.endswith("_response.py") and "/open_host_service/" in entry.path)):
+            continue
+        module = types.module(entry.path)
+        for owner, values in types.load(module).items():
+            if owner.startswith("_") or not owner.endswith(("Result", "Out", "Response")):
+                continue
+            if len(values) != 1 or not isinstance(values[0], ast.ClassDef):
+                if owner in entry.declared:
+                    add("#202", entry.path, owner, "DTO 선언 중복/미해소 — 출처 보완 필요", False)
+                continue
+            visited: set[tuple[str, str]] = set()
+            confirmed: list[str] = []
+            uncertain: list[str] = []
+            def walk(current: str, name: str, cls: ast.ClassDef) -> None:
+                key = (current, name)
+                if key in visited:
+                    return
+                visited.add(key)
+                for annotation in annotations(cls):
+                    identities, issues = types.resolve(current, annotation)
+                    uncertain.extend(issues)
+                    for origin, symbol, child in identities:
+                        segments = origin.split(".")
+                        domain = segments[segments.index("domain_layer") + 1:] if "domain_layer" in segments else []
+                        if domain and any(s in domain for s in ("value_object", "shared_value_object")):
+                            continue
+                        elif domain and ("entity" in domain or "aggregate" in domain
+                                         or len(domain) >= 2 and domain[0] == domain[1]):
+                            confirmed.append(f"{origin}.{symbol}")
+                        elif child is not None:
+                            walk(origin, symbol, child)
+                        elif _is_repo_target(copy, origin.split(".")[0], plan):
+                            uncertain.append(f"타입 `{origin}.{symbol}` 필드 선언/출처 보완 필요")
+            walk(module, owner, values[0])
+            if confirmed:
+                add("#202", entry.path, owner, "DTO 필드에서 domain aggregate/entity 도달: " + ", ".join(sorted(set(confirmed))), True)
+            if uncertain:
+                add("#202", entry.path, owner, "; ".join(sorted(set(uncertain))) + " — 출처 보완 검토 질문", False)
+    return findings
+
+
 def materialize(copy: Path, plan: Plan, *, realized: "frozenset[str]" = frozenset(),
                 base_short: str = "", promoted: "frozenset[str]" = frozenset()) -> "dict[str, list[str]]":
     """태그 의미론(D2)대로 사본 위에 팬텀을 겹친다 — add 실존 충돌은 FormError.
 
     `promoted` = `baseline_form_errors` 가 승격 형태 예외로 통과시킨 update 경로(미시뮬레이션 문면만 다르다).
 
     **재발화 판형(`--base` 명시 — Phase 2 진입 후 명세 개정 재실행)**: `realized` 는 `lift_realized_adds` 가
     앵커 커밋 전에 사본에서 걷어낸 «기실현 add» 경로다 — 여기서는 다른 add 와 똑같이 스텁으로 실체화하고
     (materialized 에 계수) already-built 에도 «기실현 — 스텁 대체 예보»로 기록한다(이중 기재는 의도 —
     `empty(기실현)` 은 materialized 에 안 실리는 것과 구별). 사본에 실존하는 add 는 기준선 트리 실존(계획↔실물
@@ -1345,20 +1787,26 @@
                 target.unlink()
                 report["materialized"].append(f"removed {entry.path}")
             else:
                 report["unsimulated"].append(f"remove(실존 없음): {entry.path}")
         elif entry.tag == "update":
             updated: "bytes | None"
             detail: str
             updated, detail = _render_service_update(copy, entry)
             if updated is not None:
                 target.write_bytes(updated)
+            marker_update, marker_detail = _render_marker_update(copy, entry)
+            if marker_update is not None:
+                updated = marker_update
+            detail += "; " + marker_detail
+            if updated is not None:
+                target.write_bytes(updated)
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
@@ -1860,42 +2308,62 @@
     "red 로 앞서 선다) / 행 자체가 없다 = 동적 import"
     "(`importlib` 리터럴).",
 )
 
 
 def _executor_stamp(blk_hash: str) -> str:
     """리포트 헤더 스탬프 — 버전 판별(행 수 휴리스틱 폐기)과 캐시 skip 대조(블록 해시)의 단일 자리."""
     return f"실행기: design_pregate.py · dddjango v{plugin_version()} · 블록 해시 {blk_hash}"
 
 
+def _declaration_lines(findings: list[DeclarationFinding] | tuple[DeclarationFinding, ...]) -> list[str]:
+    """확정 처분 ID와 후보 검토 ID는 같은 rule/path 단위를 유지하되 채널을 분리한다."""
+    lines: list[str] = []
+    for confirmed, title in ((True, "선언 확정"), (False, "선언 후보")):
+        grouped: dict[str, list[str]] = {}
+        for item in findings:
+            if item.confirmed != confirmed:
+                continue
+            line = f"[{item.rule}] {item.path}"
+            grouped.setdefault(line, []).append(f"{item.owner}: {item.detail}")
+        lines += ["", f"### {title} ({len(grouped)}건)", ""]
+        for line, details in grouped.items():
+            lines.append(f"- `{_stable_id(line)}` {line} — " + "; ".join(dict.fromkeys(details)))
+        if not grouped:
+            lines.append("- (없음)")
+    return lines
+
+
 def write_report(report_path: Path, spec: Path, base_ref: str, base_sha: str, verdict: str,
                  attributed: "list[str]", mat: "dict[str, list[str]]",
-                 notes: "list[str]", blk_hash: str, existence: ExistenceReport) -> None:
+                 notes: "list[str]", blk_hash: str, existence: ExistenceReport,
+                 declarations: list[DeclarationFinding] | tuple[DeclarationFinding, ...] = ()) -> None:
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
         f"- 판정: {verdict}",
         "",
         f"### 예보 항목 ({len(attributed)}건 · 안정 ID = sha256(규칙#+경로)[:12])",
         "",
     ]
     if attributed:
         lines.extend(f"- `{_stable_id(line)}` {line}" for line in attributed)
     else:
         lines.append("- (없음) — green 은 «설계 검증됨»이 아니라 «P/S/I급 위반 예보 0»이다.")
+    lines.extend(_declaration_lines(declarations))
     lines.extend(_existence_lines(existence))
     lines += ["", f"### already-built ({len(mat.get('already_built', []))}건) · "
                   f"미시뮬레이션 ({len(mat.get('unsimulated', []))}건)", ""]
     for item in mat.get("already_built", []):
         lines.append(f"- already-built: {item}")
     for item in mat.get("unsimulated", []):
         lines.append(f"- 미시뮬레이션: {item}")
     for item in mat.get("pruned_dirs", []):
         lines.append(f"- remove 빈 부모 정리: {item}")
     for note in notes:
@@ -1906,37 +2374,39 @@
     lines.extend(f"- {spot}" for spot in BLIND_SPOTS)
     lines.append("")
     report_path.parent.mkdir(parents=True, exist_ok=True)
     with report_path.open("a", encoding="utf-8") as fp:
         fp.write("\n".join(lines))
     print(f"\n예보 리포트 append → {report_path}")
 
 
 def write_report_stub(report_path: "Path | None", spec: Path, base_ref: str, base_sha: str,
                       verdict: str, detail: "list[str]", blk_hash: str,
-                      existence: "ExistenceReport | None" = None) -> None:
+                      existence: "ExistenceReport | None" = None,
+                      declarations: list[DeclarationFinding] | tuple[DeclarationFinding, ...] = ()) -> None:
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
         f"- 판정: {verdict}",
         "",
     ]
     lines.extend(f"- {item}" for item in detail)
+    lines.extend(_declaration_lines(declarations))
     if existence is not None:
         lines.extend(_existence_lines(existence))
     lines.append("")
     report_path.parent.mkdir(parents=True, exist_ok=True)
     with report_path.open("a", encoding="utf-8") as fp:
         fp.write("\n".join(lines))
 
 
 # ── 차단 모드 — 계획↔기준선 모순(형식 red) · 리포트 최신성 대조(--check-report) ──────────────────
 
@@ -2053,45 +2523,49 @@
     problems: "list[str]" = []
     report_hash: str = hash_m.group(1) if hash_m else "-"
     if hash_m is None:
         problems.append("최신성 증명 불가 — 마지막 헤더에 블록 해시 토큰이 없다(구판 리포트) · 재발화")
     elif report_hash != spec_hash:
         problems.append(f"stale — 명세 블록 해시 {spec_hash} ≠ 마지막 예보 {report_hash} · 재발화")
     count_m: "re.Match[str] | None" = _REPORT_COUNT_RE.search(verdict)
     defect_m: "re.Match[str] | None" = _REPORT_DEFECT_RE.search(verdict)
     attributed: int = int(count_m.group(1)) if count_m else 0
     defects: int = int(defect_m.group(1)) if defect_m else 0
+    declarations: int = len(set(_REPORT_ID_RE.findall(_subsection(section, "선언 확정"))))
+    candidates: int = len(set(_REPORT_ID_RE.findall(_subsection(section, "선언 후보"))))
     short: str
     if verdict.startswith("형식 red"):
         problems.append(f"형식 red 미해소 — 마지막 판정 «{verdict}» · architect 반송")
         short = "형식 red"
     elif verdict.startswith("예보 red"):
-        ids: "list[str]" = _REPORT_ID_RE.findall(_subsection(section, "예보 항목"))
+        ids: "list[str]" = list(dict.fromkeys(_REPORT_ID_RE.findall(_subsection(section, "예보 항목"))
+                    + _REPORT_ID_RE.findall(_subsection(section, "선언 확정"))))
         missing: "list[str]" = [i for i in ids if not _disposed(section, i)]
         if missing:
             problems.append(f"처분 미기재 {len(missing)}건(ignored|filtered 행 없음 — corrected 는 재실행이 최종본): "
                             + " ".join(f"`{i}`" for i in missing))
         short = f"red {attributed}({'처분 전건' if not missing else f'미기재 {len(missing)}'}) · 실존 결손 {defects}"
     elif verdict.startswith("예보 green"):
         short = "green" + (f" · 실존 결손 {defects}" if defects else "")
     elif verdict.startswith("skip"):
         short = "skip" + (f" · 실존 결손 {defects}" if defects else "")
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
+        "declarations": str(declarations), "candidates": str(candidates),
         "base": base_m.group(1)[:12] if base_m else "-",
     }
     return (3 if problems else 0), problems, info
 
 
 def run_check_report(spec_text: str, report_path: Path, blk_hash: str) -> int:
     """`--check-report` 진입 — 배너(G1/G1′)·G2 근거 대조의 유일한 기계 출처(`요약:` 행)."""
     print(f"# design_pregate --check-report · 모드 차단({MODE}) · {_executor_stamp(blk_hash)}")
     if not report_path.is_file():
         print(f"실행 불능: 리포트 부재 — {report_path} (pre-gate 가 이 레인에서 한 번도 실행되지 않았다 · 구형 명세·"
@@ -2102,21 +2576,22 @@
     code: int = result[0]
     problems: "list[str]" = result[1]
     info: "dict[str, str]" = result[2]
     if code == 1:
         print(f"실행 불능: {problems[0]}", file=sys.stderr)
         return 1
     for p in problems:
         print(f"  불비: {p}")
     status: str = "정합" if code == 0 else f"불비 {len(problems)}건"
     print(f"\n요약: check-report {status} · 블록 해시 {info['spec_hash']}={info['report_hash']} · "
-          f"마지막 판정 {info['short']} · 귀속 {info['attributed']}건 · 실존 결손 {info['defects']}건 · "
+          f"마지막 판정 {info['short']} · 귀속 {info['attributed']}건 · 선언 확정 {info['declarations']}건 · "
+          f"선언 후보 {info['candidates']}건 · 실존 결손 {info['defects']}건 · "
           f"기준선 {info['base']}")
     return code
 
 
 # ── main ────────────────────────────────────────────────────────────────────
 
 def main(argv: "list[str]") -> int:
     ap: _UsageParser = _UsageParser(add_help=True, description="design-spec pre-gate 예보 실행기")
     ap.add_argument("spec", help="설계 명세 markdown(기계 블록 §4 포함)")
     ap.add_argument("target", help="대상 저장소 루트(git)")
@@ -2233,70 +2708,78 @@
         try:
             mat: "dict[str, list[str]]" = materialize(copy, plan, realized=realized, base_short=base_sha[:12],
                                                       promoted=promoted)
         except FormError as exc:
             print(f"형식 red — {exc}")
             write_report_stub(report_path, spec_path, base_ref, base_sha, "형식 red", [str(exc)], blk_hash)
             print(f"\n요약: 형식 red 1건({_error_kinds([str(exc)])}) · 기준선 {base_sha[:12]} · 모드 차단")
             return 3
 
         # 계약 실존 — materialize(+골격·`__init__` 체인) 뒤 · 실체화-0 분기 앞(update 소비자만의 명세도 판정한다).
+        declarations = check_declarations(plan, copy)
+        declaration_count = len({(item.rule, item.path) for item in declarations if item.confirmed})
+        for line in _declaration_lines(declarations):
+            print(line)
         existence: ExistenceReport = check_import_existence(copy, plan)
         own_note: "str | None" = _own_interpreter_note(repo)
         if own_note is not None:
             existence.undecidable_notes.append(own_note)
         defects: int = len(existence.defects)
         cleanup_notes: "list[str]" = [f"remove 빈 부모 정리: {p}" for p in mat["pruned_dirs"]]
         for note in cleanup_notes:
             print(note)
 
         if not mat["materialized"]:
             reason = ("skip — 실체화 0건(add/empty/remove 및 제한 update 실효 조치 없음): "
                       "게이트를 부르지 않는다(공허 차분 가드 · 사유 명시)")
-            verdict_stub: str = "skip" + (f" · 계약 실존 결손 {defects}건(권고·비차단)" if defects else "")
+            verdict_stub: str = (f"예보 red — 선언 확정 {declaration_count}건" if declaration_count else "skip") + (f" · 계약 실존 결손 {defects}건(권고·비차단)" if defects else "")
             print(reason)
+            for note in plan.notes:
+                print(f"  채널 메모: {note}")
             for item in mat["unsimulated"]:
                 print(f"  미시뮬레이션: {item}")
             _print_existence(existence)
-            print(f"\n요약: 실체화 0 · 실존 결손 {defects}건 · 기준선 {base_sha[:12]} · 모드 차단")
+            print(f"\n요약: 실체화 0 · 실존 결손 {defects}건 · 선언 확정 {declaration_count}건 · 기준선 {base_sha[:12]} · 모드 차단")
             write_report_stub(report_path, spec_path, base_ref, base_sha, verdict_stub,
-                              [reason] + [f"미시뮬레이션: {x}" for x in mat["unsimulated"]] + cleanup_notes, blk_hash,
-                              existence=existence)
-            return 5 if defects else 4
+                              [reason] + [f"미시뮬레이션: {x}" for x in mat["unsimulated"]] + cleanup_notes
+                              + [f"채널 메모: {n}" for n in plan.notes], blk_hash,
+                              existence=existence, declarations=declarations)
+            return 2 if declaration_count else (5 if defects else 4)
 
         print(f"# design_pregate — 예보 실행 · 기준선 {base_sha[:12]} (--base {base_ref}) · "
               f"모드 차단({MODE}) · {_executor_stamp(blk_hash)}")
         print(f"({NO_SUBSTITUTE})")
         print(f"실체화 {len(mat['materialized'])}건 · dirty overlay {len(overlaid)}건 · "
               f"미시뮬레이션 {len(mat['unsimulated'])}건 · already-built {len(mat['already_built'])}건")
 
         gate_result: "tuple[int, list[str], str]" = run_gate(copy, scratch, ns.python_bin)
         gate_exit: int = gate_result[0]
         attributed: "list[str]" = gate_result[1]
         print("\n" + gate_result[2].rstrip())
 
         verdict: str = ("예보 green — P/S/I급 결정 계약 위반 예보 0(«설계 검증됨» 아님)"
-                        if gate_exit == 0 else
+                        if gate_exit == 0 and not declaration_count else
                         f"예보 red — P/S/I급 결정 계약 위반 예보 {len(attributed)}건")
+        verdict += f" · 선언 확정 {declaration_count}건"
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
-                         attributed, mat, plan.notes, blk_hash, existence)
-        if gate_exit != 0:
+                         attributed, mat, plan.notes, blk_hash, existence, declarations)
+        if gate_exit != 0 or declaration_count:
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
--- a/workspace/tools/pregate_field_report_smoke.py
+++ b/workspace/tools/pregate_field_report_smoke.py
@@ -285,13 +285,251 @@
         self.write(self.source, TEST, "def test_case() -> None: pass\n")
         for owner, tag in [(f"unlisted/test_first.py `{SUPPORT}` [markers: django_db]", "add"),
                            (f"`{SUPPORT}`", "add"),
                            (f"`{TEST}` [markers: django_db] `{SUPPORT}`", "update")]:
             with self.subTest(owner=owner):
                 paths = [f"add {SUPPORT}"] + ([f"{tag} {TEST}"] if tag == "update" else [])
                 self.materialize(spec_text(paths, [f"{SUPPORT}::test_support() -> None"], owner=owner))
                 output = self.checker("check-test-config.py")
                 self.assertTrue(any("[#389]" in line and SUPPORT in line for line in output.splitlines()), output)
 
+    def effects(self, text, *rows):
+        return text + '<!-- machine: use-case-effects -->\n```effects\n' + '\n'.join(rows) + '\n```\n'
+
+    def test_effect_declaration_contract_and_hash(self):
+        path = 'application/garden/application_layer/books/list_books/list_books_use_case.py'
+        uow = 'application.garden.application_layer.port.unit_of_work.book_unit_of_work'
+        for effect, declared, injected, expected in [
+            ('read-only', 'none', False, []), ('read-only', 'BookUnitOfWork', False, [('#197', True)]),
+            ('read-only', 'none', True, [('#197', True)]), ('write', 'BookUnitOfWork', True, []),
+            ('write', 'none', True, [])]:
+            with self.subTest(effect=effect, declared=declared, injected=injected):
+                text = spec_text([f'update {path}'], [f'{path}::ListBooksUseCase'] +
+                    ([f'{path}::ListBooksUseCase.__init__(self, uow: BookUnitOfWork)'] if injected else []),
+                    [f'{path}  from {uow} import BookUnitOfWork'])
+                text = self.effects(text, f'{path}::ListBooksUseCase  {effect}  uow={declared}')
+                plan, errors = pg.parse_spec(text)
+                self.assertEqual(errors, [])
+                self.assertEqual([(x.rule, x.confirmed) for x in pg.check_declarations(plan, self.source)], expected)
+                if effect == 'write' and declared == 'none':
+                    self.assertTrue(any('채널' in n or '불일치' in n for n in plan.notes))
+        base = spec_text([f'update {path}'], [f'{path}::ListBooksUseCase'])
+        # Legacy literal hash protects cache compatibility without effects.
+        import hashlib
+        parts = []
+        for name in ['file-plan', 'symbols', 'boundary-imports', 'exception-map']:
+            parts += [f'<!-- machine: {name} -->', *pg._machine_blocks(base, [])[name]]
+        parts += ['<!-- physical-signals -->']
+        self.assertEqual(pg.block_hash(base), hashlib.sha256('\n'.join(parts).encode()).hexdigest()[:12])
+        first = self.effects(base, f'{path}::ListBooksUseCase  read-only  uow=none')
+        self.assertNotEqual(pg.block_hash(first), pg.block_hash(base))
+        self.assertEqual(pg.block_hash(first), pg.block_hash(first + '\nprose'))
+        self.assertNotEqual(pg.block_hash(first), pg.block_hash(first.replace('uow=none', 'uow=X')))
+        for row in [f'{path}::ListBooksUseCase  other  uow=none', f'{path}::ListBooksUseCase  write  uow=',
+                    f'{path}::Missing  write  uow=none', f'unlisted.py::ListBooksUseCase  write  uow=none',
+                    f'{path}::ListBooksUseCase  write  uow=[',
+                    f'{path}::ListBooksUseCase  write  uow=none\n{path}::ListBooksUseCase  write  uow=none']:
+            self.assertTrue(pg.parse_spec(self.effects(base, row))[1], row)
+
+    def test_update_marker_final_state_and_preservation(self):
+        originals = ['from __future__ import annotations\nimport pytest\npytestmark = pytest.mark.django_db\n\ndef test_case(): return 42\n',
+                     'from __future__ import annotations\n\ndef test_case(): return 42\n']
+        for original in originals:
+            for markers in ['', 'django_db', 'slow']:
+                with self.subTest(original=original, markers=markers):
+                    self.write(self.source, TEST, original)
+                    _, report = self.materialize(spec_text([f'update {TEST}'], owner=f'{TEST} [markers: {markers}]'))
+                    updated = (self.copy / TEST).read_text()
+                    self.assertIn('def test_case(): return 42', updated)
+                    self.assertIn('pytestmark = [' + ', '.join('pytest.mark.' + m for m in markers.split(',') if m) + ']', updated)
+                    self.assertIn(TEST, report['materialized'])
+                    compile(updated, TEST, 'exec')
+        for tail in ['pytestmark = pytest.mark.django_db(transaction=True)\n',
+                     'pytestmark = calculate()\n', 'pytestmark = []\npytestmark = []\n',
+                     'if True:\n    pytestmark = []\n', 'pytestmark = []\npytestmark += []\n',
+                     'pytest = object()\npytestmark = []\n']:
+            original = 'import pytest\n' + tail + 'def test_case(): pass\n'
+            self.write(self.source, TEST, original)
+            _, report = self.materialize(spec_text([f'update {TEST}'], owner=f'{TEST} [markers: django_db]'))
+            self.assertEqual((self.copy / TEST).read_text(), original)
+            self.assertNotIn(TEST, report['materialized'])
+            self.assertTrue(report['unsimulated'])
+        self.write(self.source, TEST, 'import pytest as pt\npytestmark: list = (pt.mark.slow,)\n@pt.mark.django_db\nclass TestBook: pass\n')
+        self.materialize(spec_text([f'update {TEST}'], owner=f'{TEST} [markers:]'))
+        self.assertIn('@pt.mark.django_db', (self.copy / TEST).read_text())
+        self.assertIn('pytestmark = []', (self.copy / TEST).read_text())
+        for owner in [f'{TEST}::case [markers: django_db]', f'{TEST}::TestBook [markers: django_db]',
+                      f'{TEST} [markers: django_db(transaction=True)]', f'{TEST} [base: TestCase] [client: yes]', TEST]:
+            self.materialize(spec_text([f'update {TEST}'], owner=owner))
+            self.assertEqual((self.copy / TEST).read_bytes(), (self.source / TEST).read_bytes())
+        conflict = spec_text([f'update {TEST}'], owner=f'{TEST} [markers: slow]')
+        conflict += f'| second | persisted | omitted | none | update | {TEST} [markers: django_db] |\n'
+        self.assertTrue(pg.parse_spec(conflict)[1])
+
+    def test_dto_type_provenance_nested_alias_forward_and_candidates(self):
+        result = 'application/garden/application_layer/books/list_books/list_books_result.py'
+        entity = 'application/garden/domain/books/aggregate/book.py'
+        # Actual canonical tree uses domain/aggregate families; field provenance must be explicit.
+        entity = 'application/garden/domain_layer/books/aggregate/book.py'
+        module = entity[:-3].replace('/', '.')
+        self.write(self.source, entity, 'class Book: pass\n')
+        self.write(self.source, result, 'class ListBooksResult:\n    old: int\n\nclass Kept:\n    book: int\n')
+        for annotation in ['Book', 'list[Book]', 'dict[str, tuple[Book, ...]]', 'Optional[Book]',
+                           "'list[Book]'", '_Item', 'Rows', 'Book | None']:
+            with self.subTest(annotation=annotation):
+                text = spec_text([f'update {result}'], [f'{result}::alias Rows = list[Book]',
+                    f'{result}::_Item {{book: Book}}', f'{result}::ListBooksResult {{items: {annotation}}}'],
+                    [f'{result}  from {module} import Book', f'{result}  from typing import Optional'])
+                plan, errors = pg.parse_spec(text)
+                self.assertEqual(errors, [])
+                findings = pg.check_declarations(plan, self.source)
+                self.assertEqual([(x.rule, x.confirmed) for x in findings], [('#202', True)])
+                self.assertEqual((self.source / result).read_text(), 'class ListBooksResult:\n    old: int\n\nclass Kept:\n    book: int\n')
+        for declaration, imports, expected in [
+            ('Book', [], [('#202', False)]), ('int', [], []), ('Literal["Book"]', ['from typing import Literal'], []),
+            ('money.Book', ['import external.money as money'], []),
+            ('Book', ['from application.garden.domain_layer.books.value_object.book import Book'], [])]:
+            plan, errors = pg.parse_spec(spec_text([f'update {result}'], [f'{result}::ListBooksResult {{item: {declaration}}}'],
+                                                  [f'{result}  {i}' for i in imports]))
+            self.assertEqual(errors, [])
+            self.assertEqual([(x.rule, x.confirmed) for x in pg.check_declarations(plan, self.source)], expected)
+        for aliases in [[f'{result}::alias A = B', f'{result}::alias B = A'],
+                        [f'{result}::alias[TYPE_CHECKING] A = Book', f'{result}::alias[else] A = int']]:
+            plan, errors = pg.parse_spec(spec_text([f'update {result}'], [*aliases, f'{result}::ListBooksResult {{item: A}}'],
+                [f'{result}  from {module} import Book']))
+            self.assertEqual(errors, [])
+            self.assertEqual([(x.rule, x.confirmed) for x in pg.check_declarations(plan, self.source)], [('#202', False)])
+
+    def cli(self, text):
+        spec = self.root / 'design.md'
+        spec.write_text(text)
+        report = self.root / 'report.md'
+        if report.exists(): report.unlink()
+        run = subprocess.run([sys.executable, '-B', str(SCRIPTS / 'design_pregate.py'), str(spec),
+                              str(self.source), '--report', str(report)], capture_output=True, text=True, env=self.env)
+        return run, report.read_text() if report.exists() else ''
+
+    def test_declaration_only_cli_and_report_dispositions(self):
+        text = self.effects(spec_text([f'update {SERVICE}'], [f'{SERVICE}::ReadBooks']),
+                            f'{SERVICE}::ReadBooks  read-only  uow=BookUnitOfWork')
+        run, report = self.cli(text)
+        self.assertEqual(run.returncode, 2, run.stdout + run.stderr)
+        self.assertIn('선언 확정', report)
+        self.assertEqual(pg.check_report(text, report)[0], 3)
+        stable = pg._stable_id(f'[#197] {SERVICE}')
+        disposed = report + f'\n- `{stable}` **ignored** 명시 검토\n'
+        self.assertEqual(pg.check_report(text, disposed)[0], 0)
+        self.assertEqual(pg.check_report(text, disposed)[2].get("declarations"), "1")
+        self.assertEqual(pg.check_report(text.replace('uow=BookUnitOfWork', 'uow=Other'), disposed)[0], 3)
+        result = f'{SERVICE_DIR}/contract/response/list_books_response.py'
+        self.write(self.source, result, 'class ListBooksResponse: pass\n')
+        _git(self.source, 'add', '-A')
+        _git(self.source, 'commit', '-qm', 'response fixture')
+        text = spec_text([f'update {result}'], [f'{result}::ListBooksResponse {{item: Unknown}}'])
+        run, report = self.cli(text)
+        self.assertEqual(run.returncode, 4, run.stdout + run.stderr)
+        self.assertIn('선언 후보', report)
+        self.assertIn('출처', report)
+        self.assertEqual(pg.check_report(text, report)[0], 0)
+        text = text.replace('```imports\n', f'```imports\n{result}  from application.missing import Unknown\n')
+        run, report = self.cli(text)
+        self.assertEqual(run.returncode, 5, run.stdout + run.stderr)
+
+    def test_marker_update_cli_real_test_config_rule(self):
+        unit = 'application/garden/test/unit/test_book.py'
+        for original, marker, expected in [
+            ('def test_book(): pass\n', 'django_db', True),
+            ('import pytest\npytestmark = pytest.mark.django_db\ndef test_book(): pass\n', '', False),
+            ('import pytest\npytestmark = ()\n@pytest.mark.django_db\ndef test_book(): pass\n', '', False)]:
+            self.write(self.source, unit, original)
+            _git(self.source, 'add', '-A')
+            _git(self.source, 'commit', '-qm', 'marker fixture')
+            text = spec_text([f'update {unit}'], owner=f'{unit} [markers: {marker}]')
+            run, report = self.cli(text)
+            self.assertIn(run.returncode, (0, 2), run.stdout + run.stderr)
+            self.assertEqual('[#387]' in report, expected, report)
+            self.assertEqual((self.source / unit).read_text(), original)
+        # Direct checker retains class/function DB evidence after clearing only module marks.
+        self.materialize(text)
+        self.assertIn('[#387]', self.checker('check-test-config.py'))
+
+    def test_typegraph_real_tree_cross_module_alias_cycles_and_ohs_imports(self):
+        result = 'application/garden/application_layer/books/list_books/list_books_result.py'
+        aggregate = 'application/garden/domain_layer/book/book.py'
+        entity = 'application/garden/domain_layer/book/entity/page.py'
+        helper = 'application/garden/application_layer/books/list_books/item.py'
+        self.write(self.source, aggregate, 'class Book: pass\n')
+        self.write(self.source, entity, 'class Page: pass\n')
+        self.write(self.source, helper, 'from .list_books_result import ListBooksResult\n'
+                   'from application.garden.domain_layer.book.book import Book\n'
+                   'class _Item:\n    parent: ListBooksResult\n    book: Book\n')
+        for annotation, imports in [('_Item', ['from .item import _Item']),
+                                    ('book.Book', ['import application.garden.domain_layer.book.book as book']),
+                                    ('Page', ['from application.garden.domain_layer.book.entity.page import Page']),
+                                    ('application.garden.domain_layer.book.book.Book', [])]:
+            text = spec_text([f'add {result}'], [f'{result}::ListBooksResult {{item: {annotation}}}'],
+                             [f'{result}  {i}' for i in imports])
+            plan, _ = self.materialize(text)
+            findings = pg.check_declarations(plan, self.copy)
+            self.assertEqual([(f.rule, f.confirmed) for f in findings], [('#202', True)], annotation)
+        # Same-name local value object wins over the aggregate catalog.
+        vo = 'application/garden/domain_layer/book/shared_value_object/book.py'
+        self.write(self.source, vo, 'class Book:\n    text: str\n')
+        text = spec_text([f'add {result}'], [f'{result}::ListBooksResult {{item: Book}}'],
+                        [f'{result}  from application.garden.domain_layer.book.shared_value_object.book import Book'])
+        plan, _ = self.materialize(text)
+        self.assertEqual(pg.check_declarations(plan, self.copy), [])
+        # Result consumption must not synthesize a domain import into OHS.
+        text = self.service_spec(imports=['from application.garden.application_layer.books.list_books.list_books_result import ListBooksResult'],
+                                extra_paths=[f'add {result}'], extra_symbols=[f'{result}::ListBooksResult {{item: Book}}'])
+        plan, _ = self.materialize(text)
+        self.assertEqual([(f.rule, f.confirmed) for f in pg.check_declarations(plan, self.copy)], [('#202', False)])
+        self.assertNotIn('[#95]', self.checker('check-context-isolation.py'))
+        self.assertNotIn('[#96]', self.checker('check-event-publish.py'))
+        self.materialize(self.service_spec(imports=['from application.garden.domain_layer.book.book import Book']))
+        self.assertIn('[#95]', self.checker('check-context-isolation.py'))
+        self.assertIn('[#96]', self.checker('check-event-publish.py'))
+
+    def test_unresolved_uow_never_confirms_and_declaration_owners_group(self):
+        for effect, expected in [('read-only', [('#197', False)]), ('write', [])]:
+            text = self.effects(spec_text([f'update {SERVICE}'], [f'{SERVICE}::ListBooks',
+                f'{SERVICE}::ListBooks.__init__(self, uow: StrangeUnitOfWork)']),
+                f'{SERVICE}::ListBooks  {effect}  uow=none')
+            plan, errors = pg.parse_spec(text)
+            self.assertEqual(errors, [])
+            self.assertEqual([(f.rule, f.confirmed) for f in pg.check_declarations(plan, self.source)], expected)
+        text = self.effects(spec_text([f'update {SERVICE}'], [f'{SERVICE}::First', f'{SERVICE}::Second']),
+                            f'{SERVICE}::First  read-only  uow=X', f'{SERVICE}::Second  read-only  uow=Y')
+        run, report = self.cli(text)
+        self.assertEqual(run.returncode, 2, run.stdout + run.stderr)
+        self.assertIn('First:', report)
+        self.assertIn('Second:', report)
+        stable = pg._stable_id(f'[#197] {SERVICE}')
+        self.assertEqual(report.count(f'`{stable}`'), 1)
+        self.assertEqual(pg.check_report(text, report + f'\n- `{stable}` **filtered** reviewed\n')[0], 0)
+
+    def test_marker_update_noop_and_import_binding_are_preserved(self):
+        for original in ['import pytest\npytestmark = []\ndef test_case(): pass\n',
+                         'from somewhere import pytestmark\ndef test_case(): pass\n']:
+            self.write(self.source, TEST, original)
+            _, report = self.materialize(spec_text([f'update {TEST}'], owner=f'{TEST} [markers:]'))
+            self.assertEqual((self.copy / TEST).read_text(), original)
+            self.assertEqual(report['materialized'], [])
+
+    def test_typegraph_container_identity_and_literal_alias(self):
+        result = 'application/garden/application_layer/books/list_books/list_books_result.py'
+        domain_import = f'{result}  from application.garden.domain_layer.book.book import Book'
+        for annotation, symbols, imports, expected in [
+            ('Mapping[Book]', [f'{result}::Mapping {{value: int}}'], [], [('#202', False)]),
+            ('list[Book]', [f'{result}::alias list = Mapping'], [], [('#202', False)]),
+            ('LiteralName["Book"]', [], [f'{result}  from typing import Literal as LiteralName'], []),
+            ('Mapping[str, Book]', [], [f'{result}  from typing import Mapping'], [('#202', True)]),
+            ('Mapping[str, Book]', [], [], [('#202', False)])]:
+            with self.subTest(annotation=annotation, imports=imports):
+                plan, errors = pg.parse_spec(spec_text([f'update {result}'], [*symbols,
+                    f'{result}::ListBooksResult {{value: {annotation}}}'], [domain_import, *imports]))
+                self.assertEqual(errors, [])
+                self.assertEqual([(f.rule, f.confirmed) for f in pg.check_declarations(plan, self.source)], expected)
+
 
 if __name__ == "__main__":
     unittest.main(verbosity=2)
```
