# 재고 관리 시스템 BDD 테스트 + DB 통합 테스트

## 프로젝트 구조

```
inventory/
├── models.py                    # SQLAlchemy 모델 + 도메인 클래스
├── repository.py                # InventoryRepository 구현
├── service.py                   # InventoryService
├── tests/
│   ├── conftest.py              # 공통 pytest fixture
│   ├── features/
│   │   ├── stock_management.feature    # 재고 입출고 Gherkin 시나리오
│   │   ├── stock_alerts.feature        # 재고 부족 알림 시나리오
│   │   └── stock_availability.feature  # 재고 가용성 확인 시나리오
│   ├── step_defs/
│   │   ├── conftest.py                 # step_defs 전용 fixture
│   │   ├── test_stock_management.py    # 입출고 step 구현
│   │   ├── test_stock_alerts.py        # 알림 step 구현
│   │   └── test_stock_availability.py  # 가용성 step 구현
│   └── integration/
│       └── test_repository_db.py       # testcontainers DB 통합 테스트
└── requirements.txt
```

---

## 1. 도메인 모델 및 SQLAlchemy 매핑

### `models.py`

```python
from dataclasses import dataclass

from sqlalchemy import Column, Float, Integer, String
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class ProductTable(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    stock = Column(Integer, nullable=False, default=0)
    price = Column(Float, nullable=False)


@dataclass
class Product:
    id: int
    name: str
    stock: int
    price: float
```

### `repository.py`

```python
from sqlalchemy.orm import Session

from .models import Product, ProductTable


class InventoryRepository:
    def __init__(self, session: Session):
        self.session = session

    def find_by_id(self, product_id: int) -> Product | None:
        row = self.session.get(ProductTable, product_id)
        if row is None:
            return None
        return Product(id=row.id, name=row.name, stock=row.stock, price=row.price)

    def save(self, product: Product) -> Product:
        row = self.session.get(ProductTable, product.id)
        if row is None:
            row = ProductTable(
                id=product.id,
                name=product.name,
                stock=product.stock,
                price=product.price,
            )
            self.session.add(row)
        else:
            row.name = product.name
            row.stock = product.stock
            row.price = product.price
        self.session.flush()
        self.session.refresh(row)
        return Product(id=row.id, name=row.name, stock=row.stock, price=row.price)

    def find_low_stock(self, threshold: int = 5) -> list[Product]:
        rows = (
            self.session.query(ProductTable)
            .filter(ProductTable.stock <= threshold)
            .all()
        )
        return [
            Product(id=r.id, name=r.name, stock=r.stock, price=r.price) for r in rows
        ]
```

### `service.py`

```python
from .models import Product
from .repository import InventoryRepository


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
            raise ValueError(
                f"재고 부족: 현재 {product.stock}개, 요청 {quantity}개"
            )
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

## 2. Gherkin Feature 파일

### `tests/features/stock_management.feature`

```gherkin
Feature: 재고 입출고 관리
  재고 관리자로서
  상품의 재고를 입고하거나 출고하여
  정확한 재고 수량을 유지하고 싶다

  Background:
    Given 데이터베이스에 다음 상품이 존재한다
      | id | name     | stock | price  |
      | 1  | 키보드   | 10    | 50000  |
      | 2  | 마우스   | 3     | 25000  |
      | 3  | 모니터   | 0     | 350000 |

  Scenario: 재고 출고 - 정상 처리
    When 상품 1에서 3개를 출고한다
    Then 상품 1의 재고는 7개이다

  Scenario: 재고 출고 - 재고 부족 에러
    When 상품 1에서 15개를 출고하면 에러가 발생한다
    Then 에러 메시지에 "재고 부족"이 포함되어야 한다

  Scenario: 재고 출고 - 전량 출고
    When 상품 1에서 10개를 출고한다
    Then 상품 1의 재고는 0개이다

  Scenario: 재고 입고 - 정상 처리
    When 상품 2에 7개를 입고한다
    Then 상품 2의 재고는 10개이다

  Scenario: 재고 입고 - 재고 0인 상품에 입고
    When 상품 3에 5개를 입고한다
    Then 상품 3의 재고는 5개이다

  Scenario: 잘못된 수량으로 출고 시도
    When 상품 1에서 0개를 출고하면 에러가 발생한다
    Then 에러 메시지에 "수량은 0보다 커야 합니다"가 포함되어야 한다

  Scenario: 잘못된 수량으로 입고 시도
    When 상품 1에 -5개를 입고하면 에러가 발생한다
    Then 에러 메시지에 "수량은 0보다 커야 합니다"가 포함되어야 한다

  Scenario: 존재하지 않는 상품 출고 시도
    When 상품 999에서 1개를 출고하면 에러가 발생한다
    Then 에러 메시지에 "상품 999을 찾을 수 없습니다"가 포함되어야 한다
