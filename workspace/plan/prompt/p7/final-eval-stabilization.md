# P7 목표 프롬프트 - final-eval-stabilization

이 문서는 goal 실행용 입력이다. 아래 전체를 그대로 붙여 넣어 사용한다.

```text
unsandboxed eval 실행을 승인한다. public eval prompt, plugin/runtime skill context, workspace-derived eval inputs, model outputs, evaluator/oracle context가 configured model runner로 전송될 수 있음을 이해하고 승인한다. 이 승인을 근거로 sandbox가 Operation not permitted로 막히면 필요한 make eval-one 또는 make eval-all을 escalated/unsandboxed로 요청하고, 승인 요청 후 계속 진행한다.

너는 dddjango 플러그인의 P7 최종 평가 실행과 반복 수정을 수행한다.

목표: P6에서 확정한 report 체계를 기준으로 전체 eval-all을 실행하고, 실패를 정해진 수정 대상 기준으로 분류한 뒤 `analysis -> plan -> 수정 -> targeted/bucket 검증 -> 최종 eval-all` 루프로 완료한다. 종료 기준은 최종 eval-all 통과와 Blocker 0, Major 0, 열린 Minor 0이다.

대상:
- plugin: dddjango/skills/
- eval pack: workspace/develop/eval/{response,code,plugin,runtime,source,workflow}/
- eval 분석/계획: workspace/plan/eval_lv_up_plan/<bucket>/{analysis,plan}/
- skill 후속: workspace/plan/skill_lv_up_plan/<skill>/{analysis,plan}/
- reference 후속: workspace/plan/reference_lv_up_plan/<reference-area>/{analysis,plan}/
- etc 후속: workspace/plan/etc_lv_up_plan/<topic>/{analysis,plan}/

절차:
1. 정적 검증을 실행한다: validate_plan_constraints.py, test_validate_plan_constraints.py, validate_skill_docs.py --phase all --skills-dir dddjango/skills, validate_eval_bucket_pack.py.
2. 정적 검증 실패는 원인 분류 후 analysis/plan을 작성하고 좁게 수정한다.
3. 전체 평가를 실행한다: make eval-all TRY_NUMBER=1 SCOPE=full TOPIC=current-baseline EXTRA_ARGS=--rerun JOBS=3.
4. 실패가 있으면 raw output, stderr, evaluator 결과, report, run id를 확인해 원인을 분류한다.
5. 분류값은 `reference`, `skill`, `case`, `answer`, `evaluator`, `runtime-sync`, `report`, `model-variance`, `process`, `cleanup`, `tooling`, `none` 중 하나로 한다.
6. 실패별로 `bucket / case id / 실패 증상 / 원인 분류 / 수정 대상 / 필요한 검증 / run id` 표를 만든다.
7. 분석은 해당 범주의 analysis에 첫 줄 `수정 대상: ...`로 작성하고, 같은 파일명으로 plan을 작성한 뒤 수정한다.
8. 수정은 분류된 대상에만 좁게 적용한다. 매 수정마다 eval-all을 반복하지 말고 targeted eval, bucket validator, bucket eval 중 가장 좁은 검증으로 닫는다.
9. 추가/수정 case의 pass run마다 validate_eval_run.py를 실행한다.
10. 모든 known issue가 닫히면 최종 eval-all을 다시 실행한다.
11. 최종 eval-all 통과 후 HTML report가 최신 최종 run을 가리키는지 확인한다.
12. skill-creator 관점 리뷰와 독립 eval-integrity 리뷰를 수행한다. real subagent가 불가능하면 순차 fallback으로 같은 기준을 적용한다.

권한 처리:
- eval 실행이 sandbox/authorization 문제로 실패하면 goal을 종료하지 않는다.
- 필요한 데이터 전송 위험, 실행 명령, 승인 필요성을 사용자에게 쓰고 승인을 기다린다.
- 승인 후 같은 목표를 계속 진행한다.
- pass evidence 없이 complete 금지. 승인 요청 없이 blocked 금지.

종료 조건:
- 최종 eval-all이 통과한다.
- 모든 bucket report와 최종 HTML report가 최신 run을 가리킨다.
- 실패 원인 분류표에 열린 항목이 없다.
- public leakage, answer overclaim, evaluator undercheck, stale cache, stale report가 없다.
- 리뷰 결과 Blocker 0, Major 0, 열린 Minor 0이다.
- 최종 응답에 전체 run id, bucket별 status, 실패/수정 표, analysis/plan 목록, 검증 명령 결과, 미실행 검증과 사유, 리뷰 결과, Serena 사용 여부를 적는다.
```
