#!/usr/bin/env python3
"""dddjango 테스트 규율 검사기 — pytest 바인딩 + `test/` 구조·settings 환경축의 결정적 백스톱.

세 슬라이스를 강제한다.

⑴ 현행 관할 — pytest ↔ Django settings 바인딩 (무변 · 전면화):
  pytest 설정 파일(pytest.ini·tox.ini·setup.cfg·pyproject.toml)은 *존재* 하는데
  pytest-django 를 Django settings 에 묶지 못하면 테스트 수집이 조용히 실패한다(0
  collected). 설정이 아예 없는 것(manage.py test 관례)은 위반이 아니다. 바인딩 성립:
  `DJANGO_SETTINGS_MODULE`·addopts `--ds=`·`ds` 키·`django_find_project`·pytest-env
  `env`·conftest 의 Django 셋업. touched 한정을 걷고 전 설정을 본다 — 깨진 바인딩은
  언제 커밋됐든 지금 깨져 있다(기존 코드도 면제가 아니라 빚).

⑵ 트리 개정 명세 몫 — `test/` 구조 (트리 105~111행 · D56):
  #383/#384 `test/` 의 직계 자식은 다섯뿐 — `unit/`·`integration/`·`e2e/`(«테스트» —
       안이 자유)·`factories/`·`fake/`(«재료» — 규칙이 산다). 직계 파일은
       `conftest.py`·`__init__.py` 만(#596 — 파일 이름은 pytest 소유라 폐쇄(#490)
       비대상, 그래서 이 검사기는 test 파일 «이름»을 검사하지 않는다).
  #385 BC `test/` 에는 그 BC 의 테스트만 — `application.<타BC>.…` import 금지.
  #387 `test/unit/` 은 DB 를 켜지 않는다(`django_db`·django.test TestCase·`.objects`).
  #388 `test/unit/` 은 `factories/` 를 import 하지 않는다(가짜 구현은 `fake/`).
  #389 `test/integration/` 은 진짜 DB 를 켠다 — DB 신호가 하나도 없는 test 파일은 위반.
  #390 `test/e2e/` 는 입구를 거친다 — TestClient/Client·cron_job 신호가 없으면 위반.
  #391 `factories/` 는 `integration/` «안»이 아니라 그 형제다.
  #392 `factories/` 에는 factory_boy 픽스처만 온다.

⑶ 트리 개정 명세 몫 — `<project>/settings/` 환경축 (트리 139·140행):
  #445 갈리는 축은 환경 하나뿐 — 기능별 분할 파일(celery.py·logging.py 등) 금지.
  #446 «환경 하나 = 파일 하나» — base·local·production·test 는 예시(목록 열림 — T64).
       온전한 환경 이름(staging 등)은 허용하고 «약어»(prod·stg·dev …)만 위반이다.
  #447 공통 설정은 `base` 에 두고 환경 파일은 그것을 가져와 덮어쓴다.

이관 계약 (명세 조각 ⓐ): 대상 0건 가드(#74) · 분석 실패는 exit 1(fail-open 금지 —
옛 판의 «어떤 예외든 exit 0»을 걷었다).

사용법: check-test-config.py [TARGET_DIR]   (기본: 현재 디렉터리)
종료코드: 0=clean(또는 표준 미채택) · 1=사용/분석 오류 · 2=blocker(발견 출력)
구조화 레코드: DJR_FINDINGS_JSON=<경로> 지정 시 findings.py(공용 모듈)가 JSON lines 를
추가 방출한다 — 라인 출력·exit 의미론 무변(T0 B2).
"""
from __future__ import annotations

import ast
import configparser
import re
import sys

import checker_target
from findings import Findings
from pathlib import Path

try:
    import standard_tree as tree
except ImportError:  # 데이터 모듈 없이는 판정 불가 — fail-closed(분석 오류)
    print("분석 오류: standard_tree.py 를 찾지 못했다 — 검사기와 같은 폴더에 있어야 한다", file=sys.stderr)
    sys.exit(1)

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:  # 3.10 이하 — 텍스트 스캔 fallback
    tomllib = None  # type: ignore[assignment]

SKIP_DIRS = {
    ".venv", "venv", "site-packages", "node_modules", ".git", "__pycache__", ".dddjango",
    "build", "dist", ".tox", ".mypy_cache", ".pytest_cache", ".eggs",
}
DJANGO_APP_MARKERS = ("models.py", "apps.py", "views.py", "admin.py")
NEW_LAYERS = {"driving_layer", "application_layer", "domain_layer", "driven_layer"}

