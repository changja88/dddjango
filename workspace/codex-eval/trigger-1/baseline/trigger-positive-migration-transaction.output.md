Django에서 결제 상태처럼 운영 데이터에 영향이 큰 컬럼을 추가할 때는 “한 번에 모델 변경 + 기본값 + 코드 사용”을 배포하지 않는 게 안전합니다. 보통 2~3단계로 나눕니다.

**권장 절차**

1. **nullable 컬럼만 먼저 추가**
   
   ```python
   class Payment(models.Model):
       status = models.CharField(
           max_length=32,
           null=True,
           blank=True,
           choices=PaymentStatus.choices,
       )
   ```

   migration은 DB에 컬럼만 추가하게 만듭니다.

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

   이 단계에서는 `default`를 바로 넣지 않는 게 좋습니다. 큰 테이블에서 DB가 전체 row를 rewrite하거나 lock을 오래 잡을 수 있습니다.

2. **애플리케이션 코드가 새 컬럼을 쓰도록 배포**

   새 결제 생성 시점부터는 `status`를 명시적으로 저장합니다.

   ```python
   Payment.objects.create(
       user=user,
       amount=amount,
       status=PaymentStatus.PENDING,
   )
   ```

   기존 row는 아직 `NULL`일 수 있으므로 읽는 코드도 방어적으로 처리합니다.

   ```python
   status = payment.status or PaymentStatus.PENDING
   ```

3. **기존 데이터 backfill**

   데이터가 많으면 Django data migration 한 번으로 처리하기보다 배치 커맨드나 SQL을 작은 단위로 실행하는 편이 안전합니다.

   예:

   ```python
   Payment.objects.filter(status__isnull=True).update(
       status=PaymentStatus.PENDING
   )
   ```

   대량 테이블이면 `id` 범위 기준으로 나눠서 처리합니다.

4. **검증 후 NOT NULL 제약 추가**

   모든 row가 채워졌는지 확인합니다.

   ```sql
   SELECT COUNT(*) FROM payments_payment WHERE status IS NULL;
   ```

   0이면 모델을 바꿉니다.

   ```python
   status = models.CharField(
       max_length=32,
       null=False,
       blank=False,
       choices=PaymentStatus.choices,
   )
   ```

   그리고 추가 migration을 적용합니다.

**핵심 원칙**

- 큰 테이블에는 `default` 포함 `AddField`를 조심합니다.
- 컬럼 추가, 코드 반영, backfill, 제약 추가를 분리합니다.
- 배포 중 구버전/신버전 코드가 동시에 떠도 깨지지 않게 만듭니다.
- 결제 상태는 enum/choices로 제한하고, 상태 전이는 서비스 계층에서 검증하는 게 좋습니다.
- migration 전후로 `NULL` 개수, 상태별 row 수, 결제 생성/환불/실패 플로우를 확인합니다.

운영 DB가 PostgreSQL이면 특히 `NOT NULL` 추가나 인덱스 생성 방식도 테이블 크기에 따라 별도로 안전하게 나눠야 합니다.