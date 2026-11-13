# 설계 — API 문서에 그 경로에서 날 수 있는 오류를 모두 적는다(F4-173)

설계 v3.1(2026-11-13 · v1 독립 검토 처분 §10 · v2 둘째 확인 처분 §11 · v3 셋째 확인 처분 §12 — 차단 0). 시제품 · 장난감 · 실행 로그는 `workspace/scratch/f4-173-openapi-errors/`(커밋하지 않음 — 재현 `repro.py` · v1 시제품 `proto/` · v2 시제품 `proto2/` · v3 시제품 `proto3/`(정본은 `make_v3.py` 가 짓는다) · 경로 잇기 장난감 `join3/` · 검토 장난감 `review-1/` · `review-2/` · Ninja 1.6.3 · ninja_extra 0.31.7 venv).

## 0. 요지

- **원칙(사용자 원문 · 2026-11-13)**: «openapi 문서는 해당 api 에서 발생하는 에러도 다 적는 게 맞다» · «이건 리팩토링 절차에도 들어가야». API 문서는 그 경로에서 날 수 있는 오류를 **누가 보내든**(경로 코드 · framework · 미들웨어 · 앞단) 정식 응답 선언으로 모두 적는다.
- **결정 «나»(사용자 · 01:52)**: 경로 앞에서 나는 오류는 경로마다 손으로 적지 않고 API 모듈의 정해진 꼴 하나가 자동으로 붙인다. Ninja 가 보내는 답(인증 401 · CSRF 403 · 권한 403 · throttle 429 · 몸통 400 · 입력 422)은 **경로의 Ninja 경로 객체(Operation)와 생성 문서 칸**을 읽어 그 경로에만 붙이고, 미들웨어 · 앞단 답은 프로젝트 표 한 곳에 적는다. 설계 처리(질문 생략 · 이의 시 뒤집음): 사용자에게 보인 예는 «API 설정 파일 한 곳» 이었으나 이웃 규칙(#437 api.py 닫힌 목록 · #415 framework 모듈) 때문에 `api.py` 의 클래스 하나 + `framework/ninja/` 파일 둘로 나눈다.
- 경로 코드는 그대로다 — BC 오류는 지금처럼 `response=`(직접 반환하는 타입 그대로). **BC 오류의 머리**(`Retry-After` 등)는 그 경로의 `openapi_extra` 로 머리만 덧붙인다(정수 키).
- 빠짐은 검사기(#63)가 잡는다 → 리팩토링 R1 빚으로 저절로 들어간다.

## 1. 재현과 뿌리

배포판 2.36.0(`check-openapi-error-declaration.py` · 장난감 6 · `repro.py`):

| 꼴 | 결과 |
|---|---|
| 경로 코드가 직접 보내는 BC 오류의 `Retry-After` 머리를 `openapi_extra` 로 | 막힘(exit 2 · `openapi-extra`) |
| framework 401 · 422 를 `openapi_extra` 로 | 막힘 |
| API 모듈 문서 생성 재정의로 경로마다 401 · 422 · 403 · 503 | 막힘(`openapi-override`) |
| 401 을 `response=` 에 BC 밖 Schema 로 | 검사기 통과 · 규칙 글은 금지(어긋남) |
| 대조군(BC 오류만 · 성공 200 머리 보충) | 통과 |

뿌리:

- 규칙 글끼리 부딪친다. architecture-api §14.3 «상태 코드별 response body schema 와 header» · §5.4 «소비자가 계산하거나 따로 보일 값은 … 승인된 응답 머리에도 싣고» ↔ implementation-django-ninja §6.2 «framework 오류 경계 — framework status 를 BC `response={...}` 에 광고하지 않는다» · «응답 선언과 OpenAPI — 오류 응답(4xx · 5xx) 항목을 `openapi_extra` 로 보충 · override · monkeypatch · postprocessor 금지»(#63). 규칙이 싣게 한 BC 오류의 `Retry-After` 조차 문서에 적을 길이 없어 12-slot slot 12 는 «오류 status 의 머리는 생성 OpenAPI 에 선언되지 않으므로 operation `description` 에도 적는다» 로 돌아갔다.
- 금지의 목적(결정 D27 · 2026-08-06): 문서와 실제 동작이 어긋나지 않게 — api.py 의 전역 handler · 도메인 예외 목록을 걷으며 함께 들어온 금지다. 경로 앞 오류를 «적지 말라» 고 판단한 기록은 없다(그때 고려 밖).
- 자매 플러그인 dddjango-web 은 API 문서(스냅샷)를 사실의 출처로 쓰고 문서 밖 가정을 «계약 위험» 으로 표기한다 — 문서가 빠지면 그쪽 위험만 는다. 더 엄격한 기준을 따로 거는 고침이 아니다.

## 2. 시제품에서 새로 본 것(Ninja 1.6.3 · ninja_extra 0.31.7)

1. **숫자 문자열 키는 문서를 망가뜨린다.** Ninja 는 `response=` 로 지은 응답 키를 정수(503)로 두고 경로 `openapi_extra` 를 깊게 합친다. `{"responses": {"503": …}}` 처럼 문자열 키를 쓰면 정수 키 항목과 따로 남아 JSON 에 `"503"` 이 두 번 찍히고 읽는 쪽은 뒤의 것(머리만)을 갖는다 — 응답 몸통 · 필수 `description` 이 사라진다. 섞인 키는 `export_openapi_schema --sorted` 를 `TypeError` 로 죽인다(검토 S1). 지금 #63 이 허용하는 «성공 status 메타데이터 보충» 도 숫자 문자열 키를 받으니 같은 구멍이다(현장 21 파일은 모두 정수 키라 아직 안 터짐).
2. **생성 문서 칸만으로는 경로를 가를 수 없는 답이 많다**(검토 B2 · I1 재현): 함수 인증(`auth=plain_auth`)은 `security` 가 없는데 401 · 세션 쿠키 인증은 POST 에 CSRF 403 · throttle 429 · ninja_extra 권한 403 은 문서에 흔적이 없다. 반대로 `Optional[str]` · `list[str]` 쿼리(문서 `anyOf` · `array`)와 `{int:x}` · `{uuid:x}` 경로 변환기(틀리면 404 HTML)는 422 가 나지 않고, Form · File 몸통은 JSON 400 이 아니라 422 가 난다. 경로 객체(Operation)를 operationId 로 이으면 경로마다 인증 · CSRF · throttle · 권한 · 변환기를 정확히 안다(`proto2/run_review.py` — 문서 ↔ 실제 맞음).
3. **몸통 400 은 둘이다**: 깨진 JSON → Ninja `{"detail": "Cannot parse request body"}`(JSON 몸통만) · Django 몸통 상한(`DATA_UPLOAD_MAX_MEMORY_SIZE` 2.5 MB) → `text/html` 400(JSON · 폼 몸통 모두 — 검토 I2).
4. 같은 status 를 경로 코드의 BC 오류와 경로 앞 답이 함께 쓰면 한 응답 항목에 몸통 둘(`anyOf`)과 머리 합집합을 싣는다(BC 503 + 점검 503 — 문서와 실제 맞음).
5. 플러그인이 정한 서버렌더 `process_exception` 미들웨어는 `DEBUG=False` 에서 API 경로의 미식별 예외도 503 HTML 로 바꾼다(검토 I6) — API 경로에 답하는 미들웨어인지가 프로젝트마다 다르다.

v2 시제품 문서와 실제 응답(`proto2/run_review.py` · `run_proto.py`):

```
GET  /api/books/{book_id}   토큰 인증 · int 경로      → 200 401 422 503
POST /api/books             토큰 인증 · JSON · BC 503 → 201 400 401 403 413 422 503(anyOf · Retry-After · Service-Maintenance-Ends-At)
GET  /api/x/plain-auth      함수 인증                 → 200 401 503
GET  /api/x/int-conv/{x}    {int:x} 변환기             → 200 503          (실제 abc → 404 HTML · 422 없음)
GET  /api/x/opt-str         Optional[str] 쿼리        → 200 503          (실제 422 없음)
POST /api/x/form            Form 몸통                 → 200 400(HTML) 403 413 422 503
POST /api/x/session         세션 쿠키 인증             → 200 401 403(CSRF) 503
POST /api/x/throttled       throttle                  → 200 403 429 503
GET  /api3/perm/b           ninja_extra 권한           → 200 401 403
GET  /api/health            점검 제외 경로             → 200
```

## 3. 꼴(코드)

### 3.1 파일 셋

| 파일 | 누가 정하나 | 내용 |
|---|---|---|
| `framework/ninja/pre_route_responses.py` | 플러그인(글자 그대로) | 붙이는 함수 `add_pre_route_responses(api, schema)` · 도움 함수 · **Ninja 기본 행 `NINJA_RESPONSES` 와 그 몸통 Schema**(관찰값). 프로젝트가 고치지 않는다 — 검사기가 플러그인 정본과 AST 로 맞춘다(import 는 집합 · `__future__` 뺌 · 정의만 비교 — 검토 S2). 참조 글(implementation-django-ninja)에 같은 글을 싣고, 저장소 시험이 참조 글 코드 블록 = 검사기 정본을 지킨다. 이웃 검사기(#415 framework 모듈은 그 라이브러리 import · #493 · #645 · #647 주석 · `Any` 금지)를 정본이 스스로 지킨다(검토 B1). |
| `framework/ninja/pre_route_response_table.py` | 프로젝트(설계 G1 승인) | 프로젝트 행 `PRE_ROUTE_RESPONSES`(글자 값 튜플)와 그 몸통 Schema · `NOT_API_MIDDLEWARE`(API 경로에 답하지 않는 미들웨어 점 경로 글자 목록 — 4.1 d 가 뺀다 · 검토 I6). 기본 행은 여기 두지 않는다(빼서 401 · 422 를 끌 수 없다 — 검토 I5). |
| `<project>/api.py` | 플러그인 꼴 + 프로젝트 이름 | 3.2 클래스 하나와 루트 API 객체. 루트 API 가 둘 이상이면 모두 이 클래스로 짓는다(자리는 F4-150 판 몫 — 검토 Q1). |

**Ninja 기본 행**(정본 · 판정은 3.3):

| status | `when` | 몸통(관찰) |
|---|---|---|
| 401 | `auth` 경로에 인증이 있다(클래스 · 함수 · API · Router 단위) | `{"detail": str}` |
| 403 | `csrf` 쿠키 인증(CSRF 확인)이고 안전하지 않은 메서드 | `{"detail": str}` |
| 403 | `permission` ninja_extra 권한(AllowAny 밖) | `{"detail": str}` |
| 429 | `throttle` 경로에 throttle 이 있다(API · Router · operation 합) | `{"detail": str}` · 선택 머리 `Retry-After`(ninja_extra 가 싣는다 — 검토 NI2) |
| 400 | `json_body` JSON 몸통을 받는다 — 깨진 JSON | `{"detail": str}` |
| 400 | `body` 몸통을 받는다 — Django 몸통 상한 | 표 파일 `BAD_REQUEST_RESPONSE`(기본 `text/html` · 프로젝트가 JSON `handler400` 을 두면 그 꼴 — 검사기 b 가 루트 URLconf 의 `handler400` 과 대조 · 셋째 확인 N6) |
| 400 | `query` 쿼리 parameter 가 있다 — Django 칸 수 상한(`DATA_UPLOAD_MAX_NUMBER_FIELDS`) | 위와 같음(검토 NS3) |
| 422 | `input` 입력이 틀릴 수 있다 | `{"detail": [{type, loc, msg}]}` |

**프로젝트 행**: 응답을 직접 만드는 미들웨어와 앞단 — `status`(400 ~ 599) · `when`(`all` · `auth` · `body` · `input`) · 선택 `methods` · `namespaces`(API 이름공간) · `exempt`(`(메서드 | None, "<settings 이름>")` — 그 설정 목록 경로는 뺀다 · 목록은 base settings 에 둔다 — 검토 S7) · `operations`(`"GET /api/orders/{order_id}"` 꼴 — 메서드 + 생성 문서 경로 · 4.1 c 식별 글의 `METHOD 경로` 몫과 같은 글 · 그 경로에만: 승인 endpoint 의 406 · 415 · 인증 안 `HttpError(403)` 처럼 경로 객체로 못 가르는 답. operationId 는 ninja_extra 가 실행마다 바꾸므로 열쇠로 쓰지 않는다 — 검토 NB1) · `description` · `body`(같은 파일 Schema) 또는 `media_type` · 선택 `headers`.

**표 검증**(검토 NI4 · 셋째 확인 N1 · N2 · S1): 정적 몫은 검사기 4.1 b 가 G2 전에 잡고, 정본은 **문서를 만들 때**(import 때가 아니다 — import 실패는 `manage.py check` · 시험 수집 · 서버렌더까지 죽인다) 다시 본다 — 닫힌 칸 이름(TypedDict 의 필수 · 선택 키 집합 밖이면 실패) · `status` 400 ~ 599 · `methods` 는 대문자 HTTP 메서드 · `methods` · `namespaces` · `operations` 빈 튜플 금지 · `operations` 를 단 행은 `namespaces` 하나가 필수이고 그 이름공간 문서에서만 대상을 대조한다(꼴 `METHOD /경로` · 문서에 없으면 실패) · 경로 객체를 잇지 못하면 실패 · (메서드, 문서 경로)가 겹치면 Ninja 처럼 뒤의 것이 이긴다(문서와 같은 쪽). 검사기 b 는 `namespaces` 값이 루트 API `urls_namespace=` 글자 안인지도 본다. `NOT_API_MIDDLEWARE` 줄은 그 미들웨어가 API 경로를 빼는 코드 줄을 G1 근거로 단다(서버렌더 transient 미들웨어는 빼는 줄이 없으면 API 에도 답한다).

**적는 것의 경계**(검토 S9): 코드 · 설정 · 앞단 설정에 그 status 가 적힌 **의도된 답**만 적는다 — 미식별 500 · 앞단 502/504 는 결함이라 약속이 아니고 꼴도 정해지지 않는다. 없는 경로 404 · 다른 메서드 405 는 그 operation 의 답이 아니다.

### 3.2 API 모듈의 꼴 하나

```python
from ninja.openapi.schema import OpenAPISchema
from ninja_extra import NinjaExtraAPI  # 또는 ninja.NinjaAPI

from framework.ninja.pre_route_responses import add_pre_route_responses


class DocumentedAPI(NinjaExtraAPI):
    def get_openapi_schema(
        self, *, path_prefix: str | None = None, path_params: dict[str, object] | None = None
    ) -> OpenAPISchema:
        return add_pre_route_responses(self, super().get_openapi_schema(path_prefix=path_prefix, path_params=path_params))


api: DocumentedAPI = DocumentedAPI(...)
```

- 클래스 이름 · 기저(NinjaAPI · NinjaExtraAPI)는 프로젝트가 고르고, 메서드 서명 · 몸통은 글자 그대로다(Ninja 서명에 묶인다 — 서명 글자는 구현 때 이웃 검사기 · mypy strict 로 확정). 루트 API 를 알아보는 검사기 넷은 «같은 모듈 안 하위 클래스» 를 루트 생성으로 받는다(검토 확인). #437 닫힌 목록에 이 클래스 하나를 더한다.
- 이 꼴 말고의 문서 재정의 · monkeypatch · 후처리는 지금처럼 금지다.

### 3.3 붙이는 법

- 정본 함수는 `api` 의 경로 객체를 **(메서드, 생성 문서 경로)** 로 생성 문서 operation 에 잇는다 — Ninja `get_paths` 와 같은 식(`schema.path_prefix` + bound router prefix + 경로 · 변환기 지움). 여러 메서드 operation 은 Ninja 가 한 dict 를 함께 거므로 메서드마다 복사한 뒤 붙인다(검토 NB1). 경로마다 `auth`(인증 콜백 있음) · `csrf`(인증 콜백의 CSRF 확인 + 안전하지 않은 메서드) · `throttle` · `permission`(ninja_extra 경로 · 컨트롤러 권한 · AllowAny 밖) · 변환기 경로 변수(`{int:x}` 꼴 — Ninja 는 `{uuid:x}` 를 `{uuidstr:x}` 로 바꿔 둔다)를 읽는다. CSRF 는 경로의 `csrf_exempt` 면 뺀다 · 권한은 `AllowAny` 를 상속하고 `has_permission` 을 바꾸지 않은 클래스만 «누구나» 로 본다(MRO — 검토 NS2 · 셋째 확인 N5). ninja_extra 를 import 하지 않는다(쓰지 않는 프로젝트도 같은 정본).
- `input` = 몸통이 있거나, 틀릴 수 있는 parameter 가 있다 — 변환기 경로 변수는 변환기와 생성 schema 가 맞으면(`int` ↔ `integer` · `uuid` ↔ `string/uuid` · `str` · `slug` · `path` ↔ 제약 없는 글자) 틀릴 수 없다(404) · 값 제약이 붙거나 꼴이 어긋나면 틀릴 수 있다(검토 NI3) · 그 밖 경로 parameter 는 제약 없는 글자가 아니면 · 쿼리 · 머리 · 쿠키 parameter 는 필수이거나 제약 없는 글자(`string` · `anyOf[string, null]` · 글자의 `array`)가 아니면.
- `methods` · `namespaces` · `operations` 에 맞지 않거나 `exempt` 설정 목록에 든 경로는 뺀다. 같은 status 는 한 항목에 몸통 `anyOf` · 머리 합집합(경로 코드가 이미 적은 같은 이름 머리는 그대로 둔다 — 셋째 확인 S2) · 설명 이음. 변환기 ↔ schema 대조는 `title` · `description` · `default` · `examples` · `example` 칸을 뺀다(S3). component 이름이 겹치는데 꼴이 다르면 문서 생성이 실패한다(검토 S6).

### 3.4 BC 오류의 머리(경로 코드)

- `openapi_extra={"responses": {<정수 status>: {"headers": {…}}}}` — `<정수 status>` 는 그 경로 `response=` 에 선언된 status. 오류 status 에는 `headers` 만(설명 · 몸통 바꾸기 금지). **숫자 문자열 키 · 변수 키 · `**` 는 성공 · 오류 모두 위반**.
- 컨트롤러가 주입된 응답(`response: HttpResponse`)에 싣는 글자 머리 이름은 그 머리를 실은 뒤 반환하는 status 의 머리 보충에 있어야 한다(검토 S5). 12-slot slot 12 의 «오류 status 의 머리는 생성 OpenAPI 에 선언되지 않으므로 operation `description` 에도 적는다» 는 «머리 보충으로 선언한다» 로 바뀐다.

### 3.5 시험

- 표를 만들거나 행을 바꾸는 실행은 그 프로젝트에 붙는 행마다(기본 행 포함) 입장 표에 별도 승인 행을 둔다 — 그 답을 실제로 일으켜 표의 Schema 로 본문 꼴을 검증한다(값 고정 아님 · 시험용 엄격 검증). Ninja 판 올림으로 기본 몸통이 바뀌면 여기서 붉다(D27 «문서가 실제 동작과 어긋나지 않게» 를 기계로). **붙는 쪽 단언**: 그 operation 의 mounted 생성 문서에 그 status 가 있다(셋째 확인 N2 — 이것이 없으면 이름공간 오타로 행이 아무 데도 안 붙어도 시험이 초록이다). **좁힘 반대쪽**도 시험한다(검토 NI4) — `methods` · `namespaces` · `exempt` · `operations` 로 좁힌 프로젝트 행마다 빠진 쪽 operation 하나에서 그 미들웨어 조건을 일으켜 답하지 않음 · `NOT_API_MIDDLEWARE` 줄마다 API 경로에서 그 조건을 일으켜 답하지 않음. 시험은 대상 BC 시험 폴더에 둔다(그 BC 경로로 답을 일으킨다 — 리팩토링 창의 다른 BC 편집 목록 밖으로 나가지 않게 · 검토 NI1 덧). 대상 BC 경로로 일으킬 수 없는 행(다른 이름공간 · 그 BC 에 몸통 경로가 없음)은 이번 실행 시험에서 빼고 G2 배너에 «시험 자리 없음» 으로 적는다. 예외로 일어나는 미들웨어(서버렌더 transient 등)는 `RequestFactory` 로 미들웨어를 직접 불러 시험한다(셋째 확인 S4). 감수자 R-1042 «exact-format 테스트를 요구하지 않는다» · acceptance-tester R-3283 «status · 민감정보 비노출 smoke» 에 이 예외 한 구를 더한다(검토 I7).

## 4. 검사기

### 4.1 #63 check-openapi-error-declaration

| | 지금 | 바뀜 | 레인 · 자리 |
|---|---|---|---|
| a | `get_openapi_schema` 정의 전부 위반 | 3.2 꼴(루트 API 하위 클래스 · 메서드 하나 · 서명 · 몸통 글자)만 받음 | code · 새 루트 API 레인(모든 프로필) |
| b | — | 정본 파일이 받는 정본 지문(판마다 · 옛 판 지문 목록 — 검토 S8)과 다르면 위반 · 표 파일이 글자 값이 아니거나 칸 · 값이 틀리면 위반 | 새 framework 레인(모든 프로필) |
| c | — | 루트 API 를 짓는 모듈 가운데 하나라도 3.2 꼴이 아니거나 정본 · 표 파일이 없으면 **모든 operation 마다**(컨트롤러 operation 자리 · 안내 글에 operation 식별 `<클래스>.<메서드>`(모듈 함수 operation 은 `<Router 이름>.<함수>` — 구현 검토 S7 · 늘 정적 · 파일 안 유일) + 읽히면 `GET /books/{book_id}` — 검토 I3 · NS4) «경로 앞 오류가 문서에 없다» | tree(모든 프로필 — 리팩토링 R1 · registry_gate · pre-gate 가 auto) · BC 컨트롤러 자리라 R1 의 대상 BC 경로 필터를 지난다 |
| d | — | settings `MIDDLEWARE`(settings 모든 모듈의 합 — `+=` · `append` · `insert`)의 프로젝트 미들웨어(프로젝트 안 모듈 · `NOT_API_MIDDLEWARE` 밖)가 답을 내는데 표에 그 status 행이 없거나(같은 status 행이 좁힌 행 — `operations` · `methods` · `namespaces` · `exempt` · `when` 이 `all` 이 아닌 행(구현 둘째 확인 N3) — 뿐이면 · 모든 루트 API 의 이름공간을 글자로 읽고 그 모두를 덮는 `namespaces` 는 좁힘이 아니다(구현 3차 · 둘째 확인 M1 — 못 읽은 루트가 하나라도 있으면 좁힘) 위반 대신 ⓓ 후보 «이 미들웨어 답이 그 행이 좁힌 경로 · 메서드에만 나는가» — 구현 검토 I5: 좁힌 행을 아예 안 세면 특정 경로에만 답하는 미들웨어를 적을 길이 없고, 그냥 세면 다른 미들웨어의 빠짐을 덮는다), 싣는 글자 머리가 그 행 `headers` 에 없으면 그 미들웨어 자리에 위반(표가 있을 때만). 읽는 자리 = 클래스 `__call__` · `process_request` · `process_view` · `process_exception` · `process_response` · `process_template_response` · 함수 공장 미들웨어의 안쪽 함수. 읽는 답 = `HttpResponse` · `JsonResponse` · `render` · `TemplateResponse` 의 `status=` · `HttpResponse*` 고정 status 클래스 · `HTTPStatus.X` · 모듈 정수 상수 · `response.status_code = N` · `raise PermissionDenied`(403) · `BadRequest` · `SuspiciousOperation` 계열(400) · `Http404`(404 — 미들웨어가 일부러 내면 의도된 답 · 셋째 확인 S5). 읽지 못한 답은 ⓓ 후보 줄(리뷰어 몫 — 검토 I6 · S5 · NI5) | 새 framework 레인 |
| e | 오류 status `openapi_extra` 전부 위반 · 성공 보충은 숫자 문자열 키도 받음 | 3.4 머리 보충 받음 · 숫자 문자열 키는 모두 위반 | code · tree · repo scan |
| f | — | 주입 응답(주석 `HttpResponse` 로 찾음 — 이름 무관)에 싣는 글자 머리 이름이 그 branch 마지막 `Status` 의 status 머리 보충에 없으면 위반 — check-api-error-controller-contract 의 판독(`_response_parameters` · branch 꼴)을 그대로 쓴다 · 그 밖 꼴(`.headers[...]` · raw 응답 `headers=`)은 ⓓ 후보(검토 §9 f 권고) | code · tree |
| g | BC 오류 Schema 만 `extra-bc-advertisement`(`401: dict` · `401: AuthenticationError` 는 통과) | `response=` 의 4xx · 5xx 에 직접 반환하지 않는 Schema 는 무엇이든 위반(경로 앞 오류는 표로) | code 만(직접 반환 판정이 code 레인 흐름 분석 — R1 은 이 줄을 받지 않고 R2 api 렌즈가 읽는다 · 검토 S4) |

- 지금 tree · repo scan 레인은 경로에 `driving_layer` 가 든 파일만 본다(:592) — 루트 API 레인은 `NinjaAPI` · `NinjaExtraAPI`(또는 같은 모듈 하위 클래스) 생성 모듈을 찾는다. 안내 문면 · 낡은 근거 줄(:3423 «§2.2 line111»)을 고친다.

### 4.2 이웃 검사기

- #437 check-composition-root `_check_project_api`(:2886) — 3.2 클래스 하나를 닫힌 목록에 더함.
- #415 · #493 · #645 · #647 — 정본 · 3.2 글이 스스로 지킨다(검사기 무변). 정본 파일 둘 + 3.2 `api.py` 장난감이 27종 positional 에서 #63 · #437 밖 0 인 픽스처를 저장소 시험으로 둔다(검토 B1).
- #434 그대로. pregate_symbol_kinds · rulepack 재소성 · 봉인.

### 4.3 저장소 시험

- 정본 동작 시험(검토 S8): `.venv-probe` 에 django-ninja · ninja_extra · pydantic 을 고정 판으로 더하고, 장난감 프로젝트(v2 시제품 꼴)에서 «생성 문서 ↔ 실제 응답» 을 경로마다 대조하는 스모크를 verify-base-probe 에 둔다 — 참조 글 = 정본 글자 대조만으로는 Ninja 판이 바뀌어 판정이 틀려도 모른다.
- 시험 파급(검토 S10): c 가 3.2 꼴이 없는 기존 #63 · 교차 픽스처 모두에 줄을 세운다 — api_error_backstop_matrix · checker_cross_matrix · findings_count_matrix(«#63×6») · checker_baseline_matrix · field_report_checker_smoke · anchor_diff_smoke · construct_drift_report 기대를 함께 고친다.

## 5. 글(그래프 → 렌더 · Codex 미러 · rulepack)

자리 전수는 `workspace/scratch/f4-173-openapi-errors/inventory.md`(규칙 글 84 · 검사기 37 · 시험 43 · 미러 16) + 검토 S3. 바뀌는 성격별:

- **원칙 문장(새 규범 하나)**: architecture-api §5.2 · §14.3 — «API 문서는 그 경로에서 날 수 있는 의도된 오류를 누가 보내든 모두 적는다 — 경로 코드가 보내는 BC 오류는 `response=` 로, 경로 앞에서 framework · 미들웨어 · 앞단이 보내는 답은 경로 앞 응답으로, 오류의 머리는 머리 보충으로». architecture-api SKILL :27 · :31 은 이 문장과 맞는지 본다.
- **금지 문장 고침**: ninja final §2.2(:125-134 · R-0682 · R-0683) · §6.2 BC 오류 머리(:773-787 · R-0068 · R-0069 — f 의 집) · framework 오류 경계(:829-834 · R-0078) · 응답 선언과 OpenAPI(:860-874 · R-0088 · R-0089) · 406/415(:900-902 · R-0790) · OpenAPI 후보(:946-955 · :952) · SKILL :30(R-2930 · R-2932) · architect :61 · :63(R-1626 · R-1632) · api 리뷰어 :76 · :78 · :80(R-3658 · R-2686 · R-2690 · R-2691) · 감수자 :100 · :102(h) · :106(R-1011 · R-1012 · R-1022 · R-1042) · acceptance-tester :44(R-3283) · 조정자 :183 · :191 · :202(R-0331 · R-0339 · R-0350) · houserules SKILL :35(R-3135) · implementation-test :2463-2467 · :2492-2494(R-1885 ~ R-1888 · R-1898). 뜻: «framework status 를 BC `response=` 에 광고하지 않는다 · BC 오류로 바꾸지 않는다» 는 남기고 «문서에는 경로 앞 응답으로 적는다» 를 더한다. 후처리 금지는 «3.2 꼴 하나 말고» 로. «성공 100–399 리터럴 보충만» 문장 넷(R-0089 · R-0683 · R-2932 · R-0339)은 «머리 보충 — 정수 키 · 오류 status 는 headers 만» 으로.
- **몸통 주장 문장**: ninja :535-538(R-0008) · api :252(R-1999) · SKILL :30(R-2931) — «framework 기본 몸통을 BC code 계약이라 주장하지 않는다» 는 남기고 «경로 앞 응답에 관찰된 꼴로 적고 3.5 시험이 지킨다» 를 더한다.
- **합성 금지 문장**: api :257 · :346 · :407 · :550(R-2000 · R-2013 ~ R-2016 · R-2030 ~ R-2033 · R-2070) · ninja :907-908(R-0795) — 실제 응답에 status · 머리를 합성하는 금지는 그대로. «문서에 적는 것은 합성이 아니다 · 문서에 적었다고 미들웨어 합성이 허용되는 것도 아니다» 한 구.
- **참조 코드**: ninja final §6.2 에 3.1 정본 코드 · 표 예(프로젝트 행 예) · 3.2 꼴 · §2.3 `api.py` 예 코드(:246-261)를 3.2 꼴로.
- **12-slot**: slot 1(contract scope)에 경로 앞 응답 파일 둘 · 3.2 클래스의 경로와 action(`reuse | create | change`) · slot 12 에 이 scope 경로에 붙는 경로 앞 행 · 머리 보충 · 3.5 시험 행.
- **역할**: architect(프로젝트 행의 근거 — 미들웨어 코드 · 설정 · 앞단 설정 · `NOT_API_MIDDLEWARE` 근거) · api 리뷰어(행 ↔ 근거 대조 · 빠진 미들웨어 · `operations` 행) · 감수자(정본 그대로 · 3.5 행) · coder(정본을 글자 그대로) · acceptance-tester(3.5 행).
- **리팩토링 글**: 조정자 «다른 BC 편집» 갈래 «프로젝트 합성» 정의(파일 셋 이름) · V 판형 :318(`근거 M<k> | C<k>`) · 해소 판정 :314 · design-architect 의 V · 병합 글.
- **서버렌더 transient 미들웨어**: implementation-django-web final :319 · :382-389 와 architect 글에 «API 경로를 빼는 줄이 없으면 API 에도 답한다 — `NOT_API_MIDDLEWARE` 근거는 그 빼는 코드 줄» 한 구.
- **결정 기록 · 대장**: D27 «OpenAPI 도 같다» · D25 T41(`framework/ninja/openapi_rule.py` 를 뺀 까닭) · 트리 개정 명세 대장 #63 · #434 · #437 행에 «2026-11-13 개정(F4-173 · 사용자 결정)» 을 덧붙인다(기록은 지우지 않는다).
- **문서**: README :145 · :277-282 · :306-308 · `docs/file_tree.html`(:3204 api.py 행 · framework/ninja 행 둘) · 요청 가이드(7).
- **이미 낡은 곳(함께)**: Codex 감수자 SKILL :93(08-25 전 문장) · README :281.

## 6. 리팩토링 절차

- R1 빚 = 27종 검사기 위반(auto · 대상 BC 경로 필터). 4.1 c(경로마다 · operation 식별) · e · f 가 BC 컨트롤러 자리에 서므로 리팩토링 실행은 이 빚을 저절로 받는다 — 사용자 «리팩토링 절차에도». g 는 code 레인뿐이라 R2 api 렌즈(ninja §6.2 · §8 · api §5 · §14 — 이미 렌즈 점검 절)가 읽는다.
- 갚는 길(검토 I4 · NI1 · 셋째 확인 N3): 다른 BC 편집 갈래 «프로젝트 합성» 의 정의 글에 `<project>/api.py` · `framework/ninja/pre_route_responses.py` · `framework/ninja/pre_route_response_table.py` 를 이름으로 넣는다(0C · 0F · 변경 창이 받고 deps 대조 밖 — 검토 확인). 문서가 바뀌는 것은 새 종류를 만들지 않고 V 종류 `밖 동작`(문서 = 공개 계약)으로 적어 3.5 `add` 행을 싣는다 — **V 머리 근거가 `C<k>`(검사기 빚 · 여럿 — c 는 operation 마다 C 를 하나씩 낸다)도 받게** 고친다 — `refactor_audit.py` `_HEAD_V` · `_gate_changes_reds`(:3673-3676 · :3684-3687 — 이것을 안 고치면 `changes --gate` 가 붉어 `G1 변경판 확정` 이 서지 않는다) · VEntry 근거 판형 · «안 바꾼다» 때의 C 처분(`ⓐ 재상정`) · 조정자 :314 · :318 판형 · design-architect :28 · :29(G2 잔존 대조 `M_c` 는 무변 — 셋째 확인 확인). 뿌리는 «동작 변경이 따르는 검사기 빚을 V 로 싣는 길» 이 없던 것. R-3527 의 G0 «문서 층 변경(OpenAPI)» 1행도 함께 선다. 한 번 두면 모든 BC 의 c 가 함께 사라진다.
- 설치하는 실행에서 다른 BC 의 문서 시험(«framework status 가 BC 로 광고되지 않는지» 류)이 붉으면 V 의 영향 «공유 표면» 으로 적고 그 시험 고침을 다른 BC 편집 «받는 쪽 시험» 으로 싣는다(검토 NS6).

## 7. 영향

- 기존 프로젝트: c 가 경로마다 앵커 기존분 빚으로 선다(새 실행을 막지 않음 · R1 · G0 에 경로 수만큼 — 같은 고침 하나로 함께 사라지는 줄). 새 operation(이름이 바뀐 operation 포함)을 만드는 실행은 c 가 새 줄이라 막힌다 → 그 실행이 파일 둘과 클래스를 둔다(한 번).
- 숫자 문자열 키 성공 보충이 새 빚이 된다(문서를 망가뜨리는 꼴 — 맞다).
- 진행 레인: pre-gate 재예보(툴체인 stale). 레인 api-contract-common 은 «가»(api.py 문서 재정의 + 경로 `openapi_extra`)를 사용자 승인 빚으로 간다 — 새 판 뒤 그 꼴은 정본 꼴로 옮기는 빚이 된다.
- dddjango-web: 바꾸지 않는다(문서 소비자 — 계약 위험이 준다).
- 요청 가이드: 사용자가 요청에 쓰는 칸은 그대로 — 결과 예 한 줄 후보(«API 문서에 로그인 · 입력 오류 · 점검 응답까지 경로마다 적혀 있다»).

## 8. 한계

- 기계로 못 가르는 것은 «날 수 있다» 쪽으로 기운다(모두 재현): 선택 인증(인증 콜백 가운데 하나가 늘 통과)의 401 · 파일만 받는 multipart 의 Django 상한 400 · `IsAuthenticatedOrReadOnly` 의 GET 403 · `IsAuthenticated | AllowAny` 의 403 · 필수 인증 경로의 익명 throttle 429 · ninja_extra `@throttle`(기본 비율 없음)의 429(검토 NS2).
- 경로 객체로 못 가르는 답(승인 endpoint 의 406 · 415 · 인증 안 `HttpError`)은 프로젝트 행 `operations` 로만 적는다 — 빠짐은 리뷰어 몫.
- d 는 4.1 d 의 꼴만 읽는다 — 읽지 못한 답은 ⓓ 후보 줄로 리뷰어에게 넘기고, 서드파티 미들웨어는 리뷰어 몫이다.
- `exempt` 는 경로 글자 대조라 미들웨어가 접두 · 이름 · 데코레이터로 빼면 표가 그 뜻을 못 적는다 — 미들웨어가 그 설정을 같은 뜻으로 쓰는지는 리뷰어가 대조한다(검토 S11 — 미들웨어 판정 함수를 가리키는 꼴은 미들웨어 고침을 요구해 이번에 들이지 않는다).
- 앞단(nginx 등) 행은 저장소 밖 설정이 근거라 기계가 대조하지 않는다.
- 정본은 Ninja 내부(경로 객체 · `_get_bound_routers` · `OpenAPISchema.path_prefix`)에 기댄다 — Ninja 판 올림은 4.3 동작 시험과 3.5 시험이 잡는다. 받는 Ninja 판은 1.6 이상이다(옛 판은 `_get_bound_routers` 가 없을 수 있다 — 셋째 확인 S6 · 재현 못 함) — 낮은 판이면 설계가 G1 에서 판 올림을 먼저 적는다.

## 9. 열린 것

- (닫힘) 3.2 서명 `path_params: dict[str, object] | None` 은 #493 · #645 · #647(check-public-surface-annotation)과 mypy strict 를 함께 지난다(`workspace/scratch/f4-173-openapi-errors/sig/` · `proto2/mypy.ini`). 정본 파일 자체도 mypy strict 0 이어야 한다 — TypedDict 몸에 `__pydantic_config__` 를 두면 mypy 가 필수 키로 읽어 깨지므로(셋째 확인 N4) 모르는 칸은 `__required_keys__ | __optional_keys__` 로 막는다. 4.2 의 27종 0 픽스처 시험에 mypy strict 를 더한다.
- (닫힘) d · f 판독 범위 — 둘째 확인 권고대로(4.1 d · f).

## 10. v1 독립 검토 처분(`workspace/scratch/f4-173-openapi-errors/review-1.md` · 차단 2 · 중요 7 · 사소 11 · 물음 2)

운영자가 장난감으로 B2 · I1 · I2 를 다시 돌려 재현을 확인했다(`review-1/proto/run_review.py` · `run_opjoin.py`).

| # | 처분 |
|---|---|
| B1 이웃 검사기 넷 | 받음 — 정본이 #415 · #493 · #645 · #647 을 스스로 지킴 · 3.2 서명 글자 고정 · 기본 행을 정본으로 · 27종 0 픽스처(3.1 · 3.2 · 4.2) |
| B2 경로마다 다른 framework 답 | 받음 — 경로 객체를 operationId 로 이어 auth · csrf · throttle · permission 판정 · 프로젝트 행 `operations`(3.3 · v2 시제품 맞음) |
| I1 나지 않는 답 약속 | 받음 — 변환기 · `anyOf[string, null]` · 글자 배열 · JSON 몸통만 400 JSON(3.3) · 선택 인증은 한계(8) |
| I2 Django 상한 400 | 받음 — 기본 행(3.1) |
| I3 `:N` 정규화 | 받음 — 안내 글에 operation 식별(4.1 c) |
| I4 리팩토링 길 | 받음 — «프로젝트 합성» 에 이름 · V `밖 동작`(6) |
| I5 빈 표 | 받음 — 기본 행은 정본(3.1) |
| I6 API 에 답하지 않는 미들웨어 | 받음 — `NOT_API_MIDDLEWARE` · 고정 status 클래스 · `HTTPStatus`(3.1 · 4.1 d) |
| I7 3.5 ↔ R-1042 · R-3283 | 받음 — 예외 한 구(3.5 · 5) |
| S1 숫자 문자열 키 | 확인 · 정렬 내보내기 죽음 근거 더함(2) |
| S2 AST 대조 | 받음(3.1) |
| S3 글 목록 빠짐 | 받음(5) |
| S4 g 레인 | 받음 — g 는 code 만 · R2 렌즈(4.1 · 6) |
| S5 f · d 머리 | 받음(3.4 · 4.1 d) |
| S6 component 충돌 | 받음(3.3) |
| S7 exempt 설정 자리 | 받음(3.1) |
| S8 정본 판 올림 · 동작 시험 | 받음 — 받는 지문 목록 · `.venv-probe` 동작 스모크(4.1 b · 4.3) |
| S9 적는 것의 경계 | 받음 — «의도된 답» 문장(3.1) · 사용자 보고에 설계 처리 한 줄 |
| S10 시험 파급 | 받음 — 목록(4.3) |
| S11 exempt 과적합 | 일부 — 꼴은 그대로(미들웨어 고침 요구를 피함) · 한계에 적음(8) |
| Q1 여러 루트 API | 받음 — 모두 3.2 클래스 · 자리는 F4-150(3.1) |
| Q2 결정 문구 | 받음 — 설계 처리 한 줄(0) |

## 11. v2 둘째 확인 처분(`workspace/scratch/f4-173-openapi-errors/review-2.md` · 차단 1 · 중요 5 · 사소 6)

운영자가 NB1 을 장난감으로 다시 돌려 확인했다(operationId `pub_list_3f686f89` → 다음 실행 `pub_list_4772fc02` · 같은 Router 두 번에서 401 빠짐 · 여러 메서드에서 GET 에 CSRF 403). v3 정본(`make_v3.py` → `proto3/` · `join3/`)으로 다시 돌려 NB1 · NI2 · NI3 · NI4(빈 튜플 · 꼴 · 오타) · NS2(AllowAny 상속 · csrf_exempt) · NS3 가 문서 = 실제임을 확인했다.

| # | 처분 |
|---|---|
| v1 B1 시제품 안 닫힘 | 받음 — 정본은 `review-2/annot/` 주석 꼴(27종 #437 밖 0 · mypy strict 0)에서 짓는다(NS1) |
| NB1 operationId 잇기 | 받음 — (메서드, 문서 경로) 열쇠 · `operations` 같은 꼴 · 못 잇거나 겹치면 실패 · 메서드마다 복사(3.1 · 3.3) |
| NI1 V 머리 C 빚 | 받음 — V 근거에 `C<k>` (6) · 고칠 도구에 refactor_audit `_HEAD_V` · 해소 판정 · G2 잔존 대조 |
| NI2 429 머리 | 받음 — 기본 행 선택 머리 `Retry-After`(3.1) |
| NI3 변환기 판정 | 받음 — 변환기 ↔ schema 맞을 때만(3.3) |
| NI4 좁히는 칸 | 받음 — 표 검증 · 좁힘 반대쪽 시험 · transient 미들웨어 근거 줄(3.1 · 3.5 · 4.1 d · 5). «d 가 `operations` 행을 세지 않음» 은 구현 때 걷음(특정 경로에만 답하는 미들웨어를 적을 길이 없어짐 — 좁힘은 3.5 시험이 지킨다) |
| NI5 d 판독 범위 | 받음 — 권고 범위 · ⓓ 후보(4.1 d · 8) |
| NS1 주석 꼴 정본 | 받음(위) · AST 대조는 `type` 문도 정의로 센다 |
| NS2 과잉 약속 | 받음 — AllowAny 상속 · csrf_exempt 는 고침(3.3) · 나머지 한계(8) |
| NS3 쿼리 칸 수 상한 | 받음 — 기본 행(3.1) |
| NS4 c 식별 글 | 받음 — qualname + 읽히면 `METHOD 경로` · 루트 API 하나라도 꼴이 아니면 모든 operation(4.1 c) |
| NS5 3.2 예 #493 | 받음 — `api: DocumentedAPI = …`(3.2) · ninja §2.3 예도(5) |
| NS6 다른 BC 문서 시험 | 받음(6) |

## 12. v3 셋째 확인 처분(`workspace/scratch/f4-173-openapi-errors/review-3.md` · 차단 0 · 중요 6 · 사소 6 · 물음 없음)

| # | 처분 |
|---|---|
| N1 잇기 · 대상 대조 실패로 운영 문서 500 | 받음 — 겹친 열쇠는 뒤의 것이 이김(Ninja 문서와 같음) · `operations` 행은 `namespaces` 하나 필수 · 그 이름공간 문서에서만 대조(3.1) |
| N2 좁히는 칸 값 오류 · 3.5 단언 빠짐 | 받음 — `status` · `methods` 값 검증 · 검사기 b 가 `namespaces` 를 루트 API 이름공간과 대조 · 3.5 «붙는 쪽 단언» · `operations` 와 c 식별 글 관계 고침(3.1 · 3.5) |
| N3 V 머리 C 만으로는 안 섬 | 받음 — `_gate_changes_reds` · VEntry · C 처분 · C 여럿 · architect 글(6) |
| N4 정본 mypy strict | 받음 — 모르는 칸은 키 집합으로 막음 · 픽스처에 mypy strict(9) |
| N5 AllowAny 상속 덜 적음 | 받음 — `has_permission` 을 바꾸지 않은 것만(3.3) |
| N6 Django 상한 400 의 꼴 | 받음 — 표 파일 `BAD_REQUEST_RESPONSE` · `handler400` 대조(3.1) |
| S1 import 때 실패 | 받음 — 문서 만들 때로 · 정적 몫은 b(3.1) |
| S2 429 머리 덮어씀 | 받음(3.3) |
| S3 `examples` 칸 | 받음(3.3) |
| S4 3.5 자리 · RequestFactory | 받음(3.5) |
| S5 `Http404` | 받음(4.1 d) |
| S6 옛 Ninja | 받음 — 받는 판 1.6 이상 · 한계(8) |

## 13. 구현 독립 검토 처분(`workspace/scratch/f4-173-openapi-errors/impl-review-code.md` 차단 0 · 중요 5 · 사소 9 · `impl-review-text.md` 차단 0 · 중요 2 · 사소 6)

운영자가 코드 I5 · I1 · S8 을 장난감(`impl-review-code/t5_d.py` d3 · d1 · d1b · d2 · d4 · d4b — 모두 exit 0)으로 다시 돌려 확인했다.

| # | 처분 |
|---|---|
| 코드 I1 d 가 hook 밖 답을 놓침 | 받음 — self 메서드 · 같은 모듈 함수 · 프로젝트 기저 hook 한 단계 · 못 따라가면 ⓓ |
| 코드 I2 import 한 정해진 클래스 | 받음 — 다른 모듈에서 정해진 꼴로 확인된 클래스로 지으면 받음 |
| 코드 I3 HTML handler400 | 받음 — 기본값이면 ⓓ 후보 |
| 코드 I4 f 바깥 블록 머리 | 받음 — 둘레 블록 머리를 안쪽 오류 return 에 물림(현장 f 줄이 는다 — 오류 응답의 `Cache-Control` 등 · 의도한 빚) |
| 코드 I5 좁힌 행이 다른 미들웨어 빠짐을 덮음 | 받음 — 좁힌 행뿐이면 ⓓ 후보(4.1 d) |
| 코드 S1 ~ S4 · S7 ~ S9 | 받음 |
| 코드 S5 스모크 exempt 메서드 | 받음 — 다른 메서드 operation |
| 코드 S6 정본의 Python · pydantic 판 | 받음 — 글에 Python 3.12 · pydantic 2.5 이상(8 · 글) |
| 글 I1 서드파티 미들웨어 | 받음 — 행 대상은 미들웨어(서드파티 포함) · 리뷰어 blocker 목록 · 검사기 d 는 프로젝트 미들웨어만(한계 그대로) |
| 글 I2 framework-owned 목록 꼬리 구 | 받음 — «그 가운데 경로 앞에서 나는 의도된 답만» |
| 글 S1 ~ S4 · S6 | 받음(S4 = api.py 프레임워크 오류 핸들러가 기본 몸통을 바꾸면 G1 STOP · S6 = 요청 가이드 예를 §4 «적지 않아도 되는 것» 으로) |
| 글 S5 결정 기록 | 결정 기록은 고치지 않고 판 기록 «바뀐 옛 판단» 에 적는다(2.36.0 선례) |

## 14. 구현 둘째 확인 처분(`workspace/scratch/f4-173-openapi-errors/impl-review2-code.md` 차단 0 · 중요 3 · 사소 8 · `impl-review2-text.md` 차단 0 · 중요 0 · 사소 5)

운영자가 코드 N1 · N2 · N3 을 장난감(`impl-review2-code/n_toys.py` n5g exit 2 · n12a ~ n12d exit 0 · n3 · n3b · n3c exit 0 · 후보 0)으로, 글 S-1(G0 ② e 인용 ↔ 검사기 :694 · :2788 · :3687) · S-3(G2 감사 동봉이 #4 · #11 ⓓ 뿐 — 조정자 :167)을 글로 다시 확인했다. 첫 검토 지적 가운데 코드 I1 · I5 는 일부만 닫혔고 I4 고침이 오탐 하나(N1)를 열었다 — 나머지는 닫힘.

| # | 처분 |
|---|---|
| 코드 N1 try 몸통 «실행 뒤» 머리를 except 오류에 물림(오탐) | 받음 — 머리 뒤에 `return` 말고 다른 몸통 문장이 있을 때만 except · finally 로 물림 · `else` 는 그대로 |
| 코드 N2 d 가 `return <호출>` 꼴만 따름 | 받음 — hook 몸통 어디서든 부른 같은 클래스 메서드 · 같은 모듈 함수를 한 단계 |
| 코드 N3 `when` 좁힘 | 받음 — `when` ≠ `all` 도 좁힌 행(4.1 d) |
| 코드 M1 못 읽은 이름공간 | 받음(4.1 d) |
| 코드 M2 다른 모듈 정해진 클래스의 하위 클래스 루트 | 받음 — 알아봄 · `get_openapi_schema` 재정의 없으면 정해진 꼴 |
| 코드 M3 · M5 · M6 | 받음 |
| 코드 M4 `openapi_extra` 글자 꼴 | 받음 — 글에 통과 꼴 · 막는 꼴 문장 · f 가 같은 모듈 맨 위 글자 `headers` 상수를 품 |
| 코드 M7 자기 행 ⓓ 소음 | 받지 않음 — 설계가 받은 비용(exit 불산입) |
| 코드 M8 설계 기록 | 받음 — 4.1 c · d 와 이 절 |
| 글 S-1 G0 ② e 인용 | 받음 — 실제 줄 «responses 보충 —» 로 |
| 글 S-2 경로 코드의 `HttpError` | 받음 — `operations` 행으로 적는다는 구 |
| 글 S-3 G2 ⓓ 받는 이 | 받음 — 규율 감사 동봉에 #63 ⓓ 신규 · 감수자 한 줄 |
| 글 S-4 요청 가이드 앞단 | 받음 — 저장소 밖 앞단 답은 2번 «문서에 없는 바깥 서버의 동작» 에 |
| 글 S-5 낡은 «프로젝트 미들웨어» | 받음 — 트리 명세 기록 · 검사기 주석 |
| 사용자 물음(운영자 — 계획 멈출 기준) | f 의 캐시 지시 머리(`Cache-Control` · `Pragma` · `Expires`) — 현장 api f 211 가운데 183 → **사용자 «나»(2026-11-13 17시 49분)**: 세 머리는 f · d 머리 대조에서 뺀다(적는 것은 막지 않음 · 클라이언트가 읽고 행동하는 머리만 막음) · 현장 api f 211 → 28 |

## 15. 구현 셋째 확인 처분(`workspace/scratch/f4-173-openapi-errors/impl-review3-code.md` 차단 0 · 중요 4 · 사소 5 · `impl-review3-text.md` 차단 0 · 중요 0 · 사소 2)

운영자가 코드 R1 ~ R4 를 장난감(`impl-review3-code/op-repro/r3_f_toys.txt` a2 · a2b · a4 exit 0 · e3 ~ e6 exit 2 · `r3_d_toys.txt` c1 exit 0 / c1r exit 2 · b3 · b5 exit 0)으로 다시 돌려 확인했다. 넷 모두 현장 0 이고 차단은 없다. 고침마다 둘레 꼴이 새로 나와, 이번 차례는 «기계가 분명히 가르는 꼴만 위반 · 통과 · 그 밖 흐름은 ⓓ» 를 f · d 흐름에도 건다(설계 «못 읽은 것은 ⓓ» 그대로). 이 고침 뒤에는 2.36.0 선례대로 검토자 넷째 확인 대신 운영자가 셋째 확인 장난감 · matrix 로 직접 확인한다.

| # | 처분 |
|---|---|
| 코드 R1 N1 고침이 연 놓침(return 값 식 안 호출 · 반복) | 받음 — return 값 식에 `Status` · Schema 생성 밖 호출이 있으면 물림 · try 안 반복 머리는 물림 |
| 코드 R2 M3 고침이 연 오탐(늘 끝나는 복합문) | 받음 — «늘 끝나는 블록» 판정 · 판정 어려운 꼴은 ⓓ |
| 코드 R3 N3 고침이 연 놓침(좁힌 행뿐이면 머리 대조 건너뜀) | 받음 — 머리 대조는 좁힘과 무관 |
| 코드 R4 N2 남음(못 따른 호출을 이름에 받아 돌려줌) | 받음 — ⓓ |
| 코드 S1 ~ S5 | 받음(S5 = settings 진입 모듈마다 `*` import 닫힘 안에 이름) |
| 글 T-1 조정자 · 감수자 ⓓ 목록이 좁음 | 받음 — «#63 ⓓ 후보 전부(예: …)» |
| 글 T-2 설계 §14 S-4 번호 | 받음 — 2번(운영자 고침) |
| 구현 5차 S3 (지시 «물림» → ⓓ) | 받음 — 블록을 나간 머리는 흐름 따라 실리므로 원칙대로 ⓓ(운영자 직접 확인 a6) |
| 남은 한계 | 같은 반복 몸통에서 머리보다 앞에 놓인 오류 return(다음 차례에 실림)은 보지 않는다 — 현장 0 · 리뷰어 몫 |
