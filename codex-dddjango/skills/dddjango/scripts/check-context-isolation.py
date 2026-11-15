#!/usr/bin/env python3
"""dddjango 컨텍스트 격리 검사기 — BC 경계·층 방향 규율의 결정적 백스톱.

check-layer-skeleton(존재·폐쇄)의 «의존 방향» 짝이다. 경로 기대는 `standard_tree.py`
에서 도출한다. 총론 #1(안쪽으로만)·#3(관문으로만)·#5(예외 조문 없음)·#49(Shared
Kernel 없음)·#83(BC 삭제 내성)은 아래 각론 진단이 집행한다.

무엇을 잡나 (규칙 번호는 트리 개정 명세):
  방향   #2 안쪽 두 칸은 구체 기술을 모른다 · #9 driven 은 domain·port 만
         #93/#94/#95 driving 잎의 import 폭 · #185/#186 application 의 import 폭
         #251 domain 으로 들어오는 화살표 · #288 도메인 리포지토리는 domain 안에서 안 부른다
         #312 판정 인터페이스의 층(구현이 domain 밖을 import 하나) · #322 driven 으로
         들어오는 화살표는 composition_root 뿐 · #328 django_<bc> 는 persistence 만
  타 BC  #12 부를 수 있는 것은 OHS·published_event 둘 · #13 OHS 소비는 ACL 뿐
         #98 타 BC composition_root 금지 · #102 driving 중 OHS 만 · #51 test→타 BC test 금지
         #664 `cross_context/**`(트리 172~182행)는 BC 의 `driving_layer/open_host_service/` 만 import 하고 모델 클래스 ·
         `get_model()` · 시험 밖 `get_user_model()` · 날 SQL 길(connection(s) · RawSQL · DB 드라이버 import · `.raw(` · `.extra(`)을 안 쓴다
         #665 application · framework · <project> 는 cross_context 를 import 하지 않는다(<project> 의 `cross_context.` 문자열은
         `include("cross_context.backoffice.urls")` 와 설정 모듈의 앱 문자열만) · #666 주소는 `cross_context/backoffice/urls.py` 에만 · 모두 `admin_view`
  admin  #668 `django_<bc>/admin/**` 는 자기 BC 의 domain · application · composition_root · persistence · ACL 을 import 하지 않는다
         (자기 `django_<bc>/` 모듈의 다시 내보내기 한 겹 포함 — 모듈 수준 이름 · 맨 위 클래스(모델 클래스 등) 안 별칭 · 꾸러미 `__init__.py` 가
         다시 내보낸 이름(`import *` 포함)은 그 모듈의 이름으로 풂(겹 아님) · VO 멤버의 `.value` 를 글 · 수 주석(`Final[str]` · `str` 등)으로
         묶은 값(모델 클래스 속성 · 모델 모듈 수준 이름)은 거쳐 가져오기가 아님 · `checker_target.reexport_uses` 를 #356 과
         같이 씀(2.39.0 F4-180) · 파일당 한 줄 · 걸린 import 는 푼 절대 경로를 정렬한 목록 칸 · 2026-11-14 F4-158) ·
         admin → 타 BC 는 다른 칸과 같은 타 BC 규칙(#12 · #13 · #98 · #102)
  OHS    #146 published_service 금지 · #149/#113 라우팅·등록 함수 금지 · #150 평면 .py 금지
         #152/#154/#155 service·contract 구조 · #156/#157/#159/#160 계약 1타입=1파일
         (주 계약이 어노테이션으로 참조하는 보조 공개 dataclass 는 면제 — 2026-08-24 좁은 정합화 ·
         대화 창구(공개 함수가 `Generator[<Op>Response, <답>]`)의 send 답 타입과 그 구성 dataclass 도
         요청 파일에서 면제 — 2026-10-26 · implementation-python §13.5 예외)
         #162 응답에 도메인 금지 · #163 exception 은 서비스 스코프 · #164 도메인 예외 번역
         #166/#167/#168/#170 기저 예외·상속·1클래스=1모듈·_v1 금지 · #453/#454 «없다»는 답
         #455 사유는 코드로 · #472 contract 는 stdlib·같은 BC 계약만 · #482/#483/#484 명명
         #633 인자는 request 하나 · #634 공개 표면은 함수만 · #295 raw 재노출 금지
  ACL    #361 상대 BC 하나=폴더 하나 · #363 클래스명 <Bc><Capability>Adapter
         #364 포트 파일명에 공급자 BC 금지 · #450 상호 ACL 금지 · #473 기저 예외를 잡는다
         (상대 창구 코드가 돌 수 있는 try 만 — 모르면 돈다고 본다 · 2026-10-26 · 받은 글 `model_validate_json`
         검증은 받는 쪽이 선언만 있는 wire · 값 자료만 받는 모델 짓기 함수 · 같은 BC 가 import 하지 않는 사설
         함수의 `type[T]` 일 때만 안 돈다고 본다 — `_WindowTry` · 2026-11-14 F4-167)
         (#151·#364 의 «타 BC 이름» = 같은 `application/` 컨테이너의 BC — 자매 플러그인
         `web/application/<단위>` 같은 다른 컨테이너의 폴더 이름은 세지 않는다)
  기타   #14 `with unit_of_work:` 안에서 크로스-BC 포트 호출 금지 · #110 auto_import=False
         #117 두 번째 ErrorCode 컨테이너 금지 · #291/#292 예외의 자리 넷 · #431 부작용 등록 금지
         (#292 는 이름(`exception.py` · `exception/`)에 더해 application 층 모듈 맨 위 예외 클래스도 본다 —
         사설 `_X` 는 BC 안 제품 모듈이 import 할 때만 · 같은 유스케이스 칸 승격 폴더 형제는 빼고 · 2026-11-10)

ast+ 후보 채널 (㉰ — exit 불산입, 마무리는 discipline-reviewer):
  #151(창구 이름 — 기술·타 BC 토큰은 «확정» 위반) · #153(도메인 예외 속성 접근은 «확정» — 잡은 도메인 예외의 공개 필드를
  `raise <자기 BC contract/exception 클래스>(kw=n.f) [from None]` 한 문장으로 옮기는 꼴(설계에서 승인한 사건 값 · F4-105)만
  비켜 준다 · 판정은 `checker_target.ohs_event_value_handler` 가 #474 와 함께 진다 · 프로필 무관,
  출처가 확인된 usecase 실행 수가 1이 아니거나 출처·반복 횟수가 미해소이면 후보;
  builder 준비·미호출 nested 정의는 실행 수에 불산입) · #171(접미사뿐인 예외 이름) · #347(admin feature 의
  애그리거트 쓰기 — 확정 몫은 #668) · #11(경계 애너테이션의 Model/QuerySet 은 «확정», 그 외 후보)

  framework #470 강등의 사후 신호 — 공개 시그니처에 `kind`·`mode`·`bc`·`is_*` 매개변수(D38)
  <project> #433 규칙을 «주소·예외 목록»으로 적지 않는다 — BC 경로 리터럴 컬렉션
         (INSTALLED_APPS 등록은 제외)·도메인 예외 이름 컬렉션

CLI 호환 심: registry 가 렌더하는 `--error-profile`·selector 들은 «수용하되 무시»한다 —
그 lane(API error contract)은 전용 검사기 4종의 소유가 됐고, 실행·종료 계약은 무변이다.

사용법: check-context-isolation.py [TARGET_DIR] [--error-profile …] [selector …]
종료코드: 0=clean(또는 표준 미채택) · 1=사용/분석 오류 · 2=blocker(발견 출력)
구조화 레코드: DJR_FINDINGS_JSON=<경로> 지정 시 findings.py(공용 모듈)가 JSON lines 를
추가 방출한다 — 라인 출력·exit 의미론 무변(T0 B2).

그래프 좌표(T2-2): 규범 정본 = 온톨로지 그래프(`ontology/rules/`) · 이 검사기의 #N ↔ Work 조인은
  alias 대장(`ontology/wiring/aliases.ttl`)이 소유한다. 조인 확정: rule#3 → djr:R-0124 · rule#74 → djr:R-3229 ·
  rule#432 → djr:R-3219.
  미확정 #N 은 T3 이관에서 해소한다(대장 28종 — T3 게이트 조항 처분 2026-08-22 ·
  판단표 v2 + `workspace/eval/t3/memos/`).
"""
from __future__ import annotations

import argparse
import ast
import builtins
import os
import re
import sys

import checker_target
from findings import Candidates, Findings, emit_all, zero_target_guard
from pathlib import Path

try:
    import anchor_diff
    import standard_tree as tree
    import business_vocab as vocab
except ImportError:  # 데이터 모듈 없이는 판정 불가 — fail-closed(분석 오류)
    print("분석 오류: standard_tree.py/business_vocab.py/anchor_diff.py 를 찾지 못했다 — 검사기와 같은 폴더에 있어야 한다", file=sys.stderr)
    sys.exit(1)

# #472 의 «표준 라이브러리» 판정 집합 — business_vocab 의 stdlib 축(배포판·기술 낱말 제외).
STDLIB_NAMES = set(getattr(sys, "stdlib_module_names", ())) | set(vocab.STDLIB_FALLBACK)

SKIP_DIRS = {".venv", "venv", "site-packages", "node_modules", ".git", "__pycache__", ".dddjango"}
DJANGO_APP_MARKERS = ("models.py", "apps.py", "views.py", "admin.py")
NEW_LAYERS = {"driving_layer", "application_layer", "domain_layer", "driven_layer"}

TECH_TOP = {
    "django", "ninja", "celery", "rest_framework", "redis", "kafka", "pika",
    "boto3", "requests", "httpx", "psycopg", "psycopg2", "sqlalchemy", "grpc",
}
TECH_NAME_TOKENS = {"django", "ninja", "celery", "http", "grpc", "kafka", "redis", "sql", "orm", "rest", "api"}
ANSWER_NOT_EXCEPTION = ("NotFound", "AlreadyExists", "AlreadyExist", "Duplicate", "Duplicated")
FREEFORM_FIELDS = {"message", "reason", "detail"}
IDENT_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


def _entries(d: Path) -> tuple[list[Path], list[Path]]:
    dirs: list[Path] = []
    files: list[Path] = []
    for p in sorted(d.iterdir()):
        if p.name.startswith(".") or p.name in SKIP_DIRS:
            continue
        (dirs if p.is_dir() else files).append(p)
    return dirs, files


def _has_adoption_signal(bc_dir: Path) -> bool:
    has_layer = any((bc_dir / n).is_dir() for n in NEW_LAYERS)
    has_marker = any((bc_dir / m).is_file() for m in DJANGO_APP_MARKERS) or any(
        p.is_dir() and p.name.startswith("django_") for p in bc_dir.iterdir()
    )
    return has_layer or has_marker


def _parse(f: Path) -> ast.Module | None:
    try:
        return ast.parse(f.read_text(encoding="utf-8"))
    except (SyntaxError, OSError, UnicodeDecodeError):
        return None


def _camel(snake: str) -> str:
    return "".join(w.capitalize() for w in snake.split("_"))


def _ann_idents(node: ast.expr | None) -> set[str]:
    if node is None:
        return set()
    out: set[str] = set()
    for n in ast.walk(node):
        if isinstance(n, ast.Name):
            out.add(n.id)
        elif isinstance(n, ast.Attribute):
            out.add(n.attr)
        elif isinstance(n, ast.Constant) and isinstance(n.value, str):
            out.update(IDENT_RE.findall(n.value))
    return out


# ── 칸 분류 — 파일 경로·모듈 경로 공용 ──────────────────────────────────────

def _spot(parts: tuple[str, ...]) -> str:
    if not parts:
        return "bc_root"
    segs = parts
    head = segs[0]
    if head == "driving_layer":
        sub = segs[1] if len(segs) > 1 else ""
        if sub == "open_host_service":
            return "ohs_contract" if "contract" in segs else "ohs"
        if sub in ("api", "cron_job", "event_subscription"):
            return sub
        return "driving"
    if head == "application_layer":
        if len(segs) > 1 and segs[1] == "port":
            return "app_port"
        return "app"
    if head == "domain_layer":
        if "value_object" in segs or "shared_value_object" in segs:
            return "domain_vo"
        if "exception" in {s.removesuffix(".py") for s in segs[1:]}:
            return "domain_exc"
        last = segs[-1].removesuffix(".py")
        if last.endswith("_repository"):
            return "domain_repo"
        if "domain_service" in segs:
            return "domain_service"
        return "domain"
    if head == "driven_layer":
        sub = segs[1] if len(segs) > 1 else ""
        if sub.startswith("django_"):
            return "django"
        if "anticorruption_layer" in segs:
            return "acl"
        if "persistence" in segs:
            return "persistence"
        return "driven"
    if head == "composition_root":
        return "composition"
    if head == "published_event":
        return "published_event"
    if head == "test":
        return "test"
    return "other"


DOMAIN_SPOTS = {"domain", "domain_vo", "domain_exc", "domain_repo", "domain_service"}
DRIVEN_SPOTS = {"driven", "django", "acl", "persistence"}
DRIVING_SPOTS = {"driving", "api", "ohs", "ohs_contract", "cron_job", "event_subscription"}


def _resolve_relative(file_parts: tuple[str, ...], level: int, module: str | None) -> tuple[str, ...] | None:
    """상대 import 를 BC-상대 마디로 해석. None = BC 밖으로 탈출(level 과다)."""
    pkg = list(file_parts[:-1])
    up = level - 1
    if up > len(pkg):
        return None
    base = pkg[: len(pkg) - up]
    if module:
        base.extend(module.split("."))
    return tuple(base)


def _imports(mod: ast.Module):
    for node in ast.walk(mod):
        if isinstance(node, ast.Import):
            for a in node.names:
                yield node, a.name, 0
        elif isinstance(node, ast.ImportFrom):
            yield node, node.module or "", node.level


# ── 방향 매트릭스 ───────────────────────────────────────────────────────────

def _orm_writer_exempt(file_parts: tuple) -> bool:
    """adapter/<capability>/django_adapter/adapter/ 구현 — #328 면제 (houserules §5 · R-3423).

    비애그리거트 ORM 쓰기 능력의 기술 구현(2호 실증·사용자 A안). 값은
    check-port-adapter-pairing 의 #462 면제와 동일하고 경로 기준만 BC 상대로 환산.
    """
    p = file_parts
    if (len(p) == 6 and p[:2] == ("driven_layer", "adapter")
            and p[2] not in ("persistence", "anticorruption_layer", "external_system")
            and p[3:5] == ("django_adapter", "adapter")
            and p[5].endswith("_adapter.py")):
        return True
    if (len(p) == 4 and p[0] == "driven_layer" and p[1] == "adapter"
            and p[2] not in ("anticorruption_layer", "external_system")
            and p[3] == "django_adapter.py"):
        return True
    # 동명 폴더 승격 — django_adapter.py 가 django_adapter/ 로 승격돼도 면제는 유지된다.
    if (len(p) == 5 and p[0] == "driven_layer" and p[1] == "adapter"
            and p[2] not in ("anticorruption_layer", "external_system")
            and p[3] == "django_adapter" and p[4] == "django_adapter.py"):
        return True
    return False


def _apply_same_bc(loc: str, tgt: str, rel, mod_path: str, out: Findings,
                   orm_writer: bool = False) -> None:
    if loc in ("api", "driving", "cron_job", "event_subscription"):
        if tgt == "app_port":
            out.add("#93", rel, f"driving 의 잎은 `application_layer/port/` 를 import 하지 않는다 — `{mod_path}`")
        elif tgt in DRIVEN_SPOTS:
            out.add("#94", rel, f"driving 의 잎은 `driven_layer/` 를 import 하지 않는다 — `{mod_path}`")
        elif tgt in ("domain", "domain_repo", "domain_service"):
            out.add("#95", rel, f"driving 잎이 domain 에서 가져올 수 있는 것은 exception·값 객체뿐이다 — `{mod_path}`")
    elif loc == "ohs":
        if tgt in DRIVEN_SPOTS:
            out.add("#94", rel, f"driving 의 잎은 `driven_layer/` 를 import 하지 않는다 — `{mod_path}`")
        elif tgt == "app_port":
            out.add("#93", rel, f"driving 의 잎은 `application_layer/port/` 를 import 하지 않는다 — `{mod_path}`")
        elif tgt in ("domain", "domain_repo", "domain_service"):
            out.add("#95", rel, f"driving 잎이 domain 에서 가져올 수 있는 것은 exception·값 객체뿐이다 — `{mod_path}`")
    elif loc == "ohs_contract":
        if tgt != "ohs_contract":  # 같은 BC 의 다른 계약 import 는 허용 문면이다
            out.add("#472", rel, f"`contract/` 는 표준 라이브러리와 같은 BC 의 다른 계약 말고는 import 하지 않는다 — `{mod_path}`")
    elif loc in ("app", "app_port"):
        if tgt in DRIVEN_SPOTS:
            out.add("#185", rel, f"`application_layer` 는 `driven_layer` 를 import 하지 않는다(#322 — driven 으로 들어오는 화살표는 composition_root 뿐) — `{mod_path}`")
        elif tgt in DRIVING_SPOTS:
            out.add("#185", rel, f"`application_layer` 는 `driving_layer` 를 import 하지 않는다 — `{mod_path}`")
    elif loc in DOMAIN_SPOTS:
        if tgt == "domain_repo":
            out.add("#288", rel, f"`<aggregate>_repository` 는 domain 안에서 아무도 import 하지 않는다 — `{mod_path}`")
        elif tgt not in DOMAIN_SPOTS:
            rule = "#312" if loc == "domain_service" else "#1"
            out.add(rule, rel, f"domain 은 밖을 모른다(의존은 안쪽으로만) — `{mod_path}`")
    elif loc in ("driven", "persistence", "acl"):
        if tgt in DRIVEN_SPOTS and tgt != "django":
            pass  # driven 내부 협력(persistence↔acl 등)은 이 검사기의 축이 아니다
        elif tgt == "django":
            if loc != "persistence" and not orm_writer:
                out.add("#328", rel, f"`django_<bc>` 를 import 하는 것은 `adapter/persistence/` 아래와 `adapter/<capability>/django_adapter/adapter/` 의 구현 파일뿐이다 — `{mod_path}`")
        elif tgt not in DOMAIN_SPOTS and tgt != "app_port":
            out.add("#9", rel, f"`driven_layer` 는 `domain_layer` 와 `application_layer/port/` 만 import 한다 — `{mod_path}`")
    elif loc == "published_event":
        if tgt in DOMAIN_SPOTS:
            out.add("#251", rel, f"`published_event` 는 domain 을 import 하지 않는다(domain 으로 들어오는 화살표 셋에 없다) — `{mod_path}`")


def _apply_other_bc(loc: str, tgt: str, tgt_bc: str, rel, mod_path: str, out: Findings) -> None:
    if tgt in ("ohs", "ohs_contract"):
        if loc == "acl":
            return
        if loc == "app":
            out.add("#186", rel, f"`application_layer` 는 타 BC 를 직접 부르지 않고 자기 `port/` 를 거친다 — `{mod_path}`")
        else:
            out.add("#13", rel, f"타 BC 의 `open_host_service/` 를 import 하는 것은 `anticorruption_layer/` 뿐이다 — `{mod_path}`")
        return
    if tgt == "published_event":
        return  # 사실 계약 소비 — 표준 경로(#12 의 둘째)
    if loc == "test":
        if tgt == "test":
            out.add("#51", rel, f"BC 테스트가 다른 BC 의 test 를 import 하면 위반이다 — `{mod_path}`")
        return  # 테스트의 그 밖 소비는 이 검사기가 확정하지 않는다
    if tgt == "composition":
        out.add("#98", rel, f"타 BC 의 `composition_root` 는 관문(OHS) 우회다 — `{mod_path}`")
    elif tgt in ("api", "driving", "cron_job", "event_subscription"):
        out.add("#102", rel, f"타 BC 는 driving 중 `open_host_service/` 아래만 import 한다 — `{mod_path}`")
    elif loc == "app":
        out.add("#186", rel, f"`application_layer` 는 타 BC 를 직접 부르지 않고 자기 `port/` 를 거친다 — `{mod_path}`")
    else:
        out.add("#12", rel, f"타 BC 에서 부를 수 있는 것은 OHS·published_event 둘이다(#83 — 이 import 는 BC 삭제 내성을 깬다) — `{mod_path}`")


def _import_target_names(target: Path) -> set[str]:
    """import 경로가 BC 를 가리키는지(#12 등) 가리는 이름 — 점으로 시작하는 마디 밖 모든 `application/` 컨테이너의 폴더 이름.

    검사 대상 BC 는 뿌리 `application/` 뿐이지만, 서버 BC 파일이 자매 플러그인 화면 구역(`web/application/<단위>`)을
    import 하는 것도 «타 BC» import 로 잡도록 이름은 저장소 전체에서 모은다. 점 폴더(기록 사본 `.dddjango-web/` 등)는
    G2 · pre-gate 사본에 없으므로 빼서 직접 실행과 같은 이름을 쓴다 — 점 폴더 · SKIP_DIRS 는 들어가기 전에 잘라 낸다.
    """
    names: set[str] = set()
    for dirpath, dirnames, _files in os.walk(target):
        dirnames[:] = [d for d in dirnames if not d.startswith(".") and d not in SKIP_DIRS]
        if "application" not in dirnames:
            continue
        c: Path = Path(dirpath) / "application"
        if set(c.parts) & SKIP_DIRS:
            continue
        names |= {p.name for p in c.iterdir() if p.is_dir() and not p.name.startswith(".")}
    return names


# ── admin — #668(2026-11-14 F4-158) ─────────────────────────────────────────

ADMIN_FORBIDDEN_SPOTS = DOMAIN_SPOTS | {"app", "app_port", "composition", "persistence", "acl"}
# #668 금지 자리 → 그 자리의 앞마디(별칭 없는 `import a.b.c` 씨앗 — `checker_target.plain_import_seed`) · 도메인 자리는 `domain_layer`.
_ADMIN_SPOT_ROOT: dict[str, str] = {"app": "application_layer", "app_port": "application_layer",
                                    "composition": "composition_root", "persistence": "persistence",
                                    "acl": "anticorruption_layer"}


def _admin_area(file_parts: tuple[str, ...]) -> bool:
    """BC 의 admin 구역 파일인가 — 표준 자리 `driven_layer/django_<bc>/admin/**` 와 옛 자리 `django_*/admin/**`."""
    if (len(file_parts) > 3 and file_parts[0] == "driven_layer"
            and file_parts[1].startswith("django_") and file_parts[2] == "admin"):
        return True
    return len(file_parts) > 2 and file_parts[0].startswith("django_") and file_parts[1] == "admin"


_own_target = checker_target.bc_import_target
_module_level = checker_target.module_level


def _admin_reexports(bc: Path, parts: tuple[str, ...],
                     cache: dict[tuple[str, ...], tuple[set[str], set[str]]]) -> tuple[set[str], set[str]]:
    """#668 다시 내보내기 한 겹 — 자기 `django_<bc>/` 모듈이 금지 자리 다섯에서 묶은 (모듈 수준 이름, `클래스.속성`).

    씨앗은 `from … import X [as Y]` · 모듈째 `import … as m`(별칭 없는 `import a.b.c` 는 그 금지 자리의 앞마디까지의 점
    경로 — `checker_target.plain_import_seed`) · 상대 import 다(`import *` 는 출처 모듈의 이름으로 편다 —
    `checker_target.star_names`). 별칭(모듈 수준 · 맨 위 클래스 몸)과 `.value` 파생 값(받음)의 판정은
    `checker_target.reexport_bindings` 가 #356 과 같이 진다. 그 모듈이 다른 `django_<bc>/` 모듈에서 가져온 이름은
    따라가지 않는다(한 겹).
    """
    if parts in cache:
        return cache[parts]
    cache[parts] = (set(), set())
    f = checker_target.bc_module_file(bc, parts)
    mod = _parse(f) if f is not None else None
    if mod is None:
        return cache[parts]
    file_parts = f.relative_to(bc).parts

    def seed_of(node: ast.Import | ast.ImportFrom) -> set[str]:
        seeds: set[str] = set()
        if isinstance(node, ast.ImportFrom):
            base = _own_target(file_parts, node.level, node.module, bc.name)
            if base is not None:
                for a in node.names:
                    if ADMIN_FORBIDDEN_SPOTS & {_spot(base), _spot(base + (a.name,))}:
                        seeds.add(a.asname or a.name)
                        if a.name == "*":
                            seeds |= checker_target.star_names(bc, base)
        else:
            for a in node.names:
                base = _own_target(file_parts, 0, a.name, bc.name)
                if base is not None and _spot(base) in ADMIN_FORBIDDEN_SPOTS:
                    seeds.add(a.asname or checker_target.plain_import_seed(
                        a.name, _ADMIN_SPOT_ROOT.get(_spot(base), "domain_layer")))
        return seeds

    cache[parts] = checker_target.reexport_bindings(mod, seed_of)
    return cache[parts]


