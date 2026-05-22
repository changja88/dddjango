수정 대상: skill

# source-reference-audit method prompt와 artifact audit 경계 수정 계획

## 수정 범위

- `dddjango/skills/source-reference-audit/SKILL.md`
- runtime cache의 같은 skill file

## 순서

1. Leakage Evidence Protocol에 method-design prompt와 artifact audit prompt의 reporting boundary를 추가한다.
2. runtime/public wording에서 current-run findings를 절차 답변에 섞지 않도록 문구를 보강한다.
3. skill docs validation과 runtime cache parity diff를 확인한다.
4. 영향을 받은 runtime baseline-isolation targeted eval을 재실행한다.

## 완료 조건

- 방법 설계 답변은 증거 종류와 not-run status를 설명하고, 실행하지 않은 artifact 확인을 run으로 주장하지 않는다.
