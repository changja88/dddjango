# URL/리소스 설계 규칙 레퍼런스

명명 규칙, 계층적 하위 리소스, 필터링/정렬/검색 패턴을 정리한다.

---

## 명명 규칙

| 규칙 | 좋음 | 나쁨 |
|------|------|------|
| 명사 사용 (동사 아님) | `/orders` | `/create-order` |
| 복수 명사 (컬렉션) | `/customers/5` | `/customer/5` |
| 케밥 케이스, 소문자 | `/order-items` | `/orderItems`, `/order_items` |
| 후행 슬래시 없음 | `/orders` | `/orders/` |
| DB 구조 비반영 | `/products` | `/tbl_products` |

---

## 계층적 하위 리소스

부모-자식 관계에 슬래시를 사용한다. **3단계 이상 깊이는 피한다.**

```
GET /customers/5/orders          # 고객 5의 주문 목록
GET /customers/5/orders/10       # 고객 5의 주문 10
GET /customers/5/orders/10/items # 3단계 — 허용하되 더 깊이는 피함
```

---

## 필터링, 정렬, 검색 패턴

```
GET /orders?status=shipped&minCost=100      # 필터링
GET /orders?sort=-price,name                 # 정렬 (- = DESC)
GET /orders?fields=id,name,total             # 필드 선택 (sparse fieldset)
GET /orders?limit=25&offset=50               # 페이지네이션
GET /items?price=gte:10&price=lte:100        # 범위 필터
GET /products?q=keyboard                     # 검색
```
