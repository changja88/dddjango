판정: 수정 후 승인 — blocker 2 · major 9 · minor 12 — 입구·모드 뼈대와 `요청 원문` 줄은 선다. 빼는 출구 검사(허용 표지·오탐 절 단위)와 G0 정지 재개의 전역 `C<n>` 번호는 새고, 범위 규칙은 include 사슬과 교차 단위 정리를 보지 못한다.

# 로드맵 6b 설계 v1 적대 검토 X1 (2026-09-27)

- 대상: `workspace/eval/web-refactor-entry/design-v1.md`(이하 «설계») · `diagnosis.md`(이하 «진단»). 기준 HEAD `c9fcadff`.
- 실측 환경: scratch `…/scratchpad/6b-review-X1/`. 현장 사본은 `sds/`(`git clone --shared` · 현장 HEAD `09a41129b` — 진단 기준 `012e7a99c` 이후 `web/` 커밋 0), 하네스는 Claude Code 2.1.283 바이너리를 판독했다. 모델 호출 0 · 서브에이전트 0 · Serena·Graphify 미사용. 현장 원본은 읽기만 했다.
- 표기: [실측] = 명령·파일 근거 · [추정] = 확인하지 않은 판단. 권고에는 원칙 필터(테스트 보강 없음 · 기존 메커니즘 우선 · 자명한 결정은 묻지 않음)를 적용했다. 이 검토의 권고에는 사용자 결정 질문이 0건이다.

## 설계자가 물은 5곳 — 짧은 답

| 물음 | 답 | 항목 |
|---|---|---|
| §5-3 허용 표지 목록이 제외를 새게 하는가 | **샌다.** 표지를 낱말로 대조하면 부정형 문장(«예외가 아니다»·«허용하지 않으며»)에도 걸린다. `에 한해`·`만 적용`은 제한(의무) 어구다. 오탐을 «같은 절»로 받는 것도 dddjango 가 L-B1 로 걷은 절 단위 검사로 되돌아간 것이다 | B1 |
| §3-1 이름 전속이 공용 파일을 영역에 넣는가 | 현장에서 이름 규칙이 적중한 파일은 `conversation.js` 하나뿐이다. 이 파일은 home 화면에서도 돈다(include 사슬). 반대로 같은 모양의 auth 전용 2파일은 놓친다 | M2 |
| §6 `parse_scope` 확장이 6a 판정을 바꾸는가 | `residual_sets` 결과는 바뀌지 않는다[실측]. 다만 `의미` 행만 있는 절이 오면 6a 러너가 판정 불가(exit 1)를 낸다[실측] | M5 |
| §7-2 «순서 포함 동일»이 다중 치환 줄에서 거짓 red 를 내는가 | 한 줄 안의 다중 치환은 거짓 red 가 아니다. 거짓 red 는 import 재정렬·교환 쌍·폴더 점 경로에서 난다. 더 큰 문제는 결정 9 의 이름 치환이 빠진 것이다 | M6 |
| `요청 원문` 줄이 기능 요청 판별에 영향을 주는가 | 주지 않는다[실측 — 하네스 치환 함수 판독]. 남는 것은 따옴표 꼬리·리터럴 치환 주의 정도다 | m1 |

---

## Blocker

### B1. 빼는 출구 검사가 샌다 — 허용 표지의 부정형 적중 · 오탐 «같은 절» (설계 §5-3)

- **(a) 허용 표지** [실측 — 시뮬레이션]
  - 설계 ② 는 «인용이 든 문장에 허용 표지(`예외`·`허용`·…·`에 한해`·`만 적용`)가 있으면» 제외 근거로 인정한다.
  - dddjango `DocIndex.sentences`(설계가 «같은 분할»이라 한 함수)로 web 코퍼스를 나눠 보면 아래 문장들이 표지에 걸리고, 적용 한정 어구는 없다. 그래서 ②·③ 을 통과하고, 위반 인용과 다른 구간이면 ④ 도 통과한다.
    - `skills/discipline-web-houserules/references/undecidable-web.md:21`: «… → view 승격 신호이지 **예외가 아니다**.» — 표지 `예외`
    - `skills/discipline-cleancode/references/final.md:1606`: «단, 이 자격은 광범위 catch를 **허용하지 않으며** …» — 표지 `허용`
    - `commands/dddjango-web.md:11`: «… 그곳의 쓰기를 **허용하지 않는다**.» — 표지 `허용`
  - `에 한해`·`만 적용`은 제한을 거는 의무 문장이다. 예: `implementation-ui/references/final.md:102` «`|safe`는 근거 있는 신뢰 콘텐츠**에 한해** 최소로 쓴다» · `:216` «금칙은 … 중간 조상에**만 적용**된다».
  - 따라서 «표지 목록이 좁으면 채택이 늘 뿐 제외가 새지 않는다»(§5-3 끝 문단)는 틀렸다. 목록의 크기가 아니라 극성(긍정·부정)이 새는 곳이다.
