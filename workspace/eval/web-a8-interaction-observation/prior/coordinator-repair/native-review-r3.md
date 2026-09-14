검토를 마쳤다. 아래가 독립 검토 원문이다(Coordinator가 그대로 `coverage-review.md`에 보존).

---

# G0 입력범위 검토 — A8 web 관계인 (r3 · 2026-09-13)

reviewed-input: db6b70032604f5a5da4ce295680b11e3633814220ea04b1e63162c5e2261fcd9
review-result: pass

## 1. 대상별 근거표

기록 위치 표기: `log#<part> @hh:mm:ss «target»` = `captures/original-interaction-log.json`의 `part`·`at`·`target`(step id가 없어 시각+대상으로 지목). `trace r3` = 해당 case `captures/<case>-trace.json`의 `supplementary_observations_r3.steps`. 캡처 번호 = `captures/related-390x844-<번호>-…-original.png`, `eNN` = `…-eNN-…-evidence.png`. 판정: **관찰 확인** = 조작 기록과 결과 근거를 각각 확인 / **상태만** / **미관찰** / **범위 밖·비적용·비확장**(사유 병기).

대상 목록은 `design-ref/관계인.dc.html`(48–159행 화면 · 240–476행 핸들러)·`설정.dc.html`(38–82행 · 144–157행)과 `_ds_bundle.js` 부품 정의(Dialog 1065–1159 · Dropdown 2699–2953 · Select 2960–3031 · ListRow 3055–3135 · Input 1658–1746 · Textarea 2006–2092 · Checkbox 1454–1519 · ChoicePair 1525–1652 · Button 455–557 · IconButton 614–683 · Toast 1390–1448 · ProgressBar 1166– · AppBar 2529– · AppFrame 2153– · Avatar 15–57)에서 scope·visual-check를 읽기 전에 먼저 열거했다.

### 1-1. 목록·상세·삭제·설정

