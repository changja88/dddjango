# dddjango-web 실전 런(web 인증 3화면) 문제 정리 — 2026-09-05

- 상태: **v1 문제 목록**(발주자 정리 · 원인은 가설 — 반증 패널 전). 수정 대상은 대부분 플러그인 `dddjango-web`이고, 두 건은 발주자(orchestrator) 운영 교훈이다. 선행 문서: `2026-08-24-web-fidelity-defects-analysis.md`(실전 런 1호 — 요소별 값 배정·스크롤 고정 결함).
- 런 식별: 저장소 `spring_dream_server` · 브랜치 `feat/web-auth`(linked worktree) · 산출물 `.dddjango-web/20260905-0046-web-auth-screens/` · 커밋 `71dd100a`(Phase 2 진입)‥`4d671849`(HEAD, 14커밋) · 레인 Claude Opus 4.8 · **설치본 dddjango-web 1.0.0**(`installed_plugins.json` sha `6b99442` · lastUpdated 2026-08-25) · 시안 DesignSync project `80b31c85-c19c-4d97-924a-f13726b54735` `로그인.dc.html`(480×768 카드 3장 = 로그인·가입하기·비밀번호 찾기) + `_ds/chunmong-design-system-9ad494f0…` · 계약 accounts 5 endpoint.
- 증거 사본(`assets/2026-09-05-web-auth/`): `design-login-10x16.png` 시안 캡처(사용자 제공, 492×781) · `mobile-actual-login.png` 구현 모바일 캡처(사용자 제공, 992×1992) · `web-auth-login-v2.png` 구현 1440×900(발주자 Playwright, 교정 커밋 `add451cf` 뒤).
- 게이트 통과 이력(문제의 배경): 레인 G0·G1·G2 결정적 게이트 전부 통과(백스톱 24검사 blocker 0 · 모션 대조 0 · 규율 감사 blocker 0 · green 신규 0) → 발주자 G2(mypy 0 · ruff 0 · registry_gate 귀속 0 · make test 통과 · OpenAPI 동일) → **사용자 육안 대조에서 불합격**. 즉 아래 문제 대부분은 «결정적 게이트가 모두 green인 상태에서» 남은 것이다.

## 1. 문제 목록

