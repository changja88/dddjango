현재 `/private/tmp/dddjango-codex-eval`에는 리뷰할 Django 모델 파일이 없어서, 특정 클래스/라인 기준의 결론은 낼 수 없습니다. 코드 없이 판단하면 “fat model 여부”는 아래 기준으로 봐야 합니다.

**리뷰 결론**
모델이 다음 책임까지 갖고 있다면 클린 아키텍처 관점에서는 fat model입니다.

**높음**
- [Dependency Rule] -- 모델 메서드 안에서 이메일, 외부 API, 결제 SDK, Celery enqueue, 파일 저장, HTTP 호출을 직접 한다면 도메인이 인프라에 의존하는 구조입니다. 이런 부수효과는 application service 또는 adapter로 빼고, 트랜잭션 이후 실행은 `transaction.on_commit()` 또는 outbox로 처리하는 편이 맞습니다.
- [Use Case 분리] -- 모델이 “주문 생성 전체 흐름”, “예약 확정 + 알림 + 결제 + 재고 차감”처럼 여러 객체 조회/저장과 트랜잭션 흐름을 조율한다면 모델 책임을 넘었습니다. 이건 application service가 담당하고, 모델은 `confirm()`, `cancel()`, `pay()` 같은 상태 전이와 불변식 보호만 담당해야 합니다.
- [Repository 경계] -- 모델 메서드 안에서 다른 aggregate를 직접 조회하거나 여러 모델을 동시에 저장한다면 aggregate 경계가 흐려집니다. 클린/헥사고날 구조에서는 조회/저장은 repository 또는 selector/service 계층으로 이동시키는 게 좋습니다.

**중간**
- [Aggregate] -- 모델 하나가 너무 많은 연관 객체를 품고, 하나의 트랜잭션에서 여러 엔티티를 함께 수정한다면 큰 aggregate일 가능성이 큽니다. “반드시 동시에 지켜야 하는 불변식”만 모델 내부에 남기고 나머지는 ID 참조, 도메인 이벤트, 별도 aggregate로 분리하세요.
- [Domain Model] -- 상태값을 아무 데서나 직접 바꾸거나 `status = "confirmed"` 같은 문자열 할당이 퍼져 있다면 도메인 규칙이 캡슐화되지 않은 상태입니다. `TextChoices`와 `confirm()/cancel()` 같은 의도 드러나는 메서드로 상태 전이를 막아야 합니다.
- [Validation] -- 중요한 규칙이 `clean()`에만 있거나 DB 제약만 있다면 한쪽 방어가 비어 있습니다. 예를 들어 중복 예약, 음수 금액, 날짜 역전 같은 규칙은 Python 레벨 검증과 `CheckConstraint`/`UniqueConstraint`를 함께 두는 게 안전합니다.

**낮음**
- [Django Convention] -- `__str__`, `Meta.ordering`, 필요한 `indexes`, 명확한 `TextChoices`가 없으면 유지보수성과 조회 성능 쪽에서 개선 여지가 있습니다.
- [Model Size] -- 단순히 모델 파일이 길다는 이유만으로 fat model은 아닙니다. 순수 도메인 규칙이 많아서 길어진 모델은 괜찮습니다. 문제는 ORM 조회, 트랜잭션 조율, 외부 I/O, 표현 계층 로직이 섞였을 때입니다.

정리하면, Django의 “Fat Model, Thin View”는 “모든 로직을 모델에 넣으라”가 아니라 “비즈니스 규칙은 뷰에 두지 말라”에 가깝습니다. 클린 아키텍처 기준으로는 모델에는 도메인 상태와 불변식, 상태 전이만 남기고, 유스케이스 조율은 service/application layer, 영속성 추상화는 repository/selector, 외부 연동은 adapter로 분리하는 선이 적절합니다. 단순 CRUD라면 과한 repository/hexagonal 구조까지 강제할 필요는 없습니다.

---
> **관련 스킬 참조:**
> - Django 모델/서비스 분리 → **implementation-django** 스킬
> - Aggregate, 불변식, 도메인 이벤트 → **architecture-ddd** 스킬
> - Clean Architecture 경계/Repository/Adapter → **architecture-implementation-patterns** 스킬