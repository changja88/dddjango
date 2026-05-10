Order와 주문 service의 책임이 섞여 있는지 보고, 필요한 최소 코드 개선을 해줘.

요구사항:
- 주문 상태 전이 불변식은 흩어지지 않게 해.
- 외부 부작용처럼 보이는 알림 발송은 transaction commit 이후로 미룰 수 있는 경계를 만들어줘.
- 큰 아키텍처 전환이나 repository/UoW 도입은 꼭 필요할 때만 해.
- 기존 테스트를 보존하고 필요한 regression test를 추가해.