```

### `tests/features/stock_alerts.feature`

```gherkin
Feature: 재고 부족 알림
  재고 관리자로서
  재고가 임계값 이하인 상품 목록을 조회하여
  재입고 시점을 놓치지 않고 싶다

  Background:
    Given 데이터베이스에 다음 상품이 존재한다
      | id | name     | stock | price  |
      | 1  | 키보드   | 10    | 50000  |
      | 2  | 마우스   | 3     | 25000  |
      | 3  | 모니터   | 0     | 350000 |
      | 4  | 헤드셋   | 5     | 80000  |
      | 5  | 웹캠     | 15    | 45000  |

  Scenario: 기본 임계값(5)으로 재고 부족 상품 조회
    When 기본 임계값으로 재고 부족 상품을 조회한다
    Then 재고 부족 상품은 3개이다
    And 재고 부족 상품 목록에 "마우스"가 포함되어 있다
    And 재고 부족 상품 목록에 "모니터"가 포함되어 있다
    And 재고 부족 상품 목록에 "헤드셋"이 포함되어 있다

  Scenario: 커스텀 임계값으로 재고 부족 상품 조회
    When 임계값 10으로 재고 부족 상품을 조회한다
    Then 재고 부족 상품은 4개이다
    And 재고 부족 상품 목록에 "키보드"가 포함되어 있다

  Scenario: 임계값 0으로 조회하면 재고가 0인 상품만 반환
    When 임계값 0으로 재고 부족 상품을 조회한다
    Then 재고 부족 상품은 1개이다
    And 재고 부족 상품 목록에 "모니터"가 포함되어 있다

  Scenario: 모든 상품의 재고가 충분하면 빈 목록 반환
    Given 데이터베이스의 모든 상품 재고가 100으로 설정된다
    When 기본 임계값으로 재고 부족 상품을 조회한다
    Then 재고 부족 상품은 0개이다
```

### `tests/features/stock_availability.feature`

```gherkin
Feature: 재고 가용성 확인
  주문 시스템으로서
  주문 전에 재고 가용성을 확인하여
  주문 가능 여부를 판단하고 싶다

  Background:
    Given 데이터베이스에 다음 상품이 존재한다
      | id | name     | stock | price  |
      | 1  | 키보드   | 10    | 50000  |
      | 2  | 마우스   | 3     | 25000  |
      | 3  | 모니터   | 0     | 350000 |

  Scenario: 재고가 충분한 경우
    When 상품 1의 5개 가용성을 확인한다
    Then 가용 여부는 True이다

  Scenario: 재고와 정확히 같은 수량 요청
    When 상품 1의 10개 가용성을 확인한다
    Then 가용 여부는 True이다

  Scenario: 재고보다 많은 수량 요청
    When 상품 2의 5개 가용성을 확인한다
    Then 가용 여부는 False이다

  Scenario: 재고가 0인 상품의 가용성 확인
    When 상품 3의 1개 가용성을 확인한다
    Then 가용 여부는 False이다

  Scenario: 존재하지 않는 상품의 가용성 확인
    When 상품 999의 1개 가용성을 확인한다
    Then 가용 여부는 False이다
