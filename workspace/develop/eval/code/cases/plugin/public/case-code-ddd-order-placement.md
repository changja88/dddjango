주문 배치/확정 흐름을 DDD 기준에 맞게 리팩터링해줘.

요구사항:
- Ordering bounded context 안에서 사용하는 유비쿼터스 언어가 코드 이름에 드러나야 해.
- `Order`는 aggregate root로서 빈 주문 배치 금지와 결제 대기 상태에서만 확정 가능하다는 불변식을 보호해야 해.
- `Order`의 lifecycle 상태는 외부 코드가 직접 바꾸지 못하게 하고, 상태 변경은 aggregate behavior를 통해서만 일어나게 해.
- `status`/`lifecycle_status` property를 읽기 전용으로 만드는 것만으로는 부족해. backing field가 `_status`, `_state`, `_lifecycle_status`처럼 존재한다면 외부에서 그 필드에 직접 대입해도 관찰되는 lifecycle 상태가 바뀌면 안 돼.
- application service는 유스케이스 흐름을 조정하되 핵심 상태 전이 규칙을 소유하지 않게 해.
- 외부 결제/알림 연동은 실제 호출하지 말고 필요한 event/after-commit 경계만 코드나 테스트로 표현해.
- 과한 repository/UoW/hexagonal 구조는 만들지 마.
- 관련 단위 테스트에는 public lifecycle property와 backing lifecycle field 직접 대입 시도가 상태를 바꾸지 못한다는 검증을 포함하고, `python3 -m unittest discover -s tests` 결과를 보고해줘.
