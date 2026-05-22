기존 DRF `OrderViewSet`을 당장 Django Ninja로 옮기지는 않고 유지보수해야 해.

현재 문제는 serializer가 `fields = "__all__"`이고, viewset action 안에서 주문 상태 전이와 알림 발송까지 직접 처리한다는 점이야.

실제 코드는 작성하지 말고 유지보수 방향과 위험만 정리해줘. 신규 API 표준을 논의하기보다 기존 DRF 코드를 adapter로 유지하면서 어디로 책임을 옮길지 판단하고 싶어.
