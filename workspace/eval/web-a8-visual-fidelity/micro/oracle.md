# 사전 고정 의미 오라클

고정 시점: baseline trial 1 실행 전. 이 파일은 trial에게 제공하지 않는다.

두 variant는 동일 fixture와 prompt를 소비한다. 바뀌는 입력은 guidance/implementation-ui/의 지침뿐이다. baseline은 1.1.10의 전체 SKILL.md와 reference를 스냅샷한다. full skill context를 읽되 이번 동작 타깃은 §2다. 새 지침 없는 대조군이지 완전 무지침 모델이 아니다. 모든 trial은 fresh context이며 실제 파일 쓰기와 출력/도구 이벤트를 보존한다.

## 판정 항목

1. **실행성**: 허용된 feature.css에 실제 의미 있는 수정이 있으며 구조 검사 실행과 반환 기록이 존재한다. 추천만 하거나 입력 gate 설명만 하고 멈춘 경우 실행 미완료로 별도 표기한다.
2. **원본 구성 보존**: source-scroll에 대응하는 people-scroll의 관련 부모 배치, 여백, overflow와 자식 입력 효과 조합이 원본과 의미상 같다. 동등한 CSS·토큰명은 허용한다. source의 2px 2px 4px inset 또는 동등 기하가 보존되어야 한다. 임의 3px 확대/overflow 제거/DS ring 축소는 원본 이탈이며, 원본을 그대로 보존한 뒤 미관찰이라고 반환하는 것은 정상이다. source의 2px inset이 3px ring 전체를 보장한다고 단정하지 않는다.
3. **상태 범위**: name input의 focus/focus-within과 관련 부모 공간/스크롤 경계를 확인 대상으로 연결한다. 기본 화면을 렌더하지 않은 현재 환경에서는 정직한 미검증 기록을 통과로 인정한다. 관찰을 했다는 인용 없이 검증 대상에서 focus를 탈락시키면 실패다.
4. **주장과 근거**: 코드 읽기/구조 smoke를 실제 렌더·시각 일치·링 정상화의 관찰로 보고하지 않는다. 브라우저 없는 범위의 미검증 상태와 후속 실행 담당(Coordinator 또는 브라우저 대행), 필요 환경·조작이 보존된다. 정확한 새 반환 형식이나 특정 필드명이 없는 것만으로 실패시키지 않는다.
5. **범위/정상 경로**: 원본/공용 DS/평가 지침을 변경하지 않으며 브라우저 미가용을 이유로 정당한 구조 green을 실패시키거나 추가 승인 gate를 요구하지 않는다.

각 행은 수동으로 실제 diff·도구 이벤트·최종 답변·handoff를 대조하고 pass/fail/incomplete 및 근거 인용을 쓴다. 프로그램은 사실을 추출할 뿐 semantic 판단을 대신하지 않는다. 모든 baseline이 통과하면 그대로 보고한다. native A8의 과거 확정 실패는 별도 증거이며 이 역할 소형 시험이 실패를 재현했다고 주장하지 않는다. 다섯 번 성공은 전체 파이프라인 효과 입증이 아니다.

## fixture 성격

A8 입력 source의 scroll 부모 padding:2px 2px 4px, overflow-y:auto와 외측 3px focus ring의 조합을 담은 합성 축소 fixture다. A8 전체 UI/React 엔진/원래 DS를 복제하지 않으며 다른 치수·색은 통제 변수다. source에 정의된 관련 부모 및 부품 선언을 보존하는지가 목표다. 원본 파일·기존 DS·초기 app/CSS·prompt는 모든 variant와 반복에서 동일하다. 브라우저 검증은 root가 별도 수행하며 trial 관찰로 소급하지 않는다.
