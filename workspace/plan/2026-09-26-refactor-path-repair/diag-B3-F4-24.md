# 진단 B3 — F4-24 (#647 폼 `clean()` 면제: 문언 ↔ 검사기 불일치)

- 작성 2026-09-26 · 진단만(저장소 수정 0) · 재현은 scratchpad `f4-24/` 사본(`DJR_VIOLATIONS_DIR=…/f4-24/viol`)에서만 했다
- 대상 원문: `workspace/eval/field-report-4/2026-09-10-spring-dream-overhaul-lanes.md` F4-24 절

## 결론 (5줄)

1. 불일치는 실재한다. 문언이 틀렸고 검사기가 맞다. 문언의 전제 «`ModelForm.clean` 은 `None`» 은 사실이 아니다. 조사 단계에서 `BaseModelFormSet.clean` 을 `BaseModelForm.clean` 으로 잘못 읽은 것이다.
2. 레인 h2 의 pre-gate red 는 문언 탓이 아니다. pre-gate 도 같은 검사기를 돌린다. 명세가 `_…FormBase` TYPE_CHECKING 별칭 행을 symbols 에 적지 않았고, 그래서 스텁의 기저가 풀리지 않았다. 별칭 행을 적으면 green 이다(재현 완료). pre-gate 코드 결함은 없다.
3. **측정 영향은 0건이다.** 94건 가운데 `clean()` 반환은 12건이고, 전부 `dict[str, Any]` 다. `Any` 는 문언과 검사기 어느 쪽으로도 면제되지 않는다. F4-24 가 다루는 `dict[str, object]` 반환 3건은 이미 면제돼 94 에 들어 있지 않다. «빚의 56% 측정이 틀렸다» 는 주장은 **반박된다.**
4. 문언을 글자 그대로 따르도록 검사기를 좁혀도 94 → 97(+3)이다. F4-24 가 이 계수를 움직일 수 있는 최대치는 +3 이다.
5. 권고 수정은 문언을 검사기에 맞추는 개정(revision-clarification)이다. 집행 동작은 바뀌지 않는다. 다만 graph-owned 규범 문장의 개정이라 사용자 확정 1회가 필요하다. 반대 방향(검사기를 좁힘)은 규범을 강화하는 변경이고 사실 근거도 없어 권하지 않는다.

## Q1. #647 면제는 어디에 정의돼 있나 — 검증

- `#647` 은 R 번호가 아니라 검사기의 규칙 번호다. `discipline-houserules/references/final.md` 에는 `647` 이 0건이다.
- 면제 문장이 있는 곳은 `dddjango/skills/discipline-houserules/SKILL.md:78` 이다. §4(`:66`)의 `<!-- graph-owned -->` 절(`:67`) 안이고, 다음 graph-owned 절 §4.1(`:97`) 전이다. 따라서 직접 수정은 금지다.
- 정본: `ontology/rules/discipline-houserules-skill.ttl:1210` 블록 `s007-4/b7`. `djr:statesNorm djr:R-3447, djr:R-3448`, 본문 `:1215`.
  - R-3447(`:745` Prohibition «Any 기존 금지/후보…» · 현행 `@2026-09-11` rev3)
  - R-3448(`:765` Obligation «경계 object 즉시 좁힘…» · 현행 `@2026-09-11` rev3)
- 현행 문언(SKILL.md:78 · ttl:1215 · Codex 의미 미러 `codex-dddjango/skills/dddjango-discipline-houserules/SKILL.md:71` 동일):
  > «**반환값·클래스 속성**에 `dict/Mapping[…, object]` 가 남으면 좁히지 않은 누수라 #647 이 차단한다. 기존 면제는 둘 — 스텁이 강제하는 `forms.Form` 하위 `clean() -> dict[str, object]`(`ModelForm.clean` 은 `None` 이라 대상 아님)와 `TypeIs`/`TypeGuard[...]` 반환.»

## Q2. 검사기와 면제 목록 — 검증

- `dddjango/scripts/check-public-surface-annotation.py`(Codex byte 미러 `codex-dddjango/skills/dddjango/scripts/…` — `cmp` 로 동일 확인)
  - docstring `:41-48`: «면제(`object` 만): … `clean()`×{Form, BaseForm, ModelForm, BaseModelForm} · `deconstruct()`×{Field, *Field}»
  - `:163-166`:
    ```python
    FRAMEWORK_OVERRIDE_EXEMPT = {  # 스텁이 `dict[str, Any]` 반환을 강제하는 오버라이드 — `dict[str, object]` 만 면제
        "clean": {"Form", "BaseForm", "ModelForm", "BaseModelForm"},
        "deconstruct": {"Field"},
    ```
  - `_exempt_override` `:702-712`: 클래스 기저를 `_resolved_bases` 로 푼다. 이때 TYPE_CHECKING 별칭 정의까지 따라간다. 호출부는 `:1160` 이다.
  - 판정 `judge` `:1117-1132`: 값이 `Any` 이면 모든 자리에서 차단한다(`:1122`). 면제는 `object` 에만 적용된다(`:1125`).
