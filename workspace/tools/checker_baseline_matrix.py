#!/usr/bin/env python3
"""검사기 27종 출력 기준선 실측표 — {parsed·정규화 고유·unparsed·synthetic} × 레인.

T2-1 선행 장치(t2-plan v1.1 §2 — 적대 리뷰 L-10 처분): «규약 밖 11종은 일괄
미파싱 1건» 전제가 거짓(파싱 가능·불가능 라인 혼합)임이 실측됐으므로, 개작
«전» 각 검사기의 라인 채널 실태를 registry_gate 와 동일한 눈으로 세어 고정한다.
개작 커밋의 registry_gate 앵커 diff 기대는 이 표가 기준이다.

T2-1 보강 1단계(포매터 계약 §4-1) 확장:
- 계수 5튜플: (exit, parsed_raw, normalized_unique, unparsed, synthetic).
  normalized_unique 는 registry_gate 가 실제 소비하는 «정규화 후 고유 집합» 크기다
  (`_FINDING_RE` 매치 라인을 anchor_diff._normalize 로 절대 경로 접두 제거+`:N`
  라인번호 치환한 뒤 set 크기 — 재구현 없이 양쪽 다 import, S#4 처분 완성).
- 레인 키 공간: 기본 red 레인은 기존 키 `"<script>"` 유지(churn 최소화), 신규
  레인은 `"<script>::<lane>"` 복합 키.
  ① git 3레인(git-clean·git-modified·git-untracked) — git inventory/touched 분기
    검사기 7종에 한해 임시 사본에 git init(+커밋)으로 구성해 실측(적대 검증 S#6:
    비-git fail-closed 분기만 재던 사각의 종결).
  ② 위험 레인 4종(api #59 code·composition 단일 파일·openapi 직접 선언 누락·EC
    code) — fixture 디렉터리가 실재할 때만 계측하고 부재 시 «레인 대기»로
    표기한다(실패 아님). auto 프로필 기본 호출은 tree green 시 code 레인에
    도달하지 않고 즉시 exit 0 이므로(프로필 분기 — 하네스 사각 실증), auto 계열
    3종은 레인 선언의 **커스텀 argv**(dddjango-code-json selector)로 계측한다.
- `--scripts-dir/--fixtures-dir` 주입점 + `--self-test`(findings.py 사본 변조 4종을
  이 하네스+findings_count_matrix 가 red 로 잡는지 실증 — mutation self-test).

계수 정의(registry_gate 와 동일 코퍼스·동일 정규식 — import 로 단일 출처):
- parsed_raw        = stdout+stderr 에서 `_FINDING_RE`(`[#N]` 앵커) 매치 라인 수
- normalized_unique = 매치 라인의 registry_gate 동형 정규화 후 고유 집합 크기
- unparsed          = 비어 있지 않은 비매치 라인 수(ⓓ candidate·rule=null 선행 계약·헤더 등)
- synthetic         = registry_gate 합성 귀속 조건(exit≠0 and parsed==0) 충족 여부

EXPECTED 갱신 규율(기대표 관례): 개작 커밋에서 수치가 바뀌면 같은 커밋에서
`--emit-expected` 로 갱신하되 커밋 메시지에 검사기별 사유(어떤 라인이 왜
늘고 줄었는지)를 전건 기록한다 — 무사유 일괄 갱신 금지.

사용: python3 workspace/tools/checker_baseline_matrix.py
        [--emit <md 경로>] [--emit-expected] [--self-test]
        [--scripts-dir <dir>] [--fixtures-dir <dir>]
exit 0 = EXPECTED 전수 일치 / exit 2 = 불일치 존재 / exit 1 = 재료 결손·사용 오류.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

CHECKER_TIMEOUT_S: int = 300  # 무기한 verify 정지 방지(적대 검증 레인 S 9번)
HARNESS_TIMEOUT_S: int = 900  # self-test 가 하네스 «전체»를 부속 프로세스로 돌릴 때의 상한

ROOT: Path = Path(__file__).resolve().parents[2]
S: Path = ROOT / "dddjango" / "scripts"
F: Path = ROOT / "workspace" / "eval" / "fixtures"
TOOLS: Path = ROOT / "workspace" / "tools"

# 로스터·픽스처 쌍·게이트 정규식·정규화를 전부 import — 재구현 금지(단일 출처).
sys.path.insert(0, str(S))
sys.path.insert(0, str(TOOLS))
from anchor_diff import _normalize  # noqa: E402  (registry_gate 동형 정규화 — S#4 처분)
from checker_registry import REGISTRY, checker_argv  # noqa: E402
from fixture_matrix import AUTO_PAIRS, PLAIN_PAIRS  # noqa: E402  (import 시점 로스터 assert 동승)
from registry_gate import _FINDING_RE  # noqa: E402

_RED_SUB: "dict[str, str]" = {"check-layer-skeleton.py": "skeleton/bad_legacy_flat"}
_RED_SUB.update({s: f"{fx}/bad_rules" for s, fx in PLAIN_PAIRS})
_RED_SUB.update({s: f"{fx}/bad_rules" for s, fx in AUTO_PAIRS})

# ── 레인 선언(포매터 계약 §4-1 — findings_count_matrix 가 같은 선언을 import 한다) ──
# 기본 red 레인의 lane 표지("red")는 키에 넣지 않는다 — 기존 키 유지(churn 최소화).
DEFAULT_LANE: str = "red"
GIT_LANES: "tuple[str, str, str]" = ("git-clean", "git-modified", "git-untracked")
# git inventory/touched 분기 영향 7종(적대 검증 S#6 실측 — clean git 에서 exit/레코드가 달라진 군).
GIT_AFFECTED: "tuple[str, ...]" = (
    "check-response-schema-bypass.py",
    "check-app-container.py",
    "check-idempotency-scope-creep.py",
    "check-transient-overmapping.py",
    "check-choices-literal-consumption.py",
    "check-synthetic-infra-exc.py",
    "check-db-table.py",
)
# 위험 레인 4종 — (검사기, fixture 레인 디렉터리, TARGET 뒤 커스텀 argv).
# `<lane_dir>/bad_rules` 가 실재할 때만 계측. argv=() 는 무옵션 positional 호출이고,
# auto 계열 3종은 dddjango-code-json selector 렌더로 code 레인에 실도달시킨다
# (auto 기본 호출은 tree green 시 exit 0 — 표 하단에 사각 실증 관찰 라인 병기).
_RISK_SELECTOR_ARGS: "tuple[str, ...]" = (
    "--error-profile", "dddjango-code-json", "--scope", "public-v1",
    "--api-module", "config/api.py",
    "--controller-module", "application/lesson/driving_layer/controller.py",
    "--scope-bc", "lesson", "--error-bc", "lesson",
)
RISK_LANES: "tuple[tuple[str, str, tuple[str, ...]], ...]" = (
    ("check-api-error-controller-contract.py", "api_error_controller_code", _RISK_SELECTOR_ARGS),
    ("check-composition-root.py", "composition_root_single_file", ()),
    ("check-openapi-error-declaration.py", "openapi_decl_missing", _RISK_SELECTOR_ARGS),
    ("check-error-centralization.py", "error_centralization_code", _RISK_SELECTOR_ARGS + (
        "--project-code-error-module", "framework/ninja/framework_error_schema.py",
        "--project-code-error-module", "application/lesson/driving_layer/api/bc_error_schema.py",
    )),
    # R-3401 병존형 canon 의 경계 회귀 — 공통이 nullable(비-bare)·Annotated-metadata
    # 자리일 때 Literal 병존 우회가 새지 않음을 고정한다(계획 2026-08-24 §3).
    ("check-error-centralization.py", "error_centralization_literal_edge", _RISK_SELECTOR_ARGS + (
        "--project-code-error-module", "framework/ninja/framework_error_schema.py",
        "--project-code-error-module", "application/lesson/driving_layer/api/bc_error_schema.py",
    )),
)
_RISK_DIRS: "frozenset[str]" = frozenset(d for _s, d, _a in RISK_LANES)
_RISK_ARGV: "dict[str, tuple[str, ...]]" = {d: a for _s, d, a in RISK_LANES}

# ── 가드 레인 20종(귀속 매핑표 v2 A-5/A-6 — 대상-0 가드 발화 골든·M6 완결) ──
# 각 레인 = «층 신호 디렉터리만 있는» 픽스처(.gitkeep 뿐·파일 0) 호출 → exit 2·
# guard 1라인·레코드 1건(rule=null·sentinel=대상0·severity=violation). A-5 로스터
# 21 중 20 편입 — 제외 1 = context-isolation(가드 도달 불능: 신호 판정이 공집합에서
# 선행 clean 하는 사도 분기 — A-5 확정 주기·코드는 방어적 존치).
GUARD_LANE: str = "guard-zero"
_GUARD_EC_ARGS: "tuple[str, ...]" = _RISK_SELECTOR_ARGS + (
    "--project-code-error-module", "framework/ninja/framework_error_schema.py",
    "--project-code-error-module", "application/lesson/driving_layer/api/bc_error_schema.py",
)
# (검사기, fixture, TARGET 뒤 argv) — code-profile 2종(api-error·EC)은 selector 조합에서의
# 대상-0 발화를 고정(혼성 패널 M6 — 21지점 중 20 편입·context-isolation 만 도달 불능 제외).
GUARD_LANES: "tuple[tuple[str, str, tuple[str, ...]], ...]" = (
    ("check-api-error-controller-contract.py", "guard_zero_domain", _RISK_SELECTOR_ARGS),
    ("check-db-table.py", "guard_zero_domain", ()),
    ("check-domain-model.py", "guard_zero_django", ()),
    ("check-error-centralization.py", "guard_zero_domain", _GUARD_EC_ARGS),
    ("check-event-publish.py", "guard_zero_domain", ()),
    ("check-idempotency-scope-creep.py", "guard_zero_domain", ()),
    ("check-layer-skeleton.py", "guard_zero_framework", ()),
    ("check-mechanism-ownership.py", "guard_zero_domain", ()),
    ("check-missable-entrance.py", "guard_zero_domain", ()),
    ("check-naming.py", "guard_zero_domain", ()),
    ("check-ninja-boundary-middleware.py", "guard_zero_domain", ()),
    ("check-openapi-error-declaration.py", "guard_zero_domain", ()),
    ("check-port-adapter-pairing.py", "guard_zero_domain", ()),
    ("check-public-surface-annotation.py", "guard_zero_domain", ()),
    ("check-response-schema-bypass.py", "guard_zero_domain", ()),
    ("check-synthetic-infra-exc.py", "guard_zero_domain", ()),
    ("check-test-config.py", "guard_zero_domain", ()),
    ("check-transaction-boundary.py", "guard_zero_django", ()),
    ("check-transient-overmapping.py", "guard_zero_domain", ()),
    ("check-usecase-dto-placement.py", "guard_zero_django", ()),
)
_GUARD_FIXTURE: "dict[str, str]" = {s: fx for s, fx, _a in GUARD_LANES}
_GUARD_ARGV: "dict[str, tuple[str, ...]]" = {s: a for s, _fx, a in GUARD_LANES}


def lane_allowed_exits(lane: str) -> "frozenset[int]":
    """emit-expected 세탁 거부의 레인별 정당 exit 선언 — git 레인은 clean 저장소에서
    정당하게 exit 0 이 나온다(S#6: response-schema 2/1→0/0 등). red·위험 레인은 2 만."""
    if lane in GIT_LANES:
        return frozenset({0, 2})
    return frozenset({2})


def lane_argv(script: str, auto: bool, target: str, scripts_dir: Path,
              lane: str = DEFAULT_LANE) -> "list[str]":
    """checker 호출 argv — 기본은 checker_registry.checker_argv(단일 출처).
    위험 레인은 선언된 커스텀 argv(auto 플래그 대체), --scripts-dir 주입(변조
    self-test) 시에는 같은 «형태»로 주입 디렉터리를 쓴다."""
    if lane in _RISK_DIRS:
        return [sys.executable, str(scripts_dir / script), target, *_RISK_ARGV[lane]]
    if lane == GUARD_LANE:
        # 가드 재현은 무옵션 positional 기본·code-profile 2종만 선언 argv(M6) — auto 미부가.
        return [sys.executable, str(scripts_dir / script), target, *_GUARD_ARGV[script]]
    if scripts_dir == S:
        return checker_argv(sys.executable, script, target, auto)
    argv: "list[str]" = [sys.executable, str(scripts_dir / script), target]
    if auto:
        argv += ["--error-profile", "auto"]
    return argv


def _git(cwd: Path, *args: str) -> None:
    proc = subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True)
    if proc.returncode != 0:
        print(f"재료 결손: git 레인 구성 실패 — git {' '.join(args)}: "
              f"{proc.stderr.strip() or proc.stdout.strip()}", file=sys.stderr)
        raise SystemExit(1)


