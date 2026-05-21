# implementation-cleancode P2 runtime sync 계획

## 수정 이유

P2 source skill 수정 후 runtime cache의 `SKILL.md`와 `agents/openai.yaml`이 source와 달라졌다. runtime에서 최신 trigger, 제외 조건, UI metadata가 사용되도록 cache를 동기화해야 한다.

## 수정 범위

- `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-cleancode/SKILL.md`
- `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-cleancode/agents/openai.yaml`

## 수정하지 말아야 할 범위

- runtime cache의 다른 skill은 수정하지 않는다.
- `dddjango/skills/implementation-cleancode/references/*.md`는 P2에서 변경하지 않았으므로 별도 복사 대상으로 삼지 않는다.
- source reference, eval pack, validator script는 수정하지 않는다.

## 작업 체크리스트

- [x] source `SKILL.md`를 runtime cache `SKILL.md`로 복사한다.
- [x] source `agents/openai.yaml`을 runtime cache `agents/openai.yaml`로 복사한다.
- [x] `diff -qr`로 source/runtime parity를 확인한다.
- [x] 검증 명령을 다시 실행한다.
- [x] 리뷰 결과와 재평가에서 Blocker 0, Major 0, 열린 Minor 0인지 확인한다.

## 검증 명령

- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`
- `diff -qr dddjango/skills/implementation-cleancode /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-cleancode`

## 완료 조건

- runtime cache의 `implementation-cleancode` skill이 source skill과 일치한다.
- 검증 명령이 통과한다.
- runtime-sync 관련 열린 Blocker, Major, Minor가 없다.
