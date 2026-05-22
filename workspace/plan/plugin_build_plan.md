# dddjango 플러그인 재구축 계획

## 전제

- 이 계획은 `100% 성공 보장 계획`이 아니다. 모델 출력, 외부 runner, 권한 정책, 런타임 캐시는 변동 가능하다.
- 이 계획의 목적은 `성공하지 않았는데 완료라고 말하지 못하게 하는 것`이다.
- 완료는 선언하지 않는다. 완료는 현재 파일 기준 검증 산출물로만 인정한다.
- 현재 유지 대상은 `dddjango/` 플러그인 본체와 `workspace/reference/` source reference다.
- 현재 재구축 목표는 Codex 플러그인이다. 다른 런타임 호환성은 이번 P0-P8 완료 조건에서 제외한다.
- P8까지는 local/private Codex plugin을 기준으로 한다. 공개 배포, 원격 marketplace, 다른 런타임 지원은 별도 계획 없이는 완료 조건으로 삼지 않는다.
- 기존 평가 시스템은 신뢰하지 않는다. 새 평가 시스템은 P4에서 mini-bucket fixture로 먼저 검증한다.

## 출처 Ledger

| 출처 | URL | 조회일 | 이 계획에서 쓰는 범위 | 금지된 확대 해석 |
|---|---|---|---|---|
| OpenAI Codex Customization - Skills | https://developers.openai.com/codex/concepts/customization#skills | 2026-05-22 | skill 구조, progressive disclosure, `SKILL.md`, optional `scripts/`, `references/`, `assets` | dddjango 도메인 규칙의 근거로 사용 금지 |
| OpenAI Codex Agent Skills | https://developers.openai.com/codex/skills | 2026-05-22 | skill discovery, `agents/openai.yaml`, progressive disclosure 보조 확인 | plugin manifest 또는 dddjango 도메인 규칙의 근거로 사용 금지 |
| OpenAI Codex Build Plugins | https://developers.openai.com/codex/plugins/build | 2026-05-22 | `.codex-plugin/plugin.json`, plugin root 구조, Codex marketplace/cache 개념 | 다른 런타임 manifest 규칙으로 사용 금지 |
| OpenAPI Specification | https://spec.openapis.org/oas/v3.2.0.html, https://spec.openapis.org/oas/latest | 2026-05-22 | REST/HTTP API contract source 기준. 실행 시점에는 version-pinned URL을 우선한다. | DDD, DB transaction, Django ORM, pytest/TDD 기준으로 사용 금지 |
| OpenAI Evaluation Best Practices | https://developers.openai.com/api/docs/guides/evaluation-best-practices | 2026-05-22 | eval objective, dataset, metrics, run/compare, continuous evaluation 분리 | 특정 dddjango 점수 체계의 정답으로 사용 금지 |
| Google Testing Blog - Just Say No to More End-to-End Tests | https://testing.googleblog.com/2015/04/just-say-no-to-more-end-to-end-tests.html | 2026-05-22 | 큰 E2E보다 작고 원인 격리가 쉬운 피드백 루프 우선 | E2E/full regression 생략 근거로 사용 금지 |

## 절대 원칙

- 새 case를 많이 만들지 않는다. 각 단계는 최소 대표 surface만 만든다.
- targeted pass만으로 완료하지 않는다.
- HTML report만으로 완료하지 않는다.
- goal complete는 최종 검증 산출물이 있을 때만 한다.
- `not scored`, missing oracle, stale report가 하나라도 있으면 평가 시스템 완료가 아니다.
- 실패 원인을 분류하지 않고 skill, reference, evaluator, runner를 수정하지 않는다.
- reference가 부족한 경우에만 reference를 수정한다.
- skill 목적이나 trigger가 틀린 경우에만 skill을 수정한다.
- evaluator나 runner가 불안정하면 case를 늘리지 않는다.
- P5/P6 완료는 `new case pass`가 아니라 `affected bucket clean`일 때만 허용한다.
- blocked 상태는 완료가 아니다. runner 권한, 외부 전송, sandbox 정책 때문에 검증을 못 하면 `infrastructure-blocked`로 기록하고 중단한다.
- 공통 runner, scorer, oracle schema, validator, report renderer, sanitizer, digest logic을 수정하면 모든 bucket을 affected로 본다.
- 다른 에디터나 다른 에이전트 런타임 검증은 이번 Codex 플러그인 완료 조건이 아니다. 필요하면 P9 이후 별도 compatibility plan으로 분리한다.
- 구조 검증, source-path prompt assembly, HTML report, skill list visibility만으로는 완료할 수 없다. 설치된 Codex runtime에서 실제 user-like prompt가 의도한 skill을 로드한 증거가 필요하다.
- P3는 P3a static/user-prompt matrix와 P3b runtime forward-test로 분리한다. P3a가 완료되고 `ADR-0004`가 accepted이면 P4를 시작할 수 있지만, P3b runtime evidence 없이는 P7/P8을 완료할 수 없다.

