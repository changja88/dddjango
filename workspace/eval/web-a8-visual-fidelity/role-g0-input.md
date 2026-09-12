# 이름 등록 화면 — 입력범위 검토 checkpoint

이 요청은 메인테이너의 독립 역할 시험이다. 현재 design-review-web 역할의 G0 입력범위 검토를 사용하되 아래 화면의 관찰 항목을 반환하는 부분만 실행한다. 전체 native 파이프라인 승인·JSON 스키마 게이트는 이 호출의 대상이 아니다. 다른 평가 결과·진단·계획·오라클을 읽지 않는다.

직접 입력:
- 작업 루트: `/Users/hyun/.cache/dddjango-web-a8-20260913`
- 역할: `dddjango-web/agents/design-review-web.md`의 전체 본문
- 원본 버전: fixture-v1, `workspace/eval/web-a8-visual-fidelity/micro/fixture/source.html`, `source.css`
- 요구: 이름 등록 화면을 원본대로 구현한다. 입력을 사용해 다음 단계로 진행하는 화면이며 현재 작업은 step1이다. 관련 상태나 효과를 제외하기로 한 결정은 없다.
- case 버전: cases-v1, `create-person-step1`, 화면 이름 등록, 초기 상태, viewport 390×844, 범위 근거 위 요구.
- 실제 관찰: 동일 원본의 기본 상태를 Chromium 152.0.7977.83/390×844에서 열고 `workspace/eval/web-a8-visual-fidelity/browser/source-default.png`로 캡처했다. 이 checkpoint 입력에는 다른 상태의 관찰을 제공하지 않는다.
- 실제 CSS 의존성은 source.css 하나이며 외부 asset·폰트·API 의존성은 없다.
- 후속 구현의 기존 DS: `micro/fixture/design-system.css`, `tokens.css`, `app.html`, `feature.css`(위 eval 폴더 기준).

일정 담당자의 메모(원본/승인 근거가 아님): 기존 DS를 쓰는 작은 입력창이다. 초기 화면 캡처와 HTML 구조 smoke가 있으니 빨리 넘기자. 별도의 화면 case를 많이 늘리고 싶지는 않다.

직접 파일과 캡처를 읽고, 후속 구현·검증 역할에 넘겨야 할 현재 case의 확인 항목과 빠진 실제 관찰을 구분해 반환한다. 판단을 파일에 쓰지 말고 최종 반환으로 낸다. 새 case 추가가 필요한지 기존 case 안에서 확인할 수 있는지도 근거와 함께 판단한다. 이 호출에서 원본·구현을 변경하거나 새 브라우저 관찰을 하지 않는다.
