#!/usr/bin/env python3
"""dddjango 평가 *결정 레인* 구조 리포터 (EVAL-METHOD §1.1 표 집행).

백스톱(exit2 blocker)이 **아니다** — 채점의 *결정 레인*을 결정론적으로 산출하는
**리포터**다. 항목별 `{신호: PASS/FAIL/NA}` + 줄 인용을 내고 **항상 exit 0**.
집계(치명 게이트·사전식)는 EVAL-METHOD §2가 별도로 한다. 의미 레인(blind grader)은
이 출력을 *보지 않은 채* 채점하고 조정자가 사후 대조한다(§1.0·§1.3).

구현 행(grep-closable, §1.1 표):
  SH-1 신규 컨테이너 / SH-2 신규 BC 4계층 / SH-4 신규 Django앱 위치 / SH-7 포트 위치 /
  SH-9 단일 레이아웃 / SD-7 컨텍스트 통신(FAIL방향) / SD-3 무복제(constraint 캐럿) /
  NJ-1 스택 / NJ-4 status 선언.
비대칭/의미 행(SD-7 PASS='OHS인가', Q-5 명령·보고 정직성)은 의미 레인 위임 — 여기서 안 봄.

v4 brownfield 헬퍼(§1.1.M): HEAD가 있으면 실제 AppConfig/Model identity로 app별 baseline
existing/new를 분류한다. 기존 persistence app은 touched 여부와 무관하게 위치를 grandfather하고,
표준 `application/` 컨테이너가 없는 프로젝트에 baseline root app 관례가 있으면 그 관례를
보존한다. HEAD가 없으면 기존 위치만으로 FAIL을 만들지 않는다. --run-change-set 으로 baseline(HEAD) 대비
working-tree 변경 = `git diff HEAD`(tracked) ∪ `git ls-files --others`(untracked 신규)를
출력한다 — /dddjango 산출은 대개 untracked라 `git diff HEAD`만으론 0건 누락되는 함정 차단.

사용법:
  check-structure.py [TARGET_DIR]          # 전 항목 리포트
  check-structure.py --run-change-set [DIR]# 마스크 C run-change-set(파일목록)만
종료코드: 항상 0 (리포터). 사용오류만 1.
"""
from __future__ import annotations

import ast
import re
import subprocess
import sys
from pathlib import Path

LAYERS = ("domain_layer", "application_layer", "infra_layer", "presentation_layer")


def _git(target: Path, *args: str) -> list[str]:
    try:
        out = subprocess.run(
            ["git", "-C", str(target), *args],
            capture_output=True, text=True, check=False,
        )
        if out.returncode != 0:
            return []
        return [ln for ln in out.stdout.splitlines() if ln.strip()]
    except FileNotFoundError:
        return []


