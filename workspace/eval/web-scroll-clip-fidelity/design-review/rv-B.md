# 적대 검토 B — 집행 경로 («누가·언제·무엇을 근거로 실행하는가»)

대상: `workspace/design/2026-09-15-web-clip-fidelity.md` v1
검토자: 독립 적대 검토 B. 설계를 고치지 않고 지적만 한다.
실증 근거: A8 실빌드 `/Users/hyun/Desktop/spring_dream_server/.dddjango-web/20260912-1640-web-related-persons/`

BLOCKER 5 · MAJOR 8 · MINOR 3

---

## [BLOCKER] 구현측 렌더 실측은 초기 페이지 1장뿐 — 결함 컨테이너가 DOM에 없어 `check_clip_audit`은 구조적으로 «발견 0»을 낸다

**구멍**
설계 §2.2의 대상 열거는 `querySelectorAll(기반 셀렉터)` — **측정 시점의 DOM**에만 발화한다. G2의 구현측 실측은 빌드당 `render-audit-impl.json` **한 장**이고, 그것은 초기 URL의 초기 상태다. 이번 결함의 `.rpe-scroll`은 HTMX 오버레이 다이얼로그 안에 있어 초기 렌더 DOM에 **없다**. 따라서 배포 후 A8이 G2를 다시 돌려도 `check_clip_audit`은 후보 0 → `findings: []` → exit 0 → «발견 0» green을 낸다. 수리 3은 이번 결함을 **잡지 못한다**.

설계는 이 사실을 §3.1에서 이미 알고 있으면서 시안측에만 적용했다:

> `workspace/design/2026-09-15-web-clip-fidelity.md:110-112`
> 「**브라우저가 아니라 동결 dc HTML에서 뽑는다.** 결정적 이유: 이번 결함의 컨테이너는 **다이얼로그 안**이라 초기 렌더에 존재하지 않는다 — 렌더 실측은 초기 페이지에서 돌므로 그 컨테이너를 영영 못 본다.」

같은 문장이 구현측에도 그대로 성립한다. 설계는 그 대칭을 보지 못했고, §6 브리프는 그 위에서 «수리 3 단독 — 이번 결함: 잡는다»를 사용자에게 올린다.

**근거 (A8 실측 — 추측 아님)**
- `20260912-1640-web-related-persons/render-audit-impl.json` · `url = http://127.0.0.1:8891/related-persons/` (목록 페이지) · `texts` 13건 전부 목록 화면 텍스트(`관계인`·`관계인 등록하기`·`김서연`·`등록한 사람 4명`…). 다이얼로그 텍스트는 **0건**. `partial: false`·`textsTruncated: false` — 잘린 게 아니라 애초에 없다.
- 결함 컨테이너의 실제 자리: `spring_dream_server/web/related_persons/related_person_editor/section/related_person_editor_step.html:56` — `<div class="rpe-scroll" data-cm-dialog-scroll="true">`. section fragment라 오버레이를 열어야 DOM에 붙는다.
- `render-audit-impl.json`에 `rp-dialog`·`input-field` 문자열이 있으나 전부 `motion.focusSelectors`/`hoverSelectors`(CSSOM 셀렉터 텍스트)이며 DOM 증거가 아니다.
- `design-input.json`의 case는 **12건**(`related/edit-step1`·`related/register-step1`·`related/form-step2-*` 포함)인데 실측은 그중 1건(목록)만 덮는다. 상태 축 커버리지 1/12이고 결함은 나머지 11 중에 있다.
- 쌍 대칭 규정이 상태 측정을 **적극적으로 막는다**: `dddjango-web/commands/dddjango-web.md:187` 「목표 실측과 같은 실행자·같은 브라우저·같은 창폭」 + `compare_render_audit.py`가 texts key로 조인하므로, 구현측만 다이얼로그를 열면 목표측과 어긋나 대조가 diff 폭주한다.

**수정 방향**
① 판정 입력을 «초기 페이지 실측 1장»에서 떼어낸다 — `design-input.json`의 case(상태) 단위로 돌거나, 이미 다이얼로그를 여는 기존 채널(`scripts/observe_interactions.mjs` — 조작 상태 수집 드라이버)에 clip 수집을 얹는다. 구현측에는 이 드라이버가 안 돌고 있으므로 «구현측 조작 상태 실측»이 새 전제다. ② 또는 브라우저를 버리고 **구현 템플릿+CSS 정적 스윕**으로 간다 — 구현측에도 `data-cm-dialog-scroll="true"`가 그대로 살아 있고(`related_person_editor_step.html:56`), `.rpe-scroll { overflow-y: auto }`와 `padding` 부재는 `related_persons.css:393`에서 텍스트로 읽힌다. 수리 2의 추출 규칙을 구현측에 한 번 더 적용하면 상태 의존이 사라진다. ③ 어느 쪽이든 «측정 못 한 상태 k건»을 발견 0과 구별해 보고하는 커버리지 필드가 필수다.

