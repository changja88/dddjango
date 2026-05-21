수정 대상: skill
원인 분류: p3-boundary-progressive-disclosure-gap
리뷰 방식: real-subagent
리뷰 결과: Blocker 0, Major 0, 열린 Minor 2

# implementation-test P3 Skill Analysis

## 평가 범위

- Source skill: `dddjango/skills/implementation-test/SKILL.md`
- UI metadata: `dddjango/skills/implementation-test/agents/openai.yaml`
- Bundled references: `dddjango/skills/implementation-test/references/*.md`
- Source reference: `workspace/reference/implementation-test/reference/final.md`
- Runtime cache: `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-test/`
- Neighbor skills: `architecture-api`, `architecture-db`, `architecture-ddd`, `implementation-django`, `implementation-django-ninja`, `implementation-tdd`, `workflow-dddjango-subagents`, `source-reference-audit`

## P3 초기 판정

| 기준 | 판정 | 근거 |
|---|---|---|
| 직접 책임 | 충분 | `SKILL.md`는 pytest, fixtures, factories, doubles, property tests, test quality, `tests/**`, `conftest.py`, factory files를 직접 책임으로 둔다. |
| handoff 기준 | 부분 부족 | domain/DB/API/TDD/production implementation/workflow handoff는 있으나 source/reference governance, runtime cache sync, leakage/boundary review는 `source-reference-audit`로 넘긴다는 runtime routing이 없다. |
| skill 간 책임 충돌 | 열린 Minor | frontmatter와 UI metadata의 `Django Ninja TestClient/API contracts`, `Django API` 표현이 API 계약 설계까지 trigger할 수 있다. 본문은 `architecture-api` handoff를 제공하므로 Major는 아니다. |
| progressive disclosure | 충분 | `SKILL.md`는 42줄이고 다섯 bundled reference를 모두 1단계 직접 링크로 노출한다. reference 파일은 각각 `Load this when...` gate를 가진다. |
| 중복/컨텍스트 낭비 | 열린 Minor | `factories-property-tests.md`의 pytest-bdd Given/When/Then 규칙이 거의 같은 문장으로 중복된다. |
| source reference 충분성 | 충분 | source reference는 TDD는 별도 source로 넘기고, pytest/fixture/double/factory/property/coverage/Django Ninja/idempotency/concurrency 작성법을 충분히 제공한다. source 자체 수정은 필요 없다. |
| runtime cache sync | 충분 | 초기 `diff -qr` 결과 source skill과 runtime cache는 일치했다. source 수정 뒤 별도 runtime-sync 루프가 필요하다. |

## Subagent 리뷰/순차 fallback

Subagent 리뷰/순차 fallback: real-subagent.

- skill-creator 관점 subagent: Blocker 0, Major 0, Minor 2. API metadata wording의 residual misrouting risk와 pytest-bdd 중복 문장을 보고했다.
- 독립 P3 audit subagent: Blocker 0, Major 0, Minor 2. UI metadata가 runtime boundary보다 약하다는 점과 `implementation-test` 전용 semantic validator 부재를 보고했다.
- Main 통합 판단: API metadata wording과 pytest-bdd 중복은 P3 범위의 열린 Minor로 채택한다. 전용 validator hook 제안은 유용하지만 이번 P3의 좁은 수정 범위가 `dddjango/skills/implementation-test/**`이므로 source skill 변경으로 처리하지 않고 Note로 기록한다.

## skill-creator 리뷰

- 목적 명확성: 충분. test implementation/review 목적이 명확하다.
- trigger description: API 계약 설계와 API contract test mechanics가 metadata에서 더 분리되어야 한다.
- progressive disclosure: 충분. `SKILL.md`가 짧고 bundled reference가 직접 링크되어 있다.
- reference 중복/누락: pytest-bdd Given/When/Then 중복 1건을 줄이면 더 낫다.
- validation integrity: 충분. 실제 실행한 tests, coverage, mutation, subagent review만 보고하라는 rule이 있다.

## 수정 방향

- `SKILL.md` frontmatter와 `agents/openai.yaml`의 broad API wording을 `Django Ninja TestClient contract tests` 또는 test mechanics 중심으로 좁힌다.
- `SKILL.md` Routing에 source/reference governance, bundled reference parity, runtime cache sync, leakage/boundary review는 `source-reference-audit`로 넘긴다는 handoff를 추가한다.
- `SKILL.md` Runtime Rules의 risky write test rule을 이미 결정된 invariant/API/DB 기준을 검증하는 책임으로 명확히 한다.
- `factories-property-tests.md`의 pytest-bdd Given/When/Then 중복 문장을 제거한다.
- Source 수정 뒤 runtime cache가 달라지면 runtime-sync 분석/계획을 작성하고 cache를 동기화한다.

## 재평가 기준

- API 계약 설계와 API contract test mechanics가 runtime-facing metadata에서 충돌하지 않아야 한다.
- source/reference governance와 runtime cache sync가 `source-reference-audit`로 handoff되어야 한다.
- bundled reference는 1단계 링크로 발견 가능해야 하고 깊은 reference 연결이 없어야 한다.
- 같은 세부 규칙이 `SKILL.md`와 bundled reference 또는 reference 내부에 불필요하게 중복되지 않아야 한다.
- `SKILL.md`는 500줄 미만이어야 한다.
- 리뷰 결과가 Blocker 0, Major 0, 열린 Minor 0이어야 한다.

## 재평가 결과

- API wording: `SKILL.md`와 `agents/openai.yaml` 모두 Django Ninja `TestClient` contract test로 좁혀 API 계약 설계와 test mechanics의 metadata 충돌을 줄였다.
- Source/reference governance: `source-reference-audit` handoff를 frontmatter와 Routing에 추가했다.
- Risky write tests: 이미 결정된 invariant와 API/DB criteria를 검증하는 책임으로 runtime rule을 명확히 했다.
- Progressive disclosure: `SKILL.md`는 43줄이고 bundled reference 5개를 모두 1단계 직접 링크로 노출한다.
- Duplication: `factories-property-tests.md`의 pytest-bdd Given/When/Then 중복 문장을 제거했다.
- Runtime sync: source skill과 runtime cache `diff -qr` 출력 없음.
- Post-edit real-subagent review: 첫 post-edit 리뷰에서 `Django TestClient` wording Minor 1건이 나왔고, 이를 `Django Ninja TestClient`로 수정했다. 두 리뷰 모두 Blocker 0, Major 0을 보고했다.
- 최종 판정: Blocker 0, Major 0, 열린 Minor 0.
