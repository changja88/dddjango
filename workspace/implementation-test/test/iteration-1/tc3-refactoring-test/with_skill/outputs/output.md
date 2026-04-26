# 테스트 코드 리팩토링

---

## 변경 1: 여러 Act 섹션을 개별 테스트로 분리

```
[Before]
def test_product_catalog():
    db = Mock()
    cache = Mock()
    logger = Mock()
    catalog = ProductCatalog(db, cache, logger)

    # 캐시 히트 테스트
    cache.get.return_value = {'id': 1, 'name': '노트북', 'price': 1000000}
    product = catalog.get_product(1)
    assert product['name'] == '노트북'
    cache.get.assert_called_once_with('product:1')
    db.query.assert_not_called()

    # 캐시 미스 테스트
    cache.get.reset_mock()
    db.query.reset_mock()
    cache.get.return_value = None
    db.query.return_value = {'id': 2, 'name': '키보드', 'price': 50000}
    product = catalog.get_product(2)
    assert product['name'] == '키보드'
    cache.set.assert_called_once()

    # 검색 테스트
    db.query.return_value = [{'id': 1, 'name': '노트북'}, {'id': 3, 'name': '노트패드'}]
    results = catalog.search_products('노트')
    assert len(results) == 2

    # 재고 업데이트 테스트
    cache.get.return_value = {'id': 1, 'name': '노트북', 'stock': 10}
    result = catalog.update_stock(1, 5)
    assert result is True
    cache.delete.assert_called_with('product:1')

    # 재고 음수 테스트
    with pytest.raises(ValueError, match='수량은 0 이상'):
        catalog.update_stock(1, -1)

    # 존재하지 않는 상품 재고 업데이트
    cache.get.return_value = None
    db.query.return_value = None
    with pytest.raises(ValueError, match='찾을 수 없습니다'):
        catalog.update_stock(999, 5)

[After]
# 6개의 독립된 테스트 함수로 분리 (아래 전체 코드 참조)

[Reason] AAA 패턴 (Three Laws #1) -- 하나의 테스트에 6개의 Act-Assert 블록이 있다. 각 블록은 서로 다른 행위를 검증하므로 반드시 개별 테스트로 분리해야 한다. reset_mock() 호출이 필요한 것 자체가 테스트가 독립적이지 않다는 신호다.
```

---

## 변경 2: 반복되는 Mock 생성을 pytest fixture로 추출

```
[Before]
def test_product_catalog():
    db = Mock()
    cache = Mock()
    logger = Mock()
    catalog = ProductCatalog(db, cache, logger)
    ...

def test_search_with_price_filter():
    db = Mock()
    cache = Mock()
    logger = Mock()
    catalog = ProductCatalog(db, cache, logger)
    ...

[After]
@pytest.fixture
def catalog():
    db = Mock(spec=["query", "execute"])
    cache = Mock(spec=["get", "set", "delete"])
    logger = Mock(spec=["info", "warning", "error"])
    _catalog = ProductCatalog(db, cache, logger)
    _catalog._db = db
    _catalog._cache = cache
    _catalog._logger = logger
    return _catalog

[Reason] Excessive Setup 안티패턴 해소 -- 동일한 3개 Mock 생성 + ProductCatalog 인스턴스화가 모든 테스트에서 반복된다. fixture로 추출하면 각 테스트는 Arrange 단계에서 테스트 고유의 설정만 남기게 되어 의도가 명확해진다.
```

---

## 변경 3: Mock에 spec 추가

```
[Before]
db = Mock()
cache = Mock()
logger = Mock()

[After]
db = Mock(spec=["query", "execute"])
cache = Mock(spec=["get", "set", "delete"])
logger = Mock(spec=["info", "warning", "error"])

[Reason] Mock 안전성 (Mock Patterns #1) -- spec 없는 Mock은 존재하지 않는 메서드를 호출해도 에러가 발생하지 않아 API 변경 시 테스트가 거짓 통과할 수 있다. spec을 지정하면 실제 인터페이스와의 불일치를 즉시 감지한다.
```

---

## 변경 4: 약한 assert를 구체적인 검증으로 강화

```
[Before]
cache.set.assert_called_once()

[After]
cache.set.assert_called_once_with('product:2', product, ttl=300)

[Reason] Empty/Weak Assertions -- assert_called_once()는 "호출되었는지"만 확인하고 어떤 인자로 호출되었는지는 검증하지 않는다. 캐시에 올바른 키, 값, TTL이 전달되는지까지 확인해야 캐시 로직의 정확성을 보장할 수 있다.
```

