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
> | D(추기) | 항상 raise하는 도우미 `-> None` → `[possibly-undefined]` 증폭 | 플러그인이 만든 모양 아님(B가 잡음) · 문면 1줄 후보(implementation-python «항상 raise/exit 도우미는 `-> NoReturn`») | **수리 2 착지(09-04)**: R-3446 신설(implementation-python §4.4 «항상 raise 도우미는 `-> NoReturn`») — 실측 형상 n=2/2저장소(효과 n=1 · spring `_fail` 은 발주측 96e8719 로 이미 수리) · 검사기 없음 · 브랜치 `fix/field-report-2` |
> | E(추기) | `Any` 정책 부재 — «사용자 결정: 플러그인이 `Any`를 못 쓰게 강제(문면+검사기)» | 신규 규범(하우스룰 §4 절) + 검사기 #493 확장(«명시 `Any`» 위반) = 별도 수리 배치(적대 리뷰 판형) | **수리 2 착지(09-04 · 사용자 결정 1 = 시그니처만 차단)**: R-3447/R-3448 신설(하우스룰 §4 «`Any` 는 검사 포기 — 어디에도 쓰지 않는다 · 경계는 `object`/정확 타입으로 받아 즉시 좁힘» 무조건형 · 조건부 허용은 R-3150 과 자기모순이라 채택 안 함 · `object` 대체가 django-stubs strict 에서 통과함을 실측) + 검사기 #645 신설(`check-public-surface-annotation.py` — 시그니처 bare `Any` = 차단 · 제네릭 안·변수 = ⓓ 후보 → R-0284 rev3 로 감사 입력 동봉) · 소급 = application 시그니처 spring 10(프로덕션 8)·kkebi 14(10) — 미러 13·factories 6 은 `object` 기계 치환 · 실질 5 는 좁힘 수리 |
> | B 재확인 | 개정판 «수정 우선순위(발주자와 합의)»가 B를 플러그인 1순위로 기록 | 사용자 재확인(09-03 파트 1): **기각 확정** — 게이트(실행·차단)는 프로젝트 소유 · 플러그인은 «생성 코드가 mypy strict·ruff와 충돌하지 않게 설계» 원칙만 소유(R-20 등재) | 종결(8eab0f0) |
> | F(추가 19:30) | composition root 주입 callable ≡ 포트 Protocol 확인·실배선 테스트 부재(리딩 BC 1건 프로덕션 결함) — 제안 F-1·F-2 문면 2줄 | ⓪ 실측(09-04): 시그니처 불일치는 **1레인 특이**(정적 대조 27/28 BC — spring 15·kkebi 12 — 불일치 0 · 585c9c6 만 1) · 실배선 테스트 부재는 기본 상태(BC 21/28) · «26곳» 미재현(14+3) · `discipline-test` 스킬은 부재 | **수리 2 착지(09-04)**: F-1 = R-0719 rev2(implementation-django-ninja §2.3 «주입 callable ≡ 꽂히는 자리의 Protocol/`Callable` 시그니처 · 부족 인자는 팩토리 본문 안 `partial`/클로저») · F-2 = R-3450(discipline-tdd §5.5 보호 대상 목록 «composition root 실배선 정합» 1항 — 강제·소급 없음 · «BC 마다 1개» 는 quota 라 기각) |
> | G(dddjango 추기) | 카탈로그 레인 발견 ⑪ — OHS의 port 예외 소비 import가 G1 boundary-imports 기계 블록에 없어(산문 §167만) #93이 Phase 2에서 발화 · ① 리뷰 A 판정: 사각 계열이 아니라 **채널 전사 결손**(블록에 적혔다면 예보됐다 — 실행기는 선언 import를 스텁에 방출) | architect 형식 규범(boundary-imports 완전성)에 «예외 소비 import 기재» 조항 후보 · 1레인 · 승격 배치가 사각 목록 S3 문면에 «산문에만 적힌 경계 import 는 표면 밖» 반영(보고 정직화) | **수리 2 착지(09-04)**: ⓪ 실측 — 잎→port 행 블록 0/7 · #93 실발화 5레인(블록 보유 2) · 블록에 적으면 실행기가 실제로 예보(exit 2) · 뿌리 = R-3427 «경계» 미정의(+카탈로그 G1 L57↔L167 내부 모순) → R-3427 rev4(경계 3분류 — BC 내부 층 경계 중 검사기 판정 항목도 행 의무 · 잎→port 예외 import 는 그대로 적어 G1 예보) + R-3449 신설(architecture-ddd §3.6 «port 예외를 도메인 예외 칸으로 번역 — 잎은 port 예외 타입 비의존(재수출 경유 포함)») · **발주측 빚 4 BC**(⑤ C 실측 · 재수출 경유 catch — query_translation 6·fortune_intent 3·fortune_calculation 3(2파일)·notification 1 = except 13 · 명세 2건(notification-bc·fc-2)이 «선례» 로 명문화 · #93 무발화·소급 없음 · 리뷰어 전담) |
> | H(dddjango 추기) | 카탈로그 레인 발견 ⑫ — pre-content 골격의 «자리 실체화(빈 모듈)» ↔ #219/#635 «클래스 하나» 상충 → 제거 시 #218/#193/#576 캐스케이드(왕복 2회·≈14분) | Coordinator 골격 규범 또는 검사기 pre-content 면제 중 택일 후보 · 1레인 관측 | **수리 2 착지(09-04 · 사용자 결정 2 = 빈 파일 무검사)**: ⓪ 실측 — 빈 파일 존재 시 #219 2·#635 3 / 부재 시 #218 2·#193 3·#576 2·#488 5 (서로소 · green 상태 부재 · 13:42 · 삭제 왕복은 1레인, pre-content red 는 4레인) · «규범 간 모순» 은 과장(«하나» 는 Work 0 · 시점 차이) → #219/#635 가 내용 없는 골격 파일(`skeleton_placeholder`)을 건너뜀(다른 검사기 #256/#351/#114 와 정렬) + R-3181 rev3(«빈 파일의 내용 규칙은 내용이 생긴 뒤 · 삭제로 red 해소 금지») · 카탈로그 59d08c7 재실행 5→0 · HEAD 양 저장소 차분 0 |
>
> 릴리즈: 머지·rev2 집행됨(09-03 main 88a65a0) · G-A pre-gate 승격도 main 머지됨(09-04 191842a) · 전부 미push. **릴리즈는 사용자 요청 시까지 보류**. **제보 수정 단계(수리 2) 09-04 착지**: D·E·F-1/F-2·G·H 전부 브랜치 `fix/field-report-2` 에 착지(규범 35fc29b + 검사기) — ⑤·⑥ 뒤 main 로컬 머지 · 릴리즈 요청 시 `make release`(v2.17.17 후보). 정정 추기는 «수정 우선순위» 절 직전.

