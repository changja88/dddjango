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
  OHS    #146 published_service 금지 · #149/#113 라우팅·등록 함수 금지 · #150 평면 .py 금지
         #152/#154/#155 service·contract 구조 · #156/#157/#159/#160 계약 1타입=1파일
         #162 응답에 도메인 금지 · #163 exception 은 서비스 스코프 · #164 도메인 예외 번역
         #166/#167/#168/#170 기저 예외·상속·1클래스=1모듈·_v1 금지 · #453/#454 «없다»는 답
         #455 사유는 코드로 · #472 contract 는 stdlib·같은 BC 계약만 · #482/#483/#484 명명
         #633 인자는 request 하나 · #634 공개 표면은 함수만 · #295 raw 재노출 금지
  ACL    #361 상대 BC 하나=폴더 하나 · #363 클래스명 <Bc><Capability>Adapter
         #364 포트 파일명에 공급자 BC 금지 · #450 상호 ACL 금지 · #473 기저 예외를 잡는다
  기타   #14 `with unit_of_work:` 안에서 크로스-BC 포트 호출 금지 · #110 auto_import=False
         #117 두 번째 ErrorCode 컨테이너 금지 · #291/#292 예외의 자리 셋 · #431 부작용 등록 금지

ast+ 후보 채널 (㉰ — exit 불산입, 마무리는 discipline-reviewer):
  #151(창구 이름 — 기술·타 BC 토큰은 «확정» 위반) · #153(도메인 예외 속성 접근은 «확정»,
  유스케이스 호출 0/2회↑는 후보) · #171(접미사뿐인 예외 이름) · #347(admin feature 의
  애그리거트 쓰기) · #11(경계 애너테이션의 Model/QuerySet 은 «확정», 그 외 후보)

  framework #470 강등의 사후 신호 — 공개 시그니처에 `kind`·`mode`·`bc`·`is_*` 매개변수(D38)
  <project> #433 규칙을 «주소·예외 목록»으로 적지 않는다 — BC 경로 리터럴 컬렉션
         (INSTALLED_APPS 등록은 제외)·도메인 예외 이름 컬렉션

CLI 호환 심: registry 가 렌더하는 `--error-profile`·selector 들은 «수용하되 무시»한다 —
그 lane(API error contract)은 전용 검사기 4종의 소유가 됐고, 실행·종료 계약은 무변이다.

