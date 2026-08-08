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

## 영구 테스트 입장 정책

`discipline-tdd`가 상세 규칙의 단일 소유자다. 영구 test artifact를
`add/update/move/split/rename/remove/weaken`하거나 의미 보존 재조직하기 전에 다음 행을 확정한다.

| candidate | protected contract/evidence | unique production failure | existing authoritative coverage | decision | owner/path |
|---|---|---|---|---|---|

`decision`은 `add`(독자 실패를 보호할 새 테스트), `update`(승인된 계약 변경에 맞춘 기존 테스트 수정),
`reuse`(boundary가 달라도 같은 제품 failure를 기존 권위 테스트가 잡고 독자 failure가 없음),
`retain`(현행 보호 의미 유지), `remove`(명시적 계약 종료 근거가 있는 exact 기존 대상 제거), `reject`(제품 계약이 아닌 후보),
`pending`(근거·계약·중복 판정 미확정) 중 하나다. `pending`은 G1/G1′과 Phase 2 완료를 막고,
`reuse`·`reject`는 test artifact write가 0이다. `remove`는 명세의 침묵이나 현재 구현과의 불일치만으로
선택하지 않는다. `retain`의 의미 보존 move/split/rename/reorganization은 새 case·assertion·Red를 만들지
않고 전후에 같은 계약과 failure를 보호해야 한다.

허용 대상은 외부 wire·사용자 관찰 상태·보안/규제 계약, application orchestration, 도메인 불변식,
현재 DB 보장, adapter 변환·실패 번역, 별도 사용자 승인 근거 또는 실제 deployed consumer evidence 중
하나가 있는 공개 Python 계약이다. 둘 다 요구하지 않으며 두 근거가 충돌하거나 어느 쪽도 명확하지 않을
때만 `pending`이다. 반면
framework/stdlib 기본 동작, Pydantic validator 배치·오류 `loc`, private/helper/source AST·docstring·slots·
monkeypatch seam, 테스트 도구 호환, import-only availability, quota·coverage·pyramid 복제, migration
mechanics, `.dddjango` 문서 pytest는 그 자체로 자격이 없다. meta/introspection 형식 전체를 금지하지는
않는다. 실제 공개 Python consumer가 의존하는 승인된 field·signature·hierarchy 같은 계약이면 입장 심사로
판정한다.

중복은 계약·boundary·failure mechanism을 함께 비교하되 boundary 차이만으로 `add`하지 않는다. 기존
테스트가 다른 boundary에서도 같은 제품 failure를 잡고 후보가 독자 failure mechanism을 제시하지 못하면
`reuse`다. 상위 테스트에서 발견된 버그를 unit test로 자동 복제하지 않으며, 층이 달라도 독립 failure
mechanism을 보호할 때만 각각 `add`할 수 있다. 이번 실행에서
Red만 위해 만든 import/decorator/skip/loader 비계는 만든 역할이 해당 surface의 첫 Green 직후 제거한다.
