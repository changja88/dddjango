# implementation-cleancode P1 reference 수정 계획

## 수정 이유

`implementation-cleancode` skill은 Fat Model, Fat View, View/Router 비즈니스 로직, 책임 분리와 유지보수성 리뷰를 다룬다. 현재 source reference는 범용 클린 코드 기준은 충분하지만 Django/dddjango의 model/view/router/schema/template에 비즈니스 규칙이 들어가는 경우를 직접 판단할 근거가 부족하다.

## 수정 범위

- 수정 대상:
  - `workspace/reference/implementation-cleancode/reference/final.md`
- 추가 내용:
  - Django/dddjango 경계에서 Fat Model, Fat View, Fat Router/Schema/Template smell을 판정하는 기준
  - service/selector/use case/domain object로 이동할 때의 주의점
  - clean-code skill과 architecture-ddd/api/db/django skill의 역할 경계

## 수정하지 말아야 할 범위

- `workspace/develop/eval/**` 평가 case, answer, evaluator는 수정하지 않는다.
- 다른 reference area나 다른 skill은 이 reference 계획에서 수정하지 않는다.
- reference를 skill 지침처럼 과도하게 명령형으로 바꾸지 않는다.
- Django 구현 세부, DB transaction, API contract, DDD aggregate 결정은 이 reference에서 확정하지 않고 해당 전문 skill로 라우팅한다.

## 작업 체크리스트

- [ ] `final.md`에서 책임 분리와 framework boundary smell을 연결할 위치를 정한다.
- [ ] Django/dddjango 특화 smell 기준을 추가한다.
- [ ] 범용 원칙과 충돌하지 않는지 확인한다.
- [ ] 이후 skill 반영 분석에서 bundled reference와 `SKILL.md`가 보강된 source를 반영하는지 확인한다.

## 검증 명령

- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`

## 완료 조건

- `final.md`가 responsibility separation, naming, function shape, encapsulation, abstraction, SOLID, duplication, error handling, legacy review, fat model/view/router, maintainability를 모두 판단할 source 근거를 제공한다.
- plan/analysis 파일명이 같고, analysis 첫 줄이 `수정 대상: reference` 형식을 만족한다.
- reference 보강 후 skill 반영 부족 여부를 별도로 평가할 수 있다.
