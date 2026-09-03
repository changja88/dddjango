# 현장 보고(typecheck) 수리 — 3단계(계획 v1) 적대 리뷰 A(기술) — 2026-09-03

리뷰어 A. 저장소 무수정(읽기 + 스크래치 실행만). 스크래치 `scratchpad/b3/rv3/` — `scripts_patched/`(계획 2.2 그대로 패치한 검사기 사본 · `patch.diff` 134행) · `fx/`(계획 §2.4 픽스처 그대로) · `fxv1/`(수정안) · `cx/`(반례 21형) · `before/`·`after/`(양 저장소 JSON 레코드 전건 + `*.diff.txt`) · `mypy/`. 도구: mypy 2.3.1(spring_dream .venv) · spring_dream HEAD `fbe77ee`(작업 트리 dirty — 전/후는 같은 트리 대조) · kkebi HEAD `6608fb0`.
Serena: skipped — opt-in 표식 없음. graphify: 표식 없음.

## 1. 판정 표

| # | 항목 | 판정 | 근거(파일:행 · 실측) |
|---|---|---|---|
| P2-1 | §2.4 하네스 갱신 대상 | **MAJOR(오기 + 조건부→무조건)** | `fixture_matrix.py:111 ("bad_rules", 2)` 의 2 는 **기대 exit 코드**이고 23개 PLAIN_PAIRS 공용이다 — 3 으로 바꾸면 전 레인 불일치(exit 3 없음). fixture_matrix 는 **무변경**(실측 good exit 0 · bad exit 2 유지). 실제 대상: `findings_count_matrix.py:130` EXPECTED `(2, 11, 2, "…#493×7…")` → 실측 `(2, 12, 2, "#358×2,#456×2,#493×8,#69×2", "9a052fb04df6b258", "4641ad36d5748105", "757f8b708079b5e4")` — census 대상이 곧 픽스처라 «alias 형상이 census 에 없으면 불변»은 성립 불가(bad 파일 추가 = 무조건 변경). `checker_baseline_matrix.py:252` `(2, 11, 11, 4, False)` → `(2, 12, 12, 4, False)`. `checker_cross_matrix.py` +1행(아래 P2-2). `construct_drift_report` 는 8종 목록에 없어 무관 |
| P2-2 | §2.4 bad 픽스처 형상 | **MAJOR(이웃 검사기 red)** | 계획 그대로(`from application.orders.domain_layer.x import Plain as StrEnum` in `shared_value_object/`) → `check-domain-model` **#298 red**(shared_value_object 는 같은 폴더·exception 외 import 금지) + `check-layer-skeleton` #488 26→28(신설 폴더 `__init__.py` 부재) → cross matrix «모순-이월»(현재 0건 규율) 발생. 수정안 V1 실측: 같은 폴더 import(`…shared_value_object.plain import Plain as StrEnum`) + `domain_layer/__init__.py`·`shared_value_object/__init__.py` → #298 소멸 · skeleton 26/29 불변(문면만 이동) · 잔여 = `check-domain-model` ⓓ#268 info ×1(good) → cross EXPECTED 신규행 `('public_surface', 'check-domain-model.py'): (0, (), ((268, 1),), '최소성')` |
| P2-3 | §2.3 «진짜 검출 감소 경로 없음» | **MINOR(문면 정정)** | 반례 a17: 프로젝트 내부 비선언 클래스가 선언적 이름(`Schema`)이고 별칭 import(`as _Schema`) → 현행 1건 검출 → 패치 후 0(면제). 기존 동명 사각(a18 별칭 없음 = 이미 0)의 별칭 확장이라 신규 축은 아니며 실측 인스턴스 0/0(양 저장소에 선언적 동명 로컬 클래스 없음). 문장을 «감소 경로 = 동명 비선언 클래스의 별칭 import(기존 동명 사각과 동종·실측 0)»으로 정정·docstring 병기 |
| P2-4 | green→red 전환(오차단 후보) | **MINOR** | a09(중간 enum base 를 `as StrEnum` 별칭 — 정당한 호환 별칭이면 검사기 red ↔ 주석 시 mypy red = 오차단) · a21(별칭 import 뒤 로컬 `class StrEnum` 재정의 — `_import_bindings` 가 그림자를 pop 하지 않음) · a15(모듈을 base 로 — 무의미 코드). a16 은 의도된 폐쇄. 실측 인스턴스 0/0. a21 은 3줄로 닫힘(모듈 수준 ClassDef/FunctionDef/Name 대입이 같은 이름을 덮으면 pop — `check-error-centralization._module_bindings:866-891` 판형) |
| P2-5 | 데코레이터 별칭 동종 사각 | **MINOR(포함 권고)** | a13/a19: `from dataclasses import dataclass as _dataclass` → 현행·패치 모두 비선언 판정(클래스 변수·`self.attr` 첫 대입 red) vs plain `@dataclass` 면제(a20). spring_dream `@_dataclass(...)` **54파일**(현재 finding 0 — frozen VO 라 형상 미발현). 같은 helper 1줄(`deco.add(bindings.get(n, n))`)로 닫힘 — 안 닫으면 docstring 에 사각 병기 |
| P2-6 | §2.1 판형 인용·§2.2 «호출처 1곳» | **MINOR** | context-isolation `_enum_local_names:826-836` 은 **모듈 한정**(`n.module == "enum"`)이라 계획의 이름-only 정규화와 다른 판형. 가까운 선례는 error-centralization `_module_bindings`/`_resolve`(:866-905 · 이름→원명 + 그림자 pop). 구현: `_scan_stmts` 시그니처에 `bindings` 를 실어 재귀 호출 10곳 + main 1곳 갱신(diff 134행) — checker_lint 0건 |
| P2-7 | 무손실 실측 | **검증됨** | (i) 기존 픽스처 good/bad **byte 동일**(exit 0/2) (ii) 신규 good alias: 원본 red 3 → 패치 0 (iii) 신규 bad shadow: 원본 미검출 → 패치 +1(#493×8) (iv) **양 저장소 전/후 차분 0/0** — spring_dream 3310 레코드(#493 3226 · ⓓ#69 84) · kkebi 345(#493 173 · ⓓ#69 172) 완전 동일 |
| P2-8 | §2.3 효과 문면 | **MINOR(정정)** | «reading `_StrEnum` 2파일 형상이 오탐이던 것이 green» — 실파일은 **주석 부착형**(`SINGLE: str = …`)이라 현행도 미검출 → 현재 저장소 효과 0. 오탐은 STOP-C(09-01) 이전의 무주석 alias 형상에서만 성립 — 픽스처가 유일한 증거. 효과는 «다음 alias 레인의 blocker 예방»으로 써야 한다 |
| P2-9 | 1(c) `_import_bindings` 범위 | **검증됨(잔여 병기)** | 모듈 본문 + if/try 재귀로 a03(try 폴백 alias)·a06(TYPE_CHECKING alias) 해소. 잔여(현행과 동일 · 회귀 아님): a04 함수 안 import + 함수 지역 클래스 · a11 `with suppress(ImportError)` 안 import · a05 `import *` 는 양쪽 면제. docstring «모듈 스코프 import 만 해소» 병기 |
| P2-10 | 1(b) 별칭 그림자 면제 해제 = 진짜 위반? | **검증됨(조건부)** | 비-enum Foo 를 `as StrEnum`(a16) → 진짜 위반. 정당한 호환 별칭은 통상 **같은 이름**(`from backports.strenum import StrEnum` · try/except 동명)이라 무영향(a03 이 alias 형 폴백도 해소 증명). 유일한 정당 반례 = a09(중간 base 별칭) · 실측 0/0 |
| P1-1 | 새 예제 mypy | **검증됨** | `mypy/money_new.py`(계획 문면 b4 전체 + PhoneNumber `-> None`): `--strict --warn-unreachable --enable-error-code redundant-expr` **0건** · plain `--strict` **0건**. 원본 블록(정확 추출): full → `unreachable`:17 + `no-untyped-def`:56 / plain → `no-untyped-def`:56. 런타임 `Money(True)`·`Money(-1)` ValueError · `Money(3)` OK |
| P1-2 | `type(x) is bool` ↔ #69 | **검증됨** | 검사기(`fx69/`): money.py ⓓ#69 **0** · 대조 `isinstance(self.amount, bool)`·`not isinstance(self.seconds, float)` → ⓓ#69 각 1(timeouts.py:18·:27). 세 형 모두 raise-only 본문이라 **mypy 는 전부 침묵** — 차이는 #69 소음뿐 |
| P1-3 | 같은 블록의 다른 §4 자기 위반 | **MAJOR** | `subtract()` 지역 `result = self.amount - other.amount` → **#493 blocker**(money.py:30) — 원본·새 예제 모두. 계획은 PhoneNumber `-> None` 만 «§4 자기 위반 해소»로 동승시키고 이것은 «불변» 처리. R-3156 으로 예제 자체는 면제되나 레인은 예제를 그대로 베낀다 → 베낀 `subtract` 가 즉시 blocker. 수정: `result: int = self.amount - other.amount`(mypy 0/0 유지) |
| P1-4 | int→float 구멍 vs 예제 | **MINOR(문면)** | 드리프트 아님(R-3442 는 분류문 · 예제에 float 필드 없음). 단 «선언 타입의 재검사…두지 않는다» 와 «int→float 거부는 값 검사» 가 `seconds: float` + `type(x) is not float`(문자 그대로 선언 타입 재검사)에서 자기모순으로 읽힌다. 실측 `type(self.seconds) is not float` → mypy 0 · #69 0. 문면: «타입 체커가 **이미 거부하는** 입력의 재검사·강제 변환은 두지 않는다 … 통과시키는 값(bool⊂int·int→float)의 거부는 값 검사 — `type(x) is T` 형(isinstance 형은 ⓓ#69 후보)» |
| P1-5 | PhoneNumber 함수 안 `import re` | **검증됨(충돌 없음)** | 코퍼스(skills·agents·commands) 함수 안 import 규율 0건 · implementation-python §22 ruff select 에 PL/PLC 없음 · spring_dream/kkebi `ruff.toml` select(E,F,B,I,C90,N,UP,ANN,DJ,RUF,PD,TCH) PLC0415 없음 · 양 저장소 프로덕션 함수 안 import 20건 |
| P1-6 | R-3442 wiring | **MINOR** | «enforcedBy #69 **또는** delegatedTo» → 선례 R-1066·R-1098(ⓓ#69 규범, `agent-discipline-reviewer.ttl` wiring :535-540/:622-627)은 **둘 다** 보유. rulepack 은 R-1098 을 이 검사기 아래 등재(`rulepack.json:1113-1115`) · aliases.ttl 등재 불요. 채번 대안(docstring 만)은 R-1098 의 ⓓ#69 물음에 감수자가 인용할 규칙이 없어 집행선 0 — 채번 권고 |
| P1-7 | Part 1 IRI·파일 전수 | **검증됨** | §1.3 열거 = b3·b4·R-3442 Work+Expression·wiring·ISSUED(다음 번호 R-3442 확인: tail R-3441)·LEDGER `architecture-ddd-final s016-3.1 graph`(:963)·final.md·`workspace/reference/architecture-ddd/reference/final.md`·`codex-dddjango/skills/dddjango-architecture-ddd/references/final.md`·rulepack ×2. manifest_seal 그룹: `dddjango/skills/**/*.md`·`codex-dddjango/skills/**/*.md`·`ontology/**/*`·`rulepack.json` 전부 봉인 → draft 재봉인 1회로 Part 1·2 공동 처리 |

## 2. 반례 목록 (`cx/` — 각각 BC 모양 트리 1파일 · #493 건수 · 원본 vs 패치)

| 형상 | 원본 | 패치 | 판정 |
|---|---|---|---|
| a01 로컬 `class StrEnum(str, Enum)` + 상속 | 0 | 0 | 동일 |
| a02 `StrEnum = _Base` 재바인딩(모듈 변수 무주석 1) | 1 | 1 | 동일(멤버 미검출 유지) |
| a03 `try: from enum import StrEnum as _S / except ImportError: …as _S` | 1 | 0 | **오탐 소거** |
| a04 함수 안 `import … as _S` + 함수 지역 클래스 | 1 | 1 | 잔여 사각(동일) |
| a05 `from enum import *` | 0 | 0 | 동일 |
| a06 `if TYPE_CHECKING: … as _S` | 1 | 0 | **오탐 소거** |
| a07 `from .base import StrEnum`(동명 상대 import) | 0 | 0 | 동일(동명 사각 유지) |
| a08 `import enum as e; class X(e.StrEnum)` | 0 | 0 | Attribute 경로 유지 확인 |
| a09 `from …domain_enum import DomainStrEnum as StrEnum`(정당 별칭) | 0 | **1** | green→red(오차단 후보 · 실측 0) |
| a10 `Plain as StrEnum` 뒤 `from enum import StrEnum` 재import | 0 | 0 | 마지막 바인딩 승 |
| a11 `with suppress(ImportError): … as _S` | 1 | 1 | 잔여 사각(동일) |
| a12 `import enum; StrEnum = enum.StrEnum` | 1 | 1 | 동일(모듈 변수 1) |
| a13 `@_dataclass(frozen=True)` + 클래스 변수 | 1 | 1 | 데코레이터 별칭 사각(동종 · 미폐쇄) |
| a14 `BaseModel as _BaseModel` + `model_config = _ConfigDict(…)` | 1 | 0 | **오탐 소거**(StrEnum 밖 형상) |
| a15 `import pkg as Schema; class Foo(Schema)` | 0 | 1 | 무의미 코드 · 무시 |
| a16 `from enum import StrEnum` 뒤 `Plain as StrEnum` | 0 | **1** | **미탐 폐쇄(의도)** |
| a17 프로젝트 내부 비선언 `Schema` 를 `as _Schema` | **1** | **0** | **진짜 검출 감소(유일)** · 실측 0 |
| a18 같은 것 · 별칭 없음 | 0 | 0 | 기존 동명 사각 |
| a19 `@_dataclass` 비-frozen `self.last = v` | 1 | 1 | 데코레이터 별칭 사각 |
| a20 `@dataclass` 동형 | 0 | 0 | 대조군 |
| a21 별칭 import 뒤 로컬 `class StrEnum` 재정의 | 0 | **1** | green→red · 그림자 pop 부재 · 실측 0 |

## 3. 전/후 차분 표

| 대상 | 전 | 후 | 차분 |
|---|---|---|---|
| spring_dream_server(전 파일 · JSON 레코드) | 3310 (#493 3226 · ⓓ#69 84) · exit 2 | 3310 · exit 2 | **0 제거 · 0 추가**(`after/spring_dream_server.diff.txt` 빈 파일) |
| kkebi-server | 345 (#493 173 · ⓓ#69 172) · exit 2 | 345 · exit 2 | **0 / 0** |
| 픽스처 `public_surface/good`(기존) | clean 12파일 · exit 0 | byte 동일 | 0 |
| 픽스처 `public_surface/bad_rules`(기존) | blocker 11 · exit 2 | byte 동일 | 0 |
| 신규 good `book_usage_policy.py`(무주석 alias) | red 3(#493 :7·:8·:9) | clean(V1: 15파일) | −3(오탐 소거 증거) |
| 신규 bad `aliased_shadow.py` | 미검출(11) | +1 `LIMIT`(12) | +1(미탐 폐쇄 증거) |
| cross matrix(`public_surface/good` × 27종) 계획 그대로 | — | skeleton #488 26→28 · domain-model ⓓ#268 +1 | 2행 변동 |
| cross matrix V1(같은 폴더 import + `__init__.py`×2) | — | skeleton 26 불변 · domain-model ⓓ#268 +1(exit 0) | 1행 신규 |
| bad_rules × domain-model 계획 그대로 | clean | **#298 red** + ⓓ#268 | 이웃 검사기 red(V1 에서 소멸) |

## 4. 계획 수정 요구

**BLOCKER — 없음.**

**MAJOR-1(P2-1) 하네스 갱신 문면 교체 → 통과 조건**: §2.4 «`fixture_matrix.py:111 ("bad_rules", 2)` → 3» 삭제(무변경). 대신 ① `findings_count_matrix.py:130` EXPECTED 를 `--emit-expected` 로 재생성(실측 `(2, 12, 2, "#358×2,#456×2,#493×8,#69×2", 9a052fb0…, 4641ad36…, 757f8b70…)` — sha 는 최종 픽스처 내용에 종속 · 사유를 커밋 메시지에 전건 기록) ② `checker_baseline_matrix.py:252` → `(2, 12, 12, 4, False)` ③ `checker_cross_matrix.py` 신규행 `('public_surface', 'check-domain-model.py'): (0, (), ((268, 1),), '최소성')` ④ «census 에 없으면 불변» 문장 삭제(무조건 변경). construct_drift 무관 명기.

**MAJOR-2(P2-2) bad 픽스처 형상 → 통과 조건**: `aliased_shadow.py` 의 import 를 같은 폴더(`application.orders.domain_layer.shared_value_object.plain`)로 바꾸고, good/bad 양쪽 `domain_layer/__init__.py`·`shared_value_object/__init__.py`(빈 파일) 추가 — 실측 #298 소멸 · skeleton 건수 26/29 불변 · public-surface 결과(0 / +1) 유지. 픽스처 커밋에 «27종 교차 실행 결과: domain-model ⓓ#268 info 1 외 변동 0» 기록.

**MAJOR-3(P1-3) b4 교체 문면 → 통과 조건**: `subtract()` 의 `result = …` 를 `result: int = self.amount - other.amount` 로 동승(같은 «§4 자기 위반 해소» 사유 · mypy 0/0 유지 · 검사기 #493 0 재실측 — `fx69/` 판형으로).

**MINOR(권고)**: (P2-3·P2-4·P2-9) docstring 사각 병기 문면을 «모듈 스코프 import 만 해소 · 원명 기준이라 동명 비선언 클래스의 별칭(a17)·중간 base 의 선언적 이름 별칭(a09)은 각각 면제/비면제로 갈린다(receiver·모듈 무검사)»로 · a21 은 error-centralization 판형(모듈 수준 ClassDef/FunctionDef/Name 대입의 그림자 pop) 3줄 포함 · (P2-5) 데코레이터도 같은 `bindings.get` 정규화 포함(54파일 노출) · (P2-6) 선례 인용을 error-centralization `_module_bindings`/`_resolve` 로 · «호출처 1곳» → «`_scan_stmts` 시그니처 관통(재귀 10곳+main)» · (P2-8) 효과 문면 «현재 저장소 차분 0 — 무주석 alias 형상(STOP-C 이전)의 재발 예방» · (P1-4) R-3442 문면 «이미 거부하는 입력의 재검사» + `type(x) is T` 형 명시 · (P1-6) wiring 은 R-1098 선례대로 delegatedTo + enforcedBy 둘 다 · 채번 채택.

**부기(범위 밖 · 로드맵)**: 검사기는 파싱 실패 파일을 조용히 건너뛰고 «clean — 파일 N개»에 포함한다(`:413-416` `except SyntaxError: continue`) — 문법 오류 파일이 green 으로 계수되는 fail-open. 이번 리뷰에서 펜스 포함 추출로 실제로 겪음.

## 5. 10줄 요약

1. BLOCKER 0 · MAJOR 3 · MINOR 8 — 계획의 판정식·무손실 방향은 성립하나 하네스·픽스처·예제 동승 범위에 오기가 있다.
2. [검증됨] 계획대로 패치한 사본: 기존 픽스처 good/bad byte 동일(exit 0/2) · 신규 good alias 3→0 · 신규 bad shadow +1(#493×7→×8) · spring_dream(3310 레코드)·kkebi(345) 전/후 차분 **0/0** — 진탐 집합·게이트 강도 불변.
3. [MAJOR-1] `fixture_matrix.py:111` 의 2 는 23개 레인 공용 **exit 코드** — 3 으로 바꾸면 전 레인 red · fixture_matrix 는 무변경. 진짜 대상은 `findings_count_matrix` EXPECTED(무조건 변경 · 실측 `(2,12,2,"…#493×8…")`+sha 3)·`checker_baseline_matrix` `(2,12,12,4,False)`·`checker_cross_matrix` +1행.
4. [MAJOR-2] 계획의 bad 픽스처는 `shared_value_object/` 에서 타 모듈을 import 해 `check-domain-model #298` red + skeleton #488 26→28(신설 폴더 `__init__.py` 부재) — 같은 폴더 import + `__init__.py`×2 로 바꾸면 잔여는 domain-model ⓓ#268 info 1뿐(실측).
5. [MAJOR-3] 같은 graph-owned 블록의 `subtract()` 지역 `result = …` 가 #493 blocker(원본·새 예제 모두) — PhoneNumber `-> None` 동승과 같은 «§4 자기 위반» 사유인데 누락 · `result: int = …` 1토큰 동승 요구(레인이 베끼면 즉시 blocker).
6. [반례] 진짜 검출 감소 경로 **1형 존재**(a17 — 동명 비선언 클래스의 별칭 import · 기존 동명 사각의 확장 · 실측 0/0) → «없음» 문면 정정; green→red 전환 a09(정당 중간 base 별칭)·a21(별칭 뒤 로컬 재정의 · 그림자 pop 부재 · 3줄로 폐쇄)·a16(의도) · 데코레이터 별칭(a13/a19 · SD `@_dataclass` 54파일)은 동종 사각 미폐쇄 — 같은 helper 로 포함 권고.
7. [효과 정정] 실파일 `_StrEnum` 2개는 주석 부착형이라 현행도 미검출 — 현재 저장소 오탐 소거 0 · 효과는 무주석 alias 형상(STOP-C 이전)의 재발 예방이며 픽스처가 유일한 증거(kkebi 는 선언적 base 별칭 자체 0).
8. [Part 1 실측] 새 블록 mypy strict+warn_unreachable+redundant-expr 0 · plain strict 0(원본: unreachable 1 + no-untyped-def 1) · `type(x) is bool` ⓓ#69 0(isinstance 형 2건 발화 · 셋 다 mypy 침묵) · `type(x) is not float` mypy 0·#69 0 · 함수 안 `import re` 는 코퍼스·양 저장소 ruff(PLC0415 없음) 무충돌.
9. [문면] R-3442 «선언 타입의 재검사 금지» ↔ «int→float 거부는 값 검사» 가 `type(x) is not float` 에서 자기모순으로 읽힘 → «타입 체커가 이미 거부하는 입력의 재검사» + `type(x) is T` 형 명시; wiring 은 R-1066/R-1098 선례대로 delegatedTo+enforcedBy 둘 다 · 채번 채택(docstring 만이면 ⓓ#69 물음에 인용할 규칙 없음).
10. [정합·일반화] Part 1 IRI·미러·봉인 전수 완비 · Part 2 는 위 하네스 3종 + `__init__.py` 누락 · 선례 인용(context-isolation 은 모듈 한정 판형 — 실제 선례는 error-centralization `_module_bindings`) · 구현은 `_scan_stmts` 관통(재귀 10곳+main · checker_lint 0건) · Claude/Codex byte 미러·플래그 비의존·kkebi 대조 성립.
