#!/usr/bin/env python3
"""dddjango «놓칠 수 있는 입구» 검사기 — cron_job·webhook·event_subscription(D26·D53·D49).

바깥이 부르는 입구는 «놓칠 수 있는» 입구다 — 안 와도 업무가 돌아야 하고, 껍데기는
로직을 갖지 않는다.

담당 규칙 (rule-owner-map · 총 14):
  #172 [path] 예약 실행 입구는 `driving_layer/cron_job/` — api/·open_host_service/ 와
              나란히. 다른 곳의 cron_job/ 은 위반.
  #173 [path] 폴더 이름은 역할(cron_job/)이고 기술(celery)은 파일 안 — celery/ 폴더 금지.
  #174 [path] cron_job/ 아래는 하위 폴더 없이 `<job>_cron_job.py` 하나씩(_cron_job 필수).
  #175 [ast]  cron_job/__init__.py 가 <job> 들을 재수출한다 — 없으면 task 미등록.
  #179 [ast]  예약 작업 하나 = 파일 하나 — task 함수는 build 1회 + 유스케이스 1회
              (+command 생성)뿐. 그 밖 문장·둘째 task 면 위반.
  #180 [ast]  <job>_cron_job.py 는 재시도·주기를 모른다 — 데코 인자(max_retries·
              autoretry_for·countdown 류)·self.retry() 면 위반.
  #181 [ast+] 멱등성은 유스케이스가 갖는다 — 확정: cron_job/** 의 「이미 했나」 기계
              (get_or_create·select_for_update·lock) / 후보: 입구가 부른 유스케이스 중
              리포지토리 읽기 0 + save 만(「두 번 와도 결과가 같나」 — 멱등 물음의 소유자).
  #451 [ast+] 창구가 답을 낼 수 있으면 contract/response/, 낼 수 없을 때만
              contract/exception/ — 후보: OHS 서비스가 if 분기에서 계약 예외를 raise
              (「이 창구가 혼자서 답을 만들 수 있나」).
  #512 [ast+] webhook/<provider>/ 는 «보내는 쪽이 자기를 부르는 이름» — 확정: 역할
              deny(gateway·provider·payment·billing·notification·auth·external) /
              후보: 업무 어휘·역할 접미(_gateway|_provider|_client|_service|_api|_system).
  #514 [ast]  웹훅 컨트롤러는 도메인 예외를 「다시 보내지 마라」로 답한다 — 도메인
              예외를 잡아 되던지면(재시도 유발) 위반. 무엇이 그 응답인지는 발신자
              스펙이 정한다(2xx ack 보장 아님 — C8).
  #515 [path] webhook/<provider>/schema/ 겹 — schema_in.py(바깥이 보내는 모양)·
              schema_out.py(우리가 돌려주는 응답) 필수(ack 보장 없음 — 리다이렉트 상대 포함).
  #516 [ast]  webhook/ 에 오는 것은 HTTP 뿐 — 비-HTTP 소켓 라이브러리(pika·kombu·
              confluent_kafka·grpc) import·라우트 데코 없는 공개 컨트롤러 함수면 위반.
              받을 칸은 정본 트리 «개정»으로만 생긴다(#91 — BC 가 형제를 늘리지 않는다).
  #517 [ast]  서명 검증은 framework 인증 틀로 «데코레이터에 선언» — 본문의 hmac·
              compare_digest 절차면 위반.
  #629 [ast+] 후보(집합 차): webhook·event_subscription 이 쓰는 애그리거트 A 와
              cron_job 이 쓰는 B 의 차 A−B ≠ ∅ — 그 애그리거트는 입구가 안 오면 영영
              안 채워진다(「이 입구가 «안 와도» 업무가 돌아가나」). 메우는 길은
              cron_job 이 주인에게 «묻는» 것(#626).

단순화(정직 기록): 입구→유스케이스 해소는 build_X ↔ X_use_case.py 쌍(#85)만 따라간다.
«쓰는 애그리거트»는 유스케이스 시그니처·__init__ 의 `*Repository` 애너테이션 접두로 잰다.

이관 계약(명세 조각 ⓐ): 채택 신호 2원(#78) · 대상 0건 가드(#74) · ImportError
fail-closed · ⓓ 후보는 exit 불산입.

사용법: check-missable-entrance.py [TARGET_DIR]   (기본: 현재 디렉터리)
종료코드: 0=clean(또는 표준 미채택) · 1=사용/분석 오류 · 2=blocker(발견 출력)
"""
from __future__ import annotations

