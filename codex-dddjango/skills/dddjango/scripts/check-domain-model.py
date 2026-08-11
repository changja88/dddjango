#!/usr/bin/env python3
"""dddjango 도메인 모델 검사기 — 애그리거트·엔티티·값 객체·도메인 서비스·도메인 이벤트(D12·D13·D50).

담당 규칙 (rule-owner-map · 총 50):
  #8   [ast]  domain_layer 의 밖으로 나가는 import 0 — django·다른 층·다른 BC·서드파티.
  #17  [ast+] domain/app 1차 축은 도메인 이름 — 확정: 종류 낱말 폴더(entity·service 류) /
              후보: 종류 인접 낱말(data·objects·types)(Q1).
  #18  [ast+] 종류 폴더가 개념 폴더와 형제 금지 — 트리 명문 형제(shared_value_object·
              domain_service·port)만 예외(#17 과 같은 술어로 묶어 문다).
  #249 [path] domain_layer 자식 = 애그리거트들 + shared_value_object + domain_service —
              직계 파일 금지.
  #252 [path] 1차에 entity/·value_object/ 금지 — 애그리거트 안으로 내린다.
  #253 [ast]  <A>/** 는 <B>/ 의 «루트 모듈»만 import — B 의 entity·value_object 직행 금지.
  #256 [ast]  애그리거트 폴더엔 폴더와 같은 이름의 <aggregate>.py + 루트 클래스.
  #257 [ast+] 상태 변경은 루트를 지난다 — 확정: 응용·입구의 «속성 접근 후 메서드 호출»
              (order.line.change(...)) / 후보: 끝에 불변식 확인 없는 루트 메서드(Q4).
  #258 [ast]  entity/ 직접 참조 금지 — 애그리거트 밖에서 붙잡는 것은 루트뿐.
  #259 [ast+] entity/ 판정은 식별자 — 후보: id 를 가진 value_object(자리 뒤바뀜 신호).
  #260 [ast]  entity/ 클래스는 식별자(id·*_id)를 가진다.
  #261 [ast]  엔티티 하나 = 파일 하나.        #262 [path] `_entity` 접미 금지.
  #263 [path] 이름 겹칠 때 `_model` 은 ORM 쪽만 — 도메인과 같은 stem 의 models 파일 금지.
  #264 [ast]  값 객체 불변 — __init__/__post_init__ 밖 self 대입 금지.
  #265 [ast]  <A>/value_object/ 는 그 애그리거트 밖에서 안 쓰인다 — #266 과 같은 술어라
              #266 의 진단이 함께 진다(중복 진단 금지 · 유스케이스의 값 변환은 정상이라 제외).
  #266 [ast]  다른 애그리거트가 쓰면 shared_value_object/ 로 올린다(도메인 쪽 사용 검출).
  #267 [ast]  값 객체 하나 = 파일 하나(shared 포함 — #459 와 같은 규칙).
  #268 [ast+] 후보: __init__/__post_init__ 에 raise 0 인 값 객체(Q2 — 잘못된 값이 불가능한가).
  #269 [ast]  <A>/event/ 는 BC 안에서 읽혀야 한다 — 0 참조면 위반(#270: 그건 알림이라
              자리는 application_layer/port/ 다).
  #270 [ast]  driven 어댑터만 읽는 사실은 이벤트가 아니라 «알림» — 자리는 port/.
  #272 [ast]  루트는 이벤트를 기록만 한다 — publish/dispatch 호출 금지.
  #275 [ast]  과거형 사실 하나 = 파일 하나.   #276 [ast] 이벤트는 필드만(메서드 금지).
  #289 [path] 불변식 예외는 exception/ «폴더» — <A>/exception.py 파일이면 위반.
  #290 [path] exception/ 안 «깨진 불변식 하나 = 파일 하나» — 한 파일 여러 예외면 위반.
  #298 [ast]  shared_value_object 는 자기 안 + exception 모듈만 import.
  #299 [path] 애그리거트 꼴 — <X>_repository.py 부재면 위반(<X>.py 부재는 #256).
  #300 [path] <aggregate>/domain_service/ 금지 — BC 레벨 한 칸뿐.
  #301 [ast+] 후보: 루트 인자 «정확히 하나»인 도메인 서비스(루트 메서드가 될 수 있다).
  #302 [ast]  도메인 서비스는 무상태 — __init__ 의 self 상태·모듈 가변 전역 금지.
  #303 [ast]  domain_service import 허용 = 루트·value_object·exception·형제 서비스뿐.
  #304 [ast]  리포지토리를 받지도 부르지도 않는다(불러오거나 저장하면 유스케이스다).
  #305 [ast]  포트를 파라미터로 받지 않는다 — 재료는 유스케이스가 «값으로» 넘긴다.
  #307 [ast]  시그니처는 값 객체 — 전 인자가 원시 타입이면 계산 함수다.
  #308 [ast]  위반의 알림은 도메인 예외 — bool 반환 선언이면 위반.
  #310 [ast]  무상태 규칙 하나 = 파일 하나.
  #311 [ast+] 후보: 파일명이 접미사(_service)를 달거나 애그리거트 어휘 0(행위 이름 물음).
  #315 [path] Factory 는 그 애그리거트 폴더 안.
  #459 [path] shared_value_object 파일 규칙 동일 — 하위 폴더 금지.
  #505 [ast]  <A>/event/ 는 «내부용» — BC 밖 import 금지(밖은 published_event 로 옮겨 담는다).
  #506 [ast]  발행 장치(레지스트리·dispatch·signal)는 domain_layer 에 살지 않는다.
  #542 [ast]  사실은 «애그리거트»가 만든다 — 유스케이스의 도메인 이벤트 생성이면 위반.
  #543 [ast]  꺼내는 창구는 pull_events() 하나 — «안 비우는» events 프로퍼티 병존 금지.
  #546 [ast]  한 트랜잭션 = 애그리거트 하나 — «서로 다른 애그리거트 리포지토리 타입»에
              쓰기 둘이면 위반(세는 대상은 «타입이 <A>_repository.py 에서 온 것»뿐 — C7).
  #547 [ast+] 후보: 한 리포지토리를 여러 <area>/ 가 쓰거나 루트가 비대(엔티티 3+·컬렉션
              필드)한 것 — 「이 둘이 동시에 일어나면 업무가 정말 막아야 하나」(경계를 쪼갠다).
  #548 [ast]  다른 애그리거트는 «식별자 값 객체»로만 — 타입 힌트의 남의 루트 클래스 위반.
  #549 [ast]  수정 조회는 캐시 우회 — select_for_update 와 캐시가 한 함수에 있으면 위반.
  #550 [ast]  배치 면제는 «생성»에만 — 조회로 꺼낸 것들의 save_all 이면 위반.
  #565 [ast+] 후보: 도메인 Enum 값이 유스케이스·서비스 이름과 겹침 — 「업무가 이 단계
              이름을 입으로 부르나」(워크플로 위장 신호).

단순화(정직 기록): #269/#270 의 «읽힘»은 BC 파일 텍스트의 이름 등장으로 잰다. #546 의
타입 해소는 파라미터·__init__ 애너테이션의 `*Repository` 이름과 import 경로 대조다.

이관 계약(명세 조각 ⓐ): 채택 신호 2원(#78) · 대상 0건 가드(#74) · ImportError
fail-closed · ⓓ 후보 exit 불산입.

사용법: check-domain-model.py [TARGET_DIR]   (기본: 현재 디렉터리)
종료코드: 0=clean(또는 표준 미채택) · 1=사용/분석 오류 · 2=blocker(발견 출력)
"""
from __future__ import annotations

