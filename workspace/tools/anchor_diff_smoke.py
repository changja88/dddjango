#!/usr/bin/env python3
"""anchor_diff 스모크 — scope-render 직접 계열 판정 차분의 계약을 재현으로 고정한다.

registry_gate_smoke 와 같은 부류(git 앵커가 재료 — fixture_matrix 의 비-git hermetic
원칙과 상반이라 따로 둔다). release 게이트 [2/7] 검증 세트에 등록되어 함께 돈다.

케이스(2026-08-15 S3-r2″ 레인 B 유효 정지 → 개선 후보 ⑤ 수정의 고정):
  N  --anchor 미지정                        → exit 2 (현행 동작 완전 보존)
  V  공허 차분(앵커=HEAD·clean)             → exit 1 (커밋-후-검사 세탁 차단)
  M  무발견 clean + resolve 불능 앵커        → exit 1 (F2 — 재료 선검증: bogus 앵커가
                                              findings 0 이라고 침묵 exit 0 되지 않는다)
  A  신규 위반(앵커 이후 working)           → exit 2 + 신규분 절에 그 위반
  B  앵커 기존분-only                       → exit 0 + 기존분 전량 보고(침묵 금지)
  E  빚 채널(--legacy-debt-file 승인 매칭)   → exit 0 + «이관 빚» 절 보고
  E2 숫자 없는 빚 tag(`##` 류)              → exit 1 (S2 — 발화 불능 규칙은 형식 오류)
  S1 selector 렌더 + 앵커에 없는 selector    → 앵커 재실행이 그 selector 를 걷고
     (check-composition-root code-json)       «selector 렌더 재실행» 기준선으로 성립,
                                              앵커 기존 위반은 강등(exit 0)
  S2 S1 + 신규 위반 추가                     → 같은 파일 안 신규 진단만 red(exit 2),
                                              기존 진단은 기존분 절로 분리
  S3 S2 의 신규 위반을 `:N` 표기 빚으로 승인  → exit 0 + «이관 빚» 절 (F1 — 빚 매칭이
                                              registry_gate 와 같은 «정규화 라인» 코퍼스:
                                              라인번호 `:N` 표기 항목이 직접 계열에서도 격리)
  T  registry 2번 dynamic Enum 토큰          → exit 1 + DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED
     (check-error-centralization code-json)    (일반 분석 오류로 죽던 r2″ 축) · 정적
                                              대조군은 exit 0 무변
  C1 registry 2번 차분 결선(재료 축 후속)     → 앵커 기존 base-canon 위반은 강등(exit 0)
     (check-error-centralization code-json)    + 앵커 이후 새 «빈 골격 placeholder»(#114)는
                                              inventory 에서 빼도 분석 오류 아님(렌더 계약)
  C2 C1 + 신규 위반 추가                     → 같은 파일 안 신규 진단만 red(exit 2),
                                              기존 진단은 기존분 절로 분리

사용: python3 anchor_diff_smoke.py
exit 0 = 전 케이스 일치 / exit 2 = 불일치 / exit 1 = 재료 결손.
"""
from __future__ import annotations

import shutil
import os
import subprocess
import sys
import tempfile
import unittest
import contextlib
import io
import re
import json
import errno
import importlib.util
from unittest.mock import patch
from pathlib import Path

ROOT: Path = Path(__file__).resolve().parents[2]
S: Path = ROOT / "dddjango" / "scripts"
F: Path = ROOT / "workspace" / "eval" / "fixtures"
CTX: Path = S / "check-context-isolation.py"
COMP: Path = S / "check-composition-root.py"
CENT: Path = S / "check-error-centralization.py"
OPENAPI: Path = S / "check-openapi-error-declaration.py"
CONTRACT: Path = S / "check-api-error-controller-contract.py"

_GIT_ID: "list[str]" = ["-c", "user.email=smoke@dddjango", "-c", "user.name=smoke"]

# 위반 재료 — registry_gate_smoke 와 같은 잎(#95: driving 잎의 domain 애그리거트 import).
_VIOLATION_REL: str = "application/orders/driving_layer/api/order/schema/schema_smoke.py"
_VIOLATION_SRC: str = "from application.orders.domain_layer.order.order import Order\n\n_N: str = Order.__name__\n"

# T 레인 재료 — api_error_backstop_matrix BASE_FILES 동형의 최소 code-json 트리.
_COMMON_SRC: str = (
    "from ninja import Schema\n\n\n"
    "class FrameworkErrorSchema(Schema):\n"
    "    code: str\n    title: str\n    status: int\n    detail: str\n"
)
_LESSON_STATIC_SRC: str = (
    "from enum import StrEnum\n"
    "from framework.ninja.framework_error_schema import FrameworkErrorSchema\n\n\n"
    "class LessonErrorCode(StrEnum):\n"
    '    NOT_FOUND = "lesson_not_found"\n\n\n'
    "class LessonErrorSchema(FrameworkErrorSchema):\n"
    "    code: LessonErrorCode\n\n\n"
    "class LessonNotFoundError(LessonErrorSchema):\n"
    "    code: LessonErrorCode = LessonErrorCode.NOT_FOUND\n"
    '    title: str = "Lesson not found"\n'
    "    status: int = 404\n"
    '    detail: str = "The lesson does not exist."\n'
)
# 동적 wire 값 — r2″ 실증 축(모듈 상수 f-string)과 같은 모양.
_LESSON_DYNAMIC_SRC: str = _LESSON_STATIC_SRC.replace(
    '    NOT_FOUND = "lesson_not_found"',
    '    _BASE = "lesson"\n    _ignore_ = ["_BASE"]\n    NOT_FOUND = f"{_BASE}_not_found"',
)
# C 레인 재료 — 앵커 기존 base-canon 위반(레인 실전 «BC base must preserve …» 축 동형).
_LESSON_BASE_DEFAULT_SRC: str = _LESSON_STATIC_SRC.replace(
    "class LessonErrorSchema(FrameworkErrorSchema):\n    code: LessonErrorCode\n",
    "class LessonErrorSchema(FrameworkErrorSchema):\n"
    "    code: LessonErrorCode = LessonErrorCode.NOT_FOUND\n",
)
assert _LESSON_BASE_DEFAULT_SRC != _LESSON_STATIC_SRC, "C 레인 재료 치환 실패"
# C2 신규 위반 — 앵커 이후 raw string discriminator concrete(신규분 2건 재료).
_LESSON_RAW_CONCRETE_SRC: str = (
    "\n\n"
    "class LessonExpiredError(LessonErrorSchema):\n"
    '    code: LessonErrorCode = "lesson_expired"\n'
    '    title: str = "Lesson expired"\n'
    "    status: int = 410\n"
    '    detail: str = "The lesson has expired."\n'
)
_LESSON_SCHEMA_REL: str = "application/lesson/driving_layer/api/bc_error_schema.py"
_PLACEHOLDER_REL: str = "application/report/driving_layer/api/bc_error_schema.py"
_T_FILES: "dict[str, str]" = {
    "framework/ninja/__init__.py": "",
    "framework/ninja/framework_error_schema.py": _COMMON_SRC,
    "application/lesson/driving_layer/api/bc_error_schema.py": _LESSON_STATIC_SRC,
    "config/api.py": "from ninja_extra import NinjaExtraAPI\n\napi = NinjaExtraAPI()\n",
    "application/lesson/driving_layer/controller.py": "def get_lesson(request): return {'id': 1}\n",
}
_T_ARGS: "list[str]" = [
    "--error-profile", "dddjango-code-json", "--scope", "public-v1",
    "--api-module", "config/api.py",
    "--controller-module", "application/lesson/driving_layer/controller.py",
    "--scope-bc", "lesson", "--error-bc", "lesson",
    "--project-code-error-module", "framework/ninja/framework_error_schema.py",
    "--project-code-error-module", "application/lesson/driving_layer/api/bc_error_schema.py",
]

