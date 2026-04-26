# Inventory ERP Integration Refactoring

## Before

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

## After

```python
# inventory/domain/models.py
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class ProductInfo:
    name: str
    category: str
    price: Decimal


@dataclass(frozen=True)
class Stock:
    product_code: str
    available_quantity: int

    def can_reserve(self, quantity: int) -> bool:
        return self.available_quantity >= quantity
```

```python
# inventory/domain/ports.py
from abc import ABC, abstractmethod
from inventory.domain.models import ProductInfo, Stock


class InventoryPort(ABC):
    """Port: 재고 시스템에 대한 추상 인터페이스"""

    @abstractmethod
    def get_stock(self, product_code: str) -> Stock | None:
        ...

    @abstractmethod
    def reserve_stock(self, product_code: str, quantity: int) -> bool:
        ...

    @abstractmethod
    def get_product_info(self, product_code: str) -> ProductInfo | None:
        ...
```

```python
# inventory/adapters/erp_oracle_adapter.py
import cx_Oracle
from contextlib import contextmanager
from inventory.domain.ports import InventoryPort
from inventory.domain.models import ProductInfo, Stock


class ErpOracleAdapter(InventoryPort):
    """Adapter: 레거시 Oracle ERP 시스템 구현체"""

    # ERP 테이블/컬럼 매핑 (ERP 변경 시 여기만 수정)
    _TABLE_INVENTORY = "TB_INV_MASTER"
    _COL_ITEM_CODE = "ZITEM_CD"
    _COL_QTY_AVAILABLE = "ZQTY_AVAIL"

    _TABLE_ITEM = "TB_ITEM_MASTER"
    _COL_ITEM_NAME = "ZITEM_NM"
    _COL_ITEM_GROUP = "ZITEM_GRP"
    _COL_UNIT_PRICE = "ZUNIT_PRC"

    def __init__(self, dsn: str):
        self._dsn = dsn

    @contextmanager
    def _connection(self):
        conn = cx_Oracle.connect(self._dsn)
        try:
            yield conn
        finally:
            conn.close()

    def get_stock(self, product_code: str) -> Stock | None:
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT {self._COL_QTY_AVAILABLE} "
                f"FROM {self._TABLE_INVENTORY} "
                f"WHERE {self._COL_ITEM_CODE} = :1",
                [product_code],
            )
            row = cursor.fetchone()
            if not row:
                return None
            return Stock(
                product_code=product_code,
                available_quantity=row[0],
            )

    def reserve_stock(self, product_code: str, quantity: int) -> bool:
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE {self._TABLE_INVENTORY} "
                f"SET {self._COL_QTY_AVAILABLE} = {self._COL_QTY_AVAILABLE} - :1 "
                f"WHERE {self._COL_ITEM_CODE} = :2 "
                f"AND {self._COL_QTY_AVAILABLE} >= :1",
                [quantity, product_code],
            )
            conn.commit()
            return cursor.rowcount > 0

    def get_product_info(self, product_code: str) -> ProductInfo | None:
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT {self._COL_ITEM_NAME}, {self._COL_ITEM_GROUP}, "
                f"{self._COL_UNIT_PRICE} "
                f"FROM {self._TABLE_ITEM} "
                f"WHERE {self._COL_ITEM_CODE} = :1",
                [product_code],
            )
            row = cursor.fetchone()
            if not row:
                return None
            return ProductInfo(
                name=row[0],
                category=row[1],
                price=row[2],
            )
```

```python
# inventory/adapters/new_erp_api_adapter.py
import httpx
from inventory.domain.ports import InventoryPort
from inventory.domain.models import ProductInfo, Stock


class NewErpApiAdapter(InventoryPort):
    """Adapter: 신규 ERP REST API 구현체 (향후 교체용)"""

    def __init__(self, base_url: str, api_key: str):
        self._base_url = base_url
        self._headers = {"Authorization": f"Bearer {api_key}"}

    def get_stock(self, product_code: str) -> Stock | None:
        resp = httpx.get(
            f"{self._base_url}/inventory/{product_code}",
            headers=self._headers,
        )
        if resp.status_code == 404:
            return None
        data = resp.json()
        return Stock(
            product_code=product_code,
            available_quantity=data["availableQuantity"],
        )

    def reserve_stock(self, product_code: str, quantity: int) -> bool:
        resp = httpx.post(
            f"{self._base_url}/inventory/{product_code}/reserve",
            headers=self._headers,
            json={"quantity": quantity},
        )
        return resp.status_code == 200

    def get_product_info(self, product_code: str) -> ProductInfo | None:
        resp = httpx.get(
            f"{self._base_url}/products/{product_code}",
            headers=self._headers,
        )
        if resp.status_code == 404:
            return None
        data = resp.json()
        return ProductInfo(
            name=data["name"],
            category=data["category"],
            price=data["price"],
        )
```

