# 적대 리뷰 C — 증거·효과·표본 외 (현장 보고 typecheck 수리 · 5단계 구현) · 2026-09-03

리뷰어 C. 대상 = 브랜치 `fix/field-typecheck` HEAD `27342a3`(b2e1f42 검사기 · 33b0bd7 규범 · 27342a3 문서). 저장소 무수정(읽기·검사기/mypy·read-only verify 4종 실행만). 라이브 저장소 2곳은 읽기·검사기 실행만 — 전 실행을 `DJR_FINDINGS_JSON=<scratch>`로 sink 우회해 사이드카 생성 0(spring `git status` 변화 0 · kkebi `.dddjango/violations` 486→486, 08-25 미추적 5건은 기존물). 스크래치 `scratchpad/b3/rv5/`(`orig/`=main 검사기+보조 4모듈 · `patched/`=HEAD 검사기 · `ex/` 예제 · `lane/` 레인 형상 · `cprobe/` 형상 트리 · `*_orig.txt`/`*_patched.txt` 전 트리 출력).
Serena: skipped — opt-in 표식 없음 · graphify 표식 없음 → 기본 도구.

## 0. 환경·스냅숏

| 항목 | 값 |
|---|---|
| dddjango | `27342a3` · main `7e93b08` 검사기 md5 `c082d5d8…` = 태그 `dddjango--v2.17.16` 동일 · HEAD 검사기 md5 `14465bbb…` = codex 미러 byte 동일 · 렌더 final.md = codex `dddjango-architecture-ddd/references/final.md` byte 동일 |
| spring_dream_server | HEAD `96e8719`(09-03 17:57:35 `fix(typing): mypy 빚 1단계 — 기계적 49건 상환(171→122)`) · WT clean(`.claude/`만 미추적) · pyproject `strict + warn_unreachable + redundant-expr·truthy-bool·…` |
| kkebi-server | HEAD `6608fb0`(08-26) · WT 변화 없음 |
| 도구 | mypy 2.3.1(spring `.venv`) · Python 3.14 |

## 1. 재현 표 (명령·수치)

### 1-A. A 예방 재현

