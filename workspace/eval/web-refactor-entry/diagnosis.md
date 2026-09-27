# 로드맵 6b 진단 — dddjango-web 리팩토링 입구 (2026-09-27)

> **요지**
> 1. **입구 기계**: [실측] Claude 스파이크 1회에서 얇은 입구가 낸 Skill 위임을 하네스가 거부했다. 원인은 web Coordinator 의 `disable-model-invocation: true` 다. Coordinator 는 0자 적재됐고, 표지 줄은 args 에 원문 그대로 실렸다. dddjango 선례의 입구 모양은 web 에서 그대로 서지 않는다. Codex 에는 막는 장치가 없어 선례 모양이 그대로 선다 [추정 — 동형].
> 2. **모드의 일**: 대상은 6a 단위 1개(ⓐ′ 가 이미 약속함)와 그 단위 화면 사슬의 전속 정적 파일이다. 빚은 6a 러너 검사기 빚(브라운필드 면제 해제)과 리뷰어 2종의 단위 전체 의미 점검, architect 판정으로 잡는다. 6a 장치 가운데 G0 기록 정형·슬라이스 0·참조 완전성·재상정·G2 빚 행은 그대로 쓴다. 새로 만들 것은 입구·모드 판별·점검/판정 모드·웹판 인용·판정·잔존 도구(산문 정본이라 R-ID 가 없다)·M 항목 기록 행이다.
> 3. **동작 보존**: 새 장치는 필요 없다. 기존 확인(참조 완전성·`manage.py check`·백스톱·영향 범위 브라우저 확인·감사·G2 육안·houserules «기존 프로젝트 검사 실행»)이 현장에서 난 web 결함 유형을 모두 덮는다. 새로 드러난 쟁점은 하나다. web/ 밖 테스트가 옮길 web 모듈을 import 하는데(현장 tests/web 68파일 · web 모듈 84개), coder-web 은 web/ 밖을 고칠 수 없다.
> 4. **현장**: 검사기 빚은 3키(WN8)다. 브라운필드 면제를 풀어도 3키 그대로다. 의미 빚은 표본 5영역에서 후보 7종이 나왔다(수십 건 규모 추정). web «정리 요청» 발주는 0건이다.
> 5. **결정 후보 1개**: Claude 입구 방식 — web Coordinator 의 `disable-model-invocation` 을 걷을지(D1).

- 기준: 플러그인 = 이 저장소 작업 트리(HEAD `c9fcadff` · dddjango-web 1.1.25). 현장 = spring_dream_server main `012e7a99c`. 원본에는 `git log/show/grep/ls-tree/status` 만 썼다. 실행은 scratch `git clone --shared` 사본(`…/scratchpad/6b-diag/sds`)에서만 했다.
- 표기: [실측] = 명령·실험 결과 · [추정] = 확인하지 않은 판단 · [도출] = 기존 결정·플러그인 정의에서 답이 나와 질문하지 않는 것(이의가 있으면 뒤집는다 · 사용자 결정 기록이 아니다).
- Serena·Graphify 미사용 · 서브에이전트 0 · 모델 호출은 스파이크 1회뿐이다.

---

## 1. 입구 기계 (물음 1)

### 1-1. web Coordinator 에 `disable-model-invocation: true` 가 붙은 경위 [실측]

| 사실 | 근거 |
|---|---|
| web Coordinator 는 처음 생길 때부터 이 줄을 가졌다. dddart 커맨드 frontmatter 를 본떴다(dddart 에도 이 줄이 있다). 사유를 적은 기록은 없다. | `bca51105`(08-23 «W2~R3 — 에이전트 4종·커맨드…») · `workspace/design/2026-08-23-dddart-analysis-A-command-agents.md:8` |
| dddjango Coordinator 는 같은 줄을 08-05 에 걷었다. | `7718407f`(08-05 «feat: allow implicit Claude invocation» · `dddjango/commands/dddjango.md` −1행) |
| 요청 가이드 점검(09-26)은 «유지(바꾸면 비결정성↑)»를 **권고**했다. 사용자 결정 기록(§7 D-G1~G3·B1)에는 이 항목이 없다. | `workspace/plan/2026-09-26-request-guide-audit/synthesis-v2.md:19` · `:77-84` |
| 비용으로 드러난 사례가 하나 있다. 이 줄 때문에 A8 의 «확인하고 수정해» 류 일반 프롬프트가 파이프라인을 통째로 우회했다. 그래서 자동 적재 스킬에 강제 문구를 넣어 메웠다(1.1.21). | `workspace/design/2026-09-16-web-component-identity-enforcement.md:87` |
| Codex web Coordinator 에는 암묵 호출 차단이 없다(`agents/openai.yaml` 에 `policy` 없음). 이미 Claude 와 Codex 가 비대칭이다. | `codex-dddjango-web/skills/dddjango-web/agents/openai.yaml` |

### 1-2. 하네스 판정 규칙 [실측 — Claude Code 2.1.283 바이너리 판독]

- Skill 도구 검증 함수(`BVt`)는 이 순서로 본다. `if(e.disableModelInvocation && !userTypedThisTurn) → reason "disable_model_invocation" · errorCode 4`
- `userTypedThisTurn` 은 이번 턴의 사용자 메시지(메타 제외)에 정규식 `(?<!\S)/<그 스킬 이름>(?=$|\s)` 가 있을 때만 참이다. 사용자가 친 것은 `/dddjango-web:refactor` 이고 `/dddjango-web:dddjango-web` 이 아니다. 그래서 거짓이다.
- 거부 메시지에는 «Do not replicate this skill's workflow by other means — it is reserved for explicit user invocation» 이 들어 있다. 하네스가 우회 적재를 명시적으로 막는다는 뜻이다(→ 1-5 (라)).
- 이름 인자 치환(`uEe`): `arguments:` 가 있으면 args 를 셸식으로 토큰화하고(`qhr` → `Qd`, 실패하면 공백 분할), `$<이름>` 에는 **그 위치의 토큰 하나**를 넣는다. `$ARGUMENTS` 에는 원문 전체가 들어간다. 이름 치환이 한 번이라도 일어나면 `ARGUMENTS:` 꼬리를 붙이지 않는다.

