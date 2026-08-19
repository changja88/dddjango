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
from pathlib import Path

ROOT: Path = Path(__file__).resolve().parents[2]
S: Path = ROOT / "dddjango" / "scripts"
F: Path = ROOT / "workspace" / "eval" / "fixtures"
CTX: Path = S / "check-context-isolation.py"
COMP: Path = S / "check-composition-root.py"
CENT: Path = S / "check-error-centralization.py"

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


def main() -> int:
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
