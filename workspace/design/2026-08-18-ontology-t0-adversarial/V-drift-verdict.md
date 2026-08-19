# V — checker_cross_matrix 기존 표류 6건 원인 판정

- 작성: 2026-08-19 (T0 적대 검증 V 항목) · 판정 전용 — 본 문서 외 어떤 파일도 수정하지 않았다(EXPECTED 무접촉).
- 대상: `PYTHONUTF8=1 python3 workspace/tools/checker_cross_matrix.py` 차이 6건 (청정 HEAD 8b212d9 재현분).

## 0. EXPECTED 의 소재와 갱신 이력

| 항목 | 값 |
| --- | --- |
| EXPECTED 파일 | `workspace/tools/checker_cross_matrix.py` **내부 인라인 dict**(140~515행) — 별도 데이터 파일 없음 |
| 탄생 커밋 | `3d92b50` 2026-08-14 03:12 «fix(hygiene): S2.5 문면 위생 — corpus_lint·checker_cross_matrix 신설…» — 372행 전량 생성 |
| 마지막 갱신 커밋 | `2203ba1` 2026-08-15 01:12 «fix(checker): #462 admin 칸 면제…» — **단 1행** 손-스플라이스(`port_adapter_pairing × check-layer-skeleton` (488,29)→(488,33), 파일 386~388행 주석) |
| 그 후 | 무갱신. 세 검사기(check-layer-skeleton·check-usecase-dto-placement·check-db-table)도 2203ba1 이후 무개정(각각 최종 개정 47fce0d 08-12 · 25faad8 08-14 · 0350e29 08-12) |

## 1. 판정 방법 — 4개 커밋 상태 × 3개 인터프리터 전수 재현

`git archive` 로 커밋 트리를 저장소 밖(/tmp)에 추출해 census 를 재실행했다(작업 트리 무접촉).

