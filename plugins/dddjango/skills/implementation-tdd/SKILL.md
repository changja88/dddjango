---
name: implementation-tdd
description: >
  This skill should be used when the user asks to "develop with TDD",
  "write tests first", "use Red-Green-Refactor", "apply test-driven
  development", "guide me through TDD", "review TDD practices",
  "implement using TDD cycle", or when any task involves developing
  code through test-first methodology. Also use for Django/pytest TDD
  prompts, Korean prompts mentioning 쿠폰, 실패 테스트, or Red-Green-Refactor,
  and empty workspace or read-only fallback situations where examples must
  still be provided without claiming execution. Covers Red-Green-Refactor,
  classical vs London school, unit test quality, red/green bar patterns,
  Outside-In TDD, refactoring, test smells, and AI coding. For pytest,
  fixtures, or mocks, see implementation-test; for clean code, see
  implementation-cleancode.
---

# TDD 개발 방법론

TDD는 테스트를 프로덕션 코드보다 먼저 작성하여 **동작하는 깔끔한 코드**를
만드는 개발 방법론이다. 소프트웨어의 비용은 유지보수가 지배하며,
TDD는 개발의 부산물로 포괄적인 회귀 테스트 모음을 구축하여 유지보수
비용을 줄인다.

핵심 통찰: "동작하게 만들기"와 "올바르게 만들기"의 관심사를 분리한다.
먼저 동작하게 만들고(Green), 그 다음 올바르게 만든다(Refactor).

테스트 코드 기법(pytest, 픽스처, 모킹)은 implementation-test를 참조한다.
언어에 구애받지 않는 클린 코드 원칙은 implementation-cleancode를 참조한다.
Python 특화 컨벤션은 implementation-python을 참조한다.
Django 특화 테스트 컨벤션(TestCase, pytest-django)은 implementation-django를 참조한다.

## 세 가지 핵심 원칙
1. 프로덕션 코드를 작성하기 전에 실패하는 테스트를 먼저 작성한다.
2. 실패하는 테스트를 통과시키기에 충분한 만큼만 프로덕션 코드를 작성한다.
3. 모든 테스트가 통과할 때만 리팩터링한다.

다른 모든 원칙은 이 세 가지를 위해 존재한다.

## 응답 구조

모든 응답은 다음 구조를 따른다:

1. **[주요 내용]** -- 모드에 따른 코드, 리뷰, 리팩터링 결과
2. **[관련 스킬 참조]** -- 사용자의 다음 단계를 안내하는 연결점

이 스킬은 11개의 상호 연결된 스킬 체계의 일부이다.
사용자는 현재 작업 후 어떤 스킬을 호출해야 하는지 모르는 경우가
많으므로, 관련 스킬 참조가 워크플로우의 자연스러운 연결을 만든다.

ALWAYS use this exact template for the closing section:
```
---
> **관련 스킬 참조:**
> - [topic] → **[skill-name]** 스킬
```

## 운영 모드

사용자의 요청에 따라 모드를 선택한다:
- **Writing**: 사용자가 TDD를 사용하여 개발, 구현 또는 빌드하도록 요청
- **Review**: 사용자가 TDD 실천 방식이나 테스트 품질을 리뷰하도록 요청
- **Refactoring**: 사용자가 테스트 구조나 TDD 워크플로우를 개선하도록 요청

의도가 모호한 경우, Writing 모드를 기본으로 한다.

요청이 여러 모드에 걸치는 경우(예: "리뷰하고 리팩터링해줘"),
같은 코드에 대해 Review를 먼저 적용한 후 Refactoring을 적용한다.

### Writing 모드

TDD로 개발할 때, 사용자를 Red-Green-Refactor 사이클을 통해 안내한다.
모든 TDD 원칙을 묵시적으로 적용한다. 방법론을 설명하는 인라인 주석 없이
깔끔한 테스트와 프로덕션 코드를 생성한다.

코드를 생성하기 전에, 관련 주제 영역의 레퍼런스 파일을 읽는다.

