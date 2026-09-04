#!/usr/bin/env python3
"""#646 시제품(dry-run) — django-stubs 제네릭 기저의 타입 인자 규율.

판정(§2-A 확정 문면을 AST 로만 흉내):
  ⓐ bare        : 기저 집합의 클래스를 subscript 없이(`Name`/`Attribute`) 상속 = 위반
  ⓑ ignore-hdr  : 클래스 헤더 줄(`class` 줄 ~ `:` 줄)에 `# type: ignore[type-arg]` = 위반
  ⓑ′ ignore-attr: 클래스 본문 AnnAssign/Assign 줄에 `# type: ignore[type-arg]` = 위반
  통과           : 기저가 `Subscript`(`X[Model]`) · `TYPE_CHECKING` 분기에서 기저의 Subscript 로
                   바인딩된 별칭 이름(`_ModelFormBase`) 상속
  후보(exit 불산입): 헤더 줄의 code 없는 `# type: ignore`(bare-ignore) · 별칭 미해소(import 된 이름)

기저 해소: 모듈 수준 import 바인딩(if/try 하위 포함 · 함수/클래스 본문 안 import 제외)으로
  첫 세그먼트를 풀어 dotted 경로를 만들고 정본 경로 집합(`django.forms.ModelForm` 등)과 대조.
  정본 경로가 아니지만 attr 이름만 일치하면 `lenient` 로 별도 기록(오탐 분석용 · 위반 아님).

대상 파일: check-public-surface-annotation.py 의 `_is_target_file` 을 그대로 복제
  (migrations·manage/wsgi/asgi·test_*·conftest 제외 · test/ 아래는 factories/·fake/ 만 · 숨김 디렉터리 제외).

사용법: proto_646.py [--include-cbv] [--all-files] [--jsonl OUT] TARGET_DIR
종료코드: 0=clean · 2=위반 있음
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

SKIP_DIRS = {
    ".venv", "venv", "site-packages", "node_modules", ".git", "__pycache__", ".dddjango",
    "build", "dist", ".tox", ".mypy_cache", ".pytest_cache", ".eggs",
}
SCAFFOLD_FILES = {"manage.py", "wsgi.py", "asgi.py"}
TEST_DIR_NAMES = {"test", "tests"}
TEST_FREE_DIRS = {"unit", "integration", "e2e"}
MATERIAL_DIRS = {"factories", "fake"}

# ── 기저 집합(정본 dotted 경로) ────────────────────────────────────────────
ADMIN_FORM_NAMES = {
    "ModelForm", "BaseModelForm", "ModelAdmin", "InlineModelAdmin",
    "TabularInline", "StackedInline", "BaseInlineFormSet", "BaseModelFormSet",
}
_FORM_MODULES = ("django.forms", "django.forms.models")
_ADMIN_MODULES = ("django.contrib.admin", "django.contrib.admin.options")
ADMIN_FORM_PATHS: dict[str, str] = {}
for _n in ("ModelForm", "BaseModelForm", "BaseInlineFormSet", "BaseModelFormSet"):
    for _m in _FORM_MODULES:
        ADMIN_FORM_PATHS[f"{_m}.{_n}"] = _n
for _n in ("ModelAdmin", "InlineModelAdmin", "TabularInline", "StackedInline"):
    for _m in _ADMIN_MODULES:
        ADMIN_FORM_PATHS[f"{_m}.{_n}"] = _n

# django-stubs 가 TypeVar 기본값 없이 제네릭으로 선언한 CBV(bare 상속 시 mypy strict [type-arg]).
# View/TemplateView/RedirectView 는 `_ViewResponse` 에 default 가 있어 bare 가 red 가 아니다 — 집합 밖.
CBV_NAMES = {
    "DetailView", "BaseDetailView", "SingleObjectMixin",
    "ListView", "BaseListView", "MultipleObjectMixin",
    "FormView", "BaseFormView", "FormMixin",
    "CreateView", "BaseCreateView", "UpdateView", "BaseUpdateView", "ModelFormMixin",
    "DeleteView", "BaseDeleteView", "DeletionMixin",
    "ArchiveIndexView", "YearArchiveView", "MonthArchiveView", "WeekArchiveView",
    "DayArchiveView", "TodayArchiveView", "DateDetailView", "BaseDateListView",
}
_CBV_MODULES = (
    "django.views.generic", "django.views.generic.detail", "django.views.generic.list",
    "django.views.generic.edit", "django.views.generic.dates",
)
CBV_PATHS: dict[str, str] = {f"{_m}.{_n}": _n for _n in CBV_NAMES for _m in _CBV_MODULES}

IGNORE_RE = re.compile(r"#\s*type:\s*ignore(?:\[([^\]]*)\])?")


def is_target_file(path: Path) -> bool:
    parts = set(path.parts)
    if parts & SKIP_DIRS or "migrations" in parts:
        return False
    if path.name in SCAFFOLD_FILES:
        return False
    if path.name.startswith("test_") or path.name == "conftest.py":
        return False
    if parts & TEST_DIR_NAMES:
        if not (parts & MATERIAL_DIRS):
            return False
        if parts & TEST_FREE_DIRS:
            return False
    return True


# ── 바인딩 ──────────────────────────────────────────────────────────────────
@dataclass
class Bindings:
    imports: dict[str, str] = field(default_factory=dict)      # 로컬 이름 → dotted 원경로
    tc_alias: dict[str, ast.expr] = field(default_factory=dict) # TYPE_CHECKING 분기 안 대입 별칭
    rt_alias: dict[str, ast.expr] = field(default_factory=dict) # 그 밖(else·모듈 수준) 대입 별칭
    tc_classes: set[str] = field(default_factory=set)           # TYPE_CHECKING 분기 안에서 정의된 클래스 이름


def _is_type_checking_test(test: ast.expr, imports: dict[str, str]) -> bool:
    if isinstance(test, ast.Name):
        return imports.get(test.id, test.id).endswith("TYPE_CHECKING")
    if isinstance(test, ast.Attribute):
        return test.attr == "TYPE_CHECKING"
    return False


def module_bindings(mod: ast.Module) -> Bindings:
    b = Bindings()

    def record_alias(st: ast.stmt, into: dict[str, ast.expr]) -> None:
        if isinstance(st, ast.AnnAssign) and isinstance(st.target, ast.Name) and st.value is not None:
            into[st.target.id] = st.value
        elif isinstance(st, ast.Assign) and st.value is not None:
            for t in st.targets:
                if isinstance(t, ast.Name):
                    into[t.id] = st.value

    def walk(stmts: list[ast.stmt], in_tc: bool) -> None:
        for st in stmts:
            if isinstance(st, ast.ImportFrom):
                for a in st.names:
                    b.imports[a.asname or a.name] = f"{st.module}.{a.name}" if st.module else a.name
            elif isinstance(st, ast.Import):
                for a in st.names:
                    if a.asname:
                        b.imports[a.asname] = a.name
                    else:
                        top = a.name.split(".")[0]
                        b.imports[top] = top
            elif isinstance(st, ast.ClassDef):
                b.imports.pop(st.name, None)
                # TYPE_CHECKING 분기 안 «중간 클래스»(kkebi saju 모양):
                #   if TYPE_CHECKING: class _Base(admin.ModelAdmin[M]): pass / else: _Base = admin.ModelAdmin
                # → 별칭과 같은 뜻이라 첫 기저를 별칭 값으로 기록한다.
                if in_tc and st.bases:
                    b.tc_alias[st.name] = st.bases[0]
                    b.tc_classes.add(st.name)
            elif isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef)):
                b.imports.pop(st.name, None)
            elif isinstance(st, (ast.Assign, ast.AnnAssign)):
                record_alias(st, b.tc_alias if in_tc else b.rt_alias)
                targets = st.targets if isinstance(st, ast.Assign) else [st.target]
                for t in targets:
                    if isinstance(t, ast.Name):
                        b.imports.pop(t.id, None)
            elif isinstance(st, ast.If):
                tc = _is_type_checking_test(st.test, b.imports)
                walk(st.body, in_tc or tc)
                walk(st.orelse, in_tc)
            elif isinstance(st, ast.Try):
                walk(st.body, in_tc)
                for h in st.handlers:
                    walk(h.body, in_tc)
                walk(st.orelse, in_tc)
                walk(st.finalbody, in_tc)

    walk(mod.body, False)
    return b


def dotted(node: ast.expr) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        head = dotted(node.value)
        return f"{head}.{node.attr}" if head else None
    return None


def resolve_path(node: ast.expr, imports: dict[str, str]) -> str | None:
    """`forms.ModelForm` → `django.forms.ModelForm` (첫 세그먼트를 import 바인딩으로 치환)."""
    d = dotted(node)
    if d is None:
        return None
    head, _, rest = d.partition(".")
    base = imports.get(head, head)
    return f"{base}.{rest}" if rest else base


@dataclass
class BaseMatch:
    expr: str                 # 소스 표기
    resolved: str | None      # dotted 해소 경로
    canonical: str | None     # 기저 집합 이름(정본 경로 일치)
    lenient: str | None       # attr 이름만 일치(정본 경로 불일치 · 오탐 분석용)
    family: str | None        # admin_form / cbv
    shape: str                # bare / subscript / alias-subscript / alias-bare / alias-unresolved
    alias: str | None = None


def classify_base(node: ast.expr, b: Bindings, paths: dict[str, str], names: set[str], families: dict[str, str]) -> BaseMatch | None:
    shape = "bare"
    alias: str | None = None
    target = node
    if isinstance(node, ast.Subscript):
        shape = "subscript"
        target = node.value
    elif isinstance(node, ast.Name) and node.id not in b.imports:
        if node.id in b.tc_alias:
            alias = node.id
            v = b.tc_alias[node.id]
            if isinstance(v, ast.Subscript):
                shape, target = "alias-subscript", v.value
            else:
                shape, target = "alias-bare", v
        elif node.id in b.rt_alias:
            alias = node.id
            v = b.rt_alias[node.id]
            if isinstance(v, ast.Subscript):
                shape, target = "alias-subscript", v.value   # TYPE_CHECKING 밖 subscript 별칭 — 런타임 TypeError 후보
            else:
                shape, target = "alias-bare", v
    resolved = resolve_path(target, b.imports)
    if resolved is None:
        return None
    canonical = paths.get(resolved)
    attr = resolved.rsplit(".", 1)[-1]
    lenient = attr if (canonical is None and attr in names) else None
    if canonical is None and lenient is None:
        return None
    fam = families.get(canonical or lenient or "")
    return BaseMatch(ast.unparse(node), resolved, canonical, lenient, fam, shape, alias)


def ignore_codes_by_line(src_lines: list[str]) -> dict[int, set[str]]:
    out: dict[int, set[str]] = {}
    for i, line in enumerate(src_lines, start=1):
        m = IGNORE_RE.search(line)
        if m:
            codes = {c.strip() for c in (m.group(1) or "").split(",") if c.strip()}
            out[i] = codes if codes else {"<bare>"}
    return out


def header_range(cls: ast.ClassDef, src_lines: list[str]) -> tuple[int, int]:
    """`class` 줄 ~ `:` 줄. 기저·키워드의 마지막 end_lineno 부터 코드부가 `:` 로 끝나는 줄까지."""
    start = cls.lineno
    last = start
    for n in list(cls.bases) + [k.value for k in cls.keywords]:
        last = max(last, n.end_lineno or last)
    end = last
    for ln in range(last, min(len(src_lines), last + 20) + 1):
        code = src_lines[ln - 1].split("#", 1)[0].rstrip()
        if code.endswith(":"):
            end = ln
            break
    if cls.body and cls.body[0].lineno < end:
        end = cls.body[0].lineno
    return start, end


@dataclass
class Finding:
    file: str
    bc: str | None
    cls: str
    line: int
    kind: str              # violation-a / violation-b-header / violation-b-attr / pass-subscript / pass-alias / cand-*
    family: str | None
    bases: list[dict]
    detail: str = ""
    in_tc: bool = False    # 클래스 자체가 TYPE_CHECKING 분기 안에 정의됨(런타임 미실행)


def bc_of(rel: Path) -> str | None:
    parts = rel.parts
    if "application" in parts:
        i = parts.index("application")
        if i + 1 < len(parts):
            return parts[i + 1]
    return None


def scan_file(path: Path, rel: Path, include_cbv: bool) -> list[Finding]:
    src = path.read_text(encoding="utf-8")
    try:
        mod = ast.parse(src)
    except SyntaxError:
        return []
    lines = src.splitlines()
    ignores = ignore_codes_by_line(lines)
    b = module_bindings(mod)
    paths = dict(ADMIN_FORM_PATHS)
    names = set(ADMIN_FORM_NAMES)
    families = {n: "admin_form" for n in ADMIN_FORM_NAMES}
    if include_cbv:
        paths.update(CBV_PATHS)
        names |= CBV_NAMES
        families.update({n: "cbv" for n in CBV_NAMES})
    out: list[Finding] = []
    bc = bc_of(rel)

    for node in ast.walk(mod):
        if not isinstance(node, ast.ClassDef):
            continue
        matches = [m for m in (classify_base(x, b, paths, names, families) for x in node.bases) if m]
        if not matches:
            continue
        n_before = len(out)
        canon = [m for m in matches if m.canonical]
        fam = next((m.family for m in canon), None) or next((m.family for m in matches), None)
        bd = [asdict(m) for m in matches]
        hs, he = header_range(node, lines)
        hdr_codes: set[str] = set()
        for ln in range(hs, he + 1):
            hdr_codes |= ignores.get(ln, set())
        if not canon:
            out.append(Finding(str(rel), bc, node.name, node.lineno, "cand-lenient-only", fam, bd,
                               "attr 이름만 일치 — 정본 경로 아님(오탐 분석용)"))
            continue
        # ⓐ bare
        for m in canon:
            if m.shape in ("bare", "alias-bare"):
                out.append(Finding(str(rel), bc, node.name, node.lineno, "violation-a", fam, bd,
                                   f"맨몸 상속 {m.expr} ({m.shape})"))
            elif m.shape == "alias-unresolved":
                out.append(Finding(str(rel), bc, node.name, node.lineno, "cand-alias-unresolved", fam, bd, m.expr))
        # ⓑ header ignore
        if "type-arg" in hdr_codes:
            out.append(Finding(str(rel), bc, node.name, node.lineno, "violation-b-header", fam, bd,
                               f"헤더 {hs}-{he} `# type: ignore[type-arg]`"))
        elif "<bare>" in hdr_codes:
            out.append(Finding(str(rel), bc, node.name, node.lineno, "cand-bare-ignore-header", fam, bd,
                               f"헤더 {hs}-{he} code 없는 `# type: ignore`"))
        # ⓑ′ body attr ignore
        for st in node.body:
            if isinstance(st, (ast.AnnAssign, ast.Assign)):
                for ln in range(st.lineno, (st.end_lineno or st.lineno) + 1):
                    if "type-arg" in ignores.get(ln, set()):
                        tgt = ast.unparse(st.target if isinstance(st, ast.AnnAssign) else st.targets[0])
                        out.append(Finding(str(rel), bc, node.name, ln, "violation-b-attr", fam, bd,
                                           f"속성 `{tgt}` 줄 `# type: ignore[type-arg]`"))
        # pass 기록(수치 대조용)
        shapes = {m.shape for m in canon}
        if shapes <= {"subscript"}:
            out.append(Finding(str(rel), bc, node.name, node.lineno, "pass-subscript", fam, bd))
        elif shapes <= {"alias-subscript", "subscript"}:
            rt_only = [m for m in canon if m.alias and m.alias not in b.tc_alias]
            k = "cand-alias-subscript-runtime" if rt_only else "pass-alias"
            out.append(Finding(str(rel), bc, node.name, node.lineno, k, fam, bd,
                               "TYPE_CHECKING 밖 subscript 별칭 — 런타임 TypeError 후보" if rt_only else ""))
        if node.name in b.tc_classes:
            for x in out[n_before:]:
                x.in_tc = True
    return out


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("target")
    ap.add_argument("--include-cbv", action="store_true")
    ap.add_argument("--all-files", action="store_true", help="_is_target_file 규칙 무시(테스트 포함 전수)")
    ap.add_argument("--jsonl")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args(argv)
    target = Path(a.target).resolve()
    files = [
        p for p in sorted(target.rglob("*.py"))
        if (a.all_files and not (set(p.parts) & SKIP_DIRS)) or (not a.all_files and is_target_file(p))
    ]
    files = [p for p in files if not any(seg.startswith(".") for seg in p.relative_to(target).parts[:-1])]
    findings: list[Finding] = []
    for f in files:
        findings.extend(scan_file(f, f.relative_to(target), a.include_cbv))
    viol = [x for x in findings if x.kind.startswith("violation")]
    if a.jsonl:
        with open(a.jsonl, "w", encoding="utf-8") as fh:
            for x in findings:
                fh.write(json.dumps(asdict(x), ensure_ascii=False) + "\n")
    if not a.quiet:
        for x in findings:
            print(f"{x.kind:28s} {x.file}:{x.line} {x.cls} [{x.family}] {x.detail}")
    kinds: dict[str, int] = {}
    for x in findings:
        kinds[x.kind] = kinds.get(x.kind, 0) + 1
    print(f"# files={len(files)} findings={len(findings)} violations={len(viol)} kinds={json.dumps(kinds, ensure_ascii=False)}")
    return 2 if viol else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
