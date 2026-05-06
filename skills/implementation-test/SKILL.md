---
name: implementation-test
description: >
  This skill should be used when the user asks to "write tests",
  "write pytest code", "add test coverage", "create fixtures",
  "mock dependencies", "write integration tests", "use Hypothesis",
  "use factory_boy", "set up testcontainers", "configure coverage",
  "improve test quality", "fix flaky tests", or when any Python
  test code writing, review, or refactoring task occurs. Covers
  pytest, fixtures, test doubles, property-based testing, test data
  factories, time/HTTP mocking, Docker integration tests, coverage,
  mutation testing, and BDD. For TDD methodology (Red-Green-Refactor),
  see implementation-tdd. For general clean code principles, see
  implementation-cleancode.
---

# Python 테스트 코드 원칙

테스트 코드는 프로덕션 코드이다 -- 동일한 품질과 주의를 요구한다.
테스트의 지배적인 비용은 작성이 아니라 유지보수이다.
여기의 모든 원칙은 하나의 목표를 위해 존재한다: 구현이 변경되어도
깨지지 않으면서 실제 버그를 잡는 테스트를 작성하는 것.

TDD 방법론(Red-Green-Refactor)은 implementation-tdd를 참조한다.
언어에 구애받지 않는 클린 코드 원칙은 implementation-cleancode를 참조한다.
Python 특화 컨벤션(타입 힌트, dataclasses 등)은 implementation-python을 참조한다.
Django 특화 테스트 컨벤션(TestCase, pytest-django)은 implementation-django를 참조한다.

**비-Django 테스트 정밀도 가드.** 사용자가 FastAPI, 일반 Python, CLI,
라이브러리 테스트처럼 Django와 무관한 테스트를 명확히 요청하면 Django,
DDD, dddjango, pytest-django, Django settings 구조로 끌고 가지 않는다. 이런
응답에는 dddjango 스킬 체계의 `관련 스킬 참조` 섹션을 붙이지 않는다. 필요한
경우 pytest, TestClient, fixture 등 해당 프레임워크에 맞는 테스트만 제시한다.

## 세 가지 핵심 원칙
1. 모든 테스트는 명확한 Arrange-Act-Assert 구조를 통해 하나의 동작을 검증한다.
2. 모든 테스트는 독립적이다 -- 테스트 간 공유 가변 상태가 없어야 한다.
3. 외부 의존성만 Mock한다; 핵심 로직은 실제 객체로 테스트한다.

다른 모든 원칙은 이 세 가지를 위해 존재한다.

## 응답 구조

사용자가 Django/dddjango 맥락에서 테스트를 요청한 경우 응답은 다음 구조를 따른다:

1. **[주요 내용]** -- 모드에 따른 코드, 리뷰, 리팩터링 결과
2. **[관련 스킬 참조]** -- 사용자의 다음 단계를 안내하는 연결점

이 스킬은 11개의 상호 연결된 스킬 체계의 일부이다.
사용자는 현재 작업 후 어떤 스킬을 호출해야 하는지 모르는 경우가
많으므로, 관련 스킬 참조가 워크플로우의 자연스러운 연결을 만든다.
단, 명확한 비-Django 요청에서는 이 섹션을 생략한다.

When the closing section is applicable, use this exact template:
```
---
> **관련 스킬 참조:**
> - [topic] → **[skill-name]** 스킬
```

## 운영 모드

사용자의 요청에 따라 모드를 선택한다:
- **Writing**: 사용자가 테스트 코드를 생성, 구현 또는 작성하도록 요청
- **Review**: 사용자가 기존 테스트 코드를 리뷰, 검토 또는 평가하도록 요청
- **Refactoring**: 사용자가 기존 테스트 코드를 리팩터링, 개선 또는 정리하도록 요청

의도가 모호한 경우, Writing 모드를 기본으로 한다.

요청이 여러 모드에 걸치는 경우(예: "리뷰하고 리팩터링해줘"), 같은 코드에 대해 Review를 먼저 적용한 후 Refactoring을 적용한다.

### Writing 모드

새로운 테스트 코드를 생성할 때, 모든 원칙을 묵시적으로 적용한다. 원칙을
설명하는 인라인 주석 없이 깔끔한 테스트를 생성한다. 테스트가 스스로 말하게 한다.
검증하는 시나리오를 설명하는 독스트링을 복잡한 테스트 함수에 항상 작성한다.

테스트 코드를 생성하기 전에, 상세한 규칙을 적용하기 위해 관련 주제 영역의 레퍼런스 파일을 읽는다.

