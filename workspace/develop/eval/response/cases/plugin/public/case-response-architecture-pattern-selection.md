결제 승인과 주문 확정이 분리된 Django 주문 컨텍스트가 있어.

- 주문 aggregate와 상태 전이는 이미 정리되어 있다.
- 주문 확정 use case는 결제 gateway, 재고 예약, 알림 발송과 협력한다.
- 결제 승인 메시지는 유실되면 안 되지만, 단일 DB transaction으로 외부 시스템까지 묶을 수는 없다.
- 조회 화면은 주문 목록 필터와 집계가 많지만 아직 command 모델을 왜곡할 정도인지는 불명확하다.

파일 수정 없이 구현 아키텍처 패턴을 추천해줘. layered/clean/hexagonal, ports/adapters, repository/UoW, service layer, CQRS, event sourcing, saga, outbox, ACL 중 무엇을 쓰고 무엇은 쓰지 않을지, 의존성 방향과 외부 side effect 처리 기준까지 함께 정리해줘.
