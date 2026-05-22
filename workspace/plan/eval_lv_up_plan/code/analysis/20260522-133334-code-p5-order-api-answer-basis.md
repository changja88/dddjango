수정 대상: answer
리뷰 방식: real-subagent
리뷰 결과: Blocker 0, Major 1, 열린 Minor 0

# code P5 order-api answer basis 분석

## 배경

`case-code-order-api`는 code bucket의 idempotent order API 구현 case다. 구현 산출물은 service-owned idempotency, DB consistency, API adapter thinness, Problem Details, replay/conflict tests를 증거로 남겨야 한다.

## 현재 증거

Answer oracle의 `reference_basis`가 broad `workspace/develop/eval`과 `source-reference-audit/SKILL.md`만 추가로 든다. 그러나 target behavior와 consistency observations는 architecture-db, architecture-api, implementation-django, implementation-django-ninja, implementation-test의 owning references에 기대고 있다.

## 원인 분류

원인 분류는 `answer`다. Code case 자체와 deterministic checks는 타당하지만 oracle source basis가 실제 행동 계약의 owning reference를 충분히 드러내지 않는다.

## 수정 판단

Broad eval root와 source-audit skill basis를 제거하고, DDD/API/DB/Django/Ninja/Test owning skill references를 추가한다. Code-backed P5 support case이므로 direct DDD confidence로 과대 계산하지 않는 `case_role`과 `score_interpretation`은 유지한다.

## Subagent 리뷰/순차 fallback

Subagent 리뷰: real-subagent. skill-creator 관점 sidecar가 source-basis 문제를 Major로 보고했고, 메인 판단도 이를 채택한다.

## 검증

- `.venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket code`
- `make eval-one BUCKET=code CASE=case-code-order-api TRY_NUMBER=1 SCOPE=targeted TOPIC=code-p5-order-api-answer-basis EXTRA_ARGS=--rerun JOBS=1`
