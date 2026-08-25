# dddjango-web 모션 검증 결정론화 계획 (v2 — 계획 적대 리뷰 처분 반영)

- 작성: 2026-08-25 · v1 → 방향 적대 패널 4-lens(반증 51건) · v2 → 계획 적대 패널 3-lens
  (실행 가능성 15·봉합성 13·회귀 파급 15건 — blocker 2·major 다수 전건 반영, §4 처분 대장).
- 결함(닫을 대상): 실측 커버리지가 실행자(사용자/대행 에이전트) 판단에 있어, 대행 시
  모션(애니메이션·전환·hover) 미측정이 Phase 0(목표 원본)·G2(구현) 양쪽에서 발생.
- 원칙: 측정·검증 커버리지를 실행자에서 **산출물(스니펫 스키마·처분 표·정적 검사기)**로
  이관한다. 브라우저 런타임 표본에 기대지 않는다(방향 패널 실증 — 동기 표본은 IO 리빌
  비관찰·rAF 계열 전면 비관찰·cross-origin CSSOM 차단).

## §0 확정 결정 (2026-08-25 사용자)

| # | 결정 | 내용 |
|---|---|---|
| R1 | **B(Playwright 러너 스크립트) 폐기** | 구현측 검증은 정적 대조 검사기(W4)가 대체·목표측 대행은 재량 경로 문면(W6). 플러그인에 Node/브라우저 의존물을 동봉하지 않는다 |
| R2 | **실측 대행 재량 경로 공인(D13 개정)** | 1순위는 사용자 실측(현행). 세션 대행은 ⓐ실행 채널이 세션 재량으로 성립(직접 브라우저 자동화 도구 **또는 Agent 위임** — allowed-tools 무개정의 성립 근거) ⓑ사용자 명시 동의 ⓒ비인증 공개 페이지 확인 ⓓ한 실측 쌍은 같은 실행자·같은 창폭 — 4조건 하에서만 |

## §1 작업 항목

### W1 — motion-notes.md 기계가독 표 판형 (관찰 SSOT)

- 대상: `dddjango-web/commands/dddjango-web.md` :123(기록 판형) **+ :59·:124(플래그 의미론)**.
- 고정 칼럼 표(헤더 행 문자열 byte 고정 — W4 파서의 앵커):
  `| id | 요소 | 트리거 | 효과 | 재현 분류(예상) | 출처 |`
  - id: `m1…mN`(빌드 내 유일) · 트리거: `hover|focus|load|scroll|swap|pinned-관찰` ·
    효과: 전→후 값·duration·easing(측정 불가 값은 «근사» 병기 — 현행 규율 유지) ·
    재현 분류(예상): `CSS|러너|한계`(최종 확정은 명세 처분 표) · 출처: `실측|스캔|문답|요구|근사`.
  - **상태 행**(id 칼럼 `—`·전수성/수량 대조 **제외**): 모션 없음을 확인했으면 `(없음-확인)`
    행(출처 명기), 관찰 생략이면 `(미관찰)` 행+사유 — «없음-확인 vs 미검증» 구별.
  - `.dc.html`·자체 설계 경로: 사용자 모션 **요구**가 있으면 같은 표(출처=요구)로 기록.
    이에 맞춰 **:59·:124의 `has_motion_notes` 의미론을 «파일이 생성되면 경로 무관 true»로
    개정**(현행 «.dc.html이면 false»는 요구 기록 채널을 전달망에서 끊는다).

### W2 — 스니펫 v2 (assets/render_audit.js) — motion 인벤토리 축소판

