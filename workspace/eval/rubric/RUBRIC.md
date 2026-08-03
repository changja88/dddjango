# dddjango 평가지 v4 candidate — 규칙 준수 + 기능 정확성 (평가 항목)

> **상태**: `candidate` · **NOT ACTIVE** · **NOT FROZEN** · **SCORING PROHIBITED**.
> 사용자 명시 freeze 전에는 어떤 fixture도 이 문서로 채점·집계하지 않는다.
> **후보 epoch/profile/version**: `2026-08-03-code-json` / `dddjango-code-json` /
> `v4-candidate`. 결과 identity는
> `epoch + error profile + rubric version + dimension ID`다.
> **v3 재현 경계**: v3 기준과 historical 결과는 full SHA
> `d1fce5b43b13f8447b2a4b78f6c94e74efe8ff19`에서 재현한다. 기존 결과 14개는
> 불변이며 v4 의미로 소급 판정하지 않는다.
> **목적(사용자 확정)**: 산출물이 ① **우리 플러그인의 규칙(DDD·houserules·django-ninja)을 얼마나 잘 지키는가** + ② **요청 기능을 올바르게 구현했는가**를 측정한다. *baseline 대비 차별가치는 안 잰다 — 규칙 준수가 핵심.* 기능 정확성은 잰다(형태만 보면 "재고 늘어나는 주문 API"도 통과하므로).
> **PASS 바 = 표준 규칙(앵커 아님)**: 판정 기준은 각 항목 §근거의 *표준 조항*이다. §E 앵커는 *규칙 충족/위반의 예시*일 뿐 임계값이 아니다 — "플러그인이 실제로 낸 수준"을 바로 두지 않는다(순환 방지). 새 산출물은 표준 조항으로 채점하고 앵커는 참고.
> **명시적 비측정(과대주장 제거)**: baseline 대비 가치(절대 준수만 봄) · 미시 가독성·복잡도(유지보수성은 구조 대리까지만) · 보안(단 *에러 응답에 스택트레이스·내부경로·SQL 누출 0*은 항상 치명) · 명세 내적 품질(후순위). 이들은 평가지 밖/위임/후속.
> **범위**: 이 문서=평가 *항목*. 채점/집계/bisect/완료=`EVAL-METHOD.md`.
> **산출 형식**: 채점 결과지(`results/*.md`)의 섹션 순서·칼럼·필수 단서는 `EVAL-METHOD.md §6` 표준 템플릿을 따른다. 결과지 차원-섹션 순서 = 이 문서 **A→B→NINJA→FC→C→D**(E 앵커는 루브릭 전용·결과지 미포함). **TIER-OBS(에러 경로 라이브 관측)는 이 차원 순서 *밖* 별도 트랙**(라이브 런 한정·결과지에선 의미변종 메타 뒤 배치·아래 §TIER-OBS).
> **레인 표기**: 결정=구조-인지 스크립트/grep, 의미=서브에이전트 grader. 치명=치명 게이트(이진 PASS/FAIL, WEAK 금지).

---

## A. TIER-S 척추 — DDD 도메인 충실도 (S-DDD)
표준: `dddjango/skills/architecture-ddd/references/final.md`

| ID | 항목 | §근거 | PASS | FAIL | 레인 | 치명 |
|---|---|---|---|---|---|---|
| **SD-1** 빈혈: 판정 소유 | 핵심 비즈 규칙·불변식이 도메인(애그리거트/도메인서비스)에 메서드로 존재 | §3.2·§3.1 | spec 핵심 규칙이 domain_layer 코드에 구현 | 판정이 도메인에 없고 응용/인프라/스키마에만 | 의미(+grep) | ✅ |
| **SD-2** 빈혈: 프로덕션 호출 | 응용서비스가 *조회→도메인메서드→저장*으로 그 판정을 실제 호출 | §3.2·§3.6 | 프로덕션 쓰기 경로가 도메인 판정 메서드를 호출 | 도메인 메서드가 있어도 응용이 안 부르고 `.update()`/raw SQL로 우회(죽은 도메인 메서드) | 의미(호출추적) | ✅ |
| **SD-3** 빈혈: 무복제 | 비즈 판정이 인프라 SQL/ORM에 복제 안 됨(경합 가드 version/CAS만) | §3.2 | 인프라엔 version/CAS만, 판정 복제 0 | `stock__gte=` 등 비즈 조건이 WHERE/필터/F-식에 복제 | 결정+의미 | ✅ |
| **SD-4** 애그리거트 경계 | 1트랜잭션 1애그리거트(또는 동일DB 예외 명시)·최소 크기·타 애그리거트 ID 참조·일관성 방식 적정 | §3.3 규칙1~4 | 작은 경계·ID 참조·일관성 선택 근거 있음 | 거대 애그리거트 / 객체 직접 참조(도메인 FK 결합) / 근거 없는 복수 애그리거트 수정 | 결정(ID)+의미 | ✅ |
| **SD-5** 모델 표현력 | 값객체 불변·도메인서비스 무상태(애그리거트 비의존)·식별자가 유비쿼터스 언어 | §3.1·§3.5·§2.3 | frozen 값객체 / 무상태 서비스 / 비즈 용어 네이밍 | 가변 값객체(setter) / 애그리거트가 서비스 주입받음 / CRUD·매직 네이밍 | 결정+의미 | ✅ |
| **SD-6** 계층 순수성(P1a 포함) | domain/application이 HTTP·ORM presentation 타입을 모르고, 알려진 BC 예외→status mapping은 해당 controller가 직접 소유 | §5.1·§6.1; ninja §2.2·§6.2 | domain/application HTTP 무지 + 해당 controller가 알려진 구체 BC 예외를 직접 catch해 `Status` 반환 | domain/application의 HTTP·framework import 또는 status DTO 흐름 / mapping helper·handler로 소유 이동 / controller가 raw 오류 응답 생성 | 결정+의미 | ✅ |
| **SD-7** 컨텍스트 통신 | 타 BC는 `published_service`(OHS)/ACL로만; 교차 결합(모델·예외)은 ACL에 격리 | §3.2(3)·§2.5 | OHS 소비, 또는 OHS 미이주 시 `infra_layer/acl/` ACL이 업스트림 import·번역(모델·**예외**까지 ACL 격리·도메인은 포트 ABC 의존) | **ACL 밖**(도메인/응용/presentation)이 타 BC `domain_layer`/`infra_layer`(예외 포함) 직접 import / OHS 존재하는데 미경유 / ACL이 번역 안 하고 누수 | 결정+의미 | ✅ |

