## 규율 감수 리포트 — `lab/ui_lab` (범위 한정 증적 종결 재확인, G2 직전)

감사 범위(지시된 대로 한정): `evidence/discipline-review-1.final.md`의 **미검증 조건 2건**(비이미지 MIME 조기 차단 분기 / HTMX 실패 시 DOM 유지 + 실제 재시도)만. 새로 읽은 증적은 `evidence/browser-2.json`·`evidence/unchanged-source-proof.json`이고, 대조 코드는 `web/static/js/image_preview.js`(해당 분기 확인 목적)뿐이다. 그 밖의 점검은 재개하지 않았고 스코프도 넓히지 않았다. 브라우저 실행은 내가 하지 않았다 — 아래 동작 판정은 전부 harness 기록의 인용이다.

---

### 결론

**APPROVED 재확인 — blocker 0건 · important 0건.** 지시된 정확히 두 누락이 닫혔고, 이전 nit 4건과 나머지 승인 결과는 그대로 유지한다. 신규 지적·선택 작업 권고 없음.

### 1. 비이미지 MIME 조기 차단 — 종결

- 코드 경로: `image_preview.js:50-61` — `select()`가 ⓐ `releaseUrl`(:52) ⓑ `clearOutput`(:53) ⓒ 세대 증가(:54) 후 `file.type.startsWith("image/")` 실패 시 `showError()` 후 **즉시 반환**하므로 `URL.createObjectURL`(:62)에 도달하지 않는다.
- 증적 대조(`browser-2.json` `non_image_mime_probe`): `mime: "text/plain"`, `new_url_allocations: 0`(ⓒ 이전 반환과 일치), `prior_url_revocations: 1` + `prior_url: blob:…f6ac11cb…`(ⓐ와 일치, 해당 URL은 `resources.revoked`에도 존재), `stale_success_cleared: true`(ⓑ와 일치), `status: PASS`.
- 판정: 이전에 "두 실패 경로 중 decode error만 실행됨"이던 공백이 실제 실행으로 닫혔다. 남는 미검증 없음.

### 2. HTMX 실패 시 기존 DOM 유지 + 실제 재시도 — 종결

- 증적(`injected_http_failure`): `status: 503`에서 `retained_revision: rev-533259301ce9`·`retained_url: blob:…c9b38564…` 유지, 이어 **실제 HTTP `retry_status: 200`** 과 `retry_revision: rev-5118cd26356f`.
- 교차 확인: `rev-533259301ce9`는 실패 직전 마지막 성공 패널 응답과 동일하고, `rev-5118cd26356f`는 `htmx_responses` 마지막 실제 200 fragment로 실재한다(`requests` 말미 `/lab/ui-lab/fragment/panel/` xhr 3건과 정합). 즉 유지→재시도가 모의 이벤트가 아니라 실HTTP 왕복이다.
- 잡음 처리: `console_errors: []`·`page_errors: []`이고 503 관련 2건은 `expected_console_errors`로 **별도 라벨**되어 있어 요구 18(콘솔 청결)의 판정을 오염시키지 않는다.
- 정확성 유지: 이 증적 파일이 기록하는 유지 항목은 `retained_revision`·`retained_url`이다. Coordinator 요약의 "focus 유지"는 이 JSON의 명시 필드로는 확인되지 않으므로, 나는 리비전·미리보기 URL 유지까지만 인용한다(반송 사유 아님, 인용 정확성 기록).

### 3. 코드 동일성 / 회귀

- `unchanged-source-proof.json`: `matches_backstop_source_hashes: true`, 생성 소스 해시가 backstop-1 및 승인 감사 시점과 전부 동일 — 이번 증적은 **같은 코드에 대한 추가 프로브**다. 재감사 대상 변경 없음.
- `browser-2.json`의 I1~I12 전건 PASS, `django_check.exit_code 0`, `script_network_counts` 각 1회, fragment HTML 내 `<script>` 0 — 이전 결과와 동일하게 재현.
- `document.readyState === "loading"` 분기는 `defer` 호스트에서 도달 불가라는 이전 판단 그대로 유지(적용 불가 조건이며 누락 아님).

### 발견

1. **발견**: 증적 메타 불일치 — Coordinator 요약은 "34 web files unchanged"이나 `evidence/unchanged-source-proof.json:3`은 `file_count: 33`이고 `source_hashes` 항목도 33건(`:5-37`)이다. 동일성 주장의 근거는 파일 수가 아니라 전 항목 해시 일치(`:2`)이므로 실질 영향은 없다. — nit
   **권고**: 코드 변경 불필요. 기록 대조 시 파일 수는 증적 파일의 33을 정본으로 인용한다.

이전 리포트의 nit 1~4(화면 CSS 내 문서 리셋 / 명세 §6 empty 노드 열거 누락 / `image_preview.js:139-141` 무효과 대입 / 세대 번호 이중 표현)는 **그대로 유지**하며, 모두 코드 변경 없이 수용 가능한 상태다.

### 남은 미검증 조건 (반송 사유 아님)

- 시각 "시안 일치" 판정은 원본 부재로 성립하지 않음(렌더 정상만 확인).
- 브라우저 표본은 Chromium **152.0.7977.82** 1종이며 통계적 증명이 아님.
- `readyState === "loading"` 방어 분기는 이 defer 호스트에서 적용 불가.

### 현재 정본

- **최종 권위 브라우저 증적 파일**: `evidence/browser-2.json` (label `browser-2`, lane `claude`, `status: PASS`) — `browser-1.json`을 대체하는 최신 정본이며, browser-1의 스크린샷·정적 렌더 증적은 보조로 유효하다.
- **소스 동일성**: `evidence/unchanged-source-proof.json` — `matches_backstop_source_hashes: true`, 33개 `web/**` 파일 해시가 backstop-1/승인 감사본과 전부 동일. 대표 지문: `web/static/js/image_preview.js` `97b2ce7a…`, `web/static/js/password_visibility.js` `e7727507…`, `web/lab/ui_lab/view_model/ui_lab_view_model.py` `9ffaf565…`, `web/base/base.html` `0873ce07…`(무수정), `web/static/htmx/htmx.min.js` `71ea6718…`(공식 HTMX 2.0.10 지문 일치).