# Refactoring: Legacy ERP Inventory Integration

## Context

레거시 ERP 시스템(Oracle DB)과 직접 결합된 재고 관리 코드를 리팩토링한다. 현재 코드는 ERP의 테이블명(`TB_INV_MASTER`), 컬럼명(`ZQTY_AVAIL`, `ZITEM_CD`)을 도메인 서비스에서 직접 사용하고 있어 ERP 변경 시 도메인 코드가 함께 깨지는 강결합 상태이다. 향후 ERP 교체 계획이 있으므로 ACL(Anti-Corruption Layer)을 통한 완전 격리가 필요하다.

### 적용 패턴

- **Anti-Corruption Layer (ACL)**: Facade + Adapter + Translator 조합으로 ERP를 격리
- **Hexagonal Architecture (Ports & Adapters)**: 도메인이 Port(인터페이스)를 소유하고, ERP 통합은 Driven Adapter로 구현
- **Repository Pattern**: ERP 조회를 컬렉션 추상화 뒤로 은닉

---

## Change 1: ERP 직접 호출을 Port 인터페이스로 추출

```
[Before]
```

```python
# inventory/services.py
import cx_Oracle

def get_stock(product_code: str) -> int:
    conn = cx_Oracle.connect("erp_user/pass@erp-db:1521/ERPDB")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT ZQTY_AVAIL FROM TB_INV_MASTER WHERE ZITEM_CD = :1",
        [product_code]
    )
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else 0


def reserve_stock(product_code: str, quantity: int) -> bool:
    conn = cx_Oracle.connect("erp_user/pass@erp-db:1521/ERPDB")
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE TB_INV_MASTER SET ZQTY_AVAIL = ZQTY_AVAIL - :1 "
        "WHERE ZITEM_CD = :2 AND ZQTY_AVAIL >= :1",
        [quantity, product_code]
    )
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0


def sync_product_info(product_code: str) -> dict:
    conn = cx_Oracle.connect("erp_user/pass@erp-db:1521/ERPDB")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT ZITEM_NM, ZITEM_GRP, ZUNIT_PRC FROM TB_ITEM_MASTER "
        "WHERE ZITEM_CD = :1",
        [product_code]
    )
    row = cursor.fetchone()
    conn.close()
    if not row:
        return {}
    return {"name": row[0], "category": row[1], "price": row[2]}
```

```
[After]
```

```python
# inventory/domain/models.py
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class ProductCode:
    value: str


@dataclass(frozen=True)
class Stock:
    product_code: ProductCode
    available_quantity: int

    def can_reserve(self, quantity: int) -> bool:
        return self.available_quantity >= quantity


@dataclass(frozen=True)
class ProductInfo:
    product_code: ProductCode
    name: str
    category: str
    price: Decimal
```

```python
# inventory/domain/ports.py
from abc import ABC, abstractmethod

from inventory.domain.models import ProductCode, ProductInfo, Stock


class InventoryPort(ABC):
    """Driven port: 재고 조회/변경을 위한 인터페이스.

    도메인 계층이 정의하고 소유한다.
    인프라 계층(ERP adapter)이 구현한다.
    """

    @abstractmethod
    def get_stock(self, product_code: ProductCode) -> Stock | None: ...

    @abstractmethod
    def reserve_stock(self, product_code: ProductCode, quantity: int) -> bool: ...


class ProductCatalogPort(ABC):
    """Driven port: 상품 정보 조회를 위한 인터페이스."""

    @abstractmethod
    def find_product(self, product_code: ProductCode) -> ProductInfo | None: ...
```