- **(b) 오탐의 결속 단위**
  - 설계는 오탐 근거를 «위반으로 인용된 **같은 절**의 요건 문구»로 받는다.
  - dddjango 는 적대 검토 L 의 blocker(L-B1 «출구 검사가 절 단위라 과소·과잉», `review-L-step5-v2.md:47`) 뒤 블록 결속으로 바꿨다: `_false_positive` «같은 절의 다른 문장 불가»(`dddjango/scripts/refactor_audit.py:976`).
  - web 절은 길다: cleancode §3 216행 · §10 373행 · §15 347행 [실측 `grep -n '^## '`]. 긴 절의 아무 요건 문장으로 참 위반을 뺄 수 있다.
- **고칠 곳·고칠 말**
  - §5-3 ② «허용 표지(닫힌 목록)»를 «**결합형 긍정 술어** 닫힌 목록»으로 바꾼다. 목록은 `허용한다`·`허용된다`·`허용이다`·`예외로 둔다`·`예외다`·`해도 된다`·`하지 않아도 된다`·`무방하다`이다. 거기에 «같은 문장에 **부정 닫힌 목록**(`허용하지 않`·`허용되지 않`·`예외가 아니`·`예외 없`·`예외를 두지 않`)이 있으면 표지 무효»를 더한다. `에 한해`·`만 적용`은 목록에서 뺀다. 이것은 설계 §9 가 적용 한정 어구에 쓴 «결합형으로만» 원칙과 같다.
  - `--self-test` 에 «코퍼스의 부정형 문장에서 표지 적중 0»을 더한다(드리프트 방지 — 새 장치가 아니라 기존 자가 시험의 한 줄이다).
  - 오탐 근거는 «위반 인용이 든 **문단**(빈 줄·목록 머리·표 행으로 끊기는 단위 — dddjango 블록의 산문판) 안의 요건 문구»로 좁힌다.
  - §5-3 끝 문단의 «제외가 새지 않는다» 문장을 고친다.
- 러너 사례 W6-T6 에 «부정형 문장 근거 제외 red»와 «같은 절 다른 문단 오탐 red»를 더한다.

### B2. G0 정지 재개의 audit 재사용이 전역 `C<n>` 번호 이동과 범위 변동을 못 본다 (설계 §2-3 «G0 정지 재개»)

- **근거** [실측]
  - web 러너의 `C<n>`는 web/ 전체 키를 정렬해 매긴다(`dddjango-web/scripts/src/debt.py:142`). dddjango 의 «BC 필터 스캔 표 순서»와 다르다.
  - 사본 `sds`에서 범위 밖 파일 하나(`web/static/css/Bad-Name.css`)를 더했다. 이때 `static/images` 범위의 `git diff --quiet HEAD -- web/static/images` 는 0이고, `git ls-files --others … -- web/static/images` 는 0행이다. 즉 설계의 재사용 조건은 모두 성립한다.
  - 그런데 `--debt-scan` 번호는 `C1..C3 = images 3키`에서 `C1 = static/css/Bad-Name.css · C2..C4 = images`로 밀린다(`g0-a.json` ↔ `g0-b.json`).
- **영향**
  - 재사용한 `plan.md` 의 «범위 안 C<n>», 리뷰어의 «C<n> 과 같음», verdict 의 «병합 → C<n>»가 모두 다른 키를 가리킨다.
  - 그 결과 G0 `ⓐ 키:`가 새 `debt-g0.json`에서 범위 밖 키로 풀린다. 병합된 M 항목은 범위 밖 키에 붙어, `--debt-residual`로도 `residual`로도 판정되지 않을 수 있다(fail-open).
  - 전속 정적 파일의 소속도 범위 파일의 diff 없이 바뀔 수 있다. 다른 영역 템플릿이 참조를 더하면 «경계 교차»가 되고, 새 전속 파일은 `web/static/**`에 생겨 범위 경로 목록 밖이다.
- **고칠 곳·고칠 말**
  - §2-3 재사용 조건에 한 줄을 더한다: «R1 재스캔 뒤 `plan` 을 다시 돌려, **범위 파일 목록과 범위 안 키 문자열(`검사|경로`) 목록**이 그 audit `plan.md` 와 같을 때만 재사용한다».
  - `plan.md`·리뷰어 표·verdict 의 `C<n>` 옆에 키 문자열을 병기한다. `check-verdict` 재실행은 새 `debt-g0.json`에서 번호를 키로 다시 푼다.
  - W6-T10 에 «범위 밖 새 키로 번호가 밀린 경우 → 번호 재결속 또는 새 점검» 사례를 더한다.

