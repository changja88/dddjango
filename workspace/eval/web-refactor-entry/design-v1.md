# 로드맵 6b 설계 v1 — dddjango-web 리팩토링 입구 (2026-09-27)

> **요지**
> 1. **입구**: web Coordinator 의 `disable-model-invocation` 을 걷고(사용자 결정 D1 (가)), dddjango 와 같은 얇은 입구 `/dddjango-web:refactor` → Skill 위임을 둔다. 인자 잘림(진단 1-4)은 Coordinator 본문에 `요청 원문: $ARGUMENTS` 1행을 두고 모드 판별이 그 줄을 읽게 해서 푼다(따옴표 방식은 걷음). Codex 는 `$dddjango-web-refactor` 얇은 스킬(dddjango 판형 그대로).
> 2. **모드**: 대상 = 6a 단위 1개 + 그 화면 사슬의 전속 정적 파일. 흐름 = R0 대상 → R0′ 폴더 → R1 검사기 빚(`--debt-scan --refactor` — 브라운필드 면제 해제) → R2 의미 점검(리뷰어 2종 × 조각) → R2′ 인용 검사 → R3 architect 판정 → G0 → Phase 1~2(슬라이스 0 만) → G2(M = M_c + M_m).
> 3. **도구**: dddjango `refactor_audit.py` 는 rulepack(블록 결속·규범 종류)·`application/<bc>/`·렌즈 4 에 묶여 web 이 쓸 수 없다. **web 전용 최소 도구** `dddjango-web/scripts/refactor_audit.py`(plan · check · sections · check-verdict · residual · subst-check)를 둔다. rulepack 대신 «문장 단위 적용 한정 어구 + 허용 표지 닫힌 목록 + 반대 방향 열»으로 빼는 출구를 fail-closed 로 막는다. `refactor-scope.md` 파서는 6a `debt.py` 를 재사용한다.
> 4. **동작 보존**: 새 장치 없음. 슬라이스 0 끝 green 에 «기존 프로젝트 테스트 베이스라인 대비 새 실패 0»을 명시하고, web/ 밖 테스트 파일의 옛 경로 → 새 경로 **치환만** 허용해 `subst-check` 로 기계 확인한다(기능 요청의 슬라이스 0 에도 같다 — 6a W-T1r2 가 현장에서 찾은 사례).
> 5. **열린 물음 0** — 남은 갈래는 전부 기존 결정·플러그인 정의로 도출했다(§13).

- 입력: 진단 `diagnosis.md`(HEAD `c9fcadff` · 스파이크 1회) · 사용자 결정 D1 «(가) 걷는다»(09-27 · 본인 직접) · dddjango 선례(로드맵 5 `f985347d`: `dddjango/commands/refactor.md` · Coordinator `:67`·`:69`·끝 절 `:222-247` · `refactor_audit.py` 1,521행 · 설계 `step5-refactor-command-design-v5.md` §3~§7) · 6a(`d2b9281c`).
- 표기: [도출] = 기존 결정·플러그인 정의에서 답이 나와 묻지 않은 것(이의가 있으면 뒤집는다 · 사용자 결정 기록이 아니다). 행 번호는 HEAD `c9fcadff` 기준이고 계획에서 다시 확인한다.

## 0. 결정 근거 표

| # | 항목 | 이 설계의 답 | 근거 |
|---|---|---|---|
| D1 | Claude 입구 호출 정책 | web Coordinator `disable-model-invocation` 제거 · 얇은 입구 Skill 위임 | **사용자 결정 D1 (가)**(09-27) · 스파이크 1/1 거부(진단 1-3) |
| 도1 | 입구 이름·표지·Codex 트리거 | `/dddjango-web:refactor` · `리팩토링 모드(입구 /dddjango-web:refactor) · 대상: …` · `$dddjango-web-refactor` | 결정 13 (가) · 1-d |
| 도2 | 대상 · 점검 범위 | 6a 단위 1개 · 단위 + 화면 사슬 전속 정적 파일 · 여러 단위는 단위마다 실행 · 리팩토링 G0 에 ⓐ′ 없음 | ⓐ′ 약속(web `:151`) · 결정 18 (가) · 슬라이스 정의 `:203` |
| 도3 | 점검 주체·판정 | design-review-web + discipline-reviewer-web «단위 점검» 모드 · 판정 design-architect-web · G0 사용자 승인 · implementation-ui 는 리뷰어에 배정 | 결정 1-b · 1-d · 12 (가) |
| 도4 | 적용 범위 | web Override 문단 · 리팩토링 스캔은 브라운필드 면제 해제(motion.js 판형 제외) | 결정 18 (가) · 진단 4-2(현장 영향 0) |
| 도5 | G0 규칙 | 정리할 것 0 → G0 정지 · 사용자 판단 항목 대리 불가 · 결정 출처 규칙 그대로 | dddjango 끝 절 G0 · 1-d |
| 도6 | 동작 보존 | 새 장치 없음 · 기존 프로젝트 테스트 실행(베이스라인 대비 새 실패 0) | 결정 8 · 14 · 17 · houserules `final.md:107` |
| 도7 | web/ 밖 테스트 | 옛 경로 → 새 경로 치환만 허용 · 치환만인지 기계 확인 | 결정 9 · 1-d · 17 |
| 도8 | ⓐ′ 대가 줄 | «의미 점검 포함» 1구 | 1-d · dddjango `:82` 대칭 |

## 1. 입구

### 1-1. Claude

- **web Coordinator** `dddjango-web/commands/dddjango-web.md` frontmatter 에서 `disable-model-invocation: true`(`:5`)를 지운다(D1). 다른 frontmatter 키는 그대로다. dddjango `7718407f` 와 같은 1행 변경이다.
- **입구** `dddjango-web/commands/refactor.md`(새 파일 · dddjango `commands/refactor.md` 판형):
  - frontmatter: `description`(«대상 단위 하나의 기존 web 코드 전체를 dddjango-web 표준으로 정리하는 리팩토링 입구(동작 불변). 검사기 빚과 의미 점검 항목을 G0 에서 묻고 슬라이스 0 으로 정리한다. 사용자가 직접 부를 때만 쓴다.») · `argument-hint: "<대상 단위 — 예: web/home · web/static/images> [불편 서술]"` · `disable-model-invocation: true`(입구 자신은 사용자만) · `allowed-tools: Skill(dddjango-web:dddjango-web)`.
  - 본문: «Skill 도구로 `dddjango-web:dddjango-web` 을 부르고, args 로 아래 줄을 한 글자도 바꾸지 말고 그대로 넘겨라. 다른 일은 하지 않는다.» + `리팩토링 모드(입구 /dddjango-web:refactor) · 대상: $ARGUMENTS`.
