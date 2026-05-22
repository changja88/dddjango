Fixture repo에서 주문 관리용 Django 구현을 개선해줘.

요구사항:
- `Order` 조회에 재사용 가능한 custom `QuerySet`/`Manager`를 추가하고, 최근 활성 주문 목록을 반환하는 selector를 만들어줘.
- 목록 조회는 N+1이 생기지 않도록 `select_related()` 또는 `prefetch_related()`가 필요한지 판단하고, query-count regression test를 추가해.
- 주문 확정 use case는 service 함수로 두고, 상태 변경은 model method에 모아줘.
- 확정 처리는 `transaction.atomic()` 안에서 저장하고, 알림 발송처럼 외부 부작용으로 볼 수 있는 작업은 `transaction.on_commit()` 경계로 분리해. 실제 외부 호출은 하지 마.
- cache를 추가한다면 invalidation owner와 key를 코드나 주석으로 명확히 남겨줘. 필요 없다고 판단하면 이유를 남겨줘.
- REST API 계약이나 Django Ninja Router 변경은 이번 범위가 아니야.

가능하면 `python3 manage.py check`와 `python3 manage.py test`를 실행하고 결과를 보고해줘.
