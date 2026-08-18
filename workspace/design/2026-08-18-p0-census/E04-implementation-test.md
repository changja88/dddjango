# E04 — implementation-test 센서스 (P0 온톨로지 도입 사전 인벤토리)

작성일: 2026-08-18. 담당 파일 2개, 수정 없음(읽기 전용 센서스).

## 파일별 요약

| 파일 | 행수 | 절수 | 규범 문장수 | 쌍둥이(codex판) |
|---|---|---|---|---|
| `dddjango/skills/implementation-test/SKILL.md` | 68 | 4 | 46 | 있음 — `codex-dddjango/skills/dddjango-implementation-test/SKILL.md` |
| `dddjango/skills/implementation-test/references/final.md` | 2754 | 99 | 175 | 있음 — `codex-dddjango/skills/dddjango-implementation-test/references/final.md` |
| **합계** | 2822 | **103** | **221** | 전 절 상속: 쌍둥이 있음 |

계수 규약: 규범 문장은 문법 문장 단위로 세되, 세미콜론·줄표로 결합된 **독립 지시**(예: «…mocker 픽스처; raw unittest.mock 폴백 금지»)는 분리해 셌다. 설명 산문·예제 코드·코드 주석·출처 인용·표(정보성)는 제외. 애매한 문장은 보수적으로 포함하고 비고에 표시했다.

④쌍둥이 축은 파일 단위 판정이라 표 열에서 제외 — 두 파일 모두 codex판 존재(103절 전부 상속).

## SKILL.md 인벤토리

| 절 | 규범 문장 수 | ①앵커 | ②소유자 | ③백스톱 | 비고 |
|---|---|---|---|---|---|
| frontmatter(name·description) | 2 | 없음 | 명시(discipline-tdd·implementation-django 계열 위임) | 불명 | 로드 시점 지시 + 위임 라우팅. 헤딩 없음 |
| 언제 쓰나 | 8 | 없음 | 명시(discipline-tdd §5.5 소유, 경계 4위임) | 불명 | add/update/retain 게이트 조건 + 위임 불릿 4개. 무번호 헤딩 |
| 핵심 운영 원칙 | 34 | 없음 | 명시(discipline-tdd §5.5, §7.1 불변 소유 등) | 불명 | final.md 규칙의 압축 복제본(19불릿) — §19.2 압축 불릿 하나에 5문장. 표류 위험 지점 |
| 상세 레퍼런스 | 2 | 없음 | 없음 | 불명 | 주제→절 매핑 표(정보성) + 부분 로드 지시 |

## references/final.md 인벤토리