### 1-3. 스파이크 1회 [실측]

- 구성: scratch 에 `dddjango-web/` 작업 트리를 복사하고(`6b-diag/plug/dddjango-web`) `commands/refactor.md` 를 더했다. 입구는 dddjango 선례와 같은 판형이다. frontmatter 는 `disable-model-invocation: true` 와 `allowed-tools: Skill(dddjango-web:dddjango-web)` 이고, 본문 표지는 `리팩토링 모드(입구 /dddjango-web:refactor) · 대상: $ARGUMENTS` 다.
- 명령: 현장 사본 `sds` 에서 `claude -p --output-format stream-json --verbose --no-session-persistence --model sonnet --max-turns 6 --settings '{"enabledPlugins":{"dddjango-web@changja88-dddjango":false}}' --plugin-dir <사본> "/dddjango-web:refactor web/home"`. 16:28:06~16:28:26 · 2턴 · $0.17. 원시 기록은 `6b-diag/spike1.jsonl` 이다.

| 관측 | 값 |
|---|---|
| 격리 | init `plugins` 에 설치본 dddjango-web 없음 · 사본만 적재(`dddjango-web@inline 1.1.25`) · `slash_commands` 에 `dddjango-web:refactor` 있음 · permissionMode auto |
| 위임 | Skill 1회 `{"skill":"dddjango-web:dddjango-web","args":"리팩토링 모드(입구 /dddjango-web:refactor) · 대상: web/home"}` |
| 판정 | `is_error=true` — «Skill dddjango-web:dddjango-web cannot be used with Skill tool due to disable-model-invocation. Ask the user to run /dddjango-web:dddjango-web themselves … Do not replicate this skill's workflow by other means» |
| Coordinator 적재 | **0자**(전문 적재 불성립) |
| 표지 줄 | args 에 원문 그대로 실렸다(1/1). 치환 뒤 Coordinator 까지는 가지 못했다. |
| 권한 | `permission_denials: []` — 거부는 권한이 아니라 검증 단계에서 났다 |
| 끝 | 모델이 «직접 `/dddjango-web:dddjango-web` 을 입력해 주세요»로 끝냈다 · 사본 작업 트리 변화 0 |

판정: **dddjango 선례의 «얇은 입구 → Skill 위임»은 web 에서 불성립한다.** 로드맵 5 스파이크에서 run1 이 성공한 것은 대상(dddjango Coordinator)에 disable 이 없었기 때문이다(`spike-5-entry-mechanics.md:11`).

### 1-4. 위임이 열려도 남는 인자 문제 [실측 판독 + 추정]

- web Coordinator 는 `arguments: [feature, api_url]`(`dddjango-web/commands/dddjango-web.md:4`)와 `빌드할 화면: $feature`(`:15`)를 쓴다. 따옴표 없는 표지를 args 로 넘기면 `$feature` 에는 `리팩토링` 이, `$api_url` 에는 `모드(입구` 가 들어간다. 나머지는 치환 본문에서 사라진다(1-2).
- 사용자가 슬래시로 직접 치면 모델은 `<command-args>` 원문도 본다 [추정]. 그래서 기존 기능 요청의 무따옴표 사용(README:108)은 영향이 작았다(가이드 점검 F19 «영향 작음»). 반면 Skill 위임 경로에서는 모드 판별이 «요청 첫머리의 정확한 표지»를 읽을 곳이 잘린다.
- 그래서 입구가 표지를 따옴표로 감싸 넘기거나, Coordinator 에 `요청 원문: $ARGUMENTS` 1행을 두고 모드 판별이 그 줄을 읽게 해야 한다. 대리 경로(`/dddjango-web:dddjango-web <표지>` 를 직접 치는 경우)도 같은 문제를 안는다.

### 1-5. 갈래 (Claude)

| 갈래 | 모양 | 비용 | 위험 |
|---|---|---|---|
| **(가) web Coordinator 의 disable 을 걷는다** | dddjango 와 같은 모양. 얇은 입구 → Skill 위임 | frontmatter −1행 + 1-4 보정 1행(`$ARGUMENTS` 줄 또는 따옴표) · 입구 파일 1 · 0.3일 [추정] | web Coordinator 를 모델이 부를 수 있게 된다(Claude 전 세션 · 설명문이 스킬 목록에 실림). 현장 근거: dddjango 는 08-05 부터 모델 호출이 가능했지만, 맨 이름 발주 10/10 이 실제로는 명시 ns 로 들어왔다(암묵 발화 관측 0 · synthesis-v2:19). A8 사례(1-1)에서는 이 변화가 오히려 파이프라인 우회를 막는 쪽이다. 권고했던 «비결정성↑»는 실측이 없다. |
| **(바) 생성 사본 입구** | `commands/refactor.md` = Coordinator 본문 사본. frontmatter 에서 `arguments` 를 빼고, `:15` 는 표지 + `$ARGUMENTS` 로, `:17-19` 인자 설명은 바꾼다. 슬래시 확장이라 Skill 검증을 타지 않는다. | 생성 스크립트 1 + 본문 동일성 검사(verify-web) + 픽스처 · 0.5~1일 [추정] · 배포본 +136KB | 사본 드리프트. `verify-web` 이 `make verify` 자동 경로 밖이라(`Makefile:23-26`) 재생성을 잊으면 release 전까지 못 잡는다 → release-web 전 검사에 넣어야 한다. web 이 «전 파일 산문 정본»에서 «생성물 1개 있음»으로 바뀐다(AGENTS.md:24). Codex 는 영향 없다. |
| (바″) 입구 본문의 `!` 셸 삽입으로 Coordinator 를 끼워 넣음 | `` !`sed … commands/dddjango-web.md` `` | 0.3일 | 136KB 출력이 셸 출력 상한에서 잘릴 수 있다 [추정 · 미실측]. `${CLAUDE_PLUGIN_ROOT}` 29곳을 sed 로 직접 치환해야 한다. frontmatter 가 본문에 섞인다. 권하지 않는다. |
| (다) 안내만 하는 입구 | 입구가 «`/dddjango-web:dddjango-web "리팩토링 모드(입구 …) · 대상: …"` 를 치세요»를 출력하고 끝난다 | 입구 1 + 문면 10곳의 «입구가 받는다 → 안내한다» 정정 · 0.3일 | 사용자가 두 번 치고, 표지를 손으로 따옴표까지 옮겨야 한다(1-4). 표지 손상 fail-closed 가 자주 걸린다 [추정]. 결정 13 이 고른 «입구» 경험이 사라진다. |
| (라) 입구가 Coordinator 를 Read 로 적재 | 5A 의 B-1 | 0.3일 | 하네스가 금한 «other means» 우회의 취지와 충돌한다(1-2). 136KB 를 25k 토큰 상한으로 읽으려면 6회 이상 나눠 읽어야 하고, 5A 에서 부분 적재(1~83행)가 관측됐다. `${CLAUDE_PLUGIN_ROOT}` 29곳과 `$feature` 가 치환되지 않는다. 입구 allowed-tools 가 Coordinator 도구 12종을 복제해야 한다. 권하지 않는다. |
| (마) 입구 안에 리팩토링 절차를 따로 둠 | 독립 리팩토링 Coordinator | G0·슬라이스 0·G2 장치의 절반 이상을 복제해야 한다 · 3일+ | 두 Coordinator 드리프트. 권하지 않는다. |

