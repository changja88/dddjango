# UI JavaScript 선별 조사

조사일: 2026-09-05. 대상: dddjango-web의 `implementation-javascript` 신규 스킬.
스킬 작성 근거이며 현재 플러그인의 JS 금지를 해제하는 문서가 아니다.

## P1 Source Sufficiency

| field | value |
|---|---|
| purpose | Django가 렌더한 화면에서 승인된 브라우저 UI 기능을 구현·감수하기 위한 실행 메커니즘 |
| use when | 비밀번호 표시, 복사 안내, 파일 미리보기, 포커스 등 로컬 UI 동작과 HTMX 교체 수명 |
| exclude/handoff | 업무 판정·인증·인가·업무 API 호출, SPA 상태 계층, JS 일반 교과서, 빌드 도구 도입, 시안에 없는 기능 발명 |
| core criteria | 최소 메커니즘, 인스턴스 격리, 실제 제거 범위에 맞는 정리, 비동기 결과 유효성, 안전한 DOM, 접근 가능한 상호작용 |
| source priority | 브라우저 표준·MDN API 문서, HTMX 공식 문서, Django 공식 문서, W3C APG; 저장소의 결정은 외부 사실과 구분 |
| P1 classification | sufficient for scoped UI implementation; 전체 JavaScript·전체 브라우저·모든 HTMX 확장에 대한 충분성은 주장하지 않음 |

## 조사 질문과 채택

| ID / 질문 | 공식 근거 | 채택·조건 | 소유 |
|---|---|---|---|
| S1 첫 DOM은 언제 사용할 수 있나 | [MDN DOMContentLoaded](https://developer.mozilla.org/en-US/docs/Web/API/Document/DOMContentLoaded_event), [WHATWG script](https://html.spec.whatwg.org/multipage/scripting.html#the-script-element) | 외부 classic defer 또는 기존 module 정책 소비. 늦은 실행 가능 시 readyState 분기. async와 defer를 같은 것으로 취급하지 않음 | JS 구현; 로드 경로는 UI/Coordinator |
| S2 fragment 교체에서 무엇을 관찰하나 | [HTMX events](https://htmx.org/events/), [HTMX docs](https://htmx.org/docs/) | load의 새 노드, beforeCleanupElement의 실제 정리 노드. afterSwap/afterSettle은 목적에 맞게 선택 | JS는 수명 소비; 요청·swap 설계는 architecture/UI |
| S3 전달된 root도 검색되나 | [MDN querySelectorAll](https://developer.mozilla.org/en-US/docs/Web/API/Element/querySelectorAll) | 자손 검색과 receiver 자신의 matches를 구분. 스캔을 선택한 기능에만 필요 | JS 구현 |
| S4 리스너·자원은 언제 끝나나 | [MDN addEventListener](https://developer.mozilla.org/en-US/docs/Web/API/EventTarget/addEventListener), [MDN revokeObjectURL](https://developer.mozilla.org/en-US/docs/Web/API/URL/revokeObjectURL_static), [MDN File API](https://developer.mozilla.org/en-US/docs/Web/API/File_API/Using_files_from_web_applications) | 이벤트 위임 또는 중복 없는 인스턴스 연결. 소유자가 blob URL·타이머·observer를 정리. WeakMap 자체는 자원 해제가 아님 | JS 구현 |
| S5 늦은 완료는 어디에 표시하나 | [MDN isConnected](https://developer.mozilla.org/en-US/docs/Web/API/Node/isConnected), [MDN Clipboard writeText](https://developer.mozilla.org/en-US/docs/Web/API/Clipboard/writeText) | 해당 작업의 최신성 및 살아 있는 동일 UI를 확인. clipboard 성공은 Promise 완료 뒤. AbortController가 모든 Promise를 취소하는 것은 아님 | JS 구현 |
| S6 서버 값·파일명을 어떻게 전달하나 | [Django json_script](https://docs.djangoproject.com/en/5.2/ref/templates/builtins/#json-script), [MDN textContent](https://developer.mozilla.org/en-US/docs/Web/API/Node/textContent) | 문자열은 textContent/value, 데이터는 허용된 직렬화 방식. json_script는 비실행 데이터이며 현재 script 검사 정책의 별도 통합 판단 필요 | JS 소비; 템플릿 표기는 UI |
| S7 JS를 생략할 수 있나 | [MDN details](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/details), [W3C disclosure](https://www.w3.org/WAI/ARIA/apg/patterns/disclosure/) | 요구가 native details/summary로 충족되면 커스텀 JS 없음. 커스텀 disclosure에는 제어 상태·키보드 계약 필요 | JS 필요성 판별; 외형은 UI/CSS |
| S8 대화상자 초점 규칙은 무엇인가 | [W3C modal dialog](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/) | 열기·탭 이동·Escape·닫은 뒤 적절한 초점 복귀. native가 제공하는 기능은 중복 구현하지 않음 | JS 구현; 구조는 HTML |
| S9 보존·히스토리도 자동으로 해결되나 | [HTMX hx-preserve](https://htmx.org/attributes/hx-preserve/), [HTMX history](https://htmx.org/docs/#history) | 해당 기능이 있는 화면에서만 보존·복원 조건 추가 검증. 임의 pre-swap 전체 정리로 보존 상태를 파괴하지 않음 | architecture 계약 + JS 수명 구현 |

## 저장소 결정과 외부 사실의 분리

- `implementation` 분류, 새 agent 미생성, coder-web 구현·discipline-reviewer-web 감수는 이번 스킬 도입 방향이다. 브라우저 표준의 의무가 아니다.
- UI JS 허용, 기능당 파일 하나, snake_case와 `web/static/js/<기능>.js`는 master에서 연결한 웹 표준 트리의 결정이다. 현재 배포 코퍼스에는 반영되지 않았다.
- 업무 데이터의 권위는 서버에 두고, HTMX가 서버 HTML을 교체하며, JS가 UI 임시 상태를 처리한다는 구분은 이 플러그인의 아키텍처다. 일반 웹 개발 전체의 금지 규칙으로 서술하지 않는다.
- 자료의 기능 예시는 구현 후보를 설명할 뿐 시안에 없는 동작의 추가 권한을 주지 않는다. motion 러너·벤더 파일을 새 스킬 예제로 대체하지 않는다.

## 버전·범위

실행 평가는 기존 2.x 이벤트 계약을 가진 HTMX **2.0.8**에 고정했다. 공식 사이트는 갱신되며 조사 시 docs의 CDN 예제는 2.0.10이었다. 스킬에서 무조건 최신 설치나 자동 업그레이드를 지시하지 않는다. 실제 설치 버전과 사용하는 이벤트 계약을 확인한다. Django 직렬화 근거는 5.2 문서다.

Node 서버 개발, React/Vue, TypeScript 전환, 번들러, 서비스 워커, 지속 캐시, 일반 알고리즘, 프레임워크 설계는 이번 목적에서 제외했다. 필요한 브라우저 API가 새로 생기면 그 API의 공식 계약만 추가 확인한다.

기준선의 기본 구현은 B1–B9를 통과했다. 탐색 E1에서 관찰된 정리 범위 오류는 특정 파일 미리보기 패치를 복사하지 않고, 소유 root·종속 노드·독립 자식의 수명을 구분하는 조건으로 일반화했다. 효과의 한계와 실행 결과는 `workspace/eval/implementation-javascript/2026-09-05/`에서 관리한다.