> **SD-6 주의(DR-24·Goodhart 차단)**: 결정적 checker는 import와 직접형 계약을
> 좁게 증명하지만, `status: int` 같은 plain DTO가 HTTP 의미를 숨긴 채 application을 흐르는
> 변종까지 자동으로 증명하지 못한다. 의미 레인은 checker exit 0과 무관하게 domain/application
> 값 흐름과 해당 controller의 직접 mapping을 줄 인용으로 확인한다. import가 없어도 HTTP status
> 의미를 실은 DTO가 계층을 흐르면 SD-6 치명 FAIL이며 WEAK로 낮추지 않는다. 중앙 handler나
> application 예외 재발생은 v4 PASS 근거가 아니다.

> **SD-7 주의(미스캘리브 교정 2026-06-02)**: 결정 레인(`check-structure.py`)은 타 BC 내부 import를 신호로 내나 **`infra_layer/acl/` 미이주 ACL이 업스트림(catalog) 모델·리포·예외를 import·번역하는 건 표준 §2(houserules `final.md` §2 컨텍스트 간 통신 — 'OHS 미이주 시 ACL' 조문) 명시 허용 = FAIL 아님**(주의신호로만 분리; 도메인은 포트 ABC 의존·번역이 ACL 격리 시). **진짜 FAIL = ACL *밖*(도메인/응용/presentation)이 타 BC 내부를 직접 import**(예: 예외 번역이 ACL에 안 갇혀 누수) / OHS 존재하는데 미경유 / ACL 도메인누수. *근거*: smoke4-claude(catalog 결합이 ACL에 격리 → **PASS**) ↔ p1a-v3-claude(catalog 예외가 presentation·application으로 누수 `order_api_router.py:26`·`create_order_app.py:17` → **FAIL**)로 갈린다 — 과거 "Claude ACL infra import=FAIL" 앵커는 미스캘리브 오판이었다. **published_service 내부 구조**(서비스 1차 `<service>_service/`·contract 3패키지(request/response 연산당 1파일)·시그니처 3연조·published 계약 타입의 application_layer 관통 금지)는 houserules `final.md` §2 OHS 내부 구조 절(2026-07-07 신설·2026-07-08 3패키지 개정)이 규정한다 — SD-7 관측 시 함께 본다(관통·contract 계층 import는 `check-context-isolation` 확장 슬라이스가 결정 레인).

## B. TIER-S 척추 — houserules 충실도 (S-HR)
표준: `dddjango/skills/discipline-houserules/references/final.md` + `SKILL.md`

| ID | 항목 | §근거 | PASS | FAIL | 레인 | 치명 |
|---|---|---|---|---|---|---|
| **SH-1** 컨테이너 | 신규 앱이 `application/<app>/` 하위 | §0-1 | 신규 앱이 `application/` 하위 | 신규 앱이 루트(마스크 C 적용) | 결정 | ✅ |
| **SH-2** 4계층 | `{domain,application,infra,presentation}_layer/` 물리 분리 | §0-2 | 4계층 존재 + **touched 데이터소스도 4계층 빈 패키지 실현**(유스케이스 없으면 `application_layer`만 빈 계층) | 누락/평면 / **데이터소스라며 계층 폴더 생략**(§0-2·§632-(2) 개정) | 결정 | ✅ |
| **SH-3** 종류 폴더+거주 명명 | 종류 2차 폴더 전체(빈 패키지로 항상·`api`/`schema`/`acl`/`port` 포함), ORM/포트/리포가 평면 `.py` 아님; **거주 객체 명명(시점: ≥1.4.0 산출분): command/=`…Command`·query/=`…Query`·dto/=`@dataclass …Request`, 모두 `execute(request)`·repository/port 의존** | §0-3·§0-4·§4 | 종류 폴더 구조 + R/C/Q 명명 일치 + **데이터소스 BC도 종류 폴더·애그리거트 골격(`domain_layer/<aggregate>/` ORM 모델명 도출) 빈 패키지 실현** | 종류 2차 폴더(`entity`·`value_object`·`repository`·`command`·`query`·`dto`·`api`·`schema`)가 빈 패키지로라도 부재(평면 `.py`로 접음·골격 미생성) / **touched 데이터소스가 `domain_layer/<aggregate>/` 애그리거트 빈 골격 미생성**(§632-(2) 2026-06-08 개정·골격 무조건은 그 이후 산출분) / **command/에 `…Service`·자유함수·query/ selector 함수·dto/ 비-`@dataclass`(≥1.4.0 산출분)** | 결정(폴더·골격)+의미(명명) | ✅ |
| **SH-4** Django앱 위치 | `models.py`·`migrations/`가 `infra_layer/django_<app>/`; AppConfig `name`=점경로·`label` | §0-5 | 모델/마이그가 `infra_layer/django_` | 루트/앱루트/도메인에 `models.py`(마스크 C 적용) | 결정 | ✅ |
| **SH-5** ORM 명명 | ORM `<Name>Model`, 도메인 bare | §0-6·§4 | 명명 분리 | 혼동(도메인에 Model접미사·ORM이 bare) | 결정 | — |
| **SH-6** 포트/구현 명명 | 추상=개념+역할접미사(`Port`/`Repository`/`Gateway`); 구현=확립 패턴명(`Repository`/`Gateway`) 유지+기술접두·일반 포트는 `…Adapter`; `Interface`/`Impl`·파일명 약어 0 | §4 | 규약 준수 | `Interface`/`Impl` / `*_repo.py` / 일반 포트 구현이 `Port` 유지(Adapter 아님)·개념 base 불일치 | 결정 | — |
| **SH-7** 협력 포트 위치 | 협력 포트가 `domain_layer/<agg>/port/` | §2 | `domain_layer/.../port/` | `application_layer`/`infra_layer`에 위치 | 결정 | ✅ |
| **SH-8** ACL 분리 | ACL이 `infra_layer/acl/`(+domain `port/`), `repository/`에 안 섞임 | §2·§3 | acl 분리 | repository에 번역 어댑터 혼합 | 결정+의미 | — |
| **SH-9** 단일 레이아웃 | 한 앱이 두 레이아웃 안 가짐 | §1.4 | 단일 레이아웃 | `test`+`tests` 공존·`src`+`apps` 혼용 | 결정 | — |
| **SH-10** 테스트 의미군 | `test/{unit,integration,e2e}` 분리; HTTP=integration; 평면나열 0 | §1.3 | 의미군 분리·올바른 배치 | 평면 나열 / 의미 오배치 | 결정+의미 | — |