---

## Major

### M1. `plan` 이 «범위 파일 목록»으로 키를 고르면 폴더 경로 키가 빠진다 (§4-1 · §5-2 `plan`)

- 설계는 «범위 안 키는 `plan` 이 `debt-g0.json` 과 **범위 파일 목록**으로 고른다»고 쓴다. 그런데 WS 발견의 경로는 파일이 아니라 폴더다 [실측 `check_structure.py`].
  - WS5: `report('', …)` `:215`(컨테이너 = 빈 경로) · `a + '/'` `:225` · `d + '/'` `:237`·`:250`.
  - WS3·WS4·WS6·WS7: `d + '/'` `:43`·`:83`·`:124`·`:136` 등.
- 설계가 리팩토링 스캔에서 새로 켜는 키(WS5 전 단위)가 바로 이 모양이다. 문면대로 구현하면 이 키들이 범위에 들지 않는다. 그러면 G0 에 묻지 않고, «정리 끝»으로 닫힌다(fail-open).
- **고칠 말**: «키 경로가 단위 접두 `<단위>/` 아래이거나 단위 폴더 자체(`…/` 폴더 키)이거나 전속 정적 파일 목록에 있으면 범위 안이다. 빈 경로(`''`)는 컨테이너 단위다.» W6-T4 에 합성 골격 미비 단위 → `plan` 범위 키 포함을 더한다.

### M2. 범위 규칙의 «참조» 정의가 좁다 — include 를 세지 않는다 (§3-1)

현장 42파일을 설계 규칙 그대로 분류했다 [실측 `classify.py`]:

| 분류 | 수 | 파일 |
|---|---|---|
| 참조 전속 | 17 | auth 5(login·password_reset·signup .css · chunmong-logo-v2·cloud-ornament .png) · chart 4 · consultation 1(conversation.css) · employee_choice 2 · preferences 4 · related_persons 1 |
| 이름 전속 | 1 | `conversation.js` → consultation |
| 경계 교차 | 8 | home.css · user_info.css · background_sound·choice_pair·home_navigation·hour_field·toast·user_info_step .js |
| base 만 참조 | 11 | app_shell·base·components .css · htmx.min.js · background_media·dialog_dismiss·password_visibility·select_menu·submit_lock·terms_agreement·verification_timer .js |
| design_system 만 참조 | 1 | gold-blossom.png |
| **어느 규칙에도 안 듦** | 1 | `wonbo.png` — consultation + design_system 이 참조한다. 영역이 하나라 경계 교차가 아니고, 참조 전속도 무참조도 아니다 |
| 무참조 | 3 | korea_places.txt · `static/htmx/real_name_refresh.html` · `static/htmx/sub_layer_open.html` |

- **(a) HTMX 선언 include 를 세지 않는다.**
  - `web/preferences/preferences/section/preferences_profile_real_name.html:8`이 `{% include "static/htmx/real_name_refresh.html" %}`로 이 파일을 쓴다. 그런데 규칙상 이 파일은 «무참조 → 정적 단위 몫»으로 떨어진다.
  - HTMX 선언 include 는 플러그인 자신이 정의한 형태다(슬라이스 정의 `commands/dddjango-web.md:203` «HTMX 선언 include»).
- **(b) 이름 전속의 유일한 적중이 사실상 공용 파일이다.**
  - `web/home/home/view/home.html:13`이 consultation section `conversation_mount.html`(`data-conversation-mount`)을 include 한다. `conversation.js`는 `base.html:40`에서 전역으로 로드된다.
  - 즉 `conversation.js`·`conversation.css`는 home 화면에서도 렌더되고 실행된다.
  - «다른 영역의 템플릿이 f 를 참조하지 않는다»는 직접 `{% static %}`만 보므로 include 사슬을 놓친다. consultation 실행이 이 파일을 고치면 home 이 영향을 받는데, home 은 범위와 G2 영향 화면 어디에도 들지 않는다.
- **(c) 같은 모양의 파일을 놓친다.**
  - `terms_agreement.js`(훅 `data-terms-gate` → auth 템플릿만)와 `verification_timer.js`(`data-timer-*` → auth 만)도 base 전역 로드이고 한 영역 전용이다 [실측 hook grep].
  - 그런데 이름이 auth 어휘가 아니라서 auth 범위에서 빠진다. 이름 전속은 우연한 명명에 기대는 규칙이다.
