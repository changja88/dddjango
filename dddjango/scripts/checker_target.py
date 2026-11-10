"""검사기 TARGET 호출 계약 — «BC 폴더 모양» 대상 거절 (라운드 1 P2 · 2026-08-12).

검사기 27종의 TARGET 은 «저장소 루트»다(application/ 의 부모). BC 폴더나
application/ 컨테이너 자체를 주면 그 밑에서 application/ 컨테이너를 못 찾아
«표준 미채택 clean(exit 0)»으로 조용히 통과한다 — 라운드 1 실측: 파이프라인이
`check-layer-skeleton.py application/child_settings` 호출로 V1 트리를 전부
green 처리했다. 조용 통과 대신 소리내어 거절한다(#74 「조용한 무동작 금지」와
같은 정신 — 행동 고정은 fixture_matrix «호출 계약 레인» 27케이스가 진다).

여기에 «인터프리터 하한 게이트»(2026-08-14 S2 F-A)도 산다: 대상 저장소가
`pyproject.toml` 로 `requires-python >=X.Y` 를 선언했는데 검사기가 그보다 낮은
인터프리터로 돌면, 검사기의 `_parse`(SyntaxError→None) fail-open 이 3.12+ 문법
파일을 «침묵 clean» 처리한다 — 라운드 3 실측: python3.9 실행이 controller 를
통째로 스킵해 #210 발화 0 오판 2건(라운드 2 waiver 사문 판정·라운드 3 대리 답변
근거)을 만들었다. 27종 전부가 이 모듈을 거치므로 여기 한 곳이 직접 실행
채널까지 봉인한다. fixture 는 pyproject 가 없어 게이트 무발화(판정 무변).

이 모듈은 수기 소유다(standard_tree.py 는 tree_mirror_check --write 가 전체
재생성하는 기계 사본이라 여기 두지 않는다).
"""
from __future__ import annotations

import ast
import re
import stat
import sys
import fnmatch
from pathlib import Path
from types import MappingProxyType
from typing import Iterator, Mapping, NamedTuple, Optional

_BC_LAYER_DIRS: "tuple[str, ...]" = ("domain_layer", "application_layer", "driving_layer", "driven_layer")


def cache_only_instance(path: Path) -> bool:
    """실파일 없이 __pycache__ 아래 캐시만 남은 선택 인스턴스인가.

    빈 디렉터리는 허용하지만 캐시 파일 하나는 필요하다. 링크·읽기 불능은
    제외 근거가 아니므로 False로 남긴다. Git 추적 상태는 사용하지 않는다.
    """
    found = False
    pending = [(path, False)]
    try:
        while pending:
            current, in_cache = pending.pop()
            mode = current.lstat().st_mode
            if stat.S_ISLNK(mode):
                return False
            if stat.S_ISDIR(mode):
                cached = in_cache or current.name == "__pycache__"
                pending.extend((child, cached) for child in current.iterdir())
            elif stat.S_ISREG(mode) and in_cache and current.suffix in (".pyc", ".pyo"):
                with current.open("rb") as stream:
                    stream.read(1)
                found = True
            else:
                return False
    except OSError:
        return False
    return found


def skeleton_placeholder(path: Path) -> bool:
    """빈 골격 파일인가 — docstring 밖 문장이 0개(0바이트·공백·주석-only·docstring-only).

    표준 트리가 자리만 요구해 만들어 둔 파일은 aggregate·구현 의무의 대상이 아니다
    (판정 ④ 2026-08-25 — #256·#351 이 이 술어로 건너뛴다). 의미는 #114 렌더 계약의
    `_skeleton_placeholder_module`(check-error-centralization — 그쪽은 root 상대 경로
    서명이라 별도 실체)과 같다. `pass` 등 문장이 실재하거나 읽기·파싱 불능이면
    placeholder 가 아니다(fail-closed — 기존 진단 유지).
    """
    try:
        body = ast.parse(path.read_text(encoding="utf-8")).body
    except (OSError, UnicodeError, SyntaxError, ValueError):
        return False
    return not body or (
        len(body) == 1
        and isinstance(body[0], ast.Expr)
        and isinstance(body[0].value, ast.Constant)
        and isinstance(body[0].value.value, str)
    )


