---
name: implementation-cleancode
description: >
  This skill should be used when the user asks to "write clean code",
  "review code quality", "refactor for readability", "apply SOLID principles",
  "reduce complexity", or when any code writing, review, or refactoring task
  is happening. The principles here are language-agnostic. If code is being
  generated, modified, reviewed, or refactored, these principles apply.
  For Python-specific conventions, see implementation-python.
---

# Clean Code 원칙

클린 코드는 다른 엔지니어가 읽고, 이해하고, 유지보수할 수 있는 코드다.
소프트웨어의 진짜 비용은 유지보수이며, 유지보수 비용의 지배적 요소는
**이해력**이다. 여기의 모든 원칙은 하나의 목표를 위해 존재한다: 코드를
안전하게 이해하고 변경하는 데 필요한 노력을 줄이는 것.

복잡성 — 시스템을 이해하고 수정하기 어렵게 만드는 구조적 속성 — 은
**변경 증폭**(단순한 변경이 여러 곳의 수정을 요구), **인지 부하**(너무 많은
맥락이 필요), **미지의 미지**(숨겨진 의존성이나 암묵적 규칙)로 나타난다.
두 가지 근본 원인은 통제되지 않는 **의존성**과 **불명확성**이다.

Python 관련 컨벤션(타입 힌트, dataclasses, match/case, 데코레이터, asyncio)은 implementation-python을 참조한다.

## 세 가지 핵심 원칙
1. 모든 이름은 의도를 드러낸다 — 변수를 설명하는 주석이 필요하면 이름을 바꿔라.
2. 모든 함수는 하나의 추상화 수준에서 하나의 일만 한다.
3. 모든 모듈은 단순한 인터페이스 뒤에 하나의 설계 결정을 숨긴다.

다른 모든 원칙은 이 세 가지를 위해 존재한다.

**참조 파일 로딩 규칙:**
- Writing 모드: 아래 주제와 관련된 코드를 생성하기 전에 해당 참조 파일을 먼저 읽는다.
- Review 모드: 리뷰 결과를 확정하기 전에 인용한 모든 원칙의 참조 파일을 읽는다.
- Refactoring 모드: 변경 사항을 제시하기 전에 적용한 각 패턴의 참조 파일을 읽는다.

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
- **Writing**: 사용자가 코드 생성, 구현, 작성을 요청
- **Review**: 사용자가 기존 코드의 리뷰, 검토, 평가를 요청
- **Refactoring**: 사용자가 기존 코드의 리팩토링, 개선, 정리를 요청

의도가 모호한 경우 Writing 모드를 기본으로 한다.

요청이 여러 모드에 걸치는 경우(예: "리뷰하고 리팩토링해줘"), Review를 먼저 적용한 후 같은 코드에 Refactoring을 적용한다.

### Writing 모드

새 코드를 생성할 때 모든 원칙을 묵시적으로 적용한다. 원칙을 설명하는
인라인 주석 없이 클린 코드를 작성한다. 코드가 스스로 말하게 한다.

코드를 생성하기 전에 관련 주제 영역의 참조 파일을 읽어 세부 규칙을 적용한다.

### Review 모드

잘 구조화된 코드를 리뷰할 때는 개선 사항을 나열하기 전에 코드의 잘된 점을
먼저 언급한다. 품질이 낮은 코드를 리뷰할 때는 가장 영향력 있는 문제부터
집중한다.

각 발견 사항을 다음 형식으로 작성한다:

```
[Principle] — 이것이 가독성이나 유지보수성을 해치는 이유 설명
```