- 남는 갈래는 (가)와 (바)다. 둘 다 적재 보장·치환·도구 권한이 dddjango 선례와 같다. 가르는 것은 «web 메인 커맨드를 모델이 부를 수 있게 둘까» 하나다. 결정 1-d «진행 방식은 dddjango 와 동일하게»는 진행 방식에 관한 결정이고, 호출 정책까지 정하지는 않는다. 그래서 이 하나만 결정 후보로 올린다(§6 D1).

### 1-6. Codex 대조 [실측 파일 + 추정]

- 선례: `codex-dddjango/skills/dddjango-refactor/SKILL.md` 는 형제 `../dddjango/SKILL.md` 를 `wc -l` 로 잰 뒤 구간으로 나눠 끝까지 읽는다. 요청 첫 줄은 `리팩토링 모드(입구 $dddjango-refactor) · 대상: <인자>` 이고, `agents/openai.yaml` 은 `allow_implicit_invocation: false` 다. 로드맵 5 행동 시험의 Codex R-T0 에서 끝 행(210~237)까지 읽기가 성립했다(`behavior-tests-step5.md:29`).
- web: `codex-dddjango-web/skills/dddjango-web/SKILL.md` 는 297행 · 140,268 bytes 다(dddjango Codex 263행 · 141,687 bytes 와 비슷하다). 인자는 위치 인자가 아니라 «요청 문장에서 화면 요구를 추린다»(`:16`)라서 1-4 문제가 없다. 암묵 호출 차단은 형제 스킬에 없고, 읽기는 막히지 않는다.
- 판정: `codex-dddjango-web/skills/dddjango-web-refactor/{SKILL.md, agents/openai.yaml}` 를 dddjango 판형 그대로 두면 선다 [추정 — 동형 · Codex 스파이크 미실시]. 행동 시험 때 Codex R-T0 동형 1회로 확인한다.

---

## 2. web 리팩토링 모드의 일 (물음 2)

### 2-1. 대상 단위

- [도출] **대상 = 6a 단위 1개.** 단위 목록은 `web/<area>/` · `web/static/<하위>/` · `web/design_system/` · `web/base/` · 컨테이너 `web/*.py` · `web/client/<bc>/` 다(`dddjango-web/commands/dddjango-web.md:148`). ⓐ′ 가 이미 «단위별 정리를 `/dddjango-web:refactor`로»라고 약속했다(`:151`). 현장의 검사기 빚 3키는 모두 `web/static/images/` 에 있다. 그래서 영역만 받으면 ⓐ′ 가 가리키는 정리를 한 번도 할 수 없다. 현장 단위 수는 영역 8 · static 하위 5 · design_system · base · 컨테이너 · client BC 9 = 25다 [실측].
- [도출] **점검 범위 = 대상 단위 + 그 단위 화면 사슬의 전속 정적 파일.** 플러그인 정의상 화면의 기능 JS·HTMX 선언은 그 화면 사슬 슬라이스에 속한다(`:203` 슬라이스 2 = view + 템플릿 + section·widget + 기능 JS·HTMX 선언 include·외부 로드 + urls). 결정 18 은 «대상 전체»다. 정적 파일이 단위 밖에 따로 사는 web 트리에서 영역만 보면 가장 큰 의미 빚을 놓친다.
- 현장의 정적 파일 소유 분포 [실측 — 템플릿의 `{% static 'web/…' %}`·include 참조로 셈]:
  - 42개 가운데 30개는 한 영역만 참조한다. auth 5 · base 12 · chart 4 · consultation 1 · design_system 1 · employee_choice 2 · preferences 4 · related_persons 1.
  - 9개는 여러 영역이 함께 쓴다(`toast.js` 는 3영역, 나머지는 2영역). 3개는 템플릿 참조로 잡히지 않는다.
  - 참조만으로는 모자란 경우가 있다. `conversation.js`(3,332행)는 consultation 화면 기능인데 `base.html:40` 이 전역으로 로드해서 참조상 «base 소유»로 잡힌다. 그래서 전속 판정 규칙은 설계에서 정해야 한다(참조 + 화면 어휘 이름). 여러 영역이 쓰는 파일은 그 static 단위 실행의 몫이다. 영역 실행에서는 «경계 교차» 표시로 둔다(dddjango «타 BC 근거» 규칙에 대응).