# S 레인 selector — fixture_matrix composition_selector 레인과 같은 렌더.
_S_ARGS: "list[str]" = [
    "--error-profile", "dddjango-code-json", "--scope", "public-v1",
    "--api-module", "config/api.py", "--urlconf-module", "config/urls.py",
    "--registrar-module", "application/lesson/driving_layer/api/api_router.py",
]
_S_REGISTRAR_REL: str = "application/lesson/driving_layer/api/api_router.py"



def _scrubbed_env() -> "dict[str, str]":
    """검사기 하위 실행 env — 사용자 DJR_FINDINGS_JSON 오염 차단(T2-1 적대 검증 레인 S 7번 잔여)."""
    env = dict(os.environ)
    env.pop("DJR_FINDINGS_JSON", None)
    return env

def _git(repo: Path, *args: str) -> "subprocess.CompletedProcess[str]":
    return subprocess.run(["git", "-C", str(repo), *_GIT_ID, *args], capture_output=True, text=True)


def _commit_all(repo: Path, message: str) -> str:
    for step in (("add", "-A"), ("commit", "-q", "-m", message)):
        proc = _git(repo, *step)
        if proc.returncode != 0:
            raise RuntimeError(f"git {step[0]} 실패: {proc.stderr.strip()}")
    return _git(repo, "rev-parse", "HEAD").stdout.strip()


def _init_repo(td: Path, name: str, base: Path) -> "tuple[Path, str]":
    repo: Path = td / name
    shutil.copytree(base, repo)
    proc = _git(repo, "init", "-q")
    if proc.returncode != 0:
        raise RuntimeError(f"git init 실패: {proc.stderr.strip()}")
    return repo, _commit_all(repo, "anchor")


def _write(repo: Path, rel: str, src: str) -> None:
    path: Path = repo / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(src, encoding="utf-8")


def _run(script: Path, target: Path, extra: "list[str]") -> "tuple[int, str]":
    proc = subprocess.run(
        [sys.executable, str(script), str(target), *extra], capture_output=True, text=True,
        env=_scrubbed_env(),
    )
    return proc.returncode, proc.stdout + proc.stderr


def _section(out: str, title: str) -> set[str]:
    match = re.search(rf"^  == {re.escape(title)}.*?\n(.*?)(?=^  == |^판정:|\Z)", out, re.S | re.M)
    return {line.strip() for line in match.group(1).splitlines()} if match else set()


def _checker_module(script: Path):
    sys.path.insert(0, str(S))
    name = "anchor_smoke_" + script.stem.replace("-", "_")
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, script)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    return sys.modules[name]


