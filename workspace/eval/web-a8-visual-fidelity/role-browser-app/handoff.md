# 이름 등록 step1 — fresh coder 구현·브라우저 관찰 반환

이 독립 checkpoint의 `create-person-step1`에서 요청된 초기 화면·입력 포커스·진입/해제 전환·부모 경계·입력값 유지·다음 버튼 접근/활성화를 원본과 직접 대조했다. 수정 전에는 부모 여백 누락으로 입력의 위치·폭과 그림자 잘림이 원본과 달랐다. `feature.css:3`의 여백 선언 하나를 추가한 후 모든 상태를 다시 관찰했으며 이 범위에서 남은 외형 차이를 발견하지 못했다. **구조 smoke는 PASS이고, 아래 시각 판정은 이 coder의 직접 관찰 결과다. native G0/G1/G2, JSON inputs/visual 게이트 또는 독립 감사 통과를 주장하지 않는다.**

기준은 `fixture-v1` / `cases-v1`, case는 `create-person-step1` 하나, viewport는 **390×844**다. 아래 상대 경로는 모두 `/Users/hyun/.cache/dddjango-web-a8-20260913/workspace/eval/web-a8-visual-fidelity/role-browser-app` 기준이다.

## 변경과 코드 검사

실제 코드 변경 파일은 **`feature.css` 한 개**다. `.people-scroll`에 다음 선언을 추가했다.

```css
padding: var(--space-half) var(--space-half) var(--space-1);
```

이는 기존 `tokens.css:6`의 2px·4px 토큰을 소비해 `source.css:6`의 `padding: 2px 2px 4px`를 재현한다. 원본과 기존 DS에 이미 같은 focus 테두리·그림자·160ms ease 전환이 연결되어 있으므로 DS나 토큰 변경은 필요하지 않았다. 수정 전 `feature.css` 전체는 **첫 편집 전에** `observations-before.json.before_feature_css`에 보존했다. 이 JSON의 `first_code_edit_performed: false`는 당시 기준 스냅샷이다.

작업 디렉터리:
`/Users/hyun/.cache/dddjango-web-a8-20260913/workspace/eval/web-a8-visual-fidelity/role-browser-app`

실제 명령은 수정 전과 수정 후 각각 `python3 smoke.py`였고, 둘 다 **exit 0**였다. stdout 원문은 같다.

```text
PASS: HTML id uniqueness and stylesheet wiring only; no render or visual assertions
```

이 결과는 HTML ID 유일성·입력 ID·stylesheet 순서·CSS 파일 존재에 한정한다. 시각 검증으로 사용하지 않았다. 수정 전 출력은 `observations-before.json`, 수정 후 도구 반환의 exit/output은 `verification.json.structureSmoke`에 보존했다.

`python3 - <<'PY'`에서 보존된 수정 전 CSS와 현재 CSS를 `difflib.unified_diff`로 비교했다(exit 0). 출력의 변경은 위 padding 한 선언뿐이었다. 이어 같은 방식의 Python SHA-256 대조를 실행해 다음 stdout을 확인했다(exit 0).

```text
PASS: source.html, source.css, app.html, tokens.css, design-system.css, smoke.py unchanged by SHA-256
READ: observations-before.json; valid JSON
READ: browser-observations-before.json; valid JSON
READ: browser-observations-after.json; valid JSON
READ: capture-comparisons.json; valid JSON
READ: verification.json; valid JSON
```

원본·공용 파일·HTML·smoke 보존을 수정 전후 SHA-256으로 확인했다. 코드 SHA-256은 아래와 같다.

| 파일 | 수정 전 → 수정 후 |
|---|---|
| source.html | `269d9114a7ffcd135d3fb0f1b18824f511d4b654977f439213f9551005368090` 유지 |
| source.css | `0cf2a17eb473b31c24472a5a24fea654e68fd7626b0d9b0e5e0122b19d7ffd8b` 유지 |
| app.html | `7c101e70043c821bda66dfe8f42b9ace2f2da28b44ef6af42e034f1cf0ee86c3` 유지 |
| tokens.css | `c075ad5a4834a6a801b694e4fcdec255a3b897e13e26e8ed13cceb36483f639c` 유지 |
| design-system.css | `eac39358865cb1f01add4c38f4300735ad03eb29fb461394bb6814f0a999858f` 유지 |
| smoke.py | `85be8fb63c6370cad01069a0ca9659a273bb42f2e036eb2357ac402ae01a807c` 유지 |
| feature.css | `30b7549f1d4ef1a8e6f59d325239cc4b343adea1bedaac88e2f5200922dffb2d` → `1f237383d45e916d55e79bced177f7aa60bdfe2a532019ca065bf2db066db61e` |