_GIT_COMMIT_ARGS: "tuple[str, ...]" = (
    # 결정적 저자 + 서명 비활성(api_error_backstop_matrix 판형) — 사용자 git 설정 비상속.
    "-c", "user.name=baseline-matrix", "-c", "user.email=matrix@example.invalid",
    "-c", "commit.gpgsign=false", "commit", "--quiet", "--allow-empty", "-m", "lane baseline",
)


def prepare_lane_copy(src: Path, dest: Path, lane: str) -> None:
    """fixture 를 임시 사본으로 준비한다(hermetic — fixture_matrix 전례).

    git 3레인은 사본 «안»에 저장소를 구성해 git inventory/touched 분기를 실측한다:
      git-clean     = init + 전 파일 커밋(clean tracked)
      git-modified  = clean 구성 후 정렬 첫 .py 파일 1개에 말미 주석 추가(modified tracked)
      git-untracked = init + 빈 커밋만(HEAD 실재·fixture 파일은 전부 untracked «그대로»)
    """
    shutil.copytree(src, dest)
    if lane not in GIT_LANES:
        return
    _git(dest, "init", "--quiet")
    if lane == "git-untracked":
        _git(dest, *_GIT_COMMIT_ARGS)
        return
    _git(dest, "add", ".")
    _git(dest, *_GIT_COMMIT_ARGS)
    if lane == "git-modified":
        pys: "list[Path]" = sorted(dest.rglob("*.py"))
        if not pys:
            print(f"재료 결손: git-modified 레인 — {src} 에 .py 파일 없음", file=sys.stderr)
            raise SystemExit(1)
        with open(pys[0], "a", encoding="utf-8") as fh:
            fh.write("\n# git-modified 레인 표식(하네스 생성 — 검사 의미 무변 말미 주석)\n")