| 진입 상태·조작 대상 | 실제 조작 기록 위치·동작 | 결과 근거 위치 | 연결 case | 판정·보완 |
|---|---|---|---|---|
| (진입) 관계인.dc.html 로드 | log#partA @05:19:39 «페이지 로드» navigate+mount · related-list-trace `state_transition_actions` | 01 · related-list-trace `dom_snapshot`(4행·뒤로·등록 버튼) | related/list | 관찰 확인 |
| 목록 · AppBar «뒤로»(설정 경유 · history 3) | log#partA2 @05:24:23 click | e07 · url=설정.dc.html | related/list→settings/related-row | 관찰 확인(필수 동작 «뒤로=설정») |
| 목록 · AppBar «뒤로»(직접 진입 · history 2) | log#partA2 @05:24:27 click | url=about:blank | (case 없음 · 발주서 확정) | 관찰 확인(원본 history.back 우선 거동 · 소스 258–261행과 정합) |
| 목록 · ListRow 김서연 hover→press | log#partD-hover @05:34:53 | e02 · bg `color(srgb .12 .11 .09/.04)` · transform none | related/list | 관찰 확인(partA @05:19:40의 hover 프로브는 `cursor auto` 컨테이너를 잡아 무변으로 기록 → partD가 행 루트로 재측정 · visual-check가 partD 값 채택) |
| 목록 · ListRow 김서연 click | log#partA @05:19:40 | 02 · related-detail-trace | related/detail | 관찰 확인 |
| 목록 · ListRow 이하람 click | log#partA @05:19:42 | 12 · related-detail-leap-city-trace | related/detail-lunar-leap-city | 관찰 확인 |
| 목록 · ListRow 박도윤 click | log#partA @05:19:43 | 13 · related-detail-unknown-hour-trace | related/detail-unknown-hour | 관찰 확인 |
| 목록 · ListRow 정우재 click | log#partA @05:19:44 | e01 | related/detail(데이터 변이) | 관찰 확인 |
| 목록 5명 · ListRow «테스트» click | log#partB @05:26:31 | e11 | related/detail(변이) | 관찰 확인 |
| 목록 5명 · ListRow «미상» click | log#partE @05:29:45 | 32 · related-detail-unknown-place-trace | related/detail-unknown-place | 관찰 확인 |
| 목록(저장 후) · ListRow «김서연수정» click | log#partF @06:10:50 | e21 · related-detail-trace r3 | related/detail(변이) | 관찰 확인 |
| 목록 · «관계인 등록하기» hover→press→click | log#partD-hover @05:34:54 · log#partB @05:26:10 | idle/hover/press bg·shadow 값 · 06 · related-register-step1-trace | related/register-step1 | 관찰 확인 |
| 빈 목록 · «관계인 등록하기» click → 닫기 | log#partG @06:09:49 ×2 | e16 · related-empty-trace r3 · related-register-step1-trace r3 | related/empty→register-step1→empty | 관찰 확인(r2 권고 해소) |
| 목록 · `[data-cm-scroll]` scrollTop=max | log#partD-hover @05:34:55 | scrollable 0 · btnY 833 불변 | related/list | 관찰 확인(여유 0) · 긴 목록 중 고정은 미도달 — 한계 표 명시 · 임의 데이터 생성 비대상 |
| 상세 · 스크림 click | log#partA @05:19:41 | e03 · dialogs 0 | related/detail→list | 관찰 확인(Dialog 1093행 onClick=onCancel · 1095행 카드 stopPropagation 정합) |
| 상세 · Escape | log#partA @05:19:42 | e04 · dialogs 1 | — | 관찰 확인(무반응 · Dialog keydown 리스너 없음) |
| 상세 · 닫기 click | log#partA @05:19:42 | dialogs 0 · 4명 무변 | related/list | 관찰 확인 |
| 상세 · 수정하기 click | log#partC @05:26:35 | 03 · related-edit-step1-trace | related/edit-step1 | 관찰 확인 |
| 상세 · trash-2 «삭제하기» click | log#partA @05:19:45 · log#partF @06:10:24 | 10 · related-delete-confirm-trace(h2·취소/삭제하기) | related/delete-confirm | 관찰 확인 |
| 상세 · 본문 `[data-cm-dialog-scroll]` 스크롤 | 없음 | 없음 | — | 미도달(원본 데이터·120자 상한으로 카드가 프레임 778px 미초과 · 한계 표) · 비적용 |
| **삭제 확인 · 스크림 click** | log#partF @06:10:24 «스크림(카드 밖 영역)» | e14 · related-delete-confirm-trace r3(h2 [] · scrims 1 · 컨트롤 삭제하기/닫기/수정하기 · 4명 무변) | related/delete-confirm→detail | **관찰 확인(r2 fail #1 해소 · onCancel=cancelDelete 274행 정합)** |
| 삭제 확인 · Escape | log#partF @06:10:25 | e15 · trace r3(h2 유지 · scrims 1) | — | 관찰 확인(무반응) |
| 삭제 확인 · 취소 click | log#partA @05:19:45 · log#partF @06:10:25 | e05 · 상세(김서연) 복귀 | related/detail | 관찰 확인 |
| 삭제 확인 · 삭제하기(danger) click | log#partA @05:19:46 | 14 · related-toast-deleted-trace(3명 · toast 350×48 y793) | related/toast-deleted | 관찰 확인 |
| 삭제 직후 · Toast 3000ms | log#partA @05:19:49 | toast [] · 3명 | related/list | 관찰 확인 |
| 3명 → 이하람·박도윤·정우재 행→trash-2→삭제하기 ×3 | log#partA @05:19:50–52 · log#partG @06:09:49(재도달) | toast 문구 3종 · 카운트 2→1→없음 · 11 · related-empty-trace | related/empty | 관찰 확인(원본 UI만으로 도달) |
| (진입) 설정.dc.html 로드 | log#partA @05:19:56 · settings-related-row-trace | settings-390x844-related-row-original.png · trace(row rect 324×68 · icon-contact-round · subtitle) | settings/related-row | 관찰 확인 |
| 설정 · ListRow «관계인 보기» click | log#partA @05:19:57 · log#partA2 @05:24:20 | e06 · url=관계인.dc.html · history 3 | settings/related-row→related/list | 관찰 확인(소스 149행 location.assign 정합) |
| 설정 · 프로필 카드·다른 행 11·로그아웃·탈퇴·TabBar | 없음 | 없음 | — | 범위 밖(scope «설정 나머지 무변») · 비적용 |
| 설정 · Avatar 이니셜 «유» 폰트 | log#partF @06:10:51 getComputedStyle | serif 스택 fallback(Gowun Batang 404) | — | 범위 밖 요소의 렌더 사실 기록(visual-check ① 정정 근거) |

### 1-2. 등록 폼

