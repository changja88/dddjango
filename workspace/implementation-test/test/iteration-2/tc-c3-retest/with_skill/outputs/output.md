# 재고 관리 시스템 BDD 테스트 + DB 통합 테스트

## 프로젝트 구조

```
tests/
├── features/
│   └── inventory/
│       ├── stock_management.feature    # 입출고 시나리오
│       └── stock_alerts.feature        # 재고 부족 알림 시나리오
├── conftest.py                         # DB 컨테이너 + 세션 픽스처
├── test_inventory_bdd.py               # BDD step 구현
└── test_inventory_integration.py       # DB 통합 테스트
```

---

## 1. Gherkin Feature 파일

### `features/inventory/stock_management.feature`

```gherkin
Feature: 재고 입출고 관리
    재고 담당자가 상품의 입고와 출고를 처리할 수 있다.

    Background:
        Given 데이터베이스에 다음 상품이 존재한다
            | id | name   | stock | price  |
            | 1  | 키보드 | 10    | 50000  |
            | 2  | 마우스 | 3     | 25000  |
            | 3  | 모니터 | 0     | 350000 |

    Rule: 재고 출고는 보유 수량 이내에서만 가능하다

        Scenario: 재고 출고 - 정상
            When 상품 1에서 3개를 출고한다
            Then 상품 1의 재고가 7개여야 한다

        Scenario: 재고 부족 시 출고 실패
            When 상품 2에서 5개를 출고하면 에러가 발생한다
            Then "재고 부족" 에러가 반환된다

        Scenario: 재고가 0인 상품 출고 실패
            When 상품 3에서 1개를 출고하면 에러가 발생한다
            Then "재고 부족" 에러가 반환된다

    Rule: 입고 수량은 항상 양수여야 한다

        Scenario: 재고 입고 - 정상
            When 상품 1에 5개를 입고한다
            Then 상품 1의 재고가 15개여야 한다

        Scenario: 0 이하 수량 입고 시 에러
            When 상품 1에 0개를 입고하면 에러가 발생한다
            Then "수량은 0보다 커야 합니다" 에러가 반환된다

    Rule: 가용성 확인은 현재 재고와 요청 수량을 비교한다

        Scenario Outline: 상품 가용성 확인
            When 상품 <product_id>의 <quantity>개 가용성을 확인한다
            Then 가용성 결과가 <available>이어야 한다

            Examples: 충분한 재고
                | product_id | quantity | available |
                | 1          | 5        | True      |
                | 1          | 10       | True      |

            Examples: 부족한 재고
                | product_id | quantity | available |
                | 1          | 11       | False     |
                | 3          | 1        | False     |

            Examples: 존재하지 않는 상품
                | product_id | quantity | available |
                | 999        | 1        | False     |
```

### `features/inventory/stock_alerts.feature`

```gherkin
Feature: 재고 부족 알림
    재고 담당자가 임계값 이하인 상품 목록을 조회할 수 있다.

    Background:
        Given 데이터베이스에 다음 상품이 존재한다
            | id | name   | stock | price  |
            | 1  | 키보드 | 10    | 50000  |
            | 2  | 마우스 | 3     | 25000  |
            | 3  | 모니터 | 0     | 350000 |
            | 4  | 헤드셋 | 5     | 80000  |

    Rule: 임계값 이하인 상품만 알림 대상이다

        Scenario: 기본 임계값(5)으로 재고 부족 상품 조회
            When 기본 임계값으로 재고 부족 상품을 조회한다
            Then 재고 부족 상품이 2개여야 한다
            And 조회 결과에 "마우스"가 포함되어야 한다
            And 조회 결과에 "모니터"가 포함되어야 한다

        Scenario: 커스텀 임계값으로 재고 부족 상품 조회
            When 임계값 10으로 재고 부족 상품을 조회한다
            Then 재고 부족 상품이 3개여야 한다
            And 조회 결과에 "마우스"가 포함되어야 한다
            And 조회 결과에 "모니터"가 포함되어야 한다
            And 조회 결과에 "헤드셋"가 포함되어야 한다

        Scenario: 임계값 0으로 조회 시 결과 없음
            When 임계값 0으로 재고 부족 상품을 조회한다
            Then 재고 부족 상품이 0개여야 한다
```

---

## 2. conftest.py -- DB 컨테이너 및 세션 픽스처

