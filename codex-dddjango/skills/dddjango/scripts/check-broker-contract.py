#!/usr/bin/env python3
"""dddjango 브로커 계약 검사기 — `framework/broker/{internal,external}/` 축(D59)의 결정적 백스톱.

가르는 자는 「배달에 바깥 미들웨어가 필요한가」다(BC 경계가 아니다 — 둘 다 경계는 넘는다).

담당 규칙 (rule-owner-map · 총 17):
  #442 [ast]  `<project>/celery.py` 는 Celery 인스턴스 + autodiscover_tasks 만 —
              BC 타입 import·task 정의·표 밖 노드면 위반.
  #443 [ast]  autodiscover_tasks 는 packages 를 «콜러블»로, related_name=None 으로 —
              기본값으로는 driving_layer/cron_job 에 닿지 못한다.
  #444 [ast]  packages 는 목록이 아니라 규칙 — 식에 BC 이름 문자열이 나오면 위반.
  #518 [ast]  framework/broker/** 에 어느 BC 의 업무 어휘도 없다(#628 합집합 교집합 0).
  #520 [ast+] 사실을 보내 놓고 결과를 «걱정»하면 후보 — 발행이 try 안·반환값 바인딩·
              발행 뒤 ACL/OHS 호출(passive-aggressive command).
  #521 [ast]  broker/internal/ 은 바깥 미들웨어 «없이» 배달 — 네트워크·저장·별도
              프로세스 라이브러리 import 면 위반.
  #523 [ast]  구독 등록은 «메모리에만» — import_module/import_string 되살리기·
              `.objects` 저장이면 위반.
  #524 [ast]  구독표는 «사실 → 리스너 집합» — list append·defaultdict(list)면 위반
              (ready() 가 두 번 돌면 두 번 발화한다 — 멱등은 계약이 진다).
  #525 [ast]  발행은 리스너마다 하나씩, 실패는 삼키지 않는다 — 리스너 호출에 try 가
              없으면(하나가 나머지를 막음)·except 가 pass 뿐이면(삼킴) 위반.
  #527 [ast]  InternalBroker() 인스턴스는 internal_broker.py 안에 하나 — 밖에서 만들면
              위반(BC 수만큼 생기면 남의 사실이 영영 안 들린다).
  #528 [ast]  구독표는 인스턴스 속성 — 모듈 레벨 «가변 전역»(dict/defaultdict 대입)이면 위반.
  #529 [ast+] external 을 가르는 물음 「듣는 쪽이 다른 배포 단위에 있나」 — external 로
              발행하는 사실의 `<event>_subscription.py` 가 «이 저장소 안»에 있으면 후보.
  #531 [ast]  external_broker_port 는 internal 과 «다른 계약» — internal port 를
              import(상속·재사용)하면 위반.
  #532 [ast+] external 계약은 at-least-once 를 «요구로» 적는다 — 계약 docstring 에
              그 명시가 없으면 후보(멱등 물음의 소유자는 #181 — 여기서 안 묻는다).
  #533 [ast]  external 계약은 «봉투»를 요구한다 — publish 시그니처에 식별 수단
              (envelope·source+id·event_id 류)이 없으면 위반.
  #534 [path] broker/internal/·external/ 의 .py 는 «계약 하나 · 구현 하나» 둘뿐(양방향).
  #603 [ast]  external 에 내용이 오면 딸림이 함께 선다 — ⑴outbox ⑷데드레터 ⑸순서 보장
              명시 ⑹직렬화기 ⑺버전 필드(«선언 유무»만 잰다 · ⑵멱등=#181 소유 ·
              ⑶봉투=#533 이 문다).

단순화(정직 기록): #603 은 선언의 «존재»만 잰다(이름·식별자·docstring 신호) — 품질은
사람 몫이다. #520 ㉢은 발행 뒤 같은 함수의 anticorruption/OHS 어휘 호출로 근사한다.

이관 계약(명세 조각 ⓐ): 대상 0건 가드(#74 — framework/broker 채택 신호) ·
ImportError fail-closed · ⓓ 후보는 exit 불산입.

사용법: check-broker-contract.py [TARGET_DIR]   (기본: 현재 디렉터리)
종료코드: 0=clean(또는 브로커 미채택) · 1=사용/분석 오류 · 2=blocker(발견 출력)
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
from findings import Candidates, Findings, emit_all
from pathlib import Path

try:
    import standard_tree as tree
    import business_vocab as vocab
except ImportError:  # 데이터 모듈 없이는 판정 불가 — fail-closed(분석 오류)
    print("분석 오류: standard_tree.py/business_vocab.py 를 찾지 못했다 — 검사기와 같은 폴더에 있어야 한다", file=sys.stderr)
    sys.exit(1)

SKIP_DIRS = vocab.SKIP_DIRS

# #521 — 바깥 미들웨어·저장·프로세스 라이브러리(데이터 목록 — 닫지 않는다).
MIDDLEWARE_IMPORTS = {
    "celery", "redis", "kafka", "confluent_kafka", "pika", "kombu", "requests", "httpx",
    "boto3", "psycopg2", "grpc", "grpcio", "django", "sqlalchemy", "pymongo",
}
ENVELOPE_HINTS = {"envelope", "source", "event_id", "message_id", "idempotency_key", "dedup_id"}


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


def _broker_dir(root: Path) -> Path | None:
    d = root / "framework" / "broker"
    return d if d.is_dir() else None


# ── #442 · #443 · #444 — celery 결선 ────────────────────────────────────────

def _find_celery_files(root: Path) -> list[Path]:
    out = []
    for p in root.rglob("celery.py"):
        if set(p.parts) & SKIP_DIRS:
            continue
        if "application" in p.parts or "framework" in p.parts:
            continue
        out.append(p)
    return sorted(out)


def _check_celery(root: Path, py: Path, bc_names: set[str], f: Findings) -> None:
    mod = _parse(py)
    if mod is None:
        return
    for node in ast.walk(mod):
        if isinstance(node, ast.ImportFrom) and (node.module or "").split(".")[0] == "application":
            f.add("#442", _rel(root, py, node.lineno),
                  "celery.py 가 BC 를 import 한다 — 경로 문자열만 쓰고 BC 안의 타입은 모른다")
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            f.add("#442", _rel(root, py, node.lineno),
                  f"celery.py 에 함수 `{node.name}` — Celery 인스턴스와 autodiscover_tasks 만 온다")
    for node in ast.walk(mod):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr == "autodiscover_tasks"):
            continue
        packages = node.args[0] if node.args else None
        for kw in node.keywords:
            if kw.arg == "packages":
                packages = kw.value
        if packages is None or isinstance(packages, (ast.List, ast.Tuple, ast.Set)):
            f.add("#443", _rel(root, py, node.lineno),
                  "autodiscover_tasks 의 packages 가 콜러블이 아니다 — 목록은 등록 시점에 얼어붙는다")
        related = {kw.arg: kw.value for kw in node.keywords}.get("related_name")
        if not (isinstance(related, ast.Constant) and related.value is None):
            f.add("#443", _rel(root, py, node.lineno),
                  "related_name=None 이 없다 — 기본값 'tasks' 로는 driving_layer/cron_job 에 닿지 못한다")
        for n in ast.walk(node):
            if isinstance(n, ast.Constant) and isinstance(n.value, str):
                toks = set(re.split(r"[^a-z0-9_]+", n.value.lower())) - {""}
                hit = toks & bc_names
                if hit:
                    f.add("#444", _rel(root, py, n.lineno),
                          f"packages 식에 BC 이름 {sorted(hit)} — «목록»이 아니라 «규칙»으로 짓는다"
                          "(BC 하나를 지우면 이 파일이 바뀌면 안 된다)")


# ── #534 · #518 · #521 · #523 · #524 · #525 · #528 · #531 · #533 — 브로커 칸 ──

def _check_broker_folders(root: Path, broker: Path, f: Findings, cand: Candidates) -> None:
    union = vocab.all_vocab(root)
    for side in ("internal", "external"):
        d = broker / side
        if not d.is_dir():
            continue
        pys = [p for p in sorted(d.glob("*.py")) if p.name != "__init__.py"]
        port_files = [p for p in pys if p.name == f"{side}_broker_port.py"]
        if len(pys) != 2 or not port_files:
            f.add("#534", _rel(root, d),
                  f"broker/{side}/ 의 .py 가 {[p.name for p in pys]} — «계약 하나({side}_broker_port.py) · "
                  "구현 하나» 둘뿐이다(양방향)")
        for py in pys:
            mod = _parse(py)
            if mod is None:
                continue
            _check_broker_file(root, py, mod, side, union, f, cand)


def _check_broker_file(root: Path, py: Path, mod: ast.Module, side: str,
                       union: set[str], f: Findings, cand: Candidates) -> None:
    # #518 — 업무 어휘 0.
    idents: set[str] = set()
    for node in ast.walk(mod):
        if isinstance(node, ast.ClassDef) or isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            idents |= vocab.tokens(node.name)
        elif isinstance(node, ast.Name):
            idents |= vocab.tokens(node.id)
        elif isinstance(node, ast.arg):
            idents |= vocab.tokens(node.arg)
    hit = idents & union
    if hit:
        f.add("#518", _rel(root, py),
              f"broker 에 업무 어휘 {sorted(hit)[:5]} — framework/broker/ 아래에는 어느 BC 의 "
              "업무 어휘도 나오지 않는다(#628)")

    for node in ast.walk(mod):
        # #521 — internal 은 바깥 미들웨어 없이.
        if side == "internal" and isinstance(node, (ast.Import, ast.ImportFrom)):
            mods = [a.name for a in node.names] if isinstance(node, ast.Import) else [node.module or ""]
            for m in mods:
                if m.split(".")[0] in MIDDLEWARE_IMPORTS:
                    f.add("#521", _rel(root, py, node.lineno),
                          f"broker/internal/ 이 `{m}` 를 import 한다 — 배달에 네트워크도 저장도 "
                          "별도 프로세스도 두지 않는다")
        # #523 — 경로 문자열 되살리기·DB 저장 금지.
        if isinstance(node, ast.Call):
            name = node.func.id if isinstance(node.func, ast.Name) else \
                (node.func.attr if isinstance(node.func, ast.Attribute) else "")
            if name in ("import_module", "import_string", "__import__"):
                f.add("#523", _rel(root, py, node.lineno),
                      "구독을 경로 문자열로 넣고 import 로 되살린다 — 구독표는 «메모리에만» 둔다"
                      "(D40 이 반려한 signals 보다 나쁘다)")
        if isinstance(node, ast.Attribute) and node.attr == "objects":
            f.add("#523", _rel(root, py, node.lineno),
                  "구독표가 DB 로 간다(.objects) — 「사실 이름 → 파이썬 함수」는 DB 에 담을 수 없다")
        # #528 — 모듈 레벨 가변 전역.
    for node in mod.body:
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            value = node.value
            if isinstance(value, ast.Dict) or (
                    isinstance(value, ast.Call) and isinstance(value.func, ast.Name)
                    and value.func.id in ("dict", "defaultdict")):
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                names = [t.id for t in targets if isinstance(t, ast.Name)]
                if names and not all(n.isupper() for n in names):
                    f.add("#528", _rel(root, py, node.lineno),
                          f"모듈 레벨 가변 전역 `{names[0]}` — 구독표는 «인스턴스 속성»이다"
                          "(인스턴스가 모듈에 «사는» 것과는 다르다)")

    for cls in [n for n in ast.walk(mod) if isinstance(n, ast.ClassDef)]:
        for m in [n for n in cls.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]:
            if m.name == "__init__":
                for n in ast.walk(m):
                    if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) \
                            and n.func.id == "defaultdict" and n.args \
                            and isinstance(n.args[0], ast.Name) and n.args[0].id == "list":
                        f.add("#524", _rel(root, py, n.lineno),
                              "구독표가 defaultdict(list) — «사실 → 리스너 집합»이라 같은 짝이 "
                              "두 번 와도 하나여야 한다(ready() 가 두 번 돌면 두 번 발화)")
            if "subscribe" in m.name:
                for n in ast.walk(m):
                    if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) \
                            and n.func.attr == "append":
                        f.add("#524", _rel(root, py, n.lineno),
                              "구독 등록이 리스트 append — 집합이어야 중복 등록이 하나로 접힌다")
            if "publish" in m.name:
                _check_publish_loop(root, py, m, f)
                if side == "external":
                    args = [a.arg for a in m.args.args if a.arg not in ("self", "cls")]
                    ann_names = set()
                    for a in m.args.args:
                        for n in ast.walk(a.annotation) if a.annotation else []:
                            if isinstance(n, ast.Name):
                                ann_names.add(n.id)
                    has_envelope = (set(args) & ENVELOPE_HINTS
                                    or any(n.endswith("Envelope") for n in ann_names))
                    if not has_envelope:
                        f.add("#533", _rel(root, py, m.lineno),
                              "external publish 시그니처에 봉투가 없다 — 두 번 온 것을 알아볼 "
                              "식별자(source+id) 없이는 멱등을 지킬 수단이 없다")

    if side == "external" and py.name == "external_broker_port.py":
        # #531 — internal 계약 재사용 금지.
        for node in ast.walk(mod):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                mods = [a.name for a in node.names] if isinstance(node, ast.Import) else [node.module or ""]
                if any("internal_broker" in m for m in mods):
                    f.add("#531", _rel(root, py, node.lineno),
                          "external 계약이 internal 계약을 import 한다 — 보장이 달라 «다른 계약»이다"
                          "(같은 계약의 다른 구현이 아니다)")
        # #532 — at-least-once 를 «요구로» 적는다.
        text = py.read_text(encoding="utf-8")
        if not re.search(r"at[- ]least[- ]once|두 번", text, re.IGNORECASE):
            cand.add("#532", _rel(root, py),
                     "external 계약에 「반드시 도달·두 번 올 수 있다(at-least-once)」 명시가 없다 — "
                     "도달 보장은 미들웨어 설정에 살아 트리가 확인할 수 없으니 계약이 «요구로» 적는다",
                     "받는 쪽이 「안 왔을 때」와 「두 번 왔을 때」를 메우고 있나(#181·#629)")


def _check_publish_loop(root: Path, py: Path, m: ast.FunctionDef | ast.AsyncFunctionDef, f: Findings) -> None:
    """#525 — 리스너 루프: try 없으면 전파(나머지가 못 감), except 가 pass 뿐이면 삼킴."""
    for loop in [n for n in ast.walk(m) if isinstance(n, (ast.For, ast.AsyncFor))]:
        calls_listener = any(isinstance(n, ast.Call) for n in ast.walk(loop))
        if not calls_listener:
            continue
        tries = [n for n in ast.walk(loop) if isinstance(n, ast.Try)]
        if not tries:
            f.add("#525", _rel(root, py, loop.lineno),
                  "리스너 호출에 try 가 없다 — 하나가 실패하면 나머지가 못 간다"
                  "(발행은 리스너마다 하나씩 넘긴다)")
            continue
        for t in tries:
            for h in t.handlers:
                body_real = [s for s in h.body if not isinstance(s, ast.Pass)]
                if not body_real:
                    f.add("#525", _rel(root, py, h.lineno),
                          "except 가 pass 뿐 — 실패한 리스너를 «삼키면» 위반이다"
                          "(기록이 가는 곳은 #602 가 짚는다)")


