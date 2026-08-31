#!/usr/bin/env python3
"""dddjango 이름 규율 검사기 — 약어·접두/접미·패턴 낱말·어드민 자리(D9·D21·D33·D41).

담당 규칙 (rule-owner-map · 총 32 — #343 은 admin 가족이라 keyword 오배정을 이관받았다):
  #28  [path] 원전 패턴 약어 금지 — {repo,uow,acl,vo,ohs,agg,spec,svc,ctrl,impl,mgr,cfg,
              service(단독 토큰)} · 예외는 #148 의 `api`.
  #30  [path] 자리표시자 이름 파일의 접미 — `<value_object>.py` 류 «서술문·자리표시자»
              자리에 종류 접미를 «다시» 달면(`_value_object.py`·`_entity.py`) 위반.
  #33  [path] 파일 stem 첫 토큰이 트리 폴더 이름인데 조상에 그 폴더가 없으면 위반.
  #34  [path] 같은 접두 = 같은 스코프 — `<use_case>_command/_query/_result` 는 유스케이스
              폴더와 stem 이 일치, `schema_in/out` 은 `schema/` 직계.
  #36  [ast+] 정도 낱말 칸 금지 — 확정: {common,shared,base,core,util(s),helper(s),misc,
              etc,general,lib,support}(트리 고정 칸 제외) / 후보: 트리·기술·
              업무 어휘 어디에도 없는 단독 낱말 칸(「판정이 되는 물음이 붙나」).
  #41  [path] Port·Adapter·Gateway 는 폴더 이름에 안 온다(`*_port/`·`*_adapter/`·
              `*_gateway/`·`gateway/`) — 파일이 접미로 종류를 진다.
  #43  [ast]  패턴 낱말은 능력 이름에 안 온다 — 클래스 이름 «중간»의 Port/Adapter/Gateway.
  #44  [path] 도메인 서비스 이름이 같은 BC 값 객체와 겹치면 행위 이름으로.
  #76  [ast·이행] 이관 완료 조건 — 진단 0(문서 몫).
  #87  [ast]  composition_root 파일은 «자기 BC 의» composition_root 만 import.
  #97  [ast]  driving 잎은 자기 composition_root 에서 `build_*` 만 import.
  #118 [path] BC 오류 파일은 `bc_error_schema.py` — 옆 폴더 접두(`schema_bc_…`) 금지.
  #148 [path] 일반어가 된 약어는 풀지 않는다 — `application_programming_interface` 금지.
  #169 [path] 예외 계약 파일명 = 주 클래스명 snake_case.
  #247 [ast]  UnitOfWork 는 `<Bc>[<역할>]UnitOfWork`, 구현은 접두(`Django<Bc>[<역할>]UnitOfWork`) — 축약 불허·전수 판정(판정 ①).
  #309 [path] `service/` 로 줄이지 않는다 — `domain_service/` 그대로.
  #339 [path·면제] 어드민은 규정 밖 구역(자리·이름만) — 진단 0.
  #340 [path] admin/ 은 모델 하나 = 폴더 하나 — 직계 파일 금지.
  #341 [path] admin/<entity>/ 파일에 `_admin` 접미 금지.
  #342 [ast]  ModelAdmin 은 `admin/<entity>/panel.py` 에 하나.
  #343 [ast+] django 훅 몸통은 feature/ 로 — 후보: panel.py 훅 본문의 `.objects`·
              transaction·루프·모델 필드 조건(「운영 기능인가 장고 배선인가」).
  #344 [ast]  폼은 `form/<form>_form.py` — form 은 파일이 아니라 폴더, 폼 클래스는 그 안.
  #345 [ast]  운영 기능 하나 = 파일 하나(`feature/<feature>.py`) — feature.py 파일·
              한 파일 두 기능 금지.
  #348 [ast]  어드민 템플릿 — `templates/admin/<label>/…` 의 셋째 마디는 apps.py `label`
              (django_… 폴더 이름 ✗), 덮어쓰기 모델 마디는 소문자 붙임(밑줄 ✗).
  #366 [ast]  external_system 판정선 — 술어가 #367 그대로라 진단은 port-adapter 소유(중복 금지 · 진단 0).
  #382 [ast]  클래스 `Gateway` 접미 금지 — 계약이면 Port, 구현이면 Adapter.
  #481 [path] 부모 폴더 낱말을 자식 «폴더»가 반복 금지(`request/request_contract/`) —
              파일 반복은 정상(#30·#568 몫).
  #588 [ast]  사람 문구는 템플릿에 — 유스케이스·도메인의 render_to_string·gettext 호출 위반.
  #589 [ast+] 템플릿 업무 판정 후보 — `{% if %}` 조건의 비교 연산·업무 어휘(Q2).
  #590 [ast+] Presenter 는 «칸»이 아니다 — 확정: presenter 이름 칸·파일 / 후보:
              `<data>_out.py` 의 문구계 str 필드(message·body·subject·title·text).
  #610·#611 [path·이행] 화이트리스트 데이터 구조 몫 — 진단 0.

이관 계약(명세 조각 ⓐ): 채택 신호 2원(#78) · ImportError fail-closed · ⓓ 후보 exit 불산입.

사용법: check-naming.py [TARGET_DIR]   (기본: 현재 디렉터리)
종료코드: 0=clean(또는 표준 미채택) · 1=사용/분석 오류 · 2=blocker(발견 출력)
구조화 레코드: DJR_FINDINGS_JSON=<경로> 지정 시 findings.py(공용 모듈)가 JSON lines 를
추가 방출한다 — 라인 출력·exit 의미론 무변(T0 B2). 방출은 공용 ordered emitter
(emit_all) 경유 — stdout 위반·후보 라인 순서와 레코드 순서가 같고, 라인은 레코드
필드의 순수 함수다(출력 계약 v2).

그래프 좌표(T2-2): 규범 정본 = 온톨로지 그래프(`ontology/rules/`) · 이 검사기의 #N ↔ Work 조인은
  alias 대장(`ontology/wiring/aliases.ttl`)이 소유한다. 조인 확정: rule#74 → djr:R-3229.
  미확정 #N 은 T3 이관에서 해소한다(대장 28종 — T3 게이트 조항 처분 2026-08-22 ·
  판단표 v2 + `workspace/eval/t3/memos/`).
"""
from __future__ import annotations

