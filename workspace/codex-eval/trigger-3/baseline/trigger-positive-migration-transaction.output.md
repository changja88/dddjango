Django에서 운영 DB에 결제 상태 컬럼을 안전하게 추가하려면 **expand → backfill → enforce → cleanup** 순서로 나누는 게 가장 안전합니다.

**권장 절차**

1. **먼저 nullable 컬럼만 추가**
   
   운영 테이블이 크다면 `default`와 `NOT NULL`을 한 번에 넣지 않는 게 중요합니다.

   ```python
   # models.py
   class Order(models.Model):
       class PaymentStatus(models.TextChoices):
           PENDING = "pending", "Pending"
           PAID = "paid", "Paid"
           FAILED = "failed", "Failed"
           CANCELED = "canceled", "Canceled"

       payment_status = models.CharField(
           max_length=20,
           choices=PaymentStatus.choices,
           null=True,
           blank=True,
       )
   ```

   migration은 대략 이렇게 생성됩니다.

   ```python
   migrations.AddField(
       model_name="order",
       name="payment_status",
       field=models.CharField(
           max_length=20,
           choices=[
               ("pending", "Pending"),
               ("paid", "Paid"),
               ("failed", "Failed"),
               ("canceled", "Canceled"),
           ],
           null=True,
           blank=True,
       ),
   )
   ```

2. **애플리케이션 코드는 null을 처리하게 배포**

   예를 들어 기존 주문은 아직 `payment_status=None`일 수 있으므로 코드에서 안전하게 처리합니다.

   ```python
   status = order.payment_status or Order.PaymentStatus.PENDING
   ```

3. **데이터 백필을 별도 migration 또는 management command로 수행**

   데이터가 적으면 `RunPython`도 괜찮습니다.

   ```python
   def backfill_payment_status(apps, schema_editor):
       Order = apps.get_model("orders", "Order")
       Order.objects.filter(payment_status__isnull=True).update(
           payment_status="pending"
       )
   ```

   하지만 운영 테이블이 크면 `RunPython`에서 대량 update를 한 번에 치지 말고, management command나 배치 작업으로 나눠서 처리하는 편이 안전합니다.

   ```python
   qs = Order.objects.filter(payment_status__isnull=True).order_by("id")

   while True:
       ids = list(qs.values_list("id", flat=True)[:1000])
       if not ids:
           break

       Order.objects.filter(id__in=ids).update(payment_status="pending")
   ```

4. **백필 완료 확인**

   ```sql
   SELECT COUNT(*)
   FROM orders_order
   WHERE payment_status IS NULL;
   ```

   결과가 `0`인지 확인합니다.

5. **마지막에 NOT NULL과 기본값을 적용**

   백필이 끝난 뒤에 모델을 강화합니다.

   ```python
   payment_status = models.CharField(
       max_length=20,
       choices=PaymentStatus.choices,
       default=PaymentStatus.PENDING,
   )
   ```

   이후 migration에서 `null=False`가 적용되게 합니다.

**피해야 할 방식**

```python
payment_status = models.CharField(
    max_length=20,
    choices=PaymentStatus.choices,
    default=PaymentStatus.PENDING,
)
```

이걸 처음부터 기존 대형 테이블에 추가하면 DB 종류와 버전에 따라 테이블 rewrite, 긴 lock, 배포 지연이 생길 수 있습니다.

**요약**

작은 테이블이면 `default` 포함 단일 migration도 실용적으로 괜찮습니다. 하지만 운영에서 안전하게 하려면:

1. `null=True` 컬럼 추가  
2. 코드가 null을 견디게 배포  
3. 배치로 기존 데이터 백필  
4. null 없는지 검증  
5. `null=False`, `default` 적용  

이 순서가 가장 안정적입니다.