수정 대상: case

# response one-line web temp path 계획

## 수정 범위

- `dddjango/skills/implementation-django-web/SKILL.md`
- `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/implementation-django-web/SKILL.md`

## 절차

1. tiny template text change 규칙에 temporary absolute path 노출 금지를 추가한다.
2. repo-relative plain path 사용을 명시한다.
3. runtime cache에 source skill을 동기화한다.
4. skill docs validator와 response bucket validator를 실행한다.
5. one-line web edit targeted eval을 재실행하고 validate_eval_run을 통과시킨다.

## 완료 조건

- with-ddjango 응답이 `/tmp`, `/private/tmp`, eval workspace root를 사용자 출력에 노출하지 않는다.
- simple web edit 요청에서 workflow/subagent/TDD/DB/API 과작동 없이 짧은 답변을 유지한다.
