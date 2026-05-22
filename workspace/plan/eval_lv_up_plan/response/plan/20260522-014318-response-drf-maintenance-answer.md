수정 대상: answer
원인 분류: answer missing

# response DRF maintenance answer 누락 수정 계획

## 수정 파일

- `workspace/develop/eval/response/answer/case-response-django-drf-maintenance.yaml`

## 작업 순서

1. public case와 같은 id의 answer oracle을 추가한다.
2. `reference_basis`에 response eval goal, implementation-django source/runtime reference, source-reference-audit DRF guardrail, DRF maintenance bundled reference를 넣는다.
3. `target_behavior`는 기존 DRF 유지보수 adapter boundary, explicit serializer fields, state transition/service boundary, transaction/side-effect timing을 요구한다.
4. `forbidden`에는 greenfield DRF 추천, serializer/viewset business rule 소유, 강제 Ninja migration, false verification claim을 둔다.
5. `.venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket response`를 실행한다.

## 완료 조건

- response public/answer mismatch가 사라진다.
- 추가 answer가 public leakage 없이 owning skill 목적에 맞는다.
- response bucket validator가 architecture-db P4 검증을 계속 진행할 수 있다.
