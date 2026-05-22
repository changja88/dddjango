수정 대상: answer
원인 분류: answer undercheck

# response answer validator term follow-up 분석

## 문제

`validate_eval_bucket_pack.py --bucket response`가 `implementation-django-ninja`와 `implementation-test` direct answer oracle의 `target_behavior.required`에서 source-backed 핵심 용어를 구조적으로 검사한다. 현재 answer oracle 일부는 같은 의도를 담고 있지만 validator가 요구하는 paired terms를 충분히 명시하지 않아 response bucket validation이 실패했다.

## 대상

| bucket | case id | 원인 | 수정 여부 | targeted eval 필요 |
|---|---|---|---|---|
| response | `case-response-django-ninja-endpoint` | DRF-to-Ninja migration compatibility 표현 부족 | answer 수정 | 예 |
| response | `case-response-drf-ninja` | Schema/ModelSchema, auth/permission, filtering/sorting 표현 부족 | answer 수정 | 예 |
| response | `case-response-test-suite-strategy` | conftest, assertions, doubles, factory, property invariant, BDD stakeholder, flaky concurrency 표현 부족 | answer 수정 | 예 |

## 판단

- public case는 수정하지 않는다. 사용자-facing prompt에는 private oracle이나 이전 run finding 누설이 없다.
- source reference와 runtime skill은 기준을 충분히 제공한다.
- evaluator는 강화된 구조 검사를 이미 제공하고 있으므로 이번 수정은 answer oracle wording 보강이다.
- answer oracle은 reference보다 과도한 새 요구를 추가하지 않고, 기존 source reference와 bundled reference에 있는 개념을 validator가 읽을 수 있게 명시한다.

## 리뷰 방식

리뷰 방식: sequential-fallback

리뷰 결과: Blocker 0, Major 0, 열린 Minor 0

Subagent 리뷰/순차 fallback: 이전 real-subagent review에서 implementation-django-ninja validation integrity 문제를 지적했고, 이번 분석은 validator 통과를 위한 answer wording 후속이다. 별도 real-subagent는 targeted eval sandbox blocker가 먼저 남아 있어 실행하지 않았다.
