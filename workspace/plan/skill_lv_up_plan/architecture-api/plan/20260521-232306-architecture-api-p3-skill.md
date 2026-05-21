수정 대상: skill

# architecture-api P3 수정 계획

## 수정 이유

`architecture-api` skill은 REST API 계약 설계의 책임과 handoff 기준을 이미 갖고 있지만, `SKILL.md`의 runtime 규칙이 bundled reference의 세부 기준을 다시 요약한다. P3 목표에 맞게 `SKILL.md`는 핵심 절차와 routing 판단만 담고, 세부 규칙은 필요할 때 직접 링크된 reference로 로딩되도록 줄인다.

## 수정 범위

- 수정 대상:
  - `dddjango/skills/architecture-api/SKILL.md`
  - 필요 시 `dddjango/skills/architecture-api/agents/openai.yaml`
  - source skill과 runtime cache 차이가 생기면 runtime cache 동기화
- 수정하지 말아야 할 범위:
  - `workspace/reference/architecture-api/reference/final.md`
  - 다른 skill의 `SKILL.md` 또는 bundled reference
  - eval case, answer oracle, evaluator, report
  - architecture-api bundled reference의 세부 내용은 명백한 연결 누락이 있을 때만 최소 수정

## 수정 절차

1. `SKILL.md`의 description, routing, reference loading, runtime 규칙을 P3 관점으로 다시 정리한다.
2. 세부 상태 코드, Problem Details, pagination, compatibility, OpenAPI 판단은 bundled reference로 넘기고 `SKILL.md`에는 산출물 체크 순서만 남긴다.
3. direct responsibility와 handoff 기준을 `architecture-ddd`, `architecture-db`, `implementation-django-ninja`, `implementation-test`, `workflow-dddjango-subagents`와 충돌하지 않게 조정한다.
4. source skill 수정 후 runtime cache와 비교한다.
5. runtime cache가 source skill과 다르면 별도 `runtime-sync` 분석/계획을 작성하고 cache를 동기화한다.
6. subagent review 또는 순차 fallback review를 수행하고 Blocker/Major/열린 Minor가 남으면 다시 수정한다.

## 체크리스트

- [ ] `SKILL.md`가 500줄 미만이다.
- [ ] bundled reference가 모두 `SKILL.md`에서 1단계 직접 링크로 발견된다.
- [ ] `SKILL.md`가 REST API 계약 설계의 직접 책임을 설명한다.
- [ ] domain, DB, implementation, test, workflow handoff 기준이 서로 충돌하지 않는다.
- [ ] 세부 설계 규칙이 `SKILL.md`와 reference에 불필요하게 중복되지 않는다.
- [ ] source reference 후속 작업이 필요하면 reference plan으로 분류하고 skill에 억지 반영하지 않는다.
- [ ] source skill과 runtime cache가 동기화된다.
- [ ] 리뷰 결과 Blocker 0, Major 0, 열린 Minor 0이다.

## 검증 명령

```bash
.venv/bin/python -B workspace/scripts/validate_plan_constraints.py
.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py
.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills
diff -qr dddjango/skills/architecture-api /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/architecture-api
```

## 완료 조건

- `architecture-api`의 직접 책임과 handoff 기준이 명확하다.
- 다른 skill과 같은 문제를 서로 다른 기준으로 해결하도록 겹치지 않는다.
- `SKILL.md`는 핵심 절차와 routing 중심이고, 세부 자료는 필요한 때 bundled reference에서 찾을 수 있다.
- source skill과 runtime cache가 동기화된다.
- 검증 명령이 통과한다.
- 리뷰 결과가 Blocker 0, Major 0, 열린 Minor 0이다.