---

## TIER-S(조건부) — django-ninja 충실도 (S-NINJA)
표준: `dddjango/skills/implementation-django-ninja/references/final.md` + `SKILL.md`
> **조건부**: 기능에 HTTP/JSON API operation이 하나라도 있을 때만 채점. 없으면(서버렌더·CLI·배치·순수도메인) 차원 **N/A**(점수 산입 0, FAIL 아님).
> **"operation" 어휘 정의(NJ-2·SD-6·NJ-7·1회)**: 이 평가지 전반에서 **operation = 함수형 ninja operation(`@router.post def …`) *또는* ninja-extra 컨트롤러 메서드(`@route.post def …(self, …)`)**를 가리킨다. "operation 본문"은 두 형태 모두의 *메서드/함수 본문*이다 — 컨트롤러 클래스로 전환해도 **메서드 내부의 비즈로직·상태전이·ORM·수동 본문파싱·수동 필드검증·raw 응답 생성**은 함수형 operation과 *동일 기준*으로 잡힌다(클래스 래핑이 면죄부 아님). 이 정의는 어휘 명확화일 뿐 NJ-2/SD-6/NJ-7 판정기준을 바꾸지 않는다(동결 무관).
> **비중복 보증**: domain/application HTTP 무지와 mapping 소유 위치는 **SD-6**,
> 선택된 error profile의 wire/status/header/version 일관성은 **Q-2**, 일반 의존성 핀은
> **Q-7**이 소유한다. NJ-2는 비오류 operation의 얇음을 보고, **NJ-7은 해당 controller의
> 오류 직접 계약 형태**(좁은 try·구체 catch·직접 ErrorOut/Status·framework default)를 본다.
> 즉 SD-6은 계층과 소유자, NJ-7은 그 소유자가 구현한 직접 경계의 완전성을 판정한다.

| ID | 항목 | §근거 | PASS | FAIL | 레인 | 치명(조건부) |
|---|---|---|---|---|---|---|
| **NJ-1** 스택 채택 | 신규 HTTP/JSON API를 Ninja(`NinjaAPI`/`NinjaExtraAPI`)로 — (`Router` ∨ `@api_controller`/`register_controllers`) operation/컨트롤러; plain view·`JsonResponse`·DRF로 안 샘; 기존 스택 존중 (신규 표준=클래스 컨트롤러, 함수형 `Router`=레거시/415 격리 예외 — 둘 다 PASS) | §1.1·§10 | 신규 JSON API가 ninja Router operation **또는** ninja-extra `@api_controller` 컨트롤러로 등록 | 신규 JSON API가 plain `django.views`/`JsonResponse`·DRF로 구현(greenfield인데) | 결정 | ✅ |
| **NJ-2** operation 얇음(비-오류) | operation 본문에 비즈로직·상태전이·ORM·수동 본문파싱·수동 필드검증 0; service 호출 + schema 매핑만 | §1.3·§2.2 | schema 바인딩→service 호출→응답 매핑만 | operation에 `json.loads`/수동검증/ORM/비즈 분기 | 의미(+grep) | ✅ |
| **NJ-3** Schema 입출력 분리 | 요청·응답을 `Schema`/`ModelSchema`로 분리, 도메인 엔티티 직접 직렬화 0 | §2.2·§3.1 | 입·출력 별도 Schema, 도메인→DTO 매핑 | 도메인 객체 직접 `response=` / 내부필드 누출 | 결정+의미 | — (강) |
| **NJ-4** BC 오류 response 정합 | controller가 실제로 직접 반환하는 BC 오류 status를 같은 BC `<Bc>ErrorOut>`으로 `response={...}`에 선언; framework 기본 오류를 BC Schema로 광고하지 않음 | §2.2·§8 | 직접 반환 BC status→동일 BC base 선언 + 직접 BC 반환 없는 framework 401/403/route 404/422/429/500 비광고 | 직접 반환 BC status 누락·다른 BC Schema / framework 기본 status를 ErrorOut으로 거짓 광고 / `openapi_extra`·사후 후가공 | 결정 | — (강) |
| **NJ-5** operation 문서화 | `summary`(+`tags`) 부여, 무정보 반환타입(`-> object`) 금지 | §2.2 | summary/tags + 의미있는 반환타입 | summary 없음 / `-> object`·어댑터 누수형 | 결정 | — (경미) |
| **NJ-6** ninja 버전 핀 표기 | 신규 도입 시 매니페스트에 버전 핀, 기존 관례와 일치 | §2.1 | `django-ninja==<버전>` 관례 일치 | 매니페스트 부재/무핀/표기 불일치 | 결정 | — (경미) |
| **NJ-7** BC 오류 직접 계약 | 알려진 BC 실패를 해당 controller가 좁은 application 호출 경계에서 직접 ErrorOut/Status로 변환하고 framework 오류는 기본 흐름 보존 | §6.2·§8 | application 호출 한 문장만 감싼 좁은 `try` + 구체 catch + direct no-arg concrete ErrorOut(또는 BC base 직접 생성) + `Status`; 미식별/framework 오류는 기본 처리 | 오류 helper·factory·custom handler·catch-all / bare·`Exception`·`BaseException` broad catch / raw `Response`·`JsonResponse`·dict 오류 응답 / 즉시 raise-catch 우회 | 결정+의미 | — (강) |

