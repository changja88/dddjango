#!/usr/bin/env python3
"""pre-gate 픽스처 자가검증 러너 — green/red 미니 설계의 기대 판정을 고정한다.

무엇을 하나: `workspace/eval/fixtures/pregate/mini_repo/` 를 임시 git 저장소로
합성하고(커밋 1개), `design_pregate.py` 로 스펙을 돌린다. 리포트 파일은 **묶음별로 분리**해
`## pre-gate 예보` 헤더 계수 기대를 묶음별로 둔다(교차 오염 방지).

  묶음 base(리포트 1 — 헤더 4):
  green-spec.md  — 신규 BC 골격 전량·화이트리스트·5채널 전사가 오탐 0 임을 고정: exit 0.
  green2-spec.md — 스텁 충실도 4계열(수신자 표기·ABC 선언형·apps 정형 보충·Meta 합성)
                   이 오탐 0 임을 고정: exit 0.
  form-red-spec.md — 수신자 정규화 뒤에도 남는 중복 인자가 compile 격상으로 형식
                   red 가 됨을 고정: exit 3.
  red-spec.md   — 의도 위반 3건(#81 트리 밖 칸 · #267 2클래스 1파일 · #472 contract
                  pydantic import)이 «정확히 그 귀속»으로 나옴을 고정: exit 2 +
                  귀속 규칙 집합 일치 + 귀속 건수 일치.

  묶음 p1(수리 배치 2 Part 1 — 리포트 각 1):
  green3-spec.md — 사설 보조 타입 `_Item {…}`+메서드 행·Django 대입식 필드·마이그레이션
                   정형(`__init__` 빈 파일·`0001_` Migration 클래스)이 오탐 0: exit 0.
  red2-spec.md   — BC 직계 `migrations/` 오배치가 경로 기반 진탐(#81·#325)으로 남음을 고정
                   («표면 제외 금지» 증거): exit 2 + 귀속 규칙 집합·건수 일치.

  묶음 mid(E 계열 — 별도 합성 저장소·리포트 1 — 헤더 4): `midlane-spec.md` 로 재발화 판형을 고정.
  E1 계획 add 가 기준선 이후 커밋에 실존 + `--base <기준선>` → exit 0 · 사본의 그 파일은 스텁 · 기실현 0
  E2 계획 add 가 미커밋 WIP(의도 위반 실물) + `--base <기준선>` → exit 0 · «add(기실현» 1 · 사본은 스텁
  E3 E2 상태에서 `--base` 미지정 → exit 3(add 충돌 — 기본 경로 불변)
  E4 계획 add 가 기준선 트리에 실존 + `--base <기준선>` → exit 3(계획↔실물 모순 유지)

앞서 실행기 유닛 대조도 고정한다: 수신자 완전-일치 제거(`self_x` 무훼손)·`_snake` ↔ check-db-table
`_snake` 동치(드리프트 가드)·future import 단일 방출·파서 분류(`_`+대문자 = 클래스)·마이그레이션
정형 스텁의 `_check_migration_file` 직접 호출 Findings 0·블록 해시 결정성(`--block-hash` CLI 동치)·
버전 probe 동치(design_pregate ↔ registry_gate · Claude/Codex 레이아웃).

불일치면 exit 1(실행 출력 첨부). 검사기·트리 개정이 pre-gate 스텁 오탐을 새로 만들면
green 이 깨져 여기서 드러난다(설계 §9-3 드리프트 하네스의 픽스처 축).

사용: python3 workspace/tools/pregate_fixture_run.py [--keep]
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT: Path = Path(__file__).resolve().parents[2]
FIXTURES: Path = REPO_ROOT / "workspace" / "eval" / "fixtures" / "pregate"
EXECUTOR: Path = REPO_ROOT / "dddjango" / "scripts" / "design_pregate.py"
GATE: Path = REPO_ROOT / "dddjango" / "scripts" / "registry_gate.py"
CODEX_EXECUTOR: Path = REPO_ROOT / "codex-dddjango" / "skills" / "dddjango" / "scripts" / "design_pregate.py"
CLAUDE_MANIFEST: Path = REPO_ROOT / "dddjango" / ".claude-plugin" / "plugin.json"
CODEX_MANIFEST: Path = REPO_ROOT / "codex-dddjango" / ".codex-plugin" / "plugin.json"

# red-spec.md 의 의도 위반 — 규칙 집합·건수가 이와 다르면 회귀다.
EXPECTED_RED_RULES: "frozenset[str]" = frozenset({"#81", "#267", "#472"})
EXPECTED_RED_COUNT: int = 3
# red2-spec.md — BC 직계 migrations/ 오배치의 경로 기반 진탐(2026-09-03 실측 고정).
EXPECTED_RED2_RULES: "frozenset[str]" = frozenset({"#81", "#325"})
EXPECTED_RED2_COUNT: int = 2

MID_ADD: str = "application/orders/domain_layer/shared_value_object/lane_marker.py"
# E2 의 미커밋 실물 — 의도 위반(#267 2클래스 1파일)을 심어 «스텁 대체»가 실물 판정을 섞지 않음을 증명한다.
MID_REAL_SRC: str = ('class LaneMarker:\n    value: str\n\n\nclass LaneMarkerTwin:\n    value: str\n')

_FORECAST_RULE_RE: "re.Pattern[str]" = re.compile(r"^\s*`[0-9a-f]{12}` .*?\[#([\w-]+)\]", re.M)
_KEEP_RE: "re.Pattern[str]" = re.compile(r"\(--keep\) 격리 사본 보존: (\S+)")
_BLOCK_HASH_RE: "re.Pattern[str]" = re.compile(r"블록 해시 ([0-9a-f]{12})")


def _git(cwd: Path, *args: str) -> str:
    argv: "list[str]" = ["git", "-C", str(cwd), "-c", "core.hooksPath=",
                         "-c", "commit.gpgsign=false",
                         "-c", "user.email=fixture@local", "-c", "user.name=fixture"] + list(args)
    proc: "subprocess.CompletedProcess[str]" = subprocess.run(argv, capture_output=True, text=True)
    if proc.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} 실패: {proc.stderr.strip()}")
    return proc.stdout.strip()


def _run_pregate(spec: Path, repo: Path, report: Path,
                 extra: "list[str] | None" = None) -> "subprocess.CompletedProcess[str]":
    return subprocess.run(
        [sys.executable, str(EXECUTOR), str(spec), str(repo), "--report", str(report)] + (extra or []),
        capture_output=True, text=True)


def _load_module(path: Path, name: str):
    import importlib.util
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def _make_repo(scratch: Path, name: str) -> Path:
    repo: Path = scratch / name
    shutil.copytree(FIXTURES / "mini_repo", repo)
    _git(repo, "init", "-q")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "fixture-baseline")
    return repo


def _unit_checks() -> "list[str]":
    """실행기 유닛 대조 — 수신자 정규화 무훼손·_snake 검사기 동치·future 단일 방출·파서 분류·
    마이그레이션 정형·블록 해시·버전 probe."""
    out: "list[str]" = []
    dp = _load_module(EXECUTOR, "_pregate_exec")
    cases: "list[tuple[str, str]]" = [
        ("self, x: int", "x: int"), ("cls", ""), ("self", ""),
        ("self_x: int, y: int", "self_x: int, y: int"),  # 접두 유사 이름 무훼손
        ("*, a: int", "*, a: int"),
    ]
    for given, want in cases:
        got: str = dp._strip_receiver(given)
        if got != want:
            out.append(f"_strip_receiver({given!r}) = {got!r} ≠ 기대 {want!r}")
    ck = _load_module(REPO_ROOT / "dddjango" / "scripts" / "check-db-table.py", "_ck_db_table")
    for name in ("HTTPLog", "OAuth2Token", "MediaAsset", "S3Asset", "APNs", "A"):
        if dp._snake(name) != ck._snake(name):
            out.append(f"_snake({name!r}) 실행기 {dp._snake(name)!r} ≠ 검사기 {ck._snake(name)!r} — 유도 드리프트")
    entry = dp.PlanEntry(path="application/x/driven_layer/django_x/models/x_model.py", tag="add")
    entry.imports.append("from __future__ import annotations")
    stub: str = dp.render_stub(entry)
    if stub.count("from __future__") != 1:
        out.append(f"future import 방출 {stub.count('from __future__')}회 ≠ 1 — 전사 재방출 필터 회귀")

    # ④′ 파서 분류 — `_`+대문자 = 클래스 · 소문자/`_`+소문자 = 함수 · bare 필드 red.
    def parse(rest: str) -> "tuple[object, list[str]]":
        errs: "list[str]" = []
        return dp._parse_symbol_rest(rest, errs, "unit"), errs

    sym, errs = parse("_Item {a: int}")
    if errs or not isinstance(sym, dp.Symbol) or sym.kind != "class" or sym.fields != ["a: int"]:
        out.append(f"파서: `_Item {{a: int}}` → 클래스+필드 기대 ≠ {sym!r} {errs}")
    sym, errs = parse("_Item(Base)")
    if errs or not isinstance(sym, dp.Symbol) or sym.kind != "class" or sym.base != "Base":
        out.append(f"파서: `_Item(Base)` → base 있는 클래스 기대 ≠ {sym!r} {errs}")
    sym, errs = parse("_Item.method(self, x: int)")
    if errs or not isinstance(sym, dp.Method) or sym.params != "x: int":
        out.append(f"파서: `_Item.method(self, x: int)` → params `x: int` 기대 ≠ {sym!r} {errs}")
    sym, errs = parse("_helper {a: int}")
    if sym is not None or not errs or "함수에 필드" not in errs[0]:
        out.append(f"파서: `_helper {{a: int}}` → 형식 red 유지 기대 ≠ {sym!r} {errs}")
    sym, errs = parse("_helper(x: int)")
    if errs or not isinstance(sym, dp.Symbol) or sym.kind != "function" or sym.params != "x: int":
        out.append(f"파서: `_helper(x: int)` → 함수 기대 ≠ {sym!r} {errs}")
    sym, errs = parse("M(Model) {kind = models.CharField(max_length=32)}")
    if errs or not isinstance(sym, dp.Symbol) or sym.fields != ["kind = models.CharField(max_length=32)"]:
        out.append(f"파서: 대입식 필드 → 필드 OK 기대 ≠ {sym!r} {errs}")
    sym, errs = parse("M(Model) {kind}")
    if not errs or "`name = <식>`" not in errs[0]:
        out.append(f"파서: bare 필드 `kind` → 메시지에 «`name = <식>`» 기대 ≠ {errs}")
    hint_entry = dp.PlanEntry(path="application/x/domain_layer/x.py", tag="add")
    hint_entry.symbols.append(dp.Symbol(name="_Helper", base="x: int"))
    try:
        compile(dp.render_stub(hint_entry), "unit", "exec")
        out.append("compile 힌트: `_Helper(x: int)` 스텁이 compile 을 통과했다 — 형식 red 경로 회귀")
    except SyntaxError:
        if "소문자 선두" not in dp._compile_hint(hint_entry):
            out.append("compile 힌트: `_Helper(x: int)` 에 «사설 함수는 소문자 선두» 힌트 부재")

    # ⑤ 마이그레이션 정형 — `__init__` 빈 파일 · `0001_` Migration 클래스 1 + initial · 검사기 직접 호출 Findings 0.
    mig_root: str = "application/x/driven_layer/django_x/migrations/"
    init_stub: str = dp.render_stub(dp.PlanEntry(path=mig_root + "__init__.py", tag="add"))
    if init_stub != "":
        out.append(f"마이그레이션 `__init__.py` 스텁이 빈 파일이 아니다: {init_stub!r}")
    first: str = dp.render_stub(dp.PlanEntry(path=mig_root + "0001_initial.py", tag="add"))
    second: str = dp.render_stub(dp.PlanEntry(path=mig_root + "0002_more.py", tag="add"))
    for label, text, want_initial in (("0001_initial", first, True), ("0002_more", second, False)):
        try:
            compile(text, label, "exec")
        except SyntaxError as exc:
            out.append(f"마이그레이션 정형 {label} compile 실패: {exc}")
        if "class Migration(migrations.Migration):" not in text:
            out.append(f"마이그레이션 정형 {label} 에 `class Migration(migrations.Migration)` 부재")
        if ("initial = True" in text) != want_initial:
            out.append(f"마이그레이션 정형 {label}: `initial = True` 존재 {('initial = True' in text)} ≠ 기대 {want_initial}")
    transcribed = dp.PlanEntry(path=mig_root + "0003_hand.py", tag="add")
    transcribed.symbols.append(dp.Symbol(name="Migration", base="migrations.Migration",
                                         fields=["dependencies = []", "operations = []"]))
    if "계획 스텁" not in dp.render_stub(transcribed):
        out.append("마이그레이션 전사 우선 회귀: symbols 전사가 있는데 정형으로 덮였다")
    sys.path.insert(0, str(EXECUTOR.parent))
    import findings  # noqa: E402  — 검사기 Findings 컨테이너(직접 호출용)
    mo = _load_module(REPO_ROOT / "dddjango" / "scripts" / "check-mechanism-ownership.py", "_ck_mech_own")
    with tempfile.TemporaryDirectory() as td:
        for rel, text in ((mig_root + "__init__.py", init_stub), (mig_root + "0001_initial.py", first),
                          (mig_root + "0002_more.py", second)):
            f: Path = Path(td) / rel
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text(text, encoding="utf-8")
            found = findings.Findings("check-mechanism-ownership.py", defer=True)
            mo._check_migration_file(f, Path(rel), found)
            if list(found):
                out.append(f"마이그레이션 정형 {rel} 검사기 직접 호출 Findings ≠ 0: {list(found)}")

    # ⑧ 블록 해시 — 결정성·산문 불변·블록 변경 감지·CLI(`--block-hash`) 동치.
    spec_text: str = (FIXTURES / "green2-spec.md").read_text(encoding="utf-8")
    h1: str = dp.block_hash(spec_text)
    if h1 != dp.block_hash(spec_text) or not re.fullmatch(r"[0-9a-f]{12}", h1):
        out.append(f"블록 해시 비결정 또는 형식 위반: {h1!r}")
    if dp.block_hash(spec_text + "\n산문만 추가한 문장.\n") != h1:
        out.append("블록 해시가 산문 변경에 반응했다(기계 블록만 입력이어야 한다)")
    if dp.block_hash(spec_text.replace("HTTPLogModel(Model)", "HTTPLogModel(Model) {x: int}")) == h1:
        out.append("블록 해시가 symbols 블록 변경을 감지하지 못했다")
    if dp.block_hash(spec_text.replace("| (이번 슬라이스 없음) |", "| 바뀐 후보 |")) == h1:
        out.append("블록 해시가 영구 테스트 입장 표 변경을 감지하지 못했다")
    cli = subprocess.run([sys.executable, str(EXECUTOR), str(FIXTURES / "green2-spec.md"), ".", "--block-hash"],
                         capture_output=True, text=True)
    if cli.returncode != 0 or cli.stdout.strip() != f"블록 해시 {h1}":
        out.append(f"`--block-hash` CLI 출력 {cli.stdout.strip()!r}(exit {cli.returncode}) ≠ `블록 해시 {h1}`")

    # ③ 버전 probe 동치 — 두 스크립트 각자 보유 · Claude/Codex 레이아웃 2경로 · manifest 값과 일치.
    rg = _load_module(GATE, "_registry_gate_mod")
    claude_v: str = json.loads(CLAUDE_MANIFEST.read_text(encoding="utf-8"))["version"]
    codex_v: str = json.loads(CODEX_MANIFEST.read_text(encoding="utf-8"))["version"]
    if dp.plugin_version() != claude_v:
        out.append(f"design_pregate.plugin_version() {dp.plugin_version()!r} ≠ Claude manifest {claude_v!r}")
    if rg.plugin_version() != dp.plugin_version():
        out.append(f"버전 probe 불일치: registry_gate {rg.plugin_version()!r} ≠ design_pregate {dp.plugin_version()!r}")
    if CODEX_EXECUTOR.is_file():
        dp_codex = _load_module(CODEX_EXECUTOR, "_pregate_exec_codex")
        if dp_codex.plugin_version() != codex_v:
            out.append(f"Codex 레이아웃 probe {dp_codex.plugin_version()!r} ≠ Codex manifest {codex_v!r}")
    toolchain: str = rg._toolchain_line()
    if not re.search(r"^툴체인: dddjango v\S+ · py\d+\.\d+ · 실행 트리 digest [0-9a-f]{16}\(\d+파일\) · 경로 ", toolchain):
        out.append(f"registry_gate 툴체인 행 형식 위반: {toolchain!r}")
    return out


def _dump(label: str, proc: "subprocess.CompletedProcess[str]") -> None:
    print(f"---- {label} stdout ----")
    print(proc.stdout)
    if proc.stderr.strip():
        print(f"---- {label} stderr ----")
        print(proc.stderr)


def _header_count(report: Path) -> int:
    return report.read_text(encoding="utf-8").count("## pre-gate 예보") if report.is_file() else 0


def _kept_copy_is_stub(proc: "subprocess.CompletedProcess[str]", rel: str) -> "bool | None":
    """`--keep` 사본에서 계획 경로가 스텁으로 실체화됐는지(실물이 아니라) 본다 — 사본은 검사 후 지운다."""
    m = _KEEP_RE.search(proc.stdout)
    if m is None:
        return None
    scratch: Path = Path(m.group(1))
    target: Path = scratch / "copy" / rel
    try:
        return target.is_file() and "계획 스텁" in target.read_text(encoding="utf-8")
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


def _run_base_bundle(scratch: Path, failures: "list[str]") -> None:
    repo: Path = _make_repo(scratch, "repo")
    report: Path = scratch / "pregate-report.md"
    for label in ("green-spec", "green2-spec"):
        green: "subprocess.CompletedProcess[str]" = _run_pregate(FIXTURES / f"{label}.md", repo, report)
        if green.returncode != 0:
            failures.append(f"{label} 기대 exit 0 ≠ 실측 {green.returncode}")
            _dump(label, green)
        else:
            print(f"{label}: exit 0 (예보 0) — 기대 일치")

    form_red: "subprocess.CompletedProcess[str]" = _run_pregate(FIXTURES / "form-red-spec.md", repo, report)
    if form_red.returncode != 3:
        failures.append(f"form-red-spec 기대 exit 3(형식 red) ≠ 실측 {form_red.returncode}")
        _dump("form-red", form_red)
    else:
        print("form-red-spec: exit 3 (중복 인자 → compile 형식 red) — 기대 일치")

    red: "subprocess.CompletedProcess[str]" = _run_pregate(FIXTURES / "red-spec.md", repo, report)
    rules: "list[str]" = [f"#{r}" for r in _FORECAST_RULE_RE.findall(red.stdout)]
    if red.returncode != 2:
        failures.append(f"red-spec 기대 exit 2 ≠ 실측 {red.returncode}")
    if set(rules) != EXPECTED_RED_RULES:
        failures.append(f"red-spec 귀속 규칙 집합 {sorted(set(rules))} ≠ 기대 {sorted(EXPECTED_RED_RULES)}")
    if len(rules) != EXPECTED_RED_COUNT:
        failures.append(f"red-spec 귀속 건수 {len(rules)} ≠ 기대 {EXPECTED_RED_COUNT}")
    if any(f.startswith("red-spec") for f in failures):
        _dump("red", red)
    else:
        print(f"red-spec: exit 2 · 귀속 {sorted(rules)} — 기대 일치")

    if _header_count(report) != 4:
        failures.append(f"[base] 리포트 append 횟수 {_header_count(report)} ≠ 기대 4 ({report})")


def _run_p1_bundle(scratch: Path, failures: "list[str]") -> None:
    repo: Path = _make_repo(scratch, "repo-p1")
    report_g: Path = scratch / "pregate-report-green3.md"
    green3: "subprocess.CompletedProcess[str]" = _run_pregate(FIXTURES / "green3-spec.md", repo, report_g)
    if green3.returncode != 0:
        failures.append(f"green3-spec 기대 exit 0 ≠ 실측 {green3.returncode}")
        _dump("green3", green3)
    else:
        print("green3-spec: exit 0 (사설 타입·대입식 필드·마이그레이션 정형 예보 0) — 기대 일치")
    if _header_count(report_g) != 1:
        failures.append(f"[p1 green3] 리포트 append 횟수 {_header_count(report_g)} ≠ 기대 1")
    if not _BLOCK_HASH_RE.search(report_g.read_text(encoding="utf-8") if report_g.is_file() else ""):
        failures.append("[p1 green3] 리포트 헤더에 `블록 해시 <값>` 스탬프 부재")

    report_r: Path = scratch / "pregate-report-red2.md"
    red2: "subprocess.CompletedProcess[str]" = _run_pregate(FIXTURES / "red2-spec.md", repo, report_r)
    rules2: "list[str]" = [f"#{r}" for r in _FORECAST_RULE_RE.findall(red2.stdout)]
    bad_before: int = len(failures)
    if red2.returncode != 2:
        failures.append(f"red2-spec 기대 exit 2 ≠ 실측 {red2.returncode}")
    if set(rules2) != EXPECTED_RED2_RULES:
        failures.append(f"red2-spec 귀속 규칙 집합 {sorted(set(rules2))} ≠ 기대 {sorted(EXPECTED_RED2_RULES)}")
    if len(rules2) != EXPECTED_RED2_COUNT:
        failures.append(f"red2-spec 귀속 건수 {len(rules2)} ≠ 기대 {EXPECTED_RED2_COUNT}")
    if len(failures) > bad_before:
        _dump("red2", red2)
    else:
        print(f"red2-spec: exit 2 · 귀속 {sorted(rules2)} (마이그레이션 오배치 경로 진탐) — 기대 일치")
    if _header_count(report_r) != 1:
        failures.append(f"[p1 red2] 리포트 append 횟수 {_header_count(report_r)} ≠ 기대 1")


def _run_mid_bundle(scratch: Path, failures: "list[str]") -> None:
    spec: Path = FIXTURES / "midlane-spec.md"
    report: Path = scratch / "pregate-report-mid.md"

    # E1 — 기준선 이후 커밋에 계획 add 실존 → `--base <기준선>` → 사본에는 없어 스텁 · 기실현 0.
    repo: Path = _make_repo(scratch, "repo-mid-e1")
    base: str = _git(repo, "rev-parse", "HEAD")
    (repo / MID_ADD).write_text("class LaneMarker:\n    value: str\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "slice: lane marker")
    e1 = _run_pregate(spec, repo, report, ["--base", base, "--keep"])
    stub_e1: "bool | None" = _kept_copy_is_stub(e1, MID_ADD)
    built_e1: int = _header_count(report) and report.read_text(encoding="utf-8").count("already-built: add(기실현")
    if e1.returncode != 0 or "already-built 0건" not in e1.stdout or built_e1 != 0 or stub_e1 is not True:
        failures.append(f"E1 기대 exit 0·기실현 0·사본 스텁 ≠ 실측 exit {e1.returncode} · "
                        f"기실현 {built_e1} · 스텁 {stub_e1}")
        _dump("E1", e1)
    else:
        print("E1: exit 0 · 사본 스텁 · 기실현 0 (커밋된 add 는 사본 밖) — 기대 일치")

    # E2 — 미커밋 WIP(의도 위반 실물) → `--base <기준선>` → 기실현 1 · 스텁 대체(실물 판정 혼입 0).
    repo = _make_repo(scratch, "repo-mid-e2")
    base = _git(repo, "rev-parse", "HEAD")
    (repo / MID_ADD).write_text(MID_REAL_SRC, encoding="utf-8")
    e2 = _run_pregate(spec, repo, report, ["--base", base, "--keep"])
    stub_e2: "bool | None" = _kept_copy_is_stub(e2, MID_ADD)
    built_e2: int = report.read_text(encoding="utf-8").count("already-built: add(기실현") - built_e1
    if e2.returncode != 0 or "already-built 1건" not in e2.stdout or built_e2 != 1 or stub_e2 is not True:
        failures.append(f"E2 기대 exit 0·기실현 1·사본 스텁 ≠ 실측 exit {e2.returncode} · "
                        f"기실현 {built_e2} · 스텁 {stub_e2}")
        _dump("E2", e2)
    else:
        print("E2: exit 0 · 기실현 1 · 스텁 대체(실물 #267 미혼입) — 기대 일치")

    # E3 — E2 상태에서 `--base` 미지정 → 기본 경로 불변(add 충돌 형식 red).
    e3 = _run_pregate(spec, repo, report)
    if e3.returncode != 3 or "add 충돌(실존)" not in e3.stdout:
        failures.append(f"E3 기대 exit 3(add 충돌) ≠ 실측 {e3.returncode}")
        _dump("E3", e3)
    else:
        print("E3: exit 3 (미지정 `--base` — add 충돌 유지) — 기대 일치")

    # E4 — 계획 add 가 기준선 트리에 실존 → `--base` 명시해도 형식 red 유지.
    repo = _make_repo(scratch, "repo-mid-e4")
    (repo / MID_ADD).write_text("class LaneMarker:\n    value: str\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "baseline already has lane marker")
    base = _git(repo, "rev-parse", "HEAD")
    (repo / "docs_note.md").write_text("harmless\n", encoding="utf-8")  # 공허 방지용 무해 dirty
    e4 = _run_pregate(spec, repo, report, ["--base", base])
    if e4.returncode != 3 or "add 충돌(실존)" not in e4.stdout:
        failures.append(f"E4 기대 exit 3(기준선 실존 add) ≠ 실측 {e4.returncode}")
        _dump("E4", e4)
    else:
        print("E4: exit 3 (기준선 트리 실존 add — 계획↔실물 모순 유지) — 기대 일치")

    if _header_count(report) != 4:
        failures.append(f"[mid] 리포트 append 횟수 {_header_count(report)} ≠ 기대 4 ({report})")


def main(argv: "list[str]") -> int:
    ap: argparse.ArgumentParser = argparse.ArgumentParser(description="pre-gate 픽스처 러너")
    ap.add_argument("--keep", action="store_true", help="합성 저장소 보존(디버그)")
    ns: argparse.Namespace = ap.parse_args(argv)

    scratch: Path = Path(tempfile.mkdtemp(prefix="pregate-fixture-"))
    failures: "list[str]" = []
    failures.extend(_unit_checks())
    try:
        _run_base_bundle(scratch, failures)
        _run_p1_bundle(scratch, failures)
        _run_mid_bundle(scratch, failures)

        if failures:
            print("\nFAIL — pre-gate 픽스처 기대 불일치:")
            for f in failures:
                print(f"  - {f}")
            return 1
        print("\nPASS — pre-gate 픽스처 6종+E 계열 4단계+유닛 기대 일치 "
              "(green×3 예보 0 · 형식 red exit 3 · red 귀속 3건·red2 귀속 2건 정합 · 재발화 판형 E1~E4)")
        return 0
    finally:
        if ns.keep:
            print(f"(--keep) 합성 저장소 보존: {scratch}")
        else:
            shutil.rmtree(scratch, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
