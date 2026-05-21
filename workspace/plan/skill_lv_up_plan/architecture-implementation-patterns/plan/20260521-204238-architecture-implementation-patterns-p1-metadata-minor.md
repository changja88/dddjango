수정 대상: skill

# architecture-implementation-patterns P1 metadata Minor 수정 계획

## 수정 이유

Runtime guidance는 충분하지만 UI metadata default prompt가 risky write/transaction-boundary 진입점을 과소대표한다. 열린 Minor 0으로 닫기 위해 metadata를 source skill 표면과 맞춘다.

## 수정 범위

- `dddjango/skills/architecture-implementation-patterns/agents/openai.yaml`

## 수정하지 말아야 할 범위

- Source reference는 수정하지 않는다.
- `SKILL.md`와 bundled references는 해당 Minor의 원인이 아니므로 불필요하게 수정하지 않는다.
- eval pack은 수정하지 않는다.

## 작업 체크리스트

- [ ] `default_prompt` 한 문장 안에 risky-write transaction/side-effect/idempotency handoff를 포함한다.
- [ ] Runtime cache를 재동기화한다.
- [ ] source/runtime diff와 validator를 재실행한다.
- [ ] 리뷰 결과가 Blocker 0, Major 0, 열린 Minor 0인지 재확인한다.

## 검증 명령

- `diff -qr dddjango/skills/architecture-implementation-patterns /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/architecture-implementation-patterns`
- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`

## 완료 조건

- `agents/openai.yaml`이 pattern selection과 risky-write boundary entrypoint를 모두 드러낸다.
- Source/runtime cache가 동일하다.
- Validator가 모두 통과한다.
- 열린 Minor가 없다.