**빈 workspace / read-only fallback.** 프로젝트 파일이 없거나 읽기 전용이라
테스트 파일 생성 또는 pytest 실행이 불가능해도 테스트 작성 요청을 중단하지
않는다. 실행했다고 주장하지 않는다. 대신 다음 산출물을 제공한다:

1. **RED 테스트 예시** -- `tests/isolated/...` 아래에 둘 수 있는 pytest 코드.
2. **예상 실패 이유** -- 아직 구현되지 않은 함수, 서비스, repository, 예외
   때문에 실패해야 하는 이유.
3. **GREEN 최소 구현** -- 테스트를 통과시키는 최소 코드 스케치.
4. **REFACTOR 방향** -- fixture, fake repository, domain service, 예외 타입을
   정리하는 방향.
5. **실행 명령** -- `pytest ... -q` 형태의 실제 실행 명령.

실제 실행 여부와 예시 산출물을 구분한다. 실행하지 못했다면 통과했다고 말하지
말고, 사용자가 실제 프로젝트에서 실행할 다음 명령을 제시한다.

적용할 핵심 컨벤션:

**테스트 구조.** 모든 테스트는 AAA를 따른다: Arrange(설정), Act(단일 행동),
Assert(결과 검증). Act 섹션은 한 줄이다. 여러 AAA 블록은 별도의 테스트를
의미한다. 동일한 Act에 대한 관련 어설션은 허용된다.

**디렉토리 구조.** 테스트 디렉토리는 두 축으로 분리한다 -- 1차 축은 **실행 환경**,
2차 축은 **범위**이다. 환경 축이 범위 축보다 항상 위에 온다.

- `tests/isolated/` -- **통제된/제공된 테스트 환경**에서 수행하는 테스트.
  외부 의존성을 Fake/Mock/in-memory 또는 testcontainers 같은 제공된
  인프라로 대체한다. 네트워크 호출이 차단되고 시계가 고정되어 결정적이며,
  CI 기본 스위트로 항상 실행된다.
- `tests/real/` -- **실제 운영 환경**(또는 운영과 동등한 인프라)에서 수행하는
  테스트. 실 DB, 실 외부 서비스에 붙어 배포 직전 통합을 검증한다. 사전 환경
  셋업이 필요하므로 별도 게이트(예: pre-deploy)로 실행한다.

각 환경 아래에 범위(`unit/`, `integration/`, 필요 시 `e2e/`)를 둔다. 환경 축을
1차로 두는 이유는 격리 보장과 실행 정책(CI 항상 vs 사전 셋업 필요)이 범위보다
앞서 결정되기 때문이다. 둘을 섞은 평면 `tests/unit/`, `tests/integration/`은
회귀 -- 같은 `integration/`에 isolated와 real이 섞여 격리가 깨진다.

**Django 프로젝트의 isolated 환경.** Django 프로젝트에서 `tests/isolated/`는
운영 settings가 아닌 **별도의 테스트 settings 모듈**(예: `config/settings/test.py`)
에서 실행한다. 이 settings는 외부 의존성을 모두 제공된 더블로 교체한다 --
`DATABASES`는 SQLite in-memory 또는 testcontainers PostgreSQL,
`EMAIL_BACKEND`는 `django.core.mail.backends.locmem.EmailBackend`,
`CACHES`는 `LocMemCache`, `CELERY_TASK_ALWAYS_EAGER = True`와 `CELERY_BROKER_URL = "memory://"`,
`STORAGES`/`MEDIA_ROOT`는 tmp_path 기반,
`PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]`(테스트 속도).
실행 시 `DJANGO_SETTINGS_MODULE=config.settings.test`를 pytest 환경에 주입한다
(pyproject.toml의 `[tool.pytest.ini_options]`에 `DJANGO_SETTINGS_MODULE` 또는
`tests/isolated/conftest.py`에서 설정). 운영 settings로 isolated 테스트를 돌리는 것은
회귀 -- 운영 DB/SMTP/Celery 브로커가 잘못 깨어날 수 있다. `tests/real/`는
별도의 `config/settings/test_real.py`(또는 stage settings)로 실행해 환경을 명시적으로 분리한다.

> Django 특화 디테일(TestCase 선택, pytest-django 마크, Factory Boy)은
> implementation-django의 references/testing.md를 따른다.