import ast
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
DRIVING_DIRS = ("driving_layer",)

RETRY_DECO_KWARGS = {"max_retries", "autoretry_for", "retry_backoff", "retry_kwargs",
                     "default_retry_delay", "countdown", "retry_jitter"}
NON_HTTP_IMPORTS = {"pika", "kombu", "confluent_kafka", "grpc", "grpcio", "websockets"}
ROLE_DIR_DENY = {"gateway", "provider", "payment", "billing", "notification", "auth", "external"}
ROLE_SUFFIXES = ("_gateway", "_provider", "_client", "_service", "_api", "_system")
IDEMPOTENCY_MACHINERY = {"get_or_create", "select_for_update", "lock", "acquire_lock"}


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


def _driving(bc: Path) -> Path | None:
    for layer in DRIVING_DIRS:
        d = bc / layer
        if d.is_dir():
            return d
    return None


# ── #172 · #173 · #174 · #175 — cron_job 자리·모양 ─────────────────────────

def _check_cron_layout(root: Path, bc: Path, f: Findings) -> Path | None:
    cron = None
    for d in bc.rglob("cron_job"):
        if not d.is_dir() or set(d.parts) & SKIP_DIRS:
            continue
        if d.parent.name in DRIVING_DIRS:
            cron = d
        else:
            f.add("#172", _rel(root, d),
                  "cron_job/ 이 driving_layer 바깥에 있다 — 예약 실행 입구는 "
                  "driving_layer/cron_job/ 에 api/·open_host_service/ 와 나란히 둔다")
    for d in bc.rglob("celery"):
        if d.is_dir() and not set(d.parts) & SKIP_DIRS:
            f.add("#173", _rel(root, d),
                  "celery/ 폴더 — 폴더 이름은 역할(cron_job/)이고 기술(celery)은 파일 안에 있다")
    if cron is None:
        return None
    jobs: list[Path] = []
    for p in sorted(cron.iterdir()):
        if p.name == "__pycache__":
            continue
        if p.is_dir():
            f.add("#174", _rel(root, p), "cron_job/ 아래 하위 폴더 — `<job>_cron_job.py` 파일 하나씩이다")
        elif p.suffix == ".py" and p.name != "__init__.py":
            if not p.name.endswith("_cron_job.py"):
                f.add("#174", _rel(root, p), "`_cron_job` 접미사가 없다 — `<job>_cron_job.py` 가 필수다")
            else:
                jobs.append(p)
    init = cron / "__init__.py"
    if jobs:
        exported: set[str] = set()
        if init.is_file():
            mod = _parse(init)
            for node in ast.walk(mod) if mod else []:
                if isinstance(node, ast.ImportFrom):
                    exported |= {a.name for a in node.names}
                    if node.module:
                        exported.add(node.module.rsplit(".", 1)[-1])
                elif isinstance(node, ast.Import):
                    exported |= {a.name.rsplit(".", 1)[-1] for a in node.names}
        missing = [j.stem for j in jobs if j.stem not in exported]
        if missing:
            f.add("#175", _rel(root, init if init.is_file() else cron),
                  f"__init__.py 가 {missing} 를 재수출하지 않는다 — 재수출이 없으면 celery task 가 등록되지 않는다")
    return cron


# ── #179 · #180 · #181 확정 — 껍데기 규율 ───────────────────────────────────

