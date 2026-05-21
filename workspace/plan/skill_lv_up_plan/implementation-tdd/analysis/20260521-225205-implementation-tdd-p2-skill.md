수정 대상: skill
리뷰 방식: real-subagent
리뷰 결과: Blocker 0, Major 1, 열린 Minor 2

# implementation-tdd P2 skill 분석

## 점검 범위

- 대상 skill: `dddjango/skills/implementation-tdd/`
- source reference: `workspace/reference/implementation-tdd/reference/final.md`
- runtime cache: `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-tdd/`
- metadata 기준: `/Users/hyun/.codex/skills/.system/skill-creator/references/openai_yaml.md`

## 현재 상태

- `SKILL.md` 목적은 "behavior를 구현 전 테스트로 전환"하는 TDD 방법론으로 명확하다.
- frontmatter는 TDD, 테스트 목록, 실패 테스트 우선, Red-Green-Refactor, Inside-Out/Outside-In, 경계값, state/behavior verification, mock-role guidance, AI-assisted TDD, 주요 라우팅과 제외 조건을 포함한다.
- bundled references는 source reference의 핵심 결정을 압축해 제공한다.
- `agents/openai.yaml`은 `display_name`, `short_description`, `default_prompt`만 포함하며, optional interface field를 임의로 추가하지 않았다.
- source skill과 runtime cache는 최초 점검 시 `diff -qr` 결과 차이가 없었다.

## 발견 사항

### Major 1: frontmatter보다 본문 routing이 더 구체적임

- 본문은 `implementation-test`로 보내야 할 pytest fixture, mock, factory 외에 property-based tests, coverage, mutation testing, testcontainers를 함께 나열한다.
- frontmatter는 `pytest fixture/factory/tool mechanics`만 말해 body-only route-away 조건이 남는다.
- skill trigger는 frontmatter `description`에 의존하므로, routing/exclusion 조건은 description에서도 충분히 드러나야 한다.

### Minor 1: BDD/ATDD 관계는 source에 있지만 runtime discovery가 약함

- source reference에는 TDD와 BDD/ATDD 관계가 있다.
- P2 목적은 TDD methodology skill의 목적과 trigger 명확화이므로, BDD/ATDD를 별도 runtime 범위로 확장하기보다 TDD methodology 관계 설명은 허용하고 pytest-bdd/Gherkin 구현 세부는 `implementation-test`로 보내는 편이 좁고 안전하다.

### Minor 2: DDD model-candidate guidance의 source basis가 약함

- 본문 runtime rule이 ambiguous domain policy tests에서 value object, aggregate/entity, domain service 후보를 직접 제시한다.
- 이 내용은 TDD source reference보다 DDD modeling source에 가까우며, 이미 routing에서 domain rules/invariants가 불명확하면 `architecture-ddd`를 먼저 쓰라고 안내한다.
- P2에서는 reference를 억지로 확장하지 않고, TDD skill 본문에서는 confirmed tests/unresolved decisions 분리까지만 남기고 모델 후보 결정은 `architecture-ddd`로 넘기는 것이 맞다.

## 수정 판단

- reference 자체를 P2에서 수정할 필요는 없다. source reference는 TDD 방법론, 경계 테스트, Red-Green-Refactor, test quality, BDD/ATDD 관계, AI-assisted TDD를 충분히 제공한다.
- skill metadata와 body routing만 좁게 수정한다.
- runtime cache는 source skill 수정 후 동기화가 필요하다.

## Subagent 리뷰/순차 fallback

리뷰 방식: real-subagent

리뷰 결과: Blocker 0, Major 1, 열린 Minor 2

- skill-creator 리뷰: real-subagent 1건 수행. Major 1, Minor 1, Note 다수.
- 독립 리뷰: real-subagent 1건 수행. Blocker 0, Major 0, Minor 1, Note 다수.
- 통합 리뷰 결과: Blocker 0, Major 1, 열린 Minor 2.

## 완료 조건

- frontmatter description이 본문 routing/exclusion 조건을 숨기지 않는다.
- BDD/ATDD와 pytest-bdd 구현 세부의 경계가 드러난다.
- TDD skill 본문이 DDD model 후보를 독자적으로 제시하지 않는다.
- `agents/openai.yaml`이 `SKILL.md`의 좁아진 목적과 일치한다.
- source/runtime cache diff가 없다.
