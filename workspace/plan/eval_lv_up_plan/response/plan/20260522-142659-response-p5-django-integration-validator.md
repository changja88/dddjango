수정 대상: evaluator

# response P5 Django integration validator 계획

## 수정 범위

- `workspace/scripts/validate_eval_bucket_pack.py`
- `workspace/scripts/test_validate_eval_bucket_pack.py`

## 절차

1. 실패 테스트를 먼저 추가한다.
   - fragmented/tag-only P5 response answer는 reject
   - full API/Ninja, DB/Django, Web/Python, Clean Code, TDD/Test, handoff matrix answer는 accept
2. validator에 response P5 integration helper와 bucket-level coverage requirement를 추가한다.
3. response bucket validator와 unit test를 실행한다.
4. 수정 case는 targeted eval rerun 대상에 남긴다.

## 완료 조건

- response bucket pack validation이 P5 Django implementation integration case를 deterministic하게 강제한다.
- P4 direct skill coverage만으로 P5 integration 완료를 주장할 수 없다.
- 관련 validator가 통과한다.