class BaselineBcArgvRegression(unittest.TestCase):
    """완성된 argv 전체로 이름·경로 selector의 제거와 보존을 검사한다."""

    def setUp(self):
        sys.path.insert(0, str(S))
        import anchor_diff
        self.diff = anchor_diff
        self.temp = tempfile.TemporaryDirectory(prefix="baseline-bc-")
        self.addCleanup(self.temp.cleanup)
        self.snap = Path(self.temp.name)
        (self.snap / "application").mkdir()
        _write(self.snap, _LESSON_SCHEMA_REL, _LESSON_STATIC_SRC)
        _write(self.snap, "config/api.py", "api = None\n")

    def assert_argv(self, args, kept, snapshot=None):
        snap = snapshot or self.snap
        got = self.diff._baseline_argv(CENT, snap, ["/current", *args], frozenset({
            "--api-module", "--controller-module", "--project-code-error-module"}))
        self.assertEqual(got, [sys.executable, str(CENT), str(snap), *kept, "--anchor-baseline"])

    def test_missing_both_flags_split_and_equals(self):
        for args in (["--scope-bc", "report", "--error-bc", "report"],
                     ["--error-bc=report", "--scope-bc=report"]):
            with self.subTest(args=args):
                self.assert_argv(args, [])

    def test_existing_both_flags_split_and_equals(self):
        for args in (["--scope-bc", "lesson", "--error-bc", "lesson"],
                     ["--error-bc=lesson", "--scope-bc=lesson"]):
            with self.subTest(args=args):
                self.assert_argv(args, args)

    def test_mixed_order_paths_next_option_and_repeated_occurrences(self):
        args = ["--error-bc=report", "--scope", "public-v1", "--scope-bc", "lesson",
                "--controller-module", "application/report/driving_layer/controller.py",
                "--error-bc", "lesson", "--scope-bc=report", "--scope-bc", "report",
                "--project-code-error-module=" + _LESSON_SCHEMA_REL,
                "--scope-bc=lesson", "--error-bc", "report", "--error-bc=lesson",
                "--api-module", "config/api.py", "--anchor", "abc", "--anchor=def",
                "--legacy-debt-file", "debt.txt", "--legacy-debt-file=other.txt",
                "--anchor-baseline", "--error-profile=dddjango-code-json"]
        kept = ["--scope", "public-v1", "--scope-bc", "lesson", "--error-bc", "lesson",
                "--project-code-error-module=" + _LESSON_SCHEMA_REL,
                "--scope-bc=lesson", "--error-bc=lesson", "--api-module", "config/api.py",
                "--error-profile=dddjango-code-json"]
        self.assert_argv(args, kept)

    def test_bc_root_empty_file_and_all_link_forms_preserved(self):
        app = self.snap / "application"
        (app / "empty").mkdir()  # canonical 파일이 없어도 뿌리가 있으면 유지
        (app / "file").write_text("same name file\n")
        (app / "linked").symlink_to("lesson", target_is_directory=True)
        (app / "dangling").symlink_to("missing", target_is_directory=True)
        (app / "loop").symlink_to("loop", target_is_directory=True)
        for name in ("empty", "file", "linked", "dangling", "loop"):
            for args in (["--scope-bc", name, "--error-bc", name],
                         [f"--error-bc={name}", f"--scope-bc={name}"]):
                with self.subTest(name=name, args=args):
                    self.assert_argv(args, args)

    def test_application_absent_file_and_all_link_forms_preserved(self):
        for kind in ("absent", "file", "linked", "dangling", "loop"):
            with self.subTest(kind=kind):
                snap = self.snap / kind
                snap.mkdir()
                app = snap / "application"
                if kind == "file":
                    app.write_text("not a directory\n")
                elif kind == "linked":
                    app.symlink_to(self.snap / "application", target_is_directory=True)
                elif kind == "dangling":
                    app.symlink_to("missing", target_is_directory=True)
                elif kind == "loop":
                    app.symlink_to("application", target_is_directory=True)
                args = ["--scope-bc", "report", "--error-bc=report", "--scope", "next"]
                self.assert_argv(args, args, snap)

    def test_no_case_normalization_or_area_search(self):
        _write(self.snap, "application/area/report/only.py", "")
        (self.snap / "application" / "Report").mkdir()
        real_lstat = os.lstat
        calls = []

        def case_sensitive_lstat(path, *args, **kwargs):
            # 대소문자 비구별 파일시스템에서도 정확한 소문자 조회의 부재를 재현한다.
            calls.append(Path(path))
            if Path(path) == self.snap / "application" / "report":
                raise FileNotFoundError(errno.ENOENT, "missing lowercase BC")
            return real_lstat(path, *args, **kwargs)

        with patch.object(self.diff.os, "lstat", side_effect=case_sensitive_lstat):
            self.assert_argv(["--scope-bc", "report", "--error-bc=report"], [])
        self.assertIn(self.snap / "application" / "report", calls)
        self.assertNotIn(self.snap / "application" / "Report", calls)
        self.assertNotIn(self.snap / "application" / "area" / "report", calls)

    def test_lstat_uncertainty_parent_and_child_preserves(self):
        real_lstat = os.lstat
        for level in ("application", "application/report"):
            for error in (PermissionError(errno.EACCES, "denied"),
                          NotADirectoryError(errno.ENOTDIR, "not directory"),
                          OSError(errno.ELOOP, "loop"), OSError(errno.EIO, "io failure")):
                with self.subTest(level=level, error=error.errno):
                    def uncertain(path, *args, **kwargs):
                        if Path(path) == self.snap / level:
                            raise error
                        return real_lstat(path, *args, **kwargs)
                    args = ["--scope-bc", "report", "--error-bc=report"]
                    with patch.object(self.diff.os, "lstat", side_effect=uncertain):
                        self.assert_argv(args, args)


