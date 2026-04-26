# 재고 관리 시스템 BDD 테스트 및 DB 통합 테스트

## 프로젝트 구조

```
inventory/
    __init__.py
    models.py
    repository.py
    service.py
tests/
    features/
        inventory.feature
    conftest.py
    test_inventory_bdd.py
    test_inventory_integration.py
```

## 의존성

```
pip install pytest pytest-bdd testcontainers[postgres] sqlalchemy psycopg2-binary
```

---

## 1. 프로덕션 코드 (SQLAlchemy 모델 포함)

### `inventory/models.py`

```python
from dataclasses import dataclass

import sqlalchemy as sa
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class ProductModel(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    stock: Mapped[int] = mapped_column(default=0)
    price: Mapped[float] = mapped_column(sa.Numeric(10, 2), nullable=False)


@dataclass
class Product:
    id: int
    name: str
    stock: int
    price: float
```

### `inventory/repository.py`

```python
from sqlalchemy.orm import Session

from inventory.models import Product, ProductModel


class InventoryRepository:
    def __init__(self, session: Session):
        self.session = session

    def find_by_id(self, product_id: int) -> Product | None:
        row = self.session.get(ProductModel, product_id)
        if row is None:
            return None
        return Product(id=row.id, name=row.name, stock=row.stock, price=float(row.price))

    def save(self, product: Product) -> Product:
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
            row.name = product.name
            row.stock = product.stock
            row.price = product.price
        self.session.flush()
        return Product(id=row.id, name=row.name, stock=row.stock, price=float(row.price))

    def find_low_stock(self, threshold: int = 5) -> list[Product]:
        rows = (
            self.session.query(ProductModel)
            .filter(ProductModel.stock <= threshold)
            .all()
        )
        return [
            Product(id=r.id, name=r.name, stock=r.stock, price=float(r.price))
            for r in rows
        ]
```

### `inventory/service.py`

```python
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

## 2. BDD Feature 파일

### `tests/features/inventory.feature`

```gherkin
Feature: 재고 관리
    재고 담당자가 상품의 입출고를 관리하고
    재고 부족 상품을 모니터링할 수 있다.

    # --- 출고 시나리오 ---

    Scenario: 충분한 재고에서 출고
        Given 상품 "키보드"의 재고가 10개이고 가격이 50000원이다
        When 상품 "키보드"에서 3개를 출고한다
        Then 상품 "키보드"의 재고가 7개여야 한다

    Scenario: 재고 전량 출고
        Given 상품 "마우스"의 재고가 5개이고 가격이 30000원이다
        When 상품 "마우스"에서 5개를 출고한다
        Then 상품 "마우스"의 재고가 0개여야 한다

    Scenario: 재고 부족 시 출고 실패
        Given 상품 "모니터"의 재고가 2개이고 가격이 300000원이다
        When 상품 "모니터"에서 5개를 출고하면 에러가 발생한다
        Then "재고 부족" 에러 메시지가 반환된다

    # --- 입고 시나리오 ---

    Scenario: 기존 상품에 입고
        Given 상품 "키보드"의 재고가 10개이고 가격이 50000원이다
        When 상품 "키보드"에 5개를 입고한다
        Then 상품 "키보드"의 재고가 15개여야 한다

    Scenario: 0 이하 수량 입고 시 에러
        Given 상품 "마우스"의 재고가 5개이고 가격이 30000원이다
        When 상품 "마우스"에 0개를 입고하면 에러가 발생한다
        Then "수량은 0보다 커야 합니다" 에러 메시지가 반환된다

    # --- 재고 부족 알림 시나리오 ---

    Scenario: 임계값 이하 상품 조회
        Given 다음 상품들이 등록되어 있다:
            | name   | stock | price  |
            | 키보드 | 3     | 50000  |
            | 마우스 | 10    | 30000  |
            | 모니터 | 1     | 300000 |
            | 헤드셋 | 7     | 80000  |
        When 임계값 5로 재고 부족 상품을 조회한다
        Then 재고 부족 상품이 2개여야 한다
        And 재고 부족 상품에 "키보드"가 포함되어야 한다
        And 재고 부족 상품에 "모니터"가 포함되어야 한다

    # --- 가용성 확인 시나리오 ---

    Scenario: 재고가 충분할 때 가용성 확인
        Given 상품 "키보드"의 재고가 10개이고 가격이 50000원이다
        When 상품 "키보드"의 가용성을 3개로 확인한다
        Then 가용성 결과가 True여야 한다

    Scenario: 재고가 부족할 때 가용성 확인
        Given 상품 "마우스"의 재고가 2개이고 가격이 30000원이다
        When 상품 "마우스"의 가용성을 5개로 확인한다
        Then 가용성 결과가 False여야 한다
