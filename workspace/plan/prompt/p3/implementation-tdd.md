# P3 목표 프롬프트 - implementation-tdd

이 문서는 goal 실행용 입력이다. goal 실행 시 이 파일 자체를 평가하지 말고, 아래 내용을 실행 지시로 사용한다.

## Goal objective에 넣을 내용

`implementation-tdd` skill의 책임 경계, 다른 skill로 넘길 handoff 기준, progressive disclosure 구조를 점검하고, 필요한 analysis, 수정 계획, 실제 수정, 재평가를 반복해 Blocker 0, Major 0, 열린 Minor 0 상태로 닫는다.

## Goal prompt에 붙여 넣을 내용

너는 dddjango 플러그인의 `implementation-tdd` skill에 대해 P3를 수행한다.

P3의 목적은 skill 간 책임과 handoff가 겹치지 않고, `SKILL.md`는 핵심 절차만 담으며, 세부 자료는 필요한 때만 직접 연결된 bundled reference로 로딩되도록 `평가 -> analysis -> plan -> 수정 -> 재평가` 루프를 완료하는 것이다.

대상:
- skill: `dddjango/skills/implementation-tdd/`
- source reference: `workspace/reference/implementation-tdd/reference/final.md`
- runtime cache: `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-tdd/`
- skill 분석/계획: `workspace/plan/skill_lv_up_plan/implementation-tdd/`
- reference 후속 분류: `workspace/plan/reference_lv_up_plan/implementation-tdd/`

P3 점검 기준:
1. 이 skill이 직접 해결할 책임과 다른 skill로 넘길 handoff 기준이 명확한지 확인한다.
2. 두 skill 이상이 같은 문제를 서로 다른 기준으로 해결하도록 겹치지 않는지 확인한다.
3. architecture, implementation, test, source audit, workflow 역할이 서로 침범하지 않는지 확인한다.
4. `SKILL.md`는 핵심 절차와 routing 판단만 담고, 세부 규칙은 필요한 때만 references/scripts/assets로 연결되는지 확인한다.
5. `SKILL.md`가 500줄 미만이고, bundled reference는 1단계 직접 링크로 발견 가능한지 확인한다.
6. 같은 정보가 `SKILL.md`와 bundled reference에 중복 저장되어 불일치나 컨텍스트 낭비를 만들지 않는지 확인한다.
7. reference 연결이 깊거나 숨겨져 에이전트가 필요한 자료를 찾지 못하는 구조가 아닌지 확인한다.

반복 루프:
1. `SKILL.md`, `agents/openai.yaml`, source reference, bundled references를 읽고 P3 기준으로 평가한다.
2. 책임 경계, handoff, progressive disclosure, 중복/누락 문제가 있으면 `workspace/plan/skill_lv_up_plan/implementation-tdd/analysis/`에 `수정 대상: skill` 분석을 작성한다.
3. 같은 timestamp 파일명으로 `workspace/plan/skill_lv_up_plan/implementation-tdd/plan/`에 수정 계획을 작성한다. 계획에는 수정 이유, 수정 범위, 수정하지 말아야 할 범위, 체크리스트, 검증 명령, 완료 조건을 포함한다.
4. 계획에 따라 `dddjango/skills/implementation-tdd/**`만 좁게 수정한다.
5. runtime cache가 source skill과 다르면 `수정 대상: runtime-sync` 분석/계획을 작성하고 runtime cache sync를 수행한다.
6. source reference 자체의 경계 기준이 부족하면 skill을 억지로 고치지 말고 `reference_lv_up_plan/implementation-tdd/analysis/`에 `수정 대상: reference` 후속 분석을 남긴다.
7. 수정 후 같은 기준으로 재평가하고, 남은 Blocker/Major/열린 Minor가 있으면 루프를 반복한다.

리뷰:
- 가능하면 `skill-creator` 관점 subagent 리뷰와 독립 subagent 리뷰를 수행한다.
- 불가능하면 `/Users/hyun/.codex/skills/.system/skill-creator/SKILL.md`를 읽고 순차 fallback 리뷰를 수행한다.
- 리뷰 결과는 `Blocker`, `Major`, `Minor`, `Note`로 분류한다.
- 열린 Blocker, Major, Minor가 있으면 계획 또는 수정을 보완한다.

검증:
- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`
- `diff -qr dddjango/skills/implementation-tdd /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-tdd`

종료 조건:
- 직접 책임과 handoff 기준이 명확하다.
- 다른 skill과 책임이 충돌하거나 중복되지 않는다.
- `SKILL.md`는 핵심 절차 중심이고 bundled resources는 필요한 때 발견 가능하다.
- 불필요한 중복과 깊은 reference 연결이 없다.
- source skill과 runtime cache 동기화가 확인됐다.
- 필요한 analysis, plan, 수정, 재평가가 완료됐다.
- 검증 통과, 리뷰 결과 Blocker 0, Major 0, 열린 Minor 0이다.

최종 응답에는 수정한 대상, 작성한 analysis/plan 문서, 실제 수정 파일, 검증 결과, 리뷰 결과, 남은 작업, Serena 사용 여부를 요약한다.