```

---

## 3. pytest-bdd Step Definitions

### `tests/conftest.py` (공통 fixture)

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from inventory.models import Base, ProductTable


@pytest.fixture()
def in_memory_engine():
    """BDD 테스트용 SQLite in-memory 엔진."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture()
def db_session(in_memory_engine):
    """각 테스트마다 독립된 DB 세션 제공. 테스트 후 롤백."""
    connection = in_memory_engine.connect()
    transaction = connection.begin()
    session_factory = sessionmaker(bind=connection)
    session = session_factory()

    yield session

    session.close()
    transaction.rollback()
    connection.close()
```

### `tests/step_defs/conftest.py` (step_defs 전용 fixture)

```python
import pytest
from pytest_bdd import given, parsers

from inventory.models import Product, ProductTable
from inventory.repository import InventoryRepository
from inventory.service import InventoryService


@pytest.fixture()
def inventory_repo(db_session):
    return InventoryRepository(db_session)


@pytest.fixture()
def inventory_service(inventory_repo):
    return InventoryService(inventory_repo)


@pytest.fixture()
def context():
    """테스트 step 간 상태 공유용 딕셔너리."""
    return {}


@given(
    parsers.parse("데이터베이스에 다음 상품이 존재한다"),
    target_fixture="seed_products",
)
def seed_products(db_session, datatable):
    """Gherkin DataTable을 파싱하여 DB에 상품 데이터 삽입."""
    products = []
    for row in datatable:
        product = ProductTable(
            id=int(row["id"]),
            name=row["name"],
            stock=int(row["stock"]),
            price=float(row["price"]),
        )
        db_session.add(product)
        products.append(product)
    db_session.flush()
    return products


@given(
    parsers.parse("데이터베이스의 모든 상품 재고가 {stock:d}으로 설정된다"),
)
def update_all_stock(db_session, stock):
    rows = db_session.query(ProductTable).all()
    for row in rows:
        row.stock = stock
    db_session.flush()
```

> **참고**: pytest-bdd는 기본적으로 Gherkin DataTable을 직접 지원하지 않는다. DataTable 파싱을 위해 아래 `conftest.py` 플러그인을 프로젝트 루트의 `conftest.py`에 추가하거나, `pytest-bdd`의 최신 버전에서 제공하는 DataTable 지원을 사용한다. 아래는 수동 파싱 방식의 대안이다.

#### DataTable 파싱 대안 (pytest-bdd DataTable 미지원 시)

pytest-bdd가 Gherkin DataTable을 직접 지원하지 않는 경우, step 내에서 직접 데이터를 정의하는 방식을 사용할 수 있다.

```python
# 대안: DataTable 대신 step 내부에서 직접 데이터 시딩
@given("데이터베이스에 기본 상품이 존재한다", target_fixture="seed_products")
def seed_default_products(db_session):
    """DataTable 대신 fixture 내부에서 직접 데이터 삽입."""
    test_products = [
        ProductTable(id=1, name="키보드", stock=10, price=50000),
        ProductTable(id=2, name="마우스", stock=3, price=25000),
        ProductTable(id=3, name="모니터", stock=0, price=350000),
    ]
    for p in test_products:
        db_session.add(p)
    db_session.flush()
    return test_products
```

### `tests/step_defs/test_stock_management.py`

