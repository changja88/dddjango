#!/usr/bin/env python3
"""표준 파일트리 골격 검사기 — 제1원칙(#486~#491)의 결정적 백스톱.

트리 데이터는 `standard_tree.py`(정본 140행의 기계 사본) 하나에서 온다 — 이 파일에
경로 문자열을 다시 적지 않는다. 정본이 개정되면 데이터만 갈리고 이 검사기는 그대로다.

무엇을 잡나 (규칙 번호는 트리 개정 명세):
  #486  어느 BC 를 열어도 골격이 그대로 있다 — 내용 유무 무관. 채택 저장소에서는
        `application/` 직계 전부가 BC 다(신호 없는 평면 BC 도 검사 대상).
  #488  고정(·재등장) 칸은 부모가 있으면 반드시 있다 — 폴더는 비어도 `__init__.py` 로,
        파일도 비면 빈 파일로. `<project>/`(트리 136~139행)·`framework/` 고정 서브트리에도 적용.
  #489  `<…>` 자리표시자 칸만 그 개념이 생길 때 생긴다.
  #490  BC 안에 트리에 없는 경로가 있으면 위반. 재량은 «리프로 닫은 폴더 안»의 추가
        모듈뿐이다(#15 작성자 재량) — 자리표시자 «파일» 칸이 있는 층만 파일 이름이 자유다.
  #81   BC 직계는 일곱뿐. / #429·#436  `<project>/` 직계 폐쇄(면제는 넷뿐 — `settings.py` 는 아님).
  #58 #314 #393  금지 경로(management/commands · domain_layer 의 specification · BC 안 framework).
  #395  `framework/` 의 자식은 다섯(고정 셋 + `<capability>/`·`<technology>/`) — 고정 셋의
        서브트리 존재는 #488 로 본다. 인스턴스 «내용»은 content 검사기 몫.

가드 계약 (명세 조각 ⓐ):
  - 대상 0건 가드: 채택 신호는 있는데 검사할 BC 가 0이면 exit 2 (#74). 가드는 어떤
    필터보다 먼저 선다(#75).
  - 채택 신호원은 둘이다(#78): ⑴ 층 폴더 glob ⑵ Django 앱 마커.

등록 순서: 이 검사는 다른 모든 검사보다 «먼저» 돌고, 걸리면 나머지를 돌리지 않는다(#487).
내용 판정(#10·#628 등 ast 규칙)은 Phase 3 편입분이다 — 여기는 «존재·폐쇄»만 본다.

사용법: check-layer-skeleton.py [TARGET_DIR]   (기본: 현재 디렉터리)
종료코드: 0=clean(또는 표준 미채택) · 1=사용/분석 오류 · 2=blocker(발견 출력)
구조화 레코드: DJR_FINDINGS_JSON=<경로> 지정 시 findings.py(공용 모듈)가 JSON lines 를
추가 방출한다 — 라인 출력·exit 의미론 무변(T0 B2).
"""
from __future__ import annotations

import re
import sys

import checker_target
from findings import Findings, emit_all, zero_target_guard
from pathlib import Path

try:
    import standard_tree as tree
except ImportError:  # 데이터 모듈 없이는 판정 불가 — fail-closed(분석 오류)
    print("분석 오류: standard_tree.py 를 찾지 못했다 — 검사기와 같은 폴더에 있어야 한다", file=sys.stderr)
    sys.exit(1)

SKIP_DIRS = {".venv", "venv", "site-packages", "node_modules", ".git", "__pycache__", ".dddjango"}
IGNORE_FILES = {"__init__.py", ".DS_Store"}
DJANGO_APP_MARKERS = ("models.py", "apps.py", "views.py", "admin.py")
PROJECT_ALLOWED = {"api.py", "urls.py", "celery.py", "settings"}
PROJECT_EXEMPT = {"health.py", "home.py", "asgi.py", "wsgi.py", "__init__.py"}
PROJECT_REQUIRED_FILES = ("api.py", "urls.py", "celery.py")  # 트리 136~138행 fixed (#488)

NEW_LAYERS = {"driving_layer", "application_layer", "domain_layer", "driven_layer"}
TOKEN = re.compile(r"<([a-z_]+)>")


