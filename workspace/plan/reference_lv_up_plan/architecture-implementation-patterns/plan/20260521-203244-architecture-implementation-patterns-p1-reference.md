수정 대상: reference

# architecture-implementation-patterns P1 reference 개선 계획

## 수정 이유

`architecture-implementation-patterns` skill이 fallback source 상태로 운영되고 있어 P1 종료 조건인 source reference 충분성을 만족하지 못한다. 전용 `final.md`를 생성해 구현 아키텍처 패턴 선택 기준과 handoff 기준을 source reference로 고정한다.

## 수정 범위

- 생성: `workspace/reference/architecture-implementation-patterns/reference/final.md`
- 포함 기준: layered architecture, clean architecture, hexagonal architecture, ports/adapters, dependency direction/DIP, repository, Unit of Work, CQRS, event sourcing, saga, outbox, ACL, service layer
- 포함 근거: 기존 `architecture-ddd`, `implementation-django`, `implementation-python` source reference의 관련 결정과 dddjango runtime skill에서 이미 사용 중인 fallback 판단 기준

## 수정하지 말아야 할 범위

- eval case, answer oracle, evaluator는 P1 reference 생성 루프에서 수정하지 않는다.
- 기존 `architecture-ddd`, `implementation-django`, `implementation-python` source reference의 분리 예정 문구는 이번 범위에서 직접 수정하지 않는다.
- Django 구체 구현 코드, migration, API 계약, DB locking/isolation 상세는 각 owning skill reference로 넘긴다.

## 작업 체크리스트

- [ ] reference 폴더를 생성한다.
- [ ] `final.md`에 source 역할, 적용 순서, 패턴별 선택/회피 기준을 작성한다.
- [ ] 위험 쓰기에서 `Risky Write Consistency Block`에 필요한 pattern-level 판단 항목을 정의한다.
- [ ] 다른 owning skill로 넘길 범위를 명시한다.
- [ ] reference 생성 후 skill 반영 부족 여부를 재평가한다.

## 검증 명령

- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`

## 완료 조건

- `workspace/reference/architecture-implementation-patterns/reference/final.md`가 존재한다.
- P1 대상 패턴의 선택 기준, 회피 기준, handoff 기준을 판단할 수 있다.
- reference 생성 후 skill 문서의 fallback/provisional 문구와 bundled reference 반영 부족을 별도 skill 분석 대상으로 분리할 수 있다.
