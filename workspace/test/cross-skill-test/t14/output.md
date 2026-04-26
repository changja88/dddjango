# T14: implementation-cleancode -> implementation-python

**Task:** "Strategy 패턴을 Python Protocol/match-case로 구현할 때 컨벤션은?"

**Source Skill:** implementation-cleancode

## [주요 내용]

implementation-cleancode 스킬은 Strategy 패턴의 언어 비종속적 원칙을 다룬다:
- 조건문을 다형성으로 대체 (섹션 5: 객체 설계)
- Strategy 패턴: 문제가 맞을 때 적용, 억지로 적용하지 않음 (섹션 6: 디자인 패턴)
- 타입 기반 반복 조건문 -> Strategy 또는 Polymorphism 적용 (리팩터링 체크리스트)
- (`references/design-patterns.md`, `references/object-design.md` 참조)

그러나 Python Protocol 클래스와 match/case 구문의 구현 세부사항은
**이 스킬의 범위 밖**이다.

SKILL.md 위임 규칙에 따른 판단:
- "Python 관련 컨벤션(타입 힌트, dataclasses, match/case, 데코레이터, asyncio)은 implementation-python을 참조한다."

이 스킬이 제공할 수 있는 부분:
1. Strategy 패턴 적용 시점 판단 (타입 기반 반복 조건문이 있는가?)
2. 데이터가 아닌 책임으로 객체 설계 (Tell, Don't Ask)
3. 서브클래싱보다 위임 원칙

Python `Protocol`로 Strategy 인터페이스 정의, `match/case`로 디스패치 구현,
`@dataclass`와 결합하는 패턴은 **implementation-python**으로 위임한다.

---
> **관련 스킬 참조:**
> - Python Protocol과 match/case 구현 -> **implementation-python** 스킬
> - Django에서 Strategy 패턴 적용 -> **implementation-django** 스킬