| 진입 상태·조작 대상 | 실제 조작 기록 위치·동작 | 결과 근거 위치 | 연결 case | 판정·보완 |
|---|---|---|---|---|
| step1 · 닫기 | log#partB @05:26:11 | dialogs 0 | related/list | 관찰 확인 |
| step1 · 스크림 | log#partB @05:26:11 | dialogs 0 | related/list | 관찰 확인(formCancel step1=closeForm) |
| step1 · Escape | log#partB @05:26:12 | dialogs 1 | — | 관찰 확인(무반응) |
| step1 빈값 · 다음 | log#partB @05:26:12 | 07 · related-form-error-trace | related/form-error | 관찰 확인 |
| step1 · 관계 Select click(열기) | log#partB @05:26:13 | 15 · related-step1-relation-menu-trace(expanded · menuitem 8 · rect 266×264 · 카드 밖 넘침) | related/step1-relation-menu | 관찰 확인 |
| 관계 메뉴 · «배우자» pick | log#partB @05:26:13 | 값 · 닫힘 · errors [] | related/step1-relation-menu | 관찰 확인 |
| 관계 메뉴 · «기타» pick | log#partE @05:29:41(관계=기타) | 32 상세 «기타» · 새 행 user-round | related/detail-unknown-place | 관찰 확인 |
| 관계 메뉴 · «연인» pick | log#partF @06:10:44(수정 경로) | e20/e21 «연인» · heart | related/toast-saved·detail | 관찰 확인 |
| 관계 메뉴 · «부모» hover | log#partF @06:10:29 | e18 · items bg(부모만 `--surface-hover`) | related/step1-relation-menu | 관찰 확인 |
| 관계 메뉴 · 자녀·형제자매·친구·동료 pick | 없음 | 항목 렌더 15/33 · 라벨 표시는 목록 데이터(부모·자녀·친구)로 확인 | related/step1-relation-menu | 항목 렌더 확인 · pick 결과는 동일 핸들러 onRel(441행) → 데이터 변이 비확장 |
| **관계 메뉴 · ArrowDown×2→ArrowUp** | log#partF @06:10:27 | e17 · trace r3(active menuitem · focus-ring box-shadow) | related/step1-relation-menu | **관찰 확인(r2 fail #2 해소 · Dropdown 2743–2749행 정합)** |
| **관계 메뉴 · Escape** | log#partF @06:10:27 | menus 0 · expanded false · scrims 1 | related/register-step1 | **관찰 확인(메뉴만 닫힘 · 2739행)** |
| **관계 메뉴 · 메뉴 밖 mousedown** | log#partF @06:10:27 | menus 0 · scrims 1 | related/register-step1 | **관찰 확인(2735행 away)** |
| **관계 메뉴 · trigger 재클릭** | log#partF @06:10:28 | menus 0 | related/register-step1 | **관찰 확인(2787행 setOpen(!open))** |
| step1(관계=배우자) · Select 재열기 | log#partF @06:10:29 | 33 · related-step1-relation-menu-selected-trace(items: 배우자 bg `.12` + check · 나머지 transparent) | related/step1-relation-menu-selected(신규) | 관찰 확인(2883·2904·2940행 on 스타일 정합) |
| step1(관계만) · 다음 | log#partB @05:26:13 | 17 · related-form-error-name-trace | related/form-error-name | 관찰 확인 |
| 이름 Input click→type «테스트» | log#partB @05:26:14 | 16 · related-step1-name-focus-trace(focused · border/outline) | related/step1-name-focus | 관찰 확인 |
| 이름 · Tab(포커스 해제) | log#partB @05:26:14 | active=radio 여자 · 값 유지 | related/step1-name-focus | 관찰 확인 |
| 성별 «남자» click | log#partB @05:26:15 | e08 | related/register-step1 | 관찰 확인 |
| 성별 «여자» 재선택 | log#partF @06:10:30 | related-register-step1-trace r3 | related/register-step1 | 관찰 확인(r2 권고 해소) |
| step1 완료 · 다음 | log#partB @05:26:15 | progress 2 · cancel 라벨 «이전» | related/form-step2-solar | 관찰 확인 |
| 생년월일 click→type 1992→07 | log#partB @05:26:16 | 18 · related-step2-date-typing-trace | related/step2-date-typing | 관찰 확인 |
| 생년월일 · type «ab» | log#partB @05:26:16 | 값 유지 | 동상 | 관찰 확인 |
| 생년월일 · Tab | log#partB @05:26:16 | active=radio 양력 | 동상 | 관찰 확인 |
| step2(6자리) · 다음 | log#partB @05:26:16 | 19 · related-form-error-date-trace | related/form-error-date | 관찰 확인 |
| 오류 중 · type 04 | log#partB @05:26:17 | «1992.07.04» · errors [] | related/form-step2-solar | 관찰 확인 |
| 역법 «음력» click | log#partB @05:26:17 | e09 · 윤달 Checkbox 출현 | related/form-step2-lunar | 관찰 확인 |
| 윤달 Checkbox on | log#partB @05:26:18 | checked true | related/form-step2-lunar | 관찰 확인 |
| 윤달 Checkbox off | log#partF @06:10:32 | related-form-step2-lunar-trace r3(box bg 전이) | related/form-step2-lunar | 관찰 확인(r2 권고 해소) |
| 역법 «양력»(윤달 숨김) | log#partB @05:26:18 | 표시 false | related/form-step2-solar | 관찰 확인 |
| step2 · 이전 / step1(복귀) · 다음 | log#partB @05:26:18 ×2 | 값 유지 양방향 | register-step1 · form-step2-solar | 관찰 확인 |
| step2 · Escape | log#partF @06:10:31 | scrims 1 · progress 2 | related/form-step2-solar | 관찰 확인(무반응) |
| step2 · 스크림 | 없음 | 없음 | — | 동일 Dialog·동일 onCancel=formCancel(423행) · step4 스크림 관찰(goStep(step−1))로 분기 확인 · 비확장(nit) |
| step2 완료 · 다음 | log#partB @05:26:19 | progress 3 · 컨트롤 | related/form-step3 | 관찰 확인 |
| step3 빈값 · 다음 | log#partB @05:26:19 | 22 · related-form-error-hour-trace | related/form-error-hour | 관찰 확인 |
| 태어난 시 Select 열기 | log#partB @05:26:20 | 20 · related-step3-hour-menu-trace(12 + description) | related/step3-hour-menu | 관찰 확인 |
| 태어난 시 메뉴 · «유시» pick | log#partB @05:26:20 | 값 · errors [] | 동상 | 관찰 확인 |
| 태어난 시 메뉴 · ArrowDown/Up · Escape · away · 재클릭 | log#partF @06:10:33–35 | related-step3-hour-menu-trace r3 | 동상 | 관찰 확인 |
| 태어난 시(값 유시) 재열기 | log#partF @06:10:45(수정 경로) | e23 · DOM(유시 bg `.12` + check) | related/step1-relation-menu-selected(부품 공통 evidence) | 관찰 확인 — 단 e23 캡처에서는 유시 항목이 maxHeight 264 밖(스크롤)이라 강조가 보이지 않음 · 근거는 DOM 기록 |
| 몰라요 Checkbox on | log#partB @05:26:20 | 21 · related-step3-hour-unknown-trace(Select disabled · 값 소거) | related/step3-hour-unknown | 관찰 확인 |
| 몰라요 off(활성화 경로) | log#partB @05:26:21 | disabled false · 값 빈(미복원) | 동상 | 관찰 확인 |
| step3(몰라요) · 다음 통과 | log#partC @05:26:45 · log#partE | progress 4 | step3-hour-unknown→form-step4 | 관찰 확인 |
| step3 · Escape | log#partF @06:10:33 | scrims 1 · progress 3 | related/form-step3 | 관찰 확인(무반응) |
| step3 · 스크림 | 없음 | 없음 | — | step2와 동일 사유 · 비확장(nit) |
| step3 완료 · 다음 | log#partB @05:26:22 | progress 4 · 시·군 disabled · «등록하기» | related/form-step4 | 관찰 확인 |
| step4 빈값 · 등록하기 | log#partB @05:26:22 | 28 · related-form-error-region-trace | related/form-error-region | 관찰 확인 |
| 시·도 Select 열기 | log#partB @05:26:22 | 23 · related-step4-region-menu-trace(17) | related/step4-region-menu | 관찰 확인 |
| 시·도 메뉴 · «경기» pick(시·군 활성화 경로) | log#partB @05:26:23 | 24 · related-step4-city-enabled-trace | related/step4-city-enabled | 관찰 확인 |
| 시·도 메뉴 · «서울» pick(도 아님 → 시·군 disabled «시·도까지만 받아요» · 값 소거) | log#partB @05:26:25 | e10 | related/form-step4 | 관찰 확인(onRegion 458행 city 리셋) |
| 시·도 메뉴 · ArrowDown/Up · Escape · away · 재클릭 | log#partF @06:10:37–38 | related-step4-region-menu-trace r3 | related/step4-region-menu | 관찰 확인 |
| 시·도 나머지 15 항목 pick | 없음 | 항목 렌더 23 | related/step4-region-menu | 데이터 변이(도 有=경기·도 無=서울 두 분기 관찰) · 비확장 |
| step4(경기 · 시·군 빈) · 등록하기 | log#partB @05:26:23 | 29 · related-form-error-city-trace | related/form-error-city | 관찰 확인 |
| 시·군 Select 열기 | log#partB @05:26:24 | 25 · related-step4-city-menu-trace(31) | related/step4-city-menu | 관찰 확인 |
| 시·군 메뉴 · «고양시» pick | log#partB @05:26:24 | 값 · errors [] | 동상 | 관찰 확인 |
| 시·군 메뉴 · ArrowDown/Up · Escape · away · 재클릭 | log#partF @06:10:40–41 | e19 · related-step4-city-menu-trace r3 | 동상 | 관찰 확인 |
| 시·군 disabled(시·도 없음 «시·도를 먼지 골라주세요») | log#partB @05:26:22 | 09/28 · related-form-step4-trace | related/form-step4 | 비활성 조건·외형 확인 · 활성화 경로(경기 pick) 확인 |
| 못려요 Checkbox on(시·도 «서울» 유지·disabled · 시·군 «태어난 곳은 물지 않을게요») | log#partB @05:26:25 | 26 · related-step4-place-unknown-trace | related/step4-place-unknown | 관찰 확인 |
| 못려요 off(활성화 경로) | log#partB @05:26:25 | 시·도 활성 · 시·군 «시·도까지만 받아요» | 동상 | 관찰 확인 |
| 못려요 단독(시·도 빈 · placeholder «태어난 곳은 물지 않을게요») → 등록하기 | log#partE @05:29:41 ×2 | log result(DOM 텍스트) · toast «미상» · 새 행 «기타 · 2000. 01. 01. · 시간 모름» | related/detail-unknown-place | 관찰 확인(이 중간 상태의 캡처는 없음 · DOM 근거) |
| 메모 click→type / fill 130자 / Tab | log#partB @05:26:26–27 ×3 | 27 · related-step4-note-focus-trace(6/120) · 120/120 · active=이전 | related/step4-note-focus | 관찰 확인 |
| step4 · 스크림 | log#partB @05:26:27 | progress 3(이전 단계) | related/form-step4 | 관찰 확인 |
| step3(스크림 복귀) · 다음 | log#partB @05:26:27 | step4 값 유지 | related/form-step4 | 관찰 확인 |
| step4 · Escape | log#partF @06:10:36 | scrims 1 · progress 4 | related/form-step4 | 관찰 확인(무반응) |
| step4 완료 · 등록하기 | log#partB @05:26:28 | 30 · related-toast-registered-trace(5명 · success) | related/toast-registered | 관찰 확인 |
| 등록 직후 · Toast 3000ms | log#partB @05:26:31 | toast 0 · 5명 | related/list | 관찰 확인 |
| step4 → 이전×3 → step1 · 닫기 | log#partF @06:10:43 | related-list-trace r3(4명 · 등록 없음) | related/list | 관찰 확인 |

