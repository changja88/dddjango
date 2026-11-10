#!/usr/bin/env python3
"""dddjango 도메인 모델 검사기 — 애그리거트·엔티티·값 객체·도메인 서비스·도메인 이벤트(D12·D13·D50).

담당 규칙 (rule-owner-map · 총 51):
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
              응용 쪽 #257 확정 · #546 · #550 은 유스케이스 본체와 그 칸 승격 폴더(트리 42행)의
              부품 파일을 함께 본다(파일 집합 = `checker_target.joint_use_case` — 표준 밖 자리
              유스케이스 포함 · G2 함께 커밋 대조와 한 출처).
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
  #268 [ast+] 후보: 일반 VO 생성자 raise 부재 또는 custom/open Enum의 생성 검증 미확정.
              출처가 확인된 닫힌 표준 Enum/StrEnum/IntEnum만 제외(Q2 — 잘못된 값이 불가능한가).
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
  #311 [ast+] 후보: 파일명이 접미사(_service)를 달거나 애그리거트 어휘 0(규칙 복수형 포함 · 행위 이름 물음).
  #315 [path] Factory 는 그 애그리거트 폴더 안.
  #459 [path] shared_value_object 파일 규칙 동일 — 하위 폴더는 묶음만 된다(그 판정은 #654~#656).
  #505 [ast]  <A>/event/ 는 «내부용» — BC 밖 import 금지(밖은 published_event 로 옮겨 담는다).
  #506 [ast]  발행 장치(레지스트리·dispatch·signal)는 domain_layer 에 살지 않는다.
  #542 [ast]  사실은 «애그리거트»가 만든다 — 유스케이스의 도메인 이벤트 생성이면 위반.
  #543 [ast]  꺼내는 창구는 pull_events() 하나 — «안 비우는» events 프로퍼티 병존 금지.
  #546 [ast+] 해소된 동일 트랜잭션 영역에 서로 다른 repository/aggregate 타입 쓰기는 확정.
              순차 UoW 분리·nested/외부 atomic 결합; 영역·출처 미해소는 후보. 예외 둘 — 새로 여럿
              만드는 save_all(#550 · #599) · 함께 커밋: 트랜잭션을 여는 바깥 `with <uow>:` 바로 윗줄 표지
              `# joint-commit: 함께 …  잠금 …  불변식 …`(G1 승인 행 끝 칸 글 그대로)가 덮는 구간의 쓰기는
              셈에서 뺀다(#550 행 3 도 서지 않는다). 표지 진단도 #546 줄이다 — 표지 · 칸 꼴 · 떠 있는 표지 ·
              트랜잭션으로 읽는 바깥 `with` 가 아님 · 구간 안 꼴(조회한 여럿 · 잠금 정렬 고리 밖 쓰기 고리(새로 만든
              것만 쓰는 글자 고리는 빼고) · 컴프리헨션 · 람다 안 쓰기 · CAS(저장소 선언 `-> bool` · 글자 `"bool"`
              포함) 결과를 `if not …: raise` 로 받지 않음 · 쓰기 실패를 `try` · `suppress` 로 삼키거나 받는 몸 ·
              미스 몸이 continue · break · return 으로 빠져나감) · 덮을 함께 쓰기 없음 · 이미 있는 것 둘 미만 ·
              넓이(`함께` · `잠금` · 이미 있는 것 + 새 것(묶음 인자 `save_all((a, b))` · 새 것만 도는 글자 고리의
              원소 포함)이 `×n` 보다 많음) · 잠금 차례(같은 타입 = 키 정렬 고리 또는 `a, b = sorted(…)` 차례
              잠금 · 다른 타입 = `잠금` 칸 차례) · 한 유스케이스에 같은 불변식 표지 둘. 표지가 G1 승인을 받았는지는
              묻지 않는다(G2 `design_pregate.py --joint-verify` 몫).
  #547 [ast+] 후보: 한 리포지토리를 여러 <area>/ 가 쓰거나 루트가 비대(엔티티 3+·컬렉션
              필드)한 것 — 「이 둘이 동시에 일어나면 업무가 정말 막아야 하나」(경계를 쪼갠다).
  #548 [ast]  다른 애그리거트는 «식별자 값 객체»로만 — 타입 힌트의 남의 루트 클래스 위반.
  #549 [ast]  수정 조회는 캐시 우회 — select_for_update 와 캐시가 한 함수에 있으면 위반.
  #550 [ast]  배치 면제는 «생성»에만 — 이미 있는 애그리거트 여럿을 한 트랜잭션에서 바꾸면 위반.
              ① 조회로 꺼낸 «여럿»을 save_*·remove_* 하나에 넘김(구간 무관) — «여럿» = 첫 주석이
              컬렉션인 조회 이름 · 그 tuple(..)·list(..) · 원소식이 반복 변수 그 자체인 컴프리헨션
              (주석 없는 대입은 save_all 만). ② 명시 구간 안 for 몸이 조회한 여럿(조회 이름 · 묶인 저장소의
              조회 호출)의 원소나 반복 변수로 조회한 이름을 씀(쓰기가 든 문장 목록이 다른 이름의 쓰기·
              continue·중첩 고리 없이 이 고리를 나가는 break·return·raise 로 끝나면 한 건이라 뺌 · 쓰기나
              그 결과 이름이 검사식인 마지막 if 는 참 갈래를 본다 — CAS). ③ 명시 구간 안에서 따로 조회한
              같은 타입 이름 둘을 같은 실행 길에서 씀(배타 갈래 · `if not <쓰기>:` 미스 몸 · return/raise 뒤 · CAS
              (저장소 선언 `-> bool`)이면 결과를 이름에 담고 바로 다음 `if not <이름>:` 의 몸과, 쓰기 구간 안 고리
              밖 `if <CAS>:` 몸이 return/raise 로 끝난 뒤(구간 안에서 감싼 try 의 finally 밖 · 구간 바깥 다시 하기
              고리는 시도마다 새 트랜잭션이라 보지 않는다) · 같은 조회 인자(자리 차례 값 — 키워드는 저장소
              선언의 매개변수 자리)는 뺌 · 글자 고리 원소 포함) — 함께 커밋 표지 구간은 표지 칸이 승인이다(#546 표지 판정).
  #565 [ast+] 후보: 도메인 Enum 값이 유스케이스·서비스 이름과 겹침 — 「업무가 이 단계
              이름을 입으로 부르나」(워크플로 위장 신호).
  #656 [ast]  묶음 자리 = `folder_group.place(지금 트리)` — 만들 묶음(부모 `__init__.py`) ·
              풀 묶음(그 `__init__.py`) · 묶음에 둘 파일 · 부모에 둘 파일(D60 · 줄 꼴 설계 7.3).

의미 묶음(D60): 묶음 허용 칸(entity·value_object·event·exception·shared_value_object·
domain_service)의 파일은 `folder_group.group_members` 로 읽는다 — 묶음 안 파일도 같은 규칙을
진다(서비스 칸은 묶음 안 승격 본체까지). #298 의 상대 import 는 그 파일의 패키지 기준으로 푼다.

단순화(정직 기록): #269/#270 의 «읽힘»은 BC 파일 텍스트의 이름 등장으로 잰다. #546 의
타입 해소는 파라미터·__init__ 애너테이션의 `*Repository` 이름과 import 경로 대조다.
트랜잭션 영역은 표준 UoW 주입·factory·별칭과 Django atomic의 AST 범위로 한정한다.
같은 repository 타입의 여러 인스턴스는 #546 이 아니라 #550 ②③ 이 조회 이름과 조회 인자로 가른다 —
도움 메서드·다른 함수를 거친 쓰기와 속성에 담은 조회값은 보지 않는다. 미해소 영역은 통과 증명이 아니다.
#550 ③ 의 배타는 글자로 본다 — `raise` 를 함수 안 `try` 가 잡는 꼴 · `return` 으로 끝나는 목록 앞쪽의 쓰기(그
앞에서 `continue` · `break` 로 나갈 수 있다) · try 몸의 쓰기 뒤 except 의 쓰기도 배타로 봐 놓치고, 이름에 담은
묶음(`pair = (a, b)` · `for o in pair`)은 보지 않는다. 조회 인자 자리는 같은 파일 저장소 선언으로만 푼다(선언을
못 읽은 키워드는 «이름=값» 으로 따로 센다 — 같은 애그리거트를 위치 · 키워드로 섞어 다시 읽으면 붉을 수 있다). 함께
커밋 표지 판정의 «이미 있는 것» 은 그 타입 저장소 조회(get · find · list · search 머리)로 꺼낸 이름과 구간 안
`*_for_update` 조회 수로 센다 — 덜 세는 쪽이라 `×n` 이 코드보다 큰 칸은 받는다. «새 것» 은 저장소 밖 호출로 만든
이름 · 그 자리 생성 호출 · 그런 것만 담은 묶음이고, 반복 변수는 그 고리의 글자 원소로만 가린다(같은 이름의 다른 대입은
보지 않는다). 잠금 차례는 글자 차례다(갈래마다 다른 차례 · 도움 메서드 안 잠금 · 같은 BC 함께 커밋끼리 차례는 리뷰어 몫).

이관 계약(명세 조각 ⓐ): 채택 신호 2원(#78) · 대상 0건 가드(#74) · ImportError
fail-closed · ⓓ 후보 exit 불산입.

사용법: check-domain-model.py [TARGET_DIR]   (기본: 현재 디렉터리)
종료코드: 0=clean(또는 표준 미채택) · 1=사용/분석 오류 · 2=blocker(발견 출력)
구조화 레코드: DJR_FINDINGS_JSON=<경로> 지정 시 findings.py(공용 모듈)가 JSON lines 를
추가 방출한다 — 라인 출력·exit 의미론 무변(T0 B2).

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
import folder_group
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


def _word_forms(word: str) -> set[str]:
    """#311 — 애그리거트 낱말과 그 규칙 복수형(-s · 치찰음 뒤 -es · 자음+y → -ies). 불규칙형(people 류)은 받지 않는다.

    복수형은 세 글자 이상 낱말에만 만든다 — 두 글자 이하(`a` · `it`)의 +s 는 기능어(`as` · `its`)가 된다
    (`business_vocab.tokens` 의 세 글자 바닥과 같은 기준)."""
    forms: set[str] = {word}
    if len(word) >= 3:
        forms.add(word + "s")
        if word.endswith(("s", "x", "z", "ch", "sh")):
            forms.add(word + "es")
        if word.endswith("y") and word[-2] not in "aeiou":
            forms.add(word[:-1] + "ies")
    return forms


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


# ── 층 구조 — #249 · #252 · #17/#18 · #289 · #290 · #300 · #315 · #656 ──────

def _aggregate_dirs(domain: Path) -> list[Path]:
    return [p for p in sorted(domain.iterdir())
            if p.is_dir() and p.name not in DOMAIN_FIXED and p.name != "__pycache__"
            and not checker_target.cache_only_instance(p)]


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
        _check_group_places(root, bc, f)
        shared = domain / "shared_value_object"
        if shared.is_dir():
            _check_shared_imports(root, bc, shared, f)
            for py in folder_group.group_members(shared, "*.py", promotable=False):
                _check_value_object_file(root, py, f, cand)
        ds = domain / "domain_service"
        if ds.is_dir():
            _check_domain_services(root, bc, ds, f, cand)
    if app.is_dir():
        for d in sorted(p for p in app.iterdir() if p.is_dir() and p.name != "__pycache__"):
            if d.name == "port" or checker_target.cache_only_instance(d):
                continue
            if d.name in KIND_DENY:
                f.add("#17", _rel(root, d),
                      f"application_layer 1차 `{d.name}/` — 1차 축은 도메인 이름(<area>/)이다")
            elif d.name in KIND_SOFT:
                cand.add("#17", _rel(root, d), f"종류 인접 낱말 `{d.name}/`",
                         "Q1 — 이 이름이 업무의 낱말인가")


def _check_group_places(root: Path, bc: Path, f: Findings) -> None:
    """#656 — 묶음 자리는 `folder_group.place` 가 정한다. 다르면 그 줄 꼴(설계 7.3)로 한 줄씩."""
    files, dirs = folder_group.scan_tree(root, [bc.name])
    for where, msg in folder_group.lines(folder_group.place(files, dirs)):
        f.add("#656", where, msg)