```

---

## 3. BDD 테스트 구현 (Fake Repository 사용)

BDD 테스트는 비즈니스 로직 검증이 목적이므로 Fake Repository를 사용하여 빠르고 독립적으로 실행한다.

### `tests/conftest.py`

```python
import pytest

from inventory.models import Product
from inventory.repository import InventoryRepository
from inventory.service import InventoryService


class FakeInventoryRepository:
    """메모리 기반 Fake Repository -- DB 없이 비즈니스 로직을 테스트한다."""

    def __init__(self):
        self._store: dict[int, Product] = {}
        self._next_id = 1

    def find_by_id(self, product_id: int) -> Product | None:
        return self._store.get(product_id)

    def save(self, product: Product) -> Product:
        if product.id == 0:
            product.id = self._next_id
            self._next_id += 1
        self._store[product.id] = product
        return product

    def find_low_stock(self, threshold: int = 5) -> list[Product]:
        return [p for p in self._store.values() if p.stock <= threshold]

    def add_product(self, name: str, stock: int, price: float) -> Product:
        product = Product(id=self._next_id, name=name, stock=stock, price=price)
        self._next_id += 1
        self._store[product.id] = product
        return product


@pytest.fixture
def fake_repo():
    return FakeInventoryRepository()


@pytest.fixture
def inventory_service(fake_repo):
    return InventoryService(repo=fake_repo)
```

### `tests/test_inventory_bdd.py`

```python
import pytest
from pytest_bdd import scenario, given, when, then, parsers

from inventory.models import Product


# --- Scenario 함수 ---

@scenario("features/inventory.feature", "충분한 재고에서 출고")
def test_remove_stock_with_sufficient_inventory():
    pass


@scenario("features/inventory.feature", "재고 전량 출고")
def test_remove_entire_stock():
    pass


@scenario("features/inventory.feature", "재고 부족 시 출고 실패")
def test_remove_stock_fails_on_insufficient_inventory():
    pass


@scenario("features/inventory.feature", "기존 상품에 입고")
def test_add_stock_to_existing_product():
    pass


@scenario("features/inventory.feature", "0 이하 수량 입고 시 에러")
def test_add_zero_stock_fails():
    pass


@scenario("features/inventory.feature", "임계값 이하 상품 조회")
def test_low_stock_alerts():
    pass


@scenario("features/inventory.feature", "재고가 충분할 때 가용성 확인")
def test_availability_when_sufficient():
    pass


@scenario("features/inventory.feature", "재고가 부족할 때 가용성 확인")
def test_availability_when_insufficient():
    pass


# --- Given 단계 ---

@given(
    parsers.parse('상품 "{name}"의 재고가 {stock:d}개이고 가격이 {price:d}원이다'),
    target_fixture="product",
)
def product_with_stock(fake_repo, name, stock, price):
    return fake_repo.add_product(name=name, stock=stock, price=float(price))


@given("다음 상품들이 등록되어 있다:", target_fixture="products")
def products_from_table(fake_repo, datatable):
    products = []
    for row in datatable:
        product = fake_repo.add_product(
            name=row["name"],
            stock=int(row["stock"]),
            price=float(row["price"]),
        )
        products.append(product)
    return products


