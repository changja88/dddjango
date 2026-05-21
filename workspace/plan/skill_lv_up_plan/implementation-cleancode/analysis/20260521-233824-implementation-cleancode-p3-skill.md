수정 대상: skill

# implementation-cleancode P3 skill 분석

## 평가 기준

- 대상 skill: `dddjango/skills/implementation-cleancode/`
- source reference: `workspace/reference/implementation-cleancode/reference/final.md`
- runtime cache: `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-cleancode/`
- P3 기준:
  - 직접 해결할 책임과 다른 skill로 넘길 handoff 기준이 명확해야 한다.
  - architecture, implementation, test, source audit, workflow 역할과 충돌하지 않아야 한다.
  - `SKILL.md`는 핵심 절차와 routing 판단만 담고 세부 기준은 직접 링크된 bundled reference로 둔다.
  - `SKILL.md`는 500줄 미만이고 bundled reference는 1단계 직접 링크로 발견 가능해야 한다.
  - 같은 정보가 `SKILL.md`와 bundled reference에 중복 저장되어 불일치나 컨텍스트 낭비를 만들지 않아야 한다.
  - source skill과 runtime cache가 동기화되어야 한다.

## 현재 판정

| 항목 | 판정 | 근거 |
|---|---|---|
| 직접 책임 | 충분 | `SKILL.md`는 maintainability review/refactor, responsibility, naming, function shape, encapsulation, duplication, legacy smell을 직접 범위로 둔다. |
| architecture handoff | 충분 | domain/aggregate/contract/DB/architecture pattern 미결정 시 `architecture-ddd`, `architecture-api`, `architecture-db`, `architecture-implementation-patterns`로 보낸다. |
| implementation handoff | 일부 부족 | Python/Django/Django Ninja 구현 handoff는 있지만 template/static/HTMX/server-rendered web 구현 주 owner인 `implementation-django-web`이 빠져 있다. |
| test handoff | 충분 | fixture/mock/factory/coverage/TDD method가 main work이면 `implementation-test` 또는 `implementation-tdd`로 보낸다. |
| source audit handoff | 부족 | source/reference governance, skill metadata, bundled reference, cache sync, leakage review는 `source-reference-audit` 책임인데 `implementation-cleancode` routing에는 제외 조건이 없다. |
| workflow handoff | 충분 | explicit subagent, role decomposition, parallel review, composite work를 `workflow-dddjango-subagents`로 보낸다. |
| progressive disclosure | 충분 | `SKILL.md`는 46줄이고 `responsibility.md`, `naming-functions.md`, `encapsulation-abstraction.md`, `legacy-review.md`를 1단계 직접 링크한다. |
| 중복/누락 | 일부 부족 | 세부 clean-code 기준은 reference로 분리되어 중복이 작다. 다만 routing surface가 source audit/web implementation 경계를 모두 담지 않아 다른 skill 책임과 겹쳐 보일 수 있다. |
| source reference 충분성 | 충분 | `final.md`는 Django/dddjango boundary smell, transaction/API/DDD 선결정, Python 특화 reference handoff, DRY/legacy/refactoring 기준을 포함한다. source 자체 부족은 발견하지 않았다. |
| runtime cache | 현재 충분 | 수정 전 `diff -qr`는 차이를 보고하지 않았다. source skill 수정 후 runtime-sync 분석/계획과 cache 동기화가 필요하다. |

## 원인

- P1/P2에서는 source reference 반영, trigger metadata, UI prompt alignment가 중심이었다.
- P3 기준은 다른 skill의 책임을 침범하지 않는 handoff 표면을 더 엄격히 본다.
- `implementation-cleancode`는 앱 코드 품질 review/refactor skill이고, skill/reference/cache governance는 `source-reference-audit`이 담당한다.
- `implementation-cleancode`는 Fat Template을 smell로 판단할 수 있지만, TemplateView/templates/static/HTMX 구현 자체는 `implementation-django-web`의 책임이다.

## 수정 필요 범위

- `dddjango/skills/implementation-cleancode/SKILL.md`
  - frontmatter description에 `implementation-django-web`과 `source-reference-audit` handoff를 추가한다.
  - routing에 source/reference governance audit 제외 조건을 추가한다.
  - routing에 server-rendered web/template/static/HTMX implementation handoff를 추가한다.
  - Python/Django primary implementation handoff 문장을 primary owner와 clean-code advisory/co-use 기준이 더 선명하게 읽히도록 다듬는다.

## 수정하지 않는 범위

- `workspace/reference/implementation-cleancode/reference/final.md`는 현재 P3 기준에서 source gap이 없으므로 수정하지 않는다.
- bundled references는 이미 직접 링크되고 세부 기준을 나눠 담고 있으므로 새 reference를 만들거나 중복 내용을 늘리지 않는다.
- 다른 dddjango skill, eval pack, validator script는 수정하지 않는다.

## 리뷰 방식과 결과

리뷰 방식: real-subagent
- Subagent 리뷰/순차 fallback: real-subagent 2개를 read-only로 실행했다. 하나는 skill-creator 관점, 하나는 독립 P3 감사 관점이다.
- skill-creator 리뷰: Major 1, Minor 1, Note 2를 보고했다. Python primary work handoff ambiguity는 `implementation-python` primary owner와 clean-code co-use 기준을 분리해 닫았다. Runtime Rules 중 세부 reference와 중복되는 항목은 줄여 progressive disclosure를 보강했다.
- 독립 P3 리뷰: Minor 1, Note 4를 보고했다. source/reference governance handoff 누락은 `source-reference-audit` routing을 추가해 닫았다. runtime cache parity는 source 수정 후 별도 runtime-sync로 재확인했다.
리뷰 결과: Blocker 0, Major 0, 열린 Minor 0
- 닫은 Major 1: Python-specific primary work를 `implementation-python`로 넘기고, 이 skill은 maintainability review/refactor가 중심일 때만 함께 쓰도록 정리했다.
- 닫은 Minor 1: source/reference governance, metadata, bundled reference, cache sync, leakage audit 요청을 `source-reference-audit`로 넘기는 routing을 추가했다.
- 닫은 Minor 2: template/static/HTMX/server-rendered web implementation을 `implementation-django-web`로 넘기는 routing을 추가했다.
- 닫은 Minor 3: Runtime Rules의 detailed responsibility, DRY, legacy refactoring 중복을 줄이고 bundled references에 남겼다.

## 결론

P3 기준에서 source reference와 progressive disclosure 구조는 충분하다. `SKILL.md` routing surface와 Runtime Rules 중복을 좁게 수정했고, runtime cache sync와 재평가 결과 열린 Blocker, Major, Minor는 없다.