def _check_cron_job_file(root: Path, py: Path, f: Findings) -> list[str]:
    """반환: build 로 부른 유스케이스 이름들."""
    built: list[str] = []
    mod = _parse(py)
    if mod is None:
        return built
    tasks = [n for n in mod.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
             and not n.name.startswith("_")]
    if len(tasks) > 1:
        f.add("#179", _rel(root, py, tasks[1].lineno),
              f"task 가 {len(tasks)}개 — 예약 작업 하나 = 파일 하나다")
    for fn in tasks:
        for d in fn.decorator_list:
            if isinstance(d, ast.Call):
                for kw in d.keywords:
                    if kw.arg in RETRY_DECO_KWARGS:
                        f.add("#180", _rel(root, py, d.lineno),
                              f"데코 인자 `{kw.arg}` — 재시도와 주기는 celery «설정»이 갖는다"
                              "(입구가 알면 입구에 로직이 생긴 것이다)")
        for n in ast.walk(fn):
            if isinstance(n, (ast.If, ast.For, ast.While)):
                f.add("#179", _rel(root, py, n.lineno),
                      "task 본문에 제어 흐름 — build 1회 + 유스케이스 1회 호출이 전부다")
                break
        for n in ast.walk(fn):
            if isinstance(n, ast.Call):
                if isinstance(n.func, ast.Name) and n.func.id.startswith("build_"):
                    built.append(n.func.id[len("build_"):])
                if isinstance(n.func, ast.Attribute) and n.func.attr == "retry":
                    f.add("#180", _rel(root, py, n.lineno),
                          "self.retry() — 재시도는 celery 설정이 갖는다")
                if isinstance(n.func, (ast.Name, ast.Attribute)):
                    name = n.func.id if isinstance(n.func, ast.Name) else n.func.attr
                    if name in IDEMPOTENCY_MACHINERY:
                        f.add("#181", _rel(root, py, n.lineno),
                              f"「이미 했나」 기계 `{name}` 가 입구에 있다 — 멱등성은 cron_job 이 "
                              "아니라 유스케이스가 갖는다(바깥이 부르는 입구 전부에 같다)")
    return built


# ── #512 · #514 · #515 · #516 · #517 — webhook ─────────────────────────────