# ── 애그리거트 한 폴더 — #256 · #260~#276 · #289 · #290 · #300 · #315 · #543 ──

def _check_aggregate(root: Path, bc: Path, agg: Path, f: Findings, cand: Candidates) -> None:
    root_py = checker_target.slot_file(agg / f"{agg.name}.py")  # 동명 폴더 승격(#490 교체형)이면 본체
    root_cls_name = _camel(agg.name)
    if root_py is None:
        f.add("#256", _rel(root, agg),
              f"`{agg.name}.py` 가 없다 — 애그리거트 루트 클래스 하나가 폴더와 같은 이름의 "
              "파일로 온다")
    elif checker_target.skeleton_placeholder(root_py):
        pass  # 빈 골격(주석·docstring뿐) — 루트 클래스 의무 제외 (판정 ④ 2026-08-25)
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
        for py in folder_group.group_members(exc_dir, "*.py", promotable=False):
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
        for py in folder_group.group_members(ent_dir, "*.py", promotable=False):
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
        for py in folder_group.group_members(vo_dir, "*.py", promotable=False):
            if py.name != "__init__.py":
                _check_value_object_file(root, py, f, cand)
    ev_dir = agg / "event"
    if ev_dir.is_dir():
        _check_domain_events(root, bc, agg, ev_dir, f)
    # #263 — 같은 stem 의 ORM 모델은 _model 로 갈린다.
    # 승격 부품 stem 포섭은 의도다(이름 충돌 회피 우선 — 2026-09-01).
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


def _journal_pending_stores(cls: ast.ClassDef) -> "set[str]":
    """저널 애그리거트 관용구(#543 부칙 2026-08-25)의 pending 저장소 이름 집합.

    이벤트가 곧 도메인 실체인 저널 애그리거트(실체 `events` 저장소와 발행 대기 큐가 분리된
    이중 구조)는 `pull_events()` 대신 «pending 조회 property + 실소거 창구»가 인정 형태다.
    전건(전부 충족한 저장소만 인정 — fail-closed):
      ① 사적(밑줄) 필드이고 실체 저장소 이름(`_events`/`events`)이 아니다(이중 구조 — 같은
         이름이면 일반 관용구라 창구는 pull_events 하나다)
      ② 어떤 메서드/property 가 그 저장소의 tuple 사본을 반환한다(`return tuple(self.<store>)`)
      ③ 어떤 메서드 body 가 같은 저장소를 실제로 비운다(`.clear()` 또는 빈 재대입 — 이름
         불문·행위 판별. no-op mark 디코이는 여기서 탈락한다)
    """
    private_fields: set[str] = set()
    for node in ast.walk(cls):
        if isinstance(node, ast.AnnAssign):
            if isinstance(node.target, ast.Name):
                private_fields.add(node.target.id)
            elif isinstance(node.target, ast.Attribute) \
                    and isinstance(node.target.value, ast.Name) \
                    and node.target.value.id == "self":
                private_fields.add(node.target.attr)
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Attribute) and isinstance(t.value, ast.Name) \
                        and t.value.id == "self":
                    private_fields.add(t.attr)
    private_fields = {
        n for n in private_fields
        if n.startswith("_") and n not in ("_events",)
    }
    queried: set[str] = set()
    cleared: set[str] = set()

    def _self_attr(node: ast.AST) -> str:
        return node.attr if (
            isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name)
            and node.value.id == "self"
        ) else ""

    for m in [n for n in cls.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]:
        # 생성자(초기화)의 빈 리스트 대입은 «비움»이 아니다 — 여기서 cleared 를 수집하면
        # no-op mark 디코이가 초기화만으로 ③을 충족해 버린다(fail-closed).
        is_ctor = m.name in ("__init__", "__post_init__")
        for node in ast.walk(m):
            if isinstance(node, ast.Return) and isinstance(node.value, ast.Call) \
                    and isinstance(node.value.func, ast.Name) \
                    and node.value.func.id == "tuple" and node.value.args:
                store = _self_attr(node.value.args[0])
                if store:
                    queried.add(store)
            if is_ctor:
                continue
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                    and node.func.attr == "clear":
                store = _self_attr(node.func.value)
                if store:
                    cleared.add(store)
            if isinstance(node, ast.Assign):
                for t in node.targets:
                    store = _self_attr(t)
                    if store and isinstance(node.value, (ast.List, ast.Tuple)) \
                            and not getattr(node.value, "elts", None):
                        cleared.add(store)
            if isinstance(node, ast.AnnAssign) and node.value is not None:
                store = _self_attr(node.target)
                if store and isinstance(node.value, (ast.List, ast.Tuple)) \
                        and not getattr(node.value, "elts", None):
                    cleared.add(store)
    return private_fields & queried & cleared


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
    if has_events_attr and not has_pull and not _journal_pending_stores(cls):
        f.add("#543", _rel(root, py, cls.lineno),
              "이벤트 기록은 있는데 pull_events() 가 없다 — 꺼내는 창구는 그 하나다")


def _closed_standard_enum(mod: ast.Module, cls: ast.ClassDef) -> tuple[bool, bool]:
    """정확한 표준 enum 기저 + 정적 멤버만 면제한다. 동적 확장은 후보다."""
    origins = {}
    for st in mod.body:
        if st is cls:
            break
        if isinstance(st, ast.ImportFrom):
            for a in st.names:
                origins.pop(a.asname or a.name, None)
            if st.module == "enum" and not st.level:
                origins.update({a.asname or a.name: "enum." + a.name for a in st.names})
        elif isinstance(st, ast.Import):
            for a in st.names:
                origins.pop(a.asname or a.name.split(".")[0], None)
                if a.name == "enum": origins[a.asname or a.name] = "enum"
        else:
            for n in ast.walk(st):
                if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store): origins.pop(n.id, None)
                if isinstance(n, ast.Attribute) and isinstance(n.ctx, (ast.Store, ast.Del)):
                    base = n.value
                    while isinstance(base, ast.Attribute): base = base.value
                    if isinstance(base, ast.Name): origins.pop(base.id, None)
            if isinstance(st, (ast.FunctionDef, ast.ClassDef)): origins.pop(st.name, None)
    def name(expr):
        if isinstance(expr, ast.Name): return origins.get(expr.id, "")
        if isinstance(expr, ast.Attribute): return name(expr.value) + "." + expr.attr
        return ""
    enum_based = any(name(b) in {"enum.Enum", "enum.StrEnum", "enum.IntEnum", "enum.Flag", "enum.IntFlag"} for b in cls.bases)
    if len(cls.bases) != 1 or cls.keywords or cls.decorator_list or name(cls.bases[0]) not in {
        "enum.Enum", "enum.StrEnum", "enum.IntEnum"
    }:
        return False, enum_based
    members = 0
    for st in cls.body:
        if isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if st.name in {"_missing_", "__new__", "__init__", "__call__"}: return False, enum_based
        elif isinstance(st, (ast.Assign, ast.AnnAssign)):
            targets = st.targets if isinstance(st, ast.Assign) else [st.target]
            if any(isinstance(t, ast.Name) and t.id in {"_missing_", "__new__", "__init__", "__call__"} for t in targets): return False, enum_based
            value = st.value
            if value is None: continue
            try:
                ast.literal_eval(value)
            except (ValueError, TypeError):
                if not (isinstance(value, ast.Call) and name(value.func) == "enum.auto" and not value.args and not value.keywords):
                    return False, enum_based
            members += 1
        elif not (isinstance(st, ast.Pass) or isinstance(st, ast.Expr) and isinstance(st.value, ast.Constant)):
            return False, enum_based
    aliases = {cls.name}
    for st in mod.body[mod.body.index(cls) + 1:]:
        if isinstance(st, ast.Assign) and isinstance(st.value, ast.Name) and st.value.id in aliases:
            aliases.update(t.id for t in st.targets if isinstance(t, ast.Name))
        for n in ast.walk(st):
            if isinstance(n, ast.Attribute) and isinstance(n.ctx, (ast.Store, ast.Del)) and isinstance(n.value, ast.Name) and n.value.id in aliases:
                return False, enum_based
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in {"setattr", "delattr"} and n.args and isinstance(n.args[0], ast.Name) and n.args[0].id in aliases:
                return False, enum_based
    return members > 0, enum_based


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
        closed_enum, enum_based = _closed_standard_enum(mod, cls)
        if not closed_enum and (not has_validation or enum_based):
            cand.add("#268", _rel(root, py, cls.lineno),
                     (f"`{cls.name}` 의 닫힌 표준 Enum 생성 검증을 확정할 수 없다 — "
                      "custom/open 생성 경로를 검토한다" if enum_based else
                      f"`{cls.name}` 의 __init__/__post_init__ 에 raise 가 없다 — 값 객체는 "
                      "만들어지는 시점에 스스로 검증한다"),
                     "Q2 — 이 타입 조합만으로 잘못된 값이 «불가능»한가")


