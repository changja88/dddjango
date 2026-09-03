# 적대 리뷰 C — 증거·과적합·표본 외 (현장 보고 typecheck 수리 · 3단계 계획 v1) · 2026-09-03

리뷰어 C. 대상 = `workspace/plan/2026-09-03-field-report-repair-plan.md` v1. 저장소 무수정(dddjango 읽기·검사기 실행만). 표본 저장소는 읽기·검사기 실행만 — 단 **첫 baseline 실행 2회가 표본 저장소 `.dddjango/violations/`에 레코드 파일 1개씩(20260903T083259Z-bb35af28 · 20260903T083301Z-a7a8d810)을 남겨 즉시 삭제**했고 이후 전 실행은 `DJR_FINDINGS_JSON=<scratch>`로 sink를 우회했다(잔여 0 확인). 스크래치 `scratchpad/b3/rv3/`(`fx/public_surface/`는 사이비 리뷰어 산출 — 내 것 아님·참고만).
Serena: skipped — opt-in 표식(`.serena/project.yml`) 없음 · graphify 표식 없음 → 기본 도구.

## 0. 측정 환경·스냅숏 (표본이 리뷰 중 드리프트했다 — 재현 시 이 표를 기준으로)

| 항목 | 값 |
|---|---|
| dddjango | `7e93b08` · 검사기 사본 `rv3/orig/`(byte 동일) · 패치 `rv3/patched/`(§2 diff) |
| spring_dream_server 스냅숏 ① | 17:32 KST · HEAD `fbe77ee` + 작업 트리 더러움(ruff format 미커밋) |
| spring_dream_server 스냅숏 ② | 17:41 KST · **HEAD `59a9f10`**(17:36 `style: pre-push 훅 자동 정리분`) + **21 dirty** — 그중 `book_usage_policy.py`·`abstention_reason.py`가 **17:37:37에 plain `StrEnum`+무주석으로 바뀜**(HEAD는 아직 `_StrEnum`+주석) · llm_access·query_translation VO 6파일·테스트 2파일도 수정(발주측 A 정리) |
| spring 현재 mypy(훅 범위 `spring_dream_server framework`) | **122건/24파일**(rv1의 171 → 발주측 정리로 −49) · **redundant-expr 0 · Enum members 0 · unreachable 0** — A·C 발화 전건이 이미 작업 트리에서 소멸(미커밋) |
| kkebi-server | HEAD `6608fb0`(08-26) · 작업 트리 변화 없음 · 검사기 실행 전후 동일 |
| 도구 | mypy 2.3.1(spring `.venv`) · Python 3.14.7 · 검사기 실행 대상 = 저장소 루트(호출 계약) |

## 1. 형상 계수 표 (Q1 — 검사기 #493 base 판정의 사각 실발화 규모 · `rv3/census.py` 독립 AST)

범례: A1 선언적 base를 별칭 import(`from M import Decl as X`) · A1c 그 alias base 클래스 · B 비선언 클래스를 선언적 이름으로 별칭(미탐 1형) · C1 로컬 중간 base(`class _B(Decl)`→`class X(_B)`) · C2 교차 모듈 중간 base(`FrameworkErrorSchema(Schema)`→`class XErrorSchema(FrameworkErrorSchema)`) · D `from dataclasses import dataclass as _dataclass`(데코레이터 alias — 계획 밖 형제 사각) · E 모듈 본문 밖 import(전부 `if TYPE_CHECKING:` 테스트) · F 혼합 base

| 저장소(전 트리) | 파일 | 클래스 | 선언 base 클래스 | **A1 파일/A1c 클래스** | **B** | **C1 클래스(파일)** | **C2** | **D 파일/Dc 클래스** | E | F |
|---|---|---|---|---|---|---|---|---|---|---|
| spring_dream_server | 2845 | 1809 | 244 | **5 / 22** | 0 | **22 (6)** | **5** | **54 / 64** | 12(테스트) | 4 |
| kkebi-server | 3983 | 2768 | 383 | **0 / 0** | 0 | **89 (14)** | **10** | 0 / 0 | 0 | 0 |