def _check_webhook(root: Path, bc: Path, f: Findings, cand: Candidates) -> list[tuple[Path, str]]:
    edges: list[tuple[Path, str]] = []
    driving = _driving(bc)
    if driving is None:
        return edges
    hooks = driving / "webhook"
    if not hooks.is_dir():
        return edges
    bc_vocab_set = vocab.bc_vocab(bc)
    for provider in sorted(p for p in hooks.iterdir() if p.is_dir() and p.name != "__pycache__"):
        name = provider.name
        if name in ROLE_DIR_DENY or set(name.split("_")) & ROLE_DIR_DENY:
            f.add("#512", _rel(root, provider),
                  f"webhook/{name}/ — 역할 이름이다. 폴더는 «보내는 쪽이 자기를 부르는 이름» "
                  "그대로다(toss/·stripe/) — 둘째 결제사가 오면 이름이 거짓말이 된다")
        elif name.endswith(ROLE_SUFFIXES) or vocab.tokens(name) & bc_vocab_set:
            cand.add("#512", _rel(root, provider),
                     f"webhook/{name}/ 이 역할 접미·업무 어휘와 겹친다",
                     "보내는 쪽 문서가 자기를 이 이름으로 부르나")
        schema = provider / "schema"
        if not (schema / "schema_in.py").is_file() or not (schema / "schema_out.py").is_file():
            f.add("#515", _rel(root, provider),
                  "schema/schema_in.py·schema_out.py 겹이 없다 — 바깥이 보내는 모양과 우리가 "
                  "돌려주는 응답이 각각 산다(돌려주는 것이 ack 라는 보장은 없다)")
    for py in _py_files(hooks):
        mod = _parse(py)
        if mod is None:
            continue
        domain_excs: set[str] = set()
        for node in ast.walk(mod):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                mods = [a.name for a in node.names] if isinstance(node, ast.Import) \
                    else [node.module or ""]
                for m in mods:
                    if m.split(".")[0] in NON_HTTP_IMPORTS:
                        f.add("#516", _rel(root, py, node.lineno),
                              f"`{m}` import — webhook 에 오는 것은 HTTP 뿐이다. 다른 전송의 칸은 "
                              "정본 트리를 «개정»해야 생긴다(#91 · BC 가 형제를 늘리지 않는다)")
                if isinstance(node, ast.ImportFrom) and "exception" in (node.module or "") \
                        and "domain_layer" in (node.module or ""):
                    domain_excs |= {a.asname or a.name for a in node.names}
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                mods = [a.name for a in node.names] if isinstance(node, ast.Import) \
                    else [node.module or ""]
                if any(m.split(".")[0] in ("hmac", "hashlib") for m in mods):
                    f.add("#517", _rel(root, py, node.lineno),
                          "서명 검증 절차가 본문에 있다(hmac/hashlib) — framework 인증 틀로 "
                          "라우트 데코레이터에 선언한다")
        if py.name.endswith("_controller.py"):
            for cls_or_mod in [mod] + [n for n in ast.walk(mod) if isinstance(n, ast.ClassDef)]:
                for fn in [n for n in cls_or_mod.body
                           if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]:
                    if fn.name.startswith("_"):
                        continue
                    if not fn.decorator_list and isinstance(cls_or_mod, ast.ClassDef):
                        f.add("#516", _rel(root, py, fn.lineno),
                              f"컨트롤러 공개 메서드 `{fn.name}` 에 HTTP 라우트 데코가 없다")
                    for n in ast.walk(fn):
                        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) \
                                and n.func.attr == "compare_digest":
                            f.add("#517", _rel(root, py, n.lineno),
                                  "compare_digest 절차가 컨트롤러 본문에 있다 — 검증은 데코 선언이다")
                        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) \
                                and n.func.id.startswith("build_"):
                            edges.append((py, n.func.id[len("build_"):]))
                        if isinstance(n, ast.Try):
                            for h in n.handlers:
                                caught = {x.id for x in ast.walk(h.type) if isinstance(x, ast.Name)} \
                                    if h.type else set()
                                if caught & domain_excs and any(
                                        isinstance(s, ast.Raise) for s in ast.walk(h)):
                                    f.add("#514", _rel(root, py, h.lineno),
                                          "도메인 예외를 잡아 «되던진다» — 업무 규칙 위반은 다시 받아도 "
                                          "영원히 같다. 「다시 보내지 마라」로 읽히는 응답을 준다"
                                          "(무엇이 그 응답인지는 발신자 스펙이 정한다)")
    return edges


# ── #451 — 창구 예외 후보 ───────────────────────────────────────────────────

def _check_contract_exception(root: Path, bc: Path, cand: Candidates) -> None:
    driving = _driving(bc)
    if driving is None:
        return
    ohs = driving / "open_host_service"
    if not ohs.is_dir():
        return
    exc_classes: set[str] = set()
    for py in _py_files(ohs):
        if "exception" in py.parts or py.parent.name == "exception":
            mod = _parse(py)
            for node in ast.walk(mod) if mod else []:
                if isinstance(node, ast.ClassDef):
                    exc_classes.add(node.name)
    if not exc_classes:
        return
    for py in _py_files(ohs):
        if not py.name.endswith("_service.py"):
            continue
        mod = _parse(py)
        if mod is None:
            continue
        for iff in [n for n in ast.walk(mod) if isinstance(n, ast.If)]:
            for n in ast.walk(iff):
                if isinstance(n, ast.Raise) and isinstance(n.exc, ast.Call) \
                        and isinstance(n.exc.func, ast.Name) and n.exc.func.id in exc_classes:
                    cand.add("#451", _rel(root, py, n.lineno),
                             f"창구가 if 분기에서 계약 예외 `{n.exc.func.id}` 를 raise 한다 — "
                             "답을 낼 수 있으면 전부 contract/response/ 로 간다",
                             "이 창구가 «혼자서» 답을 만들 수 있나")


# ── #181 후보 · #629 — 입구가 부른 유스케이스 ──────────────────────────────

