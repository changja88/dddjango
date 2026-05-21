# implementation-tdd P1 runtime sync 계획

## 수정 이유

P1 skill metadata 보강 후 source skill과 runtime cache가 달라졌다. runtime cache가 stale 상태면 실제 runtime에서 수정된 metadata를 사용하지 못하므로 cache 동기화가 필요하다.

## 수정 범위

- `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-tdd/agents/openai.yaml`
  - `dddjango/skills/implementation-tdd/agents/openai.yaml`와 동일하게 동기화한다.

## 수정하지 말아야 할 범위

- `SKILL.md`와 `references/*.md`는 source와 runtime cache가 동일하므로 건드리지 않는다.
- source reference, eval case, answer oracle, evaluator는 runtime-sync 범위가 아니다.

## 작업 체크리스트

- [ ] source `agents/openai.yaml`을 runtime cache 위치로 복사한다.
- [ ] `diff -qr`로 source skill과 runtime cache가 동일한지 확인한다.
- [ ] validators를 실행한다.
- [ ] subagent 리뷰와 메인 재평가를 통합해 Blocker 0, Major 0, 열린 Minor 0 상태를 확인한다.

## 검증 명령

- `diff -qr dddjango/skills/implementation-tdd /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-tdd`
- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`

## 완료 조건

- runtime cache와 source skill diff가 없다.
- 지정 validators가 통과한다.
- runtime-sync 관련 Blocker, Major, 열린 Minor가 0이다.
