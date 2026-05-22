수정 대상: case
원인 분류: case

# coupon expiration boundary public case 분석

## 범위

- bucket: `code`
- case: `case-code-coupon-tdd`
- run id: `20260522-111959-code-try01-targeted-implementation-tdd-p4`

## 현상

targeted eval에서 with-ddjango는 used coupon Red/Green과 최소 주문 금액 경계, 만료일 당일 허용 테스트를 추가했지만 만료일 다음 날 거절 테스트를 추가하지 않아 oracle verdict가 partial이 됐다.

현재 public case는 "만료일 당일"만 명시하고, answer oracle은 source reference의 boundary pair 기준에 따라 "만료일 당일 accepted / 다음 날 rejected"를 요구한다. runtime reference는 boundary example을 확장하라고 하지만, code-backed eval에서 반복 가능한 pass run을 만들기에는 public prompt가 덜 직접적이다.

## 판단

원인은 case under-specification이다. P4 기준의 boundary cases를 안정적으로 검증하려면 public prompt 자체가 만료일 당일과 다음 날을 함께 테스트하라고 요구해야 한다.

## 리뷰 방식

리뷰 방식: real-subagent

리뷰 결과: Blocker 0, Major 0, 열린 Minor 0

재평가 결과: `20260522-112629-code-try01-targeted-implementation-tdd-p4`가 passed이고 with-ddjango answer-oracle verdict가 pass다.
