# 현장 보고(typecheck) 수리 — 절차·적대 리뷰 루브릭 (2026-09-03 사용자 확정)

- 대상: `2026-09-03-field-report-spring-dream-typecheck.md`의 A(값 객체 예제 타입 재검사)·C(하우스룰 §2 Enum 멤버 주석). B(mypy·ruff 결정적 G2 게이트)는 사용자 판정으로 **기각·발주측 소관**(프로젝트 툴체인·pre-push 훅·발주서 체크리스트 — R-12 가이드 1줄만). 로드맵 R-14.
- 성격: 그래프 정본 문면 리비전(실행기·검사기 무변경 예정). 판형 = 배치 2 루브릭(`2026-09-03-repair-batch-2-rubric.md`) 6단계 + 배치 3 보강(⓪ 증거·⑥ 재검). 적대 리뷰는 **①·③·⑤ 3회 + ⑥ 감사·재검**, 매회 독립 서브에이전트 3기(기술·규범·증거/표본 외), ⓐ 실측 재현성·ⓑ 무손실 판정식·ⓒ 효과 과대 추정 필답 + 3축(코퍼스 정합·일반화·무손실) + 심각도(BLOCKER/MAJOR/MINOR/검증됨).
- 결정 게이트 3: ① 뒤 «수리 범위 확정»(A·C 유지/축소·보고서 제안 3·4 채택 여부) → ③ 뒤 «문면 확정» → ⑥ 뒤 «릴리즈». 릴리즈 판단 재료: 실행기·검사기 무접촉이라 카탈로그 재실측 무오염·Claude 레인이라 캐시 삭제 위험 없음 → 즉시 v2.17.17 또는 승격 배치 동승.

## ⓪ 조사자(코디) 검증 결과 (2026-09-03 — 리뷰어는 이 전제를 공격한다)

