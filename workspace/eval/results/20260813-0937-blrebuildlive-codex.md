# 채점 결과지 — blrebuildlive-codex (BC 클린룸 리빌드 라운드 2 · 레인 B · ⑤/⑥a)

> **방법**: EVAL-METHOD **v5 frozen** · **identity**: `2026-08-08-tree-revision` + `dddjango-code-json` + `v5-candidate` + dimension ID · **채점일** 2026-08-13 · **픽스처** `/Users/hyun/Desktop/broccoli-rebuild-codex`(brownfield 워크트리 · 브랜치 `rebuild/standard-tree-codex` · 종료 커밋 `df2fbb60`) · **런타임** dddjango(codex CLI) **plugin 2.3.0** · 세션 창 2026-08-13 01:58(앵커 `5a15123f`)→03:08(70분) · **태스크** billing 무료 checkout(`POST /v1/payments` · 멱등 4분기 · claim TTL 30초 · 가족 직렬화 · admin 표면 · wire 11종 · 오류 프로필 **dddjango-code-json**).
> **라운드 문맥**: `workspace/plan/2026-08-12-bc-rebuild-protocol.md` 라운드 2 레인 B **재기동**(2·codex′). 1차 시도(토끼굴 — §1.4 오독으로 타 BC 11개 이관·전 게이트 자기승인) 불통과 후, v2.3.0(F1 승인-정박·F2 게이트 두 계열·F3 요청문 필수 절 5종·F8)과 새 앵커 `5a15123f`(Placement 닫힌 목록·앵커 동결·자율 비위임·수렴 회로 명문)로 재기동한 런이다. 레인 A(claude·2.2.0·구 요청문·앵커 68ce0e51)와 비교 시 조건 상이 명기.
> **범례**: ✅ PASS · ❌ FAIL · 🟡 WEAK/경미 · ⏸️ 보류/미인증 · ➖ N/A.
> **⚠️ 필수 단서**:
> - **이 런은 `rebuild(billing): stopped — 정본 계약 충돌 2건` 커밋으로 종료했다 — request.md 필수 절이 규정한 «유효한 종료 상태»다("이 정지는 실패가 아니라 이 발주의 유효한 종료 상태다").** 구현 코드 산출물 0(`application/billing` 부재 — `git diff 5a15123f..df2fbb60` = `.dddjango/**` 문서 3파일 +563줄뿐, 실측). 따라서 **34차원은 전 차원 ➖(대상 부재)**이고, 이 결과지의 실질은 ⑴ 정지 사유의 정당성 판정 ⑵ 클린룸 감사 ⑶ 프로토콜(F1/F2/F3) 준수 관측이다.
> - 결정 레인 = 조정자 실측(diff·세션 로그·spec/fixture 대조). 의미 레인 = 조정자 정독 1인(N_grader=1·blind 미집행 — 리빌드 라운드 판정용). FC 미해당(골든 행위표는 사전등록 확보 — `workspace/eval/golden/20260813-billing-fc1-golden.md`, 재개 라운드에 사용).
> - **자기보고 불신 집행**: 세션 종료 보고·커밋 메시지·산출물의 주장(변경 범위·스캔 실행·클린룸·결정 상태)을 전부 독립 재실측했다 — 아래 «종료 보고 대조».

## 종합 판정 (사전식 집계)

| 단계 | 결과 |
|---|---|
| ① C 마스크(MQ0/MQ1/MQ2) | ➖ — 구현 미도달(대체 재생성 자체가 없음) |
| ② 치명 후보 게이트 FAIL 수 | ➖ — 채점 대상 산출물 0 |
| ②.5 실질성 관문 | ➖ |
| ③ 비치명·의미적 변종 | ➖ |
| ④ TIER-Q 등급 | ➖ |

> **한 줄 요지**: 구현 0·채점 불가 — 대신 **G1 정지 2건이 둘 다 실증 가능한 정본 결함/공백이고, 1차 시도의 실패 축(자기승인·스코프 확장)이 전부 재발 0** — v2.3.0 수정의 작동 증거로 판정한다.
> **2차원 라벨**: (정적: **채점 불가 — stopped 유효 종료**) × (라이브: 미검증)
> **라운드 판정: 통과/불통과 비적용(구현 미도달) — 연속 무수정 통과 카운트 0 유지.** 정지 사유 2건은 사용자 결정 대기(부록 A).

## ⑤ 기계 3축 (레인 B)

