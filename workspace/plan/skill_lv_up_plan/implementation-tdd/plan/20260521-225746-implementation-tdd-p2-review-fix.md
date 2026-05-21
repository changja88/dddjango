# implementation-tdd P2 재평가 수정 계획

## 수정 이유

P2 1차 수정 후에도 source reference가 직접 지원하지 않는 DDD ownership routing 표현과 body-only 누락 조건이 남았다. skill runtime은 TDD source가 뒷받침하는 방법론 범위로 좁히고, 상세 테스트 도구 구현 routing은 frontmatter와 본문에 모두 드러내야 한다.

## 수정 범위

- `dddjango/skills/implementation-tdd/SKILL.md`
  - frontmatter에서 `architecture-ddd` routing 표현을 제거한다.
  - body routing에서 `aggregate ownership`, `ubiquitous language` 표현을 제거한다.
  - body routing의 `implementation-test` 항목에 pytest-bdd/Gherkin mechanics를 추가한다.
  - runtime rule에서 `model ownership` routing을 제거하고 unresolved decisions 분리로 바꾼다.

## 수정하지 말아야 할 범위

- bundled references는 수정하지 않는다.
- `agents/openai.yaml`은 현재 alignment가 확인됐으므로 수정하지 않는다.
- DDD routing source decision을 P2 skill 수정으로 새로 만들지 않는다.

## 체크리스트

- [ ] unsupported DDD ownership routing wording 제거
- [ ] pytest-bdd/Gherkin body routing 추가
- [ ] runtime cache sync 분석/계획 작성 및 동기화
- [ ] source/runtime diff 확인
- [ ] 필수 검증 재실행

## 검증 명령

```bash
.venv/bin/python -B workspace/scripts/validate_plan_constraints.py
.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py
.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills
diff -qr dddjango/skills/implementation-tdd /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-tdd
```

## 완료 조건

- 재평가 리뷰 결과 Blocker 0, Major 0, 열린 Minor 0이다.
- source/runtime cache parity가 확인된다.
- 검증 결과가 확인되고, 전체 skill validator 실패가 있으면 target 외 실패인지 명확히 분리한다.