def _scan_admin_imports(f: Path, file_parts: tuple[str, ...], bc: Path, bc_rel: Path, all_bcs: set[str],
                        out: Findings) -> None:
    """#668 — admin 은 자기 BC 의 domain · application · composition_root · persistence · ACL 을 import 하지 않는다.

    함수 안 · 상대 import · 그 BC 꾸러미에서 층 이름을 가져오는 꼴 · 자기 `django_<bc>/` 모듈의 다시 내보내기 한 겹
    (이름 · `import *` · 가져온 맨 위 클래스(모델 클래스 등) 안 별칭 · 모듈째 가져와 속성 사슬 · 꾸러미 `__init__.py` 가 다시 내보낸 이름 —
    `checker_target.reexport_uses` 를 #356 과 같이 씀) 포함. 줄은 파일당 하나 — 걸린 import 는 푼 절대 경로를
    정렬한 목록 칸이다(줄 번호 없음 · 상대 ↔ 절대 · 꾸러미 ↔ 모듈 · 차례만 바꾼 고침은 같은 줄). 자기 BC 의 `django_<bc>/` ·
    `open_host_service/`(창구) · `published_event/` 는 연다. 타 BC 는 다른 칸과 같은 타 BC 규칙(#12 · #13 · #98 · #102).
    """
    mod = _parse(f)
    if mod is None:
        return
    rel = bc_rel / f.relative_to(bc)
    prefix: tuple[str, ...] = bc_rel.parts
    hits: dict[str, None] = {}
    cache: dict[tuple[str, ...], tuple[set[str], set[str]]] = {}
    for node in ast.walk(mod):
        if isinstance(node, ast.Import):
            for a in node.names:
                parts = a.name.split(".")
                if "application" in parts:
                    i = parts.index("application")
                    if i + 1 < len(parts) and parts[i + 1] in all_bcs and parts[i + 1] != bc.name:
                        _apply_other_bc("django", _spot(tuple(parts[i + 2:])), parts[i + 1], rel, a.name, out)
                        continue
                tgt = _own_target(file_parts, 0, a.name, bc.name)
                if tgt is not None and _spot(tgt) in ADMIN_FORBIDDEN_SPOTS:
                    hits.setdefault(".".join(prefix + tgt))
        elif isinstance(node, ast.ImportFrom):
            if node.level > 0:
                base = _resolve_relative(file_parts, node.level, node.module or None)
                if base is None:
                    out.add("#12", rel, "상대 import 가 BC 밖으로 탈출한다 — 타 BC 는 관문으로만 부른다")
                    continue
            else:
                parts = (node.module or "").split(".")
                if "application" not in parts:
                    continue
                i = parts.index("application")
                if not (i + 1 < len(parts) and parts[i + 1] in all_bcs):
                    continue
                if parts[i + 1] != bc.name:
                    _apply_other_bc("django", _spot(tuple(parts[i + 2:])), parts[i + 1], rel, node.module or "", out)
                    continue
                base = tuple(parts[i + 2:])
            if _spot(base) in ADMIN_FORBIDDEN_SPOTS:
                hits.setdefault(".".join(prefix + base))
                continue
            for a in node.names:
                if _spot(base + (a.name,)) in ADMIN_FORBIDDEN_SPOTS:
                    hits.setdefault(".".join(prefix + base + (a.name,)))
    for _line, where, names, _imported in checker_target.reexport_uses(
            mod, bc, file_parts, lambda parts: _admin_reexports(bc, parts, cache)):
        hits.setdefault(".".join(prefix + where + names))
    if hits:
        out.add("#668", rel, "admin 은 자기 BC 의 `domain_layer/` · `application_layer/` · `composition_root/` · "
                "`adapter/persistence/` · `adapter/anticorruption_layer/` 를 import 하지 않는다(자기 `django_<bc>/` 모듈을 "
                "거쳐 다시 가져와도 같다) — 단순 자료는 ORM 값(모델 필드 · 모델의 속성 · 메서드)으로 읽고 쓰고(도메인 값 "
                "집합의 값으로 거르거나 견줄 때는 모델이 VO 멤버의 `.value` 를 `Final[str]` 로 묶은 값 속성 — "
                "implementation-django §2.5), DB 로 걸 수 없는 규칙이 있는 쓰기는 그 BC 창구(`driving_layer/open_host_service/`)를 "
                f"부른다 · 두 BC 이상의 값을 보이는 화면은 `cross_context/backoffice/` 다 — {sorted(hits)}")


def _scan_imports(f: Path, bc: Path, bc_rel: Path, all_bcs: set[str], out: Findings) -> None:
    file_parts = f.relative_to(bc).parts
    if _admin_area(file_parts):
        _scan_admin_imports(f, file_parts, bc, bc_rel, all_bcs, out)
        return
    loc = _spot(file_parts)
    if loc in ("django", "composition", "other", "bc_root"):
        return  # django 는 #326(check-db-table) 소유 · composition_root 는 전부를 안다
    mod = _parse(f)
    if mod is None:
        return
    rel = bc_rel / f.relative_to(bc)
    orm_writer = _orm_writer_exempt(file_parts)
    for node, mod_path, level in _imports(mod):
        if level > 0:
            target_parts = _resolve_relative(file_parts, level, mod_path or None)
            if target_parts is None:
                out.add("#12", rel, "상대 import 가 BC 밖으로 탈출한다 — 타 BC 는 관문으로만 부른다")
                continue
            _apply_same_bc(loc, _spot(target_parts), rel, "." * level + mod_path, out, orm_writer)
            continue
        parts = mod_path.split(".")
        if "application" in parts:
            i = parts.index("application")
            if i + 1 < len(parts) and parts[i + 1] in all_bcs:
                tgt_bc = parts[i + 1]
                tgt = _spot(tuple(parts[i + 2:]))
                if tgt_bc == bc.name:
                    _apply_same_bc(loc, tgt, rel, mod_path, out, orm_writer)
                else:
                    _apply_other_bc(loc, tgt, tgt_bc, rel, mod_path, out)
                continue
        if loc == "ohs_contract" and parts[0] not in STDLIB_NAMES and parts[0] != "application":
            out.add("#472", rel, f"`contract/` 는 표준 라이브러리와 같은 BC 의 다른 계약 말고는 import 하지 않는다 — `{mod_path}`")
            continue
        if parts[0] in TECH_TOP and loc in (DOMAIN_SPOTS | {"app", "app_port"}):
            out.add("#2", rel, f"안쪽 두 칸(domain·application)은 구체 기술을 모른다(#5 — 예외 조문은 없다, 전부 port 뒤로) — `{mod_path}`")


# ── OHS — #146~#171 · #453~#455 · #482~#484 · #633 · #634 · #295 ───────────

def _domain_imported_names(mod: ast.Module) -> set[str]:
    """domain_layer 에서 import 된 이름(도메인 예외 raw 전파 판정용)."""
    names: set[str] = set()
    for node in ast.walk(mod):
        if isinstance(node, ast.ImportFrom) and node.module and "domain_layer" in node.module.split("."):
            names.update(a.asname or a.name for a in node.names)
    return names


def _check_ohs(ohs: Path, bc: Path, bc_rel: Path, agg_names: set[str], container_bcs: set[str],
               out: Findings, cand: Candidates, root: "Path | None" = None) -> None:
    rel0 = bc_rel / ohs.relative_to(bc)
    dirs, files = _entries(ohs)
    for f in files:
        if f.name != "__init__.py":
            out.add("#150", rel0 / f.name, "`open_host_service/` 의 1차 축은 `<service>/` 폴더다 — 평면 `.py` 를 두지 않는다")

    for svc in dirs:
        if checker_target.cache_only_instance(svc):
            continue
        srel = rel0 / svc.name
        tokens = set(svc.name.split("_"))
        if tokens & TECH_NAME_TOKENS or tokens & (container_bcs - {bc.name}):
            out.add("#151", srel, "창구 이름은 「무엇을 해 주는가」로 짓는다 — 기술·타 BC 이름 토큰이 들어 있다")
        elif svc.name.removesuffix("_service") in agg_names or svc.name in agg_names:
            cand.add("#151", srel, f"창구 이름 `{svc.name}` 이 애그리거트 이름과 같다", "Q1(이 이름이 «무엇을 해 주는가»를 말하나)")

        entry_name = f"{svc.name}_service.py"
        # 진입점 칸은 동명 폴더 승격 가능 — entry 는 실현(파일 또는 `<svc>_service/` 본체)이다.
        entry = checker_target.slot_file(svc / entry_name)
        if entry is None:
            out.add("#152", srel / entry_name, f"창구의 진입점은 `{svc.name}_service.py` 하나다 — 부재")
        sdirs, sfiles = _entries(svc)
        for p in sdirs:
            if p.name == f"{svc.name}_service" and (p / entry_name).is_file():
                continue  # 본체 실존하는 승격 폴더 — 진입점 칸의 실현이다
            if p.name != "contract":
                out.add("#154", srel / p.name, "`<service>/` 안은 `<service>_service.py` 와 `contract/` 둘로 구성한다")
        for p in sfiles:
            if p.name not in (entry_name, "__init__.py"):
                out.add("#154", srel / p.name, "`<service>/` 안은 `<service>_service.py` 와 `contract/` 둘로 구성한다")

        ops: set[str] = set()
        sends: "dict[str, set[str]]" = {}
        if entry is not None:
            ops = _check_ohs_service(entry, srel / entry.relative_to(svc), out, cand, root, bc.name)
            sends = _window_send_types(entry)

        contract = svc / "contract"
        if contract.is_dir():
            cdirs, cfiles = _entries(contract)
            for p in cdirs:
                if p.name not in ("request", "response", "exception"):
                    out.add("#155", srel / "contract" / p.name, "`contract/` 는 `request/`·`response/`·`exception/` 셋으로 갈린다(#163 — exception 은 연산 축이 아니라 서비스 스코프다)")
            for p in cfiles:
                if p.name != "__init__.py":
                    out.add("#155", srel / "contract" / p.name, "`contract/` 직계에 평면 파일을 두지 않는다")
            _check_contract_kind(contract / "request", "Request", "#157", "#156", ops, srel, out, sends)
            _check_contract_kind(contract / "response", "Response", "#160", "#159", ops, srel, out)
            _check_published_exceptions(contract / "exception", svc.name, srel, out, cand)


_ALIAS_DEPTH = 8


def _module_type_aliases(mod: ast.Module) -> "dict[str, ast.expr]":
    """모듈 수준 별칭 세 꼴 — PEP 695 `type X = …` · `X: TypeAlias = …` · 맨 대입 `X = A | B` / `X = G[…]`.
    대화 창구 send 답 해소 전용이다(맨 대입 단일 이름 `X = Y` 는 상수와 갈리지 않아 풀지 않는다 · 제네릭 별칭은 대상 밖)."""
    out: "dict[str, ast.expr]" = {}
    for n in mod.body:
        if isinstance(n, ast.TypeAlias) and isinstance(n.name, ast.Name) and not n.type_params:
            out[n.name.id] = n.value
        elif (isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name) and n.value is not None
              and "TypeAlias" in _ann_idents(n.annotation)):
            out[n.target.id] = n.value
        elif (isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name)
              and isinstance(n.value, (ast.BinOp, ast.Subscript))):
            out[n.targets[0].id] = n.value
    return out


def _unquote(e: "ast.expr | None") -> "ast.expr | None":
    """문자열 어노테이션은 식으로 파싱한다(못 읽으면 None — 파서 깊이 넘침 포함)."""
    if isinstance(e, ast.Constant) and isinstance(e.value, str):
        try:
            return ast.parse(e.value, mode="eval").body
        except (SyntaxError, ValueError, MemoryError, RecursionError):
            return None
    return e


def _alias_names(names: "set[str]", aliases: "dict[str, ast.expr]", renamed: "dict[str, str]") -> set[str]:
    """이름들을 별칭 고정점까지 풀어 구성 이름으로 — `import … as` 별명은 원래 이름으로 되돌린다(순환은 seen 이 멈춘다)."""
    out: set[str] = set()
    seen: set[str] = set()
    queue: "list[str]" = sorted(names)
    while queue:
        raw: str = queue.pop()
        name: str = renamed.get(raw, raw)
        if name in seen:
            continue
        seen.add(name)
        if name in aliases:
            queue.extend(_ann_idents(_unquote(aliases[name])))
        else:
            out.add(name)
    return out


def _window_send_types(entry: Path) -> "dict[str, set[str]]":
    """대화 창구의 연산별 send 답 이름 — 공개 함수가 `Generator[<Op>Response, <답>, …]` 을 돌려주면 둘째 인자 <답> 의 이름
    (F4-123 · 2026-10-26 · implementation-python §13.5 예외). 진입 파일 별칭은 반환 머리와 답 둘 다 고정점까지 풀고 `import … as`
    별명은 원래 이름으로 되돌린다. `AsyncGenerator` · `Iterator` 는 대상 밖. 연산 이름은 `_check_ohs_service` 의 ops 와 같은 규칙."""
    mod = _parse(entry)
    out: "dict[str, set[str]]" = {}
    if mod is None:
        return out
    aliases = _module_type_aliases(mod)
    renamed: "dict[str, str]" = {}
    for n in mod.body:
        if isinstance(n, ast.ImportFrom):
            for a in n.names:
                if a.asname:
                    renamed[a.asname] = a.name

    def original(name: str) -> str:
        return renamed.get(name, name)

    for fn in mod.body:
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)) or fn.name.startswith("_"):
            continue
        ret = _unquote(fn.returns)
        seen: set[str] = set()
        for _ in range(_ALIAS_DEPTH):
            if isinstance(ret, ast.Name) and original(ret.id) in aliases and original(ret.id) not in seen:
                seen.add(original(ret.id))
                ret = _unquote(aliases[original(ret.id)])
            else:
                break
        if not isinstance(ret, ast.Subscript):
            continue
        head = ret.value
        head_name = head.id if isinstance(head, ast.Name) else head.attr if isinstance(head, ast.Attribute) else ""
        if original(head_name) != "Generator" or not isinstance(ret.slice, ast.Tuple) or len(ret.slice.elts) < 2:
            continue
        op = fn.name.removesuffix("_command") if fn.name.endswith("_command") else fn.name.removesuffix("_query")
        out.setdefault(op, set()).update(_alias_names(_ann_idents(_unquote(ret.slice.elts[1])), aliases, renamed))
    return out


def _ohs_execution_count(entry: Path, mod: ast.Module, fn: ast.AST) -> tuple[int, bool]:
    """현재 함수의 정적 execute 수. builder 준비와 미호출 내부 정의는 세지 않는다."""
    root = next((p.parent for p in entry.parents if p.name == "application"), entry.parent)

    def imports(body, source):
        result = {}
        for st in body:
            if isinstance(st, ast.Import):
                for a in st.names:
                    result[a.asname or a.name.split(".")[0]] = a.name if a.asname else a.name.split(".")[0]
            elif isinstance(st, ast.ImportFrom):
                module = st.module or ""
                if st.level:
                    parts = source.relative_to(root).with_suffix("").parts[:-1]
                    module = ".".join((*parts[:len(parts) - st.level + 1], *module.split(".")))
                for a in st.names:
                    result[a.asname or a.name] = module + "." + a.name
            elif isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                result.pop(st.name, None)
            elif isinstance(st, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
                for t in st.targets if isinstance(st, ast.Assign) else [st.target]:
                    for n in ast.walk(t):
                        if isinstance(n, ast.Name):
                            result.pop(n.id, None)
        return result

    def address(expr, env):
        if isinstance(expr, ast.Constant) and isinstance(expr.value, str):
            try:
                return address(ast.parse(expr.value, mode="eval").body, env)
            except SyntaxError:
                return ""
        if isinstance(expr, ast.Name):
            return env.get(expr.id, "")
        if isinstance(expr, ast.Attribute):
            base = address(expr.value, env)
            return base + "." + expr.attr if base else ""
        return ""

    def usecase(name):
        parts = name.split(".")
        if not ("application_layer" in parts and len(parts) > 1 and parts[-2].endswith("_use_case")):
            return False
        source = root.joinpath(*parts[:-1]).with_suffix(".py")
        declaration = _parse(source) if source.is_file() else None
        return declaration is not None and any(isinstance(st, ast.ClassDef) and st.name == parts[-1] for st in declaration.body)

    def builder(name):
        parts = name.split(".")
        if "composition_root" not in parts or not re.fullmatch(r"build_.+_use_case", parts[-1]):
            return False
        source = root.joinpath(*parts[:-1]).with_suffix(".py")
        if not source.is_file():
            source = root.joinpath(*parts[:-1], "__init__.py")
        declaration = _parse(source)
        if declaration is None:
            return False
        env = imports(declaration.body, source)
        target = next((st for st in declaration.body if isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef)) and st.name == parts[-1]), None)
        if target is None:
            return False
        if usecase(address(target.returns, env)):
            return True
        return any(isinstance(st, ast.Return) and isinstance(st.value, ast.Call)
                   and usecase(address(st.value.func, env)) for st in target.body)

    def origin(expr, env):
        if isinstance(expr, ast.Call):
            name = address(expr.func, env)
            return "@usecase" if usecase(name) or builder(name) else ""
        return address(expr, env)

    count, unknown = 0, False

    def inspect(expr, env):
        nonlocal count, unknown
        if isinstance(expr, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)):
            return
        if isinstance(expr, ast.Call) and isinstance(expr.func, ast.Attribute) and expr.func.attr == "execute":
            receiver = origin(expr.func.value, env)
            if receiver == "@usecase" or usecase(receiver):
                count += 1
            else:
                unknown = True
        before = count
        for child in ast.iter_child_nodes(expr):
            inspect(child, env)
        if isinstance(expr, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)) and count != before:
            unknown = True

    def block(body, env):
        nonlocal unknown
        for st in body:
            if isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                env[st.name] = ""
                continue
            if isinstance(st, (ast.If, ast.For, ast.AsyncFor, ast.While, ast.Try, ast.With, ast.AsyncWith)):
                branches = []
                if isinstance(st, (ast.With, ast.AsyncWith)):
                    for item in st.items:
                        inspect(item.context_expr, env)
                    branch = dict(env)
                    for item in st.items:
                        if item.optional_vars:
                            for n in ast.walk(item.optional_vars):
                                if isinstance(n, ast.Name): branch[n.id] = ""
                    block(st.body, branch)
                    branches = [branch, env]
                else:
                    condition_before = count
                    for field in ("test", "iter"):
                        value = getattr(st, field, None)
                        if value is not None: inspect(value, env)
                    if isinstance(st, ast.While) and count != condition_before:
                        unknown = True
                    branch = dict(env)
                    if isinstance(st, (ast.For, ast.AsyncFor)):
                        for n in ast.walk(st.target):
                            if isinstance(n, ast.Name): branch[n.id] = ""
                    before = count
                    block(st.body, branch)
                    if isinstance(st, (ast.For, ast.AsyncFor, ast.While)) and count != before:
                        unknown = True
                    other = dict(env)
                    block(st.orelse, other)
                    branches = [branch, other]
                    if isinstance(st, ast.Try):
                        for handler in st.handlers:
                            branch = dict(env)
                            if handler.name: branch[handler.name] = ""
                            block(handler.body, branch)
                            branches.append(branch)
                for key in set().union(*(b.keys() for b in branches)):
                    values = {b.get(key, "") for b in branches}
                    env[key] = values.pop() if len(values) == 1 else ""
                if isinstance(st, ast.Try): block(st.finalbody, env)
                continue
            inspect(st, env)
            if isinstance(st, (ast.Import, ast.ImportFrom)):
                env.update(imports([st], entry))
            elif isinstance(st, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
                value = origin(st.value, env) if not isinstance(st, ast.AugAssign) else ""
                for t in st.targets if isinstance(st, ast.Assign) else [st.target]:
                    for n in ast.walk(t):
                        if isinstance(n, ast.Name): env[n.id] = value if isinstance(t, ast.Name) else ""
        return env

    env = imports(mod.body, entry)
    for arg in (*fn.args.posonlyargs, *fn.args.args, *fn.args.kwonlyargs):
        name = address(arg.annotation, env)
        env[arg.arg] = "@usecase" if usecase(name) else ""
    block(fn.body, env)
    return count, unknown


def _check_ohs_service(entry: Path, rel, out: Findings, cand: Candidates,
                       root: "Path | None" = None, own_bc: str = "") -> set[str]:
    mod = _parse(entry)
    if mod is None:
        return set()
    domain_names = _domain_imported_names(mod)
    ops: set[str] = set()
    for node in mod.body:
        if isinstance(node, ast.ClassDef) and not node.name.startswith("_"):
            out.add("#634", rel, f"`<service>_service.py` 의 공개 표면은 모듈 수준 «함수»뿐이다 — `{node.name}` (계약 클래스는 `contract/` 에 산다)")
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == "__all__":
                    exported = {e.value for e in ast.walk(node.value) if isinstance(e, ast.Constant) and isinstance(e.value, str)}
                    for nm in sorted(exported & domain_names):
                        out.add("#295", rel, f"도메인 예외를 `__all__` 로 재노출하지 않는다 — `{nm}`")
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) or node.name.startswith("_"):
            continue
        fn = node
        if fn.name.endswith("_command"):
            ops.add(fn.name.removesuffix("_command"))
        elif fn.name.endswith("_query"):
            ops.add(fn.name.removesuffix("_query"))
        else:
            out.add("#482", rel, f"창구 공개 함수 이름은 `_command`/`_query` 로 끝난다 — `{fn.name}`")
            ops.add(fn.name)
        n_params = len(fn.args.posonlyargs) + len(fn.args.args) + len(fn.args.kwonlyargs)
        if n_params == 0:
            if fn.name.endswith("_command"):
                out.add("#633", rel, f"인자 0개는 입력 없는 `_query` 만 허용한다 — `{fn.name}`")
        elif n_params > 1 or fn.args.vararg or fn.args.kwarg:
            out.add("#633", rel, f"창구 공개 함수는 그 연산의 request 계약 «하나»만 받는다 — `{fn.name}`")
        else:
            only = (fn.args.posonlyargs + fn.args.args + fn.args.kwonlyargs)[0]
            if only.annotation is not None and not any(i.endswith("Request") for i in _ann_idents(only.annotation)):
                out.add("#633", rel, f"맨 스칼라 인자는 위반이다 — `{fn.name}` 은 request 계약을 받는다")
        for sub in ast.walk(fn):
            if isinstance(sub, ast.Raise) and sub.exc is not None:
                exc_name = None
                target = sub.exc.func if isinstance(sub.exc, ast.Call) else sub.exc
                if isinstance(target, ast.Name):
                    exc_name = target.id
                if exc_name in domain_names:
                    out.add("#164", rel, f"도메인 예외를 raw 로 전파하지 않는다 — `{exc_name}` 은 `contract/exception/` 타입으로 번역해 던진다(#295)")
            if isinstance(sub, ast.ExceptHandler) and sub.name:
                handler_types = _ann_idents(sub.type)
                if handler_types & domain_names and not (
                    root is not None and checker_target.ohs_event_value_handler(sub, mod, root, own_bc)
                ):
                    for inner in ast.walk(sub):
                        if isinstance(inner, ast.Attribute) and isinstance(inner.value, ast.Name) and inner.value.id == sub.name:
                            out.add("#153", rel, f"도메인 예외는 «타입»으로만 쓴다 — `{sub.name}.{inner.attr}` 속성 접근은 계약이 도메인 모양에 얹힌 것이다" + checker_target.OHS_EVENT_VALUE_FORM_NOTE)
                            break
        exec_calls, unknown_execution = _ohs_execution_count(entry, mod, fn)
        if exec_calls != 1 or unknown_execution:
            cand.add("#153", f"{rel}:{fn.lineno}", f"`{fn.name}` 의 확인된 유스케이스 실행 {exec_calls}회 — 실행 횟수/출처 확인 필요", "「이 문장이 «계약↔응용 DTO 변환»인가」")
        for d in fn.decorator_list:
            ids = _ann_idents(d)
            # 라우팅·등록 데코레이터만 문다 — 호출형 데코레이터 일반(@lru_cache(...) 류)은 #149 의 대상이 아니다.
            if ids & {"route", "router", "api_controller", "register"} or (
                ids & {"get", "post", "put", "patch", "delete", "head", "options"} and ids & {"api", "router", "app"}
            ):
                out.add("#149", rel, f"OHS 는 같은 프로세스 함수 호출이다 — 라우팅·등록을 두지 않는다(#113) — `{fn.name}`")
                break
    return ops