- **인자 보정(진단 1-4) — `$ARGUMENTS` 1행을 고른다**
  - Coordinator `:15` `빌드할 화면: $feature` 아래에 `요청 원문: $ARGUMENTS` 1행을 둔다. 하네스는 `$ARGUMENTS` 에 args 원문 전체를 넣는다(진단 1-2 판독).
  - 모드 판별(§2-1)은 **`요청 원문:` 줄**을 판별 입력으로 읽는다. 그 줄이 여는 따옴표(`"`·`'`)로 시작하면 그 한 글자를 떼고 본다.
  - 따옴표 갈래를 걷은 이유: ① args 에 사용자 따옴표가 섞이면 셸식 토큰화가 실패하고 공백 분할로 떨어진다(진단 1-2 `qhr` → 실패 시 공백 분할) — 입구 표지가 다시 잘린다. ② 대리 경로(`/dddjango-web:dddjango-web 리팩토링 모드(…) · 대상: …` 직접 입력)와 기존 기능 요청의 무따옴표 사용(README:108)도 `$ARGUMENTS` 줄 하나로 같이 풀린다. ③ 변경이 Coordinator 1행이고 입구 문면이 dddjango 와 같게 남는다.
  - `$feature`·`$api_url` 의 기존 뜻은 바꾸지 않는다(기능 요청 경로 무변). 리팩토링 모드에서 `$api_url` 자리는 쓰지 않는다(§2-3 step 3 생략).
- **호출 정책 변화의 기록**: D1 대가(모델이 web Coordinator 를 스스로 부를 수 있음)를 README·REQUEST_GUIDE 에는 적지 않는다(dddjango 도 적지 않았다). 행동 시험 W6-T12 에서 맨 프롬프트의 암묵 호출 여부를 **관찰만** 기록한다(합격 기준 아님 — D1 이 받아들인 대가다).

### 1-2. Codex

- `codex-dddjango-web/skills/dddjango-web-refactor/SKILL.md` + `agents/openai.yaml`(`allow_implicit_invocation: false`) — `codex-dddjango/skills/dddjango-refactor/` 판형 그대로:
  - «형제 스킬 `dddjango-web` 의 Coordinator 로 작동하라. 본문은 `../dddjango-web/SKILL.md` 다 — 먼저 `wc -l` 로 길이를 잰 뒤 구간으로 나눠 끝까지 읽는다(마지막 절 «리팩토링 모드»의 끝 문장까지).» · `scripts/` 와 역할 스킬 경로 기준 = 형제 `../dddjango-web/`.
  - 요청 첫 줄: `리팩토링 모드(입구 $dddjango-web-refactor) · 대상: <인자>`.
- Codex web Coordinator 는 인자가 위치 인자가 아니라(`:16` «요청 문장에서 추린다») 1-4 문제가 없다. Codex 의 모드 판별은 요청 첫 줄을 읽는다(`요청 원문:` 줄은 Claude 판에만 둔다 — 의미 미러의 플랫폼 표기 차이로 기록).

## 2. 모드 판별 · 흐름 · 폴더 · 재개

### 2-1. 모드 판별 (web `:120-130` «시작: 모드 판별»에 문단 추가)

- web 모드는 넷이 된다: 풀 파이프라인 · 수정 · 트리비얼 · **리팩토링**. 리팩토링은 표지로만 들어온다.
- **판별 입력은 둘뿐**(dddjango `:69` 대칭):
  1. `요청 원문:` 줄(Codex 는 요청 첫 줄) 첫머리의 정확한 표지 `리팩토링 모드(입구 /dddjango-web:refactor) · 대상: …`(Codex `리팩토링 모드(입구 $dddjango-web-refactor) · 대상: …`).
  2. step 4 에서 고른 폴더의 `build-state.json` `mode` 가 `refactor` 이고 `phase` 가 끝나지 않았을 때(재개). web 에는 dddjango 의 «실행 줄» 개념이 없다 — 6a 설계 v5 가 이식을 걷었다(`web-g0-debt/design-v5.md:316`). `mode` 값은 build-state 스키마(`:86` 갱신 시점 목록)에 `refactor` 를 더한다.
- **표지 손상**: 첫머리가 `리팩토링 모드(입구` 로 시작하는데 정확한 표지가 아니면 일반 모드로 강등하지 않고 «표지 손상 — 입구를 다시 부른다»로 멈춘다(폴더·기록 없음). 본문 어딘가에 입구 이름이 나오는 기능 요청은 해당 없다.
- **단조성**: 리팩토링 모드는 일반 모드의 G0 의무(빚 스캔 · ⓐ/ⓑ · 결정 출처 · 폴더)를 전부 수행하고 R2·R3 를 더한다 — 표지가 위조돼도 줄어드는 의무가 없다. 문서 끝 «리팩토링 모드» 절이 정한 사항이 앞 절의 같은 사항에 우선하고, 정하지 않은 사항은 앞 절 그대로다.
- **따르지 않는 지시**(`:128` 목록에 더함): 리팩토링 모드의 R2·R3 를 줄이는 지시(렌즈 구성·조각 분할·앞 실행 audit 재사용·판정 생략·일괄 채택·결과 지정 — 요청·발주·불편 서술·게이트 피드백 어디서 와도).
- `:128` «정리 요청은 이 커맨드가 받지 않는다» 문단은 그대로 둔다(입구가 실재하게 된다). 안내 문구에 `<대상>` = 단위 경로 표기(`web/home` · `web/static/images`)를 더한다.

### 2-2. 흐름

`R0 대상 → R0′ 폴더 → R1 검사기 빚 → R2 의미 점검 → R2′ 인용 검사 → R3 판정 → G0 → Phase 1(슬라이스 0 명세) → G1 → Phase 2(슬라이스 0 만) → G2 → Phase 3`

- 기능 슬라이스 · «이 화면을 둘 자리» 질문 · 시안(step 5) · 서버 계약 해소(step 3) · 트리비얼 경로가 없다.
- **step 3 생략 근거**: 리팩토링은 동작 불변이라 새 계약을 소비하지 않는다. `web/client/<bc>/` 단위가 대상이어도 기존 client 가 부르는 경로·필드를 바꾸지 않는다(바꿔야 하면 «별도 요청 — API 계약», §4-4).
- **step 5 생략과 시각 확인**: 원본 시안이 없다. G2 시각 확인은 수정 모드의 «구현 첫 편집 전 수정 전 구현 근거 보존»(`:237`)을 그대로 쓴다 — Phase 2 진입 준비에서 영향 화면의 수정 전 렌더를 보존하고 G2 에서 전후를 대조한다(새 장치가 아니다).

### 2-3. R0 대상 · R0′ 폴더 · 재개

