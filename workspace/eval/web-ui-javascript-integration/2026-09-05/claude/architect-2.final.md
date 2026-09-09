설계 명세 1건을 작성했다. 코드는 쓰지 않았다.

**산출 경로**: `/Users/hyun/Desktop/dddjango/workspace/eval/web-ui-javascript-integration/2026-09-05/design.md`

**사전 조사(실사)**: `web/` 트리(urls.py 빈 urlpatterns · base/base.html · design_system/foundation/tokens.css 9토큰 · motion.css 빈 파일 · component/ 은 .gitkeep만 · static 4폴더 + vendored htmx) 및 `host/settings.py`(TEMPLATES DIRS=web, STATICFILES_DIRS 프리픽스 튜플 교정본, MIDDLEWARE=[])를 직접 읽고 소비했다. 기존 화면 관례는 골격 외 없음.

**주요 결정 요약**
- G0 ① 신설 영역 `lab` / 화면 개념 `ui_lab` 1개, 삼총사+페이지 템플릿 + section 4종. revision marker·패널별 제어 활성 판정이 서버 표시 판정이므로 정적 화면 판례가 아니라 VM 필요(undecidable-web §1).
- form 없음(제출·서버 검증 없음) → `form/` 미생성. static_only → `client/**` 0, 인용 엔드포인트 0.
- swap 경계 3종 확정: 패널 B **root outerHTML** / 유지되는 패널 A의 **종속 자식(미리보기 소유자 root)** / 미리보기 root 안의 **독립 자식(노트, 자원 비종속)** — 노트를 미리보기 root **내부**에 두어 자식 정리와 소유자 정리를 harness가 구별 가능하게 했다. fragment 3라우트는 전부 부작용 없는 GET, 이름은 `lab:ui_lab*`, 리터럴은 `web/lab/urls.py` 단독.
- 수명 메커니즘을 코더가 발명하지 않도록 확정: document 위임 1회 등록, `activate`(readyState/`htmx:load` + matches+자손), hidden 제어 가시화, WeakMap `{objectUrl, generation}`, capture-phase `error`/`load` + src 동일성 검증, `htmx:beforeCleanupElement`에서 **출력 노드 포함 여부로** 소유자 정리와 독립 자식 정리를 분기, textContent 전용 출력, fragment 무-script·페이지 scripts block 1회 외부 로드(classic defer).
- 분류: native disclosure = **S3**(details/summary, 기능 JS 0) / password_visibility.js·image_preview.js = **S1**(승인된 로컬 UI JS). 러너 채택 0 → motion.js 미설치, base.html 수정 없음.
- 토큰 전수: 기존 9건 전부 채택 + 신규 1건(`--border-width-hairline`, 출처=자체 설계) 등록. 시안·motion-notes·render-audit·manifest 부재 → 각 처분표 비대상(0=0 대조), 이탈 표 행 0.
- 신규 21 + 수정 2 = 파일 목록 전체 확정, 자기모순·백스톱 정합 스캔 각 1회 수행 기록.

**미해결 blocker: 없음.** (참고 사항 2건은 명세 §11에 기록: host `MIDDLEWARE=[]` — 이번 화면은 state-changing 0이라 무영향이나 향후 POST fragment 시 배선 선행 필요 / `system-ui` 서체 환경 의존은 행위 목록 16번으로 확인 항목화.)

브라우저 실행·`manage.py check`는 이 역할에서 수행하지 않았다 — 성공 주장 없음.