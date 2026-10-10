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

  묶음 mid(E 계열 — 별도 합성 저장소·리포트 1 — 헤더 6): `midlane-spec.md`·`midlane-red-spec.md` 로 재발화 판형을 고정.
  E1 계획 add 가 기준선 이후 커밋에 실존 + `--base <기준선>` → exit 0 · 사본의 그 파일은 스텁 · 기실현 0
  E2 계획 add 가 미커밋 WIP(의도 위반 실물) + `--base <기준선>` → exit 0 · «add(기실현» 1 · 사본은 스텁 ·
     **해소(L∖N) 0 ∧ check-domain-model anchor 열 0**(실물이 앵커 스냅숏에 안 실렸다는 증거)
  E1′/E2′ red 변형(`midlane-red-spec.md` — 스텁 자체가 #267): 커밋 실물 / 동내용 미커밋 WIP → **둘 다 exit 2 · 같은
     안정 ID · E2′ 해소 0·anchor 열 0**(5단계 리뷰 MAJOR A — 기실현 add 앵커 오염 회귀 가드)
  E3 E2 상태에서 `--base` 미지정 → exit 3(add 충돌 — 기본 경로 불변)
  E4 계획 add 가 기준선 트리에 실존 + `--base <기준선>` → exit 3(계획↔실물 모순 유지)

  묶음 imports(수리 배치 2 Part 3 — 계약 실존 3단 · 합성 저장소 2 = `mini_repo` + `imports_overlay/` · 리포트 각 1):
  imports-green-spec.md       — 실존 확인 `FrozenClock`·서브모듈 형·자기 add 해소·서드파티(update 소비자)·**update 대상 새 심볼
                                `TickingClock`(자기 update 해소 S′)** → 결손 0 · exit 0.
  imports-red-spec.md         — ⑴ 모듈 부재·⑵ 0B 자리표시자·⑶ 심볼 미정의 각 1 · registry 귀속 0 → **exit 5**(권고·비차단).
  imports-update-only-spec.md — file-plan `update` 뿐(실체화 0) + ⑵ 결손 1 → exit 5 + «실체화 0 · 실존 결손 1건»(kkebi S2 판형).
  묶음 enforce(차단 모드 승격 2026-09-03 — 별도 리포트 1 — 헤더 7):
  noblock-spec.md        — machine 마커 0(구형 명세 판형) → 형식 red(블록 부재) exit 3(관찰 모드의 exit 4 skip 폐지).
  empty-block-spec.md    — 마커 + 주석뿐인 펜스(file-plan 0행) → 형식 red(블록 공허) exit 3(빈 펜스 도피 봉쇄).
  update-target-spec.md  — `update` 1행을 저장소 상태 셋으로: ⓐ 기준선 부재 → exit 3 «update 대상 부재»(재라벨 도피 봉쇄) ·
                           ⓑ 기준선에 유효 승격 형태(`promo/__init__.py`+`promo/promo.py`) 커밋 → 예외 통과·실체화 0 → exit 4 ·
                           ⓒ 승격 폴더 미커밋(오버레이만) → exit 3(오버레이 불인정).
  remove-target-spec.md  — 비후행 `remove` 기준선 부재 → exit 3 «remove 대상 부재» · 짝 remove-deferred-spec.md(`remove@L1`) → exit 4.
  empty-conflict-spec.md — `empty` 가 기준선 실존 파일을 가리킴 → exit 3 «empty 충돌»(empty 재라벨 도피 봉쇄 — 6단계 감사).
  묶음 checkreport(`--check-report` — 전용 저장소·리포트): red-spec 실행 뒤 처분 행 append 를 단계별로 대조 —
  미라벨 3 → ignored 2 append 3(미기재 1) → corrected 3 → filtered 0 → 오염 행(무값 «블록 해시 갱신») 0 → 다른 명세 3(stale) ·
  형식 red 리포트 3 · 블록 부재 리포트 3 · skip·결손 리포트 0 · 해시 토큰 없는 구판 헤더 3 · 표 형식 처분(백틱 라벨) 3 · 리포트 부재 1.
  묶음 stub(스텁 머리 — 합성 저장소 = `mini_repo` + `stub_overlay/`(포트 · #488 고정 칸) · 리포트 1 — 헤더 10):
  `stub-adapter-init-*-spec.md` 10 — 재수출만 하는 어댑터 패키지 `__init__.py`(맨 · `./` · 겹친 `/` 경로) · `empty` → exit 0 ·
  전사 future 명시 · 클래스 · 별칭(타입 없음은 #493 함께) · TYPE_CHECKING 별칭 쌍 · exception-map 창구 → #640 1건(진탐) ·
  `__init__.py` 스텁 원문(--keep 사본) 대조 3. 그리고 재료 파일 스텁 글 대조 10칸(`stub-material-*-spec.md` 9 ·
  `render_stub` 직접 — 검사기 무관): 본문 = docstring + `return settings.PREGATE_STUB` · plain settings 결속 한 번(보충 ·
  괄호 · 공백 원문) · 별칭 · 함수 없는 꼴 보충 0 · `./` · 겹친 `/` = 맨 경로 글 · 재료 자리 밖 둘은 `raise NotImplementedError`.
  묶음 stub-material(D17 소유 · #652 — 합성 저장소 = `mini_repo` + `stub_overlay/` + `stub_material_overlay/`(값 객체) · 리포트 1 — 헤더 7):
  재료 명세 7(P1 · P1′ · P1″a · P1″b · P1-dot · P1-dslash → exit 0 · P2 `-> dict` → #652 «반환 주석» 1건(진탐)) — 검사기 결과 단언.
  실행기 exit 규약: 0 green · 2 귀속 red(결손 병기) · 3 형식 red(문법 · 블록 부재·공허 · add 충돌 · update/remove 대상 기준선 부재) ·
  4 skip(실체화 0·결손 0) · 5 결손 ≥1 ∧ (귀속 0 ∨ 실체화 0) · 1 실행 불능 · `--check-report`: 0 정합 · 3 불비 · 1 리포트/절 부재.
  (아래 재발화 판형의 케이스 이름 E1~E4 는 이 러너의 것 — 승격 계획서의 실행기 변경 항목 번호와 무관.)

앞서 실행기 유닛 대조도 고정한다: 수신자 완전-일치 제거(`self_x` 무훼손)·`_snake` ↔ check-db-table
`_snake` 동치(드리프트 가드)·future import 단일 방출·파서 분류(`_`+대문자 = 클래스)·마이그레이션
정형 스텁의 `_check_migration_file` 직접 호출 Findings 0·블록 해시 결정성(`--block-hash` CLI 동치)·
버전 probe 동치(design_pregate ↔ registry_gate · Claude/Codex 레이아웃)·**계약 실존 유닛 매트릭스 ⓐ~ⓟ**
(합성 사본 + 합성 Plan · 검사기 27종 비의존: 실존 확인·⑶ 미정의·⑵ 0B/docstring-only·⑴ 부재·자기 add ⑶ 생략·자기
`empty` ⑵·승격 폴더 `__init__` 재수출·서브모듈 형·서드파티 X·`framework.*` 부재 ⑴·`import a.b.c`·상대 import·
`import *` U·planned-remove ⑴/`remove@Ln` 실존·ID 안정성 + TypeAlias·AsyncFunctionDef·승격 폴더 부품 S·empty 모듈
import ⑵ 비적용·namespace-dir 이름 U·`import *` 재수출/`__getattr__` U·빈 패키지 `__init__` ⑵ 비적용·계수 항등식 +
**update 대상**(선언 이름 S′·현재 표면 K·미선언 U·0B 대상 ⑵ 비적용·**사본 부재 대상은 ⑴ 유지**)·세미콜론 복합행 전 문 판정·T 이름 단위).

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
import types
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
# 계약 실존 결손 항목 — 접두 `e-` 라 예보 ID 정규식과 절대 겹치지 않는다(채널 분리의 기계 표현). stdout(들여쓰기)·
# 리포트(`- ` 불릿) 양쪽 문면을 같은 식으로 센다.
_EXISTENCE_LINE_RE: "re.Pattern[str]" = re.compile(r"^\s*(?:- )?`e-[0-9a-f]{12}` ([⑴⑵⑶]) ", re.M)
_EXISTENCE_AGG_RE: "re.Pattern[str]" = re.compile(
    r"집계: 행 (\d+) · 이름 판정 (\d+) · 실존 확인 (\d+) · 자기 add 해소 (\d+) · 자기 update 해소 (\d+) · "
    r"저장소 밖\(검사 밖\) (\d+) · 판정 불능 (\d+) · 결손 (\d+)")
_RESOLVED_RE: "re.Pattern[str]" = re.compile(r"해소\(L∖N\) (\d+)건")
_DOMAIN_MODEL_ROW_RE: "re.Pattern[str]" = re.compile(r"\| `check-domain-model\.py` \| (\d+) \| (\d+) \|")
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


def _load_module(path: Path, name: str) -> "types.ModuleType":
    import importlib.util
    spec: "importlib.machinery.ModuleSpec | None" = importlib.util.spec_from_file_location(name, path)
    mod: "types.ModuleType" = importlib.util.module_from_spec(spec)
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
    dp: "types.ModuleType" = _load_module(EXECUTOR, "_pregate_exec")
    cases: "list[tuple[str, str]]" = [
        ("self, x: int", "x: int"), ("cls", ""), ("self", ""),
        ("self_x: int, y: int", "self_x: int, y: int"),  # 접두 유사 이름 무훼손
        ("*, a: int", "*, a: int"),
    ]
    for given, want in cases:
        got: str = dp._strip_receiver(given)
        if got != want:
            out.append(f"_strip_receiver({given!r}) = {got!r} ≠ 기대 {want!r}")
    ck: "types.ModuleType" = _load_module(REPO_ROOT / "dddjango" / "scripts" / "check-db-table.py", "_ck_db_table")
    for name in ("HTTPLog", "OAuth2Token", "MediaAsset", "S3Asset", "APNs", "A"):
        if dp._snake(name) != ck._snake(name):
            out.append(f"_snake({name!r}) 실행기 {dp._snake(name)!r} ≠ 검사기 {ck._snake(name)!r} — 유도 드리프트")
    entry: "dp.PlanEntry" = dp.PlanEntry(path="application/x/driven_layer/django_x/models/x_model.py", tag="add")
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
    hint_entry: "dp.PlanEntry" = dp.PlanEntry(path="application/x/domain_layer/x.py", tag="add")
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
    transcribed: "dp.PlanEntry" = dp.PlanEntry(path=mig_root + "0003_hand.py", tag="add")
    transcribed.symbols.append(dp.Symbol(name="Migration", base="migrations.Migration",
                                         fields=["dependencies = []", "operations = []"]))
    if "계획 스텁" not in dp.render_stub(transcribed):
        out.append("마이그레이션 전사 우선 회귀: symbols 전사가 있는데 정형으로 덮였다")
    sys.path.insert(0, str(EXECUTOR.parent))
    import findings  # noqa: E402  — 검사기 Findings 컨테이너(직접 호출용)
    mo: "types.ModuleType" = _load_module(REPO_ROOT / "dddjango" / "scripts" / "check-mechanism-ownership.py", "_ck_mech_own")
    with tempfile.TemporaryDirectory() as td:
        for rel, text in ((mig_root + "__init__.py", init_stub), (mig_root + "0001_initial.py", first),
                          (mig_root + "0002_more.py", second)):
            f: Path = Path(td) / rel
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text(text, encoding="utf-8")
            found: "findings.Findings" = findings.Findings("check-mechanism-ownership.py", defer=True)
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
    cli: "subprocess.CompletedProcess[str]" = subprocess.run(
        [sys.executable, str(EXECUTOR), str(FIXTURES / "green2-spec.md"), ".", "--block-hash"],
                         capture_output=True, text=True)
    # 2026-09-27 로드맵 3 S-4: 둘째 행에 실행 트리 digest(캐시 skip 이 툴체인 교체도 대조) — 첫 행은 종전 그대로
    cli_lines: "list[str]" = cli.stdout.strip().splitlines()
    if (cli.returncode != 0 or len(cli_lines) != 2 or cli_lines[0] != f"블록 해시 {h1}"
            or re.fullmatch(r"실행 트리 digest [0-9a-f]{16}", cli_lines[1]) is None):
        out.append(f"`--block-hash` CLI 출력 {cli.stdout.strip()!r}(exit {cli.returncode}) ≠ "
                   f"`블록 해시 {h1}` + `실행 트리 digest <16hex>`")

    # ③ 버전 probe 동치 — 두 스크립트 각자 보유 · Claude/Codex 레이아웃 2경로 · manifest 값과 일치.
    rg: "types.ModuleType" = _load_module(GATE, "_registry_gate_mod")
    claude_v: str = json.loads(CLAUDE_MANIFEST.read_text(encoding="utf-8"))["version"]
    codex_v: str = json.loads(CODEX_MANIFEST.read_text(encoding="utf-8"))["version"]
    if dp.plugin_version() != claude_v:
        out.append(f"design_pregate.plugin_version() {dp.plugin_version()!r} ≠ Claude manifest {claude_v!r}")
    if rg.plugin_version() != dp.plugin_version():
        out.append(f"버전 probe 불일치: registry_gate {rg.plugin_version()!r} ≠ design_pregate {dp.plugin_version()!r}")
    if CODEX_EXECUTOR.is_file():
        dp_codex: "types.ModuleType" = _load_module(CODEX_EXECUTOR, "_pregate_exec_codex")
        if dp_codex.plugin_version() != codex_v:
            out.append(f"Codex 레이아웃 probe {dp_codex.plugin_version()!r} ≠ Codex manifest {codex_v!r}")
    toolchain: str = rg._toolchain_line()
    if not re.search(r"^툴체인: dddjango v\S+ · py\d+\.\d+ · 실행 트리 digest [0-9a-f]{16}\(\d+파일\) · 경로 ", toolchain):
        out.append(f"registry_gate 툴체인 행 형식 위반: {toolchain!r}")
    return out


def _existence_unit_checks() -> "list[str]":
    """계약 실존 유닛 매트릭스 ⓐ~ⓟ + 델타(TypeAlias·AsyncFunctionDef·승격 폴더 부품·empty 모듈 import·namespace-dir·
    `import *` 재수출) — 합성 사본 디렉터리 + 합성 Plan 으로 `check_import_existence` 를 직접 부른다(git·검사기 비의존)."""
    out: "list[str]" = []
    dp: "types.ModuleType" = _load_module(EXECUTOR, "_pregate_exec_existence")
    if dp._repo_root_packages() != frozenset({"application", "framework"}):
        out.append(f"_repo_root_packages() = {sorted(dp._repo_root_packages())} ≠ {{application, framework}}")
    with tempfile.TemporaryDirectory() as td:
        copy: Path = Path(td)
        dl: str = "application/shop/domain_layer/"
        files: "dict[str, str]" = {
            "application/__init__.py": "", "application/shop/__init__.py": "", dl + "__init__.py": "",
            dl + "sku.py": "class Sku:\n    pass\n",
            dl + "empty0.py": "",
            dl + "doc_only.py": '"""only doc."""\n',
            dl + "promo/__init__.py": "from .promo import Promo as Promo\n__all__ = [\"Promo\"]\n",
            dl + "promo/promo.py": "class Promo: ...\n",
            dl + "promo/part.py": "class Part: ...\n",
            dl + "star.py": "from .sku import *\n",
            dl + "dyn.py": "def __getattr__(name): ...\n",
            dl + "nsdir/leaf.py": "X = 1\n",
            dl + "stay.py": "class Stay: ...\n",
            dl + "upd.py": "class Existing: ...\n",   # update 대상 — 현재 표면 {Existing} · symbols 선언 {NewName}
            dl + "upd0.py": "",                        # 0B update 대상 — ⑵ 비적용 · 선언 {Planned}
            dl + "modern.py": ("async def fetch(): ...\na, (b, c) = 1, (2, 3)\nd: int = 4\nimport os.path\nimport json as js\n"
                              "if True:\n    from os import sep\ntry:\n    import nothing\nexcept ImportError:\n    nothing = None\n"
                              "with open(__file__) as fh:\n    W = 1\n__all__ = [\"listed\"]\n"),
        }
        if sys.version_info >= (3, 12):
            files[dl + "modern.py"] = "type Alias = int\n" + files[dl + "modern.py"]
        for rel, text in files.items():
            f: Path = copy / rel
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text(text, encoding="utf-8")
        plan: "dp.Plan" = dp.Plan()
        for tag, rel in (("add", dl + "new_vo.py"), ("add", "application/shop/application_layer/uc/do_uc/do_uc_use_case.py"),
                         ("empty", dl + "blank.py"), ("remove", dl + "gone.py"), ("remove", dl + "stay.py"),
                         ("update", dl + "consumer.py"), ("remove", dl + "leaver.py"),
                         ("update", dl + "upd.py"), ("update", dl + "upd0.py"), ("update", dl + "ghost.py")):
            plan.entries[rel] = dp.PlanEntry(path=rel, tag=tag, deferred_remove=(rel.endswith("stay.py")))
        plan.entries[dl + "upd.py"].declared.append("NewName")
        plan.entries[dl + "upd0.py"].declared.append("Planned")
        plan.entries[dl + "ghost.py"].declared.append("Planned")  # 사본에 파일 없음 — 부재 update 대상
        (copy / dl / "blank.py").write_text("", encoding="utf-8")  # materialize 가 만든 자기 empty 상태
        consumer: str = dl + "consumer.py"
        rows: "list[tuple[str, str, str]]" = [
            # (라벨, stmt, 기대) — 기대 ∈ K|S|X|U|⑴|⑵|⑶
            ("ⓐ 실존 확인", "from application.shop.domain_layer.sku import Sku", "K"),
            ("ⓑ ⑶ 미정의", "from application.shop.domain_layer.sku import Nope", "⑶"),
            ("ⓒ ⑵ 0B", "from application.shop.domain_layer.empty0 import Thing", "⑵"),
            ("ⓓ ⑵ docstring-only", "from application.shop.domain_layer.doc_only import Thing", "⑵"),
            ("ⓔ ⑴ 부재", "from application.shop.domain_layer.absent import Thing", "⑴"),
            ("ⓕ 자기 add(⑶ 생략)", "from application.shop.domain_layer.new_vo import NotInSymbols", "S"),
            ("ⓖ ⑵ 자기 empty", "from application.shop.domain_layer.blank import Thing", "⑵"),
            ("ⓗ 승격 폴더 재수출", "from application.shop.domain_layer.promo import Promo", "K"),
            ("ⓘ 서브모듈 형", "from application.shop.domain_layer.promo import part", "K"),
            ("ⓙ 서드파티", "from ninja import Schema", "X"),
            ("ⓚ framework 부재", "from framework.test.clock import Clock", "⑴"),
            ("ⓛ import a.b.c", "import application.shop.domain_layer.sku", "K"),
            ("ⓛ′ import 부재", "import application.shop.domain_layer.absent", "⑴"),
            ("ⓜ 상대 .", "from .sku import Sku", "K"),
            ("ⓜ′ 상대 ..", "from ..domain_layer.sku import Sku", "K"),
            ("ⓜ″ 상대 탈출", "from .....nowhere import x", "U"),
            ("ⓝ import *", "from application.shop.domain_layer.sku import *", "U"),
            ("ⓞ planned-remove", "from application.shop.domain_layer.gone import Thing", "⑴"),
            ("ⓞ′ remove@Ln 실존", "from application.shop.domain_layer.stay import Stay", "K"),
            ("TypeAlias", "from application.shop.domain_layer.modern import Alias", "K" if sys.version_info >= (3, 12) else "⑶"),
            ("AsyncFunctionDef", "from application.shop.domain_layer.modern import fetch", "K"),
            ("Assign 튜플", "from application.shop.domain_layer.modern import c", "K"),
            ("AnnAssign", "from application.shop.domain_layer.modern import d", "K"),
            ("import a.b → a", "from application.shop.domain_layer.modern import os", "K"),
            ("import as", "from application.shop.domain_layer.modern import js", "K"),
            ("If 재귀", "from application.shop.domain_layer.modern import sep", "K"),
            ("Try 재귀", "from application.shop.domain_layer.modern import nothing", "K"),
            ("With 재귀", "from application.shop.domain_layer.modern import W", "K"),
            ("__all__ 문자열", "from application.shop.domain_layer.modern import listed", "K"),
            ("승격 폴더 부품 S", "from application.shop.application_layer.uc.do_uc.do_uc_use_case.do_uc_failure import DoUcFailure", "S"),
            ("승격 슬롯 자체 S", "from application.shop.application_layer.uc.do_uc.do_uc_use_case import DoUcUseCase", "S"),
            ("empty 모듈 import(⑵ 비적용)", "import application.shop.domain_layer.blank", "K"),
            ("empty 서브모듈 형(⑵ 비적용)", "from application.shop.domain_layer import blank", "K"),
            ("0B 모듈 import(⑵ 비적용)", "import application.shop.domain_layer.empty0", "K"),
            ("namespace-dir 이름 U", "from application.shop.domain_layer.nsdir import Thing", "U"),
            ("namespace-dir 서브모듈", "from application.shop.domain_layer.nsdir import leaf", "K"),
            ("namespace-dir 리프", "from application.shop.domain_layer.nsdir.leaf import X", "K"),
            ("import * 재수출 U", "from application.shop.domain_layer.star import Sku", "U"),
            ("__getattr__ U", "from application.shop.domain_layer.dyn import Anything", "U"),
            ("빈 패키지 __init__ (⑵ 비적용 → ⑶)", "from application.shop.domain_layer import Nothing", "⑶"),
            # update 대상(MAJOR B) — 선언 이름 S′ · 현재 표면 K · 미선언·미실존 U · 0B 대상 ⑵ 비적용 · 모듈 import K
            ("update 대상 선언 이름 S′", "from application.shop.domain_layer.upd import NewName", "S′"),
            ("update 대상 현재 표면 K", "from application.shop.domain_layer.upd import Existing", "K"),
            ("update 대상 미선언 U", "from application.shop.domain_layer.upd import Missing", "U"),
            ("update 0B 대상 선언 S′(⑵ 비적용)", "from application.shop.domain_layer.upd0 import Planned", "S′"),
            ("update 0B 대상 미선언 U(⑵ 비적용)", "from application.shop.domain_layer.upd0 import Other", "U"),
            ("update 대상 모듈 import K", "import application.shop.domain_layer.upd0", "K"),
            ("update 대상 서브모듈 형 K", "from application.shop.domain_layer import upd", "K"),
            # 사본에 부재한 update 대상(6단계 재검 MAJOR-1) — update 는 파일을 만들지 않으므로 ⑴ 유지(S′·K 세탁 금지)
            ("부재 update 대상 선언 이름 ⑴", "from application.shop.domain_layer.ghost import Planned", "⑴"),
            ("부재 update 대상 미선언 ⑴", "from application.shop.domain_layer.ghost import Other", "⑴"),
            ("부재 update 대상 모듈 import ⑴", "import application.shop.domain_layer.ghost", "⑴"),
            # 세미콜론 복합행 — 둘째 문(부재)도 판정된다(F-3)
            ("세미콜론 복합행 둘째 문 ⑴", "import application.shop.domain_layer.sku; from application.shop.domain_layer.absent import Thing", "⑴"),
        ]
        for _, stmt, _ in rows:
            plan.import_rows.append(dp.ImportRow(consumer=consumer, stmt=stmt))
        # 판정 밖·불능 행: 소비자 planned-remove · 문법 불량 stmt(update 소비자).
        plan.import_rows.append(dp.ImportRow(consumer=dl + "leaver.py", stmt="from application.shop.domain_layer.sku import Sku"))
        plan.import_rows.append(dp.ImportRow(consumer=consumer, stmt="from application.shop.domain_layer.sku import"))

        def verdict_of(stmt: str) -> str:
            single: "dp.Plan" = dp.Plan(entries=plan.entries)
            single.import_rows.append(dp.ImportRow(consumer=consumer, stmt=stmt))
            r: "dp.ExistenceReport" = dp.check_import_existence(copy, single)
            if r.defects:
                return r.defects[0].stage
            if r.confirmed:
                return "K"
            if r.self_add:
                return "S"
            if r.self_update:
                return "S′"
            if r.outside:
                return "X"
            return "U" if r.undecidable else "?"

        for label, stmt, want in rows:
            got: str = verdict_of(stmt)
            if got != want:
                out.append(f"계약 실존 {label}: `{stmt}` → {got} ≠ 기대 {want}")
        rep: "dp.ExistenceReport" = dp.check_import_existence(copy, plan)
        if rep.judged != rep.confirmed + rep.self_add + rep.self_update + rep.outside + rep.undecidable + rep.defective:
            out.append(f"계약 실존 계수 항등식 위반: T {rep.judged} ≠ K {rep.confirmed}+S {rep.self_add}+S′ {rep.self_update}"
                       f"+X {rep.outside}+U {rep.undecidable}+D {rep.defective}")
        # T 이름 단위(F-4) — 세미콜론 복합행 2 · 소비자 remove 2이름 2 · 문법 불량 1 · 상대 탈출 2이름 2(항등식 유지)
        for label, consumer_path, stmt, want_t, want_u in (
                ("세미콜론 복합행", consumer, "import application.shop.domain_layer.sku; from application.shop.domain_layer.absent import Thing", 2, 0),
                ("소비자 remove 2이름", dl + "leaver.py", "from application.shop.domain_layer.sku import Sku, Nope", 2, 2),
                ("문법 불량", consumer, "from application.shop.domain_layer.sku import", 1, 1),
                ("상대 탈출 2이름", consumer, "from .....nowhere import x, y", 2, 2)):
            one: "dp.Plan" = dp.Plan(entries=plan.entries)
            one.import_rows.append(dp.ImportRow(consumer=consumer_path, stmt=stmt))
            r1: "dp.ExistenceReport" = dp.check_import_existence(copy, one)
            if r1.judged != want_t or r1.undecidable != want_u or r1.judged != (
                    r1.confirmed + r1.self_add + r1.self_update + r1.outside + r1.undecidable + r1.defective):
                out.append(f"T 이름 단위 {label}: T {r1.judged}(기대 {want_t}) · U {r1.undecidable}(기대 {want_u}) · 항등식 "
                           f"{r1.confirmed}+{r1.self_add}+{r1.self_update}+{r1.outside}+{r1.undecidable}+{r1.defective}")
        if rep.rows != len(plan.import_rows):
            out.append(f"계약 실존 행 수 R {rep.rows} ≠ import_rows {len(plan.import_rows)}")
        if not any("소비자 제거" in n for n in rep.undecidable_notes) or not any("문법" in n for n in rep.undecidable_notes):
            out.append(f"계약 실존 판정 불능 사유(소비자 제거·문법) 부재: {rep.undecidable_notes}")
        details: "dict[str, str]" = {f"{d.module} import {d.name}": d.detail for d in rep.defects}
        if "자리표시자(0B — 기존 실물)" != details.get("application.shop.domain_layer.empty0 import Thing"):
            out.append(f"⑵ 문면(0B — 기존 실물) 불일치: {details.get('application.shop.domain_layer.empty0 import Thing')!r}")
        if "자리표시자(docstring/주석-only — 기존 실물)" != details.get("application.shop.domain_layer.doc_only import Thing"):
            out.append(f"⑵ 문면(docstring-only) 불일치: {details.get('application.shop.domain_layer.doc_only import Thing')!r}")
        if "자리표시자(0B — 자기 `empty`)" != details.get("application.shop.domain_layer.blank import Thing"):
            out.append(f"⑵ 문면(자기 empty) 불일치: {details.get('application.shop.domain_layer.blank import Thing')!r}")
        if "모듈 부재 — update 대상 부재(계획↔실물 모순)" != details.get("application.shop.domain_layer.ghost import Planned"):
            out.append(f"⑴ 문면(부재 update 대상) 불일치: {details.get('application.shop.domain_layer.ghost import Planned')!r}")
        # ⓟ ID 안정성 — 같은 (모듈, 이름) 소비자 2개 → 항목 1·소비자 2 · 단계(⑴→⑵) 무관 · 예보 ID 정규식 불충돌.
        two: "dp.Plan" = dp.Plan(entries=plan.entries)
        two.import_rows.append(dp.ImportRow(consumer=consumer, stmt="from application.shop.domain_layer.absent import Thing"))
        two.import_rows.append(dp.ImportRow(consumer=dl + "other.py", stmt="from application.shop.domain_layer.absent import Thing"))
        r2: "dp.ExistenceReport" = dp.check_import_existence(copy, two)
        if len(r2.defects) != 1 or len(r2.defects[0].consumers) != 2 or r2.defective != 2:
            out.append(f"ⓟ 결손 합치기 실패: 항목 {len(r2.defects)} · 소비자 {[d.consumers for d in r2.defects]} · D {r2.defective}")
        eid: str = dp._existence_id("application.shop.domain_layer.absent", "Thing")
        if not re.fullmatch(r"e-[0-9a-f]{12}", eid) or _FORECAST_RULE_RE.search(f"`{eid}` ⑴ 모듈 부재 [#81]"):
            out.append(f"ⓟ 안정 ID 형식/불충돌 위반: {eid}")
        lines: str = "\n".join(dp._existence_lines(r2))
        if len(_EXISTENCE_LINE_RE.findall(lines)) != 1 or _EXISTENCE_AGG_RE.search(lines) is None:
            out.append(f"계약 실존 절 형식 위반:\n{lines}")
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
    m: "re.Match[str] | None" = _KEEP_RE.search(proc.stdout)
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


def _count_built(report: Path) -> int:
    """리포트의 «already-built: add(기실현» 누적 행 수(묶음 리포트는 append 라 차분으로 센다)."""
    return report.read_text(encoding="utf-8").count("already-built: add(기실현") if report.is_file() else 0


def _anchor_clean(stdout: str) -> bool:
    """E2/E2′ 증거 — 해소(L∖N) 0 ∧ check-domain-model anchor 열 0(실물이 앵커 스냅숏에 안 실렸다)."""
    resolved: "re.Match[str] | None" = _RESOLVED_RE.search(stdout)
    row: "re.Match[str] | None" = _DOMAIN_MODEL_ROW_RE.search(stdout)
    return resolved is not None and resolved.group(1) == "0" and row is not None and row.group(1) == "0"


def _run_mid_bundle(scratch: Path, failures: "list[str]") -> None:
    spec: Path = FIXTURES / "midlane-spec.md"
    spec_red: Path = FIXTURES / "midlane-red-spec.md"
    report: Path = scratch / "pregate-report-mid.md"

    # E1 — 기준선 이후 커밋에 계획 add 실존 → `--base <기준선>` → 사본에는 없어 스텁 · 기실현 0.
    repo: Path = _make_repo(scratch, "repo-mid-e1")
    base: str = _git(repo, "rev-parse", "HEAD")
    (repo / MID_ADD).write_text("class LaneMarker:\n    value: str\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "slice: lane marker")
    e1: "subprocess.CompletedProcess[str]" = _run_pregate(spec, repo, report, ["--base", base, "--keep"])
    stub_e1: "bool | None" = _kept_copy_is_stub(e1, MID_ADD)
    built_e1: int = _count_built(report)
    if e1.returncode != 0 or "already-built 0건" not in e1.stdout or built_e1 != 0 or stub_e1 is not True:
        failures.append(f"E1 기대 exit 0·기실현 0·사본 스텁 ≠ 실측 exit {e1.returncode} · "
                        f"기실현 {built_e1} · 스텁 {stub_e1}")
        _dump("E1", e1)
    else:
        print("E1: exit 0 · 사본 스텁 · 기실현 0 (커밋된 add 는 사본 밖) — 기대 일치")

    # E2 — 미커밋 WIP(의도 위반 실물) → `--base <기준선>` → 기실현 1 · 스텁 대체(실물 판정 혼입 0) ·
    # 해소 0 ∧ anchor 열 0(실물이 앵커 스냅숏에 안 실렸다 — MAJOR A 오염 가드).
    repo = _make_repo(scratch, "repo-mid-e2")
    base = _git(repo, "rev-parse", "HEAD")
    (repo / MID_ADD).write_text(MID_REAL_SRC, encoding="utf-8")
    e2: "subprocess.CompletedProcess[str]" = _run_pregate(spec, repo, report, ["--base", base, "--keep"])
    stub_e2: "bool | None" = _kept_copy_is_stub(e2, MID_ADD)
    built_e2: int = _count_built(report) - built_e1
    if (e2.returncode != 0 or "already-built 1건" not in e2.stdout or built_e2 != 1 or stub_e2 is not True
            or not _anchor_clean(e2.stdout)):
        failures.append(f"E2 기대 exit 0·기실현 1·사본 스텁·해소 0·anchor 열 0 ≠ 실측 exit {e2.returncode} · "
                        f"기실현 {built_e2} · 스텁 {stub_e2} · 앵커 무오염 {_anchor_clean(e2.stdout)}")
        _dump("E2", e2)
    else:
        print("E2: exit 0 · 기실현 1 · 스텁 대체(실물 #267 미혼입) · 해소 0·anchor 열 0 — 기대 일치")

    # E3 — E2 상태에서 `--base` 미지정 → 기본 경로 불변(add 충돌 형식 red).
    e3: "subprocess.CompletedProcess[str]" = _run_pregate(spec, repo, report)
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
    e4: "subprocess.CompletedProcess[str]" = _run_pregate(spec, repo, report, ["--base", base])
    if e4.returncode != 3 or "add 충돌(실존)" not in e4.stdout:
        failures.append(f"E4 기대 exit 3(기준선 실존 add) ≠ 실측 {e4.returncode}")
        _dump("E4", e4)
    else:
        print("E4: exit 3 (기준선 트리 실존 add — 계획↔실물 모순 유지) — 기대 일치")

    # E1′/E2′ — red 변형(스텁 자체가 #267): 커밋 실물 vs 동내용 미커밋 WIP → 둘 다 exit 2 · 같은 ID(MAJOR A 회귀 가드).
    repo = _make_repo(scratch, "repo-mid-e1r")
    base = _git(repo, "rev-parse", "HEAD")
    (repo / MID_ADD).write_text(MID_REAL_SRC, encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "slice: lane marker (2 classes)")
    e1r: "subprocess.CompletedProcess[str]" = _run_pregate(spec_red, repo, report, ["--base", base])
    ids_e1r: "list[str]" = sorted(set(_FORECAST_RULE_RE.findall(e1r.stdout)))
    repo = _make_repo(scratch, "repo-mid-e2r")
    base = _git(repo, "rev-parse", "HEAD")
    (repo / MID_ADD).write_text(MID_REAL_SRC, encoding="utf-8")
    e2r: "subprocess.CompletedProcess[str]" = _run_pregate(spec_red, repo, report, ["--base", base])
    ids_e2r: "list[str]" = sorted(set(_FORECAST_RULE_RE.findall(e2r.stdout)))
    if (e1r.returncode != 2 or e2r.returncode != 2 or ids_e1r != ids_e2r or ids_e1r != ["267"]
            or "already-built 1건" not in e2r.stdout or not _anchor_clean(e2r.stdout)):
        failures.append(f"E1′/E2′ 기대 exit 2·2·같은 ID(#267)·E2′ 기실현 1·해소 0·anchor 열 0 ≠ 실측 "
                        f"exit {e1r.returncode}/{e2r.returncode} · ID {ids_e1r}/{ids_e2r} · "
                        f"앵커 무오염 {_anchor_clean(e2r.stdout)}")
        _dump("E1′", e1r)
        _dump("E2′", e2r)
    else:
        print("E1′/E2′: exit 2·2 · 같은 ID(#267) · E2′ 기실현 1·해소 0·anchor 열 0 (기실현 add 앵커 무오염) — 기대 일치")

    if _header_count(report) != 6:
        failures.append(f"[mid] 리포트 append 횟수 {_header_count(report)} ≠ 기대 6 ({report})")

    # 2026-09-27 로드맵 3 S-3 — F4-23 회귀 가드(별도 리포트 · 위 헤더 계수 무접촉).
    report_f: Path = scratch / "pregate-report-mid-f423.md"
    green_spec: Path = FIXTURES / "green-spec.md"
    wip_outside: "tuple[str, ...]" = ("application/billing/test/__init__.py", "application/billing/test/unit/__init__.py")
    # E5 — 기준선 이후 S1 커밋(신규 BC 일부) + 계획 밖 WIP(새 폴더 `__init__.py`) → `--base <기준선>`:
    # 오버레이 생략(기준선≠HEAD) → 사본 = 기준선 트리 → 골격 실체화 → green · «dirty overlay 생략» 행.
    repo = _make_repo(scratch, "repo-mid-e5")
    base = _git(repo, "rev-parse", "HEAD")
    s1: Path = repo / "application/billing/domain_layer/shared_value_object/invoice_number.py"
    s1.parent.mkdir(parents=True, exist_ok=True)
    s1.write_text("class InvoiceNumber:\n    value: str\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "slice 1: billing value object")
    for rel in wip_outside:
        (repo / rel).parent.mkdir(parents=True, exist_ok=True)
        (repo / rel).write_text("", encoding="utf-8")
    e5: "subprocess.CompletedProcess[str]" = _run_pregate(green_spec, repo, report_f, ["--base", base])
    if e5.returncode != 0 or "dirty overlay 생략: 기준선≠HEAD · 작업 트리 변경 2경로" not in e5.stdout:
        failures.append(f"E5(F4-23) 기대 exit 0 · «dirty overlay 생략 … 2경로» ≠ 실측 exit {e5.returncode}")
        _dump("E5", e5)
    else:
        print("E5: exit 0 · dirty overlay 생략 2경로 (기준선≠HEAD 재발화 — 혼합 사본 없음 · F4-23) — 기대 일치")
    # E6 — 기준선 = HEAD(첫 슬라이스 미커밋) + 계획 밖 WIP 가 신규 BC 폴더를 만든 상태 → 기본 실행:
    # 골격 가드는 기준선 트리로 판정 → 신규 BC 골격 실체화 → green(앵커 오염으로 골격을 건너뛰지 않는다 · 검토 E m7).
    repo = _make_repo(scratch, "repo-mid-e6")
    for rel in wip_outside:
        (repo / rel).parent.mkdir(parents=True, exist_ok=True)
        (repo / rel).write_text("", encoding="utf-8")
    e6: "subprocess.CompletedProcess[str]" = _run_pregate(green_spec, repo, report_f)
    if e6.returncode != 0 or "dirty overlay 생략" in e6.stdout:
        failures.append(f"E6(골격 가드 기준선화) 기대 exit 0 · 오버레이 유지 ≠ 실측 exit {e6.returncode}")
        _dump("E6", e6)
    else:
        print("E6: exit 0 · 기준선 = HEAD 오버레이 유지 · 신규 BC 골격 실체화 (계획 밖 WIP 앵커 오염 무해) — 기대 일치")


def _run_imports_bundle(scratch: Path, failures: "list[str]") -> None:
    """계약 실존 e2e 3종 — 합성 저장소 2(`mini_repo` + `imports_overlay/`) · 리포트 각 1."""
    repo: Path = scratch / "repo-imports"
    shutil.copytree(FIXTURES / "mini_repo", repo)
    shutil.copytree(FIXTURES / "imports_overlay", repo, dirs_exist_ok=True)
    _git(repo, "init", "-q")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "fixture-baseline+imports-overlay")

    def section(report: Path) -> str:
        text: str = report.read_text(encoding="utf-8") if report.is_file() else ""
        at: int = text.find("### 계약 실존")
        return text[at:] if at >= 0 else ""

    report_g: Path = scratch / "pregate-report-imports-green.md"
    green: "subprocess.CompletedProcess[str]" = _run_pregate(FIXTURES / "imports-green-spec.md", repo, report_g)
    agg: "re.Match[str] | None" = _EXISTENCE_AGG_RE.search(green.stdout)
    counts: "tuple[int, ...]" = tuple(int(x) for x in agg.groups()) if agg else ()
    if (green.returncode != 0 or _FORECAST_RULE_RE.search(green.stdout) or _EXISTENCE_LINE_RE.search(green.stdout)
            or counts != (5, 5, 2, 1, 1, 1, 0, 0) or "요약: 귀속 0건 · 실존 결손 0건" not in green.stdout):
        failures.append(f"imports-green-spec 기대 exit 0·결손 0·집계 (5,5,2,1,1,1,0,0) ≠ 실측 exit {green.returncode} · 집계 {counts}")
        _dump("imports-green", green)
    else:
        print("imports-green-spec: exit 0 · 결손 0 · 집계 K2/S1/S′1/X1 (실존 확인·서브모듈·자기 add·update 대상 새 심볼·서드파티) — 기대 일치")
    if _header_count(report_g) != 1 or "### 계약 실존 (boundary-imports 3단 · 결손 0건" not in section(report_g):
        failures.append(f"[imports green] 리포트 append {_header_count(report_g)} ≠ 1 또는 계약 실존 절 부재")

    report_r: Path = scratch / "pregate-report-imports-red.md"
    red: "subprocess.CompletedProcess[str]" = _run_pregate(FIXTURES / "imports-red-spec.md", repo, report_r)
    stages: "list[str]" = _EXISTENCE_LINE_RE.findall(red.stdout)
    if (red.returncode != 5 or sorted(stages) != ["⑴", "⑵", "⑶"] or _FORECAST_RULE_RE.search(red.stdout)
            or "요약: 귀속 0건 · 실존 결손 3건" not in red.stdout):
        failures.append(f"imports-red-spec 기대 exit 5·⑴⑵⑶ 각 1·귀속 0 ≠ 실측 exit {red.returncode} · 단계 {stages}")
        _dump("imports-red", red)
    else:
        print("imports-red-spec: exit 5 · ⑴⑵⑶ 각 1 · 귀속 0 (권고·비차단) — 기대 일치")
    sec_r: str = section(report_r)
    if (_header_count(report_r) != 1 or len(_EXISTENCE_LINE_RE.findall(sec_r)) != 3
            or "- 판정: 예보 green" not in report_r.read_text(encoding="utf-8")
            or "계약 실존 결손 3건(권고·비차단)" not in report_r.read_text(encoding="utf-8")):
        failures.append(f"[imports red] 리포트 append {_header_count(report_r)} ≠ 1 또는 절 항목/헤더 병기 불일치")

    report_u: Path = scratch / "pregate-report-imports-update-only.md"
    upd: "subprocess.CompletedProcess[str]" = _run_pregate(FIXTURES / "imports-update-only-spec.md", repo, report_u)
    stages_u: "list[str]" = _EXISTENCE_LINE_RE.findall(upd.stdout)
    if (upd.returncode != 5 or stages_u != ["⑵"] or "실체화 0건" not in upd.stdout
            or "요약: 실체화 0 · 실존 결손 1건" not in upd.stdout):
        failures.append(f"imports-update-only-spec 기대 exit 5·⑵ 1·«실체화 0» ≠ 실측 exit {upd.returncode} · 단계 {stages_u}")
        _dump("imports-update-only", upd)
    else:
        print("imports-update-only-spec: exit 5 · 실체화 0 · ⑵ 1 (kkebi S2 판형 — update 소비자 포함) — 기대 일치")
    sec_u: str = section(report_u)
    if (_header_count(report_u) != 1 or len(_EXISTENCE_LINE_RE.findall(sec_u)) != 1
            or "- 판정: skip · 계약 실존 결손 1건(권고·비차단)" not in report_u.read_text(encoding="utf-8")):
        failures.append(f"[imports update-only] 리포트 append {_header_count(report_u)} ≠ 1 또는 stub 절/판정 불일치")


_FORECAST_ID_RE: "re.Pattern[str]" = re.compile(r"^\s*`([0-9a-f]{12})` .*?\[#[\w-]+\]", re.M)
_SUMMARY_FORM_RE: "re.Pattern[str]" = re.compile(r"^요약: 형식 red (\d+)건\(([^)]+)\)", re.M)
_SUMMARY_CHECK_RE: "re.Pattern[str]" = re.compile(r"^요약: check-report (정합|불비 \d+건) · 블록 해시 ([0-9a-f]{12})=(\S+)", re.M)
PROMO_PY: str = "application/orders/domain_layer/shared_value_object/promo.py"


def _run_check(spec: Path, report: Path) -> "subprocess.CompletedProcess[str]":
    return subprocess.run([sys.executable, str(EXECUTOR), str(spec), ".", "--check-report", str(report)],
                          capture_output=True, text=True)


def _expect_form(label: str, proc: "subprocess.CompletedProcess[str]", kind: str, report: Path, verdict: str,
                 failures: "list[str]") -> None:
    """차단 모드 형식 red 경로 공통 단언 — exit 3 · `요약: 형식 red N건(<종류>)` 접두 · 리포트 `- 판정:` 문면·해시 병기."""
    m: "re.Match[str] | None" = _SUMMARY_FORM_RE.search(proc.stdout)
    text: str = report.read_text(encoding="utf-8") if report.is_file() else ""
    last: str = text[text.rfind("## pre-gate 예보"):] if "## pre-gate 예보" in text else ""
    ok: bool = (proc.returncode == 3 and m is not None and kind in m.group(2)
                and f"- 판정: {verdict}" in last and re.search(r"블록 해시 [0-9a-f]{12}", last) is not None)
    if not ok:
        failures.append(f"{label} 기대 exit 3·요약 «형식 red N건({kind})»·판정 «{verdict}» ≠ 실측 exit {proc.returncode} · "
                        f"요약 {m.group(0) if m else '(없음)'}")
        _dump(label, proc)
    else:
        print(f"{label}: exit 3 · {m.group(0)} · 판정 «{verdict}» — 기대 일치")


def _run_enforce_bundle(scratch: Path, failures: "list[str]") -> None:
    """차단 모드 회피 경로 봉쇄 — 블록 부재·공허·update/remove 대상 기준선 부재(승격 형태 예외·오버레이 불인정)."""
    report: Path = scratch / "pregate-report-enforce.md"
    repo: Path = _make_repo(scratch, "repo-enforce")
    _expect_form("noblock-spec", _run_pregate(FIXTURES / "noblock-spec.md", repo, report),
                 "블록 부재", report, "형식 red(블록 부재)", failures)
    if "모드: 차단(enforce)" not in report.read_text(encoding="utf-8"):
        failures.append("[enforce] 리포트 헤더에 «모드: 차단(enforce)» 스탬프 부재")
    _expect_form("empty-block-spec", _run_pregate(FIXTURES / "empty-block-spec.md", repo, report),
                 "블록 공허", report, "형식 red(블록 공허)", failures)
    spec_u: Path = FIXTURES / "update-target-spec.md"
    _expect_form("update-target ⓐ(기준선 부재)", _run_pregate(spec_u, repo, report),
                 "update 대상 부재", report, "형식 red", failures)
    _expect_form("remove-target-spec", _run_pregate(FIXTURES / "remove-target-spec.md", repo, report),
                 "remove 대상 부재", report, "형식 red", failures)
    _expect_form("empty-conflict-spec", _run_pregate(FIXTURES / "empty-conflict-spec.md", repo, report),
                 "empty 충돌", report, "형식 red", failures)
    deferred: "subprocess.CompletedProcess[str]" = _run_pregate(FIXTURES / "remove-deferred-spec.md", repo, report)
    if deferred.returncode != 4 or "후행 remove" not in deferred.stdout:
        failures.append(f"remove-deferred-spec 기대 exit 4(후행 remove 판정 밖·실체화 0) ≠ 실측 {deferred.returncode}")
        _dump("remove-deferred", deferred)
    else:
        print("remove-deferred-spec: exit 4 (remove@L1 은 판정 밖 · 실체화 0) — 기대 일치")
    # ⓒ 오버레이만(미커밋 승격 폴더) → 기준선 부재라 여전히 exit 3.
    promo_dir: Path = repo / PROMO_PY[:-3]
    promo_dir.mkdir(parents=True)
    (promo_dir / "__init__.py").write_text("", encoding="utf-8")
    (promo_dir / "promo.py").write_text("class Promo:\n    code: str\n    rate: int\n", encoding="utf-8")
    _expect_form("update-target ⓒ(승격 폴더 미커밋)", _run_pregate(spec_u, repo, report),
                 "update 대상 부재", report, "형식 red", failures)
    # ⓑ 승격 형태를 기준선에 커밋 → 예외 통과 · update 뿐이라 실체화 0 · 결손 0 → exit 4.
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "promote promo")
    promoted: "subprocess.CompletedProcess[str]" = _run_pregate(spec_u, repo, report)
    if promoted.returncode != 4 or "승격 형태 실존 — 예외 통과" not in promoted.stdout:
        failures.append(f"update-target ⓑ 기대 exit 4(승격 형태 예외·실체화 0) ≠ 실측 {promoted.returncode}")
        _dump("update-target promoted", promoted)
    else:
        print("update-target ⓑ(승격 형태 커밋): exit 4 · 예외 통과 문면 — 기대 일치")
    if _header_count(report) != 8:
        failures.append(f"[enforce] 리포트 append 횟수 {_header_count(report)} ≠ 기대 8 ({report})")


def _expect_check(label: str, proc: "subprocess.CompletedProcess[str]", code: int, failures: "list[str]",
                  needle: "str | None" = None) -> None:
    m: "re.Match[str] | None" = _SUMMARY_CHECK_RE.search(proc.stdout)
    ok: bool = proc.returncode == code and (code == 1 or m is not None) and (needle is None or needle in proc.stdout)
    if not ok:
        failures.append(f"check-report {label} 기대 exit {code}{'·«' + needle + '»' if needle else ''} ≠ 실측 exit "
                        f"{proc.returncode} · 요약 {m.group(0) if m else '(없음)'}")
        _dump(f"check-report {label}", proc)
    else:
        print(f"check-report {label}: exit {code}{' · ' + m.group(1) if m else ''} — 기대 일치")


def _run_inflow_bundle(scratch: Path, failures: "list[str]") -> None:
    """로드맵 3 S-1·S-1b(F4-21) — 발주자 승인 머지 유입(추가·수정·삭제)과 check-report 기준선 치환 봉쇄."""
    spec: Path = FIXTURES / "inflow-spec.md"
    spec_add: Path = FIXTURES / "inflow-addconflict-spec.md"
    report: Path = scratch / "pregate-report-inflow.md"
    repo: Path = _make_repo(scratch, "repo-inflow")
    # 기준선 이전 머지(불참이어야 한다): side 가지를 기준선 전에 한 번 받는다.
    root_branch: str = _git(repo, "rev-parse", "--abbrev-ref", "HEAD")
    _git(repo, "checkout", "-q", "-b", "side")
    (repo / "docs_side.md").write_text("side\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "side note")
    _git(repo, "checkout", "-q", root_branch)
    _git(repo, "merge", "-q", "--no-ff", "-m", "early merge side", "side")
    early: str = _git(repo, "rev-parse", "HEAD")
    base: str = early
    # 레인 S1 · main 쪽(추가·수정·삭제) · 승인 머지.
    _git(repo, "checkout", "-q", "-b", "upstream")
    (repo / "config/inflow_settings.py").write_text("INFLOW_FLAG: bool = True\n", encoding="utf-8")
    (repo / "config/api.py").write_text((repo / "config/api.py").read_text(encoding="utf-8")
                                        + "INFLOW_ROUTE: str = \"inflow\"\n", encoding="utf-8")
    _git(repo, "rm", "-q", "config/celery.py")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "upstream: add/modify/delete")
    _git(repo, "checkout", "-q", root_branch)
    (repo / "docs_lane.md").write_text("lane S1\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "lane S1")
    lane_s1: str = _git(repo, "rev-parse", "HEAD")
    _git(repo, "merge", "-q", "--no-ff", "-m", "approved merge upstream", "upstream")
    merge: str = _git(repo, "rev-parse", "HEAD")
    approved: Path = scratch / "approved-merges.txt"
    approved.write_text(f"{early} 기준선 이전(불참)\n{merge} 승인\n", encoding="utf-8")
    flag: "list[str]" = ["--approved-merge-file", str(approved)]
    bad_before: int = len(failures)

    a = _run_pregate(spec, repo, report, ["--base", base])
    if a.returncode != 3 or "update 대상 기준선 이후 실존: config/inflow_settings.py" not in a.stdout \
            or "--approved-merge-file" not in a.stdout:
        failures.append(f"inflow 무플래그 기대 exit 3 · «update 대상 기준선 이후 실존» + 승인 유입 갈래 안내 ≠ 실측 exit {a.returncode}")
        _dump("inflow-a", a)
    b = _run_pregate(spec, repo, report, ["--base", base] + flag)
    if (b.returncode != 0 or "승인 유입: 3경로(추가 1 · 수정 1 · 삭제 1)" not in b.stdout
            or "불참 머지 1" not in b.stdout or "요약: 귀속 0건 · 실존 결손 0건" not in b.stdout):
        failures.append(f"inflow 플래그 기대 exit 0 · 승인 유입 3경로(추가 1·수정 1·삭제 1) · 불참 1 · 결손 0 ≠ 실측 exit {b.returncode}")
        _dump("inflow-b", b)
    c = _run_pregate(spec_add, repo, scratch / "pregate-report-inflow-add.md", ["--base", base] + flag)
    if c.returncode != 3 or "승인 유입 add 충돌: config/inflow_settings.py" not in c.stdout:
        failures.append(f"inflow add 충돌 기대 exit 3 · «승인 유입 add 충돌» ≠ 실측 exit {c.returncode}")
        _dump("inflow-c", c)
    bad_list: Path = scratch / "approved-bad.txt"
    bad_list.write_text(f"{lane_s1} 비머지\n", encoding="utf-8")
    d = _run_pregate(spec, repo, scratch / "pregate-report-inflow-bad.md",
                     ["--base", base, "--approved-merge-file", str(bad_list)])
    if d.returncode != 1 or "승인 머지 목록 검증 실패" not in d.stderr:
        failures.append(f"inflow 비머지 목록 기대 exit 1 · «검증 실패» ≠ 실측 exit {d.returncode} · {d.stderr.strip()[:120]}")
    e = _run_pregate(spec, repo, scratch / "pregate-report-inflow-missing.md",
                     ["--base", base, "--approved-merge-file", str(scratch / "no-such.txt")])
    if e.returncode != 1 or "승인 머지 목록 부재" not in e.stderr:
        failures.append(f"inflow 목록 부재 기대 exit 1 ≠ 실측 exit {e.returncode}")
    # S-1b — 기대 기준선: 전체 · 7자 접두 일치 → 0 · 다른 SHA → 3 «기준선 치환» · --check-report 없이 → 1.
    def check(expect: "str | None") -> "subprocess.CompletedProcess[str]":
        extra: "list[str]" = ["--expect-base", expect] if expect is not None else []
        return subprocess.run([sys.executable, str(EXECUTOR), str(spec), ".", "--check-report", str(report)] + extra,
                              capture_output=True, text=True)
    for label, expect, want, needle in (("전체", base, 0, "정합"), ("7자 접두", base[:7], 0, "정합"),
                                        ("치환", lane_s1, 3, "기준선 치환")):
        r = check(expect)
        if r.returncode != want or needle not in r.stdout:
            failures.append(f"check-report --expect-base[{label}] 기대 exit {want} · «{needle}» ≠ 실측 exit {r.returncode}")
            print(r.stdout[-600:])
    lone = subprocess.run([sys.executable, str(EXECUTOR), str(spec), ".", "--expect-base", base],
                          capture_output=True, text=True)
    if lone.returncode != 1 or "--check-report 와 함께만" not in lone.stderr:
        failures.append(f"--expect-base 단독 기대 exit 1 ≠ 실측 exit {lone.returncode}")
    # S-3b — 기준선 이후 레인 커밋이 만든 계약을 file-plan 없이 소비 → 결손(판정 무변) + «기준선 이후 바뀐 파일» 처방.
    repo_p: Path = _make_repo(scratch, "repo-postbase")
    base_p: str = _git(repo_p, "rev-parse", "HEAD")
    (repo_p / "framework/test").mkdir(parents=True, exist_ok=True)
    (repo_p / "framework/test/lane_helper.py").write_text("class LaneHelper:\n    pass\n", encoding="utf-8")
    _git(repo_p, "add", "-A")
    _git(repo_p, "commit", "-q", "-m", "lane S1 helper")
    f = _run_pregate(FIXTURES / "postbase-defect-spec.md", repo_p, scratch / "pregate-report-postbase.md", ["--base", base_p])
    if (f.returncode != 5 or "기준선 이후 바뀐 파일 `framework/test/lane_helper.py`" not in f.stdout
            or "그 이름을 symbols 에 선언" not in f.stdout):
        failures.append(f"S-3b 결손 안내 기대 exit 5 · «기준선 이후 바뀐 파일 … symbols 에 선언» ≠ 실측 exit {f.returncode}")
        _dump("postbase", f)
    g = _run_pregate(FIXTURES / "postbase-defect-spec.md", repo_p, scratch / "pregate-report-postbase-head.md")
    if g.returncode != 4 or "기준선 이후 바뀐 파일" in g.stdout:  # update 만 · 실체화 0 · 결손 0 = skip(4)
        failures.append(f"S-3b 기본 실행(HEAD) 기대 exit 4(skip · 결손 0) · 안내 없음 ≠ 실측 exit {g.returncode}")
        _dump("postbase-head", g)
    if len(failures) == bad_before:
        print("inflow: 무플래그 exit 3 · 플래그 exit 0(추가 1·수정 1·삭제 1 · 불참 1 · 결손 0) · add 충돌 3 · "
              "비머지·부재 목록 1 · --expect-base 전체/7자 0 · 치환 3 · 단독 1 · 기준선 이후 결손 안내(exit 5)·HEAD 결손 0(skip 4) — 기대 일치")


def _run_checkreport_bundle(scratch: Path, failures: "list[str]") -> None:
    """`--check-report` — 리포트 최신성·처분 완결 대조(전용 저장소·리포트 · 실제 실행기 출력 위에 처분 행 append)."""
    repo: Path = _make_repo(scratch, "repo-cr")
    report: Path = scratch / "pregate-report-cr.md"
    red_spec: Path = FIXTURES / "red-spec.md"
    red: "subprocess.CompletedProcess[str]" = _run_pregate(red_spec, repo, report)
    ids: "list[str]" = _FORECAST_ID_RE.findall(red.stdout)
    if red.returncode != 2 or len(ids) != EXPECTED_RED_COUNT:
        failures.append(f"[checkreport] red-spec 준비 실패 — exit {red.returncode} · ID {len(ids)}")
        _dump("checkreport red", red)
        return
    _expect_check("red 미라벨", _run_check(red_spec, report), 3, failures, f"처분 미기재 {EXPECTED_RED_COUNT}건")
    with report.open("a", encoding="utf-8") as fp:
        fp.write("\n## pre-gate 처분 라벨 (코디네이터 소유 · 차단 모드)\n")
        for i in ids[:2]:
            fp.write(f"- `{i}` [#x] path → **ignored**(빚: docs/legacy-debt.md:12 · STOP docs/stop-1.md)\n")
    _expect_check("ignored 2 append", _run_check(red_spec, report), 3, failures, "처분 미기재 1건")
    with report.open("a", encoding="utf-8") as fp:
        fp.write(f"- `{ids[2]}` [#x] path → **corrected** — 개정으로 소멸 예정\n")
    _expect_check("3번째 corrected(불인정)", _run_check(red_spec, report), 3, failures, "처분 미기재 1건")
    with report.open("a", encoding="utf-8") as fp:
        fp.write(f"- `{ids[2]}` [#x] path → **filtered**(ⓐ S1 — 본문 규칙)\n")
    _expect_check("3번째 filtered(전건)", _run_check(red_spec, report), 0, failures, "red 3(처분 전건)")
    with report.open("a", encoding="utf-8") as fp:
        fp.write("- 블록 해시 갱신 — 재실행 예정(무값 문자열 · 파서 무영향)\n")
    _expect_check("오염 행 무영향", _run_check(red_spec, report), 0, failures)
    _expect_check("다른 명세(stale)", _run_check(FIXTURES / "green-spec.md", report), 3, failures, "stale")
    # 표 형식 처분(reading 판형 — 백틱 라벨·표 셀)은 정형이 아니라 불인정: 새 red 절 뒤에 표만 있으면 불비.
    red2: "subprocess.CompletedProcess[str]" = _run_pregate(red_spec, repo, report)
    with report.open("a", encoding="utf-8") as fp:
        fp.write("\n| ID | 라벨 | 근거 |\n|---|---|---|\n" + "".join(f"| `{i}` | `filtered` | 표 형식 |\n" for i in ids))
    _expect_check("표 형식 처분(불인정)", _run_check(red_spec, report), 3, failures, f"처분 미기재 {EXPECTED_RED_COUNT}건")
    if red2.returncode != 2:
        failures.append(f"[checkreport] red 재실행 exit {red2.returncode} ≠ 2")
    else:
        print("check-report red 재실행: exit 2 — 기대 일치")
    # 형식 red 리포트 · 블록 부재 리포트 · skip·결손 리포트 · 구판 헤더 · 리포트 부재.
    report_f: Path = scratch / "pregate-report-cr-form.md"
    _run_pregate(FIXTURES / "form-red-spec.md", repo, report_f)
    _expect_check("형식 red 마지막", _run_check(FIXTURES / "form-red-spec.md", report_f), 3, failures, "형식 red 미해소")
    report_n: Path = scratch / "pregate-report-cr-noblock.md"
    _run_pregate(FIXTURES / "noblock-spec.md", repo, report_n)
    _expect_check("블록 부재 마지막", _run_check(FIXTURES / "noblock-spec.md", report_n), 3, failures, "형식 red 미해소")
    report_s: Path = scratch / "pregate-report-cr-skip.md"
    repo_i: Path = _make_repo(scratch, "repo-cr-imports")
    shutil.copytree(FIXTURES / "imports_overlay", repo_i, dirs_exist_ok=True)
    _git(repo_i, "add", "-A")
    _git(repo_i, "commit", "-q", "-m", "imports-overlay")
    _run_pregate(FIXTURES / "imports-update-only-spec.md", repo_i, report_s)
    _expect_check("skip·결손 통과", _run_check(FIXTURES / "imports-update-only-spec.md", report_s), 0, failures, "skip · 실존 결손 1")
    old: Path = scratch / "pregate-report-cr-old.md"
    old.write_text(re.sub(r" · 블록 해시 [0-9a-f]{12}", "", report_s.read_text(encoding="utf-8")), encoding="utf-8")
    _expect_check("구판 헤더(해시 토큰 없음)", _run_check(FIXTURES / "imports-update-only-spec.md", old), 3, failures,
                  "최신성 증명 불가")
    _expect_check("리포트 부재", _run_check(red_spec, scratch / "no-such-report.md"), 1, failures)
    _expect_check("절 부재", _run_check(red_spec, FIXTURES / "green-spec.md"), 1, failures)


def _enforce_unit_checks() -> "list[str]":
    """차단 모드 유닛 — `baseline_form_errors`(순수 판정 · 전건 열거 · 승격 형태 예외) · `check_report`(파서 경계)."""
    out: "list[str]" = []
    dp: "types.ModuleType" = _load_module(EXECUTOR, "_pregate_enforce")
    if len(dp.BLIND_SPOTS) != 9 or any(not s.startswith(f"S{i + 1} ") for i, s in enumerate(dp.BLIND_SPOTS)):
        out.append("BLIND_SPOTS 번호 S1~S9 불일치(filtered ⓐ 인용 결정성)")
    if dp.MODE != "enforce":
        out.append(f"MODE = {dp.MODE!r} ≠ 'enforce'")
    with tempfile.TemporaryDirectory(prefix="pregate-unit-") as tmp:
        copy: Path = Path(tmp)
        for rel in ("a/existing.py", "a/gone_dir/__init__.py", "a/promo/__init__.py", "a/promo/promo.py",
                    "a/half/__init__.py", "a/half2/half2.py"):
            (copy / rel).parent.mkdir(parents=True, exist_ok=True)
            (copy / rel).write_text("", encoding="utf-8")
        def plan_of(rows: "list[tuple[str, str, bool]]") -> "object":
            plan = dp.Plan()
            for tag, path, deferred in rows:
                plan.entries[path] = dp.PlanEntry(path=path, tag=tag, deferred_remove=deferred)
            return plan
        in_head = lambda p: p == "a/in_head.py"
        cases: "list[tuple[str, list[tuple[str, str, bool]], list[str], set[str]]]" = [
            ("add 부재", [("add", "a/new.py", False)], [], set()),
            ("add 충돌", [("add", "a/existing.py", False)], ["add 충돌"], set()),
            ("update 실존", [("update", "a/existing.py", False)], [], set()),
            ("update 부재", [("update", "a/ghost.py", False)], ["update 대상 부재"], set()),
            ("update HEAD 실존", [("update", "a/in_head.py", False)], ["update 대상 기준선 이후 실존"], set()),
            ("update 승격 형태", [("update", "a/promo.py", False)], [], {"a/promo.py"}),
            ("update 폴더만(__init__)", [("update", "a/half.py", False)], ["update 대상 부재"], set()),
            ("update 본체만(__init__ 없음)", [("update", "a/half2.py", False)], ["update 대상 부재"], set()),
            ("update 비승격 폴더", [("update", "a/gone_dir.py", False)], ["update 대상 부재"], set()),
            ("remove 실존", [("remove", "a/existing.py", False)], [], set()),
            ("remove 부재", [("remove", "a/ghost.py", False)], ["remove 대상 부재"], set()),
            ("remove@Ln 부재(판정 밖)", [("remove", "a/ghost.py", True)], [], set()),
            ("empty 부재(정상)", [("empty", "a/new2.py", False)], [], set()),
            ("empty 충돌(기준선 실존)", [("empty", "a/existing.py", False)], ["empty 충돌"], set()),
            ("일괄 열거", [("update", "a/g1.py", False), ("remove", "a/g2.py", False), ("add", "a/existing.py", False)],
             ["update 대상 부재", "remove 대상 부재", "add 충돌"], set()),
        ]
        for label, rows, want_kinds, want_promoted in cases:
            plan = plan_of(rows)
            in_baseline = frozenset(p for p in plan.entries if (copy / p).exists())
            errors, promoted = dp.baseline_form_errors(plan, copy, in_baseline, "abc123", in_head)
            kinds = [e.split(":", 1)[0].split("(", 1)[0].strip() for e in errors]
            if kinds != want_kinds or set(promoted) != want_promoted:
                out.append(f"baseline_form_errors[{label}] = {kinds} · promoted {sorted(promoted)} ≠ 기대 "
                           f"{want_kinds} · {sorted(want_promoted)}")
    spec_text: str = (FIXTURES / "green-spec.md").read_text(encoding="utf-8")
    h: str = dp.block_hash(spec_text)
    def head(hh: str, verdict: str, mode: str = "", base: str = "0" * 40) -> str:
        """실행기 자신의 stub writer 로 헤더를 만든다 — 손 합성이 아니라 형식 드리프트에 같이 움직인다(5단계 리뷰 A8)."""
        with tempfile.TemporaryDirectory(prefix="pregate-cr-") as td:
            rp: Path = Path(td) / "r.md"
            dp.write_report_stub(rp, Path("green-spec.md"), "HEAD", base, verdict, [], hh, execution_mode=mode)
            return rp.read_text(encoding="utf-8") + "\n"
    noblock_text: str = (FIXTURES / "noblock-spec.md").read_text(encoding="utf-8")
    red_body: str = ("### 예보 항목 (2건 · 안정 ID = sha256(규칙#+경로)[:12])\n\n- `aaaaaaaaaaaa` [#81] x\n- `bbbbbbbbbbbb` [#267] y\n\n"
                     "### 계약 실존\n\n- `e-cccccccccccc` ⑴ z\n")
    green_v: str = "예보 green — P/S/I급 결정 계약 위반 예보 0(«설계 검증됨» 아님) · 계약 실존 결손 0건(권고·비차단)"
    red_v: str = "예보 red — P/S/I급 결정 계약 위반 예보 2건 · 계약 실존 결손 1건(권고·비차단)"
    coord: str = "\n## pre-gate 처분 라벨 (코디네이터 소유)\n"
    disp = lambda i, label: f"- `{i}` [#x] p → **{label}**(근거)\n"
    cur_digest: str = dp._pregate_digest()
    A40, B40 = "a" * 40, "b" * 40
    rec = lambda sha: f"\n- pre-gate 기준선 — {sha} · 2026-09-27T00:00:00Z\n"
    decl_v: str = "예보 red — P/S/I급 결정 계약 위반 예보 0건 · 선언 확정 1건 · 계약 실존 결손 0건(권고·비차단)"
    decl_body: str = "### 선언 확정 (1건)\n\n- `dddddddddddd` [#574] a/ledger_port.py — LedgerPort.record: 포트 인자\n"
    disp574 = lambda label, rule="#574": f"- `dddddddddddd` [{rule}] a/ledger_port.py → **{label}**(근거)\n"

    def decl_head(rule: str = "#574") -> str:
        """스텁의 빈 «선언 확정» 소절을 선언 확정 1건으로 바꾼다(실행기 writer 형식)."""
        text_: str = head(h, decl_v)
        assert "### 선언 확정 (0건)\n\n- (없음)\n" in text_
        return text_.replace("### 선언 확정 (0건)\n\n- (없음)\n", decl_body.replace("[#574]", f"[{rule}]"))
    rcases: "list[tuple[str, str, int, str]]" = [
        ("green 정합", head(h, green_v), 0, "green"),
        ("stale", head("f" * 12, green_v), 3, "stale"),
        ("형식 red", head(h, "형식 red(블록 부재)"), 3, "형식 red 미해소"),
        ("skip", head(h, "skip"), 0, "skip"),
        ("skip·결손", head(h, "skip · 계약 실존 결손 2건(권고·비차단)"), 0, "실존 결손 2"),
        ("red 미기재", head(h, red_v) + red_body, 3, "처분 미기재 2건"),
        ("red 전건", head(h, red_v) + red_body + coord + disp("aaaaaaaaaaaa", "ignored") + disp("bbbbbbbbbbbb", "filtered"), 0, "처분 전건"),
        ("red corrected 불인정", head(h, red_v) + red_body + coord + disp("aaaaaaaaaaaa", "corrected") + disp("bbbbbbbbbbbb", "filtered"), 3, "미기재 1건"),
        ("이전 절 처분 불인정", head(h, red_v) + red_body + coord + disp("aaaaaaaaaaaa", "ignored") + disp("bbbbbbbbbbbb", "ignored") + head(h, red_v) + red_body, 3, "처분 미기재 2건"),
        ("절 내부 삽입 내성", head(h, red_v).replace("\n- 기준선 SHA:", "\n| 표 | 삽입 |\n|---|---|\n- 기준선 SHA:") + red_body + coord + disp("aaaaaaaaaaaa", "ignored") + disp("bbbbbbbbbbbb", "ignored"), 0, "처분 전건"),
        ("접두 오인 방지(처분 절 헤더)", head(h, green_v) + "\n## pre-gate 예보 처분 정리\n- 기준선 SHA: `x` 블록 해시 ffffffffffff\n- 판정: 형식 red\n", 0, "green"),
        ("e-ID 판독 밖", head(h, red_v) + red_body + coord + disp("aaaaaaaaaaaa", "ignored") + disp("bbbbbbbbbbbb", "filtered"), 0, "실존 결손 1"),
        ("해시 토큰 없음", head(h, green_v).replace(f" · 블록 해시 {h}", ""), 3, "최신성 증명 불가"),
        ("절 부재", "# 리포트\n아무 절도 없다\n", 1, "예보 절 부재"),
        ("타임스탬프 없는 제목은 절이 아님", "\n## pre-gate 예보 — t · s\n\n- 기준선 SHA: `x` 블록 해시 ffffffffffff\n- 판정: 형식 red\n", 1, "예보 절 부재"),
        ("헤더 행 부재", head(h, green_v).replace("- 기준선 SHA:", "- 기준선:"), 1, "헤더 행 부재"),
        # rv3-C ⓔ·ⓡ·ⓢ + 5단계 C 결정 잔여 1
        ("형식 red ∧ stale(사유 2)", head("f" * 12, "형식 red(블록 부재)"), 3, "stale", 2),
        ("같은 ID ignored+corrected → 통과", head(h, red_v) + red_body + coord + disp("aaaaaaaaaaaa", "corrected") + disp("aaaaaaaaaaaa", "ignored") + disp("bbbbbbbbbbbb", "filtered"), 0, "처분 전건"),
        ("ID 행 ≠ 라벨 행(불인정)", head(h, red_v) + red_body + coord + "- `aaaaaaaaaaaa` [#x] p\n  → **ignored**(근거)\n" + disp("bbbbbbbbbbbb", "filtered"), 3, "미기재 1건"),
        ("구형 skip + 마커 없는 명세", None, 3, "블록 부재"),
        # 2026-09-27 로드맵 3 S-4 — 툴체인 최신성(실행 트리 digest)
        ("툴체인 stale", head(h, green_v).replace(f"실행 트리 digest {cur_digest}", "실행 트리 digest " + "0" * 16),
         3, "stale(툴체인)", 1),
        ("digest 토큰 없음(구판 헤더)", head(h, green_v).replace(f" · 실행 트리 digest {cur_digest}", ""),
         3, "툴체인 증명 불가", 1),
        # 로드맵 3 S-1b · 검토 H-M2/H-M3 — 명시 재예보의 기준선 대조 의무 · 새 실행 경계(폴더 재사용)
        ("명시 재예보 · --expect-base 누락", head(h, green_v, "명시 재예보(--base " + "0" * 40 + ")"),
         3, "기준선 대조 누락", 1),
        ("앞 실행 예보 · 명세 불변(옛 digest·명시 재예보여도 정합)",
         head(h, green_v, "명시 재예보(--base " + "0" * 40 + ")").replace(f"실행 트리 digest {cur_digest}",
                                                                        "실행 트리 digest " + "0" * 16)
         + "\n- 실행 경계 — 새 실행 G0 승인 2026-09-26T16:00:00Z\n", 0, "앞 실행 예보(명세 불변)"),
        ("앞 실행 예보 · 명세 변경", head("f" * 12, green_v) + "\n- 실행 경계 — 새 실행 G0 승인 2026-09-26T16:00:00Z\n",
         3, "stale"),
        # 검토 I-M1 — `--base` 를 빼고 HEAD 로 다시 돌린 재발화 · 리포트 `pre-gate 기준선` 행 대조(플래그 무관)
        ("I-M1 명시→HEAD 판형 · 기준선 행 없음", head(h, green_v, f"명시 재예보(--base {A40})", A40) + head(h, green_v, base=B40),
         3, "기준선 대조 누락", 1),
        ("I-M1 명시→HEAD 판형 · 기준선 행 있음", head(h, green_v, base=A40) + rec(A40)
         + head(h, green_v, f"명시 재예보(--base {A40})", A40) + head(h, green_v, base=B40), 3, "기준선 치환", 1),
        ("기준선 행 · 명시 재예보 일치", head(h, green_v, base=A40) + rec(A40) + head(h, green_v, f"명시 재예보(--base {A40})", A40),
         0, "green"),
        ("기준선 행만 · Phase 1 마지막 절 일치", head(h, green_v, base=A40) + rec(A40), 0, "green"),
        ("기준선 행 · Phase 1 마지막 절 불일치", head(h, green_v, base=B40) + rec(A40), 3, "기준선 치환", 1),
        ("기준선 행 중복", head(h, green_v, base=A40) + rec(A40) + rec(A40), 3, "기준선 행 중복", 1),
        ("기준선 행 형식 불비", head(h, green_v, base=A40) + "- pre-gate 기준선 — HEAD\n", 3, "기준선 행 형식 불비", 1),
        ("경계 앞 기준선 행은 이번 실행 밖", head(h, green_v, base=A40) + rec(A40)
         + "\n- 실행 경계 — 실행 · G0 승인 20260927-0100 · 2026-09-26T16:00:00Z\n" + head(h, green_v, base=B40), 0, "green"),
        # 검토 I-m4 — 선언 확정 #574 의 filtered 는 기계로 불인정
        ("#574 filtered 불인정", decl_head() + coord + disp574("filtered"), 3, "#574 는 filtered 불인정", 1),
        ("#574 ignored 인정", decl_head() + coord + disp574("ignored"), 0, "처분 전건"),
        ("#574 외 선언 확정은 filtered 인정", decl_head("#197") + coord + disp574("filtered", "#197"), 0, "처분 전건"),
    ]
    for case in rcases:
        label, text, want_code, needle = case[:4]
        want_n: "int | None" = case[4] if len(case) > 4 else None
        if text is None:  # 구형 명세(마커 0) + 관찰기 skip 스텁이 마지막 절 — 소급 블록 후 재발화 강제
            code, problems, info = dp.check_report(noblock_text, head(dp.block_hash(noblock_text), "skip"))
        else:
            code, problems, info = dp.check_report(spec_text, text)
        blob: str = " ".join(problems) + " " + " ".join(info.values())
        if code != want_code or needle not in blob or (want_n is not None and len(problems) != want_n):
            out.append(f"check_report[{label}] = exit {code} · {problems} · {info.get('short')} ≠ 기대 exit {want_code}·«{needle}»"
                       + (f"·사유 {want_n}" if want_n is not None else ""))
    # 검토 I-m1 — 앞 실행 예보 정합은 대조 생략을 요약에 밝힌다(`--expect-base` 를 줘도 조용히 넘기지 않는다)
    prior_text: str = head(h, green_v) + "\n- 실행 경계 — 실행 · G0 승인 20260927-0100 · 2026-09-26T16:00:00Z\n"
    code_p, _probs_p, info_p = dp.check_report(spec_text, prior_text, expect_base="c" * 12)
    if code_p != 0 or "대조 생략" not in info_p.get("short", "") or "미대조" not in info_p.get("short", ""):
        out.append(f"check_report[앞 실행 · --expect-base 미대조 표기] = exit {code_p} · {info_p.get('short')}")
    # 로드맵 3 S-4: digest 는 판정 입력만 본다 — rulepack.json(그래프 명칭 투영물) 변경은 무반응 · 검사기 변경은 반응
    with tempfile.TemporaryDirectory(prefix="pregate-digest-") as td:
        copy_dir: Path = Path(td) / "scripts"
        shutil.copytree(EXECUTOR.parent, copy_dir, ignore=shutil.ignore_patterns("__pycache__"))
        saved_dir: Path = dp.SCRIPTS_DIR
        try:
            dp.SCRIPTS_DIR = copy_dir
            base_d: str = dp._pregate_digest()
            (copy_dir / "rulepack.json").write_text("{}", encoding="utf-8")
            rulepack_d: str = dp._pregate_digest()
            checker: Path = sorted(copy_dir.glob("check-*.py"))[0]
            checker.write_text(checker.read_text(encoding="utf-8") + "\n# touched\n", encoding="utf-8")
            checker_d: str = dp._pregate_digest()
        finally:
            dp.SCRIPTS_DIR = saved_dir
        if base_d != cur_digest or rulepack_d != base_d or checker_d == base_d:
            out.append(f"_pregate_digest 판정 입력 범위 위반 — 사본 {base_d} · 현재 {cur_digest} · rulepack 변경 뒤 "
                       f"{rulepack_d} · 검사기 변경 뒤 {checker_d}(rulepack 무반응 · 검사기 반응이어야 한다)")
    return out


def _in_argument_unit_checks() -> "list[str]":
    """로드맵 3 S-2(F4-22) — 포트 인자 `<data>_in` 의 #574 예보. 현장형(같은 폴더 import 행 없음) 양성 · `_out` 개명 ·
    반환 중계 · 필드 중계 · update 부분 선언(실물 반환 유지) · 손대지 않은 legacy · 해소 불능 반환(후보) · framework 포트."""
    dp = _load_module(EXECUTOR, "_design_pregate_s2")
    out: "list[str]" = []
    port = "application/billing/application_layer/port/ledger"

    def spec(plan: "list[str]", symbols: "list[str]") -> str:
        return ("# s2\n\n<!-- machine: file-plan -->\n```paths\n" + "\n".join(plan) + "\n```\n\n"
                "<!-- machine: symbols -->\n```symbols\n" + "\n".join(symbols) + "\n```\n")

    def run(label: str, text: str, real: "dict[str, str]", want: "list[tuple[str, bool]]") -> None:
        plan, errors = dp.parse_spec(text)
        if errors or plan is None:
            out.append(f"S-2[{label}] 명세 파싱 실패: {errors}")
            return
        with tempfile.TemporaryDirectory(prefix="pregate-s2-") as td:
            copy = Path(td)
            for rel, body in real.items():
                (copy / rel).parent.mkdir(parents=True, exist_ok=True)
                (copy / rel).write_text(body, encoding="utf-8")
            got = [(f.owner, f.confirmed) for f in dp.check_in_argument_forecast(plan, copy)]
        if got != want:
            out.append(f"S-2[{label}] = {got} ≠ 기대 {want}")

    run("현장형 양성(import 행 없음)", spec(
        [f"add\t{port}/ledger_port.py", f"add\t{port}/entry_in.py"],
        [f"{port}/entry_in.py::EntryIn {{amount: int}}", f"{port}/ledger_port.py::LedgerPort(ABC) {{}}",
         f"{port}/ledger_port.py::LedgerPort.record(self, entry: EntryIn) -> None"]), {},
        [("LedgerPort.record", True)])
    run("컨테이너 안(tuple[XIn, ...])", spec(
        [f"add\t{port}/ledger_port.py", f"add\t{port}/entry_in.py"],
        [f"{port}/entry_in.py::EntryIn {{amount: int}}", f"{port}/ledger_port.py::LedgerPort(ABC) {{}}",
         f"{port}/ledger_port.py::LedgerPort.record_many(self, entries: tuple[EntryIn, ...]) -> None"]), {},
        [("LedgerPort.record_many", True)])
    run("_out 개명(음성)", spec(
        [f"add\t{port}/ledger_port.py", f"add\t{port}/entry_out.py"],
        [f"{port}/entry_out.py::EntryOut {{amount: int}}", f"{port}/ledger_port.py::LedgerPort(ABC) {{}}",
         f"{port}/ledger_port.py::LedgerPort.record(self, entry: EntryOut) -> None"]), {}, [])
    run("반환 중계(음성)", spec(
        [f"add\t{port}/ledger_port.py", f"add\t{port}/entry_in.py"],
        [f"{port}/entry_in.py::EntryIn {{amount: int}}", f"{port}/ledger_port.py::LedgerPort(ABC) {{}}",
         f"{port}/ledger_port.py::LedgerPort.fetch(self) -> EntryIn",
         f"{port}/ledger_port.py::LedgerPort.record(self, entry: EntryIn) -> None"]), {}, [])
    run("필드 중계(음성)", spec(
        [f"add\t{port}/ledger_port.py", f"add\t{port}/page_in.py", f"add\t{port}/item_in.py"],
        [f"{port}/item_in.py::ItemIn {{x: int}}", f"{port}/page_in.py::PageIn {{items: tuple[ItemIn, ...]}}",
         f"{port}/ledger_port.py::LedgerPort(ABC) {{}}",
         f"{port}/ledger_port.py::LedgerPort.search(self) -> PageIn",
         f"{port}/ledger_port.py::LedgerPort.detail(self, item: ItemIn) -> None"]), {}, [])
    real_port = ("from abc import ABC\n\nfrom application.billing.application_layer.port.ledger.entry_in import EntryIn\n\n\n"
                 "class LedgerPort(ABC):\n    def get(self) -> EntryIn: ...\n")
    real_in = "class EntryIn:\n    amount: int\n"
    run("update 부분 선언 — 실물 반환 유지(음성)", spec(
        [f"update\t{port}/ledger_port.py"],
        [f"{port}/ledger_port.py::LedgerPort(ABC) {{}}",
         f"{port}/ledger_port.py::LedgerPort.put(self, item: EntryIn) -> None"]),
        {f"{port}/ledger_port.py": real_port, f"{port}/entry_in.py": real_in}, [])
    legacy_port = ("from abc import ABC\n\nfrom application.billing.application_layer.port.ledger.entry_in import EntryIn\n\n\n"
                   "class LedgerPort(ABC):\n    def put(self, item: EntryIn) -> None: ...\n")
    run("손대지 않은 legacy 메서드(음성)", spec(
        [f"update\t{port}/ledger_port.py"],
        [f"{port}/ledger_port.py::LedgerPort(ABC) {{}}", f"{port}/ledger_port.py::LedgerPort.touch(self) -> None",
         f"{port}/ledger_port.py::LedgerPort.put(self, item: EntryIn) -> None"]),
        {f"{port}/ledger_port.py": legacy_port, f"{port}/entry_in.py": real_in}, [])
    run("typing 컨테이너 반환 중계(import 행 없음 · 음성)", spec(
        [f"add\t{port}/ledger_port.py", f"add\t{port}/z_in.py"],
        [f"{port}/z_in.py::ZIn {{v: int}}", f"{port}/ledger_port.py::LedgerPort(ABC) {{}}",
         f"{port}/ledger_port.py::LedgerPort.stream(self) -> Iterator[ZIn]",
         f"{port}/ledger_port.py::LedgerPort.push(self, z: ZIn) -> None"]), {}, [])
    run("해소 불능 반환 안의 같은 이름(후보)", spec(
        [f"add\t{port}/ledger_port.py", f"add\t{port}/z_in.py"],
        [f"{port}/z_in.py::ZIn {{v: int}}", f"{port}/ledger_port.py::LedgerPort(ABC) {{}}",
         f"{port}/ledger_port.py::LedgerPort.stream(self) -> Page[ZIn]",
         f"{port}/ledger_port.py::LedgerPort.push(self, z: ZIn) -> None"]), {}, [("LedgerPort.push", False)])
    # 검토 I-m2 — typing 컨테이너 인자(import 행 없음)도 잎까지 본다
    for head_, ann in (("Optional", "Optional[EntryIn]"), ("Sequence", "Sequence[EntryIn]"),
                       ("Mapping", "Mapping[str, EntryIn]"), ("Annotated", "Annotated[EntryIn, 'x']")):
        run(f"{head_} 인자(양성)", spec(
            [f"add\t{port}/ledger_port.py", f"add\t{port}/entry_in.py"],
            [f"{port}/entry_in.py::EntryIn {{amount: int}}", f"{port}/ledger_port.py::LedgerPort(ABC) {{}}",
             f"{port}/ledger_port.py::LedgerPort.record(self, entry: {ann}) -> None"]), {},
            [("LedgerPort.record", True)])
    other = "application/billing/application_layer/port/other"
    run("다른 폴더의 동명 반환은 중계가 아니다(양성)", spec(
        [f"add\t{port}/ledger_port.py", f"add\t{port}/entry_in.py", f"add\t{other}/other_port.py",
         f"add\t{other}/entry_in.py"],
        [f"{port}/entry_in.py::EntryIn {{amount: int}}", f"{other}/entry_in.py::EntryIn {{v: int}}",
         f"{other}/other_port.py::OtherPort(ABC) {{}}", f"{other}/other_port.py::OtherPort.get(self) -> EntryIn",
         f"{port}/ledger_port.py::LedgerPort(ABC) {{}}",
         f"{port}/ledger_port.py::LedgerPort.record(self, entry: EntryIn) -> None"]), {},
        [("LedgerPort.record", True)])
    # 검토 I-m3 — legacy 의 기존 `_in` 인자는 빚(문면 차이·서명의 다른 변경 무관) · 새로 들이는 `_in` 인자만 예보
    str_legacy = legacy_port.replace("item: EntryIn", "item: 'EntryIn'")
    run("legacy 문자열 주석(음성)", spec(
        [f"update\t{port}/ledger_port.py"],
        [f"{port}/ledger_port.py::LedgerPort(ABC) {{}}",
         f"{port}/ledger_port.py::LedgerPort.put(self, item: EntryIn) -> None"]),
        {f"{port}/ledger_port.py": str_legacy, f"{port}/entry_in.py": real_in}, [])
    run("legacy 서명 변경 · 기존 _in 인자 유지(음성)", spec(
        [f"update\t{port}/ledger_port.py"],
        [f"{port}/ledger_port.py::LedgerPort(ABC) {{}}",
         f"{port}/ledger_port.py::LedgerPort.put(self, item: EntryIn, *, force: bool = False) -> None"]),
        {f"{port}/ledger_port.py": legacy_port, f"{port}/entry_in.py": real_in}, [])
    run("legacy 에 새 _in 인자(양성)", spec(
        [f"update\t{port}/ledger_port.py", f"add\t{port}/extra_in.py"],
        [f"{port}/extra_in.py::ExtraIn {{v: int}}", f"{port}/ledger_port.py::LedgerPort(ABC) {{}}",
         f"{port}/ledger_port.py::LedgerPort.put(self, item: EntryIn, extra: ExtraIn) -> None"]),
        {f"{port}/ledger_port.py": legacy_port, f"{port}/entry_in.py": real_in}, [("LedgerPort.put", True)])
    fw = "framework/notify"
    run("framework 포트(양성)", spec(
        [f"add\t{fw}/notify_port.py", f"add\t{fw}/message_in.py"],
        [f"{fw}/message_in.py::MessageIn {{body: str}}", f"{fw}/notify_port.py::NotifyPort(ABC) {{}}",
         f"{fw}/notify_port.py::NotifyPort.send(self, message: MessageIn) -> None"]), {},
        [("NotifyPort.send", True)])
    return out


def _run_execution_modes_bundle(scratch: Path, failures: list[str]) -> None:
    """12 CLI combinations retain tag semantics and explain initial versus explicit reforecast."""
    for baseline in (False, True):
        repo = _make_repo(scratch, f'modes-{baseline}')
        target = repo / MID_ADD
        target.parent.mkdir(parents=True, exist_ok=True)
        original = 'class LaneMarker:\n    value: str\n'
        target.write_text(original)
        if baseline:
            _git(repo, 'add', '-A')
            _git(repo, 'commit', '-qm', 'mode baseline')
        for tag in ('add', 'empty', 'update'):
            for explicit in (False, True):
                spec = scratch / 'mode-spec.md'
                spec.write_text('<!-- machine: file-plan -->\n```paths\n' + f'{tag} {MID_ADD}\n```\n'
                    '<!-- machine: symbols -->\n```symbols\n' + (f'{MID_ADD}::LaneMarker {{value: str}}\n'
                    if tag == 'add' else '') + '```\n')
                report = scratch / f'mode-{baseline}-{tag}-{explicit}.md'
                run = _run_pregate(spec, repo, report, ['--base', 'HEAD'] if explicit else [])
                expected = (4 if tag == 'update' else 3) if baseline else (3 if tag == 'update' or not explicit else 0)
                label = f'mode baseline={baseline} tag={tag} explicit={explicit}'
                text = report.read_text() if report.exists() else ''
                mode = '명시 재예보(--base HEAD)' if explicit else '초기 예보(기준선 기본 HEAD)'
                cause = ('기준선 실존' if baseline else '기준선 부재·오버레이 실존') if tag == 'add' else ''
                if run.returncode != expected or mode not in run.stdout or mode not in text:
                    failures.append(f'{label}: exit {run.returncode} != {expected} or missing execution mode\n{run.stdout}{run.stderr}')
                if expected == 3 and cause and cause not in text:
                    failures.append(f'{label}: missing specific cause {cause}')
                if tag == 'update' and not baseline and not all(x in text for x in ('초기 예보', '재예보')):
                    failures.append(f'{label}: absent update needs both execution purposes')
                if '승인 제품 변경' not in text or '작업 기록' not in text:
                    failures.append(f'{label}: file-plan scope guidance absent')
                if target.read_text() != original:
                    failures.append(f'{label}: source bytes changed')
                print(f'{label}: exit {run.returncode} (expected {expected})')


# 묶음 stub — 재수출만 하는 어댑터 패키지 `__init__.py` 스텁의 머리(#640 거짓 red 수리 · 진탐 유지).
STUB_INIT: str = "application/orders/driven_layer/adapter/clock/system_adapter/__init__.py"
STUB_INIT_640: str = f"[#640] {STUB_INIT}: 어댑터 패키지의 `__init__.py` 는 재수출 전용이다"
STUB_REEXPORT: str = "from .adapter.system_clock_adapter import SystemClockAdapter as SystemClockAdapter"
# (명세, exit, 예보 항목 문구 조각들) — 조각마다 예보 항목 한 줄에 정확히 대응한다(건수 = 조각 수).
STUB_CASES: "tuple[tuple[str, int, tuple[str, ...]], ...]" = (
    ("stub-adapter-init-spec", 0, ()),                       # 재수출 한 줄 — 머리 future 줄 빼 0
    ("stub-adapter-init-dotpath-spec", 0, ()),               # 경로 `./application/…` — 정규화 마디로 판정
    ("stub-adapter-init-dslash-spec", 0, ()),                # 경로 겹친 `/` — 같음
    ("stub-adapter-init-empty-spec", 0, ()),                 # `empty` — 무변
    ("stub-adapter-init-future-spec", 2, (STUB_INIT_640,)),  # 전사에 future 명시 — 머리 그대로(진탐)
    ("stub-adapter-init-red-spec", 2, (STUB_INIT_640,)),     # `__init__.py` 에 클래스 — 진탐
    ("stub-adapter-init-alias-spec", 2, (STUB_INIT_640,      # 타입 없는 별칭 — 진탐 + 별칭 첫 대입 타입 없음
                                         f"[#493] {STUB_INIT}:N: 모듈 변수 `DefaultClock` 의 첫 대입에 타입이 없다")),
    ("stub-adapter-init-alias-typed-spec", 2, (STUB_INIT_640,)),  # 타입 붙은 별칭 — 진탐
    ("stub-adapter-init-alias-tc-spec", 2, (STUB_INIT_640,)),     # TYPE_CHECKING 별칭 쌍 — 진탐
    ("stub-adapter-init-raises-spec", 2, (STUB_INIT_640,)),       # exception-map 창구 — 진탐
)
# 실체화한 `__init__.py` 스텁 원문(--keep 사본) — 재수출만이면 docstring + 전사, 전사에 future 가 있으면 머리 그대로.
STUB_INIT_TEXT: "dict[str, str]" = {
    "stub-adapter-init-spec": f'"""pre-gate 팬텀 스텁."""\n\n{STUB_REEXPORT}\n\n',
    "stub-adapter-init-dotpath-spec": f'"""pre-gate 팬텀 스텁."""\n\n{STUB_REEXPORT}\n\n',
    "stub-adapter-init-future-spec": f'"""pre-gate 팬텀 스텁."""\nfrom __future__ import annotations\n\n{STUB_REEXPORT}\n\n',
}


# 재료 파일 스텁 글 대조 — `render_stub` 직접(검사기 · 합성 저장소 무관 · 그래서 검사기 판과 무관하게 같은 기대).
STUB_MATERIAL: str = "application/orders/composition_root/wiring_material.py"
STUB_MATERIAL_BODY: str = "return settings.PREGATE_STUB"
# (명세, 계획 경로(정규화), 꼴) — 꼴: canonical(정형 본문 · plain settings 결속 정확히 한 번) · alias(정형 본문 · 보충 0) ·
# nofunc(함수 · django.conf import 0) · plain(재료 파일 아님 — `raise NotImplementedError` · 보충 0).
STUB_MATERIAL_CASES: "tuple[tuple[str, str, str], ...]" = (
    ("stub-material-spec", STUB_MATERIAL, "canonical"),                    # 전사 settings 있음
    ("stub-material-nosettings-spec", STUB_MATERIAL, "canonical"),         # 전사 settings 없음 → 한 줄 보충
    ("stub-material-settings-paren-spec", STUB_MATERIAL, "canonical"),     # `import (settings)` — 구문으로 같은 결속
    ("stub-material-settings-space-spec", STUB_MATERIAL, "canonical"),     # 겹친 공백 — 같음
    ("stub-material-dotpath-spec", STUB_MATERIAL, "canonical"),            # `./application/…` — 정규화 마디
    ("stub-material-dslash-spec", STUB_MATERIAL, "canonical"),             # 겹친 `/` — 같음
    ("stub-material-settings-alias-spec", STUB_MATERIAL, "alias"),         # `settings as s` — 보충하지 않음
    ("stub-material-nofunc-spec", STUB_MATERIAL, "nofunc"),                # 함수 symbol 없음 — 보충하지 않음
    ("stub-material-elsewhere-spec", "application/orders/composition_root/legacy/wiring_material.py", "plain"),
    ("stub-material-elsewhere-spec", "application/orders/domain_layer/wiring_material.py", "plain"),
)
# 원문 표기가 남는지(전사 그대로) — 보충 꼴은 보충 줄 원문이 정확히 한 번.
STUB_MATERIAL_RAW: "dict[str, str]" = {
    "stub-material-spec": "from django.conf import settings",
    "stub-material-nosettings-spec": "from django.conf import settings",
    "stub-material-settings-paren-spec": "from django.conf import (settings)",
    "stub-material-settings-space-spec": "from  django.conf  import settings",
    "stub-material-settings-alias-spec": "from django.conf import settings as s",
}


def _stub_material_text_checks() -> "list[str]":
    """재료 파일 정형 스텁의 글 — 본문 = docstring + `return settings.PREGATE_STUB` · plain settings 결속 한 번 ·
    별칭 · 함수 없는 꼴 보충 0 · 정규화 경로(`./` · 겹친 `/`)에서 맨 경로와 같은 글 · 재료 자리 밖은 지금 스텁 그대로."""
    import ast as _ast
    from pathlib import PurePosixPath as _P
    dp: "types.ModuleType" = _load_module(EXECUTOR, "_pregate_stub_material")
    out: "list[str]" = []
    texts: "dict[str, str]" = {}

    def binds(tree: "_ast.Module") -> "tuple[int, int]":
        plain = other = 0
        for node in tree.body:
            if isinstance(node, _ast.ImportFrom) and node.module == "django.conf":
                for alias in node.names:
                    if alias.name == "settings" and alias.asname is None:
                        plain += 1
                    else:
                        other += 1
        return plain, other

    for name, rel, kind in STUB_MATERIAL_CASES:
        label: str = f"[stub 재료 글] {name} · {rel}"
        plan, errors = dp.parse_spec((FIXTURES / f"{name}.md").read_text(encoding="utf-8"))
        entries = [e for k, e in (plan.entries.items() if plan else []) if _P(k).parts == _P(rel).parts]
        if errors or len(entries) != 1:
            out.append(f"{label}: 파싱 오류 {errors} · 정규화 경로 대응 {len(entries)}개(기대 1)")
            continue
        text: str = dp.render_stub(entries[0])
        texts[name] = text
        try:
            tree: "_ast.Module" = _ast.parse(text)
        except SyntaxError as exc:
            out.append(f"{label}: 스텁이 파싱되지 않는다 — {exc}")
            continue
        funcs = [n for n in tree.body if isinstance(n, _ast.FunctionDef)]
        plain, other = binds(tree)
        body: "list[str]" = ([_ast.unparse(s) for s in funcs[0].body] if len(funcs) == 1 else [])
        doc_ok: bool = len(funcs) == 1 and _ast.get_docstring(funcs[0]) == "계획 스텁."
        if kind in ("canonical", "alias"):
            if not (doc_ok and len(body) == 2 and body[1] == STUB_MATERIAL_BODY):
                out.append(f"{label}: 본문이 docstring + `{STUB_MATERIAL_BODY}` 가 아니다 — {body}")
        if kind == "canonical" and (plain, other) != (1, 0):
            out.append(f"{label}: `from django.conf import settings` 결속 {plain}번 · 다른 꼴 {other}번(기대 1 · 0)")
        if kind == "alias" and (plain, other) != (0, 1):
            out.append(f"{label}: 별칭 꼴에 보충이 생겼다 — plain {plain} · 별칭 {other}(기대 0 · 1)")
        if kind == "nofunc" and (funcs or plain or other):
            out.append(f"{label}: 함수 없는 재료 파일에 함수 {len(funcs)} · django.conf import {plain + other}(기대 0 · 0)")
        if kind == "plain" and not (doc_ok and len(body) == 2 and body[1] == "raise NotImplementedError" and (plain, other) == (0, 0)):
            out.append(f"{label}: 재료 자리 밖인데 정형이 붙었다 — 본문 {body} · django.conf import {plain + other}")
        raw: "str | None" = STUB_MATERIAL_RAW.get(name)
        if raw is not None and text.splitlines().count(raw) != 1:
            out.append(f"{label}: 전사 원문 `{raw}` 줄이 정확히 한 번이 아니다({text.splitlines().count(raw)})")
    for name in ("stub-material-dotpath-spec", "stub-material-dslash-spec"):
        if name in texts and texts[name] != texts.get("stub-material-spec"):
            out.append(f"[stub 재료 글] {name}: 정규화 경로의 스텁이 맨 경로와 다르다")
    if not out:
        print(f"stub 재료 파일 스텁 글 대조 {len(STUB_MATERIAL_CASES)}칸 — 기대 일치")
    return out


def _kept_text(proc: "subprocess.CompletedProcess[str]", rel: str) -> "str | None":
    """`--keep` 사본의 계획 경로 원문(없으면 None) — 사본은 읽은 뒤 지운다."""
    m: "re.Match[str] | None" = _KEEP_RE.search(proc.stdout)
    if m is None:
        return None
    kept: Path = Path(m.group(1))
    try:
        target: Path = kept / "copy" / rel
        return target.read_text(encoding="utf-8") if target.is_file() else None
    finally:
        shutil.rmtree(kept, ignore_errors=True)


def _run_stub_bundle(scratch: Path, failures: "list[str]") -> None:
    """스텁 정형 — 재료 파일 스텁 글 대조(`render_stub` 직접) + 재수출 `__init__.py` 머리(합성 저장소 1 =
    `mini_repo` + `stub_overlay/`: 포트 · #488 고정 칸 · 리포트 1(헤더 = 사례 수))."""
    failures.extend(_stub_material_text_checks())
    repo: Path = scratch / "repo-stub"
    shutil.copytree(FIXTURES / "mini_repo", repo)
    shutil.copytree(FIXTURES / "stub_overlay", repo, dirs_exist_ok=True)
    _git(repo, "init", "-q")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "fixture-baseline+stub-overlay")
    report: Path = scratch / "pregate-report-stub.md"
    for name, want_exit, want_items in STUB_CASES:
        keep: bool = name in STUB_INIT_TEXT
        proc: "subprocess.CompletedProcess[str]" = _run_pregate(FIXTURES / f"{name}.md", repo, report,
                                                                ["--keep"] if keep else None)
        items: "list[str]" = [ln.strip() for ln in proc.stdout.splitlines() if re.match(r"^\s*`[0-9a-f]{12}` ", ln)]
        bad_before: int = len(failures)
        if proc.returncode != want_exit:
            failures.append(f"[stub] {name} 기대 exit {want_exit} ≠ 실측 {proc.returncode}")
        if len(items) != len(want_items) or any(sum(piece in it for it in items) != 1 for piece in want_items):
            failures.append(f"[stub] {name} 예보 항목 {items} ≠ 기대 조각 {list(want_items)}")
        if keep:
            text: "str | None" = _kept_text(proc, STUB_INIT)
            if text != STUB_INIT_TEXT[name]:
                failures.append(f"[stub] {name} `__init__.py` 스텁 원문 {text!r} ≠ 기대 {STUB_INIT_TEXT[name]!r}")
        if len(failures) > bad_before:
            _dump(f"stub {name}", proc)
        else:
            print(f"stub {name}: exit {proc.returncode} · 예보 {len(items)}건 — 기대 일치")
    if _header_count(report) != len(STUB_CASES):
        failures.append(f"[stub] 리포트 append 횟수 {_header_count(report)} ≠ 기대 {len(STUB_CASES)}")


# 묶음 stub-material — D17 소유 · #652: 재료 파일(`composition_root/wiring_material.py`) 스텁의 검사기 귀속.
# 재료 파일 규칙 #652 · 그 트리 칸이 있는 검사기 판(D17 이후)에서만 선다 — 스텁 글 대조(`_stub_material_text_checks`)와 달리
# 검사기 결과를 단언한다. 합성 저장소 = `mini_repo` + `stub_overlay/` + `stub_material_overlay/`(값 객체 `LanguageCode`).
STUB_MATERIAL_652: str = f"[#652] {STUB_MATERIAL}:N: wiring_material.py 는 결선 재료만 둔다 — `default_language` 의 "
STUB_MATERIAL_CHECKER_CASES: "tuple[tuple[str, int, tuple[str, ...]], ...]" = (   # D17 소유 · #652
    ("stub-material-spec", 0, ()),                     # P1 재료 함수 `-> LanguageCode` · 전사 settings — 정형 본문으로 0
    ("stub-material-badret-spec", 2, (STUB_MATERIAL_652 + "반환 주석이 F2 클래스 이름 하나 또는 str · int · bool · float 가 아니다(F3)",)),
    ("stub-material-nosettings-spec", 0, ()),          # P1′ settings 전사 없음 — 보충 한 줄
    ("stub-material-settings-paren-spec", 0, ()),      # P1″a `import (settings)` — 구문으로 같은 결속 · 보충 없음
    ("stub-material-settings-space-spec", 0, ()),      # P1″b 겹친 공백 — 같음
    ("stub-material-dotpath-spec", 0, ()),             # P1-dot `./application/…` — 정규화 마디
    ("stub-material-dslash-spec", 0, ()),              # P1-dslash 겹친 `/` — 같음
)


def _run_stub_material_bundle(scratch: Path, failures: "list[str]") -> None:
    """D17 소유 · #652 — 재료 파일 스텁이 #652 «본문 꼴» 거짓 red 를 내지 않고(0), 진짜 위반(반환 주석 `dict`)은
    다음 탈락 문구로 남는지(1건) 검사기로 본다. 합성 저장소 1 · 리포트 1(헤더 = 사례 수 7)."""
    repo: Path = scratch / "repo-stub-material"
    shutil.copytree(FIXTURES / "mini_repo", repo)
    shutil.copytree(FIXTURES / "stub_overlay", repo, dirs_exist_ok=True)
    shutil.copytree(FIXTURES / "stub_material_overlay", repo, dirs_exist_ok=True)
    _git(repo, "init", "-q")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "fixture-baseline+stub-overlay+stub-material-overlay")
    report: Path = scratch / "pregate-report-stub-material.md"
    for name, want_exit, want_items in STUB_MATERIAL_CHECKER_CASES:
        proc: "subprocess.CompletedProcess[str]" = _run_pregate(FIXTURES / f"{name}.md", repo, report)
        items: "list[str]" = [ln.strip() for ln in proc.stdout.splitlines() if re.match(r"^\s*`[0-9a-f]{12}` ", ln)]
        bad_before: int = len(failures)
        if proc.returncode != want_exit:
            failures.append(f"[stub-material · D17 #652] {name} 기대 exit {want_exit} ≠ 실측 {proc.returncode}")
        if len(items) != len(want_items) or any(sum(piece in it for it in items) != 1 for piece in want_items):
            failures.append(f"[stub-material · D17 #652] {name} 예보 항목 {items} ≠ 기대 조각 {list(want_items)}")
        if len(failures) > bad_before:
            _dump(f"stub-material {name}", proc)
        else:
            print(f"stub-material(D17 #652) {name}: exit {proc.returncode} · 예보 {len(items)}건 — 기대 일치")
    if _header_count(report) != len(STUB_MATERIAL_CHECKER_CASES):
        failures.append(f"[stub-material · D17 #652] 리포트 append 횟수 {_header_count(report)} ≠ 기대 {len(STUB_MATERIAL_CHECKER_CASES)}")


def main(argv: "list[str]") -> int:
    ap: argparse.ArgumentParser = argparse.ArgumentParser(description="pre-gate 픽스처 러너")
    ap.add_argument("--keep", action="store_true", help="합성 저장소 보존(디버그)")
    ns: argparse.Namespace = ap.parse_args(argv)

    scratch: Path = Path(tempfile.mkdtemp(prefix="pregate-fixture-"))
    failures: "list[str]" = []
    failures.extend(_unit_checks())
    failures.extend(_existence_unit_checks())
    failures.extend(_enforce_unit_checks())
    failures.extend(_in_argument_unit_checks())
    try:
        _run_execution_modes_bundle(scratch, failures)
        _run_base_bundle(scratch, failures)
        _run_p1_bundle(scratch, failures)
        _run_mid_bundle(scratch, failures)
        _run_imports_bundle(scratch, failures)
        _run_enforce_bundle(scratch, failures)
        _run_checkreport_bundle(scratch, failures)
        _run_inflow_bundle(scratch, failures)
        _run_stub_bundle(scratch, failures)
        _run_stub_material_bundle(scratch, failures)      # D17 소유 · #652

        if failures:
            print("\nFAIL — pre-gate 픽스처 기대 불일치:")
            for f in failures:
                print(f"  - {f}")
            return 1
        print("\nPASS — pre-gate 픽스처 15종+E 계열 6단계+유닛 기대 일치 "
              "(green×3 예보 0 · 형식 red exit 3 · red 귀속 3건·red2 귀속 2건 정합 · 재발화 판형 E1~E4+E1′/E2′ · "
              "계약 실존 imports 3종 exit 0/5/5 · 차단 모드 enforce 7(블록 부재·공허·update/remove 부재·승격 예외) · "
              "--check-report 14단계 + 유닛 매트릭스 · 스텁 정형 stub 10 + 재료 글 10(재수출 __init__ 0 · 진탐 #640 유지 · 재료 정형 본문) · "
              "stub-material 7(D17 #652 — 재료 0 · 반환 주석 진탐 1))")
        return 0
    finally:
        if ns.keep:
            print(f"(--keep) 합성 저장소 보존: {scratch}")
        else:
            shutil.rmtree(scratch, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
