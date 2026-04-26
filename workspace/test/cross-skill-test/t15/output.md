# T15: implementation-python -> implementation-cleancode

**Task:** "700줄 클래스를 SOLID 원칙으로 분리하는 방법은?"

**Source Skill:** implementation-python

## [주요 내용]

implementation-python 스킬은 Python 고유의 컨벤션과 패턴을 다루지만,
SOLID 원칙에 기반한 클래스 분리는 **이 스킬의 범위 밖**이다.

SKILL.md 위임 규칙에 따른 판단:
- "언어 비종속적 원칙(네이밍, 함수, SOLID, 디자인 패턴, 리팩토링)은 implementation-cleancode에 위임한다."

이 스킬이 제공할 수 있는 부분:
1. 분리 후 Python 클래스 설계 패턴 (`@classmethod`, `__repr__`, `_protected`)
2. Protocol을 통한 인터페이스 분리 (ISP 구현)
3. `@dataclass(frozen=True)`로 값 객체 추출
4. `match/case`로 조건부 로직 선언적 구현

700줄 God Class 분해 원칙(변경 빈도에 따른 분리), SRP(단일 책임),
OCP(개방-폐쇄), Extract Method, Decompose Conditional은
**implementation-cleancode**로 위임한다.

---
> **관련 스킬 참조:**
> - SOLID 원칙과 God Class 분해 -> **implementation-cleancode** 스킬
> - DDD 기반 도메인 객체 분리 -> **architecture-ddd** 스킬
