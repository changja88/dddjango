# workflow-dddjango-subagents P3 skill 수정 계획

## 수정 이유

P3 기준은 workflow skill이 직접 해결할 coordination 책임과 다른 skill로 넘길 handoff 기준을 명확히 하고, `SKILL.md`는 핵심 절차와 routing 판단만 담으며, 세부 자료는 1단계 bundled reference로 필요한 때 로딩되도록 요구한다.

현재 구조는 전반적으로 충분하지만 source/reference governance와 eval/cache-sync wording이 `source-reference-audit` 책임과 겹쳐 보일 수 있고, DB Agent와 Django Agent의 transaction/migration ownership이 약간 모호하다. 이 두 지점을 좁게 보강한다.

## 수정 범위

- `dddjango/skills/workflow-dddjango-subagents/SKILL.md`
  - DB/Django transaction/migration ownership boundary를 role table 뒤에 명시한다.
  - Source/reference governance, eval traceability, broad cache/provenance audit은 `source-reference-audit`로 넘긴다는 handoff를 명시한다.
  - Workflow-local cache sync report는 유지하되 broader audit ownership과 구분한다.
- `dddjango/skills/workflow-dddjango-subagents/references/role-map.md`
  - DB Agent와 Django Agent의 ownership boundary note를 추가한다.
- `dddjango/skills/workflow-dddjango-subagents/references/integration-checklist.md`
  - Source/runtime boundary, eval follow-up, cache sync report가 workflow-local coordination evidence인지 source-audit/eval-pack ownership인지 구분한다.

## 수정하지 말아야 할 범위

- `dddjango/skills/workflow-dddjango-subagents/` 밖의 skill은 수정하지 않는다.
- `workspace/reference/workflow-dddjango-subagents/reference/final.md`는 이번 skill 수정에서 직접 고치지 않는다. 부족한 source reference 기준은 reference follow-up 분석으로 분류한다.
- Eval case, answer oracle, evaluator, report, generated eval run artifacts는 수정하지 않는다.
- Validator가 요구하는 `SKILL.md` canonical role table, exact sequential fallback sentence, `wait_agent`/`close_agent` result collection rule, `Cache sync report` visibility는 제거하지 않는다.
- `agents/openai.yaml`은 현재 metadata가 P3 기준에 충분하므로 수정하지 않는다.

## 체크리스트

- [x] `SKILL.md`가 500줄 미만을 유지한다.
- [x] Bundled references가 `SKILL.md`에서 1단계 직접 링크로 발견 가능하다.
- [x] Workflow는 coordination/integration을 맡고 source-reference audit은 provenance/cache/eval-traceability audit을 맡는다고 구분된다.
- [x] DB Agent와 Django Agent의 transaction/migration handoff가 명확하다.
- [x] Role table 중복은 제거하고 validator-required runtime summary만 유지하며 exact detail은 `role-map.md`에 둔다.
- [x] Source skill 수정 뒤 runtime-sync 분석/계획을 작성하고 runtime cache를 동기화한다.
- [x] Reference taxonomy gap은 reference analysis/plan으로 분류하고 source reference를 수정해 닫았다.
- [x] 검증 명령이 통과한다.
- [x] 재평가 결과 Blocker 0, Major 0, 열린 Minor 0이다.

## 검증 명령

- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`
- `diff -qr dddjango/skills/workflow-dddjango-subagents /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/workflow-dddjango-subagents`

## 완료 조건

- 직접 책임과 handoff 기준이 명확하다.
- Architecture, implementation, test, source audit, workflow 역할이 서로 침범하지 않는다.
- `SKILL.md`는 핵심 절차 중심이고 500줄 미만이다.
- Bundled references는 모두 1단계 직접 링크로 발견 가능하다.
- 불필요한 중복이나 깊은 reference 연결이 없다.
- Source skill과 runtime cache가 동기화된다.
- 리뷰 결과가 Blocker 0, Major 0, 열린 Minor 0이다.