TEST_CHILDREN = {"unit", "integration", "e2e", "factories", "fake"}
TEST_DIRECT_FILES = {"conftest.py", "__init__.py"}

# settings/ 파일 이름 — 약어(#446 · 규율 ④)와 기능 분할(#445) 블록리스트.
ABBREV_BAN = {"prod": "production", "dev": "local", "stg": "staging", "stag": "staging", "loc": "local", "tst": "test"}
FEATURE_BAN = {
    "celery", "database", "db", "logging", "cache", "storage", "email",
    "auth", "api", "static", "cors", "rest", "drf", "security",
}

INI_CONFIGS = {"pytest.ini": "[pytest]", "tox.ini": "[pytest]", "setup.cfg": "[tool:pytest]"}
PYPROJECT_SECTION = "[tool.pytest.ini_options]"
BINDING_LINE_RE = re.compile(r"^\s*(?:DJANGO_SETTINGS_MODULE|ds|django_find_project)\s*[=:]", re.MULTILINE)
BINDING_SUBSTRINGS = ("DJANGO_SETTINGS_MODULE", "--ds=", "--ds ", "django_find_project")
CONFTEST_MARKERS = (
    "DJANGO_SETTINGS_MODULE", "django.setup(", "settings.configure(", "pytest_configure",
)

DB_TEST_BASES = {"TestCase", "TransactionTestCase", "LiveServerTestCase"}
ENTRANCE_NAMES = {"Client", "TestClient", "TestAsyncClient", "APIClient"}


def _has_adoption_signal(bc_dir: Path) -> bool:
    """채택 신호원 둘(#78) — check-layer-skeleton 과 같은 판."""
    has_layer = any((bc_dir / n).is_dir() for n in NEW_LAYERS)
    has_marker = any((bc_dir / m).is_file() for m in DJANGO_APP_MARKERS) or any(
        p.is_dir() and p.name.startswith("django_") for p in bc_dir.iterdir()
    )
    return has_layer or has_marker


def _find_bcs(target: Path) -> list[Path]:
    bcs: list[Path] = []
    for c in target.rglob("application"):
        if not c.is_dir() or set(c.parts) & SKIP_DIRS:
            continue
        bcs.extend(p for p in sorted(c.iterdir()) if p.is_dir() and not p.name.startswith("."))
    return bcs


def _read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


# ── 슬라이스 ⑴ — pytest ↔ Django settings 바인딩 ────────────────────────────

def _text_has_binding(text: str) -> bool:
    if any(s in text for s in BINDING_SUBSTRINGS):
        return True
    return BINDING_LINE_RE.search(text) is not None


def _ds_in_addopts(addopts: object) -> bool:
    if isinstance(addopts, str):
        text = addopts
    elif isinstance(addopts, (list, tuple)):
        text = " ".join(str(x) for x in addopts)
    else:
        return False
    return "--ds=" in text or "--ds " in text


def _env_has_ds(env: object) -> bool:
    if isinstance(env, str):
        text = env
    elif isinstance(env, (list, tuple)):
        text = " ".join(str(x) for x in env)
    else:
        return False
    return "DJANGO_SETTINGS_MODULE" in text


def _toml_has_binding(path: Path) -> bool | None:
    """pyproject.toml — pytest 섹션이 없으면 None(대상 아님)."""
    text = _read_text(path)
    if text is None:
        return None
    if tomllib is not None:
        try:
            data = tomllib.loads(text)
        except Exception:
            return _text_has_binding(text) or None  # 파싱 실패 — 텍스트 신호가 없으면 판정 유보
        section = data.get("tool", {}).get("pytest", {}).get("ini_options")
        if not isinstance(section, dict):
            return None
        if "DJANGO_SETTINGS_MODULE" in section or "django_find_project" in section:
            return True
        if str(section.get("ds", "")).strip():
            return True
        if _ds_in_addopts(section.get("addopts")) or _env_has_ds(section.get("env")):
            return True
        return False
    if PYPROJECT_SECTION not in text:
        return None
    return _text_has_binding(text)


