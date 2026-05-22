수정 대상: answer
원인 분류: answer underclaim

# coupon TDD code oracle boundary 분석

## 범위

- bucket: `code`
- case: `case-code-coupon-tdd`
- answer: `workspace/develop/eval/code/answer/case-code-coupon-tdd.yaml`

## 현재 상태

public case는 "최소 주문 금액 경계값, 만료일 당일, 이미 사용한 쿠폰"을 테스트하라고 요청한다. source reference는 boundary-driven policy에서 경계 자체와 가장 가까운 반대편 값을 함께 테스트 목록에 넣어야 한다고 한다.

현재 answer oracle은 "minimum amount boundary, expiration day, expired coupon, used coupon"을 요구하지만 최소 주문 금액의 accepted/rejected pair를 명시하지 않아 boundary cases 기준을 덜 검증한다.

## 판단

원인은 answer underclaim이다. public case는 경계값을 충분히 유도하고 있으므로 public 문구를 고치지 않고 answer oracle에서 source 기준에 맞춰 nearest rejected/complement expectation을 명시한다.

## Inventory

| bucket | case id | public | answer | evaluator 관련성 | 수정 여부 | targeted eval 필요 | run id | status |
|---|---|---|---|---|---|---|---|---|
| code | `case-code-coupon-tdd` | 쿠폰 정책 TDD 구현 요청 | boundary pair와 Red proof 기대값 보강 | code validator와 hidden behavior check 대상 | case/answer/evaluator/fixture 수정 | 예 | `20260522-112629-code-try01-targeted-implementation-tdd-p4` | passed |

## 리뷰 방식

리뷰 방식: real-subagent

리뷰 결과: Blocker 0, Major 0, 열린 Minor 0

재평가 결과: `case-code-coupon-tdd` targeted eval이 passed이고 RUN_VALIDATION findings가 없다.