**빈 workspace / read-only fallback.** 프로젝트 파일이 없거나 읽기 전용이라
파일 생성, 수정, pytest 실행을 할 수 없어도 TDD 요청을 중단하지 않는다.
실행했다고 주장하지 않는다. 대신 다음 산출물을 제공한다:

1. **RED 테스트 예시** -- 사용자가 실제 프로젝트에 옮길 수 있는 실패하는
   pytest 테스트 코드.
2. **예상 실패 이유** -- 아직 없는 함수, 서비스, 예외, 모델 동작 때문에
   왜 실패해야 하는지.
3. **GREEN 최소 구현** -- 위 테스트만 통과시키는 최소 프로덕션 코드.
4. **REFACTOR 방향** -- 그린 상태에서 분리할 도메인 객체, 서비스, 예외,
   fixture 개선 방향.
5. **실행 명령** -- 사용자가 실제 프로젝트에서 실행할 pytest 명령.

이 fallback에서도 RED/GREEN/REFACTOR 라벨을 유지한다. 테스트를 실행하지
않았다면 "실행하지 못했습니다"라고 명시하고, 통과했다고 말하지 않는다.

적용할 핵심 원칙:

**Red-Green-Refactor 사이클.** 모든 기능은 실패하는 테스트로 시작한다.
통과하기에 충분한 코드만 작성한다. 그린 바 상태에서 리팩터링한다. 이 사이클은
TDD의 심장 박동이다 -- 절대 단계를 건너뛰지 않는다.

**테스트 선택.** 가장 단순한 경우(빈 입력, 0, null)부터 시작한다.
새로운 것을 가르쳐주고 자신감을 가지고 구현할 수 있는 다음 테스트를 선택한다.
알려진 것에서 미지의 것으로 이동한다.

**그린 바 전략.** 확신이 없을 때 Fake It(상수 반환)을 사용하고,
추상화가 불명확할 때 Triangulation(두 예제가 일반화를 강제)을 사용하며,
해결책이 명확할 때 Obvious Implementation을 사용한다.

**스쿨 선택.** 실제 객체를 사용하는 순수 도메인 로직에는
Classical(Inside-Out)을 사용한다. Mock을 사용하는 외부 시스템 통합에는
London(Outside-In)을 사용한다. 적절할 때 둘 다 혼합한다.

**테스트 품질.** 모든 테스트는 네 가지 기둥을 만족한다: 회귀 보호,
리팩터링 내성, 빠른 피드백, 유지보수성. 출력 기반 > 상태 기반 >
커뮤니케이션 기반 검증을 선호한다.

### Review 모드

TDD 실천 방식을 리뷰할 때는, 개선사항을 나열하기 전에 코드가
잘한 점을 먼저 언급한다. 실천 방식이 미흡할 때는, 가장 영향력 있는
이슈에 먼저 집중한다.

각 발견사항의 형식:

```
[Principle] -- TDD 방법론을 위반하는 이유 설명
```

리뷰를 확정하기 전에, 아래의 모든 항목을 검증한다. 누락된 항목은 사용자가 나중에 직접 발견해야 하므로 모두 확인한다.
- [ ] 관련 스킬 참조 포함 -- 사용자의 다음 워크플로우를 위한 스킬 연결
- [ ] 프로덕션 코드 이후에 테스트 작성 (테스트 우선이 아닌 테스트 나중)
- [ ] Red-Green-Refactor 사이클 증거 없음 (점진적 테스트 없이 대규모 구현)
- [ ] 구현 세부사항에 결합된 테스트 (낮은 리팩터링 내성)
- [ ] 내부 협력자에 대한 Mock 남용 (London 스쿨의 잘못된 적용)
- [ ] 테스트 격리 누락 (테스트 간 공유 가변 상태)
- [ ] 테스트 냄새: Assertion Roulette, Erratic Test, Fragile Test, Obscure Test
- [ ] 점진적 개발 없음 (빅뱅 구현)
- [ ] 출력 기반으로 충분한 곳에서 커뮤니케이션 기반 테스트
- [ ] 경계/엣지 케이스 테스트 누락 (불완전한 테스트 목록)
- [ ] 설계를 이끌지 않는 테스트 (사후 테스트)

