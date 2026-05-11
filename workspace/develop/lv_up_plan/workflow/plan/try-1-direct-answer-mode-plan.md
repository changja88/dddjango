# Try 1 Workflow 수정 계획: Direct Answer Mode

작성일: 2026-05-11
분석 근거: `workspace/develop/lv_up_plan/workflow/analysis/try-1-workflow-failure-classification.md`
대상 family: `tiny-task-restraint`

## 1. 목표

`case-workflow-tiny-restraint`의 with-dddjango fail을 고친다. 핵심은 단순 설명/opt-out 요청에서 dddjango workflow를 과적용하지 않는 것뿐 아니라, 사용자가 요구한 출력 형식을 그대로 지키는 것이다.

이번 try는 `Direct Answer Mode`를 작게 추가한다. composite workflow, risky write, review-focused, actual subagent trace 동작은 건드리지 않는다.

## 2. 현재 실패 요약

public case는 “Django Ninja Router가 무엇인지 두 문장으로 설명”하고, “역할 분해나 dddjango 전체 workflow는 필요 없다”고 했다.

with-dddjango는 Role Map, Handoff Contract, Integration Checklist를 출력하지 않았지만, 두 문장 중 두 번째 문장을 “명령/테스트를 실행하지 않았다”는 메타 보고로 사용했다. 그래서 실제 설명 문장은 하나뿐이고 oracle의 `두 문장 설명` 요구를 만족하지 못했다.

## 3. 수정 범위

수정 대상:

- `dddjango/skills/workflow-dddjango-subagents/SKILL.md`
- `dddjango/skills/workflow-dddjango-subagents/references/delegation-rules.md`
- `dddjango/skills/implementation-django-ninja/SKILL.md`

수정하지 않을 대상:

- `dddjango/skills/workflow-dddjango-subagents/agents/openai.yaml`
- `dddjango/.codex-plugin/plugin.json`
- `.agents/plugins/marketplace.json`
- `workspace/develop/eval/workflow/cases/plugin/public/case-workflow-tiny-restraint.md`
- `workspace/develop/eval/workflow/answer/case-workflow-tiny-restraint.yaml`

이유:

- routing 자체는 대체로 맞았다. workflow ceremony는 나오지 않았다.
- 문제는 direct answer path의 출력 discipline 부족이다.
- eval case와 oracle은 명확하고 수정할 필요가 없다.
- targeted eval에서 short Django Ninja explanation은 `implementation-django-ninja`도 실제 출력 경로에 들어오는 것으로 확인됐다.

## 4. Skill-creator 리뷰 반영

`skill-creator` 기준으로 이번 계획은 실패 family 하나만 작게 고치고, 자세한 출력 기준을 reference에 두려는 점은 맞다. 다만 구현 전에 다음 보강이 필요하다.

- Progressive disclosure: `SKILL.md`에는 핵심 규칙만 1개 추가하고, 예외와 상세 기준은 `delegation-rules.md`에 둔다. 같은 내용을 양쪽에 길게 중복하지 않는다.
- Validation integrity: eval answer의 target phrase나 case-specific 문구를 skill에 넣지 않는다. 구현 후 skill 파일에 `case-workflow`나 해당 public case의 고유 문구가 들어가지 않았는지 확인한다.
- Metadata drift: `agents/openai.yaml`을 수정하지 않더라도, 변경 후 default prompt가 새 규칙과 모순되지 않는지 읽어서 확인한다. 모순이 있으면 이번 try의 범위를 재검토하고 plan에 먼저 기록한다.
- Cache/source consistency: 커밋 대상은 workspace canonical source만 둔다. 실제 eval이 installed plugin cache를 읽는다면 cache sync는 별도 실행 단계로 처리하고, 커밋하지 않으며 최종 보고에 cache path와 source mapping을 남긴다.
- Forward test: subagent forward-test는 이번 try의 기본값으로 쓰지 않는다. 이미 bucket eval이 실제 사용 시나리오를 제공하므로 targeted eval과 인접 회귀 eval을 1차 검증으로 삼는다. 별도 subagent 검증이 필요하면 expected fix나 oracle 내용을 넘기지 않는다.

## 5. 구현 방침

### 5.1 사전 확인

수정 전 다음 파일을 읽고 현재 문맥을 확인한다.

- `dddjango/skills/workflow-dddjango-subagents/SKILL.md`
- `dddjango/skills/workflow-dddjango-subagents/references/delegation-rules.md`
- `dddjango/skills/workflow-dddjango-subagents/agents/openai.yaml`
- `dddjango/skills/implementation-django-ninja/SKILL.md`

확인할 것:

- 기존 routing이 short explanation과 opt-out을 이미 direct path로 보내는지.
- `Output Shape`와 `Runtime Rules`의 command honesty 규칙이 pure answer-only 요청과 충돌하는지.
- `openai.yaml`의 default prompt가 role-decomposed workflow만 강제하는 표현인지, 아니면 opt-out/direct path와 공존 가능한 표현인지.
- short Django Ninja explanation이 `workflow-dddjango-subagents`가 아니라 `implementation-django-ninja`로 처리될 때도 같은 output discipline이 적용되는지.

### 5.2 `SKILL.md`

`Runtime Rules` 또는 `Routing` 근처에 짧은 규칙을 추가한다.