def lane_plan(fixtures_dir: Path) -> "list[tuple[str, str, str, Path | None]]":
    """(키, 검사기, 레인, 원천 fixture 경로) — 경로 None = 레인 대기(픽스처 병행 제작·실패 아님)."""
    plan: "list[tuple[str, str, str, Path | None]]" = []
    for script, _auto in REGISTRY:
        plan.append((script, script, DEFAULT_LANE, fixtures_dir / _RED_SUB[script]))
    for script in GIT_AFFECTED:
        for lane in GIT_LANES:
            plan.append((f"{script}::{lane}", script, lane, fixtures_dir / _RED_SUB[script]))
    for script, lane_dir, _extra in RISK_LANES:
        src: Path = fixtures_dir / lane_dir / "bad_rules"
        plan.append((f"{script}::{lane_dir}", script, lane_dir, src if src.is_dir() else None))
    for script, guard_fx, _a in GUARD_LANES:
        plan.append((f"{script}::{GUARD_LANE}", script, GUARD_LANE, fixtures_dir / guard_fx))
    return plan


# 기준선(--emit-expected 재생성): 키 -> (exit, parsed_raw, normalized_unique, unparsed, synthetic)
# 기본 레인 27종은 2026-08-19 개작 전 실측과 동일(exit·parsed_raw·unparsed·synthetic 무변 —
# normalized_unique 열만 신규 실측). git 3레인은 2026-08-20 보강 1단계 실측(S#6 부합:
# response-schema·app-container·idempotency·transient·choices 는 clean git 에서 exit 0).
# 실측 검증: domain_model parsed=48 = findings_smoke DM_COUNT_VIOLATION · common_container
# synthetic = rule=null 선행 계약 라인(비[#N]) 실증. synthetic 군은 7종(«11종» 아님 — L-10 확정).
EXPECTED: "dict[str, tuple[int, int, int, int, bool]]" = {
    "check-mechanism-ownership.py": (2, 6, 6, 1, False),
    "check-error-centralization.py": (2, 5, 5, 1, False),
    "check-response-schema-bypass.py": (2, 0, 0, 3, True),
    "check-layer-skeleton.py": (2, 10, 10, 1, False),
    "check-openapi-error-declaration.py": (2, 3, 3, 1, False),
    "check-context-isolation.py": (2, 58, 57, 6, False),
    "check-app-container.py": (2, 0, 0, 4, True),
    "check-ninja-boundary-middleware.py": (2, 0, 0, 4, True),
    "check-common-container.py": (2, 0, 0, 4, True),
    "check-idempotency-scope-creep.py": (2, 0, 0, 3, True),
    "check-public-surface-annotation.py": (2, 10, 10, 4, False),
    "check-test-config.py": (2, 13, 13, 2, False),
    "check-transient-overmapping.py": (2, 0, 0, 3, True),
    "check-synthetic-infra-exc.py": (2, 1, 1, 2, False),
    "check-api-error-controller-contract.py": (2, 9, 9, 3, False),
    "check-composition-root.py": (2, 18, 18, 4, False),
    "check-db-table.py": (2, 26, 26, 2, False),
    "check-choices-literal-consumption.py": (2, 0, 0, 6, True),
    "check-usecase-dto-placement.py": (2, 35, 35, 7, False),
    "check-transaction-boundary.py": (2, 13, 13, 3, False),
    "check-domain-model.py": (2, 48, 47, 14, False),
    "check-port-adapter-pairing.py": (2, 79, 79, 10, False),
    "check-event-publish.py": (2, 20, 20, 5, False),
    "check-broker-contract.py": (2, 22, 22, 6, False),
    "check-missable-entrance.py": (2, 17, 17, 5, False),
    "check-naming.py": (2, 29, 29, 6, False),
    "check-business-vocabulary.py": (2, 48, 48, 7, False),
    "check-response-schema-bypass.py::git-clean": (0, 0, 0, 0, False),
    "check-response-schema-bypass.py::git-modified": (2, 0, 0, 3, True),
    "check-response-schema-bypass.py::git-untracked": (2, 0, 0, 3, True),
    "check-app-container.py::git-clean": (0, 0, 0, 0, False),
    "check-app-container.py::git-modified": (0, 0, 0, 0, False),
    "check-app-container.py::git-untracked": (2, 0, 0, 3, True),
    "check-idempotency-scope-creep.py::git-clean": (0, 0, 0, 0, False),
    "check-idempotency-scope-creep.py::git-modified": (2, 0, 0, 3, True),
    "check-idempotency-scope-creep.py::git-untracked": (2, 0, 0, 3, True),
    "check-transient-overmapping.py::git-clean": (0, 0, 0, 0, False),
    "check-transient-overmapping.py::git-modified": (0, 0, 0, 0, False),
    "check-transient-overmapping.py::git-untracked": (2, 0, 0, 3, True),
    "check-choices-literal-consumption.py::git-clean": (0, 0, 0, 0, False),
    "check-choices-literal-consumption.py::git-modified": (0, 0, 0, 0, False),
    "check-choices-literal-consumption.py::git-untracked": (0, 0, 0, 0, False),
    "check-synthetic-infra-exc.py::git-clean": (2, 1, 1, 1, False),
    "check-synthetic-infra-exc.py::git-modified": (2, 1, 1, 1, False),
    "check-synthetic-infra-exc.py::git-untracked": (2, 1, 1, 2, False),
    "check-db-table.py::git-clean": (2, 24, 24, 1, False),
    "check-db-table.py::git-modified": (2, 24, 24, 1, False),
    "check-db-table.py::git-untracked": (2, 26, 26, 1, False),
    # 위험 레인 4종(2026-08-20 실측 — 픽스처 완성분·레인 커스텀 argv): auto 기본 호출은
    # tree green 시 code 레인 미도달 exit 0(표 하단 관찰 라인) — selector 렌더로 실도달.
    # parsed 0·synthetic True = code 레인 발화가 아직 [#N] 라인 앵커 밖(구 문면)이라는
    # 정직한 기록 — 3단계 포매터 이행 시 parsed 증가로 갱신된다(사유 의무).
    "check-api-error-controller-contract.py::api_error_controller_code": (2, 3, 3, 2, False),
    "check-composition-root.py::composition_root_single_file": (2, 1, 1, 2, False),
    "check-openapi-error-declaration.py::openapi_decl_missing": (2, 1, 1, 2, False),
    # unparsed 4→11: R-3401 경계 red 2 concrete(무 default Literal 5·좁힘값≠default 2) 추가(2026-08-24)
    "check-error-centralization.py::error_centralization_code": (2, 1, 1, 11, False),
    "check-error-centralization.py::error_centralization_literal_edge": (2, 0, 0, 5, True),
    "check-api-error-controller-contract.py::guard-zero": (2, 0, 0, 1, True),
    "check-error-centralization.py::guard-zero": (2, 0, 0, 1, True),
    "check-openapi-error-declaration.py::guard-zero": (2, 0, 0, 1, True),
    "check-response-schema-bypass.py::guard-zero": (2, 0, 0, 1, True),
    "check-db-table.py::guard-zero": (2, 0, 0, 1, True),
    "check-domain-model.py::guard-zero": (2, 0, 0, 1, True),
    "check-event-publish.py::guard-zero": (2, 0, 0, 1, True),
    "check-idempotency-scope-creep.py::guard-zero": (2, 0, 0, 1, True),
    "check-layer-skeleton.py::guard-zero": (2, 0, 0, 1, True),
    "check-mechanism-ownership.py::guard-zero": (2, 0, 0, 1, True),
    "check-missable-entrance.py::guard-zero": (2, 0, 0, 1, True),
    "check-naming.py::guard-zero": (2, 0, 0, 1, True),
    "check-ninja-boundary-middleware.py::guard-zero": (2, 0, 0, 1, True),
    "check-port-adapter-pairing.py::guard-zero": (2, 0, 0, 1, True),
    "check-public-surface-annotation.py::guard-zero": (2, 0, 0, 1, True),
    "check-synthetic-infra-exc.py::guard-zero": (2, 0, 0, 1, True),
    "check-test-config.py::guard-zero": (2, 0, 0, 1, True),
    "check-transaction-boundary.py::guard-zero": (2, 0, 0, 1, True),
    "check-transient-overmapping.py::guard-zero": (2, 0, 0, 1, True),
    "check-usecase-dto-placement.py::guard-zero": (2, 0, 0, 1, True),
}