def _ini_has_binding(path: Path, section_header: str) -> bool | None:
    text = _read_text(path)
    if text is None or section_header not in text:
        return None
    section_name = section_header.strip("[]")
    parser = configparser.ConfigParser()
    try:
        parser.read_string(text)
    except configparser.Error:
        return _text_has_binding(text)
    if not parser.has_section(section_name):
        return None
    items = {k.lower(): (v or "") for k, v in parser.items(section_name)}
    if "django_settings_module" in items or "django_find_project" in items:
        return True
    if items.get("ds", "").strip():
        return True
    if _ds_in_addopts(items.get("addopts", "")) or _env_has_ds(items.get("env")):
        return True
    # 같은 파일의 다른 섹션이 settings 를 묶을 수 있다(tox `[testenv] setenv`).
    return _text_has_binding(text)


def _conftest_configures_django(root: Path) -> bool:
    for path in root.rglob("conftest.py"):
        if set(path.parts) & SKIP_DIRS:
            continue
        text = _read_text(path)
        if text is not None and any(m in text for m in CONFTEST_MARKERS):
            return True
    return False


def _find_pytest_configs(root: Path) -> list[tuple[Path, bool]]:
    """(path, has_binding) — pytest 설정 섹션을 가진 파일 전부(전면 · touched 무관)."""
    out: list[tuple[Path, bool]] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or set(path.parts) & SKIP_DIRS:
            continue
        if path.name == "pyproject.toml":
            has = _toml_has_binding(path)
        elif path.name in INI_CONFIGS:
            has = _ini_has_binding(path, INI_CONFIGS[path.name])
        else:
            continue
        if has is not None:
            out.append((path, has))
    return out


def _check_binding(root: Path, configs: list[tuple[Path, bool]], out: Findings) -> None:
    if not configs:
        return  # pytest 미도입(manage.py test 관례) — 위반이 아니다
    if any(has for _, has in configs) or _conftest_configures_django(root):
        return
    for path, _ in configs:
        out.add("바인딩", path.relative_to(root), "pytest 설정에 Django settings 바인딩이 없다 — `DJANGO_SETTINGS_MODULE`(또는 `--ds=`/`django_find_project`/conftest 셋업)이 없으면 수집이 조용히 실패한다(0 collected)")


# ── 슬라이스 ⑵ — BC test/ 구조 ──────────────────────────────────────────────

def _imports_of(mod: ast.Module) -> list[str]:
    out: list[str] = []
    for node in ast.walk(mod):
        if isinstance(node, ast.Import):
            out.extend(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            out.append(node.module)
    return out


def _db_signals(mod: ast.Module) -> bool:
    for node in ast.walk(mod):
        if isinstance(node, ast.Attribute) and node.attr in ("django_db", "objects"):
            return True
        if isinstance(node, ast.Name) and node.id == "django_db":
            return True
        if isinstance(node, ast.ImportFrom) and node.module == "django.test":
            if any(a.name in DB_TEST_BASES or a.name == "Client" for a in node.names):
                return True
    return False


def _entrance_signals(mod: ast.Module) -> bool:
    for node in ast.walk(mod):
        if isinstance(node, (ast.Name, ast.Attribute)):
            nm = node.id if isinstance(node, ast.Name) else node.attr
            if nm in ENTRANCE_NAMES:
                return True
    for p in _imports_of(mod):
        if "cron_job" in p:
            return True
    return False


# pytest-django 의 입구 fixture 관용구(2026-08-12 · 라운드 1′ C1 — 이름 토큰만 보던
# 사각으로 blackbox e2e 5파일이 전부 오탐이었다).
CLIENT_FIXTURES: "frozenset[str]" = frozenset({"client", "async_client"})
# e2e 가 import 하면 «입구 우회» 신호인 자기 BC 구현 칸(#390 검출 보강 — blackbox 는
# 계약만 본다 · acceptance 헌장 「프로덕션 구현 코드를 보지 않는다」).
IMPL_LAYERS: "frozenset[str]" = frozenset(
    {"domain_layer", "application_layer", "driving_layer", "driven_layer", "composition_root"}
)


def _flows_into_call(fn: "ast.FunctionDef | ast.AsyncFunctionDef", names: "set[str]") -> bool:
    """인자가 «Call 로 흐르는가» — 수신자 attr 호출(client.get(...)) 또는 호출 인자
    전달(helper(client)/helper(c=client)). 존재·Load 사용만으로는 신호가 아니다
    (미사용 장식 인자·assert-only 우회 차단 — 적대 리뷰 R1·R2 실측)."""
    for node in ast.walk(fn):
        if not isinstance(node, ast.Call):
            continue
        f = node.func
        if isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name) and f.value.id in names:
            return True
        for a in list(node.args) + [kw.value for kw in node.keywords]:
            if isinstance(a, ast.Name) and a.id in names:
                return True
    return False