# 계약 어휘 접미 — 보조 타입 면제 불가 이름(#484 «Result 금지»·R-0531 어휘 혼용 금지)
_CONTRACT_VOCAB_SUFFIXES = ("Response", "Request", "Result", "Command", "Query")


def _dataclass_local_names(mod: ast.Module) -> set[str]:
    """`from dataclasses import dataclass(as 별칭)` 로 실제 들여온 이름만 — 이름만 같은
    로컬 데코레이터를 dataclass 로 치지 않는다(혼성 패널 Y#8 — _enum_local_names 동형)."""
    names: set[str] = set()
    for n in mod.body:
        if isinstance(n, ast.ImportFrom) and n.module == "dataclasses":
            for a in n.names:
                if a.name == "dataclass":
                    names.add(a.asname or a.name)
    return names


def _dataclass_module_aliases(mod: ast.Module) -> set[str]:
    names: set[str] = set()
    for n in mod.body:
        if isinstance(n, ast.Import):
            for a in n.names:
                if a.name == "dataclasses":
                    names.add(a.asname or "dataclasses")
    return names


def _is_dataclass_def(cls: ast.ClassDef, local: set[str], mods: set[str]) -> bool:
    for d in cls.decorator_list:
        target = d.func if isinstance(d, ast.Call) else d
        if isinstance(target, ast.Name) and target.id in local:
            return True
        if (isinstance(target, ast.Attribute) and target.attr == "dataclass"
                and isinstance(target.value, ast.Name) and target.value.id in mods):
            return True
    return False


def _contract_aux_exempt(mod: ast.Module, pubs: "list[ast.ClassDef]", suffix: str,
                         extra_seeds: "set[str] | None" = None) -> set[str]:
    """주 계약(`<Operation><suffix>`)의 필드 어노테이션이 직·간접 참조하는 같은 파일의
    보조 공개 dataclass — 1타입=1파일·접미 강제의 면제 집합(2026-08-24 좁은 정합화).
    자격 셋 전부: ① 주 계약에서 전이 참조(인용 forward-ref 포함 — _ann_idents) ② 계약
    어휘 접미 아님 ③ import 검증된 @dataclass. 고정점 순회라 자기·상호 참조에 안전하다.
    참조가 모듈 내 `type` 별칭(PEP 695)을 경유하면 별칭을 해소해 구성 클래스까지
    따라간다(중첩 별칭 포함 — 판정 ⑦ 2026-08-25 · seen 가드라 순환에도 안전).
    두 연산이 한 보조 타입을 공유하면 정의는 한 계약 파일에 두고 다른 계약이 같은 BC
    계약 간 import(#472 허용)로 참조한다 — 파일별 중복 정의는 같은 지식 두 벌이다.
    `extra_seeds` 는 대화 창구의 send 답 구성 이름(2026-10-26) — 주 계약 필드 참조와 같은 길로 자격을 본다."""
    local: set[str] = _dataclass_local_names(mod)
    mods: set[str] = _dataclass_module_aliases(mod)
    by_name: dict[str, ast.ClassDef] = {c.name: c for c in pubs}
    aliases: "dict[str, set[str]]" = {
        n.name.id: _ann_idents(n.value)
        for n in mod.body
        if isinstance(n, ast.TypeAlias) and isinstance(n.name, ast.Name)
    }

    def field_refs(cls: ast.ClassDef) -> set[str]:
        refs: set[str] = set()
        for s in cls.body:
            if isinstance(s, ast.AnnAssign):
                refs |= _ann_idents(s.annotation)
        return refs

    exempt: set[str] = set()
    primaries = [c for c in pubs if c.name.endswith(suffix)]
    seen: set[str] = {c.name for c in primaries}
    queue: "list[str]" = [name for c in primaries for name in field_refs(c)] + sorted(extra_seeds or ())
    while queue:
        name = queue.pop()
        if name in seen:
            continue
        seen.add(name)
        if name in aliases:  # PEP 695 별칭 — 구성 이름으로 해소(중첩은 이 순회가 잇는다)
            queue.extend(aliases[name])
            continue
        cand = by_name.get(name)
        if cand is None:
            continue
        if (not name.endswith(_CONTRACT_VOCAB_SUFFIXES)
                and _is_dataclass_def(cand, local, mods)):
            exempt.add(name)
            queue.extend(field_refs(cand))
    return exempt


def _check_contract_kind(kind_dir: Path, suffix: str, one_file_rule: str, only_rule: str,
                         ops: set[str], srel, out: Findings, sends: "dict[str, set[str]] | None" = None) -> None:
    if not kind_dir.is_dir():
        return
    kname = kind_dir.name
    for f in sorted(kind_dir.glob("*.py")):
        if f.name == "__init__.py":
            continue
        rel = srel / "contract" / kname / f.name
        stem = f.stem
        expected_tail = f"_{kname}"
        if stem.endswith(expected_tail):
            op = stem.removesuffix(expected_tail)
            if ops and op not in ops:
                out.add("#483", rel, f"계약 파일은 창구 함수와 짝이다 — `{op}` 연산 함수가 `<service>_service.py` 에 없다")
        mod = _parse(f)
        if mod is None:
            continue
        pubs = [n for n in mod.body if isinstance(n, ast.ClassDef) and not n.name.startswith("_")]
        send_names: set[str] = (sends or {}).get(stem.removesuffix(expected_tail), set()) if stem.endswith(expected_tail) else set()
        seeds: set[str] = _alias_names(send_names, _module_type_aliases(mod), {}) if send_names else set()
        exempt: set[str] = _contract_aux_exempt(mod, pubs, suffix, seeds)
        primaries = [c for c in pubs if c.name.endswith(suffix)]
        surplus = [c for c in pubs if not c.name.endswith(suffix) and c.name not in exempt]
        if len(pubs) >= 2 and (len(primaries) >= 2 or surplus):
            send_clause: str = " · 대화 창구의 send 답 타입과 그 구성 dataclass" if suffix == "Request" else ""
            out.add(one_file_rule, rel, f"계약 타입 하나 = 파일 하나다 — 공개 클래스가 {len(pubs)}개다(주 계약이 어노테이션으로 참조하는 보조 dataclass{send_clause} 만 예외)")
        for cls in pubs:
            if not cls.name.endswith(suffix) and cls.name not in exempt:
                out.add("#484", rel, f"계약 클래스는 `<Operation>{suffix}` 다(`Result` 금지 — {only_rule}: 이 폴더에는 이 창구가 {'받는' if suffix == 'Request' else '돌려주는'} 타입과 그 구성 보조 dataclass 만 온다) — `{cls.name}`")
            if suffix == "Response" and cls.name.endswith(suffix):
                field_names = {
                    s.target.id for s in cls.body
                    if isinstance(s, ast.AnnAssign) and isinstance(s.target, ast.Name)
                }
                if field_names & FREEFORM_FIELDS and "code" not in field_names:
                    out.add("#455", rel, f"못 해 준 사유는 «코드»로 담는다 — 자유 문자열({', '.join(sorted(field_names & FREEFORM_FIELDS))})만 있고 `code` 가 없다")
        for node, mod_path, level in _imports(mod):
            if level == 0 and "domain_layer" in mod_path.split("."):
                if kname == "response":
                    out.add("#162", rel, f"응답 계약에 도메인 객체를 그대로 담지 않는다 — `{mod_path}`")


def _check_published_exceptions(exc_dir: Path, svc_name: str, srel, out: Findings, cand: Candidates) -> None:
    if not exc_dir.is_dir():
        return
    base_file = exc_dir / f"{svc_name}_published_error.py"
    py_files = [f for f in sorted(exc_dir.glob("*.py")) if f.name != "__init__.py"]
    if py_files and not base_file.is_file():
        out.add("#166", srel / "contract" / "exception" / base_file.name, f"서비스당 기저 예외 하나를 `{base_file.name}` 에 둔다 — 부재")
    base_classes: set[str] = set()
    bmod = _parse(base_file) if base_file.is_file() else None
    if bmod is not None:
        base_classes = {n.name for n in bmod.body if isinstance(n, ast.ClassDef)}
    sibling_classes: set[str] = set()
    parsed: list[tuple[Path, ast.Module]] = []
    for f in py_files:
        mod = _parse(f)
        if mod is None:
            continue
        parsed.append((f, mod))
        sibling_classes.update(n.name for n in mod.body if isinstance(n, ast.ClassDef))
    for f, mod in parsed:
        rel = srel / "contract" / "exception" / f.name
        if re.search(r"_v\d+$", f.stem):
            out.add("#170", rel, "예외 계약 파일에 `_v1` 접미를 붙이지 않는다")
        pubs = [n for n in mod.body if isinstance(n, ast.ClassDef) and not n.name.startswith("_")]
        if len(pubs) >= 2:
            out.add("#168", rel, f"published 예외는 클래스 하나당 1모듈이다 — {len(pubs)}개")
        for cls in pubs:
            if re.search(r"V\d+$", cls.name):
                out.add("#170", rel, f"예외 계약 클래스에 버전 접미를 붙이지 않는다 — `{cls.name}`")
            if any(tok in cls.name for tok in ANSWER_NOT_EXCEPTION):
                out.add("#453", rel, f"「물건이 없다·이미 있다·규칙이 거절한다」는 예외가 아니라 답이다(#454 — 공개 예외는 «돌려줄 것이 아예 없는» 갈래뿐) — `{cls.name}`")
            if f != base_file:
                base_names = {b.attr if isinstance(b, ast.Attribute) else getattr(b, "id", "") for b in cls.bases}
                if base_names & {"Exception", "BaseException"} and not (base_names & (base_classes | sibling_classes)):
                    out.add("#167", rel, f"published 예외는 기저 예외를 상속한다(중간층 경유 허용) — `{cls.name}` 이 `Exception` 직접 상속이다")
            bare = cls.name
            for tok in ("Error", "Exception", "Failed", "Failure"):
                bare = bare.removesuffix(tok)
            if not bare:
                cand.add("#171", rel, f"예외 이름이 접미사뿐이다 — `{cls.name}`", "「부르는 쪽이 이름만 보고 분기할 수 있나」")


# ── ACL — #361 · #363 · #450 · #473 ────────────────────────────────────────

def _acl_dir(bc: Path) -> Path | None:
    cand_path = bc / "driven_layer" / "adapter" / "anticorruption_layer"
    return cand_path if cand_path.is_dir() else None


# #473 — 이름 · 값을 거쳐 아무 코드에나 닿는 내장(이름으로 속성 찾기 · 반복기 한 칸 읽기 · 동적 실행)은 «알려진 바깥» 이 아니다.
_REACHING_BUILTINS: frozenset[str] = frozenset({
    "super", "type", "getattr", "hasattr", "setattr", "delattr", "vars", "globals", "locals",
    "__import__", "eval", "exec", "next", "iter", "anext", "aiter"})
# #473 — 넘긴 값을 끝까지 읽거나 넘긴 함수를 부르는 내장. 바깥 아닌 맨 이름(창구가 돌려준 생성기 · 창구 함수를
# 담았을 수 있다)을 넘기면 창구 코드가 돌 수 있다고 본다.
_CONSUMING_BUILTINS: frozenset[str] = frozenset({
    "list", "tuple", "set", "frozenset", "dict", "bytes", "bytearray", "sorted", "reversed", "sum", "min", "max",
    "any", "all", "enumerate", "zip", "map", "filter"})


def _covers_base(node: ast.Try, base_names: set[str]) -> bool:
    """마지막 except 가 상대 창구의 기저 예외를 잡나."""
    return bool(node.handlers) and bool(_ann_idents(node.handlers[-1].type) & base_names)


def _reraises(node: ast.Try) -> bool:
    """처리기 안에 잡은 예외를 그대로 다시 던지는 `raise` · `raise <잡은 이름>` 이 있나."""
    return any(
        isinstance(r, ast.Raise) and (r.exc is None or (isinstance(r.exc, ast.Name) and r.exc.id == h.name))
        for h in node.handlers for r in ast.walk(h)
    )


def _tries(node: ast.AST, owner: str):
    """(try, 둘러싼 `클래스.함수`) 를 소스 차례로 — 진단 꼬리용."""
    for child in ast.iter_child_nodes(node):
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            yield from _tries(child, f"{owner}.{child.name}" if owner else child.name)
            continue
        if isinstance(child, ast.Try) and child.handlers:
            yield child, owner
        yield from _tries(child, owner)


def _root(expr: ast.expr) -> str | None:
    """`a.b[c](d).e` 의 뿌리 이름 `a` — 뿌리가 이름이 아니면(글자 · 식) None."""
    while isinstance(expr, (ast.Attribute, ast.Subscript, ast.Call)):
        expr = expr.func if isinstance(expr, ast.Call) else expr.value
    return expr.id if isinstance(expr, ast.Name) else None


# ── #473 받은 글 검증 — `model_validate_json` 받는 쪽의 허용 목록(2026-11-14 F4-167) ────────────────
# 검증 때도 모델의 검증기 · 칸 기본값 짓기 · 바탕 클래스 코드가 돈다. 그래서 받는 쪽이 «검증 코드가 끼어들 수 없는 꼴» 일 때만
# 그 부르기를 «안 돈다» 로 본다. `model_validate` · `model_validate_strings` 는 넘긴 값을 끝까지 읽어(창구 생성기 · property)
# 받지 않는다.
_TEXT_VALIDATORS: frozenset[str] = frozenset({"model_validate_json"})
_FACTORY_BUILTINS: frozenset[str] = frozenset({
    "tuple", "list", "dict", "set", "frozenset", "str", "int", "float", "bool", "len", "enumerate", "zip", "range",
    "isinstance"})
_DATA_BUILTINS: frozenset[str] = frozenset({
    "str", "int", "float", "bool", "bytes", "tuple", "list", "dict", "set", "frozenset", "None", "type"})
_DATA_TYPING: frozenset[str] = frozenset({"Literal", "Optional", "Union", "Final", "Annotated", "ClassVar"})
_STD_DATA: dict[str, frozenset[str]] = {
    "datetime": frozenset({"date", "datetime", "time", "timedelta", "timezone"}), "decimal": frozenset({"Decimal"}),
    "uuid": frozenset({"UUID"}), "types": frozenset({"EllipsisType", "NoneType"})}
_WIRE_IMPORT_TOPS: frozenset[str] = frozenset({
    "__future__", "typing", "typing_extensions", "pydantic", "datetime", "decimal", "enum", "uuid", "types"})
_NAME_DEVICES: frozenset[str] = frozenset({
    "globals", "locals", "vars", "setattr", "delattr", "__import__", "importlib", "exec", "eval"})
_NAME_DEVICE_ATTRS: frozenset[str] = frozenset({"__dict__", "__setattr__", "__delattr__"})
# 짝 폴더에서 pydantic 모델의 칸 · 짓기를 실행 때 바꾸는 속성(`model_fields[...] = …` · `model_rebuild(force=True)`).
_MODEL_REBUILD_ATTRS: frozenset[str] = frozenset({"model_fields", "model_rebuild"})
# 칸 정의 자리의 `Field(...)` 에서 아무 값이나 받는 꼬리표 인자 — 검증 때 부르지 않는 이름 · 설명 글이다.
_FIELD_LABELS: frozenset[str] = frozenset({"alias", "title", "description", "validation_alias", "serialization_alias"})
# 칸 정의 자리의 세 꼴 — 칸 타입 · 칸 하나(타입 또는 (타입, 기본값)) · 칸 묶음(`**` 로 펼치는 dict).
_FIELD_TYPE: str = "type"
_FIELD_SPEC: str = "spec"
_FIELD_DICT: str = "dict"
_PYDANTIC_MODEL_BASES: frozenset[str] = frozenset({"BaseModel", "RootModel"})
_WIRE_ENUM_BASES: frozenset[str] = frozenset({"Enum", "StrEnum", "IntEnum"})
_NOT_DATA_SUFFIXES: tuple[str, ...] = ("Port", "Repository", "Protocol", "Command", "Query", "UnitOfWork", "Service",
                                       "Adapter", "Gateway", "Client")
_PLAIN_TYPE_BUILTINS: frozenset[str] = frozenset({
    "str", "int", "float", "bool", "bytes", "tuple", "list", "dict", "set", "frozenset"})
_BUILTIN_CONTAINERS: frozenset[str] = frozenset({"tuple", "list", "dict", "set", "frozenset"})
_PLAIN_TYPING: frozenset[str] = frozenset({
    "Optional", "Union", "Literal", "ClassVar", "Final", "List", "Dict", "Tuple", "Set", "FrozenSet"})
_OLD_CONTAINERS: tuple[str, ...] = ("List", "Dict", "Tuple", "Set", "FrozenSet")


def _uses_name_device(mod: ast.Module) -> bool:
    """이름 · 값을 실행 때 바꾸는 장치를 쓰나 — globals · locals(모듈 수준에서는 globals 와 같다) · vars · setattr · delattr ·
    `__import__` · importlib · exec · eval(맨 이름 · `builtins` 의 속성 · `from builtins import …` · `__builtins__`) · `__dict__` ·
    함수의 `__globals__` · 내장 함수의 `__self__`(= builtins) · 모듈의 `.__builtins__` · `sys.modules` · `sys._getframe` · 틀의
    `f_globals` · `f_locals`(`sys` · `builtins` 는 `import … as` 별칭도 같다) · 별 import(`from .x import *`). 맨 속성 이름
    (`x.vars`)은 세지 않는다. 쓰는 파일은 이름에 기대는 면제(#473 받은 글 검증 허용 목록 · wire 모듈 · #134 pydantic 이름)를
    쓰지 않는다."""
    modules: dict[str, str] = {"sys": "sys", "builtins": "builtins"}  # 이름 → 그 이름이 가리키는 sys · builtins
    for n in ast.walk(mod):
        if isinstance(n, ast.Import):
            modules.update({a.asname: a.name for a in n.names if a.asname and a.name in ("sys", "builtins")})
    for n in ast.walk(mod):
        if isinstance(n, ast.ImportFrom) and any(a.name == "*" for a in n.names):
            return True
        if isinstance(n, ast.Name) and (n.id in _NAME_DEVICES or n.id == "__builtins__"):
            return True
        if isinstance(n, ast.Attribute) and n.attr in (
                "__dict__", "f_globals", "f_locals", "__globals__", "__self__", "__builtins__"):
            return True
        if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name) and (
                (modules.get(n.value.id) == "sys" and n.attr in ("modules", "_getframe"))
                or (modules.get(n.value.id) == "builtins" and n.attr in _NAME_DEVICES)):
            return True
        if isinstance(n, ast.Import) and any(a.name.split(".")[0] == "importlib" for a in n.names):
            return True
        if isinstance(n, ast.ImportFrom) and (n.module or "").split(".")[0] == "importlib":
            return True
        if isinstance(n, ast.ImportFrom) and (
                (n.module == "sys" and any(a.name in ("modules", "_getframe") for a in n.names))
                or (n.module == "builtins" and any(a.name in _NAME_DEVICES for a in n.names))):
            return True
    return False


def _bind_counts(node: ast.AST) -> dict[str, int]:
    """이 마디 안에서 이름마다 묶는 자리 수 — 대입 · 지움 · 매개변수 · def · class · import · `except … as` ·
    `match` 갈래 이름 · 타입 매개변수."""
    out: dict[str, int] = {}

    def add(name: str | None) -> None:
        if name:
            out[name] = out.get(name, 0) + 1

    for n in ast.walk(node):
        kind: str = type(n).__name__  # match · 타입 매개변수 마디는 해석기 판에 따라 없다(3.10 · 3.12)
        if isinstance(n, ast.Name) and not isinstance(n.ctx, ast.Load):
            add(n.id)
        elif isinstance(n, ast.arg):
            add(n.arg)
        elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            add(n.name)
        elif isinstance(n, (ast.Import, ast.ImportFrom)):
            for a in n.names:
                add(a.asname or a.name.split(".")[0])
        elif isinstance(n, ast.ExceptHandler):
            add(n.name)
        elif kind in ("MatchAs", "MatchStar"):
            add(n.name)
        elif kind == "MatchMapping":
            add(n.rest)
        elif kind in ("TypeVar", "ParamSpec", "TypeVarTuple"):
            add(getattr(n, "name", None))
    return out


def _plain_field_annotation(ann: ast.AST | None, leaf: set[str], typing_of: dict[str, str],
                            in_classvar: bool = False) -> bool:
    """wire 칸 주석이 «검증 코드가 끼어들 수 없는 꼴» 인가.

    끝 이름은 `leaf`(다시 묶이지 않은 맨 타입 · 계약 · 표준 값 이름 · 같은 조건 wire)뿐이고, 첨자 머리는 내장 그릇과
    `typing` 의 Optional · Union · Final · ClassVar · Literal · 옛 그릇 이름뿐이다. `|` · `...` · `None` 은 받는다.
    부르기 · 람다 · 속성 · 글자 주석(Literal 안 글자 빼고) · `Annotated` 는 받지 않는다. `ClassVar[...]` 안은 검증 칸이 아니라
    이름을 가리지 않는다(부르기 · 람다 · 속성 · 글자는 거기서도 받지 않는다).
    """
    if ann is None:
        return False
    if isinstance(ann, ast.Constant):
        return ann.value is None or ann.value is Ellipsis
    if isinstance(ann, ast.Name):
        return in_classvar or ann.id in leaf or typing_of.get(ann.id) in _OLD_CONTAINERS
    if isinstance(ann, ast.BinOp) and isinstance(ann.op, ast.BitOr):
        return (_plain_field_annotation(ann.left, leaf, typing_of, in_classvar)
                and _plain_field_annotation(ann.right, leaf, typing_of, in_classvar))
    if isinstance(ann, ast.Tuple):
        return all(_plain_field_annotation(e, leaf, typing_of, in_classvar) for e in ann.elts)
    if isinstance(ann, ast.Subscript) and isinstance(ann.value, ast.Name):
        head: str = ann.value.id
        origin: str | None = typing_of.get(head)
        if origin == "Literal":
            elts: list[ast.expr] = ann.slice.elts if isinstance(ann.slice, ast.Tuple) else [ann.slice]
            return all(isinstance(e, ast.Constant) and (e.value is None or isinstance(e.value, (str, int, bool)))
                       for e in elts)
        if origin == "ClassVar":
            return _plain_field_annotation(ann.slice, leaf, typing_of, True)
        if (head in _BUILTIN_CONTAINERS and head in leaf) or origin in ("Optional", "Union", "Final", *_OLD_CONTAINERS):
            return _plain_field_annotation(ann.slice, leaf, typing_of, in_classvar)
    return False


def _typing_imports(mod: ast.Module, binds: dict[str, int]) -> dict[str, str]:
    """모듈 최상위 `from typing(_extensions) import X [as Y]` 가운데 한 번만 묶인 그릇 · 꾸밈 이름 → 원 이름."""
    out: dict[str, str] = {}
    for st in mod.body:
        if isinstance(st, ast.ImportFrom) and st.level == 0 and st.module in ("typing", "typing_extensions"):
            for a in st.names:
                name: str = a.asname or a.name
                if binds.get(name) == 1 and a.name in _PLAIN_TYPING:
                    out[name] = a.name
    return out


_PARTNER_ALTERED: dict[Path, bool] = {}  # 짝 ACL 폴더 → 바꿔 끼우기 있음(_check_acl 이 부를 때마다 비운다)


def _plain_methods(mod: ast.Module, into: dict[str, set[str]]) -> None:
    """모듈의 클래스마다 보통 메서드(classmethod · staticmethod 빼고) 이름을 `into` 에 모은다."""
    for cls in ast.walk(mod):
        if isinstance(cls, ast.ClassDef):
            into.setdefault(cls.name, set()).update(
                f.name for f in cls.body if isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef))
                and not any(isinstance(d, ast.Name) and d.id in ("classmethod", "staticmethod") for d in f.decorator_list))