작성: spring_dream_server 발주자 세션(Claude). 대상: dddjango 플러그인 v2.17.16 (`~/.claude/plugins/cache/changja88-dddjango/dddjango/2.17.16`).
계기: 2026-09-03 15:06 spring_dream_server 첫 `git push`(776커밋)에서 pre-push 훅(pre-commit: ruff·ruff format·mypy strict 전체)이 처음 돌아 mypy 171건·ruff format 미적용 189파일이 한꺼번에 노출됐다. 그중 dddjango 레인 산출물에서 나온 것을 원인별로 추적했다.

## 요약 · 위임 추적표 (dddjango 소유자용)

| # | 결함 | 증거 규모 | 고칠 곳(플러그인) | 수정 종류 | 실현 가능성 · 규모 | 상태 |
|---|---|---|---|---|---|---|
| A | 값 객체 템플릿이 선언 타입을 `isinstance`로 재검사 → mypy `[redundant-expr]` | 값 객체 6종 13건 | `architecture-ddd/references/final.md` 값 객체 예제(§A) + `discipline-test`/`implementation-test` 테스트 규율 한 줄 | 문면 | **가능 · 소**: 예제 코드 교체 + 문장 2개. 검사기 불요(B가 잡음) | 착지(수리 1 · R-3442/R-3443 · main 88a65a0) |
| B | G2 완료 조건 "mypy·ruff clean"이 결정적 단계가 아니라 «실행했으면 보고» | 8/29·8/31·9/3 레인 산출물이 활성 mypy 규칙 위반 채 통과 · format 미적용 189파일 | `commands/dddjango.md` Phase 2 G2 직전 단계(§B) | 파이프라인 | **가능 · 중**: 3명령(`mypy --follow-imports=silent <BC>`·`ruff check`·`ruff format --check`) 결정적 실행 + exact command·exit·건수 lane-report 기록. 설정 실존 기계 확인. 1순위 | 기각 확정(게이트는 프로젝트 소유 · R-20) |
| C | `check-public-surface-annotation.py`(#493)가 `… import StrEnum as _StrEnum` / `Schema as _Schema` / `BaseModel as _BaseModel` 별칭 base를 선언적 클래스로 해소 못 함 → 레인이 enum 멤버 `: str`·pydantic `model_config: ConfigDict` 주석으로 우회 → mypy `[misc]` | Enum 2파일 6건(9/1 STOP) + **pydantic/ninja 3파일 19건(9/3 추기 실측)** = 25건 | `scripts/check-public-surface-annotation.py` `_is_declarative_class`(§C) + discipline 문면 한 줄(imported base 제외) + (선택) «선언형 base 별칭 import 금지» 규칙 | 검사기 (+문면) | **가능 · 소**: 모듈 import 별칭 → 원 이름 해소(AST `ImportFrom.asname`) 후 대조 + 프로브 3개(StrEnum·Schema·BaseModel). spring_dream 코드는 플러그인 대기 없이 수리(Enum 완료·pydantic 3파일은 2단계) | 착지(수리 1 · 검사기 #493 별칭 해소 · main 88a65a0) |
| D | 항상 raise하는 도우미 `-> None` → `[possibly-undefined]` 13건 증폭 | 도우미 1개 → 13건 | `implementation-python` 타입 힌트 절(§D) | 문면(선택) | **가능 · 극소**: 한 문장(`-> NoReturn`). 실질 해결은 B | 착지(수리 2 · R-3446) |
| E | `Any` 정책 부재 — §4 «모든 이름에 타입»이 `Any`로 충족됨. 사용자 결정: **플러그인이 `Any`를 못 쓰게 강제** | 시그니처 `Any` 47(RAG 런타임 38·fabfile 7) · RAG 런타임 663줄 · 레인 BC 시그니처 0 | `discipline-houserules` §4 문면(§E) + `scripts/check-public-surface-annotation.py`에 «명시 `Any` 금지» 규칙 추가 | 문면 + 검사기 | **가능 · 중**: 검사기는 이미 모든 annotation을 AST로 순회하므로 `Any`(및 `typing.Any` 속성형) 탐지 추가는 작음. 프레임워크 경계(`clean() -> dict[str, Any]` 미러·`request.user`) 취급을 문면으로 정해야 함(예: 받는 즉시 좁히기 의무·시그니처 `Any` 0) | 착지(수리 2 · R-3447/R-3448 + #645) |
| F | (추가 9/3 19:30) composition root가 driven 어댑터에 **시그니처가 다른 함수를 그대로 주입**해도 걸리는 그물이 없다 — 설계 리뷰·discipline·테스트 규율 어디에도 «주입 callable ≡ 포트 Protocol» 확인과 «실배선 1회 실행» 요구가 없어, 리딩 16행 `dependency_wiring.py:42`가 인자 2개 부족한 함수를 꽂은 채 G2를 통과(실요청은 검색 단계에서 TypeError→500) | 리딩 BC 1건(프로덕션 결함) · 테스트 26곳 전부 팩토리 fake | `implementation-django-ninja` §composition_root 문면 한 줄(§F-1) + `implementation-test`/`discipline-test` 테스트 규율 한 줄(§F-2). B와 달리 mypy 실행 요구가 아님 | 문면 2줄 | **가능 · 극소**: 문장 2개. 검사기 불요(실배선 테스트가 잡음). 플러그인이 mypy를 돌리지 않는다는 방침(B 기각)과 양립 | 착지(수리 2 · R-0719 rev2 · R-3450 — 정정 추기 ①② 참조) |

상태 열은 dddjango 소유자가 갱신한다. spring_dream 발주자는 반영 릴리즈 버전을 `claude plugin list`로 확인한 뒤 A의 코드 13건을 정리한다.

> **정정 추기(dddjango 측 · 2026-09-04 · 수리 2 ⓪~③ 실측 — 원문은 보존한다)**
> ① 추적표 A·F 행과 F-2 의 «`discipline-test`» 스킬은 존재하지 않는다 — 테스트가 무엇을 보호하는가는 `discipline-tdd` §5.5 소유(F-2 착지) · 메커니즘은 `implementation-test`.
> ② F «테스트 26곳」 은 미재현 — 실측 `build_*` monkeypatch 14 + llm_access 3(증거 `workspace/eval/field-report-2/evidence/F/`).
> ③ D «13건 증폭」 은 43e9628 시점 수치 — HEAD 는 발주측 96e8719 로 `_fail -> NoReturn` 이라 0 · 표본 외 kkebi 1건(`payment_processing_adapter.py:437` — 같은 파일에 `-> Never` 정답 공존)은 호출부 위치라 mypy 증폭 0.
> ④ E «시그니처 `Any` 47 · application 0」 은 ANN401(별표 인자 면제) 기준 — 재집계 application 프로덕션 시그니처 bare `Any` = spring 8 · kkebi 10(Django 스텁 미러 13 · 실질 세탁 5 — 증거 `evidence/DE/`). 변수 주석 bare 37/61 · 제네릭 안 포함 120/133.
> ⑤ G «6행 블록」 은 카탈로그 G1 판본(9ee721e) 기준으로 정확 · 잎→port 행이 블록에 있는 명세는 0/7 · 카탈로그 G1 L57(«OHS 는 port 를 import 하지 않는다」)과 L167 이 내부 모순.
> ⑥ H «왕복 2회·≈14분」 = 게이트 red 2회 · 파일 왕복(0B add→delete→add) 1회 · 13분 42초 · «lane 6」 정의는 발주서에 없음(ledger 는 레인 4) · 삭제 왕복은 카탈로그 1레인, pre-content #219/#635 red 자체는 4레인(promotion-pricing·fortune-reading·kkebi saju·catalog).

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

- **수리 완료(2026-09-03 `36258bb`, 발주자 직접)**: ① 런타임 embedder = Release manifest `build_plan_ref` → Build Plan의 유일한 `model-snapshot:` 참조 → `verify_model_snapshot_ref`·`load_local_embedder`(framework `service_runtime.retrieve_release_evidence_with_local_embedder`, `functools.cache`로 프로세스당 1회) ② BC 배선은 `partial(…, data_root=data_root)`만 주입(#85 인라인 유지, BC 안 싱글톤 없음). 검증: mypy 122→121·registry_gate 귀속 0·make test 614+2096.
- 리딩 BC 실배선 테스트 1개 추가(`test/unit/test_composition_root_wiring.py` — F-2 선례): 진짜 팩토리→실 어댑터→실 런타임→실 Release, fake는 LLM 경계 포트와 가중치 소재뿐. 옛 배선으로 되돌리면 `TypeError: missing 'data_root' and 'embedder'`로 실패함을 실측.
- 작성 중 플러그인 검사기가 잡은 것 2건(F-2 문면에 함께 적을 정합 조건): 타 BC OHS 계약 import(#13·#385 → **자기 BC의 fake 포트**로 대체) · `test/integration/`은 실DB 자리(#389 → **`test/unit/`**에 둔다).

## G·H. (dddjango 측 추기 · 2026-09-03 · 카탈로그 레인 발견 ⑪·⑫ — 사용자 지시로 이 파일에 병기)

같은 프로젝트(spring_dream_server)의 fortune-catalog 레인(v2.17.16 · REPORT f6ef7ff)에서 관측된 플러그인 결손 후보 2건. 1차 자료: `workspace/eval/pregate-observe/ledger.md` 레인 4 «발견», spring REPORT «설계 진화» 3·«비고» lane 6. 둘 다 1레인 관측이라 제보 수정 단계에서 ⓪(재현·표본 외 대조·무손실 판정)부터 시작한다.

### G. 산문 전용 계약 — boundary-imports 기계 블록에 예외 소비 import가 없다 (발견 ⑪)

- 증상: driving 잎 OHS가 `application_layer/port/` 예외를 직접 import하는 경로가 G1 명세의 boundary-imports 블록(6행)에 없고 산문 §167에만 있었다 → pre-gate(기계 블록만 판정)가 보지 못하고 Phase 2 슬라이스에서 #93 발화 → use case가 port 예외를 app-layer 실패로 번역하도록 설계 진화(REPORT «설계 진화» 3).
- 후보 처방: architect 형식 규범(«물리 신호 어노테이션»·boundary-imports 완전성)에 «예외 클래스 소비 import도 기재» 조항 1줄 — 기계 블록의 커버 표면을 산문 계약까지 넓힌다. 검사기 변경 없음(pre-gate는 블록을 읽을 뿐).
- ⓪ 질문: 리딩·notification 등 다른 레인 명세에서 예외 소비 import가 블록 밖에 놓인 사례가 있는가(≥2 레인) · 조항 추가가 architect 반송(형식 red)을 늘리는가(무손실).

### H. pre-content 골격 상충 — 자리 실체화 vs 존재-하나 규칙 (발견 ⑫)

- 증상: 슬라이스 0 골격에서 빈 `_port.py`/`_use_case.py`를 만들면 #219/#635(«클래스 하나»)가 발화하고, 빈 파일을 지우면 #218/#193/#576이 캐스케이드로 발화 → 빈 자리 복원(왕복 2회·≈14분 · spring 커밋 59d08c7→99253ce→9c8814e).
- 후보 처방(택일): ⓐ Coordinator 골격 규범에 «pre-content 골격은 자리 실체화 없이 첫 슬라이스가 채운다» ⓑ 해당 검사기에 pre-content(빈 모듈) 면제 — ⓑ는 면제 «추가»라 무손실 증명 별도.
- ⓪ 질문: 다른 신규 BC 레인(kkebi 21런·spring 리딩)에서 같은 왕복이 있었는가 · 캐스케이드 3종의 발화 조건이 결정적으로 재현되는가.
