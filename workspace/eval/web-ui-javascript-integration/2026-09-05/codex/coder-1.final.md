승인된 단일 UI screen slice를 구현했습니다. `/lab/ui-lab/`에서 두 password toggle, 두 local image preview, native help disclosure와 세 종류 HTMX 교체를 제공합니다.

현재 앱의 `.agents/skills/` 배포본에서 coder-web 및 필수 지식을 읽었습니다. Coordinator가 수정한 static prefix를 그대로 소비하여 core는 `web/htmx/htmx.min.js`, 기능 자원은 `web/js/...`·`web/css/...`로 연결했습니다. `design.md`, host/base, 의존성, Git은 변경하지 않았고 영구 테스트나 추가 문서를 생성하지 않았습니다.

**실제 검증 결과**

- 각 Python 구현 단계의 `py_compile`: 통과.
- 각 단계 및 최종 `python -B manage.py check`: **0 issues**, 기존 baseline 대비 신규 이슈 없음.
- 두 기능 JS의 `node --check`: 통과.
- Django **5.2.17**의 임시 Client 검증: 페이지 HTTP 200, 중복 없는 DOM ID, 각 입력 2개, native help, 외부 script 순서 확인.
- A/B × 3종 fragment를 각각 3회 렌더: 총 **18회** 모두 새 revision, 올바른 target root, `no-store`, script/link/page wrapper 부재 확인.
- 페이지·fragment POST 405, 잘못된 panel key 404 확인.
- core·기능 JS·CSS·tokens의 static 이름 5개 모두 corrected host 설정으로 resolve 확인.

**정확한 변경 목록: 신규 20개, 수정 1개**

수정:
```text
web/urls.py
```

신규:
```text
web/lab/__init__.py
web/lab/urls.py
web/lab/widget/.gitkeep
web/lab/ui_lab/__init__.py
web/lab/ui_lab/view/__init__.py
web/lab/ui_lab/view/ui_lab_view.py
web/lab/ui_lab/view/ui_lab.html
web/lab/ui_lab/view_model/__init__.py
web/lab/ui_lab/view_model/ui_lab_view_model.py
web/lab/ui_lab/state/__init__.py
web/lab/ui_lab/state/ui_lab_state.py
web/lab/ui_lab/section/ui_lab_fixture.html
web/lab/ui_lab/section/ui_lab_panel.html
web/lab/ui_lab/section/ui_lab_preview.html
web/lab/ui_lab/section/ui_lab_preview_body.html
web/lab/ui_lab/section/ui_lab_note.html
web/static/htmx/ui_lab_refresh.html
web/static/js/password_visibility.js
web/static/js/image_preview.js
web/static/css/ui_lab.css
```

**남은 상태:** 확인된 구현 blocker는 없습니다. 실제 브라우저 조작, HTMX 네트워크 교체, object URL 해제 계수, decode 실패·지연 주입, 키보드·viewport·console 검증과 canonical backstop은 이번 역할에서 실행하지 않았습니다. Coordinator의 독립 harness 검증이 남아 있으며, 브라우저 통과나 스크린샷 증적을 주장하지 않습니다.

Serena: 생략 — 기본 파일 도구로 구현했으며 검색·로드·초기화하지 않았습니다.