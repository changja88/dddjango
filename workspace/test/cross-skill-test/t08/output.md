# T08: architecture-implementation-patterns -> implementation-python

**Task:** "Repository를 Python Protocol로 구현할 때 type hint 컨벤션은?"

**Source Skill:** architecture-implementation-patterns

## [주요 내용]

architecture-implementation-patterns 스킬은 Repository 패턴의 구조적 설계를 다룬다:
- 리포지토리 추상화가 테이블 단위가 아닌 애그리거트 단위
- 추상화(인터페이스)는 사용하는 계층이 소유한다 (소유권 역전)
- 포트 인터페이스가 기술적 연산이 아닌 도메인 의도를 표현
- (섹션 4: `references/persistence.md` 참조)

그러나 Python Protocol 구현, type hint 컨벤션은 **이 스킬의 범위 밖**이다.

SKILL.md 위임 규칙에 따른 판단:
- "Python 컨벤션(타입 힌트, 데이터클래스)에 대해서는 implementation-python에 위임한다."

이 스킬이 제공할 수 있는 부분:
1. Repository 포트 인터페이스의 메서드 시그니처 설계
2. 의존성 역전 원칙에 따른 인터페이스 배치
3. 어댑터 구현에 비즈니스 로직 포함 금지

`Protocol` 클래스 정의, `PEP 695` 제네릭 구문, `X | None` 타입 힌트는
**implementation-python**으로 위임한다.

---
> **관련 스킬 참조:**
> - Python Protocol과 type hint 컨벤션 -> **implementation-python** 스킬
> - SOLID 원칙 (DIP) -> **implementation-cleancode** 스킬
