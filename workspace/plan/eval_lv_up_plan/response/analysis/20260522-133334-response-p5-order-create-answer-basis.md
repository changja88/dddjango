수정 대상: answer
리뷰 방식: real-subagent
리뷰 결과: Blocker 0, Major 1, 열린 Minor 0

# response P5 order-create answer basis 분석

## 배경

`case-response-order-create`는 response bucket의 mixed risky-write design case다. 목표는 workflow 실행 평가가 아니라 DDD, DB, API, Django Ninja, Test decision이 같은 주문 invariant로 연결되는지 확인하는 것이다.

## 현재 증거

Answer oracle의 `reference_basis`가 `workspace/develop/eval` 같은 넓은 경로와 `source-reference-audit/SKILL.md`를 포함한다. 또한 workflow role-map을 risky consistency ordering 근거로 든다. Public case는 subagent/workflow 실행을 요구하지 않으므로, durable answer oracle은 owning skill/source references만 근거로 삼는 편이 낫다.

## 원인 분류

원인 분류는 `answer`다. Case와 target behavior는 타당하지만 reference basis가 평가 편의용 broad source와 non-owning source-audit skill을 섞어 P5 direct/mixed response coverage 경계를 흐린다.

## 수정 판단

Broad eval root와 source-reference-audit skill, workflow role-map 근거를 제거하고, DDD/API/DB/Django Ninja/Test owning source와 runtime bundled references만 남긴다. 기준 자체 부족은 보이지 않으므로 skill/reference 후속은 만들지 않는다.

## Subagent 리뷰/순차 fallback

Subagent 리뷰: real-subagent. skill-creator 관점 sidecar가 source-basis 문제를 Major로 보고했고, 메인 판단도 이를 채택한다.

## 검증

- `.venv/bin/python -B workspace/scripts/validate_eval_bucket_pack.py --bucket response`
- `make eval-one BUCKET=response CASE=case-response-order-create TRY_NUMBER=1 SCOPE=targeted TOPIC=response-p5-order-create-answer-basis EXTRA_ARGS=--rerun JOBS=1`