import ast
import re
import sys
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
DOMAIN_FIXED = {"shared_value_object", "domain_service"}

KIND_DENY = {"entity", "entities", "value_object", "value_objects", "event", "events",
             "exception", "exceptions", "model", "models", "service", "services",
             "repository", "repositories", "dto", "dtos", "util", "utils", "helper",
             "helpers", "manager", "managers", "handler", "handlers", "validator",
             "validators", "factory", "factories", "aggregate", "aggregates"}
KIND_SOFT = {"data", "objects", "types", "classes", "logic", "rules"}
PRIMITIVES = {"str", "int", "float", "bool", "dict", "list", "Decimal", "bytes", "datetime", "date"}
# python3.9 에는 sys.stdlib_module_names 가 없다 — 기본 목록으로 메운다(#8 오탐 방지).
_STDLIB_FALLBACK = {
    "abc", "ast", "asyncio", "base64", "bisect", "calendar", "collections", "contextlib",
    "copy", "dataclasses", "datetime", "decimal", "enum", "fractions", "functools", "hashlib",
    "heapq", "hmac", "importlib", "inspect", "io", "itertools", "json", "logging", "math",
    "numbers", "operator", "os", "pathlib", "queue", "random", "re", "secrets", "statistics",
    "string", "struct", "sys", "textwrap", "threading", "time", "traceback", "types", "typing",
    "unicodedata", "uuid", "warnings", "weakref", "zoneinfo", "__future__",
}
STDLIB = set(getattr(sys, "stdlib_module_names", ())) | _STDLIB_FALLBACK


class Findings(list):
    def add(self, rule: str, where: str, msg: str) -> None:
        self.append(f"[{rule}] {where}: {msg}")


class Candidates(list):
    def add(self, rule: str, where: str, msg: str, question: str) -> None:
        self.append(f"[ⓓ{rule}] {where}: {msg} — 물음: {question}")


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


def _public_classes(mod: ast.Module) -> list[ast.ClassDef]:
    return [n for n in mod.body if isinstance(n, ast.ClassDef) and not n.name.startswith("_")]


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


# ── 층 구조 — #249 · #252 · #17/#18 · #289 · #290 · #300 · #459 · #315 ─────

def _aggregate_dirs(domain: Path) -> list[Path]:
    return [p for p in sorted(domain.iterdir())
            if p.is_dir() and p.name not in DOMAIN_FIXED and p.name != "__pycache__"]


