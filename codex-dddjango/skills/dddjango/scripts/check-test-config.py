#!/usr/bin/env python3
"""dddjango pytest 러너 설정 깨짐 결정적 백스톱 (Phase 2 러너 준비 §6.2 집행).

pytest 설정 파일은 *존재* 하는데 pytest-django 를 Django settings 에 묶지 못하는
*결정적 깨짐* 을 적출한다 — 이 상태에선 `DJANGO_SETTINGS_MODULE` 미설정으로 ORM/모델
import 가 `ImproperlyConfigured` 로 죽어 **테스트 수집이 조용히 실패**하고, acceptance-tester
의 깨끗한 Red 가 성립하지 않는다. Phase 2 의 러너 준비 단계가 greenfield 에 pytest 를 깔며
`[tool.pytest.ini_options]` 에 실제 `DJANGO_SETTINGS_MODULE` 을 박도록 명령하는데, 그 산출이
설정만 만들고 settings 바인딩을 빠뜨린 회귀를 결정적으로 막는다.

대상 설정(이번 작업이 새로 만들/수정한 것만):
  - `pytest.ini`  ([pytest] 섹션)
  - `setup.cfg`   ([tool:pytest] 섹션)
  - `pyproject.toml` ([tool.pytest.ini_options])
  - `tox.ini`     ([pytest] 섹션)

*왜 결정적 백스톱인가* — 설정-없음(manage.py test 관례)과 설정-있으나-바인딩-없음은 둘 다
`manage.py test` 로는 Green 처럼 보일 수 있고(pytest 미경유), pytest 수집 실패는 "0 tests
collected" 류로 조용히 지나간다. discipline-reviewer 가 프로즈로 잡으려면 회피 표면이 된다 —
이 스크립트가 그 절반을 결정적으로 메운다(고정밀·저-recall, 거짓양성 ≈0).

거짓양성 ≈ 0 — 다음은 *위반이 아니라* 전부 통과(발화 안 함):
  - **pytest 설정이 아예 없음** — 프로젝트가 `manage.py test`/Django TestCase 관례를 쓰는
    *존중 대상* 경우다(Phase 2 러너 준비가 명시적으로 존중). 설정 파일이 없으면 무조건 exit 0.
    (이 스크립트는 "pytest 를 도입했는데 깨졌다" 만 본다 — "pytest 를 안 썼다" 는 위반이 아니다.)
  - **설정 자체에 `DJANGO_SETTINGS_MODULE` 이 있음** — `DJANGO_SETTINGS_MODULE = a.b.settings`
    또는 addopts/명령행의 `--ds=a.b.settings`(pytest-django 별칭 `ds`)로 바인딩됐으면 정상.
  - **conftest 가 Django 를 셋업함** — 레포 어디든 `conftest.py` 가
    `os.environ.setdefault("DJANGO_SETTINGS_MODULE"`, `django.setup(`, `settings.configure(`,
    또는 `pytest_configure` 로 Django 를 구성하면 정상 경로다(설정 파일 밖 바인딩).
  - **`django_find_project` / `addopts --ds=`** — pytest-django 의 프로젝트 자동탐색/명령행
    settings 지정으로도 바인딩이 성립한다.
  - 이번 작업이 건드린 설정만 본다(git 신규/수정·미추적). 기존에 커밋된 채 안 건드린 설정은
    존중(brownfield) → 건너뜀. git 판정 불가면 스킵(거짓양성 회피).
  - 파싱 실패·파일 부재 등 어떤 예외든 **fail-open**(exit 0) — 이건 정밀 그물이지 정확성
    오라클이 아니다. 못 읽으면 막지 않는다(잘못된 차단보다 미차단을 택한다).

사용법: check-test-config.py [TARGET_DIR]   (기본 TARGET_DIR=현재 디렉터리)
종료코드: 0=clean(또는 설정 없음·판정 불가·파싱 실패), 2=blocker(발견 출력), 1=사용 오류.
"""
from __future__ import annotations