```text
Direct Answer Mode: If the routing decision is to stay direct because the task is a short explanation, tiny edit, or explicit opt-out, preserve the user's requested output shape. For pure answer-only requests, answer with the requested content only; do not add Role Map, Handoff Contract, Integration Checklist, subagent status, validation footer, or command-honesty boilerplate. For actual file edits or commands, keep the final report limited to the concrete changed files and verification that must be reported.
```

주의:

- `case-workflow-tiny-restraint`의 정답 문장을 넣지 않는다.
- `Django Ninja Router` 같은 case-specific phrase를 넣지 않는다.
- 기존 composite/risky workflow section 요구를 약화하지 않는다.
- command honesty를 제거하지 않는다. 단순 답변 요청과 실제 작업 보고를 구분한다.

### 5.3 `delegation-rules.md`

`When To Stay Direct` 아래에 출력 제한을 추가한다.

```text
When staying direct for a pure answer-only request, answer with the requested content only. If the user asks for a fixed answer shape such as a sentence count or bullet count, every requested unit should answer the user's question. Do not spend one of those units on meta-reporting such as tests not run, commands not run, or no subagents used unless that is the user's question. For direct implementation work, still report changed files and verification honestly, but keep it compact and do not add workflow sections.
```

주의:

- validation honesty 자체를 제거하지 않는다.
- 파일 수정, 명령 실행, 테스트 실행이 실제로 있었던 구현 작업에서는 여전히 보고한다.
- 단순 설명 요청에서만 footer/meta sentence를 억제한다.

### 5.4 `implementation-django-ninja/SKILL.md`

short Django Ninja explanation이 이 skill로 직접 처리될 수 있으므로 `Output Shape`를 추가한다.

```text
For pure answer-only requests, output only the requested answer. If the user asks for a fixed number of sentences or bullets, return exactly that many units and stop at the final requested unit. Do not append or embed command lists, checks, tool reports, Serena notes, or skill/reference loading reports.
```

주의:

- Django Ninja Router의 case-specific 정답 문장을 넣지 않는다.
- 정의형 질문에는 요청한 개념과 일반적 사용만 설명한다.
- 구현 작업에서는 verification honesty를 유지한다.

## 6. 검증 계획

문서/스킬 검증:

```bash
python3 -B workspace/scripts/validate_skill_docs.py --phase docs
python3 -B workspace/scripts/validate_eval_bucket_pack.py --bucket workflow
rg -n "case-workflow|Django Ninja Router가 무엇인지|두 문장으로 설명|역할 분해나 dddjango 전체 workflow" dddjango/skills/workflow-dddjango-subagents dddjango/skills/implementation-django-ninja
git diff --check
```

`rg` 명령은 결과가 없어야 한다. 일반적인 `Django Ninja Router/Schema` reference 문구는 허용하지만, public case 고유 문구나 case id가 skill에 들어가면 eval-specific leakage/overfit으로 본다.

targeted eval:

```bash
python3 -B workspace/scripts/run_initial_eval.py \
  --bucket workflow \
  --run-id 20260511-workflow-try-1-direct-answer \
  --case case-workflow-tiny-restraint \
  --model gpt-5.5 \
  --reasoning xhigh \
  --evaluator-model gpt-5.5 \
  --evaluator-reasoning high \
  --rerun
```

cache/source 확인:

- eval 전 with-dddjango runtime이 workspace source를 읽는지 installed plugin cache를 읽는지 확인한다.
- cache를 읽는다면 workspace canonical source와 cache 파일을 동기화한 뒤 eval을 실행한다.
- cache sync 산출물은 커밋하지 않고, 어떤 cache path를 어떤 source에서 맞췄는지만 보고한다.

회귀 확인:

```bash
python3 -B workspace/scripts/run_initial_eval.py \
  --bucket workflow \
  --run-id 20260511-workflow-try-1-direct-answer-regression \
  --case case-workflow-opt-out \
  --case case-workflow-sequential-fallback \
  --model gpt-5.5 \
  --reasoning xhigh \
  --evaluator-model gpt-5.5 \
  --evaluator-reasoning high \
  --rerun
```

## 7. 성공 기준

- `case-workflow-tiny-restraint` with-dddjango가 pass 또는 최소 4 / 5 이상.
- tiny 설명 답변에서 두 문장 모두 설명에 사용된다.
- pure answer-only 출력에 `Commands run`, `Checks not run`, `실행한 명령`, `체크`, `Serena` tail이 붙지 않는다.
- `case-workflow-opt-out`은 Role Map/Handoff/Integration Checklist를 계속 출력하지 않는다.
- `case-workflow-sequential-fallback`은 필요한 workflow sections와 delegation honesty를 유지한다.
- `runs/`, raw transcript, generated report html은 커밋하지 않는다.
- `dddjango/skills/workflow-dddjango-subagents/agents/openai.yaml`을 수정하지 않았으면, default prompt가 direct path와 모순되지 않는다는 확인을 최종 보고에 포함한다.

## 8. 실패 시 다음 try

try-1이 실패하면 `try-2`에서는 다음을 검토한다.

- `workflow-dddjango-subagents` description이 short explanation에서도 너무 강하게 trigger되는지 확인한다.
- `implementation-django-ninja` 같은 직접 설명용 skill이 더 먼저 선택되도록 skill metadata를 조정할지 검토한다.
- tiny-task eval oracle이 “두 문장 모두 설명”을 더 명시적으로 요구하도록 보강할지 검토한다.
