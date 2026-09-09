# 파일 미리보기 구현 보고

산출물은 `file_preview.js` 하나다. 지정된 `implementation-javascript` 스킬과 레퍼런스의 로딩·이벤트 위임·HTMX 수명·Blob URL·텍스트 출력 규칙을 적용했다.

## 로딩 방식

전체 페이지의 호스트 템플릿에서 classic 외부 스크립트를 `defer`로 한 번 로드한다. 아래 `src`는 평가 앱이 이 파일을 제공하는 경로에 맞춘다.

```html
<script src="file_preview.js" defer></script>
```

파일 내부는 IIFE 범위다. 문서에 이벤트를 한 번 위임하므로 최초 DOM 스캔이나 root별 초기화가 필요 없다. 이후 추가·교체되는 section도 같은 리스너를 사용한다. 제공된 section 마크업의 구조와 `data-*` 계약은 변경하지 않았다.

## 구현 판단

- 로컬 파일을 img에 연결하고 사용한 Blob URL을 정리해야 하므로 JavaScript를 사용했다. 폼 제출·서버 업로드·네트워크 호출은 구현하지 않았다.
- 가장 가까운 `[data-file-preview]`가 기능의 소유자다. 이벤트 처리마다 현재 input·img·output을 조회하고, 활성 Blob URL과 그 URL에 대응하는 input·img 참조만 root를 키로 한 WeakMap에 보관한다.
- 이미지 선택은 같은 root의 img를 표시하고 파일명을 `textContent`로 그대로 출력한다. 이미지 여부는 로컬 표시를 위해 `File.type`의 `image/` 접두사로 확인한다. 이미지가 아니면 선택과 기존 미리보기를 비우고 기존 output에 안내한다. 지우기 버튼은 input·img·output을 모두 비운다.
- 재선택과 지우기는 이전 Blob URL을 해제한다. HTMX 정리에서는 제거 영역에 포함된 root 또는 활성 input·img의 수명을 끝낸다. 안내문·output·버튼 등 관련 없는 자식의 정리 이벤트만으로 활성 미리보기를 지우지 않는다. 반복 정리는 이미 해제한 URL을 다시 해제하지 않는다.
- `htmx:beforeCleanupElement`의 `detail.elt`가 정리 대상이라는 공식 이벤트 계약을 확인해 사용했다. [HTMX 이벤트 문서](https://htmx.org/events/#htmx:beforeCleanupElement)
- FileReader·Promise·타이머를 사용하지 않아 늦은 완료 콜백이 다른 선택을 덮어쓰는 경로가 없다. Blob URL은 이미지 load 직후 해제하지 않고 해당 미리보기의 사용 수명 동안 유지한다.

## 실제 확인

다음 명령을 실행했고 종료 코드 `0`으로 JavaScript 구문 검사를 통과했다.

```sh
node --check /tmp/dddjango-ui-js-20260905/with-skill/file_preview.js
```

브라우저 설치·실행과 동작 테스트는 요청에 따라 수행하지 않았다. 첫 진입·여러 인스턴스·실제 HTMX 요청을 통한 추가·innerHTML/outerHTML 교체·삭제·URL 해제의 브라우저 검증 결과는 주장하지 않는다. HTMX 밖에서 직접 노드를 제거하는 별도 경로, history/preserve 동작, 손상된 이미지의 디코딩 실패 처리는 이번 구현의 검증 범위에 포함하지 않았다.

Serena: skipped — 지정된 임시 기능 파일의 소규모 구현이며 기본 편집·구문 검사 도구를 사용했다.
