# 현장 보고(typecheck) 수리 — 1단계 적대 리뷰 A(기술·설계) — 2026-09-03

리뷰어 A. 저장소 무수정·라이브 저장소 읽기 전용. 실측은 `scratchpad/b3/mypy/rv2a/`(mypy 2.3.1 · Python 3.14.7 · spring_dream .venv). 판정 어휘 = 배치 2 루브릭(BLOCKER 문제 불성립/품질 훼손 · MAJOR 근거 약함·수정 필요 · MINOR 표현·범위 · 검증됨).

## (1) 항목별 판정 표

| 항목 | 판정 | 한 줄 근거 |
|---|---|---|
| A-1 «타입 재검사는 죽은 조건» | **MAJOR** | str/int 경로는 참(호출처 전수 typed·`_rehydrate_caller_label(value: object)`가 `type(value) is not str`로 선좁힘 `generation_audit.py:251-255`). 그러나 ① 어드민 폼 2곳은 `dict[str, Any]`를 그대로 넘긴다(보고서 «전부 str 선언» 오기) ② **`float` 재검사는 살아 있다** — mypy가 `Timeout(seconds=30)`(int→float 승격)을 통과시키므로 `generation_settings.py:49`는 redundant-expr로 찍히지만 런타임 거부 조건이고 레인 자체 테스트 `("timeout_seconds", 45)`가 그 거부를 기대한다 ③ 제3 레인(fortune_character)이 같은 가드를 `# type: ignore[redundant-expr]`로 남겨 «의도적 방어»라 주석 — 레인 간 판단 불일치 실증. 문제 자체는 성립(≥3 레인·결정적 재현). |
| A-2(a) 플래그 무관 원칙인가 | **MAJOR** | 원칙(«타입은 시그니처·mypy 소유»)은 plain strict에서도 옳다 — 죽은 분기는 탐지 여부와 무관하게 죽었고 예제의 `int()` 강제 변환은 값 훼손(12.7→12)이라 플래그 무관 결함. 단 문장은 mypy의 정적 구멍 2건(bool⊂int · int→float 승격)을 **명시적으로 결정**해야 한다 — 안 하면 레인이 살아 있는 float 가드를 지우거나(:49) 반대로 ignore로 덮는다(fortune_character). |
| A-2(b) 코퍼스 모순 | **검증됨**(MINOR 1) | DDD 자기 검증=불변식(값) 강제, 타입 선행조건이 아님. cleancode §12.7 «"외부"를 정하고 그 경계에서 검증»(1729행)이 처방 방향 그대로. pydantic §12.3 «coercion이 잘못된 입력을 숨기면 strict»는 현행 예제의 `int()` coercion과 오히려 충돌 — 교체가 정합을 높인다. Validator 예제(792·805행)는 `value` 무타입(Any 입력)이라 모순 아님. MINOR: implementation-test §3.1 `test_add_raises_on_invalid_type`(153행, `add("a", 1)`)이 제안 3과 형태 충돌 — `add` 시그니처 미표시라 판정 유보. |
| A-2(c) 대체 예제 실측 | **검증됨** | `proposed.py`(보고서 예제 + `add` + 경계 함수 2형) → strict+warn_unreachable+redundant-expr **0건**, plain strict 0건. 원본 예제 → full 1건(`unreachable` :11), plain 0건. |
| A-2(d) 교체 vs 유지+경계 문장 | **교체+문장 병행이 무손실** | 유지안은 플러그인이 권하는 플래그에서 red인 예제·값 훼손 coercion을 코퍼스에 남긴다 — 무손실이 아니라 결함 보존. graph-owned(`ontology/rules/architecture-ddd-final.ttl:2222`) → rules 정본 교체 + 렌더. |
| A-3 제안 3(테스트 규율) | **MAJOR — 축소 채택** | 방향은 코퍼스 정합(implementation-test §15.5 «Python 구조만 재확인하는 테스트는 reject» 2105행 · discipline-tdd 425행 reject 정의). 그러나 «`type: ignore[arg-type]` 금지»는 잘못된 지렛대 — spring_dream 테스트 ignore 9곳 중 진짜 타입 위반 거부 테스트는 1곳+파라미터 6행뿐, 나머지는 `object` 파라미터·`**kwargs: dict[str, object]`(정상값 테스트 :49·:58·:69 포함)·통합 race 테스트(chat_relay :86). 의도 기준으로 재문면. |
| A-3 제안 4(예제 mypy 스모크) | **기각** | 실측: architecture-ddd 코드 블록 28 → strict-clean 4/28(오류 141) · implementation-python 78 → 12/78(오류 281). unreachable/redundant는 ddd_006(Money)·py_052·py_057 3블록뿐. 1블록용 하네스=과적합, 전수=400건 재작업. 예제는 «개념 전달용 발췌»(SKILL.md:74)로 선언돼 있다. 대체: 스크래치 1회 실측을 LEDGER 사유/커밋에 기록. |
| C-1 Enum 예외 대 «예외 0» | **BLOCKER(문제 불성립)** | 예외는 **이미 있다** — `dddjango/skills/discipline-houserules/SKILL.md:72` «프레임워크 선언: … enum 멤버(`RED = 1`) — 달면 프레임워크 의미가 오작동한다», 정본 `ontology/rules/discipline-houserules-skill.ttl:470/968`, 커밋 e954659(2026-06-04 DR-39), 설치본 Claude 2.17.16 캐시 :72·Codex 2.17.16 캐시 :65 모두 존재. 보고서 «예외 누락»은 오진 — 리딩 레인(Codex)이 기존 규칙을 어긴 준수 실패다. 닫힌 목록은 열거 가능(아래 §2 C)하나 표본 2저장소에서 다른 항목 발화 0건 → 확장 근거 없음. 최대 MINOR 문면 강화. |
| ⓒ 효과 | **MAJOR(과대)** | 실측 171건 중 redundant-expr 16 = 레인 **11**(보고서 13은 과계수 — 열거된 행도 11) + framework 5(보고서 «3»). Enum 6. A+C = 17/171 = 9.9%. 정리 커밋은 어차피 1건(A·C·redundant-cast 통합) → 커밋 수 절감 0~1. C 효과는 규칙 기존재로 ≈0(85 enum 파일 중 2파일·1레인만 위반, kkebi 106파일 0). kkebi(동일 mypy 플래그) A형 0·C형 0 → 표본 외 발화 없음. |