---

## [BLOCKER] 단측 검사인데 목표측 플래그 `has_render_audit`에 매달려 있다 — 렌더 실측 합법 생략 빌드에서 통째로 소멸하고 «해당 없음» 문장조차 없다

**구멍**
`check_clip_audit`은 설계 스스로 «단측 검사다(목표↔구현 조인 키가 없다)»(§2.3)라고 규정한다. 그런데 그 유일한 입력 `render-audit-impl.json`을 만드는 G2 절은 **목표측 플래그**로 잠겨 있다. 목표(시안) 원본을 못 열었다는 이유로 **로컬 runserver에서 얼마든지 측정 가능한 구현측 검사**가 통째로 사라진다. 그리고 이 경우 배너에 무엇을 적어야 하는지 설계에 없다 — 모션 축에는 있는 «해당 없음» 문장이 clip 축에는 없으므로 결과는 **무출력**, 즉 조용한 통과다.

**근거**
- `dddjango-web/commands/dddjango-web.md:187` 「**렌더 실측 기계 대조(`has_render_audit`이면)**: 구현 페이지(runserver)에서 같은 스니펫을 … 실행해 … `render-audit-impl.json`로 저장하면, 네가 `compare_render_audit.py`를 실행한다」 — 구현측 측정 자체가 이 조건절 안에 있다.
- 생략이 합법인 사유 enum은 **전부 목표측 사정**이다: `dddjango-web/commands/dddjango-web.md:143` 「**실측 생략이 합법인 사유는 enum이다** — 원본 열람 불가 · 필요한 인증 상태 접근 불가 · 브라우저 채널 부재」. 앞 둘은 구현측 측정 가능성과 무관하다.
- 같은 줄: 「생략이 확정되면 **파일을 만들지 않고**(스텁 금지 …)」 → `has_render_audit=false` → G2 구현측 측정 없음 → clip 검사 입력 없음.
- 모션 축에는 부재 시 문장이 명시돼 있다: `dddjango-web/commands/dddjango-web.md:187` 「`has_motion_notes`가 false면 «모션 처분 대조: 해당 없음(관찰 채널 부재)» 1줄」. 설계 §2.3은 «배너 1급 의무 표기»만 적고 대응 문장을 정의하지 않았다.
- 설계 §5는 위험을 R1(v3 버전 올림)·R2(후보 폭발)·R3(수리 2·3 중첩)만 다루고 이 경로를 언급하지 않는다.

**수정 방향**
clip 판정의 발동 조건을 `has_render_audit`에서 **분리**한다 — 구현측은 항상 측정 가능(runserver)이므로 별도 플래그·별도 실행 줄로 세운다. 부재/실패 시 배너 문장을 enum으로 못 박는다(«절단 판정: 미실행 + 사유» / «절단 판정: 해당 없음(구현 렌더 접근 불가)»), 조용한 무출력을 금지한다.

---

## [BLOCKER] 새 산출물에 build-state 플래그도, 구버전 폴더 «신규 동결» 질문 합류도 없다 — 재사용 폴더(= A8 최종 시험 경로)에서 수리 2 사슬이 통째로 불발한다

**구멍**
`motion-notes.md`·`render-audit.json`은 각각 build-state 플래그(`has_motion_notes`·`has_render_audit`)를 갖고, 그 플래그가 ⓐ 역할 전달 ⓑ 검사 발동 ⓒ **구버전 폴더 재사용 시 «신규 동결» 질문 합류**를 모두 건다. `clip-containers.md`에는 셋 다 없다. §4의 규범 편집표에 `build-state.json` 스키마 행이 없고, Phase 0 step 4의 채널 열거도 손대지 않는다.

결과: 이 배포 **이전에 만들어진 모든 폴더**(A8 포함)를 ⓐ 재사용으로 열면, Coordinator는 「이 폴더에 없던 채널 산출물」 질문에서 clip 채널을 묻지 않는다 → `clip-containers.md` 미생성 → 명세에 처분 표 없음 → G2의 `check_clip_spec.py <design-spec.md> <clip-containers.md> <web-root>`는 파일 부재로 exit 1(미실행) 또는 헤더 미검출 `[warn]` exit 0. **어느 쪽도 red가 아니다.** 「배포 후 A8 세션이 스스로 잡는지가 최종 시험」이라는 진단의 전제가 이 구멍 하나로 무너진다.