def _entries(d: Path) -> tuple[list[Path], list[Path]]:
    dirs, files = [], []
    for p in sorted(d.iterdir()):
        if p.name.startswith(".") or p.name in SKIP_DIRS:
            continue
        if p.is_dir():
            dirs.append(p)
        elif p.name not in IGNORE_FILES and not p.name.endswith(".pyc"):
            files.append(p)
    return dirs, files


def _has_adoption_signal(bc_dir: Path) -> bool:
    """채택 신호원 둘(#78): 층 폴더 또는 Django 앱 마커."""
    has_layer = any((bc_dir / n).is_dir() for n in NEW_LAYERS)
    has_marker = any((bc_dir / m).is_file() for m in DJANGO_APP_MARKERS) or any(
        p.is_dir() and p.name.startswith("django_") for p in bc_dir.iterdir()
    )
    return has_layer or has_marker


# ── 트리 대조 재귀 ──────────────────────────────────────────────────────────

def _segments(row: "tree.Row") -> list[str]:
    return row.name.rstrip("/").split("/")


def _file_pattern_ok(name: str, pattern: str) -> bool:
    """`<form>_form.py` 같은 마지막 마디 패턴과 대조 — `<tok>` 는 비지 않은 아무 이름."""
    rx = TOKEN.sub("(.+)", re.escape(pattern))
    return re.fullmatch(rx, name) is not None


def _check_multi(dir_path: Path, shapes: list[list[str]], out: Findings) -> None:
    """하위 경로를 품은 행(form/·feature/·templates/ …)의 «모양» 검사 — 트리 85~88행.

    shapes 는 남은 마디 목록들이다. 마지막 마디는 파일 패턴, 그 앞은 폴더 마디
    (`<tok>` 마디는 아무 이름). 어느 모양에도 안 맞는 항목은 트리에 없는 경로다(#490).
    """
    dirs, files = _entries(dir_path)
    for f in files:
        ok = any(len(s) == 1 and _file_pattern_ok(f.name, s[0]) for s in shapes)
        if not ok:
            out.add("#490", f, "이 자리의 파일 모양이 아니다 — 트리에 없는 경로")
    for p in dirs:
        nexts = [s[1:] for s in shapes if len(s) > 1 and (TOKEN.search(s[0]) or s[0] == p.name)]
        if nexts:
            _check_multi(p, nexts, out)
        else:
            out.add("#490", p, "트리에 없는 칸이다 — 반환")


def _check_level(dir_path: Path, row: "tree.Row", bindings: dict[str, str], out: Findings,
                 skip: frozenset[str] = frozenset()) -> None:
    """row(폴더 칸)의 실제 디렉터리 dir_path 를 트리 기대와 대조하고 재귀한다."""
    kids = tree.children(row)
    if not kids:  # 트리가 리프로 닫은 폴더 — 안은 작성자 재량(#490·#15)
        return

    fixed_dirs: dict[str, "tree.Row"] = {}
    fixed_files: dict[str, "tree.Row"] = {}
    dir_placeholder: "tree.Row | None" = None
    has_file_placeholder = False  # 자리표시자 «파일» 칸 — 이것이 있어야만 파일 이름이 자유다(#490)
    multi_shapes: dict[str, list[list[str]]] = {}

    for c in kids:
        segs = _segments(c)
        if len(segs) > 1:
            multi_shapes.setdefault(segs[0], []).append(segs[1:] if not tree.is_dir(c) else segs[1:])
            continue
        if tree.is_dir(c):
            if c.kind in ("fixed", "reappear"):
                fixed_dirs[tree.concrete_name(c, bindings).rstrip("/")] = c
            else:
                dir_placeholder = c
        else:
            if c.kind in ("fixed", "reappear"):
                fixed_files[tree.concrete_name(c, bindings)] = c
            else:
                has_file_placeholder = True

    dirs, files = _entries(dir_path)
    dirs = [p for p in dirs if p.name not in skip]
    files = [p for p in files if p.name not in skip]
    dir_names = {p.name for p in dirs}

    # #488 — 고정 칸은 부모가 있으면 반드시 있다
    for name, crow in fixed_dirs.items():
        sub = dir_path / name
        if not sub.is_dir():
            out.add("#488", sub, f"고정 칸 `{name}/` 부재 — 비어도 `__init__.py` 로 만든다 (트리 {crow.r}행)")
            continue
        if not (sub / "__init__.py").is_file():
            out.add("#488", sub, "고정 칸 폴더에 `__init__.py` 가 없다")
        _check_level(sub, crow, bindings, out)
    for name, crow in fixed_files.items():
        if not (dir_path / name).is_file():
            out.add("#488", dir_path / name, f"고정 파일 부재 — 비면 빈 파일로 만든다 (트리 {crow.r}행)")

    # #490 — 폴더 폐쇄: 칸이 아닌 폴더는 위반. 자리표시자 폴더가 있으면 나머지는 인스턴스다.
    if row.name.startswith("migrations"):
        for p in dirs:  # <migration>.py 는 파일 자리 — 폴더는 트리에 없는 경로다
            out.add("#490", p, "`migrations/` 아래 폴더는 트리에 없는 경로다")
        return
    for p in dirs:
        if p.name in fixed_dirs:
            continue
        if p.name in multi_shapes:
            _check_multi(p, multi_shapes[p.name], out)
        elif dir_placeholder is not None:
            inst_bind = dict(bindings)
            for tok in set(TOKEN.findall(dir_placeholder.name)):
                inst_bind[tok] = p.name
            _check_level(p, dir_placeholder, inst_bind, out)
        elif p.name == "commands" and dir_path.name == "management":
            out.add("#58", p, "`management/commands/` 를 만들지 않는다")
        else:
            out.add("#490", p, "트리에 없는 칸이다 — 반환")

    # 파일 폐쇄 — 자리표시자 «파일» 칸이 있는 층만 이름이 자유다. 고정 파일 칸만 있는 층의
    # 추가 파일은 트리에 없는 경로다(#490 — 재량 조항은 «리프로 닫은 폴더»에만 걸린다).
    if not has_file_placeholder:
        for f in files:
            if f.name not in fixed_files:
                out.add("#490", f, "트리가 이 층에 이름을 준 파일이 아니다")


