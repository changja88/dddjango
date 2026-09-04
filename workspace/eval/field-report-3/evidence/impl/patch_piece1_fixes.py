"""⑤-1 정정 — rv5-A N-1(MAJOR)·N-2·N-3·N-4·N-5·N-6(a)·N-7·N-9 + rv5-C M1(docstring)·M4(ⓓ legacy 검사기별).
실행: cd /Users/hyun/Desktop/dddjango && python3 <this>
"""
import pathlib

P = pathlib.Path("dddjango/scripts/check-public-surface-annotation.py")
t = P.read_text(encoding="utf-8")


def rep(old: str, new: str, count: int = 1) -> None:
    global t
    assert t.count(old) == count, (t.count(old), old[:90])
    t = t.replace(old, new)


# N-9 · import re 상단
rep("import ast\nimport sys\n", "import ast\nimport re\nimport sys\n")
rep('TYPE_IGNORE_RE = __import__("re").compile(r"#\\s*type:\\s*ignore(?:\\[([^\\]]*)\\])?")\n',
    'TYPE_IGNORE_RE = re.compile(r"#\\s*type:\\s*ignore(?:\\[([^\\]]*)\\])?")\n')
# N-1 (MAJOR) · TC 중간 ClassDef 의 Subscript 기저 전부 기록(첫 기저는 마지막에)
rep("    값 = Assign/AnnAssign 의 Name/Attribute/Subscript · `TYPE_CHECKING` 분기 안 ClassDef 의 첫 기저.\n",
    "    값 = Assign/AnnAssign 의 Name/Attribute/Subscript · `TYPE_CHECKING` 분기 안 ClassDef 의 첫 기저 + 나머지\n    Subscript 기저(mixin-first 형 `class _B(Mixin, admin.ModelAdmin[M])` — 첫 기저를 마지막에 두어 «뒤 정의 우선» 을 보존).\n")
rep("            elif isinstance(st, ast.ClassDef) and in_tc and st.bases:\n                out.setdefault(st.name, []).append((st.bases[0], True))\n",
    "            elif isinstance(st, ast.ClassDef) and in_tc and st.bases:\n                lst = out.setdefault(st.name, [])\n                lst.extend((b, True) for b in st.bases[1:] if isinstance(b, ast.Subscript))  # mixin-first 중간 ClassDef\n                lst.append((st.bases[0], True))\n")
# N-2 · else 분기 런타임 ClassDef 는 ⓐ 대상 밖(ⓑ·ⓓ② 유지)
rep("    lines = src.splitlines()\n    tc_classes: set[ast.ClassDef] = set()\n\n    def mark_tc(stmts: list[ast.stmt], in_tc: bool) -> None:\n        for st in stmts:\n            if isinstance(st, ast.ClassDef) and in_tc:\n                tc_classes.add(st)\n            elif isinstance(st, ast.If):\n                mark_tc(st.body, in_tc or _is_type_checking(st.test))\n                mark_tc(st.orelse, in_tc)\n",
    "    lines = src.splitlines()\n    tc_classes: set[ast.ClassDef] = set()\n    rt_only: set[ast.ClassDef] = set()  # `if TYPE_CHECKING:` 의 else 직계 ClassDef — 런타임 짝(맨몸이 정당 · ⓐ 대상 밖)\n\n    def mark_tc(stmts: list[ast.stmt], in_tc: bool) -> None:\n        for st in stmts:\n            if isinstance(st, ast.ClassDef) and in_tc:\n                tc_classes.add(st)\n            elif isinstance(st, ast.If):\n                if _is_type_checking(st.test):\n                    rt_only.update(s for s in st.orelse if isinstance(s, ast.ClassDef))\n                mark_tc(st.body, in_tc or _is_type_checking(st.test))\n                mark_tc(st.orelse, in_tc)\n")
rep("        elif bare:\n            out.add(\"#646\", where, f\"`{cls.name}` 이 django-stubs 제네릭 기저",
    "        elif bare and cls not in rt_only:\n            out.add(\"#646\", where, f\"`{cls.name}` 이 django-stubs 제네릭 기저")
# N-5 · ⓑ(ii) 는 헤더 범위 밖 줄만
rep("                    for ln in range(st.lineno, (st.end_lineno or st.lineno) + 1):\n                        codes = _ignore_codes(lines[ln - 1]) if ln - 1 < len(lines) else None\n                        if codes and \"type-arg\" in codes:\n",
    "                    for ln in range(st.lineno, (st.end_lineno or st.lineno) + 1):\n                        if ln <= end:\n                            continue  # 한 줄 클래스(`class X(B): x = 1  # type: ignore[type-arg]`)는 헤더 ⓑ(i) 가 이미 셌다\n                        codes = _ignore_codes(lines[ln - 1]) if ln - 1 < len(lines) else None\n                        if codes and \"type-arg\" in codes:\n")