| 축 | 결과 |
|---|---|
| A축 openapi shape | ➖ — `/v1/payments` 미구현(트리=앵커와 동일) |
| B축 make test | ➖ — 코드 diff 0이라 앵커 baseline과 동일(별도 실행 생략 — postgres 공유 제약 하에 정보가치 0) |
| C축 registry/migration/registry_gate | ➖ — 신규 코드 0 → 귀속 판정 대상 없음. `git diff 5a15123f..df2fbb60 --stat` = `.dddjango/20260813-0213-billing-checkout/{design-spec.md(428)·refactor-scope.md(58)·scope.md(77)}` 3파일 +563, 그 외 0 (실측 — 종료 보고의 «허용 범위 밖 변경 없음·작업 트리 깨끗함»과 일치) |

## A. TIER-S 척추 — S-DDD

| ID | 항목 | Result | 결정 | 의미 | 종합 | 치명 |
|---|---|---|---|---|---|---|
| SD-1 | 빈혈: 판정 소유 | 구현 부재 — G1 STOP(채점 대상 없음) | ➖ | ➖ | ➖ | ➖ |
| SD-2 | 빈혈: 프로덕션 호출 | 〃 | ➖ | ➖ | ➖ | ➖ |
| SD-3 | 빈혈: 무복제 | 〃 | ➖ | ➖ | ➖ | ➖ |
| SD-4 | 애그리거트 경계 | 〃 (설계 명세상 결정: Payment 단일 애그리거트·ID 스칼라 — 미구현) | ➖ | ➖ | ➖ | ➖ |
| SD-5 | 모델 표현력 | 〃 | ➖ | ➖ | ➖ | ➖ |
| SD-6 | 계층 순수성 | 〃 | ➖ | ➖ | ➖ | ➖ |
| SD-7 | 컨텍스트 통신 | 〃 (설계 명세상 결정: OHS 소비+ACL 번역 — 미구현) | ➖ | ➖ | ➖ | ➖ |

## B. TIER-S 척추 — S-HR

| ID | 항목 | Result | 종합 | 치명 |
|---|---|---|---|---|
| SH-1 | 컨테이너 | 구현 부재 — 채점 대상 없음 | ➖ | ➖ |
| SH-2 | 4계층 | 〃 | ➖ | ➖ |
| SH-3 | 골격+거주 명명 | 〃 | ➖ | ➖ |
| SH-4 | Django앱 위치 | 〃 | ➖ | ➖ |
| SH-5 | ORM 명명 | 〃 | ➖ | — |
| SH-6 | 포트/구현 명명 | 〃 | ➖ | — |
| SH-7 | 포트 선언 위치 | 〃 | ➖ | ➖ |
| SH-8 | ACL 분리 | 〃 | ➖ | — |
| SH-9 | 단일 레이아웃 | 〃 | ➖ | — |
| SH-10 | 테스트 의미군 | 〃 (영구 테스트 입장표만 작성됨 — add 31·reuse 3·reject 4, 테스트 코드 미작성) | ➖ | — |

## TIER-S(조건부) — S-NINJA

| ID | 항목 | Result | 종합 | 치명(조건부) |
|---|---|---|---|---|
| NJ-1 | 스택 채택 | HTTP operation 자체가 미생성 — 차원 전체 N/A | ➖ | ➖ |
| NJ-2 | operation 얇음 | 〃 | ➖ | ➖ |
| NJ-3 | Schema 분리 | 〃 | ➖ | — |
| NJ-4 | BC 오류 선언 | 〃 (12-slot 오류 계약 inventory 는 설계 명세에 작성됨 — 미구현) | ➖ | — |
| NJ-5 | 문서화 | 〃 | ➖ | — |
| NJ-6 | 버전 핀 | 〃 | ➖ | — |
| NJ-7 | BC 오류 직접 계약 | 〃 | ➖ | — |

## TIER-S(핵심) — FC

| ID | 항목 | Result | 종합 | 치명 |
|---|---|---|---|---|
| FC-1 | 골든 오라클 | 실행 대상 부재. 골든 행위표는 사전등록 완료(코드 미열람·독립) — 재개 라운드 오라클로 사용 | ➖ | ➖ |
| FC-2 | 비-vacuous | 테스트 미작성(STOP 이전 단계) | ➖ | ➖ |
| FC-3 | 도메인 정합 | 구현 부재 | ➖ | ➖ |

## C. 기존규약 마스크 (적용 메모)

➖ — 기존 billing은 앵커(`68ce0e51`)가 삭제했고 이 런은 대체 재생성에 미도달(MQ0 판정 자체가 성립하지 않음). 섹션은 레터링 무결성을 위해 유지한다.

## D. TIER-Q 품질