리뷰를 확정하기 전에 아래의 모든 항목을 확인한다. 누락된 항목은 사용자가 나중에 직접 발견해야 하므로 모두 확인한다.
- [ ] 관련 스킬 참조 포함 -- 사용자의 다음 워크플로우를 위한 스킬 연결
- [ ] 도메인 예외 대신 에러 코드 또는 dict 반환 사용
- [ ] 불변 값 객체여야 할 가변 데이터
- [ ] Strategy 또는 Polymorphism을 사용할 수 있는 타입 기반 반복 조건문
- [ ] Null Object를 사용할 수 있는 산재된 None 검사
- [ ] 혼합된 책임을 가진 God Class
- [ ] 가드 절이어야 할 중첩된 if문
- [ ] 쿼리 함수 내 숨겨진 부수 효과
- [ ] Protocol을 통해 주입해야 할 테스트 불가능한 의존성
- [ ] 매직 넘버 또는 이름 없는 상수
- [ ] 중복된 지식 (단순한 코드 중복이 아닌)

리뷰 결과를 확정하기 전에 인용한 모든 원칙의 참조 파일을 읽어 정확성을 확인한다.

### Refactoring 모드

리팩토링 시 변경 전/후를 보여주고 각 변경의 이유를 명시한다.
각 변경을 특정 원칙에 연결하여 근거를 추적 가능하게 한다.
각 변경을 다음 형식으로 작성한다:

```
[Before]
<원본 코드>

[After]
<개선된 코드>

[Reason] Principle — 이 변경이 코드를 개선하는 이유 설명
```

변경 사항을 제시하기 전에 아래의 모든 적용 가능한 개선을 적용한다. 적용 가능한 항목을 건너뛰면 사용자가 추가 리팩토링을 해야 하므로 모두 적용한다.
- [ ] 관련 스킬 참조 포함 -- 사용자의 다음 워크플로우를 위한 스킬 연결
- [ ] 에러 코드 또는 dict 반환 → 도메인 예외로 대체
- [ ] 불변이어야 할 가변 데이터 → frozen 값 객체로 변환
- [ ] 타입 기반 반복 조건문 → Strategy 또는 Polymorphism 적용
- [ ] 산재된 None 검사 → Null Object 도입
- [ ] God Class → 변경 빈도에 따라 분해
- [ ] 중첩된 if문 → 가드 절로 평탄화
- [ ] 숨겨진 부수 효과 → 별도의 커맨드로 추출
- [ ] 테스트 불가능한 의존성 → Protocol을 통해 주입
- [ ] 매직 넘버 → 이름 있는 상수
- [ ] 중복된 지식 → 단일 권위 있는 소스

변경 사항을 제시하기 전에 적용한 각 패턴의 참조 파일을 읽는다.

형식이 개선의 깊이를 제한하지 않도록 한다. 코드에 근본적인 재설계가
필요한 경우, 먼저 전체 재설계를 적용한 후 위의 형식으로 변경 사항을
제시한다. 개별 변경 후에는 **전체 리팩토링된 코드**를 제공하여 사용자가
모든 것이 어떻게 맞아떨어지는지 볼 수 있게 한다.

---

## 1. 네이밍

좋은 이름은 주석의 필요성을 없애고 코드를 검색 가능하게 만든다.
의도를 드러낸다. 오해를 유발하는 정보와 노이즈 단어를 피한다. 개념당 한 단어.
클래스는 명사, 메서드는 동사. 이름 길이는 스코프 크기에 비례한다.

> Reference: `references/naming.md`

---

## 2. 함수

함수는 조직의 첫 번째 단위다. 블록에서 의미 있는 이름의 함수를
추출할 수 있다면, 원래 함수는 둘 이상의 일을 하고 있는 것이다.
하나의 추상화 수준에서 하나의 일만 한다. 매개변수를 최소화한다(최대 3개).
플래그 인수 금지. 커맨드와 쿼리를 분리한다.

`input / process / output` 같은 패턴이 나타나면 같은 수준에 유지한다.
대칭 구조를 유지하기 위해 헬퍼를 추출한다.

> Reference: `references/functions.md`

---

## 3. 주석과 포맷팅

