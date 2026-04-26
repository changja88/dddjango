# 상품 카탈로그 검색/필터/정렬 API 설계

## 엔드포인트

```
GET /api/v1/products/search
```

---

## 쿼리 파라미터

| 파라미터 | 타입 | 필수 | 설명 | 예시 |
|---|---|---|---|---|
| `q` | string | N | 키워드 검색 (상품명, 설명 대상) | `q=무선 이어폰` |
| `category` | string (반복) | N | 카테고리 ID 필터, 다중 선택 가능 | `category=electronics&category=audio` |
| `price_min` | integer | N | 최소 가격 (원 단위) | `price_min=10000` |
| `price_max` | integer | N | 최대 가격 (원 단위) | `price_max=50000` |
| `sort` | enum | N | 정렬 기준 (기본값: `relevance`) | `sort=price_asc` |
| `cursor` | string | N | 다음 페이지 커서 (Base64 인코딩) | `cursor=eyJpZCI6MTAwfQ==` |
| `limit` | integer | N | 페이지당 항목 수 (기본: 20, 최대: 100) | `limit=20` |
| `fields` | string | N | 응답에 포함할 필드 (쉼표 구분) | `fields=id,name,price,thumbnail_url` |

### 정렬 옵션 (`sort`)

| 값 | 설명 |
|---|---|
| `relevance` | 관련도순 (기본값, `q` 파라미터 사용 시) |
| `price_asc` | 가격 낮은 순 |
| `price_desc` | 가격 높은 순 |
| `popularity` | 인기순 (판매량/조회수 기반) |
| `newest` | 최신 등록순 |

### 필드 선택 (`fields`)

선택 가능한 필드 목록:

`id`, `name`, `description`, `price`, `original_price`, `discount_rate`, `currency`, `thumbnail_url`, `images`, `category`, `brand`, `rating`, `review_count`, `sales_count`, `stock_status`, `created_at`, `updated_at`

`fields` 파라미터를 생략하면 기본 필드셋(`id`, `name`, `price`, `original_price`, `discount_rate`, `currency`, `thumbnail_url`, `category`, `brand`, `rating`, `review_count`, `stock_status`)이 반환된다.

---

## 요청 예시

```
GET /api/v1/products/search?q=무선+이어폰&category=electronics&category=audio&price_min=20000&price_max=100000&sort=price_asc&limit=10&fields=id,name,price,thumbnail_url,rating
```

---

## 응답 형식

### 성공 응답 (200 OK)

```json
{
  "data": [
    {
      "id": "prod_a1b2c3d4",
      "name": "프리미엄 무선 블루투스 이어폰",
      "price": 45900,
      "thumbnail_url": "https://cdn.example.com/products/a1b2c3d4/thumb.webp",
      "rating": 4.7
    },
    {
      "id": "prod_e5f6g7h8",
      "name": "스포츠 무선 이어폰 방수",
      "price": 32000,
      "thumbnail_url": "https://cdn.example.com/products/e5f6g7h8/thumb.webp",
      "rating": 4.3
    }
  ],
  "pagination": {
    "next_cursor": "eyJzY29yZSI6MC44NSwidGllYnJlYWtfaWQiOiJwcm9kX2U1ZjZnN2g4In0=",
    "has_next": true,
    "limit": 10
  },
  "meta": {
    "total_count": 243,
    "applied_filters": {
      "q": "무선 이어폰",
      "category": ["electronics", "audio"],
      "price_min": 20000,
      "price_max": 100000
    },
    "sort": "price_asc",
    "fields": ["id", "name", "price", "thumbnail_url", "rating"]
  }
}
```

### 기본 필드셋 응답 예시 (fields 파라미터 생략 시)

```json
{
  "data": [
    {
      "id": "prod_a1b2c3d4",
      "name": "프리미엄 무선 블루투스 이어폰",
      "price": 45900,
      "original_price": 59000,
      "discount_rate": 22,
      "currency": "KRW",
      "thumbnail_url": "https://cdn.example.com/products/a1b2c3d4/thumb.webp",
      "category": {
        "id": "electronics",
        "name": "전자기기",
        "path": ["전자기기", "오디오", "이어폰"]
      },
      "brand": {
        "id": "brand_001",
        "name": "SoundMax"
      },
      "rating": 4.7,
      "review_count": 1289,
      "stock_status": "in_stock"
    }
  ],
  "pagination": {
    "next_cursor": "eyJzY29yZSI6MC44NSwidGllYnJlYWtfaWQiOiJwcm9kX2U1ZjZnN2g4In0=",
    "has_next": true,
    "limit": 20
  },
  "meta": {
    "total_count": 243,
    "applied_filters": {
      "q": "무선 이어폰"
    },
    "sort": "relevance",
    "fields": "default"
  }
}
```

