# 채점 결과지 — psrebuildlive-claude (BC 클린룸 리빌드 라운드 3 · 레인 A · ⑤/⑥a)

> **방법**: EVAL-METHOD **v5 frozen** · **identity**: `2026-08-08-tree-revision` + `dddjango-code-json` + `v5-candidate` + dimension ID · **채점일** 2026-08-14 00:59 · **픽스처** `/Users/hyun/Desktop/broccoli-rebuild`(브랜치 `rebuild/standard-tree` · 채점 대상 커밋 `e2ede4aa` — parent_settings 클린룸 재구현·29파일 +881/−414) · **런타임** dddjango(Claude Code) **plugin 2.5.0** · 재구현 세션 Claude Opus 4.8(기동 08-13 18:53 KST·완주 커밋 08-14 00:07) · **앵커** `3f14e4f1` · **태스크** parent_settings 부모 푸시 알림 동의(`GET/PATCH /v1/parents/me/notification-consent` · **카테고리 7종**·기본 전부 true·부분 갱신·422 unknown category · OHS `parent_notification_enabled` 동결 계약(top-level `open_host_service/` — spec §4) · 오류 프로필 **dddjango-code-json**).
> **라운드 문맥**: `2026-08-12-bc-rebuild-protocol.md` 라운드 3 레인 A. 요청문=템플릿 v2.5.0(F3 필수 절 5종·빚 가필=승인 위조 조항 포함). 라이브런 중 사용자 경유 개입 2건(승인 대장 `round3-liverun-approvals.md`): ⑴ usage_quota·ai_chat lazy화 최소 스코프 확장 승인 ⑵ STOP 재개=전체 재작업+#210 기각+#51 조건부.
> **범례**: ✅ PASS · ❌ FAIL · 🟡 WEAK/경미 · ⏸️ 보류/미인증 · ➖ N/A.
> **⚠️ 필수 단서**:
> - **결정 레인 = 조정자 empirical 전수**(⑤ 3축·registry_gate·SD-6 grep). **의미 레인 = 독립 서브에이전트 grader 1인**(읽기 전용·git 열람 0·결정 결과 비전달) — `N_grader=1`.
> - **⚠ 인터프리터 사건(이번 라운드 조정자 측 최대 발견)**: C축 1차 실행(python3.9)은 **3.12+ 문법 파일을 검사기 `_parse` 실패로 침묵 스킵**(fail-open — 레인 B controller 로 실증) → **레인 `.venv` python 3.14 로 전수 재실행한 값만 봉인 판정**이다. 이 구멍은 라운드 2 판정 일부를 소급 뒤집는다(조정자 노트 ④).
> - **FC-1 골든 행위표: parent_settings 분 미확보**(billing 분만 존재) — FC 축은 대체 관측·동결 방법의 인증 아님(⏸️).
> - **클린룸 감사(세션 로그 실측)**: 금지 접근 0 — git 명령은 `status`/`add`/`commit` 뿐(이력 열람 0)·V1 원본(`~/Desktop/broccoli-server`) 접근 0·eval 재료 접근 0.
> - **자기보고 불신 집행**: 커밋 메시지 주장(귀속 0·6885 green·diff 0) 전부 독립 재실측 — 아래 ⑤ 표와 전부 일치.

## 종합 판정 (사전식 집계)

| 단계 | 결과 |
|---|---|
| ① C 마스크 | **MQ0=Y**(앵커가 BC 삭제·이 런이 재생성 — 승인 트랙) → MQ1=Y ∧ MQ2=N(카테고리 유효성·동의 전이·기본값 적재) → §0 전부 강제+도메인 실코드 의무 → **충족** |
| ② 치명 게이트 | **FAIL 0** — SD-1~7·SH-1·2·3·4·7·NJ-1·2·Q-4 전부 통과(의미 레인 포함·grader 치명 후보 0) |
| ②.5 실질성 관문 | degenerate 0 — 판정 실코드·non-vacuous 신호 실재 |
| ③ 비치명·의미변종 | 위반 판정 0 — 관찰(아래 메타)은 전부 해석 지점/주의 보고 |
| ④ TIER-Q 등급 | **상** — FAIL 0 · WEAK 2(Q-7 어노테이션 부분·NJ-5 문서 표면) |

