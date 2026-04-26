---
name: architecture-implementation-patterns
description: >
  Use this skill when the user asks to "apply hexagonal architecture", "set up
  ports and adapters", "implement CQRS", "add event sourcing", "design a clean
  architecture", "apply onion architecture", "structure the project layers",
  "separate read and write models", "implement repository pattern", "add unit
  of work", "apply data mapper", "integrate with legacy systems", "add
  anti-corruption layer", "implement outbox pattern", "apply dependency
  injection", "apply DIP", "replace legacy system", or equivalent Korean
  phrases like "헥사고날 적용", "프로젝트 구조 잡아줘", "레이어 분리", "의존성
  역전 적용", "레거시 교체/마이그레이션", "CQRS 적용", "이벤트 소싱 도입". Use
  this skill whenever architecture pattern selection, dependency direction, or
  infrastructure abstraction is being discussed — even for seemingly simple
  tasks like deciding where a repository interface belongs or how to isolate
  external dependencies. Covers architecture styles (hexagonal, clean, onion,
  layered), CQRS, event sourcing (with outbox, snapshot, projection),
  persistence patterns (unit of work, data mapper, repository), and integration
  patterns (ACL, integration events, bubble context). This skill handles
  framework-agnostic pattern selection and design; for Django-specific
  implementation (ORM, service layer, signals), see implementation-django.
  For domain modeling (aggregates, entities, bounded contexts), see
  architecture-ddd. For database schema design, see architecture-db.
  For REST API design principles, see architecture-api.
---

# 아키텍처 구현 패턴

이 스킬은 코드 의존성 구조화, 인프라 추상화, 바운디드 컨텍스트 통합을 위한
아키텍처 패턴을 다룬다. 도메인 모델링과 전략적/전술적 DDD 패턴에 대해서는
architecture-ddd에 위임한다. 데이터베이스 스키마 설계(정규화, 인덱스)에 대해서는
architecture-db에 위임한다. REST API 설계 원칙(엔드포인트, 버저닝)에 대해서는
architecture-api에 위임한다. Python 컨벤션(타입 힌트, 데이터클래스)에 대해서는
implementation-python에 위임한다. Django 코어(모델, ORM, 설정)에 대해서는
implementation-django에 위임한다. Django Ninja API(Schema, Router)에 대해서는
implementation-django-ninja에 위임한다. 클린 코드 원칙(SOLID, 네이밍)에
대해서는 implementation-cleancode에 위임한다.

**기본 요구사항 — 모든 모드에 적용:**
- 의존성은 항상 안쪽을 향한다: 도메인은 인프라에 의존해서는 안 된다.
- 추상화(인터페이스)는 구현하는 계층이 아니라 사용하는 계층이 소유한다
  (소유권 역전).
- 현재 복잡도를 처리할 수 있는 가장 단순한 패턴을 선택한다. 단순한 CRUD에는
  레이어드 아키텍처로 충분하다; 모든 곳에 헥사고날을 강제하지 않는다.

아래 섹션에서 다루는 주제를 작업할 때는 링크된 참조 파일을 읽고 상세한
컨벤션과 코드 예시를 확인한다.

**참조 로딩 규칙:**
- 설계 모드: 아키텍처를 제안하기 전에 관련 참조를 먼저 읽는다.
- 리뷰 모드: 결과를 확정하기 전에 인용된 모든 패턴의 참조를 읽는다.
- 리팩터링 모드: 변경 사항을 제시하기 전에 적용된 각 패턴의 참조를 읽는다.

## 응답 구조

모든 응답은 다음 구조를 따른다:

1. **[주요 내용]** -- 모드에 따른 코드, 리뷰, 리팩터링 결과
2. **[관련 스킬 참조]** -- 사용자의 다음 단계를 안내하는 연결점

이 스킬은 11개의 상호 연결된 스킬 체계의 일부이다.
사용자는 현재 작업 후 어떤 스킬을 호출해야 하는지 모르는 경우가
많으므로, 관련 스킬 참조가 워크플로우의 자연스러운 연결을 만든다.

