구독 서비스에서 무료 체험, 유료 전환, 해지 예약, 사용권 부여 흐름을 DDD 관점으로 먼저 모델링해줘.

요구사항:
- 먼저 문제 공간과 솔루션 공간을 나누고, 핵심/지원/일반 하위 도메인을 구분해줘.
- Subscription, Entitlement, Billing 같은 용어가 같은 의미로 섞이지 않도록 bounded context와 유비쿼터스 언어를 정리해줘.
- aggregate 후보와 entity/value object 후보를 나누고, 어떤 불변식을 어느 consistency boundary 안에서 지켜야 하는지 설명해줘.
- 결제 성공, 해지 예약, 사용권 만료 같은 변화는 domain event나 domain service가 필요한지 판단해줘.
- 구현 코드, Django model, DB migration, REST API 계약, subagent 역할 분해는 작성하지 말고 architecture-ddd 설계 결정과 다음 handoff 범위만 답해줘.
