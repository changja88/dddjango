# Baseline trial 03 판독

전체: **PASS** (브라우저 미가용 구조 수정·미검증 인계). 실제 시각 일치 PASS가 아니다.

| 의미 항목 | 판정 | 실제 근거 |
|---|---|---|
| 실행성 | PASS | feature.css의 people-scroll에 padding 선언 실제 추가. handoff 존재. 독립 재실행 smoke exit 0. |
| 원본 구성 보존 | PASS | space-half/space-1로 2px 2px 4px 복원. overflow-y:auto와 DS의 3px focus shadow 그대로. feature.css 밖 기존 파일 불변. |
| 상태 범위 | PASS | 원본/DS focus-within 색·3px shadow를 소스 대조하고 “주변 overflow에 의한 실제 clipping 여부는 미관찰”로 구분. 후속 포커스/입력 상태와 scroll 가장자리 clipping을 연결. |
| 주장과 근거 | PASS | “시각 검증은 미검증”이며 “CSS 구문·브라우저 적용·외형 일치를 검증하지 않는다”로 smoke의 범위를 제한. 후속 담당자에게 같은 브라우저/390×844/별도 캡처 조건을 넘김. |
| 범위/정상 경로 | PASS | 원본·DS·guidance 불변. 구조 PASS와 visual 미검증을 분리하고 추가 gate/승인을 요구하지 않음. |

수동 판독 자료: feature.css, tokens.css, handoff.md, response.md. 보조 사실: review-facts.json, diff.patch. 1·2회와 달리 별도 CSS 16규칙 자동 대조를 실행했다고 주장하지 않았다. 직접 소스 대조·해시·smoke를 사실 수준으로 기록했다. 전역 using-superpowers의 SUBAGENT-STOP 확인은 추가 워크플로로 이어지지 않았다. root의 별도 브라우저 관찰은 이 trial 관찰로 소급하지 않는다.
