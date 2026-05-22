수정 대상: evaluator
원인 분류: evaluator

## 배경

최종 targeted re-review에서 `case-response-django-web-page`의 public case와 answer oracle은 form subpath를 명확히 요구하지만, `validate_eval_bucket_pack.py`의 `web-forms` 구조 검증은 `form`, `post`, `invalid/error` 정도만 확인한다는 Minor가 나왔다.

## 문제

- 구조 validator가 `GET`, `valid POST`, `invalid POST`, 사용자 회복 가능한 error rendering, `ModelForm.Meta.fields`를 모두 확인하지 않는다.
- `valid POST`는 `invalid POST` 문자열의 부분 문자열로 오인될 수 있으므로 단순 substring 검증도 충분하지 않다.

## 수정 방향

- Django Web response answer의 `web-forms` group을 form, GET, valid POST, invalid POST, error rendering, `ModelForm.Meta.fields` 단위로 강화한다.
- required term 검증을 단순 substring에서 token boundary를 고려하는 helper로 바꿔 `invalid POST`가 `valid POST`를 충족하지 못하게 한다.
- validator regression test를 강화한다.

## 리뷰 기록

리뷰 방식: real-subagent
리뷰 결과: Blocker 0, Major 0, 열린 Minor 1

Subagent 리뷰/순차 fallback: targeted re-review가 validator under-enforcement를 Minor로 보고했다.
