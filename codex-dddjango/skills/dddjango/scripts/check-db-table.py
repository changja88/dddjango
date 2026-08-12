#!/usr/bin/env python3
"""dddjango `driven_layer/django_<bounded_context>/` 검사기 — 장고 앱 규율의 결정적 백스톱.

트리 75~88행(driven_layer)의 기계 몫 규칙 18개를 강제한다. 경로 기대는
`standard_tree.py` 에서 도출한다 — 이 파일에 트리 경로를 다시 적지 않는다.

무엇을 잡나 (규칙 번호는 트리 개정 명세):
  경로   #318 `driven_layer/` 자식 폴더는 `django_<bc>/`·`adapter/` 둘뿐
         #324/#467 층 이름 위장(`infra_layer`·`infrastructure_layer`·`driven_adapter`·
         `secondary_adapter`·`adapter_layer`) · #325 ORM 산출물은 `django_<bc>/` 안에만
         #334 `models` 는 파일이 아니라 패키지
  apps   #329 `label` 명시 · #330 label=BC 이름=폴더-`django_` · #331 label 중복 금지
         #332 `name` 은 전체 점 경로 · #535 `ready()` 본문 한 줄=event_wiring import
         #536 그 import 가 `ready()` 밖이면 위반 · #537 `ready()` 에서 DB 금지
         #538 모듈 최상단 import 는 django 뿐 · 리스너 정의 금지
  import #326 `django_<bc>/` 는 잎 — django 와 같은 폴더 안 말고 import 0
         (유일 면제: apps.py `ready()` 안의 event_wiring 한 줄 — #538)
  모델   #335 표 하나=파일 하나 · `_model.py` 접미 · #632 클래스명 `<Name>Model` 상시
         #630 신규 모델 `Meta.db_table` 존재 + 값 `<app_label>_<entity_snake>`
         #631 타 BC 모델을 FK·O2O·M2M 으로 참조 금지(문자열 참조 포함)

가드 계약 (명세 조각 ⓐ):
  - 대상 0건 가드(#74): 채택 신호는 있는데 검사할 앱이 0건이고 다른 발견도 없으면 exit 2.
  - fail-open 차단: `.git` 부재는 면제가 아니다 — 신규 식별이 불가하면 «전 모델을 신규로
    간주»하고 그 사실을 출력한다(#630 값 검사). 기존(추적된) 모델의 db_table 은 신규가
    아니므로 보지 않는다 — «기존 테이블명 보존(개명 강제 아님)»이 #630 문면이다.
  - 신규 모델 = 신규 파일: #335(표 하나=파일 하나)가 규약이라 모델 추가는 곧 파일 추가다 —
    porcelain 파일 단위(`??`/`A`) 판정이 규약과 동치다.

사용법: check-db-table.py [TARGET_DIR]   (기본: 현재 디렉터리)
종료코드: 0=clean(또는 표준 미채택) · 1=사용/분석 오류 · 2=blocker(발견 출력)
"""
from __future__ import annotations

import ast
import re
import subprocess
import sys

import checker_target
from pathlib import Path

try:
    import standard_tree as tree
except ImportError:  # 데이터 모듈 없이는 판정 불가 — fail-closed(분석 오류)
    print("분석 오류: standard_tree.py 를 찾지 못했다 — 검사기와 같은 폴더에 있어야 한다", file=sys.stderr)
    sys.exit(1)

SKIP_DIRS = {".venv", "venv", "site-packages", "node_modules", ".git", "__pycache__", ".dddjango"}
DJANGO_APP_MARKERS = ("models.py", "apps.py", "views.py", "admin.py")

DRIVEN = "driven_layer"
BANNED_LAYER_NAMES = {  # driven_layer 를 다르게 부르는 이름 — 규칙 번호 매핑
    "infra_layer": "#324", "infrastructure_layer": "#324",
    "driven_adapter": "#324", "secondary_adapter": "#324",
    "adapter_layer": "#467",
}
RELATION_FIELDS = {"ForeignKey", "OneToOneField", "ManyToManyField"}
MODEL_SUFFIX = "Model"
NON_MODEL_BASES = {"BaseModel"}  # pydantic 등 — ORM base 로 보지 않는다(거짓 양성 회피)