import ast
import re
import sys

import checker_target
from findings import Candidates, Findings, emit_all, zero_target_guard
from pathlib import Path

try:
    import standard_tree as tree
    import business_vocab as vocab
except ImportError:  # 데이터 모듈 없이는 판정 불가 — fail-closed(분석 오류)
    print("분석 오류: standard_tree.py/business_vocab.py 를 찾지 못했다 — 검사기와 같은 폴더에 있어야 한다", file=sys.stderr)
    sys.exit(1)

SKIP_DIRS = vocab.SKIP_DIRS
DJANGO_APP_MARKERS = ("models.py", "apps.py", "views.py", "admin.py")
NEW_LAYERS = {"driving_layer", "application_layer", "domain_layer", "driven_layer"}

# #28 — 원전 패턴 약어(데이터 목록 — 닫지 않는다) · 예외 api(#148).
ABBREV_DENY = {"repo", "uow", "acl", "vo", "ohs", "agg", "spec", "svc", "ctrl", "impl", "mgr", "cfg"}
# #36 — 정도 낱말(공통이냐를 정도로 재는 이름).
DEGREE_DENY = {"common", "shared", "base", "core", "util", "utils", "helper", "helpers",
               "misc", "etc", "general", "lib", "support"}
KIND_RESUFFIX = {"_value_object", "_entity", "_event", "_exception", "_domain_service"}
PHRASE_FIELDS = {"message", "body", "subject", "title", "text"}

_TREE_DIR_NAMES: set = set()
_TREE_FILE_NAMES: set = set()
for _row in tree.ROWS:
    _nm = _row.name
    if _nm.endswith("/"):
        _nm = _nm[:-1]
    if "<" in _nm:
        continue
    for _seg in _nm.split("/"):
        if _seg.endswith(".py") or _seg.endswith(".html"):
            _TREE_FILE_NAMES.add(_seg)
        elif _seg:
            _TREE_DIR_NAMES.add(_seg)


def _has_adoption_signal(bc_dir: Path) -> bool:
    """채택 신호원 둘(#78) — check-layer-skeleton 과 같은 판."""
    has_layer = any((bc_dir / n).is_dir() for n in NEW_LAYERS)
    has_marker = any((bc_dir / m).is_file() for m in DJANGO_APP_MARKERS) or any(
        p.is_dir() and p.name.startswith("django_") for p in bc_dir.iterdir()
    )
    return has_layer or has_marker


def _parse(path: Path) -> ast.Module | None:
    try:
        return ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, SyntaxError):
        return None


def _py_files(base: Path) -> list[Path]:
    return [p for p in sorted(base.rglob("*.py")) if not set(p.parts) & SKIP_DIRS]