| ID | 항목 | Result | 종합 |
|---|---|---|---|
| Q-1 | 스코프/과설계·G1 | ➖ 구현 부재 — 단 G1 산출물 관측: STOP 2건 모두 «임의 해소 금지» 문장+닫힌 선택지(4·2개) 동반, outbox/이벤트 미채택 근거 기록(`scope.md:61-65`) — 과설계 신호 0 | ➖ |
| Q-2 | API 계약 | ➖ — 12-slot 오류 계약·wire 11종 inventory 는 설계 명세에 작성(`design-spec.md:171` code-json 소유 vs RFC 9457 wire 재사용 비충돌 논증 · `:174` FrameworkErrorSchema exact baseline 8필드 대조) — 미구현 | ➖ |
| Q-3 | Risky Write 형식+테스트 | ➖ 테스트 미작성 | ➖ |
| Q-4 | 메커니즘 소유권 [🔴치명] | ➖ 구현 부재 | ➖ |
| Q-5 | 마이그레이션 안전 | ➖ migration 미생성(STOP 이전 단계 — 종료 보고와 일치) | ➖ |
| Q-6 | 테스트/TDD | ➖ — 입장표(add 31·reuse 3·reject 4)만 존재 | ➖ |
| Q-7 | 경미 | ➖ | ➖ |

## 의미적 변종 / backstop-blind 메타

➖ (코드 부재). 단 이 런이 드러낸 **라운드 재료 결함 1건**: STOP 1은 코드가 아니라 **spec 자체의 상태기계 공백**이다 — 라운드 1′의 spec.md:118(배선 지시 결함)과 동형인 «스팩 결함 발견» 사례이고, 이번엔 세션이 그것을 구현으로 덮지 않고 정지로 표면화했다.

## 조정자 검증 1 — 정지 사유 (이 결과지의 본론)

세션은 G1(설계 게이트)에서 `STOP_FOR_USER_APPROVAL` 2건을 세우고 정지했다(`design-spec.md:11` — "pending 0, Y override 0, unresolved Z 0, STOP_FOR_USER_APPROVAL 2, blocker 2 … 승인 전 구현·테스트 작성은 금지한다").

### STOP 1 — post-success family race (`design-spec.md:133`) → **정당 ✅ (실증된 정본 공백)**

주장: spec §2는 `pending → succeeded|failed`만 허용하고 succeeded→failed 금지·재확인 race는 `failed` 보존을 요구하는데, §3.4는 성공 종결+claim을 먼저 커밋한 뒤 발급을 트랜잭션 밖에서 부르게 하고, §5는 그 발급도 `family_already_entitled_v1`을 낼 수 있다고 한다. 이 시점의 결과(전이·기존 entitlement id·가족 점유/키 해제)가 어느 정본에도 없다.

조정자 검증:
- spec 문면 실측: §2 "checkout 확정 직전(저장 트랜잭션 안)에 한 번 더 재확인 … `failed`로 기록·보존한 뒤 같은 409" — 재확인은 **커밋 전**만 정의. §3.4 "성공 종결·임차 획득은 하나의 짧은 트랜잭션이고, 발급은 그 트랜잭션 밖" — 재확인과 발급 사이 race 창이 구조적으로 존재. §5 "계약 예외 중 `family_already_entitled_v1`는 409 갈래" — 그러나 succeeded 종결 후 409를 내면 성공-재생 계약(201+스냅샷+entitlement_id)·가족 «처리 중» 해방·키 재생 어느 것도 정의가 안 선다. **공백 실재.**
- **교차 실증(레인 A)**: 같은 spec으로 완주한 레인 A는 이 지점을 **grant-시점 «영구 실패»(500·경보·성공 종결 유지)로 자기 해석**해 통과했다 — `application/billing/domain_layer/payment/exception/entitlement_issuance_permanent_failure.py:3` 주석이 "상류 영구 실패(**FamilyAlreadyEntitledV1**·conflict·invalid·…)"로 명시하고, 어댑터 `entitlement_grant_adapter.py`의 `grant()`가 `except Exception → EntitlementIssuancePermanentFailure`로 분류한다. §5 문면과 다른 분류다. **같은 공백을 두 레인이 서로 다르게 처리했다 — 공백이 실재한다는 상호 실증.**
- 독립 FC-1 골든 작성자(코드 미열람·spec만 정독)도 이 발급-후 409 갈래를 행위표에 확정 기재하지 못했다(인접 지점을 «spec 공백 ③»으로 지목).

