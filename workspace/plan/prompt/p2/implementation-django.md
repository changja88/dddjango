# P2 목표 프롬프트 - implementation-django

이 문서는 검토 대상이 아니라 goal 실행용 입력이다. goal 실행 시 이 파일 자체를 평가하지 말고, 아래 내용을 실행 지시로 사용한다.

## Goal objective에 넣을 내용

`implementation-django` skill의 `SKILL.md` 목적, trigger, 제외 조건, `agents/openai.yaml` metadata를 점검하고, 필요한 analysis, 수정 계획, 실제 수정, 재평가를 반복해 Blocker 0, Major 0, 열린 Minor 0 상태로 닫는다.

## Goal prompt에 붙여 넣을 내용

너는 dddjango 플러그인의 `implementation-django` skill에 대해 P2를 수행한다.

P2의 목적은 `SKILL.md`가 해당 skill의 목적, 실제 사용 조건, trigger, 제외 조건을 명확히 드러내고 `agents/openai.yaml` metadata와 일치하도록 `평가 -> analysis -> plan -> 수정 -> 재평가` 루프를 완료하는 것이다.

대상:
- skill: `dddjango/skills/implementation-django/`
- source reference: `workspace/reference/implementation-django/reference/final.md`
- runtime cache: `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-django/`
- skill 분석/계획: `workspace/plan/skill_lv_up_plan/implementation-django/`
- reference 후속 분류: `workspace/plan/reference_lv_up_plan/implementation-django/`

P2 점검 기준:
1. 실제 사용자 표현과 사용 예시가 skill 목적과 일치하는지 확인한다.
2. frontmatter `description`에 사용 조건, trigger, 제외 조건이 충분히 들어 있는지 확인한다.
3. 본문에만 숨은 trigger 규칙이 없는지 확인한다.
4. `agents/openai.yaml`의 `display_name`, `short_description`, `default_prompt`가 `SKILL.md`와 어긋나지 않는지 확인한다.
5. `agents/openai.yaml`은 `/Users/hyun/.codex/skills/.system/skill-creator/references/openai_yaml.md` 기준을 반영하고, 명시 요청 없는 optional interface field를 추가하지 않았는지 확인한다.
6. source skill과 runtime cache skill이 같은 내용을 가리키는지 확인한다.

반복 루프:
1. 먼저 `SKILL.md`, `agents/openai.yaml`, source reference, bundled references를 읽고 P2 기준으로 평가한다.
2. `SKILL.md` 목적/trigger/제외 조건/metadata 불일치가 있으면 `workspace/plan/skill_lv_up_plan/implementation-django/analysis/`에 `수정 대상: skill` 분석을 작성한다.
3. 같은 timestamp 파일명으로 `workspace/plan/skill_lv_up_plan/implementation-django/plan/`에 수정 계획을 작성한다. 계획에는 수정 이유, 수정 범위, 수정하지 말아야 할 범위, 체크리스트, 검증 명령, 완료 조건을 포함한다.
4. 계획에 따라 `dddjango/skills/implementation-django/**`만 좁게 수정한다.
5. runtime cache가 다르면 `수정 대상: runtime-sync` 분석/계획을 작성하고 runtime cache sync를 수행한다.
6. reference 자체가 부족하면 P2에서 억지로 skill을 맞추지 말고 `reference_lv_up_plan/implementation-django/analysis/`에 `수정 대상: reference` 후속 분석을 남긴다.
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
- `diff -qr dddjango/skills/implementation-django /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-django`

종료 조건:
- `SKILL.md` 목적, trigger, 제외 조건이 명확하다.
- frontmatter description과 본문이 충돌하지 않는다.
- `agents/openai.yaml`이 `SKILL.md`와 일치한다.
- source skill과 runtime cache 동기화가 확인됐다.
- 필요한 analysis, plan, 수정, 재평가가 완료됐다.
- 검증 통과, 리뷰 결과 Blocker 0, Major 0, 열린 Minor 0이다.

최종 응답에는 수정한 대상, 작성한 analysis/plan 문서, 실제 수정 파일, 검증 결과, 리뷰 결과, 남은 작업, Serena 사용 여부를 요약한다.
