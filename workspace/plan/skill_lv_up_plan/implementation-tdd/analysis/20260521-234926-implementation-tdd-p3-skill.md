수정 대상: skill
리뷰 방식: real-subagent
리뷰 결과: Blocker 0, Major 2, 열린 Minor 3

# implementation-tdd P3 skill 분석

## 점검 범위

- 대상 skill: `dddjango/skills/implementation-tdd/`
- source reference: `workspace/reference/implementation-tdd/reference/final.md`
- runtime cache: `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-tdd/`
- 인접 책임: `architecture-ddd`, `architecture-api`, `architecture-db`, Django 구현 skills, `implementation-test`, `workflow-dddjango-subagents`, `source-reference-audit`

## 현재 상태

- `SKILL.md`는 40줄로 500줄 미만이며, 핵심 routing, reference loading, runtime rules만 담고 있다.
- bundled references 4개는 모두 `SKILL.md`에서 1단계 직접 링크로 발견 가능하다.
- `diff -qr dddjango/skills/implementation-tdd /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-tdd`는 최초 점검 시 차이가 없었다.
- `implementation-test`와의 경계는 pytest fixture/mock/factory, property-based tests, coverage, mutation testing, testcontainers, pytest-bdd/Gherkin mechanics를 넘기는 방식으로 대체로 명확하다.
- `workflow-dddjango-subagents`와의 경계는 composite/risky/subagent 요청을 먼저 넘기는 방식으로 명확하다.

## 발견 사항

### Major 1: 불명확한 도메인 정책/불변식 handoff가 body에서 약함

- `SKILL.md`는 API contract, DB constraint, transaction, locking, migration rollout, consistency가 불명확하면 `architecture-api` 또는 `architecture-db`를 먼저 쓰라고 한다.
- 그러나 테스트 기대값을 고정하기 전 도메인 정책, invariant, aggregate/use case ownership이 불명확한 경우의 handoff는 본문 routing에 직접 드러나지 않는다.
- runtime rule은 ambiguous policy tests를 confirmed behavior와 unresolved decisions로 분리하라고 하지만, unresolved domain decision의 owner가 `architecture-ddd`임을 말하지 않아 TDD skill이 도메인 결정을 암묵적으로 떠안을 수 있다.
- P3 기준상 architecture와 TDD 역할이 서로 침범하지 않으려면, TDD는 테스트 순서와 test list를 맡고 도메인 정책 소유권 결정은 `architecture-ddd`로 넘긴다는 경계가 필요하다.

### Minor 1: `agents/openai.yaml`의 short_description이 `implementation-test`와 겹쳐 보임

- `short_description`의 `test strategy` 표현은 테스트 작성/리뷰, coverage, concurrency를 맡는 `implementation-test`와 넓게 겹쳐 보일 수 있다.
- UI metadata에서는 TDD cycle, first failing test, boundary sequencing처럼 이 skill의 직접 책임을 더 좁게 드러내는 편이 안전하다.

### Major 2: BDD/ATDD relationship 책임의 bundled reference 발견성이 부족함

- frontmatter description은 `BDD/ATDD relationship`을 직접 책임으로 말한다.
- source reference에는 TDD와 BDD/ATDD 관계가 있지만, runtime bundled references 중 이 관계를 직접 설명하는 1단계 reference가 없다.
- `implementation-test`는 pytest-bdd/Gherkin mechanics를 맡으므로, `implementation-tdd`는 BDD/ATDD를 TDD 방법론 관계와 acceptance-loop 판단으로만 좁게 설명하는 bundled reference를 제공해야 한다.

### Minor 2: AI-assisted TDD의 security/performance handoff가 암묵적임

