# T3 발주 — implementation-test-final

- 원문: `dddjango/skills/implementation-test/references/final.md` (현재 2754행 — 센서스와 일치)
- 스코프: REF 49절 · 규범 175문장 (파일럿 기이관 절 제외됨)
- 산출: `workspace/eval/t3/specs/implementation-test-final.spec.json` + `workspace/eval/t3/worksheets/implementation-test-final.md`

| section_key | 헤딩 | 센서스 행 | 규범 수 | 운반체 | 재진술 | 비고 |
|---|---|---|---|---|---|---|
| s001 | Python 테스트 코드 작성 종합 가이드 | 1–7 | 4 | none | Y:implementation-test-skill/s003 | h1+도입 인용문 — 문서 전체 입장 게이트 4문장. P0 머리말의 앞부분 |
| s004-1.1 | 1.1 Martin Fowler의 테스트 피라미드 | 37–69 | 5 | code,table | N | 80/15/5 quota 부정·비율 근거 add 금지. 코드 펜스=피라미드 그림(예제), 표=정보성 |
| s005-1.2 | 1.2 Google의 SMURF 프레임워크 | 70–85 | 1 | none | N | «반드시 그렇게 해야 한다» Google 교리 인용 — 애매, 보수 포함(P0 승계) |
| s007-1.4 | 1.4 Migration 전용 테스트와 DB-backed 현행 동작 테스트 식별 | 100–112 | 5 | table | N | 오라클 기준 분류표=판정 규칙 담체(표 행이 규범 운반) |
| s008-2 | 2. 테스트 더블 분류 체계 | 113–128 | 1 | table | N | Meszaros 5분류 기본 채택 1문장, 표는 정보성 |
| s011-3.2 | 3.2 Fixture (setUp/tearDown) [테스트주도 개발 + 파이썬코딩의기술] | 152–227 | 1 | code | N | 픽스처 사용 지시 1문장. «pytest 스타일 (권장)» 라벨 미계수(P0 승계) |
| s013-3.4 | 3.4 단언(Assertion) [테스트주도 개발] | 238–258 | 3 | code | N | 입장 근거 아님 절연문 포함 |
| s014-3.5 | 3.5 예외 테스트 [테스트주도 개발] | 259–269 | 1 | code | N | 예외 테스트 작성 지시 1문장 |
| s017-3.8 | 3.8 monkeypatch를 활용한 환경 격리 | 303–313 | 1 | code | N | 시간 모킹 전용 라이브러리 권장(§10 참조) |
| s021-4.1 | 4.1 pyproject.toml 종합 설정 | 347–397 | 4 | code | N | settings 실제 경로·분할 존재 시만·하드코딩 금지 + filterwarnings 전역 금지(blockquote). 백스톱 check-test-config ⑴⑶(P0) |
| s022-4.2 | 4.2 conftest.py 계층 구조 | 398–415 | 7 | code | Y:implementation-test-final/s105-20.5 | stock OPTIONS·연결 의미 주입 금지가 §20.5와 이중 서술(P0 발견 7). 승인 branch만 생성 등 고유 규범은 비커버 |
| s027-6 | 6. pytest 플러그인 생태계 | 535–538 | 3 | none | N | §6 도입: 훈련 기억 버전 기입 금지·버전-핀 규율·설계 반송 조건 |
| s029-6.2 | 6.2 pytest-asyncio: 비동기 테스트 | 583–624 | 2 | code | N | auto/strict 모드 «권장» 2건 — 연성 지침, 보수 포함(P0 승계) |
| s030-6.3 | 6.3 pytest-cov: 커버리지 통합 | 625–648 | 2 | code | N | threshold 신설 금지·중앙 decision 없는 추가 금지 |
| s033-7 | 7. Mock과 테스트 더블 실전 | 699–702 | 5 | none | N | §7 도입: mocker 기본·create_autospec 유일 예외·raw unittest.mock 금지 |
| s034-7.1 | 7.1 검증 방식 우선순위 [Unit Testing - Khorikov + 파이썬코딩의기술] | 703–714 | 3 | table | N | 검증 우선순위 표는 판정 순서 운반. 외부 의존성만 Mock 교리 원문 |
| s036-7.3 | 7.3 의존 관계 캡슐화로 모킹을 쉽게 만들기 [파이썬코딩의기술] | 749–785 | 1 | code | Y:implementation-test-final/s034-7.1 | 말미 인용문이 §7.1 교리 재진술(P0 비고 — 중복) |
| s038-7.5 | 7.5 AsyncMock: 비동기 함수 모킹 | 823–872 | 1 | code | N | 사용 조건문 — 약한 지시, 보수 포함(P0 승계) |
| s041-7.8 | 7.8 호출 순서 검증 | 956–981 | 1 | code | N | 순서 검증 시 assert_has_calls/mock_calls 지시 |
| s042-8 | 8. Property-Based Testing (Hypothesis) | 982–987 | 2 | none | N | §8 도입 게이트: 생성 능력은 add 근거 아님 |
| s049-9.1 | 9.1 기본 개념 | 1147–1156 | 4 | code | N | factory_boy 기본·정확 필드 행/VO 직접 생성 정당·factories 위치. 백스톱 check-test-config #391/#392(P0) |
| s055-10 | 10. 시간 모킹 (freezegun / time-machine) | 1318–1321 | 2 | none | N | §10 도입: 전용 라이브러리 사용·monkeypatch 직접 교체 비권장 |
| s063-12 | 12. Docker 기반 통합 테스트 (testcontainers) | 1583–1586 | 1 | none | N | «실제 서비스로 테스트한다» — 애매, 보수 포함(P0 승계) |
| s067-13 | 13. 커버리지 설정 (coverage.py) | 1694–1697 | 1 | none | N | §13 도입: coverage 목표 채우기용 case 신설 금지 |
| s070-14 | 14. 멀티환경 테스트 (tox / nox) | 1778–1781 | 1 | none | N | «라이브러리 개발 시 필수적» — 지식 서술이나 «필수» 표지, 보수 포함(P0 승계) |
| s075-15.1 | 15.1 FIRST 원칙 [Clean Code - Robert C. Martin] | 1894–1977 | 8 | code | N | FIRST 5원칙 각각 규범 + Timely 소유 절연(discipline-tdd) |
| s076-15.2 | 15.2 AAA 패턴 (Arrange-Act-Assert) | 1978–2036 | 7 | code | N | 가독성 recipe 절연 + Act 한 줄·관련 assert 허용(핵심 규칙 3항 포함) |
| s077-15.3 | 15.3 화이트박스 테스트를 피하라 [테스트주도 개발 + Codepipes Blog] | 2037–2056 | 5 | code | N | 설계 관점·기법 관점 이중 규범 |
| s078-15.4 | 15.4 외부 계약 기댓값은 리터럴로 — 프로덕션 상수 역수입 금지 [Google Testing Blog]  | 2057–2070 | 8 | code | N | 리터럴 강제 + 경계 셋 ①②③. P0: 확정 비커버(검사기는 테스트를 게이트 밖 명시 배제) |
| s079-15.5 | 15.5 발행 이벤트 봉투의 union-enum 동기 후보 | 2071–2078 | 5 | none | N | union-enum 동기 candidate signal·reject 목록 명세적 |
| s081-16.1 | 16.1 코드 수준 안티패턴 | 2081–2187 | 6 | code | Y:implementation-test-final/s034-7.1 | Liar 변종(산출물 오귀속)·Free Ride만 명시 규범, 목록은 암묵 지식 미계수. Mockery 항이 §7.1 교리 재진술 |
| s082-16.2 | 16.2 전략 수준 안티패턴 [Codepipes Blog] | 2188–2202 | 1 | none | N | 항목 1 괄호 규범만 계수 — 8항목 번호 목록 자체는 암묵 금지 미계수(P0 승계) |
| s083-17 | 17. Mutation Testing [mutmut] | 2203–2206 | 4 | none | N | §17 도입: score·생존 mutant는 승인 근거 아님 |
| s088-17.5 | 17.5 뮤테이션 점수 목표 | 2279–2284 | 3 | none | N | quota 아님 + 승인 add/update에만 작성 |
| s092-19 | 19. Django Ninja API 계약 테스트 | 2377–2384 | 5 | none | N | §19 도입: mounted client 원칙·adapter-local TestClient 조건부 허용 |
| s093-19.1 | 19.1 Mounted 공개 응답 계약 | 2385–2408 | 2 | code | N | 구현 세부 검증 금지 |
| s094-19.2 | 19.2 요청 검증과 오류 응답 | 2409–2413 | 2 | none | N | 오류 계약 add·update 한정(§5.5 decision row 선행) |
| s095-19.2.1 | 19.2.1 승인된 HTTP 오류 계약 | 2414–2430 | 12 | none | N | 파일 내 최대 규범 밀도 절. schema shape 변경=별도 명시 사용자 승인 |
| s096-19.2.2 | 19.2.2 공개 Python Schema 계약 | 2431–2445 | 5 | none | N | 자동 비대상 5항목 불릿은 금지 목록(규범 운반이나 산문 문장으로 계수됨 — P0 승계). 소유자 미명명 «별도 decision row» 어휘 |
| s097-19.2.3 | 19.2.3 공개 OpenAPI 계약 | 2446–2456 | 5 | none | N | 내부 직접 호출은 mounted 문서 대체 불가 |
| s098-19.3 | 19.3 인증, 페이지네이션, 필터링 | 2457–2478 | 2 | code | N | 불명확 시 API 설계 먼저 확정 |
| s099-19.4 | 19.4 pytest-django DB 접근 선택 | 2479–2505 | 4 | code | Y:implementation-test-final/s103-20.3 | transaction=True 선택 규범이 §20.3과 중복 서술. check-test-config #387/#389와 인접하나 동일 규칙 아님(P0) |
| s100-20 | 20. Idempotency와 동시성 테스트 | 2506–2511 | 4 | none | N | §20 도입: 주제·예제 존재만으로 테스트 증설 금지 |
| s101-20.1 | 20.1 Idempotency replay 계약 | 2512–2568 | 4 | code | N | replay 동일 결과·payload 불일치 충돌 실패·architecture-api/db 선행 |
| s102-20.2 | 20.2 중복 생성 방지와 DB 제약 | 2569–2585 | 3 | code | N | mock repository 대체 금지 |
| s103-20.3 | 20.3 Transaction과 row lock 테스트 | 2586–2613 | 4 | code | N | transaction=True 과번역 금지 — §20.5와 짝 규칙 |
| s104-20.4 | 20.4 Race condition 재현 테스트 | 2614–2640 | 2 | code | N | flaky 시 skip 전 분석 의무 |
| s105-20.5 | 20.5 결정적 CAS-충돌 재시도 테스트 (스파이) | 2641–2680 | 11 | code | N | 커스텀 DatabaseWrapper 교체 금지(출처-불문)·stock OPTIONS만. 백스톱 check-mechanism-ownership ⑴ 부분 커버(P0) |
| s106-21 | 21. 테스트 디버깅 기법 | 2681–2684 | 1 | none | N | implementation-python 위임 1문장 |
