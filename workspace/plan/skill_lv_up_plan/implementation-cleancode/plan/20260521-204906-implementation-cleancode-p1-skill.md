# implementation-cleancode P1 skill 수정 계획

## 수정 이유

source reference에 Django/dddjango 경계에서 Fat Model, Fat View, Fat Router/Schema/Template, service dumping ground를 판정하는 기준을 추가했다. runtime skill은 이 source 기준을 충분히 반영해야 하므로 bundled reference와 UI metadata를 보강한다.

## 수정 범위

- `dddjango/skills/implementation-cleancode/SKILL.md`
  - `responsibility.md` 로딩 설명에 Django boundary smell 범위를 추가한다.
  - Runtime Rules에 Fat Model/View/Router 판단 기준과 전문 skill 라우팅 경계를 추가한다.
- `dddjango/skills/implementation-cleancode/references/responsibility.md`
  - framework entrypoint, model, schema/serializer, template, service dumping ground 기준을 추가한다.
- `dddjango/skills/implementation-cleancode/agents/openai.yaml`
  - short description과 default prompt가 Fat View/Router 유지보수성 리뷰를 더 잘 드러내도록 갱신한다.

## 수정하지 말아야 할 범위

- `workspace/reference/**`는 이 skill 계획에서 추가 수정하지 않는다.
- `workspace/develop/eval/**`는 P1에서 직접 고치지 않는다. eval 문제가 발견되면 `workspace/plan/eval_lv_up_plan/<bucket>/analysis/` 후속 대상으로 분류한다.
- 다른 skill의 `SKILL.md`, bundled references, runtime cache는 이 계획에서 수정하지 않는다.
- Django transaction, DB schema, REST contract, aggregate ownership을 clean-code reference에 억지로 넣지 않는다.

## 작업 체크리스트

- [ ] `responsibility.md`에 Django/dddjango framework boundary smell 기준을 압축 추가한다.
- [ ] `SKILL.md` reference loading과 runtime rule을 source 기준에 맞춘다.
- [ ] `agents/openai.yaml` UI metadata를 skill 목적과 일치시킨다.
- [ ] source/runtime cache drift를 확인하고, 필요하면 별도 `runtime-sync` 분석/계획 후 cache를 동기화한다.
- [ ] validators를 실행한다.
- [ ] subagent 또는 sequential fallback 리뷰 결과를 통합해 Blocker 0, Major 0, 열린 Minor 0인지 재평가한다.

## 검증 명령

- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`

## 완료 조건

- `implementation-cleancode` runtime skill이 source reference의 clean-code 기준과 Django/dddjango boundary smell 기준을 충분히 반영한다.
- `SKILL.md`는 여전히 concise하고, 세부 판단 기준은 bundled reference에 있다.
- `agents/openai.yaml`이 SKILL.md 목적과 충돌하지 않는다.
- subagent 또는 sequential fallback 리뷰에서 Blocker 0, Major 0, 열린 Minor 0 상태다.
