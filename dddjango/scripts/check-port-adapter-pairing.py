#!/usr/bin/env python3
"""dddjango 포트·어댑터 짝맞춤 검사기 — 선언(port/)과 구현(adapter/)·페이크(test/fake/)의 계약(D37·D44·D51·D57).

담당 규칙 (rule-owner-map · 총 83 — 기계 진단이 있는 것만 요약):
  port/  #457 선언은 application_layer/port/ 아래뿐 · #212 선언만(구현 0줄) · #215 능력
         하나=폴더 하나(직계 파일 금지) · #216 안은 계약·자료·실패 셋 · #218 파일명=폴더명 ·
         #219 추상 인터페이스 하나 · #220 <Capability>Port · #225 exception.py 필수 ·
         #64 포트 예외는 도메인 예외 비상속 · #214 애그리거트 리포지토리 선언은 여기 금지 ·
         #227[ast+] 자료는 원시값으로 안 될 때만(후보) · #228 <data>_in/_out 에 도메인·
         유스케이스 DTO 금지(토큰 검사 ✗ — predicates ⓐ) · #573 방향(_in/_out) 이름 교차 ·
         #485[ast+] 메서드는 의도(확정: notify·handle·execute… / 후보: 동사 아님) ·
         #594[ast+] 폴더 이름에 누가·언제·어떻게 금지(#595 확정: 기술 이름 정확 일치) ·
         #313 domain_layer/<agg>/port/ 금지
  bypass #229 계약은 port/domain_bypass_query/ · #231 domain_layer 에 조회 계약 금지 ·
         #232 능력=폴더·셋 낱말 · #233[ast+] 「무엇을 알고 싶은가」(확정: 기술·BC 토큰) ·
         #234 파일명=폴더명·하나 · #235 <Capability>DomainBypassQuery · #236 반출은 이름
         붙인 정적 타입(QuerySet·dict·Model ✗) · #238 exception.py 필수 · #239 도메인
         예외 비상속 · #465 _repository 접미 금지 · #475[ast+] 날것으로 업무 판정(후보)
  uow    #240 선언은 port/unit_of_work/ · #241 대화 계약과 «괄호»의 분리(포트에 uow
         메서드 ✗) · #242 exception.py 금지 · #244 <boundary>_unit_of_work.py · #245 계약
         셋(__enter__/__exit__/after_commit — exact-set·판정 ②) · #246 리포지토리 노출 금지 · #374 구현 파일 자리 ·
         #376 구현은 transaction.on_commit 으로 채움 · #476 선언↔구현 1:1(양방향) ·
         #566 on_commit robust 미지정이면 앞 콜백 실패로 통째 소실
  adapter #460 구현은 driven_layer/adapter/ 아래(django_<bc> 만 예외) · #319 네 갈래
         (ORM→persistence·타 BC→acl·소켓→external_system·나머지→capability — 단
         비애그리거트 ORM «능력 포트» 구현은 capability 의 django 어댑터: #462 확장) · #349
         repository/ 는 django_<bc> 밖 · #350 read_model/ 금지 · #351 선언↔구현 1:1 ·
         #352 폴더 아님 · #354 Django<Aggregate>Repository · #356 thin read 는 domain 비
         의존 · #359 Django<Capability>DomainBypassQuery · #365 acl 은 우리 BC 이름만 ·
         #367 소켓 여는 import 는 external_system 어댑터 안뿐(목록은 데이터 — 닫지 않는다) ·
         #368[ast+] 값의 자리에 기계(후보) · #369 벤더=폴더 · #370 <System><Capability>
         Adapter · #371~#373 나머지 어댑터 자리·이름 · #464 command/query 분할 금지 ·
         #477 리포지토리 구현은 domain import 필수 · #582 파일은 기술을 말한다 ·
         #583 양방향 1:1 은 셋뿐 · #545 save() 는 «안 꺼낸 사실» 가드 · #551 계약은
         ABC+@abstractmethod · #552 구현은 계약 상속 · #553[ast+] 어댑터의 업무 판정(후보) ·
         #554 계약이 선언한 실패로 · #555 벤더 예외 그대로 흘림 금지 · #556 재시도 기계는
         framework 몫 · #557 벤더 오류 코드 판정은 어댑터 안뿐
  fake   #575 test/fake/ 에만 · #576 짝 선언 없는 페이크(한 방향) · #577 선언 상속·같은
         이름 · #578 기술 만지면 어댑터 · #579 프로덕션의 페이크 import · #580
         dependency_wiring 의 페이크 주입 · #581 평평하게
  기타   #134 컨트롤러는 build_* 만(직접 생성 금지) · #574 <data>_in 생성은 어댑터만 ·
         #71(=#304·#305·#8)·#40(=#403·#408·#219·#220)·#463(=#319)·#480(dto 이름 — usecase-dto
         관할과 자리 분리해 port 구역만) — 참조·중복 진단 금지 원칙대로 실체는 한 곳만.

이관 계약(명세 조각 ⓐ): 채택 신호 2원(#78) · 대상 0건 가드(#74) · ImportError
fail-closed · ⓓ 후보 exit 불산입.

사용법: check-port-adapter-pairing.py [TARGET_DIR]   (기본: 현재 디렉터리)
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
DRIVEN_DIRS = ("driven_layer",)
DRIVING_DIRS = ("driving_layer",)

PORT_KIND_FILES = {"exception.py", "__init__.py"}
UOW_METHODS = {"__enter__", "__exit__", "after_commit", "__init__"}
# #367 — 소켓 여는 라이브러리(저장소 의존성에 맞춰 유지하는 «데이터» — 닫지 않는다).
SOCKET_LIBS = {"httpx", "requests", "boto3", "openai", "redis", "kafka", "confluent_kafka",
               "pika", "kombu", "grpc", "grpcio", "smtplib", "psycopg2", "pymongo", "stripe"}
RETRY_LIBS = {"tenacity", "backoff", "retrying"}
INTENT_DENY = {"notify", "handle", "execute", "process", "run", "do"}
ASKING_PREFIX = ("has_", "is_", "can_", "current_", "get_", "find_", "list_", "count_", "exists_")
VERB_HINTS = {"send", "issue", "revoke", "generate", "publish", "acquire", "release", "charge",
              "refund", "create", "delete", "save", "remove", "fetch", "resolve", "render",
              "sign", "verify", "upload", "download", "enqueue", "schedule", "cancel", "mark",
              "record", "translate", "convert", "open", "close", "lock", "unlock", "now"}
MEANS_WORDS = {"client", "cache", "sync", "cron", "queue", "http", "rest", "sdk",
               "nightly", "daily", "hourly", "weekly", "realtime", "driver", "gateway"}
TECH_EXACT = {"smtp", "redis", "celery", "kafka", "django", "ninja", "stripe", "s3", "grpc"}


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


def _driven(bc: Path) -> Path | None:
    for layer in DRIVEN_DIRS:
        if (bc / layer).is_dir():
            return bc / layer
    return None


def _bases(cls: ast.ClassDef) -> set[str]:
    return {b.id if isinstance(b, ast.Name) else getattr(b, "attr", "") for b in cls.bases}


def _ann_names(node: ast.AST | None) -> set[str]:
    out: set[str] = set()
    if node is None:
        return out
    for n in ast.walk(node):
        if isinstance(n, ast.Name):
            out.add(n.id)
        elif isinstance(n, ast.Attribute):
            out.add(n.attr)
        elif isinstance(n, ast.Constant) and isinstance(n.value, str):
            try:
                out |= _ann_names(ast.parse(n.value, mode="eval").body)
            except SyntaxError:
                pass
    return out


# ── port/<capability>/ — #212~#228 · #485 · #594 · #64 ─────────────────────

def _check_port_tree(root: Path, bc: Path, bc_vocab_set: set, tech: set,
                     f: Findings, cand: Candidates) -> None:
    app = bc / "application_layer"
    port = app / "port"
    domain = bc / "domain_layer"
    if domain.is_dir():
        for d in domain.rglob("port"):
            if d.is_dir() and not set(d.parts) & SKIP_DIRS:
                f.add("#313", _rel(root, d),
                      "domain_layer 아래 port/ — 붙는 포트(리포지토리)는 <aggregate>_repository.py "
                      "로 자리가 났고 안 붙는 포트는 도메인 것이 아니다")
    if app.is_dir():
        for py in _py_files(app):
            parts = py.relative_to(app).parts
            if py.stem.endswith("_port") and "port" not in parts:
                f.add("#457", _rel(root, py),
                      "선언(*_port.py)이 application_layer/port/ 밖에 있다 — 「바깥에 있어야 "
                      "하는 것」을 적는 자리는 거기 하나다")
            if py.stem.endswith("_unit_of_work") and "unit_of_work" not in parts:
                f.add("#240", _rel(root, py),
                      "UnitOfWork 선언이 port/unit_of_work/ 밖에 있다")
    if not port.is_dir():
        return
    for p in sorted(port.iterdir()):
        if p.is_file() and p.suffix == ".py" and p.name != "__init__.py":
            f.add("#215", _rel(root, p),
                  "port/ 직계 파일 — 능력 하나 = 폴더 하나다(포트를 파일 하나로 두지 않는다)")
    for cap in sorted(p for p in port.iterdir() if p.is_dir() and p.name != "__pycache__"):
        if cap.name in ("domain_bypass_query", "unit_of_work"):
            continue
        _check_capability_folder(root, bc, cap, bc_vocab_set, tech, f, cand)
    bypass = port / "domain_bypass_query"
    if bypass.is_dir():
        _check_bypass(root, bypass, tech, f, cand)
    uow = port / "unit_of_work"
    if uow.is_dir():
        _check_uow_port(root, uow, f)


def _check_capability_folder(root: Path, bc: Path, cap: Path, bc_vocab_set: set, tech: set,
                             f: Findings, cand: Candidates) -> None:
    # #594/#595 — 이름 판정.
    toks = set(cap.name.split("_"))
    if toks & TECH_EXACT:
        f.add("#594", _rel(root, cap),
              f"port 능력 이름 `{cap.name}/` 에 기술 — 「무엇이 필요한가」로 짓는다"
              "(smtp_client ✗ → email_sender ✓ · 판정은 #595 「그것이 바뀌어도 이름이 그대로인가」)")
    elif toks & MEANS_WORDS:
        cand.add("#594", _rel(root, cap),
                 f"능력 이름 `{cap.name}/` 에 수단·계기 낱말 {sorted(toks & MEANS_WORDS)}",
                 "그것(공급자·계기·수단)이 바뀌어도 이 이름이 그대로인가(#595)")
    expected = f"{cap.name}_port.py"
    ports = list(cap.glob("*_port.py"))
    if not (cap / expected).is_file():
        f.add("#218", _rel(root, cap),
              f"계약 파일 이름이 폴더와 다르다 — `{expected}` 여야 한다({[p.name for p in ports]})")
    if not (cap / "exception.py").is_file():
        f.add("#225", _rel(root, cap), "exception.py 가 없다 — 포트 폴더마다 필수다")
    for py in sorted(cap.glob("*.py")):
        if py.name == "__init__.py":
            continue
        ok = py.name in PORT_KIND_FILES or py.stem.endswith("_port") \
            or py.stem.endswith("_out") or py.stem.endswith("_in")
        if not ok:
            f.add("#216", _rel(root, py),
                  "port/<capability>/ 에 오는 것은 계약(*_port.py)·자료(<data>_out/_in.py)·"
                  "실패(exception.py) 셋이다")
        if py.stem.endswith("_repository"):
            f.add("#214", _rel(root, py),
                  "애그리거트 리포지토리 선언이 port/ 에 있다 — 자리는 domain_layer/<aggregate>/ 다")
        mod = _parse(py)
        if mod is None:
            continue
        if py.stem.endswith("_port"):
            _check_port_contract(root, cap, py, mod, f, cand)
        if py.stem == "exception":
            for node in ast.walk(mod):
                if isinstance(node, ast.ImportFrom) and "domain_layer" in (node.module or ""):
                    f.add("#64", _rel(root, py, node.lineno),
                          "포트 예외가 도메인을 import 한다 — 도메인 예외를 상속하지 않는다")
        if py.stem.endswith(("_out", "_in")):
            _check_port_data(root, py, mod, f, cand)


def _check_port_contract(root: Path, cap: Path, py: Path, mod: ast.Module,
                         f: Findings, cand: Candidates) -> None:
    if checker_target.skeleton_placeholder(py):
        return  # 내용 없는 골격 파일 — 내용 규칙(#219·#551·#220·#241·#212·#485)의 대상이 아니다(결정 2 · 2026-09-04)
    classes = [n for n in mod.body if isinstance(n, ast.ClassDef) and not n.name.startswith("_")]
    if len(classes) != 1:
        f.add("#219", _rel(root, py), f"공개 클래스 {len(classes)}개 — 추상 인터페이스 «하나»가 온다")
    for cls in classes:
        if "ABC" not in _bases(cls):
            f.add("#551", _rel(root, py, cls.lineno),
                  f"`{cls.name}` 이 ABC 를 상속하지 않는다 — 미구현은 인스턴스화의 TypeError 로 잡는다(D44)")
        want = f"{_camel(cap.name)}Port"
        if not cls.name.endswith("Port") or not cls.name.endswith(want):
            f.add("#220", _rel(root, py, cls.lineno),
                  f"`{cls.name}` — port/<capability>/ 의 클래스는 `{want}` 로 끝난다")
        uow_like = {m.name for m in cls.body if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))} \
            & {"commit", "rollback", "after_commit", "__enter__", "__exit__"}
        if uow_like:
            f.add("#241", _rel(root, py, cls.lineno),
                  f"대화 계약에 UnitOfWork 낱말 {sorted(uow_like)} — 바깥에 «시키는» 것은 "
                  "port/<capability>/, 내 저장을 «묶는» 것은 port/unit_of_work/ 다")
        for m in [n for n in cls.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]:
            if m.name.startswith("__"):
                continue
            decos = {d.id if isinstance(d, ast.Name) else getattr(d, "attr", "") for d in m.decorator_list}
            if "abstractmethod" not in decos:
                f.add("#212", _rel(root, py, m.lineno),
                      f"`{m.name}` 에 구현이 있다 — port/ 에는 선언만 온다(구현은 한 줄도 없다 · #551)")
            first = m.name.split("_", 1)[0]
            if m.name in INTENT_DENY or m.name.endswith(("_command", "_query")):
                f.add("#485", _rel(root, py, m.lineno),
                      f"`{m.name}` — 무엇을 시키는지 말하지 않는 이름이다(시키면 명령형 동사구, "
                      "물으면 묻는 꼴 — revoke_for_child()·has_shipped())")
            elif not m.name.startswith(ASKING_PREFIX) and first not in VERB_HINTS:
                cand.add("#485", _rel(root, py, m.lineno),
                         f"포트 메서드 `{m.name}` 의 첫 토큰이 동사도 묻는 꼴도 아니다",
                         "이 이름이 무엇을 시키는지 말하나")


def _check_port_data(root: Path, py: Path, mod: ast.Module, f: Findings, cand: Candidates) -> None:
    for node in ast.walk(mod):
        if isinstance(node, ast.ImportFrom):
            m = node.module or ""
            if "domain_layer" in m:
                f.add("#228", _rel(root, py, node.lineno),
                      "<data> 파일이 domain_layer 를 import 한다 — 업무 어휘가 포트 밖으로 새면 "
                      "안 된다(필요한 값은 «펴서» 싣는다 · 값 객체 «모양»은 #227 이 허용)")
            if m.endswith(("_command", "_query", "_result")) or "_use_case" in m:
                f.add("#228", _rel(root, py, node.lineno),
                      "<data> 파일이 유스케이스 어휘를 참조한다 — 여기는 «이름 붙인 정적 타입»이다")
    for cls in [n for n in mod.body if isinstance(n, ast.ClassDef)]:
        if py.stem.endswith("_out") and cls.name.endswith("In"):
            f.add("#573", _rel(root, py, cls.lineno),
                  "`_out.py` 에 …In 클래스 — 방향 기준점은 «우리 안쪽»이다(들어오면 _in, 나가면 _out)")
        if py.stem.endswith("_in") and cls.name.endswith("Out"):
            f.add("#573", _rel(root, py, cls.lineno), "`_in.py` 에 …Out 클래스 — 방향이 뒤집혔다")
        if "dto" in cls.name.lower() or cls.name.endswith(("Command", "Result")):
            f.add("#480", _rel(root, py, cls.lineno),
                  f"`{cls.name}` — 이 칸의 반출 타입을 DTO·Command·Result 라 부르지 않는다"
                  "(<use_case>_command/_result 은 유스케이스의 어휘다)")
        fields = [n for n in cls.body if isinstance(n, ast.AnnAssign)]
        if len(fields) == 1:
            cand.add("#227", _rel(root, py, cls.lineno),
                     f"`{cls.name}` 필드가 하나 — 원시값·값 객체로 되면 만들지 않는다",
                     "이 자료를 원시값 인자로 «펴서» 넘길 수 있나")


# ── domain_bypass_query — #229~#239 · #465 ─────────────────────────────────

def _check_bypass(root: Path, bypass: Path, tech: set, f: Findings, cand: Candidates) -> None:
    for p in sorted(bypass.iterdir()):
        if p.is_file() and p.suffix == ".py" and p.name != "__init__.py":
            f.add("#232", _rel(root, p), "domain_bypass_query/ 직계 파일 — 능력 하나 = 폴더 하나다")
    for cap in sorted(p for p in bypass.iterdir() if p.is_dir() and p.name != "__pycache__"):
        toks = set(cap.name.split("_"))
        if toks & (TECH_EXACT | vocab.bc_names(root)):
            f.add("#233", _rel(root, cap),
                  f"`{cap.name}/` — 「무엇을 알고 싶은가」로 짓고 «누가 주는지»는 이름에 넣지 않는다")
        elif "_" not in cap.name:
            cand.add("#233", _rel(root, cap), f"`{cap.name}/` 이 명사 하나뿐이다",
                     "Q1 — 무엇을 알고 싶은가가 이름에 있나")
        expected = f"{cap.name}_query.py"
        queries = list(cap.glob("*_query.py"))
        if not (cap / expected).is_file() or len(queries) > 1:
            f.add("#234", _rel(root, cap),
                  f"계약 하나 = 파일 하나·이름은 폴더와 같다 — `{expected}`({[p.name for p in queries]})")
        if not (cap / "exception.py").is_file():
            f.add("#238", _rel(root, cap), "exception.py 가 없다 — 필수다")
        for py in sorted(cap.glob("*.py")):
            if py.stem.endswith("_repository"):
                f.add("#465", _rel(root, py),
                      "_repository 접미 — 이 칸은 애그리거트를 안 거치므로 리포지토리가 아니다"
                      "(접미사는 _query, 선언·구현이 함께 단다)")
            mod = _parse(py)
            if mod is None:
                continue
            if py.stem == "exception":
                for node in ast.walk(mod):
                    if isinstance(node, ast.ImportFrom) and "domain_layer" in (node.module or ""):
                        f.add("#239", _rel(root, py, node.lineno),
                              "bypass 예외가 도메인을 import 한다 — 도메인 예외를 상속하지 않는다")
            if py.stem.endswith("_query"):
                want = f"{_camel(cap.name)}DomainBypassQuery"
                for cls in [n for n in mod.body if isinstance(n, ast.ClassDef)]:
                    if not cls.name.endswith("DomainBypassQuery") or not cls.name.endswith(want):
                        f.add("#235", _rel(root, py, cls.lineno),
                              f"`{cls.name}` — 계약은 `{want}` 로 끝난다(구현은 접두사로 갈린다)")
                    for m in [n for n in cls.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]:
                        names = _ann_names(m.returns)
                        if names & {"QuerySet", "dict", "Dict"} or any(n.endswith("Model") for n in names):
                            f.add("#236", _rel(root, py, m.lineno),
                                  f"`{m.name}` 반환 {sorted(names)[:3]} — 내보내는 자료는 «이름 붙인 "
                                  "정적 타입» 하나다(도메인·ORM 로우·QuerySet ✗)")


def _check_uow_port(root: Path, uow: Path, f: Findings) -> None:
    if (uow / "exception.py").is_file():
        f.add("#242", _rel(root, uow / "exception.py"),
              "unit_of_work/ 에 exception.py — 두지 않는다(실패는 저장 계약의 몫이 아니다)")
    for py in sorted(uow.glob("*.py")):
        if py.name in ("__init__.py", "exception.py"):
            continue
        if not py.stem.endswith("_unit_of_work"):
            f.add("#244", _rel(root, py),
                  "저장 경계 하나 = 파일 하나 · 이름은 `<boundary>_unit_of_work.py` 다")
        mod = _parse(py)
        if mod is None:
            continue
        for cls in [n for n in mod.body if isinstance(n, ast.ClassDef)]:
            methods = {m.name for m in cls.body if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))}
            # #245 — 계약은 정확히 UOW_METHODS(판정 ② 2026-08-25 — dunder canon 실집행):
            # with 문이 정상·예외·조기 return 전 경로에서 __exit__(커밋/롤백)를 보장한다.
            # open/close 등 비-dunder 도, __call__ 등 여분 dunder 도 계약 밖이다.
            extra = methods - UOW_METHODS
            if extra:
                f.add("#245", _rel(root, py, cls.lineno),
                      f"계약 밖 메서드 {sorted(extra)} — UnitOfWork 의 계약은 셋"
                      "(__enter__/__exit__/after_commit)뿐이다")
            missing = (UOW_METHODS - {"__init__"}) - methods
            if missing:
                f.add("#245", _rel(root, py, cls.lineno),
                      f"계약 메서드 {sorted(missing)} 가 없다 — UnitOfWork 의 계약 셋"
                      "(__enter__/__exit__/after_commit)은 전부가 와야 한다")
            for node in ast.walk(cls):
                ann = None
                if isinstance(node, ast.AnnAssign):
                    ann = node.annotation
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.returns:
                    ann = node.returns
                if ann is not None and any(x.endswith("Repository") for x in _ann_names(ann)):
                    f.add("#246", _rel(root, py, node.lineno),
                          "리포지토리 타입 노출 — unit_of_work/ 의 클래스는 리포지토리를 노출하지 않는다")


# ── domain_layer 쪽 — #231 ─────────────────────────────────────────────────

def _check_domain_side(root: Path, bc: Path, f: Findings) -> None:
    domain = bc / "domain_layer"
    if not domain.is_dir():
        return
    for py in _py_files(domain):
        mod = _parse(py)
        for cls in [n for n in (mod.body if mod else []) if isinstance(n, ast.ClassDef)]:
            if cls.name.endswith("DomainBypassQuery"):
                f.add("#231", _rel(root, py, cls.lineno),
                      "애그리거트가 안 나오는 조회 계약이 domain_layer 에 있다 — 자리는 "
                      "application_layer/port/domain_bypass_query/ 다(#229)")


# ── driven adapter — #319~#376 · #464~#583 ─────────────────────────────────

def _aggregate_pending_api(domain: Path, agg: str) -> "tuple[str, set[str], set[str]]":
    """#545 부칙(2026-08-25) 적용 술어 — («full»|«half»|«none», pending 저장소, 조회 표면).

    적용은 이벤트 채택 애그리거트에 한한다(eventless root 에 가드를 강제하면 dead seam 뿐이다
    — saju SajuChart·billing 6종 실증). 채택 판별(2원):
      ⓑ 루트 파일의 pending 3요소 전건 — 사적 list 필드 + 그 필드의 조회 표면(tuple/bool/len/
         list 사본 반환 또는 bare 반환) + **같은 필드를 실제로 비우는 소거/소모 창구**(clear·
         빈 재대입 — 생성자 초기화는 제외. 소거 창구 요건이 SajuChart(_snapshots — append 만)
         오탐을 차단한다) → «full»(가드 검사)
      ⓐ ⓑ 미충족 + `event/` 비-`__init__` 실재 → «half»(반쪽 채택 — 가드 대상 API 가 없어
         준수 불능이므로 후보 발화)
      둘 다 아니면 «none»(비적용).
    """
    event_dir = domain / agg / "event"
    event_adopted = event_dir.is_dir() and any(
        p.suffix == ".py" and p.stem != "__init__" for p in event_dir.iterdir())
    root_py = domain / agg / f"{agg}.py"
    stores: set[str] = set()
    queries: set[str] = set()
    mod = _parse(root_py) if root_py.is_file() else None
    if mod is not None:
        for cls in [n for n in mod.body if isinstance(n, ast.ClassDef)]:
            fields: set[str] = set()
            for node in ast.walk(cls):
                if isinstance(node, ast.AnnAssign):
                    if isinstance(node.target, ast.Name):
                        fields.add(node.target.id)
                    elif isinstance(node.target, ast.Attribute) \
                            and isinstance(node.target.value, ast.Name) \
                            and node.target.value.id == "self":
                        fields.add(node.target.attr)
                if isinstance(node, ast.Assign):
                    for t in node.targets:
                        if isinstance(t, ast.Attribute) and isinstance(t.value, ast.Name) \
                                and t.value.id == "self":
                            fields.add(t.attr)
            fields = {n for n in fields if n.startswith("_")}
            queried: "dict[str, set[str]]" = {}
            consumed: set[str] = set()
            for m in [n for n in cls.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]:
                is_ctor = m.name in ("__init__", "__post_init__")
                for node in ast.walk(m):
                    ret = node.value if isinstance(node, ast.Return) else None
                    if isinstance(ret, ast.Call) and isinstance(ret.func, ast.Name) \
                            and ret.func.id in ("tuple", "bool", "len", "list") and ret.args:
                        a = ret.args[0]
                        if isinstance(a, ast.Attribute) and isinstance(a.value, ast.Name) \
                                and a.value.id == "self" and a.attr in fields:
                            queried.setdefault(a.attr, set()).add(m.name)
                    if isinstance(ret, ast.Attribute) and isinstance(ret.value, ast.Name) \
                            and ret.value.id == "self" and ret.attr in fields:
                        queried.setdefault(ret.attr, set()).add(m.name)
                    if is_ctor:
                        continue
                    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                            and node.func.attr == "clear" \
                            and isinstance(node.func.value, ast.Attribute) \
                            and isinstance(node.func.value.value, ast.Name) \
                            and node.func.value.value.id == "self" \
                            and node.func.value.attr in fields:
                        consumed.add(node.func.value.attr)
                    if isinstance(node, ast.Assign):
                        for t in node.targets:
                            if isinstance(t, ast.Attribute) and isinstance(t.value, ast.Name) \
                                    and t.value.id == "self" and t.attr in fields \
                                    and isinstance(node.value, (ast.List, ast.Tuple)) \
                                    and not getattr(node.value, "elts", None):
                                consumed.add(t.attr)
            # 채택 = 사적 저장소 + 실소거/소모 창구(둘이면 충분 — 08-15형 «store 직접
            # 비소모 읽기»가 항상 가능한 가드 표면이다). 조회 표면(queried)은 가드 조인
            # 인정 목록으로만 쓴다. 소거 창구 요건이 SajuChart(_snapshots — append 만)
            # 류 조회-전용 스냅숏의 오탐을 차단한다.
            for store in fields & consumed:
                stores.add(store)
                queries |= queried.get(store, set())
    if stores:
        return "full", stores, queries
    if event_adopted:
        return "half", set(), set()
    return "none", set(), set()


def _guard_polarity(test: ast.AST, target: ast.AST) -> "bool | None":
    """질의 노드까지의 경로 극성 — True=잔존(truthy) 경로에서 raise 도달 · None=판별 불능.

    부정형 블랙리스트: `not`·`== 0`/`is None`(0·None·False 비교)·판별 불능 래핑. `len(x) > 0`·
    `!= 0`·`bool(x)`·bare truthy·or/and 합성(진리 유지)은 양성. 불인정이면 이 질의는 가드가
    아니다(fail-closed — «빈-경우-raise» 정당 판정(event_stream)을 보존한다).
    """
    path: "list[ast.AST]" = []

    def _find(node: ast.AST, anc: "list[ast.AST]") -> bool:
        if node is target:
            path.extend(anc)
            return True
        return any(_find(c, anc + [node]) for c in ast.iter_child_nodes(node))

    if not _find(test, []):
        return None
    neg = 0
    prev: ast.AST = target
    for anc in reversed(path):
        if isinstance(anc, ast.UnaryOp) and isinstance(anc.op, ast.Not):
            neg += 1
        elif isinstance(anc, ast.Compare):
            if prev is not anc.left or len(anc.ops) != 1:
                return None
            op, cmpv = anc.ops[0], anc.comparators[0]
            zeroish = isinstance(cmpv, ast.Constant) and (cmpv.value is None or cmpv.value == 0
                                                          or cmpv.value is False)
            if isinstance(op, (ast.Eq, ast.Is)) and zeroish:
                neg += 1
            elif isinstance(op, (ast.NotEq, ast.IsNot)) and zeroish:
                pass
            elif isinstance(op, (ast.Gt, ast.GtE)) and isinstance(cmpv, ast.Constant) \
                    and cmpv.value == 0:
                pass
            else:
                return None
        elif isinstance(anc, ast.Call) and isinstance(anc.func, ast.Name) \
                and anc.func.id in ("bool", "len", "tuple"):
            pass
        elif isinstance(anc, ast.BoolOp):
            pass
        else:
            return None
        prev = anc
    return neg % 2 == 0


def _save_event_guard_ok(save_fn: "ast.FunctionDef | ast.AsyncFunctionDef",
                         stores: set, queries: set) -> bool:
    """#545 의미 가드 창(부칙 2026-08-25) — 전건 충족 형태가 하나라도 있으면 True.

    ① 수신자 = save 매개변수(+동일 함수 단순 별칭) ② 질의 대상 = 적용 술어가 인정한 pending
    저장소/조회 표면(무관 질의 디코이 차단) ③ 극성 — 잔존(truthy) 경로의 raise(«빈-경우-
    raise»·죽은 분기 불인정) ④ raise 가 truthy 분기(body)에 있고 같은 함수 handler 에
    삼켜지지 않음 ⑤ 가드가 save body 의 첫 ORM 접촉(`objects` 체인) 이전. 이름 토큰의 단순
    존재(죽은 분기·지역 이름·무관 수신자)는 가드가 아니다.
    """
    params = {a.arg for a in save_fn.args.args + save_fn.args.kwonlyargs if a.arg != "self"}
    aliases = set(params)
    for node in ast.walk(save_fn):
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Name) \
                and node.value.id in aliases:
            for t in node.targets:
                if isinstance(t, ast.Name):
                    aliases.add(t.id)
    surface = stores | queries
    orm_line: "int | None" = None
    for node in ast.walk(save_fn):
        if isinstance(node, ast.Attribute) and node.attr == "objects":
            ln = getattr(node, "lineno", None)
            if ln is not None and (orm_line is None or ln < orm_line):
                orm_line = ln
    tries = [n for n in ast.walk(save_fn) if isinstance(n, ast.Try)]

    def _swallowed(raise_node: ast.Raise, host_if: ast.If) -> bool:
        rname = ""
        if isinstance(raise_node.exc, ast.Call) and isinstance(raise_node.exc.func, ast.Name):
            rname = raise_node.exc.func.id
        elif isinstance(raise_node.exc, ast.Name):
            rname = raise_node.exc.id
        for ty in tries:
            in_body = any(raise_node in ast.walk(s) for s in ty.body)
            if not in_body:
                continue
            for h in ty.handlers:
                names: list[str] = []
                if isinstance(h.type, ast.Name):
                    names = [h.type.id]
                elif isinstance(h.type, ast.Tuple):
                    names = [e.id for e in h.type.elts if isinstance(e, ast.Name)]
                elif h.type is None:
                    return True
                if any(n in _BROAD_HANDLER_NAMES or n == rname for n in names):
                    return True
        return False

    for stmt in ast.walk(save_fn):
        if not isinstance(stmt, ast.If):
            continue
        if isinstance(stmt.test, ast.Constant) and not stmt.test.value:
            continue
        if any(isinstance(c, ast.Constant) and c.value is False
               for b in ast.walk(stmt.test)
               if isinstance(b, ast.BoolOp) and isinstance(b.op, ast.And)
               for c in b.values):
            continue
        hits = [n for n in ast.walk(stmt.test)
                if isinstance(n, ast.Attribute) and n.attr in surface
                and isinstance(n.value, ast.Name) and n.value.id in aliases]
        if not any(_guard_polarity(stmt.test, q) is True for q in hits):
            continue
        if orm_line is not None and stmt.lineno >= orm_line:
            continue
        raises = [n for s in stmt.body for n in ast.walk(s)
                  if isinstance(n, ast.Raise) and n.exc is not None]
        if any(not _swallowed(r, stmt) for r in raises):
            return True
    return False


def _check_driven(root: Path, bc: Path, agg_names: set, bc_vocab_set: set,
                  f: Findings, cand: Candidates) -> None:
    driven = _driven(bc)
    if driven is None:
        return
    for d in driven.rglob("*"):
        if d.is_dir() and d.name in ("read_model", "query_model") and not set(d.parts) & SKIP_DIRS:
            f.add("#350", _rel(root, d),
                  "read_model/ — Thin Read 구현은 adapter/persistence/domain_bypass_query/ 에 산다")
    for dj in bc.glob("django_*"):
        if (dj / "repository").is_dir():
            f.add("#349", _rel(root, dj / "repository"),
                  "repository/ 가 django_<bc>/ 안에 있다 — 형제로 둔다(구현은 애그리거트와 "
                  "ORM 모델을 «동시에» import 해야 한다)")
    adapter = driven / "adapter"
    if not adapter.is_dir():
        return
    persistence = adapter / "persistence"
    # persistence/repository — #351 · #352 · #354 · #464 · #477 · #545.
    repo_dir = persistence / "repository"
    decl_stems = set()
    domain = bc / "domain_layer"
    if domain.is_dir():
        # 빈 골격 선언(주석·docstring뿐)은 선언이 아니다 — 구현 의무 제외, 단 그 자리에
        # 구현이 실재하면 orphan 으로 잡힌다(빈 계약의 구현 — 판정 ④ 2026-08-25).
        decl_stems = {p.stem for p in domain.glob("*/*_repository.py")
                      if not checker_target.skeleton_placeholder(p)}
    impl_stems = set()
    if repo_dir.is_dir():
        for p in sorted(repo_dir.iterdir()):
            if p.is_dir() and p.name != "__pycache__":
                if p.name in ("command", "query"):
                    f.add("#464", _rel(root, p),
                          "command/query 로 가르지 않는다 — 가르는 축은 「도메인을 거쳤나」다")
                    continue
                # 동명 폴더 승격(#490 교체형 — 2026-09-01): <agg>_repository/ 에 본체가
                # 실존하면 본체를 구현 파일로 취급한다(형태 검증은 registry #4 소유).
                if p.name.endswith("_repository") and (p / f"{p.name}.py").is_file():
                    continue
                f.add("#352", _rel(root, p),
                      "리포지토리 구현은 폴더가 아니라 파일이다(애그리거트당 하나)")
        for py in checker_target.slot_glob(repo_dir, "*_repository.py"):
            impl_stems.add(py.stem)
            agg = py.stem[: -len("_repository")]
            mod = _parse(py)
            if mod is None:
                continue
            imports_domain = any(
                isinstance(n, ast.ImportFrom) and "domain_layer" in (n.module or "")
                for n in ast.walk(mod))
            if not imports_domain:
                f.add("#477", _rel(root, py),
                      "구현이 domain_layer 를 import 하지 않는다 — 번역자는 애그리거트와 ORM "
                      "모델을 동시에 알아야 한다")
            want = f"Django{_camel(agg)}Repository"
            for cls in [n for n in mod.body if isinstance(n, ast.ClassDef) and not n.name.startswith("_")]:
                if cls.name != want:
                    f.add("#354", _rel(root, py, cls.lineno),
                          f"`{cls.name}` — 구현 클래스는 `{want}` 다(역할 이름은 선언과 공유하고 "
                          "기술 접두사가 가른다)")
                if not any(b.endswith("Repository") for b in _bases(cls)):
                    f.add("#552", _rel(root, py, cls.lineno),
                          f"`{cls.name}` 이 계약을 상속하지 않는다 — 상속만 하면 미구현을 런타임이 "
                          "잡는다(D44)")
                for m in [n for n in cls.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]:
                    if m.name == "save":
                        # 스펙 대장 #545 부칙(2026-08-25) — 적용 술어(이벤트 채택 애그리거트
                        # 한정) + 의미 가드 창(토큰 존재가 아니라 잔존-시-raise 의 의미 검사).
                        mode, stores, queries = _aggregate_pending_api(domain, agg)
                        if mode == "full":
                            if not _save_event_guard_ok(m, stores, queries):
                                f.add("#545", _rel(root, py, m.lineno),
                                      "save() 에 «안 꺼낸 사실» 가드가 없다 — 남아 있으면 예외를 던진다"
                                      "(사실 발행 세 걸음의 ②가 ③보다 앞이다 — D59)")
                        elif mode == "half":
                            cand.add("#545", _rel(root, py, m.lineno),
                                     f"`{agg}` 는 event/ 만 있고 루트 pending 상태/API 가 없다 — "
                                     "가드 대상이 없어 준수 불능(반쪽 채택)",
                                     "이벤트 채택을 완성할 것인가, event/ 를 걷어낼 것인가")
        for missing in sorted(decl_stems - impl_stems):
            f.add("#351", _rel(root, repo_dir),
                  f"선언 `{missing}.py` 의 구현이 없다 — 선언마다 구현이 «정확히 하나» 있다")
        for orphan in sorted(impl_stems - decl_stems):
            f.add("#351", _rel(root, repo_dir / f"{orphan}.py"),
                  "선언 없는 리포지토리 구현 — 1:1 은 양방향이다(#583)")
    # persistence/domain_bypass_query — #356 · #359 · #583.
    thin = persistence / "domain_bypass_query"
    port_bypass = bc / "application_layer" / "port" / "domain_bypass_query"
    if thin.is_dir():
        contract_caps = {p.name for p in port_bypass.iterdir() if p.is_dir()} \
            if port_bypass.is_dir() else set()
        for py in checker_target.slot_glob(thin, "*_query.py"):
            capname = py.stem[: -len("_query")]
            if contract_caps and capname not in contract_caps:
                f.add("#583", _rel(root, py),
                      "계약 없는 Thin Read 구현 — repository·unit_of_work·domain_bypass_query "
                      "셋은 1:1 이 «양방향»이다")
            mod = _parse(py)
            if mod is None:
                continue
            for node in ast.walk(mod):
                if isinstance(node, ast.ImportFrom) and "domain_layer" in (node.module or ""):
                    f.add("#356", _rel(root, py, node.lineno),
                          "Thin Read 가 domain_layer 를 import 한다 — 이 길은 도메인을 «안» 거친다")
            want = f"Django{_camel(capname)}DomainBypassQuery"
            for cls in [n for n in mod.body if isinstance(n, ast.ClassDef) and not n.name.startswith("_")]:
                if cls.name != want:
                    f.add("#359", _rel(root, py, cls.lineno), f"`{cls.name}` — 구현 이름은 `{want}` 다")
    # persistence/unit_of_work — #374 · #376 · #476 · #566.
    uow_impl = persistence / "unit_of_work"
    port_uow = bc / "application_layer" / "port" / "unit_of_work"
    decl_uows = {p.stem for p in port_uow.glob("*_unit_of_work.py")} if port_uow.is_dir() else set()
    impl_uows = set()
    if uow_impl.is_dir():
        for py in checker_target.slot_glob(uow_impl, "*.py"):
            if py.name == "__init__.py":
                continue
            if not py.stem.endswith("_unit_of_work"):
                f.add("#374", _rel(root, py),
                      "UnitOfWork 구현은 `<boundary>_unit_of_work.py` 파일이다(경계 하나에 하나)")
                continue
            impl_uows.add(py.stem)
            mod = _parse(py)
            if mod is None:
                continue
            for cls in [n for n in mod.body if isinstance(n, ast.ClassDef)]:
                for m in [n for n in cls.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]:
                    if m.name != "after_commit":
                        continue
                    on_commits = [n for n in ast.walk(m)
                                  if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                                  and n.func.attr == "on_commit"]
                    if not on_commits:
                        f.add("#376", _rel(root, py, m.lineno),
                              "after_commit 구현이 transaction.on_commit 으로 채워지지 않았다")
                    for c in on_commits:
                        robust = {kw.arg for kw in c.keywords}
                        if "robust" not in robust:
                            f.add("#566", _rel(root, py, c.lineno),
                                  "on_commit 에 robust 미지정 — 장고 기본값은 앞 콜백 실패로 "
                                  "뒤 콜백이 «통째로» 사라지는 모양이다(사실 발행 콜백 금지 자리)")
    for missing in sorted(decl_uows - impl_uows):
        f.add("#476", _rel(root, persistence if persistence.is_dir() else driven),
              f"UoW 선언 `{missing}.py` 의 구현이 없다 — 1:1 이다(검사는 폴더 목록 두 번)")
    for orphan in sorted(impl_uows - decl_uows):
        f.add("#476", _rel(root, uow_impl / f"{orphan}.py"), "선언 없는 UoW 구현 — 1:1 이다")
    # adapter 갈래·소켓·이름 — #319 · #367 · #369 · #370 · #371~373 · #582 · #365.
    _check_adapter_families(root, bc, adapter, agg_names, bc_vocab_set, f, cand)


# #365 부칙(2026-08-25) — 통신 축: 이들 top-level import(또는 `__import__` 호출)가 하나라도
# 있으면 «순수 스텁»이 아니다. SOCKET_LIBS(벤더)와 합집합으로 쓴다. importlib·asyncio 는
# 동적 import·소켓 우회 채널이라 포함한다.
_COMM_AXIS_STDLIB = frozenset({
    "urllib", "http", "socket", "ssl", "subprocess", "importlib", "asyncio",
    "ftplib", "xmlrpc", "telnetlib", "smtplib", "poplib", "imaplib", "socketserver",
})


def _acl_target_pure(root: Path, bc: Path, target_dir: Path) -> bool:
    """스냅숏 부재 대상 ACL 의 구조 순수성 — import 가 자기 BC·framework·비통신 stdlib 뿐인가.

    벤더(SOCKET_LIBS·미지의 서드파티)·통신 stdlib·`__import__` 호출이 하나라도 있으면 False
    (fail-closed — 미지 top-level 은 서드파티로 간주해 불인정).
    """
    import sys as _sys
    stdlib = getattr(_sys, "stdlib_module_names", frozenset())
    for py in _py_files(target_dir):
        mod = _parse(py)
        if mod is None:
            return False
        for node in ast.walk(mod):
            fulls: list[str] = []
            if isinstance(node, ast.Import):
                fulls = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                if node.level:  # 상대 import — BC 안을 못 벗어난다
                    continue
                fulls = [node.module or ""]
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
                    and node.func.id == "__import__":
                return False
            for full in fulls:
                top = full.split(".", 1)[0]
                if top in _COMM_AXIS_STDLIB or top in SOCKET_LIBS:
                    return False
                if top == "application":
                    segs = full.split(".")
                    if len(segs) < 2 or segs[1] != bc.name:
                        return False
                    continue
                if top == "framework" or top in stdlib:
                    continue
                return False
    return True


_BROAD_HANDLER_NAMES = frozenset({"Exception", "BaseException"})


def _is_declared_error_module(module: str, bc_name: str) -> bool:
    """«같은 BC» 선언 오류 모듈 — port/**/exception.py(파일형)·domain_layer/**/exception(폴더형).

    BC 세그먼트를 현 BC 와 대조한다(대조 리뷰 2026-08-25 — 타 BC 선언 오류의 재던짐은
    이 인정의 대상이 아니다: 그 import 자체는 격리 규칙 소관이되 #555 는 fail-closed).
    """
    if not module.startswith("application."):
        return False
    segs = module.split(".")
    if len(segs) < 2 or segs[1] != bc_name:
        return False
    if ".application_layer.port." in module and module.endswith(".exception"):
        return True
    if ".domain_layer." in module and (module.endswith(".exception") or ".exception." in module):
        return True
    return False


def _handler_declared_error(root: Path, bc_name: str, mod: ast.Module, handler: ast.ExceptHandler) -> bool:
    """#555 재던짐 인정 — handler 가 잡는 타입이 «계약이 선언한 실패»인가(전건 충족만 True).

    ① 이름이 같은 BC 선언 오류 모듈에서의 ImportFrom 바인딩이고 ② 그 심볼이 대상 모듈의
    ClassDef 이며(별칭 Assign 세탁 불인정) ③ 현 모듈 내 재바인딩이 없고 ④ 튜플이면 전 원소
    충족. 광역 이름은 출처와 무관하게 불인정(블랙리스트 우선). Attribute 형·해석 불능은
    불인정(fail-closed). builtin 상속 여부는 판별에 쓰지 않는다(포트 오류가 ValueError
    서브클래스인 실물 — kkebi).
    """
    t = handler.type
    if t is None:
        return False
    names = [t] if isinstance(t, ast.Name) else (list(t.elts) if isinstance(t, ast.Tuple) else None)
    if not names or not all(isinstance(n, ast.Name) for n in names):
        return False
    imports: dict[str, tuple[str, str]] = {}  # 지역 이름 → (모듈, 원 심볼)
    rebound: set[str] = set()
    for node in mod.body:
        if isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            for alias in node.names:
                imports[alias.asname or alias.name] = (node.module, alias.name)
        if isinstance(node, ast.Assign):
            for tgt in node.targets:
                if isinstance(tgt, ast.Name):
                    rebound.add(tgt.id)
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) \
                and node.value is not None:
            rebound.add(node.target.id)
    for n in names:
        if n.id in _BROAD_HANDLER_NAMES or n.id in rebound or n.id not in imports:
            return False
        module, symbol = imports[n.id]
        if not _is_declared_error_module(module, bc_name):
            return False
        target = root / (module.replace(".", "/") + ".py")
        target_mod = _parse(target) if target.is_file() else None
        if target_mod is None:
            return False
        if not any(isinstance(s, ast.ClassDef) and s.name == symbol for s in target_mod.body):
            return False
    return True


def _check_adapter_families(root: Path, bc: Path, adapter: Path, agg_names: set,
                            bc_vocab_set: set, f: Findings, cand: Candidates) -> None:
    acl = adapter / "anticorruption_layer"
    if acl.is_dir():
        bcs = vocab.bc_names(root)
        for d in sorted(p for p in acl.iterdir() if p.is_dir() and p.name != "__pycache__"):
            if d.name not in bcs:
                # 스펙 대장 #365 부칙(2026-08-25) — «우리 BC»는 병렬 워크트리 개발로 이
                # 스냅숏에 없는 자사 BC 를 포함한다. 대상 부재 시 구조 순수성(통신 축
                # import 0 — 자기 BC·framework·비통신 stdlib 뿐)이면 후보로 강등하고,
                # 통신 축이 하나라도 있으면 위반 유지(외부 시스템의 ACL 위장 차단).
                if _acl_target_pure(root, bc, d):
                    cand.add("#365", _rel(root, d),
                             f"acl/{d.name}/ — 이 스냅숏에 없는 대상(순수 스텁 — 통신 import 0)",
                             "병렬 워크트리에서 개발 중인 «우리 BC»인가, 외부 시스템인가")
                else:
                    f.add("#365", _rel(root, d),
                          f"acl/{d.name}/ — 우리가 못 고치고 계약이 저장소 밖인 상대는 "
                          "external_system/ 이다(anticorruption_layer 는 «우리 다른 BC» 전용)")
    ext = adapter / "external_system"
    if ext.is_dir():
        for p in sorted(ext.iterdir()):
            if p.is_file() and p.suffix == ".py" and p.name != "__init__.py":
                f.add("#369", _rel(root, p), "external_system/ 직계 파일 — 벤더 하나 = 폴더 하나다")
        for system in sorted(p for p in ext.iterdir() if p.is_dir() and p.name != "__pycache__"):
            for py in checker_target.slot_glob(system, "*.py"):
                if py.name == "__init__.py":
                    continue
                mod = _parse(py)
                if mod is None:
                    continue
                for cls in [n for n in mod.body if isinstance(n, ast.ClassDef) and not n.name.startswith("_")]:
                    if not (cls.name.endswith("Adapter") and cls.name.startswith(_camel(system.name))):
                        f.add("#370", _rel(root, py, cls.lineno),
                              f"`{cls.name}` — 바깥 시스템 어댑터는 `<System><Capability>Adapter` 다")
                for n in ast.walk(mod):
                    if isinstance(n, ast.ClassDef) and any(
                            w in n.name for w in ("Breaker", "Limiter", "Retry")):
                        cand.add("#368", _rel(root, py, n.lineno),
                                 f"`{n.name}` 정의 — 값(몇 초·몇 번)은 여기, «기계»(차단기·백오프)는 "
                                 "framework 가 준다(#556)", "이게 «기계»인가 «값»인가")
    # 소켓 import 전수(#367) · 재시도 기계(#556) · 예외 흘림(#554·#555) · 판정(#553·#557 은 아래 응용).
    driven = adapter.parent
    for py in _py_files(driven):
        parts = py.relative_to(driven).parts
        mod = _parse(py)
        if mod is None:
            continue
        # 동명 폴더 승격 — <capability>_adapter/ 승격 폴더 안 부품도 어댑터 몸통이다(#367 면제).
        in_ext_adapter = "external_system" in parts and (
            py.stem.endswith("_adapter")
            or (py.parent.name.endswith("_adapter")
                and (py.parent / f"{py.parent.name}.py").is_file()))
        for node in ast.walk(mod):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                mods = [a.name for a in node.names] if isinstance(node, ast.Import) \
                    else [node.module or ""]
                for m in mods:
                    top = m.split(".")[0]
                    if top in SOCKET_LIBS and not in_ext_adapter:
                        f.add("#367", _rel(root, py, node.lineno),
                              f"소켓 여는 `{top}` import — external_system/<system>/<capability>"
                              "_adapter.py 안에서만 허용된다(브로커·캐시·메일도 들어온다 — "
                              "목록은 저장소 의존성에 맞춰 유지하는 데이터다)")
                    if top in RETRY_LIBS:
                        f.add("#556", _rel(root, py, node.lineno),
                              f"재시도 «기계» `{top}` — 판정은 driven, 기계는 framework, 다시 "
                              "부르기는 입구다(셋을 한 칸에 뭉치면 위반)")
        if "adapter" in parts and py.stem.endswith("_adapter"):
            cap_dir = py.parent
            # 동명 폴더 승격 — 본체(<technology>_adapter/<technology>_adapter.py)면
            # 능력 폴더는 승격 폴더의 한 단 위다.
            if cap_dir.name == py.stem:
                cap_dir = cap_dir.parent
            if cap_dir.parent == adapter and cap_dir.name not in (
                    "persistence", "anticorruption_layer", "acl", "external_system"):
                if py.stem == f"{cap_dir.name}_adapter":
                    f.add("#582", _rel(root, py),
                          "파일이 폴더를 되풀이한다 — 한 포트에 어댑터가 여럿일 수 있어 파일은 "
                          "«어느 기술인가»를 말한다(<technology>_adapter.py)")
                tech_stem = py.stem[: -len("_adapter")]
                want = f"{_camel(tech_stem)}{_camel(cap_dir.name)}Adapter"
                for cls in [n for n in mod.body if isinstance(n, ast.ClassDef) and not n.name.startswith("_")]:
                    if cls.name.endswith("Adapter") and cls.name != want:
                        f.add("#373", _rel(root, py, cls.lineno),
                              f"`{cls.name}` — 나머지 어댑터 클래스는 `{want}` 다(#371 자리)")
                    if not any(b.endswith("Port") for b in _bases(cls)):
                        f.add("#552", _rel(root, py, cls.lineno),
                              f"`{cls.name}` 이 포트 계약을 상속하지 않는다(D44)")
        # #319(갈래 판정)의 실체는 방향별 소유자가 진다 — ORM→#462 · 소켓→#367 ·
        # 벤더 폴더→#365 · 타 BC→ctx. 여기서 다시 물면 중복 진단이다.
        # #554 · #555 — 예외 번역. 측정 정밀화(2026-08-25): 이미 번역된 «계약이 선언한
        # 실패»를 잡아 관찰(내구 기록) 후 그대로 재던지는 bare raise 는 벤더 누수가 아니다 —
        # handler 타입을 보고 가린다(_handler_declared_error · 성문 #555 문면은 벤더·django
        # 예외만 겨눈다 — kkebi billing 이관 어댑터 실물 판형).
        if "adapter" in parts:
            for node in ast.walk(mod):
                if isinstance(node, ast.Try):
                    for h in node.handlers:
                        h_declared = _handler_declared_error(root, bc.name, mod, h)
                        for n in ast.walk(h):
                            if isinstance(n, ast.Raise):
                                if n.exc is None:
                                    if h_declared:
                                        continue
                                    f.add("#555", _rel(root, py, n.lineno),
                                          "벤더·django 예외를 «그대로» 위로 흘린다 — 전역 제약 ②가 "
                                          "«실패의 모양»으로 깨진다(계약이 선언한 실패로 바꾼다)")
                                elif isinstance(n.exc, ast.Call) and isinstance(n.exc.func, ast.Name) \
                                        and n.exc.func.id in ("Exception", "RuntimeError", "ValueError"):
                                    f.add("#554", _rel(root, py, n.lineno),
                                          f"`{n.exc.func.id}` 로 바꾼다 — 어댑터는 «계약이 선언한 실패»"
                                          "로만 바꾼다(리포지토리면 도메인 예외, 능력 포트면 포트 예외)")
    # #462 — ORM 모델 import 는 persistence 셋 + django_<bc>/admin/ + capability 의
    # django 어댑터 뿐.
    # admin/ 면제는 트리 정본과의 짝맞춤이다: §1 트리가 django_<bc>/admin/<entity>/
    # (panel·form/·feature/) 칸을 명시하는데 관리 패널은 ModelAdmin 등록에 ORM 모델이
    # 필수라, 면제 없이는 그 칸의 어떤 준수 구현도 불가능했다(2026-08-15 S3-r2′ 실증).
    # capability django 어댑터 면제(#462 확장 — 2026-08-24): §1 트리 103~104행
    # adapter/<capability>/<technology>_adapter.py 의 django 기술 구현. #319 ORM
    # 갈래의 persistence 셋에는 «비애그리거트 ORM 쓰기 능력»의 칸이 없어(리포지토리=
    # 애그리거트 전용 #354 · bypass=조회 전용 #236) 그 능력 포트 구현이 여기 온다 —
    # admin 과 같은 «트리 짝맞춤» 계열(2호 실증: 실전 런의 정본 덱 적재·이관 대상
    # 대량 프로모션 능력, 사용자 A안 승인). 성문 = houserules §5 «driven 출구
    # 면제»(R-3423 — 리비전 10호 채번·#328 check-context-isolation 정합 동기).
    for py in _py_files(driven):
        parts = py.relative_to(driven).parts
        if "persistence" in parts or "models" in parts or py.parent.name == "models":
            continue
        if len(parts) >= 2 and parts[0].startswith("django_") and parts[1] == "admin":
            continue
        if (len(parts) == 3 and parts[0] == "adapter"
                and parts[1] not in ("anticorruption_layer", "external_system")
                and parts[2] == "django_adapter.py"):
            continue
        # 동명 폴더 승격 — django_adapter.py 가 django_adapter/ 로 승격돼도 면제는 유지된다.
        if (len(parts) == 4 and parts[0] == "adapter"
                and parts[1] not in ("anticorruption_layer", "external_system")
                and parts[2] == "django_adapter" and parts[3] == "django_adapter.py"):
            continue
        mod = _parse(py)
        for node in ast.walk(mod) if mod else []:
            if isinstance(node, ast.ImportFrom) and re.search(r"(^|\.)models(\.|$)", node.module or ""):
                f.add("#462", _rel(root, py, node.lineno),
                      "ORM 모델 import — 허용은 adapter/persistence/ 아래 셋(repository·"
                      "domain_bypass_query·unit_of_work)·django_<bc>/admin/·"
                      "adapter/<capability>/ 의 django_adapter.py 뿐이다")


# ── fake — #575~#581 ───────────────────────────────────────────────────────

def _check_fake(root: Path, bc: Path, f: Findings) -> None:
    fake = bc / "test" / "fake"
    decl_stems: set[str] = set()
    port = bc / "application_layer" / "port"
    if port.is_dir():
        decl_stems |= {p.stem for p in port.rglob("*_port.py")}
        decl_stems |= {p.stem for p in port.rglob("*_query.py")}
        decl_stems |= {p.stem for p in port.rglob("*_unit_of_work.py")}
    domain = bc / "domain_layer"
    if domain.is_dir():
        decl_stems |= {p.stem for p in domain.glob("*/*_repository.py")}
    if fake.is_dir():
        for p in sorted(fake.iterdir()):
            if p.is_dir() and p.name != "__pycache__":
                f.add("#581", _rel(root, p), "test/fake/ 아래 겹 — 평평하다(경로만 길어진다)")
        for py in sorted(fake.glob("*.py")):
            if py.name == "__init__.py":
                continue
            if py.stem not in decl_stems:
                f.add("#576", _rel(root, py),
                      f"`{py.stem}` 의 짝이 될 «선언»이 없다 — 검사는 한 방향뿐이다"
                      "(선언에 페이크를 강제하지는 않는다)")
            mod = _parse(py)
            if mod is None:
                continue
            for cls in [n for n in mod.body if isinstance(n, ast.ClassDef)]:
                bases = _bases(cls)
                if not any(b.endswith(("Port", "Repository", "UnitOfWork", "DomainBypassQuery"))
                           for b in bases):
                    f.add("#577", _rel(root, py, cls.lineno),
                          f"`{cls.name}` 이 선언을 상속하지 않는다 — 페이크는 선언 상속·같은 파일 "
                          "이름으로 짝을 진다")
            for node in ast.walk(mod):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    mods = [a.name for a in node.names] if isinstance(node, ast.Import) \
                        else [node.module or ""]
                    if any(m.split(".")[0] in ("django", "requests", "httpx", "boto3", "redis")
                           for m in mods):
                        f.add("#578", _rel(root, py, node.lineno),
                              "페이크가 기술을 만진다(DB·네트워크) — 그건 페이크가 아니라 어댑터다")
    # #575 — fake 이름의 파일이 test/fake 밖에.
    for py in _py_files(bc):
        parts = py.relative_to(bc).parts
        if "fake" in py.stem and not ("test" in parts and "fake" in parts) \
                and "test" not in parts[:1]:
            f.add("#575", _rel(root, py),
                  "포트의 «가짜 구현»이 test/fake/ 밖에 있다 — 숨겨 두면 다른 의미군이 무심코 "
                  "가져다 쓴다")
    # #579 · #580 — 프로덕션의 페이크 import.
    for py in _py_files(bc):
        parts = py.relative_to(bc).parts
        if "test" in parts:
            continue
        mod = _parse(py)
        for node in ast.walk(mod) if mod else []:
            if isinstance(node, ast.ImportFrom) and ".fake" in "." + (node.module or ""):
                rule = "#580" if "composition_root" in parts else "#579"
                msg = ("dependency_wiring 이 페이크를 꽂는다 — 설정·플래그로 켠다면 그건 진짜 "
                       "어댑터라 adapter/<capability>/ 에 산다"
                       if rule == "#580" else
                       "프로덕션 코드가 페이크를 import 한다 — 배포에 실리는 순간 가짜가 진짜 "
                       "자리에 선다")
                f.add(rule, _rel(root, py, node.lineno), msg)


# ── 응용·입구 쪽 — #134 · #574 · #475 · #553 · #557 · #460 ─────────────────

def _check_use_side(root: Path, bc: Path, bc_vocab_set: set, f: Findings, cand: Candidates) -> None:
    app = bc / "application_layer"
    if app.is_dir():
        for py in _py_files(app):
            parts = py.relative_to(app).parts
            if py.stem.endswith("_adapter") and "port" not in parts:
                f.add("#460", _rel(root, py),
                      "구현(*_adapter.py)이 driven_layer/adapter/ 밖에 있다 — 구현은 전부 거기 산다")
            mod = _parse(py)
            if mod is None:
                continue
            in_syms: set[str] = set()
            bypass_syms: set[str] = set()
            for node in ast.walk(mod):
                if isinstance(node, ast.ImportFrom):
                    m = node.module or ""
                    if m.endswith("_in") and ("port" in m or "framework" in m):
                        in_syms |= {a.asname or a.name for a in node.names}
                    if "domain_bypass_query" in m:
                        bypass_syms |= {a.asname or a.name for a in node.names}
            for node in ast.walk(mod):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
                        and node.func.id in in_syms:
                    f.add("#574", _rel(root, py, node.lineno),
                          f"유스케이스가 `{node.func.id}`(<data>_in) 를 만든다 — 여기 오는 것은 "
                          "«바깥이 답한 것»이라 만드는 것은 어댑터뿐이다")
            # #475 — bypass 결과의 업무 판정(후보).
            bound: set[str] = set()
            for node in ast.walk(mod):
                if isinstance(node, ast.arg) and node.annotation is not None:
                    names = {x.id for x in ast.walk(node.annotation) if isinstance(x, ast.Name)}
                    if any(n.endswith("DomainBypassQuery") for n in names):
                        bound.add(node.arg)
                if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call) \
                        and isinstance(node.value.func, ast.Attribute) \
                        and isinstance(node.value.func.value, ast.Name) \
                        and node.value.func.value.id in bound and len(node.targets) == 1 \
                        and isinstance(node.targets[0], ast.Name):
                    bound.add(node.targets[0].id)
            if bound:
                for node in ast.walk(mod):
                    if isinstance(node, ast.If):
                        used = {x.id for x in ast.walk(node.test) if isinstance(x, ast.Name)}
                        if used & bound:
                            cand.add("#475", _rel(root, py, node.lineno),
                                     "domain_bypass_query 결과가 조건식에 흐른다 — 이 자료는 도메인 "
                                     "규칙을 안 태운 «날것»이다", "Q2 — 이 판정이 업무 규칙인가")
            # #557 — 벤더 오류 코드 판정이 위층에.
            for node in ast.walk(mod):
                if isinstance(node, ast.Compare) and isinstance(node.left, ast.Attribute) \
                        and node.left.attr in ("code", "errno", "status_code"):
                    f.add("#557", _rel(root, py, node.lineno),
                          "벤더 오류 코드를 위층이 판정한다 — 일시 실패의 정규화는 그 인프라를 "
                          "«소유한» 어댑터가 한다")
    for layer in DRIVING_DIRS:
        base = bc / layer
        if not base.is_dir():
            continue
        for py in _py_files(base):
            if not py.name.endswith("_controller.py"):
                continue
            mod = _parse(py)
            for node in ast.walk(mod) if mod else []:
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and (
                        node.func.id.endswith(("UseCase", "Repository", "Adapter"))):
                    f.add("#134", _rel(root, py, node.lineno),
                          f"컨트롤러가 `{node.func.id}` 를 직접 만든다 — 매 요청 build_<use_case>() "
                          "를 부른다(직접 생성 금지)")
    # 어댑터의 업무 판정(#553 후보) — driven 어댑터 파일의 조건식에 업무 어휘.
    driven = _driven(bc)
    if driven is not None:
        for py in _py_files(driven):
            if not py.stem.endswith("_adapter"):
                continue  # 리포지토리는 번역자라 도메인 어휘 접촉이 정상 — #553 후보는 어댑터만.
            mod = _parse(py)
            for node in ast.walk(mod) if mod else []:
                if isinstance(node, ast.If):
                    toks = set()
                    for x in ast.walk(node.test):
                        if isinstance(x, ast.Attribute):
                            toks |= vocab.tokens(x.attr)
                        elif isinstance(x, ast.Name):
                            toks |= vocab.tokens(x.id)
                    if toks & bc_vocab_set:
                        cand.add("#553", _rel(root, py, node.lineno),
                                 f"어댑터 조건식에 업무 어휘 {sorted(toks & bc_vocab_set)[:3]} — "
                                 "어댑터는 «바꾸고 부르고 바꾼다» 셋뿐이다(D45)",
                                 "Q2 — 이 조건이 업무 규칙인가")


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
    if bcs and not any((bc / "application_layer").is_dir() or _driven(bc) is not None
                       for bc in bcs):
        guard = zero_target_guard(
            "blocker: 채택 신호는 있는데 application_layer/driven 층이 0건이다 — 조용한 무동작을 금지한다(#74)"
        )
        emit_all(guard, printer=print, indent="")
        return 2

    for bc in bcs:
        bc_vocab_set = vocab.bc_vocab(bc)
        domain = bc / "domain_layer"
        agg_names = {d.name for d in domain.iterdir()
                     if d.is_dir() and d.name not in ("shared_value_object", "domain_service", "__pycache__")} \
            if domain.is_dir() else set()
        _check_port_tree(root, bc, bc_vocab_set, tech, findings, cand)
        _check_domain_side(root, bc, findings)
        _check_driven(root, bc, agg_names, bc_vocab_set, findings, cand)
        _check_fake(root, bc, findings)
        _check_use_side(root, bc, bc_vocab_set, findings, cand)

    emit_all(cand, printer=print, indent="")
    if findings:
        print("blocker — 포트·어댑터 짝맞춤 위반 (선언은 port/·구현은 adapter/·페이크는 test/fake/ — D37·D44·D51·D57)")
        emit_all(findings, printer=print, indent="  ")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
