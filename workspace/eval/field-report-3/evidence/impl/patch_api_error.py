"""④-2 조각 2 — check-api-error-controller-contract.py #648/#649(프로필 무관 트리 슬라이스) + check-openapi-error-declaration.py stale 문면.
실행: cd /Users/hyun/Desktop/dddjango && python3 <this>
"""
import pathlib

P = pathlib.Path("dddjango/scripts/check-api-error-controller-contract.py")
t = P.read_text(encoding="utf-8")
assert "#648" not in t, "이미 패치됨"


def rep(old: str, new: str, count: int = 1) -> None:
    global t
    assert t.count(old) == count, (t.count(old), old[:80])
    t = t.replace(old, new)


# 1. docstring — 트리 슬라이스 규칙 2 추가
rep(
    "tree↔code 동일 사건 이중 방출은 tree 사이트 선점 억제로 막는다(귀속 매핑표 v2\noverlap 절 — #62·#474 는 handler 행, ⓓ#125 는 route 함수 def 행 좌표).\n",
    "tree↔code 동일 사건 이중 방출은 tree 사이트 선점 억제로 막는다(귀속 매핑표 v2\noverlap 절 — #62·#474 는 handler 행, ⓓ#125 는 route 함수 def 행 좌표).\n"
    "표준 트리 슬라이스(모든 프로필 · `_slice_check_controller_ast`)의 코드 형상 규칙 2(09-04 현장 보고 3 S-5):\n"
    "  #648 반환 주석의 `ninja.Status` 상자는 하나 — union(`|`·`Optional`·`Union`·문자열 주석)을 평탄화한 구성원 중\n"
    "       `Status[…]`(origin = `ninja.Status`/`ninja.responses.Status` · 모듈 수준 import 바인딩으로 해소)가 2개\n"
    "       이상이면 위반(`-> Status[Out | Err]` 또는 `-> Out | Status[Err]` 로). `Status[T]` 는 불변이라 상자 둘은\n"
    "       concrete 직접 반환에서 mypy strict red 이고, 값 변수를 base 로 주석해 통과시킨 형태도 같은 금지(형태 금지).\n"
    "  #649 클래스가 ninja `Schema`(origin `ninja.Schema`/`ninja.schema.Schema`)와 pydantic `RootModel`\n"
    "       (`pydantic.RootModel`/`pydantic.root_model.RootModel`)을 함께 상속하면 위반(메타클래스 충돌 —\n"
    "       성공 union 응답은 `RootModel[Annotated[A | B, Field(discriminator=…)]]` 단독 상속). 파일 한정 없음.\n"
    "  둘 다 api/** 전 파일 + OHS `*_service.py`(트리 슬라이스 대상)에서 돌고 overlap 억제 비대상(keys None).\n",
)