**근거**
- `dddjango-web/commands/dddjango-web.md:130` 「**기존 폴더에 아직 없는 채널 산출물(구버전 빌드라 `motion-notes.md`·`render-audit.json`이 애초에 없던 폴더)은 «재동결»이 아니라 «신규 동결» 선택지로 같은 질문에 합류**시킨다(플러그인 개정으로 생긴 채널이 재사용 경로에서 조용히 불발되는 것을 막는다 …)」 — 열거가 2종으로 고정돼 있다. 같은 열거가 수정 모드에도 복제돼 있다(`:206`).
- `dddjango-web/commands/dddjango-web.md:69-70` — `has_motion_notes`·`has_render_audit`의 build-state 계약. 「복원 시 … 기존 파일에 `has_render_audit` 키가 없으면 false로 읽는다」(`:130`)까지 있다.
- 설계 §4 표(`:148-158`)에 `build-state.json` 행 없음. §3.1은 「Coordinator가 `motion-notes.md`처럼 architect에게 전달」만 적고 플래그·재사용 질문을 다루지 않는다.
- A8 폴더는 정의상 재사용 폴더다(`20260912-1640-web-related-persons/` — 이미 `_history`·완료 산출물 보유).

**수정 방향**
`has_clip_containers`(또는 동등한 상태 키)를 build-state 스키마에 넣고, Phase 0 step 4·수정 모드 step 1의 채널 열거 2곳에 `clip-containers.md`를 더한다. 「구판형 산출물 업그레이드 재기록」 선택지에도 합류시킨다.

---

## [BLOCKER] `check_clip_spec.py --spec-only`의 실행 지점이 §4 규범 편집에 없다 — architect 반송 경로가 배선되지 않는다

**구멍**
설계 §3.3은 `--spec-only`를 «G1 직후 … red는 architect 반송 근거»로 규정한다. 그런데 §4의 Coordinator 편집 항목은 **G2만** 적는다:

> `workspace/design/2026-09-15-web-clip-fidelity.md:150`
> 「Phase 0 step 5에 `extract_clip_containers.py` 실행 · 입력 전달 계약에 `clip-containers.md` · **G2에** `check_clip_audit.py`·`check_clip_spec.py` 실행과 배너 표기 · 렌더 실측 `--require-version 3`」

「G1 직후」에 해당하는 Coordinator 절은 Phase 1 step 6(`commands/dddjango-web.md:168`)인데, 그 절을 편집하라는 지시가 §4에 없다. 규범 편집표가 계획서의 입력이 되는 저장소 관례상, 이 누락은 그대로 «아무도 안 도는 검사기»가 된다 — 이 플러그인의 전과(前科)와 정확히 같은 형태다.

**근거**
- `dddjango-web/commands/dddjango-web.md:168` — 모션 선례는 이 절에 명시적으로 박혀 있다: 「**같은 시점 — 모션 처분 표 기계 점검**(`has_motion_notes`이면): `python … check_motion_spec.py --spec-only <설계 명세> <산출물 폴더>/motion-notes.md` … **FINDING(전수성 위반·판형 위반)은 architect 반송 근거다**(G2의 판단-자료 지위와 다르다 …)」.
- 설계 §4에는 그 자리에 대응하는 편집이 없다.

**부수 지적**: §3.3·§6이 「G1 직후」를 「G1(설계)에서 잡는다」로 표기하는데, `commands:168`은 **G1 승인 직후**(사용자가 이미 배너를 승인한 뒤)다. 즉 사용자는 빈칸 있는 처분 표를 승인한 상태에서 반송이 일어난다. 브리프 §6의 「잡는 시점: G1(설계)」은 이 점에서 과장이다.

**수정 방향**
§4 표의 Coordinator 행에 «Phase 1 step 6에 `check_clip_spec.py --spec-only` 실행 + FINDING=architect 반송 + `[warn]`=배너 표면화»를 명시 추가한다. 발동 조건(`clip-containers.md` 존재 / 플래그)도 함께 적는다.

---

## [BLOCKER] 발견 ≥1(exit 2)의 처분 규칙이 없고 마무리 백스톱도 이 축을 안 막는다 — 결함을 알고도 빌드가 «완료»로 닫힌다

**구멍**
설계 §2.3은 지위를 「판단 자료(비차단)·배너 1급 의무 표기」로만 정하고, **exit 2일 때 무엇이 일어나는지 아무 규칙도 두지 않는다**. 비교 대상인 `compare_render_audit`·`check_motion_spec`에는 그 규칙이 명문으로 있다. 게다가 clip 판정은 단측이라 «명세 위반인가»를 물을 상대가 없다 — 설계가 규칙을 안 주면 판정 결과를 처분할 근거 자체가 없고, 배너에서 «발견 3건» 한 줄로 수락되면 그대로 닫힌다.

마무리 그물도 없다. `backstop.py`는 WS/WI/WN/WP 4패밀리와 `check_design_evidence`(inputs·visual)만 인프로세스로 돈다 — `compare_render_audit`·`check_motion_spec`을 부르지 않고, 설계 §4 표에도 `backstop.py` 행이 없다.