def _resolve_use_case(bc: Path, name: str) -> Path | None:
    app_layer = bc / "application_layer"
    if not app_layer.is_dir():
        return None
    hits = [p for p in app_layer.rglob(f"{name}_use_case.py") if not set(p.parts) & SKIP_DIRS]
    return hits[0] if hits else None


def _use_case_profile(uc_path: Path) -> tuple[set[str], bool, bool]:
    """(쓰는 애그리거트 이름, 읽기 있음, save 있음)."""
    aggs: set[str] = set()
    reads = saves = False
    mod = _parse(uc_path)
    if mod is None:
        return aggs, reads, saves
    for node in ast.walk(mod):
        if isinstance(node, ast.arg) and node.annotation is not None:
            for n in ast.walk(node.annotation):
                if isinstance(n, ast.Name) and n.id.endswith("Repository"):
                    stem = n.id[: -len("Repository")]
                    aggs.add("".join(
                        ("_" + c.lower()) if c.isupper() else c for c in stem).lstrip("_"))
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            head = node.func.attr.split("_", 1)[0]
            if head in ("get", "find", "list", "search", "exists", "count"):
                reads = True
            elif head in ("save", "remove"):
                saves = True
    return aggs, reads, saves


def _check_entrance_use_cases(root: Path, bc: Path,
                              outside_edges: list[tuple[Path, str]],
                              cron_built: list[str], cand: Candidates) -> None:
    outside_aggs: set[str] = set()
    for src, name in outside_edges:
        uc = _resolve_use_case(bc, name)
        if uc is None:
            continue
        aggs, reads, saves = _use_case_profile(uc)
        outside_aggs |= aggs
        if saves and not reads:
            cand.add("#181", _rel(root, uc),
                     f"입구({src.relative_to(root).as_posix()})가 부른 유스케이스가 조회 없이 "
                     "save 만 한다 — 멱등은 유스케이스가 갖는다",
                     "두 번 와도 결과가 같나")
    cron_aggs: set[str] = set()
    for name in cron_built:
        uc = _resolve_use_case(bc, name)
        if uc is not None:
            cron_aggs |= _use_case_profile(uc)[0]
    gap = outside_aggs - cron_aggs
    if gap:
        cand.add("#629", _rel(root, bc),
                 f"webhook·event_subscription 만 쓰는 애그리거트 {sorted(gap)} — 바깥이 부르는 "
                 "입구는 «놓칠 수 있는» 입구라, 그 입구가 «와야만» 일이 되는 설계는 위반이다. "
                 "빠진 것은 cron_job 이 시각에 깨어나 주인에게 «물어» 메운다(#626)",
                 "이 입구가 «안 와도» 업무가 돌아가나")


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

    # 대상 0건 가드(#74) — adopted 인데 driving 층이 0건이면 경로 계약 불일치다.
    if bcs and not any(_driving(bc) is not None for bc in bcs):
        print("blocker: 채택 신호는 있는데 driving 층 디렉터리가 0건이다 — 조용한 무동작을 금지한다(#74)")
        return 2

    for bc in bcs:
        cron = _check_cron_layout(root, bc, findings)
        cron_built: list[str] = []
        if cron is not None:
            for py in sorted(cron.glob("*_cron_job.py")):
                cron_built += _check_cron_job_file(root, py, findings)
        hook_edges = _check_webhook(root, bc, findings, cand)
        _check_contract_exception(root, bc, cand)
        sub_edges: list[tuple[Path, str]] = []
        driving = _driving(bc)
        if driving is not None and (driving / "event_subscription").is_dir():
            for py in _py_files(driving / "event_subscription"):
                mod = _parse(py)
                for n in ast.walk(mod) if mod else []:
                    if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) \
                            and n.func.id.startswith("build_"):
                        sub_edges.append((py, n.func.id[len("build_"):]))
        _check_entrance_use_cases(root, bc, hook_edges + sub_edges, cron_built, cand)

    for c in cand:
        print(c)
    if findings:
        print("blocker — 놓칠 수 있는 입구 위반 (입구는 껍데기·멱등은 유스케이스·빠짐은 cron 이 메운다 — D26·D53·D49)")
        for x in findings:
            print(f"  {x}")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