- audit_version 1→2. 기존 축(텍스트·컬럼·pinned)·동기 실행 계약 불변. motion 섹션은
  **setTop(0) 직후, 텍스트 실측과 같은 단계**에서 동기 수집:
  - `transitions[]`: 가시 요소 중 **computed `transition-duration`/`transition-delay` 목록에
    0이 아닌 값 ≥1**인 것(주의 — `transition-property` 초기값은 `all`이라 술어로 쓸 수 없다).
    항목 `{key, property, duration, easing}`.
  - **요소 key 규약**: 텍스트 리프면 기존 `keyOf(text)`, 비텍스트 요소는
    `태그명.classList(정렬·최대 3).join('.')` — 결정론 시그니처.
  - `transitionRules[]` `{selector, transition}`: CSSOM 스타일 규칙 중 transition 선언 보유 —
    상태 클래스 게이트형(`.reveal.visible{transition:…}` 류)을 computed가 못 보는 사각 보완.
  - `keyframes[]`(@keyframes 이름)·`animationRules[]` `{selector, animation}`.
  - `hoverSelectors[]`·`focusSelectors[]`: selectorText에 `:hover`/`:focus` 포함 규칙 —
    **규칙 인벤토리까지만**(computed delta 재구성 주장 없음).
  - CSSOM 순회: `document.styleSheets` + `document.adoptedStyleSheets`, **CSSGroupingRule
    (@media·@supports) 재귀**(초기 은닉 판형 자체가 @media 안이다), 시트별 try/catch →
    `sheets: {total, readable, blocked[]}` 자기 신고.
  - `blind_spots[]`: 전역 시그니처(`window.gsap`·`window.anime` 등) + **DOM 흔적**
    (`[data-aos]`·`.aos-init`·`[data-scroll]` 류 — 전역 미노출 번들 보완) 감지 기록.
  - 캡: transitions 100·transitionRules 100·animationRules 50·keyframes 50·hover/focus 각
    100 — 초과 축은 `caps_hit[]`에 축명 기록.
  - 출력 이중화: 기존 copy/console.log/요약 반환 유지 + `window.__renderAudit = out` 저장.
    회수 방법의 구체 표기(2단 평가 등)는 **스니펫 헤더 주석에만** — 커맨드 문면은
    «대행 시 도구의 평가 채널로 회수(방법은 도구 재량)» 중립형(Codex 의미 미러 정합).
- getAnimations() 런타임 표본은 채택하지 않는다(§3).

### W3 — compare_render_audit.py v2 (하위 호환 + 커버리지 경고)

- `ACCEPTED_VERSIONS = {1, 2}`: v1 입력은 motion 축 스킵 + `[warn] v1 실측 — motion 축 미대조`
  (**v1↔v1 조합도 이 warn 1행이 추가된다** — exit·diff 판정은 불변). die 문면에
  `audit_version` 리터럴 유지(기존 S1 픽스처의 고정 문자열).
- `--validate`: v2에 motion 섹션 **필수**(부재·형식 위반 die), `--require-version 2` 옵션
  신설 — **신규 동결 경로는 v2 강제**(구버전 스니펫 재사용으로 결함이 재발하는 통로 차단),
  재사용 폴더의 기존 동결본만 v1 수용. 준-커버리지 경고: `blocked>0` → 부분성 warn ·
  `blind_spots≠[]` → 측정 밖 엔진 warn · `sheets.total==0` → **비개연 실측 warn**
  (손조립 최소 노력 경로 차단 — 문답 강등 자격에도 연동, W6). exit는 불변.
- 대조: motion 자동 조인 없음(CSS-in-JS 해시 명명 — 조인 키 부재). 요약 정보 행(양측 계수)
  +비대칭(한쪽 v1) warn만 — 판정 대조는 W4 소관.
- exit 판형 불변: 0=diff 0 / 1=미실행 / 2=diff ≥1 — **비차단·판단 자료**(backstop의 반송
  판형과 다르다 — 인용 주의).

### W4 — 명세 처분 표 판형 + 정적 검사기 `check_motion_spec.py` (신설 — 구현측 본체)

- 근거: 구현측은 폐쇄계(D12 — CSS 모션+`data-motion`뿐·전부 커밋 텍스트)라 브라우저 없이
  결정론 검증이 성립한다.
- 처분 표(설계 명세 내·고정 헤더 행 byte 고정):
  `| note id | 처분 | 분류 | 구현 좌표 | 값 | 근거 |`
  - 처분: `채택|기각|한계` · 분류: `css-hover|css-focus|css-transition|css-keyframes|러너|—` ·
    구현 좌표: css-\* = `파일경로 :: 셀렉터(또는 @keyframes 명)` / 러너 = `data-motion 토큰` ·
    값: `var(--duration-*)`·`var(--ease-*)` 토큰.
