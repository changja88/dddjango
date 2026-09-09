## 화면 설계 리뷰 노트 — 범위 한정 재리뷰(중요 발견1 종결 확인)

**리뷰한 설계 경로(확인)**: `/private/tmp/dddjango-web-js-integration-20260905/claude/app/design.md` — 이것만 권위본으로 읽었다. 이전 라운드 노트가 가리키던 `.../workspace/eval/web-ui-javascript-integration/2026-09-05/design.md`(`evidence/design-review-1.md` 머리말)는 이번 판정 대상이 아니며, 그 산출이 app 안으로 바이트 복사된 뒤 교정됐다는 Coordinator 사실만 인용한다.
**참조한 증적**: `evidence/design-review-1.md`(직전 발견 목록), 실제 host 픽스처(`web/base/base.html`·`web/urls.py`·`web/design_system/foundation/tokens.css`·`web/design_system/component/.gitkeep`·`web/static/**`), 배포본 `architecture-web`(SKILL·final.md §1·§3·§4·§7)·`undecidable-web.md`.
**입력 조건 재확인**: static_only 승인(OpenAPI·server-contract 부재, 업무 API 소비 0) / 시안·design-tokens·asset-manifest·motion-notes·render-audit 전부 부재(native design 승인) → 점검 항목 5·6ⓐⓑⓒⓓⓔ는 입력 채널 부재로 **해당 없음**, 7은 «인용 0건 + 발주 불필요» 처분이 정확.

## 판정: **APPROVED** — blocker 0건, important 발견1 **종결(closed)**

### 1. important 발견1 종결 검증 (요청된 정확 교정)

- **확인**: §6의 신설 표 «HTMX 선언 조각의 include 호스트·지배 플래그(1:1 확정)»가 세 조각을 각각 교체 단위 자신에 고정한다 — `static/htmx/ui_lab_panel_swap.html` → `section/ui_lab_panel.html` / `panel.root_swap_enabled`(패널 B만), `..._preview_swap.html` → `section/ui_lab_preview.html` / `preview.child_swap_enabled`(패널 A만), `..._note_swap.html` → `section/ui_lab_note.html` / `note.swap_enabled`(패널 A만). 각 행에 `{% if %}` 조건 판형까지 명시됐다.
- **확인**: "페이지 템플릿(`ui_lab.html`)에는 어떤 선언 조각도 include하지 않는다"가 명문화되어, 직전 발견의 실패 모드(outerHTML 교체 시 트리거 소실 → I7 반복 swap 붕괴)가 봉쇄됐다. 근거 정합: architecture-web final.md §4 «HTMX 선언 조각은 `static/htmx/<기능>.html`에 두고 section/페이지에서 include».
- **확인(중복 표기 일치)**: 같은 1:1이 §7 UI 동작 계약 표의 «JS/HTMX 파일» 칸 3행(“**include 호스트 = section/… (교체 단위 자신)**, 조건 `{% if … %}`”), §12 파일 목록 19–21행 비고, §12 «템플릿 참조 경로» 문단(“페이지가 아니라 §6 표가 지정한 section에서만”), §13 수량 대조(`fragment 라우트 3 = view 함수 3 = section swap 단위 3 = 선언 파일 3 = include 호스트 3 = 지배 플래그 3, 페이지 include 0`)에서 **모순 없이 반복**된다.
- **확인(실제 swap 경계 반복 일치)**: `#ui-lab-panel-b`/`#ui-lab-preview-a`/`#ui-lab-note-a` + `outerHTML` 조합이 §6 라우팅 표 · §6 DOM id 계약 · §6 선언 조각 문단 · §7 3개 행에서 전부 동일하다. 표시 판정 소유는 VM 단독(§4 `root_swap_enabled`/`child_swap_enabled`/`swap_enabled`)이며 템플릿은 bool 표시 분기만 한다 — §3 view 수동성 위반 서술 0건.
- **확인(교체 후 재실행 가능성)**: fragment 3개가 각각 패널 B state·패널 A preview state·패널 A note state를 렌더하므로 해당 플래그가 참으로 유지되어 교체된 HTML 안에 트리거가 다시 존재한다 — I7 성립.

### 2. 새 blocker 스캔 — **없음**

- 라우팅(§4 항목): 리터럴은 `web/lab/urls.py` 단독(`app_name="lab"`), `web/urls.py`(현재 `urlpatterns: list = []`)에 include 1줄 합산, fragment 3개가 이름 붙은 path로 소속 view 영역 urls에 존재, 템플릿은 `{% url 'lab:…' %}` — architecture-web §7 준수.
- host 경로 재대조: 실제 `base/base.html`이 `{% static 'design_system/foundation/tokens.css' %}`·`{% static 'web/htmx/htmx.min.js' %}` defer, 범용 3블록 보유 → 명세 §1·§7-1의 `web/js/…`·`web/css/…` 프리픽스와 base 무수정 결정이 교정 픽스처와 일치. 선언 조각 include 경로(`static/htmx/…`, TEMPLATES DIRS=`web/`)와 static URL 프리픽스를 혼동하지 않았고, static URL을 fragment endpoint로 쓰지 않는다(§4·§5).
- 계약·격리: 인용 엔드포인트 0, `client/**` 미생성, driving_layer/도메인 어휘 0 — 침묵 오발화 없음(§6).
- design_system: `component/`는 `.gitkeep`뿐임을 직접 확인 → 재사용 후보 0, 신설 0. `tokens.css` 실측 9토큰 전수 채택(빈칸 0) + 신규 1건(`--border-width-hairline`) 출처 기록 — §8 준수.
- 행위 목록(18건) ↔ 분해 조각 상호 커버 유지, 미사용 조각 0.

### 3. 직전 nit 4건 — 유지·이월(범위 확대 없음)

nit2(disclosure 소유 템플릿 미기재)·nit3(노트 «안» 배치 결정 기록)·nit4(`autocomplete`/`name` 값 미확정)·nit5(`--text-color` 테두리 겸용)는 현재 설계에서 변경되지 않았으나 **모두 비차단**이며 코더 진행을 막지 않는다. 이번 범위에서 새 권고를 추가하지 않는다.

**결론**: important 발견1은 §§6/7/12/13의 1:1 확정으로 종결됐고, 반복 표기의 swap 경계가 전부 일치하며 새 blocker는 없다 — **현재 design.md는 coder 착수 준비 완료(APPROVED)**. 브라우저 실행·`manage.py check`는 이 역할에서 수행하지 않았다(성공 주장 없음, harness 소관).