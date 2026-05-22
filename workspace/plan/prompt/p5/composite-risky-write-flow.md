# P5 목표 프롬프트 - composite-risky-write-flow

이 문서는 goal 실행용 입력이다. 아래 전체를 그대로 붙여 넣어 사용한다.

```text
unsandboxed targeted eval 실행을 승인한다. public eval prompt, plugin/runtime skill context, workspace-derived eval inputs, model outputs, evaluator/oracle context가 configured model runner로 전송될 수 있음을 이해하고 승인한다. 이 승인을 근거로 sandbox가 Operation not permitted로 막히면 필요한 make eval-one을 escalated/unsandboxed로 요청하고, 승인 요청 후 계속 진행한다.

너는 dddjango 플러그인의 P5 composite/risky-write 연계 평가를 수행한다.

목표: 여러 skill이 함께 필요한 risky write 시나리오에서 DDD, DB, API, Django, Test, Review 책임 분해와 handoff가 올바르게 평가되는지 `평가 -> analysis -> plan -> 수정 -> 재평가` 루프로 닫는다. 종료 기준은 Blocker 0, Major 0, 열린 Minor 0이다.

대상:
- skills: architecture-ddd, architecture-db, architecture-api, architecture-implementation-patterns, implementation-django, implementation-django-ninja, implementation-tdd, implementation-test, implementation-cleancode, workflow-dddjango-subagents
- eval pack: workspace/develop/eval/{response,code,plugin,runtime,source,workflow}/
- eval 분석/계획: workspace/plan/eval_lv_up_plan/<bucket>/{analysis,plan}/
- skill/reference 후속: 필요할 때만 workspace/plan/{skill_lv_up_plan,reference_lv_up_plan}/<name>/

P5 기준:
1. 평가가 단일 skill 품질이 아니라 복합 시나리오의 역할 분해, handoff, integration owner를 검증해야 한다.
2. risky write는 aggregate invariant, transaction owner, locking/isolation, uniqueness/idempotency storage, Idempotency-Key, side-effect timing, retry, concurrency/integration test를 함께 본다.
3. public case는 answer oracle, private 평가 기준, 이전 run finding을 누설하지 않는다.
4. answer는 reference보다 과도한 구조를 강제하지 않고, skill 간 책임을 흐리지 않는다.
5. workflow case가 개별 skill 직접 평가를 중복하지 않도록 P4 direct coverage와 P5 integration coverage를 구분한다.

절차:
1. workflow, response, code bucket에서 주문/예약/결제/재고/환불/권한/ledger, risky-write, idempotency, transaction, outbox, concurrency 관련 case/answer/evaluator를 inventory한다.
2. `bucket / case id / 검증하는 연계 / 수정 여부 / targeted eval 필요 / run id / status` 표를 만든다. 추가/수정한 case/answer/evaluator는 모두 targeted eval 필요로 표시한다.
3. gap을 `case`, `answer`, `evaluator`, `skill`, `reference`, `model-variance` 중 하나로 먼저 분류한다.
4. eval 문제는 `workspace/plan/eval_lv_up_plan/<bucket>/analysis/`에 한글 분석을 쓰고 첫 줄은 `수정 대상: ...`로 한다. 같은 파일명으로 `plan/`에 계획을 쓴 뒤 좁게 수정한다.
5. 기준 자체가 부족할 때만 skill/reference 후속 분석과 계획을 작성한다.
6. 수정 후 관련 bucket validator를 실행하고, 추가/수정 case는 각각 `make eval-one BUCKET=<bucket> CASE=<case-id> TRY_NUMBER=1 SCOPE=targeted TOPIC=<topic> EXTRA_ARGS=--rerun JOBS=1`로 확인한다.
7. targeted eval이 sandbox/authorization으로 실패하면 goal을 끝내지 말고 사용자에게 필요한 명시 승인을 요청한다. 승인이 필요하면 사유와 명령을 제시하고 계속 진행한다. pass run 없이 complete 금지. 승인 요청 없이 blocked 금지.
8. eval-all은 P6 전에는 실행하지 않는다.
9. skill-creator 관점 subagent와 독립 workflow review subagent를 우선 사용한다. 불가하면 순차 fallback으로 같은 기준을 적용하고 실제 실행 여부를 정직하게 기록한다.

필수 검증:
- .venv/bin/python -B workspace/scripts/validate_plan_constraints.py
- .venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py
- .venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills
- 관련 bucket마다 .venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket <bucket>
- 추가/수정한 모든 case의 targeted eval pass run과 validate_eval_run.py 확인

종료 조건:
- P5 risky-write 연계 case가 책임 분해와 handoff를 검증한다.
- 수정 case마다 현재 파일 기준 pass run이 있다.
- public leakage, answer overclaim, evaluator undercheck가 없다.
- 리뷰 결과 Blocker 0, Major 0, 열린 Minor 0이다.
- 최종 응답에 검증표, 수정 파일, analysis/plan, run id/status, 미실행 검증과 사유, 리뷰 결과, Serena 판단을 적는다.
```