def _foreign_attribute_write(mod: ast.Module, plain: dict[str, set[str]]) -> bool:
    """메서드 첫 매개변수 `self` · `cls` 의 칸 말고 다른 속성을 바꾸나(대입 · 지움 · 덧셈 대입) — 이름이 `cls` 인 보통 함수
    매개변수(`def _install(cls): cls.model_validate_json = …`) · `@staticmethod` 의 첫 매개변수는 메서드 첫 매개변수가 아니라
    바꾸기로 센다. 짝 폴더 클래스(`plain` = 폴더 전체의 클래스 → 보통 메서드)의 보통 메서드를 클래스에서 꺼내면
    (`_Patch.install(PartWire)` — 아무 값이나 `self` 가 된다 · 다른 파일에서 import 한 클래스 · `모듈.클래스.메서드` 도) 그것도
    바꾸기로 센다."""

    def static(fn: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
        return any(isinstance(d, ast.Name) and d.id == "staticmethod" for d in fn.decorator_list)

    held: dict[str, set[str]] = {}  # 이 파일에서 짝 폴더 클래스를 가리키는 이름 → 보통 메서드
    _plain_methods(mod, held)
    for n in ast.walk(mod):
        if isinstance(n, (ast.Import, ast.ImportFrom)):
            for a in n.names:
                if a.name.split(".")[-1] in plain:
                    held.setdefault(a.asname or a.name, set()).update(plain[a.name.split(".")[-1]])
    for n in ast.walk(mod):
        if isinstance(n, ast.Attribute):
            methods: set[str] = (held.get(n.value.id, set()) if isinstance(n.value, ast.Name)
                                 else plain.get(n.value.attr, set()) if isinstance(n.value, ast.Attribute) else set())
            if n.attr in methods:
                return True

    def visit(node: ast.AST, owner: str | None) -> bool:
        for child in ast.iter_child_nodes(node):
            inner: str | None = owner
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                first: list[ast.arg] = [*child.args.posonlyargs, *child.args.args][:1]
                inner = (first[0].arg if isinstance(node, ast.ClassDef) and first and first[0].arg in ("self", "cls")
                         and not static(child) else None)
            elif isinstance(child, (ast.ClassDef, ast.Lambda)):
                inner = None
            if isinstance(child, ast.Attribute) and not isinstance(child.ctx, ast.Load) and not (
                    inner is not None and isinstance(child.value, ast.Name) and child.value.id == inner):
                return True
            if visit(child, inner):
                return True
        return False

    return visit(mod, None)


def _partner_altered(partner: Path) -> bool:
    """짝 ACL 폴더 파일 하나라도 이름 · 값을 실행 때 바꾸는 장치(`__setattr__` · `__delattr__` 포함)를 쓰거나, 메서드 첫
    매개변수 `self` · `cls` 의 칸 밖의 속성을 바꾸거나(대입 · 지움 · 덧셈 대입 — wire · 그 칸 타입(계약 dataclass 등) · pydantic
    바탕 어느 것이든 검증 때 도는 코드를 꽂을 수 있다), 짝 폴더 클래스의 보통 메서드를 클래스에서 꺼내거나(파일을 건너도),
    pydantic 모델의 칸 · 짓기를 실행 때 바꾸는 속성(`model_fields` ·
    `model_rebuild` · `__pydantic_*`)을 쓰나 · 못 읽는 파일이 있나. 그러면 그 폴더 파일들은 허용 목록을 쓰지 않는다."""
    partner = partner.resolve()
    if partner not in _PARTNER_ALTERED:
        altered: bool = False
        mods: list[ast.Module] = []
        for f in sorted(partner.rglob("*.py")):
            try:
                mods.append(ast.parse(f.read_text(encoding="utf-8")))
            except (OSError, SyntaxError, UnicodeDecodeError, ValueError):
                altered = True  # 못 읽는 파일 — 바꿔 끼우는지 모른다
                break
        plain: dict[str, set[str]] = {}  # 짝 폴더 전체의 클래스 → 보통 메서드
        for mod in mods:
            _plain_methods(mod, plain)
        for mod in [] if altered else mods:
            if _uses_name_device(mod) or _foreign_attribute_write(mod, plain) or any(
                    isinstance(n, ast.Attribute) and (n.attr in _NAME_DEVICE_ATTRS or n.attr in _MODEL_REBUILD_ATTRS
                                                      or n.attr.startswith("__pydantic"))
                    for n in ast.walk(mod)):
                altered = True
                break
        _PARTNER_ALTERED[partner] = altered
    return _PARTNER_ALTERED[partner]


_DOMAIN_DATA: dict[tuple[Path, str], bool] = {}  # (도메인 모듈 파일, 이름) → 자료 클래스(_check_acl 이 부를 때마다 비운다)


def _domain_data_class(path: Path, module: str, name: str) -> bool:
    """`domain_layer` 에서 온 이름이 자료 클래스인가 — 그 모듈 파일의 최상위 클래스이고, 같은 모듈 바탕을 끝까지 따라가
    metaclass 가 없고 다른 모듈 바탕은 enum 바탕(`Enum` · `StrEnum` · `IntEnum` · `Flag` · `IntFlag`)과 `str` · `int` ·
    `object` 뿐일 때만. ABC · Protocol · Generic · 그 밖의 다른 모듈 바탕은 직접이든 간접이든 자료가 아니다(못 찾아도 아니다)."""
    parts: tuple[str, ...] = path.resolve().parts
    if "application" not in parts:
        return False
    i: int = len(parts) - 1 - parts[::-1].index("application")
    base: Path = Path(*parts[:i]).joinpath(*module.split("."))
    module_file: Path = base.with_suffix(".py") if base.with_suffix(".py").is_file() else base / "__init__.py"
    key: tuple[Path, str] = (module_file, name)
    if key not in _DOMAIN_DATA:
        ok: bool = False
        try:
            mod: ast.Module = ast.parse(module_file.read_text(encoding="utf-8"))
            classes: dict[str, ast.ClassDef] = {st.name: st for st in mod.body if isinstance(st, ast.ClassDef)}
            enum_bases: set[str] = {a.asname or a.name for st in mod.body if isinstance(st, ast.ImportFrom)
                                    and st.level == 0 and st.module == "enum" for a in st.names
                                    if a.name in ("Enum", "StrEnum", "IntEnum", "Flag", "IntFlag")}

            def plain(cname: str, seen: set[str]) -> bool:
                if cname in seen or cname not in classes:
                    return False
                seen.add(cname)
                cls: ast.ClassDef = classes[cname]
                if any(k.arg == "metaclass" for k in cls.keywords):
                    return False
                for b in cls.bases:
                    if isinstance(b, ast.Name) and b.id in classes:
                        if not plain(b.id, seen):
                            return False
                    elif not (isinstance(b, ast.Name) and (b.id in enum_bases or b.id in ("str", "int", "object"))):
                        return False  # ABC · Protocol · Generic · 다른 모듈 바탕(보수)
                return True

            ok = plain(name, set())
        except (OSError, SyntaxError, UnicodeDecodeError, ValueError, RecursionError):
            ok = False
        _DOMAIN_DATA[key] = ok
    return _DOMAIN_DATA[key]


def _partner_root(path: Path) -> Path | None:
    """이 파일이 든 짝 ACL 폴더 `…/anticorruption_layer/<partner>/`."""
    parts: tuple[str, ...] = path.parts
    if "anticorruption_layer" not in parts:
        return None
    i: int = len(parts) - 1 - parts[::-1].index("anticorruption_layer")
    return Path(*parts[: i + 2]) if i + 1 < len(parts) else None


class _BcImports:
    """꼴 C 판정 재료 — 한 BC 의 프로덕션 파일(BC 바로 아래 `test/` · SKIP_DIRS 뺌)이 import 마디로 들이는 모듈 · 이름. 처음 물을 때
    한 번 읽는다(`_check_acl` 이 BC 마다 하나 짓는다). 못 읽거나 못 파싱하는 파일이 하나라도 있으면 «모른다» 다."""

    def __init__(self, bc: Path) -> None:
        self.bc: Path = bc
        self._built: bool = False
        self._unknown: bool = False
        self._whole: list[tuple[str, ...]] = []  # 통째로 들인 모듈 · 꾸러미 마디(`import` · `from 꾸러미 import 아래 모듈` · 별 import)
        self._named: set[tuple[tuple[str, ...], str]] = set()  # (모듈 마디, 이름) — `from 모듈 import 이름`

    def _parts(self, path: Path) -> tuple[str, ...]:
        """BC 를 담은 폴더의 부모 기준 모듈 마디 — `…/application/billing/x/y.py` → ("application", "billing", "x", "y")."""
        parts: list[str] = list(path.relative_to(self.bc.parent.parent).parts)
        parts[-1] = parts[-1].removesuffix(".py")
        if parts[-1] == "__init__":
            parts.pop()
        return tuple(parts)

    def _absolute(self, dotted: str) -> tuple[str, ...] | None:
        """절대 import 의 모듈 마디 — BC 를 담은 폴더 이름(`application`)부터. 그 이름이 없으면 이 저장소 BC 밖이다."""
        names: tuple[str, ...] = tuple(dotted.split("."))
        top: str = self.bc.parent.name
        return names[names.index(top):] if top in names else None

    def _build(self) -> None:
        self._built = True
        for f in sorted(self.bc.rglob("*.py")):
            rp: tuple[str, ...] = f.relative_to(self.bc).parts
            if set(rp) & SKIP_DIRS or rp[0] == "test":
                continue
            try:
                mod: ast.Module = ast.parse(f.read_text(encoding="utf-8"))
            except (OSError, SyntaxError, UnicodeDecodeError, ValueError):
                self._unknown = True  # 못 읽는 파일 — 무엇을 import 하는지 모른다
                return
            here: tuple[str, ...] = self._parts(f)
            package: tuple[str, ...] = here if f.name == "__init__.py" else here[:-1]
            for n in ast.walk(mod):
                if isinstance(n, ast.Import):
                    for a in n.names:
                        target: tuple[str, ...] | None = self._absolute(a.name)
                        if target is not None:  # `import a.b` 는 꼭대기 `a` 를 묶어 그 아래 모두에 닿는다
                            self._whole.append(target if a.asname else target[:1])
                elif isinstance(n, ast.ImportFrom):
                    if n.level == 0:
                        target = self._absolute(n.module or "")
                    elif n.level - 1 <= len(package):
                        target = package[:len(package) - (n.level - 1)] + (tuple(n.module.split(".")) if n.module else ())
                    else:
                        target = None
                    if target is None:
                        continue
                    for a in n.names:
                        if a.name == "*":
                            self._whole.append(target)
                        else:
                            self._named.add((target, a.name))
                            self._whole.append(target + (a.name,))  # 아래 모듈 · 꾸러미를 이름으로 들임

    def private(self, path: Path, name: str) -> bool:
        """그 BC 프로덕션 파일 어디서도 그 모듈의 그 이름을 import 하지 않고(짝 폴더 파일 · 다시 내보내기 포함) 그 모듈이나 그 위
        꾸러미를 통째로 · 별 import 로 들이지 않나(같은 모듈의 다른 이름 import 는 세지 않는다). 모르면 아니다."""
        if not self._built:
            self._build()
        if self._unknown:
            return False
        module: tuple[str, ...] = self._parts(path)
        return (module, name) not in self._named and not any(module[:len(w)] == w for w in self._whole)


def _window_import(module: str, name: str) -> bool:
    """`from <module> import <name>` 이 창구(`open_host_service` — 계약 `contract` 아래는 빼고) 쪽인가."""
    parts: list[str] = f"{module}.{name}".split(".")
    return "open_host_service" in parts and "contract" not in parts


def _contract_import(module: str) -> bool:
    """상대 창구 계약(`open_host_service/…/contract/…`) 모듈인가."""
    parts: list[str] = module.split(".")
    return "open_host_service" in parts and "contract" in parts


class _PartnerWires:
    """짝 ACL 폴더 안의 «선언만 있는 wire 모듈» 판정 — 모듈마다 한 번 잰다."""

    def __init__(self, partner: Path) -> None:
        self.partner: Path = partner.resolve()
        self.cache: dict[Path, bool] = {}

    def _inside(self, p: Path | None) -> bool:
        return p is not None and p.resolve().is_relative_to(self.partner)

    def resolve(self, here: Path, node: ast.ImportFrom) -> tuple[Path | None, dict[str, Path | None]]:
        """상대 import 의 (대상 모듈 파일, {이름 → 하위 모듈 파일}) — 짝 폴더 밖이면 (None, {})."""
        base: Path = here.parent
        for _ in range(node.level - 1):
            base = base.parent
        target: Path = base.joinpath(*node.module.split(".")) if node.module else base
        module_file: Path | None = (target / "__init__.py") if target.is_dir() else target.with_suffix(".py")
        subs: dict[str, Path | None] = {}
        for a in node.names:
            candidates: list[Path] = [target / f"{a.name}.py", target / a.name / "__init__.py"]
            subs[a.asname or a.name] = next((c for c in candidates if c.is_file()), None)
        if not self._inside(target if target.exists() else target.with_suffix(".py")):
            return None, {}
        if module_file is not None and not (module_file.is_file() and self._inside(module_file)):
            module_file = None
        subs = {k: v for k, v in subs.items() if v is None or self._inside(v)}
        return module_file, subs

    def module_ok(self, f: Path, seen: set[Path] | None = None) -> bool:
        """선언만 있는 wire 모듈인가 — 상대 import 로 닿는 짝 폴더 모듈도 같은 조건을 지나야 한다."""
        f = f.resolve()
        if f in self.cache:
            return self.cache[f]
        seen = set() if seen is None else seen
        if f in seen:
            return True
        seen.add(f)
        ok: bool = self._module_ok(f, seen)
        self.cache[f] = ok
        return ok

    def _module_ok(self, f: Path, seen: set[Path]) -> bool:
        """짝 폴더 안 · 이름 장치 0 · import 는 표준 몇 · pydantic · 계약 · 같은 조건 짝 폴더 모듈뿐 · 최상위는 import ·
        wire 클래스 · 글자 · 부르기(람다) 없는 대입 · `type` 별칭뿐."""
        if not f.is_relative_to(self.partner) or len(seen) > 30:
            return False
        try:
            mod: ast.Module = ast.parse(f.read_text(encoding="utf-8"))
        except (OSError, SyntaxError, UnicodeDecodeError):
            return False
        if _uses_name_device(mod):
            return False
        binds: dict[str, int] = _bind_counts(mod)
        typing_of: dict[str, str] = _typing_imports(mod, binds)
        leaf: set[str] = {n for n in _PLAIN_TYPE_BUILTINS if n not in binds}  # 다시 묶인 내장 이름은 맨 타입이 아니다
        # 이 모듈 클래스(앞 참조 포함) — 모두 아래 클래스 조건을 지나야 모듈이 선다.
        leaf |= {st.name for st in mod.body if isinstance(st, ast.ClassDef) and binds.get(st.name) == 1}
        for st in mod.body:
            if isinstance(st, ast.ImportFrom) and st.level == 0 and st.module:
                for a in st.names:
                    name: str = a.asname or a.name
                    if binds.get(name) == 1 and (_contract_import(st.module)
                                                 or a.name in _STD_DATA.get(st.module, frozenset())):
                        leaf.add(name)
            elif isinstance(st, ast.ImportFrom):  # 상대 import 이름 — 아래에서 그 모듈도 module_ok 로 거른다
                leaf |= {a.asname or a.name for a in st.names if binds.get(a.asname or a.name) == 1}
        bases: set[str] = {"str", "int"}
        for stmt in mod.body:
            if isinstance(stmt, ast.Import):
                if any(a.name.split(".")[0] not in _WIRE_IMPORT_TOPS for a in stmt.names):
                    return False
            elif isinstance(stmt, ast.ImportFrom):
                if stmt.level == 0:
                    top: str = (stmt.module or "").split(".")[0]
                    if not (top in _WIRE_IMPORT_TOPS or _contract_import(stmt.module or "")):
                        return False
                    if top == "pydantic":
                        bases |= {a.asname or a.name for a in stmt.names if a.name in _PYDANTIC_MODEL_BASES}
                    if top == "enum":
                        bases |= {a.asname or a.name for a in stmt.names if a.name in _WIRE_ENUM_BASES}
                else:
                    module_file, subs = self.resolve(f, stmt)
                    if module_file is None and not any(subs.values()):
                        return False
                    for alias in stmt.names:
                        target_file: Path | None = subs.get(alias.asname or alias.name) or module_file
                        if target_file is None or not self.module_ok(target_file, seen):
                            return False
                        bases.add(alias.asname or alias.name)
            elif isinstance(stmt, ast.ClassDef):
                if not _wire_class(stmt, bases, leaf, typing_of):
                    return False
                bases.add(stmt.name)
            elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant):
                continue
            elif isinstance(stmt, (ast.Assign, ast.AnnAssign)) or type(stmt).__name__ == "TypeAlias":
                value: ast.expr | None = getattr(stmt, "value", None)
                if value is not None and any(isinstance(x, (ast.Call, ast.Lambda)) for x in ast.walk(value)):
                    return False
            else:
                return False
        return True


def _literal_call(node: ast.AST, names: frozenset[str]) -> bool:
    """`ConfigDict(...)` · `Field(...)` 처럼 글자 값만 받는 짓기 부르기인가."""
    return (isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in names
            and all(isinstance(a, ast.Constant) for a in node.args)
            and all(isinstance(k.value, ast.Constant) for k in node.keywords))


def _wire_class(cls: ast.ClassDef, bases: set[str], leaf: set[str], typing_of: dict[str, str]) -> bool:
    """선언만 있는 wire 클래스인가 — 데코레이터 0 · 바탕은 `bases`(pydantic 모델 · enum · 다른 wire)뿐 · 몸통은 칸 · 설정 ·
    글자 · `pass` 뿐(메서드 · 검증기 0) · 칸 주석은 `_plain_field_annotation` 꼴 · 칸 값은 글자 · 글자만 받는 `Field(...)` ·
    `ConfigDict(...)`."""
    if cls.decorator_list or not cls.bases:
        return False
    if not all(isinstance(b, ast.Name) and b.id in bases for b in cls.bases):
        return False
    if not all(isinstance(k.value, ast.Constant) for k in cls.keywords):
        return False
    for item in cls.body:
        if isinstance(item, ast.Expr) and isinstance(item.value, ast.Constant):
            continue
        if isinstance(item, ast.Pass):
            continue
        if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
            if not _plain_field_annotation(item.annotation, leaf, typing_of):
                return False  # Annotated 검증기 · default_factory · 같은 파일 자료 클래스 · 모듈 별칭 칸 타입
            if item.value is None or isinstance(item.value, ast.Constant) or _literal_call(
                    item.value, frozenset({"ConfigDict", "Field"})):
                continue
            return False
        if isinstance(item, ast.Assign) and all(isinstance(t, ast.Name) for t in item.targets):
            if isinstance(item.value, ast.Constant) or _literal_call(item.value, frozenset({"ConfigDict"})):
                continue
            return False
        return False
    return True


def _enclosing_functions(mod: ast.Module) -> dict[int, ast.FunctionDef | ast.AsyncFunctionDef]:
    """try(id) → 그 try 를 둘러싼 가장 안쪽 함수 — 받은 글 검증 허용 목록이 그 함수의 매개변수를 본다."""
    out: dict[int, ast.FunctionDef | ast.AsyncFunctionDef] = {}

    def visit(node: ast.AST, fn: ast.FunctionDef | ast.AsyncFunctionDef | None) -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.Try) and fn is not None:
                out[id(child)] = fn
            inner: ast.FunctionDef | ast.AsyncFunctionDef | None = (
                child if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)) else fn)
            visit(child, inner)

    visit(mod, None)
    return out


