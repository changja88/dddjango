# P4 목표 프롬프트 - architecture-ddd

이 문서는 goal 실행용 입력이다. 아래 전체를 그대로 붙여 넣어 사용한다.

```text
너는 dddjango 플러그인의 architecture-ddd skill에 대해 P4를 수행한다.

목표: 개별 skill 평가가 이 skill의 목적과 source reference를 정확히 검증하도록 `평가 -> analysis -> plan -> 수정 -> 재평가` 루프를 반복해 Blocker 0, Major 0, 열린 Minor 0으로 닫는다.

대상:
- skill: dddjango/skills/architecture-ddd/
- reference: workspace/reference/architecture-ddd/reference/final.md
- eval pack: workspace/develop/eval/{response,code,plugin,runtime,source,workflow}/
- eval 분석/계획: workspace/plan/eval_lv_up_plan/<bucket>/{analysis,plan}/
- skill 후속: workspace/plan/skill_lv_up_plan/architecture-ddd/
- reference 후속: workspace/plan/reference_lv_up_plan/architecture-ddd/

P4 기준:
1. 관련 case가 subdomain, bounded context, ubiquitous language, aggregate, entity/value object, invariant, domain event/service, use case, consistency boundary 기준을 검증하는지 확인한다.
2. positive/negative case가 사용 조건과 제외 조건을 모두 검증하는지 확인한다.
3. public case가 answer oracle, private 기준, 이전 run finding을 누설하지 않는지 확인한다.
4. answer oracle이 reference보다 과도하거나 부족한 요구를 하지 않는지 확인한다.
5. case, answer, evaluator가 같은 skill 목적을 검증하는지 확인한다.
6. 여러 skill 연계, subagent workflow 자체의 평가는 P5로 넘기고 P4에서는 개별 skill 평가만 닫는다.

절차:
1. SKILL.md, agents/openai.yaml, bundled references, source reference를 읽는다.
2. eval_goal, cases/plugin/*.json, public case, answer, fixture, manual_protocol, workspace/scripts/evaluate_eval_run.py, workspace/scripts/validate_eval_run.py, bucket pack validator 등 evaluator/검증 scripts를 검색해 관련 case를 찾는다. skill 이름만 보지 말고 trigger 용어와 reference 핵심어도 rg로 확인한다.
3. 수정 파일 목록에서 case id를 역산한 뒤 `bucket / case id / public / answer / evaluator 관련성 / 수정 여부 / targeted eval 필요 / run id / status` inventory를 확정한다. 추가/수정한 case와 answer는 모두 targeted eval 필요로 표시한다. 관련 case가 없거나 coverage가 부족하면 Major 이상으로 분류한다.
4. 부족이 있으면 먼저 원인을 `case`, `answer`, `evaluator`, `reference`, `skill`, `model-variance` 중 하나로 분류한다. 수정 없음이면 새 analysis/plan은 만들지 말고 근거를 최종 응답에 남긴다.
5. P4 기본 수정 대상은 case/answer/evaluator다. eval 문제는 `eval_lv_up_plan/<bucket>/analysis/`에 한글 분석을 쓰고, 첫 줄은 `수정 대상: ...`, 파일명은 `YYYYMMDD-HHMMSS-<bucket>-topic.md`로 한다. 같은 파일명으로 `plan/`에 계획을 쓴 뒤 eval 파일만 좁게 수정한다.
6. reference 또는 skill은 eval로 검증할 기준 자체가 부족할 때만 후속 분석/계획을 작성한다. 이때도 한글, 첫 줄 `수정 대상: ...`, `YYYYMMDD-HHMMSS-<target>-topic.md` 파일명을 지킨다.
7. 수정 후 관련 bucket validator를 실행하고, 추가/수정한 모든 case는 각각 `make eval-one BUCKET=<bucket> CASE=<case-id> TRY_NUMBER=1 SCOPE=targeted TOPIC=<topic> EXTRA_ARGS=--rerun JOBS=1`로 확인한다. 실패해도 중단하지 말고 run dir, raw stdout/stderr, RUN_VALIDATION, report를 확인해 원인을 분류한다. authorization이면 먼저 사용자 권한을 요청한다. hard reject 후 repo-side 수정 가능성을 배제한 뒤에만 blocked로 둔다. 같은 요청은 반복하지 않는다. eval-all은 P6 전 반복하지 않는다.
8. 리뷰는 skill-creator 관점 subagent와 독립 subagent를 우선 사용한다. skill-creator 리뷰는 trigger, 목적, reference, progressive disclosure, validation integrity를 각각 판정한다.
9. 리뷰 결과를 Blocker/Major/Minor/Note로 분류하고, 열린 Blocker/Major/Minor가 있으면 다시 수정한다.

필수 검증:
- .venv/bin/python -B workspace/scripts/validate_plan_constraints.py
- .venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py
- .venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills
- 관련 bucket마다 .venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket <bucket>
- 추가/수정한 모든 case 각각의 `make eval-one BUCKET=<bucket> CASE=<case-id> TRY_NUMBER=1 SCOPE=targeted TOPIC=<topic> EXTRA_ARGS=--rerun JOBS=1`와 run id/status 기록

종료 조건:
- 관련 case/answer/evaluator가 reference 기반 개별 skill 목적을 검증한다.
- public case 누설과 answer over/under-claim이 없다.
- 필요한 analysis/plan/수정/targeted 재평가가 끝났다. 추가/수정 case의 pass run이 하나라도 없으면 complete가 아니다. 권한 요청 없이 blocked 금지.
- 리뷰 결과 Blocker 0, Major 0, 열린 Minor 0이다.
- 최종 응답에 case별 검증표(case, 수정 여부, targeted eval 필요, run id, status), 수정 파일, analysis/plan, 미실행 검증과 사유, 리뷰 결과, Serena 판단/사용 여부를 적는다.
```