def _count_lane(script: str, auto: bool, src: Path, lane: str,
                scripts_dir: Path) -> "tuple[int, int, int, int, bool]":
    with tempfile.TemporaryDirectory() as td:
        tmp_fx = Path(td) / "fixture"
        prepare_lane_copy(src, tmp_fx, lane)
        # 사용자 환경의 DJR_FINDINGS_JSON 을 상속하면 이 하네스가 사용자의 실제
        # 레코드 파일에 테스트 레코드를 append 한다(T2-1 적대 검증 레인 S 7번 — 544행 오염
        # 실증). 라인 채널만 재는 도구이므로 레코드 sink 를 아예 끊는다.
        env = dict(os.environ)
        env.pop("DJR_FINDINGS_JSON", None)
        proc = subprocess.run(
            lane_argv(script, auto, str(tmp_fx), scripts_dir, lane),
            capture_output=True, text=True, cwd=str(ROOT), env=env,
            timeout=CHECKER_TIMEOUT_S,
        )
        prefixes: "tuple[str, ...]" = (str(tmp_fx) + "/", str(tmp_fx))
        parsed_raw = unparsed = 0
        normalized: "set[str]" = set()
        for raw in (proc.stdout + "\n" + proc.stderr).splitlines():
            if not raw.strip():
                continue
            m = _FINDING_RE.match(raw)
            if m:
                parsed_raw += 1
                normalized.add(_normalize(m.group(1), prefixes))
            else:
                unparsed += 1
    synthetic = proc.returncode != 0 and parsed_raw == 0
    return (proc.returncode, parsed_raw, len(normalized), unparsed, synthetic)


