# T04: architecture-ddd -> implementation-python

**Task:** "Value Object를 Python frozen dataclass와 type hint로 구현하는 방법은?"

**Source Skill:** architecture-ddd

## [주요 내용]

architecture-ddd 스킬은 값 객체(Value Object)의 개념적 설계를 다룬다:
- 속성 조합으로 식별되며 불변이다
- 가능한 한 값 객체를 선호한다 -- 불변성이 부수 효과를 제거한다
- (섹션 6: `references/value-objects-entities.md` 참조)

그러나 Python 구현 세부사항(frozen dataclass, type hint 컨벤션)은 **이 스킬의 범위 밖**이다.

SKILL.md 위임 규칙에 따른 판단:
- "Python 컨벤션(타입 힌트, 데이터클래스)에 대해서는 implementation-python에 위임한다."

DDD 스킬이 제공할 수 있는 부분:
1. 어떤 개념이 값 객체인지 판단 기준 (동등성은 속성으로, 불변, 부수 효과 없음)
2. 값 객체 설계 원칙 (자가 검증, 연산의 닫힘)

`@dataclass(frozen=True, slots=True)`, `X | None` 구문, `Protocol` 등의
Python 구현 패턴은 **implementation-python**으로 위임한다.

---
> **관련 스킬 참조:**
> - Python frozen dataclass와 type hint 컨벤션 -> **implementation-python** 스킬
> - 값 객체의 SOLID 원칙 적용 -> **implementation-cleancode** 스킬