def _check_domain_events(root: Path, bc: Path, agg: Path, ev_dir: Path, f: Findings) -> None:
    bc_texts: dict[Path, str] = {}
    for py in _py_files(bc):
        try:
            bc_texts[py] = py.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
    driven_only_dirs = ("driven_layer",)
    for py in folder_group.group_members(ev_dir, "*.py", promotable=False):
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
    for py in folder_group.group_members(shared, "*.py", promotable=False):
        mod = _parse(py)
        package = folder_group.package_of(py.relative_to(root).as_posix())
        for node in ast.walk(mod) if mod else []:
            if not isinstance(node, ast.ImportFrom):
                continue
            m = _absolute_module(package, node.level, node.module)
            if not m or m.split(".")[0] in STDLIB:
                continue
            ok = "shared_value_object" in m or m.split(".")[-1] == "exception" \
                 or ".exception." in m or m.endswith(".exception")
            if not ok:
                f.add("#298", _rel(root, py, node.lineno),
                      f"shared_value_object 가 `{m}` 를 import 한다 — 같은 폴더 안과 exception "
                      "모듈 말고는 아무것도 import 하지 않는다")


def _absolute_module(package: str, level: int, module: "str | None") -> str:
    """`from` import 의 대상 모듈 — 상대 import 는 그 파일의 패키지 기준 절대 경로로 푼다."""
    if level == 0:
        return module or ""
    parts = package.split(".") if package else []
    base = parts[: len(parts) - (level - 1)] if level - 1 <= len(parts) else []
    return ".".join(base + ([module] if module else []))


# ── domain_service — #301~#311 ─────────────────────────────────────────────

def _check_domain_services(root: Path, bc: Path, ds: Path, f: Findings, cand: Candidates) -> None:
    domain = bc / "domain_layer"
    agg_names = {d.name for d in _aggregate_dirs(domain)}
    root_classes = {_camel(n) for n in agg_names}
    # #311 — 파일명 낱말(`_` 경계) 하나가 애그리거트 낱말이거나 그 규칙 복수형이면 어휘가 있다(`visits` ∋ visit).
    agg_words = {form for a in agg_names for w in a.split("_") for form in _word_forms(w)}
    for py in folder_group.group_members(ds, "*.py", promotable=True):  # 묶음 안 · 승격 본체 포함(부품은 #15 재량 — 제외)
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
        elif not agg_words & stem_toks:
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
            arg_anns = [(_ann_names(a.annotation), a.arg)
                        for a in (*fn.args.posonlyargs, *fn.args.args, *fn.args.kwonlyargs)
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


# #506 — 이름을 낱말로 나눠 본다: `EventBus` 는 걸리고 앞글자만 같은 `BusySlots` · `BusinessHours` 는 걸리지 않는다.
PUBLISH_DEVICE_WORDS: frozenset[str] = frozenset({
    "Registry", "Registries", "Dispatcher", "Dispatchers", "Bus", "Buses", "Busses",
    "Signal", "Signals", "Signaler", "Signalers", "Signaller", "Signallers",
})
CAMEL_WORD: re.Pattern[str] = re.compile(r"[A-Z][a-z]*")


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
                            elif len(segs) >= 6:
                                f.add("#253", _rel(root, py, node.lineno),
                                      f"`{other}` 승격 루트의 부품 `{segs[5]}` import — 승격 루트가 "
                                      f"공개하는 것은 «루트 모듈»(패키지 `{other}.{other}`)뿐이다")
                    elif top not in STDLIB:
                        f.add("#8", _rel(root, py, node.lineno),
                              f"`{m}` — domain_layer 의 밖으로 나가는 import 는 0 이다")
            if isinstance(node, ast.ClassDef):
                if PUBLISH_DEVICE_WORDS & set(CAMEL_WORD.findall(node.name)):
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
    for node in _function_nodes(cls_or_fn):
        if isinstance(node, ast.arg) and node.annotation is not None:
            for n in _ann_names(node.annotation):
                if n.endswith("Repository"):
                    stem = n[: -len("Repository")]
                    out[node.arg] = re.sub(r"(?<!^)(?=[A-Z])", "_", stem).lower()
    return out


def _function_nodes(node: ast.AST):
    """내부 정의는 그 함수의 별도 검사에 맡긴다."""
    yield node
    for child in ast.iter_child_nodes(node):
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)):
            continue
        yield from _function_nodes(child)


def _transaction_write_regions(root: Path, py: Path, mod: ast.Module, fn: ast.AST,
                               cls: ast.ClassDef | None, repos: dict[str, str]):
    """lexical region만 관찰한다. 호출자/ATOMIC_REQUESTS/간접 helper의 commit 증명은 하지 않는다.

    반환: (구간 → 쓴 애그리거트 집합, 경계 불명 여부, 쓰기 호출 목록). 쓰기 호출 하나 =
    (호출, 구간, 그 호출을 감싼 구간 안 `for` 문들(바깥 → 안), 애그리거트) — #550 이 쓴다."""
    def key(expr):
        return ast.unparse(expr) if isinstance(expr, (ast.Name, ast.Attribute)) else ""

    def imports(body):
        result = {}
        for st in body:
            if isinstance(st, ast.ImportFrom):
                module = st.module or ""
                if st.level:
                    parts = py.relative_to(root).with_suffix("").parts[:-1]
                    module = ".".join((*parts[:len(parts) - st.level + 1], *module.split(".")))
                result.update({a.asname or a.name: module + "." + a.name for a in st.names})
            elif isinstance(st, ast.Import):
                result.update({a.asname or a.name.split(".")[0]: a.name if a.asname else a.name.split(".")[0] for a in st.names})
        return result

    def address(expr, env):
        if isinstance(expr, ast.Constant) and isinstance(expr.value, str):
            try: return address(ast.parse(expr.value, mode="eval").body, env)
            except SyntaxError: return ""
        if key(expr) in env: return env[key(expr)]
        if isinstance(expr, ast.Attribute):
            base = address(expr.value, env)
            return base + "." + expr.attr if base else ""
        return ""

    def is_uow(name):
        parts = name.split(".")
        return (".application_layer.port.unit_of_work." in name and len(parts) > 1
                and parts[-2].endswith("_unit_of_work") and parts[-1].endswith("UnitOfWork"))

    module_env = {}
    for st in mod.body:
        if isinstance(st, (ast.Import, ast.ImportFrom)):
            module_env.update(imports([st]))
        elif isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef)):
            module_env[st.name] = "@uow" if is_uow(address(st.returns, module_env)) else ""
        elif isinstance(st, ast.ClassDef):
            module_env[st.name] = ""
        elif isinstance(st, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
            for target in st.targets if isinstance(st, ast.Assign) else [st.target]:
                module_env[key(target)] = ""

    def origin(expr, env):
        if isinstance(expr, ast.Call):
            name = address(expr.func, env)
            if is_uow(name) or name == "@uow": return "@uow"
            parts = name.split(".")
            source = root.joinpath(*parts[:-1]).with_suffix(".py")
            declaration = _parse(source) if source.is_file() else None
            if declaration:
                target = next((st for st in declaration.body if isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef)) and st.name == parts[-1]), None)
                if target and is_uow(address(target.returns, imports(declaration.body))): return "@uow"
            return ""
        name = address(expr, env)
        return "@uow" if is_uow(name) else name

    def params(function, env):
        for arg in (*function.args.posonlyargs, *function.args.args, *function.args.kwonlyargs):
            env[arg.arg] = "@uow" if is_uow(address(arg.annotation, module_env)) else ""

    env = dict(module_env)
    if cls:
        init = next((st for st in cls.body if isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef)) and st.name == "__init__"), None)
        if init:
            init_env = dict(module_env)
            params(init, init_env)
            # 생성자 직접 주입/별칭만 지원한다. 분기·helper는 확정하지 않는다.
            for st in init.body:
                if isinstance(st, (ast.Assign, ast.AnnAssign)):
                    value = origin(st.value, init_env)
                    for target in st.targets if isinstance(st, ast.Assign) else [st.target]:
                        init_env[key(target)] = value
                elif not isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    for target in _function_nodes(st):
                        if isinstance(target, (ast.Name, ast.Attribute)) and isinstance(target.ctx, (ast.Store, ast.Del)):
                            init_env[key(target)] = ""
            env.update({k: v for k, v in init_env.items() if k.startswith("self.")})
    params(fn, env)
    regions = {0: set()}
    unknown = False
    writes = []
    loops = []

    def atomic(expr, local):
        target = expr.func if isinstance(expr, ast.Call) else expr
        return address(target, local) == "django.db.transaction.atomic"

    def scan(expr, local, region):
        nonlocal unknown
        for node in _function_nodes(expr):
            if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute): continue
            recv = node.func.value
            repo_key = recv.id if isinstance(recv, ast.Name) else recv.attr if isinstance(recv, ast.Attribute) and isinstance(recv.value, ast.Name) and recv.value.id == "self" else ""
            agg = repos.get(repo_key)
            if agg and node.func.attr.split("_", 1)[0] in {"save", "remove"}:
                regions.setdefault(region, set()).add(agg)
                writes.append((node, region, tuple(loops), agg))
            name = address(node.func, local)
            if name.startswith("django.db.transaction.") and name != "django.db.transaction.atomic": unknown = True

    def block(body, local, region):
        nonlocal unknown
        for st in body:
            if isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                local[st.name] = ""
                continue
            if isinstance(st, (ast.With, ast.AsyncWith)):
                child = dict(local)
                kinds = [atomic(item.context_expr, local) or origin(item.context_expr, local) == "@uow" for item in st.items]
                next_region = region
                if not all(kinds):
                    unknown = True
                    if region == 0: next_region = -1
                elif region == 0:
                    next_region = st.lineno
                for item in st.items:
                    scan(item.context_expr, local, region)
                    if item.optional_vars: child[key(item.optional_vars)] = origin(item.context_expr, local)
                block(st.body, child, next_region)
                aliases = {key(i.optional_vars) for i in st.items if i.optional_vars}
                for k, v in child.items():
                    if k not in aliases:
                        local[k] = "" if v == "@uow" and local.get(k) != v else v
                continue
            if isinstance(st, (ast.If, ast.For, ast.AsyncFor, ast.While, ast.Try)):
                for field in ("test", "iter"):
                    value = getattr(st, field, None)
                    if value: scan(value, local, region)
                branches = []
                loop_in_region = region != 0 and isinstance(st, (ast.For, ast.AsyncFor))
                for branch_body in (st.body, st.orelse):
                    branch = dict(local)
                    if isinstance(st, (ast.For, ast.AsyncFor)): branch[key(st.target)] = ""
                    if loop_in_region and branch_body is st.body: loops.append(st)
                    block(branch_body, branch, region)
                    if loop_in_region and branch_body is st.body: loops.pop()
                    branches.append(branch)
                if isinstance(st, ast.Try):
                    for handler in st.handlers:
                        branch = dict(local)
                        if handler.name: branch[handler.name] = ""
                        block(handler.body, branch, region)
                        branches.append(branch)
                for k in set().union(*(b.keys() for b in branches)):
                    values = {b.get(k, "") for b in branches}
                    local[k] = values.pop() if len(values) == 1 else ""
                if isinstance(st, ast.Try): block(st.finalbody, local, region)
                continue
            scan(st, local, region)
            if isinstance(st, (ast.Import, ast.ImportFrom)): local.update(imports([st]))
            if isinstance(st, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
                value = origin(st.value, local) if not isinstance(st, ast.AugAssign) else ""
                for target in st.targets if isinstance(st, ast.Assign) else [st.target]:
                    local[key(target)] = value
    decorators = fn.decorator_list
    region = fn.lineno if any(atomic(d, env) for d in decorators) else 0
    if any(not atomic(d, env) for d in decorators): unknown = True
    block(fn.body, env, region)
    return regions, unknown, writes


# #550 — 조회 머리 · «여럿» 주석의 바깥 이름 · 반복 대상 포장 · 교정 문면.
READ_HEADS = ("get", "find", "list", "search")
MANY_ANNOTATIONS = {"list", "List", "tuple", "Tuple", "Sequence", "MutableSequence", "Iterable", "Iterator",
                    "Collection", "set", "Set", "frozenset", "FrozenSet", "AbstractSet"}
LOOP_WRAPPERS = ("list", "tuple", "sorted", "reversed", "enumerate")
TRY_NODES = tuple(t for t in (ast.Try, getattr(ast, "TryStar", None)) if t)
MATCH_NODE = getattr(ast, "Match", None)
M550 = ("한 트랜잭션은 애그리거트 «하나»를 바꾼다: 같이 되돌려야 하면 한 애그리거트로 묶고, 아니면 건마다 트랜잭션을 연다"
        "(반복문 안에서 `with uow`) — 묶음은 새로 만들 때만")
# #550 행 3 · #546 확정의 꼬리 — 따로 꺼낸 것 둘(같은 타입 · 다른 타입)은 이름 붙은 승인 예외(함께 커밋)의 자리가 있다.
M_JOINT = ("한 트랜잭션은 애그리거트 «하나»를 바꾼다: 같이 되돌려야 하면 먼저 경계(한 애그리거트 · 이동 기록)를, 이미 있는 둘을 "
           "함께 바꿔야 하면 설계로 돌려 G1 승인(함께 커밋)을 받는다 — 코드에서 표지만 달지 않는다")
M_SWALLOW = ("승인 구간 안에서 쓰기 실패를 받아 삼킨다(`try` 의 `except` 가 `raise` 로 끝나지 않거나 · `except` · `finally` 몸이 "
             "`continue` · `break` · `return` 으로 빠져나가거나 · `suppress`) — 하나라도 실패하면 둘 다 그대로여야 한다: 예외 받기 · "
             "다시 하기는 `with` 바깥에 둔다(시도마다 새 트랜잭션)")


def _read_assignments(fn: ast.AST) -> dict[str, list[ast.Call]]:
    """이름 → 그 이름에 담은 조회 호출(get·find·list·search 머리 메서드)들 — 주석 유무와 무관하게 차례대로."""
    out: dict[str, list[ast.Call]] = {}
    for n in _function_nodes(fn):
        if isinstance(n, ast.Assign) and len(n.targets) == 1:
            target = n.targets[0]
        elif isinstance(n, ast.AnnAssign):
            target = n.target
        else:
            continue
        value = n.value
        if isinstance(target, ast.Name) and isinstance(value, ast.Call) and isinstance(value.func, ast.Attribute) \
                and value.func.attr.split("_", 1)[0] in READ_HEADS:
            out.setdefault(target.id, []).append(value)
    return out


def _many_read_names(fn: ast.AST, reads: dict[str, list[ast.Call]]) -> set[str]:
    """조회로 꺼낸 «여럿» — 첫 주석 대입(#493 이 강제하는 주석)의 바깥 이름이 컬렉션인 조회 이름."""
    first: dict[str, ast.expr] = {}
    for n in _function_nodes(fn):
        if isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name):
            first.setdefault(n.target.id, n.annotation)
    out: set[str] = set()
    for name in reads:
        ann = first.get(name)
        outer = ann.value if isinstance(ann, ast.Subscript) else ann
        word = outer.id if isinstance(outer, ast.Name) else outer.attr if isinstance(outer, ast.Attribute) else ""
        if word in MANY_ANNOTATIONS:
            out.add(name)
    return out