**픽스처.** 설정/정리에 yield가 있는 pytest 픽스처를 사용한다. 스코프를
신중하게 선택한다: 격리를 위한 function(기본값), 비용이 큰 리소스를 위한
module/session. 공유 픽스처에는 conftest.py 계층을 사용하며, 환경별 강제
규칙(isolated에서 네트워크/시계 차단, real에서 실 DB 연결)은 각 환경의
conftest.py에 둔다.

**검증 우선순위.** 출력 기반 검증(반환 값에 대한 assert)을 상태 기반(객체
상태에 대한 assert)보다, 상태 기반을 커뮤니케이션 기반(mock.assert_called)
보다 선호한다. 외부 의존성(결제, 이메일 등)만 Mock한다.

**테스트 데이터.** 복잡한 객체 그래프에 factory_boy를 사용한다. 순수 함수와
데이터 구조에 대한 속성 기반 테스트에 Hypothesis를 사용한다. 단순한 데이터 주도
테스트에 parametrize를 사용한다. 테스트가 일반적인 변이를 잡을 수 있도록
비교 연산자(< vs <=, > vs >=)에서 경계 값을 고려한다.

**외부 의존성.** 시간 모킹에 time-machine을 사용한다(freezegun보다
100-200배 빠름). HTTP 모킹에 responses/aioresponses를 사용한다.
실제 서비스 통합 테스트에 testcontainers를 사용한다.

### Review 모드

잘 구조화된 테스트 코드를 리뷰할 때는, 개선사항을 나열하기 전에 테스트가
잘한 점을 먼저 언급한다. 품질이 낮은 테스트 코드를 리뷰할 때는, 가장
영향력 있는 이슈에 먼저 집중한다.

각 발견사항의 형식:

```
[Principle] -- 테스트 신뢰성이나 유지보수성을 해치는 이유 설명
```

리뷰를 확정하기 전에, 아래의 모든 항목을 검증한다. 누락된 항목은 사용자가 나중에 직접 발견해야 하므로 모두 확인한다.
- [ ] 관련 스킬 참조 포함 -- 사용자의 다음 워크플로우를 위한 스킬 연결
- [ ] 별도 테스트여야 하는 여러 Act 섹션이 있는 테스트
- [ ] 테스트 간 공유 가변 상태 (전역 변수, 클래스 속성)
- [ ] Mock 남용 -- 실제 객체 대신 핵심 비즈니스 로직을 Mock
- [ ] Mock 객체에 spec/autospec 누락 (존재하지 않는 메서드 호출 허용)
- [ ] 시간, 순서 또는 외부 서비스에 의존하는 불안정한 테스트
- [ ] 다른 데이터로 반복되는 테스트 케이스에 parametrize 누락
- [ ] 테스트 의도를 가리는 과도한 설정
- [ ] 동작 대신 구현 세부사항에 대한 Assert (The Inspector)
- [ ] 의미 있는 어설션이 없는 테스트 (The Liar / Secret Catcher)
- [ ] 잘못된 테스트 수준 -- 단위 테스트로 검증 가능한 것에 E2E, 또는 그 반대

리뷰 결과를 확정하기 전에, 인용된 모든 원칙의 레퍼런스를 읽어 정확성을 확인한다.

### Refactoring 모드

리팩터링할 때는 변경 전/후를 보여주고 각 변경의 이유를 명시한다.
각 변경을 특정 원칙에 연결하여 근거를 추적 가능하게 한다.
각 변경의 형식:

```
[Before]
<원래 코드>

[After]
<개선된 코드>

[Reason] Principle -- 이 변경이 테스트를 개선하는 이유 설명
```

변경사항을 제시하기 전에, 아래의 모든 적용 가능한 개선사항을 적용한다. 적용 가능한 항목을 건너뛰면 사용자가 추가 리팩토링을 해야 하므로 모두 적용한다.
- [ ] 관련 스킬 참조 포함 -- 사용자의 다음 워크플로우를 위한 스킬 연결
- [ ] 여러 Act 섹션 -> 별도 테스트로 분리
- [ ] 공유 가변 상태 -> 픽스처로 격리
- [ ] 과도하게 Mock된 테스트 -> Mock을 Fake나 실제 객체로 교체
- [ ] spec 없는 Mock -> spec 추가 또는 create_autospec 사용
- [ ] 시간 의존 테스트 -> time-machine/freezegun 적용
- [ ] 반복적인 테스트 케이스 -> parametrize로 추출
- [ ] 복잡한 설정 -> 픽스처나 팩토리로 추출
- [ ] 구현에 결합된 어설션 -> 동작을 검증하도록 재작성
- [ ] 비어 있거나 약한 어설션 -> 의미 있는 검증 추가
- [ ] 잘못 배치된 테스트 수준 -> 적절한 수준으로 이동

