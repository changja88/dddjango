# A8 시안 재현 교정 — 개발 검증 기록

현재 기록 시점: dddjango-web 산문 런타임 구현·전체 검증·최종 적대 구현 리뷰 완료, 커밋·릴리즈 직전. 실제 발행 결과는 정식 릴리즈를 따른다. 이 디렉터리는 과거 실패와 교정 근거를 보존하는 개발 기록이며 사용자 앱의 미처리 목록이 아니다. 이번 범위의 미해결 결함은 없다.

## 수정

원본을 읽고도 부모 여백을 누락한 A8-V1, 브라우저 미실행과 외형 일치 주장이 공존한 A8-V2, focus 상태가 검증 위임에서 빠진 A8-V3를 다뤘다. [진단](diagnosis.md)은 당시 버전·커밋·실행 근거를 보존한다.

정본 6개와 Codex 의미 미러 6개를 수정했다. 기존 스타일 적용 근거를 case·상태별 필수 반환 표로 바꾸고, 관련 부모 배치/여백/overflow와 자식 효과를 원본부터 구현·실제 관찰까지 연결했다. G0에서 확인한 부품 내부 상태를 기존 case에 연결해 설계·코더·브라우저 대행·감수자에게 전달한다. Coordinator는 빠진 상태·미검증·실패를 상위 case의 pass로 합치지 않고, 미검증과 포괄적 matches 주장이 충돌하면 정정·보완을 요구한다.

모든 조상·CSS 속성·pseudo-state의 전수 목록이나 별도 JSON case를 강제하지 않는다. 원본 이미지의 관찰 한계, 등가 CSS, 기존 DS 재사용, 브라우저 미가용·정당한 분리 위임, 데이터/구조 슬라이스의 green을 유지한다. 원본의 2px 여백을 복사했다는 사실로 3px ring 전체가 보인다고 주장하지 않는다.

JSON 스키마·검사기·온톨로지와 실제 사용자 A8 앱은 변경 대상이 아니다. 전체 검사에 필요한 기존 backend manifest 봉인 불일치는 정본 도구로 재발행했다. 이 부수 변경은 봉인과 기계 렌더 사실 2파일이며 backend 런타임 수정이 아니다.

## 절차와 실행 증거

| 단계 | 결과와 근거 |
|---|---|
| 진단 | 실제 1.1.10 A8 native 실행에서 세 누락을 확정. 이미 G2를 통과했다고 확대하지 않음 |
| 계획 적대 검토 | 최초 Important 2건(상태별 결과의 상위 case 수용, 위임·감수·가용 브라우저 시험)을 [계획](../../plan/2026-09-13-web-a8-visual-fidelity.md)에 반영하고 독립 재검토 통과 |
| 지침 micro | [결과](micro/results.md): 기존 5/5, 후보 5/5 PASS. 전부 실제 부모 여백을 보존하고 focus/부모 경계를 정직하게 미검증 인계 |
| G0 상태 발견 | [실제 반환](role-g0-return.md): 기본 case에서 focus·입력/해제·부모 경계의 관찰 부족을 발견. 새 focus case 증설 없이 기존 case 확인 항목으로 연결 |
| Coordinator 인계·수용 | [판정](role-coordinator-decision.md): 합성 미검증/matches 반환 거절, 구조 PASS와 시각 unverified 분리. [요청 원문](role-dispatch.md)을 수정 없이 fresh coder에게 전달 |
| 가용 브라우저 coder | [반환](role-browser-app/handoff.md): 원본·수정 전을 먼저 실제 조작하고 padding 1선언 수정 후 재관찰. 안정 상태 5개와 경계 상세 1개의 최종 원본↔구현 PNG가 byte 동일. 전환은 실제 프레임·이벤트로 별도 관찰 |
| 독립 감수 | [감수 판정](role-review/report.md): 원본과 직접 브라우저 대조해 여백 누락 A는 blocker, 논리 padding 등가 구현 B는 PASS. 원본/B의 4상태 PNG는 byte 동일 |
| CSS 원인 통제 | [독립 관찰](browser/README.md): 원본 2px inset에서는 링 2px, 누락에서는 0px, 4px 공간 통제에서는 3px 노출. 4px은 승인된 구현 해법이 아닌 원인 분리용 통제 |
| 필수 검사 | [검증 기록](verification/result.json): 최종 `make verify` 6/6, exit 0, 293초. strict Claude manifest 검증 통과. 12개 runtime와 봉인 2파일의 검증 hash 보존 |
| 최종 적대 구현 리뷰 | [전체 리뷰](final-review.md): Critical 0 / Important 0, Spec PASS / Quality PASS / ReadyToRelease YES. 기록의 대상 요소 수 12→11 오기는 아래 실행 노트에 정정 이력 보존 |

## 해석과 한계

기존 지침 대조군도 모두 통과했으므로 micro의 성공률 개선이나 실제 A8 native 실패의 재현·해소를 이 결과로 주장하지 않는다. 확인한 것은 후보의 원본 보존·정당한 미검증 인계, 독립 역할 간 상태 전달과 잘못된 pass 거부, 가용 브라우저 실행과 통제 fixture의 재현이다. 전체 native Coordinator 파이프라인·실제 Django 앱·최종 G2·양 런타임 설치 cache 평가를 수행한 결과가 아니다. Claude/Codex 배포 소스의 의미 미러와 reference byte 일치는 별도 검증했다.

실행 경계와 초기 실패는 [실행 노트](execution-notes.md)에 보존한다. 소형 시험의 child raw transcript를 별도로 export할 수 없었으므로 역할 자기 보고와 평가자의 파일 대조·독립 smoke·직접 브라우저 관찰을 구별한다. 원본/구현 파일이나 캡처를 평가자가 고쳐 성공으로 바꾸지 않았다.

배포 대상은 dddjango-web patch 1.1.11이다. 사용자 승인에 따라 검토 완료 후 `make release-web`으로 발행한다. 실제 발행 여부·최종 커밋은 [정식 릴리즈](https://github.com/changja88/dddjango/releases/tag/dddjango-web--v1.1.11)를 따른다.

Serena·Graphify는 워크트리에 opt-in 표식이 없어 사용하지 않았다.
