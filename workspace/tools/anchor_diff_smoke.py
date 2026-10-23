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
from types import ModuleType
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
# F4-89 바로 앞 배포판(dddjango 2.21.2) — Q40·Q41 «배포판과 같음» 대조의 옛 판. HEAD 로 잡으면 커밋 뒤 새 판 자신이 된다.
_RELEASED_2212_COMMIT: str = "c4e40615"
# #2 · #5 기준선이 코드 슬라이스까지 모으기 바로 앞 배포판(dddjango 2.22.1) — «트리 진단만 있는 앵커는 옛 판과 글자 같음» 대조의 옛 판(HEAD 금지).
_RELEASED_2221_COMMIT: str = "62a5e5db"
# F4-89 남은 몫(BC 이름 바꾸기 대응) · 앵커 사본 심링크 고침 바로 앞 배포판(dddjango 2.22.2) — «짝이 서지 않으면 옛 판과 글자 같음» 대조의 옛 판(HEAD 금지).
_RELEASED_2222_COMMIT: str = "2e86346f"

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

    def test_approved_flag_two_forms_and_usage_errors(self) -> None:
        rest: list[str]
        value: str | None
        error: str | None
        import anchor_diff
        for args in (["--approved-merge-file", "a.txt"], ["--approved-merge-file=a.txt"]):
            self.assertEqual(anchor_diff.split_approved_merge(["target", *args, "--ap", "config/api.py"]),
                             (["target", "--ap", "config/api.py"], "a.txt", None))
        for args, message in ((["--approved-merge-file"], "값이 없다"),
                              (["--approved-merge-file="], "값이 없다"),
                              (["--approved-merge-file", "a", "--approved-merge-file=b"], "한 번만 준다")):
            with self.subTest(args=args):
                rest, value, error = anchor_diff.split_approved_merge(args)
                self.assertIn(message, error)

    def test_default_drop_error_bcs_keeps_list_and_explicit_drop(self) -> None:
        import anchor_diff
        _write(self.snap, "application/orders/__init__.py", "")
        argv: list[str] = [str(self.snap), "--error-bc", "orders", "--scope-bc", "orders"]
        before: list[str] = anchor_diff._baseline_argv(CTX, self.snap, argv, frozenset())
        self.assertIsInstance(before, list)
        self.assertEqual(before, anchor_diff._baseline_argv(CTX, self.snap, argv, frozenset(), drop_error_bcs=frozenset()))
        after: list[str] = anchor_diff._baseline_argv(CTX, self.snap, argv, frozenset(), drop_error_bcs=frozenset({"orders"}))
        self.assertNotIn("--error-bc", after)


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


class UnnumberedDebtRegression(unittest.TestCase):
    """번호 없는 줄 빚의 전체 일치와 허용하지 않는 입력 꼴을 고정한다."""
    printed: str = ("- application/accounts/driving_layer/api/bc_error_schema.py:1: "
               "duplicate project code wire value: unknown_place_code: from enum import StrEnum")
    norm: str = printed.replace("bc_error_schema.py:1:", "bc_error_schema.py:N:")
    entry: str = "= check-error-centralization.py :: " + printed
    old_message: str = "`#<규칙번호> <부분문자열>`(규칙번호는 숫자)"
    form_message: str = "번호 없는 줄은 `= <검사기 파일> :: - <주어>: <메시지>`(검사기가 찍은 줄 전체 · 주어는 상대 경로)"

    def setUp(self) -> None:
        self.repo: Path
        self.anchor: str
        sys.path.insert(0, str(S))
        import anchor_diff
        self.diff: ModuleType = anchor_diff
        self.temp: tempfile.TemporaryDirectory[str] = tempfile.TemporaryDirectory(prefix="unnumbered-debt-")
        self.addCleanup(self.temp.cleanup)
        self.td: Path = Path(self.temp.name)
        self.repo, self.anchor = _init_repo(self.td, "repo", F / "skeleton/good_bc")
        _write(self.repo, "dirty.md", "dirty\n")

    def debt(self, *lines: str) -> Path:
        path: Path = self.td / "debt.txt"
        path.write_text("".join(line + "\n" for line in lines), encoding="utf-8")
        return path

    def partition(self, findings: list[str], debt: Path, script: Path = CENT) -> tuple[int, str]:
        out: io.StringIO = io.StringIO()
        with patch.object(self.diff, "_run_lines", side_effect=((0, []),)), contextlib.redirect_stdout(out):
            code: int = self.diff.partition_exit(script=script, label=f"[{script.stem}]", target=self.repo,
                anchor=self.anchor, argv=[str(self.repo)], findings=findings, debt_file=str(debt))
        return code, out.getvalue()

    def test_printed_and_normalized_forms_load_as_one_entry(self):
        rules: list[tuple[str, str]] = self.diff.load_debt(self.debt(self.entry, "= check-error-centralization.py :: " + self.norm))
        self.assertEqual(rules, [("=", "check-error-centralization.py :: " + self.norm)] * 2)

    def test_only_the_whole_line_matches(self):
        code: int
        out: str
        other_path: str = self.printed.replace("accounts", "fortune_saju")
        other_message: str = self.printed.replace("unknown_place_code", "unknown_place")
        longer: str = self.printed + " x"
        tagged: str = self.printed.replace("- ", "[#572] ", 1)
        moved: str = self.printed.replace("bc_error_schema.py:1:", "bc_error_schema.py:7:")
        code, out = self.partition([self.printed, other_path, other_message, longer, tagged, moved],
                                   self.debt(self.entry))
        self.assertEqual(code, 2, out)
        self.assertEqual(_section(out, "이관 빚"), {self.printed, moved})
        self.assertEqual(_section(out, "신규분"), {other_path, other_message, longer, tagged})

    def test_other_checker_does_not_match(self):
        code: int
        out: str
        code, out = self.partition([self.printed], self.debt(self.entry), script=CONTRACT)
        self.assertEqual(code, 2, out)
        self.assertIn("이관 빚 0건", out)
        code, out = self.partition([self.printed],
                                   self.debt("= check-api-error-controller-contract.py :: " + self.printed))
        self.assertEqual(code, 2, out)
        self.assertIn("이관 빚 0건", out)

    def test_numbered_entries_unchanged_and_cannot_cover_unnumbered_line(self):
        code: int
        out: str
        findings: list[str] = ["[#95] web/a.py: 위반", "[#96] web/b.py: 위반", self.printed]
        code, out = self.partition(findings, self.debt("#95 web/a.py", "#2 unknown_place_code"))
        self.assertEqual(code, 2, out)
        self.assertEqual(_section(out, "이관 빚"), {"[#95] web/a.py: 위반"})
        self.assertEqual(_section(out, "신규분"), {"[#96] web/b.py: 위반", self.printed})
        code, out = self.partition(findings, self.debt("#95 web/a.py", self.entry))
        self.assertEqual(code, 2, out)
        self.assertEqual(_section(out, "이관 빚"), {"[#95] web/a.py: 위반", self.printed})
        self.assertEqual(_section(out, "신규분"), {"[#96] web/b.py: 위반"})

    def test_registry_gate_line_shape_uses_the_same_predicate(self):
        rules: list[tuple[str, str]] = self.diff.load_debt(self.debt(self.entry))
        self.assertTrue(self.diff.debt_match("check-error-centralization.py :: " + self.norm, rules))
        self.assertFalse(self.diff.debt_match("check-api-error-controller-contract.py :: " + self.norm, rules))
        self.assertFalse(self.diff.debt_match(self.norm, rules))

    def test_valid_nonemitted_entry_loads_and_leaves_new(self) -> None:
        # 최종 리뷰 사소 3: 형식상 유효하지만 실제로 나오지 않는 줄까지 로더가 거절하지는 않는다.
        debt: Path = self.debt("= check-openapi-error-declaration.py :: " + self.printed,
                              "= check-error-centralization.py :: - ./application/a.py: m")
        self.assertEqual(self.diff.load_debt(debt), [
            ("=", "check-openapi-error-declaration.py :: " + self.norm),
            ("=", "check-error-centralization.py :: - ./application/a.py: m"),
        ])
        code: int
        out: str
        code, out = self.partition([self.printed], debt, script=CENT)
        self.assertEqual(code, 2, out)
        self.assertIn("이관 빚 0건", out)
        self.assertEqual(_section(out, "신규분"), {self.printed})

    def test_invalid_entry_forms_are_usage_errors(self):
        checker_message: str = ("번호 없는 줄의 검사기는 check-api-error-controller-contract.py · check-composition-root.py · "
                           "check-context-isolation.py · check-error-centralization.py · "
                           "check-openapi-error-declaration.py 가운데 하나")
        cases: dict[str, str] = {
            "= check-nothing.py :: " + self.printed: checker_message,
            "= check-naming.py :: " + self.printed: checker_message,
            "= check-error-centralization.py :: [#572] application/a.py:1: m": self.form_message,
            "= check-error-centralization.py :: - /abs/application/a.py:1: m": self.form_message,
            "= check-error-centralization.py :: - application/a.py": self.form_message,
            "= check-error-centralization.py " + self.printed: self.form_message,
            "=check-error-centralization.py :: " + self.printed: self.form_message,
            self.printed: self.old_message,
        }
        for raw, message in cases.items():
            with self.subTest(raw=raw):
                path: Path = self.debt(raw)
                expected: str = f"빚 목록 줄 형식 오류: {raw!r} — {message}"
                with self.assertRaises(self.diff.AnchorDiffUsage) as caught:
                    self.diff.load_debt(path)
                self.assertEqual(str(caught.exception), expected)
                with self.assertRaises(self.diff.AnchorDiffUsage) as validated:
                    self.diff.validate_materials(self.repo, self.anchor, str(path))
                self.assertEqual(str(validated.exception), expected)

    def test_debt_line_checkers_are_the_partition_exit_callers(self):
        callers: set[str] = {p.name for p in S.glob("check-*.py") if "anchor_diff.partition_exit(" in p.read_text(encoding="utf-8")}
        self.assertEqual(self.diff._DEBT_LINE_CHECKERS, frozenset(callers))

    def test_real_reg02_collision_line_recorded_and_other_checker_not(self):
        code: int
        out: str
        line: str
        repo: Path = self.td / "cent"
        for rel, source in _T_FILES.items():
            _write(repo, rel, source)
        self.assertEqual(_git(repo, "init", "-q").returncode, 0)
        anchor: str = _commit_all(repo, "code contract")
        rel: str = "application/report/driving_layer/api/bc_error_schema.py"
        _write(repo, rel, _LESSON_STATIC_SRC.replace("Lesson", "Report"))
        extra: list[str] = [*_T_ARGS, "--scope-bc", "report", "--error-bc", "report", "--project-code-error-module", rel,
                 "--anchor", anchor]
        code, out = _run(CENT, repo, extra)
        self.assertEqual(code, 2, out)
        (line,) = _section(out, "신규분")
        self.assertRegex(line, r"^- application/lesson/driving_layer/api/bc_error_schema\.py:\d+: "
                               r"duplicate project code wire value: lesson_not_found: from enum import StrEnum$")
        code, out = _run(CENT, repo, [*extra, "--legacy-debt-file",
                                      str(self.debt("= check-error-centralization.py :: " + line))])
        self.assertEqual(code, 0, out)
        self.assertIn("신규분(앵커 이후) 0건 · 앵커 기존분(잔존) 0건 · 이관 빚 1건", out)
        self.assertEqual(_section(out, "이관 빚"), {line})
        code, out = _run(CENT, repo, [*extra, "--legacy-debt-file",
                                      str(self.debt("= check-composition-root.py :: " + line))])
        self.assertEqual(code, 2, out)
        self.assertEqual(_section(out, "신규분"), {line})