def _rel(root: Path, path: Path, line: int | None = None) -> str:
    s = path.relative_to(root).as_posix()
    return f"{s}:{line}" if line else s


def _camel(snake: str) -> str:
    return "".join(w.capitalize() for w in snake.split("_"))


def _snake(camel: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", camel).lower()


def _walk_dirs(base: Path) -> list[Path]:
    return [d for d in sorted(base.rglob("*")) if d.is_dir() and not set(d.parts) & SKIP_DIRS
            and d.name != "__pycache__"]


# ── #28 · #148 · #309 · #41 · #36 · #481 — 폴더·경로 낱말 ───────────────────

def _check_path_words(root: Path, bc: Path, bc_vocab_set: set, tech: set,
                      f: Findings, cand: Candidates) -> None:
    for d in _walk_dirs(bc):
        name = d.name
        rel = _rel(root, d)
        toks = set(name.split("_"))
        hit = toks & ABBREV_DENY
        if hit:
            f.add("#28", rel, f"약어 {sorted(hit)} — 원전 패턴 이름은 줄이지 않고 풀어 쓴다(api 만 예외 — #148)")
        if name == "service":
            f.add("#309", rel, "`service/` — `domain_service/` 를 그대로 쓴다(줄이지 않는다)")
        if "application_programming_interface" in name:
            f.add("#148", rel, "일반어가 된 약어는 풀어 쓰지 않는다 — `api` 그대로 쓴다")
        # 동명 폴더 승격(#490 교체형)의 정본 형 — 폴더명+`.py` 본체가 폴더 안에 실존.
        promoted = (d / f"{name}.py").is_file()
        if name == "gateway" or (name.endswith(("_port", "_adapter", "_gateway")) and not promoted):
            # 승격 폴더(본체 실존)는 칸 실현이라 #41 면제 — `*_port` 는 승격 배제 칸이라
            # 면제 개념 밖이지만, 승격 시도 자체는 registry #4(#490)가 red 로 잡는다.
            f.add("#41", rel, "Port·Adapter·Gateway 는 폴더 이름에 나오지 않는다 — "
                              "파일이 접미사로 종류를 진다(`<capability>_port.py`)")
        if name in DEGREE_DENY and name not in _TREE_DIR_NAMES \
                and d.parent.name not in ("domain_layer", "application_layer"):
            # domain/app 1차의 종류·정도 낱말은 #17/#18(domain-model) 소유 — 중복 진단 금지.
            f.add("#36", rel, f"정도 낱말 `{name}` — 칸 이름은 「판정이 되는 물음」을 가져야 "
                              "하고 「공통이냐」처럼 정도로 재는 이름은 쓰지 않는다")
        elif ("_" not in name and name not in _TREE_DIR_NAMES and name not in tech
              and not vocab.tokens(name) & bc_vocab_set and len(name) >= 3
              and not name.startswith("django")
              and d.parent.name in ("framework", "driving_layer")):
            cand.add("#36", rel, f"칸 `{name}` 이 트리·기술·업무 어휘 어디에도 없다",
                     "이 이름에 예/아니오로 답하는 물음이 붙나")
        # #481 — 부모 낱말 반복(폴더만).
        parent = d.parent.name
        if parent and len(parent) >= 3 and parent not in ("application",) \
                and parent not in NEW_LAYERS:
            if name != parent and name.split("_", 1)[0] == parent and not promoted:
                # 첫 토큰이 부모 그대로일 때만 문다 — `order/place_order/` 같은
                # `<area>/<use_case>/` 의 자연스러운 재등장은 반복이 아니다.
                # 승격 폴더(promoted — `turn/turn_controller/` 류)는 칸 실현이라 면제하고,
                # 완전 동명(`order/order/`)은 위 `name != parent` 가드가 원래 안 문다.
                f.add("#481", rel, f"자식 폴더가 부모 `{parent}/` 의 낱말을 반복한다 — "
                                   "파일의 접두·접미 반복(#30·#568)만 정상이다")
        # #148 — 파일 쪽도 본다(아래 파일 루프와 별개로 폴더 이름은 여기서 끝).
    for py in _py_files(bc):
        stem = py.stem
        if stem == "__init__":
            continue
        toks = set(stem.split("_"))
        hit = toks & ABBREV_DENY
        if hit:
            f.add("#28", _rel(root, py), f"약어 {sorted(hit)} — 원전 패턴 이름은 풀어 쓴다")
        if "application_programming_interface" in stem:
            f.add("#148", _rel(root, py), "일반어가 된 약어는 풀어 쓰지 않는다 — `api` 그대로")


# ── #30 · #33 · #34 — 접두·접미 스코프 ──────────────────────────────────────

def _check_prefix_suffix(root: Path, bc: Path, f: Findings) -> None:
    for py in _py_files(bc):
        stem, parts = py.stem, py.relative_to(bc).parts
        if stem == "__init__" or py.name in _TREE_FILE_NAMES:
            continue
        # #30 — 자리표시자 자리의 종류 재접미.
        for suf in KIND_RESUFFIX:
            if not stem.endswith(suf):
                continue
            kind = suf[1:]
            parent = py.parent.name
            if "open_host_service" in parts and "contract" in parts:
                continue  # 트리 27·29·32행 — OHS `contract/` 안은 접미형이 정본이다(`<exception>_exception.py`)
            if parent == kind or (kind == "value_object" and parent == "shared_value_object"):
                f.add("#30", _rel(root, py),
                      f"`{suf}` 재접미 — 폴더가 종류를 말하는 자리표시자 자리(`<{kind}>.py`)는 "
                      "접미사를 달지 않는다(가르는 자는 「이름이 곧 서술문인가」 — D41)")
        # #33 — 첫 토큰이 트리 폴더 이름인데 조상에 없다.
        # 단 #335 가 소유하는 `django_<bc>/models/<entity>_model.py` 자리는 대상이 아니다 —
        # entity 이름의 첫 토큰이 트리 폴더명과 겹치는 것은 #335 준수의 합법 귀결이다
        # (예: EventStreamModel → event_stream_model.py · 스펙 대장 #33 부칙 2026-08-25).
        first = stem.split("_", 1)[0]
        model_slot = (
            stem.endswith("_model")
            and py.parent.name == "models"
            and py.parent.parent.name.startswith("django_")
        )
        if first in _TREE_DIR_NAMES and first not in parts[:-1] and stem != first and not model_slot:
            if not any(seg.startswith(first) for seg in parts[:-1]):
                f.add("#33", _rel(root, py),
                      f"접두 `{first}_` 가 조상 폴더에 없다 — 접두는 자기가 «속한» 곳을 가리키고 "
                      "옆 폴더 이름을 빌리지 않는다")
        # #34 — application use-case boundary 안에서 같은 접두 = 같은 스코프.
        is_use_case_boundary = (
            len(parts) == 4
            and parts[0] == "application_layer"
            and parts[1] != "port"
        )
        # 승격 폴더(#490 교체형) 안은 한 층 더 깊다 — uc 폴더 기준 상대 판정. boundary 세 칸
        # (`_command`·`_query`·`_result`)은 승격 배제라 유스케이스 «직계»만 정본이고, 승격
        # 폴더 부품이 boundary 접미의 미끼 이름을 달아도 같은 #34 다.
        in_promoted_part = (
            len(parts) == 5
            and parts[0] == "application_layer"
            and parts[1] != "port"
            and (py.parent / f"{py.parent.name}.py").is_file()
        )
        for suf in ("_command", "_query", "_result"):
            if not stem.endswith(suf) or "domain_bypass_query" in parts:
                continue
            if is_use_case_boundary:
                base = stem[: -len(suf)]
                if py.parent.name != base:
                    f.add("#34", _rel(root, py),
                          f"`{stem}.py` 가 `{py.parent.name}/` 에 있다 — `<use_case>{suf}` 는 "
                          f"«유스케이스당»이라 `{base}/` 폴더 안이어야 한다")
            elif in_promoted_part:
                f.add("#34", _rel(root, py),
                      f"`{stem}.py` 가 승격 폴더 `{py.parent.name}/` 안에 있다 — "
                      f"`<use_case>{suf}` 는 «유스케이스 직계» 파일 칸이다(boundary 칸은 승격 배제)")
        # schema 칸은 승격 허용 — 정본 자리는 `schema/` 직계 또는 `schema/<동명 승격 폴더>/` 의
        # 본체(`schema/schema_in/schema_in.py`)다. 승격 폴더 부품은 stem 이 달라 이 판정 밖이다.
        schema_slot_ok = py.parent.name == "schema" or (
            py.parent.name == stem and py.parent.parent.name == "schema"
        )
        if stem in ("schema_in", "schema_out") and not schema_slot_ok:
            f.add("#34", _rel(root, py),
                  f"`{stem}.py` 가 `schema/` 밖에 있다 — `schema_*` 는 «<area>/ 당» 하나, "
                  "`schema/` 직계다")


# ── #44 · #169 · #118 · #247 — 겹침·계약 이름 ──────────────────────────────

def _check_name_pairs(root: Path, bc: Path, f: Findings) -> None:
    domain = bc / "domain_layer"
    if domain.is_dir():
        vo_stems = {p.stem for p in domain.glob("*/value_object/*.py") if p.stem != "__init__"}
        vo_stems |= {p.stem for p in domain.glob("shared_value_object/*.py") if p.stem != "__init__"}
        # domain_service 는 승격 허용 칸 — 승격 본체(`domain_service/<이름>/<이름>.py`) stem 포함.
        ds_stems = {p.stem for p in checker_target.slot_glob(domain / "domain_service", "*.py")
                    if p.stem != "__init__"}
        for name in sorted(vo_stems & ds_stems):
            f.add("#44", _rel(root, domain / "domain_service" / f"{name}.py"),
                  f"도메인 서비스 `{name}` 이 같은 BC 의 값 객체와 겹친다 — 행위 이름으로 짓는다"
                  "(`settle_turn` 처럼)")
    for py in _py_files(bc):
        parts = py.relative_to(bc).parts
        # #169 — 예외 계약 파일명 = 주 클래스명 snake_case.
        if "contract" in parts and "exception" in parts and py.stem != "__init__":
            mod = _parse(py)
            classes = [n for n in (mod.body if mod else []) if isinstance(n, ast.ClassDef)]
            if classes and _snake(classes[0].name) != py.stem:
                f.add("#169", _rel(root, py),
                      f"파일명이 주 클래스 `{classes[0].name}` 의 snake_case(`{_snake(classes[0].name)}`)가 아니다")
        # #118 — bc_error_schema 접두 금지.
        if py.name.endswith("bc_error_schema.py") and py.name != "bc_error_schema.py":
            f.add("#118", _rel(root, py),
                  "옆 폴더 이름을 접두로 달았다 — BC 오류 파일 이름은 `bc_error_schema.py` 그대로다")
        # #247 — UnitOfWork 이름(판정 ① 2026-08-25): 계약 `<Bc>[<역할>]UnitOfWork` ·
        # 구현 `<기술접두><Bc>[<역할>]UnitOfWork`(접두 임의 — 동작 보존). 역할 수식어는
        # CamelCase 1어절 이상 선택. 축약(`Uow` 등)·접미 이탈은 공개 클래스 전수 판정으로
        # 가시화한다(불허 — 종전 endswith 가드는 비-UnitOfWork 접미를 불가시 처리했다).
        if "unit_of_work" in parts and py.stem != "__init__":
            mod = _parse(py)
            bc_camel = _camel(bc.name)
            expected = bc_camel + "UnitOfWork"
            port_re = re.compile(rf"^{bc_camel}([A-Z][A-Za-z0-9]*)?UnitOfWork$")
            impl_re = re.compile(rf"^[A-Z][A-Za-z0-9]*{bc_camel}([A-Z][A-Za-z0-9]*)?UnitOfWork$")
            in_port = "port" in parts
            for cls in [n for n in (mod.body if mod else []) if isinstance(n, ast.ClassDef)]:
                if cls.name.startswith("_"):
                    continue
                if in_port and not port_re.fullmatch(cls.name):
                    f.add("#247", _rel(root, py, cls.lineno),
                          f"UnitOfWork 계약 이름 `{cls.name}` — `{expected}`"
                          f"(역할이 있으면 `{bc_camel}<역할>UnitOfWork`) 꼴이어야 한다(축약 불허)")
                if not in_port and not impl_re.fullmatch(cls.name):
                    f.add("#247", _rel(root, py, cls.lineno),
                          f"구현 이름 `{cls.name}` — 같은 이름에 «접두»로 갈린다"
                          f"(`Django{expected}` 꼴 — 역할 수식어는 계약과 공유·축약 불허)")


# ── #87 · #97 — composition_root import 방향 ────────────────────────────────

def _check_wiring_imports(root: Path, bc: Path, f: Findings) -> None:
    comp = bc / "composition_root"
    own = bc.name
    if comp.is_dir():
        for py in _py_files(comp):
            mod = _parse(py)
            for node in ast.walk(mod) if mod else []:
                if isinstance(node, ast.ImportFrom) and "composition_root" in (node.module or ""):
                    segs = (node.module or "").split(".")
                    if segs[0] == "application" and len(segs) >= 2 and segs[1] != own:
                        f.add("#87", _rel(root, py, node.lineno),
                              f"타 BC `{segs[1]}` 의 composition_root import — 자기 BC 의 "
                              "composition_root 만 import 한다")
    for layer in ("driving_layer",):
        base = bc / layer
        if not base.is_dir():
            continue
        for py in _py_files(base):
            if py.name in ("api_router.py", "event_router.py", "event_wiring.py", "__init__.py"):
                continue
            mod = _parse(py)
            for node in ast.walk(mod) if mod else []:
                if isinstance(node, ast.ImportFrom) and "composition_root" in (node.module or ""):
                    segs = (node.module or "").split(".")
                    bad_bc = segs[0] == "application" and len(segs) >= 2 and segs[1] != own
                    bad_names = [a.name for a in node.names if not a.name.startswith("build_")]
                    if bad_bc or bad_names:
                        f.add("#97", _rel(root, py, node.lineno),
                              f"driving 잎의 composition_root import 는 «자기 BC 의 build_*» 만이다"
                              + (f" — `{bad_names[0]}` 는 build_* 가 아니다" if bad_names else ""))


# ── #43 · #382 — 클래스 낱말 ───────────────────────────────────────────────

def _check_class_words(root: Path, bc: Path, f: Findings) -> None:
    for py in _py_files(bc):
        mod = _parse(py)
        if mod is None:
            continue
        for cls in [n for n in ast.walk(mod) if isinstance(n, ast.ClassDef)]:
            toks = re.findall(r"[A-Z][a-z0-9]*", cls.name)
            if cls.name.endswith("Gateway"):
                f.add("#382", _rel(root, py, cls.lineno),
                      f"`{cls.name}` — Gateway 접미사를 쓰지 않는다(계약이면 Port, 구현이면 Adapter)")
            elif set(toks[:-1]) & {"Port", "Adapter", "Gateway"}:
                f.add("#43", _rel(root, py, cls.lineno),
                      f"`{cls.name}` — 패턴 낱말은 자리가 대신 말하니 능력 이름에 쓰지 않는다"
                      "(동사에서 온 이름(Issuer·Generator·Sender)만 남긴다)")


# ── #340 ~ #348 · #343 — 어드민 ────────────────────────────────────────────

DJANGO_HOOKS = {"get_urls", "save_model", "delete_model", "get_queryset", "response_change",
                "response_add", "formfield_for_foreignkey", "has_change_permission"}


def _admin_dirs(bc: Path) -> list[Path]:
    return [d / "admin" for d in sorted(bc.glob("django_*")) if (d / "admin").is_dir()]


def _check_admin(root: Path, bc: Path, f: Findings, cand: Candidates) -> None:
    for admin in _admin_dirs(bc):
        for p in sorted(admin.iterdir()):
            if p.is_file() and p.suffix == ".py" and p.name != "__init__.py":
                f.add("#340", _rel(root, p),
                      "admin/ 직계 파일 — 모델 하나 = 폴더 하나(`admin/<entity>/`)다")
        for entity_dir in sorted(p for p in admin.iterdir() if p.is_dir() and p.name != "__pycache__"):
            for py in _py_files(entity_dir):
                if py.stem.endswith("_admin"):
                    f.add("#341", _rel(root, py),
                          "`_admin` 접미사 — 폴더가 «누구»를 말하니 파일은 «무엇»만 말한다")
            if (entity_dir / "form.py").is_file():
                f.add("#344", _rel(root, entity_dir / "form.py"),
                      "`form` 은 파일이 아니라 폴더다 — `form/<form>_form.py`")
            form_dir = entity_dir / "form"
            if form_dir.is_dir():
                for py in form_dir.glob("*.py"):
                    if py.name != "__init__.py" and not py.name.endswith("_form.py"):
                        f.add("#344", _rel(root, py), "폼 파일은 `<form>_form.py` 다(폼 하나 = 파일 하나)")
            if (entity_dir / "feature.py").is_file():
                f.add("#345", _rel(root, entity_dir / "feature.py"),
                      "`feature` 는 파일이 아니라 폴더다 — `feature/<feature>.py`(기능 하나 = 파일 하나)")
            feat_dir = entity_dir / "feature"
            if feat_dir.is_dir():
                for py in feat_dir.glob("*.py"):
                    mod = _parse(py)
                    pub = [n for n in (mod.body if mod else [])
                           if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
                           and not n.name.startswith("_")]
                    if len(pub) > 1:
                        f.add("#345", _rel(root, py),
                              f"공개 정의 {len(pub)}개 — 운영 기능 하나 = 파일 하나다")
            # #342 · #343 · #344(폼 클래스 자리) — panel.py.
            panel = entity_dir / "panel.py"
            panel_admins = 0
            for py in _py_files(entity_dir):
                mod = _parse(py)
                if mod is None:
                    continue
                for cls in [n for n in ast.walk(mod) if isinstance(n, ast.ClassDef)]:
                    bases = {b.id if isinstance(b, ast.Name) else getattr(b, "attr", "") for b in cls.bases}
                    if bases & {"ModelAdmin", "TabularInline", "StackedInline"}:
                        if py.name != "panel.py":
                            f.add("#342", _rel(root, py, cls.lineno),
                                  "ModelAdmin 이 panel.py 밖에 있다 — 클래스는 `admin/<entity>/panel.py` 에 하나다")
                        elif bases & {"ModelAdmin"}:
                            panel_admins += 1
                            if panel_admins > 1:
                                f.add("#342", _rel(root, py, cls.lineno),
                                      "panel.py 에 ModelAdmin 이 둘 — 모델 하나 = 폴더 하나 = 패널 하나다")
                    if bases & {"Form", "ModelForm"} and "form" not in py.relative_to(entity_dir).parts:
                        f.add("#344", _rel(root, py, cls.lineno),
                              "폼 클래스가 form/ 밖에 있다 — `form/<form>_form.py` 에 둔다")
            if panel.is_file():
                mod = _parse(panel)
                for cls in [n for n in ast.walk(mod) if isinstance(n, ast.ClassDef)] if mod else []:
                    for m in [n for n in cls.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]:
                        if m.name not in DJANGO_HOOKS:
                            continue
                        for n in ast.walk(m):
                            hitmsg = None
                            if isinstance(n, ast.Attribute) and n.attr == "objects":
                                hitmsg = "`.objects` 질의"
                            elif isinstance(n, ast.Name) and n.id == "transaction":
                                hitmsg = "transaction 사용"
                            elif isinstance(n, (ast.For, ast.While)):
                                hitmsg = "루프"
                            if hitmsg:
                                cand.add("#343", _rel(root, panel, n.lineno),
                                         f"django 훅 `{m.name}` 본문에 {hitmsg} — 훅은 panel.py 에 "
                                         "남기고 몸통은 feature/ 로 내린다",
                                         "이 문장이 운영 «기능»인가 장고 «배선»인가")
                                break
        # #348 — 템플릿 경로.
        droot = admin.parent
        tadmin = droot / "templates" / "admin"
        if tadmin.is_dir():
            for seg in sorted(p for p in tadmin.iterdir() if p.is_dir()):
                if seg.name.startswith("django_"):
                    f.add("#348", _rel(root, seg),
                          "templates/admin/ 셋째 마디가 폴더 이름(django_…)이다 — apps.py 의 "
                          "`label` 이어야 한다")
                for model_seg in sorted(p for p in seg.iterdir() if p.is_dir()):
                    if "_" in model_seg.name:
                        f.add("#348", _rel(root, model_seg),
                              "덮어쓰기 경로의 모델 마디에 밑줄 — 모델 클래스명을 «전부 소문자로 "
                              "붙인 것»(밑줄 없음)이다")


# ── #588 · #589 · #590 — 문구의 자리 ───────────────────────────────────────

RENDER_CALLS = {"render_to_string", "gettext", "gettext_lazy", "ngettext", "format_lazy"}
TEMPLATE_IF_RE = re.compile(r"{%\s*(?:el)?if\s+(.+?)\s*%}")


def _check_phrase_home(root: Path, bc: Path, bc_vocab_set: set, f: Findings, cand: Candidates) -> None:
    for layer in ("application_layer", "domain_layer"):
        base = bc / layer
        if not base.is_dir():
            continue
        for py in _py_files(base):
            mod = _parse(py)
            for node in ast.walk(mod) if mod else []:
                if isinstance(node, ast.Call):
                    name = node.func.id if isinstance(node.func, ast.Name) else \
                        (node.func.attr if isinstance(node.func, ast.Attribute) else "")
                    if name in RENDER_CALLS or name == "_":
                        f.add("#588", _rel(root, py, node.lineno),
                              f"`{name or '_'}()` — 사람 문구는 템플릿에 살고 그것을 여는 것은 "
                              "«어댑터»뿐이다(유스케이스·도메인 호출 금지)")
    # #590 — presenter 칸·파일 확정, _out 문구 필드 후보.
    for d in _walk_dirs(bc):
        if "presenter" in d.name:
            f.add("#590", _rel(root, d),
                  "presenter 칸 — Presenter 는 «칸»이 아니라 «경계 모양»이다(문구를 빚는 자리를 "
                  "따로 만들지 않는다)")
    for py in _py_files(bc):
        if "presenter" in py.stem:
            f.add("#590", _rel(root, py), "presenter 파일 — 문구를 빚는 자리를 따로 만들지 않는다")
        if py.name.endswith("_out.py"):
            mod = _parse(py)
            for node in ast.walk(mod) if mod else []:
                if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) \
                        and node.target.id in PHRASE_FIELDS:
                    cand.add("#590", _rel(root, py, node.lineno),
                             f"`{node.target.id}` str 필드 — 안쪽은 코드·번호·수량·locale 까지만 싣는다",
                             "이 값이 사람이 읽을 문구인가")
    # #589 — 템플릿 업무 판정 후보.
    for html in sorted(bc.rglob("*.html")):
        if set(html.parts) & SKIP_DIRS:
            continue
        try:
            text = html.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for i, line in enumerate(text.splitlines(), 1):
            for m in TEMPLATE_IF_RE.finditer(line):
                cond = m.group(1)
                has_op = bool(re.search(r"[<>]=?|==|!=|\band\b|\bor\b", cond))
                cond_toks = vocab.tokens(cond.replace(".", "_"))
                if has_op or cond_toks & bc_vocab_set:
                    cand.add("#589", f"{_rel(root, html)}:{i}",
                             f"`{{% if {cond} %}}` — 「환불이 되나」를 템플릿이 다시 쓰면 같은 규칙이 "
                             "두 채널이 된다(D30). 여기 오는 것은 «이미 정해진 값»뿐이다",
                             "이 조건이 업무 판정인가")


