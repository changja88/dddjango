# 채점 결과지 — csrebuildlive-claude (BC 클린룸 리빌드 라운드 1′ · ⑤/⑥a)

> **방법**: EVAL-METHOD **v5 frozen** · **identity**: `2026-08-08-tree-revision` + error profile(아래 단서) + `v5-candidate` + dimension ID · **채점일** 2026-08-12 · **픽스처** `/Users/hyun/Desktop/broccoli-rebuild`(brownfield 워크트리 · 브랜치 `rebuild/standard-tree` · 채점 대상 커밋 `6dedbfd0` — child_settings 클린룸 재구현, 입력은 spec.md + api_shape_pre.json + request.md 뿐) · **런타임** dddjango(Claude Code) **plugin 2.1.0** · 재구현 세션 Claude Opus 4.8 · **태스크** 자녀 본인 알림 동의 GET/PATCH 2 유스케이스(카탈로그 opt-out 기본값 · 배치 원자성 · 미설정=기본값 · last-write-wins upsert).
> **라운드 문맥**: `workspace/plan/2026-08-12-bc-rebuild-protocol.md`의 ⑤ 기계 3축 + ⑥a 평가를 겸한다. 라운드 1(`ad27fa3b` — V1 트리 재생산·불통과) 후 플러그인 v2.1.0(P1′ 트리 답습 발본색원 · P2 검사기 호출 계약 · H1 shape 정규화)으로 재기동한 재라운드다.
> **error profile 단서**: v5 동결 identity 의 profile 은 `dddjango-code-json`(greenfield 8벌용)이나, 이 픽스처의 오류 계약은 **확립된 RFC 9457 중앙 problem+json**(08-04 API-error 계약의 preserve-established — 결정 레인 `--error-profile auto` 가 검출)이다. 오류-소유 축(SD-6 후반·NJ-4·NJ-7·Q-2)은 **auto 모드 검사기 3종 + 확립 계약 문면**으로 판정하고 code-json 문면(controller 직접 `Status(error)`)을 강요하지 않는다 — 준거는 08-04 선행 계약이며 기준 변경이 아니다.
> **범례**: ✅ PASS · ❌ FAIL · 🟡 WEAK/경미 · ⏸️ 보류/미인증 · ➖ N/A.
> **⚠️ 필수 단서**:
> - **결정 레인 = empirical 전수**(⑤ 3축 + shadow registry 27종 — 조정자 실측·봉인). **의미 레인 = 조정자 read-only 정독 1인** — `N_grader=1`, **blind 미집행**(리빌드 라운드 판정용 — 형식 eval "완료" 대용 아님).
> - **FC-1 골든 사전등록 부재**(조정자가 코드 기열람 — 사전등록 불가) · **FC-2 mutation 미실행**. FC 축은 대체 관측(A축 shape diff 0 + 스위트 실측)으로 보고하며 **동결 방법의 FC 인증이 아니다**(⏸️).
> - **클린룸 감사(transcript 실측)**: 금지 접근 0 — `git show/log` 3건 전부 자기 커밋·HEAD 확인, 옛 구현 해시(`1c02d89a`·`ad27fa3b`)·eval_ai 접근 0. **자기보고 불신 집행**: ④ 커밋 메시지의 주장(7193 green·diff 0·skeleton clean)을 전부 독립 재실측했다.
> - **도구 환경**: 픽스처 `.venv`(python 3.14 · pytest-django) — 이번 런의 신규 테스트 도구 추가·핀 0(기존 스택 재사용). 조정자 추가 도구 0.

## 종합 판정 (사전식 집계)