import configparser
import re
import subprocess
import sys
from pathlib import Path

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:  # pragma: no cover - 3.10 이하 fallback
    tomllib = None  # type: ignore[assignment]

SKIP_DIRS = {
    ".venv", "venv", "site-packages", "node_modules", ".git", "__pycache__",
    "build", "dist", ".tox", ".mypy_cache", ".pytest_cache", ".eggs",
}

# pytest 설정 파일 이름과 그 안에서 pytest 설정을 담는 섹션 헤더.
# pyproject.toml 은 TOML 이라 별도 처리(아래).
INI_CONFIGS = {
    "pytest.ini": "[pytest]",
    "tox.ini": "[pytest]",
    "setup.cfg": "[tool:pytest]",
}
PYPROJECT_SECTION = "[tool.pytest.ini_options]"

# 설정 *텍스트* 에 이 중 하나라도 있으면 Django settings 바인딩이 성립한 것으로 본다(고정밀·관용).
# tomllib 부재(3.10 이하)·configparser 실패 시의 **텍스트 스캔 fallback** 에서만 쓴다 — 구조화 파서
# 경로(tomllib·configparser)는 키를 정밀 확인한다. fallback 은 라인-앵커로 위양성을 피한다:
#   DJANGO_SETTINGS_MODULE — 직접 환경/옵션 지정(라인 키 `DJANGO_SETTINGS_MODULE = …` 또는 본문 등장).
#   --ds=a.b.settings / --ds a.b.settings — pytest-django addopts 별칭(명령행 형태).
#   ds = a.b.settings — pytest-django ini 별칭 키(라인-앵커, `python_files`·`addopts` 등 다른 키와
#     구분하려고 줄 시작에서 `ds` 키만 매칭).
#   django_find_project — pytest-django 프로젝트 자동탐색.
BINDING_LINE_RE = re.compile(
    r"^\s*(?:DJANGO_SETTINGS_MODULE|ds|django_find_project)\s*[=:]",
    re.MULTILINE,
)
BINDING_SUBSTRINGS = ("DJANGO_SETTINGS_MODULE", "--ds=", "--ds ", "django_find_project")


def _text_has_binding(text: str) -> bool:
    """텍스트 스캔 fallback — 구조화 파서를 못 쓸 때만. 명령행 `--ds=`·`DJANGO_SETTINGS_MODULE`
    본문 등장, 또는 라인-앵커 ini 키(`ds =`·`DJANGO_SETTINGS_MODULE =`·`django_find_project =`)를 본다."""
    if any(s in text for s in BINDING_SUBSTRINGS):
        return True
    return BINDING_LINE_RE.search(text) is not None

# conftest 가 Django 를 구성하는 신호(설정 파일 밖 바인딩 — 전부 정상 경로).
CONFTEST_MARKERS = (
    'os.environ.setdefault("DJANGO_SETTINGS_MODULE"',
    "os.environ.setdefault('DJANGO_SETTINGS_MODULE'",
    'os.environ["DJANGO_SETTINGS_MODULE"]',
    "os.environ['DJANGO_SETTINGS_MODULE']",
    "DJANGO_SETTINGS_MODULE",
    "django.setup(",
    "settings.configure(",
    "pytest_configure",
)


def _git_available(root: Path) -> bool:
    return (root / ".git").exists()


