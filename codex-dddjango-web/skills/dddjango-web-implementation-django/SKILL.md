---
name: dddjango-web-implementation-django
description: Django 스택 표기법 — urls(path·<Bc>Routes·navigator reverse·문서 셸 탭·게이트 redirect), 탭 재탭 2단 동작(링크 이동), in-process api_client·safe_api_call 실패 종류·DataSource, 템플릿·요청 수명·CSRF, 정적 이미지·레이아웃 형상 재현, CSS(foundation 변수·theme·부품 CSS)·외부 JS 고정 사본. 라우팅·DataSource·템플릿·CSS·정적 자산 코드를 쓸 때 로드한다.
user-invocable: false
---

# Django 표기법

## 언제 쓰나

URL·내비게이션·문서 셸(탭) 코드를 쓸 때, DataSource·api_client를 쓸 때, 템플릿·CSRF·요청 수명을 다룰 때, 정적 이미지·CSS·웹폰트·외부 JS 사본을 배선할 때 로드한다. 전문을 읽지 말고 아래 라우팅 표로 필요한 절만 부분 적재한다. 경계:

- 라우팅 짝의 역할·리터럴 단일 출처 규율 → `dddjango-web-architecture-ui`
- root 동작 규율·refresh 처방 → `dddjango-web-architecture-state`
- safe_api_call·Either 계약 → `dddjango-web-architecture-data`
- VM·조각 응답·hx-* → `dddjango-web-implementation-htmx`, 언어·frozen dataclass → `dddjango-web-implementation-python`, UI JS → `dddjango-web-implementation-javascript`

## 핵심 운영 원칙

- URL path·name 리터럴은 `<bc>_router.py`에만 — `class <Bc>Routes` 상수(네임스페이스 붙은 name)로 묶고 `reverse`·`redirect`는 상수·href만 받는다(문자열 리터럴 금지 — NM13) (§2)
- navigator는 `reverse(<Bc>Routes.…)` 정적 href 헬퍼 — router를 **헬퍼 함수 안에서** import한다(router→view→VM→navigator→router 순환을 첫 import에서 끊는다·국소 ruff에 PLC0415를 켜지 않는다) (§2)
- 템플릿은 URL을 만들지 않는다 — `{% url %}`·`href="/…"` 금지, State의 href만 (§2·§6)
- 문서 셸은 `root/scaffold/view/root_view.html` — 모든 페이지가 extends, htmx core는 build-state `htmx_core_static` 경로를 로드 (§2)
- extends 대상은 둘뿐 — 페이지 → `root_view.html`만 · 조각(section·widget·component) → `design_system/component/**`만(IM26) · 공용 부품에 값만 넘기면 `include … with … only`, 마크업 자리는 부품의 `{% block %}`을 extends로 채운다(slot 부품) (§6·§10)
- 게이트·세션 신원 이월·탭 기록은 `RootRequestHandler.process_view`에서 **view 모듈이 `web.`으로 시작할 때만**(같은 프로세스 API 호출의 재진입 차단) · `__call__`은 응답 뒤 신원 reset + 조각 요청의 3xx를 200 + `HX-Redirect`로 (§2·§6)
- 다른 화면이 임베드하는 화면은 셸 없는 `<화면>_embed_fragment` + navigator `<화면>_embed_href()` (§2)
- **탭 재탭 2단 동작(확정)·전환 복원**: RootVM이 현재 탭은 첫 화면 href, 다른 탭은 세션 `root.tab_last`의 마지막 경로로 — 재탭은 첫 화면 복귀·맨 위, 전환은 마지막 위치 복원, BC는 무관여 (§3)
- BC 화면의 유일한 접점: 최상위에 별도 스크롤 컨테이너를 두지 않는다(문서 스크롤 유지) · 탭 링크에 hx-get·hx-boost 금지 (§3)
- in-process 실패 종류는 셋(상태코드 `ApiStatusError`·백엔드 미처리 예외=500·파싱) — 타임아웃 없음, 세션 이월(미들웨어+contextvar)은 쿠키 부착 한정·정규화는 safe_api_call 단일 출구 (§4)
- DataSource는 `ApiClient`로 엔드포인트를 부르는 plain class — 도메인 엔티티 직반환, 백엔드 경로 리터럴의 유일 거처 (§4)
- VM은 요청마다 새로 — 요청 사이 값을 VM·모듈 전역에 두지 않는다 · POST는 CSRF(`{% csrf_token %}`·`hx-headers`) · 출력은 자동 이스케이프만(`|safe` 금지) · Django Form 층 없음 (§6)
- 정적 이미지 `<img src="{% static 'web/images/…' %}">` — 경로는 asset-manifest `local_path` 그대로 (§8) · 형상은 동결 시안을 템플릿+CSS로 빠짐없이 재현·직수입 금지 (§9)
- 색·글자 리터럴은 `design_system/foundation/*.css` 안에서만 — 조각 CSS·부품 CSS·`style` 속성 금지(NM10) · 부품 CSS 클래스는 `<수식>-<군>` 접두·상태는 BEM `--`·`aria-*`/`data-*`(NM12) · 초기화·웹폰트는 theme (§10)
- 외부 JS는 명세가 고른 것만 `web/static/vendor/<라이브러리>/<버전>/` 고정 사본 — CDN 실행 태그 금지 (§11)
- **테스트는 전용 스킬로 이전**: 무엇을/오라클/비-vacuity/단언 FORM은 `dddjango-web-discipline-test`, Django 메커니즘(VM 대체·테스트 클라이언트·HTML 단언·HTMX 헤더·`unittest.mock`·날짜 주입·브라우저 테스트)은 `dddjango-web-implementation-test` (§7)

## 상세 레퍼런스

| 질문 | 위치 |
|---|---|
| 버전·전제·호스트 연결 경계 | [`references/final.md`](references/final.md) §1 |
| path·Routes·navigator·문서 셸·게이트·전환 표기 | final.md §2 |
| 탭 재탭 동작을 어떻게 구현하나 | final.md §3 |
| api_client 실패 종류·세션 이월·DataSource 표기 | final.md §4 |
| 로컬 저장 | final.md §5 (web에는 해당 없음) |
| 템플릿 표지·요청 수명·대화 표시·CSRF·템플릿 표기 | final.md §6 |
| 테스트 표기는 어디로 이전했나(dddjango-web-discipline-test·dddjango-web-implementation-test) | final.md §7 |
| 정적 이미지 에셋·`{% static %}` 표기 | final.md §8 |
| 레이아웃 형상 — 시안 충실 재현 | final.md §9 |
| foundation 변수·theme(초기화·웹폰트)·부품/조각 CSS | final.md §10 |
| 외부 JS 고정 사본 | final.md §11 |

각 절은 필요한 절만 읽는다(`## §N.` 헤더로 grep 가능 — 전체 로드 불필요).