## (2) 반례·근거 인용

### A-1 호출처 전수(독립 grep·AST)
- 프로덕션 호출처(테스트 제외): `translation_service.py:72-79`(`TranslateRequest` dataclass `question: str`·`query_language: str` — `translate_request.py:15-18`), `translate_use_case.py:93-99`(`GenerationConfigurationOut` `model: str … timeout_seconds: float` — `generation_configuration_out.py:8-12`), `generation_service.py:118-125/168-175/210-217/251-258`(`RequestedGenerationSettings` typed — `generate_text_request.py:25-28`, `caller_label: str` :38), `generation_audit.py:255`(`_rehydrate_caller_label(value: object)` → `type(value) is not str` 선좁힘 :251-253 — 보고서 주장 확인).
- **반례 ①(Any 경로)**: `query_translation_configuration_form.py:30-48` · `intent_generation_configuration_form.py:32-50` — `cleaned: dict[str, Any]`를 `create(model=cleaned["model"], …)`로 직접 전달. mypy 무언. 런타임 타입은 ORM 필드(`query_translation_configuration_model.py:21-28` CharField·PositiveIntegerField·FloatField)가 보장하지만 «좁히기»는 없다. 보고서 제안 2가 cleaned_data를 경계로 이미 지목하므로 처방은 유지, «전부 str 선언» 서술만 정정.
- **반례 ②(승격 구멍)**: `variant_type_is.py` 실측 — `Timeout(seconds=30)`·`Money(amount=True)` mypy strict **무오류**. 같은 파일 `not isinstance(self.seconds, float)` → `redundant-expr`(:28), `type(self.seconds) is not float` → 무경고(:20). 실파일 대조: `generation_settings.py:49`(isinstance형, 찍힘) vs `translation_generation_settings.py:40`(`type() is not float`형, 안 찍힘 — 보고서 목록 :32·:34·:42에 :40 없음) — 같은 의도가 형태에 따라 하나만 red. 레인 테스트 `test_generation_settings.py:96 ("timeout_seconds", 45)`·:97 `True`·:85-86 `True/False`가 이 구멍의 거부를 기대한다.
- **반례 ③(제3 레인의 반대 결정)**: `fortune_character/domain_layer/prompt_set/value_object/weight.py:18-20` · `character/value_object/service_currency_amount.py:18-20` — «런타임 untrusted 입력 방어 — 타입계약을 어긴 caller를 막는 의도적 가드다(U-* 테스트가 검증) … 가드는 유지한다» + `# type: ignore[redundant-expr]`. kkebi `image/domain_layer/image/image.py:36-39`도 같은 긴장(재수화 NULL 드리프트 이중 방어 assert + ignore). → 코퍼스가 판정하지 않아 레인마다 즉흥 결정.
- kkebi 대조(AST): 인자 선언 타입을 isinstance로 재검사 **0건/0파일**, `object`/`Any` 인자 좁히기 60건. spring_dream: 14건/9파일(레인 11 + fortune_character 2 + framework glossary.py:292 1). Enum 멤버 주석 kkebi 0(106파일·341멤버), spring_dream 2파일(85파일).

