Django 주문 앱에서 주문 목록 조회가 느리고, 주문 확정 처리 뒤 알림 발송과 캐시 무효화 시점도 헷갈려.

실제 파일 수정은 하지 말고 Django 구현 계획만 답해줘.

확인하고 싶은 내용:
- `Order` model, custom `QuerySet`/`Manager`, selector 중 어디에 조회 조건과 eager loading을 둘지
- 주문 확정 use case를 model method와 service 중 어디에 둘지
- `transaction.atomic()`과 `transaction.on_commit()`을 어떻게 둘지
- `select_related()`/`prefetch_related()`, query-count 검증, cache invalidation을 어떻게 볼지
- settings/security에서 secrets, secure cookie, CSRF 같은 항목은 어떤 확인만 남기면 되는지

REST API 설계나 Django Ninja Router 코드는 이번 범위가 아니야.