class BaselineSliceRegression(unittest.TestCase):
    """기준선 재실행(`--anchor-baseline`)도 트리 · 코드 슬라이스를 끝까지 모은다 — #2 · #5(#15 는 2026-09-10 F4-8).

    앵커에 트리 진단이 하나라도 있으면 기준선이 트리 줄에서 끝나 옛 코드 줄이 전부 «신규» 가 되던 결함의 고정이다.
    풀리는 쪽 · 여전히 막는 쪽 · 반대로 막히는 쪽 · 기준선 사다리 두 갈래 · 받아들인 한계를 실제 렌더로 단언한다."""

    api: str = "application/billing/driving_layer/api"
    ctrl: str = "application/lesson/driving_layer/controller.py"
    note: dict[str, str] = {"docs/lane_note.md": "레인은 문서 한 장만 더했다\n"}
    # 무관한 영역(billing)의 트리 진단 — 코드 슬라이스가 대표하지 않는 꼴(scope 밖 #114 · 고른 모듈 밖 monkeypatch).
    tree02: dict[str, str] = {api + "/api_router.py": "ROUTES: list = []\n"}
    tree05: dict[str, str] = {api + "/docs_patch.py": "def patch(api):\n    api.openapi_schema = None\n"}
    t114: str = ("[#114] " + api + ": `bc_error_schema.py` 가 없다 — HTTP 오류를 아직 안 여는 BC 에도 "
                 "«빈 파일»로 항상 있다(부모 api/ 가 항상이라)")
    t63: str = "[#63] " + api + "/docs_patch.py:N: `openapi_schema` monkeypatch — OpenAPI 를 사후 변형하지 않는다"
    c572: str = ("[#572] " + _LESSON_SCHEMA_REL + ":N: BC base must preserve common required/default semantics: "
                 "code: LessonErrorCode = LessonErrorCode.NOT_FOUND")
    # #2 «트리 줄 = 코드 줄» 재료 — 정본 ErrorCode 가 StrEnum 이 아니다(#636). 둘째 컨테이너(legacy)는 트리 슬라이스만 본다.
    code636: str = _LESSON_STATIC_SRC.replace("class LessonErrorCode(StrEnum)", "class LessonErrorCode(str)")
    legacy: str = '\n\nclass LessonLegacyErrorCode(str):\n    OLD = "lesson_old"\n'
    c636: str = "[#636] " + _LESSON_SCHEMA_REL + ":N: LessonErrorCode must directly inherit enum.StrEnum: class LessonErrorCode(str):"
    t636: str = ("[#636] " + _LESSON_SCHEMA_REL + ": `LessonLegacyErrorCode` 는 `StrEnum` 이어야 한다 — "
                 "Literal·맨 문자열 상수 모음으로 대신하지 않는다")
    # #5 코드 줄 재료 — 404 를 직접 돌려주는데 response= 에 없다.
    missing: str = ("from ninja import Router, Status\n"
                    "from application.lesson.driving_layer.api.bc_error_schema import LessonNotFoundError\n\n"
                    "router = Router()\n\n\n"
                    '@router.get("/{lesson_id}", response={200: dict})\n'
                    "def get_lesson(request, lesson_id: int):\n"
                    "    if lesson_id == 0:\n"
                    "        error = LessonNotFoundError()\n"
                    "        return Status(error.status, error)\n"
                    '    return {"id": lesson_id}\n')
    c404: str = "[#63] " + ctrl + ":N: missing-response: " + ctrl + ":N:get_lesson 직접 반환 오류 status 404가 response=에서 누락"
    # #5 «사건 하나» 재료 — 트리 줄(responses 보충)과 코드 줄(openapi-extra)이 같은 사건을 가리킨다.
    extra: str = ("from ninja import Router\n\nrouter = Router()\n\n\n"
                  '@router.get("/{lesson_id}", response={200: dict}, '
                  'openapi_extra={"responses": {404: {"description": "none"}}})\n'
                  "def get_lesson(request, lesson_id: int):\n"
                  '    return {"id": lesson_id}\n')
    extra_code: str = "[#63] " + ctrl + ":N: openapi-extra: " + ctrl + ":N:get_lesson 오류 responses [404]를 openapi_extra로 수동 선언"
    extra_tree: str = ("[#63] " + ctrl + ":N: `openapi_extra` 의 responses 보충 — 오류 응답은 `response=` 에 그 status 의 실제 오류 타입 "
                       "그대로 직접 선언한다(허용은 `response=` 에 선언된 성공 status 의 리터럴 메타데이터 보충뿐)")
    sel05: list[str] = _T_ARGS[:-4]  # #5 는 inventory selector(--project-code-error-module)를 받지 않는다
    pre05: list[str] = ["--error-profile", "preserve-established", "--scope", "public-v1", "--api-module", "config/api.py",
                        "--controller-module", ctrl, "--scope-bc", "lesson"]
    selector: str = "기준선=selector 렌더 재실행):"

    def setUp(self) -> None:
        self.temp: tempfile.TemporaryDirectory[str] = tempfile.TemporaryDirectory(prefix="baseline-slice-")
        self.addCleanup(self.temp.cleanup)
        self.td: Path = Path(self.temp.name)

    def tree(self, name: str, files: dict[str, str]) -> Path:
        root: Path = self.td / name
        for rel, source in {**_T_FILES, **files}.items():
            _write(root, rel, source)
        return root

    def lane(self, name: str, anchor: dict[str, str], change: dict[str, str], *, commit: bool = True) -> tuple[Path, str]:
        """앵커 커밋(_T_FILES + anchor) 위에 레인 변경을 얹는다 — commit=False 면 작업 트리에만 둔다."""
        repo: Path = self.tree(name, anchor)
        self.assertEqual(_git(repo, "init", "-q").returncode, 0)
        sha: str = _commit_all(repo, "anchor")
        for rel, source in change.items():
            _write(repo, rel, source)
        if commit:
            _commit_all(repo, "lane")
        return repo, sha

    def assert_diff(self, result: tuple[int, str], code: int, new: set[str], existing: set[str],
                    baseline: str | None = None) -> str:
        actual: int
        out: str
        actual, out = result
        normalize = lambda lines: {re.sub(r":\d+(?=:|\b)", ":N", line) for line in lines}
        self.assertEqual(actual, code, out)
        self.assertIn(self.selector if baseline is None else baseline, out)
        self.assertEqual(normalize(_section(out, "신규분")), new, out)
        self.assertEqual(normalize(_section(out, "앵커 기존분")), existing, out)
        return out

    def released(self) -> Path:
        """2.22.1 배포 커밋의 scripts 사본 — 옛 판은 HEAD 가 아니라 상수에 묶는다(이 고침을 커밋한 뒤에도 옛 판이다)."""
        old: Path = self.td / "released-2221"
        old.mkdir()
        archive: subprocess.CompletedProcess[bytes] = subprocess.run(
            ["git", "-C", str(ROOT), "archive", _RELEASED_2221_COMMIT, "dddjango/scripts"], capture_output=True, check=True)
        subprocess.run(["tar", "-x", "-C", str(old)], input=archive.stdout, check=True)
        return old / "dddjango" / "scripts"

    def test_A1_reg02_other_bc_tree_diagnostic_keeps_old_code_line_existing(self) -> None:
        repo: Path
        anchor: str
        repo, anchor = self.lane("a1", {_LESSON_SCHEMA_REL: _LESSON_BASE_DEFAULT_SRC, **self.tree02}, self.note)
        self.assert_diff(_run(CENT, repo, [*_T_ARGS, "--anchor", anchor]), 0, set(), {self.t114, self.c572})

    def test_A5b_reg02_single_old_event_code_text_is_existing(self) -> None:
        # 옛 사건 하나(#636 StrEnum 아님)가 inventory 에만 있다 — 현재는 코드 줄이 대표하고 트리 줄은 지워진다.
        repo: Path
        anchor: str
        rel: str = self.api + "/bc_error_schema.py"
        source: str = (_LESSON_STATIC_SRC.replace("Lesson", "Billing").replace("lesson_", "billing_")
                       .replace("(StrEnum)", "(str)"))
        repo, anchor = self.lane("a5b", {rel: source}, self.note)
        self.assert_diff(_run(CENT, repo, [*_T_ARGS, "--project-code-error-module", rel, "--anchor", anchor]), 0, set(),
                         {"[#636] " + rel + ":N: BillingErrorCode must directly inherit enum.StrEnum: class BillingErrorCode(str):"})

    def test_B1_reg05_other_bc_tree_diagnostic_keeps_old_code_line_existing(self) -> None:
        repo: Path
        anchor: str
        repo, anchor = self.lane("b1", {self.ctrl: self.missing, **self.tree05}, self.note)
        self.assert_diff(_run(OPENAPI, repo, [*self.sel05, "--anchor", anchor]), 0, set(), {self.t63, self.c404})

    def test_B3_reg05_single_old_event_code_text_is_existing(self) -> None:
        repo: Path
        anchor: str
        repo, anchor = self.lane("b3", {self.ctrl: self.extra}, self.note)
        self.assert_diff(_run(OPENAPI, repo, [*self.sel05, "--anchor", anchor]), 0, set(), {self.extra_code})

    def test_B4b_reg05_preserve_touched_file_keeps_repo_scan_line_existing(self) -> None:
        # preserve 렌더: 옛 연산이 있는 파일을 레인이 커밋 전에 주석 한 줄만 건드렸다 — 저장소 전수 줄도 앵커에 있던 줄이다.
        repo: Path
        anchor: str
        repo, anchor = self.lane("b4b", {self.ctrl: self.extra}, {self.ctrl: self.extra + "\n\n# 레인이 주석 한 줄만 더했다\n"},
                                 commit=False)
        self.assert_diff(_run(OPENAPI, repo, [*self.pre05, "--anchor", anchor]), 0, set(), {
            self.extra_tree,
            "[#63] " + self.ctrl + ": operation 'get_lesson' (오류 [404] 가 openapi_extra 에만·response= 누락)"})

    def test_guard_reg02_only_lane_lines_stay_new(self) -> None:
        # 막는 쪽 가드: 옛 줄이 기존분으로 가도 레인이 만든 다른 글자 줄은 신규로 남는다.
        repo: Path
        anchor: str
        repo, anchor = self.lane("guard02", {_LESSON_SCHEMA_REL: _LESSON_BASE_DEFAULT_SRC, **self.tree02},
                                 {_LESSON_SCHEMA_REL: _LESSON_BASE_DEFAULT_SRC + _LESSON_RAW_CONCRETE_SRC})
        prefix: str = "- " + _LESSON_SCHEMA_REL + ":N: "
        out: str = self.assert_diff(_run(CENT, repo, [*_T_ARGS, "--anchor", anchor]), 2, {
            prefix + 'raw string FrameworkErrorSchema discriminator: code: LessonErrorCode = "lesson_expired"',
            prefix + 'concrete discriminator default must use own ErrorCode member: code: LessonErrorCode = "lesson_expired"',
        }, {self.t114, self.c572})
        self.assertIn("신규분(앵커 이후) 2건 · 앵커 기존분(잔존) 2건", out)

    def test_guard_reg05_only_lane_line_stays_new(self) -> None:
        repo: Path
        anchor: str
        added: str = ('\n\n@router.get("/other", response={200: dict}, openapi_extra={"responses": {410: {"description": "gone"}}})\n'
                      "def get_other(request):\n    return {}\n")
        repo, anchor = self.lane("guard05", {self.ctrl: self.missing, **self.tree05}, {self.ctrl: self.missing + added})
        out: str = self.assert_diff(_run(OPENAPI, repo, [*self.sel05, "--anchor", anchor]), 2, {
            "[#63] " + self.ctrl + ":N: openapi-extra: " + self.ctrl + ":N:get_other 오류 responses [410]를 openapi_extra로 수동 선언",
        }, {self.t63, self.c404})
        self.assertIn("신규분(앵커 이후) 1건 · 앵커 기존분(잔존) 2건", out)

    def test_reverse_reg05_event_edited_to_tree_only_becomes_new(self) -> None:
        # 반대 방향: 앵커에서 코드 줄이 대표하던 사건을 레인이 손대(dict 를 모듈 상수로 뺌) 현재에는 트리 줄로만 나온다.
        # 기준선에는 코드 글자만 있으므로 그 트리 줄은 신규다 — 레인이 그 자리를 건드렸을 때만 · #15 와 같은 동작.
        repo: Path
        anchor: str
        moved: str = (self.extra.replace("router = Router()\n", 'router = Router()\n\nNOT_FOUND = {404: {"description": "none"}}\n')
                      .replace('{"responses": {404: {"description": "none"}}}', '{"responses": NOT_FOUND}'))
        self.assertIn('openapi_extra={"responses": NOT_FOUND}', moved)
        repo, anchor = self.lane("reverse", {self.ctrl: self.extra}, {self.ctrl: moved})
        self.assert_diff(_run(OPENAPI, repo, [*self.sel05, "--anchor", anchor]), 2, {self.extra_tree}, set())

    def test_reverse_reg02_fixing_canonical_code_makes_other_old_tree_line_new(self) -> None:
        # 반대 방향의 넓은 꼴: #2 는 코드 줄 하나가 같은 (규칙, 파일)의 트리 줄을 모두 지운다. 앵커의 옛 #636 둘 가운데
        # 레인이 정본만 고치면, 기준선에서 지워졌던 다른 옛 트리 줄이 현재에 드러나 신규가 된다(레인이 손대지 않은 줄).
        repo: Path
        anchor: str
        repo, anchor = self.lane("reverse02", {_LESSON_SCHEMA_REL: self.code636 + self.legacy},
                                 {_LESSON_SCHEMA_REL: _LESSON_STATIC_SRC + self.legacy})
        self.assert_diff(_run(CENT, repo, [*_T_ARGS, "--anchor", anchor]), 2, {self.t636}, set())

    def test_debt_entry_for_old_code_line_moves_to_existing(self) -> None:
        # 2.22.1 에서 우회로로 빚 목록에 적어 둔 옛 코드 줄(A-1 · B-1 꼴): 빚은 남은 신규에만 걸리므로 이제 기존분으로 가고
        # 이관 빚은 0건이다(exit 는 그대로 0 — 그 빚 줄은 지워도 된다).
        repo: Path
        anchor: str
        for name, script, selectors, files, entry, existing in (
            ("debt02", CENT, _T_ARGS, {_LESSON_SCHEMA_REL: _LESSON_BASE_DEFAULT_SRC, **self.tree02},
             "#572 BC base must preserve", {self.t114, self.c572}),
            ("debt05", OPENAPI, self.sel05, {self.ctrl: self.missing, **self.tree05}, "#63 missing-response", {self.t63, self.c404}),
        ):
            with self.subTest(checker=script.name):
                repo, anchor = self.lane(name, files, self.note)
                debt: Path = self.td / (name + ".txt")
                debt.write_text(entry + "\n", encoding="utf-8")
                out: str = self.assert_diff(
                    _run(script, repo, [*selectors, "--anchor", anchor, "--legacy-debt-file", str(debt)]), 0, set(), existing)
                self.assertIn("신규분(앵커 이후) 0건 · 앵커 기존분(잔존) 2건 · 이관 빚 0건", out)
                self.assertEqual(_section(out, "이관 빚"), set(), out)

    def test_ladder_rung2_reg05_skeleton_error_bc_keeps_old_code_line_existing(self) -> None:
        # 앵커의 selector 렌더가 서지 않는 까닭이 빈 골격 --error-bc 면 사다리 2칸이 선다 — 트리 진단이 있어도
        # 걷은 렌더가 코드 줄까지 모으므로 옛 코드 줄은 기존분이다(`기준선 오류:` 줄 없음).
        repo: Path
        anchor: str
        report: str = "application/report/driving_layer"
        repo, anchor = self.lane("rung2", {
            self.ctrl: self.missing, **self.tree05,
            report + "/api/bc_error_schema.py": "", report + "/controller.py": "def get_report(request): return {}\n",
        }, {report + "/api/bc_error_schema.py": _LESSON_STATIC_SRC.replace("Lesson", "Report").replace("lesson_", "report_")})
        out: str = self.assert_diff(
            _run(OPENAPI, repo, [*self.sel05, "--controller-module", report + "/controller.py", "--scope-bc", "report",
                                 "--error-bc", "report", "--anchor", anchor]),
            0, set(), {self.t63, self.c404},
            "기준선=selector 렌더 재실행(빈 골격 --error-bc 걷음: report · 그 영역 아래 줄 제외) + positional 기준선):")
        self.assertNotIn("기준선 오류:", out)

    def test_ladder_positional_reg02_unanalyzable_anchor_shows_baseline_error(self) -> None:
        # 앵커의 코드 분석이 서지 않고(동적 Enum 값) 2칸도 없으면 positional 로 내려간다 — 가려져 있던 오류가
        # `기준선 오류:` 로 보이고, 셈과 exit 는 트리 줄만 있던 옛 기준선과 같다.
        repo: Path
        anchor: str
        repo, anchor = self.lane("positional", {_LESSON_SCHEMA_REL: _LESSON_DYNAMIC_SRC, **self.tree02},
                                 {_LESSON_SCHEMA_REL: _LESSON_DYNAMIC_SRC + _LESSON_RAW_CONCRETE_SRC})
        out: str = self.assert_diff(_run(CENT, repo, [*_T_ARGS, "--anchor", anchor]), 2, {
            "- " + _LESSON_SCHEMA_REL + ':N: raw string FrameworkErrorSchema discriminator: code: LessonErrorCode = "lesson_expired"',
        }, {self.t114}, "기준선=positional 기준선(selector 렌더 불능 강등 — selector-lane 진단은 전량 신규 취급)):")
        self.assertIn("  기준선 오류: [check-error-centralization] 사용 오류: DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED ", out)

    def test_direct_baseline_exit_codes_tree_only_tree_code_and_analysis_failure(self) -> None:
        # 끝 블록의 계약: 진단 없음 = 0(아무것도 찍지 않는다) · 트리 줄만 = 2(차분으로 되들어가지 않고 끝난다) ·
        # 트리 + 코드 = 2(둘 다 찍는다) · 코드 분석 불능 = 1.
        code: int
        out: str
        for script, args, tree, coded, broken, tree_mark, code_mark in (
            (CENT, _T_ARGS, self.tree02, {_LESSON_SCHEMA_REL: _LESSON_BASE_DEFAULT_SRC},
             {_LESSON_SCHEMA_REL: _LESSON_DYNAMIC_SRC}, "[#114] " + self.api + ":", "BC base must preserve"),
            (OPENAPI, self.sel05, self.tree05, {self.ctrl: self.missing},
             {"framework/ninja/framework_error_schema.py": "invalid syntax ???\n"}, "`openapi_schema` monkeypatch", "missing-response"),
        ):
            for kind, files, want in (("clean", {}, 0), ("tree", tree, 2), ("tree-code", {**tree, **coded}, 2),
                                      ("analysis", {**tree, **broken}, 1)):
                with self.subTest(checker=script.name, kind=kind):
                    code, out = _run(script, self.tree(script.stem + "-" + kind, files), [*args, "--anchor-baseline"])
                    self.assertEqual(code, want, out)
                    if kind == "clean":
                        # 깨끗한 사본의 exit 0 은 승인 병합의 «M^1 에 없다» 증명이 기대는 값이다(끝 블록의 `else 0`).
                        self.assertEqual(out, "")
                        continue
                    self.assertIn(tree_mark, out)
                    self.assertEqual(code_mark in out, kind == "tree-code", out)
                    self.assertEqual("사용 오류" in out, kind == "analysis", out)
                    self.assertNotIn("앵커 차분", out)

    def test_tree_only_anchor_output_matches_released_2221(self) -> None:
        # 코드 슬라이스가 대표하지 않는 트리 진단만 있는 앵커 — 출력이 2.22.1 과 글자 그대로다(끝 블록이 없으면 머리 줄이 바뀐다).
        repo: Path
        anchor: str
        old: Path = self.released()
        wrong_name: dict[str, str] = {self.api + "/bc_error_schema.py": "", self.api + "/error_schemas.py": "X: int = 1\n"}  # #568
        for name, script, files, selectors in (("r02-114", CENT, self.tree02, _T_ARGS), ("r02-568", CENT, wrong_name, _T_ARGS),
                                               ("r05-63", OPENAPI, self.tree05, self.sel05)):
            repo, anchor = self.lane(name, files, self.note)
            for argv in ([*selectors, "--anchor", anchor], ["--anchor", anchor]):
                with self.subTest(case=name, selector=len(argv) > 2):
                    result: tuple[int, str] = _run(script, repo, argv)
                    self.assertEqual(result, _run(old / script.name, repo, argv))
                    self.assertEqual(result[0], 0, result[1])
                    self.assertIn(self.selector, result[1])
                    self.assertIn("신규분(앵커 이후) 0건 · 앵커 기존분(잔존) 1건", result[1])
        # 옛 판이 정말 옛 판인지 — 옛 코드 줄이 함께 있는 앵커(A-1)에서는 두 판이 갈려야 한다.
        repo, anchor = self.lane("contrast", {_LESSON_SCHEMA_REL: _LESSON_BASE_DEFAULT_SRC, **self.tree02}, self.note)
        self.assertEqual(_run(old / CENT.name, repo, [*_T_ARGS, "--anchor", anchor])[0], 2)
        self.assertEqual(_run(CENT, repo, [*_T_ARGS, "--anchor", anchor])[0], 0)

    def test_한계_same_text_line_added_by_lane_is_existing(self) -> None:
        # 알려진 한계(2.22.0 노트 «같은 글자의 줄»): 대조는 줄 번호를 지운 글자의 집합이다. 레인이 옛 줄과 글자가 같은
        # 새 위반을 더하면 기존분으로 간다 — 앵커에 트리 진단이 있어도 없는 앵커와 같은 모델이다(성공 보장이 아니라 고정).
        repo: Path
        anchor: str
        field: str = ('\n\nclass Lesson{name}Error(LessonErrorSchema):\n    code: LessonErrorCode = LessonErrorCode.NOT_FOUND\n'
                      '    title: str = "Lesson {name}"\n    status: int = 410\n    detail: str = "The lesson is {name}."\n'
                      '    missing: str = ""\n')
        before: str = _LESSON_STATIC_SRC + field.format(name="Gone")
        prefix: str = "- " + _LESSON_SCHEMA_REL + ":N: "
        same: set[str] = {prefix + 'additional public field: missing: str = ""',
                          prefix + 'concrete adds field outside common shape: missing: str = ""'}
        for name, tree, lines in (("plain", {}, same), ("tree", self.tree02, same | {self.t114})):
            with self.subTest(anchor=name):
                repo, anchor = self.lane("limit-" + name, {_LESSON_SCHEMA_REL: before, **tree},
                                         {_LESSON_SCHEMA_REL: before + field.format(name="Locked")})
                out: str = self.assert_diff(_run(CENT, repo, [*_T_ARGS, "--anchor", anchor]), 0, set(), lines)
                self.assertIn(f"앵커 기존분(잔존) {4 + len(tree)}건", out)  # 레인의 두 줄도 기존분에 섞여 보고된다

    def test_한계_reg02_code_line_hides_other_tree_lines_of_same_rule_and_file(self) -> None:
        # 알려진 한계: #2 의 억제 키는 (규칙, 파일)이라 코드 #636 한 줄이 그 파일의 트리 #636 을 모두 지운다. 정본 ErrorCode 가
        # 이미 StrEnum 이 아닌 파일에 레인이 StrEnum 아닌 둘째 `*ErrorCode` 를 더하면, 그 줄은 찍히지도 않고 이 검사기는 exit 0 이다.
        # 같은 꼴을 registry_gate(positional #2 의 트리 줄)와 #117(check-context-isolation — 둘째 ErrorCode 컨테이너)이 막으므로
        # G2 전체로는 통과하지 않는다. 트리 진단 없는 앵커에서는 배포판도 이렇게 센다(성공 보장이 아니라 고정).
        repo: Path
        anchor: str
        repo, anchor = self.lane("limit-636", {_LESSON_SCHEMA_REL: self.code636}, {_LESSON_SCHEMA_REL: self.code636 + self.legacy})
        out: str = self.assert_diff(_run(CENT, repo, [*_T_ARGS, "--anchor", anchor]), 0, set(), {self.c636})
        self.assertNotIn("LessonLegacyErrorCode", out)


class ApprovedInflowRepo:
    """설계 v3 §7의 실제 검사기용 git 재료. 모든 쓰기는 시험 임시 폴더 안이다."""

    port: str = "application/accounts/application_layer/port/billing_zulu_port.py"
    fixed: str = "application/xbc/composition_root/wiring_material.py"
    error: str = "application/{bc}/driving_layer/api/bc_error_schema.py"

    def __init__(self, td: Path, name: str):
        self.root: Path = td / name
        self.root.mkdir()
        self.git("init", "-q", "-b", "main")

    def git(self, *args: str) -> str:
        proc: subprocess.CompletedProcess[str] = _git(self.root, *args)
        if proc.returncode:
            raise RuntimeError(f"git {args}: {proc.stdout}{proc.stderr}")
        return proc.stdout.strip()

    def write(self, rel: str, src: str = "") -> None:
        _write(self.root, rel, src)

    def rm(self, rel: str) -> None:
        path: Path = self.root / rel
        if path.is_dir() and not path.is_symlink():
            shutil.rmtree(path)
        else:
            path.unlink()

    def commit(self, message: str) -> str:
        return _commit_all(self.root, message)

    def checkout(self, ref: str, branch: str | None = None) -> None:
        self.git("checkout", "-q", *(["-b", branch] if branch else []), ref)

    def merge(self, ref: str = "main", *, pending: bool = False) -> str:
        self.git("merge", "-q", "--no-ff", *( ["--no-commit"] if pending else ["-m", "approved merge"]), ref)
        return self.git("rev-parse", "HEAD")

    def approved(self, *shas: str) -> Path:
        path: Path = self.root.parent / (self.root.name + "-approved.txt")
        path.write_text("".join(sha + " approved\n" for sha in shas), encoding="utf-8")
        return path

    def bc(self, bc: str) -> None:
        tree: ModuleType = _checker_module(S / "standard_tree.py")
        def fixed(parent: str, row) -> None:
            for child in tree.children(row):
                if child.kind == "placeholder":
                    continue
                name: str = child.name.replace("<bounded_context>", bc)
                rel: str = parent + "/" + name.rstrip("/")
                if name.endswith("/"):
                    self.write(rel + "/__init__.py")
                    fixed(rel, child)
                else:
                    self.write(rel)
        base: str = "application/" + bc
        self.write(base + "/__init__.py")
        fixed(base, tree.ROWS[0])
        self.write(base + "/driving_layer/api/api_router.py",
                   f"from ninja_extra import NinjaExtraAPI\n\ndef register_{bc}_api(api: NinjaExtraAPI) -> None:\n    pass\n")

    def project(self, *bcs: str) -> None:
        for directory in ("application", "framework", "framework/ninja", "framework/broker",
                          "framework/broker/internal", "framework/broker/external", "framework/pure",
                          "framework/test", "framework/test/fake", "framework/test/unit", "config", "config/settings"):
            self.write(directory + "/__init__.py")
        for kind in ("internal", "external"):
            for suffix in ("", "_port"):
                self.write(f"framework/broker/{kind}/{kind}_broker{suffix}.py")
        self.write("manage.py", 'import os\nos.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.base")\n')
        self.write("config/settings/base.py", "INSTALLED_APPS: list[str] = []\n")
        self.write("config/api.py", "from ninja_extra import NinjaExtraAPI\n\napi: NinjaExtraAPI = NinjaExtraAPI()\n")
        for name in ("urls", "asgi", "wsgi", "celery"):
            self.write(f"config/{name}.py")
        self.write("framework/ninja/framework_error_schema.py",
                   "from ninja import Schema\n\nclass FrameworkErrorSchema(Schema):\n    error: str\n    message: str\n")
        for bc in bcs:
            self.bc(bc)

    def schema(self, bc: str, wire: str, *, extra: bool = False) -> None:
        prefix: str = "".join(word.title() for word in bc.split("_"))
        self.write(self.error.format(bc=bc),
            "from enum import StrEnum\nfrom framework.ninja.framework_error_schema import FrameworkErrorSchema\n\n"
            f'class {prefix}ErrorCode(StrEnum):\n    UNKNOWN = "{wire}"\n\n'
            f"class {prefix}ErrorSchema(FrameworkErrorSchema):\n    error: {prefix}ErrorCode\n\n"
            f"class UnknownPlaceError({prefix}ErrorSchema):\n    error: {prefix}ErrorCode = {prefix}ErrorCode.UNKNOWN\n"
            '    message: str = "Place is unknown."\n' + ('    missing: str = ""\n' if extra else ""))

    def controller(self, bc: str, *, legacy: bool = False) -> None:
        base: str = f"application/{bc}"
        api: str = base + "/driving_layer/api/place"
        for directory in (base + "/application_layer/place", api, api + "/schema"):
            self.write(directory + "/__init__.py")
        for name in ("in", "out"):
            self.write(api + f"/schema/schema_{name}.py")
        source: str = ('from ninja import Router\n\nrouter: Router = Router()\n\n'
                       '@router.get("/place", response={200: str})\ndef get_place(request: object) -> str:\n    return "ready"\n')
        if legacy:
            prefix: str = "".join(word.title() for word in bc.split("_"))
            use: str = base + "/application_layer/place/read_place"
            self.write(use + "/__init__.py")
            self.write(use + "/read_place_use_case.py",
                       "class ReadPlaceUseCase:\n    def execute(self, place_id: int) -> str:\n        return str(place_id)\n")
            for kind in ("command", "query", "result"):
                self.write(use + f"/read_place_{kind}.py")
            self.write(base + "/composition_root/dependency_wiring.py",
                f"from application.{bc}.application_layer.place.read_place.read_place_use_case import ReadPlaceUseCase\n\n"
                "def build_read_place_use_case() -> ReadPlaceUseCase:\n    return ReadPlaceUseCase()\n")
            source = ("from ninja import Router, Status\n"
                f"from application.{bc}.application_layer.place.read_place.read_place_use_case import ReadPlaceUseCase\n"
                f"from application.{bc}.composition_root.dependency_wiring import build_read_place_use_case\n"
                f"from application.{bc}.driving_layer.api.bc_error_schema import {prefix}ErrorSchema, UnknownPlaceError\n\n"
                "router: Router = Router()\n\n"
                '@router.get("/place", response={200: str, 404: UnknownPlaceError})\n'
                f"def get_place(request: object, place_id: int) -> str | Status[{prefix}ErrorSchema]:\n"
                "    use_case: ReadPlaceUseCase = build_read_place_use_case()\n    try:\n"
                "        result: str = use_case.execute(place_id)\n    except Exception:\n"
                "        return Status(404, UnknownPlaceError())\n    return result\n")
        self.write(api + "/place_controller.py", source)

    def rename_bc(self, old: str, new: str) -> None:
        dest: Path = self.root / "application" / new
        (self.root / "application" / old).rename(dest)
        for path in dest.rglob("*.py"):
            source: str = path.read_text(encoding="utf-8")
            path.write_text(source.replace("".join(w.title() for w in old.split("_")),
                                            "".join(w.title() for w in new.split("_"))).replace(old, new), encoding="utf-8")

    def selectors(self, bcs: tuple[str, ...], *, inventory: bool = False) -> list[str]:
        argv: list[str] = ["--error-profile", "dddjango-code-json", "--scope", "f89-code", "--api-module", "config/api.py"]
        for bc in bcs:
            argv += ["--controller-module", f"application/{bc}/driving_layer/api/place/place_controller.py",
                     "--scope-bc", bc, "--error-bc", bc]
        if inventory:
            for rel in ("framework/ninja/framework_error_schema.py", *(self.error.format(bc=bc) for bc in bcs)):
                argv += ["--project-code-error-module", rel]
        return argv

    def cause_merge(self, *, drop_in_merge: bool = False, before: bool = False) -> tuple[str, str]:
        self.project("accounts", "orders")
        if not before:
            self.write(self.port, "")
        if before:
            self.bc("billing")
        anchor: str = self.commit("anchor")
        self.checkout(anchor, "lane")
        self.write("lane.txt", "lane\n")
        if before:
            self.rm("application/billing")
        self.commit("lane before merge")
        self.checkout("main")
        if before:
            self.rm("application/billing")
            self.write(self.port, "")
        else:
            self.bc("billing")
        self.commit("upstream cause")
        self.checkout("lane")
        self.merge(pending=drop_in_merge)
        if drop_in_merge:
            self.rm("application/billing")
            self.commit("merge drops cause")
        return anchor, self.git("rev-parse", "HEAD")

    def ledger(self) -> tuple[str, str]:
        self.project("accounts", "decisive_fortune", "fortune_house", "service_policy")
        self.schema("accounts", "unknown_place_code")
        self.schema("decisive_fortune", "unknown_place_code", extra=True)
        self.rm("application/decisive_fortune/composition_root/wiring_material.py")
        self.controller("accounts", legacy=True)
        self.controller("decisive_fortune")
        anchor: str = self.commit("anchor")
        self.checkout(anchor, "lane")
        self.schema("service_policy", "policy_unknown")
        self.commit("lane schema")
        self.controller("service_policy")
        self.commit("lane entrance")
        self.checkout("main")
        self.rename_bc("decisive_fortune", "fortune_saju")
        self.commit("upstream rename")
        self.write("web/application/chart/presentation_layer/chart.py", "class Chart:\n    pass\n")
        self.write(".dddjango-web/adopted.txt", "adopted\n")
        self.commit("sister web")
        self.checkout("lane")
        merge: str = self.merge()
        self.write("application/service_policy/application_layer/place/__init__.py", "# lane follow-up\n")
        self.commit("follow-up")
        return anchor, merge


