# implementation-tdd P3 skill 수정 계획

## 수정 이유

`implementation-tdd`는 TDD 방법론과 Red-Green-Refactor 실행 순서를 맡는다. 현재 `SKILL.md`는 API/DB/구현/test mechanics/workflow handoff는 명확하지만, 테스트 기대값을 고정하기 전에 도메인 정책, invariant, use case ownership이 불명확한 경우의 architecture handoff가 약하다. 또한 UI metadata의 `test strategy` 표현이 `implementation-test` 책임과 넓게 겹쳐 보인다.

## 수정 범위

- `dddjango/skills/implementation-tdd/SKILL.md`
  - routing에 불명확한 domain policy, invariant, use case ownership은 `architecture-ddd`에서 먼저 결정한다는 handoff를 추가한다.
  - security/performance가 주된 위험이면 TDD loop만으로 닫지 않고 관련 architecture/implementation/workflow skill로 넘긴다는 handoff를 추가한다.
  - legacy/refactoring strategy가 주된 이슈이면 `implementation-cleancode`와 협업한다는 handoff를 추가한다.
  - ambiguous policy runtime rule에 unresolved domain decisions는 `architecture-ddd`로 넘긴다는 문장을 보강한다.
  - `BDD/ATDD` 관계 reference를 1단계 직접 링크로 추가한다.
  - 기존 validator가 요구하는 validity-window boundary guardrail 문구는 유지한다.
- `dddjango/skills/implementation-tdd/agents/openai.yaml`
  - `short_description`을 broad test strategy가 아니라 TDD cycle과 first failing test 중심으로 좁힌다.
- `dddjango/skills/implementation-tdd/references/bdd-atdd.md`
  - BDD/ATDD 관계와 pytest-bdd/Gherkin 구현 세부 handoff를 짧게 정리한다.

## 수정하지 말아야 할 범위

- `workspace/reference/implementation-tdd/reference/**`는 이번 P3 skill 수정에서 직접 고치지 않는다.
- `implementation-test`, architecture skills, workflow skill은 수정하지 않는다.
- pytest fixture/mock/factory, property-based, coverage, mutation, testcontainers, pytest-bdd/Gherkin 구현 세부를 `implementation-tdd`로 가져오지 않는다.
- `SKILL.md`에 source reference 본문의 긴 예시나 상세 testing pattern을 복사하지 않는다.
- BDD/ATDD reference는 방법론 관계와 routing만 담고, pytest-bdd 구현 방법은 `implementation-test`로 넘긴다.

## 체크리스트

- [ ] domain policy/invariant/use case ownership handoff를 `architecture-ddd`로 명시한다.
- [ ] security/performance handoff를 runtime routing에 명시한다.
- [ ] legacy/characterization/refactoring handoff를 runtime routing에 명시한다.
- [ ] ambiguous policy rule이 TDD 책임과 architecture handoff를 함께 드러낸다.
- [ ] BDD/ATDD 관계가 bundled reference로 1단계 발견 가능하다.
- [ ] UI metadata가 `implementation-test`와 겹치는 broad test strategy 표현을 줄인다.
- [ ] bundled reference 링크는 1단계 직접 링크 상태를 유지한다.
- [ ] runtime cache sync 분석/계획을 별도로 작성하고 cache를 동기화한다.
- [ ] real-subagent 리뷰 결과를 통합해 Blocker/Major/열린 Minor를 닫는다.

## 검증 명령

```bash
.venv/bin/python -B workspace/scripts/validate_plan_constraints.py
.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py
.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills
diff -qr dddjango/skills/implementation-tdd /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-tdd
```

## 완료 조건

- 직접 책임과 handoff 기준이 명확하다.
- 다른 skill과 책임이 충돌하거나 중복되지 않는다.
- `SKILL.md`는 핵심 절차와 routing 중심으로 500줄 미만을 유지한다.
- bundled references는 `SKILL.md`에서 직접 발견 가능하다.
- source skill과 runtime cache가 동일하다.
- 검증 명령이 통과하고 리뷰 결과가 Blocker 0, Major 0, 열린 Minor 0이다.