class _WindowTry:
    """기저를 안 잡는 try 에서 상대 창구 코드가 돌 수 있나(#473) — 모르면 돈다고 본다.

    안 돈다 = 몸통(기저를 잡고 다시 던지지 않는 안쪽 try 의 몸통은 뺀다)에서
      ① 창구 · ACL 안 import 이름 · 같은 파일 함수/클래스 이름이 글자로 없고(인자 · 람다 안 포함 — 콜백이 잡힌다)
      ② 모든 호출 · with · 반복 · await · yield from 대상의 뿌리가 «알려진 바깥» 이고
         (내장 · 창구 밖 import · 그것으로만 지은 모듈 상수 — 파일 안에서 다시 묶이지 않은 이름)
      ③ self · cls 의 속성 · 같은 파일 함수 이름의 속성 · 같은 파일에서 값을 담는 속성을 읽지 않고
      ④ 넘긴 값을 읽거나 넘긴 함수를 부르는 내장에 바깥 아닌 맨 이름을 넘기지 않을 때뿐이다.
    알려진 바깥 함수는 넘겨받은 맨 이름(지역 · 매개변수)과 그 칸을 자료로 쓴다고 본다 — 이 판정의 한계다.

    받은 글 검증(2026-11-14 F4-167): 몸통의 `model_validate_json` 부르기는 받는 쪽이 아래 셋 가운데 하나일 때만 그 부르기와
    받는 쪽 마디를 «안 돈다» 로 본다. 인자와 몸통의 다른 마디는 위 판정 그대로다(검증 말고 같은 파일 함수를 함께 부르면 붉다).
      A 선언만 있는 wire 클래스 — 같은 파일 클래스, 또는 짝 ACL 폴더 안 상대 import(그 import 말고 묶기 0). 바탕은 같은 파일
        wire 면 pydantic 모델 · 다른 wire, 상대 wire 모듈이면 거기에 enum 도. 데코레이터 · 메서드 · 검증기 0 · 클래스 키워드는 글자만,
        몸통은 칸 · 글자 · 글자만 받는 `Field(...)` · `ConfigDict(...)` 뿐, 칸 주석은 맨 타입 · 계약 · 표준 값 이름 · 같은 조건
        wire · 표준 그릇뿐(`Annotated` · 부르기 · 람다 · 속성 · 글자 주석 0 — 같은 파일 enum 은 칸 타입이 아니다). 상대 wire
        모듈은 최상위가 import · 클래스 · 글자 · 부르기 없는 대입뿐이고, import 는 표준 몇 · pydantic · 계약 · 같은 조건을 지나는
        짝 폴더 모듈뿐이다.
      B 같은 파일 모델 짓기 함수의 부르기 `F(인자…)` — 인자는 글자이거나 둘러싼 함수의 «값 자료» 매개변수(자료 타입 주석 ·
        기본값 0 · 다시 안 묶음 · 주석에 `type` · pydantic 이름이 별칭 안까지 없음)뿐. F 는 `_model_factory` 꼴이고, `create_model`
        의 칸 정의(칸 키워드 값 · `**` · 예약 칸)는 짓기 함수 몸통에 글자로 적은 타입 식과 파일 안에서 고쳐지지 않는 모듈 상수 표의
        첨자 꺼냄으로만 짓는다(`_factory_fields_ok` · `_plain_reads` · `_unaltered` — `__config__` 상수도 그 자리 말고는 첨자 ·
        `in` 으로만 읽고 고쳐지지 않아야 한다). 짓기 함수 매개변수는
        키 고르기 · 칸 이름으로만 — dict · tuple · list · str 매개변수가 칸 정의로 흘러가면 받지 않는다(다른 짓기 함수만 부르고 그
        자리가 같은 꼴로 넘길 때만 실어 나르기로 받는다).
      C `_` 로 시작하는 함수의 `type[T]`(T 의 바운드 = pydantic 모델) · `type[<wire>]` 매개변수 — 기본값 0 · 다시 안 묶음 · 그
        함수 이름이 값으로 새지 않고 파일 안 부르는 자리마다 그 칸에 wire 를 넘김. 그리고 같은 BC 프로덕션 파일(`test/` 뺌 — 짝
        폴더 파일 · 다시 내보내기 포함) 어디서도 그 이름을 import 하지 않고 그 모듈(그 위 꾸러미 포함)을 통째로 · 별 import 로
        들이지 않을 때만(같은 모듈의 다른 이름 import 는 세지 않는다 · 못 읽는 파일이 있으면 받지 않는다 · `_BcImports`). 다른 BC ·
        같은 BC 응용 층의 import 는 #186 · #185 가 따로 막는다(다른 BC driven 층은 #12).
    파일이 이름 · 값을 실행 때 바꾸는 장치(globals · locals · vars · setattr · importlib · exec · `builtins` 의 그 이름 · `__dict__` ·
    `__globals__` · `__self__` · `__builtins__` · `sys.modules`(별칭 포함) · 별 import …)를 쓰거나, 짝 ACL 폴더의 어느 파일이 그 장치 ·
    pydantic 의 칸 바꾸기(`model_fields` · `model_rebuild` · `__pydantic_*`)를 쓰거나 메서드 첫 매개변수 `self` · `cls` 의 칸 밖의
    속성을 바꾸거나 짝 폴더 클래스의 보통 메서드를 클래스에서 꺼내면(파일을 건너도 · 못 읽는 파일 포함) 허용 목록 전체를 쓰지 않는다. 묶기는 대입 · 지움 · 매개변수 · def · class · import ·
    `except … as` · `match` 갈래 이름 · 타입 매개변수를 센다.
    남는 한계: `TypeAdapter(<TypedDict · wire>)` 모듈 상수의 `validate_json` 은 받는 쪽 허용 목록 밖이다(붉음 그대로 — 다음 판 후보).
    꼴 C 는 같은 BC 다른 파일의 동적 import(importlib · `__import__` · `sys.modules` 꺼냄)를 보지 않고, 꼴 B 의 표 · 설정 상수는 그릇
    글자에 담아 다른 이름으로 옮겨 고치는 길(깊이 1 이상 — `t = (_T["a"],)`)을 보지 않는다. `getattr(…, "<장치 이름>")` 꼴의 장치
    꺼냄도 보지 않는다. 꼴 C 는 `application/` 밖(framework 등) 파일의 import 를 보지 않는다 — 그 import 는
    check-business-vocabulary #46(«framework 가 application/ 쪽을 import 한다»)이 따로 막는다.
    """

    def __init__(self, mod: ast.Module, base_names: set[str], path: Path | None = None,
                 bc_imports: _BcImports | None = None) -> None:
        self.base_names: set[str] = base_names
        self._bc_imports: _BcImports | None = bc_imports
        self.defs: set[str] = set()
        self.holders: set[str] = set()  # 파일 안에서 값을 담는 속성 이름(`x.a = …` · 클래스 몸통 `a = …`) — 창구를 담았을 수 있다
        self.inside: set[str] = set()
        outside: set[str] = set()
        bound: dict[str, int] = {}  # 파일 안에서 묶인 횟수(대입 · 매개변수 · def)
        for n in ast.walk(mod):
            if isinstance(n, ast.Import):
                for a in n.names:
                    parts: list[str] = a.name.split(".")
                    window: bool = "open_host_service" in parts and "contract" not in parts
                    (self.inside if window else outside).add(a.asname or parts[0])
            elif isinstance(n, ast.ImportFrom):
                local: bool = n.level > 0 or "anticorruption_layer" in (n.module or "").split(".")
                for a in n.names:
                    parts = f"{n.module}.{a.name}".split(".")
                    window = n.level == 0 and "open_host_service" in parts and "contract" not in parts
                    (self.inside if local or window else outside).add(a.asname or a.name)
            elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                self.defs.add(n.name)
                bound[n.name] = bound.get(n.name, 0) + 1
                for item in n.body if isinstance(n, ast.ClassDef) else []:
                    targets: list[ast.expr] = (item.targets if isinstance(item, ast.Assign)
                                               else [item.target] if isinstance(item, ast.AnnAssign) else [])
                    self.holders.update(t.id for t in targets if isinstance(t, ast.Name))
            elif isinstance(n, ast.Attribute) and isinstance(n.ctx, ast.Store):
                self.holders.add(n.attr)
            elif isinstance(n, ast.Name) and not isinstance(n.ctx, ast.Load):
                bound[n.id] = bound.get(n.id, 0) + 1
            elif isinstance(n, ast.arg):
                bound[n.arg] = bound.get(n.arg, 0) + 1
        self.inside |= self.defs
        self.known: set[str] = (outside | set(dir(builtins))) - _REACHING_BUILTINS - self.inside - set(bound)
        for stmt in mod.body:  # 모듈 상수 — 한 번만 묶였고 값을 알려진 바깥으로만 지었다(람다 없음)
            target: ast.expr | None = None
            if isinstance(stmt, ast.Assign) and len(stmt.targets) == 1:
                target = stmt.targets[0]
            elif isinstance(stmt, ast.AnnAssign) and stmt.value is not None:
                target = stmt.target
            if isinstance(target, ast.Name) and bound.get(target.id) == 1 and all(
                    not isinstance(x, ast.Lambda) and (not isinstance(x, ast.Name) or x.id in self.known)
                    for x in ast.walk(stmt.value)):
                self.known.add(target.id)
        self._setup_validation(mod, path, bound)

    def _setup_validation(self, mod: ast.Module, path: Path | None, bound: dict[str, int]) -> None:
        """받은 글 검증 허용 목록의 재료 — wire · 자료 이름 · 자료 별칭 · 모델 짓기 함수 · `type[T]` 매개변수."""
        self.wires: set[str] = set()
        self.data_names: set[str] = set()
        self.data_alias: set[str] = set()
        self.alias_values: dict[str, ast.expr] = {}
        self.factories: set[str] = set()
        self.model_factories: set[str] = set()
        self.factory_constants: set[str] = set()  # 짓기 함수만 읽을 수 있는 모듈 상수(알려진 바깥 · wire 로만 지음)
        self.typed_params: dict[str, set[str]] = {}
        self.pydantic: dict[str, str] = {}  # pydantic 에서 import 한 이름 → 원 이름
        self._module: ast.Module = mod
        self._path: Path | None = path
        self._functions: dict[str, ast.FunctionDef] = {}
        self._makers: set[str] = set()  # create_model 을 (짓기 함수를 거쳐) 부르는 짓기 함수 — 칸 정의를 보기 전
        self._call_sites: dict[str, list[tuple[ast.Call, str | None]]] = {}  # 함수 → (부르기, 그 부르기가 든 최상위 함수)
        self._leaked: set[str] = set()  # 맨 부르기 말고 값으로 쓰인 최상위 함수 이름
        self._parents: dict[int, ast.AST] = {}
        self._constant_values: dict[str, ast.expr] = {}
        self._type_leaves: set[str] = set()
        self._fields_memo: dict[str, bool] = {}
        self._returns_memo: dict[tuple[str, str], tuple[bool, frozenset[tuple[str, str, str]]]] = {}
        self._local_memo: dict[tuple[str, str], tuple[bool, frozenset[tuple[str, str, str]]]] = {}
        self._carrier_memo: dict[tuple[str, str], bool] = {}
        self._table_memo: dict[tuple[str, str], bool] = {}
        self._busy: set[tuple[str, ...]] = set()
        partner: Path | None = _partner_root(path) if path is not None else None
        self._partner: Path | None = partner
        self.allowlist: bool = partner is not None and not _uses_name_device(mod) and not _partner_altered(partner)
        if not self.allowlist:
            return
        binds: dict[str, int] = _bind_counts(mod)
        self._binds: dict[str, int] = binds
        for node in ast.walk(mod):
            for child in ast.iter_child_nodes(node):
                self._parents[id(child)] = node
        contract_names: set[str] = set()
        std_names: set[str] = set()
        imported: dict[str, int] = {}
        window: set[str] = set()
        for n in ast.walk(mod):
            if isinstance(n, ast.Import):
                for a in n.names:
                    name: str = a.asname or a.name.split(".")[0]
                    imported[name] = imported.get(name, 0) + 1
            elif isinstance(n, ast.ImportFrom):
                for a in n.names:
                    name = a.asname or a.name
                    imported[name] = imported.get(name, 0) + 1
                    if n.level == 0 and _window_import(n.module or "", a.name):
                        window.add(name)
        wire_modules: _PartnerWires = _PartnerWires(partner)
        for stmt in mod.body:
            if isinstance(stmt, ast.ImportFrom) and stmt.level == 0 and stmt.module:
                for a in stmt.names:
                    name = a.asname or a.name
                    if imported.get(name) != 1:
                        continue
                    if stmt.module.split(".")[0] == "pydantic":
                        self.pydantic[name] = a.name
                    if binds.get(name) != 1:
                        continue  # import 말고 다른 묶기가 있다(가림)
                    not_data: bool = a.name.endswith(_NOT_DATA_SUFFIXES)
                    if _contract_import(stmt.module) and not not_data:
                        contract_names.add(name)
                        self.data_names.add(name)
                    if a.name in _STD_DATA.get(stmt.module, frozenset()):
                        std_names.add(name)
                        self.data_names.add(name)
                    parts: list[str] = stmt.module.split(".")
                    if (parts[0] == "application" and "domain_layer" in parts and not stmt.module.endswith("_repository")
                            and not not_data and _domain_data_class(path, stmt.module, a.name)):
                        self.data_names.add(name)
            elif isinstance(stmt, ast.ImportFrom) and stmt.level > 0:
                module_file, subs = wire_modules.resolve(path, stmt)
                for a in stmt.names:
                    name = a.asname or a.name
                    target_file: Path | None = subs.get(name) or module_file
                    if (imported.get(name) == 1 and binds.get(name) == 1
                            and target_file is not None and wire_modules.module_ok(target_file)):
                        self.wires.add(name)  # 짝 폴더 안 선언만 있는 wire — import 말고 다시 묶기 · 가림 0
        pydantic_bases: set[str] = {k for k, v in self.pydantic.items()
                                    if v in _PYDANTIC_MODEL_BASES and binds.get(k) == 1}
        typing_of: dict[str, str] = _typing_imports(mod, binds)
        self._typing_of: dict[str, str] = typing_of
        base_leaf: set[str] = {n for n in _PLAIN_TYPE_BUILTINS if n not in binds} | contract_names | std_names
        grew: bool = True
        while grew:  # 같은 파일 wire 클래스 — 다른 같은 파일 wire 를 칸 타입으로 쓰는 것까지(고정점)
            grew = False
            for stmt in mod.body:
                if isinstance(stmt, ast.ClassDef) and binds.get(stmt.name) == 1 and stmt.name not in self.wires:
                    names_in: set[str] = {x.id for x in ast.walk(stmt) if isinstance(x, ast.Name)}
                    if (_wire_class(stmt, pydantic_bases | self.wires, base_leaf | self.wires, typing_of)
                            and not (names_in & window)):
                        self.wires.add(stmt.name)
                        grew = True
        for stmt in mod.body:
            target: ast.expr | None = None
            if isinstance(stmt, ast.Assign) and len(stmt.targets) == 1:
                target = stmt.targets[0]
            elif isinstance(stmt, ast.AnnAssign) and stmt.value is not None:
                target = stmt.target
            if isinstance(target, ast.Name) and bound.get(target.id) == 1 and target.id not in imported and all(
                    not isinstance(x, ast.Lambda) and (not isinstance(x, ast.Name) or x.id in self.known
                                                       or x.id in self.wires or x.id in self.factory_constants)
                    for x in ast.walk(stmt.value)) and not any(isinstance(x, ast.Call) and not (
                        isinstance(x.func, ast.Name) and (x.func.id in self.pydantic or x.func.id in self.wires))
                        for x in ast.walk(stmt.value)):
                self.factory_constants.add(target.id)
                self._constant_values[target.id] = stmt.value
        for stmt in mod.body:  # 자료 타입 별칭 — `X: TypeAlias = …` · `type X = …`
            alias: str | None = None
            value: ast.expr | None = None
            if (isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name)
                    and isinstance(stmt.annotation, ast.Name) and stmt.annotation.id == "TypeAlias"
                    and stmt.value is not None):
                alias, value = stmt.target.id, stmt.value
            elif type(stmt).__name__ == "TypeAlias" and isinstance(stmt.name, ast.Name):
                alias, value = stmt.name.id, stmt.value
            if alias is not None and binds.get(alias) == 1 and self._data_annotation(value, alias=True):
                self.data_alias.add(alias)
                self.alias_values[alias] = value
        self.data_alias |= self.wires  # 상대 wire 모듈에서 온 별칭 이름(`_WireType`)도 자료 별칭이다
        functions: dict[str, ast.FunctionDef] = {
            fn.name: fn for fn in mod.body if isinstance(fn, ast.FunctionDef)
            and binds.get(fn.name) == 1 and fn.name not in imported and not fn.decorator_list}
        self._functions = functions
        called: set[int] = set()
        for top in mod.body:  # 부르는 자리마다 그 부르기가 든 최상위 함수(메서드 · 모듈 수준이면 None)
            owner: str | None = top.name if isinstance(top, ast.FunctionDef) else None
            for n in ast.walk(top):
                if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in functions:
                    self._call_sites.setdefault(n.func.id, []).append((n, owner))
                    called.add(id(n.func))
        self._leaked = {n.id for n in ast.walk(mod) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)
                        and n.id in functions and id(n) not in called}
        self._type_leaves = ({n for n in _PLAIN_TYPE_BUILTINS if n not in binds} | self.wires | self.data_names
                             | self.data_alias)
        creates: dict[str, bool] = {}
        changed: bool = True
        while changed:
            changed = False
            for name, fn in functions.items():
                if name not in self.factories:
                    ok, makes = self._model_factory(fn)
                    if ok:
                        self.factories.add(name)
                        creates[name] = makes
                        changed = True
        reach: dict[str, set[str]] = {n: {c.func.id for c in ast.walk(functions[n]) if isinstance(c, ast.Call)
                                          and isinstance(c.func, ast.Name) and c.func.id in self.factories}
                                      for n in self.factories}
        for n in self.factories:  # 자신이나 부르는 짓기 함수가 create_model 을 부르면 모델 짓기 함수다
            todo: list[str] = [n]
            seen: set[str] = set()
            while todo:
                m: str = todo.pop()
                if m in seen:
                    continue
                seen.add(m)
                todo += list(reach.get(m, ()))
            if any(creates.get(m) for m in seen):
                self._makers.add(n)
        self.model_factories = {n for n in sorted(self._makers) if self._factory_fields_ok(n)}
        dropped: bool = True
        while dropped:  # 서로 부르는 모델 짓기 함수 — 받지 않은 짓기 함수를 부르는 짓기 함수도 받지 않는다
            dropped = False
            for name in sorted(self.model_factories):
                if any(isinstance(c, ast.Call) and isinstance(c.func, ast.Name)
                       and c.func.id in self._makers - self.model_factories for c in ast.walk(functions[name])):
                    self.model_factories.discard(name)
                    dropped = True
        self._collect_typed_params(mod, functions)

    def _carries_class(self, ann: ast.AST | None, seen: set[str] | None = None) -> bool:
        """주석이 클래스를 실어 나를 수 있나 — `type` · pydantic 이름이 직접 또는 별칭 안(별칭의 별칭까지)에 있다."""
        seen = set() if seen is None else seen
        for x in ast.walk(ann) if ann is not None else ():
            if isinstance(x, ast.Name):
                if x.id == "type" or x.id in self.pydantic:
                    return True
                if x.id in self.data_alias and x.id not in self.wires and x.id not in seen:
                    seen.add(x.id)
                    if self._carries_class(self.alias_values.get(x.id), seen):
                        return True
        return False

    def _data_annotation(self, ann: ast.AST | None, alias: bool = False) -> bool:
        """«자료 타입» 주석인가 — 내장 값 · 그릇 · Literal · Optional · Union · Final · Annotated · ClassVar · 같은 BC 도메인
        자료 클래스 · 계약 · 표준 값 이름 · wire · 자료 별칭뿐. 문자열 · Any · object · Callable · Iterator · Generator ·
        Protocol · Sequence · Mapping 은 목록 밖이라 자료가 아니다. `alias`(별칭 값 안)에서는 `type[…]` · pydantic 모델도
        받는다 — 그런 별칭은 «값 자료» 가 아니다(`_carries_class`)."""
        if ann is None or (isinstance(ann, ast.Constant) and isinstance(ann.value, str)):
            return False
        if isinstance(ann, ast.Constant):
            return ann.value is None or ann.value is Ellipsis
        if isinstance(ann, ast.Name):
            if ann.id in _DATA_BUILTINS or ann.id in self.data_names or ann.id in self.data_alias:
                return ann.id != "type" or alias
            if ann.id in self.wires:
                return True
            return alias and self.pydantic.get(ann.id) in _PYDANTIC_MODEL_BASES
        if isinstance(ann, ast.BinOp) and isinstance(ann.op, ast.BitOr):
            return self._data_annotation(ann.left, alias) and self._data_annotation(ann.right, alias)
        if isinstance(ann, ast.Tuple):
            return all(self._data_annotation(e, alias) for e in ann.elts)
        if isinstance(ann, ast.Subscript) and isinstance(ann.value, ast.Name):
            head: str = ann.value.id
            if head == "Literal":
                return True
            if head == "type":
                return self._data_annotation(ann.slice, alias=True)
            if head in _BUILTIN_CONTAINERS or head in _DATA_TYPING:
                return self._data_annotation(ann.slice, alias)
        return False

    def _model_factory(self, fn: ast.FunctionDef) -> tuple[bool, bool]:
        """(같은 파일 모델 짓기 함수로 받나, `create_model` 을 부르나).

        매개변수는 모두 자료 타입 주석 · 기본값은 글자 · `*args` · `**kwargs` 0 · 몸통에서 다시 묶지 않는다. 몸통에 중첩 정의 ·
        람다 · 클래스 · yield · await · global · nonlocal · with 가 없고, 읽는 이름은 매개변수 · 지역 · 알려진 바깥 · wire ·
        짓기 함수 · 자료 이름 · 자료 별칭 · pydantic 이름 · 짓기 함수용 모듈 상수 · `__name__` 뿐이다(창구 쪽 이름은 읽지도
        않는다). 맨 이름 부르기는 `create_model` · `Field` · 내장 몇 · 짓기 함수 · wire · 자료 이름뿐이고, 속성 부르기의 뿌리는
        매개변수 · 지역 · 자료 이름 · wire 뿐이다. `create_model` 에 넘기는 칸 정의는 `_factory_fields_ok` 가 따로 본다.
        """
        a: ast.arguments = fn.args
        params: list[ast.arg] = [*a.posonlyargs, *a.args, *a.kwonlyargs]
        if a.vararg or a.kwarg or not all(self._data_annotation(x.annotation) for x in params):
            return False, False
        if not all(isinstance(d, ast.Constant) for d in [*a.defaults, *(d for d in a.kw_defaults if d is not None)]):
            return False, False
        param_names: set[str] = {x.arg for x in params}
        in_annotation: set[int] = set()
        for n in ast.walk(fn):  # 주석은 이름 검사 밖이다(평가되지 않거나 def 때 한 번)
            for ann in ([n.annotation] if isinstance(n, (ast.AnnAssign, ast.arg)) else []) + (
                    [n.returns] if isinstance(n, ast.FunctionDef) else []):
                if ann is not None:
                    in_annotation |= {id(x) for x in ast.walk(ann)}
        locals_: set[str] = set(_bind_counts(ast.Module(body=fn.body, type_ignores=[])))
        if locals_ & param_names:
            return False, False  # 매개변수를 다시 묶는다(`except … as` · `match` 갈래까지)
        readable: set[str] = (param_names | locals_ | self.known | self.wires | self.factories | self.data_names
                              | self.data_alias | set(self.pydantic) | self.factory_constants | {"__name__"})
        makes: bool = False
        for n in ast.walk(fn):
            if n is not fn and isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef,
                                              ast.Yield, ast.YieldFrom, ast.Await, ast.Global, ast.Nonlocal,
                                              ast.With, ast.AsyncWith, ast.AsyncFor)):
                return False, False
            if id(n) in in_annotation:
                continue
            if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load):
                if n.id not in readable or (n.id in self.inside and n.id not in self.factories | self.wires):
                    return False, False
            if isinstance(n, ast.Call):
                func: ast.expr = n.func
                if isinstance(func, ast.Name):
                    if self.pydantic.get(func.id) == "create_model":
                        makes = True
                    elif not (func.id in _FACTORY_BUILTINS or self.pydantic.get(func.id) == "Field"
                              or func.id in self.factories or func.id in self.wires or func.id in self.data_names):
                        return False, False
                elif isinstance(func, ast.Attribute):
                    root: str | None = _root(func)
                    if root is None or not (root in param_names or root in locals_ or root in self.data_names
                                            or root in self.wires):
                        return False, False
                else:
                    return False, False
        return True, makes

    # ── 꼴 B 의 칸 정의 — 글자 그대로의 타입 식 · 고쳐지지 않는 모듈 상수 표의 첨자 꺼냄에서만 ──────────────
    # 칸 정의 자리(`create_model` 의 칸 키워드 값 · `**` · 그 안의 dict 값)는 짓기 함수 몸통에 글자로 적은 타입 식, 또는 파일 안에서
    # 첨자 대입 · 메서드로 바뀌지 않는 모듈 상수 표의 첨자 꺼냄으로만 짓는다. 짓기 함수 매개변수는 키 고르기 · 칸 이름으로만 쓴다 —
    # 매개변수가 칸 정의 자리에 닿으면 «그 함수를 부르는 자리가 모두 다른 짓기 함수 안이고 그 인자가 같은 꼴» 일 때만 받는다
    # (`needs` 의 (함수, 매개변수, 꼴) — 부르는 자리마다 다시 본다).

    def _factory_fields_ok(self, name: str) -> bool:
        """모델 짓기 함수의 `create_model` 칸 정의 · 예약 칸이 모두 위 꼴이고, 부르는 다른 모델 짓기 함수도 그러한가."""
        if name in self._fields_memo:
            return self._fields_memo[name]
        if ("factory", name) in self._busy:
            return True  # 지금 재는 중 — 그 판정이 부르는 자리까지 모두 보고 정한다
        self._busy.add(("factory", name))
        fn: ast.FunctionDef = self._functions[name]
        needs: set[tuple[str, str, str]] = set()
        ok: bool = True
        for n in ast.walk(fn):
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Name):
                if self.pydantic.get(n.func.id) == "create_model":
                    ok = ok and self._create_model_ok(n, fn, needs)
                elif n.func.id in self._makers and n.func.id != name:
                    ok = ok and self._factory_fields_ok(n.func.id)
        ok = ok and self._needs_met(needs)
        self._busy.discard(("factory", name))
        self._fields_memo[name] = ok
        if not ok:  # «재는 중 = 받음» 으로 잰 중간 값을 버린다
            self._returns_memo.clear()
            self._local_memo.clear()
        return ok

    def _create_model_ok(self, call: ast.Call, fn: ast.FunctionDef, needs: set[tuple[str, str, str]]) -> bool:
        """`create_model(<이름>, …)` — 이름 말고 자리 인자 0 · 예약 칸(`__…`)은 글자 · `__module__=__name__` ·
        `__config__=<고쳐지지 않는 모듈 상수>` · `__base__=<wire>` 뿐 · 칸 키워드 값은 칸 하나 · `**` 는 칸 묶음."""
        if len(call.args) > 1 or any(isinstance(a, ast.Starred) for a in call.args):
            return False
        for k in call.keywords:
            if k.arg is None:
                if not self._field_ok(k.value, _FIELD_DICT, fn, needs):
                    return False
            elif k.arg.startswith("__"):
                v: ast.expr = k.value
                if not (isinstance(v, ast.Constant)
                        or (k.arg == "__module__" and isinstance(v, ast.Name) and v.id == "__name__")
                        or (k.arg == "__config__" and isinstance(v, ast.Name) and v.id in self.factory_constants
                            and self._plain_reads(v.id, config=True) and self._unaltered(v.id))
                        or (k.arg == "__base__" and isinstance(v, ast.Name) and v.id in self.wires)):
                    return False
            elif not self._field_ok(k.value, _FIELD_SPEC, fn, needs):
                return False
        return True

    def _field_ok(self, expr: ast.expr | None, kind: str, fn: ast.FunctionDef | None,
                  needs: set[tuple[str, str, str]]) -> bool:
        """칸 정의 자리의 식이 그 꼴(칸 타입 · 칸 하나 · 칸 묶음)로 글자 그대로의 타입 식 · 고쳐지지 않는 모듈 상수 표의 첨자
        꺼냄에서만 오나. `fn` 이 None 이면 모듈 수준(상수 표의 값)이다."""
        if expr is None:
            return False
        if isinstance(expr, ast.Constant):
            return kind == _FIELD_TYPE and expr.value is None  # 글자 타입 이름은 모듈 이름공간에서 eval 된다
        if isinstance(expr, ast.Name):
            return self._name_field_ok(expr.id, kind, fn, needs)
        if isinstance(expr, ast.IfExp):
            return self._field_ok(expr.body, kind, fn, needs) and self._field_ok(expr.orelse, kind, fn, needs)
        if (isinstance(expr, ast.Call) and isinstance(expr.func, ast.Name) and expr.func.id in self.factories
                and fn is not None and expr.func.id not in self._scope_names(fn)):
            if any(isinstance(a, ast.Starred) for a in expr.args) or any(k.arg is None for k in expr.keywords):
                return False
            if kind in (_FIELD_TYPE, _FIELD_SPEC) and expr.func.id in self._makers:
                return self._factory_fields_ok(expr.func.id)  # 지은 모델은 칸 타입이 된다
            return self._returns_ok(expr.func.id, kind, needs)
        if (isinstance(expr, ast.Subscript) and isinstance(expr.value, ast.Name)
                and (fn is None or expr.value.id not in self._scope_names(fn)) and self._frozen_table(expr.value.id)):
            return self._table_ok(expr.value.id, kind)
        if kind == _FIELD_TYPE:
            return self._type_expr_ok(expr, fn, needs)
        if kind == _FIELD_SPEC:
            if isinstance(expr, ast.Tuple) and len(expr.elts) == 2:
                return self._field_ok(expr.elts[0], _FIELD_TYPE, fn, needs) and self._default_ok(expr.elts[1])
            return self._type_expr_ok(expr, fn, needs)
        if isinstance(expr, ast.Dict):
            return all(self._field_ok(v, _FIELD_DICT if k is None else _FIELD_SPEC, fn, needs)
                       for k, v in zip(expr.keys, expr.values))
        if isinstance(expr, ast.DictComp):
            return self._field_ok(expr.value, _FIELD_SPEC, fn, needs)
        return False

    def _scope_names(self, fn: ast.FunctionDef) -> set[str]:
        """짓기 함수의 매개변수 · 지역 이름."""
        a: ast.arguments = fn.args
        return {x.arg for x in [*a.posonlyargs, *a.args, *a.kwonlyargs]} | set(
            _bind_counts(ast.Module(body=fn.body, type_ignores=[])))

    def _name_field_ok(self, name: str, kind: str, fn: ast.FunctionDef | None, needs: set[tuple[str, str, str]]) -> bool:
        """칸 정의 자리의 이름 — 매개변수면 needs 에 적고, 지역이면 그 지역 칸 묶음을 보고, 모듈 이름이면 맨 타입 · wire ·
        자료 이름 · 자료 별칭만(칸 묶음 자리의 모듈 이름은 받지 않는다 — 표를 통째로 펼치지 않는다)."""
        if fn is not None:
            a: ast.arguments = fn.args
            if name in {x.arg for x in [*a.posonlyargs, *a.args, *a.kwonlyargs]}:
                needs.add((fn.name, name, kind))
                return True
            if name in self._scope_names(fn):
                return self._local_ok(fn, name, kind, needs)
        return kind != _FIELD_DICT and name in self._type_leaves

    def _type_expr_ok(self, expr: ast.expr, fn: ast.FunctionDef | None, needs: set[tuple[str, str, str]]) -> bool:
        """글자 그대로의 타입 식 — 맨 타입 · wire · 자료 이름 · 자료 별칭 · `None`, 그것들을 내장 그릇 · `typing` 의 Optional ·
        Union · 옛 그릇 이름 · Literal(글자만) · `|` 로 묶은 것(`Annotated` · 부르기 · 속성 · 글자 타입 0)."""
        if isinstance(expr, ast.Constant):
            return expr.value is None
        if isinstance(expr, ast.Name):
            return self._name_field_ok(expr.id, _FIELD_TYPE, fn, needs)
        if isinstance(expr, ast.BinOp) and isinstance(expr.op, ast.BitOr):
            return self._type_expr_ok(expr.left, fn, needs) and self._type_expr_ok(expr.right, fn, needs)
        if isinstance(expr, ast.Subscript) and isinstance(expr.value, ast.Name):
            head: str = expr.value.id
            if fn is not None and head in self._scope_names(fn):
                return False
            origin: str | None = self._typing_of.get(head)
            elts: list[ast.expr] = expr.slice.elts if isinstance(expr.slice, ast.Tuple) else [expr.slice]
            if origin == "Literal":
                return all(isinstance(e, ast.Constant) and (e.value is None or isinstance(e.value, (str, int, bool)))
                           for e in elts)
            if (head in _BUILTIN_CONTAINERS and head not in self._binds) or origin in ("Optional", "Union", *_OLD_CONTAINERS):
                return all((isinstance(e, ast.Constant) and e.value is Ellipsis) or self._type_expr_ok(e, fn, needs)
                           for e in elts)
        return False

    def _default_ok(self, expr: ast.expr) -> bool:
        """`(타입, 기본값)` 의 기본값 — 글자, 또는 자리 인자가 글자이고 꼬리표(alias · title · description …) 밖 키워드가 글자인
        pydantic `Field(...)`(`default_factory` 같은 이름 값은 받지 않는다)."""
        if isinstance(expr, ast.Constant):
            return True
        return (isinstance(expr, ast.Call) and isinstance(expr.func, ast.Name) and self.pydantic.get(expr.func.id) == "Field"
                and all(isinstance(a, ast.Constant) for a in expr.args)
                and all(k.arg is not None and (k.arg in _FIELD_LABELS or isinstance(k.value, ast.Constant))
                        for k in expr.keywords))

    def _returns_ok(self, name: str, kind: str, needs: set[tuple[str, str, str]]) -> bool:
        """짓기 함수의 돌려주는 값이 모두 그 꼴인가(돌려주기 없는 끝 = None)."""
        key: tuple[str, str] = (name, kind)
        if key not in self._returns_memo:
            if ("returns", name, kind) in self._busy:
                return False
            self._busy.add(("returns", name, kind))
            fn: ast.FunctionDef = self._functions[name]
            sub: set[tuple[str, str, str]] = set()
            ok: bool = all(self._field_ok(r.value if r.value is not None else ast.Constant(value=None), kind, fn, sub)
                           for r in ast.walk(fn) if isinstance(r, ast.Return))
            self._busy.discard(("returns", name, kind))
            self._returns_memo[key] = (ok, frozenset(sub))
        ok, sub = self._returns_memo[key]
        needs |= sub
        return ok

    def _local_ok(self, fn: ast.FunctionDef, name: str, kind: str, needs: set[tuple[str, str, str]]) -> bool:
        """짓기 함수 지역 칸 묶음 — 묶기는 단순 대입 · 주석 대입뿐이고 그 값이 칸 묶음, 첨자 대입 `x[k] = v` 의 v 는 칸 하나,
        읽기는 칸 정의 자리 · `{**x}` · 첨자 대입 바탕 · 다른 짓기 함수의 실어 나르기 칸뿐(메서드 · 덧셈 대입 · 지움 0).
        칸 타입 · 칸 하나 꼴의 지역은 받지 않는다."""
        if kind != _FIELD_DICT:
            return False
        key: tuple[str, str] = (fn.name, name)
        if key not in self._local_memo:
            if ("local", fn.name, name) in self._busy:
                return False
            self._busy.add(("local", fn.name, name))
            body: ast.Module = ast.Module(body=fn.body, type_ignores=[])
            sub: set[tuple[str, str, str]] = set()
            simple: int = 0
            ok: bool = True
            for n in ast.walk(body):
                if not ok:
                    break
                parent: ast.AST | None = self._parents.get(id(n))
                if isinstance(n, ast.Name) and n.id == name:
                    if isinstance(n.ctx, ast.Load):
                        ok = self._carried_load_ok(n, allow_store=True)
                    elif ((isinstance(parent, ast.Assign) and len(parent.targets) == 1 and parent.targets[0] is n)
                          or (isinstance(parent, ast.AnnAssign) and parent.target is n and parent.value is not None)):
                        simple += 1
                        ok = self._field_ok(parent.value, _FIELD_DICT, fn, sub)
                    else:
                        ok = False
                elif (isinstance(n, ast.Subscript) and not isinstance(n.ctx, ast.Load) and isinstance(n.value, ast.Name)
                      and n.value.id == name):
                    ok = (isinstance(parent, ast.Assign) and len(parent.targets) == 1 and parent.targets[0] is n
                          and self._field_ok(parent.value, _FIELD_SPEC, fn, sub))
            ok = ok and simple >= 1 and simple == _bind_counts(body).get(name, 0)
            self._busy.discard(("local", fn.name, name))
            self._local_memo[key] = (ok, frozenset(sub))
        ok, sub = self._local_memo[key]
        needs |= sub
        return ok

    def _carried_load_ok(self, node: ast.Name, allow_store: bool) -> bool:
        """칸 묶음을 실어 나르는 이름의 읽기 자리 — `create_model(**x)` · `{**x}` · 다른 짓기 함수의 실어 나르기 칸 ·
        (지역이면) 첨자 대입 바탕 `x[k] = v`."""
        parent: ast.AST | None = self._parents.get(id(node))
        if isinstance(parent, ast.keyword):
            call: ast.AST | None = self._parents.get(id(parent))
            if not isinstance(call, ast.Call) or not isinstance(call.func, ast.Name):
                return False
            if parent.arg is None:
                return self.pydantic.get(call.func.id) == "create_model"
            return call.func.id in self.factories and self._pure_carrier(call.func.id, parent.arg)
        if isinstance(parent, ast.Dict):
            return any(k is None and v is node for k, v in zip(parent.keys, parent.values))
        if isinstance(parent, ast.Call) and isinstance(parent.func, ast.Name) and parent.func.id in self.factories:
            positional: list[ast.arg] = [*self._functions[parent.func.id].args.posonlyargs,
                                         *self._functions[parent.func.id].args.args]
            index: int = next((i for i, a in enumerate(parent.args) if a is node), -1)
            return 0 <= index < len(positional) and self._pure_carrier(parent.func.id, positional[index].arg)
        return (allow_store and isinstance(parent, ast.Subscript) and parent.value is node
                and isinstance(parent.ctx, ast.Store))

    def _pure_carrier(self, name: str, param: str) -> bool:
        """그 짓기 함수가 그 매개변수를 칸 묶음으로 실어 나르기만 하나(읽기가 모두 `_carried_load_ok` 자리 · 첨자 대입 0) —
        넘겨받은 지역 칸 묶음을 거기서 바꾸지 못하게."""
        key: tuple[str, str] = (name, param)
        if key not in self._carrier_memo:
            if ("carrier", name, param) in self._busy:
                return False
            self._busy.add(("carrier", name, param))
            fn: ast.FunctionDef = self._functions[name]
            self._carrier_memo[key] = all(
                self._carried_load_ok(n, allow_store=False) for n in ast.walk(ast.Module(body=fn.body, type_ignores=[]))
                if isinstance(n, ast.Name) and n.id == param)
            self._busy.discard(("carrier", name, param))
        return self._carrier_memo[key]

    def _frozen_table(self, name: str) -> bool:
        """모듈 상수 표(dict · tuple · list 글자)이고 파일 안에서 첨자 꺼냄 · `in` 견줌 말고 다른 읽기가 없고(`_plain_reads`)
        고쳐지지 않나(`_unaltered`)."""
        if name not in self.factory_constants or not isinstance(self._constant_values.get(name),
                                                                 (ast.Dict, ast.Tuple, ast.List)):
            return False
        return self._plain_reads(name) and self._unaltered(name)

    def _plain_reads(self, name: str, config: bool = False) -> bool:
        """모듈 상수의 맨 이름 읽기가 첨자 꺼냄 · `in` 견줌뿐인가(`config` 면 `create_model(…, __config__=이름)` 자리도) — 그릇
        글자 · 함수 기본값 · 다른 이름에 담아 옮겨 고치는 길(깊이 0)을 막는다."""
        makers: set[str] = {k for k, v in self.pydantic.items() if v == "create_model"}
        for n in ast.walk(self._module):
            if isinstance(n, ast.Name) and n.id == name and isinstance(n.ctx, ast.Load):
                parent: ast.AST | None = self._parents.get(id(n))
                if (isinstance(parent, ast.Subscript) and parent.value is n) or (
                        isinstance(parent, ast.Compare) and any(isinstance(op, (ast.In, ast.NotIn)) for op in parent.ops)):
                    continue
                call: ast.AST | None = self._parents.get(id(parent)) if isinstance(parent, ast.keyword) else None
                if (config and isinstance(parent, ast.keyword) and parent.arg == "__config__" and isinstance(call, ast.Call)
                        and isinstance(call.func, ast.Name) and call.func.id in makers):
                    continue
                return False
        return True

    def _unaltered(self, name: str) -> bool:
        """모듈 상수(표 · `__config__` 설정)가 파일 안에서 고쳐지지 않나 — 그 이름의 읽기마다 이름에서 시작하는 첨자 사슬이 모두
        읽기이고(`_T["a"]["x"] = …` · `del _T["a"]` 0), 사슬 끝(`IfExp` · `and` · `or` 는 건너 본다)이 속성(메서드 · 칸) · 대입 ·
        덧셈 대입 · `:=` · 반복 · with · 펼치기 · 돌려주기 · 람다 · 부르는 함수 자리로 가지 않고, 부르기 인자면 그 부르기가
        `create_model` · 짓기 함수일 때만. 그릇 글자에 담아 다른 이름으로 옮겨 고치는 길은 보지 않는다(한계)."""
        makers: set[str] = self.factories | {k for k, v in self.pydantic.items() if v == "create_model"}
        for n in ast.walk(self._module):
            if not (isinstance(n, ast.Name) and n.id == name and isinstance(n.ctx, ast.Load)):
                continue
            top: ast.AST = n
            parent: ast.AST | None = self._parents.get(id(n))
            while True:
                if isinstance(parent, ast.Subscript) and parent.value is top:
                    if not isinstance(parent.ctx, ast.Load):
                        return False  # 사슬 첨자 대입 · 지움
                elif not (isinstance(parent, ast.BoolOp) or (isinstance(parent, ast.IfExp) and parent.test is not top)):
                    break
                top, parent = parent, self._parents.get(id(parent))
            if isinstance(parent, (ast.Attribute, ast.Assign, ast.AnnAssign, ast.AugAssign, ast.NamedExpr, ast.For,
                                   ast.AsyncFor, ast.comprehension, ast.withitem, ast.Starred, ast.Return, ast.Yield,
                                   ast.YieldFrom, ast.Await, ast.Lambda)):
                return False
            call: ast.AST | None = self._parents.get(id(parent)) if isinstance(parent, ast.keyword) else parent
            if isinstance(call, ast.Call) and (call.func is top or not (isinstance(call.func, ast.Name)
                                                                        and call.func.id in makers)):
                return False
        return True

    def _table_ok(self, name: str, kind: str) -> bool:
        """모듈 상수 표의 값이 모두 그 꼴인가(키는 묻지 않는다)."""
        key: tuple[str, str] = (name, kind)
        if key not in self._table_memo:
            table: ast.expr = self._constant_values[name]
            values: list[ast.expr] = table.values if isinstance(table, ast.Dict) else list(table.elts)
            self._table_memo[key] = bool(values) and all(self._field_ok(v, kind, None, set()) for v in values)
        return self._table_memo[key]

    def _needs_met(self, needs: set[tuple[str, str, str]]) -> bool:
        """칸 정의 자리에 닿은 매개변수마다 — 그 함수가 값으로 새지 않고, 부르는 자리가 하나 이상이며 모두 다른 짓기 함수 안이고,
        그 칸 인자가 같은 꼴인가(그 인자가 다시 매개변수에 닿으면 이어서 본다)."""
        done: set[tuple[str, str, str]] = set()
        todo: list[tuple[str, str, str]] = list(needs)
        while todo:
            item: tuple[str, str, str] = todo.pop()
            if item in done:
                continue
            done.add(item)
            name, param, kind = item
            sites: list[tuple[ast.Call, str | None]] = self._call_sites.get(name, [])
            if name in self._leaked or not sites:
                return False
            for call, owner in sites:
                if owner is None or owner not in self.factories:
                    return False
                if any(isinstance(a, ast.Starred) for a in call.args) or any(k.arg is None for k in call.keywords):
                    return False
                positional: list[ast.arg] = [*self._functions[name].args.posonlyargs, *self._functions[name].args.args]
                index: int = next((i for i, a in enumerate(positional) if a.arg == param), -1)
                arg: ast.expr | None = (call.args[index] if 0 <= index < len(call.args)
                                        else next((k.value for k in call.keywords if k.arg == param), None))
                sub: set[tuple[str, str, str]] = set()
                if arg is None or not self._field_ok(arg, kind, self._functions[owner], sub):
                    return False
                todo.extend(sub - done)
        return True

    def _collect_typed_params(self, mod: ast.Module, functions: dict[str, ast.FunctionDef]) -> None:
        """꼴 C — `_` 로 시작하는 함수의 `type[T]`(T 의 바운드 = pydantic 모델) · `type[<wire>]` 매개변수를 함수마다 모은다(파일
        안 부르는 자리 기준 — 다른 파일의 import 는 받을 때 `_BcImports.private` 가 본다)."""
        old_bounds: dict[str, str] = {}
        for stmt in mod.body:  # 옛 꼴 `T = TypeVar("T", bound=…)`
            if (isinstance(stmt, ast.Assign) and len(stmt.targets) == 1 and isinstance(stmt.targets[0], ast.Name)
                    and isinstance(stmt.value, ast.Call) and isinstance(stmt.value.func, ast.Name)
                    and stmt.value.func.id == "TypeVar"):
                for k in stmt.value.keywords:
                    if k.arg == "bound" and isinstance(k.value, ast.Name):
                        old_bounds[stmt.targets[0].id] = k.value.id
        calls: dict[str, list[ast.Call]] = {name: [c for c, _ in self._call_sites.get(name, [])] for name in functions}
        for name, fn in functions.items():
            if not name.startswith("_") or name in self._leaked or not calls[name]:
                continue
            bounds: dict[str, str] = dict(old_bounds)
            for tp in getattr(fn, "type_params", None) or []:
                bound_name: ast.expr | None = getattr(tp, "bound", None)
                if isinstance(bound_name, ast.Name):
                    bounds[tp.name] = bound_name.id
            a: ast.arguments = fn.args
            params: list[ast.arg] = [*a.posonlyargs, *a.args]
            rebound: dict[str, int] = _bind_counts(ast.Module(body=fn.body, type_ignores=[]))
            for i, param in enumerate(params):
                ann: ast.expr | None = param.annotation
                if not (isinstance(ann, ast.Subscript) and isinstance(ann.value, ast.Name) and ann.value.id == "type"
                        and isinstance(ann.slice, ast.Name)):
                    continue
                inner: str = ann.slice.id
                if not (self.pydantic.get(bounds.get(inner, "")) in _PYDANTIC_MODEL_BASES or inner in self.wires):
                    continue
                if i >= len(params) - len(a.defaults) or param.arg in rebound:
                    continue  # 기본값이 있거나 몸통에서 다시 묶는다
                if all(self._passes_wire(c, i, param.arg) for c in calls[name]):
                    self.typed_params.setdefault(name, set()).add(param.arg)

    def _passes_wire(self, call: ast.Call, index: int, param: str) -> bool:
        """이 부르기가 그 칸에 wire 클래스 이름을 넘기나(`*` · `**` 펼치기 0)."""
        if any(isinstance(x, ast.Starred) for x in call.args) or any(k.arg is None for k in call.keywords):
            return False
        got: ast.expr | None = call.args[index] if index < len(call.args) else next(
            (k.value for k in call.keywords if k.arg == param), None)
        return isinstance(got, ast.Name) and got.id in self.wires

    def _validation_nodes(self, node: ast.Try, encl: ast.FunctionDef | ast.AsyncFunctionDef | None) -> set[int]:
        """try 몸통에서 «안 돈다» 로 받는 마디(id) — `model_validate_json` 부르기와 그 받는 쪽이 A · B · C 일 때만."""
        out: set[int] = set()
        if not self.allowlist:
            return out
        data_params: set[str] = set()
        typed: set[str] = set()
        if encl is not None:
            a: ast.arguments = encl.args
            positional: list[ast.arg] = [*a.posonlyargs, *a.args]
            defaulted: set[str] = {x.arg for x in positional[len(positional) - len(a.defaults):]} if a.defaults else set()
            defaulted |= {x.arg for x, d in zip(a.kwonlyargs, a.kw_defaults) if d is not None}
            rebound: dict[str, int] = _bind_counts(ast.Module(body=encl.body, type_ignores=[]))
            data_params = {x.arg for x in [*positional, *a.kwonlyargs] if self._data_annotation(x.annotation)
                           and not self._carries_class(x.annotation) and x.arg not in defaulted and x.arg not in rebound}
            if (self._functions.get(encl.name) is encl and encl.name in self.typed_params  # 같은 이름의 메서드가 아니라 그 최상위 함수
                    and self._bc_imports is not None and self._path is not None
                    and self._bc_imports.private(self._path, encl.name)):
                typed = self.typed_params[encl.name]
        for n in ast.walk(ast.Module(body=node.body, type_ignores=[])):
            if not (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr in _TEXT_VALIDATORS):
                continue
            receiver: ast.expr = n.func.value
            if isinstance(receiver, ast.Name) and (receiver.id in typed or receiver.id in self.wires):
                out |= {id(n), id(receiver)}
            elif (isinstance(receiver, ast.Call) and isinstance(receiver.func, ast.Name)
                  and receiver.func.id in self.model_factories
                  and all((isinstance(x, ast.Name) and x.id in data_params) or isinstance(x, ast.Constant)
                          for x in [*receiver.args, *(k.value for k in receiver.keywords)])
                  and all(k.arg is not None for k in receiver.keywords)):
                out |= {id(n), id(receiver), id(receiver.func)}
        return out

    def may_run_window(self, node: ast.Try, encl: ast.FunctionDef | ast.AsyncFunctionDef | None = None) -> bool:
        approved: set[int] = self._validation_nodes(node, encl)
        stack: list[ast.AST] = list(node.body)
        while stack:
            n: ast.AST = stack.pop()
            if isinstance(n, ast.Try) and _covers_base(n, self.base_names) and not _reraises(n):
                stack.extend([*n.handlers, *n.orelse, *n.finalbody])  # 몸통의 창구 예외는 안쪽 try 에서 끝난다
                continue
            if id(n) in approved:  # 받은 글 검증 부르기 · 그 받는 쪽 — 인자와 받는 쪽 안만 더 본다
                if isinstance(n, ast.Call):
                    stack.extend([*n.args, *(k.value for k in n.keywords)])
                    if isinstance(n.func, ast.Attribute):
                        stack.append(n.func.value)
                continue
            if self._runs(n):
                return True
            stack.extend(ast.iter_child_nodes(n))
        return False

    def _runs(self, n: ast.AST) -> bool:
        """이 마디에서 «알려진 바깥» 밖의 코드가 돌 수 있나."""
        if isinstance(n, ast.Name):
            return n.id in self.inside
        if isinstance(n, ast.Attribute):  # 메서드 · property · 담아 둔 창구(콜백) — 매개변수 · 지역 · 받은 값의 칸은 자료로 본다
            return n.attr in self.defs or n.attr in self.holders or _root(n) in ("self", "cls")
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in _CONSUMING_BUILTINS and any(
                isinstance(a, ast.Name) and a.id not in self.known for a in [*n.args, *(k.value for k in n.keywords)]):
            return True
        ran: ast.expr | None = (n.func if isinstance(n, ast.Call) else n.context_expr if isinstance(n, ast.withitem)
                                else n.iter if isinstance(n, (ast.For, ast.AsyncFor, ast.comprehension))
                                else n.value if isinstance(n, (ast.Await, ast.YieldFrom)) else None)
        return ran is not None and _root(ran) not in self.known


