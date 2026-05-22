작은 사내 admin 기능에서 `announcement_category` 테이블 하나를 추가하려고 해.

상황:
- 컬럼은 `id`, `name`, `sort_order`, `is_active` 정도야.
- 데이터는 운영자가 가끔 직접 관리하고, 동시 쓰기나 외부 요청 retry는 없어.
- 기존 대형 테이블 backfill이나 hot-table index 변경도 없어.
- 전체 ERD나 트랜잭션/락 설계 문서까지는 필요 없어.

이 정도 작업에서 확인할 DB migration 영향과 최소한의 제약조건만 짧게 알려줘.