def _interpreter_gap_reason(root: Path) -> "str | None":
    """대상의 `requires-python` 하한을 현 인터프리터가 못 미치면 사용 오류 «사유»."""
    py = root / "pyproject.toml"
    if not py.is_file():
        return None
    try:
        text = py.read_text(encoding="utf-8")
    except OSError:
        return None
    m = re.search(r'requires-python\s*=\s*"[^"]*>=\s*(\d+)\.(\d+)', text)
    if m is None:
        return None
    lo = (int(m.group(1)), int(m.group(2)))
    if sys.version_info[:2] >= lo:
        return None
    cur = f"{sys.version_info[0]}.{sys.version_info[1]}"
    return (
        f"대상은 python >={lo[0]}.{lo[1]} 선언(pyproject.toml)인데 이 인터프리터는 {cur} 다 — "
        "AST 파싱 실패 파일이 침묵 스킵(fail-open)돼 거짓 clean 이 된다. "
        "대상 저장소의 .venv 인터프리터로 재실행하라"
    )


def bc_shaped_target_reason(target: "Path | str") -> "str | None":
    """TARGET 이 BC 폴더·application/ 컨테이너 모양이면 사용 오류 «사유»를 돌려준다.

    판정 + 대상 pyproject 1파일 읽기(인터프리터 하한 게이트)만 한다 — 호출자가
    자기 사용 오류 경로(print+return 1 또는 UsageError)로 보낸다. 존재하지 않거나
    디렉터리가 아닌 TARGET 은 각 검사기의 기존 오류 경로 몫이라 None 을 돌려준다.
    """
    p = Path(target)
    if not p.is_dir():
        return None
    # 위반 레코드 sink 의 «대상 저장소» 등록(T2-2) — 27종이 전부 이 모듈을 거치므로
    # 여기 한 곳이 설치본 기본 경로(`<root>/.dddjango/violations/`)를 봉인한다.
    try:
        import findings

        findings.set_target(p)
    except Exception:  # 레코드 채널은 «추가» 채널 — 등록 실패가 검사를 죽이지 않는다
        pass
    if (p / "application").is_dir():
        return _interpreter_gap_reason(p)  # 루트 모양 — 호출 계약 정상·인터프리터 하한만 확인
    layers = [n for n in _BC_LAYER_DIRS if (p / n).is_dir()]
    if layers:
        return (
            f"TARGET 이 BC 폴더로 보인다(층 폴더 직계: {', '.join(layers)}) — "
            "검사기의 대상은 저장소 루트다(application/ 의 부모)"
        )
    if p.name == "application" and any(
        child.is_dir() and any((child / n).is_dir() for n in _BC_LAYER_DIRS) for child in p.iterdir()
    ):
        return "TARGET 이 application/ 컨테이너 자체다 — 검사기의 대상은 저장소 루트다(application/ 의 부모)"
    return None

# ── 동명 폴더 승격(#490 교체형) 경로 해소 — 2026-09-01 ──────────────────────

ADAPTER_ROLES: tuple[str, ...] = ("adapter", "command", "constant", "contract", "schema")


def adapter_bundle(path: Path) -> bool:
    """BC의 세 어댑터 패키지 자리인가 — 내용이나 본체 파일 유무와 무관하다."""
    if not path.name.endswith("_adapter"):
        return False
    parent = path.parent
    if parent.parent.name in ("anticorruption_layer", "external_system"):
        parent = parent.parent
    return (parent.parent.name == "adapter"
            and parent.parent.parent.name == "driven_layer"
            and parent.name not in ("persistence", "anticorruption_layer", "external_system")) \
        or (parent.name in ("anticorruption_layer", "external_system")
            and parent.parent.name == "adapter"
            and parent.parent.parent.name == "driven_layer")


def adapter_component(path: Path) -> Path | None:
    """고정 역할 폴더의 직계 파일이면 바깥 어댑터 패키지를 반환한다."""
    bundle = path.parent.parent
    return bundle if path.parent.name in ADAPTER_ROLES and adapter_bundle(bundle) else None