class EmptyScopeBcRegression(unittest.TestCase):
    """세 검사기 × 두 explicit profile의 parser 계약과 실행 흐름을 고정한다."""
    scripts = (CENT, OPENAPI, CONTRACT)
    profiles = ("dddjango-code-json", "preserve-established")

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="empty-scope-bc-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for rel, source in _T_FILES.items():
            _write(self.root, rel, source)

    def args(self, script, profile):
        args = [str(self.root), "--error-profile", profile, "--scope", "public-v1",
                "--api-module", "config/api.py", "--controller-module",
                "application/lesson/driving_layer/controller.py"]
        if script == CENT and profile == "dddjango-code-json":
            args += ["--project-code-error-module", "framework/ninja/framework_error_schema.py",
                     "--project-code-error-module", _LESSON_SCHEMA_REL]
        return args

    def test_baseline_empty_scope_parser_accepts_all_six(self):
        for script in self.scripts:
            module = _checker_module(script)
            for profile in self.profiles:
                with self.subTest(checker=script.name, profile=profile):
                    self.assertIn(profile, module.ERROR_PROFILES)
                    config = module._parse_config([*self.args(script, profile), "--anchor-baseline"])
                    self.assertEqual(config.scope_bcs, ())
                    self.assertEqual(config.error_bcs, ())

    def test_normal_empty_scope_same_required_error_all_six(self):
        for script in self.scripts:
            module = _checker_module(script)
            for profile in self.profiles:
                with self.subTest(checker=script.name, profile=profile):
                    with self.assertRaises(module.UsageError) as raised:
                        module._parse_config(self.args(script, profile))
                    self.assertEqual(str(raised.exception), "필수 인자 누락: --scope-bc")

    def test_baseline_remaining_error_bc_outside_scope_rejected_all_six(self):
        for script in self.scripts:
            module = _checker_module(script)
            for profile in self.profiles:
                with self.subTest(checker=script.name, profile=profile):
                    with self.assertRaises(module.UsageError) as raised:
                        module._parse_config([*self.args(script, profile), "--anchor-baseline",
                                              "--error-bc", "lesson"])
                    self.assertEqual(str(raised.exception), "--error-bc는 --scope-bc의 부분집합이어야 함")

    def test_name_grammar_and_duplicates_still_rejected(self):
        for script in self.scripts:
            module = _checker_module(script)
            for profile in self.profiles:
                for baseline in ([], ["--anchor-baseline"]):
                    for option in ("--scope-bc", "--error-bc"):
                        with self.subTest(checker=script.name, profile=profile,
                                          baseline=baseline, option=option):
                            args = [*self.args(script, profile), *baseline, "--scope-bc", "lesson"]
                            repeated = ([option, "lesson"] if option == "--scope-bc" else
                                        [option, "lesson", option + "=lesson"])
                            with self.assertRaisesRegex(module.UsageError, "반복 인자 중복: " + option):
                                module._parse_config([*args, *repeated])
                            with self.assertRaisesRegex(module.UsageError, "잘못된 BC 이름: " + option + "=Lesson"):
                                module._parse_config([*args, option, "Lesson"])

    def test_git_target_baseline_forbidden_all_six(self):
        self.assertEqual(_git(self.root, "init", "-q").returncode, 0)
        for script in self.scripts:
            module = _checker_module(script)
            for profile in self.profiles:
                with self.subTest(checker=script.name, profile=profile):
                    with self.assertRaisesRegex(module.UsageError, "git 저장소 TARGET 금지"):
                        module._parse_config([*self.args(script, profile), "--scope-bc", "lesson",
                                              "--anchor-baseline"])

    def test_empty_scope_runs_analysis_instead_of_early_success(self):
        # parser 검사는 위에서 별도 단언한다. 정상 tree에서 #2의 schema 분석을 확인한다.
        _write(self.root, "framework/ninja/framework_error_schema.py",
               _COMMON_SRC.replace("FrameworkErrorSchema(Schema)", "FrameworkErrorSchema(object)"))
        code, out = _run(CENT, self.root,
                         [*self.args(CENT, "dddjango-code-json")[1:], "--anchor-baseline"])
        self.assertEqual(code, 2, out)
        self.assertIn("common FrameworkErrorSchema must directly inherit ninja.Schema", out)
        self.assertIn("BLOCKER — code-profile", out)
        # #5의 공통 source는 parser의 선택 source 검사 뒤 code 분석에서 읽는다.
        # #15는 빈 error BC에서도 선택 API source 분석을 계속한다.
        for script, source_path in ((OPENAPI, "framework/ninja/framework_error_schema.py"),
                                    (CONTRACT, "config/api.py")):
            with self.subTest(checker=script.name):
                _write(self.root, source_path, "invalid syntax ???\n")
                code, out = _run(script, self.root,
                                 [*self.args(script, "dddjango-code-json")[1:], "--anchor-baseline"])
                self.assertEqual(code, 1, out)
                self.assertNotIn("필수 인자 누락: --scope-bc", out)
                self.assertIn("production source 분석 불능: " + source_path, out)


class BcSelectorPartitionRegression(unittest.TestCase):
    """실제 #2 렌더의 신규·기존 정규화 진단문 집합을 literal 기대값과 대조한다."""
    legacy = {"[#572] " + _LESSON_SCHEMA_REL + ":N: BC base must preserve common required/default semantics: code: LessonErrorCode = LessonErrorCode.NOT_FOUND"}

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="bc-selector-partition-")
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name) / "repo"
        for rel, source in _T_FILES.items():
            _write(self.repo, rel, source)
        _write(self.repo, _LESSON_SCHEMA_REL, _LESSON_BASE_DEFAULT_SRC)
        self.assertEqual(_git(self.repo, "init", "-q").returncode, 0)
        self.anchor = _commit_all(self.repo, "legacy code contract")

    def add_bc(self, name, source=_LESSON_STATIC_SRC):
        rel = f"application/{name}/driving_layer/api/bc_error_schema.py"
        _write(self.repo, rel, source.replace("Lesson", name.title()).replace("lesson_", name + "_"))
        return ["--scope-bc", name, "--error-bc=" + name, "--project-code-error-module", rel]

    def assert_partition(self, extra, new, existing=None):
        code, out = _run(CENT, self.repo, [*_T_ARGS, *extra, "--anchor", self.anchor])
        self.assertEqual(code, 2 if new else 0, out)
        self.assertIn("기준선=selector 렌더 재실행", out)
        self.assertNotIn("positional 기준선", out)
        self.assertNotIn("사용 오류", out)
        normalize = lambda lines: {re.sub(r":\d+(?=:|\b)", ":N", line) for line in lines}
        self.assertEqual(normalize(_section(out, "신규분")), new, out)
        self.assertEqual(normalize(_section(out, "앵커 기존분")), self.legacy if existing is None else existing, out)

    def test_absent_bc_names_keep_legacy_strings_without_downgrade(self):
        self.assert_partition(self.add_bc("report"), set())

    def test_contract_absent_bc_split_and_equals_keep_exact_legacy_set(self):
        repo, anchor = _init_repo(Path(self.temp.name), "contract",
                                  F / "api_error_controller_code/bad_rules")
        _write(repo, "application/report/driving_layer/api/bc_error_schema.py",
               _LESSON_STATIC_SRC.replace("Lesson", "Report").replace("lesson_", "report_"))
        _write(repo, "application/report/driving_layer/controller.py", "def report(request): return {}\n")
        existing = {
            "[#62] application/lesson/driving_layer/controller.py:N: bare catch forbidden: except:",
            "[#62] application/lesson/driving_layer/controller.py:N: catch must be direct own-BC application/domain exception: except Exception:",
            "[#59] application/lesson/driving_layer/controller.py:N: custom Ninja exception_handler forbidden: @router.exception_handler(LessonMissing)",
        }
        for selectors in (["--scope-bc", "report", "--error-bc", "report"],
                          ["--scope-bc=report", "--error-bc=report"]):
            with self.subTest(selectors=selectors):
                code, out = _run(CONTRACT, repo, [*_T_ARGS[:-4], *selectors,
                    "--controller-module=application/report/driving_layer/controller.py", "--anchor", anchor])
                self.assertEqual(code, 0, out)
                self.assertIn("기준선=selector 렌더 재실행", out)
                self.assertNotIn("positional 기준선", out)
                self.assertNotIn("사용 오류", out)
                self.assertEqual(_section(out, "신규분"), set(), out)
                normalized = {re.sub(r":\d+(?=:|\b)", ":N", line)
                              for line in _section(out, "앵커 기존분")}
                self.assertEqual(normalized, existing, out)

    def test_new_violation_in_existing_bc_stays_new(self):
        extra = self.add_bc("report")
        _write(self.repo, _LESSON_SCHEMA_REL, _LESSON_BASE_DEFAULT_SRC + _LESSON_RAW_CONCRETE_SRC)
        prefix = "- " + _LESSON_SCHEMA_REL + ":N: "
        self.assert_partition(extra, {
            prefix + 'raw string FrameworkErrorSchema discriminator: code: LessonErrorCode = "lesson_expired"',
            prefix + 'concrete discriminator default must use own ErrorCode member: code: LessonErrorCode = "lesson_expired"',
        })

    def test_new_bc_own_violation_stays_new(self):
        extra = self.add_bc("report", _LESSON_BASE_DEFAULT_SRC)
        self.assert_partition(extra, {"[#572] application/report/driving_layer/api/bc_error_schema.py:N: BC base must preserve common required/default semantics: code: ReportErrorCode = ReportErrorCode.NOT_FOUND"})

    def test_new_bc_first_wire_collision_with_existing_subject_stays_new(self):
        extra = self.add_bc("report")
        rel = "application/report/driving_layer/api/bc_error_schema.py"
        _write(self.repo, rel, (self.repo / rel).read_text().replace('"report_not_found"', '"lesson_not_found"'))
        self.assert_partition(extra, {"- " + _LESSON_SCHEMA_REL + ":N: duplicate project code wire value: lesson_not_found: from enum import StrEnum"})

    def test_common_schema_change_stays_new(self):
        extra = self.add_bc("report")
        _write(self.repo, "framework/ninja/framework_error_schema.py",
               _COMMON_SRC.replace("FrameworkErrorSchema(Schema)", "FrameworkErrorSchema(object)"))
        self.assert_partition(extra, {"- framework/ninja/framework_error_schema.py:N: common FrameworkErrorSchema must directly inherit ninja.Schema: class FrameworkErrorSchema(object):"})

    def test_known_limit_existing_wire_collision_added_owner_same_string_is_existing(self):
        old = self.add_bc("report")
        rel = "application/report/driving_layer/api/bc_error_schema.py"
        _write(self.repo, rel, (self.repo / rel).read_text().replace('"report_not_found"', '"lesson_not_found"'))
        self.anchor = _commit_all(self.repo, "existing two-owner collision")
        new = self.add_bc("zebra")
        rel = "application/zebra/driving_layer/api/bc_error_schema.py"
        _write(self.repo, rel, (self.repo / rel).read_text().replace('"zebra_not_found"', '"lesson_not_found"'))
        collision = "- " + _LESSON_SCHEMA_REL + ":N: duplicate project code wire value: lesson_not_found: from enum import StrEnum"
        self.assert_partition([*old, *new], set(), self.legacy | {collision})