def _check_layout(root: Path, bc: Path, f: Findings, cand: Candidates) -> None:
    domain = bc / "domain_layer"
    app = bc / "application_layer"
    if domain.is_dir():
        for p in sorted(domain.iterdir()):
            if p.is_file() and p.suffix == ".py" and p.name != "__init__.py":
                f.add("#249", _rel(root, p),
                      "domain_layer 직계 파일 — 자식은 애그리거트 폴더와 shared_value_object/·"
                      "domain_service/ 뿐이다")
        for d in _aggregate_dirs(domain):
            if d.name in ("entity", "value_object"):
                f.add("#252", _rel(root, d),
                      f"1차 폴더 `{d.name}/` — 클래스 종류가 아니라 `<aggregate>/` 가 1차이고 "
                      "entity/·value_object/ 는 그 «안»으로 내린다")
            elif d.name in KIND_DENY:
                f.add("#17", _rel(root, d),
                      f"종류 낱말 1차 폴더 `{d.name}/` — 1차 축은 «도메인 이름»이고 종류는 "
                      "2차다(§0-4 · 트리 명문 형제(shared_value_object·domain_service)만 예외 — #18)")
            elif d.name in KIND_SOFT:
                cand.add("#17", _rel(root, d), f"종류 인접 낱말 `{d.name}/`",
                         "Q1 — 이 이름이 업무의 낱말인가")
            else:
                # #299 · #256 전제 — 애그리거트 꼴.
                if not (d / f"{d.name}_repository.py").is_file():
                    f.add("#299", _rel(root, d),
                          f"`{d.name}_repository.py` 가 없다 — 애그리거트 폴더는 루트와 "
                          "리포지토리 선언 파일을 갖는다(#282)")
                _check_aggregate(root, bc, d, f, cand)
        shared = domain / "shared_value_object"
        if shared.is_dir():
            for p in sorted(shared.iterdir()):
                if p.is_dir() and p.name != "__pycache__":
                    f.add("#459", _rel(root, p),
                          "shared_value_object/ 하위 폴더 — 파일 규칙은 애그리거트 안 값 객체와 "
                          "똑같고 다른 것은 «사는 폴더»뿐이다")
            _check_shared_imports(root, bc, shared, f)
            for py in sorted(shared.glob("*.py")):
                _check_value_object_file(root, py, f, cand)
        ds = domain / "domain_service"
        if ds.is_dir():
            _check_domain_services(root, bc, ds, f, cand)
    if app.is_dir():
        for d in sorted(p for p in app.iterdir() if p.is_dir() and p.name != "__pycache__"):
            if d.name == "port":
                continue
            if d.name in KIND_DENY:
                f.add("#17", _rel(root, d),
                      f"application_layer 1차 `{d.name}/` — 1차 축은 도메인 이름(<area>/)이다")
            elif d.name in KIND_SOFT:
                cand.add("#17", _rel(root, d), f"종류 인접 낱말 `{d.name}/`",
                         "Q1 — 이 이름이 업무의 낱말인가")


# ── 애그리거트 한 폴더 — #256 · #260~#276 · #289 · #290 · #300 · #315 · #543 ──

def _check_aggregate(root: Path, bc: Path, agg: Path, f: Findings, cand: Candidates) -> None:
    root_py = agg / f"{agg.name}.py"
    root_cls_name = _camel(agg.name)
    if not root_py.is_file():
        f.add("#256", _rel(root, agg),
              f"`{agg.name}.py` 가 없다 — 애그리거트 루트 클래스 하나가 폴더와 같은 이름의 "
              "파일로 온다")
    else:
        mod = _parse(root_py)
        classes = _public_classes(mod) if mod else []
        if not any(c.name == root_cls_name for c in classes):
            f.add("#256", _rel(root, root_py), f"루트 클래스 `{root_cls_name}` 이 없다")
        for cls in classes:
            _check_root_class(root, root_py, cls, f, cand)
    if (agg / "exception.py").is_file():
        f.add("#289", _rel(root, agg / "exception.py"),
              "exception 이 파일이다 — 깨진 불변식 하나 = 파일 하나로 exception/ «폴더» 아래 둔다")
    exc_dir = agg / "exception"
    if exc_dir.is_dir():
        for py in sorted(exc_dir.glob("*.py")):
            if py.name == "__init__.py":
                continue
            mod = _parse(py)
            if mod and len(_public_classes(mod)) > 1:
                f.add("#290", _rel(root, py),
                      f"한 파일에 예외 {len(_public_classes(mod))}개 — 깨진 불변식 하나 = 파일 하나다")
    if (agg / "domain_service").is_dir():
        f.add("#300", _rel(root, agg / "domain_service"),
              "<aggregate>/domain_service/ — 도메인 서비스는 BC 레벨 domain_layer/domain_service/ "
              "한 칸에만 산다")
    ent_dir = agg / "entity"
    if ent_dir.is_dir():
        for py in sorted(ent_dir.glob("*.py")):
            if py.name == "__init__.py":
                continue
            if py.stem.endswith("_entity"):
                f.add("#262", _rel(root, py), "`_entity` 접미사 — 폴더가 이미 말한다")
            mod = _parse(py)
            if mod is None:
                continue
            classes = _public_classes(mod)
            if len(classes) > 1:
                f.add("#261", _rel(root, py), f"공개 클래스 {len(classes)}개 — 엔티티 하나 = 파일 하나다")
            for cls in classes:
                if not _has_identifier(cls):
                    f.add("#260", _rel(root, py, cls.lineno),
                          f"`{cls.name}` 에 식별자(id·*_id) 필드가 없다 — entity/ 판정은 "
                          "«식별자를 갖고 값이 바뀌어도 같은 것인가»다(#259)")
    vo_dir = agg / "value_object"
    if vo_dir.is_dir():
        for py in sorted(vo_dir.glob("*.py")):
            if py.name != "__init__.py":
                _check_value_object_file(root, py, f, cand)
    ev_dir = agg / "event"
    if ev_dir.is_dir():
        _check_domain_events(root, bc, agg, ev_dir, f)
    # #263 — 같은 stem 의 ORM 모델은 _model 로 갈린다.
    domain_stems = {p.stem for p in agg.rglob("*.py") if p.stem != "__init__"}
    for models_dir in bc.rglob("models"):
        if not models_dir.is_dir() or set(models_dir.parts) & SKIP_DIRS:
            continue
        for py in models_dir.glob("*.py"):
            if py.stem in domain_stems and not py.stem.endswith("_model"):
                f.add("#263", _rel(root, py),
                      f"도메인 `{py.stem}` 과 같은 이름의 ORM 모듈 — 겹치면 ORM 쪽만 `_model` 을 단다")
    # #315 — Factory 는 애그리거트 폴더 안(도메인 전역 검사는 아래 _check_domain_wide).