- **A1 내역(spring 5파일 전부 fortune_reading 레인·codex)**: `_StrEnum` 2(`8216c78` 09-01 WIP · 현재 WT는 plain) · `_Schema` 2(`585c9c6` 09-03 P4 · 16 클래스) · `_BaseModel` 1(`framework/pydantic/cited_answer_schema.py` `8216c78` · 4 클래스). `_dataclass` 54파일도 같은 레인 4커밋(P1~P4 09-01→09-03)이며 비테스트 alias import 총 **35줄**(`_Literal` 13·`_Mapping` 6·`_UUID` 4·`_Schema` 2·`_StrEnum` 2 …). kkebi는 alias import 1줄(`_NinjaExtraAPI`)·선언 base alias 0.
- **C1/C2 내역**: 양 저장소 **모든 BC의 `bc_error_schema.py`**(`<Bc>ErrorSchema(FrameworkErrorSchema)` → 오류별 하위 클래스 — spring 5 BC·kkebi 10 BC) + kkebi `schema_in/out.py` 13 + `scripts/import_legacy_tarot/ledger_models.py` 4. 본문이 전부 AnnAssign이라 **현재 발화 0**(잠재).
- **판정**: «alias 사각(A1)은 reading 1레인 단발» — **검증됨**(양 저장소·양 런타임에서 fortune_reading 외 0). 단 그 레인 안에서는 **체계적 관용구**(35줄·58파일·4커밋·STOP-C 뒤에도 P4까지 지속)라 «단발 사고»가 아니라 «레인 스타일»이다 — 같은 스타일의 Codex 레인이 다시 서면 재발한다. 전이 면제(C1/C2)는 **잠재 일반**(spring 27·kkebi 99 클래스) — §4 표의 promotion 사건이 이미 실발화 선례.

## 2. 수리 전/후 실측 차분 표 (Q2 — 계획 §2.2 독립 구현 · `rv3/patch.diff` 137행)

패치 요지(계획 문면 그대로): `_import_bindings(mod)`(모듈 본문 + if/try 하위 재귀 · ImportFrom `asname or name`→`name` · Import `asname or top`) → `_base_name(b, bindings)`(Name → `bindings.get(id, id)` · Attribute → attr) → `_is_declarative_class(cls, bindings)` · bindings를 `_scan_stmts`/`_scan_class`에 관통(호출처는 클래스 진입 1곳이지만 재귀 스코프라 매개변수 관통이 필요 — 계획 «호출처 1곳» 표현은 구현 시 재귀 관통으로 읽어야 한다). 데코레이터·#69·#358·#456 무접촉.

| 대상 | 전(orig) | 후(patched) | 차분 |
|---|---|---|---|
| spring_dream 전 트리 ①(17:32) | 3226 #493 · exit 2 | 3226 · exit 2 | **0행** |
| spring_dream 전 트리 ②(17:41 · 드리프트 후) | 3225 · exit 2 | 3225 · exit 2 | **0행** |
| kkebi 전 트리 | 173 · exit 2 | 173 · exit 2 | **0행** |
| 픽스처 `public_surface/good`(임시 사본) | exit 0 · 0건 | 동일 | **byte 동일** |
| 픽스처 `public_surface/bad_rules` | exit 2 · 11건 | 동일 | **byte 동일** |
| 라이브 발견 분포(참고) | spring: framework 3079·docs 83·spring_dream_server 64 → `application/` 0(①)/32(② — 레인 신규 커밋분) · kkebi: web 110·kkebi_server 63·`application/` 0 | — | 계획이 말하는 «오탐이던 실코드»는 라이브에 **없다**(HEAD 2파일은 주석 부착으로 이미 clean·WT는 plain) |

스크래치 형상(`rv3/fx/*` · `application/orders/domain_layer/x/`):