def adapter_implementations(directory: Path) -> list[Path]:
    """한 상대·기술 폴더 아래 구현 파일을 찾는다. 구형 파일도 내용 진단은 유지한다."""
    out = slot_glob(directory, "*.py")
    if directory.is_dir():
        for bundle in sorted(directory.iterdir()):
            if bundle.is_dir() and adapter_bundle(bundle):
                out.extend(sorted((bundle / "adapter").glob("*.py")))
    return out

def slot_file(expected: "Path") -> "Path | None":
    """칸 경로 `<…>/<이름>.py` 의 실현 — 파일이면 그 파일, 유효 승격이면 본체, 없으면 None."""
    if expected.is_file():
        return expected
    name = expected.name
    if name.endswith(".py"):
        promo = expected.parent / name[:-3]
        body = promo / name
        if promo.is_dir() and body.is_file():
            return body
    return None


def slot_glob(directory: "Path", pattern: str) -> "list[Path]":
    """단층 glob 의 승격 인지판 — `pattern` 파일 + (이름+`.py` 가 pattern 인 폴더의) 승격 본체."""
    out: "list[Path]" = sorted(directory.glob(pattern))
    if directory.is_dir():
        for p in sorted(directory.iterdir()):
            if p.is_dir():
                body = p / (p.name + ".py")
                if body.is_file() and fnmatch.fnmatch(p.name + ".py", pattern):
                    out.append(body)
    return out


# ── 시험 경로 판별 — check-idempotency-scope-creep 에서 올림(2026-10-29) ─────────────

TEST_DIR_NAMES = {"test", "tests"}


def is_test_path(path: Path) -> bool:
    """시험 파일인가 — 경로 조각에 `test`·`tests` 가 있거나, 이름이 `test_` 로 시작하거나, `conftest.py`.

    부르는 쪽은 저장소 상대 경로를 넘긴다 — 절대 경로면 저장소 밖 조상 폴더 이름까지 세어
    `test/` 아래 놓인 사본이 통째로 시험으로 빠진다.
    """
    parts = path.parts
    return bool(set(parts) & TEST_DIR_NAMES) or path.name.startswith("test_") or path.name == "conftest.py"


# ── 예외 클래스 판별 — check-usecase-dto-placement 에서 올림(2026-11-10 · #210 면제 · #292 클래스) ──────

def exception_based(cls: "ast.ClassDef", declared: "Mapping[str, ast.ClassDef]", depth: int = 0) -> bool:
    """기반 사슬에 Exception/Error 가 닿는가 — 베이스가 `declared`(같은 모듈 맨 위 클래스)에 있으면 그 사슬을 따라가고
    (이름 끝은 보지 않는다 — `…Error` 이름의 같은 모듈 비예외 클래스를 상속한 것은 예외가 아니다), 없으면 베이스 이름이
    `Exception` 이거나 `Exception` · `Error` 로 끝날 때 참(다섯 단 넘으면 거짓).

    다른 모듈의 사용자 기반 클래스만 상속하고 그 이름이 `Exception` · `Error` 로 끝나지 않으면 놓친다.
    """
    if depth > 5:
        return False
    for base in cls.bases:
        name = base.attr if isinstance(base, ast.Attribute) else getattr(base, "id", "")
        if name in declared:
            if exception_based(declared[name], declared, depth + 1):
                return True
        elif name == "Exception" or name.endswith(("Exception", "Error")):
            return True
    return False


# ── 유스케이스 칸(트리 42행) 승격의 부품 — 역할 내 독립 흐름(②′) · 2026-10-29 ──────────
#
# 부품 종류는 선언 없이 가른다(houserules final §0 «②′ 승격의 부품»):
#   본체 = `<x>_use_case/<x>_use_case.py` · 틀 = `<x>_frame.py`(이름 고정이 곧 선언) ·
#   부품 클래스 = 본체 클래스 `__init__` 이 만들어 `self` 속성에 대입하는 형제 모듈 클래스 ·
#   흐름 부품(갈래 · 단계) = 틀이 아니면서 부품 클래스를 정의한 형제 · 잎 = 나머지 형제.
# 클래스 베이스(`ClassDef.bases`)는 판별 재료가 아니다.

_USE_CASE_SUFFIX = "_use_case"


