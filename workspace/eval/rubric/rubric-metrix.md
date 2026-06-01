# 채점 결과지 템플릿 (rubric-metrix)

> 채점할 때 이 파일을 `results/`로 복사해 `날짜시간-smoke{N}-{claude|codex}.md`로 만들고 채운다.

## 작성법

- **채점은 반드시 `EVAL-METHOD.md`로 한다** — 항목별 레인(결정/의미)·사전식 집계·치명 게이트·마스크 C를 그 문서 절차대로 적용한다. 이 표는 그 산출을 옮겨 적는 *보고 뷰*다.
- **클로드·코덱스는 따로 채점한다** — 한 런타임 = 한 파일. 한 파일에 두 런타임 섞지 않는다.
- **채점 결과 파일** — `results/` 폴더에 만든다. 파일명 = `날짜시간-smoke{숫자}-{claude|codex}.md` (형식 `YYYYMMDD-HHmm-smoke{N}-{claude|codex}.md`, 예: `20260602-1530-smoke3-claude.md` / `20260602-1530-smoke3-codex.md`).

### 칸 작성
> **판정 범례(이모지)**: ✅ PASS · ❌ FAIL · 🟡 WEAK · ⏸️ 보류 · ➖ 해당 레인 없음(N/A). 결정·의미·종합 칸은 이 이모지로 적는다.
- **Result** = 그 런타임이 그 항목을 *실제로 어떻게 했는지* 한 줄. 근거(`파일:줄` + 무슨 코드/구조)를 **사실만**. 평가·이유 금지 — "무엇을 했나"만.
- **결정** = 결정 레인(스크립트/grep) 판정. ✅/❌. 그 항목에 결정 레인이 없으면 ➖.
- **의미** = 의미 레인(grader가 코드 읽고 판정) 판정. 치명 항목 = ✅/❌(🟡 금지), 비치명 = ✅/🟡/❌. 의미 레인이 없으면 ➖.
- **종합** = 그 항목 *최종 판정*(사전식 집계 입력, EVAL-METHOD §2). **결정·의미 중 하나라도 ❌이면 ❌**; 둘 다 ✅(또는 한쪽 ➖ + 한쪽 ✅)면 ✅; 비치명 WEAK는 🟡. 특히 **`결정=✅ ∧ 의미=❌`(의미적 변종)도 ❌**(§2.2) — 이때 `Result` 끝에 `[의미적 변종]` 표기. **치명 항목 종합 ❌ 1개 = 픽스처 전체 FAIL.**
- **S-NINJA** = HTTP/JSON API가 하나도 없으면 차원 전체 ➖.

### 판정을 어떻게 얻나 (레인은 `RUBRIC.md`를 따름)
- **결정** → `python3 workspace/eval/tools/check-structure.py ~/Desktop/dddjango-smoke{N}-{claude|codex}` 등 스크립트/grep 결과로 기계 판정.
- **의미** → grader가 코드를 읽고 판정(SD-1 빈혈 등 grep 불가). EVAL-METHOD §1.0 역할분리 + N_grader≥3(적대 1).
- **FC** → 코드를 골든표(`FC-GOLDEN.md`)로 실제 실행 / mutation 주입해 테스트 red 확인.

## A. TIER-S 척추 — DDD 도메인 충실도 (S-DDD)

| ID | 항목 | §근거 | Result | 결정 | 의미 | 종합 | 치명 |
|---|---|---|---|---|---|---|---|
| **SD-1** 빈혈: 판정 소유 | 핵심 비즈 규칙·불변식이 도메인(애그리거트/도메인서비스)에 메서드로 존재 | §3.2·§3.1 |  |  |  |  | 치명 |
| **SD-2** 빈혈: 프로덕션 호출 | 응용서비스가 *조회→도메인메서드→저장*으로 그 판정을 실제 호출 | §3.2·§3.6 |  |  |  |  | 치명 |
| **SD-3** 빈혈: 무복제 | 비즈 판정이 인프라 SQL/ORM에 복제 안 됨(경합 가드 version/CAS만) | §3.2 |  |  |  |  | 치명 |
| **SD-4** 애그리거트 경계 | 1트랜잭션 1애그리거트(또는 동일DB 예외 명시)·최소 크기·타 애그리거트 ID 참조·일관성 방식 적정 | §3.3 규칙1~4 |  |  |  |  | 치명 |
| **SD-5** 모델 표현력 | 값객체 불변·도메인서비스 무상태(애그리거트 비의존)·식별자가 유비쿼터스 언어 | §3.1·§3.5·§2.3 |  |  |  |  | 치명 |
| **SD-6** 계층 순수성(P1a 포함) | domain이 HTTP/ORM/프레임워크 import 0; 예외→status 변환이 presentation 단일점 | §5.1·§6.1; ninja §2.2·§6.2 |  |  |  |  | 치명 |
| **SD-7** 컨텍스트 통신 | 타 BC는 `published_service`(OHS)/ACL 포트로만, 직접 import 0 | §3.2(3)·§2.5 |  |  |  |  | 치명 |

## B. TIER-S 척추 — houserules 충실도 (S-HR)