```python
import pytest
from pytest_bdd import given, parsers, scenario, then, when

from inventory.service import InventoryService


# --- Scenario 연결 ---

@scenario("../features/stock_management.feature", "재고 출고 - 정상 처리")
def test_remove_stock_success():
    pass


@scenario("../features/stock_management.feature", "재고 출고 - 재고 부족 에러")
def test_remove_stock_insufficient():
    pass


@scenario("../features/stock_management.feature", "재고 출고 - 전량 출고")
def test_remove_stock_all():
    pass


@scenario("../features/stock_management.feature", "재고 입고 - 정상 처리")
def test_add_stock_success():
    pass


@scenario("../features/stock_management.feature", "재고 입고 - 재고 0인 상품에 입고")
def test_add_stock_zero_initial():
    pass


@scenario("../features/stock_management.feature", "잘못된 수량으로 출고 시도")
def test_remove_stock_invalid_quantity():
    pass


@scenario("../features/stock_management.feature", "잘못된 수량으로 입고 시도")
def test_add_stock_invalid_quantity():
    pass


@scenario("../features/stock_management.feature", "존재하지 않는 상품 출고 시도")
def test_remove_stock_not_found():
    pass


# --- When Steps ---

@when(
    parsers.parse("상품 {product_id:d}에서 {quantity:d}개를 출고한다"),
    target_fixture="result_product",
)
def remove_stock(inventory_service: InventoryService, product_id, quantity):
    return inventory_service.remove_stock(product_id, quantity)


@when(
    parsers.parse("상품 {product_id:d}에서 {quantity:d}개를 출고하면 에러가 발생한다"),
    target_fixture="error_raised",
)
def remove_stock_with_error(
    inventory_service: InventoryService, product_id, quantity, context
):
    with pytest.raises(ValueError) as exc_info:
        inventory_service.remove_stock(product_id, quantity)
    context["error_message"] = str(exc_info.value)
    return exc_info


@when(
    parsers.parse("상품 {product_id:d}에 {quantity:d}개를 입고한다"),
    target_fixture="result_product",
)
def add_stock(inventory_service: InventoryService, product_id, quantity):
    return inventory_service.add_stock(product_id, quantity)


@when(
    parsers.parse("상품 {product_id:d}에 {quantity:d}개를 입고하면 에러가 발생한다"),
    target_fixture="error_raised",
)
def add_stock_with_error(
    inventory_service: InventoryService, product_id, quantity, context
):
    with pytest.raises(ValueError) as exc_info:
        inventory_service.add_stock(product_id, quantity)
    context["error_message"] = str(exc_info.value)
    return exc_info


# --- Then Steps ---

@then(parsers.parse("상품 {product_id:d}의 재고는 {expected:d}개이다"))
def verify_stock(inventory_service: InventoryService, product_id, expected):
    product = inventory_service.repo.find_by_id(product_id)
    assert product is not None, f"상품 {product_id}을 찾을 수 없습니다"
    assert product.stock == expected, (
        f"기대값: {expected}, 실제값: {product.stock}"
    )


@then(parsers.parse('에러 메시지에 "{message}"이 포함되어야 한다'))
def verify_error_message_eul(context, message):
    assert message in context["error_message"], (
        f'"{message}"가 에러 메시지에 없음: {context["error_message"]}'
    )


@then(parsers.parse('에러 메시지에 "{message}"가 포함되어야 한다'))
def verify_error_message_ga(context, message):
    assert message in context["error_message"], (
        f'"{message}"가 에러 메시지에 없음: {context["error_message"]}'
    )
```

### `tests/step_defs/test_stock_alerts.py`

```python
from pytest_bdd import parsers, scenario, then, when

from inventory.service import InventoryService


# --- Scenario 연결 ---

@scenario("../features/stock_alerts.feature", "기본 임계값(5)으로 재고 부족 상품 조회")
def test_default_threshold():
    pass


@scenario("../features/stock_alerts.feature", "커스텀 임계값으로 재고 부족 상품 조회")
def test_custom_threshold():
    pass


@scenario("../features/stock_alerts.feature", "임계값 0으로 조회하면 재고가 0인 상품만 반환")
def test_zero_threshold():
    pass


@scenario("../features/stock_alerts.feature", "모든 상품의 재고가 충분하면 빈 목록 반환")
def test_all_sufficient():
    pass


# --- When Steps ---

@when(
    "기본 임계값으로 재고 부족 상품을 조회한다",
    target_fixture="low_stock_products",
)
def get_low_stock_default(inventory_service: InventoryService):
    return inventory_service.get_low_stock_alerts()


@when(
    parsers.parse("임계값 {threshold:d}으로 재고 부족 상품을 조회한다"),
    target_fixture="low_stock_products",
)
def get_low_stock_custom(inventory_service: InventoryService, threshold):
    return inventory_service.get_low_stock_alerts(threshold)


# --- Then Steps ---

@then(parsers.parse("재고 부족 상품은 {count:d}개이다"))
def verify_low_stock_count(low_stock_products, count):
    assert len(low_stock_products) == count, (
        f"기대값: {count}개, 실제값: {len(low_stock_products)}개\n"
        f"상품 목록: {[p.name for p in low_stock_products]}"
    )


@then(parsers.parse('재고 부족 상품 목록에 "{name}"가 포함되어 있다'))
def verify_product_in_list_ga(low_stock_products, name):
    names = [p.name for p in low_stock_products]
    assert name in names, f'"{name}"이 목록에 없음: {names}'


@then(parsers.parse('재고 부족 상품 목록에 "{name}"이 포함되어 있다'))
def verify_product_in_list_i(low_stock_products, name):
    names = [p.name for p in low_stock_products]
    assert name in names, f'"{name}"가 목록에 없음: {names}'
```

