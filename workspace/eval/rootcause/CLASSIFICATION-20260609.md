# dddjango 근본원인 분류 — 2026-06-09 (ultracode 전수 스윕)

> **박제 정본.** ultracode Workflow가 전 reference·skill·관측 문제를 사용자 3분류(① LLM 비결정 / ② reference 부족 / ③ reference 미반영 skill 드리프트) 결정트리로 분류한 결과의 **영구 사본**. 휘발성 /tmp 원본(`wv5num2m0.output`, 192KB) + 조정자 수동 ninja 보강을 병합. 발단(사용자): "개선이 결정적이지 않고 비결정이 남아 품질이 시도마다 다르다 — 비결정인가, reference 부족인가, reference 미반영 skill 문제인가?"

## ⚠️ 사후 정정 (2026-06-10) — FC-1 재분류 + 정정 구현
아래 분류는 *분류 시점* 기준이다. 직후 2b 구현 단계의 실측이 **FC-1을 뒤집었다**:
- **FC-1: 2b → 1 (간헐 비결정).** 구현 전 검증에서 초반 A/B는 `Status(201,…)`→500 / 튜플→통과로 발화했으나, **이후 어떤 통제 구성에서도 재현 불가**(fresh venv · PYTHONHASHSEED 0~7 · pydantic 2.11~2.13 · pristine fixture). "첫 몇 런만 실패" 패턴 = 결정적 표준결함이 아니라 **ninja-extra의 간헐 미스바인딩**. 표준 `Status(201,…)`는 django-ninja **공식 권장형**이고 대부분 작동한다.
- **③ 튜플 폐기**: deprecated 형을 표준에 박는 손해라 사용자 결정으로 기각. 적용된 건 **매직넘버 `201` → `status.HTTP_201_CREATED`(ninja_extra plain int) 상수화**뿐(클린코드·동작 동일·`HTTPStatus.CREATED`는 IntEnum이라 역으로 500 유발 확인→회피). FC-1의 500 비결정은 **후속 동시성 검증서 비결함 확정**(아래).
- **✅ 후속 동시성 검증 (2026-06-10) — FC-1 비결함 확정**: 사용자 "간헐도 용납 불가"로 봉인 착수 → 봉인 전 재현 사냥. 순차 240+(해시시드 0~19 · `.pyc` 정리 · fixture 통합 12 · Literal `status` 충돌 MRE 75) + **동시 1200+**(진짜 멀티스레드 WSGI[`wsgiref`+`ThreadingMixIn`] · 워밍업 없는 첫요청 다발 · **`Status` vs 튜플 대조 무차별**=둘 다 100% 201) **전부 음성 · 500 = 0회**. 동시성은 "첫 몇 런만 실패"의 가장 그럴듯한 메커니즘 후보였으나 그것도 닫힘. → FC-1 **1(간헐 비결정) → 사실상 비결함(유령)**; 초반 A/B는 stale `.pyc` 환경 아티팩트로 판단. **`Status` 표준 무변경 확정** — 봉인 강행 시 공식 비-deprecated형을 추측 교체(회귀 위험)·대안 전무(튜플=deprecated · 단일 schema=200+NJ-4 파괴). 415 carve-out(C 정책·DR-48)도 사용자 재확인=무변경.
- 따라서 **관측 2b: 1 → 0**, **reference 결함: 8 → 7**(2a 2 + 2b 5 = ddd-factory·check_password·safe_sql·test-router·ninja-api). "관측 문제 대부분 비결정"이 *FC-1 자신으로* 재확증됨.

**적용된 정정 (2026-06-10·배포→정본→codex 3미러 전파·`corpus_mirror_sync` 11/11 in-sync)**: ddd-factory·check_password·safe_sql·ninja-api(`§6.2 NinjaAPI()`→`NinjaExtraAPI()`) + FC-1 상수. **test-router 보류**(DR-48 §20 얽힘). **🔴 미커밋.**

## 메타
- **방법**: ultracode Workflow — Inventory → Classify(결정트리) → Latent sweep(미발화 코퍼스) → Synthesize, 각 분류에 **적대검증(adversarial verify)** stage. 관측 문제는 라이브 채점지에서, 잠재 결함은 코드 미발화 영역 스윕에서 수집.
- **규모**: 분류 항목 **37** · 대상 스킬 **11** · 에이전트 **99**
- **코드 기준**: HEAD `a4c7434`
- **원본**: `/private/tmp/claude-501/-Users-hyun-Desktop-dddjango/00909d0e-.../tasks/wv5num2m0.output` (192KB JSON, **휘발성** — 본 문서가 영구 사본)
- ⚠️ **워크플로 latent 스윕 불완전**: 5스킬만 완료 — `ninja` 잠재 에이전트가 **API 500으로 크래시**(사용자가 실시간 포착). 조정자가 사후 수동 보강(아래 §조정자 수동 ninja 보강) → **본 문서 집계는 보정 후 값**.

## 결정트리 (사용자 3분류 + 세분)
| 코드 | 의미 | 처방 |
|---|---|---|
| **0** | by-design (설계상 허용·결함 아님) | 드롭, 정본 무수정 |
| **1** | LLM 비결정 (표준 올바른데 런간 흔들림) | backstopable=yes → 백스톱 / no → 수용+EVAL 계측 |
| **2a** | reference 부족 (침묵) | 신규 저술 |
| **2b** | reference 틀림 (버그를 가르침) | 정본 정정 → `corpus_mirror_sync` 전파 |
| **3** | skill 드리프트 (정본 옳은데 미러 유실) | 재동기 |

## 최종 집계 (보정 후)
| 분류 | 관측 | 잠재 | 합 |
|---|---|---|---|
| 0 by-design | 2 | — | 2 |
| 1 비결정 | 20 | 0 | 20 |
| 2a 부족 | 0 | 2 | 2 |
| 2b 틀림 | 1 (FC-1) | 5 | 6 |
| 3 드리프트 | 0 | 0 | 0 |
| **합** | **23** | **7** | **30** |

- **스킬측 결함(2a+2b+3) = 8**: 관측 1(FC-1) + 잠재 7.
- **reference 결함 = 8** (2a 2 + 2b 6).
- ⚠️ /tmp 원본은 **reference 7 / 총 29**(ninja-api 누락). 보정 후 **8 / 30**. 차이 = §조정자 수동 ninja 보강의 `ninja-api` 1건.
- **핵심 결론**: *관측* 한정 **87%(20/23)가 비결정** — 표준·미러 byte-identical로 올바른데 LLM(특히 Codex coder/architect)이 런간 흔들림. *잠재* 스윕은 **정반대**(7건 전부 스킬측). 즉 "비결정 우세"는 이미 하드닝된 관측 모집단의 **선택편향**이고, 미발화 코퍼스 결함은 별개로 존재.

## ② reference 결함 8건 (정정 대상 — 스캔용 인덱스)
| # | 코드 | 위치(정본) | 분류 | 결함 | 정정 방향 |
|---|---|---|---|---|---|
| 1 | **FC-1** | django-ninja §2.2:160-171·§2.3:194-200 | 2b·**치명·관측** | `Status(201,Out)` × ninja-extra 다중응답 → 201→OrderOut 바인딩 실패 → **happy path 500** | 검증통과형 — ①성공 단일 schema / ③튜플 `return 201,X`+:625 노트 정정 (설계선택·② status키 비충돌은 기각) |
| 2 | ddd-factory | architecture-ddd:847 | 2b·잠재·**실행증명** | factory가 Product(@dataclass)에 없는 `store_id` 전달+`description` 누락 → `TypeError` | 문서 내 단일 Product 정의와 정합 |
| 3 | check_password | discipline-cleancode:458-460 | 2b·잠재·**실행증명** | "좋은 예"가 `-> bool`인데 no-user서 `None` 누수(나쁜 예보다 퇴행) | `bool(user and verify(...))` 또는 분기 |
| 4 | safe_sql | implementation-python:2559 | 2b·잠재·**실행증명** | `-> str`인데 스킬 자기-강제(§23.1 mypy strict)서 깨짐 | `-> tuple[str, list]` |
| 5 | test-router | implementation-test:2507 §20.1 | 2b·잠재·경미 | router import가 flat `orders.api` → verbatim 복사 시 import 불가 | 4-layer `presentation_layer.api…` 경로 |
| 6 | ninja-api | django-ninja:500 | 2b·잠재·경미·**조정자 보강** | `api = NinjaAPI()` ↔ 표준 강제 `NinjaExtraAPI()`(DR-48) 모순 | `NinjaExtraAPI()`로 정정 |
| 7 | django-web 에러페이지 | implementation-django-web (신규) | 2a·잠재·**진짜 고아** | 서버렌더 service→예외→500.html/handler500/재렌더 침묵(ninja JSON-only라 위임 불가) | 신규 저술 |
| 8 | test-error-contract | implementation-test (신규) | 2a·잠재 | 에러변환 *계약테스트 기법* 침묵(값은 houserules §2:144가 정의·기법 오너 부재) | 신규 저술 |

## 조정자 수동 ninja 보강 (워크플로 latent 누락분)
워크플로 `ninja` 잠재 에이전트가 API 500으로 죽어 latent 스윕에서 ninja가 비었다(5스킬만 완료). 조정자가 `implementation-django-ninja` 정본을 직접 재스윕:
- **추가** — `ninja-api` (2b 경미): `implementation-django-ninja/reference/final.md:500` `api = NinjaAPI()` ↔ 표준이 강제하는 `NinjaExtraAPI()`(DR-48 클래스 컨트롤러) 모순. §6.2 예시가 잘못된 진입점을 보임. (정본 :222는 `NinjaExtraAPI()`로 올바름 — :500만 어긋남.)
- **기각(오탐)** — `problem(404, ...)`·`problem(415, ...)`의 `...`는 **문서 ellipsis**(주석이 §6.2 중앙 헬퍼를 가리킴)이지 미완성 코드/TypeError 랜드마인이 **아님**. 워크플로 재스윕 에이전트의 과잉표기를 조정자가 실코드 확인 후 기각.

## synthesis (워크플로 출력 — verbatim)

### summary
관측 23문제 전부 적대검증 upheld=true. 최종 분포: 0-by-design 2 · 2a 0 · 2b 1 · 3 0 · 1-nondeterminism 20. 잠재결함 6건(5스킬): 2b 4 · 2a 2. 핵심 결론: 관측 문제 한정으로는 스킬측 결함(2a+2b+3)이 1건(FC-1 단독)뿐이고 87%(20/23)가 1-비결정 — 표준·미러가 올바르고 충실한데도 LLM(특히 Codex coder/architect)이 런간 흔들림. 단 잠재결함 스윕은 정반대(6건 전부 스킬측 2a/2b)라, '비결정 우세'는 이미 디버깅·반복검증된 관측 항목에 국한된 선택편향이며 미발화 코퍼스 결함은 별개로 존재. 보정 앵커 'ACL-EX2=2a'는 STALE(DR-44 이후 houserules:144·ninja §6.2가 침묵을 byte-id로 메움)→현재 1로 정정 확인. HEAD=a4c7434.

### categoryCounts
관측문제(23건): 0-by-design=2 (BC-decomposition, 415-406-overengineering) · 2a-reference-insufficient=0 · 2b-reference-wrong=1 (FC-1) · 3-skill-drift=0 · 1-nondeterminism=20. ─── 잠재결함(6건, 5스킬): 2b=4 (architecture-ddd factory store_id, discipline-cleancode check_password→bool, implementation-python safe_sql→str, implementation-test §20.1 router import) · 2a=2 (implementation-django-web 서버렌더 에러페이지 침묵, implementation-test 에러변환 계약테스트 레시피 침묵) · 0/1/3=0. ─── 합계(관측+잠재 29건): 0=2 · 1=20 · 2a=2 · 2b=5 · 3=0. ─── 스킬측(2a+2b+3): 관측 1 / 잠재 6 / 합 7. 비결정(1): 관측 20 / 잠재 0. 비결함(0): 2.

### remedyRouting
【2b → 정본 정정 (corpus_mirror_sync 후 미러 전파); 결정적·우선】 (1) FC-1: ninja §2.2:160-171 / §2.3:194-200 create 예시를 검증통과형으로 — 성공 단일 schema(response={201:OrderOut}+return order) 또는 OrderOut/ProblemOut status 키 비충돌(disjoint discriminator), 그리고 :625-626 '튜플 deprecated' 노트가 작동 경로를 막지 않게 수정. 수용기준=골든 happy path(stock>=qty→201) 실측 통과·§2.3=§2.2 동일 동기화. (2)[잠재] architecture-ddd:847 factory를 문서 정의 Product(@dataclass id;name;description;price)와 정합(store_id 추가 또는 호출 정정+description 제공). (3)[잠재] discipline-cleancode:458-460 check_password를 bool(user and verify(...)) 또는 if 분기로(-> bool 약속 준수·no-user None 누수 제거). (4)[잠재] implementation-python:2559 safe_sql 시그니처를 -> tuple[str,list]로(자기-강제 mypy --strict 통과). (5)[잠재] implementation-test:2507 §20.1 router import를 4-layer 경로(presentation_layer.api...router)로 통일. 【2a → 신규 저술】 (6)[잠재] implementation-django-web: 서버렌더 어댑터 service→domain/conflict/transient 예외 → 500.html/error.html/handler500/재렌더 경로 지침 신설(§6 POST flow·§7 HTMX·§10 매트릭스에 '서비스 충돌→에러 렌더' 행). ninja(JSON-only) 위임 불가=진짜 고아. (7)[잠재] implementation-test: 에러변환 계약테스트 *기법* 레시피 신설(도메인예외→비2xx, catch-all→problem+json[NJ-7], operation-level OperationalError 'database is locked'→raw 500 누수 금지[ACL-EX2]). houserules §2:144가 계약 *값*은 정의하나 테스트 *기법* 오너(implementation-test) 부재. 【3 → 재동기】 해당 없음(관측·잠재 모두 미러 byte-identical 확인). 【1 → 수용 또는 백스톱】 ▸이미 배선된 결정적 백스톱(추가 작업 불요·계측만): catch-all-missing(⑯), NJ-4-openapi-extra(⑤), anemic-sql-duplication(⑪ C형), idempotency-scope-creep(⑩). ▸backstopable=yes·미배선→신규 결정적 백스톱 후보(라이브 N≥2 재현 후): httperror-malformed-body(⑯에 HttpError-handler 부재 확장), migration-0001-rewrite(touched 0001 재작성/state-only 0002 부재 AST), catalog-husk(check-app-container counterpart 면제 사각=DR-51 ⑰ 재도입, 롤백 이력·라이브 효과 선검증). ▸backstopable=no→수용+계측(EVAL 라이브 매트릭스·reviewer salience·정본 무변경): ACL-EX2(EP-3 transient→{503,409}), FC-2-boundary(FC-2 mutation 동적), NJ-2-raw-parsing, logger-exception-missing, mechanism-ownership, anemic-dead-domain, cross-bc-orm-fk, vacuous-concurrency-test, misattributed-constraint-test, 415-bypass-functional-router. ▸nit·비례성 미달→RUBRIC 경미 유지(백스톱 보류): NJ-1-jsonresponse(🟡), NJ-5-bare-status(경미), controllerbase-inheritance(nit). 【0 → 드롭(결함 아님)】 BC-decomposition, 415-406-overengineering — 정본 무수정. 재현성 강제는 정본 아닌 eval 하니스(G0 경계 고정 프롬프트).

### topPriorities
1. [2b·결정적] FC-1 ninja create 예시 정정 — §2.2:160-171/§2.3:194-200를 검증통과형(성공 단일 schema 또는 status 키 비충돌)으로, :625-626 deprecated 노트 수정. happy path 500을 가르치는 유일한 관측 2b·치명. 골든 201 실측 통과로 수용
2. [2b·잠재·실행증명] implementation-python:2559 safe_sql -> str→-> tuple[str,list] — 스킬이 자기-강제(§23.1 mypy strict=true)하는 바로 그 체커에서 깨짐. 결정적·일망타진
3. [2b·잠재·실행증명] discipline-cleancode:458-460 check_password — '좋은 예'가 -> bool인데 no-user서 None 반환(나쁜 예보다 퇴행). bool(...) 또는 분기로 정정
4. [2b·잠재·실행증명] architecture-ddd:847 factory가 Product(@dataclass)에 없는 store_id 전달+description 누락 → TypeError. 문서 내 단일 Product와 정합화
5. [2b·잠재] implementation-test:2507 §20.1 router import를 flat orders.api→4-layer presentation_layer 경로로 통일(코더 verbatim 복사 시 import 불가)
6. [2a·잠재·반복실패군] implementation-test 에러변환 계약테스트 *기법* 레시피 신설(도메인예외→비2xx·catch-all→problem+json·OperationalError raw 500 누수 금지). 표준이 값은 정의하나 테스트 기법 부재
7. [2a·잠재] implementation-django-web 서버렌더 service→예외→에러페이지(500.html/handler500/재렌더) 지침 신설 — ninja(JSON-only) 위임 불가한 진짜 고아
8. [1·backstopable=yes] catalog-husk(완전 이주 누락) — check-app-container counterpart 면제 사각 재현. DR-51 ⑰ 재도입 후보이나 롤백 이력·라이브 효과 선검증 필수
9. [1·backstopable=yes] httperror-malformed-body·migration-0001-rewrite — 깨끗한 AST 신호 존재(⑯ HttpError 부재 확장 / touched 0001 재작성 게이트). 라이브 N≥2 재현 후 결정적 백스톱
10. [1·수용+계측] ACL-EX2 인프라예외 누수·FC-2 경계테스트 — 의미층이라 backstopable=no. EVAL-METHOD 라이브 매트릭스(EP-3 503 화이트리스트·FC-2 mutation)로 계측, 정본 무변경

### answerToUser
전체적으로는 '비결정 vs 스킬부족' 둘 다 실재하나, **관측된 문제에 한정하면 압도적으로 LLM 비결정(1) 문제**입니다 — 단 중요한 단서가 붙습니다.

■ 정량 답 (관측 23문제, 전부 적대검증 통과)
- 1-비결정: 20건 (87%)
- 0-설계상 허용(결함 아님): 2건 (BC 분해, 415/406 협상 — designer-decides)
- 2b-정본 오류: 1건 (FC-1 단독 — ninja create 예시가 happy path 500을 가르침)
- 2a-정본 부족: 0건
- 3-드리프트: 0건
→ 스킬측 결함(2a+2b+3) 합계 = 1건뿐. 표준 본문도 Claude/Codex 미러도 byte-identical로 올바른데 LLM(특히 Codex coder/architect)이 같은 프롬프트에서 런마다 흔들립니다(catalog 이주 누락, raw JsonResponse, openapi_extra-only, 빈혈 SQL, 멱등성 스코프크립 등). 보정 앵커 4개와 정합하며, 'ACL-EX2=2a' 앵커는 이미 STALE(DR-44 이후 houserules:144·ninja §6.2가 그 침묵을 메움)이라 현재는 1로 정정됨을 확인했습니다.

■ 그러나 — '비결정 우세'는 선택편향입니다 (정직한 한계)
1) **N=관측 한정**: 이 23건은 이미 라이브 평가에서 발화·디버깅·여러 차례 정정된 항목입니다. 표준이 이미 보강을 거친 모집단이라 잔여가 비결정으로 수렴하는 게 자연스럽습니다. 런타임 우열 결론은 금지(N=1·태스크 heaviness 교락).
2) **잠재결함 스윕은 정반대**: 코드 미발화 영역을 훑으니 6건 전부 스킬측이었습니다(2b 4 + 2a 2). 셋은 *실행으로 증명된* 랜드마인 — architecture-ddd factory의 store_id 미존재 TypeError, discipline-cleancode check_password가 `-> bool`인데 None 누수, implementation-python safe_sql가 `-> str`인데 자기-강제 mypy --strict에서 깨짐(셋 다 제가 재현 실행으로 확인). 둘은 진짜 침묵(서버렌더 에러페이지·에러변환 계약테스트 기법), 하나는 같은 문서 내 router import 모순입니다. 즉 **미발화 코퍼스에는 스킬 결함이 여전히 누적**되어 있고 관측 표본에 안 잡혔을 뿐입니다.

■ 처방 우선순위 (결정적 수정 먼저)
- 즉시 결정적 고침(영향×확실성 최상): FC-1 정정 + 잠재 2b 4건(전부 실행으로 깨짐 확인). 이건 비결정이 아니라 '표준이 버그를 가르침'이라 고치면 끝납니다.
- 신규 저술 2a 2건(서버렌더 에러페이지·에러변환 테스트 기법).
- 비결정 20건: 절반은 이미 결정적 백스톱이 배선됨(⑤⑩⑪⑯, 계측만), 나머지는 backstopable=yes면 라이브 N≥2 후 백스톱(catalog-husk·httperror·migration-0001), no면 수용+EVAL 매트릭스 계측. nit급(NJ-1/5, ControllerBase 상속)은 RUBRIC 경미 유지.
- 0번 2건은 드롭(정본 무수정). 재현성은 정본이 아니라 eval 하니스(G0 경계 고정)로 처리.

요약: "관측된 회귀는 대부분 비결정이라 표준 추가 저술보다 백스톱·계측이 본질이다. 단 코퍼스 자체에는 아직 발화 안 된 스킬측 랜드마인(특히 시그니처↔본문 불일치 2b)이 6건 더 있으니, 비결정 계측과 별개로 그 결정적 결함부터 닫아야 한다."

## 관측 분류 항목 전체 (37건 · id · 최종분류 · upheld · 논거)

#### FC-1 — `2b-reference-wrong`  (upheld: True)

UPHELD: 2b-reference-wrong (high confidence). Adversarially re-verified every competing category against reference+mirror file:line; all falsified except 2b.

REFERENCE TEACHES THE BREAKING RECIPE (not silent, not correct): /Users/hyun/Desktop/dddjango/workspace/reference/implementation-django-ninja/reference/final.md prescribes — in BOTH worked create examples — the exact failing combination: (a) function-form §2.2 :160-171 = `@router.post(..., response={201: OrderOut, 404: ProblemOut, 409: ProblemOut})` (:162, multi-response union) + `return Status(201, OrderOut(id=order.id, status=order.status))` (:171, runtime constructor); (b) class-controller §2.3 :194-200 = `@route.post("", response={201: OrderOut, 409: ErrorOut})` (:194) + `return Status(201, OrderOut(...))` (:200). Field conflict reinforces: OrderOut.status:str (:148) ↔ ProblemOut.status:int (:154), shared key "status". I grep-confirmed there is NO worked example anywhere in the reference returning a bare schema (`return order`/`return OrderOut(...)`) for the create happy path — `Status(201,...)` is the ONLY prescribed create return. Decisively, :625-626 actively deprecates the one form that WORKS: "`(status, schema)` 튜플 반환은 1.6.x에서 deprecated다" — steering authors off the working path onto the broken one. Central catch-all §6.2 :575-577 `@api.exception_handler(Exception)` → :537-541 `_server_error` returns 500 problem+json, which swallows the ProblemOut.model_validate ValidationError raised internally when Status(201,OrderOut) binds against the multi-ProblemOut union → happy-path 500.