| ID | 항목 | §근거 | Result | 결정 | 의미 | 종합 | 치명 |
|---|---|---|---|---|---|---|---|
| **SH-1** 컨테이너 | 신규 앱이 `application/<app>/` 하위 | §0-1 |  |  |  |  | 치명 |
| **SH-2** 4계층 | `{domain,application,infra,presentation}_layer/` 물리 분리 | §0-2 |  |  |  |  | 치명 |
| **SH-3** 종류 폴더 | 종류 2차 폴더(빈 패키지 허용), ORM/포트/리포가 평면 `.py` 아님 | §0-3·§0-4 |  |  |  |  | — |
| **SH-4** Django앱 위치 | `models.py`·`migrations/`가 `infra_layer/django_<app>/`; AppConfig `name`=점경로·`label` | §0-5 |  |  |  |  | 치명 |
| **SH-5** ORM 명명 | ORM `<Name>Model`, 도메인 bare | §0-6·§4 |  |  |  |  | — |
| **SH-6** 포트/구현 명명 | 추상=개념+역할접미사; 구현=기술접두+base명 일치; `Interface`/`Impl`·파일명 약어 0 | §4 |  |  |  |  | — |
| **SH-7** 협력 포트 위치 | 협력 포트가 `domain_layer/<agg>/port/` | §2 |  |  |  |  | 치명 |
| **SH-8** ACL 분리 | ACL이 `infra_layer/acl/`(+domain `port/`), `repository/`에 안 섞임 | §2·§3 |  |  |  |  | — |
| **SH-9** 단일 레이아웃 | 한 앱이 두 레이아웃 안 가짐 | §1.4 |  |  |  |  | — |
| **SH-10** 테스트 의미군 | `test/{unit,integration,e2e}` 분리; HTTP=integration; 평면나열 0 | §1.3 |  |  |  |  | — |

## TIER-S(조건부) — django-ninja 충실도 (S-NINJA)

| ID | 항목 | §근거 | Result | 결정 | 의미 | 종합 | 치명(조건부) |
|---|---|---|---|---|---|---|---|
| **NJ-1** 스택 채택 | 신규 HTTP/JSON API를 Ninja(`NinjaAPI`+`Router`)로; plain view·`JsonResponse`·DRF로 안 샘; 기존 스택 존중 | §1.1·§10 |  |  |  |  | 치명 |
| **NJ-2** operation 얇음(비-오류) | operation 본문에 비즈로직·상태전이·ORM·수동 본문파싱·수동 필드검증 0; service 호출 + schema 매핑만 | §1.3·§2.2 |  |  |  |  | 치명 |
| **NJ-3** Schema 입출력 분리 | 요청·응답을 `Schema`/`ModelSchema`로 분리, 도메인 엔티티 직접 직렬화 0 | §2.2·§3.1 |  |  |  |  | — (강) |
| **NJ-4** status별 response 선언 | 가능한 모든 status를 `response={...}`에 schema 선언(OpenAPI 가시성) | §2.2·§8 |  |  |  |  | — (강) |
| **NJ-5** operation 문서화 | `summary`(+`tags`) 부여, 무정보 반환타입(`-> object`) 금지 | §2.2 |  |  |  |  | — (경미) |
| **NJ-6** ninja 버전 핀 표기 | 신규 도입 시 매니페스트에 버전 핀, 기존 관례와 일치 | §2.1 |  |  |  |  | — (경미) |

## TIER-S(핵심) — 기능 정확성 (FC)

| ID | 항목 | Result | 결정 | 의미 | 종합 | 치명 |
|---|---|---|---|---|---|---|
| **FC-1** 골든 오라클 | 평가자가 *명세 무관* 외부 행위표를 사전등록(예: 재고10·주문3→201∧남은7 / 재고2·주문5→409∧재고불변∧주문0)하고 코드를 그 표로 직접 두드림 |  |  |  |  | 치명 |
| **FC-2** 테스트 비-vacuous | 핵심 로직에 mutation 주입(차감 부호·`>=`→`>`·status 값) 후 테스트 red 확인 |  |  |  |  | 치명 |
| **FC-3** 도메인 정합(negative gate) | 명백한 도메인 오류 부재 — 음수 재고 허용·차감 방향 역전·주문↔재고 인과 역전 등 |  |  |  |  | 치명 |

## D. TIER-Q 품질

| ID | 항목 | §근거 | Result | 결정 | 의미 | 종합 |
|---|---|---|---|---|---|---|
| **Q-1** 스코프/과설계·G1 | 요청 외 기능 발명 0(멱등성·멀티라인·합산이 task 요구였나); 양방향(과소=빈혈은 SD / 과잉=무거운 패턴 미도입 §6.8); 고-blast 트레이드오프를 G1 상정(사후기록≠상정) | ddd §6.8·houserules §6.1 |  |  |  |  |
| **Q-2** API 계약 | status/problem(RFC 9457) 일관·버전 정책 일관·콘텐츠협상 근거 | architecture-api §4~14 |  |  |  |  |
| **Q-3** §9.6 형식+테스트 실현 | Risky Write 8행 다뤄짐(N/A 근거); 선언 동시성 기준이 **실제 테스트로 실현**·소진→409 경로·결정적 CAS 스파이 | architecture-db §9.6·implementation-test §20.5 |  |  |  |  |
| **Q-4** 메커니즘 소유권 **[🔴 치명 — v3 승격]** | 커스텀 DB 백엔드/`DatabaseWrapper`/PRAGMA/몽키패치 0 | architecture-db §9.5·§16.4 |  |  |  |  |
| **Q-5** 마이그레이션 안전 | 기존 0001 불변·`db_table`/`label` 보존·expand 단계·backfill | architecture-db §11 |  |  |  |  |
| **Q-6** 테스트/TDD | `check`+`test` 그린바·인수가 명세 행위 덮음·의미군 분리 | implementation-test·discipline-tdd |  |  |  |  |
| **Q-7** 경미 | 빈 종류폴더 누락·타입힌트·주석 언어 일관(§5)·의존성 핀(§6.2) | houserules §5·§6.2 |  |  |  |  |
