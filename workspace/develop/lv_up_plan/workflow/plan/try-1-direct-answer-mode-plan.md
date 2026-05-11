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

## 4. 구현 방침

### 4.1 `SKILL.md`

`Runtime Rules` 또는 `Routing` 근처에 짧은 규칙을 추가한다.

```text
Direct Answer Mode: If the routing decision is to stay direct because the task is a short explanation, tiny rename, simple local edit, or explicit opt-out, preserve the user's requested output shape. Do not add Role Map, Handoff Contract, Integration Checklist, subagent status, validation footer, or command-honesty boilerplate unless the user asked for work performed or files/commands were actually used in a way that must be reported.
```

주의:

- `case-workflow-tiny-restraint`의 정답 문장을 넣지 않는다.
- `Django Ninja Router` 같은 case-specific phrase를 넣지 않는다.
- 기존 composite/risky workflow section 요구를 약화하지 않는다.

### 4.2 `delegation-rules.md`

`When To Stay Direct` 아래에 출력 제한을 추가한다.

```text
When staying direct, answer with the requested content only. If the user asks for two sentences, both sentences should answer the question. Do not spend one of the requested sentences on meta-reporting such as tests not run, commands not run, or no subagents used unless that is the user's question.
```

주의:

- validation honesty 자체를 제거하지 않는다.
- 파일 수정, 명령 실행, 테스트 실행이 실제로 있었던 구현 작업에서는 여전히 보고한다.
- 단순 설명 요청에서만 footer/meta sentence를 억제한다.

## 5. 검증 계획

문서/스킬 검증:

```bash
python3 -B workspace/scripts/validate_skill_docs.py --phase docs
python3 -B workspace/scripts/validate_eval_bucket_pack.py --bucket workflow
git diff --check
```

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

## 6. 성공 기준

- `case-workflow-tiny-restraint` with-dddjango가 pass 또는 최소 4 / 5 이상.
- tiny 설명 답변에서 두 문장 모두 설명에 사용된다.
- `case-workflow-opt-out`은 Role Map/Handoff/Integration Checklist를 계속 출력하지 않는다.
- `case-workflow-sequential-fallback`은 필요한 workflow sections와 delegation honesty를 유지한다.
- `runs/`, raw transcript, generated report html은 커밋하지 않는다.

## 7. 실패 시 다음 try

try-1이 실패하면 `try-2`에서는 다음을 검토한다.

- `workflow-dddjango-subagents` description이 short explanation에서도 너무 강하게 trigger되는지 확인한다.
- `implementation-django-ninja` 같은 직접 설명용 skill이 더 먼저 선택되도록 skill metadata를 조정할지 검토한다.
- tiny-task eval oracle이 “두 문장 모두 설명”을 더 명시적으로 요구하도록 보강할지 검토한다.