# N-3 · _slot_is_object — Ellipsis 제거 · 이종 튜플 index · dict 키 자리
rep('def _slot_is_object(ann: "ast.AST | None", depth: int, bindings: dict[str, str]) -> bool:\n    """결과가 놓이는 자리의 «선언 값 타입»이 object 인가 — depth 0 = 결과 자체 · 1 = 컨테이너 원소.\n    union 은 전 구성원(None 제외)이 object 슬롯일 때만 True. 주석 부재는 False(후보 — 반환 주석 없는 함수)."""\n',
    'def _slot_is_object(ann: "ast.AST | None", depth: int, bindings: dict[str, str], idx: "int | None" = None) -> bool:\n    """결과가 놓이는 자리의 «선언 값 타입»이 object 인가 — depth 0 = 결과 자체 · 1 = 컨테이너 원소(`idx` = 이종 튜플의\n    원소 위치 · -1 = dict 리터럴의 키 자리 · None = 값/원소 자리). `...` 는 원소가 아니다. union 은 전 구성원(None 제외)이\n    object 슬롯일 때만 True. 주석 부재는 False(후보 — 반환 주석 없는 함수)."""\n')
rep("        return bool(rest) and all(_slot_is_object(m, depth, bindings) for m in rest)\n    if depth == 0:\n        return isinstance(ann, ast.Name) and ann.id == \"object\"\n    if isinstance(ann, ast.Subscript) and _leaf(_resolved_name(ann.value, bindings)) in (RECORD_CONTAINERS | SEQUENCE_CONTAINERS):\n        elts = list(ann.slice.elts) if isinstance(ann.slice, ast.Tuple) else [ann.slice]\n        val = _unstring(elts[-1]) if elts else None\n        return isinstance(val, ast.Name) and val.id == \"object\"\n    return False\n",
    "        return bool(rest) and all(_slot_is_object(m, depth, bindings, idx) for m in rest)\n    if depth == 0:\n        return isinstance(ann, ast.Name) and ann.id == \"object\"\n    if isinstance(ann, ast.Subscript) and _leaf(_resolved_name(ann.value, bindings)) in (RECORD_CONTAINERS | SEQUENCE_CONTAINERS):\n        elts = list(ann.slice.elts) if isinstance(ann.slice, ast.Tuple) else [ann.slice]\n        variadic = any(isinstance(e, ast.Constant) and e.value is Ellipsis for e in elts)\n        elts = [e for e in elts if not (isinstance(e, ast.Constant) and e.value is Ellipsis)]\n        if not elts:\n            return False\n        if idx is not None and idx >= 0 and _leaf(_resolved_name(ann.value, bindings)) in (\"tuple\", \"Tuple\") and not variadic:\n            pick = elts[idx] if idx < len(elts) else elts[-1]  # 이종 튜플 — 그 원소의 자리\n        elif idx == -1 and len(elts) > 1:\n            pick = elts[0]  # dict 키 자리\n        else:\n            pick = elts[-1]  # 값/원소 자리\n        val = _unstring(pick)\n        return isinstance(val, ast.Name) and val.id == \"object\"\n    return False\n")
rep("    def judge(node: ast.AST, depth: int) -> \"tuple[bool, str, int]\":\n        p = parent.get(node)\n        if isinstance(p, ast.AnnAssign):\n            return (not _slot_is_object(p.annotation, depth, bindings), \"주석 변수\", p.lineno)\n",
    "    def judge(node: ast.AST, depth: int, idx: \"int | None\" = None) -> \"tuple[bool, str, int]\":\n        p = parent.get(node)\n        if isinstance(p, ast.AnnAssign):\n            return (not _slot_is_object(p.annotation, depth, bindings, idx), \"주석 변수\", p.lineno)\n")
rep("            return (not _slot_is_object(ann, depth, bindings), \"반환\", p.lineno)\n",
    "            return (not _slot_is_object(ann, depth, bindings, idx), \"반환\", p.lineno)\n")
rep("        if isinstance(p, (ast.Dict, ast.List, ast.Tuple, ast.Set)) and depth == 0:\n            cand, why, ln = judge(p, 1)\n",
    "        if isinstance(p, (ast.Dict, ast.List, ast.Tuple, ast.Set)) and depth == 0:\n            pos: \"int | None\" = None\n            if isinstance(p, ast.Tuple):\n                pos = next((i for i, e in enumerate(p.elts) if e is node), None)\n            elif isinstance(p, ast.Dict) and any(k is node for k in p.keys):\n                pos = -1  # dict 리터럴의 키 자리\n            cand, why, ln = judge(p, 1, pos)\n")
