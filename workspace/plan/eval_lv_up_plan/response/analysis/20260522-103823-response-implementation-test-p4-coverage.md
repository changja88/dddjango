수정 대상: case
원인 분류: case

# implementation-test response P4 분석

## 문제

`implementation-test`는 pytest 구조, fixture/conftest, parametrization, assertion, test double, factory_boy/Faker, Hypothesis, time/HTTP mocking, testcontainers, coverage/mutation, BDD, flaky test, Django Ninja TestClient, idempotency/concurrency test를 다루는 개별 skill이다. 현재 response bucket에는 `case-response-coupon-ambiguity`와 `case-response-order-create`가 implementation-test source를 일부 참조하지만, 각각 TDD ambiguity 또는 DDD/DB/API mixed 설계 case라서 P4의 개별 implementation-test 목적을 직접 검증하지 못한다.

## 영향

- 관련 source reference가 존재해도 개별 skill trigger와 positive runtime behavior가 직접 평가되지 않는다.
- mixed order-create case가 API/DB/DDD 연계 검증으로 implementation-test coverage를 대체할 위험이 있다.
- 작은 assertion 질문에서 Direct Answer 경계를 지키는 negative case가 없어 `implementation-test`가 과적용되는지 확인하기 어렵다.

## 수정 방향

- response public case를 추가해 파일 수정 없는 테스트 전략/리뷰 상황에서 implementation-test가 직접 선택되어야 하는 조건을 검증한다.
- 같은 bucket에 tiny assertion negative case를 추가해 `pytest.approx` 수준의 직접 답변과 workflow/TDD/DDD 과적용 방지를 검증한다.
- answer oracle은 source reference와 bundled runtime references에 있는 테스트 구현 기준만 요구하고, public prompt에 private oracle이나 이전 run finding을 노출하지 않는다.
- evaluator에 direct implementation-test coverage 함수를 추가해 mixed/P5 인접 tag가 개별 skill coverage로 계산되지 않도록 한다.

## 리뷰 방식

리뷰 방식: not-run

Subagent 리뷰/순차 fallback: 초기 원인 분류 단계에서는 아직 수정 전이라 real subagent 리뷰를 실행하지 않았다. 수정 후 별도 skill-creator 관점 subagent와 독립 subagent 리뷰로 Blocker/Major/Minor를 닫는다.

리뷰 결과: Blocker 0, Major 1, 열린 Minor 0