def _check_banned_paths(bc_dir: Path, out: Findings) -> None:
    """경로 자체가 금지인 것 — 자리표시자 인스턴스로 흡수되지 않도록 전역으로 잡는다."""
    for p in bc_dir.rglob("*"):
        if not p.is_dir() or set(p.parts) & SKIP_DIRS:
            continue
        if p.name == "commands" and p.parent.name == "management":
            out.add("#58", p, "`management/commands/` 를 만들지 않는다")
        elif p.name == "specification" and "domain_layer" in p.parts:
            out.add("#314", p, "`domain_layer/` 에 `specification/` 폴더를 두지 않는다")
        elif p.name == "framework":
            out.add("#393", p, "`framework/` 는 저장소 루트 소유다 — BC 아래에 두면 위반")


def _check_bc(bc_dir: Path, out: Findings) -> None:
    bindings = {"bounded_context": bc_dir.name}
    root = tree.bc_root()
    allowed = {tree.concrete_name(c, bindings).rstrip("/") for c in tree.children(root)}
    pre_flagged: set[str] = set()
    dirs, files = _entries(bc_dir)
    for p in dirs:
        if p.name not in allowed:
            out.add("#81", p, "BC 직계는 일곱뿐이다 — 여덟째는 없다")
            pre_flagged.add(p.name)
    _check_level(bc_dir, root, bindings, out, frozenset(pre_flagged))
    _check_banned_paths(bc_dir, out)


# ── framework/ · <project>/ — BC 폐쇄(#490)의 주어는 아니지만 자기 규칙이 있다 ──

def _framework_rows() -> "tree.Row":
    return next(r for r in tree.ROWS if r.depth == 0 and r.name == "framework/")


def _check_framework(fw_dir: Path, out: Findings) -> None:
    """#395 자식 다섯 + #488 고정 서브트리 존재. 인스턴스 «내용»은 content 검사기 몫."""
    fw = _framework_rows()
    fixed = {c.name.rstrip("/"): c for c in tree.children(fw) if c.kind == "fixed"}
    dirs, files = _entries(fw_dir)
    for f in files:
        out.add("#395", f, "`framework/` 직계에 파일 칸은 없다 — 자식은 다섯(폴더)뿐")
    for name, crow in fixed.items():
        sub = fw_dir / name
        if not sub.is_dir():
            out.add("#488", sub, f"고정 칸 `{name}/` 부재 (트리 {crow.r}행)")
            continue
        if not (sub / "__init__.py").is_file():
            out.add("#488", sub, "고정 칸 폴더에 `__init__.py` 가 없다")
        _check_framework_fixed(sub, crow, out)
    # <capability>/·<technology>/ 는 이름으로 못 가른다 — 존재만 허용하고 내용은 여기서 안 본다