| 절 | 규범 문장 수 | ①앵커 | ②소유자 | ③백스톱 | 비고 |
|---|---|---|---|---|---|
| 머리말(도입 인용문+목차) | 4 | 없음 | 명시(discipline-tdd가 소유) | 불명 | 문서 전체 입장 게이트 선언. § 없음 |
| §1.1 테스트 피라미드 | 5 | 있음 | 명시(discipline-tdd §5.5 candidate) | 불명 | 80/15/5 quota 부정, 비율 근거 add 금지 |
| §1.2 SMURF | 1 | 있음 | 없음 | 불명 | «반드시 그렇게 해야 한다»는 Google 교리 인용 — 애매하나 보수 포함 |
| §1.3 Google 테스트 크기 | 0 | 있음 | 없음 | 불명 | 지식 서술만 |
| §1.4 migration/DB-backed 오라클 식별 | 5 | 있음 | 명시(discipline-tdd §5.5 소유) | 불명 | 오라클 기준 분류표는 판정 규칙 담체 — 온톨로지 후보 |
| §2 테스트 더블 분류 | 1 | 있음 | 없음 | 불명 | Meszaros 5분류 기본 채택 |
| §3.1 pytest 기본 구조 | 0 | 있음 | 없음 | 불명 | 예제만 |
| §3.2 Fixture | 1 | 있음 | 없음 | 불명 | «pytest 스타일 (권장)» 라벨은 미계수 |
| §3.3 xUnit 매핑 | 0 | 있음 | 없음 | 불명 | 매핑 표만 |
| §3.4 단언 | 3 | 있음 | 없음 | 불명 | 입장 근거 아님 절연문 포함 |
| §3.5 예외 테스트 | 1 | 있음 | 없음 | 불명 | |
| §3.6 파라미터화 | 0 | 있음 | 없음 | 불명 | 예제만 |
| §3.7 conftest 공유 픽스처 | 0 | 있음 | 없음 | 불명 | 예제만 |
| §3.8 monkeypatch | 1 | 있음 | 없음 | 불명 | 시간 모킹 전용 라이브러리 권장(§10 참조) |
| §3.9 tmp_path | 0 | 있음 | 없음 | 불명 | 예제만 |
| §3.10 전체 실행 | 0 | 있음 | 없음 | 불명 | 명령어만 |
| §4.1 pyproject.toml 설정 | 4 | 있음 | 없음 | 커버 | check-test-config.py ⑴바인딩·⑶settings 분할(#445-447)이 명백 대응. filterwarnings 전역 금지 규칙은 스크립트 밖. 문면에 스크립트명 없음 |
| §4.2 conftest 계층 | 7 | 있음 | 명시(discipline-houserules §2 단일 출처, architect 소유, implementation-django §16.4) | 비커버 | 트리 직계 규칙은 check-test-config ⑵ 소유 영역이나, 이 절 고유 규범(승인 branch만 생성·PRAGMA/BEGIN/isolation 주입 금지)은 검사기 없음 |
| §5.1 내장 마커 | 0 | 있음 | 없음 | 불명 | 예제만 |
| §5.2 커스텀 마커 | 0 | 있음 | 없음 | 불명 | 예제만 |
| §5.3 마커→fixture | 0 | 있음 | 없음 | 불명 | 예제만 |
| §6 도입(버전-핀) | 3 | 있음 | 명시(implementation-django-ninja §2.1 규율, implementation-django §3.1 소유) | 불명 | 훈련 기억 버전 기입 금지 + 설계 반송 조건 |
| §6.1 pytest-xdist | 0 | 있음 | 없음 | 불명 | 명령어만 |
| §6.2 pytest-asyncio | 2 | 있음 | 없음 | 불명 | auto/strict 모드 «권장» 2건 — 연성 지침, 보수 포함 |
| §6.3 pytest-cov | 2 | 있음 | 없음 | 불명 | threshold 신설 금지·중앙 decision 없는 추가 금지 |
| §6.4 pytest-randomly | 0 | 있음 | 없음 | 불명 | 도구 설명만 |
| §6.5 pytest-timeout | 0 | 있음 | 없음 | 불명 | 예제만 |
| §7 도입(mock 도구) | 5 | 있음 | 명시(§7.1이 교리 불변 소유) | 불명 | mocker 기본·create_autospec 유일 예외·raw unittest.mock 금지 |
| §7.1 검증 방식 우선순위 | 3 | 있음 | 없음 | 불명 | 외부 의존성만 Mock — 교리 원문 |
| §7.2 Mock 기본 | 0 | 있음 | 없음 | 불명 | 예제만 |
| §7.3 의존 캡슐화 | 1 | 있음 | 없음 | 불명 | 인용문이 §7.1 규칙 재진술 — 중복 |
| §7.4 PropertyMock | 0 | 있음 | 없음 | 불명 | 예제만 |
| §7.5 AsyncMock | 1 | 있음 | 없음 | 불명 | 사용 조건문 — 약한 지시, 보수 포함 |
| §7.6 seal() | 0 | 있음 | 없음 | 불명 | 코드 주석에 create_autospec 예외 재진술(예제라 미계수) |
| §7.7 side_effect | 0 | 있음 | 없음 | 불명 | 예제만 |
| §7.8 호출 순서 검증 | 1 | 있음 | 없음 | 불명 | |
| §8 도입(Hypothesis 게이트) | 2 | 있음 | 명시(discipline-tdd §5.5) | 불명 | 생성 능력은 add 근거 아님 |
| §8.1 기본 사용법 | 0 | 있음 | 없음 | 불명 | 예제만 |
| §8.2 전략 조합 | 0 | 있음 | 없음 | 불명 | 예제만 |
| §8.3 @example | 0 | 있음 | 없음 | 불명 | 예제만 |
| §8.4 settings | 0 | 있음 | 없음 | 불명 | 예제만 |
| §8.5 Stateful | 0 | 있음 | 없음 | 불명 | 예제만 |
| §9.1 factory_boy 기본 개념 | 4 | 있음 | 명시(discipline-houserules §2 트리 단일 출처) | 커버 | factories 위치·내용은 check-test-config #391·#392가 명백 대응(부분 — factory_boy 기본 선택 자체는 미검사). 문면에 스크립트명 없음 |
| §9.2 기본 팩토리 | 0 | 있음 | 없음 | 불명 | 예제만 |
| §9.3 SubFactory | 0 | 있음 | 없음 | 불명 | 예제만 |
| §9.4 Trait | 0 | 있음 | 없음 | 불명 | 예제만 |
| §9.5 배치·재현성 | 0 | 있음 | 없음 | 불명 | 예제만 |
| §9.6 ORM 통합 | 0 | 있음 | 없음 | 불명 | 예제만 |
| §10 도입(시간 모킹) | 2 | 있음 | 없음 | 불명 | 전용 라이브러리 사용·monkeypatch 비권장 |
| §10.1 freezegun | 0 | 있음 | 없음 | 불명 | 예제만 |
| §10.2 time-machine | 0 | 있음 | 없음 | 불명 | 예제만 |
| §10.3 비교·선택 기준 | 0 | 있음 | 없음 | 불명 | 선택 가이드 표(정보성) |
| §11.1 responses | 0 | 있음 | 없음 | 불명 | 예제만 |
| §11.2 aioresponses | 0 | 있음 | 없음 | 불명 | 예제만 |
| §11.3 HTTPretty | 0 | 있음 | 없음 | 불명 | 선택 가이드 표(정보성) |
| §12 도입(testcontainers) | 1 | 있음 | 없음 | 불명 | «실제 서비스로 테스트한다» — 애매, 보수 포함 |
| §12.1 PostgreSQL | 0 | 있음 | 없음 | 불명 | 예제만 |
| §12.2 Redis | 0 | 있음 | 없음 | 불명 | 예제만 |
| §12.3 복수 서비스 | 0 | 있음 | 없음 | 불명 | 예제만 |
| §13 도입(coverage 게이트) | 1 | 있음 | 없음 | 불명 | coverage 목표 채우기용 case 신설 금지 |
| §13.1 설정 | 0 | 있음 | 없음 | 불명 | 설정 예만 |
| §13.2 명령어 | 0 | 있음 | 없음 | 불명 | 명령어만 |
| §14 도입(tox/nox) | 1 | 있음 | 없음 | 불명 | «라이브러리 개발 시 필수적» — 지식 서술이나 «필수» 표지, 보수 포함 |
| §14.1 tox | 0 | 있음 | 없음 | 불명 | 예제만 |
| §14.2 nox | 0 | 있음 | 없음 | 불명 | 예제만 |
| §14.3 비교 | 0 | 있음 | 없음 | 불명 | 표만 |
| §15.1 FIRST | 8 | 있음 | 명시(Timely는 discipline-tdd가 다룸) | 불명 | 5원칙 각각 규범 + 소유 절연 1 |
| §15.2 AAA | 7 | 있음 | 없음 | 불명 | 가독성 recipe 절연 + Act 한 줄·관련 assert 허용 |
| §15.3 화이트박스 회피 | 5 | 있음 | 없음 | 불명 | 설계 관점·기법 관점 이중 규범 |
| §15.4 기댓값 리터럴 | 8 | 있음 | 명시(discipline-tdd «명백한 데이터» 소유, discipline-cleancode §2.14) | 비커버 | check-choices-literal-consumption.py가 이 절을 **인용하며 테스트를 게이트 밖에 명시 배제** — 리터럴 강제 자체는 결정적 검사 없음. 경계 셋(①②③) 구조 |
| §15.5 union-enum 동기 후보 | 5 | 있음 | 명시(discipline-tdd §5.5 candidate signal) | 불명 | reject 목록(isinstance·get_args·멤버 집합) 명세적 |
| §16.1 코드 수준 안티패턴 | 6 | 있음 | 명시(Free Ride: 소유자 discipline-tdd §5.5에 송부) | 불명 | Liar 변종(산출물 오귀속)·Free Ride만 명시 규범, 나머지 목록은 암묵 금지 지식(미계수) |
| §16.2 전략 수준 안티패턴 | 1 | 있음 | 없음 | 불명 | 항목 1 괄호 규범만 계수 — 8항목 목록 자체는 암묵 금지(미계수) |
| §17 도입(mutation 게이트) | 4 | 있음 | 명시(discipline-tdd §5.5 candidate) | 불명 | score·생존 mutant는 승인 근거 아님 |
| §17.1 개념 | 0 | 있음 | 없음 | 불명 | 지식만 |
| §17.2 뮤테이션 종류 | 0 | 있음 | 없음 | 불명 | 표만 |
| §17.3 mutmut 사용법 | 0 | 있음 | 없음 | 불명 | 명령어만 |
| §17.4 결과 해석 | 0 | 있음 | 없음 | 불명 | Survived→입장 심사 힌트는 서술 |
| §17.5 점수 목표 | 3 | 있음 | 없음 | 불명 | quota 아님 + 승인 add/update에만 작성 |
| §18.1 Given-When-Then | 0 | 있음 | 없음 | 불명 | gherkin 예만 |
| §18.2 pytest-bdd | 0 | 있음 | 없음 | 불명 | 예제만 |
| §19 도입(Ninja 계약) | 5 | 있음 | 명시(discipline-tdd §5.5) | 불명 | mounted client 원칙·adapter-local TestClient 조건부 허용 |
| §19.1 mounted 공개 응답 | 2 | 있음 | 없음 | 불명 | 구현 세부 검증 금지 |
| §19.2 도입 | 2 | 있음 | 명시(discipline-tdd §5.5 decision row) | 불명 | 오류 계약 add·update 한정 |
| §19.2.1 승인된 HTTP 오류 계약 | 12 | 있음 | 명시(schema shape 변경 = 별도 명시적 **사용자** 승인) | 불명 | 파일 내 최대 규범 밀도 절. plugin 공통 오류 schema property 목록 부재 선언 |
| §19.2.2 공개 Python Schema 계약 | 5 | 있음 | 없음 | 불명 | «별도 decision row» 어휘로 §5.5 암시하나 소유자 미명명. 자동 비대상 5항목 목록 |
| §19.2.3 공개 OpenAPI 계약 | 5 | 있음 | 없음 | 불명 | 내부 직접 호출은 대체 불가 |
| §19.3 인증·페이지네이션 | 2 | 있음 | 없음 | 불명 | 불명확 시 API 설계 먼저 확정 |
| §19.4 django_db 선택 | 4 | 있음 | 없음 | 불명 | check-test-config #387·#389(unit DB 금지/integration DB 필수)와 인접하나 동일 규칙 아님 |
| §20 도입(동시성 게이트) | 4 | 있음 | 명시(discipline-tdd §5.5) | 불명 | 주제·예제 존재만으로 테스트 증설 금지 |
| §20.1 Idempotency replay | 4 | 있음 | 명시(architecture-api 계약 준수, architecture-db 선행) | 불명 | |
| §20.2 중복 생성·DB 제약 | 3 | 있음 | 없음 | 불명 | mock repository 대체 금지 |
| §20.3 Transaction·row lock | 4 | 있음 | 없음 | 불명 | transaction=True 과번역 금지 — §20.5와 짝 규칙 |
| §20.4 Race 재현 | 2 | 있음 | 없음 | 불명 | flaky 시 skip 전 분석 의무 |
| §20.5 결정적 CAS 스파이 | 11 | 있음 | 명시(architect 소유, architecture-db §9.5, implementation-django §16.4 출처-불문 금지) | 커버 | 커스텀 DatabaseWrapper 교체 금지는 check-mechanism-ownership.py ⑴이 명백 대응(부분 — 프로덕션 settings 축만, conftest 주입은 §4.2와 함께 비커버). 문면에 스크립트명 없음 |
| §21 도입 | 1 | 있음 | 명시(implementation-python 위임) | 불명 | |
| §21.1 pdb 진입 | 0 | 있음 | 없음 | 불명 | 명령어만 |
| §22 참고 문헌 | 0 | 있음 | 없음 | 불명 | 출처 표만 |
| 부록: 도구 설치 | 0 | 있음 | 없음 | 불명 | 설치 명령어만 |

## 축 집계 (절 수 103 기준)

| 축 | 집계 |
|---|---|
| ①앵커 | 있음 98 · 없음 5 (SKILL.md 4절 전부 + final.md 머리말) |
| ②소유자 | 명시 23 · 없음 80 |
| ③백스톱 | 커버 3 (§4.1·§9.1·§20.5) · 비커버 2 (§4.2·§15.4) · 불명 98 |
| ④쌍둥이 | 있음 103 · 없음 0 |

## 특이 발견

1. **입장 게이트 패턴의 전면 통일** — 규범이 있는 거의 모든 절이 `discipline-tdd` §5.5 decision row(add/update/retain/reuse/reject)를 선행 조건으로 반복 인용(문서 전체 15회 이상). 규칙 레지스트리의 «선행 게이트» 관계가 이미 사실상 어휘로 존재한다.
2. **SKILL.md «핵심 운영 원칙»이 final.md의 압축 복제본** — 34개 규범 문장이 §1~§20 규칙의 요약이며 각 불릿이 (§N) 참조를 단다. 특히 §19.2를 한 불릿 5문장으로 압축 — 개정 시 이중 갱신이 필요한 표류 위험 지점.
3. **앵커 비대칭** — final.md는 §번호 체계 완비(3단 §19.2.1까지)로 외부 문서·검사기가 이미 «implementation-test §15.4» 식으로 인용 중. 반면 SKILL.md 절은 무번호 헤딩이라 안정 앵커가 없다.
4. **백스톱 역참조만 존재** — 문서 문면은 check-*.py를 한 번도 지목하지 않는다. 검사기 쪽에서만 대응 확인: `check-test-config.py`(§4.1 pytest↔settings 바인딩·settings 분할, §9.1 factories 위치 #391/#392), `check-mechanism-ownership.py`(§20.5 DatabaseWrapper 교체 금지). 온톨로지 도입 시 정방향 링크 부재가 메꿀 지점.
5. **§15.4는 확정 비커버** — `check-choices-literal-consumption.py`가 §15.4를 인용하면서 테스트 파일을 게이트 밖에 명시적으로 둔다(«테스트는 게이트가 보지 않는다»). 테스트 기댓값 리터럴 강제 자체를 잡는 결정적 검사기는 없다.
6. **규범 밀도 양극화** — §19(37)·§15(33)·§20(28)에 규범의 56%가 집중되고, §3·§5·§8~§14·§18·§21 등 도구 지식 절은 0~2문장. 온톨로지 등록 실대상은 SKILL 원칙 + 머리말 + §1·§4·§6~§7 도입·§15~§17·§19~§20으로 좁혀진다.
7. **소유 주체 어휘가 이미 풍부(23/103절 명시)** — discipline-tdd §5.5, discipline-houserules §2, architecture-api, architecture-db §9.5, implementation-django §3.1·§16.4, implementation-django-ninja §2.1, implementation-python, architect(역할), «사용자 승인»(§19.2.1)까지 8개 이상 관할 주체가 문면에 등장 — 레지스트리 owner 필드의 초기값이 사실상 문서화돼 있다. 같은 규칙의 중복 서술도 확인: §7.1 교리가 §7.3 인용문·§16.1 Mockery에 재등장, §4.2와 §20.5가 연결 의미 금지(stock OPTIONS)를 이중 서술.
