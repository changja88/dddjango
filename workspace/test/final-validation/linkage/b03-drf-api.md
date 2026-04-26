# B03: Cross-Skill Boundary Test -- DRF API 설계 요청

- **입력**: "DRF로 REST API를 만들 건데, URL 네이밍 컨벤션이랑 버저닝 전략 좀 알려줘."
- **활성 스킬**: `architecture-api`
- **모드**: 설계 모드
- **검증 포인트**: 프레임워크 종속 구현이 아닌 설계 원칙으로 응답하는지, 구현은 `implementation-django-ninja`로 위임하는지

---

## 스킬 응답

URL 네이밍 컨벤션과 버저닝 전략은 프레임워크에 종속되지 않는 REST API 설계 원칙이다. DRF든 Django Ninja든 어떤 프레임워크를 쓰든 동일하게 적용된다.

### URL 네이밍 컨벤션

| 규칙 | 좋음 | 나쁨 |
|------|------|------|
| 명사 사용 (동사 금지) | `/orders` | `/create-order`, `/get-users` |
| 복수 명사 (컬렉션) | `/customers/5` | `/customer/5` |
| kebab-case 소문자 | `/order-items` | `/orderItems`, `/order_items` |
| 후행 슬래시 없음 | `/orders` | `/orders/` |
| DB 구조 비반영 | `/products` | `/tbl_products` |

**계층적 하위 리소스**는 슬래시로 부모-자식 관계를 표현하되, 3단계 이상 깊이는 피한다.

```
GET /customers/5/orders          # 고객 5의 주문 목록
GET /customers/5/orders/10       # 고객 5의 주문 10
GET /customers/5/orders/10/items # 3단계 -- 허용하되 더 이상은 피함
```

**필터링/정렬/검색**은 URL 경로가 아닌 쿼리 파라미터로 처리한다.

```
GET /orders?status=shipped&min_cost=100   # 필터링
GET /orders?sort=-price,name              # 정렬 (- = DESC)
GET /products?q=keyboard                  # 검색
```

### 버저닝 전략

세 가지 전략이 있으며, 하나를 선택해서 일관되게 적용해야 한다.

| 전략 | 예시 | 장점 | 단점 |
|------|------|------|------|
| **URL Path** | `/api/v1/products` | 즉시 보임, 라우팅 쉬움 | REST 원칙 위반, URL 오염 |
| **Header** | `Accept-Version: v1` | 깨끗한 URL, REST 부합 | 브라우저에서 안 보임, 디버깅 어려움 |
| **Query Param** | `?version=1` | 중간 지점, 가시적 | 캐싱 복잡, 필터와 혼동 |

**실전 권장 패턴**: URL path로 메이저 버전, 헤더로 마이너 조정. Stripe의 날짜 기반 모델이 모범 사례다.

```
URL path:  /v1/charges                     # 메이저 버전
Header:    Stripe-Version: 2024-10-01      # 세부 버전 (날짜 기반)
```

### Breaking vs Non-Breaking Change 구분

버전을 올려야 하는지 판단하는 기준이다.

| 변경 유형 | Breaking? |
|----------|:---------:|
| 응답에 필드 추가 | X |
| 선택적 요청 파라미터 추가 | X |
| 필드 제거/이름 변경/타입 변경 | **O** |
| 필수 파라미터 추가 | **O** |
| URL 경로 변경 | **O** |

핵심 원칙: **추가는 자유, 제거는 금지**(Additive changes only). Breaking change가 필요하면 새 버전을 도입하고, 필드 마이그레이션은 Expand-and-Contract 3단계(신규 필드 추가 -> Deprecation 표시 -> 기존 필드 제거)로 진행한다.

---

> **관련 스킬 참조:**
> - Django Ninja로 이 설계를 실제 코드로 구현 -> **implementation-django-ninja** 스킬
> - 데이터베이스 스키마 설계 (리소스에 대응하는 테이블) -> **architecture-db** 스킬

---

## 경계 검증 분석

### 스킬이 올바르게 처리한 부분

1. **프레임워크 비종속 원칙으로 응답**: 사용자가 "DRF로"라고 요청했지만, URL 네이밍과 버저닝은 프레임워크에 종속되지 않는 설계 원칙이다. 스킬의 첫 문장("이 스킬은 특정 프레임워크에 종속되지 않는 REST API 설계 원칙을 다룬다")에 따라 DRF 고유 기능(ViewSet, Router, DefaultRouter 등)이 아닌 보편적 REST 설계 규칙으로 답변했다.

2. **구현 위임**: 스킬 설명에 명시된 대로("Django Ninja API 구현에 대해서는 implementation-django-ninja에 위임한다") 관련 스킬 참조에서 `implementation-django-ninja`를 안내했다. DRF가 아닌 Django Ninja를 구현 스킬로 연결한 것은 스킬 체계의 설계 의도를 따른 것이다.

3. **참조 로딩 규칙 준수**: 설계 모드의 규칙("API를 제안하기 전에 관련 참조를 먼저 읽는다")에 따라 `references/url-design.md`와 `references/versioning.md`를 읽은 후 응답을 구성했다.

### 경계 위반이 발생하지 않은 이유

- `architecture-api` 스킬은 설계 원칙만 다루고, 프레임워크별 구현은 범위 밖이다.
- DRF의 `DefaultRouter`, `SimpleRouter`, `@api_view` 같은 프레임워크 고유 개념은 이 스킬의 관할이 아니다.
- 사용자가 물어본 "URL 네이밍 컨벤션"과 "버저닝 전략"은 모두 이 스킬이 커버하는 설계 영역에 해당한다.
- 실제 코드 구현이 필요한 시점에 `implementation-django-ninja`로 자연스럽게 연결된다.