---

## 에러 응답

### 400 Bad Request -- 잘못된 파라미터

```json
{
  "error": {
    "code": "INVALID_PARAMETER",
    "message": "price_min must be a non-negative integer.",
    "details": [
      {
        "field": "price_min",
        "reason": "invalid_type",
        "message": "Expected integer, received string."
      }
    ]
  }
}
```

### 400 Bad Request -- 유효하지 않은 커서

```json
{
  "error": {
    "code": "INVALID_CURSOR",
    "message": "The provided cursor is expired or malformed."
  }
}
```

### 422 Unprocessable Entity -- 논리적 오류

```json
{
  "error": {
    "code": "INVALID_PRICE_RANGE",
    "message": "price_min cannot be greater than price_max.",
    "details": [
      {
        "field": "price_min",
        "value": 100000
      },
      {
        "field": "price_max",
        "value": 50000
      }
    ]
  }
}
```

---

## 커서 기반 페이지네이션 상세

### 커서 구조

커서는 정렬 기준에 따른 마지막 항목의 위치 정보를 Base64 인코딩한 값이다. 내부적으로는 다음과 같은 JSON 구조를 갖는다.

```json
// sort=price_asc 일 때
{
  "sort_value": 45900,
  "tiebreak_id": "prod_a1b2c3d4"
}

// sort=relevance 일 때
{
  "sort_value": 0.85,
  "tiebreak_id": "prod_a1b2c3d4"
}

// sort=newest 일 때
{
  "sort_value": "2026-03-15T09:30:00Z",
  "tiebreak_id": "prod_a1b2c3d4"
}
```

`tiebreak_id`는 동일한 정렬 값을 가진 항목 간 안정 정렬을 보장한다.

### 사용 흐름

```
1. 첫 페이지: GET /api/v1/products/search?q=이어폰&limit=20
2. 다음 페이지: GET /api/v1/products/search?q=이어폰&limit=20&cursor=<next_cursor>
3. has_next=false 이면 마지막 페이지
```

### 주의사항

- 커서 값은 불투명(opaque)하게 취급해야 하며 클라이언트가 직접 생성하거나 수정하면 안 된다.
- 커서는 발급 시점의 정렬/필터 조건과 결합되어 있으므로, 동일한 검색 조건으로만 사용해야 한다.
- 커서 만료 시간은 서버 설정에 따르며 만료된 커서로 요청하면 `INVALID_CURSOR` 에러를 반환한다.

---

## 설계 근거

### 왜 커서 기반 페이지네이션인가

오프셋 기반(`page=3&per_page=20`)은 중간 삽입/삭제 시 항목 누락이나 중복이 발생한다. 커서 기반은 마지막으로 본 항목 이후를 조회하므로 데이터 변동에 안정적이며, `OFFSET N`을 사용하지 않으므로 대규모 데이터셋에서 DB 성능이 일정하게 유지된다.

`total_count`는 별도 COUNT 쿼리로 제공하되, 대규모 데이터에서는 근사값(approximate count)으로 대체할 수 있다. `meta.total_count`가 정확하지 않을 수 있음을 클라이언트에 안내해야 한다.

### 왜 repeated query parameter 방식인가

카테고리 다중 선택에 `category=electronics&category=audio` 방식을 사용한다. `category=electronics,audio`(쉼표 구분)도 가능하지만, repeated parameter 방식이 HTTP 표준에 더 부합하고 URL 인코딩 이슈가 없다.

### 왜 fields 파라미터를 제공하는가

모바일 클라이언트 등 대역폭이 제한된 환경에서 불필요한 필드를 제외하여 응답 크기를 줄인다. 서버 측에서도 불필요한 JOIN이나 계산을 생략할 수 있어 성능상 이점이 있다.

### 키워드 검색 동작

`q` 파라미터는 상품명(`name`)과 설명(`description`) 필드를 대상으로 전문 검색(full-text search)을 수행한다. `sort=relevance`(기본값)일 때 검색 점수(TF-IDF 또는 BM25 기반)로 정렬된다. `q` 파라미터 없이 다른 필터만 사용할 경우 기본 정렬은 `newest`로 폴백한다.
