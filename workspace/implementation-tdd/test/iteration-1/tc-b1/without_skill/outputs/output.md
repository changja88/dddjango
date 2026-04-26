# TDD 관점 테스트 코드 리뷰: WeatherService

## 1. 총평

이 테스트 코드는 기본적인 mock 기반 단위 테스트로서 동작은 하지만, **TDD의 핵심 원칙과는 상당한 거리가 있다.** 테스트가 구현 세부사항(implementation detail)에 과도하게 결합되어 있고, 실패 경로에 대한 고려가 전혀 없으며, 테스트가 설계를 이끌어내는(drive) 역할을 하지 못하고 있다.

---

## 2. 주요 문제점

### 2.1 구현 세부사항에 대한 과도한 결합

**문제 코드:**
```python
mock_get.assert_called_once_with(
    'https://api.weather.com/v1/current',
    params={'city': 'Seoul', 'key': 'test-key'}
)
```

이 assertion은 `requests.get`이 정확히 어떤 URL과 파라미터로 호출되었는지를 검증한다. 이는 **행위(behavior)가 아닌 구현 방식(implementation)을 테스트**하는 것이다.

- 내부적으로 `httpx`, `aiohttp`, 혹은 `urllib`로 교체하면 테스트가 깨진다.
- URL 구성 방식을 리팩터링해도 테스트가 깨진다.
- TDD에서 테스트는 **"무엇을 하는가(what)"를 검증해야지, "어떻게 하는가(how)"를 검증하면 안 된다.**

**개선 방향:** HTTP 호출의 정확한 형태를 검증하는 대신, 반환값의 정확성만 검증하거나, HTTP 클라이언트를 의존성 주입(DI)으로 분리한다.

### 2.2 테스트 대상과 mock 대상의 혼재 (프로덕션 코드와 테스트가 같은 파일)

현재 `WeatherService` 클래스가 테스트 파일 안에 정의되어 있다. TDD에서는:

1. 먼저 테스트를 작성한다 (RED)
2. 테스트를 통과시키기 위한 최소한의 프로덕션 코드를 작성한다 (GREEN)
3. 리팩터링한다 (REFACTOR)

프로덕션 코드와 테스트 코드가 같은 파일에 있으면 이 사이클을 따르기 어렵고, **테스트가 구현을 주도하는 것이 아니라 구현을 확인만 하는 형태**가 된다.

### 2.3 실패 경로(Sad Path) 테스트 부재

현재 테스트는 **모두 정상 응답(Happy Path)만 검증**한다. TDD에서는 실패 시나리오를 먼저 고려하여 견고한 설계를 이끌어내야 한다.

누락된 테스트 케이스:
- API가 HTTP 4xx/5xx 에러를 반환하는 경우
- 응답 JSON에 `'main'` 키나 `'temp'` 키가 없는 경우
- 네트워크 타임아웃 또는 연결 실패
- `city`가 빈 문자열이거나 `None`인 경우
- `days`가 0 이하인 경우
- API 키가 유효하지 않은 경우

이러한 테스트가 없으므로, `WeatherService`에는 에러 처리 로직도 없다. **TDD였다면 실패 케이스 테스트를 먼저 작성하고, 그것을 통과시키기 위해 에러 처리 코드를 추가했을 것이다.**

### 2.4 경계값(Boundary) 테스트 부재

`is_hot` 메서드에서 경계값 30도에 대한 테스트가 없다:

```python
# 누락: 정확히 30도일 때의 동작은?
def test_is_hot_at_boundary():
    # temp == 30.0 -> is_hot은 False여야 하는가?
```

현재 구현에서 `> 30`이므로 30.0은 `False`를 반환하지만, 이것이 의도된 동작인지 테스트로 명시되지 않았다. TDD에서는 **경계 조건을 먼저 테스트로 정의하여 명세(specification) 역할**을 하게 한다.

### 2.5 설계를 개선하지 못하는 테스트

TDD의 핵심 가치 중 하나는 **테스트가 더 나은 설계를 이끌어내는 것**이다. 현재 테스트는 `requests.get`을 직접 patch하고 있는데, 이는 `WeatherService`가 HTTP 클라이언트에 직접 의존하고 있기 때문이다.

TDD로 접근했다면 테스트의 어려움이 설계 문제를 드러내, 아래와 같은 구조로 발전했을 가능성이 높다:

```python
# 의존성 주입을 통한 개선된 설계
class WeatherService:
    def __init__(self, api_key: str, http_client=None):
        self.api_key = api_key
        self.http_client = http_client or requests

    def get_temperature(self, city: str) -> float:
        resp = self.http_client.get(...)
        ...
```

이렇게 하면 `patch` 없이 fake/stub 객체를 주입하여 테스트할 수 있고, 테스트가 구현 세부사항에서 분리된다.

---

## 3. 긍정적인 부분

- `test_is_hot_true`와 `test_is_hot_false`로 boolean 반환의 양쪽 케이스를 모두 검증하고 있다.
- 테스트 함수명이 `test_<메서드명>_<조건>` 형태로 일관성이 있다.
- mock 응답 데이터가 실제 API 응답 구조를 반영하고 있어 가독성이 좋다.
- 각 테스트가 독립적으로 실행 가능하다 (공유 상태 없음).

---

## 4. TDD 사이클 기반 개선 제안

아래는 TDD Red-Green-Refactor 사이클을 따라 이 코드를 개선하는 방향이다.

### 4.1 Phase 1: RED - 실패하는 테스트 먼저 작성

```python
# 에러 처리에 대한 테스트를 먼저 작성
def test_get_temperature_raises_on_http_error():
    client = FakeHttpClient(status_code=500)
    service = WeatherService('test-key', http_client=client)
    with pytest.raises(WeatherServiceError):
        service.get_temperature('Seoul')

def test_get_temperature_raises_on_missing_data():
    client = FakeHttpClient(json_data={'unexpected': 'format'})
    service = WeatherService('test-key', http_client=client)
    with pytest.raises(WeatherServiceError):
        service.get_temperature('Seoul')

def test_is_hot_boundary_at_30():
    client = FakeHttpClient(json_data={'main': {'temp': 30.0}})
    service = WeatherService('test-key', http_client=client)
    assert service.is_hot('Seoul') is False
```

### 4.2 Phase 2: GREEN - 테스트를 통과시키는 최소 구현

```python
class WeatherServiceError(Exception):
    pass

class WeatherService:
    def __init__(self, api_key: str, http_client=None):
        self.api_key = api_key
        self.http_client = http_client or requests
        self.base_url = 'https://api.weather.com/v1'

    def get_temperature(self, city: str) -> float:
        resp = self.http_client.get(
            f'{self.base_url}/current',
            params={'city': city, 'key': self.api_key}
        )
        if resp.status_code != 200:
            raise WeatherServiceError(f'HTTP {resp.status_code}')
        data = resp.json()
        try:
            return data['main']['temp']
        except KeyError as e:
            raise WeatherServiceError(f'Unexpected response format: {e}')
```

### 4.3 Phase 3: REFACTOR - 테스트 헬퍼 정리

```python
# 테스트 전용 Fake 객체 (patch 불필요)
class FakeResponse:
    def __init__(self, json_data, status_code=200):
        self.status_code = status_code
        self._json_data = json_data

    def json(self):
        return self._json_data

class FakeHttpClient:
    def __init__(self, json_data=None, status_code=200):
        self.response = FakeResponse(json_data or {}, status_code)
        self.last_request = None

    def get(self, url, **kwargs):
        self.last_request = (url, kwargs)
        return self.response
```

---

## 5. 체크리스트 요약

| 항목 | 현재 상태 | 개선 필요 |
|------|-----------|-----------|
| Happy Path 테스트 | O | - |
| Sad Path / 에러 테스트 | X | 필수 |
| 경계값 테스트 | X | 필수 |
| 구현과 테스트 분리 | X | 필수 |
| 의존성 주입 활용 | X | 권장 |
| `patch` 대신 Fake/Stub 사용 | X | 권장 |
| 테스트가 설계를 주도 | X | TDD 핵심 |
| 테스트 함수 네이밍 | O | - |
| 테스트 독립성 | O | - |

---

## 6. 결론

현재 코드는 **"구현 후 테스트 작성(Test-After)"** 패턴이며, TDD가 아니다. TDD에서 테스트는 단순한 검증 도구가 아니라 **설계 도구(design tool)이자 명세(specification)**이다. 핵심 개선 포인트 세 가지:

1. **실패 케이스 테스트를 먼저 작성**하여 에러 처리 설계를 이끌어낼 것
2. **의존성 주입**으로 HTTP 클라이언트를 분리하여 `patch` 의존을 제거할 것
3. **경계값 테스트**를 추가하여 비즈니스 규칙을 명세로 남길 것