class ApprovedInflowPartitionRegression(unittest.TestCase):
    """설계 v3 §7-2: 실제 렌더·사유·exit, K 한계는 성공 보장이 아니다."""

    def setUp(self) -> None:
        self.temp: tempfile.TemporaryDirectory[str] = tempfile.TemporaryDirectory(prefix="approved-scope-")
        self.addCleanup(self.temp.cleanup)
        self.td: Path = Path(self.temp.name)

    def repo(self, name: str) -> ApprovedInflowRepo:
        return ApprovedInflowRepo(self.td, name)

    def run_scope(self, r: ApprovedInflowRepo, anchor: str, merges: tuple[str, ...],
                  script: Path = CTX, argv: list[str] | None = None) -> tuple[int, str]:
        return _run(script, r.root, [*(argv if argv is not None else ["--scope-bc", "accounts"]),
                     "--anchor", anchor, "--approved-merge-file", str(r.approved(*merges))])

    def verdict(self, result: tuple[int, str], code: int, reason: str) -> str:
        actual: int
        out: str
        actual, out = result
        self.assertEqual(actual, code, out)
        self.assertIn(reason, out)
        return out

    def test_Q1_ledger_inflow_and_anchor_existing(self) -> None:
        """장부 꼴 — 2.22.3 부터 앵커 사본을 옛 BC 이름으로 렌더해 accounts 줄이 앵커 기존분(2.22.2 까지는 `측정 무효(M^1)` · exit 2)."""
        anchor: str
        merge: str
        r: ApprovedInflowRepo = self.repo("ledger")
        anchor, merge = r.ledger()
        argv: list[str] = r.selectors(("accounts", "fortune_saju", "service_policy"), inventory=True)
        out: str = self.verdict(self.run_scope(r, anchor, (merge,), CENT, argv), 0, "앵커 기존분(잔존) 1건")
        self.assertNotIn("측정 무효(M^1)", out)
        self.assertNotIn("  기준선 오류:", out)
        self.assertIn("영역 이름 대응(승인 머지가 가져온 BC 이름 바꾸기 — 앵커 사본은 그 이름으로 렌더): fortune_saju→decisive_fortune", out)
        self.assertIn("승인 유입 2건", out)
        self.assertIn("^1 에 주어 파일 없음", out)

    def test_Q1prime_ledger_exact_debt(self) -> None:
        r: ApprovedInflowRepo = self.repo("ledger-debt")
        anchor: str
        merge: str
        anchor, merge = r.ledger()
        argv: list[str] = r.selectors(("accounts", "fortune_saju", "service_policy"), inventory=True)
        code: int
        out: str
        code, out = _run(CENT, r.root, argv + ["--anchor", anchor])
        self.assertEqual(code, 2, out)
        line: str = next(l.strip() for l in out.splitlines() if l.strip().startswith("- application/accounts/") and "duplicate project" in l)
        debt: Path = self.td / "exact-debt.txt"
        debt.write_text("= check-error-centralization.py :: " + line + "\n", encoding="utf-8")
        self.verdict(self.run_scope(r, anchor, (merge,), CENT, argv + ["--legacy-debt-file", str(debt)]),
                     0, "앵커 기존분(잔존) 1건 · 이관 빚 0건 · 승인 유입 2건")  # 2.22.2 까지는 «이관 빚 1건»

    def test_Q2_ladder_reg15_reg05_with_and_without_flag(self) -> None:
        anchor: str
        merge: str
        r: ApprovedInflowRepo = self.repo("ladder")
        anchor, merge = r.ledger()
        argv: list[str] = r.selectors(("accounts", "fortune_saju", "service_policy"))
        for script, count in ((CONTRACT, 4), (OPENAPI, 1)):
            for flag in (False, True):
                with self.subTest(script=script.name, flag=flag):
                    extra: list[str] = ["--approved-merge-file", str(r.approved(merge))] if flag else []
                    out: str = self.verdict(_run(script, r.root, argv + ["--anchor", anchor] + extra), 0,
                        "selector 렌더 재실행(빈 골격 --error-bc 걷음: service_policy · 그 영역 아래 줄 제외)")
                    self.assertIn(f"앵커 기존분(잔존) {count}건", out)

    def test_Q4_Q5_Q7_Q13_cause_break_and_later_upstream_fix(self) -> None:
        anchor: str
        merge: str
        for mode in ("merge-gap", "chain-gap", "later-fix", "before"):
            with self.subTest(mode=mode):
                r: ApprovedInflowRepo = self.repo(mode)
                anchor, merge = r.cause_merge(drop_in_merge=mode == "merge-gap")
                merges: tuple[str, ...] = (merge,)
                if mode == "merge-gap":
                    r.bc("billing"); r.commit("lane own cause")
                    reason: str = f"유입 증명 실패(승인 머지 {merge[:12]} 결과에 없음)"
                elif mode == "chain-gap":
                    r.rm("application/billing"); gap: str = r.commit("remove cause")
                    r.bc("zulu"); r.commit("new lane cause")
                    reason = f"유입 증명 실패(승인 머지 {merge[:12]} 뒤 사슬 {gap[:12]} 에 없음)"
                elif mode == "later-fix":
                    r.checkout("main"); r.rm("application/billing"); r.commit("upstream fixes cause")
                    r.checkout("lane"); m2: str = r.merge(); merges += (m2,)
                    r.bc("zulu"); r.commit("lane creates cause")
                    reason = f"유입 증명 실패(뒤 승인 머지 {m2[:12]} 의 ^2 에 없음)"
                else:
                    # Q13 k0-before: 두 부모에 같은 줄이 이미 있다.
                    r.checkout(merge + "^1", "both")
                    r.bc("zulu"); r.commit("lane cause before merge")
                    merge = r.merge(); merges = (merge,)
                    reason = "상호작용 미증명"
                self.verdict(self.run_scope(r, anchor, merges), 2, reason)

    def test_Q8_reg02_later_upstream_fix_blocks_old_merge_shortcut(self) -> None:
        # Claude B2: M0 이 들인 중복 코드를 상류가 M1 에서 고쳤는데 레인이 같은 중복 줄을 다시 만든다.
        # 주어(aaa)의 전달 머지는 M1 이라 L 이 서지 않고, 옛 M0 의 지름길(^1 에 주어 파일 없음)은 ⓑ 가 막는다.
        r: ApprovedInflowRepo = self.repo("b2")
        r.project("accounts"); r.controller("accounts"); r.schema("accounts", "acc")
        anchor: str = r.commit("A")
        r.checkout(anchor, "lane"); r.write("lane.txt", "l"); r.commit("L1")
        r.checkout("main")
        for bc in ("aaa", "bbb"):
            r.bc(bc); r.controller(bc); r.schema(bc, "dup_x")
        r.commit("U0 adds aaa and bbb with dup_x")
        r.checkout("lane"); m0: str = r.merge()
        aaa: str = r.error.format(bc="aaa")
        r.checkout("main"); r.schema("bbb", "bbb_own"); r.write(aaa, (r.root / aaa).read_text() + "# touched upstream\n")
        r.commit("U1 fixes duplicate and touches aaa")
        r.checkout("lane"); m1: str = r.merge()
        r.bc("zzz"); r.controller("zzz"); r.schema("zzz", "dup_x"); r.commit("L2 lane re-creates dup_x")
        argv: list[str] = r.selectors(("zzz",))
        for rel in ("framework/ninja/framework_error_schema.py", *(r.error.format(bc=bc) for bc in ("accounts", "aaa", "bbb", "zzz"))):
            argv += ["--project-code-error-module", rel]
        line: str = aaa + ":1: duplicate project code wire value: dup_x: from enum import StrEnum"
        for merges, reason in (((m0, m1), f"유입 증명 실패(뒤 승인 머지 {m1[:12]} 의 ^2 에 없음)"),
                               ((m1,), "유입 증명 실패(이중 원인)")):
            with self.subTest(approved=len(merges)):
                out: str = self.verdict(self.run_scope(r, anchor, merges, CENT, argv), 2, reason)
                self.assertIn(f"  - {line}\n    ↳ 귀속 유지: {reason}\n", out)
                self.assertIn("승인 유입 0건", out)

    def test_Q9_literal_delete_restore_and_modify_delete_resolution(self) -> None:
        anchor: str
        merge: str
        for mode in ("restore", "working", "modify-delete"):
            with self.subTest(mode=mode):
                r: ApprovedInflowRepo = self.repo(mode)
                if mode != "modify-delete":
                    anchor, merge = r.cause_merge(before=True)
                    r.bc("billing")
                    if mode == "restore":
                        r.commit("lane restore")
                    reason: str = "유입 증명 실패(이중 원인)"
                else:
                    r.project("accounts", "orders", "billing")
                    anchor = r.commit("A")
                    r.checkout(anchor, "lane"); r.write("application/billing/domain_layer/__init__.py", "# lane keeps BC\n"); r.commit("lane modify")
                    r.checkout("main"); r.rm("application/billing"); r.write(r.port); r.commit("upstream delete")
                    r.checkout("lane")
                    proc: subprocess.CompletedProcess[str] = _git(r.root, "merge", "--no-ff", "--no-commit", "main")
                    self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
                    r.bc("billing"); merge = r.commit("resolve by keeping BC")
                    reason = "유입 증명 실패(이중 원인)"
                self.verdict(self.run_scope(r, anchor, (merge,)), 2, reason)

    def test_Q12_empty_approval(self) -> None:
        anchor: str
        merge: str
        r: ApprovedInflowRepo = self.repo("inflow")
        anchor, merge = r.cause_merge()
        self.verdict(self.run_scope(r, anchor, ()), 2, "상호작용 미증명")

    def test_Q30_clean_inflow(self) -> None:
        r: ApprovedInflowRepo = self.repo("clean-inflow")
        anchor: str
        merge: str
        anchor, merge = r.cause_merge()
        self.verdict(self.run_scope(r, anchor, (merge,)), 0, "(L 증명) · 상호작용")

    def test_Q22_Q31_Q32_Q33_chain_conditions(self) -> None:
        anchor: str
        merge: str
        for mode in ("remerge-no", "remerge-yes", "unrelated", "other-up", "over", "empty", "invalid", "octopus"):
            with self.subTest(mode=mode):
                r: ApprovedInflowRepo = self.repo(mode)
                anchor, merge = r.cause_merge()
                merges: tuple[str, ...] = (merge,)
                code: int = 2
                reason: str = ""
                if mode.startswith("remerge"):
                    r.git("revert", "-m", "1", "--no-edit", merge)
                    r.checkout("main"); r.write("application/billing/domain_layer/up.txt", "u\n"); r.commit("upstream again")
                    r.checkout("lane"); m2: str = r.merge()
                    if mode == "remerge-yes":
                        merges += (m2,); code = 0; reason = f"유입: {m2[:12]}(L 증명)"
                    else:
                        reason = f"유입 증명 실패(승인 머지 {merge[:12]} 뒤 미승인 머지 {m2[:12]})"
                elif mode in ("unrelated", "other-up"):
                    r.checkout("main" if mode == "unrelated" else anchor, None if mode == "unrelated" else "hotfix")
                    r.write("framework/pure/up.py", "X: int = 1\n"); r.commit("unrelated upstream")
                    r.checkout("lane"); m2 = r.merge("main" if mode == "unrelated" else "hotfix"); merges += (m2,)
                    code = 0 if mode == "unrelated" else 2
                    reason = "(L 증명) · 상호작용" if code == 0 else f"유입 증명 실패(뒤 승인 머지 {m2[:12]} 의 ^2 에 없음)"
                elif mode in ("over", "empty"):
                    for index in range(64 if mode == "over" else 80):
                        if mode == "empty":
                            r.git("commit", "-q", "--allow-empty", "-m", str(index))
                        else:
                            r.write("lane.txt", str(index)); r.commit(str(index))
                    code = 2 if mode == "over" else 0
                    reason = f"측정 생략(사슬 커밋 65 > 한도 64) — {merge[:12]}" if code == 2 else "(L 증명) · 상호작용"
                elif mode == "invalid":
                    r.write("pyproject.toml", '[project]\nrequires-python = ">=3.99"\n'); gap: str = r.commit("cannot measure")
                    r.rm("pyproject.toml"); r.commit("fixed")
                    reason = f"측정 무효(사슬 {gap[:12]}) — {merge[:12]}"
                else:
                    for branch in ("s1", "s2"):
                        r.checkout(merge, branch); r.write(f"{branch}.txt", branch); r.commit(branch); r.checkout("lane")
                    r.git("merge", "-q", "--no-ff", "-m", "octopus", "s1", "s2")
                    reason = f"유입 증명 실패(승인 머지 {merge[:12]} 뒤 미승인 머지 {r.git('rev-parse', 'HEAD')[:12]})"
                self.verdict(self.run_scope(r, anchor, merges), code, reason)

    def test_K1_한계_interaction_swap_worktree_add_then_remove_and_merge_swap(self) -> None:
        # 설계 §10-2 + 최종 리뷰 사소 1: 같은 글자가 끊기지 않는 원인 교체의 한계.
        anchor: str
        merge: str
        for mode in ("KM1", "KMw", "add_rem", "evil-merge", "d7"):
            with self.subTest(mode=mode):
                r: ApprovedInflowRepo = self.repo(mode)
                anchor, merge = r.cause_merge()
                if mode == "evil-merge":
                    r.checkout(merge + "^1"); r.merge(pending=True)
                r.bc("zulu")
                if mode == "add_rem":
                    r.commit("add own cause first")
                if mode != "d7":
                    r.rm("application/billing")
                if mode != "KMw":
                    head: str = r.commit("swap cause")
                    if mode == "evil-merge":
                        merge = head
                self.verdict(self.run_scope(r, anchor, (merge,)), 0, "(L 증명) · 상호작용")

    def test_Q6_Q21_and_K1_한계_file_partner_swap(self) -> None:
        # 설계 §10-2: 지움→더함은 차단, 더함→지움과 병합 안 교체는 같은 글자 한계.
        for mode in ("KFM1", "KFM2", "add_rem", "evil-merge", "d17"):
            with self.subTest(mode=mode):
                r: ApprovedInflowRepo = self.repo(mode)
                r.project("accounts", "orders"); r.controller("accounts"); r.controller("orders")
                r.schema("accounts", "acc"); r.schema("orders", "ord")
                anchor: str = r.commit("A")
                r.checkout(anchor, "lane"); r.write("lane.txt", "lane")
                if mode == "d17":
                    r.schema("orders", "dup")
                r.commit("L0"); r.checkout("main")
                for bc in ("aaa", "bbb"):
                    r.bc(bc); r.controller(bc); r.schema(bc, "dup")
                r.commit("U"); r.checkout("lane"); merge: str = r.merge(pending=mode == "evil-merge")
                gap: str = ""
                if mode != "d17":
                    if mode in ("KFM1", "add_rem", "evil-merge"):
                        r.bc("zzz"); r.controller("zzz"); r.schema("zzz", "dup")
                        if mode == "add_rem":
                            r.commit("add own partner first")
                    r.schema("bbb", "bbb_own")
                    if mode == "KFM2":
                        gap = r.commit("remove upstream partner")
                        r.bc("zzz"); r.controller("zzz"); r.schema("zzz", "dup")
                    head: str = r.commit("swap partner")
                    if mode == "evil-merge":
                        merge = head
                bcs: tuple[str, ...] = ("accounts", "orders", "aaa", "bbb", "zzz") if mode != "d17" else ("accounts", "orders", "aaa", "bbb")
                reason: str = f"뒤 사슬 {gap[:12]} 에 없음)" if mode == "KFM2" else "(L 증명 · ^1 에 주어 파일 없음) · 파일 verbatim"
                self.verdict(self.run_scope(r, anchor, (merge,), CENT, r.selectors(bcs, inventory=True)), 2 if mode == "KFM2" else 0, reason)

    def test_Q40_Q41_released_help_ap_and_noflag(self) -> None:
        old: Path = self.td / "released"
        old.mkdir()
        archive: subprocess.CompletedProcess[bytes] = subprocess.run(["git", "-C", str(ROOT), "archive", _RELEASED_2212_COMMIT, "dddjango/scripts"], capture_output=True, check=True)
        subprocess.run(["tar", "-x", "-C", str(old)], input=archive.stdout, check=True)
        r: ApprovedInflowRepo = self.repo("contract")
        r.project("accounts"); r.controller("accounts"); r.schema("accounts", "acc")
        anchor: str = r.commit("A"); r.write("lane.txt", "dirty")
        for script in (CENT, OPENAPI, CTX, CONTRACT, COMP):
            for argv in (["--help"], ["--ap", "config/api.py"], ["--anchor", anchor]):
                with self.subTest(script=script.name, argv=argv):
                    self.assertEqual(_run(script, r.root, argv), _run(old / "dddjango/scripts" / script.name, r.root, argv))

    def test_Q3_helper_in_dropped_bc_is_not_baseline(self) -> None:
        r: ApprovedInflowRepo = self.repo("helper")
        for rel, source in _T_FILES.items():
            r.write(rel, source)
        ctrl: str = "application/report/driving_layer/controller.py"
        src: str = ('from ninja import Router\nfrom application.lesson.driving_layer.api.bc_error_schema import LessonNotFoundError\n'
                    'router = Router()\n@router.get("/")\ndef get_report(request):\n    return LessonNotFoundError()\n')
        r.write(ApprovedInflowRepo.error.format(bc="report"))
        r.write(ctrl, src)
        api: str = "application/report/driving_layer/api.py"
        r.write(api, "from ninja_extra import NinjaExtraAPI\nfrom .controller import router\napi = NinjaExtraAPI()\n")
        anchor: str = r.commit("A")
        r.write(ApprovedInflowRepo.error.format(bc="report"), _LESSON_STATIC_SRC.replace("Lesson", "Report").replace("lesson_not_found", "report_not_found"))
        r.write(ctrl, src.replace('@router.get("/")\n', "")); r.commit("lane helper")
        argv: list[str] = [*_T_ARGS[:_T_ARGS.index("--project-code-error-module")], "--scope-bc", "report", "--error-bc", "report", "--controller-module", ctrl]
        argv[argv.index("--api-module") + 1] = api
        self.verdict(self.run_scope(r, anchor, (), CONTRACT, argv), 2, "[#126]")

    def code_merge(self, name: str, *, before: str = "", upstream_move: bool = False, pending: bool = False):
        r: ApprovedInflowRepo = self.repo(name)
        r.project("accounts", "orders", *( ("policy",) if before == "partial" else ()))
        for bc in ("accounts", "orders", *( ("policy",) if before == "partial" else ())):
            r.controller(bc)
        r.schema("accounts", "wire_x"); r.schema("orders", "wire_b")
        anchor: str = r.commit("A")
        r.checkout(anchor, "lane"); r.write("lane.txt", "l")
        if before in ("duplicate", "partial"):
            r.schema("orders", "wire_x")
        if before == "partial":
            r.write(r.error.format(bc="policy"), "from framework.ninja.framework_error_schema import FrameworkErrorSchema\nclass PolicyErrorSchema(FrameworkErrorSchema):\n    error: str\n")
        if before == "comment":
            r.write(r.error.format(bc="accounts"), (r.root / r.error.format(bc="accounts")).read_text() + "# comment\n")
        r.commit("L0"); r.checkout("main")
        if upstream_move:
            r.schema("accounts", "moved")
        elif before == "comment":
            r.write(r.error.format(bc="accounts"), (r.root / r.error.format(bc="accounts")).read_text() + "# upstream comment\n")
        r.bc("zulu"); r.controller("zulu"); r.schema("zulu", "wire_x", extra=not upstream_move)
        r.commit("U"); r.checkout("lane")
        if pending:
            proc: subprocess.CompletedProcess[str] = _git(r.root, "merge", "--no-ff", "--no-commit", "main")
            self.assertIn(proc.returncode, (0, 1), proc.stdout + proc.stderr)
        else:
            r.merge()
        return r, anchor, r.git("rev-parse", "HEAD")

    def test_Q10_Q11_Q14_Q13_reverts_edits_conflicts_and_double_cause(self) -> None:
        r: ApprovedInflowRepo
        anchor: str
        merge: str
        for mode in ("a1-revert", "a2-ours", "a2-resolve", "d3", "d4", "d6", "d11"):
            with self.subTest(mode=mode):
                r, anchor, merge = self.code_merge(mode, before="comment" if mode in ("a2-resolve", "d11") else ("duplicate" if mode == "d6" else ""),
                    upstream_move=mode.startswith("a"), pending=mode in ("a2-ours", "a2-resolve", "d11"))
                if mode.startswith("a"):
                    r.schema("accounts", "wire_x")
                    if mode != "a1-revert":
                        merge = r.commit("merge resolves to anchor")
                    else:
                        r.commit("lane reverts")
                    reason: str = "상호작용 미증명"
                elif mode in ("d3", "d4", "d11"):
                    p: str = r.error.format(bc="zulu" if mode != "d11" else "accounts")
                    if mode == "d11":
                        r.schema("accounts", "wire_x")
                    r.write(p, (r.root / p).read_text() + '\nclass SecondError(' + ("Zulu" if mode != "d11" else "Accounts") + 'ErrorSchema):\n    error: str = "wire_x"\n    message: str = "new"\n')
                    if mode != "d4":
                        head: str = r.commit("lane adds second violation")
                        if mode == "d11":
                            merge = head
                    reason = "worktree 수정 중" if mode == "d4" else ("충돌 해소분(M≠M^2)" if mode == "d11" else "레인 커밋 수정")
                else:
                    reason = "측정 무효(M^1)"
                self.verdict(self.run_scope(r, anchor, (merge,), CENT, r.selectors(("accounts", "orders", "zulu"), inventory=True)), 2, reason)

    def test_Q15_partial_M1_and_Q16_partial_merge_result(self) -> None:
        r: ApprovedInflowRepo
        anchor: str
        merge: str
        for mode in ("d16", "c8", "c8-gap"):
            with self.subTest(mode=mode):
                r, anchor, merge = self.code_merge(mode, before="partial")
                r.schema("policy", "policy_unknown"); r.commit("finish policy")
                reason: str = "측정 무효(M^1)"
                if mode == "c8":
                    # 새 주어 zulu는 M^1 부재 지름길을 거친다. 병합 결과에 레인의 트리 진단(policy #572)이 있어도 #2 기준선이
                    # 코드 줄까지 모으므로 사슬 이어짐이 보인다 — zulu 두 줄만 유입이고 accounts 줄은 부분 M^1 로 남는다.
                    reason = f"↳ 유입: {merge[:12]}(L 증명 · ^1 에 주어 파일 없음) · 파일 verbatim"
                if mode == "c8-gap":
                    # 부분 렌더(exit 2)에 줄이 없으면 «없다» 가 아니라 측정 무효다 — 레인이 상류 줄을 지웠다가 다음 커밋에서 되살린다.
                    p: str = r.error.format(bc="zulu")
                    source: str = (r.root / p).read_text()
                    r.write(p, source.replace('    missing: str = ""\n', "")); gap: str = r.commit("lane drops upstream line")
                    r.write(p, source); r.commit("lane restores upstream line")
                    reason = f"측정 무효(사슬 {gap[:12]}) — {merge[:12]}"
                out: str = self.verdict(self.run_scope(r, anchor, (merge,), CENT, r.selectors(("accounts", "orders", "policy", "zulu"), inventory=True)), 2, reason)
                if mode != "d16":
                    self.assertEqual(out.count("↳ 귀속 유지: 측정 무효(M^1)"), 1, out)
                    self.assertIn("승인 유입 2건" if mode == "c8" else "승인 유입 0건", out)
                    self.assertEqual(out.count("↳ 유입: "), 2 if mode == "c8" else 0, out)
                    self.assertEqual(out.count("측정 무효(사슬 "), 0 if mode == "c8" else 2, out)

    def test_M2_upstream_event_with_tree_and_code_text_is_inflow(self) -> None:
        # 상류가 들인 사건 하나가 트리 줄(#636 StrEnum 아님)이자 코드 줄이다 — ^2 기준선이 트리에서 끝나지 않고
        # 코드 줄까지 모아야 «^2 에 있다» 가 선다. 앵커 · 레인 쪽에는 트리 진단이 없다.
        r: ApprovedInflowRepo = self.repo("m2-tree")
        r.project("accounts", "orders")
        for bc in ("accounts", "orders"):
            r.controller(bc)
        r.schema("accounts", "wire_x"); r.schema("orders", "wire_b")
        anchor: str = r.commit("A")
        r.checkout(anchor, "lane"); r.write("lane.txt", "l"); r.commit("L0")
        r.checkout("main"); r.bc("zulu"); r.controller("zulu"); r.schema("zulu", "wire_z")
        p: str = r.error.format(bc="zulu")
        r.write(p, (r.root / p).read_text().replace("class ZuluErrorCode(StrEnum)", "class ZuluErrorCode(str)"))
        r.commit("U"); r.checkout("lane"); merge: str = r.merge()
        r.write("lane.txt", "after"); r.commit("lane after merge")
        out: str = self.verdict(self.run_scope(r, anchor, (merge,), CENT, r.selectors(("accounts", "orders", "zulu"), inventory=True)),
                                0, f"↳ 유입: {merge[:12]}(L 증명 · ^1 에 주어 파일 없음) · 파일 verbatim")
        self.assertIn("신규분(앵커 이후) 0건 · 앵커 기존분(잔존) 0건 · 이관 빚 0건 · 승인 유입 1건", out)
        self.assertIn("ZuluErrorCode must directly inherit enum.StrEnum: class ZuluErrorCode(str):", out)
        self.assertNotIn("측정 무효(", out)

    def test_Q9_reg02_hybrid_commit_and_worktree(self) -> None:
        for mode in ("commit", "working"):
            with self.subTest(mode=mode):
                r: ApprovedInflowRepo = self.repo(mode)
                r.project("accounts", "zulu")
                for bc in ("accounts", "zulu"):
                    r.controller(bc)
                r.schema("accounts", "wire_x"); r.schema("zulu", "wire_z")
                anchor: str = r.commit("A")
                r.checkout(anchor, "lane"); r.schema("accounts", "wire_y"); r.commit("lane takes Y")
                r.checkout("main"); r.schema("accounts", "wire_y"); r.schema("zulu", "wire_x"); r.commit("upstream moves X")
                r.checkout("lane"); merge: str = r.merge()
                r.schema("accounts", "wire_x")
                if mode == "commit":
                    r.commit("lane returns X")
                self.verdict(self.run_scope(r, anchor, (merge,), CENT, r.selectors(("accounts", "zulu"), inventory=True)),
                             2, "상호작용 미증명" if mode == "commit" else "worktree 수정 중")

    def test_Q18_Q9_folder_cycle(self) -> None:
        r: ApprovedInflowRepo = self.repo("cycle")
        r.project("accounts", "orders")
        acl: str = "application/{bc}/driven_layer/adapter/anticorruption_layer"
        r.write(acl.format(bc="accounts") + "/orders/__init__.py")
        anchor: str = r.commit("A")
        r.checkout(anchor, "lane"); r.write("lane.txt", "l"); r.commit("L")
        r.checkout("main"); r.write(acl.format(bc="orders") + "/accounts/__init__.py"); r.commit("U")
        r.checkout("lane"); r.merge(pending=True); r.rm(acl.format(bc="orders") + "/accounts"); merge: str = r.commit("merge drops reverse ACL")
        (r.root / (acl.format(bc="orders") + "/accounts")).mkdir()
        self.verdict(self.run_scope(r, anchor, (merge,), CTX, ["--scope-bc", "accounts", "--scope-bc", "orders"]), 2, "비-blob 경로")

    def test_Q17_reg16_M2(self) -> None:
        r: ApprovedInflowRepo = self.repo("reg16")
        anchor: str
        merge: str
        anchor, merge = r.ledger()
        r.write("config/urls.py", 'from django.urls import path\nfrom config.api import api\n'
            'from application.service_policy.driving_layer.api.api_router import register_service_policy_api\n'
            'register_service_policy_api(api)\nurlpatterns = [path("api/", api.urls)]\n')
        r.commit("lane wires registrar")
        argv: list[str] = ["--error-profile", "dddjango-code-json", "--scope", "f89", "--api-module", "config/api.py", "--urlconf-module", "config/urls.py",
                          "--registrar-module", "application/service_policy/driving_layer/api/api_router.py"]
        self.verdict(self.run_scope(r, anchor, (merge,), COMP, argv), 2, "측정 무효(M^2)")

    def test_Q19_removed_preserve_inventory_not_supplemented(self) -> None:
        for mode in ("dup", "import"):
            with self.subTest(mode=mode):
                r: ApprovedInflowRepo = self.repo(mode)
                r.project("accounts", "orders", "zulu")
                for bc in ("accounts", "zulu"):
                    r.controller(bc); r.schema(bc, "wire_x")
                extra: str = "application/accounts/driving_layer/api/place/extra.py"
                if mode == "import":
                    r.write(extra, 'from application.zulu.driving_layer.api.bc_error_schema import ZuluErrorSchema as E\nclass Extra(E):\n    pass\ndef raw():\n    return E(error="wire_x")\n')
                anchor: str = r.commit("A")
                r.checkout(anchor, "lane"); r.write("lane.txt", "l"); r.commit("L")
                r.checkout("main"); r.rm("application/zulu"); r.commit("U delete")
                r.checkout("lane"); merge: str = r.merge()
                r.schema("orders", "wire_x"); r.controller("orders")
                if mode == "import":
                    r.write(extra, (r.root / extra).read_text().replace("application.zulu.", "application.orders.").replace("ZuluErrorSchema", "OrdersErrorSchema"))
                r.commit("lane fills orders")
                self.verdict(self.run_scope(r, anchor, (merge,), CENT, r.selectors(("accounts", "orders"), inventory=True)), 2, "기준선 오류:")

    def test_Q20_escape(self) -> None:
        r: ApprovedInflowRepo
        anchor: str
        merge: str
        r, anchor, merge = self.code_merge("escape")
        r.checkout(merge + "^2", "escape-up")
        r.write("payload.txt", (r.root / r.error.format(bc="zulu")).read_text())
        r.rm(r.error.format(bc="zulu")); (r.root / r.error.format(bc="zulu")).symlink_to(r.root / "payload.txt")
        r.commit("upstream escape")
        r.checkout(merge + "^1", "escape-lane"); merge = r.merge("escape-up")
        self.verdict(self.run_scope(r, anchor, (merge,), CENT, r.selectors(("accounts", "orders", "zulu"), inventory=True)), 2, "측정 무효(M^2)")

    def test_Q34_subject_name_inflow(self) -> None:
        # row17-18-after: 상류가 포트 내용을 고치며 공급자 BC 를 들이고, 레인은 병합 뒤 포트 «내용» 만 앵커 값으로 되돌린다.
        # 줄(#364 포트 이름)의 원인은 포트 이름 + 상류 BC 라 끊기지 않는다 — Q30 과 달리 주어 파일을 병합이 바꿨다가 레인이 되돌렸다.
        r: ApprovedInflowRepo = self.repo("names")
        original: str = "class BillingZuluPort:\n    pass\n"
        r.project("accounts", "orders"); r.write(r.port, original)
        anchor: str = r.commit("A")
        r.checkout(anchor, "lane"); r.write("lane.txt", "lane\n"); r.commit("L0")
        r.checkout("main"); r.write(r.port, "# upstream\n"); r.bc("billing"); r.commit("U edits subject and adds cause")
        r.checkout("lane"); merge: str = r.merge()
        r.write(r.port, original); r.commit("lane reverts subject content")
        blob: dict[str, str] = {ref: r.git("rev-parse", f"{ref}:{r.port}") for ref in (anchor, merge + "^1", merge, "HEAD")}
        self.assertNotEqual(blob[merge], blob[merge + "^1"])  # 병합이 주어 파일을 바꿨다
        self.assertEqual(blob["HEAD"], blob[anchor])  # 레인이 내용만 앵커 값으로 되돌렸다
        self.verdict(self.run_scope(r, anchor, (merge,)), 0, f"유입: {merge[:12]}(L 증명) · 상호작용")