**근거**
- `dddjango-web/commands/dddjango-web.md:187`(모션) 「발견은 위 diff와 같이 구체적 이탈 결정 범위를 대조한다(**명세 위반/미결정은 반송**, 승인된 이탈만 사유와 함께 `g2_visual`에 기록)」 / (실측) 「명세 위반·미결정 이탈을 발견하면 `implementation_visual=failed`로 기록해 수정/설계로 반송하고, 재확인 전 G2 승인으로 넘기지 않는다」.
- `dddjango-web/scripts/backstop.py:249-256` — 실행 패밀리는 `run_structure`/`run_imports`/`run_naming`/`run_purity`뿐. `:294-307` — design 축은 `validate_inputs`/`validate_visual`뿐.
- `dddjango-web/commands/dddjango-web.md:191` Phase 3 마무리도 같은 `backstop.py` 재실행이 전부다.
- 설계 §4 표(`:148-158`)에 `backstop.py`·`check_design_evidence.py` 행 없음.

**수정 방향**
exit 2의 처분을 명문화한다 — 최소한 「발견 행마다 ⓐ 명세 처분 표의 결정 범위 안 / ⓑ 승인된 이탈 / ⓒ 미결정 → ⓒ는 `implementation_visual=failed`·반송」의 3분기와 `g2_visual` 기록 의무. 닫기 그물이 필요하면 `check_design_evidence`의 visual 계약에 «clip 판정 미실행/미처분» 항목을 얹어 마무리 backstop이 blocker를 내게 한다(현재 유일하게 «완료»를 막는 자리다).

---

## [MAJOR] 재동결 폐기·재생성 집합에 `clip-containers.md`가 없다 — stale 좌표표로 false green

**구멍**
재동결은 `design-ref/`를 전량 폐기·재수집한다. `clip-containers.md`는 그 dc HTML에서 기계 추출한 **파생물**이므로 함께 폐기·재생성돼야 하는데, 설계는 재동결을 한 글자도 다루지 않는다. 결과: 새 시안으로 재동결한 뒤에도 옛 `clip-containers.md`가 남고, 명세 처분 표는 **존재하지 않는 컨테이너**를 전수 처분한 상태로 `check_clip_spec` 양방향 검사를 통과한다.

**근거**
- `dddjango-web/scripts/refreeze.py:32-37` `FIXED_DISCARD_FILES = ('source-manifest.json', 'design-tokens.json', 'asset-manifest.json', 'screen-meta.json', 'render-audit.json', 'design-input.json', 'coverage-review.md', 'scope.md', 'refreeze-diff.json')` / `FIXED_DISCARD_TREES = ('design-ref',)` — clip 없음.
- `refreeze.py:39-40` `REQUIRED_STAGING` — `check`의 완전성 판정 목록에도 없다.
- `refreeze.py:428-429` — `render-audit.json`은 journal 플래그로 staging 재수집을 강제하는데, clip에는 대응물이 없다.
- 설계 §5 R1은 A8의 진행 중 재동결(`_refreeze-20260915-200029`)을 인지하면서도 **v3 버전 축만** 논한다.
- 참고: `motion-notes.md`도 `FIXED_DISCARD_FILES`에 없다 — 기존 관례가 «파생물 전부 폐기»가 아니므로 설계가 명시하지 않으면 자동으로 되지 않는다.

**수정 방향**
`FIXED_DISCARD_FILES`·`REQUIRED_STAGING`에 `clip-containers.md` 추가 여부를 §4에서 명시 결정하고, 재동결 계약 픽스처(`Makefile:110` 「재동결 계약(유보·잔존·경로 치환 불변식)」)에 회귀를 얹는다.

---

## [MAJOR] «배너 1급 의무 표기»가 어느 배너의 어떤 문장인지 설계에 없다 — 기존 판형에는 축마다 문장이 고정돼 있다

**구멍**
설계 §2.3은 「배너 1급 의무 표기」라고만 쓴다. 기존 판형은 그렇지 않다 — **어느 배너**인지와 **문장 자체**(수행/미수행/해당 없음 3분기)를 리터럴로 못 박아 둔다. 문장이 없으면 LLM Coordinator가 표기를 생략하거나 임의 표현으로 적고, grep·회귀가 불가능해진다.

**근거** — 기존 3축의 실제 문장:
- G0 배너: `dddjango-web/commands/dddjango-web.md:143` 「**G0 배너에 «렌더 실측: 미수행 + 사유»로 표면화한다**(조용한 생략 금지)」
- G2 배너: `:187` 「**결과는 G2 배너 1급 항목으로 의무 표기한다** — 수행 시 «실측 대조: diff N건 + 축별 요약» / 미수행 시 «실측 대조: 미수행 + 사유»(모드 판별·디자인 출처와 같은 항상-표시 급 — 미검증 상태로 제시한다)」
- G2 배너(모션): `:187` 「`has_motion_notes`가 false면 «모션 처분 대조: 해당 없음(관찰 채널 부재)» 1줄」
- Phase 3 종료 보고: `:193` 「실행한 검증만 보고한다(… **렌더 실측 기계 대조 결과[수행했으면 — diff 요약]** …)」 — 종료 보고에도 축별 항목이 열거된다.