주석은 코드로 의도를 표현하는 데 실패했기 때문에 존재한다. 공개 API는
반드시 독스트링을 가진다. 인라인 주석은 *왜*를 기록하지, *무엇*을 기록하지
않는다. 주석 처리된 코드를 삭제한다. 파일을 ~200줄 이하로 유지한다(최대 500).
자동 포매터를 사용하고 CI에서 강제한다.

> Reference: Inline — 이 섹션의 안내는 위에서 완결된다.

---

## 4. 추상화와 캡슐화

구현이 아닌 인터페이스에 의존한다. 상태를 캡슐화한다 — 객체가 *무엇을*
할 수 있는지 노출하고, *어떻게* 하는지 숨긴다. 정보 은닉은 설계 결정을
인터페이스 뒤에 유지한다; 같은 지식이 여러 모듈에 누출되면 통합한다.

> Reference: `references/abstraction.md`

---

## 5. 객체 설계

데이터가 아닌 책임으로 객체를 설계한다. Tell, Don't Ask. 조건문을
다형성으로 대체한다. 서브클래싱보다 위임. 로직을 데이터 가까이에
유지한다. 변경 빈도에 따라 분리한다.

> Reference: `references/object-design.md`, `references/solid.md`

---

## 6. 디자인 패턴

문제가 맞을 때 패턴을 적용한다; 억지로 적용하지 않는다. 주요 패턴:
Factory Method, Abstract Factory, Value Object, Null Object, Strategy,
Observer, Template Method, Pluggable Object.

> Reference: `references/design-patterns.md`

---

## 7. 상태와 에러 처리

변수의 스코프와 수명을 최소화한다. 불변 값 객체를 선호한다.
먼저 설계로 에러를 제거하고, 그 다음 예외(에러 코드가 아닌)를 사용한다.
가드 절은 중첩된 조건문을 평탄화한다. 신뢰 경계에서 검증한다.

> Reference: `references/state.md`, `references/error-handling.md`

---

## 8. DRY와 중복

DRY는 **지식**에 관한 것이지, 키 입력에 관한 것이 아니다. 서로 다른 도메인
개념을 표현하는 두 개의 동일한 코드 조각은 중복이 아니다. 같은 비즈니스
규칙을 인코딩하는 두 개의 다른 코드 조각은 중복이다. 단일 권위 있는
소스를 추출한다.

> Reference: `references/dry.md`

---

## 9. 협업과 의존성

높은 응집도, 낮은 결합도. 상속보다 합성. 직교성 — 한 모듈의 변경이
관련 없는 모듈의 변경을 강제하지 않아야 한다. 가역성을 위해 변동성 높은
의존성을 추상화 뒤에 감싼다.

> Reference: `references/refactoring.md` section on collaboration.

---

## 10. 리팩토링

코드 스멜과 그 해결책을 안다: Bloaters, OO Abusers, Change
Preventers, Dispensables, Couplers. 핵심 기법: Extract Method,
Replace Temp with Query, Decompose Conditional, Guard Clauses, Table-Driven
Methods.

> Reference: `references/refactoring.md` section on refactoring.

---

## 11. 레거시 코드

레거시 코드는 테스트가 없는 코드다. Seams(의존성 주입 + Protocol)를
사용하여 테스트 가능하게 만든다. 새로운 동작을 위한 Sprout Method.
전/후 훅을 위한 Wrap Method. 리팩토링 전에 현재 동작을 포착하는
Characterisation Tests.

> Reference: `references/legacy.md`

---

## 12. 설계 철학

Design It Twice — 최소 두 가지 접근 방식을 비교한다. 빠르게 구현한 후
개선한다. 안정적인 도메인 개념을 중심으로 구조화한다. YAGNI — 추측성
미래 요구사항을 위해 만들지 않는다. Broken Windows — 나쁜 코드를 즉시
수정한다. ETC (Easier to Change) — 궁극의 설계 휴리스틱. 항상 작은 단계로.

> Reference: `references/philosophy.md`
