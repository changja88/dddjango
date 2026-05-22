# P5 목표 프롬프트 - opt-out-and-restraint-flow

이 문서는 goal 실행용 입력이다. 아래 전체를 그대로 붙여 넣어 사용한다.

```text
unsandboxed targeted eval 실행을 승인한다. public eval prompt, plugin/runtime skill context, workspace-derived eval inputs, model outputs, evaluator/oracle context가 configured model runner로 전송될 수 있음을 이해하고 승인한다. 이 승인을 근거로 sandbox가 Operation not permitted로 막히면 필요한 make eval-one을 escalated/unsandboxed로 요청하고, 승인 요청 후 계속 진행한다.

너는 dddjango 플러그인의 P5 opt-out/restraint 연계 평가를 수행한다.

목표: 작은 작업, 단순 답변, 사용자 opt-out, tiny edit에서 workflow/subagent/skill 조합을 과적용하지 않는지 plugin-level 평가로 검증하고 `평가 -> analysis -> plan -> 수정 -> 재평가` 루프로 닫는다. 종료 기준은 Blocker 0, Major 0, 열린 Minor 0이다.

대상:
- skills: workflow-dddjango-subagents, implementation-django, implementation-django-ninja, implementation-django-web, implementation-python, implementation-cleancode, implementation-test, implementation-tdd, architecture-* skills
- eval pack: workspace/develop/eval/{workflow,plugin,response,code,runtime,source}/
- eval 분석/계획: workspace/plan/eval_lv_up_plan/<bucket>/{analysis,plan}/

P5 기준:
1. 단순 rename, tiny assertion, one-line explanation, small CRUD, simple web edit에서 composite workflow를 붙이지 않는지 평가한다.
2. 사용자가 subagent 계획이 필요 없다고 하면 role map, handoff, validation footer를 과하게 붙이지 않는지 평가한다.
3. Direct Answer Mode가 필요한 경우 사용자 출력 형식을 보존하는지 확인한다.
4. 개별 skill negative case가 아니라 plugin-level routing/restraint 연계 문제를 검증하는지 구분한다.
5. public case는 answer oracle, private 기준, 이전 run finding을 누설하지 않는다.

절차:
1. workflow/plugin/response/code bucket에서 opt-out, tiny-restraint, false-claim, simple rename, small edit, direct-answer 관련 case/answer/evaluator를 inventory한다.
2. `bucket / case id / 검증하는 restraint / 수정 여부 / targeted eval 필요 / run id / status` 표를 만든다.
3. P4 개별 skill negative case와 P5 plugin-level restraint case를 분리한다.
4. gap을 `case`, `answer`, `evaluator`, `skill`, `reference`, `model-variance` 중 하나로 분류한다.
5. eval 문제는 `workspace/plan/eval_lv_up_plan/<bucket>/analysis/`에 한글 분석을 쓰고 첫 줄은 `수정 대상: ...`로 한다. 같은 파일명으로 `plan/`을 작성한 뒤 좁게 수정한다.
6. 수정 후 관련 bucket validator를 실행하고 추가/수정 case는 각각 targeted eval을 실행한다.
7. targeted eval이 sandbox/authorization으로 실패하면 goal을 끝내지 말고 사용자에게 명시 승인을 요청한다. 승인 후 계속한다. pass run 없이 complete 금지. 승인 요청 없이 blocked 금지.
8. eval-all은 P6 전에는 실행하지 않는다.
9. skill-creator 관점 subagent와 독립 restraint review subagent를 우선 사용한다. 불가하면 순차 fallback으로 같은 기준을 적용한다.

필수 검증:
- .venv/bin/python -B workspace/scripts/validate_plan_constraints.py
- .venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py
- .venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills
- 관련 bucket마다 .venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket <bucket>
- 추가/수정 case마다 targeted eval pass run
- pass run마다 validate_eval_run.py 실행

종료 조건:
- restraint 평가가 작은 작업과 opt-out에서 플러그인 과작동을 검증한다.
- 수정 case마다 현재 파일 기준 pass run이 있다.
- public leakage, answer overclaim, evaluator undercheck가 없다.
- 리뷰 결과 Blocker 0, Major 0, 열린 Minor 0이다.
- 최종 응답에 검증표, 수정 파일, analysis/plan, run id/status, 미실행 검증과 사유, 리뷰 결과, Serena 판단을 적는다.
```
