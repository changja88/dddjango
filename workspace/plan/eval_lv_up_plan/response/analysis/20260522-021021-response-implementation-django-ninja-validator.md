수정 대상: evaluator

원인 분류: evaluator

문제:

- `validate_eval_bucket_pack.py`는 response bucket에 architecture-api, architecture-db, architecture-implementation-patterns, implementation-cleancode, implementation-django P4 coverage tag set을 강제하지만 implementation-django-ninja 전용 P4 coverage set은 없다.
- 이 상태에서는 case를 추가해도 Router, Schema/ModelSchema, endpoint adapter, auth/permission, filtering/sorting, pagination, Problem Details, OpenAPI, TestClient, DRF-to-Ninja coverage가 빠진 pack을 구조 검증에서 잡지 못한다.

수정 방향:

- response bucket validator에 implementation-django-ninja P4 coverage tag set을 추가한다.
- implementation-django-ninja tag가 붙은 answer는 source reference, SKILL.md, bundled reference를 모두 요구한다.
- target_behavior의 required 항목에는 Router/Schema/Auth/Filter/Pagination/Problem/OpenAPI/TestClient/DRF-to-Ninja 핵심어가 누락되지 않도록 최소 semantic check를 둔다.
- validator unit test를 추가해 coverage tag 누락과 source/runtime basis 누락을 확인한다.

Inventory:

| bucket | case id | public | answer | evaluator 관련성 | 수정 여부 | targeted eval 필요 | run id | status |
|---|---|---|---|---|---|---|---|---|
| response | all response cases | 해당 없음 | 해당 없음 | implementation-django-ninja P4 coverage enforcement 추가 | 예정 | case 수정과 함께 필요 | 미실행 | pending |

리뷰 방식: real-subagent

리뷰 결과: Blocker 1, Major 4, 열린 Minor 1

Subagent 리뷰/순차 fallback: real subagent 리뷰에서 coverage tag 산재 허용, forbidden-only keyword 충족, DRF-to-Ninja answer 우회가 지적됨.

skill-creator 리뷰: evaluator 자체는 skill file은 아니지만 validation integrity 항목에서 Major가 있어 수정한다.