변경사항을 제시하기 전에, 적용된 각 패턴의 레퍼런스를 읽는다.

형식이 개선의 깊이를 제한하지 않도록 한다. 테스트 코드에 근본적인 재설계가
필요한 경우, 전체 재설계를 먼저 적용한 후 위의 형식으로 변경사항을
제시한다. 개별 변경 후, 사용자가 전체 구조를 파악할 수 있도록
**완전한 리팩터링된 코드**를 제공한다.

---

## 응답 작성 직전 체크리스트 (필수)

다음 항목을 모두 점검한다. 누락 시 응답 작성 전에 보강한다.

### 작성/리뷰/리팩토링 공통
- [ ] 시간 모킹은 time-machine을 기본으로 사용 (freezegun 대비 100-200배 빠른 C 확장 -- pytest-codspeed 벤치 인용)
- [ ] HTTP 외부 호출이 있는 코드는 responses 라이브러리 또는 httpretty/respx로 모킹
- [ ] Mock 객체에는 spec= 또는 create_autospec으로 인터페이스 강제
- [ ] Repository/Gateway 같은 의존성은 InMemoryRepository Fake 클래스로 교체 (MagicMock 남발 = Mockery 안티패턴)
- [ ] fixture는 conftest.py로 추출하여 여러 테스트 모듈에서 공유 (function 스코프 기본)
- [ ] 경계값 테스트는 mutation testing(mutmut, cosmic-ray) 관점에서 boundary +/-1 케이스 포함
- [ ] pytest-randomly로 테스트 순서 무작위화하여 격리 검증

### 작성 모드 추가
- [ ] **fixture는 yield 기반 setup/teardown 패턴 사용 (`yield resource; resource.cleanup()`)**
- [ ] **HTTP 모킹은 `@responses.activate` 데코레이터 + `responses.add(method, url, json=...)` 실제 코드 사용**
- [ ] **Hypothesis property-based test에 `@example()` 데코레이터로 회귀 케이스 명시 추가**

### 리뷰 모드 추가
- [ ] Mockery (모든 의존성을 MagicMock으로 처리) 안티패턴 지적 + InMemoryFake 권고
- [ ] 외부 네트워크 호출 미모킹 시 responses/httpretty 권고
- [ ] mutation testing 관점에서 약한 assertion(>=, <= 만 검증, 경계 미검증) 지적
- [ ] **테스트 setup이 5줄 이상 또는 다중 객체 생성 시 Excessive Setup 안티패턴으로 지적 + Builder/Factory 권고**
- [ ] **HTTP 외부 호출 미모킹 시 `@responses.activate` + `responses.add` 코드 예시로 권고 (말로만이 아닌)**
- [ ] **`mock.send.assert_called_once_with(expected_args)` 형태로 호출 인자 검증 누락을 직접 지적 (assert_called만이 아닌)**

### 리팩토링 모드 추가
- [ ] conftest.py로 fixture 이동 + 여러 테스트 모듈 공유 가능하게 재배치
- [ ] 경계값 (예: 박수 1 vs 2, 요금 999 vs 1000) parametrize로 확장
- [ ] InMemoryRepository Fake 클래스 정의 + Mock(spec=...) 또는 raw MagicMock을 모두 교체
- [ ] mutation testing으로 살아남는 mutant 0이 되도록 boundary 케이스 추가
- [ ] pytest-randomly와 호환되는 테스트 격리 (fixture function 스코프, monkeypatch 사용)
- [ ] **fixture를 yield 기반 setup/teardown 패턴으로 전환**

### 잔여 디테일 정밀도 (회귀 방지 — 절대 누락 금지)

다음 3개 항목은 평면 디렉토리, "time-machine을 쓰자"는 단순 권고, 모호한 시간 단위로 회귀하기 쉽다. 반드시 아래의 정확한 형태로 작성한다.