def _many_argument(arg: ast.expr, many: set[str]) -> str | None:
    """#550 행 1 인자 꼴 — «여럿» 이름 · 그 `tuple(..)` · `list(..)` · 원소식이 반복 변수 그 자체인 컴프리헨션."""
    if isinstance(arg, ast.Name):
        return arg.id if arg.id in many else None
    if isinstance(arg, ast.Call) and isinstance(arg.func, ast.Name) and arg.func.id in ("tuple", "list") \
            and len(arg.args) == 1 and not arg.keywords:
        return _many_argument(arg.args[0], many)
    if isinstance(arg, (ast.ListComp, ast.SetComp, ast.GeneratorExp)) and len(arg.generators) == 1:
        gen = arg.generators[0]
        if isinstance(gen.iter, ast.Name) and gen.iter.id in many and isinstance(gen.target, ast.Name) \
                and isinstance(arg.elt, ast.Name) and arg.elt.id == gen.target.id:
            return gen.iter.id
    return None


def _loop_source(it: ast.expr, reads: dict[str, list[ast.Call]], repos: dict[str, str]) -> str | None:
    """반복 대상이 조회한 여럿인가 — 조회 이름이나 묶인 저장소의 조회 호출(그대로이거나 `list` · `tuple` · `sorted` ·
    `reversed` · `enumerate` 로 싼 것). 반환: 문면에 보일 출처."""
    while isinstance(it, ast.Call) and isinstance(it.func, ast.Name) and it.func.id in LOOP_WRAPPERS and it.args:
        it = it.args[0]
    if isinstance(it, ast.Name):
        return it.id if it.id in reads else None
    if isinstance(it, ast.Call) and isinstance(it.func, ast.Attribute) \
            and it.func.attr.split("_", 1)[0] in READ_HEADS:
        recv = it.func.value
        key = recv.id if isinstance(recv, ast.Name) else recv.attr if isinstance(recv, ast.Attribute) \
            and isinstance(recv.value, ast.Name) and recv.value.id == "self" else ""
        return f"{it.func.attr}(…)" if key in repos else None
    return None


def _read_by_loop(calls: list[ast.Call], loop: ast.AST, targets: set[str]) -> bool:
    """이 반복문 몸 안의 조회 호출이 반복 변수에 기댄 인자로 불렸는가(같은 키를 다시 읽는 재시도 고리는 아니다)."""
    inside = {id(x) for st in loop.body for x in ast.walk(st)}
    return any(id(c) in inside and any(isinstance(x, ast.Name) and x.id in targets
                                       for a in (*c.args, *(k.value for k in c.keywords)) for x in ast.walk(a))
               for c in calls)


def _leaves_loop_after(call: ast.Call, loop: ast.AST, parents: dict, write_args: dict[int, str]) -> bool:
    """쓴 뒤 길이 다른 이름의 쓰기 · `continue` · 중첩 고리 없이 `return` · `raise` 나 이 반복문을 나가는 `break` 로
    끝나는가 — 한 실행에 하나만 바꾼다(같은 이름을 다시 쓰는 것은 같은 애그리거트라 센다 밖). 쓴 뒤 길 = 쓰기가 든
    문장 목록의 나머지, 또는 쓰기(나 그 결과를 담은 이름)가 검사식인 마지막 `if` 의 참 갈래(CAS — 거짓 갈래는 쓰지 않은
    길이라 쓰기만 없으면 된다). 결과 이름의 `if not <이름>:` 몸에 바로 든 `continue` 도 쓰지 않은 길이다."""
    name = call.args[0].id
    stmt = call
    while not isinstance(stmt, ast.stmt):
        stmt = parents[stmt]
    if isinstance(stmt, ast.Return):
        return True
    result = None
    if isinstance(stmt, ast.If) and stmt.test is call:
        gate = stmt
    else:
        owner = parents.get(stmt)
        seq = next((s for s in (getattr(owner, f, None) for f in ("body", "orelse", "finalbody"))
                    if isinstance(s, list) and any(x is stmt for x in s)), None)
        if seq is None:
            return False
        rest = seq[next(i for i, s in enumerate(seq) if s is stmt) + 1:]
        if isinstance(stmt, (ast.Assign, ast.AnnAssign)) and stmt.value is call:
            target = stmt.target if isinstance(stmt, ast.AnnAssign) else stmt.targets[0] if len(stmt.targets) == 1 else None
            result = target.id if isinstance(target, ast.Name) else None
        gate = rest[0] if result and len(rest) == 1 and isinstance(rest[0], ast.If) \
            and isinstance(rest[0].test, ast.Name) and rest[0].test.id == result else None
    if gate is not None:
        if any(id(x) in write_args for st in gate.orelse for x in ast.walk(st)):
            return False
        owner, seq, rest = gate, gate.body, gate.body
    if not seq or seq[-1] is stmt or not isinstance(seq[-1], (ast.Return, ast.Raise, ast.Break)):
        return False
    missed = {id(c) for st in rest if isinstance(st, ast.If) and isinstance(st.test, ast.UnaryOp)
              and isinstance(st.test.op, ast.Not) and isinstance(st.test.operand, ast.Name)
              and st.test.operand.id == result for c in st.body if isinstance(c, ast.Continue)}
    if any(isinstance(x, (ast.For, ast.AsyncFor, ast.While))
           or (isinstance(x, ast.Continue) and id(x) not in missed)
           or (id(x) in write_args and write_args[id(x)] != name)
           for st in rest for x in ast.walk(st)):
        return False
    if isinstance(seq[-1], ast.Break):
        cur = owner
        while cur is not None and not isinstance(cur, (ast.For, ast.AsyncFor, ast.While)):
            cur = parents.get(cur)
        return cur is loop
    return True


