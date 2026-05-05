지정된 fixture는 `Fixture: none`인 리뷰형 프롬프트라 실제 대상 파일은 없습니다. 참고로 저장소의 예시 fixture에서는 [models.py](/Users/hyun/Desktop/dddjango/evals/fixtures/django-shop/shop/orders/models.py:19)의 `Order.cancel()`처럼 validation, 상태 변경, `save()`가 모델 메서드 안에 같이 들어간 형태가 보입니다.

클린 코드 관점의 리팩터링 방향은 “모델을 비우자”가 아니라 “변경 이유가 다른 책임을 경계로 분리하자”입니다.

1. 모델에는 도메인 상태 전이만 남긴다  
   `Order.cancel()`은 “취소 가능한가”, “취소되면 어떤 필드가 바뀌는가” 같은 주문 불변식만 담당하게 합니다. 외부 API 호출, DB 저장 시점, 트랜잭션 orchestration은 모델 밖으로 빼는 편이 좋습니다.

   ```python
   class Order(models.Model):
       def cancel(self, reason: str, actor_email: str, now) -> None:
           if self.status == self.STATUS_SHIPPED:
               raise OrderCannotBeCancelled("shipped orders cannot be cancelled")
           if self.status == self.STATUS_CANCELLED:
               return
           if not reason:
               raise InvalidCancelReason("cancel reason is required")

           self.status = self.STATUS_CANCELLED
           self.cancel_reason = f"{reason} by {actor_email}"
           self.cancelled_at = now
   ```

2. 저장과 트랜잭션은 application service로 이동한다  
   모델 메서드가 `save()`까지 해버리면 호출자는 “검증만 한 건지, 상태만 바꾼 건지, DB까지 쓴 건지” 예측하기 어렵습니다. 서비스 함수가 트랜잭션, 락, 저장 필드, 외부 연동 순서를 명시적으로 제어하게 합니다.

   ```python
   def cancel_order(order_id: int, reason: str, actor_email: str) -> Order:
       with transaction.atomic():
           order = Order.objects.select_for_update().get(id=order_id)
           order.cancel(reason=reason, actor_email=actor_email, now=timezone.now())
           order.save(update_fields=["status", "cancel_reason", "cancelled_at"])

       return order
   ```

3. 외부 API 호출은 gateway/client로 분리한다  
   모델이나 도메인 메서드가 결제사, 배송사, 재고 API 같은 세부 구현을 직접 알면 테스트와 장애 처리가 어려워집니다. `PaymentGateway`, `InventoryClient`, `NotificationClient` 같은 얇은 경계를 두고 서비스에서 호출합니다.

   중요한 점은 외부 API 호출을 DB 트랜잭션 안에 무심코 넣지 않는 것입니다. 보통은:
   - DB 상태 전이를 원자적으로 저장
   - 커밋 이후 외부 API 호출 또는 outbox/event 발행
   - 실패 시 재시도/보상 로직을 별도 처리

   같은 흐름이 더 안전합니다.

4. validation을 성격별로 나눈다  
   도메인 불변식은 모델 또는 도메인 정책에 둡니다. 예: 배송 완료 주문은 취소 불가.  
   입력 형식 검증은 form/schema/serializer/view layer에 둡니다. 예: `reason` 필드가 문자열인지, 길이가 맞는지.  
   외부 상태 검증은 service/gateway에 둡니다. 예: 결제 취소 가능 여부를 PG에서 확인.

5. 테스트는 분리된 책임 단위로 작성한다  
   모델 테스트는 DB 저장보다 상태 전이와 예외를 검증합니다.  
   서비스 테스트는 `save()`, 트랜잭션, 외부 gateway 호출 순서를 검증합니다.  
   API/view 테스트는 request parsing과 response mapping만 확인합니다.

최종 구조는 대략 이렇게 잡는 게 적당합니다.

```text
orders/
  models.py              # Order 상태와 도메인 불변식
  services.py            # use case orchestration, transaction, save
  gateways.py            # 외부 API 경계
  exceptions.py          # 도메인/유스케이스 예외
  views.py               # HTTP 입출력만
```

핵심은 모델 메서드를 없애는 것이 아니라, 모델 메서드가 “주문이 스스로 지켜야 할 규칙”만 표현하게 하고, 외부 I/O와 저장 흐름은 서비스 계층으로 올리는 것입니다.