# --- When 단계: 출고 ---

@when(
    parsers.parse('상품 "{name}"에서 {quantity:d}개를 출고한다'),
    target_fixture="action_result",
)
def remove_stock(inventory_service, fake_repo, name, quantity):
    product = _find_product_by_name(fake_repo, name)
    result = inventory_service.remove_stock(product.id, quantity)
    return {"product": result}


@when(
    parsers.parse('상품 "{name}"에서 {quantity:d}개를 출고하면 에러가 발생한다'),
    target_fixture="action_result",
)
def remove_stock_with_error(inventory_service, fake_repo, name, quantity):
    product = _find_product_by_name(fake_repo, name)
    try:
        inventory_service.remove_stock(product.id, quantity)
        return {"error": None}
    except ValueError as e:
        return {"error": str(e)}


# --- When 단계: 입고 ---

@when(
    parsers.parse('상품 "{name}"에 {quantity:d}개를 입고한다'),
    target_fixture="action_result",
)
def add_stock(inventory_service, fake_repo, name, quantity):
    product = _find_product_by_name(fake_repo, name)
    result = inventory_service.add_stock(product.id, quantity)
    return {"product": result}


@when(
    parsers.parse('상품 "{name}"에 {quantity:d}개를 입고하면 에러가 발생한다'),
    target_fixture="action_result",
)
def add_stock_with_error(inventory_service, fake_repo, name, quantity):
    product = _find_product_by_name(fake_repo, name)
    try:
        inventory_service.add_stock(product.id, quantity)
        return {"error": None}
    except ValueError as e:
        return {"error": str(e)}


# --- When 단계: 재고 부족 조회 ---

@when(
    parsers.parse("임계값 {threshold:d}로 재고 부족 상품을 조회한다"),
    target_fixture="low_stock_result",
)
def query_low_stock(inventory_service, threshold):
    return inventory_service.get_low_stock_alerts(threshold)


# --- When 단계: 가용성 확인 ---

@when(
    parsers.parse('상품 "{name}"의 가용성을 {quantity:d}개로 확인한다'),
    target_fixture="availability_result",
)
def check_availability(inventory_service, fake_repo, name, quantity):
    product = _find_product_by_name(fake_repo, name)
    return inventory_service.check_availability(product.id, quantity)


# --- Then 단계: 재고 검증 ---

@then(parsers.parse('상품 "{name}"의 재고가 {expected:d}개여야 한다'))
def verify_stock(fake_repo, name, expected):
    product = _find_product_by_name(fake_repo, name)
    assert product.stock == expected


# --- Then 단계: 에러 검증 ---

@then(parsers.parse('"{message}" 에러 메시지가 반환된다'))
def verify_error_message(action_result, message):
    assert action_result["error"] is not None
    assert message in action_result["error"]


# --- Then 단계: 재고 부족 알림 검증 ---

@then(parsers.parse("재고 부족 상품이 {count:d}개여야 한다"))
def verify_low_stock_count(low_stock_result, count):
    assert len(low_stock_result) == count


@then(parsers.parse('재고 부족 상품에 "{name}"가 포함되어야 한다'))
def verify_low_stock_contains(low_stock_result, name):
    names = [p.name for p in low_stock_result]
    assert name in names


# --- Then 단계: 가용성 검증 ---

@then(parsers.parse("가용성 결과가 {expected}여야 한다"))
def verify_availability(availability_result, expected):
    expected_bool = expected == "True"
    assert availability_result is expected_bool


# --- 헬퍼 ---

def _find_product_by_name(fake_repo, name: str) -> Product:
    for product in fake_repo._store.values():
        if product.name == name:
            return product
    raise ValueError(f"테스트 데이터에 '{name}' 상품이 없습니다")