def _has_identifier(cls: ast.ClassDef) -> bool:
    for node in ast.walk(cls):
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            if node.target.id == "id" or node.target.id.endswith("_id"):
                return True
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Attribute) and (t.attr == "id" or t.attr.endswith("_id")):
                    return True
        if isinstance(node, ast.arg) and (node.arg == "id" or node.arg.endswith("_id")):
            return True
    return False


def _check_root_class(root: Path, py: Path, cls: ast.ClassDef, f: Findings, cand: Candidates) -> None:
    has_events_attr = False
    has_pull = False
    for node in ast.walk(cls):
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Attribute) and t.attr in ("_events", "events"):
                    has_events_attr = True
        if isinstance(node, ast.AnnAssign):
            t = node.target
            if (isinstance(t, ast.Name) and t.id in ("_events", "events")) or \
                    (isinstance(t, ast.Attribute) and t.attr in ("_events", "events")):
                has_events_attr = True
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                and node.func.attr in ("publish", "dispatch", "send", "emit"):
            recv = node.func.value
            if not (isinstance(recv, ast.Attribute) and recv.attr in ("_events", "events")):
                f.add("#272", _rel(root, py, node.lineno),
                      f"루트가 `{node.func.attr}` 를 부른다 — 이벤트는 «기록만»(리스트 append) 하고 "
                      "아무도 부르지 않는다(메시지 버스를 모르고 I/O 를 하지 않는다)")
    for m in [n for n in cls.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]:
        if m.name == "pull_events":
            has_pull = True
            clears = any(
                (isinstance(n, ast.Assign) and any(
                    isinstance(t, ast.Attribute) and t.attr in ("_events", "events")
                    for t in n.targets))
                or (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                    and n.func.attr == "clear")
                for n in ast.walk(m))
            if not clears:
                f.add("#543", _rel(root, py, m.lineno),
                      "pull_events 가 비우지 않는다 — 꺼내면 비운다(«안 꺼낸 사실»을 save 가 잡는다)")
        if m.name == "events" and any(
                (isinstance(d, ast.Name) and d.id == "property") for d in m.decorator_list):
            f.add("#543", _rel(root, py, m.lineno),
                  "`events` 프로퍼티 — «안 비우고 읽는» 길을 두면 위반이다(창구는 pull_events 하나)")
        # #257 후보 — 상태를 바꾸는 공개 메서드 끝의 불변식 확인.
        if not m.name.startswith("_") and m.name != "pull_events":
            def _self_target(t: ast.AST) -> bool:
                return isinstance(t, ast.Attribute) and isinstance(t.value, ast.Name) \
                    and t.value.id == "self"
            assigns_self = any(
                (isinstance(n, ast.Assign) and any(_self_target(t) for t in n.targets))
                or (isinstance(n, ast.AnnAssign) and _self_target(n.target))
                for n in ast.walk(m))
            if assigns_self and m.body:
                last = m.body[-1]
                ends_with_check = isinstance(last, (ast.Raise, ast.If)) or (
                    isinstance(last, ast.Expr) and isinstance(last.value, ast.Call)
                    and isinstance(last.value.func, ast.Attribute)
                    and ("valid" in last.value.func.attr or "check" in last.value.func.attr
                         or "ensure" in last.value.func.attr or "assert" in last.value.func.attr))
                if not ends_with_check:
                    cand.add("#257", _rel(root, py, m.lineno),
                             f"상태 변경 메서드 `{m.name}` 끝에 불변식 확인이 없다",
                             "Q4 — 이 메서드 뒤에도 불변식이 참인가")
    if has_events_attr and not has_pull:
        f.add("#543", _rel(root, py, cls.lineno),
              "이벤트 기록은 있는데 pull_events() 가 없다 — 꺼내는 창구는 그 하나다")


def _check_value_object_file(root: Path, py: Path, f: Findings, cand: Candidates) -> None:
    mod = _parse(py)
    if mod is None:
        return
    classes = _public_classes(mod)
    if len(classes) > 1:
        f.add("#267", _rel(root, py), f"공개 클래스 {len(classes)}개 — 값 객체 하나 = 파일 하나다")
    for cls in classes:
        has_validation = False
        for m in [n for n in cls.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]:
            in_ctor = m.name in ("__init__", "__post_init__")
            if in_ctor:
                if any(isinstance(n, ast.Raise) for n in ast.walk(m)):
                    has_validation = True
                continue
            for n in ast.walk(m):
                if isinstance(n, ast.Assign):
                    for t in n.targets:
                        if isinstance(t, ast.Attribute) and isinstance(t.value, ast.Name) \
                                and t.value.id == "self":
                            f.add("#264", _rel(root, py, n.lineno),
                                  f"`{m.name}` 에서 self.{t.attr} 대입 — 값 객체는 불변이다"
                                  "(__init__ 밖 자기 속성 대입 금지)")
        # #259 후보 — id 를 가진 값 객체.
        for node in ast.walk(cls):
            if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) \
                    and (node.target.id == "id" or node.target.id.endswith("_id")):
                cand.add("#259", _rel(root, py, node.lineno),
                         f"값 객체 `{cls.name}` 이 식별자 `{node.target.id}` 를 가진다 — "
                         "식별자를 갖고 값이 바뀌어도 같은 것이면 그것은 엔티티다",
                         "Q4 — 이것이 값인가 엔티티인가")
                break
        if not has_validation:
            cand.add("#268", _rel(root, py, cls.lineno),
                     f"`{cls.name}` 의 __init__/__post_init__ 에 raise 가 없다 — 값 객체는 "
                     "만들어지는 시점에 스스로 검증한다",
                     "Q2 — 이 타입 조합만으로 잘못된 값이 «불가능»한가")


