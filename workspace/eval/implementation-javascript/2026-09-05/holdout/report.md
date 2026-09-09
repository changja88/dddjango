# 복사 UI 적용 평가

적용 자료는 지정된 `implementation-javascript/SKILL.md`와 `references/final.md`이며, 임시 앱의 UI JS 작성 승인을 전제로 `copy_feedback.js` 하나를 작성했다. 기존 마크업과 외부 classic `defer` 1회 로드 계약을 그대로 사용한다.

## 구현 판단

- 기능 root는 `[data-copy-feedback]`이다. 문서에 클릭 위임을 한 번 연결하고, 클릭할 때 해당 root의 현재 input/output을 조회한다. 초기 스캔이나 `htmx:load` 초기화 없이 최초 화면과 이후 추가된 여러 UI가 독립적으로 작동한다.
- root별 최신 작업 객체를 `WeakMap`에 저장한다. 버튼은 계속 누를 수 있으며, 뒤 작업이 시작되면 앞 작업의 성공·실패 안내를 무효화한다. 호출 시점 input의 `value`를 Clipboard API에 전달한다.
- 성공 문구는 `writeText()`가 성공한 뒤에만 표시한다. 권한 거절, API 미지원 등 예외는 실패 문구로 처리한다. 새 작업을 시작하면 이전 안내를 비운다. 안내는 기존 `role="status"` output의 `textContent`에 넣고, 기본 button의 키보드 동작과 초점은 유지한다.
- 완료 시 최신 작업 여부, root 연결 여부, 시작 당시 input/output과 현재 노드의 동일성을 모두 확인한다. 제거된 UI나 교체된 자식에 대한 결과는 새 DOM에 적용하지 않는다.
- `htmx:beforeCleanupElement`에서는 제거 영역에 속한 root와 실제 종속 input/output의 작업만 무효화한다. 살아 있는 root의 무관한 자식 정리는 작업을 없애지 않는다. root의 자식이 교체된 뒤 다시 클릭하면 새 노드를 사용한다.
- Clipboard Promise 자체는 취소하지 못한다. 무효화는 안내에 적용되며, 이미 시작한 시스템 클립보드 쓰기 순서까지 보장한다고 주장하지 않는다. 타이머·observer·object URL을 만들지 않아 별도 자원 해제나 공통 로더는 필요 없다.

## 추가 판단

1. 기본 `details`/`summary`로 요구를 충족하는 FAQ에는 JS 파일을 만들지 않는다.
2. 할인금액 계산과 관리자 여부의 업무·권한 판정은 서버 소유이므로 UI JS로 옮기는 제안을 수용하지 않는다. 서버가 결정한 표시 데이터를 소비하는 것과 업무 판정을 수행하는 것은 구분한다.
3. 기존 프로젝트가 사용자 JS를 금지한다면 이 스킬을 읽은 것만으로 예외가 생기지 않는다. 해당 충돌을 보고하고 JS 구현을 보류한다. 금지 규칙이나 백스톱을 임의로 수정하지 않는다.

## 검증 범위

`node --check /tmp/dddjango-ui-js-20260905/holdout/copy_feedback.js`를 실행했고 종료 코드 0으로 구문 확인을 통과했다. 요청에 따라 브라우저·패키지는 설치하지 않았고 브라우저 실행, 실제 HTMX HTTP 교체, 시스템 클립보드와 권한 검증은 수행하지 않았다. 다중 root 격리, 성공/실패 완료 순서 역전, root 및 input/output 교체·삭제, 이웃 UI 보존, 키보드 클릭 경로는 평가자의 실제 브라우저 평가 대상이다.

Serena: skipped — 지정된 스킬 문서와 임시 단일 기능 파일만 다루므로 기본 도구로 충분.