def _arms(node: ast.AST, parents: dict) -> dict[int, str]:
    """노드가 놓인 갈래 — 갈래 문(if · try · match)마다 어느 팔에 있는가(try 몸과 else 는 한 팔 · finally 는 팔이 아니다)."""
    out: dict[int, str] = {}
    cur = node
    while cur in parents:
        par = parents[cur]
        arm = None
        if isinstance(par, ast.If):
            arm = "body" if any(s is cur for s in par.body) else "else" if any(s is cur for s in par.orelse) else None
        elif isinstance(par, TRY_NODES):
            if any(s is cur for s in (*par.body, *par.orelse)):
                arm = "body"
            else:
                arm = next((f"except{i}" for i, h in enumerate(par.handlers) if h is cur), None)
        elif MATCH_NODE is not None and isinstance(par, MATCH_NODE):
            arm = next((f"case{i}" for i, c in enumerate(par.cases) if c is cur), None)
        if arm is not None:
            out[id(par)] = arm
        cur = par
    return out


def _region_writes_550(fn: ast.AST, writes: list, reads: dict[str, list[ast.Call]],
                       flagged: set[int], repos: dict[str, str],
                       excused: "set[int] | frozenset[int]" = frozenset(),
                       params: "Callable[[ast.Call], list[str] | None]" = lambda c: None,
                       cas: "Callable[[ast.AST], bool]" = lambda c: False) -> list[tuple[int, str]]:
    """#550 행 2 · 행 3 — 같은 transaction 구간에서 조회한 애그리거트 여럿을 쓴다. 반환: (줄, 문면)."""
    if not any(region > 0 for _, region, _, _ in writes):
        return []
    parents = {child: parent for parent in _function_nodes(fn) for child in ast.iter_child_nodes(parent)}
    write_args = {id(w[0]): (w[0].args[0].id if w[0].args and isinstance(w[0].args[0], ast.Name) else "")
                  for w in writes}
    out: list[tuple[int, str]] = []
    pool: dict[tuple[int, str], list[tuple[str, ast.Call]]] = {}
    for call, region, loops, agg in writes:
        if region <= 0 or id(call) in flagged or not call.args or not isinstance(call.args[0], ast.Name):
            continue
        name, meth = call.args[0].id, call.func.attr
        message = None
        for loop in loops:
            targets = {x.id for x in ast.walk(loop.target) if isinstance(x, ast.Name)}
            source = _loop_source(loop.iter, reads, repos) if name in targets else None
            if source is not None:
                found = f"조회로 꺼낸 여럿(`{source}`)을 도는 반복문이 한 트랜잭션 안에서 `{meth}` 로 쓴다"
            elif _read_by_loop(reads.get(name, []), loop, targets):
                found = f"한 트랜잭션 안 반복문에서 반복 변수로 조회한 애그리거트(`{name}`)를 `{meth}` 로 쓴다"
            else:
                continue
            if not _leaves_loop_after(call, loop, parents, write_args):
                message = found
                break
        literal_loop = next((lp for lp in loops if _literal_names(lp.iter) is not None
                             and name in {x.id for x in ast.walk(lp.target) if isinstance(x, ast.Name)}), None)
        if message is not None:
            out.append((call.lineno, f"{message} — {M550}"))
        elif id(call) in excused:
            continue
        elif name in reads:
            pool.setdefault((region, agg), []).append((name, call))
        elif literal_loop is not None and not _leaves_loop_after(call, literal_loop, parents, write_args):
            # 글자 고리(`for x in sorted((a, b), key=…)`) — 원소 이름마다 쓴 것(한 건만 바꾸고 나가는 고리는 뺀다).
            for element in _literal_names(literal_loop.iter) or []:
                if element in reads:
                    pool.setdefault((region, agg), []).append((element, call))
        elif (comp := _literal_comprehension(call, name, parents)) is not None:
            # 컴프리헨션 글자 고리(`[save(o) for o in (a, b)]`) — 원소 이름마다 쓴 것.
            for element in comp:
                if element in reads:
                    pool.setdefault((region, agg), []).append((element, call))
    for (region, _agg), items in pool.items():
        # 행 3 — 같은 저장소 타입 · 같은 실행 길(배타 갈래 제외) · 조회 인자가 다른 두 이름(같은 인자면 같은 애그리거트).
        pair = next(((a, b) for i, a in enumerate(items) for b in items[i + 1:]
                     if a[0] != b[0] and _read_key(reads[a[0]][0], params(reads[a[0]][0]))
                     != _read_key(reads[b[0]][0], params(reads[b[0]][0]))
                     and not _exclusive(a[1], b[1], parents, cas, region)), None)
        if pair is not None:
            (first, _), (second, call) = pair
            out.append((call.lineno, f"한 트랜잭션에서 따로 조회한 애그리거트 둘(`{first}` · `{second}`)을 차례로 쓴다 — {M_JOINT}"))
    return out


def _read_key(call: ast.Call, params: "list[str] | None" = None) -> str:
    """조회 호출 인자의 지문 — 인자 «값» 을 자리 차례로 둔다(키워드는 저장소 선언의 그 메서드 매개변수 자리에 놓는다 · 자리를
    모르는 키워드는 «이름=값» 으로 뒤에 · 선언 없이 키워드 하나뿐이면 첫 자리). 읽기 메서드가 달라도(get · get_for_update) 자리
    값이 같으면 같은 애그리거트 · 자리만 바뀐 두 조회(`get(a, b)` · `get(b, a)`)는 다른 애그리거트."""
    slots: dict[int, str] = {i: ast.dump(a) for i, a in enumerate(call.args)}
    rest: list[str] = []
    for k in call.keywords:
        if params and k.arg in params:
            slots[params.index(k.arg)] = ast.dump(k.value)
        else:
            rest.append(f"{k.arg}={ast.dump(k.value)}")
    if not call.args and len(call.keywords) == 1 and rest:
        slots, rest = {0: ast.dump(call.keywords[0].value)}, []
    return repr((sorted(slots.items()), sorted(rest)))


def _exclusive(a: ast.AST, b: ast.AST, parents: dict, cas: "Callable[[ast.AST], bool]" = lambda c: False,
               region: int = 0) -> bool:
    """두 노드가 서로 배타인 갈래(if/else · match case · try 몸/except · except 끼리)에 있는가.
    ⑴ `if not <쓰기 a>:` 몸 안의 쓰기 b(CAS 미스 = a 를 쓰지 않음) ⑵ a 가 든 문장 목록이 `return` · `raise` 로
    끝나고 b 가 그 목록 밖 뒤쪽이면 한 실행에 둘 다 일어나지 않는다."""
    arms_a, arms_b = _arms(a, parents), _arms(b, parents)
    if any(k in arms_b and arms_b[k] != v for k, v in arms_a.items()):
        return True
    return any(_cas_miss_body(x, y, parents, cas, region) or _returns_before(x, y, parents) for x, y in ((a, b), (b, a)))


def _cas_test_if(x: ast.AST, parents: dict) -> "tuple[ast.If, bool, bool] | None":
    """쓰기 x 를 검사식으로 받는 `if` · `not` 여부 · 결과 이름 꼴 여부 — `if [not] x(..):` 또는 결과를 이름에 담고 바로 다음
    문장이 `if [not] <이름>:`(`_leaves_loop_after` · 표지 판정의 CAS 받기와 같은 판독)."""
    par = parents.get(x)
    if isinstance(par, ast.If) and par.test is x:
        return par, False, False
    if isinstance(par, ast.UnaryOp) and isinstance(par.op, ast.Not) and isinstance(parents.get(par), ast.If) \
            and parents[par].test is par:
        return parents[par], True, False
    if not isinstance(par, (ast.Assign, ast.AnnAssign)) or par.value is not x:
        return None
    target = par.targets[0] if isinstance(par, ast.Assign) and len(par.targets) == 1 else getattr(par, "target", None)
    owner = parents.get(par)
    seq = next((getattr(owner, f) for f in ("body", "orelse", "finalbody")
                if isinstance(getattr(owner, f, None), list) and any(st is par for st in getattr(owner, f))), [])
    at = next((i for i, st in enumerate(seq) if st is par), None)
    nxt = seq[at + 1] if at is not None and at + 1 < len(seq) else None
    if not isinstance(target, ast.Name) or not isinstance(nxt, ast.If):
        return None
    test = nxt.test
    if isinstance(test, ast.Name) and test.id == target.id:
        return nxt, False, True
    if isinstance(test, ast.UnaryOp) and isinstance(test.op, ast.Not) and isinstance(test.operand, ast.Name) \
            and test.operand.id == target.id:
        return nxt, True, True
    return None