### A-2 코퍼스 문면
- `architecture-ddd/references/final.md:500-502` 원본 — `if not isinstance(self.amount, int): object.__setattr__(self, "amount", int(self.amount))` — warn_unreachable에서 :11 unreachable(`original.py`), 값 훼손 coercion. `implementation-python/references/final.md:1465-1470` «coercion이 잘못된 입력을 숨기면 strict mode» 취지와 역행.
- `discipline-cleancode/references/final.md:1729` «"외부"를 어디로 정할지 결정하고, 그 경계에서 데이터를 검증하라» — 처방 문장의 코퍼스 내 근거.
- `implementation-test/references/final.md:2105` «`isinstance(EventType.X, str)` … Python/Pydantic 구조만 다시 확인하는 테스트는 … `reject`» · `discipline-tdd/references/final.md:425` reject 정의 — 제안 3의 부착점.
- `implementation-test/references/final.md:150-153` `test_add_raises_on_invalid_type` — 제안 3과 형태 충돌 후보(MINOR).

### A-3 테스트 ignore 분류(spring_dream 9곳)
| 파일:행 | 성격 | 제안 3 대상? |
|---|---|---|
| `llm_access/test/unit/test_caller_label.py:52-55` (123·None·bytes → str) | 순수 타입 위반 거부 | 예 |
| `test_generation_settings.py:76-104` 24행 중 `123·None·1.5·None·2.0` 6행 | 타입 위반 | 예 |
| 같은 파라미터 `True·False·45` 5행 | mypy 구멍(값 검사) | 아니오 — 유지 |
| 같은 파라미터 공백·0·-1·inf·nan 등 13행 | 값 불변식 | 아니오 |
| `test_generation_settings.py:49·:58·:69` (`**kwargs: dict[str, object]`) | 정상값 수용 테스트의 구조 잡음 | 아니오 — 금지하면 오탐 |
| `product/test/unit/test_product_values.py:27-30·45-48`, `wallet/...:99-108` (`[True, 0, -1]`, 파라미터 `object`) | 값·bool 검사, 파라미터 타입만 느슨 | 아니오 |
| `chat_relay/test/integration/…race.py:83-86` (`room_id: object`) | 통합 race 테스트 구조 | 아니오 |

