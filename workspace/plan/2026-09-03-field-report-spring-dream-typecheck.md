# 현장 보고 — spring_dream_server mypy strict 전체 검사에서 드러난 dddjango 결함 3건 (2026-09-03)

> **처분 상태 (dddjango 측 · 2026-09-03 갱신)** — 상세 회신: `2026-09-03-field-report-reply.md` · 절차: 루브릭 `2026-09-03-field-report-repair-rubric.md`·계획 `2026-09-03-field-report-repair-plan.md` · 증거 `workspace/eval/field-report-typecheck/`
>
> | # | 판정 | 처분 | 상태 |
> |---|---|---|---|
> | A | **성립**(«죽은 조건» 전제는 과장 — float/bool 가드는 살아 있음) | `architecture-ddd` §3.1 Money 예제 교체 + 규범 신설 R-3442(자기 검증은 값 불변식만·신규·수정 값 객체 적용)·R-3443(재검사·강제 변환 금지·좁히기는 경계 소유) | 브랜치 `fix/field-typecheck` 착지(33b0bd7) · ⑤ 통과 · ⑥ 감사+재검 **«머지 가능»**(73e1812) · 미결 2(판별 기준·적용 단위)는 **rev2 채택·적용**(사용자 09-03 — R-3442·R-3443 clarification: 거부 가능 = 선언 타입의 하위 타입 값만·`type(x) is <하위 타입>` 형·승격 값 거부 금지 · 적용 대상 = 신규 값 객체·손대는 줄) · main 로컬 머지 |
> | A 제안 3·4 | 범위 밖 / 기각 | 테스트 규율 추가는 1프로젝트 관행(과적합 경계) · 예제 mypy 스모크는 과적합 | 종결 |
> | B | 사실 검증됨(23 run 중 mypy 무기록 8) — **기각·발주측 소관** | 프로젝트 툴체인 게이트는 pre-push 훅·발주서 체크리스트 소유 · R-12 발주 가이드에 1줄 반영 예정 | 종결(사용자 결정) |
> | C | **불성립(문면)** — Enum 멤버 예외는 R-3154에 v1.0.0부터 성문 · 실물 원인 = 검사기 #493의 import 별칭(`StrEnum as _StrEnum`) 오탐 → 레인 주석 부착 우회 → mypy red | 검사기 수리: base·데코레이터 이름을 모듈 import 바인딩으로 원명 해소(그림자 pop) · 픽스처 good 2/bad 2 · 양 저장소 전/후 차분 0 · 증거 orig 6 → patched 0 | 착지(b2e1f42) · ⑤ 통과 · 잔재 2파일은 발주측 96e8719로 해소 확인 |
>
> | C 추기(09-03 개정판) | pydantic/ninja 별칭 3파일 19건 · 제안 2(one-public-symbol 계산 제외·별칭 없이 직접 import 문면) | 별칭 해소가 `Schema as _Schema`·`BaseModel as _BaseModel`에도 동일 적용(증거 `evidence-alias-schema/` orig 2 → 0) · 제안 2는 **기각** — 별칭은 이제 원명으로 풀리고 별칭 자체는 적법(#345는 정의만 계수 — 별칭 관행의 근거가 코퍼스에 없음) | 종결 |
> | D(추기) | 항상 raise하는 도우미 `-> None` → `[possibly-undefined]` 증폭 | 플러그인이 만든 모양 아님(B가 잡음) · 문면 1줄 후보(implementation-python «항상 raise/exit 도우미는 `-> NoReturn`») | **R-18 등재** · 사용자 09-03: 조사 전 **보류** |
> | E(추기) | `Any` 정책 부재 — «사용자 결정: 플러그인이 `Any`를 못 쓰게 강제(문면+검사기)» | 신규 규범(하우스룰 §4 절) + 검사기 #493 확장(«명시 `Any`» 위반) = 별도 수리 배치(적대 리뷰 판형) | **R-19 등재** · 사용자 09-03: 조사 전 **보류** — 착수 시 범위(시그니처 무조건·변수 주석 프레임워크 미러 조건부) 재확인 |
> | B 재확인 | 개정판 «수정 우선순위(발주자와 합의)»가 B를 플러그인 1순위로 기록 | 사용자 재확인(09-03 파트 1): **기각 확정** — 게이트(실행·차단)는 프로젝트 소유 · 플러그인은 «생성 코드가 mypy strict·ruff와 충돌하지 않게 설계» 원칙만 소유(R-20 등재) | 종결(8eab0f0) |
> | F(추가 19:30) | composition root 주입 callable ≡ 포트 Protocol 확인·실배선 테스트 부재(리딩 BC 1건 프로덕션 결함) — 제안 F-1·F-2 문면 2줄 | 접수 · ⓪ 검증 전(재현·표본 외 대조·무손실 판정 미실시) | 처분 결정 대기(검증 착수 / D·E와 같은 조사 전 보류) |
>
> 릴리즈: ⑥ 감사 조건 충족 → 재검 «머지 가능». 머지·rev2 집행됨(09-03). 남은 결정 = 릴리즈 시점(즉시 v2.17.17 / pre-gate 승격 배치 동승) · F 처분.

작성: spring_dream_server 발주자 세션(Claude). 대상: dddjango 플러그인 v2.17.16 (`~/.claude/plugins/cache/changja88-dddjango/dddjango/2.17.16`).
계기: 2026-09-03 15:06 spring_dream_server 첫 `git push`(776커밋)에서 pre-push 훅(pre-commit: ruff·ruff format·mypy strict 전체)이 처음 돌아 mypy 171건·ruff format 미적용 189파일이 한꺼번에 노출됐다. 그중 dddjango 레인 산출물에서 나온 것을 원인별로 추적했다.

## 요약 · 위임 추적표 (dddjango 소유자용)

| # | 결함 | 증거 규모 | 고칠 곳(플러그인) | 수정 종류 | 실현 가능성 · 규모 | 상태 |
|---|---|---|---|---|---|---|
| A | 값 객체 템플릿이 선언 타입을 `isinstance`로 재검사 → mypy `[redundant-expr]` | 값 객체 6종 13건 | `architecture-ddd/references/final.md` 값 객체 예제(§A) + `discipline-test`/`implementation-test` 테스트 규율 한 줄 | 문면 | **가능 · 소**: 예제 코드 교체 + 문장 2개. 검사기 불요(B가 잡음) | 미착수 |
| B | G2 완료 조건 "mypy·ruff clean"이 결정적 단계가 아니라 «실행했으면 보고» | 8/29·8/31·9/3 레인 산출물이 활성 mypy 규칙 위반 채 통과 · format 미적용 189파일 | `commands/dddjango.md` Phase 2 G2 직전 단계(§B) | 파이프라인 | **가능 · 중**: 3명령(`mypy --follow-imports=silent <BC>`·`ruff check`·`ruff format --check`) 결정적 실행 + exact command·exit·건수 lane-report 기록. 설정 실존 기계 확인. 1순위 | 미착수 |
| C | `check-public-surface-annotation.py`(#493)가 `… import StrEnum as _StrEnum` / `Schema as _Schema` / `BaseModel as _BaseModel` 별칭 base를 선언적 클래스로 해소 못 함 → 레인이 enum 멤버 `: str`·pydantic `model_config: ConfigDict` 주석으로 우회 → mypy `[misc]` | Enum 2파일 6건(9/1 STOP) + **pydantic/ninja 3파일 19건(9/3 추기 실측)** = 25건 | `scripts/check-public-surface-annotation.py` `_is_declarative_class`(§C) + discipline 문면 한 줄(imported base 제외) + (선택) «선언형 base 별칭 import 금지» 규칙 | 검사기 (+문면) | **가능 · 소**: 모듈 import 별칭 → 원 이름 해소(AST `ImportFrom.asname`) 후 대조 + 프로브 3개(StrEnum·Schema·BaseModel). spring_dream 코드는 플러그인 대기 없이 수리(Enum 완료·pydantic 3파일은 2단계) | 미착수 |
| D | 항상 raise하는 도우미 `-> None` → `[possibly-undefined]` 13건 증폭 | 도우미 1개 → 13건 | `implementation-python` 타입 힌트 절(§D) | 문면(선택) | **가능 · 극소**: 한 문장(`-> NoReturn`). 실질 해결은 B | 미착수 |
| E | `Any` 정책 부재 — §4 «모든 이름에 타입»이 `Any`로 충족됨. 사용자 결정: **플러그인이 `Any`를 못 쓰게 강제** | 시그니처 `Any` 47(RAG 런타임 38·fabfile 7) · RAG 런타임 663줄 · 레인 BC 시그니처 0 | `discipline-houserules` §4 문면(§E) + `scripts/check-public-surface-annotation.py`에 «명시 `Any` 금지» 규칙 추가 | 문면 + 검사기 | **가능 · 중**: 검사기는 이미 모든 annotation을 AST로 순회하므로 `Any`(및 `typing.Any` 속성형) 탐지 추가는 작음. 프레임워크 경계(`clean() -> dict[str, Any]` 미러·`request.user`) 취급을 문면으로 정해야 함(예: 받는 즉시 좁히기 의무·시그니처 `Any` 0) | 미착수 |
| F | (추가 9/3 19:30) composition root가 driven 어댑터에 **시그니처가 다른 함수를 그대로 주입**해도 걸리는 그물이 없다 — 설계 리뷰·discipline·테스트 규율 어디에도 «주입 callable ≡ 포트 Protocol» 확인과 «실배선 1회 실행» 요구가 없어, 리딩 16행 `dependency_wiring.py:42`가 인자 2개 부족한 함수를 꽂은 채 G2를 통과(실요청은 검색 단계에서 TypeError→500) | 리딩 BC 1건(프로덕션 결함) · 테스트 26곳 전부 팩토리 fake | `implementation-django-ninja` §composition_root 문면 한 줄(§F-1) + `implementation-test`/`discipline-test` 테스트 규율 한 줄(§F-2). B와 달리 mypy 실행 요구가 아님 | 문면 2줄 | **가능 · 극소**: 문장 2개. 검사기 불요(실배선 테스트가 잡음). 플러그인이 mypy를 돌리지 않는다는 방침(B 기각)과 양립 | 미착수 |

상태 열은 dddjango 소유자가 갱신한다. spring_dream 발주자는 반영 릴리즈 버전을 `claude plugin list`로 확인한 뒤 A의 코드 13건을 정리한다.

## 수정 우선순위 · 판단 기준 (발주자와 합의 2026-09-03)

플러그인 수정은 두 종류다. **결정적 검사**(파이프라인이 반드시 실행하고 exit로 판정 — 읽든 말든 잡힘)와 **지식·템플릿 문면**(에이전트가 읽고 지켜야 효과 — 확률적).

1. **B가 1순위.** G2에 mypy·ruff check·ruff format --check를 결정적 단계로 넣으면 mypy가 잡는 모든 종류(A·C·D 포함)가 레인 안에서 막힌다. 이것 하나가 구조적 해결이다.
2. **A·C는 문면 수정 필수.** 플러그인 템플릿·하우스룰이 그 모양을 «만들어 내므로» B만으로는 레인마다 red가 나고 매번 수리 왕복이 생긴다. 원인 문면을 고쳐야 애초에 안 만든다.
3. **D는 문면 한 줄만(선택).** 플러그인이 시킨 모양이 아니고 B가 잡는다. 검사기 추가 불요.
4. 앞으로의 기준: 플러그인이 만든 모양이면 문면 수정, 검사가 잡는 단순 누락이면 «게이트 + 발생 시 수리», 검사가 못 잡는데 레인 두 곳 이상에서 반복되면 문면 후보.

spring_dream_server 쪽은 B 반영 전까지 발주자 G2 체크리스트(머지 전 3명령)로 같은 검사를 대신한다. A에 해당하는 코드 13건은 플러그인 문면 수정 뒤에 정리하고, C 6건(9/1 결정 기존)과 D 13건은 게이트 이전 빚이라 즉시 수리한다.

## 환경

- 프로젝트 mypy 설정(`pyproject.toml [tool.mypy]`): `strict = true`, `warn_unreachable = true`, `enable_error_code = [ignore-without-code, truthy-bool, truthy-iterable, redundant-expr, possibly-undefined, unused-awaitable, redundant-self]`, plugin `mypy_django_plugin.main`. 이 설정은 2026-08-26 커밋 `4eaf960`부터 그대로다.
- ruff: `ruff.toml` line-length 130, `select = [E,F,B,I,C90,N,UP,ANN,DJ,RUF,PD,TCH]`. 레인은 `ruff check`는 통과시켰으나 `ruff format`은 적용하지 않았다(HEAD 기준 `ruff format --check .` → 189파일 would reformat).
- 재현: spring_dream_server 루트에서 `uv run mypy spring_dream_server framework` (171건 · 36파일), `uv run ruff format --check .`.

## A. 값 객체 템플릿 — 선언 타입 재검사

### 증상 (mypy `[redundant-expr] Left operand of "or" is always false`)

레인이 만든 값 객체 팩토리가 인자를 `str`/`int`/`float`로 선언해 놓고 같은 타입인지 다시 검사한다.

```python
# application/llm_access/domain_layer/generation_audit/value_object/generation_settings.py:43
def create(cls, *, model: str, max_output_tokens: int, ..., timeout_seconds: float, max_retries: int):
    if not isinstance(model, str) or not model.strip(): raise ...            # :43 — 좌항 항상 거짓
    if isinstance(max_output_tokens, bool) or not isinstance(max_output_tokens, int) or ...  # :45
    if not isinstance(timeout_seconds, float) or ...                          # :49
    if isinstance(max_retries, bool) or not isinstance(max_retries, int) or ...  # :51
```

발생 위치(13건, 레인 산출물):
- `application/llm_access/domain_layer/generation_audit/value_object/generation_settings.py` :43 :45 :49 :51
- `application/llm_access/domain_layer/generation_audit/value_object/caller_label.py` :27
- `application/query_translation/domain_layer/shared_value_object/translation_generation_settings.py` :32 :34 :42
- `application/query_translation/domain_layer/shared_value_object/question.py` :16
- `application/query_translation/domain_layer/shared_value_object/query_language.py` :20
- `application/query_translation/domain_layer/shared_value_object/glossary_reference.py` :33
- (동형 3건은 레인 밖 프로젝트 코드: `framework/technology/rag/runtime/service_runtime.py` :981 :982, `rag_builder/steps/__init__.py` :622 :1767 :4277)

### 검사가 정말 불필요한지 — 호출처 전수 확인(Serena `find_referencing_symbols`)

- 프로덕션 호출처는 전부 `str`로 선언된 값을 넘긴다: OHS 요청 계약(`caller_label: str`, `model: str`, `question: str`, `query_language: str`), 유스케이스의 설정 객체, Django 어드민 폼.
- 유일한 진짜 경계(DB 스냅숏 복원)는 값 객체를 부르기 **전에** 좁힌다 — `GenerationAudit._rehydrate_caller_label(value: object)`가 `type(value) is not str`로 거른 뒤 `CallerLabel.create(value)`를 호출. 이것이 올바른 배치다.
- `str`이 아닌 값을 넘기는 호출은 테스트뿐이며, 전부 `# type: ignore[arg-type]`를 달고 일부러 넘긴다(`test_caller_label.py::test_create_rejects_non_string_value`, `test_generation_settings.py::test_create_rejects_each_invariant_violation`). 즉 검사를 위해 존재하는 테스트다.

→ 타입 재검사는 프로덕션에서 참이 될 수 없는 죽은 조건이다. 값 검사(공백 금지·패턴·범위·`bool` 제외)는 필요하고 mypy도 문제 삼지 않는다.

### 원인 — 플러그인 템플릿

`skills/architecture-ddd/references/final.md` 값 객체 권장 예제(2.17.16 기준 약 L488~505):

```python
class Money:
    amount: int
    currency: str = "KRW"
    def __post_init__(self) -> None:
        """자기 검증 (Self-Validation): 생성 시점에 불변식 강제"""
        if not isinstance(self.amount, int):
            object.__setattr__(self, "amount", int(self.amount))
        if self.amount < 0: ...
```

필드를 `int`로 선언하고 다시 `int`인지 검사(심지어 강제 변환)한다. 레인은 이 형태를 «자기 검증»으로 답습했다. 플러그인이 mypy strict를 완료 조건으로 요구하면서 자기 예제가 그 검사에 걸린다. `implementation-python/references/final.md`의 `Validator` 예제(L785~)는 `value`가 무타입이라 충돌은 없지만 같은 관용구를 강화한다.

### 제안

1. 값 객체 예제를 «값의 불변식만» 검증하도록 교체. 타입은 시그니처가 약속하고 mypy가 지킨다.
   ```python
   @dataclass(frozen=True, slots=True)
   class Money:
       amount: int
       currency: str = "KRW"
       def __post_init__(self) -> None:
           """자기 검증: 값의 불변식만. 타입은 시그니처·mypy 소유."""
           if isinstance(self.amount, bool) or self.amount < 0:   # bool은 int의 하위 타입 — 값 검사에 속한다
               raise ValueError(f"금액은 0 이상이어야 합니다: {self.amount}")
           if not self.currency:
               raise ValueError("통화 코드는 필수입니다")
   ```
2. 타입 좁히기는 입력이 `object`인 경계(driven adapter 역직렬화·스냅숏 복원·폼 `cleaned_data`)가 담당한다는 문장을 값 객체 절에 추가. 모범: `object` 입력 → `type(v) is not str`/`isinstance` → 값 객체 팩토리 호출.
3. 테스트 규율(`discipline-test`/`implementation-test`): "선언 타입을 위반하는 인자를 `# type: ignore[arg-type]`로 넘겨 거부를 검증하는 테스트를 만들지 않는다 — 타입은 mypy가 보호한다. 경계 좁히기 함수는 `object` 입력으로 테스트한다."
4. 위 예제가 mypy strict + `redundant-expr`에서 0건인지 플러그인 자체 스모크에 넣는다.

## B. G2 게이트 — mypy·ruff format이 결정적 단계가 아니다

### 증거

- `redundant-expr`는 2026-08-26(`4eaf960`)부터 활성. 위 값 객체는 2026-08-29(`8d3aac0`, llm_access 슬라이스 2)·2026-08-31(`ad56395`, query_translation)에 레인이 만들었고 G2를 통과했다.
- 2026-09-03 머지된 리딩 16행 `fortune_reading` BC에 mypy 37건: StrEnum 멤버 주석 6(C 참조), ninja `Schema` + pydantic `RootModel` 다중 상속 메타클래스 충돌과 그 여파(`schema_out.py` 15, 컨트롤러 `return-value`·`call-arg` 7), `dependency_wiring.py:42` 주입 함수 시그니처 ≠ Protocol(`arg-type`), `redundant-cast` 2, `validate_calculation_output.py:165` Literal 불일치.
- 전 BC 산출물이 `ruff format` 미적용(줄 폭 130 기준 189파일). 레인은 `ruff check`만 돌린 것으로 보인다.
- `commands/dddjango.md` L172는 "(타입 검사가 구성돼 있으면) mypy strict 결과"를 **보고** 항목으로만 둔다. 결정적 백스톱 27종(registry)에 mypy·ruff format은 없다.

### 제안

Phase 2, G2 배너 직전(registry_gate 6번과 같은 위치)에 결정적 3단계를 추가하고 exact command·exit·건수를 lane-report에 기록하게 한다. 프로젝트 루트 cwd, 프로젝트 설정 그대로:

```
uv run mypy --follow-imports=silent <BC 루트>     # 0건 = 통과. BC 파일만 판정(브라운필드 상류 legacy 제외), 상류 함수 시그니처 대조는 유지
uv run ruff check <BC 루트>                        # 0건
uv run ruff format --check <BC 루트>               # 0건 (또는 ruff format 적용을 슬라이스 커밋 규율에 포함)
```

- `--follow-imports=silent`를 쓰는 이유: 프로젝트 전체 mypy는 brownfield legacy(spring_dream은 framework/rag 런타임 116건)에 항상 막혀 게이트로 쓸 수 없다. 이 모드는 BC 파일의 오류만 보고하면서도 상류 모듈의 어노테이션으로 호출을 검사하므로 `dependency_wiring.py:42` 같은 주입 시그니처 불일치는 잡힌다.
- 설정 재정의 금지(레인이 `--ignore-errors`·`# type: ignore` 남발로 통과시키지 못하게 `ignore-without-code`는 프로젝트가 이미 켬).
- 코디네이터가 "타입 검사가 구성돼 있으면"을 판단하는 대신, `pyproject.toml [tool.mypy]`/`ruff.toml` 실존을 기계적으로 확인해 있으면 필수로 돈다.

## C. 검사기 #493 — import 별칭 `_StrEnum`을 enum base로 해소하지 못함 (정정: 하우스룰 문면 문제가 아니다)

### 증상 (mypy `[misc] Enum members must be left unannotated`, 6건)

```python
# application/fortune_reading/domain_layer/shared_value_object/book_usage_policy.py:1,7-9
from enum import StrEnum as _StrEnum
class BookUsagePolicy(_StrEnum):
    SINGLE: str = "single"
    SOURCE_AND_COMMENTARY: str = "source_and_commentary"
    COMPARE: str = "compare"
```
`abstention_reason.py:7-9`도 동일. 같은 BC의 `translation_disposition_kind.py`·`retrieval_disposition_kind.py`는 직접 `from enum import StrEnum` + 무주석 멤버라 mypy 0건이다.

### 원인 — 검사기의 별칭 해소 부재 (실측)

- 하우스룰 §4는 이미 enum 멤버를 면제한다("프레임워크 선언: … enum 멤버(`RED = 1`) — 달면 프레임워크 의미가 오작동한다"). 문면은 옳다.
- `scripts/check-public-surface-annotation.py`의 `_is_declarative_class`는 base를 **이름 문자열**로만 대조한다(`DECLARATIVE_BASE_NAMES = {"Enum","StrEnum",…}`). `from enum import StrEnum as _StrEnum` 뒤 `class X(_StrEnum)`은 `_StrEnum`이 집합에 없어 일반 클래스로 취급되고, 멤버 `X = "x"`가 #493 «클래스 변수 첫 대입에 타입 없음»으로 잡힌다.
- 2.17.16 실측(격리 프로브): `class A(_StrEnum): X = "x"` → `[#493] … 클래스 변수 X 의 첫 대입에 타입이 없다` · `class B(StrEnum): X = "x"` → 위반 없음.
- 이력: 리딩 레인이 2026-09-01 `docs/superpowers/orders/lane/STOP-fortune-reading-strenum-registry-alias.md`로 같은 결함(당시 2.17.12)을 보고했다. 발주자 결정은 C(직접 `StrEnum` import = 저장소 표준 형상, 별칭 폐기)였고 세 파일은 되돌렸다. 그러나 이후 슬라이스에서 만든 두 파일이 다시 별칭을 쓰고, STOP 문서가 «금지된 workaround»라고 명시한 «멤버에 `: str` 주석 달기»로 #493을 우회했다. mypy 게이트(B)가 없어 통과했다.

### 추기 (2026-09-03 18:40) — 같은 구멍이 pydantic/ninja base에도 열려 있다 (실측 19건)

- 대상: `application/fortune_reading/driving_layer/api/evidence_provisioning/schema/schema_out.py`(12)·`schema_in.py`(3)는 `from ninja import Schema as _Schema`, `framework/pydantic/cited_answer_schema.py`(4)는 `from pydantic import BaseModel as _BaseModel`. 세 파일 모두 `model_config: ConfigDict = ConfigDict(...)`로 주석을 달았고, pydantic이 `model_config`를 `ClassVar[ConfigDict]`로 선언해 두었으므로 mypy `[misc] Cannot override class variable (previously declared on base class "Schema") with instance variable`가 19건 난다. pydantic 문서 형상(`model_config = ConfigDict(...)`, 무주석)이 옳다.
- 2.17.16 실측(fortune_reading BC 복사본 3변형, `check-public-surface-annotation.py .`):

  | 변형 | #493 `model_config` 적발 |
  |---|---|
  | 현재(주석 있음 · `_Schema`) | 0 |
  | 주석 제거 · `_Schema` 유지 | **12** (`클래스 변수 model_config 의 첫 대입에 타입이 없다`) |
  | 주석 제거 · `Schema`로 별칭 해제 | 0 |

  → 검사기가 올바른 코드를 막고, 레인이 검사기를 통과시키려 붙인 주석이 mypy 위반이 된다. `DECLARATIVE_BASE_NAMES`에 `Schema`·`BaseModel`은 이미 있으므로 문제는 오직 별칭 미해소다.
- 별칭을 쓰는 동기도 플러그인 쪽에 있다: 위 제안 2의 one-public-symbol/file 계산이 import된 base를 공개 심볼로 세기 때문에 레인이 `_` 접두로 숨긴다. 저장소의 다른 BC(promotion·wallet·product·service_policy·media_library·fortune_record)는 `from ninja import Schema` 직접 import + 무주석 `model_config`라 0건이다 — 리딩 레인만 이 형상.
- 재발 방지 옵션(선택): 검사기 수정과 별개로 «선언형 base(`Schema`·`BaseModel`·`StrEnum`·`Model` …)는 별칭 없이 직접 import한다»를 discipline 문면에 한 줄 두면, 검사기 수정 전 버전에서도 같은 우회가 생기지 않는다.

### 제안

1. 검사기: `_is_declarative_class`가 모듈의 `import`/`from … import … as …`를 읽어 별칭을 원래 이름으로 해소한 뒤 `DECLARATIVE_BASE_NAMES`와 대조한다(`enum.StrEnum`·`pydantic.BaseModel` 속성 형태도 포함). 프로브 3개(`_StrEnum`·`_Schema`·`_BaseModel` 별칭 vs 직접)를 검사기 스모크에 추가.
2. 문면: 하우스룰 §4는 그대로. 다만 «imported base(stdlib·pydantic·ninja·Django)는 one-public-symbol/file 계산에서 제외»(9/1 발주자 결정)를 discipline 문면에 한 줄 명문화하면 레인이 별칭을 쓸 동기가 사라진다. 선택으로 «선언형 base는 별칭 없이 직접 import» 한 줄을 더하면 검사기 수정 전에도 재발이 막힌다.
3. spring_dream 쪽: Enum 두 파일은 직접 import + 무주석 멤버로 되돌렸다(2026-09-03 `96e8719`, 1단계). pydantic/ninja 세 파일은 별칭 해제 + `model_config` 주석 제거로 2단계에서 수리한다. 9/1 결정이 이미 있으므로 플러그인 수정을 기다리지 않는다.

## 재현 명령 (spring_dream_server 루트)

```
uv run mypy spring_dream_server framework 2>&1 | grep -c ' error: '          # 171
uv run mypy spring_dream_server framework 2>&1 | grep 'redundant-expr'        # A 16건
uv run mypy spring_dream_server framework 2>&1 | grep 'Enum members'          # C 6건
uv run ruff format --check .                                                  # 189 files would be reformatted (9/3 정리 커밋 전)
```

## spring_dream_server 쪽 후속(참고)

- C 6건·D 13건·redundant-cast 5건 등 기계적 수정은 발주자가 main에서 정리 커밋 예정. A 13건은 플러그인 문면 수정 뒤. 리딩 스키마 메타클래스 충돌(B의 37건 중 22건)은 리딩 BC 증분 발주.
- 발주자 G2 체크리스트에도 위 3명령을 추가한다(플러그인 수정과 별개로 즉시 적용).

## D. (추가 · 소) 항상 raise하는 도우미를 `-> None`으로 선언 → `[possibly-undefined]` 13건 증폭

- 증상: `framework/technology/rag/runtime/service_runtime.py:635` `def _fail(message, error=None) -> None:`는 두 경로 모두 `raise`인데 반환형이 `None`이라, `try: x = … except: _fail(…)` 뒤의 `x` 사용 13곳이 전부 "정의 안 됐을 수 있음"으로 잡힌다. `-> NoReturn`으로 바꾸면 13건 → 0건(임시 클론에서 실측).
- 출처: 리딩 16행 레인(codex, dddjango 파이프라인 P3) 커밋 `43e9628`(2026-09-02). 파일은 framework 경로지만 발주서 허용 경로 안의 레인 산출물이다.
- 플러그인 관련성: `implementation-python` 참조에 `NoReturn` 언급이 0건이다. 같은 저장소의 다른 레인 산출물(`llm_access/.../serialized_audit_payload.py`, `stream_generation_use_case.py`)은 `NoReturn`을 썼으므로 지식 부재라기보다 일관성 문제이고, B의 G2 mypy가 돌았다면 레인 안에서 잡혔을 항목이다.
- 제안: `implementation-python` 타입 힌트 절에 한 줄 — "항상 `raise`(또는 `sys.exit`)로 끝나는 도우미는 `-> NoReturn`. `-> None`으로 쓰면 호출부의 흐름 분석(`possibly-undefined`·unreachable)이 깨진다." 검사기 추가는 불필요(B의 mypy 결정적 실행이 잡는다).

## E. (추가) `Any` 정책 부재 — 하우스룰 §4 «모든 이름에 타입»은 `Any`로도 충족된다

- 관찰: 플러그인 문서(implementation-python·houserules·discipline·agents) 어디에도 `Any` 취급 규칙이 없다. §4는 «주석의 존재»만 요구하므로 `x: Any`·`-> Any`가 규율을 통과한다. 리딩 16행 레인의 discipline reviewer는 이를 «typed-first 위반(`Any`에 의한 타입 소거)»으로 자체 판정해 98곳을 교정했다 — 즉 규칙이 없어서 레인이 즉석 규칙을 만들었다.
- 규모(spring_dream, 2026-09-03): 함수 시그니처의 명시 `Any`(ruff ANN401 기준) 47건 — framework 40(RAG 런타임 38 포함) · `fabfile.py` 7(Fabric `Context`) · application 0. 변수 주석까지 포함하면 framework/rag/runtime 663줄 · application 300줄(대부분 Django `clean() -> dict[str, Any]`·`request.user` 같은 프레임워크 경계 미러).
- 판정: dddjango 레인 산출물은 시그니처 `Any`가 0이다(47 중 application 0). RAG 런타임(발주 03 «dddjango 미사용 codex 레인»)이 `Mapping[str, Any]` 중심으로 쓰여 mypy `[no-any-return]` 9건·`Any` 세탁의 주 발원지다. 따라서 이번 9건은 플러그인 문제가 아니지만, **플러그인에 `Any` 정책이 없는 것은 별개의 공백**이다.
- **사용자 결정(2026-09-03): 플러그인이 `Any`를 못 쓰게 강제한다 — 문면과 검사기 둘 다 필수.**
- 제안(문면): §4에 한 절 — "`Any`는 타입이 아니라 검사 포기다. 함수 시그니처에 `Any` 0. 경계 입력(JSON·폼 `cleaned_data`·`request.user`·무스텁 서드파티)은 `object` 또는 프레임워크가 주는 정확한 타입으로 받아 **받는 즉시** 좁힌다(TypeIs/isinstance/`type() is`). JSON 문서는 `Mapping[str, object]`." 결정적 검사(플러그인 소유): `check-public-surface-annotation.py`가 이미 모든 annotation 노드를 순회하므로 «명시 `Any`»(`Any`·`typing.Any`·`t.Any` 속성형, 제네릭 인자 안 포함) 발견 시 위반으로 출력하는 규칙을 추가한다 — 시그니처(인자·반환)는 무조건, 변수 주석은 프레임워크 미러 자리(Django `clean()`·`cleaned_data`·`request.user`)만 «받는 즉시 좁히기» 조건부 허용 여부를 문면으로 확정. 프로젝트 ruff `ANN401`은 이와 별개로 켤 수 있으나(spring_dream은 2026-08-26부터 ignore), 플러그인 검사가 있으면 프로젝트 설정에 의존하지 않는다.

## F. (추가 · 2026-09-03 19:30) composition root의 어댑터 주입 — 시그니처 불일치를 걸러 줄 그물이 없다

### 증상 (프로덕션 결함 · mypy `[arg-type]` 1건이 드러냄)

```python
# application/fortune_reading/composition_root/dependency_wiring.py:42 (리딩 16행 P4 커밋 585c9c6 · 2026-09-03 02:32)
evidence_retrieval_port=RagRuntimeEvidenceRetrievalAdapter(run_retrieval=service_runtime.retrieve_release_evidence)
```

- 어댑터의 포트 Protocol `_RunRetrieval.__call__`은 키워드 인자 9개(`work_id, rag_id, release_id, target_language, retrieval_contract_id/version/digest, query_terms, content_roles`)를 받는다. 주입된 실물 `retrieve_release_evidence`는 그 9개에 더해 **`data_root: Path`·`embedder: Embedder`를 필수**로 요구한다(기본값 없음).
- 어댑터는 9개로 호출하므로 실요청이 검색 단계에 도달하는 순간 `TypeError`가 나고, 컨트롤러의 catch 집합(`_PrepareFortuneEvidenceFailure`)이 아니라 500이 된다. 리딩 머지(`b349dc3`) 이후 main에서 실제 검색이 동작한 적이 없다.
- mypy: `Argument "run_retrieval" to "RagRuntimeEvidenceRetrievalAdapter" has incompatible type "def retrieve_release_evidence(*, data_root: Path, embedder: Embedder, …)"; expected "_RunRetrieval"  [arg-type]`.

### 왜 파이프라인을 통과했나

1. **설계**: architect 명세는 이 함수의 시그니처(`data_root, embedder, work_id, …`)를 그대로 옮겨 적었지만(STOP L2 문서에도 등장) «`embedder`를 누가 어떻게 공급하는가»를 결정하지 않았다. design-review ddd/api/db 셋 다 driven 어댑터의 **미해결 의존**을 지적하지 않았다 — 리뷰 관점 목록에 «주입 callable의 시그니처 ≡ 포트 Protocol»이 없다.
2. **구현·감사**: coder는 함수를 그대로 꽂았고 discipline reviewer도 지나쳤다. 하우스룰·implementation 문면에 «주입 callable은 포트 Protocol과 시그니처가 같아야 하고, 부족한 인자는 composition root가 `functools.partial`/클로저로 묶어 넘긴다»가 없다.
3. **테스트**: 리딩 BC 테스트 26곳이 전부 `build_prepare_fortune_evidence_use_case`를 monkeypatch fake로 바꿔 끼운다(플러그인 문면 «매요청 호출 … 테스트 오버라이드 회피»가 이 방식을 정당화). 어댑터 단위 테스트는 9-인자 fake callable을 넣어 통과. **실배선(진짜 팩토리 → 진짜 어댑터 → 진짜 함수)을 한 번이라도 타는 테스트가 없다.**
4. B(G2 mypy)가 있었으면 즉시 잡혔겠지만, B는 «플러그인이 mypy를 돌리지 않는다»로 종결됐다. 따라서 F는 **mypy 실행 요구가 아니라 문면 2줄**로 제안한다.

### 제안 (문면 2줄 · 검사기 불요)

- **F-1 `implementation-django-ninja` composition_root 절(«build_<use_case>() 팩토리» 문단)에 한 줄**: "어댑터 생성자에 주입하는 callable(함수·메서드·`partial`)은 **어댑터가 선언한 Protocol과 시그니처가 같아야 한다**. 실물 함수가 더 많은 인자를 요구하면 그 인자(경로·모델·설정)는 **composition root가 `functools.partial`/클로저로 묶어** 넘기고, 어댑터·use case는 모른다. 시그니처가 다른 함수를 그대로 꽂는 것은 #85 «만들기와 꽂기 둘뿐»의 «꽂기»가 아니라 미완성 배선이다."
- **F-2 `implementation-test`(또는 `discipline-test`) 테스트 규율에 한 줄**: "BC마다 **composition root 실배선 테스트 1개** — 각 `build_<use_case>()`를 진짜로 호출해 만들어진 use case를 최소 한 경로 실행한다(외부 I/O는 데이터 루트·fixture로, LLM만 fake). 팩토리를 monkeypatch로 통째 갈아 끼우는 테스트는 이 1개를 대체하지 못한다." 이 테스트가 있으면 F 유형은 CI에서 직접 터진다.
- design-review(api 또는 ddd) 관점 목록에 «driven 어댑터의 주입 의존(경로·모델·자격)이 명세에 공급처까지 적혀 있는가» 한 항목을 추가하면 설계 단계에서도 걸린다(선택).

### spring_dream 쪽 후속(참고)

- 수정 방향(발주자 결정 대기 2건): ① 런타임 embedder = Release가 pin한 로컬 모델 스냅숏(`model_snapshot.verify_model_snapshot_ref` → `load_local_embedder`)을 그대로 로드 ② 모델 재사용(캐시) 자리는 BC가 아니라 framework 런타임(`service_runtime`) — BC 안 모듈 전역·lazy 싱글톤은 플러그인 규칙 위반이므로. BC 배선은 `partial(…, data_root=data_root)`만 넘긴다.
- 리딩 BC에 실배선 테스트 1개 추가(F-2 선례).
