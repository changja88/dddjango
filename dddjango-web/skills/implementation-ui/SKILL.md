---
name: implementation-ui
description: web 구현 표기법 — 시안 재현 절차(직수입 금지·토큰화·asset-manifest), 삼총사 view/view_model/state·form 표기, Django 템플릿·HTMX section 표기(커스텀 JS 금지·vendored htmx), design_system 토큰·CSS, in-process client(django.test.Client)·urls. web/ 트리의 코드를 구현할 때 먼저 로드한다. 무엇을 어느 조각에 담는가·판별·승격·계약 소비 절차는 architecture-web, 트리·명명 사실은 discipline-web-houserules, 보편 클린코드는 discipline-cleancode로 위임.
user-invocable: false
---

# web 구현 표기

## 언제 쓰나

`web/` 트리의 코드를 쓸 때 로드한다 — HTML 템플릿·삼총사 .py(view/view_model/state)·form·section·widget·design_system·client·urls. 시안(이미지·HTML)을 화면으로 재현할 때, HTMX 부분 재렌더·토큰·에셋을 배선할 때도 여기다. 전문을 읽지 말고 아래 라우팅 표로 필요한 절만 부분 적재한다. 경계:

- 무엇을 view/section/widget 어느 조각에 담나 — 판별·승격·계약 소비 절차 → `architecture-web`
- 파일을 어느 폴더에 어떤 이름으로 만드나 — 트리·명명 사실 → `discipline-web-houserules`
- 명명·함수 형태·캡슐화·중복 같은 보편 규율 → `discipline-cleancode`
- 호스트 배선(INSTALLED_APPS·TEMPLATES DIRS·STATICFILES_DIRS 프리픽스 튜플·ROOT_URLCONF include·ALLOWED_HOSTS·htmx vendored 설치) → Coordinator — 커맨드 Phase 0 전제조건 검사
- BC 안 서버렌더(driven_layer templates·Django admin)는 비관할 — dddjango 플러그인 소관

## 핵심 운영 원칙

- **재현이지 직수입이 아니다** — 시안 HTML의 마크업·클래스·인라인 스타일 복붙 금지. 외형 관찰→시각 값 tokens.css 등록→3단 분해 재구축. 보이는 요소는 빠짐없이 재현 (§2)
- 시안 없으면 coder-web 재량+기존 design_system 관례 — placeholder로 조용히 채우지 않고, 근사 처리는 보고에 표면화 (§2)
- view는 함수 뷰 고정 — URL 바인딩·form 수신·세션 쿠키 추출·VM 호출·render·fragment 분기(HX-Request 헤더 또는 전용 라우트)만, 판단 금지. auth는 `@login_required` — 페이지·fragment 라우트 동일 적용 (§3)
- 입력 검증=form(`form/` 조건 생성·`<View>Form`)·표시 상태=VM 분담. VM이 client 호출→응답 모델→state 조립·계약 예외를 표시 상태로 번역·session_key 운반. state는 `@dataclass(frozen=True)` 프리미티브·중첩 dataclass — 예외로 Django Form 1종(검증 실패 재렌더 시 운반), 타입 힌트 전면 (§3)
- 템플릿: extends 첫 비주석 줄·load 알파벳순·태그 안 한 칸 공백·block 이름으로 닫기·state만 참조(표시 분기만 — 계산·필터링 금지) (§4)
- `{% url %}`·`{% static %}` 의무 — 경로 하드코딩 금지. base.html은 «거의 빈» 골격 (§4)
- section=`<view>_<section>.html` — 허용 htmx 속성은 hx-get·hx-post·hx-target·hx-swap·hx-headers·hx-trigger. CSRF는 state-changing(hx-post)만 hx-headers 토큰, state-changing도 페이지와 같은 auth·permission·CSRF (§5)
- **커스텀 JS 금지** — 동작은 htmx 속성으로만. inline `<script>` 금지·web/** .js 신설 금지, htmx는 static/js/ vendored 단일 파일·CDN 금지 (§5)
- widget·component include는 `with … only` 의무 — 암묵 context 상속 금지. 페이지→section include는 state 명시 전달(`with state=state`). widget에 화면 이름 금지·component에 BC 어휘 금지 (§5·§6)
- 스타일 값은 `var(--…)`만 — 리터럴 금지. 이미지는 static/images/ 착지·asset-manifest 같은 src 행 조인(`local_path`→`{% static %}`·token 열 비소비)·manifest 없으면 절 비적용(placeholder 금지) (§7)
- client는 `Client(raise_request_exception=False)` 고정 — capability별 호출 함수 안 생성(공통 호출기 없음)·view가 추출한 session_key를 VM 경유 이월(None=익명)·계약 근거는 server-contract.json 경량본뿐·BC URL 리터럴은 client 전속 (§8)
- 영역 urls.py가 path·name 단일 출처(fragment 라우트 포함) — 루트는 include 합산, `app_name` 네임스페이스로만 참조 (§9)

## 상세 레퍼런스

| 주제 | 절 |
|---|---|
| 이 스킬의 소관·비관할 handoff | [`references/final.md`](references/final.md) §1 |
| 시안(이미지·HTML)의 화면 재현 절차 | final.md §2 |
| view·view_model·form·state 파일 표기 | final.md §3 |
| 페이지 템플릿·base.html 표기 | final.md §4 |
| section 파일·HTMX 속성·CSRF·JS 금지 표기 | final.md §5 |
| widget·component include 표기 | final.md §6 |
| tokens.css·이미지 에셋 표기 | final.md §7 |
| client 호출·신원 이월·응답 모델·예외 변환 표기 | final.md §8 |
| urls 정의·include 합산·name 참조 표기 | final.md §9 |

각 절은 필요한 절만 읽는다(`## §N.` 헤더로 grep 가능 — 전체 로드 불필요).
