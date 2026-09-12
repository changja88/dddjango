`feature.css`의 `.people-scroll`에 원본의 `2px 2px 4px` 패딩을 기존 토큰으로 추가했습니다. `app.html`, `tokens.css`, `design-system.css`는 수정하지 않았습니다.

- 수정 전후 `python3 smoke.py` 모두 exit 0.
- 토큰을 치환하여 원본 CSS 16개 블록과 구현 선언의 일치를 정적으로 확인했습니다.
- **실제 렌더와 시각 검증은 미검증입니다.** 후속 담당자가 `390×844`에서 입력 기본·입력값·포커스 상태, 그림자와 스크롤 영역의 클리핑, 화면 배치를 확인해야 합니다.
- 읽은 파일, 변경 내용, 검증 명령·출력, 전후 hash와 남은 검증을 [handoff.md](/Users/hyun/.cache/dddjango-web-a8-20260913/workspace/eval/web-a8-visual-fidelity/micro/baseline/trial-04/handoff.md)에 기록했습니다.

Serena는 원문 확인과 CSS 한 선언 수정이므로 생략했습니다.