def measure(scripts_dir: Path, fixtures_dir: Path
            ) -> "tuple[dict[str, tuple[int, int, int, int, bool]], list[str]]":
    """레인 계획 전수 실측 — (키→5튜플, 레인 대기 키 목록)."""
    roster: "dict[str, bool]" = dict(REGISTRY)
    got: "dict[str, tuple[int, int, int, int, bool]]" = {}
    waiting: "list[str]" = []
    for key, script, lane, src in lane_plan(fixtures_dir):
        if src is None:
            waiting.append(key)
            continue
        if not src.is_dir():
            print(f"재료 결손: fixture {src} 없음", file=sys.stderr)
            raise SystemExit(1)
        got[key] = _count_lane(script, roster[script], src, lane, scripts_dir)
    return got, waiting


# ── mutation self-test(§4-1) — findings.py 사본 변조 4종을 하네스 쌍이 잡는지 실증 ──
# 레코드 변조는 검사기가 아니라 findings.py 사본에 가한다(검사기 사본 전부가 이 모듈을
# 경유하므로 한 곳 변조가 27종 전체에 미친다). 각 항목: (이름, 설명, 추가 코드, 후속 대기 여부)
# 후속 대기 = 현시점 하네스가 정당하게 못 잡는 변조(3단계 ordered oracle 완성 후 red 전환).
_MUTATIONS: "tuple[tuple[str, str, str, bool], ...]" = (
    ("record-drop", "라인 유지+레코드 누락(첫 레코드 1건 침묵 탈락)", """
# [self-test 변조: record-drop] 라인 채널은 그대로, 프로세스 첫 레코드 1건만 침묵 탈락.
_st_orig_emit = _emit
_st_dropped = [False]
def _emit(*args, **kwargs):
    if not _st_dropped[0]:
        _st_dropped[0] = True
        return
    _st_orig_emit(*args, **kwargs)
""", False),
    ("rule-swap", "레코드 rule 교체(#N → #999999 — 라인 무변)", """
# [self-test 변조: rule-swap] 라인 채널은 그대로, 레코드의 rule 만 바꾼다.
_st_orig_emit = _emit
def _emit(checker, rule, file, symbol, severity, message, contract_ref=None):
    if rule is not None:
        rule = "#999999"
    _st_orig_emit(checker, rule, file, symbol, severity, message, contract_ref=contract_ref)
""", False),
    ("reorder", "레코드 순서 역전(종료 시 역순 방출·서수 재채번 — 은닉형)", """
# [self-test 변조: reorder] 방출을 버퍼링했다가 프로세스 종료 시 역순으로 쓴다.
# 서수(record_id)는 쓰는 시점에 채번되므로 연속 증가 oracle 을 회피하는 은닉형 —
# stdout↔record «ordered» 대조(--strict-order·3단계 이행 후 기본화)만 잡을 수 있다.
import atexit as _st_atexit
_st_orig_emit = _emit
_st_buffer = []
def _emit(*args, **kwargs):
    _st_buffer.append((args, kwargs))
def _st_flush():
    for args, kwargs in reversed(_st_buffer):
        _st_orig_emit(*args, **kwargs)
_st_atexit.register(_st_flush)
""", False),
    ("duplicate", "레코드 중복 삽입(전건 2회 방출 — 라인 무변)", """
# [self-test 변조: duplicate] 라인 채널은 그대로, 레코드를 전건 2회 방출한다.
_st_orig_emit = _emit
def _emit(*args, **kwargs):
    _st_orig_emit(*args, **kwargs)
    _st_orig_emit(*args, **kwargs)
""", False),
    ("stdout-message-drift", "라인 문면만 변조(레코드 무변 — 혼성 패널 M5 실증 축)", """
# [self-test 변조: stdout-message-drift] 레코드 필드는 그대로, violation 라인 문면만
# 뒤에 표식을 붙인다 — (severity, rule) 열 대조는 통과하고 재구성 대조만 잡을 수 있다.
_st_orig_line = FindingEntry.line
def _st_drift_line(self):
    s = _st_orig_line.fget(self)
    return s + " [DRIFT]" if self.kind == "violation" else s
FindingEntry.line = property(_st_drift_line)
""", False),
)