- **A 재현**: 플러그인 예제 `dddjango/skills/architecture-ddd/references/final.md` 490~505행(graph-owned 절 473~548 · 정본 `ontology/rules/architecture-ddd-final.ttl` ≈2222)이 `amount: int` 선언 후 `isinstance` 재검사+`int()` 강제 변환. mypy 2.3.1 `--strict --warn-unreachable --enable-error-code redundant-expr`(spring_dream_server pyproject 08-26 4eaf960과 동일)로 예제 자체 → unreachable 1·redundant-expr 1(`scratchpad/b3/mypy/repro.py`). 실파일 `generation_settings.py` 4·`caller_label.py` 1 = 5건 재현. **단 plain `--strict`만으로는 두 오류 모두 발생하지 않는다**(프로젝트 추가 플래그 의존).
- **C 재현**: 하우스룰 §2 «모든 이름 첫 대입에 타입 — 예외 0 · 클래스 변수 포함»(`dddjango/skills/discipline-houserules/SKILL.md:66` graph-owned · 정본 `ontology/rules/discipline-houserules-skill.ttl:422/940`). mypy 2.3.1 `Enum members must be left unannotated [misc]` — 최소 재현 2건 + 실파일 `book_usage_policy.py` 3건. 검사기 `check-public-surface-annotation.py`(#493)는 주석 유/무 Enum 멤버 모두 clean(`scratchpad/b3/mypy/fx/`) → 검사기↔mypy 충돌 없음, 문면↔mypy 충돌만. 해석 불일치 실증: reading 레인은 주석 부착, 카탈로그 레인은 미부착(`fortune_visibility_status.py`).
- **B 사실 확인**: Coordinator 172행 mypy «구성돼 있으면 결과 보고»·ruff 무언급·백스톱 27종 무포함. 레인별 실행 불일치(accounts·fortune-calculation·chat-relay·fortune-character-2 실행 / query-translation·fortune-reading REPORT mypy 언급 0). → 기각(발주측).

## ① 공격 질문 (항목마다 필답 · 판정 병기)

- A-1 «타입 재검사는 프로덕션에서 죽은 조건»이 참인가 — 값 객체가 `object`/`Any` 입력을 받는 경로(역직렬화·DB 스냅숏 복원·폼 cleaned_data·JSON)가 전부 경계에서 먼저 좁히는가. spring_dream_server 호출처 전수(보고서는 Serena로 확인 주장 — 독립 재확인)·kkebi-server 대조.
- A-2 예제 교체가 DDD «자기 검증(Self-Validation)» 원칙과 코퍼스의 다른 문면(discipline-cleancode·implementation-python Validator 예제·pydantic strict 절)을 약화·모순시키는가. «타입은 시그니처·mypy 소유, 값 불변식만 검증» 문장이 plain strict 프로젝트에서도 옳은가(플래그 무관한 원칙인가, 아니면 redundant-expr 프로젝트에만 맞는 처방인가).
- A-3 보고서 제안 3(«선언 타입 위반 인자를 `# type: ignore[arg-type]`로 넘기는 거부 테스트 금지 · 경계 좁히기는 object 입력으로 테스트») — discipline-test/implementation-test 코퍼스와 정합·과적합 여부. 제안 4(예제 mypy 스모크 하네스) — 비용 대비·과적합.
- C-1 Enum 예외가 «예외 0 — 조건부 면제는 흔들리는 암묵 규칙»의 취지를 깨는가. 미끄럼길: typing spec이 «주석 금지/필수»를 정하는 다른 자리(Enum 멤버 금지 · `TypeAlias`·dataclass 필드·NamedTuple 필드 필수 · `__slots__`·`__match_args__` 등)를 **닫힌 목록**으로 열거할 수 있는가 — 열거 가능하면 «문법이 정한 자리»로 예외를 닫는 문면이 가능한지.
- C-2 architect symbols 문법 b35(`NAME = "literal"` 허용)·#493 검사기 동작(Enum 본문 미검사가 의도인지 우연인지 코드로 확인)·implementation-python «타입 어노테이션 상시 유지» 규범과 정합.
- ⓒ 효과: A·C를 고치면 무엇이 줄어드는가(레인당 mypy 정리 노동·G2 후 정리 커밋) — 과대 추정 여부. 표본 외(kkebi) 발화 유무.

## 3·5단계 3축 · 심각도

배치 2 루브릭 §3·심각도 준용. 코퍼스 정합 = 건드리는 IRI·검사기·문법 성문 전수 열거. 일반화 = Claude/Codex 동일·프로젝트 플래그 비의존·kkebi 대조. 무손실 = 검사기 무접촉(검출 집합 불변)·게이트 강도 불변.

## 1단계 결과 (2026-09-03 — 적대 리뷰 3기 A 기술·B 규범·C 증거 · 산출 `workspace/eval/field-report-typecheck/rv1/`)

| 항목 | 판정 | 핵심 근거 |
|---|---|---|
| A 문제 성립 | **검증됨** | redundant-expr 16 = VO 11(2레인: llm_access claude 5·query_translation codex 6) + 리딩 service_runtime 2 + 비-dddjango 3. 숨은 A: fortune_character `# type: ignore[redundant-expr]` 3·wallet/chat_relay `x: object = …` 우회 5 → 관용구 노출 6/23 run. 코퍼스 판정 부재 실증(같은 관용구를 레인마다 무처리/억제/우회) |
| A 전제 «죽은 조건» | **MAJOR(과장)** | mypy는 `float` 인자에 `int`·`int` 인자에 `bool`을 통과 → float/bool 가드는 살아 있고 레인 테스트가 그 거부를 기대(`test_generation_settings.py:96`). 어드민 폼 2곳은 `dict[str, Any]`를 팩토리에 직접 전달(«호출처 전부 str» 오기). 발화 형상: raise-only `if not isinstance: raise`는 침묵·or-체인/비-raise 본문만 발화 |
| A 처방 방향 | **검증됨(플래그 무관)** | «값 불변식만 검증·타입은 시그니처 소유»는 cleancode §12.7·implementation-python §12·검사기 #69(«런타임 타입 가드는 타입 체커 몫») 동방향 → 현행 예제가 자기 규범과 어긋난 내부 모순 해소. 대체 예제 strict+warn_unreachable+redundant-expr 0건 실측 |
| A 수리 범위 | **MAJOR(동반 필요)** | 같은 graph-owned 블록의 `PhoneNumber.__post_init__(self)`가 `-> None` 부재 → plain strict `no-untyped-def`(하우스룰 §4 자기 위반) 동반 수리. Money 원문 자체 발화는 unreachable 1(조사자 «2건»은 레인 형상 혼입 — 정정) |
| A MINOR 3 | 반영 | 규범 문장에 플래그명 금지 · `isinstance(x, bool)` 대신 `type(x) is bool`(#69 ⓓ 소음 0) · bool⊂int·int→float 구멍 처리를 문면에 명시(없으면 레인이 살아 있는 가드를 지우거나 ignore로 덮음) |
| 보고서 제안 3(type: ignore 거부 테스트) | 의견 갈림 | A: 축소 채택(implementation-test §15.5 «구조 재확인 테스트 reject»에 부착 — «금지» 문면은 ignore 9곳 중 8곳이 값 테스트라 오탐 지렛대) / B: 이번 범위 밖 → **결정 게이트** |
| 보고서 제안 4(예제 mypy 스모크) | **기각** | 코퍼스 예제 strict-clean 4/28·12/78 — 1블록 하네스는 과적합 |
| C 문면 수리 | **BLOCKER(불성립)** | Enum 멤버 예외는 R-3154(«프레임워크 선언 … enum 멤버(`RED = 1`)» SKILL.md:72)에 v1.0.0(e954659)부터 성문·Coordinator :133·검사기 docstring·pregate b35·rulepack 5표면 일치·양 런타임 byte 동일. 조사자 ⓪가 소문자 «enum» 검색 누락 |
| C 진짜 뿌리 | **MAJOR(원인 귀속)** | 검사기 #493 alias 사각: `from enum import StrEnum as _StrEnum` → base 이름 문자열 비교(`:135-143`)로 무주석 멤버를 blocker 오판 → 레인이 주석 부착 우회 → mypy `[misc]`. 09-01 STOP(strenum-registry-alias·2.17.12)에서 발주자 결정 C(plain StrEnum 복귀)로 종결됐으나 WIP 커밋 2파일 누락 = 잔재 6건. 전 BC 20+ StrEnum 무주석·주석은 alias 2파일뿐(상관 100%) → «레인 간 해석 불일치» 반증. 표본 외 kkebi Enum 106파일 주석 0·1/43 run 단발 |
| B(mypy·ruff 게이트) | 기각(사용자) — 사실은 검증됨 | 23 run 중 mypy 무기록 7, A/C 발화 3레인 전부 무기록 쪽·기록 16 run 발화 0 → «실행이 갈렸다» 성립. BC 스코프 실행도 pyproject 플래그 상속이라 실행만 했으면 레인 안에서 잡힘. 처방은 발주측(훅·체크리스트) |
| ⓒ 효과 | **MINOR(과대)** | 문면 귀속 19/171(11%)·나머지 89% = 비-dddjango 49% + 코더 선택 40%. 향후 ≈0.4~0.8건/run·1~3분/run + 우회 보일러플레이트 감소. kkebi: 설정 동일·전체 mypy 0건이나 관용구 21파일 존재(발화 0) → A는 «관용구 × 플래그 × 형상» 조건부 결함(spring_dream 특이 아님·plain strict 무해) |

### ⓪ 정정(원문 보존·추기)
- C «Enum 예외 누락»은 오류 — 소문자 «enum 멤버» 문면 존재. C «검사기↔mypy 충돌 없음»도 alias 형상에서는 오류(양쪽 red). A «예제 자체 2건»은 1건(unreachable)+레인 형상 1건.

### ① 결론 (결정 게이트 «수리 범위 확정» 상신)
- **A 채택**: s016-3.1 코드 블록 교체(Money 값 불변식만 + `type(x) is bool`·`-> None` PhoneNumber 동승) + 경계 문장(타입 좁히기는 `object` 입력 경계 소유 — 산문 또는 신규 채번). 선택: 제안 3 축소(implementation-test §15.5 부착).
- **C 기각**: 문면 no-op. 검사기 #493 alias 사각은 오탐 소거형 검사기 후보로 로드맵 등재(1레인·우회 결정 존재 → 필터상 보류) — 이번 배치 포함 여부는 사용자 결정.
- **B 기각 유지**(발주측). 현장 보고 회신에 C 정정(규범 미준수·잔재 2파일)·B 처분을 포함한다.

## 2·3단계 결과 (2026-09-03)
- 계획 v1 → ③ 적대 리뷰 3기(BLOCKER 0 · MAJOR 5계열 · MINOR 12) → v2 델타(문면 int→float 모순 삭제 · R-3442 Obligation + R-3443 Prohibition 분할 · brownfield 적용 대상 문장 · wiring delegatedTo discipline-reviewer만 · `result: int` 동승 · 하네스 오독 정정 · bad 픽스처 형상 · 데코레이터 별칭 포함 · R-15/R-16 등재) → 사용자 «문면 확정».

## 4단계 구현 기록 (2026-09-03 · 브랜치 `fix/field-typecheck`)
- Part 2 검사기: `_module_bindings`(모듈 수준 import 바인딩 + 그림자 pop) · `_resolved_name`(base·데코레이터 Name → 원명 · Attribute attr) · `_scan_stmts`/`_scan_class` bindings 관통 · docstring «검출 한계» 5항(⑤ 반영 후). 픽스처 good 2(`book_usage_policy.py` alias StrEnum · `reading_cursor.py` alias dataclass) · bad 2(`plain_base.py` · `aliased_shadow.py`) + `__init__.py`. EXPECTED: findings_count #493×7→8 · baseline 11→12 · cross 무변(census는 비-0 exit만 기록 — 픽스처 정리 후 public_surface/domain-model 행 제거). 하네스 green: fixture 102 · findings 73 · baseline 73 · cross 350. codex byte 미러 cmp 0.
- Part 1 그래프: rdflib 편집+canon(왕복 byte 동일 선확인) — b4 예제 교체 · b3 불릿 2 + statesNorm · R-3442/R-3443 신설(rev 1) · wiring delegatedTo · ISSUED 2행 → gate 90/90 → render --apply → LEDGER s016-3.1 재기준선(ff912545…) → target-counts +2/+2/+2 → q4 emit(3443) → make rulepack(양쪽) → 소스 미러 span 교체 + corpus_mirror_sync --write(11/11) → render-sync·ledger-check green.
- 검수표 실측: 계획서 말미 표(verify·봉인·조감도는 ⑤ 전 기입).
- 라이브 저장소 접촉: 검사기 실행만(사이드카 4건 즉시 제거) · 파일 무변경.
