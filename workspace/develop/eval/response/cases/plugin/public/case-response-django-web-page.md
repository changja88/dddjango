Django 서버 렌더링 주문 상세 화면을 설계하려고 해.

파일 수정 없이 답변만 해줘. 다음 항목을 구현 판단 기준으로 정리해줘.

- TemplateView, Generic CBV, FBV 중 무엇을 선택할지
- base template과 include/component를 언제 나눌지
- page-specific CSS/JS를 static file로 둘 때 template에서 어떻게 연결하고 검증할지
- memo 같은 선택 표시값이 `None` 또는 빈 문자열일 때 template이 raw fallback을 결정하지 않게 하는 기준
- web form은 GET, valid POST, invalid POST, error rendering, `ModelForm.Meta.fields` 명시를 어떻게 확인하고, HTMX fragment가 있을 때 CSRF, auth/permission, progressive enhancement를 어떻게 확인할지
- REST API, Django Ninja Router/Schema, ORM/migration/transaction, pytest fixture 상세 구현으로 넘어가야 하는 경계
- render/browser/collectstatic/security check를 실행하지 않았을 때 완료 보고에 어떻게 적을지