def _client_fixture_entrance(mod: ast.Module) -> bool:
    """fixture 관용구 판정은 «all» 이다 — top-level test_* «전부»가 자기 client/async_client
    인자를 Call 로 흘려야 파일이 입구 신호를 얻는다(혼합 파일 은닉 차단 — R5). test 함수가
    0개면 불성립(공허 참 차단)."""
    tests: "list[ast.FunctionDef | ast.AsyncFunctionDef]" = [
        n for n in mod.body
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name.startswith("test_")
    ]
    if not tests:
        return False
    for fn in tests:
        arg_names: "set[str]" = {
            a.arg for a in list(fn.args.posonlyargs) + list(fn.args.args) + list(fn.args.kwonlyargs)
        }
        fixture_args: "set[str]" = arg_names & CLIENT_FIXTURES
        if not fixture_args or not _flows_into_call(fn, fixture_args):
            return False
    return True


def _check_bc_test(bc: Path, bc_rel: Path, out: Findings) -> None:
    test_dir = bc / "test"
    if not test_dir.is_dir():
        return  # 존재는 skeleton #488 소유 — 여기서 중복으로 내지 않는다
    for p in sorted(test_dir.iterdir()):
        if p.name.startswith(".") or p.name == "__pycache__":
            continue
        if p.is_dir():
            if p.name not in TEST_CHILDREN:
                out.add("#384", bc_rel / "test" / p.name, "`test/` 의 자식은 다섯뿐이다 — unit/·integration/·e2e/·factories/·fake/ (#383: 폴더 이름이 «무엇을 켜고 도는가»를 말한다)")
        elif p.name not in TEST_DIRECT_FILES:
            out.add("#384", bc_rel / "test" / p.name, "`test/` 직계 파일은 `conftest.py` 뿐이다 — 테스트는 unit/·integration/·e2e/ 안으로")

    # factories/ 위치(#391) — test/ 직계가 아닌 곳의 factories/
    for p in test_dir.rglob("factories"):
        if p.is_dir() and p.parent != test_dir:
            out.add("#391", bc_rel / p.relative_to(bc), "`factories/` 는 `integration/` 안이 아니라 그 형제로 둔다")

    for f in sorted(test_dir.rglob("*.py")):
        rel_in = f.relative_to(test_dir)
        rel = bc_rel / "test" / rel_in
        try:
            mod = ast.parse(f.read_text(encoding="utf-8"))
        except (SyntaxError, OSError, UnicodeDecodeError):
            continue
        top = rel_in.parts[0] if len(rel_in.parts) > 1 else ""
        imports = _imports_of(mod)
        for p in imports:
            parts = p.split(".")
            if parts[0] == "application" and len(parts) > 1 and parts[1] != bc.name:
                out.add("#385", rel, f"`{p}` import — BC `test/` 에는 그 BC 의 테스트만 온다(타 BC 는 입구로 검사한다)")
        if top == "unit":
            if _db_signals(mod):
                out.add("#387", rel, "`test/unit/` 은 DB 를 켜지 않는다 — 포트 자리에는 `fake/` 의 가짜 구현을 꽂는다")
            if any("factories" in p.split(".") for p in imports):
                out.add("#388", rel, "`test/unit/` 은 `factories/` 를 import 하지 않는다")
        elif top == "integration" and f.name.startswith("test_"):
            if not _db_signals(mod):
                out.add("#389", rel, "`test/integration/` 은 진짜 DB 를 켠다 — DB 신호(django_db·TestCase·.objects)가 없다면 unit/ 자리다")
        elif top == "e2e" and f.name.startswith("test_"):
            if not (_entrance_signals(mod) or _client_fixture_entrance(mod)):
                out.add("#390", rel, "`test/e2e/` 는 입구에서 출구까지 본다 — 입구(TestClient·API·cron_job·client fixture 사용)를 안 거치면 위반이다")
        if top == "e2e":
            for p in imports:
                parts_own = p.split(".")
                if (
                    parts_own[0] == "application" and len(parts_own) > 2
                    and parts_own[1] == bc.name and parts_own[2] in IMPL_LAYERS
                ):
                    out.add("#390", rel, f"`{p}` import — `test/e2e/` 는 blackbox 다(입구에서 출구까지 한 흐름 통째로): 자기 BC 구현 칸 import 는 입구 우회 신호다")
        if top == "factories" and f.name != "__init__.py":
            has_factory = any(p == "factory" or p.startswith("factory.") for p in imports) or any(
                isinstance(n, ast.ClassDef) and any(str(getattr(b, "attr", getattr(b, "id", ""))).endswith("Factory") for b in n.bases)
                for n in ast.walk(mod)
            )
            if not has_factory:
                out.add("#392", rel, "`factories/` 에는 factory_boy 픽스처만 온다 — 다른 재료는 `fake/` 또는 테스트 안으로")


