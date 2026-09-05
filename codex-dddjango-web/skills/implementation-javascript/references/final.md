# UI JavaScript 구현 레퍼런스

승인된 화면 요구의 브라우저 UI 동작을 구현·감수할 때 필요한 표기다. dddjango-web의 UI 동작 계약·기능별 배치·host 외부 로드 규칙을 전제로 하며, 이를 변경하는 권한은 포함하지 않는다. 필요한 `## §N.` 절만 읽는다.

## §1. 책임과 최소 구현

| 기술 | 이 플러그인에서 담당할 것 | JS로 옮기지 않을 것 |
|---|---|---|
| Python/Django | 요청 처리, form 검증, VM의 서버 표시 데이터 조립, API 계약 소비 | 업무 권한·가격·저장 결과의 최종 판정 |
| HTML | 서버가 결정한 데이터의 구조·의미·기본 폼 동작 | JS 문자열로 별도의 서버 화면 템플릿 작성 |
| HTMX | 사용자 동작에 따른 요청과 서버 HTML 교체 | 같은 업무 요청을 fetch/XHR로 중복 수행 |
| CSS | 토큰·레이아웃·시각 상태·전환 | JS에 색·간격·애니메이션 시스템 재정의 |
| JavaScript | 비밀번호 표시 전환, 복사 안내, 파일 미리보기, 필요한 포커스 등 임시 UI 동작 | 브라우저를 업무 상태의 권위 있는 저장소로 사용 |

