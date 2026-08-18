# E08 — architecture-db + architecture-api P0 센서스

담당: 문서 담당자 E08 · 기준일 2026-08-18 · 담당 파일 4개(수정 없음, 읽기 전용 조사)

## 파일별 요약

| 파일 | 행수 | 절수 | 규범 문장수 |
|---|---:|---:|---:|
| `dddjango/skills/architecture-db/SKILL.md` | 47 | 4 | 18 |
| `dddjango/skills/architecture-db/references/final.md` | 736 | 15 (목차 + §1–§14) | 106 |
| `dddjango/skills/architecture-api/SKILL.md` | 51 | 4 | 20 |
| `dddjango/skills/architecture-api/references/final.md` | 638 | 16 (목차 + §1–§15) | 166 |
| **합계** | 1,472 | **39** | **310** |

집계 방식 메모:
- 절 단위 = final.md는 최상위 §, SKILL.md는 H2 헤딩(+frontmatter 1절). 소절(§N.M)은 상위 절에 귀속시키고 비고에 명시.
- 규범 문장 = 지시·금지·조건 문장. 상황→권장/기준 매핑 표는 지시 내용을 담은 행(셀)을 문장 1로 보수적 포함(비고에 «표 행» 표시). 설명·정의·예제 코드·이유 서술 제외.
- ④쌍둥이는 파일 단위 판정 후 절에 상속: **4파일 모두 codex 쌍둥이 존재** (`codex-dddjango/skills/architecture-{db,api}/…`). references/final.md 2건은 바이트 동일, SKILL.md 2건은 개명 표기 차이만(아래 특이 발견 6).

---

## architecture-db/SKILL.md

| 절 | 규범 문장 수 | ①앵커 | ②소유자 | ③백스톱 | 비고 |
|---|---:|---|---|---|---|
| frontmatter (name·description·user-invocable) | 2 | 없음 | 없음 | 비커버 | «먼저 로드한다»·«…로 위임» 2건. `user-invocable: false`는 설정값이라 문장 미포함 |
| 언제 쓰나 | 4 | 없음 | 없음 | 비커버 | 로드 조건 1 + 위임 경계 화살표 3(→ implementation-django / architecture-ddd / architecture-api) |
| 핵심 운영 원칙 | 10 | 없음 | 명시(부분) | 불명 | 7개 불릿이 final.md §4·5·7·8·9.4·9.6·9.7·11 요약-복제. §9.6 불릿에 `discipline-tdd` 입장 결정·coder 주체 명시. §9.6 복제분은 check-idempotency-scope-creep.py 간접 커버이나 문면 스크립트 지목 없음 |
| 상세 레퍼런스 | 2 | 없음 | 없음 | 비커버 | «해당 절을 따른다»·«필요한 항목만 읽는다». 주제→§ 라우팅 표는 매핑이라 문장 미포함 |

소계: 4절 · 18문장. SKILL 절에는 § 번호가 전혀 없고 헤딩도 전 스킬 공통 범용 문구(«언제 쓰나» 등)라 안정 앵커 부재.

---

## architecture-db/references/final.md