### 2-2. 단계 대조 — dddjango «리팩토링 모드»(`dddjango/commands/dddjango.md:69` · `:222-247`) ↔ web

| dddjango | web 에서 | 6a 재사용 | 새로 필요 |
|---|---|---|---|
| 모드 판별: 정확한 표지 · 재개 실행 줄 `모드 리팩토링` · 표지 손상 fail-closed · 단조성 · R2·R3 축소 지시 불복(`:67`·`:69`) | web 모드 판별 절(`:120-130`)에 4번째 모드로 문단을 더한다. 재개 표지는 실행 줄이 아니라 `build-state.json` `mode` 값이다(web 에는 «실행·앵커» 개념이 없다 — 6a 설계 v5 가 이식을 걷었다, `web-g0-debt/design-v5.md:316`). | 정리 요청 입구 정지(`:128`) · «따르지 않는 지시» 목록(`:128`) | 판별 문단 · build-state `mode: refactor` |
| R0 대상 BC 1개 · 부재/복수/기능 혼입 → 입구 정지 | 대상 단위 1개(2-1) · 같은 정지 | 단위 정의(`:148`) | 단위 이름 해석(`web/static/images` 류 경로 표기) |
| R0′ `refactor-<bc>` 폴더 · 실행 선택(잇기/승인됨/폐기) | `.dddjango-web/<생성일>-refactor-<단위 케밥>` · 잇기는 build-state phase 로 판단 | 폴더 확정·`build-state` 생성(`:144`) | 리팩토링 폴더만 후보로 보이는 규칙 |
| G0 정지 재개(audit 재사용 — BC 무변·새 파일 0·check-verdict 0) | 같은 조건을 «단위 + 전속 정적 파일»에 건다 | `## G0 정지` 절(`:156`) | 재사용 조건 검사(도구) |
| R1 27종 · `C<n>` | `--debt-scan` 을 단위로 거른다. **리팩토링 모드에서는 브라운필드 면제를 풀어야 한다**(결정 18 — legacy htmx core 위치·로드 태그, 기존 단위 골격 미비 WS5. motion.js 판형은 플러그인 갱신 사안이라 남긴다). 현장 영향은 0이다(§4-2). | 러너 스캔·JSON 동결·`C<n>`(`src/debt.py:116-158`) | `--debt-scan` 리팩토링 변형(면제 해제 + WS5 전 단위) · 픽스처 |
| R2 리뷰어 4렌즈 `BC_AUDIT` × 조각(`refactor_audit.py plan`) | design-review-web(architecture-web 렌즈) + discipline-reviewer-web(cleancode·houserules·JS)의 «단위 점검 모드». implementation-ui 규범은 지금 판정하는 리뷰어가 없다(적재 에이전트는 coder-web 뿐) → 결정 12 (가)를 web 에 적용해 리뷰어에게 배정한다 [도출]. 조각 크기의 예: consultation 은 영역 3,186행 + 전속 정적 파일(conversation.css 3,243 · conversation.js 3,332)로 약 9.8K행이다. | — | 두 에이전트 점검 모드 절 · 렌즈·조각 계획 |
| R2′ 인용 검사(`check` — rulepack R-ID·블록 해시) | web 은 산문 정본이라 R-ID 가 없다. 인용 = `<스킬>/<파일> §N` + 인용문이고, md 원문과 정규화 대조한다(`refactor_audit.normalize` 와 같은 정규화). dddjango 도구는 rulepack 에 묶여 있어 그대로 못 쓴다(`dddjango/scripts/refactor_audit.py:69-96` 렌즈·`application/<bc>/` 고정). | — | 웹판 도구(plan·outline·check·check-verdict·residual) |
| R3 design-architect «의미 항목 판정» + `check-verdict`(빠지는 출구 4종) | design-architect-web «의미 항목 판정» 모드 + 웹판 check-verdict | — | architect 모드 절 · 도구 |
| 적용 범위 규범 ⑴⑵ + 한정 어구 52 | web Override 문단. web 문면의 적용 한정 어휘는 줄 수로 touched 6 · 신규 단위 7 · 새 파일 6 · 레거시 18 · 브라운필드 12 · legacy 12 · 기존 코드 12 · 이번 작업 3 · added 3 이다 [실측 grep — 중복 포함 · 대상 목록은 설계에서 분류]. ⑵ 에는 design-review-web 의 «구현 표기는 보지 않는다»(`agents/design-review-web.md:59`)가 든다. | — | Override 문단 · 한정 어구 목록 |
| G0: 배너 계수 1행 · C/M ⓐ/ⓑ · ⓐ′ 없음 · 사용자 판단 항목(대리 불가) · 별도 요청·제외·오탐 목록 | 같다 | 결정 출처·충돌·dirty+ⓐ·기록 정형 `## G0`(`:151-156`) | **M 항목 행** — 러너의 `ⓐ 키:`·`재상정 키:` 는 `C<n>` 만 받는다(`src/debt.py:192-198` · 다른 값은 판정 불가 exit 1). `의미 ⓐ 키:` 같은 별도 행이 필요하다. |
| Phase 1~2: 슬라이스 0 만 · 0T/0C 창 + behavior_guard | 슬라이스 0 만. web 에는 플러그인 테스트가 없어 0T 가 없다. 6a 슬라이스 0 그대로에 M 항목 계획을 더한다. | architect 슬라이스 0 절 · DR 경량 점검 필수(`:189`) · coder-web 슬라이스 0 규칙(`agents/coder-web.md:57`) · 끝 green(`:211`) | 감사를 조각 단위로 나누는 판형 |
| G2: M = M_c + M_m · residual → 리뷰어 잔존 확인 · 반송 1회 → 재상정 STOP | M_c = `--debt-residual`(`:217`) · M_m = 웹판 residual | 빚 3행 · `ⓐ 재상정` 절(`:191`) · diff 게이트 | M_m 판정 · 재상정 행 확장 |
| 대리: 입구는 사용자만 · 대리는 메인 커맨드에 표지를 넣어 시작 | 같다. 단 web 대리 경로는 표지를 **따옴표로 감싸야** 한다(1-4). | — | REQUEST_GUIDE §7 문장 |