- **(d) Python 경로 참조를 세지 않는다.** `web/client/place_directory/korea_places_client.py:21`의 `Path(...)/"static"/"files"/"korea_places.txt"`가 «무참조»로 분류된다.
- **고칠 말**(새 장치 대신 6a 의 기존 대조를 쓴다)
  - «참조 = 6a 참조 완전성의 꼬리 대조(`git grep -n -F -e <꼬리> -- web '*.py' '*.html' '*.css' '*.js' ':(exclude).dddjango-web'` — `commands/dddjango-web.md:211`)가 적중한 줄»로 정의를 바꾼다. 그러면 `{% static %}`·`{% include "static/…" %}`·CSS `url()`·Python 경로가 한 규칙으로 잡힌다.
  - `plan` 이 템플릿 `{% include %}`·`{% extends %}` 리터럴로 «영역 밖 페이지가 include 하는 범위 템플릿»(현장: `home.html:13`)을 «경계 교차 소비자» 목록으로 `plan.md`에 적고, 그 페이지를 G2 영향 화면에 싣는다.
  - 이름 전속을 걷는다. base 전역 로드 파일은 `web/static/js` 단위 실행의 몫이다. 이렇게 하면 `conversation.js`와 auth 2파일이 같은 규칙을 따른다.
  - «비영역 단위(base·design_system)만 참조 → 정적 단위 몫» · «영역 1 + 비영역 단위 참조(`wonbo.png`) → 정적 단위 몫»을 명시한다.
- 덧: §3-2 «42개 중 30개가 한 영역 참조(참조 전속 후보)»는 진단이 base 를 영역으로 센 수치다. 설계 자신의 규칙으로는 17(+ 이름 1)이다.

### M3. 교차 단위 정리가 어느 실행에서도 끝나지 않는다 (§3-1 경계 교차 · §4-4)

- 진단의 대표 의미 빚 «화면 기능 JS 의 base 전역 로드»(근거 undecidable-web §6 «페이지 전용 기능 로드는 해당 페이지의 scripts block에 한 번 두며»)를 고치려면 두 단위를 함께 고쳐야 한다. base.html 의 로드 태그(base 단위)와 영역 페이지의 `{% block scripts %}`(영역 단위)다.
  - 현장 `base.html:32-40`은 기능 JS 8개를 전역 로드한다 [실측].
- 두 실행이 서로를 가리키며 순환한다.
  - **영역 실행**: `base.html:40`은 범위 밖이다. `check` ②(«범위 안»)에서 인용 불일치로 떨어지거나, «별도 요청 — 경계 교차 → 그 단위의 리팩토링 실행»이 된다.
  - **base 실행**: 영역 템플릿이 범위 밖이라 다시 «경계 교차»가 된다.
  - 결과적으로 이 유형은 영구히 정리되지 않는다.
- **고칠 말**(기존 메커니즘): 6a 개명·이동 묶음의 «참조 파일의 단위는 스캔 단위에 넣는다»(`commands/dddjango-web.md:150`)를 리팩토링 범위에도 쓴다.
  - «범위 파일을 가리키는 다른 단위 템플릿의 로드·include **줄**(그 줄만)은 편집 범위다. `plan.md`가 그 줄 목록을 적고, 그 페이지는 G2 영향 화면이다.»
  - §4-4 «경계 교차»는 그 줄 밖을 고쳐야 할 때만 쓴다.

### M4. 렌즈 목록에서 `undecidable-web.md`가 빠졌다 (§4-2)

- `discipline-web-houserules/references/undecidable-web.md`의 지위와 배정은 이렇다 [실측].
  - «백스톱이 못 보는 **의미 판별의 단일 출처**»(`:3`)다.
  - 배정표(`:9-14`)는 6종 판별의 검증자를 바로 design-review-web·discipline-reviewer-web 로 둔다.
  - 진단 4-3 의 base 전역 로드 후보 근거(§6)도 이 파일이다.
- 설계 §4-2 렌즈는 houserules «SKILL·final §1~§6·§8»만 적고 이 파일을 넣지 않았다. 리뷰어는 도구 상수 절 목록으로 점검하므로, 결정 1 이 겨냥한 «검사기가 못 보는 의미 위반»의 핵심 6종이 점검 밖에 남는다.
- **고칠 말**: 배정표 그대로 넣는다 — screen 렌즈에 undecidable-web §1~§4, discipline 렌즈에 §1·§3·§4·§5·§6. 절 번호는 계획 전수 목록에 넣는다.

### M5. G0 계열 절 정형 — `의미` 행만 있는 절에서 6a 러너가 판정 불가를 낸다 (§6 · §8)

