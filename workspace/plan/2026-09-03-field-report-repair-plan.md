# 현장 보고(typecheck) 수리 계획 v1 — 2부 구성 (2026-09-03 · ③ 적대 리뷰 전)

- 지위: 루브릭 `2026-09-03-field-report-repair-rubric.md` ① 결과의 사용자 결정(범위 = A 규범 예제 + C′ 검사기 alias 사각 · 제안 3 제외 · 제안 4 기각 · B 발주측)을 집행하는 계획 v1. ③ 적대 리뷰(3축) 후 «문면 확정» 게이트.
- 공통 비범위: 다른 검사기의 base 이름 문자열 비교(§2-4 조사 목록)는 등재만 · 값 객체 예제 밖의 코퍼스 예제 strict-clean 화(4/28·12/78)는 범위 밖 · 테스트 규율(제안 3) 범위 밖 · Coordinator/agents 문면 무변경.
- 릴리즈: 실행기(`design_pregate.py`)·registry 판정 무접촉 → 카탈로그 재실측 무오염. 검사기 #493 변경은 registry 27종 중 1종의 **오탐 소거·미탐 1형 폐쇄**(§2-3 무손실 증명)라 G2 강도 불변. 릴리즈 시점은 ⑥ 뒤 사용자 결정.

---

# Part 1 — A: 값 객체 예제 교체 + 경계 원칙 성문

## 1.1 정본·소유
- 코드 블록: `ontology/rules/architecture-ddd-final.ttl` `s016-3.1/b4`(kind-code · 규범 IRI 없음 · 리터럴 교체 = 리비전 번호 없음) — 렌더 `dddjango/skills/architecture-ddd/references/final.md` 490~548행(graph-owned 473~548).
- 원칙 문장: `s016-3.1/b3`(kind-norm · statesNorm R-0494·R-0495·R-0496 «핵심 원칙» 목록)에 불릿 1개 추가 + **신규 채번 R-3442**(Obligation). 대안(③에서 판정): 채번 없이 b4 코드 블록 docstring 문장만(코퍼스 비용 0·집행선 없음).
- 다른 정본에 같은 관용구 없음(리뷰 B 전수 — 유일 1곳). `s016-3.1` 밖 `Money` 예제(:2608 s0xx — add만)는 무관.

## 1.2 문면 초안

### b4 코드 블록(교체 — 변경 지점만)
```python
    def __post_init__(self) -> None:
        """자기 검증 (Self-Validation): 값의 불변식만 강제한다 — 타입은 시그니처가 약속하고 타입 체커가 지킨다"""
        if type(self.amount) is bool:  # bool 은 int 의 하위 타입이라 타입 체커가 통과시킨다 — 값 검사에 속한다
            raise ValueError(f"금액은 정수여야 합니다: {self.amount!r}")
        if self.amount < 0:
            raise ValueError(f"금액은 0 이상이어야 합니다: {self.amount}")
        if not self.currency:
            raise ValueError("통화 코드는 필수입니다")
```
- 삭제: `if not isinstance(self.amount, int): object.__setattr__(self, "amount", int(self.amount))` 2행(죽은 분기 + 값 훼손 coercion).
- `PhoneNumber.__post_init__(self)` → `__post_init__(self) -> None`(하우스룰 §4 자기 위반 해소 · 본문 불변).
- 나머지(add/subtract/multiply/_ensure_same_currency/Address) 불변. 플래그명(redundant-expr 등) 미기재(리뷰 B MINOR).

### b3 «핵심 원칙» 불릿 추가(R-3442 신설 · Obligation)
> - 자기 검증은 **값의 불변식만** 검사한다 — 선언 타입의 재검사·강제 변환은 두지 않는다(타입은 시그니처가 약속하고 타입 체커가 지킨다). 타입 체커가 통과시키는 값(`bool`⊂`int`·`int`→`float`)의 거부는 값 검사에 속한다. `object`/`Any`/JSON 입력의 타입 좁히기는 값 객체를 부르기 **전**에 경계(역직렬화·스냅숏 복원·폼 `cleaned_data`)가 담당한다.

- prefLabel: «값 객체 자기 검증은 값 불변식만 — 타입 좁히기는 경계 소유»@ko · revisionKind n/a(신설 rev 1) · ISSUED append `R-3442	2026-09-03	rules/architecture-ddd-final.ttl`.
- wiring: `enforcedBy` → `check-public-surface-annotation.py` #69(ⓓ 후보 — isinstance 가드 뒤 TypeError/ValueError) · `delegatedTo` → discipline-reviewer(의미 변종). 무소유 Norm은 구조 검사 red이므로 둘 중 하나 필수.