- **R0 대상**: `대상:` 인자에서 단위를 정확히 1개 읽는다. 표기는 `web/` 기준 경로다(`web/home` · `web/static/images` · `web/design_system` · `web/base` · `web/client/orders` · 컨테이너는 `web/*.py`). 끝 `/` 는 무시한다. 6a 단위 목록(`:148`)에 맞고 실재해야 한다. 없음 · 2개 이상 · 단위가 아닌 경로(`web/home/home/view` 처럼 단위 안쪽) · 불편 서술이 새 동작·새 계약을 요구함(기능 혼입)이면 폴더·기록 없이 입구에서 멈추고 사용법을 안내한다(기능은 `/dddjango-web:dddjango-web` 으로 · 여러 단위는 단위마다 한 실행). 불편 서술은 항목 후보다(선택).
- **R0′ 폴더**: slug = `refactor-<단위 케밥>`(예: `refactor-home` · `refactor-static-images` · `refactor-web-py`). 폴더 이름은 web 관례 `<date +%Y%m%d-%H%M>-<slug>` 다. 후보는 slug 가 같은 폴더뿐이다 — 있으면 그것만 보이고(«새 폴더» 없음 · 끝난 실행 뒤의 새 점검은 그 폴더를 재사용), 없으면 새 폴더를 R1 전에 만든다(`:144` «새 화면» 목록 규칙은 쓰지 않는다).
- **잇기**: 고른 폴더의 build-state `mode: refactor` 이고 phase 가 G0 뒤·끝나기 전이면 잇는다 — R2·R3 를 다시 돌리지 않고 그 audit 의 `verdict.md` 를 그대로 쓴다(M 목록 동결). phase 가 끝났으면 새 점검이다(같은 폴더 · R1~R3 새로 · 6a 재사용 폴더 규칙대로 `debt-g0.json` 교체).
- **표지 없는 잇기**: 표지 없는 `/dddjango-web:dddjango-web` 으로 `mode: refactor` 폴더를 «기존 폴더 이어서»로 고르면 그 순간부터 리팩토링 모드다(그때까지의 일반 모드 Phase 0 산출은 버린다). 그 요청에 기능이 섞였으면 G0 정지로 기록하고 기능은 따로 요청하라고 안내한다.
- **G0 정지 재개**(dddjango 대칭): 리팩토링 실행의 `## G0 정지 <시각>` 절에 `모드 리팩토링 · audit <R2 시각>` 을 적는다. 같은 폴더에서 다시 시작했고 최신 기록이 이 정지이면 — 그 audit `plan.md` 에 `범위 미커밋 변경 0` 이 적혀 있고 · 범위 파일(단위 + 전속 정적 파일 목록)이 그 HEAD 이후 바뀌지 않았고(`git diff --quiet <그 HEAD> -- <범위 경로…>` — 작업 트리 포함) · 새 파일이 없을 때(`git ls-files --others --exclude-standard -- <범위 경로…>` 빈 결과)만 `check-verdict` 를 다시 돌려 exit 0 이면 audit·verdict 를 재사용하고 R1 만 다시 돈다. 하나라도 어긋나면 새 점검이다. 재사용 거부(«새로 점검»)는 사용자 본인 직접 답만 받는다.

## 3. 대상 단위 · 점검 범위

### 3-1. 범위 = 단위 파일 + 전속 정적 파일

- **단위 파일**: 대상 단위 아래 git 우주(6a `debt_universe` 와 같은 우주 — `git ls-files -co --exclude-standard`, 바이트코드 제외).
- **전속 정적 파일**(대상이 영역 `web/<area>/` 일 때만 — 정적 단위·design_system·base·컨테이너·client 가 대상이면 단위 파일만): `web/static/**` 파일 f 가 다음 중 하나이면 그 영역 전속이다.
  1. **참조 전속**: f 를 참조하는 템플릿이 모두 그 영역 안에 있다. 참조 = 템플릿의 `{% static '<프리픽스>/…' %}`(프리픽스 사상은 `STATICFILES_DIRS` 규약 — `web/` → `web/static/` · `design_system/` → `web/design_system/`) · CSS `url(...)` 의 상대·절대 경로.
  2. **이름 전속**: f 의 파일 이름 줄기(확장자·내용 해시 접미 `_<hex>` 제외)가 그 영역의 화면 어휘 — 영역 이름 또는 그 영역 안 화면 폴더 이름(`web/<area>/<view>/`) — 와 같거나 `<어휘>_`·`<어휘>-` 로 시작하고, **다른 영역의 템플릿이 f 를 참조하지 않는다**(base 전역 로드는 참조로 세지 않는다). 현장 `conversation.js`(base `:40` 전역 로드 · 화면 폴더 `web/consultation/conversation/`)가 여기에 든다.
- **경계 교차**: 둘 이상의 영역(base 제외)이 참조하는 정적 파일은 그 정적 단위 실행의 몫이다. 영역 실행에서는 범위에 넣지 않고 `plan.md` 에 «경계 교차» 목록으로 적는다 — 리뷰어가 이 파일과 얽힌 위반(예: 영역 템플릿이 공용 JS 의 전역 함수를 부름)을 내면 architect 가 «별도 요청 — 경계 교차»로 판정할 수 있다(§4-4). dddjango «타 BC» 규칙의 대응이다.
- **어디에도 참조되지 않는 정적 파일**은 정적 단위 몫이다.
- 판정은 `refactor_audit.py plan` 이 결정적으로 한다(§5). 규칙 이름·근거를 파일마다 적는다(`참조 전속` · `이름 전속` · `경계 교차`).

### 3-2. 현장 모양(진단 2-1 실측 기준)

- 42개 정적 파일 중 30개가 한 영역 참조(참조 전속 후보) · 9개 다영역(경계 교차) · 3개 무참조. `conversation.js`·`conversation.css` 는 이름 전속으로 consultation 에 든다 → consultation 실행 범위 약 9.8K행(진단 2-2).

## 4. 빚 — 검사기(C) + 의미(M)

### 4-1. R1 검사기 빚 — `--debt-scan --refactor`

- **러너 계약**(`backstop.py` · `src/debt.py`):
  - `--debt-scan --refactor [--json <경로>]`: 6a 스캔과 같은 우주·키·`C<n>` 에 **브라운필드 면제를 끈다** — `DEBT_EXEMPT` 의 WP1(legacy htmx core)·WP2(그 로드 태그) 면제를 걷고, WS5(골격 완비)를 **모든 기존 단위**에 적용한다(빚 모드의 «WS5 빚 모드 제외» notice 대신 발견). WP5(motion.js 판형)는 플러그인 갱신 사안이라 면제를 유지한다.
  - JSON 에 `"mode": "refactor"` 필드를 더한다(6a 스캔은 `"feature"` — 없으면 `feature` 로 읽는다).
  - `--refactor` 는 `--debt-scan` 과만 쓴다. `--debt-residual` 은 `debt-g0.json` 의 `mode` 를 읽어 **같은 의미론으로** 다시 스캔한다(플래그 없이 — G0 와 G2 의 의미론이 어긋날 수 없게).
  - 단위 필터는 러너에 두지 않는다 — 스캔은 web/ 전체를 동결하고, 범위 안 키는 `plan` 이 `debt-g0.json` 과 범위 파일 목록으로 고른다(§5 `plan --debt`).
- 현장 영향: 면제 해제로 늘어나는 키 0(진단 4-2).
- 기록: 6a step 4′ 스캔 기록 절(`## 빚 스캔 <시각>`) 그대로 · 표는 범위 안 키만 · «미룰 수 없음»은 `C<n>` 에만.

### 4-2. R2 의미 점검 — 리뷰어 2종 «단위 점검» 모드