설계는 이 중 어느 것도 지정하지 않았고, G0(추출 실패 시)·G1(`--spec-only` 결과)·종료 보고의 표기 의무는 아예 언급이 없다.

**수정 방향**
4개 배너(G0·G1·G2·종료 보고)별로 문장 리터럴을 §2.3/§3.3에 못 박는다 — 최소 G2의 수행/미수행/해당 없음 3문장과 G1의 FINDING/[warn] 표기.

---

## [MAJOR] R1의 «v2 → 미실행 보고»가 exit enum·픽스처 어디에도 내려오지 않았고, 구현측 JSON의 버전은 G2에서 아무도 강제하지 않는다

**구멍**
§5 R1은 「«v2 — clip 블록 없음»으로 **미실행 보고**(통과 아님)를 내야 한다. 조용한 green 금지」라고 요구만 하고, ① `check_clip_audit.py`의 exit 계약(§2.3의 `1`=사용법·스키마)에 「clip 블록 부재 = 스키마 오류」를 묶지 않았고 ② §2.4의 픽스처 목록(negative↔positive 짝 + 결정론)에 «v2 입력 → exit 1» 케이스를 넣지 않았다. 규범·검사기·시험 셋 중 어디에도 R1이 없다.

더 큰 문제는 R1이 잘못된 경로를 걱정한다는 점이다. 구현측 JSON은 G2에서 **그 세션의 플러그인 스니펫으로 새로 측정**하므로 배포 후엔 v3가 나온다. 진짜 v2 유입 경로는 **설치본 스큐**(사용자 `/plugin` 갱신 지연 — 이 저장소의 상습 상태)와 캐시된 산출 재사용이고, 그 경로를 막을 검사가 없다. `--require-version`은 Phase 0의 `--validate`에서만 쓰이고 G2 대조 경로에는 없으며, 버전 불일치는 **warn**이다.

**근거**
- `dddjango-web/commands/dddjango-web.md:143` — `--require-version 2`는 목표측 **동결 직후 validate**에만 걸린다. `:187`의 G2 대조는 `compare_render_audit.py <target> <impl>` 2인자 호출로 `--validate`를 쓰지 않는다.
- `dddjango-web/scripts/compare_render_audit.py:205-207` — 「`if tver != iver: warns.append(f"실측 버전 불일치 target=v{tver} impl=v{iver} — motion 축 미대조")`」 → **warn일 뿐 차단하지 않는다**.
- `compare_render_audit.py:43` `ACCEPTED_VERSIONS = {1, 2}` — 설계 §2.3대로 3을 더하면 v2 impl도 계속 합법 입력이다.

**수정 방향**
`check_clip_audit.py`가 입력의 `audit_version`과 `clip` 블록 유무를 **명시 판정**해 exit 1 + 고정 문장(«clip 블록 없음 — v{n} 산출, 재실측 필요»)을 내게 하고, §2.4 픽스처에 그 케이스를 넣는다. G2 구현측 저장 직후 `--validate --require-version 3`를 1회 돌리는 것도 §4에 넣을지 결정한다(목표측 동결 선례와 동형).

---

## [MAJOR] 역할 파일의 «입력» 절과 자기 점검이 편집 대상에서 빠졌다 — architect는 clip 축을 받을 계약도, 수량 대조 항목도 없다

**구멍**
§4는 `design-architect-web.md`에 「클리핑 컨테이너 전수 처분 의무 + 표 판형」, `design-review-web.md`에 「처분 표 전수성 리뷰 항목」만 준다. 두 역할 파일은 **입력을 조건 플래그별 불릿으로 열거하는 자체 계약**을 갖고 있고, 그 열거에 없으면 역할은 그 파일을 받을 근거가 없다. 또 architect의 「수량 대조」 자기 점검은 축이 명시 열거돼 있어, clip 축을 넣지 않으면 «행 수 = 처분 표 행 수» 자가 검사가 안 돈다.

**근거**
- `dddjango-web/agents/design-architect-web.md:25-26` — 「(있으면 — `has_motion_notes`) `motion-notes.md` 경로 — … 동적 표현 전수 처분(architecture-web §8)의 **유일한 입력**이다」 / 「(있으면 — `has_render_audit`) `render-audit.json` 경로 — …」 처럼 채널마다 전용 불릿이 있다.
- `dddjango-web/agents/design-architect-web.md:77` 자기 점검 「**수량 대조**: 절단 토큰 수 = 채택+기각 항목 수 / 렌더 실측 texts·pinned 항목 수 = 실측 처분 항목 수 / **motion-notes의 모션 id(`m*`) 행 수 = 처분 표 행 수(상태 행 제외)** / manifest 항목 수 = 이미지 정형 목록 항목 수 / 인용 엔드포인트 수 = …」 — 열거형이다.
- `dddjango-web/agents/design-review-web.md:17` — 리뷰어 입력도 「(has_motion_notes면) `motion-notes.md` 경로 — 충실도 ⓓ의 대조 근거 … (has_render_audit면) `render-audit.json` 경로 — 충실도 ⓔ의 대조 근거」로 열거돼 있다.
- Coordinator의 역할 호출 입력도 절마다 명시 열거다: `commands/dddjango-web.md:163`(architect)·`:164`(review)·`:166`(반영 재호출)·`:167`(override 재호출)·`:179`(coder)·`:185`(discipline). §4의 「입력 전달 계약에 `clip-containers.md`」 한 줄은 `:157`의 총칙만 가리키며 이 6개 열거를 덮지 못한다.