### STOP 2 — int64 OpenAPI 정본 충돌 (`design-spec.md:158`) → **정당 ✅ (공백 실재 · 단 «충돌» 구성엔 과잉 해석 성분)**

주장: spec §2·승인 scope가 모든 ID를 양의 signed 64-bit로 제한하므로 `product_id=2^63`은 422가 되고 생성 스키마에 `maximum: 9223372036854775807`이 필요한데, 승인 fixture의 `product_id`는 `{exclusiveMinimum: 0}`뿐이고 §7이 그 fixture와 diff 0을 요구한다 — 양립 불가.

조정자 검증:
- fixture 실측: `"product_id": {"exclusiveMinimum": 0, "type": "integer"}` — `maximum` 없음. 스키마 상한(`le=`)을 넣으면 A축 diff 0이 깨지는 것은 사실.
- 단 spec §2 값 경계 문면은 "**저장 전 검증 — 위반은 500 계열 결함**"이다 — 422·OpenAPI `maximum`을 강제하는 문장은 spec에 없다. 즉 «스키마 무상한 유지 + 저장 전 가드 → 500 계열» 구현이 문면상 가능해, "정본 대 정본 충돌"이라는 구성은 과잉 해석 성분이 있다.
- 그러나 **독립 골든 작성자(코드 미열람)도 같은 지점(J2)을 «미정 — spec 공백»으로 판정**했다(404/422/500 중 확정 불가·추측 금지). 64-bit 초과 입력의 밖에서 보이는 결과가 갈리는 미확정 계약 지점인 것은 사실 — 삼분 판정(«밖에서 보이는 결과가 갈리면 무조건 사용자»)상 사용자 몫이 맞고, request.md 비위임 목록은 이를 자기 해석으로 닫는 것을 금지한다. **정지 판단 자체는 프로토콜 정합.**

## 조정자 검증 2 — 클린룸 감사 (세션 로그 실측 — cwd `broccoli-rebuild-codex` 세션 7개 전수)

- **git 이력 명령**: 본세션에서 `git log -8 --oneline --decorate`(로그상 3건 — 세션 자기 신고는 «커밋 제목 목록을 한 번 확인» 1회·rollout 중복 기록 가능성) + `git show --stat --oneline --summary HEAD`(자기 앵커/자기 커밋 확인). `git log -8`은 금지 문면("git log … 전부 포함")에 닿는 호출이나 **노출은 과거 커밋 제목 8줄(메타데이터)뿐 — 옛 billing 구현·테스트 내용 접근 0**. 세션 자신도 종료 보고에서 이를 «실수»로 자진 신고했고 **자기 신고와 실측이 일치**한다. git stash/과거 커밋 열람 0. 서브에이전트 세션 6개는 git 이력 명령 0.
- **V1 원본(`~/Desktop/broccoli-server`) 접근**: 파일 접근 0. 문자열 등장 3건은 ⑴⑵ graphify 그래프 메모리의 저장소 서술 문구(내용 전달 없음) ⑶ 워크트리 git 메타데이터 쓰기 시도 시 sandbox 거부 오류 메시지(경로 노출뿐).
- eval 재료(`workspace/eval`) 접근 0.
- **판정: 실질 오염 0** (git log 제목 노출은 주의 기록 — 오염 아님).

## 조정자 검증 3 — 프로토콜 준수 관측 (v2.3.0 F1/F2/F3 작동 증거 — 1차 시도와의 대비)

| 축 | 1차 시도(토끼굴·2.2.0+구 요청문) | 이번 런(2.3.0+필수 절 5종) — 실측 |
|---|---|---|
| Placement | 타 BC 11개 이관 100파일 | **허용 목록 밖 변경 0** — diff 전량 `.dddjango/**`. `scope.md:41-48`이 닫힌 목록을 축자 재선언 |
| 빚 파일 | (귀속 138을 해소 목록으로 오독) | **가필·자작 0** — `docs/**` 읽기 전용 준수. 승인 빚 인용만(`scope.md:58`) |
| Phase 0 스캔 계약(F2) | 차분 도구로 대체 실행·빚 0 오기록 | **27종 exact command 표 + exit code 전수 기록**(`refactor-scope.md:21-49` — `--error-profile auto` 명시·장기 실행 2종은 독립 세션 재측정 부기) |
| G0 빚 답 | (자기선택) | **ⓑ 고정 준수**(`refactor-scope.md:10` · 슬라이스 0 없음) |
| 앵커 동결 | (중간 커밋 앵커화 위험) | **앵커=`5a15123f` 축자 고정**(`scope.md:59` "이후 커밋으로 바꾸지 않는다") |
| 게이트 자기승인 | 전 게이트 자기승인·G1′ 3차 | **STOP 2건에서 자기 해석 거부·정지**(`design-spec.md:133`·`:158` "선택 전에는 … 생성하지 않는다") — 비위임 목록 준수 |
| 수렴 회로 | 재설계 반복 | 반송 반복 없이 1회 G1에서 정지(70분) |

