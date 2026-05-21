# P1 목표 프롬프트 - implementation-cleancode

## Goal objective에 넣을 내용

`implementation-cleancode` skill의 source reference 충분성, skill 반영도, runtime sync를 평가하고, 필요한 analysis, 수정 계획, 실제 수정, 재평가를 반복해 Blocker 0, Major 0, 열린 Minor 0 상태로 닫는다.

## Goal prompt에 붙여 넣을 내용

너는 dddjango 플러그인의 `implementation-cleancode` skill에 대해 P1을 수행한다.

P1의 목적은 단순 점검이 아니라 `평가 -> analysis -> plan -> 수정 -> 재평가` 루프를 반복해 skill이 충분한 reference를 정확히 반영하도록 만드는 것이다.

대상:
- skill: `dddjango/skills/implementation-cleancode/`
- source reference: `workspace/reference/implementation-cleancode/reference/final.md`
- reference area: `implementation-cleancode`
- runtime cache: `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-cleancode/`
- skill 분석/계획: `workspace/plan/skill_lv_up_plan/implementation-cleancode/`
- reference 분석/계획: `workspace/plan/reference_lv_up_plan/implementation-cleancode/`

폴더 구조:
- reference 부족 분석: `workspace/plan/reference_lv_up_plan/implementation-cleancode/analysis/`
- reference 수정 계획: `workspace/plan/reference_lv_up_plan/implementation-cleancode/plan/`
- skill 반영 부족 분석: `workspace/plan/skill_lv_up_plan/implementation-cleancode/analysis/`
- skill 수정 계획: `workspace/plan/skill_lv_up_plan/implementation-cleancode/plan/`
- runtime sync 분석/계획: `workspace/plan/skill_lv_up_plan/implementation-cleancode/analysis/`, `workspace/plan/skill_lv_up_plan/implementation-cleancode/plan/`
- eval 문제가 발견되면 P1에서 수정하지 않고 `workspace/plan/eval_lv_up_plan/<bucket>/analysis/` 후속 대상으로 분류한다.

반복 루프:
0. 반드시 `평가 -> analysis -> plan -> 수정 -> 재평가` 순서로 진행한다. 여기서 평가는 실제 eval runner만 뜻하지 않고, P1 기준에 따라 reference, skill, runtime cache를 판정하는 assessment를 포함한다. 실제 targeted eval은 필요할 때 검증 단계에서만 실행한다.
1. source reference가 responsibility separation, naming, function shape, encapsulation, abstraction, SOLID, duplication, error handling, legacy review, fat model/view/router, maintainability 기준을 판단하기에 충분한지 분석한다.
2. reference가 부족하면 `reference_lv_up_plan/implementation-cleancode/analysis/`에 `수정 대상: reference` 분석을 쓰고, 같은 timestamp 파일명으로 `reference_lv_up_plan/implementation-cleancode/plan/`에 개선 계획을 작성한 뒤 `workspace/reference/implementation-cleancode/**`를 수정한다.
3. reference가 충분해진 뒤 `SKILL.md`, `references/**`, `agents/openai.yaml`이 reference를 충분히 반영하는지 분석한다.
4. skill 반영이 부족하면 `skill_lv_up_plan/implementation-cleancode/analysis/`에 `수정 대상: skill` 분석을 쓰고, 같은 timestamp 파일명으로 `skill_lv_up_plan/implementation-cleancode/plan/`에 개선 계획을 작성한 뒤 `dddjango/skills/implementation-cleancode/**`를 수정한다.
5. source skill과 runtime cache가 다르면 `수정 대상: runtime-sync`로 분석/계획을 쓰고 runtime cache sync까지 수행한다.
6. 수정 후 검증하고 같은 기준으로 재평가한다. 남은 문제가 있으면 올바른 `analysis/`와 `plan/` 위치에 문서를 갱신하거나 새로 작성한 뒤 루프를 반복한다.

계획 문서에는 수정 이유, 수정 범위, 수정하지 말아야 할 범위, 작업 체크리스트, 검증 명령, 완료 조건을 포함한다.

리뷰:
- 가능하면 `skill-creator` 관점의 subagent 리뷰와 독립 subagent 리뷰를 수행한다.
- 불가능하면 `/Users/hyun/.codex/skills/.system/skill-creator/SKILL.md`를 읽고 순차 fallback 리뷰를 수행한다.
- 리뷰 결과는 `Blocker`, `Major`, `Minor`, `Note`로 분류한다.
- Blocker, Major, 열린 Minor가 있으면 계획 또는 수정을 보완하고 루프를 반복한다.

검증:
- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`

금지:
- reference 문제가 있는데 skill만 수정해서 덮지 않는다.
- skill 문제가 있는데 reference를 억지로 바꾸지 않는다.
- eval 문제를 P1에서 임의로 고치지 않고 `eval_lv_up_plan` 후속 대상으로 분류한다.
- 실행하지 않은 subagent, validator, eval, Serena 사용을 실행했다고 쓰지 않는다.

종료 조건:
- reference 상태가 충분하다.
- skill이 reference를 충분히 반영한다.
- bundled references와 `agents/openai.yaml`이 skill 목적과 충돌하지 않는다.
- source skill과 runtime cache 동기화 여부가 확인됐다.
- 필요한 평가, analysis, plan, 수정, 재평가 루프가 완료됐다.
- 검증이 통과했다.
- 리뷰 결과가 Blocker 0, Major 0, 열린 Minor 0이다.

최종 응답에는 수정한 대상, 작성한 analysis 문서, 작성한 plan 문서, 실제 수정 파일, 검증 결과, 리뷰 결과, 남은 작업, Serena 사용 여부를 요약한다.