# ── main ────────────────────────────────────────────────────────────────────

def main(argv: list[str]) -> int:
    if len(argv) > 1:
        print(f"사용법: {Path(sys.argv[0]).name} [TARGET_DIR]", file=sys.stderr)
        return 1
    root = Path(argv[0]).resolve() if argv else Path.cwd()
    bad_target_reason = checker_target.bc_shaped_target_reason(root)
    if bad_target_reason is not None:
        print(f"사용 오류: {bad_target_reason}", file=sys.stderr)
        return 1
    if not root.is_dir():
        print(f"사용 오류: 디렉터리가 아니다 — {root}", file=sys.stderr)
        return 1

    findings = Findings(defer=True)
    cand = Candidates(defer=True)
    tech = vocab.tech_names()
    bcs = [bc for bc in vocab.bc_dirs(root) if _has_adoption_signal(bc)]

    # 대상 0건 가드(#74) — touched 필터 없음이라 자리는 대상 집합 직후다(#75).
    if bcs and not any(_py_files(bc) for bc in bcs):
        guard = zero_target_guard(
            "blocker: 채택 신호는 있는데 검사할 .py 가 0건이다 — 조용한 무동작을 금지한다(#74)"
        )
        emit_all(guard, printer=print, indent="")
        return 2

    for bc in bcs:
        bc_vocab_set = vocab.bc_vocab(bc)
        _check_path_words(root, bc, bc_vocab_set, tech, findings, cand)
        _check_prefix_suffix(root, bc, findings)
        _check_name_pairs(root, bc, findings)
        _check_wiring_imports(root, bc, findings)
        _check_class_words(root, bc, findings)
        _check_admin(root, bc, findings, cand)
        _check_phrase_home(root, bc, bc_vocab_set, findings, cand)

    # ⓓ#36 — framework 능력 칸 이름의 물음(트리·기술·업무 어휘 밖 단독 낱말).
    if bcs:
        union = vocab.all_vocab(root)
        fw = root / "framework"
        if fw.is_dir():
            for d in sorted(p for p in fw.iterdir() if p.is_dir() and p.name != "__pycache__"):
                if d.name in DEGREE_DENY:
                    findings.add("#36", _rel(root, d),
                                 f"정도 낱말 `{d.name}` — 칸 이름은 「판정이 되는 물음」을 가져야 한다")
                elif "_" not in d.name and d.name not in _TREE_DIR_NAMES \
                        and d.name not in tech and not vocab.tokens(d.name) & union:
                    cand.add("#36", _rel(root, d), f"framework 칸 `{d.name}` 이 트리·기술·업무 어휘 어디에도 없다",
                             "이 이름에 예/아니오로 답하는 물음이 붙나")

    emit_all(cand, printer=print, indent="")
    if findings:
        print("blocker — 이름 규율 위반 (풀어 쓰고·자리가 종류를 말하고·접두는 제 집을 가리킨다 — D9·D21·D33·D41)")
        emit_all(findings, printer=print, indent="  ")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
