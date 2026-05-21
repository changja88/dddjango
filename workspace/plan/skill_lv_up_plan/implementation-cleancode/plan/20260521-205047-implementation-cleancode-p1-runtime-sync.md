# implementation-cleancode P1 runtime sync 계획

## 수정 이유

`implementation-cleancode` source skill을 수정했으므로 runtime cache가 같은 내용을 제공하도록 동기화해야 한다.

## 수정 범위

- source:
  - `dddjango/skills/implementation-cleancode/SKILL.md`
  - `dddjango/skills/implementation-cleancode/agents/openai.yaml`
  - `dddjango/skills/implementation-cleancode/references/responsibility.md`
- runtime cache:
  - `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-cleancode/SKILL.md`
  - `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-cleancode/agents/openai.yaml`
  - `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-cleancode/references/responsibility.md`

## 수정하지 말아야 할 범위

- 다른 skill의 runtime cache는 수정하지 않는다.
- `workspace/reference/**`와 `workspace/develop/eval/**`는 runtime sync 계획에서 수정하지 않는다.
- runtime cache에 source와 다른 임의 수정을 넣지 않는다.

## 작업 체크리스트

- [ ] source의 변경 파일 3개를 runtime cache에 복사한다.
- [ ] `diff -qr`로 source/runtime 일치를 확인한다.
- [ ] validators를 실행한다.
- [ ] subagent 또는 sequential fallback 리뷰 결과를 최종 재평가에 반영한다.

## 검증 명령

- `diff -qr dddjango/skills/implementation-cleancode /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-cleancode`
- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`

## 완료 조건

- `diff -qr`가 source/runtime 차이를 보고하지 않는다.
- P1 검증 명령이 통과한다.
- runtime sync 관련 Blocker 0, Major 0, 열린 Minor 0 상태다.