```python
# tests/conftest.py
import pytest
from testcontainers.postgres import PostgresContainer
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import Session, DeclarativeBase


class Base(DeclarativeBase):
    pass


class ProductModel(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    stock = Column(Integer, nullable=False, default=0)
    price = Column(Float, nullable=False)


@pytest.fixture(scope="session")
def postgres_container():
    """세션 스코프: 전체 테스트 스위트에서 컨테이너 1회 시작."""
    with PostgresContainer("postgres:16-alpine") as postgres:
        yield postgres


@pytest.fixture(scope="session")
def db_engine(postgres_container):
    """세션 스코프 엔진. 테이블 생성 포함."""
    engine = create_engine(postgres_container.get_connection_url())
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(db_engine):
    """각 테스트를 트랜잭션으로 감싸서 격리."""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()
```

---

## 3. 도메인 모델 + 리포지토리 (SQLAlchemy 구현)

```python
# inventory/models.py
from dataclasses import dataclass


@dataclass
class Product:
    id: int
    name: str
    stock: int
    price: float
```

```python
# inventory/repository.py
from sqlalchemy.orm import Session
from inventory.models import Product


class InventoryRepository:
    def __init__(self, session: Session):
        self.session = session

    def find_by_id(self, product_id: int) -> Product | None:
        from tests.conftest import ProductModel

        row = self.session.get(ProductModel, product_id)
        if row is None:
            return None
        return Product(id=row.id, name=row.name, stock=row.stock, price=row.price)

    def save(self, product: Product) -> Product:
        from tests.conftest import ProductModel

        row = self.session.get(ProductModel, product.id)
        if row is None:
            row = ProductModel(
                id=product.id,
                name=product.name,
                stock=product.stock,
                price=product.price,
            )
            self.session.add(row)
        else:
            row.stock = product.stock
            row.price = product.price
            row.name = product.name
        self.session.flush()
        return product

    def find_low_stock(self, threshold: int = 5) -> list[Product]:
        from tests.conftest import ProductModel

        rows = (
            self.session.query(ProductModel)
            .filter(ProductModel.stock < threshold)
            .all()
        )
        return [
            Product(id=r.id, name=r.name, stock=r.stock, price=r.price) for r in rows
        ]
```

```python
# inventory/service.py
from inventory.models import Product
from inventory.repository import InventoryRepository


class InventoryService:
    def __init__(self, repo: InventoryRepository):
        self.repo = repo

    def add_stock(self, product_id: int, quantity: int) -> Product:
        if quantity <= 0:
            raise ValueError("수량은 0보다 커야 합니다")
        product = self.repo.find_by_id(product_id)
        if not product:
            raise ValueError(f"상품 {product_id}을 찾을 수 없습니다")
        product.stock += quantity
        return self.repo.save(product)

    def remove_stock(self, product_id: int, quantity: int) -> Product:
        if quantity <= 0:
            raise ValueError("수량은 0보다 커야 합니다")
        product = self.repo.find_by_id(product_id)
        if not product:
            raise ValueError(f"상품 {product_id}을 찾을 수 없습니다")
        if product.stock < quantity:
            raise ValueError(f"재고 부족: 현재 {product.stock}개, 요청 {quantity}개")
        product.stock -= quantity
        return self.repo.save(product)

    def get_low_stock_alerts(self, threshold: int = 5) -> list[Product]:
        return self.repo.find_low_stock(threshold)

    def check_availability(self, product_id: int, quantity: int) -> bool:
        product = self.repo.find_by_id(product_id)
        if not product:
            return False
        return product.stock >= quantity
```

---

## 4. BDD Step 구현

