수정 대상: skill

# workflow subagent honesty Minor 수정 계획

## 수정 범위

- 수정: `dddjango/skills/workflow-dddjango-subagents/SKILL.md`
- 수정: `dddjango/skills/workflow-dddjango-subagents/references/delegation-rules.md`
- 수정: `dddjango/skills/workflow-dddjango-subagents/agents/openai.yaml`

## 절차

1. `SKILL.md`의 actual subagent reporting 규칙에 status ledger 필드를 추가한다.
2. `delegation-rules.md`의 real subagent 규칙에 동일 ledger와 validation honesty 문장을 추가한다.
3. `agents/openai.yaml` default prompt를 짧게 보강해 runtime metadata와 SKILL.md 의미를 맞춘다.
4. skill docs validator를 실행한다.

## 검증

- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`
- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`

## 완료 조건

- actual subagent result collection은 ledger로 확인하도록 안내된다.
- validation/eval/browser/Serena/subagent review false claim 금지가 delegation reference에서도 보인다.
- skill-creator Minor 3개가 열린 상태로 남지 않는다.