- 현행 `debt.residual_sets`에 넣어 봤다 [실측].
  - `## ⓐ 재상정`에 `의미 재상정 키: M2`만 있으면 DebtError «`재상정 키:` 행이 정확히 한 번 있어야 한다(0번)»가 난다.
  - `## G0 재승인`에 `의미 ⓐ 키:`만 있으면 «`ⓐ 키:` 행이 … (0번)»이 난다.
  - C·M 행이 함께 있는 절은 결과가 C 만 있을 때와 같다. 따라서 `_ROW_RE` 확장이 6a 판정을 바꾸지 않는다는 설계 주장은 맞다.
- 설계 §8 은 «C 는 `재상정 키:` · M 은 `의미 재상정 키:`»라고만 쓴다. 이대로면 모델이 M 전용 절을 C 행 없이 쓰게 되고, G2 `--debt-residual`이 exit 1 로 멈춘다.
- 두 가지가 정해지지 않았다.
  - `## G0`에 `의미 ⓐ 키:`가 없을 때 `residual`이 빈 집합으로 읽으면 M_m = 0 이 되어 fail-open 이다.
  - `residual`이 `M<n>`을 풀 audit 폴더를 어디서 찾는지 없다. dddjango 는 실행 줄 `audit <시각>`이 없으면 ToolError 를 낸다(`dddjango/scripts/refactor_audit.py:1199-1201`). 설계는 `G0 정지` 절에만 audit 시각을 적는다.
- **고칠 말**(§6)
  - «G0 계열 절은 6a 정형 행을 항상 적는다(해당 없으면 `-`). 의미 행은 그 위에 더한다.»
  - «`debt-g0.json` mode=refactor 이면, 마지막 `## G0` 절에 `의미 ⓐ 키:` 정확히 1행과 `모드 리팩토링 · audit <R2 시각>` 1행이 있어야 한다. 없으면 `residual` exit 1.»

### M6. `subst-check`가 결정 9 의 이름 치환을 빠뜨렸고, 쌍의 출처 계약이 없다 (§7-2)

- **결정 9 의 절반만 옮겼다.**
  - 결정 9(«이름 치환은 허용하자» — `evening-report.md:129-133`)는 dddjango 0C 대응표에 «파일·디렉터리 이동 · 정의 이동 · **이름 대응**»으로 들어갔다(`dddjango/scripts/behavior_guard.py:8-14`).
  - 결정 17 은 web 을 «dddjango 0C 치환 규칙의 대응»으로 정했다(`evening-report.md:169`).
  - 설계는 결정 9 를 근거로 들면서 경로 쌍만 받는다. 그러면 테스트가 import 하는 이름을 바꾸는 M 항목은 전부 red 가 되고 재상정으로 간다. 현장 예: `ConversationViewModel` import 5파일 · `render_authenticated` 5곳 · `reverse(` 이름 330회.
- **쌍의 출처가 정해지지 않았다.** `--pairs <명세 슬라이스 0 절 경로>`는 architect 가 쓴 산문 절을 파싱하는데, 형식 계약이 없다.
- **거짓 red 가 나는 곳**
  - 순서 포함 대조: 개명으로 import 정렬 순서가 바뀌어 줄이 옮겨지면 red 다.
  - 교환(A↔B)·연쇄 쌍의 순차 역치환: red 다.
  - 폴더 이동의 패키지 점 경로(`web.consultation.conversation.view_model` 수준 import·patch): 파일 쌍으로 풀리지 않아 red 다.
  - `.dddjango-web/` 변경이 슬라이스 커밋에 섞이면 «테스트 밖 web/ 밖 파일»로 red 다.
- **거짓 red 가 아닌 곳**: 한 줄 다중 치환은 역치환을 모두 적용하면 green 이다. 현장 실례는 1줄로, `tests/web/consultation/test_record_detail_view.py:114`가 두 경로를 담는다 [실측]. 설계자가 걱정한 다중 치환 줄은 문제가 아니다.
- **고칠 말**
  - 경로 쌍은 6a 참조 완전성이 이미 쓰는 `git diff -M --name-status <git_snapshot>..<슬라이스 0 커밋> -- web/`의 개명 쌍으로 한다. 폴더 쌍은 옛·새 공통 접두로 뽑는다.
  - 명세 슬라이스 0 절에 정형 행 `이름: <옛> → <새>`를 두고, 그 쌍을 단어 경계 치환으로 더한다.
  - 역치환은 긴 꼬리부터 한 번에(동시 치환) 한다. 대조는 파일마다 줄 **다중집합**으로 한다. `.dddjango-web/`은 뺀다.
  - 결정 9 의 «정의 본문이 이름 말고 같을 때만» 조건은 새 AST 검사를 만들지 말고 기존 5번 감사(DR)의 슬라이스 0 대조 항목으로 싣는다.
- W6-T8 에 «이름 쌍 green · import 재정렬 green · 교환 쌍 green»을 더한다.