# ── 슬라이스 ⑶ — <project>/settings/ 환경축 ─────────────────────────────────

def _find_settings_dirs(root: Path) -> list[Path]:
    out: list[Path] = []
    for p in root.rglob("settings"):
        if not p.is_dir() or set(p.parts) & SKIP_DIRS:
            continue
        if "application" in p.parts:
            continue  # BC 안 settings 는 이 축이 아니다(있다면 skeleton 몫)
        out.append(p)
    return sorted(out)


def _base_imported(mod: ast.Module) -> bool:
    for node in ast.walk(mod):
        if isinstance(node, ast.ImportFrom):
            m = node.module or ""
            if m == "base" or m.endswith(".base"):
                return True
            if node.level >= 1 and (m == "base" or any(a.name == "base" for a in node.names)):
                return True
    return False


def _check_settings_dir(d: Path, root: Path, out: Findings) -> None:
    for f in sorted(d.glob("*.py")):
        rel = f.relative_to(root)
        stem = f.stem
        if stem in ("__init__", "base"):
            continue
        if stem in ABBREV_BAN:
            out.add("#446", rel, f"환경 파일 이름에 약어를 쓰지 않는다 — `{stem}` 이 아니라 `{ABBREV_BAN[stem]}`")
            continue
        if stem in FEATURE_BAN:
            out.add("#445", rel, f"`settings/` 에서 갈리는 축은 환경 하나뿐이다 — 기능별 파일(`{stem}.py`)로 쪼개지 않는다(공통 설정은 `base.py` 로)")
            continue
        try:
            mod = ast.parse(f.read_text(encoding="utf-8"))
        except (SyntaxError, OSError, UnicodeDecodeError):
            continue
        if not _base_imported(mod):
            out.add("#447", rel, "환경 파일은 `base` 를 가져와 덮어쓴다 — `from .base import *` 가 없다")


def main(argv: list[str]) -> int:
    if len(argv) > 1:
        print(f"사용법: {Path(sys.argv[0]).name} [TARGET_DIR]", file=sys.stderr)
        return 1
    target = Path(argv[0]).resolve() if argv else Path.cwd()
    bad_target_reason = checker_target.bc_shaped_target_reason(target)
    if bad_target_reason is not None:
        print(f"사용 오류: {bad_target_reason}", file=sys.stderr)
        return 1
    if not target.is_dir():
        print(f"사용 오류: 디렉터리가 아니다 — {target}", file=sys.stderr)
        return 1

    try:
        bcs = _find_bcs(target)
        configs = _find_pytest_configs(target)
        settings_dirs = _find_settings_dirs(target)
        test_dirs = [bc / "test" for bc in bcs if (bc / "test").is_dir()]

        adopted = any(_has_adoption_signal(b) for b in bcs)
        # 대상 0건 가드(#74) — 채택 신호는 있는데 이 검사기의 대상이 전부 0건이면 exit 2.
        if adopted and not test_dirs and not configs and not settings_dirs:
            print("blocker: 채택 신호는 있는데 test/·pytest 설정·settings 대상이 전부 0건이다 — 조용한 무동작을 금지한다(#74)")
            return 2
        if not adopted and not configs and not settings_dirs:
            print("표준 레이아웃 미채택 — 검사 대상 없음 (clean)")
            return 0

        findings = Findings()
        _check_binding(target, configs, findings)
        for bc in bcs:
            _check_bc_test(bc, bc.relative_to(target), findings)
        for d in settings_dirs:
            _check_settings_dir(d, target, findings)
    except Exception as exc:  # 분석 실패는 조용한 통과가 아니다 — fail-closed
        print(f"분석 오류: {exc}", file=sys.stderr)
        return 1

    if findings:
        print(f"blocker {len(findings)}건 — 테스트·settings 규율 위반 (트리 105~111·139·140행)")
        for f in findings:
            print(" ", f)
        return 2
    print(f"clean — test/ {len(test_dirs)}곳 · pytest 설정 {len(configs)}개 · settings {len(settings_dirs)}곳 규율 일치 (standard_tree {tree.SOURCE_SHA})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