class BcRenamePairingRegression(unittest.TestCase):
    """짝 규칙의 안전 장치를 반환값으로 바로 단언한다(검사기를 돌리지 않는다) — `merge_bc_renames` · `snapshot_bc_aliases`.

    후보와 «서로 가장 닮은 하나» 는 상류 사실(병합 기준 B · 상류 쪽 M^2)만으로 정하고, 레인 쪽(M^1 · M)은 선 짝을 버리는
    데만 쓴다. 문턱 0.5 · 겹친 경로 바닥 3 · 동률 · 병합 기준 여럿 · 되짚기 가드를 하나씩 고정한다."""

    def setUp(self) -> None:
        sys.path.insert(0, str(S))
        import anchor_diff
        self.ad = anchor_diff
        self.ad._RENAME_CACHE.clear()
        self.temp: tempfile.TemporaryDirectory[str] = tempfile.TemporaryDirectory(prefix="bc-pair-")
        self.addCleanup(self.temp.cleanup)
        self.td: Path = Path(self.temp.name)

    def bc(self, root: Path, name: str, *areas: str, extra: tuple[str, ...] = ()) -> None:
        base: str = f"application/{name}"
        for rel in ("__init__.py", "driving_layer/__init__.py", "driving_layer/api/__init__.py", "driving_layer/api/api_router.py",
                    "driving_layer/api/bc_error_schema.py", f"driven_layer/django_{name}/apps.py", *extra):
            _write(root, f"{base}/{rel}", "")
        for area in areas:
            api: str = f"{base}/driving_layer/api/{area}"
            for rel in (f"{base}/application_layer/{area}/__init__.py", api + "/__init__.py", api + f"/{area}_controller.py",
                        api + "/schema/__init__.py", api + "/schema/schema_in.py", api + "/schema/schema_out.py"):
                _write(root, rel, "")

    def scene(self, name: str, base: "dict[str, tuple[str, ...]]", upstream, *, lane_pre=None, in_merge=None, lane_post=None,
              directory_renames: str = "false") -> tuple[Path, str, str]:
        """앵커(main) → 레인 커밋 → 상류 커밋 → 레인이 main 을 병합 → 레인 후속. (root, anchor, merge) 를 돌려준다."""
        root: Path = self.td / name
        root.mkdir()
        self.assertEqual(_git(root, "init", "-q", "-b", "main").returncode, 0)
        _write(root, "application/__init__.py", "")
        for bc, areas in base.items():
            self.bc(root, bc, *areas)
        anchor: str = _commit_all(root, "anchor")
        _git(root, "checkout", "-q", "-b", "lane")
        _write(root, "lane.txt", "lane\n")
        if lane_pre is not None:
            lane_pre(root)
        _commit_all(root, "lane")
        _git(root, "checkout", "-q", "main")
        upstream(root)
        _commit_all(root, "upstream")
        _git(root, "checkout", "-q", "lane")
        merged = _git(root, "-c", f"merge.directoryRenames={directory_renames}", "merge", "-q", "--no-ff",
                      *(["--no-commit"] if in_merge is not None else ["-m", "approved merge"]), "main")
        if in_merge is not None:
            in_merge(root)
            _commit_all(root, "approved merge (lane-made result)")
        else:
            self.assertEqual(merged.returncode, 0, merged.stdout + merged.stderr)
        merge: str = _git(root, "rev-parse", "HEAD").stdout.strip()
        self.assertEqual(len(_git(root, "show", "-s", "--format=%P", merge).stdout.split()), 2)
        _write(root, "lane2.txt", "lane\n")
        if lane_post is not None:
            lane_post(root)
        _commit_all(root, "lane follow-up")
        return root, anchor, merge

    @staticmethod
    def rename(root: Path, old: str, new: str, *, inner: bool = True) -> None:
        dest: Path = root / "application" / new
        (root / "application" / old).rename(dest)
        if inner:
            for path in sorted(dest.rglob(f"*{old}*"), key=lambda p: -len(p.parts)):
                path.rename(path.with_name(path.name.replace(old, new)))

    def merges(self, root: Path, anchor: str, *shas: str) -> list:
        listing: Path = self.td / (root.name + "-approved.txt")
        listing.write_text("".join(sha + " approved\n" for sha in shas), encoding="utf-8")
        head: str = _git(root, "rev-parse", "HEAD").stdout.strip()
        return self.ad.load_approved_merges(listing, root, anchor, head)[0]

    def pairs(self, root: Path, anchor: str, merge: str) -> tuple:
        self.ad._RENAME_CACHE.clear()
        return self.ad.merge_bc_renames(root, self.merges(root, anchor, merge)[0])

    def aliases(self, root: Path, anchor: str, *shas: str) -> dict:
        self.ad._RENAME_CACHE.clear()
        head: str = _git(root, "rev-parse", "HEAD").stdout.strip()
        return self.ad.snapshot_bc_aliases(root, anchor, head, self.merges(root, anchor, *shas))

    def test_P1_plain_rename_pairs_and_inner_old_name_is_the_same_shape(self) -> None:
        inner: tuple[str, ...] = ("driven_layer/django_alpha/migrations/0001_initial.py", "driven_layer/django_alpha/migrations/0002_more.py",
                                  "driven_layer/django_alpha/models/thing.py", "driven_layer/django_alpha/models/other.py")
        for keep_inner in (False, True):
            with self.subTest(keep_inner=keep_inner):
                root, anchor, merge = self.scene(f"plain-{keep_inner}", {"alpha": ("place",), "keep": ("place",)},
                                                 lambda r, k=keep_inner: self.rename(r, "alpha", "beta", inner=not k))
                self.assertEqual(self.pairs(root, anchor, merge), (("alpha", "beta"),))
                self.assertEqual(self.aliases(root, anchor, merge), {"beta": "alpha"})
        # 안쪽 `django_<옛 이름>/` 아래에 고정 칸 밖 파일이 많은 개명 — 새 쪽 모양에서 옛 이름도 토큰이어야 닮음이 선다
        root = self.td / "inner-kept"
        root.mkdir()
        _git(root, "init", "-q", "-b", "main")
        self.bc(root, "alpha", "place", extra=inner)
        anchor = _commit_all(root, "anchor")
        _git(root, "checkout", "-q", "-b", "lane"); _write(root, "lane.txt", "l\n"); _commit_all(root, "lane")
        _git(root, "checkout", "-q", "main"); self.rename(root, "alpha", "beta", inner=False); _commit_all(root, "upstream")
        _git(root, "checkout", "-q", "lane"); _git(root, "merge", "-q", "--no-ff", "-m", "approved merge", "main")
        merge = _git(root, "rev-parse", "HEAD").stdout.strip()
        _write(root, "lane2.txt", "l\n"); _commit_all(root, "follow-up")
        self.assertTrue((root / "application/beta/driven_layer/django_alpha/models/thing.py").exists())
        self.assertEqual(self.pairs(root, anchor, merge), (("alpha", "beta"),))

    def test_P2_tie_two_renames_or_two_old_one_new_is_no_pair(self) -> None:
        def two(root: Path) -> None:
            self.rename(root, "alpha", "beta")
            self.rename(root, "gamma", "delta")
        root, anchor, merge = self.scene("tie-two", {"alpha": ("place",), "gamma": ("place",)}, two)
        self.assertEqual(self.pairs(root, anchor, merge), ())
        self.assertEqual(self.aliases(root, anchor, merge), {})

        def absorb(root: Path) -> None:      # 모양이 같은 옛 영역 둘이 사라지고 새 영역 하나 — 새 쪽에서 보면 동률
            self.rename(root, "alpha", "beta")
            shutil.rmtree(root / "application/gamma")
        root, anchor, merge = self.scene("tie-absorb", {"alpha": ("place",), "gamma": ("place",)}, absorb)
        self.assertEqual(self.pairs(root, anchor, merge), ())
        # 두 옛 후보가 한 새 후보를 서로 다른 점수(12/12 · 6/12)로 «가장 닮은 것» 으로 고른다 — 새 쪽에서 본 유일 최고만 짝이다
        root, anchor, merge = self.scene("two-pick-one", {"alpha": ("place", "detail"), "gamma": ("place",)}, absorb)
        self.assertEqual(self.pairs(root, anchor, merge), (("alpha", "beta"),))
        self.assertEqual(self.aliases(root, anchor, merge), {"beta": "alpha"})

    def test_P3_threshold_and_common_floor(self) -> None:
        def unrelated(areas: tuple[str, ...]):
            def run(root: Path) -> None:
                shutil.rmtree(root / "application/alpha")
                self.bc(root, "beta", *areas)
            return run
        root, anchor, merge = self.scene("below", {"alpha": ("place",)}, unrelated(("place", "issue", "redeem")))
        self.assertEqual(self.pairs(root, anchor, merge), ())                       # 닮음 6/18 — 0 초과 문턱 미만
        root, anchor, merge = self.scene("edge", {"alpha": ("place",)}, unrelated(("place", "detail")))
        self.assertEqual(self.pairs(root, anchor, merge), (("alpha", "beta"),))     # 닮음 6/12 — 정확히 문턱
        for count, want in ((2, ()), (3, (("alpha", "beta"),))):                    # 닮음 1.0 이어도 겹친 경로 바닥 3
            with self.subTest(common=count):
                files: tuple[str, ...] = tuple(f"domain_layer/thing/part{i}.py" for i in range(count))
                root = self.td / f"floor-{count}"
                root.mkdir()
                _git(root, "init", "-q", "-b", "main")
                self.bc(root, "alpha", extra=files)
                anchor = _commit_all(root, "anchor")
                _git(root, "checkout", "-q", "-b", "lane"); _write(root, "lane.txt", "l\n"); _commit_all(root, "lane")
                _git(root, "checkout", "-q", "main"); self.rename(root, "alpha", "beta"); _commit_all(root, "upstream")
                _git(root, "checkout", "-q", "lane"); _git(root, "merge", "-q", "--no-ff", "-m", "approved merge", "main")
                merge = _git(root, "rev-parse", "HEAD").stdout.strip()
                _write(root, "lane2.txt", "l\n"); _commit_all(root, "follow-up")
                self.assertEqual(self.pairs(root, anchor, merge), want)

    def test_P4_two_merge_bases_is_no_pair(self) -> None:
        root: Path = self.td / "crisscross"
        root.mkdir()
        _git(root, "init", "-q", "-b", "main")
        self.bc(root, "alpha", "place")
        anchor: str = _commit_all(root, "anchor")
        _git(root, "checkout", "-q", "-b", "lane"); _write(root, "lane.txt", "l\n"); lane1: str = _commit_all(root, "lane 1")
        _git(root, "checkout", "-q", "main"); _write(root, "docs/n.txt", "n\n"); _commit_all(root, "upstream note")
        _git(root, "checkout", "-q", "lane"); _git(root, "merge", "-q", "--no-ff", "-m", "lane takes main", "main")
        first: str = _git(root, "rev-parse", "HEAD").stdout.strip()
        _git(root, "checkout", "-q", "main"); _git(root, "merge", "-q", "--no-ff", "-m", "main takes lane 1", lane1)
        self.rename(root, "alpha", "beta"); _commit_all(root, "upstream rename")
        _git(root, "checkout", "-q", "lane"); _git(root, "merge", "-q", "--no-ff", "-m", "approved merge", "main")
        merge: str = _git(root, "rev-parse", "HEAD").stdout.strip()
        _write(root, "lane2.txt", "l\n"); _commit_all(root, "follow-up")
        self.assertEqual(len(_git(root, "merge-base", "--all", merge + "^1", merge + "^2").stdout.split()), 2)
        self.ad._RENAME_CACHE.clear()
        self.assertEqual(self.ad.merge_bc_renames(root, self.merges(root, anchor, first, merge)[1]), ())

    def test_P5_lane_side_can_only_discard_a_pair(self) -> None:
        """레인이 옛 폴더를 병합 결과에 남기거나 새 이름을 미리 만들어도 다른 후보로 돌아가지 않는다 — 짝이 사라질 뿐이다."""
        base: "dict[str, tuple[str, ...]]" = {"alpha": ("place", "detail"), "decoy": ("place",)}

        def upstream(root: Path) -> None:      # alpha → beta 개명 · 절반 겹치는 decoy 는 지움
            self.rename(root, "alpha", "beta")
            shutil.rmtree(root / "application/decoy")
        root, anchor, merge = self.scene("natural", base, upstream)
        self.assertEqual(self.pairs(root, anchor, merge), (("alpha", "beta"),))
        root, anchor, merge = self.scene("steered", base, upstream,
                                         lane_pre=lambda r: _write(r, "application/alpha/lane_keep.py", "# keep\n"),
                                         lane_post=lambda r: shutil.rmtree(r / "application/alpha"))
        self.assertTrue(_git(root, "cat-file", "-e", merge + ":application/alpha/lane_keep.py").returncode == 0)
        self.assertEqual(self.pairs(root, anchor, merge), ())          # 1판은 (decoy → beta) 로 돌아갔다
        self.assertEqual(self.aliases(root, anchor, merge), {})
        root, anchor, merge = self.scene("precreated", base, upstream,
                                         lane_pre=lambda r: _write(r, "application/beta/lane_pre.py", "# pre\n"))
        self.assertEqual(self.pairs(root, anchor, merge), ())
        same: "dict[str, tuple[str, ...]]" = {"alpha": ("place",), "gamma": ("place",)}

        def two(root: Path) -> None:
            self.rename(root, "alpha", "beta")
            self.rename(root, "gamma", "delta")

        def cross(root: Path) -> None:         # gamma 를 남기고 beta 를 미리 만들어 (alpha → delta) 엇짝을 노린다
            _write(root, "application/gamma/lane_keep.py", "# keep\n")
            _write(root, "application/beta/lane_pre.py", "# pre\n")
        root, anchor, merge = self.scene("crossed", same, two, lane_pre=cross)
        self.assertEqual(self.pairs(root, anchor, merge), ())          # 1판은 (alpha → delta)

        def prune_new(root: Path) -> None:     # (Codex «prune») 병합 결과에서 새 이름 하나(delta)를 지운다
            shutil.rmtree(root / "application/delta")
        root, anchor, merge = self.scene("pruned", same, two, lane_pre=lambda r: shutil.rmtree(r / "application/gamma"),
                                         in_merge=lambda r: (_git(r, "checkout", "main", "--", "application/beta", "application/delta"),
                                                             shutil.rmtree(r / "application/gamma", ignore_errors=True), prune_new(r)))
        self.assertEqual(self.pairs(root, anchor, merge), ())          # 1판은 남은 후보끼리 (alpha → beta)

        def take_upstream(root: Path) -> None: # (Codex «redirect») 레인이 진짜 옛 영역(alpha)을 병합 전에 지움 — 병합은 상류 결과를 받는다
            _git(root, "checkout", "main", "--", "application/beta")
            for name in ("alpha", "decoy"):
                shutil.rmtree(root / "application" / name, ignore_errors=True)
        root, anchor, merge = self.scene("redirected", base, upstream, lane_pre=lambda r: shutil.rmtree(r / "application/alpha"),
                                         in_merge=take_upstream)
        self.assertEqual(self.pairs(root, anchor, merge), ())          # 1판은 (decoy → beta) 로 돌아갔다

        def drop_new(root: Path) -> None:      # 병합 결과에서 상류의 새 영역(beta)을 뺀다 — 레인은 병합 뒤 beta 를 스스로 다시 만든다
            for name in ("alpha", "beta"):
                shutil.rmtree(root / "application" / name, ignore_errors=True)
        root, anchor, merge = self.scene("new-dropped-in-merge", base, upstream, in_merge=drop_new,
                                         lane_post=lambda r: self.bc(r, "beta", "place", "detail"))
        self.assertEqual(_git(root, "cat-file", "-e", merge + ":application/beta").returncode != 0, True)
        self.assertEqual(self.pairs(root, anchor, merge), ())          # 버리기 «새 이름이 병합 결과에 있다» 가 막는다
        self.assertEqual(self.aliases(root, anchor, merge), {})

        def add_only(root: Path) -> None:      # 상류는 같은 모양의 beta 를 더하기만 — alpha 는 그대로 둔다
            self.bc(root, "beta", "place", "detail")
        root, anchor, merge = self.scene("lane-deletes-in-merge", base, add_only,
                                         in_merge=lambda r: shutil.rmtree(r / "application/alpha"))
        self.assertFalse((root / "application/alpha").exists())
        self.assertEqual(self.pairs(root, anchor, merge), ())

        def grow(root: Path) -> None:          # 병합 커밋에서 레인이 새 영역에 파일을 잔뜩 더해도 모양은 상류 쪽에서 읽는다
            for i in range(20):
                _write(root, f"application/beta/domain_layer/lane_made/part{i}.py", "")
        root, anchor, merge = self.scene("lane-grows-new", base, upstream, in_merge=grow)
        self.assertEqual(self.pairs(root, anchor, merge), (("alpha", "beta"),))

    def test_P6_snapshot_alias_walk_guards(self) -> None:
        ad = self.ad

        def merge(sha: str, position: "int | None", only_head: bool = False):
            return ad.ApprovedMerge(sha, sha + "^1", sha + "^2", "approved", position, "", "main", only_head)

        def aliases(pairs: "dict[str, tuple]", merges: list, head: set, snap: set) -> dict:
            roots = {"HEAD": frozenset(head), "SNAP": frozenset(snap)}
            with patch.object(ad, "merge_bc_renames", lambda root, m: pairs[m.sha]), \
                    patch.object(ad, "_bc_roots", lambda root, rev: roots[rev]):
                return ad.snapshot_bc_aliases(self.td, "SNAP", "HEAD", merges)

        chain: "dict[str, tuple]" = {"m1": (("a", "b"),), "m2": (("b", "c"),)}
        two: list = [merge("m1", 1), merge("m2", 3)]
        self.assertEqual(aliases(chain, two, {"c", "k"}, {"a", "k"}), {"c": "a"})            # 두 번 개명을 되짚어 잇는다
        self.assertEqual(aliases(chain, two, {"c", "k"}, {"b", "k"}), {"c": "b"})            # 사이 사본은 사이 이름으로
        self.assertEqual(aliases(chain, two, {"c", "k"}, {"c", "k"}), {})                    # 새 이름이 이미 있는 사본
        self.assertEqual(aliases(chain, two, {"c", "a", "k"}, {"a", "k"}), {})               # 레인이 옛 이름을 되살림
        self.assertEqual(aliases({"m1": (("a", "b"),), "m3": (("a", "c"),)}, [merge("m1", 1), merge("m3", 5)],
                                 {"b", "c"}, {"a"}), {})                                      # 한 옛 이름에 둘이 겹침 → 둘 다 버림
        self.assertEqual(aliases({"m1": (("a", "b"),)}, [merge("m1", None)], {"b"}, {"a"}), {})          # 판정 불참 머지
        self.assertEqual(aliases({"m1": (("a", "b"),)}, [merge("m1", 1, True)], {"b"}, {"a"}), {})       # ^2 가 HEAD 브랜치뿐
        self.assertEqual(aliases({"m1": (("a", "b"),)}, [merge("m1", 1)], {"b"}, {"a"}), {"b": "a"})
        with patch.object(ad, "run_git", side_effect=AssertionError("승인 목록이 없으면 git 을 부르지 않는다")):
            self.assertEqual(ad.snapshot_bc_aliases(self.td, "SNAP", "", []), {})

    def test_P7_fixed_slots_leave_before_names_become_tokens(self) -> None:
        """BC 이름이 트리 낱말(`api`)이어도 고정 칸이 모양에 남아 상관없는 영역과 닮아 보이지 않는다."""
        def upstream(root: Path) -> None:      # 고정 칸뿐인 `api` 를 지우고 고정 칸뿐인 상관없는 영역을 만든다
            shutil.rmtree(root / "application/api")
            self.bc(root, "coupon")
        root, anchor, merge = self.scene("tree-word", {"api": ()}, upstream)
        self.assertEqual(self.pairs(root, anchor, merge), ())
        self.assertEqual(self.ad._bc_shape(frozenset({"driving_layer/api/api_router.py", "driving_layer/api/hello/hello_controller.py",
                                                      "driven_layer/django_api/apps.py"}), "api"),
                         frozenset({"driving_layer/<bc>/hello/hello_controller.py"}))

    def test_P10_short_new_names_do_not_rewrite_the_token(self) -> None:
        """새 이름이 `bc` · `b` · `c` 여도(토큰 `<bc>` 의 글자) BC 이름을 따른 도메인 경로가 같은 모양이 된다 — 한 번에 치환.
        한 이름이 다른 이름의 앞머리인 개명(`fortune → fortune_saju`)은 긴 이름부터 맞춰야 같은 모양이 된다."""
        def named(name: str) -> tuple[str, ...]:
            return (f"domain_layer/{name}/{name}.py", f"domain_layer/{name}/{name}_repository.py",
                    f"domain_layer/{name}/exception/{name}_missing.py")
        for old, new in (("zeta_domain", "bc"), ("zeta_domain", "b"), ("zeta_domain", "c"), ("fortune", "fortune_saju")):
            with self.subTest(new=new):
                root: Path = self.td / f"token-{new}"
                root.mkdir()
                _git(root, "init", "-q", "-b", "main")
                self.bc(root, old, extra=named(old))
                anchor: str = _commit_all(root, "anchor")
                _git(root, "checkout", "-q", "-b", "lane"); _write(root, "lane.txt", "l\n"); _commit_all(root, "lane")
                _git(root, "checkout", "-q", "main"); self.rename(root, old, new); _commit_all(root, "upstream")
                self.assertTrue((root / f"application/{new}/{named(new)[1]}").exists())
                _git(root, "checkout", "-q", "lane"); _git(root, "merge", "-q", "--no-ff", "-m", "approved merge", "main")
                merge: str = _git(root, "rev-parse", "HEAD").stdout.strip()
                _write(root, "lane2.txt", "l\n"); _commit_all(root, "follow-up")
                self.assertEqual(self.ad._bc_shape(frozenset(named(old)), old, new), self.ad._bc_shape(frozenset(named(new)), old, new))
                self.assertEqual(self.pairs(root, anchor, merge), ((old, new),))

    def test_P8_alias_argv_touches_only_the_bc_root_and_django_segment(self) -> None:
        alias: dict[str, str] = {"fortune_saju": "decisive_fortune", "place": "place_core"}
        argv: list[str] = ["/target", "--scope", "fortune_saju", "--api-module", "config/api.py",
            "--scope-bc", "fortune_saju", "--error-bc=fortune_saju", "--scope-bc", "accounts",
            "--controller-module", "application/fortune_saju/driven_layer/django_fortune_saju/apps.py",
            "--project-preserve-error-module=application/fortune_saju/driving_layer/api/bc_error_schema.py",
            "--controller-module", "application/place/driving_layer/api/place/place_controller.py",
            "--registrar-module", "application/accounts/driving_layer/api/fortune_saju/api_router.py",
            "--event-value", "application.fortune_saju.domain_layer.place.exception.place_gone.FortuneSajuPlaceGone.place_id",
            "--anchor", "abc", "--approved-merge-file=fortune_saju.txt"]
        self.assertEqual(self.ad._alias_argv(argv, alias), ["/target", "--scope", "fortune_saju", "--api-module", "config/api.py",
            "--scope-bc", "decisive_fortune", "--error-bc=decisive_fortune", "--scope-bc", "accounts",
            "--controller-module", "application/decisive_fortune/driven_layer/django_decisive_fortune/apps.py",
            "--project-preserve-error-module=application/decisive_fortune/driving_layer/api/bc_error_schema.py",
            "--controller-module", "application/place_core/driving_layer/api/place/place_controller.py",
            "--registrar-module", "application/accounts/driving_layer/api/fortune_saju/api_router.py",
            "--event-value", "application.fortune_saju.domain_layer.place.exception.place_gone.FortuneSajuPlaceGone.place_id",
            "--anchor", "abc", "--approved-merge-file=fortune_saju.txt"])
        # 새 이름이 고정 파일명 · 층 이름 · 안쪽 이름과 겹치는 재료 — BC 뿌리 조각만 바뀐다
        for now, path in (("error", "application/error/driving_layer/api/bc_error_schema.py"),
                          ("bc", "application/bc/driving_layer/api/bc_error_schema.py"),
                          ("api", "application/api/driving_layer/api/api_router.py"),
                          ("order", "application/order/driving_layer/api/order_total/order_total_controller.py"),
                          ("place", "application/place/driving_layer/api/place/place_controller.py"),
                          ("schema", "application/schema/driving_layer/api/place/schema/schema_in.py")):
            with self.subTest(now=now):
                want: str = "application/decisive_fortune/" + path.split("/", 2)[2]
                self.assertEqual(self.ad._alias_argv(["--project-code-error-module", path, "--scope-bc", now, f"--controller-module={path}"],
                                                     {now: "decisive_fortune"}),
                                 ["--project-code-error-module", want, "--scope-bc", "decisive_fortune", f"--controller-module={want}"])

    def test_P9_ladder_prefers_the_plain_render_and_takes_the_renamed_one_only_when_higher(self) -> None:
        """지금 이름의 1칸이 서면 그대로(2.22.2 와 같은 실행) · 서지 않을 때만 옛 이름 사다리 · 그쪽이 더 높은 칸일 때만."""
        ad = self.ad
        argv: list[str] = ["/target", "--scope-bc", "fortune_saju"]
        alias: dict[str, str] = {"fortune_saju": "decisive_fortune"}
        rung2: str = "selector 렌더 재실행(빈 골격 --error-bc 걷음: x · 그 영역 아래 줄 제외)"

        def ladder(plain: str, renamed: str):
            calls: list[bool] = []

            def fake(script, snap, args, flags, alias=None):
                is_renamed: bool = "decisive_fortune" in args
                calls.append(is_renamed)
                return ad._Baseline(0, ["- renamed" if is_renamed else "- plain"], renamed if is_renamed else plain)
            real = ad._baseline_lines
            with patch.object(ad, "_baseline_lines", fake):
                got = real(CTX, self.td, argv, frozenset(), alias)
            return got.lines, got.aliases, calls
        positional: str = "positional 기준선(selector 렌더 불능 강등 — selector-lane 진단은 전량 신규 취급)"
        pair: tuple = (("fortune_saju", "decisive_fortune"),)
        self.assertEqual(ladder("selector 렌더 재실행", "selector 렌더 재실행"), (["- plain"], (), [False]))   # 옛 이름 사다리를 타지도 않는다
        self.assertEqual(ladder(positional, "selector 렌더 재실행"), (["- renamed"], pair, [False, True]))
        self.assertEqual(ladder(positional, rung2), (["- renamed"], pair, [False, True]))
        self.assertEqual(ladder(rung2, "selector 렌더 재실행"), (["- renamed"], pair, [False, True]))
        self.assertEqual(ladder(rung2, rung2), (["- plain"], (), [False, True]))
        self.assertEqual(ladder(positional, positional), (["- plain"], (), [False, True]))
        self.assertEqual(ladder(positional, "기준선 불능(fail-closed — 전량 신규 취급)"), (["- plain"], (), [False, True]))