def _use_case_promotion(expected: Path) -> "Path | None":
    """칸 경로 `<…>/<x>_use_case.py` 가 동명 폴더 승격으로 실현됐으면 본체 — 파일 실현이 이기는 `slot_file` 판독."""
    if expected.is_file() or not expected.name.endswith(_USE_CASE_SUFFIX + ".py"):
        return None
    return slot_file(expected)


def _folder_modules(folder: Path) -> "list[Path]":
    """승격 폴더 직계 `.py` 파일(이름 차례) — `__init__.py` · 숨김 파일 제외(`__pycache__` 는 폴더라 빠진다)."""
    return sorted(
        p for p in folder.iterdir()
        if p.suffix == ".py" and p.name != "__init__.py" and not p.name.startswith(".") and p.is_file()
    )


def _frame_file(body: Path) -> "Path | None":
    frame = body.parent / (body.stem[: -len(_USE_CASE_SUFFIX)] + "_frame.py")
    return frame if frame.is_file() else None


def use_case_parts(expected: Path) -> "list[Path]":
    """유스케이스 칸 `<…>/<x>_use_case.py` 의 실현 파일 — 승격이면 본체 + 형제 부품.

    트리 42행 동명 폴더 승격(`<x>_use_case/` 안에 `<x>_use_case.py`)이면 본체를 맨 앞에 두고
    폴더 직계의 다른 `.py` 를 이름 차례로 잇는다(`__init__.py` · `__pycache__` 제외).
    그 밖에는 `slot_file` 과 같다 — 파일 실현이면 `[그 파일]`, 다른 칸의 승격이면 `[본체]`, 없으면 `[]`.
    """
    body = _use_case_promotion(expected)
    if body is None:
        found = slot_file(expected)
        return [] if found is None else [found]
    return [body] + [p for p in _folder_modules(body.parent) if p != body]


def use_case_frame(expected: Path) -> "Path | None":
    """유스케이스 칸 승격 폴더의 틀 부품 `<x>_frame.py` — 승격이 아니거나 틀 파일이 없으면 None."""
    body = _use_case_promotion(expected)
    return None if body is None else _frame_file(body)


class UseCasePartKinds(NamedTuple):
    """유스케이스 칸 승격 폴더의 부품 종류 — `use_case_part_kinds` 의 결과(읽기 전용)."""

    body: Path  # 본체 `<x>_use_case.py`
    body_class: Optional[str]  # 본체 클래스 — 맨 위 공개 클래스 중 `execute` 를 정의한 첫 것(없으면 공개 클래스가 하나일 때 그것)
    part_attrs: Mapping[str, tuple[str, Path]]  # 부품 속성 이름 → (부품 클래스 이름, 정의 모듈) · 소스 차례 · 같은 속성은 처음 것
    part_classes: Mapping[str, Path]  # 부품 클래스 이름 → 정의 모듈(틀 클래스 포함)
    frame: Optional[Path]  # 틀 `<x>_frame.py`
    flow_parts: frozenset[Path]  # 부품 클래스를 정의한 형제 가운데 틀이 아닌 것(갈래 · 단계)
    leaves: frozenset[Path]  # 나머지 형제(본체 · 틀 · 흐름 부품 · `__init__.py` 밖)
    is_split: bool  # ②′ 폴더 — 틀 파일이 있거나 흐름 부품이 하나 이상


def _parse_module(path: Path) -> "ast.Module | None":
    try:
        return ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, SyntaxError, ValueError):
        return None


def _folder_package(dotted: str, folder: Path) -> bool:
    """점 경로 `dotted` 가 폴더 `folder` 자신의 패키지 경로인가 — 점 경로가 폴더 경로의 꼬리다."""
    package = tuple(dotted.split("."))
    tail = folder.absolute().parts
    return len(package) <= len(tail) and tail[-len(package):] == package


def _sibling_stem(node: ast.ImportFrom, folder: Path) -> "str | None":
    """`from .<모듈> import …` 또는 형제의 절대 경로(`<…>.<폴더>.<모듈>` — 점 경로 앞부분이 폴더 경로 꼬리)의 `<모듈>`."""
    if node.module is None:
        return None
    if node.level == 1:
        return None if "." in node.module else node.module
    if node.level != 0:
        return None
    head, _, stem = node.module.rpartition(".")
    if not head:
        return None
    return stem if _folder_package(head, folder) else None