> **NJ-4 정확성 경계**: 검사는 실제 직접 반환 status→같은 BC base Schema까지 보증한다.
> 하나의 `<Bc>ErrorOut>`이 여러 status에 쓰여 각 status 문서에 BC Enum 전체 code subset이
> 과대 노출되는 것은 v4의 승인된 한계다. 이를 보완하려고 OpenAPI를 수동 후가공하지 않는다.
>
> **의도적 제외(표준이 강제 안 함·거짓양성 원천)**: operationId 명시(§8 "확인"일 뿐·자동생성),
> framework 기본 body의 exact snapshot, Idempotency/인증/페이지네이션 정책 자체(Q-2 위임).
> **앵커 한계(거짓양성 직결)**: NJ-2만 강한 양극 앵커(smoke2-codexB 극단 ↔ 준수 다수). **NJ-1·3·6은 8벌 전부 준수라 known-bad 부재** → 준수 강제 게이트로는 약함(동결 전 합성 반례/baseline plain-view 참조 결정).
> **🔴 에러 경로 정독(NJ-4·NJ-7·SD-6)**: 성공 path와 checker exit 0만 보고 PASS를
> 주지 않는다. controller의 application 호출, `try`/`except`, ErrorOut 생성, `Status`,
> `response={...}`를 함께 읽고 모든 오류 helper·factory·custom handler·catch-all을 검색한다.
> v4에서 handler나 raw `Response`/`JsonResponse`/dict 오류 응답은 정상 대안이 아니라 NJ-7
> FAIL이다. 실제 직접 반환하는 BC status가 같은 BC base로 선언되지 않거나, 직접 BC 반환 없는
> framework 오류가 ErrorOut으로 광고되면 NJ-4 FAIL이다.

## TIER-S(핵심) — 기능 정확성 (FC)
> 형태가 아무리 맞아도 *동작이 틀리면* 무가치다. FC는 코드가 **요청 기능을 실제로 올바르게** 하는지를 *명세와 독립된 외부 기준*으로 잰다 — 명세·코드·테스트가 같은 방향으로 틀린 순환(그린바 통과인데 기능 오류)을 차단. **치명 게이트.**

| ID | 항목 | PASS | FAIL | 레인 | 치명 |
|---|---|---|---|---|---|
| **FC-1** 골든 오라클 | 평가자가 *명세 무관* 외부 행위표를 사전등록(예: 재고10·주문3→201∧남은7 / 재고2·주문5→409∧재고불변∧주문0)하고 코드를 그 표로 직접 두드림 | 모든 골든 케이스 일치 | 하나라도 불일치(차감 방향·status·부작용) | 의미(외부 오라클 실행) | ✅ |
| **FC-2** 테스트 비-vacuous | 핵심 로직 mutation(차감 부호·판정 경계)과 controller 오류 status mutation 후 테스트 red 확인 | M1·M2 각각 red + M3에서 concrete default 또는 BC base constructor status 변조 시 HTTP/body status 단언 모두 red | mutation에도 green 또는 M3의 HTTP/body 단언 한쪽만 red | 결정(주입 실행) | ✅ |
| **FC-3** 도메인 정합(negative gate) | 명백한 도메인 오류 부재 — 음수 재고 허용·차감 방향 역전·주문↔재고 인과 역전 등 | 명백 오류 0 | 명백 도메인 오류 1+ | 의미 | ✅ |

> **FC vs SD 구분**: SD는 "*비빈혈 형태*"(판정이 도메인에 있나), FC는 "*그 판정이 맞나*"(동작이 정답인가). 비빈혈인데 *틀린* 모델(잘못된 불변식)은 SD PASS·FC FAIL로 갈린다 — 적대리뷰 CF-2(틀린 도메인 모델) 차단.
> **조건/사전등록**: 골든 표(FC-1)는 태스크별로 *채점 전에* 사전등록(method §과적합). FC-1·2는 fixture에 `.venv`·실행 가능 코드가 있을 때 실측.

---

## C. 기존규약 마스크 (S-HR 항목 판정 조건 — §1.1↔§1.2)
> 8벌 전부 `catalog/`가 평면 `startapp`으로 **시드**돼 있어, 평면 유지가 §1.1 존중인지 §1.2 위반인지로 SH 판정이 뒤집힌다. SH 항목(특히 SH-1·SH-4) 채점 시 다음을 **곱한다**:

- **신규 앱**(baseline에 없던, 런이 생성) → **§0 전부 강제**(존중 면제 없음).
- **기존 앱**(baseline에 있던) →
  - 런이 그 앱에 **새 판정·불변식을 얹었으면**(예: 재고 차감 판정) → §1.2 + ddd §3.2 "판정 소유→구조 이주" 발동. *그 판정 코드*는 표준 트리 대상(평면 유지 시 SH FAIL) + SD-1~3와 교차.
  - **판정은 안 얹었으나 *런이 건드렸으면*(diff에 새 마이그레이션·필드·제약)** → **§632-(2) 2026-06-08 개정으로 *깊이 면제는 폐지***: 데이터소스도 위치(`application/<app>/`)·4계층·`domain_layer/<aggregate>/`(ORM 모델명 도출) 애그리거트 빈 골격·종류 2차 폴더를 **빈 패키지로 무조건 실현**. 면제는 *판정 실내용(`.py`)*에만(빈혈 회귀 방지). 따라서 ① 루트 평면(`<app>/`)이면 **SH-1·4 FAIL** ② `application/<app>/`로 옮겼어도 4계층·애그리거트 골격·종류 폴더를 접으면 **SH-2·3 FAIL**. **루트 잔재 정정(발견1·cbvlive-codex)**: 모델을 셰임 이주(`Product=ProductModel`)·`MIGRATION_MODULES`로 옮겼어도 **루트에 앱 디렉터리(`apps.py`·`views.py`·`tests.py` 잔재)를 남기면 SH-1·4 FAIL**(`check-structure.py:89` 루트 `apps.py`→FAIL-신호가 정답; "모델 이주로 위치 충족" PASS 뒤집기 폐기 — 위치 충족 = 앱 패키지가 루트에서 완전 제거). **경계(migrations-only 핀 ⊥ 앱 잔재)**: 0001 히스토리 보존 목적 `MIGRATION_MODULES` 핀으로 **`migrations/`만** 루트에 남고 `apps.py`·`models.py`가 전부 이주했으면 **SH-1·4 PASS·Q-5 트레이드오프**(SH-4 의미 🟡); `apps.py`가 루트에 남으면 **SH-1 FAIL**(판별: 루트에 `apps.py` 유무).
  - **판정도 안 얹고 *런이 안 건드린* 무관 기존 앱** → §1.1 존중 → 평면 유지 = **위반 아님**(SH 면제).

> **조작화(v3)**: 이 "판정 적재" 판단은 `EVAL-METHOD.md §1.1.M`의 이진 하위질문(MQ1=런 diff에 핵심규칙 분기 추가? / MQ2=단순 상류 데이터소스?)으로 집행한다 — `MQ1=Y ∧ MQ2=N`이면 §1.2 발동. N_grader 경합 시 **보수적으로 *적재됨*(엄격)** + 인간 큐(치명 게이트 입력이므로).
>
> **위치·깊이 통합(개정 2026-06-08 — §632-(2) 면제 폐지)**: 이전엔 MQ1/MQ2가 *4계층 전개 의무*(애그리거트 골격)를 갈랐으나(MQ1=N이면 4계층 면제), **개정으로 touched 데이터소스는 위치·4계층·애그리거트 골격·종류 폴더가 모두 무조건**이다. MQ1/MQ2가 이제 가르는 것은 **판정 *실내용*(`.py` 코드)을 어디 두느냐**뿐: `MQ1=Y∧MQ2=N`이면 그 BC가 판정을 소유해 도메인 *실코드*가 채워지고(SD-1~3 교차), `MQ1=N`이면 도메인 골격은 *빈 패키지*로 남는다(빈혈 회귀 방지) — **그러나 골격·위치 자체는 양쪽 다 의무**. *런이 건드린(diff 포함)* 기존 앱은 MQ1=N이어도 루트 평면이면 **SH-1·4 FAIL**, `application/<app>/`로 옮겼어도 골격을 접으면 **SH-2·3 FAIL**. SH 면제 = 그 앱이 **런 diff에 없음(untouched)**일 때만(구 "MQ1=N이면 §1.2 면제가 깊이까지" 해석은 개정으로 폐기). 결정 레인: `check-app-container.py`(7번째·touched 루트 앱→exit 2)는 위치만, 골격 부재는 `check-layer-skeleton`(종류 폴더 확장)·SH-2/SH-3로 본다. **smoke6-claude(catalog touched·MQ1=N·루트 평면)·cbvlive-codex(루트 apps.py 잔재)는 SH-1·4 FAIL이 맞다.**

---

## D. TIER-Q 품질 (카운트 순위 — `EVAL-METHOD.md §2.4`; '가중치 수치' 미정의라 v3에서 카운트 기반 전환)

| ID | 항목 | §근거 | PASS | FAIL/WEAK | 레인 |
|---|---|---|---|---|---|
| **Q-1** 스코프/과설계·G1 | 요청 외 기능 발명 0(멱등성·멀티라인·합산이 task 요구였나); 양방향(과소=빈혈은 SD / 과잉=무거운 패턴 미도입 §6.8); 고-blast 트레이드오프를 G1 상정(사후기록≠상정) | ddd §6.8·houserules §1.1 | 요청 범위 내·미선택 패턴 근거 기록 | 요청 외 발명 / 무거운 패턴 남용 / 고-blast를 §Open Questions에만 | 의미(spec) |
| **Q-2** API 계약 | 선택된 error profile의 wire/status/header/version 일관성 | architecture-api §4~14 | profile 선택과 wire shape·HTTP/body status·표준 header·version 전환이 일관 | profile 혼합 / HTTP-body status drift / 승인 header·version 전환 누락 | 의미 |
| **Q-3** §9.6 형식+테스트 실현 | Risky Write 8행 다뤄짐(N/A 근거); 선언 동시성 기준이 **실제 테스트로 실현**·소진→409 경로·결정적 CAS 스파이 | architecture-db §9.6·implementation-test §20.5 | 8행 + 동시성 전 분기 결정적 테스트 | 8행 누락 / 약속 테스트 부재 / 소진 경로 미테스트 | grep+의미 |
| **Q-4** 메커니즘 소유권 **[🔴 치명 — v3 승격]** | 커스텀 DB 백엔드/`DatabaseWrapper`/PRAGMA/몽키패치 0 | architecture-db §9.5·§16.4 | 표준 ORM만 | 커스텀 백엔드/PRAGMA/몽키패치 | 결정 |
| **Q-5** 마이그레이션 안전 | 기존 0001 불변·`db_table`/`label` 보존·expand 단계·backfill | architecture-db §11 | 이력 불변·호환 변경 | 기존 0001 재작성 / 테이블 rename 위험 | 결정+의미 |
| **Q-6** 테스트/TDD | `check`+`pytest` 그린바·인수가 명세 행위 덮음·의미군 분리·**pytest 관용구**(함수형·`@pytest.mark.django_db`)·mock 도구 `mocker`·ORM 영속 factory_boy(만능 아님) | implementation-test·discipline-tdd | pytest 그린바+커버리지+생태계 준수 | 실패/에러 / 행위 누락 / raw `unittest.mock`·Django `TestCase` 폴백(greenfield) | 결정(실행)+의미 |
| **Q-7** 경미 | 빈 종류폴더 누락·**공개 표면 변수 어노테이션**(§4 — 모듈/클래스 변수 리터럴 상수 첫 대입 필수·함수 지역변수 권장·면제는 §4 참조)·주석 언어 일관(§5)·의존성 핀(§6.2) | houserules §4·§4.1·§5·§6.2 | 준수 | 경미 흠(WEAK) | 결정(check-public-surface-annotation)+의미 |