### 2-3. 의미 점검 — 결정 1·18 을 web 에 적용

- [도출] 결정 1-a·1-b·1-d·18(가)에 따라 리뷰어가 단위 기존 코드 **전체**를 web 표준으로 본다. 판정은 design-architect-web 이 하고, 사용자는 G0 에서 승인한다. 기능 요청 쪽은 지금처럼 의미 점검을 하지 않는다.
- [도출] 대상 규범은 dddjango-web 자신의 스킬 5종이다(architecture-web · discipline-web-houserules · discipline-cleancode · implementation-ui · implementation-javascript). 결정 12 의 «web 102»는 dddjango 쪽 `implementation-django-web` 규범이다(`diag-5B-bc-audit-mode.md:69`·`:227`). 독립 플러그인인 dddjango-web 은 이것을 적재할 수 없으므로 들여오지 않는다.

### 2-4. 6a 장치 — 그대로 / 고쳐서 / 새로

- **그대로 (10)**: 빚 스캔 러너와 JSON 동결 · `refactor-scope.md` 절 머리 4종과 기록 정형 · 결정 출처 규칙 · 충돌·dirty+ⓐ · build-state `slice-0-debt` · coder-web 슬라이스 0 규칙 · 참조 완전성 `git grep` · DR 경량 점검의 슬라이스 0 두 항목 · `ⓐ 재상정` 절 · G2 빚 3행.
- **고쳐서 (4)**:
  - `--debt-scan` 리팩토링 변형(면제 해제·단위 필터).
  - 정형 행에 M 항목.
  - ⓐ′ 대가 줄에 «의미 점검 포함» 1구. dddjango `:82` 에는 있고 web `:151` 에는 없다.
  - 정리 요청 안내 문구를 입구 방식(D1)에 맞춘다.
- **새로 (7)**:
  - 입구(Claude·Codex).
  - 모드 판별 문단과 끝 절 «리팩토링 모드».
  - 리뷰어 2종 단위 점검 모드와 잔존 확인.
  - architect 판정 모드.
  - web Override.
  - 웹판 도구.
  - REQUEST_GUIDE §6 입구 문단과 §7 대리 문장.

---

## 3. 동작 보존의 web 판 (물음 3)

### 3-1. «밖에서 보이는 동작»은 플러그인이 이미 정의했다

- `agents/coder-web.md:57`: 슬라이스 0 은 «밖에서 보이는 렌더·동작과 페이지·fragment 라우트 URL 이 바뀌지 않는다(정적 자산 경로는 참조를 함께 치환하면 바뀌어도 된다)».
- web 안전망 정의: `skills/discipline-cleancode/SKILL.md:29`(«동작 보존 안전망은 py_compile·`manage.py check`·결정적 백스톱·사용자 육안») · `references/final.md:2389`(생성 앱 영구 테스트 없음) · `discipline-web-houserules/references/final.md:107`(«기존 프로젝트의 적용 가능한 검사는 함께 실행한다»).

### 3-2. 표면별 현재 확인

| 표면 | 리팩토링이 바꿀 수 있는 경로 | 이미 있는 확인 | 빈 곳 |
|---|---|---|---|
| 페이지·fragment 라우트 URL | 화면을 영역 사이로 옮길 때 영역 include 접두가 바뀜 | coder-web:57 규범 · 영향 범위 브라우저 확인(`:213`·`:242`) · 현장 tests/web 는 이름으로 고정(`reverse(` 330회 · 경로 리터럴 web 1건 [실측]) | path 문자열 기계 대조 없음. dddjango 결정 8 도 URL 표면을 뺐다(«새는 것이 나오면 그때 더한다»). |
| 렌더 HTML·DOM(클래스·data-attr·문구) | VM 분할·section 재배치·템플릿 이동 | 수정 모드 «구현 첫 편집 전 수정 전 구현 근거 보존»(`:237`) · 3-1 영향 범위 렌더·브라우저 확인 · DR 최종 감사 · G2 사용자 육안 · 현장 tests/web(DOM·JS 하네스 단언 — `test_conversation_ui_behavior.py` 9,400행+) | 전후 기계 대조 없음 — 결정 17 로 제외 |
| HTMX 응답·헤더 | view 분할 | 같음 | 같음 |
| 정적 자산 경로 | WN8 개명 | 참조 완전성 `git grep`(`:211`) | 저장소 밖 소비자 — 알려진 것 0 [추정]. 현재 nginx `StaticFilesStorage` 이고 해시 이름이 없다(발주서 `2026-09-27-fortune-employee-6-2-1-media-url-upload.md:55-57` [실측]). 다만 web 그림을 CDN 주소로 내는 저장소가 들어오는 중이다(`framework/test/unit/test_cdn_image_static_files_storage.py` — HEAD 에 있음). |
| CSS 외형 | 리터럴 → 토큰 치환 | G2 육안 · clip·focus(판단 자료) | 토큰 값 = 원 리터럴 기계 확인 없음(감사 몫) |
| JS 동작 | 기능 파일 분할·정리 | 3-1 UI 동작 증거 · DR 점검 8번 | — |

### 3-3. 현장 증거 — web 결함은 어디서 잡혔나 [실측 — 현장 `git log -- web` 174커밋 중 «회귀·깨짐·fix» 계열 제목]

