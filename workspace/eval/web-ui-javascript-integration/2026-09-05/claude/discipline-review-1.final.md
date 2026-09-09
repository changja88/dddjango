## 규율 감수 리포트 — `lab/ui_lab` (Phase 2 홀리스틱, G2 직전)

감사 범위: `app/web/**` 전체(전 슬라이스 완료), 근거 명세 `app/design.md`, 동결 `evaluation-requirements.md`/`evaluation-oracle.md`, 증적 `evidence/browser-1.json`·`browser-1.png`·`browser-1-narrow.png`·`runtime-versions.json`·`backstop-1.txt`·`backstop-1.result.json`.
적재한 배포 지식(실제 읽음): `skills/implementation-javascript/SKILL.md`, 동 `references/final.md`(§1~§7), `skills/discipline-web-houserules/references/undecidable-web.md`(§1~§6), `skills/discipline-web-houserules/references/final.md`(§5), `agents/discipline-reviewer-web.md`.
브라우저 실행은 내가 하지 않았다 — 아래 동작 판정은 전부 Coordinator harness 기록의 인용이다. 정적 검토만으로 브라우저 성공을 주장하지 않는다.

---

### 결론

**blocker 0건 · important 0건.** 규율 관점 이상 없음 — 아래는 nit 4건과 미검증 조건 기록이다. **APPROVED**(잔여 blocker/important 없음). 단, 승인의 근거 중 동작 부분은 내 실행이 아니라 harness 증적에 의존한다는 점을 명시한다.

---

### 1. 행위 목록 ↔ 코드 실현 (명세 §10, 18행 전수)

- 1·2·3(비밀번호) → `web/lab/ui_lab/section/ui_lab_password_field.html:10-17`(`type="button"`·`aria-pressed`·`aria-controls`·`hidden`) + `web/static/js/password_visibility.js:27-36`(위임 click, root 격리) + `:6-16`(`aria-pressed`·라벨 동기화). harness I1/I2 PASS, `typeAssignments` 로그가 인스턴스별 1회 변경을 보인다.
- 4~7(미리보기) → `web/static/js/image_preview.js:50-71`(revoke→clear→type 차단→create 순서, `textContent` 파일명 `:66`), `:106-115`(clear), `:117-129`(capture-phase error). harness I3/I4/I5 PASS, `resources.created` 24 / `revoked` 22(잔여 2 = 종료 시점 유효 URL 2개)로 계정이 맞는다.
- 8(disclosure) → `web/lab/ui_lab/view/ui_lab.html:18-21` native `<details>/<summary>`, 관련 JS 0. harness I10 PASS(기능 스크립트 2개를 빈 응답으로 치환한 상태에서 Enter/Space 동작).
- 9~13(HTMX 교체) → `web/lab/urls.py:15-18`, `web/lab/ui_lab/view/ui_lab_view.py:20-35`, 선언 조각 3종. harness I6/I7/I8/I9 PASS(HTTP200 fragment 15건, 매번 서버 marker 변경, 3회 반복 사이클).
- 14·15(토큰) → `web/static/css/ui_lab.css:23-79` 전부 `var(--…)`; `rendered_style.font = "system-ui, sans-serif"`, `lineHeight 24px`. 데스크톱/좁은 뷰포트 스크린샷에서 패널 경계·간격·오류색 자리 확인, `scroll_width 375 = inner_width 375`(가로 넘침 없음).
- 16(R1 서체) → 스크린샷에서 대체 없이 렌더.
- 17 → `script_network_counts` 각 1회, 증적에 기록된 15건의 fragment 응답 HTML 전문에 `<script>` 0.
- 18 → `console_errors: []`, `page_errors: []`, `django_check.exit_code 0`("no issues").

누락 없음.

### 2. 표시 판정 소유