# N-4 · #650 메시지 이름 = origin
rep("                cands.add(\"#650\", f\"{rel}:{ln}\", f\"`json.{_name_of(node.func) or 'load'}(…)` 결과가 {why}로 흐른다\", JSON_Q)\n",
    "                fn_name = _dotted(node.func, origins).rsplit(\".\", 1)[-1] if isinstance(node.func, ast.Name) else _name_of(node.func)\n                cands.add(\"#650\", f\"{rel}:{ln}\", f\"`json.{fn_name}(…)` 결과가 {why}로 흐른다\", JSON_Q)\n")
# N-9 · 라벨 붙임(«… 주석의» · «… 반환 타입의»)
rep('f"{label} 의 " + RECORD_MSG.format(v="Any")', 'f"{label}의 " + RECORD_MSG.format(v="Any")')
rep('f"{label} 의 " + RECORD_MSG.format(v="object")', 'f"{label}의 " + RECORD_MSG.format(v="object")')
rep('f"{label} 의 `dict/Mapping[…, object]`"', 'f"{label}의 `dict/Mapping[…, object]`"')
rep('f"{label} 의 자리표시 `object`"', 'f"{label}의 자리표시 `object`"')
# C M1 · 루트 필터 의미 docstring
rep("  #646·#647·#650 은 `application/`·`framework/` 루트 안 파일만 본다(kkebi `web/`·`scripts/` 등 자매\n       플러그인·운영 스크립트 영역 제외 — 기존 5규칙의 대상은 무변).\n",
    "  #646·#647·#650 은 상대 경로 성분에 `application`/`framework` 가 있는 파일만 본다(어느 깊이든 — `src/application/**`\n       도 채택 신호와 같은 판 · kkebi `web/`·`scripts/` 등 자매 플러그인·운영 스크립트 영역 제외 — 기존 5규칙의 대상은 무변).\n")
P.write_text(t, encoding="utf-8"); print("check-public-surface-annotation.py: N-1/2/3/4/5/9 · M1")

# ── registry_gate N-6(a) · M4 ──────────────────────────────────────────────
G = pathlib.Path("dddjango/scripts/registry_gate.py"); u = G.read_text(encoding="utf-8")


def rg(old: str, new: str) -> None:
    global u
    assert u.count(old) == 1, old[:90]
    u = u.replace(old, new)


rg("    if candidates:\n        want_c: \"set[str]\" = set(candidates)\n",
   "    if candidates is not None:  # ⓓ 채널이 있을 때(N′∪L′≠∅)만 키를 둔다 — ⓓ 0 인 저장소는 payload byte 무변(P0′)\n        want_c: \"set[str]\" = set(candidates)\n")
rg("        _write_introduced(Path(ns.introduced_json), anchor_sha, attributed,\n                          n_records, cur_prefixes, provenance, cand_new)\n",
   "        _write_introduced(Path(ns.introduced_json), anchor_sha, attributed,\n                          n_records, cur_prefixes, provenance,\n                          cand_new if (n_cands or l_cands) else None)\n")
rg("    if n_cands or l_cands:\n        print(f\"\\n== ⓓ 신규(N′∖L′) {len(cand_new)}건 · legacy {cand_legacy}건 · 해소 {cand_resolved}건 — exit 불산입 · 감수자 입력은 신규분만(R-0284) ==\")\n        for line in cand_new:\n            print(f\"  {line}\")\n",
   "    if n_cands or l_cands:\n        print(f\"\\n== ⓓ 신규(N′∖L′) {len(cand_new)}건 · legacy {cand_legacy}건 · 해소 {cand_resolved}건 — exit 불산입 · 감수자 입력은 신규분만(R-0284) ==\")\n        for line in cand_new:\n            print(f\"  {line}\")\n        legacy_by: \"dict[str, int]\" = {}\n        for line in (n_cands & l_cands):\n            legacy_by[line.split(\" :: \", 1)[0]] = legacy_by.get(line.split(\" :: \", 1)[0], 0) + 1\n        for script in sorted(legacy_by):\n            print(f\"  legacy {script}: {legacy_by[script]}\")\n")
# docstring — 채널 목록에 ⓓ 앵커 차분 1항 + _write_introduced 키 설명
rg("- **귀속 0 ≠ 전체 clean** — legacy 잔존(L∩N)은 exit 에 안 들어가되 항상 보고한다\n",
   "- **귀속 0 ≠ 전체 clean** — legacy 잔존(L∩N)은 exit 에 안 들어가되 항상 보고한다\n- **ⓓ 앵커 차분 채널**(2026-09-04 현장 보고 3 ⓔ2): `[ⓓ#N]` 후보 라인도 같은 정규화로 앵커 L′·현재 N′ 를 갈라\n  «ⓓ 신규(N′∖L′)» 절(+검사기별 legacy 계수)에 인쇄하고 sidecar 에 `candidate_lines`·`candidate_records` 로\n  싣는다 — exit 불산입 · `records`(위반)와 분리 · ⓓ 가 하나도 없는 저장소는 출력·sidecar byte 무변.\n")
