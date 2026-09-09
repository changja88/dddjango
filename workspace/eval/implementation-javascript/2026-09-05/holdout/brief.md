# 별도 UI 적용 과제

신규 implementation-javascript SKILL.md와 필요한 reference를 읽어 적용한다. 임시 앱에서는 UI JS 사용이 승인됐다. 지정 폴더에 copy_feedback.js 하나와 report.md를 작성한다. 다른 프로젝트·평가 결과는 읽지 않는다.

HTMX 2.0.8 페이지의 여러 복사 UI가 독립 작동한다. DOM 계약:

```html
<section data-copy-feedback><input data-copy-text value="복사할 내용"><button type="button" data-copy-button>복사</button><output data-copy-status role="status"></output></section>
```

클릭하면 해당 input의 현재 값을 clipboard에 복사하고 성공 후 `복사했습니다`, 실패 시 `복사하지 못했습니다`를 표시한다. 사용자가 다시 눌러 뒤 작업이 먼저 완료할 수 있다. root 자체 또는 그 안의 input/output이 HTMX로 교체/삭제될 수 있다. 이미 시작한 오래된 작업의 안내가 새 UI나 더 최근 결과를 덮으면 안 된다.

스크립트는 외부 classic defer로 한 번 로드한다. 현재 마크업을 그대로 사용하고 서버 요청/프레임워크/전역 공통 로더는 불필요하다. 브라우저 평가는 평가자가 수행하며 구현자는 구문 확인까지만 보고한다.

report에 추가 판단도 적는다: 기본 details/summary로 충분한 FAQ에 JS 파일이 필요한가; 할인금액·관리자 여부 판정을 UI JS에 넣자는 제안의 처리; 기존 프로젝트가 사용자 JS를 금지하는데 이 스킬만 읽은 경우의 처리.