# ── #520 · #527 · #529 — 발행 자리 ─────────────────────────────────────────

def _internal_broker_classes(broker: Path) -> set[str]:
    out: set[str] = set()
    impl = broker / "internal" / "internal_broker.py"
    if impl.is_file():
        mod = _parse(impl)
        if mod:
            out = {n.name for n in mod.body if isinstance(n, ast.ClassDef)}
    return out or {"InternalBroker"}


def _snake(camel: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", camel).lower()


def _check_publish_sites(root: Path, broker: Path, f: Findings, cand: Candidates) -> None:
    broker_classes = _internal_broker_classes(broker)
    subs = {p.name[: -len("_subscription.py")] for p in root.rglob("*_subscription.py")
            if not set(p.parts) & SKIP_DIRS}
    for py in _py_files(root):
        if broker in py.parents and py.name == "internal_broker.py":
            continue
        mod = _parse(py)
        if mod is None:
            continue
        uses_external = any(
            isinstance(n, ast.ImportFrom) and "external_broker" in (n.module or "")
            for n in ast.walk(mod))
        for node in ast.walk(mod):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
                    and node.func.id in broker_classes:
                f.add("#527", _rel(root, py, node.lineno),
                      f"`{node.func.id}()` 를 internal_broker.py 밖에서 만든다 — 인스턴스는 그 파일 안에 "
                      "하나다(BC 마다 만들면 «남의 사실»이 영원히 안 들린다)")
        for fn in [n for n in ast.walk(mod) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]:
            publishes: list[ast.Call] = []
            for n in ast.walk(fn):
                if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "publish":
                    publishes.append(n)
            if not publishes:
                continue
            # #520 ㉠ — try 안의 발행.
            for t in [n for n in ast.walk(fn) if isinstance(n, ast.Try)]:
                for n in ast.walk(t):
                    if n in publishes:
                        cand.add("#520", _rel(root, py, n.lineno),
                                 "발행이 try 안에 있다 — 사실을 보내 놓고 결과를 «걱정»하고 있다"
                                 "(passive-aggressive command)", "이 사실이 안 나가면 내가 할 일이 있나")
            # #520 ㉡ — 반환값 바인딩.
            for n in ast.walk(fn):
                if isinstance(n, ast.Assign) and n.value in publishes:
                    cand.add("#520", _rel(root, py, n.lineno),
                             "발행 반환값을 바인딩한다 — 사실이면 결과가 없어야 한다",
                             "이 사실이 안 나가면 내가 할 일이 있나")
            # #520 ㉢ — 발행 뒤 ACL·OHS 호출.
            last_pub = max(n.lineno for n in publishes)
            for n in ast.walk(fn):
                if isinstance(n, ast.Call) and n.lineno > last_pub:
                    chain = []
                    cur: ast.AST = n.func
                    while isinstance(cur, ast.Attribute):
                        chain.append(cur.attr)
                        cur = cur.value
                    if isinstance(cur, ast.Name):
                        chain.append(cur.id)
                    joined = "_".join(chain).lower()
                    if any(p.lower().strip("_") == "acl" for p in chain) \
                            or "anticorruption" in joined or "open_host" in joined:
                        cand.add("#520", _rel(root, py, n.lineno),
                                 "발행 뒤 같은 함수에서 ACL/OHS 를 부른다 — 지시였어야 할 사실이다",
                                 "이 사실이 안 나가면 내가 할 일이 있나")
            # #529 — external 발행인데 구독이 같은 저장소 안.
            if uses_external:
                for n in publishes:
                    for a in list(n.args) + [kw.value for kw in n.keywords]:
                        ev = None
                        if isinstance(a, ast.Call) and isinstance(a.func, ast.Name):
                            ev = _snake(a.func.id)
                        elif isinstance(a, ast.Name) and a.id[:1].isupper():
                            ev = _snake(a.id)
                        elif isinstance(a, ast.Constant) and isinstance(a.value, str):
                            ev = a.value.rsplit(".", 1)[-1]
                        if ev and ev in subs:
                            cand.add("#529", _rel(root, py, n.lineno),
                                     f"external 로 발행한 사실 `{ev}` 의 구독이 «이 저장소 안»에 있다 — "
                                     "external 을 가르는 물음은 「듣는 쪽이 다른 배포 단위에 있나」다",
                                     "듣는 쪽이 따로 배포되나")


# ── #603 — external 딸림 다섯(기계 몫) ──────────────────────────────────────

def _check_external_obligations(root: Path, broker: Path, f: Findings) -> None:
    ext = broker / "external"
    if not ext.is_dir():
        return
    contents = [p for p in ext.glob("*.py") if p.name != "__init__.py"]
    if not contents:
        return
    broker_text = "\n".join((p.read_text(encoding="utf-8") for p in _py_files(broker)))
    repo_names = {
        p.name for p in root.rglob("*.py")
        if not set(p.parts) & SKIP_DIRS
        and not any(seg.startswith(".") for seg in p.relative_to(root).parts[:-1])  # 숨김 디렉터리 제외(F-C)
    }
    where = _rel(root, ext)
    if not (any("outbox" in n for n in repo_names) or "outbox" in broker_text.lower()):
        f.add("#603", where, "⑴ outbox 가 없다 — 커밋과 발행을 한 트랜잭션에 묶는 선언이 필요하다")
    if not re.search(r"dead_?letter|dlq", broker_text, re.IGNORECASE):
        f.add("#603", where, "⑷ 재시도·데드레터 선언이 없다")
    if not re.search(r"ordering|ordered|in_order|순서", broker_text, re.IGNORECASE):
        f.add("#603", where, "⑸ 순서 보장 «여부»의 명시가 없다")
    if not re.search(r"serializ|직렬화", broker_text, re.IGNORECASE):
        f.add("#603", where, "⑹ 직렬화 형식 선언이 없다")
    if not re.search(r"version|버전", broker_text, re.IGNORECASE):
        f.add("#603", where, "⑺ 스키마 진화(버전) 규칙이 없다")


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
    bc_names = vocab.bc_names(root)

    for celery_py in _find_celery_files(root):
        _check_celery(root, celery_py, bc_names, findings)

    broker = _broker_dir(root)
    if broker is not None:
        _check_broker_folders(root, broker, findings, cand)
        _check_publish_sites(root, broker, findings, cand)
        _check_external_obligations(root, broker, findings)

    emit_all(cand, printer=print, indent="")
    if findings:
        print("blocker — 브로커 계약 위반 (internal/external 을 가르는 자는 「배달에 바깥 미들웨어가 필요한가」 — D59)")
        emit_all(findings, printer=print, indent="  ")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
