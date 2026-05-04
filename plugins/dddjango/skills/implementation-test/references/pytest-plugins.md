# pytest 플러그인 생태계 레퍼런스

pytest 플러그인 사용법과 설정에 대한 상세 규칙과 예시.

---

## 1. pytest-xdist: 병렬 테스트 실행

```bash
pip install pytest-xdist
```

```bash
pytest -n auto                    # 자동 CPU 감지
pytest -n 8                       # 명시적 워커 수
```

**분산 전략**:

```bash
pytest -n auto --dist load        # 라운드 로빈 분배 (기본)
pytest -n auto --dist loadscope   # 모듈/클래스 단위로 같은 워커에 배치
pytest -n auto --dist loadfile    # 같은 파일의 테스트를 같은 워커에 배치
pytest -n auto --dist loadgroup   # xdist_group 마커로 그룹 지정
```

```python
import pytest

# loadgroup 사용 예시: 같은 워커에서 실행되어야 하는 테스트
@pytest.mark.xdist_group("database_sequential")
def test_create_user():
    pass

@pytest.mark.xdist_group("database_sequential")
def test_update_user():
    pass
```

> 출처: [pytest-xdist Documentation](https://pytest-xdist.readthedocs.io/en/stable/distribution.html)

---

## 2. pytest-asyncio: 비동기 테스트

```bash
pip install pytest-asyncio
```

**설정 (pyproject.toml)**:

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"   # auto | strict
```

- **auto**: 모든 `async def` 테스트와 fixture를 자동으로 비동기 처리. 프로젝트가 asyncio만 사용할 때 권장.
- **strict**: `@pytest_asyncio.fixture`를 명시적으로 붙여야 함. 여러 비동기 라이브러리를 동시 사용할 때 권장.

```python
import pytest
import httpx

# auto 모드: @pytest.mark.asyncio 불필요
async def test_async_endpoint():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com/health")
    assert response.status_code == 200

# strict 모드에서의 async fixture
import pytest_asyncio

@pytest_asyncio.fixture
async def async_client():
    async with httpx.AsyncClient(base_url="http://testserver") as client:
        yield client

async def test_with_client(async_client):
    response = await async_client.get("/api/users")
    assert response.status_code == 200
```

> 출처: [pytest-asyncio Documentation](https://pytest-asyncio.readthedocs.io/en/latest/concepts.html)

---

## 3. pytest-cov: 커버리지 통합

```bash
pip install pytest-cov
```

```bash
pytest --cov=src tests/                    # 기본 사용
pytest --cov=src --cov-report=html tests/  # HTML 리포트
pytest --cov=src --cov-fail-under=80 tests/ # 최소 커버리지 강제
pytest --cov=src --cov-branch tests/       # 분기 커버리지
pytest -n auto --cov=src tests/            # xdist와 함께 사용
```

> 출처: [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)

---

## 4. pytest-randomly: 테스트 순서 무작위화

```bash
pip install pytest-randomly
```

테스트 간 암묵적 의존성을 발견하기 위해 실행 순서를 무작위로 섞는다.

```bash
pytest                                     # 자동 적용 (설치만 하면 활성화)
pytest -p randomly --randomly-seed=12345   # 시드 고정
pytest -p randomly --randomly-seed=last    # 마지막 시드 재현
pytest -p no:randomly                      # 비활성화
```

> 출처: [pytest-randomly PyPI](https://pypi.org/project/pytest-randomly/)

---

## 5. pytest-timeout: 테스트 시간 제한

```python
import pytest

@pytest.mark.timeout(5)
def test_should_be_fast():
    """5초 안에 완료되어야 하는 테스트"""
    result = quick_operation()
    assert result is not None

@pytest.mark.timeout(120)
def test_allowed_to_be_slow():
    """2분까지 허용"""
    result = batch_processing()
    assert result.success
```

```toml
# pyproject.toml에서 전역 설정
[tool.pytest.ini_options]
timeout = 30
```

> 출처: [pytest-timeout PyPI](https://pypi.org/project/pytest-timeout/)
