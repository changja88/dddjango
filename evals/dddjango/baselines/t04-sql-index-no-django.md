# T04 Baseline: SQL-only 인덱스 질문에서 Django 오염 방지

필수 기대 기준:

- 사용자가 Django 코드가 필요 없다고 했으므로 Django Ninja, Router, Schema를 제안하지 않는다.
- PostgreSQL 쿼리 패턴, 선택도, 복합 인덱스, 부분 인덱스 또는 covering index를 검토한다.
- `EXPLAIN`/`EXPLAIN ANALYZE`로 검증하는 방법을 제시한다.
- 쓰기 비용과 인덱스 과다 생성 위험을 함께 설명한다.
