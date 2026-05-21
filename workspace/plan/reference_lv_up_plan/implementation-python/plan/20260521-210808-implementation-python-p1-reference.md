수정 대상: reference

## 수정 이유

runtime skill은 pydantic v2를 외부 DTO/config/runtime validation boundary로 제한하고 `Enum/StrEnum`을 finite state 표현으로 안내한다. source reference가 이 판단을 명시적으로 뒷받침해야 skill만 앞서가는 상태를 피할 수 있다.

## 수정 범위

- `workspace/reference/implementation-python/reference/final.md`
  - `Enum` 섹션에 Python target이 허용할 때 `StrEnum`을 우선 고려하고, 낮은 target에서는 `str, Enum`을 사용하는 기준을 추가한다.
  - pydantic v2 섹션에 boundary rule을 추가한다.
  - pydantic validation error와 domain invariant의 책임 경계를 명시한다.

## 수정하지 말아야 할 범위

- source reference 전체를 runtime reference 형태로 축약하지 않는다.
- pydantic을 기본 domain model로 권장하지 않는다.
- Django Ninja Schema/API serialization 결정은 `implementation-django-ninja` 책임으로 남긴다.
- eval case, answer oracle, fixture는 수정하지 않는다.

## 작업 체크리스트

- [x] `Enum` 섹션에 `StrEnum` version gate 추가
- [x] pydantic v2 boundary rule 추가
- [x] reference 수정 후 skill reflection gap을 별도 평가
- [x] validator 실행

## 검증 명령

- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`

## 완료 조건

- pydantic v2 boundary와 `StrEnum` 기준이 source reference에서 직접 확인된다.
- source reference가 필수 판단 축을 모두 충분히 뒷받침한다.
- reference 관련 Blocker 0, Major 0, 열린 Minor 0 상태가 재평가로 확인된다.

## 완료 확인

- `workspace/reference/implementation-python/reference/final.md`에 `Enum/StrEnum` 기준과 pydantic v2 boundary 결정이 추가됐다.
- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py` 통과.
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills` 통과.
