주문 배치/확정 흐름을 DDD 기준에 맞게 리팩터링해줘.

요구사항:
- Ordering bounded context 안에서 사용하는 유비쿼터스 언어가 코드 이름에 드러나야 해.
- `Order`는 aggregate root로서 빈 주문 배치 금지와 결제 대기 상태에서만 확정 가능하다는 불변식을 보호해야 해.
- application service는 유스케이스 흐름을 조정하되 핵심 상태 전이 규칙을 소유하지 않게 해.
- 외부 결제/알림 연동은 실제 호출하지 말고 필요한 event/after-commit 경계만 코드나 테스트로 표현해.
- 과한 repository/UoW/hexagonal 구조는 만들지 마.
- 관련 단위 테스트를 추가하고 `python3 -m unittest discover -s tests` 결과를 보고해줘.