```python
# tests/test_inventory_bdd.py
import pytest
from pytest_bdd import scenario, given, when, then, parsers

from tests.conftest import ProductModel
from inventory.repository import InventoryRepository
from inventory.service import InventoryService


# --- Scenario 등록: stock_management.feature ---


@scenario(
    "features/inventory/stock_management.feature",
    "재고 출고 - 정상",
)
def test_remove_stock_normal():
    pass


@scenario(
    "features/inventory/stock_management.feature",
    "재고 부족 시 출고 실패",
)
def test_remove_stock_insufficient():
    pass


@scenario(
    "features/inventory/stock_management.feature",
    "재고가 0인 상품 출고 실패",
)
def test_remove_stock_zero():
    pass


@scenario(
    "features/inventory/stock_management.feature",
    "재고 입고 - 정상",
)
def test_add_stock_normal():
    pass


@scenario(
    "features/inventory/stock_management.feature",
    "0 이하 수량 입고 시 에러",
)
def test_add_stock_invalid_quantity():
    pass


@scenario(
    "features/inventory/stock_management.feature",
    "상품 가용성 확인",
)
def test_check_availability():
    pass


# --- Scenario 등록: stock_alerts.feature ---


@scenario(
    "features/inventory/stock_alerts.feature",
    "기본 임계값(5)으로 재고 부족 상품 조회",
)
def test_low_stock_default_threshold():
    pass


@scenario(
    "features/inventory/stock_alerts.feature",
    "커스텀 임계값으로 재고 부족 상품 조회",
)
def test_low_stock_custom_threshold():
    pass


@scenario(
    "features/inventory/stock_alerts.feature",
    "임계값 0으로 조회 시 결과 없음",
)
def test_low_stock_zero_threshold():
    pass


# --- Shared Fixtures ---


@pytest.fixture()
def inventory_service(db_session):
    repo = InventoryRepository(db_session)
    return InventoryService(repo)


@pytest.fixture()
def action_result():
    """Step 간 결과 전달용 컨테이너."""
    return {}


# --- Given Steps ---


@given("데이터베이스에 다음 상품이 존재한다", target_fixture="seed_products")
def seed_products(db_session, datatable):
    """Background에서 호출. datatable은 pytest-bdd가 파싱한 테이블."""
    products = []
    for row in datatable:
        product = ProductModel(
            id=int(row["id"]),
            name=row["name"],
            stock=int(row["stock"]),
            price=float(row["price"]),
        )
        db_session.add(product)
        products.append(product)
    db_session.flush()
    return products


# --- When Steps: 출고 ---


@when(
    parsers.parse("상품 {product_id:d}에서 {quantity:d}개를 출고한다"),
    target_fixture="action_result",
)
def remove_stock(inventory_service, product_id, quantity):
    result = inventory_service.remove_stock(product_id, quantity)
    return {"success": True, "product": result}


@when(
    parsers.parse("상품 {product_id:d}에서 {quantity:d}개를 출고하면 에러가 발생한다"),
    target_fixture="action_result",
)
def remove_stock_with_error(inventory_service, product_id, quantity):
    try:
        inventory_service.remove_stock(product_id, quantity)
        return {"success": True, "error": None}
    except ValueError as e:
        return {"success": False, "error": str(e)}


# --- When Steps: 입고 ---


@when(
    parsers.parse("상품 {product_id:d}에 {quantity:d}개를 입고한다"),
    target_fixture="action_result",
)
def add_stock(inventory_service, product_id, quantity):
    result = inventory_service.add_stock(product_id, quantity)
    return {"success": True, "product": result}


@when(
    parsers.parse("상품 {product_id:d}에 {quantity:d}개를 입고하면 에러가 발생한다"),
    target_fixture="action_result",
)
def add_stock_with_error(inventory_service, product_id, quantity):
    try:
        inventory_service.add_stock(product_id, quantity)
        return {"success": True, "error": None}
    except ValueError as e:
        return {"success": False, "error": str(e)}


# --- When Steps: 가용성 확인 ---


@when(
    parsers.parse("상품 {product_id:d}의 {quantity:d}개 가용성을 확인한다"),
    target_fixture="action_result",
)
def check_availability(inventory_service, product_id, quantity):
    available = inventory_service.check_availability(product_id, quantity)
    return {"available": available}


# --- When Steps: 재고 부족 조회 ---


@when("기본 임계값으로 재고 부족 상품을 조회한다", target_fixture="action_result")
def get_low_stock_default(inventory_service):
    alerts = inventory_service.get_low_stock_alerts()
    return {"alerts": alerts}


@when(
    parsers.parse("임계값 {threshold:d}으로 재고 부족 상품을 조회한다"),
    target_fixture="action_result",
)
def get_low_stock_custom(inventory_service, threshold):
    alerts = inventory_service.get_low_stock_alerts(threshold)
    return {"alerts": alerts}


# --- Then Steps: 재고 검증 ---


@then(parsers.parse("상품 {product_id:d}의 재고가 {expected:d}개여야 한다"))
def verify_stock(inventory_service, product_id, expected):
    product = inventory_service.repo.find_by_id(product_id)
    assert product is not None
    assert product.stock == expected


# --- Then Steps: 에러 검증 ---


@then(parsers.parse('"{message}" 에러가 반환된다'))
def verify_error_message(action_result, message):
    assert action_result["success"] is False
    assert message in action_result["error"]


# --- Then Steps: 가용성 검증 ---


@then(parsers.parse("가용성 결과가 {expected}이어야 한다"))
def verify_availability(action_result, expected):
    expected_bool = expected == "True"
    assert action_result["available"] is expected_bool


# --- Then Steps: 재고 부족 알림 검증 ---


@then(parsers.parse("재고 부족 상품이 {count:d}개여야 한다"))
def verify_low_stock_count(action_result, count):
    assert len(action_result["alerts"]) == count


@then(parsers.parse('조회 결과에 "{name}"가 포함되어야 한다'))
def verify_low_stock_contains(action_result, name):
    names = [p.name for p in action_result["alerts"]]
    assert name in names


@then(parsers.parse('조회 결과에 "{name}"가 포함되어야 한다'))
def verify_low_stock_contains_alt(action_result, name):
    names = [p.name for p in action_result["alerts"]]
    assert name in names
```