```python
# inventory/services.py
from inventory.domain.models import ProductCode, ProductInfo, Stock
from inventory.domain.ports import InventoryPort, ProductCatalogPort


class InventoryService:
    def __init__(
        self,
        inventory_port: InventoryPort,
        catalog_port: ProductCatalogPort,
    ) -> None:
        self._inventory = inventory_port
        self._catalog = catalog_port

    def get_stock(self, product_code: str) -> int:
        code = ProductCode(product_code)
        stock = self._inventory.get_stock(code)
        return stock.available_quantity if stock else 0

    def reserve_stock(self, product_code: str, quantity: int) -> bool:
        code = ProductCode(product_code)
        return self._inventory.reserve_stock(code, quantity)

    def sync_product_info(self, product_code: str) -> dict:
        code = ProductCode(product_code)
        product = self._catalog.find_product(code)
        if not product:
            return {}
        return {
            "name": product.name,
            "category": product.category,
            "price": product.price,
        }
```

```
[Reason] Hexagonal Architecture (Ports & Adapters) + DIP (Ownership Inversion)
-- 도메인 서비스가 cx_Oracle, ERP 테이블명, 컬럼명에 직접 의존하고 있었다.
   도메인 계층이 Port(InventoryPort, ProductCatalogPort)를 정의하고 소유함으로써
   의존성 방향을 역전시켰다. 도메인 코드는 더 이상 인프라를 import하지 않으며,
   ERP가 어떤 DB를 사용하는지, 테이블 구조가 어떤지 전혀 알지 못한다.
   도메인 모델(Stock, ProductInfo, ProductCode)을 도입하여 ERP의 암호화된
   컬럼명(ZQTY_AVAIL, ZITEM_CD)을 우리 도메인 언어로 치환했다.
```

---

## Change 2: ACL을 통한 ERP 격리 -- Adapter + Translator 구현

```
[Before]
```

ERP 격리 계층이 존재하지 않는다. 도메인 서비스가 ERP의 테이블 구조, 컬럼명, 접속 정보를 직접 알고 있다. ERP가 변경되면 `inventory/services.py`를 수정해야 한다.

```
[After]
```

```python
# inventory/infrastructure/erp/translator.py
from decimal import Decimal

from inventory.domain.models import ProductCode, ProductInfo, Stock


class ErpInventoryTranslator:
    """Translator: ERP 도메인 개념을 우리 도메인 개념으로 매핑.

    ERP의 컬럼명/데이터 형식과 우리 도메인 모델 간의 변환을
    이 한 곳에서 집중 관리한다.
    """

    @staticmethod
    def to_stock(product_code: str, row: tuple | None) -> Stock | None:
        if row is None:
            return None
        # ERP 컬럼 순서: ZQTY_AVAIL
        return Stock(
            product_code=ProductCode(product_code),
            available_quantity=int(row[0]),
        )

    @staticmethod
    def to_product_info(product_code: str, row: tuple | None) -> ProductInfo | None:
        if row is None:
            return None
        # ERP 컬럼 순서: ZITEM_NM, ZITEM_GRP, ZUNIT_PRC
        return ProductInfo(
            product_code=ProductCode(product_code),
            name=row[0],
            category=row[1],
            price=Decimal(str(row[2])),
        )
```

```python
# inventory/infrastructure/erp/connection.py
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Generator

import cx_Oracle


@dataclass(frozen=True)
class ErpConnectionConfig:
    user: str
    password: str
    host: str
    port: int
    service_name: str

    @property
    def dsn(self) -> str:
        return f"{self.user}/{self.password}@{self.host}:{self.port}/{self.service_name}"


class ErpConnectionFactory:
    """Facade: ERP 접속의 복잡성을 단순화."""

    def __init__(self, config: ErpConnectionConfig) -> None:
        self._config = config

    @contextmanager
    def connect(self) -> Generator[cx_Oracle.Connection, None, None]:
        conn = cx_Oracle.connect(self._config.dsn)
        try:
            yield conn
        finally:
            conn.close()
```

