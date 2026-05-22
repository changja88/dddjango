수정 대상: answer

# P5 supporting restraint code 수정 계획

1. `workspace/develop/eval/code/answer/case-code-small-rename.yaml`에 `restraint_scope: supporting-control`을 추가한다.
2. validator의 known scope table에 해당 case를 supporting control로 등록한다.
3. code bucket validator와 `case-code-small-rename` targeted eval을 실행한다.
