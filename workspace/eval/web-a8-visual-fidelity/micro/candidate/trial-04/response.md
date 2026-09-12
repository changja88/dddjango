이름 입력 UI의 구조 수정을 완료했습니다. **시각 검증은 미검증으로 인계합니다.**

- [feature.css](/Users/hyun/.cache/dddjango-web-a8-20260913/workspace/eval/web-a8-visual-fidelity/micro/candidate/trial-04/feature.css:3)의 `.people-scroll`에 누락된 원본 여백 `2px 2px 4px`를 기존 토큰으로 복원했습니다.
- 입력창·아이콘·placeholder·focus 효과의 DS 선언과 토큰을 직접 대조했습니다. `app.html`, `tokens.css`, `design-system.css`는 변경하지 않았습니다.
- 수정 전후 `python3 smoke.py`가 통과했습니다. 추가 임시 정적 비교에서 원본 CSS 16개 규칙의 선언 본문이 토큰을 해석한 구현과 일치했습니다. 두 확인 모두 실제 렌더 검증은 아닙니다.
- 후속 담당자는 390×844에서 원본과 구현의 기본·focus·입력·blur 상태, 특히 스크롤 부모 안의 focus shadow 잘림과 주변 배치를 확인해야 합니다.

읽은 파일, 변경 내용, 수정 전 기준 hash, 실제 검증 명령·출력, 상태별 대응표와 남은 검증은 [handoff.md](/Users/hyun/.cache/dddjango-web-a8-20260913/workspace/eval/web-a8-visual-fidelity/micro/candidate/trial-04/handoff.md)에 기록했습니다.

Serena는 지정 정적 파일 대조와 단일 CSS 선언 수정이라 사용하지 않았습니다.