- `a1af4fbee`: 다른 레인이 공용 부품 `glass_button.html` 을 지워 intake 에서 `TemplateDoesNotExist` 가 났다. 삭제 파일 참조가 남은 사례로, 6a 참조 완전성 `git grep`(삭제 포함)이 잡는 유형이다.
- `b07567507`(CSRF include `only` → 403) · `ea63513f8`(«None» 리터럴 렌더): 둘 다 레인 안 렌더 스모크·육안이 잡았다. 3-1 브라우저 확인 유형이다.
- `0479fb87c`(tokens.css `}` 유실 → 토큰 전부 미적용): 머지 사고이고 다음 레인의 브라우저 검증이 잡았다.
- 리팩토링이 G2 를 지나 새어 나간 web 사례는 0건이다. web 정리 레인 자체가 없었다(§4-5).

### 3-4. 판정

- [도출] **새 동작 보존 장치를 만들지 않는다.** 근거는 결정 8(마 — 새는 것이 나오면 더함) · 14(기존 테스트 충분 가정 · 새 장치 없음) · 17(개명·치환만 기계 확인 · 렌더 전후 대조와 tests/web 채택 없음) · 플러그인 정의(3-1)다. 현장에서 난 유형은 모두 기존 확인이 덮는다(3-3).
- [도출] 리팩토링 모드의 슬라이스 0 끝 green 에 **기존 프로젝트 테스트 실행 결과**(베이스라인 대비 새 실패 0)를 명시한다. houserules `final.md:107` 을 구체화하는 것이다. 테스트를 고치거나 보탤 일은 없다(결정 14). 현장 tests/web 는 한 번에 1,615 passed 규모다(현장 커밋 `7e52044c2` 메시지).
- 한 가지 주의: 리팩토링 모드는 영향 범위가 넓다. `design_system`·`base`·`static/css` 대상이면 영향 범위 확인(`:242`)이 현장 화면 12개 전부가 된다. 장치가 아니라 G2 비용 문제다.
- **새 쟁점 — web/ 밖 테스트의 옛 경로 참조** [실측]
  - 6a 참조 완전성 `git grep … -- web '*.py' …` 의 `'*.py'` 는 저장소 전체와 맞는다. 예로 conversation VM 모듈이나 `conversation_mount.html` 을 옮기면 tests/web 5파일이 걸린다.
  - 현장 tests/web 는 68파일이 web 모듈 84개를 import 하고, 템플릿 경로 문자열 27종을 쓴다.
  - 그런데 coder-web 은 «web/ 밖 코드를 절대 수정하지 않는다»(`agents/coder-web.md:75`). 지금 규범대로면 그런 이동은 참조 완전성 red → 재상정 STOP 이다.
  - [도출] 결정 9(정의 본문이 같을 때 이름 치환 허용 — «준수율을 높이는데 좋을거 같아»)와 1-d 에 따라, web/ 밖 **테스트 파일**에는 옛 경로 → 새 경로 치환만 허용한다. coder-web:75 의 근거는 백엔드 격리(WI)이고 테스트에는 해당하지 않는다. 치환만 했는지는 결정 17 의 틀(치환만 기계 확인)로 본다 — 테스트 diff 의 새 줄을 새→옛으로 되돌리면 지운 줄과 같아야 한다. `git diff` 1줄 명령 또는 작은 검사 · 0.5일 [추정].

---

## 4. 현장 실측 (물음 4)

### 4-1. 6a 러너 `--debt-scan` [실측]

- 명령: `python3 dddjango-web/scripts/backstop.py <sds> --debt-scan --json 6b-diag/debt-g0-head.json`
- 결과: exit 2 · **키 3 · 발견 3 · 스캔 파일 358** · 0.9초.
- C1~C3 = WN8 `web/static/images/{chunmong-logo-v2,cloud-ornament,gold-blossom}.png`(kebab). 6a 진단 때(`495128e26`)와 같다.
- 곁 관찰: 표준 이름은 `<이름>_<내용hash>.<확장자>` 다(houserules `final.md` §4 `static/images/` 행). WN8 은 snake_case 만 본다. 리팩토링에서 해시 접미는 의미 점검 몫이다.

### 4-2. 결정 18 적용(브라운필드 면제 해제) 모사 [실측]

- scratch 사본에서 빈 트리 커밋을 `--diff-base` 로 주었다(모든 파일이 added · 모든 단위가 신규 → WS5 가 전 단위를 본다 · legacy 면제 없음). `backstop.py <sds> --diff-base <빈 커밋>` 구조 발견은 **3건(WN8)으로 그대로**다. 시안 16건은 과거 빌드 증거라 결정 16 으로 빚 밖이다.
- 현장에서는 면제 해제가 검사기 빚을 늘리지 않는다. 기존 단위는 골격이 모두 완비됐고, core 는 표준 위치(`web/static/htmx/htmx.min.js`)다.

### 4-3. 의미 빚 표본 [실측 수치 · 위반 여부는 추정 — 판정은 리뷰어·architect 몫]

| 영역(표본) | 후보 | 규범 근거 | 수치·위치 |
|---|---|---|---|
| consultation | VM 과대·긴 함수 | cleancode §3·§9 | `conversation_view_model.py` 1,606행 · 40행 넘는 함수 8(`_make_state` 124행 `:841` · `_function_card` 123행 `:1426` · `render_authenticated` 93행 `:214`) — web 전체에서 40행 넘는 함수 16/523 중 8 |
| consultation·base | 화면 기능 JS 의 base 전역 로드 | undecidable-web §6(`:63` 페이지 전용 기능 로드는 그 페이지 scripts block) | `base.html:40` `conversation.js`(3,332행 · 함수 153 · IIFE 1개 — 기능당 한 파일 판단도 필요) |
| home | 다른 영역 section include | architecture-web `final.md:101` 수평 격리 · section = 화면 전속 | `home.html:13` → `consultation/conversation/section/conversation_mount.html`(web 전체에서 1건) |
| preferences | view 안의 판단 | architecture-web `final.md:65`·`:69` «view 는 진입점뿐 — 판단 금지» · implementation-ui `final.md:63` | `preferences_view.py:28-66` — 라우트 이름으로 3갈래 분기 · SameSite 값 검증과 쿠키 삭제(`:54-56`) |
| chart | CSS 간격·크기 리터럴(tokens.css 밖) | houserules SKILL §3 레드 플래그 «생 색·간격 리터럴»(WP4 는 색만 본다 — `check_purity.py:268-277`) | `chart.css` px/rem 리터럴 238(gap 61 · padding 28+ · height 21) · 다른 파일은 components 121 · signup 32 · employee_choice 30 · password_reset 21 · login 16 |
| (전체) | 템플릿 계산 필터 | houserules §5⑥(템플릿은 state 만) | `|add` 11 · `|yesno` 11 · `|slugify` 2 · `|safe` 2 — 표시 판정 분기(`{% if … == '…' %}`)는 0 |
| static/images | 해시 없는 파일명 | houserules §4 | 3개 전부 |