NEW_LAYERS = {"driving_layer", "application_layer", "domain_layer", "driven_layer"}
# 잎 규칙(#326)의 위반 마디 — 트리에서 도출한 저장소 내부 어휘. stdlib·서드파티는 판정 유보.
REPO_VOCAB = (
    {c.name.rstrip("/") for c in tree.children(tree.bc_root())}
    | {"application", "framework"}
)


class Findings(list):
    def add(self, rule: str, path: Path, msg: str) -> None:
        self.append(f"[{rule}] {path}: {msg}")


def _entries(d: Path) -> tuple[list[Path], list[Path]]:
    dirs: list[Path] = []
    files: list[Path] = []
    for p in sorted(d.iterdir()):
        if p.name.startswith(".") or p.name in SKIP_DIRS:
            continue
        (dirs if p.is_dir() else files).append(p)
    return dirs, files


def _has_adoption_signal(bc_dir: Path) -> bool:
    """채택 신호원 둘(#78) — check-layer-skeleton 과 같은 판."""
    has_layer = any((bc_dir / n).is_dir() for n in NEW_LAYERS)
    has_marker = any((bc_dir / m).is_file() for m in DJANGO_APP_MARKERS) or any(
        p.is_dir() and p.name.startswith("django_") for p in bc_dir.iterdir()
    )
    return has_layer or has_marker


def _snake(name: str) -> str:
    """CamelCase → snake_case. 연속 대문자(약어)는 한 마디로(`HTTPLog` → `http_log`)."""
    s = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)
    s = re.sub(r"([a-z\d])([A-Z])", r"\1_\2", s)
    return s.lower()


