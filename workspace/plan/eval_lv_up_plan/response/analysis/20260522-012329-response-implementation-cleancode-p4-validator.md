수정 대상: evaluator

# implementation-cleancode P4 evaluator 분석

## 배경

현재 `workspace/scripts/validate_eval_bucket_pack.py`는 response bucket에 architecture-db, architecture-api, architecture-implementation-patterns P4 coverage tag 집합을 강제한다. 반면 `implementation-cleancode` P4의 핵심 축은 validator에 고정되어 있지 않아, 관련 case가 사라지거나 축이 빠져도 bucket validator가 통과할 수 있다.

## 현재 증거

- validator 상수:
  - `RESPONSE_ARCHITECTURE_DB_P4_COVERAGE_TAGS`
  - `RESPONSE_ARCHITECTURE_API_P4_COVERAGE_TAGS`
  - `RESPONSE_ARCHITECTURE_IMPLEMENTATION_PATTERNS_P4_COVERAGE_TAGS`
- clean-code 관련 coverage는 `REQUIRED_COVERAGE_TAGS["response"]`에도 직접 포함되어 있지 않고, P4 전용 누락 메시지도 없다.
- `workspace/scripts/test_validate_eval_bucket_pack.py`도 clean-code P4 coverage 누락을 실패시키는 테스트가 없다.

## gap 분류

Major. case/answer를 보강하더라도 evaluator가 개별 skill 목적 축을 강제하지 않으면 P4 완료 상태를 유지할 수 없다.

리뷰 방식: not-run

리뷰 결과: Blocker 0, Major 1, 열린 Minor 0

## 수정 방향

- response bucket에 `RESPONSE_IMPLEMENTATION_CLEANCODE_P4_COVERAGE_TAGS`를 추가한다.
- P4 목표의 축을 tag로 구조화한다.
- validator가 해당 tag 누락 시 `response: implementation-cleancode P4 coverage_tags missing` finding을 내도록 한다.
- validator unit test를 추가해 누락 감지를 보존한다.