| 절 | 규범 문장 수 | ①앵커 | ②소유자 | ③백스톱 | 비고 |
|---|---:|---|---|---|---|
| 목차 | 0 | 없음 | 없음 | 비커버 | GitHub 앵커 링크(#1-…) — §N 표기와 이중 앵커 체계 |
| §1 데이터베이스 모델링 프로세스 | 1 | 있음 | 없음 | 비커버 | 청유형 «말을 믿지 말자 — …합의안을 갖자» 보수적 포함. 나머지 설명·표 |
| §2 개념적 데이터 모델링 (ERD) | 3 | 있음 | 없음 | 비커버 | 작성 원칙 2 + 인조키 조건 지시 1 |
| §3 정규화 (1NF — BCNF) | 1 | 있음 | 없음 | 비커버 | «정규화 먼저, 필요시에만 역정규화» — §4.2·§5·SKILL 불릿1과 중복 규칙 |
| §4 역정규화 | 2 | 있음 | 없음 | 비커버 | «반드시 정규화 먼저»·«읽기 많다고 바로 역정규화는 잘못» — §3.4와 중복 |
| §5 성능 최적화 순서 | 2 | 있음 | 없음 | 비커버 | «다음 순서를 반드시 지킨다»·«슬로우 쿼리부터 시작한다». 동일 규칙 4중 출현(SKILL·§3.4·§4.2·§5) |
| §6 인덱스 아키텍처: B+Tree | 0 | 있음 | 없음 | 비커버 | 전부 메커니즘 설명(WAL 서술 포함) — 규범 없음 |
| §7 인덱스 설계 베스트 프랙티스 | 6 | 있음 | 없음 | 비커버 | 순서 결정 규칙 2 + §7.4 원칙 표 행 4(표 행) |
| §8 제약조건과 중복 방지 | 19 | 있음 | 없음 | 불명 | 서두 보호 원칙 1, §8.1 주의 셀 5(표 행), cascade 금지 1, **BC 경계 FK 금지 2**(출처로 `architecture-ddd` §3.3 인용 — 출처 명시이지 판정 주체 아님), §8.3 매핑 표 4(표 행)+«최소한 다음을 정한다» 1, §8.4 rollout 1+단계 4. BC FK 금지는 check-context-isolation.py 인접이나 FK 검사 코드 없음 확인 → 불명 |
| §9 트랜잭션, 격리 수준, 락 | 43 | 있음 | 명시 | 커버(부분) | 최중량 절: §9.4=1, §9.5=18(엔진 의존성·연결 설정 경계·낙관적 동시성 단락), §9.6=12(Risky Write 블록·Test criteria 심사), §9.7=12(Outbox 표 포함). 소유자 다수 명시: 판정=도메인 책임, 테스트 입장=`discipline-tdd` 심사, ENGINE 교체=설계 승인, stored result HTTP 매핑=presentation(api §13.3). 백스톱: check-idempotency-scope-creep.py가 자기 문면에서 «architecture-db §9.6 Idempotency storage 집행» 명시 → §9.6 항목만 커버, 나머지(§9.5 CAS·§9.7 outbox)는 check-transaction-boundary·check-event-publish·check-broker-contract 인접이나 대응 미명시. 외부 피인용 최다: §9.5 9회·§9.6 2회·§9.7 3회. 인라인 결정 ID: #529·#626·D50(검사기측) |
| §10 쿼리 최적화 | 4 | 있음 | 없음 | 비커버 | ANALYZE 조건 지시 1 + §10.5 원칙 표 행 3(표 행) |
| §11 운영 rollout, backfill, migration safety | 16 | 있음 | 없음 | 비커버 | 관할 선언 2(구현은 implementation-django로 «넘긴다» — 위임 명시이나 판정 주체 아님), §11.1=2, §11.2 불릿 5, §11.3 설계 기준 셀 5(표 행), §11.4=1, §11.5 산출물 의무 1 |
| §12 데이터 모델링 패턴: 계층 구조 | 4 | 있음 | 없음 | 비커버 | §12.4 선택 가이드 매핑 4(표 행). 나머지 설명 |
| §13 데이터 모델링 패턴: 상속과 다형성 | 5 | 있음 | 없음 | 비커버 | 다형적 연관 앱 레벨 보장 의무 1 + §13.5 선택 가이드 4(표 행) |
| §14 참고 문헌 | 0 | 있음 | 없음 | 비커버 | 출처 표만 |

소계: 15절 · 106문장.

---

## architecture-api/SKILL.md

| 절 | 규범 문장 수 | ①앵커 | ②소유자 | ③백스톱 | 비고 |
|---|---:|---|---|---|---|
| frontmatter (name·description·user-invocable) | 2 | 없음 | 없음 | 비커버 | «먼저 로드한다»·«…로 위임». 위임처 표기 혼재: `dddjango:architecture-ddd`(콜론 접두) vs `architecture-db`(무접두) |
| 언제 쓰나 | 6 | 없음 | 없음 | 비커버 | 로드 조건 1 + 위임 경계 5 |
| 핵심 운영 원칙 | 10 | 없음 | 명시(부분) | 불명 | 8불릿 = final.md § 요약-복제. 에러 프로필 불릿(3문장)에 승인 주체 명시: 별도 사용자 승인·G1 표면화(STOP). 해당 불릿은 check-api-error-controller-contract.py·check-error-centralization.py·check-openapi-error-declaration.py 인접이나 문면 스크립트 지목 없음 |
| 상세 레퍼런스 | 2 | 없음 | 없음 | 비커버 | db판과 동일 패턴 |

소계: 4절 · 20문장.

---

## architecture-api/references/final.md

| 절 | 규범 문장 수 | ①앵커 | ②소유자 | ③백스톱 | 비고 |
|---|---:|---|---|---|---|
| 목차 | 0 | 없음 | 없음 | 비커버 | |
| §1 REST 아키텍처 원칙 | 0 | 있음 | 없음 | 비커버 | 정의·원칙 설명만 |
| §2 HTTP 메서드와 멱등성 | 0 | 있음 | 없음 | 비커버 | 속성 표·PATCH 멱등성 뉘앙스 전부 사실 서술. 지시력은 SKILL 불릿1이 담당 |
| §3 URL/리소스 설계 규칙 | 7 | 있음 | 없음 | 비커버 | 명명 규칙 표 5(표 행) + 계층 슬래시 1 + «3단계 이상 깊이는 피한다» 1 |
| §4 HTTP 상태 코드 | 17 | 있음 | 명시 | 불명 | 상태 코드 용도 매핑 13(표 행: 2xx 4·4xx 7·5xx 2, «애매하면 500» 포함) + **CAS 재시도 소진 status 규칙 3**(누락 금지 의무·controller 헤더 소유·설계자 임의 확정 금지 — 선택 venue §5/G1 명시) + PRG 1(보수적 포함). CAS 소진 규칙은 db §9.5와 짝인데 대응 검사기 불명 |
| §5 요청/응답 계약 (§5.4 포함) | 45 | 있음 | 명시 | 커버(부분) | §5.1=9(입력 상한 의무·매직넘버 위임 포함), §5.2=6, §5.3=1, **§5.4=29**(프로필 우선순위 4·wire 혼합 금지 2·신규 범위/preserve-established 관할 4·code-json 불릿 15·framework 헤더 경계 3). 소유자 최밀집: controller 소유, preserve-established=native 보존 관할(12-slot 계약 소유), shape 승인=명시적 사용자 승인, 열거 밖 조합=G1 표면화 STOP. §5.4 문면이 «레시피의 정본은 구현 스킬·검사기 계약»이라 검사기를 정본으로 지목 — check-api-error-controller-contract.py·check-error-centralization.py가 controller-owned 매핑 집행에 명백 대응(부분: wire shape 승인 자체는 게이트 소관). 인라인 결정 ID: «2026-08-13» 사례 각주, G1/G2·12-slot·STOP_FOR_USER_APPROVAL 용어 정의 내장. §5.4는 외부 피인용 있음 |
| §6 RFC 9457 에러 응답 형식 | 7 | 있음 | 없음 | 불명 | 적용 범위 자기 선언 3(§5.4 선택 범위에만 적용·code-json 범위 비적용·구현 형태는 §5.4 단서) + 확장 필드 무시 1 + §6.3 핵심 규칙 3. 관할 «범위»는 선언하나 판정 주체 명시는 없음 |
| §7 HTTP 헤더와 콘텐츠 협상 | 7 | 있음 | 없음 | 커버(부분) | 406/415 매핑 2(표 행) + 혼동 금지 1 + 인용 블록 4(별도 승인 범위 한정·Ninja-owned pre-body 경계·415 실확인·**전역 middleware/helper/handler 합성 금지**). 합성 금지는 문면이 implementation-django-ninja §6.3을 지목하고 check-ninja-boundary-middleware.py가 그 §6 집행을 자기 선언 — 체인 경유 명백 대응(부분). §7.2는 외부 피인용 3회 |
| §8 인증과 인가 | 21 | 있음 | 명시 | 불명 | §8.1=3(401 challenge 의무·확립 계약 보존+G1 회부·전역 합성 금지), §8.2 매핑 3(표 행), §8.3=3(쿼리 파라미터 비밀 금지 — §5.1과 중복), §8.4=12(Bearer 표 2 포함, challenge 규칙 재진술 중복 1 포함). 편차 처리 venue=G1 명시. 전역 합성 금지는 §7과 동일 규칙 반복이나 §8 문면엔 검사기 대응 체인 없음 → 불명 |
| §9 페이지네이션 | 7 | 있음 | 없음 | 비커버 | 선택 기준 매핑 3(표 행) + 실전 원칙 4 |
| §10 버전 관리 | 2 | 있음 | 없음 | 비커버 | «하나의 전략 일관 적용»·«문서화+마이그레이션 경로». «일반 패턴: URL path 메이저…»는 서술로 보고 제외 |
| §11 하위 호환성과 Deprecation | 17 | 있음 | 없음 | 비커버 | Breaking 판정표 9(표 행 — 파이프라인이 쓰는 판정 기준) + Deprecation 프로세스 5단계 + 실전 원칙 3(«추가는 자유, 제거는 금지» 포함) |
| §12 Rate Limiting | 8 | 있음 | 명시 | 불명 | 알고리즘 매핑 4(표 행) + 실전 원칙 4(Retry-After 보존·전역 합성 금지·controller 소유 — §5.4 framework 경계와 중복 규칙). controller 소유 명시 |
| §13 멱등성 키 (Idempotency-Key) | 24 | 있음 | 명시 | 커버(부분) | §13.2 동작 방식 6(presentation status 소유 규칙 내장), §13.3=12(계약 결정 의무 1+표 내장 3+replay 소유권 5+fingerprint 3), §13.4=6(**채택은 G0/G1 사용자 결정·미요청 기본 미적용** 포함). 소유자: presentation controller가 status·매핑 소유, 중앙 error handler 소유 금지, 채택=사용자 결정. check-idempotency-scope-creep.py가 채택 게이트를 집행하고 자기 문면에 «기존 확립된 멱등 계약은 존중 — §13» 참조 → 부분 커버. db §9.6 Idempotency storage와 규칙 쌍(상호 § 참조) |
| §14 OpenAPI | 4 | 있음 | 없음 | 커버(부분) | 반영 의무 1(+9개 표면 목록) + 실전 원칙 3. check-openapi-error-declaration.py(«OpenAPI 오류 계약 결정적 백스톱»)가 표면 목록 중 에러 프로필 항목에 명백 대응 — 부분 |
| §15 참고 문헌 | 0 | 있음 | 없음 | 비커버 | |

소계: 16절 · 166문장.

---

## 4축 집계 (39절 기준)

| 축 | 값 |
|---|---|
| ①앵커 | 있음 29 · 없음 10 (없음 = SKILL 8절 + 목차 2절) |
| ②소유자 | 명시 8 · 없음 31 (명시 = db SKILL 원칙, db §9, api SKILL 원칙, api §4·§5·§8·§12·§13) |
| ③백스톱 | 커버 5 · 불명 7 · 비커버 27 (커버 = db §9, api §5·§7·§13·§14 — **전부 부분 커버**) |
| ④쌍둥이 | 존재 39 · 부재 0 |

---

## 특이 발견

1. **규범 극단 집중**: 310문장 중 db §9(43)·api §5.4(29)·api §13(24)·api §8(21) 네 클러스터가 117문장(38%). 나머지 절 다수는 교과 지식(규범 0~7)이라, 온톨로지 레지스트리 대상은 사실상 «게이트·소유권·경계» 클러스터에 한정된다.
2. **문서→검사기 참조 0회, 대응은 역방향 단방향**: 4파일 문면에 `check-*.py` 이름이 한 번도 없다. 대응 근거는 전부 검사기 쪽 docstring(check-idempotency-scope-creep.py → db §9.6·api §13 명시)이거나 참조 체인(api §7.2 → implementation-django-ninja §6.3 → check-ninja-boundary-middleware.py). 백스톱 커버 5절도 전부 부분 커버.
3. **이미 존재하는 ID 체계가 산문에 내장**: final.md §N 앵커(외부 피인용: db §9.5 9회, §9.7·api §7.2 각 3회, §9.6 2회 등), 이슈 번호(#529·#626), 날짜 결정 각주(«2026-08-13»), 게이트·계약 용어(G0/G1/G2·12-slot·STOP_FOR_USER_APPROVAL, 검사기측 D50·D59·C3). 온톨로지의 룰 ID 후보가 이미 존재하나 표기가 4종 혼재.
4. **피인용 허브 절에 소절 앵커 부재**: db §9.5는 최다 피인용(9회)인데 내부가 «엔진 의존성 단락», «위 낙관적 동시성 메커니즘» 같은 산문 포인터로만 구분된다(§9.5.x 없음). api §5.4도 동일(불릿·굵은 소제목만).
5. **동일 규칙의 다중 복제**: 정규화 우선 규칙 4곳(db SKILL 불릿1·§3.4·§4.2·§5), 전역 handler/helper 합성 금지 4곳(api §5.4·§7·§8×2·§12), 쿼리 파라미터 비밀 금지 2곳(api §5.1·§8.3), 401 challenge 의무 3곳(api §8.1 표·불릿·§8.4). SKILL 핵심 운영 원칙은 구조적으로 final.md 요약-복제라 표류 위험 상시.
6. **쌍둥이는 사실상 동기화 상태**: references/final.md 2건은 codex판과 바이트 동일. SKILL.md 2건만 차이 — codex판은 `user-invocable: false` 제거 + `architecture-ddd` → `dddjango-architecture-ddd` 개명 표기(의도된 이름 격리, 2c64672 커밋 계열). 표류 아님.
7. **규칙 쌍이 두 문서에 분산**: db §9.5 낙관적 동시성 ↔ api §4.2 CAS 소진 status, db §9.6 Idempotency storage(stored result) ↔ api §13.3 replay/status 소유 — 서로 § 번호로 상호 참조하며 한쪽만 고치면 깨지는 결합. 위임처 표기도 혼재(`dddjango:architecture-ddd` 콜론 접두 vs `architecture-db` 무접두, codex판은 `dddjango-` 접두).