### 1-3. 수정 폼

| 진입 상태·조작 대상 | 실제 조작 기록 위치·동작 | 결과 근거 위치 | 연결 case | 판정·보완 |
|---|---|---|---|---|
| 상세(김서연) · 수정하기 → step1 프리필 | log#partC @05:26:35 | 03 · related-edit-step1-trace | related/edit-step1 | 관찰 확인 |
| 수정 step1 · 관계 재열기(프리필 강조) | log#partF @06:10:44 | related-edit-step1-trace r3(배우자 bg `.12` + check) | related/edit-step1 | 관찰 확인 |
| 수정 step1 · 관계→연인 · 이름→«김서연수정» | log#partF @06:10:44 | 표시 연인 · value | related/edit-step1 | 관찰 확인 |
| 수정 step1 · 다음 | log#partC @05:26:36 | 04 · related-form-step2-solar-trace(«1992.07.04» · 양력 · 윤달 숨김) | related/form-step2-solar | 관찰 확인 |
| 수정 step2 · 다음 | log#partC @05:26:36 | 05 · related-form-step3-trace(«유시» 활성) | related/form-step3 | 관찰 확인 |
| 수정 step3 · 다음 | log#partC @05:26:37 | 09 · related-form-step4-trace(서울 · 시·군 disabled · 24/120 · 저장하기) | related/form-step4 | 관찰 확인 |
| 수정 step4 · 저장하기(무변경) | log#partC @05:26:37 | 31 · related-toast-saved-trace | related/toast-saved | 관찰 확인 |
| 수정 step4 · 저장하기(관계·이름 변경) | log#partF @06:10:46 | e20 · related-toast-saved-trace r3(행 «김서연수정 / 연인 …» 위치 유지 · toast 새 이름) | related/toast-saved | 관찰 확인(r2 권고 해소) |
| 상세(이하람) → 수정하기 → 다음 | log#partC @05:26:41 | 04b · related-form-step2-lunar-trace(음력·윤달 checked) | related/form-step2-lunar | 관찰 확인 |
| 수정(이하람) step3 → 다음 | log#partC @05:26:42 | e12(경남 · 진주시 활성 프리필) | related/step4-city-enabled(변이) | 관찰 확인 |
| 수정 step4 · 이전×3 → 닫기 | log#partC @05:26:42–43 | 값 유지(인시) · 목록 · 이하람 무변 | related/edit-step1 | 관찰 확인 |
| 상세(박도윤) → 수정하기 → 다음×2 | log#partC @05:26:44 | e13(몰라요 checked · Select disabled) | related/step3-hour-unknown(변이) | 관찰 확인 |
| step3(몰라요 프리필) · 다음 | log#partC @05:26:45 | progress 4 · 경기 고양시 프리필 | related/form-step4 | 관찰 확인 |
| 수정 폼 · 스크림 / Escape | 없음 | 없음 | — | 등록 폼과 같은 Dialog 인스턴스(hasForm 107행)·같은 onCancel · draft 데이터만 다름 → 등록 경로 관찰(스크림 step1·4 · Escape step1~4)로 충족 · 데이터 변이 비확장(nit) |

