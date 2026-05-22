수정 대상: evaluator
원인 분류: evaluator

# architecture-ddd P4 response 평가 분석

## 문제

`response/eval_goal.md`는 Strategic DDD 평가에서 `subdomain`, `bounded context`, `context map`, `ubiquitous language`, `aggregate boundary`, `invariant`, `value object/entity`, `domain event`, `dispatch timing`, `outbox/eventual consistency`를 요구한다. 그러나 현재 response bucket에는 이 기준을 architecture-ddd 단일 skill 관점으로 직접 검증하는 case가 없고, `answer` schema validator도 DDD 관찰 필드를 구조적으로 요구하지 않는다.

현재 `case-response-order-create`는 DDD, DB, API, Django Ninja, Test가 결합된 mixed-boundary 사례라 P4의 개별 architecture-ddd skill 평가로만 보기 어렵다. workflow/subagent 결합 평가는 P5로 넘겨야 하므로 P4에서는 pure response 설계 case가 필요하다.

## 영향

- public case가 DDD 설계 목적을 묻더라도 answer oracle이 필수 관찰점을 빠뜨려도 validator가 통과할 수 있다.
- `case`, `answer`, `evaluator`가 같은 architecture-ddd 목적을 구조적으로 검증한다는 증거가 약하다.
- 개별 skill P4 종료 조건 중 DDD 기준 전체 coverage가 response bucket에서 직접 증명되지 않는다.

## 수정 방향

- response bucket에 architecture-ddd 전용 public case를 추가한다.
- matching answer oracle에 reference 기반 `ddd_observations`를 추가한다.
- `validate_eval_bucket_pack.py`가 response answer 중 `architecture-ddd-direct` coverage tag를 가진 case에 필수 DDD 관찰 필드를 요구하게 한다.
- public case에는 answer oracle, private 기준, 이전 run finding을 넣지 않는다.

## 리뷰 방식

리뷰 방식: not-run

현재 문서는 수정 전 원인 분석이며, 실제 subagent 리뷰는 수정과 검증 후 P4 통합 리뷰 단계에서 별도 실행한다.

리뷰 결과: Blocker 0, Major 0, 열린 Minor 0