def _check_domain_events(root: Path, bc: Path, agg: Path, ev_dir: Path, f: Findings) -> None:
    bc_texts: dict[Path, str] = {}
    for py in _py_files(bc):
        try:
            bc_texts[py] = py.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
    driven_only_dirs = ("driven_layer",)
    for py in sorted(ev_dir.glob("*.py")):
        if py.name == "__init__.py":
            continue
        mod = _parse(py)
        if mod is None:
            continue
        classes = _public_classes(mod)
        if len(classes) > 1:
            f.add("#275", _rel(root, py), f"공개 클래스 {len(classes)}개 — 과거형 사실 하나 = 파일 하나다")
        for cls in classes:
            for m in cls.body:
                if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef)) and not m.name.startswith("__"):
                    f.add("#276", _rel(root, py, m.lineno),
                          f"이벤트에 메서드 `{m.name}` — 필드만 있는 자료구조다")
            readers = [p for p, text in bc_texts.items()
                       if p != py and cls.name in text]
            if not readers:
                f.add("#269", _rel(root, py, cls.lineno),
                      f"`{cls.name}` 을 이 BC 안에서 아무도 읽지 않는다 — 읽는 사람이 없으면 "
                      "이벤트가 아니라 «알림»이고 자리는 application_layer/port/ 다(#270)")
            elif all(set(p.relative_to(bc).parts) & set(driven_only_dirs) for p in readers):
                f.add("#270", _rel(root, py, cls.lineno),
                      f"`{cls.name}` 을 driven 어댑터만 읽는다 — 그것은 «알림»이라 자리는 "
                      "application_layer/port/ 다")


def _check_shared_imports(root: Path, bc: Path, shared: Path, f: Findings) -> None:
    for py in sorted(shared.glob("*.py")):
        mod = _parse(py)
        for node in ast.walk(mod) if mod else []:
            if not isinstance(node, ast.ImportFrom):
                continue
            m = node.module or ""
            if not m or m.split(".")[0] in STDLIB:
                continue
            ok = "shared_value_object" in m or m.split(".")[-1] == "exception" \
                 or ".exception." in m or m.endswith(".exception")
            if not ok:
                f.add("#298", _rel(root, py, node.lineno),
                      f"shared_value_object 가 `{m}` 를 import 한다 — 같은 폴더 안과 exception "
                      "모듈 말고는 아무것도 import 하지 않는다")


# ── domain_service — #301~#311 ─────────────────────────────────────────────

def _check_domain_services(root: Path, bc: Path, ds: Path, f: Findings, cand: Candidates) -> None:
    domain = bc / "domain_layer"
    agg_names = {d.name for d in _aggregate_dirs(domain)}
    root_classes = {_camel(n) for n in agg_names}
    for py in sorted(ds.glob("*.py")):
        if py.name == "__init__.py":
            continue
        mod = _parse(py)
        if mod is None:
            continue
        stem_toks = set(py.stem.split("_"))
        if py.stem.endswith(("_service", "_domain_service")):
            cand.add("#311", _rel(root, py), "접미사를 단 도메인 서비스 파일명 — 접미사 없이 "
                     "«행위»로 짓는다(`lesson_slot_policy`·`settle_turn`)",
                     "이 이름이 규칙 «행위»를 말하나")
        elif not any(set(a.split("_")) & stem_toks for a in agg_names):
            cand.add("#311", _rel(root, py), "파일명에 주어가 되는 애그리거트 어휘가 없다",
                     "이 이름이 규칙 «행위»를 말하나")
        pubs = [n for n in mod.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
                and not n.name.startswith("_")]
        if len(pubs) > 1:
            f.add("#310", _rel(root, py), f"공개 정의 {len(pubs)}개 — 무상태 규칙 하나 = 파일 하나다")
        for node in ast.walk(mod):
            if isinstance(node, ast.ImportFrom):
                m = node.module or ""
                if not m or m.split(".")[0] in STDLIB:
                    continue
                bad = ".entity." in m or m.endswith("_repository") or ".port." in m \
                    or m.split(".")[0] in ("django", "framework")
                if bad:
                    f.add("#303", _rel(root, py, node.lineno),
                          f"`{m}` import — domain_service 는 루트·value_object·exception·형제 "
                          "서비스만 import 한다")
        for fn in [n for n in ast.walk(mod) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]:
            if fn.name.startswith("_"):
                continue
            arg_anns = [(_ann_names(a.annotation), a.arg) for a in fn.args.args
                        if a.arg not in ("self", "cls")]
            for names, arg in arg_anns:
                if any(n.endswith("Repository") for n in names):
                    f.add("#304", _rel(root, py, fn.lineno),
                          f"`{arg}` 가 리포지토리다 — 불러오거나 저장하면 그건 유스케이스다"
                          "(Vernon 의 실례도 이 트리에선 유스케이스로 간다 — 3차 T24)")
                elif any(n.endswith("Port") for n in names):
                    f.add("#305", _rel(root, py, fn.lineno),
                          f"`{arg}` 가 포트다 — 재료는 유스케이스가 모아 «값으로» 넘긴다")
            root_args = [arg for names, arg in arg_anns if names & root_classes]
            if len(root_args) == 1 and len(arg_anns) >= 1:
                cand.add("#301", _rel(root, py, fn.lineno),
                         f"루트 인자가 정확히 하나(`{root_args[0]}`) — 루트 메서드가 될 수 있으면 "
                         "애그리거트로 간다(못 하는 이유는 «안 받거나·없음 판정·둘 이상»뿐)",
                         "이 규칙이 루트 메서드로 표현될 수 있나")
            flat = [n for names, _ in arg_anns for n in names]
            if arg_anns and all(set(names) <= PRIMITIVES for names, _ in arg_anns) and flat:
                f.add("#307", _rel(root, py, fn.lineno),
                      f"`{fn.name}` 의 인자가 전부 원시 타입 — 그건 도메인 서비스가 아니라 계산 "
                      "함수다(amount: Money 처럼 값 객체가 온다)")
            if fn.returns is not None and _ann_names(fn.returns) == {"bool"}:
                f.add("#308", _rel(root, py, fn.lineno),
                      f"`{fn.name}` 이 bool 을 돌려준다 — 규칙 위반의 알림은 «도메인 예외»다")
        for cls in [n for n in mod.body if isinstance(n, ast.ClassDef)]:
            for m in [n for n in cls.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]:
                if m.name == "__init__":
                    for n in ast.walk(m):
                        if isinstance(n, ast.Assign) and any(
                                isinstance(t, ast.Attribute) and isinstance(t.value, ast.Name)
                                and t.value.id == "self" for t in n.targets):
                            f.add("#302", _rel(root, py, n.lineno),
                                  "__init__ 이 self 상태를 만든다 — 도메인 서비스는 무상태다")
        for node in mod.body:
            if isinstance(node, ast.Assign) and isinstance(node.value, (ast.Dict, ast.List)):
                f.add("#302", _rel(root, py, node.lineno),
                      "모듈 레벨 가변 전역 — 도메인 서비스는 무상태다")