- 면제 집합과 문언은 같은 커밋 `56b27e12`(2026-09-04 fr3 조각 1)에서 함께 태어났다. 이후 면제 집합은 바뀌지 않았다(`git log -S`).
- 설계 의도는 ModelForm 포함이었다. `workspace/plan/2026-09-04-field-report-repair-3-plan.md:62` 와 `:121` 이 `{clean: {Form, BaseForm, ModelForm, BaseModelForm}}` 를 명시한다.
- 문언이 갈라진 출처는 `workspace/eval/field-report-3/evidence/impl/probe18-summary.md:23` 이다. «`forms/models.pyi:141 BaseModelForm.clean(self) -> None` → `ModelForm.clean` 은 대상 아님» 이라고 적었다.
- 스텁·런타임 실측(spring_dream `.venv` django-stubs 6.1.0 · 읽기만):
  - `django-stubs/forms/forms.pyi:78` `BaseForm.clean(self) -> dict[str, Any] | None`
  - `django-stubs/forms/models.pyi:72-92` `BaseModelForm` 에는 `clean` 선언이 없다. BaseForm 의 것을 상속한다.
  - `models.pyi:141` `clean(self) -> None` 은 `:114` `class BaseModelFormSet` 의 메서드다. **즉 probe 가 잘못 귀속했다.**
  - 런타임 `django/forms/models.py:441-444`(`class BaseModelForm` `:347` 안)는 `return self.cleaned_data` 다. dict 를 반환한다.
- 면제 잠금 픽스처는 `forms.Form` 하나뿐이다: `workspace/eval/fixtures/public_surface/good/…/admin/order/form/order_form.py:14-20`. ModelForm 면제는 코드로만 집행되고 픽스처로 잠겨 있지 않다.

## Q3. pre-gate 는 왜 red 를 냈나 — 검증(재현)

- h2 run `spring_dream_server/.dddjango/20260917-0342-text-library/`
  - `pregate-report.md:23-24`: #647 ×2 (`fixed_phrase_form.py` · `prompt_form.py`)
  - `:124-125`, `:272-273`: filtered ⓑ 로 처분됐다.
- 원인은 명세 symbols 에 별칭 행이 없었던 것이다.
  - `design-spec.md:555-556`: `FixedPhraseForm(_FixedPhraseFormBase) {}` + `clean() -> dict[str, object]`
  - `:596`: «#646 TypeAlias 기저는 symbols 에 미기재(b0 선례 · 의도)»
  - `::alias` 행은 0건이다.
- pre-gate 는 별칭 전사를 지원한다.
  - 문법 `design_pregate.py:48-50`(`alias[TYPE_CHECKING]`/`alias[else]`), 렌더 `:1061-1066`
  - architect 의무 `dddjango/agents/design-architect.md:91` «데코레이터·모듈 별칭도 symbols에 명시한다»
  - 둘 다 `525f6873`(2026-09-10) 이후 dddjango v2.18.1+ 에 들어 있다. h2 는 v2.18.3 이었다.
  - «b0 선례» 는 v2.18.0(09-10, 별칭 전사 없음) 시절의 우회다(spring_dream 메모 `dddjango-pregate-transcription-gaps.md` P5). 그 뒤로 낡았다.
- 재현(scratch 사본의 `parse_spec`+`render_stub` → 사본 검사기):

  | 스텁 | 결과 |
  |---|---|
  | 별칭 행 없음 → `class FixedPhraseForm(_FixedPhraseFormBase)`(미바인딩) | #647 blocker exit 2 |
  | 별칭 행 있음 → `if TYPE_CHECKING: _FixedPhraseFormBase: TypeAlias = forms.ModelForm[…]` | clean exit 0 |
  | 직접 `forms.ModelForm` 기저 | #647 면제, #646 만 발화 |
  | 폼이 아닌 클래스 | #647 blocker |

