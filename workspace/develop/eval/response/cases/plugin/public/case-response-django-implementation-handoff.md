주문 확정 기능을 구현하기 전에 dddjango 관점의 역할 경계와 handoff만 정리해줘.

이번 PR에는 다음 일이 함께 들어갈 수 있어.

- `OrderService.confirm()`의 `transaction.atomic()` 범위, 중복 확정 방지, `transaction.on_commit()` 알림 발송
- 운영 중인 주문 상태 컬럼의 migration/backfill 계획
- Django Ninja `POST /orders/{id}/confirm` Router/Schema, status code, Problem Details, OpenAPI 영향
- 서버 렌더링 주문 상세 페이지의 상태 badge, template/static 연결, 권한 확인
- `OrderStatus`와 금액 표시 타입을 Python `StrEnum`/dataclass 또는 더 단순한 타입으로 정리할지
- 테스트는 먼저 어떤 실패 테스트를 둘지, pytest fixture/factory/concurrency test는 어디까지 둘지
- fat service나 template business logic이 생기지 않게 clean-code review에서 무엇을 볼지

실제 파일 수정, 테스트 실행, subagent 실행은 하지 말고 답변만 해줘. API 계약과 Ninja adapter, DB/transaction 정책과 Django 구현, Web/template 책임, TDD 절차와 pytest mechanics, production code와 test/review 책임을 서로 섞지 않게 정리해줘.