---

## 변경 5: 구현 결합도가 높은 assert 조정

```
[Before]
# 캐시 히트 테스트에서
cache.get.assert_called_once_with('product:1')
db.query.assert_not_called()

[After]
# 출력 기반 검증을 우선하고, 외부 의존성 호출 검증은 핵심 계약만 확인
assert product == {'id': 1, 'name': '노트북', 'price': 1000000}
db.query.assert_not_called()

[Reason] 검증 방식 우선순위 (출력 기반 > 통신 기반) -- 반환값 자체를 검증하면 cache.get의 호출 여부는 반환값으로 이미 간접 검증된다. db.query.assert_not_called()는 캐시 히트 시 DB를 호출하지 않는다는 핵심 계약이므로 유지한다.
```

---

## 변경 6: 에러 케이스에 parametrize 적용

```
[Before]
# 재고 음수 테스트
with pytest.raises(ValueError, match='수량은 0 이상'):
    catalog.update_stock(1, -1)

# 존재하지 않는 상품 재고 업데이트
cache.get.return_value = None
db.query.return_value = None
with pytest.raises(ValueError, match='찾을 수 없습니다'):
    catalog.update_stock(999, 5)

[After]
def test_update_stock_rejects_negative_quantity(catalog):
    with pytest.raises(ValueError, match='수량은 0 이상'):
        catalog.update_stock(1, -1)

def test_update_stock_raises_for_nonexistent_product(catalog):
    catalog._cache.get.return_value = None
    catalog._db.query.return_value = None

    with pytest.raises(ValueError, match='찾을 수 없습니다'):
        catalog.update_stock(999, 5)

[Reason] 독립성 유지 (Three Laws #2) -- 두 에러 케이스는 원인과 사전 조건이 다르다(음수 수량 vs 존재하지 않는 상품). 각각 독립된 Arrange가 필요하므로 별도 테스트로 분리한다. 동일한 패턴(같은 함수, 같은 인자 구조, 다른 데이터만)이 아니므로 parametrize보다 개별 함수가 의도를 더 명확하게 전달한다.
```

---

## 전체 리팩토링 결과

