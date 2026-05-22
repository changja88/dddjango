수정 대상: answer

# P5 plugin packaging traceability 수정 계획

## 수정 범위

- `workspace/develop/eval/plugin/answer/case-plugin-packaging-sync.yaml`

## 순서

1. `reference_basis`에 marketplace entry와 `plugins/dddjango` symlink/equivalent entry를 추가한다.
2. target behavior와 evidence_required는 현재 요구와 충돌하지 않는지 확인한다.
3. plugin bucket validator를 실행한다.
4. 수정 case targeted eval을 실행하고 pass run에 `validate_eval_run.py`를 실행한다.

## 완료 조건

- answer oracle이 plugin manifest, marketplace entry, symlink/equivalent entry를 모두 source basis로 추적한다.
- public case에는 answer-only material이 노출되지 않는다.
