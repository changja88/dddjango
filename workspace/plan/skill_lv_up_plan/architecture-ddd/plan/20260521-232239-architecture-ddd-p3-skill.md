# architecture-ddd P3 skill 수정 계획

## 수정 이유

P3 평가에서 `architecture-ddd`의 risky write handoff가 DB/API/Test 책임은 명확히 나누지만, outbox, saga, ACL, repository/UoW, transaction owner pattern 같은 구현 아키텍처 선택을 `architecture-implementation-patterns`로 넘기는 기준을 명시하지 않는 문제가 확인됐다. 이 기준을 좁게 보강해 DDD skill이 구현 패턴 결정을 직접 소유하지 않도록 한다.

## 수정 범위

- `dddjango/skills/architecture-ddd/SKILL.md`

## 수정하지 말아야 할 범위

- `workspace/reference/architecture-ddd/**`는 이번 P3에서 source gap으로 보지 않으므로 수정하지 않는다.
- bundled references는 직접 링크와 세부 자료 분리가 이미 충분하므로 수정하지 않는다.
- 다른 skill의 routing이나 runtime rules는 수정하지 않는다.
- eval case, answer oracle, evaluator, report는 이번 범위가 아니다.

## 작업 체크리스트

- [x] risky write runtime rule에 `architecture-implementation-patterns` handoff를 추가한다.
- [x] DDD-owned decision과 implementation-pattern, DB, API, Test-owned decision을 한 문장 안에서 분리한다.
- [x] TDD sequencing 요청 handoff를 `implementation-tdd` 책임으로 드러낸다.
- [x] source skill과 runtime cache 차이를 확인한다.
- [x] runtime cache 차이가 있으면 runtime-sync 분석/계획을 작성하고 cache를 동기화한다.
- [x] `skill-creator` 관점 리뷰와 독립 P3 리뷰를 수행한다.
- [x] 검증 명령과 `diff -qr`를 실행한다.

## 검증 명령

```bash
.venv/bin/python -B workspace/scripts/validate_plan_constraints.py
.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py
.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills
diff -qr dddjango/skills/architecture-ddd /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/architecture-ddd
```

## 완료 조건

- `architecture-ddd`의 직접 책임과 handoff 기준이 충돌 없이 드러난다.
- `architecture-implementation-patterns`, `architecture-db`, `architecture-api`, `implementation-test`, `workflow-dddjango-subagents`와 책임이 겹치지 않는다.
- `SKILL.md`는 500줄 미만이며 핵심 절차와 routing 판단만 담는다.
- bundled references는 `SKILL.md`에서 1단계 직접 링크로 발견 가능하다.
- source skill과 runtime cache가 동기화되어 있다.
- 리뷰와 검증 결과 Blocker 0, Major 0, 열린 Minor 0이다.
