현재 `/private/tmp/dddjango-codex-eval`에는 코드가 없어서 구체 모델을 보고 나누긴 어렵습니다. Django에서 도메인 모델은 보통 “테이블 단위”가 아니라 **업무 불변식과 변경 이유가 같은 단위**로 나누는 게 좋습니다.

추천 기준은 이렇습니다.

1. **Bounded Context 먼저 나누기**
   예를 들어 커머스라면:
   - `catalog`: 상품, 옵션, 가격표
   - `ordering`: 장바구니, 주문, 주문항목
   - `payment`: 결제, 환불, 승인 이력
   - `fulfillment`: 배송, 출고, 송장
   - `account`: 회원, 주소, 인증 관련 프로필

   `Product`, `Order`, `Payment`가 서로 FK로 연결될 수는 있지만, 같은 앱에 다 넣지는 않습니다. 업무 언어와 변경 주기가 다르면 분리합니다.

2. **Aggregate Root 중심으로 모델 묶기**
   한 트랜잭션에서 함께 일관성을 지켜야 하는 객체를 하나의 aggregate로 봅니다.

   예:
   - `Order`는 aggregate root
   - `OrderLine`은 `Order` 내부 구성요소
   - 주문 총액, 주문 상태 전이, 취소 가능 여부는 `Order` 쪽 도메인 메서드로 둠

   ```python
   class Order(models.Model):
       status = models.CharField(...)
       
       def cancel(self):
           if self.status not in ["pending", "paid"]:
               raise CannotCancelOrder()
           self.status = "cancelled"
   ```

3. **앱은 “공유 모델 창고”가 아니게 하기**
   `common`, `core`, `utils` 같은 앱에 비즈니스 모델을 몰아넣으면 시간이 지나면서 경계가 무너집니다.

   괜찮은 공통:
   - timestamp mixin
   - base model
   - 공통 exception
   - shared value object

   피해야 할 공통:
   - `UserProfile`
   - `Product`
   - `OrderStatus`
   - 도메인 정책 객체

4. **Django model은 persistence + 최소 도메인 행위**
   모델에 모든 유스케이스를 넣기보다는:
   - 엔티티 불변식: model method
   - 여러 aggregate를 조합하는 작업: service/application layer
   - 외부 API, 결제, 메일: infra layer 또는 adapter

   예:
   ```text
   ordering/
     models.py          # Order, OrderLine
     services.py        # place_order, cancel_order
     selectors.py       # read/query helpers
     policies.py        # discount, cancel policy
     exceptions.py
   ```

5. **FK 방향은 의존 방향을 드러내게 하기**
   `ordering.Order`가 `catalog.Product`를 참조하는 건 자연스럽지만, `catalog.Product`가 주문을 알아야 한다면 경계가 이상한 신호일 수 있습니다.

   권장:
   - 주문 항목은 주문 시점의 상품명/가격 스냅샷을 보관
   - `Product` 변경이 과거 주문 금액을 바꾸지 않게 함

6. **상태 전이가 있는 모델은 독립 도메인으로 보기**
   다음이 있으면 별도 도메인 후보입니다.
   - 상태 머신이 있다
   - 권한/정책이 복잡하다
   - 이벤트가 발생한다
   - 별도 관리자/운영 화면이 필요하다
   - 변경 주기가 다른 팀/기능과 다르다

실무적으로는 처음부터 너무 잘게 나누기보다, `account`, `catalog`, `ordering`, `payment`처럼 큰 업무 경계로 시작하고, 각 앱 안에서 aggregate 단위로 모델과 서비스를 정리하는 편이 좋습니다.

현재 프로젝트가 비어 있어서 구체 도메인을 모르면 일반론까지만 가능합니다. 실제 엔티티 목록이나 만들려는 서비스 설명을 주면, Django 앱 구조와 모델 경계까지 더 구체적으로 쪼개드릴 수 있습니다.