---

## 5. DB 통합 테스트 (testcontainers 직접 사용)

```python
# tests/test_inventory_integration.py
"""
InventoryRepository + InventoryService의 실제 PostgreSQL 통합 테스트.
testcontainers로 Docker 기반 PostgreSQL을 사용한다.
conftest.py의 postgres_container, db_session 픽스처를 재사용한다.
"""
import pytest

from tests.conftest import ProductModel
from inventory.models import Product
from inventory.repository import InventoryRepository
from inventory.service import InventoryService


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def repository(db_session):
    return InventoryRepository(db_session)


@pytest.fixture()
def service(repository):
    return InventoryService(repository)


@pytest.fixture()
def seeded_products(db_session):
    """3개의 테스트 상품을 DB에 시딩한다."""
    products = [
        ProductModel(id=1, name="키보드", stock=10, price=50000),
        ProductModel(id=2, name="마우스", stock=3, price=25000),
        ProductModel(id=3, name="모니터", stock=0, price=350000),
    ]
    for p in products:
        db_session.add(p)
    db_session.flush()
    return products


# ---------------------------------------------------------------------------
# Repository Tests
# ---------------------------------------------------------------------------


class TestInventoryRepository:

    def test_find_by_id_returns_product(self, repository, seeded_products):
        result = repository.find_by_id(1)

        assert result is not None
        assert result.name == "키보드"
        assert result.stock == 10

    def test_find_by_id_returns_none_for_missing(self, repository, seeded_products):
        result = repository.find_by_id(999)

        assert result is None

    def test_save_updates_existing_product(self, repository, seeded_products):
        product = Product(id=1, name="키보드", stock=20, price=55000)

        saved = repository.save(product)

        assert saved.stock == 20
        reloaded = repository.find_by_id(1)
        assert reloaded.stock == 20

    def test_find_low_stock_with_default_threshold(
        self, repository, seeded_products
    ):
        results = repository.find_low_stock()

        names = {p.name for p in results}
        assert names == {"마우스", "모니터"}

    def test_find_low_stock_with_custom_threshold(
        self, repository, seeded_products
    ):
        results = repository.find_low_stock(threshold=11)

        names = {p.name for p in results}
        assert names == {"키보드", "마우스", "모니터"}

    def test_find_low_stock_returns_empty_when_all_above(
        self, repository, seeded_products
    ):
        results = repository.find_low_stock(threshold=0)

        assert results == []


# ---------------------------------------------------------------------------
# Service Tests (real DB, no mocks)
# ---------------------------------------------------------------------------


class TestInventoryServiceIntegration:

    def test_add_stock_increases_quantity(self, service, seeded_products):
        result = service.add_stock(product_id=1, quantity=5)

        assert result.stock == 15

    def test_add_stock_rejects_zero_quantity(self, service, seeded_products):
        with pytest.raises(ValueError, match="수량은 0보다 커야 합니다"):
            service.add_stock(product_id=1, quantity=0)

    def test_add_stock_rejects_negative_quantity(self, service, seeded_products):
        with pytest.raises(ValueError, match="수량은 0보다 커야 합니다"):
            service.add_stock(product_id=1, quantity=-3)

    def test_add_stock_raises_for_missing_product(self, service, seeded_products):
        with pytest.raises(ValueError, match="상품 999을 찾을 수 없습니다"):
            service.add_stock(product_id=999, quantity=5)

    def test_remove_stock_decreases_quantity(self, service, seeded_products):
        result = service.remove_stock(product_id=1, quantity=3)

        assert result.stock == 7

    def test_remove_stock_allows_full_depletion(self, service, seeded_products):
        result = service.remove_stock(product_id=2, quantity=3)

        assert result.stock == 0

    def test_remove_stock_rejects_insufficient_stock(
        self, service, seeded_products
    ):
        with pytest.raises(ValueError, match="재고 부족"):
            service.remove_stock(product_id=2, quantity=5)

    def test_remove_stock_rejects_zero_quantity(self, service, seeded_products):
        with pytest.raises(ValueError, match="수량은 0보다 커야 합니다"):
            service.remove_stock(product_id=1, quantity=0)

    def test_remove_stock_raises_for_missing_product(
        self, service, seeded_products
    ):
        with pytest.raises(ValueError, match="상품 999을 찾을 수 없습니다"):
            service.remove_stock(product_id=999, quantity=3)

    def test_check_availability_true_when_sufficient(
        self, service, seeded_products
    ):
        assert service.check_availability(product_id=1, quantity=10) is True

    def test_check_availability_false_when_insufficient(
        self, service, seeded_products
    ):
        assert service.check_availability(product_id=1, quantity=11) is False

    def test_check_availability_false_for_missing_product(
        self, service, seeded_products
    ):
        assert service.check_availability(product_id=999, quantity=1) is False

    def test_get_low_stock_alerts_default_threshold(
        self, service, seeded_products
    ):
        alerts = service.get_low_stock_alerts()

        names = {p.name for p in alerts}
        assert names == {"마우스", "모니터"}

    def test_get_low_stock_alerts_custom_threshold(
        self, service, seeded_products
    ):
        alerts = service.get_low_stock_alerts(threshold=11)

        assert len(alerts) == 3

    def test_sequential_operations_are_consistent(
        self, service, seeded_products
    ):
        """입고 후 출고가 순차적으로 반영되는지 검증한다."""
        service.add_stock(product_id=1, quantity=5)

        result = service.remove_stock(product_id=1, quantity=12)

        assert result.stock == 3
```

