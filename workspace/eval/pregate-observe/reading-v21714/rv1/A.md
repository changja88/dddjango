# 수리 배치 3 · 1단계 적대 리뷰 A — R-5d(update 대상 symbols 미실체화)

- 리뷰어: A · 2026-09-03 · 저장소 무수정(읽기 + 스크래치 실행만). 실험 러너·산출: `scratchpad/b3/rv1/run_p1.py`(monkeypatch — 실행기 원본 무접촉) · `p1-{dedupe,naive}-{e6fb491,final}.{md,stdout}`.
- 판형: 배치 2 루브릭 §1(ⓐⓑⓒ)·§3(3축)·심각도(BLOCKER/MAJOR/MINOR/검증됨).
- Serena: skipped — 리뷰·스크래치 실험 작업이라 기본 도구로 충분(`.serena/project.yml` 부재).

## 1. 항목별 판정 표

| 항목 | 판정 | 한 줄 근거 |
|---|---|---|
| ⓐ(1) 코드 지점 — update 칸 symbols 미실체화 | **검증됨** | `design_pregate.py:466-470` 비-add 칸은 `entry.declared` 만 남기고 `continue`(symbols 전사 폐기) · `:1023` `update` → `unsimulated` 만 기록 · docstring `:17-20`(② 화이트리스트 한정)·`:43`(«스텁 전사는 add 소비자만») · 설계 D2 `2026-09-01-pregate-design.md:61` |
| ⓐ(2) reading #107 = 이 한계의 산물 | **검증됨** (계수 정정 MINOR) | 기준선 d892894 `api_router.py` = **0B 자리표시자**(`git show` 공백) · 명세 e6fb491 L918 `update api_router.py` + L980 symbols `register_fortune_reading_api(api: NinjaExtraAPI) -> None` + L994 imports · 검사기 tree 레인 `check-composition-root.py:2103-2111` «지금 함수 0개» · 처분표 L77 사유가 update 미실체화 명시 · WIP 오버레이에 함수가 생기자 소멸(L1455) · 수리판 재실행 A 동일 ID · **P1 실험: 스텁 병합 시 #107 소멸·#188 잔존**(2→1). 단 «20회 재처분»은 예보 등장 20회이고 **실기재 처분은 14회**(표 행 7 + «stable filtered» 메모 7) |
| ⓐ(3) 레인 3 G1′ «update-only라 예보 0» | **MAJOR** | 실측 출력은 «예보 0»이 아니라 **형식 red ×2**(기실현 add 충돌 — 리포트 4·5차) · G1′ 델타 = conftest.py update **+ K1(add 칸 예외 base 변경)·K2(add 칸 import)** 라 update-only 도 아님 · «예보 0»은 레인의 자가 추론 문면 · 레인 3 update 5행 중 **symbols 선언 0행** → 실체화할 것이 애초에 없어 R-5d «발화»가 아니라 무사건 · G2 귀속 0(REPORT L27) → 손실 0. ⓪ «충족(2레인·구조적)»의 2번째 레인은 관측 사건이 아닌 구조 추론 — 관측 기준으로는 **1레인(reading)** |
| ⓐ(4) «장수 레인 add 42→0 수렴» | **MAJOR** | 교란 요인 2개: ① 형식 red 6/6 = 기실현 add 충돌을 **add→update 개서**로 회피(ledger 레인 R) — v2.17.16 `lift_realized_adds`(`:960`)면 스텁 대체·개서 불요 ② `--base` 가 44회 동안 **15개 SHA 로 이동**(d892894→…→80431d9) — R-3432 «G1 기준선 SHA 고정» 위반 판형이라 커밋된 add 가 기준선 트리에 실존→충돌. 증거: 최종 명세 update+symbols 9행 중 **8행이 e6fb491 시점 add 행**(schema_in/out·evidence_retrieval_port·request 계약·validate_citations_use_case·fake 3) — 처음부터 update 였던 것은 api_router.py 1행. 잔존 구조 사실: 브라운필드 레인은 개시부터 update 다수(30/72)지만 symbols 동반은 1행 |
| ⓑ P1 병합(dedupe 조건부) | **검증됨** | e6fb491: 2건→1건(#107 소멸·진탐 #188 보존·composition-root 0/0·#111 미발화) · final: skip 불변(9행 전부 기실존 → 병합 생략). 조건 5개 필수(§3) |
| ⓑ P1 병합(naive — 중복 무시) | **BLOCKER** | final 80431d9 에서 **신규 오탐 4건**: #107 «지금 함수 2개»·#157 계약 공개 클래스 2·#219 port 공개 클래스 2·#635 진입점 클래스 2 — 전부 중복 정의 아티팩트(`p1-naive-final.stdout:56-59`) |
| ⓑ P2 규칙별 선언 면제 | **MAJOR** | 시뮬레이션 없이 출력 억제 — 규칙별 하드코딩(#107→#593/#635/#188 …)이 실행기 안에 검사기 지식 사본을 만든다(D1 «검사기 무접촉»은 지키나 코퍼스 이중화) · «등록 함수 개명(구 이름 잔존)» 진탐을 가린다 · 비일반 |
| ⓑ P3 Coordinator 이월 규범 | **MINOR** | 무손실 자명·실행기 무변경. 효과 = reading 14행(≈≤15분/26h·<1%)·레인 1~3 0. N-1(#188 filtered 26회→③형 재발)이 보여주듯 재기재도 이월도 오처분을 못 잡는다 — 이월 조항은 «최초 근거 절 ID 참조 + 경로·규칙 문맥 변동 시 재판정» 단서 없이는 R-3433 근거 병기 의무를 약화. R-5d 커버 주장과 무관(노동만) |
| ⓑ P4 architect «새 이름은 add 신규 모듈로» | **BLOCKER** | 동기 사례 자체가 불가능 — registrar 칸은 `application/<bc>/driving_layer/api/api_router.py` 고정(`check-composition-root.py:1386-1399 _registrar_spec`·final.md 트리 9행) · 나머지 8행도 고정 칸(port·schema·contract·use_case·fake). 도구 커버를 위해 모듈을 쪼개는 설계 왜곡 = 품질 훼손 |
| ⓒ 커버 이득 크기 | **MAJOR(과대)** | update+symbols 행: reading G1시점 **1/30** · final 9/73(8행은 기실현 add → dedupe 생략 → 효과 0) · 레인 1 **0/2** · 레인 2 **0/7** · 레인 3 **0/5**. 4레인 합계 실효 1행 = 오탐 ID 1개(#107) 소거 |
| ⓒ 재처분 노동 | **MINOR** | 14행(각 1줄·Codex 저술·개정 사이클 내) — 23:43Z(run 2)~익일 01:10 KST 사이 ≈26h 레인 대비 ≤15분 |
| ⓒ «③형 STOP 예방» 근거 | **MAJOR(근거 없음)** | 레인 1~3 G2 귀속 0/0/0 · reading STOP-149 의 update 행 파일 귀속(prepare_fortune_evidence_use_case.py #635 · citation_validation_service.py #474/#153)은 그 update 행에 **symbols/imports 선언 0**(`declared=[]`) + #474/#153 은 C급 본문 규칙 → P1 이 있었어도 예측 0/149. 실제 ③형(#188)은 add 쪽 area 규칙(N-1 소관) |

## 2. 반례·근거 인용

### 2.1 코드 지점(ⓐ1)
- `dddjango/scripts/design_pregate.py:466-470`
  ```python
  if entry.tag != "add":
      plan.notes.append(f"symbols 미반영(비-add `{entry.tag}` 칸 — 스텁 전사 밖 · update 대상이면 계약 실존의 «자기 update 해소» 근거로만 쓴다): {path}")
      continue
  ```
- `:1023` `elif entry.tag == "update": report["unsimulated"].append(f"update(시뮬레이션 밖 — ② 화이트리스트 정형 append 한정): ...")`
- `:1172-1174` `_realize_module` — update 는 사본 실물(표면 = 이 명세 «이후» 상태라는 문면과 실제 표면 = «이전» 상태의 괴리가 S′ 라벨로만 봉합됨).
- 설계 정본 `workspace/design/2026-09-01-pregate-design.md:61` «`update`: 실물 보존 + append만 — ② 화이트리스트의 정형 배선 1줄류에 한정».

### 2.2 reading #107(ⓐ2)
- 기준선 실물: `sds$ git show d892894:application/fortune_reading/driving_layer/api/api_router.py` → **0바이트**(표준 트리 고정 파일 자리표시자 — STOP-149 L69 도 fortune_calculation 의 같은 4파일을 «0-byte fixed file»로 기술). `80431d9` 에서는 registrar 실존.
- 명세 e6fb491: L918 `update application/fortune_reading/driving_layer/api/api_router.py` · L980 symbols · L994 imports `from ninja_extra import NinjaExtraAPI` · L1007 산문이 «현재 pre-gate가 non-add symbol/import를 의도적으로 미실체화하므로 #107은 update projection 정보 결손에 의한 filtered» 라고 자가 진단.
- 검사기: tree 레인 `check-composition-root.py:2103-2111` `reg_fns = [...]; if len(named) != 1 or ...: findings.add("#107", rel, "... (지금 함수 {len(reg_fns)}개)")`. code 레인 `#111`(`:1573-1577`)은 `config.registrar_modules`(`:1686-1690`) 등재 registrar 에만 돌아 미마운트 BC 에선 미평가 → 본문 `raise NotImplementedError` 스텁이 #111 로 «이동»하지 않음(실험 확인: composition-root anchor 0 / current 0).
- 리포트: `.dddjango/20260831-2331-fortune-reading/pregate-report.md` L20(초회 예보)·L77(처분 사유)·L942(«stable filtered»)·L1455(«WIP의 api_router.py가 exact registrar를 materialize하여 미발행 — dirty-overlay 관찰»). 계수: `grep -c '^| \`92767435ca49\`'`=7 · «stable» 메모 7 · 예보 항목 행 20.
- 수리판 재실행 A(`reading-v21714/rerun-v21716-e6fb491-base-d892894.md`): 동일 ID 2건 + «채널 메모: symbols 미반영(비-add update 칸…): api_router.py» — 한계 명시.

### 2.3 레인 3(ⓐ3)
- `.dddjango/20260902-1842-notification-email-template/pregate-report.md` 4차(11:46Z)·5차(11:47Z) 판정 = **형식 red**(add 충돌 실존) · 말미 «G1′ 개정 pre-gate 처분» 절: «G1′ 델타: 루트 conftest.py seed 픽스처(update) · K1 `InvalidEmailNoticeTemplate(Exception→ValueError)` · K2 모델 `EmailNoticeKind` import 보완» → update 1 + add 칸 정정 2. 파서 실측: lane3 `update 5 / symbols 동반 0`.
- REPORT L27 `registry_gate --anchor dc7fd9f` 귀속 0.

### 2.4 42→0 교란(ⓐ4)
- `reading_parsed.json` runs: base 열이 d8928940→1a48d3bc→1e80644b→82f842c0→ce355310→29929353→d16ffb10→71cee9f8→f52dbc82→8e5f5e9d→434dbdda→3318d90f→d24bff8e→d64890fc→61b56ef4→c75bab65→78c9bb65→a88d829a→80431d94(15+ 이동). R-3432(`dddjango.md:98`) «`--base <G1 승인 시점 기준선 SHA>` 명시» 판형과 불일치.
- 형식 red 6회(run 18·21·30·34·39·40) 전건 «add 충돌(실존)» → 리포트 L2256 절 «HEAD에 이미 착지한 T20 물리 파일은 machine materialization `update`로 교정했다» — add→update 개서의 직접 증거.
- 파서 실측: e6fb491 add 42 중 최종 update+symbols 9행의 8행 포함(§1 표).

### 2.5 P1 실험(ⓑ)
| 실행 | 실체화 | 귀속 | 항목 | 비고 |
|---|---|---|---|---|
| 원판 A(v2.17.16) e6fb491/d892894 | 42 | 2 | #107·#188 | 기준 |
| **P1-dedupe** e6fb491/d892894 | 43(+api_router 병합) | **1** | #188 | #107 소멸 · composition-root 0/0 · #111 미발화 |
| P1-naive e6fb491/d892894 | 43 | 1 | #188 | 빈 파일이라 dedupe 와 동일 |
| 원판 B final/80431d9 | 0 | skip | — | 기준 |
| **P1-dedupe** final/80431d9 | 0 | **skip** | — | 9행 전부 «선언 전부 기실존 — 병합 생략» |
| P1-naive final/80431d9 | 9 | **4** | #107(함수 2)·#157·#219·#635 | **중복 정의 오탐 4건 신규** — dedupe 필수의 결정적 반례 |

능동 탐색한 반례와 처리:
- `from __future__ import annotations` 재방출 → 파일 중간 위치는 SyntaxError → compile fail-closed(형식 red) — 병합 렌더에서 제외해야 함(러너가 제외).
- 기존 파일 파싱 불능(WIP 문법 오류) → FormError 로 올리면 명세 탓이 아닌 형식 red → «미시뮬레이션(파싱 불능)» 메모가 정답(러너 방식).
- `__init__.py` update 대상에 symbols → 렌더러가 클래스/def 를 패키지 init 에 방출 → R-2499 «빈 `__init__.py`» 계열 위반 제조 가능 → 병합 거부(메모) 필요. 4레인 실측 0행이라 관측 오탐 0.
- 마운트된 BC 에서 registrar 부재 + 스텁 본문 → #111 이동 가능성 — 마운트됐다면 registrar 가 실존해 dedupe 생략 → 사실상 배제.
- 어노테이션 `api: NinjaExtraAPI` 가 import 결합 없이 붙으면 code 레인 `_is_root_api_annotation` 오탐 가능 → update 소비자의 boundary-imports 행도 함께 병합(dedupe by 문) 필요.
- «등록 함수 개명(구 이름 잔존)» 계획 → append 로 함수 2 → #107 red — 명세가 파일 내 제거를 표현할 수 없는 구조적 사각(4레인 0건) → 사각 목록에 «병합은 append 전용 — 기존 이름 제거·형상 변경은 표면 밖» 병기.
- 계약 실존 채널: `judge_update_target`(`:1339`) 은 symbols 선언 → S′ 를 먼저 보므로 집계 불변(fixture `imports-green` 기대 (5,5,2,1,1,1,0,0) 유지). 단 그 fixture 의 update 대상 `frozen_clock.py` 에 `TickingClock` 이 부재라 P1 이면 실체화 +1 → stub 절 EXPECTED 재실측 필요(`pregate_fixture_run.py:641-650`).

### 2.6 효과(ⓒ)
- 파서 실측(`design_pregate.parse_spec`): reading e6fb491 add 42(symbols 8)/update 30(symbols **1**) · final update 73(symbols 9) · lane1 add 69(53)/update 2(**0**) · lane2 add 34(21)/update 7(**0**) · lane3 add 20(11)/update 5(**0**).
- STOP-149(`docs/superpowers/orders/lane/STOP-fortune-reading-p4-registry-attribution-149.md` §3): update 행 파일 귀속 = prepare_fortune_evidence_use_case.py #635 · citation_validation_service.py #474/#153. e6fb491 에서 두 파일 모두 `declared=[]`·imports 0 → 채널 부재라 어떤 update 시뮬레이션도 예측 불가(원인은 R-3426/R-3427 전수 의무 미이행 — R-5d 아님). #472/#162 는 add 행(contract) 이었으나 imports 미선언 — 역시 채널 은폐.

## 3. 처방 P1~P4 판정과 권고

| 처방 | 무손실 | 일반화 | 비용 | 판정 |
|---|---|---|---|---|
| **P1 병합 append(조건부)** | 검증됨 — 검출 집합 단조(append 는 AST 노드 추가만·L 과 동일한 기존 파일 진단 불변) · 게이트 강도·exit·STOP 불변(관찰 모드·G2 무접촉·검사기 27종 무접촉 D1 유지) · 오차단 0(final skip 불변) | 기계 블록+AST 만 의존·양 런타임 동일 실행기(codex byte 미러) · 표준 트리 0B 고정 파일 «채우기» 판형은 플러그인 정의라 프로젝트 비의존 · kkebi 대조는 구조적 불가(⓪ 병기) | 실행기 소규모(`_parse_symbols` 분기·`materialize` update 분기·병합 렌더 30~50행) + 픽스처 good/bad 짝 + 문면 정렬 | **권고** — 단 «대형·규범 동반»이 아니라 **소규모 렌더 확장 묶음**으로 재분류 |
| P2 규칙별 면제 | 실질 억제(선언 신뢰) — 개명 진탐 은폐 | 규칙별 하드코딩 → 비일반·코퍼스 이중화 | 낮음 | 기각(MAJOR) |
| P3 이월 규범 | 무손실 | 양 런타임 동일 | 매우 낮음 | R-5d 와 별개 — N-1 의 R-3433 rev4 에 «이월(최초 근거 절 ID 참조·문맥 변동 시 재판정)» 1문장으로 동반 가능(선택) |
| P4 architect 신규 모듈 add | 품질 훼손(고정 칸 위반) | — | — | 기각(BLOCKER) |

**P1 필수 조건(5)**: ① 기존 최상위 바인딩 이름(`_top_level_names`)과 겹치는 선언은 병합 생략 + 메모 ② `from __future__` 재방출 금지·헤더 docstring 제외 ③ 대상이 `.py` 실물이고 파싱 가능할 때만(부재 = ⑴ 유지 · 파싱 불능 = 미시뮬레이션 메모 · `__init__.py` = 병합 거부) ④ update 소비자의 boundary-imports 행도 dedupe 병합 ⑤ 사각 목록에 «append 전용 — 기존 이름 제거·형상 변경 표면 밖» 상시 병기.

**코퍼스 정합(P1 시 건드릴 것)**: 실행기 `design_pregate.py` docstring `:17-20·:41-43`·`_parse_symbols :466-470`·`materialize :1023`·리포트 사각 문면(«미시뮬레이션: update 계획…»·«update 대상의 미선언·미실존 이름») · 설계 D2 `pregate-design.md:61·:84` · **R-3427 rev2**(`agent-design-architect.ttl:1723` — «스텁 전사는 add 소비자만» 문면) · **R-3426 rev2**(`:1703` — «자리표시자 실현 파일의 공개 심볼 전부» 범위에 «update 칸에서 새로 내는 최상위 이름» 명시 — 현재는 R-3427 문면에만 있음) · R-3432/R-3433/R-3434 **불변** · rulepack: 검사기 무변경이라 ttl 개정분만 `make rulepack`·LEDGER · 픽스처 신규 good/bad(0B update+symbols → red→green · 기실존 이름 → 생략) + `imports-green` EXPECTED 재실측 · `pregate_fixture_run.py` · codex byte 미러 · `make verify`. 검사기 27종·`pregate_symbol_kinds.json` 무접촉.

**권고 처방 1개**: **P1(dedupe 병합 append, 조건 5)** — 근거는 «③형 예방·커버 확대»가 아니라 **오탐 계열 소거**(배치 1 스텁 충실도와 같은 급): 표준 트리 0B 고정 파일을 채우는 `update` 판형에서 #107·#593 류 «존재-하나» 규칙이 구조적으로 오탐을 내고, 그 오탐이 개정마다 재처분을 강요한다. 관측 사건 1레인(reading 1 ID)이므로 배치 필터(≥2레인 관측)를 엄격히 적용하면 R-5a/b 와 같은 «보류» 등급이며, 등재하려면 ①브리프에 «2레인 중 1레인은 구조 추론» 병기가 필요하다.

## 4. 요약(10줄)

1. ⓐ(1)(2) 검증됨: `design_pregate.py:466-470`(비-add symbols 폐기)·`:1023`(update 미시뮬레이션) 확정 · reading #107 은 0B 자리표시자 `api_router.py`(d892894) + update+symbols 선언의 산물 — 수리판 재실행·P1 실험(스텁 병합 시 #107 소멸·#188 보존)으로 3중 재현.
2. 계수 정정(MINOR): «20회 재처분»은 예보 등장 20회 · 실기재 처분 14회(표 7+메모 7).
3. ⓐ(3) MAJOR: 레인 3 G1′ 실측은 «예보 0»이 아니라 형식 red ×2이며 델타는 update 1+add 정정 2 · update 5행 symbols 0 → 관측 사건 없음. ⓪ «2레인» 중 1레인은 구조 추론 — 관측 기준 1레인.
4. ⓐ(4) MAJOR: add 42→0 수렴은 v2.17.14 기실현 add 형식 red 회피 개서 + `--base` 15회 이동(R-3432 위반 판형)의 산물 — 최종 update+symbols 9행 중 8행이 원래 add. v2.17.16+고정 기준선이면 재현 안 됨.
5. ⓒ MAJOR(과대): update+symbols 실효 행 = reading 1 · 레인 1~3 0·0·0 → 4레인 이득 = 오탐 ID 1개·재처분 14행(≤15분/26h) · ③형 예방 근거 0(STOP-149 의 update 행 귀속은 채널 미선언·C급이라 예측 불가).
6. ⓑ P1 naive = BLOCKER: final 명세에서 중복 정의 오탐 4건 신규(#107 함수 2·#157·#219·#635 — `p1-naive-final.stdout:56-59`).
7. ⓑ P1 dedupe = 검증됨: e6fb491 2→1(진탐 #188 보존·#111 미이동) · final skip 불변 · 검출 단조·게이트 강도·STOP 불변·오차단 0. 필수 조건 5(중복 생략·`__future__` 제외·`.py`·파싱 가능·`__init__` 거부·imports 동반 병합·사각 병기).
8. P2 기각(MAJOR — 규칙별 억제·비일반·개명 진탐 은폐) · P4 기각(BLOCKER — registrar 칸 고정 `check-composition-root.py:1386` · 설계 왜곡) · P3 MINOR(무손실이나 효과 ≈0 — N-1 의 R-3433 rev4 에 1문장 동반 선택지).
9. 권고: **P1 dedupe 병합**을 «대형·규범 동반»이 아닌 **소규모 렌더 확장 묶음**(오탐 계열 소거)으로 재분류해 진행 — 코퍼스 접점은 R-3426/R-3427 rev 문면·설계 D2·픽스처 good/bad+`imports-green` EXPECTED·codex 미러뿐(R-3432~3434·검사기 27종 불변).
10. 필터 유의: 관측 사건 1레인이므로 ≥2레인 관측 기준을 엄격 적용하면 R-5a/b 와 같은 보류 등급 — ①브리프에 «레인 3 은 구조 추론·kkebi 구조적 불충족» 병기 필수.