class RenamedBcBaselineRegression(unittest.TestCase):
    """승인 머지가 상류의 BC 이름 바꾸기를 가져왔고 지금 이름의 selector 렌더가 서지 않을 때, 앵커 · 병합 전 사본의 기준선을
    그 사본의 옛 이름으로 렌더한다(F4-89 남은 몫 — 실제로는 #2 만 해당한다).

    풀리는 쪽(앵커부터 있던 줄 → 앵커 기존분) · 2.22.2 에서 서던 렌더와 유입 증명은 글자 그대로 · 1:1 로 서지 않거나 상황 밖이면
    2.22.2 와 글자 같음(fail-closed) · 레인이 만든 줄은 그대로 신규 · 받아들인 한계를 실제 렌더로 단언한다. 옛 판은 배포 커밋 상수."""

    pair: str = "fortune_saju→decisive_fortune"
    alias_head: str = "  기준선 영역 이름 대응(승인 머지가 가져온 BC 이름 바꾸기 — 앵커 사본은 그 이름으로 렌더): "
    dup: str = ("- application/accounts/driving_layer/api/bc_error_schema.py:N: duplicate project code wire value: "
                "unknown_place_code: from enum import StrEnum")
    extra_lines: set[str] = {
        '- application/accounts/driving_layer/api/bc_error_schema.py:N: additional public field: missing: str = ""',
        '- application/accounts/driving_layer/api/bc_error_schema.py:N: concrete adds field outside common shape: missing: str = ""'}

    def setUp(self) -> None:
        self.temp: tempfile.TemporaryDirectory[str] = tempfile.TemporaryDirectory(prefix="renamed-bc-")
        self.addCleanup(self.temp.cleanup)
        self.td: Path = Path(self.temp.name)
        self.areas: dict[str, str] = {}

    def released(self) -> Path:
        """2.22.2 배포 커밋의 scripts 사본(HEAD 금지 — 이 고침을 커밋한 뒤에도 옛 판이다)."""
        old: Path = self.td / "released-2222"
        if not old.exists():
            old.mkdir()
            archive: subprocess.CompletedProcess[bytes] = subprocess.run(
                ["git", "-C", str(ROOT), "archive", _RELEASED_2222_COMMIT, "dddjango/scripts"], capture_output=True, check=True)
            subprocess.run(["tar", "-x", "-C", str(old)], input=archive.stdout, check=True)
        return old / "dddjango" / "scripts"

    @staticmethod
    def urls(r: ApprovedInflowRepo) -> None:
        bcs: list[str] = sorted(p.parent.parent.parent.name for p in (r.root / "application").glob("*/driving_layer/api/api_router.py"))
        r.write("config/urls.py", "from django.urls import path\nfrom config.api import api\n"
                + "".join(f"from application.{bc}.driving_layer.api.api_router import register_{bc}_api\n" for bc in bcs)
                + "".join(f"register_{bc}_api(api)\n" for bc in bcs) + 'urlpatterns = [path("api/", api.urls)]\n')

    def area(self, r: ApprovedInflowRepo, bc: str, area: str) -> None:
        """place 가 아닌 영역 이름의 최소 컨트롤러(고정 칸 밖 경로 모양이 BC 마다 달라지게)."""
        api: str = f"application/{bc}/driving_layer/api/{area}"
        for rel in (f"application/{bc}/application_layer/{area}/__init__.py", api + "/__init__.py", api + "/schema/__init__.py",
                    api + "/schema/schema_in.py", api + "/schema/schema_out.py"):
            r.write(rel)
        r.write(api + f"/{area}_controller.py", 'from ninja import Router\n\nrouter: Router = Router()\n')

    def anchor(self, name: str, *, df_value: str = "unknown_place_code", df_extra: bool = True,
               acc_extra: bool = False, charm: str | None = None, heavy: bool = False,
               legacy: bool = False) -> tuple[ApprovedInflowRepo, str]:
        r: ApprovedInflowRepo = ApprovedInflowRepo(self.td, name)
        r.project("accounts", "decisive_fortune", "service_policy", *(("lucky_charm",) if charm else ()))
        r.schema("accounts", "unknown_place_code", extra=acc_extra)
        r.schema("decisive_fortune", df_value, extra=df_extra)
        r.controller("accounts", legacy=legacy)
        r.controller("decisive_fortune")
        if charm is not None:
            r.schema("lucky_charm", "charm_unknown", extra=True)
            if charm == "place":
                r.controller("lucky_charm")
            else:
                self.area(r, "lucky_charm", charm)
                self.areas["fortune_charm"] = charm
        if heavy:  # 파일마다 BC 이름이 든 한 줄 — 이름 바꾸기 뒤 git 의 내용 닮음으로는 짝이 0 이 된다
            base: Path = r.root / "application/decisive_fortune"
            for path in sorted(base.rglob("*.py")):
                if path.name != "bc_error_schema.py":
                    path.write_text(f'"""decisive_fortune {path.relative_to(base).as_posix()}."""\n', encoding="utf-8")
        self.urls(r)
        anchor: str = r.commit("anchor")
        r.checkout(anchor, "lane")
        r.schema("service_policy", "policy_unknown")
        r.controller("service_policy")
        self.urls(r)
        r.commit("lane")
        return r, anchor

    @staticmethod
    def full_rename(r: ApprovedInflowRepo, old: str, new: str) -> None:
        """폴더 · 파일 안 이름과 함께 안쪽 경로의 이름(`django_<bc>/`)까지 바꾸는 개명."""
        r.rename_bc(old, new)
        for path in sorted((r.root / "application" / new).rglob(f"*{old}*"), key=lambda p: -len(p.parts)):
            path.rename(path.with_name(path.name.replace(old, new)))

    def upstream(self, r: ApprovedInflowRepo, *steps: tuple[str, str], value: str | None = None, full: bool = False) -> str:
        r.checkout("main")
        for old, new in steps:
            if full:
                self.full_rename(r, old, new)
            else:
                r.rename_bc(old, new)
        if value is not None:
            r.schema(steps[-1][1], value)
        self.urls(r)
        r.commit("upstream rename")
        r.checkout("lane")
        merge: str = r.merge()
        r.write("application/service_policy/application_layer/place/__init__.py", f"# lane follow-up {merge[:7]}\n")
        r.commit("lane follow-up")
        return merge

    def note_merge(self, r: ApprovedInflowRepo, tag: str) -> str:
        r.checkout("main")
        r.write(f"docs/{tag}.txt", tag + "\n")
        r.commit("upstream note " + tag)
        r.checkout("lane")
        merge: str = r.merge()
        r.write(f"lane-{tag}.txt", tag + "\n")
        r.commit("lane after " + tag)
        return merge

    def argv(self, *bcs: str, inventory: bool = True) -> list[str]:
        out: list[str] = ["--error-profile", "dddjango-code-json", "--scope", "f89-code", "--api-module", "config/api.py"]
        for bc in bcs:
            area: str = self.areas.get(bc, "place")
            out += ["--controller-module", f"application/{bc}/driving_layer/api/{area}/{area}_controller.py",
                    "--scope-bc", bc, "--error-bc", bc]
        if inventory:
            for rel in ("framework/ninja/framework_error_schema.py",
                        *(f"application/{bc}/driving_layer/api/bc_error_schema.py" for bc in bcs)):
                out += ["--project-code-error-module", rel]
        return out

    def run_both(self, r: ApprovedInflowRepo, anchor: str, merges: tuple[str, ...], argv: list[str],
                 script: Path = CENT) -> tuple[tuple[int, str], tuple[int, str]]:
        extra: list[str] = ["--anchor", anchor] + (["--approved-merge-file", str(r.approved(*merges))] if merges else [])
        return _run(script, r.root, argv + extra), _run(self.released() / script.name, r.root, argv + extra)

    def assert_existing(self, new: tuple[int, str], lines: set[str], *, inflow: int, pairs: str) -> str:
        code: int
        out: str
        code, out = new
        self.assertEqual(code, 0, out)
        self.assertIn(self.alias_head + pairs + "\n", out)
        self.assertNotIn("  기준선 오류:", out)
        self.assertIn(f"승인 유입 {inflow}건", out)
        self.assertEqual({re.sub(r":\d+:", ":N:", l) for l in _section(out, "앵커 기존분") if l.startswith(("- ", "[#"))},
                         lines, out)
        return out

    def test_R1_ledger_line_moves_to_existing_and_debt_entry_unused(self) -> None:
        r: ApprovedInflowRepo = ApprovedInflowRepo(self.td, "ledger")
        anchor: str
        merge: str
        anchor, merge = r.ledger()
        argv: list[str] = r.selectors(("accounts", "fortune_saju", "service_policy"), inventory=True)
        new, old = self.run_both(r, anchor, (merge,), argv)
        self.assertEqual(old[0], 2, old[1])
        self.assertIn("↳ 귀속 유지: 측정 무효(M^1)", old[1])
        self.assert_existing(new, {self.dup}, inflow=2, pairs=self.pair)
        debt: Path = self.td / "exact-debt.txt"
        debt.write_text("= check-error-centralization.py :: " + self.dup.replace(":N:", ":1:") + "\n", encoding="utf-8")
        new, old = self.run_both(r, anchor, (merge,), argv + ["--legacy-debt-file", str(debt)])
        self.assertEqual(old[0], 0, old[1])
        self.assertIn("이관 빚 1건 · 승인 유입 2건", old[1])
        out: str = self.assert_existing(new, {self.dup}, inflow=2, pairs=self.pair)
        self.assertIn("앵커 기존분(잔존) 1건 · 이관 빚 0건 · 승인 유입 2건", out)

    def test_R2_old_file_subject_lines_also_existing(self) -> None:
        r: ApprovedInflowRepo
        anchor: str
        r, anchor = self.anchor("acc-extra", acc_extra=True)
        merge: str = self.upstream(r, ("decisive_fortune", "fortune_saju"))
        new, old = self.run_both(r, anchor, (merge,), self.argv("accounts", "fortune_saju", "service_policy"))
        self.assertEqual(old[0], 2, old[1])
        self.assertIn("신규분(앵커 이후) 3건", old[1])
        out: str = self.assert_existing(new, {self.dup} | self.extra_lines, inflow=2, pairs=self.pair)
        self.assertIn("신규분(앵커 이후) 0건", out)

    def test_R3_two_merges_rename_in_first_second_and_chain(self) -> None:
        for shape in ("first", "second", "chain"):
            with self.subTest(shape=shape):
                r: ApprovedInflowRepo
                anchor: str
                r, anchor = self.anchor("two-" + shape)
                if shape == "second":
                    m1: str = self.note_merge(r, "one")
                    m2: str = self.upstream(r, ("decisive_fortune", "fortune_saju"))
                else:
                    m1 = self.upstream(r, ("decisive_fortune", "fortune_saju"))
                    m2 = self.note_merge(r, "two") if shape == "first" else self.upstream(r, ("fortune_saju", "saju"))
                now: str = "saju" if shape == "chain" else "fortune_saju"
                new, old = self.run_both(r, anchor, (m1, m2), self.argv("accounts", now, "service_policy"))
                self.assertEqual(old[0], 2, old[1])
                self.assert_existing(new, {self.dup}, inflow=2, pairs=f"{now}→decisive_fortune")

    def test_R4_name_in_every_line_and_small_files_still_pairs(self) -> None:
        """파일 안 이름까지 모두 바뀌어 git 의 내용 닮음(-M)으로는 짝이 0 인 꼴 — 경로 구조로만 짝짓는다."""
        r: ApprovedInflowRepo
        anchor: str
        r, anchor = self.anchor("heavy", heavy=True)
        merge: str = self.upstream(r, ("decisive_fortune", "fortune_saju"))
        renames: list[str] = [l for l in r.git("diff", "-M", "--name-status", anchor, "HEAD", "--", "application/").splitlines()
                              if l.startswith("R") and "application/decisive_fortune/" in l]
        self.assertEqual(renames, [])
        new, old = self.run_both(r, anchor, (merge,), self.argv("accounts", "fortune_saju", "service_policy"))
        self.assertEqual(old[0], 2, old[1])
        self.assert_existing(new, {self.dup}, inflow=2, pairs=self.pair)

    def test_R5_two_bcs_in_one_merge_pair_by_shape(self) -> None:
        r: ApprovedInflowRepo
        anchor: str
        r, anchor = self.anchor("multi", charm="charm")
        merge: str = self.upstream(r, ("decisive_fortune", "fortune_saju"), ("lucky_charm", "fortune_charm"))
        new, old = self.run_both(r, anchor, (merge,), self.argv("accounts", "fortune_charm", "fortune_saju", "service_policy"))
        self.assertEqual(old[0], 2, old[1])
        self.assert_existing(new, {self.dup}, inflow=4, pairs="fortune_charm→lucky_charm, fortune_saju→decisive_fortune")

    def test_R6_rename_with_new_duplicate_from_upstream_is_inflow(self) -> None:
        r: ApprovedInflowRepo
        anchor: str
        r, anchor = self.anchor("newdup", df_value="df_unknown", df_extra=False)
        merge: str = self.upstream(r, ("decisive_fortune", "fortune_saju"), value="unknown_place_code")
        new, old = self.run_both(r, anchor, (merge,), self.argv("accounts", "fortune_saju", "service_policy"))
        self.assertEqual(old[0], 2, old[1])
        self.assertIn("↳ 귀속 유지: 측정 무효(M^1)", old[1])
        code: int
        out: str
        code, out = new
        self.assertEqual(code, 0, out)
        self.assertIn(self.dup.replace(":N:", ":1:") + "\n    ↳ 유입: " + merge[:12] + "(L 증명) · 상호작용", out)
        self.assertIn("    ↳ ^1 기준선: selector 렌더 재실행 — 영역 이름 대응: " + self.pair + "\n", out)

    def test_R7_other_four_scope_renders_are_byte_identical_to_released(self) -> None:
        """#6 · #5 · #15 · #16 은 사본 대응을 받지 않으므로 이름 바꾼 승인 병합 뒤에도 2.22.2 와 글자 같다(정보 줄도 없다 ·
        preserve-established #16 처럼 지금 이름 렌더가 서지 않는 꼴도)."""
        r: ApprovedInflowRepo
        anchor: str
        r, anchor = self.anchor("others", legacy=True)
        merge: str = self.upstream(r, ("decisive_fortune", "fortune_saju"))
        bcs: tuple[str, ...] = ("accounts", "fortune_saju", "service_policy")
        comp: list[str] = ["--error-profile", "dddjango-code-json", "--scope", "f89-code", "--api-module", "config/api.py",
                           "--urlconf-module", "config/urls.py"] + [x for bc in bcs
                           for x in ("--registrar-module", f"application/{bc}/driving_layer/api/api_router.py")]
        seen: int = 0
        for script, argv in ((CTX, self.argv(*bcs, inventory=False)), (OPENAPI, self.argv(*bcs, inventory=False)),
                             (CONTRACT, self.argv(*bcs, inventory=False)), (COMP, comp)):
            with self.subTest(script=script.name):
                new, old = self.run_both(r, anchor, (merge,), argv, script)
                self.assertEqual(new, old)
                self.assertNotIn("영역 이름 대응", new[1])
                seen += "앵커 차분(" in old[1]
        self.assertGreaterEqual(seen, 3)
        new, _old = self.run_both(r, anchor, (merge,), self.argv(*bcs))          # 같은 저장소의 #2 는 풀린다
        self.assert_existing(new, {self.dup}, inflow=2, pairs=self.pair)
        # #16 preserve-established · 새 이름 registrar 하나만 고름 — 앵커 사본에서 그 registrar 가 걷혀 URLconf 만 남으면 지금 이름
        # 렌더가 사용 오류로 서지 않는다. 대응은 #2 에만 넘기므로 옛 registrar 를 되살리지 않는다(2.22.2 와 글자 같음).
        r, anchor = self.anchor("preserve16")
        r.checkout(anchor)
        r.write("application/accounts/composition_root/dependency_wiring.py",
                "from application.accounts.driving_layer.api.bc_error_schema import AccountsErrorSchema\n\n_E = AccountsErrorSchema\n")
        r.git("checkout", "-q", "-B", "main")
        anchor = r.commit("anchor with an accounts #101 line")
        r.git("checkout", "-q", "-B", "lane", anchor)
        r.schema("service_policy", "policy_unknown"); r.controller("service_policy"); self.urls(r); r.commit("lane")
        merge = self.upstream(r, ("decisive_fortune", "fortune_saju"))
        preserve: list[str] = ["--error-profile", "preserve-established", "--scope", "f89-code", "--api-module", "config/api.py",
                               "--urlconf-module", "config/urls.py",
                               "--registrar-module", "application/fortune_saju/driving_layer/api/api_router.py"]
        new, old = self.run_both(r, anchor, (merge,), preserve, COMP)
        self.assertIn("기준선 오류: [check-composition-root] 사용 오류: preserve-established의 --urlconf-module/--registrar-module", old[1])
        self.assertEqual(new, old)
        # #15 · 다른 영역(accounts)이 개명된 영역의 오류 클래스를 import — 지금 이름 렌더가 `re-export provenance 분석 불능` 으로
        # 서지 않는 꼴. 대응은 #2 에만 넘기므로 #15 는 2.22.2 와 글자 같다(풀리지 않음 — 뒤 판 후보).
        def xref(rr: ApprovedInflowRepo, other: str) -> None:
            prefix: str = "".join(word.title() for word in other.split("_"))
            rr.write("application/accounts/driving_layer/api/place/place_controller.py",
                     "from ninja import Router, Status\n"
                     f"from application.{other}.driving_layer.api.bc_error_schema import UnknownPlaceError, {prefix}ErrorSchema\n\n"
                     "router: Router = Router()\n\n"
                     '@router.get("/place", response={200: str, 404: UnknownPlaceError})\n'
                     f"def get_place(request: object, place_id: int) -> str | Status[{prefix}ErrorSchema]:\n"
                     "    try:\n        result: str = str(place_id)\n"
                     "    except ValueError:\n        return Status(404, UnknownPlaceError())\n"
                     "    return result\n")
        r, anchor = self.anchor("xref15", df_value="df_unknown", df_extra=False)
        r.checkout(anchor)
        xref(r, "decisive_fortune"); r.controller("decisive_fortune", legacy=True)
        r.git("checkout", "-q", "-B", "main")
        anchor = r.commit("anchor: accounts controller imports decisive_fortune errors")
        r.git("checkout", "-q", "-B", "lane", anchor)
        r.schema("service_policy", "policy_unknown"); r.controller("service_policy"); self.urls(r); r.commit("lane")
        r.checkout("main"); r.rename_bc("decisive_fortune", "fortune_saju"); xref(r, "fortune_saju"); self.urls(r)
        r.commit("upstream rename + accounts import"); r.checkout("lane"); merge = r.merge()
        r.write("lane2.txt", "lane\n"); r.commit("lane follow-up")
        new, old = self.run_both(r, anchor, (merge,), self.argv(*bcs, inventory=False), CONTRACT)
        self.assertIn("re-export provenance 분석 불능", old[1])
        self.assertEqual(new, old)

    def test_R8_real_shape_two_old_bcs_gone_one_new(self) -> None:
        """현장 모양 — 옛 영역 둘(내용 있는 오류 모듈 하나 · 빈 골격 하나)이 사라지고 새 영역 하나: 개명 + 삭제 / 개명 + 흡수."""
        for shape in ("deleted", "absorbed"):
            with self.subTest(shape=shape):
                r: ApprovedInflowRepo = ApprovedInflowRepo(self.td, "real-" + shape)
                r.project("accounts", "decisive_fortune", "story_content", "service_policy")
                r.schema("accounts", "unknown_place_code")
                r.schema("decisive_fortune", "unknown_place_code", extra=True)
                r.controller("accounts")
                r.controller("decisive_fortune")
                self.area(r, "decisive_fortune", "detail")
                self.area(r, "story_content", "content")          # story_content 의 오류 모듈은 0 바이트 골격 그대로
                self.urls(r)
                anchor: str = r.commit("anchor")
                r.checkout(anchor, "lane")
                r.schema("service_policy", "policy_unknown"); r.controller("service_policy"); self.urls(r); r.commit("lane")
                r.checkout("main")
                r.rename_bc("decisive_fortune", "fortune_saju")
                r.rm("application/story_content")
                if shape == "absorbed":
                    self.area(r, "fortune_saju", "content")
                self.urls(r)
                r.commit("upstream: rename decisive_fortune, " + shape + " story_content")
                r.checkout("lane")
                merge: str = r.merge()
                r.write("lane2.txt", "lane\n"); r.commit("lane follow-up")
                new, old = self.run_both(r, anchor, (merge,), self.argv("accounts", "fortune_saju", "service_policy"))
                self.assertEqual(old[0], 2, old[1])
                self.assertIn("↳ 귀속 유지: 측정 무효(M^1)", old[1])
                self.assert_existing(new, {self.dup}, inflow=2, pairs=self.pair)

    def test_R9_new_names_that_collide_with_fixed_or_inner_names_still_resolve(self) -> None:
        """새 이름이 `error` · `bc` · `api`(고정 파일명 · 층 이름) · `order`(영역 `order_total`) · `place`(영역 `place`)여도 STOP-3 꼴이 풀린다."""
        for now in ("error", "bc", "api", "order", "place"):
            with self.subTest(now=now):
                self.areas = {now: "order_total"} if now == "order" else {}
                r: ApprovedInflowRepo = ApprovedInflowRepo(self.td, "collide-" + now)
                r.project("accounts", "decisive_fortune", "service_policy")
                r.schema("accounts", "unknown_place_code")
                r.schema("decisive_fortune", "unknown_place_code", extra=True)
                r.controller("accounts")
                if now == "order":
                    self.area(r, "decisive_fortune", "order_total")
                else:
                    r.controller("decisive_fortune")
                self.urls(r)
                anchor: str = r.commit("anchor")
                r.checkout(anchor, "lane")
                r.schema("service_policy", "policy_unknown"); r.controller("service_policy"); self.urls(r); r.commit("lane")
                merge: str = self.upstream(r, ("decisive_fortune", now))
                bcs: tuple[str, ...] = tuple(sorted(("accounts", now, "service_policy")))
                new, old = self.run_both(r, anchor, (merge,), self.argv(*bcs))
                self.assertEqual(old[0], 2, old[1])
                self.assert_existing(new, {self.dup}, inflow=2, pairs=f"{now}→decisive_fortune")

    def test_B_released_inflow_and_standing_renders_are_kept(self) -> None:
        """2.22.2 에서 «승인 유입» 이던 실행이 대응 때문에 `측정 무효(M^1)` 로 바뀌지 않는다(검토 차단 1 의 세 재현 — 옛 판과 글자 같음)."""
        def scene(name: str, *, df_schema: "str | None", df_legacy: bool, up_schema: "str | None", up_accounts_legacy: bool):
            r: ApprovedInflowRepo = ApprovedInflowRepo(self.td, name)
            r.project("accounts", "decisive_fortune", "service_policy")
            r.schema("accounts", "unknown_place_code")
            r.controller("accounts")
            if df_schema is not None:
                r.schema("decisive_fortune", df_schema)
            r.controller("decisive_fortune", legacy=df_legacy)
            self.urls(r)
            anchor: str = r.commit("anchor")
            r.checkout(anchor, "lane")
            r.schema("service_policy", "policy_unknown"); r.controller("service_policy"); self.urls(r); r.commit("lane")
            r.checkout("main")
            r.rename_bc("decisive_fortune", "fortune_saju")
            if up_schema is not None:
                r.schema("fortune_saju", up_schema)
            if up_accounts_legacy:
                r.controller("accounts", legacy=True)
            self.urls(r)
            r.commit("upstream rename and more")
            r.checkout("lane")
            merge: str = r.merge()
            r.write("lane2.txt", "lane\n"); r.commit("lane follow-up")
            return r, anchor, merge
        bcs: tuple[str, ...] = ("accounts", "fortune_saju", "service_policy")
        cases = (   # (이름, 재료, 검사기들)
            ("b3", dict(df_schema=None, df_legacy=False, up_schema="unknown_place_code", up_accounts_legacy=False), (CENT,)),
            ("b2", dict(df_schema="df_unknown", df_legacy=True, up_schema=None, up_accounts_legacy=True), (OPENAPI,)),
            ("b1", dict(df_schema=None, df_legacy=False, up_schema="saju_unknown", up_accounts_legacy=True), (CONTRACT, OPENAPI)),
        )
        for name, material, scripts in cases:
            r, anchor, merge = scene(name, **material)
            for script in scripts:
                with self.subTest(case=name, script=script.name):
                    new, old = self.run_both(r, anchor, (merge,), self.argv(*bcs, inventory=script is CENT), script)
                    self.assertEqual(old[0], 0, old[1])
                    self.assertIn("↳ 유입: " + merge[:12], old[1])
                    self.assertEqual(new, old)

    def test_A_lane_cannot_steer_or_forge_a_pair(self) -> None:
        """레인이 옛 폴더를 병합 결과에 남기거나 새 이름을 미리 만들어도 짝이 다른 옛 영역으로 가지 않는다(검토 차단 2 의 두 재현)."""
        # a1 — 상류: decisive_fortune(빈 골격 · 영역 둘) → fortune_saju 개명 + lucky_charm(같은 값 · 절반 겹침) 삭제. 레인: 옛 폴더를 남김.
        r: ApprovedInflowRepo = ApprovedInflowRepo(self.td, "steered")
        r.project("accounts", "decisive_fortune", "lucky_charm", "service_policy")
        r.schema("accounts", "unknown_place_code"); r.controller("accounts")
        r.controller("decisive_fortune"); self.area(r, "decisive_fortune", "detail")
        r.schema("lucky_charm", "unknown_place_code"); r.controller("lucky_charm")
        self.urls(r)
        anchor: str = r.commit("anchor")
        r.checkout(anchor, "lane")
        r.schema("service_policy", "policy_unknown"); r.controller("service_policy")
        r.write("application/decisive_fortune/lane_keep.py", "# lane keeps the old folder alive\n"); self.urls(r); r.commit("lane")
        r.checkout("main")
        r.rename_bc("decisive_fortune", "fortune_saju"); r.schema("fortune_saju", "saju_unknown"); r.rm("application/lucky_charm")
        self.urls(r); r.commit("upstream rename + delete lucky_charm")
        r.checkout("lane")
        self.assertEqual(_git(r.root, "-c", "merge.directoryRenames=false", "merge", "-q", "--no-ff", "-m", "approved merge", "main").returncode, 0)
        merge: str = r.git("rev-parse", "HEAD")
        self.assertEqual(_git(r.root, "cat-file", "-e", merge + ":application/decisive_fortune/lane_keep.py").returncode, 0)
        r.rm("application/decisive_fortune"); r.schema("service_policy", "unknown_place_code"); self.urls(r)
        r.commit("lane removes the kept folder and duplicates the accounts value")
        new, old = self.run_both(r, anchor, (merge,), self.argv("accounts", "fortune_saju", "service_policy"))
        self.assertEqual(old[0], 2, old[1])
        self.assertEqual(new, old)
        # a2 — 상류: 모양이 같은 두 영역을 한 병합에서 개명(동률). 레인: 옛 이름 하나를 남기고 새 이름 하나를 미리 만든다.
        r = ApprovedInflowRepo(self.td, "crossed")
        r.project("accounts", "decisive_fortune", "lucky_charm", "service_policy")
        r.schema("accounts", "unknown_place_code"); r.controller("accounts")
        r.schema("decisive_fortune", "unknown_place_code", extra=True); r.controller("decisive_fortune"); r.controller("lucky_charm")
        self.urls(r)
        anchor = r.commit("anchor")
        r.checkout(anchor, "lane")
        r.schema("service_policy", "policy_unknown"); r.controller("service_policy")
        r.write("application/lucky_charm/lane_keep.py", "# keep\n"); r.write("application/fortune_saju/lane_pre.py", "# pre\n")
        self.urls(r); r.commit("lane")
        r.checkout("main")
        self.full_rename(r, "decisive_fortune", "fortune_saju"); self.full_rename(r, "lucky_charm", "fortune_charm")
        self.urls(r); r.commit("upstream renames two same-shaped BCs")
        r.checkout("lane")
        self.assertEqual(_git(r.root, "-c", "merge.directoryRenames=false", "merge", "-q", "--no-ff", "-m", "approved merge", "main").returncode, 0)
        merge = r.git("rev-parse", "HEAD")
        r.rm("application/lucky_charm"); r.rm("application/fortune_saju/lane_pre.py"); self.urls(r); r.commit("lane follow-up")
        new, old = self.run_both(r, anchor, (merge,), self.argv("accounts", "fortune_charm", "fortune_saju", "service_policy"))
        self.assertEqual(old[0], 2, old[1])
        self.assertEqual(new, old)

    def test_G1_no_one_to_one_pair_or_outside_is_byte_identical_to_released(self) -> None:
        """짝이 서지 않거나 상황 밖이면 2.22.2 와 글자 같음 — 동률 · 상관없는 BC 지우고 만들기 · 같은 이름 파일 하나뿐인 작은 영역 ·
        레인 자기 이름 바꾸기(그대로 · 자기 곁가지 병합을 승인 목록에 올림) · 옛 이름 되살림 · 승인 목록 없음."""
        cases: dict[str, tuple[ApprovedInflowRepo, str, tuple[str, ...], tuple[str, ...]]] = {}
        r, anchor = self.anchor("tie", charm="place")
        merge = self.upstream(r, ("decisive_fortune", "fortune_saju"), ("lucky_charm", "fortune_charm"), full=True)
        cases["tie"] = (r, anchor, (merge,), ("accounts", "fortune_charm", "fortune_saju", "service_policy"))
        r, anchor = self.anchor("delete-add")
        r.checkout("main"); r.rm("application/decisive_fortune"); r.bc("coupon"); r.schema("coupon", "unknown_place_code")
        self.area(r, "coupon", "coupon_issue"); self.areas["coupon"] = "coupon_issue"; self.urls(r)
        r.commit("upstream deletes decisive_fortune, adds coupon"); r.checkout("lane"); merge = r.merge()
        cases["delete-add"] = (r, anchor, (merge,), ("accounts", "coupon", "service_policy"))
        r, anchor = self.anchor("lane-rename")
        r.rename_bc("decisive_fortune", "fortune_saju"); self.urls(r); r.commit("lane renames the partner itself")
        merge = self.note_merge(r, "lr")
        cases["lane-rename"] = (r, anchor, (merge,), ("accounts", "fortune_saju", "service_policy"))
        r, anchor = self.anchor("recreate")
        merge = self.upstream(r, ("decisive_fortune", "fortune_saju"))
        r.bc("decisive_fortune"); r.schema("decisive_fortune", "unknown_place_code"); r.controller("decisive_fortune")
        self.urls(r); r.commit("lane re-creates the old BC name")
        cases["recreate"] = (r, anchor, (merge,), ("accounts", "decisive_fortune", "fortune_saju", "service_policy"))
        r, anchor = self.anchor("anchor-only")
        self.upstream(r, ("decisive_fortune", "fortune_saju"))
        cases["anchor-only"] = (r, anchor, (), ("accounts", "fortune_saju", "service_policy"))
        # 고정 칸 밖 파일이 같은 이름 하나뿐인 작은 영역 둘(지우고 만들기) — 닮음 1.0 이어도 겹친 경로 바닥(3) 아래라 짝이 아니다
        r = ApprovedInflowRepo(self.td, "tiny-mirror")
        r.project("accounts", "lucky_charm", "service_policy")
        r.schema("accounts", "unknown_place_code"); r.controller("accounts"); r.schema("lucky_charm", "unknown_place_code")
        r.write("application/lucky_charm/driven_layer/django_lucky_charm/migrations/0001_initial.py")
        self.urls(r)
        anchor = r.commit("anchor")
        r.checkout(anchor, "lane"); r.schema("service_policy", "policy_unknown"); r.controller("service_policy"); self.urls(r); r.commit("lane")
        r.checkout("main"); r.rm("application/lucky_charm"); r.bc("coupon")
        r.write("application/coupon/driven_layer/django_coupon/migrations/0001_initial.py"); self.urls(r)
        r.commit("upstream deletes lucky_charm, adds an unrelated small coupon"); r.checkout("lane"); merge = r.merge()
        r.schema("service_policy", "unknown_place_code"); r.commit("lane duplicates the accounts value")
        cases["tiny-mirror"] = (r, anchor, (merge,), ("accounts", "service_policy"))
        # 레인이 곁가지에서 이름을 바꿔 자기 가지에 병합하고 그 병합을 승인 목록에 올림 — ^2 를 담은 ref 가 HEAD 브랜치뿐이라 짝을 쓰지 않는다
        r, anchor = self.anchor("own-side-merge", df_value="df_unknown")
        r.checkout("lane", "side"); r.rename_bc("decisive_fortune", "fortune_saju"); self.urls(r); r.commit("lane-made rename on a side branch")
        r.checkout("lane"); r.write("lane-own.txt", "lane\n"); r.commit("lane")
        merge = r.merge("side")
        r.git("branch", "-q", "-D", "side")
        r.schema("fortune_saju", "unknown_place_code", extra=True); r.commit("lane makes the duplicate in the renamed BC")
        cases["own-side-merge"] = (r, anchor, (merge,), ("accounts", "fortune_saju", "service_policy"))
        for name, (r, anchor, merges, bcs) in cases.items():
            for script in (CENT, CTX):
                with self.subTest(case=name, script=script.name):
                    new, old = self.run_both(r, anchor, merges, self.argv(*bcs, inventory=script is CENT), script)
                    self.assertEqual(new, old)
                    self.assertNotIn("영역 이름 대응", new[1])

    def test_G2_lane_made_duplicates_stay_new(self) -> None:
        """레인이 옛 이름 BC 에 중복을 만든 뒤 상류가 이름을 바꿈 · 레인이 짝 BC 를 지우고 중복을 옮김 — 둘 다 신규로 남는다."""
        r: ApprovedInflowRepo
        anchor: str
        r, anchor = self.anchor("old-name-dup", df_value="df_unknown")
        r.schema("decisive_fortune", "unknown_place_code", extra=True); r.commit("lane makes the duplicate")
        r.checkout("main"); r.rename_bc("decisive_fortune", "fortune_saju"); self.urls(r); r.commit("upstream rename")
        r.checkout("lane")
        _git(r.root, "merge", "-q", "--no-ff", "--no-commit", "main")
        _git(r.root, "checkout", "--theirs", "--", ".")
        if (r.root / "application/decisive_fortune").exists():
            r.rm("application/decisive_fortune")
        r.schema("fortune_saju", "unknown_place_code", extra=True); self.urls(r)
        merge: str = r.commit("approved merge keeps the lane value")
        self.assertEqual(len(r.git("show", "-s", "--format=%P", merge).split()), 2)
        new, _old = self.run_both(r, anchor, (merge,), self.argv("accounts", "fortune_saju", "service_policy"))
        self.assertEqual(new[0], 2, new[1])
        self.assertIn(self.dup, {re.sub(r":\d+:", ":N:", l) for l in _section(new[1], "신규분")}, new[1])
        r, anchor = self.anchor("moves-dup")
        r.rm("application/decisive_fortune"); r.schema("service_policy", "unknown_place_code"); self.urls(r)
        r.commit("lane moves the duplicate")
        merge = self.note_merge(r, "mv")
        new, old = self.run_both(r, anchor, (merge,), self.argv("accounts", "service_policy"))
        self.assertEqual(new, old)
        self.assertEqual(new[0], 2, new[1])

    def test_한계_same_text_third_owner_mirrored_delete_add_and_subject_flip(self) -> None:
        """받아들인 한계(성공 보장 아님): ① 레인이 셋째 모듈에 같은 값 — 줄 글자가 같아 앵커 기존분(이름 바꾸기 없을 때와 같은 모델)
        ② 상류가 BC 를 지우고 고정 칸 밖 경로가 똑같은(겹친 경로 3 이상 · 절반 이상) 새 BC 를 만들면 이름 바꾸기로 짝지어진다
        ③ 옛 이름이 짝 모듈보다 알파벳 앞이면 짝이 서도 그대로 막힌다(중복 값 줄의 주어가 알파벳 첫 모듈이라)."""
        r: ApprovedInflowRepo
        anchor: str
        r, anchor = self.anchor("third-owner")
        merge: str = self.upstream(r, ("decisive_fortune", "fortune_saju"))
        r.schema("service_policy", "unknown_place_code"); r.commit("lane adds a third owner of the value")
        new, old = self.run_both(r, anchor, (merge,), self.argv("accounts", "fortune_saju", "service_policy"))
        self.assertEqual(old[0], 2, old[1])
        self.assert_existing(new, {self.dup}, inflow=2, pairs=self.pair)
        r, anchor = self.anchor("mirror")
        r.checkout("main"); r.rm("application/decisive_fortune"); r.bc("coupon"); r.schema("coupon", "unknown_place_code")
        r.controller("coupon"); self.urls(r); r.commit("upstream deletes decisive_fortune, adds coupon of the same shape")
        r.checkout("lane"); merge = r.merge()
        new, old = self.run_both(r, anchor, (merge,), self.argv("accounts", "coupon", "service_policy"))
        self.assertEqual(old[0], 2, old[1])
        self.assertIn(self.alias_head + "coupon→decisive_fortune\n", new[1])
        self.assertEqual(new[0], 0, new[1])
        # ③ 옛 이름이 짝 모듈보다 알파벳 앞(`aaa_fortune` → `zzz_saju`): 앵커 줄의 주어가 옛 영역 쪽이라 글자가 달라 그대로 막힌다
        r = ApprovedInflowRepo(self.td, "subject-flip")
        r.project("accounts", "aaa_fortune", "service_policy")
        r.schema("accounts", "unknown_place_code"); r.controller("accounts")
        r.schema("aaa_fortune", "unknown_place_code"); r.controller("aaa_fortune"); self.urls(r)
        anchor = r.commit("anchor")
        r.checkout(anchor, "lane"); r.schema("service_policy", "policy_unknown"); r.controller("service_policy"); self.urls(r); r.commit("lane")
        merge = self.upstream(r, ("aaa_fortune", "zzz_saju"))
        new, old = self.run_both(r, anchor, (merge,), self.argv("accounts", "service_policy", "zzz_saju"))
        self.assertEqual((old[0], new[0]), (2, 2), new[1])
        self.assertIn(self.alias_head + "zzz_saju→aaa_fortune\n", new[1])
        self.assertIn(self.dup.replace(":N:", ":1:") + "\n    ↳ 귀속 유지: 측정 무효(M^1)", new[1])