class SisterAnchorRegression(unittest.TestCase):
    """주어 칸만 분할하며 기준선·분석 실패와 사용 오류는 보호한다."""
    title = "자매 플러그인 영역(dddjango-web 소유 — 서버 판정 밖 · 보고만)"

    def setUp(self):
        sys.path.insert(0, str(S))
        import anchor_diff
        self.diff = anchor_diff
        self.temp = tempfile.TemporaryDirectory(prefix="sister-anchor-")
        self.addCleanup(self.temp.cleanup)
        self.td = Path(self.temp.name)
        self.repo, _ = _init_repo(self.td, "repo", F / "skeleton/good_bc")
        _write(self.repo, "manage.py", 'import os\nos.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")\n')
        _write(self.repo, "config/settings.py", "")
        _write(self.repo, ".gitignore", ".dddjango-web/\n")
        (self.repo / ".dddjango-web").mkdir()
        self.anchor = _commit_all(self.repo, "server project")
        _write(self.repo, "dirty.md", "dirty\n")

    def partition(self, findings, runs=((0, []),), **kwargs):
        out = io.StringIO()
        with patch.object(self.diff, "_run_lines", side_effect=runs), contextlib.redirect_stdout(out):
            code = self.diff.partition_exit(script=CTX, label="[check-context-isolation]",
                target=self.repo, anchor=self.anchor, argv=[str(self.repo)], findings=findings, **kwargs)
        return code, out.getvalue()

    def section(self, out, title):
        match = re.search(rf"^  == {re.escape(title)}.*?\n(.*?)(?=^  == |^판정:|\Z)", out, re.S | re.M)
        return {line.strip() for line in match.group(1).splitlines()} if match else set()

    def test_numeric_contract_folder_and_missing_locator_report_only(self):
        findings = ["[#95] web/application/shop/a.py:8: 위반", "- web_test/missing.py: 계약 위반",
                    "[#488] .dddjango-web/missing.py: 없음", "[#450] web/application/shop: 폴더 위반"]
        code, out = self.partition(findings)
        self.assertEqual(code, 0, out)
        self.assertIn(f"== {self.title} 4건 ==", out)
        self.assertEqual(self.section(out, self.title), set(findings))
        self.assertIn("신규분(앵커 이후) 0건", out)

    def test_mixed_subject_only_each_server_line_stays(self):
        server = ["[#95] application/orders/a.py: 의존 web/application/shop/a.py",
                  "- application/orders/missing.py: web/helper.py 의존",
                  "[#488] application/orders: 폴더 위반"]
        web = ["[#95] web/application/shop/a.py: 서버 의존 application/orders/a.py"]
        code, out = self.partition(server + web)
        self.assertEqual(code, 2, out)
        self.assertEqual(self.section(out, "신규분"), set(server))
        self.assertEqual(self.section(out, self.title), set(web))

    def test_settings_setters_require_one_supported_literal_environment_write(self):
        supported = [
            'os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")',
            'os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings"',
        ]
        unsupported = [
            'os.environ.update(DJANGO_SETTINGS_MODULE="config.settings")',
            'os.environ.update({"DJANGO_SETTINGS_MODULE": "config.settings"})',
            'os.putenv("DJANGO_SETTINGS_MODULE", "config.settings")',
            'os.putenv(key(), "config.settings")',
            'os.environ.__setitem__("DJANGO_SETTINGS_MODULE", "config.settings")',
            'os.environ.setdefault("DJANGO_SETTINGS_MODULE", choose())',
            'os.environ["DJANGO_SETTINGS_MODULE"] = choose()',
            'other.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")',
            'DJANGO_SETTINGS_MODULE = "config.settings"',
            'os.environ[key()] = "config.settings"',
            'os.environ.update(values)',
            'os.environ.update(**values)',
        ]
        for statement in supported:
            with self.subTest(supported=statement):
                _write(self.repo, "manage.py", "import os\n" + statement + "\n")
                self.assertTrue(self.diff.sister_owned(self.repo))
        for statement in unsupported + [supported[0]]:
            for prefix in ("", supported[0] + "\n"):
                # 단독의 알려진 setdefault는 위의 정상 대조군. 복수는 거절한다.
                if not prefix and statement == supported[0]:
                    continue
                with self.subTest(statement=statement, prefix=prefix):
                    _write(self.repo, "manage.py", "import os\n" + prefix + statement + "\n")
                    code, out = self.partition(["[#446] web/settings/dev.py: 서버 설정"])
                    self.assertEqual(code, 2, out)
                    self.assertNotIn(self.title, out)
                    self.assertEqual(self.section(out, "신규분"), {"[#446] web/settings/dev.py: 서버 설정"})

    def test_ambiguous_analysis_synthetic_target_and_outside_stay(self):
        for finding in ("[#74] (target): 대상 0", "[#95] ../web/a.py: 위반",
                        "[#95] /web/a.py: 위반", "[#95] web/../application/a.py: 위반",
                        "[#95] web/a.py, application/a.py: 두 주어", "알 수 없음 web/a.py",
                        "[분석] web/a.py: 실패", "[진단 미파싱 · exit 2] web/a.py"):
            with self.subTest(finding=finding):
                code, out = self.partition([finding])
                self.assertEqual(code, 2, out)
                self.assertEqual(self.section(out, "신규분"), {finding})
                self.assertNotIn(self.title, out)

    def test_selector_downgrade_success_splits_failure_keeps(self):
        finding = "[#95] web/a.py: 위반"
        code, out = self.partition([finding], runs=((1, ["selector 실패"]), (0, [])))
        self.assertEqual(code, 0, out)
        self.assertIn("positional 기준선", out)
        self.assertEqual(self.section(out, self.title), {finding})
        code, out = self.partition([finding], runs=((1, ["selector 실패"]), (1, ["positional 실패"])))
        self.assertEqual(code, 2, out)
        self.assertIn("기준선 불능", out)
        self.assertEqual(self.section(out, "신규분"), {finding})
        self.assertNotIn(self.title, out)

    def test_pending_analysis_and_unparsed_baseline_preserve_stop(self):
        finding = "[#95] web/a.py: 위반"
        for kwargs in ({"analysis_pending": True},
                       {"runs": ((2, ["[진단 미파싱 · exit 2] fail-closed"]),)}):
            with self.subTest(kwargs=kwargs):
                code, out = self.partition([finding], **kwargs)
                self.assertEqual(code, 2, out)
                self.assertEqual(self.section(out, "신규분"), {finding})
                self.assertNotIn(self.title, out)

    def test_debt_first_and_material_archive_failures_remain(self):
        debt = self.td / "debt.txt"
        debt.write_text("#95 web/a.py\n")
        code, out = self.partition(["[#95] web/a.py: 위반", "[#96] web/b.py: 위반"], debt_file=str(debt))
        self.assertEqual(code, 0, out)
        self.assertEqual(self.section(out, "이관 빚"), {"[#95] web/a.py: 위반"})
        self.assertEqual(self.section(out, self.title), {"[#96] web/b.py: 위반"})
        with patch.object(self.diff, "snapshot_anchor", side_effect=self.diff.AnchorDiffUsage("git archive 실패")):
            with self.assertRaisesRegex(self.diff.AnchorDiffUsage, "archive 실패"):
                self.partition(["[#95] web/a.py: 위반"])
        self.anchor = "deadbeef"
        with self.assertRaisesRegex(self.diff.AnchorDiffUsage, "resolve 불능"):
            self.partition(["[#95] web/a.py: 위반"])

    def test_no_split_output_matches_head_2191(self):
        import importlib.util
        old = self.td / "anchor_diff.py"
        proc = _git(ROOT, "show", "HEAD:dddjango/scripts/anchor_diff.py")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        old.write_text(proc.stdout)
        spec = importlib.util.spec_from_file_location("sister_old_anchor", old)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = mod
        spec.loader.exec_module(mod)
        for finding in ("[#95] application/orders/a.py: web/a.py 의존", "[#74] (target): 대상 0"):
            with self.subTest(finding=finding):
                code, out = self.partition([finding])
                previous = io.StringIO()
                with patch.object(mod, "_run_lines", return_value=(0, [])), contextlib.redirect_stdout(previous):
                    old_code = mod.partition_exit(script=CTX, label="[check-context-isolation]", target=self.repo,
                        anchor=self.anchor, argv=[str(self.repo)], findings=[finding])
                self.assertEqual((code, out), (old_code, previous.getvalue()))

    def test_actual_error_schema_web_helper_contract_record_and_analysis_stay(self):
        for rel, source in _T_FILES.items():
            _write(self.repo, rel, source)
        self.anchor = _commit_all(self.repo, "code profile anchor")
        _write(self.repo, "web/helper.py", "def enrich(value): return value\n")
        _write(self.repo, _LESSON_SCHEMA_REL, "from web.helper import enrich\n"
               + _LESSON_STATIC_SRC + "\nhelper = enrich\n")
        sink = self.td / "findings.jsonl"
        env = _scrubbed_env()
        env["DJR_FINDINGS_JSON"] = str(sink)
        proc = subprocess.run([sys.executable, str(CENT), str(self.repo), *_T_ARGS,
                               "--anchor", self.anchor], capture_output=True, text=True, env=env)
        out = proc.stdout + proc.stderr
        self.assertEqual(proc.returncode, 2, out)
        contract = [r for r in map(json.loads, sink.read_text().splitlines())
                    if r["file"] == _LESSON_SCHEMA_REL + ":20"]
        self.assertEqual(len(contract), 1, out)
        self.assertIsNone(contract[0]["rule"])
        self.assertEqual(contract[0]["message"], "BC error module helper/mutation/side effect forbidden: helper = enrich")
        self.assertEqual(self.section(out, "신규분"),
            {"- " + _LESSON_SCHEMA_REL + ":20: " + contract[0]["message"]})
        self.assertIn("DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED", out)
        self.assertNotIn(self.title, out)

    def test_actual_sister_only_anchor_and_no_anchor_stop(self):
        web = "web/application/shop/driving_layer/api/item/schema/invalid.py"
        _write(self.repo, web, "from application.orders.domain_layer.order.order import Order\n")
        code, out = _run(CTX, self.repo, [])
        self.assertEqual(code, 2, out)
        self.assertIn("[#12] " + web + ":", out)
        self.assertNotIn(self.title, out)
        code, out = _run(CTX, self.repo, ["--anchor", self.anchor])
        self.assertEqual(code, 0, out)
        self.assertEqual(self.section(out, self.title),
            {"[#12] " + web + ": 타 BC 에서 부를 수 있는 것은 OHS·published_event 둘이다(#83 — 이 import 는 BC 삭제 내성을 깬다) — `application.orders.domain_layer.order.order`"})