### `tests/step_defs/test_stock_availability.py`

```python
from pytest_bdd import parsers, scenario, then, when

from inventory.service import InventoryService


# --- Scenario 연결 ---

@scenario("../features/stock_availability.feature", "재고가 충분한 경우")
def test_sufficient_stock():
    pass


@scenario("../features/stock_availability.feature", "재고와 정확히 같은 수량 요청")
def test_exact_stock():
    pass


@scenario("../features/stock_availability.feature", "재고보다 많은 수량 요청")
def test_insufficient_stock():
    pass


@scenario("../features/stock_availability.feature", "재고가 0인 상품의 가용성 확인")
def test_zero_stock():
    pass


@scenario("../features/stock_availability.feature", "존재하지 않는 상품의 가용성 확인")
def test_nonexistent_product():
    pass


# --- When Steps ---

@when(
    parsers.parse("상품 {product_id:d}의 {quantity:d}개 가용성을 확인한다"),
    target_fixture="availability_result",
)
def check_availability(inventory_service: InventoryService, product_id, quantity):
    return inventory_service.check_availability(product_id, quantity)


# --- Then Steps ---

@then(parsers.parse("가용 여부는 {expected}이다"))
def verify_availability(availability_result, expected):
    expected_bool = expected == "True"
    assert availability_result == expected_bool, (
        f"기대값: {expected_bool}, 실제값: {availability_result}"
    )
```

---

## 4. testcontainers DB 통합 테스트

### `tests/integration/test_repository_db.py`

