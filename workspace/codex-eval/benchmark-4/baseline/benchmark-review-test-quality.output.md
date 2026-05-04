작업 디렉터리 `/private/tmp/dddjango-codex-eval`가 비어 있고, 지시된 `config.toml`도 없어 실제 테스트 파일 기준의 라인별 리뷰는 할 수 없었습니다. 대신 Django + pytest 기준에서 “fixture 의존이 과하고 assert가 약한 테스트”를 판단하고 개선할 기준을 정리합니다.

**핵심 리뷰 기준**

1. **DB fixture 남용 줄이기**
   - 대용량 JSON/YAML fixture를 테스트 기본값처럼 로드하지 않는다.
   - 테스트가 필요한 최소 객체만 factory로 만든다.
   - fixture는 “도메인 상태를 설명하는 데이터”가 아니라 “테스트 편의용 dump”가 되기 쉽기 때문에, 실패 원인 추적이 어려워진다.
   - 권장: `factory_boy`, `model_bakery`, 직접 builder fixture 사용.

2. **테스트가 필요한 데이터만 명시적으로 생성**
   ```python
   user = UserFactory(is_active=True)
   order = OrderFactory(user=user, status=Order.Status.PAID)
   ```

   이런 식으로 테스트 조건이 코드에 드러나야 한다.  
   `loaddata users orders products` 후 특정 id를 꺼내 쓰는 패턴은 취약하다.

3. **assert는 결과의 의미를 검증해야 함**
   약한 assert 예:
   ```python
   assert response.status_code == 200
   assert result is not None
   assert len(items) > 0
   ```

   개선 예:
   ```python
   assert response.status_code == 200
   assert response.json() == {
       "id": order.id,
       "status": "paid",
       "total": "12000",
   }
   ```

   또는 DB side effect까지 확인:
   ```python
   order.refresh_from_db()
   assert order.status == Order.Status.CANCELLED
   assert Payment.objects.filter(order=order, refunded=True).exists()
   ```

4. **“실행됐다”가 아니라 “올바르게 동작했다”를 검증**
   특히 view/API 테스트에서 `200`, `302`, `template used`만 확인하면 회귀를 거의 못 잡는다.
   확인해야 할 것:
   - 응답 payload
   - redirect target
   - permission/authorization 결과
   - DB 변경 여부
   - 생성/삭제/상태 전이
   - 외부 호출 mock이 올바른 인자로 호출됐는지

5. **fixture는 역할별로 작게 유지**
   좋은 fixture:
   ```python
   @pytest.fixture
   def paid_order(user):
       return OrderFactory(user=user, status=Order.Status.PAID)
   ```

   나쁜 fixture:
   ```python
   @pytest.fixture
   def full_system_state(db):
       call_command("loaddata", "everything.json")
   ```

6. **테스트 이름이 비즈니스 규칙을 말해야 함**
   약한 이름:
   ```python
   def test_order_cancel():
   ```

   좋은 이름:
   ```python
   def test_paid_order_can_be_cancelled_before_shipping():
   def test_shipped_order_cannot_be_cancelled():
   ```

7. **공유 fixture의 암묵적 상태 제거**
   여러 테스트가 같은 DB fixture의 특정 id, 순서, 기존 값에 의존하면 테스트 간 결합도가 높아진다.
   이런 패턴은 우선 리팩터링 대상:
   ```python
   user = User.objects.get(pk=1)
   product = Product.objects.first()
   ```

8. **권한/실패 케이스를 별도 테스트로 분리**
   정상 케이스만 있고 실패 케이스가 없으면 품질이 낮다.
   최소 기준:
   - anonymous user
   - wrong owner
   - invalid input
   - missing required field
   - boundary value
   - already processed state

9. **mock assert도 구체적으로**
   약한 예:
   ```python
   assert send_mail.called
   ```

   개선:
   ```python
   send_mail.assert_called_once_with(
       to=user.email,
       template="orders/cancelled.html",
       context={"order_id": order.id},
   )
   ```

10. **테스트 데이터 생성 비용 관리**
   DB fixture가 느린 테스트의 원인이면 다음 기준으로 나눈다:
   - pure unit test: DB 없이 함수/서비스 검증
   - model/service test: 최소 DB 객체만 생성
   - integration/API test: 필요한 관계만 factory로 구성
   - full fixture/e2e: 극소수 smoke test에만 허용

**개선 우선순위**

1. `loaddata`, 대형 fixture, `pk=1`, `.first()` 의존 테스트를 찾는다.
2. 각 테스트가 실제로 검증하려는 비즈니스 규칙을 이름으로 바꾼다.
3. JSON/DB fixture를 factory나 builder fixture로 치환한다.
4. `status_code == 200`, `is not None`, `len(...) > 0` 같은 assert를 구체적 결과 검증으로 강화한다.
5. 정상 케이스 옆에 권한/실패/경계 케이스를 추가한다.

실제 파일이 제공되면 다음 단계로는 테스트별로 `fixture 의존도`, `assert 강도`, `회귀 탐지력`, `DB 사용 필요성`을 기준으로 라인 단위 리뷰를 할 수 있습니다.