| # | 문제 | 발견 | 결정적 게이트가 잡았나 | 소유 | 상태 |
|---|---|---|---|---|---|
| 1 | **시안 프레임 비율(10:16) 무시** — 시안의 480×768 카드를 «디자인 도구 프리뷰 chrome»으로 처분하고 전체 뷰포트 + 350px 중앙 컬럼으로 재구성 → 모바일에서 구성이 시안과 다름 | 사용자 육안 | ✗ (프레임·비율 규칙 자체가 없음) | 플러그인 규범 공백 + 설계 판단 | 미해결 |
| 2 | **시안 이미지 미착지** — 로고 캘리그라피(258px)·구름 장식 ×2(76px)·gold-blossom(버튼 장식) 전부 placeholder(텍스트 워드마크 «춘몽»·장식 생략) | G0에서 표면화 → 발주자가 placeholder 확정 → 사용자 거부 | ✗ (도구가 실패를 표면화는 함 — 처분이 틀림) | 도구 한계(DesignSync 256KiB 캡) + 발주자 결정 오류 | 미해결 |
| 3 | **시안에 없는 UI 발명** — «로그인 상태 유지» 체크박스. 시안에서는 `keepSignedIn` prop **default false**·`<sc-if value="{{ showKeep }}">` 안의 미노출 변형인데, 계약 `remember_me`가 있다는 이유로 노출 | 사용자 | ✗ (design-review-web 항목 5 «시안에 없는 요소 발명 금지» 점검이 있으나 통과) | 플러그인(리뷰 강도·계약→UI 유도 규칙 부재) | 미해결 |
| 4 | **글자색·링크 스타일 편차** — 시안: 인사말 `--ink-800` + 강조 `--gold-600`, 하단 «가입하기 │ 비밀번호 찾기»는 ghost Button(sm) + hairline 세로 구분선. 구현: 링크가 핑크 굵은 글자·구분선 없음 등 | 사용자 | ✗ (render-audit N/A → 실측값 비교 자체가 없었음) | 플러그인(`.dc.html` 시안의 실측 경로 부재) | 미해결 |
| 5 | **비밀번호 보기(eye) 토글 미구현** — 시안에 IconButton `eye`/`eye-off` 존재. «커스텀 JS 금지»로 명세에서 미구현 처분(비-모션 위험 항목) | 명세(발주자·사용자 미인지) | — | 규범 충돌(시안 요소 vs JS 금지)을 제품 결정으로 올리지 않음 | 미해결 |
| 6 | **Django 여러 줄 `{# … #}` 주석이 화면에 글자로 노출** — 7 템플릿(컴포넌트 4 + section 3). Django `{# #}`는 한 줄 전용 | 발주자 Playwright | ✗ (백스톱·규율 감사 통과) | 플러그인(렌더 스모크 부재·템플릿 주석 규칙 없음) | 해결 `add451cf` |
| 7 | **동결 fonts.css의 gstatic 절대 URL 404** → Gowun Batang 미로드(콘솔 404 ×2, `document.fonts` error) | 발주자 콘솔 | ✗ | 플러그인(외부 자원 도달성 검사 없음 · «동결 fonts.css 그대로 재사용» 규칙) | 해결 `add451cf` |
| 8 | **저장소 전체 규약(#493 첫 대입 주석·#645 `Any`) 위반 110건** — dddjango-web 백스톱(24검사)에는 dddjango registry 검사기가 없어 레인 G2 green, 발주자 `registry_gate --anchor`에서 red | 발주자 registry_gate | ✗ | 플러그인 간 게이트 정합 | 해결 `49247355` |
| 9 | **G2 «시각 대조»가 브라우저 렌더 0회로 끝남** — `.dc.html` 시안은 render-audit N/A(`has_render_audit=false`) → G2 시각 = 결정적 게이트 통과로 종결. 6·7이 그래서 살아남음 | 구조적 | — | 플러그인 | 미해결(근본) |
| 10 | **운영: 시안 자산 결손을 사용자에게 올리지 않음** — 발주서 §5 «제품 결정만 에스컬레이션» 목록에 «시안 자산(이미지) 수급 불가»가 없어 발주자가 기술 판단으로 placeholder 확정 | 사용자 지적 | — | 발주자(발주서 템플릿) | 교훈 |

## 2. 상세

### 2.1 시안 프레임 비율(10:16) — 문제 1

- 사실: 시안 `.dc.html`은 3화면을 각각 `width: 480px; height: 768px` 카드로 배치한다(동결본 `design-ref/로그인.dc.html` — `480px`·`768px` 각 3회). 480:768 = 10:16. 사용자 진술: «우리는 기본적으로 10:16 비율로 디자인을 제작한다» — 즉 아트보드 비율은 도구 아티팩트가 아니라 **디자인 계약**이다.
- 명세 처분(design-spec.md:283): «시안 프레임 = 디자인 도구 아티팩트 … 프리뷰 chrome이지 화면 내용이 아니다 — coder는 실제 모바일 화면(전체 뷰포트·bg-app 배경·`--content-max`(350px) 중앙 컬럼)으로 재구성하고 480×768 카드·화살표·세로 라벨은 재현하지 않는다.» 카드 사이 화살표·세로 라벨을 chrome으로 본 것은 맞지만, **카드 크기까지 chrome으로 묶어 버렸다**.
- 결과: `mobile-actual-login.png`(9:19.5 폰)에서 로고·인사말·패널이 시안 구성과 다르게 놓이고 하단 절반이 빈 배경. `design-tokens.json`의 `layout` 절은 **빈 객체 `{}`** — 프레임 크기가 토큰으로 절단되지 않았다.
- 원인 가설: (a) 플러그인 규범에 아트보드 크기·비율을 어떻게 다룰지 규칙이 없다(architecture-web·houserules·agents 전부 «artboard/프레임/뷰포트/비율» 0건). (b) `extract_design`이 layout 토큰을 비워 두면 architect가 프레임을 «없는 것»으로 취급한다. (c) G1 리뷰(design-review-web)에 «시안 프레임 처분»을 점검하는 항목이 없다.
- 수정 방향: Phase 0에서 화면 카드의 W×H를 추출해 `design-tokens.json.layout.frame`에 기록(«프레임 = 레이아웃 계약» 기본값). 명세는 프레임 기준 좌표를 쓰고, **뷰포트 대응 정책**(contain 스테이지 / 폭 기준 스케일 / 브레이크포인트)은 사용자 결정 항목(PRODUCT-DECISION)으로 노출한다. 프레임을 chrome으로 처분하려면 명세에 근거를 쓰고 리뷰어가 대조한다.

### 2.2 시안 이미지 미착지 — 문제 2

- 사실: 시안 `<img>` 3건(`assets/chunmong-logo-v2.png` 258px · `assets/cloud-ornament.png` ×2 76px, 우측 `scaleX(-1)`) + 디자인 시스템 `assets/ornaments/gold-blossom.png`(SpecialButton 장식). `asset-manifest.json` 2항목 모두 `status: "failed"` — note: «DesignSync get_file 256KiB 캡에 절단(truncated:true · 262144 base64 cap · IEND 없음 · PIL 'image file is truncated')». `has_design_images=false` → design-spec §이미지 정형 목록(335~337행)·§⑧(410행) «로고 이미지 placeholder(G0) — 텍스트 워드마크 «춘몽», 원본 도착 시 교체».
- 흐름: `fetch_images.py`는 «조용한 폴백 금지»(139·193행)를 지켜 실패를 표면화했고, Coordinator는 G0에서 orchestrator에 올렸다. **orchestrator(발주자)가 placeholder를 확정**했고 사용자에게 묻지 않았다. 사용자: «시안에 있는 이미지는 다운 받아서 asset에 넣어야 하는데 하지도 않았다».
- 원인: (a) 도구 한계 — DesignSync `get_file`은 256KiB 캡이라 원본 PNG를 온전히 못 받는다(플러그인이 우회할 수 없음). (b) **결정 소유 오류** — 시안 자산 결손은 화면 외형을 바꾸는 «제품» 문제인데 발주서 §5 에스컬레이션 목록(시안 artboard 부재·카피/법적 문구·UX 분기·계약 부재)에 없어 기술 판단으로 흘렀다. (c) 명세가 placeholder를 «정상 처분»으로 문서화해 G1·G2 어디서도 blocker가 아니었다.
- 수정 방향: `has_design_images=false`이면서 시안에 `<img>`가 있으면 **자동 placeholder 금지** → G0에서 «자산 수급» PRODUCT-DECISION(사용자가 수동 다운로드해 `design-ref/assets/`에 착지 / 워드마크 대체 승인 / 보류)을 강제. 착지 폴더에서 `fetch_images.py --assets-root`가 재동결하는 절차를 성문. 발주서 템플릿 §5에 «시안 자산 결손» 항목 추가.

### 2.3 시안에 없는 UI 발명 — 문제 3

- 사실: 동결 시안 로그인 카드의 «로그인 상태 유지»는 `<sc-if value="{{ showKeep }}">` 안 Checkbox이고(동결본 오프셋 ~6187), 컴포넌트 props 선언에 `keepSignedIn … "default": false … "label": "로그인 상태 유지 체크박스"`(오프셋 ~25885). 같은 파일의 `showSocial`(default false)은 명세가 «기본 false(장식 옵션) + 계약 부재»로 **미구현** 처분(design-spec.md:286)했으면서, `keepSignedIn`은 계약에 `remember_me`가 있다는 이유로 노출했다(명세 170·182·235행). 같은 신호를 반대로 처분한 셈이다.
- 원인 가설: «계약 필드가 있으면 UI를 만든다»는 암묵 규칙. design-review-web 항목 5는 «시안에 없는 요소 발명»을 점검하지만 시안 파일 안에 문자열이 존재하면(변형 안에 있어도) 통과된 것으로 보인다.
- 수정 방향: 규범에 명문화 — **시안 default false 변형(`sc-if`·props default·`showX` 플래그)은 미노출이 기본**이고, 계약 필드는 UI 요소의 근거가 아니다(계약이 요구하는데 시안에 없으면 PRODUCT-DECISION — 이번 런의 name/terms 처리와 동일 경로). 리뷰어 체크: 명세 요소 목록의 각 항목에 «시안 좌표(오프셋/컴포넌트)와 그 변형 default»를 붙이게 하고 default false면 근거 요구.

### 2.4 글자색·링크 스타일 편차 — 문제 4

- 사실(시안, 동결본 오프셋 ~5021·~6804): 인사말 `font: var(--fw-regular) var(--fs-title-3)/1.66 var(--font-serif); color: var(--ink-800)`, 강조 `<strong>` `color: var(--gold-600)`; 하단 링크 = `Button variant="ghost" size="sm"` 둘 사이 `width:1px;height:13px;background:var(--border-hairline)` 세로선. 구현(`web-auth-login-v2.png`·`mobile-actual-login.png`): 링크 두 개가 핑크(버튼 계열 색) 굵은 글자, 구분선 없음. 인사말도 시안 캡처와 톤이 다르다(사용자 지적 «폰트색도 달라»).
- 원인 가설: 토큰은 174개 채택됐지만(명세 «토큰 전수 처분») **요소↔토큰 배정**은 architect 서술에 의존하고, `.dc.html` 시안은 render-audit(실측)이 없어 computed 값 대조가 0회였다. 선행 문서 1호의 A1(«요소↔값 결합 부재»)과 같은 뿌리.
- 수정 방향: `.dc.html`도 실측 가능하게 — Playwright로 시안 파일 자체를 렌더(DesignSync에서 받은 HTML + `_ds` 번들)해 `render-audit.json`을 만드는 경로를 검토. 불가하면 최소한 명세의 요소 목록에 시안 인라인 스타일(font/color) 원문 인용을 의무화하고 coder가 그 토큰을 쓰도록 백스톱(요소별 색 토큰 대조).

### 2.5 eye 토글 미구현 — 문제 5

- 사실: 시안 IconButton `icon: on ? 'eye' : 'eye-off'`(오프셋 ~30182). 명세 393행 «[비-모션 위험] 비밀번호 보기(eye) 토글 미구현(커스텀 JS 금지) — password 필드는 항상 가림».
- 문제: 시안에 있는 상호작용 요소를 규범(커스텀 JS 금지) 때문에 제거하는 것은 화면 요구를 바꾸는 결정이다. 사용자·발주자 모두 G1 요약에서 이를 결정 항목으로 보지 못했다.
- 수정 방향: «시안 요소 vs 규범 충돌»은 명세의 별도 표(«규범 충돌 처분»)로 모아 G1에서 반드시 노출하고, 처분은 PRODUCT-DECISION(허용 최소 JS / 생략 승인 / 대체 UI). htmx 표준 속성만으로 불가한 상호작용의 허용 범위를 규범이 정의해야 한다.

### 2.6 템플릿 주석 노출 — 문제 6 (해결)

- 사실: `web/design_system/component/{backdrop/aurora_backdrop,progress/step_progress,bar/app_bar,field/text_field}.html` · `web/accounts/signup/section/signup_password.html` · `web/accounts/password_reset/section/{password_reset_done,password_reset_password}.html` 첫 줄이 여러 줄 `{# … #}`. 렌더 결과 `/login/`에 주석 본문 4개가 텍스트로 노출(Playwright `document.body.innerText` `{#` 4건). 백스톱 24검사·규율 감사·green 모두 통과.
- 수정: `add451cf` — `{% comment %}` 변환 + `tests/test_web_auth_screens_render.py`(3화면 GET 200 · 본문 `{#` 미포함).
- 플러그인 방향: (a) coder-web·houserules에 «템플릿 주석은 `{% comment %}` 또는 한 줄 `{# #}`» 성문 + 백스톱(«`{#` 뒤 같은 줄에 `#}` 없음» 정적 검사). (b) G2에 **렌더 스모크 의무**(§2.9).

### 2.7 죽은 폰트 URL — 문제 7 (해결)

- 사실: `web/design_system/foundation/tokens.css` 6행 `@import url("https://fonts.googleapis.com/css2?family=Gowun+Batang…")` + 8~9행 `@font-face{font-family:"Gowun Batang"… src:url("https://fonts.gstatic.com/s/gowunbatang/v7/…woff2")}`(동결 `_ds/tokens/fonts.css`에서 그대로 옮김 — 명세 «동결 fonts.css를 그대로 재사용(R4)»). gstatic 파일 URL 2건 404 → 나중 선언인 @font-face가 이겨 서체 로드 실패(`document.fonts` `Gowun Batang:400:error`).
- 수정: `add451cf` — 8~9행 제거(@import만 유지), 편차 기록.
- 플러그인 방향: 동결 CSS의 **절대 URL 자원은 도달성 검사(HEAD 200)** 뒤 채택, 실패 시 표면화. 콘솔 404 0건을 G2 렌더 스모크 항목에 포함.

### 2.8 저장소 공용 규약 미준수 — 문제 8 (해결)

- 사실: 발주자 `registry_gate.py . --anchor 58d8925e` → 귀속 110건 red, 전부 `check-public-surface-annotation.py`(#493 모듈·지역 변수 첫 대입 타입 주석 없음 110 · #645 `Any` 16 — `web/accounts/signup/view_model/signup_view_model.py` 39 · `password_reset_view_model.py` 32 · form/state/view/client 나머지). 레인은 mypy strict·ruff·web 백스톱 24검사 green이었다.
- 수정: `49247355`.
- 플러그인 방향: dddjango-web G2 정의에 «저장소가 dddjango를 채택했으면 `registry_gate --anchor <base>` 귀속 0»을 명시(web/은 저장소 공용 규약 예외가 아님). coder-web 규율에 #493·#645 요지 인용.

### 2.9 G2 시각 대조의 구조적 공백 — 문제 9

- 사실: `build-state.json` `has_render_audit=false`, `g2_visual` = «결정적 게이트 통과 … 렌더 실측 N/A(.dc.html)». 레인은 runserver·브라우저를 한 번도 띄우지 않았고, 발주자가 임시 Postgres + `settings.local` 더미 env + Playwright로 처음 렌더해 6·7을 찾았다. 사용자 육안 대조가 1·3·4를 찾았다.
- 수정 방향: G2에 **렌더 스모크(필수)** — 대상 화면 전부 GET 200 · 본문에 `{#`/`{{`/`{%` 잔존 0 · 콘솔 404/JS 오류 0 · 폰트 로드 확인 · 시안 프레임 비율(문제 1)과 폰 비율 두 뷰포트 스크린샷 산출 → 사용자 육안 대조 입력물로 REPORT에 첨부. 로컬 DB 없이도 돌도록 `django.test.Client` 경로(테스트) + 선택적 runserver 경로를 모두 성문.

### 2.10 발주자 운영 교훈 — 문제 10

- 이미지 결손(§2.2)을 사용자에게 올리지 않은 것, «로그인 상태 유지»·eye 처분을 G1 요약에서 걸러내지 못한 것은 발주자 판단 오류다. 발주서 §5 «제품 결정만 에스컬레이션» 목록에 다음을 추가한다: 시안 자산 결손, 시안 요소의 미구현 처분(규범 충돌 포함), 시안 default 변형의 노출 여부, 시안 프레임 처분.
- 발주자 G2 체크리스트에 «브라우저 렌더 + 스크린샷 사용자 전달»을 고정한다(이번 런은 사후에 추가).

## 3. 처분 제안 순서 (플러그인 입력)

1. **규범 3건 성문**(architecture-web·houserules·design-review-web): 시안 프레임 = 레이아웃 계약(§2.1) · 시안 default false 변형 미노출·계약≠UI 근거(§2.3) · 시안 요소 vs 규범 충돌은 G1 결정표(§2.5).
2. **G0 자산 결손 → PRODUCT-DECISION 강제 + 수동 착지 절차**(§2.2).
3. **G2 렌더 스모크 필수화 + 백스톱 2종**(템플릿 주석 · 절대 URL 도달성)(§2.6·2.7·2.9).
4. **dddjango-web G2에 `registry_gate --anchor` 의무 명시**(§2.8).
5. `.dc.html` 시안 render-audit 경로 검토(§2.4) — 불가 판정이면 요소별 스타일 원문 인용 의무로 대체.

## 4. 미해결 질문

- 10:16 프레임의 뷰포트 대응 규칙(폰 9:19.5·데스크톱)을 어떻게 정의할지 — 사용자 결정 필요(§2.1).
- DesignSync 256KiB 캡을 우회하는 정식 경로가 있는지(도구 측). 없으면 «사용자 수동 다운로드 착지»가 유일한 경로다.
- 커스텀 JS 금지 아래 eye 토글 같은 시안 상호작용을 어디까지 허용할지(§2.5).