> **Q-4 치명 처리(v3)**: Q-4는 TIER-Q에 배치돼 있으나 **치명 게이트**다 — `EVAL-METHOD.md §2 step2`에서 처리(FAIL→픽스처 전체 FAIL)하고 §2.4 Q 등급(카운트)에는 **불산입**. 나머지 Q-1·2·3·5·6·7만 품질 등급에 들어간다.

---

## TIER-OBS(라이브 전용·비채점) — 에러 경로 라이브 관측 트랙

> **성격**: 라이브 런에서만 적용할 비채점 관측 후보다. **A~D의 정확히 34개 채점
> 차원·치명 게이트 밖**이며 35번째 차원이 아니다. v4는 아직 NOT ACTIVE / NOT FROZEN이므로
> EP probe도 현재 실행·채점하지 않는다. 사용자 freeze 뒤 라이브 관측을 시작하더라도 probe
> 결과는 차원 점수나 종합 FAIL로 환산하지 않고 라이브 축과 잔여흠 원장에만 기록한다.
> **정본 분리(SSOT)**: 아래 표는 항목과 필수 계약의 요약이다. **상세 N/A 규칙·probe 어댑터·판정 절차의 단일 정본은 `EVAL-METHOD.md §4.3.1`**이다. 매 라이브 채점지 **필수 섹션화 집행 = `EVAL-METHOD.md §6.1` #9.5**.
> **NJ-7과 구분(이중계상 차단)**: NJ-7은 controller의 BC 오류 직접 계약을 정적·의미
> 레인에서 판정하고 라벨에 반영한다. EP는 framework/BC 종단의 실제 status·shape를 관측만
> 하며 라벨에 반영하지 않는다. raw catch-all은 어느 쪽에서도 요구하지 않는다.

| ID | 관측 항목 (무엇을 두드리나) | 비고 |
|---|---|---|
| **EP-1** 깨진 본문 | malformed body가 framework 기본 400이고 BC ErrorOut shape/code가 아님; body exact snapshot 금지 | HTTP operation 없으면 N/A |
| **EP-2** 요청 검증 | request validation이 framework 기본 422이고 BC ErrorOut shape/code가 아님; body exact snapshot 금지 | 검증 가능한 필드가 없으면 다른 필수 필드 |
| **EP-3** 인프라·retryable 두 종단 | raw 인프라 실패→framework 기본 500; G1 승인 stable public retryable 실패→자기 BC 예외 정규화→controller 503/409 + 승인 code/header | 두 종단과 N/A 규칙은 §4.3.1 |
| **EP-4** 재고 부족 | 409 + 승인된 자기 BC code JSON | FC-1 골든과 교차확인 |

> **C 정책 무충돌**: EP-1~4에는 415/406 협상 항목이 없다. Q-1의 외부 공개 API
> 조건부 정책과 섞지 않는다. EP status·shape·N/A 정본은 `EVAL-METHOD.md §4.3.1`이다.
> **앵커 면제**: 라이브 probe라 §E 정적 앵커가 부적합 — 어댑터 예시는 `EVAL-METHOD.md §4.3.1 ⓑ`가 대신한다. **EP-1~4는 기본 4종**이며 변종(EP-1b·2b 등)은 §4.3.1 ⓑ 어댑터 재량(RUBRIC은 4기본만 고정). **v4 적용 경계·소급 금지**: EP는 사용자가 `2026-08-03-code-json` epoch를 명시적으로 freeze한 뒤 새로 생산하는 v4 라이브 결과에만 적용한다. working tree의 historical v3 결과 14개는 재작성·재채점하거나 EP 섹션을 추가하지 않는다.

---

## E. 앵커 (항목별 예시 — *임계값 아님*; 판정 바=표준 규칙)

> 앵커는 *규칙이 충족/위반된 구체 예시*일 뿐 PASS 임계값이 아니다(바=각 항목 §근거 표준 조항). 8벌서 뽑되 "플러그인이 낸 수준"을 기준으로 굳히지 않는다(순환 방지). 앵커가 예시일 뿐이므로 *홀드아웃 격리 불요* — 단 채점 *기준(criteria) 자체를 8벌 보고 조정*하지는 않는다(method §과적합).
> **출처·마스킹(v3)**: 아래 앵커는 *현존 fixture 직접경로*(`~/Desktop/dddjango-<run>/...`)로 좌표한다 — 삭제된 채점기록(`EVAL-*.md`)을 인용하지 않는다(2차 자료 의존·검증불가 차단). **grader 배포본에는 fixture명·줄번호를 제거한 익명 스니펫+표준 §근거만** 노출하고 출처 라벨은 조정자가 보유한다(`EVAL-METHOD.md §1.2` — 줄번호 노출과 blind 마스킹의 모순 해소).
> **v4 경계**: 아래에 남은 중앙 handler·catch-all·RFC 9457 예시는 v3 역사 기록일
> 뿐 v4 PASS 앵커가 아니다. 해당 기준은 **v3에서 폐기; v4 동일 ID 재정의**되었다.
> historical 결과를 고치거나 재채점하지 않고 locator commit으로만 재현한다.

