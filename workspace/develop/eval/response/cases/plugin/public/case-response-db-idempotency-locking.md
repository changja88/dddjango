결제 승인 처리에서 같은 외부 결제 이벤트가 retry되거나 동시에 들어올 수 있어.

상황:
- `payment_id`는 외부 PG가 주는 값이고 한 결제 승인에 대해 하나만 있어야 해.
- 같은 `Idempotency-Key`와 같은 요청 fingerprint는 같은 처리 결과를 재사용해야 해.
- 같은 `Idempotency-Key`지만 요청 fingerprint가 다르면 충돌로 남겨야 해.
- 결제 승인 후 주문 상태를 `PAID`로 바꾸고, 알림 발송은 DB commit 이후에 하고 싶어.
- API 응답 형식이나 Django 코드 구현보다 DB가 중복 처리와 race를 어떻게 막을지가 궁금해.

DB transaction boundary, isolation/locking 선택, unique constraint, idempotency 저장소 위치와 key scope, request fingerprint, replay reference, retention/cleanup, 실패 시 retry 기준을 중심으로 설계해줘.