```

---

## 4. DB 통합 테스트 (testcontainers + PostgreSQL)

통합 테스트는 실제 PostgreSQL 컨테이너를 사용하여 Repository 계층이 DB와 올바르게 상호작용하는지 검증한다. 세션 스코프로 컨테이너를 한 번만 시작하고, 각 테스트는 트랜잭션 롤백으로 격리한다.

### `tests/test_inventory_integration.py`

```python
import pytest
from testcontainers.postgres import PostgresContainer
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from inventory.models import Base, Product, ProductModel
from inventory.repository import InventoryRepository
from inventory.service import InventoryService


@pytest.fixture(scope="session")
def postgres_container():
    """세션 전체에서 PostgreSQL 컨테이너 1회 시작."""
    with PostgresContainer("postgres:16-alpine") as postgres:
        yield postgres


@pytest.fixture(scope="session")
def db_engine(postgres_container):
    """세션 스코프 엔진 -- 테이블 생성은 한 번만 수행한다."""
    engine = create_engine(postgres_container.get_connection_url())
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def db_session(db_engine):
    """각 테스트를 트랜잭션으로 감싸 격리한다."""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def repo(db_session):
    return InventoryRepository(db_session)


@pytest.fixture
def service(repo):
    return InventoryService(repo)


def _seed_product(db_session, name: str, stock: int, price: float) -> Product:
    """테스트 데이터 삽입 헬퍼."""
    row = ProductModel(name=name, stock=stock, price=price)
    db_session.add(row)
    db_session.flush()
    return Product(id=row.id, name=row.name, stock=row.stock, price=float(row.price))


# --- Repository 통합 테스트 ---


class TestInventoryRepositoryIntegration:

    def test_find_by_id_returns_existing_product(self, repo, db_session):
        product = _seed_product(db_session, "키보드", 10, 50000.0)

        found = repo.find_by_id(product.id)

        assert found is not None
        assert found.name == "키보드"
        assert found.stock == 10
        assert found.price == 50000.0

    def test_find_by_id_returns_none_for_missing(self, repo):
        found = repo.find_by_id(99999)

        assert found is None

    def test_save_updates_existing_product(self, repo, db_session):
        product = _seed_product(db_session, "마우스", 5, 30000.0)
        product.stock = 20

        saved = repo.save(product)

        assert saved.stock == 20
        reloaded = repo.find_by_id(product.id)
        assert reloaded.stock == 20

    def test_find_low_stock_returns_only_below_threshold(self, repo, db_session):
        _seed_product(db_session, "키보드", 3, 50000.0)
        _seed_product(db_session, "마우스", 10, 30000.0)
        _seed_product(db_session, "모니터", 1, 300000.0)

        low_stock = repo.find_low_stock(threshold=5)

        names = {p.name for p in low_stock}
        assert names == {"키보드", "모니터"}

    def test_find_low_stock_includes_exact_threshold(self, repo, db_session):
        _seed_product(db_session, "헤드셋", 5, 80000.0)

        low_stock = repo.find_low_stock(threshold=5)

        assert len(low_stock) == 1
        assert low_stock[0].name == "헤드셋"


# --- Service + DB 통합 테스트 ---