```python
"""
testcontainers를 사용한 PostgreSQL DB 통합 테스트.

실제 PostgreSQL 컨테이너에서 InventoryRepository의 CRUD 동작을 검증한다.
Docker가 실행 중이어야 한다.
"""

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker
from testcontainers.postgres import PostgresContainer

from inventory.models import Base, Product, ProductTable
from inventory.repository import InventoryRepository


@pytest.fixture(scope="module")
def postgres_container():
    """모듈 단위로 PostgreSQL 컨테이너를 시작하고 종료한다."""
    with PostgresContainer("postgres:16-alpine") as postgres:
        yield postgres


@pytest.fixture(scope="module")
def engine(postgres_container):
    """PostgreSQL 컨테이너에 연결하는 SQLAlchemy 엔진."""
    engine = create_engine(postgres_container.get_connection_url())
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture()
def db_session(engine):
    """
    각 테스트 함수마다 트랜잭션으로 감싸서 격리된 세션 제공.
    테스트 종료 시 롤백하여 데이터가 누적되지 않는다.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session_factory = sessionmaker(bind=connection)
    session = session_factory()

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def repo(db_session):
    return InventoryRepository(db_session)


@pytest.fixture()
def sample_product(db_session) -> ProductTable:
    """테스트용 기본 상품 1건 삽입."""
    product = ProductTable(id=1, name="테스트 키보드", stock=10, price=50000.0)
    db_session.add(product)
    db_session.flush()
    return product


@pytest.fixture()
def multiple_products(db_session) -> list[ProductTable]:
    """다양한 재고 수준의 상품 여러 건 삽입."""
    products = [
        ProductTable(id=1, name="키보드", stock=10, price=50000.0),
        ProductTable(id=2, name="마우스", stock=3, price=25000.0),
        ProductTable(id=3, name="모니터", stock=0, price=350000.0),
        ProductTable(id=4, name="헤드셋", stock=5, price=80000.0),
        ProductTable(id=5, name="웹캠", stock=15, price=45000.0),
    ]
    for p in products:
        db_session.add(p)
    db_session.flush()
    return products


# ============================================================
# find_by_id 테스트
# ============================================================

class TestFindById:
    def test_existing_product(self, repo, sample_product):
        """존재하는 상품을 ID로 조회하면 Product 객체를 반환한다."""
        result = repo.find_by_id(1)

        assert result is not None
        assert isinstance(result, Product)
        assert result.id == 1
        assert result.name == "테스트 키보드"
        assert result.stock == 10
        assert result.price == 50000.0

    def test_nonexistent_product(self, repo):
        """존재하지 않는 ID로 조회하면 None을 반환한다."""
        result = repo.find_by_id(999)
        assert result is None

    def test_returns_domain_object_not_orm_entity(self, repo, sample_product):
        """반환값은 ORM 엔티티가 아닌 도메인 Product dataclass이다."""
        result = repo.find_by_id(1)
        assert isinstance(result, Product)
        assert not isinstance(result, ProductTable)


# ============================================================
# save 테스트
# ============================================================

class TestSave:
    def test_save_updates_existing_product(self, repo, sample_product):
        """기존 상품의 필드를 수정하고 저장하면 DB에 반영된다."""
        product = Product(id=1, name="테스트 키보드", stock=20, price=55000.0)

        saved = repo.save(product)

        assert saved.stock == 20
        assert saved.price == 55000.0

        # DB에서 다시 조회하여 확인
        reloaded = repo.find_by_id(1)
        assert reloaded.stock == 20
        assert reloaded.price == 55000.0

    def test_save_new_product(self, repo, db_session):
        """새 상품을 저장하면 DB에 삽입된다."""
        new_product = Product(id=100, name="새 상품", stock=50, price=10000.0)

        saved = repo.save(new_product)

        assert saved.id == 100
        assert saved.name == "새 상품"

        reloaded = repo.find_by_id(100)
        assert reloaded is not None
        assert reloaded.name == "새 상품"

    def test_save_returns_product_domain_object(self, repo, sample_product):
        """save 메서드는 도메인 Product 객체를 반환한다."""
        product = Product(id=1, name="테스트 키보드", stock=10, price=50000.0)
        result = repo.save(product)
        assert isinstance(result, Product)

    def test_save_stock_to_zero(self, repo, sample_product):
        """재고를 0으로 저장해도 정상 동작한다."""
        product = Product(id=1, name="테스트 키보드", stock=0, price=50000.0)

        saved = repo.save(product)
        assert saved.stock == 0

        reloaded = repo.find_by_id(1)
        assert reloaded.stock == 0


# ============================================================
# find_low_stock 테스트
# ============================================================

class TestFindLowStock:
    def test_default_threshold(self, repo, multiple_products):
        """기본 임계값(5) 이하인 상품만 반환한다."""
        results = repo.find_low_stock()

        assert len(results) == 3
        names = {p.name for p in results}
        assert names == {"마우스", "모니터", "헤드셋"}

    def test_custom_threshold(self, repo, multiple_products):
        """커스텀 임계값 이하인 상품만 반환한다."""
        results = repo.find_low_stock(threshold=10)

        assert len(results) == 4
        names = {p.name for p in results}
        assert "웹캠" not in names  # stock=15, 임계값 10 초과

    def test_zero_threshold(self, repo, multiple_products):
        """임계값 0이면 재고가 0인 상품만 반환한다."""
        results = repo.find_low_stock(threshold=0)

        assert len(results) == 1
        assert results[0].name == "모니터"

    def test_no_low_stock(self, repo, db_session):
        """모든 상품의 재고가 충분하면 빈 리스트를 반환한다."""
        product = ProductTable(id=1, name="충분한 상품", stock=100, price=10000.0)
        db_session.add(product)
        db_session.flush()

        results = repo.find_low_stock(threshold=5)
        assert results == []

    def test_empty_table(self, repo):
        """상품이 없으면 빈 리스트를 반환한다."""
        results = repo.find_low_stock()
        assert results == []

    def test_returns_list_of_domain_objects(self, repo, multiple_products):
        """반환 리스트의 각 원소는 도메인 Product dataclass이다."""
        results = repo.find_low_stock()
        for product in results:
            assert isinstance(product, Product)
            assert not isinstance(product, ProductTable)

    def test_threshold_boundary_inclusive(self, repo, multiple_products):
        """임계값과 정확히 같은 재고를 가진 상품도 포함된다 (<=)."""
        # 헤드셋: stock=5, threshold=5 -> 포함되어야 함
        results = repo.find_low_stock(threshold=5)
        names = {p.name for p in results}
        assert "헤드셋" in names


# ============================================================
# 트랜잭션 격리 검증
# ============================================================

class TestTransactionIsolation:
    def test_changes_are_rolled_back_between_tests_1(self, repo, db_session):
        """첫 번째 테스트에서 상품을 삽입한다."""
        product = ProductTable(id=999, name="격리 테스트 상품", stock=1, price=100.0)
        db_session.add(product)
        db_session.flush()

        result = repo.find_by_id(999)
        assert result is not None

    def test_changes_are_rolled_back_between_tests_2(self, repo):
        """이전 테스트에서 삽입한 상품이 롤백되어 존재하지 않는다."""
        result = repo.find_by_id(999)
        assert result is None, "이전 테스트의 데이터가 롤백되지 않았습니다"


# ============================================================
# 동시 조작 시나리오 (서비스 계층 연동)
# ============================================================

class TestServiceWithRealDB:
    """InventoryService를 실제 DB와 연결하여 통합 검증."""

    @pytest.fixture()
    def service(self, repo):
        from inventory.service import InventoryService
        return InventoryService(repo)

    def test_add_and_remove_stock_flow(self, service, sample_product):
        """입고 후 출고하는 전체 플로우가 정상 동작한다."""
        # 초기: 10개
        result = service.add_stock(1, 5)
        assert result.stock == 15

        result = service.remove_stock(1, 8)
        assert result.stock == 7

    def test_remove_stock_exceeds_raises_error(self, service, sample_product):
        """재고 이상 출고하면 ValueError가 발생한다."""
        with pytest.raises(ValueError, match="재고 부족"):
            service.remove_stock(1, 999)

    def test_add_stock_invalid_quantity_raises_error(self, service, sample_product):
        """0 이하 수량 입고 시 ValueError가 발생한다."""
        with pytest.raises(ValueError, match="수량은 0보다 커야 합니다"):
            service.add_stock(1, 0)

        with pytest.raises(ValueError, match="수량은 0보다 커야 합니다"):
            service.add_stock(1, -3)

    def test_low_stock_alert_after_removal(self, service, repo, sample_product):
        """출고 후 재고가 임계값 이하가 되면 알림 목록에 포함된다."""
        # 초기: 10개, 임계값: 5
        alerts = service.get_low_stock_alerts(threshold=5)
        assert len(alerts) == 0  # 10 > 5

        service.remove_stock(1, 7)  # 10 - 7 = 3
        alerts = service.get_low_stock_alerts(threshold=5)
        assert len(alerts) == 1
        assert alerts[0].stock == 3

    def test_check_availability_reflects_stock_changes(self, service, sample_product):
        """재고 변동이 가용성 확인에 즉시 반영된다."""
        assert service.check_availability(1, 10) is True

        service.remove_stock(1, 5)  # 10 -> 5
        assert service.check_availability(1, 10) is False
        assert service.check_availability(1, 5) is True
```