## 산출물 정책

작업 산출물은 `workspace/plan/constraint_rules.md`와
`workspace/plan/governance/naming_convention.md`를 따른다. 진행 상태는
`workspace/plan/status/phase_status.md`가 유일한 source of truth다.

| 종류 | 위치 | 생성 조건 |
|---|---|---|
| source reference | `workspace/reference/<area>/reference/final.md` | 공식 문서와 신뢰 자료로 기준이 확정된 경우 |
| plugin skill | `dddjango/skills/<skill>/` | reference 기준과 trigger가 확정된 경우 |
| Codex skill metadata | `dddjango/skills/<skill>/agents/openai.yaml` | Codex interface, invocation policy, dependencies metadata가 필요하고 `SKILL.md`와 일치하는 경우 |
| bundled reference | `dddjango/skills/<skill>/references/` | `SKILL.md`에 넣으면 과한 세부 기준인 경우 |
| deterministic script | `dddjango/skills/<skill>/scripts/` | 반복 실행과 결정성이 필요한 경우 |
| rebuild inventory | `workspace/plan/phases/p0-inventory/evidence/<work-item>-inventory.md` | P0에서 현재 자산을 고정할 때 |
| usage cards | `workspace/plan/phases/p1-5-usage-cards/cards/<work-item>-evidence.md` | P1.5에서 trigger family별 실제 사용자 요청을 고정할 때 |
| phase analysis | `workspace/plan/phases/<phase>/analysis/<work-item>-analysis.md` | 문제 원인과 수정 대상을 분류할 때 |
| phase plan | `workspace/plan/phases/<phase>/plan/<work-item>-plan.md` | analysis에 대응하는 좁은 수정 계획을 작성할 때 |
| phase evidence | `workspace/plan/phases/<phase>/evidence/<work-item>-evidence.md` | 검증 산출물을 phase에 귀속할 때 |
| phase closure | `workspace/plan/phases/<phase>/closure/<work-item>-closure.md` | 해당 work item이 닫혔음을 기록할 때 |
| goal prompt | `workspace/plan/goals/<phase>/<work-item>-prompt.md` | goal 기능으로 실행할 입력을 보존할 때 |
| decision record | `workspace/plan/decisions/ADR-<nnnn>-<topic>.md` | 범위, 정책, 증거 기준 같은 결정을 고정할 때 |
| review evidence | `workspace/plan/reviews/summaries/<work-item>-review.md` | 외부/에이전트/수동 리뷰를 완료 근거로 쓸 때 |
| raw review evidence | `workspace/plan/reviews/raw/<timestamp>-<perspective>.md` | 리뷰 결과를 대화 알림이 아니라 repo artifact로 보존할 때 |
| eval protocol | `workspace/plan/governance/eval_protocol.md` | 평가 시스템을 구현하기 전 |
| 평가 시스템 | 별도 설계 전까지 생성 금지 | runner/scoring/report 게이트가 먼저 확정된 뒤 |

Index 업데이트 규칙:

- 모든 work item은 `workspace/plan/indexes/artifact_index.md`에 기록한다.
- 검증을 주장하는 work item은 `workspace/plan/indexes/evidence_index.md`에 기록한다.
- 리뷰를 근거로 쓰는 work item은 `workspace/plan/indexes/review_index.md`에 기록한다.
- goal 기능으로 실행한 work item은 `workspace/plan/indexes/goal_index.md`에 기록한다.
- phase 상태 변경은 `workspace/plan/status/phase_status.md`에만 기록한다.
- superseded 문서는 삭제하지 않고 `workspace/plan/status/superseded_index.md`에 기록한다.

Skill 내부 금지 파일:

- `README.md`, `INSTALLATION_GUIDE.md`, `QUICK_REFERENCE.md`, `CHANGELOG.md` 같은 보조 문서는 skill 내부에 만들지 않는다.
- plugin root README는 marketplace/share 단계에서만 별도 판단한다. 현재 local/private 단계에서는 만들지 않는다.

Bundled script 검증:

- `dddjango/skills/<skill>/scripts/`에 script를 추가하거나 수정하면 representative 실행 증거를 남긴다.
- script 실행이 실패하면 해당 skill은 완료할 수 없다.
- script 검증 증거는 입력, 명령, stdout/stderr, exit code, 산출물 path를 포함한다.
- 모든 bundled resource는 `SKILL.md`에서 직접 링크되거나 script contract에 명시되어야 한다.
- 사용 조건이 없는 stale/placeholder `scripts/`, `references/`, `assets/` 파일은 제거한다.

## 증거 규칙

- 모든 검증 증거는 현재 파일 기준이어야 한다.
- 리뷰 증거는 대화 알림 ID만으로 인정하지 않는다. reviewer prompt, 입력 artifact digest, raw reviewer output 전문 또는 sanitized raw output 파일, 반영 line/diff 근거가 repo 안에 있어야 한다.
- model-backed run은 case, answer, evaluator, runner, validator, 관련 skill/reference 파일 digest를 run metadata에 저장해야 한다.
- run metadata digest에는 report renderer, report template/static asset, eval protocol, plugin manifest, install/cache metadata도 포함한다.
- model-backed run metadata에는 model id/version, runner destination, prompt assembly source, system/developer prompt template, tool/sandbox policy snapshot, oracle model/config, scoring prompt/config를 저장한다.
- 완료 시 현재 파일 digest와 run metadata digest가 일치해야 한다.
- 불일치한 run은 완료 증거로 인정하지 않는다.
- raw artifact가 primary truth다. HTML은 표시 검증일 뿐이다.
- report는 항상 현재 renderer로 재생성한 뒤 raw artifact와 대조한다.
- `case x variant` 매트릭스에서 baseline과 with-plugin 각각 oracle JSON이 있어야 한다.
- oracle JSON이 missing, empty, malformed이면 실패다.
- prompt/prose/raw text는 command execution evidence가 아니다. command claim은 structured event의 command/tool event만 증거로 인정한다.
- local path/private field scan은 2단계로 실행한다.
- 1단계는 redaction 전 ephemeral raw input(event JSONL, stdout, stderr, report input, validation finding)을 검사한다. forbidden local path나 private field가 있으면 run은 실패다.
- 1단계 결과는 경로 원문이 아니라 count, class, hash, artifact kind 같은 sanitized finding summary로만 저장한다.
- 2단계는 저장된 redacted artifact와 report HTML을 다시 검사한다. redaction 후에도 forbidden local path가 남으면 run 실패다.
- sanitizer가 누출을 지워서 저장 artifact가 깨끗해진 경우도 pass가 아니다. redaction 전 누출이 있으면 실패다.
- model-backed run metadata에는 `flake_history` 또는 variance status를 포함한다. 최근 pass/fail disagreement가 있으면 원인 분류와 수정 증거 없이는 final completion 근거로 쓰지 않는다.

Affected bucket 정의:

- case/answer/evaluator 변경: 해당 case가 속한 bucket.
- bucket-local validator/report 설정 변경: 해당 bucket.
- shared runner, scorer, oracle schema, validator, report renderer, sanitizer, digest logic 변경: 모든 bucket.
- skill/reference/runtime cache 변경: 해당 skill을 참조하는 모든 bucket.
- plugin manifest/install/cache metadata 변경: plugin, runtime, source, workflow bucket과 관련 smoke 검증.

## 단계별 계획

### P0. 현재 자산 동결

목표: 현재 남은 reference와 skill이 실제로 무엇인지 고정한다.

체크리스트:

- [ ] `dddjango/.codex-plugin/plugin.json` 필수 필드와 paths를 확인한다.
- [ ] plugin component set을 inventory한다: `skills`, `agents/openai.yaml`, `assets`, `hooks`, `.mcp.json`, `.app.json` 존재 여부.
- [ ] P8까지 local/private Codex plugin 기준인지 기록한다. 기준이 바뀌면 marketplace/cache evidence gate를 별도 갱신한다.
- [ ] `dddjango/skills/*/SKILL.md` 목록을 inventory한다.
- [ ] `workspace/reference/*/reference/final.md` 목록을 inventory한다.
- [ ] source reference와 skill의 1:1 또는 1:N 관계를 `workspace/plan/phases/p0-inventory/evidence/<work-item>-inventory.md`에 표로 만든다.
- [ ] 이 단계에서는 inventory 외 파일을 수정하지 않는다.

완료 게이트:

- [ ] `workspace/plan/phases/p0-inventory/evidence/<work-item>-inventory.md`가 있고 `workspace/plan/indexes/artifact_index.md`에 기록되어 있다.
- [ ] 누락된 skill/reference 관계가 `unknown`으로 표시되어 있다.
- [ ] inventory 외 수정 파일이 없다.

