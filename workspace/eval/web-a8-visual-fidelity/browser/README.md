# 부모 여백과 focus 링 — 독립 통제 관찰

2026-09-13, Chromium 152.0.7977.83, viewport 390×844. micro/fixture의 원본 HTML/CSS를 같은 새 page에서 렌더했다. `probe.js`의 함수 본문을 Playwright browser_run_code_unsafe의 code 인자로 실행했다. filename 호출의 결과 파싱은 실패해 판정에 쓰지 않았으며 code 인자 재실행의 결과가 `observations.json`이다. 각 기본/focus 상태는 실제 blur/focus 뒤 220ms 기다리고 캡처했다. 캡처에서 caret만 숨겨 점멸 차이를 제외했다. 소유 page는 닫았다.

| 통제 조건 | 입력 x / 폭 | 입력 좌측 중앙 바깥쪽에서 보이는 링 | 관찰 |
|---|---|---|---|
| 원본 padding 2px 2px 4px | 45 / 300px | 2px | 원본 구성에서도 3px 링의 바깥 1px은 부모 경계에서 잘림 |
| padding 누락 0px | 43 / 304px | 0px | 실제 computed shadow는 여전히 3px이나 좌우 외측 링이 모두 잘림 |
| 공간 확보 통제 4px | 47 / 296px | 3px | 링 전체가 보임; 원본과 다른 기하이므로 승인된 구현 해법으로 취급하지 않음 |

`pixel-samples.json`은 각 focus PNG의 입력 좌측 중앙에서 x−4..x−1 네 픽셀을 표준 PNG 디코딩 후 읽은 값이다. 흰 배경은 [255,255,255], 링은 [235,228,225]였다. PNG 자체도 육안 확인했다. overflow-y:auto는 세 경우 모두 computed overflow-x:auto다.

이 관찰은 부모 공간이 자식 효과에 미치는 원인을 분리한다. A8 전체 앱의 수정이나 인수 검증, micro trial 에이전트가 직접 브라우저를 관찰했다는 증거는 아니다. fixture가 보존해야 할 기준은 원본이며, 개선이 필요하면 실제 이탈을 구체적으로 결정해야 한다.