def _check_acl(acl: Path, bc: Path, bc_rel: Path, out: Findings) -> set[str]:
    for cache in (_PARTNER_ALTERED, _DOMAIN_DATA):
        cache.clear()  # 받은 글 검증 판정 재료는 부를 때의 디스크로만 잰다
    bc_imports: _BcImports = _BcImports(bc)  # 꼴 C 가 처음 물을 때 이 BC 프로덕션 파일을 한 번 읽는다
    rel0 = bc_rel / acl.relative_to(bc)
    dirs, files = _entries(acl)
    for f in files:
        if f.name != "__init__.py":
            out.add("#361", rel0 / f.name, "`anticorruption_layer/` 아래는 상대 BC 하나 = 폴더 하나다 — 평면 파일을 두지 않는다")
    partners: set[str] = set()
    for d in dirs:
        partners.add(d.name)
        # 어댑터 칸은 동명 폴더 승격 가능 — 본체는 파일 칸과 동격이고, 승격 폴더의
        # 부품도 import 검사(#473) 대상이다(격리 규칙은 폴더 전체가 주어다).
        scan: "list[tuple[Path, bool]]" = [(f, True) for f in checker_target.adapter_implementations(d)]
        for sub in sorted(p for p in d.iterdir() if p.is_dir()):
            body = sub / f"{sub.name}.py"
            if body.is_file():
                scan.extend((f, False) for f in sorted(sub.glob("*.py")) if f != body)
        for f, is_slot in scan:
            if f.name == "__init__.py":
                continue
            rel = rel0 / d.name / f.relative_to(d)
            mod = _parse(f)
            if mod is None:
                continue
            expected_prefix = _camel(d.name)
            if is_slot:
                for cls in (n for n in mod.body if isinstance(n, ast.ClassDef) and not n.name.startswith("_")):
                    if not cls.name.endswith("Adapter"):
                        out.add("#363", rel, f"ACL 어댑터 클래스 이름은 `<Bc><Capability>Adapter` 다 — `{cls.name}`")
                    elif not cls.name.startswith(expected_prefix):
                        out.add("#363", rel, f"ACL 어댑터 이름은 상대 BC(`{expected_prefix}`)로 시작한다 — `{cls.name}`")
            uses_ohs = any(
                level == 0 and "open_host_service" in p.split(".")
                for _n, p, level in _imports(mod)
            )
            if not uses_ohs:
                continue
            base_names: set[str] = set()
            for node in ast.walk(mod):
                if isinstance(node, ast.ImportFrom) and node.module and "published_error" in node.module:
                    base_names.update(a.asname or a.name for a in node.names)
            if not base_names:
                out.add("#473", rel, "ACL 어댑터는 상대 창구의 «기저 예외»를 반드시 잡는다 — 기저(`*_published_error`) import 가 없다")
                continue
            reach: _WindowTry | None = None  # 기저를 안 잡는 try 가 있을 때만 짓는다
            enclosing: dict[int, ast.FunctionDef | ast.AsyncFunctionDef] = _enclosing_functions(mod)
            for node, owner in _tries(mod, ""):
                if _covers_base(node, base_names):
                    continue
                reach = reach or _WindowTry(mod, base_names, f, bc_imports)
                if reach.may_run_window(node, enclosing.get(id(node))):
                    out.add("#473", f"{rel}:{node.lineno}",
                            "try 의 마지막 except 에 상대 창구의 기저 예외가 있어야 한다(#167 짝 — 둘이 닫혀야 약속이 선다)"
                            f" — 상대 창구가 돌 수 있는 try · `{owner or '모듈'}`")
    return partners