| 단계 | 결과 |
|---|---|
| ① 마스크 C | **MQ0=Y**(기존 BC 삭제-후-재생성 — 라운드 프로토콜의 승인 트랙) → 대체 코드로 취급, **MQ1=Y ∧ MQ2=N**(카탈로그 멤버십·기본값·배치 원자성 판정 적재) → §0 전부 강제 + 도메인 실코드 의무 |
| ② 치명 게이트 | **FAIL 1 — SD-6 계층 순수성**: `application_layer` 가 `django.db` 를 직접 import(포트 우회) → 픽스처 전체 FAIL, 사전식 종료 |
| ②.5 실질성 관문 | (참고) degenerate 0 — 도메인 판정 실코드·비-vacuous 테스트 실재 |
| ③ 비치명 의미변종 | (참고) 역방향 변종 1군(#390: 결정 FAIL ∧ 의미 PASS — 검사기 사각) · 비치명 흠 다수(아래 표) |
| ④ TIER-Q 등급 | 미산출(치명 종료) — 참고 카운트: WEAK 2(Q-6·Q-7) · FAIL 0 |

**2차원 라벨**: **(정적: FAIL) × (라이브: 미검증)** — P1a/P2/P3 위반주입 트랙은 미수행(리빌드 라운드 범위 밖).

**라운드 판정: ⑤ 불통과 (C축 red)** — 연속 무수정 통과 카운트 0 유지.
- **A축 ✅** 계약 모양 등가: openapi shape diff **0** (pre = x-date 정규화판 · 51 paths).
- **B축 ✅** 전역 `make test` **7193 passed · exit 0** (재구현 스위트 12파일 포함).
- **C축**: `migration_gate` — **child_settings 잔존 0 ✅ (V2 표준 트리 달성 — 라운드 1의 V1 재생산과 대비·v2.1.0 P1′/P2 의 성공 자 충족)** · `bc_registry_run`(shadow · 27종) — **exit 2 ❌**: green 18 · red 9, **child_settings 귀속 blocker 23건**(비귀속 216건은 baseline 잔존 — 아래 분리표).

## 결정 레인 (empirical · 조정자 봉인)

| 검사 | 결과 |
|---|---|
| A축 openapi_shape diff | **0줄** (pre ↔ post 완전 일치) |
| B축 make test | **7193/7193 green** (173.77s) |
| C축 migration_gate | child_settings **0건** (전체 66건 = 전부 legacy 15 BC) |
| C축 registry 27종 (shadow: BC+framework+`<project>`) | **green 18 · red 9** — `#4 skeleton`(6건 전부 비-BC baseline) · `#6 context-isolation`(14) · `#11 annotation`(150건 전부 비-BC) · `#12 test-config`(9) · `#16 composition-root`(53) · `#17 db-table`(1) · `#20 transaction-boundary`(2) · `#23 event-publish`(2) · `#27 business-vocabulary`(3) |
| 귀속 분리 | blocker 총 239 = **child_settings 귀속 23** + baseline 잔존 216(타입 미주석 150 · api.py/urls.py 옛 배선 ~60 · framework 고정 칸 부재 3 · celery.py 부재 · openapi_schema/response_policies 위치 2 · prod 약어) |

**child_settings 귀속 23건** (규칙 축약): 층 격리 `#2`/`#4`(application `django.db`) · `#96`×2(driving schema 잎→domain import) · `#326`(django 잎→domain VO import) · 배선 계약 `#107`/`#108`/`#109`(api_router: 등록 함수 0·전역 api import·top-level 등록) · `#110`(auto_import 미차단) · `#431`/`#441`(urls.py 부작용 등록) · `#437`×2(api.py 에 BC 예외 import) · 쓰기 어휘 `#287`(`save_consents` 인자 2개) · 테스트 규율 `#385`×2(타 BC test import) · `#390`×5(입구 미검출 — 사각, 아래 메타) · `#387`(unit 이 DB 마킹) · `#420`(BC 안 인증 테스트 파일).

## A. TIER-S 척추 — S-DDD

| ID | Result(조정자 검증 · 줄 인용) | 결정 | 의미 | 종합 | 치명 |
|---|---|---|---|---|---|
| SD-1 판정소유 | `domain_layer/notification_consent/notification_consent.py:55-73` `apply_changes` validate-all-then-apply-all(부분 변경 없음) · `value_object/notification_category.py:40-48` `resolve` 멤버십 판정·`:28-30` `default_enabled` 도메인 소유 | ➖ | ✅ | ✅ | ✅ |
| SD-2 프로덕션 호출 | `update_notification_consent_use_case.py:40-44` load→`apply_changes`→save · `get_…use_case.py:32` — 죽은 도메인 메서드 0 | ➖ | ✅ | ✅ | ✅ |
| SD-3 무복제 | driven `repository/notification_consent_repository.py:56-61` upsert 는 `ON CONFLICT` 경합 가드만 — 비즈 조건 SQL 0 · 기본값 채움은 도메인 `from_stored`(`:36-39` 는 위임만) | ✅ | ✅ | ✅ | ✅ |
| SD-4 애그리거트 경계 | 단일 애그리거트(NotificationConsent) · `models/notification_consent_model.py:25` `child_id = BigIntegerField()` — 타 BC FK 없는 ID-값 참조 · 1트랜잭션 1애그리거트(#287 은 쓰기 «어휘» 위반이지 복수 애그리거트 쓰기 아님 — Q-7 로) | ✅ | ✅ | ✅ | ✅ |
| SD-5 모델 표현력 | VO=`StrEnum`(불변)·기본값 정책 단일 출처 `_DEFAULT_ENABLED` · 유비쿼터스 명명(consent·category·enabled) · 재구성 팩토리 `from_stored`/`default_for` | ✅ | ✅ | ✅ | ✅ |
| **SD-6 계층 순수성** | **`update_notification_consent_use_case.py:16` `from django.db import transaction` · `:43` `with transaction.atomic()` — application 이 framework 를 직접 import(트랜잭션 포트 우회 — `application_layer/port/unit_of_work/` 칸은 빈 채 존재하는데 안 씀)**. HTTP 무지 자체는 유지(#2 가 잡은 것은 django). 오류-소유 축은 확립 중앙 계약(preserve)이라 FAIL 사유 아님 | ❌ `#2`/`#4` | ❌ | **❌** | **❌ 치명** |
| SD-7 컨텍스트 통신 | 타 BC `domain_layer`/`driven_layer` import 0(결정 grep) · pairing 인증 소비는 확립 입구 경유 + 속성 접근만(`notification_consent_controller.py:44-47`·`:68` — principal 타입 비누수 docstring `:13-15`) — 단 그 경로가 legacy `presentation_layer` 라 루트 실행 `#12`/`#83`(BC 삭제 내성) 신호 존재 · OHS 미이주 세계의 확립 경로로 판정 | ✅(grep)·루트 `#12` 신호 | 🟡 | 🟡 | ✅(FAIL 문면 비해당) |

## B. TIER-S 척추 — S-HR (판 = registry 위임 · v5)

| ID | Result | 종합 | 치명 |
|---|---|---|---|
| SH-1 컨테이너 | `application/child_settings/` (#7 exit 0) | ✅ | ✅ |
| SH-2 4계층 | **V2 4계층 물리 분리**(domain·application·driving·driven_layer — good_bc 표준 7칸과 일치·V1 이름 0). #4 exit 2 의 6건은 전부 비-BC baseline(framework `broker/`·`pure/`·`test/fake/` 부재 · `<project>` celery.py·잉여 2파일) | ✅ | ✅ |
| SH-3 골격+거주 명명 | 고정·재등장 칸 빈 채 실현(`bc_error_schema.py`·`event_router.py`·`published_event/`·port 칸 — 0바이트 실현) · `<use_case>_use_case.py`/`_command`/`_query`/`_result` 어휘(#19·#26 exit 0) | ✅ | ✅ |
| SH-4 Django 앱 위치 | `driven_layer/django_child_settings/models/`·`migrations/` · `db_table="child_settings_notification_consent"` (#17 red 사유는 위치가 아니라 `#326` 잎 import) | ✅ | ✅ |
| SH-5 ORM 명명 | `NotificationConsentModel` ↔ bare `NotificationConsent` | ✅ | — |
| SH-6 포트/구현 명명 | ABC `NotificationConsentRepository`(domain) ↔ `DjangoNotificationConsentRepository`(기술 접두) — `Impl`/약어 0 | ✅ | — |
| SH-7 포트 선언 위치 | 리포지토리 선언 `domain_layer/notification_consent/notification_consent_repository.py:22` · 능력 포트 칸은 `application_layer/port/` 뿐(트리 밖 port 0 · #22 exit 0). #20 red 사유는 위치가 아니라 SD-6/#287 | ✅ | ✅ |
| SH-8 ACL 분리 | 교차 결합 없음 — `adapter/anticorruption_layer/` 빈 실현·repository 에 번역 혼합 0 | ✅ | — |
| SH-9 단일 레이아웃 | `test/` 단일(공존 0) | ✅ | — |
| SH-10 테스트 의미군 | 의미군 분리 자체는 표준(unit 4·integration 2·e2e 5·fake·factories) — 단 **규율 위반 4군**: `#385` 타 BC test import(`_acceptance_helpers.py:37-48`) · `#387` unit 이 `@pytest.mark.django_db`(`test_update…:28` — SD-6 django.db 의 연쇄) · `#420` BC 안 인증 테스트 파일 · `#390`(사각 — 메타) | ❌ | — |

## TIER-S(조건부) — S-NINJA (HTTP operation 有 → 채점)

| ID | Result | 종합 | 치명 |
|---|---|---|---|
| NJ-1 스택 | ninja-extra `@api_controller`(`notification_consent_controller.py:52`) + `register_controllers`(api_router.py:23) — plain view·DRF 0 | ✅ | ✅ |
| NJ-2 operation 얇음 | `:67-72`·`:90-99` — principal 속성 접근→합성 루트 팩토리→UC `execute`→`from_result` 투영. 비즈 분기·ORM·수동 파싱 0 | ✅ | ✅ |
| NJ-3 Schema 분리 | `ChildNotificationConsentPatchIn`(StrictBool — 강제 변환 차단 `schema_in.py:42`) / `ChildNotificationConsentOut`(`from_result` 원시 투영 `schema_out.py:50-55`) — 도메인 직접 직렬화 0 | ✅ | — |
| NJ-4 오류 OpenAPI 선언 | operation 별 `response={…}` 선언(GET 200/401/503 · PATCH 200/400/401/422/503 — `:56-60`·`:76-82`) · framework status 는 `FrameworkErrorSchema`/`FrameworkValidationErrorSchema` 로(BC schema 거짓 광고 0) · **A축 diff 0 = 옛 계약과 선언 동일** · `openapi_extra`/후가공 0 · #5 exit 0 | ✅ | — |
| NJ-5 문서화 | summary·description·tags 전부(`:52`·`:61-65`·`:84-88`) | ✅ | — |
| NJ-6 버전 핀 | 신규 도입 0 | ➖ | — |
| NJ-7 오류 직접 계약 | 확립 preserve 계약: 중앙 `@api.exception_handler(ChildSettingsError)`(api.py — ④ 가 확립 표에 1행 추가) · controller 는 catch 없는 통과(`:5-11` docstring — 자기 계약 인지 명시) · #15 exit 0(auto). code-json 문면이면 FAIL 이나 준거는 확립 계약 | ✅(profile 단서) | — |

## TIER-S(핵심) — FC (대체 관측 — 동결 방법의 인증 아님)

| ID | Result | 종합 | 치명 |
|---|---|---|---|
| FC-1 골든 오라클 | ⏸️ 사전등록 불가(코드 기열람). **대체 관측**: A축 diff 0(계약 모양= 옛 계약) + spec §3 행위(절대값 영속·빈 맵/필드 생략 no-op·422 두 종·401 네 슬라이스) e2e 5파일 실측 green | ⏸️ | ⏸️ |
| FC-2 비-vacuous | ⏸️ mutation 미실행. 대체 관측: e2e 가 저장 후 GET 재확인(영속 회귀 `test_patch…:37-39`)·기본값↔저장값 구별 unit(`test_update…:45-58`) — vacuous 반증 신호는 있으나 실측 아님 | ⏸️ | ⏸️ |
| FC-3 도메인 정합 | 정독: opt-out 기본값 방향(`default_enabled=True`)·validate-then-apply(부분 변경 없음)·last-write-wins upsert·빈 배치 no-op — 명백 도메인 오류 0 | ✅ | ✅ |

## C. 기존규약 마스크 (적용 메모)

MQ0=**Y** — 기존 child_settings 를 라운드 앵커(`0ee0353f`)가 삭제하고 이 런이 재생성(프로토콜 승인 트랙). 대체 코드로 취급 → MQ1=**Y**(멤버십·기본값·배치 원자성 판정 적재) ∧ MQ2=**N** → **§0 전부 강제 + 도메인 실코드 의무 → 충족**(SD-1). 배선이 닿은 기존 파일(api.py·urls.py·settings)은 touched — 확립 패턴에 1행씩 추가하는 최소 diff(+20줄)였고, 그 확립 패턴 자체가 registry 위반(#437·#441·#431)이라 «답습 vs 표준» 긴장이 배선 축으로 이동했다(메타 참조).

## D. TIER-Q 품질 (참고 — 치명 종료로 등급 미산출)

Q-1 스코프 ✅(spec 밖 발명 0 — `_MAX_CONSENTS=32` DoS 상한도 spec §3 요구) · Q-2 API 계약 ✅(확립 RFC 9457 일관 — A축 diff 0·slug/타이틀 BC 구분) · Q-3 동시성 ✅(race-safe upsert + `test/integration/test_child_notification_consent_concurrency.py` 실재·B축 green) · **Q-4 메커니즘 ✅[🔴치명 통과]**(#1 exit 0 — 커스텀 백엔드/PRAGMA/몽키패치 0) · Q-5 마이그레이션 ✅(신규 앱 자기 `0001` — 라운드 트랙 정당·B축 green) · Q-6 테스트 🟡(12파일·pytest 관용구·fake/factories 실재·전역 green — 단 SH-10 의 규율 위반 4군) · Q-7 🟡(BC 코드 타입 주석 완비(#11 의 BC 귀속 0 — ④ 가 중간 실측 후 6건 자가 수정) — 남은 흠: `#287` 쓰기 어휘·`#96`×2·`#326` 잎 import·`#110` auto_import).

## 의미적 변종 / backstop-blind 메타

- **역방향 변종(결정 FAIL ∧ 의미 PASS) — `#390`×5**: e2e 5파일 전부 «입구 미경유» blocker 인데, 실물은 Django test client 로 HTTP 만 두드리는 blackbox 다(`_acceptance_helpers.py:97-142` 가 client.get/patch 소유). 입구 표지가 **타 BC 헬퍼 import(#385) 뒤에 숨어** 파일 단위 검출이 실패한 것 — `#385` 의 그림자이자 **검사기 사각 카드**(⑦ 재료).
- **배선 답습(이 라운드 최대 발견)**: `api_router.py:5-13` docstring 이 스스로 «확립된 import-time 등록 규약을 보존한다(preserve profile) — parent_settings_api_router.py 동형»이라 적고 `#107`/`#108`/`#109`/`#431` 위반 형태를 선택했다. **preserve-established 는 08-04 오류 wire 계약의 profile 인데, 그 논리가 등록·배선 규율 축까지 확장 적용**됐다 — 라운드 1 «트리 답습»의 배선판. 트리 축은 P1′ 로 닫혔음이 실증됐고(V2 트리 재생산), 답습 압력이 다음 남은 축(배선·잎 import·테스트 재료)으로 이동했다.
- **단일 출처 ↔ 잎 규율 긴장 — `#96`·`#326`**: schema·model 이 카탈로그 enum 을 도메인 VO 에서 파생(`schema_in.py:38`·`model:28` — 리터럴 표류 방지, #18 choices-literal exit 0)하는 대신 잎 import 금지를 위반. 두 규칙이 현 트리에서 동시 충족 불가능한 모양인지 ⑦ 에서 판정 필요.
- backstop-blind: `#12`(pairing.presentation_layer auth import — BC 삭제 내성)는 **루트 실행에서만 발화**하고 shadow(이웃 부재)에선 침묵 — shadow 판정의 알려진 한계로 박제.

## 조정자 노트

- **④ 세션 감사(transcript 실측)**: 클린룸 위반 0. 세션은 **registry 27종을 루트 TARGET 으로 전수 실행**하고 child_settings 귀속까지 스스로 슬라이스했다(P2 호출 계약 준수 — BC 폴더 TARGET 사각의 재발 없음). 귀속 red 중 일부(타입 주석 6건·domain-model 1건)는 그 자리에서 수정했으나, **잔존 23건은 «확립 규약 보존» 논리로 남긴 채 커밋** — 커밋 메시지는 skeleton clean 만 게이트 증거로 인용했다. v2.1.0 게이트 계약(«루트 registry 전체 1회 green 만 증거»)은 brownfield legacy 잡음 아래 문자 그대로 충족 불가하므로, **귀속(attribution) 기준의 계약 공백**이 드러났다(⑦ 처분 재료 — 플러그인 결함 후보).
- **v2.1.0 수정 효과 실증**: 라운드 1 의 실패 축(V1 트리 재생산·BC-폴더 TARGET 조용 통과)은 재발 0 — gate child_settings 잔존 0·V2 표준 7칸·호출 계약 가드 작동. 결함의 «축이 이동»했다: 트리 → 배선/잎/테스트 규율 + SD-6 포트 우회.
- **품질 절대치**: 도메인 모델(SD-1~5)·스키마 계약(NJ 전부)·동시성 대비는 높은 수준 — 치명 1건(SD-6)과 규율 위반 23건이 «파이프라인이 registry red 를 남기고 종료해도 되는가»라는 프로세스 물음으로 수렴한다.
- **다음**: ⑦ 삼분 처분(23건 각각 플러그인/구현/스팩 귀속) → 수정 → 재라운드. ⑥b 사용자 리뷰는 ⑤ 불통과 라운드라 생략 가능(프로토콜 단서).

## 사후 정정 (2026-08-12 — in-place 부기 · lastlive-claude 전례)

- **「spec 결함 0」 판정 정정 → 스팩 결함 1건**: 조정자 노트의 «spec 결함은 0» 은 오판이었다.
  `docs/rebuild/child_settings/spec.md` 의 옛 §3·§5·§6 이 «오류 계약 = 중앙 소유» 를 넘어
  **api.py 매핑 테이블 행 추가라는 «배선 구현»까지 지시**했고(§6 복원 지점 ③ «넷»), 라운드
  1′ 의 api.py +16줄(#437 귀속)은 세션의 일탈이 아니라 이 지시의 집행이었다. 스팩은 wire
  계약만 말해야 한다 — 배선 자리는 트리 축(표준) 소유다. D3 결정(code-json 이주)과 함께
  spec 재작성으로 해소(워크트리 `0908671c`).
- 본 결과지의 나머지 판정(치명 SD-6·정적 FAIL·라운드 불통과)은 불변이다. profile 단서
  (preserve 문면 채점)도 당시 spec·설계 명세 기준으로 유효했다 — 다음 라운드부터 오류 축은
  code-json 문면으로 판정한다(프로토콜 A축 개정 참조).
