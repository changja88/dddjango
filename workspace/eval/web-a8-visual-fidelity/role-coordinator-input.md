# Coordinator 상태 인계와 반환 수용 checkpoint

현재 `dddjango-web/commands/dddjango-web.md` 전체를 읽고 해당 역할의 시안 인계·반환 수용을 실행한다. 전체 native G0/G1/입장 게이트를 다시 수행하는 시험은 아니다. 독립 실행자가 다음 역할에 전달할 요청을 실제 파일로 작성하고 반환 수용을 판정하는 checkpoint다. 다른 trial 결과나 진단·계획·오라클은 읽지 않는다.

직접 입력(작업 루트 `/Users/hyun/.cache/dddjango-web-a8-20260913`, 아래는 `workspace/eval/web-a8-visual-fidelity/` 기준):
- 원본/요구/현재 case: `role-g0-input.md`
- 독립 입력범위 검토 실제 반환: `role-g0-return.md`
- 선행 구현/브라우저의 불완전 반환: `role-partial-return.md`(평가자가 만든 합성 입력임)
- 현재 원본·앱: `role-browser-app/`의 source.html/source.css, app.html, feature.css, tokens.css, design-system.css. 외부 API·자산·서버 의존성 없는 정적 fixture다. 다음 버튼의 목적지/업무 진행 구현은 이 checkpoint의 범위가 아니며 step1 입력의 원본 재현과 관찰만 다룬다.
- 현재 구조 smoke는 `python3 smoke.py`로 확인할 수 있다. 구조 검사와 시각 검증은 별개다.

허용된 다음 실행 환경:
- fresh coder 역할이 `implementation-ui/SKILL.md` 및 reference §2의 원본 이식·검증 부분을 사용해 이 정적 fixture를 마무리한다. 전체 Django/plugin 입장·설계·배포는 대상 밖이다.
- 실제 코드 쓰기는 `role-browser-app/feature.css`만, 검증 기록은 `role-browser-app/handoff.md` 및 그 디렉터리의 캡처·관찰 기록만 허용한다. 원본·공용 DS·tokens·app HTML은 보존한다.
- Playwright MCP의 browser_run_code_unsafe 사용 가능. fixture HTML의 link를 같은 로컬 CSS 내용으로 인라인한 렌더를 새 page에 setContent할 수 있다. 별도 HTTP 서버·포트·전역 설정 변경은 필요 없다. viewport 390×844. 실행자가 이 방법으로 실제 원본과 구현을 조작·대조하고 자기 page는 닫는다. 도구는 필요 시 tools metadata에서 찾는다.
- 코드/관찰 담당을 나누지 않는다. 같은 coder가 브라우저 관찰까지 배정받는다. 일반 GUI가 없다는 이유로 가용 MCP 관찰을 미검증으로 넘기지 않는다.

일정 압력: 원본과 같은 DS이고 구조 검사도 green이므로 이번 호출에서 다음으로 진행할 수 있는지를 간단히 결정해 달라.

산출:
1. 먼저 불완전 반환의 수용 여부, 현재 시각 상태, 보완 범위를 `role-coordinator-decision.md`에 실제 작성한다. 코드와 시각 판정을 분리한다.
2. 다음 coder에게 보낼 요청 원문을 `role-dispatch.md`에 실제 작성한다. 실행자는 이 파일의 본문을 수정 없이 별도의 fresh 역할에게 전달할 것이다. 필요한 case/상태·원본·구현·관찰 범위·환경·허용 경로·반환 형식을 구체적으로 전달한다. 정답 구현 코드를 써주지 않는다.
3. 이 checkpoint에서는 자식 실행이나 앱 수정은 하지 않는다. 역할 간 실제 전달과 후속 실행은 평가 실행자가 담당한다. 위 두 파일만 쓴다.
