# implementation-tdd P1 점검 프롬프트

Goal objective:

```text
P1: dddjango:implementation-tdd 스킬의 reference 반영도 점검
```

Goal 사용 규칙:

- Goal 기능에는 위 objective 한 줄만 사용한다.
- 현재 goal 도구 스키마에는 objective 최대 글자 수가 명시되어 있지 않다.
- 운영 기준으로 Goal objective는 80자 이하로 유지한다. 현재 objective 길이는 52자다.
- 세부 절차, 리뷰 등급, 재검토 루프, 종료 조건은 Goal에 넣지 않고 이 프롬프트 본문으로만 처리한다.
- Goal 완료는 이 문서의 종료 조건이 충족된 경우에만 가능하다.

작업 지시:

- 이 문서 전체를 그대로 프롬프트로 사용해 P1 점검을 진행한다.
- Blocker, Major, 열린 Minor가 0개가 될 때까지 재검토한다.
- P1 범위에서는 skill, reference, eval을 바로 수정하지 말고 수정 대상 후보, 후속 분석 문서 위치, 다음 단계만 확정한다.
- 수정 대상 후보가 `none`이 아니면 아래 후속 분석 문서 위치 규칙에 맞춰 분석 문서만 남긴다.
- 개선 계획 문서는 P1 분석을 근거로 별도 계획 단계에서 작성한다.
- 종료 조건 충족 여부를 산출 형식에 맞춰 보고한다.

대상:

- Skill: `dddjango/skills/implementation-tdd/SKILL.md`
- Skill reference: `dddjango/skills/implementation-tdd/references/*.md`
- Source reference: `workspace/reference/implementation-tdd/reference/final.md`
- Plan 기준: `workspace/plan/master_plan.md`의 `P1`, `C-REF`
- 제약 기준: `workspace/plan/constraint_rules.md`

후속 분석 문서 위치:

- `<skill-name>`은 대상 `dddjango/skills/<skill-name>/SKILL.md`의 폴더명과 동일하게 쓴다.
- `reference` 개선 후보는 `workspace/plan/reference_lv_up_plan/<skill-name>/analysis/YYYYMMDD-HHMMSS-<skill-name>-p1-reference.md`에 기록한다.
- `skill` 또는 `runtime-sync` 개선 후보는 `workspace/plan/skill_lv_up_plan/<skill-name>/analysis/YYYYMMDD-HHMMSS-<skill-name>-p1-skill.md`에 기록한다.
- `eval` 개선 후보는 관련 bucket이 확정된 경우 `workspace/plan/eval_lv_up_plan/<bucket>/analysis/YYYYMMDD-HHMMSS-<bucket>-p1-eval.md`에 기록한다.
- `eval` 개선 후보이지만 bucket이 확정되지 않으면 후속 분석 문서를 만들지 않고 `eval 점검 필요 여부`와 `다음 단계`에 bucket 확정 필요를 적는다.
- 수정 대상 후보가 `none`이면 후속 분석 문서는 만들지 않고 산출 형식의 `후속 분석 문서 위치`에 `없음`을 적는다.
- 분석 문서 첫 줄은 `workspace/plan/constraint_rules.md`의 `수정 대상:` 허용 값을 따른다.

진행 절차:

- [ ] `implementation-tdd`가 맡아야 할 목적을 한 문장으로 정리한다.
- [ ] source reference의 핵심 기준을 확인한다.
- [ ] `SKILL.md`의 `description`, `Routing`, `Reference Loading`, `Runtime Rules`가 source reference를 빠뜨리지 않는지 확인한다.
- [ ] test list, failing test first, Red-Green-Refactor, Inside-Out/Outside-In, acceptance/unit loop, boundary case, mock-role 기준이 runtime 규칙으로 충분히 반영됐는지 확인한다.
- [ ] implementation-test, DDD, API, DB, workflow skill과의 handoff 조건이 과하거나 부족하지 않은지 확인한다.
- [ ] reference가 부족한지, skill이 부족한지, eval 점검으로 넘겨야 하는지 분류한다.
- [ ] 독립 리뷰 또는 순차 fallback으로 P1 결론을 재검토한다.
- [ ] real subagent를 사용할 수 있으면 `skill-creator` 관점 리뷰를 별도 subagent에 맡긴다.
- [ ] real subagent를 사용할 수 없으면 `/Users/hyun/.codex/skills/.system/skill-creator/SKILL.md`를 읽고 순차 fallback으로 점검한다.
- [ ] `skill-creator` 관점으로 `SKILL.md` 목적 명확성, trigger description, progressive disclosure, reference 중복/누락, validation integrity를 점검한다.
- [ ] P1 범위에서는 skill, reference, eval을 바로 수정하지 말고 필요한 분석만 지정된 `*_lv_up_plan/<대상>/analysis` 위치에 문서화한다.