### M7. 기능 요청 슬라이스 0 확장이 6a G0 계약과 어긋난다 (§7-2 끝 · §7-1 ③)

- 6a 개명·이동 묶음의 참조 줄 grep 은 `web/`만 본다(«옛 경로의 꼬리 문자열로 `web/`을 grep» — `commands/dddjango-web.md:150`). 그래서 G0 의 «슬라이스 0 규모»와 «충돌»(발주 쓰기 경계 — `:153`) 판정이 web/ 밖 테스트 편집을 모른 채 ⓐ 를 받는다.
- 현장 발주의 허용 경로는 `tests/web/**`다(`docs/superpowers/orders/2026-09-05-web-auth-screens-2.md:99` [실측]). 그런데 설계가 드는 W-T1r2 사례 파일은 `tests/test_settings_profiles.py:131·148`로 tests/web 밖이다. 이 파일은 storage URL 시험에 web 이미지 이름을 표본 문자열로 쓴다 [실측].
- 결과적으로 슬라이스 0 끝에서 coder-web 예외가 발주 경계를 넘는다.
- **고칠 말**(같은 명령을 다시 쓴다)
  - 묶음의 참조 줄 grep pathspec 을 참조 완전성과 같게(`web '*.py' '*.html' '*.css' '*.js' ':(exclude).dddjango-web'`) 바꾼다. 그러면 web/ 밖 테스트 파일이 G0 규모·충돌 판정에 오른다.
  - `:193` «스캔 단위 확인»에 «web/ 밖 테스트 치환 파일은 단위 판정 대상이 아니다» 1구를 둔다.

### M8. green ④ «기존 프로젝트 테스트 새 실패 0»이 근거로 든 결정 17 과 반대이고, 플러그인의 안전망 정의와 충돌한다 (§0 도6 · §7-1 ④)

- 결정 17 설계 처리 문면은 «렌더 전후 대조·**tests/web 채택**은 넣지 않는다»다(`evening-report.md:169` · `web-g0-debt/design-v5.md:11`). 걷은 (나)는 «현장 tests/web 를 고정 대상으로»였다(`morning-briefs-2026-09-27.md:78`).
- web 플러그인의 안전망 정의도 다르다: «동작 보존 안전망은 py_compile·`manage.py check`·결정적 백스톱·사용자 육안»(`skills/discipline-cleancode/SKILL.md:29`).
- 그런데 설계는 ④ 의 근거로 «결정 8·14·17»을 든다.
- 사용자에게 물을 일은 아니다. 결정 14 원칙(«작성된 테스트는 이미 실행이 가능» · 기존 테스트 충분 가정)과 houserules `final.md:107`(«기존 프로젝트의 적용 가능한 검사는 함께 실행한다»)이 답을 준다.
- **고칠 말**
  - §0 도6 의 근거에서 «17»을 빼고 «설계 처리 17 의 "tests/web 채택 없음"을 결정 14 원칙으로 대체한다(이의 시 뒤집는다)»를 적는다.
  - §10 에 `discipline-cleancode/SKILL.md:29`(+ `references/final.md` §16.5 단서 · Codex 미러)의 안전망 목록에 «기존 프로젝트 테스트(있으면 — 베이스라인 대비)» 1구를 더한다.
  - 실행 범위를 한 줄로 정한다: 전체 suite(현장 약 6,000 함수)인지, web 을 참조하는 테스트인지.

### M9. 별도 요청 «HTMX 응답 계약» 유형에 기계 근거가 없다 (§4-4 · §5-3)

- §4-4 는 유형이 5개인데, §5-3 «유형별 근거 검사»는 4개뿐이다(`urls.py path(` · `web/client/` · 범위 밖 · web/ 밖).
- dddjango `_separate`는 모든 유형에 근거 검사를 두고, 근거가 없으면 채택으로 재분류한다(`dddjango/scripts/refactor_audit.py:1004-1027`).
- 이대로면 리뷰어 «아니오»와 유형 이름만으로 항목이 빠진다(fail-open 쪽). 아니면 구현자가 검사를 지어내게 된다.
- **고칠 말**: «HTMX 응답 계약 근거 = 항목 `파일:행`이 view `.py`의 `HX-` 문자열 행이거나 fragment 응답 `render(`·`TemplateResponse(` 행. 그 밖은 채택 재분류.» 또는 이 유형을 걷고 «라우트 URL»과 합쳐 «동작 변경 → 기능 요청» 한 유형으로 둔다.

---

## Minor