> **한 줄 요지**: **⑤ 3축 전부 green — v5 리빌드 라운드 최초의 문면 완전 통과**(A diff 0 · B 6885 passed 신규 red 0 · C 귀속 0·빚 #12 1건 목록 내). 산출물은 라운드 2 «Q 상·치명 0» 수준을 유지하며, 라운드 2 최대 사건(빚 파일 자가 확장)의 정반대 행동 — **빚을 늘리지 않고 재작업으로 #385/#51 발화 자체를 소멸**시켜 승인 빚을 #12 하나로 줄였다(F3 «가필=승인 위조» 조항 아래 정directions 준수).
> **2차원 라벨**: (정적: 준수 — FC ⏸️ 단서) × (라이브: 미검증 — 위반주입·EP probe 라운드 범위 밖).
> **라운드 판정: ⑤ 문면 통과 — 단 ⑥a 는 결점 0 이 아니다(아래 «남는 결점» — 코드 결함 아님·판정 인프라/근거 결함). ⑥b 사람 평가 접수로 라운드 닫힘·스트릭 카운트는 사용자 몫.**

## ⑤ 기계 3축 (조정자 실측 · python 3.14 봉인)

| 축 | 결과 |
|---|---|
| **A축** openapi shape | ✅ **diff 0** — `uv run` schema dump → `openapi_shape.py --success-only` → `api_shape_pre_success.json` 대비 0줄(스코프 확장 lazy화가 2xx 무접촉임을 기계 증명) |
| **B축** pytest | ✅ **6885 passed · 0 failed · 158.56s**(`uv run pytest -q --tb=no` maxfail 없이) — 앵커 기준 **신규 red 0** + 앵커 red 10(notifications 동의-OFF) **green 복귀 관찰** |
| **C축** | migration_gate: **parent_settings 잔존 0**(전체 59=전부 타 BC V1 legacy) · **registry_gate `--anchor 3f14e4f1`(3.14): 귀속(N∖L) 0건 → green** · 이관 빚 1건=#12(`notification_consent_controller.py` → `application.accounts.presentation_layer.authentication`) — 승인 목록 내 · legacy 잔존(L∩L) 5,598·해소 7 · bc_registry_run blocker 11 = #431×10(`broccoli_server/urls.py` V1 잔존 배선 — 앵커 시점부터 존재·차분 밖 legacy)+#12 빚 1 — **task 신규 0** |

- **빚 최소화 실증**: 앵커 빚 파일은 #12/#385/#389 3행(accounts)이나 실발화는 **#12 하나뿐** — 세션이 STOP 재개 후 인증 픽스처를 accounts test helper 비의존으로 재작업해 #385(및 목록 밖이던 #51) 발화를 소멸시켰다(`design-spec.md:39` «승인 빚은 #12 하나만 잔존»·실측 일치). 목록 밖 신규 귀속 0·`docs/**` 무접촉(F3 준수).
- **#51 조건부 승인의 처분**: 조정자 대리 답변은 «accounts 경로면 빚 1행 추가 승인/밖이면 수정»이었으나 세션은 **빚 추가 대신 소멸 갈래를 스스로 선택** — 더 강한 해소.

## A. TIER-S 척추 — S-DDD (의미 레인 grader + 조정자 grep)

| ID | Result | 결정 | 의미 | 종합 | 치명 |
|---|---|---|---|---|---|
| SD-1 판정소유 | 멤버십 판정 `value_object/notification_category.py:59-67`(`resolve`→도메인 예외)·기본값 단일출처 `:72-80` · 전이 2단계 원자(validate-all→apply-all) `notification_consent.py:73-80` · 기본값 채움 `:56-58` — 전부 domain_layer 실재 | ➖ | ✅ | ✅ | ✅ |
| SD-2 프로덕션 호출 | `update_notification_consent_use_case.py:51-59` 조회→`apply_changes`→`with uow: save(aggregate)` — 죽은 메서드·`.update()`/raw SQL 우회 0(grep 전수) | ➖ | ✅ | ✅ | ✅ |
| SD-3 무복제 | 리포 `repository/notification_consent_repository.py:39` filter=parent_id 식별뿐·`:65-70` unique+ON CONFLICT upsert=경합 가드 허용 범위 · 모델 choices 는 VO 파생(복제 아님) | ✅ | ✅ | ✅ | ✅ |
| SD-4 애그리거트 경계 | 1트랜잭션 1애그리거트·`parent_id` BigInt ID-값 참조·FK 0(`notification_consent_model.py:27`) | ✅ | ✅ | ✅ | ✅ |
| SD-5 모델 표현력 | VO=StrEnum 불변·OHS 계약·command/query/result 전부 `frozen=True` · 유비쿼터스 명명(consents·apply_changes·UnknownParentNotificationCategory) | ✅ | ✅ | ✅ | ✅ |
| SD-6 계층 순수성 | **domain/application 의 django·ninja·pydantic import 0(조정자+grader 이중 grep 전수)** — 트랜잭션은 `application_layer/port/unit_of_work/parent_settings_unit_of_work.py`(ABC)→driven 구현 · result=원시 consents/categories 만·HTTP status DTO 0 · 매핑 controller 직소유(`notification_consent_controller.py:124-129`) | ✅ | ✅ | ✅ | ✅ |
| SD-7 컨텍스트 통신 | OHS 동결 계약(top-level `open_host_service/notification_consent/` — spec §4) 경로·`parent_notification_enabled(Request{parent_id,category})→Response{enabled}` 시그니처 무변(`notification_consent_service.py:35-37`)·밖=False 무예외(`:41-42`) — 스텁 본문만 구현 대체 · 소비자 notifications ACL 은 OHS 계약만 import 실측 · controller 의 accounts import 는 승인 빚 #12(RUBRIC SD-7 주의 — FAIL 아님·빚 클래스) | 신호 有(#12×1) | ✅ | ✅ | ✅ |

## B. TIER-S 척추 — S-HR (판 = registry 위임 · 3.14 실측)

| ID | Result | 종합 | 치명 |
|---|---|---|---|
| SH-1 컨테이너 | `application/parent_settings/` 하위 전수 (#7 exit 0) | ✅ | ✅ |
| SH-2 4계층 | `{driving,application,domain,driven}_layer/` 물리 실재 (#4 귀속 0) | ✅ | ✅ |
| SH-3 골격+거주 명명 | 고정·재등장 칸 빈 실현 · `…UseCase.execute(command|query)→result`·`_command/_query/_result`·`dto` 0 (#19·#26 발화 0) | ✅ | ✅ |
| SH-4 Django앱 위치 | `driven_layer/django_parent_settings/{models,migrations}/`·AppConfig 점경로·INSTALLED_APPS 1행 | ✅ | ✅ |
| SH-5 ORM 명명 | `NotificationConsentModel` ↔ bare `NotificationConsent` | ✅ | — |
| SH-6 포트/구현 명명 | ABC 개념+역할접미·구현 기술접두(`DjangoNotificationConsentRepository` 등)·`Impl`/약어 0 | ✅ | — |
| SH-7 포트 선언 위치 | 리포지토리=`domain_layer/notification_consent/notification_consent_repository.py` · 능력 포트=`application_layer/port/` (#22 발화 0) | ✅ | ✅ |
| SH-8 ACL 분리 | 이 라운드 상류 소비 없음(인바운드 중화 라운드) — N/A 성 통과 | ✅ | — |
| SH-9 단일 레이아웃 | `test/` 단일 | ✅ | — |
| SH-10 테스트 의미군 | `test/{unit,integration,e2e,fake,factories}` · e2e blackbox(#390 동형 0) · **타 BC test import 재작업으로 소멸**(#385/#51 발화 0 실측) | ✅ | — |

## TIER-S(조건부) — S-NINJA

| ID | Result | 종합 | 치명 |
|---|---|---|---|
| NJ-1 스택 | `@api_controller`+`register_parent_settings_api(api)` 명시 registrar(`urls.py`)·`auto_import=False`·중앙 api.py 무접촉 | ✅ | ✅ |
| NJ-2 얇음 | principal·command 조립·application 호출·매핑뿐 — ORM/수동검증/비즈 분기 0(의미 레인 확인) | ✅ | ✅ |
| NJ-3 Schema 분리 | In/Out 분리·명시 매핑 | ✅ | — (강) |
| NJ-4 오류 선언 | BC 직접 반환 status=같은 BC `<Bc>ErrorSchema`(FrameworkErrorSchema 상속) `response=` 선언·거짓 광고 0 (#5 발화 0) | ✅ | — (강) |
| NJ-5 문서화 | 기본 충족 — 🟡 문서 표면 소폭(모양 아님·A축 무관) | 🟡 | — (경미) |
| NJ-6 버전 핀 | 기존 스택 준용·신규 핀 0 | ✅ | — (경미) |
| NJ-7 오류 직접 계약 | 좁은 try(호출 1문장 `:124-125`)+구체 except+무인자 concrete `Problem()` 직접 `Status(422)`(`:127-129`)·helper/handler/catch-all 0 — **catch 대상은 응용 노출 예외 `UnknownNotificationCategory`**(use case 가 도메인 예외→응용 번역 `use_case.py:54-55` — «#210 응용 예외 번역» 재작업 반영)·3.14 검사기 green 실증 | ✅ | — (강) |

## TIER-S(핵심) — FC (대체 관측 — 동결 방법의 인증 아님)

| ID | Result | 종합 | 치명 |
|---|---|---|---|
| FC-1 골든 오라클 | ⏸️ parent_settings 골든 행위표 미확보(사전등록 없음 — 라운드 재료 준비 공백) · 대체 관측: A축 diff 0+spec↔스위트 대조 충돌 후보 0 | ⏸️ | ⏸️ |
| FC-2 비-vacuous | ⏸️ mutation 미실행 · 422 unknown category·부분 갱신·기본값 red 단언 실재(신호) | ⏸️ | ⏸️ |
| FC-3 도메인 정합 | 카탈로그 7종 선언순 축자(=spec §1)·기본 전부 true·부분 갱신·unknown→422·last-write-wins 멱등 upsert — e2e #1~#8 실증(`test/e2e/test_notification_consent_api.py:135-307`)·부호반전/인과역전 0 | ✅ | ✅ |

## C. 기존규약 마스크

MQ0=Y(앵커 삭제→재생성) → §0 강제 충족. 배선 touched: `settings/base.py` 1행·`urls.py` registrar 호출 행 + **승인 스코프 확장 2파일**(`usage_quota_api_router.py` 함수형 지연화 15행·이에 따른 `urls.py` 기존 usage_quota mount 행 갱신) — 사용자 승인(승인 대장 ⑴) 범위 내·A축 diff 0 이 기존 계약 불변을 기계 증명. F3 Placement 위반 0.

## D. TIER-Q 품질

Q-1 스코프 ✅(표면=spec·발명 0) · Q-2 API 계약 ✅(오류 wire slug/status 축자·A축 diff 0) · Q-3 동시성 ✅(PATCH 멱등·경합은 저장 계약으로 결정적 검증) · **Q-4 ✅[치명 통과]**(커스텀 백엔드/몽키패치 0) · Q-5 ✅(자기 0001·기존 이력 침범 0) · Q-6 ✅(pytest 함수형·factory·fake ABC) · Q-7 🟡(프로덕션 전수 준수 — 테스트 모듈 일부 상수 어노테이션 누락 관찰).

## 의미적 변종 / backstop-blind 메타

1. **[검사기-표준 충돌 — 이번 라운드 최대 수확(레인 간 공동)]** **#210 vs #95/NJ-7 충돌 실재**: `check-context-isolation.py:211` #95 는 «driving 잎이 domain 에서 가져올 수 있는 것은 exception·값 객체뿐»으로 domain 예외 import 를 **허용**하는데, `check-usecase-dto-placement.py` #210 은 `domain_layer/**/exception/**` 을 «other»로 일괄 금지한다. 레인 A 는 응용 층 노출 예외 catch 로 #210 을 만족하는 모양을 실증(교집합 비어있지 않음 — 레인 B «공집합» 주장의 반례)했으나, **NJ-7 code-json 의 확립 모양(라운드 2 billing: domain 예외 12종 direct catch — 당시 결과지가 «강 PASS» 로 인증)이 #210 위반 모양**이라는 충돌은 실재한다. 수정 사이클 정본 결정 필요(어느 모양이 표준인가 — #210 개정 vs NJ-7/#95 문면 조정).
2. **[판정 근거 소급 무효]** 조정자 STOP 대리 답변 «#210 기각» 의 근거(라운드 2 billing #210 발화 0 실측)는 **python3.9 파싱 스킵 아티팩트**였다(billing `payment_controller.py` 는 3.9 문법 오류로 검사기에 안 보였음 — 08-14 소급 실증). 지시가 만든 «응용 예외 번역» 모양이 3.14 검사기에서 green 이라 **결론은 사후 유효하나 근거는 무효** — 대리 답변 절차의 검증 규율 재료.
3. 기타 관찰(의미 레인): ⑴ repo 가 `consent._events` 사적 필드를 직접 읽음(+테스트 주입) — 캡슐화 완화 관찰(#545 계열의 정당 실현 주장·위반 판정 아님) ⑵ upsert 동일값 재전송도 `updated_at` 갱신(문서화됨) ⑶ 테스트 자기 도출 PASS — spec 문면·입장표 번호 축자 도출·구현 심볼 import 0·옛 테스트 복제 흔적 미발견.

## 조정자 노트

- **④ 세션 감사**: 클린룸 위반 0(git 이력 열람 0·V1 0·eval 0). 커밋 메시지 자기보고 3건(6885 green·귀속 0·diff 0) **전부 독립 재실측 일치** — 라운드 2의 ⚠ 2건(자가확장 기준 주장) 대비 정직성 결함 0.
- **v2.5.0 레버 관측(확정분)**: L2 BC-범위 pytest 작동(내부 루프 21:3) · **L4 문면 이탈 1건**(리뷰어 4종을 연속 4메시지 background 로 배차 — 실행은 병렬·손실 ~1분·«한 응답 다발» 문면 미준수) · AskUserQuestion 2건 실발화(선택지마다 대가 병기·STOP 형식 준수) · «정지 커밋 후 구조화 질문» 문면 그대로 작동 · F1 승인-정박 작동(«discipline 판정은 결정 아님·사용자 몫» 문구 실발화) · 수렴 회로 위반 0(같은 게이트 반송 ≤2).
- **벽시계**: 기동 18:53 → 완주 커밋 00:07(약 5h14m) — 최대 손실은 배선 지뢰(usage_quota import-time `api.urls` 동결) 조사→STOP→재작업 ~1h+ (재료 결함·speed-plan §1.5 실측 기입). 라운드 2 대비 결함 축 재발 0.
- **라운드 2 결함 축 대조**: 빚 파일 자가 확장 → **정반대 실증**(빚 소멸 재작업·docs 무접촉) · waiver 사문 → 이번 waiver 0 · #365 도구 아티팩트 → 재발 0(ROSTER_AWARE 수정 작동).
- **남는 결점(코드 아님 — 수확 큐행)**: ⑴ **검사기 실행 인터프리터 계약 부재**(3.9 fail-open 침묵 스킵 — C축·bc_registry_run·registry_gate 전부 해당·과거 판정 소급 오염) ⑵ #210↔#95/NJ-7 충돌 ⑶ FC-1 골든 사전등록 라운드 재료 누락 ⑷ preflight 배선 스모크 부재(지뢰 ~2h).
- **다음**: ⑥b 사람 평가 접수 → 라운드 종결·스트릭 판정(사용자 몫 — ⑤ 문면 통과·⑥a 코드 결점 0, 단 판정 인프라 결점은 S2 수정 사이클행).