## 1.3 검증(무손실·정합)
- 새 예제 mypy 2.3.1 `--strict --warn-unreachable --enable-error-code redundant-expr` 0건 + plain `--strict` 0건(스크래치 실측 · 리뷰 A 기실측 재현).
- 코퍼스 정합: cleancode §12.7(경계 검증)·implementation-python §12(coercion)·R-3158·검사기 #69 문면과 동방향 확인(리뷰 B). #69는 raise-only `isinstance` 가드를 ⓓ 후보로 내므로 새 예제의 `type(x) is bool` 가드는 #69 무발화(리뷰 B MINOR 근거) — 픽스처로 확인.
- 3축: 정합(건드리는 IRI = b3·b4·R-3442·wiring 1~2 · 렌더 md 1 · rulepack · LEDGER s016-3.1 행 · 소스 미러 1 · codex byte 미러 1) · 일반화(플래그 무관 원칙·양 런타임 byte 동일 final.md) · 무손실(검사기 무변경 — 검출 집합 불변).

## 1.4 절차(리비전 레시피)
rdflib 편집+canon 재직렬화(왕복 byte 동일 선확인) → `ontology_gate.py` green → `ontology_render.py --apply architecture-ddd-final` → LEDGER 재기준선(s016-3.1) → 계수표(NormShape +1·ExpressionShape +1)·q4 골든 → `make rulepack` → 소스 미러 절 수동 교체 + `corpus_mirror_sync --write`(11/11) → codex byte 미러 → `make verify`.

---

# Part 2 — C′: 검사기 #493 선언적 base 판정의 import alias 사각 폐쇄

## 2.1 원인(코드 지점)
`dddjango/scripts/check-public-surface-annotation.py:127-143` — `_name_of(b)`(Name.id 또는 Attribute.attr)를 `DECLARATIVE_BASE_NAMES`와 **문자열 비교**. `from enum import StrEnum as _StrEnum` → `_StrEnum` ∉ 집합 → 비선언적 판정 → 무주석 멤버 `#493` blocker(**오탐**). 역방향: `from x import Foo as StrEnum` → 이름만 일치해 면제(**미탐 1형**). 같은 저장소의 `check-context-isolation.py:_enum_local_names`는 import 바인딩(asname→원명)으로 해소하는 판형을 이미 갖고 있다 — 같은 판형을 쓴다(검사기 간 일관).