- 추정 규모: 영역마다 수 건~십수 건씩, 25단위 합계 수십 건이다 [추정]. 검사기 빚 3키보다 한 자릿수 이상 많다. dddjango R-T0 는 BC 1개에서 BC_AUDIT 8다발 · 54행 · 항목 41건 · 약 $83 · 35분이었다(`behavior-tests-step5.md:30`·`:51`). web 영역 1개는 렌즈 2~3 × 조각 1~2 = 2~6다발이다. 가장 큰 consultation(약 9.8K행)은 비용을 $40~65 로 외삽한다 [추정].

### 4-4. 현장 tests/web [실측]

- 79파일 · `def test_` 986개(6a 진단 때 927개). 1,615 passed 규모다.
- web 모듈 import 는 68파일 · 84모듈이고, 템플릿 경로 문자열은 27종이다. `reverse(` 는 330회, 경로 리터럴 web GET 은 1건이다. 정적 URL 을 고정한 시험도 있다(`test_conversation_view.py:1183` «/static/web/files/wonbo.png» — 발주서 6-2-1 `:59`).

### 4-5. web «정리 요청» 사례 [실측]

- 현장 발주서 중 dddjango-web 을 언급하는 113개와 web 발주·GATE 파일에서 «리팩터·리팩토링·구조 정리·정리만·동작 유지·품질만»을 grep 했다. web 정리만 하는 요청은 **0건**이다. 동작 유지가 나온 곳은 기능 발주 안의 보존 조건뿐이다(`2026-09-08-web-login-fidelity.md:47`).
- 사용자 방침(09-26): «리팩토링 자체는 다른 프로젝트에서 진행할거야 … 1서비스 발주, 2책공장 일정까지만»(`2026-09-25-web-8b3-teller-detail-sheet-tabs.md:7`). 캠페인 계획은 web·tests/web 를 BC 리팩터의 **동결 소비자**로 둔다(`workspace/plan/2026-09-26-refactor-campaign/plan-v2.md:44-45`). web 리팩토링 착수 시점은 정해지지 않았다.
- 플러그인 쪽 시험 사례: 6a W-T3 «홈 화면 코드 구조만 정리» → 입구 안내 후 정지에 합격했고, 입구 파일이 없음을 스스로 알렸다(`workspace/eval/web-g0-debt/behavior-tests.md:10`).

---

## 5. 6a 가 6b 몫으로 남긴 문면 (물음 5) [실측 grep]

| # | 위치 | 문면의 약속 | 6b 가 해야 할 것 |
|---|---|---|---|
| 1 | `dddjango-web/commands/dddjango-web.md:128` | 정리 요청은 `/dddjango-web:refactor <대상>` 이 받는다 · 빚 스캔 전에 안내하고 정지 · 섞인 요청은 G0 배너에 «의미 정리는 `/dddjango-web:refactor`» 1행 | 입구 실재 · `<대상>` 표기(단위 이름) 안내 · D1 이 (다)면 «받는다 → 안내한다» 정정 |
| 2 | 같은 파일 `:151` | ⓐ′ «단위별 정리를 `/dddjango-web:refactor`로 먼저 진행(이 요청은 G0 정지 · 착륙 뒤 다시 시작)» — 빚 단위가 2개 이상일 때 | 입구가 **6a 단위**(`static/images` 포함)를 받아야 하고, 그 실행이 그 단위 검사기 키를 없애야 한다(재시작 스캔이 0). 대가 줄에 «의미 점검 포함» 1구를 더한다(dddjango `:82` 대칭) |
| 3 | `dddjango-web/skills/discipline-web-houserules/SKILL.md:15` | 검사기가 내지 않는 관행·의미 정리 → 리팩토링 입구 | 의미 점검이 실재해야 한다(R2·R3) |
| 4 | 같은 스킬 `references/final.md:217`(§8) | 교정 사전의 대부분(views.py 누적·forms.py·전역 templates·CBV·context dict·inline JS·리터럴·무네임스페이스 static) → 리팩토링 입구(Claude/Codex 두 표기) | 리뷰어 점검 절이 §8 사전을 대상에 넣어야 한다 |
| 5 | `dddjango-web/REQUEST_GUIDE.md:205-207`(§6 끝 문단) | 모양·동작은 두고 기존 코드만 정리 = 입구 · 정리만 요청하면 안내 후 정지 | 입구 사용법 문단(6a impl-log:25 «6b 가 쓴다»). dddjango §6 판형(`dddjango/REQUEST_GUIDE.md:163-183`)을 따른다. 대상 단위 · 불편 서술 · 동작 불변 · 기존 테스트 안전망 · 축소 지시 불복을 담는다. §7 대리 문장은 따옴표 표지다(1-4) |
| 6~10 | Codex 대응: `codex-dddjango-web/skills/dddjango-web/SKILL.md:150`·`:173` · `…/discipline-web-houserules/SKILL.md:14` · `…/references/final.md:217` · `codex-dddjango-web/REQUEST_GUIDE.md:205-206`(byte 미러) | `$dddjango-web-refactor` | 얇은 스킬 `dddjango-web-refactor/` 실재 · 같은 정정의 의미 미러 |