class AnchorSnapshotEscapeRegression(unittest.TestCase):
    """앵커 사본에 사본 밖을 가리키는 심링크가 있으면 앵커 실행을 기준선으로 쓰지 않는다(기존 결함 ⓑ 후보 A) — 지금 내용을
    읽어 레인 위반이 «원래 있던 것» 으로 빠지던 길. 저장소 안 상대 심링크는 2.22.2 와 글자 같음."""

    ctx: list[str] = ["--error-profile", "dddjango-code-json", "--scope", "sym", "--api-module", "config/api.py", "--scope-bc", "accounts"]
    gate: Path = S / "registry_gate.py"

    def setUp(self) -> None:
        self.temp: tempfile.TemporaryDirectory[str] = tempfile.TemporaryDirectory(prefix="anchor-escape-")
        self.addCleanup(self.temp.cleanup)
        self.td: Path = Path(self.temp.name)

    def repo(self, kind: str) -> tuple[Path, str]:
        root: Path = self.td / kind
        for rel in ("application/__init__.py", "application/accounts/__init__.py",
                    "application/accounts/domain_layer/__init__.py", "config/__init__.py", "shared/payload_impl.py"):
            _write(root, rel, "")
        _write(root, "config/api.py", "from ninja_extra import NinjaExtraAPI\n\napi: NinjaExtraAPI = NinjaExtraAPI()\n")
        target: str = str((root / "shared/payload_impl.py").resolve()) if kind == "abs" else "../../../shared/payload_impl.py"
        os.symlink(target, root / "application/accounts/domain_layer/payload.py")
        self.assertEqual(_git(root, "init", "-q").returncode, 0)
        anchor: str = _commit_all(root, "anchor")
        _write(root, "shared/payload_impl.py", "from django.db import models\n")
        return root, anchor

    def released(self) -> Path:
        old: Path = self.td / "released-2222"
        if not old.exists():
            old.mkdir()
            archive: subprocess.CompletedProcess[bytes] = subprocess.run(
                ["git", "-C", str(ROOT), "archive", _RELEASED_2222_COMMIT, "dddjango/scripts"], capture_output=True, check=True)
            subprocess.run(["tar", "-x", "-C", str(old)], input=archive.stdout, check=True)
        return old / "dddjango" / "scripts"

    @staticmethod
    def masked(result: tuple[int, str]) -> tuple[int, str]:
        return result[0], "\n".join("툴체인: (가림)" if l.startswith("툴체인:") else l for l in result[1].splitlines())

    def test_E1_absolute_link_at_anchor_is_fail_closed(self) -> None:
        root: Path
        anchor: str
        root, anchor = self.repo("abs")
        code: int
        out: str
        code, out = _run(CTX, root, self.ctx + ["--anchor", anchor])
        self.assertEqual(code, 2, out)
        self.assertIn("기준선=기준선 불능(fail-closed — 전량 신규 취급)", out)
        self.assertIn("  기준선 오류: 앵커 사본에 사본 밖을 가리키는 심링크 application/accounts/domain_layer/payload.py", out)
        self.assertEqual(_run(self.released() / CTX.name, root, self.ctx + ["--anchor", anchor])[0], 0)
        code, out = _run(self.gate, root, ["--anchor", anchor])
        self.assertEqual(code, 2, out)
        self.assertIn(f"주의: 앵커 {anchor[:12]} 사본에 사본 밖을 가리키는 심링크 application/accounts/domain_layer/payload.py — "
                      "기준선 불능이라 fail-closed(현재 위반 전량 귀속)", out)
        self.assertEqual(_run(self.released() / "registry_gate.py", root, ["--anchor", anchor])[0], 0)

    def test_E3_gate_does_not_split_sister_lines_when_the_anchor_is_unusable(self) -> None:
        """«기준선 불능 … 전량 귀속» 을 찍은 실행은 자매 영역(web) 줄도 가르지 않는다(조정자 글 «측정 실패가 먼저다»)."""
        gate = _checker_module(self.gate)
        line: str = "check-context-isolation.py :: [#95] web/a.py: 위반"
        record: dict = {"checker": "check-context-isolation.py", "rule": "#95", "file": "web/a.py", "message": "위반",
                        "kind": "violation", "severity": "error"}

        def fake(target, sink=None, git_root=None, only=None, unclassifiable=None):
            current: bool = Path(target).name == "current"                         # web 줄은 현재 쪽에만(= 귀속 후보)
            return {"check-context-isolation.py": 2 if current else 0}, ({line} if current else set()), ([record] if current else []), set()
        for kind, want_code, sister in (("plain", 0, True), ("escape", 2, False)):
            with self.subTest(kind=kind):
                root: Path = self.td / ("sister-" + kind)
                _write(root, "manage.py", 'import os\nos.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")\n')
                for rel in ("config/settings.py", "shared/x.py"):
                    _write(root, rel, "")
                _write(root, ".gitignore", ".dddjango-web/\n")
                _write(root, "web/a.py", "x = 1\n")
                (root / ".dddjango-web").mkdir()
                if kind == "escape":
                    os.symlink("/dev/null", root / "shared/disabled.conf")
                self.assertEqual(_git(root, "init", "-q").returncode, 0)
                anchor: str = _commit_all(root, "anchor")
                _write(root, "note.md", "dirty\n")
                out: io.StringIO = io.StringIO()
                with patch.object(gate, "_run_registry", side_effect=fake), contextlib.redirect_stdout(out):
                    code: int = gate.main([str(root), "--anchor", anchor])
                text: str = out.getvalue()
                self.assertEqual(code, want_code, text)
                self.assertEqual("자매 플러그인 영역" in text, sister, text)
                if kind == "escape":
                    self.assertIn("기준선 불능이라 fail-closed(현재 위반 전량 귀속)", text)
                    self.assertIn("== 귀속(N∖L) 1건 ==", text)

    def test_E2_in_repo_relative_link_is_byte_identical_to_released(self) -> None:
        root: Path
        anchor: str
        root, anchor = self.repo("rel")
        for script, argv in ((CTX, self.ctx), (self.gate, [])):
            with self.subTest(script=script.name):
                self.assertEqual(self.masked(_run(script, root, argv + ["--anchor", anchor])),
                                 self.masked(_run(self.released() / script.name, root, argv + ["--anchor", anchor])))


