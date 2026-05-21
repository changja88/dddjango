수정 대상: skill

# implementation-cleancode P2 skill 분석

## 평가 기준

- 대상 skill: `dddjango/skills/implementation-cleancode/`
- source reference: `workspace/reference/implementation-cleancode/reference/final.md`
- runtime cache: `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-cleancode/`
- metadata 기준: `/Users/hyun/.codex/skills/.system/skill-creator/references/openai_yaml.md`
- P2 기준:
  - 실제 사용자 표현과 사용 예시가 skill 목적과 일치하는가
  - frontmatter `description`에 사용 조건, trigger, 제외 조건이 충분한가
  - 본문에만 숨은 trigger 규칙이 없는가
  - `agents/openai.yaml`의 `display_name`, `short_description`, `default_prompt`가 `SKILL.md`와 일치하는가
  - 명시 요청 없는 optional interface field를 추가하지 않았는가
  - source skill과 runtime cache가 같은 내용을 가리키는가

## 현재 판정

| 항목 | 판정 | 근거 |
|---|---|---|
| 목적 | 충분 | `SKILL.md`는 review, refactor, maintainability 개선을 목적으로 두고, behavior/domain intent 보존을 명시한다. |
| 실제 사용자 표현 | 충분 | frontmatter가 clean code, code review, refactoring, naming, function shape, Fat Model/View/Router, 레거시, 유지보수성 리뷰 등 실제 요청 표현을 포함한다. |
| trigger description | 일부 부족 | frontmatter는 넓은 trigger와 주요 라우팅 제외 조건을 담지만, 본문에서 제외하는 `tiny naming question`이 frontmatter에는 `simple one-line explanations`로만 간접 표현되어 있다. |
| 본문 숨은 trigger | 일부 부족 | 본문 Runtime Rules는 직접 refactor 요청을 처리한다고 명시하지만, `agents/openai.yaml`의 default prompt는 review-only로 보일 수 있다. |
| source reference 반영 | 충분 | source reference는 범용 클린 코드, Django/dddjango boundary smell, legacy refactoring 기준을 제공하고 bundled references가 이를 압축 반영한다. |
| bundled references | 충분 | `responsibility.md`, `naming-functions.md`, `encapsulation-abstraction.md`, `legacy-review.md`가 세부 기준을 분리해 progressive disclosure를 유지한다. |
| `agents/openai.yaml` | 일부 부족 | optional field는 없고 `display_name`, `short_description`은 적절하지만, `default_prompt`가 `review`만 말해 직접 refactor 사용 조건과 완전히 맞지 않는다. |
| runtime cache | 현재 충분 | P2 최초 확인 시 `diff -qr`가 차이를 보고하지 않았다. source skill 수정 후에는 별도 runtime-sync 분석/계획이 필요하다. |

## 원인

- P1에서는 source reference 반영과 Fat boundary smell 보강이 중심이었다.
- P2 기준에서는 skill routing metadata가 실제 사용 조건을 더 선명히 드러내야 한다.
- `SKILL.md` 본문은 direct refactor 요청을 허용하지만 UI default prompt가 review-only 예시라 사용자가 이 skill을 리뷰 전용으로 오해할 수 있다.
- tiny naming question 제외 조건은 본문에 직접 있지만 frontmatter에서 더 명확히 보이면 trigger 오탐을 줄일 수 있다.

## 수정 필요 범위

- `dddjango/skills/implementation-cleancode/SKILL.md`
  - frontmatter `description`을 `Use when` 형태로 조정한다.
  - tiny naming questions, typo-only, formatter-only, simple one-line explanations 제외 조건을 명확히 한다.
  - 본문 첫 문장을 review/refactor/maintainability improvement 범위가 frontmatter와 같은 의미로 읽히게 다듬는다.
- `dddjango/skills/implementation-cleancode/agents/openai.yaml`
  - `short_description`과 `default_prompt`가 review와 refactor를 모두 포함하되, optional interface field는 추가하지 않는다.

## 수정하지 않는 범위

- `workspace/reference/implementation-cleancode/reference/final.md`는 P2 현재 기준에서 source gap이 없으므로 수정하지 않는다.
- bundled reference 본문은 P2 기준을 충족하므로 중복 설명을 늘리지 않는다.
- 다른 dddjango skill과 eval pack은 수정하지 않는다.

## 리뷰 방식과 결과

리뷰 방식: real-subagent
- Subagent 리뷰/순차 fallback: real-subagent 2개를 실행했다. 하나는 skill-creator 관점, 하나는 독립 P2 감사 관점이다.
- skill-creator 리뷰: UI default prompt가 review-only로 보여 직접 refactor 범위를 덜 드러내고, frontmatter가 `implementation-django`와 `implementation-django-ninja`를 직접 말하지 않는 Minor를 제기했다. `agents/openai.yaml`과 frontmatter를 수정해 닫았다.
- 독립 P2 리뷰: frontmatter에 `implementation-test`/`implementation-tdd` 라우팅과 explicit subagent/role-decomposition 라우팅이 덜 보이는 Minor를 제기했다. frontmatter를 수정해 닫았다.
리뷰 결과: Blocker 0, Major 0, 열린 Minor 0
- 닫은 Minor 1: UI default prompt가 review-only로 보일 수 있고 frontmatter 제외 조건이 tiny naming question을 직접 드러내지 않았다.
- 닫은 Minor 2: frontmatter의 Django 구현 라우팅이 구체 skill 이름 대신 `Django skills`로만 보였다.
- 닫은 Minor 3: test/TDD-primary 작업과 explicit subagent/role-decomposition 라우팅이 본문에 비해 frontmatter에서 덜 명확했다.

## 결론

source reference와 bundled references는 P2 기준을 충족한다. `SKILL.md` frontmatter와 `agents/openai.yaml`을 좁게 수정했고, source 수정 후 runtime cache는 별도 runtime-sync 절차로 맞췄다. 재평가 결과 열린 Blocker, Major, Minor는 없다.
