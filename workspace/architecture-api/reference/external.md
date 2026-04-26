# API 설계 원칙 — 외부 자료

---

## 1. URL/리소스 설계 규칙

### 1.1 핵심 원칙

- **명사, 동사 아님**: URI는 자원(thing)을 나타낸다. `/orders`이지 `/create-order`가 아니다. 행위는 HTTP 메서드로 표현
- **컬렉션은 복수 명사**: `/customers`는 컬렉션, `/customers/5`는 특정 항목
- **계층적 하위 리소스**: 부모-자식 관계에 슬래시 사용. `/customers/5/orders`. 3단계 이상 깊이는 피한다
- **케밥 케이스, 소문자**: `/bone-counts`이지 `/boneCount`이나 `/bone_counts`가 아니다
- **후행 슬래시 없음**: `/orders`가 맞고 `/orders/`는 틀리다
- **DB 구조를 반영하지 않는다**: API는 비즈니스 엔티티의 추상화이지 내부 테이블의 반영이 아니다

### 1.2 필터링, 정렬, 검색 패턴

```
GET /orders?minCost=100&status=shipped          # 필터링
GET /orders?sort=-price,name                     # 정렬 (- = DESC)
GET /orders?fields=id,name                       # 필드 선택
GET /orders?limit=25&offset=50                   # 페이지네이션
GET /items?price=gte:10&price=lte:100            # 범위 필터
```

### 1.3 HTTP 메서드와 리소스 매트릭스

| 리소스 | POST | GET | PUT | DELETE |
|--------|------|-----|-----|--------|
| /customers | 새로 생성 | 전체 조회 | 일괄 수정 | 전체 삭제 |
| /customers/1 | 에러 | 단건 조회 | 단건 수정 | 단건 삭제 |
| /customers/1/orders | 고객 1의 주문 생성 | 고객 1의 주문 조회 | 일괄 수정 | 전체 삭제 |

