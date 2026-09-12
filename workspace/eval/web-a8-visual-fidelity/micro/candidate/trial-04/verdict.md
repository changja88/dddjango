# Candidate trial 04 판독

전체: **PASS** (브라우저 미가용 구조 수정·미검증 인계). 실제 시각 일치 PASS가 아니다.

| 의미 항목 | 판정 | 실제 근거 |
|---|---|---|
| 실행성 | PASS | people-scroll padding 한 선언 실제 복원. handoff 존재. 독립 재실행 smoke exit 0. |
| 원본 구성 보존 | PASS | 원본의 2px 2px 4px를 기존 tokens로 복원. overflow/DS의 3px focus ring 및 다른 기존 파일 불변. |
| 상태 범위 | PASS | 부모 scroll 구조와 focus 진입·유지·해제를 연결. 3px shadow와 2px 위/옆 여백·overflow에서 생기는 실제 잘림은 양쪽 실제 관찰을 요구. |
| 주장과 근거 | PASS | “잘림이 없거나 외형이 일치한다고 판정하지 않음” 및 전체시각 미검증. 후속 브라우저 담당자/Coordinator·390×844·원본/구현/별도 실제캡처·focus/blur조작을 인계. |
| 범위/정상 경로 | PASS | 원본·DS·guidance 불변. 원본에 없는 filled/disabled/error 상태를 추가하지 않음. 구조 완료와 미검증을 분리하고 추가 승인 질문/gate/영구 테스트·계획 없음. |

수동 판독 자료: feature.css, tokens.css, handoff.md, response.md. 보조 사실: review-facts.json, diff.patch. 대응표의 행 개수가 3·4·5행으로 달라도 semantic 항목은 일관되므로 형식 차이를 실패시키지 않았다.