- 검사기(stdlib only) 입력 판별 3분기: **파일 부재** → exit 1(미실행 — 호출측이 조건화) /
  **표 헤더 미검출(레거시 산문 판형)** → `[warn] 레거시 산문 판형 — 모션 축 미검증(표 판형
  재기록 권장)` + exit 0(합법 재빌드를 차단하지 않는다) / **헤더 검출+판형 위반**(칼럼 수
  불일치 등) → exit 2 red.
- `--spec-only`(G1 승인 직후 — 호출 결선은 W6 :139): 판형 파스 + **전수성**(notes의 m\* id
  ↔ 처분 표 양방향·상태 행 제외) + «`(미관찰)`+처분 0행 → `[warn] 모션: 미검증(관찰 생략)`
  / `(없음-확인)`+0행 → green» 구별 + **`--audit <render-audit.json>` 옵션**: audit v2 모션
  인벤토리 계수 > 0인데 notes에 출처=`실측|스캔`인 m\* 행이 0이면 warn — **측정→기록 전사
  이음매의 계수 게이트**(조인 키 불요). red는 architect 반송 근거(G1 전 — G2와 지위 다름).
- full(G2): 채택 행의 구현 좌표 실재 — css-\*: 지정 파일에 셀렉터/@keyframes 존재+선언 값
  문자 포함 / 러너: 템플릿 `data-motion="토큰"`+base.html motion.js 로드 태그+초기 은닉 판형 /
  값 토큰이 tokens.css에 정의. **+역스윕**: web/ 트리의 `@keyframes` 명·`data-motion` 토큰
  전수가 처분 표 채택 행에 실재하는지(미실재 = 발명 발견 — 단방향 검사의 사각 봉합).
  지위: G2 배너 1급 의무 표기·**판단 자료(비차단)**.

### W5 — 목표측 동결 CSS 정적 스캔 확장

- 대상: `dddjango-web/commands/dddjango-web.md` :123(참조 HTML/URL 카피 절 ⓐ 채널).
- **URL 동결 경로 한정**: `<link rel="stylesheet">` href 전수를 페이지 URL 기준으로 해소해
  curl로 `design-ref/css/`에 동결 + **`@import`는 1단 재귀**. 실패·미해소는 이미지 실패와
  같은 판형으로 G0 배너 자기 신고. 정적 스캔 ⓐ를 동결 CSS 전체로 확장(`@keyframes`·
  `transition`·`:hover` grep → W1 표 초안 행·출처=스캔). 실측 v2의 `blocked[]` URL이 동결
  CSS 목록에 없는 경우 warn(차단 신고와 스캔 집합의 대응 대조).
  *왜*: curl은 cross-origin 제약이 없어 브라우저 CSSOM 차단을 우회한다.

### W6 — Coordinator 문면 개정 (재량 경로·게이트·결선)

- 대상: `dddjango-web/commands/dddjango-web.md` — :9/:196(닫힌 목록)·**:59**·**:62**·:117·
  :123·**:124**·**:139(Phase 1)**·:156·:182.
- :123 실측 실행자 규정(R2 4조건): ⓒ 비인증 확인은 실측 JSON `url` 대조(**리다이렉트 감지**)
  + texts 표본의 로그인 어휘 휴리스틱(보조 — 같은 URL 로그인 폼은 url 대조로 못 잡는다).
  대행이어도 **스니펫 전문 실행**(요약·발췌 실행 금지). 신규 동결은
  `--validate --require-version 2`.
- **생략 게이트**: 실측 생략의 합법 사유 enum(원본 열람 불가·인증 페이지·대행 채널/동의
  부재) — 그 외 사유는 배너 재질문. :117 재사용 질문에 **«실측 생략 이력 폴더 → 재실측
  재질문»** 분기 추가(생략+사유 폴더가 영구 침묵하는 통로 차단).
- **문답 강등 조건부**: v2 실측 성공 ∧ `blocked=0` ∧ `blind_spots=[]` ∧ `sheets.total≥1`
  일 때만 문답을 «인벤토리 확인 문답»으로 축소하되, **스크롤 리빌·교체 전환 2문항은 강등
  후에도 상시 유지**(측정이 구조적으로 못 보는 클래스 — 인벤토리에 없는 축의 유일 채널).
