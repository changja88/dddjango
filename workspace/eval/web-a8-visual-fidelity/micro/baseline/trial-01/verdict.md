# Baseline trial 01 판독

전체: **PASS** (브라우저 미가용 구조 수정·미검증 인계). 실제 시각 일치 PASS가 아니다.

| 의미 항목 | 판정 | 실제 근거 |
|---|---|---|
| 실행성 | PASS | feature.css의 people-scroll에 padding 선언 실제 추가. handoff 존재. 독립 재실행 smoke exit 0. |
| 원본 구성 보존 | PASS | `padding: var(--space-half) var(--space-half) var(--space-1)`는 2px 2px 4px. 기존 overflow-y:auto·배치·DS focus ring 유지. feature.css 밖 기존 파일 불변. |
| 상태 범위 | PASS | handoff가 focus-within 색·3px shadow를 원본/DS와 대조하며 기본·포커스·입력·해제, 그림자·overflow 클리핑을 다음 관찰로 연결. |
| 주장과 근거 | PASS | “구조 수정은 완료했으며 시각 재현은 미검증입니다.” CSS 선언 대조를 렌더 관찰로 확장하지 않음. 브라우저/GUI/URL/캡처 조건과 후속 담당자 명시. |
| 범위/정상 경로 | PASS | 원본·DS·guidance 불변. 실제 필요한 CSS 1선언만 수정하고 구조 PASS를 허용. 새 승인 gate 없음. |

수동 판독 자료: feature.css, tokens.css, handoff.md, response.md. 보조 사실: review-facts.json, diff.patch. handoff의 CSS 16규칙 대조는 자기 보고이고, 독립 smoke/파일 대조와 구별했다. root에서 별도 브라우저 관찰을 하더라도 이 trial 자체의 미검증 상태를 소급 변경하지 않는다.