| # | 대상 | 명령 | 결과 | 판정 |
|---|---|---|---|---|
| A-a1 | 렌더 md §3.1 새 예제(`ex/vo_example.py` — awk로 코드 펜스 추출 59행) | `mypy --strict --warn-unreachable --enable-error-code redundant-expr,truthy-bool,truthy-iterable,possibly-undefined,ignore-without-code,redundant-self,unused-awaitable` | **0건** | 검증됨 |
| A-a2 | 같은 파일 | `mypy --strict` | **0건** | 검증됨 |
| A-a3 | main 원본 예제(`git show main:` 추출 `ex/vo_example_main.py`) | full / plain | **2건**(:17 unreachable · :56 no-untyped-def) / **1건**(:56) | 원본 발화 재현 — rv1 정정(«예제 자체 1+1»)과 일치 |
| A-b1 | 보고서 레인 형상 원문 `generation_settings.py`@`59a9f10`(17:57 정리 전 · `lane/generation_settings_orig.py`) | spring 루트에서 `.venv/bin/mypy <파일>`(pyproject 상속) | **4건** :43 :45 :49 :51 `redundant-expr` | 보고서 4건 재현 |
| A-b2 | 새 규범대로 고친 사본 `lane/gs_norm.py`(isinstance 재검사 4곳 삭제 · `type(x) is bool` 2곳 · float 자리 int 수용 — `isinstance(` 0) | 동일 | **0건** | 검증됨 |
| A-b3 | 변종 `lane/gs_norm_isinstance.py`(`isinstance(x, bool)` 형) | 동일 | **0건** | `type(x) is bool` 강제는 mypy 사유가 아님(#69 ⓓ 소음 회피 사유만) |
| A-b4 | 값 검사 생존(런타임 · spring `.venv` python · `GenerationConfigurationInvalid` 실물 import) | 10케이스 | blank model **REJECT** · bool tokens **REJECT** · 0 tokens **REJECT** · **int timeout(float 자리) ACCEPT** · inf/neg timeout **REJECT** · bool retries **REJECT** · neg retries **REJECT** · bad effort **REJECT** · ok **ACCEPT** | 범위·공백·bool 가드 전부 생존 — 검증됨 |
| A-b5 | 라이브 HEAD 실파일(발주측 17:57 정리본) | 동일 mypy | 0건 — 단 발주측은 `type(timeout_seconds) is not float`(int 거부)를 **4파일**에 채택(`generation_settings.py:49`·`translation_generation_settings.py:40`·`intent_generation_settings.py:43`·`serialized_audit_payload.py:339`) | R-3442 «float 자리 int 거부 안 함»과 **반대 선택** — §4 MAJOR-1 근거 |

### 1-C′. C′ 예방 재현

| # | 대상 | orig(main) | patched(HEAD) | mypy `--strict` | 판정 |
|---|---|---|---|---|---|
| C-1 | 증거 폴더 2파일을 표준 트리(`cprobe/evtree/application/fortune_reading/domain_layer/shared_value_object/`)에 배치 | **#493 6건 · exit 2** | **clean · exit 0**(파일 6) | — | 증거 README(orig 6 → 0) 독립 재현 — 검증됨 |
| C-2 | 라이브 HEAD 실파일 2개(현재 plain `StrEnum` + 무주석) | 0 | 0 | 0 | 수리본 0건 — 검증됨(orig도 0: 별칭이 이미 사라져서) |
| C-3 | `alias_bare.py`(`StrEnum as _StrEnum` + 무주석) | #493 1 | **0** | 0 | 오탐 소거 |
| C-4 | `alias_annotated.py`(별칭 + `A: str = "a"` — 레인의 우회 형상) | 0 | **0** | **[misc] 2건** | 우회는 검사기가 안 잡고 mypy만 red — 그대로 |
| C-5 | `plain_annotated.py`(별칭 없이 주석 부착) | 0 | **0** | **[misc] 1건** | 동일 — «별칭 없이 주석 부착»도 #493 0 · mypy red |
| C-6 | 픽스처 `public_surface/good` | #493 **3**(book_usage_policy 2 · reading_cursor 1) | **0** | — | 수리 전 red 재현 — 검수표 일치 |
| C-7 | 픽스처 `public_surface/bad_rules` | #493 **7** | **8**(aliased_shadow +1) | — | 미탐 폐쇄 — 검수표 일치 |

문서가 «우회 불필요·R-3154 옳음»을 말하는가: 회신 C행(«규범 변경 0 · R-3154 v1.0.0부터 성문 · 레인이 주석 부착으로 우회 → mypy [misc]») + «별칭은 이제 원명으로 풀지만 09-01 결정 C를 바꿀 이유 없음» — **암시적으로만**. «멤버 주석 부착은 R-3154 위반이며 결정적 검사기는 이를 잡지 않는다(mypy·리뷰어만)»는 문장은 없다(§4 MINOR-3).

### 1-X. 표본 외·정합 실측

| # | 대상 | 명령 | orig | patched | 판정 |
|---|---|---|---|---|---|
| X-1 | spring 전 트리 @`96e8719` | `DJR_FINDINGS_JSON=… python3 <v>/check-public-surface-annotation.py .` | 3311행 · blocker **3225** · exit 2 | 3311행 · 3225 · exit 2 | `diff` **0행** — 검증됨(검수표 3309는 17:57 커밋 전 스냅숏 — 드리프트, 차분 0 불변) |
| X-2 | kkebi 전 트리 @`6608fb0` | 동일 | 347행 · blocker **173** · exit 2 | 347 · 173 · exit 2 | `diff` **0행** — 검증됨 |
| X-3 | read-only verify 4종 @HEAD | `ontology_ledger_check.py` · `ontology_render_sync.py` · `corpus_mirror_sync.py --check` · `manifest_seal.py --check --draft` | — | 위반 0 · 540절 red 0/warn 0 · 11/11 in-sync · green(256파일·draft) | 검증됨(`make verify` 전체는 소성물 재생성 위험으로 미실행 — 검수표 6/6 기록 신뢰) |
| X-4 | 계획 v2 «확정 대상 문면» ↔ 렌더 md 불릿 2 | md5 | 7d62c82b… / 3df3cb7c… | 동일 / 동일 | byte 일치 |
| X-5 | 그래프 산출 | ISSUED `R-3442`·`R-3443` 2행 · wiring `delegatedTo agent-discipline-reviewer` 2 · LEDGER s016-3.1 `ff912545…` · rulepack `s016-3.1 works [R-0494..R-3443]` · `R-3442.agents=[agent-discipline-reviewer]` | — | 실재 | 검증됨 |

## 2. 사실 대조표 (회신 수치)

| 회신 주장 | 실물 | 판정 |
|---|---|---|
| «23 run 중 mypy 무기록 7» | rv1/C.md §3 표 23행 — 무기록 행 **8**: 0827 openai-rag(REPORT·lane-report 없음) · 0827 ai-chat(없음) · 0829 llm-gateway · 0830 fortune-character-1 · 0831 query-translation · 0831 fortune-reading · 0902 media-library · 0902 notification-email-template. rv1 자체 문장도 «6 + 0827 2건 불명»=8인데 7로 적음 | **MINOR-1** — 7 → «확정 6 + 불명 2 = 8» |
| «A/C 발화 3레인 전부 무기록» | llm_access·query_translation·fortune_reading 3행 모두 «없음» | 검증됨 |
| «C 5표면 일치(R-3154 SKILL.md:72 v1.0.0부터·Coordinator·검사기 docstring·pregate b35·rulepack)» | SKILL.md:72 «enum 멤버(`RED = 1`)» ✓ · `e954659`(06-04) ∈ `dddjango--v1.0.0` ✓ · 검사기 docstring :12 ✓ · design_pregate :43 ✓ · rulepack R-3154 ✓ · **Coordinator :133은 «문법 없는 자리만 면제»**(enum 명시 없음) | 4 명시 + 1 느슨 — **MINOR-2** |
| «orig 6 → patched 0» | §1-C′ C-1 재현 | 검증됨 |
| «양 저장소 전/후 차분 0» | X-1·X-2 | 검증됨 |
| «잔재 2파일 09-03 17:57 커밋으로 해소» | `96e8719` 17:57:35 — `book_usage_policy.py`·`abstention_reason.py` 각 10행 변경(`_StrEnum`→`StrEnum` · 주석 제거) 포함 · A 6파일·테스트 2파일도 동승 | 검증됨 |
| «렌더본 mypy full 0·plain 0» | A-a1·A-a2 | 검증됨 |
| «R-12에 툴체인 1줄 반영 예정» | 로드맵 R-12 행에 «툴체인» 문구 실재 | 검증됨 |
| 로드맵 **R-14 행 본문** | «C: 하우스룰 §2 … Enum/StrEnum 멤버 예외 명시 … 검사기 #493은 무충돌 확인» · 증거 «C reading 3건+레인 간 해석 불일치» · 상태 «① 적대 리뷰 3기 진행 중» | 회신(C 문면 불성립·#493 alias 사각·상관 100%)과 **3곳 모순** — **MAJOR-4** |

## 3. 부작용 표 (표본 외·소급·집행선)

| 항목 | 실측 | 판정 |
|---|---|---|
| kkebi 검사기 차분 | 0행(173/173) | 부작용 0 |
| kkebi 기존 값 객체의 R-3442/3443 즉시 위반 형상(rough grep · VO 폴더 · 비테스트) | `isinstance(self.x, <선언타입>)`/`not isinstance(x, T)` **8파일/11행** · `type(x) is (not) T` **68행** — rv3 AST 계수(75파일/207행)의 하위 집합 | 소급 red는 «적용 대상 = 신규·수정 값 객체» 문면이 막는다 — **단 «손대는 값 객체»는 파일/클래스 단위**라 그 VO를 한 줄이라도 고치는 슬라이스는 나머지 재검사 줄 제거 의무 |
| spring 동형 | 10파일/14행 · `type() is` 27행(발주측 17:57 정리 후 잔존 — `type(timeout_seconds) is not float` 4파일 포함) | 다음 dddjango 슬라이스가 이 VO를 손대면 R-3442(float 자리 int 수용)와 **레인 테스트 기대(int 거부)** 충돌 |
| 하우스룰 선례와의 granularity | houserules SKILL.md:29 «기존 파일을 수정할 때 표준이 정하는 것은 **추가·변경되는 줄**의 형태뿐 — 같은 파일의 기존 줄은 고치지도(전파 금지)» · reviewer :84 «이번 작업이 **touched한 코드만** — untouched 면제(grandfather)» | R-3442 «손대는 값 객체 … 손대는 슬라이스에서 제거»는 **VO 단위** → 줄 단위 선례와 충돌 — **MAJOR-3**. 계획 D1-3은 이 문면을 의도했으나 rv3 C의 요구는 «하우스룰 이관 원칙 준용»이었고 그 원칙은 줄 단위다 |
| 집행선(delegatedTo discipline-reviewer) | reviewer frontmatter skills = discipline-cleancode·discipline-tdd·implementation-test·discipline-houserules(**architecture-ddd 없음**) · :131 «로드한 4 스킬의 절을 근거로 인용» · rulepack `agents` 필드는 런타임 주입 경로 없음(rulepack 소비자는 design-architect symbols뿐) · architecture-ddd-final 위임 52건이 전부 같은 명목 패턴 | R-3442/3443 리뷰어 집행 **없음**(기존 패턴 답습 — 신규 결함 아님) — **MAJOR-2**의 절반 |
| 코더 읽기 경로 | coder frontmatter skills = implementation-django/ninja/web/python·discipline-tdd·implementation-test(**architecture-ddd 없음**, 본문 참조 0) · 레인 스펙 2건(`.dddjango/20260829-1601-llm-gateway-caller-settings`·`20260831-1130-query-translation` design-spec.md)에 `isinstance(` **0** → A 관용구는 코더 자체 산물 · qt 스펙 :63 «timeout 양의 유한 **float**»(architect 문면)이 float 재검사의 촉발 | §3.1 예제·불릿을 읽는 것은 architect·design-review-ddd뿐 → **VO를 실제로 쓰는 코더에게 닿는 문면 변경 0** — **MAJOR-2** |
| 검사기 docstring «검출 한계» 4항 | 로컬 중간 base 전이 면제 없음 · Attribute receiver 무검사 · 동명 비선언 별칭 면제 · 동명 로컬 클래스 — 형상 프로브 C-3~C-5·픽스처 C-6·C-7과 정합 | 검증됨 |

## 4. 판정·수정 요구

BLOCKER 0 · **MAJOR 4** · MINOR 3 · 검증됨 다수.

| # | 심각도 | 내용 | 수정 요구 |
|---|---|---|---|
| MAJOR-1 | 규범 결정성(Q1-c) | R-3442 문면의 판별 기준이 **비결정적**: «타입 체커가 통과시키는 값의 거부는 값 검사(`type(x) is T`)» vs «시그니처가 수용을 약속한 값은 거부하지 않는다» — `bool`⊂`int`와 `int`→`float` **둘 다** 체커 통과·둘 다 시그니처 수용이라 두 문장이 서로를 부정하고, 괄호의 예시 2개만이 결론을 정한다. 열거 밖(`str` 하위 — `StrEnum` 멤버가 `str` 자리 · `IntEnum` in `int` · `float` in `complex` · `Decimal`)은 레인이 판별 불가. 실증: 발주측이 같은 날 `type(timeout_seconds) is not float`를 4파일에 채택(qt 스펙 «유한 float» 유래) — 규범 예시와 정반대 | 판별 기준을 1문장으로 닫는다 — 예: «거부가 허용되는 것은 선언 타입의 **하위 클래스 중 값 의미가 다른 것**(`bool`⊂`int`)뿐이다. 수치 탑 승격(`int`→`float`·`float`→`complex`, PEP 484)과 그 밖의 하위 클래스는 시그니처가 수용을 약속한 값이라 거부하지 않는다». 근거(수치 탑)를 적어야 레인이 «고치지» 않는다. graph-owned → ttl 리비전(R-3442 rev2) |
| MAJOR-2 | 예방 경로(Q1 총괄) | 수리한 문면(§3.1 예제·불릿·R-3442/3443)을 **코더도 discipline-reviewer도 읽지 않는다**(frontmatter skills 실측). 레인 스펙에 관용구 0 → 문제의 생산자(코더)가 읽는 코퍼스(implementation-python §12 coercion·Validator :792·houserules §4)는 무변경. delegatedTo reviewer는 명목(52건 기존 패턴). 결과: A «예방»의 유일 경로는 architect 명세 문면(qt :63 «float» 같은 유형 불변식 서술 억제)뿐 | ⑥에서 결정: (a) 검수표·회신에 «집행선 없음 — 예방은 architect 명세 경유·리뷰어는 architecture-ddd 미로드»를 사실대로 기록, (b) 코더가 읽는 자리(implementation-python §12 또는 houserules §4)에 R-3443 교차 참조 1줄 — 별도 리비전 후보로 로드맵 등재(R-14b). 이번 배치에서 문면을 더 늘리지 않더라도 «예방한다»는 서술은 «architect 명세 경유로 예방 기대»로 낮춘다 |
| MAJOR-3 | 적용 대상 granularity(Q3) | «손대는 값 객체 … 손대는 슬라이스에서 제거»(VO 단위)가 houserules :29 «추가·변경되는 줄만 — 기존 줄 전파 금지»·reviewer :84 «touched한 코드만» 줄 단위 선례와 충돌. kkebi `type() is` 68행·spring 27행이 «한 줄 수정 슬라이스»에서 제거 의무로 켜지고, spring은 레인 테스트(int 거부 기대)까지 삭제해야 함 — 하우스룰 «없다 → 이 작업의 것이 아니다»와 정면 | 둘 중 하나 명시: «손대는 값 객체의 **추가·변경되는 줄**에 적용(기존 줄 전파 금지 준용)» 또는 «이 규범은 VO 단위로 전파 금지를 override한다(죽은 재검사 제거는 의미 불변)» — 후자면 reviewer/houserules 쪽에도 같은 문장 필요. 계획 D1-3 문면과 rv3 C 요구(«하우스룰 이관 원칙 준용») 사이의 불일치를 ⑥에서 확정 |
| MAJOR-4 | 문서 사실 정합(Q5) | 로드맵 R-14 행이 회신과 3곳 모순(C 문면 수리 계획·«#493 무충돌»·«레인 간 해석 불일치»·상태 «① 진행 중») — 이력 불릿(:87-89)은 맞으나 행 본문이 반대 사실을 진술 | R-14 행을 회신 처분으로 갱신(A 규범 R-3442/3443 · C 검사기 alias 사각 · B 기각 · 상태 ④ 완료·⑤ 진행) |
| MINOR-1 | 수치 | «무기록 7» → 8(확정 6 + 0827 불명 2) — rv1 산술 오류 승계 | 회신·rv1 정정(«6 확정 + 2 불명») |
| MINOR-2 | 수치 | «5표면» 중 Coordinator :133은 «문법 없는 자리만 면제»(enum 명시 없음) | «4표면 명시 + Coordinator 총칭»으로 |
| MINOR-3 | 회신 문면(Q2) | «멤버 주석 부착은 R-3154 위반·결정적 검사기 무감(mypy·리뷰어만)·이제 별칭도 원명 해소라 우회 동기 소멸» 명시 부재 | 회신 C행에 1문장 |
| 검증됨 | — | 예제 full/plain 0(원본 2/1) · 레인 형상 4→0 + 값 검사 10케이스 생존 · 증거 6→0 · 우회 형상 #493 0·mypy [misc] 3 · 픽스처 good 3→0·bad 7→8 · spring 3225/kkebi 173 차분 0 · read-only verify 4종 green · 문면 byte 일치 · 잔재 2파일 17:57 커밋 · codex 미러 byte 동일 · main 검사기 = v2.17.16 태그 · 회신·조감도에 노동 절감 과대 서술 없음(계획 v2 «절감 0·예방만» 유지) | — |

효과 프레이밍(Q5): 회신은 효과를 서술하지 않고(과대 0), 조감도 행은 실측(mypy 0·차분 0·6→0)만 적으며 «절감» 어휘 없음, 계획 v2 «노동 절감 0·예방만» 유지 — **지킴**. 단 MAJOR-2에 따라 «예방» 자체가 architect 경유 기대치임을 ⑥ 문서가 밝혀야 과대가 아니다.

## 5. 10줄 요약

1. A 예제: 렌더 md §3.1 추출본 mypy 2.3.1 full(strict+warn_unreachable+redundant-expr+truthy-bool 등) **0** · plain strict **0**(main 원본 2/1) — 검증됨. 레인 형상 `generation_settings.py`@59a9f10 4건 → 새 규범 사본 **0건**, 런타임 10케이스에서 공백·범위·bool 가드 전부 생존(float 자리 int만 수용) — 검증됨.
2. C′: main 검사기(=v2.17.16 태그 md5) 증거 2파일 **#493 6 → HEAD 0** 독립 재현 · 라이브 HEAD 실파일 0/0 · «별칭 없이/있이 주석 부착» 우회는 HEAD에서도 #493 0·mypy `[misc]` red 유지 · 픽스처 good 3→0·bad 7→8 — 검증됨.
3. 표본 외: spring@96e8719 3311행/3225 blocker · kkebi@6608fb0 347행/173 — orig/patched `diff` **0행** · 사이드카 생성 0 · read-only verify 4종(ledger·render-sync·mirror --check·seal --check --draft) green.
4. **MAJOR-1** R-3442 판별 기준 비결정: bool⊂int와 int→float 둘 다 «체커 통과»이자 «시그니처 수용»이라 두 문장이 상충, 예시 2개 밖(str 하위·IntEnum·complex)은 레인이 판별 불가 — 발주측이 같은 날 `type(timeout_seconds) is not float`를 4파일에 채택(규범 예시와 반대). 수치 탑 근거로 1문장 닫기(rev2).
5. **MAJOR-2** 예방 경로: 코더·discipline-reviewer 모두 architecture-ddd 미로드(frontmatter 실측) · 레인 스펙 2건에 `isinstance(` 0 → 관용구는 코더 산물이고 수리 문면은 architect·design-review-ddd만 읽음 · delegatedTo reviewer는 명목(기존 52건 패턴). «예방»은 architect 명세 경유 기대치로 낮추고 코더 측 교차 참조 1줄을 R-14b로 등재.
6. **MAJOR-3** «손대는 값 객체 … 슬라이스에서 제거»는 VO 단위 — houserules :29 줄 단위 전파 금지·reviewer :84 touched-only와 충돌. kkebi `type() is` 68행·spring 27행(+레인 테스트)이 한 줄 수정 슬라이스에서 제거 의무로 켜짐 — 줄 단위 정렬 또는 override 명시 중 확정.
7. **MAJOR-4** 로드맵 R-14 행 본문이 회신과 3곳 모순(C 하우스룰 §2 수리·«#493 무충돌»·«레인 간 해석 불일치»·«① 진행 중») — 갱신 필요.
8. 회신 수치: «A/C 발화 3레인 무기록»·«orig 6→0»·«차분 0»·«잔재 2파일 17:57 커밋(96e8719)» 검증됨 · «무기록 7»은 표 실계수 **8**(확정 6+불명 2 — rv1 산술 오류 승계, MINOR) · «5표면» 중 Coordinator :133은 enum 무명시 총칭(MINOR).
9. 회신 C행에 «주석 부착 = R-3154 위반·결정적 검사기 무감(mypy·리뷰어만)» 명시 없음(MINOR) — 우회 불필요·R-3154 옳음은 암시적으로만 전달.
10. 효과 프레이밍: 회신·조감도에 «절감» 서술 없음, 계획 v2 «노동 절감 0·예방만» 유지 — 지킴. BLOCKER 0 · MAJOR 4 · MINOR 3.