- **렌즈 2개**(dddjango 렌즈 4 의 web 판):
  - `screen` = `dddjango-web:design-review-web` — architecture-web §1~§8 + implementation-ui §3(삼총사 표기)·§5(section·HTMX)·§8(client)·§9(urls) + agent 문면 «G1 설계 모드 점검 항목» 중 코드에 적용되는 항목.
  - `discipline` = `dddjango-web:discipline-reviewer-web` — discipline-cleancode §1~ + discipline-web-houserules SKILL·final §1~§6·§8 + implementation-javascript §1~§7 + implementation-ui §4(템플릿)·§6(widget·component)·§7(토큰·CSS·에셋).
  - implementation-ui §1(handoff)·§2(시안 재현 절차)는 기존 코드 점검 대상이 아니다(시안 입력 절차). houserules final §7(백스톱 연동)은 R1 몫이다.
  - 배정 근거: 결정 12 (가)(기술 규칙은 리뷰어에게 분담) — implementation-ui 는 지금 coder-web 만 적재하므로 리뷰어가 **플러그인 루트 경로로 읽는다**(frontmatter 스킬 목록은 모드별로 못 바꾼다 · dddjango 와 같은 처리). 렌즈별 점검 절 목록(`문서 §절`)은 도구 상수로 고정하고 `--self-test` 가 절 실재를 대조한다. 절 번호 전수는 계획이 확정한다.
- **조각**: 범위 파일을 경로 순으로 쌓아 5,000행 문턱으로 자른다(문턱을 넘는 단일 파일은 단독 조각). 영역이면 순서는 `view_model·state·view(.py)` → 템플릿(view·section·widget) → 전속 CSS → 전속 JS 다(한 화면 사슬이 같은 조각에 오도록 — 화면 폴더 단위로 먼저 묶고 문턱을 적용). 조각 × 렌즈 = 파견 다발.
- **파견 입력**: 모드 `UNIT_AUDIT` · 조각 파일 목록 · 렌즈 · 점검 절 목록 · 범위 안 `C<n>` 목록(중복 표시용) · 불편 서술 항목 · 적용 범위 규범 원문(§9) · 플러그인 설치 루트 절대 경로 · `plan.md` 의 «경계 교차» 목록. 한 응답 안 병렬이 원칙이다(런타임 동시 슬롯 한도 단위의 반복은 위반 아님).
- **산출 표**(dddjango §3-3 과 같은 열): `행# | 규칙 = <문서> §<절> «원문 인용 20~60자» | 반대 방향 규칙(있으면 같은 형식) | 파일:행 | 위반 요지 | 동작 불변 정리 가능(예 / 아니오 — 사유: 라우트 URL · API 계약 · HTMX 응답 계약 · 경계 교차 · web/ 밖) | C<n> 과 같음(있으면)`.
  - 위치마다 파일 경로를 다시 적는다(dddjango R-T2 관찰 — `:25-34 · :51` 축약이 인용 불일치를 냈다).
  - 규칙 문구를 댈 수 없는 항목은 내지 않는다. 불편 서술을 규칙에 잇지 못하면 `규칙 = 근거 없음(불편 #k)` 행.
  - 표만 낸다. Coordinator 는 그대로 `audit/<R2 시각>/<렌즈>-<조각>.md` 에 쓰고 대화에 다시 출력하지 않는다.
  - 테스트 충분성·커버리지는 점검 항목이 아니다(원칙).
- **에이전트 문면**: design-review-web 에 «단위 점검 모드» 절(기본 = 지금의 G0 입력범위 모드·G1 설계 모드 · 명시 입력이 있을 때만 단위 점검) · discipline-reviewer-web 에 같은 절(기본 = Phase 1 경량·Phase 2 감사). 두 절 모두 «잔존 확인»(§8) 하위 항목을 둔다.

### 4-3. R2′ 인용 검사 · R3 판정

- **R2′**: `refactor_audit.py check <audit>` — 불일치 행만 원 리뷰어에게 1회 재인용(코드 재점검 아님) → 다시 `check` → 남는 행은 «인용 불일치» 목록(무언 삭제 금지).
- **R3**: `refactor_audit.py sections <audit>` → `dddjango-web:design-architect-web` 을 «의미 항목 판정» 모드로 부른다(입력 = `check.md`·`sections.md` 경로 · `C<n>` 목록 · 자기 도구 Grep). architect 가 `verdict.md`(`M<n> | 원 행 | 판정 | 근거 | 파일:행 목록`)를 쓰면 `check-verdict` → red 면 red 행·사유로 1회 재호출 → 또 red 면 `check-verdict --final`(남은 red 행 = 채택). G0 배너 계수는 `check-verdict` 의 `요약:` 행이 출처다.
- 판정 범주는 dddjango 와 같다: 채택 · 병합 → M<k>|C<n> · 제외 · 오탐 · 사용자 판단 · 별도 요청. 비용·일정·규모는 빼는 사유가 아니다(그것은 사용자의 ⓑ).
- architect 문면: «의미 항목 판정» 모드 절 · 경계 예외 1행(«리팩토링 모드 판정(`verdict.md`)은 예외 — 판정 근거는 `sections.md` 가 공급한 것뿐»).

### 4-4. 별도 요청 유형 (web)

리뷰어 «아니오 — 사유»가 있고 아래 근거가 있을 때만 별도 요청이다(없으면 채택으로 재분류).

| 유형 | 근거(항목 자기 `파일:행`) | 가는 곳 |
|---|---|---|
| 라우트 URL | 정리가 페이지·fragment 라우트 URL 을 바꾼다 — `파일:행` 이 `urls.py` 의 `path(` 행이거나 템플릿 `{% url %}` 이름이 바뀌어야 한다 | `/dddjango-web:dddjango-web` 기능 요청(동작 변경) |
| API 계약 | `web/client/<bc>/` 파일이고 그 행이 호출 경로·필드 소비를 정의한다 | «/dddjango로 발주» |
| HTMX 응답 계약 | view 가 반환하는 fragment 템플릿·`HX-*` 헤더를 바꿔야 한다 | 기능 요청 |
| 경계 교차 | 편집할 파일이 범위 밖(다른 영역 · `plan.md` «경계 교차» 목록의 정적 파일) | 그 단위의 리팩토링 실행 |
| web/ 밖 | 편집할 파일이 web/ 밖(settings·application 등 — 테스트 파일의 경로 치환은 해당 없음 §7) | «/dddjango로 발주» |

## 5. 도구 — web 판 `refactor_audit.py`

### 5-1. 갈래 비교

| 갈래 | 모양 | 비용 | 위험 | 판정 |
|---|---|---|---|---|
| (A) dddjango `refactor_audit.py` 를 web 에서 쓴다 | web 프로필(렌즈·경로·rulepack 없음 모드)을 dddjango 도구에 더함 | 3~4일 + dddjango 봉인·미러 연쇄 | ① web 은 독립 플러그인이다 — dddjango 미설치 사용자에게 도구가 없다(설치본 경로도 다름) ② 도구의 빼는 출구 검사가 전부 rulepack `blocks`·`norm_kind`·`overrides` 에 서 있다(`Corpus` `:304-440`) — web 은 온톨로지 밖이라 web rulepack 을 새로 만들어야 한다(새 장치 최대) | 걷음 |
| (B) web 전용 최소 도구 | `dddjango-web/scripts/refactor_audit.py`(표준 라이브러리 · Codex byte 미러) — 하위 명령 이름·산출 파일은 dddjango 와 같게, rulepack 결속 대신 문장 단위 어구 검사 | 2~3일 | 코드 일부(정규화·절 경계·문장 분할·표 파싱·verdict 파싱·residual 골격)가 두 플러그인에 복제된다 — 배포 단위가 달라 공용 import 는 불가. 드리프트는 각 도구의 자가 시험·러너 사례가 각자 막는다 | **고름** |
| (C) 도구 없음 | 리뷰어 표·verdict 를 `refactor-scope.md` 와 Coordinator 판단으로만 운영 | 0일 | 결정 1-b «증명 책임은 빼는 쪽»의 기계 관문이 사라진다 — 제외·오탐·별도 요청이 모델 규율에만 걸린다. 인용 실재도 기계로 안 본다(dddjango R-T2 에서 7행 중 1행이 위치 표기로 불일치 — `check` 가 잡아 재인용). 잔존 M_m 의 «근거 없는 해소» 차단도 없다 | 걷음 |