def sibling_stem(node: ast.ImportFrom, folder: Path) -> "str | None":
    """`from <형제 모듈> import <이름>` 의 형제 모듈 `<모듈>` — 부품 종류 판별(`use_case_part_kinds`)과 같은 풀이.

    `from .<모듈> import …` · `from <…>.<폴더>.<모듈> import …`. 그 밖은 None 이다.
    """
    return _sibling_stem(node, folder)


def sibling_module_imports(node: ast.AST, folder: Path) -> "list[str]":
    """모듈 자체를 이름으로 들이는 import 가 가리키는 폴더 안 `<모듈>` — 형제 파일인지는 부르는 쪽이 본다.

    `from . import <모듈>` · `from <…>.<폴더> import <모듈>` · `import <…>.<폴더>.<모듈>`.
    `sibling_stem` 이 푸는 꼴(`from <모듈> import <이름>`)과 다른 꼴은 빈 목록이다.
    """
    if isinstance(node, ast.ImportFrom):
        if _sibling_stem(node, folder) is not None:
            return []
        package = (node.level == 1 and node.module is None) or (
            node.level == 0 and node.module is not None and _folder_package(node.module, folder))
        return [a.name for a in node.names if a.name != "*"] if package else []
    if isinstance(node, ast.Import):
        out: "list[str]" = []
        for alias in node.names:
            head, _, stem = alias.name.rpartition(".")
            if head and _folder_package(head, folder):
                out.append(stem)
        return out
    return []


def _sibling_imports(mod: ast.Module, folder: Path, siblings: "dict[str, Path]") -> "dict[str, tuple[str, Path]]":
    """본체 모듈 안(어디서든)에서 형제 모듈에서 가져온 이름 — 지역 이름 → (원래 이름, 형제 모듈)."""
    out: "dict[str, tuple[str, Path]]" = {}
    for node in ast.walk(mod):
        if not isinstance(node, ast.ImportFrom):
            continue
        stem = _sibling_stem(node, folder)
        sibling = siblings.get(stem) if stem is not None else None
        if sibling is None:
            continue
        for alias in node.names:
            if alias.name != "*":
                out[alias.asname or alias.name] = (alias.name, sibling)
    return out


def _body_class(mod: ast.Module) -> "ast.ClassDef | None":
    publics = [n for n in mod.body if isinstance(n, ast.ClassDef) and not n.name.startswith("_")]
    for cls in publics:
        if any(isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == "execute" for n in cls.body):
            return cls
    return publics[0] if len(publics) == 1 else None


def _own_scope(node: ast.AST) -> "Iterator[ast.AST]":
    """함수 몸의 노드(소스 차례) — 안쪽 함수 · lambda · 클래스의 몸에는 들어가지 않는다."""
    for child in ast.iter_child_nodes(node):
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)):
            continue
        yield child
        yield from _own_scope(child)


def _init_constructions(cls: ast.ClassDef) -> "list[tuple[str, str]]":
    """`__init__` 의 `self.<속성> = C(…)` · `self.<속성>: T = C(…)` — (속성, `C` 지역 이름) 소스 차례."""
    init = next((n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == "__init__"), None)
    if init is None or not init.args.args:
        return []
    me = init.args.args[0].arg
    out: "list[tuple[str, str]]" = []
    for node in _own_scope(init):
        if isinstance(node, ast.Assign):
            targets, value = node.targets, node.value
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            targets, value = [node.target], node.value
        else:
            continue
        if not (isinstance(value, ast.Call) and isinstance(value.func, ast.Name)):
            continue
        for tg in targets:
            if isinstance(tg, ast.Attribute) and isinstance(tg.value, ast.Name) and tg.value.id == me:
                out.append((tg.attr, value.func.id))
    return out


