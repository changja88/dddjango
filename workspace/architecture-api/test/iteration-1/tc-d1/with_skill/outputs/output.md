# 상품 카탈로그 검색/필터/정렬 API 설계

## 리소스 식별

| 리소스 | URI | 설명 |
|--------|-----|------|
| 상품 컬렉션 | `/products` | 상품 목록 (검색/필터/정렬 포함) |
| 상품 단건 | `/products/{product_id}` | 개별 상품 상세 |
| 카테고리 컬렉션 | `/categories` | 필터 UI에 사용할 카테고리 목록 |

---

## 엔드포인트

### `GET /v1/products`

상품 목록을 검색, 필터, 정렬, 페이지네이션하여 반환한다.

---

## 쿼리 파라미터

### 검색

| 파라미터 | 타입 | 설명 | 예시 |
|----------|------|------|------|
| `q` | string | 키워드 검색 (상품명, 설명 대상 전문 검색) | `?q=무선+키보드` |

### 필터

| 파라미터 | 타입 | 설명 | 예시 |
|----------|------|------|------|
| `category` | string (반복 가능) | 카테고리 필터. 다중 선택 시 파라미터를 반복하여 OR 조건으로 동작 | `?category=electronics&category=accessories` |
| `price` | string (범위 연산자) | 가격 범위 필터. `gte:`, `lte:` 접두사로 min/max 지정 | `?price=gte:10000&price=lte:50000` |

### 정렬

| 파라미터 | 타입 | 설명 | 예시 |
|----------|------|------|------|
| `sort` | string | 정렬 기준. `-` 접두사는 내림차순. 쉼표로 다중 정렬 | `?sort=-price` |

**허용되는 정렬 필드:**

| 값 | 설명 | 기본 방향 |
|----|------|-----------|
| `price` / `-price` | 가격 오름차순 / 내림차순 | - |
| `popularity` / `-popularity` | 인기순 오름차순 / 내림차순 | - |
| `created_at` / `-created_at` | 등록일 오름차순 / 내림차순 | - |
| (생략 시) | `q` 존재 시 관련도순, 없으면 `-created_at` | 기본값 |

### 페이지네이션 (커서 기반)

| 파라미터 | 타입 | 설명 | 예시 |
|----------|------|------|------|
| `limit` | integer | 페이지당 결과 수 (기본 25, 최대 100) | `?limit=25` |
| `starting_after` | string | 이 커서 이후의 결과를 반환. 불투명한 base64 인코딩 토큰 | `?starting_after=eyJpZCI6MTIzfQ` |
| `starting_before` | string | 이 커서 이전의 결과를 반환 (역방향 탐색용) | `?starting_before=eyJpZCI6NDU2fQ` |

커서는 서버가 생성하는 불투명 토큰이다. 내부적으로 정렬 기준 필드 값과 ID 조합을 base64 인코딩한다. 클라이언트는 커서를 파싱하거나 직접 구성하지 않고, 응답의 `cursors` 객체에서 받은 값을 그대로 전달한다.

### 필드 선택 (Sparse Fieldset)

| 파라미터 | 타입 | 설명 | 예시 |
|----------|------|------|------|
| `fields` | string (쉼표 구분) | 응답에 포함할 필드 목록. 생략 시 전체 필드 반환 | `?fields=id,name,price,thumbnail_url` |

**선택 가능 필드:** `id`, `name`, `description`, `price`, `original_price`, `currency`, `category`, `brand`, `thumbnail_url`, `images`, `rating`, `review_count`, `in_stock`, `created_at`

---

## 요청 예시

```
GET /v1/products?q=무선+키보드&category=electronics&category=accessories&price=gte:10000&price=lte:50000&sort=-popularity&limit=25&starting_after=eyJpZCI6MTIzfQ&fields=id,name,price,thumbnail_url,rating
```

---

## 응답 형식

### 성공 응답 (`200 OK`)

```json
{
  "data": [
    {
      "id": "prod_a1b2c3",
      "name": "로지텍 무선 키보드 K380",
      "price": 39900,
      "thumbnail_url": "https://cdn.example.com/products/prod_a1b2c3/thumb.webp",
      "rating": 4.5
    },
    {
      "id": "prod_d4e5f6",
      "name": "앱코 무선 기계식 키보드",
      "price": 45000,
      "thumbnail_url": "https://cdn.example.com/products/prod_d4e5f6/thumb.webp",
      "rating": 4.2
    }
  ],
  "pagination": {
    "has_more": true,
    "cursors": {
      "after": "eyJwb3B1bGFyaXR5Ijo5NTAsImlkIjoicHJvZF9kNGU1ZjYifQ",
      "before": "eyJwb3B1bGFyaXR5Ijo5ODAsImlkIjoicHJvZF9hMWIyYzMifQ"
    }
  },
  "meta": {
    "total_count": 142,
    "applied_filters": {
      "q": "무선 키보드",
      "category": ["electronics", "accessories"],
      "price_min": 10000,
      "price_max": 50000
    },
    "sort": "-popularity"
  }
}
```