- [ ] **작성 모드에서 테스트 디렉토리는 1차 축이 실행 환경(`tests/isolated/`, `tests/real/`), 2차 축이 범위(`unit/`, `integration/`, 필요 시 `e2e/`)인 2단계 계층 구조로 명시. `tests/isolated/`는 통제된/제공된 테스트 환경(Fake, Mock, in-memory, testcontainers, 네트워크 차단, 시계 고정), `tests/real/`은 실제 운영 환경(실 DB, 실 외부 서비스)으로 의미를 명시한다. pyproject.toml의 pytest testpaths에 `["tests/isolated", "tests/real"]` 두 디렉토리를 모두 등록하는 코드를 제시하고, 환경별 강제 규칙(isolated에서 네트워크/시계 차단 autouse, real에서 실 DB 연결 픽스처)은 각 환경의 `conftest.py`에 두는 예시를 함께 제시한다. 다음은 모두 회귀: 단일 평면 `tests/`, 환경 축이 누락된 `tests/unit/`/`tests/integration/`만 사용, isolated/real 의미 정의 누락, testpaths에 두 디렉토리 모두 등록 누락.**
- [ ] **Django 프로젝트라면 `tests/isolated/`는 별도의 테스트 settings 모듈(`config/settings/test.py`)에서 실행되며, 이 settings는 외부 의존성을 차단한다 -- `DATABASES`는 SQLite in-memory 또는 testcontainers, `EMAIL_BACKEND`는 `locmem`, `CACHES`는 `LocMemCache`, `CELERY_TASK_ALWAYS_EAGER=True`, `CELERY_BROKER_URL="memory://"`, `PASSWORD_HASHERS`는 `MD5PasswordHasher`. `DJANGO_SETTINGS_MODULE=config.settings.test`를 pyproject.toml `[tool.pytest.ini_options]`의 `DJANGO_SETTINGS_MODULE` 또는 `tests/isolated/conftest.py`에서 설정한다. `tests/real/`은 별도의 `config/settings/test_real.py`(또는 stage settings)로 실행한다. 운영 settings로 isolated 테스트를 돌리는 것은 회귀.**
- [ ] **time-machine 권고 시 반드시 다음 정확한 근거를 함께 인용: "freezegun은 순수 Python 구현인 반면 time-machine은 C 확장으로 구현되어 있어 동일 작업에서 100~200배 빠름. 시간 모킹이 많은 테스트 스위트에서 실질적인 실행 시간 차이가 발생". 단순히 "time-machine이 더 빠르다", "time-machine을 쓰자"는 회귀 표현. 작성/리뷰/리팩토링 모드 어디서든 동일 근거 명시.**
- [ ] **리팩토링 모드에서 시간 단위는 **'밀리초 단위'** 또는 **'마이크로초 단위'** 같은 구체 명시(초/분 모호 표현 금지). 테스트 순서 무작위화 도구는 반드시 패키지 이름 **`pytest-randomly`** 를 명시 (단순 "테스트 순서를 랜덤으로 실행하세요"는 회귀). 두 항목 모두 코드/명령 예시(예: `pip install pytest-randomly`, `pytest --randomly-seed=last`)로 제시.**

---

## 1. 테스트 전략

테스트 피라미드: ~80% 단위, ~15% 통합, ~5% E2E (Google 비율).
상위 수준 테스트에서 버그를 발견하면, 먼저 단위 테스트를 작성한다.
Google SMURF: Speed, Maintainability, Utilization, Reliability, Fidelity.
테스트 크기(Small/Medium/Large)가 테스트 유형 라벨보다 중요하다.

> Reference: `references/test-strategy.md`

---

## 2. 테스트 더블과 검증

Meszaros의 5가지 유형: Dummy, Stub, Spy, Mock, Fake. 테스트 의도를
전달하기 위해 정확한 용어를 사용한다. 검증 우선순위: 출력 기반 >
상태 기반 > 커뮤니케이션 기반. 외부 의존성만 Mock한다;
저장소와 내부 협력자에는 Fake를 사용한다.

> Reference: `references/test-doubles.md`

---

## 3. pytest 픽스처와 어설션

설정/정리에 yield가 있는 pytest 픽스처를 사용한다. 리소스 비용에 따라
스코프를 지정한다: 격리를 위한 function, 비용이 큰 리소스를 위한
module/session. 공유를 위해 conftest.py 계층을 사용한다.
깔끔한 어설션을 위해 `pytest.raises`, `pytest.approx`, parametrize를 사용한다.

> Reference: `references/pytest-fixtures.md`

---

## 4. pytest 설정과 마커

pyproject.toml에서 설정한다: testpaths, strict-markers, strict-config.
이유와 함께 내장 마커(skip, skipif, xfail)를 사용한다. 오타를 방지하기
위해 커스텀 마커를 등록한다. 동적 동작을 위해 conftest 훅을 사용한다.

> Reference: `references/pytest-configuration.md`

---

## 5. pytest 플러그인 생태계

