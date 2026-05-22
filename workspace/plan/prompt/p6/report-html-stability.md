# P6 목표 프롬프트 - report-html-stability

이 문서는 goal 실행용 입력이다. 아래 전체를 그대로 붙여 넣어 사용한다.

```text
너는 dddjango 플러그인의 P6 HTML report 최신성 점검을 수행한다.

목표: 전체 평가 전에 run id, bucket report, latest/latest-valid, 실패 근거 링크가 항상 최신 평가 결과를 정확히 보여주는지 `점검 -> analysis -> plan -> 수정 -> 검증` 루프로 확정한다. 종료 기준은 Blocker 0, Major 0, 열린 Minor 0이다.

대상:
- report/render: workspace/scripts/render_eval_review_html.py 및 관련 report/latest 처리 코드
- eval runs: workspace/develop/eval/{response,code,plugin,runtime,source,workflow}/runs/
- latest/latest-valid: workspace/develop/eval/{response,code,plugin,runtime,source,workflow}/
- eval 분석/계획: workspace/plan/eval_lv_up_plan/<bucket>/{analysis,plan}/
- etc 분석/계획: workspace/plan/etc_lv_up_plan/<topic>/{analysis,plan}/

P6 기준:
1. 최신 run id와 HTML report에 표시된 run id가 일치해야 한다.
2. latest와 latest-valid가 의도한 최신 실행을 가리켜야 한다.
3. report가 bucket별 pass/fail, case별 결과, variant별 차이를 보여줘야 한다.
4. 실패 case에서 raw output, stderr, evaluator 결과, answer-oracle 근거로 추적 가능해야 한다.
5. eval-all이 중간 실패해도 생성된 bucket report와 실패 근거가 유실되지 않아야 한다.
6. 이전 run report를 최신 결과로 오인하게 만드는 stale pointer가 없어야 한다.

절차:
1. 기존 run artifact와 report 생성 코드를 inventory한다. `bucket / latest / latest-valid / 최신 run id / report run id / 문제 여부` 표를 만든다.
2. gap을 `report`, `evaluator`, `tooling`, `process`, `none` 중 하나로 분류한다.
3. 문제가 있으면 해당 analysis에 한글로 기록하고 첫 줄은 `수정 대상: ...`로 한다. 같은 파일명으로 plan을 작성한 뒤 좁게 수정한다.
4. eval report 문제는 `workspace/plan/eval_lv_up_plan/<bucket>/analysis|plan/`에 작성한다. 공통 report/tooling 문제는 `workspace/plan/etc_lv_up_plan/<topic>/analysis|plan/`에 작성한다.
5. 수정 후 관련 report renderer test, validate_eval_run.py, validate_eval_bucket_pack.py를 실행한다.
6. 실제 eval-all은 P7 전까지 실행하지 않는다. 필요한 경우 기존 run artifact 또는 작은 fixture/run artifact로 report 최신성을 검증한다.
7. skill-creator 관점 리뷰와 독립 report/eval-integrity 리뷰를 수행한다. real subagent가 불가능하면 순차 fallback으로 같은 기준을 적용한다.

필수 검증:
- .venv/bin/python -B workspace/scripts/validate_plan_constraints.py
- .venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py
- .venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills
- .venv/bin/python -B workspace/scripts/test_render_eval_review_html.py
- 필요한 bucket의 validate_eval_run.py 또는 validate_eval_bucket_pack.py

종료 조건:
- report/latest/latest-valid 최신성 점검표에 열린 항목이 없다.
- stale report, stale pointer, 누락된 실패 근거 링크가 없다.
- 수정이 있으면 analysis/plan과 검증 결과가 남아 있다.
- 리뷰 결과 Blocker 0, Major 0, 열린 Minor 0이다.
- 최종 응답에 점검표, 수정 파일, analysis/plan, 검증 명령 결과, 미실행 검증과 사유, 리뷰 결과, Serena 사용 여부를 적는다.
```
