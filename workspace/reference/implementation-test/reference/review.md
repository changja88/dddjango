# 코딩 테스트 문서 상충/모순/불일치 의사결정

Internal: `workspace/reference/implementation-test/reference/internal.md`
External: `workspace/reference/implementation-test/reference/external.md`

---

### 1. 테스트 더블 분류 체계

**상충 유형**: 불일치

| | Internal | External |
|---|---------|----------|
| 출처 | 파이썬코딩의기술 (Brett Slatkin) | Unit Testing (Vladimir Khorikov) |
| 주장 | 테스트 더블을 Mock과 Fake 2가지로 분류 | Dummy, Stub, Spy, Mock, Fake 5가지로 분류 |

**Internal 근거**: Mock은 요청에 따라 적절한 응답을 돌려주는 것이고, Fake는 기능을 대부분 제공하지만 더 단순한 구현을 사용하는 것(예: 메모리 내 데이터베이스)이다. Python 실무에서는 이 두 가지 구분만으로 충분하다는 입장이다.

**External 근거**: Dummy(빈 값 전달용), Stub(미리 정해진 값 반환), Spy(호출 기록), Mock(호출 검증), Fake(간소화된 실제 구현)로 5가지를 정확히 구분해야 한다. 테스트 의도를 정확히 전달하고 Mock 오남용을 방지하기 위해 세밀한 분류가 필요하다는 입장이다.

**추천**: External ▶ (5가지 분류가 테스트 의도를 명확히 전달하고, Mock과 Stub의 혼용을 방지하므로 개념적 정확성이 높다)

---

### 2. 시간 모킹 방법

**상충 유형**: 상충

| | Internal | External |
|---|---------|----------|
| 출처 | 파이썬코딩의기술 (Brett Slatkin) | freezegun/time-machine 공식 문서 |
| 주장 | monkeypatch.setattr로 datetime을 직접 교체 | 전용 라이브러리(freezegun/time-machine)를 사용 |

**Internal 근거**: pytest 내장 monkeypatch 픽스처로 `datetime` 모듈을 Mock 객체로 교체한다. 외부 의존성 없이 순수 pytest만으로 시간 모킹이 가능하며, `monkeypatch.setattr("myapp.utils.datetime", Mock(now=Mock(return_value=fake_now)))` 패턴을 사용한다.

**External 근거**: monkeypatch 방식은 패치 대상 모듈 경로를 정확히 지정해야 하고, 여러 모듈에서 datetime을 import하면 누락이 발생한다. freezegun/time-machine은 전역적으로 시간 함수를 교체하므로 누락 없이 일관되게 동작하고, 시간 흐름 시뮬레이션(`tick`), 시간 이동(`move_to`/`shift`) 등 고급 기능을 제공한다. time-machine은 C 확장으로 100~200배 빠르다.

**추천**: External ▶ (monkeypatch는 패치 누락 위험이 크고, 전용 라이브러리가 안전성/기능/성능 모두 우위)

---

### 3. Mock 사용 범위에 대한 관점

**상충 유형**: 모순

| | Internal | External |
|---|---------|----------|
| 출처 | 파이썬코딩의기술 (Brett Slatkin) | Codepipes Blog / Unit Testing (Khorikov) |
| 주장 | 의존성 주입 + Mock을 적극 활용하여 테스트를 쉽게 만들어라 | 과도한 Mock은 안티패턴("Mockery")이며 외부 의존성만 Mock해야 한다 |

**Internal 근거**: 테스트 코드를 이해하기 어렵다면 더 나은 추상화로 Mock을 쉽게 작성해야 한다. 의존 관계를 주입받도록 설계를 개선하면 모든 의존성을 Mock으로 대체할 수 있어 테스트가 단순해진다. DB, 이메일 등 모든 의존성을 Mock 처리하는 패턴을 "좋음"으로 제시한다.

**External 근거**: 너무 많은 Mock으로 실제 시스템을 전혀 테스트하지 않게 되는 "Mockery" 안티패턴을 경고한다. 6개의 Mock을 사용하는 테스트는 "실제로 뭘 테스트하는 건지" 의문이라며, 외부 의존성(결제 게이트웨이 등)만 Mock하고 핵심 로직은 실제로 실행해야 한다고 주장한다.

**추천**: 병합 (의존성 주입으로 테스트 용이성을 확보하되, Mock은 외부 의존성에 한정하고 핵심 비즈니스 로직은 실제 객체로 테스트)

---

### 4. 테스트 내 다중 Assert 허용 여부

**상충 유형**: 불일치

| | Internal | External |
|---|---------|----------|
| 출처 | 파이썬코딩의기술 (Brett Slatkin) | Clean Code (Robert C. Martin) / Bill Wake |
| 주장 | 하나의 테스트에서 관련된 여러 assert를 자유롭게 사용 | Act은 반드시 한 줄, 여러 AAA 블록은 별도 테스트로 분리 |

**Internal 근거**: `test_assertions()` 예제에서 동등성, 포함, 예외, 근사값 검증을 하나의 테스트 함수에 나열하며, 관련된 검증을 한 곳에 모아 보여주는 패턴을 제시한다. Mock 검증에서도 `assert_called_once_with` 뒤에 `assert "25.0" in result`를 연달아 사용한다.

**External 근거**: AAA(Arrange-Act-Assert) 패턴에서 Act 섹션은 단일 함수 호출이어야 하고, 하나의 테스트에 여러 Act-Assert 쌍이 있으면 반드시 분리해야 한다. "Free Ride" 안티패턴으로 관련 없는 assert 추가를 경고하고, 각 테스트가 정확히 하나의 동작만 검증해야 한다고 주장한다.

**추천**: 병합 (동일한 Act에 대한 여러 assert는 허용하되, 서로 다른 Act-Assert 쌍은 별도 테스트로 분리)

---

### 5. 화이트박스 테스트에 대한 프레이밍

**상충 유형**: 불일치

| | Internal | External |
|---|---------|----------|
| 출처 | 테스트주도 개발 (Kent Beck) | Codepipes Blog / DZone |
| 주장 | 화이트박스 테스트 욕구는 "설계 문제"이므로 설계를 고쳐야 한다 | 구현 세부사항에 결합하는 것은 "테스트 안티패턴(The Inspector)"이다 |

**Internal 근거**: 화이트박스 테스트를 바라는 것은 테스팅 문제가 아니라 설계 문제다. public 프로토콜만을 이용해서 테스트를 작성해야 한다. 내부 구현을 들여다봐야 한다면, 그것은 인터페이스 설계가 잘못된 것이므로 프로덕션 코드의 설계를 개선해야 한다.

**External 근거**: 내부 구현에 결합된 테스트("The Inspector")는 리팩토링할 때마다 깨진다. 정렬 알고리즘이 quicksort인지 spy로 검증하는 대신, 결과가 정렬되어 있는지만 검증해야 한다. 이것은 테스트 작성 기법의 문제로 프레이밍한다.

**추천**: 병합 (두 관점 모두 "구현 세부사항에 결합하지 말라"는 결론은 동일하나, Internal처럼 설계를 먼저 의심하고, External처럼 테스트 기법도 함께 개선하는 양면 접근이 가장 효과적)
