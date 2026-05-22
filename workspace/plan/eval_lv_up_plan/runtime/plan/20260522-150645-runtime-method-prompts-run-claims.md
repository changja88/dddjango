수정 대상: case

# runtime method prompts run-claim 수정 계획

## 수정 범위

- `workspace/develop/eval/runtime/cases/plugin/public/case-runtime-baseline-isolation.md`
- `workspace/develop/eval/runtime/cases/plugin/public/case-runtime-private-material.md`
- `workspace/develop/eval/runtime/cases/plugin/public/case-runtime-stale-cache.md`

## 순서

1. method-design 성격의 public prompt에 current/prior run finding 인용 금지를 추가한다.
2. 실행하지 않은 검증은 not-run/unknown으로 남기도록 요구한다.
3. runtime bucket validator를 실행한다.
4. 수정 case targeted eval을 재실행하고 pass run에 `validate_eval_run.py`를 실행한다.

## 완료 조건

- runtime method prompts가 실제 실행 claim 없이 증거 종류, 판정 기준, not-run status를 요구한다.
