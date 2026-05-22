장바구니 할인 정책을 TDD로 설계하려고 해.

상황:
- 주문 금액이 50,000원 이상이면 무료 배송을 적용한다.
- 쿠폰은 만료일 당일까지 사용할 수 있고, 이미 사용한 쿠폰은 다시 쓸 수 없다.
- 결제 승인이 성공하면 알림 gateway를 호출해야 하지만, 실제 외부 호출은 테스트에서 일어나면 안 된다.
- PO가 BDD 시나리오 초안을 줄 수 있지만, pytest-bdd step definition이나 fixture 구현까지는 지금 필요 없다.

파일 수정 없이 답변만 해줘. 테스트 목록에서 시작해서 첫 실패 테스트, Red-Green-Refactor 진행, Inside-Out/Outside-In 선택, acceptance test와 unit test의 순서, 상태 검증과 행위 검증을 어디에 쓸지 정리해줘.

