# TDD 관점 테스트 코드 리뷰: WeatherService

## 잘한 점

1. **AAA 패턴 준수**: 모든 테스트가 Arrange(Mock 설정, 서비스 생성) - Act(메서드 호출) - Assert(결과 검증) 구조를 따르고 있다. 테스트를 위에서 아래로 자연스럽게 읽을 수 있다.

2. **테스트 격리**: 각 테스트가 `with patch` 컨텍스트 매니저를 사용하여 독립적인 Mock 상태를 갖는다. 공유 가변 상태가 없으므로 Erratic Test 냄새가 없다.

3. **경계값 테스트**: `is_hot`에 대해 True/False 두 경우를 모두 테스트하고 있다.

4. **외부 의존성에 Mock 사용**: `requests.get`은 외부 HTTP API 호출이므로 Mock으로 격리하는 것은 런던 학파 관점에서 올바른 선택이다.

---

## 개선 사항

### [런던 학파 오적용 - 내부 협력자에 대한 구현 결합] -- `test_is_hot_true`, `test_is_hot_false`에서 `is_hot`의 내부 구현인 `get_temperature` 호출을 `requests.get` 수준까지 Mock하고 있다

`is_hot`은 `get_temperature`의 반환값이 30을 초과하는지 판단하는 **순수한 비교 로직**이다. 그런데 테스트가 `requests.get`까지 Mock하면서 `{'main': {'temp': 35.0}}` 같은 API 응답 구조를 알아야 한다. 이는 `is_hot`의 관심사가 아닌 `get_temperature`의 구현 세부사항이다.

Khorikov의 4대 기둥 중 **리팩토링 내성**이 낮아진다. 만약 `get_temperature`가 내부적으로 다른 API 엔드포인트를 쓰거나 응답 구조가 바뀌면, `is_hot` 테스트까지 깨진다. `is_hot`의 행위 자체는 변하지 않았는데도 테스트가 실패하는 **거짓 양성(false positive)** 상황이 발생한다.

더 나은 접근: `get_temperature`를 Mock하여 `is_hot`이 온도 비교 로직만 검증하도록 격리하거나, `is_hot` 로직을 순수 함수로 추출하여 출력 기반 테스트로 전환한다.

---

### [통신 기반 테스트 남용 - 출력 기반 테스트가 적합한 곳에서 행위 검증 사용] -- `test_get_temperature`와 `test_get_forecast`에서 `assert_called_once_with`로 호출 인자를 정밀 검증하고 있다

`assert_called_once_with`로 URL과 params를 정확히 검증하는 것은 통신 기반(Communication-based) 테스트다. Khorikov의 권고에 따르면 출력 기반 > 상태 기반 > 통신 기반 순서로 선호해야 한다.

`get_temperature`가 25.5를 반환하는지(출력 기반)만 검증하면 충분한데, `requests.get`이 어떤 URL과 파라미터로 호출되었는지까지 검증하면 **구현에 결합된 테스트**가 된다. 만약 base_url이 바뀌거나, 파라미터 이름이 변경되면, 반환값은 동일해도 테스트가 깨진다.

외부 API 호출의 정확성을 검증해야 하는 상황이라면 별도의 통합 테스트나 계약 테스트(Contract Test)에서 다루는 것이 적절하다. 단위 테스트에서는 반환값 검증에 집중하는 것이 리팩토링 내성을 높인다.

---

### [Test-Last 징후 - 프로덕션 코드와 테스트가 동일 파일에 완성된 형태로 존재] -- 프로덕션 코드(`WeatherService`)와 테스트 코드가 함께 제시되어 Red-Green-Refactor 사이클의 흔적이 없다

TDD의 3법칙에 따르면 (1) 실패하는 테스트를 먼저 작성하고, (2) 테스트를 통과시킬 최소한의 프로덕션 코드를 작성하고, (3) 초록 막대 아래에서 리팩토링해야 한다. 현재 코드는 `WeatherService` 클래스가 완성된 형태로 존재하고, 테스트가 이를 사후 검증하는 구조다.

TDD라면 다음과 같은 점진적 과정이 있어야 한다:
- 1단계: `get_temperature`만 있는 최소 클래스 + 해당 테스트
- 2단계: `is_hot` 추가 + 해당 테스트
- 3단계: `get_forecast` 추가 + 해당 테스트

이 과정이 보이지 않으므로 Big-bang 구현 후 테스트를 붙인 것으로 판단된다.

---

### [경계값 테스트 누락 - 불완전한 테스트 목록] -- `is_hot`의 경계값인 정확히 30도인 경우가 테스트되지 않았다