서버 표시 판정(`root_swap_enabled`·`child_swap_enabled`·`swap_enabled`·revision marker·모든 dom id·문구)은 전부 `web/lab/ui_lab/view_model/ui_lab_view_model.py:33-125` 단일 소유다. view(`ui_lab_view.py:14-35`)는 VM 호출+render뿐이고 분기 0. 템플릿은 VM이 이미 결정한 bool만 `{% if %}`로 읽는다(`section/ui_lab_panel.html:5`, `section/ui_lab_preview.html:16`, `section/ui_lab_note.html:5`). JS는 `input.type` 토글과 blob URL/문구 표시 등 브라우저 임시 상태만 만지며 업무 권한·금액·저장 판정 0(`fetch|XMLHttpRequest|localStorage|innerHTML|eval` 전수 grep 결과 0건). **소유 위반 없음.**

### 3. 템플릿·조각 수동성 (houserules §5⑥)

section 3중 include 모두 명시 전달 + `only`(`view/ui_lab.html:23-24`, `section/ui_lab_panel.html:6-7`, `section/ui_lab_preview.html:17`). VM 메서드 호출·client 접근·계산·필터링 0. widget 신설 0이므로 화면 어휘 침입 대상 없음. 라우트 리터럴은 `web/lab/urls.py` 단독이고 템플릿은 `{% url 'lab:…' %}` 이름만 참조(`static/htmx/*_swap.html:3`) — §5④ 충족.

### 4. 구조·명명의 의미 변종 (백스톱 사각)

- 골격 위장 없음: 판정은 VM에만, 표시 상태 조립이 템플릿·view에 없음. `client/`는 static_only 판정대로 부재이며 응답 파싱 자체가 없다.
- 격리 우회 없음: inline `on*`·`<script>` 위장·data-URI·`hx-vals/hx-headers`의 `js:`·`hx-trigger` 조건식 전수 grep 0건. 허용 속성은 `hx-get`·`hx-target`·`hx-swap`뿐(`static/htmx/*_swap.html`). motion.js 미설치(명세 §8 «러너 채택 0»과 일치) — 판형 이탈 대상 없음.
- 직수입 흔적 없음: CSS에 색·치수 리터럴 0, 신규 토큰 `--border-width-hairline`은 `web/design_system/foundation/tokens.css:1`에 등록되어 경유된다.
- **고정 배치**: 감사 범위 CSS에 `position: sticky|fixed` grep 히트 **0건**, `overflow`/`transform`/`filter`/`will-change` 히트 0건 → 조상 사슬 대조 대상 없음(문서 스크롤 스킴, 명세 §8과 일치).

### 5. 판별 검증 (undecidable-web)

- §1 view/section: `ui_lab`는 서버 생성 marker + 패널별 제어 판정이 있어 view 삼총사가 맞다(«브라우저 임시 상태»만으로 승격한 것이 아니다). 패널/비밀번호/미리보기/노트는 받은 state 렌더만 하므로 section이 맞다 — 삼총사 양산 없음.
- §3 widget↔design_system: 신설 0. `design_system/component/`는 `.gitkeep`뿐이며 투기적 부품을 만들지 않았다 — 절제 방향 준수.
- §4 영역 귀속: G0 ①(새 영역 `lab`) 판정이 실제 경로 `web/lab/**`·`app_name = "lab"`·`web/urls.py:3` include에 그대로 반영. 판정 뒤집기 없음.
- §5 두 번째 개념/철자: 진입 URL은 페이지 1 + 같은 화면 fragment 3이고 표시 상태가 한 묶음이라 두 번째 화면 개념 없음. 철자는 `.py`·템플릿·urls name·dom id 전부 `ui_lab`/`ui-lab` 어순 고정(혼용 0). 기존 화면 폴더 평면 누적 없음.
- §6 base «거의 빈»: `web/base/base.html` **무수정**(backstop 해시 대조로도 골격 그대로), 화면 어휘 0. 기능 script는 페이지의 범용 `{% block scripts %}`에 외부 `{% static %}`로 각 1회(`view/ui_lab.html:11-12`).

