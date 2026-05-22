수정 대상: evaluator

# implementation-django-ninja P4 fresh review Minor 수정 계획

## 대상

- `workspace/develop/eval/response/answer/case-response-drf-ninja.yaml`
- `workspace/scripts/validate_eval_bucket_pack.py`
- `workspace/scripts/test_validate_eval_bucket_pack.py`

## 계획

1. `case-response-drf-ninja.yaml`에서 broad `workspace/develop/eval` reference basis를 제거한다.
2. `has_implementation_django_ninja_direct_coverage()`에서 `case_id`가 `case-response-django-ninja-`로 시작하지 않으면 direct coverage로 보지 않는다.
3. unrelated response case가 full implementation-django-ninja tags와 refs를 갖더라도 direct coverage로 인정되지 않는 테스트를 추가한다.
4. response bucket validator와 validator tests를 실행한다.
5. 전체 필수 로컬 검증을 다시 실행한다.

## 완료 기준

- fresh review Minor 2건이 수정된다.
- response pack validator와 테스트가 통과한다.
- targeted eval pass evidence가 없는 Blocker는 별도 미완료 조건으로 남긴다.