def _check_framework_fixed(dir_path: Path, row: "tree.Row", out: Findings) -> None:
    for c in tree.children(row):
        if c.kind != "fixed":
            continue
        name = c.name.rstrip("/")
        target = dir_path / name
        if tree.is_dir(c):
            if not target.is_dir():
                out.add("#488", target, f"고정 칸 `{name}/` 부재 (트리 {c.r}행)")
            else:
                if not (target / "__init__.py").is_file():
                    out.add("#488", target, "고정 칸 폴더에 `__init__.py` 가 없다")
                _check_framework_fixed(target, c, out)
        elif not target.is_file():
            out.add("#488", target, f"고정 파일 부재 (트리 {c.r}행)")


def _find_project_pkg(target: Path) -> tuple[Path | None, str]:
    """<project> 판정 — manage.py 의 DJANGO_SETTINGS_MODULE 이 1순위(결정적), 없으면 유일 후보만."""
    manage = target / "manage.py"
    if manage.is_file():
        m = re.search(r"DJANGO_SETTINGS_MODULE[\"']\s*,\s*[\"']([\w.]+)[\"']", manage.read_text(encoding="utf-8", errors="ignore"))
        if m:
            pkg = target / m.group(1).split(".")[0]
            if pkg.is_dir():
                return pkg, "manage.py"
    cands = [
        p for p in sorted(target.iterdir())
        if p.is_dir() and not p.name.startswith(".") and p.name not in SKIP_DIRS
        and p.name not in ("application", "framework")
        and ((p / "settings").is_dir() or (p / "settings.py").is_file())
    ]
    if len(cands) == 1:
        return cands[0], "유일 후보"
    if len(cands) > 1:
        return None, f"후보 {len(cands)}개 — manage.py 없음, 판정 보류"
    return None, "없음"


def _check_project(pkg: Path, out: Findings) -> None:
    dirs, files = _entries(pkg)
    for p in dirs + files:
        if p.name in PROJECT_ALLOWED or p.name in PROJECT_EXEMPT:
            continue
        hint = " — `settings/` 로 이관한다" if p.name == "settings.py" else ""
        out.add("#429", p, f"`<project>/` 에는 전역에 하나만 요구되는 것만 온다 (api.py·urls.py·celery.py·settings/){hint}")
    for name in PROJECT_REQUIRED_FILES:  # #488 — 트리 136~138행 fixed
        if not (pkg / name).is_file():
            out.add("#488", pkg / name, "고정 파일 부재 — 비면 빈 파일로 만든다 (`<project>/` · 트리 136~138행)")
    if not (pkg / "settings").is_dir() and not (pkg / "settings.py").is_file():
        out.add("#488", pkg / "settings", "고정 칸 `settings/` 부재 (트리 139행)")


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
    signaled = [b for b in bcs if _has_adoption_signal(b)]
    fw_dir = target / "framework"

    # 대상 0건 가드(#74) — 어떤 필터보다 먼저(#75)
    repo_signal = bool(signaled) or fw_dir.is_dir()
    if not repo_signal:
        print("표준 레이아웃 미채택 — 검사 대상 없음 (clean)")
        return 0
    if not bcs:
        guard = zero_target_guard(
            "blocker: 채택 신호는 있는데 검사할 BC 가 0건이다 — 조용한 무동작을 금지한다(#74)"
        )
        emit_all(guard, printer=print, indent="")
        return 2

    findings = Findings()
    # 채택 저장소에서는 application/ 직계 «전부»가 BC 다(#486) — 신호 없는 평면 BC 도 검사한다.
    for bc in bcs:
        _check_bc(bc, findings)
    if fw_dir.is_dir():
        _check_framework(fw_dir, findings)
    pkg, how = _find_project_pkg(target)
    if pkg is not None:
        _check_project(pkg, findings)
    elif how.startswith("후보"):
        print(f"주의: `<project>/` {how} — `<project>` 검사를 건너뛴다(오판 방지)")

    if findings:
        print(f"blocker {len(findings)}건 — 골격이 어긋나면 나머지 검사를 돌리지 않는다(#487)")
        for f in findings:
            print(" ", f)
        return 2
    print(f"clean — BC {len(bcs)}개 골격 일치 (트리 140행 · standard_tree {tree.SOURCE_SHA})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