### P1. Reference 충분성 검증

목표: skill을 고치기 전에 source reference가 충분한지 확인한다.

Source 우선순위:

1. 공식 문서와 표준 문서
2. primary project documentation
3. 신뢰 가능한 engineering article
4. unsupported blog 또는 기억 기반 기준

체크리스트:

- [ ] 각 `final.md`가 목적, 사용 조건, 제외 조건, 핵심 판단 기준을 포함하는지 확인한다.
- [ ] 기준마다 source 우선순위를 기록한다.
- [ ] 불확실하거나 출처가 약한 기준은 provisional로 표시한다.
- [ ] OpenAPI는 REST/HTTP API contract 기준으로만 사용하고 DDD/DB/Django ORM/test 기준으로 쓰지 않는다.
- [ ] OpenAPI 직접 source 사용 대상은 `architecture-api`, `implementation-django-ninja`로 제한한다. 다른 skill은 handoff/reference boundary로만 참조한다.
- [ ] source gap이 있으면 reference만 수정한다.

완료 게이트:

- [ ] 모든 reference가 `sufficient`, `needs-source`, `provisional` 중 하나로 판정된다.
- [ ] `needs-source`가 하나라도 있으면 다음 단계로 가지 않는다.
- [ ] `provisional`은 skill에 조심스럽게 반영할 수 있지만 eval completion 근거로 쓰지 않는다.

### P1.5. 실제 사용 예시 고정

목표: skill 구조를 고치기 전에 실제 사용자가 어떤 말로 skill을 부를지 고정한다.

체크리스트:

- [ ] trigger family마다 realistic user prompt 2-3개를 작성한다.
- [ ] trigger family마다 exclusion prompt 1개를 작성한다.
- [ ] 각 prompt에 expected skill, expected bundled resource load, expected artifact behavior, common non-goal을 기록한다.
- [ ] 내부 taxonomy가 아니라 사용자 언어를 기준으로 작성한다.
- [ ] usage card는 `description`, handoff 문구, P3 forward-test, P5 case 설계의 입력으로 사용한다.

완료 게이트:

- [ ] `workspace/plan/phases/p1-5-usage-cards/cards/<work-item>-evidence.md`가 있고 `workspace/plan/indexes/artifact_index.md`에 기록되어 있다.
- [ ] 모든 high-risk trigger family에 positive/exclusion usage card가 있다.
- [ ] usage card 없이 `SKILL.md` description 또는 trigger handoff를 수정하지 않는다.

### P2. Skill 구조와 trigger 검증

목표: 각 skill이 Codex에서 발견 가능하고 과하게 로딩되지 않도록 만든다.

체크리스트:

- [ ] `SKILL.md` frontmatter는 `name`, `description`만 사용한다.
- [ ] `name`은 skill folder basename과 일치한다.
- [ ] `description`에 usage card 기반 사용 조건과 제외 조건이 들어 있다.
- [ ] `description`은 기본 120 words 이하, hard limit 180 words 또는 1200 chars 이하로 유지한다.
- [ ] `SKILL.md` body는 500줄 미만이고 기본 3500 words 이하이며, 실행 절차와 resource navigation 및 필수 규칙만 담는다.
- [ ] `SKILL.md`와 bundled references 사이에 중복 섹션이 없다. 상세 domain material은 direct reference로 이동한다.
- [ ] bundled references는 한 단계 아래에 있고 `SKILL.md`에서 직접 연결된다.
- [ ] 100줄 초과 bundled reference는 상단 table of contents를 포함한다. 검색 키워드와 section anchor는 TOC의 보조 수단이다.
- [ ] 모든 bundled resource는 use condition이 있고 `SKILL.md`에서 직접 링크되거나 script contract에 명시되어 있다.
- [ ] stale/placeholder bundled resource가 없다.
- [ ] `agents/openai.yaml`은 Codex optional metadata로 검증한다: `interface`, invocation `policy`, `dependencies`.
- [ ] `agents/openai.yaml`은 display name, short description, default prompt, trigger intent가 `SKILL.md`와 일치하는지 비교한다.
- [ ] `policy.allow_implicit_invocation`이 expected trigger와 충돌하지 않는다.
- [ ] `dependencies.tools`가 있다면 실제 필요성과 사용 가능성 증거가 있다.
- [ ] `agents/openai.yaml`을 생성/수정할 때는 `skill-creator/references/openai_yaml.md`를 확인하고, `skill-creator/scripts/generate_openai_yaml.py` 사용 증거 또는 generator 미사용 사유를 남긴다.
- [ ] runtime boundary scan은 plugin root 전체에 적용한다: `.codex-plugin/plugin.json`, `skills/**/SKILL.md`, `skills/**/references/**`, `skills/**/scripts/**`, `skills/**/agents/openai.yaml`, `assets/**`, `hooks/**`, `.mcp.json`, `.app.json`.
- [ ] runtime files는 absolute local path, plugin root 밖 path traversal, source tree 의존을 포함하지 않는다.
- [ ] `workspace/reference`는 source-governance/audit 대상 설명으로만 허용한다. runtime bundled reference, allowed runtime path, normal skill dependency로 쓰면 실패다.