```python
# inventory/infrastructure/erp/adapter.py
from inventory.domain.models import ProductCode, ProductInfo, Stock
from inventory.domain.ports import InventoryPort, ProductCatalogPort
from inventory.infrastructure.erp.connection import ErpConnectionFactory
from inventory.infrastructure.erp.translator import ErpInventoryTranslator


class ErpInventoryAdapter(InventoryPort):
    """Driven Adapter: ERP DB를 통한 InventoryPort 구현.

    ACL 역할: ERP의 테이블/컬럼 구조(TB_INV_MASTER, ZQTY_AVAIL 등)를
    이 어댑터 안에 캡슐화하여 도메인을 오염으로부터 보호한다.
    """

    # ERP 테이블/컬럼명을 상수로 관리 -- ERP 스키마 변경 시 이곳만 수정
    _TABLE = "TB_INV_MASTER"
    _COL_ITEM_CODE = "ZITEM_CD"
    _COL_AVAILABLE_QTY = "ZQTY_AVAIL"

    def __init__(
        self,
        connection_factory: ErpConnectionFactory,
        translator: ErpInventoryTranslator,
    ) -> None:
        self._connection_factory = connection_factory
        self._translator = translator

    def get_stock(self, product_code: ProductCode) -> Stock | None:
        with self._connection_factory.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT {self._COL_AVAILABLE_QTY} FROM {self._TABLE} "
                f"WHERE {self._COL_ITEM_CODE} = :1",
                [product_code.value],
            )
            row = cursor.fetchone()
        return self._translator.to_stock(product_code.value, row)

    def reserve_stock(self, product_code: ProductCode, quantity: int) -> bool:
        with self._connection_factory.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE {self._TABLE} SET {self._COL_AVAILABLE_QTY} = "
                f"{self._COL_AVAILABLE_QTY} - :1 "
                f"WHERE {self._COL_ITEM_CODE} = :2 AND {self._COL_AVAILABLE_QTY} >= :1",
                [quantity, product_code.value],
            )
            affected = cursor.rowcount
            conn.commit()
        return affected > 0


class ErpProductCatalogAdapter(ProductCatalogPort):
    """Driven Adapter: ERP DB를 통한 ProductCatalogPort 구현."""

    _TABLE = "TB_ITEM_MASTER"
    _COL_ITEM_CODE = "ZITEM_CD"
    _COL_ITEM_NAME = "ZITEM_NM"
    _COL_ITEM_GROUP = "ZITEM_GRP"
    _COL_UNIT_PRICE = "ZUNIT_PRC"

    def __init__(
        self,
        connection_factory: ErpConnectionFactory,
        translator: ErpInventoryTranslator,
    ) -> None:
        self._connection_factory = connection_factory
        self._translator = translator

    def find_product(self, product_code: ProductCode) -> ProductInfo | None:
        with self._connection_factory.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT {self._COL_ITEM_NAME}, {self._COL_ITEM_GROUP}, "
                f"{self._COL_UNIT_PRICE} FROM {self._TABLE} "
                f"WHERE {self._COL_ITEM_CODE} = :1",
                [product_code.value],
            )
            row = cursor.fetchone()
        return self._translator.to_product_info(product_code.value, row)
```

```
[Reason] Anti-Corruption Layer (Facade + Adapter + Translator)
-- Evans의 ACL 3요소를 구현했다.
   (1) Facade(ErpConnectionFactory): ERP 접속 복잡성을 단순화하고 접속 문자열이
       코드 전체에 하드코딩되던 문제를 해결한다.
   (2) Adapter(ErpInventoryAdapter, ErpProductCatalogAdapter): ERP의 인터페이스를
       도메인 Port의 인터페이스로 변환한다. ERP의 테이블명, 컬럼명이 어댑터
       내부 상수로 캡슐화되어 ERP 스키마 변경 시 이곳만 수정하면 된다.
   (3) Translator(ErpInventoryTranslator): ERP의 row 데이터(ZQTY_AVAIL, ZITEM_NM 등)를
       도메인 객체(Stock, ProductInfo)로 변환한다. 데이터 형식 변환(int, Decimal)도
       이곳에서 처리한다.
   도메인 코드는 ERP가 Oracle인지, REST API인지, 파일인지 전혀 모른다.
```