## 실제 브라우저 실행

같은 coder가 **Playwright MCP `mcp__playwright__browser_run_code_unsafe`**를 사용했다. 관찰 브라우저는 **Chromium 152.0.7977.83**, 실측 viewport **390×844**, DPR **1**이었다. 관찰 user agent는 `Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36`였다. UA의 축약 버전과 `browser().version()` 반환을 구별한다.

기존 사용자 page를 사용하지 않고 각 관찰마다 `page.context().newPage()`로 생성했다. `setViewportSize({width:390,height:844})`, `bringToFront()`, `setContent(...,{waitUntil:"load"})`, `document.fonts.ready` 대기 후 관찰했다. URL은 메모리 렌더의 `about:blank`다. 실제 파일을 읽어 원본의 source.css link만 동일 CSS 내용의 style로 치환했고, 구현은 tokens.css → design-system.css → feature.css 순서를 그대로 유지했다. 이 치환은 메모리 HTML에만 적용했다. 원본/구현 HTML 파일·외부 서버·포트·설정은 변경하지 않았다.

각 page에서 기본 전체 캡처 → `locator("#person-name").click()` → 빈 입력 focus → `fill("김민수")` → `keyboard.press("Tab")`으로 다음 버튼 focus → `keyboard.press("Enter")` 활성화를 실행했다. focus 전후에는 requestAnimationFrame으로 550ms 이상 실제 프레임의 최종 borderColor·boxShadow·활성 요소·CSS animation currentTime/progress를 기록했다. transitionrun/start/end 및 focusin/out 이벤트도 함께 기록했다. 캡처에는 `animations:"allow"`를 사용해 전환을 멈추거나 강제 종료하지 않았다. `caret:"hide"`는 캡처의 깜박임을 없애기 위한 옵션이며 입력값·포커스 동작은 유지했다.

첫 편집 전에 `source-current-*`와 `implementation-before-*`의 모든 상태를 생성·직접 열람했다. 그 후 CSS를 수정했다. 수정 후에는 변경하지 않은 원본도 새 page에서 다시 렌더해 `source-current-post-*`와 `implementation-after-*` 전체 상태를 생성하고 직접 열람했다. 원본 이전 관찰을 수정 후 직접 대조의 대체물로 사용하지 않았다.

## 스타일 적용 근거 표

모든 행의 case는 `create-person-step1`, viewport는 390×844다. `browser-observations-before.json`은 첫 편집 전 원본/구현 2개, `browser-observations-after.json`은 수정 후 현재 원본/최종 구현 2개의 실제 관찰 원문이다.

