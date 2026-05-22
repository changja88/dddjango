수정 대상: case

# P5 opt-out/restraint workflow 수정 계획

1. `workspace/develop/eval/workflow/cases/plugin/public/case-workflow-opt-out.md`의 질문을 실제 짧은 rename/migration 답변 요청으로 맞춘다.
2. `case-workflow-opt-out.yaml`의 required behavior를 public prompt와 같은 수준으로 유지하고 `restraint_scope: plugin-level`, `p5-plugin-restraint` tag를 추가한다.
3. `case-workflow-tiny-restraint.yaml`에 `workflow-dddjango-subagents/SKILL.md`, `delegation-rules.md` basis와 `direct-answer-mode`, `p5-plugin-restraint`, `restraint_scope: plugin-level`을 추가한다.
4. `case-workflow-design-no-meta-tail.yaml`, `case-workflow-critical-path-delegation-restraint.yaml`, `case-workflow-false-claim.yaml`에 `restraint_scope: plugin-level`과 `p5-plugin-restraint` tag를 추가한다.
5. `workspace/scripts/validate_eval_bucket_pack.py`가 P5/P4 restraint scope를 검사하도록 보강한다.
6. `workspace/scripts/test_validate_eval_bucket_pack.py`에 P5 scope 누락을 잡는 테스트와 P4 individual-skill scope를 받는 테스트를 추가한다.
7. 검증은 workflow bucket validator, 관련 script unit test, 수정 workflow case targeted eval과 `validate_eval_run.py`로 닫는다.
