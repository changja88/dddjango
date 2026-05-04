`/private/tmp/dddjango-codex-eval` 안에는 실제 Django 프로젝트/테스트 파일이 없어 특정 라인 단위 리뷰는 못 했습니다. 대신 활성화된 `implementation-test`, `implementation-django` 기준으로 “DB fixture 과의존 + 약한 assert”에 대한 pytest 품질 리뷰 기준을 정리합니다.

**핵심 리뷰**
[Fixture 과의존] -- DB fixture가 시나리오의 전제 조건을 숨기면 테스트가 무엇을 검증하는지 읽히지 않습니다. `user`, `order`, `paid_order`처럼 의미 있는 fixture는 괜찮지만, 거대한 `seed_db`, `sample_data`, `db_fixture`는 테스트 의도를 가립니다.

[Weak Assertion] -- `assert response.status_code == 200`, `assert obj is not None`, `assert len(items) > 0`만 있으면 회귀 보호가 약합니다. 상태 코드뿐 아니라 응답 JSON, DB 상태 변화, 생성/수정된 필드, 권한/소유권, 부수효과까지 검증해야 합니다.

[Excessive DB Integration] -- 단위 테스트로 충분한 도메인 규칙까지 DB를 타면 느리고 깨지기 쉽습니다. 순수 로직은 DB 없이 테스트하고, ORM/쿼리/트랜잭션/constraint가 핵심인 경우에만 `django_db`를 붙이는 기준이 필요합니다.

[Obscure Test] -- fixture가 여러 단계의 관계 데이터를 자동 생성하면 테스트가 실패했을 때 원인 파악이 어렵습니다. 각 테스트의 Arrange에서 핵심 데이터는 명시하고, 반복 보일러플레이트만 factory/fixture로 숨기는 편이 낫습니다.

[Missing Behavior Assertion] -- API 테스트는 “요청 성공”이 아니라 “비즈니스 동작 발생”을 검증해야 합니다. 예: 주문 생성이면 응답 코드, 응답 body, `Order.objects.count()`, `status`, `user`, `total_price`, 재고 차감, 이벤트/메일 enqueue 여부를 함께 봅니다.

**개선 기준**
1. fixture는 “데이터 덤프”가 아니라 “의미 있는 상태”를 만든다.  
   예: `user`보다 `active_user`, `expired_subscription`, `paid_order`가 낫습니다.

2. JSON/DB fixture 파일 의존은 줄이고 `factory_boy`를 기본으로 둔다.  
   `Trait`로 상태를 표현합니다: `OrderFactory(paid=True)`, `UserFactory(staff=True)`.

3. 각 테스트는 AAA 구조를 따른다.  
   Act는 한 줄이어야 하고, 여러 Act가 있으면 테스트를 분리합니다.

4. assert는 최소 “출력 + 상태 변화”를 검증한다.  
   API면 `status_code`만 보지 말고 응답 body와 DB 변화를 같이 봅니다.

5. DB가 필요 없는 테스트는 DB를 쓰지 않는다.  
   `SimpleTestCase` 또는 순수 pytest 테스트로 분리하고, `@pytest.mark.django_db`는 필요한 테스트에만 붙입니다.

6. 쿼리 성능이 사용자 경로에 중요하면 `assertNumQueries`를 추가한다.  
   list/detail API, dashboard, admin-like 화면은 N+1 회귀 테스트가 있어야 합니다.

7. 반복 케이스는 fixture 복제가 아니라 `pytest.mark.parametrize`로 표현한다.  
   경계값, 권한 조합, 상태 전이 테스트에 특히 유효합니다.

8. 외부 의존성만 mock한다.  
   핵심 비즈니스 로직을 mock하지 말고 실제 객체나 InMemory Fake를 씁니다. mock을 쓰면 `spec`/`autospec`을 강제합니다.

**약한 테스트 예시**
```python
def test_create_order(client, user, product):
    client.force_login(user)

    response = client.post("/orders/", {"product_id": product.id})

    assert response.status_code == 200
```

**개선 예시**
```python
@pytest.mark.django_db
def test_create_order_authenticated_user_creates_pending_order(client, user, product):
    client.force_login(user)

    response = client.post("/orders/", {"product_id": product.id})

    assert response.status_code == 201
    assert response.json()["status"] == "pending"

    order = Order.objects.get()
    assert order.user == user
    assert order.product == product
    assert order.status == Order.Status.PENDING
    assert order.total_price == product.price
```

우선 적용할 리뷰 게이트는 이 정도가 적절합니다: “fixture 이름만 보고 상태가 이해되는가”, “Act가 하나인가”, “status code 외에 비즈니스 결과를 검증하는가”, “DB가 정말 필요한 테스트인가”, “실패 시 원인이 한눈에 좁혀지는가”.

---
> **관련 스킬 참조:**
> - pytest fixture/assert 품질 개선 → **implementation-test** 스킬
> - Django 테스트 구조와 DB 사용 기준 → **implementation-django** 스킬