---

## Change 3: ERP 교체 대비 -- 새 ERP Adapter 교체 경로 확보

```
[Before]
```

ERP 교체 시 `inventory/services.py`의 모든 SQL과 cx_Oracle 호출을 찾아 수정해야 한다. 코드 곳곳에 ERP 스키마 지식이 퍼져 있어 교체 범위를 파악할 수 없다.

```
[After]
```

```python
# inventory/infrastructure/new_erp/adapter.py
import httpx

from inventory.domain.models import ProductCode, ProductInfo, Stock
from inventory.domain.ports import InventoryPort, ProductCatalogPort


class NewErpInventoryAdapter(InventoryPort):
    """새 ERP(REST API 기반)로 교체 시 이 어댑터만 추가하면 된다.

    도메인 코드(services.py, models.py, ports.py)는 일절 수정하지 않는다.
    """

    def __init__(self, base_url: str, api_key: str) -> None:
        self._base_url = base_url
        self._api_key = api_key

    def get_stock(self, product_code: ProductCode) -> Stock | None:
        response = httpx.get(
            f"{self._base_url}/inventory/{product_code.value}",
            headers={"Authorization": f"Bearer {self._api_key}"},
        )
        if response.status_code == 404:
            return None
        data = response.json()
        return Stock(
            product_code=product_code,
            available_quantity=data["availableQuantity"],
        )

    def reserve_stock(self, product_code: ProductCode, quantity: int) -> bool:
        response = httpx.post(
            f"{self._base_url}/inventory/{product_code.value}/reserve",
            headers={"Authorization": f"Bearer {self._api_key}"},
            json={"quantity": quantity},
        )
        return response.status_code == 200


class NewErpProductCatalogAdapter(ProductCatalogPort):
    # 동일한 패턴으로 구현 -- 생략
    ...
```

```python
# inventory/bootstrap.py
from inventory.domain.ports import InventoryPort, ProductCatalogPort
from inventory.infrastructure.erp.adapter import (
    ErpInventoryAdapter,
    ErpProductCatalogAdapter,
)
from inventory.infrastructure.erp.connection import (
    ErpConnectionConfig,
    ErpConnectionFactory,
)
from inventory.infrastructure.erp.translator import ErpInventoryTranslator
from inventory.services import InventoryService


def create_inventory_service() -> InventoryService:
    """Composition Root: 의존성 조립.

    ERP 교체 시 이 함수에서 어댑터만 교체하면 된다.
    도메인 코드와 서비스 코드는 수정하지 않는다.
    """
    config = ErpConnectionConfig(
        user="erp_user",
        password="pass",         # 실제로는 환경변수/시크릿 관리자에서 로드
        host="erp-db",
        port=1521,
        service_name="ERPDB",
    )
    connection_factory = ErpConnectionFactory(config)
    translator = ErpInventoryTranslator()

    inventory_port: InventoryPort = ErpInventoryAdapter(connection_factory, translator)
    catalog_port: ProductCatalogPort = ErpProductCatalogAdapter(connection_factory, translator)

    # ERP 교체 시:
    # inventory_port = NewErpInventoryAdapter(base_url="...", api_key="...")
    # catalog_port = NewErpProductCatalogAdapter(base_url="...", api_key="...")

    return InventoryService(
        inventory_port=inventory_port,
        catalog_port=catalog_port,
    )
```

