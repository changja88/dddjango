구현을 시도했지만 현재 `/private/tmp/dddjango-codex-eval`은 비어 있고, 세션이 `read-only`라 `discounts.py`와 `tests/test_discount_policy.py` 생성이 차단됐습니다. `apply_patch`도 “writing is blocked by read-only sandbox”로 거부됐고, pytest 실행도 할 수 없습니다.

적용하려던 구성은 다음입니다.

- `discounts.py`
  - `NoDiscountPolicy`
  - `FixedAmountDiscountPolicy`
  - `PercentageDiscountPolicy`
  - `MinimumSubtotalDiscountPolicy`
  - `Decimal` 기반 금액 처리
  - 음수 금액/잘못된 할인율 방어
  - 고정 할인은 주문 금액을 초과하지 않도록 cap 처리

- `tests/test_discount_policy.py`
  - pytest fixture 포함: `subtotal`, `fixed_10_discount`
  - 테스트 이름을 행위 중심으로 작성
  - edge case 포함:
    - 고정 할인이 subtotal보다 큰 경우
    - 최소 주문 금액 경계값
    - 최소 주문 금액 미만
    - 음수 subtotal
    - 음수 할인액
    - 음수/100% 초과 할인율
    - 음수 최소 주문 금액

쓰기 가능한 환경이면 아래 명령으로 검증하면 됩니다.

```bash
pytest
```

현재 제약 때문에 실제 파일 반영과 테스트 실행은 완료하지 못했습니다.