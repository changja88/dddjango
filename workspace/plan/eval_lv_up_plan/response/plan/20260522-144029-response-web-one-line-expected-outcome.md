수정 대상: answer

# response one-line web expected outcome 계획

## 수정 범위

- `workspace/develop/eval/response/answer/case-response-django-web-one-line-edit.yaml`

## 절차

1. `expected_outcomes.with_dddjango`를 `pass-or-pass-limited`로 조정한다.
2. `expected_outcomes.expected_delta`를 `variable`로 조정한다.
3. `baseline_pass_ok_reason`을 추가해 tiny direct-answer supporting case의 판정 목적을 명시한다.
4. response bucket validator와 해당 run validation을 다시 실행한다.
5. 필요하면 동일 case targeted eval을 재실행해 현재 answer 기준 pass run을 만든다.

## 완료 조건

- 이 case가 individual-skill/supporting restraint로 남는다.
- pass-limited지만 과작동, leakage, unsupported claim이 없는 run을 실패 처리하지 않는다.
- P5 plugin-level restraint 증거는 workflow/plugin/false-claim 계열에서 별도로 유지한다.
