# rv5-2-C — ⑤-2 조각 2(S-5 + ⓔ1 · `d701df8` + 정정 `cad221b`) 구현 리뷰 · 리뷰어 C(증거·표본 외 축 — 실측 재현·무손실·회신 재료) · 2026-09-04

대상: 커밋 `d701df8`(검사기 `check-api-error-controller-contract.py` #648/#649 · `check-openapi-error-declaration.py` 문면 2 · `check-public-surface-annotation.py` ⑤-1 정정 · `registry_gate.py` · 픽스처·온톨로지) + 정정 `cad221b`(봉인 재발행·verify4·기록) · 구현 기록 `evidence/impl/piece2-summary.md` · 회신 3 초안 `workspace/plan/2026-09-04-field-report-reply-3.md`. 실서고 무접촉 — 실행은 격리 사본 `$S/fr3/{spring(7bfe1aa)·spring-d2eaafe·spring-f5ee428·kkebi(6608fb0)}`(각 실서고 venv · cwd=사본) · 산출 `$S/rv5C2/`(무손실 판형 `ll/` = `rv3C/lossless.sh`+`lossless_fx.py`+`lossless_diff.py` 를 R 만 바꿔 복사 · `rv5c2_analyze.py` 계수 · `rv5c2_gate_run.sh` ⓔ2 · `rv5c2_mypy.log` · `rv5c2_smoke.log` · `rv5c2_openapi_codejson_*.txt` · `rv5c2_kkebi_nofilter.jsonl` · 이전 중단 시도의 산출은 `prev/` 로 격리). 임시 파일(`rv5c2_probe.md`·`rv5c2_mini/`·`rv5c2_scripts/`)은 실행 뒤 제거 · 4사본 `git status` 에 내 파일 0(spring 의 `mp_probe_rv5b/` 는 리뷰어 B 잔존물 · 계수에서 제외). 새 검사기 HEAD = `d701df8` 이후 무변(`cad221b`·`b541870` 은 workspace 만) · codex 미러 6파일 byte 동일 `cmp` 확인. Serena: skipped — 리서치·재계산(코드 수정 없음 · `.serena/project.yml` 부재).

## 1. 판정 표

| # | 항목 | 판정 | 근거(요약 · 상세 §2~§5) |
|---|---|---|---|
| C-1 | 4사본 실측 재현 — #648/#649 건수·파일:줄 = ⓪ S5 ②표 | **검증됨** | `--error-profile auto` 새 검사기: #648 spring **7**(accounts 6 · fortune_record 1) · d2eaafe **8** · f5ee428 **8**(+fortune_reading `evidence_provisioning_controller.py:159`) · kkebi **6**(identity 2 · review 2 · saju 2) · #649 d2eaafe/f5ee428 **1**(`schema_out.py:151`) · HEAD·kkebi 0 — 파일·함수·def 줄 전부 S5 ②표와 일치(§2) |
| C-2 | openapi 검사기 `auto` 출력 byte 동일 · public-surface 4사본 계수 = 조각 1 기록(⑤-1 정정 뒤) | **검증됨 + MINOR(M4)** | openapi auto: 4사본 old/new stdout **0 byte 양쪽 빈 출력**·레코드 0 → «byte 동일» 은 공허(문면 변경은 code-json 경로에만 — 내가 f5ee428 code-json old/new 로 확인: `[#63]` 2줄 동일 · 조치 1줄만 차이 = 의도한 stale 정정). public-surface: #493 3,216/3,225/3,225/173 · #646 18/31/18/21 · #647 차단 594/585/603/161 · ⓓ 입구 255/261/261/253 · 자리표시 8/9/9/42 · #650 40/38/40/1 — **전 셀 일치** |
| C-3 | 무손실 재실행(슬롯 키 판형) · main 픽스처 9/9 | **검증됨** | `ll/lossless.sh main worktree` 재실행 → 판정 행 `impl/lossless2-verdict.txt` 와 **행 단위 동일**(diff 0) · 12/12 OK · 픽스처 «OK 99 · RED 3»(⑤-1 과 같은 신설 파일의 옛 #493) · scripts-diff 6파일 · `git archive main` 픽스처 트리 재추출 → **9/9 · `VERDICT: LOSSLESS`** |
| C-4 | gate ⓔ2(kkebi · 무해 파일 · `--anchor HEAD --introduced-json`) | **검증됨** | «ⓓ 신규 0 · legacy 1,269(검사기별 14행 분해) · 귀속 0 · exit 0» · 로그 = `impl/gate2-kkebi.log` 와 **동일**(툴체인 행 포함 · 실행 트리 digest `a268e474f016714c`(39파일)) · sidecar `candidate_lines: []`·`candidate_records: []` **키 존재** · sidecar 8키 byte 동일 · 실행 뒤 `docs/rv5c2_probe.md` 제거·사본 clean |
| C-5 | 회신 3 초안 수치(§2 ②④⑤⑥⑦⑧ · §3) | **검증됨 + MINOR 2(M1 scripts 212→218 · M2 «레인 4개»↔«1/7 레인»)** | §4 표 — 검사기 계수 44셀 중 **틀린 것 1**(§2 ⑤ kkebi `scripts/` 212 → **218**) · 서술 불일치 1(§1 «레인 4개 반복» vs §3 «1/7 레인» — 첫 도입 커밋은 **7**) · kkebi base 31 → #63 은 **실행으로 확인**(identity 16 · saju 9 · review 5 · image 1) · `Form.clean -> dict[str, object]` 면제는 mini 픽스처로 실증 |
| C-6 | 정직 기록(d701df8 «verify 6/6» 거짓 → cad221b 정정) | **검증됨** | `verify4.log` 실재·6/6 green(base-core 69초 · base-cross 234초) · `verify3.log` 는 d701df8 에 이미 RED 로 커밋됨(«봉인 후 변경 — construct_drift_report.py · tree_sha256 드리프트» · d701df8 의 기록은 그것을 «6/6 green» 이라 적음 = 자기모순) · manifest diff 가 원인과 정합: `construct_drift_report.py` 실제 sha 는 06fef51→d701df8 에서 바뀌었는데(`ce6097…→7e1c59…`) manifest 항목은 d701df8 에서 `ab6efaf…` 그대로(sealed_commit 06fef51) → cad221b 에서 `c63e987…`·sealed_commit d701df8 로 재봉인 — «골든 갱신 뒤 봉인» 순서 착오 서술 그대로 |
| C-7 | smoke 33/33 · mypy 재현 | **검증됨** | `registry_gate_smoke.py` 독립 실행 **33/33**(2분 20초) · mypy(각 venv · cwd=사본): f5ee428 `fortune_reading` **31건/7파일**(그중 S-5 = return-value 5 · :151 metaclass+no-untyped-call · call-arg root 2 = **9**) · HEAD 같은 경로 **0** · HEAD `accounts`+`fortune_record`(상자 둘 7 함수) **0**/397 · kkebi 상자 둘 BC 4경로 **0**/295 |
| C-8 | openapi 검사기 stale 문면 잔존 | MINOR(M3) | 정정 2곳(`:5~7` docstring · `:3362` 조치)은 확인 · 그러나 `:3359` 헤더 «response= <Bc>ErrorSchema 계약 불일치» · `:3372` 주석 · `:3478` 메시지 «오류 응답은 `response={status: <Bc>ErrorSchema}` 로 직접 선언한다» 가 남음(계획 §2.3 «`:3371` 검토» 권장분) — 축이 «직접 선언 vs 후처리» 라 R-0681 rev2 와 정면 모순은 아님 · 이월 가능 |

**BLOCKER 0 · MAJOR 0 · MINOR 4(M1~M4).**

## 2. 실측 재현 표 (구현 기록·S5 vs C · 새 검사기 HEAD × 4사본)

### 2-1 api-error(`--error-profile auto`) · openapi(auto)

| 사본 | 레코드 old→new · exit | #648 (파일:def 줄) | #649 | S5 ②표 대조 | openapi auto old/new |
|---|---|---|---|---|---|
| spring 7bfe1aa | 7→14 · 0→2 | **7** — `accounts/…/account_controller.py` :173 `register_account` · :313 `reset_password` · :359 `change_password` · :399 `get_my_profile` · :459 `update_my_profile` · :545 `withdraw_account` · `fortune_record/…/record_archive_controller.py:94 get_fortune_record` | 0 | 함수 7 동일(accounts 좌표는 S5 f5ee428 def 줄 +10 = HEAD `birth_place` 증분) | stdout 0B/0B · exit 0/0 |
| d2eaafe | 6→15 · 0→2 | **8** = 위 accounts 6(:163·303·349·389·438·504) + fortune_record :94 + `fortune_reading/…/evidence_provisioning_controller.py:159 prepare_evidence_bundle` | **1** `…/schema/schema_out.py:151 EvidenceProvisionResponseSchema` | S5 «f5ee428 8 함수·ⓒ 1» 좌표 동일 | 0B/0B |
| f5ee428 | 7→16 · 0→2 | **8**(d2eaafe 와 같은 좌표) | **1**(:151) | 동일 | 0B/0B |
| kkebi 6608fb0 | 27→33 · 0→2 | **6** — identity `profile_controller.py:127 record_first_touch` · `web_session_controller.py:452 refresh_web_session` · review `review_controller.py:192 create_review` · `:246 delete_review` · saju `reading_controller.py:145 start_reading_generation` · `relationship_controller.py:227 delete_relationship_profile` | 0 | 6 좌표 동일 | 0B/0B |

B∖A = #648/#649 만 · A∖B 0 · exit 0→2 는 신규 규칙 라인이 있는 사본만(4/4) — 구현 기록 문면 그대로.

### 2-2 public-surface(줄 기준 · 루트 필터 뒤 · 조각 1 기록 «⑤-1 정정 뒤» 대조)

| 항목 | spring | d2eaafe | f5ee428 | kkebi |
|---|---|---|---|---|
| #493(집합 동일) | 3,216 | 3,225 | 3,225 | 173 |
| #646 | 18(헤더 17 · 속성줄 1 · 16 파일 · 8 BC) | 31(9 BC · +fortune_character 13) | 18 | 21(헤더 21 · 4 BC) |
| #647 차단 줄(레코드) | 594(733) · Any 518 · object 78(반환 60 · 속성 18) | 585(722) | 603(742) | 161(166) · Any 52 · object 111(반환 59 · 속성 52) |
| #647 ⓓ 입구 줄(레코드) | 255(296) · application 128 · framework 127 | 261(302) | 261(302) | 253(265) · application 252 · framework 1 |
| #647 자리표시 object | 8 | 9 | 9 | 42 |
| #650 ⓓ | 40(framework 32 · application 8) | 38 | 40 | 1 |
| 루트 분포(#646/#647/#650) | application·framework 만 | 〃 | 〃 | web·scripts **0** |

## 3. 무손실 · gate 재현

**무손실(`$S/rv5C2/lossless-rerun.log` · 17:03~17:07)**: `git archive main` 옛 검사기 vs working tree(= HEAD 검사기) · scripts-diff **6파일**(검사기 3 · `registry_gate.py` · `pregate_symbol_kinds.json` · `rulepack.json` = 이번 변경 전부) · 저장소 4사본 × 3 검사기 **12/12 OK** · 픽스처 «OK 99 · RED 3» · `VERDICT: RED`(RED 3 = ⑤-1 과 동일한 신설 픽스처 파일의 옛 #493 8건) — 판정 행 전부 `impl/lossless2-verdict.txt` 와 **행 단위 동일**. main 픽스처 트리(`git archive main workspace/eval/fixtures` 재추출 46 루트 · `lossless_fx_main.py` R 경로만 교체) **9/9 OK · `VERDICT: LOSSLESS`**. 로그의 spring old 레코드 4,103 vs 판정 4,097 차이 6 = `mp_probe_rv5b/`(리뷰어 B 잔존 untracked) — 판형 `EXCLUDE_PREFIX` 가 제외(계수 영향 0 · new 4,537 은 기록과 동일).

**gate ⓔ2(kkebi · `rv5c2_gate_run.sh` · 17:04:12~17:06:01 · 앵커 HEAD=6608fb0 · 무해 파일 `docs/rv5c2_probe.md` 1)**: 위반 채널 «귀속 0 · legacy 잔존 518 · 해소 2» · ⓓ 채널 «**신규 0 · legacy 1,269 · 해소 0** — 검사기별 14행(public-surface 573 · domain-model 363 · port-adapter 133 · usecase-dto 75 · layer-skeleton 56 · api-error 16 · event-publish 13 · naming 13 · business-vocab 7 · missable-entrance 7 · context-isolation 6 · transaction-boundary 5 · broker 1 · composition-root 1)» · exit **0** · 로그 = `impl/gate2-kkebi.log` 와 diff 0(툴체인 행 `v2.17.17 · py3.14 · digest a268e474f016714c(39파일)` 포함) · sidecar = `impl/gate2-kkebi-introduced.json` 과 byte 동일(`schema·anchor·experiment_run_id·attributed_lines·records·unmatched_lines·candidate_lines·candidate_records` 8키 · `candidate_*` 빈 목록 존재 — ⓓ legacy ≠ ∅ 규칙). 실행 시작 시 kkebi 사본에 타 리뷰어 파일 0 · 종료 뒤 probe 제거 · clean.

**smoke(`rv5c2_smoke.log`)**: `registry_gate_smoke.py` 독립 실행 «케이스 33 · 일치 33 · 불일치 0 · exit 0»(Q ⓓ 앵커 차분 · Q′ ⓓ+위반 동반 포함).

## 4. 회신 3 초안 수치 정정 표 (항목 · 초안 값 · 실측 값 · 판정)

| 절 | 항목 | 초안 값 | 실측 값(새 검사기 HEAD · 격리 사본) | 판정 |
|---|---|---|---|---|
| §1 S-5 | 상자 둘 반복 규모 | «08-25 이후 레인 4개 반복 · spring 7·kkebi 6 함수» | 함수 7·6 ✓ · 첫 도입 커밋(blame) **7** = spring accounts `06346ff`(+슬라이스 3981d49·43d8ae4·452e1f9 같은 레인) · fortune_record `eda6b96` · fortune_reading `585c9c6` · kkebi identity `cb3f4ad`(**08-24**) · identity web_session `c2b2bfd` · review `fb14fa2` · saju `65c1ffd` → 08-25 이후는 6 | **정정**: «레인 4개» → «레인 7(08-25 이후 6)» 또는 «4개 이상» — §3 «1/7 레인» 과 맞춘다(M2) |
| §2 ② | #646 legacy spring | 18줄(16 파일 · 8 BC: fortune_intent 4 · accounts 3 · wallet 3 · media_library 2 · notification 2 · query_translation 2 · fortune_record 1 · promotion 1) | **동일**(헤더 17 + 속성줄 1) | ✓ |
| §2 ② | #646 legacy kkebi | 21줄(4 BC: tarot 10 · billing 7 · share 2 · top3 2) | **동일**(헤더 21 · 21 파일) | ✓ |
| §2 ④ | spring #647 차단 | 594 · framework/technology 449 · application 145(fortune_character 27 · fortune_calculation 24 · chat_relay 17 · promotion 14 · fortune_reading 11 · product 10) | **동일**(594 = 449 + 145 · BC 6 순서·값 동일) | ✓ |
| §2 ④ | spring ⓓ 입구 | 255(framework 127 · fortune_reading 42 · llm_access 35 · chat_relay 19 · fortune_record 11) | **동일** | ✓ |
| §2 ④ | spring 자리표시 · #650 | 8 · 40(framework 32 · fortune_calculation 8) | **동일** | ✓ |
| §2 ④ | kkebi #647 차단 | 161(saju 54 · billing 36 · product_observability 23 · tarot 20 · share 11 · identity 7) | **동일** | ✓ |
| §2 ④ | kkebi ⓓ 입구 · 자리표시 · #650 | 253(billing 116 · product_observability 30 · tarot 27 · identity 26 · saju 21) · 42(`pull_events -> list[object]` 16) · 1 | **동일**(`pull_events()` 16 · `_reject_json_constant()` 4 …) | ✓ |
| §2 ④ | `Form.clean -> dict[str, Any]` 18(spring 15 · kkebi 3) · «`dict[str, object]` 로 바꾸면 면제» | 18 | `clean()` 반환 Any #647 차단 **15**(fortune_character 4 · service_policy 4 · fortune_intent 2 · media_library·notification·product·promotion·query_translation 1) · **3**(image·share·top3) · mini 픽스처: `forms.Form.clean -> dict[str, object]` 발화 0 · `-> dict[str, Any]` #647 1 | ✓(면제 실증) |
| §2 ④ | «2차 정리(RAG 822줄)» | 822 | 검사기 밖(S4 수치 인용) — 재측정 안 함 | 미검증(S4 몫) |
| §2 ⑤ | kkebi `web/` 대상 밖 | 111줄 | 루트 필터 해제 탐침(`_in_rule_roots → True`): web #647 차단 104 + ⓓ 7 = **111** | ✓ |
| §2 ⑤ | kkebi `scripts/` 대상 밖 | **212줄** | scripts #647 차단 39 + ⓓ 186(자리표시 포함) + #650 1 → 서로 다른 줄 **218**(같은 줄 차단∧ⓓ 7) | **정정 212 → 218**(M1 · ⑤-1 정정 N-3 등으로 ⓓ 집합이 바뀐 뒤 재계수 안 됨) |
| §2 ⑤ | web/scripts #645 ⓓ nested 잔존 | 155 | **155**(web 102 · scripts 53 · bare 포함 240) | ✓ |
| §2 ⑥ | 리딩 400/503 base 선언 #63 2건 | 2 | code-json(HEAD·f5ee428) `[#63]` **2**(400 → InvalidRequest · 503 → Registry\|ResourceLimit\|Temporary) | ✓ |
| §2 ⑦ | 상자 둘 spring 7 · kkebi 6 내역 | accounts 6 · fortune_record 1 / identity 2 · review 2 · saju 2 | **동일** | ✓ |
| §2 ⑦ | kkebi base 31 → code-json #63 | 31(identity 16 · saju 9 · review 5 · image 1) | code-json **실행**(BC 별 컨트롤러 전부 selector): identity **16**(session 10 · account 3 · web_session 2 · profile 1) · saju **9** · review **5** · image **1** = **31** · 전건 `wrong-response-schema` | ✓(«돌리면 #63» 실증) |
| §2 ⑧ | spring `4cfedb4` 상환 · kkebi `TarotCardOut` 선례 | — | `4cfedb4 fix(fortune_reading): ninja Status 반환 주석·RootModel 단독 상속 정리` 실재 · `tarot/…/schema_out.py:50` · e2e discriminator 단언 실재 | ✓ |
| §3 S-1 | ignore 17+1(spring) · 21(kkebi) | — | 헤더 17 + 속성줄 1 · 헤더 21 | ✓ |
| §3 S-4 | Any 누수 ≈6(92줄/16 BC) | 92/16 | application #647 Any 차단 **92 줄** / BC **16** = 5.75 | ✓ |
| §3 S-4 | object 반환/속성 ≈3(53/16) | 53/16 | application object 차단 **53**(반환 35 · 속성 18) / 16 = 3.3 | ✓ |
| §3 S-4 | ⓓ 감수 ≈8/BC · kkebi ≈21 | 128/16 · 252/12 | ⓓ 입구 application **128**/16 = 8.0 · **252**/12 = 21.0(+자리표시 5 · 42) | ✓ |
| §3 S-4 | 449/594 = 76% | 76% | 449/594 = 75.6% | ✓ |
| §3 S-5 | «red 는 concrete 직접(리딩 1/7 레인) · 13 함수 mypy 통과» | — | f5ee428 `fortune_reading` mypy return-value 5(+ :151 2 + root 2 = 9) · HEAD 0 · spring HEAD accounts+fortune_record **0**/397 · kkebi 상자 둘 4 BC 경로 **0**/295 → 13 함수 mypy-clean | ✓(§1 «4개» 만 정정) |

## 5. 사각 · 미확인

1. `make verify` 는 재실행하지 않았다(manifest 등 쓰기 경로) — `verify4.log` 6/6 + 봉인 manifest 해시 정합(§1 C-6) + smoke 33/33 독립 재현 + 픽스처 무손실 9/9 로 대체. 대표 byte 골든(`construct_drift_report.py` 8/8)은 verify4 base-core green 에 의존.
2. openapi `auto` «byte 동일» 은 빈 출력끼리의 동일이다(M4) — 문면 정정의 실증은 code-json 경로(f5ee428 old/new 조치 1줄 차이)로 대신했다. 기록에 «auto 는 stdout 0B · 문면은 code-json 으로 확인» 병기를 권한다.
3. «7 레인» 은 blame 의 첫 도입 커밋 7 로 셌다 — accounts 슬라이스 4 커밋을 한 레인으로 접었고, kkebi identity 두 파일(08-24 `cb3f4ad` · 08-25 `c2b2bfd`)은 별개 커밋이라 2 로 셌다. 레인 정의(발주 단위 vs 커밋)에 따라 6~8 사이로 흔들릴 수 있어 회신은 «7(커밋 기준)» 또는 «4개 이상» 으로 못 박는 편이 안전하다.
4. 루트 필터 해제 탐침은 검사기 사본 1줄 패치(`return True`)로 돌렸다 — 다른 경로 의존이 없어 web/scripts 계수는 새 규칙의 실제 사각 규모지만, 검사기 정본에는 그런 옵션이 없으므로 회신 수치는 «탐침 기준» 임을 알아둔다.
5. kkebi code-json 은 BC 별 `*_controller.py` 전부를 `--controller-module` 로 넘겼다(scope 이름 `public-v1` 은 픽스처 관례 차용) — 31 이 전부 나왔으므로 selector 누락은 없으나 spring 은 리딩 컨트롤러 1개만 돌렸다(S5 와 같은 범위).
6. 사본은 리뷰어 A2·B2 와 동시 공유됐다 — 내 gate 실행 창(17:04~17:06)에 kkebi 에 타 리뷰어 파일 0 을 확인했고, 무손실 실행 중 spring 의 `mp_probe_rv5b/`(B) 는 판형이 제외했다. 역방향(내 `rv5c2_probe.md` 가 타 리뷰어 gate 에 섞였을 가능성)은 비-py 파일이라 영향 0.
7. `.dddjango/violations/*.jsonl` sink 파일이 4사본에 untracked 로 누적된다(이번 세션 전 리뷰어 공통) — 계수·gate 에 영향 없음(gate 는 `DJR_VIOLATIONS_DIR` 해제 · 트리 스캔은 `.py` 만).
