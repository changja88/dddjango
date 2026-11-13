#!/usr/bin/env python3
"""경로 앞 응답 정본 동작 스모크(F4-173 · 설계 §4.3) — 플러그인 정본 `add_pre_route_responses` 가 붙인 생성 문서가 장난감 프로젝트의
실제 응답과 맞는지 경로마다 대조한다. 참조 글 = 정본 글자 대조만으로는 Ninja 판이 바뀌어 판정이 틀려도 모른다 — 이 스모크가 그 몫이다.

장난감 = `workspace/eval/fixtures/pre_route_behavior/toy/`(루트 API 넷 — 3.2 꼴 `DocumentedAPI(NinjaAPI)` 셋 · `DocumentedExtraAPI
(NinjaExtraAPI)` 하나 · 프로젝트 표 · 미들웨어 셋) 을 tempdir 에 복사하고, 정본은 **실행 때** `dddjango/scripts/
pre_route_responses_canonical.py` 를 그 사본의 `framework/ninja/pre_route_responses.py` 로 복사해 쓴다(정본이 바뀌면 이 스모크가 실물을
본다). 장난감은 고정 판 `.venv-probe`(Django 6.1 · django-ninja · ninja_extra · pydantic · mypy — `make probe-env`)로 돈다 — 러너 자신은
표준 라이브러리만.

단언:
  ① 문서 — 루트 API 넷의 마운트 문서(`/<ns>/openapi.json`)에서 operation 마다 status 집합 = 기대(빠짐 · 남는 operation 없음) ·
     고른 (operation, status) 의 몸통 꼴(`<media>:<component>`) · 머리 이름 = 기대.
  ② 실제 — 요청마다(Django 시험 클라이언트) status = 기대 · 그 status 가 문서에 있으면 몸통이 문서 꼴(media · JSON Schema 부분 집합)이고
     실제가 싣는 머리(Retry-After · Service-Maintenance-Ends-At)가 문서 머리에 있다 · 문서에 없는 status 는 operation 답이 아닌 것(404)뿐.
  ③ Django 400 처리기를 JSON 으로 둔 표(`BAD_REQUEST_RESPONSE`)와 URLconf — 몸통 상한 · 쿼리 칸 상한 400 이 그 꼴로 문서 = 실제.
  ④ 표가 틀린 꼴 — `manage.py check` · 보통 경로 요청은 서고 문서를 만들 때만 정해진 ValueError(마운트 문서 500).
  ⑤ mypy strict 0 — 정본 · 표 · 3.2 `api.py` 둘(`--strict` · django-stubs).
exit 0 = 전 단언 통과 · 1 = 불일치 · 실행 불능.

  --canonical <파일>  정본 대신 그 파일을 붙여 돈다(옛 시제품 정본이 붉은지 보는 대조용).
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True

ROOT: Path = Path(__file__).resolve().parents[2]
FIXTURE: Path = ROOT / "workspace" / "eval" / "fixtures" / "pre_route_behavior"
CANONICAL: Path = ROOT / "dddjango" / "scripts" / "pre_route_responses_canonical.py"
PROBE_PY: Path = ROOT / ".venv-probe" / "bin" / "python"
CANON_REL: str = "framework/ninja/pre_route_responses.py"
TABLE_REL: str = "framework/ninja/pre_route_response_table.py"
MYPY_TARGETS: "tuple[str, ...]" = (CANON_REL, TABLE_REL, "toyproj/api.py", "toyproj/extra_api.py")
CHILD_TIMEOUT: int = 300
NOT_OPERATION_ANSWERS: "frozenset[int]" = frozenset({404})     # 없는 경로(변환기가 안 맞음) — operation 의 답이 아니다(설계 §3.1)
WATCHED_HEADERS: "tuple[str, ...]" = ("Retry-After", "Service-Maintenance-Ends-At")
TOKEN: "dict[str, str]" = {"HTTP_AUTHORIZATION": "Bearer good"}
CROSS: "dict[str, str]" = {"HTTP_SEC_FETCH_SITE": "cross-site"}
MANY_FIELDS: str = "&".join(f"k{i}=v" for i in range(1001))   # DATA_UPLOAD_MAX_NUMBER_FIELDS(1000) 넘김

# ① operation 마다 생성 문서 status 집합(마운트 문서 · 빠짐 · 남는 operation 없음)
DOCS: "dict[str, dict[str, list[int]]]" = {
    "api": {
        "GET /api/books/{book_id}": [200, 401, 422, 503],            # 클래스 인증 · int 경로 변수(변환기 없음)
        "POST /api/books": [201, 400, 401, 403, 413, 422, 503],      # JSON 몸통 · BC 503 + 점검 503
        "GET /api/health": [200],                                    # 점검 · 다른 사이트 모두 뺌(exempt · GET)
        "GET /api/shelves/{code}": [200, 503],                       # 제약 없는 글자 경로 변수
        "POST /api/webhook": [200, 503],                             # 다른 사이트 거절 뺌(exempt POST)
        "GET /api/webhook": [200, 503],                              # 같은 경로 GET — 다른 사이트 거절은 안전하지 않은 메서드만
        "PUT /api/webhook": [200, 403, 503],                         # 같은 경로 PUT — exempt 는 POST 만 빼므로 403 그대로
        "GET /api/search": [200, 400, 503],                          # 기본값 있는 글자 쿼리 — 422 없음 · 칸 수 상한 400
        "GET /api/search-required": [200, 400, 422, 503],            # 필수 쿼리
        "GET /api/x/plain-auth": [200, 401, 503],                    # 함수 인증(문서 security 없음)
        "GET /api/x/int-conv/{item_id}": [200, 503],                 # {int:x} 변환기 — 틀리면 404
        "GET /api/x/uuid-conv/{item_id}": [200, 503],                # {uuid:x} 변환기
        "GET /api/x/uuid-plain/{item_id}": [200, 422, 503],          # 변환기 없는 UUID
        "GET /api/x/opt-str": [200, 400, 503],                       # Optional[str]
        "GET /api/x/filter": [200, 400, 503],                        # Query[Schema] 선택 칸
        "GET /api/x/list-str": [200, 400, 503],                      # list[str] 쿼리
        "POST /api/x/form": [200, 400, 403, 413, 422, 503],          # Form — 깨진 JSON 400 없음(상한 400 은 HTML)
        "POST /api/x/upload": [200, 400, 403, 413, 422, 503],        # File
        "POST /api/x/session": [200, 401, 403, 503],                 # 쿠키 인증 — CSRF 403
        "POST /api/x/throttled": [200, 403, 429, 503],               # ninja throttle
        "POST /api/x/item": [200, 400, 403, 413, 422, 503],          # JSON 몸통
        "POST /api/x/attempt": [200, 403, 429, 503],                 # BC 429(머리 보충) + throttle 429 합침
        "GET /api/s/router-auth": [200, 401, 503],                   # Router 단위 인증
        "GET /api/public/item": [200, 503],                          # 같은 Router 두 번 — 공개 쪽
        "GET /api/private/item": [200, 401, 503],                    # 같은 Router 두 번 — 인증 쪽
        "GET /api/p/child/leaf": [200, 401, 429, 503],               # Router 중첩 — 부모 인증 · throttle
        "GET /api/dup/open": [200, 503],                             # 같은 operation_id — 공개
        "GET /api/dup/closed": [200, 401, 503],                      # 같은 operation_id — 인증
        "GET /api/conv/positive/{book_id}": [200, 422, 503],         # {int:x} + 값 제약
        "GET /api/conv/slug-int/{code}": [200, 422, 503],            # {slug:x} 인데 int
        "POST /api/conv/session-exempt": [200, 401, 403, 503],       # 쿠키 인증 + csrf_exempt — 403 은 다른 사이트 거절뿐
    },
    "api2": {                                                        # API 단위 쿠키 인증 · 점검 503 은 이름공간 밖
        "GET /api2/api-auth": [200, 401],
        "GET /api2/api-auth-off": [200],
        "POST /api2/api-auth-post": [200, 401, 403],
    },
    "api3": {                                                        # ninja_extra
        "GET /api3/ctl/a": [200, 401, 403],
        "GET /api3/perm/b": [200, 401, 403],
        "GET /api3/noauth/c": [200, 403],
        "GET /api3/pub/list": [200, 406],                            # AllowAny 상속(바꾸지 않음) · 표 `operations` 406
        "GET /api3/pub/ro": [200, 403],                              # 한계(§8): 읽기만 허용 권한의 GET 403
        "GET /api3/pub/either": [200, 403],                          # 한계(§8): `A | AllowAny`
        "GET /api3/closed/x": [200, 403],                            # AllowAny 상속 + has_permission 바꿈
        "GET /api3/thr/a": [200, 429],                               # 컨트롤러 throttle
        "GET /api3/thr2/b": [200, 429],                              # 한계(§8): 기본 비율 없는 @throttle
    },
    "apib": {                                                        # 같은 Router 두 번(인증 쪽 먼저) · 여러 메서드
        "GET /apib/private/item": [200, 401],
        "GET /apib/public/item": [200],
        "GET /apib/m/both": [200, 401],
        "POST /apib/m/both": [200, 401, 403],
    },
}
# 고른 (이름공간, operation, status) 의 몸통 꼴 `<media>:<component | string>` 과 머리 `h:<이름>`
DETAIL: str = "application/json:NinjaDetailOut"
HTML: str = "text/html:string"
PARTS: "dict[tuple[str, str, int], list[str]]" = {
    ("api", "POST /api/books", 503): ["application/json:BookShelfBusyError", "application/json:ServiceMaintenanceOut",
                                      "h:Retry-After", "h:Service-Maintenance-Ends-At"],
    ("api", "POST /api/books", 400): [DETAIL, HTML],
    ("api", "POST /api/books", 401): [DETAIL],
    ("api", "POST /api/books", 422): ["application/json:NinjaValidationOut"],
    ("api", "POST /api/books", 413): [HTML],
    ("api", "POST /api/x/form", 400): [HTML],
    ("api", "GET /api/search", 400): [HTML],
    ("api", "POST /api/x/session", 403): ["application/json:CrossSiteRequestRejectedOut", DETAIL],
    ("api", "POST /api/conv/session-exempt", 403): ["application/json:CrossSiteRequestRejectedOut"],
    ("api", "PUT /api/webhook", 403): ["application/json:CrossSiteRequestRejectedOut"],
    ("api", "POST /api/x/throttled", 429): [DETAIL, "h:Retry-After"],
    ("api", "POST /api/x/attempt", 429): ["application/json:TooManyAttemptsError", DETAIL, "h:Retry-After"],
    ("api", "GET /api/shelves/{code}", 503): ["application/json:ServiceMaintenanceOut", "h:Service-Maintenance-Ends-At"],
    ("api2", "POST /api2/api-auth-post", 403): ["application/json:CrossSiteRequestRejectedOut", DETAIL],
    ("api3", "GET /api3/pub/list", 406): ["application/json:NotAcceptableOut"],
    ("api3", "GET /api3/closed/x", 403): [DETAIL],
    ("api3", "GET /api3/thr/a", 429): [DETAIL, "h:Retry-After"],
    ("apib", "POST /apib/m/both", 403): ["application/json:CrossSiteRequestRejectedOut", DETAIL],
}

# 같은 이름 머리는 경로 코드(BC 오류 머리 보충)가 적은 정의를 그대로 둔다(셋째 확인 S2)
HEADER_DEFS: "dict[tuple[str, str, int, str], dict]" = {
    ("api", "POST /api/x/attempt", 429, "Retry-After"): {"required": True, "description": "다시 시도까지 초",
                                                         "schema": {"type": "integer"}},
    ("api", "POST /api/books", 503, "Retry-After"): {"schema": {"type": "integer"}},
}


def _req(rid: str, ns: str, op: str, status: int, path: str = "", **spec: object) -> dict:
    method, doc_path = op.split(" ", 1)
    return {"id": rid, "ns": ns, "op": op, "expect": status, "method": method.lower(), "path": path or doc_path, **spec}


MAINT: "dict[str, object]" = {"MAINTENANCE_MODE": True}
SMALL: "dict[str, object]" = {"DATA_UPLOAD_MAX_MEMORY_SIZE": 10}
JSON: str = "application/json"
# ② 실제 응답 — 문서에 있는 status 면 그 꼴이어야 한다
REQUESTS: "list[dict]" = [
    _req("책 토큰 없음", "api", "GET /api/books/{book_id}", 401, "/api/books/1"),
    _req("책 번호 글자", "api", "GET /api/books/{book_id}", 422, "/api/books/x", headers=TOKEN),
    _req("책 몸통 칸 빠짐", "api", "POST /api/books", 422, data="{}", content_type=JSON, headers=TOKEN),
    _req("책 BC 503(Retry-After)", "api", "POST /api/books", 503, data='{"title": "busy"}', content_type=JSON, headers=TOKEN),
    _req("책 다른 사이트", "api", "POST /api/books", 403, data='{"title": "a"}', content_type=JSON, headers={**TOKEN, **CROSS}),
    _req("책 깨진 JSON", "api", "POST /api/books", 400, data="{x", content_type=JSON, headers=TOKEN),
    _req("책 몸통 상한", "api", "POST /api/books", 400, data='{"title": "aaaaaaaaaaaaaaaaaaaa"}', content_type=JSON, headers=TOKEN,
         settings=SMALL),
    _req("책 점검 중", "api", "POST /api/books", 503, data='{"title": "a"}', content_type=JSON, headers=TOKEN, settings=MAINT),
    _req("선반 점검 중", "api", "GET /api/shelves/{code}", 503, "/api/shelves/a", settings=MAINT),
    _req("건강 점검 중(뺌)", "api", "GET /api/health", 200, settings=MAINT),
    _req("웹훅 다른 사이트(뺌)", "api", "POST /api/webhook", 200, headers=CROSS),
    _req("웹훅 GET 다른 사이트(안전 메서드)", "api", "GET /api/webhook", 200, headers=CROSS),
    _req("웹훅 PUT 다른 사이트(exempt 는 POST 만)", "api", "PUT /api/webhook", 403, headers=CROSS),
    _req("검색 q 없음", "api", "GET /api/search", 200),
    _req("검색 칸 1001", "api", "GET /api/search", 400, query="q=a&" + MANY_FIELDS),
    _req("필수 검색 q 없음", "api", "GET /api/search-required", 422),
    _req("함수 인증 키 없음", "api", "GET /api/x/plain-auth", 401),
    _req("int 변환기 글자", "api", "GET /api/x/int-conv/{item_id}", 404, "/api/x/int-conv/abc"),
    _req("uuid 변환기 글자", "api", "GET /api/x/uuid-conv/{item_id}", 404, "/api/x/uuid-conv/abc"),
    _req("변환기 없는 uuid 글자", "api", "GET /api/x/uuid-plain/{item_id}", 422, "/api/x/uuid-plain/abc"),
    _req("선택 글자 쿼리 깨진 글자", "api", "GET /api/x/opt-str", 200, query="q=%FF"),
    _req("선택 칸 Schema 쿼리", "api", "GET /api/x/filter", 200, query="q=a&tag=b"),
    _req("글자 목록 쿼리", "api", "GET /api/x/list-str", 200, query="tags=a&tags=b"),
    _req("Form 칸 빠짐", "api", "POST /api/x/form", 422, data={}),
    _req("Form 에 깨진 JSON", "api", "POST /api/x/form", 422, data="{x", content_type=JSON),
    _req("Form 몸통 상한", "api", "POST /api/x/form", 400, data={"name": "a" * 50}, settings=SMALL),
    _req("File 없음", "api", "POST /api/x/upload", 422, data={}),
    _req("쿠키 인증 CSRF", "api", "POST /api/x/session", 403, client="csrf"),
    _req("쿠키 인증 로그인 없음", "api", "POST /api/x/session", 401),
    _req("ninja throttle 둘째", "api", "POST /api/x/throttled", 429, repeat=2),
    _req("JSON 몸통 빔", "api", "POST /api/x/item", 422, data="", content_type=JSON),
    _req("JSON 몸통 깨짐", "api", "POST /api/x/item", 400, data="{x", content_type=JSON),
    _req("JSON 몸통 상한", "api", "POST /api/x/item", 400, data='{"title": "aaaaaaaaaaaaaaaaaaaa"}', content_type=JSON,
         settings=SMALL),
    _req("Router 인증 토큰 없음", "api", "GET /api/s/router-auth", 401),
    _req("같은 Router 공개 쪽", "api", "GET /api/public/item", 200),
    _req("같은 Router 인증 쪽", "api", "GET /api/private/item", 401),
    _req("중첩 Router 토큰 없음", "api", "GET /api/p/child/leaf", 401),
    _req("같은 operation_id 공개", "api", "GET /api/dup/open", 200),
    _req("같은 operation_id 인증", "api", "GET /api/dup/closed", 401),
    _req("변환기 + 값 제약", "api", "GET /api/conv/positive/{book_id}", 422, "/api/conv/positive/0"),
    _req("slug 변환기 int", "api", "GET /api/conv/slug-int/{code}", 422, "/api/conv/slug-int/abc"),
    _req("csrf_exempt CSRF 강제", "api", "POST /api/conv/session-exempt", 401, client="csrf"),
    _req("csrf_exempt 다른 사이트", "api", "POST /api/conv/session-exempt", 403, client="csrf", headers=CROSS),
    _req("API 쿠키 인증 로그인 없음", "api2", "GET /api2/api-auth", 401),
    _req("API 쿠키 인증 끈 경로 · 점검 중(이름공간 밖)", "api2", "GET /api2/api-auth-off", 200, settings=MAINT),
    _req("API 쿠키 인증 POST CSRF", "api2", "POST /api2/api-auth-post", 403, client="csrf"),
    _req("ninja_extra 인증 + 권한 토큰 없음", "api3", "GET /api3/ctl/a", 401),
    _req("ninja_extra 권한 거절", "api3", "GET /api3/perm/b", 403, headers=TOKEN),
    _req("ninja_extra 인증 없는 권한", "api3", "GET /api3/noauth/c", 403),
    _req("AllowAny 상속(바꾸지 않음)", "api3", "GET /api3/pub/list", 200),
    _req("표 operations 406", "api3", "GET /api3/pub/list", 406, headers={"HTTP_ACCEPT": "text/csv"}),
    _req("읽기만 허용 GET", "api3", "GET /api3/pub/ro", 200),
    _req("A | AllowAny", "api3", "GET /api3/pub/either", 200),
    _req("AllowAny 상속 + has_permission 바꿈", "api3", "GET /api3/closed/x", 403),
    _req("ninja_extra throttle 둘째(Retry-After)", "api3", "GET /api3/thr/a", 429, repeat=2),
    _req("기본 비율 없는 @throttle 둘째", "api3", "GET /api3/thr2/b", 200, repeat=2),
    _req("뒤집은 같은 Router 인증 쪽", "apib", "GET /apib/private/item", 401),
    _req("뒤집은 같은 Router 공개 쪽", "apib", "GET /apib/public/item", 200),
    _req("여러 메서드 GET(CSRF 없음)", "apib", "GET /apib/m/both", 401, client="csrf"),
    _req("여러 메서드 POST CSRF", "apib", "POST /apib/m/both", 403, client="csrf"),
]
# ③ Django 400 처리기를 JSON 으로 — 표 `BAD_REQUEST_RESPONSE` = JSON Schema · URLconf `handler400`
JSON400_PARTS: "dict[tuple[str, str, int], list[str]]" = {
    ("api", "POST /api/x/item", 400): ["application/json:BadRequestOut", DETAIL],
    ("api", "POST /api/x/form", 400): ["application/json:BadRequestOut"],
    ("api", "GET /api/search", 400): ["application/json:BadRequestOut"],
}
JSON400_REQUESTS: "list[dict]" = [
    _req("JSON 처리기 · 몸통 상한", "api", "POST /api/x/item", 400, data='{"title": "aaaaaaaaaaaaaaaaaaaa"}', content_type=JSON,
         settings=SMALL),
    _req("JSON 처리기 · 깨진 JSON", "api", "POST /api/x/item", 400, data="{x", content_type=JSON),
    _req("JSON 처리기 · Form 몸통 상한", "api", "POST /api/x/form", 400, data={"name": "a" * 50}, settings=SMALL),
    _req("JSON 처리기 · 쿼리 칸 1001", "api", "GET /api/search", 400, query="q=a&" + MANY_FIELDS),
]
# ④ 표가 틀린 꼴 → (표 파일, 실패하는 이름공간, ValueError 글)
ALL_NS: "tuple[str, ...]" = ("api", "api2", "api3", "apib")
FAILS: "list[tuple[str, tuple[str, ...], str]]" = [
    ("bad_unknown_key", ALL_NS, "unknown pre-route row keys: ['namespace']"),
    ("bad_empty_tuple", ALL_NS, "empty narrowing tuple in pre-route row 403"),
    ("bad_operations_form", ALL_NS, "pre-route operation must be 'METHOD /path': pub_list"),
    ("bad_operations_target", ("api3",), "pre-route operation not in this document: GET /api3/pub/lists"),
    ("bad_operations_namespace", ALL_NS, "pre-route row 406 with operations needs exactly one namespace"),
    ("bad_status", ALL_NS, "pre-route status out of 400-599: 302"),
    ("bad_methods", ALL_NS, "pre-route methods must be upper-case HTTP methods: ('post',)"),
    ("bad_component_collision", ("api",), "component name collision: BookOut"),
]


def _env() -> "dict[str, str]":
    drop: "tuple[str, ...]" = ("DJANGO_", "PYTEST_", "MYPY")
    env: "dict[str, str]" = {k: v for k, v in os.environ.items()
                             if not k.startswith(drop) and k not in ("PYTHONPATH", "PYTHONHOME", "PYTHONSTARTUP")}
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return env


def _toy(td: Path, canonical: Path, table: "Path | None" = None) -> Path:
    """장난감 사본 — 정본(실행 때 복사) · (있으면) 표 파일을 바꿔 둔다."""
    toy: Path = td / "toy"
    shutil.copytree(FIXTURE / "toy", toy, ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copyfile(canonical, toy / CANON_REL)
    if table is not None:
        shutil.copyfile(table, toy / TABLE_REL)
    return toy


def _probe(toy: Path, plan: dict) -> dict:
    plan_path: Path = toy / "plan.json"
    out_path: Path = toy / "out.json"
    plan_path.write_text(json.dumps({**plan, "out": str(out_path)}, ensure_ascii=False), encoding="utf-8")
    proc = subprocess.run([str(PROBE_PY), "-B", "probe.py", str(plan_path)], cwd=toy, capture_output=True, text=True,
                          env=_env(), timeout=CHILD_TIMEOUT)
    if proc.returncode != 0 or not out_path.is_file():
        raise RuntimeError(f"탐침 실패(exit {proc.returncode}): {(proc.stdout + proc.stderr)[-1500:]}")
    return json.loads(out_path.read_text(encoding="utf-8"))


def _ref_name(schema: dict) -> str:
    ref: object = schema.get("$ref")
    return ref.rsplit("/", 1)[1] if isinstance(ref, str) else str(schema.get("type", "inline"))


def _parts(response: dict) -> "list[str]":
    """문서 응답 항목 → `<media>:<component | type>` · `h:<머리>`."""
    out: "list[str]" = []
    for media, item in (response.get("content") or {}).items():
        schema: dict = item.get("schema") or {}
        for one in schema.get("anyOf") or [schema]:
            out.append(f"{media}:{_ref_name(one)}")
    out += [f"h:{name}" for name in response.get("headers") or {}]
    return sorted(out)


def _resolve(schema: dict, components: dict) -> dict:
    seen: int = 0
    while "$ref" in schema and seen < 32:
        schema = components.get(schema["$ref"].rsplit("/", 1)[1], {})
        seen += 1
    return schema


TYPES: "dict[str, tuple[type, ...]]" = {"object": (dict,), "array": (list,), "string": (str,), "integer": (int,),
                                        "number": (int, float), "boolean": (bool,), "null": (type(None),)}


def _conforms(value: object, schema: dict, components: dict, where: str = "$") -> "list[str]":
    """JSON Schema 부분 집합(`$ref` · `anyOf` · `type` · `properties` · `required` · `items` · `enum` · `const`) 대조."""
    schema = _resolve(schema, components)
    if "anyOf" in schema:
        return [] if any(not _conforms(value, s, components, where) for s in schema["anyOf"]) else \
            [f"{where}: anyOf 어느 꼴과도 맞지 않는다({json.dumps(value, ensure_ascii=False)[:80]})"]
    kind: object = schema.get("type")
    if isinstance(kind, str):
        wanted: "tuple[type, ...]" = TYPES.get(kind, (object,))
        if not isinstance(value, wanted) or (isinstance(value, bool) and kind in ("integer", "number")):
            return [f"{where}: {kind} 아님({type(value).__name__})"]
    if "enum" in schema and value not in schema["enum"]:
        return [f"{where}: enum 밖 {value!r}"]
    if "const" in schema and value != schema["const"]:
        return [f"{where}: const 아님 {value!r}"]
    problems: "list[str]" = []
    if isinstance(value, dict):
        problems += [f"{where}: 필수 칸 `{k}` 없음" for k in schema.get("required", []) if k not in value]
        for key, sub in (schema.get("properties") or {}).items():
            if key in value:
                problems += _conforms(value[key], sub, components, f"{where}.{key}")
    if isinstance(value, list) and isinstance(schema.get("items"), dict):
        for i, item in enumerate(value):
            problems += _conforms(item, schema["items"], components, f"{where}[{i}]")
    return problems


def _ops(doc: dict) -> "dict[str, dict]":
    return {f"{m.upper()} {p}": op for p, item in (doc.get("paths") or {}).items() for m, op in item.items()}


def _doc_checks(docs: dict, expected: "dict[str, dict[str, list[int]]] | None",
                parts: "dict[tuple[str, str, int], list[str]]", tag: str) -> "list[str]":
    fails: "list[str]" = []
    for ns, entry in docs.items():
        if entry["status"] != 200 or entry["doc"] is None:
            fails.append(f"{tag} {ns} 마운트 문서 status {entry['status']}")
    for ns, want in (expected or {}).items():
        doc: dict = docs.get(ns, {}).get("doc") or {}
        got: "dict[str, list[int]]" = {k: sorted(int(s) for s in op["responses"]) for k, op in _ops(doc).items()}
        for key in sorted(set(want) | set(got)):
            if want.get(key) != got.get(key):
                fails.append(f"{tag} 문서 {ns} `{key}` status {got.get(key)} ≠ 기대 {want.get(key)}")
    for (ns, key, status), want_parts in parts.items():
        op: dict = _ops(docs.get(ns, {}).get("doc") or {}).get(key, {})
        response: "dict | None" = (op.get("responses") or {}).get(str(status))
        got_parts: "list[str] | None" = _parts(response) if response is not None else None
        if got_parts != sorted(want_parts):
            fails.append(f"{tag} 문서 {ns} `{key}` {status} 꼴 {got_parts} ≠ 기대 {sorted(want_parts)}")
    for (ns, key, status, name), want_def in (HEADER_DEFS if expected is not None else {}).items():
        op = _ops(docs.get(ns, {}).get("doc") or {}).get(key, {})
        got_def: object = ((op.get("responses") or {}).get(str(status)) or {}).get("headers", {}).get(name)
        if got_def != want_def:
            fails.append(f"{tag} 문서 {ns} `{key}` {status} 머리 `{name}` 정의 {got_def} ≠ 경로 코드가 적은 {want_def}")
    return fails


def _response_checks(docs: dict, responses: dict, requests: "list[dict]", tag: str) -> "list[str]":
    fails: "list[str]" = []
    for spec in requests:
        got: "dict | None" = responses.get(spec["id"])
        label: str = f"{tag} 실제 «{spec['id']}» {spec['op']}"
        if got is None:
            fails.append(f"{label}: 응답 없음")
            continue
        status: int = got["status"]
        if status != spec["expect"]:
            fails.append(f"{label}: status {status} ≠ 기대 {spec['expect']} · {got['body'][:120]!r}")
            continue
        doc: dict = docs[spec["ns"]]["doc"] or {}
        op: dict = _ops(doc).get(spec["op"], {})
        declared: "dict | None" = (op.get("responses") or {}).get(str(status))
        if declared is None:
            if status not in NOT_OPERATION_ANSWERS:
                fails.append(f"{label}: 실제 {status} 가 문서에 없다(문서 {sorted(int(s) for s in op.get('responses') or {})})")
            continue
        media: str = got["headers"].get("Content-Type", "").split(";")[0].strip()
        content: dict = declared.get("content") or {}
        if media not in content:
            fails.append(f"{label}: 실제 media `{media}` 가 문서 {status} 의 {sorted(content)} 밖")
            continue
        if media == "application/json":
            try:
                body: object = json.loads(got["body"])
            except ValueError:
                fails.append(f"{label}: JSON 몸통이 아니다 {got['body'][:80]!r}")
                continue
            problems: "list[str]" = _conforms(body, content[media].get("schema") or {},
                                              (doc.get("components") or {}).get("schemas") or {})
            fails += [f"{label}: 몸통이 문서 꼴이 아니다 — {p}" for p in problems]
        headers: "set[str]" = set(declared.get("headers") or {})
        fails += [f"{label}: 실제 머리 `{h}` 가 문서 {status} 머리 {sorted(headers)} 밖" for h in WATCHED_HEADERS
                  if h in got["headers"] and h not in headers]
    return fails


def _fail_checks(td: Path, canonical: Path) -> "list[str]":
    fails: "list[str]" = []
    for name, failing, message in FAILS:
        toy: Path = _toy(td / name, canonical, FIXTURE / "tables" / f"{name}.py")
        tag: str = f"[표 {name}]"
        try:
            got: dict = _probe(toy, {"mode": "fail", "settings": {}})
        except RuntimeError as exc:                   # import 때 죽음 — 문서를 만들 때만 실패해야 한다(셋째 확인 S1)
            fails.append(f"{tag} 장난감이 문서 생성 전에 죽는다 — {str(exc)[-400:]}")
            continue
        if got["check"] != "ok":
            fails.append(f"{tag} manage.py check 가 서야 한다 — 지금 {got['check'][:160]}")
        if got["plain_request"] != 200:
            fails.append(f"{tag} 보통 경로 요청(GET /api/health)이 서야 한다 — 지금 {got['plain_request']}")
        for ns in ALL_NS:
            want: str = f"ValueError: {message}" if ns in failing else "ok"
            if got["schema"].get(ns) != want:
                fails.append(f"{tag} {ns} 문서 생성 {got['schema'].get(ns)!r} ≠ 기대 {want!r}")
            want_status: int = 500 if ns in failing else 200
            if got["mounted"].get(ns) != want_status:
                fails.append(f"{tag} {ns} 마운트 문서 status {got['mounted'].get(ns)} ≠ 기대 {want_status}")
    return fails


def _mypy(td: Path, canonical: Path) -> "list[str]":
    toy: Path = _toy(td / "mypy", canonical)
    proc = subprocess.run([str(PROBE_PY), "-B", "-m", "mypy", "--config-file", "mypy.ini", "--cache-dir", str(td / "mypy-cache"),
                           *MYPY_TARGETS], cwd=toy, capture_output=True, text=True, env=_env(), timeout=CHILD_TIMEOUT)
    out: str = (proc.stdout + proc.stderr).strip()
    want: str = f"Success: no issues found in {len(MYPY_TARGETS)} source files"
    return [] if proc.returncode == 0 and want in out else [f"[mypy strict] exit {proc.returncode} — {out[-1500:]}"]


def main() -> int:
    canonical: Path = CANONICAL
    if "--canonical" in sys.argv[1:-1]:
        canonical = Path(sys.argv[sys.argv.index("--canonical") + 1]).resolve()
    if not PROBE_PY.is_file():
        print("FAIL — .venv-probe 부재(make probe-env 필요)")
        return 1
    if not canonical.is_file():
        print(f"FAIL — 정본 파일이 없다: {canonical}")
        return 1
    fails: "list[str]" = []
    with tempfile.TemporaryDirectory(prefix="pre-route-") as tmp:
        td: Path = Path(tmp)

        def main_stage() -> "list[str]":
            run: dict = _probe(_toy(td / "main", canonical), {"mode": "full", "settings": {}, "requests": REQUESTS})
            return (_doc_checks(run["docs"], DOCS, PARTS, "[기본]")
                    + _response_checks(run["docs"], run["responses"], REQUESTS, "[기본]"))

        def json_stage() -> "list[str]":
            run: dict = _probe(_toy(td / "json400", canonical, FIXTURE / "tables" / "json_handler400.py"),
                               {"mode": "full", "settings": {"ROOT_URLCONF": "toyproj.urls_json400"}, "requests": JSON400_REQUESTS})
            return (_doc_checks(run["docs"], None, JSON400_PARTS, "[JSON 400]")
                    + _response_checks(run["docs"], run["responses"], JSON400_REQUESTS, "[JSON 400]"))
        for stage, label in ((main_stage, "기본"), (json_stage, "JSON 400"), (lambda: _fail_checks(td, canonical), "표 실패 꼴"),
                             (lambda: _mypy(td, canonical), "mypy strict")):
            try:
                fails += stage()
            except (RuntimeError, subprocess.TimeoutExpired, OSError, ValueError, KeyError) as exc:
                fails.append(f"[{label}] 실행 불능 — {type(exc).__name__}: {str(exc)[-1200:]}")
    ops: int = sum(map(len, DOCS.values()))
    print(f"요약: 경로 앞 응답 동작 — 문서 operation {ops} · 꼴 {len(PARTS) + len(JSON400_PARTS)} · 머리 정의 {len(HEADER_DEFS)} · 실제 요청 "
          f"{len(REQUESTS) + len(JSON400_REQUESTS)} · 표 실패 꼴 {len(FAILS)} · mypy strict {len(MYPY_TARGETS)} 파일 · "
          f"어긋남 {len(fails)}")
    if fails:
        print("FAIL — 경로 앞 응답 정본 동작 스모크:")
        for f in fails:
            print("  - " + f.replace("\n", "\n    "))
        return 1
    print("PASS — 경로 앞 응답 정본 동작 스모크(생성 문서 = 실제 응답 · 표 검증 · mypy strict)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
