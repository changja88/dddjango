현재 디렉터리에는 `config.toml`이 없어서 로컬 지침은 확인할 수 없었습니다.

Django에서 결제 상태 컬럼을 안전하게 추가할 때는 한 번에 `NOT NULL + default`로 추가하지 말고, 보통 **expand → backfill → contract** 순서로 나눕니다.

**권장 절차**

1. **nullable 컬럼만 먼저 추가**
   ```python
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

   migration은 `AddField`만 포함되게 합니다. 대용량 테이블에서는 DB default를 동시에 넣으면 락이나 테이블 rewrite 위험이 있습니다.

2. **애플리케이션 코드에서 신규 row는 항상 값 쓰기**
   예를 들어 결제 생성 시 `payment_status="pending"`을 명시합니다. 이 배포 이후 새 데이터는 null이 생기지 않게 만듭니다.

3. **기존 데이터 backfill**
   작은 테이블이면 `RunPython`도 가능하지만, 큰 테이블이면 migration 안에서 한 번에 업데이트하지 말고 management command나 배치 작업으로 나눠 처리하는 게 안전합니다.

   예:
   ```python
   Order.objects.filter(payment_status__isnull=True).update(
       payment_status="pending"
   )
   ```

   대용량이면 `id` 범위나 chunk 단위로 처리합니다.

4. **검증**
   ```sql
   SELECT COUNT(*) FROM app_order WHERE payment_status IS NULL;
   ```

   0인지 확인합니다.

5. **마지막 migration에서 `null=False` 적용**
   ```python
   payment_status = models.CharField(
       max_length=20,
       choices=PaymentStatus.choices,
       default=PaymentStatus.PENDING,
       null=False,
   )
   ```

   이 단계는 기존 null이 모두 제거된 뒤에만 진행합니다.

**주의할 점**

- migration 안에서 현재 모델 클래스를 직접 import하지 말고 `apps.get_model()`을 쓰세요.
- 대용량 테이블에서는 `atomic = False`를 고려하세요.
- `payment_status`로 자주 필터링한다면 index를 추가하되, PostgreSQL에서는 가능하면 concurrent index를 별도 migration으로 추가하세요.
- DB 제약까지 강하게 걸고 싶다면 `CheckConstraint`를 추가하되, PostgreSQL 대용량 테이블에서는 `NOT VALID` 후 validate하는 방식도 고려할 수 있습니다.
- MySQL 대용량 테이블이면 online DDL 가능 여부를 확인하고, 필요하면 `gh-ost`나 `pt-online-schema-change` 같은 도구를 쓰는 게 안전합니다.

핵심은 **컬럼 추가, 데이터 채우기, 제약 강화**를 각각 분리해서 배포하는 것입니다.