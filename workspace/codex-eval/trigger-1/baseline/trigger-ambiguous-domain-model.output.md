**주요 내용**

현재 `/private/tmp/dddjango-codex-eval`에는 실제 프로젝트 파일이 없어서, 구체 모델이 아니라 DDD 기준의 분리 원칙으로 답할게요.

도메인 모델은 “테이블 후보”가 아니라 **비즈니스 언어와 불변식의 경계**로 나누는 게 좋습니다. 순서는 이렇게 잡으면 됩니다.

1. **하위 도메인부터 나누기**
   - 핵심 도메인: 제품의 경쟁력을 만드는 부분. 직접 정교하게 모델링.
   - 지원 도메인: 운영 보조, CRUD 성격. 단순 Django 모델/서비스로 충분.
   - 범용 도메인: 인증, 권한, 결제 PG 연동 등. 외부 솔루션이나 얇은 래퍼 선호.

2. **바운디드 컨텍스트 정하기**
   같은 단어가 문맥마다 다르게 쓰이면 분리 신호입니다.

   예:
   | 용어 | 컨텍스트 A | 컨텍스트 B | 분리 여부 |
   |---|---|---|---|
   | 주문 | 고객이 결제하려는 장바구니 결과 | 물류가 출고해야 할 작업 단위 | 분리 가능 |
   | 상품 | 판매 가능한 카탈로그 항목 | 창고의 재고 관리 대상 | 분리 가능 |
   | 사용자 | 로그인 주체 | 구매자/판매자/담당자 역할 | 역할 모델 분리 고려 |

3. **애그리거트는 작게 잡기**
   한 트랜잭션에서 반드시 함께 지켜야 하는 불변식만 하나의 애그리거트에 넣습니다.

   예를 들어 커머스라면 대략:

   - `catalog`
     - `Product` aggregate root
     - 값 객체: `Money`, `ProductName`, `CategoryPath`
   - `orders`
     - `Order` aggregate root
     - 내부 값 객체/엔티티: `OrderLine`, `ShippingAddress`
     - 이벤트: `OrderPlacedEvent`, `OrderCancelledEvent`
   - `payments`
     - `Payment` aggregate root
     - 이벤트: `PaymentApprovedEvent`, `PaymentFailedEvent`
   - `inventory`
     - `StockItem` aggregate root
     - 이벤트: `StockReservedEvent`, `StockReleasedEvent`
   - `accounts`
     - `User`, `Customer`, `Seller` 등 인증/프로필 경계 분리

4. **Django 앱은 바운디드 컨텍스트 단위로**
   `products`, `orders`, `payments`, `inventory`, `accounts`처럼 나누되, “모델 하나당 앱 하나”는 피하는 게 좋습니다. 앱의 목적을 한 문장으로 설명할 수 있어야 합니다.

5. **컨텍스트 간 참조는 객체가 아니라 ID로**
   `Order` 안에 `Product` 객체 전체를 들고 있지 말고 `product_id`, 주문 시점의 `product_name`, `unit_price` 같은 스냅샷 값을 둡니다. 결제 성공 후 주문 상태 변경, 재고 차감 같은 흐름은 도메인 이벤트나 응용 서비스에서 조율합니다.

권장 구조는 이런 식입니다.

```text
apps/
  orders/
    domain/
      models.py
      events.py
      repositories.py
    application/
      services.py
    models.py
    api/
      schemas.py
      routers.py

  payments/
  inventory/
  catalog/
  accounts/
```

핵심 기준은 이겁니다: **같이 변경되는 규칙은 같이 두고, 다른 언어/다른 생명주기/다른 트랜잭션 경계를 가지면 나눕니다.**

---
> **관련 스킬 참조:**
> - 바운디드 컨텍스트, 애그리거트 설계 → **architecture-ddd** 스킬
> - Django 앱/모델 구조화 → **implementation-django** 스킬