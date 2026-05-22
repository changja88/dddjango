수정 대상: runtime-sync

# workflow subagent honesty runtime sync 계획

## 수정 범위

- 동기화 대상: `dddjango/skills/workflow-dddjango-subagents/SKILL.md`
- 동기화 대상: `dddjango/skills/workflow-dddjango-subagents/agents/openai.yaml`
- 동기화 대상: `dddjango/skills/workflow-dddjango-subagents/references/delegation-rules.md`
- runtime cache 대상: installed `dddjango-local` cache의 동일 skill 경로

## 절차

1. canonical source 세 파일을 runtime cache 동일 경로로 복사한다.
2. `validate_skill_docs.py --phase all --skills-dir dddjango/skills`로 cache/source parity를 확인한다.
3. 최종 보고에 cache sync 여부와 validator 결과를 남긴다.

## 검증

- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`
- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`

## 완료 조건

- runtime cache differs 오류가 사라진다.
- canonical source와 runtime cache의 workflow subagent honesty 문구가 일치한다.
