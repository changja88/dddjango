---
name: dddjango-web-implementation-htmx
description: htmx 2.0.10 표기법 — 요청마다 만드는 VM·State·조각 응답, 세션·프로세스 수명 표기(SharedState·Service), hx-* 속성 규율, 첫 렌더·hx-indicator·오류 조각, 액션 응답·HX-Trigger 재조회, 재시도 없음, 금지 표면(hx-on·js:·조건식·확장)과 백스톱 PU 연동. VM·SharedState·Service·root의 요청 구동 코드와 hx-* 속성을 쓸 때 로드한다.
user-invocable: false
---

# htmx 표기법

## 언제 쓰나

VM·SharedState·Service·root_vm·handler의 요청 구동 코드, view 함수·조각 응답 함수, 템플릿의 hx-* 속성 선택, 로딩·오류 표시, 재조회·갱신 이벤트 표기가 필요할 때 로드한다. 전문을 읽지 말고 아래 라우팅 표로 필요한 절만 부분 적재한다. 경계:

- 수명 **결정**(어느 변종이 세션·프로세스 수명인가)·State 계약·에러 2채널 → `dddjango-web-architecture-state`
- 상태 동작 허용 위치 닫힌 열거 → `dddjango-web-discipline-houserules`
- urls·navigator·템플릿·CSRF 표기 → `dddjango-web-implementation-django`, frozen dataclass·언어 → `dddjango-web-implementation-python`
- 브라우저 UI 동작(JS) → `dddjango-web-implementation-javascript`

**수명 경계**: 세션 보관·시그널 연결 *표기법*은 이 스킬 소유, 수명 *결정*(SharedState=세션·Service·root handler=프로세스, VM=요청)은 dddjango-web-architecture-state §9 소유.

## 핵심 운영 원칙

- htmx는 2.0.10 한 파일 — 새 설치는 `web/static/htmx/htmx.min.js`, 기존 설치는 그대로 소비 · root_view는 build-state `htmx_core_static` 경로를 한 번 `defer` 로드 · 판 올림·이중 설치 금지 (§1)
- 요청 구동은 둘뿐 — 페이지 view가 `<화면>VM().build(…)`로 첫 렌더, `<화면>_<조각>_fragment`가 같은 VM으로 section 조각 응답(임베드 첫 렌더 `<화면>_embed_fragment` 포함) (§2)
- VM은 `build(...) -> <화면>State` — 조회 실패는 `BadRequestResponse` raise(에러 채널 ①), **view(페이지·조각 함수)가 잡아 같은 section을 맥락 `load_error`·`retry_href`로 그린다**(section 루트 id 유지·`error_feedback.html`은 그 안에서 include) · 요청 입력은 메서드 인자로 (§2·§5)
- `hx-trigger="load"`는 다른 view를 임베드하는 자리 하나만 — 부모는 자식 VM을 부르지 않고 navigator `<화면>_embed_href()`의 주소를 둔다 (§4·§7)
- 조각 요청의 redirect(로그인 302 포함)는 `RootRequestHandler`가 200 + `HX-Redirect`로 바꿔 전체 이동 — 조각 view는 `redirect(href)`만 (§6)
- 세션 수명은 view가 넘긴 `request.session`을 SharedState가 `MutableMapping[str, object]`로 받아 `<bc>.<관심사>` 키만 다룬다(reset은 자기 키만) · 프로세스 수명은 root_initializer의 시그널 연결 — application_layer는 django·`request`를 모른다 (§3)
- hx-* 는 일곱만(`hx-get`·`hx-post`·`hx-target`·`hx-swap`·`hx-trigger`·`hx-headers`·`hx-indicator`) — 조회는 GET·상태 변경은 POST+CSRF, URL은 State의 href (§4)
- **오류 조각은 200으로** — htmx 2는 4xx·5xx 응답을 교체하지 않는다, 액션 단추는 데이터 조각 안에만 (§5)
- 액션 성공 후 재조회는 액션 응답이 다시 build한 section — 다른 조각 갱신은 응답 `HX-Trigger: <bc>-<관심사>` + `hx-trigger="… from:body"` (§6)
- **자동 재시도 없음**: htmx는 실패 요청을 다시 보내지 않는다 — 재시도는 사용자의 «다시 시도» `hx-get` (§8)
- `hx-on*`·`js:`·`hx-trigger [조건식]`·인라인 실행·`hx-ext`·`hx-boost`·`transition:true`·`hx-delete/put/patch` 금지 (§9)
- `request`를 view 밖으로 반출하지 않는다 — VM·SharedState·UseCase에 `HttpRequest`를 넘기지 않는다 (§7)

## 상세 레퍼런스

| 질문 | 위치 |
|---|---|
| 버전·고정 판·2.x 기본값 | [`references/final.md`](references/final.md) §1 |
| 요청 구동 형태·VM 시그니처·이름 | final.md §2 |
| 세션·프로세스 수명을 어떻게 쓰나 | final.md §3 |
| hx-* 어디서 무엇을·URL 출처 | final.md §4 |
| 첫 렌더·로딩·오류 조각 | final.md §5 |
| 재조회·갱신 이벤트 표기 | final.md §6 |
| View 측 — view 함수·조각 템플릿 | final.md §7 |
| 재시도를 어떻게 다루나 | final.md §8 |
| 쓰면 안 되는 htmx 표면 | final.md §9 |
| 백스톱으로 규약을 기계 집행 | final.md §10 |

각 절은 필요한 절만 읽는다(`## §N.` 헤더로 grep 가능 — 전체 로드 불필요).