def _cas_miss_body(x: ast.AST, y: ast.AST, parents: dict, cas: "Callable[[ast.AST], bool]" = lambda c: False,
                   region: int = 0) -> bool:
    """y 가 쓰기 x 가 «쓰지 않은» 길에만 있는가 — ⑴ `if not x(..):` 몸 안(설계 §5 고침 ⑴) ⑵ x 가 CAS(저장소 선언 `-> bool`)이고
    결과 이름 꼴 `n = x` · 바로 다음 `if not n:` 몸 안 ⑶ x 가 CAS 이고 `if x:`(결과 이름 꼴 포함) 몸이 그 앞에서 고리를 나가지 않고
    `return` · `raise` 로 끝나며 y 가 그 몸 밖 뒤쪽 — 그 `if` 가 쓰기 구간(줄 region 의 트랜잭션 `with`) 안 고리 속이 아니고 y 가
    구간 안에서 그것을 감싼 `try` 의 `finally` 밖일 때만(구간 바깥 고리는 시도마다 새 트랜잭션이다)."""
    hit = _cas_test_if(x, parents)
    if hit is None:
        return False
    node, negated, named = hit
    if (named or not negated) and not cas(x):
        return False
    inside = {id(n) for st in node.body for n in ast.walk(st)}
    if negated:
        return id(y) in inside
    up: ast.AST = node
    while up in parents and not isinstance(up, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
        child, up = up, parents[up]
        if isinstance(up, (ast.With, ast.AsyncWith)) and up.lineno == region:
            break
        if isinstance(up, (ast.For, ast.AsyncFor, ast.While)):
            return False
        if isinstance(up, TRY_NODES) and not any(st is child for st in up.finalbody) \
                and id(y) in {id(n) for st in up.finalbody for n in ast.walk(st)}:
            return False
    return (isinstance(node.body[-1], (ast.Return, ast.Raise)) and not _escapes(node.body[:-1])
            and id(y) not in inside and y.lineno > node.body[-1].lineno)


def _returns_before(x: ast.AST, y: ast.AST, parents: dict) -> bool:
    """x 를 감싼 문장 목록 하나가 `return` · `raise` 로 끝나고 y 가 그 목록 밖 · 그 끝보다 뒤쪽인가."""
    stmt = x
    while not isinstance(stmt, ast.stmt):
        stmt = parents[stmt]
    while stmt in parents:
        owner = parents[stmt]
        for field in ("body", "orelse", "finalbody"):
            seq = getattr(owner, field, None)
            if isinstance(seq, list) and any(s is stmt for s in seq):
                inside = {id(n) for st in seq for n in ast.walk(st)}
                if isinstance(seq[-1], (ast.Return, ast.Raise)) and id(y) not in inside \
                        and y.lineno > seq[-1].lineno:
                    return True
        if isinstance(owner, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return False
        stmt = owner
    return False


LITERAL_WRAPPERS = ("sorted", "list", "tuple", "reversed")
_JOINT_CACHE: dict = {}


def _literal_names(it: ast.expr) -> list[str] | None:
    """반복 대상이 글자 그대로의 튜플 · 리스트 · 집합(`sorted` · `list` · `tuple` · `reversed` 로 싼 것 포함)이면 원소 이름들."""
    while isinstance(it, ast.Call) and isinstance(it.func, ast.Name) and it.func.id in LITERAL_WRAPPERS and it.args:
        it = it.args[0]
    if isinstance(it, (ast.Tuple, ast.List, ast.Set)) and it.elts and all(isinstance(e, ast.Name) for e in it.elts):
        return [e.id for e in it.elts]
    return None


def _escapes(stmts: list) -> bool:
    """문장 목록 안에 그 목록 밖으로 나가는 `return` · (안에서 새로 연 고리 밖의) `continue` · `break` 가 있는가 — 함수 · 람다 ·
    클래스 정의 안은 보지 않는다."""
    def walk(node: ast.AST, in_loop: bool) -> bool:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)):
            return False
        if isinstance(node, ast.Return) or (isinstance(node, (ast.Continue, ast.Break)) and not in_loop):
            return True
        loop = in_loop or isinstance(node, (ast.For, ast.AsyncFor, ast.While))
        return any(walk(c, loop) for c in ast.iter_child_nodes(node))
    return any(walk(s, False) for s in stmts or [])


def _literal_comprehension(call: ast.Call, name: str, parents: dict) -> list[str] | None:
    """쓰기가 컴프리헨션 안이고 그 반복 변수(name)가 글자 튜플 · 리스트 · 집합을 돌면 원소 이름들."""
    cur = call
    while cur in parents and not isinstance(cur, ast.stmt):
        cur = parents[cur]
        if isinstance(cur, (ast.ListComp, ast.SetComp, ast.GeneratorExp, ast.DictComp)):
            outer = parents.get(cur)
            if isinstance(cur, ast.GeneratorExp) and isinstance(outer, ast.Call) and isinstance(outer.func, ast.Name) \
                    and outer.func.id in ("any", "next") and outer.args and outer.args[0] is cur:
                return None  # 먼저 된 하나만 쓰고 나간다 — 고리 꼴의 `_leaves_loop_after` 와 같은 뜻(검토 v4.1 S-2)
            for gen in cur.generators:
                if name in {x.id for x in ast.walk(gen.target) if isinstance(x, ast.Name)}:
                    return _literal_names(gen.iter)
            return None
    return None


def _receiver_agg(call: ast.Call, bindings: dict[str, str]) -> str | None:
    recv = call.func.value if isinstance(call.func, ast.Attribute) else None
    key = recv.id if isinstance(recv, ast.Name) else recv.attr if isinstance(recv, ast.Attribute) \
        and isinstance(recv.value, ast.Name) and recv.value.id == "self" else ""
    return bindings.get(key)


def _repo_read(name: str, agg: str, reads: dict, bindings: dict[str, str]) -> bool:
    """이름이 그 애그리거트 저장소의 조회(get · find · list · search 머리)로 꺼낸 것인가 — 이미 있는 애그리거트."""
    return any(_receiver_agg(c, bindings) == agg for c in reads.get(name, []))


def _literal_pair(arg: ast.expr, reads: dict, bindings: dict[str, str]) -> str | None:
    """#550 행 1 넓힘 — 저장소 조회 이름 둘 이상을 담은 글자 튜플 · 리스트 · 집합(`save_all((a, b))`)."""
    if isinstance(arg, (ast.Tuple, ast.List, ast.Set)):
        names = [e.id for e in arg.elts if isinstance(e, ast.Name)
                 and any(_receiver_agg(c, bindings) for c in reads.get(e.id, []))]
        if len(set(names)) >= 2:
            return ", ".join(dict.fromkeys(names))
    return None


def _repo_methods(root: Path, bc: str, agg: str) -> "dict[str, ast.FunctionDef | ast.AsyncFunctionDef]":
    """저장소 선언 `domain_layer/<agg>/<agg>_repository.py` 의 메서드(같은 파일 선언만 읽는다)."""
    key = ("methods", root, bc, agg)
    if key not in _JOINT_CACHE:
        src = root / "application" / bc / "domain_layer" / agg / f"{agg}_repository.py"
        try:
            mod = ast.parse(src.read_text(encoding="utf-8"))
        except (OSError, SyntaxError, UnicodeDecodeError):
            mod = None
        _JOINT_CACHE[key] = {n.name: n for n in (ast.walk(mod) if mod else [])
                             if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    return _JOINT_CACHE[key]


def _bool_writes(root: Path, bc: str, agg: str) -> set[str]:
    """저장소 선언에서 `-> bool`(글자 `"bool"` 포함)인 쓰기(CAS) 메서드 이름."""
    return {name for name, n in _repo_methods(root, bc, agg).items() if name.split("_", 1)[0] in ("save", "remove")
            and ((isinstance(n.returns, ast.Name) and n.returns.id == "bool")
                 or (isinstance(n.returns, ast.Constant) and n.returns.value == "bool"))}


def _read_params(root: Path, bc: str, call: ast.Call, bindings: dict[str, str]) -> "list[str] | None":
    """조회 호출이 부르는 저장소 메서드의 매개변수 자리 차례(`self` 빼고) — 선언을 못 읽으면 None."""
    agg = _receiver_agg(call, bindings) if isinstance(call.func, ast.Attribute) else None
    method = _repo_methods(root, bc, agg).get(call.func.attr) if agg else None
    if method is None:
        return None
    names = [a.arg for a in method.args.posonlyargs + method.args.args]
    return names[1:] if names[:1] == ["self"] else names


def _is_cas(root: Path, bc: str, call: ast.AST, bindings: dict[str, str]) -> bool:
    """저장소 선언이 `-> bool` 인 쓰기 호출인가."""
    agg = _receiver_agg(call, bindings) if isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute) else None
    return agg is not None and call.func.attr in _bool_writes(root, bc, agg)


def _sorted_unpack(fn: ast.AST, before: int) -> list[str] | None:
    """함수 안 `a, b = sorted(...)`(그 줄이 before 앞) 의 이름 차례."""
    best = None
    for n in _function_nodes(fn):
        if isinstance(n, ast.Assign) and n.lineno < before and len(n.targets) == 1 \
                and isinstance(n.targets[0], ast.Tuple) and isinstance(n.value, ast.Call) \
                and isinstance(n.value.func, ast.Name) and n.value.func.id == "sorted":
            best = [e.id for e in n.targets[0].elts if isinstance(e, ast.Name)]
    return best


def _key_mentions(call: ast.Call, key: str) -> bool:
    kw = next((k.value for k in call.keywords if k.arg == "key"), None)
    if kw is None:
        return True
    return any((isinstance(x, ast.Attribute) and x.attr == key) or (isinstance(x, ast.Constant) and x.value == key)
               for x in ast.walk(kw))


def _sorted_literal_loop(node: ast.AST) -> bool:
    return isinstance(node, (ast.For, ast.AsyncFor)) and isinstance(node.iter, ast.Call) \
        and isinstance(node.iter.func, ast.Name) and node.iter.func.id == "sorted" and _literal_names(node.iter) is not None