class SnapshotLinkHelperRegression(unittest.TestCase):
    """F4-97 · F4-98 · F4-96(2.23.1) — 사본 속 링크 도우미(빼도 되는 자리 · 걷기 전에 재기 · 이름 순서) ·
    잴 수 없음 셈 · scope 렌더 승인 유입 · #15 새 꼴의 앵커 차분."""

    def setUp(self) -> None:
        self.temp: tempfile.TemporaryDirectory[str] = tempfile.TemporaryDirectory(prefix="anchor-link-")
        self.addCleanup(self.temp.cleanup)
        self.td: Path = Path(self.temp.name)
        self.ad: ModuleType = _checker_module(S / "anchor_diff.py")

    def test_prunable_link_protects_document_inputs_in_any_case(self) -> None:
        expect: dict[str, bool] = {
            ".dddjango-web/r/basetemp/test_xcurrent": True, ".dddjango/run/sub/x": True, ".dddjango/run/other.md": True,
            ".github/x": True, "zz/.x": True, "application/orders/x.py": False, ".dddjango": False,
            ".dddjango/run": False, ".dddjango/run/scope.md": False, ".dddjango/run/design-spec.md": False,
            ".DDDJANGO/run/design-spec.md": False, ".dddjango/run/DESIGN-SPEC.MD": False, ".DDDJANGO/run/SCOPE.MD": False}
        self.assertEqual({rel: self.ad.prunable_link(rel) for rel in expect}, expect)

    def test_prune_measures_before_removing_and_names_surface_links_first(self) -> None:
        outside: Path = self.td / "outside"
        outside.mkdir()
        hidden_only: Path = self.td / "hidden-only"
        (hidden_only / ".dddjango-web").mkdir(parents=True)
        os.symlink(str(outside), hidden_only / ".dddjango-web" / "current")
        self.assertEqual(self.ad.prune_hidden_escapes(hidden_only), [".dddjango-web/current"])
        self.assertFalse(os.path.lexists(hidden_only / ".dddjango-web" / "current"))
        self.assertIsNone(self.ad.snapshot_escape(hidden_only))
        through: Path = self.td / "through"
        (through / "application").mkdir(parents=True)
        os.symlink(str(outside), through / ".x")
        os.symlink("../.x/y.py", through / "application" / "y.py")
        self.assertEqual(self.ad.prune_hidden_escapes(through), [])
        self.assertTrue(os.path.islink(through / ".x"))
        self.assertEqual(self.ad.snapshot_escape(through), "application/y.py")

    def test_unmeasured_count_reads_both_measurement_failure_prefixes(self) -> None:
        retained: dict[str, str] = {"a": "측정 무효(스냅숏 실패) — 0123456789ab",
                                    "b": "측정 생략(사슬 커밋 65 > 한도 64) — 0123456789ab",
                                    "c": "유입 증명 실패(이중 원인)"}
        self.assertEqual(self.ad.unmeasured_count(["a", "b", "c", "d"], retained), 2)

    def test_L4_scope_render_inflow_through_record_link_history_is_proven(self) -> None:
        repo: Path
        anchor: str
        repo, anchor = _init_repo(self.td, "l4", F / "skeleton" / "good_bc")
        base: str = _git(repo, "branch", "--show-current").stdout.strip()
        _git(repo, "checkout", "-q", "-b", "lane"); _write(repo, "lane_note.md", "lane\n"); _commit_all(repo, "lane")
        _git(repo, "checkout", "-q", base)
        _write(repo, _VIOLATION_REL, _VIOLATION_SRC)
        link_dir: Path = repo / ".dddjango-web" / "r" / "basetemp"
        link_dir.mkdir(parents=True)
        os.symlink(str(self.td / "gone" / "x1"), link_dir / "test_xcurrent")
        _commit_all(repo, "X1")
        _git(repo, "checkout", "-q", "lane"); _git(repo, "merge", "-q", "--no-ff", "-m", "M1", base)
        m1: str = _git(repo, "rev-parse", "HEAD").stdout.strip()
        _git(repo, "checkout", "-q", base); _git(repo, "rm", "-q", ".dddjango-web/r/basetemp/test_xcurrent"); _commit_all(repo, "X2")
        _git(repo, "checkout", "-q", "lane"); _git(repo, "merge", "-q", "--no-ff", "-m", "M2", base)
        m2: str = _git(repo, "rev-parse", "HEAD").stdout.strip()
        approved: Path = self.td / "l4-approved.txt"
        approved.write_text(f"{m1} M1\n{m2} M2\n", encoding="utf-8")
        code, out = _run(CTX, repo, ["--anchor", anchor, "--approved-merge-file", str(approved)])
        self.assertEqual(code, 0, out)
        self.assertIn("숨김 경로 링크를 뺀 사본", out)
        self.assertNotIn("측정 무효", out)

    def test_C1a_new_predicate_forms_in_an_untouched_controller_are_existing_findings(self) -> None:
        import api_error_backstop_matrix as matrix
        files: dict[str, str] = matrix._f496_files(matrix._f496_body(
            "readiness: LessonReadiness = inspect_lesson(lesson_id)\nmissing: tuple[str, ...] = readiness.missing\n"
            "if missing:\n    incomplete: LessonErrorSchema = LessonIncompleteError()\n    return Status(400, incomplete)\n"
            "return recalculate_lesson(lesson_id)"))
        repo: Path = self.td / "c1a"
        for rel, src in files.items():
            _write(repo, rel, src)
        _git(repo, "init", "-q")
        anchor: str = _commit_all(repo, "anchor")
        _write(repo, "notes.md", "lane\n")
        _commit_all(repo, "lane: unrelated")
        args: list[str] = [a for a in matrix.controller_args() if a != matrix.TARGET_DIR]
        code, out = _run(CONTRACT, repo, [*args, "--anchor", anchor])
        self.assertEqual(code, 0, out)
        self.assertIn("신규분(앵커 이후) 0건", out)
        self.assertIn("Result variant/outcome failure branch forbidden", out)