---

## 5. 의존성 및 실행 방법

### `requirements.txt`

```
pytest>=8.0
pytest-bdd>=7.0
sqlalchemy>=2.0
testcontainers[postgres]>=4.0
psycopg2-binary>=2.9
```

### 실행 명령어

```bash
# BDD 테스트 실행 (SQLite in-memory, Docker 불필요)
pytest tests/step_defs/ -v --tb=short

# DB 통합 테스트 실행 (Docker 필요)
pytest tests/integration/ -v --tb=short

# 전체 테스트 실행
pytest tests/ -v --tb=short

# 특정 feature 파일의 시나리오만 실행
pytest tests/step_defs/test_stock_management.py -v

# BDD 테스트 결과를 Gherkin 형식으로 출력
pytest tests/step_defs/ -v --gherkin-terminal-reporter
```

---

## 6. 설계 포인트 요약

| 항목 | 결정 | 근거 |
|------|------|------|
| BDD 엔진 | pytest-bdd | pytest 에코시스템과 자연스럽게 통합, fixture 재사용 가능 |
| BDD용 DB | SQLite in-memory | 빠른 실행, Docker 의존 없음, 단위 테스트에 적합 |
| 통합 테스트 DB | PostgreSQL via testcontainers | 실제 DB 드라이버/쿼리 동작 검증 |
| 테스트 격리 | 트랜잭션 롤백 | 각 테스트가 독립적으로 실행되며 데이터 오염 없음 |
| 컨테이너 scope | module | 컨테이너 시작 비용 최소화, 테스트 간 세션은 격리 |
| 도메인/ORM 분리 | Product (dataclass) vs ProductTable (ORM) | Repository가 ORM 의존을 캡슐화, 서비스 계층은 순수 도메인 객체만 사용 |
| Step 재사용 | conftest.py에 공통 Given step 배치 | 여러 feature 파일에서 동일한 Background 재사용 |
| 한국어 조사 처리 | "이/가" 별도 step 정의 | Gherkin 시나리오의 자연스러운 한국어 표현 지원 |

