지정 fixture path `/Users/hyun/Desktop/dddjango/none`는 존재하지 않았고, 평가 workspace `/private/tmp/dddjango-codex-eval`도 비어 있어 실제 파일/라인 단위 리뷰와 pytest 실행은 불가능했습니다. 따라서 “통과했다”고 말할 수 없고, 아래는 read-only fallback 기준의 리뷰 findings와 적용 가능한 예시 diff입니다.

**Review Findings**

[Excessive Fixture] -- DB fixture에 테스트 의미가 숨으면 Arrange가 불투명해집니다. 테스트가 “왜 이 데이터여야 하는지”를 읽을 수 없고, fixture 변경 하나가 여러 테스트를 동시에 깨뜨립니다. JSON fixture/autouse fixture는 통합 테스트 일부에만 두고, 도메인 규칙은 builder/factory로 테스트 안에 필요한 값만 만드세요.

[Weak Assertion] -- `assert response.status_code == 200`, `assert obj is not None`, `assert len(qs) > 0` 수준은 회귀 보호가 약합니다. mutation testing 관점에서 `<`/`<=`, 필드 누락, 잘못된 상태 전이를 못 잡습니다. 반환 값, DB 상태, 외부 호출 인자를 정확히 검증해야 합니다.

[Slow Test Boundary] -- 순수 도메인 규칙에 `@pytest.mark.django_db`와 DB fixture를 붙이면 피드백이 느려집니다. 도메인 unit test는 Django ORM 없이 실행하고, integration test만 DB/transaction/query count를 검증하세요.

[Fixture Scope] -- session/module scope DB fixture나 autouse fixture는 테스트 간 공유 상태를 만들기 쉽습니다. 기본은 function scope, 비싼 외부 자원만 명시적 상위 scope로 제한합니다.

**개선 기준**

도메인 unit test: `tests/isolated/unit/...`, `django_db` 없음, 실제 도메인 객체와 InMemoryFake 사용, 출력 기반 assert 우선.

Django integration test: `tests/isolated/integration/...`, `pytest.mark.django_db`, factory_boy로 필요한 행만 생성, `assertNumQueries` 또는 `django_assert_num_queries`로 N+1 회귀 방지.

외부 HTTP/메일/결제: MagicMock 남발 대신 `responses` 또는 spec 있는 fake gateway 사용. Mock을 쓴다면 `assert_called_once_with(expected_args)`까지 검증합니다.

**예시 Diff**

```diff
diff --git a/tests/isolated/unit/test_order_policy.py b/tests/isolated/unit/test_order_policy.py
new file mode 100644
--- /dev/null
+++ b/tests/isolated/unit/test_order_policy.py
@@
+import pytest
+
+from orders.domain import Order, OrderLine, OrderPolicy
+
+
+@pytest.mark.parametrize(
+    ("quantity", "expected_total"),
+    [(1, 10_000), (2, 20_000)],
+)
+def test_order_policy_total_amount_calculates_from_lines(quantity, expected_total):
+    # Arrange
+    order = Order(lines=[OrderLine(product_id=1, unit_price=10_000, quantity=quantity)])
+
+    # Act
+    total = OrderPolicy().total_amount(order)
+
+    # Assert
+    assert total == expected_total
diff --git a/tests/isolated/integration/test_order_checkout.py b/tests/isolated/integration/test_order_checkout.py
new file mode 100644
--- /dev/null
+++ b/tests/isolated/integration/test_order_checkout.py
@@
+import pytest
+
+
+@pytest.mark.django_db
+def test_checkout_marks_order_paid_and_records_payment(order_factory, payment_gateway):
+    # Arrange
+    order = order_factory(status="pending", total_amount=20_000)
+    payment_gateway.approve.return_value = "payment-123"
+
+    # Act
+    result = order.checkout(payment_gateway=payment_gateway)
+
+    # Assert
+    order.refresh_from_db()
+    assert result.payment_id == "payment-123"
+    assert order.status == "paid"
+    payment_gateway.approve.assert_called_once_with(order_id=order.id, amount=20_000)
```

**RED / GREEN / REFACTOR**

RED: 위 테스트는 현재 `orders.domain`, `OrderPolicy`, `order_factory`, `payment_gateway`가 없거나 기존 구현이 DB fixture에 묶여 있으면 실패해야 합니다.

GREEN 최소 구현: `OrderLine`, `Order`, `OrderPolicy.total_amount()`를 순수 Python 객체로 분리하고, checkout 통합 경로는 factory로 생성한 한 건의 주문만 사용하게 만듭니다.

REFACTOR: 큰 DB fixture를 제거하고 `order_factory`, `payment_gateway` fake, 필요한 경우 `InMemoryOrderRepository`로 나눕니다. 5줄 이상 반복 setup은 factory/builder로 올리되, 테스트 의도를 가리지 않게 이름을 구체화합니다.

검증 명령:

```bash
pytest tests/isolated/unit -q
pytest tests/isolated/integration -q
pytest --randomly-seed=random tests/isolated -q
```

---
> **관련 스킬 참조:**
> - 테스트 리팩터링과 pytest fixture 개선 → **implementation-test** 스킬