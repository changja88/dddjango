# BDD (pytest-bdd) 레퍼런스

pytest-bdd를 사용한 BDD 테스트 구현의 상세 규칙과 예시.
BDD는 TDD의 진화형이다. TDD가 개발자 중심의 코드 정확성에 집중한다면,
BDD는 비즈니스 요구사항을 자연어로 표현하여 이해관계자와의 소통을 중시한다.

```
TDD 진화 경로:
TDD (코드 정확성) → ATDD (인수 테스트) → BDD (행위 명세 + 소통)
```

| 구분 | TDD | BDD |
|------|-----|-----|
| 관점 | 개발자 중심 | 사용자/비즈니스 중심 |
| 명세 언어 | 프로그래밍 언어 | 자연어 (Gherkin) |
| 테스트 단위 | 함수/클래스 | 시나리오/행위 |
| 산출물 | 단위 테스트 | 살아있는 문서(living documentation) |
| 참여자 | 개발자 | 개발자 + 기획자 + QA |

> 출처: Daniel Terhorst-North (BDD 창시자), [Introducing BDD](https://dannorth.net/blog/introducing-bdd/)

---

## 1. Given-When-Then [Daniel Terhorst-North & Chris Matts]

```gherkin
# features/order.feature
Feature: 주문 처리
    사용자가 상품을 주문하고 결제할 수 있다.

    Scenario: 재고가 있는 상품 주문
        Given 상품 "노트북"의 재고가 5개 있다
        And 사용자의 장바구니에 "노트북" 1개가 담겨있다
        When 사용자가 주문을 확정한다
        Then 주문이 성공적으로 생성된다
        And 재고가 4개로 감소한다

    Scenario: 재고 부족 시 주문 실패
        Given 상품 "태블릿"의 재고가 0개 있다
        And 사용자의 장바구니에 "태블릿" 1개가 담겨있다
        When 사용자가 주문을 확정한다
        Then "재고 부족" 오류가 발생한다
```

---

## 2. pytest-bdd로 구현

```python
# tests/test_order.py
import pytest
from pytest_bdd import scenario, given, when, then, parsers


@scenario("../features/order.feature", "재고가 있는 상품 주문")
def test_order_with_stock():
    pass


@scenario("../features/order.feature", "재고 부족 시 주문 실패")
def test_order_without_stock():
    pass


# --- Given 단계: 초기 상태 설정 ---
@given(
    parsers.parse('상품 "{product}"의 재고가 {count:d}개 있다'),
    target_fixture="inventory",
)
def inventory_with_stock(product, count):
    inventory = Inventory()
    inventory.set_stock(product, count)
    return inventory


@given(
    parsers.parse('사용자의 장바구니에 "{product}" {count:d}개가 담겨있다'),
    target_fixture="cart",
)
def cart_with_item(product, count):
    cart = ShoppingCart()
    cart.add(product, count)
    return cart


# --- When 단계: 행위 실행 ---
@when("사용자가 주문을 확정한다", target_fixture="order_result")
def place_order(inventory, cart):
    service = OrderService(inventory)
    try:
        order = service.place_order(cart)
        return {"success": True, "order": order}
    except InsufficientStockError as e:
        return {"success": False, "error": str(e)}


# --- Then 단계: 결과 검증 ---
@then("주문이 성공적으로 생성된다")
def order_created(order_result):
    assert order_result["success"] is True


@then(parsers.parse("재고가 {count:d}개로 감소한다"))
def stock_decreased(inventory, count):
    assert inventory.get_stock("노트북") == count


@then(parsers.parse('"{message}" 오류가 발생한다'))
def error_occurred(order_result, message):
    assert order_result["success"] is False
    assert message in order_result["error"]
```

---

## 3. Background: 공유 전제 조건

Background는 feature 파일 내 **모든 시나리오에 공통되는 전제 조건**을 한 번만 선언한다.
4줄 이하로 짧게 유지하고, 일부 시나리오에만 해당하는 설정은 넣지 않는다.

```gherkin
Feature: 재고 관리
    Background:
        Given 데이터베이스에 다음 상품이 존재한다
            | name   | stock | price  |
            | 키보드 | 10    | 50000  |
            | 마우스 | 3     | 25000  |
            | 모니터 | 0     | 350000 |

    Scenario: 재고 출고 - 정상
        When 상품 "키보드"에서 3개를 출고한다
        Then 상품 "키보드"의 재고가 7개여야 한다

    Scenario: 재고 부족 시 출고 실패
        When 상품 "모니터"에서 1개를 출고하면 에러가 발생한다
        Then "재고 부족" 에러가 반환된다
```

**핵심 규칙**:
- 모든 시나리오에 공통되는 설정만 포함한다
- 비즈니스 맥락을 기술한다 (기술적 셋업이 아님)
- 생생하고 기억하기 쉬운 이름을 사용한다 ("User A"보다 "Alice")

pytest-bdd에서 Background 단계는 `.feature` 파일에 선언하면 자동으로 수집된다.
여러 feature 파일에 걸쳐 공유하는 단계는 `conftest.py`에 배치한다.

> 출처: [Cucumber Gherkin Reference](https://cucumber.io/docs/gherkin/reference/), [Writing Better Gherkin](https://cucumber.io/docs/bdd/better-gherkin/)

---

## 4. Scenario Outline + Examples: 파라미터화된 시나리오

동일한 시나리오를 다른 데이터 조합으로 반복 실행한다. Examples 블록을 명명하여
정상 케이스, 에지 케이스, 에러 케이스를 구분한다.

```gherkin
Scenario Outline: 배송비 계산
    Given 상품 무게가 <weight>kg이다
    When 거리 <distance>km로 배송을 요청한다
    Then 배송비는 <fee>원이어야 한다

    Examples: 정상 케이스
        | weight | distance | fee   |
        | 2.0    | 150      | 5000  |
        | 5.0    | 300      | 8500  |

    Examples: 경계값
        | weight | distance | fee   |
        | 0.1    | 1        | 3050  |
        | 100.0  | 1000     | 50000 |

    Examples: 익스프레스
        | weight | distance | fee   |
        | 2.0    | 150      | 7500  |
```

**핵심 규칙**:
- `<angle_bracket>` 파라미터가 Examples 테이블의 컬럼 헤더와 매핑된다
- Examples 블록마다 이름을 붙여서 자기 문서화한다
- 테이블이 커지면 별도의 Scenario Outline으로 분리한다
- UI 테스트처럼 느린 테스트에는 과도한 Outline을 피한다

> 출처: [Cucumber Gherkin Reference](https://cucumber.io/docs/gherkin/reference/), [pytest-bdd Documentation](https://pytest-bdd.readthedocs.io/)

---

## 5. Rule 키워드 (Gherkin v6+)

같은 비즈니스 규칙을 예증하는 시나리오들을 그룹화한다.
파일을 분리하지 않고도 논리적 구조를 제공한다.

```gherkin
Feature: 할인 정책

    Rule: 골드 회원은 10% 할인을 받는다
        Scenario: 골드 회원의 일반 상품 구매
            Given 골드 회원 "Alice"가 로그인했다
            When 가격 10000원인 상품을 구매한다
            Then 결제 금액이 9000원이어야 한다

        Scenario: 골드 회원의 프로모션 상품 구매
            Given 골드 회원 "Alice"가 로그인했다
            And 상품에 5% 프로모션이 적용되어 있다
            When 가격 10000원인 상품을 구매한다
            Then 결제 금액이 8500원이어야 한다

    Rule: 최대 할인율은 30%를 초과할 수 없다
        Scenario: 할인 캡 적용
            Given 플래티넘 회원 "Bob"이 로그인했다
            And 상품에 25% 프로모션이 적용되어 있다
            When 가격 10000원인 상품을 구매한다
            Then 결제 금액이 7000원이어야 한다
```

> 출처: [Gherkin Rules](https://cucumber.io/blog/bdd/gherkin-rules/)

---

## 6. Feature 파일 구조 패턴

**파일 분리 기준**:
- `.feature` 파일 하나에 Feature 키워드 하나 (Gherkin 규칙)
- **비즈니스 역량(capability)** 기준으로 분리한다 (사용자 스토리 단위가 아님)
- 파일을 한눈에 파악할 수 없으면 분리한다
- 폴더 계층으로 세분화한다

```
features/
├── inventory/
│   ├── stock_management.feature    # 입출고
│   ├── stock_alerts.feature        # 재고 부족 알림
│   └── stock_availability.feature  # 가용성 확인
├── order/
│   ├── order_creation.feature
│   └── order_payment.feature
└── auth/
    └── login.feature
```

**태그로 횡단적 조직화**:

```gherkin
@smoke @inventory
Feature: 재고 관리
```

```bash
pytest --tags="smoke"          # 스모크 테스트만
pytest --tags="not slow"       # 느린 테스트 제외
```

> 출처: [Solving: How to Organise Feature Files](https://cucumber.io/blog/bdd/solving-how-to-organise-feature-files/), [Automation Panda: What Should Be a Feature](https://automationpanda.com/2017/10/19/in-bdd-what-should-be-a-feature/)

---

## 7. Step 재사용 전략

### 안티패턴: Feature 파일과 1:1 결합

Feature 파일마다 Step 파일을 만들면 중복과 유지보수 비용이 폭증한다.

### 올바른 접근: 도메인 개념 기준 구성

```
tests/step_defs/
├── conftest.py                # 공유 step (Given 로그인, Given DB 시딩)
├── inventory_steps.py         # 재고 도메인 step
├── order_steps.py             # 주문 도메인 step
└── auth_steps.py              # 인증 도메인 step
```

**conftest.py 계층 활용**:
- 부모 `conftest.py`에 공통 step을 배치한다
- 자식 테스트 파일이 부모의 step을 자동으로 상속한다
- feature 특화 step만 테스트 모듈에 직접 작성한다

```python
# tests/conftest.py -- 모든 BDD 테스트에서 공유
from pytest_bdd import given

@given("관리자 사용자가 로그인했다", target_fixture="admin_user")
def admin_logged_in():
    user = create_admin()
    login(user)
    return user
```

### 안티패턴: 접속사 Step

```gherkin
# 나쁨: 재사용 불가능한 결합 step
Given 사용자가 로그인하고 관리자 권한이 있고 대시보드에 있다

# 좋음: 개별 step으로 분리
Given 사용자가 로그인했다
And 관리자 권한이 부여되어 있다
And 대시보드 페이지에 있다
```

> 출처: [Cucumber Anti-patterns](https://cucumber.io/docs/guides/anti-patterns/), [pytest-bdd Documentation](https://pytest-bdd.readthedocs.io/)

---

## 8. BDD 안티패턴과 BRIEF 원칙

### 8개 주요 안티패턴

| 안티패턴 | 설명 | 해결 |
|----------|------|------|
| **코드 이후에 Gherkin 작성** | 협업 설계 이점을 상실 | 구현 전에 Gherkin을 먼저 작성 |
| **부수적 세부사항** | 핵심 행위와 무관한 설정이 시나리오를 흐림 | 행위 이해에 필수적인 내용만 포함 |
| **여러 결과 동시 검증** | 하나의 시나리오가 여러 행위를 검증 | 시나리오 하나 = 행위 하나 = 실패 사유 하나 |
| **Feature 결합 Step** | Step이 특정 feature에서만 재사용 가능 | 도메인 개념 기준으로 step 구성 |
| **접속사 Step** | "그리고"로 여러 행위를 하나의 step에 결합 | And/But 키워드로 개별 step 분리 |
| **UI 중심 시나리오** | 버튼 클릭, 필드 입력 등 구현을 기술 | 무엇(행위)을 기술, 어떻게(구현)는 제외 |
| **단독 Gherkin 작성** | 한 사람이 격리되어 모든 Gherkin 작성 | Three Amigos 세션 (기획+개발+QA) |
| **Outline 남용** | 과도한 파라미터화로 느리고 비대한 스위트 | 느린(UI) 테스트에는 절제, 빠른 테스트에만 활용 |

### BRIEF 원칙 (좋은 시나리오의 기준)

- **B**usiness-language: 비즈니스 언어로 작성
- **R**eal data: 구체적이고 생생한 예시 사용
- **I**ntention-revealing: 무엇을 하는지(의도) 기술, 어떻게는 제외
- **E**ssential: 부수적 세부사항 제거
- **F**ocused: 시나리오 하나에 행위 하나

> 출처: [Cucumber Anti-patterns Part 1](https://cucumber.io/blog/bdd/cucumber-antipatterns-part-one/), [Keep Your Scenarios BRIEF](https://cucumber.io/blog/bdd/keep-your-scenarios-brief/)

---

## 9. 에지 케이스 열거 전략

세 가지 범주로 시나리오를 시작한다:
1. **Happy path** -- 주요 성공 시나리오
2. **Failure path** -- 예상되는 에러 조건
3. **Edge cases** -- 경계값, 빈 입력, 최대값

```gherkin
Scenario Outline: 출금 경계 조건
    Given 계좌 잔고가 <balance>원이다
    When <amount>원을 출금한다
    Then 결과는 <outcome>이어야 한다

    Examples: 정상 거래
        | balance | amount | outcome |
        | 10000   | 5000   | success |
        | 5000    | 5000   | success |

    Examples: 경계값
        | balance | amount | outcome      |
        | 0       | 1      | insufficient |
        | 1       | 1      | success      |
        | 5000    | 5001   | insufficient |

    Examples: 잘못된 입력
        | balance | amount | outcome        |
        | 10000   | 0      | invalid_amount |
        | 10000   | -1     | invalid_amount |
```

명명된 Examples 블록으로 에지 케이스를 범주화하면 누락을 방지하고 자기 문서화된다.

> 출처: [Cucumber Gherkin Reference](https://cucumber.io/docs/gherkin/reference/), [SmartBear Best Practices](https://support.smartbear.com/cucumberstudio/docs/tests/best-practices.html)