- **m1 `요청 원문` 줄** [실측 — 2.1.283 `uEe` 판독]
  - 치환 순서는 이름 인자 → `$ARGUMENTS[N]` → `$<숫자>` → `$ARGUMENTS`(원문 전체)다. 값의 `$`는 이스케이프된다. 이름 치환이 한 번이라도 일어나면 `ARGUMENTS:` 꼬리가 붙지 않는다.
  - 기능 요청은 `요청 원문` 첫머리가 표지가 아니므로 판별에 영향이 없다. 표지를 따옴표로 감싼 입력은 앞 따옴표만 떼면 `대상: web/home"`처럼 **닫는 따옴표가 남는다** — 양끝 짝 따옴표를 뗀다.
  - 새 끝 절·문단에 `$ARGUMENTS`·`$0`~`$9`·`$feature` 리터럴을 쓰면 본문 어디서든 치환된다(필요하면 `\$`).
  - D1 뒤에는 모델이 조립한 args 도 «요청 원문»으로 보인다. «결정 출처 — 본인 직접»의 근거가 아님을 1구로 적는다(`:152` «사용자가 직접 입력한»과 맞춤).
  - 리팩토링 모드의 `빌드할 화면:` 줄(`$feature` = `리팩토링`)은 판별 입력이 아니라는 1구를 둔다.
- **m2 잇기·끝남 판정**
  - build-state `phase`에 끝 값이 없다(`scope|design|implement|finalize` — `commands/dddjango-web.md:61`). «끝난 실행» 기준(예: `g2_approved` ∧ Phase 3 합치기 끝, 또는 `phase: done`)을 적는다.
  - R2~R3 도중 세션이 죽은 경우(phase=scope · G0 전 · 정지 절 없음)의 처리를 1줄 둔다.
- **m3 Override «렌더 결과 보존»**: `coder-web.md:57`의 예외 «(정적 자산 경로는 참조를 함께 치환하면 바뀌어도 된다)»를 같이 쓴다. 없으면 WN8 개명 자체가 렌더 결과(`src`) 변경으로 읽힌다.
- **m4 `:191` «백스톱 위반이 아닌 기존 코드의 이동 → 반송·정지»**: 이 조항은 리팩토링 M ⓐ 이동에도 문자 그대로 걸린다. 끝 절에 «M ⓐ 항목의 이동·개명은 승인 목록이다» 1구를 둔다.
- **m5 WP2 면제 해제**: 6a `_exempt` 주석(«defer 를 붙이면 실행 순서가 바뀌어 동작 불변 교정이 아니다» — `debt.py:90-91`)과 Override «동작 보존 그대로»에 어긋난다. WP2 는 WP5 처럼 면제를 유지하고, WP1·WS5 만 해제한다(현장 영향 0 — 빈 트리 `--diff-base` 모사로 구조 3건 그대로 [실측]).
- **m6 «미룰 수 없음» 키**: 6a 빚 목록 규칙(«경로와 무관한 «미룰 수 없음» 키» — `:148`)을 리팩토링 R1 표(«범위 안 키만»)가 버린다. 유지할지 1줄로 정한다.
- **m7 §10 누락**
  - `dddjango-web/.claude-plugin/plugin.json` description · `codex-dddjango-web/.codex-plugin/plugin.json` longDescription — 로드맵 5 는 둘 다 고쳤다 [실측 `dddjango/.claude-plugin/plugin.json:5` · `codex-dddjango/.codex-plugin/plugin.json:25`].
  - README 사용 예 표(`README.md:105-110` — dddjango 리팩토링 행 `:109`의 대칭).
  - 모드 판별 절 제목 «구조 단위 삼분류»(`:120`).
  - REQUEST_GUIDE §7 의 «사용자 판단 항목은 대신 답하지 않음» 1행.
  - §10 5′ 의 대리 표지 문장은 dddjango 배포 가이드에 없다(`dddjango/REQUEST_GUIDE.md` §7). 대리 세션도 슬래시 입력은 사용자 입력으로 성립하므로, 가이드는 입구만 안내하고 표지는 적지 않는 편이 대칭이다.