완료 게이트:

- [ ] 모든 skill이 frontmatter, description, body size, direct reference links를 통과한다.
- [ ] 모든 skill에 대해 `skill-creator/scripts/quick_validate.py <skill-folder>` 또는 동일 기준의 local validator 실행 증거가 있다.
- [ ] validator가 없거나 실행 불가하면 P2 안에서 대체 validator를 먼저 만들고 fixture로 검증한다.
- [ ] skill끼리 trigger가 겹치는 항목은 handoff 문구가 있다.
- [ ] source plugin 안에서 runtime에 필요한 bundled references가 모두 존재한다.
- [ ] Codex compatibility issue가 `unknown`으로 남아 있지 않다.
- [ ] `agents/openai.yaml` policy/dependencies와 `SKILL.md` trigger 기대가 충돌하지 않는다.

### P3. 최소 사용 시나리오 검증

목표: 평가 시스템 없이도 각 skill이 실제 요청에서 쓸 수 있는지 확인한다.

P3 split:

- P3a static/user-prompt matrix: usage card 기반 prompt set, expected routing,
  common non-goal, blocked runtime evidence, index/status 기록을 고정한다.
- P3b runtime forward-test: approved external Codex/OpenAI runtime 또는 실행
  가능한 local/offline provider에서 actual skill loaded, routing observation,
  final answer, overclaim, leakage를 관찰한다.

P3a가 완료되고 `ADR-0004-p3-runtime-forward-test-deferral.md`가 accepted이면
P4를 시작할 수 있다. 단, P3 전체가 complete인 것은 아니며 P4/P5/P6 결과는
runtime-routing evidence가 없다는 제한을 가진다. P7/P8 완료 전에는 P3b 또는
그와 동등한 installed-runtime user-like evidence가 반드시 필요하다.

검증 matrix:

- Codex trigger smoke
- manual source review
- fresh isolated subagent/user-like forward-test

Forward-test 규칙:

- fresh isolated context를 사용한다.
- subagent forward-test는 리뷰 요청이 아니라 실제 사용자 요청처럼 작성한다.
- prompt에는 target skill path와 user-like task만 준다.
- 기대 답, 의도한 수정, 이전 결론, suspected bug를 넘기지 않는다.
- raw output, loaded skill, routing observation, final answer를 저장한다.
- forward-test는 prior `workspace/plan/**`, eval outputs, previous forward-test artifacts를 볼 수 없는 clean temp workspace에서 실행한다.
- transcript는 실행 후 `workspace/plan/phases/p3-forward-tests/evidence/`에 저장한다.
- 각 실행 후 artifact contamination을 정리하고, subagent가 prior review/test artifact에 접근할 수 없었다는 contamination check를 기록한다.

결과 schema:

- prompt
- expected trigger
- actual skill loaded
- raw output path
- raw output 저장 위치: `workspace/plan/phases/p3-forward-tests/evidence/<work-item>-evidence.md`
- wrong routing 여부
- overclaim 여부
- 수정 대상: `none`, `reference`, `skill`, `trigger`, `runtime-sync`

완료 게이트:

- [ ] P3a: 모든 high-risk trigger family의 happy/exclusion prompt matrix가 있다.
- [ ] P3a: runtime 실행이 막힌 경우 blocked evidence와 승인/로컬 provider 시도 결과가 기록되어 있다.
- [ ] P3b: 모든 skill에 happy/exclusion runtime 결과가 있다.
- [ ] P3b: 각 trigger family 또는 high-risk skill마다 fresh isolated subagent/user-like forward-test가 최소 1개 있다.
- [ ] 실패가 있으면 해당 skill/reference/trigger만 수정한다.
- [ ] Codex trigger smoke가 실행 불가하면 P3b를 `infrastructure-blocked`로 기록하고 P3 전체를 complete로 표시하지 않는다.
- [ ] fresh forward-test를 실행할 수 없으면 P3b를 `infrastructure-blocked`로 기록한다. P4 진입은 P3a 완료와 accepted ADR이 있을 때만 허용한다.
- [ ] 평가 runner나 HTML report는 아직 만들지 않는다.