class TestInventoryServiceIntegration:

    def test_add_stock_persists_to_db(self, service, repo, db_session):
        product = _seed_product(db_session, "키보드", 10, 50000.0)

        result = service.add_stock(product.id, 5)

        assert result.stock == 15
        persisted = repo.find_by_id(product.id)
        assert persisted.stock == 15

    def test_remove_stock_persists_to_db(self, service, repo, db_session):
        product = _seed_product(db_session, "키보드", 10, 50000.0)

        result = service.remove_stock(product.id, 3)

        assert result.stock == 7
        persisted = repo.find_by_id(product.id)
        assert persisted.stock == 7

    def test_remove_stock_raises_on_insufficient_inventory(self, service, db_session):
        product = _seed_product(db_session, "모니터", 2, 300000.0)

        with pytest.raises(ValueError, match="재고 부족"):
            service.remove_stock(product.id, 5)

    def test_remove_stock_does_not_modify_db_on_failure(self, service, repo, db_session):
        """출고 실패 시 DB의 재고가 변경되지 않아야 한다."""
        product = _seed_product(db_session, "모니터", 2, 300000.0)

        with pytest.raises(ValueError):
            service.remove_stock(product.id, 5)

        persisted = repo.find_by_id(product.id)
        assert persisted.stock == 2

    def test_add_stock_raises_on_invalid_quantity(self, service, db_session):
        product = _seed_product(db_session, "마우스", 5, 30000.0)

        with pytest.raises(ValueError, match="수량은 0보다 커야 합니다"):
            service.add_stock(product.id, 0)

    def test_add_stock_raises_on_missing_product(self, service):
        with pytest.raises(ValueError, match="찾을 수 없습니다"):
            service.add_stock(99999, 5)

    def test_check_availability_true_when_sufficient(self, service, db_session):
        product = _seed_product(db_session, "키보드", 10, 50000.0)

        assert service.check_availability(product.id, 10) is True

    def test_check_availability_false_when_insufficient(self, service, db_session):
        product = _seed_product(db_session, "마우스", 2, 30000.0)

        assert service.check_availability(product.id, 5) is False

    def test_check_availability_false_for_missing_product(self, service):
        assert service.check_availability(99999, 1) is False

    def test_low_stock_alerts_integration(self, service, db_session):
        _seed_product(db_session, "키보드", 3, 50000.0)
        _seed_product(db_session, "마우스", 10, 30000.0)
        _seed_product(db_session, "모니터", 1, 300000.0)
        _seed_product(db_session, "헤드셋", 7, 80000.0)

        alerts = service.get_low_stock_alerts(threshold=5)

        names = {p.name for p in alerts}
        assert len(alerts) == 2
        assert names == {"키보드", "모니터"}
```

---

## 5. pytest 설정

### `pyproject.toml`

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
markers = [
    "integration: Docker 기반 통합 테스트 (testcontainers)",
]
strict_markers = true
strict_config = true
```

통합 테스트만 별도 실행하려면 마커를 추가하고 다음과 같이 실행한다:

```bash
# BDD 테스트만 실행
pytest tests/test_inventory_bdd.py -v

# DB 통합 테스트만 실행
pytest tests/test_inventory_integration.py -v

# 전체 실행
pytest tests/ -v
```

---

## 설계 결정 요약

| 결정 | 근거 |
|------|------|
| BDD에 Fake Repository 사용 | BDD는 비즈니스 행위를 검증하는 것이 목적이다. DB 의존성을 제거하여 Fast, Independent 원칙을 지킨다. |
| 통합 테스트에 실제 PostgreSQL 사용 | Repository 계층의 SQL 쿼리와 ORM 매핑이 실제 DB에서 올바르게 동작하는지 검증해야 한다. Mock이나 SQLite로는 PostgreSQL 고유 동작을 놓칠 수 있다. |
| 세션 스코프 컨테이너 + 트랜잭션 롤백 | 컨테이너 시작 비용은 세션에서 한 번만 부담하고, 각 테스트는 트랜잭션 롤백으로 격리하여 Independent 원칙을 보장한다. |
| `_seed_product` 헬퍼 | 각 통합 테스트가 자체 데이터를 생성하여 테스트 간 의존성을 제거한다. Excessive Setup 안티패턴을 피하면서도 독립성을 유지한다. |
| BDD step에서 `target_fixture` 활용 | Given/When 단계의 결과를 Then 단계에 자연스럽게 전달한다. 전역 상태 없이 pytest의 fixture 메커니즘으로 데이터를 공유한다. |
| 출력 기반 검증 우선 | `assert result.stock == 7` 처럼 반환값을 검증한다. Mock의 `assert_called` 같은 통신 기반 검증은 사용하지 않는다. |