def _new_paths(root: Path) -> set[Path] | None:
    """git 신규(untracked `??`·staged `A`) 파일 절대경로 집합. None = git 저장소가 아니다."""
    if not (root / ".git").exists():
        return None
    try:
        res = subprocess.run(
            ["git", "-C", str(root), "status", "--porcelain", "-uall"],
            capture_output=True, text=True,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if res.returncode != 0:
        return None
    out: set[Path] = set()
    for line in res.stdout.splitlines():
        code, rest = line[:2], line[3:]
        if "?" not in code and "A" not in code:
            continue
        path = rest.strip().strip('"')
        if " -> " in path:
            path = path.split(" -> ")[-1]
        out.add((root / path).resolve())
    return out


# ── apps.py — #329~#332 · #535~#538 ─────────────────────────────────────────

def _is_event_wiring_import(node: ast.stmt) -> bool:
    if isinstance(node, ast.ImportFrom):
        mods = (node.module or "").split(".")
        return "event_wiring" in mods or any(a.name == "event_wiring" for a in node.names)
    if isinstance(node, ast.Import):
        return any("event_wiring" in a.name.split(".") for a in node.names)
    return False


def _str_assign(cls: ast.ClassDef, name: str) -> str | None:
    """클래스 본문의 `name = "리터럴"` 값. 없거나 비-리터럴이면 None."""
    for stmt in cls.body:
        targets: list[str] = []
        value: ast.expr | None = None
        if isinstance(stmt, ast.Assign):
            targets = [t.id for t in stmt.targets if isinstance(t, ast.Name)]
            value = stmt.value
        elif isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
            targets = [stmt.target.id]
            value = stmt.value
        if name in targets and isinstance(value, ast.Constant) and isinstance(value.value, str):
            return value.value
    return None


def _check_apps_py(app_dir: Path, bc_name: str, rel: Path, out: Findings) -> str | None:
    """apps.py 규칙 검사. 반환 = 명시된 label(#331 대조용 — 없으면 None)."""
    apps_py = app_dir / "apps.py"
    if not apps_py.is_file():
        return None  # 존재는 skeleton #488 소유 — 여기서 중복으로 내지 않는다
    try:
        mod = ast.parse(apps_py.read_text(encoding="utf-8"))
    except (SyntaxError, OSError, UnicodeDecodeError):
        out.add("분석", rel / "apps.py", "apps.py 를 파싱하지 못했다")
        return None

    config: ast.ClassDef | None = None
    for node in mod.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            if _is_event_wiring_import(node):
                out.add("#536", rel / "apps.py", "event_wiring import 가 `ready()` 밖에 있다 — 부팅 1단계에서는 모델을 못 읽는다")
            else:
                for p in _import_paths(node):
                    top = p.split(".")[0]
                    if top not in ("django", "__future__"):
                        out.add("#538", rel / "apps.py", f"모듈 최상단 import 는 django 것뿐이다 — `{p}`")
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            out.add("#538", rel / "apps.py", f"apps.py 에서 리스너·함수를 정의하면 위반이다 — `{node.name}`")
        elif isinstance(node, ast.ClassDef):
            base_names = {b.attr if isinstance(b, ast.Attribute) else getattr(b, "id", "") for b in node.bases}
            if any(n.endswith("AppConfig") for n in base_names):
                config = node
            else:
                out.add("#538", rel / "apps.py", f"apps.py 에는 AppConfig 만 산다 — `{node.name}`")

    if config is None:
        out.add("#329", rel / "apps.py", "AppConfig 클래스가 없다 — `label` 을 명시 선언할 자리가 없다")
        return None

    label = _str_assign(config, "label")
    if label is None:
        out.add("#329", rel / "apps.py", "`label` 을 명시 선언한다 — 기본값에 기대지 않는다")
    else:
        if label != bc_name:
            out.add("#330", rel / "apps.py", f"`label`(`{label}`)은 BC 이름(`{bc_name}`)과 같아야 한다")
        if app_dir.name != f"django_{label}":
            out.add("#330", rel / "apps.py", f"폴더 이름은 `django_` + label 이다 — `django_{label}` ≠ `{app_dir.name}`")

    name = _str_assign(config, "name")
    if name is None:
        out.add("#332", rel / "apps.py", "`name` 을 전체 점 경로로 적는다")
    elif "." not in name or name.split(".")[-1] != app_dir.name:
        out.add("#332", rel / "apps.py", f"`name`(`{name}`)은 이 앱까지의 전체 점 경로여야 한다")

    ready = next(
        (n for n in config.body if isinstance(n, ast.FunctionDef) and n.name == "ready"), None
    )
    if ready is not None:
        body = list(ready.body)
        if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant):
            body = body[1:]  # docstring 은 본문으로 세지 않는다
        one_line = len(body) == 1 and isinstance(body[0], (ast.Import, ast.ImportFrom)) and _is_event_wiring_import(body[0])
        if not one_line:
            out.add("#535", rel / "apps.py", "`ready()` 본문은 한 줄이다 — 자기 BC 의 `composition_root/event_wiring.py` 를 부른다")
        for sub in ast.walk(ready):
            if isinstance(sub, ast.Attribute) and sub.attr == "objects":
                out.add("#537", rel / "apps.py", "`ready()` 에서 DB 를 만지면 위반이다 — 테스트가 프로덕션 DB 에 질의하게 된다")
                break
    return label


# ── import 잎 규칙 — #326 ───────────────────────────────────────────────────

def _import_paths(node: ast.stmt) -> list[str]:
    if isinstance(node, ast.Import):
        return [a.name for a in node.names]
    if isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
        return [node.module]
    return []


def _leaf_violation(path_str: str, app_name: str) -> bool:
    """절대 import 가 저장소 안 다른 코드를 가리키는가. stdlib·서드파티는 판정 유보."""
    parts = path_str.split(".")
    if parts[0] in ("django", "__future__"):
        return False
    if app_name in parts:
        return False  # 절대 경로로 자기 앱 안을 가리킨다
    return any(p in REPO_VOCAB for p in parts) or any(p.startswith("django_") for p in parts)


def _vo_derivation_path(mod_path: str, bc: str) -> bool:
    """#326 예외(2026-08-12 D1′) — 자기 BC domain VO 모듈인가.

    `implementation-django` 코퍼스(:203·:215)가 「도메인 판정 값 집합은 domain StrEnum 에서
    파생」을 요구해 잎 규칙과 상충하던 것을, «값 파생 전용» 좁은 예외로 정렬했다.
    허용은 from-import + 나열·순회·멤버 참조까지 — 호출(판정·행위)은 여전히 위반이다."""
    parts: "list[str]" = mod_path.split(".")
    return (
        parts[:2] == ["application", bc]
        and "domain_layer" in parts
        and ("value_object" in parts or "shared_value_object" in parts)
    )


