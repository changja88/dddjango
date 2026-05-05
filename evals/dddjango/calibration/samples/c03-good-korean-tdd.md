# 쿠폰 정책 TDD

실패 테스트부터 작성합니다. 정상 할인, 경계 금액, 만료 쿠폰 실패, 중복 사용
실패를 pytest로 먼저 고정합니다.

## 실패 테스트

```python
def test_coupon_cannot_be_used_twice():
    result = apply_coupon(...)
    assert result.is_failure
```

## 최소 구현

값 객체와 도메인 예외, `ApplyCouponResult`를 사용해 위 테스트만 통과시키는
최소 구현을 둡니다.

## 리팩터링

그린 상태에서 repository, Django model, external gateway 경계를 분리합니다.
실제 테스트는 실행하지 않았습니다. 실행할 명령은 `pytest`입니다.