def use_case_part_kinds(folder: Path) -> "UseCasePartKinds | None":
    """유스케이스 칸 승격 폴더 `<x>_use_case/` 의 부품 종류 판별 — skeleton · transaction-boundary ·
    usecase-dto · domain-model 이 함께 쓰는 한곳.

    부품 클래스 = 본체 클래스 `__init__` 이 `self.<속성> = C(…)` 또는 `self.<속성>: T = C(…)` 로
    만들어 대입하는 `C` 가운데, 형제 모듈(`from .<모듈> import C` · 그 형제의 절대 경로)에서
    가져왔고 그 모듈 맨 위에 클래스로 정의된 것. 형제 함수 호출 · 실행마다 만드는 지역 객체는
    부품 클래스가 아니다(그 모듈은 잎이다).
    승격 폴더가 아니면(이름이 `_use_case` 로 끝나지 않거나 본체 `<x>_use_case.py` 없음) None,
    본체나 부품 클래스를 가져온 형제가 파싱되지 않으면 None 이다(fail-open — 부르는 쪽은
    ②′ 판정을 건너뛴다).
    """
    body = folder / (folder.name + ".py")
    if not folder.name.endswith(_USE_CASE_SUFFIX) or not body.is_file():
        return None
    mod = _parse_module(body)
    if mod is None:
        return None
    siblings = [p for p in _folder_modules(folder) if p != body]
    imported = _sibling_imports(mod, folder, {p.stem: p for p in siblings})
    cls = _body_class(mod)
    constructions = _init_constructions(cls) if cls is not None else []
    part_attrs: "dict[str, tuple[str, Path]]" = {}
    part_classes: "dict[str, Path]" = {}
    classes_of: "dict[Path, set[str]]" = {}
    for attr, local in constructions:
        hit = imported.get(local)
        if hit is None:
            continue
        name, module = hit
        if module not in classes_of:
            sibling_mod = _parse_module(module)
            if sibling_mod is None:
                return None
            classes_of[module] = {n.name for n in sibling_mod.body if isinstance(n, ast.ClassDef)}
        if name not in classes_of[module]:
            continue
        part_attrs.setdefault(attr, (name, module))
        part_classes.setdefault(name, module)
    frame = _frame_file(body)
    flow_parts = frozenset(m for m in part_classes.values() if m != frame)
    return UseCasePartKinds(
        body=body,
        body_class=cls.name if cls is not None else None,
        part_attrs=MappingProxyType(part_attrs),
        part_classes=MappingProxyType(part_classes),
        frame=frame,
        flow_parts=flow_parts,
        leaves=frozenset(p for p in siblings if p != frame and p not in flow_parts),
        is_split=frame is not None or bool(flow_parts),
    )


# ── OHS 창구의 사건 값 옮기기 — #474(check-api-error-controller-contract) · #153(check-context-isolation) 공용 · F4-105 ──
# 승인 표면은 G1 의 exception-map 값 칸과 published 예외의 선언 필드다 — 프로필과 무관하다(check-context-isolation 은 프로필을 안 쓴다).

OHS_EVENT_VALUE_FORM_NOTE: str = (
    " (승인한 사건 값을 옮기는 꼴만 비켜 준다: 잡은 구체 예외 하나 · 양쪽 클래스에 직접 선언된 `str` / `str | None` 필드 · "
    "본문은 `raise 공개예외(kw=n.f) [from None]` 한 문장)"
)


def _module_import_origins(mod: ast.Module) -> "dict[str, str]":
    """모듈 맨 위 `from <절대 경로> import <이름>` 의 지역 이름 → 원 경로 — 모듈 수준에서 다시 묶이는 이름은 뺀다."""
    origins: "dict[str, str]" = {}
    rebound: "set[str]" = set()
    for node in mod.body:
        if isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            for alias in node.names:
                local = alias.asname or alias.name
                if local in origins:
                    rebound.add(local)
                origins[local] = f"{node.module}.{alias.name}"
        elif isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            rebound.add(node.name)
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            rebound.update(t.id for t in targets if isinstance(t, ast.Name))
    return {name: origin for name, origin in origins.items() if name not in rebound}