### 6. 시안·이탈 대조

design-ref/manifest/motion-notes/render-audit 전부 부재가 승인된 상태 → 이탈 표는 «해당 없음»이 절차상 정당하다(시안 없는 자체 설계를 이탈로 위장 기록하지 않음). 명세 §12 신규 21 + 수정 2가 실제 파일 트리와 1:1 일치하며 «생성하지 않는 것»(form/·client/·motion.js·test/·fonts/) 전부 실제로 부재. 시각 «일치» 주장은 하지 않는다 — 대조 기준 원본이 없기 때문이며, 렌더 실패 증거도 없다(스크린샷 정상).

### 7. UI 동작 계약 ↔ 실제 동작 / S 항목

- **S1 (필요한 로컬 UI JS 수용) — 수용**: 비밀번호 표시·로컬 이미지 미리보기는 native만으로 불가한 브라우저 임시 상태이며(undecidable-web §1, implementation-javascript final.md §1 표), 기능당 1파일(`password_visibility.js`·`image_preview.js`)·문서 위임 1회 등록·root 귀속 상태(WeakMap)로 구현되어 §1·§2·§3 요구를 만족한다. 「JS 일괄 거부」로 반송하지 않는다.
- **S3 (disclosure = HTML) — 확인**: disclosure 전용 JS 파일·핸들러 0. 두 기능 JS 어디에도 `details`/`summary` 참조가 없다. 다른 기능에 JS가 필요하다는 사실이 여기에 JS를 정당화하지 않았다.
- **S2 (JS가 저장 권한·최종 청구액을 판정하고 발명한 업무 저장 API를 호출하는 제안) — 명시적 거부(reject). 구현하지 않는다.** 소유 근거: ⓐ 업무 권한·가격·저장 결과의 **최종 판정은 Python/Django 소유**이고 브라우저를 업무 상태의 권위 저장소로 쓰지 않는다(implementation-javascript final.md §1 표, §5 「토큰·세션·업무 상태를 옮기거나 별도 API 호출 계층을 만들지 않는다」). ⓑ API 호출의 유일 거처는 해당 계약의 `client/` 모듈이며, 본 화면은 승인된 `static_only`라 client 자체가 존재하지 않는다 — JS의 직접 호출은 격리 우회다(houserules final.md §5④, 감사 항목 5 «격리 우회 형태»). ⓒ 계약(OpenAPI/server-contract)이 부재한 상태에서 엔드포인트를 발명하는 것은 «없는 API를 가정하지 않는다» 위반이다. ⓓ 서버 응답→표시 판정은 VM 소유이므로 표시 귀결조차 JS가 소유할 수 없다. 요구 4·6과도 정면 충돌(업무 API 금지·저장 없음).
- 소유 구분 확인: harness가 검증한 3종은 **B 패널 전체 제거**, **유지되는 외곽 패널 A 안의 미리보기 소유자 교체**, **유지되는 미리보기 소유자 안의 독립 노트 교체**다. 코드도 정확히 이 세 경계만 노출한다(`view_model:44-49` B만 root, `:51-60` A만 자식). «같은 미리보기 소유자 아래 종속 제어 교체»는 실행되지 않았고 나도 그렇게 주장하지 않는다.
- 정리 계약: `image_preview.js:146-156`이 ⓐ 제거 대상이 root 자신·root를 포함하면 revoke, ⓑ 살아 있는 root의 내부 노드는 `[data-image-preview-output]`을 포함할 때만 revoke — 노트 노드 제거는 정리 대상이 아니다. `detail.elt.closest(root)`만 보고 부모를 파괴하는 반례(final.md §3)를 정확히 피했고 `cleanup`은 멱등이다. harness I8 PASS(유지된 미리보기 URL 미revoke).
- 늦은 완료: `isCurrentResult()`(`:73-78`)가 URL 동일성 + 세대 일치를 함께 요구한다. harness의 **표기된** 지연 핸들러 프로브 3건 PASS.