def _called_symbols(mod: ast.Module, names: "set[str]") -> "set[str]":
    """이름이 «호출»로 쓰였는가 — `Sym(...)` 또는 `Sym.method(...)`. 순회·comprehension·
    멤버 속성 참조(`m.value`)는 호출이 아니라 파생이라 잡지 않는다."""
    hit: "set[str]" = set()
    for node in ast.walk(mod):
        if not isinstance(node, ast.Call):
            continue
        fn = node.func
        if isinstance(fn, ast.Name) and fn.id in names:
            hit.add(fn.id)
        elif isinstance(fn, ast.Attribute) and isinstance(fn.value, ast.Name) and fn.value.id in names:
            hit.add(fn.value.id)
    return hit


def _check_leaf_imports(app_dir: Path, app_rel: Path, out: Findings) -> None:
    """#326 — `django_<bc>/` 는 잎. migrations/ 는 생성물이라, admin/** 은 #327 면제라 제외."""
    bc_name: str = app_dir.name[len("django_"):] if app_dir.name.startswith("django_") else app_dir.name
    for f in sorted(app_dir.rglob("*.py")):
        rel_in_app = f.relative_to(app_dir)
        if set(rel_in_app.parts) & SKIP_DIRS or rel_in_app.parts[0] in ("migrations", "admin"):
            continue
        try:
            mod = ast.parse(f.read_text(encoding="utf-8"))
        except (SyntaxError, OSError, UnicodeDecodeError):
            continue
        is_apps_py = rel_in_app.parts == ("apps.py",)
        vo_symbols: "dict[str, str]" = {}
        for node in ast.walk(mod):
            if not isinstance(node, (ast.Import, ast.ImportFrom)):
                continue
            if is_apps_py and _is_event_wiring_import(node):
                continue  # 유일 면제(#538 문면)는 ready() 안의 event_wiring 한 줄 —
                # ready() 밖이면 #536 이, 딴 줄이 늘면 #535 가 잡는다(자리 소유 분리)
            if isinstance(node, ast.ImportFrom) and node.level > 0:
                if node.level > len(rel_in_app.parts):
                    out.add("#326", app_rel / rel_in_app, f"상대 import 가 `{app_dir.name}/` 밖을 가리킨다 — 이 폴더는 잎이다")
                continue
            for mod_path in _import_paths(node):
                if not _leaf_violation(mod_path, app_dir.name):
                    continue
                if isinstance(node, ast.ImportFrom) and _vo_derivation_path(mod_path, bc_name):
                    for alias in node.names:  # 파생 전용 예외 — 사용을 아래에서 판정
                        vo_symbols[alias.asname or alias.name] = mod_path
                    continue
                out.add("#326", app_rel / rel_in_app, f"`{mod_path}` import — `django_<bc>/` 는 django 와 같은 폴더 안 말고 아무것도 import 하지 않는다(잎 — 예외는 자기 BC domain VO 의 값 파생뿐)")
        for sym in sorted(_called_symbols(mod, set(vo_symbols))):
            out.add("#326", app_rel / rel_in_app, f"`{vo_symbols[sym]}` 의 `{sym}` 호출 — VO import 는 값 파생(나열·순회·멤버 참조) 전용이다: 판정·행위 호출은 잎 밖 몫")


# ── models/ — #334 · #335 · #630 · #631 · #632 ─────────────────────────────

def _is_model_base(base: ast.expr) -> bool:
    name = base.attr if isinstance(base, ast.Attribute) else getattr(base, "id", "")
    if not name or name in NON_MODEL_BASES:
        return False
    return name == MODEL_SUFFIX or name.endswith(MODEL_SUFFIX)


def _const_bool(value: ast.expr) -> bool | None:
    if isinstance(value, ast.Constant) and isinstance(value.value, bool):
        return value.value
    return None