- (B) 를 고른 근거: 빼는 출구(범위 축소)를 막는 관문이 결정 1-b·18 의 핵심이고, 그 관문은 규범 문면 대조라 사람·모델 규율로 갈음할 수 없다. 반면 dddjango 도구를 web 에 걸면 web 이 온톨로지로 끌려 들어간다(AGENTS «전 파일 산문 정본» 위반). (B) 는 이미 검증된 dddjango 도구의 **계약(하위 명령·산출 파일·exit)을 그대로 두고**, rulepack 의존부만 문면 규칙으로 바꾼다.
- **outline 은 두지 않는다**: 리뷰어·architect 가 Read/Grep 을 가진다. dddjango `outline`(AST 정의 목록)은 교차 파일 발견 보조였는데, web 의 교차 관계는 템플릿 include·static 참조라 `plan.md` 의 범위·경계 교차 목록이 그 몫을 한다. 행동 시험에서 교차 파일 누락이 보이면 그때 더한다.

### 5-2. 하위 명령 (대상 프로젝트 루트에서 · Coordinator 만 돌린다)

| 하위 명령 | 입력 → 출력 | 계약 |
|---|---|---|
| `plan <단위> --debt <debt-g0.json> --out <audit>` | 단위 → 범위 파일(단위 + 전속 정적 — 규칙 이름·근거) · 경계 교차 목록 · 범위 안 `C<n>` 목록 · 렌즈 × 조각 · 점검 절 목록 · `HEAD` · `범위 미커밋 변경 N` → `plan.md` | 단위가 6a 단위 목록 밖·부재면 exit 1 |
| `check <audit>` | 리뷰어 표 행마다 ① 인용이 그 문서 §절 본문에 있다(dddjango 와 같은 `normalize` — 강조·백틱·인용 머리·공백류 제거) ② `파일:행` 이 작업 트리에 실재하고 범위 안이다 → `check.md`(통과 행 + 인용 불일치 목록과 사유) | 문서 경로 사상: Claude `skills/<x>/…` · `agents/<n>.md` · `commands/dddjango-web.md` ↔ Codex `skills/<x>/…` · `dddjango-web-<n>/SKILL.md` · `dddjango-web/SKILL.md`. 인용은 그 플랫폼 설치본에서 찾는다 — 의미 미러에서 못 찾으면 불일치(fail-closed · 채택 쪽) |
| `sections <audit>` | 인용된 절과 반대 방향 절의 **절 전체 원문** + 적용 범위 규범 원문(Coordinator «리팩토링 모드» 절에서 읽음) + 적용 한정 어구·허용 표지 목록 → `sections.md` | 절 = 그 제목부터 같은 수준 이상 다음 제목 전까지 |
| `check-verdict <audit> [--feedback <파일>] [--final]` | 아래 §5-3 → `verdict-log.md` append · `요약:` 1행 | exit 0 · 2(red) · 1 |
| `residual <산출물 폴더> [--finalize <시각>]` | §8 → `residual/<시각>/review-<렌즈>.md` 묶음 · 결과 확정 | exit 0 · 2 · 1 |
| `subst-check <기준 커밋> <대상 커밋> --pairs <명세 슬라이스 0 절 경로>` | web/ 밖 변경 파일마다 «치환만» 대조(§7-2) | exit 0 · 2 · 1 |
| `--self-test` | 점검 절 실재 · 경로 사상 · 어구 상수 = 규범 문면 | exit 0 · 2 |

- 공통: `--platform claude|codex`(기본: 자기 위치로 판별) · `--plugin-root`. 모든 하위 명령이 `요약:` 1행을 낸다.
- `refactor-scope.md` 는 6a `src/debt.py` 의 `parse_scope` 를 import 해 읽는다(§6 — 파서 한 곳).

### 5-3. `check-verdict` — rulepack 없는 빼는 출구 검사 (증명 책임은 빼는 쪽 · fail-closed)

- 공통: 통과 행마다 판정 1개 · `M<n>` 유일 · 재실행에서 기존 `M<n>` 유지.
- **문장**: dddjango 와 같은 분할(`다.`·`.`+공백·목록 머리·표 칸·원숫자·빈 줄) — 인용이 걸친 문장 전부가 «인용이 든 문장»이다.

| 출구 | 필수 근거 | 검사 |
|---|---|---|
| **제외** | `<문서> §<절> «인용»` | ① 인용이 그 절에 실재한다 ② 근거가 **리뷰어의 «반대 방향 규칙» 열**이거나, 인용이 든 문장에 **허용 표지**(닫힌 목록 — `예외`·`허용`·`해도 된다`·`하지 않아도 된다`·`무방`·`에 한해`·`만 적용` · 목록 전수는 계획) 가 있다 ③ 인용이 든 문장에 **적용 한정 어구**(§9 닫힌 목록)가 없고, 인용이 적용 범위 규범 문단 자신이 아니다 ④ 제외 인용 구간이 위반 행 인용 구간과 겹치지 않는다 |
| **오탐**(요건 불충족 포함) | 위반으로 인용된 **같은 절**의 요건 문구 인용 | 인용 ⊂ 위반 행의 인용 절 · 인용이 든 문장에 적용 한정 어구가 없다 |
| **별도 요청** | 리뷰어 «아니오 — 사유» + 유형 근거(§4-4) | «아니오» 없으면 채택 재분류 · 유형별 근거 검사(`urls.py path(` 행 · `web/client/` 경로 · 범위 밖 파일 · web/ 밖 파일) |
| **병합** | 대상 ID | M → M: 대상은 채택 `M<k>` 뿐 · M → C: 리뷰어가 그 행에 «`C<n>` 과 같음»을 적었을 때만 |
| **사용자 판단** | 반대 방향 규칙 인용 | 반대 방향 인용이 든 문장에 적용 한정 어구가 없고 적용 범위 규범 자신이 아니다(결정 18 이 이미 가른 충돌은 묻지 않는다) |

- dddjango 대비 약해진 곳과 그 보정: rulepack `norm_kind`(Permission/Exception) 대신 «반대 방향 열 또는 허용 표지»를 쓴다. 표지가 없는 문장을 근거로 한 제외는 red → 1회 재호출 → 채택이다(fail-closed). 표지 목록이 좁으면 채택이 늘 뿐 제외가 새지 않는다.
- **대리 출처 축소 검사**: R3 재실행 입력 파일 첫 줄의 «결정 출처» 정형이 대리 출처인데 채택 → 제외·오탐·병합으로 줄면 red(dddjango `--feedback` 과 같다).

## 6. G0 기록 정형 확장 — M 항목 행

