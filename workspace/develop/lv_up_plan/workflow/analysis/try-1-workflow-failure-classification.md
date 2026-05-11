# Workflow 실패 원인 분류

작성일: 2026-05-11
시도: `try-1`
기준 run: `workspace/develop/eval/workflow/runs/20260511-0413-initial-full`
기준 문서: `workspace/develop/lv_up_plan/plan_guide.md`

## 1. 평가 항목 선택

우선순위는 `fail`, `blocked`, hard gate failure를 먼저 본다. 이번 workflow run에서 with-dddjango 기준 hard gate failure와 blocked는 없고, 실제 fail은 하나다.

| 우선순위 | case | baseline | with-dddjango | delta | 판정 |
|---|---|---:|---:|---:|---|
| P0 | `case-workflow-tiny-restraint` | 4 / 5 pass | 3 / 5 fail | -1.0 | 즉시 개선 대상 |
| P1 | `case-workflow-actual-subagent-trace` | 4 / 5 pass | 5 / 5 pass | +1.0 | trace 표현 점검 |
| P1 | `case-workflow-risky-write` | 4 / 5 pass | 5 / 5 pass | +1.0 | 유지 회귀 방지 |
| P2 | `case-workflow-review-focused` | 3 / 5 pass | 5 / 5 pass | +2.0 | 유지 회귀 방지 |
| P2 | `case-workflow-positive-composite` | 2 / 5 fail | 5 / 5 pass | +3.0 | 유지 회귀 방지 |
| P2 | `case-workflow-live-delegation` | 2 / 5 fail | 5 / 5 pass | +3.0 | 유지 회귀 방지 |
| P3 | 나머지 pass | pass | pass | 0 이상 | 현재는 관찰 대상 |

이번 개선 루프의 첫 target family는 `tiny-task-restraint`로 제한한다. 전체 workflow를 한 번에 고치지 않는다.

## 2. 실패 원인 분류

### P0: `case-workflow-tiny-restraint`

public case:

```text
Django Ninja Router가 무엇인지 두 문장으로 설명해줘.

역할 분해나 dddjango 전체 workflow는 필요 없어.
```

with-dddjango 응답은 workflow ceremony를 출력하지 않았지만, 두 문장 중 실제 설명은 한 문장뿐이고 두 번째 문장을 “명령/검증 미실행 보고”로 사용했다. oracle은 이를 `두 문장 설명 요청 미충족`으로 fail 처리했다.

원인 분류:

| 분류 | 판단 | 근거 |
|---|---|---|
| eval/oracle 문제 | 낮음 | oracle은 `두 문장 설명`, `역할 분해 금지`, `workflow ceremony 금지`를 명확히 요구한다. 채점 기준은 과도하지 않다. |
| public case 문제 | 낮음 | 사용자가 “두 문장”과 “workflow 불필요”를 직접 말한다. 평가하려는 tiny-task restraint를 충분히 유도한다. |
| skill 문제 | 높음 | `workflow-dddjango-subagents`는 “short explanation은 직접 답하라”고 하지만, 직접 답변 모드에서 요청한 출력 형식을 보존하고 검증/명령 footer를 붙이지 말라는 지침이 없다. |
| plugin 문제 | 낮음 | workflow role map, handoff, subagent 섹션은 출력되지 않았다. 즉 skill trigger/routing의 큰 실패는 아니다. |
| reference 문제 | 중간 | `delegation-rules.md`의 `When To Stay Direct`가 직접 답변을 말하지만, “직접 답변이면 dddjango 완료 보고를 생략하라”까지는 닫지 않는다. |
| 모델 한계 | 중간 | 일반적인 command honesty 습관이 짧은 답변 형식과 충돌했다. 다만 skill/reference로 억제 가능하다. |

결론: 평가/문제보다 `workflow` skill의 negative path 지침이 부족하다. 특히 “workflow를 쓰지 말아야 하는 경우”를 정했지만, 그 경우 최종 응답을 어떻게 짧게 끝내야 하는지 부족하다.

## 3. 수정 위치 결정

1차 수정 위치:

- `dddjango/skills/workflow-dddjango-subagents/SKILL.md`
- `dddjango/skills/workflow-dddjango-subagents/references/delegation-rules.md`

수정 방향:

- `SKILL.md`의 Routing 또는 Runtime Rules에 `Direct Answer Mode`를 추가한다.
- `delegation-rules.md`의 `When To Stay Direct`에 출력 제한을 추가한다.
- 내용은 짧게 유지한다. skill-creator 기준으로 자세한 예시는 reference에 두고, `SKILL.md`에는 핵심 규칙만 둔다.

추가 수정 후보:

- `dddjango/skills/workflow-dddjango-subagents/agents/openai.yaml`: 현재 default prompt는 role-decomposed workflow에 맞춰져 있고 tiny case의 직접 원인은 아니다. 이번 루프에서는 수정하지 않는다.
- `dddjango/skills/implementation-django-ninja/SKILL.md`: targeted eval 중 실제로 short Django Ninja explanation에서 로드되는 skill로 확인되면, direct answer output discipline을 함께 보강한다. 단, case-specific 정답 문구는 넣지 않는다.
- `dddjango/.codex-plugin/plugin.json`, `.agents/plugins/marketplace.json`: routing/cache/source 불일치 증거가 없다. 이번 루프에서는 수정하지 않는다.
- `workspace/develop/eval/workflow/answer/case-workflow-tiny-restraint.yaml`: oracle은 적절하므로 수정하지 않는다.
- `workspace/develop/eval/workflow/cases/plugin/public/case-workflow-tiny-restraint.md`: public case가 명확하므로 수정하지 않는다.

## 4. 작은 수정안

`SKILL.md`에는 다음 의미의 규칙만 추가한다.

```text
Direct Answer Mode: If the routing decision is to stay direct because the task is a short explanation, tiny rename, simple local edit, or explicit opt-out, preserve the user's requested output shape. Do not add Role Map, Handoff Contract, Integration Checklist, subagent status, validation footer, or command-honesty boilerplate unless the user asked for work performed or you actually changed files/run commands.
```

`delegation-rules.md`에는 다음 의미를 추가한다.

```text
When staying direct, answer with the relevant content only. If the user asks for two sentences, both sentences should answer the question. Do not spend one of the requested sentences on meta-reporting such as tests not run, commands not run, or no subagents used unless that is the user's question.
```

이 수정은 평가 정답 문구를 skill에 넣는 방식이 아니다. `case-workflow-tiny-restraint`에만 맞춘 target phrase가 아니라, short explanation과 opt-out 계열 전체에 적용되는 일반 규칙이다.

## 5. 재평가 계획

수정 후 targeted rerun:

```bash
python3 -B workspace/scripts/run_initial_eval.py \
  --bucket workflow \
  --run-id 20260511-workflow-tiny-restraint-fix \
  --case case-workflow-tiny-restraint \
  --model gpt-5.5 \
  --reasoning xhigh \
  --evaluator-model gpt-5.5 \
  --evaluator-reasoning high \
  --rerun
```

인접 회귀 확인:

```bash
python3 -B workspace/scripts/run_initial_eval.py \
  --bucket workflow \
  --run-id 20260511-workflow-direct-mode-regression \
  --case case-workflow-opt-out \
  --case case-workflow-sequential-fallback \
  --model gpt-5.5 \
  --reasoning xhigh \
  --evaluator-model gpt-5.5 \
  --evaluator-reasoning high \
  --rerun
```

최소 성공 기준:

- `case-workflow-tiny-restraint` with-dddjango가 pass 또는 최소 4 / 5 이상.
- `case-workflow-opt-out`에서 role map/handoff/checklist가 계속 나오지 않음.
- `case-workflow-sequential-fallback`에서 필요한 workflow sections와 delegation honesty가 유지됨.
- generated `runs/`, report html, raw output은 커밋하지 않음.

## 6. 커밋 계획

try-1 기록 커밋에는 다음만 포함한다.

- `workspace/develop/lv_up_plan/plan_guide.md`
- `workspace/develop/lv_up_plan/workflow/analysis/try-1-workflow-failure-classification.md`
- `workspace/develop/lv_up_plan/workflow/plan/try-1-direct-answer-mode-plan.md`

다음 구현 커밋에는 다음 후보만 포함한다.

- `dddjango/skills/workflow-dddjango-subagents/SKILL.md`
- `dddjango/skills/workflow-dddjango-subagents/references/delegation-rules.md`
- 필요 시 cache sync 대상 파일

커밋 제외:

- `workspace/develop/eval/*/runs/**`
- raw transcript
- generated report html
- temp log/cache

## 7. 다음 액션

다음 단계는 이 문서의 P0 수정안만 적용하는 것이다. 수정 후 `case-workflow-tiny-restraint`를 먼저 재실행하고, 통과하면 `case-workflow-opt-out`, `case-workflow-sequential-fallback`으로 회귀를 확인한다.

## 8. 구현 중 추가 관찰

`workflow-dddjango-subagents`만 보강한 뒤 targeted eval을 실행하자, 실제 with-ddjango 응답은 `implementation-django-ninja`와 `using-superpowers` skill loading 명령을 최종 답변에 보고했다. 즉 P0 실패의 직접 출력 경로는 workflow skill 하나가 아니라, short Django Ninja explanation을 처리하는 `implementation-django-ninja`의 answer-only output discipline까지 포함한다.

추가 결론:

- `workflow-dddjango-subagents`: opt-out/direct path 원칙을 닫는 공통 위치로 유지한다.
- `implementation-django-ninja`: short Django Ninja explanation의 실제 처리 위치이므로 `Output Shape`를 추가한다.
- installed plugin cache: eval runtime이 `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/...`를 읽으므로, targeted eval 전 workspace canonical source와 cache를 동기화해야 한다.