### P4. 평가 시스템 골격 검증

목표: case를 늘리기 전에 runner, scoring, report가 최소 suite에서 신뢰 가능한지 확인한다.

P4 entry condition:

- P3a static/user-prompt matrix가 complete여야 한다.
- P3b runtime forward-test가 blocked인 경우 `ADR-0004`가 accepted되어 있어야
  한다.
- P4 산출물에는 runtime-routing evidence가 deferred 상태임을 기록한다.

P4 선행 산출물:

- [ ] `workspace/plan/governance/eval_protocol.md`에 case schema, answer schema, oracle output schema, scoring semantics, artifact names, failure semantics, report invariants, command contract를 먼저 정의한다.

Mini-bucket fixture:

- pass case 1개
- partial case 1개
- fail case 1개
- missing-oracle injected case 1개
- malformed-oracle injected case 1개
- stale-report injected case 1개
- local-path injected artifact 1개
- sanitizer-only pass injected case 1개: redaction 전 누출이 있었지만 저장 artifact가 깨끗한 경우도 실패해야 한다.
- private-field leak injected artifact 1개
- expected_outcomes conflict fixture 1개
- Korean negation false-positive fixture 1개
- prompt-only command claim fixture 1개
- 각 fixture는 baseline/with-plugin 양 variant의 oracle 존재, malformed, missing, scored 상태를 검증한다.

체크리스트:

- [ ] runner는 model output 없이 fixture-only로 먼저 동작한다.
- [ ] raw artifact 기준으로 scoring completeness를 판정한다.
- [ ] report는 raw artifact와 일치해야 한다.
- [ ] missing/malformed oracle은 실패한다.
- [ ] stale report는 실패한다.
- [ ] command claim은 structured event command/tool evidence만 인정한다.
- [ ] local path leakage는 raw/report 모두에서 실패한다.
- [ ] redaction 전 누출이 있으면 redaction 성공 여부와 무관하게 실패한다.

완료 게이트:

- [ ] mini-bucket full run이 기대대로 pass/fail을 구분한다.
- [ ] 모든 fixture의 결과가 raw artifact, validator, report에서 일치한다.
- [ ] `not scored`가 있으면 run이 실패한다.
- [ ] P5/P6에서 사용할 `run-one`, `run-bucket`, `render-report`, `validate-run` command contract가 확정되어 있다.
- [ ] bucket 영향 판단표가 `workspace/plan/governance/eval_protocol.md`에 포함되어 있다.

### P4.5. 설치와 런타임 parity precheck

목표: model-backed 검증 전에 source plugin과 실제 runtime plugin이 다르지 않음을 확인한다.

체크리스트:

- [ ] Codex local install/cache path를 기록한다.
- [ ] Codex marketplace source와 plugin enabled state를 기록한다.
- [ ] `.codex-plugin/plugin.json` parse 결과와 all manifest path field validation 결과를 저장한다.
- [ ] installed/cache plugin path, skill count/name list, source/cache diff 결과를 저장한다.
- [ ] Codex discovery evidence를 재현 가능한 raw output으로 남긴다. 허용 증거는 `/plugins` transcript 또는 screenshot, app-server `plugin/list`/`plugin/read` JSON, `skills/list` 결과, `codex plugin --help`로 확인한 CLI command output 중 실제 환경에서 가능한 것을 사용한다.
- [ ] source skill과 Codex runtime cache diff를 확인한다.
- [ ] Codex runtime이 plugin root 밖 파일을 필요로 하지 않는지 확인한다.
- [ ] scripts가 있으면 installed cache에서 `PLUGIN_ROOT`가 cache root를 가리키는 상태로 representative script 실행 증거를 남긴다.

완료 게이트:

- [ ] source/cache diff가 없다.
- [ ] plugin root 밖 reference 의존이 없다.
- [ ] Codex discovery smoke가 최소 1개 skill에서 통과한다.
- [ ] model-backed P5/P6 실행 전에 설치/cache/discovery raw evidence가 현재 파일 기준으로 존재한다.

### P5. 개별 skill 평가 최소 세트

목표: 각 skill의 목적을 대표하는 최소 평가만 만든다.

체크리스트:

- [ ] skill folder 기준이 아니라 trigger family 기준으로 positive/negative surface를 정한다.
- [ ] 기본은 trigger family당 positive 1개, negative 1개다.
- [ ] 더 늘릴 때는 P4 안정성과 coverage gap 근거가 있어야 한다.
- [ ] answer는 reference criterion coverage, required observations, forbidden overclaim 중심으로 작성한다.
- [ ] baseline verdict 고정과 `expected_delta` completion gate 사용은 금지한다.
- [ ] baseline verdict, with-plugin verdict, `pass-or-pass-limited`, `expected_delta` 같은 고정 verdict/delta는 completion gate로 금지한다.
- [ ] `expected_outcomes` 허용 필드는 criterion coverage, required observations, forbidden overclaim로 제한한다.
- [ ] flaky case가 2회 이상 나오면 case/answer/evaluator 문제로 분류하고 확장 금지한다.
- [ ] model-backed 신규 case는 기본 2회 실행한다. 비용이나 권한 때문에 1회만 실행하면 `single-pass provisional`로 표시하고 full regression 전 완료 근거로 쓰지 않는다.

완료 게이트:

- [ ] 모든 신규/수정 case가 targeted pass다.
- [ ] model-backed 신규/수정 case는 기본 2회 모두 pass다.
- [ ] 1회만 실행한 case는 `single-pass provisional`이며 P5 완료 근거로 쓰지 않는다.
- [ ] affected bucket all-cases run이 pass다.
- [ ] affected bucket `not scored == 0`이다.
- [ ] affected bucket missing/malformed oracle JSON이 0이다.
- [ ] affected bucket `validate-run`이 통과한다.
- [ ] HTML score visibility가 raw artifact와 일치한다.
- [ ] 현재 파일 digest와 run metadata digest가 일치한다.
- [ ] shared eval infrastructure를 수정했다면 모든 bucket이 clean이다.

### P6. Skill 연계 평가 최소 세트

목표: 플러그인 단위 연계가 필요한 대표 흐름만 검증한다.

체크리스트:

- [ ] DDD + DB + API + Django + Test 대표 흐름 1개를 만든다.
- [ ] tiny edit / opt-out restraint 대표 흐름 1개를 만든다.
- [ ] source/runtime governance 대표 흐름 1개를 만든다.
- [ ] subagent/workflow honesty 대표 흐름 1개를 만든다.
- [ ] 개별 skill 평가를 integration 평가 근거로 재사용하지 않는다.
- [ ] workflow/subagent trace는 실제 artifact가 있을 때만 pass한다.

완료 게이트:

- [ ] 모든 신규/수정 integration case가 targeted pass다.
- [ ] model-backed 신규/수정 integration case는 기본 2회 모두 pass다.
- [ ] 1회만 실행한 integration case는 `single-pass provisional`이며 P6 완료 근거로 쓰지 않는다.
- [ ] affected bucket all-cases run이 pass다.
- [ ] affected bucket `not scored == 0`이다.
- [ ] affected bucket missing/malformed oracle JSON이 0이다.
- [ ] affected bucket `validate-run`이 통과한다.
- [ ] current-file fingerprint가 run evidence와 일치한다.
- [ ] skill 책임 침범, false claim, source leakage가 0이다.
- [ ] shared eval infrastructure를 수정했다면 모든 bucket이 clean이다.

### P7. 설치와 패키징 검증

목표: source plugin과 Codex install/cache가 일치하는지 최종 확인한다.

P7 entry condition:

- P3b runtime forward-test 또는 동등한 installed-runtime user-like evidence를
  실행할 수 있는 runtime channel이 있어야 한다. 실행할 수 없으면 P7은
  `infrastructure-blocked`이고 complete가 아니다.

체크리스트:

- [ ] Codex `.codex-plugin/plugin.json`의 `skills: "./skills/"`를 확인한다.
- [ ] Codex cache diff를 확인한다.
- [ ] every manifest path field starts with `./`, resolves relative to plugin root, stays inside plugin root, and exists when required.
- [ ] `.codex-plugin/` 아래에는 `plugin.json`만 있다.
- [ ] plugin root 밖 path traversal이 없다.
- [ ] local plugin이면 cache path version은 `local`로 기록하고, manifest `version`은 source copy와 installed copy의 `plugin.json` 값이 일치하는지 비교한다.
- [ ] non-local marketplace install이면 Codex가 노출하는 marketplace/version semantics에 맞춰 별도 비교한다.
- [ ] high-risk trigger family마다 설치된 Codex runtime에서 user-like task를 최소 1개 실행한다.
- [ ] installed-runtime user-like task는 actual skill loaded, source/cache path, final answer/artifacts, false-trigger/exclusion behavior를 기록한다.

Command evidence contract:

- Codex evidence는 `.codex-plugin/plugin.json` parse 결과, installed/cache plugin path, skill count/name list, source/cache diff 결과를 포함한다.
- Codex discovery evidence는 재현 가능한 raw output으로 남긴다. 허용 증거는 `/plugins` transcript 또는 screenshot, app-server `plugin/list`/`plugin/read` JSON, `skills/list` 결과, `codex plugin --help`로 확인한 CLI command output 중 실제 환경에서 가능한 것을 사용한다.
- 각 evidence raw output은 `workspace/plan/phases/p7-install-packaging/evidence/<work-item>-evidence.md`에 저장한다.

완료 게이트:

- [ ] Codex skill 목록에서 namespace가 의도대로 보인다.
- [ ] source/cache diff가 없다.
- [ ] plugin root 밖 runtime dependency가 없다.
- [ ] installed-runtime user-like task가 high-risk trigger family마다 의도한 skill을 로드했다.
- [ ] false-trigger/exclusion behavior가 usage card와 일치한다.

### P8. Full regression

목표: 최종 full run으로만 완료를 선언한다.

체크리스트:

- [ ] 전체 bucket run을 실행한다.
- [ ] 모든 `case x variant`가 scored인지 raw artifact 기준으로 확인한다.
- [ ] missing/malformed oracle JSON이 0인지 확인한다.
- [ ] expected outcome 충돌이 0인지 확인한다.
- [ ] validator false positive가 0인지 확인한다.
- [ ] local path leakage가 raw/report 전체에서 0인지 확인한다.
- [ ] HTML latest가 최종 run을 가리키는지 확인한다.
- [ ] P7 installed-runtime user-like task evidence가 현재 skill/manifest/cache 기준인지 확인한다. P7 이후 skill, manifest, metadata, cache가 바뀌었으면 P7 installed-runtime task를 다시 실행한다.
- [ ] P3b runtime forward-test deferral이 해소되었는지 확인한다. 해소되지 않았으면 full regression이 통과해도 P8 complete 금지.
- [ ] unresolved flaky history가 0인지 확인한다.

완료 게이트:

- [ ] full run pass다.
- [ ] `not scored` 0이다.
- [ ] missing/malformed oracle 0이다.
- [ ] local path leakage 0이다.
- [ ] report stale 0이다.
- [ ] current-file fingerprint mismatch 0이다.
- [ ] unresolved flaky history 0이다.
- [ ] installed-runtime user-like task evidence가 현재 파일 기준이고 high-risk trigger family coverage를 만족한다.
- [ ] P3b runtime forward-test 또는 accepted equivalent installed-runtime evidence가 current다.
- [ ] 마지막 독립 리뷰의 Blocker 0, Major 0, 열린 Minor 0 증거가 `workspace/plan/reviews/`에 있다.

### P9. 선택: 다른 런타임 호환성

목표: Codex 플러그인 완료 후에만 다른 런타임 호환성을 별도 범위로 검토한다.

규칙:

- [ ] P9는 P0-P8의 Codex 완료 조건이 아니다.
- [ ] 다른 런타임 manifest, cache, invocation, namespace 검증 실패는 Codex 플러그인 완료를 막지 않는다.
- [ ] 다른 런타임을 지원하려면 별도 source ledger, 별도 compatibility plan, 별도 evidence gate를 만든다.
- [ ] Codex용 `SKILL.md`, `agents/openai.yaml`, `.codex-plugin/plugin.json` 기준을 다른 런타임 규칙과 섞지 않는다.

## 리뷰 운영 규칙

- 계획 문서 안에 자체 인증 리뷰 결과를 쓰지 않는다.
- 모든 리뷰는 `workspace/plan/reviews/<timestamp>-<topic>.md`에 별도 저장한다.
- 리뷰 파일에는 reviewer prompt, 입력 artifact, findings, 반영 여부, 남은 open issue를 기록한다.
- 리뷰 파일에는 reviewer prompt 전문, 입력 artifact digest, raw reviewer output 전문 또는 raw output 저장 위치, 반영 line/diff 근거를 기록한다.
- Blocker 또는 Major가 하나라도 열려 있으면 계획을 확정하지 않는다.
- 최종 판정은 “문서가 주장하는 상태”가 아니라 “리뷰 evidence 파일이 증명하는 상태”로만 말한다.

## 최종 판정 기준

- 이 계획이 확정되려면 별도 리뷰 evidence에서 Blocker 0, Major 0, 열린 Minor 0이어야 한다.
- 현재 문서만으로는 완료를 주장하지 않는다.
- 첫 실행은 P0 inventory다.
- 평가 시스템 재작성은 P4 전까지 금지한다.