def _is_str_annotation(node: ast.AST) -> bool:
    """주석이 `str` 또는 `str | None` 인가."""
    def is_str(part: ast.AST) -> bool:
        return isinstance(part, ast.Name) and part.id == "str"

    def is_none(part: ast.AST) -> bool:
        return isinstance(part, ast.Constant) and part.value is None

    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
        return (is_str(node.left) and is_none(node.right)) or (is_none(node.left) and is_str(node.right))
    return is_str(node)


def _exception_str_fields(root: Path, origin: str) -> "frozenset[str] | None":
    """예외 클래스(그 모듈에 바로 정의 — 재수출 · 상속 밖)의 공개 `str` · `str | None` 필드. 모듈 · 클래스를 못 읽으면 None."""
    module, _, class_name = origin.rpartition(".")
    base = root.joinpath(*module.split("."))
    mod = _parse_module(base.with_suffix(".py")) or _parse_module(base / "__init__.py")
    classes = [n for n in mod.body if isinstance(n, ast.ClassDef) and n.name == class_name] if mod is not None else []
    if len(classes) != 1:
        return None
    declared: "dict[str, bool]" = {}

    def declare(name: str, annotation: ast.AST) -> None:
        if not name.startswith("_"):
            declared[name] = declared.get(name, True) and _is_str_annotation(annotation)

    for statement in classes[0].body:
        if isinstance(statement, ast.AnnAssign) and isinstance(statement.target, ast.Name):
            declare(statement.target.id, statement.annotation)
        elif isinstance(statement, ast.FunctionDef) and statement.name == "__init__" and statement.args.args:
            receiver = statement.args.args[0].arg
            for node in _own_scope(statement):
                if (isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Attribute)
                        and isinstance(node.target.value, ast.Name) and node.target.value.id == receiver):
                    declare(node.target.attr, node.annotation)
    return frozenset(name for name, is_str in declared.items() if is_str)


def _own_domain_exception(origin: str, own_bc: str) -> bool:
    parts = origin.split(".")
    return len(parts) >= 4 and parts[:2] == ["application", own_bc] and parts[2] == "domain_layer"


def _own_published_exception(origin: str, own_bc: str) -> bool:
    parts = origin.split(".")
    return parts[:4] == ["application", own_bc, "driving_layer", "open_host_service"] \
        and parts[5:7] == ["contract", "exception"] and len(parts) >= 8


def ohs_event_value_handler(handler: ast.ExceptHandler, mod: ast.Module, root: Path, own_bc: str) -> bool:
    """OHS catch 가 승인된 사건 값을 published 예외로 옮기는 꼴인가 — 이 꼴만 #474 · #153 을 비켜 간다.

    `except <자기 BC domain_layer 예외 하나> as n:` 의 본문이 `raise <자기 BC contract/exception 클래스>(kw=n.f, …) [from None]`
    한 문장이고, 인자는 모두 keyword 이며 `n.f` 꼴이고, `f` 가 잡은 예외의 공개 필드 · `kw` 가 published 클래스의
    선언 필드(`str` · `str | None`)일 때만이다. `str(n)` · 통째 쓰기 · `from n` · 다른 문장이 끼면 그대로 위반이다."""
    if handler.name is None or not isinstance(handler.type, ast.Name) or len(handler.body) != 1:
        return False
    raised = handler.body[0]
    if not isinstance(raised, ast.Raise) or not isinstance(raised.exc, ast.Call) or not isinstance(raised.exc.func, ast.Name):
        return False
    if raised.cause is not None and not (isinstance(raised.cause, ast.Constant) and raised.cause.value is None):
        return False
    call = raised.exc
    if call.args or not call.keywords:
        return False
    origins = _module_import_origins(mod)
    caught = origins.get(handler.type.id)
    published = origins.get(call.func.id)
    if caught is None or published is None or not _own_domain_exception(caught, own_bc) \
            or not _own_published_exception(published, own_bc):
        return False
    caught_fields = _exception_str_fields(root, caught)
    published_fields = _exception_str_fields(root, published)
    if caught_fields is None or published_fields is None:
        return False
    for keyword in call.keywords:
        value = keyword.value
        if (keyword.arg not in published_fields
                or not (isinstance(value, ast.Attribute) and isinstance(value.value, ast.Name)
                        and value.value.id == handler.name and value.attr in caught_fields)):
            return False
    return True