- 판정: 문언 결함이 있다(Q1/Q2). pre-gate 코드 결함은 없다. h2 의 red 는 명세 전사 누락이다.
- F4-24 원문의 추정 «pre-gate 스텁 예보는 문언 쪽(엄격)을 따르는 듯» 은 **틀렸다.** pre-gate 는 산문을 읽지 않는다.
- 선택 개선(추론): pre-gate 가 «클래스 기저 이름이 별칭·import 어느 쪽으로도 바인딩되지 않음» 을 형식 경고로 알렸다면 h2 는 filtered 대신 corrected 로 갔을 것이다. `parse_spec` 는 이 경우 오류 0 이다(재현 확인).

## Q4. 94건 측정에 영향이 있나 — 검증

- 근거: `evidence/root-run-508a841a8/check-public-surface-annotation.py.txt` 의 blocker 절(`:2` «blocker 4966건» ~ `:4969` ⓓ 시작 전)
  - `application/<bc>/` 필터를 거치면 #647 94 · #645 10 · #646 3 이다. `bc-scan-root-508a841a8.json` 과 plan-v2.md:8 의 94 와 일치한다. 94/168 = 56.0%.
- 값 기준: `Any` 69 · `object` 25. 자리 기준: 반환 33 · 매개변수 23 · 주석(변수/속성) 38.

| 분류 | 건수 | 값 | F4-24 영향 |
|---|---|---|---|
| A 폼 `clean()` 반환 | 12 | 전부 `dict[str, Any]` | 없음 — `Any` 는 문언·검사기 모두 차단 |
| B 폼/패널 `cleaned: dict[str, Any]` 지역 | 18 | Any | 없음 |
| C admin `get_actions()`/`actions` | 6 | Any | 없음 |
| D admin 검증 helper·writer 매개변수 등 | 18 | Any | 없음 |
| E domain_layer(chat_relay payload/item 5 · 반환 2) | 7 | object | 없음 |
| F application_layer | 2 | object | 없음 |
| G test 재료(factories) | 5 | object 3 · Any 2 | 없음 |
| H 어댑터·ORM·클라이언트·OHS 계약 | 26 | object 13 · Any 13 | 없음 |

- 전수 확인(`git show/grep 508a841a8`, 읽기만):
  - `application/**` 의 `def clean(self) ->` 는 24개다. `-> None` 9 · `-> dict[str, Any]` 12(= A) · `-> dict[str, object]` 3.
  - 3건은 `fortune_type_book_inline_form.py:112` · `fixed_phrase_form.py:38` · `prompt_form.py:62` 이다. 셋 다 ModelForm 별칭 기저라 검사기가 면제하고, 94 밖이다.
- **결론: F4-24 가 94건에 미치는 영향은 0이다.** 문언대로 검사기를 좁혔다면 97(+3)이다. «F4-24 때문에 빚의 56% 측정이 틀렸다» 는 사실이 아니다.
- 간접 영향(상환 레시피 쪽) — 검증:
  - A 12건의 최소 상환은 `dict[str, Any]` → `dict[str, object]` 이다.
  - Django ModelForm 기저 9건(별칭 7 · 맨몸 2)은 검사기 기준으로 면제된다. 맨몸 2건은 #646 이 따로 남는다.
  - 현행 문언을 믿는 레인은 이 상환이 막혀 있다고 읽고 TypedDict/`-> None` 쪽으로 과잉 설계할 수 있다. F4-24 의 실제 비용은 여기다.
  - B 18건도 `object` 로 바꾸면 차단에서 ⓓ 후보로 내려간다(변수 자리 `object` = ⓓ · docstring `:43`).
- 인접 관찰 — 검증, F4-24 범위 밖:
  - parler `TranslatableModelForm` 기저 3건(`character_form.py` · `product_form.py` · `campaign_form.py`)은 `dict[str, object]` 로 바꿔도 #647 blocker 로 남는다(재현).
  - 이유: 검사기가 외부 클래스 MRO 를 따라가지 않고, 면제 집합에 parler 가 없다. 규칙 근거(스텁 강제 오버라이드의 미러)를 넓힐지는 별도 결정이다.

## Q5. 어느 쪽을 고치나 · 최소 수정 · 변경 파일