| case·대상/조작 상태 | 원본 위치·구성(관련 부모 포함) | 구현 위치·구성 | 실제 수행·관찰 근거 | 결과·차이 또는 미검증 사유/다음 실행자·필요 조건 |
|---|---|---|---|---|
| 초기 빈 입력·전체 화면 | `source.html:3`, `source.css:3–16`. body grid 가운데 배치, dialog 344×316/padding20/gap20/radius24, h1 20px/28px. scroll flex column/gap24/min-height0/overflow-y:auto/padding2 2 4, step gap24, field gap8. input 높이52/radius16/padding0 14/gap10, 원형 장식18px, 라벨·안내13px/20px, 버튼44px/radius14. | `app.html:3`, `feature.css:1–5`, `design-system.css:1–11`, `tokens.css:2–11`. people-dialog/people-scroll/people-step, ds-field/label/input/icon/button가 대응한다. dialog·spacing·type·color·border·radius 토큰을 소비하며 변경 후 scroll padding도 기존 토큰으로 대응한다. | 같은 MCP 메모리 렌더의 `*-default.png` 4개를 직접 열람. 양 JSON의 `states.default` 전체 요소 rect/styles·문구 확인. 후 원본↔후 구현 전체 PNG 바이트도 동일(`capture-comparisons.json`). | 수정 전 입력은 (43,360) 304×52, 후 원본·구현은 (45,362) 300×52. 라벨·안내문도 +2px,+2px 이동해 원본과 일치. 최종 카드 (23,264) 344×316, 제목 (43,284), 버튼 (43,516) 304×44가 일치했다. 타이포·색·배경·장식·문구·화면 경계에도 남은 차이를 발견하지 못함. |
| 빈 입력 포커스 | `source.css:10–14`, source-field > source-input > icon/input. 입력 자체 border0/outline:none, 래퍼 `:focus-within`에서 border #8f675b와 3px/rgba(.18) 그림자. source-scroll/step 안에 배치된다. | `design-system.css:6–10`, ds-field > ds-input > ds-icon/input. border는 `--accent`, 그림자는 `--input-focus-shadow`, 크기·gap·padding은 기존 input 토큰. 부모는 수정된 `feature.css:3–4`. | `#person-name` 실제 클릭, `states.emptyFocused`, `*-empty-focused.png` 4개 및 `*-focus-boundary-detail.png` 4개 직접 열람. 최종 적용 border `rgb(143,103,91)`, shadow `rgba(143,103,91,0.18) 0px 0px 0px 3px`를 렌더와 함께 관찰. | 원본/구현 모두 입력에 focus가 있고 래퍼의 테두리·그림자가 나타남. 최종 원본↔구현 full/detail PNG 동일. DS 선언값만으로 판정하지 않음. |
| 포커스 진입·해제 전환 | `source.css:10–11`: border-color·box-shadow 160ms ease; 초기 #d5d1c7/none ↔ focus #8f675b/3px rgba(.18). 관련 부모는 위 scroll/step/field. | `design-system.css:6–7`, `tokens.css:10`의 `--duration-fast:160ms`, `--input-focus-shadow`. 공용 선언은 보존. | 각 관찰의 `transitions.focusEntry/focusExit`에 실제 click/Tab 동안 각각 34 rAF 샘플과 transition 이벤트. `*-focus-entry-live.png`·`*-focus-exit-live.png` 8개와 안정 상태 캡처를 직접 열람. 후 원본/구현 진입의 CSS animation currentTime 50ms에서 progress .5375, border rgb(175,152,141), 그림자 spread 1.6125px를 각각 관찰. | 진입 중 0→약.305→1.6125→2.7041→3px의 변화 및 해제 중 3→중간값→none을 관찰. 양 방향의 4개 border-color와 box-shadow transitionend가 `elapsedTime:0.16` 반환. 160ms ease는 선언값, currentTime/progress/색 변화는 브라우저 관찰값이다. rAF·이벤트 전달은 약 16.7ms 단위이며 벽시계상 샘플 시각은 근사다. live PNG는 서로 같은 ms에 촬영하지 않아 프레임 단위 동일성은 주장하지 않지만 진행·종결 상태 재현을 확인했다. |
| 부모 경계 안의 입력 효과 | `source.css:6–11`: source-scroll (43,332) 304×164, padding2 2 4, computed overflow-x/y:auto; source-step (45,334) 300×124, field 300×80, input (45,362) 300×52. 부모 padding/overflow와 자식3px 그림자 조합. | `feature.css:3–4` people-scroll/step + `design-system.css:4,6–7` ds-field/input. 수정 전 scroll padding0, 변경 후 2 2 4. 후 rect와 overflow는 원본과 같음. | focus full/detail 캡처의 상·하·좌·우를 직접 대조했고 JSON의 scrollWidth/clientWidth=304, scrollHeight/clientHeight=164 및 실제 좌표도 함께 확인. `source-current-post-focus-boundary-detail.png` ↔ `implementation-after-focus-boundary-detail.png` PNG 동일. | 수정 전에는 좌우 경계와 래퍼가 붙어 측면 그림자가 잘렸음. 변경 후 원본과 같은 2px 측면 공간이 생김. 원본도 3px spread 전체를 좌우에 보이는 구성은 아니며 overflow 경계에서 바깥쪽 일부가 잘린다. 그 실제 결과를 유지했다. 위·아래 그림자, 라벨과 안내문 간격, 입력 가용 폭도 원본과 일치. |
| 이름 입력·포커스 해제·값 유지 | `source.html:3`, `source.css:12–15`. icon 뒤 input flex1/min-width0, placeholder #888276, 입력 본문 #292823. wrapper는 blur 시 기본 border/none 복귀. | `app.html:3`, `design-system.css:8–10` 및 `feature.css:5`. 같은 ds-icon/입력 구조·type/text 토큰, 동일 부모 배치. | 양쪽 `fill("김민수")` 후 `*-filled-focused.png`, Tab 후 `*-filled-blurred-button-focused.png` 직접 열람. JSON의 `states.filledFocused/filledBlurred`와 activeElement/value/styles를 확인. | placeholder가 김민수로 바뀌고 장식·텍스트 정렬이 유지됨. Tab 후 activeElement BUTTON, 값 김민수 유지, wrapper border rgb(213,209,199), shadow none. 후 원본↔구현 각 PNG 동일. |
| step1 다음 버튼 접근·활성화 | `source.html:3` button type=button, `source.css:16`. dialog 마지막 자식, 높이44/flex-shrink0, 연결 스크립트·목적지 없음. | `app.html:3` ds-button, `design-system.css:11`의 기존 button 토큰; 같은 dialog 마지막 자식. | 입력 후 실제 Tab 접근과 Enter 활성화. 양 JSON의 `buttonActivation`에 isTrusted=true, detail=0 click 한 번, DOM 동일 여부·URL 기록. `*-after-button-activation.png` 4개를 직접 열람. | 다음 버튼의 native 키보드 focus 외곽선이 보임. Enter 후 양쪽 모두 DOM unchanged=true, about:blank 유지, 김민수와 step1 화면 유지. 정적 버튼의 실제 결과이며 다음 단계 진행 성공이나 검증 규칙/API를 구현·주장하지 않음. |