# ── 도메인 전역 — #8 · #253 · #258 · #265/#266 · #505 · #506 · #548 · #315 ──

def _check_domain_wide(root: Path, bc: Path, all_bcs: list[Path], f: Findings) -> None:
    domain = bc / "domain_layer"
    if not domain.is_dir():
        return
    agg_names = {d.name for d in _aggregate_dirs(domain)}
    own = bc.name
    for py in _py_files(domain):
        mod = _parse(py)
        if mod is None:
            continue
        my_agg = None
        parts = py.relative_to(domain).parts
        if parts and parts[0] in agg_names:
            my_agg = parts[0]
        for node in ast.walk(mod):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                mods = [a.name for a in node.names] if isinstance(node, ast.Import) \
                    else [node.module or ""]
                for m in mods:
                    top = m.split(".")[0]
                    if not m or node.__class__ is ast.ImportFrom and node.level:  # 상대 import 는 자기 안
                        continue
                    if top == "application":
                        segs = m.split(".")
                        if len(segs) >= 3 and (segs[1] != own or segs[2] != "domain_layer"):
                            f.add("#8", _rel(root, py, node.lineno),
                                  f"`{m}` — domain_layer 의 밖으로 나가는 import 는 0 이다"
                                  "(django 도 다른 층도 다른 BC 도 모른다)")
                        elif len(segs) >= 5 and segs[2] == "domain_layer" and my_agg \
                                and segs[3] in agg_names and segs[3] != my_agg:
                            other, tail = segs[3], segs[4]
                            if tail == "entity" or (len(segs) >= 5 and ".entity." in m + "."):
                                f.add("#258", _rel(root, py, node.lineno),
                                      f"타 애그리거트 `{other}` 의 entity 직접 참조 — 붙잡을 수 "
                                      "있는 것은 루트뿐이고 언제나 루트를 거쳐 닿는다")
                            elif tail == "value_object":
                                f.add("#266", _rel(root, py, node.lineno),
                                      f"타 애그리거트 `{other}` 의 값 객체 사용 — <A>/value_object/ 는 "
                                      "그 애그리거트 밖에서 안 쓰인다(#265)라, 쓰기 시작하는 순간 "
                                      "shared_value_object/ 로 올린다")
                            elif tail != other:
                                f.add("#253", _rel(root, py, node.lineno),
                                      f"`{other}` 의 `{tail}` 모듈 import — 타 애그리거트는 "
                                      "«루트 모듈»만 import 한다")
                    elif top not in STDLIB:
                        f.add("#8", _rel(root, py, node.lineno),
                              f"`{m}` — domain_layer 의 밖으로 나가는 import 는 0 이다")
            if isinstance(node, ast.ClassDef):
                if any(w in node.name for w in ("Registry", "Dispatcher", "Bus", "Signal")):
                    f.add("#506", _rel(root, py, node.lineno),
                          f"발행 장치 `{node.name}` — 배달은 framework/broker/ 몫이라 "
                          "domain_layer 에 살지 않는다")
                if "Factory" in node.name and my_agg is None:
                    f.add("#315", _rel(root, py, node.lineno),
                          f"`{node.name}` 이 애그리거트 폴더 밖에 있다 — 복잡한 조립(Factory)은 "
                          "그 애그리거트 폴더 «안»에 둔다")
        # #548 — 남의 루트 클래스 타입 힌트.
        if my_agg:
            other_roots = {_camel(a) for a in agg_names if a != my_agg}
            for node in ast.walk(mod):
                ann = None
                if isinstance(node, ast.AnnAssign):
                    ann = node.annotation
                elif isinstance(node, ast.arg):
                    ann = node.annotation
                if ann is not None:
                    hit = _ann_names(ann) & other_roots
                    if hit:
                        f.add("#548", _rel(root, py, node.lineno),
                              f"타 애그리거트 루트 `{sorted(hit)[0]}` 타입 힌트 — 다른 애그리거트는 "
                              "«식별자 값 객체»로만 문다(면제는 조회 성능 하나 — 원전 Reason Four)")
    # #505 — 다른 BC 에서의 도메인 이벤트 사용. (#265 는 #266 과 같은 술어라 #266 이 문다.)
    for other_bc in all_bcs:
        if other_bc == bc:
            continue
        for py in _py_files(other_bc):
            mod = _parse(py)
            for node in ast.walk(mod) if mod else []:
                if isinstance(node, ast.ImportFrom):
                    m = node.module or ""
                    if f"application.{own}.domain_layer." in m and ".event" in m:
                        f.add("#505", _rel(root, py, node.lineno),
                              f"타 BC 가 `{own}` 의 도메인 이벤트를 import 한다 — <A>/event/ 는 "
                              "«내부용»이고 밖으로 알릴 것은 published_event/ 로 «옮겨 담는다»")


