# E07 — implementation-django-ninja P0 센서스

작성: 2026-08-18 · 담당 파일 2개 전수 판독. 규범 문장 = 지시·금지·조건 문장(설명 산문·예제 코드·이유 서술 제외, 애매하면 포함 후 비고 표시).

## 파일별 요약

| 파일 | 행수 | 절수 | 규범 문장수 |
|---|---:|---:|---:|
| `dddjango/skills/implementation-django-ninja/SKILL.md` | 56 | 4 | 44 |
| `dddjango/skills/implementation-django-ninja/references/final.md` | 1019 | 24 | 275 |
| **합계** | 1075 | **28** | **319** |

쌍둥이(④): `codex-dddjango/skills/implementation-django-ninja/SKILL.md`(55행)·`references/final.md`(1019행) **둘 다 존재** → 전 절 «쌍둥이 있음» 상속.

집계 기준 비고:
- 규범 문장은 마침표 단위로 세되, 세미콜론·줄표로 명확히 독립한 규칙 2개가 한 문장에 있으면 2로 셌다(비고 표시).
- 명사구 체크리스트(§2.1 확인 5항, §3.2 확인 4항, §8 candidate 10항, §9.1 candidate 8항, §9.2 artifact 5항, §10 checklist 10항, §6.1 상태코드 매핑표)는 «문장»이 아니라 지배 문장 1개로만 셌다 — 실제 구속 항목 수는 문장 수보다 훨씬 많다.
- 백스톱 판정은 문면 지목(§6.2의 checker·marker 언급) 또는 명백 대응(스크립트 docstring이 이 문서 §를 «집행» 근거로 인용)일 때만 커버.

## 절별 인벤토리 — SKILL.md

| 절 | 규범 문장 수 | ①앵커 | ②소유자 | ③백스톱 | 비고 |
|---|---:|---|---|---|---|
| [SKILL.md] frontmatter(description) | 2 | 없음 | 명시(위임 스킬 4개 명명) | 비커버 | 로드 트리거·위임 문장. 헤딩 없는 YAML — 참조 표지 부재 |
| [SKILL.md] § 언제 쓰나 | 5 | 있음(제목 라벨) | 명시(경계 4행이 소유 스킬 명명) | 비커버 | 라우팅·로딩 규칙 — 검사기 대상 아님 |
| [SKILL.md] § 핵심 운영 원칙 | 35 | 있음(제목 라벨) | 명시(G1 slot 6·중앙 test admission·architecture-api/db 명명) | 불명 | final.md 규칙의 압축 요약 — 각 bullet이 §N 역참조. 백스톱은 원 절이 소유(요약 절 자체를 지목하는 검사기 없음). 표류 위험 표면 |
| [SKILL.md] § 상세 레퍼런스 | 2 | 있음(제목 라벨) | 없음 | 비커버 | §1–§11 주제→절 매핑표. «필요한 항목만 읽는다» 로딩 규칙 |

SKILL.md 소계: 4절 · 44문장.

## 절별 인벤토리 — references/final.md

