# TC3 - Test Code Refactoring Result

## Identified Problems

1. **Monolithic test function** -- `test_product_catalog`가 6개의 서로 다른 시나리오를 하나의 함수에 담고 있다. 하나가 실패하면 나머지는 실행되지 않고, 실패 원인 파악이 어렵다.
2. **Mock 상태 공유 및 `reset_mock` 호출** -- 하나의 Mock 객체를 여러 시나리오에서 재사용하면서 `reset_mock()`을 수동으로 호출한다. 이전 테스트의 상태가 다음 테스트에 누출될 위험이 있다.
3. **Fixture 미사용** -- `db`, `cache`, `logger`, `catalog`을 매 테스트 함수마다 수동으로 생성한다. pytest fixture로 중복을 제거할 수 있다.
4. **미사용 import** -- `time`, `os`, `patch`를 import하지만 사용하지 않는다.
5. **테스트 이름이 시나리오를 설명하지 않음** -- `test_product_catalog`라는 이름만으로는 무엇을 검증하는지 알 수 없다.

## Refactored Code

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

    def search_products(self, keyword: str, min_price: float = 0, max_price: float = float('inf')) -> list[dict]:
        results = self.db.query(
            'SELECT * FROM products WHERE name LIKE %s AND price BETWEEN %s AND %s',
            f'%{keyword}%', min_price, max_price
        )
        self.logger.info(f'Search for {keyword}: {len(results)} results')
        return results

    def update_stock(self, product_id: int, quantity: int) -> bool:
        if quantity < 0:
            raise ValueError('수량은 0 이상이어야 합니다')
        product = self.get_product(product_id)
        if not product:
            raise ValueError(f'상품 {product_id}을 찾을 수 없습니다')
        self.db.execute('UPDATE products SET stock = %s WHERE id = %s', quantity, product_id)
        self.cache.delete(f'product:{product_id}')
        self.logger.info(f'Stock updated: product={product_id}, quantity={quantity}')
        return True


# ===== Fixtures =====

@pytest.fixture
def db():
    return Mock()


@pytest.fixture
def cache():
    return Mock()


@pytest.fixture
def logger():
    return Mock()


@pytest.fixture
def catalog(db, cache, logger):
    return ProductCatalog(db, cache, logger)


# ===== get_product tests =====

class TestGetProduct:
    def test_returns_cached_product_without_db_query(self, catalog, cache, db):
        cache.get.return_value = {'id': 1, 'name': '노트북', 'price': 1000000}

        product = catalog.get_product(1)

        assert product == {'id': 1, 'name': '노트북', 'price': 1000000}
        cache.get.assert_called_once_with('product:1')
        db.query.assert_not_called()

    def test_queries_db_on_cache_miss_and_caches_result(self, catalog, cache, db):
        cache.get.return_value = None
        db.query.return_value = {'id': 2, 'name': '키보드', 'price': 50000}

        product = catalog.get_product(2)

        assert product == {'id': 2, 'name': '키보드', 'price': 50000}
        db.query.assert_called_once_with('SELECT * FROM products WHERE id = %s', 2)
        cache.set.assert_called_once_with('product:2', {'id': 2, 'name': '키보드', 'price': 50000}, ttl=300)

    def test_returns_none_when_product_not_found(self, catalog, cache, db):
        cache.get.return_value = None
        db.query.return_value = None

        product = catalog.get_product(999)

        assert product is None
        cache.set.assert_not_called()


# ===== search_products tests =====

class TestSearchProducts:
    def test_returns_matching_products(self, catalog, db):
        db.query.return_value = [
            {'id': 1, 'name': '노트북'},
            {'id': 3, 'name': '노트패드'},
        ]

        results = catalog.search_products('노트')

        assert len(results) == 2

    def test_passes_price_filter_to_query(self, catalog, db):
        db.query.return_value = [{'id': 1, 'name': '저렴한노트북', 'price': 500000}]

        results = catalog.search_products('노트북', min_price=100000, max_price=600000)

        assert len(results) == 1
        db.query.assert_called_once_with(
            'SELECT * FROM products WHERE name LIKE %s AND price BETWEEN %s AND %s',
            '%노트북%', 100000, 600000,
        )

    def test_logs_search_result_count(self, catalog, db, logger):
        db.query.return_value = [{'id': 1, 'name': '노트북'}]

        catalog.search_products('노트북')

        logger.info.assert_called_once_with('Search for 노트북: 1 results')


# ===== update_stock tests =====

class TestUpdateStock:
    def test_updates_stock_and_invalidates_cache(self, catalog, cache, db, logger):
        cache.get.return_value = {'id': 1, 'name': '노트북', 'stock': 10}

        result = catalog.update_stock(1, 5)

        assert result is True
        db.execute.assert_called_once_with(
            'UPDATE products SET stock = %s WHERE id = %s', 5, 1,
        )
        cache.delete.assert_called_once_with('product:1')
        logger.info.assert_called_once_with('Stock updated: product=1, quantity=5')

    def test_raises_error_for_negative_quantity(self, catalog):
        with pytest.raises(ValueError, match='수량은 0 이상'):
            catalog.update_stock(1, -1)

    def test_raises_error_for_nonexistent_product(self, catalog, cache, db):
        cache.get.return_value = None
        db.query.return_value = None

        with pytest.raises(ValueError, match='찾을 수 없습니다'):
            catalog.update_stock(999, 5)
```

## Summary of Changes

| # | Before | After | Rationale |
|---|--------|-------|-----------|
| 1 | `test_product_catalog` 하나에 6개 시나리오 | 9개의 개별 테스트 메서드 | 각 테스트가 독립적으로 실행/실패하므로 원인 파악이 즉각적이다 |
| 2 | `reset_mock()` 수동 호출 | fixture를 통한 자동 격리 | 매 테스트마다 새 Mock이 주입되므로 상태 누출이 불가능하다 |
| 3 | 매 함수마다 `db = Mock()` 반복 | `@pytest.fixture`로 한 번 선언 | 중복 제거, 의존성 변경 시 수정 지점이 하나다 |
| 4 | `import time, os, patch` | 미사용 import 제거 | 불필요한 의존성 제거 |
| 5 | `test_product_catalog` | `TestGetProduct`, `TestSearchProducts`, `TestUpdateStock` 클래스 분리 | 기능 단위로 그룹화하여 구조가 명확하다 |
| 6 | 테스트 이름 `test_product_catalog` | `test_returns_cached_product_without_db_query` 등 서술형 | 테스트 이름만으로 검증 의도를 파악할 수 있다 |
| 7 | 캐시 미스 시 `cache.set` 호출 여부만 확인 | 인자까지 정확히 검증 | TTL 값(300)과 캐시 키가 올바른지까지 확인한다 |
| 8 | 상품 미존재 시 `get_product` 반환값 미검증 | `test_returns_none_when_product_not_found` 추가 | 경계 조건 커버리지 향상 |
| 9 | 로깅 검증 없음 | `test_logs_search_result_count` 추가 | `logger.info` 호출이 올바른 메시지를 전달하는지 확인 |