def _run_harness(name: str, scripts_dir: "Path | None") -> int:
    cmd: "list[str]" = [sys.executable, str(TOOLS / name)]
    if scripts_dir is not None:
        cmd += ["--scripts-dir", str(scripts_dir)]
    env = dict(os.environ)
    env["PYTHONUTF8"] = "1"
    return subprocess.run(cmd, capture_output=True, text=True, env=env,
                          cwd=str(ROOT), timeout=HARNESS_TIMEOUT_S).returncode


def self_test() -> int:
    """검사기 사본(findings.py) 변조 4종 × {이 하네스, findings_count_matrix} red 실증."""
    # 대조군: 무변조 상태의 두 하네스가 green 이어야 변조 red 가 «검출»의 증거가 된다.
    base_ctl = _run_harness("checker_baseline_matrix.py", None)
    count_ctl = _run_harness("findings_count_matrix.py", None)
    if base_ctl != 0 or count_ctl != 0:
        print(f"재료 결손: 무변조 대조군이 green 이 아니다 — baseline exit {base_ctl} · "
              f"count exit {count_ctl}. self-test 는 green 기반에서만 의미가 있다", file=sys.stderr)
        return 1
    rows: "list[str]" = [
        "| 변조 | baseline exit | count exit | 판정 |",
        "|---|---|---|---|",
        f"| (대조군 무변조) | {base_ctl} | {count_ctl} | green 기반 확인 ✓ |",
    ]
    failed: "list[str]" = []
    with tempfile.TemporaryDirectory(prefix="djr-mutation-selftest-", dir="/tmp") as td:
        for name, desc, snippet, deferred in _MUTATIONS:
            mut_dir = Path(td) / name
            shutil.copytree(S, mut_dir, ignore=shutil.ignore_patterns("__pycache__"))
            with open(mut_dir / "findings.py", "a", encoding="utf-8") as fh:
                fh.write(snippet)
            base_rc = _run_harness("checker_baseline_matrix.py", mut_dir)
            count_rc = _run_harness("findings_count_matrix.py", mut_dir)
            caught = base_rc == 2 or count_rc == 2
            if caught:
                who = "+".join(n for n, rc in (("baseline", base_rc), ("count", count_rc)) if rc == 2)
                verdict = f"red 검출 ✓({who})"
            elif deferred:
                verdict = "기대 red·실측 green(단계 후속 이행 대기 — 3단계 ordered oracle 후 red 전환)"
            else:
                verdict = "✗ 미검출(하네스 결함)"
                failed.append(name)
            rows.append(f"| {name}({desc}) | {base_rc} | {count_rc} | {verdict} |")
    print("\n".join(rows))
    if failed:
        print(f"self-test 실패: 필수 red 미검출 — {failed}")
        return 2
    print("self-test 통과: 필수 red 5종 검출(reorder=ordered 기본화·stdout-message-drift=재구성 대조 — M5)")
    return 0


