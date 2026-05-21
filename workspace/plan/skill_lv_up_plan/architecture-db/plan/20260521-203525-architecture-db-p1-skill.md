수정 이유: `SKILL.md`의 reference loading은 positive condition은 충분하지만 file-specific negative condition이 약해 불필요한 reference loading을 유도할 수 있다.

작업 ID: 20260521-203525-architecture-db-p1-skill

## 수정 범위

- `dddjango/skills/architecture-db/SKILL.md`의 `Reference Loading` 섹션을 보완한다.
- 각 bundled reference에 대해 읽을 조건과 읽지 않을 조건을 한 문장 안에 명시한다.

## 수정하지 말아야 할 범위

- source reference는 이미 보강했으므로 이 plan에서 다시 수정하지 않는다.
- bundled reference 파일의 세부 내용을 `SKILL.md`에 복사하지 않는다.
- `agents/openai.yaml`은 semantic mismatch가 확인되지 않으면 수정하지 않는다.

## 작업 체크리스트

- [x] `schema-modeling.md` loading 조건에 operational-only 질문에서는 읽지 않는다는 경계를 추가한다.
- [x] `constraints-indexes.md` loading 조건에 transaction-only 질문에서는 읽지 않는다는 경계를 추가한다.
- [x] `transactions-locking.md` loading 조건에 pure modeling/index-only 질문에서는 읽지 않는다는 경계를 추가한다.
- [x] `rollout-constraints.md` loading 조건에 non-operational schema questions에서는 읽지 않는다는 경계를 추가한다.
- [x] runtime cache sync 필요 여부를 재평가한다.

## 검증 명령

- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`
- `diff -qr dddjango/skills/architecture-db /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/architecture-db`

## 완료 조건

- 각 bundled reference의 loading condition과 non-loading boundary가 명확하다.
- `SKILL.md`가 source final을 과장하거나 축소하지 않는다.
- skill validator가 통과한다.
- runtime cache sync plan을 별도로 실행해 source/cache diff가 사라진다.

## 완료 판정

완료. Runtime sync plan을 별도로 작성 및 실행했고, 최종 재평가 결과는 Blocker 0, Major 0, 열린 Minor 0이다.