# 2. 상수 + origin 워커 + 판정 함수 — `_deco_route_name` 앞
rep(
    "def _deco_route_name(deco: _ast.expr) -> str | None:\n",
    "_STATUS_ORIGINS = {\"ninja.Status\", \"ninja.responses.Status\"}\n"
    "_SCHEMA_ORIGINS = {\"ninja.Schema\", \"ninja.schema.Schema\"}\n"
    "_ROOTMODEL_ORIGINS = {\"pydantic.RootModel\", \"pydantic.root_model.RootModel\"}\n"
    "\n"
    "\n"
    "def _tree_origins(mod: _ast.Module) -> dict[str, str]:\n"
    "    \"\"\"모듈 수준 import 바인딩 — 로컬 이름 → dotted origin(if/try 하위 포함 · 뒤 정의 우선 · 함수·클래스 본문 안 import 는 무시).\"\"\"\n"
    "    origins: dict[str, str] = {}\n"
    "\n"
    "    def walk(stmts: \"list[_ast.stmt]\") -> None:\n"
    "        for st in stmts:\n"
    "            if isinstance(st, _ast.ImportFrom) and st.level == 0 and st.module:\n"
    "                for a in st.names:\n"
    "                    origins[a.asname or a.name] = f\"{st.module}.{a.name}\"\n"
    "            elif isinstance(st, _ast.Import):\n"
    "                for a in st.names:\n"
    "                    origins[a.asname or a.name.split(\".\")[0]] = a.name if a.asname else a.name.split(\".\")[0]\n"
    "            elif isinstance(st, (_ast.ClassDef, _ast.FunctionDef, _ast.AsyncFunctionDef)):\n"
    "                origins.pop(st.name, None)\n"
    "            elif isinstance(st, _ast.If):\n"
    "                walk(st.body)\n"
    "                walk(st.orelse)\n"
    "            elif isinstance(st, _ast.Try):\n"
    "                walk(st.body)\n"
    "                for h in st.handlers:\n"
    "                    walk(h.body)\n"
    "                walk(st.orelse)\n"
    "                walk(st.finalbody)\n"
    "\n"
    "    walk(mod.body)\n"
    "    return origins\n"
    "\n"
    "\n"
    "def _tree_dotted(node: _ast.AST, origins: dict[str, str]) -> str:\n"
    "    if isinstance(node, _ast.Name):\n"
    "        return origins.get(node.id, node.id)\n"
    "    if isinstance(node, _ast.Attribute):\n"
    "        head = _tree_dotted(node.value, origins)\n"
    "        return f\"{head}.{node.attr}\" if head else node.attr\n"
    "    return \"\"\n"
    "\n"
    "\n"
    "def _tree_unstring(node: _ast.AST) -> _ast.AST:\n"
    "    if isinstance(node, _ast.Constant) and isinstance(node.value, str):\n"
    "        try:\n"
    "            return _ast.parse(node.value, mode=\"eval\").body\n"
    "        except SyntaxError:\n"
    "            return node\n"
    "    return node\n"
    "\n"
    "\n"
    "def _tree_union_members(node: _ast.AST) -> \"list[_ast.AST]\":\n"
    "    \"\"\"`X | Y` · `Optional[X]` · `Union[X, Y]` 평탄화(문자열 주석 재파싱) — 합집합이 아니면 [node].\"\"\"\n"
    "    node = _tree_unstring(node)\n"
    "    if isinstance(node, _ast.BinOp) and isinstance(node.op, _ast.BitOr):\n"
    "        return _tree_union_members(node.left) + _tree_union_members(node.right)\n"
    "    if isinstance(node, _ast.Subscript):\n"
    "        head = node.value.attr if isinstance(node.value, _ast.Attribute) else getattr(node.value, \"id\", \"\")\n"
    "        if head in (\"Optional\", \"Union\"):\n"
    "            elts = list(node.slice.elts) if isinstance(node.slice, _ast.Tuple) else [node.slice]\n"
    "            out: \"list[_ast.AST]\" = []\n"
    "            for e in elts:\n"
    "                out.extend(_tree_union_members(e))\n"
    "            return out\n"
    "    return [node]\n"
    "\n"
    "\n"
    "def _status_box_count(returns: \"_ast.AST | None\", origins: dict[str, str]) -> int:\n"
    "    \"\"\"#648 — 반환 주석 union 구성원 중 `Status[…]` 상자 수.\"\"\"\n"
    "    if returns is None:\n"
    "        return 0\n"
    "    return sum(\n"
    "        1 for m in _tree_union_members(returns)\n"
    "        if isinstance(m, _ast.Subscript) and _tree_dotted(m.value, origins) in _STATUS_ORIGINS\n"
    "    )\n"
    "\n"
    "\n"
    "def _schema_rootmodel_mix(cls: _ast.ClassDef, origins: dict[str, str]) -> bool:\n"
    "    \"\"\"#649 — ninja `Schema` 와 pydantic `RootModel` 동시 상속.\"\"\"\n"
    "    bases = {_tree_dotted(b.value if isinstance(b, _ast.Subscript) else b, origins) for b in cls.bases}\n"
    "    return bool(bases & _SCHEMA_ORIGINS) and bool(bases & _ROOTMODEL_ORIGINS)\n"
    "\n"
    "\n"
    "def _deco_route_name(deco: _ast.expr) -> str | None:\n",
)