`is_hot`은 `> 30`으로 판단한다. True(35도)와 False(20도) 케이스는 있지만, 경계값인 **정확히 30도**인 경우가 빠져 있다. 30도일 때 `is_hot`이 False를 반환하는지 확인하는 테스트가 필요하다. 이는 빨간 막대 패턴의 **테스트 목록** 원칙에 해당한다 -- 시작 전에 테스트해야 할 모든 경우를 나열하고, 경계값을 포함해야 한다.

또한 다음 엣지 케이스들도 누락되었다:
- API 호출 실패 시(네트워크 오류, 타임아웃)의 에러 처리
- 잘못된 응답 형식(키 누락 등)에 대한 방어 코드 테스트
- `get_forecast`에서 `days`가 0이거나 음수인 경우

---

### [테스트 코드 중복 - 반복되는 Mock 설정] -- 4개 테스트 모두에서 동일한 `with patch('requests.get')`, `WeatherService('test-key')` 패턴이 반복된다

테스트 냄새 카탈로그의 **Test Code Duplication**에 해당한다. `patch`와 `WeatherService` 인스턴스 생성이 모든 테스트에서 반복된다. pytest fixture를 사용하여 공통 설정을 추출하면 유지보수성이 향상된다.

```python
@pytest.fixture
def weather_service():
    return WeatherService('test-key')

@pytest.fixture
def mock_api():
    with patch('requests.get') as mock_get:
        yield mock_get
```

---

### [테스트 명명 - 조건과 기대 행위가 드러나지 않는 이름] -- `test_get_temperature`, `test_get_forecast` 등은 메서드 이름만 반복하고 있다

테스팅 패턴의 명명 규칙인 `[테스트 대상]_[조건]_[기대 행위]` 형식을 따르지 않는다. 현재 이름으로는 어떤 시나리오를 테스트하는지 알 수 없다. 테스트 냄새 중 **Obscure Test**에 가깝다.

개선 예시:
- `test_get_temperature` -> `test_get_temperature__valid_city__returns_temperature_from_api`
- `test_is_hot_true` -> `test_is_hot__temperature_above_30__returns_true`
- `test_get_forecast` -> `test_get_forecast__valid_city_and_days__returns_forecast_list`

---

## 리뷰 체크리스트 검증 결과

| 항목 | 판정 | 비고 |
|------|------|------|
| Test-last 징후 | **해당** | 완성된 프로덕션 코드 + 사후 테스트 구조 |
| Red-Green-Refactor 사이클 부재 | **해당** | 점진적 개발 흔적 없음, big-bang 구현 |
| 구현 세부사항에 결합된 테스트 | **해당** | `assert_called_once_with`로 URL/params 정밀 검증, `is_hot`이 API 응답 구조에 의존 |
| 내부 협력자에 대한 Mock 남용 | **해당** | `is_hot` 테스트에서 `requests.get`까지 Mock (내부 메서드인 `get_temperature`의 구현을 관통) |
| 테스트 격리 문제 | 해당 없음 | `with patch` 컨텍스트 매니저로 격리 양호 |
| 테스트 냄새 | **해당** | Test Code Duplication (반복 설정), Obscure Test (불명확한 이름) |
| Big-bang 구현 | **해당** | 3개 메서드가 한 번에 완성된 형태 |
| 출력 기반 테스트 가능한 곳에서 통신 기반 사용 | **해당** | `get_temperature` 반환값 검증이면 충분한 곳에서 호출 인자까지 검증 |
| 경계/엣지 케이스 누락 | **해당** | 경계값 30도, 에러 상황, 잘못된 입력 미테스트 |
| 설계를 주도하지 않는 테스트 | **해당** | 테스트가 설계를 이끌지 않고, 기존 구현을 사후 검증 |

---

## 요약

이 테스트 코드는 기본적인 동작 검증은 수행하지만, TDD 방법론의 관점에서 보면 **Test-Last(사후 테스트)** 방식으로 작성된 코드의 전형적 특징을 보인다. 가장 큰 문제는 (1) 통신 기반 테스트의 남용으로 리팩토링 내성이 낮고, (2) `is_hot` 같은 순수 비교 로직이 API 응답 구조에 결합되어 있으며, (3) 경계값과 에러 케이스가 누락되어 회귀 방지 능력이 불완전하다는 점이다.

TDD로 이 코드를 다시 작성한다면, `get_temperature`를 먼저 Red-Green-Refactor로 완성하고, `is_hot`은 `get_temperature`를 Mock하여 순수 비교 로직만 테스트하며, 경계값 30도 케이스를 포함하는 순서로 점진적으로 개발할 것을 권고한다.
