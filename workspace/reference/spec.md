# dddjango Product Spec

이 파일은 `dddjango`의 canonical product spec이다. `workspace/reference/**`의 나머지 문서는 source reference corpus이며, 배포본은 `dddjango/`, Codex 의미 미러는 `codex-dddjango/`에 둔다.

## 현행 계약 테스트 정책

1. 영구 테스트의 오라클은 현재 구현이 아니라 **현재 승인된 요구·설계·지원 계약**이다.
2. Django migration 파일·번호·dependency graph·operation·적용 순서·과거 model state·forward/reverse·DDL 자체를 오라클로 삼는 migration 전용 테스트를 새로 만들거나 새 case·assertion·시나리오로 확장하지 않는다.
3. 과거 구현·종료된 계약·버그 이력만을 보존하는 history-only 테스트는 영구 유지하지 않는다. 과거 버그에서 태어났어도 현재 계약을 검증하면 유효한 회귀 테스트다.
4. 승인된 변경 계약을 직접 단언하거나 변경 코드 경로를 직접 검증하는 **관련 테스트**만 조정한다. 전체 suite 실패는 편집 범위를 넓히는 권한이 아니다.

현재 계약에는 현재 도메인 불변식과 명시적 부재 의무뿐 아니라 지원 중인 구 API·이미 저장된 데이터·발행된 이벤트·보안·개인정보·규제 의무가 포함된다. 새 명세의 침묵은 종료 승인이 아니다. 테스트 삭제·assertion 약화는 G1/G1′에서 해당 의무의 종료와 적용 가능한 support·deprecation/Sunset·rollout·영속 호환성 근거가 명시적으로 승인됐을 때만 허용한다. 불명확하면 `pending`이며 Phase 2 완료를 막는다.

관련 기존 테스트는 현재 계약과 같으면 유지하고, 승인된 기대가 바뀌면 갱신·분리하며, 모든 기대가 명시적으로 종료됐으면 삭제한다. 현행 assertion과 종료 assertion이 섞였으면 현행 보장을 남기고 부분 조정한다. 부재 자체가 계약이 아니면 제거된 동작을 대신하는 404·필드 부재 테스트를 발명하지 않는다.

기존 migration 전용 테스트는 분류만으로 일괄 삭제하지 않는다. 현재 기대가 같으면 그대로 유지하고, 기대가 바뀌면 기존 assertion만 제자리 갱신·축소할 수 있으며, 모든 기대가 종료됐으면 삭제한다. 새 파일·case·migration 시나리오·coverage 확장이 필요하면 테스트를 만들지 않고 검증 공백을 보고한다. 현재 model·ORM·service·API·DB constraint를 검증하는 정상 DB-backed 테스트는 migration history가 오라클이 아니므로 허용한다.

이 정책은 migration 구현·검토·rollout/backfill·이력 보존을 금지하지 않는다. migration boundary, snapshot, receipt, write-once artifact, lock 또는 새 런타임 검사 스크립트를 도입하지 않는다.