### 1-4. 시각 상태·비대상(조용한 생략 방지용 명시)

| 대상 | 조작 기록 | 결과 근거 | 연결 case | 판정·사유 |
|---|---|---|---|---|
| Dialog 버튼 glass(닫기·취소·이전) · primary(수정하기·다음·등록하기·저장하기) · danger(삭제하기) · IconButton plain(뒤로·trash-2)의 hover/press | 없음(실측은 primary Button·ListRow만 · log#partD-hover) | 번들 cmBtnTones/cmIbTones 정의값(455–606행 · inline style이라 CSS 스캔 불가) · render-audit hover 3은 `a:hover`뿐 | — | 클릭·입력 대상도, 새로 드러나는 대상도, 결과가 달라지는 진입 상태도 아닌 포인터 일시 시각 상태 · DS 부품 공통 → 대상 규칙상 판정 미반영 · 권고(§6) |
| 버튼·radio·Checkbox의 focus-visible 링 | Tab 이동 log#partB(이름→여자 · 생년월일→양력 · 메모→이전) | trace `active`(tag·rect) · 캡처 없음 | — | 부분 관찰(한계 표 명시) · menuitem 포커스 링은 e17/e19 캡처 |
| 상세 «음력 YYYY. MM. DD.»(윤달 아님) 접두 | 없음 | 없음(fmtBirth 235행 3분기 중 양력·«음력 윤달» 2분기 관찰) | related/detail(변이) | 독립 값 조합(역법×윤달) · 규칙상 비확장 · 권고 |
| 오류 표시 중 이전/스크림 → err 초기화 | 없음 | 없음(goStep 266행 err '' · 단계 이동과 patch 소거는 각각 관찰) | — | 동일 버튼·결과 조합 · nit |
| 캔버스 knob 4 variant | 없음 | 없음 | — | 사용자 결정 list-default-variant-only · 캔버스 편집 패널이며 앱 프레임 조작 대상 아님 |
| 긴 목록 pinned · Dialog 내부 스크롤 · 메뉴 스크롤 중간 · 모션 duration · API media | 없음 | 한계 표(r3 갱신) | — | 미도달/비적용 사유 명시 확인 |

## 2. 검토한 scope·원본·case 버전

- `scope.md` — design-input이 가리키는 sha `782074db…`(해시 재계산 도구 없음 · prepare exit 0 기록과 전달 digest로만 정합 확인). 사용자 요구·승인 출처 절(필수 동작 §3 · 확정 이탈 · **기존 결정 출처 보완(r3)** · 실행 경계 r2/r3 · case 표 34행)을 먼저 읽고, 관찰 결과·case 표는 대상 목록 작성 후에 읽음.
- `design-input.json` version 1 · reference_root `design-ref` · manifests `[source-manifest.json]` · coverage_review **null** · **34 case** 전부 viewport [390,844] · scope_refs 비어 있지 않음(`scope.md#related_persons` ×33 · `#preferences` ×1) · 관계인 entrypoint sha `cf2fe348…` ×33 · 설정 `b88e995b…` ×1 · 각 case reference_capture·source_observation 포인터 존재.
- `source-manifest.json` collection=archive · archive_ready=true · source_ready=false(archive 정상) · files 22 전부 ok · dependencies 30(ok 24 · external 6 = Google Fonts css/woff2 ×3 · Pretendard woff2 · lucide css/woff2).
- 원본 직접 열람: `관계인.dc.html` 전문(480행) · `설정.dc.html` 전문(166행) · `_ds_bundle.js` 위 §1 머리에 적은 15개 부품 정의 · `tokens/typography.css`(32–42행).
- 관찰 증거: `captures/*-original.png` **34장 전부 열람** · `*-evidence.png` **22장 전부 열람**(e01–e21·e23 — 전달받은 «23»과 다름 · §6) · `original-interaction-log.json` **123 step 전문** · trace 34 중 r3 append 16건(delete-confirm·step1-relation-menu-selected 전문 · 나머지 14건은 r3 절 Grep) · source-observation 4건 원문(list·delete-confirm·settings·신규 34) + design-input 포인터 34.
- 이전 case 목록: `_history/v1`(10) · `v2`·`v3`·`v4`(13 · hour-picker 포함) · `v5-r1`(12) · `v5-r2`(33) · r2 trace 바이트 16건 `_history/v5-r2/captures/` 보존 확인.
- 직전 검토 원문 `_history/v5-r2/coverage-review.md`(fail) — 보완 목록 출처로만 사용 · 판단 근거 아님.
- 사용자 결정 원문 `coordinator-repair/existing-approval.md`(scope가 인용 · 발주서 개정 13·14 · 결정 5) 읽음.
- 참조 계약 `skills/implementation-ui/references/design-evidence.md`(archive 경로 · source_observation · prepare/review 절) · `motion-notes.md`(r3 메모) · `render-audit.json`(hoverSelectors `a:hover`×3 · pinned 0 · blocked 시트 4) · `asset-manifest.json`(images 0) · `screen-meta.json` · `design-spec.md` §11 이탈 표 위치(545행 · 설계 판단은 검토하지 않음).
- 미참조: G1 지식(architecture-web) · 다른 실행·평가 기록 · 원본 A8 워크트리 · 원본 서버/CDP(접근 0).

## 3. 원본 렌더 확인 결과(캡처 직접 열람)

- **프레임·viewport 구별**: 56장 전부 390×844 AppFrame clip(trace `content_crop` x85 y72.84 w390 h844) · 브라우저 viewport 560×1040은 trace `browser_viewport`에 별도 기록 → 계약의 "canvas ≠ viewport 구별" 충족.
- **case 상태 일치**: 34장 각각이 case `state`와 일치 — 01 목록 4행(관계 accent·heart/users-round/user-round·음력 접두·«시간 모름») · 02/12/13/32 상세 4 데이터 변이(양력·음력 윤달·«모른다고 하셨어요»·«모른다고 하션어요»[원본 오타]·«적어둔 메모가 없어요») · 10 danger Dialog(인주 원반 trash-2·danger 버튼) · 14/30/31 toast 2 tone(info/check 아이콘 · 등록 버튼과 겹침) · 11 빈 상태 · 06/03 등록/수정 step1 · 07/17/19/22/28/29 오류 caption 6종 · 15/20/23/25 메뉴가 카드 하단 버튼 위로 넘침 · **33(신규) «배우자» 행 accent 배경 + check** · 16/18/27 포커스 accent 테두리 · 21/26 disabled 흐림 + placeholder 변이 · 04/04b/05/09 프리필 · 24 시·군 활성 · 설정 캡처 «관계인 보기» 행 + subtitle + contact-round.
- **evidence 일치**: e14 스크림 후 상세 복귀 · e15 Escape 후 확인 Dialog 유지 · e16 빈 상태 위 등록 폼 · e17/e19 menuitem 포커스 링 · e18 «부모» hover 배경 · e20 «김서연수정 / 연인» 행 + toast · e21 상세 반영 · e23 태어난 시 메뉴(유시 강조는 스크롤 밖 · DOM 근거) · r2 e01–e13도 기록과 일치.
- **원본 URL·버전**: 모든 trace `url` = `http://127.0.0.1:57232/{관계인,설정}.dc.html` · `frozen_version` v5 · source_observation `archive_sha256 bddc54ec…` 동일 · entrypoint sha가 design-input/manifest와 일치 · source_observation 내부 capture sha = design-input reference_capture sha(표본 4건). 서버 제공 바이트 == design-ref는 visual-check ② #1·#17의 curl sha 기록(r2·r3 두 번)으로 확인 — 나는 해시를 재계산하지 않았다.
- **폰트 fallback**: 전 trace Pretendard Variable loaded · lucide 400 loaded · Gowun Batang 400 unloaded/700 error(woff2 404). 범위 안 요소의 타이포 토큰(`--type-title-2/3`·body·body-sm·label·caption)은 typography.css 34–41행에서 전부 `--font-sans` → 관계인 화면 렌더 영향 0. serif는 display/quote 토큰과 Avatar(번들 44행)뿐 → 설정 Avatar «유»만 fallback(범위 밖 요소 · visual-check ①이 r3에서 정정함 · 확인).
- **런타임 전용 자원**: React/ReactDOM 18.3.1 UMD(unpkg · support.js 동적 로드) · Pretendard woff2 · lucide css/woff2 → trace `resources`로 해소. archive external 6건 중 실제 미로드는 Gowun Batang뿐. failed_requests는 그 404 1건 · 콘솔 예외 0.
- **이미지 자산**: asset-manifest images=[] · 원본 `<img>` 0 · 아이콘 전부 lucide 글리프(캡처에서 chevron-left/right·heart·users-round·user-round·trash-2·check·chevron-down·user-round-plus·calendar·contact-round·info 렌더 확인) → 정합.
- **trace 필드 한계**: r2 `dialogs`(danger Dialog 0으로 셈)·`errors`(placeholder 혼입)는 한계 표에 명시 · r3는 `scrims`로 Dialog 유무를 셈 · 상태 판정은 h2·controls·캡처 근거 → 판정 영향 없음. Dialog 루트 레이어 기하 (0,44,390,778)·z 60·cm-fade-in은 probe 기록과 Dialog 1080–1092행 정합.

## 4. 범위변경 근거 대조

- **case 이력**: v1(10) → v2/v3/v4(13 · +delete-confirm·form-step3·form-step4·hour-picker) → v5-r1(12 · −hour-picker) → v5-r2(33 · 관찰 승격 +21) → **r3 34(+1 `related/step1-relation-menu-selected`)**. r1 이후 삭제 0 · viewport 축소 0(전부 390×844 유지). hour-picker 삭제 근거 = v5 원본 135행이 `Select`이며 BottomSheet 정의 없음 → 원본 소스 자체가 근거.
- **재동결 v3~v5 사용자 출처**: r2 지적이던 미기재가 scope «기존 결정 출처 보완» 표(v2 개정 2 · v3 개정 9 · v4 개정 11 · v5 개정 13·14)로 채워졌고, v5 원문(`existing-approval.md` · 본문 sha 기재)은 관계 라벨 8종·D1·D7·D3~D5·DS 전역 결정을 담아 scope 요약과 일치. 새 제품 결정 0이라는 서술과도 정합.
- **확정 이탈 ↔ 원본 관찰**: relation-kind-8(메뉴 8 항목 관찰 · v5로 이탈 폭 0) · form-4-step(ProgressBar 4·라벨 없음 관찰) · PD-2 삭제 흐름(danger Dialog·문구·toast 관찰) · note-max-500(원본 120/120 관찰 · web 500은 승인 이탈로 기재) · settings-row-no-subtitle(원본 subtitle 관찰 · 미재현 승인) · list-default-variant-only(knob 미조작 근거) — 전부 서로 일관.
- **nit**: 확정 이탈 PD-3 서술 «시안의 단일 자유 텍스트 태어난 곳»은 v2 시점 기술이며 v5 원본은 이미 시·도/시·군 Select(144–145행) → 이탈 폭이 0에 가까움. G0 입력 판정에는 영향 없고 이탈 표 재기술은 설계 단계 소관.

## 5. 현재 판정

**통과(pass).**

- r2 판정을 가른 두 항목(삭제 확인 스크림 click · 4개 Select 메뉴 열림 상태의 부품 정의 이벤트)이 각각 실제 조작 기록(log#partF · trace r3) + 결과 근거(DOM 값) + 캡처(e14 · e17/e19)로 채워졌고, 부품 정의(Dialog 1093행 · Dropdown 2733–2757행)와 결과가 일치한다.
- 원본에서 독립 열거한 클릭·입력 대상, 조작 후 드러나는 대상, 결과가 달라지는 진입 상태(입력칸 click/type/blur · 선택·해제·복귀 · 화면 이탈 · disabled 조건과 활성화 경로 · 오류 6종 · toast 2종 · 데이터 행 각각 · 빈 상태 · 설정 진입/복귀)에 조작 기록과 결과 근거가 모두 있다. 34 case 전수에 원본 렌더·viewport·scope 참조가 일치한다.
- 조작 없이 남긴 행(§1-4)은 포인터 시각 상태·독립 값 조합·동일 인스턴스/핸들러의 데이터 변이·미도달 한계이며 각각 사유가 문서에 명시돼 있어 조용한 생략이 아니다. 이 판정은 현재 입력에 대한 것이며 다음 phase 개방은 Coordinator 소유다.

## 6. 보완에 필요한 사실(비차단 · 기록/권고)

- **문서 개수 정정**: evidence 캡처는 실제 22장(e01–e21 · e23 · e22 없음). visual-check ①·⑤와 Coordinator 인계문의 «23(r2 13 + r3 10)»은 «22(r2 13 + r3 9)»로 맞춰야 한다.
- **e23 한계 명시**: `related-390x844-e23-hour-menu-selected-evidence.png`는 선택 항목 «유시»가 메뉴 스크롤 영역 밖이라 강조가 캡처에 보이지 않는다(근거는 DOM 기록). visual-check r3 표의 해당 행에 한 줄 병기 권고.
- **scope_refs 앵커**: `scope.md#related_persons`·`#preferences`는 scope.md에 실제 heading 앵커가 없다(case 표 절이 실제 참조). 검사기는 비어 있지 않음만 요구하므로 차단 아님 · 다음 갱신 시 실제 절 이름으로 정리 권고.
- **권고 관찰(같은 원본 · 선택)**: ⓐ Dialog 버튼 glass/danger·IconButton plain의 hover/press 실측(번들 정의값과 대조 · DS 재사용이면 G1이 부품 계약으로 처리 가능) ⓑ 상세 «음력»(윤달 아님) 접두 1회(이하람 수정 → 윤달 해제 → 저장 → 상세) ⓒ 수정 폼 스크림/Escape 1회 ⓓ 오류 표시 중 «이전»으로 caption 소거 1회. 어느 것도 새 case를 요구하지 않는다.
- **설계 단계 인계 사실**: 확정 이탈 PD-3 서술은 v5 원본(구조 Select)과 어긋나므로 design-spec 이탈 표에서 «이탈 폭 0(시안이 구조 피커로 바뀜)»으로 재기술 대상.
- **내가 하지 않은 것**: sha256 재계산(도구 없음 · prepare exit 0과 파일 내 포인터 정합으로 대체) · 원본 서버/CDP 접근 · 파일 쓰기.

(도구 메모: 읽기 전용 검토라 Serena/Graphify는 사용하지 않았고 opt-in 표식도 확인하지 않았다. Read/Grep/Glob만 사용.)
agentId: ae18b192df7bbe82f (use SendMessage with to: 'ae18b192df7bbe82f', summary: '<5-10 word recap>' to continue this agent)
<usage>subagent_tokens: 324262
tool_uses: 119
duration_ms: 802938</usage>