| 절 | 규범 문장 수 | ①앵커 | ②소유자 | ③백스톱 | 비고 |
|---|---:|---|---|---|---|
| 서두(제목·위임 안내·목차, L1–29) | 3 | 없음 | 명시(architecture-api·implementation-django·implementation-test) | 비커버 | «Django Ninja는 greenfield 기본 목표» 정책 문장 포함 |
| §1.1 Django Ninja skill의 역할 | 1 | 있음(§1.1) | 명시(자기 스킬 범위) | 비커버 | 범위 서술 — «다룬다» 1문장만 보수적 포함. 책임 bullet 8항은 명사구 |
| §1.2 다른 source reference로 위임할 책임 | 4 | 있음(§1.2) | 명시(4개 스킬 «결정한다/담당한다») | 비커버 | 순수 소유 배정 절 |
| §1.3 Router thinness 원칙 | 3 | 있음(§1.3) | 없음 | 불명 | 허용 5항·금지 5항 목록은 명사구(지배 문장 2개로 계수) |
| §2.1 Router 등록 | 11 | 있음(§2.1) | 없음 | 불명 | 버전 핀 규율(기억 속 버전 금지·resolve 실제 버전 기록) 밀도 높음. 확인 체크리스트 5항 별도. implementation-django §3.1 교차 참조 |
| §2.2 Operation 선언 | 25 | 있음(§2.2) | 명시(«10번 slot이 승인한 한 경로») | 커버 | check-composition-root.py(L1880)·check-openapi-error-declaration.py(L3260)가 §2.2를 집행 근거로 인용 — 대응은 검사기→문서 단방향. 2-path(예외/Result) 규칙이 §6.2와 중복 서술 |
| §2.3 클래스 컨트롤러 (ninja-extra) — 신규 표준 | 38 | 있음(§2.3) | 없음(«승인된 별도 scope» 승인 주체 미명명) | 커버 | check-composition-root.py가 컴포지션 루트·Q-7 축 커버(registrar/auto_import 축 커버 여부는 불명 — 비고). Q-7 위반 코드 인용. «보존 근거는 소비자 의존» 원칙 §6.2와 짝 |
| §3.1 Request/response schema 분리 | 17 | 있음(§3.1) | 명시(중앙 영구 테스트 입장 심사·architecture-ddd §2.5/§3.7·discipline-tdd) | 불명 | birth-enum·discriminator 규칙. 원시 리터럴 소비 금지는 check-choices-literal-consumption.py(cleancode §2.14)와 부분 대응. 외부 이슈 앵커 vitalik/django-ninja#1308 인용 |
| §3.2 ModelSchema 사용 기준 | 1 | 있음(§3.2) | 없음 | 불명 | 확인 4항은 의문형 체크리스트. 예제 코드 주석 속 규칙(«민감 필드는 넣지 않는다»)은 예제라 제외 |
| §3.3 Resolver와 computed field | 2 | 있음(§3.3) | 없음 | 불명 | |
| §4.1 Authentication | 9 | 있음(§4.1) | 없음 | 불명 | request.auth에 ErrorSchema 금지 — §6.2 auth 단락과 중복 서술 |
| §4.2 Authorization | 5 | 있음(§4.2) | 없음 | 불명 | |
| §5.1 Filtering과 sorting | 7 | 있음(§5.1) | 명시(implementation-django 위임·architecture-api 계약 선행) | 불명 | 예시 코드 앞 괄호 문장(«신규 표면은 §2.3 형태») 1문장 포함 |
| §5.2 Pagination | 7 | 있음(§5.2) | 명시(«API contract가 결정한다») | 불명 | «offset이 단순하다»는 권고 산문으로 제외(비고). «timestamp와 id를 함께 쓴다»는 권고지만 표지 있어 포함 |
| §6.1 Status code mapping | 8 | 있음(§6.1) | 명시(architecture-api·«503/409 선택은 명세 §5/G1이 정한다») | 커버 | 상태코드 13항 매핑표는 명사구(문장 아님). 503 bullet만 문장형 규칙 3. 전역 변환 금지 축은 check-ninja-boundary-middleware.py(«§6 집행»)와 오류 계열 checker가 커버 |
| §6.2 `dddjango-code-json` 오류 프로필 | 85 | 있음(§6.2) | 명시(G1 slot 6·10번 slot·12-slot·Coordinator·API/discipline reviewer) | 커버 | **문서 최대 절(전체의 31%)**. 문면이 checker를 역할명으로 지목(schema checker·controller/OpenAPI checker)+marker ID 2종(DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED·RESOLVED_DYNAMIC_ERROR_SHAPE_ANALYSIS) — 실물은 check-error-centralization.py·check-api-error-controller-contract.py·check-openapi-error-declaration.py. 날짜 스탬프 canon 예외(2026-08-15) 내장. 내부 소단락 10여 개(굵은 라벨)가 사실상 하위 절 |
| §6.3 콘텐츠 협상 실패 (406/415) | 15 | 있음(§6.3) | 명시(architecture-api §7.2 별도 승인·중앙 입장 심사) | 커버 | check-ninja-boundary-middleware.py docstring이 §6.3을 명시 인용(전역 미들웨어 자작 적출) |
| §7 Idempotency-Key | 8 | 있음(§7) | 명시(architecture-db·implementation-django 소유) | 불명 | check-idempotency-scope-creep.py는 인접(스코프크립 차단·architecture-db §9.6 집행)이나 §7 문면 규칙과 부분 대응 — 커버 단정 불가 |
| §8 OpenAPI | 5 | 있음(§8) | 명시(중앙 영구 테스트 입장 심사) | 불명 | candidate 10항 명사구. 오류 선언 축은 check-openapi-error-declaration.py가 §2.2 근거로 커버하나 §8 자체 규칙(mounted 문서 검증·정직 보고)은 프로세스 규칙 |
| §9.1 공개 HTTP 검증 범위 | 8 | 있음(§9.1) | 명시(discipline-tdd 중앙 입장 심사) | 불명 | TestClient(router) 격리 검증의 증거 부정 — 테스트 입장 규율. candidate 8항 명사구 |
| §9.2 검증 보고 기준 | 3 | 있음(§9.2) | 없음 | 비커버 | 보고 정직성 규칙(«Not run 표시») — 검사기 부재 명백 |
| §10 DRF-to-Ninja migration | 4 | 있음(§10) | 없음 | 불명 | checklist 10항 명사구 |
| §11 라우팅 기준 | 6 | 있음(§11) | 명시(절 전체가 소유 스킬 라우팅) | 비커버 | SKILL.md 경계 4행·frontmatter 위임과 3중 중복 표면 |
| §12 참고 문헌 | 0 | 있음(§12) | 없음 | 비커버 | 규범 0 — 외부 URL 8건 |

