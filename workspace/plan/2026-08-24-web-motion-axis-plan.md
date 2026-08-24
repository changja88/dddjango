# dddjango-web «동적 표현(모션) 축» 개정 계획 v2 (적대 리뷰 반영 확정본)

- 상태: **v2 구현 완료** (2026-08-24. v1 → 3인 반증 패널 35건 → 처분 반영 → §4 전 행 집행. 검증: run_fixtures 105 PASS 양측 · `claude plugin validate --strict` 통과 · `make verify` green)
- 소유: dddjango-web 플러그인 (전 파일 산문 정본 — 온톨로지 밖·md 직접 수정)
- 적대 리뷰: R1 규율·회색지대(12건) · R2 파이프라인 배선(11건) · R3 과공학·실무 함정(12건) — 처분 대장은 §7

## 1. 문제 (진단 요약 — v1과 동일)

kkebi.io/saju(원본·Expo/RN Web)의 hover가 산출물에 0건 탈락. 원본 hover는 CSS가 아니라 JS 런타임(`onHoverIn`·`hovered`)이라 정적 동결(HTML·토큰 절단·스크린샷)에 0비트 담긴다. `extract_design.py:358`은 `hover:` 변형 접두를 명시 제거. `design-review-web.md` ⓓ의 상호작용 상태 검사는 먹일 입력이 없어 공허했다. 08-24 «암묵값 전수» 개정(정적 암묵값)과 다른 축.

## 2. 사용자 확정 결정 (이 대화 — 2026-08-24 · 리뷰로 뒤집힌 것 없음)

- **결정 ①** 우산 축 = «동적 표현» — 상호작용 상태(hover/focus/active/disabled) + 모션(transition·keyframes·스크롤 리빌).
- **결정 ②** 모션 별도 관리 — `design_system/foundation/motion.css`. 규범은 자리·판형만, 내용물은 런마다.
- **결정 ③** JS 허용 확장 = D12 v2 — **닫힌 2파일 열거**: `static/js/`의 vendored `htmx.min.js` + `motion.js`. 그 외 vendored 추가 금지 문장은 보존·이월(«형태 한정» 서술로 일반화하지 않는다 — R1-12). 화면 코드는 JS를 쓰지 않고 `data-motion` 선언만.
- **결정 ④** motion.js 거처 = `static/js/` — 변경 이유 분리(디자인 값 vs 고정 인프라)·«JS 유일 거처» 불변식·design_system에 JS 범주 불개방.
- 커버 경계: 상태·전환·keyframes·스크롤 리빌까지. 패럴랙스·제스처·물리 스프링·`hx-swap`의 `transition:true`(View Transitions — 채널 단일화)는 **한계/금지 칸**. 러너 기능 확장 금지.

## 3. 설계 상세 (v2 — 리뷰 반영)

### 3.1 소유 경계

| 무엇 | 거처 | 규칙 |
|---|---|---|
| 모션 custom property 정의 전부(`--duration-*`·`--ease-*`·이동거리·스케일 등) | `foundation/tokens.css` | motion.css엔 custom property 정의 금지 — keyframes·클래스 선언만(keyframes 중간값 리터럴은 허용) (R1-10) |
| **공용** `@keyframes`·모션 유틸 클래스 | `foundation/motion.css` | 명명 `motion-*` 고정 · **화면 어휘 금지 유지** (R1-9) |
| **화면 전속** `@keyframes` | 그 화면 CSS(`static/css/*.css`) | `<view>_` 접두 필수 — 화면 어휘를 design_system에 넣지 않는 절충 (R1-9) |
| `:hover`/`:focus-visible`/`transition` 규칙 | 화면 CSS·component CSS 직접 | 값은 `var()` 참조(기존 토큰 규칙) |
| 발동 러너 | `static/js/motion.js` (vendored·**조건 설치**) | §3.2 |
| 초기 은닉·PRM 가드 | **CSS 단일 소유** | 은닉은 `html.motion-ready` 하위 셀렉터 + `@media (prefers-reduced-motion: no-preference)` 안에서만 — 러너 실패·차단 시 콘텐츠 항상 표시 (R3-4·R3-9) |

### 3.2 motion.js 판형

- 소스 `dddjango-web/assets/motion.js` → **명세의 러너 분류 채택 항목 ≥1일 때만** Phase 2 진입 준비에서 Coordinator가 `cp` 설치 (R3-5 조건화). base.html `<script defer>` 배선은 coder-web이 명세 근거로 수행.
- 동작: 로드 시 `document.documentElement`에 `motion-ready` 부여 → `[data-motion]`을 IntersectionObserver로 관찰, 진입 시 `motion-in` 부여 후 **unobserve(one-shot)** → MutationObserver(htmx 비의존)로 신규 노드만 재등록 (R3-7). PRM 분기 없음 — CSS가 소유 (R3-9). 의존성 0·IIFE·`defer` 로드 (R3-11).
- 수정·확장 금지의 집행 = **canonical asset 해시 대조**(backstop이 자기 위치 기준 `../assets/motion.js`와 대조 — cp 판형이라 결정적) (R1-4).

