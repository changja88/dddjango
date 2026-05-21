# source-reference-audit P1 skill 수정 계획

## 수정 이유

Reference 보강으로 P1 source decision이 명확해졌다. Runtime skill이 이를 충분히 반영하지 않으면 실제 감사 응답에서 absent material, dedicated/provisional source status, DRF guardrail provenance, metadata/cache evidence를 빠뜨릴 수 있다.

## 수정 범위

- `dddjango/skills/source-reference-audit/SKILL.md`
  - source material loading rule 보강
  - runtime provenance rule 보강
  - DRF guardrail audit rule 추가
  - runtime metadata/cache sync rule 보강
  - validation coverage rule에 expected evidence와 first-class dimensions 유지
- `dddjango/skills/source-reference-audit/agents/openai.yaml`
  - `short_description`을 25-64자 guideline 안에서 축약하되 provenance/gap/leakage/boundary scope를 유지

## 수정하지 말아야 할 범위

- `workspace/reference/source-reference-audit/reference/final.md`를 runtime skill에 그대로 복사하지 않는다.
- runtime cache는 source skill 수정 후 별도 runtime-sync analysis/plan에 따라 동기화한다.
- eval files는 수정하지 않는다.

## 작업 체크리스트

- [x] `SKILL.md` Source Loading에 absent supplemental material reporting을 추가한다.
- [x] `SKILL.md` Source Loading 또는 Conflict/Gap Ledger에 dedicated/provisional criteria를 추가한다.
- [x] `SKILL.md`에 DRF guardrail audit source 대조 rule을 추가한다.
- [x] `SKILL.md` runtime metadata/cache sync rule을 보강한다.
- [x] `agents/openai.yaml` short_description을 guideline 안으로 축약한다.
- [x] source skill과 runtime cache 차이를 확인한다.
- [x] runtime-sync analysis/plan을 작성하고 cache를 동기화한다.
- [x] validators를 실행한다.

## 검증 명령

```bash
.venv/bin/python -B workspace/scripts/validate_plan_constraints.py
.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py
.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills
```

## 완료 조건

- Source reference의 P1 decision이 `SKILL.md` runtime procedure에 충분히 반영된다.
- `agents/openai.yaml`이 source reference와 `SKILL.md` 목적에 semantic alignment를 유지하고 `short_description` 길이 guideline을 만족한다.
- source skill과 runtime cache가 diff 없이 일치한다.
- Blocker 0, Major 0, 열린 Minor 0이다.
