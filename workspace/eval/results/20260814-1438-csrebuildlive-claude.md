# 채점 결과지 — csrebuildlive-claude (BC 클린룸 리빌드 S3-r1 · 레인 A · ⑤/⑥a)

> **방법**: EVAL-METHOD **v5 frozen** · **identity**: `2026-08-08-tree-revision` + `dddjango-code-json` + `v5-candidate` + dimension ID · **채점일** 2026-08-14 14:57 · **픽스처** `/Users/hyun/Desktop/broccoli-rebuild`(브랜치 `rebuild/standard-tree` · 채점 대상 커밋 `60610e3a` — child_settings 클린룸 재구현·86파일 +2,856 · working tree clean=런-정지 확인) · **런타임** dddjango(Claude Code) **plugin 2.7.0** · 재구현 세션 **Claude Opus 4.8(레인 모델 고정)** · **앵커** `42a904ae` · 기동 HEAD `833a16aa` · 실행 1h58m(12:39:43→14:38:01) · **태스크** 자녀 본인 알림 동의 GET/PATCH 2 유스케이스(`/v1/children/me/notification-consent` · 카탈로그 단일 `ai_message_arrived`·opt-out 기본값 true·미설정=기본값 파생·배치 판정 원자성·last-write-wins upsert·maxProperties 32 DoS 상한·422 두 갈래 · 오류 프로필 **dddjango-code-json**·wire=RFC 9457 problem+json 모양 V1 축자).
> **라운드 문맥**: `2026-08-12-bc-rebuild-protocol.md` S3-r1(자율 반복 — Herdr 기동·인풋 대행). 이 라운드의 «삭제된 직전 판»은 V1 이 아니라 **라운드 1′ 재구현 산출물**(spec.md 서두 ⑥ 채점 주석)이며 V1 원본은 `1c02d89a^` 에 있다 — 옛 테스트 시나리오 대조는 V1 기준(부록 A).
> **범례**: ✅ PASS · ❌ FAIL · 🟡 WEAK/경미 · ⏸️ 보류/미인증 · ➖ N/A.
> **⚠️ 필수 단서**:
> - **결정 레인 = 하네스 실측 봉인 값**(⑤ 3축·registry_gate 차분·migration_gate·bc_registry_run — 재실행 불요 지시). **의미 레인 = 독립 AI 채점자 1인**(재구현·재료 준비 비참여·read-only 정독) — `N_grader=1`(κ 미보고). 형식 eval «완료» 대용 아님.
> - **FC-1 골든 행위표: child_settings S3-r1 분 미확보**(`workspace/eval/golden/` 실측 — billing 분만 존재) — FC 축은 대체 관측·동결 방법의 FC 인증 아님(⏸️). 라운드 3 psrebuild 「남는 결점 ⑶」과 동일 공백 지속.
> - **클린룸·세션 감사 = 하네스 관측 원자료**: STOP 0 · 판단 개입 0 · 도구-실행 승인 왕복 ~32회 전부 read-only 탐색/허용 경로 생성/검증 명령(설계 결정 대리 답변 0).
> - **자기보고 불신 집행**: 완주 커밋 주장 4건(6895 green·귀속 0·2xx shape 일치·regi #15 pass)은 하네스 봉인 실측과 전부 일치. 완주 보고의 **자기 판정 2건**은 조정자가 산출물·표준 문면으로 독립 검증(조정자 노트 ②·③).
> - **fixture 도구 환경(env/produced/used)**: env=픽스처 `.venv`(python 3.14·pytest-django·factory_boy 기존 스택) · produced=이번 런 신규 테스트 도구 추가·핀 0(기존 재사용) · used=pytest 함수형(`def test_*`+`@pytest.mark.django_db`)·factory_boy(`test/factories/notification_consent_model_factory.py:21` `DjangoModelFactory`)·fake ABC(`test/fake/__init__.py`)·`unittest.mock`/`TestCase` 출현 0(grep 실측) · 조정자 추가 도구 0.

## 종합 판정 (사전식 집계)

| 단계 | 결과 |
|---|---|
| ① C 마스크 | **MQ0=Y**(앵커 `42a904ae` 가 1′ 산출물 삭제·이 런이 재생성 — 승인 트랙) → **MQ1=Y ∧ MQ2=N**(카탈로그 멤버십·기본값 파생·배치 원자성 판정 적재) → §0 전부 강제 + 도메인 실코드 의무 → **충족** |
| ② 치명 게이트 | **FAIL 0** — SD-1~7·SH-1·2·3·4·7·NJ-1·2·Q-4 전부 통과(의미 레인 포함·치명 후보 0) |
| ②.5 실질성 관문 | degenerate 0 — 도메인 판정 실코드·비-vacuous 단언 실재(빈 골격은 §632-(2) 의무 골격뿐) |
| ③ 비치명·의미변종 | `[결정PASS∧의미FAIL]` 0 — 관찰 4건은 전부 해석 지점/주의 보고(아래 메타) |
| ④ TIER-Q 등급 | **상** — FAIL 0 · WEAK 1(Q-7 — e2e 모듈 상수·헬퍼 무주석, parent 동형) |

> **한 줄 요지**: **⑤ 3축 전부 green + 치명 0 + Q 상 — 라운드 3 레인 A(parent_settings)에 이은 2회 연속 문면 완전 통과.** 라운드 1′ 이 같은 BC 에서 낸 귀속 23건의 결함 축(§SD-6 UoW 우회·배선 답습 #107-110/#431/#437·잎 import·#287·테스트 규율 #385/#387/#390/#420)이 **전 축 재발 0**으로 소멸했고, G2 blocker 2건(#51·#81)을 빚 가필 없이 재작업으로 소멸시켰다(라운드 2 «빚 자가 확장»의 정반대 — F3 작동 지속). spec.md:73-74 의 wire/소유 이중 문면은 실물 3점 근거의 결합 판독으로 해소·구현했다(조정자 노트 ③ — 레인 B STOP 과 상호 대조).
> **2차원 라벨**: (정적: 준수 — FC ⏸️ 단서) × (라이브: 미검증 — 위반주입·EP probe 라운드 범위 밖).
> **라운드 판정: ⑤ 문면 통과 · ⑥a 치명 0·Q 상** — **결정 주체 관측: 자기 해석 2(둘 다 실물 근거·검증 일치 — 조정자 노트 ②·③) · 자가 승인 0(게이트 입력은 요청문 위임 범위 내·비위임 침범 0·빚 가필 0) · STOP 0**. 스트릭 카운트(S3 N=2 기점)는 사용자 몫.

## ⑤ 기계 3축 (하네스 실측 봉인 · python 3.14)

| 축 | 결과 |
|---|---|
| **A축** openapi shape | ✅ **성공(2xx) 경로 정규화 diff 0** — `api_shape_pre_success.json` 대비 byte 등가(51 paths 판·GET/PATCH 200·maxProperties 32·propertyNames enum) |
| **B축** pytest | ✅ **6895 passed · red 0**(154s) — 앵커 baseline 6855 대비 **+40 = 신규 테스트 40 전부 green**(조정자 검산: unit 17·integration 13·e2e 10 = 40 일치) |
| **C축** | registry_gate(`--anchor 42a904ae`·정본 빚 파일) **귀속(N∖L) 0·exit 0** · migration_gate child_settings **잔존 0** · bc_registry_run 21 green/6 red — red 발화 전부 중앙·브라운필드(#493 타입·#437·#431/#441 urls = 앵커 기존분·차분 0 실증) · **child 경로 발화 = `#12` pairing authentication import 1건뿐 = 빚 목록 내** |

- **빚 규율**: 앵커 빚 파일 3행(#12/#385/#389 `application.pairing`) 중 실발화 **#12 하나**. #385/#389 발화는 e2e 인증 arrange 를 **프로덕션 HTTP 엔드포인트 인라인**(accounts 소셜로그인→자녀 생성→pairing QR→claim, `test/e2e/test_notification_consent_api.py:107-166`)으로 지어 원천 소멸 — 타 BC test 모듈 import 0. **빚 파일 가필 0 · `docs/**` 무접촉**(F3 준수).
- **G2 blocker 2건 소멸 궤적**(verification-report.md §G2): ⑴ **#81** 루트 `open_host_service/` — 표준 BC-root 7칸 실측(`standard_tree.bc_root()`)으로 parent 의 루트 OHS 를 «앵커 grandfathered legacy»로 판별·**답습 거부**(빈 placeholder 삭제·design §A.5 정정 — 전역 CLAUDE.md 「legacy 배치는 규약이 아니라 빚」 문면 그대로 작동) ⑵ **#51** e2e 의 `application.pairing.test.*` import — 목록 밖 귀속을 빚 수용이 아니라 재작업으로 해소. 재차분 귀속 0 · 수렴 회로 준수(같은 게이트 반송 ≤2).

## A. TIER-S 척추 — S-DDD (의미 레인 정독 + 조정자 grep)

| ID | Result(줄 인용) | 결정 | 의미 | 종합 | 치명 |
|---|---|---|---|---|---|
| SD-1 판정소유 | 멤버십 단일출처 `value_object/notification_category.py:47-53`(`try_resolve`)·`:55-63`(`resolve`→도메인 예외 승격) · 기본값 정책 `:31-36`+`_DEFAULT_ENABLED:67-69` · 배치 원자성 validate-all→apply-all `notification_consent.py:76-90` · 미설정=기본값 파생 `from_stored:56-65` — 전부 domain_layer 실재 | ➖ | ✅ | ✅ | ✅ |
| SD-2 프로덕션 호출 | `update_notification_consent_use_case.py:57-64` 조회→`apply_changes`→`with uow: save(aggregate)` · `get_…use_case.py:31-37` 조회→투영 — `.update()`/raw SQL 우회 0·죽은 도메인 메서드 0(grep 전수) | ➖ | ✅ | ✅ | ✅ |
| SD-3 무복제 | driven repo `find_by_child` 는 `filter(child_id=)` 식별뿐 · `save` 의 `bulk_create(update_conflicts=True, unique_fields=[…])` = 경합 가드 허용 범위(ON CONFLICT upsert) · 모델 `choices` 는 VO 파생(`notification_consent_model.py:30-33` — #326 파생 전용 예외·복제 아님) · DB CHECK·컬럼 기본값 0(도메인 소유 — 스키마 integration 이 sparse 를 단언) | ✅ | ✅ | ✅ | ✅ |
| SD-4 애그리거트 경계 | 단일 애그리거트 `NotificationConsent`·1트랜잭션 1애그리거트(`save(consent)` 하나·#287 준수 — 1′ 의 `save_consents` 인자 2개 위반 소멸) · `child_id = BigIntegerField()` ID-값 참조·교차 BC FK 0 | ✅ | ✅ | ✅ | ✅ |
| SD-5 모델 표현력 | VO=StrEnum 불변·command/query/result 전부 `@dataclass(frozen=True)` · 유비쿼터스 명명(consents·apply_changes·pending_changes·UnknownChildNotificationCategory) · 도메인 서비스 미채택(단일 애그리거트 — 빈 placeholder 정당) | ✅ | ✅ | ✅ | ✅ |
| SD-6 계층 순수성 | **domain/application 의 django·ninja·pydantic import 0(조정자 grep 전수 — exit 1 무매치)** — 1′ 치명(`from django.db import transaction` 응용 직결)의 정반대: 트랜잭션은 `application_layer/port/unit_of_work/child_settings_unit_of_work.py`(ABC 계약 셋)→driven `DjangoChildSettingsUnitOfWork` 구현 · result=원시 `consents/categories` 만·HTTP status DTO 0 · status 선택은 controller 직소유(`notification_consent_controller.py:125-129`) | ✅ | ✅ | ✅ | ✅ |
| SD-7 컨텍스트 통신 | 타 BC import = **pairing authentication 1건뿐**(`notification_consent_controller.py:69` — 승인 빚 #12·목록 내), accounts·타 BC import 0(grep 전수) · accounts 는 ID-값 참조(`child_id: int`)만 · e2e 는 타 BC 를 프로덕션 HTTP 로만 소비(#51 재작업) · 인바운드 0 이라 OHS 발행 없음(루트 OHS 답습 거부 — §⑤) | 신호 有(#12×1 — 빚 클래스) | ✅ | ✅ | ✅ |

## B. TIER-S 척추 — S-HR (판 = registry 위임 · 차분 귀속 0 실측)

| ID | Result | 종합 | 치명 |
|---|---|---|---|
| SH-1 컨테이너 | `application/child_settings/` 하위 전수 (#7 exit 0·루트 잔재 0) | ✅ | ✅ |
| SH-2 4계층 | `{driving,application,domain,driven}_layer/` 물리 실재 (#4 차분 귀속 0) | ✅ | ✅ |
| SH-3 골격+거주 명명 | 고정·재등장 칸 빈 실현(entity/event/domain_service/shared_value_object/webhook/cron_job/admin/acl/external_system/domain_bypass_query·`event_router.py`·`event_wiring.py` 0바이트) · `…UseCase.execute(query|command)→result`·`_command/_query/_result` 어휘·`dto` 낱말 0(grep 실측) (#19·#26 발화 0) · **get=`_query` 실코드+`_command` 빈 칸 / update=`_command` 실코드+`_query` 빈 칸 — parent 미러·설계 §A.2 문면과 정합**(조정자 노트 ④) | ✅ | ✅ |
| SH-4 Django앱 위치 | `driven_layer/django_child_settings/{models,migrations}/` · AppConfig `name` 점경로·`label="child_settings"`(`apps.py:11-15`) · INSTALLED_APPS 1행 · 루트 `models.py` 0 | ✅ | ✅ |
| SH-5 ORM 명명 | `NotificationConsentModel` ↔ bare `NotificationConsent` | ✅ | — |
| SH-6 포트/구현 명명 | ABC 개념+역할접미(`NotificationConsentRepository`·`ChildSettingsUnitOfWork`)·구현 기술접두(`Django…`)·`Interface`/`Impl`/약어 파일명 0 | ✅ | — |
| SH-7 포트 선언 위치 | 리포지토리=`domain_layer/notification_consent/notification_consent_repository.py` · 능력 포트=`application_layer/port/unit_of_work/` (#22·#20 차분 발화 0) | ✅ | ✅ |
| SH-8 ACL 분리 | 상류 모델 소비 없음(ID-값 참조만) — `anticorruption_layer/` 빈 placeholder 존치·N/A 성 통과 | ✅ | — |
| SH-9 단일 레이아웃 | `test/` 단일(`tests/` 공존 0) | ✅ | — |
| SH-10 테스트 의미군 | `test/{unit,integration,e2e,factories,fake}` 표준 5분류 · e2e=blackbox HTTP(구현 심볼 import 0 — #390 동형 0) · unit=fake 격리 DB 미기동(#387) · 타 BC test import 0(#385/#51 소멸 실측) | ✅ | — |

## TIER-S(조건부) — S-NINJA

| ID | Result | 종합 | 치명 |
|---|---|---|---|
| NJ-1 스택 | ninja-extra `@api_controller("/children", …, auto_import=False)` + 명시 registrar `register_child_settings_api(api)`(`api_router.py:23-24` — 인자로 받고 프로젝트 api import 0·#108) · urls.py 호출 1행 · plain view/DRF/JsonResponse 0 | ✅ | ✅ |
| NJ-2 얇음 | GET/PATCH 본문 = principal 해석·command 조립·use case 호출·`from_result` 매핑뿐(`:110-115`·`:125-130`) — ORM/수동 파싱/수동 검증/비즈 분기 0 | ✅ | ✅ |
| NJ-3 Schema 분리 | `ChildNotificationConsentPatchIn`/`ChildNotificationConsentOut` 분리 · `from_result` 가 유일한 result→wire 투영(도메인/ORM 직렬화 0) | ✅ | — (강) |
| NJ-4 오류 선언 | 직접 반환 BC status 422 = 같은 BC `UnknownChildNotificationCategoryProblem`(`ChildSettingsErrorSchema`⊂`FrameworkErrorSchema`) `response=` 선언 · framework 400/401/503 은 `FrameworkErrorSchema` 로 문서화만(BC 스키마 거짓 광고 0) · `openapi_extra` 후가공 0 — #5 의 «base 선호» 지적은 parent canon 바이트 동형·차분 귀속 0(메타 ②) | ✅ | — (강) |
| NJ-5 문서화 | GET/PATCH 모두 `summary`+`description`·컨트롤러 `tags` · 반환 타입 `Status[ChildNotificationConsentOut]`/union 명시(`-> object` 0) | ✅ | — (경미) |
| NJ-6 버전 핀 | 기존 스택 준용·신규 도입 0(핀 변경 불요) | ✅ | — (경미) |
| NJ-7 오류 직접 계약 | 좁은 try(application 호출 한 문장 `:123-124`)+구체 except `UnknownNotificationCategory`+무인자 concrete `UnknownChildNotificationCategoryProblem()`+주입 response header 설정+직접 two-arg `Status(422, error)`(`:125-129`) · GET 은 BC 오류 없어 try 없음 · helper/handler/factory/catch-all/raw 응답 0 — catch 대상은 **응용 노출 예외**(use case 경계 번역 `use_case.py:60-61` — parent «#210 응용 예외 번역» canon 동형) · #15 exit 0 실측 | ✅ | — (강) |

## TIER-S(핵심) — FC (대체 관측 — 동결 방법의 인증 아님)

| ID | Result | 종합 | 치명 |
|---|---|---|---|
| FC-1 골든 오라클 | ⏸️ child_settings S3-r1 골든 행위표 사전등록 부재(golden/ 실측 — 라운드 재료 공백 지속) · 대체 관측: A축 diff 0 + spec §1~§3 ↔ e2e 시나리오 1~9 축자 대조 충돌 후보 0 + V1 시나리오 대조 도메인 축 전 커버(부록 A) | ⏸️ | ⏸️ |
| FC-2 비-vacuous | ⏸️ mutation 미실행 · red 신호 실재: 삽입순서 첫 위반 결정성(`test_notification_consent.py:141-152` — 순회 비결정이면 red)·갈래 판별 단언(e2e #4·#5 — `type` 이 BC problem 이면 red)·원자성 부분영속 단언(e2e #7)·last-write-wins(`repository:…reinsert_absorbed`) | ⏸️ | ⏸️ |
| FC-3 도메인 정합 | 기본값 opt-out true·절대값 부분갱신·빈 변경 no-op·배치 원자(유효분 미영속)·last-write-wins·자기 범위 — e2e #1~#9(`test_notification_consent_api.py:186-389`)+unit 실증 · 부호 반전/인과 역전/기본값 역전 0 | ✅ | ✅ |

## C. 기존규약 마스크

MQ0=Y(앵커가 1′ 산출물 삭제→이 런 재생성 — 프로토콜 승인 트랙) → MQ1=Y ∧ MQ2=N → §0 전부 강제+도메인 실코드 의무 — 충족. 배선 touched: `settings/base.py` INSTALLED_APPS 1행 add·`urls.py` import 1행+`register_child_settings_api(api)` 1행 add(`legacy_api_patterns` 스냅샷보다 앞 — split-brain 방어 주석 준수). **기존 행 삭제·이동·재정렬 0 · `api.py` 무접촉(#437) · Placement 닫힌 목록 위반 0.**

## D. TIER-Q 품질

| ID | Result | 종합 |
|---|---|---|
| Q-1 스코프 | 표면=spec 축자·발명 0 — 멱등성 `Idempotency-Key` 는 §G 배너로 표면화 후 **기본 미적용 commit**(대가 양면 병기 — 승인 입력은 자율 조항 위임 범위)·406/415 협상 0·`propertyNames` enum 은 spec §3 명시 지시(발명 아님) | ✅ |
| Q-2 API 계약 | 오류 wire slug/title/detail V1 축자(`bc_error_schema.py:50-55`)·`type`=full URI·4-field problem+json(runtime proof+e2e #6 exact 동등)·`Content-Type: application/problem+json`(V1 중앙 `problem_response` 의 media type 물증과 등가)·framework 갈래 비혼합·A축 diff 0 | ✅ |
| Q-3 §9.6+테스트 실현 | design §D.5 8행 전부(Idempotency 행 «미적용(알려진 한계)» 정직 표기) · 동시성은 **결정적 주입**(선INSERT→재저장 ON CONFLICT 흡수 — Barrier 실스레드 0)·UoW 롤백·스키마 sparse/제약 pin 각각 integration 실현 | ✅ |
| Q-4 메커니즘 [🔴치명] | 커스텀 백엔드/`DatabaseWrapper`/PRAGMA/몽키패치 0 — stock `transaction.atomic()`+`bulk_create(update_conflicts=True)` 뿐(#1 차분 귀속 0) | ✅ |
| Q-5 마이그레이션 | 신규 앱 자기 `0001_initial`(dependencies=[]) · 기존 이력 침범 0 · 재빌드 전제(fresh test DB·표준 파생 `db_table`/`label` 동일 = state-reconcile)를 design §D.2 에 박제 | ✅ |
| Q-6 테스트/TDD | pytest 함수형+`@pytest.mark.django_db`·factory_boy·fake ABC·`unittest.mock`/`TestCase` 0 · 인수(e2e 9 시나리오)가 spec 행위 전수 커버·의미군 분리·40/40 green | ✅ |
| Q-7 경미 | 프로덕션 코드 전수 어노테이션 준수(#11 차분 귀속 0) — 🟡 e2e 모듈 상수(`API`·`CHILD_CONSENT_URL`·`UNKNOWN_CHILD_PROBLEM_BODY` 등)·arrange 헬퍼 무주석(parent e2e 동형 관찰 — 라운드 3 결과지와 동일 흠) | 🟡 |

## 의미적 변종 / backstop-blind 메타

`[결정PASS∧의미FAIL]` = 0. 관찰(위반 판정 아님):

1. **[근거 인용 과대 — 표준 침묵 지점의 «정본» 주장]** 응용 예외 `UnknownNotificationCategory` 의 **command 모듈 동거**를 docstring 이 «implementation-django-ninja §2.2 정본»이라 인용하나(`update_notification_consent_command.py:8-13`), §2.2 문면은 «known domain/application exception 구체 catch»와 «command/Result 는 application layer DTO 에서 import»까지만 말하고 **응용 예외의 홈 파일은 지정하지 않는다**(조정자 표준 정독 — 오히려 §2.2 예시는 도메인 예외 직접 import: `references/final.md:149-150`). 배치 자체는 합리(#210 만족·응용층 소유·parent canon 동형)·위반 아님 — 단 이 지점은 **기수확 #210↔#95/NJ-7 충돌**(라운드 3 메타 ①)의 같은 축이며, 수정 사이클에서 «응용 예외 홈» 문면을 표준에 명문화할 때 이 canon 을 입력으로 쓸 것.
2. **[#5 base-선호 지적 vs concrete 선언 canon]** `check-openapi-error-declaration` 직접 실행이 child 422=concrete 선언에 «base 선호»를 지적(exit 2)하나 parent 컨트롤러와 바이트 동형·차분 귀속 0 — 검사기 문면과 확립 canon(두 라운드 연속) 사이의 미세 간극. NJ-4 판정엔 무영향(concrete 도 같은 BC 스키마).
3. **[캡슐화 완화 — 설계 승인 가드]** driven repo 가 `consent._events` 사적 필드를 직접 읽고(`repository/notification_consent_repository.py:44`) 테스트가 주입(`:…save_raises_when_unpublished_facts_remain`) — #545 record→pull→publish 백스톱의 정당 실현 주장(설계 §B.1 명문)·parent 동형. 위반 판정 아님·관찰 유지.
4. **[관측 불가 계약의 정직한 한계]** 카탈로그가 단일 카테고리라 «선언 순서(정렬 금지)» 계약의 고유 실패가 관측 불가 — 입장 표가 스스로 «카테고리 ≥2 에서 재심»으로 박제(design §E). GET e2e 는 exact 리스트 단언으로 최대한 pin.

## 조정자 노트

- **① 세션 감사(하네스 원자료 + 산출물 교차)**: STOP 0·판단 개입 0·승인 왕복 ~32회 전부 기계적(설계 대리 답변 0). 클린룸 위반 신호 0 — request.md 금지 축(git 이력 열람) 관련 관측 없음·e2e 는 스스로 «clean-room: 옛 구현/테스트 미열람» 선언·V1 대조(부록 A)에서 복제 흔적 0(명명·분해·단언 형태 전부 상이 + V1 에 없는 초과 커버 5건).
- **② 자기 판정 검증 ⑴ — 게이트 자동 승인**: 요청문 자율 조항은 «게이트의 승인 입력»만 위임. 실제 궤적: G0 빚 질문=발화 조건 미충족(빚 0 실측 — refactor-scope 27종 표)·G1=§G 배너(멱등성) 기본 미적용 채택(위임 범위·보수적 기본값)·G2 blocker 2건=승인이 아니라 **재작업으로 소멸**(빚 가필 0·허용 경로 내). 비위임 7항(STOP·blocker 수용·빚 목록 밖 수용·경로 밖 변경·scope 사후 개정·G0 ⓐ 자기선택) 침범 0 — **자가 승인 0 판정**.
- **③ 자기 판정 검증 ⑵ + spec.md:73-74 판정(결정 주체 축)**: ⓐ #5/#6/#16 직접 실행 exit≠0 을 «parent canon 바이트 동형·타 BC legacy — child 귀속 아님»으로 자기 분류 → 하네스 차분 실측(귀속 0)·조정자 정독과 **일치**(verification-report 에 근거 전수 기록 — 자기 해석 1로 계상하되 검증 통과). ⓑ **spec :73-74 wire/소유 이중 문면**: 레인 A 는 «wire=RFC 9457 problem+json 모양(V1 축자) + 소유=code-json controller 레시피»의 **결합 판독**으로 해소(design §F slot 3 명문). 조정자 검증 — 실물 3점이 이 판독을 지지: ⑴ spec §3 자체가 D3 개정 주석으로 두 축을 분리 지정 ⑵ 공용 `FrameworkErrorSchema` 가 «RFC 9457 problem+json canonical core»(framework 실물 — code-json 프로필의 공통 스키마가 이 저장소에선 problem 모양) ⑶ V1 중앙 `problem_response` 가 `content_type="application/problem+json"`(1c02d89a^ 실측) → controller 의 주입 response header 설정이 V1 wire 등가. **밖에서 보이는 wire 는 spec 이 slug/title/detail·V1 축자로 못박아 판독 간 갈림 없음 → STOP 요건(«밖에서 보이는 결과가 갈리는 물음») 비해당 — 자기 해석 1로 계상·정당 판정.** 레인 B 의 같은 지점 STOP 과 이 판독은 상호 배타가 아니라 «문면이 두 번 읽게 만든다»는 재료 결함 신호의 양면 — spec §3 서두 한 문장(«problem+json 은 wire 모양이고 소유·레시피는 code-json» 선언문)을 앞세우는 재료 보강 후보.
- **④ 하네스 관측 1건 확인 — command/query 스캐폴드**: 최종 산출물 실측 — get=`get_notification_consent_query.py` 15줄 실코드+`get_notification_consent_command.py` 0바이트, update=`update_notification_consent_command.py` 28줄+`update_notification_consent_query.py` 0바이트. **표준 골격은 두 종류 파일을 상존시키고 미사용 종류가 빈 칸**(parent 미러 바이트 패턴 동일·design §A.2 «빈 placeholder — get 은 query 를 씀» 문면 정합) — 정반대 관측은 «미사용 칸이 빈다»의 오독으로 판정. 명세·표준·산출물 3자 정합 확인.
- **⑤ 1′ 결함 축 전수 대조(같은 BC 재라운드의 핵심 물음)**: SD-6 UoW 우회(django 응용 직결) → **포트+driven 구현**으로 소멸 · 배선 답습 #107-110(top-level 등록·전역 api import) → 표준 registrar+`auto_import=False`+인자 주입 · #431/#441/#437 → urls 명시 호출·api.py 무접촉 · #96/#326 잎 import → VO 파생 전용(스키마·모델 모두 단일출처 파생) · #287 → `save(consent)` 하나 · #385/#390/#420 → e2e 프로덕션 인라인·blackbox·새 도출 · #387 → unit fake 격리. **귀속 23→0.**
- **⑥ 벽시계**: 1h58m — parent 5h14m 대비 대폭 단축(재료 결함 지뢰 0 + parent canon 존재 + v2.7.0 레버). 속도-성능 트레이드오프 신호 없음(치명 0·Q 상 유지 — speed-plan 실측 기입 재료).
- **⑦ 남는 결점(코드 아님 — 수확 큐행)**: ⑴ FC-1 골든 사전등록 재료 공백 **3라운드 연속**(billing 분만 존재 — S3 자율 반복이면 라운드 준비 절차에 골든 생성 단계 명문화 필요) ⑵ spec :73-74 이중 문면(위 ③ — 레인 B STOP 재료) ⑶ «응용 예외 홈» 표준 침묵+canon «정본» 인용 과대(메타 ① — #210↔#95 수확 건과 병합 처리) ⑷ #5 base-선호 문면 vs concrete canon 간극(메타 ②).

## 부록 A. 옛 테스트 시나리오 대조 (기준 = V1 원본 `1c02d89a^` · ⑥ 채점 주석)

V1 테스트 24건(acceptance 12·unit 12) ↔ 신규 스위트 40건 대응:

| V1 시나리오 | 신규 대응 | 판정 |
|---|---|---|
| get_unset 200 기본값(+no_audience) | e2e #1(exact 동등 — Out 스키마가 2필드뿐) | ✅ 커버 |
| patch 토글·영속 / retoggle 절대값 | e2e #2(off→GET 영속→on 재토글) | ✅ 커버 |
| empty patch 200 무변경 | e2e #3(빈 맵+필드 생략 2형·후속 GET) | ✅ 초과 커버 |
| unknown/타 BC 코드 422 child slug | e2e #6(exact 4-field·problem+json 헤더) + unit `resolve` 타 BC 코드(`child_report`) | ✅ 커버 |
| non-bool 422 validation | e2e #4(“yes”·1 두 형·갈래 판별·비영속 확인) | ✅ 초과 커버 |
| oversized 422 validation | e2e #5(33키·갈래 판별 — BC problem 아님 단언) | ✅ 초과 커버 |
| 미인증 401 / 부모 토큰 401 | e2e #8×2(+WWW-Authenticate)·#9(GET/PATCH 양경로) | ✅ 커버 |
| mixed batch 원자·child slug | e2e #6+#7(유효분 미영속 GET 재확인) | ✅ 커버 |
| **malformed JSON 400** | **직접 대응 없음** — framework 소유(spec §3 «BC 는 선언만»·PATCH `response` 400 선언은 실재) | 🟡 유일 미커버 smoke(위반 아님 — 중앙 계약 축) |
| unit: 카탈로그·기본값·resolve 계열 | unit category 6건 동등+`try_resolve` 신규 | ✅ 커버 |
| unit: from_stored/default_for·원자성 | unit consent 8건(+pending 델타·삽입순서 결정성 — V1 에 없음) | ✅ 초과 커버 |
| unit: use case 3건(mocker) | unit use case 3건(fake ABC — 동일 3 시나리오) | ✅ 커버 |
| (V1 에 없음) | UoW integration 3·스키마 integration 3·repo 가드/이웃 무접촉 | — 신규 초과 |

복제 흔적 0(파일 분해·명명·arrange 방식·단언 형태 전부 상이 — V1 은 helper 파일+mocker, 신규는 인라인 arrange+fake ABC). V1 `choices` 투영 unit 은 구조 변경(VO `choices()` 메서드 소멸·모델 인라인 파생)으로 대응 무의미.

## 처분 제안 (사용자 결정 입력)

1. **통과** — ⑤ 3축 green·치명 0·Q 상·결정 주체 깨끗(자가 승인 0·STOP 0·빚 가필 0). S3 «연속 무수정 통과» 스트릭 카운트 적립 후보(레인 A 기준 2연속 — 기점·계상은 사용자 몫).
2. **재료 보강 후보(다음 라운드 전)**: ⑴ FC-1 골든 행위표를 라운드 준비 절차의 필수 산출물로 명문화(3라운드 연속 공백) ⑵ spec §3 서두에 wire-모양/소유-레시피 분리 선언 한 문장(레인 B STOP·레인 A 판독 부담의 공통 근원 제거).
3. **플러그인 수정 후보(수확 큐 병합)**: ⑴ «컨트롤러가 catch 하는 응용 예외의 홈» 표준 문면 신설 — 기수확 #210↔#95/NJ-7 충돌 정본 결정에 parent/child 2회 canon(command 모듈 동거)을 입력으로 ⑵ #5 base-선호 문면과 concrete 선언 canon 정합.