---

## 7. 핵심 테스트 시나리오 커버리지

### BDD 시나리오 (17개)

**재고 입출고 (`stock_management.feature`)** -- 8개
- 정상 출고 (10 - 3 = 7)
- 재고 부족 에러
- 전량 출고 (10 - 10 = 0)
- 정상 입고 (3 + 7 = 10)
- 재고 0 상품 입고 (0 + 5 = 5)
- 0개 출고 시도 -> ValueError
- 음수 입고 시도 -> ValueError
- 존재하지 않는 상품 출고 -> ValueError

**재고 부족 알림 (`stock_alerts.feature`)** -- 4개
- 기본 임계값(5) 조회
- 커스텀 임계값(10) 조회
- 임계값 0 조회 (재고 0인 상품만)
- 모든 재고 충분 시 빈 목록

**가용성 확인 (`stock_availability.feature`)** -- 5개
- 재고 충분
- 재고 == 요청 수량 (경계값)
- 재고 부족
- 재고 0
- 존재하지 않는 상품

### DB 통합 테스트 (16개)

**Repository CRUD**
- `find_by_id`: 존재하는 상품, 존재하지 않는 상품, 도메인 객체 타입 검증
- `save`: 기존 상품 수정, 신규 상품 삽입, 반환 타입 검증, 재고 0 저장
- `find_low_stock`: 기본 임계값, 커스텀 임계값, 임계값 0, 재고 충분, 빈 테이블, 도메인 객체 타입, 경계값 포함(<=)

**트랜잭션 격리**
- 테스트 간 데이터 롤백 검증 (2개 테스트 쌍)

**서비스 + DB 통합**
- 입고/출고 전체 플로우
- 재고 부족 에러
- 잘못된 수량 에러
- 출고 후 알림 목록 반영
- 재고 변동 후 가용성 즉시 반영