def _meta_info(model_node: ast.ClassDef) -> dict | None:
    """`class Meta` 의 면제 플래그와 db_table. None = 정적 판정 불능(보수적 스킵 — FP≈0)."""
    flags: dict = {"abstract": False, "proxy": False, "managed": True, "db_table": None, "has_db_table": False}
    meta = next((n for n in model_node.body if isinstance(n, ast.ClassDef) and n.name == "Meta"), None)
    if meta is None:
        return flags
    if meta.bases:  # 상속 Meta → 옵션을 정적으로 확정할 수 없다
        return None
    for stmt in meta.body:
        if isinstance(stmt, ast.Assign):
            names = [t.id for t in stmt.targets if isinstance(t, ast.Name)]
            value = stmt.value
        elif isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name) and stmt.value is not None:
            names = [stmt.target.id]
            value = stmt.value
        else:
            continue
        for nm in names:
            if nm == "db_table":
                flags["has_db_table"] = True
                if isinstance(value, ast.Constant) and isinstance(value.value, str):
                    flags["db_table"] = value.value
            elif nm in ("abstract", "proxy", "managed"):
                b = _const_bool(value)
                if b is None:
                    return None
                flags[nm] = b
    return flags


def _relation_target(call: ast.Call) -> ast.expr | None:
    if call.args:
        return call.args[0]
    for kw in call.keywords:
        if kw.arg == "to":
            return kw.value
    return None


def _check_model_file(
    f: Path, app_dir: Path, bc_name: str, label: str, other_labels: set[str],
    is_new: bool, rel: Path, out: Findings,
) -> None:
    try:
        mod = ast.parse(f.read_text(encoding="utf-8"))
    except (SyntaxError, OSError, UnicodeDecodeError):
        return
    imports: dict[str, str] = {}  # 이름 → 절대 점 경로 (#631 출처 추적)
    for node in mod.body:
        if isinstance(node, ast.Import):
            for a in node.names:
                imports[(a.asname or a.name).split(".")[0]] = a.name
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            for a in node.names:
                imports[a.asname or a.name] = f"{node.module}.{a.name}"

    concrete: list[str] = []
    for node in mod.body:
        if not isinstance(node, ast.ClassDef) or not any(_is_model_base(b) for b in node.bases):
            continue
        if not node.name.endswith(MODEL_SUFFIX):
            out.add("#632", rel, f"ORM 모델 클래스는 «상시» `<Name>Model` 이다 — `{node.name}`")

        for stmt in node.body:  # #631 — 면제(abstract 등)와 무관하게 관계 필드는 전부 본다
            value = stmt.value if isinstance(stmt, (ast.Assign, ast.AnnAssign)) else None
            if not isinstance(value, ast.Call):
                continue
            func = value.func
            fname = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", "")
            if fname not in RELATION_FIELDS:
                continue
            target = _relation_target(value)
            if isinstance(target, ast.Constant) and isinstance(target.value, str):
                s = target.value
                if "." in s and s.split(".")[0] in other_labels:
                    out.add("#631", rel, f"타 BC 모델 참조 `\"{s}\"` — 타 BC 는 ID «값»으로만 참조한다(FK·O2O·M2M 금지)")
            else:
                root = target
                while isinstance(root, ast.Attribute):
                    root = root.value
                origin = imports.get(getattr(root, "id", ""), "")
                parts = origin.split(".")
                foreign_app = any(p.startswith("django_") and p != app_dir.name for p in parts)
                foreign_bc = "application" in parts and bc_name not in parts
                if origin and (foreign_app or foreign_bc):
                    out.add("#631", rel, f"타 BC 모델 참조(`{origin}`) — 타 BC 는 ID «값»으로만 참조한다(FK·O2O·M2M 금지)")

        meta = _meta_info(node)
        if meta is None:
            continue  # 상속 Meta·비-리터럴 플래그 — 정적 판정 불능
        if meta["abstract"] or meta["proxy"] or not meta["managed"]:
            continue  # 자체 표가 없다 — #630·#335 카운트 면제
        concrete.append(node.name)
        if is_new:  # #630 — 신규 모델만. 기존 모델의 테이블명은 보존한다(개명 강제 아님)
            base = node.name[: -len(MODEL_SUFFIX)] if node.name.endswith(MODEL_SUFFIX) else node.name
            expected = f"{label}_{_snake(base)}"
            if not meta["has_db_table"]:
                out.add("#630", rel, f"신규 모델 `{node.name}` 이 `Meta.db_table` 을 명시하지 않았다 — 기본값이면 `model` 군더더기가 테이블명에 샌다(기대 `{expected}`)")
            elif meta["db_table"] is not None and meta["db_table"] != expected:
                out.add("#630", rel, f"`{node.name}` 의 db_table `{meta['db_table']}` ≠ 규약 `{expected}` (`<app_label>_<entity_snake>`)")

    if len(concrete) >= 2:
        out.add("#335", rel, f"표 하나 = 파일 하나 — 한 파일에 concrete 모델이 {len(concrete)}개다({', '.join(concrete)})")