리뷰 결과를 확정하기 전에, 인용된 모든 원칙의 레퍼런스를 읽는다.

### Refactoring 모드

테스트나 TDD 워크플로우를 리팩터링할 때는, 변경 전/후를 보여주고
각 변경의 이유를 명시한다. 각 변경을 특정 원칙에 연결하여 근거를
추적 가능하게 한다. 각 변경의 형식:

```
[Before]
<원래 코드>

[After]
<개선된 코드>

[Reason] Principle -- TDD 실천을 개선하는 이유 설명
```

변경사항을 제시하기 전에, 아래의 모든 적용 가능한 개선사항을 적용한다. 적용 가능한 항목을 건너뛰면 사용자가 추가 리팩토링을 해야 하므로 모두 적용한다.
- [ ] 관련 스킬 참조 포함 -- 사용자의 다음 워크플로우를 위한 스킬 연결
- [ ] 테스트 나중 코드 -> Red-Green-Refactor 단계로 재구조화
- [ ] 구현에 결합된 테스트 -> 구현이 아닌 동작을 검증하도록 재작성
- [ ] Mock 남용 -> 적절한 곳에서 실제 객체나 Fake로 교체
- [ ] 테스트 격리 누락 -> 픽스처 추출, 공유 상태 제거
- [ ] 테스트 냄새 -> 냄새 카탈로그의 해당 치료법 적용
- [ ] 빅뱅 구현 -> 점진적 TDD 단계로 분해
- [ ] 불명확한 테스트 -> 명확성을 위해 이름 변경 및 재구조화 (AAA 패턴)
- [ ] 엣지 케이스 누락 -> 테스트 목록에서 경계 테스트 추가
- [ ] 커뮤니케이션 기반 테스트 -> 가능한 곳에서 출력 기반으로 변환
- [ ] 약한 어설션 -> 회귀를 잡을 수 있도록 강화

변경사항을 제시하기 전에, 적용된 각 패턴의 레퍼런스를 읽는다.

형식이 개선의 깊이를 제한하지 않도록 한다. 코드에 근본적인 TDD 재설계가
필요한 경우, 전체 재설계를 먼저 적용한 후 위의 형식으로 변경사항을
제시한다. 개별 변경 후, 사용자가 전체 구조를 파악할 수 있도록
**완전한 리팩터링된 코드**를 제공한다.

---

## 응답 작성 직전 체크리스트 (필수)

### 공통
- [ ] 테스트 함수명: `test_<대상>_<조건>_<기대결과>` 형식
- [ ] AAA(Arrange-Act-Assert) 구조 명시
- [ ] 사이클 단계(RED/GREEN/REFACTOR) 라벨링

### 리뷰 모드
- [ ] 요구사항에 누락된 케이스(예: 대기열, 정원 초과 시 처리) 명시적으로 발견·지적
- [ ] 잘한 점 먼저 짚고 개선 사항 제시
- [ ] [원칙: 한 줄] -- 이유 형식
- [ ] **getter/setter 직접 호출 + 외부 if 분기는 Tell Don't Ask 위반 / anemic 모델로 명시 지적**

### 리팩토링 모드
- [ ] 외부 의존성(Repository, Gateway)은 InMemory Fake 클래스 정의 + Protocol/ABC로 DI
- [ ] 함수 반환은 튜플/dict 대신 명시적 결과 타입(`@dataclass(frozen=True) class EnrollmentResult`)
- [ ] Before/After/Reason 형식 일관 적용
- [ ] **테스트 코드만이 아닌 프로덕션 코드 전체 제공** (Service, Repository, Domain Model 모두)
- [ ] 그린 바 유지(리팩토링 중 테스트 깨짐 없음)

---

## 1. TDD 철학

TDD의 목표는 동작하는 깔끔한 코드이다. TDD는 두려움을 관리한다 --
복잡한 문제가 어떻게 끝날지 모르는 합리적인 두려움이다. 결정과 검증
사이의 피드백 간격은 작은 단계를 통해 제어된다.