# ── 그 밖 — #14 · #110 · #113 · #117 · #146 · #291 · #292 · #364 · #431 · #347 ──

def _check_ports(bc: Path, bc_rel: Path, container_bcs: set[str], out: Findings) -> None:
    port = bc / "application_layer" / "port"
    if not port.is_dir():
        return
    for p in sorted(port.rglob("*")):
        rel_parts = p.relative_to(port).parts
        if set(rel_parts) & SKIP_DIRS:
            continue
        tokens = set(p.name.removesuffix(".py").split("_"))
        if tokens & (container_bcs - {bc.name}):
            out.add("#364", bc_rel / p.relative_to(bc), "포트는 «필요»(capability)로 이름 붙는다 — 포트 이름에 공급자 BC 이름을 넣지 않는다")


def _cross_bc_port_names(acl: Path | None) -> set[str]:
    """ACL 어댑터가 구현(import)하는 자기 BC 포트 클래스 이름 — «크로스-BC 포트»의 정의."""
    names: set[str] = set()
    if acl is None:
        return names
    for f in acl.rglob("*.py"):
        mod = _parse(f)
        if mod is None:
            continue
        ctor_only: set[str] = _constructor_only_port_names(mod)
        for node in ast.walk(mod):
            if isinstance(node, ast.ImportFrom) and node.module and "port" in node.module.split("."):
                names.update(a.asname or a.name for a in node.names
                             if a.name.endswith("Port") and (a.asname or a.name) not in ctor_only)
    return names


def _constructor_only_port_names(mod: ast.Module) -> set[str]:
    """`__init__` 매개변수 주석과 그 `self.<칸>: <포트> = <매개변수>` 대입 주석 안에서만 쓰인 이름 — 어댑터가 구현하는 포트가 아니라
    주입받은 의존이다(파일마다 판정 — 다른 어댑터가 상속하거나 `returns` 로 쓰면 그 파일에서 #14 로 살아난다)."""
    allowed: set[int] = set()
    for fn in ast.walk(mod):
        if not (isinstance(fn, ast.FunctionDef) and fn.name == "__init__" and fn.args.args):
            continue
        params = [*fn.args.posonlyargs, *fn.args.args, *fn.args.kwonlyargs]
        names = {arg.arg for arg in params}
        for arg in params:
            if arg.annotation is not None:
                allowed.update(id(sub) for sub in ast.walk(arg.annotation))
        receiver = (fn.args.posonlyargs + fn.args.args)[0].arg
        for statement in fn.body:
            if (isinstance(statement, ast.AnnAssign) and isinstance(statement.target, ast.Attribute)
                    and isinstance(statement.target.value, ast.Name) and statement.target.value.id == receiver
                    and isinstance(statement.value, ast.Name) and statement.value.id in names):
                allowed.update(id(sub) for sub in ast.walk(statement.annotation))
    uses: dict[str, list[ast.Name]] = {}
    for node in ast.walk(mod):
        if isinstance(node, ast.Name):
            uses.setdefault(node.id, []).append(node)
    return {name for name, found in uses.items() if all(id(use) in allowed for use in found)}


def _check_uow_cross(bc: Path, bc_rel: Path, cross_ports: set[str], out: Findings) -> None:
    if not cross_ports:
        return
    app = bc / "application_layer"
    if not app.is_dir():
        return
    # 유스케이스 칸은 동명 폴더 승격 가능 — 부품의 `with uow:` 크로스 호출도 같은 규칙이라
    # 승격 폴더(본체 실존) 내부 .py 전체를 스캔에 넣는다.
    targets: "set[Path]" = set(app.rglob("*_use_case.py"))
    for d in app.rglob("*_use_case"):
        if d.is_dir() and (d / f"{d.name}.py").is_file():
            targets.update(d.rglob("*.py"))
    for f in sorted(targets):
        mod = _parse(f)
        if mod is None:
            continue
        attr_names: set[str] = set()
        for node in ast.walk(mod):
            if isinstance(node, ast.FunctionDef) and node.name == "__init__":
                for arg in node.args.posonlyargs + node.args.args + node.args.kwonlyargs:
                    if _ann_idents(arg.annotation) & cross_ports:
                        attr_names.update({arg.arg, f"_{arg.arg}"})
        if not attr_names:
            continue
        for node in ast.walk(mod):
            if not isinstance(node, ast.With):
                continue
            ctx_text = " ".join(ast.dump(item.context_expr) for item in node.items).lower()
            if "unit_of_work" not in ctx_text and "uow" not in ctx_text:
                continue
            for sub in ast.walk(node):
                if (
                    isinstance(sub, ast.Call)
                    and isinstance(sub.func, ast.Attribute)
                    and isinstance(sub.func.value, ast.Attribute)
                    and sub.func.value.attr in attr_names
                ):
                    out.add("#14", bc_rel / f.relative_to(bc), f"`with unit_of_work:` 블록 «안»에서 크로스-BC 포트(`{sub.func.value.attr}`)를 부르면 위반이다")
                    break


def _check_api_controllers(bc: Path, bc_rel: Path, out: Findings) -> None:
    for driving in ("driving_layer",):
        api = bc / driving / "api"
        if not api.is_dir():
            continue
        for f in sorted((bc / driving).rglob("api_router.py")):
            if f.parent != api:
                out.add("#113", bc_rel / f.relative_to(bc), "등록 파일은 `api/` 바로 밑에 둔다")
        for f in sorted(api.rglob("*_controller.py")):
            mod = _parse(f)
            if mod is None:
                continue
            for node in mod.body:
                if not isinstance(node, ast.ClassDef):
                    continue
                for deco in node.decorator_list:
                    target = deco.func if isinstance(deco, ast.Call) else deco
                    nm = target.attr if isinstance(target, ast.Attribute) else getattr(target, "id", "")
                    if nm != "api_controller":
                        continue
                    kwargs = {k.arg for k in deco.keywords} if isinstance(deco, ast.Call) else set()
                    ok = isinstance(deco, ast.Call) and any(
                        k.arg == "auto_import" and isinstance(k.value, ast.Constant) and k.value.value is False
                        for k in deco.keywords
                    )
                    if not ok:
                        out.add("#110", bc_rel / f.relative_to(bc), f"`@api_controller(..., auto_import=False)` 로 자동 등록을 끈다 — `{node.name}`")


def _check_exception_spots(bc: Path, bc_rel: Path, out: Findings) -> None:
    dl = bc / "domain_layer"
    if (dl / "exception.py").is_file():
        out.add("#291", bc_rel / "domain_layer" / "exception.py", "BC 바로 밑 `domain_layer/exception.py` 를 두지 않는다 — 도메인 예외의 자리는 애그리거트 밑 `exception/` 과 공유 개념의 `shared_value_object/` 둘이다(#657)")
    if (dl / "exception").is_dir():
        out.add("#292", bc_rel / "domain_layer" / "exception", "예외의 자리는 넷으로 갈린다 — 한 애그리거트 업무 규칙은 `domain_layer/<aggregate>/exception/` · 여러 애그리거트가 함께 쓰는 개념은 `shared_value_object/`(#657) · 남에게 공개하는 실패는 OHS `contract/exception/` · 바깥 행위자는 `port/<capability>/exception.py` 다")
    app = bc / "application_layer"
    if app.is_dir():
        for p in sorted(app.rglob("*")):
            rp = p.relative_to(app).parts
            if set(rp) & SKIP_DIRS or (rp and rp[0] == "port"):
                continue
            if (p.is_file() and p.name == "exception.py") or (p.is_dir() and p.name == "exception"):
                # 승격 부품에도 적용 — 예외 자리는 규범 전역·2026-09-01
                out.add("#292", bc_rel / p.relative_to(bc), "application 쪽 예외 자리는 `port/<capability>/exception.py`(바깥 행위자의 죽음)뿐이다")
        _check_exception_classes(bc, bc_rel, app, out)


_APP_EXCEPTION_CLASS_FIX: str = (
    "예외의 자리는 넷(애그리거트 `exception/` · `shared_value_object/` · OHS `contract/exception/` · 바깥 행위자의 죽음은 "
    "`port/<capability>/exception.py`)이다 — 한 유스케이스의 실패도 판정이면 도메인 예외로 두고, 그 값을 창구 · "
    "컨트롤러가 보여야 하면 설계에서 승인한 사건 값 칸으로 옮긴다"
)


def _check_exception_classes(bc: Path, bc_rel: Path, app: Path, out: Findings) -> None:
    """#292 를 클래스로도 본다 — `application_layer/` 모듈 맨 위 클래스 가운데 기반 사슬이 Exception · Error 에 닿는 것.

    `port/` · 시험 · 이미 이름(`exception.py` · `exception/`)으로 걸린 자리 안은 보지 않는다. 앞 `_` 사설 클래스는
    모듈 밖 제품 모듈이 import 할 때만 센다 — 같은 유스케이스 칸 승격 폴더의 형제 모듈은 빼고(그 폴더
    `__init__.py` 의 재수출은 바깥 공개라 센다), 시험만 import 하면 세지 않는다. import 는 그 BC 안 모듈만 본다.
    """
    importers: "list[tuple[Path, ast.Module]] | None" = None
    for p in sorted(app.rglob("*.py")):
        rp = p.relative_to(app).parts
        if set(rp) & SKIP_DIRS or rp[0] == "port" or "exception" in rp[:-1] or p.name == "exception.py":
            continue
        rel = bc_rel / p.relative_to(bc)
        if checker_target.is_test_path(rel):
            continue
        mod = _parse(p)
        if mod is None:
            continue
        classes = [n for n in mod.body if isinstance(n, ast.ClassDef)]
        declared = {c.name: c for c in classes}
        for cls in classes:
            if not checker_target.exception_based(cls, declared):
                continue
            where = f"{rel.as_posix()}:{cls.lineno}"
            if not cls.name.startswith("_"):
                out.add("#292", where, f"예외 클래스 `{cls.name}` 가 application 층 모듈에 있다. {_APP_EXCEPTION_CLASS_FIX}")
                continue
            if importers is None:
                importers = _product_modules(bc, bc_rel)
            folder_parts = checker_target.use_case_parts(p.parent.parent / f"{p.parent.name}.py")
            own = set(folder_parts) if p in folder_parts else {p}
            users = [f for f, m in importers
                     if f not in own and _imports_private_class(f, m, p, cls.name, bc.parent.parent)]
            if users:
                shown = " · ".join(f"`{(bc_rel / u.relative_to(bc)).as_posix()}`" for u in users)
                out.add("#292", where, f"사설 예외 클래스 `{cls.name}` 를 모듈 밖 제품 코드({shown})가 import 한다 — "
                                       f"바깥이 잡으면 사설 이름이어도 예외 자리 규칙을 따른다. {_APP_EXCEPTION_CLASS_FIX}")


def _product_modules(bc: Path, bc_rel: Path) -> "list[tuple[Path, ast.Module]]":
    """BC 안 시험 아닌 `.py` 와 그 구문 트리 — 파싱되지 않는 파일은 뺀다."""
    out: "list[tuple[Path, ast.Module]]" = []
    for f in sorted(bc.rglob("*.py")):
        rel = f.relative_to(bc)
        if set(rel.parts) & SKIP_DIRS or checker_target.is_test_path(bc_rel / rel):
            continue
        mod = _parse(f)
        if mod is not None:
            out.append((f, mod))
    return out


def _import_base(importer: Path, level: int, module: "str | None", root: Path) -> Path:
    """`from <module> import …` 이 가리키는 경로(확장자 없음) — 절대 경로는 `root`(BC 컨테이너의 부모) 기준."""
    base = root
    if level > 0:
        base = importer.parent
        for _ in range(level - 1):
            base = base.parent
    return base.joinpath(*module.split(".")) if module else base


def _imports_private_class(importer: Path, mod: ast.Module, owner: Path, name: str, root: Path) -> bool:
    """`importer` 가 `owner` 모듈의 `name` 을 들이는가 — `from <owner> import name` 이거나, 모듈 `owner` 를 들여
    `<모듈>.name` 으로 읽는다."""
    stem = owner.parent if owner.name == "__init__.py" else owner.with_suffix("")
    module_imported = False
    for node in ast.walk(mod):
        if isinstance(node, ast.ImportFrom):
            base = _import_base(importer, node.level, node.module, root)
            if base == stem and any(a.name == name for a in node.names):
                return True
            module_imported = module_imported or any(base / a.name == stem for a in node.names)
        elif isinstance(node, ast.Import):
            module_imported = module_imported or any(root.joinpath(*a.name.split(".")) == stem for a in node.names)
    return module_imported and any(isinstance(n, ast.Attribute) and n.attr == name for n in ast.walk(mod))


def _check_banned_entrance_name(bc: Path, bc_rel: Path, out: Findings) -> None:
    for spot in (bc / "published_service", bc / "driving_layer" / "published_service"):
        if spot.is_dir():
            out.add("#146", bc_rel / spot.relative_to(bc), "타 BC 입구는 `driving_layer/open_host_service/` 다 — `published_service/` 칸을 만들지 않는다")


def _check_error_code_containers(bc: Path, bc_rel: Path, out: Findings) -> None:
    containers: list[Path] = []
    for f in sorted(bc.rglob("*.py")):
        rp = f.relative_to(bc).parts
        if set(rp) & SKIP_DIRS or rp[0] == "test":
            continue
        mod = _parse(f)
        if mod is None:
            continue
        if any(isinstance(n, ast.ClassDef) and n.name.endswith("ErrorCode") for n in mod.body):
            containers.append(f)
    if len(containers) > 1:
        for f in containers[1:]:
            out.add("#117", bc_rel / f.relative_to(bc), f"BC 안에 두 번째 ErrorCode 컨테이너를 두지 않는다 — 첫째는 `{containers[0].relative_to(bc)}`")
    _check_canonical_module_containers(bc, bc_rel, out)


_ENUM_BASE_NAMES = {"Enum", "IntEnum", "StrEnum", "Flag", "IntFlag", "ReprEnum"}


def _enum_local_names(mod: ast.Module, wanted: "set[str]") -> "set[str]":
    """`from enum import …(as 별칭)` 로 실제 들여온 이름만 — import 없는 맨 이름은
    enum 계열이 아니다(혼성 패널 Y#8: 로컬 헬퍼 동명 오발화 차단)."""
    names: "set[str]" = set()
    for n in mod.body:
        if isinstance(n, ast.ImportFrom) and n.module == "enum":
            for a in n.names:
                if a.name in wanted:
                    names.add(a.asname or a.name)
    return names


def _enum_module_names(mod: ast.Module) -> "set[str]":
    """`import enum (as 별칭)` 의 모듈 이름들 — Attribute 판은 이 receiver 만 매치(Y#8)."""
    names: "set[str]" = set()
    for n in mod.body:
        if isinstance(n, ast.Import):
            for a in n.names:
                if a.name == "enum":
                    names.add(a.asname or a.name)
    return names


def _names_enum(expr: ast.expr, local: "set[str]", tails: "set[str]",
                enum_mods: "set[str]") -> bool:
    if isinstance(expr, ast.Name):
        return expr.id in local
    if isinstance(expr, ast.Attribute):
        return (isinstance(expr.value, ast.Name) and expr.value.id in enum_mods
                and expr.attr in tails)
    return False


def _check_canonical_module_containers(bc: Path, bc_rel: Path, out: Findings) -> None:
    """정본 오류 모듈(`driving_layer/api/bc_error_schema.py`) 안의 잉여 컨테이너.

    check-error-centralization 의 «second ErrorCode/StrEnum container»·복수 `<Bc>ErrorCode`
    사건이 #117 소유로 이관된 자리(귀속 매핑표 v2 행23ⓑ·24ⓐ·30ⓑ·31) — 파일 단위 검사가
    못 보는 모듈 내부 사건 모양을 소유자가 직접 포섭한다(U11 소유자 보강).
    """
    module = bc / "driving_layer" / "api" / "bc_error_schema.py"
    if not module.is_file():
        return
    mod = _parse(module)
    if mod is None:
        return
    canonical = "".join(part.capitalize() for part in bc.name.split("_")) + "ErrorCode"
    rel = bc_rel / module.relative_to(bc)
    str_enum_local = _enum_local_names(mod, {"StrEnum"})
    call_local = _enum_local_names(mod, _ENUM_BASE_NAMES)
    enum_mods = _enum_module_names(mod)
    canonical_seen = False
    for node in mod.body:
        if isinstance(node, ast.ClassDef):
            if node.name == canonical and not canonical_seen:
                canonical_seen = True
                continue
            if node.name.endswith("ErrorCode") or any(_names_enum(b, str_enum_local, {"StrEnum"}, enum_mods) for b in node.bases):
                out.add("#117", f"{rel}:{node.lineno}", f"BC 안에 두 번째 ErrorCode 컨테이너를 두지 않는다 — 정본 오류 모듈의 컨테이너는 `{canonical}` 하나다")
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            value = node.value
            if isinstance(value, ast.Call) and _names_enum(value.func, call_local, _ENUM_BASE_NAMES, enum_mods):
                out.add("#117", f"{rel}:{node.lineno}", "BC 안에 두 번째 ErrorCode 컨테이너를 두지 않는다 — functional Enum 으로 컨테이너를 늘리지 않는다")


def _check_admin_features(bc: Path, bc_rel: Path, cand: Candidates) -> None:
    for f in sorted(bc.rglob("*.py")):
        rp = f.relative_to(bc).parts
        if set(rp) & SKIP_DIRS or "feature" not in rp or "admin" not in rp:
            continue
        mod = _parse(f)
        if mod is None:
            continue
        has_domain = any(level == 0 and "domain_layer" in p.split(".") for _n, p, level in _imports(mod))
        has_repo_write = any(
            isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr in ("save", "remove", "save_all")
            for n in ast.walk(mod)
        )
        if has_domain and has_repo_write:
            cand.add("#347", bc_rel / f.relative_to(bc), "admin feature 가 애그리거트를 부르고 리포지토리 쓰기를 한다 — 업무 규칙이 있는 운영 쓰기는 그 BC 창구(`driving_layer/open_host_service/`)로 부르고 `feature/` 에는 화면만 둔다(도메인 · 응용 import 는 #668)", "「이 쓰기에 DB 로 걸 수 없는 업무 규칙이 걸리나 — 걸리면 그 BC 창구로 부르나」")


def _check_boundary_annotations(bc: Path, bc_rel: Path, out: Findings) -> None:
    """#11 확정 몫 — 경계 파일 애너테이션에 QuerySet·ORM Model 타입."""
    boundary_globs = ("application_layer/port/**/*.py", "driving_layer/open_host_service/**/contract/**/*.py")
    for pattern in boundary_globs:
        for f in sorted(bc.glob(pattern)):
            mod = _parse(f)
            if mod is None:
                continue
            for node in ast.walk(mod):
                anns: list[ast.expr | None] = []
                if isinstance(node, ast.AnnAssign):
                    anns.append(node.annotation)
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    anns.extend(a.annotation for a in node.args.posonlyargs + node.args.args + node.args.kwonlyargs)
                    anns.append(node.returns)
                for ann in anns:
                    idents = _ann_idents(ann)
                    bad = {i for i in idents if i == "QuerySet" or (i.endswith("Model") and i != "BaseModel")}
                    for b in sorted(bad):
                        out.add("#11", bc_rel / f.relative_to(bc), f"경계를 넘는 데이터에 엔티티도 DB 행도 실리지 않는다 — 애너테이션 `{b}` (연 쪽이 닫기까지 못 한다)")


# D38 사후 신호 중 «기계 확정» 가능한 것은 BC 식별 인자뿐이다 — kind·mode·is_* 는
# 일반 시그니처와 구별할 수 없어(무해한 mode 인자 실증) 확정 판정에서 걷었다(08-12 리뷰).
BRANCH_PARAM_NAMES = {"bc", "bounded_context"}


def _check_framework_demotion(target: Path, out: Findings) -> None:
    """#470 — 강등을 매개변수로 때운 «사후 신호»(D38): framework 공개 시그니처의 BC 분기 매개변수."""
    fw = target / "framework"
    if not fw.is_dir():
        return
    for f in sorted(fw.rglob("*.py")):
        rel_parts = f.relative_to(fw).parts
        if set(rel_parts) & SKIP_DIRS or "test" in rel_parts:
            continue
        mod = _parse(f)
        if mod is None:
            continue
        for node in ast.walk(mod):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) or node.name.startswith("_"):
                continue
            for arg in node.args.posonlyargs + node.args.args + node.args.kwonlyargs:
                if arg.arg in BRANCH_PARAM_NAMES:
                    out.add("#470", f.relative_to(target), f"`{node.name}({arg.arg}=…)` — 강등은 매개변수를 더 받는 것이 아니라 인라인해서 각 BC 로 돌려보내고 다시 뽑는 것이다(D38)")