def _check_models_pkg(
    app_dir: Path, bc_name: str, label: str, other_labels: set[str],
    new_set: set[Path] | None, bc_rel: Path, out: Findings,
) -> None:
    bc_dir = app_dir.parent.parent
    if (app_dir / "models.py").is_file():
        out.add("#334", bc_rel / (app_dir / "models.py").relative_to(bc_dir), "`models` 는 파일이 아니라 패키지(폴더)다")
        model_files = [app_dir / "models.py"]
    else:
        model_files = []
    models_pkg = app_dir / "models"
    if models_pkg.is_dir():
        for f in sorted(models_pkg.rglob("*.py")):
            if f.name == "__init__.py" or set(f.relative_to(app_dir).parts) & SKIP_DIRS:
                continue
            if not f.name.endswith("_model.py"):
                out.add("#335", bc_rel / f.relative_to(bc_dir), "ORM 모델 파일은 `models/<entity>_model.py` 다 — `_model` 접미가 필수다")
            model_files.append(f)
    for f in model_files:
        is_new = new_set is None or f.resolve() in new_set
        rel = bc_rel / f.relative_to(bc_dir)
        _check_model_file(f, app_dir, bc_name, label, other_labels, is_new, rel, out)


# ── BC 경로 규칙 — #318 · #324 · #467 · #325 ────────────────────────────────

def _check_bc_paths(bc: Path, bc_rel: Path, out: Findings) -> None:
    dirs, _ = _entries(bc)
    for p in dirs:
        if p.name in BANNED_LAYER_NAMES:
            rule = BANNED_LAYER_NAMES[p.name]
            out.add(rule, bc_rel / p.name, f"층 이름은 `driven_layer/` 다 — `{p.name}/` 를 쓰지 않는다")
    for layer_name in (DRIVEN,):
        layer = bc / layer_name
        if not layer.is_dir():
            continue
        ldirs, _ = _entries(layer)
        for p in ldirs:
            if p.name.startswith("django_") or p.name == "adapter":
                continue
            out.add("#318", bc_rel / layer_name / p.name, "`driven_layer/` 의 자식 폴더는 `django_<bc>/` 와 `adapter/` 둘뿐이다")
    for p in bc.rglob("*"):
        rel = p.relative_to(bc)
        parts = rel.parts
        if set(parts) & SKIP_DIRS or parts[0] == "test" or "templates" in parts:
            continue
        orm_artifact = (
            (p.is_dir() and p.name in ("migrations", "models", "admin"))
            or (p.is_file() and p.name in ("models.py", "admin.py"))
        )
        if orm_artifact and not any(seg.startswith("django_") for seg in parts[:-1]):
            out.add("#325", bc_rel / rel, "ORM 모델·마이그레이션·어드민은 `driven_layer/django_<bc>/` 안에 산다")


# ── #331 — label 이 설치된 다른 앱과 겹치지 않는다 ──────────────────────────

def _installed_app_tails(target: Path) -> set[str]:
    """settings 의 INSTALLED_APPS 문자열 원소 말단 마디(label 근사 — 기본 label=패키지명)."""
    tails: set[str] = set()
    candidates: list[Path] = []
    for p in target.rglob("settings.py"):
        if not set(p.parts) & SKIP_DIRS:
            candidates.append(p)
    for p in target.rglob("settings"):
        if p.is_dir() and not set(p.parts) & SKIP_DIRS:
            candidates.extend(f for f in sorted(p.glob("*.py")))
    for f in candidates:
        try:
            mod = ast.parse(f.read_text(encoding="utf-8"))
        except (SyntaxError, OSError, UnicodeDecodeError):
            continue
        for node in ast.walk(mod):
            if not isinstance(node, ast.Assign):
                continue
            if not any(isinstance(t, ast.Name) and t.id == "INSTALLED_APPS" for t in node.targets):
                continue
            if isinstance(node.value, (ast.List, ast.Tuple)):
                for el in node.value.elts:
                    if isinstance(el, ast.Constant) and isinstance(el.value, str):
                        tails.add(el.value.split(".")[-1])
    return tails