def _joint_verdict(root: Path, bc: str, fn: ast.AST, w: ast.AST, row, writes: list, reads: dict, parents: dict,
                   bindings: dict[str, str], row1_ids: set[int]) -> str | None:
    """표지가 덮는 `with` 하나를 표지 칸(= G1 승인 행 끝 칸)과 대조한다 — 문제가 없으면 None."""
    if row is None:
        return (f"표지 꼴이 틀렸다 — {checker_target.JOINT_MARK_FORM} — 표지는 G1 승인 행이 있는 함께 커밋에만 단다"
                "(승인 행이 없으면 표지를 지우고 이 함께 쓰기를 설계로 돌린다 — pending)")
    if row.malformed:
        return f"표지 칸 꼴이 틀렸다 — {row.malformed}(설계로 돌린다 — 표지만 고쳐 풀지 않는다)"
    row = {"aggs": dict(row.aggs), "lock": list(row.lock)}
    inside = {id(x) for st in w.body for x in ast.walk(st)}
    mine = [wr for wr in writes if id(wr[0]) in inside]
    if any(region == -1 for _c, region, _l, _a in mine):
        return ("표지는 검사기가 트랜잭션으로 읽는 `with`(작업 단위 · `transaction.atomic`) 바로 위에만 단다 — 이 `with` 를 "
                "트랜잭션으로 읽지 못했다(승인 꼴로 쓴다)")
    if any(region != w.lineno for _c, region, _l, _a in mine):
        return "표지는 트랜잭션을 여는 바깥 `with` 바로 위에 단다 — 이 `with` 는 바깥 트랜잭션(작업 단위 · atomic) 안에 있다"
    types = {agg for *_, agg in mine}
    fu: dict[str, list[ast.Call]] = {}
    for st in w.body:
        for n in ast.walk(st):
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and "for_update" in n.func.attr:
                agg = _receiver_agg(n, bindings)
                if agg:
                    fu.setdefault(agg, []).append(n)
    names: dict[str, set[str]] = {}
    for call, _region, loops, agg in mine:
        if not call.args or not isinstance(call.args[0], ast.Name):
            continue
        name = call.args[0].id
        if _repo_read(name, agg, reads, bindings):
            names.setdefault(agg, set()).add(name)
        for lp in loops:
            if name in {x.id for x in ast.walk(lp.target) if isinstance(x, ast.Name)}:
                names.setdefault(agg, set()).update(
                    e for e in (_literal_names(lp.iter) or []) if _repo_read(e, agg, reads, bindings))
    existing = {t: max(len(names.get(t, ())), len(fu.get(t, ()))) for t in types | set(fu)}
    made = {t.id for n in _function_nodes(fn) if isinstance(n, (ast.Assign, ast.AnnAssign)) and isinstance(n.value, ast.Call)
            and _receiver_agg(n.value, bindings) is None
            for t in (n.targets if isinstance(n, ast.Assign) else [n.target]) if isinstance(t, ast.Name)}

    loops_of = {id(c): lps for c, _r, lps, _a in mine}

    def new_name(name: str, agg: str) -> bool:
        """저장소 밖 호출로 만든 이름이고 그 타입 조회 · 잠금으로 꺼낸 이름이 아닌가."""
        return name in made and name not in names.get(agg, set())

    def fresh_keys(expr: ast.AST, agg: str, loops: tuple = ()) -> "list[str] | None":
        """새로 만든 것만 쓰는 인자면 그 열쇠들 — 저장소 밖 호출로 만든 이름(조회 · 잠금 이름이 아닌) · 그 자리 생성 호출 · 그런 것만
        담은 글자 튜플 · 리스트 · 집합(`save_all((a, b))`) · 그런 이름만 도는 글자 고리의 반복 변수(반복 변수는 그 고리의 글자
        원소로만 가린다 — 같은 이름의 다른 대입은 보지 않는다)."""
        if isinstance(expr, ast.Name):
            loop = next((lp for lp in reversed(loops) if isinstance(lp, (ast.For, ast.AsyncFor))
                         and isinstance(lp.target, ast.Name) and lp.target.id == expr.id), None)
            if loop is not None:
                elements = _literal_names(loop.iter)
                return list(elements) if elements and all(new_name(e, agg) for e in elements) else None
            return [expr.id] if new_name(expr.id, agg) else None
        if isinstance(expr, ast.Call):
            return [f"@{expr.lineno}:{expr.col_offset}"] if _receiver_agg(expr, bindings) is None else None
        if isinstance(expr, (ast.Tuple, ast.List, ast.Set)) and expr.elts:
            parts = [fresh_keys(e, agg) for e in expr.elts]
            return [k for part in parts for k in part] if all(part is not None for part in parts) else None
        return None

    def is_fresh(c: ast.Call, agg: str) -> bool:
        """새로 만든 것의 쓰기(`fresh_keys`)."""
        return bool(c.args) and fresh_keys(c.args[0], agg, loops_of.get(id(c), ())) is not None
    fresh: dict[str, set[str]] = {}
    for call, _region, loops, agg in mine:
        keys = fresh_keys(call.args[0], agg, loops) if call.args else None
        if keys:
            fresh.setdefault(agg, set()).update(keys)
    if any(id(c) in row1_ids for c, *_ in mine):
        return "승인 구간 안 조회한 여럿을 한꺼번에 쓴다 — 예외 밖(#550 행 1)"
    locked_names = {t.id for st in w.body for n in ast.walk(st)
                    if isinstance(n, (ast.Assign, ast.AnnAssign)) and isinstance(n.value, ast.Call)
                    and isinstance(n.value.func, ast.Attribute) and "for_update" in n.value.func.attr
                    for t in (n.targets if isinstance(n, ast.Assign) else [n.target]) if isinstance(t, ast.Name)}
    for st in w.body:
        for loop in (n for n in ast.walk(st) if isinstance(n, (ast.For, ast.AsyncFor, ast.While))):
            body = {id(x) for b in loop.body for x in ast.walk(b)}
            literal = _literal_names(loop.iter) if isinstance(loop, (ast.For, ast.AsyncFor)) else None
            if literal and len(literal) >= 2 and all(x in locked_names for x in literal):
                continue  # 꼴 P 로 이미 잠근 것들을 도는 저장 고리 — 쓰기 차례는 묻지 않는다
            inner = [(c, a) for c, _r, _l, a in mine if id(c) in body]
            if literal and inner and all(is_fresh(c, a) for c, a in inner):
                continue  # 새로 만든 것만 쓰는 글자 고리(반복 변수는 원소로 가린다) — 새 행의 INSERT 는 남의 행을 잠그지 않는다(§4.1)
            if any(id(c) in body for c, *_ in mine) and not _sorted_literal_loop(loop):
                return ("승인 구간 안에서 쓰기를 감싼 고리는 잠금 정렬 고리(`for x in sorted((a, b), …)`) 하나뿐이다 — "
                        "조회한 여럿은 예외 밖이고, 다시 하는 고리는 `with` 바깥에 둔다(시도마다 새 트랜잭션)")
    mine_ids = {id(c) for c, *_ in mine}
    for st in w.body:
        for n in ast.walk(st):
            if not isinstance(n, TRY_NODES + (ast.With, ast.AsyncWith)) \
                    or not any(id(x) in mine_ids for b in n.body for x in ast.walk(b)):
                continue
            if isinstance(n, TRY_NODES) and (
                    any(not h.body or not isinstance(h.body[-1], ast.Raise) or _escapes(h.body) for h in n.handlers)
                    or _escapes(n.finalbody)):
                return M_SWALLOW
            if isinstance(n, (ast.With, ast.AsyncWith)) and any(
                    isinstance(i.context_expr, ast.Call) and getattr(i.context_expr.func, "id", getattr(i.context_expr.func, "attr", ""))
                    == "suppress" for i in n.items):
                return M_SWALLOW
    for call, *_ in mine:
        cur = call
        while cur in parents and cur is not w:
            cur = parents[cur]
            if isinstance(cur, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp, ast.Lambda)):
                return "승인 구간 안 쓰기를 컴프리헨션 · 람다 안에 둔다 — 승인 꼴(정렬 고리 · 차례 조회)로 쓴다"
    for call, _region, _loops, agg in mine:
        if call.func.attr in _bool_writes(root, bc, agg):
            par = parents.get(call)
            ok = isinstance(par, ast.UnaryOp) and isinstance(par.op, ast.Not) and isinstance(parents.get(par), ast.If) \
                and parents[par].test is par and parents[par].body and isinstance(parents[par].body[-1], ast.Raise) \
                and not _escapes(parents[par].body)
            if not ok and isinstance(par, (ast.Assign, ast.AnnAssign)) and par.value is call:
                target = par.targets[0] if isinstance(par, ast.Assign) and len(par.targets) == 1 else getattr(par, "target", None)
                owner = parents.get(par)
                seq = next((getattr(owner, f) for f in ("body", "orelse", "finalbody")
                            if isinstance(getattr(owner, f, None), list) and any(x is par for x in getattr(owner, f))), [])
                nxt = seq[seq.index(par) + 1] if par in seq and seq.index(par) + 1 < len(seq) else None
                ok = isinstance(target, ast.Name) and isinstance(nxt, ast.If) and isinstance(nxt.test, ast.UnaryOp) \
                    and isinstance(nxt.test.op, ast.Not) and isinstance(nxt.test.operand, ast.Name) \
                    and nxt.test.operand.id == target.id and nxt.body and isinstance(nxt.body[-1], ast.Raise) \
                    and not _escapes(nxt.body)
            if not ok:
                return (f"CAS 쓰기 `{call.func.attr}` 의 결과를 `if not …: raise` 로 받지 않는다(미스 몸에서 `continue` · "
                        "`break` · `return` 으로 나가는 길도 없어야 한다) — 둘째가 미스면 예외로 통째 되돌려야 한다(하나라도 실패하면 둘 다 그대로)")
    if len(types) < 2 and max(existing.values(), default=0) < 2:
        return ("덮을 함께 쓰기를 찾지 못했다 — 함께 쓰기가 없으면 표지를 지우고, 있으면 승인 꼴(같은 타입은 정렬 고리 · "
                "차례 조회 · 조회 이름 그대로)로 쓴다")
    if sum(existing.values()) < 2:
        return "이미 있는 애그리거트가 둘 이상이 아니다 — 예외 밖(새 기록은 그 하나가 품는다)"
    if types | {t for t, n in existing.items() if n} != set(row["aggs"]):
        return f"바꾸는 애그리거트 {sorted(types)} 가 승인 `함께` {sorted(row['aggs'])} 와 다르다"
    locked = {t for t, _ in row["lock"]}
    if {t for t, n in existing.items() if n} != locked:
        return f"이미 있는 것 {sorted(t for t, n in existing.items() if n)} 이 승인 `잠금` {sorted(locked)} 과 다르다"
    for t in sorted(types | set(existing)):
        e, k = existing.get(t, 0), len(fresh.get(t, ()))
        n, want = e + k, row["aggs"].get(t, 1)
        if (n >= 2) != (want >= 2) or n > want:
            return (f"`{t}` 바꾸는 것 {n} 개(이미 있는 것 {e} · 새 것 {k})가 표지 `{t}×{want}` 와 다르다 — `×n` 은 이미 있는 것과 "
                    "새로 만드는 것을 함께 센다")
    keys = dict(row["lock"])
    for t, n in existing.items():
        if n < 2:
            continue
        calls_fu = sorted(fu.get(t, []), key=lambda c: (c.lineno, c.col_offset))
        unpack = _sorted_unpack(fn, calls_fu[0].lineno) if calls_fu else None
        if len(calls_fu) >= 2 and unpack and [c.args[0].id if c.args and isinstance(c.args[0], ast.Name) else ""
                                               for c in calls_fu][:len(unpack)] == unpack:
            continue  # 꼴 P — `a, b = sorted(키들)` 차례로 잠그는 조회
        lockers = calls_fu or [c for c, _r, _l, agg in mine if agg == t and not is_fresh(c, agg)]
        loops_ok = []
        for c in lockers:
            cur, hit = c, None
            while cur in parents and cur is not w:
                cur = parents[cur]
                if _sorted_literal_loop(cur):
                    hit = cur.iter
                    break
            loops_ok.append(hit)
        if not all(loops_ok):
            return (f"같은 타입 `{t}` 여럿을 고정 차례로 잠근다 — `sorted((a, b), key=…)` 고리 안에서 쓰거나 "
                    f"`a, b = sorted(<키들>)` 차례로 `*_for_update` 조회한다(승인 잠금 `{t}({keys[t]})`)")
        if not all(_key_mentions(sl, keys[t]) for sl in loops_ok):
            return f"같은 타입 `{t}` 를 승인 잠금 키 `{keys[t]}` 와 다른 키로 정렬한다"
    first: dict[str, int] = {}
    for st in w.body:
        for n in ast.walk(st):
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and _receiver_agg(n, bindings) in keys \
                    and ("for_update" in n.func.attr
                         or (n.func.attr.split("_", 1)[0] in ("save", "remove") and not is_fresh(n, _receiver_agg(n, bindings)))):
                t = _receiver_agg(n, bindings)
                first[t] = min(first.get(t, n.lineno), n.lineno)
    order = [t for t, _ in row["lock"] if t in first]
    if [first[t] for t in order] != sorted(first[t] for t in order):
        return f"다른 타입을 승인 `잠금` 차례 {' → '.join(t for t, _ in row['lock'])} 와 다르게 처음 잠근다"
    return None