| 항목 | FAIL 예시 | PASS 예시 |
|---|---|---|
| SD-3 빈혈 무복제 | Codex `catalog/published_service/stock.py:42` `stock__gte=quantity` | Claude `catalog/.../product.py:35-46` `Product.deduct_stock()` |
| SD-6 계층순수성/P1a | v4 FAIL: application이 status DTO/HTTP 의미를 소유하거나 controller가 mapping을 helper/handler에 위임 | **v3 역사 PASS(현재 폐기)**: 중앙 handler 발화. **v4 candidate PASS bar**: domain/application HTTP 무지 + 알려진 BC 예외를 해당 controller가 직접 catch/`Status` 반환 |
| SD-7 컨텍스트 통신 | Claude `p1a-v3 order_api_router.py:26`·`create_order_app.py:17`(ACL 밖 presentation·application이 catalog 도메인 **예외** 직접 import = 번역 ACL 미격리) | Codex `catalog_acl.py`(OHS만) · Claude `smoke4 product_stock_acl.py`(catalog 결합이 ACL에만 격리 — 미이주 직접통합은 표준 §2 허용) |
| SH-4 Django앱 위치 | Codex `catalog/models.py`·`catalog/migrations/` 루트(touched 데이터소스라 위반·개정 2026-06-08) / **cbvlive-codex 루트 `catalog/apps.py`·`views.py`·`tests.py` 잔재**(셰임 이주해도 앱 패키지 루트 존속→SH-1·4 FAIL) | Claude `application/catalog/infra_layer/django_catalog/models/` + **루트 catalog 완전 삭제**(cbvlive-claude); migrations-only 핀(apps.py 이주)은 SH-4 🟡·Q-5 |
| SH-7 협력포트 위치 | Codex `application_layer/create_order/port/` | Claude `domain_layer/order/port/` |
| SH-9 단일 레이아웃 | Codex `catalog/test/`+`catalog/tests/` 공존 | (단일 test 디렉터리) |
| SH-6 명명 | (8벌 위반 0) | 전 픽스처 `Interface`/`Impl`/`_repo.py` 0건 |
| Q-1 스코프 | Codex 멱등성 `Idempotency-Key` 필수(task 미요구) / **Codex 협상 레이어 발명**: **406** Accept 협상(`fklive-codex api_orders.py:43-86` `_parse_media_range` q파싱; §6.3:443-444 'single repr이면 406 불필요' escape-valve **직격**) + **415** Content-Type(발명 범위·본문검증이라 *literal 위반 아님*·§7.2 계약); 뿌리=`design-spec.md:123-126` architect 협상 레이어 전체 / Claude 합산 정규화 | 요청 범위 내 모델 / **Claude 406/415 의도적 공백**(`fklive-claude design-spec.md:81` 명시 배제) |
| Q-4 메커니즘 | final-claudeA `config/db_backends/sqlite3_immediate/base.py` | p1a-v3 양쪽 순수 version CAS |
| Q-5 마이그레이션 | Claude `django_catalog/migrations/0001_initial.py:14-25`(기존 0001 재작성) | 신규 앱 0001 + 별도 0002 expand |
| NJ-2 operation 얇음 | Codex `smoke2-codexB/.../create_order/api_orders.py:108-213`(operation이 `json.loads(request.body)` 수동파싱+수동검증+7 except status 분기) | Claude `p1a-v3-claude/.../api_order.py:61-63`(schema 바인딩→service→`Status(201,…)` 매핑만) |
| NJ-4 status 선언 | `poc-codex/.../api_orders.py:209,211`(`response={201}`만·오류 6종은 `openapi_extra`로 → 가시성O·`response=` 위반) | **v3 역사 예시(소급 불변)**: `201/400/404/406/409/415/422` 선언. **v4 candidate PASS bar**: 실제 직접 BC 반환 status만 동일 BC `<Bc>ErrorOut>`으로 선언하고 framework 기본 status는 ErrorOut으로 광고하지 않음 |
| NJ-5 문서화 | Codex `final-codexB/.../api_orders.py:31` 반환타입 `Union[...,HttpResponse]`(어댑터 누수) | p1a-v3 양쪽 `operation_id`+`summary`(+Claude `tags`) |
| FC-3 도메인 정합 | (반례) 차감 부호 역전·음수 재고 허용·인과 역전 | 8벌 모두 재고 차감 방향 정상 |
| Q-3 동시성 결정성 | Codex `test_..._api.py` `Barrier(2)`+ThreadPool 실스레드 레이스(스케줄러 의존=비결정·flaky) | 결정적 CAS-스파이(stale `version` 1회 주입→수렴) |

> NJ-1·3·6·FC-1은 8벌 known-bad 부재(전부 준수/미관측) — FAIL은 *표준 위반 정의*로 채점(앵커 없이도). 외부 baseline·합성 반례는 선택적 보강.
> **NJ-1/2/5 앵커 좌표 — 클래스 컨트롤러 병기(단서)**: 위 NJ 앵커는 함수형 operation 좌표(`def create_order(request, payload)` 형태의 `api_order(s).py:줄`)를 가리키나, ninja-extra 전환 후엔 **동일 위반이 컨트롤러 메서드 형태**로 나타난다 — `def create_order(self, request, payload)`(첫 인자 `self`). 즉 NJ-2의 `json.loads`/수동검증/ORM/비즈 분기는 *컨트롤러 메서드 본문*에서, NJ-5의 무정보 반환타입·summary 누락은 *`@route.*` 메서드*에서, NJ-1의 plain-view/`JsonResponse` 누수는 *컨트롤러 미등록(`register_controllers` 부재)*에서 동형으로 잡는다. 기존 함수형 좌표는 레거시/415 격리 예외 픽스처용으로 **유지**(삭제 아님)하고, 클래스 형태를 병기 단서로 더한 것이다.
> **Q-1 415/406 C 정책(위 Q-1 앵커 — 이전 'underdetermined' 단서를 결정화)**: 415/406은 **내부전용 API에선 기본 비적용이 정상**(과소 아님) — 스코프에 **'외부 공개 API'가 명시될 때만** 적용 대상. (a) 명시 *없이* 415/406 협상 레이어를 **발명**하면 **Q-1 과설계**(위 Q-1 Codex 좌표 = 이 케이스); (b) 명시 *있는데* 415/406을 **누락**하면 **Q-2 계약 흠**. Codex 415 구현이 §6.3 레시피 아닌 post-hoc이라 'underdetermined'였던 단서는 이 C 정책으로 **결정화**된다(내부전용 스코프라 발명=과설계). 앵커는 §5 freeze 밖이라 재서술 정당.