```python
import pytest
from unittest.mock import Mock


class ProductCatalog:
    def __init__(self, db, cache, logger):
        self.db = db
        self.cache = cache
        self.logger = logger

    def get_product(self, product_id: int) -> dict | None:
        cached = self.cache.get(f'product:{product_id}')
        if cached:
            return cached
        product = self.db.query('SELECT * FROM products WHERE id = %s', product_id)
        if product:
            self.cache.set(f'product:{product_id}', product, ttl=300)
        return product

    def search_products(
        self, keyword: str, min_price: float = 0, max_price: float = float('inf')
    ) -> list[dict]:
        results = self.db.query(
            'SELECT * FROM products WHERE name LIKE %s AND price BETWEEN %s AND %s',
            f'%{keyword}%', min_price, max_price,
        )
        self.logger.info(f'Search for {keyword}: {len(results)} results')
        return results

    def update_stock(self, product_id: int, quantity: int) -> bool:
        if quantity < 0:
            raise ValueError('수량은 0 이상이어야 합니다')
        product = self.get_product(product_id)
        if not product:
            raise ValueError(f'상품 {product_id}을 찾을 수 없습니다')
        self.db.execute(
            'UPDATE products SET stock = %s WHERE id = %s', quantity, product_id
        )
        self.cache.delete(f'product:{product_id}')
        self.logger.info(f'Stock updated: product={product_id}, quantity={quantity}')
        return True


# ===== 테스트 코드 =====


@pytest.fixture
def catalog():
    db = Mock(spec=["query", "execute"])
    cache = Mock(spec=["get", "set", "delete"])
    logger = Mock(spec=["info", "warning", "error"])
    _catalog = ProductCatalog(db, cache, logger)
    _catalog._db = db
    _catalog._cache = cache
    _catalog._logger = logger
    return _catalog


class TestGetProduct:

    def test_returns_cached_product_without_db_query(self, catalog):
        cached_product = {'id': 1, 'name': '노트북', 'price': 1000000}
        catalog._cache.get.return_value = cached_product

        product = catalog.get_product(1)

        assert product == cached_product
        catalog._db.query.assert_not_called()

    def test_queries_db_and_caches_on_cache_miss(self, catalog):
        db_product = {'id': 2, 'name': '키보드', 'price': 50000}
        catalog._cache.get.return_value = None
        catalog._db.query.return_value = db_product

        product = catalog.get_product(2)

        assert product == db_product
        catalog._cache.set.assert_called_once_with(
            'product:2', db_product, ttl=300
        )

    def test_returns_none_for_nonexistent_product(self, catalog):
        catalog._cache.get.return_value = None
        catalog._db.query.return_value = None

        product = catalog.get_product(999)

        assert product is None
        catalog._cache.set.assert_not_called()


class TestSearchProducts:

    def test_returns_matching_products(self, catalog):
        expected = [{'id': 1, 'name': '노트북'}, {'id': 3, 'name': '노트패드'}]
        catalog._db.query.return_value = expected

        results = catalog.search_products('노트')

        assert results == expected

    def test_passes_price_filter_to_query(self, catalog):
        catalog._db.query.return_value = [
            {'id': 1, 'name': '저렴한노트북', 'price': 500000}
        ]

        results = catalog.search_products('노트북', min_price=100000, max_price=600000)

        assert len(results) == 1
        catalog._db.query.assert_called_once_with(
            'SELECT * FROM products WHERE name LIKE %s AND price BETWEEN %s AND %s',
            '%노트북%', 100000, 600000,
        )

    def test_logs_search_results_count(self, catalog):
        catalog._db.query.return_value = [{'id': 1}, {'id': 2}]

        catalog.search_products('노트')

        catalog._logger.info.assert_called_once_with('Search for 노트: 2 results')


class TestUpdateStock:

    def test_updates_stock_and_invalidates_cache(self, catalog):
        catalog._cache.get.return_value = {'id': 1, 'name': '노트북', 'stock': 10}

        result = catalog.update_stock(1, 5)

        assert result is True
        catalog._db.execute.assert_called_once_with(
            'UPDATE products SET stock = %s WHERE id = %s', 5, 1
        )
        catalog._cache.delete.assert_called_once_with('product:1')

    def test_rejects_negative_quantity(self, catalog):
        with pytest.raises(ValueError, match='수량은 0 이상'):
            catalog.update_stock(1, -1)

        catalog._db.execute.assert_not_called()

    def test_raises_for_nonexistent_product(self, catalog):
        catalog._cache.get.return_value = None
        catalog._db.query.return_value = None

        with pytest.raises(ValueError, match='찾을 수 없습니다'):
            catalog.update_stock(999, 5)

        catalog._db.execute.assert_not_called()
```

---

## 리팩토링 요약

| 항목 | 적용 여부 | 내용 |
|------|-----------|------|
| Multiple Act sections -> SPLIT | O | 6개 Act-Assert 블록을 9개 독립 테스트로 분리 |
| Shared mutable state -> ISOLATE | O | reset_mock() 제거, fixture로 테스트마다 새 인스턴스 생성 |
| Over-mocked tests -> REPLACE | -- | db/cache/logger는 외부 의존성이므로 Mock 사용이 적절 |
| Mock without spec -> ADD spec | O | 모든 Mock에 spec 추가 |
| Time-dependent tests | -- | 해당 없음 |
| Repetitive test cases -> parametrize | -- | 에러 케이스들의 사전 조건이 달라 parametrize 대신 개별 분리 |
| Complex setup -> EXTRACT to fixture | O | 3개 Mock + catalog 생성을 fixture로 추출 |
| Implementation-coupled assertions | O | 출력 기반 검증 우선, 핵심 계약만 통신 기반 검증 유지 |
| Empty/weak assertions | O | assert_called_once()를 인자까지 검증하는 형태로 강화 |
| Misplaced test level | -- | 해당 없음 |

추가 개선 사항:
- `TestGetProduct`, `TestSearchProducts`, `TestUpdateStock` 클래스로 관련 테스트를 논리적으로 그룹화
- 존재하지 않는 상품 조회 시 캐시에 저장하지 않는 동작을 검증하는 테스트 추가 (`test_returns_none_for_nonexistent_product`)
- 로깅 동작을 검증하는 테스트 분리 (`test_logs_search_results_count`)
- 에러 발생 시 DB execute가 호출되지 않음을 검증하여 부작용 방지 확인