# ── 응용 쪽 — #257 확정 · #542 · #546 · #547 · #549 · #550 · #565 ───────────

def _repo_bindings(cls_or_fn: ast.AST) -> dict[str, str]:
    """이름 → 애그리거트(snake) — `*Repository` 애너테이션 파라미터·self 속성."""
    out: dict[str, str] = {}
    for node in ast.walk(cls_or_fn):
        if isinstance(node, ast.arg) and node.annotation is not None:
            for n in _ann_names(node.annotation):
                if n.endswith("Repository"):
                    stem = n[: -len("Repository")]
                    out[node.arg] = re.sub(r"(?<!^)(?=[A-Z])", "_", stem).lower()
    return out


def _check_application_side(root: Path, bc: Path, f: Findings, cand: Candidates) -> None:
    app = bc / "application_layer"
    domain = bc / "domain_layer"
    if not app.is_dir():
        return
    event_classes: set[str] = set()
    if domain.is_dir():
        for py in domain.glob("*/event/*.py"):
            mod = _parse(py)
            event_classes |= {c.name for c in _public_classes(mod)} if mod else set()
    repo_area_use: dict[str, set[str]] = {}
    for py in _py_files(app):
        mod = _parse(py)
        if mod is None:
            continue
        rel_parts = py.relative_to(app).parts
        area = rel_parts[0] if rel_parts else ""
        # #542 — 유스케이스의 도메인 이벤트 생성.
        imported_events: set[str] = set()
        for node in ast.walk(mod):
            if isinstance(node, ast.ImportFrom):
                m = node.module or ""
                if ".domain_layer." in m and (".event." in m or m.endswith(".event")):
                    imported_events |= {a.asname or a.name for a in node.names}
                if m.endswith("_repository"):
                    agg = m.rsplit(".", 1)[-1][: -len("_repository")]
                    repo_area_use.setdefault(agg, set()).add(area)
        for node in ast.walk(mod):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
                    and node.func.id in (imported_events & (event_classes or imported_events)):
                f.add("#542", _rel(root, py, node.lineno),
                      f"유스케이스가 도메인 이벤트 `{node.func.id}` 를 지어낸다 — 사실은 "
                      "«애그리거트»가 상태를 바꾼 그 메서드 안에서 기록한다")
        if not py.name.endswith("_use_case.py"):
            continue
        for fn in [n for n in ast.walk(mod) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]:
            bindings = _repo_bindings(fn)
            cls_parent = next((c for c in ast.walk(mod) if isinstance(c, ast.ClassDef)
                               and fn in ast.walk(c)), None)
            if cls_parent is not None:
                init = next((m for m in cls_parent.body
                             if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))
                             and m.name == "__init__"), None)
                if init is not None:
                    param_map = _repo_bindings(init)
                    for st in ast.walk(init):
                        target = None
                        if isinstance(st, ast.Assign) and len(st.targets) == 1:
                            target, value = st.targets[0], st.value
                        elif isinstance(st, ast.AnnAssign) and st.value is not None:
                            target, value = st.target, st.value
                        else:
                            continue
                        if isinstance(target, ast.Attribute) and isinstance(value, ast.Name) \
                                and value.id in param_map:
                            bindings[target.attr] = param_map[value.id]
            written: set[str] = set()
            loaded_from_read: set[str] = set()
            for n in ast.walk(fn):
                if isinstance(n, ast.Assign) and isinstance(n.value, ast.Call) \
                        and isinstance(n.value.func, ast.Attribute):
                    head = n.value.func.attr.split("_", 1)[0]
                    if head in ("get", "find", "list", "search") and len(n.targets) == 1 \
                            and isinstance(n.targets[0], ast.Name):
                        loaded_from_read.add(n.targets[0].id)
                if not isinstance(n, ast.Call) or not isinstance(n.func, ast.Attribute):
                    continue
                recv, meth = n.func.value, n.func.attr
                names = set()
                if isinstance(recv, ast.Name):
                    names.add(recv.id)
                elif isinstance(recv, ast.Attribute) and isinstance(recv.value, ast.Name) \
                        and recv.value.id == "self":
                    names.add(recv.attr)
                agg = next((bindings[x] for x in names if x in bindings), None)
                head = meth.split("_", 1)[0]
                if agg and head in ("save", "remove"):
                    written.add(agg)
                    if meth == "save_all" and n.args and isinstance(n.args[0], ast.Name) \
                            and n.args[0].id in loaded_from_read:
                        f.add("#550", _rel(root, py, n.lineno),
                              "조회로 꺼낸 것들을 save_all — 배치 면제는 «생성»에만 걸린다"
                              "(이미 있는 것 여럿 고치기는 면제가 아니다)")
                # #257 확정 — 리포지토리에서 나온 객체의 «속성 접근 후 메서드 호출».
                if isinstance(recv, ast.Attribute) and isinstance(recv.value, ast.Name) \
                        and recv.value.id in loaded_from_read:
                    f.add("#257", _rel(root, py, n.lineno),
                          f"`{recv.value.id}.{recv.attr}.{meth}(...)` — 애그리거트 상태 변경은 "
                          "전부 «루트를 지나야» 한다(내부에 손을 넣지 않는다)")
            if len(written) >= 2:
                f.add("#546", _rel(root, py, fn.lineno),
                      f"서로 다른 애그리거트 리포지토리 {sorted(written)} 에 쓰기 둘 — 한 트랜잭션은 "
                      "애그리거트 «하나»를 바꾼다(D50 · 세는 대상은 타입이 <A>_repository.py 에서 온 것뿐)")
    for agg, areas in sorted(repo_area_use.items()):
        if len(areas) >= 2:
            cand.add("#547", _rel(root, bc),
                     f"`{agg}_repository` 를 여러 <area>/ {sorted(areas)} 가 쓴다 — 경계가 "
                     "너무 묶였을 신호다(트랜잭션을 늘리지 말고 «경계를 쪼갠다»)",
                     "서로 다른 일을 하는 두 사용자가 이 경계로 충돌하나")
    # #547 후보 ⑶ — 비대한 루트.
    if domain.is_dir():
        for agg in _aggregate_dirs(domain):
            ents = [p for p in (agg / "entity").glob("*.py") if p.stem != "__init__"] \
                if (agg / "entity").is_dir() else []
            root_py = agg / f"{agg.name}.py"
            if len(ents) >= 3 and root_py.is_file():
                mod = _parse(root_py)
                has_coll = any(
                    isinstance(n, ast.AnnAssign) and _ann_names(n.annotation) & {"list", "List", "Sequence"}
                    for n in ast.walk(mod)) if mod else False
                if has_coll:
                    cand.add("#547", _rel(root, root_py),
                             f"엔티티 {len(ents)}개 + 무제한 컬렉션 필드 — 루트가 비대하다",
                             "이 둘이 «동시에» 일어나면 업무가 정말 막아야 하나")
    # #565 후보 — 도메인 Enum 값 ∩ 유스케이스·서비스 이름.
    uc_names: set[str] = set()
    for area in app.iterdir() if app.is_dir() else []:
        if area.is_dir() and area.name not in ("port", "__pycache__"):
            uc_names |= {d.name for d in area.iterdir() if d.is_dir()}
    if domain.is_dir() and uc_names:
        for py in _py_files(domain):
            mod = _parse(py)
            for cls in [n for n in ast.walk(mod) if isinstance(n, ast.ClassDef)] if mod else []:
                bases = {b.id if isinstance(b, ast.Name) else getattr(b, "attr", "") for b in cls.bases}
                if not bases & {"Enum", "StrEnum", "IntEnum", "TextChoices", "Choices"}:
                    continue
                for st in cls.body:
                    if isinstance(st, ast.Assign) and isinstance(st.value, ast.Constant) \
                            and isinstance(st.value.value, str) and st.value.value in uc_names:
                        cand.add("#565", _rel(root, py, st.lineno),
                                 f"도메인 Enum 값 `{st.value.value}` 이 유스케이스 이름과 겹친다 — "
                                 "워크플로를 도메인 어휘로 위장한 것이면 자리는 유스케이스다",
                                 "업무가 이 단계 이름을 «입으로 부르나»")