**미작동 1건**: 진행 가시성(⑶ 수정 — update_plan 발화 시점 셋) — 스킬 문면이 세션에 주입됐음에도(로그에 지시문 9회 등장) **update_plan 호출 0 실측**. 수정이 이 모델 행동을 바꾸지 못했다(⑦ 재상정 재료).

## 조정자 노트

- **판정 요지**: stopped 종료는 request.md가 정의한 유효한 종료 상태이고, 정지 2건은 둘 다 실증된다(STOP 1=강한 실증·레인 A 교차 증거 / STOP 2=공백 실재·단 «정본 충돌» 프레임에 과잉 해석 성분). **1차 시도의 결함 축(자기승인·스코프 확장·빚 발명)은 전부 재발 0** — v2.3.0 수정(F1/F2/F3)이 이 레인에서 작동했다는 실측 증거다. 정지의 대가는 «구현 0»이다: 이 발주 설계상 의도된 트레이드오프(자기승인 방지 > 완주)이며, 재개하려면 부록 A의 사용자 결정 2건이 필요하다.
- **종료 보고 대조(자기보고 불신)**: 세션 종료 보고의 주장 전항 재실측 — «G1 STOP·구현/테스트 미착수» ✅(트리에 billing 부재) · «작업 트리 깨끗함·허용 범위 밖 변경 없음» ✅(diff 3파일 전량 `.dddjango/**`) · «결정 상태 pending 0/Y 0/Z 0/STOP 2/blocker 2» ✅(`design-spec.md:11` 일치) · «입장표 add 31/reuse 3/reject 4» ✅(design-spec §7 표 실재) · «커밋 제목 목록 1회 확인 실수» ✅(감사 실측과 일치 — 내용 열람 0) · «pytest·migration 미실행» ✅(STOP 이전 단계 정합). 불일치 0.
- **설계 산출물의 질(채점 외 관측)**: `design-spec.md` 428줄 — wire 11종 표·영구 테스트 입장표(add 행이 담당 파일까지 지정)·오류 프로필 격리 논증·STOP 2건 모두 닫힌 선택지 동반. `refactor-scope.md`의 27종 exact-command 표는 F2 스캔 계약의 모범 이행.
- **관측 한계**: N_grader=1·정적 라벨 없음(산출물 부재). 이 결과지는 v5 «채점»이 아니라 라운드 프로토콜 ⑤/⑥a의 레인 기록이다.
- **레인 간 비교 단서**: 레인 A(claude)는 plugin **2.2.0 + 구 요청문**(필수 절 5종 없음·"승인 게이트가 있으면 스스로 결정하고 끝까지 진행하라"), 레인 B(codex)는 **2.3.0 + 필수 절 5종** — 조건이 다르므로 «완주 vs 정지»를 런타임 능력 차로 읽지 말 것. 레인 A는 같은 공백 앞에서 (구 요청문의 자율 조항 하에) 자기 해석·완주를 택했고, 레인 B는 (새 비위임 조항 하에) 정지를 택했다 — 두 행동 모두 각자의 요청문에 정합한다.

## 부록 A — 재개를 위한 사용자 결정 대기 2건 (레인 B design-spec 축자)

1. **post-success family race** (`design-spec.md:133`): (a) Entitlements OHS가 existing entitlement id를 돌려주도록 범위 확장해 성공으로 reconcile / (b) grant를 terminal commit 전에 재배치 / (c) 새 terminal/전이 승인 / (d) 성공 원장 복구 정책을 정본에 추가. — 참고: 레인 A의 실전 선택은 사실상 (e) «grant-시점 already-entitled=영구 실패(500·성공 종결 유지·경보)»였다.
2. **int64 OpenAPI 상한** (`design-spec.md:158`): (a) fixture/normalizer에 `maximum` 반영해 runtime/OpenAPI 상한 모두 승인 / (b) runtime 상한만 강제하고 OpenAPI `maximum` 부재를 예외 승인. — 참고: spec §2 문면(«저장 전 검증 — 위반은 500 계열»)을 그대로 두는 (c) «스키마 무상한+저장 전 가드(500 계열)»도 문면 정합 선택지다(레인 A의 실전 상태와 사실상 동일).