- **m8 W6-T5 합격 기준**: `wonbo.png`·`real_name_refresh.html`·`terms_agreement.js` 분류와 home 의 «경계 교차 소비자» 표시를 더한다(M2).
- **m9 `check` 행의 괄호**: «의미 미러에서 못 찾으면 불일치(fail-closed · 채택 쪽)»는 위반 행에 대해서는 반대다. 인용 불일치 행은 M 에 들지 않고 목록 표시만 된다(dddjango L-M2 처분과 같다). 괄호는 `check-verdict` 근거에만 쓴다.
- **m10 `sections` 의 필요 증명이 약하다**: architect 는 Read 를 가지고, `check-verdict`가 근거를 문서에 직접 대조한다. 유지한다면 경계 예외(«판정 근거는 `sections.md`가 공급한 것뿐»)의 이유를 1줄 적는다. 빼도 fail-open 은 없다.
- **m11 `subst-check`의 위치**: 기능 요청 슬라이스 0 에도 쓰이는데 `refactor_audit.py` 안에 둔다. 두 모드 공용이라는 것을 도구 설명·Coordinator 호출문에 명시한다.
- **m12 작업량** [추정]
  - 표에 설계 v2·적대 재검토·계획·계획 리뷰 몫이 없다. 선례로 로드맵 5 는 설계 v1→v5 · 계획 v1→v2 · 추정 12~17 → 계획 17~19 였고, 6a 는 v1→v5 였다.
  - 도구 2.5~3일도 적다. dddjango 도구(1,521행 · 러너 54사례 · 검토 K~O 에서 출구 검사 blocker 반복)의 이식이라도 M2 참조 파서·include 사슬, B1 극성 표지, M6 이름 쌍을 더하면 3.5~4.5일이다.
  - 합계는 약 **11~14일**로 본다.

---

## 결정·원칙 대조 (볼 것 6)

| 대조 | 판정 |
|---|---|
| 결정 1(1-a·1-b·1-d) | 입구·R2·R3·G0 승인 구조는 맞다. 1-b «증명 책임은 빼는 쪽»의 기계 관문은 B1 로 샌다 |
| 결정 8·14 | 새 장치 없음 · 테스트 보강 없음은 맞다. ④ 테스트 실행은 원칙 14 로 설명하고 근거에서 17 을 뺀다(M8) |
| 결정 9 | 이름 치환 누락(M6) |
| 결정 17 | 문면 모순(M8) · 치환 규칙의 대응이 절반(M6) |
| 결정 18 | Override ⑴⑵ 는 dddjango 와 같은 모양이라 맞다. 면제 해제(WP1·WS5)는 맞고, WP2 는 동작 보존 쪽이라 유지한다(m5) |
| D1 | 입구 위임은 선다. 하네스 검증은 `disableModelInvocation && !userTypedThisTurn`만 보므로 D1 뒤 막는 장치가 없다(진단 1-2 판독과 일치). W6-T12 관찰만 두는 처분은 적절하다 |

## 새 장치 필요성 (볼 것 2)

| 하위 명령 | 기존 메커니즘으로 대체 | 판정 |
|---|---|---|
| `plan` | 불가. 범위·조각·재사용 결정성이 필요하다. 다만 참조 판정은 6a 꼬리 grep 을 재사용한다(M2) | 둔다 |
| `check` | 불가. dddjango R-T2 에서 인용 불일치를 실제로 잡았다 | 둔다 |
| `sections` | 가능하다(m10) | 선택 |
| `check-verdict` | 불가. 도구가 빠지면 결정 1-b 의 관문이 모델 규율에만 걸린다(설계 §5-1 (C) 판단 동의) | 둔다 — B1 보정 필수 |
| `residual` | 결정적 바닥은 `git diff --quiet`, 묶음은 Coordinator 가 할 수 있다. 다만 `--finalize`의 «새 `파일:행` 근거 없는 해소 = 잔존»은 기계 검사다 | 둔다 — M5 보정 |
| `subst-check` | 결정 8(1)·17 이 요구하는 기계 확인이라 필요하다. 쌍은 6a `git diff -M` 을 재사용한다(M6) | 둔다 |

## 실측 기록 (scratch `/private/tmp/claude-501/-Users-hyun-Desktop-dddjango/ed01792c-e467-4a58-a794-ed16237ffb9e/scratchpad/6b-review-X1/`)

- 하네스: `/opt/homebrew/Caskroom/claude-code@latest/2.1.283/claude`의 `uEe`·`qhr` 판독 — 이름 인자 → `$ARGUMENTS[N]` → `$(\d+)(?!\w)` → `replaceAll("$ARGUMENTS", 원문)` · `!F&&r&&n` 일 때만 `ARGUMENTS:` 꼬리.
- `sds/`: 현장 `--shared` 사본(HEAD `09a41129b`).
- `g0-a.json` · `g0-b.json`: B2 번호 이동. 범위 밖 `Bad-Name.css` 추가 → C1..C3 가 C2..C4 로 밀림. 추가 파일은 지웠다.
- `owner.py` · `classify.py`: M2 의 42파일 분류.
- 빈 트리 커밋 `--diff-base` 모사: 구조 3(WN8) · 시안 16 — 진단 4-2 와 같다.
- `debt.residual_sets` 사례 A·B·C: M5.
- `dddjango/scripts/refactor_audit.py` `DocIndex.sentences`로 web 문장 분할 → 표지 적중: B1.
- 저장소에 쓴 파일은 이 검토 1개다. 커밋·push 없음.
