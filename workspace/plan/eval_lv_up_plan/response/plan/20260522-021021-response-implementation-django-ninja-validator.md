수정 대상: evaluator

목표:

- response bucket validator가 implementation-django-ninja P4 coverage 누락과 answer/source basis 누락을 구조적으로 탐지하게 한다.

수정 순서:

1. `workspace/scripts/validate_eval_bucket_pack.py`에 `RESPONSE_IMPLEMENTATION_DJANGO_NINJA_P4_COVERAGE_TAGS`를 추가한다.
2. `validate_implementation_django_ninja_answer`를 추가해 required reference와 bundled reference를 확인한다.
3. response bucket answer 검증과 coverage 검증 경로에 새 validator를 연결한다.
4. `workspace/scripts/test_validate_eval_bucket_pack.py`에 coverage tag set 누락 테스트와 source/runtime basis 누락 테스트를 추가한다.

검증:

- `.venv/bin/python -B workspace/scripts/test_validate_eval_bucket_pack.py`
- `.venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket response`

완료 조건:

- implementation-django-ninja P4 coverage tags가 빠진 response pack은 실패한다.
- implementation-django-ninja answer가 source reference, SKILL.md, bundled reference 없이 통과하지 않는다.
- 기존 다른 bucket 검증 요구를 약화하지 않는다.