사용법: check-context-isolation.py [TARGET_DIR] [--error-profile …] [selector …]
종료코드: 0=clean(또는 표준 미채택) · 1=사용/분석 오류 · 2=blocker(발견 출력)
구조화 레코드: DJR_FINDINGS_JSON=<경로> 지정 시 findings.py(공용 모듈)가 JSON lines 를
추가 방출한다 — 라인 출력·exit 의미론 무변(T0 B2).
"""
from __future__ import annotations

import argparse
import ast
import re
import sys

import checker_target
from findings import Candidates, Findings
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

def _apply_same_bc(loc: str, tgt: str, rel, mod_path: str, out: Findings) -> None:
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
            if loc != "persistence":
                out.add("#328", rel, f"`django_<bc>` 를 import 하는 것은 `adapter/persistence/` 아래뿐이다 — `{mod_path}`")
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


def _scan_imports(f: Path, bc: Path, bc_rel: Path, all_bcs: set[str], out: Findings) -> None:
    file_parts = f.relative_to(bc).parts
    loc = _spot(file_parts)
    if loc in ("django", "composition", "other", "bc_root"):
        return  # django 는 #326(check-db-table) 소유 · composition_root 는 전부를 안다
    mod = _parse(f)
    if mod is None:
        return
    rel = bc_rel / f.relative_to(bc)
    for node, mod_path, level in _imports(mod):
        if level > 0:
            target_parts = _resolve_relative(file_parts, level, mod_path or None)
            if target_parts is None:
                out.add("#12", rel, "상대 import 가 BC 밖으로 탈출한다 — 타 BC 는 관문으로만 부른다")
                continue
            _apply_same_bc(loc, _spot(target_parts), rel, "." * level + mod_path, out)
            continue
        parts = mod_path.split(".")
        if "application" in parts:
            i = parts.index("application")
            if i + 1 < len(parts) and parts[i + 1] in all_bcs:
                tgt_bc = parts[i + 1]
                tgt = _spot(tuple(parts[i + 2:]))
                if tgt_bc == bc.name:
                    _apply_same_bc(loc, tgt, rel, mod_path, out)
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


def _check_ohs(ohs: Path, bc: Path, bc_rel: Path, agg_names: set[str], all_bcs: set[str],
               out: Findings, cand: Candidates) -> None:
    rel0 = bc_rel / ohs.relative_to(bc)
    dirs, files = _entries(ohs)
    for f in files:
        if f.name != "__init__.py":
            out.add("#150", rel0 / f.name, "`open_host_service/` 의 1차 축은 `<service>/` 폴더다 — 평면 `.py` 를 두지 않는다")

    for svc in dirs:
        srel = rel0 / svc.name
        tokens = set(svc.name.split("_"))
        if tokens & TECH_NAME_TOKENS or tokens & (all_bcs - {bc.name}):
            out.add("#151", srel, "창구 이름은 「무엇을 해 주는가」로 짓는다 — 기술·타 BC 이름 토큰이 들어 있다")
        elif svc.name.removesuffix("_service") in agg_names or svc.name in agg_names:
            cand.add("#151", srel, f"창구 이름 `{svc.name}` 이 애그리거트 이름과 같다", "Q1(이 이름이 «무엇을 해 주는가»를 말하나)")

        entry = svc / f"{svc.name}_service.py"
        if not entry.is_file():
            out.add("#152", srel / entry.name, f"창구의 진입점은 `{svc.name}_service.py` 하나다 — 부재")
        sdirs, sfiles = _entries(svc)
        for p in sdirs:
            if p.name != "contract":
                out.add("#154", srel / p.name, "`<service>/` 안은 `<service>_service.py` 와 `contract/` 둘로 구성한다")
        for p in sfiles:
            if p.name not in (entry.name, "__init__.py"):
                out.add("#154", srel / p.name, "`<service>/` 안은 `<service>_service.py` 와 `contract/` 둘로 구성한다")

        ops: set[str] = set()
        if entry.is_file():
            ops = _check_ohs_service(entry, srel / entry.name, out, cand)

        contract = svc / "contract"
        if contract.is_dir():
            cdirs, cfiles = _entries(contract)
            for p in cdirs:
                if p.name not in ("request", "response", "exception"):
                    out.add("#155", srel / "contract" / p.name, "`contract/` 는 `request/`·`response/`·`exception/` 셋으로 갈린다(#163 — exception 은 연산 축이 아니라 서비스 스코프다)")
            for p in cfiles:
                if p.name != "__init__.py":
                    out.add("#155", srel / "contract" / p.name, "`contract/` 직계에 평면 파일을 두지 않는다")
            _check_contract_kind(contract / "request", "Request", "#157", "#156", ops, srel, out)
            _check_contract_kind(contract / "response", "Response", "#160", "#159", ops, srel, out)
            _check_published_exceptions(contract / "exception", svc.name, srel, out, cand)


def _check_ohs_service(entry: Path, rel, out: Findings, cand: Candidates) -> set[str]:
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
                if handler_types & domain_names:
                    for inner in ast.walk(sub):
                        if isinstance(inner, ast.Attribute) and isinstance(inner.value, ast.Name) and inner.value.id == sub.name:
                            out.add("#153", rel, f"도메인 예외는 «타입»으로만 쓴다 — `{sub.name}.{inner.attr}` 속성 접근은 계약이 도메인 모양에 얹힌 것이다")
                            break
        calls = sum(
            1 for sub in ast.walk(fn)
            if isinstance(sub, ast.Call) and "use_case" in ast.dump(sub.func).lower()
        )
        exec_calls = sum(
            1 for sub in ast.walk(fn)
            if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Attribute) and sub.func.attr == "execute"
        )
        if max(calls, exec_calls) != 1:
            cand.add("#153", f"{rel}:{fn.lineno}", f"`{fn.name}` 의 유스케이스 호출이 {max(calls, exec_calls)}회다 — 창구는 「바꾸고·부르고·되돌리는 일만」 한다", "「이 문장이 «계약↔응용 DTO 변환»인가」")
        for d in fn.decorator_list:
            ids = _ann_idents(d)
            # 라우팅·등록 데코레이터만 문다 — 호출형 데코레이터 일반(@lru_cache(...) 류)은 #149 의 대상이 아니다.
            if ids & {"route", "router", "api_controller", "register"} or (
                ids & {"get", "post", "put", "patch", "delete", "head", "options"} and ids & {"api", "router", "app"}
            ):
                out.add("#149", rel, f"OHS 는 같은 프로세스 함수 호출이다 — 라우팅·등록을 두지 않는다(#113) — `{fn.name}`")
                break
    return ops


def _check_contract_kind(kind_dir: Path, suffix: str, one_file_rule: str, only_rule: str,
                         ops: set[str], srel, out: Findings) -> None:
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
        if len(pubs) >= 2:
            out.add(one_file_rule, rel, f"계약 타입 하나 = 파일 하나다 — 공개 클래스가 {len(pubs)}개다")
        for cls in pubs:
            if not cls.name.endswith(suffix):
                out.add("#484", rel, f"계약 클래스는 `<Operation>{suffix}` 다(`Result` 금지 — {only_rule}: 이 폴더에는 이 창구가 {'받는' if suffix == 'Request' else '돌려주는'} 타입만 온다) — `{cls.name}`")
            if suffix == "Response":
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


def _check_acl(acl: Path, bc: Path, bc_rel: Path, out: Findings) -> set[str]:
    rel0 = bc_rel / acl.relative_to(bc)
    dirs, files = _entries(acl)
    for f in files:
        if f.name != "__init__.py":
            out.add("#361", rel0 / f.name, "`anticorruption_layer/` 아래는 상대 BC 하나 = 폴더 하나다 — 평면 파일을 두지 않는다")
    partners: set[str] = set()
    for d in dirs:
        partners.add(d.name)
        for f in sorted(d.glob("*.py")):
            if f.name == "__init__.py":
                continue
            rel = rel0 / d.name / f.name
            mod = _parse(f)
            if mod is None:
                continue
            expected_prefix = _camel(d.name)
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
            for node in ast.walk(mod):
                if isinstance(node, ast.Try) and node.handlers:
                    last = node.handlers[-1]
                    if not (_ann_idents(last.type) & base_names):
                        out.add("#473", rel, "try 의 마지막 except 에 상대 창구의 기저 예외가 있어야 한다(#167 짝 — 둘이 닫혀야 약속이 선다)")
    return partners


# ── 그 밖 — #14 · #110 · #113 · #117 · #146 · #291 · #292 · #364 · #431 · #347 ──

def _check_ports(bc: Path, bc_rel: Path, all_bcs: set[str], out: Findings) -> None:
    port = bc / "application_layer" / "port"
    if not port.is_dir():
        return
    for p in sorted(port.rglob("*")):
        rel_parts = p.relative_to(port).parts
        if set(rel_parts) & SKIP_DIRS:
            continue
        tokens = set(p.name.removesuffix(".py").split("_"))
        if tokens & (all_bcs - {bc.name}):
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
        for node in ast.walk(mod):
            if isinstance(node, ast.ImportFrom) and node.module and "port" in node.module.split("."):
                names.update(a.asname or a.name for a in node.names if a.name.endswith("Port"))
    return names


def _check_uow_cross(bc: Path, bc_rel: Path, cross_ports: set[str], out: Findings) -> None:
    if not cross_ports:
        return
    app = bc / "application_layer"
    if not app.is_dir():
        return
    for f in sorted(app.rglob("*_use_case.py")):
        mod = _parse(f)
        if mod is None:
            continue
        attr_names: set[str] = set()
        for node in ast.walk(mod):
            if isinstance(node, ast.FunctionDef) and node.name == "__init__":
                for arg in node.args.args + node.args.kwonlyargs:
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
        out.add("#291", bc_rel / "domain_layer" / "exception.py", "BC 바로 밑 `domain_layer/exception.py` 를 두지 않는다 — 도메인 예외의 표준 자리는 애그리거트 밑 하나뿐이다")
    if (dl / "exception").is_dir():
        out.add("#292", bc_rel / "domain_layer" / "exception", "예외의 자리는 셋으로 갈린다 — 업무 규칙 위반은 `domain_layer/<aggregate>/exception/` 이다")
    app = bc / "application_layer"
    if app.is_dir():
        for p in sorted(app.rglob("*")):
            rp = p.relative_to(app).parts
            if set(rp) & SKIP_DIRS or (rp and rp[0] == "port"):
                continue
            if (p.is_file() and p.name == "exception.py") or (p.is_dir() and p.name == "exception"):
                out.add("#292", bc_rel / p.relative_to(bc), "application 쪽 예외 자리는 `port/<capability>/exception.py`(바깥 행위자의 죽음)뿐이다")


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
    names = set(wanted)
    for n in mod.body:
        if isinstance(n, ast.ImportFrom) and n.module == "enum":
            for a in n.names:
                if a.name in wanted:
                    names.add(a.asname or a.name)
    return names


def _names_enum(expr: ast.expr, local: "set[str]", tails: "set[str]") -> bool:
    if isinstance(expr, ast.Name):
        return expr.id in local
    if isinstance(expr, ast.Attribute):
        return expr.attr in tails
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
    canonical_seen = False
    for node in mod.body:
        if isinstance(node, ast.ClassDef):
            if node.name == canonical and not canonical_seen:
                canonical_seen = True
                continue
            if node.name.endswith("ErrorCode") or any(_names_enum(b, str_enum_local, {"StrEnum"}) for b in node.bases):
                out.add("#117", f"{rel}:{node.lineno}", f"BC 안에 두 번째 ErrorCode 컨테이너를 두지 않는다 — 정본 오류 모듈의 컨테이너는 `{canonical}` 하나다")
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            value = node.value
            if isinstance(value, ast.Call) and _names_enum(value.func, call_local, _ENUM_BASE_NAMES):
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
            cand.add("#347", bc_rel / f.relative_to(bc), "admin feature 가 애그리거트를 부르고 리포지토리 쓰기를 한다 — 공유 유스케이스는 `application_layer` 에 남긴다", "「이 조작을 사용자 API 도 하나」")


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
                    anns.extend(a.annotation for a in node.args.args + node.args.kwonlyargs)
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
    ns = _build_parser().parse_args(argv)
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
            anchor_diff.validate_materials(target, ns.anchor, ns.anchor_debt_file)
        except anchor_diff.AnchorDiffUsage as exc:
            print(f"사용 오류: {exc}", file=sys.stderr)
            return 1

    containers = [
        p for p in target.rglob("application")
        if p.is_dir() and not (set(p.parts) & SKIP_DIRS)
    ]
    bcs: list[Path] = []
    for c in containers:
        bcs.extend(p for p in sorted(c.iterdir()) if p.is_dir() and not p.name.startswith("."))

    if not any(_has_adoption_signal(b) for b in bcs):
        print("표준 레이아웃 미채택 — 검사 대상 없음 (clean)")
        return 0
    if not bcs:
        print("blocker: 채택 신호는 있는데 검사할 BC 가 0건이다 — 조용한 무동작을 금지한다(#74)")
        return 2

    all_bcs = {b.name for b in bcs}
    findings = Findings()
    cand = Candidates()
    acl_partners: dict[str, set[str]] = {}

    for bc in bcs:
        bc_rel = bc.relative_to(target)
        dl = bc / "domain_layer"
        agg_names: set[str] = set()
        if dl.is_dir():
            agg_dirs, _ = _entries(dl)
            agg_names = {p.name for p in agg_dirs if p.name not in ("shared_value_object", "domain_service")}

        for f in sorted(bc.rglob("*.py")):
            if set(f.relative_to(bc).parts) & SKIP_DIRS:
                continue
            _scan_imports(f, bc, bc_rel, all_bcs, findings)

        ohs = bc / "driving_layer" / "open_host_service"
        if ohs.is_dir():
            _check_ohs(ohs, bc, bc_rel, agg_names, all_bcs, findings, cand)

        acl = _acl_dir(bc)
        if acl is not None:
            acl_partners[bc.name] = _check_acl(acl, bc, bc_rel, findings)
        _check_uow_cross(bc, bc_rel, _cross_bc_port_names(acl), findings)
        _check_ports(bc, bc_rel, all_bcs, findings)
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

    if cand:
        print(f"ⓓ 후보 {len(cand)}건 — 기계가 좁힌 후보다(exit 불산입). 마무리는 discipline-reviewer 의 물음이 한다:")
        for c in cand:
            print(" ", c)
    if findings:
        print(f"blocker {len(findings)}건 — 컨텍스트 격리·경계 규율 위반")
        for f in findings:
            print(" ", f)
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
                )
            except anchor_diff.AnchorDiffUsage as exc:
                print(f"사용 오류: {exc}", file=sys.stderr)
                return 1
        return 2
    print(f"clean — BC {len(bcs)}개 격리 규율 일치 (standard_tree {tree.SOURCE_SHA})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