ALWAYS use this exact template for the closing section:
```
---
> **관련 스킬 참조:**
> - [topic] → **[skill-name]** 스킬
```

## 운영 모드

사용자의 요청에 따라 모드를 선택한다:
- **설계**: 애플리케이션 아키텍처 설계, 패턴 선택, 계층 정의
- **리뷰**: 기존 아키텍처의 패턴 위반 사항 평가
- **리팩터링**: 기존 구조를 아키텍처 패턴에 맞게 개선

의도가 모호한 경우 설계 모드를 기본으로 한다.

### 설계 모드

애플리케이션 아키텍처를 설계할 때 다음 순서를 따른다:

1. **복잡도를 먼저 평가한다.** 단순 CRUD -> 레이어드로 충분하다. 여러 통합이 있는
   복잡한 도메인 -> 헥사고날 또는 클린. 과도한 엔지니어링을 하지 않는다.

2. **의존성 방향을 정의한다.** 모든 소스 코드 의존성은 안쪽을 향한다. 도메인이
   인터페이스(포트)를 정의하고, 인프라가 이를 구현한다(어댑터).

3. **패턴을 선택적으로 적용한다.** CQRS와 이벤트 소싱은 최상위 아키텍처가 아니다
   — 이점이 있는 바운디드 컨텍스트에만 적용한다.

4. **통합 경계를 계획한다.** 외부 시스템은 ACL을 통해 통신한다. 내부 도메인
   이벤트는 내부에 유지하고, 통합 이벤트가 BC 경계를 넘는다.

### 리뷰 모드

잘 구성된 아키텍처를 리뷰할 때는 개선 사항을 나열하기 전에 강점을 먼저
인정한다. 각 발견 사항은 다음 형식으로 작성한다:

```
[패턴] -- 이 구조가 해당 패턴의 원칙을 위반하는 이유 설명
```

리뷰를 확정하기 전에 이 체크리스트의 모든 항목을 검증한다:

- [ ] 의존성이 안쪽을 향하는가 (도메인이 인프라를 import하지 않는가)
- [ ] 인터페이스를 구현하는 계층이 아닌 사용하는 계층이 소유하는가 (소유권 역전)
- [ ] 외부 시스템이 포트/어댑터 또는 ACL 뒤에 격리되어 있는가
- [ ] CQRS가 시스템 전체가 아닌 바운디드 컨텍스트별로 선택적으로 적용되었는가
- [ ] 도메인 이벤트가 통합 이벤트로 직접 노출되지 않는가
- [ ] 리포지토리 추상화가 테이블 단위가 아닌 애그리거트 단위인가
- [ ] Unit of Work가 트랜잭션 경계를 명시적으로 관리하는가
- [ ] 커맨드 메서드가 쿼리 데이터를 반환하지 않는가 (CQS 원칙)
- [ ] 계층 간 순환 의존성이 없는가
- [ ] 통합 이벤트가 내부 도메인 개념을 누출하지 않는가
- [ ] 어댑터 구현에 비즈니스 로직이 포함되어 있지 않은가
- [ ] 포트 인터페이스가 기술적 연산이 아닌 도메인 의도를 표현하는가
- [ ] 패턴의 복잡도가 문제의 복잡도에 부합하는가 (과도한 엔지니어링 없음)

### 리팩터링 모드

변경 전/후를 보여주고 각 변경의 이유를 명시한다. 각 변경을 특정 패턴 원칙에
연결한다. 각 변경은 다음 형식으로 작성한다:

```
[Before]
<원래 구조/코드>

[After]
<개선된 구조/코드>

[Reason] 패턴 -- 이 변경이 해당 패턴에 부합하는 이유 설명
```

변경 사항을 제시하기 전에 아래의 적용 가능한 모든 개선을 적용한다:

- [ ] 도메인의 인프라 의존성 -> 포트 인터페이스 + 어댑터로 추출
- [ ] 직접 외부 시스템 호출 -> ACL로 래핑 (Facade + Adapter + Translator)
- [ ] 모놀리식 읽기/쓰기 모델 -> CQRS로 분리 (복잡도가 정당화하는 경우)
- [ ] 외부에 노출된 도메인 이벤트 -> 통합 이벤트로 변환
- [ ] 도메인의 DB 로직 -> 리포지토리/데이터 매퍼로 이동
- [ ] 분산된 트랜잭션 관리 -> Unit of Work로 통합
- [ ] 도메인 개념의 원시 타입 -> 값 객체로 추출
- [ ] 데이터를 반환하는 커맨드 메서드 -> 커맨드 + 쿼리로 분리
- [ ] 과도하게 엔지니어링된 단순 도메인 -> 적절한 패턴 수준으로 단순화
- [ ] 의도적으로 적용하지 않은 패턴과 그 이유를 명시

---

## 1. 아키텍처 스타일

헥사고날(포트 & 어댑터), 클린 아키텍처, 어니언 아키텍처, 전통적인 레이어드
아키텍처를 비교한다. 모두 동일한 핵심 목표 — 도메인을 향한 의존성을 갖는
관심사 분리 — 를 공유하지만 내부 계층 구조화 방식이 다르다. DIP(의존성 역전
원칙)는 세 가지 현대 패턴 모두의 이론적 기반이다.

가장 적합한 단순한 스타일을 선택한다: 단순 CRUD에는 레이어드, 다중 통합
시스템에는 헥사고날, 내부 계층 구조화 가이드로는 어니언/클린을 참조한다.

> Reference: `references/hexagonal.md`

## 2. CQRS

CQRS(Command Query Responsibility Segregation)는 읽기 모델과 쓰기 모델을
분리한다. Meyer의 CQS(메서드 수준)에서 Young의 CQRS(모델 수준)로 발전했다.
최상위 아키텍처가 아니다 — 비대칭적 읽기/쓰기 최적화가 필요한 바운디드
컨텍스트에 선택적으로 적용한다.

세 가지 구현 수준: 동일 DB에 다른 모델, 별도 DB에 최종 일관성, 이벤트 기반
프로젝션.

> Reference: `references/cqrs.md`

## 3. 이벤트 소싱

현재 상태 대신 불변 이벤트의 시퀀스로 상태 변경을 저장한다. 관련 패턴 포함:
Outbox(신뢰할 수 있는 이벤트 발행), Snapshot(리플레이 성능), Projection(읽기
모델 구성), Event Upcasting(스키마 진화).

선택적으로 적용한다 — 모든 바운디드 컨텍스트에 이벤트 소싱이 필요한 것은
아니다. Greg Young은 이벤트 소싱 모놀리스가 가장 큰 안티패턴이라고 경고한다.

> Reference: `references/event-sourcing.md`

## 4. 영속성 패턴

Data Mapper, Unit of Work, Repository, Identity Map — 도메인 모델에서
영속성을 추상화하기 위한 구체적 접근법. Active Record 대 Data Mapper의
트레이드오프와 프레임워크별 고려사항(SQLAlchemy classical mapping 대
Django ORM)을 다룬다.

Django 특화 영속성 패턴에 대해서는 implementation-django도 참조한다.

> Reference: `references/persistence.md`

## 5. 통합 패턴

부패 방지 계층(ACL), 통합 이벤트, Bubble Context — 바운디드 컨텍스트를
연결하고 외부 또는 레거시 시스템과 통합하기 위한 패턴. ACL은 가장 방어적인
컨텍스트 매핑 패턴이다. 통합 이벤트는 내부 도메인 이벤트와 구별되어야 한다.

전략적 컨텍스트 매핑 패턴(파트너십, 고객-공급자, 순응자)에 대해서는
architecture-ddd를 참조한다.

> Reference: `references/integration.md`