| (레인 × 검사기) | EXPECTED | 74ffe53 v2.6.0 (25faad8 **이전**) | 3d92b50 (EXPECTED 탄생) | 2203ba1 (마지막 갱신) | HEAD 작업트리 |
| --- | --- | --- | --- | --- | --- |
| event_publish × layer-skeleton | (488,47) | (488,**37**) | (488,**37**) | (488,**37**) | (488,**37**) |
| event_publish × usecase-dto | (193,1),(569,4),(570,2) | (569,2),(570,1) | (569,2),(570,1) | (569,2),(570,1) | (569,2),(570,1) |
| event_publish_leaf × layer-skeleton | (488,53) | (488,**47**) | (488,**47**) | (488,**47**) | (488,**47**) |
| event_publish_leaf × usecase-dto | (140,1),(193,1),(569,4),(570,2) | (140,1),(569,2),(570,1) | 좌동 | 좌동 | 좌동 |
| port_adapter_pairing × layer-skeleton | (488,33),(490,1) | (488,29) — **490 없음** | (488,29) — **490 없음** | (488,33) | (488,33) |
| port_adapter_pairing × db-table | (2,(318,1),(325,1),'최소성') | exit 2 · id 없음(**#74 가드-red**) | exit 2 · **#74 가드-red** | **exit 0 clean** | **exit 0 clean** |

- 인터프리터 3종(/usr/bin/python3 3.9.6 · homebrew 3.12 · 3.14.7) 결과 동일 — 환경 가설 기각.
- **EXPECTED 의 6개 값은 어떤 커밋 상태에서도 재현되지 않는다.** 반대로 현재 값은 25faad8 «이전» 커밋(74ffe53)부터 이미 동일하다 → «25faad8 개정 후 EXPECTED 미갱신» 추정은 **기각**.
- 결정타: 클린 추출한 3d92b50·2203ba1 에서 `checker_cross_matrix.py` 전량 실행 시 **그 시점에 이미 각각 6건 차이**(exit 2). 두 커밋 메시지의 «cross 차이 0» 검증 주장은 클린 체크아웃에서 성립한 적이 없다 — census 채집(`--emit-expected`)과 «차이 0» 대조가 **같은 더러운 작업 트리**(fixture `good/` 안 비커밋 잔재 포함)에서 수행됐다는 뜻이다. 유령 값의 모양이 전부 «현재 값 + 추가 재료»형(#569/#570 정확 2배, #193·#490 추가, #488 +10/+6, django 앱 유래 #318/#325)인 것도 이와 정합한다. 잔재의 실체는 비커밋이라 사후 재구성 불가(불확정은 이 지점뿐이며 판정에는 영향 없음).

## 2. 6건 판정 표

| # | 현상 | 원인 커밋·근거 | 판정 | 처분안 |
| --- | --- | --- | --- | --- |
| 1 | event_publish × check-layer-skeleton (488,47)→(488,37) | `3d92b50` 에서 EXPECTED 가 더러운 트리 census 로 탄생(47은 어느 커밋에서도 재현 불가·전 커밋 실측 37). 검사기 자체는 EXPECTED 탄생 «이전»(47fce0d) 이후 무개정 — `dddjango/scripts/check-layer-skeleton.py:147-158`(#488) | **EXPECTED 유령값** (회귀 아님·의도 개정도 아님) | (a) `--emit-expected` 갱신 안전 |
| 2 | event_publish × check-usecase-dto-placement (193,1),(569,4),(570,2)→(569,2),(570,1) | 동일 유령(2배 카운트+#193 은 census 당시 good/ 중복 재료 정황). 현재 red 실체 3건: `…/good/application/billing/application_layer/billing/record_order/`의 `record_order_result.py`[#570]·`record_order_command.py`·`record_order_query.py`[#569] (`check-usecase-dto-placement.py:287,299-308`). 25faad8 이 이 검사기를 개정(+56행)했으나 **이전 커밋 74ffe53 실측도 동일** → 개정 기인 아님 | **EXPECTED 유령값** | (a) 갱신 안전 — #193 검출 능력은 `api_error_controller`·`naming` × usecase-dto 행(각 (193,1))이 무표류인 것으로 건재 |
| 3 | event_publish_leaf × check-layer-skeleton (488,53)→(488,47) | 1과 동일(53 재현 불가·전 커밋 실측 47) | **EXPECTED 유령값** | (a) 갱신 안전 |
| 4 | event_publish_leaf × check-usecase-dto-placement (140,1),(193,1),(569,4),(570,2)→(140,1),(569,2),(570,1) | 2와 동일. (140,1)은 양쪽 공통 유지 — ⓓ후보 `…orders/driving_layer/api/order/schema/schema_in.py`(`check-usecase-dto-placement.py:504`, exit 불산입 후보) | **EXPECTED 유령값** | (a) 갱신 안전 |
| 5 | port_adapter_pairing × check-layer-skeleton (488,33),(490,1)→(488,33) | (490,1)은 **탄생 시점부터 유령** — 클린 3d92b50 실측 (488,29) 단독. `2203ba1` 스플라이스가 488 만 29→33 손계산 갱신(good측 2파일 `django_orders/admin/order/panel.py`·`models/order_model.py` 추가 기인 — 실측 일치)하고 유령 (490,1)을 존치 (`checker_cross_matrix.py:386-388`) | **EXPECTED 유령값**(꼬리) + 스플라이스 부분 갱신 | (a) 갱신 안전 — #490 능력은 missable_entrance·test_config·test_config_entrance·transaction_boundary × layer-skeleton 의 (490,1) 행 4개가 무표류인 것으로 건재 |
| 6 | port_adapter_pairing × check-db-table **기대 red 소멸**('최소성' (318,1),(325,1)) | 2중 원인. ① (318,1),(325,1)부터 유령 — 클린 3d92b50 실측은 `blocker: … django_<bounded_context>/ 앱이 0건 … (#74)` **가드-red**(id 없음·분류도 '최소성'이 아니라 '가드-red'가 맞았음). ② `2203ba1` 이 #462 admin 면제 사이클에서 good측에 **합법 최소 django_orders 골격**(`class OrderModel: pass` — models.Model 비상속이라 ORM 값검사 비대상)을 의도 추가 → #74 가드 전제(앱 0건) 해소, 검사 본체가 실제 수행되어 `clean — django 앱 1개 규율 일치` exit 0 | **유령값 + 의도된 fixture 합법화** (검사 능력 약화 아님) | (a) 갱신 안전(행 삭제가 옳음) — #318/#325 능력 실증: `db_table/bad_rules` 실측 blocker 26건 중 `[#318] …driven_layer/repositories`·`[#325] …adapter/persistence/admin.py` 현재도 발화(`check-db-table.py:463,474`) |

## 3. 총평

**6건 전부 검사기 회귀 아님 — 일괄 `--emit-expected` 갱신 안전**(원인은 검사기가 아니라 EXPECTED 쪽: 더러운 작업 트리에서 채집된 유령 census + 2203ba1 부분 손-스플라이스이며, 소멸 1건 포함 전 건에서 관련 규칙 #488·#490·#193·#569·#570·#140·#318·#325 의 검출 능력이 타 레인/bad fixture 에서 건재함을 실측 확인했다).

부대 권고(갱신 작업 시):
1. 갱신 후 EXPECTED 는 372→**371행**(db-table 행 삭제). 자동 분류는 event/port × layer-skeleton = 골격-부재, usecase-dto 2행 = 최소성으로 산출되며 타당하다.
2. `checker_cross_matrix.py:386-388` 의 2026-08-15 스플라이스 주석에 «(490,1)은 유령이었음» 정정 각주를 함께 남길 것(차분 세탁 방지 원칙 준수).
3. 재발 방지: `--emit-expected` 와 «차이 0» 검증은 반드시 클린 체크아웃(또는 `git status` 상 fixture 경로 무잔재 확인) 후 수행 — 이번 유령의 발생 기전이 정확히 이 절차 부재였다.

## 부록 — 근거 좌표

- EXPECTED 정의·대조 로직: `workspace/tools/checker_cross_matrix.py:57-84`(census — 비-0 exit 만 기록: «행 소멸»=exit 0 전환), `:114-125`(변화·소멸 발화), `:140-515`(EXPECTED), `:386-388`(2203ba1 스플라이스 주석)
- 규칙 문면: `dddjango/scripts/check-layer-skeleton.py:147-158`(#488)·`:160-185`(#490) · `dddjango/scripts/check-usecase-dto-placement.py:287`(#193)·`:299-308`(#569·#570)·`:490-504`(ⓓ#140) · `dddjango/scripts/check-db-table.py:463`(#318)·`:474`(#325)
- 검증 실행: /tmp 추출본 4상태 × python 3.9.6/3.12/3.14.7 — 클린 3d92b50 전량 실행 결과 «차이 6건 · exit 2», 클린 2203ba1 동일(HEAD 보고분과 문면까지 일치)
