# rv5-C — ⑤-1 조각 1(S-1 + S-4 · `56b27e1`) 구현 리뷰 · 리뷰어 C(증거·표본 외 축 — 실측 재현·무손실·소급·회신 재료) · 2026-09-04

대상: 커밋 `56b27e1`(+기록 `06fef51`) — 새 검사기 `dddjango/scripts/check-public-surface-annotation.py`(HEAD = 56b27e1 과 byte 동일 · codex 미러 byte 동일) · `registry_gate.py` ⓔ2 · 구현 기록 `evidence/impl/piece1-summary.md` 의 실측표·검증 절. 실서고 무접촉 — 실행은 격리 사본 `$S/fr3/{spring(7bfe1aa)·spring-d2eaafe·spring-f5ee428·kkebi(6608fb0)}`(각 실서고 venv 인터프리터 · cwd=사본 · 사본은 `mp_probe_*` 없음 확인 · 타 세션 sink `.dddjango/violations/*.jsonl` 만 untracked) · 산출 `$S/rv5C/`(옛 검사기 = `git show main:` 4 파일 `old/` — `git archive main` 과 byte 동일 · 무손실 판형 사본 `ll/` = `rv3C/lossless.sh`+`lossless_fx.py`+`lossless_diff.py` 를 R 만 바꿔 복사 — 구현자의 `rv3C/out` 을 덮지 않기 위해 · `analyze.py` 계수·슬롯 1:1·BC 분포 · `gate_runs.sh`/`gate_run3.sh` ⓔ2 실측 3회 · 사본 임시 파일 전부 제거 확인). mypy 는 돌리지 않았다(효과 수치는 검사기 실측으로 재확인 — §5). Serena: skipped — 리서치·재계산(코드 수정 없음 · `.serena/project.yml` 부재).

## 1. 판정 표