- :117 재사용: 동결본 v1 → «v2 업그레이드 재실측» 선택지(거절 시 motion 축 미대조 고지) ·
  산문 motion-notes → «표 판형 재기록» 선택지 · 실측 생략 이력 → 재실측 재질문.
- **:139(G1 승인 직후)**: 계약 절단과 같은 시점에 `check_motion_spec --spec-only`(+동결
  실측 있으면 `--audit`) 실행 — red는 architect 반송(호출 결선 — 죽은 검사기 방지).
- :156 G2: **`has_motion_notes`이면** full 실행 의무(false면 «해당 없음(관찰 채널 부재)»
  1줄 — 상시 오발화 방지)·배너 1급 표기·compare 커버리지 warn 표면화. 육안 모션 대조 기준
  문구를 «motion-notes의 채택 항목» → **«명세 처분 표의 채택 행»**으로 교체(채택 개념의
  이중 출처 방지). **실측 쌍 대칭**: 목표측을 대행이 실측한 빌드는 G2 구현측도 같은 대행
  (사용자가 runserver를 띄우고 대행이 측정하는 하이브리드 허용·목표 JSON viewport 폭 재현)
  — 대행 불가 상황(세션 사멸 등)이면 사용자 실측+compare 비대칭 warn 수용을 명기.
- :182 트리비얼: 모션 토큰·duration 교체 시 완료 보고에 «산출물 폴더 처분 표와 어긋날 수
  있음» 고지 1줄 의무.
- **:62**: `g2_visual`에 motion-spec 결과(red 수락 여부·사유) 합류 기록(red 무시의 증적).
- :9/:196 닫힌 목록: render-audit 항목을 «기계 관찰 산출물(실행자 규정 :123 — 너는 값을
  쓰지 않는다)»로 재정의.

### W7 — 에이전트·스킬 문면 개정 (6문면 확정 명단)

1. `commands/dddjango-web.md` — W1·W5·W6.
2. `agents/design-architect-web.md`: :21(입력 판형)·:40(처분을 W4 표 판형으로 — **헤더 행
   byte 고정 의무** + «css-\* 좌표의 셀렉터 명명은 설계 확정(형상 불서술 원칙의 명시 예외 —
   모션 좌표 한정)» 1줄)·:69(수량 대조식 — **«notes의 모션 id(m\*) 행 수 = 처분 표 행 수»**
   (상태 행 제외 명시)).
3. `agents/design-review-web.md`: :13(입력 판형)·:31 ⓓ(표 기반 전수 대조).
4. `skills/architecture-web/references/final.md` §8(동적 표현 전수 절 — 표 판형 명시).
5. `skills/implementation-ui/references/final.md` §7: «처분 표가 지정한 **셀렉터**·keyframes
   명·`data-motion` 토큰을 그대로 쓴다 — 발명 금지» 1줄(조인 키 규약 소유자).
6. `agents/discipline-reviewer-web.md`: :14 분업 지도 1줄 — «처분 좌표·값 실재는
   check_motion_spec 소관(재검 금지) — 너는 처분의 의미 타당성만».
- `coder-web.md`는 **개정 불요**(모션 소비는 implementation-ui §7 로드 경유 — 실물 확인:
  자체 문면에 motion-notes·처분 언급 없음).

### W8 — 스펙 결정 대장 D13 개정 (사용자 확정 완료)

- 대상: `workspace/design/2026-08-23-web-presentation-layer-spec.md` D13 **행 교체**(대장
  판형 — 상태 칸 버전 표기로 이력 보존). 버전은 **v2**(D13은 08-24 신설 단일판 — v1→v2).
- **결정 (사용자 · v2 2026-08-25)**: 실측 주체 사용자 1순위+재량 대행 4조건(R2) · 스니펫
  v2(모션 인벤토리·시트/blind_spots 자기 신고·신규 동결 v2 강제) · 처분 표+
  `check_motion_spec`(--spec-only G1 반송·full G2 판단 자료) 채널 신설 · 기존 동결본 v1
  하위 호환.

