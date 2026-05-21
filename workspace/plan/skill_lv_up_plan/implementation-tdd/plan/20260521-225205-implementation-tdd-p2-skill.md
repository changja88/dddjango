# implementation-tdd P2 skill 수정 계획

## 수정 이유

`implementation-tdd`는 TDD 방법론 skill이므로 trigger metadata와 본문 routing이 같은 경계를 말해야 한다. 현재 본문에는 `implementation-test`로 넘기는 상세 테스트 도구/기법과 DDD 모델 후보 안내가 frontmatter보다 구체적으로 들어 있어 P2 기준상 숨은 routing 또는 source-basis gap으로 보일 수 있다.

## 수정 범위

- `dddjango/skills/implementation-tdd/SKILL.md`
  - frontmatter description에 property-based tests, coverage, mutation testing, testcontainers, pytest-bdd/Gherkin mechanics의 route-away 조건을 드러낸다.
  - Django ORM/services/API 구현 handoff를 명확히 한다.
  - DDD model 후보 직접 제시는 제거하고, 불명확한 domain model ownership은 `architecture-ddd`로 넘긴다.
- `dddjango/skills/implementation-tdd/agents/openai.yaml`
  - default prompt를 TDD loop 중심으로 더 짧고 명확하게 조정한다.

## 수정하지 말아야 할 범위

- `workspace/reference/implementation-tdd/reference/**`는 수정하지 않는다.
- 다른 skill의 `SKILL.md`, metadata, bundled references는 수정하지 않는다.
- test fixture/mock/factory 세부 구현 지침을 `implementation-tdd`로 끌어오지 않는다.
- optional `openai.yaml` interface fields를 새로 추가하지 않는다.

## 체크리스트

- [ ] `SKILL.md` frontmatter와 본문 routing 불일치를 줄인다.
- [ ] BDD/ATDD methodology와 pytest-bdd/Gherkin mechanics 경계를 명확히 한다.
- [ ] DDD model 후보 제시를 제거하고 `architecture-ddd` routing으로 대체한다.
- [ ] `agents/openai.yaml` default prompt가 `$implementation-tdd`를 포함하고 1문장으로 유지된다.
- [ ] runtime cache sync 분석/계획을 별도로 작성하고 cache를 동기화한다.
- [ ] 재평가에서 Blocker 0, Major 0, 열린 Minor 0을 확인한다.

## 검증 명령

```bash
.venv/bin/python -B workspace/scripts/validate_plan_constraints.py
.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py
.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills
diff -qr dddjango/skills/implementation-tdd /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-tdd
```

## 완료 조건

- P2 발견 사항의 Major와 열린 Minor가 모두 닫힌다.
- source skill과 runtime cache가 같은 내용을 가진다.
- 필수 검증 명령이 통과한다.
- 최종 보고에 analysis/plan, 수정 파일, 검증 결과, 리뷰 결과, 남은 작업, Serena 사용 여부를 남긴다.
