파일 미리보기는 `file_preview.js` 하나로 구현했다. 과제의 DOM 계약을 그대로 사용한다.

페이지 공통 템플릿에서 다음과 같이 외부 파일을 한 번 로드한다. HTMX로 내려오는 부분 HTML에는 이 태그를 포함하지 않는다. HTMX 2.0.8은 과제의 기존 로딩을 사용한다.

```django
{% load static %}
<script src="{% static 'js/file_preview.js' %}" defer></script>
```

문서에 `change`, `click`, `htmx:beforeCleanupElement` 리스너를 각각 한 번 등록한다. 이벤트가 발생한 요소의 가장 가까운 `[data-file-preview]` 안에서 입력·이미지·파일명만 변경하므로 초기 두 개와 나중에 추가된 미리보기가 독립적으로 작동하도록 작성했다. DOM 교체 후 별도 초기화나 요소별 리스너 등록은 없다.

선택한 파일은 object URL로 미리 보여주고, 파일명은 `textContent`로 표시한다. 이미지 판정은 `File.type`의 `image/` 접두사 기준이다. 이미지가 아니면 입력과 미리보기를 비우고 기존 output에 `이미지 파일을 선택해 주세요.`를 표시한다. 유효한 이미지 선택에서는 input의 파일을 유지하며, 지우기는 input·이미지·파일명을 모두 비운다.

root별 object URL은 `WeakMap`에 보관한다. 재선택·빈 선택·지우기에서는 이전 URL을 해제한다. HTMX 정리 이벤트에서는 해당 root와 정리 대상 아래의 root를 처리하여 부모 innerHTML 교체, root outerHTML 교체, 삭제 때 URL을 해제하도록 했다. root 내부 교체도 해당 root의 기존 URL을 정리한다. 정리 이벤트의 의미와 `detail.elt`는 [HTMX 공식 이벤트 문서](https://htmx.org/events/#htmx:beforeCleanupElement)를 확인했다. 이 제거 처리는 HTMX의 정리 이벤트를 기준으로 한다.

실제로 수행한 확인은 다음과 같다.

- `node --check /tmp/dddjango-ui-js-20260905/baseline/file_preview.js`: 종료 코드 0으로 통과했다.
- 작성한 소스를 읽어 DOM 선택 범위, 파일명 `textContent` 사용, URL 생성·해제 흐름을 확인했다. 구현에는 네트워크 호출·폼 제출·서버 업로드 코드가 없다.
- 실제 HTMX 2.0.8을 사용한 브라우저 검증을 시도했지만, Playwright MCP는 기존 브라우저 프로필 사용 중 오류로 실행되지 않았다. 별도 임시 프로필의 Chrome 실행도 시작 단계에서 `SIGABRT`로 종료되었다. 따라서 브라우저 동작 검증은 완료하지 못했으며, 준비한 시나리오의 성공을 주장하지 않는다. 임시 검증 환경은 제거했다.

프로젝트 코드와 다른 평가 결과는 읽지 않았다. 새 implementation-javascript 스킬은 사용하지 않았다. Serena: skipped — 지정된 임시 파일 구현으로 기본 도구만 사용했다.