rg("    필드의 순수 함수다(출력 계약 v2).\n\n    **sink 격리(T2-3)**", "    필드의 순수 함수다(출력 계약 v2). 반환 4번째 = 정규화 ⓓ 후보 라인 집합(N′/L′ 재료).\n\n    **sink 격리(T2-3)**") if "필드의 순수 함수다(출력 계약 v2).\n\n    **sink 격리(T2-3)**" in u else None
rg("    매칭은 `findings.line_of_record` 로 레코드를 라인으로 되돌린 뒤 게이트와 **같은\n    정규화**를 적용해 키를 맞춘다.",
   "    매칭은 `findings.line_of_record` 로 레코드를 라인으로 되돌린 뒤 게이트와 **같은\n    정규화**를 적용해 키를 맞춘다. `candidates`(ⓓ 신규 라인 · N′∪L′≠∅ 일 때만 list)가 오면\n    `candidate_lines`·`candidate_records`(severity info · 신규분만) 를 `records` 와 분리해 싣는다.")
G.write_text(u, encoding="utf-8"); print("registry_gate.py: N-6(a) · M4 · docstring")

# ── smoke N-7 ─────────────────────────────────────────────────────────────
Sm = pathlib.Path("workspace/tools/registry_gate_smoke.py"); v = Sm.read_text(encoding="utf-8")
old = ("            and payload_q.get(\"candidate_lines\") and all(\"fresh_probe\" in l for l in payload_q[\"candidate_lines\"])\n"
       "            and not any(\"fresh_probe\" in str(r.get(\"file\", \"\")) for r in payload_q.get(\"records\", []))  # records 와 분리\n"
       "        )\n"
       "        rows.append((\"Q ⓓ 앵커 차분\", 0, code, q_ok, \"ⓓ 신규 1·legacy 1 · sidecar 분리 키 · exit 무변\"))\n"
       "        # Q′ — 같은 재료에 위반을 함께 심으면 exit 2(ⓓ 절은 그대로).\n"
       "        _plant_violation(repo)\n"
       "        code, out = _gate(repo, anchor)\n"
       "        rows.append((\"Q′ ⓓ + 위반 동반\", 2, code, \"== ⓓ 신규(N′∖L′) 1건\" in out and \"schema_smoke\" in out, \"ⓓ 절 유지 · 위반은 귀속\"))\n")
new = ("            and payload_q.get(\"candidate_lines\") and all(\"fresh_probe\" in l for l in payload_q[\"candidate_lines\"])\n"
       "            and payload_q.get(\"candidate_records\")\n"
       "            and all(r.get(\"severity\") == \"info\" and r.get(\"rule\") == \"#69\" and str(r.get(\"file\", \"\")).endswith(\"fresh_probe.py\")\n"
       "                    for r in payload_q[\"candidate_records\"])\n"
       "            and payload_q.get(\"records\") == []  # ⓓ 는 records(위반)와 분리\n"
       "        )\n"
       "        rows.append((\"Q ⓓ 앵커 차분\", 0, code, q_ok, \"ⓓ 신규 1·legacy 1 · sidecar 분리 키(info #69 · records []) · exit 무변\"))\n"
       "        # Q′ — 같은 재료에 위반을 함께 심으면 exit 2(ⓓ 절은 그대로 · records 는 위반만 · candidate_lines 는 ⓓ 만).\n"
       "        _plant_violation(repo)\n"
       "        side_q2: Path = td / \"introduced_q2.json\"\n"
       "        code, out = _gate(repo, anchor, [\"--introduced-json\", str(side_q2)])\n"
       "        payload_q2: dict = json.loads(side_q2.read_text(encoding=\"utf-8\")) if side_q2.is_file() else {}\n"
       "        q2_ok: bool = (\n"
       "            \"== ⓓ 신규(N′∖L′) 1건\" in out and \"schema_smoke\" in out\n"
       "            and payload_q2.get(\"records\") and all(\"schema_smoke\" in str(r.get(\"file\", \"\")) for r in payload_q2[\"records\"])\n"
       "            and all(\"fresh_probe\" in l for l in payload_q2.get(\"candidate_lines\", []))\n"
       "        )\n"
       "        rows.append((\"Q′ ⓓ + 위반 동반\", 2, code, q2_ok, \"ⓓ 절 유지 · records 는 위반만 · candidate_lines 는 ⓓ 만\"))\n")
assert v.count(old) == 1; Sm.write_text(v.replace(old, new), encoding="utf-8"); print("registry_gate_smoke.py: N-7")