**수정 방향**
§4를 파일 단위가 아니라 **절 단위**로 쪼갠다 — architect 입력 불릿·수량 대조 행·review 입력 불릿·Coordinator 6개 호출 열거를 각각 명시한다.

---

## [MAJOR] 이 축에서 «실제로 차단하는» 유일한 집행점(discipline-reviewer-web의 조상 사슬 대조)과 이미 존재하는 인과 지식을 설계가 건드리지 않는다

**구멍**
파이프라인에는 이미 이 CSS 메커니즘을 정확히 아는 두 자리가 있고, 그중 하나는 **blocker를 내는** 자리다. 설계는 새 비차단 검사 2종을 만들면서 둘 다 손대지 않는다 — 결과적으로 «차단하는 규칙은 sticky 무력화만 알고, 링 절단은 아무도 blocker로 올리지 않는» 상태가 유지된다.

**근거**
- `dddjango-web/agents/discipline-reviewer-web.md:61` 「**고정 배치 무력화**: 감사 범위 CSS에 `position: sticky|fixed`가 grep으로 **히트하면 조상 사슬 대조가 의무다**(발견 여부 재량 아님) — sticky와 그 의도된 스크롤포트 사이의 중간 조상에 스크롤 컨테이너를 만드는 overflow(`hidden`·`auto`·`scroll` — 어느 축이든)가 있으면 … **blocker**다」 — 트리거(grep 히트)·의무(재량 아님)·등급(blocker)이 모두 선 유일한 자리다.
- `dddjango-web/agents/discipline-reviewer-web.md:63` 「자동 실측의 검사 축 밖인 배경·**그림자**·필터도 해당 원본에 있으면 이 대조에 포함한다」 — 그림자 축의 소유자가 이미 이 리뷰어인데, 설계는 그에게 새 산출물도 새 의무도 주지 않는다.
- `dddjango-web/skills/implementation-ui/references/final.md:213` 「래퍼·셸의 가로 삐짐 클립이 필요하면 `overflow-x: clip`을 쓴다 — 스크롤 컨테이너를 만들지 않는 유일한 클립이다(**타 축의 visible 강등 없음**)」 — 진단이 원인으로 지목한 「한 축이 visible이 아니면 다른 축도 강등된다」는 **이미 규범에 성문화돼 있다**. 빠진 건 지식이 아니라 «바깥 그림자를 지는 요소»에 대한 적용이다.
- 설계 §4 표에 `agents/discipline-reviewer-web.md` 행 없음.

**수정 방향**
`discipline-reviewer-web.md:61`의 트리거를 「`position: sticky|fixed` grep 히트」에서 「외곽 `box-shadow`(포커스 링 포함)를 선언한 규칙의 대상이 `overflow ≠ visible` 조상 아래에 있는가」까지 넓히는 것을 §4에 넣을지 결정한다 — 이것이 이번 결함을 **차단 등급**으로 잡는 유일한 기존 경로이며, 비용은 규범 한 문단이다. `implementation-ui/final.md:210-215`의 배치 거동 절에 링/그림자 여유 요구를 붙이는 것도 같은 자리다.

---

## [MAJOR] 트리비얼 패스트트랙이 padding·overflow 값 수정을 G2 없이 통과시킨다 — 결함을 만드는 가장 흔한 diff 형태가 새 검사 밖이다

**구멍**
이번 결함의 수리는 정확히 「`padding: 3px 3px 4px` 한 줄」이고, 그 역방향(패딩 제거·overflow 추가)도 같은 형태다. 트리비얼 채널은 「신규 파일 0 + 비구조 diff(문구·**토큰 값**·이미지 교체)」를 G2 없이 통과시키며, 설계 §4는 트리비얼 절을 다루지 않는다.

**근거**
- `dddjango-web/commands/dddjango-web.md:215` 「신규 파일 0 + 비구조 diff(문구·토큰 값·이미지 교체)일 때 후보가 된다」
- `:220` 「공통 절차: ① 판정과 근거 승인 1회 … → ③ `backstop.py … --diff-base <편집 직전 HEAD>`(시안 대상은 `--design-build` 필수) + `python manage.py check` → ④ 조건별 검증 결과 보고. **별도 G2·미커밋 합치기는 없다.**」
- `:217`은 모션 축만 명시 합류시킨다: 「**모션/duration 수정도 이 증거 조건에 포함한다**」 — clip 축에 대응 문장 없음.
- 그리고 backstop은 이 축을 안 본다(위 BLOCKER 5 참조).