```
[Reason] Hexagonal Architecture -- Adapter 교체 가능성 확보
-- Hexagonal Architecture의 핵심 목표는 "외부 교체 가능성"이다. Port(인터페이스)를
   도메인이 소유하고, 각 외부 시스템을 Adapter로 구현하면, 같은 Port에 대해
   여러 Adapter를 만들 수 있다. ERP 교체 시 NewErpInventoryAdapter를 작성하고
   Composition Root(bootstrap.py)에서 주입 대상만 바꾸면 된다.
   도메인 코드(models.py, ports.py)와 애플리케이션 서비스(services.py)는
   일절 수정하지 않는다. 이것이 Evans가 말한 "레거시 마이그레이션 완료 후
   ACL을 폐기할 수 있다"의 구체적 실현이다.
```

---

## Change 4: 커넥션 하드코딩 제거 + 리소스 누수 방지

```
[Before]
```

```python
conn = cx_Oracle.connect("erp_user/pass@erp-db:1521/ERPDB")
cursor = conn.cursor()
cursor.execute(...)
row = cursor.fetchone()
conn.close()  # 예외 발생 시 close()에 도달하지 못함 -- 리소스 누수
return row[0] if row else 0
```

- 접속 문자열이 3개 함수에 하드코딩 (비밀번호 포함)
- 예외 발생 시 `conn.close()`에 도달하지 못하여 커넥션 누수
- 각 함수마다 커넥션 생성/해제를 반복

```
[After]
```

```python
# ErpConnectionFactory.connect() -- contextmanager로 안전한 리소스 관리
@contextmanager
def connect(self) -> Generator[cx_Oracle.Connection, None, None]:
    conn = cx_Oracle.connect(self._config.dsn)
    try:
        yield conn
    finally:
        conn.close()  # 예외 발생 여부와 관계없이 항상 실행


# Adapter에서의 사용
def get_stock(self, product_code: ProductCode) -> Stock | None:
    with self._connection_factory.connect() as conn:  # 안전한 리소스 관리
        cursor = conn.cursor()
        cursor.execute(...)
        row = cursor.fetchone()
    # with 블록을 벗어나면 자동으로 conn.close() 호출
    return self._translator.to_stock(product_code.value, row)
```

```
[Reason] Infrastructure Adapter 내부 품질 개선
-- 접속 정보를 ErpConnectionConfig로 추출하여 하드코딩을 제거했다.
   contextmanager를 사용하여 예외 발생 시에도 커넥션이 반드시 정리된다.
   커넥션 생성 로직이 ErpConnectionFactory 한 곳에 집중되어,
   커넥션 풀링 등 향후 개선도 이곳에서만 처리하면 된다.
```

---

## Change 5: 테스트 용이성 확보 -- Fake Adapter

```
[Before]
```

테스트 시 실제 Oracle DB에 접속해야 한다. 단위 테스트가 불가능하고, CI 환경 구성이 어렵다.

```
[After]
```

```python
# tests/fakes.py
from inventory.domain.models import ProductCode, ProductInfo, Stock
from inventory.domain.ports import InventoryPort, ProductCatalogPort


class FakeInventoryAdapter(InventoryPort):
    def __init__(self) -> None:
        self._stocks: dict[str, int] = {}

    def set_stock(self, product_code: str, quantity: int) -> None:
        """테스트 셋업용."""
        self._stocks[product_code] = quantity

    def get_stock(self, product_code: ProductCode) -> Stock | None:
        qty = self._stocks.get(product_code.value)
        if qty is None:
            return None
        return Stock(product_code=product_code, available_quantity=qty)

    def reserve_stock(self, product_code: ProductCode, quantity: int) -> bool:
        current = self._stocks.get(product_code.value, 0)
        if current < quantity:
            return False
        self._stocks[product_code.value] = current - quantity
        return True


class FakeProductCatalogAdapter(ProductCatalogPort):
    def __init__(self) -> None:
        self._products: dict[str, ProductInfo] = {}

    def add_product(self, product: ProductInfo) -> None:
        """테스트 셋업용."""
        self._products[product.product_code.value] = product

    def find_product(self, product_code: ProductCode) -> ProductInfo | None:
        return self._products.get(product_code.value)
```