## 2.2 변경(함수 단위 · 판정 로직 국한)
- 신설 `_import_bindings(mod) -> dict[str, str]`: 모듈 본문(제어 블록 안 포함 — `ast.walk` 아닌 본문 순회 + if/try 하위 문 재귀)의 `ImportFrom`(`asname or name` → `name`)·`Import`(`asname or top` → `name`) 바인딩.
- `_is_declarative_class(cls, bindings)`: base가 `ast.Name`이면 `bindings.get(id, id)`(import 바인딩이면 **원명**, 로컬 정의면 그대로) · `ast.Attribute`면 현행대로 `attr`(receiver 무검사 — 라이브러리 모듈 목록을 닫지 않는다 · 사각 병기). 그 뒤 `∩ DECLARATIVE_BASE_NAMES`.
- 호출처 1곳(클래스 본문 스캔 진입)에 bindings 전달. 다른 판정(#69·#358·#456·시그니처·지역·속성) 무접촉.
- docstring 사각 추기: «로컬 중간 base(`class _Base(StrEnum)` → `class X(_Base)`)의 전이 면제는 하지 않는다(기존과 동일) · Attribute base는 receiver 무검사».

## 2.3 무손실 증명
- 검출 집합 단조성: 변경은 «Name base의 정규화» 1축뿐. (i) alias 없는 코드 → `bindings.get(id, id) == id` → 판정 동일(byte 동일 출력 — 픽스처 `good`·`bad_rules` 기존 계수 불변) (ii) alias로 들여온 선언적 base → 면제 추가(오탐 소거·규범 R-3154 «enum 멤버 무주석»과 정합) (iii) 비선언 클래스를 선언적 이름으로 별칭 → 면제 해제(미탐 폐쇄 — 검출 증가). 진짜 검출 감소 경로 없음.
- 게이트 강도: exit 의미·규칙 번호·메시지 불변. 다른 검사기 무접촉.
- 오차단 0: 선언적 base를 alias로 들여온 실코드가 오탐이던 것이 green이 되는 것뿐(reading `_StrEnum` 2파일 형상 — 스크래치 재현으로 전/후 대조).

## 2.4 픽스처·하네스
- `workspace/eval/fixtures/public_surface/good/…/domain_layer/shared_value_object/book_usage_policy.py`: `from enum import StrEnum as _StrEnum` + 무주석 멤버 → 기대 0(수리 전 red = 결함 재현 증거).
- `…/bad_rules/…/aliased_shadow.py`: `from application.orders.domain_layer.x import Plain as StrEnum` + 무주석 클래스 변수 → 기대 #493 1건(미탐 폐쇄 증거). `fixture_matrix.py:111` `("bad_rules", 2)` → 3으로 갱신.
- `findings_count_matrix`·`construct_drift` EXPECTED: 검사기 출력이 census 대상에서 바뀌면 재실측(alias 형상이 census에 없으면 불변 — 실측으로 확정).
- codex byte 미러 `codex-dddjango/skills/dddjango/scripts/check-public-surface-annotation.py` rsync → `manifest_seal` draft → `make verify`.

## 2.5 규범 문면
- 규범 변경 0(R-3154 «문법 없는 자리 — enum 멤버» 그대로). 검사기 docstring 1행(사각 병기)만. Coordinator :133 문면 불변.

## 2.6 조사(등재만 — 비범위)
같은 문자열 비교 판형: `check-context-isolation.py:615` · `check-db-table.py:180` · `check-domain-model.py:846` · `check-port-adapter-pairing.py:137` · `check-usecase-dto-placement.py:171`(`check-error-centralization.py:2101`·`check-api-error-controller-contract.py:2147`은 이미 바인딩 해소). 로드맵 후보 R-15로 등재 — 발화 관측 시 같은 판형으로 수리.

---

# 통합·순서·검증 게이트
1. 브랜치 `fix/field-typecheck` — 커밋 ① Part 2 검사기+픽스처(수리 전 red 증명은 별도 커밋 대신 증거 폴더 `evidence-alias-*`의 orig 출력으로 보존 — ⑥ 감사 주석) ② Part 1 그래프 리비전+렌더+rulepack+LEDGER ③ 미러(소스·codex) ④ 계수표·골든·봉인 draft.
2. `make verify` 6/6 green · 새 예제 mypy 0건 · 픽스처 매트릭스 green · 수리 전/후 census EXPECTED 대조.
3. ⑤ 구현 적대 리뷰 → ⑥ 감사·재검 → 릴리즈 브리프(즉시 v2.17.17 / 승격 배치 동승).
4. 현장 보고 회신 `2026-09-03-field-report-reply.md`: A 처분·C 정정(R-3154 기성문·alias 사각 수리·잔재 2파일은 발주측 정리)·B 처분(발주측 훅·체크리스트)·제안 3·4 처분.

---

# v2 반영 델타 — ③ 계획 적대 리뷰 3기(A 기술·B 규범·C 증거) 전건 반영 (2026-09-03 · 산출 `workspace/eval/field-report-typecheck/rv3/`)

리뷰 결과: BLOCKER 0 · MAJOR 7(5계열) · MINOR 12. 방향 변경 없음 — 아래 델타가 v1 본문에 우선한다(충돌 시 델타가 정본).

## Part 1 델타
- **D1-1 문면 모순(MAJOR·A/B 일치)**: «int→float 거부는 값 검사» 삭제(PEP 484 수치 탑 — `float` 시그니처는 int 수용을 약속). 값 검사로 남는 것은 «타입 체커가 통과시키는 값의 거부»이며 예시는 `bool`⊂`int`뿐. 반대로 «시그니처가 수용을 약속한 값은 거부하지 않는다»를 명시.
- **D1-2 채번 분할(B 정합)**: b3 선례(«불변 (setter 금지)» → R-0495 Obligation + R-0496 Prohibition)대로 **R-3442 Obligation**(자기 검증은 값의 불변식만) + **R-3443 Prohibition**(타입 체커가 이미 거부하는 입력의 재검사·강제 변환 금지 + 좁히기는 경계 소유). docstring-only 대안은 R-3156(코드 예시는 적용 대상 밖)에 의해 비규범 → 기각 확정.
- **D1-3 brownfield 처분(MAJOR·C)**: R-3442/3443은 형상 무관이라 즉시 위반이 spring 19파일·kkebi 75파일/207행(그중 `type() is` 형 153행은 mypy·#69 침묵). 규범에는 관찰 모드가 없으므로 적용 대상을 **«이번 작업이 새로 쓰거나 손대는 값 객체»**로 성문(기존 코드는 소급 대상 아님 — 손대는 슬라이스에서 제거·G0 빚 스캔 대상 아님(검사기 밖)). 코퍼스 선례: 앵커 차분·R-3156.
- **D1-4 wiring(MAJOR·C / A·B 조정)**: `enforcedBy #69`는 명목(ⓓ 후보·isinstance 한정·지배 형 `type() is`와 권장 형 모두 무감각) → **`delegatedTo discipline-reviewer`만**(무소유 red 회피 충족 — shapes sh:or). 문면에 «#69 ⓓ 후보는 관련 신호일 뿐 집행선이 아니다» 검수표 기록.
- **D1-5 예제 동승(MAJOR·A / MINOR·C)**: 같은 블록 `subtract()`의 `result = self.amount - other.amount` → `result: int = …`(하우스룰 §4 자기 위반·레인이 베끼면 blocker). PhoneNumber `-> None`은 유지, 함수 안 `import re`는 코퍼스·양 저장소 ruff 무충돌이라 유지.
- **D1-6 어휘(MINOR·B)**: «테스트·타입 체커»(#69 문면과 정렬) · «스냅숏 복원»→«Data Mapper 복원·요청 Schema·폼 `cleaned_data`».
- **D1-7 계수·산출 누락(B)**: target-counts NormShape **+2**·WorkShape **+2**·ExpressionShape **+2** · q4 골든 distinct_works 3441→3443 · ISSUED 2행 · LEDGER s016-3.1 append와 소스 미러 span 교체를 **같은 단계**(어긋나면 corpus_mirror_sync exit 3) · 봉인 draft(통합 ④ 1회) · 검수표 기록 위치 = 이 계획서 말미 «검수표» 절 · `ontology-adoption-map.html` 갱신(사용자 상시 지침).

### 확정 대상 문면 (b3 «핵심 원칙» 불릿 2개 — 사용자 «문면 확정» 게이트 입력)
> - 값 객체의 자기 검증은 **값의 불변식만** 검사한다(R-3442). 타입 체커가 통과시키는 값의 거부는 값 검사에 속하며 `type(x) is T` 형으로 쓴다(예: `bool`⊂`int`). 시그니처가 수용을 약속한 값(예: `float` 자리의 `int`)은 거부하지 않는다. 적용 대상은 이번 작업이 새로 쓰거나 손대는 값 객체다 — 기존 코드는 소급 대상이 아니며 손대는 슬라이스에서 제거한다.
> - 선언 타입을 값 객체 안에서 **재검사하거나 강제 변환하지 않는다**(R-3443) — 타입은 시그니처가 약속하고 테스트·타입 체커가 지킨다. `object`/`Any`/JSON 입력의 타입 좁히기는 값 객체를 부르기 **전**에 경계(Data Mapper 복원·요청 Schema·폼 `cleaned_data`)가 담당한다.

### 확정 대상 예제 diff (b4 코드 블록 — 변경 지점만)
```
-        """자기 검증 (Self-Validation): 생성 시점에 불변식 강제"""
-        if not isinstance(self.amount, int):
-            object.__setattr__(self, "amount", int(self.amount))
+        """자기 검증 (Self-Validation): 값의 불변식만 — 타입은 시그니처가 약속하고 테스트·타입 체커가 지킨다"""
+        if type(self.amount) is bool:  # bool 은 int 의 하위 타입이라 타입 체커가 통과시킨다 — 값 검사에 속한다
+            raise ValueError(f"금액은 정수여야 합니다: {self.amount!r}")
         if self.amount < 0:
 ...
-        result = self.amount - other.amount
+        result: int = self.amount - other.amount
 ...
-    def __post_init__(self):
+    def __post_init__(self) -> None:
```
- 실측(A·C 독립): 교체본 mypy strict+warn_unreachable+redundant-expr **0** · plain strict **0**(원본 unreachable 1 + no-untyped-def 1) · `type(x) is bool` ⓓ#69 **0**.

## Part 2 델타
- **D2-1 하네스 오독(MAJOR·A/B/C 일치)**: `fixture_matrix.py:111`의 2는 **기대 exit 코드** — 무변경. 실제 갱신: `findings_count_matrix.py:130` EXPECTED(#493×7→×8 + sha 3) · `checker_baseline_matrix.py:252` `(2,11,11,4,False)`→12 · `checker_cross_matrix` 무변(census는 비-0 exit만 기록 — ⑤ 정정) · `construct_drift` 무접촉(실측).
- **D2-2 bad 픽스처 형상(MAJOR·A)**: 타 모듈 import는 #298·#488(신설 폴더 `__init__.py` 부재)을 함께 울림 → **같은 폴더 import + `__init__.py`×2**. 잔여 = domain-model ⓓ#268 info 1(실측·무해).
- **D2-3 helper 판형·범위(A 권고 채택)**: 선례 인용을 `check-error-centralization._module_bindings`로 정정(context-isolation은 모듈 한정 판형). 신설 `_module_bindings(mod)`: 모듈 수준 `Import`/`ImportFrom` 바인딩(asname→원명) + **그림자 pop**(import 뒤 같은 이름의 모듈 수준 ClassDef/FunctionDef/Assign 재바인딩 시 바인딩 제거 — 반례 a21 폐쇄 3줄). 적용 대상 = **base(Name) + 데코레이터(Name·Call.func Name)** — `@_dataclass` 별칭(spring 54파일)이 같은 사각이라 같은 helper로 폐쇄. Attribute는 현행(attr 매치·receiver 무검사).
- **D2-4 무손실 문면 정정(A)**: «진짜 검출 감소 경로 없음» → «1형 존재 — 동명 비선언 클래스의 별칭 import(기존 동명 사각의 확장·양 저장소 실측 0)». 정당 중간 base 별칭(a09)은 green→red 전환이 아니라 **불변**(전이 면제 비범위 유지).
- **D2-5 증거 아티팩트(MINOR·C)**: 라이브 HEAD 2파일은 주석형이라 현행도 미검출·WT는 발주측이 17:37 plain StrEnum으로 정리(미커밋) → 오탐 재현 증거는 **HEAD 사본의 주석 제거본**(orig 6 → patched 0)을 `workspace/eval/field-report-typecheck/`에 보관. 실측(A·C 독립 구현 2종): spring 3310/3226 · kkebi 345/173 전 트리 전/후 차분 **0** · 픽스처 byte 동일.
- **D2-6 docstring 문구(B)**: «면제 규칙»이 아니라 «검출 한계(오탐 가능 형상)»로: 로컬 중간 base 전이 면제 없음 · Attribute receiver 무검사 · 동명 비선언 별칭.
- **D2-7 로드맵 등재(MAJOR·C — §2.6 보강)**: 같은 검사기의 남은 facet **중간 base 전이 면제**(spring 27·kkebi 99 클래스 — 전 BC `bc_error_schema.py` · 08-31 promotion `TranslatableModelForm` 주석 우회 현존 · 현재 발화 0) → R-15b 등재. base 문자열 비교 family는 3일 3레인·양 런타임(08-30 accounts → 08-31 promotion → 09-01 reading) — «단발» 서술은 alias facet 한정으로 정정. 다른 검사기 5종 = R-15a. 파싱 실패 파일의 조용한 green(`check-public-surface-annotation.py:413-416`) = R-16 후보(A 관찰).

## 효과 서술 정정(C)
- 현재 spring WT mypy 122(171→122는 발주측 정리)·redundant-expr 0·Enum members 0 → 이번 배치의 노동 절감 **0**, 가치는 **예방**(Part 1 귀속 11/171 = 6% · Part 2는 무주석 alias 형상 재발 예방 — 픽스처가 유일 증거). 과대 서술 금지.

## 검수표(④·⑤ 기록 자리)
| 항목 | 기대 | 실측 |
|---|---|---|
| 그래프 게이트 | green | green 90/90 (ontology_gate) |
| 렌더 diff = 델타 문면·예제만 | 예 | 예 — final.md +7/−5(불릿 2·예제 4지점) · render-sync red 0 · ledger-check 위반 0 |
| target-counts N/W/E +2/+2/+2 · q4 3443 | 예 | 3452/3452/3546 · hierarchy green · q4 emit 후 7종 일치 |
| corpus_mirror_sync 11/11 · codex byte cmp 0 | 예 | 11/11 in-sync(소스 span 수동 교체 + --write) · 검사기 codex cmp 0 |
| 새 예제 mypy full/plain 0 · #69 0 · #493 0 | 예 | 렌더 md 추출본: mypy 2.3.1 full 0 · plain 0 · #69/#493 0 |
| 픽스처 good=0·bad_rules exit 2·EXPECTED #493×8 | 예 | good clean(16파일 · 수리 전 #493×3 오탐 재현) · bad #493×8(aliased_shadow +1 · ⑤ 반영: 절대 import로 #298 소거) · fixture_matrix 102/102 · findings 73/73 · baseline 73/73 · cross 350/350 |
| 양 저장소 전/후 차분 0 | 예 | spring_dream 3309/3309 · kkebi 345/345 · 사이드카 제거 · 증거 `evidence-alias-strenum/` orig 6 → patched 0 |
| make verify 6/6 · 봉인 draft | 예 | 1차 red 2(봉인 드리프트·symbol_kinds 소성물 — 예상) → `manifest_seal --write`(status=draft)·`gen_pregate_symbol_kinds` 재소성 → **6/6 green**(177초) |
| 조감도 HTML 갱신 | 예 | `ontology-adoption-map.html` 2026-09-03 행 추가 |
| wiring 근거(D1-4) | delegatedTo만 | `#69` ⓓ 후보는 관련 신호일 뿐 집행선이 아니다(isinstance+raise 형 한정·exit 불산입) — enforcedBy 미기재 · 문장→Work: 불릿 1 → R-3442 · 불릿 2 → R-3443 |

---

# ⑤ 구현 적대 리뷰 반영 (2026-09-03 · 산출 `workspace/eval/field-report-typecheck/rv5/`)

리뷰 결과: A 통과(MINOR 3) · B 통과(MINOR 2) · C BLOCKER 0·MAJOR 4·MINOR 3. 반영: bad 픽스처 절대 import(#298 소거) · docstring «if/try 밖 모듈 블록 미탐색» · 로드맵 R-14 현행화 + R-14b(예방 경로)·R-17(같은 문서 `__post_init__` 무주석 2곳) 등재 · 회신 수치 정정(무기록 8·«5표면» 총칭·주석 부착 = R-3154 위반 명시) · 검수표 하네스 수치·wiring 근거 행.

## 미결 2 — 확정 문면(R-3442)의 결정성 (사용자 결정 · 릴리즈 게이트 동반 상신)
- **MAJOR-1 판별 기준**: 현행 «타입 체커가 통과시키는 값의 거부는 값 검사(예: bool⊂int) · 시그니처가 수용을 약속한 값(예: float 자리의 int)은 거부하지 않는다»는 두 예가 모두 «체커 통과·시그니처 수용»이라 원리로 구분되지 않는다(레인이 str 하위 타입·IntEnum·complex 등에서 판별 불가 — 발주측은 같은 날 `type(timeout_seconds) is not float`를 4파일에 채택해 예시와 반대로 감).
  - **rev2 제안(clarification · ⑥ 감사 R2-1~3 반영)**: «거부할 수 있는 것은 선언 타입의 **하위 타입** 값뿐이다(`bool`⊂`int`처럼 상속으로 통과하는 값). 거르는 형은 `type(x) is <거부할 하위 타입>`(예: `type(amount) is bool`)뿐이며, `type(x) is not <선언 타입>` 형은 승격 값까지 거부하므로 쓰지 않는다. 수치 탑 **승격**으로 통과하는 값(`float` 자리의 `int`·`complex` 자리의 `float`)은 시그니처가 수용을 약속한 것이므로 거부하지 않는다. `bool`은 값 의미가 다른 하위 타입이라 어느 수치 자리에서든 거부할 수 있다.» + 적용 대상 문장을 R-3442·R-3443 공통으로(«두 규범의 적용 대상은 …»).
- **MAJOR-3 적용 단위**: «적용 대상은 이번 작업이 새로 쓰거나 손대는 값 객체 … 손대는 슬라이스에서 제거한다»는 값 객체(파일) 단위라, 하우스룰의 «줄 단위 전파 금지»·discipline-reviewer touched-only 판정과 충돌(한 줄 수정 슬라이스가 파일 전체의 `type() is` 재검사 제거 의무를 켬 — kkebi 68행·spring 27행).
  - **rev2 제안**: «적용 대상은 이번 작업이 새로 쓰는 값 객체와 **손대는 줄**이다 — 손대지 않는 기존 재검사는 소급 대상이 아니며 정리는 발주 소관이다.»
- 두 제안 모두 R-3442 Expression rev2(clarification)로 착지 가능 — 그래프·렌더·LEDGER·q4(리비전 +1)·rulepack·미러 재실행 1사이클(≈10분). 사용자가 ⓐ rev2 채택 / ⓑ 현행 유지(문면 확정 존중) 중 결정.