> Reference: `references/tdd-philosophy.md`

---

## 2. Red-Green-Refactor 사이클

Red: 작은 실패하는 테스트를 작성한다. Green: 최소한의 코드로 통과시킨다.
Refactor: 그린 바 상태에서 중복을 제거한다. 이 분할 정복 접근법은
"동작"을 먼저 해결한 후 "깔끔함"을 해결한다.

> Reference: `references/red-green-refactor.md`

---

## 3. TDD 스쿨: Classical vs London

Classical (Detroit): 실제 객체, 상태 검증, Inside-Out.
London (Mockist): 협력자에 대한 Mock, 동작 검증, Outside-In.
컨텍스트에 따라 선택한다 -- 순수 도메인 로직은 Classical을,
외부 의존성은 London을 선호한다.

> Reference: `references/tdd-schools.md`

---

## 4. 좋은 단위 테스트의 네 가지 기둥

Khorikov의 네 가지 기둥: 회귀 보호, 리팩터링 내성, 빠른 피드백,
유지보수성. 처음 세 가지는 상호 배타적이다(CAP과 유사). 출력 기반 >
상태 기반 > 커뮤니케이션 기반을 선호한다.

> Reference: `references/unit-test-pillars.md`

---

## 5. Red Bar 패턴

테스트를 작성할 시점: 테스트 목록을 유지하고, 새로운 것을 가르쳐주는
다음 테스트를 선택하며, 가장 단순한 경우(null 연산)부터 시작하고,
테스트를 설명으로 활용한다.

> Reference: `references/red-bar-patterns.md`

---

## 6. Green Bar 패턴

테스트를 통과시키는 방법: Fake It(상수를 반환한 후 일반화),
Triangulation(두 예제가 추상화를 강제), Obvious Implementation
(확신이 있을 때 바로 구현).

> Reference: `references/green-bar-patterns.md`

---

## 7. 테스팅 패턴

테스트 격리, AAA 패턴(Assert First 사고), 의미 있는 테스트 데이터,
네이밍 컨벤션, Mock 사용 계층, Crash Test Dummy, Self Shunt,
Log String, Clean Check-in.

> Reference: `references/testing-patterns.md`

---

## 8. Outside-In TDD와 Double Loop

GOOS 접근법: 외부 루프(인수 테스트)는 Red 상태를 유지하고 내부
루프(단위 테스트)는 Red-Green-Refactor를 순환한다. 아키텍처를 위한
Walking Skeleton. Mock Roles Not Objects. Tell Don't Ask.

> Reference: `references/outside-in-tdd.md`

---

## 9. TDD에서의 디자인 패턴

TDD 중 사용되는 패턴: Value Object(불변성), Null Object(조건문 제거),
Factory Method(유연한 생성), Command, Composite, Collecting Parameter.

> Reference: `references/design-patterns-tdd.md`

---

## 10. 리팩터링 패턴

Reconcile Differences, Isolate Change, Migrate Data, Extract Method,
Inline Method, Extract Interface (Protocol), Move Method, Method Object.
모든 리팩터링은 그린 바 상태에서 수행한다.

> Reference: `references/refactoring-patterns.md`

---

## 11. 테스트 냄새 카탈로그

동작 냄새: Assertion Roulette, Erratic Test, Fragile Test,
Frequent Debugging, Slow Test, Manual Intervention. 코드 냄새:
Obscure Test, Conditional Logic, Hard-Coded Data, Duplication, Eager Test.

> Reference: `references/test-smells.md`

---

## 12. TDD와 AI 코딩

프롬프트 엔지니어링으로서의 TDD: 테스트가 AI에게 무엇을 만들고 언제
완료인지 알려준다. TDAID 5단계 워크플로우: Plan -> Red -> Green(AI) ->
Refactor(AI+Dev) -> Validate. TDD는 AI 환각, 의도하지 않은 동작,
보안 취약점으로부터 방어한다.

> Reference: `references/tdd-ai.md`