final.md 소계: 24절 · 275문장.

## 4축 집계 (절 수 기준, 총 28절)

| 축 | 값 |
|---|---|
| ①앵커 | 있음 26 / 없음 2 (SKILL frontmatter·final 서두) |
| ②소유자 | 명시 17 / 없음 11 |
| ③백스톱 | 커버 5 (§2.2·§2.3·§6.1·§6.2·§6.3) / 비커버 9 / 불명 14 |
| ④쌍둥이 | 있음 28 / 없음 0 |

## 특이 발견

1. **§6.2 초거대 절**: 규범 85문장으로 문서 전체(275)의 31%. 굵은 라벨 소단락(공통 core와 변경 gate / BC 오류 언어 / 컨트롤러가 변환을 소유한다 / 추출 금지 / framework 오류 경계 / 인프라 오류 경계 / 응답 선언과 OpenAPI / 승인된 wire 보존 등) 10여 개가 § 번호 없는 사실상 하위 절 — 레지스트리화 시 §6.2 단일 ID로는 해상도 부족.
2. **검사기 marker ID 체계가 이미 문면에 존재**: `DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED`·`RESOLVED_DYNAMIC_ERROR_SHAPE_ANALYSIS`(§6.2)가 문서↔검사기↔Coordinator 프로토콜의 안정 식별자로 작동 중. 단 스크립트 파일명은 문서에 한 번도 등장하지 않고, 대응은 검사기 docstring이 문서 §를 인용하는 **단방향**(check-ninja-boundary-middleware.py «§6 집행», check-composition-root.py·check-openapi-error-declaration.py가 §2.2 인용).
3. **외부 승인 슬롯 ID가 문서 밖 앵커로 다수 사용**: «G1 slot 6», «10번 slot», «12-slot», «Q-7» — 이 문서에 정의 없이 참조만 있음. 온톨로지 도입 시 슬롯 체계의 정본 위치 확인 필요.
4. **3중 중복 라우팅 표면**: frontmatter description ↔ SKILL «언제 쓰나» 경계 4행 ↔ final §1.2/§11 — 같은 위임 규칙이 3곳에 병렬 서술. SKILL «핵심 운영 원칙» 35문장도 final 규칙의 압축 복사본(각 bullet §N 역참조로 결박돼 있으나 문장 자체는 이중 유지).
5. **규칙 본문 중복 2건**: controller 오류 변환 2-path(예외/Result) 순서가 §2.2와 §6.2에 거의 동일하게 반복, auth 실패 규칙(None/AuthenticationError·request.auth ErrorSchema 금지)이 §4.1과 §6.2에 반복.
6. **날짜 스탬프 canon 예외 내장**: «좁힌 식별자 field는 …required여도 canon이다(식별자 field 한정·ErrorCode 좁힘 동반일 때만 — 2026-08-15)»(§6.2) — 결정 기록이 규칙 문장 안에 박혀 있음. 레지스트리의 결정 이력 필드 후보.
7. **명사구 체크리스트 대량**: §2.1(5)·§3.2(4)·§6.1 상태코드(13)·§8(10)·§9.1(8)·§9.2(5)·§10(10) — 문장 계수에서 빠진 구속 항목 55+개. 외부 이슈 앵커(vitalik/django-ninja#1308, §3.1)도 규칙 근거로 인용됨.