```python
# inventory/services.py
from inventory.domain.ports import InventoryPort
from inventory.domain.models import ProductInfo


class InventoryService:
    """도메인 서비스: Port에만 의존, 구체 ERP 구현을 모름"""

    def __init__(self, inventory_port: InventoryPort):
        self._inventory = inventory_port

    def get_available_stock(self, product_code: str) -> int:
        stock = self._inventory.get_stock(product_code)
        return stock.available_quantity if stock else 0

    def reserve_stock(self, product_code: str, quantity: int) -> bool:
        return self._inventory.reserve_stock(product_code, quantity)

    def sync_product_info(self, product_code: str) -> dict:
        info = self._inventory.get_product_info(product_code)
        if not info:
            return {}
        return {"name": info.name, "category": info.category, "price": info.price}
```

```python
# inventory/config.py
from inventory.adapters.erp_oracle_adapter import ErpOracleAdapter
from inventory.services import InventoryService

# 조립 (Composition Root) - ERP 교체 시 이 파일만 변경
inventory_service = InventoryService(
    inventory_port=ErpOracleAdapter(dsn="erp_user/pass@erp-db:1521/ERPDB"),
)
```

## Reason

### 핵심 문제 진단

원본 코드에는 세 가지 구조적 문제가 있다.

1. **강결합**: 서비스 함수가 `cx_Oracle`, ERP 테이블명(`TB_INV_MASTER`), ERP 컬럼명(`ZQTY_AVAIL`, `ZITEM_CD`)에 직접 의존한다. ERP가 변경되면 비즈니스 로직이 담긴 서비스 코드를 직접 수정해야 한다.
2. **교체 불가능**: ERP를 새 시스템으로 교체하려면 모든 서비스 함수를 처음부터 다시 작성해야 한다. DB 접속 방식, 테이블 구조, 컬럼명이 코드 전체에 흩어져 있기 때문이다.
3. **리소스 관리 부재**: 매 호출마다 커넥션을 생성하고, 예외 발생 시 `conn.close()`가 호출되지 않아 커넥션이 누수된다.

### 적용한 패턴: Ports and Adapters (Hexagonal Architecture)

리팩토링의 핵심은 **Port(추상 인터페이스)** 와 **Adapter(구체 구현)** 를 분리하는 것이다.

| 구성 요소 | 역할 | 파일 |
|---|---|---|
| Domain Model | 도메인 개념을 표현하는 불변 객체 | `domain/models.py` |
| Port | 외부 시스템과의 계약을 정의하는 추상 인터페이스 | `domain/ports.py` |
| Adapter | Port를 특정 기술로 구현 | `adapters/erp_oracle_adapter.py` |
| Service | Port에만 의존하는 비즈니스 로직 | `services.py` |
| Composition Root | 구체 구현을 조립하는 진입점 | `config.py` |

### 각 변경의 구체적 이유

**도메인 모델 분리 (`domain/models.py`)**
- `Stock`, `ProductInfo`를 `frozen=True` dataclass로 정의하여 ERP 테이블의 row tuple 대신 의미 있는 도메인 객체를 사용한다.
- `row[0]`, `row[1]` 같은 인덱스 접근이 `stock.available_quantity`, `info.name`으로 바뀌어 코드 가독성이 향상된다.

**Port 인터페이스 정의 (`domain/ports.py`)**
- `InventoryPort` ABC가 재고 시스템과의 계약을 정의한다. 서비스는 이 인터페이스에만 의존하므로 ERP가 Oracle이든 REST API든 관계없다.

**Adapter 구현 (`adapters/erp_oracle_adapter.py`)**
- ERP 테이블명과 컬럼명을 클래스 상수로 한곳에 모았다. ERP 스키마가 변경되면 상수만 수정하면 된다.
- `contextmanager`로 커넥션을 관리하여 예외 발생 시에도 `close()`가 반드시 호출된다.

**신규 ERP Adapter 예시 (`adapters/new_erp_api_adapter.py`)**
- 향후 ERP 교체 시 새 Adapter만 작성하면 된다. 서비스 코드는 한 줄도 변경하지 않는다.
- 이 예시는 REST API 기반 ERP를 가정한 구현이다.

**Composition Root (`config.py`)**
- ERP 교체 시 이 파일에서 `ErpOracleAdapter`를 `NewErpApiAdapter`로 바꾸면 끝난다.

### 변경 전후 비교

| 항목 | Before | After |
|---|---|---|
| ERP 테이블명 변경 | 3개 함수의 SQL 모두 수정 | Adapter 상수 1곳만 수정 |
| ERP 시스템 교체 | 전체 서비스 코드 재작성 | 새 Adapter 작성 + config 1줄 변경 |
| 커넥션 누수 | 예외 시 close() 미호출 | contextmanager로 보장 |
| 테스트 | 실제 Oracle DB 필요 | Port를 mock하여 단위 테스트 가능 |
| 도메인 표현 | `row[0]` 인덱스 접근 | `stock.available_quantity` 명시적 접근 |