### 3.3 파이프라인 배선

1. **관찰 — 1차 주체는 사용자** (R2-1·R3-2): 발동 조건 = **원본이 실서비스 화면(제공 형식 무관 — 참조 HTML/URL·스크린샷-only 포함)** (R2-7). Coordinator는 ⓐ 동결본 정적 스캔(`:hover`·`transition`·`@keyframes` grep — CSS 네이티브 원본의 실신호 수확) ⓑ 사용자 문답(트리거별: 마우스 올림/포커스/로드/스크롤/교체 시 무엇이 어떻게 변하나) ⓒ 기록 서기. 기록 판형(수치 칸 포함 — R3-8): 요소 / 트리거 / 효과(변화 전→후 값·duration·easing — 측정 불가면 '근사' 명기) / 재현 분류(CSS | 러너 | 한계). 산출: `<산출물 폴더>/motion-notes.md`. 사용자가 관찰 생략 시 «미관찰+사유» 기록. `.dc.html` 경로·트리비얼(산출물 폴더 없음)은 해당 없음 1줄, static_only는 의무 동일(교체 모션만 해당 없음) (R2-7).
2. **Coordinator 닫힌 목록**(:9·:193)에 motion-notes.md + «vendored JS 설치(htmx·조건부 motion)» 반영 (R2-3·R1-3).
3. **플래그** `has_motion_notes` — 스키마(:55)+갱신 시점 «플래그 4종»(:63)+설정 스텝(:121) 삼중 배선 (R2-8). 재동결 합류 질문을 3종(openapi·design-ref·motion-notes)으로 (:114) (R2-6).
4. **전달**: Phase 1 입력 열거(:131 architect·:132 review-web)에 `(있으면) motion-notes 경로` 추가 + 두 에이전트 md 입력 절 (R2-4). coder-web에는 전달하지 않는다 — 명세가 단일 근거(한계 항목은 명세에 «한계»로 박혀 집행).
5. **설계**: architecture-web §8 «동적 표현 전수(설계자 소유)» — motion-notes 전 항목 채택/기각/한계 처분(빈칸 0).
6. **리뷰**: design-review-web ⓓ의 대조 입력 = motion-notes 명시.
7. **구현 표기**(implementation-ui 모션 절): motion.css/화면 keyframes 접두 판형 · htmx 클래스 짝에 **`swap:`/`settle:` 수식어 필수 표기**(기본 swap 0ms·settle 20ms라 수식어 없인 무효과 — R3-6) · `data-motion` 소비 · base.html 로드 태그 판형(`{% static %}` 정확 경로·`defer`) · `hx-swap` `transition:true` 금지 · 한계 항목 구현 금지.
8. **G2 ⓑ**: 대조 범위에 hover/focus·로드/교체 모션 + **대조 기준 = motion-notes 채택 항목** 명시, static_only는 교체 모션 해당 없음 (R2-10). `g2_visual`에 포함.

### 3.4 트리·골격·생성 주체

- 트리 v3.1 → v3.2: foundation/에 `motion.css`, `static/js/` 주석 «vendored 2종(htmx·motion[조건]) — D12v2».
- **motion.css 생성 주체 = coder-web 첫 슬라이스**(tokens.css와 동일 — :145 귀속. 최초 골격(Coordinator)에 넣지 않는다 — 소유 충돌 해소, R2-9 채택·R3 빈 골격안 기각). 배선 ⓕ는 htmx 존재 검사 유지 + motion.js는 조건 설치라 존재 검사 아닌 문면 참조만.

## 4. 변경 파일 (v2 전수 — «htmx 단일» 잔존 문면 색출 반영)