def _check_project_rule_lists(pkg: Path, target: Path, out: Findings) -> None:
    """#433 — `<project>/` 파일의 «주소·예외 목록». INSTALLED_APPS(등록의 정본 자리)와
    MIDDLEWARE 를 제외한다 — MIDDLEWARE 안의 BC 경로는 «주소 목록»이 아니라 «금지된
    자가등록»이고 그 실체는 check-ninja-boundary-middleware(registry #8)가 소유한다
    (겹침 재검토 2026-08-12 — 같은 항목 이중 발화 제거·중복 진단 금지)."""
    for f in sorted(pkg.rglob("*.py")):
        if set(f.relative_to(pkg).parts) & SKIP_DIRS:
            continue
        mod = _parse(f)
        if mod is None:
            continue
        rel = f.relative_to(target)
        domain_exc_names: set[str] = set()
        for node in ast.walk(mod):
            if isinstance(node, ast.ImportFrom) and node.module:
                mods = node.module.split(".")
                if "domain_layer" in mods and "exception" in mods:
                    domain_exc_names.update(a.asname or a.name for a in node.names)
        for node in mod.body:
            if not isinstance(node, ast.Assign):
                continue
            targets = {t.id for t in node.targets if isinstance(t, ast.Name)}
            if targets & {"INSTALLED_APPS", "MIDDLEWARE"}:
                continue
            for coll in ast.walk(node.value):
                if not isinstance(coll, (ast.List, ast.Tuple, ast.Set, ast.Dict)):
                    continue
                elems = (coll.keys + coll.values) if isinstance(coll, ast.Dict) else coll.elts
                for el in elems:
                    if el is None:
                        continue
                    if isinstance(el, ast.Constant) and isinstance(el.value, str) and el.value.startswith("application."):
                        out.add("#433", rel, f"규칙을 «주소 목록»으로 적지 않는다 — BC 경로 리터럴 `{el.value}` (BC 가 늘 때마다 이 파일이 바뀐다 · #432)")
                    elif isinstance(el, ast.Name) and el.id in domain_exc_names:
                        out.add("#433", rel, f"규칙을 «예외 목록»으로 적지 않는다 — 도메인 예외 `{el.id}` 나열")


def _find_project_pkg(target: Path) -> Path | None:
    manage = target / "manage.py"
    if manage.is_file():
        m = re.search(r"DJANGO_SETTINGS_MODULE[\"']\s*,\s*[\"']([\w.]+)[\"']", manage.read_text(encoding="utf-8", errors="ignore"))
        if m:
            pkg = target / m.group(1).split(".")[0]
            if pkg.is_dir():
                return pkg
    cands = [
        p for p in sorted(target.iterdir())
        if p.is_dir() and not p.name.startswith(".") and p.name not in SKIP_DIRS
        and p.name not in ("application", "framework")
        and ((p / "settings").is_dir() or (p / "settings.py").is_file())
    ]
    return cands[0] if len(cands) == 1 else None


def _check_project_registration(target: Path, out: Findings) -> None:
    pkg = _find_project_pkg(target)
    if pkg is None:
        return
    _check_project_rule_lists(pkg, target, out)
    for name in ("api.py", "urls.py"):
        f = pkg / name
        if not f.is_file():
            continue
        rel = f.relative_to(target)
        try:
            src = f.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if "noqa: F401" in src:
            out.add("#431", rel, "부작용 등록(`# noqa: F401` import 등록)은 금지다 — 허용은 `urls.py` 의 `register_<bc>_api(api)` 명시 호출뿐이다")
        mod = _parse(f)
        if mod is None:
            continue
        imported: dict[str, str] = {}
        for node in mod.body:
            if isinstance(node, ast.ImportFrom) and node.module and node.module.split(".")[0] == "application":
                for a in node.names:
                    imported[a.asname or a.name] = f"{node.module}.{a.name}"
            elif isinstance(node, ast.Import):
                for a in node.names:
                    if a.name.split(".")[0] == "application":
                        imported[(a.asname or a.name).split(".")[0]] = a.name
        used = {n.id for n in ast.walk(mod) if isinstance(n, ast.Name)}
        for nm, path in sorted(imported.items()):
            if nm not in used:
                out.add("#431", rel, f"쓰이지 않는 BC import — 부작용 등록이다(`{path}`)")


# ── cross_context — #664 · #665 · #666(트리 172~182행 · 2026-11-14 F4-159) ──────────

CROSS_URLS_MODULE = "cross_context.backoffice.urls"
CROSS_APP_RE = re.compile(r"cross_context\.backoffice(?:\.apps\.[A-Za-z_][A-Za-z0-9_]*)?")
DJANGO_MODEL_BASES = {"django.db.models.Model", "django.db.models.base.Model"}
RAW_SQL_IMPORTS = {
    "django.db": {"connection", "connections"},
    "django.db.models": {"RawSQL"},
    "django.db.models.expressions": {"RawSQL"},
}
DB_DRIVER_MODULES = {"sqlite3", "psycopg", "psycopg2", "MySQLdb", "pymysql", "cx_Oracle", "oracledb"}
ROUTE_CALLS = {"path", "re_path"}
MODEL_META_KEYS = {"db_table", "managed", "proxy"}


def _call_name(node: ast.Call) -> str:
    fn = node.func
    return fn.attr if isinstance(fn, ast.Attribute) else (fn.id if isinstance(fn, ast.Name) else "")


def _ohs_window(dotted: str) -> bool:
    """#664 — `application.<bc>.driving_layer.open_host_service…` 꼴인가(창구 서비스 · 계약 · 창구 예외)."""
    parts = dotted.split(".")
    return len(parts) >= 4 and parts[0] == "application" and parts[2:4] == ["driving_layer", "open_host_service"]


def _import_origins(mod: ast.Module, file_parts: tuple[str, ...]) -> dict[str, str]:
    """모듈 수준 import 가 묶은 이름 → 출처 점 경로(상대 import 는 저장소 뿌리 기준으로 푼다)."""
    origins: dict[str, str] = {}
    for node in _module_level(mod.body):
        if isinstance(node, ast.Import):
            for a in node.names:
                origins[a.asname or a.name.split(".")[0]] = a.name if a.asname else a.name.split(".")[0]
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                base = _resolve_relative(file_parts, node.level, node.module or None)
                if base is None:
                    continue
                src = ".".join(base)
            else:
                src = node.module or ""
            for a in node.names:
                if a.name != "*":
                    origins[a.asname or a.name] = f"{src}.{a.name}" if src else a.name
    return origins


def _dotted_origin(expr: ast.expr, origins: dict[str, str]) -> str | None:
    chain: list[str] = []
    while isinstance(expr, ast.Attribute):
        chain.append(expr.attr)
        expr = expr.value
    if not isinstance(expr, ast.Name) or expr.id not in origins:
        return None
    return ".".join([origins[expr.id], *reversed(chain)])


def _project_class(target: Path, dotted: str) -> tuple[ast.ClassDef, dict[str, str]] | None:
    """저장소 안 모듈의 맨 위 클래스(기저 한 번 따라가기용) — 없거나 못 읽으면 None."""
    module, _, name = dotted.rpartition(".")
    if not module:
        return None
    p = target.joinpath(*module.split("."))
    f = next((c for c in (p.with_suffix(".py"), p / "__init__.py") if c.is_file()), None)
    if f is None or set(f.relative_to(target).parts) & SKIP_DIRS:
        return None
    mod = _parse(f)
    if mod is None:
        return None
    cls = next((n for n in mod.body if isinstance(n, ast.ClassDef) and n.name == name), None)
    return (cls, _import_origins(mod, f.relative_to(target).parts)) if cls is not None else None


def _django_model_base(cls: ast.ClassDef, origins: dict[str, str], local: dict[str, ast.ClassDef],
                       target: Path, follow: bool) -> bool:
    """밑 클래스의 import 출처가 `django.db.models.Model` 인가 — follow 면 같은 파일 · 저장소 안 기저를 한 번 따라간다."""
    for b in cls.bases:
        d = _dotted_origin(b, origins)
        if d in DJANGO_MODEL_BASES:
            return True
        if not follow:
            continue
        if d is None and isinstance(b, ast.Name) and b.id in local and local[b.id] is not cls:
            if _django_model_base(local[b.id], origins, local, target, False):
                return True
        elif d is not None:
            found = _project_class(target, d)
            if found is not None and _django_model_base(found[0], found[1], {}, target, False):
                return True
    return False


def _model_class(cls: ast.ClassDef, origins: dict[str, str], local: dict[str, ast.ClassDef], target: Path) -> bool:
    """#664 모델 클래스 — 밑 클래스가 Django 모델(별칭 · 프로젝트 기저 한 번 포함)이거나 안 `Meta` 에 표 표지가 있다."""
    for inner in cls.body:
        if isinstance(inner, ast.ClassDef) and inner.name == "Meta":
            for st in inner.body:
                targets = st.targets if isinstance(st, ast.Assign) else ([st.target] if isinstance(st, ast.AnnAssign) else [])
                if any(isinstance(t, ast.Name) and t.id in MODEL_META_KEYS for t in targets):
                    return True
    return _django_model_base(cls, origins, local, target, True)


def _raw_sql_import(node: ast.AST) -> str | None:
    """#664 날 SQL 길의 import — `django.db` 의 connection(s) · RawSQL · DB 드라이버 모듈."""
    if isinstance(node, ast.Import):
        hit = next((a.name for a in node.names if a.name.split(".")[0] in DB_DRIVER_MODULES), None)
        return hit
    if isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
        if node.module.split(".")[0] in DB_DRIVER_MODULES:
            return node.module
        names = RAW_SQL_IMPORTS.get(node.module, set()) & {a.name for a in node.names}
        if names:
            return f"{node.module}.{sorted(names)[0]}"
    return None


def _check_cross_inbound(target: Path, proj: Path | None, out: Findings) -> None:
    """#665 — `application/**` · `framework/**` · `<project>/**` 는 `cross_context` 를 import 하지 않는다(admin · 합성 루트 · 함수 안 포함)."""
    roots: list[Path] = [target / "application", target / "framework"]
    if proj is not None:
        roots.append(proj)
    for base in roots:
        if not base.is_dir():
            continue
        for f in sorted(base.rglob("*.py")):
            if set(f.relative_to(target).parts) & SKIP_DIRS:
                continue
            mod = _parse(f)
            if mod is None:
                continue
            for inbound in ast.walk(mod):
                if isinstance(inbound, ast.Import):
                    paths = [a.name for a in inbound.names]
                elif isinstance(inbound, ast.ImportFrom) and inbound.level == 0 and inbound.module:
                    paths = [inbound.module]
                else:
                    continue
                for p in paths:
                    if p.split(".")[0] == "cross_context":
                        out.add("#665", f.relative_to(target), "BC · framework · `<project>/` 는 `cross_context/` 를 import 하지 "
                                f"않는다(`<project>/urls.py` 는 `include(\"{CROSS_URLS_MODULE}\")` 문자열로만) — `{p}`")


def _check_cross_strings(proj: Path, target: Path, out: Findings) -> None:
    """#665 — `<project>/` 의 `cross_context.` 문자열은 `include` 첫 인자의 urls 모듈과 설정 모듈의 앱 문자열만."""
    for f in sorted(proj.rglob("*.py")):
        rp = f.relative_to(proj).parts
        if set(rp) & SKIP_DIRS:
            continue
        mod = _parse(f)
        if mod is None:
            continue
        settings_module = rp[-1] == "settings.py" or "settings" in rp[:-1]
        ok: set[int] = set()
        for node in ast.walk(mod):
            if isinstance(node, ast.Call) and _call_name(node) == "include":
                first = node.args[0] if node.args else next((k.value for k in node.keywords if k.arg == "arg"), None)
                if isinstance(first, ast.Tuple) and first.elts:
                    first = first.elts[0]
                if isinstance(first, ast.Constant) and first.value == CROSS_URLS_MODULE:
                    ok.add(id(first))
        for node in ast.walk(mod):
            if not (isinstance(node, ast.Constant) and isinstance(node.value, str)
                    and node.value.startswith("cross_context.")) or id(node) in ok:
                continue
            if settings_module and CROSS_APP_RE.fullmatch(node.value):
                continue
            out.add("#665", f"{f.relative_to(target)}:{node.lineno}", "`<project>/` 가 `cross_context` 에 닿는 문자열은 "
                    f"`include(\"{CROSS_URLS_MODULE}\")` 와 설정 모듈의 앱 문자열(`cross_context.backoffice` · 그 `apps` 모듈의 "
                    f"설정 클래스)뿐이다 — 주소는 `cross_context/backoffice/urls.py` 한 곳에서 `admin_view` 로 감싼다 — `{node.value}`")


def _check_cross_context(target: Path, out: Findings) -> None:
    """#664 · #665 · #666 — BC 밖 합성 칸 `cross_context/`(트리 172~182행)."""
    proj = _find_project_pkg(target)
    _check_cross_inbound(target, proj, out)
    if proj is not None:
        _check_cross_strings(proj, target, out)
    cc = target / "cross_context"
    if not cc.is_dir():
        return
    urls = cc / "backoffice" / "urls.py"
    for f in sorted(cc.rglob("*.py")):
        rel = f.relative_to(target)
        if set(rel.parts) & SKIP_DIRS:
            continue
        mod = _parse(f)
        if mod is None:
            continue
        is_test = "test" in rel.parts
        for node in ast.walk(mod):
            if not isinstance(node, (ast.Import, ast.ImportFrom)):
                continue
            raw = _raw_sql_import(node)
            if raw is not None:
                out.add("#664", rel, f"`cross_context/` 는 날 SQL 길을 쓰지 않는다 — `{raw}` (값은 그 BC 창구로)")
            if isinstance(node, ast.ImportFrom) and node.level > 0:
                if node.level - 1 >= len(rel.parts) - 1:
                    out.add("#664", rel, f"상대 import 가 `cross_context/` 밖으로 나간다 — `{'.' * node.level}{node.module or ''}`")
                continue
            if isinstance(node, ast.Import):
                bad = [a.name for a in node.names if a.name.split(".")[0] == "application" and not _ohs_window(a.name)]
            elif (node.module or "").split(".")[0] == "application" and not _ohs_window(node.module or ""):
                names = [a.name for a in node.names]
                bad = [] if names and all(_ohs_window(f"{node.module}.{n}") for n in names) else [node.module or ""]
            else:
                bad = []
            for p in bad:
                out.add("#664", rel, "`cross_context/` 가 BC 에서 import 하는 것은 그 BC 의 `driving_layer/open_host_service/` "
                        f"아래(창구 서비스 · 계약 · 창구 예외)뿐이다 — `{p}`")
        origins = _import_origins(mod, rel.parts)
        local = {n.name: n for n in mod.body if isinstance(n, ast.ClassDef)}
        for node in ast.walk(mod):
            if isinstance(node, ast.ClassDef) and _model_class(node, origins, local, target):
                out.add("#664", f"{rel}:{node.lineno}", f"`cross_context/` 는 모델 클래스를 두지 않는다 — `{node.name}`"
                        "(`managed = False` · 프로젝트 기저 · 표 표지 `Meta` 도) · 값은 그 BC 창구로 읽는다")
            if not isinstance(node, ast.Call):
                continue
            name = _call_name(node)
            if name == "get_model" or (name == "get_user_model" and not is_test):
                out.add("#664", f"{rel}:{node.lineno}", f"`cross_context/` 는 BC 모델을 꺼내지 않는다 — `{name}()` (값은 그 BC 창구로)")
            if isinstance(node.func, ast.Attribute) and name in ("raw", "extra"):
                out.add("#664", f"{rel}:{node.lineno}", f"`cross_context/` 는 날 SQL 을 쓰지 않는다 — `.{name}(…)` (값은 그 BC 창구로)")
            if f == urls and name in ROUTE_CALLS:
                view = node.args[1] if len(node.args) > 1 else next((k.value for k in node.keywords if k.arg == "view"), None)
                wrapped = isinstance(view, ast.Call) and isinstance(view.func, ast.Attribute) and view.func.attr == "admin_view"
                if not wrapped:
                    out.add("#666", f"{rel}:{node.lineno}", f"화면 주소는 `admin.site.admin_view(…)` 로 감싼다 — `{name}(…)`"
                            "(admin 로그인 · 권한을 그대로 쓴다 · `include` 도 두지 않는다)")
            elif f != urls and name in ROUTE_CALLS | {"Router"}:
                out.add("#666", f"{rel}:{node.lineno}", f"`cross_context/` 의 주소는 `cross_context/backoffice/urls.py` 한 파일에만 "
                        f"적는다 — `{name}(…)`")


# ── main ────────────────────────────────────────────────────────────────────

class _UsageParser(argparse.ArgumentParser):
    """usage 오류를 문면 계약(exit 1)으로 — argparse 기본 exit 2 는 «위반»과 겹친다
    (check-composition-root `_UsageParser` 패턴 이식)."""

    def error(self, message: str) -> None:
        print(f"사용 오류: {message}", file=sys.stderr)
        raise SystemExit(1)


def _build_parser() -> argparse.ArgumentParser:
    p = _UsageParser(add_help=True)
    p.add_argument("target", nargs="?", default=".")
    # 호환 심 — registry 렌더가 넘기는 selector 들. API-error lane 은 전용 검사기 소유가
    # 됐으므로 여기서는 수용만 하고 쓰지 않는다(실행·종료 계약 무변).
    p.add_argument("--error-profile", action="append", default=[])
    p.add_argument("--scope", action="append", default=[])
    p.add_argument("--api-module", action="append", default=[])
    p.add_argument("--controller-module", action="append", default=[])
    p.add_argument("--scope-bc", action="append", default=[])
    p.add_argument("--error-bc", action="append", default=[])
    # 판정 차분(anchor_diff) — 신규분만 blocker·앵커 기존분은 보고 강등(2026-08-15 r2″).
    p.add_argument("--anchor", default=None)
    p.add_argument(anchor_diff.BASELINE_FLAG, action="store_true", dest="anchor_baseline")
    p.add_argument(anchor_diff.DEBT_FLAG, dest="anchor_debt_file", default=None)
    return p


def main(argv: list[str]) -> int:
    rest: list[str] = argv
    approved_merge_file: str | None = None
    approved_merge_error: str | None = None
    if any(t == anchor_diff.APPROVED_MERGE_FLAG or t.startswith(anchor_diff.APPROVED_MERGE_FLAG + "=") for t in argv):
        # 플래그가 있을 때만 새 함수를 부른다 — 플래그 없는 실행은 2.21.1 과 같은 argv·같은 anchor_diff 이름만 쓴다.
        rest, approved_merge_file, approved_merge_error = anchor_diff.split_approved_merge(argv)
    ns = _build_parser().parse_args(rest)
    ns.anchor_approved_merge_file: str | None = approved_merge_file
    if approved_merge_error is not None:
        print(f"사용 오류: {approved_merge_error}", file=sys.stderr)
        return 1
    target = Path(ns.target)
    bad_target_reason = checker_target.bc_shaped_target_reason(target)
    if bad_target_reason is not None:
        print(f"사용 오류: {bad_target_reason}", file=sys.stderr)
        return 1
    if not target.is_dir():
        print(f"사용 오류: 디렉터리가 아니다 — {target}", file=sys.stderr)
        return 1
    if ns.anchor is not None and ns.anchor_baseline:
        print(f"사용 오류: --anchor 와 {anchor_diff.BASELINE_FLAG} 는 함께 전달할 수 없다", file=sys.stderr)
        return 1
    if ns.anchor_debt_file is not None and ns.anchor is None:
        print(f"사용 오류: {anchor_diff.DEBT_FLAG} 는 --anchor 와 함께만 쓸 수 있다(차분 전용 빚 채널)", file=sys.stderr)
        return 1
    if ns.anchor_approved_merge_file is not None and ns.anchor is None:
        print(f"사용 오류: {anchor_diff.APPROVED_MERGE_FLAG} 는 --anchor 와 함께만 쓸 수 있다(차분 전용 승인 유입 채널)", file=sys.stderr)
        return 1
    if ns.anchor_baseline and anchor_diff.is_git_worktree(target.resolve()):
        print(
            f"사용 오류: {anchor_diff.BASELINE_FLAG} 는 앵커 스냅숏(비-git) 재실행 전용이다 — "
            "git 저장소 TARGET 에는 쓸 수 없다",
            file=sys.stderr,
        )
        return 1
    if ns.anchor is not None:
        # 재료 선검증 — 무발견 clean 이라도 resolve 불능 앵커·부재/형식 오류 빚 파일·
        # 공허 차분이 침묵 exit 0 되지 않게 여기서 막는다(fail-closed).
        try:
            anchor_diff.validate_materials(target, ns.anchor, ns.anchor_debt_file,
                **({"approved_merge_file": ns.anchor_approved_merge_file}
                   if ns.anchor_approved_merge_file is not None else {}))
        except anchor_diff.AnchorDiffUsage as exc:
            print(f"사용 오류: {exc}", file=sys.stderr)
            return 1

    containers = [
        p for p in (target / "application",)
        if p.is_dir() and not (set(p.parts) & SKIP_DIRS)
    ]
    bcs: list[Path] = []
    for c in containers:
        bcs.extend(p for p in sorted(c.iterdir()) if p.is_dir() and not p.name.startswith("."))

    if not any(_has_adoption_signal(b) for b in bcs):
        print("표준 레이아웃 미채택 — 검사 대상 없음 (clean)")
        return 0
    if not bcs:
        guard = zero_target_guard(
            "blocker: 채택 신호는 있는데 검사할 BC 가 0건이다 — 조용한 무동작을 금지한다(#74)"
        )
        emit_all(guard, printer=print, indent="")
        return 2

    all_bcs = _import_target_names(target)
    findings = Findings(defer=True)
    cand = Candidates(defer=True)
    acl_partners: dict[str, set[str]] = {}

    for bc in bcs:
        bc_rel = bc.relative_to(target)
        # #151·#364 의 «타 BC 이름» 은 같은 컨테이너의 BC 뿐이다 — `web/application/<단위>` 같은 다른 컨테이너 이름은 세지 않는다.
        container_bcs = vocab.container_bc_names(bc)
        dl = bc / "domain_layer"
        agg_names: set[str] = set()
        if dl.is_dir():
            agg_dirs, _ = _entries(dl)
            agg_names = {p.name for p in agg_dirs if p.name not in ("shared_value_object", "domain_service")
                         and not checker_target.cache_only_instance(p)}

        for f in sorted(bc.rglob("*.py")):
            if set(f.relative_to(bc).parts) & SKIP_DIRS:
                continue
            _scan_imports(f, bc, bc_rel, all_bcs, findings)

        ohs = bc / "driving_layer" / "open_host_service"
        if ohs.is_dir():
            _check_ohs(ohs, bc, bc_rel, agg_names, container_bcs, findings, cand, target)

        acl = _acl_dir(bc)
        if acl is not None:
            acl_partners[bc.name] = _check_acl(acl, bc, bc_rel, findings)
        _check_uow_cross(bc, bc_rel, _cross_bc_port_names(acl), findings)
        _check_ports(bc, bc_rel, container_bcs, findings)
        _check_api_controllers(bc, bc_rel, findings)
        _check_exception_spots(bc, bc_rel, findings)
        _check_banned_entrance_name(bc, bc_rel, findings)
        _check_error_code_containers(bc, bc_rel, findings)
        _check_admin_features(bc, bc_rel, cand)
        _check_boundary_annotations(bc, bc_rel, findings)

    for a, partners in sorted(acl_partners.items()):
        for b in sorted(partners):
            if a in acl_partners.get(b, set()):
                findings.add("#450", Path("application") / a, f"두 BC(`{a}`·`{b}`)가 서로의 `anticorruption_layer/` 에 들어 있다 — 순환 결합이다")

    _check_framework_demotion(target, findings)
    _check_project_registration(target, findings)
    _check_cross_context(target, findings)

    if cand:
        print(f"ⓓ 후보 {len(cand)}건 — 기계가 좁힌 후보다(exit 불산입). 마무리는 discipline-reviewer 의 물음이 한다:")
        emit_all(cand, printer=print, indent="  ")
    if findings:
        print(f"blocker {len(findings)}건 — 컨텍스트 격리·경계 규율 위반")
        emit_all(findings, printer=print, indent="  ")
        if ns.anchor is not None:
            try:
                return anchor_diff.partition_exit(
                    script=Path(__file__).resolve(),
                    label="[check-context-isolation]",
                    target=target,
                    anchor=ns.anchor,
                    argv=argv,
                    findings=list(findings),
                    path_flags=frozenset({"--api-module", "--controller-module"}),
                    debt_file=ns.anchor_debt_file,
                    **({"approved_merge_file": ns.anchor_approved_merge_file, "baseline_collects_all": True}
                       if ns.anchor_approved_merge_file is not None else {}),
                )
            except anchor_diff.AnchorDiffUsage as exc:
                print(f"사용 오류: {exc}", file=sys.stderr)
                return 1
        return 2
    print(f"clean — BC {len(bcs)}개 격리 규율 일치 (standard_tree {tree.SOURCE_SHA})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
