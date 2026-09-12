# Coordinator 반환 수용 판정

불완전 반환의 **전체 시각 확인 완료 주장은 수용하지 않는다**. 현재 `create-person-step1`의 시각 상태는 **unverified(미검증)**이며, 이 상태로 시각 완료나 다음 단계 진행을 승인하지 않는다. 지금 수행할 일은 같은 case의 빠진 원본·구현 관찰과 필요한 화면 CSS 보완이다. 전체 native G0/G1/G2나 JSON 입장 게이트를 실행한 것으로 판정하지 않는다.

## 근거와 코드·시각 판정

작업 루트는 `/Users/hyun/.cache/dddjango-web-a8-20260913`다. 현행 `dddjango-web/commands/dddjango-web.md` 전체, 지정된 `role-g0-input.md`, 독립 검토 반환 `role-g0-return.md`, 합성 입력 `role-partial-return.md`, 현재 `role-browser-app/`의 원본·구현 HTML/CSS와 smoke를 확인했다. 인계 판형은 `dddjango-web/skills/implementation-ui/SKILL.md` 및 `references/final.md` §2를 소비했다. 아래 eval 상대 경로의 기준은 `workspace/eval/web-a8-visual-fidelity/`다.

| 축 | 실제 근거 | 이번 수용 판정 |
|---|---|---|
| 원본 정합 | `role-browser-app/source.html`, `source.css`를 `micro/fixture/`의 같은 파일과 바이트 대조해 둘 다 동일함을 확인 | `fixture-v1` 기준 유지. 원본 교체 없음 |
| 코드·구조 | `role-browser-app/`에서 `python3 smoke.py` 실제 실행, exit 0. 출력: `PASS: HTML id uniqueness and stylesheet wiring only; no render or visual assertions` | HTML ID 유일성·대상 입력 ID·CSS 배선과 파일 존재만 PASS. 코드 전체의 정확성이나 시각 일치를 뜻하지 않음 |
| 기본 화면 | 독립 입력범위 검토는 `browser/source-default.png`에서 기본 원본을 확인했다고 반환. 불완전 반환은 구현 초기 화면의 제목·입력·다음 버튼 존재만 확인했다고 서술 | 원본 기본 관찰의 출처와 구현 smoke 수준의 자기 보고를 구별해 보존. 이 Coordinator는 새 브라우저 관찰을 하지 않았고 현재 원본↔구현 기본 외형 일치를 검증하지 않음 |
| 관련 상태 | 불완전 반환 자체에 focus 조작 및 원본↔구현 상태 대조 미실행이 명시됨. 독립 검토도 포커스·전환·입력값·해제 관찰 부족으로 `review-result: fail` | 관련 상태 미검증 유지. 기존 case에 포함된 관찰을 다음 호출에서 수행해야 함 |
| 전체 시각 요약 | `Visual outcome matches the frozen design in each case`가 위 미실행 사실과 공존 | 포괄적 일치 요약을 거부하고 상태별 근거와 일치하는 정정 반환을 요구 |

현재 파일에서 원본 스크롤 부모와 구현 스크롤 부모의 여백 구성 차이는 확인했다. 입력 부품의 DS 포커스 선언이 대응해도 부모의 배치·가용 폭·overflow가 만드는 실제 표시 범위까지 보존됐다고 추론할 수 없다. 이는 실제 렌더로 확인할 항목이며, 아직 이 Coordinator가 그림자 잘림이나 그 수정 성공을 관찰했다는 뜻은 아니다. 현재 시각 판정은 미검증이고, 후속 실행에서 실제 차이가 확인되면 해당 상태를 failed로 구별해 수정·재확인해야 한다.

원본 확인값:

- `source.html` SHA-256: `269d9114a7ffcd135d3fb0f1b18824f511d4b654977f439213f9551005368090`
- `source.css` SHA-256: `0cf2a17eb473b31c24472a5a24fea654e68fd7626b0d9b0e5e0122b19d7ffd8b`

## 보완 범위와 담당

`cases-v1`의 **`create-person-step1` 하나, viewport 390×844**를 유지한다. 이름 등록 step1을 원본대로 구현하며 관련 상태·효과를 제외한 결정은 없다. 일정 압력과 DS 재사용·구조 green은 이탈 승인이나 관찰 생략 근거가 아니다. 새 focus case나 step2를 추가할 필요 없이 다음 항목을 같은 case 안에서 확인한다.

1. 초기 빈 입력과 화면 전체의 요소·치수·타이포·색·간격·장식·버튼 배치를 원본과 대조한다.
2. `#person-name`에 실제 포커스를 주고 입력 래퍼의 테두리와 그림자, 진입·복귀 전환을 확인한다.
3. 이름을 입력하고 다른 요소로 포커스를 이동해 placeholder 전환·입력값 유지·해제 후 외형을 확인한다.
4. 입력이 놓인 스크롤 부모의 배치·여백·overflow와 자식 그림자의 상하좌우 표시 범위를 원본·수정 전·수정 후 렌더에서 대조한다.
5. step1 안의 키보드 접근과 다음 버튼 접근·활성화 사실을 확인한다. 목적지·업무 진행·추가 검증 규칙은 이번 범위 밖이며 정적 원본에 없는 결과를 만들어내지 않는다.

**fresh coder 한 명이 코드 수정과 브라우저 관찰을 함께 담당한다.** 가용 Playwright MCP `browser_run_code_unsafe`에서 새 page에 로컬 HTML의 CSS를 인라인한 렌더를 `setContent`하고 원본과 구현을 같은 viewport에서 조작한다. 원본 관련 상태와 수정 전 구현을 첫 편집 전에 관찰·보존하고 필요한 `feature.css` 변경 후 같은 범위를 재확인한다. 일반 GUI가 없다는 이유로 가용 MCP 관찰을 뒤로 넘기지 않는다.

코드 변경은 `role-browser-app/feature.css`만 허용된다. 검증 기록은 같은 디렉터리의 `handoff.md`와 캡처·관찰 기록에만 남긴다. 원본·공용 DS·tokens·app HTML은 보존한다. 상세 요청 원문은 `role-dispatch.md`에 작성했다. 이 checkpoint에서는 자식 실행·앱 수정·커밋·서버 실행을 하지 않는다.

## 후속 반환 수용 조건

구조 검사의 실제 명령·exit·출력과 시각 판정을 분리해서 받는다. 시각 반환은 위 상태별 실제 조작·원본/구현 위치·캡처/관찰 원문·차이·미검증 범위를 `implementation-ui` §2의 표로 연결해야 한다. 수정 전후 비교 3종도 양쪽 근거와 함께 기록한다. 필수 상태가 빠지면 case 전체 PASS로 합치지 않고 같은 담당자에게 필요한 관찰을 보완시킨다. 미실행을 후속 일로 넘기면서 전체 외형 일치를 주장한 요약은 다시 수용하지 않는다. 이 checkpoint의 범위 안에서 반환 근거가 충족됐다는 판정과, 범위 밖 native 시각 게이트·독립 감사 통과 주장은 구별한다.

실행한 읽기·smoke·해시 대조는 도구 출력에서 소비했으며 별도 로그를 생성하지 않았다. Coordinator가 작성한 파일은 이 판정문과 `role-dispatch.md` 두 개다. Serena·Graphify는 opt-in이 없어 사용하지 않았다.