### C-1 «문법이 정한 자리» 닫힌 목록 — mypy 2.3.1 실측(`rv2a/c1/`)
| 범주 | 자리 | 실측 |
|---|---|---|
| 주석 **금지** | Enum/StrEnum/IntEnum/Flag 멤버, `_ignore_`, `nonmember()` | `[misc] Enum members must be left unannotated` (c01·c17·c19). `RED: Final = 1`은 통과(c02) |
| 주석 **금지** | `TypeVar`·`ParamSpec`·`TypeVarTuple`·`NewType` | `Cannot declare the type of a TypeVar or similar construct` / `… NewType declaration` (c03) |
| **지정 형식만** | 타입 별칭(`X: TypeAlias = …` 또는 bare/`type X = …`) | `Bad: type[int] = int` → `not valid as a type [valid-type]` (c07) |
| **지정 형식만** | `__match_args__`(bare 또는 `Final`) | `tuple[str, ...]` 주석 시 캡처가 Any로 퇴화 `[no-any-return]` (c12 vs c13/c14) |
| **지정 형식만** | 함수형 `Enum("…")`·`NamedTuple("…")`·`TypedDict("…")`·`namedtuple` | 주석 자체는 통과(c05)하나 타입 자리 사용 불가(c07과 동형) |
| **지정 형식만** | Django 모델 필드 | `name: str = CharField()` → `[assignment]`, 정확한 Field 타입은 통과(c18) |
| 주석 **필수** | dataclass 필드·NamedTuple 클래스 필드·TypedDict·Protocol 속성·pydantic/ninja | c09 필드 누락(`arg-type`), c10 `[misc]`, c11 `[misc]`, c16 `All protocol members must have explicitly declared types` |
| 무관 | `__slots__`·`__all__`·`Final`·walrus·comprehension | 통과(c12·c15·c20) |

→ 목록은 닫히고 짧다(금지 3 · 형식 지정 4 · 필수 5). 그러나 spring_dream·kkebi 양쪽에서 TypeVar/NewType/`__match_args__` **주석 발화 0건**(bare 사용도 0건). 기존 문면의 «문법이 없는 자리» 예시(SKILL.md:70-72)는 walrus·comprehension·match 캡처·`import as`·def/class 바인딩을 빠뜨린 예시 목록이라 원래 열거형이 아니다.

## (3) 처방 권고

**A — 교체 + 경계·구멍 문장 보강(둘 다)**
1. `architecture-ddd` §3.1 Money 예제(ttl:2222)를 보고서 대체 예제로 교체(실측 0건). `int()` coercion 제거가 핵심 — «자기 검증»은 값 불변식이다.
2. 값 객체 절에 1~2문장 추가: «타입은 시그니처가 약속하고 mypy가 지킨다. `object`/`Any`가 들어오는 자리(역직렬화·스냅숏 복원·폼 `cleaned_data`·`json.loads`)가 경계이며 거기서 좁힌 뒤 팩토리를 부른다(`value: object` → `type(v) is not str` → 팩토리).»
3. **필수 추가(보고서 누락)**: mypy 정적 구멍 2건의 처리 결정을 문면에 박는다 — «`bool`은 `int`의 하위 타입이라 `isinstance(x, bool)` 거부는 값 검사로 유지한다(redundant-expr 0건). `int`→`float` 승격(PEP 484)은 시그니처 계약의 일부이므로 값 객체가 거부하지 않는다 — float 표현 강제가 정말 도메인 규칙이면 `type(x) is not float`(무경고)로 쓰되 시그니처를 `float`로 둔 계약과 충돌함을 안다.» (둘 중 어느 쪽을 택하든 명시 — 현재 두 레인이 두 형태를 혼용).
4. `# type: ignore[redundant-expr]`로 타입 재검사를 남기는 형태(fortune_character)를 명시 금지 — 방어는 경계로 이동.