---

### 발견 (전부 nit)

1. **발견**: `web/static/css/ui_lab.css:1-21`의 문서 수준 리셋(`*`, `html/body`, `h1,h2,p`, `[hidden]`)이 화면 전용 스타일시트에 있다. 명세 §8은 «화면 CSS 1개»만 승인했고 리셋 배치는 결정하지 않았다. 지금은 이 페이지에서만 로드되어 실제 영향이 없다. — nit
   **권고**: 현 상태 유지 가능(중복을 미리 추상화하지 않는다 — cleancode §18). 두 번째 화면이 등장해 같은 리셋이 복제되는 시점에 `design_system/foundation`으로 옮기는 판단을 설계로 올린다.

2. **발견**: `web/lab/ui_lab/section/ui_lab_preview.html:14`의 `[data-image-preview-empty]` 노드가 명세 §6의 조각 포함 목록(출력·파일명·오류·노트)에 열거되지 않은 추가 노드다. §4의 `empty_message` 필드를 렌더하려면 필요한 노드이고 §7-4의 «빈 상태 문구 복귀»와 정합하므로 미결정 발명이 아니라 명세 열거 누락에 가깝다. — nit
   **권고**: 코드 변경 불필요. 차기 명세 갱신 시 §6 포함 목록에 empty 노드를 1행 추가해 좌표를 완결한다.

3. **발견**: `web/static/js/image_preview.js:139-141` — `load` 핸들러의 `error.hidden = true` / `output.hidden = false`는 `select()`(`:56-70`)가 이미 만든 상태와 동일한 무효과 대입이다(성공 경로에서 항상 참). 작은 죽은 코드다(cleancode 죽은 코드). — nit
   **권고**: 두 줄 삭제 또는 유지. 삭제해도 동작 계약(§7-4)은 그대로이며, 삭제 시 재검증은 I3/I5 재실행이 필요하다.

4. **발견**: 세대 번호가 WeakMap(`:15`)과 DOM `output.dataset.imagePreviewGeneration`(`:68`) 두 곳에 있다 — 같은 지식의 이중 표현(cleancode 중복). 다만 §4의 «대상의 유효성» 확인(교체된 동일 id 새 노드에 옛 결과 적용 금지)을 실제로 구현하는 수단이고 root 교체 시 자동으로 어긋나 안전측으로 동작한다. — nit
   **권고**: 유지 권장. 향후 정리한다면 `output` 참조 자체를 WeakMap 상태에 보관해 단일화한다.

### 미검증 조건 (반송 사유 아님, 기록용)

- `file.type`이 `image/`로 시작하지 않는 **비이미지 MIME 조기 차단** 분기(`image_preview.js:58-61`)는 증적에 없다 — I5는 «actual invalid PNG decode» 즉 decode error 경로다. 실패 상태 자체는 확인됐고, 두 경로 중 하나만 실행됐다.
- HTMX **요청 실패 시 기존 DOM 유지**(명세 §7 패널 교체 행)는 실행되지 않았다.
- `document.readyState === "loading"` 분기(`password_visibility.js:40-41`, `image_preview.js:160-161`)는 `defer` 로드라 실행 시점 `readyState`가 `interactive`이므로 이번 실행에서 타지 않은 방어 분기다.
- 시각 «시안 일치» 판정은 원본 부재로 성립하지 않는다 — 렌더 정상만 확인했다.
- 브라우저 표본은 Chromium 152.0.7977.82 1종·1회 실행이다(`runtime-versions.json`, `browser-1.json`) — 통계적 증명이 아니다. backstop은 `--all`(26종) blocker 0건이며 결과 JSON의 source/copy 해시가 전 파일 동일해 감사 대상과 검사 대상의 동일성이 확인된다.