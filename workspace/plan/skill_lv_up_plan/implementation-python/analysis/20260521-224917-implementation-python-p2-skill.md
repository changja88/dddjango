수정 대상: skill

# implementation-python P2 skill 분석

## 평가 기준

- 대상 skill: `dddjango/skills/implementation-python/`
- source reference: `workspace/reference/implementation-python/reference/final.md`
- runtime cache: `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-python/`
- metadata 기준: `/Users/hyun/.codex/skills/.system/skill-creator/references/openai_yaml.md`
- P2 기준:
  - 실제 사용자 표현과 사용 예시가 skill 목적과 일치하는가
  - frontmatter `description`에 사용 조건, trigger, 제외 조건이 충분한가
  - 본문에만 숨은 trigger 규칙이 없는가
  - `agents/openai.yaml`의 `display_name`, `short_description`, `default_prompt`가 `SKILL.md`와 일치하는가
  - 명시 요청 없는 optional interface field를 추가하지 않았는가
  - source skill과 runtime cache가 같은 내용을 가리키는가

## 현재 판정

`SKILL.md`는 Python 언어 계층의 type hint, `X | None`, built-in generics, dataclass, `Enum`/`StrEnum`, `Protocol`, pydantic v2 boundary, async/concurrency, exception, Ruff/mypy/pyright 기준을 다룬다. 목적과 reference loading 구조는 source reference와 충돌하지 않고, bundled references도 세부 판단을 한 단계 reference로 분리한다.

다만 P2 metadata와 runtime/source boundary 기준에서 몇 가지 gap이 남아 있었다. 첫째, 본문 Routing은 explicit subagent, role decomposition, parallel review, responsibility splitting 요청을 `workflow-dddjango-subagents`로 보내지만 frontmatter `description`에는 이 trigger가 없었다. 둘째, reference navigation에는 `TypedDict`, type narrowing, decorator, Python-version gate, `NamedTuple`, `match/case`, context manager 같은 Python-specific trigger가 있었지만 frontmatter에서 덜 드러났다. 셋째, `agents/openai.yaml`의 `short_description`은 25-64자 quick-scan blurb 제약보다 길었다. 넷째, bundled runtime references가 `workspace/reference/**` source-authoring path를 직접 노출했다.

## Blocker

없음.

## Major

1. body-only workflow trigger
   - `SKILL.md` 본문은 사용자가 dddjango subagent, role decomposition, parallel review, responsibility splitting을 명시적으로 요구하면 먼저 `workflow-dddjango-subagents`를 사용하라고 한다.
   - frontmatter `description`은 Python typing/API/DB/Django/test 라우팅을 담지만 workflow/subagent trigger를 드러내지 않는다.
   - frontmatter가 실제 routing 조건을 충분히 포함하도록 보정해야 한다.

2. `agents/openai.yaml` short_description 길이 제약 위반
   - `openai_yaml.md`는 `interface.short_description`을 25-64 chars로 설명한다.
   - 현재 `short_description`은 skill 범위를 설명하지만 quick-scan blurb로는 길다.
   - optional interface field는 추가하지 않고 64자 안에서 Python type, validation, concurrency, typecheck 범위를 암시하도록 줄인다.

3. runtime bundled reference의 source-authoring path 노출
   - `dddjango/skills/**/references/**`는 runtime-facing bundled reference다.
   - `references/*.md` 첫머리의 `Source basis: workspace/reference/...` 문구는 source-authoring path를 runtime guidance에 노출한다.
   - source 근거 요약은 유지하되 `workspace/reference/**` 경로는 제거해야 한다.

4. frontmatter trigger coverage 부족
   - 본문 reference navigation에는 `TypedDict`, type narrowing, decorator, Python-version gate, `NamedTuple`, `match/case`, context manager가 있다.
   - frontmatter가 이 Python-specific trigger 표현을 포함하지 않으면 해당 요청에서 skill 선택이 약해질 수 있다.
   - description에 핵심 trigger vocabulary를 추가한다.

## Minor

1. `agents/openai.yaml` default_prompt가 topic inventory처럼 길다.
   - `$implementation-python`을 명시하고 의미는 맞지만, OpenAI metadata 기준의 짧은 example starting prompt로 보기 어렵다.
   - 짧은 한 문장으로 줄인다.

## Note

- `display_name`은 skill 목적과 일치한다.
- `default_prompt`는 `$implementation-python`을 명시하므로 필수 조건은 만족했지만, 더 짧은 example prompt로 보정한다.
- bundled references는 필요한 세부 판단을 분리하지만, runtime-facing 파일에 source-authoring path를 직접 노출하지 않아야 한다.
- source reference 자체의 P2 후속 gap은 발견하지 못했다.
- source skill과 runtime cache는 P2 최초 확인 시 `diff -qr` 기준 차이가 없었다. source 수정 후에는 별도 runtime-sync analysis/plan을 작성하고 cache를 동기화한다.

## 리뷰 방식과 결과

리뷰 방식: real-subagent
- Subagent 리뷰/순차 fallback: real-subagent 리뷰 2건을 실행했다. 하나는 skill-creator 관점, 하나는 독립 P2 감사 관점이다.
- skill-creator 리뷰: runtime bundled reference의 `workspace/reference/**` path 노출을 Major로, frontmatter trigger coverage와 `short_description` 길이를 추가 finding으로 제기했다. 모두 수정했다.
- 독립 P2 리뷰: runtime bundled reference의 source-authoring path 노출을 Major로, `default_prompt`가 짧은 example prompt라기보다 topic inventory에 가깝다는 Minor를 제기했다. 모두 수정했다.
리뷰 결과: Blocker 0, Major 0, 열린 Minor 0

## 재평가

- `SKILL.md` frontmatter에 `TypedDict`, type narrowing, decorators, `NamedTuple`, `match/case`, context managers, Python-version gates와 `workflow-dddjango-subagents` routing을 추가해 본문에만 숨은 trigger를 닫았다.
- `agents/openai.yaml`의 `short_description`을 25-64자 범위 안으로 줄이고, `default_prompt`를 `$implementation-python`을 포함한 짧은 example prompt로 보정했다.
- bundled references의 `workspace/reference/**` path를 제거하고 source 근거는 path 없는 요약 문구로 남겼다.
- optional interface field는 추가하지 않았다.
- source reference 추가 gap은 발견하지 못했다.
- 재평가 결과: Blocker 0, Major 0, 열린 Minor 0

## 결론

P2 현재 기준에서 source reference는 충분하다. `SKILL.md` frontmatter의 workflow/Python-specific trigger 누락, `agents/openai.yaml` metadata 길이와 prompt 형태, bundled runtime reference의 source-authoring path 노출을 수정했다. runtime cache는 별도 runtime-sync 계획에 따라 동기화한다.