| 케이스 | 형상 | orig | patched | 판정 |
|---|---|---|---|---|
| a | `from enum import StrEnum as _StrEnum` + 무주석 멤버 2 | 2 | **0** | 오탐 소거(ii) |
| k | **HEAD 실파일 2개**(`git show HEAD:`) — 주석 그대로 / 주석 제거 | 0 / **6** | 0 / **0** | 실코드 재현은 «주석 제거 사본»으로만 성립 |
| b | `from …plain import Plain as StrEnum` + 무주석 | 0 | **1** | 미탐 폐쇄(iii) |
| f | `from django.db.models import Model as _Model` + 필드 | 1 | 0 | (ii) |
| g | `try: from enum import StrEnum as _StrEnum / except: … as _StrEnum` | 1 | 0 | if/try 재귀 확인 |
| c | 로컬 중간 base `class _Base(StrEnum)` → `class X(_Base)` | 1 | 1 | 비범위(계획 명시) — 그대로 red |
| d | 교차 모듈 중간 base | 1 | 1 | 비범위 — 그대로 red |
| e / e2 | `@_dataclass` alias + `self.total =` / plain `@dataclass` 동형 | 1 / 0 | 1 / 0 | **데코레이터 alias는 미해소**(계획 «Name base 1축» 그대로) |
| h | `from …x import fake as enum` → `class X(enum.StrEnum)` | 0 | 0 | receiver 무검사(계획 병기) |
| i | `import enum as e` → `class X(e.StrEnum)` | 0 | 0 | 현행도 attr 매치 |
| (참고) 사이비 리뷰어 `fx/public_surface` | good 3 red / bad 7 | good 0 / bad 8 | 계획 §2.4 기대와 일치 |

**판정: 무손실 검증됨** — 오탐 소거(a·f·g·k)·미탐 폐쇄(b) 밖의 변화 0(라이브 2저장소·픽스처 byte 동일·c/d/e/h/i 불변). 진탐 감소 경로 없음. exit·규칙 번호·메시지 불변.

## 3. Part 1 — R-3442 소급 red 규모 · 형상 · 효과 (Q3)

### 3.1 mypy가 실제로 찍는 형상 (`rv3/forms.py` · 필드 `n: int`·`s: float`·`t: str` · strict+warn_unreachable+redundant-expr)

| 형상 | mypy | #69 후보(isinstance만) |
|---|---|---|
| `not isinstance(x, int) or …` / `not isinstance(s, float) or …` | **redundant-expr** | ⓓ |
| `isinstance(n, bool) or n < 1`(bool 구멍) · `isinstance(n, bool)` 단독 | 침묵 | ⓓ |
| `type(n) is bool`(계획 예제 형) · `type(s) is not float or …` · `type(n) is not int or …`(kkebi 지배 형) · `type(t) is not str` raise-only | 침묵 | **무발화** |
| `not isinstance(t, str): raise` raise-only · `not isinstance(s, float): raise` | 침묵 | ⓓ |

→ 현장 보고를 낳은 형상은 **or-체인 isinstance 1종**(+비-raise 본문의 unreachable)뿐. R-3442 문면(«선언 타입의 재검사·강제 변환은 두지 않는다»)은 형상 무관이라 **규범 범위 ≫ mypy 발화 범위**이고, 그 초과분 대부분(`type() is` 형)은 **#69도 못 본다**.

### 3.2 소급 red 규모 (`rv3/vo_recheck.py` · `application/**/domain_layer/**` 비테스트 · 선언 필드/매개변수 vs 검사 타입 대조 · Optional 좁히기·`object` 매개변수는 제외)

| 저장소 | 도메인 파일 | **위반 파일(VO)** | 위반 행 | OR_CHAIN | RAISE_ONLY | WIDEN(`x: object = self.x`) | IGNORE | NONRAISE | COERCE | 형상 split | BC 분포 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| spring_dream | 643 | **19 (18)** | 23 | 12 | 1 | 4 | 3 | 0 | 0 | `type() is` 14 · isinstance 9 | wallet 7·product 4·promotion 3·fortune_character 3·fortune_record 1·chat_relay 1 |
| kkebi | 880 | **75 (62)** | **207** | 48 | 34 | 13 | 0 | 1 | 1 | **`type() is` 139** · isinstance 67 · coerce 1 | daily 45·billing 16·saju 12·top3 1·product_observability 1 |
| 허용(참고) | — | HOLE_BOOL spring 4/kkebi 1 · HOLE_FLOAT spring 3 · OBJ_PARAM 2/3 · NARROW 0/4 | — | — | — | — | — | — | — | — | — |