# ── #549 — 수정 조회의 캐시 우회 ────────────────────────────────────────────

def _check_cache_bypass(root: Path, bc: Path, f: Findings) -> None:
    for layer in ("driven_layer",):
        base = bc / layer
        if not base.is_dir():
            continue
        for py in _py_files(base):
            mod = _parse(py)
            if mod is None:
                continue
            for fn in [n for n in ast.walk(mod) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]:
                has_lock = any(isinstance(n, ast.Attribute) and n.attr == "select_for_update"
                               for n in ast.walk(fn))
                has_cache = any(
                    (isinstance(n, ast.Name) and n.id in ("cache", "caches"))
                    or (isinstance(n, ast.Attribute) and "cache" in n.attr)
                    for n in ast.walk(fn))
                deco_cached = any("cache" in ast.dump(d) for d in fn.decorator_list)
                if has_lock and (has_cache or deco_cached):
                    f.add("#549", _rel(root, py, fn.lineno),
                          "select_for_update 와 캐시가 한 함수에 있다 — 수정하려고 꺼내는 조회는 "
                          "캐시를 «우회»한다(선은 애그리거트가 아니라 트랜잭션이다 · "
                          "select_for_update 를 캐시하면 DB 락이 무용지물)")


# ── main ────────────────────────────────────────────────────────────────────

def main(argv: list[str]) -> int:
    if len(argv) > 1:
        print(f"사용법: {Path(sys.argv[0]).name} [TARGET_DIR]", file=sys.stderr)
        return 1
    root = Path(argv[0]).resolve() if argv else Path.cwd()
    if not root.is_dir():
        print(f"사용 오류: 디렉터리가 아니다 — {root}", file=sys.stderr)
        return 1

    findings = Findings()
    cand = Candidates()
    bcs = [bc for bc in vocab.bc_dirs(root) if _has_adoption_signal(bc)]

    # 대상 0건 가드(#74) — touched 필터 없음이라 자리는 대상 집합 직후다(#75).
    if bcs and not any((bc / "domain_layer").is_dir() or (bc / "application_layer").is_dir()
                       for bc in bcs):
        print("blocker: 채택 신호는 있는데 domain_layer/application_layer 가 0건이다 — 조용한 무동작을 금지한다(#74)")
        return 2

    for bc in bcs:
        _check_layout(root, bc, findings, cand)
        _check_domain_wide(root, bc, bcs, findings)
        _check_application_side(root, bc, findings, cand)
        _check_cache_bypass(root, bc, findings)

    for c in cand:
        print(c)
    if findings:
        print("blocker — 도메인 모델 위반 (루트를 지나고·값은 불변이고·한 트랜잭션 = 애그리거트 하나 — D12·D13·D50)")
        for x in findings:
            print(f"  {x}")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