- 러너 파서(`src/debt.py` `_ROW_RE`)는 `ⓐ 키`·`요구 키`·`재상정 키` 만 읽고 값은 `C<n>` 만 받는다(다른 값 exit 1). M 항목은 **별도 행**으로 둔다:
  - G0·G0 재승인 절: `의미 ⓐ 키: <M<n> 공백 구분 | ->`(리팩토링 모드에서만 · 한 번).
  - `ⓐ 재상정` 절: `의미 재상정 키: <M<n> …>`(M 항목 재상정일 때).
- **파서 한 곳**: `parse_scope` 가 두 행을 함께 수집하도록 `_ROW_RE` 를 넓힌다(`의미 ⓐ 키`·`의미 재상정 키`) — 값 검사는 이름별 정규식(`C[1-9]\d*` / `M[1-9]\d*`). `--debt-residual` 의 `residual_sets` 는 C 행만 접고(동작 무변), web `refactor_audit.py residual` 은 같은 `parse_scope` 결과에서 M 행을 같은 순서 접기(마지막 `## G0` 부터 · 재상정 빼기 · 재승인 되살림)로 읽는다. 6a 픽스처는 무변이어야 한다.
- 리팩토링 G0 절의 `요구 키:` 는 `-` 다(기능 요구가 없다). `ⓐ 키:` 는 `C<n>` ⓐ.
- 배너 1행(dddjango 끝 절 G0 판형): `검사기 빚 N_c건(미룰 수 없음 k) · 의미 채택 N_m건 · 사용자 판단 u건 · 별도 요청 j건 · 제외 x건 · 오탐 d건 · 병합→C b건 · 인용 불일치 q건 · 규칙 근거 없는 불편 f건` + 슬라이스 0 규모 1행. 빚 질문은 `C<n>`·`M<n>` 에 ⓐ/ⓑ 만(ⓐ′ 없음). 별도 요청·제외·오탐·병합→C·인용 불일치·근거 없는 불편은 목록 파일 경로와 건수로 표시(질문 아님 · 계수는 `verdict-log.md` 마지막 exit 0 판).
- 사용자 판단 항목은 G0 질문이다(«위반으로 보고 정리 / 허용으로 보고 뺌» · 대리 불가). 수정 요청(게이트 피드백)으로 R3 를 다시 돌릴 때는 «판정 근거 오류 지적»만 받는다.
- 정리할 것 0(C ⓐ 후보 0 · M 채택 0)이면 G0 정지(`## G0 정지` · 사유 «정리 대상 없음»).

## 7. 슬라이스 0 · 동작 보존

### 7-1. 흐름

- Phase 1: design-architect-web 슬라이스 0 명세(C·M ⓐ 키마다 파일 계획 · 개명·이동 쌍 · 삭제 파일 · **web/ 밖 테스트 치환 파일**) → design-review-web(G1 설계 모드) → discipline-reviewer-web 경량 점검(필수 — 6a `:189`) → G1. 파견 입력에 `모드 리팩토링` · `M<n>` ⓐ 목록(규칙 인용 포함) · 적용 범위 규범 원문을 싣는다 — 슬라이스 0 에는 ⑴ 만 풀리고 ⑵ 는 그대로다.
- Phase 2: 슬라이스 0 만(`slices[0]` = `slice-0-debt` · 기능 슬라이스 없음). coder-web 입력 = 6a 슬라이스 0 호출 그대로 + `M<n>` ⓐ 목록 + 적용 범위 규범 원문.
- **끝 green**(6a 셋 + 하나 · 리팩토링 모드와 기능 요청 공통으로 고친다):
  1. `py_compile` + `manage.py check` 베이스라인 대비 신규 0.
  2. `--debt-residual` 요약 `ⓐ 잔존` 0.
  3. 개명·이동 참조 완전성(`git grep` exit 1) — **web/ 밖 파일이 걸리면**(현장: tests/web 68파일이 web 모듈 84개 import) 그 파일은 §7-2 치환으로 고치고 `subst-check` exit 0 을 함께 요구한다.
  4. **기존 프로젝트 테스트**: Phase 2 진입 준비 ④에서 check 베이스라인과 함께 프로젝트의 기존 테스트 명령(프로젝트 설정에서 읽음 — 예: `pytest` 설정·`manage.py test`)을 1회 돌려 **실패 목록 베이스라인**을 기록하고, 슬라이스 0 끝에 다시 돌려 **새 실패 0**. 테스트를 고치거나 보태지 않는다(결정 14 — 경로 치환만 예외 §7-2). 명령이 없거나 돌릴 수 없으면 «미실행 + 사유»를 G2 배너에 적는다(green 조건이 아니라 표면화 — houserules `final.md:107` «적용 가능한 검사»).
- 5번 규율 감사(`discipline-reviewer-web`)는 R2 조각 단위로 나눠 부를 수 있고(`plan.md` 재사용), 마지막 홀리스틱은 조각 리포트 종합과 조각 경계 교차 항목만 본다.

### 7-2. web/ 밖 테스트 파일 — 치환만 허용 [도출 · 결정 9 · 1-d · 17]

- `coder-web.md:75`(«web/ 밖 코드를 절대 수정하지 않는다»)에 예외 1구를 둔다: «슬라이스 0 에서 명세 슬라이스 0 절이 적은 web/ 밖 **테스트 파일**의 옛 경로 → 새 경로 문자열 치환만 한다». 근거: 그 경계의 이유는 백엔드 격리(WI)이고, 테스트 파일의 참조 문자열 치환은 백엔드 코드를 바꾸지 않는다. 테스트의 판정·단언은 바꾸지 않는다(결정 14).
- 대상 판정: 테스트 파일 = 프로젝트 테스트 설정이 수집하는 경로(현장 `tests/`) 아래 파일. 그 밖의 web/ 밖 파일은 여전히 금지다(§4-4 «web/ 밖» 별도 요청).
- **`subst-check`**: `git diff -U0 <기준>..<대상> -- <web/ 밖 변경 파일>` 의 파일마다 — 더한 줄들에서 명세 쌍의 새 꼬리를 옛 꼬리로 되돌리면 지운 줄들과 **같다**(순서 포함), 그리고 web/ 밖 변경 파일은 모두 테스트 경로 안이다. 아니면 exit 2 와 어긋난 줄. 꼬리 규칙은 6a 참조 완전성과 같다(`static/` 접두 제거 · `.py` 는 점 경로도).
- 기능 요청의 슬라이스 0 에도 같은 규칙이다 — 6a W-T1r2 가 현장 `tests/test_settings_profiles.py:131·148`(이미지 옛 파일명 URL 문자열)을 찾아 «설계 단계에서 확인»으로 넘겼다. 지금 규범대로면 그 개명은 참조 완전성 red → 재상정 STOP 이다.

## 8. G2 — M = M_c + M_m

- **M_c**: `--debt-residual`(`debt-g0.json` `mode` 로 같은 의미론 재스캔) 요약의 `ⓐ 잔존`.
- **M_m**: `refactor_audit.py residual <폴더>`
  - 결정적 바닥: `의미 ⓐ 키` 항목의 `파일:행` 목록 파일이 `git_snapshot` 이후 바뀌지 않았으면 잔존(무변 = 미해소).
  - 그 밖 항목: 렌즈별 묶음 `residual/<시각>/review-<렌즈>.md`(항목 행 + 슬라이스 0 개명 쌍) → 원 렌즈 리뷰어를 «단위 점검 — 잔존 확인»으로 한 번씩 부른다(입력 = 묶음 + 최종 코드). 결과 표를 `result-<렌즈>.md` 에 쓰고 `residual <폴더> --finalize <시각>` 으로 확정한다 — 새 `파일:행` 근거 없는 «해소»는 잔존.
