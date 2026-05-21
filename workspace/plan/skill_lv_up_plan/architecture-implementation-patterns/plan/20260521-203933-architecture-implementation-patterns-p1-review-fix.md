수정 대상: skill

# architecture-implementation-patterns P1 리뷰 보완 계획

## 수정 이유

실제 subagent 리뷰에서 남은 Major와 열린 Minor가 모두 runtime skill의 source 반영 누락으로 분류됐다. Dedicated source reference의 기준을 runtime-facing skill과 bundled references에 더 직접적으로 반영해 Blocker 0, Major 0, 열린 Minor 0 상태로 닫는다.

## 수정 범위

- `dddjango/skills/architecture-implementation-patterns/SKILL.md`
- `dddjango/skills/architecture-implementation-patterns/references/pattern-selection.md`
- `dddjango/skills/architecture-implementation-patterns/references/ports-adapters.md`
- `dddjango/skills/architecture-implementation-patterns/references/outbox-acl.md`
- `dddjango/skills/architecture-implementation-patterns/agents/openai.yaml`

## 수정하지 말아야 할 범위

- `workspace/reference/architecture-implementation-patterns/reference/final.md`는 이미 충분하므로 이번 보완에서 바꾸지 않는다.
- `repository-uow.md`는 리뷰 항목과 직접 관련이 없어 불필요하게 수정하지 않는다.
- eval case, answer, evaluator는 수정하지 않는다.

## 작업 체크리스트

- [ ] `transaction script` 표현을 source reference와 맞는 simple flow 또는 straightforward service function 표현으로 바꾼다.
- [ ] `agents/openai.yaml` default prompt에 layered/clean/hexagonal, CQRS, event sourcing을 포함한다.
- [ ] Risky Write Consistency Block API handoff에 `Idempotency-Key`, status code, Problem Details를 포함한다.
- [ ] CQRS와 saga 기준에 eventual consistency 수용 조건을 추가한다.
- [ ] Layered architecture 계층별 허용/금지 책임표를 bundled reference에 추가한다.
- [ ] Clean/hexagonal 선택 기준에 failure isolation과 contract stability를 명시한다.
- [ ] Source skill 수정 후 runtime cache를 재동기화한다.

## 검증 명령

- `diff -qr dddjango/skills/architecture-implementation-patterns /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/architecture-implementation-patterns`
- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`

## 완료 조건

- Subagent가 지적한 Major와 Minor가 모두 runtime source 반영으로 해소된다.
- Runtime cache와 source skill이 다시 동일하다.
- 세 validator가 통과한다.
- 최종 리뷰 결과가 Blocker 0, Major 0, 열린 Minor 0이다.