| # | 파일 | 변경 앵커 |
|---|---|---|
| 1 | `workspace/design/2026-08-23-web-presentation-layer-spec.md` | :19(§1.1 목표 문면)·:41(D12→v2)·:84(§1.3㉠ 트리 v3.2 — houserules와 byte 동기) |
| 2 | `dddjango-web/skills/discipline-web-houserules/references/final.md` | :60(트리)·:93(골격 표 — motion.css는 coder 귀속이라 §4 표·§6 위임으로)·:98·:132-135(§4 표 foundation·static/css·static/js 행)·:154(§5 ⑤ WP)·:186(패밀리)·:193(handoff) |
| 3 | `dddjango-web/skills/discipline-web-houserules/references/undecidable-web.md` | :55(§6 base.html 입장 목록 — motion.css link 상시·motion.js script 조건·defer) |
| 4 | `dddjango-web/skills/discipline-web-houserules/SKILL.md` | :39(«vendored htmx 외 JS» 위반 목록) |
| 5 | `dddjango-web/commands/dddjango-web.md` | :9·:193(닫힌 목록)·:55(스키마)·:63(플래그 4종)·:107(ⓕ 문면)·:114(재동결 3종)·:120(관찰 기록 의무)·:121(플래그 설정)·:131·:132(입력 열거)·:140(Phase 2 준비 — 조건 설치)·:145(design_system 귀속에 motion.css)·:153(G2 ⓑ)·:179(트리비얼 1줄) |
| 6 | `dddjango-web/skills/architecture-web/references/final.md` | :22(§1 «htmx 유일»)·§8(:128-130 옆 «동적 표현 전수» 불릿) |
| 7 | `dddjango-web/skills/architecture-web/SKILL.md` | :22(«htmx 유일») |
| 8 | `dddjango-web/skills/implementation-ui/references/final.md` | :112(허용 속성에 data-motion)·:118-119(§5 JS 문면)·:141(토큰 범주에 모션 값)·모션 표기 절 신설 |
| 9 | `dddjango-web/skills/implementation-ui/SKILL.md` | :28(«vendored 단일 파일») |
| 10 | `dddjango-web/agents/design-architect-web.md` | 입력 절(+motion-notes)·행위 목록(동적 표현 전수 처분) |
| 11 | `dddjango-web/agents/design-review-web.md` | 입력 절(+motion-notes)·:31 ⓓ(대조 입력 지목) |
| 12 | `dddjango-web/agents/coder-web.md` | :53(D12 문면 — 화이트리스트 2종·motion.js 수정 금지) |
| 13 | `dddjango-web/agents/discipline-reviewer-web.md` | :52(D12 우회 형태에 motion.js 확장·해시 이탈) |
| 14 | `dddjango-web/assets/motion.js` | 신설 — §3.2 판형 |
| 15 | `dddjango-web/scripts/src/check_purity.py` | WP1 그룹 화이트리스트({htmx 변형}·{motion.js} 그룹별 ≤1 — R1-6) · WP2 예외를 `{% static 'js/htmx.min.js' %}`/`{% static 'js/motion.js' %}` 정확 매칭(CDN 구멍 동시 폐쇄 — R1-7) · WP3에 `hx-vals`/`hx-headers` `js:` 접두·`hx-trigger` 대괄호 조건식(R1-8) · WP 신설: motion.js 해시 대조(R1-4) |
| 16 | `dddjango-web/scripts/src/check_structure.py` | :190 부근 WS5 — htmx 개별 존재 검사(motion은 부재 허용·존재 시 WP가 검증) (R1-6·R2-9) |
| 17 | `dddjango-web/scripts/test/` 픽스처 | F22b/F22c 재편 + 신규 red/green(motion 공존·CDN 위장·js: 채널·해시 이탈·화면 keyframes 무접두) |
| 18 | `codex-dddjango-web/**` | references·undecidable byte 미러 · SKILL.md 의미 미러 · assets/scripts 사본 |

## 5. 검증

`scripts/test/run_fixtures.sh` green → `claude plugin validate dddjango-web --strict` → codex 미러 byte 대조 → `make verify`(verify-web).

## 6. 비변경 (선 긋기)

dddjango(백엔드) 무수정 · 러너 기능 확장 금지 · `.dc.html`·트리비얼에 관찰 의무 불소급 · htmx 설치 절차(curl) 불변 · `hx-swap` `transition:true` 금지.

## 7. 적대 리뷰 처분 대장 (35건 → 채택 수리 30 · 기각 3 · 반증 실패 확인 2군)

- **채택(주요)**: base.html 배선 소유(R3-1·R2-2 → #3·#8) · 관찰 주체 사용자 재배정(R2-1·R3-2 → §3.3-1) · 닫힌 목록(R2-3·R1-3 → #5) · 전달 문면(R2-4 → #5·#10·#11) · «htmx 유일» 전수 색출 13곳(R1-1·2·5·11·12, R2-5·11 → #1~#13) · WP 재구조 4갈래(R1-4·6·7·8, R3-3 → #15) · WS5(R1-6·R2-9 → #16) · 조건 설치(R3-5 → §3.2) · 소유 통일(R2-9 → §3.4) · FOUC/PRM CSS 단일 소유(R3-4·9 → §3.1) · one-shot/defer(R3-7·11 → §3.2) · swap/settle 수식어(R3-6 → §3.3-7) · 수치 칸(R3-8 → §3.3-1) · 발동 조건 재정의(R2-7) · 플래그 삼중 배선(R2-8) · 재동결 3종(R2-6) · G2 대조 기준(R2-10) · keyframes 절충(R1-9 → §3.1) · 토큰 경계(R1-10 → §3.1) · D12v2 닫힌 열거(R1-12) · transition:true 금지(R3-12).
- **기각**: 빈 motion.css 최초 골격(R3 — 소유 충돌(R2-9)이 더 커 coder 귀속으로 대체) · 브라우저 도구 요건(R3-2 대안 — 문답 판형 채택) · coder-web에 motion-notes 직접 전달(명세 단일 근거 원칙).
- **반증 실패 확인**: STATICFILES 서빙·collectstatic·G2 런서버 부재·MutationObserver 성능.