---

## 6. 테스트 설정

### `pyproject.toml`

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
markers = [
    "integration: 실제 DB를 사용하는 통합 테스트",
]
bdd_features_base_dir = "tests/"
```

### 필요 패키지

```
pytest
pytest-bdd
testcontainers[postgres]
sqlalchemy
psycopg2-binary
```

### 실행 명령

```bash
# BDD 테스트만 실행
pytest tests/test_inventory_bdd.py -v

# 통합 테스트만 실행
pytest tests/test_inventory_integration.py -v

# 전체 실행
pytest tests/ -v
```

---

## 설계 결정 요약

| 결정 | 근거 |
|------|------|
| **Feature 파일을 비즈니스 역량 기준 분리** | `stock_management`(입출고)와 `stock_alerts`(알림)는 독립된 비즈니스 역량. BDD 레퍼런스 Section 6의 파일 분리 기준을 따른다. |
| **Background로 공유 전제 조건 선언** | 모든 시나리오에 공통되는 상품 시딩을 Background에 배치. BDD 레퍼런스 Section 3의 규칙(4줄 이하, 모든 시나리오에 공통)을 따른다. |
| **Rule 키워드로 비즈니스 규칙 그룹화** | 같은 feature 내에서 "출고는 보유 수량 이내", "입고 수량은 양수" 등 규칙별로 시나리오를 그룹화. BDD 레퍼런스 Section 5를 따른다. |
| **Scenario Outline으로 가용성 확인 파라미터화** | Happy/Failure/Edge 세 범주의 Examples 블록으로 구분. BDD 레퍼런스 Section 4, 9의 에지 케이스 열거 전략을 따른다. |
| **BRIEF 원칙 준수** | 시나리오에 기술적 세부사항(DB 연결, SQL 등) 없이 비즈니스 언어로만 작성. Section 8의 안티패턴(부수적 세부사항, UI 중심)을 회피한다. |
| **Session 스코프 컨테이너 + Function 스코프 트랜잭션 롤백** | 컨테이너 시작 비용(수 초)은 세션에서 1회, 테스트 격리는 트랜잭션 롤백으로 보장. integration-testing 레퍼런스 Section 1의 패턴을 따른다. |
| **통합 테스트에서 Mock 배제** | 스킬의 Three Laws 3번("Mock only external dependencies; test core logic with real objects")과 verification priority(Output-based > State-based > Communication-based)를 따라 실제 DB로 테스트한다. |
| **Step을 도메인 개념 기준으로 구성** | Feature-Step 1:1 결합 안티패턴을 피하고 conftest.py로 공유 step을 관리. BDD 레퍼런스 Section 7을 따른다. |
| **AAA 패턴 준수** | 모든 통합 테스트가 Arrange(seeded_products) - Act(단일 서비스 호출) - Assert(결과 검증) 구조. Act section은 1줄. 스킬의 핵심 규칙을 따른다. |