```python
# tests/test_inventory_service.py
from decimal import Decimal

from inventory.domain.models import ProductCode, ProductInfo
from inventory.services import InventoryService
from tests.fakes import FakeInventoryAdapter, FakeProductCatalogAdapter


class TestInventoryService:
    def setup_method(self) -> None:
        self.inventory_adapter = FakeInventoryAdapter()
        self.catalog_adapter = FakeProductCatalogAdapter()
        self.service = InventoryService(
            inventory_port=self.inventory_adapter,
            catalog_port=self.catalog_adapter,
        )

    def test_get_stock_returns_available_quantity(self) -> None:
        self.inventory_adapter.set_stock("PROD-001", 100)
        assert self.service.get_stock("PROD-001") == 100

    def test_get_stock_returns_zero_when_not_found(self) -> None:
        assert self.service.get_stock("UNKNOWN") == 0

    def test_reserve_stock_succeeds(self) -> None:
        self.inventory_adapter.set_stock("PROD-001", 100)
        assert self.service.reserve_stock("PROD-001", 30) is True
        assert self.service.get_stock("PROD-001") == 70

    def test_reserve_stock_fails_when_insufficient(self) -> None:
        self.inventory_adapter.set_stock("PROD-001", 10)
        assert self.service.reserve_stock("PROD-001", 20) is False

    def test_sync_product_info(self) -> None:
        self.catalog_adapter.add_product(
            ProductInfo(
                product_code=ProductCode("PROD-001"),
                name="Test Product",
                category="Electronics",
                price=Decimal("29900"),
            )
        )
        result = self.service.sync_product_info("PROD-001")
        assert result["name"] == "Test Product"
        assert result["category"] == "Electronics"
```

```
[Reason] Hexagonal Architecture -- Driven Adapter 교체에 의한 테스트 용이성
-- Hexagonal Architecture의 핵심 동기 중 하나가 "DB 없이 자동화 테스트를
   실행할 수 있게 하라"(Cockburn)이다. Port(인터페이스)를 도메인이 소유하므로,
   테스트 시 FakeInventoryAdapter를 주입하면 Oracle DB 없이 서비스 로직을
   빠르게 검증할 수 있다. 이는 Persistence 패턴의 Repository에서도 같은
   원리이다(Cosmic Python의 FakeBatchRepository 패턴).
```

---

## Final Structure

```
inventory/
  domain/
    models.py              # Stock, ProductInfo, ProductCode (도메인 모델)
    ports.py               # InventoryPort, ProductCatalogPort (도메인이 소유하는 인터페이스)
  infrastructure/
    erp/
      connection.py        # ErpConnectionConfig, ErpConnectionFactory (Facade)
      translator.py        # ErpInventoryTranslator (Translator)
      adapter.py           # ErpInventoryAdapter, ErpProductCatalogAdapter (Adapter)
    new_erp/
      adapter.py           # NewErpInventoryAdapter (교체용 Adapter)
  services.py              # InventoryService (애플리케이션 서비스)
  bootstrap.py             # Composition Root (의존성 조립)
tests/
  fakes.py                 # FakeInventoryAdapter, FakeProductCatalogAdapter
  test_inventory_service.py
```

## Checklist

- [x] Infrastructure dependency in domain --> EXTRACT port interface + adapter
- [x] Direct external system call --> WRAP with ACL (Facade + Adapter + Translator)
- [x] DB logic in domain --> MOVE to adapter
- [ ] Monolithic read/write model --> SPLIT with CQRS: 현재 복잡도에서는 불필요. 재고 조회와 변경이 동일 모델로 충분히 처리 가능.
- [ ] Domain event exposed externally --> N/A: 현재 이벤트 발행 없음
- [ ] Scattered transaction management --> CONSOLIDATE with Unit of Work: 현재 각 작업이 단일 SQL로 완결되므로 UoW 도입은 과설계. 복수 aggregate 변경이 필요해지면 도입한다.