리뷰 등급:

- `Blocker`: Goal 수행을 시작하거나 끝낼 수 없게 만드는 누락이다. 예: 기준 reference 위치를 확정할 수 없음, 대상 skill 파일 없음, P1 범위 자체가 불명확함.
- `Major`: P1 결론을 왜곡할 수 있는 문제다. 예: source reference 핵심 기준 누락, 책임 경계 오판, fallback/provisional 상태 과장, 수정 대상 분류 불가.
- `Minor`: P1 결론은 가능하지만 다음 반복에서 혼선을 만들 수 있는 문제다. 예: 표현 모호성, 산출 항목 누락, 후속 계획 위치 불명확.
- `Note`: 수정이 필요 없는 관찰 또는 이후 P2~P4에서 확인할 참고 사항이다.

재검토 루프:

- [ ] `Blocker`와 `Major`는 반드시 0개가 될 때까지 프롬프트 또는 점검 결과를 보완한다.
- [ ] `Minor`는 0개가 될 때까지 정리하는 것을 원칙으로 한다.
- [ ] 다만 P1 범위를 벗어난 `Minor`는 열린 이슈로 남기지 말고 `Note` 또는 다음 단계의 후속 항목으로 내려보낸다.
- [ ] 같은 `Minor`가 두 번 이상 반복되면 프롬프트 자체의 종료 조건이나 산출 형식을 보강한다.

종료 조건:

- [ ] 기준 reference 상태가 `충분`, `개선 필요`, `fallback/provisional 유지` 중 하나로 확정되어 있다.
- [ ] 수정 대상 후보가 `reference`, `skill`, `eval`, `runtime-sync`, `none` 중 하나로 정해져 있다.
- [ ] `Blocker`와 `Major`가 0개다.
- [ ] 열린 `Minor`가 0개다. P1 밖에서 처리할 항목은 `Note` 또는 `다음 단계`에 명시되어 있다.
- [ ] subagent 리뷰를 실행했거나, 실행하지 못한 경우 순차 fallback 사유가 기록되어 있다.
- [ ] `skill-creator` 관점 리뷰를 실행했거나, 실행하지 못한 경우 `skill-creator` SKILL.md 기준 순차 fallback 사유가 기록되어 있다.
- [ ] 다음 단계가 `P2 진행`, `reference 개선 계획`, `skill 개선 계획`, `eval 점검`, `runtime-sync 확인`, `blocker 기록` 중 하나로 정해져 있다.
- [ ] 수정 대상 후보가 `none`이 아니면 후속 분석 문서가 대상별 `analysis/` 폴더 아래에 작성되어 있다.
- [ ] 개선 계획 문서를 P1에서 작성하지 않았다.
- [ ] 실제로 실행하지 않은 검증, 리뷰, subagent 작업을 수행한 것처럼 쓰지 않았다.

산출 형식:

```text
수정 대상 후보:
기준 reference:
reference 상태:
skill 반영도:
책임 경계:
eval 점검 필요 여부:
후속 분석 문서 위치:
다음 단계:
리뷰 방식:
리뷰 결과:
Subagent 리뷰/순차 fallback:
skill-creator 리뷰:
통합 리뷰 결과:
종료 조건 충족 여부:
검증/미검증:
```