## 수정 전후 비교 3종

| 비교쌍 | 대상/상태 | 양쪽 원본/렌더 근거 | 차이 | 결과/미확인 사유 |
|---|---|---|---|---|
| 기존 원본 ↔ 현재 기준 원본 | fixture-v1 원본 유지·초기 화면, 이번 관찰 두 회차의 원본 관련 상태 | 인계의 source.html/source.css hash와 현재 파일 hash가 일치. 기존 제공 `../browser/source-default.png`를 직접 열람했고 이번 `source-current-default.png`와 PNG 바이트 동일. 이번 원본 `source-current-*` ↔ `source-current-post-*` 및 양 browser JSON. | 원본 코드 교체 없음. 새 관찰 두 회차의 안정 상태/경계 detail 6종 PNG도 전부 동일. | 원본 유지 확인. 기존 제공 캡처가 focus·전환 관찰을 증명한다고 해석하지 않았다. 관련 상태는 이번에 새로 관찰했다. |
| 현재 기준 원본 ↔ 수정 후 실제 구현 | 전체 화면과 위 모든 관련 상태·조작 | `source.html/source.css`와 `app.html/tokens.css/design-system.css/feature.css` 실제 로드 순서. `source-current-post-*` ↔ `implementation-after-*`, `browser-observations-after.json`, `capture-comparisons.json`. | 안정 상태 5개와 경계 detail 1개의 PNG 바이트 동일. live 전환 캡처는 촬영 시각 차이로 중간 색 강도가 다를 수 있어 같은 프레임 비교로 사용하지 않음. 실제 rAF 진행·이벤트·종결 상태를 대조했다. | 해당 상태 범위의 외형 및 실제 전환/입력/버튼 결과 재현 확인. 구체 승인 이탈 없음. native visual 게이트·독립 감사는 이번 checkpoint 밖. |
| 수정 전 실제 구현 ↔ 수정 후 실제 구현 | 위치·폭·그림자 표시 수정과 전체/상태 회귀 | `observations-before.json.before_feature_css`, `implementation-before-*` ↔ `implementation-after-*`, 양 browser JSON의 states/transitions/buttonActivation. | scroll padding0→2 2 4, 내부 시작점 +2px,+2px, 가용 폭 304→300. 그림자의 좌우 표시가 원본에 맞음. 카드·제목·버튼의 rect와 기본 타입/색·focus effect 토큰은 유지. | 요청 차이가 반영됨. 텍스트 입력·값 유지·focus 복귀·Tab/Enter 동작과 전체 배치에서 추가 회귀를 발견하지 못함. 원본↔최종 직접 대조로도 확인. |

## 증거 경로와 재소비

