수정 대상: answer

# response one-line web restraint scope 계획

## 수정 범위

- `workspace/develop/eval/response/answer/case-response-django-web-one-line-edit.yaml`
- `workspace/scripts/validate_eval_bucket_pack.py`

## 절차

1. one-line web edit case intent에서 P5 direct evidence처럼 보이는 표현을 제거한다.
2. `restraint_scope: individual-skill`로 바꾸고 `p5-plugin-restraint` tag를 제거한다.
3. known restraint scope map에 case id를 추가해 누락을 재발 방지한다.
4. response bucket validator와 unit test를 실행한다.

## 완료 조건

- one-line web edit는 P5 목표의 negative/restraint supporting evidence로 남되 full P5 integration evidence로 세지지 않는다.
- validator가 scope 누락을 잡는다.
