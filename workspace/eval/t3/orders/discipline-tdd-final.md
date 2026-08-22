# T3 발주 — discipline-tdd-final

- 원문: `dddjango/skills/discipline-tdd/references/final.md` (현재 1122행 — 센서스와 일치)
- 스코프: REF 44절 · 규범 156문장 (파일럿 기이관 절 제외됨)
- 산출: `workspace/eval/t3/specs/discipline-tdd-final.spec.json` + `workspace/eval/t3/worksheets/discipline-tdd-final.md`

| section_key | 헤딩 | 센서스 행 | 규범 수 | 운반체 | 재진술 | 비고 |
|---|---|---|---|---|---|---|
| s001 | TDD 개발 방법론 가이드 | 1–7 | 2 | none | Y:discipline-tdd-final/s025-5.5 | 무앵커 전역 규칙(h1 직후 인용구). reuse·reject→write 0 규칙 3중 사본(서문·skill s004·§5.5)의 하나 |
| s006-2.1 | 2.1 기본 사이클 [테스트주도 개발] | 29–44 | 11 | code | N | 코드 펜스 안 사이클 절차 지시 3 + 상세 단계 8 규범 계수(P0 승계, 애매) |
| s012-3.4 | 3.4 실전 권고: 상황별 선택 | 202–214 | 1 | table | N | 표는 인용구가 배경 지식으로 강등. 실규범(고전 학파 기본·Mock은 외부 의존성 격리만)이 강등 인용구 안에 있음 |
| s015-4.2 | 4.2 회귀 방지의 위상 [Khorikov] | 240–252 | 4 | code | Y:discipline-tdd-final/s025-5.5 | 장애 보고→§5.5 candidate 우선 절차 재서술 2 + 설계 원칙 의무 2 |
| s018-4.5 | 4.5 세 가지 테스트 스타일 [Khorikov] | 294–344 | 2 | code,table | Y:discipline-tdd-final/s036-7.6 | 검증 우선순위(출력>상태>통신)·순수 함수 추출 — §7.6과 2중 규칙 |
| s021-5.1 | 5.1 테스트 후보 목록 | 357–375 | 10 | code | Y:discipline-tdd-final/s025-5.5 | «각 후보는 §5.5 통과 add·update일 때만 Red» 전역 규칙 재진술 포함. 쿠폰 예시 문장도 규칙 서술형이라 포함(P0 애매 승계) |
| s022-5.2 | 5.2 한 단계 테스트 | 376–379 | 2 | none | N | 다음 테스트 선택 기준 |
| s023-5.3 | 5.3 시작 테스트 | 380–389 | 2 | code | N | 시작점 규칙 |
| s024-5.4 | 5.4 설명 테스트 | 390–393 | 1 | none | N | 한 문장 지시 |
| s025-5.5 | 5.5 영구 테스트 입장 심사와 현행 계약 수명 주기 | 394–464 | 57 | table | Y:discipline-tdd-skill/s004 | 최대 절(182중 57=31%). 7값 decision·심사표 스키마 표·화이트 6항/블랙 8항(명사구는 지배문 1씩만 계수)·조정 6분기·migration 금지·DB-backed 허용(P0 승계). skill 요약·서문과 3중 사본, 표류 의심 |
| s027-6.1 | 6.1 가짜로 구현하기 (Fake It) | 467–489 | 2 | code | N | 상수 반환→변수화 절차 |
| s028-6.2 | 6.2 삼각측량 (Triangulation) | 490–505 | 2 | code | N | «예 2개 이상일 때만 추상화» + 사용 시점 권고(애매, P0 승계 포함) |
| s029-6.3 | 6.3 명백한 구현 (Obvious Implementation) | 506–511 | 2 | none | N | 권고 포함(애매, P0 승계) |
| s031-7.1 | 7.1 테스트 격리 | 514–538 | 3 | code | N | 독립성 의무·공유 상태 제거·fixture 사용 |
| s032-7.2 | 7.2 AAA 패턴: Arrange-Act-Assert [Osherove] | 539–560 | 3 | code | N | AAA 의무 + Assert First 사고법(인용구 안 규범 포함) |
| s033-7.3 | 7.3 테스트 데이터 | 561–566 | 3 | none | N | 상수 중복 의미 금지 포함 |
| s034-7.4 | 7.4 명백한 데이터 | 567–578 | 1 | code | N | 관계 드러내기 지시 |
| s035-7.5 | 7.5 테스트 명명 규칙 [Osherove] | 579–598 | 1 | code | N | 명명 패턴은 코드 펜스 형식 명세지만 규범 1 계수(P0 승계) |
| s036-7.6 | 7.6 Mock보다 출력·상태 검증을 우선한다 [Khorikov] | 599–602 | 4 | none | Y:discipline-tdd-final/s018-4.5 | 검증 우선순위 소유 선언·implementation-test §7 위임·mocker 도구 지정. §4.5와 2중 |
| s037-7.7 | 7.7 깨진 테스트 / 깨끗한 체크인 [테스트주도 개발] | 603–609 | 1 | none | N | 팀 규칙만 규범. 혼자 규칙은 서술형 제외(애매, P0 승계) |
| s038-8 | 8. 테스트 더블 분류 체계 | 610–615 | 1 | none | N | implementation-test 위임 스텁 |
| s040-9.1 | 9.1 이중 루프 TDD (Double Loop TDD) | 618–670 | 2 | code | Y:discipline-tdd-final/s025-5.5 | «양쪽 테스트 자동 의무 아님»·«각 후보는 §5.5 통과» — 후자는 전역 규칙 재진술 |
| s041-9.2 | 9.2 Walking Skeleton [Freeman & Pryce - GOOS] | 671–694 | 3 | code | N | availability test 부정·실제 E2E 행동일 때만 후보 |
| s042-9.3 | 9.3 Mock Roles, Not Objects [Freeman, Pryce, Mackinnon, Waln | 695–698 | 3 | none | N | 역할 Mock 원칙 + implementation-test §7 위임 |
| s043-9.4 | 9.4 Tell, Don't Ask 원칙 [Freeman & Pryce - GOOS] | 699–728 | 1 | code | N | 인용구 지시 1 |
| s045-10.1 | 10.1 값 객체 (Value Object) | 746–770 | 1 | code | N | 불변 유지 지시 |
| s046-10.2 | 10.2 널 객체 (Null Object) | 771–793 | 1 | code | N | 동일 프로토콜 제공 |
| s047-10.3 | 10.3 팩토리 메서드 (Factory Method) | 794–815 | 1 | code | N | 생성 유연성 |
| s049-11.1 | 11.1 차이점 일치시키기 | 818–821 | 2 | none | N | 단계적 수렴·합치기 |
| s050-11.2 | 11.2 변화 격리하기 | 822–825 | 1 | none | N | 격리 지시 |
| s051-11.3 | 11.3 데이터 이주시키기 | 826–855 | 6 | code | N | 지시 1 + 5단계 절차 |
| s052-11.4 | 11.4 메서드 추출하기 | 856–876 | 1 | code | N | - |
| s053-11.5 | 11.5 메서드 인라인 | 877–880 | 1 | none | N | - |
| s054-11.6 | 11.6 인터페이스 추출하기 | 881–910 | 1 | code | N | Protocol 사용 |
| s055-11.7 | 11.7 메서드 옮기기 | 911–914 | 1 | none | N | - |
| s056-11.8 | 11.8 메서드 객체 | 915–920 | 1 | none | N | - |
| s058-12.1 | 12.1 행위 냄새 (Behavior Smells) | 923–958 | 2 | table,code | Y:discipline-tdd-final/s025-5.5 | 예제 뒤 2문장만 계수(«분리는 recipe»·«새 case는 §5.5 판정» — 후자 재진술). 표 해결책 열 6칸은 명사구 준규범, 문장 아님(P0 승계) |
| s060-13 | 13. 레거시 코드 다루기 | 993–998 | 1 | none | N | discipline-cleancode 위임 스텁 |
| s061-14 | 14. Property-Based Testing | 999–1004 | 1 | none | N | implementation-test 위임 스텁 |
| s062-15 | 15. Mutation Testing | 1005–1010 | 1 | none | N | implementation-test 위임 스텁 |
| s064-16.1 | 16.1 TDD와 BDD의 관계 | 1013–1033 | 1 | code,table | N | 설명·진화 경로 펜스·비교표 속 pytest-bdd 위임 1만 규범 |
| s066-17.1 | 17.1 TDD as Prompt Engineering | 1036–1047 | 2 | code | Y:discipline-tdd-final/s025-5.5 | §5.5 입장 전제·«요구/AI 위험이 자동 승인 아님» — 전자는 전역 규칙 재진술 |
| s069-17.4 | 17.4 dddjango Admission을 추가한 TDAID 6단계 | 1085–1097 | 6 | code | Y:discipline-tdd-final/s025-5.5 | Plan→Admission→Red→Green→Refactor→Validate 6단계 코드 펜스 절차를 규범 계수(P0 애매 승계). Admission 행=§5.5 심사 압축 사본 |
| s070-18 | 18. Python 테스트 생태계 심화 | 1098–1103 | 1 | none | N | implementation-test 위임 스텁 |