HTMX는 부분 교체를 할 수 있는 요청·HTML 교체 도구다. 실시간성을 자동 보장하는 계층이 아니다. polling·SSE 같은 전달 방식은 요구와 서버 계약이 있을 때 따로 설계한다. 이 스킬을 계기로 도입하지 않는다. [HTMX docs](https://htmx.org/docs/)

native `<details>/<summary>`가 요구를 충족하면 그것을 쓴다. JS 기능을 찾기 위해 원래 없던 상호작용을 추가하지 않는다. [MDN details](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/details)

한 기능은 사용자에게 보이는 동작 단위다. **한 기능의 JS는 파일 하나**이며 내부 함수 수와는 무관하다. 초기화·이벤트·정리를 함께 둔다. 새 웹 트리가 적용된 환경의 경로는 `web/static/js/<기능>.js`이고 이름은 snake_case다. 경로·벤더·중복 이름 충돌의 판정은 houserules에서 받는다. 이 규칙은 프로젝트 결정이며 일반 JavaScript 언어 규칙이 아니다. 기존 트리가 다르면 이 문서만으로 파일을 옮기지 않는다.

같은 화면의 다른 기능을 `ui.js`에 합치거나, 한 기능을 init/events/cleanup 파일로 나누지 않는다. 여러 인스턴스는 같은 파일을 공유하되 상태는 해당 root에 귀속한다. 상태 저장·로딩을 위해 새 프레임워크나 전역 레지스트리를 만들 필요는 없다.

## §2. 로드·DOM 계약·이벤트

페이지 수명 동안 외부 기능 스크립트를 한 번 로드한다. 실제 `{% static %}` 인자와 로드 위치는 승인된 host/template 규칙에서 받는다. fragment에 실행 스크립트를 반복 포함하거나 inline handler·`hx-on`/`js:` 표현식으로 기능 코드를 흩어놓지 않는다.

- 기존 classic 정책이면 `defer`와 파일 내부 범위를 쓸 수 있다. 기존 module 정책이면 그 방식을 따른다. module에 defer를 더해도 같은 효과가 추가되는 것은 아니다. `async`는 DOM·의존 스크립트 순서를 보장하는 대체물이 아니다. [WHATWG script](https://html.spec.whatwg.org/multipage/scripting.html#the-script-element)
- 초기 DOM을 읽는 코드가 늦게 실행될 수도 있으면 `document.readyState`가 `loading`인지에 따라 DOMContentLoaded 대기 또는 즉시 초기화한다. 한 번 등록한 이벤트 위임만으로 충분하면 최초 DOM 스캔도 필요 없다. [MDN DOMContentLoaded](https://developer.mozilla.org/en-US/docs/Web/API/Document/DOMContentLoaded_event)
- 기능은 명시적 root와 그 안의 역할을 나타내는 `data-*` 표식을 사용한다. CSS 클래스 이름을 동작 계약으로 추정하지 않는다. 반복 UI의 전역 ID 중복, document에서 첫 요소만 찾는 선택을 피한다.
- 위임에서 `event.target`의 Element 여부를 확인하고 `closest`로 실제 제어 요소를 찾는다. 중첩된 독립 기능을 허용하는 명세라면 가장 가까운 소유 root가 일치하는지도 확인한다.

**단순 기능 예제 — `password_visibility.js`.** 아래 DOM은 계약 설명용이며 특정 마크업을 모든 화면에 강제하지 않는다. 서버 값·경로·스타일은 기존 템플릿이 제공한다. 버튼은 JS 연결 전 hidden이라 기능이 없는 제어가 노출되지 않는다.

```html
<div data-password-visibility>
  <label>비밀번호 <input type="password" autocomplete="current-password" data-password-input></label>
  <button type="button" data-password-toggle aria-pressed="false" hidden>비밀번호 표시</button>
</div>
```

```javascript
(() => {
  const selector = "[data-password-visibility]";
  function activate(scope) {
    const roots = new Set(scope.querySelectorAll(selector));
    const owner = scope instanceof Element ? scope.closest(selector) : null;
    if (owner) roots.add(owner);
    for (const root of roots) {
      const input = root.querySelector("[data-password-input]");
      const button = root.querySelector("[data-password-toggle]");
      if (!input || !button) continue;
      button.setAttribute("aria-pressed", String(input.type === "text"));
      button.hidden = false;
    }
  }
  document.addEventListener("click", (event) => {
    if (!(event.target instanceof Element)) return;
    const button = event.target.closest("[data-password-toggle]");
    const root = button?.closest(selector);
    const input = root?.querySelector("[data-password-input]");
    if (!input) return;
    const visible = input.type === "password";
    input.type = visible ? "text" : "password";
    button.setAttribute("aria-pressed", String(visible));
  });
  document.addEventListener("htmx:load", (event) => activate(event.detail.elt));
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => activate(document), { once: true });
  } else {
    activate(document);
  }
})();
```

이 예제는 root별 외부 자원이 없으므로 destroy 레지스트리가 없다. activate가 여러 번 불려도 클릭 리스너를 추가하지 않는다. 전달된 새 노드의 소유 root까지 찾으므로 버튼·input만 교체해도 현재 요소로 다시 맞춘다. 버튼의 고정된 이름과 `aria-pressed`가 상태를 함께 전달한다. root는 동일 기능이 중첩되지 않는 DOM 계약이다. 다른 구조는 그 소유 경계에 맞게 적용한다.

## §3. HTMX와 UI 수명

설치된 HTMX 버전을 먼저 확인한다. 아래는 2.x 이벤트 계약을 소비한다. 새 버전·확장·다른 swap 방식이 있으면 해당 공식 계약을 확인하며 자동 업그레이드는 하지 않는다. [HTMX events](https://htmx.org/events/)

| 상황 | 필요한 처리 |
|---|---|
| 최초 페이지 | DOM 사용 가능 시 연결. HTMX 최초 load와 겹쳐도 효과 중복 없음 |
| 새 HTML 추가·root 교체 | 초기화가 필요한 기능은 `htmx:load`의 `detail.elt`와 그 자손을 발견 |
| DOM 배치 이후 측정 필요 | 목적에 맞는 afterSwap/afterSettle 선택. 둘을 동일 타이밍으로 보지 않음 |
| HTMX가 노드 정리 | `htmx:beforeCleanupElement`의 `detail.elt`가 무엇을 소유·포함하는지 확인 |

`element.querySelectorAll()`은 그 요소 자신을 반환하지 않는다. 스캔 구현은 자신의 `matches()`와 자손 검색을 함께 고려한다. 이벤트 위임만 쓰는 기능에는 이 스캔 규칙을 억지로 적용하지 않는다. [MDN querySelectorAll](https://developer.mozilla.org/en-US/docs/Web/API/Element/querySelectorAll)

**초기화가 필요한 경우** root별 연결 여부를 코드 내부에서 관리하고 같은 root에는 중복 리스너·observer를 붙이지 않는다. `WeakMap`은 인스턴스 상태를 저장하는 선택지다. DOM의 `data-initialized` 문자열만으로 연결 여부를 판단하면 복제·히스토리 복원에서 실제 리스너와 어긋날 수 있다. 단순 기능에 init/destroy 틀을 강제하지 않는다.

**자원 정리가 필요한 경우** 생성한 코드가 해제도 소유한다. root가 제거되거나 그 자원을 실제 사용하는 노드가 교체되는 순간 해당 작업·자원만 끝낸다. 반복 정리는 안전해야 한다.

- 정리 대상이 root 자신 또는 root를 포함한 제거 영역이면 그 root의 자원을 해제한다.
- 정리 대상이 살아 있는 root 안의 자식이면 **그 자식이 해당 자원의 실제 종속 노드인지** 확인한다. 독립 안내문·장식 노드의 삭제만으로 부모 기능의 선택 상태를 지우지 않는다. `detail.elt.closest(rootSelector)` 결과만으로 부모 전체를 정리하지 않는다.
- root는 유지되고 input·제어·출력 등 기능의 자식이 교체되는 계약이라면, 제거되는 참조를 무효화하고 새 노드를 다시 연결하거나 동작 시 현재 노드를 조회한다. “root 초기화 완료”만 보고 오래된 자식 참조를 계속 사용하지 않는다.
- pre-swap에서 페이지 전체를 무조건 정리하지 않는다. `hx-preserve`처럼 살아남거나 이동하는 요소가 있는 화면은 그 상태 보존을 실제 swap에서 확인한다. 히스토리 기능이 있는 화면은 저장된 DOM과 JS 인스턴스가 같은 수명을 가진다고 가정하지 않는다. [HTMX preserve](https://htmx.org/attributes/hx-preserve/), [HTMX history](https://htmx.org/docs/#history)

HTMX 바깥의 DOM 제거 경로가 승인된 기능에 있다면 그 제거 코드도 소유 자원 정리를 호출해야 한다. 단지 가능성이 있다는 이유로 document 전체 MutationObserver를 추가하지 않는다.

## §4. 브라우저 자원·비동기 결과

| 실제로 사용하는 자원 | 수명 종료 시 처리 |
|---|---|
| root별 리스너 | 같은 함수 참조로 제거하거나 해당 인스턴스 AbortController의 signal로 등록 후 abort |
| timer·animation frame | 작업이 더 이상 유효하지 않으면 clear/cancel |
| observer | 해당 인스턴스 disconnect |
| blob object URL | 재선택·clear·사용 노드 제거 시 이전 URL revoke |
| 취소 가능한 비동기 작업 | 해당 API의 취소 계약 사용; 완료 콜백의 유효성도 확인 |

반복 익명 리스너 등록은 같은 코드처럼 보여도 중복될 수 있다. 문서 수명 리스너를 한 번 설치한 기능은 root마다 그 리스너를 제거할 필요가 없다. WeakMap의 항목 삭제나 GC만으로 URL·타이머·외부 관찰이 해제되었다고 보지 않는다. [MDN addEventListener](https://developer.mozilla.org/en-US/docs/Web/API/EventTarget/addEventListener)

파일 미리보기는 로컬 File을 표시하는 일이다. 업로드 성공·파일 허용의 서버 판정과 다르다. object URL을 쓰면 새 선택으로 대체할 때 이전 URL을 끝내고, 마지막 사용이 끝날 때 revoke한다. 이미지 load 직후의 무조건 revoke는 이후 사용자 동작에 필요한 URL까지 없앨 수 있다. 실제 사용 수명을 기준으로 정한다. [MDN File API](https://developer.mozilla.org/en-US/docs/Web/API/File_API/Using_files_from_web_applications), [MDN revokeObjectURL](https://developer.mozilla.org/en-US/docs/Web/API/URL/revokeObjectURL_static)

Promise 뒤에 UI를 갱신하는 코드는 두 가지를 확인한다.

1. **작업의 최신성**: 같은 root의 뒤에 시작한 작업이나 clear·dispose가 이전 결과를 무효화했는가. 세대 번호 또는 현재 작업 객체의 동일성으로 표현할 수 있다.
2. **대상의 유효성**: 그 root와 출력 노드가 아직 해당 기능의 현재 DOM인가. 연결 여부만으로 최신 작업임을 보장하지는 않는다. 같은 ID의 새 노드를 다시 찾아 이전 결과를 적용하지 않는다. [MDN isConnected](https://developer.mozilla.org/en-US/docs/Web/API/Node/isConnected)

복사 안내는 사용자가 누른 동작 안에서 Clipboard API를 호출하고, writeText가 실제 성공한 뒤 성공을 표시한다. secure context·권한 거절·API 미지원에 대한 실패 경로를 처리한다. 실패했는데 성공 문구를 보여주지 않는다. Clipboard Promise에는 AbortSignal 취소 계약이 없으므로 UI 정리만으로 이미 시작한 복사를 취소했다고 쓰지 않는다. 새 작업·사라진 UI의 결과 표시는 무효화할 수 있다. [MDN Clipboard writeText](https://developer.mozilla.org/en-US/docs/Web/API/Clipboard/writeText)

## §5. 데이터 소비와 DOM 출력

문자열은 `textContent`나 폼 요소의 `value`로 넣는다. 사용자 문자열·파일명·API 메시지를 `innerHTML`로 해석하지 않는다. 승인된 서버 HTML 교체는 HTMX 계약이 담당한다. [MDN textContent](https://developer.mozilla.org/en-US/docs/Web/API/Node/textContent)

서버에서 전달한 구조화 값이 필요하면 implementation-ui의 허용된 전달 방식과 템플릿 escaping을 소비한다. Django `json_script`는 비실행 JSON 데이터이며 `textContent`를 JSON.parse하여 읽는다. 이를 실행 JS 허용과 혼동하지 않는다. 수동 JSON 문자열 조립, 템플릿 값을 실행 소스에 끼워 넣기, eval은 데이터 전달 방식이 아니다. 단일 값은 정상 escape된 quoted data 속성으로 충분할 수 있다. [Django json_script](https://docs.djangoproject.com/en/5.2/ref/templates/builtins/#json-script)

클라이언트 표시 검사는 사용자 편의를 위한 것이다. HTML 조작이나 JS 생략으로 우회해도 서버의 입력 검증·인증·인가가 유지되어야 한다. 이 스킬의 UI 요구를 계기로 토큰·세션·업무 상태를 localStorage에 옮기거나 별도 API 호출 계층을 만들지 않는다.

## §6. 키보드·포커스·시각 상태

클릭 가능한 기본 요소는 button/link 의미에 맞게 사용한다. 폼 안에서 제출하지 않는 제어는 `type="button"`이다. 상태를 바꿀 때 hidden·disabled·해당 ARIA 상태·화면 표시가 서로 어긋나지 않게 한다. ARIA 속성은 키보드 동작을 대신 구현하지 않는다.

disclosure에는 펼침 상태와 제어 대상 관계를, dialog에는 초점 진입·Tab 이동·Escape·종료 뒤 복귀를 해당 패턴에 맞춘다. 모든 제어에 dialog의 키보드 규칙을 적용하지 않는다. native 요소가 제공하는 처리를 중복 구현하지 않는다. 원래 초점 대상이 제거됐다면 명세의 다음 동작에 맞는 살아 있는 대상으로 이동한다. [W3C disclosure](https://www.w3.org/WAI/ARIA/apg/patterns/disclosure/), [W3C modal dialog](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/)

복사·선택 같은 상태 안내는 필요한 경우 템플릿의 status/live 영역을 사용하되, 시안에 없는 토스트·모션·모달을 새로 만들지 않는다. 시각 값과 전환은 CSS가 소유한다. 기존 motion 러너의 판형이나 data-motion 계약을 이 스킬로 바꾸지 않는다.

## §7. 구현 검증과 감수

검증은 기능의 실제 위험에 비례한다. 단순 토글에 파일·네트워크·히스토리 검사를 모두 요구하지 않는다. 정적 구문 검사는 브라우저 수명 검증을 대신하지 않는다.

| 해당하는 조건 | 확인할 동작 |
|---|---|
| 모든 UI JS | 승인된 동작, 초기 진입, 사용자가 실제 누르는 경로; 반복 UI가 있으면 인스턴스 격리 |
| HTMX로 갱신되는 UI | 실제 요청에 의한 추가·교체·삭제, root 자체와 자손 처리, 유지되는 이웃의 상태 |
| 인스턴스 초기화 | 같은 root 재처리에도 동작·리스너 중복 없음 |
| 자원 보유 | 재선택·clear·제거 뒤 해당 자원 종료, 유지된 UI는 정상 |
| 비동기 완료 | 실패·늦은 완료·새 작업 뒤 오래된 완료·제거된 대상 |
| 키보드/포커스 기능 | 키보드 조작, 상태 의미, 필요한 초점 이동·복귀 |
| history/preserve 사용 | 해당 화면의 실제 복원·보존 경로 |

브라우저 API의 성공·실패 타이밍을 제어한 테스트는 해당 상태 경로의 증거다. 그것을 실제 OS 권한·클립보드 성공이나 모든 브라우저 호환성 증거로 부르지 않는다. 수동 HTMX 이벤트는 멱등성 확인에 쓸 수 있지만 실제 HTTP swap 검사를 대신하지 않는다.

감수 결과는 **문제 위치 → 어긴 화면/수명 계약 → 실제 영향 → 필요한 수정**으로 적는다. 단순 위임에 destroy 함수가 없다는 이유, 또는 framework·공통 유틸리티가 없다는 이유만으로 반송하지 않는다. 승인되지 않은 서버 책임 이동·외형 발명은 해당 소유 경계로 반송한다.

완료 보고에는 변경한 기능 파일, 실제 실행한 조건과 결과, 검증하지 못한 적용 조건을 남긴다. 검사 실패를 피하려 기존 금지 규칙이나 테스트 기대값을 변경하지 않는다.
