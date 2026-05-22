수정 대상: evaluator
원인 분류: evaluator

# implementation-python code 평가 validator 분석

## 문제

skill-creator 관점 real subagent 리뷰에서 `code` bucket의 `case-code-python-state`가 implementation-python code-backed 대표 case인데도 validator가 이를 implementation-python case로 검증하지 못한다는 Blocker가 확인됐다.

현재 상태:

- `workspace/scripts/validate_eval_bucket_pack.py`는 `response` bucket에서만 `validate_implementation_python_answer()`를 호출한다.
- `code` bucket coverage는 implementation-django, implementation-django-web만 추가 확인한다.
- `workspace/develop/eval/code/answer/case-code-python-state.yaml`은 `implementation-python` tag가 없고, runtime skill/bundled reference basis도 없다.

## 영향

P4 기준 1, 4, 5를 만족하지 못한다. code-backed Python case가 source reference와 runtime bundled reference를 실제로 기준으로 삼지 않아도 bucket validator가 통과할 수 있다.

## 수정 방향

- `case-code-python-state.yaml`을 implementation-python code-backed case로 명시한다.
- answer oracle에 `dddjango/skills/implementation-python/SKILL.md`, `typing.md`, `dataclasses-enums.md`, `protocols-boundaries.md`, `pydantic-v2.md` reference basis를 추가한다.
- `validate_eval_bucket_pack.py`에 code bucket용 implementation-python coverage set과 direct coverage 확인을 추가한다.
- code bucket에서도 `validate_implementation_python_answer()`를 호출한다.
- unit test로 coverage/tag/reference 누락을 실패로 만든다.

## 리뷰 방식

리뷰 방식: real-subagent

Subagent 리뷰/순차 fallback: skill-creator 관점 real subagent가 Blocker 1, Major 2, Minor 3을 보고했다. 이 문서는 Blocker와 Major 중 eval validator/answer에 해당하는 항목을 닫기 위한 후속 분석이다.

skill-creator 리뷰: validation integrity Blocker, code answer traceability Major, implementation-python tag 누락 Major.

리뷰 결과: Blocker 1, Major 2, 열린 Minor 0
