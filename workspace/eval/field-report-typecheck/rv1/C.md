# 적대 리뷰 C — 증거·효과·표본 외 (현장 보고 typecheck 수리 · 1단계 문제 검증) · 2026-09-03

리뷰어 C. 저장소 무수정(읽기·검사 명령 실행만). 산출 파일은 이 디렉터리(`rv2/`)에만 씀.

## 0. 측정 환경 (재현 시점 구분)

| 항목 | 값 |
|---|---|
| spring_dream_server HEAD | `fbe77ee` (09-03 16:35 `chore(ruff)`) — **09-03 커밋 33개**(리딩 docs 대부분 + `chore(ruff)` 4 + `chore(pre-commit)` 1). 작업 트리 **더러움**: 562 files(+2609/−4519) = `ruff format` 적용분 미커밋. A/C 실파일은 작업 트리에서 무변경 |
| 측정 방식 | mypy: 작업 트리와 `git archive HEAD` 깨끗한 export 양쪽. ruff: export(`b349dc3`·`90b37eb`·`fbe77ee`) + 작업 트리 |
| 도구 | spring_dream `.venv` mypy 2.3.1 · ruff 0.16.4 · pre-push 훅 `uv run mypy spring_dream_server framework`(= 보고서 명령) |
| kkebi-server HEAD | `6608fb0` (08-26) · `.venv` mypy 2.3.1 · ruff 0.16.3 · pre-push 훅 mypy 설치 · `.dddjango/` run 20개(08-23~08-26) |
| 캐시 | 모든 mypy 실행 `--cache-dir`는 scratchpad(단 최초 1회 작업 트리 실행은 기본 `.mypy_cache` — gitignore 대상, `git status` 무변화 확인) |

## 1. 대조표 — 보고서 수치 4 + 조사자 재현 수치

