수정 대상: answer

# P5 opt-out/restraint plugin routing 수정 계획

1. `workspace/develop/eval/plugin/answer/case-plugin-trigger-routing.yaml`의 required behavior에 opt-out, tiny edit, Direct Answer Mode, false claim refusal, no meta-tail restraint가 frontmatter/routing boundary에서 드러나는지 확인하는 항목을 추가한다.
2. 같은 answer에 `restraint_scope: plugin-level`과 `p5-plugin-restraint` coverage tag를 추가한다.
3. validator가 plugin bucket에서 P5 restraint tag를 요구하도록 보강한다.
4. plugin bucket validator와 `case-plugin-trigger-routing` targeted eval을 실행한다.