# 3. 트리 슬라이스 본문 — origins 계산 + #648 · #649 방출
rep(
    "    domain_names: set[str] = set()\n"
    "    for node in _ast.walk(mod):\n"
    "        if isinstance(node, _ast.ImportFrom) and node.level == 0 and node.module:\n"
    "            if \"domain_layer\" in node.module.split(\".\"):\n"
    "                domain_names.update(a.asname or a.name for a in node.names)\n"
    "    for node in _ast.walk(mod):\n"
    "        if isinstance(node, (_ast.FunctionDef, _ast.AsyncFunctionDef)):\n"
    "            routes = [d for d in node.decorator_list if _deco_route_name(d)]\n",
    "    domain_names: set[str] = set()\n"
    "    for node in _ast.walk(mod):\n"
    "        if isinstance(node, _ast.ImportFrom) and node.level == 0 and node.module:\n"
    "            if \"domain_layer\" in node.module.split(\".\"):\n"
    "                domain_names.update(a.asname or a.name for a in node.names)\n"
    "    origins: dict[str, str] = _tree_origins(mod)\n"
    "    for node in _ast.walk(mod):\n"
    "        if isinstance(node, _ast.ClassDef) and _schema_rootmodel_mix(node, origins):\n"
    "            msg = f\"`{node.name}` 이 ninja `Schema` 와 pydantic `RootModel` 을 함께 상속했다 — 메타클래스 충돌 · 성공 union 응답은 `RootModel[Annotated[A | B, Field(discriminator=…)]]` 단독 상속이다\"\n"
    "            findings.add(\"#649\", f\"{rel}:{node.lineno}\", msg)\n"
    "            finding_keys.append(None)\n"
    "    for node in _ast.walk(mod):\n"
    "        if isinstance(node, (_ast.FunctionDef, _ast.AsyncFunctionDef)):\n"
    "            boxes = _status_box_count(node.returns, origins)\n"
    "            if boxes >= 2:\n"
    "                msg = f\"`{node.name}()` 반환 주석에 `Status[…]` 상자가 {boxes}개 — 상자는 하나다(`-> Status[Out | Err]` 또는 `-> Out | Status[Err]`) · `Status[T]` 는 불변이라 concrete 직접 반환이 mypy strict 에서 막힌다\"\n"
    "                findings.add(\"#648\", f\"{rel}:{node.lineno}\", msg)\n"
    "                finding_keys.append(None)\n"
    "            routes = [d for d in node.decorator_list if _deco_route_name(d)]\n",
)
P.write_text(t, encoding="utf-8")
print("patched", P)

# ── openapi 검사기 stale 문면 2곳 ──────────────────────────────────────────
Q = pathlib.Path("dddjango/scripts/check-openapi-error-declaration.py")
u = Q.read_text(encoding="utf-8")
old1 = ("검사를 보존한다. ``dddjango-code-json`` profile은 선택된 operation이 직접 반환하는\n"
        "BC 오류와 ``response={status: <Bc>ErrorSchema}`` 선언의 일치를 검증하고, 선택 API\n"
        "module의 수동 OpenAPI 후처리를 차단한다.\n")
new1 = ("검사를 보존한다. ``dddjango-code-json`` profile은 선택된 operation이 직접 반환하는\n"
        "BC 오류와 그 status 에서 실제 반환하는 오류 타입 그대로(concrete·``Union``·명시값 base —\n"
        "base 뭉뚱그림 금지 · 2026-08-25)의 ``response=`` 선언의 일치를 검증하고, 선택 API\n"
        "module의 수동 OpenAPI 후처리를 차단한다.\n")
assert u.count(old1) == 1; u = u.replace(old1, new1)
old2 = "        \"  조치: 각 직접 반환 status를 같은 BC의 <Bc>ErrorSchema base로 선언하고, \"\n"
new2 = "        \"  조치: 각 직접 반환 status를 그 status에서 실제 반환하는 오류 타입 그대로(concrete·Union·명시값 base — base 뭉뚱그림 금지) 선언하고, \"\n"
assert u.count(old2) == 1; u = u.replace(old2, new2)
Q.write_text(u, encoding="utf-8")
print("patched", Q)
