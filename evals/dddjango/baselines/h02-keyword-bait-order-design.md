# H02 Baseline: Keyword bait order design

좋은 답변은 주어진 단어를 단순 나열하지 않고 API, 도메인, DB, 테스트 판단을
서로 연결해야 한다. Router/Schema/response mapping은 Django Ninja 코드 구조와
이어져야 하고, 애그리거트/불변식/유스케이스는 라우터 밖의 도메인 경계로
설명되어야 한다.

transaction, idempotency, concurrency 판단은 실제 중복 요청과 동시 주문 위험을
다뤄야 하며, pytest/TDD는 RED, GREEN, REFACTOR 흐름과 검증 케이스로 이어져야 한다.