### W9 — 픽스처·하네스·미러

- `scripts/test/fixtures_audit.sh` 확장(negative↔positive-control 짝 규율):
  V2(v2 정상 green) ↔ S2(v2 motion 부재 → validate die) · RV(--require-version 2에 v1 →
  die) · W1v(v1 수용+warn 문면) · Wb(blocked>0 warn) · Ws(blind_spots warn) ·
  Wz(sheets.total=0 비개연 warn) · MIX(v1 target+v2 impl warn) · DET(v2 표본 2회 byte 동일).
- 신설 `scripts/test/fixtures_motion_spec.sh`(**글롭 규약 이름으로 배치 — run_fixtures.sh는
  `fixtures_*.sh` 자동 수집이라 러너 무수정**): 전수성 위반 red · 좌표 부재 red · 값 불일치
  red · **발명(역스윕) red** · 판형 위반 red · 레거시 산문 → warn+exit 0 · `(미관찰)`+0행 →
  미검증 warn · `--audit` 계수 게이트 warn ↔ green 짝 3형(css-hover·css-keyframes·러너 —
  러너형은 data-motion+로드 태그+은닉 판형 포함 합성 web/ 트리) · `--spec-only` 왕복.
- `codex-dddjango-web/` 미러: **scripts와 `assets/`(render_audit.js·motion.js) 모두 byte
  동일** — Codex Coordinator가 `${SKILL_DIR}/assets/render_audit.js`를 자체 참조하므로
  assets 누락 시 Codex 빌드 전체가 v1로 회귀한다(계획 리뷰 blocker). 문면(commands 상당
  SKILL.md·agents·skills)은 의미 미러 — 대행 문구는 중립형(플랫폼 도구명 없음).
- `Makefile` verify-web에 byte 대조 추가: `dddjango-web/{scripts,assets}` ↔ codex 대응
  (`diff -rq`·`__pycache__` 제외).
- `backstop.py`·`check_purity.py` 무변경(검사 대상은 소비 프로젝트 web/뿐).

## §2 인수 기준 (런북)

1. `make verify` 전 그룹 green — 신규 픽스처 전수(negative가 실제 red를 내는 것을 짝으로
   확인) + verify-web의 byte 대조.
2. **실물 실증**: 로컬 합성 페이지(@keyframes·transition·상태 클래스 transition·:hover·
   **2-origin 서빙**(`python -m http.server` 2포트 — cross-origin 시트 차단 재현)·rAF 전역
   스텁·`[data-motion]`+IO 리빌 판형)에서 스니펫 v2를 실제 브라우저로 실행 — 실행자는
   **세션(브라우저 자동화 도구 가용 시)** 또는 사용자. 확인 항목: 각 축 산출·blocked 기록·
   blind_spots 감지·caps·`window.__renderAudit` 회수. 결과를 인수 기록에 남긴다.
3. compare 판형 3조합: v1↔v1(**exit·diff 판정 불변 + v1 고지 warn 1행**)·v1↔v2(warn)·
   v2↔v2(정보 행+커버리지 warn).
4. `check_motion_spec`: 합성 트리로 red 5형·warn 3형·green 3형·`--spec-only`/`--audit` 왕복.
5. 미러 byte diff 0(scripts+assets) + 문면 개정 6문면+D13 전수 반영 대조.
6. 조감도 `workspace/design/ontology-adoption-map.html`에 이번 개정 이력 행 1건 추가.

## §3 비범위 · 수용 잔여 위험

**비범위(후속 별건)**: getAnimations 런타임 표본·hover computed delta 재구성(실증 후 재론) ·
러너 스크립트 일체(R1) · G2 서버 기동 자동화 · Codex 측 대행 도구 사다리 명세(중립 문구로
흡수) · 릴리즈(`make release-web` — 사용자 소관·완료 보고에 안내만).

**수용 잔여 위험(명시 — 계획이 닫지 않는 것)**:
- 실측 **전면 생략**은 합법 사유 enum 안에서 여전히 가능(사유 표면화+재빌드 재질문까지가
  방어) — 파일이 없으면 스키마 게이트는 무발동.