**수정 방향**
트리비얼 절에 「clip 축에 닿는 diff(레이아웃 `padding`/`overflow`/`box-shadow` 수정)는 트리비얼 비대상 — 수정 모드로 승격」 또는 「트리비얼에도 clip 판정 1회 의무」 중 하나를 §4에서 결정한다. 현행 「view 시그니처·state 모양·라우트 변경이 필요하면 멈추고 수정 모드로 승격」(`:220`)과 같은 판형이다.

---

## [MAJOR] `CANDIDATE_CAP` 초과가 «발견 0»과 구별되지 않는다

**구멍**
설계 §5 R2는 전역 `:focus-visible` 때문에 후보가 폭발할 수 있음을 인정하고 상한(`CANDIDATE_CAP`)·`caps_hit` 기록을 둔다. 그런데 ① 후보를 어떤 **결정적 순서**로 자를지 규칙이 없고 ② `caps_hit`가 비지 않았을 때 판정을 「부분 실행」으로 보고해야 한다는 의무가 없다. 상한에 잘린 뒤쪽에 결함이 있으면 exit 0 + 배너 «발견 0»이 나온다. A8은 전역 규칙이 실재하는 빌드다(`base.css :: :focus-visible` — 설계 §1이 직접 확인).

**근거**
- 설계 `:168` 「상한(`CANDIDATE_CAP`)을 두고 초과는 `caps_hit`에 남긴다(v2 판형)」 — 기록만 요구.
- v2 판형의 실제 소비: `dddjango-web/scripts/compare_render_audit.py`의 커버리지 warn은 `commands:143`·`:187`에서 **배너 표면화 항목**으로 명문화돼 있다. clip에는 그 연결이 없다.
- A8 실측: `render-audit-impl.json`의 `motion.caps_hit = []`·`blind_spots = []`이지만 `focusSelectors`에 `:focus-visible` 전역 규칙이 실재한다(9건 중 1건).

**수정 방향**
`caps_hit` 비지 않음 = 「부분 판정」으로 exit·배너 문장을 가르고, 후보 절단 순서를 문서 순 등 결정적 규칙으로 못 박는다(결정론 픽스처와도 맞물린다).

---

## [MAJOR] 추출 실패 시 `(미추출)` 상태 행을 쓸 주체가 없다 + dc 아닌 시안 경로의 «해당 없음»이 미정의

**구멍**
§3.1은 상태 행 의무를 「클리핑 컨테이너 0건이면 `(없음-확인)`, 추출 불가면 `(미추출)`+사유」로 정하면서 동시에 「**서기가 아니라 기계 산출**이다」라고 못 박는다. 기계가 죽으면 파일 자체가 생기지 않으므로 `(미추출)` 행을 쓸 주체가 없다 — 그러면 하류의 `check_clip_spec`은 파일 부재 → 미실행/warn → 조용한 통과다. 모션 축은 이 함정을 서기 규정(「너는 서기다」)으로 피해 갔다.

또 §3.1은 입력을 「동결 dc HTML」로 한정한다. 시안 경로는 dc 말고도 ⓐ 일반 정적 HTML(`freeze_design.py` 경로) ⓑ 이미지 단독 ⓒ 자체 설계가 있는데, 이들에 대해 `clip-containers.md`를 만드는지·만들지 않는지·배너에 무엇을 적는지 설계에 없다. 인라인 `overflow`는 일반 HTML 시안에도 흔하다.

**근거**
- 설계 `:114-115` 「`scripts/extract_clip_containers.py` → `<산출물 폴더>/clip-containers.md` (Coordinator가 `motion-notes.md`처럼 architect에게 전달. 단 **서기가 아니라 기계 산출**이다.)」 / `:126` 「상태 행(id `—`) 의무: … 추출 불가면 `(미추출)`+사유」
- 비교: `dddjango-web/commands/dddjango-web.md:9` 「**동적 표현 관찰 기록(`motion-notes.md` — 너는 서기다: 출처는 정적 스캔+사용자 문답)**」 — 소유자가 사람(에이전트)이라 실패해도 행이 남는다.
- 시안 경로 분기: `commands:141-142`(정적 HTML·이미지 단독)·`:148`(출처 없음 = 자체 설계).
- 설계 §3.3의 레거시 처리는 「헤더 미검출(레거시 빌드)은 `[warn]`+exit 0」뿐 — **파일 부재**는 다루지 않는다.