- 현재 spring WT 기준 mypy 발화 0인데도 R-3442로는 19파일(6 BC·claude/codex 혼재)이 즉시 위반이다 — 발주측이 방금 한 정리조차 `not isinstance(x, float)` → **`type(x) is not float`**(mypy 침묵·R-3442 «int→float 거부 = 값 검사»로 허용)로 바꾼 것이지 재검사를 없앤 것이 아니다.
- kkebi 75파일/207행은 전부 typed 호출자(`reconstitute(last_sequence: int …)`·유스케이스)에서만 불리는 **죽은 재검사 + 확장 우회**(`daily_compatibility.py:83-96` 5필드 object 확장 뒤 isinstance) — 품질상 제거가 옳고(#69·cleancode §12.7과 동방향) 잡음이 아니다. 그러나 **관찰 모드 없는 Obligation**이라 discipline-reviewer가 손대지 않은 VO에도 즉시 위반을 낼 수 있는데, 계획은 brownfield 처분(«손대는 파일만» 등)을 적지 않았다.
- **(a)** 새 예제·문면은 or-체인/비-raise 형상에만 맞춘 것은 아니다(형상 무관 원칙) — 그래서 오히려 kkebi raise-only 34파일·확장 우회 13파일 전부가 위반이 된다. **(b)** 소급은 정당(죽은 코드)하나 규모가 크고 G2 검사기가 아니라 리뷰어 재량에 맡겨져 레인마다 갈릴 위험 — 처분 문면 필수. **(c)** 효과 수치: 루브릭 «19/171(11%)»는 A 13에 비-VO `service_runtime` 2를 포함(R-3442 적용 밖) → **17/171**, 그중 C 6은 검사기 수리가 아니라 발주측 alias 제거로 사라짐(이미 소멸) → Part 1 귀속 가능 = **11/171(6%)**. 현재 트리에서 A·C 잔존 **0**이므로 «이번 정리 노동 절감»은 0, 효과는 전적으로 예방(레인당 ≈0.5건·1~3분 상한은 과장 아님·하한 0).

### 3.3 예제 실측
- 원문(final.md 486~544 verbatim): full 플래그 → `unreachable`:17 + `no-untyped-def`:56 = 2건. **계획 교체본**(b4 교체 + PhoneNumber `-> None`): full **0건** · plain strict **0건**(계획 §1.3 검증됨). 검사기: #69 후보 **0**(`type() is bool` 무발화 — 계획 근거 검증됨).
- 그러나 같은 graph-owned 블록 `Money.subtract`의 `result = self.amount - other.amount`(final.md:515 부근)가 **#493 지역 변수 위반** — 계획이 PhoneNumber `-> None`을 «하우스룰 §4 자기 위반 해소»로 동승시키면서 같은 블록의 두 번째 자기 위반은 남긴다(MINOR — 일관성).
- wiring `enforcedBy → check-public-surface-annotation.py #69`: #69는 exit 불산입 후보이며 isinstance 형만 본다 — R-3442 위반의 지배 형(`type() is`, kkebi 139/207행)과 계획 예제가 권하는 허용 형(`type() is bool`) 모두에 무감각 → 집행선으로는 **명목**. `delegatedTo discipline-reviewer`가 실질이며 enforcedBy를 걸면 rulepack이 «검사기가 지킨다»고 거짓 선언한다.

## 4. 과거 사건 표 (Q4 — 전수: 런 폴더 `.dddjango/*/` + spring `docs/superpowers/orders/lane/STOP-*.md`)

런 폴더 키워드 실측: `_StrEnum`·`redundant-expr`·`Enum members` **양 저장소 0건**, `#493` spring 57파일/16619행·kkebi 110파일(백스톱 스캔 덤프 — 노이즈). 사건 기록은 **spring 레인 STOP 문서**에만 있다(런 폴더만 뒤지면 «0건»으로 오판).

| # | 저장소·레인·날짜·런타임 | 사각 facet | 발화 | 처분 | 우회 흔적 |
|---|---|---|---|---|---|
| 1 | spring accounts 08-30 claude · `STOP-custom-user-annotation-gap.md` | **base 이름 집합 결손**(`AbstractBaseUser`·`PermissionsMixin`) | #493 ×11 | ⓐ 승인 빚 + 플러그인 A2 수정(`b9252e9` 09-01 이름 3개 추가) | 주석 부착 시 필드 타입 `Any` 붕괴 실측 → 부착 거부 |
| 2 | spring promotion 08-31 codex · `STOP-promotion-g2-checker-contract-conflicts.md` | **외부 라이브러리 중간 base** `CampaignForm(parler.TranslatableModelForm)` | #493 ×1 | 레인이 `target_product_ids: forms.CharField = forms.CharField(...)` **주석 부착으로 우회** | 현존(`campaign_form.py:90`) — **전이 면제 사각의 실발화 선례** |
| 3 | spring fortune_reading 09-01 codex 2.17.12 · `STOP-fortune-reading-strenum-registry-alias.md` | **import alias** `_StrEnum` | #493 ×8(3파일) | 발주자 C = plain `StrEnum` 복귀(«checker는 저장소 표준과 일치 — 정정 대상 아님») | WIP 2파일(`8216c78`) 누락 → 주석 부착 잔재 → mypy `[misc]` 6 → **09-03 17:37 WT에서 발주측 정리(미커밋)** |
| 4 | spring fortune_reading 09-01→09-03 codex(P1~P4) | 같은 레인 `_Schema`·`_BaseModel`·`_dataclass`(54)·`_Literal` 등 alias 스타일 지속 | 0(필드 전부 AnnAssign) | 없음 | 잠재 — `_dataclass` + `self.x =`면 재발(§2 e) |
| 5 | spring fortune_reading 09-02 codex 2.17.14 · `STOP-…-p3-discipline-first-assignment-annotations.md` | #493 테스트 지역 변수(alias 무관) | 2 | 결정 A | `EvidenceSet as _EvidenceSet` private import 관용구 STOP-C 뒤에도 유지 |
| 6 | spring fortune_reading P1 · `STOP-fortune-reading-p1-tree-contract.md:52` | `NonEmptyString` 첫 대입 #493(별칭/타입 alias facet 추정 — 형상 미검증) | 1 | 미진행 | — |
| 7 | kkebi saju-chart-engine 08-24 · design-spec Z-8/Z-8A · `implementation-review-discipline-s2.md` I-2 | #493 **TypeAlias 첫 대입**(`Power = dict[str, float]`) ↔ Ruff UP040 충돌 | 2 | 사용자 override: `TypeAlias` 주석 + `# noqa: UP040` | 현존 |
| 8 | kkebi billing-migration 08-23 · `review-s3-discipline.md:36` | #493 테스트 지역 — 리뷰어가 «enum member … finding 제외» 명시 | 3 | 반송 | 규범 인지 정상 |
| A-facet(참고) | spring fortune_character 08-30 claude | `# type: ignore[redundant-expr]` 3 VO | — | 레인 억제 | 현존 3파일/5행 · kkebi 1 |

- «1레인 단발»: **alias facet만 참**(사건 3·4 = 한 레인). **base 이름 문자열 비교 family로 보면 3일 연속 3레인·양 런타임**(1→2→3: 결손 이름·중간 base·alias) — 계획 §2.6이 «다른 검사기의 같은 판형»은 등재하면서 **같은 검사기의 남은 facet(중간 base·데코레이터 alias)**는 docstring 병기로 끝낸다. 사건 2가 선례이므로 최소 로드맵 R-15에 «check-public-surface-annotation 중간 base(로컬 C1 22/89·외부 라이브러리)» 항목과 promotion 선례를 적어야 한다(로컬 C1은 같은 모듈 ClassDef 표를 한 번 더 보면 닫힌다 — 비용 10줄·오차단 위험 0).
- 다른 레인의 alias 회피 흔적: 없음(kkebi alias 0·spring 다른 BC 0) — 반대로 사건 2처럼 **주석 부착 우회**가 남는다.

## 5. 심각도 총괄 · 계획 수정 요구

| 항목 | 판정 | 근거·요구 |
|---|---|---|
| Part 2 무손실(검출 집합 단조·게이트 강도·오차단 0) | **검증됨** | 라이브 2저장소 3스냅숏 차분 0 · 픽스처 byte 동일 · 스크래치 a/f/g/k(오탐→0)·b(미탐→1)·c/d/e/h/i 불변 |
| Part 2 «alias 사각 = 1레인 단발» | **검증됨(조건부)** | facet 기준 참. family 기준 3레인 — 서술을 «alias facet 1레인·base 판정 family 3레인(사건 1·2·3)»으로 정정 |
| Part 2 §2.4 `fixture_matrix.py:111 ("bad_rules", 2) → 3` | **MAJOR** | 그 `2`는 **기대 exit 코드**(`for sub, want in (("good", 0), ("bad_rules", 2))`) — 3으로 바꾸면 매트릭스 red. 계수 골든은 `workspace/tools/checker_baseline_matrix.py:252` `(2, 11, 11, 4, False)` → parsed/normalized **12** 와 `findings_count_matrix.py:130` `#493×7`→`×8` + sha 3열 재실측. `construct_drift_report.py` EXPECTED_SHA에는 public-surface 없음(무접촉). fixture_matrix는 `good` exit 0 / `bad_rules` exit 2 그대로 |
| Part 2 «실코드 전/후 대조» 증거 설계 | **MINOR** | HEAD 2파일은 주석 부착이라 전/후 모두 0, WT는 이미 plain — 증거는 `git show HEAD:` 사본의 **주석 제거본**(orig 6 → patched 0)으로 만들고 회신에 «잔재 2파일은 09-03 WT에서 발주측 정리됨(미커밋)» 반영 |
| Part 2 전이 면제·데코레이터 alias 비범위 | **MAJOR(로드맵 누락)** | 중간 base는 잠재 일반(C1/C2 spring 27·kkebi 99) + **promotion 08-31 실발화 선례**(외부 라이브러리 base) · `_dataclass` alias 64클래스 같은 레인. 요구: §2.6에 같은 검사기 facet 2건을 선례와 함께 등재(또는 로컬 C1만 이번에 동승 — 10줄·오차단 0) |
| Part 1 예제·원칙 플래그 무관 | **검증됨** | 교체본 full/plain 0건 · #69 후보 0 · 코퍼스 동방향(rv1 A·B) |
| Part 1 R-3442 소급 red | **MAJOR** | spring 19파일(6 BC)·kkebi **75파일/207행**(5 BC·≥5레인)이 즉시 위반 — 그중 `type() is` 형 153행은 mypy·#69 모두 침묵. 품질상 정당(죽은 재검사)하나 관찰 모드 없음. 요구: 문면에 brownfield 처분 1문장(예: «기존 값 객체는 손대는 파일에서만 정리 — 하우스룰 이관 원칙 준용») + 구멍 검사 허용 형(`type(x) is bool` · int→float 거부)을 명시한 그대로 유지 |
| Part 1 wiring `enforcedBy #69` | **MAJOR** | #69는 후보·isinstance 한정 — 지배 형 무감각·예제 권장 형도 무감각. 요구: `delegatedTo discipline-reviewer`만(구조 검사가 허용하면) · enforcedBy는 걸지 않는다 |
| Part 1 같은 블록 `result` 지역 변수 #493 | **MINOR** | PhoneNumber `-> None`만 동승하면 자기 위반 1건 잔존 — `result: int = …` 동승(본문 의미 불변) |
| 효과 수치 | **MINOR(과대)** | 19/171 → 17(비-VO 2 제외) → Part 1 귀속 11/171(6%) · C 6은 검사기 수리 아닌 발주측 정리로 소멸 · 현재 WT A/C 0·총 122 → 이번 노동 절감 0, 예방 효과만. 회신 문면 정정 |
| Part 2 «호출처 1곳 전달» | MINOR(표현) | `_scan_stmts`가 재귀라 bindings 매개변수 관통 필요(패치 137행 중 대부분이 관통) — 구현 지시를 «스코프 재귀 관통»으로 |

## 10줄 요약

1. Part 2 무손실 **검증됨**: 계획 §2.2를 독립 구현(`rv3/patch.diff` 137행)해 spring_dream(3226/3225 · 스냅숏 2회)·kkebi(173) 전 트리 전/후 차분 **0행**, 픽스처 good/bad_rules **byte 동일**, 스크래치 형상 a/f/g/k 오탐→0·b 미탐→1·c/d/e/h/i 불변 — 검출 감소 경로 없음.
2. 형상 계수: 선언 base alias는 **spring 5파일/22클래스·kkebi 0** — 전부 fortune_reading 레인(codex 09-01→09-03, `_dataclass` 54파일 포함 alias import 35줄의 «레인 스타일»). 전이 면제(중간 base)는 **spring 27·kkebi 99 클래스**(모든 BC의 `bc_error_schema.py`)로 잠재 일반, 현재 발화 0.
3. «1레인 단발»은 alias facet에 한해 참. base 문자열 비교 **family**로는 08-30 accounts(이름 결손 11건·플러그인 수정) → 08-31 promotion(`TranslatableModelForm` 중간 base 1건 · 주석 부착 우회 현존) → 09-01 fortune_reading(alias 8건 · STOP-C) 3일 3레인·양 런타임 — 계획 §2.6은 같은 검사기의 남은 facet(중간 base·데코레이터 alias)을 로드맵에서 빠뜨림(**MAJOR**).
4. 런 폴더 `.dddjango/*/`에는 `_StrEnum`·`redundant-expr`·`Enum members` **0건** — 사건은 spring `docs/superpowers/orders/lane/STOP-*.md`에만 있다. 다른 레인의 alias 회피 흔적 없음(kkebi alias 0).
5. **MAJOR**: 계획 §2.4 `fixture_matrix.py:111 ("bad_rules", 2)→3`은 exit 코드 오독(바꾸면 red). 실제 갱신 지점은 `checker_baseline_matrix.py:252 (2,11,11,4,False)`→12·`findings_count_matrix.py:130 #493×7`→×8+sha; construct_drift 무접촉.
6. 라이브 «오탐이던 실코드»는 없다: HEAD 2파일은 주석 부착이라 전/후 0, WT는 17:37에 발주측이 plain `StrEnum`으로 정리(미커밋). 증거는 HEAD 사본 주석 제거본(orig 6→patched 0)으로 만들어야 한다(MINOR).
7. Part 1 예제 교체본 mypy full/plain **0건**·#69 후보 0(검증됨). 단 같은 블록 `subtract`의 `result` 지역 변수가 #493 자기 위반으로 잔존(MINOR).
8. **MAJOR**: R-3442는 형상 무관이라 mypy 발화(or-체인 isinstance 1종)보다 훨씬 넓다 — 즉시 위반 spring 19파일(6 BC)·kkebi **75파일/207행**(daily 45·billing 16·saju 12), 그중 `type() is` 형 153행은 mypy·#69 모두 침묵. 죽은 재검사라 소급은 정당하나 관찰 모드 없음 → brownfield 처분 1문장 필수.
9. **MAJOR**: wiring `enforcedBy #69`는 명목(후보·isinstance 한정·지배 형과 권장 형 모두 무감각) → `delegatedTo discipline-reviewer`만.
10. 효과: 현재 spring WT mypy **122건·redundant-expr 0·Enum members 0**(171→122는 발주측 정리) — 이번 노동 절감 0, 예방만. 루브릭 19/171은 비-VO 2 포함·C 6은 검사기 수리와 무관 → Part 1 귀속 11/171(6%)(MINOR 과대). BLOCKER 없음 · MAJOR 4 · MINOR 4.
