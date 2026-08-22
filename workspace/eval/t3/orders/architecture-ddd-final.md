# T3 발주 — architecture-ddd-final

- 원문: `dddjango/skills/architecture-ddd/references/final.md` (현재 2124행 — **센서스 2122행에서 드리프트: 아래 행 번호는 참고값, spec은 반드시 현재 파일에서 재확정**)
- 스코프: REF 36절 · 규범 206문장 (파일럿 기이관 절 제외됨)
- 산출: `workspace/eval/t3/specs/architecture-ddd-final.spec.json` + `workspace/eval/t3/worksheets/architecture-ddd-final.md`

| section_key | 헤딩 | 센서스 행 | 규범 수 | 운반체 | 재진술 | 비고 |
|---|---|---|---|---|---|---|
| s004-1.2 | 1.2 전략 설계 우선 원칙 | 11–23 | 6 | none | Y:architecture-ddd-final/s051-8 | [의사결정 #6]+번호 명령 4+«활용하되» — §8 #6·SKILL s004에도 사본 |
| s007-2.1 | 2.1 지식 탐구 (Knowledge Crunching) | 36–103 | 2 | code | N | «~은 지식 탐구가 아니다» 정의형 부정 — 애매 보수 포함(P0 승계) |
| s008-2.2 | 2.2 도메인과 하위 도메인 | 104–168 | 1 | code,table | N | 표 셀 «사내 구현 필수»만 규범 |
| s009-2.3 | 2.3 유비쿼터스 언어 (Ubiquitous Language) | 169–211 | 4 | code | Y:architecture-ddd-final/s052-9 | BC 내에서만 유효 원칙 — §9·SKILL s004에 사본 |
| s010-2.4 | 2.4 바운디드 컨텍스트 (Bounded Context) | 212–253 | 4 | code | Y:architecture-ddd-final/s052-9 | «반드시 그래야 하는 것은 아니다» 허용형 — 애매 포함(P0 승계). §9 BC 행이 [B] 문장 사본 |
| s011-2.5 | 2.5 컨텍스트 맵 (Context Map) | 254–362 | 17 | code,table | Y:architecture-ddd-final/s026 | BC 간 enum·상수 공유 경계 단락이 birth-enum 원리 재진술 포함. 표 마커 셀 3 계수 |
| s012-2.6 | 2.6 증류 (Distillation) | 363–418 | 1 | code,table | N | 표 셀 «최고의 인재를 투입해야 한다»만 |
| s016-3.1 | 3.1 값 객체 (Value Object) | 465–538 | 3 | code | Y:architecture-ddd-final/s052-9 | 불변·동등성·setter 금지 — §9 값 객체 행에 사본 |
| s019 | Vernon의 4가지 설계 규칙 | 644–820 | 17 | code | Y:architecture-ddd-final/s052-9 | Vernon 4규칙(헤딩 4+규칙1 2+규칙2 인용 1+규칙3 ORM 확장 4+규칙4 6) — §8 #4·§9·SKILL 사본 |
| s021-3.4 | 3.4 리포지토리 (Repository) | 838–897 | 4 | code | Y:architecture-ddd-final/s052-9 | Cosmic Python 인용=규칙 포함(P0 규약 ②). 코드 주석 «별도 리포지토리 만들지 않는다»는 예제로 제외 |
| s022-3.5 | 3.5 도메인 서비스 (Domain Service) | 898–993 | 6 | code | Y:architecture-ddd-final/s052-9 | [의사결정 #3] — §8 #3·§9·SKILL 사본 |
| s023-3.6 | 3.6 응용 서비스 (Application Service) | 994–1091 | 9 | code | Y:architecture-ddd-final/s052-9 | 예제 코드 내부 규범 주석 2건 포함(#635·#484 «두 어휘를 섞지 말 것» — P0 규약 ③). §9·SKILL 사본 |
| s024-3.7 | 3.7 도메인 이벤트 (Domain Event) | 1092–1181 | 3 | code | Y:architecture-ddd-final/s052-9 | [의사결정 #7]+수집→디스패치 2(uow.after_commit — 본문·코드 주석 절 내 중복). §8 #7·§9·SKILL 사본 |
| s025 | Outbox 패턴 | 1182–1199 | 14 | none | N | Outbox(h4) — 선택 조건 불릿 내 #529·#603·#626 내장 규칙 각각 셈(P0 승계). 소유 핸드오프 4건 포함 |
| s026 | 발행 이벤트 타입 — 1종째부터 enum (birth-enum) | 1200–1209 | 18 | none | Y:architecture-ddd-skill/s004 | birth-enum(h4) — SKILL 불릿·§2.5 단락·§6.7 코드 주석에 사본. 배치·파생 Literal·append-only·제외 짝조항·소비자 짝규칙 |
| s029-4.1 | 4.1 의도를 드러내는 인터페이스 (Intention-Revealing Interfaces) | 1333–1356 | 1 | code | N | - |
| s030-4.2 | 4.2 부작용 없는 함수 (Side-Effect-Free Functions) | 1357–1373 | 1 | code | N | - |
| s031-4.3 | 4.3 단언 (Assertions) | 1374–1390 | 1 | code | N | - |
| s032-4.4 | 4.4 개념적 윤곽 (Conceptual Contours) | 1391–1394 | 2 | none | N | - |
| s033-4.5 | 4.5 독립형 클래스 (Standalone Classes) | 1395–1398 | 1 | none | N | - |
| s034-4.6 | 4.6 연산의 닫힘 (Closure of Operations) | 1399–1425 | 1 | code | N | 조건형 권고 — 애매 보수 포함(P0 승계) |
| s035-5 | 5. 아키텍처 | 1426–1429 | 1 | none | Y:architecture-ddd-final/s051-8 | P0 «§5 서두» [의사결정 #5] — §8 #5에 사본 |
| s036-5.1 | 5.1 계층 아키텍처 | 1430–1442 | 3 | code | Y:architecture-ddd-final/s052-9 | 방향 규칙 3 — §9 계층+DIP 행·SKILL 사본. 펜스는 계층 다이어그램 |
| s037-5.2 | 5.2 DIP (의존성 역전 원칙) | 1443–1490 | 2 | code | Y:architecture-ddd-final/s052-9 | §9·SKILL 사본 |
| s038-5.3 | 5.3 핵사고날 아키텍처 (포트와 어댑터) | 1491–1517 | 16 | none | N | 방향 1+선택 4+회피 3+포트 5+어댑터 3. §9 핵사고날 행은 주제 서술이라 사본 아님으로 판정 |
| s039-5.4 | 5.4 CQRS (커맨드-쿼리 책임 분리) | 1518–1536 | 10 | none | Y:architecture-ddd-final/s051-8 | [의사결정 #2]·Greg Young 인용=규칙 — §8 #2·§9 사본. «선택 적용 안전» 애매 포함(P0 승계) |
| s040-5.5 | 5.5 대규모 구조 (Large-Scale Structure) | 1537–1604 | 5 | code,table | N | 표 셀 명령형 5 — Evans 패턴 서술의 명령형 표기, 애매 보수 포함(P0 승계) |
| s042-6.1 | 6.1 패키지 구조 | 1607–1671 | 11 | code | Y:architecture-ddd-final/s051-8 | [의사결정 #8]·houserules 배치 권위 이양 — §8 #8 사본. 트리 펜스 내 tests/ 주석은 본문 동일 규칙으로 제외 |
| s043-6.2 | 6.2 Data Mapper 패턴 | 1672–1677 | 2 | none | N | - |
| s044-6.3 | 6.3 Repository + Unit of Work 패턴 | 1678–1728 | 3 | code | N | - |
| s046-6.5 | 6.5 Saga 패턴 (분산 트랜잭션) | 1843–1911 | 2 | code,table | N | 보상 실행 1+멱등성 필수 1 |
| s047-6.6 | 6.6 단순한 비즈니스 로직 패턴 | 1912–1940 | 2 | code | N | «적합하다» 권고형 — 애매 보수 포함(P0 승계) |
| s048-6.7 | 6.7 마이크로서비스와 DDD | 1941–1995 | 2 | code,table | Y:architecture-ddd-final/s026 | 코드 주석에 birth-enum·§2.5 재진술(계수는 제외 — 본문 규칙 사본). 표 셀 «최소화 필수» 포함 |
| s049-6.8 | 6.8 패턴 선택 절차와 Risky Write 라우팅 | 1996–2019 | 14 | table | Y:architecture-ddd-skill/s004 | 소유권 표 6행=순수 규범(행 단위 계수, P0 승계). SKILL 불릿 10 사본 |
| s050-7 | 7. 복잡성 관리 원칙 | 2020–2057 | 3 | code | N | 통찰 3건 — 서술·규범 경계 애매, 보수 포함(P0 승계) |
| s052-9 | 9. 핵심 요약 | 2073–2093 | 14 | table | Y:architecture-ddd-skill/s004 | 14행 전부 본문 재진술 — 본문·§9·SKILL 3중 사본의 축(표류 위험) |