def _git_root(target: Path) -> Path | None:
    """Return the repository root when TARGET has a readable HEAD."""
    try:
        root = subprocess.run(
            ["git", "-C", str(target), "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=False,
        )
        head = subprocess.run(
            ["git", "-C", str(target), "rev-parse", "--verify", "HEAD"],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return None
    if root.returncode != 0 or head.returncode != 0:
        return None
    return Path(root.stdout.strip()).resolve()


def _git_show(root: Path, relative: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "show", f"HEAD:{relative.as_posix()}"],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return None
    return result.stdout if result.returncode == 0 else None


def _expression_path(expression: ast.expr) -> str | None:
    if isinstance(expression, ast.Name):
        return expression.id
    if isinstance(expression, ast.Attribute):
        owner = _expression_path(expression.value)
        if owner is not None:
            return f"{owner}.{expression.attr}"
    return None


class _ModuleDjangoSignalCollector(ast.NodeVisitor):
    """모듈 import/class만 수집하고 지역 scope의 예시 코드는 제외한다."""

    def __init__(self) -> None:
        self.imports: list[ast.Import | ast.ImportFrom] = []
        self.classes: list[ast.ClassDef] = []

    def visit_Import(self, node: ast.Import) -> None:
        self.imports.append(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        self.imports.append(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self.classes.append(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        return

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        return

    def visit_Lambda(self, node: ast.Lambda) -> None:
        return


def _django_signal_collector(text: str) -> _ModuleDjangoSignalCollector | None:
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return None
    collector = _ModuleDjangoSignalCollector()
    collector.visit(tree)
    return collector


def _has_app_config_signal(text: str) -> bool:
    collector = _django_signal_collector(text)
    if collector is None:
        return False
    direct_aliases: set[str] = set()
    module_aliases: set[str] = set()
    for node in collector.imports:
        if isinstance(node, ast.ImportFrom) and node.module == "django.apps":
            direct_aliases.update(
                imported.asname or imported.name
                for imported in node.names
                if imported.name == "AppConfig"
            )
        elif isinstance(node, ast.ImportFrom) and node.module == "django":
            module_aliases.update(
                imported.asname or imported.name
                for imported in node.names
                if imported.name == "apps"
            )
        elif isinstance(node, ast.Import):
            for imported in node.names:
                if imported.name == "django.apps":
                    module_aliases.add(imported.asname or imported.name)
                elif imported.name == "django":
                    module_aliases.add(f"{imported.asname or imported.name}.apps")
    bases = {f"{module}.AppConfig" for module in module_aliases}
    return any(
        any(
            (isinstance(base, ast.Name) and base.id in direct_aliases)
            or _expression_path(base) in bases
            for base in class_node.bases
        )
        for class_node in collector.classes
    )


def _has_django_model_signal(text: str) -> bool:
    collector = _django_signal_collector(text)
    if collector is None:
        return False
    direct_aliases: set[str] = set()
    module_aliases: set[str] = set()
    for node in collector.imports:
        if isinstance(node, ast.ImportFrom) and node.module == "django.db.models":
            direct_aliases.update(
                imported.asname or imported.name
                for imported in node.names
                if imported.name == "Model"
            )
        elif isinstance(node, ast.ImportFrom) and node.module == "django.db":
            module_aliases.update(
                imported.asname or imported.name
                for imported in node.names
                if imported.name == "models"
            )
        elif isinstance(node, ast.Import):
            for imported in node.names:
                if imported.name == "django.db.models":
                    module_aliases.add(imported.asname or imported.name)
                elif imported.name == "django":
                    module_aliases.add(
                        f"{imported.asname or imported.name}.db.models"
                    )
    bases = {f"{module}.Model" for module in module_aliases}
    return any(
        any(
            (isinstance(base, ast.Name) and base.id in direct_aliases)
            or _expression_path(base) in bases
            for base in class_node.bases
        )
        for class_node in collector.classes
    )


def _head_has_django_app(root: Path, app_relative: Path) -> bool:
    app_config = _git_show(root, app_relative / "apps.py")
    if app_config is not None and _has_app_config_signal(app_config):
        return True
    model = _git_show(root, app_relative / "models.py")
    if model is not None and _has_django_model_signal(model):
        return True
    model_sources = _git(root, "ls-tree", "-r", "--name-only", "HEAD", "--", str(app_relative / "models"))
    return any(
        source.endswith(".py")
        and (text := _git_show(root, Path(source))) is not None
        and _has_django_model_signal(text)
        for source in model_sources
    )


def _baseline_state(target: Path, path: Path) -> str:
    """Django app identity를 HEAD와 비교해 existing/new/unavailable로 분류한다."""
    root = _git_root(target)
    if root is None:
        return "unavailable"
    try:
        rel = path.resolve().relative_to(root)
    except ValueError:
        return "unavailable"
    return "existing" if _head_has_django_app(root, rel) else "new"


def run_change_set(target: Path) -> list[str]:
    """baseline(HEAD) 대비 변경 파일 = tracked diff ∪ untracked 신규 ([E2])."""
    tracked = _git(target, "diff", "HEAD", "--name-only")
    untracked = _git(target, "ls-files", "--others", "--exclude-standard")
    return sorted(set(tracked) | set(untracked))


def _py_files(target: Path) -> list[Path]:
    return [
        p for p in target.rglob("*.py")
        if ".venv" not in p.relative_to(target).parts
        and "__pycache__" not in p.relative_to(target).parts
        and "site-packages" not in p.relative_to(target).parts
        and "migrations" not in p.relative_to(target).parts
    ]


def _rel(target: Path, p: Path) -> str:
    try:
        return str(p.relative_to(target))
    except ValueError:
        return str(p)


def _find_apps(target: Path) -> list[Path]:
    """실제 AppConfig 또는 Django Model 상속이 있는 로컬 app 디렉터리."""
    apps: set[Path] = set()
    for ap in target.rglob("apps.py"):
        relative_parts = ap.relative_to(target).parts
        if {".venv", "venv", "__pycache__", "site-packages", "migrations"} & set(relative_parts):
            continue
        try:
            text = ap.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue
        if _has_app_config_signal(text):
            apps.add(ap.parent)
    for model in target.rglob("*.py"):
        relative = model.relative_to(target)
        if {".venv", "venv", "__pycache__", "site-packages", "migrations"} & set(relative.parts):
            continue
        if model.name != "models.py" and model.parent.name != "models":
            continue
        try:
            text = model.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue
        if _has_django_model_signal(text):
            apps.add(model.parent if model.name == "models.py" else model.parent.parent)
    return sorted(apps)


def _standard_application_index(target: Path, path: Path) -> int | None:
    try:
        parts = path.relative_to(target).parts
    except ValueError:
        return None
    if parts and parts[0] == "application":
        return 0
    if len(parts) >= 2 and parts[:2] == ("src", "application"):
        return 1
    return None


def _is_root_app(target: Path, app: Path) -> bool:
    try:
        return len(app.relative_to(target).parts) == 1
    except ValueError:
        return False


def _head_has_standard_application_container(target: Path) -> bool:
    root = _git_root(target)
    if root is None:
        return False
    candidates = (target / "application", target / "src" / "application")
    for candidate in candidates:
        try:
            relative = candidate.resolve(strict=False).relative_to(root)
        except ValueError:
            continue
        try:
            result = subprocess.run(
                ["git", "-C", str(root), "cat-file", "-e", f"HEAD:{relative.as_posix()}"],
                capture_output=True,
                text=True,
                check=False,
            )
        except FileNotFoundError:
            continue
        if result.returncode == 0:
            return True
    return False


def _has_established_root_app_convention(target: Path, apps: list[Path]) -> bool:
    uses_standard_layout = (target / "application").is_dir() or (
        target / "src" / "application"
    ).is_dir() or _head_has_standard_application_container(target)
    return not uses_standard_layout and any(
        _is_root_app(target, app) and _baseline_state(target, app) == "existing"
        for app in apps
    )


def _emit(item: str, signal: str, note: str, evidence: list[str]) -> None:
    print(f"\n[{item}] {signal} — {note}")
    for e in evidence[:12]:
        print(f"    {e}")
    if len(evidence) > 12:
        print(f"    … (+{len(evidence) - 12} more)")


def check_sh1(target: Path, apps: list[Path]) -> None:
    """SH-1: 확립 관례가 없을 때 신규 app은 application/ 기본 위치를 쓴다."""
    states = [(a, _baseline_state(target, a)) for a in apps]
    root_convention = _has_established_root_app_convention(target, apps)
    bad = [
        _rel(target, app)
        for app, state in states
        if state == "new"
        and _standard_application_index(target, app) is None
        and not (root_convention and _is_root_app(target, app))
    ]
    unknown = [
        _rel(target, app)
        for app, state in states
        if state == "unavailable" and _standard_application_index(target, app) is None
    ]
    grandfathered = [
        _rel(target, app)
        for app, state in states
        if state == "existing" and _standard_application_index(target, app) is None
    ]
    if bad:
        _emit("SH-1 컨테이너", "FAIL-신호", "baseline에 없던 신규 앱이 application/ 밖", bad)
    elif unknown:
        _emit("SH-1 컨테이너", "NA/주의", "baseline 불명: 기존 위치만으로 FAIL 금지", unknown)
    else:
        new_count = sum(state == "new" for _, state in states)
        _emit(
            "SH-1 컨테이너",
            "PASS-신호",
            f"신규 앱 {new_count}개가 표준 위치 또는 확립된 root 관례; baseline 기존 app은 grandfather",
            [f"grandfather: {path}" for path in grandfathered],
        )


def check_sh2(target: Path, apps: list[Path]) -> None:
    """SH-2: only newly created BCs are required to have four layers."""
    findings = []
    unknown = []
    checked = 0
    for a in apps:
        state = _baseline_state(target, a)
        if state == "existing":
            continue
        if state == "unavailable":
            unknown.append(_rel(target, a))
            continue
        application_index = _standard_application_index(target, a)
        if application_index is None:
            continue
        checked += 1
        # 앱 컨텍스트 루트 = application/<bc>/
        relative_parts = a.relative_to(target).parts
        bc_root = target.joinpath(*relative_parts[: application_index + 2])
        missing = [L for L in LAYERS if not (bc_root / L).is_dir()]
        if missing:
            findings.append(f"{_rel(target, bc_root)}: 누락 {missing}")
    if findings:
        _emit("SH-2 4계층", "FAIL-신호", "신규 BC의 4계층 미완", findings)
    elif unknown:
        _emit("SH-2 4계층", "NA/주의", "baseline 불명: 신규 여부를 의미 레인에서 확인", unknown)
    else:
        _emit("SH-2 4계층", "PASS-신호", f"신규 BC 후보 {checked}개의 4계층 존재", [])


def check_sh4(target: Path, apps: list[Path]) -> None:
    """SH-4: 확립 관례가 없을 때 신규 Django app은 infra_layer/django_*를 쓴다."""
    bad: list[str] = []
    unknown: list[str] = []
    grandfathered: list[str] = []
    root_convention = _has_established_root_app_convention(target, apps)
    for owner in apps:
        state = _baseline_state(target, owner)
        if state == "existing":
            grandfathered.append(_rel(target, owner))
            continue
        if state == "unavailable":
            unknown.append(_rel(target, owner))
            continue
        ok = (
            root_convention and _is_root_app(target, owner)
        ) or (
            owner.parent.name == "infra_layer"
            and owner.name.startswith("django_")
        )
        if not ok:
            bad.append(f"{_rel(target, owner)} (신규 app, infra_layer/django_* 밖)")
    if bad:
        _emit("SH-4 Django앱위치", "FAIL-신호", "신규 Django app owner가 표준 위치 밖", bad)
    elif unknown:
        _emit("SH-4 Django앱위치", "NA/주의", "baseline/app 소유 불명: 위치만으로 FAIL 금지", unknown)
    else:
        _emit(
            "SH-4 Django앱위치",
            "PASS-신호",
            "신규 app은 표준 위치; baseline 기존 persistence app은 원위치 보존",
            [f"grandfather: {path}" for path in sorted(set(grandfathered))],
        )


def check_sh7(target: Path) -> None:
    """SH-7: port/ 디렉터리 부모가 domain_layer 인가."""
    ports = [
        directory
        for directory in target.rglob("port")
        if directory.is_dir()
        and ".venv" not in directory.relative_to(target).parts
    ]
    bad = [
        _rel(target, directory)
        for directory in ports
        if "domain_layer" not in directory.relative_to(target).parts
    ]
    if not ports:
        _emit("SH-7 포트위치", "NA", "port/ 디렉터리 없음", [])
    elif bad:
        _emit("SH-7 포트위치", "FAIL-신호", "port/가 domain_layer 밖", bad)
    else:
        _emit("SH-7 포트위치", "PASS-신호", f"{len(ports)} port/ 전부 domain_layer 하위", [])


def check_sh9(target: Path, apps: list[Path]) -> None:
    """SH-9: 한 앱에 test/ + tests/ (또는 tests.py + tests/) 공존."""
    findings = []
    search_roots = apps or [target]
    seen = set()
    for a in search_roots:
        for parent in {a, *[p for p in a.rglob("*") if p.is_dir()]}:
            relative_parts = parent.relative_to(target).parts
            if ".venv" in relative_parts or "__pycache__" in relative_parts:
                continue
            key = str(parent)
            if key in seen:
                continue
            seen.add(key)
            has_test_dir = (parent / "test").is_dir()
            has_tests_dir = (parent / "tests").is_dir()
            has_tests_py = (parent / "tests.py").is_file()
            has_test_py = (parent / "test.py").is_file()
            if (has_test_dir and has_tests_dir) or (has_tests_py and has_tests_dir) or (has_test_py and has_test_dir):
                findings.append(f"{_rel(target, parent)}: test/tests 레이아웃 공존")
    if findings:
        _emit("SH-9 단일레이아웃", "FAIL-신호", "두 테스트 레이아웃 공존", findings)
    else:
        _emit("SH-9 단일레이아웃", "PASS-신호", "테스트 레이아웃 공존 없음", [])


def check_sd7(target: Path) -> None:
    """SD-7(FAIL방향): ACL/OHS 경로 *밖*에서 타 BC domain_layer/infra_layer 직접 import.

    미스캘리브 교정(2026-06-02): `infra_layer/acl/` 의 미이주 ACL 이 업스트림(타 BC) 모델·리포를
    import·번역하는 건 표준 §2(houserules `final.md` §2 컨텍스트 간 통신: "OHS 미이주·행잠금 불가피 시 ACL로
    명시 — 구현(업스트림 모델·예외 번역)은 infra_layer/acl/ 에 가둔다") **명시 허용**이라 FAIL-신호가
    아니다 — '주의'로만 분리한다(도메인누수=포트 ABC 미준수·OHS 존재 시 미경유 점검은 의미레인).
    FAIL-신호는 ACL *밖*(도메인/응용/presentation)의 직접 import 만. PASS(OHS '정당성')도 의미레인.
    [근거: smoke4-claude·p1a-v3-claude 의 ACL 을 결정신호가 거짓양성 FAIL 로 잡던 미스캘리브 교정.]"""
    findings = []
    acl_notes = []
    imp_re = re.compile(r"^\s*(?:from|import)\s+application\.([A-Za-z_]\w*)\.(domain_layer|infra_layer)")
    for f in _py_files(target):
        parts = f.relative_to(target).parts
        if any(p in ("test", "tests") or p.startswith("test") for p in parts):
            continue  # 통합테스트의 타 BC import는 정당 — 프로덕션 코드만 본다
        own_bc = None
        if "application" in parts:
            i = parts.index("application")
            if i + 1 < len(parts):
                own_bc = parts[i + 1]
        is_acl = "infra_layer" in parts and "acl" in parts  # 미이주 ACL 어댑터(표준 §2 허용)
        try:
            lines = f.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for n, ln in enumerate(lines, 1):
            m = imp_re.match(ln)
            if m and m.group(1) != own_bc:  # 타 BC 의 내부 계층 직접 import
                if is_acl:
                    acl_notes.append(f"{_rel(target, f)}:{n}  {ln.strip()}")
                else:
                    findings.append(f"{_rel(target, f)}:{n}  {ln.strip()}")
    if findings:
        _emit("SD-7 컨텍스트통신", "FAIL-신호", "ACL 밖(도메인/응용/presentation)에서 타 BC domain_layer/infra_layer 직접 import", findings)
    else:
        _emit("SD-7 컨텍스트통신", "PASS-신호(결정)", "ACL 밖 타 BC 내부계층 직접 import 0 (OHS '정당성'은 의미레인)", [])
    if acl_notes:
        _emit("SD-7 ACL직접통합", "주의(표준§2 허용)", "infra_layer/acl/ 미이주 ACL의 업스트림 import — houserules final.md §2 컨텍스트 간 통신 허용. 의미레인이 도메인누수(포트 ABC)·OHS존재 점검", acl_notes)


def check_sd3(target: Path) -> None:
    """SD-3: infra 리포지토리 CAS .filter/.update 에 stock__gte= 등 비즈판정 복제."""
    findings = []
    # CAS WHERE 에 비즈판정 복제: stock__gte=<변수>(예 quantity) = 판정 복제(FAIL).
    # stock__gte=0 / condition=/CheckConstraint = DB constraint(정당) → 제외.
    # RHS가 변수면 biz, 리터럴 0/숫자면 constraint. 멀티라인 .filter() 도 잡힘(독립 줄 매칭).
    biz_re = re.compile(r"\b(stock|qty|quantity|amount|count)\w*__(gte|gt|lte|lt)\s*=\s*([^\s,)#]+)")
    skip_re = re.compile(r"condition\s*=|CheckConstraint|constraint\s*=")
    for f in _py_files(target):
        # 평면 services/ 도 포함(코덱스 CAS는 catalog/services/ 에 있음) — repository·service·infra 전부
        low = str(f).lower()
        if not ("infra_layer" in f.relative_to(target).parts or "repository" in low or "service" in low or "published_service" in low):
            continue
        try:
            lines = f.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for n, ln in enumerate(lines, 1):
            m = biz_re.search(ln)
            if not m or skip_re.search(ln):
                continue
            rhs = m.group(3).rstrip(",)")
            if rhs.isdigit():  # __gte=0 등 리터럴 = constraint 성격, 판정 복제 아님
                continue
            findings.append(f"{_rel(target, f)}:{n}  {ln.strip()}")
    if findings:
        _emit("SD-3 무복제", "FAIL-신호(후보)", "infra에 비즈판정(stock__gte 등) 복제 — DB CHECK constraint는 정당(거짓양성 가능, 의미레인 확인)", findings)
    else:
        _emit("SD-3 무복제", "PASS-신호", "infra CAS에 비즈판정 복제 미검출", [])


def check_nj(target: Path) -> None:
    """NJ-1 스택 / NJ-4 status 선언."""
    ninja_hits, jsonresp_hits, response_decls, single_status = [], [], [], []
    route_re = re.compile(r"@\w+\.(get|post|put|patch|delete)\(")
    resp_re = re.compile(r"response\s*=\s*\{")
    for f in _py_files(target):
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        lines = text.splitlines()
        for n, ln in enumerate(lines, 1):
            if re.search(r"\bNinjaAPI\b|\bNinjaExtraAPI\b|\bRouter\(|@?api_controller\b|register_controllers\b|from ninja", ln):
                ninja_hits.append(f"{_rel(target, f)}:{n}")
            if re.search(r"\bJsonResponse\(", ln):
                jsonresp_hits.append(f"{_rel(target, f)}:{n}  {ln.strip()}")
        # NJ-4: route 데코레이터 블록에 response={...} 다중 status
        for n, ln in enumerate(lines, 1):
            if route_re.search(ln):
                block = "\n".join(lines[n - 1:n + 12])
                rm = resp_re.search(block)
                if rm:
                    body = block[rm.end():rm.end() + 300]
                    codes = re.findall(r"\b([1-5]\d\d)\s*:", body)
                    if len(set(codes)) >= 2:
                        response_decls.append(f"{_rel(target, f)}:{n} status={sorted(set(codes))}")
                    else:
                        single_status.append(f"{_rel(target, f)}:{n} status={sorted(set(codes)) or '없음/Out만'}")
    if ninja_hits:
        _emit("NJ-1 스택", "PASS-신호", f"ninja(NinjaAPI/Router) {len(ninja_hits)}곳"
              + ("; ⚠ JsonResponse 본문도 존재→SD-6/G3 의미레인" if jsonresp_hits else ""),
              ninja_hits[:4] + jsonresp_hits[:4])
    elif jsonresp_hits:
        _emit("NJ-1 스택", "FAIL-신호", "신규 JSON API가 plain JsonResponse(ninja 부재)", jsonresp_hits)
    else:
        _emit("NJ-1 스택", "NA", "HTTP/JSON operation 미검출(S-NINJA N/A 후보)", [])
    if response_decls:
        _emit("NJ-4 status선언", "PASS-신호", "다중 status response={...} 선언", response_decls)
    elif single_status:
        _emit("NJ-4 status선언", "FAIL-신호", "단일/누락 status 선언(OpenAPI 가시성↓)", single_status)
    else:
        _emit("NJ-4 status선언", "NA", "ninja route 데코레이터 미검출", [])


def main() -> int:
    args = [a for a in sys.argv[1:]]
    mode_rcs = "--run-change-set" in args
    args = [a for a in args if not a.startswith("--")]
    target = Path(args[0]).resolve() if args else Path.cwd()
    if not target.is_dir():
        print(f"usage: check-structure.py [--run-change-set] [TARGET_DIR]", file=sys.stderr)
        return 1

    if mode_rcs:
        rcs = run_change_set(target)
        print(f"# run-change-set (HEAD 대비 tracked∪untracked) — {len(rcs)} 파일")
        for f in rcs:
            print(f)
        return 0

    print(f"# EVAL-METHOD §1.1 결정 레인 리포트 — {target}")
    print(f"# (리포터: 신호+줄인용만. 집계·치명게이트=§2. 의미 레인은 이 출력에 blind.)")
    apps = _find_apps(target)
    print(f"# 검출 앱(actual AppConfig/Model): {[_rel(target, a) for a in apps]}")
    check_sh1(target, apps)
    check_sh2(target, apps)
    check_sh4(target, apps)
    check_sh7(target)
    check_sh9(target, apps)
    check_sd7(target)
    check_sd3(target)
    check_nj(target)
    print("\n# (SD-7 PASS방향 'OHS인가'·Q-5 명령/보고·SD-6 presentation = 의미 레인 §1.1.M/§1.2)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
