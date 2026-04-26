# T18: implementation-django -> implementation-cleancode

**Task:** "300줄 서비스 함수에 가드 절과 Extract Method를 적용하려면?"

**Source Skill:** implementation-django

## [주요 내용]

implementation-django 스킬은 서비스 레이어 아키텍처를 다룬다:
- 모델 500줄 초과 시 서비스 함수 도입
- `<entity>_<action>` 네이밍
- 쓰기에 서비스, 읽기에 셀렉터
- (섹션 14: `references/service-layer.md` 참조)

그러나 가드 절(Guard Clause)과 Extract Method 리팩터링 기법은
**이 스킬의 범위 밖**이다.

SKILL.md 위임 규칙에 따른 판단:
- "언어 비종속적 원칙(네이밍, SOLID, 디자인 패턴)은 implementation-cleancode에 위임한다."

이 스킬이 제공할 수 있는 부분:
1. 서비스 함수의 Django 컨벤션 (`order_create()`, `order_confirm()`)
2. `transaction.on_commit()` 사용 패턴
3. Fat 뷰 -> 서비스 추출 (리팩터링 체크리스트)

가드 절로 중첩 if문 평탄화, Extract Method로 추상화 수준 통일,
SOLID 원칙 적용은 **implementation-cleancode**로 위임한다.

---
> **관련 스킬 참조:**
> - 가드 절과 Extract Method 리팩터링 -> **implementation-cleancode** 스킬
> - Python 함수 관용구 (위치/키워드 전용) -> **implementation-python** 스킬