### 전체 필드 응답 (fields 생략 시) -- 단건 데이터 구조

```json
{
  "id": "prod_a1b2c3",
  "name": "로지텍 무선 키보드 K380",
  "description": "블루투스 멀티 디바이스 무선 키보드. 최대 3대 기기 동시 연결.",
  "price": 39900,
  "original_price": 49900,
  "currency": "KRW",
  "category": {
    "id": "cat_electronics",
    "name": "전자기기"
  },
  "brand": "Logitech",
  "thumbnail_url": "https://cdn.example.com/products/prod_a1b2c3/thumb.webp",
  "images": [
    "https://cdn.example.com/products/prod_a1b2c3/1.webp",
    "https://cdn.example.com/products/prod_a1b2c3/2.webp"
  ],
  "rating": 4.5,
  "review_count": 1247,
  "in_stock": true,
  "created_at": "2025-11-15T09:30:00Z"
}
```

---

## 에러 응답 (RFC 9457 Problem Details)

### 잘못된 정렬 필드 (`400 Bad Request`)

```json
{
  "type": "https://api.example.com/problems/invalid-sort-field",
  "title": "Invalid sort field.",
  "status": 400,
  "detail": "Sort field 'color' is not allowed. Allowed fields: price, popularity, created_at.",
  "instance": "/v1/products?sort=color"
}
```

### 잘못된 가격 범위 (`400 Bad Request`)

```json
{
  "type": "https://api.example.com/problems/invalid-price-range",
  "title": "Invalid price range.",
  "status": 400,
  "detail": "price min (50000) must be less than or equal to price max (10000).",
  "instance": "/v1/products?price=gte:50000&price=lte:10000"
}
```

### 유효하지 않은 커서 (`400 Bad Request`)

```json
{
  "type": "https://api.example.com/problems/invalid-cursor",
  "title": "Invalid pagination cursor.",
  "status": 400,
  "detail": "The provided cursor is malformed or expired. Please restart from the first page.",
  "instance": "/v1/products?starting_after=invalid_token"
}
```

### Rate Limit 초과 (`429 Too Many Requests`)

```json
{
  "type": "https://api.example.com/problems/rate-limit-exceeded",
  "title": "Rate limit exceeded.",
  "status": 429,
  "detail": "You have exceeded 100 requests per minute. Retry after 23 seconds.",
  "instance": "/v1/products"
}
```

응답 헤더에 `Retry-After: 23` 포함.

---

## 설계 근거

| 결정 | 근거 |
|------|------|
| 복수 명사 `/products` | URL 명명 규칙: 컬렉션은 복수 명사 |
| 동사 없이 `GET` 메서드만 사용 | REST 원칙: 행위는 HTTP 메서드로 표현, URL에 동사를 넣지 않음 |
| `?q=` 검색 파라미터 | URL 설계 규칙: 검색은 쿼리 파라미터 `q`로 표현 |
| `?price=gte:10000` 범위 필터 | URL 설계 규칙: `gte:`, `lte:` 접두사로 범위 표현 |
| `?category=a&category=b` 반복 파라미터 | 다중 선택 필터는 동일 파라미터 반복으로 OR 조건 표현 |
| `?sort=-price` 정렬 | URL 설계 규칙: `-` 접두사로 내림차순 표현 |
| 커서 기반 페이지네이션 | 대용량 상품 데이터에서 offset 대비 17배 빠른 성능. 실시간 삽입/삭제 시 데이터 일관성 보장 |
| 불투명 base64 커서 | 페이지네이션 원칙: 클라이언트가 커서를 토큰으로 취급하도록 인코딩 |
| `?fields=` sparse fieldset | 목록 조회 시 불필요한 필드를 제외하여 응답 크기 절감. 모바일 환경 최적화 |
| RFC 9457 에러 형식 | 모든 에러 응답에 일관된 Problem Details 형식 적용 |
| URL 경로에 `/v1/` 포함 | 버전 관리: 향후 breaking change 시 `/v2/`로 분리 가능 |