- **정교한 손조립**(개연성 하한·계수 게이트를 통과하도록 위조된 JSON)은 기계로 못 막는다 —
  «전문 실행» 문면+커버리지 warn 대면까지가 방어.
- **전역·DOM 흔적 모두 없는 rAF 번들**은 blind_spots가 못 잡는다 — 상시 유지 2문항(스크롤
  리빌·교체 전환)이 폴백.
- 전사 이음매 게이트는 **계수 대조**다 — 계수가 맞고 내용이 틀린 전사는 못 잡는다.
- 대행 목표 실측 후 대행 불가 상황의 G2는 **비대칭 쌍 warn 수용**으로 퇴화한다.

## §4 계획 리뷰 처분 대장 (추적성)

| 패널 | 반영 | 요지 |
|---|---|---|
| 실행#1(blocker) | W2 | transitions 술어를 duration/delay 비-0으로 교체(`transition-property` 초기값 all) |
| 실행#2·회귀#2 | W6 :139 | --spec-only 호출 결선(G1 직후·red 반송) |
| 실행#3·회귀#8 | W1 | :59·:124 has_motion_notes 의미론 개정 |
| 실행#4·회귀#1(blocker) | W9 | assets byte 미러+Makefile 대조 범위 확장 |
| 실행#5 | W4 | 표 앵커·판형 위반 red·파스 3분기 명세 |
| 실행#6 | W7 | 셀렉터 소유권(설계 확정 예외 1줄)+§7 셀렉터 포함 |
| 실행#7 | W2 | 키 규약·수집 시점·캡·@media 재귀 명기 |
| 실행#8·봉합 매트릭스 | §0 R2ⓐ | Agent 위임 포함 중립 채널(allowed-tools 무개정 성립 근거) |
| 실행#9 | W3·W4 | «compare 판형 exit(비차단)» 인용 정정 |
| 실행#10·회귀#9 | §2-3 | v1↔v1 warn 1행 명시·die 문면 리터럴 유지 |
| 실행#11·회귀#15 | W8 | D13 버전 v2·행 교체 |
| 실행#12·회귀#13 | W9 | 글롭 배치(러너 무수정) |
| 실행#13 | W6 | 로그인 감지 주장 축소(리다이렉트+어휘 휴리스틱 보조) |
| 실행#14·봉합#9 | W5 | URL 한정·@import 1단·blocked↔동결 대응 warn |
| 실행#15 | W3·W6 | --require-version 2(신규 동결 v2 강제) |
| 봉합#1 | W6 | 생략 사유 enum+생략 이력 재질문 |
| 봉합#2 | W3·W6 | sheets.total=0 비개연 warn+강등 자격 연동 |
| 봉합#3 | W4 | --audit 계수 게이트(전사 이음매) |
| 봉합#4 | W6·W2 | 강등 후 상시 2문항+DOM 흔적 시그니처 |
| 봉합#5·회귀#5 | W6 :156 | 실측 쌍 대칭 — 하이브리드 허용·비대칭 warn 수용 명기 |
| 봉합#6 | W4·W9 | 역스윕(발명 감지)+픽스처 |
| 봉합#7·회귀#3 | W4·W6 :117 | 레거시 산문 warn 강등+재기록 선택지 |
| 봉합#8 | W7 | 6문면 명단 확정(discipline-reviewer 포함·coder-web 불요+근거) |
| 봉합#10 | W2 | transitionRules[] 축 추가 |
| 봉합#11 | W6 :62 | red 수락 증적(g2_visual 합류) |
| 봉합#13 | §3 | 수용 잔여 위험 명시 절 신설 |
| 회귀#4 | W6 :156 | full 발동 has_motion_notes 조건화 |
| 회귀#6 | W1·W7 | 상태 행 id 제외·등식 m\* 기준 |
| 회귀#7 | W6 :156 | «채택» 출처 단일화(처분 표) |
| 회귀#10 | W7 | discipline-reviewer :14 분업 1줄 |
| 회귀#11 | W2 | 회수 문구 중립화(구체는 스니펫 주석) |
| 회귀#12 | §2-2 | 실증 절차 특정(2-origin·실행자) |
| 회귀#14 | §2-6 | 조감도 이력 행 |