- bundled `ai-assisted-tdd.md`는 security, concurrency, performance가 ordinary TDD examples beyond additional analysis라고 말한다.
- `SKILL.md` routing은 API/DB/transaction/locking은 명시하지만 security/performance 추가 분석 handoff를 직접 말하지 않는다.
- TDD skill이 보안/성능 분석을 직접 수행한다는 오해를 막기 위해, security/performance가 주된 위험이면 관련 architecture/implementation/workflow skill로 넘긴다는 guardrail이 필요하다.

### Minor 3: legacy/characterization work handoff가 약함

- source reference는 legacy code handling을 clean-code material로 넘긴다.
- `implementation-cleancode`는 legacy code, refactoring, code smell review를 맡는다.
- `implementation-tdd`가 characterization test와 Red-Green-Refactor 순서는 맡을 수 있지만, legacy seam/refactoring strategy 자체는 `implementation-cleancode`와 협업해야 한다는 top-level handoff가 있으면 더 명확하다.

## 중복/누락 점검

- `SKILL.md`와 `references/test-list.md`에는 validity window와 independent-axis boundary 규칙이 일부 중복된다.
- 현재 validator가 `SKILL.md`에 `day after expiration rejected`와 `A rejection on another axis` 문구를 요구하므로, 이번 P3에서는 해당 핵심 runtime guardrail을 유지한다.
- reference는 세부 예시와 test-list 설계를 담고, `SKILL.md`는 routing과 실행 중 반드시 지켜야 하는 핵심 guardrail만 유지하므로 열린 P3 중복 문제로 보지 않는다.

## source reference 후속 판단

- source reference는 TDD 방법론, test list, boundary, Red-Green-Refactor, BDD/ATDD 관계, AI-assisted TDD를 충분히 제공한다.
- 다만 DDD handoff 자체를 source reference가 명시적으로 정리하지는 않는다. 기존 P2 후속 분석이 `workspace/plan/reference_lv_up_plan/implementation-tdd/analysis/20260521-225746-implementation-tdd-p2-ddd-routing-source-gap.md`에 남아 있다.
- 이번 P3에서는 runtime skill이 도메인 결정을 수행하지 않도록 handoff만 좁게 명시하고, source reference 보강은 별도 reference 개선 대상으로 유지한다.

## Subagent 리뷰/순차 fallback

리뷰 방식: real-subagent

리뷰 결과: Blocker 0, Major 1, 열린 Minor 1

- skill-creator 관점 real-subagent 리뷰를 요청했다.
- 독립 P3 real-subagent 리뷰에서 BDD/ATDD bundled reference 누락을 Major로, boundary guidance 중복과 security/performance handoff 약함을 Minor로 제기했다.
- skill-creator 관점 real-subagent 리뷰에서 legacy/characterization handoff 약함을 Minor로 제기했다.
- boundary guidance 중복은 validator가 요구하는 핵심 runtime guardrail이므로, 세부는 reference에 두고 핵심 guardrail만 `SKILL.md`에 남기는 방식으로 닫는다.
- 이 문서 기준의 열린 항목은 Major 2, Minor 2이며, 수정 후 재평가에서 Blocker 0, Major 0, 열린 Minor 0으로 닫아야 한다.

## 완료 조건

- `SKILL.md` routing이 불명확한 domain policy/invariant/use case ownership을 `architecture-ddd`로 넘긴다.
- `BDD/ATDD relationship`은 1단계 bundled reference로 발견 가능하다.
- security/performance가 TDD만으로 충분하지 않은 위험이면 관련 architecture/implementation/workflow skill로 넘긴다.
- legacy/refactoring strategy가 주된 이슈이면 `implementation-cleancode`와 handoff한다.
- `implementation-tdd`가 테스트 순서, test list, Red-Green-Refactor, verification choice를 직접 책임으로 유지한다.
- `implementation-test`와 겹치는 broad test strategy 표현을 줄인다.
- 수정 후 source skill과 runtime cache가 동기화된다.
- 재평가와 검증에서 Blocker 0, Major 0, 열린 Minor 0을 확인한다.