- 파일 8개 · 자리 10곳이다(review-Q-impl:194 «8개 파일이 참조하는데 아직 없다»). 지금 배포본에 넣으면 존재하지 않는 입구를 가리킨다. 그래서 «6b 착륙 전 push 없음» 조건이 살아 있다(`web-g0-debt/plan-v2.md:3`).
- 그 밖에 갱신할 곳: `README.md:318`(«커맨드 1») · `AGENTS.md:24`(«커맨드 1 +») · `claude plugin validate dddjango-web --strict`.

---

## 6. 결정 (물음 6)

### 6-1. 질문 생략 — 도출 [도출 · 이의가 있으면 뒤집는다]

1. 입구 이름·표지·Codex 트리거 = `/dddjango-web:refactor` · `리팩토링 모드(입구 /dddjango-web:refactor) · 대상: …` · `$dddjango-web-refactor`(결정 13 (가) · 1-d).
2. 대상 = 6a 단위 1개, 점검 범위 = 단위 + 화면 사슬 전속 정적 파일(2-1 — ⓐ′ 약속 · 결정 18 · 슬라이스 정의 `:203`). 여러 단위는 단위마다 실행하고, 리팩토링 G0 에는 ⓐ′ 가 없다(dddjango 와 같음).
3. 점검 = design-review-web + discipline-reviewer-web 단위 점검 모드 · 판정 = design-architect-web · 사용자 G0 승인(결정 1-b · 1-d). implementation-ui 규범은 리뷰어에게 배정한다(결정 12 (가) · 1-d).
4. 적용 범위 Override 를 web 문면에 둔다. 브라운필드 면제를 리팩토링 스캔에서 해제한다(결정 18 (가) — 현장 영향 0).
5. 정리할 것 0 → G0 정지 · 사용자 판단 항목은 대리 불가 · 결정 출처 규칙 그대로(dddjango 와 같음).
6. 동작 보존에 새 장치를 두지 않는다. 기존 프로젝트 테스트는 그대로 실행한다(3-4 · 결정 8·14·17 · houserules:107).
7. web/ 밖 테스트의 옛 경로는 치환만 허용하고, 치환인지를 기계로 확인한다(3-4 · 결정 9 · 1-d).
8. ⓐ′ 대가 줄에 «의미 점검 포함»을 넣는다(1-d · dddjango `:82`).

### 6-2. 결정 후보

**D1 — Claude 입구: web Coordinator 의 `disable-model-invocation` 을 걷을까**
- 실측: 걷지 않으면 얇은 입구 위임은 하네스가 거부한다(스파이크 1/1 · Coordinator 0자).
- (가) 걷는다: dddjango 와 같은 입구 · 변경 2행 · 0.3일. 대가 — Claude 모든 세션에서 모델이 web Coordinator 를 스스로 부를 수 있다. dddjango 는 08-05 부터 이 상태이고 암묵 발화 관측은 0이다(맨 이름 발주 10/10 이 명시 호출). Codex web 은 이미 이 상태다. A8 에서는 오히려 일반 프롬프트의 파이프라인 우회를 막는다.
- (바) 사본 입구: 호출 정책은 그대로다 · 0.5~1일 · 배포본 +136KB. 대가 — Coordinator 를 고칠 때마다 재생성해야 한다. 동일성 검사를 release-web 에 넣어야 한다(verify-web 은 자동 경로 밖). web 이 산문 정본 원칙에서 생성물 1개를 예외로 갖게 된다.
- 둘 다 1-4 인자 보정이 필요하고, 적재·치환·권한은 같다.

---

## 7. 작업량 추정 [추정 · 플러그인 개발 작업일]

| 몫 | (가) 기준 | 비고 |
|---|---|---|
| 입구 Claude·Codex + 1-4 보정 | 0.3~0.5 | (바)면 +0.5 |
| Coordinator 모드 판별 문단 + 끝 절 «리팩토링 모드» + Codex 의미 미러 | 1.5~2 | 산문 정본이라 온톨로지 비용 0 |
| 리뷰어 2종 단위 점검·잔존 확인 모드 · architect 판정 모드 · web Override · 역할 SKILL 미러 | 1.5~2 | |
| 웹판 도구(plan·outline·check·check-verdict·residual — md 인용 대조) + 러너 사례 | 2~3 | dddjango 도구(1,362행)보다 작다. rulepack·블록 결속이 없다 |
| 러너 `--debt-scan` 리팩토링 변형 · M 행 · 픽스처 | 0.5~1 | |
| web/ 밖 테스트 치환 확인 | 0.5 | |
| REQUEST_GUIDE §6·§7 + byte 미러 · README·AGENTS | 0.5 | |
| 행동 시험(실하네스 R-T0 동형 — 대상 `web/home` 또는 `web/static/images` · Codex 동형 1) · 구현 리뷰 · verify-web | 1.5~2 | |
| **합계** | **약 8.5~11.5일** | 선례: 로드맵 5 계획 17~19일(그래프 비용 포함) · 6a 설계 4.5~6.5일 |

## 8. 원시 기록 (scratch · 커밋 밖)

`/private/tmp/claude-501/-Users-hyun-Desktop-dddjango/ed01792c-e467-4a58-a794-ed16237ffb9e/scratchpad/6b-diag/`

- `spike1.jsonl` — 스파이크 stream-json.
- `plug/dddjango-web/` — 입구를 더한 사본.
- `sds/` — 현장 `--shared` 사본(작업 트리 변화 0).
- `debt-g0-head.json` — 빚 스캔 동결.
- `all.txt` — `--all` 출력.
- `allnew.txt` — 면제 해제 모사 출력.
