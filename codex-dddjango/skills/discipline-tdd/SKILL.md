---
name: discipline-tdd
description: TDD 실천 규율 — Red-Green-Refactor 사이클, 언제·왜 TDD를 하는가, 고전 학파 vs 런던 학파, 좋은 단위 테스트의 4대 특성, 현행 계약 기반 영구 테스트 입장·중복 판정·수명 주기, Outside-In TDD·이중 루프, 리팩토링 패턴, BDD와 TDD의 관계, AI 보조 TDD. TDD 사이클 설계·학파 선택·테스트 생성·유지·갱신·분리·삭제·검증 우선순위 결정이 필요하면 로드한다. 테스트 코드 작성법(mock 사용법·assert·픽스처·pytest 메커니즘)은 implementation-test로 위임.
---

# TDD 실천 규율

## 언제 쓰나

TDD 사이클을 어떻게 운용할지, 어떤 학파를 선택할지, 테스트 목록을 어디서 시작할지, AI 보조 구현 시 테스트를 어떻게 명세로 활용할지가 불명확할 때 로드한다. 경계:

- pytest fixture·mock·assert·팩토리 상세 작성법 → `dddjango-implementation-test`
- 테스트 코드 품질(가독성·구조·냄새) 원칙 → `dddjango-discipline-cleancode`
- Django TestClient·API 테스트 메커니즘 → `implementation-django`
- migration 전용 테스트와 DB-backed 현행 동작 테스트의 기술적 식별 → `dddjango-implementation-test`

## 핵심 운영 원칙

- TDD의 목표는 작동하는 깔끔한 코드다: 두려움 없이 변경할 수 있는 용기가 핵심 (§1.1–§1.2)
- Red-Green-Refactor 순서를 지켜라: 실패하는 테스트 먼저, 통과 후에만 리팩토링 (§2.1)
- 고전 학파(상태 검증)를 기본으로, 협력 구조 설계가 목적일 때만 런던 학파(행위 검증)를 선택한다 (§3.1–§3.4)
- 좋은 테스트의 4대 기둥: 회귀 방지, 리팩토링 내성, 빠른 피드백, 유지 보수성 — 리팩토링 내성은 타협하지 않는다 (§4.1–§4.4)
- 테스트 목록은 후보일 뿐이다. 모든 영구 test artifact의 add/update/move/split/rename/remove/weaken·재조직 전에 §5.5 입장 심사를 거치며, 의미 보존 재조직은 새 case·Red 없이 전후 보호가 같아야 한다 (§5.1–§5.3)
- 영구 테스트는 승인된 현행 계약·독자 실패·기존 권위 coverage를 판정한다. 공개 Python 계약은 별도 사용자 승인 또는 deployed consumer evidence 중 하나로 자격을 얻는다. `pending`은 G1을 막고 `reuse`·`reject`는 test artifact write가 0이다 (§5.5)
- migration 전용 테스트는 새로 만들거나 새 case·assertion·시나리오로 확장하지 않는다. 과거 버그에서 태어났어도 현행 계약을 검증하는 회귀 테스트는 보존한다 (§5.5)
- 초록 막대 전략: 가짜로 구현하기 → 삼각측량 → 명백한 구현 순으로 진행 (§6.1–§6.3)
- 테스트는 격리하고, AAA 패턴으로 구조화하라: Arrange-Act-Assert (§7.1–§7.2)
- Mock보다 출력·상태 검증을 우선한다: Mock 과다 사용은 리팩토링 내성을 약화시킨다 (§7.6)
- Outside-In 이중 루프도 바깥·안쪽 테스트를 자동 의무화하지 않는다. Walking Skeleton은 실제 얇은 E2E 행동이다 (§9.1–§9.2)
- AI 보조 TDD에서 테스트는 명세다: 개발자가 테스트를 작성하고, AI 구현은 테스트를 통과한 후 검증한다 (§17.1–§17.4)

## 상세 레퍼런스

주제별로 [`references/final.md`](references/final.md)의 해당 절을 따른다:

| 주제 | 절 |
|---|---|
| TDD 핵심 철학 (목표·용기) | §1 |
| TDD 사이클 (Red-Green-Refactor·pytest 예시) | §2 |
| TDD 학파 비교 (고전 vs 런던·상태 vs 행위 검증·Inside-Out vs Outside-In) | §3 |
| 좋은 단위 테스트의 4대 특성 (회귀 방지·리팩토링 내성·피드백·유지보수) | §4 |
| 빨간 막대 패턴 (후보 목록·영구 테스트 입장 심사·현행 계약 수명 주기·Red 비계 제거) | §5 |
| 초록 막대 패턴 (가짜 구현·삼각측량·명백한 구현) | §6 |
| 테스팅 패턴 (격리·AAA·테스트 데이터·명명·Mock 우선순위) | §7 |
| Outside-In TDD와 이중 루프 (Double Loop·Walking Skeleton·Mock Roles) | §9 |
| 디자인 패턴과 TDD (값 객체·널 객체·팩토리 메서드) | §10 |
| 리팩토링 패턴 (차이점 일치·변화 격리·메서드 추출·인터페이스 추출) | §11 |
| 테스트 냄새 카탈로그 (행위 냄새·코드 냄새) | §12 |
| BDD와 TDD의 관계 (TDD→ATDD→BDD 진화 경로) | §16 |
| TDD와 AI 코딩의 관계 (TDD as Prompt Engineering·dddjango Admission 확장 6단계) | §17 |

각 절은 [`references/final.md`](references/final.md)에서 필요한 항목만 읽는다(전체 로드 불필요).
