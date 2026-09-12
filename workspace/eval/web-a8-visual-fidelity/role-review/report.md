# 독립 시각 감수 결과

**구현 A: 시각 통과 불가. 구현 B: 이번 정적 fixture 범위에서 시각 통과 가능.** 현재 `dddjango-web/agents/discipline-reviewer-web.md` 전체와 `implementation-ui` §2·design-evidence 계약을 읽고 적용했다. 원본·각 구현을 직접 렌더하고 조작했으며, 코더의 합성 보고를 시각 증거로 사용하지 않았다.

대상은 `fixture-v1`의 `create-person-step1`, 390×844 CSS px, DPR 1이다. 기본 → 빈 입력 focus → `김하늘` 입력 → Tab으로 버튼에 focus를 옮긴 blur 상태를 원본/A/B 각각 확인했다. 관찰 시각은 2026-09-12T17:08:19Z부터이며, Chromium 152.0.0.0/macOS 컨텍스트에서 실행했다. 구체적으로 승인된 외형 이탈은 없다.

1. **발견 — A / blocker:** 스크롤 부모의 내부 여백 누락으로 기본·focus·input·blur 모두 원본 배치를 보존하지 못했고, focus/input에서는 양옆 포커스 그림자가 원본보다 더 잘린다. 원본은 [source.css:6](source.css)에 `padding: 2px 2px 4px`가 있지만 [variant-a.css:3](variant-a.css)의 `.people-scroll`에는 padding이 없다. 공용 입력의 focus 선언은 [design-system.css:7](design-system.css)에 존재하며 원본 [source.css:11](source.css)과 동일한 3px 그림자로 계산된다. 선언의 존재와 계산된 값이 같아도 부모에 의한 잘림까지 같아지지는 않았다.

   **실제 관찰 근거:** 스크롤 viewport는 세 대상 모두 x=43, y=332, 304×164이며 computed overflow는 양축 `auto`다. 원본 입력 셸은 x=45, y=362, 300×52, A는 x=43, y=360, 304×52다. A의 레이블·아이콘·입력 문구·설명문도 왼쪽/위로 2px 이동한다. [원본 focus](source-focus.png)와 [A focus](a-focus.png), [원본 input](source-input.png)과 [A input](a-input.png)을 직접 열람하여 양옆 shadow 공간이 사라지는 차이를 확인했다. 기본·blur에서도 입력 폭/위치 차이가 유지된다. 그림자가 전부 없어지는 것은 아니며 위아래와 둥근 모서리 일부는 보인다.

   **권고 — 최소 보완:** `variant-a.css:3`의 스크롤 부모에 원본의 상/우/하/좌 2/2/4/2px 여백을 기존 `--space-half`·`--space-1` 토큰으로 연결한다. 이후 동일 네 상태를 재관찰한다. 공용 DS나 focus 토큰 값을 변경할 필요는 없다. 이번 감수에서는 구현을 수정하지 않았다. 승인되지 않은 실제 외형 차이이므로 현행 역할의 시각 게이트 기준에 따라 blocker로 반환한다.

**B — 이번 시각 감수 범위에서 규율 관점 이상 없음.** [variant-b.css:3](variant-b.css)의 `padding-block: var(--space-half) var(--space-1); padding-inline: var(--space-half)`는 현행 문서의 쓰기 방향에서 원본의 물리 shorthand와 같은 2/2/4/2px로 계산된다. 직접 본 기본·focus·input·blur 화면의 배치, 텍스트/아이콘, 색, 둥근 모서리, 포커스 그림자와 잘림, blur 뒤 버튼의 native 파란 focus 표시가 원본과 같았다. 11개 대상 요소에 대해 기록한 rect/style/client/scroll/text의 대조에서도 B는 차이가 없었다. 각 상태를 별도 page에서 새로 생성한 원본/B PNG는 네 쌍 모두 바이트가 동일했다. 이 비교는 실제 캡처 열람을 보강하는 결과이며 코드나 JSON만으로 통과를 정한 것이 아니다. 같은 외형을 만드는 논리 속성 표기를 불필요하게 물리 속성으로 바꾸라고 권고하지 않는다.