> 출처: [Microsoft REST API Design](https://learn.microsoft.com/en-us/azure/architecture/best-practices/api-design), [restfulapi.net](https://restfulapi.net/resource-naming/), [Google API Design Guide](https://cloud.google.com/apis/design/resource_names)

---

## 2. API 버전 관리

### 2.1 세 가지 전략

| 전략 | 예시 | 장점 | 단점 |
|------|------|------|------|
| **URL Path** | `GET /api/v1/products` | 즉시 보임, 라우팅 쉬움 | REST 원칙 위반 (하나의 URI = 하나의 자원) |
| **Header** | `Accept-Version: v1` | 깨끗한 URL, REST 원칙 부합 | 브라우저에서 안 보임, 디버깅 어려움 |
| **Query Parameter** | `GET /api/users?version=1` | 중간 지점, 가시적 | 캐싱 복잡, 필터 파라미터와 혼동 |

### 2.2 Stripe의 날짜 기반 버전 관리 (업계 표준)

- URL path에 메이저 버전 (`/v1/charges`), 실제 버전은 헤더로 관리
- `Stripe-Version: 2024-10-01` — 날짜 기반 버전
- 신규 계정은 자동으로 최신 버전에 고정
- 요청별 오버라이드 가능: `curl -H "Stripe-Version: 2024-10-01"`

### 2.3 실전 원칙

- 하나의 전략을 선택하고 일관되게 적용
- 일반 패턴: URL path로 메이저 버전, 헤더로 마이너 조정
- 버전 관리 방식을 문서화하고 마이그레이션 경로를 제공

> 출처: [Stripe Blog - API Versioning](https://stripe.com/blog/api-versioning), [Stripe API - Versioning](https://docs.stripe.com/api/versioning)

---

## 3. 페이지네이션

### 3.1 세 가지 접근법

| 방식 | 요청 | 성능 | 데이터 일관성 | 랜덤 접근 |
|------|------|------|-------------|----------|
| **Offset** | `?limit=25&offset=50` | 대규모에서 저하 (스킵 비용) | 낮음 (삽입/삭제 시 누락/중복) | 가능 |
| **Cursor** | `?limit=25&starting_after=obj_abc` | 일정 O(1) | 높음 (고정 위치 참조) | 불가 |
| **Keyset** | `?limit=25&after_id=123` | 일정 (인덱스 활용) | 높음 (불변 정렬키) | 불가 |

**성능 차이**: PostgreSQL 100만 건에서 cursor 기반이 offset 기반보다 **17배 빠름**.

### 3.2 Stripe의 구현

```json
{
  "data": [...],
  "has_more": true,
  "url": "/v1/customers",
  "object": "list"
}
// 다음 페이지: GET /v1/customers?starting_after=cus_abc123
```

### 3.3 실전 원칙

- 인덱싱된, 불변, 유니크한 필드(타임스탬프 + ID 조합)를 커서로 사용
- 커서를 불투명하게 인코딩(base64)하여 클라이언트가 토큰으로 취급하도록
- 페이지당 100-200개 결과 권장

> 출처: [Stripe API - Pagination](https://docs.stripe.com/api/pagination), [Slack API - Pagination](https://api.slack.com/docs/pagination)

---

## 4. Rate Limiting

### 4.1 Rate Limit 헤더 (GitHub 표준)

```
HTTP/2 200 OK
X-RateLimit-Limit: 60          # 윈도우 내 최대 요청 수
X-RateLimit-Remaining: 56      # 남은 요청 수
X-RateLimit-Reset: 1372700873  # 윈도우 리셋 시각 (UTC epoch)
```

### 4.2 429 Too Many Requests

```
HTTP/2 429 Too Many Requests
Retry-After: 30                 # 재시도 대기 시간 (초)
X-RateLimit-Remaining: 0
```

### 4.3 알고리즘 비교

| 알고리즘 | 동작 | 버스트 처리 | 적합 |
|---------|------|-----------|------|
| **Fixed Window** | 이산 시간 블록 내 카운트 | 경계 버스트 문제 (2배) | 단순, 저오버헤드 |
| **Sliding Window** | 연속 이동 시간 프레임 | 부드러움, 경계 문제 없음 | 정확, 약간 더 많은 메모리 |
| **Token Bucket** | 고정 속도로 토큰 추가, 요청당 소비 | 제어된 버스트 허용 | 퍼블릭 API 기본 |
| **Leaky Bucket** | 고정 속도로 배출, 초과 거부 | 버스트 없음, 일정 출력 | 트래픽 셰이핑 |

### 4.4 실전 원칙

- 비용이 큰 작업(인증, DB 쿼리) **전에** rate limit 검사
- 복제본 간 카운터 공유를 위해 외부 저장소(Redis) 사용
- 429 응답에 항상 `Retry-After` 헤더 포함

> 출처: [GitHub Docs - Rate Limits](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api), [IETF Draft - RateLimit Headers](https://datatracker.ietf.org/doc/draft-ietf-httpapi-ratelimit-headers/)

---

## 5. 에러 응답 형식 (RFC 9457)

### 5.1 Problem Details for HTTP APIs

**Content-Type**: `application/problem+json`

| 필드 | 타입 | 설명 |
|------|------|------|
| `type` | URI | 문제 유형 식별. 생략 시 `about:blank` |
| `title` | string | 문제 유형의 짧은 요약 (동일 유형이면 동일 제목) |
| `status` | integer | HTTP 상태 코드 (100-599) |
| `detail` | string | 이 **특정 발생**에 대한 설명 |
| `instance` | URI | 이 특정 발생 식별 |

### 5.2 예시

```json
HTTP/1.1 403 Forbidden
Content-Type: application/problem+json

{
  "type": "https://example.com/probs/out-of-credit",
  "title": "You do not have enough credit.",
  "status": 403,
  "detail": "Your current balance is 30, but that costs 50.",
  "instance": "/account/12345/msgs/abc",
  "balance": 30,
  "accounts": ["/account/12345", "/account/67890"]
}
```

`balance`와 `accounts`는 **확장 필드**. 문제 유형 정의에서 추가 필드를 정의할 수 있다.

### 5.3 핵심 규칙

- `type`은 문서화 역할을 하는 안정적 URI
- `title`은 **유형**(재사용 가능), `detail`은 **특정 발생**
- 클라이언트는 인식하지 못하는 확장 필드를 무시해야 한다

> 출처: [IETF RFC 9457](https://www.rfc-editor.org/rfc/rfc9457.html), [Swagger Blog - Problem Details](https://swagger.io/blog/problem-details-rfc9457-doing-api-errors-well/)

---

## 6. 멱등성 (Idempotency)

### 6.1 HTTP 메서드의 안전성과 멱등성

| 메서드 | 안전 | 멱등 | 설명 |
|--------|:----:|:----:|------|
| GET | O | O | 읽기 전용, 부수효과 없음 |
| HEAD | O | O | GET과 동일하지만 본문 없음 |
| OPTIONS | O | O | 통신 옵션 설명 |
| PUT | X | O | 전체 교체 — 반복해도 같은 결과 |
| DELETE | X | O | 삭제 — 반복해도 같은 효과 |
| POST | X | X | 매번 새 리소스 생성 가능 |
| PATCH | X | X | 부분 수정, 반복 시 결과 달라질 수 있음 |

### 6.2 POST의 멱등성 문제

네트워크 장애로 서버는 처리했지만 클라이언트가 응답을 받지 못한 경우, POST를 재시도하면 중복 생성 위험.

### 6.3 Idempotency-Key 패턴 (Stripe)

```
POST /v1/charges
Idempotency-Key: KG5LxSFa3M4fcVng
Content-Type: application/json

{"amount": 2000, "currency": "usd"}
```

**동작 방식**:
1. 클라이언트가 고유 키 생성 (V4 UUID 권장)
2. 서버가 첫 요청의 상태 코드 + 응답 본문을 저장
3. 동일 키의 후속 요청은 저장된 결과를 반환 (500 에러도 포함)
4. 키는 24시간 후 만료 (Stripe 정책)
5. POST에만 적용 — GET, DELETE는 이미 멱등

> 출처: [Stripe API - Idempotent Requests](https://docs.stripe.com/api/idempotent_requests), [Stripe Blog - Idempotency](https://stripe.com/blog/idempotency), [IETF Draft - Idempotency-Key](https://datatracker.ietf.org/doc/draft-ietf-httpapi-idempotency-key-header/)

---

## 7. HATEOAS

### 7.1 개념

HATEOAS(Hypermedia as the Engine of Application State)는 REST 제약 조건으로, 서버가 모든 응답에 탐색 링크를 제공한다. 클라이언트는 URL을 하드코딩하지 않고 동적으로 발견한다.

### 7.2 HAL 형식

```json
{
  "_links": {
    "self": { "href": "/orders/123" },
    "next": { "href": "/orders?page=2" },
    "customer": { "href": "/customers/456" }
  },
  "_embedded": {
    "items": [
      {
        "_links": { "self": { "href": "/products/789" } },
        "name": "Widget",
        "price": 9.99
      }
    ]
  },
  "orderNumber": 123,
  "status": "processing"
}
```

Content-Type: `application/hal+json`

### 7.3 실용적 가치 vs 복잡성

| 가치 | 복잡성 |
|------|--------|
| 클라이언트를 서버 URL 구조에서 분리 | 응답 페이로드 증가 |
| 서버가 엔드포인트를 자유롭게 진화 | 형식 표준 난립 (HAL, Siren, JSON-LD, JSON:API) |
| 자기 문서화 API 탐색 | 클라이언트가 링크를 동적으로 따라가도록 구축 필요 |

### 7.4 업계 현실

Twitter, Facebook API 모두 HATEOAS를 구현하지 않는다. 대부분의 "RESTful" API는 Richardson Maturity Model Level 2(HTTP 동사 + 리소스)에서 멈추고, Level 3(하이퍼미디어)에 도달하지 않는다.

### 7.5 언제 사용하는가

- 소비자가 많은 대규모 퍼블릭 API (긴 수명주기)
- URL 분리가 진정한 가치를 제공할 때
- 단순 CRUD API나 내부 마이크로서비스에는 **오버헤드가 크다**

> 출처: [Wikipedia - HATEOAS](https://en.wikipedia.org/wiki/HATEOAS), [restfulapi.net - HATEOAS](https://restfulapi.net/hateoas/), [Ben Morris - Pragmatic REST](https://www.ben-morris.com/pragmatic-rest-apis-without-hypermedia-and-hateoas/)