def _porcelain(root: Path, relpath: str) -> str | None:
    try:
        res = subprocess.run(
            ["git", "-C", str(root), "status", "--porcelain", "--", relpath],
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if res.returncode != 0:
        return None
    return res.stdout


def _is_new_or_modified(root: Path, file: Path) -> bool | None:
    """이번 작업이 이 파일을 새로 만들거나 수정했나. 판정 불가면 None(→ 스킵)."""
    if not _git_available(root):
        return None
    try:
        rel = file.relative_to(root).as_posix()
    except ValueError:
        return None
    out = _porcelain(root, rel)
    if out is None:
        return None
    return bool(out.strip())


def _read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def _ds_in_addopts(addopts: object) -> bool:
    """addopts(문자열 또는 리스트)에 `--ds=`/`ds` settings 지정이 있나."""
    if isinstance(addopts, str):
        text = addopts
    elif isinstance(addopts, (list, tuple)):
        text = " ".join(str(x) for x in addopts)
    else:
        return False
    return "--ds=" in text or "--ds " in text


def _env_has_ds(env: object) -> bool:
    """pytest-env 의 `env` 키(리스트 또는 멀티라인 문자열)가 `DJANGO_SETTINGS_MODULE` 을
    설정하나. pytest-env 플러그인은 `env = ["DJANGO_SETTINGS_MODULE=proj.settings"]`(TOML 리스트)
    또는 ini 멀티라인 `env =\\n    DJANGO_SETTINGS_MODULE=proj.settings` 로 settings 를 바인딩한다.
    값을 문자열화해 `DJANGO_SETTINGS_MODULE` 등장만 본다(고정밀·관용)."""
    if isinstance(env, str):
        text = env
    elif isinstance(env, (list, tuple)):
        text = " ".join(str(x) for x in env)
    else:
        return False
    return "DJANGO_SETTINGS_MODULE" in text


def _toml_has_binding(path: Path) -> bool | None:
    """pyproject.toml `[tool.pytest.ini_options]` 에 Django settings 바인딩이 있나.
    pytest 설정 섹션 자체가 없으면 None(이 파일은 pytest 설정이 아님→대상 아님).
    바인딩 있으면 True, 설정은 있으나 바인딩 없으면 False."""
    if tomllib is not None:
        try:
            data = tomllib.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return None  # 파싱 실패 → fail-open(이 파일은 판정 불가)
        section = data.get("tool", {}).get("pytest", {}).get("ini_options")
        if not isinstance(section, dict):
            return None  # pytest 설정 섹션 없음 → 대상 아님
        if "DJANGO_SETTINGS_MODULE" in section:
            return True
        if "django_find_project" in section:
            return True
        if "ds" in section and str(section.get("ds", "")).strip():
            return True
        if _ds_in_addopts(section.get("addopts")):
            return True
        if _env_has_ds(section.get("env")):  # pytest-env 플러그인 바인딩
            return True
        return False
    # tomllib 부재(3.10 이하) — 텍스트 스캔 fallback.
    text = _read_text(path)
    if text is None or PYPROJECT_SECTION not in text:
        return None
    return _text_has_binding(text)


def _ini_has_binding(path: Path, section_header: str) -> bool | None:
    """INI 류(pytest.ini·tox.ini·setup.cfg) 설정에 Django settings 바인딩이 있나.
    pytest 설정 섹션 자체가 없으면 None(대상 아님)."""
    text = _read_text(path)
    if text is None or section_header not in text:
        return None  # pytest 설정 섹션 없음 → 대상 아님
    # configparser 로 해당 섹션 키를 정밀 확인하되, 실패하면 텍스트 스캔으로 fail-open.
    section_name = section_header.strip("[]")
    parser = configparser.ConfigParser()
    try:
        parser.read_string(text)
    except configparser.Error:
        return _text_has_binding(text)
    if not parser.has_section(section_name):
        return None
    items = {k.lower(): (v or "") for k, v in parser.items(section_name)}
    if "django_settings_module" in items:
        return True
    if "django_find_project" in items:
        return True
    if items.get("ds", "").strip():
        return True
    if _ds_in_addopts(items.get("addopts", "")):
        return True
    if _env_has_ds(items.get("env")):  # pytest-env 플러그인 바인딩
        return True
    # pytest 섹션엔 바인딩 키가 없으나 같은 파일의 다른 섹션이 settings 를 묶을 수 있다
    # (예: tox.ini `[testenv]` 의 `setenv = DJANGO_SETTINGS_MODULE = …`). TOML fallback 과
    # 동일한 fail-open — 본문 스캔으로 settings 신호를 보고 거짓양성을 피한다.
    return _text_has_binding(text)


def _conftest_configures_django(root: Path) -> bool:
    """레포 어디든 conftest.py 가 Django 를 셋업하면 True(설정 파일 밖 바인딩)."""
    for path in root.rglob("conftest.py"):
        if set(path.parts) & SKIP_DIRS:
            continue
        text = _read_text(path)
        if text is None:
            continue
        if any(m in text for m in CONFTEST_MARKERS):
            return True
    return False


def _find_pytest_configs(root: Path) -> list[tuple[Path, bool | None]]:
    """이번 작업이 건드린 pytest 설정 파일과 각자의 바인딩 보유 여부.
    (path, has_binding) — has_binding 가 None 이면 그 파일은 pytest 설정이 아니거나 판정 불가."""
    out: list[tuple[Path, bool | None]] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if set(path.parts) & SKIP_DIRS:
            continue
        name = path.name
        if name == "pyproject.toml":
            has = _toml_has_binding(path)
        elif name in INI_CONFIGS:
            has = _ini_has_binding(path, INI_CONFIGS[name])
        else:
            continue
        if has is None:
            continue  # pytest 설정 섹션 없음·판정 불가 → 대상 아님
        if _is_new_or_modified(root, path) is not True:
            continue  # 미변경·비-git·판정 불가 → 스킵(brownfield 존중·거짓양성 회피)
        out.append((path, has))
    return out


def main(argv: list[str]) -> int:
    root = Path(argv[1]).resolve() if len(argv) > 1 else Path.cwd()
    if not root.is_dir():
        print(f"[check-test-config] 사용 오류: 디렉터리 아님 {root}", file=sys.stderr)
        return 1

    try:
        configs = _find_pytest_configs(root)
    except Exception:
        return 0  # 어떤 예외든 fail-open(정밀 그물이지 정확성 오라클 아님).

    if not configs:
        return 0  # pytest 설정 없음(manage.py test 관례 존중) → 발화 안 함.

    # 설정 중 하나라도 자체 바인딩을 가지면 러너는 묶인다. conftest 의 Django 셋업도 바인딩.
    if any(has for _, has in configs):
        return 0
    if _conftest_configures_django(root):
        return 0

    findings: list[str] = []
    for path, _ in configs:
        findings.append(f"  - {path.relative_to(root).as_posix()}")

    print(
        "[check-test-config] BLOCKER — pytest 설정은 있으나 Django settings 바인딩이 없다"
        "(pytest-django 가 테스트를 수집할 수 없는 결정적 깨짐):"
    )
    for f in findings:
        print(f)
    print(
        "  근거: Phase 2 러너 준비·`implementation-test`/`implementation-django` §6.2. 위 pytest "
        "설정에 `DJANGO_SETTINGS_MODULE`(또는 addopts `--ds=`/`django_find_project`)가 없고 "
        "conftest 의 Django 셋업(`os.environ.setdefault(\"DJANGO_SETTINGS_MODULE\"…`·"
        "`django.setup()`·`settings.configure()`·`pytest_configure`)도 없다 — pytest-django 가 "
        "settings 를 못 찾아 ORM/모델 import 가 `ImproperlyConfigured` 로 죽고 테스트 수집이 "
        "조용히 실패한다(0 collected). 설정에 프로젝트의 실제 `DJANGO_SETTINGS_MODULE` 을 더하거나 "
        "conftest 에서 Django 를 셋업하라. (pytest 설정을 아예 두지 않고 `manage.py test` 관례를 "
        "쓰는 것은 위반이 아니다 — 이 가드는 'pytest 를 도입했는데 바인딩이 깨진' 경우만 본다.)"
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