| # | 항목 | 판정 | 근거(요약 · 상세 §2~§6) |
|---|---|---|---|
| C-1 | 실측표(구현 기록 · rv3-C §2) 독립 재현 — 4사본 | **검증됨** | 새 검사기 × 4사본 = 구현 기록 표와 **전 셀 일치**(spring #646 18 · #647 594/255/8 · #650 40 · #645 76 · #493 3,216 / d2eaafe 31·585/261/9·38·78·3,225 / kkebi 21·161/253/42·1·121·173) · f5ee428 신규 수치 18·603/261/9·40·78·3,225 · 레코드/줄 이중 계수 병기(§2) |
| C-2 | `[#645]` byte 동일 · ⓓ#645→#647 **슬롯** 1:1 · 혼재 줄 | **검증됨 + MINOR(M2 — 증거 키 단위)** | `[#645]` 발화 라인·레코드 다중집합 4사본 전부 **동일**(76/78/78/121) · ⓓ#645 감소분(655/642/661/55)을 (경로·줄·**슬롯 라벨**) 키로 대조 → **matched 전량 · unmatched 0 · 역방향(#647 Any 슬롯 중 ⓓ#645 출처 없음) 0 · bare 접힘 0** · 혼재 줄 spring 2(`steps/__init__.py:747` `blocks` ⓓ 잔존/`source_descriptor` 차단 · `release_store.py:533` 매개변수 3 차단/반환 ⓓ 잔존) 정확 — 단 구현 기록·`cmp647.py`·`lossless_diff.py` 의 1:1 은 (경로,줄) 키다(Δ3 ⑫ «슬롯» 미반영 · 데이터로는 문제 0 — 여기서 닫음) |
| C-3 | 무손실 재실행(`lossless.sh main worktree` 판형) · RED 3 전수 · main 픽스처 9/9 | **검증됨** | 재실행 로그 = `impl/lossless1.log` 와 **행 단위 동일**(scripts-diff 경로 행 제외) · 12/12 OK · `VERDICT: RED` 의 원인 = 픽스처 3 케이스의 A∖B `#493` **8건 전수** = 신설 `admin/order/panel.py`(:19·20·21·25·26·27 = 6) + 신설 `admin/shipment/panel.py:17`(1) + 신설 `stub_generic_bad.py:26`(1) — 전부 56b27e1 신설 파일에 **옛 #493** 이 낸 오탐(별칭·subscript 기저 선언적 면제 회복 = 의도) · main 픽스처 트리 재실행 **9/9 OK · LOSSLESS** |
| C-4 | registry_gate ⓔ2 실측 재현(kkebi) | **검증됨** | ① 무해 파일(`docs/rv5c_probe.md`) → «귀속 0 · legacy 512 · ⓓ 신규 **0** · ⓓ legacy **1,269** · exit **0**» = 구현 기록 동일 · sidecar 키 = 현행 6개뿐(`candidate_*` **부재** ✓ `if candidates:`) ② 새 파일 `application_layer/.../rv5c_probe_helper.py`(`x: dict[str, object]` 지역 변수) → «ⓓ 신규 **1**(`[ⓓ#647] …:N: \`x\` 주석 …`) · sidecar `candidate_lines` 1·`candidate_records` 1(info #647 `:5`) · `records` 에는 ⓓ **무포함**(단 새 파일이 `#490` 트리 이름 위반을 내 귀속 1·exit 2 — 내 배치 탓 · ⓓ 는 exit 불산입) ③ 기존 유스케이스 파일 `execute()` 에 `_rv5c_probe: dict[str, object] = {}` 1줄 삽입(아래 줄 밀림) → «귀속 **0** · ⓓ 신규 **1** · legacy 1,269 무변 · exit **0** · sidecar `candidate_*` 1/1 · `records` []» = Δ14 문면 완전 재현(§3) |
| C-5 | 소급·legacy 표(회신 3용) 갱신 | **검증됨 + MINOR(M5 — Δ12 «105」 정의)** | §4 표 — 새 검사기 기준 BC 별 상위 6 · `Form.clean -> dict[str, Any]` 잔존 spring **15**·kkebi **3** · kkebi `web/`·`scripts/` 는 #646/#647/#650 **0**(루트 분포 application 472·framework 1(ⓓ `framework/pure/jcs.py:26`)) · 브라운필드 상한 재산 · Δ12 «web/scripts #645 ⓓ nested kkebi 105 잔존」 은 **#647 형상 부분집합**(rv3-C 산법) — 새 검사기의 web/scripts ⓓ#645 nested 잔존 **줄은 155**(web 102·scripts 53 · bare 포함 240) → 회신은 «155(그중 105 는 dict 값 Any 형상)」 로 |
| C-6 | ⓓ 감수 부담 — 총량 · ⓔ2 뒤 신규분 0 · 새 BC 형상 | **검증됨** | §4-2 — spring application ⓓ **223 줄**/16 BC(#647 133·#69 43·#645 40·#650 8) + framework 213 · kkebi application **485 줄**/12 BC(#647 294·#69 112·#645 79·#650 1) + web 166·scripts 134 · ⓔ2 뒤 신규분 = **0**(C-4 ①) · 새 BC 예상 ⓓ 형상 = `pull_events -> list[object]` kkebi 16/42(애그리거트당 1) · `_reject_json_constant` 4(문면 «미러면 통과」 로 닫힘) · TypeIs 재구성 도우미 2~4 |
| C-7 | 효과 서술 재료(rv1-C §5 정직화) 재확인 | **검증됨** | §5 — S-1 «8/10 레인 은폐 18줄」 = #646 spring HEAD **18**(헤더 17+속성줄 1 · 16 파일 · **8 BC**) · «1/10 레인 mypy 26」 = d2eaafe #646 **31** 의 차분 **13**(fortune_character 맨몸 13 = S1 «맨몸 13」) · S-4 «Any 누수 ≈6/레인」 = application #647 Any 차단 **92 줄/16 BC = 5.8** · «object 반환/속성 ≈3」 = **53/16 = 3.3**(반환 35·속성 18) · ⓓ ≈7/BC → 새 검사기 #647 ⓓ 입구 **8.0/BC**(+자리표시 5) · kkebi ≈24 → **21.0**(+42 자리표시 = 24.5) · «mypy 빚 67/70 RAG」 는 재측정 안 함 — 검사기로는 #647 차단 594 중 `framework/technology`(rag) **449 = 76%** 가 같은 방향 |
| C-8 | 루트 필터 구현 | **검증됨 + MINOR(M1 — any-part 의미)** | `_in_rule_roots(rel) = bool(RULE_ROOTS & set(rel.parts))`(:638) — «경로 어느 구성요소든 `application`/`framework`」 · 4사본에 중첩 `application/`·`framework/` 디렉터리 0 이라 효과 0 이나 `web/framework/x.py`·`docs/application/…` 가 생기면 필터가 뚫린다 → `rel.parts[0] in RULE_ROOTS` 권고 |
| C-9 | 구현 기록 문면 | MINOR(M3) | «`admin/order/panel.py` 무주석 admin 선언 속성 7」 → order/panel.py **6** + shipment/panel.py **1** · «+5 `mp_probe_*` 사본 오염 제외」 는 현재 사본에 없음(정리됨) · «#647 ⓓ 입구 줄 255」 옆에 레코드 296(다중 슬롯) 병기 권고 |
| C-10 | ⓔ2 관측성 | MINOR(M4) | «ⓓ legacy 1,269」 는 **27 검사기 합**(public-surface 만은 kkebi 794 줄·810 레코드 · usecase-dto #68/#103 등 포함) — 위반 절과 달리 검사기별 내역 없음 · 신규 라인은 `script ::` 접두로 귀속 가능 · legacy 도 `by_checker` 한 줄 권고(문면 비용 3줄) |

BLOCKER 0 · MAJOR 0 · MINOR 5(M1~M5).

## 2. 실측 재현 표 (구현 기록 vs C · 새 검사기 HEAD × 4사본 · 각 실서고 venv · 루트 필터 뒤)

레코드 = `DJR_FINDINGS_JSON` sink · 줄 = 서로 다른 (경로, 줄). 구현 기록 표는 «줄」 기준(#646·#650 은 레코드=줄).

| 항목 | spring HEAD 기록 / **C** | d2eaafe 기록 / **C** | f5ee428 **C**(신규) | kkebi 기록 / **C** |
|---|---|---|---|---|
| #646 위반(레코드=줄) | 18 / **18**(헤더 17·속성줄 1 · 16 파일 · 8 BC) | 31 / **31**(+fortune_character 맨몸 13) | **18** | 21 / **21**(헤더 21 · 21 파일 · 4 BC) |
| #646 ⓓ | — / **0** | **0** | **0** | — / **0** |
| #647 위반 줄(레코드) | 594 / **594**(733 · Any 655·object 78) | — / **585**(722) | **603**(742) | 161 / **161**(166 · Any 55·object 111) |
| #647 ⓓ 입구 줄(레코드) | 255 / **255**(296) | — / **261**(302) | **261**(302) | 253 / **253**(265) |
| #647 ⓓ 자리표시 object 줄 | 8 / **8** | — / **9** | **9** | 42 / **42** |
| #650 ⓓ | 40 / **40**(framework 32·application 8) | 38 / **38** | **40** | 1 / **1**(identity) |
| #645 위반 라인 | 76 / **76 byte 동일** | 78 / **78 동일** | **78 동일** | 121 / **121 동일** |
| ⓓ#645 레코드 old→new | 708→53 | 693→51 | 714→53 | 385→330 |
| ⓓ#645 감소 → #647 슬롯 1:1 | 655 / **655/655**(unmatched 0 · 역방향 0) | — / **642/642** | **661/661** | 55 / **55/55** |
| 혼재 줄(같은 줄 ⓓ#645 잔존 ∧ #647 Any 차단) | **2**(:747 · :533 — 슬롯 단위 정확) | 2(:745·:532) | 2 | 0 |
| #493 레코드 · 집합 | 3,216 / **3,216 · 집합 동일** | 3,225 / **3,225 동일** | **3,225 동일** | 173 / **173 동일** |
| 루트 분포(#646/#647/#650) | app 18 / app 286·fw 751 / app 8·fw 32 | app 31 / 271·762 / 6·32 | app 18 / 291·762 / 8·32 | app 21 / **app 472·fw 1** / app 1 — **web·scripts 0** |
| exit old→new | 2→2 | 2→2 | 2→2 | 2→2 |

방법: `$S/rv5C/ll/lossless.sh main worktree`(old = `git archive main` · new = working tree = 56b27e1) 의 sink·stdout 을 `analyze.py` 로 계수. 슬롯 키 = 옛 ⓓ#645 nested 메시지 접두(`` `fn()` 매개변수 `x` `` · `` `fn()` 반환 타입 `` · `` `X` 주석 ``) ↔ 새 #647 메시지 «… 의 값 자리가 `Any`」 접두 — 같은 (경로, 줄) 안에서 라벨까지 일치해야 matched.

## 3. 무손실 · gate 재현

**무손실(`ll/lossless-rerun.log` · 4분)**: scripts diff 4 파일(검사기·`registry_gate.py`·`pregate_symbol_kinds.json`·`rulepack.json` — 나머지 24 검사기 byte 동일) · 저장소 4사본 × 3 검사기 **12/12 OK**(A∖B = ⓓ#645 만 · B∖A = {#646,#647,#650} 만 · api-error 7/6/7/27 · openapi 0 · exit 동일) · 픽스처 «OK 99 · RED 3」 · `VERDICT: RED` — **`impl/lossless1.log` 와 행 단위 동일**. RED 3 의 비허용 A∖B 전수(판형은 5건까지만 인쇄 — 전수는 내가 sink 로 재계수):

| 픽스처 케이스 | 옛 #493 (A∖B) | 파일 | 56b27e1 |
|---|---|---|---|
| `fx.public_surface_good` · `fx.cross.public_surface` | 7 = `admin/order/panel.py` :19 `model`·:20 `form`·:21 `extra`·:25 `list_display`·:26 `readonly_fields`·:27 `inlines` + `admin/shipment/panel.py:17 list_display` | 신설(0B→27줄 · 17줄 신설) | exit 2→0 |
| `fx.public_surface_bad_rules` | 1 = `stub_generic_bad.py:26 inlines` | 신설(36줄) | 28→37(B∖A #647 6·#646 6+ⓓ1·#650 1) |

→ 8/8 이 «신설 파일 + 옛 #493 오탐(별칭·subscript 기저의 선언적 면제 미회복)」 · 저장소 4사본 #493 집합 무변과 정합. **main 픽스처 트리(`impl/lossless_fx_main.py` · `rv3C/fixtures-main`) 재실행 = 9/9 OK · `VERDICT: LOSSLESS`**.

**registry_gate ⓔ2(kkebi · 앵커 HEAD=6608fb0 · dddjango v2.17.17 · 실행 트리 digest `5e1eb5935e8172ab` = 구현 기록 동일 · 각 97초)**:

| run | 변경 | 귀속 | legacy | ⓓ 신규 / legacy / 해소 | exit | sidecar |
|---|---|---|---|---|---|---|
| ① 무해 파일 `docs/rv5c_probe.md` | 비-py 1 | **0** | 512(해소 2) | **0 / 1,269 / 0** | **0** | 키 6(`schema·anchor·experiment_run_id·attributed_lines·records·unmatched_lines`) — **`candidate_*` 부재** |
| ② 새 파일 `application/billing/application_layer/point/get_my_point_balance/rv5c_probe_helper.py`(`x: dict[str, object] = {}` 지역) | py 1 | 1(`check-layer-skeleton #490` — 새 파일이 트리 이름 밖) | 512 | **1 / 1,269 / 0** — `[ⓓ#647] …:N: \`x\` 주석 의 \`dict/Mapping[…, object]\`` | 2(#490 탓 · ⓓ 불산입) | `candidate_lines` 1 · `candidate_records` 1(info #647 `:5`) · `records` 1 = #490 위반만(ⓓ **무포함**) |
| ③ 기존 `get_my_point_balance_use_case.py` `execute()` 첫 줄에 `_rv5c_probe: dict[str, object] = {}` 삽입(아래 줄 전부 +1) | 수정 1(아래 줄 전부 밀림) | **0** | 512(해소 2) | **1 / 1,269 / 0** — `[ⓓ#647] …use_case.py:N: \`_rv5c_probe\` 주석 …` · legacy 1,269 **무변**(줄 밀림이 ⓓ 차분에 0 — `:N` 정규화) | **0**(ⓓ 불산입 실증) | `candidate_lines` 1 · `candidate_records` 1(info #647 `:25`) · `records` **[]** |

①②③ 뒤 `git status`(violations 제외)에 내 파일 없음 — 사본 복원 확인(③ 은 `git checkout -- <file>`). ①은 구현 기록 `gate-kkebi.log` 와 절·수치 동일. ③ 이 Δ14 문면 «앵커=HEAD + 무해 변경 → exit 0 · 귀속 0 · ⓓ 신규 n · legacy ⓓ n 보고」 의 완전형이다. **주의**: ③ 종료 시점(16:16:44) `$S/kkebi` 에 타 리뷰어의 untracked `rv5a_probe.md` 가 관측됐다 — 리뷰어 A 가 같은 사본에서 동시에 gate 를 돌리고 있었다면 내 ②(16:12:28~16:14:02 · `rv5c_probe_helper.py` #490+ⓓ 1)·③(16:15:14~16:16:44 · use_case 수정 ⓓ 1) 이 그쪽 결과에 «귀속 1/ⓓ 신규 1」 로 섞였을 수 있다(파일명 `rv5c_*`·`_rv5c_probe` 로 식별 가능). 내 ①②③ 은 비-py 파일이라 영향 없음. 관찰: 위반 채널 표에서 `check-app-container.py`(kkebi)·`check-idempotency-scope-creep.py`(spring·kkebi) 가 «anchor 2 · current 0」(해소 2·1건) — 구현 기록 로그에도 같으며 이번 조각 밖(앵커 스냅숏 대칭성 · §6-3).

## 4. 소급 · ⓓ 부담 표 (회신 3용 · 새 검사기 실측 · 루트 필터 뒤 · 앵커 격리 전 전량)

### 4-1 소급·legacy (rv3-C §4 갱신 — 수치 전부 재현 · 변경분만 굵게)

| 규칙 | spring HEAD | kkebi HEAD | 격리 채널 | 루트 필터로 빠지는 것 |
|---|---|---|---|---|
| #646 | 18(헤더 17+속성줄 1 · 16 파일 · 8 BC: fortune_intent 4 · accounts 3 · wallet 3 · media_library 2 · notification 2 · query_translation 2 · fortune_record 1 · promotion 1) | 21(21 파일 · 4 BC: tarot 10 · billing 7 · share 2 · top3 2) | N∖L(exit) | 0 |
| #647 차단(줄) | 594(Any 92+framework · object 반환·속성) — framework/technology(rag) **449** · fortune_character 27 · fortune_calculation 24 · chat_relay 17 · promotion 14 · fortune_reading 11 · product 10 | 161(Any 52 · 반환 59 · 속성 52) — saju 54 · billing 36 · product_observability 23 · tarot 20 · share 11 · identity 7 | N∖L(exit) | kkebi web·scripts **0**(실측) · spring docs·scripts·server 0 |
| #647 ⓓ 입구(줄) | 255 — framework 127 · fortune_reading 42 · llm_access 35 · chat_relay 19 · fortune_record 11 · fortune_catalog 9 | 253 — billing 116 · product_observability 30 · tarot 27 · identity 26 · saju 21 · notification 13 (· daily 12) | ⓔ2 N′∖L′(보고) | 〃 |
| #647 반환 object ⓓ(자리표시) | 8 — `_sequence` 2 · `role/content` 2 · `used_at` · `sanitize` · `run_source_boundary` · `_run_key` | 42 — `pull_events` **16** · `_reject_json_constant` 4 · `_require_sequence`·`fetch_merge_journal`·`_parsed_json_or_none`·`build_get_shared_reading` 각 2 · 기타 12 | ⓔ2 | — |
| #650 ⓓ | 40(framework 32 · fortune_calculation 8) | **1**(identity) | ⓔ2 | — |
| `Form.clean -> dict[str, Any]`(#647 차단 legacy · 회신 안내) | 15(fortune_character 4 · service_policy 4 · fortune_intent 2 · media_library 1 · notification 1) | 3(image·share·top3) | N∖L | web 밖 |
| ⓓ#645 nested 잔존(기존 규칙 · 무변) | 7 줄(framework 5 · application 2) | **155 줄**(web 102 · scripts 53 · application 7 — 그중 dict 값 Any 형상 105 = rv3-C) · bare 포함 전체 web 165·scripts 75·application 79·fabfile 8 | 기존 ⓓ | «루트 필터로 대상 밖」 이 아니라 «기존 규칙 그대로」 |
| 브라운필드 update 잎 노출 상한(최근 40 커밋 × 새 ⓓ 파일) | ⓓ 파일 손댄 커밋 **16** · 상한 중앙 0 / 평균 11.6 / 최대 146 | **14** · 0 / 1.7 / 14 | 줄 밀림 0(③) → 실제 귀속 = 개명 슬롯 수 | — |

### 4-2 ⓓ 감수 부담(새 검사기 ⓓ 전량 · 줄 · #645 잔존+#647 입구+자리표시+#650+#69)

| 저장소 | application 합 / BC 수 = 평균 | 규칙 내역(application) | BC 상위 | application 밖 |
|---|---|---|---|---|
| spring | **223 / 16 = 13.9** | #647 133 · #69 43 · #645 40 · #650 8 | fortune_reading 57 · llm_access 40 · chat_relay 27 · fortune_character 21 · fortune_calculation 19 · fortune_catalog 13 · fortune_record 13 · promotion 10 | framework/technology 213 · docs 10(#69) · fabfile 6 |
| kkebi | **485 / 12 = 40.4** | #647 294 · #69 112 · #645 79 · #650 1 | billing 143 · saju 104 · tarot 65 · identity 50 · product_observability 46 · daily 33 · notification 18 | web 166 · scripts 134 · fabfile 8 |

ⓔ2 뒤 «신규분만」 = run ① **0** — 위 전량이 legacy 로 접힌다(gate 의 ⓓ legacy 1,269 는 27 검사기 합 · public-surface 만 794 줄). 새 BC 산출 시 예상 ⓓ(형상별 · kkebi 형상 기준): 애그리거트당 `pull_events -> list[object]` 1(문면 «도메인 이벤트 union `list[<Bc>Event]`」 로 닫힘) · JSON 값 도우미 `-> object` 0~2(`JsonValue`) · 좁히기 도우미 0~1(`TypeIs`) · 프레임워크 콜백 미러 0~1(문면 «통과」) · `dict[str, object]` 입구 매개변수/지역 변수는 유스케이스당 1~3(R-3448 즉시 좁힘 물음) — 레인당 3~8 예상(spring 8.0 · kkebi 21.0 은 legacy 밀도).

## 5. 효과 수치 (rv1-C §5 정직화 문구 — 새 검사기로 재확인)

| 문구 | 새 검사기 실측 | 판정 |
|---|---|---|
| S-1 «8/10 레인 은폐 18줄 예방」 | spring HEAD #646 **18** = `# type: ignore[type-arg]` 헤더 17 + 속성줄 1 · 16 파일 · **8 BC** | ✓ |
| S-1 «1/10 레인 mypy 26」 | d2eaafe #646 **31** − HEAD 18 = **13** = fortune_character 맨몸(ⓐ) 13 클래스(S1 «맨몸 13」 · mypy 26 은 그 10 파일) | ✓(검사기는 클래스 13 · mypy 는 오류 26 — 단위 다름을 병기) |
| S-1 «왕복 0」 | 검사기 밖(레인 관측) | 재측정 없음 |
| S-4 «레인당 Any 누수 ≈6」 | application #647 **Any 차단 92 줄 / 16 BC = 5.8**(fortune_character 27·fortune_calculation 24·chat_relay 17·promotion 14 …) | ✓ |
| S-4 «object 반환/속성 ≈3 예방」 | application #647 object 차단 **53 줄**(반환 35 · 속성 18) / 16 = **3.3** | ✓ |
| S-4 «ⓓ 감수 ≈7/BC(kkebi ≈24)」 | #647 ⓓ 입구 spring **128/16 = 8.0**(+자리표시 5) · kkebi **252/12 = 21.0**(+42 = 24.5) · 전 ⓓ 규칙 합은 13.9 / 40.4(§4-2) | ✓(«≈8 / ≈21(+자리표시 ≈4)」 로 갱신 · ⓔ2 뒤 legacy 0 병기) |
| S-4 «mypy 빚 67/70 은 발주측 RAG」 | 재측정 안 함 · 검사기 #647 차단 594 중 `framework/technology` **449(76%)** · ⓓ 입구 255 중 127(50%) | 방향 일치 |

## 6. 사각 · 미확인

1. `make verify` 는 재실행하지 않았다(218초 · working tree 무접촉 제약 — `manifest draft` 등 쓰기 경로) — `impl/verify1.log` 6/6 에 의존. 검사기·`registry_gate.py` 가 HEAD·56b27e1·codex 미러와 byte 동일임은 확인.
2. 무손실 판형 사본(`ll/`)은 `rv3C/lossless.sh` 와 R 경로만 다르다 — 스크립트 본문 동일(`cp`) · 결과 로그 행 단위 동일이 근거.
3. ⓔ2 gate 표의 «anchor 2 → current 0」(`check-app-container`·`check-idempotency-scope-creep`) 은 앵커 스냅숏과 working tree 의 비대칭(무시 파일·비-git 스냅숏)일 가능성 — 사본 ignored 파일 0 · 이번 조각 밖 · ⓓ 채널은 해소 0 이라 영향 없음. 별도 추적 권고.
4. 슬롯 1:1 은 메시지 접두 파싱에 의존한다(`매개변수 \`x\`` · `반환 타입` · `\`X\` 주석`) — `*args/**kwargs` 도 같은 어휘라 통과했으나 새 슬롯 어휘가 추가되면 `analyze.py` 의 접두 표를 갱신해야 한다.
5. 브라운필드 상한은 rv3-C 판형(손댄 파일의 ⓓ 줄 합)과 같고 ⓓ 집합만 새 검사기로 바뀌었다 — 커밋 diff 가 그 def 줄을 실제로 바꿨는지는 여전히 안 봤다(③ 의 줄 밀림 실증으로 방향만 닫음).
6. mypy 는 돌리지 않았다 — §5 의 «mypy 26」·«67/70」 은 S1/S4 수치를 인용했고 검사기 수치와의 단위 차(클래스 vs 오류)를 병기했다.
7. 사본은 리뷰어 A·B 와 동시 공유됐다 — 종료 시점 `$S/spring` 에 `mp_probe_rv5b/`(B) · `$S/kkebi` 에 `rv5a_probe.md`(A · 이후 제거됨) 관측. 내 계수는 `mp_probe_` 접두 제외(판형 규칙)이고 spring old/new 레코드 4,097/4,537 이 구현 기록과 일치해 오염 0 으로 판단 · gate ①~③ 은 kkebi 라 B 무관 · A 의 비-py 파일은 무영향. 역방향(내 ②③ 이 A 의 gate 에 섞였을 가능성)은 §3 주의 참조.