class HiddenSnapshotRegression(unittest.TestCase):
    """숨김 뺀 풀기(`snapshot_anchor(drop_hidden=True)` — registry_gate 앵커 · 출처 스냅숏 몫): 숨김 폴더를 지나는 항목
    (실행 기록)만 빼고 문서 입력 · 그 조상과 마지막 성분 하나만 숨김인 항목(`.gitkeep` 꼴)은 남긴다 · 뺀 항목의 숨김 아닌
    조상 폴더는 빈 폴더로 둔다(지금 쪽 사본과 같다) · 남길 링크가 사본에 그대로 남지 않는 숨김 칸을 지나면 지금처럼 전체를
    푼다 · 숨김 뺀 풀기가 실패해도 전체를 푼다 · 직접 실행 검사기(`partition_exit`)는 지금처럼 전체를 푼다."""

    def setUp(self) -> None:
        self.temp: tempfile.TemporaryDirectory[str] = tempfile.TemporaryDirectory(prefix="anchor-hidden-")
        self.addCleanup(self.temp.cleanup)
        self.td: Path = Path(self.temp.name)
        self.ad: ModuleType = _checker_module(S / "anchor_diff.py")

    @staticmethod
    def tree(dest: Path) -> "set[str]":
        """사본 안 폴더(끝에 `/`) · 파일 · 링크(사본 상대 경로) — 링크를 따라 내려가지 않는다."""
        out: "set[str]" = set()
        for current, dirs, files in os.walk(dest):
            for name in dirs + files:
                path: str = os.path.join(current, name)
                rel: str = os.path.relpath(path, dest)
                if os.path.islink(path) or os.path.isfile(path):
                    out.add(rel)
                elif os.path.isdir(path):
                    out.add(rel + "/")
        return out

    @staticmethod
    def hidden(paths: "set[str]") -> "set[str]":
        return {p for p in paths if any(part.startswith(".") for part in p.rstrip("/").split("/"))}

    @staticmethod
    def entries(paths: "set[str]") -> "set[str]":
        return {p for p in paths if not p.endswith("/")}

    def snap(self, repo: Path, sha: str, name: str, drop: bool = True) -> "tuple[Path, list[str]]":
        dest: Path = self.td / "snaps" / name
        return dest, self.ad.snapshot_anchor(repo, sha, dest, drop_hidden=drop)

    def repo(self, name: str, files: "dict[str, str]", links: "dict[str, str] | None" = None) -> "tuple[Path, str]":
        root: Path = self.td / name
        for rel, src in files.items():
            _write(root, rel, src)
        for rel, target in (links or {}).items():
            (root / rel).parent.mkdir(parents=True, exist_ok=True)
            os.symlink(target, root / rel)
        self.assertEqual(_git(root, "init", "-q").returncode, 0)
        return root, _commit_all(root, "tree")

    @staticmethod
    def index_add(repo: Path, mode: str, path: str, body: bytes) -> None:
        """작업 트리를 거치지 않고 색인에 바로 넣는다(대소문자만 다른 이름 · UTF-8 아닌 이름 · NFD 이름 그대로)."""
        blob: str = subprocess.run(["git", "-C", str(repo), "hash-object", "-w", "--stdin"], input=body,
                                   capture_output=True, check=True).stdout.decode("ascii").strip()
        subprocess.run(["git", "-C", str(repo), "-c", "core.precomposeunicode=false", "update-index", "--add",
                        "--cacheinfo", f"{mode},{blob},{path}"], capture_output=True, check=True)

    def commit_index(self, repo: Path, message: str) -> str:
        proc: "subprocess.CompletedProcess[str]" = _git(repo, "commit", "-q", "-m", message)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return _git(repo, "rev-parse", "HEAD").stdout.strip()

    def test_A1_records_are_left_out_and_document_inputs_and_dot_files_stay(self) -> None:
        repo: Path
        repo, _anchor = _init_repo(self.td, "a1", F / "skeleton" / "good_bc")
        for rel, src in {".dddjango-web/20261016-run/captures/baseline/application/orders/x.py": "X = 1\n",
                         ".github/workflows/ci.yml": "on: push\n", ".gitignore": "x\n", "application/orders/.keep": "",
                         ".pre-commit-config.yaml": "repos: []\n", "deploy/.env.sample": "KEY=\n",
                         "config/logs/.gitkeep": "", "application/payments/.gitkeep": "",
                         "application/orders/notes/.cache/f": "cache\n",
                         ".dddjango/run1/scope.md": "# 범위\n", ".dddjango/run1/design-spec.md": "# 설계\n",
                         ".dddjango/run1/notes/big.txt": "n\n", ".dddjango/README.md": "r\n"}.items():
            _write(repo, rel, src)
        _commit_all(repo, "records")
        self.index_add(repo, "100644", ".DDDJANGO/run3/DESIGN-SPEC.MD", b"# upper\n")
        sha: str = self.commit_index(repo, "case variant")
        full: Path
        full, _pruned = self.snap(repo, sha, "a1-full", drop=False)
        dest: Path
        pruned: "list[str]"
        dest, pruned = self.snap(repo, sha, "a1")
        got: "set[str]" = self.tree(dest)
        whole: "set[str]" = self.tree(full)
        self.assertEqual(pruned, [])
        # 숨김 아닌 쪽(폴더 포함)은 2.24.2(전체 풀기)와 같다 — 숨김 폴더만 든 `application/orders/notes/` 도 빈 폴더로 있다
        self.assertEqual(got - self.hidden(got), whole - self.hidden(whole))
        self.assertIn("application/orders/notes/", got)
        self.assertNotIn("application/orders/notes/.cache/", got)
        # 풀린 항목 = 트리 항목 가운데 `prunable_path` 가 거짓인 것(가름과 실제 풀기가 같다)
        split: "object" = self.ad.hidden_split(repo, sha)
        self.assertIsNotNone(split)
        self.assertEqual(self.entries(got), {p for p in self.entries(whole) if not self.ad.prunable_path(p)})
        self.assertEqual(split.plain + len(split.kept_hidden), len(self.entries(got)))
        # 마지막 성분 하나만 숨김인 항목은 남고(2.24.2 와 같다), 숨김 폴더 안은 문서 입력 · `.dddjango` 바로 아래만 남는다
        for rel in (".gitignore", ".pre-commit-config.yaml", "deploy/.env.sample", "config/logs/.gitkeep",
                    "application/payments/.gitkeep", "application/orders/.keep"):
            self.assertIn(rel, got)
        under_hidden: "set[str]" = {p.casefold() for p in self.entries(got) if p.startswith((".dddjango/", ".DDDJANGO/"))}
        self.assertEqual(under_hidden, {".dddjango/run1/scope.md", ".dddjango/run1/design-spec.md", ".dddjango/readme.md",
                                        ".dddjango/run3/design-spec.md"})
        self.assertTrue(os.path.lexists(dest / ".DDDJANGO" / "run3" / "DESIGN-SPEC.MD"))
        folded_whole: "set[str]" = {p.casefold() for p in whole}   # 전체 풀기도 `.DDDJANGO` 철자로 한 폴더에 풀 수 있다
        folded_got: "set[str]" = {p.casefold() for p in got}
        for rel in (".dddjango-web/20261016-run/captures/baseline/application/orders/x.py", ".github/workflows/ci.yml",
                    ".dddjango/run1/notes/big.txt", "application/orders/notes/.cache/f"):
            self.assertIn(rel, folded_whole)
            self.assertNotIn(rel, folded_got)

    def test_A2_subfolder_root_follows_archive_scope_and_a_missing_folder_is_an_empty_copy(self) -> None:
        repo: Path
        with_sub: str
        repo, with_sub = self.repo("a2", {"proj/app/a.py": "A = 1\n", "proj/.h/x.py": "H = 1\n", "other/o.txt": "o\n"})
        self.assertEqual(_git(repo, "rm", "-rq", "proj").returncode, 0)
        without_sub: str = self.commit_index(repo, "proj removed")
        self.assertEqual(_git(repo, "checkout", "-q", with_sub).returncode, 0)
        sub: Path = repo / "proj"
        dest: Path
        dest, _pruned = self.snap(sub, with_sub, "a2-with")
        self.assertEqual(self.tree(dest), {"app/", "app/a.py"})
        full: Path
        full, _pruned = self.snap(sub, with_sub, "a2-with-full", drop=False)
        self.assertEqual(self.tree(full), {"app/", "app/a.py", ".h/", ".h/x.py"})
        for drop in (True, False):
            with self.subTest(drop=drop):
                pruned: "list[str]"
                dest, pruned = self.snap(sub, without_sub, f"a2-without-{drop}", drop=drop)
                self.assertEqual((self.tree(dest), pruned), (set(), []))

    def test_A3_only_document_inputs_skips_the_first_archive(self) -> None:
        repo: Path
        sha: str
        repo, sha = self.repo("a3", {".dddjango/run/scope.md": "# 범위\n", ".github/x.yml": "x\n"})
        with patch.object(self.ad, "_untar_archive", wraps=self.ad._untar_archive) as untar:
            dest: Path
            dest, _pruned = self.snap(repo, sha, "a3")
        self.assertEqual(self.tree(dest), {".dddjango/", ".dddjango/run/", ".dddjango/run/scope.md"})
        self.assertEqual([call.args[1] for call in untar.call_args_list],
                         [[sha, "--", ":(literal).dddjango/run/scope.md"]])

    def test_A4_non_utf8_names_never_raise_anything_but_a_named_failure(self) -> None:
        repo: Path
        repo, _sha = self.repo("a4", {"app/ok.py": "OK = 1\n"})
        self.index_add(repo, "100644", ".h/\udcff.py", b"H = 1\n")
        self.index_add(repo, "120000", "app/l", b"\xff-missing")
        sha: str = self.commit_index(repo, "non-utf8 hidden name + link target")
        dest: Path
        pruned: "list[str]"
        dest, pruned = self.snap(repo, sha, "a4")
        self.assertEqual((self.tree(dest), pruned), ({"app/", "app/ok.py", "app/l"}, []))
        self.index_add(repo, "100644", "app/\udcff.py", b"X = 1\n")
        sha = self.commit_index(repo, "non-utf8 surface name")
        for drop in (True, False):
            with self.subTest(drop=drop):
                try:
                    self.snap(repo, sha, f"a4-surface-{drop}", drop=drop)
                except self.ad.AnchorDiffUsage as exc:   # 이 파일 시스템이 그 이름을 못 만들면 이름 붙은 실패(지금 판과 같다)
                    self.assertIn("실패", str(exc))

    def test_A5_pathspec_environment_does_not_change_the_copy(self) -> None:
        repo: Path
        sha: str
        repo, sha = self.repo("a5", {"app/a.py": "A = 1\n", ".h/x.py": "H = 1\n", "app/.cache/y": "y\n",
                                     "app/.keep": "", ".dddjango/run/scope.md": "# 범위\n", "lib/B.py": "B = 1\n"})
        plain: Path
        plain, _pruned = self.snap(repo, sha, "a5-plain")
        self.assertEqual(self.tree(plain), {"app/", "app/a.py", "app/.keep", "lib/", "lib/B.py",
                                            ".dddjango/", ".dddjango/run/", ".dddjango/run/scope.md"})
        for name, env in (("literal-icase-glob", {"GIT_LITERAL_PATHSPECS": "1", "GIT_ICASE_PATHSPECS": "1",
                                                  "GIT_GLOB_PATHSPECS": "1"}),
                          ("noglob", {"GIT_NOGLOB_PATHSPECS": "1"})):
            with self.subTest(env=name), patch.dict(os.environ, env):
                dest: Path
                dest, _pruned = self.snap(repo, sha, "a5-" + name)
                self.assertEqual(self.tree(dest), self.tree(plain))

    def test_A6_A7_A8_kept_links_through_a_dropped_path_extract_everything(self) -> None:
        cases: "dict[str, tuple[dict[str, str], dict[str, str]]]" = {
            "a6": ({".h/x.py": "H = 1\n", "app/b.py": "B = 1\n"}, {"app/x.py": "../.h/x.py"}),
            "a7": ({".x/keep": "k\n", "application/orders/z.py": "Z = 1\n"},
                   {"application/orders/y.py": "../../.x/../application/orders/z.py"}),
            "a8": ({".dddjango/notes/x.md": "# 노트\n", "app/b.py": "B = 1\n"}, {".dddjango/run/scope.md": "../notes/x.md"}),
        }
        for name, (files, links) in cases.items():
            with self.subTest(case=name):
                repo: Path
                sha: str
                repo, sha = self.repo(name, files, links)
                self.assertIsNone(self.ad.hidden_split(repo, sha))
                dest: Path
                pruned: "list[str]"
                dest, pruned = self.snap(repo, sha, name)
                full: Path
                full, _pruned = self.snap(repo, sha, name + "-full", drop=False)
                self.assertEqual((self.tree(dest), pruned), (self.tree(full), []))
                self.assertTrue(self.hidden(self.tree(dest)))
        kept: "frozenset[str]" = frozenset({".dddjango/run/scope.md", ".dddjango/other/scope.md", "config/logs/.gitkeep"})
        crosses = self.ad.link_crosses_pruned
        self.assertTrue(crosses("application/orders/y.py", "../../.x/../application/orders/z.py", kept))
        self.assertTrue(crosses(".dddjango/run/scope.md", "../notes/x.md", kept))
        self.assertTrue(crosses(".dddjango/run/scope.md", "../other/scope.md", kept))   # `.dddjango` 폴더 자체는 남지 않는다
        self.assertTrue(crosses("app/k", "../config/logs/.gitkeep", frozenset()))
        self.assertFalse(crosses("app/k", "../config/logs/.gitkeep", kept))
        self.assertFalse(crosses("app/y.py", "/abs/.h/y.py", kept))

    def test_A9_a_link_leaving_the_copy_root_stops_the_walk_and_stays_fail_closed(self) -> None:
        (self.td / "outside" / ".h").mkdir(parents=True)
        (self.td / "outside" / ".h" / "y.py").write_text("Y = 1\n", encoding="utf-8")
        repo: Path
        sha: str
        repo, sha = self.repo("a9", {"app/b.py": "B = 1\n", ".dddjango-web/r/log.txt": "l\n"},
                              {"app/y.py": "../../outside/.h/y.py"})
        self.assertFalse(self.ad.link_crosses_pruned("app/y.py", "../../outside/.h/y.py", frozenset()))
        dest: Path
        dest, _pruned = self.snap(repo, sha, "a9")
        full: Path
        full, _pruned = self.snap(repo, sha, "a9-full", drop=False)
        self.assertEqual(self.tree(dest), {"app/", "app/b.py", "app/y.py"})
        self.assertEqual(self.ad.snapshot_escape(dest), "app/y.py")
        self.assertEqual(self.ad.snapshot_escape(full), "app/y.py")

    def test_A10_direct_checker_anchor_still_extracts_hidden_records(self) -> None:
        """직접 실행 검사기는 실제 작업 트리를 재므로 앵커도 숨김 경로까지 푼다 — 숨김 경로 주어 줄은 앵커 기존분 그대로."""
        repo: Path
        repo, _anchor = _init_repo(self.td, "a10", F / "skeleton" / "good_bc")
        copied: Path = repo / ".dddjango-web" / "r" / "baseline" / "application"
        shutil.copytree(F / "skeleton" / "good_bc" / "application", copied)
        router: Path = copied / "orders" / "driving_layer" / "api" / "api_router.py"
        router.write_text(router.read_text(encoding="utf-8") + "import os\n", encoding="utf-8")
        anchor: str = _commit_all(repo, "record copy of the app")
        _write(repo, "lane_note.md", "lane\n")
        _commit_all(repo, "lane")
        code: int
        out: str
        code, out = _run(COMP, repo, ["--anchor", anchor])
        self.assertEqual(code, 0, out)
        self.assertIn("신규분(앵커 이후) 0건", out)
        self.assertIn(".dddjango-web/r/baseline/application/orders/driving_layer/api/api_router.py",
                      out.split("== 앵커 기존분", 1)[-1])

    def test_A11_links_to_record_folders_or_dddjango_itself_extract_everything(self) -> None:
        """남길 링크가 사본에 그대로 남지 않는 숨김 칸(`.dddjango` · `.dddjango/<폴더>` 처럼 일부만 남는 폴더 포함)에 닿거나
        지나면 전체를 푼다 — 지금 쪽 사본은 링크를 따라 내용을 실물로 복사한다. 남는 숨김 항목 자체를 가리키면 그대로 뺀다."""
        files: "dict[str, str]" = {".dddjango/run1/notes.md": "n\n", ".dddjango/run2/scope.md": "# 범위\n",
                                   ".dddjango/run2/notes.md": "n\n", "app/b.py": "B = 1\n", ".gitignore": "x\n",
                                   ".dddjango-web/r/log.txt": "l\n"}
        for name, target in (("run1", "../.dddjango/run1"), ("run2", "../.dddjango/run2"), ("root", "../.dddjango"),
                             ("doc", "../.dddjango/run2/scope.md")):
            with self.subTest(link=name):
                repo: Path
                sha: str
                repo, sha = self.repo("a11-" + name, files, {"app/lnk": target})
                self.assertIsNone(self.ad.hidden_split(repo, sha))
                dest: Path
                dest, _pruned = self.snap(repo, sha, "a11-" + name)
                full: Path
                full, _pruned = self.snap(repo, sha, "a11-" + name + "-full", drop=False)
                self.assertEqual(self.tree(dest), self.tree(full))
        repo, sha = self.repo("a11-dotfile", files, {"app/lnk": "../.gitignore"})
        self.assertIsNotNone(self.ad.hidden_split(repo, sha))
        dest, _pruned = self.snap(repo, sha, "a11-dotfile")
        self.assertIn("app/lnk", self.tree(dest))
        self.assertNotIn(".dddjango-web/", self.tree(dest))
        self.assertTrue((dest / "app" / "lnk").is_file())

    def test_A12_split_extraction_failure_falls_back_to_the_full_copy(self) -> None:
        """NFD 로 커밋된 문서 입력 이름은 macOS git 의 argv NFC 바꿈 때문에 `:(literal)` 이 맞지 않는다 — 숨김 뺀 풀기가
        실패하면 사본을 비우고 지금처럼 전체를 푼다(재료 결손 · 측정 무효가 아니다)."""
        import unicodedata
        repo: Path
        repo, _sha = self.repo("a12", {"a.py": "A = 1\n", ".dddjango-web/r/log.txt": "l\n"})
        self.index_add(repo, "100644", unicodedata.normalize("NFD", ".dddjango/결제/scope.md"), b"# scope\n")
        sha: str = self.commit_index(repo, "nfd document input")
        dest: Path
        pruned: "list[str]"
        dest, pruned = self.snap(repo, sha, "a12")
        full: Path
        full, _pruned = self.snap(repo, sha, "a12-full", drop=False)
        nfc = lambda paths: {unicodedata.normalize("NFC", p) for p in paths}  # noqa: E731
        self.assertEqual((nfc(self.tree(dest)), pruned), (nfc(self.tree(full)), []))
        self.assertIn(".dddjango-web/r/log.txt", self.tree(dest))


def main() -> int:
    """스모크 전체를 이 실행 전용 임시 폴더(TMPDIR)에서 돈다 — 게이트 · 검사기의 임시 사본 뿌리가 실제 임시 폴더의
    다른 실행 사본과 섞이지 않게."""
    private: str = tempfile.mkdtemp(prefix="anchor-smoke-tmp-")
    saved: "str | None" = os.environ.get("TMPDIR")
    os.environ["TMPDIR"] = private
    tempfile.tempdir = private
    try:
        return _main()
    finally:
        tempfile.tempdir = None
        if saved is None:
            os.environ.pop("TMPDIR", None)
        else:
            os.environ["TMPDIR"] = saved
        shutil.rmtree(private, ignore_errors=True)


def _main() -> int:
    suite = unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromTestCase(case) for case in (
        BaselineBcArgvRegression, EmptyScopeBcRegression, BcSelectorPartitionRegression, SisterAnchorRegression,
        UnnumberedDebtRegression, BaselineSliceRegression, ApprovedInflowPartitionRegression,
        BcRenamePairingRegression, RenamedBcBaselineRegression, AnchorSnapshotEscapeRegression,
        SnapshotLinkHelperRegression, HiddenSnapshotRegression))
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
