# P5 목표 프롬프트 - django-implementation-integration

이 문서는 goal 실행용 입력이다. 아래 전체를 그대로 붙여 넣어 사용한다.

```text
unsandboxed targeted eval 실행을 승인한다. public eval prompt, plugin/runtime skill context, workspace-derived eval inputs, model outputs, evaluator/oracle context가 configured model runner로 전송될 수 있음을 이해하고 승인한다. 이 승인을 근거로 sandbox가 Operation not permitted로 막히면 필요한 make eval-one을 escalated/unsandboxed로 요청하고, 승인 요청 후 계속 진행한다.

너는 dddjango 플러그인의 P5 Django implementation 연계 평가를 수행한다.

목표: Django, Django Ninja, Django Web, Python, Clean Code, Test/TDD skill이 함께 쓰이는 구현 시나리오에서 책임 경계와 handoff가 평가로 보장되는지 `평가 -> analysis -> plan -> 수정 -> 재평가` 루프로 닫는다. 종료 기준은 Blocker 0, Major 0, 열린 Minor 0이다.

대상:
- skills: implementation-django, implementation-django-ninja, implementation-django-web, implementation-python, implementation-cleancode, implementation-test, implementation-tdd, architecture-api, architecture-db, workflow-dddjango-subagents
- eval pack: workspace/develop/eval/{response,code,plugin,runtime,source,workflow}/
- eval 분석/계획: workspace/plan/eval_lv_up_plan/<bucket>/{analysis,plan}/

P5 기준:
1. Django ORM/service/migration, Ninja Router/Schema, server-rendered web, Python typing, clean-code review, pytest/TDD가 서로 책임을 침범하지 않는지 평가한다.
2. API 구현은 architecture-api 계약과 implementation-django-ninja adapter 책임을 구분한다.
3. ORM/transaction/migration은 architecture-db/implementation-django 책임과 API/web/test 책임을 구분한다.
4. test/TDD는 테스트 절차와 pytest mechanics를 분리하고, production code skill 평가를 대체하지 않는다.
5. 작은 rename, tiny assertion, one-line web edit 같은 요청에 composite workflow를 과적용하지 않는지 negative/restraint 평가를 포함한다.

절차:
1. response/code/workflow/plugin bucket에서 Django 구현 연계 case를 inventory한다. `bucket / case id / 연결 skill / 수정 여부 / targeted eval 필요 / run id / status` 표를 만든다.
2. P4 direct case와 P5 integration case를 분리한다. 개별 skill 직접 검증만 하는 case를 P5 완료 근거로 세지 않는다.
3. gap을 `case`, `answer`, `evaluator`, `skill`, `reference`, `model-variance` 중 하나로 분류한다.
4. eval 문제는 `workspace/plan/eval_lv_up_plan/<bucket>/analysis/`에 한글 분석을 쓰고 첫 줄은 `수정 대상: ...`로 한다. 같은 파일명으로 `plan/`에 계획을 작성한 뒤 좁게 수정한다.
5. skill/reference 기준이 부족할 때만 해당 lv_up_plan에 후속 분석과 계획을 작성한다.
6. 수정 후 관련 bucket validator를 실행하고 추가/수정 case는 각각 targeted eval을 실행한다.
7. targeted eval이 sandbox/authorization으로 실패하면 goal을 종료하지 말고 사용자에게 명시 승인을 요청한다. 필요한 데이터 전송 위험과 실행 명령을 쓰고, 승인 후 계속한다. pass run 없이 complete 금지. 승인 요청 없이 blocked 금지.
8. eval-all은 P6 전에는 실행하지 않는다.
9. skill-creator 관점 subagent와 독립 integration review subagent를 우선 사용한다. 불가하면 순차 fallback으로 같은 기준을 적용한다.

필수 검증:
- .venv/bin/python -B workspace/scripts/validate_plan_constraints.py
- .venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py
- .venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills
- 관련 bucket마다 .venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket <bucket>
- 추가/수정 case마다 `make eval-one BUCKET=<bucket> CASE=<case-id> TRY_NUMBER=1 SCOPE=targeted TOPIC=<topic> EXTRA_ARGS=--rerun JOBS=1`
- pass run마다 validate_eval_run.py 실행

종료 조건:
- Django 구현 연계 평가가 skill 책임 경계와 handoff를 검증한다.
- 수정 case마다 현재 파일 기준 targeted pass run이 있다.
- public leakage, answer overclaim, evaluator undercheck가 없다.
- 리뷰 결과 Blocker 0, Major 0, 열린 Minor 0이다.
- 최종 응답에 검증표, 수정 파일, analysis/plan, run id/status, 미실행 검증과 사유, 리뷰 결과, Serena 판단을 적는다.
```