- **M > 0**: 해당 항목만 슬라이스 0 을 1회 재개봉(coder-web) → 끝 green 재확인 → 5번 감사(반송 diff)·백스톱·`residual` 재실행. 그래도 M > 0 이면 `ⓐ 재상정` STOP(처분 «별도 요청 | 출처 있는 ⓑ | 플러그인 결함 | 작업 중단» · C 는 `재상정 키:` · M 은 `의미 재상정 키:`).
- **G2 배너**: 6a 빚 3행을 `G0 ⓐ N건 중 잔존 M(M_c · M_m) · 재상정 제외 K건 · legacy 잔존 L · G0 에 없던 키 X` 로 바꾸고, 제외·오탐·별도 요청·병합→C·인용 불일치 다섯 목록을 다시 표시한다. 시각 대조는 §2-2(수정 전 렌더 보존본과 전후 대조).
- 백스톱 diff 게이트(`--diff-base`)는 그대로 돈다 — 개명·이동의 새 경로 발견은 여기서 잡힌다(6a 두 게이트 짝).

## 9. 적용 범위 규범 (web Override 문단)

- Coordinator «리팩토링 모드» 끝 절에 문단 1개(web 은 산문 정본 — R-ID·`djr:overrides` 없음):
  - ⑴ «리팩토링 모드의 단위 점검과 그 슬라이스 0 은 표준을 대상 범위(단위 + 전속 정적 파일)의 기존 코드 전체에 적용한다. 규범의 신규·touched·이번 작업·신규 단위·새 파일 적용 한정과 기존 코드·레거시·브라운필드 형태의 보존·면제·존중 조항은 기능 요청의 범위 규범이라 이 점검과 그 슬라이스 0 에는 적용하지 않는다.»
  - ⑵ «리뷰어의 diff·touched 한정 관찰, 구현 표기 열람 금지(design-review-web), 수정 모드 touched 한정 감사 조항은 단위 점검(점검과 잔존 확인)과 그 판정에서만 적용하지 않는다. 슬라이스 0 의 리뷰와 감사는 이 조항을 그대로 따른다.»
  - 끝에 «외부에서 보이는 동작(페이지·fragment 라우트 URL · API client 가 소비하는 계약 · HTMX 응답 · 렌더 결과) 보존 규범은 그대로다 — 리팩토링도 동작 불변이다. 이 규범과 이 규범이 푸는 규범은 단위 점검 항목을 빼는 근거가 되지 않는다.» + 적용 한정 어구 닫힌 목록 «…».
- **적용 한정 어구 분류 원칙**(전수 분류는 계획): web 문면(커맨드·에이전트 4·스킬 5 의 SKILL·references)의 적용 한정 어휘(진단 2-2 실측 — touched 6 · 신규 단위 7 · 새 파일 6 · 레거시 18 · 브라운필드 12 · legacy 12 · 기존 코드 12 · 이번 작업 3 · added 3 줄)를 줄마다 셋으로 가른다 — T(적용 조건을 한정하는 문장 → 목록 어구 후보) · N(외부 계약·동작 보존 · 절차 · 무관) · T*(두 몫 — 풀리는 몫만). 어구는 **결합형**으로만 싣는다(맨 낱말 «기존·신규·새·레거시»는 싣지 않는다 — dddjango 40항목 판정과 같은 원칙 · 판정 단위는 인용이 든 문장).
- **파견 입력에 원문 · 에이전트 1행**: Coordinator 가 리팩토링 모드의 모든 파견 입력(리뷰어 2종 단위 점검 · R3 `sections.md` · 슬라이스 0 의 architect·리뷰어·coder·DR)에 규범 원문을 싣는다. 파견 받는 에이전트 4개의 모드 무관 위치에 «파견 입력에 적용 범위 규범이 실려 있으면 그 규범이 정한 몫과 때를 따른다» 1행. 곁 문면은 두지 않는다(dddjango N-M2 와 같은 이유).
- **«리팩터링 대상 = 백스톱 위반» 류 사본**: web 문면에서 같은 한정(«검사기가 내지 않는 관행·의미 정리 → 리팩토링 입구» — houserules SKILL `:15` · final §8 `:217`)은 이미 리팩토링 입구로 보내는 문장이라 고칠 것 없음. 계획에서 전수 grep 으로 확인한다.
- **드리프트 방지**: `refactor_audit.py --self-test` 가 어구 상수 = 규범 문면 «…» 를 대조한다(`verify-web` 경로). dddjango `rulepack_smoke` 라벨 식 같은 전수 드리프트 검사는 두지 않는다(web 은 R-ID 가 없고, 새 범위 어구는 web 수리 절차의 구현 리뷰가 본다).

## 10. 문면 갱신 — 6a 가 남긴 10곳 · 그 밖

| # | 위치 | 할 일 |
|---|---|---|
| 1 | Claude Coordinator `:128` | `<대상>` = 단위 경로 표기 안내 · 입구 실재 |
| 2 | 같은 파일 `:151` ⓐ′ | 대가 줄 «ⓐ′ 이 요청은 G0 정지하고 정리 착륙 뒤 다시 시작한다» 에 «(의미 점검 포함)» 1구 |
| 3 | houserules SKILL `:15` | 무변 확인(의미 정리 → 입구 — 입구 실재로 참이 됨) |
| 4 | houserules final §8 `:217` | 무변 확인 · 리뷰어 점검 절 목록에 §8 사전 포함(§4-2) |
| 5 | REQUEST_GUIDE §6 끝(`:205-207`) | 입구 사용법 문단 — dddjango §6 판형(`dddjango/REQUEST_GUIDE.md:163-183`): 대상 단위 · 불편 서술 · 동작 불변 · 기존 테스트 안전망 · 축소 지시 불복 · 여러 단위는 단위마다 |
| 5′ | REQUEST_GUIDE §7 | 대리 경로 문장: `/dddjango-web:dddjango-web 리팩토링 모드(입구 /dddjango-web:refactor) · 대상: <단위>`(따옴표 불요 — `요청 원문` 줄) |
| 6~10 | Codex 대응 5곳 | 같은 정정의 의미 미러 · REQUEST_GUIDE byte 미러 |
| + | `README.md:318` · `AGENTS.md:24` | «커맨드 1» → «커맨드 2(메인 + 리팩토링 입구)» · 스크립트 목록에 `refactor_audit.py` |
| + | `Makefile` verify-web | `refactor_audit.py --self-test` · 러너 사례 · byte 미러 대조에 새 파일 포함(기존 `diff -rq` 가 잡는지 계획에서 확인) |

- 봉인: `Makefile` 을 고치면 6a 와 같이 `manifest_seal.py --write` → feat → 재발행 chore.
- «6b 착륙 전 push 금지»는 이 작업의 커밋으로 풀린다(push 는 로드맵 9 릴리즈).