**수정 방향**
추출 실패 시 Coordinator가 `(미추출)`+사유 행을 쓰는 주체임을 명시(기계 산출 원칙의 예외)하거나, 실패를 G0 배너 1급 항목으로 올린다. dc 외 경로는 「해당 없음(시안 형식)」 상태 행 또는 명시적 비적용 + 배너 1줄로 닫는다.

---

## [MINOR] §6 브리프의 수치가 §1·§3.1과 어긋난다 — 사용자 결정 게이트에 틀린 표가 올라간다

**구멍**
§6 표는 「수리 3 단독 / 이번 결함: **잡는다**」·「수리 2+3 / 잡는 시점: **G1(설계)**+G2」로 적는다. 위 BLOCKER 1에 따라 수리 3 단독은 이번 결함을 못 잡고, BLOCKER 4에 따라 수리 2는 «G1 승인 **직후**»다. 결정 브리프는 「10줄 이하 브리프·수치 기반」 관례로 사용자 결정의 유일한 근거가 되므로, 틀린 수치는 그대로 잘못된 축소 결정(«수리 3 먼저»)을 유도한다.

**근거**: 설계 `:177-186`(§6 표 — `:179` 「잡는 시점 | G2(구현 대조) | G1(설계)+G2」·`:182` 「이번 결함 | 잡는다 | 잡는다(더 일찍)」)와 `:110-112`·`:150`의 충돌.

**수정 방향**: BLOCKER 1·4 해소 후 표를 재작성하거나, 「수리 3은 상태 측정 확장이 전제」라는 조건을 표에 명시한다.

---

## [MINOR] 새 실브라우저 회귀는 `make verify`(커밋 전 green 게이트) 밖이다 — `release-web`에서만 돈다

**구멍**
§2.4는 실브라우저 회귀 1건을 `verify-web-browser`에 넣는다. 그 타깃은 `make verify`의 구성원이 아니라 `release-web`의 선행 타깃이다. AGENTS.md는 「커밋 전 `make verify` green을 확인한다」를 규범으로 두므로, 새 회귀는 커밋 게이트를 통과한 뒤 릴리즈에서야 발화한다.

**근거**
- `Makefile:23` `VERIFY_TARGETS := verify-ontology verify-base-core verify-base-cross verify-base-backstop verify-base-regen verify-web` — `verify-web-browser` 없음.
- `Makefile:305` `release-web: verify-web-browser _release`
- `Makefile:119-128` — `verify-web-browser`는 현재 `test_observe_interactions.mjs` 1개뿐이고 `DRY=1`이면 스킵된다(`:122`).

**수정 방향**: 의도된 배치인지 §2.4에 1줄 명시한다(순수 판정 `node --test`는 `verify-web`, 브라우저 회귀는 릴리즈 게이트 — 라는 분업이면 그대로 적는다).

---

## [MINOR] design-review-web에 «전수성 리뷰»를 주면 모션 선례의 분업과 충돌한다

**구멍**
§4는 리뷰어에게 「처분 표 전수성 리뷰 항목」을 준다. 모션 축의 확립된 분업은 정반대다 — 전수성·판형은 기계가 선검하고 **리뷰어는 의미 타당성만** 본다. 전수성을 리뷰어에게 주면 기계 작업이 중복되고, 정작 아무도 안 보는 축(처분의 의미 타당성 — 「이 좌표·padding 값이 시안 컨테이너와 정말 대응하는가」)이 무주공산이 된다. 또한 리뷰어는 Phase 1 step 2(G1 **승인 전**)에 돌고 `--spec-only`는 step 6(승인 **후**)에 도는데, 순서 관계가 설계에 없다.

**근거**
- `dddjango-web/agents/design-review-web.md:45` ⓓ 「**전수성·판형 자체는 `check_motion_spec --spec-only`가 기계 선검한다 — 재검하지 말고 너는 처분의 의미 타당성**[관찰 효과 ↔ 분류·좌표·값 매핑이 맞는가]을 본다」
- 호출 순서: `commands:164`(리뷰어) ↔ `:168`(G1 승인 직후 `--spec-only`).

**수정 방향**: 리뷰어 항목을 「clip 처분의 **의미 타당성**(좌표·padding·overflow가 시안 컨테이너와 대응하는가)」으로 재기술하고, 전수성은 기계 소관으로 명시한다.

---

## 검토하지 않은 것

- 판정 규칙 자체의 CSS 정확성(링 확장 계산·클리핑 조상 판별·hard/soft 축 구분) — 검토 A 소관.
- `extract_clip_containers.py`의 좌표 표기·파스 앵커 설계 세부.
- Codex 미러의 본문 대응(커맨드·에이전트는 의미 미러라 기계 대조가 없다 — `Makefile:95-98`의 byte 대조는 `scripts`·`assets`·`references`만 덮는다. §4가 「의미 미러」로 처리한 커맨드/에이전트 편집은 누락돼도 green이며, 이는 이 배치에 국한되지 않는 기존 구조다).
