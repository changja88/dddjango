# Docker 기반 통합 테스트 (testcontainers) 레퍼런스

testcontainers-python을 사용한 통합 테스트의 상세 규칙과 예시.

testcontainers-python은 실제 Docker 컨테이너를 사용하여 통합 테스트를 수행한다. mock이나 인메모리 대체물이 아닌 **실제 서비스**로 테스트한다.

```bash
pip install testcontainers[postgres]
```

---

## 1. PostgreSQL 통합 테스트

```python
import pytest
from testcontainers.postgres import PostgresContainer
import sqlalchemy

@pytest.fixture(scope="session")
def postgres_container():
    """세션 스코프: 전체 테스트 스위트에서 1번만 시작"""
    with PostgresContainer("postgres:16-alpine") as postgres:
        yield postgres

@pytest.fixture(scope="function")
def db_engine(postgres_container):
    """각 테스트마다 새 엔진 (트랜잭션 롤백으로 격리)"""
    engine = sqlalchemy.create_engine(
        postgres_container.get_connection_url()
    )
    yield engine
    engine.dispose()

@pytest.fixture(scope="function")
def db_session(db_engine):
    """각 테스트를 트랜잭션으로 감싸서 격리 (SQLAlchemy 2.0 스타일)"""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = Session(connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()

def test_user_crud(db_session):
    """실제 PostgreSQL에서 CRUD 테스트"""
    user = User(name="Alice", email="alice@example.com")
    db_session.add(user)
    db_session.flush()

    found = db_session.query(User).filter_by(name="Alice").first()
    assert found is not None
    assert found.email == "alice@example.com"
```

---

## 2. Redis 통합 테스트

```python
from testcontainers.redis import RedisContainer
import redis

@pytest.fixture(scope="module")
def redis_client():
    with RedisContainer("redis:7-alpine") as container:
        client = redis.Redis.from_url(container.get_connection_url())
        yield client

@pytest.fixture(autouse=True)
def _clean_redis(redis_client):
    """각 테스트 후 Redis 데이터 초기화"""
    yield
    redis_client.flushall()

def test_cache_set_get(redis_client):
    redis_client.set("key", "value")
    assert redis_client.get("key") == b"value"

def test_cache_expiry(redis_client):
    redis_client.setex("temp", 1, "temporary")
    assert redis_client.get("temp") == b"temporary"
    import time
    time.sleep(1.1)
    assert redis_client.get("temp") is None
```

---

## 3. 여러 서비스 동시 사용

```python
@pytest.fixture(scope="session")
def services():
    """여러 서비스를 한 번에 시작"""
    with PostgresContainer("postgres:16") as pg, \
         RedisContainer("redis:7") as redis_container:
        yield {
            "postgres_url": pg.get_connection_url(),
            "redis_url": redis_container.get_connection_url(),
        }

def test_full_integration(services):
    """실제 DB + 실제 캐시로 통합 테스트"""
    db = create_engine(services["postgres_url"])
    cache = redis.from_url(services["redis_url"])

    user_service = UserService(db=db, cache=cache)
    user = user_service.create("Alice")
    assert user_service.get_cached(user.id) is not None
```

> 출처: [testcontainers-python 공식 문서](https://testcontainers-python.readthedocs.io/), [Testcontainers Getting Started](https://testcontainers.com/guides/getting-started-with-testcontainers-for-python/)
