예약 요청/확정/만료 흐름을 DDD 기준에 맞게 리팩터링해줘.

요구사항:
- Reservation bounded context 안에서 사용하는 유비쿼터스 언어가 코드 이름과 테스트에 드러나야 해.
- `Reservation`은 aggregate root로서 숙박일 수가 1박 이상이어야 한다는 규칙, 요청된 예약만 확정 가능하다는 규칙, 확정된 예약은 만료 처리할 수 없다는 규칙을 보호해야 해.
- application service는 유스케이스 흐름과 저장/조회, room availability hold 경계 호출만 조정하고 핵심 상태 전이 규칙을 소유하지 않게 해.
- room availability나 inventory는 같은 aggregate 안의 자식 객체처럼 섞지 말고 외부 경계로 표현해. 실제 외부 호출은 하지 말고 in-memory boundary나 event/after-commit 경계만 코드나 테스트로 표현해.
- 과한 repository/UoW/hexagonal 구조는 만들지 마.
- 관련 단위 테스트를 추가하고 `python3 -m unittest discover -s tests` 결과를 보고해줘.
