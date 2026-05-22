# P5 목표 프롬프트 - source-runtime-governance-integration

이 문서는 goal 실행용 입력이다. 아래 전체를 그대로 붙여 넣어 사용한다.

```text
unsandboxed targeted eval 실행을 승인한다. public eval prompt, plugin/runtime skill context, workspace-derived eval inputs, model outputs, evaluator/oracle context가 configured model runner로 전송될 수 있음을 이해하고 승인한다. 이 승인을 근거로 sandbox가 Operation not permitted로 막히면 필요한 make eval-one을 escalated/unsandboxed로 요청하고, 승인 요청 후 계속 진행한다.

너는 dddjango 플러그인의 P5 source/runtime governance 연계 평가를 수행한다.

목표: source-reference-audit가 skill/reference/runtime cache/metadata/eval traceability 문제를 다른 skill workflow와 섞이지 않게 분류하고, 필요한 handoff를 평가가 잡아내는지 `평가 -> analysis -> plan -> 수정 -> 재평가` 루프로 닫는다. 종료 기준은 Blocker 0, Major 0, 열린 Minor 0이다.

대상:
- skills: source-reference-audit, workflow-dddjango-subagents, 모든 dddjango runtime skill
- eval pack: workspace/develop/eval/{source,runtime,plugin,workflow,response,code}/
- eval 분석/계획: workspace/plan/eval_lv_up_plan/<bucket>/{analysis,plan}/
- skill/reference 후속: 필요할 때만 workspace/plan/{skill_lv_up_plan,reference_lv_up_plan}/<name>/

P5 기준:
1. source/reference gap, provenance, bundled reference, agents/openai.yaml, runtime cache sync, package metadata, validation coverage, eval traceability가 source-reference-audit 책임으로 분류되는지 평가한다.
2. workflow-dddjango-subagents는 coordination 중 발견한 governance follow-up을 직접 해결하지 않고 owning follow-up으로 분류하는지 평가한다.
3. runtime cache나 plugin metadata가 stale이면 source skill과 cache path를 명확히 매핑하는지 확인한다.
4. public case가 private source path, answer oracle, prior run finding을 누설하지 않는지 확인한다.
5. P4 개별 source skill 평가와 P5 plugin governance 연계 평가를 분리한다.

절차:
1. source/runtime/plugin/workflow bucket에서 metadata, cache sync, wrong routing, private material, stale cache, missing metadata, trigger routing, packaging sync 관련 case/answer/evaluator를 inventory한다.
2. `bucket / case id / 검증하는 governance 연계 / 수정 여부 / targeted eval 필요 / run id / status` 표를 만든다.
3. gap을 `case`, `answer`, `evaluator`, `skill`, `reference`, `runtime-sync`, `model-variance` 중 하나로 분류한다.
4. eval 문제는 `workspace/plan/eval_lv_up_plan/<bucket>/analysis/`에 한글 분석을 쓰고 첫 줄은 `수정 대상: ...`로 한다. 같은 파일명으로 `plan/`을 작성한 뒤 좁게 수정한다.
5. skill/reference/cache 기준이 부족할 때만 해당 lv_up_plan에 후속 분석과 계획을 작성한다.
6. 수정 후 관련 bucket validator를 실행하고 추가/수정 case는 각각 targeted eval을 실행한다.
7. targeted eval이 sandbox/authorization으로 실패하면 goal을 종료하지 말고 사용자에게 명시 승인을 요청한다. 승인 후 계속한다. pass run 없이 complete 금지. 승인 요청 없이 blocked 금지.
8. eval-all은 P6 전에는 실행하지 않는다.
9. skill-creator 관점 subagent와 독립 source-governance review subagent를 우선 사용한다. 불가하면 순차 fallback을 기록한다.

필수 검증:
- .venv/bin/python -B workspace/scripts/validate_plan_constraints.py
- .venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py
- .venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills
- 관련 bucket마다 .venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket <bucket>
- 추가/수정 case마다 targeted eval pass run
- pass run마다 validate_eval_run.py 실행
- runtime cache를 고쳤다면 source skill과 cache diff 확인

종료 조건:
- governance 평가가 source/reference/runtime/plugin 책임을 구분한다.
- 수정 case마다 현재 파일 기준 pass run이 있다.
- public leakage, answer overclaim, evaluator undercheck가 없다.
- 리뷰 결과 Blocker 0, Major 0, 열린 Minor 0이다.
- 최종 응답에 검증표, 수정 파일, analysis/plan, run id/status, cache sync 상태, 미실행 검증과 사유, 리뷰 결과, Serena 판단을 적는다.
```