병렬 실행을 위한 pytest-xdist(비용이 큰 픽스처에 loadscope).
비동기 테스트를 위한 pytest-asyncio(auto 모드 권장). 커버리지를 위한
pytest-cov. 순서 독립성을 위한 pytest-randomly. 무한 실행 테스트를
위한 pytest-timeout.

> Reference: `references/pytest-plugins.md`

---

## 6. Mock 패턴

API 드리프트를 잡기 위해 `Mock(spec=...)` 또는 `create_autospec`을
사용한다. 설정되지 않은 속성 접근을 방지하기 위해 `seal()`을 사용한다.
비동기 함수에 `AsyncMock`을 사용한다. 동적 응답과 오류 시뮬레이션에
`side_effect`를 사용한다. 더 쉬운 모킹을 위해 의존성을 캡슐화한다.

> Reference: `references/mock-patterns.md`

---

## 7. 속성 기반 테스트 (Hypothesis)

특정 예제 대신 속성(불변식)을 정의한다. Hypothesis가 자동으로 수백 개의
입력을 생성한다. 데이터 생성에 strategy를 사용하고, 경계 값에 `@example`을
사용한다. 가변 상태가 있는 시스템에 stateful testing을 사용한다.

> Reference: `references/property-based-testing.md`

---

## 8. 테스트 데이터 팩토리 (factory_boy)

선언적 테스트 데이터 생성에 factory_boy를 사용한다. 고유 값에 Sequence,
현실적인 데이터에 Faker, 계산된 필드에 LazyAttribute를 사용한다.
객체 변형에 Trait을 사용한다. 관계에 SubFactory를 사용한다.
SQLAlchemy와 Django ORM과 통합된다.

> Reference: `references/test-data-factory.md`

---

## 9. 시간 모킹

CPython 프로젝트에서는 freezegun보다 time-machine(C 확장, 100-200배
빠름)을 선호한다. 데코레이터 또는 컨텍스트 매니저를 사용한다. 시간
진행에 `traveller.shift()`를 사용한다. 재사용성을 위해 pytest 픽스처로
사용한다.

> Reference: `references/time-mocking.md`

---

## 10. HTTP 모킹

requests 라이브러리에 responses를, aiohttp에 aioresponses를 사용한다.
json/status와 함께 예상 URL을 등록한다. 동적 응답에 callback을 사용한다.
`body=ConnectionError(...)`로 오류를 시뮬레이션한다. 사용하는 HTTP
클라이언트에 따라 라이브러리를 선택한다.

> Reference: `references/http-mocking.md`

---

## 11. 통합 테스트 (testcontainers)

실제 Docker 기반 서비스 테스트에 testcontainers를 사용한다. 컨테이너
생명주기에 session 스코프, 트랜잭션 롤백을 통한 테스트 격리에 function
스코프를 사용한다. PostgreSQL, Redis, Kafka 등을 지원한다.

> Reference: `references/integration-testing.md`

---

## 12. 커버리지와 멀티 환경

pyproject.toml에서 커버리지를 설정한다: source, branch, fail_under,
exclude 패턴. 다중 버전 테스트에 tox(선언적 TOML) 또는 nox(Python 코드)를
사용한다. 브랜치 커버리지는 테스트되지 않은 조건문을 잡는다.

> Reference: `references/coverage-multienv.md`

---

## 13. 테스트 품질과 안티패턴

FIRST: Fast, Independent, Repeatable, Self-validating, Timely. AAA:
단일 Act 줄로 Arrange-Act-Assert. 주요 안티패턴: The Liar,
Excessive Setup, The Inspector, Mockery, Free Ride. 화이트박스
테스트를 피한다 -- 구현이 아닌 동작을 검증한다.

> Reference: `references/test-quality.md`

---

## 14. 변이 테스트 (mutmut)

작은 코드 변이를 도입하고 테스트가 이를 잡는지 검증한다. 유형:
산술, 비교, 논리, 상수, 문장 삭제. 80% 이상의 변이 점수를 목표로 한다.
살아남은 변이체를 분석하여 테스트 갭을 찾는다, 특히 경계 조건에서.

> Reference: `references/mutation-testing.md`

---

## 15. BDD (pytest-bdd)

비즈니스가 읽을 수 있는 명세를 위해 .feature 파일에 Given-When-Then을
사용한다. pytest-bdd로 구현한다: parser와 함께 @given, @when, @then.
단계 데이터 전달에 target_fixture를 사용한다.

> Reference: `references/bdd.md`
