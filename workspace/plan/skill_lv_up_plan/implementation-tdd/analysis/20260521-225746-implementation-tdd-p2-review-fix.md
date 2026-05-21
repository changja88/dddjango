수정 대상: skill

# implementation-tdd P2 재평가 수정 분석

## 재평가 결과

post-change real-subagent 리뷰에서 다음 열린 항목이 남았다.

- Major: `architecture-ddd` routing과 aggregate/model ownership 표현은 `implementation-tdd` source reference에서 직접 뒷받침되지 않는다.
- Minor: frontmatter에는 pytest-bdd/Gherkin mechanics route-away가 있지만 본문 `Routing`에는 같은 조건이 명시되지 않았다.

## 원인

- P2 1차 수정에서 DDD model 후보 제시는 제거했지만, 기존 body routing의 `aggregate ownership`, `ubiquitous language`와 새 runtime rule의 `model ownership` 표현이 남아 있었다.
- BDD/ATDD relationship은 source reference에 있고 pytest-bdd 구현 세부는 `implementation-test`로 넘긴다는 source 경계가 있으나, runtime body에 pytest-bdd/Gherkin routing이 빠져 있었다.

## 수정 판단

- `implementation-tdd`는 TDD 방법론 skill이므로 source가 직접 지원하지 않는 DDD ownership routing을 runtime rule로 유지하지 않는다.
- 불명확한 행위/정책은 테스트 기대값을 고정하지 말고 unresolved decision으로 분리한다는 TDD 범위의 안내만 남긴다.
- pytest-bdd/Gherkin mechanics는 본문 routing에도 명시해 frontmatter와 본문을 맞춘다.
- DDD ownership routing을 source reference에 보강할지 여부는 P2에서 억지로 처리하지 않고 reference 후속 분석으로 남긴다.

## Subagent 리뷰/순차 fallback

리뷰 방식: real-subagent

리뷰 결과: Blocker 0, Major 0, 열린 Minor 0

- post-change real-subagent 리뷰 1건을 수행했다.
- 통합 판단: Major 1과 Minor 1은 skill wording 수정으로 닫을 수 있다.
- 재수정 후 final real-subagent 리뷰 결과 Blocker 0, Major 0, Minor 0으로 확인됐다.

## 완료 조건

- `SKILL.md`에서 source-basis가 약한 DDD ownership routing 표현이 제거된다.
- pytest-bdd/Gherkin route-away 조건이 frontmatter와 본문 모두에 보인다.
- 재검토에서 Blocker 0, Major 0, 열린 Minor 0이 된다.