def _usage() -> int:
    print("사용: checker_baseline_matrix.py [--emit <md 경로>] [--emit-expected] "
          "[--self-test] [--scripts-dir <dir>] [--fixtures-dir <dir>]", file=sys.stderr)
    return 1


def main(argv: "list[str]") -> int:
    emit: "Path | None" = None
    emit_expected = False
    run_self_test = False
    scripts_dir: Path = S
    fixtures_dir: Path = F
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--emit-expected":
            emit_expected = True
        elif a == "--self-test":
            run_self_test = True
        elif a in ("--emit", "--scripts-dir", "--fixtures-dir"):
            if len(argv) < i + 2:
                return _usage()
            val = argv[i + 1]
            i += 1
            if a == "--emit":
                emit = Path(val)
            elif a == "--scripts-dir":
                scripts_dir = Path(val).resolve()
            else:
                fixtures_dir = Path(val).resolve()
        else:
            return _usage()
        i += 1

    if run_self_test:
        return self_test()

    # 로스터↔기대표 키 집합 양방향 검사(적대 검증 레인 S 10번) — assert 가 아니라 런타임 검사다
    # (PYTHONOPTIMIZE=1 이면 assert 가 사라져 «전수 일치»로 세탁된다).
    roster = {script for script, _ in REGISTRY}
    if len(roster) != 27:
        print(f"재료 결손: REGISTRY 로스터 27종 가정 위반({len(roster)})", file=sys.stderr)
        return 1
    if not emit_expected:
        default_keys = {k for k in EXPECTED if "::" not in k}
        git_keys = {k for k in EXPECTED if "::" in k and k.split("::", 1)[1] in GIT_LANES}
        want_git = {f"{s}::{lane}" for s in GIT_AFFECTED for lane in GIT_LANES}
        guard_keys = {k for k in EXPECTED if k.endswith(f"::{GUARD_LANE}")}
        want_guard = {f"{s}::{GUARD_LANE}" for s, _fx, _a in GUARD_LANES}
        if guard_keys != want_guard:
            print(f"재료 결손: 가드 레인 키 불일치 — 선언만: {sorted(want_guard - guard_keys)} · "
                  f"기대표만: {sorted(guard_keys - want_guard)}", file=sys.stderr)
            return 1
        risk_keys = set(EXPECTED) - default_keys - git_keys - guard_keys
        want_risk = {f"{s}::{d}" for s, d, _a in RISK_LANES}
        if default_keys != roster:
            print(f"재료 결손: 로스터↔EXPECTED 키 불일치 — 로스터만: {sorted(roster - default_keys)} · "
                  f"기대표만: {sorted(default_keys - roster)}", file=sys.stderr)
            return 1
        if git_keys != want_git:
            print(f"재료 결손: git 레인 키 불일치 — 선언만: {sorted(want_git - git_keys)} · "
                  f"기대표만: {sorted(git_keys - want_git)}", file=sys.stderr)
            return 1
        if not risk_keys <= want_risk:
            print(f"재료 결손: 미선언 레인 키 — {sorted(risk_keys - want_risk)}", file=sys.stderr)
            return 1

    got, waiting = measure(scripts_dir, fixtures_dir)
    lane_of: "dict[str, str]" = {key: lane for key, _s, lane, _src in lane_plan(fixtures_dir)}

    if emit_expected:
        # 실패 상태를 «새 정답»으로 세탁하는 것을 막는다(적대 검증 레인 S 1번) — 단 거부는
        # 레인별 정당 exit 선언(lane_allowed_exits)을 따른다: red 픽스처는 exit 2 여야 하지만
        # git-clean 류 레인은 정당하게 exit 0 일 수 있다(S#6).
        bad = [k for k, (e, _p, _n, _u, _syn) in got.items()
               if e not in lane_allowed_exits(lane_of[k])]
        if bad:
            print(f"거부: 레인별 정당 exit 를 벗어난 검사기 — {sorted(bad)}. 개작 결함을 "
                  f"기대표로 세탁할 수 없다(사유와 함께 코드를 먼저 고쳐라)", file=sys.stderr)
            return 1
        print('EXPECTED: "dict[str, tuple[int, int, int, int, bool]]" = {')
        for key, _script, _lane, src in lane_plan(fixtures_dir):
            if src is None:
                continue
            e, p, n, u, syn = got[key]
            print(f'    "{key}": ({e}, {p}, {n}, {u}, {syn}),')
        print("}")
        for key in waiting:
            print(f"# 레인 대기(픽스처 병행 제작 — 실측 후 등재): {key}", file=sys.stderr)
        return 0

    lines: "list[str]" = [
        "| 키(검사기[::레인]) | exit | parsed_raw | norm_unique | unparsed | synthetic | 판정 |",
        "|---|---|---|---|---|---|---|",
    ]
    mismatch = 0
    for key, _script, _lane, src in lane_plan(fixtures_dir):
        if src is None:
            lines.append(f"| `{key}` | — | — | — | — | — | 레인 대기(픽스처 병행 제작 — 실패 아님) |")
            if key in EXPECTED:
                mismatch += 1
                lines[-1] = lines[-1].replace("실패 아님)", "실패 아님) ✗ 기대 존재·재료 부재")
            continue
        cur = got[key]
        e, p, n, u, syn = cur
        want = EXPECTED.get(key)
        ok = cur == want
        if not ok:
            mismatch += 1
        mark = "✓" if ok else f"✗ 기대 {want}"
        lines.append(f"| `{key}` | {e} | {p} | {n} | {u} | {'1건' if syn else '—'} | {mark} |")
    # 위험 레인 auto 사각 실증(관찰 라인 — 비게이트): auto 계열 3종은 기본 auto 호출로는
    # tree green 시 code 레인 미도달 exit 0 이 나온다 — 커스텀 argv 계측의 근거 기록.
    roster_auto: "dict[str, bool]" = dict(REGISTRY)
    for script, lane_dir, extra in RISK_LANES:
        if not extra or not roster_auto[script]:
            continue
        src = fixtures_dir / lane_dir / "bad_rules"
        if not src.is_dir():
            continue
        e_auto = _count_lane(script, roster_auto[script], src, DEFAULT_LANE, scripts_dir)[0]
        lines.append(f"| `{script}::{lane_dir}` (auto 기본 호출 관찰) | {e_auto} | — | — | — | — | "
                     f"code 레인 미도달 사각 실증(비게이트) |")
    summary = f"레인 {len(got)} · 일치 {len(got) - mismatch} · 불일치 {mismatch} · 대기 {len(waiting)}"
    table = "\n".join(lines)
    print(table)
    print(summary)
    if emit is not None:
        emit.write_text(
            "# T2 검사기 출력 기준선 — 27종 × 레인(red·git 3레인·위험 레인)\n\n"
            f"생성: {date.today().isoformat()} · `workspace/tools/checker_baseline_matrix.py --emit` 산출물"
            "(손으로 고치지 않는다 — 재실행으로 재생성).\n\n"
            "T2-1 개작(공용 findings 모듈 편입)의 anchor diff 기대 기준선 — 계수 정의·갱신 규율은 도구 docstring.\n\n"
            f"{table}\n\n{summary}\n",
            encoding="utf-8",
        )
        print(f"실측표 기록: {emit}")
    return 0 if mismatch == 0 else 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