**C — 코퍼스 수리 기각(문제 불성립) · MINOR 문면 강화 선택**
- 기존 SKILL.md:72의 enum 항목을 독립 줄로 승격하고 사유·오류 코드를 붙인다: «enum 멤버는 `NAME = value`로만 — typing spec(enums#defining-members)이 주석 있는 이름을 멤버로 보지 않으며 mypy `[misc] Enum members must be left unannotated`». 
- 닫힌 목록 확장은 **금지 3건(Enum 멤버·TypeVar류·NewType)**까지만 허용 가능(실측 확정·문면 1줄). «문법이 정한 자리는 문법을 따른다» 단독 문면은 조건부 면제 드리프트(SKILL.md:66이 경고)를 다시 열므로 채택 불가. 형식 지정·필수 범주는 현행 문면(pydantic·ninja·dataclass 필수, 모델 필드 bare)이 이미 덮는다.
- 근본 원인은 준수 실패(Codex 리딩 레인)이므로 코퍼스 수리보다 G2 감수 항목/발주측 mypy 실행(B, 발주측 소관)이 실제 차단선이다.

**제안 3 — 축소 채택**: discipline-tdd reject 범주(425행) 또는 implementation-test §15.5(2105행)에 1문장 부착 — «선언 타입 밖의 값(str 자리에 int/None/bytes, int 자리에 float)을 넘겨 거부를 검증하는 테스트는 언어 구조 재확인이므로 reject — 타입은 mypy가 보호한다. mypy가 못 보는 구멍(bool⊂int·int→float)의 거부는 값 검사이므로 유지. 경계 좁히기 함수는 `object` 입력으로 테스트한다.» «`type: ignore[arg-type]` 금지» 문구는 제외(오탐 8/9).

**제안 4 — 기각**: 코퍼스 예제 strict-clean 비율 4/28·12/78. 대체로 이번 리비전의 스크래치 실측 결과를 LEDGER 재기준선 사유에 기록.

## (4) 10줄 요약

1. A 문제는 성립 — 실측 redundant-expr 16건 = 레인 11(보고서 «13»은 과계수) + framework 5, 3개 레인(llm_access·query_translation·fortune_character)이 같은 관용구를 서로 다르게 처리(무처리/`ignore`) → 코퍼스 판정 부재 실증.
2. 그러나 «죽은 조건» 전제는 MAJOR — mypy는 `Timeout(seconds=30)`·`Money(amount=True)`를 통과시키므로 float/bool 재검사는 살아 있고, 레인 테스트 `("timeout_seconds", 45)`가 그 거부를 기대한다; `type() is not float` 형은 mypy 무경고라 형태에 따라 결과가 갈린다.
3. 어드민 폼 2곳은 `dict[str, Any]`를 그대로 팩토리에 넘긴다 — «호출처 전부 str 선언» 서술 오기(제안 2가 cleaned_data를 경계로 지목하므로 처방은 유지).
4. A-2 원칙은 플래그 무관하게 옳다(죽은 분기·`int()` 값 훼손 coercion은 pydantic §12.3 취지에도 역행) — 단 bool⊂int·int→float 구멍의 처리를 문면에 명시해야 한다(없으면 레인이 살아 있는 가드를 지우거나 ignore로 덮는다).
5. 대체 예제 실측 strict+warn_unreachable+redundant-expr 0건(plain strict도 0) — 원본은 unreachable 1. 코퍼스 모순 없음(cleancode §12.7 경계 검증이 오히려 근거). 교체+경계 문장 병행이 무손실, «예제 유지»는 결함 보존.
6. 제안 3은 축소 채택 — implementation-test §15.5 «구조 재확인 테스트 reject»에 부착; «`type: ignore[arg-type]` 금지»는 ignore 9곳 중 8곳이 값 테스트·구조 잡음이라 오탐 지렛대.
7. 제안 4 기각 — 코퍼스 예제 strict-clean 4/28(ddd)·12/78(python), 1블록 하네스는 과적합.
8. **C는 BLOCKER(문제 불성립)** — enum 멤버 예외가 이미 SKILL.md:72·ttl:470/968·커밋 e954659(06-04)·Claude/Codex 2.17.16 설치본 모두에 존재. 리딩 레인(Codex)의 준수 실패이지 코퍼스 누락이 아니다.
9. C-1 닫힌 목록은 실측으로 닫힌다(금지: Enum 멤버·TypeVar류·NewType / 형식 지정: 별칭·`__match_args__`·함수형 팩토리·모델 필드 / 필수: dataclass·NamedTuple·TypedDict·Protocol·pydantic) — 그러나 양 저장소 발화 0건이라 금지 3건 1줄 이상 확장 근거 없음; «문법이 정한 자리» 단독 문면은 면제 드리프트 재개방이라 불가.
10. ⓒ 효과 과대 — A+C 17/171(9.9%), 정리 커밋 절감 0~1, C 효과 ≈0(85 enum 파일 중 1레인 2파일 위반), kkebi(동일 플래그) A형·C형 발화 0 → 효과는 spring_dream 3레인 국지적·레인당 4~6줄 1회성.