- 근거:
  1. 면제 근거는 «스텁이 강제하는 오버라이드» 다. 그런데 스텁에서 Form 과 ModelForm 의 `clean` 은 같은 선언(`BaseForm.clean`)이다. 근거가 둘을 가를 수 없다.
  2. R-3447(같은 블록)은 «스텁이 `Any` 인 오버라이드도 우리 쪽은 `object` 로» 쓰라고 의무화한다. 그런데 #647 이 ModelForm 의 `dict[str, object]` 를 막으면 두 규범이 서로 부딪힌다. `TypedDict` 반환은 `dict[str, Any] | None` 오버라이드와 호환되지 않는다(추론 — mypy `[override]`).
  3. 설계 계획(repair-3-plan:62·:121)과 검사기가 일치한다. 문언만 잘못된 probe 를 따랐다.
- #546(트랜잭션 쓰기) · #648(반환 Status) · #550 은 이 면제와 무관하다. #645 는 `dict` 값 자리를 #647 에 넘긴다(docstring `:21-25`). 둘은 충돌하지 않는다.
- **최소 수정(권고 A — 문언 → 검사기):** b7 괄호 문구를 다음처럼 바꾼다.
  > «스텁이 강제하는 `forms.Form`/`ModelForm` 계열(`BaseForm`·`BaseModelForm` 하위 — 기저는 TYPE_CHECKING 별칭까지 해소) `clean() -> dict[str, object]`»

  «`ModelForm.clean` 은 `None`» 구절은 지운다. 집행 동작 변화는 0이다.
- 변경 파일(A):
  1. `ontology/rules/discipline-houserules-skill.ttl` — b7 `djr:text` 를 수정하고, R-3448 에 새 Expression(`@2026-09-2x` · rev4 · `djr:revisionKind djr:revision-clarification`)을 더하고 currentExpression 을 교체한다. b7 은 R-3447·R-3448 공동 진술이다. 면제 문장은 R-3448(object 경계) 소관으로 보인다(추론 — 확정은 구현 시).
  2. `ontology_gate.py` → `ontology_render.py --apply discipline-houserules-skill` 로 `dddjango/skills/discipline-houserules/SKILL.md:78` 을 재투영한다.
  3. `ontology/LEDGER.tsv` — `discipline-houserules-skill s007-4` rebaseline 행을 append 한다(선례 `:1632`).
  4. `make rulepack` → `dddjango/scripts/rulepack.json`(R-3448 expression id 변경). 계수표 `workspace/eval/fixtures/ontology_gate/target-counts.json` ExpressionShape +1 · q4 골든을 확인한다(레시피 기준).
  5. `codex-dddjango/skills/dddjango-discipline-houserules/SKILL.md:71` — 의미 미러를 손으로 반영한다.
  6. (권장 잠금) `workspace/eval/fixtures/public_surface/good/` 에 ModelForm 별칭 기저 + `clean() -> dict[str, object]` 픽스처 1개를 더한다. 그에 따라 골든/EXPECTED 행렬 → `manifest_seal.py --write`(마지막) → `make verify` 순으로 진행한다.
  7. (선택) 검사기 `:163` 주석을 «`dict[str, Any] | None`» 으로 정밀화한다. 이때 Codex byte 미러를 동시 갱신한다. 동작 변화는 0이다.
  - 변경 없음: `workspace/reference/**` — 대상이 SKILL.md 라 final.md 소스 미러 범위 밖이다(`ModelForm.clean` 0건 확인). `design_pregate.py` 도 바꾸지 않는다.
- 비권고 B(검사기 → 문언): ModelForm 을 면제에서 뺀다.
  - 규범이 강화되고, 기존 green 3건이 새 빚이 된다.
  - 사실과 어긋난 전제(ModelForm.clean = None)를 제도화하게 된다.
  - 픽스처·골든·Codex byte 미러를 모두 갱신해야 한다.
- 결정 성격:
  - A 는 «집행 중인 동작에 문언을 맞추는 정정 + 사실 오류 삭제» 다. 판단이 필요한 규범 변경은 아니다.
  - 그래도 graph-owned 문장을 개정하므로 사용자 명시 확정 1회 후에 진행한다(명시적 결정 게이트).
  - parler 확장(Q4 인접)과 pre-gate 미바인딩 기저 경고(Q3)는 별도 결정 항목이다.

## 검증 vs 추론

- 검증(파일 대조/실행):
  - Q1 위치·문언
  - Q2 상수·판정 경로·커밋 이력·스텁/런타임 선언·probe 오귀속
  - Q3 명세 누락·별칭 문법·재현 4종
  - Q4 94 재집계·분류·`clean` 24개 전수·parler 재현
- 추론:
  - 면제 문장의 소유 R 번호(R-3448 추정)
  - TypedDict 반환의 mypy `[override]` 비호환
  - 미바인딩 기저 경고가 h2 를 corrected 로 돌렸을 것이라는 가정