def _check_application_side(root: Path, bc: Path, f: Findings, cand: Candidates) -> None:
    app = bc / "application_layer"
    domain = bc / "domain_layer"
    if not app.is_dir():
        return
    event_classes: set[str] = set()
    if domain.is_dir():
        for py in [e for d in sorted(domain.iterdir()) if d.is_dir()
                   for e in folder_group.group_members(d / "event", "*.py", promotable=False)]:
            mod = _parse(py)
            event_classes |= {c.name for c in _public_classes(mod)} if mod else set()
    repo_area_use: dict[str, set[str]] = {}
    marked_keys: dict[tuple, str] = {}
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
        uc_key = checker_target.joint_use_case(py.relative_to(root).as_posix(), lambda r: (root / r).is_file())
        if uc_key is None:
            continue
        marks = checker_target.joint_marks(py.read_text(encoding="utf-8"))
        used_marks: set[int] = set()
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
            loaded_from_read: set[str] = set()
            reads = _read_assignments(fn)
            many = _many_read_names(fn, reads)
            flagged_550: set[int] = set()
            for n in _function_nodes(fn):
                if isinstance(n, ast.Assign) and isinstance(n.value, ast.Call) \
                        and isinstance(n.value.func, ast.Attribute):
                    head = n.value.func.attr.split("_", 1)[0]
                    if head in READ_HEADS and len(n.targets) == 1 \
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
                if agg and head in ("save", "remove") and n.args:
                    # #550 행 1(구간과 무관) — 조회로 꺼낸 «여럿»을 한 번의 쓰기에 넘긴다. 주석 없는 대입(옛 꼴)은 save_all 만.
                    hit = _many_argument(n.args[0], many)
                    pair = None if hit is not None else _literal_pair(n.args[0], reads, bindings)
                    if hit is None and pair is None and meth == "save_all" and isinstance(n.args[0], ast.Name) \
                            and n.args[0].id in loaded_from_read:
                        hit = n.args[0].id
                    if hit is not None or pair is not None:
                        flagged_550.add(id(n))
                        f.add("#550", _rel(root, py, n.lineno),
                              f"조회로 꺼낸 여럿(`{hit or pair}`)을 `{meth}` 로 한꺼번에 쓴다"
                              + ("(`save_all` 은 새로 만든 것만 받는다)" if pair is not None else "") + f" — {M550}")
                # #257 확정 — 리포지토리에서 나온 객체의 «속성 접근 후 메서드 호출».
                if isinstance(recv, ast.Attribute) and isinstance(recv.value, ast.Name) \
                        and recv.value.id in loaded_from_read:
                    f.add("#257", _rel(root, py, n.lineno),
                          f"`{recv.value.id}.{recv.attr}.{meth}(...)` — 애그리거트 상태 변경은 "
                          "전부 «루트를 지나야» 한다(내부에 손을 넣지 않는다)")
            regions, unknown_boundary, writes = _transaction_write_regions(root, py, mod, fn, cls_parent, bindings)
            excused: set[int] = set()
            parents_j = {child: parent for parent in _function_nodes(fn) for child in ast.iter_child_nodes(parent)}
            for w in [n for n in _function_nodes(fn) if isinstance(n, (ast.With, ast.AsyncWith))]:
                body = marks.get(w.lineno - 1)
                if body is None:
                    continue
                used_marks.add(w.lineno - 1)
                fields = checker_target.joint_fields(body)
                inv = fields.inv if fields is not None else " ".join(body.split())
                key = (*uc_key, inv)
                problem = _joint_verdict(root, bc.name, fn, w, fields, writes, reads, parents_j, bindings, flagged_550)
                if problem is None and key in marked_keys:
                    problem = f"같은 불변식 표지가 이 유스케이스에 둘(먼저 {marked_keys[key]}) — 승인 하나는 구간 하나만 덮는다"
                marked_keys.setdefault(key, _rel(root, py, w.lineno))
                if problem is not None:
                    f.add("#546", _rel(root, py, w.lineno), f"함께 커밋 표지 «{inv}» — {problem}")
                    continue
                inside = {id(x) for st in w.body for x in ast.walk(st)}
                excused |= {id(c) for c, *_ in writes if id(c) in inside}
            for line, message in _region_writes_550(
                    fn, writes, reads, flagged_550, bindings, excused,
                    params=lambda c: _read_params(root, bc.name, c, bindings),
                    cas=lambda c: _is_cas(root, bc.name, c, bindings)):
                f.add("#550", _rel(root, py, line), message)
            regions = {}
            for c, region, _l, agg in writes:
                regions.setdefault(region, set())
                if id(c) not in excused:
                    regions[region].add(agg)
            for region, written in regions.items():
                if region > 0 and len(written) >= 2:
                    f.add("#546", _rel(root, py, region),
                          f"명시 transaction 구간에서 서로 다른 애그리거트 리포지토리 {sorted(written)} 에 쓰기 둘(현행 타입 계수) — {M_JOINT}")
            all_written = set().union(*regions.values())
            if len(all_written) >= 2 and (unknown_boundary or regions.get(0) or regions.get(-1)):
                cand.add("#546", _rel(root, py, fn.lineno),
                         f"서로 다른 애그리거트 쓰기 {sorted(all_written)} 의 transaction 경계 불명 — 같은 트랜잭션인지 확인 필요",
                         "현재 함수의 lexical 구간 밖·불명 경계가 이 쓰기들을 묶는가")
        for number in sorted(set(marks) - used_marks):
            f.add("#546", _rel(root, py, number),
                  "함께 커밋 표지가 트랜잭션을 여는 `with` 바로 위에 있지 않다(떠 있는 표지) — 표지는 그 아래 `with` 하나만 덮는다")
    for agg, areas in sorted(repo_area_use.items()):
        if len(areas) >= 2:
            cand.add("#547", _rel(root, bc),
                     f"`{agg}_repository` 를 여러 <area>/ {sorted(areas)} 가 쓴다 — 경계가 "
                     "너무 묶였을 신호다(트랜잭션을 늘리지 말고 «경계를 쪼갠다»)",
                     "서로 다른 일을 하는 두 사용자가 이 경계로 충돌하나")
    # #547 후보 ⑶ — 비대한 루트.
    if domain.is_dir():
        for agg in _aggregate_dirs(domain):
            ents = [p for p in folder_group.group_members(agg / "entity", "*.py", promotable=False)
                    if p.stem != "__init__"]
            root_py = checker_target.slot_file(agg / f"{agg.name}.py")  # 승격이면 본체(#547 ⑶ 채널 복원)
            if len(ents) >= 3 and root_py is not None:
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
        if area.is_dir() and area.name not in ("port", "__pycache__") \
                and not checker_target.cache_only_instance(area):
            uc_names |= {d.name for d in area.iterdir() if d.is_dir() and d.name != "__pycache__"
                         and not checker_target.cache_only_instance(d)}
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
    bad_target_reason = checker_target.bc_shaped_target_reason(root)
    if bad_target_reason is not None:
        print(f"사용 오류: {bad_target_reason}", file=sys.stderr)
        return 1
    if not root.is_dir():
        print(f"사용 오류: 디렉터리가 아니다 — {root}", file=sys.stderr)
        return 1

    findings = Findings(defer=True)
    cand = Candidates(defer=True)
    bcs = [bc for bc in vocab.server_bc_dirs(root) if _has_adoption_signal(bc)]

    # 대상 0건 가드(#74) — touched 필터 없음이라 자리는 대상 집합 직후다(#75).
    if bcs and not any((bc / "domain_layer").is_dir() or (bc / "application_layer").is_dir()
                       for bc in bcs):
        guard = zero_target_guard(
            "blocker: 채택 신호는 있는데 domain_layer/application_layer 가 0건이다 — 조용한 무동작을 금지한다(#74)"
        )
        emit_all(guard, printer=print, indent="")
        return 2

    for bc in bcs:
        _check_layout(root, bc, findings, cand)
        _check_domain_wide(root, bc, bcs, findings)
        _check_application_side(root, bc, findings, cand)
        _check_cache_bypass(root, bc, findings)

    emit_all(cand, printer=print, indent="")
    if findings:
        print("blocker — 도메인 모델 위반 (루트를 지나고·값은 불변이고·한 트랜잭션 = 애그리거트 하나(예외: 새로 여럿 만들기 · G1 승인 함께 커밋) — D12·D13·D50)")
        emit_all(findings, printer=print, indent="  ")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