## 11. 행동 시험 (web 수리 절차 · 실하네스 = 6a 하네스 · 현장 `--shared` 사본 · 무거운 실행은 하나씩)

| # | 요청·상태 | 합격 |
|---|---|---|
| W6-T0 | `/dddjango-web:refactor web/static/images` | Skill 1회 성립(거부 0) · args = 표지 원문 · Coordinator 전문 적재(끝 절 끝 문장) · `요청 원문` 줄로 리팩토링 모드 판별 · 폴더 `…-refactor-static-images` · R1 `--refactor` · `plan` · R2 파견 · G0 배너 도달(C 3 · M 은 파일명 해시 접미 후보) |
| W6-T1 | 표지 손상(`리팩토링 모드(입구 /dddjango-web:refactor) 대상 web/home`) | «표지 손상» 정지 · 폴더 0 |
| W6-T2 | 대상 없음 / 두 단위 / 단위 안쪽 경로 / 기능 혼입 불편 서술 | 입구 정지 · 사용법 안내 · 폴더 0 |
| W6-T3 | `/dddjango-web:refactor web/home` 실하네스 R2~R3 | 범위 = home + 이름·참조 전속 정적 파일 · 렌즈 2 × 조각 · `check` 통과(불일치는 재인용) · `check-verdict` exit 0 · 배너 계수 1행 · `home.html:13` 다른 영역 section include 가 채택 또는 «별도 요청 — 경계 교차»로 나옴 · 비용·벽시계 기록 |
| W6-T4 | 러너: `--debt-scan --refactor` | 합성 legacy core·골격 미비 단위 → 키 증가 · 기본 스캔 대조 무변 · `--debt-residual` 이 `mode` 를 따름 · 6a 픽스처 55 무변 |
| W6-T5 | `plan` 결정 규칙(현장 사본) | consultation 에 `conversation.js`·`conversation.css` 이름 전속 · `toast.js` 경계 교차 · 무참조 파일 정적 단위 몫 |
| W6-T6 | `check-verdict` 사례(러너) | 표지 없는 문장 근거 제외 red · 어구 문장 근거 제외 red · 반대 방향 열 근거 제외 통과 · 규범 문단 자신 인용 red · 구간 겹침 red · 오탐 다른 절 red · «아니오» 없는 별도 요청 → 채택 재분류 · 대리 출처 축소 red · `--final` 채택 기록 |
| W6-T7 | `residual` 사례(러너) | 무변 파일 결정적 잔존 · 근거 없는 해소 → 잔존 · 재상정 제외 · 재상정 뒤 재승인 되살림 |
| W6-T8 | `subst-check` 사례(러너) | 치환만 green · 단언 변경 red · 테스트 밖 web/ 밖 파일 red |
| W6-T9 | 6a 기능 요청 슬라이스 0 책상 재생(W-T9 판형) — 이미지 개명 + `tests/test_settings_profiles.py` 치환 | 참조 완전성 exit 1 · `subst-check` exit 0 · 치환 없이는 red |
| W6-T10 | G0 정지 재개 — 범위 무변 → audit 재사용 · 범위 파일 1줄 변경 → 새 점검 | 두 갈래 |
| W6-T11 | 회귀: 6a W-T2 요청(`/dddjango-web:dddjango-web` 기능 요청) | 일반 모드 · `요청 원문` 줄 무해 · 6a 흐름 그대로 |
| W6-T12 | 관찰: 맨 프롬프트 «설정 화면 안내 문구 섹션 추가해 줘»(슬래시 없음) | 암묵 호출 여부 **기록만**(D1 대가 · 합격 기준 아님) |
| W6-C | Codex `$dddjango-web-refactor web/home` | 얇은 스킬이 형제 SKILL 끝까지 읽음 · 리팩토링 모드 · 같은 질문 지점(R2 파견 또는 G0) |

- 비용 추정: W6-T3 실 R2~R3 약 $20~40(home 영역 · 렌즈 2 × 조각 1~2 — dddjango R-T0 $83(파견 8)에서 외삽). consultation 은 시험에 쓰지 않는다($40~65 추정).

## 12. 작업량 [추정 · 플러그인 개발 작업일]

| 몫 | 일 |
|---|---|
| 입구 Claude·Codex · disable 제거 · `요청 원문` 1행 · 모드 판별 문단 | 0.5 |
| Coordinator 끝 절 «리팩토링 모드»(R0~G2 · Override) + Codex 의미 미러 | 1.5~2 |
| 에이전트 4(단위 점검 모드 ×2 · 판정 모드 · coder 치환 예외 · 모드 무관 1행) + 역할 SKILL 미러 | 1~1.5 |
| `refactor_audit.py` web 판(plan · check · sections · check-verdict · residual · subst-check · self-test) + 러너 사례 | 2.5~3 |
| 러너 `--refactor` · `parse_scope` M 행 · 픽스처 | 0.5~1 |
| 적용 한정 어구 전수 분류(web 문면) | 0.5 |
| REQUEST_GUIDE §6·§7 · README · AGENTS · Makefile · 봉인 | 0.5 |
| 행동 시험(실하네스 · Codex 1 · 러너) · 구현 리뷰 · verify-web | 1.5~2 |
| **합계** | **약 8.5~11일** |

## 13. 열린 물음

- **사용자 결정이 필요한 물음 0.** 도출로 처리한 것(이의가 있으면 뒤집는다):
  1. 인자 보정 = `요청 원문: $ARGUMENTS` 1행(따옴표 갈래 걷음 — §1-1 근거 ①~③).
  2. 도구 = web 전용 최소 도구(B)(§5-1 — 결정 1-b 관문 · web 산문 정본 원칙). outline 은 두지 않음.
  3. implementation-ui 배정: §3·§5·§8·§9 → screen 렌즈 · §4·§6·§7 → discipline 렌즈 · §1·§2 제외(결정 12 (가) · 절 성격).
  4. 전속 정적 파일 = 참조 전속 ∪ 이름 전속 · 다영역은 경계 교차(§3-1 — 결정 18 · 슬라이스 정의 `:203` · dddjango 타 BC 규칙).
  5. 리팩토링 스캔의 면제 해제 범위 = WP1·WP2 legacy 면제 + WS5 전 단위 · WP5 motion.js 면제 유지(결정 18 · 플러그인 갱신 사안).
  6. web/ 밖 테스트 치환 허용을 기능 요청 슬라이스 0 에도 적용(결정 9 · 17 · 6a W-T1r2 현장 사례).
  7. 슬라이스 0 끝 «기존 프로젝트 테스트 새 실패 0» — 명령이 없으면 미실행 표면화(houserules `:107` · 결정 14).
  8. step 3(계약)·step 5(시안) 생략 · G2 시각 확인 = 수정 모드 수정 전 렌더 보존본 대조(`:237`).
- **적대 검토에 부탁할 곳**: §5-3 허용 표지 목록이 제외를 새게 하는가 · §3-1 이름 전속이 공용 파일을 영역에 잘못 넣는가 · §6 `parse_scope` 확장이 6a 판정을 바꾸는가 · §7-2 `subst-check` 의 «순서 포함 동일»이 다중 치환 줄에서 거짓 red 를 내는가 · `요청 원문` 줄이 기능 요청 판별(표지 오탐)에 영향을 주는가.