| # | 주장 | 출처 | 재산출 | 판정 | 근거 명령 |
|---|---|---|---|---|---|
| 1 | mypy 전체 171건·36파일 | 보고서 | **171 / 36 files / checked 69** — 작업 트리·HEAD export 동일(file:code multiset diff 0) | 일치 | `.venv/bin/mypy spring_dream_server framework` (`rv2/mypy_worktree.txt`·`mypy_head.txt`) |
| 2 | redundant-expr 16 | 보고서 | **16** | 일치 — **분해는 정정**: 보고서 «VO 13 + 레인 밖 3» → 실측 **VO 11**(generation_settings 4·caller_label 1·translation_generation_settings 3·question 1·query_language 1·glossary_reference 1) **+ service_runtime.py :981 :982 = 2**(리딩 dddjango 레인 `ca5e41a`) **+ rag_builder/steps 3**(비-dddjango) | `grep redundant-expr` + `git blame HEAD` |
| 3 | Enum members 6 | 보고서 | **6**(book_usage_policy :7-9 · abstention_reason :7-9, 둘 다 `8216c78`) | 일치 | `grep 'Enum members'` |
| 4 | ruff format 189 (9/3 정리 전) | 보고서 | **189** @`b349dc3`(리딩 머지 11:31) 및 @`90b37eb`; **187** @HEAD(`660ca12` docs/** 제외 −2); **0** @작업 트리(format 적용 미커밋 — `1855 files already formatted`) | 일치(시점 명시 필요) | export 후 `ruff format --check .` |
| 5 | A 실파일 5건(generation_settings 4·caller_label 1) | 조사자 ⓪ | 5 | 일치 | #2 |
| 6 | C 실파일 book_usage_policy 3 | 조사자 ⓪ | 3 (+abstention_reason 3 = 6) | 일치 | #3 |
| 7 | «예제 자체 → unreachable 1·redundant-expr 1» | 조사자 ⓪ | **정정**: 플러그인 원문(final.md 486~548 verbatim 추출 `rv2/money/money_example.py`) → **unreachable 1**(Money :17)뿐. `repro.py:20`의 redundant-expr는 조사자가 넣은 `CallerLabel.create`(레인 형상) — 예제 밖. 대신 같은 graph-owned 블록 **PhoneNumber `__post_init__(self)` 반환 주석 누락 → `no-untyped-def` 1**(plain `--strict`에서도 발화) — 조사자 미기재 | 부분 정정 | `mypy --strict --warn-unreachable --enable-error-code redundant-expr money_example.py` |
| 8 | «plain `--strict`만으로는 A 두 오류 미발화» | 조사자 ⓪ | 확인 — 6형상(`rv2/shapes/shapes.py`) plain strict 0건. **추가 실측**: 플래그 풀세트에서도 **raise-only 본문(`if not isinstance(x, T): raise`)은 침묵**(mypy는 raise 단독 블록을 reachability no-op으로 취급) — 발화 형상은 **or-체인(redundant-expr)** 과 **비-raise 본문(unreachable)** 뿐 | 일치+보강 | 위 |
| 9 | C는 플래그 의존? | (미기재) | **플래그 무관** — 플래그 0개 `mypy repro.py`에서도 2건 발화 | 보강 | `mypy repro.py` |
| 10 | 검사기 #493 주석 유/무 Enum 모두 clean | 조사자 ⓪ | `clean — 파일 6개` | 일치 | `check-public-surface-annotation.py .` @`b3/mypy/fx` |
| 11 | 리딩 BC 37건 · 메타클래스 22 · redundant-cast 2 · wiring:42 · Literal:165 | 보고서 B | 37 ✓ · schema_out 14 + controller 8 = 22 ✓(보고서 15+7) · 리딩 redundant-cast 2 ✓(+service_runtime 3) · ✓ · ✓ | 일치 | by-file 집계 |
| 12 | D possibly-undefined 13 | 보고서 D | 13, 전부 `service_runtime.py`(`43e9628`) | 일치 | `grep possibly-undefined` |
| 13 | «08-26부터 켜져 있었는데 G2 통과» | 보고서 B | `4eaf960`(08-26 23:24)이 redundant-expr·warn_unreachable **최초 도입**; `9760c71`·`8d3aac0`·`ad56395`·`8216c78`·`43e9628` 전부 4eaf960의 후손, 각 커밋의 `pyproject.toml`에 두 플래그 실재 | 일치 | `git show <sha>:pyproject.toml`·`merge-base --is-ancestor` |
| 14 | «전체 검사» 범위 | 보고서 | **훅 대상은 `spring_dream_server framework` = 69 파일 + import 폐쇄이지 `application/` 전수가 아님**. `mypy application` → 124건/2727 files, **171에 없는 오류 31**(fortune_character admin 26 · 리딩 OHS 3 · notification admin 2) — redundant-expr 신규 3(citation_validation_service :62 :63 «If condition is always true» — A 동형 비-VO, 리딩 P4 `585c9c6`; notification panel :79 — `obj is None or obj.pk is None`, A 비동형) | 신규 관찰 | `mypy application` (`rv2/mypy_application.txt`) |

## 2. 귀속표 — A 16 + C 6 (+ 동형 관찰)

| 파일:행 | 건 | 커밋(생성) | 날짜 | dddjango run | 런타임(master 발주표) | 커밋 접두 |
|---|---|---|---|---|---|---|
| llm_access/.../generation_settings.py :43 :45 :49 :51 | 4 | `9760c71`(S1) → `8d3aac0`(S2 수정) | 08-29 | `20260829-1601-llm-gateway-caller-settings` | **claude** Opus 4.8 · herdr 워크트리 | `feat(llm_access)` |
| llm_access/.../caller_label.py :27 | 1 | `9760c71` | 08-29 | 같음 | claude | `feat(llm_access)` |
| query_translation/.../translation_generation_settings.py :32 :34 :42 · question :16 · query_language :20 · glossary_reference :33 | 6 | `ad56395`(S2) | 08-31 | `20260831-1130-query-translation` | **codex** · dddjango 2.17.10 | `feat:` |
| framework/.../service_runtime.py :981 :982 | 2 | `ca5e41a`(L2 소비부 분리) | 09-03 | `20260831-2331-fortune-reading` | **codex** gpt-5.6 xhigh · 2.17.14 | `refactor(rag)` |
| framework/.../rag_builder/steps/__init__.py :622 / :1767 / :4277 | 3 | `3d1fb20` / `dad6f2e` / `f4b09f5` | 08-30 / 09-01 / 08-30 | **없음** — 발주 03 공통 RAG 빌더(codex 가이드 작업)·31행 출처 주소 변환표(codex 비-dddjango) | — | 무접두 / `fix(rag)` |
| C: fortune_reading/.../book_usage_policy.py :7-9 · abstention_reason.py :7-9 | 6 | `8216c78`(P1 wip) | 09-01 | `20260831-2331-fortune-reading` | **codex** | `wip(fortune-reading)` |

- 접두 `dddjango(`는 spring_dream 전 776커밋 중 **13개(notification 2레인)** 뿐 — 귀속은 접두가 아니라 `.dddjango/<run>` + master 발주표 런타임 열로 했다.
- **«3레인» 재산출**: A 발화 dddjango 레인 = **3**(llm_access·query_translation·fortune_reading[비-VO 2]) — 보고서가 «VO 6종 13건»으로 묶은 것은 **2 레인 11건**이고, 나머지 2건은 리딩 레인의 비-VO(`any(not isinstance(term, str) ...)` over `tuple[str, ...]`). C = **1 레인**. A∪C 발화 = 3 / 23 runs. 런타임: claude 1 · codex 2 → **런타임 특이 아님**.
- **숨은 A(억제·우회) — 문면 유도 관용구의 실제 노출 레인**: fortune_character(claude, 08-30) `# type: ignore[redundant-expr]` **3 VO 파일**(language_code :22 주석 «mypy strict는 value:str 선언 탓에 … 가드는 유지한다») — 레인이 mypy로 **보고** 억제; wallet(codex) **4 VO 파일** + chat_relay 1 파일 `raw_value: object = self.value` 확장 우회. spring_dream VO 286 파일 중 or-체인 isinstance 16 파일(5 BC) — 발화 6 + 억제 3 + 우회 5 + 정상 좁히기 2. → 관용구 노출 레인 **6/23**(flagged 3 · suppressed 1 · widened 2).

## 3. 레인별 mypy/ruff 실행 기록표 (dddjango run 23 · REPORT-*.md + `.dddjango/<run>/lane-report.md` 전수)

| run | 런타임 | mypy 기록(범위) | ruff 기록 | A/C 발화 |
|---|---|---|---|---|
| 0827 openai-rag-generation | claude? | REPORT·lane-report 없음(설계 문서만 mypy 언급) | — | 0 |
| 0827 ai-chat-sse-core | claude? | 없음 | — | 0 |
| **0829 llm-gateway-caller-settings** | claude | **없음**(lane-report: `ruff check application/llm_access/` All checks passed·I001 8건 정리만) | check만 | **A 5** |
| 0830 fortune-character | claude | `spring_dream_server framework` Success(훅 범위 전체) | — | 0 (**ignore[redundant-expr] 3으로 억제**) |
| 0830 accounts | claude | `mypy application/accounts` Success 240 files | check + **format --check 통과** | 0 |
| 0830 service-policy | claude | `application/service_policy` Success(strict) | — | 0 |
| 0830 fortune-character-1 | codex | **없음** | Ruff 통과(범위 미기재) | 0 |
| 0830 fortune-record | codex | mypy success 147 files(BC 범위 추정) | Ruff 통과 | 0 |
| 0830 product | codex | `uv run mypy application/product` 116 files 0 | ruff | 0 |
| 0830 chat-relay-1 | claude | mypy 329 files clean | — | 0 |
| 0830 wallet | codex | `uv run mypy application/wallet` 178 files 통과 | ruff 통과 | 0 (**widen 우회 4**) |
| 0831 fortune-intent | codex | `fortune_intent` 진단 0; **«import graph의 기존 llm_access 5건은 허용 경로 밖 기준선»** | — | 0 (A 5를 관측·방치) |
| **0831 query-translation** | codex 2.17.10 | **없음**(REPORT·lane-report mypy 0) | «Ruff check / format check 통과 · 64 files clean» | **A 6** |
| 0831 fortune-calculation | claude | mypy strict BC 160 + 스크립트 2 → 0 | check clean | 0 |
| 0831 promotion-pricing | codex | `uv run mypy application/promotion` 198 files 0 | `ruff check application/promotion` 0 | 0 |
| **0831 fortune-reading** | codex 2.17.14 | **없음**(REPORT mypy 0) | Ruff **scoped check**(D54 epoch 이후 변경 경로) All checks passed — format 무언급 | **C 6 · A 2(비-VO) · D 13 · 메타클래스 22 등 76** |
| 0901 fortune-character-2 | claude | `mypy spring_dream_server framework` 변경 파일 0 / 잔존 80 = framework/rag 기준선 | 변경 5파일 check/format | 0 |
| 0901 fortune-calculation-enhancements(=−1) | codex | `uv run mypy --strict application/fortune_calculation` 181 files 0 | check clean · **`ruff format` exit 1 인지·방치**(«baseline formatting debt») | 0 |
| 0901 chat-relay-turn-refactor | claude | 승격 폴더 Success · framework/rag 80 pre-existing | 변경 파일 check | 0 |
| 0901 promotion-openapi-headers(=−2) | codex | full mypy: framework/rag + jsonschema stubs만 | 변경 파일 check/format exit 0 | 0 |
| 0902 media-library | claude | **없음** | 없음 | 0 |
| 0902 notification-bc | claude | «mypy strict clean»(범위 미기재) | — | 0 |
| 0902 notification-email-template | claude | **없음** | 없음 | 0 (훅 범위 밖 panel:79 redundant-expr 1, A 비동형) |

**판정**: «보고 항목이라 실행이 갈렸다» **성립**. mypy 기록 없는 run **7/23**(llm_access·fortune-character-1·query-translation·fortune-reading·media-library·notification-email-template + 0827 2건 불명). A/C 발화 3 레인은 **전부 기록 없음 쪽**; 기록 있는 16 run은 발화 0(fortune_character는 억제로 0). 실행 범위·플래그: BC 폴더 스코프가 다수(`mypy application/<bc>`), 훅 전체 범위 3(fortune-character·fortune-character-2·promotion-2), 프로젝트 설정 그대로(`--strict` 중복 1). BC 스코프 실행도 pyproject의 redundant-expr를 상속하므로 **실행만 했으면 A는 레인 안에서 잡혔다**(fortune-intent가 다음 날 llm_access 5건을 실제로 봤다). ruff format: `--check` 실행 기록 3 run(accounts·promotion-2·query-translation 64 files)·인지 후 방치 1(fortune-calculation-1); 189 파일 분포 = fortune_reading 46 · framework 25 · fortune_calculation 23 · chat_relay 22 · fortune_character 14 · notification 8 · media_library 8 · product 4 · tests/ 30여 · 기타 (application 129 = test 62 + 비-test 67).

## 4. 표본 외 kkebi-server (읽기 전용)

| 항목 | 실측 |
|---|---|
| (a) mypy 설정 | `strict=true`·`warn_unreachable=true`·`enable_error_code`에 `redundant-expr` 포함 — spring_dream과 **동일 템플릿**(kkebi `2147d55` 08-20 도입 → kkebi 전 레인 08-23~26 이전). pre-push 훅 `uv run mypy kkebi_server application framework scripts/import_legacy_saju` 설치 |
| (d) 전체 mypy | **`Success: no issues found in 3553 source files`** — redundant-expr 0 · unreachable 0 · Enum members 0 |
| (b) 값 객체 관용구 | VO 300 파일 · isinstance 39 파일 · **or-체인 8 파일** · **확장 우회 `x: object = self.x` 11 파일/24행**(전부 08-25 `3fab0dc`·`8399451`·`3e97c3d` = saju-chart-engine·saju-remainder 레인) · raise-only 직접 재검사(`if not isinstance(self.weight, int): raise`) 10 파일/14행(mypy 침묵 형상) · `ignore[redundant-expr]` 1(비-VO) |
| (c) Enum 멤버 주석 | Enum 106 파일 · **주석 부착 0** (spring_dream: 85 파일 중 2, 둘 다 리딩 `8216c78`) |
| kkebi 정리 커밋 | mypy 관련 1건(`483c613` web-tarot, 무관) — A/C형 정리 이력 0 |

**판정**: 
- **A**: 문면이 유도하는 «선언 타입 재검사» 관용구는 **양 프로젝트·양 런타임에 일반**(kkebi 21/300 VO · spring_dream 16 or-체인 + 5 확장 + 3 억제). mypy **발화**는 (i) 사용자 표준 플래그(redundant-expr ∨ warn_unreachable — **두 프로젝트 공통**, plain strict 아님) ∧ (ii) 형상(or-체인 또는 비-raise 본문)에 의존. 따라서 «spring_dream 플래그 특이» **아님**(kkebi 동일 플래그), «플러그인 일반 결함»은 **조건부 참** — 플래그 없는 프로젝트에선 죽은 조건일 뿐 오류 아님. kkebi 레인이 발화 0인 이유는 우회 형상(확장 24행·raise-only)이지 관용구 부재가 아님 → 수리 효과는 «오류 제거»보다 **«우회 보일러플레이트·억제 주석 제거»** 쪽이 더 일반적.
- **C**: 플래그 무관·mypy 일반. 그러나 발화 **1/43 run**(codex 리딩 P1 wip), 같은 레인의 다른 Enum 5 파일은 미부착 — 문면 해석 편차의 단발 사례.

## 5. 효과 — 171 분류·절감 상한/하한·과대 추정

**171 귀속(HEAD blame, 커밋 25)**

| 구분 | 건 | 내역 |
|---|---|---|
| dddjango 레인 | **87** | fortune_reading 76(`585c9c6` 27·`43e9628` 18·`ca5e41a` 16·`8216c78` 14·`ca1ab0a` 1) · query_translation 6 · llm_access 5 |
| 비-dddjango(가이드 작업 레인) | **84** | 발주 03 공통 RAG 빌더(codex) 52 · 25행 초벌 공정(claude Fable) 20 · 용어사전 2 · C11 2 · 출처 변환표 3 · `f820145` 4 · `7486414` 1 |

**플러그인 문면 귀속 가능 = A 13 + C 6 = 19 / 171 (11%)** — dddjango 레인분 87 중 22%. 나머지 dddjango 레인 68건: ninja `Schema`+`RootModel` 메타클래스 여파 22(플러그인 스킬에 `RootModel` 언급 0 — 코더 선택) · D possibly-undefined 13(`NoReturn` 미사용) · arg-type 7 · return-value 6 · redundant-cast 5 · 기타 — **문면 예제 귀속 불가**. 비-dddjango 84 + 훅 범위 밖 31(§1 #14)은 전부 발주측(B 영역).

**절감 추정**

| | 상한 | 하한 |
|---|---|---|
| 1회성 정리 노동(이번) | A 13 + C 6 = 19 one-liner ≈ 20~40분 + llm_access 테스트 5개 `# type: ignore[arg-type]` 삭제·재작성(query_translation은 죽은 분기 테스트 0 = 미검증 사문) | 문면 수리는 **이미 발생한 노동을 줄이지 못함**(0) |
| 레인당 향후 | spring_dream 비율 A 13/23 ≈ 0.57건/run · C 6/23 ≈ 0.26 → 합 ≈ **0.8건/run ≈ 1~3분/run**; 더해 우회 보일러플레이트(kkebi 2레인 24행·spring_dream 5파일)·억제 주석 3 감소 | 43 run 기준 A 13/43 ≈ 0.30 · C 6/43 ≈ 0.14; **mypy 미실행 레인은 문면을 고쳐도 다른 오류(메타클래스·NoReturn)가 그대로 새므로 «정리 커밋» 자체는 소멸하지 않음** → 정리 커밋 노동 절감 하한 ≈ 0 |

**과대 추정 판정**: 보고서의 프레이밍 «171건 노출 → dddjango 결함 3건»은 수치 자체는 정확하나, (1) A «VO 6종 13건»은 **11건 2레인**(+2 비-VO)으로 정정, (2) 171의 **89%**가 문면과 무관(비-dddjango 49% + 코더 선택 40%), (3) «리딩 37건»의 문면 귀속은 C 6뿐, (4) 189 파일은 62가 테스트·25가 framework — «전 BC ruff format 미적용»은 맞지만 A·C 수리와 무관. **B(기각·발주측)가 효과의 대부분을 가진 항목**이고 A·C는 «작지만 결정적으로 재현되는» 문면 결함이다. 효과 과대 추정: **MINOR**(수치 정확·귀속 프레이밍 과장).

## 6. 심각도 총괄

| 항목 | 판정 | 사유 |
|---|---|---|
| A 문제 성립(재현성) | **검증됨** | 결정적 재현(예제 원문 unreachable 1 · 실파일 11+2) · 발화 3 레인 + 억제/우회 3 레인 · kkebi 관용구 21 파일(우회로 발화 0) · 양 런타임 |
| A 효과·표본 외 일반화 | **MINOR** | 플래그(사용자 표준, plain strict 아님) ∧ 형상 의존 — 문면에 «플래그 무관 원칙»으로 쓸지는 ③ 문면 게이트 사안. 절감 ≈ 1~3분/run + 보일러플레이트 |
| A 보고서 수치 | **MINOR 정정** | 13/3 → 11+2/3 · «예제 자체 2건» → 1건(+별건 `no-untyped-def`) |
| **A 수리 범위 신규 관찰** | **MAJOR(수리 범위 결정용)** | 같은 graph-owned 블록 `PhoneNumber.__post_init__(self)` 반환 주석 누락 = 하우스룰 §4를 플러그인 자기 예제가 위반(plain strict 발화) — A 문면 교체 시 동반 수정 안 하면 «예제 mypy 스모크»(제안 4) 채택 여부와 무관하게 red 잔존 |
| C 문제 성립 | **검증됨** | 플래그 0에서도 발화 · 검사기 clean(문면↔mypy 충돌만) |
| C 효과 | **MINOR** | 1/43 run · 같은 레인 내 5:2 미부착 — 단발 해석 편차. 문면 1줄로 닫히는 범위 |
| «실행이 갈렸다»(B 사실) | **검증됨** | 무기록 7/23 · 발화 3 레인 전부 무기록 · 기록 16 레인 발화 0 · fortune-intent가 llm_access 5건 관측 기록 |
| 보고서 재현 수치 4 | **검증됨** | 171·16·6 일치 · 189는 `b349dc3`~`90b37eb` 시점 일치(HEAD 187·작업 트리 0) |

## 10줄 요약

1. 보고서 수치 4개 전부 독립 재산출 일치: mypy 171/36파일(작업 트리=HEAD export)·redundant-expr 16·Enum 6·ruff format 189(@`b349dc3`~`90b37eb`; HEAD 187 — `660ca12` docs/** 제외 −2; 작업 트리 0 = format 적용 미커밋).
2. A 분해 정정: «VO 13 + 레인 밖 3» → VO 11(2레인) + service_runtime 2(리딩 dddjango 레인 `ca5e41a`, 비-VO) + rag_builder/steps 3(비-dddjango). 귀속: llm_access(claude, `9760c71`) 5 · query_translation(codex, `ad56395`) 6 · fortune_reading(codex) 2 — 런타임 특이 아님.
3. 조사자 «예제 자체 2건» 정정: 플러그인 Money 원문은 unreachable 1뿐(redundant-expr 1은 조사자가 넣은 레인 형상); 대신 같은 graph-owned 블록 `PhoneNumber.__post_init__(self)`가 `no-untyped-def`(plain strict 발화) — 하우스룰 §4 자기 위반, 수리 범위 동반 권고(MAJOR).
4. 발화 형상 실측: 플래그 풀세트에서도 raise-only `if not isinstance(x,T): raise`는 침묵(mypy reachability no-op); 발화는 or-체인(redundant-expr)·비-raise 본문(unreachable)뿐. plain `--strict`는 A 0건, C는 플래그 0에서도 발화.
5. 실행 기록표(23 run): mypy 무기록 7 — A/C 발화 3레인(llm_access·query_translation·fortune_reading) 전부 무기록 쪽, 기록 16 run 발화 0, fortune-intent(08-31)가 llm_access 5건을 «허용 경로 밖 기준선»으로 관측 → «실행이 갈렸다» 성립. BC 스코프 실행도 pyproject 플래그를 상속하므로 실행만 했으면 레인 안에서 잡혔다.
6. 숨은 A: fortune_character(claude) `# type: ignore[redundant-expr]` 3 VO(레인이 보고 억제) · wallet 4+chat_relay 1 `x: object = self.x` 우회 → 관용구 노출 6/23 run.
7. 표본 외 kkebi: 설정 동일(strict+warn_unreachable+redundant-expr, 08-20부터)·훅 설치·전체 mypy 0건/3553 — 그러나 VO 300 중 확장 우회 11 파일/24행(08-25 2레인)+raise-only 재검사 10 파일 = 관용구 21 파일 존재·발화 0. Enum 106 파일 주석 0. → A는 «플러그인 일반 관용구 × 사용자 표준 플래그 × 형상» 조건부 결함(spring_dream 플래그 특이 아님·plain strict 무해), C는 1/43 run 단발.
8. 171 귀속: dddjango 레인 87(리딩 76·qt 6·llm 5) / 비-dddjango 84. 문면 귀속 가능 A 13 + C 6 = 19/171(11%); 나머지 89% = 비-dddjango 49% + 코더 선택(메타클래스 22·NoReturn 13·arg-type 등) 40%. 훅 범위 밖 `mypy application` 추가 31건(fortune_character admin 26 등) 별도.
9. 효과: 이번 정리 노동은 문면 수리로 안 줄어듦(하한 0); 향후 ≈0.8건/run(spring_dream) ~ 0.44/run(43 run) ≈ 1~3분/run + 우회 보일러플레이트·억제 주석 감소 — «정리 커밋» 자체는 B 미실행 레인에서 계속 발생. 효과 과대 추정 MINOR(수치 정확·귀속 프레이밍 과장).
10. 심각도: A 성립 검증됨/효과 MINOR/수리 범위 MAJOR(PhoneNumber 동반) · C 성립 검증됨/효과 MINOR · 보고서 수치 검증됨(분해 2건 정정) · B 사실(실행 갈림) 검증됨.
