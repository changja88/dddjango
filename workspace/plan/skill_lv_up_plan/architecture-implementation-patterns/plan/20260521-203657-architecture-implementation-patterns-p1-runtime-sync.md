수정 대상: runtime-sync

# architecture-implementation-patterns P1 runtime sync 계획

## 수정 이유

Source skill은 dedicated source reference 기준으로 갱신됐지만 runtime cache는 이전 provisional/fallback 문서를 유지하고 있다. Runtime cache를 source skill과 동일하게 동기화해야 실제 Codex runtime에서 수정 내용이 반영된다.

## 수정 범위

- `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/architecture-implementation-patterns/SKILL.md`
- `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/architecture-implementation-patterns/agents/openai.yaml`
- `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/architecture-implementation-patterns/references/*.md`

## 수정하지 말아야 할 범위

- Source reference와 source skill 내용은 runtime sync 과정에서 다시 편집하지 않는다.
- 다른 skill cache는 수정하지 않는다.
- eval pack은 수정하지 않는다.

## 작업 체크리스트

- [ ] Source skill directory를 runtime cache skill directory에 복사한다.
- [ ] `diff -qr`로 source/runtime 차이가 사라졌는지 확인한다.
- [ ] validator 세 개를 실행한다.

## 검증 명령

- `diff -qr dddjango/skills/architecture-implementation-patterns /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/architecture-implementation-patterns`
- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`

## 완료 조건

- Source skill과 runtime cache의 `diff -qr` 출력이 없다.
- Runtime-facing skill에서 stale provisional/fallback 문구가 제거된다.