| case·대상/조작 상태 | 원본 위치·구성(관련 부모 포함) | 구현 위치·구성 | 실제 수행·관찰 근거 | 결과·차이 또는 미검증 |
|---|---|---|---|---|
| create-person-step1 / A / 기본 | source.css:4–15; dialog 20px padding, scroll 2/2/4/2px·overflow auto, 입력 300×52 | variant-a.css:1–5; scroll padding 0, design-system.css:4–10의 공용 필드/아이콘 | 새 page, CSS 메모리 인라인, setContent; [원본](source-default.png) / [A](a-default.png) | 실패. 입력 x/y가 −2px, 폭 +4px. 레이블·아이콘·설명도 이동 |
| create-person-step1 / A / focus | source.css:6·10–14; 부모 안의 테두리+3px shadow | variant-a.css:3·design-system.css:7; 같은 shadow와 여백 없는 부모 | 빈 입력 click 후 220ms 대기; [원본](source-focus.png) / [A](a-focus.png) | 실패. 배치 차이와 양옆 shadow 추가 잘림 |
| create-person-step1 / A / input | 위와 같음, placeholder 대신 입력값 | 위와 같음 | 실제 locator.fill("김하늘"), input focused 확인; [원본](source-input.png) / [A](a-input.png) | 실패. 입력은 표시되나 배치·잘림 차이 유지 |
| create-person-step1 / A / blur | source.css:10–16; 기본 테두리 복귀, 버튼 native focus | 같은 기본/버튼 스타일, padding 누락 지속 | 실제 keyboard.press("Tab") 후 220ms 대기, active BUTTON 확인; [원본](source-blur.png) / [A](a-blur.png) | 실패. shadow 제거·버튼 focus 동작은 같지만 배치 차이 지속 |
| create-person-step1 / B / 기본 | source.css:4–15; scroll 2/2/4/2px와 자식 구성을 포함 | variant-b.css:1–5; logical padding과 tokens.css:6, 공용 DS | 별도 새 page에서 렌더; [원본](source-default.png) / [B](b-default.png) | 통과. 실제 외형·기록 실측·독립 PNG 일치 |
| create-person-step1 / B / focus | source.css:6·10–14; 부모/테두리/shadow 조합 | variant-b.css:3·design-system.css:6–10·tokens.css:10 | 빈 입력 click 후 220ms 대기; [원본](source-focus.png) / [B](b-focus.png) | 통과. focus 효과와 원본 수준의 잘림까지 일치 |
| create-person-step1 / B / input | 위와 같음, 입력값 표시 | 위와 같음 | 실제 locator.fill("김하늘"); [원본](source-input.png) / [B](b-input.png) | 통과. 입력값과 focus 외형 일치 |
| create-person-step1 / B / blur | source.css:10–16; 기본 입력·focus 버튼 | design-system.css:6–11·variant-b.css:3 | 실제 Tab 후 220ms 대기; [원본](source-blur.png) / [B](b-blur.png) | 통과. 값 유지·shadow 제거·버튼 focus 외형 일치 |

**실제 실행과 코드 확인의 구분.** 브라우저에서는 같은 컨텍스트에 각 대상의 새 page를 하나씩 만들고 `setViewportSize({width:390,height:844})`, 로컬 CSS link의 메모리 인라인 치환, `setContent`, `document.fonts.ready`를 실행했다. 원본은 source.html/source.css, 구현은 app.html/tokens.css/design-system.css와 해당 variant를 사용했다. 원본·구현 파일을 수정하지 않았고 서버나 포트를 열지 않았다. 캡처는 `fullPage:false, caret:"hide", animations:"disabled"`로 각각 독립 생성했다. 실제 focus/fill/Tab 상태와 computed style·DOM 치수·활성 요소·캡처 경로·SHA-256·실행 코드 원문을 [observations.json](observations.json)에 기록했다. 12개 캡처 모두 `tools.view_image`로 열람했다. 코드 확인은 관찰된 차이의 원인과 최소 보완 위치를 찾는 데 사용했다.

세 page의 request·failed request·page error 기록은 모두 빈 목록이다. 문서의 `fonts.status`는 loaded였고 이미지 요소는 0개였다. 외부 폰트/API/media를 사용하지 않는 정적 fixture이므로 raw media 대응·영상 재생은 비적용이다. 산술상 3px shadow 전체가 원본에서 반드시 보인다고 주장하지 않는다. 원본도 좌우 padding은 2px이며, 이 감수는 그 실제 출력의 잘림을 기준으로 비교했다.

**한계와 미실행.** 전체 native Django 구조, 백스톱, HTTP/HTMX swap, API, 버튼 제출/다음 단계, 다른 viewport·브라우저·writing-mode, 160ms transition 중간 프레임은 이번 요청 범위가 아니며 검증하지 않았다. blur는 Tab으로 확인했다. 실제 macOS IME 조합이나 모바일 키보드는 시험하지 않았다. 일반 파이프라인의 design-input/manifest/visual-evidence 게이트를 통과시켰다는 의미가 아니다. 기존 원본↔현재 원본 및 수정 전 구현↔수정 후 구현의 과거 쌍은 제공되지 않았고 이 감수는 변경 작업이 아니므로 수행하지 않았다. 과거 상태나 다른 trial 결과를 읽어 추정하지 않았다. 영향 없는 과거 case 캡처 재사용은 없으며 요구된 네 상태 모두 이번 회차에서 새로 관찰했다.

**도구 한계와 정리.** 첫 브라우저 snippet의 `require`는 미정의 오류, 두 번째의 dynamic import는 `ERR_VM_DYNAMIC_IMPORT_CALLBACK_MISSING` 오류였다. 둘 다 page 생성 전에 실패했고 observations에 보존했다. 기본 파일 읽기 도구로 내용을 읽어 지원되는 page API에 메모리 전달한 세 번째 실행은 성공했다. 새 CLI·자동 승인 옵션·권한 확장·대체 브라우저는 사용하지 않았다. 내가 만든 3개 page는 각각 finally에서 닫았으며 종료 후 tab 목록은 최초 조회에서 보였던 about:blank 한 개만 남았다. 해당 기존 blank tab은 닫지 않았다. 원본·구현 7개 입력 파일의 전후 SHA-256은 모두 같았다. 결과 파일은 이 디렉터리의 report.md, observations.json, 12개 PNG로 한정했다.

Serena와 Graphify는 opt-in이 없고 명시적으로 제외되어 검색·로드·호출·초기화하지 않았다.