---

## v2 변경 요약 (적대 리뷰 반영)
- **북극성 정직화**: "DDD·houserules 실현" → "**규칙 준수 + 기능 정확성**"; baseline 차별가치·미시 유지보수성·보안(누출 제외)·명세 품질을 *명시적 비측정*으로 선언(과대주장 제거).
- **FC(기능 정확성) 신설**(치명) — 골든 오라클·mutation·도메인 정합. "재고 늘어나는 API 全PASS"(CF-1)·"틀린 도메인 모델"(CF-2) 차단.
- **PASS 바=표준 규칙, 앵커=예시**(임계값 아님) — 순환(C2)·홀드아웃 오염(C1) 해소.
- **SD-6 의미변종=치명 FAIL** — 스크립트 텍스트 게이밍(C3 Goodhart) 차단.
- **Q-3 Barrier 레이스=비결정 FAIL 앵커**(CF-7).

## v3 역사 — 당시 동결 전 결정 (2026-06-02)
> 아래는 locator commit에서 재현되는 v3 회고다. v4 상태를 동결하거나 활성화하지 않는다.
> 특히 중앙 handler/catch-all 기준은 **v3에서 폐기; v4 동일 ID 재정의**되었다.
> **v3 라이브 결과지 rollout 맥락(비규범)**: `maj1live(2026-06-07)`부터 v3 결과지에 EP 표 섹션을 사용했다. 이 날짜는 active v4 cutoff가 아니며 historical v3 결과 14개에 EP 섹션을 추가하거나 결과를 재작성·재채점하는 근거가 아니다.
1. **치명 게이트 목록** — SD 전부 + FC 전부 + SH-1·2·**3**·4·7 + (조건부)NJ-1·2 + **Q-4(치명 승격 확정)** + **SH-3(종류 폴더·골격 치명 격상 2026-06-08)**.
2. **마스크 C "판정 적재"** — `EVAL-METHOD §1.1.M` 이진 하위질문으로 조작화 + 경합 보수=*적재됨*.
3. **FC-1 골든 오라클** — **적대 grader가 프롬프트 직후·코드 열람 전** 작성, 작성자⊥채점자(§1.4).
4. **S-NINJA 배치** — NJ-1·2 조건부 치명, NJ-3·4=비치명 '강'(Q 카운트 정규 편입, 강-FAIL 시 상한 '중'), NJ-5·6 경미(§2.1·§2.4).
5. **빠지거나 과한 항목(v3 역사)** — v3 당시 차원 집합에
   **NJ-7(오류 변환 완전성·catch-all)**을 1회 추가했다. 규칙 내용은 당시 §6.2에
   선재했으나 측정 차원이 없던 빈틈을 메운 것이며, 신설 동기는 aclex2live fixture 관찰이었다.
   이 catch-all 의미는 **v3에서 폐기; v4에서 동일 NJ-7 ID를 `BC 오류 직접 계약`으로 재정의**한다.
   - **동결 해제 2건째(2026-06-08): NJ-1 판정기준을 클래스 컨트롤러(`NinjaExtraAPI`/`@api_controller`) 허용으로 개정** — *차원 수 불변*(NJ-1 신설 아님)·*판정기준* 변경만(함수형 `NinjaAPI`+`Router`만 합격이던 결정 레인을 `NinjaExtraAPI`+`@api_controller`/`register_controllers`도 PASS로 확장). 판정기준은 §5 사전등록 동결 대상이므로 명시 해제로 기록한다. 근거: ninja-extra 클래스 컨트롤러 도입(2026-06-08). 신규 표준=클래스 컨트롤러, 함수형 Router=레거시/415 격리 예외(둘 다 ninja 스택 PASS).
   - **동결 해제 3건째(2026-06-08): SH-3 치명 격상 + §632-(2) 면제 폐지 반영** — *차원 수 불변*(SH-3 신설 아님)·**치명 배정 변경**(비치명 `—`→치명) + **판정기준 변경**(데이터소스 골격을 빈 패키지로 무조건 실현·종류 폴더 부재 시 FAIL). 치명 배정·판정기준은 §5 사전등록 동결 대상이라 명시 해제로 기록. **근거 = 표준 동기**(fixture 동기 아님): `architecture-ddd/references/final.md:632` §632-(2) 개정(데이터소스 깊이 면제 폐지) + `discipline-houserules` §0-1 — 평가지가 *개정된 표준*을 따라가는 것(§5.2 "criteria는 표준 §근거에 선재"와 정합·NJ-7과 달리 fixture 관찰 산물 아님). **발견1(SH-1/4 마스크 C 정정)은 별개 성격** — 차원·치명·판정기준 변경이 아니라 *기존 SH-1/4 규칙의 올바른 적용*(루트 `apps.py` 잔재=위반)을 마스크 C 산문이 잘못 PASS로 뒤집던 것을 바로잡음 → **freeze 해제 불요**(기준 불변·적용만 교정).

## v4 candidate 사전등록 요약 — NOT ACTIVE / NOT FROZEN

- 채점 차원은 정확히 34개다: `SD-1..7 + SH-1..10 + NJ-1..7 + FC-1..3 + Q-1..7`.
- NJ-7 ID와 비치명 강도는 유지하되 의미를 `BC 오류 직접 계약`으로 바꾼다.
- 이 후보는 적대 리뷰·34-ID 기계 대조와 사용자 명시 freeze 전까지 scoring prohibited다.

(채점 절차·집계·bisect·결승선·과적합 방지·**산출 형식(§6)** = `EVAL-METHOD.md`)