MIRROR FAITHFUL (rules out 3-drift): /Users/hyun/Desktop/dddjango/dddjango/skills/implementation-django-ninja/references/final.md is byte-identical in the FC-1 region — :138 status:str, :144 status:int, :152 response={201:OrderOut,404:ProblemOut,409:ProblemOut}, :157 `-> Status[OrderOut]`, :161 `return Status(201, OrderOut(...))`, :184-190 class controller identical; offset -10 is only the §3 P1 Source-Sufficiency header block (832 vs 822 lines). Recipe lives ONLY in references/final.md — grep of SKILL.md/coder.md/codex SKILL.md for ProblemOut|Status(201|response={201 = empty. Both copies equally wrong = mirror faithful, not drift.

RULES OUT 1-nondeterminism (the most dangerous misclassification): The standard hard-prescribes the breaking form in both examples with no working alternative for create, so the LLM did not wobble — it faithfully executed a defective prescription. Contrapositive proven by the dual eval: nj7live-CODEX (results/20260609-2010-nj7live-codex.md :70,:78) used the DEPRECATED tuple `return 201, OrderCreatedOut(...)` → FC-1 PASS (happy path 201); nj7live-CLAUDE (results/20260609-2245-nj7live-claude.md :28) used the PRESCRIBED `return Status(201, OrderOut(...))` → 3 success tests failed/500, A/B-confirmed, clean-build (`python -B`, 0 pyc) deterministic ×7; stale .pyc masked it live. Standard's prescribed path breaks, deprecated path works = wrong reference, not LLM variance.

RULES OUT 2a (silence): §2.2/§2.3 are explicit with full worked code — not silent. RULES OUT 0 (by-design): happy-path 500 is a functional failure; symptom's "form≠function" caveat does NOT license broken output (designer-decides covers BC decomposition, not working-vs-500). Exactly matches calibration anchor FC-1=2b.

REFINEMENT (does not change category): the `-> Status[OrderOut]` ANNOTATION (:132,:167,:195 — type subscription) is correct/harmless; the defect is solely the runtime VALUE `return Status(201, OrderOut(...))` under a multi-`response` union. context7 ninja-extra docs show route returns via `status_code=` route config or plain schema, not a `Status(code,schema)` runtime wrapper under unions — consistent with the wrapper being a poor fit. REMEDY: correct the reference (then corpus_mirror_sync.py): make the §2.2 :160-171 / §2.3 :194-200 create examples a verified-passing form — either success single-schema (`response={201: OrderOut}` + `return order`/`return OrderOut(...)` so the union never validates the 201 payload as ProblemOut), or make OrderOut/ProblemOut non-conflicting (disjoint discriminator / matching "status" type), or fix the :625-626 note to stop deprecating the working tuple (or replace with an actually-verified Status usage). Acceptance = golden-oracle happy path (stock>=quantity → 201) passes empirically; §2.3 must be synced identically to §2.2.

#### FC-2-boundary — `None`  (upheld: True)

UPHELD as 1-nondeterminism (high confidence). I attempted to overturn each alternative and all failed.

(2b ruled out — reference NOT wrong) discipline-tdd reference final.md:367 commands recording "경계 자체와 결과가 달라지는 가장 가까운 바깥쪽 값" and :372-379 gives the worked ==boundary / boundary+1 coupon example. implementation-test reference final.md:2267 explicitly states `> 10`만 테스트하면 `>`→`>=` mutant 미감지, and :2275-2276 shows the strong test adding `==10`(exact boundary)·`==11`. The doctrine is correct and executable, not a buggy prescription. So this is NOT the LLM correctly following a broken reference.

(2a ruled out — NOT silence) Same lines prove the doctrine is present, not absent. I checked it is not hiding in another section by confirming it IS the section that teaches it.

(3 ruled out — NO drift) `diff` shows mirror is NOT pure byte-identical (reference has a P1 Source Sufficiency governance header at lines 1-14 the mirror lacks) — so the original "byte-identical" wording is imprecise. BUT that header is corpus-sufficiency metadata, unrelated to FC-2. The substantive boundary doctrine is fully mirrored: tdd mirror final.md:355 carries the identical sentence; test mirror final.md:2258 carries the identical "quantity=10 케이스가 없어서 감지 못함" comment; after stripping the P1 header the TDD body is byte-identical. No relevant content lost.

(1 NOT masking a fixable gap — the most dangerous misclassification) The reference+mirror genuinely teach the exact lost-boundary scenario with a worked example; nothing is ambiguous or missing for the LLM to follow. The decisive proof is the run-to-run flip on IDENTICAL corpus + IDENTICAL mutation protocol: ptcat-codex.md:67 (경계 `<`→`<=` = 24 passed green → FC-2 치명 FAIL, test_product.py has stock>qty and stock<qty but no exact boundary), nj7live-codex.md:13 (경계 vacuous, red율 2/3 → FAIL), versus ptbootlive-codex.md:80 (경계 `<`→`<=` = 1 failed → PASS solely because test_concurrent happened to use stock=1·q=1, explicitly "단위는 경계 미커버이나 통합이 잡음"). Same prompt, same Codex runtime, opposite verdict driven by an incidental fixture choice = the definition of nondeterminism, not a doctrine gap.

(backstopable=no, confirmed) 16 check-*.py scripts; grep for mutation/boundary/경계 returns 6 matches, all false positives — 경계 means architectural boundary (check-ninja-boundary-middleware presentation boundary, check-synthetic-infra-exc infra boundary, check-error-centralization presentation boundary) and mutmut appears only in error-handler guard prose. Zero backstops count boundary-value test cases or enforce mutant survival. The symptom is a MISSING test case whose semantic necessity an AST gate cannot prove (false positives on normal-looking tests), and whether a candidate assertion actually kills the boundary mutant is a runtime judgment. The reference itself delegates this dynamically: discipline-reviewer.md confines the reviewer to static signals ("산출물 제거 시 red 여부의 정밀(near-mutation) 판정은 그레이더 FC-2 몫이고, 너는 정적 신호…만 본다"), RUBRIC.md:74 puts FC-2 in the 결정(주입 실행) lane, and EVAL-METHOD.md:114 runs the mutation via `.venv/bin/pytest` (dynamic). This matches calibration anchor FC-2 exactly (category 1, backstopable=partial/no). Remedy = accept + instrument via the existing dynamic FC-2 mutation gate; a coder-time AST backstop is unfit and any further determinism would require a post-coder dynamic (non-AST) CI gate decided only after live N>=2 frequency measurement.

References re-confirmed by direct read: discipline-tdd reference final.md:367,372-379; implementation-test reference final.md:2267,2275-2276; mirrors tdd final.md:355 / test final.md:2258 (doctrine retained); discipline-reviewer.md static-signal delegation bullet; RUBRIC.md:74; EVAL-METHOD.md:113-114; result files ptcat-codex:67, nj7live-codex:13, ptbootlive-codex:80 (run-to-run flip).

#### ACL-EX2 — `None`  (upheld: True)

분류 유지: 1-nondeterminism (confidence medium→high). 적대적 재검증 결과 모든 load-bearing 주장과 모든 대안 카테고리를 source file:line으로 확인했고, 분류가 옳다.

[핵심 발견: 2a 앵커는 STALE — 분류가 정확히 지적] 보정 앵커 'ACL-EX2=2a'는 DR-44 코퍼스 시점엔 옳았으나 이후 표준 저술(aclex R2/ACLEX-B, DR-44~50)이 그 침묵을 *byte-for-byte* 메웠다. 직접 확인:
- discipline-houserules 정본 final.md:144 = "transient 인프라 예외(`OperationalError` 중 DB 락·deadlock·serialization failure)는 협력 포트가 선언하는 우리 쪽 *도메인* 예외 집합이 아니다 — ACL은 이를 도메인 예외로 위장 번역하지 않고(포트에 인프라 누수 금지), **presentation 경계의 단일 변환점이 retryable(503/409) problem으로 매핑한다**". 2a 앵커가 '침묵'이라던 바로 그 지점이 명시 채워짐.
- implementation-django-ninja 정본 final.md:458-488 = transient(락/deadlock/serialization)→503/409 매핑 + `@api.exception_handler(OperationalError)`:557-565 시그니처 분기(`_is_retryable_db_error`→503 / 영구장애 500) + IntegrityError:568-572 형식 500 + Exception catch-all:575-577 + "⚠️ 필수 불변식" 분기강제 박스:480-488.

[2b 기각 — 표준이 버그를 가르치지 않음] FC-1(정본 ninja:146-171 status 충돌이 happy path를 500화=실행시 깨지는 처방)과 달리, ACL-EX2 잔여(non-transient DatabaseError→500)는 표준이 *명시적으로 옳다고 처방한 동작*이다 — final.md:460-461·482-483 "disk I/O·`no such table`·`database is malformed`→500"; :538·:560 영구장애 500 분기. 실행시 깨지는 예시 없음.

[2a 기각 — 침묵 아님] 2a 앵커가 인용한 §2:144 침묵은 위처럼 채워짐. 추가로 잔여 누수 경로(OHS `published_service` raw re-raise)도 미커버 침묵 아니다: 중앙 핸들러는 단일 NinjaExtraAPI 인스턴스의 presentation 경계에 등록(final.md:435-440)되어 OHS·ACL·직접 어느 경로든 무관하게 경계 도달 infra 예외를 잡는다(path-agnostic catch-all). non-transient는 그 경계에서 정확히 500화.

[3-skill-drift 기각 — 미러 충실] 바이트 diff로 houserules §2:144 = HOUSERULES_L144_BYTE_IDENTICAL 확인. Claude 미러 ninja references/final.md:557-577 세 핸들러+MRO 주석 보유. discipline-reviewer.md가 4개 배타 렌즈 전부 인코딩: line41(중앙화 완전성/under-mapping transient 미매핑→500 important), line43(over-mapping 영구장애 retryable 오분류 important·check-transient-overmapping), line44(NJ-7 catch-all·check-catch-all-handler), line46(ACL 전수성 carve-out (d) transient 제외·위장번역 금지·check-synthetic-infra-exc). 백스톱 3종 + 16종 전부 존재. Codex 미러 codex-dddjango/.../implementation-django-ninja/SKILL.md 존재.

[0-by-design 기각] designer-decides 명시 없음.

[1-nondeterminism 확정 — 라이브 증거가 직접 뒷받침] 증상 헤드라인(transient `OperationalError("database is locked")`→500)은 *재현 안 됨*: ptbootlive-codex results/20260609-1523-...:114 EP-3="503 관측 — **500 아님**(ACL-EX2/maj1 회귀 없음·transient 경로 정상)"; ptbootlive-claude ...:113 동일 503. 잔여는 codex `published_service.py` raw re-raise하는 **non-transient** DatabaseError→500뿐(:104·:116, grader "status 정당·형식 problem+json 안전 → **비치명 잔여흠**"). claude는 :115 "ACL-EX2 깨끗(전파→영구장애 500 분기·테스트 검증·누수 없음)". 런간 변종 = OHS가 *영구* 오류를 raw re-raise하느냐(claude 분기로 clean·codex raw)인데 둘 다 표준상 500이 정답이라 오분류 누수 아님 = 표준·미러 충분한데 LLM 구현이 흔들림 = nondeterminism.

[backstopable=no 확정] 판별자 'transient(재시도 해소)냐 permanent(영구장애)냐'가 런타임 의미층. reviewer line43이 명시적으로 런타임 판정 거부("'transient인지'의 런타임 판정으로 면책되지 않음 — 분기 유무만"). ⑭(check-transient-overmapping=분기없는 통째매핑만)·⑮(check-synthetic-infra-exc=`from`없는 합성만)은 '정당하게 500된 영구오류'와 'should-have-been-domain 누수'를 가르는 깨끗한 AST/텍스트 신호가 없어 원리상 사각 — 거짓양성(정당 영구-500 차단) 위험이 이득 초과. 의도된 잔여.

[처방 동의] 수용+계측. EVAL-METHOD §4.3.1 에러경로 라이브 관측 매트릭스로 EP-3 transient→{503,409} 화이트리스트 강제(조정자 실 SQLite EXCLUSIVE lock+재시도소진 probe로 sequential green 위장 방지). 신규 백스톱/표준 불요(완비·충실 확인). 분류의 자체 경고도 정확·유용: 보정 앵커 'ACL-EX2=2a'를 현 정본 §2:144·§6.2:557-572로 갱신 권장 — 후속 분류 일관성 보호.

#### BC-decomposition-nondeterminism — `0-by-design`  (upheld: True)

분류 유지(0-by-design). 분류자가 틀렸을 가능성을 우선 가정하고 2a/2b/3/1로 반증을 시도했으나 모두 실패했고, 결정트리는 필터 0에서 멈춘다.

[3-드리프트 반증 — 실패] 정본↔미러 byte-identity를 직접 diff로 검증: 정본 final.md:235 = 미러 :219(\"하위 도메인은 발견하고, 바운디드 컨텍스트는 설계한다\"), 정본 :239 = 미러 :223(\"1:1로 묶으려는 시도는 바람직한 목표이지만, 반드시 그래야 하는 것은 아니다 [C]\"), 정본 :648 = 미러 :632(판정-소유→구조 귀결은 *조건부*) — 셋 다 `diff` BYTE-IDENTICAL. 미러가 designer-decides 언어를 잃지도, 소유를 강제하는 규칙을 추가하지도 않았다. 드리프트 아님.

[2a-부족 반증 — 실패] '정본이 침묵'이 아니다. 소유 *판단 기준*은 명시돼 있다: §3.3 규칙1(진짜 불변식을 일관성 경계 안에서 보호, 정본 :658)·§2.4 유비쿼터스 언어(:232). 정본이 미규정으로 두는 것은 *특정 프롬프트의 특정 답*(재고 판정을 catalog가 소유하나 order가 소유하나)뿐이며, 이는 기준 자체가 판단-의존적이라 의도적이다. 즉 '말해야 할 단일 정답을 정본이 빠뜨림'이 아니다 → 2a 아님.

[2b-오류 반증 — 실패] 정본의 *자기 예제*(:1642 `inventory/` BC, :1972 `InventoryACL` — order↔inventory 분리)가 소유를 *처방*하는 것 아닌가를 검토했으나, 이는 :239 \"반드시 그래야 하는 것은 아니다\"와 정합하는 *예시적 분해 하나*일 뿐이고 eval의 실제 catalog/product/order 프롬프트에 소유를 박지 않는다. 오히려 방어가능 분해의 *공간*을 보여줘 0-by-design을 강화한다. 실행하면 깨지는 잘못된 처방 없음 → 2b 아님.

[1-비결정 반증 — 실패, 이 오판이 가장 위험하나 성립 안 함] 카테고리 1은 '정본·미러가 단일 정답을 정하기에 충분한데 LLM이 흔들림'을 요구한다. 그러나 두 분해(catalog=판정소유 [ptcat·ptbootlive-claude·nj7live] vs catalog=데이터소스/order=판정소유 [ptbootlive-codex])는 :239 + 조건부 :648 하 *둘 다 실질적으로 합법*이라 수렴할 단일 정답이 없다. 게다가 시스템이 이 변동을 *명시 인지하고 설계된 해소 경로*를 둔다: design-architect.md:21 \"미고정이면('모르겠다') 네가 배치를 판단하고 *왜*를 명세에 남긴다\" + *왜* \"같은 입력에 BC 경계가 매 실행 달라지지 않게\"; commands/dddjango.md:66 G0 옵션③ \"모르겠다 — 설계자가 정함\" + *왜* \"파이프라인이 고정 안 하면 architect가 매 실행 암묵 달리 정함(재현 불가)\". 결정적으로 design-architect.md:36이 *과잉결정 방지 가드*까지 둔다: \"BC 배치·ACL 생략은 유비쿼터스 언어·소유 경계로 판단하고, 규칙4를 그 근거로 끌어쓰지 마라\" — 기계적 규칙이 아니라 판단에 맡김을 명문화. backstopable=no가 옳다(결정적 백스톱은 정당한 designer-decides 분기 하나를 임의로 위반 판정하게 됨). → 1 아님.

[0-설계상 확정] 정본이 변동을 *의도적으로* 허용함을 명시(:235 '설계한다', :239 '반드시 그래야 하는 것은 아니다')하고, 에이전트 층이 G0 옵션③로 'architect가 정하면 재현불가하나 정당'을 설계에 박았다. 보정 앵커 'BC 분해(판정소유)=0 (architecture-ddd §632 designer-decides·둘 다 방어가능)'와 정확히 일치.

처방: 드롭(결함 아님·정본/미러/백스톱 무수정). 평가 함의 — (a) 이 축으로 산출물이 갈려도 어느 쪽도 FAIL 아님; (b) 치명 FAIL 레인 런간 반전(DR-24 Codex→c4live Claude→nj2live Codex)은 이 자유도+태스크 heaviness 교락이므로 N=1로 런타임 우열 결론 금지(EVAL-METHOD '우열금지' 정합). 재현성을 기계적으로 강제하려면 정본 교정이 아니라 평가 하니스 차원(G0 경계 고정 프롬프트로 옵션③ 경로를 닫음)으로 처리 — 처방 위치는 reference/skill이 아니라 eval 프로토콜이다.

재확인한 file:line: 정본 /Users/hyun/Desktop/dddjango/workspace/reference/architecture-ddd/reference/final.md:235·239·648·658·1642·1972; 미러 /Users/hyun/Desktop/dddjango/dddjango/skills/architecture-ddd/references/final.md:219·223·632(전부 정본과 byte-identical diff 확인); 에이전트 /Users/hyun/Desktop/dddjango/dddjango/agents/design-architect.md:21·36; /Users/hyun/Desktop/dddjango/dddjango/commands/dddjango.md:66; SKILL /Users/hyun/Desktop/dddjango/dddjango/skills/architecture-ddd/SKILL.md:11·19.

#### httperror-malformed-body — `None`  (upheld: True)

UPHELD: 1-nondeterminism (high confidence). Adversarially verified every decision-tree leg by direct file:line re-inspection at the actual current HEAD (a4c7434; classifier cited stale f82f9d7 — corrected below, conclusion unchanged).

(2b — reference WRONG?) RULED OUT. The canonical recipe is correct and executable, not a self-breaking example. workspace/reference/implementation-django-ninja/reference/final.md:503-507 defines the central problem() helper; :526-534 defines `@api.exception_handler(HttpError)` with explicit "깨진 본문·파싱 실패·임의 HttpError → RFC9457 body" coverage and even a non-standard-status guard (HTTPStatus ValueError → "Request error"). LIVE PROOF it works: ptbootlive-claude.md:111 EP-1 (malformed/garbage JSON probe) → 400 application/problem+json; nj7live-codex.md:91 EP-1 → application/problem+json `{"type":"/problems/invalid-request",...}`. This is the OPPOSITE of the FC-1 anchor, whose canonical example 500s on happy path. The reference here teaches the right thing and it runs green → not 2b.

(2a — reference SILENT?) RULED OUT. The reference does not merely mention HttpError — it issues an explicit, load-bearing directive: :607-608 "깨진 본문·파싱 실패처럼 body를 만드는 핸들러가 없는 HttpError는 B만으론 ninja 기본 body({"detail"})라 RFC9457 미달이므로 위 @api.exception_handler(HttpError)를 함께 둔다(B로 대체 불가)"; :664-666 "임의 status·HttpError도 §6.2의 @api.exception_handler(HttpError)가 body를 problem화한다... 대안 B는 ... HttpError body를 대체하지 못한다." grep "outside contract|계약 외|framework-default acceptable" over the reference = ZERO hits for any malformed-body exemption (only the 415 content-type C-policy at :637, which is negotiation, not format). Unlike the ACL-EX2 anchor (reference §2:144 truly silent on infra-exception responsibility), §6.2:526 explicitly prescribes the malformed-body path → not 2a.

(3 — DRIFT?) RULED OUT. `git show HEAD:` grep -c "exception_handler(HttpError)" = 3 for ALL three mirrors at current HEAD a4c7434: canonical reference (3), Claude mirror dddjango/skills/.../references/final.md (3, lines 516/598/654), Codex mirror codex-dddjango/skills/.../references/final.md (3, lines 516/598/654). `git status` on reference + ninja mirror = clean (no working-tree drift). All three carry the correct recipe, committed, parallel positions → no drift.

(0 — BY-DESIGN?) RULED OUT. The reference never says "둘 다 방어가능"/designer-decides for malformed-body format. The only exemption is the 415/406 content-type *negotiation* C-policy (:637, internal-only), and both the reference and the working-tree agent guidance explicitly distinguish negotiation from error *format* — design-architect.md:35 (uncommitted): "415/406 협상 면제(비-JSON 거절)는 에러 형식 면제가 아니다 ... '비-JSON·parse 실패는 framework-default·계약 외'로 배제하지 말고 중앙 problem+json 변환점이 그 오류까지 덮는다고 명세에 박는다." Malformed-body→plain is affirmatively prohibited, not blessed → not 0.

(1 — confirmed.) The reference+mirrors ARE sufficient and committed, yet runtime output splits run-to-run on the SAME standard text: ptcat(Codex)=problem+json vs ptboot(Codex)=plain. Root cause is the architect LLM over-generalizing the 415 carve-out into a format exemption: ptbootlive-codex.md:125 "design-spec:98이 'Non-JSON content-type·parse 실패는 framework-default·outside contract'로 선제 배제 → coder는 명세 충실 구현. 단 표준 §6.2:516은 ... 명시 처방이라 명세의 배제가 표준과 충돌"; :131 confirms run-to-run nondeterminism. The prompt-layer fix (A architect carve-out removal at design-architect.md:34-35 + B reviewer NJ-7 trigger at discipline-reviewer.md:44) made it CONVERGE to problem+json on both runtimes (nj7live-codex.md:18/96/101: design-spec no longer excludes, coder implements handler, EP-1 problem+json). Guidance was sufficient; the LLM wavered → textbook 1-nondeterminism, structurally identical to the FC-2 anchor (reference correct, no hard gate, LLM inconsistent).

backstopable = YES (genuine unmet signal, fillable deterministically). Verified directly: dddjango/scripts/check-catch-all-handler.py:153-154 sets has_catchall only when exc in CATCH_ALL={"Exception","BaseException"} and emits only (1) missing Exception catch-all and (2) handler re-raise — there is NO HttpError-presence check, so a project with handlers + Exception catch-all but no HttpError handler passes exit0 (the malformed-body blind spot, confirmed by ptbootlive-codex.md:103 and nj7live-codex.md:101). The presence of `@<var>.exception_handler(HttpError)` (or register-form add_exception_handler(HttpError, fn)) is a clean AST signal homologous to the existing check — extend/add backstop ⑯ to flag handler-set-without-HttpError. 415 C-policy internal-only exemption does not conflict (format obligation is independent of negotiation policy; reviewer NJ-7 at line 44 already encodes "415 부재는 안 잡되 HttpError problem 핸들러 부재는 본다").

Factual correction (no impact on category): classifier cited commit f82f9d7 / `git show HEAD:`; actual HEAD is a4c7434. Re-verified at a4c7434 — all grep counts (3/3/3) and the clean reference state hold. The agent-layer fix (A+B) is uncommitted (design-architect.md and discipline-reviewer.md show `M`; `git show HEAD:design-architect.md | grep -c "협상.*면제"` = 0), matching memory note dddjango-nj7-httperror-architect ("백스톱 ⑯ 보류·다음=dual라이브→또plain이면 C집행"). The reference (the decision-tree's source of truth) is committed+correct+present; the wavering is purely at the LLM/agent layer → 1-nondeterminism upheld, terminal remedy = deterministic backstop ⑯ on live re-occurrence.

#### catch-all-missing — `None`  (upheld: True)

UPHELD: 1-nondeterminism (backstopable=yes). Adversarially re-walked the decision tree, re-confirming every cited file:line by direct read.

(0) NOT by-design — canonical explicitly criminalizes catch-all-as-cover: workspace/reference/implementation-django-ninja/reference/final.md:467 "핸들러 누락을 catch-all로 때우면 중앙화 완전성 위반이다". No designer-decides.

(2b) NOT canonical-wrong — re-read final.md:464-467 (prescribes @api.exception_handler(Exception)→500 problem+json + logger.exception only), :565-577 (recipe with WORKING code: MRO most-specific-first → catch-all doesn't intercept concrete handlers, executes correctly, does NOT 500 unlike FC-1), :573-575 (forbids raise exc re-raise WITH django-ninja 1.6.x empirical basis "ninja는 핸들러 안의 raise를...Django로 전파해 DEBUG=True면 text/plain traceback이 샌다"). Prescription is correct + executable, not a bug-teaching example.

(2a) NOT silent — explicit complete prescription exists (catch-all bullet + recipe + 1.6.x empirical note + completeness-violation framing). Not ACL-EX2-style responsibility gap.

(3) NOT drift — both mirrors faithful: Claude dddjango/skills/implementation-django-ninja/references/final.md:464-467 byte-identical to canonical (diff EXIT 0); Codex codex-dddjango/skills/implementation-django-ninja/references/final.md:464,565,573 present; reviewer NJ-7 lens in BOTH dddjango/agents/discipline-reviewer.md:44 + codex-dddjango/skills/dddjango-discipline-reviewer/SKILL.md:45.

(1) IS nondeterminism — canonical+mirror both correct AND complete → LLM drifts despite sufficient guidance. Consistent with anchors FC-2(1)/BC-decomp(0). The DR-47 dual-runtime catch-all-absence observation occurred when the 33-item rubric had NO measurement dimension + backstop was mid-addition; symptom self-admits current runs (ptcat/ptbootlive/nj7live) now PASS = nondeterminism amplitude.

backstopable=YES — STRONGEST case: deterministic backstop ALREADY exists+wired. dddjango/scripts/check-catch-all-handler.py (9799B, pure AST): :54 CATCH_ALL set, :77-91 _reraise_lineno (bare raise/raise Name → reraise; raise...from x AND raise NewType(...) EXEMPT), :153-169 per-NinjaAPI-instance aggregation → exit2 (:195). Codex mirror byte-identical (codex-dddjango/skills/dddjango/scripts/check-catch-all-handler.py 9799B). Gate ⑯ wired both runtimes (dddjango/commands/dddjango.md:86 + codex-dddjango/skills/dddjango/SKILL.md:105). Pure structural signal, touched-only, false-pos≈0; low-recall gap (register-style/return{}/multi-API) covered by reviewer NJ-7 semantic lens.

MINOR (non-affecting): whereObserved/skillEvidence cite results/20260607-2022-aclex2live-codex.md which does NOT exist on disk (ugrep "No such file"). The aclex2live dual observation lives in DR-47 + existing grading files (ptcat:60/ptbootlive:71/nj7live:84 confirm catch-all present now). Stale results-path reference, not a logic flaw — category 1 stands on canonical(correct)+mirror(faithful)+backstop(exists), all independently re-verified.

#### catalog-husk — `1-nondeterminism`  (upheld: True)

UPHELD — 1-nondeterminism (high). 적대적 재검증으로 0/2a/2b/3을 모두 직접 file:line으로 반증했고 1이 잔여로 귀결.

(0) by-design? NO. 정본이 "미완 이주"·"§0-1 위반"으로 명시 규정 — discipline-houserules/reference/final.md:27(§0-7), implementation-django/reference/final.md:1030-1035(§10.4), architecture-ddd/reference/final.md:632·648. BC분해 anchor(designer-decides)의 정반대.

(2b) 정본 틀림? NO. 처방 추적: §10.4(final.md:1030)는 `git rm -r <app>/` + INSTALLED_APPS 탈등록을 명령 — 실행하면 husk가 *고쳐진다*(FC-1 anchor의 happy-path-500 버그 예시와 달리 정본 처방이 올바름).

(2a) 정본 부족? NO(최고위험 오판이라 최강 검증). 정본은 침묵이 아니라 *실패모드를 축자적으로 진단*: implementation-django/reference/final.md:1033-1035 "코더가 move를 copy로 떨어뜨려(새 트리만 만들고 옛 루트 git 방치) 앱이 두 곳에 남는다" — symptom의 copy-not-move·탈등록 누락을 글자그대로 예견. 변종(빈 migrations dir)도 같은 `git rm -r`(line 1030)이 커버. ACL-EX2 anchor(houserules §2:144 인프라예외 침묵)와 명확히 구분.

(3) 드리프트? NO. 3개 load-bearing 구절 모두 정본↔미러 byte-identical 확인: houserules §0-7(canon:27=mirror:27), impl-django §10.4(canon:1030-1035=mirror:1001-1006), architecture-ddd §632(canon:632=mirror:632). 에이전트도 규칙 운반(design-architect.md:40 "이주는 배타적이다… 옛 루트 완전삭제·INSTALLED_APPS 탈등록 결과제약"; discipline-reviewer.md:46 "application/ 컨테이너 누락(앱이 루트 평면)"). 드리프트 0.

(1) 비결정? YES. 정본·미러·에이전트가 올바르고 명시·byte-identical인데도 Codex coder가 런마다 흔들리고 Claude는 항상 완전이주. 0/2a/2b/3 제거 후 잔여=1.

backstopable=yes-in-principle(경험적 caveat 동반). check-app-container.py:197-198 `if _has_migrated_counterpart(...): continue`가 역방향 husk(counterpart 존재∧옛 루트 공존)를 면제 → 구조적 사각 직접 확인. 전용 백스톱 check-duplicate-app.py(DR-51 ⑰)는 부재 확인(ls 실패=롤백됨). 즉 의미층이 아니라 배선/발화 문제.

⚠️ 분류 carried-forward에 흡수할 실측 정정(카테고리 불변): symptom의 whereObserved가 현 심각도를 과장. 최신 산출물 재독 결과 — ptcat-codex:39,109·nj7live-codex:51,110·ptbootlive-codex:52,123 모두 *치명* SH-1/4=PASS이고 빈 `migrations/` dir 변종(비치명)만 잔존. *치명* full-husk(apps.py 생존+INSTALLED_APPS 등록 유지)는 dslive-codex(DR-50)·duplive-codex(ptcat:109가 "이전 duplive-codex 옛 루트 잔존 SH-1/4 입력 흠" 대비)에서만 재현. 이주배타성 처방을 캐시에 신선화한 뒤 최근 3런은 빈-dir 변종만 = 같은 런타임이 때론 완전·때론 husk → 1-nondeterminism 강화. 치명형은 라이브 N이 비재현으로 수렴 중, 빈-dir 변종이 라이브-잔존하나 비치명. remedy의 "현상 라이브 N≥2 재현 선행" caveat가 *치명형*에 정확히 부합(현재 비재현). 본 워크플로는 분석전용이라 어떤 파일도 미수정.

#### NJ-1-jsonresponse — `1-nondeterminism`  (upheld: True)

UPHELD as 1-nondeterminism (high). Adversarially stress-tested all four alternative categories against direct file:line evidence; all fail, leaving 1.

REFERENCE IS CORRECT AND PRESENT (excludes 2a + 2b). Canonical `workspace/reference/implementation-django-ninja/reference/final.md` prescribes the central problem helper unambiguously: `:497` `from ninja.responses import Response  # JsonResponse 서브클래스 + ninja JSON 인코더`, `:503-504` `def problem(...) -> Response`, `:507` `return Response(body, status=status, content_type="application/problem+json")` — with `:505` stating "모든 오류 변환이 이 헬퍼만 거친다". Hand-rolled JsonResponse is explicitly forbidden in PROSE at `:130` ("operation 본문에서... 수제 HttpResponse/JsonResponse로 오류 응답을 직접 만들지 않는다") and reinforced at `:627-628`, `:649` ("수제 JsonResponse 금지"). 2b excluded: the recipe RUNS correctly — `ninja.responses.Response` is real and the example is valid (no bug taught). 2a excluded: not silent — the prescription is the canonical recipe (a concrete runnable correct example IS sufficient guidance), and even the eval framework reads it as a clear prescription (RUBRIC.md:66 "§6.2가...ninja.responses.Response 반환함을 처방"). The line-130 prohibition being scoped to operation bodies does not create a gap, because the central-handler requirement lives in the prescribed recipe code that the standard mandates as the single conversion point.

NO DRIFT (excludes 3). Byte-identical across all three sources: canonical `:497/:507`; Claude mirror `dddjango/skills/.../final.md:487/:497`; Codex mirror `codex-dddjango/skills/.../final.md:487/:497` (line offset = header only). Prohibition lines (130/627-628/649 → mirror 639) also identical. Codex mirror has ZERO loss — it carries the exact correct prescription Codex then ignores at runtime.

NOT 0-BY-DESIGN. RUBRIC.md:66 explicitly lists `django.http.JsonResponse` under "진짜 일탈(채점 대상): (a) ninja.responses.Response 아닌 django.http.JsonResponse = 경미(🟡 NJ-1)"; EVAL-METHOD.md:100 (Q-a) "에러 응답이 django.http.JsonResponse로 나가나?(Y=🟡 NJ-1 경미)". It is a SCORED deviation, not a designer-permitted variant. The classifier's reading is exactly right: "underdetermined" (RUBRIC:65, ptbootlive-codex:126) refers strictly to grader split on SEVERITY (🟡 minor), never to permission. No "둘 다 방어가능"/designer-decides language exists for this point.

1-NONDETERMINISM CONFIRMED BY DIRECT CROSS-RUN OBSERVATION. Same prompt family, opposite outcomes run-to-run: ptbootlive-codex `config/api.py:38` django.http.JsonResponse (results/20260609-1523-ptbootlive-codex.md:67); nj7live-codex `config/api.py:51` django.http.JsonResponse (results/20260609-2010-nj7live-codex.md:66); ptcat-codex `config/api.py:20` "JsonResponse/DRF 0" — CLEAN (results/20260609-0452-ptcat-codex.md:54). Claude complies consistently. Sufficient + faithful guidance in all three sources, yet Codex flips — textbook nondeterminism. Probable cause confirmed: `ninja.responses.Response` IS a JsonResponse subclass (reference:497 comment) and wire behavior (content-type/status) is identical, so the model slips harmlessly to the more familiar django import.

REMEDY (concur): accept+instrument, consistent with FC-2 anchor (backstopable=partial, accept-first). A narrow deterministic backstop is technically possible (AST: presentation config/api.py @api.exception_handler fn returning django.http.JsonResponse(), complementing the two existing backstops that deliberately exclude this point — check-response-schema-bypass.py excludes the central handler's response assembly, check-error-centralization.py sees application layer only). But 🟡-minor severity + identical wire behavior + grader-underdetermined make a hard gate disproportionate (false-positive/proportionality risk). Keep discipline-reviewer salience scoring it 🟡 NJ-1 via EVAL-METHOD §4.3.1/100 Q-a. No standard edit warranted — canonical and both mirrors are already correct.

#### NJ-5-bare-status — `None`  (upheld: True)

분류 1-nondeterminism 유지(high). 적대 검증 4축 모두 분류를 지지.

(0 by-design 반증) NJ-5는 RUBRIC.md:60·rubric-metrix.md:59 채점 정규항목("결정/—(경미)")이며 designer-decides 축 아님. 정본은 bare `-> Status`/deprecated tuple을 허용 변종으로 명시하지 않고 특정 정형을 처방 → 0 배제.

(2b 반증 — 가장 중요) FC-1(2b 앵커)과의 직교성이 핵심 쟁점. 정본 final.md:167·171의 *워크드 예시 자체*가 `def create_order(...) -> Status[OrderOut]:` ... `return Status(201, OrderOut(...))`를 다중 status `response={201:OrderOut,404/409:ProblemOut}`와 함께 보여주고, 이 `Status(201,...)` 런타임이 ninja-extra 다중응답서 500을 유발(nj7live-claude.md:27·83 실측). 그러나 그 런타임-500은 **FC-1이 잡는 책임**이고 NJ-5가 아니다. NJ-5는 순수 *annotation 형태*(`-> Status` bare vs `Status[OrderOut]`)와 *반환 관용구*(deprecated tuple)만 본다. annotation 처방("단일 성공 schema면 그 타입, 다중 성공 status면 `Status[...]`", :132)은 건전·구체적이고, `-> Status[OrderOut]`로 쓰면 정확·비-deprecated. 결정타: 정본은 bare `-> Status`를 *한 번도* 가르치지 않고(grep `-> Status` 비-subscript = exit1, 전부 :167/195/654 parametrized) deprecated tuple도 *한 번도* 가르치지 않으며(grep `return 201,` = exit1) :626에서 명시 deprecated 못박음. 즉 두 변종 모두 *올바른 처방으로부터의 실제 일탈*이지 정본이 가르친 버그가 아님 → 2b 결정적 배제. 증상의 '아이러니'(Codex tuple 작동 vs Claude `Status()` 500)는 정확히 NJ-5(겉치레 form)와 FC-1(런타임)이 직교라서 발생.

(2a 반증) 침묵 아님. :132 처방 + :626 deprecation 노트가 명시 존재 → 2a 배제.

(3 drift 반증) 정본·미러 둘 다 올바름. 미러 final.md:122(처방)·:157/:185(예시 `Status[OrderOut]`)·:616(deprecation)이 정본 :132/:167/:195/:626과 byte-identical(diff = P1 메타헤더 strip + 제목줄뿐). SKILL은 별도 확인 불요(미러 본문 일치) → 3 배제.

(1 잔여 — 모호성을 LLM탓 전가? 반증) 정본·미러가 *정말* 충분·명시적인데 같은 프롬프트서 런간 분산: bare `-> Status`(ptcat-codex:58·ptbootlive-codex:71·nj7live-claude:83)·deprecated tuple(nj7live-codex:70 `-> tuple[int,...]`/`return 201,...`) vs 정형 `-> Status[OrderOut]`(ptbootlive-claude:69) → 명백한 1-nondeterminism. backstopable=partial-leans-no: 16종 check-*.py 중 `func.returns`의 Status-subscript나 2-tuple return 탐지 0(check-response-schema-bypass.py는 raw JsonResponse/HttpResponse 2xx 본문 우회만·`.returns` 미검사 확인). bare-Status/tuple은 깨끗한 AST 신호로 탐지 *가능*하나, EVAL-METHOD.md:26·:134 명시 "NJ-5·6=경미(정규 카운트, 강등 없음)"이라 상한강등도 없는 겉치레 항목 — DR-35/DR-38 '반복확인된 비-겉치레만 백스톱' 자세와 일관되게 value-to-noise 낮음.

처방: 수용+계측. 정본/미러 변경 불요(둘 다 올바름). 라이브 N≥2 반복·비례성 확인 시 *좁은* AST 백스톱(반환 annotation이 bare Name 'Status'이거나 operation 본문 ast.Return이 2xx 2-tuple → exit; download/stream/redirect/204 면제) 원리상 가능하나 그 전까지 RUBRIC 경미 유지 + reviewer nit(현행 NJ-5 전용 불릿 없음). 핵심: LLM 비결정이지 지식 결함 아님.

#### NJ-4-openapi-extra — `None`  (upheld: True)

분류 유지: 1-nondeterminism (high). 모든 file:line 인용을 정본·미러 1차 소스에 직접 대조해 적대적 반증을 시도했고, 네 카테고리 대안이 전부 무너진다.

[2b 반증 — 정본은 틀리지 않고 옳다] workspace/reference/implementation-django-ninja/reference/final.md:128 "가능한 모든 status를 `response={...}`에 선언한다(404·409·422 포함)" + :129 "openapi_extra·get_openapi_schema로 status를 수동 선언하는 것은 이 요구를 충족하지 않는다 … ninja는 응답 타입으로 인지 못해 … 계약 밖". 정상 예시 :160-166 `response={201: OrderOut, 404: ProblemOut, 409: ProblemOut}`는 실행 가능·올바름. openapi_extra/get_openapi_schema 의 *유일한 다른* 언급(:618 "생성된 OpenAPI를 사후 변형하지 않는다")조차 금지를 강화. 자기모순 0 → 보정앵커 FC-1(2b: 표준이 버그 교육)과 결정적으로 다름.

[2a 반증 — 침묵 아님] :129가 이 실패모드(openapi_extra로만 선언)를 *정확히 명명*하고 이유까지 설명. 다른 섹션에 묻힌 게 아니라 정면으로 다룸. 보정앵커 ACL-EX2(2a: 인프라예외 책임 침묵)와 다름.

[3 반증 — 드리프트 0] diff 결과 정본 :128-129 == Claude 미러 dddjango/skills/.../references/final.md:118-119 == Codex 미러 codex-dddjango/skills/.../references/final.md:118-119 **byte-identical**(셸 diff 확인). SKILL.md 압축(Claude:22·Codex:21)도 보존. 정본엔 맞는데 미러가 잃은 부분 없음.

[0 반증 — designer-decides 아님] openapi_extra-for-status 에 "둘 다 방어가능"·designer-decides·underdetermined 어휘 0. 정본은 "충족하지 않는다"로 단정. (:410 의 designer-decides 는 503-vs-409 status *선택*에 관한 것·무관.)

[1 확정] 정본·양 미러 모두 옳고 충분 → 현행 런 전부 PASS(nj7live-codex:69·ptcat-codex:57 등 NJ-4 ✅)인데 poc-codex(api_orders.py:209,211)서만 FAIL = 충분한 지침에도 런마다 갈리는 비결정 시그니처. 보정앵커 FC-2(1)와 동형(hard 강제 부재 시 LLM 비일관).

[backstopable=yes, 이미 출하·배선] 분류자 평가 정확. 전담 결정-레인 백스톱 ⑤ check-openapi-error-declaration.py 가 Claude(dddjango/scripts/, _scan_file:114-132·_openapi_extra_error_statuses:95-111 — openapi_extra responses 4xx/5xx ∧ response= 누락 → 설명 산출·exit2)·Codex(codex-dddjango/skills/dddjango/scripts/) 양쪽 존재, commands/dddjango.md:86 에 ⑤번으로 배선("openapi_extra로만 선언하고 response={…}엔 누락 = NJ-4 위반"). poc-codex 의 정확한 리터럴 형태를 AST로 결정적 차단. 저-recall 잔여(:15-30 자기명시: 변수/spread `{**EXTRA}`·get_openapi_schema 오버라이드)만 의미 레인이며 discipline-reviewer.md(API 오류 중앙화 규율·NJ-7 불릿)가 커버.

[분류자 표현 1건 미세보정 — 카테고리 불변] 분류자가 증상의 "G3 backstop exit0 통과"를 "부정확"이라 했으나 약간 불공정: RUBRIC.md:66 이 그 response-schema 백스톱을 실제로 "G3 backstop"이라 부르고 (a)(b) 둘 다 거기선 exit0 통과라고 *동일하게* 진술. 증상은 RUBRIC 자체 용어를 씀. 그러나 분류자의 실질 논점(별도 결정-레인 ⑤가 흔한 형태를 잡음)은 정확·load-bearing 하므로 1-nondeterminism + backstopable=yes 판정을 오히려 강화. remedy(현행 4-레그 유지·신규 처방 불요·계측)도 타당.

#### NJ-2-raw-parsing — `1-nondeterminism`  (upheld: True)

분류(1-nondeterminism, backstopable=no) 유지. 적대적 반증 시도가 모두 실패했고, file:line 직접 재확인으로 네 대안 카테고리를 각각 배제함.

[2b 반증 — 가장 중요한 적대 테스트] FC-1식 "정본이 버그를 가르침" 가능성을 우선 의심해 §6.3 레시피를 정밀 검증. 정본 implementation-django-ninja/reference/final.md:637 은 *옛* parse_body 415 처방이 왜 깨지는지 명시("`parse_body` 안에서 `raise HttpError(415)`해도 400으로 먹혀 작동하지 않는다")하고, *작동하는* `add_decorator(fn, mode="view")` 레시피(:639-655, operation.run 이전 view 데코레이터에서 request.content_type 검사→중앙 problem(415) 헬퍼)로 교체함. DEVLOG.md:93 DR-35 가 "근본=ninja 1.6.x parse_body→400 wrap 버그로 표준 §6.3 처방 *자체가 버그* → add_decorator(mode=\"view\")로 §6.3 3미러 교체"로 이 정정을 박제. 즉 버그는 *과거에* 존재했으나 이미 정정됨 → 현재 텍스트는 올바름(2b 아님). FC-1(2b 유지)과의 결정적 차이=FC-1은 충돌 schema 버그가 텍스트에 *미정정 잔존*, NJ-2는 정정 완료.

[2a 반증] 침묵 아님. §1.3 "Router thinness 원칙"(:71), §2.3 클래스 컨트롤러(:179+, `payload: OrderIn` 선언 바인딩 강제·"오류는 raise하고 성공만 return"), §6.3:637(raw json.loads/request.body 함수형·클래스 둘 다 금지 NJ-2 명문)·:660-661("어느 status에서도 operation·helper가 request.body/json.loads로 본문 수동 파싱하지 않는다 — operation을 얇게 유지하는 핵심 신호")가 이 문제에 직접·올바르게 말함.

[3-drift 반증] NJ-2 라인 내용 byte-identical. canonical:637 = claude-mirror:627 = codex-mirror:627 모두 SHA256 e46b634fa1df5b13...(분류가 인용한 해시와 일치). 같은 라인번호 SHA 불일치(canonical:637 6014627f≠... )는 canonical-only "P1 Source Sufficiency" 메타블록(:3-12)에 의한 10행 오프셋 때문이며, 분류가 미러를 :627로 인용해 이를 정확히 반영함 — 진짜 드리프트 아님. 두 미러는 서로 full-file 동일(MIRRORS-IDENTICAL). SKILL.md:19 "Router는 HTTP 어댑터로 얇게 §1.3"로 thin-operation 요약 보강.

[0-by-design 반증] NJ-2는 *명시적 금지*(raw 파싱 prohibition)지 designer-decides 축 아님.

[backstopable=no 확정] check-*.py 16종 중 json.loads/request.body를 *코드로* 스캔하는 스크립트 0(엄격 grep -ln 결과 공집합). 분류가 "거짓 단서"로 든 둘을 검증: check-ninja-boundary-middleware.py는 AST로 settings.MIDDLEWARE 항목만 스캔(:90-115, regex ^application...presentation_layer$ :47), json.loads는 remediation 메시지 문자열일 뿐 — *미들웨어 자가등록*이라는 별개 NJ-1 관심사. check-idempotency-scope-creep.py는 regex idempoten(:49) 매칭, NJ-2는 근본원인 주석(:7)에만 등장. DEVLOG DO-NOT-RETRY #12(:185)가 독립적으로 같은 결론: operation 콘텐츠협상/입력파싱 백스톱 신호가 "정당 코드와 동형(잡으면 FP·안 잡으면 operation 인라인 회피·양립불가)". 신호가 의미층(비-operation 맥락의 raw json.loads는 정당·"operation 얇음"은 품질판단)이라 결정적 백스톱은 위양성 또는 이름회피 누락 불가피.

[1-nondeterminism 양성 근거] 양 런타임이 충실·올바른 지침을 가졌으나 런간 흔들림. DEVLOG:85 DR-34 Claude NJ-2 치명 FAIL ↔ :78 DR-27/DR-24 Codex NJ-2 FAIL(역방향) → :94 DR-36 *양 PASS*("효과 입증 ... DR-34서 또 반전·N=1·우열 금지"). 양방향 반전 = LLM이 충분한 지침에도 흔들리는 nondeterminism의 전형. FC-2(=1) 보정 앵커와 정합.

처방(수용+계측·신규 백스톱 금지)은 DR-35의 검증된 결론과 일치. "1을 LLM탓으로 잘못 돌렸나"라는 최위험 오판 점검: 정본이 모호/부족하지 않음을 §1.3·§2.3·§6.3 세 곳 직접 인용으로 확인했고, 레시피가 실행가능함을 DR-35 라이브(DR-36 양 PASS)로 확인 → 2a/2b로 강등할 근거 없음. 분류 정확.

#### controllerbase-inheritance — `None`  (upheld: True)

UPHELD — 1-nondeterminism, high confidence. Adversarially re-walked every tree axis at file:line; the classification's substance holds on all five, with one evidence correction (Codex mirror path) that does not change the verdict.

0 (by-design)? NO. Reference takes a single clear stance, not "둘 다 방어가능": workspace/reference/implementation-django-ninja/reference/final.md:211-212 ("**`ControllerBase`를 직접 상속하지 않는다** — `@api_controller` 데코레이터가 컨트롤러 기반을 자동 주입한다(명시 상속은 중복이다)") + inline :193 ("ControllerBase 미상속(@api_controller가 자동 주입)"). Not designer-decides.

2b (reference wrong)? NO — and this is the sharpest discriminator. The reference says inheriting is *redundant* ("중복이다"), not *broken*. `@api_controller` auto-injects the controller base, so `OrderController(ControllerBase)` still runs correctly. This is categorically asymmetric to the FC-1 anchor (2b), where executing the taught example breaks the happy path with a 500 — there the standard teaches a bug; here it teaches no bug, only redundancy. So the reference is correct, not wrong. LLM misuse of correct guidance = 1, not 2b.

2a (insufficient)? NO. The most dangerous misclassification to rule out, and it is genuinely ruled out: not silence. Explicit, unambiguous guidance exists at :211-212 and :193 ("미상속", "직접 상속하지 않는다", "명시 상속은 중복이다"). It is not buried in an unrelated section — it sits in the §2.3 class-controller 요점 list directly under the canonical example.

3 (drift)? NO. Both mirrors are byte-identical to the reference. Claude: dddjango/skills/implementation-django-ninja/references/final.md:201-202 (diff IDENTICAL). Codex: codex-dddjango/skills/implementation-django-ninja/references/final.md:183,201 (diff IDENTICAL). CORRECTION to the original skillEvidence: it cited the Codex mirror as codex-dddjango/skills/dddjango-implementation-django-ninja/SKILL.md and claimed ControllerBase was absent there. That path does not exist; the real Codex mirror has the same path shape as Claude (skills/implementation-django-ninja/references/final.md) and carries both the :183 inline comment and the :201 "직접 상속하지 않는다" bullet byte-identically. The no-drift conclusion is therefore correct; only the cited path was wrong. Verdict unaffected.

1 (nondeterminism)? YES. Reference + both mirrors hold the correct, unambiguous guidance byte-identically, yet Codex emitted the redundant `OrderController(ControllerBase)` (ptcat-codex results/20260609-0452-ptcat-codex.md:113 "부수(채점 무관)…`OrderController(ControllerBase)` 명시상속(§2.3 권고 위반·nit)", :120 "품질 nit: …`ControllerBase` 명시상속") while Claude complied (DR-48). The enforcement surface is empty in exactly the way nondeterminism predicts: discipline-reviewer.md has 0 ControllerBase mentions (grep count = 0; the §6.2 "무조건 클래스 컨트롤러" bullet at :42 governs only 함수형 Router 잔존 vs 클래스 형태, never the inheritance detail), and dddjango/scripts/ has 0 ControllerBase/api_controller coverage (grep NONE). Sufficient guidance + zero enforcement + LLM wavers = textbook 1-nondeterminism. Consistent with anchors ACL-EX2 (2a), FC-1 (2b), BC분해 (0).

backstopable = yes (technically): an `@api_controller`-decorated class whose bases contain `ControllerBase`/ninja_extra base is a clean AST structural signal, no semantic judgment. But nit-weight and N=1 make an 18th deterministic backstop disproportionate per the DEVLOG "only backstop repeatedly-confirmed" principle (DR-35/DR-33), since correct ninja-extra code does not break. Proportionate remedy: accept+instrument until live N>=2; if recurs, add a discipline-reviewer one-liner under :42 (grounded in §2.3:211-212), reserving a backstop for confirmed recurrence. Reference and both mirrors stay unchanged — already correct and synced.

#### logger-exception-missing — `None`  (upheld: True)

분류 유지(1-nondeterminism · backstopable=no · confidence high). 4개 적대 반증 시도 전부 실패.

(2b 배제) 정본 레시피는 *실행 가능*하다 — FC-1 앵커(OrderOut.status:str↔ProblemOut.status:int 충돌로 happy path 500)와 달리 깨지는 예시가 아니다: workspace/reference/implementation-django-ninja/reference/final.md:491 `import logging`·:499 `logger = logging.getLogger(__name__)`·:539 `logger.exception(...)`(`_server_error` 내부)이 모두 정의되고, :576 catch-all `on_unhandled`가 :577 `return _server_error(request, exc)`로 위임. 표준은 *올바른* 동작을 가르친다.

(2a 배제) 침묵 아님 — :475 산문 명령 "스택은 `logger.exception`으로만 남긴다" + 작동 코드. ACL-EX2(인프라예외 책임 진짜 침묵)와 정반대.

(3 배제) 미러 드리프트 없음 — claude(dddjango/skills/implementation-django-ninja/references/final.md)·codex(codex-dddjango/skills/implementation-django-ninja/references/final.md)·canon 모두 logger.exception count=3, 동일 라인(미러 465/529/580). ⚠️ 분류문의 Codex 경로 문자열 `dddjango-implementation-django-ninja`는 오타(실경로는 접두사 없음)이나 *실질*(count=3·충실)은 실파일로 확인됨 → 결론 무영향.

(1 확정) 같은 코퍼스인데 출력 갈림: ptcat-codex(results/20260609-0452-ptcat-codex.md:60)는 logger.exception 누락(명시적 nit·NJ-7 PASS)인 반면 ptbootlive-claude:71·nj7live-codex:72·ptbootlive-codex:73(":73 ...ptcat의 logger 누락 개선")는 모두 보유. = FC-2 앵커(권장·hard 게이트 부재·LLM 비일관)와 동형.

(backstopable=no 확정) check-catch-all-handler.py 차단조건은 catch-all 부재+되던지기만 검사 — logger.exception은 :191 docstring 인용에만 등장(조건 아님), 픽스처는 catch-all 보유·`raise exc`=0이라 exit0 정당. discipline-reviewer.md:44 NJ-7 불릿은 로깅 호출 미커버(agents logger grep=표준인용뿐). RUBRIC.md:62 NJ-7 통과기준에 logger.exception 미포함(:51-52/:117 = 정적 결정레인 grep·관측성 아님 → 비채점 nit). 전용 게이트는 등가형식 거짓양성(logger.error exc_info=True·구조화로거·로깅미들웨어)+`_server_error` 위임추적 필요+최저심각도라 DR-35/DR-38 철학(반복확인 blocker/important·깨끗신호만)에 부적합.

처방: 수용+계측(콘텐츠 무변경·백스톱 신설 금지·RUBRIC freeze). 정본·미러 이미 올바르고 다수 런이 자발 준수 → 잔여흠 원장 기록. 선택적 최저비용 레버(필수 아님): reviewer.md:44 nit 한 줄, 단 프롬프트-only 넛지 신뢰도 낮음(DR-22 0/3).

#### 415-406-overengineering — `0-by-design`  (upheld: True)

분류 유지: 0-by-design (DROP). 적대적 재검증에서 네 후보 모두 file:line으로 반증됨.

[2b 반증 — 정본이 틀린 게 아니다] 정본 implementation-django-ninja/reference/final.md §6.3:658-659가 협상을 *선택적*으로 명시("대안 표현을 *실제로* 제공할 때만 협상이 의미 있고, 단일 표현이면 보통 406이 불필요하다")하고, architecture-api §7.2:313이 406을 정책 재량으로 둔다("가용 표현 특성 목록을 본문에 제공하거나, 정책상 기본 표현으로 대체 응답할 수 있다"). §6.3:637의 415 레시피는 `add_decorator(mode="view")` *작동하는* 처방(DR-35 사후)이지 실행하면 깨지는 예시가 아니다 — FC-1 앵커(happy path 500)와 달리 실행 결함이 없으므로 "정본이 버그를 가르침"이 아니다.

[2a 반증 — 침묵 아니다] §6.3:637이 C 정책 기본을 명시 진술한다("(a) 기본은 내부전용이라 비적용(C 정책 — 내부 클라이언트만 호출하면 content-type 강제가 불요)") + opt-in 메커니즘("(b) 외부 공개로 415가 정말 필요한 endpoint만 함수형 Router로 격리"). 에이전트도 design-architect.md:35에 "침묵 시 기본 내부전용" 명문. 스코프-의도 규칙이 *저술되어 있다*.

[3 반증 — 드리프트 아니다] diff 4회 실행: 정본 vs Claude/Codex 미러의 유일한 차이는 *앞에 덧댄* P1 Source Sufficiency 메타블록과 스코프 배너뿐, §6.3/§7.2 *본문*은 동일. "C 정책 — 내부 클라이언트만 호출하면 content-type 강제" grep 카운트가 정본·Claude·Codex 모두 정확히 1로 일치. 양 에이전트(design-architect.md:35·discipline-reviewer.md:41)도 일관.

[1 반증 — 가장 위험한 오판을 회피] 비결정성으로 보면 고칠 수 없는 걸 "LLM 탓"으로 돌리는 게 아니라 *반대로* 허용된 동작을 결함으로 오인하게 된다. 증상은 정본이 *허용하는* 과설계다. escape-valve(§6.3:637 외부공개 격리)는 *정본이 대개 침묵하는* 스코프 의도에 대한 opt-in이라, 스코프 침묵 시 coder가 (외부일 수 있는) endpoint에 415/406을 발명하는 건 sanctioned discretion이지 충분한 지침을 어긴 흔들림이 아니다. DR-38 로그("백스톱 구조적 불가·신호가 정당코드와 동형")가 협상 신호(`_parse_media_range` q파싱)가 정당 외부 endpoint 구현과 구조적으로 동형임을 확정 — 의미층이라 깨끗한 AST/텍스트 신호 부재. 단 필터 0이 먼저 발화하므로 1번 가지 자체에 도달하지 않음.

[0 확정 — 필터 0이 먼저 발화] 정본이 이 변동을 *의도적으로 허용*: §7.2:313(406 정책 재량)·§6.3:658-659(협상 선택성)·§6.3:637(415 내부전용 기본 + 외부공개 opt-in). 보정 앵커 BC분해(0·designer-decides)와 동형, FC-1(2b·버그 교습)과 대조. reviewer가 이미 비지적(discipline-reviewer.md:41 "415 비적용 비지적 — 내부전용 스코프에서 415 부재를 지적하지 않는다"). DR-38이 "막을 위반 아님"으로 종결.

[처방] DROP. 신규저술(2a)·정정(2b)·재동기(3)·백스톱(1) 어느 것도 불필요. 잔존물은 EVAL-METHOD/RUBRIC이 소유한 Q-1(경미) 채점 판단뿐(코드/스킬 무변경). 굳이 후속이면 평가지에서 "스코프 외부공개 명시 없는데 415/406 협상 발명"을 Q-1 경미로 균일 표기하는 채점 일관성 정도.

[정직 — 라인번호 미세 드리프트] rationale이 인용한 "§6.3:637/658-659/668-671·§7.2:313"은 실제 정본 라인과 *일치* 확인됨(637=415 C정책·658-659=협상 선택성·313=406 정책대체). DR-38이 일부 인용에서 ":443-444"를 썼으나 그건 다른 버전 라인이고, 현행 정본의 해당 텍스트는 위 라인에 실재. 인용 모든 주장이 실제 file:line에 존재·정확.

#### 415-bypass-functional-router — `1-nondeterminism`  (upheld: True)

UPHELD — category 1-nondeterminism, backstopable=no. Adversarially re-verified every cited file:line; the category holds, with three minor citation imprecisions that do not change it.

CORE SPINE CONFIRMED:
- §6.3 C policy is byte-identical across all three mirrors: workspace/reference/implementation-django-ninja/reference/final.md:637 == dddjango/skills/.../final.md:627 == codex-dddjango/skills/.../final.md:627 (diff: the ONLY corpus↔mirror difference is a 10-line "P1 Source Sufficiency" header stripped from mirrors, exactly explaining the 637→627 offset; §6.3 body identical). Rules out cat 3 (drift).
- Architect OWNS + defaults internal: design-architect.md:35 == codex SKILL.md:35 (byte-identical diff confirmed): "415/406 콘텐츠 협상은 기본 내부전용 비적용 ... 외부 공개로 415가 정말 필요한 표면이면 명세에 '외부 공개'를 명시 기록하고(침묵 시 기본 내부전용)". This explicitly assigns the external/internal decision to the spec AND states the default — so NOT silence, ruling out 2a (contrast genuine 2a ACL-EX2 which is silent).
- Coder must DEFER: coder.md:38 == codex coder SKILL.md:34 (byte-identical): "함수형 Router는 외부공개 415 격리 같은 *명세가 지정한* 예외 경로에만 둔다."
- RUBRIC.md:156 carries the Q-1 C-policy "decision-crystallized" block; RUBRIC.md:145 scores the exact Codex 406/415 invention as "Q-1 과설계". Both confirmed.

ADVERSARIAL PROBES ALL FAILED TO OVERTURN:
- 2b? The §6.3 recipe and C policy are sound — no broken/executing-fails example. No 2b.
- 2a? Reference is NOT silent; it routes the decision through architect/spec and defaults internal. No 2a.
- 3? Standard is faithfully mirrored at every layer (corpus, architect, coder, reviewer, rubric). No drift. No 3.
- 1? Standard correct+complete+faithfully mirrored, yet the Codex coder runtime self-classified an internal-only surface as external to take the functional-Router escape — a semantic LLM judgment drift on a determination the standard explicitly defaults to internal. Matches anchor FC-2 (cat 1). This IS Category 1.

BACKSTOPPABLE = NO confirmed empirically: a spec-declared-external functional Router and a self-escalated one produce identical code shapes (functional Router + add_decorator(mode="view")); no clean AST signal separates them. I enumerated all 16 dddjango/scripts/check-*.py — NONE read internal/external intent (only check-idempotency-scope-creep.py greps spec prose, for a different signal). Distinguishing requires reliably parsing design-spec prose for "외부 공개", not a deterministic structural signal.

THREE MINOR CITATION CORRECTIONS (non-determinative):
1. The codex reviewer carve-out ("외부공개 415 격리용 함수형 Router(§3.7·§6.3)는 정당한 예외 경로라 대상 아님") is byte-identical to claude's but sits at codex SKILL.md:43, NOT :42 as the classification stated (claude is :42; off-by-one from a preceding bullet). The rule IS present in both runtimes — substance intact.
2. The classification names "check-structure.py" as the existing weak backstop, but that file does NOT exist in dddjango/scripts/. This STRENGTHENS backstopable=no: not only does no backstop read external intent, the named one is absent (the ninja-adjacent scripts are check-ninja-boundary-middleware.py / check-catch-all-handler.py / check-openapi-error-declaration.py / check-response-schema-bypass.py, none of which read internal-vs-external).
3. The carve-out's "§3.7" cross-reference is a phantom — no §3.7 exists in the corpus ninja final.md (legacy-path content is at §2.3:174, legacy warning at :116). This is a stale section NUMBER in a parenthetical pointer only; the substantive prescription (default-internal, functional Router only for spec-declared external) remains correct and complete, so it does not make the reference "wrong" in the 2b sense.

Net: the standard is correct and faithfully mirrored at corpus/architect/coder/reviewer/rubric; the failure is the Codex coder self-deciding internal→external against a spec-routed, default-internal rule. Category 1, backstop NO. Remedy = accept + reviewer spec-vs-code consistency check (if a touched functional Router carries 415 isolation, require a "외부 공개" line in the design-spec per architect.md:35/coder.md:38; absent it, flag important per RUBRIC:145/156); collect live N≥2 (DR-48 backlog "2차 라이브·3차 백스톱", dslive-codex 후속②) before any hardening; do NOT add a pure "functional-Router-present" AST backstop (false-positives on legitimate spec-declared isolation + grandfathered legacy). dslive-codex result file is uncommitted on this branch (confirmed absent), consistent with the classification's note; symptom + verified standard text are sufficient.

#### idempotency-scope-creep — `1-nondeterminism`  (upheld: True)

CATEGORY UPHELD = 1-nondeterminism (backstopable=yes), but the classifier's rationale contains FABRICATED citations that must be corrected; the verdict survives on the real, verified evidence.

ADVERSARIAL RE-CHECK of each alternative (file:line re-read directly):

[0 by-design? NO] Sought "둘 다 방어가능"/designer-decides for unrequested idempotency — none. The opposite is verbatim true: agents/design-architect.md:36 "⚠ 스코프 가드 — Idempotency storage 행: 사용자가 멱등성(Idempotency-Key)을 요청하지 않았으면 이 행을 silent하게 필수 서브시스템으로 빌드하지 않는다 … 미요청 멱등성을 명세에 silent 의무로 박는 건 스코프 초과다". Standard actively forbids, not permits.

[2a insufficient/silent? NO] The exact failure is named+prescribed in real lines: design-architect.md:36 (G1 surfacing), discipline-reviewer.md:39 (C-form anemia 직격: "도메인 규칙 메서드가 애초에 없는 경우 … blocker"), :41 (API 오류 중앙화: "일부 예외만 핸들러가 처리하고 나머지 status 선택이 operation·application에 남는 부분 중앙화는 면제가 아니라 blocker"), design-review-ddd.md:40 ("스코프 의문은 발견으로만 올린다"). Not silence — unlike the ACL-EX2 anchor (houserules §2 truly silent on infra-exception transient/permanent).

[2b reference wrong? NO] Surviving citations are CORRECT doctrine that does NOT break on execution: architecture-ddd/reference/final.md:648 "판정을 소유하면 그 코드는 도메인 컨텍스트가 되어 표준 구조로 이주한다"; architecture-db/reference/final.md:419 (=mirror :402) "stored result(= 도메인/응용 outcome; HTTP status·응답 표현은 presentation이 소유 … §13.3·P1a)"; implementation-django-ninja/reference/final.md:443 "오류는 operation에서 raise하고, problem+json 변환은 중앙 @api.exception_handler와 헬퍼 한 곳이 한다". Contrast the FC-1 anchor where ninja:146-171 literally teaches a bug — here nothing executes-and-breaks. So 2b out.

[3 drift? NO] Diffed the load-bearing lines ref↔mirror: ddd:648 byte-identical, db:419/:402 byte-identical, ninja §6.2:443 byte-identical (verified via diff). No lost doctrine.

[1 nondeterminism? YES — and not a cop-out] Correct + faithfully-mirrored guidance, yet Codex architect wobbles. check-idempotency-scope-creep.py:11-15 self-documents the exact category-1 signature: "미요청 멱등성 금지 가드는 이미 design-architect(§9.6)에 산문으로 있으나 … DR-27에서 architect가 'risky write라 권장'이라 합리화하며 번복했다(가이드 단독 = 재현율 약함, DR-21)." This is FC-2-anchor-homologous (prose present, no hard gate → LLM inconsistent), but STRONGER backstopability because a deterministic gate actually shipped.

[backstopable=yes — VERIFIED WIRED] commands/dddjango.md:86 enumerates ⑩ check-idempotency-scope-creep in the 16-gate runner; scope axis detected by clean AST/text AND-composition (scope.md "미요청 단정" ∧ application/<bc> idempotency artifact ∧ ¬G1 채택 → exit2). The status:int-flows-through-app semantic variant itself is non-text-deterministic (correctly noted) and is delegated to discipline-reviewer.md:39/:41 semantic lens. Sound.

CRITICAL DEFECT IN THE CLASSIFIER'S EVIDENCE (does not flip category, but must be fixed): referenceEvidence cites implementation-django-ninja final.md:531 ("도메인 outcome은 응용 계층이 저장하고 … application·domain은 status를 만들지 않는다") and :550 ("보관·재현의 계층 책임을 지킨다 … application·domain이 status를 catch·생성·저장하지 않는다") — these lines DO NOT EXIST. grep for that prose returns 0 hits in BOTH reference and mirror. Actual ninja :531 is the @api.exception_handler(HttpError) code block; actual :550 is _is_retryable_db_error(). The rationale's "ninja §13.3:531" is likewise phantom (ninja ref is 832 lines, mirror 822; §13.3 numbering is not present). These are hallucinated citations. The doctrine the classifier ATTRIBUTED to ninja:531/550 genuinely exists but at DIFFERENT locations: db ref:419 (presentation owns HTTP status) + ninja §6.2:443-470 (operation raises, central handler converts). Because those real, byte-identically-mirrored lines fully support the same conclusion, the category 1-nondeterminism verdict stands — but the supporting citation set must be repaired (substitute db:419 + ninja §6.2:443 for the non-existent ninja:531/550) before this classification is treated as evidence-backed.

#### anemic-sql-duplication — `None`  (upheld: True)

분류 유지: 1-nondeterminism, backstopable=yes (high). 4개 적대 점검 모두 분류를 지지.

(0 designer-decides? NO) 정본 architecture-ddd/reference/final.md:646 은 단정적 금지다 — "응용 서비스·리포지토리·인프라(SQL/ORM)는 그 판정을 대신 내리거나 복제하지 않는다 … 동시성 안전이 필요해도 판정을 SQL로 옮기지 말고, 인프라엔 경합 가드(낙관적 version/CAS)만". '둘 다 방어가능'/designer-decides 문구 없음. BC분해(0)와 명확히 구분.

(2b 정본 틀림? NO) 처방이 실행가능·정확하다 — 도메인 메서드가 판정 소유, 인프라는 version/CAS 가드만. FC-1과 달리 실행해도 happy path가 깨지지 않고, 3개 사이트에서 일관. 버그 레시피의 반대.

(2a 침묵? NO — 3곳에 명시) ① ddd §3.2 :646 ② db §9.5 architecture-db/reference/final.md:408 ("비즈니스 판정(예: stock>=qty)을 SQL WHERE나 ORM 호출로 옮기면 … 빈혈 … 인프라엔 경합 가드만 둔다 — 낙관적 version/CAS") ③ db §9.6 Rule ownership 행 :418 ("WHERE stock>=qty·ORM update()에 복제해 도메인 메서드를 죽이지 않는지"). ACL-EX2(2a 침묵)와 정반대.

(3 드리프트? NO — 미러 충실) ddd 미러 dddjango/skills/architecture-ddd/references/final.md:630 = 정본 :646 byte-identical. Claude reviewer dddjango/agents/discipline-reviewer.md:39 + Codex reviewer codex-dddjango/skills/dddjango-discipline-reviewer/SKILL.md:40 둘 다 "부재형(C형) 직격" 풀 점검 보유(check-anemic-sql-guard 명시·C형[domain_layer 메서드 0개=blocker] vs B형[메서드 존재=DRY·의미몫] 분리·이름위장/외부배치 변종은 사람에 위임). Codex coordinator SKILL.md:105 에 ⑪ 배선 확인. Codex architecture-ddd/SKILL.md(43줄 인덱스 포인터·빈혈 0매치)는 드리프트 아님 — 설계상 코퍼스-장 미러가 아닌 인덱스이고, Codex 집행경로(reviewer+백스톱)는 온전. 분류자가 이미 이를 명시 처리함(경로명 'dddjango-' 접두 없는 architecture-ddd/ 로 실측 정정).

(1 비결정? YES) 정본 3곳 정확 + 미러 2곳 충실인데도 LLM이 filter(stock__gte=quantity).update()로 판정을 SQL에 복제 = 1-nondeterminism 정의. 현행 런은 version CAS만이라 PASS, DR-32가 과거 3픽스처 B1 회귀 포착(런간 진동).

(backstopable=yes) dddjango/scripts/check-anemic-sql-guard.py(206줄) 도크스트링·로직 확인: G1(.filter/.exclude→.update 의 <col>__(gte|gt|lte|lt)=비리터럴, col∉{version,id,pk}) ∧ G2(git 신규/수정·brownfield 스킵) ∧ G3(BC domain_layer 규칙 메서드 0개) → exit2. B형·CHECK Q(...)·version 가드·__gte=0 리터럴 다 통과(FP≈0). recall 갭(도메인 메서드 domain_layer 밖·이름위장)은 reviewer 위임. FC-2(backstopable=partial)와 동류이되 지배 변종 C형엔 하드 결정게이트 존재 → yes.

처방=수용+계측(배선완료). 신규 저술/정정/재동기 불요.

#### anemic-dead-domain — `1-nondeterminism`  (upheld: True)

분류 유지 = 1-nondeterminism (high confidence). 적대적 재검증으로 4개 결정-트리 분기 전부 반증 시도했고 모두 1을 가리킨다.

[2b 배제 — 정본이 틀린 게 아니라 올바름] workspace/reference/architecture-ddd/reference/final.md:646 이 이 문제의 '죽은 메서드' 변종을 직접 호명: "응용 서비스는 *조회 → 도메인 기능 실행 → 영속화* 순서로 그것을 프로덕션 쓰기 경로에서 **실제로 호출**한다 … 판정을 인프라로 옮기면 같은 판정의 도메인 메서드가 호출되지 않는 죽은 코드가 되어 위 빈혈 모델로 회귀한다." 처방대로 실행하면 풍부한 도메인 모델이 되어 *깨지지 않는다*(FC-1식 버그 예시 아님). 동시성 대안(인프라엔 version/CAS만, 도메인 메서드부터 재실행)도 올바름.

[2a 배제 — 가장 위험한 함정, 가장 강하게 시험함] 정본이 단순 aspirational 산문이 아니라 *실행 가능한 구체 레시피*를 준다: §3.6(final.md:1010-1019)이 "비즈니스 로직을 직접 구현하지 않으며 도메인 객체에 위임"/"도메인 로직을 직접 구현하면 안 된다"를 못박고, :1082-1087 의 `cancel_order` 예시가 *조회→`order.cancel()`(주석 "도메인 로직은 Order 애그리거트에 위임")→끝*을 복사 가능한 코드로 시연한다. '어떻게 호출하나'까지 operational 하게 명시 → 침묵·모호 아님.

[3 배제 — 드리프트 없음] md5 검증: 정본 :646, Claude 미러 dddjango/skills/architecture-ddd/references/final.md:630, Codex 미러 codex-dddjango/skills/architecture-ddd/references/final.md:630 셋 다 c36ffc94d36b6c238c6118e38429d7ff 로 byte-identical (:648/:632 도 bc2a70a4 일치). *양 런타임* 미러 모두 충실 → 역사적 '양 런타임 비결정'을 미러 갭으로 돌릴 수 없음.

[0 배제] 정본이 빈혈을 "안티패턴"(:599)·"회귀"(:646)로 금지 — designer-decides 아님.

[1 확정] 정본·양 미러 모두 올바르고 충분하며, discipline-reviewer.md:39 가 죽은-메서드(B형)·부재(C형) 두 변종을 명시 소유("테스트만 부르면 죽은 코드 … 부재형(C형) 직격")하는데도, 역사(DR-13/14/15 B1 도메인소유 '양 런타임 비결정', 현행 런은 deduct_stock 프로덕션 호출로 PASS)가 LLM 이 충분한 지침에도 런마다 도메인 소유·호출을 다르게 실현함을 보인다. 보정 앵커 FC-2(권장하나 hard 게이트 없음·LLM 비일관·backstopable=부분)와 동형·일관.

[backstopable=partial 확인] check-anemic-sql-guard.py 가 C형(도메인 규칙 메서드 0개 + 판정 SQL만)을 좁고 결정적으로 차단(line 29-30·111-127, 거짓양성≈0)하나, B형(메서드 존재+응용이 .update() 우회)은 line 178 에서 명시 면제("G3 면제: 도메인 규칙 메서드 존재 = B형(복제, reviewer 위임)"), recall 갭(도메인 메서드를 domain_layer 밖)은 docstring line 18 이 reviewer 에 위임 자인. 죽은-메서드 변종·위장 거주는 호출그래프 도달성+판정 의미 식별이 필요해 깨끗한 AST/텍스트 신호 부재 → 의미층, 신규 백스톱 신설 금지. remedy = 수용 + 기배선된 C형 백스톱 유지 + RUBRIC SD-1/SD-2 라이브 계측.

#### cross-bc-orm-fk — `None`  (upheld: True)

분류 1-nondeterminism 유지(confidence high). 네 점검을 정본/미러 file:line 직접 재확인으로 적대 검증했고 모두 분류를 지지한다.

(0 by-design 배제) architecture-ddd/reference/final.md:666 '규칙 3' 헤딩 + :670이 cross-BC ORM FK를 *경성 금지*로 규정('BC 경계를 넘는 ORM 관계 ForeignKey·OneToOneField·ManyToManyField를 두지 않는다' + 세 경계[애그리거트 내부=자유/같은 BC=허용/다른 BC=금지] + 왜[Vernon Reference-by-Identity·Fowler Bounded Context·모듈러모놀리스]). designer-decides 토글 아님. 카드의 'nj2 FK underdetermined' 헤지는 규칙4 직교분해라는 별개의 더 좁은 질문이지 FK 금지 자체가 아님.

(2b 정본-틀림 배제) :670은 실행되는 코드 예시가 아니라 *금지 산문*이라 'happy path가 깨지는 버그 레시피'가 원천적으로 없다(FC-1의 OrderOut.status:str↔ProblemOut.status:int 500과 대조). 예시 코드 :692·:746은 `product_id: str`=올바른 ID참조 패턴. 유일하게 오해유발 소지인 OrderItem FK 예시는 implementation-django/reference/final.md:1711이 '`product`가 다른 BC면 `ForeignKey(Product)` 대신 `product_id` 값참조'로 *명시 교정*. 정본 틀리지 않음.

(2a 정본-부족 배제) 침묵의 정반대 — 번호붙은 규칙 헤딩(:666 규칙3/:672 규칙4)에 필드 3종 실명·세 경계·근거·예외(AUTH_USER_MODEL)까지 명기, :678이 '한 트랜잭션→FK OK' 함정을 직교성 가드로 봉합. 다른 섹션에 흩어진 게 아니라 규칙3 본문에 집중.

(3 드리프트 배제) diff 결과: 정본:670 ↔ Claude미러 :654, 정본:678 ↔ Claude미러 :662, houserules 정본:134 ↔ 미러:134 모두 byte-identical(RULE3/RULE4/HR IDENTICAL). Codex 미러 :654/:662도 동일 문자열. 에이전트 집행 충실: design-architect.md:38('타 BC 참조는 ID값+ACL/OHS로 명세, BC 경계 ORM FK를 결과 제약으로 금지 — 안 박으면 코더가 참조 무결성 명분으로 cross-BC FK 삽입'), discipline-reviewer.md:46(레드플래그 '타 BC 모델을 ORM ForeignKey/OneToOneField/ManyToManyField로 참조'…ID값참조+ACL/OHS 존재검증으로 반송, 같은 BC FK는 정상). DR-37 '16미러' 일관 존재(DEVLOG:95 corroborate).

(1 비결정 확정·오판 아님) 정본·미러가 모호/부족한데 LLM탓 돌린 게 아닌지가 가장 위험한 점검인데, 여기 정본은 단순 존재를 넘어 *전수적·선제 방어적*이다(규칙3 ORM 확장+세 경계+필드 실명+:678 트랜잭션 함정 봉합+impl-django:1711 오해예시 교정+architect/reviewer 양 집행). 코더가 정직하게 모호성 주장 불가. 그런데 카드가 '현행 런은 product_id:int ID참조로 PASS' vs DR-36 부수는 'Claude OrderModel→catalog ORM FK 그음' = 같은 프롬프트 런간 정반대(P4③) = 비결정 서명. 부족이 아니라 흔들림.

(보정앵커 일관) FC-1=2b·ACL-EX2=2a는 정본에 오류/침묵이 있었으나 여기는 정본 정확+미러 byte-identical 충실이라 그 둘이 구조적으로 불가능; FC-2=1(부분 backstopable)과 동형(올바르나 hard 게이트 없는 지침+런간 변동).

(backstopable partial 검증) 신호는 원리상 깨끗한 AST(relational field 타깃 app_label ≠ 자기 BC)이나, check-*.py 16종 중 cross-BC FK 전용 백스톱 부재 — check-context-isolation.py는 line49 정규식 `^\s*(?:from|import)\s+application\.<bc>\.(domain_layer|infra_layer)`로 *import 결합만* 봄(reviewer.md:46 명시), FK-via-field 타깃 미커버. DR-37 백스톱 보류(BC 멤버십 판별 위양성[app_label≠디렉토리명]·N=1)는 정당. 정본/미러 변경 불요(이미 정확·충실).

#### vacuous-concurrency-test — `1-nondeterminism`  (upheld: True)

UPHELD (high confidence, backstopable=partial). Every cited file:line re-verified independently; all four adversarial probes came back negative for misclassification.

[2b ruled out — the dangerous one] The §20.5 recipe is NOT a buggy prescription. canonical implementation-test/reference/final.md:2612-2658 gives a deterministic single-thread CAS-spy (ConflictOnceRepository.save_with_version_guard bumps version once → CAS 0 rows → retry) whose assertion `assert product.stock == 3` (from stock=5, qty=2) is an EXACT post-condition, not tautological, and executes without flakiness. The standard teaches the CORRECT pattern — so the producer's vacuous test is misuse of good guidance, not a standard fault. Contrast FC-1 anchor (=2b) where the standard literally teaches a happy-path-500 bug. Not the same.

[2a ruled out] Not silence. The exact failure mode is named in ≥3 places: §20.5 (deterministic spy as the answer, §20.4 race self-flagged "SQLite 비결정적·flaky" at :2618/:2624 — matching the symptom's Barrier-race-scheduler-dependency verbatim), §17.4/17.5 weak-vs-strong / Survived mutant (`>→>=`) at :2240-2282, and discipline-tdd reference/final.md:31 "보안과 동시성은 TDD만으로 부족."

[3 ruled out] No drift. §20.5 mirror dddjango/skills/implementation-test/references/final.md:2612-2648 is byte-identical (same line numbers, same ConflictOnceRepository). Reviewer "행사 위장 경계" bullet at discipline-reviewer.md:36 names BOTH symptoms literally — 순차 vacuous (`save_with_cas`→True still green) AND 항진 단언 `(n-remaining)<=n` as important — and the Codex mirror dddjango-discipline-reviewer/SKILL.md:37 is identical. Nothing lost.

[1 confirmed] canonical + mirror + agent all teach this anti-pattern down to the two precise symptoms, yet producer writes the vacuous test → LLM wobbles despite sufficient instruction = 1-nondeterminism. Consistent with anchor FC-2 (=1, backstopable=partial), which is structurally identical.

[backstopable=partial, confirmed] All 16 check-*.py enumerated; grep for oversell/sequential/tautology/vacuous/save_with_cas/concurrency = 0 hits — no targeted gate exists, and no AST gate inspects `assert (left)<=(right)`. Reviewer marks it important (WEAK ceiling), not blocker, so no hard gate. True discriminator is mutation survival (patch save_with_cas→always-True and see if the test dies) — inherently dynamic/semantic; only the tautology assertion is narrowly AST-capturable. Reviewer also explicitly protects the valid case ("재고 판정의 *순차* 검증과 구분"), so a deterministic gate carries real false-positive risk → partial.

[remedy measurement channel verified] Q-3 is a genuine rubric dimension (RUBRIC.md:103, rubric-metrix.md:76: "선언 동시성 기준이 실제 테스트로 실현·결정적 CAS 스파이", detection "grep+의미") actively scored in live results (ptbootlive, ptcat). The accept+measure-via-reviewer-important+EVAL-Q-3 stance is grounded; a new hard backstop should wait for live N≥2 recurrence of the tautology-assertion variant only.

#### misattributed-constraint-test — `None`  (upheld: True)

분류 유지: 1-nondeterminism, backstopable=no. 네 카테고리를 적대적으로 반증 시도했으나 모두 기각됨, 보정 앵커 FC-2=1과 완전 정합.

(2b 반증 — 정본이 틀렸나?) 아니다. workspace/reference/implementation-test/reference/final.md:2105 "The Liar 변종 — 산출물 오귀속" 문단은 FC-1 앵커식 '실행하면 깨지는 예시'가 아니라 올바른 진단+처방이다. 교차참조 architecture-db §9.5(workspace/reference/architecture-db/reference/final.md:404)를 직접 확인 — 거기서 실제로 "불변식 CHECK 백스톱(예: stock>=0)"을 권장하므로 "다층 방어 병행 정상"은 자기모순이 아님. 정본은 내적으로 정합하고 옳음.

(2a 반증 — 부족/침묵인가? 가장 강한 반대가설, 최우선 검증) 아니다. 문단이 증상(명명 CheckConstraint(stock>=0)를 약화해도 PositiveIntegerField가 IntegrityError를 내 통과), 원인(술어 동치 암묵 가드가 먼저 통과해 구별 증명 실패), 처방(동치면 docstring 명시·strictly stronger[상한·복합·>=N]면 구별 단언)을 모두 명시. DR-45 #4 증상(명명 제약 stock>=-999999 약화해도 green·삭제해도 false green)은 이 문단이 적은 stock>=0 사례의 *직접 인스턴스*다. 지식 수준에서 충분 → 2a 아님.

(3 반증 — 드리프트인가?) 아니다. diff로 byte-identity 직접 검증: 정본:2105 ↔ Claude 미러 dddjango/skills/implementation-test/references/final.md:2095 ↔ Codex 미러 codex-dddjango/skills/implementation-test/references/final.md:2095 모두 IDENTICAL, §16 섹션 전체도 IDENTICAL(offset 제외).

(1 정당성 — 고칠 수 있는 걸 포기한 오판 아닌가? 가장 위험한 오류) 생산자측 지침이 구체적·완비된 상태에서 LLM이 IntegrityError를 발화시킨 가드를 오귀속(명명 제약으로 단언하나 실제로는 암묵 필드 CHECK가 먼저 발화)하는 의미·판단 슬립 = 카테고리 1의 정의. backstopable=no 확정: 16개 check-*.py 전수 grep 결과 IntegrityError/constraint 문자열은 check-synthetic-infra-exc.py·check-transient-overmapping.py 두 곳뿐이며 둘 다 ACL-EX2(인프라예외 합성/과잉매핑) 탐지로 *이 오귀속과 무관*. "어느 CHECK 가드가 IntegrityError를 발화하는가"는 런타임·의미 판별(mutation testing 본질)이라 정적 AST 불가.

(분류자 정밀도 보정 2건, 판정 불변) ① rationale의 "grep 0"은 문자 그대로는 부정확 — IntegrityError/constraint 문자열이 2개 스크립트에 존재. 그러나 그것들은 *다른* 현상(인프라예외 합성)을 잡으므로 작동 주장("이 오귀속을 잡는 백스톱 없음")은 유효. ② remedy의 측정-갭 진단은 정확하고 증거가 더 강함: FC-GOLDEN.md:35가 명시적으로 "DB CHECK constraint(stock__gte=0)는 도메인 판정 아니므로 mutation 대상 제외", RUBRIC.md:74 FC-2 mutation 항목도 부호/경계/status만 다룸 → 명명 제약이 mutation 측정에서 빠지는 것이 이 false-green 잔존의 직접 원인이라는 처방 비판이 정확. 처방 방향(수용+계측 강화·생산자측 salience·신규 백스톱 보류)은 의미층·N=1·위양성 위험에 비추어 DR-35/DR-38식 '반복 확인된 결정적 신호만' 원칙과 일관하여 타당.

부수 관측(처방 보강 근거): 이 오귀속 문단은 workspace/reference/ 전체에서 implementation-test 단일 출처에만 존재(discipline-tdd 정본·acceptance-tester.md 36줄 모두 mutation/오귀속/constraint 언급 0). 스킬 본문이 정본을 충실 미러하므로 드리프트(3)는 아니나, 에이전트 지침 미반영은 remedy (b) salience 보강의 타당한 표적.

#### migration-0001-rewrite — `1-nondeterminism`  (upheld: True)

분류 유지: 1-nondeterminism (확신 high). 적대적 반증 시도가 모두 실패했다.

결정트리 재순회 (각 분기 file:line 직접 재확인):

(0 by-design?) 아님. 정본은 양면적("둘 다 방어가능")이 아니라 일방·처방적이다. workspace/reference/implementation-django/reference/final.md:1003 "기존 0001_initial 은 불변(재작성·삭제 금지)", :1031-1032 "MIGRATION_MODULES로 옛 루트 <app>.migrations를 가리키는 잔존 핀도 두지 않는다(새 경로 단일 소유)" — 증상의 두 변종(0001 재작성, migrations-only 핀)을 모두 명시적으로 금지. designer-decides 없음.

(2b 정본 틀림?) 아님 — 이 점이 FC-1과 갈리는 핵심. FC-1은 정본 예시 자체가 실행하면 500을 낸다(표준이 버그를 가르침). 그러나 여기 §10.4(:976-1035)는 정확한 실패모드를 명시("코더가 기존 0001을 *재작성*(fresh initial)하기 쉽다", :984)하고 정확한 올바른 메커니즘(SeparateDatabaseAndState state-only 0002, :1013-1019, database_operations=[] :1018, AlterModelTable로 db_table 보존 :1006-1007)을 제시 — 이것이 *현행 런이 PASS하는 바로 그 메커니즘*이다. 검증 절차까지 정확(:1027-1029 makemigrations --check + sqlmigrate로 DDL 미발행 확인). 정본 처방을 실행하면 깨지는 게 아니라 통과한다. → 2b 배제.

(2a 부족?) 아님. §10.4가 이 시나리오를 직접·전용으로 다룬다(:976 "10.4 이미 이주가 결정된 뒤의 마이그레이션 이력 보존"). 원 문제의 relevantSkill이 architecture-db(§11)를 먼저 들지만, architecture-db는 *올바르게 핸드오프*한다: workspace/reference/architecture-db/reference/final.md:525 "migration file 구현법이 아니라... migration class 작성은 implementation-django로 넘긴다", :9 "Do not use for... Django ORM code mechanics... hand off". 즉 HOW의 소유자는 implementation-django §10.4이고 거기 상세·실행가능하게 존재. 침묵이 아니라 올바른 경계 위임 — 못 찾은 게 아니라 다른(올바른) 스킬에 있음. → 2a 배제(원 문제의 스킬 오귀속이 갭을 만들지 않음).

(3 드리프트?) 아님. 양 미러 충실: Claude dddjango/skills/implementation-django/references/final.md:974-1002, Codex codex-dddjango/skills/implementation-django/references/final.md:974-1002 — grep로 SeparateDatabaseAndState/재작성·삭제 금지/database_operations=[]/MIGRATION_MODULES 모두 동일 라인 일치 확인. 에이전트도 강화 반영: dddjango/agents/design-architect.md:40 "기존 label 유지·기존 db_table 명시 보존·기존 0001 불변(클래스 rename은 state-only 0002로)" + "이력 보존 *메커니즘*은 implementation-django §10.4가 소유", dddjango/agents/design-review-db.md:31 "기존 db_table·label·0001 보존(클래스 rename은 state-only)이 명세에 박혔는지 확인... 누락이면 brownfield DB 위험이므로 blocker". → 3 배제.

(1 비결정?) 성립. 정본·양미러·두 에이전트(architect 처방 + db reviewer blocker)가 모두 불변-0001/state-only-0002를 올바르게 처방하는데도 한 Claude 런이 0001을 재작성(FAIL, whereObserved: django_catalog/migrations/0001_initial.py:14-25)했고 현행 런은 state-only로 준수(PASS). 모호/부족을 LLM탓으로 돌린 게 아니라(2b/2a/3 모두 적극 반증됨) 충분한 지침에도 흔들린 것 = 1-nondeterminism. 보정 앵커 FC-2(category 1, backstopable 부분)와 일관.

backstopable=yes (FC-2 동형, 부분→가능): 신호가 깨끗한 AST/구조 — git-touched migrations/0001_initial.py 존재 + ORM 클래스 rename된 기존 앱(Meta db_table 명시)인데 state-only SeparateDatabaseAndState(... database_operations=[]) 0002 부재 → exit 2. SH-4 변종(MIGRATION_MODULES 핀으로 옛 루트 <app>/migrations 지목, reference:1031-1032 금지)도 동시 탐지. 현재 결정적 백스톱이 이를 의도적으로 다루지 않음이 명시됨: dddjango/scripts/check-app-container.py:213 "이 스크립트는 그중 *위치* 한 축만 본다. 기존 0001 보존은 implementation-django §10.4(label/db_table 유지·state-only...)" — 진짜 미커버 갭이라 결정적 체크로 닫을 수 있다. 도입 전까지 design-review-db.md:31 blocker가 catch.

처방: 수용 + 계측 후 결정적 백스톱 추가. 정본·미러는 올바르고 충실하므로 텍스트 수정 불필요(신규 저술 2a·정정 2b·재동기 3 모두 해당 없음). 분석 전용 워크플로 준수 — Read/Grep/Bash diff만 사용, 어떤 파일도 수정하지 않음.

#### mechanism-ownership — `1-nondeterminism`  (upheld: True)

분류 UPHELD: 1-nondeterminism (high confidence). 4개 대안을 적대적으로 반증했고 모두 기각됨. 단 backstopable 필드는 "yes(완전)"가 아니라 "partial(부분)"로 정정해야 함(아래).

[0-by-design 기각] 정본이 이 변동을 의도적으로 허용하지 않고 명시 금지함: architecture-db 정본 /Users/hyun/Desktop/dddjango/workspace/reference/architecture-db/reference/final.md:406 "구현이 환경 한계(sqlite 락)를 이유로 자기 판단으로 만들지 않는다 ... *출처-불문*"; implementation-django 정본 /Users/hyun/Desktop/dddjango/workspace/reference/implementation-django/reference/final.md:1558 "이 금지는 출처-불문이다". designer-decides 아님(§632 BC분해와 대조).

[2b-reference-wrong 기각] 정본은 틀리지 않고 실행 가능한 올바른 처방을 제시: architecture-db 정본:404·:408이 version/CAS 조건부 원자 UPDATE(WHERE엔 version 경합 가드만, 비즈니스 판정 제외)를 처방. FC-1 앵커(정본이 happy-path 500 버그를 *가르침*)와 달리, 이 처방을 따르면 깨지지 않고 동시성 안전 코드가 나옴. LLM 오용(=1)이지 정본 오류 아님.

[2a-reference-insufficient 기각] 침묵이 아니라 코퍼스에서 가장 전수적으로 명세된 규칙 중 하나. 정본 두 곳이 금지 형태를 출처-불문으로 열거(DatabaseWrapper 상속·런타임 몽키패치·connection_created·init_command BEGIN/PRAGMA 주입·isolation_level 조작·DB 미들웨어·conftest 패치)+허용 화이트리스트(stock OPTIONS: transaction_mode/timeout+안전 PRAGMA foreign_keys·busy_timeout·synchronous·cache_size). ACL-EX2 앵커(houserules §2:144가 포트 도메인 예외에만 앵커·인프라예외 침묵)와 달리 빈틈 없음.

[3-skill-drift 기각] 정본 vs 미러 직접 diff 결과 유일한 차이는 P1 Source Sufficiency 메타데이터 헤더(정본에만 존재, 미러는 corpus_mirror_sync가 제거)뿐. load-bearing 두 문장은 byte-identical: architecture-db 정본:406 == 미러 /Users/hyun/Desktop/dddjango/dddjango/skills/architecture-db/references/final.md:389; implementation-django 정본:1558 == 미러 /Users/hyun/Desktop/dddjango/dddjango/skills/implementation-django/references/final.md:1529. 분류자가 인용한 라인번호 오프셋(406 vs 389, 1558 vs 1529)은 헤더 줄수로 완전히 설명됨. Codex 포트도 동일 지침 보유(codex-dddjango/skills/{architecture-db,implementation-django}/references/final.md). 미러 충실—드리프트 없음.

[1-nondeterminism 확정] 4계층 모두 올바른 지침 정합: 정본(위), 미러(위), coder.md:50("기술 메커니즘은 architect 설계 결정·출처-불문·환경상 부족해 보이면 설계로 반송"), discipline-reviewer.md:40(메커니즘-소유권 blocker: DatabaseWrapper 상속·isolation_level·init_command 등 출처-불문 동일위반·허용=stock OPTIONS)·:55(소유권 vs 정확성 구분). 그런데도 coder가 config/db_backends/sqlite3_immediate/base.py 자작(DR-06 33분 토끼굴, DEVLOG §3 DO-NOT-RETRY #2 "코더가 architect의 기술 메커니즘 대체"). 충분·올바른·충실한 지침에도 LLM이 흔들린 비결정의 교과서적 사례. 모호/부족을 LLM탓으로 돌린 오판 아님—정본이 실제로 전수적으로 올바름을 file:line으로 확인.

[backstopable 정정: yes→partial] 분류자는 "yes(완전 backstopable)"라 했으나 백스톱 소스가 이를 반증. /Users/hyun/Desktop/dddjango/dddjango/scripts/check-mechanism-ownership.py:4-9 docstring이 스스로 "좁은 **고정밀·저-recall** 게이트"라 선언하고, smoke2에서 실제 난 커스텀-DatabaseWrapper 형태 *하나만* 차단하며 "런타임 몽키패치·시그널 같은 *의미적* 회피는 **일부러 잡지 않는다** — 그건 ② 표준 텍스트와 ③ discipline-reviewer 의미 체크가 담당"이라 명시. 발화엔 4조건 AND 필요(비-stock ENGINE+레포-로컬 백엔드 파일+DatabaseWrapper 서브클래스+의미마커[_start_transaction_under_autocommit/BEGIN IMMEDIATE/BEGIN EXCLUSIVE/isolation_level]+이번 변경 신규/수정, :32-43,:110-138). 즉 *출처-불문* 위반 클래스 중 지배적 단일 형태(DR-06이 친 것)만 결정적으로 잡히고, 의미동등 변종의 긴 꼬리는 reviewer 의미층이 보완. FC-2 앵커의 "backstopable=부분"과 동형이지 깨끗한 단일 AST 신호로 *완전* 커버되는 게 아님. 백스톱은 commands/dddjango.md:86 게이트 ①로 배선 확인됨(16종, exit2 시 설계 반송).

[remedy] 1-nondeterminism·backstopable=partial의 처방은 이미 4계층 집행 완료(현행 런 PASS, DEVLOG §3): 결정적 백스톱(고정밀, 단일 지배 형태 차단)+reviewer 의미 blocker(출처-불문 꼬리 커버)+coder 예방+표준 텍스트. 신규 저술·정정·재동기 불필요(정본·미러·Codex·백스톱·reviewer 정합). 잔여 비결정=백스톱이 의도적으로 안 잡는 의미적 변종뿐이며 reviewer 의미층이 보완하나, 이는 LLM 의존이라 N=1 미검증 시 완전 차단 보장 못 함—category 1의 본질적 잔여 위험.

#### fixture-contamination-q6 — `2a-reference-insufficient`  (upheld: True)

분류 유지(2a-reference-insufficient, confidence medium). 적대적 재검증에서 5개 가지를 모두 file:line으로 반증 시도했고 분류가 견뎠다.

[1-비결정 아님 — 결정적 반증, 가장 위험한 오판부터 검증] 분류의 핵심 주장(LLM 산출물은 흔들리지 않았다)을 ptbootlive 깨끗 baseline 양 파일에서 직접 확인. workspace/eval/results/20260609-1523-ptbootlive-codex.md:28-32 = Codex가 깨끗 venv에서 pytest·pytest-django·pytest-mock·factory_boy 설치+`requirements.txt:4-7` 4종 전부 핀+pyproject.toml 설정 완비, :32가 명시적으로 "ptcat 핀 0(오염)·Q-7 WEAK는 fixture 오염(조정자 pytest 선설치) 산물이었고 깨끗 baseline에선 완전 이행". 20260609-1539-ptbootlive-claude.md:28-30 = Claude도 (설치 Y)×(핀 Y), requirements-dev.txt로 dev 분리까지. **양 런타임 모두 Tier-1 설치+핀 완전 이행** → 모델은 안 흔들렸다. 흔들린 주체 = 인간 조정자 채점 과정(env 오염+Q-6 오기), ptcat-codex.md:5·:119가 자기 오염을 자인. 따라서 1 아님.

[2b 아님] coder.md:34 "§2.1 버전-핀 규율로 매니페스트에 핀"이 *실행하면 깨지는가*? ptbootlive가 양 런타임 작동 산출물 입증 → 정본 처방은 올바르고 실행됨. 깨진 예시·잘못된 처방 없음. ninja §2.1 핀 소유 = corpus final.md:98 확인.

[3 아님 — 드리프트 양쪽 인용] corpus implementation-test final.md:564 ↔ mirror final.md:554 = 동일 문장("테스트 스택 동반 패키지... §2.1 버전-핀 규율... 실제 설치 버전을 매니페스트에 핀"), 줄번호 차이는 선행 콘텐츠 오프셋일 뿐 byte-identical. 게다가 코더 표준 본체는 agents/coder.md:34·acceptance-tester.md:30·commands/dddjango.md:80에 *직접* 저술(미러-동기 아님)되어 전부 올바름. 드리프트 경로 해당 없음.

[0 아님] designer-decides/둘 다 방어가능 프레이밍 부재.

[2a 매핑 — 카테고리 경계 stress 인정하되 앵커-일관] 결함이 봉합된 위치 = EVAL-METHOD.md:85-96 §1.1.T로, "2026-06-09 신설"·자기출처 명시("ptcat 사건 교훈: 조정자가 fixture venv에 pytest 선설치하면…")·이전 방법론 reference는 env 위생/3축(env≠produced≠used) 분리에 *침묵* → 신규 저술로 빈칸을 메움. 구조적으로 ACL-EX2 앵커(2a=reference 침묵→신규 저술)와 동형. 정직한 균열: 이 흠은 *생성코드 표준*이 아니라 *측정 장치/채점 방법*에 있어 결정트리(reference final.md+미러 축) 경계를 늘리지만, 트리 자체 논리("침묵 reference→신규 저술")에 2a로 깨끗이 매핑되고 confidence=medium이 이 긴장을 정확히 포착.

backstopable=no 유지: 코더 표준은 이미 완전하고 LLM 준수가 ptbootlive로 입증되어 코드-탐지 백스톱 불요. 측정-과정 규율(환경 무통제·채점 오기)은 결정적 AST/텍스트 신호 대상이 아닌 사람-과정 게이트.

#### Q6-test-runner-fallback — `1-nondeterminism`  (upheld: True)

UPHELD: 1-nondeterminism (high). All cited file:line re-confirmed verbatim, and the strongest competing category (2a) tested and rejected.

CONFIRMED CITATIONS:
- Hard mandate present in operational mirrors (the agent actually loads these), all explicit/non-optional: dddjango/commands/dddjango.md:80 "러너는 **항상 pytest다(예외 없음)**...새로 쓰는 테스트는 무조건 pytest 관용구"; dddjango/agents/coder.md:34 "단위 테스트는 **무조건 pytest로**...새 테스트는 pytest로(예외 없음)"; dddjango/agents/acceptance-tester.md:30 "인수 테스트는 **무조건 pytest 관용구**...예외 없다".
- Drift=0: codex-dddjango/skills/dddjango/SKILL.md:99 is byte-identical to dddjango.md:80.
- FAIL codified: workspace/eval/rubric/RUBRIC.md:106 Q-6 lists "raw `unittest.mock`·Django `TestCase` 폴백(greenfield)" as the explicit FAIL signal.
- Backstop blind-spot confirmed verbatim: dddjango/scripts/check-test-config.py:277-278 `if not configs: return 0  # pytest 설정 없음(manage.py test 관례 존중)` — deliberately exits 0 on no-pytest-config, so the fallback never fires a gate. No other check-*.py fires on TestCase/unittest fallback (grep: only check-test-config.py and check-layer-skeleton.py even mention TestCase, neither as a fallback blocker).

ADVERSARIAL PROBE → 2a REJECTED (this was the real risk): the knowledge corpus workspace/reference/implementation-test/reference/final.md only marks pytest ":174 **pytest 스타일 (권장)**" (recommended) and at :153 shows "**xUnit 스타일 (unittest)**" with TestCase as a legit style — so a literalist could claim Codex picking TestCase merely follows the corpus (=2a silence). Rejected because: decision-tree question-1 ("정본에 올바른 지침이 있나") is satisfied by the OPERATING source-of-truth the agent loads — agents/*.md + commands/dddjango.md carry an EXPLICIT HARD mandate ("예외 없음") in three places, byte-mirrored into Codex, with RUBRIC Q-6 codifying the exact FAIL. That is not silence; the rule is present, correct, faithfully mirrored, and following it yields a clean pytest suite. The final.md "권장" wording is at most a mild corpus-vs-mirror salience gap, not absence of correct guidance. Codex defies a hard rule it provably holds.

2b REJECTED: reference pytest-django config final.md:344-355 (DJANGO_SETTINGS_MODULE) is runnable/correct — no executes-and-breaks example.
3 (drift) REJECTED: Codex SKILL.md:99 byte-identical; coder/acceptance-tester carry it too — nothing lost in mirroring.

HOMOLOGY with anchor FC-2 (=1): strong text mandate + NO hard gate firing on the fallback + Codex N=2 inconsistent (DR-42 C3 · DR-45 Q-6 MISS · duplive-codex manage.py test) = same shape as FC-2 (tdd recommends, no hard gate, LLM inconsistent, backstopable partial).

backstopable=yes-narrow: clean import/AST signal (greenfield touched-gate ∧ new test imports django.test.TestCase/unittest.mock ∧ repo has zero pytest config/conftest django setup → blocker), but FP surface = brownfield "기존 TestCase 관례 존중" (coder.md:34) so needs a greenfield-vs-brownfield gate (hence narrow; live N≥2 then precise gate per DR-35/37). Keep check-test-config.py's no-config exemption (orthogonal: it watches "broke a config it added"); new guard watches orthogonal "greenfield yet skipped pytest entirely." Remedy = enforcement mechanism only; text already sufficient, no corpus authoring/correction/resync needed.

NUANCE (not a category change): reference final.md "권장" is softer than operational "예외 없음" — a minor corpus salience inconsistency worth tightening, but it does not move the category to 2a since the binding correct rule lives faithfully in the operational layer.

#### G0-plain-recommendation — `None`  (upheld: True)

UPHELD as 1-nondeterminism (backstopable=no). All four load-bearing citations and the timeline re-verified directly.

(0 by-design) Ruled out: plain Django recommendation violates DR-16 (API stack = architect 1st-class decision, default Ninja); standard does not say "both defensible".

(2a/2b reference) Ruled out at corpus level. workspace/reference/ has 12 entries (the known skills + spec.md) and NO command/coordinator skill dir; grep of framework-decision text ("기본은 Django Ninja", "어느 API 프레임워크", "G0 결정 축", "plain으로 낮추", "결정 축이 아니다") over the entire reference corpus = 0 hits. The governing reference for coordinator behavior is the orchestrator/agent artifacts, not the corpus — so there is no corpus text to be silent (2a) or wrong (2b) about.

(3 drift) Ruled out. The CORRECT negative boundary is present and byte-identical across runtimes: Claude dddjango/commands/dddjango.md:65 and Codex codex-dddjango/skills/dddjango/SKILL.md:84 both md5=3194a6157124b0b3e280640ffdaf14ae ("어느 API 프레임워크로 구현하나는 G0 결정 축이 아니다 ... 특정 스택을 추천하지 않는다 ... 스택 판정은 design-architect 소유다 ... 없으면 기본 Django Ninja"). Downstream owner default also present both runtimes: design-architect.md:35 / dddjango-design-architect/SKILL.md:35 ("기본은 Django Ninja ... 의존성이 requirements에 없다는 사실만으로 plain으로 낮추지 않는다").

(timeline 2a->1) git log -S confirms the framework negative-boundary was ADDED by commit 2bdf006 (DR-31). At the DR-16 observation moment the G0 section was genuinely silent on framework (a 2a signature), but DR-31 already filled that silence correctly. The classification concerns the CURRENT state: correct guidance present, no drift, leaving only the LLM coordinator's residual freedom to drift even past an explicit boundary = 1-nondeterminism. This is the precise transition the decision tree handles, and it correctly resists the most-dangerous misfile (calling a fixable 2a "nondeterminism") because the silence was real but is already authored away — nothing left to write or fix.

(backstopable=no) Confirmed. 16 check-*.py scripts; the only one matching a G0/coordinator/framework grep is check-idempotency-scope-creep.py, which is a FALSE POSITIVE — its "G0" means "G0=확장금지" (no-scope-expansion idempotency rule) and it inspects disk artifacts (application/<bc>/ code, scope.md, design-spec.md), never the runtime-framework choice or G0 banner conversation. The string 'plain' in scripts (check-error-centralization.py:11, check-response-schema-bypass.py:16,23) appears only as EXEMPTION rationale in code-level checks, not conversation checks. The symptom (framework over-ask + plain recommendation) fires in the G0 approval banner before any .py/scope.md is written, so there is zero disk surface for a deterministic signal — structurally identical to the ACL-EX2 accept-and-measure anchor and consistent with the FC-2 anchor (guidance exists, no hard gate, LLM-inconsistent).

Remedy stands: accept + measure; no new backstop; prescription already enforced (DR-31 2-mirror byte-identical negative boundary + downstream default-Ninja both runtimes); next lever is live N>=2 accumulation (live N=1 via DR-34 framework-not-raised). Evidence files (absolute): /Users/hyun/Desktop/dddjango/dddjango/commands/dddjango.md:65, /Users/hyun/Desktop/dddjango/codex-dddjango/skills/dddjango/SKILL.md:84, /Users/hyun/Desktop/dddjango/dddjango/agents/design-architect.md:35, /Users/hyun/Desktop/dddjango/codex-dddjango/skills/dddjango-design-architect/SKILL.md:35, /Users/hyun/Desktop/dddjango/dddjango/scripts/check-idempotency-scope-creep.py, /Users/hyun/Desktop/dddjango/workspace/reference/ (dir listing).

#### datasource-skeleton-skip — `None`  (upheld: True)

UPHELD as 1-nondeterminism (high, backstopable=partial). All four adversarial probes failed to overturn.

NOT 2b (reference-wrong): architecture-ddd reference final.md §632 (block "표준 트리 *골격*은 데이터소스도 예외 없이 빈 패키지(__init__.py)로 실현한다 ... domain_layer/<aggregate>/에 *빈* 애그리거트 골격 ... 애그리거트 1차 폴더명은 ORM 모델명에서 도출(ProductModel→domain_layer/product/)") and houserules reference final.md:21/:24 are structure directives, not runnable examples that break on execution. grep for any surviving old "4계층/애그리거트 전개 면제" contradicting the mandate = EMPTY. No 2b residue.

NOT 2a (silence): the exact symptom is named — houserules ref :21 "데이터소스 앱도 위치·골격 모두 예외 없이 표준대로다", :24 "presentation_layer의 api/·schema/도 포함 ... 표현이 없는 BC도 빈 패키지로 항상 생성", ddd §632 "골격을 접으면 ... 루트 평면 <app>/은 §0-1 위반".

NOT 3 (drift): DDD mirror final.md:632 == reference §632 block byte-identical (grep-confirmed); houserules mirror final.md:21/:24 == reference verbatim; design-architect.md ("데이터소스도 빈 패키지로 무조건 실현", ORM-name derivation), design-review-ddd.md ("위치·골격은 면제 안 된다 ... 골격 생략은 §0 위반"), discipline-reviewer.md ("위치만 옮기고 종류 2차 폴더를 빈 패키지로조차 실현하지 않은 변종은 네가 본다 — 백스톱 사각") all carry the same mandate.

NOT 0 (by-design): grep for designer-discretion/underdetermined/둘 다 방어 near datasource/골격 = EMPTY. DR-49 (2026-06-08) REVOKED the exemption; mandate is unconditional — opposite of designer-discretion.

IS 1: reference+mirror+4 agents all correct, byte-identical, naming the exact symptom; LLM (cbvlive-codex) folded the skeleton anyway. backstopable=partial confirmed: check-layer-skeleton.py FIXED_NAME arm (:77-79 presentation_layer/api·schema·infra_layer/acl, FP=0 per :135/:198) is the deterministic "logic expansion"; AGG_CORE arm (:84/:168) covers existing aggregates; but :44 self-documents "ORM에서 애그리거트 이름을 추론하지 않는다 — 디스크에 실재하는 domain_layer/<X>/만 검사한다" and the 0-aggregate case (= datasource skeleton wholly missing, the precise symptom) is handed to the reviewer semantic lane ("안 잡고 reviewer 의미 레인에 맡긴다(저-recall 수용)") — an intentional FP-avoidance choice consistent with DR-32/37 app_label≠dir-name boundary. Remedy: accept+measure, keep deterministic fixed-name arm, do NOT add an ORM-inference arm. Isomorphic to confirmed anchor FC-2. Caveat: cited dslive-codex result file not present under workspace/eval/results/ (DR-50 unpushed per memory) — does not affect the determining reference/mirror axis.

#### bytecode-hygiene-eval — `2a-reference-insufficient`  (upheld: True)

분류 유지: **2a-reference-insufficient** (high confidence). 적대적 재검증으로 4개 경계(0/1/2b/3)를 모두 직접 반증했고, 핵심 주장 "정본(EVAL-METHOD) 침묵"이 가장 강한 형태의 2a-rebuttal probe에도 살아남았다.

[로커스 확정 — 하니스이지 코드생성 스킬 아님]
문제 진술 자체가 자기표지("eval 방법론 갭(라벨 아닌 하니스)"·relevantSkill=EVAL-METHOD·"채점 전 바이트코드 purge 필수"). 가장 위험한 대안인 "사실은 coder/discipline-tdd 결함(소스 미재실행)" 가설을 검사: dddjango/agents/coder.md grep "재실행|re-run|refactor 후 실행" = 0건; discipline-tdd reference/final.md:10 은 "refactor only on green"뿐, *최종 리팩터 후 재실행 의무* 규칙 부재. 그러나 설령 그런 coder 규칙이 있어 위반됐어도 그건 *별개 문제*(미실행 소스 배포)다. 이 문제는 명시적으로 **grader가 가려진 동작을 읽어 FAIL→PASS로 보인 것**이고, 이는 채점-실행-위생 = EVAL-METHOD 소관. 로커스 정확.

[2b 반증 — 정본/미러가 틀린 걸 가르치지 않음] RUBRIC.md:73 FC-1 기준(재고10·주문3→201∧잔7)은 옳고, purge 후 정확히 FAIL을 낸다. workspace/reference/ 전체 grep(pyc|bytecode|__pycache__|python -B|purge) = `pycodestyle`(Ruff 설정·무관) 외 0건. RUBRIC 전체에도 바이트코드/클린빌드 언급 0(유일 "stale" 히트 RUBRIC:152는 동시성 CAS-스파이 stale version·무관). 표준이 *깨지는 예시를 가르치지* 않음 = 2b 시그니처 없음. FC-1=2b 앵커("표준이 버그를 가르침")와 비동형.

[2a 확정 — 진짜 침묵, 인접 섹션에 숨은 것 아님] EVAL-METHOD.md:111-116 은 러너를 극도로 상세 규정(`.venv/bin/pytest`·pytest-django·`--ds=`·"manage.py test 금지"·ptcat env-오염 carve-out line113)하나 **바이트코드 위생은 한 글자도 없다**. "다른 섹션에 있는데 못 찾은 것 아닌가"(=3/1로 밀 위험) 정밀 검사: §4.3.1:190 "probe 실행 환경" 노트는 `setup_test_environment()`/`ALLOWED_HOSTS`(DisallowedHost 위양성)·ninja 파싱-검증 2단계만 다룸 — `.pyc`/클린빌드 부재. 인접 전제조건은 다루나 *바이트코드 상태* 전제는 미저술. 침묵 확정.

[3 반증 — 드리프트 아님] 바이트코드-purge 규칙은 어떤 정본·미러·스킬 reference에도 존재한 적 없음(corpus 전수 grep 0). 동기화에서 잃은 게 아니라 애초 미저술. → 3 아님.

[1 반증 — 비결정 아님, 결정론적 하니스 구멍] 충분한 지침에도 LLM이 흔들린 게 아니다. 코더가 마지막 테스트 실행 *후* tuple→Status 교체(NJ-5 "개선")하면 stale .pyc 잔존, *현재 문서화된* 러너 절차를 따르는 grader는 purge 안 해 가려진 동작을 결정론적으로 읽음. 마스킹 실재 확인: ~/Desktop/dddjango-nj7live-claude order_controller.py:12 `from ninja import Status`·:58 `-> Status`·:65 `return Status(...)`(소스 깨짐, 클린빌드 happy path 500). 처방은 생성코드 백스톱/"수용+계측"이 아니라 *절차 지시*(purge 스텝). → 1 아님.

[0 반증] EVAL-METHOD·RUBRIC 어디에도 "stale 바이트코드로 채점 허용" 의도적 명시 없음. 오히려 FC 기계(§1.4)는 *실제 동작을 결정론적으로* 잡는 설계라 마스킹이 그 의도를 정면 위배. → 0 아님.

[앵커 일관성 + 재발 증거] ACL-EX2=2a("전수성을 도메인 예외에만 앵커·인프라예외 책임 *침묵*")와 동형 — 방법이 러너를 pytest 호출에만 앵커하고 그 런의 *바이트코드 상태 전제*에 침묵. 재발 확정: DEVLOG.md:94 DR-36 "Codex FC-2 경계(stock==quantity) 회귀테스트 FAIL(`.pyc` 정리 후 재현)" — 같은 마스킹이 이미 한 번 물었는데 방법에 미박제(= 비결정 LLM이 아니라 미저술 규칙의 반복 노출 = 2a 강화).

[처방 형태의 강한 선례 — 정밀 보강] 제안 처방(EVAL-METHOD §1.4 purge 전제 1줄 + §6.2 헤더 필수 필드 + 소급 규율)은 *바로 같은 코퍼스가 이미 측정-전제조건 갭을 처리하는 방식*과 양식적으로 일치한다. EVAL-METHOD.md:263 은 2026-06-09 *바로 그날* ptcat env-오염 갭에 "fixture 도구 환경" 필수 헤더 필드를 신설했고 명시적 소급 미적용을 달았다(§4.3.1:204 소급차단 패턴과 동형). 즉 2a "신규 저술" 처방이 §6.2:263 선례 덕에 거의 기계적·저위험. 처방 항목3(하니스 도구화: `__pycache__` 삭제 + `python -B`)은 결정론·LLM 비의존이라 2a 신규저술 + 하니스 자동화가 같은 방향 — 단 이는 생성코드 백스톱(check-*.py)과 무관(채점 실행 환경 문제이지 생성물 아님)이라 backstopable=N/A가 정확. 범위 한정도 정확: implementation-test reference는 "테스트 작성법"(redis fixture·--lf 재실행)이라 grader 실행 위생과 별개 — locus 오인 주의 표기 타당.

#### reviewer-livefire-downgrade — `None`  (upheld: True)

분류 유지: 1-nondeterminism (backstopable=yes). 적대적 반증 시도가 모두 실패했고, 인용된 file:line 근거가 전수 일치한다.

[2b 반증 시도 — 정본이 틀렸나?] 실패. workspace/reference/implementation-django-ninja/reference/final.md:130 "오류는 operation에서 raise하고 성공 schema만 return한다 ... operation 본문에서 (status, ErrorSchema) 튜플이나 수제 HttpResponse/JsonResponse로 오류 응답을 직접 만들지 않는다", :443-446 "오류는 operation에서 raise하고, problem+json 변환은 중앙 @api.exception_handler와 헬퍼 한 곳이 한다. 이게 처방된 기본이다 ... operation이 raw 응답을 만들 일이 없어 본문 우회가 구조적으로 불가능", :510 "도메인 예외 → status 매핑은 presentation 소유" — 모두 *올바르고 실행가능*하다. FC-1 앵커(final.md:146-171 status:str↔status:int 충돌로 happy path 500=정본이 버그를 가르침)와 결정적으로 다르다. 여기 정본은 일관·작동하는 처방이다. LLM이 *올바른* blocker를 강등한 것은 정본 결함이 아니라 올바른 지침의 오용이다. → 2b 아님.

[2a 반증 시도 — 정본 침묵인가?] 실패. final.md:130이 operation 본문 수제 오류 응답을 명시 금지하고 :443-446이 중앙 핸들러를 명령한다 — 침묵이 아니다. ACL-EX2 앵커(houserules §2:144가 전수성을 포트 *도메인* 예외에만 앵커·인프라 transient/permanent 침묵)와 달리, 여기 정본은 오류→HTTP 중앙화를 직접 다룬다. → 2a 아님.

[3 반증 시도 — 미러 드리프트인가?] 실패. Claude 미러 dddjango/agents/discipline-reviewer.md:41이 위반을 blocker로 분류하고 안티-강등 표현 박제("일부 예외만 핸들러가 처리하고 나머지 status 선택이 operation·application에 남는 부분 중앙화는 면제가 아니라 blocker다", "'하나라도 있음'이 위반을 사면하지 않는다"). Codex 미러 codex-dddjango/skills/dddjango-discipline-reviewer/SKILL.md:42가 동일 불릿 보유, 인접 :43에 직접 지시 "DR-21식 강등 방지를 위해 권고로 흐리지 말고 명확히 important로 든다". 정본·양 미러 모두 올바름 — 미러가 잃은 게 없다. → 3 아님.

[0 반증 시도 — 설계상 허용인가?] 실패. 오류→HTTP 중앙화는 designer-decides 축이 아니라 하드 blocker다(final.md:130이 본문 오류 생성을 결함으로 규정: "변환이 흩어지고 problem+json content-type을 일관되게 못 맞춘다"). BC 분해(§632 designer-decides) 앵커와 다르다. → 0 아님.

[1 잔여 — 가장 위험한 오판(고칠 수 있는 걸 LLM탓으로) 점검] 정본도 미러도 *정말 충분*하다(위 4개 반증으로 입증). 그런데도 LLM이 흔들린다: 고립 텍스트판별 N=9/9 blocker(DEVLOG.md:66·:183 #10)였으나 라이브 파이프라인(전체 에이전트+carve-out+홀리스틱 심각도+경쟁 blocker)에선 같은 실위반을 권고로 silent downgrade(DR-21). DEVLOG.md:183 DO-NOT-RETRY #10이 근본을 정확히 진단: "silent downgrade/누락은 bullet이 아니라 주의 배분·산출 형식에서 일어남 ... 문구 강화 자체가 부족"(v2 사전시뮬 0/3, DR-22). 충분한 지침에도 비결정적 약화 = 1번 정의 그대로. 모호/부족을 LLM탓으로 돌린 게 아님이 정본·미러 직접 인용으로 확정된다.

[backstopable=yes 하위질문 점검] 확정. 결정적 백스톱 dddjango/scripts/check-error-centralization.py가 실재하며(직접 읽음) AND 합성: 경로(application_layer/, line 68) AND 신호(RESPONSE_CALL_RE·ERROR_STATUS_RE·HTTP_ERROR_RE·NINJA_IMPORT_RE, lines 42-58) AND git-diff(_is_new_or_modified, lines 77-99), 발견 시 exit 2(line 135). commands/dddjango.md:86에 게이트 ②로 배선됨(직접 확인: "②...check-error-centralization.py(4계층 application 계층이 오류→HTTP status 변환을 직접 수행했는가)"). P1a 핵심 형태(application_layer가 JsonResponse/HttpResponse·status=4xx/5xx·ninja HttpError·ninja import 직접 생성)는 깨끗한 AST/텍스트 신호라 결정적으로 차단 가능. FC-2 앵커(하드 게이트 미존재·backstopable=partial)보다 *더 명확한* 1/yes — 게이트가 가능할 뿐 아니라 이미 구축·배선·exit2 작동(DR-23 dual·DR-30 라이브 배선).

[backstopable의 한 가지 미묘점 — 정직하게 점검] 백스톱이 원리상 못 보는 의미적 변종(멱등성 스코프크립→status:int 객체가 application 흐름→중앙핸들러 죽은코드, DR-24)은 존재하며 backstopable=no다. DEVLOG.md DO-NOT-RETRY #11이 "exit0을 구조적 준수로 해석" 금지를 박제. 분류가 이를 이미 명시 수용(reviewer 의미 레인+별도 백스톱 ⑩ check-idempotency-scope-creep[commands/dddjango.md:86에 배선 확인]+RUBRIC SD-6으로 계측). 즉 핵심 형태=backstopable, 의미층=계측이라는 분류의 nuance가 코퍼스로 완전 뒷받침된다 — 과대주장 없음.

결론: 4개 보정 앵커와 정합(2a=정본침묵·2b=정본버그교습·1=하드게이트미존재와 명확히 구분되고, 여기선 정본 올바름+하드 결정적 게이트 이미 존재라 가장 깨끗한 1/yes). 분류 유지.

#### backstop-exit0-false-compliance — `1-nondeterminism`  (upheld: True)

분류 유지(1-nondeterminism·non-backstopable). 적대적 재검증에서 인용된 모든 근거가 verbatim 확인되고 네 경쟁 카테고리(2b·2a·3·0)가 모두 반증됨.

[정본 = 방법론] 이 문제는 산출물 결함이 아니라 채점 방법론 메타 문제다 — LLM grader가 결정적 백스톱 침묵(exit0)을 의미적 준수로 과신하는 인지 일탈. 따라서 결정트리의 "정본"은 reference 코퍼스가 아니라 EVAL-METHOD.md + RUBRIC.md(문제 relevantSkill이 명시). 이 prerequisite는 DEVLOG §3 #11(:184)·#14(:187)이 문제 프레이밍과 verbatim 일치해 확정: "백스톱 침묵(exit0)은 '그 백스톱의 좁은 텍스트 계약 통과'일 뿐 ... 전면 준수로 일반화 금지".

[0 반증] designer-decides 아님 — 채점-정확성 실패이고 능동 처방 대상. 드롭 아님.

[2b 반증 — 정본이 틀린 게 아니라 LLM이 올바른 규칙을 안 따름] EVAL-METHOD/RUBRIC의 규칙은 *올바른* anti-Goodhart 규칙이다. FC-1(2b)은 표준이 *버그를 가르치는*(OrderOut.status:str↔ProblemOut.status:int + return Status 201 예시→happy path 500) 경우지만, 여기 방법론은 정확히 *옳은 것*을 가르친다. 실패는 grader가 올바른 규칙을 건너뛴 것이지 규칙이 오도한 게 아니다. 재확인: EVAL-METHOD.md:100("operation 본문·backstop exit0만으로 NJ/SD-6 판정 금지")·:109("결정 PASS면 의미 생략 절대 금지 — 의미 레인은 항상 수행")·:137("스크립트 exit0이어도 의미 FAIL이면 치명")·:139(Goodhart 모든 치명항목 차단); RUBRIC.md:26("의미 레인 FAIL이면 스크립트 exit0이어도 SD-6 치명 FAIL(WEAK 강등 금지)").

[2a 반증 — 침묵 아님] 방법론이 이 문제에 대해 *반복·명시* 지침을 보유(5+ loci). 단순 산문 규칙을 넘어 (i) 항목별 blind-spot 카드 의무(:52)·SD-6 "status:int 객체 흐름 못 봄"(:63), (ii) 결과지 backstop-blind 메타 섹션 의무(:254), (iii) *프로세스 집행*: N_grader≥3 + 적대 grader(:21·:46)·자기보고 불신·조정자 직접검증(:262·:270)·경합 시 보수 FAIL(:105). "산문만이라 사실상 침묵"이라는 가장 강한 2a 반론도 이 프로세스 통제로 무너진다 — DR-24의 5-서브에이전트 심층감사를 제도화한 것이라, 침묵 빈틈이 아니라 known-hard 문제에 대한 *수용된 프로세스 통제*다.

[3 반증 — 드리프트 없음] grader가 실제 읽는 별도 미러가 존재하지 않는다: workspace/eval/rubric/는 EVAL-METHOD.md·RUBRIC.md·rubric-metrix.md 셋뿐이고 파생 grader 프롬프트/템플릿이 없다(코퍼스→미러 동기 비대상 단일출처). 저-recall 사실을 담는 또 다른 잠재 "미러"인 백스톱 docstring도 자백을 충실 보유: check-error-centralization.py:1-13·check-mechanism-ownership.py:1-9("좁은 고정밀·저-recall ... 의미적 회피는 일부러 잡지 않는다 — ③ discipline-reviewer 담당")·check-idempotency-scope-creep.py:31-33("한계(정직) — 이름 회피 ... recall 갭은 discipline-reviewer가 보완"). 방법론·스크립트 양쪽이 정직 → 드리프트 부재.

[→ 1, backstopable=no] 정본 적정·미러 충실(부재)인데도 LLM grader가 흔들린다. 결정적 discriminator는 *일탈의 거주지*: fixture는 텍스트 계약을 통과(exit0이 백스톱이 보는 것에 대해 정확)했고, 잔여는 의미적이며, 방법론은 이미 의미 레인으로 그것을 잡으라고 *의무화*한다. 따라서 일탈은 산출물 텍스트나 reference 산문이 아니라 grader 인지(의무 의미 레인 건너뛰기·단일-패스 합리화 'OperationalError→500=carve-out 정당')에 있다. 코드베이스 위 어떤 AST/텍스트 신호도 "grader가 exit0을 과신했다"를 결정적으로 탐지 불가 — 정의상 코드베이스는 텍스트 계약을 통과했고 잔여는 의미적이기 때문. 보정 앵커 FC-2(category 1·부분 backstopable)와 일관하되 여기선 방법론이 하드 규칙(exit0≠준수⇒치명 FAIL)을 *이미 보유*함에도 LLM이 흔들리므로 backstopable=no가 더 강하게 성립.

[처방] 수용+계측(프로세스 통제·이미 배선됨): :100/:109/:137 규칙 계속 집행, :52 blind-spot 카드 + :254 backstop-blind 메타 섹션 의무 유지, N_grader≥3 + 적대 grader + 자기보고 불신 유지. 반복 의미 변종(멱등성 스코프크립·합성 인프라예외·transient 과잉매핑·test-config·catch-all)에 좁은 전용 백스톱을 추가했으나(check-idempotency-scope-creep/-synthetic-infra-exc/-transient-overmapping/-test-config/-catch-all-handler 실재 확인), 이들은 각자 저-recall이고 동일 blind-spot을 재방출하며 특정 반복 변종만 깎을 뿐 — 메타 문제(grader 과신)를 backstopable로 만들지 못한다.

#### g1-escalation-nondeterminism — `None`  (upheld: True)

분류 유지: category 1-nondeterminism, backstopable=partial. 적대적으로 5개 탈출 경로를 모두 반증했고(분류자가 틀렸다는 가정에서 출발), 인용 file:line이 전부 직접 재확인됨.

[2b 반증 — 정본 틀림 아님] §6.8 정본 workspace/reference/architecture-ddd/reference/final.md:1989-2010은 올바른 *패턴 선택 절차*다(가벼운 패턴 우선·소유 라우팅 표). grep으로 blast/escalat/G1/표면화/에스컬 전부 0매치 확인. :1996 step4("선택하지 않은 무거운 패턴과 이유를 기록")는 명세 *문서화*이지 에스컬레이션 규칙이 아니다 — 실행하면 깨지는 예시가 아니므로 2b 아님. 스코프-규율 정본(:648 데이터소스 골격 의무·"판정 소유" 기준)도 올바르다.

[2a 반증 — 가장 위험한 오판, 집중 검증] 증상은 두 축(②스코프 규율 갭·③G1 에스컬레이션 비결정, DEVLOG DR-24:68 원문 "메타 4갭(②스코프 규율 ③G1 비결정)"과 일치)을 묶는데, *둘 다 침묵이 아니라 명문화*돼 있다: (i) 스코프-규율 규칙 — design-architect.md:36("미요청 멱등성을 명세에 silent 의무로 박는 건 스코프 초과다… 같은 원리로 다른 견고성 결정도 silent 의무화 말고 G1 표면화"), :40, dddjango.md:59("범위 아님"에 "필요 시 설계가 G1에서 제안")·:65·:66; (ii) G1 에스컬레이션 메커니즘 — design-architect.md:52(미해결 트레이드오프→명세 옵션→Coordinator G1 제시)·:38·:36, dddjango.md:75. 정본 자기책임(누락금지·임의확정금지)은 architecture-api:184("설계자가 임의 확정하지 않는다 … §5/G1")·architecture-ddd:648에 커버됨. §6.8이 에스컬레이션 게이트에 침묵하는 것은 그것이 본질적으로 *오케스트레이션*(coordinator 게이트) 산출물이지 정본 코퍼스 내용이 아니기 때문이라 2a 정본 결함이 아니다.

[3 반증 — 드리프트 없음] §6.8 정본 vs 미러 diff: dddjango/skills/architecture-ddd/references/final.md:1973 헤더·내용 byte-identical. 스코프·G1 지침은 라이브-로드 미러(agents/*.md·commands/dddjango.md)에 전부 존재. → 3 아님.

[0 반증 — 설계상 허용 아님] 정본은 고-blast 트레이드오프를 사용자에게 *표면화*하길 원한다(architecture-api:184 "임의 확정하지 않는다")—"둘 다 방어가능" 명시 없음. BC분해/판정소유(category 0)와 달리 여기선 designer-decides가 아니다.

[1 확정] 정본(누락금지 :648/:184)·에이전트(에스컬레이션 :52/:38/:36)·코디네이터(:75·:59) 모두 충분·올바른 지침을 담는데도 architect가 런마다 고-blast 트레이드오프를 §Open Questions에 매장하거나 요청 외 스코프(멱등성·협상)를 비일관 차단(DR-24 메타 ②③). 보정 앵커 FC-2(권장하나 hard 게이트 없음·LLM 비일관·backstopable=partial)와 동형이고, ACL-EX2(2a=정본이 자기 책임 침묵)와 구별된다.

[backstopable=partial 정밀성] 멱등성 변종 *결과*는 결정적 백스톱 ⑩ check-idempotency-scope-creep.py가 잡는다 — 존재 확인(dddjango/scripts/, 로직 "2 ∧ 3 ∧ ¬4 → exit 2", scope.md 미요청단정+application 멱등성 코드)·배선 dddjango.md:86. 그러나 '§Open Questions 매장 vs G1 상정' 일반 결정과 협상-발명은 의미층이라 깨끗한 신호 없음 — DR-38(DEVLOG:96 "협상=막을 위반 아님, §6.3:441이 406 협상 허용/명령→백스톱 신호가 정당 코드와 동형=구조적 불가")이 독립 확인. 따라서 일반 메타갭=backstopable=no(수용+계측).

[미세 정정·분류 강화] classifier rationale가 스코프-규율 축의 정본 커버를 §6.8/architecture-api에 의존하나, 최강 앵커는 architecture-ddd:648(데이터소스 골격 의무) + 에이전트층이다. 정본 커버가 rationale가 인정한 것보다 *두텁다* → 2a 반증을 강화하고 category 1을 더 분명히 한다(분류 변경 불요).

처방 동의: (a) ⑩으로 멱등성 변종 결과 차단(이미 배선), (b) 일반 메타갭은 의미층이라 결정적 백스톱 불가·문구 추가 불요(지침 이미 올바르게 존재), (c) dual 라이브 N≥2 계측으로 §Open Questions→G1 승격 재현율 관측, 임계 이상+깨끗한 신호 발견 시에만 좁은 백스톱 승격(P1a→⑩·C3→⑩ 선례). 정본/미러 텍스트 수정 불요(드리프트 0, 정본 자기책임 커버됨).

#### corpus-skill-drift — `0-by-design`  (upheld: True)

UPHELD as 0-by-design (drop). I independently re-verified every load-bearing claim with my own extraction methods (not trusting the tool's self-report), and adversarially tested the three competing categories. All hold.

AUTHORITATIVE TOOL: `python3 workspace/tools/corpus_mirror_sync.py --format json` → exit 0, 11/11 skills inv1=in_sync AND inv2=in_sync. The body comparison is honest, not gameable: corpus_mirror_sync.py:132 does a literal byte compare of post-anchor region; split_at_body (:58-94) anchors on the FIRST non-P1 '## ' heading and raises StructureError (:90-92) on any non-attribution line before the anchor, so a real body drift cannot masquerade as in_sync.

INDEPENDENT BODY CHECK (my own awk extraction from first non-P1 '## ' heading to EOF, sha256 src-vs-dep): MATCH for all 11/11. The mirror body lost NOTHING — refutes category 3 directly (decision-tree 3 = "정본엔 맞는데 미러가 잃음", but mirror body ≡ reference body byte-exact).

REFUTING THE PROBLEM'S OWN FACTUAL CLAIMS (the classification correctly caught these errors):
(1) Problem: "ninja만 skill +99줄". FALSE. wc -l: src=832, dep=822, codex=822 → source has +10 lines, not skill +99. Full `diff src dep` for ninja = exactly the 10-line `## P1 Source Sufficiency` block at src lines 3-12, located BEFORE the body anchor at src:26. Direction (source holds more, not skill) and magnitude (+10 not +99) both wrong in the problem.
(2) Problem: "본문 어긋남" (body diverges). FALSE. Independent sha256 body match 11/11.

PER-SKILL DIFF LOCALIZATION: every src-vs-dep diff line falls within preamble (before src_body_anchor_line): architecture-api 16 lines / anchor 19; implementation-django 29 / 32; ninja 10 / 26; etc. houserules = 0 diff lines (it carries P1 in dep too, per docstring :19). 100% of diffs are P1 table + source blockquote + abbreviation legend + '---' hr — the attribution region the tool docstring (:12-13) explicitly excludes as "의도적으로 다름".

inv2 RE-CHECK (dep references vs codex references, correct paths codex-dddjango/skills/<skill>/references/final.md per paths_for :111): 0 difflines all 11/11 (byte-identical Claude↔Codex).

SECONDARY CONCERN (problem flags SKILL.md + agents/*.md manual mirrors): SKILL.md Claude vs Codex = exactly 1 diff line per skill, confirmed for all 11 to be `< user-invocable: false` (frontmatter only, DR-48 known fact) — body byte-identical. agents/*.md have no source-mirror and no regeneration path (docstring :17-18: out of scope, not an R5 regression mechanism). No current classifiable body drift in either.

CATEGORY ADJUDICATION vs decision tree:
- 2b rejected: no wrong-vs-right content divergence exists; mirror body ≡ reference body.
- 2a rejected: not silent — an authoritative fail-CLOSED tool with explicit invariant spec exists.
- 3 rejected: mirror lost no body content (sha256 11/11 MATCH; inv1=in_sync). Residual = intended structural asymmetry (reference=source-of-truth holding P1; distribution=runtime copy stripping P1), documented at corpus_mirror_sync.py:12-13,62-72.
- 0-by-design CONFIRMED: tool-documented intentional allowance, structurally analogous to the BC-decomposition anchor (둘 다 방어가능/의도적). Regression guard already gated: fail-CLOSED detector currently exit 0; --write resolves any future body drift deterministically.

Remedy = drop (not a defect). Only operational note: agents/*.md and SKILL.md are outside the tool's auto-scope, so editing them requires manual 3-copy sync + a pre-commit `corpus_mirror_sync.py --check`; this is a build-checklist item, not a corpus defect to remediate.

#### user-invocable-frontmatter-drift — `0-by-design`  (upheld: True)

UPHELD as 0-by-design (high confidence). Adversarially re-verified all competing categories against direct file:line evidence; every alternative is refuted.

EMPIRICAL CORE (read-only, re-confirmed):
- Reference corpus is silent on frontmatter: `grep -rniE "user-invocable|frontmatter" workspace/reference/` → 0 hits. Corpus governs body knowledge only.
- Claude = 11/11 SKILL.md carry `user-invocable: false` on frontmatter line 4 (verified per-file: every Claude skills/*/SKILL.md line 4 = "user-invocable: false"). e.g. dddjango/skills/architecture-api/SKILL.md:4.
- Codex = 0/19 SKILL.md contain any `user-invocable` field (`grep -rn user-invocable codex-dddjango/skills/` → empty). Codex frontmatter closes after line 3 (name+description only): codex-dddjango/skills/architecture-api/SKILL.md lines 1-4 = `---` / name / description / `---`.
- The SYNC-mirrored portion is byte-identical: diff of references/final.md Claude↔Codex for all 11 corpus skills = OK/identical (rc=0). The thing that IS mirrored has zero drift.

WHY NOT 3-skill-drift (strongest competitor; symptom even calls it "구조적 드리프트 nit"): Drift requires the corpus to hold correct content a mirror lost. (a) Corpus silent on frontmatter (0 hits) — nothing to lose. (b) corpus_mirror_sync.py:17 EXPLICITLY exempts SKILL.md from mirroring ("스코프 밖(설계상 미러 면제, plugin-native 단일 파일): SKILL.md · agents/*.md · commands/*.md"); invariant 2 (corpus_mirror_sync.py:11-13) demands byte-equality only for references/final.md, which I verified identical for all 11. (c) `user-invocable: false` is a Claude Code skill-frontmatter field hiding internal sub-skills from the `/` menu — correct on Claude; its absence is correct on Codex because Codex's frontmatter contract carries only name/description. No symmetric "correct" value exists, so this is not lost content. REFUTED.

WHY NOT 2a-reference-insufficient (tempting reframe "corpus is silent → fill the gap"): silence is by-design, not insufficiency. corpus_mirror_sync.py:17 marks SKILL.md "설계상 미러 면제, plugin-native 단일 파일" — a platform-specific file the corpus deliberately does not govern. The corpus scope (final.md body) excludes platform skill metadata. REFUTED.

WHY NOT 2b-reference-wrong: frontmatter is not corpus-governed at all (0 hits) — there is no corpus text that could be wrong. REFUTED.

WHY NOT 1-nondeterminism: no LLM authors static plugin frontmatter; these are hand-authored mirror files, not generated output. The asymmetry is deterministic and intentional. Classifying it as 1 would be the dangerous mis-call (giving up on a fixable thing), but here there is nothing broken to fix. REFUTED.

WHY 0-by-design (Filter 0 fires — both states defensible): `user-invocable: false` correct on Claude (hides internal sub-skills from `/` menu); its absence correct on Codex (field meaningless to that platform's frontmatter contract). The 11-vs-19 set difference is itself by-design: the 8 Codex-only skills (dddjango, dddjango-coder, dddjango-design-architect, dddjango-design-review-{api,db,ddd}, dddjango-discipline-reviewer, dddjango-acceptance-tester) map exactly to Claude's agents/*.md (7 files: acceptance-tester, coder, design-architect, design-review-{api,db,ddd}, discipline-reviewer) + commands/dddjango.md (verified by ls). That is an architectural port choice (Claude=agents/commands, Codex=skills), not a knowledge regression. Consistent with anchor "BC 분해(판정소유) = 0" (both defensible). The symptom's own proposed criterion — sync on SKILL.md *body* byte-id — is an admission that frontmatter divergence is acceptable.

REMEDY: DROP. Cosmetic/infra metadata nit with zero behavioral effect; no source rewrite, correction, re-sync, or backstop warranted. Bodies already byte-identical exactly as the symptom requires.

MINOR CORRECTION to original classification's skillEvidence: the Codex path is codex-dddjango/skills/architecture-api/SKILL.md (NOT codex-dddjango/skills/dddjango-architecture-api/...). Non-load-bearing typo; substance (0/19 user-invocable, frontmatter = name+description only) fully holds.

#### version-pin-anchor-drift — `3-skill-drift`  (upheld: True)

분류 유지(category 3-skill-drift·high confidence). 적대적 반증 5갈래 모두 기각, 보정 앵커(FC-1=2b·ACL-EX2=2a·FC-2=1·BC분해=0)와 일관.

[핵심 증거 — 앵커 이동 커밋 직접 확인] 청소 커밋 74ad682 제목이 문자 그대로 "std: bare §6.2 핀 참조 → implementation-django-ninja §2.1 (버전핀 댕글링 청소·8파일·양판)"이고, `git show 74ad682`로 확인한 치환 패턴이 정확히 `§6.2 핀/버전-핀 규율` → `implementation-django-ninja §2.1 버전-핀 규율`이다. 변경 파일 = agents/acceptance-tester.md·coder.md, SKILL(dddjango·houserules·coder·acceptance-tester)·commands/dddjango.md = 8파일(SKILL/agents/commands)뿐. **`dddjango/scripts/check-test-config.py`는 이 커밋의 변경 파일 목록에 없다** → 따라서 :2·:297이 옛 `§6.2 핀` 앵커를 그대로 보유. 이것이 파생 산출물 lag = skill-drift의 정의.

[2b 기각 — 정본 안 틀림·올바른 위치] `grep -rn "§6\.2" workspace/reference/ | grep -iE "핀|러너|버전|설치"` = **공집합**. 정본은 핀-맥락 bare §6.2 댕글링이 0건. 핀 *표기*/매니페스트 = implementation-django-ninja/reference/final.md:98-100·:246("매니페스트 핀은 §2.1과 동일"), 버전 *값* 규칙 = houserules SKILL.md:97("### §6.2 새 런타임 의존성의 버전 선택"·Codex SKILL.md:96 동일). 정본이 깨지는 예시를 가르치지 않음.

[2a 기각 — 침묵 아님] 지침이 실재하고 올바른 곳(ninja §2.1·houserules §6.2)에 배치됨. 결함은 순수 파생-포인터 lag.

[3 유지] 결함 표면 = 백스톱 스크립트 자신의 docstring(:2 "Phase 2 러너 준비 §6.2 집행")·메시지(:297 "`implementation-test`/`implementation-django` §6.2"). 후자는 오귀속 — implementation-test §6.2 = pytest-asyncio(final.md:610), implementation-django §6 = 뷰패턴 CBV/FBV(final.md:687·§6.2 부재) → 둘 다 버전핀 §6.2 미소유. 이 스크립트는 corpus_mirror_sync 스코프 밖(workspace/tools/corpus_mirror_sync.py:17 "스코프 밖: SKILL·agents·commands", :21-23 "13 런타임 게이트(dddjango/scripts/check-*.py)는 …동기 대상 아님")이라 수동 유지 영역 → DR-48이 경고한 "수동 미러 드리프트" 실현. 정본=참(앵커 ninja §2.1 이동)인데 파생 산출물만 따라가지 못함 = 3.

[Codex byte-identity] `diff <(sed -n '2p;297p' dddjango/scripts/check-test-config.py) <(sed -n '2p;297p' codex-dddjango/skills/dddjango/scripts/check-test-config.py)` = IDENTICAL(exit 0). 양판 동일 lag.

[1 기각] 정적 plugin/corpus 파일 결함(whereObserved=DR-48 부수발견②), LLM 생성 출력의 비결정 흔들림 아님. 충분한 지침에도 흔들린 게 아니라 toolchain 포인터가 안 따라온 것.

[0 기각] designer-decides 변동 아님 — 내부 포인터 정합 결함.

[처방 범위 완전성 + 미세 정정] 플러그인 트리 전체 핀-맥락 bare §6.2 댕글러 = 정확히 check-test-config.py:2·:297(×2 미러)뿐. discipline-reviewer.md:35의 "houserules §6.2"는 자격화된 명시 앵커(houserules SKILL.md:97 실재)라 댕글러 아님 — 분류가 옳게 제외. houserules SKILL.md:97/96은 §6.2 섹션 *헤더 자체*(정의처)라 댕글러 아님. 즉 처방 대상 = 그 두 줄(양판) 한정으로 분류의 remedy 범위가 완전. remedy 미세 보강: :297 자격화 시 매니페스트 표기는 ninja §2.1(+implementation-django §3.1), 값 규칙은 houserules §6.2로 명시하고 오귀속 implementation-test §6.2[pytest-asyncio]·implementation-django §6.2[부재] 귀속 제거 — 분류가 이미 정확히 지목. 결정적 텍스트 nit이므로 재동기로 종결(라이브 불요·생성 동작 영향 0·백스톱 신설은 N=1 doc nit에 과투자).

#### unmapped-domain-exception-latent — `None`  (upheld: True)

분류 유지: 1-nondeterminism (confidence high). 5개 결정-트리 가지를 적대적으로 전수 재확인했고 모두 1을 지지한다. 단, 분류지의 Codex skillEvidence에 사실 오류가 1건 있으나 카테고리는 불변.

[0-by-design 반증] 정본 workspace/reference/implementation-django-ninja/reference/final.md:450-453이 이 변동을 명시적으로 *금지*한다 — "스키마는 1차 방어지 유일 방어가 아니라… 빠뜨리지 않는다(매핑 누락을 스키마 의존으로 정당화 금지)." designer-decides의 정반대. 0 아님.

[2b-reference-wrong 반증] 정본 :490-577은 *완결·자기일관 동작 레시피*다 — problem() 헬퍼(:503), 도메인 예외별 핸들러(ProductNotFound :510 / InsufficientStock :515), framework 기본 오버라이드(:520), transient 분기(:557-565, 영구장애 500 분기 포함), 최후방 catch-all @api.exception_handler(Exception)(:575). MRO 순서까지 주석(:575 "구체 핸들러가 MRO상 먼저"). 따라 실행해도 깨지지 않는다 — FC-1(OrderOut.status:str↔ProblemOut.status:int 충돌로 happy path 500)처럼 표준이 버그를 가르치는 게 아니다. latent 흠은 생산자가 핸들러를 *누락*할 때만 생기는 준수 실패지 처방 결함이 아님. 2b 아님.

[2a-reference-insufficient 반증] 침묵이 아니라 이 시나리오의 *축자적* 기술이 :450-453에 존재(Field 중복가드→도메인 raise latent→공통 베이스 매핑에서 누락 금지)하며, 도메인 핸들러 등록 *방법*까지 :510-517로 구체 시연. 막연한 exhortation이 아니라 actionable recipe. 2a 아님.

[3-skill-drift 반증] 양 미러 모두 텍스트를 축자 보유. Claude 미러 dddjango/skills/implementation-django-ninja/references/final.md:440-443은 정본과 byte-identical(diff 결과 §P1 메타헤더 블록 3-12행만 차이, 본문 동일). Codex 미러 codex-dddjango/skills/implementation-django-ninja/references/final.md:443도 동일 텍스트 보유(diff 차이=동일 P1 메타헤더뿐). 콘텐츠 드리프트 0. 3 아님.

[1-nondeterminism 유지] 정본 정확 + 양 미러 충실인데도 DR-45 생산자가 핸들러 누락. 결정적 백스톱 check-catch-all-handler.py는 (1)catch-all 부재(:165-171) (2)핸들러 되던지기(:173-179)만 차단하고, "특정 도메인 예외(InvalidOrderQuantity)가 매핑돼야 하는데 누락"은 의미층이라 원리상 못 봄(docstring :24-28이 의미 완전성을 discipline-reviewer로 명시 위임). 게다가 catch-all이 존재하면(아니면 조건1 발화) 이 흠은 traceback이 아니라 500 problem+json으로 *가려져* 신호조차 안 남 → backstopable=partial-no 정확. 의미 렌즈는 discipline-reviewer가 소유: agents/discipline-reviewer.md:41("부분 중앙화는 면제가 아니라 blocker"·"중앙 변환점의 완전성[미매핑 누수]… important")·:44(NJ-7 catch-all 렌즈, "백스톱은 Exception catch-all 존재만 보아… 네가 본다"). 보정 앵커 FC-2(정본 권장·LLM 비일관·backstopable=부분)와 구조 동형.

[심각도 정합] DEVLOG.md:126(DR-45)이 이 항목을 *minor*로 기록("InvalidOrderQuantity 핸들러 부재[스키마 Field(ge=1)가 가려 latent]"), RUBRIC.md:62/173이 NJ-7을 비치명 '강'(NJ-3·4급)으로 등록 → minor/latent 심각도 정확, 신규 hard 게이트 추가는 과잉이라는 remedy와 정합.

[정정 1건 — 카테고리 불변] 분류지 skillEvidence가 Codex 콘텐츠를 "47줄 얇은 포인터 SKILL.md"로 *오기*했다. 실제 NJ-7 콘텐츠는 codex-dddjango/skills/implementation-django-ninja/references/final.md(822줄, :443에 텍스트 보유)에 있고 SKILL.md(47줄)는 스킬 진입 포인터일 뿐이다. 그러나 두 파일 모두 텍스트를 보유하므로 "콘텐츠 드리프트 없음" 결론은 정확 → 카테고리 1-nondeterminism 불변.

remedy: 수용+계측(FC-2 동형). 정본·미러가 이미 올바른 처방을 보유하므로 저술/정정/재동기 불필요. 결정 백스톱 부적합(어떤 도메인 예외가 raise 가능한지는 의미층·catch-all이 흠을 500으로 가려 신호 소실). (a) discipline-reviewer 의미 렌즈가 "유스케이스가 raise하는 도메인 예외 전수가 중앙 매핑에 있나" 유지(agents:41/44에 명문) (b) RUBRIC NJ-7 라이브 관측+잔여흠 원장 계측(스키마 우회 probe로 미식별 500 노출). N=1·minor·latent라 과잉 게이트 금지.

#### release-unpushed-incomplete — `0-by-design`  (upheld: True)

UPHELD as 0-by-design (drop). Adversarial re-verification confirms the classification.

EMPIRICAL CLAIMS RE-VERIFIED: origin/main=392627c (v1.0.0), local HEAD=a4c7434, 106 commits ahead (git rev-list --count origin/main..HEAD). plugin.json local=1.9.0 vs git show origin/main:dddjango/.claude-plugin/plugin.json=1.0.0. marketplace.json source="./dddjango" → deployment artifact = origin/main = v1.0.0, so the live-validation-vs-release-artifact gap is factually confirmed. DEVLOG.md:20 carries the explicit user-approval release gate ("릴리스는 사용자 명시 push 승인 대기·가드레일이 push 차단"). The symptom's parenthetical "origin은 58660a0까지" is stale (true origin/main=392627c), but the substantive claim is accurate and the classifier already noted this.

ADVERSARIAL TEST OF EACH AXIS: The classifier's core premise — no reference/skill/agent/command governs git push or marketplace release — holds under exhaustive grep. The only 3 corpus hits for push/release/marketplace are all individually-inspected false positives: workspace/reference/implementation-python/reference/final.md:2033 (code comment "향후 릴리스에서 개선"), workspace/reference/implementation-test/reference/final.md:474 (pytest xfail reason string), dddjango/skills/discipline-houserules/SKILL.md:104 (Python dependency pinning policy, not plugin deployment). None governs this plugin's deployment.
- 2b fails: no reference about push to be wrong.
- 2a fails: silence here is genuine out-of-scope, not a missed section (greps are unrelated).
- 3 fails: drift presupposes correct corpus push-guidance that a mirror lost; none exists. plugin.json 1.9.0 vs 1.0.0 is release-lag, NOT mirror drift.
- 1 fails: this axis concerns generated Django code wobbling under sufficient guidance; push/release is not generated code and not produced by any agent run, so the axis is inapplicable — there is no corpus lever to under-determine.

ON THE 0 WRINKLE: The strict BC-decomposition anchor for category 0 = corpus text affirmatively says "both defensible." Here the corpus is SILENT rather than affirmatively permissive. However, the taxonomy's operative meaning of category 0 is "not a corpus defect → drop," and the unpushed state is the intended product of two deliberate controls: (1) the global guardrail "Commit or push only when the user asks" (CLAUDE.md + system reminder), and (2) the DEVLOG.md:20 user-approval release gate. Intentional and sanctioned → same operative conclusion as 0-by-design, and consistent with the BC anchor=0 (process/designer-decides → drop).

WHY NOT A CORPUS-QUALITY CATEGORY AT ALL: categories 1/2a/2b/3 each presuppose content that produces or governs generated Django code. Push/marketplace release is an operational, human-gated deployment step with zero governance anywhere in the corpus (verified). Nothing to author (2a), correct (2b), resync (3), or stabilize (1).

REMEDY (operational, not root-cause): drop from the defect ledger; track as a release-checklist item. On user push approval: merge/PR eval→main, push, bump deployed plugin.json to current (1.9.0). No corpus authoring, mirror resync, or new backstop is warranted.

Key evidence paths: workspace/DEVLOG.md:20 (release gate), .claude-plugin/marketplace.json (source="./dddjango"), dddjango/.claude-plugin/plugin.json (local 1.9.0), /Users/hyun/.claude/CLAUDE.md (push guardrail). False-positive grep hits: workspace/reference/implementation-python/reference/final.md:2033, workspace/reference/implementation-test/reference/final.md:474, dddjango/skills/discipline-houserules/SKILL.md:104.

#### duplicate-app-backstop-blind — `None`  (upheld: True)

UPHELD: 1-nondeterminism (backstopable=yes), confidence high. Adversarially re-verified every cited file:line; the classification survives every refutation attempt.

DECISION-TREE WALK (each branch checked against the actual files):

0-by-design? REFUTED. Canonical houserules §0-7 "이주 배타성" (workspace/reference/discipline-houserules/reference/final.md:27) treats dual residence as a hard violation ("미완 이주다"), NOT a defensible designer choice. Contrast the BC-decomposition anchor (=0) where architecture-ddd §632 explicitly says designer-decides. No such permission here.

2b (reference WRONG)? REFUTED. §0-7 (final.md:27) is a CORRECT, executable rule: "기존 Django 앱을 infra_layer/django_<app>/로 이주하면 옛 루트 <app>/는 migrations/까지 통째 제거하고 INSTALLED_APPS에서 옛 루트 등록을 뺀다 … counterpart가 새 경로에 자기 마이그레이션을 갖췄는데도 같은 앱이 옛 루트와 application/에 동시 존재하면(앱 파일이든 migrations/-only든) 미완 이주다." Following it does NOT break anything (unlike the FC-1 anchor where the prescription itself yields a 500). The producing agent (Codex coder, copy-not-move) VIOLATES a correct rule → that is misuse of a correct reference = 1, not 2b.

2a (reference INSUFFICIENT)? REFUTED. §0-7 is NOT silent — it names the exact dual-residence case (migrated counterpart EXISTS + old root remains = incomplete migration). This is the decisive contrast with the ACL-EX2 anchor (=2a), where discipline-houserules §2:144 genuinely says nothing about infra-exception transient/permanent responsibility. Here the reference speaks directly to the symptom. Supporting context: §0-1:21, §0-5:25 (Django app lives in infra_layer/django_<app>/).

3 (skill DRIFT)? REFUTED. I read both files in full. dddjango/skills/discipline-houserules/references/final.md:27 is BYTE-IDENTICAL to canonical §0-7 (verbatim match confirmed). Mirror is faithful; nothing lost.

1 (NONDETERMINISM)? UPHELD. Reference + mirror both correctly prescribe the rule, yet (a) a producing agent reproducibly violates it (DR-51: Codex copy-not-move, N=20+) and (b) the PRODUCTION-TIME deterministic net is blind. Verified in code: check-app-container.py:197-198 exempts the candidate via `if _has_migrated_counterpart(app_container, d.name): continue`; the helper _has_migrated_counterpart (:164-179, reusing _has_real_app_content :146-161) returns True precisely when application/<name>/ holds a real migrated counterpart — which is exactly the dual-residence husk scenario. G3 (per its own docstring :29-31 and :198 comment "이미 application/ 로 이주됨 → orphan/정리 영역") was designed for the orphan-cleanup case and therefore CANNOT fire on dual residence. The symptom itself concedes the eval-time net DOES catch it: I confirmed check-structure.py:89 emits FAIL-신호 via `bad = [... for a in apps if "application" not in a.parts]` (RUBRIC SH-1, RUBRIC.md:87-93), and reviewer.md:46 carries prose for the touched-root-data-source variant. That isolates the gap to the production-time TOOL, not the skill/reference — the signature of 1-nondeterminism, not a reference/mirror defect.

backstopable = YES — HONEST AND DEMONSTRATED. A clean path/AST signal exists at production time: root candidate is a FULL Django app package (apps.py/models.py present; migrations-only-with-apps-moved is PASS/Q-5 per RUBRIC, so excluded) AND application/<name>/ holds a real migrated counterpart (G3-INVERTED, reusing _has_real_app_content). Feasibility is already PROVEN: DR-51's dedicated ⑰ check-duplicate-app inverted G3 into a trigger, was implemented, and passed 6 synthetic fixtures + a dslive dual run (codex exit2 / claude exit0). I VERIFIED the current state matches the stated rollback: `dddjango/scripts/check-duplicate-app.py` does NOT exist (ls exit=1). The rollback was caused by a live-VALIDATION gap (the duplive fixture was a clean full-migration that never exercised ⑰), not by signal infeasibility. Closest anchor FC-2 (=1, recommended-but-not-hard-gated, backstopable=partial); this case is STRONGER — the missing net is fully deterministic and already demonstrated working.

WHY NOT mis-blaming the agent (the most dangerous error per the rubric): The reference and mirror are demonstrably SUFFICIENT (correct, explicit, byte-identical, naming the exact case) — so the gap cannot be re-routed to 2a/2b/3. The decision tree has no separate "tool-gap" bucket; a blind production backstop while reference+mirror are correct lands on 1 by construction, with backstopable=yes pointing straight at the fix (re-land ⑰). This is the opposite of giving up on a fixable defect.

REMEDY CORRECTION (does not affect the category): the remedy cites workspace/flow/plugin-audit-roadmap.md (rank-1) and fix-plan.md, but on this branch workspace/flow/ currently holds only dddjango-timeline.html — those roadmap files are absent from the working tree, so that pointer is stale. The remedy DIRECTION remains sound and verified-feasible: re-land a deterministic production-time backstop dedicated to dual residence — Signal: repo-root candidate is a FULL Django app package (migrations-only history-pin excluded per RUBRIC.md Q-5) AND application/<name>/ holds a real migrated counterpart (reuse check-app-container._has_real_app_content) → exit 2; make it touched-INDEPENDENT (the old root may be git-untracked, which is why check-app-container's G2 touched-gate :117-143 and G3 exemption :197-198 both miss it); drop the registration/dead-remnant G4 (DR-51 subagent IMPORTANT-1, to also catch pure copy-not-move where only the root is registered); wire into commands/dddjango.md + SKILL gate list + byte-identical Claude & Codex script mirrors; and CRITICALLY validate with a REAL dual-residence live fixture (the exact gap that caused the prior rollback). Keep reviewer.md:46 prose as the semantic backstop for name-disguised variants. Do NOT touch the reference or mirrors — §0-7 (final.md:27) is already correct and faithfully mirrored.

## 잠재 결함 — 미발화 코퍼스 스윕 (5스킬, ninja 제외=§보강)

### architecture-ddd
**[1]**
- **type**: landmine
- **location**: workspace/reference/architecture-ddd/reference/final.md:847 (mirror: dddjango/skills/architecture-ddd/references/final.md:831)
- **description**: CONFIRMED by execution. The 'Aggregate as Factory' snippet at canonical line 847 returns `Product(id=product_id, store_id=self.id, name=name, price=price)` with a `-> "Product"` annotation, but the only `class Product` in the document (canonical 734-739 / mirror 718-723) is `@dataclass class Product: id; name; description; price` — it has NO `store_id` field and `description` is required with no default. Running the factory snippet against that Product raises `TypeError: __init__() got an unexpected keyword argument 'store_id'` (I reconstructed both blocks and executed it; output was exactly this TypeError). Two independent breakages: (a) `store_id` is rejected as an unexpected kwarg, (b) required `description` is omitted. Adversarial checks that could have refuted it but did not: (1) The blocks are separate fenced code blocks under separate subsections (Product under '#### Vernon의 4가지 설계 규칙', create_product under '#### 애그리거트를 팩토리로 사용하기'), but the factory block defines its own `Store` yet neither defines nor imports `Product`, so the `-> "Product"` annotation and the constructor call can only resolve to the single document-defined `Product` (grep-confirmed: exactly one `class Product`). The snippet is executable-but-broken as written, same defect class as the FC-1 anchor. (2) The `price: Money` vs `price: int` mismatch is annotation-only and does NOT cause the failure (dataclasses don't enforce types at runtime); the failure is specifically `store_id`/missing `description`, exactly as claimed. (3) Present byte-identically in canonical and mirror (verified), so correctly NOT drift. Primary type is landmine (broken executable example); it is secondarily an internal inconsistency (two incompatible 'Product' shapes implied). Severity lower than FC-1 since this is an illustrative tactical-pattern snippet, not the generated-code happy path.
- **suspectedCategory**: 2b

### discipline-cleancode
**[1]**
- **type**: landmine
- **location**: workspace/reference/discipline-cleancode/reference/final.md:458-460 (mirror dddjango/skills/discipline-cleancode/references/final.md:448-450)
- **description**: CONFIRMED. §3.7 '부수 효과를 일으키지 마라'의 '좋은 예'(권장 리팩터링)인 check_password가 `-> bool`로 선언됐으나 본문은 `return user and verify(user.encoded_phrase, password)`다. find_user가 no-user 경로에서 falsy(None)를 반환하면 `user and ...`가 좌측 피연산자에서 단락 평가되어 그 None을 그대로 반환한다. 실측: happy-path→True(bool), wrong-password→False(bool), no-user→None(NoneType, isinstance bool=False). 즉 시그니처가 약속한 bool이 아닌 None을 산출하는 반환형 landmine(FC-1과 동형: 시그니처↔실제 산출 타입 불일치). 아이러니 검증: 같은 절의 '나쁜 예'(if user and verify: return True / return False)는 세 경로 모두 정상 bool(True/False/False)을 돌려주므로, '좋은 예'가 '나쁜 예'보다 반환형 정확성에서 오히려 퇴행하며 깨진 패턴을 모범으로 가르친다. find_user의 None 반환은 표준 lookup 관용구라 no-user 경로는 가상이 아니다. 정본·미러(및 codex 미러)가 byte-identical로 동일한 결함을 모범으로 제시. RUBRIC FC-1(치명, 골든 오라클 반환/status 기반)·FC-2(반환/status mutation) 차원과 동형이라 '반환형 하드영역' 서술도 정확.
- **suspectedCategory**: 2b

### implementation-django-web
**[1]**
- **type**: silent-gap
- **location**: workspace/reference/implementation-django-web/reference/final.md:173-184 (§6 Web forms/POST flow), :217-237 (§7 HTMX), :272-288 (§10 acceptance matrix); mirror dddjango/skills/implementation-django-web/references/final.md:163-174, :207-227, :262-278
- **description**: CONFIRMED silent-gap. Adversarial verification: (1) Full-file grep across source, mirror, AND SKILL.md plus a Korean-synonym sweep (오류/예외/실패/충돌/재시도/복구) returns the ONLY exception vocabulary as `raise ValidationError` inside form clean() (source 188/200/206, mirror 178/190/196) — pure presentation-layer input validation. No 500.html/error.html/handler500/re-render-on-service-failure/conflict/transient/retry guidance exists anywhere (negative grep empty). (2) The POST-flow FBV (create_article, source line 102) and HTMX view (like_article, source line 235) call services BARE — no try/except, no error-rendering branch, no comment that these can raise domain/conflict/transient exceptions. (3) The §7 handoff (source line 226) is gated strictly on 'JSON API처럼...Problem Details가 필요해지면' → ninja/api. Verified the ninja reference's purpose (implementation-django-ninja final.md line 7) owns application/problem+json JSON error mapping and its entire handler apparatus (lines 130/434/443/507/528) is JSON-only; it structurally CANNOT own a server-rendered HTML error page. So the server-rendered error path is genuinely orphaned, not legitimately handed off. (4) §10 matrix's only form row (source 283/mirror 273) covers GET/valid POST/invalid POST/redirect/form error — input validation only, never 'service raised conflict → rendered error path'. (5) This is the same exception-translation-at-adapter family as ACL-EX2/error-centralization, which is a documented recurring eval FAILURE family (confirmed present in workspace/eval/rubric/EVAL-METHOD.md, RUBRIC.md, and multiple results/*.md) — here unaddressed for the web adapter. All cited file:line anchors verified exact (source §6=173,§7=217,§10=272; mirror §6=163,§7=207,§10=262). Guidance is ABSENT (not present-but-wrong, not a drift). Category 2a, mirroring the ACL-EX2 anchor.
- **suspectedCategory**: 2a

### implementation-python
**[1]**
- **type**: landmine
- **location**: workspace/reference/implementation-python/reference/final.md:2559 (mirror: dddjango/skills/implementation-python/references/final.md:2549)
- **description**: CONFIRMED. §28.2 Template Strings example: signature `def safe_sql(template: Template) -> str:` (canonical L2559 / mirror L2549) is contradicted by its body `return "".join(parts), params` (canonical L2568 / mirror L2558), which packs a 2-tuple `tuple[str, list]` — NOT a str. The call site `query, params = safe_sql(...)` (canonical L2571 / mirror L2561) unpacks two values, which only works because the real return is a tuple. Mechanism proven: (1) runtime confirms `return a, b` yields a 2-element tuple (str, list); (2) mypy --strict — the exact mode this skill mandates in §23.1 (`strict = true`, L2341) and §23.2 (pyright `typeCheckingMode: strict`, L2366) — on a faithful reproduction emits `error: Incompatible return value type (got "tuple[str, list[Any]]", expected "str") [return-value]` plus a downstream `error: Unpacking a string is disallowed [misc]` at the call site. Adversarial counter-checks failed to exonerate: PEP 563/649 deferred annotation evaluation (the §28 topic itself) does NOT suppress the error. Correct annotation is `-> tuple[str, list]` (precisely `tuple[str, list[Any]]`). FC-1-homologous: the skill teaches a 'good example' that immediately fails under its own self-mandated strict type checker. Canonical and mirror are byte-identical (only line offsets differ), so this is a genuine canonical-source defect, not drift.
- **suspectedCategory**: 2b

### implementation-test
**[1]**
- **type**: silent-gap
- **location**: workspace/reference/implementation-test/reference/final.md §19.2 (2413-2438) and §20 (2485-2658); mirror dddjango/skills/implementation-test/references/final.md §19.2 (2413-2428) / §20 (2485-2658)
- **description**: CONFIRMED. The error-translation / exception-mapping CONTRACT TEST recipe is genuinely absent from implementation-test. Whole-file grep returns ZERO signals for 503, application/problem+json, catch-all, OperationalError, 'database is locked', or StockConflict. The lone 409 (§20.1, source:2544) is an idempotency payload-mismatch conflict ({400,409,422}), not a domain/infra-exception->HTTP-status mapping. §19.2 shows only framework-auto-generated validation failure ({400,422}, empty items). §20.5 proves concurrency CONVERGENCE (asserts stock==3), not error->status mapping. Three repeatedly-failing eval areas have no recipe: (1) domain exception -> correct non-2xx (e.g. StockConflictError -> 409, transient OperationalError -> 503), (2) unexpected catch-all -> application/problem+json (NJ-7), (3) operation-level infra exception (OperationalError 'database is locked') not leaking as raw 500 (ACL-EX2). Adversarial delegation check REJECTED: the analogous owner implementation-django-ninja §9 (lines 717-755) only demonstrates happy-path 201 and validation 422 (same gap); its checklist merely lists 'idempotency replay와 conflict' and 'Problem Details error shape' as topics with no test that drives a domain/infra exception to a status. The §19.2/§20.1 delegation pointers ('follow architecture-api') delegate the contract VALUES, not the test TECHNIQUE; implementation-test is the named owner of test recipes (architecture-db §9.5 final.md:425 points to implementation-test §20.5 for the deterministic concurrency proof, but the error-translation analogue has no recipe to point to). houserules §2 (final.md:144) authoritatively defines this exact error-translation contract (ACL exhaustiveness, transient infra -> retryable 503/409, '500 leak = under-mapping'). Source and mirror are byte-identical, so this is a corpus-level gap (homologous to calibration anchor ACL-EX2/2a), not drift. Note: claimed mirror range was approximate (actual §19.2 mirror ends ~2428, §20 starts at 2485); substance correct.
- **suspectedCategory**: 2a

**[2]**
- **type**: contradiction
- **location**: workspace/reference/implementation-test/reference/final.md:2507 (§20.1) vs :2415 (§19.1); mirror dddjango/skills/implementation-test/references/final.md:2497 vs :2405
- **description**: CONFIRMED. Within the SAME document, same mechanism (wrapping a functional Router via 'from ninja.testing import TestClient; client = TestClient(router)'), adjacent sections, the router import path contradicts itself. §19.1 (source:2415, mirror:2405) uses the 4-layer layout 'from orders.presentation_layer.api.order.router import router'; §20.1 idempotency example (source:2507, mirror:2497) uses the flat legacy path 'from orders.api import router'. Adversarial 'legitimate-alternative' defense REJECTED: the houserules standard tree (final.md:69 and :217) defines the HTTP entry point as '<app>_api_router.py' and adapters under 'presentation_layer/api/'; no flat 'orders/api.py' module exists in the standard tree, so §20.1's path is genuinely off-tree and a coder copying it verbatim produces an unresolvable import. Every OTHER router/controller import in the file (source:2390/2415/2474; mirror:2380/2405/2464) uses the 4-layer path -- §20.1 is the lone flat outlier, consistent with §19 having been revised to the 4-layer/class-controller layout while the §20.1 idempotency block was left on the old flat path. The mirror replicates the identical inconsistency (mirror:2497 vs 2380/2405/2464), so this is a corpus-level contradiction, not drift.
- **suspectedCategory**: 2b

## 정직 / 한계 (박제)
- **N=관측 한정 선택편향**: 관측 23건은 이미 라이브에서 발화·디버깅·수차례 정정된 항목 → 잔여가 비결정으로 수렴하는 게 자연스러움. 미발화 코퍼스 결함은 별개로 존재(잠재 7건이 증거).
- **조정자 과잉정정 기록**: 조정자가 4표본 손수 검토만으로 "대부분 스킬 부족, 비결정 아님"이라 단언했으나, 전수 적대검증은 *관측 한정* 87% 비결정으로 **반전**. 표본 추출의 함정을 박제.
- **ACL-EX2 앵커 STALE 정정**: 보정 앵커 'ACL-EX2=2a(침묵)'는 DR-44 이후 `houserules:144`·ninja §6.2가 침묵을 byte-id로 메워 현재는 **1(비결정)**. 본 분류에 반영.
- **런타임 우열 금지**: N=1·태스크 heaviness 교락 → Claude/Codex 우열 결론 아님.
- **2b 잠재 4건 중 3건(ddd-factory·check_password·safe_sql)은 워크플로 에이전트 실행증명**, 조정자 미재확인 → 정정 착수 시 1단계는 "직접 재현(거짓양성이면 드롭)".