- `observations-before.json`: 첫 편집 전 코드 전체·입력 hash·구조 smoke·초기 MCP 오류 원문.
- `browser-observations-before.json`: 첫 편집 전 source-current 및 implementation-before의 실제 browserVersion/viewport/전체 요소 rect·computed styles·상태·rAF frames·이벤트·버튼 결과·캡처 경로·생성 page 정리 원문.
- `browser-observations-after.json`: 수정 후 source-current-post 및 implementation-after의 같은 관찰 원문.
- `capture-comparisons.json`: 직접 열람한 안정 PNG의 Python 표준 라이브러리 byte 비교와 SHA-256. 원본↔후 구현 6쌍 모두 동일이며 이 사실은 동일하게 인코딩된 픽셀을 보조 증명한다. 서로 다른 시각에 찍힌 live PNG는 이 비교에서 제외했다.
- `verification.json`: 수정 후 hash·smoke 도구 결과·브라우저 복구/정리 사실·직접 연 캡처의 절대 경로 32개.
- `handoff.md`: 이 반환 문서.

실제 생성하고 `view_image`로 직접 재열람한 PNG는 다음 **4개 prefix × 8개 suffix = 32개**다. 전체 화면은 390×844, 경계 detail은 같은 viewport에서 (38,332,314,134)를 잘라 캡처했다. 이후 이미지 파일을 편집하지 않았다.

| Prefix | 의미 |
|---|---|
| source-current | 첫 CSS 편집 전 현재 원본 |
| implementation-before | 첫 CSS 편집 전 실제 구현 |
| source-current-post | CSS 수정 후 다시 렌더한 같은 원본 |
| implementation-after | CSS 수정 후 실제 구현 |

각 prefix의 suffix는 `-default.png`, `-focus-entry-live.png`, `-empty-focused.png`, `-focus-boundary-detail.png`, `-filled-focused.png`, `-focus-exit-live.png`, `-filled-blurred-button-focused.png`, `-after-button-activation.png`다. 기존 제공 `../browser/source-default.png`는 이 32개와 구별하며 직접 열람했다. 관찰 JSON도 저장 후 Python JSON 파싱으로 다시 읽었고 비교표에 필요한 실제 값과 rAF 원문을 도구 출력에서 재소비했다. 임시 렌더·진단 코드는 메모리/도구 출력에서만 사용했다.

최초 MCP 두 번은 `Browser is already in use for /Users/hyun/Library/Caches/ms-playwright-mcp/mcp-chrome-6bb91ef, use --isolated to run multiple instances of the same browser`로 실패했다. 부모 Coordinator가 자신이 소유한 통제 세션을 닫은 뒤 동일 MCP 접근이 복구되었다. 첫 복구 탐색의 `process` 참조는 `ReferenceError: process is not defined`였고, 그 참조를 제거한 메타데이터 조회와 실제 관찰 두 회차는 성공했다. 이 coder는 새 프로필·cache·설정 변경이나 다른 브라우저 우회를 하지 않았다.

선택적 Pillow 픽셀 비교 진단은 `ModuleNotFoundError: No module named 'PIL'`(exit 1)로 실행 초기에 실패했고 파일을 생성하지 않았다. 설치하지 않고 기존 PNG의 표준 라이브러리 byte 비교로 확인했다(exit 0). 이 실패와 대체 방법은 `capture-comparisons.json`에 남겼다. 픽셀 차이 개수나 임의 임계값을 측정했다고 주장하지 않는다.

생성한 page 4개는 각 관찰 호출의 finally에서 모두 닫았다. 마지막 `browser_tabs({action:"list"})` 결과는 작업용 `about:blank` 한 개뿐이었다. 부모의 정리 지시를 따라 `browser_close({})`를 실행했고 원문 `No open tabs. Navigate to a URL to create one.`을 받았다. 사용자 page는 나타나지 않았고 조작하지 않았다.

요청 범위의 필수 상태 중 미실행·미검증으로 남긴 항목은 없다. 전환 샘플의 시간 정밀도와 비동기 live 캡처 시각 한계는 위 표에 명시했다. step2·API·업무 진행·다른 viewport·native 파이프라인·독립 감사는 승인된 범위 밖이므로 실행하지 않았다.

Serena·Graphify는 opt-in이 없어 검색·로드·호출·초기화하지 않았다.