def main(argv: list[str]) -> int:
    if len(argv) > 1:
        print(f"사용법: {Path(sys.argv[0]).name} [TARGET_DIR]", file=sys.stderr)
        return 1
    target = Path(argv[0]) if argv else Path(".")
    bad_target_reason = checker_target.bc_shaped_target_reason(target)
    if bad_target_reason is not None:
        print(f"사용 오류: {bad_target_reason}", file=sys.stderr)
        return 1
    if not target.is_dir():
        print(f"사용 오류: 디렉터리가 아니다 — {target}", file=sys.stderr)
        return 1

    containers = [
        p for p in target.rglob("application")
        if p.is_dir() and not (set(p.parts) & SKIP_DIRS)
    ]
    bcs: list[Path] = []
    for c in containers:
        bcs.extend(p for p in sorted(c.iterdir()) if p.is_dir() and not p.name.startswith("."))

    # 대상 0건 가드(#74) — 어떤 필터보다 먼저(#75)
    if not any(_has_adoption_signal(b) for b in bcs):
        print("표준 레이아웃 미채택 — 검사 대상 없음 (clean)")
        return 0

    findings = Findings()
    apps: list[tuple[Path, Path, str]] = []  # (app_dir, bc_rel, bc_name)
    for bc in bcs:
        bc_rel = bc.relative_to(target)
        _check_bc_paths(bc, bc_rel, findings)
        for layer_name in (DRIVEN,):
            layer = bc / layer_name
            if not layer.is_dir():
                continue
            for p in sorted(layer.iterdir()):
                if p.is_dir() and p.name.startswith("django_"):
                    apps.append((p, bc_rel, bc.name))

    if not apps and not findings:
        print("blocker: 채택 신호는 있는데 `django_<bounded_context>/` 앱이 0건이다 — 조용한 무동작을 금지한다(#74)")
        return 2

    new_set = _new_paths(target.resolve())
    if new_set is None and apps:
        print("주의: git 저장소가 아니다 — 신규 식별이 불가해 «전 모델»에 #630 값 검사를 적용한다(fail-closed)")

    labels: dict[str, list[Path]] = {}
    app_labels: dict[Path, str] = {}
    for app_dir, bc_rel, bc_name in apps:
        label = _check_apps_py(app_dir, bc_name, bc_rel / app_dir.parent.name / app_dir.name, findings)
        effective = label or app_dir.name[len("django_"):]
        app_labels[app_dir] = effective
        labels.setdefault(effective, []).append(app_dir)

    # INSTALLED_APPS 말단 마디는 label 근사다(기본 label=패키지명). 자기 등재의 말단은
    # `django_<bc>` 라 label 과 다르므로, label 이 tails 에 있으면 «다른 앱»과의 충돌이다.
    installed_tails = _installed_app_tails(target)
    for app_dir, bc_rel, bc_name in apps:
        label = app_labels[app_dir]
        rel = bc_rel / app_dir.parent.name / app_dir.name
        if len(labels[label]) > 1:
            findings.add("#331", rel, f"label `{label}` 이 저장소 안 다른 앱과 겹친다")
        elif label in installed_tails:
            findings.add("#331", rel, f"label `{label}` 이 설치된 다른 앱(INSTALLED_APPS)과 겹친다")
        _check_leaf_imports(app_dir, rel, findings)
        _check_models_pkg(app_dir, bc_name, label, set(labels) - {label}, new_set, bc_rel, findings)

    if findings:
        print(f"blocker {len(findings)}건 — driven_layer/django_<bc>/ 규율 위반")
        for f in findings:
            print(" ", f)
        return 2
    print(f"clean — django 앱 {len(apps)}개 규율 일치 (트리 75~88행 · standard_tree {tree.SOURCE_SHA})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