def main() -> int:
    suite = unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromTestCase(case) for case in (
        BaselineBcArgvRegression, EmptyScopeBcRegression, BcSelectorPartitionRegression, SisterAnchorRegression))
    result = unittest.TextTestRunner(verbosity=2).run(
        suite)
    if not result.wasSuccessful():
        return 2
    base: Path = F / "skeleton" / "good_bc"
    sel_good: Path = F / "composition_selector" / "good"
    sel_bad: Path = F / "composition_selector" / "bad_rules"
    for need in (CTX, COMP, CENT, base, sel_good, sel_bad):
        if not need.exists():
            print(f"재료 결손: {need} 없음", file=sys.stderr)
            return 1

    rows: "list[tuple[str, int, int, bool, str]]" = []
    with tempfile.TemporaryDirectory() as td_s:
        td: Path = Path(td_s)

        # N — --anchor 미지정: 현행 동작(위반 → exit 2) 완전 보존.
        repo, _anchor = _init_repo(td, "plain", base)
        _write(repo, _VIOLATION_REL, _VIOLATION_SRC)
        code, out = _run(CTX, repo, [])
        rows.append(("N 무-anchor 보존", 2, code, "#95" in out and "앵커 차분" not in out, "차분 미관여"))

        # V — 공허 차분: 위반을 커밋해 앵커=HEAD·clean 로 만들면 사용 오류.
        repo, _anchor = _init_repo(td, "vacuous", base)
        _write(repo, _VIOLATION_REL, _VIOLATION_SRC)
        head: str = _commit_all(repo, "violation at head")
        code, out = _run(CTX, repo, ["--anchor", head])
        rows.append(("V 공허 차분", 1, code, "공허" in out, "앵커=HEAD·clean 세탁 차단"))

        # M — 무발견 clean + resolve 불능 앵커: findings 0 이어도 재료 선검증이 막는다(F2).
        repo, _anchor = _init_repo(td, "bogus", base)
        code, out = _run(CTX, repo, ["--anchor", "deadbeef"])
        rows.append((
            "M clean+bogus 앵커", 1, code,
            "resolve 불능" in out,
            "무발견 clean 에서도 앵커 재료 선검증(F2)",
        ))

        # A — 앵커 이후 working tree 신규 위반 → 신규분 blocker.
        repo, anchor = _init_repo(td, "new", base)
        _write(repo, _VIOLATION_REL, _VIOLATION_SRC)
        code, out = _run(CTX, repo, ["--anchor", anchor])
        rows.append((
            "A 신규분 red", 2, code,
            "신규분(앵커 이후) 1건" in out and "schema_smoke" in out.split("== 신규분")[-1],
            "신규 위반이 신규분 절에",
        ))

        # B — 앵커에 이미 있던 위반 + 무해 변경 → 강등 + 전량 보고.
        repo, _pre = _init_repo(td, "existing", base)
        _write(repo, _VIOLATION_REL, _VIOLATION_SRC)
        anchor = _commit_all(repo, "violation as anchor")
        _write(repo, "docs_note.md", "harmless\n")
        code, out = _run(CTX, repo, ["--anchor", anchor])
        rows.append((
            "B 기존분-only green", 0, code,
            "신규분(앵커 이후) 0건" in out and "앵커 기존분" in out and "schema_smoke" in out,
            "exit 0 + 기존분 전량 보고",
        ))

        # E — 빚 채널: A 의 신규 위반을 승인 목록으로 → exit 제외·빚 절 보고.
        repo, anchor = _init_repo(td, "debt", base)
        _write(repo, _VIOLATION_REL, _VIOLATION_SRC)
        debt: Path = td / "debt.txt"
        debt.write_text("// 승인: 스모크 빚\n#95 schema_smoke\n", encoding="utf-8")
        code, out = _run(CTX, repo, ["--anchor", anchor, "--legacy-debt-file", str(debt)])
        rows.append((
            "E 빚 채널", 0, code,
            "이관 빚" in out and "schema_smoke" in out,
            "빚 매칭 신규분은 exit 제외·기록 의무",
        ))

        # E2 — 숫자 없는 빚 tag: 어떤 `[#N]` 과도 일치 불능인 «발화 불능 규칙» 거절(S2).
        bad_debt: Path = td / "bad_debt.txt"
        bad_debt.write_text("## schema_smoke\n", encoding="utf-8")
        code, out = _run(CTX, repo, ["--anchor", anchor, "--legacy-debt-file", str(bad_debt)])
        rows.append((
            "E2 숫자 없는 tag 거절", 1, code,
            "형식 오류" in out,
            "발화 불능 빚 규칙은 조용히 수용하지 않는다(S2)",
        ))

        # S1 — selector 렌더 + 앵커에 없는 selector 경로: 앵커 재실행이 그 selector 를
        #      걷고 «selector 렌더 재실행» 기준선으로 성립, 앵커 기존 위반은 강등된다.
        repo_dir: Path = td / "selector"
        shutil.copytree(sel_bad, repo_dir)
        registrar: Path = repo_dir / _S_REGISTRAR_REL
        registrar_src: str = registrar.read_text(encoding="utf-8")
        registrar.unlink()  # 앵커 시점엔 registrar 부재
        proc = _git(repo_dir, "init", "-q")
        if proc.returncode != 0:
            raise RuntimeError(f"git init 실패: {proc.stderr.strip()}")
        anchor = _commit_all(repo_dir, "anchor without registrar")
        registrar.write_text(registrar_src, encoding="utf-8")  # registrar 신규 등장
        code, out = _run(COMP, repo_dir, [*_S_ARGS, "--anchor", anchor])
        rows.append((
            "S1 selector 드롭 기준선", 0, code,
            "selector 렌더 재실행" in out and "앵커 기존분(잔존) 1건" in out and "ProjectAPI" in out,
            "부재 selector 는 걷고 기준선 성립·앵커 기존 위반 강등",
        ))

        # S2 — S1 + 신규 위반(project api 모듈에 BC import 추가): 같은 파일 안에서
        #      신규 진단만 red 로 남고 기존 진단은 기존분 절로 분리된다.
        api_module: Path = repo_dir / "config" / "api.py"
        api_module.write_text(
            "from application.lesson.driving_layer.controller import LessonController\n"
            + api_module.read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        code, out = _run(COMP, repo_dir, [*_S_ARGS, "--anchor", anchor])
        rows.append((
            "S2 신규·기존 혼재 분리", 2, code,
            "신규분(앵커 이후) 1건" in out
            and "controller` import" in out.split("== 신규분")[-1]
            and "앵커 기존분(잔존) 1건" in out,
            "신규 진단만 red·기존 진단은 보고 절",
        ))

        # S3 — F1: S2 의 신규 위반(`config/api.py:1 …`)을 «정규화 표기»(`:N`) 빚으로 승인.
        #      빚 매칭 코퍼스가 registry_gate 와 같은 정규화 라인이므로 `:N` 항목이
        #      직접 계열에서도 격리된다(원문 라인 매칭이던 구판에선 매칭 불능 → exit 2).
        norm_debt: Path = td / "norm_debt.txt"
        norm_debt.write_text("#437 config/api.py:N\n", encoding="utf-8")
        code, out = _run(
            COMP, repo_dir,
            [*_S_ARGS, "--anchor", anchor, "--legacy-debt-file", str(norm_debt)],
        )
        rows.append((
            "S3 `:N` 표기 빚 격리(F1)", 0, code,
            "신규분(앵커 이후) 0건" in out
            and "config/api.py" in out.split("== 이관 빚")[-1].split("== 앵커 기존분")[0]
            and "앵커 기존분(잔존) 1건" in out,
            "빚 코퍼스=정규화 라인(registry_gate 동일)",
        ))

        # T — registry 2번 dynamic Enum 토큰: 일반 분석 오류 대신 PROOF 토큰 발화.
        proj: Path = td / "token"
        for rel, src in _T_FILES.items():
            _write(proj, rel, src)
        code, out = _run(CENT, proj, list(_T_ARGS))
        rows.append((
            "T 정적 대조군", 0, code, "BLOCKER" not in out, "정적 Enum 은 무변 clean",
        ))
        _write(proj, "application/lesson/driving_layer/api/bc_error_schema.py", _LESSON_DYNAMIC_SRC)
        code, out = _run(CENT, proj, list(_T_ARGS))
        rows.append((
            "T 동적 Enum 토큰", 1, code,
            "DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED" in out and "dynamic Enum value" in out,
            "exit 1 진단 전건 토큰 → runtime proof 경로",
        ))

        # C1 — registry 2번 차분 결선(2026-08-15 재료 축 후속): 앵커 기존 base-canon
        #      위반은 강등되고, 앵커 이후 새로 생긴 «빈 골격 placeholder»(#114)는
        #      렌더 계약대로 inventory 에서 빼도 분석 오류가 아니다.
        cent_repo: Path = td / "cent"
        for rel, src in _T_FILES.items():
            _write(cent_repo, rel, src)
        _write(cent_repo, _LESSON_SCHEMA_REL, _LESSON_BASE_DEFAULT_SRC)
        proc = _git(cent_repo, "init", "-q")
        if proc.returncode != 0:
            raise RuntimeError(f"git init 실패: {proc.stderr.strip()}")
        anchor = _commit_all(cent_repo, "anchor with base-canon violation")
        _write(cent_repo, _PLACEHOLDER_REL, "")  # 앵커 이후 새 BC 의 빈 골격
        code, out = _run(CENT, cent_repo, [*_T_ARGS, "--anchor", anchor])
        rows.append((
            "C1 #2 기존분 강등·빈 골격 제외", 0, code,
            "신규분(앵커 이후) 0건" in out
            and "앵커 기존분(잔존) 1건" in out
            and "must preserve common required/default semantics" in out
            and "canonical candidate" not in out,
            "base-canon 기존분 강등 + placeholder 미계상",
        ))

        # C2 — C1 + 앵커 이후 신규 위반(raw string discriminator concrete): 같은 파일
        #      안에서 신규 진단만 red 로 남고 기존 진단은 기존분 절로 분리된다.
        cent_schema: Path = cent_repo / _LESSON_SCHEMA_REL
        cent_schema.write_text(
            cent_schema.read_text(encoding="utf-8") + _LESSON_RAW_CONCRETE_SRC,
            encoding="utf-8",
        )
        code, out = _run(CENT, cent_repo, [*_T_ARGS, "--anchor", anchor])
        new_section: str = out.split("== 신규분")[-1].split("== 앵커 기존분")[0]
        rows.append((
            "C2 #2 신규·기존 혼재 분리", 2, code,
            "신규분(앵커 이후) 2건" in out
            and "raw string FrameworkErrorSchema discriminator" in new_section
            and "앵커 기존분(잔존) 1건" in out,
            "신규 진단만 red·기존 진단은 보고 절",
        ))

    print("| 케이스 | 기대 exit | 실측 | 내용 | 판정 | 비고 |")
    print("|---|---|---|---|---|---|")
    bad: int = 0
    for name, want, got, content_ok, note in rows:
        ok: bool = want == got and content_ok
        if not ok:
            bad += 1
        print(f"| {name} | {want} | {got} | {'✓' if content_ok else '✗'} | {'✓' if ok else '✗ 불일치'} | {note} |")
    print(f"케이스 {len(rows)} · 일치 {len(rows) - bad} · 불일치 {bad}")
    return 0 if bad == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
