확인이 끝났습니다. 조작 대상 독립 열거(원본 `.dc.html` 2종 + `_ds_bundle.js`의 Dialog·Select 부품 정의)와 실제 조작 기록(`original-interaction-log.json` 86 step · trace 33건 · 캡처 46장)을 전부 대조했습니다. 아래가 독립 검토 원문입니다.

---

# G0 입력범위 검토 — A8 web 관계인 (r2 · 2026-09-13)

reviewed-input: 23908d43d49a0c2aca8604466080f9b73c114c0409ff8e7e3469cc492c5915de
review-result: fail

## 1. 검토한 scope·원본·case 버전

- `scope.md`(r2 checkpoint 절·디자인 case 표 33행 포함 · design-input.json이 가리키는 sha `cef8a5fa…` — 나는 해시 재계산 도구가 없어 prepare exit 0 기록과 전달 digest 일치로만 확인)
- `design-input.json` version 1 · reference_root `design-ref` · manifests `[source-manifest.json]` · coverage_review null · **33 case** 전부 viewport [390,844] · scope_refs `scope.md#related_persons` ×32 · `scope.md#preferences` ×1
- `source-manifest.json` collection=archive · archive_ready=true · source_ready=false(archive 정상) · files 22 전부 ok · dependencies 30(ok 24 · external 6: Google Fonts css/woff2 ×3 · Pretendard woff2 · lucide css/woff2)
- 원본 entrypoint: `design-ref/관계인.dc.html`(sha `cf2fe348…` · 34922B) · `design-ref/설정.dc.html`(`b88e995b…` · 11815B) — 두 파일 전문과 `support.js` 참조, `_ds_bundle.js`의 Dialog(1070–1152행)·Select(2725–2764행)·AppBar(2585–2660행)·Avatar(28–57행) 정의 직접 열람
- 관찰 증거: `captures/*-original.png` 33 · `*-evidence.png` 13 · `*-trace.json` 33 · `*-source-observation.json` 33(3건 원문 확인 · 나머지는 design-input 포인터 정합) · `original-interaction-log.json` 86 step
- 이전 case 목록: `_history/v1`(10) · `v2/v3/v4`(13 · hour-picker+delete-confirm 포함) · `v5-r1`(12)
- 참조 계약: plugin `skills/implementation-ui/references/design-evidence.md`(archive 경로 · source_observation · prepare/review 절)
- 미참조: design-spec.md · design-review.md · 이전 coverage-review.md(지시대로 판단 근거에서 제외)

## 2. 대상별 근거표

기록 위치 표기: `log#<part>` = `captures/original-interaction-log.json`의 `part` 값과 `target` 문자열. 캡처 번호는 `captures/related-390x844-<번호>-…-original.png`. 판정: **관찰 확인** = 조작 기록과 결과 근거 둘 다 확인 / **상태만** = 조작 칸 없음 / **미관찰** / **범위 밖·비적용**.

### 2-1. 목록·상세·삭제·설정

| 진입 상태·조작 대상 | 실제 조작 기록 위치·동작 | 결과 근거 위치 | 연결 case | 판정·보완 |
|---|---|---|---|---|
| (진입) 관계인.dc.html 로드 | log#partA «페이지 로드» navigate+mount · related-list-trace `state_transition_actions` | 01 · related-list-trace `dom_snapshot`(4행·뒤로·등록 버튼) | related/list | 관찰 확인 |
| 목록 · AppBar «뒤로»(설정에서 진입 · history 3) | log#partA2 «AppBar IconButton 뒤로 count=1» click | settings-390x844-e07-after-back-evidence.png · url=설정.dc.html | related/list→settings | 관찰 확인 |
| 목록 · AppBar «뒤로»(직접 진입 · history 2) | log#partA2 click | url=about:blank | (case 없음 · 발주서 «뒤로=설정» 확정) | 관찰 확인(원본 history.back 우선 거동) |
| 목록 · ListRow 김서연 hover→press | log#partD-hover «ListRow 김서연 루트» | e02 · log result bg `color(srgb .12 .11 .09/.04)` · transform none | related/list | 관찰 확인 — partA의 hover 프로브는 `role null·cursor auto` 컨테이너를 잡아 bg 무변으로 기록됐고 partD가 실제 행 루트(cursor pointer)로 재측정. visual-check는 partD 값 채택 → 정합 |
| 목록 · ListRow 김서연 click | log#partA click | 02 · related-detail-trace(dialogs 1 · 삭제하기/닫기/수정하기) | related/detail | 관찰 확인 |
| 목록 · ListRow 이하람 click | log#partA | 12 · related-detail-leap-city-trace | related/detail-lunar-leap-city | 관찰 확인 |
| 목록 · ListRow 박도윤 click | log#partA | 13 · related-detail-unknown-hour-trace | related/detail-unknown-hour | 관찰 확인 |
| 목록 · ListRow 정우재 click | log#partA | e01 | related/detail(데이터 변이) | 관찰 확인 |
| 목록 5명 · ListRow «테스트»(신규) click | log#partB | e11 | related/detail(변이) | 관찰 확인 |
| 목록 5명 · ListRow «미상» click | log#partE | 32 · related-detail-unknown-place-trace | related/detail-unknown-place | 관찰 확인 |
| 목록 · «관계인 등록하기» hover→press→mouseup | log#partD-hover | log result idle/hover/press bg·shadow | related/register-step1 | 관찰 확인 |
| 목록 · «관계인 등록하기» click | log#partB | 06 · related-register-step1-trace | related/register-step1 | 관찰 확인 |
| 목록 · `[data-cm-scroll]` scrollTop=max | log#partD-hover | scrollable 0 · btnY 833 불변 | related/list | 관찰 확인(여유 0) · 긴 목록 스크롤 중 고정은 미도달 — 한계 표에 기재됨 |
| 빈 목록 · «관계인 등록하기» | 없음 | 11 · related-empty-trace `controls`에 버튼 존재 | related/empty | 상태만 — 빈 상태에서 등록 click은 미조작(같은 `openForm(null)` 핸들러 · nit) |
| 상세 · 스크림 click | log#partA «스크림(카드 밖 영역)» | e03 · dialogs 0 | related/detail→list | 관찰 확인(번들 Dialog 1093행 스크림 `onClick: onCancel` · 카드 `stopPropagation`과 정합) |
| 상세 · Escape | log#partA press | e04 · dialogs 1 | — | 관찰 확인(무반응 · 번들 Dialog에 keydown 리스너 없음 — Escape/keydown은 Select 2739·2752행뿐) |
| 상세 · 닫기 click | log#partA | dialogs 0 · 4명 무변 | related/list | 관찰 확인 |
| 상세 · 수정하기 click | log#partC | 03 · related-edit-step1-trace(프리필) | related/edit-step1 | 관찰 확인 |
| 상세 · trash-2 «삭제하기» click | log#partA | 10 · related-delete-confirm-trace(h2 «김서연님을 삭제할까요?» · 취소/삭제하기) | related/delete-confirm | 관찰 확인 |
| 상세 · 본문 `[data-cm-dialog-scroll]` 스크롤 | 없음 | 없음 | — | 미도달(원본 데이터로 카드가 프레임을 넘지 않음 · 한계 표 기재 · 비적용) |
| 삭제 확인 · 취소 click | log#partA | e05 · 상세(김서연) 복귀 | related/detail | 관찰 확인 |
| 삭제 확인 · 삭제하기(danger) click | log#partA | 14 · related-toast-deleted-trace(3명 · toast rect 350×48 y793) | related/toast-deleted | 관찰 확인 |
| **삭제 확인 · 스크림 click** | **없음** | **없음** | related/delete-confirm | **미관찰** — 원본 Dialog 스크림 onClick=onCancel=`cancelDelete`(상세 복귀)로 예상되나 관찰 0. visual-check ④-1에 «미조작» 자인, «미관찰·한계» 표에는 부재. 삭제 흐름은 확정 이탈 PD-2 «위치·확인 단계·문구 전부 시안» → 범위 안 |
| 삭제 확인 · Escape | 없음 | 없음 | — | 미관찰(코드상 무반응 예상 · 근거는 코드뿐) |
| 삭제 직후 · Toast 3000ms 대기 | log#partA | toast=[] · 3명 유지 | related/list | 관찰 확인 |
| 목록 3명 · 이하람/박도윤/정우재 행→trash-2→삭제하기 ×3 | log#partA click×3 ×3 | 각 toast 문구·카운트 2→1→없음 · 11 · related-empty-trace | related/empty | 관찰 확인(원본 UI만으로 도달) |
| (진입) 설정.dc.html 로드 | log#partA navigate · settings-related-row-trace | settings-390x844-related-row-original.png · trace(contact-round «관계인 보기» · subtitle) | settings/related-row | 관찰 확인 |
| 설정 · ListRow «관계인 보기» click | log#partA · log#partA2 | e06 · url=관계인.dc.html · history 3 | settings/related-row→related/list | 관찰 확인 |
| 설정 · 프로필 카드·다른 행 11·로그아웃·탈퇴·TabBar | 없음 | 없음 | — | 범위 밖(scope «설정 나머지 무변») · 비적용 |

### 2-2. 등록 폼

| 진입 상태·조작 대상 | 실제 조작 기록 위치·동작 | 결과 근거 위치 | 연결 case | 판정·보완 |
|---|---|---|---|---|
| step1 · 닫기 | log#partB | dialogs 0 | related/list | 관찰 확인 |
| step1 · 스크림 | log#partB | dialogs 0 | related/list | 관찰 확인 |
| step1 · Escape | log#partB | dialogs 1 | — | 관찰 확인(무반응) |
| step1 빈값 · 다음 | log#partB | 07 · related-form-error-trace | related/form-error | 관찰 확인 |
| step1 · 관계 Select click(열기) | log#partB | 15 · related-step1-relation-menu-trace(expanded true · menuitem 8 · rect 266×264) | related/step1-relation-menu | 관찰 확인 |
| 관계 메뉴 · «배우자» pick | log#partB | 값·닫힘·errors [] | related/step1-relation-menu | 관찰 확인 |
| 관계 메뉴 · «기타» pick | log#partE(`관계=기타`) | 32 상세 «기타» · 목록 행 user-round | related/detail-unknown-place | 관찰 확인(결과는 상세/목록 행으로 간접) |
| **메뉴 열림 · 메뉴 밖 mousedown(away)** | **없음** | **없음** | step1-relation-menu · step3-hour-menu · step4-region-menu · step4-city-menu(부품 공통) | **미관찰** — 번들 Select 2735행 `document mousedown away → setOpen(false)` |
| **메뉴 열림 · Escape** | **없음** | **없음** | 동상 | **미관찰** — 번들 2739행 `Escape → setOpen(false)` |
| 메뉴 열림 · ArrowDown/ArrowUp | 없음 | 없음 | 동상 | 미관찰 — 번들 2743–2749행 menuitem 포커스 순환 |
| 메뉴 열림 · trigger 재클릭 | 없음 | 없음 | 동상 | 미관찰 |
| step1(관계만) · 다음 | log#partB | 17 · related-form-error-name-trace | related/form-error-name | 관찰 확인 |
| step1 · 이름 Input click→type «테스트» | log#partB | 16 · related-step1-name-focus-trace(focused true · outline/border) | related/step1-name-focus | 관찰 확인 |
| 이름 입력 중 · Tab(blur) | log#partB | active=radio 여자 · 값 유지 | related/step1-name-focus | 관찰 확인 |
| step1 · radio «남자» | log#partB | e08 · 여자 false/남자 true | related/register-step1 | 관찰 확인(«여자» 재선택은 미조작 · 같은 ChoicePair · nit) |
| step1 완료 · 다음 | log#partB | progress 2 · cancel 라벨 «이전» | related/form-step2-solar | 관찰 확인 |
| step2 · 생년월일 click→type 1992→07 | log#partB | 18 · related-step2-date-typing-trace(value «1992.07» · focused) | related/step2-date-typing | 관찰 확인 |
| 생년월일 · type «ab» | log#partB | value 유지 | 동상 | 관찰 확인 |
| 생년월일 · Tab | log#partB | active=radio 양력 | 동상 | 관찰 확인 |
| step2(6자리) · 다음 | log#partB | 19 · related-form-error-date-trace | related/form-error-date | 관찰 확인 |
| 오류 중 · type 04 | log#partB | «1992.07.04» · errors [] | related/form-step2-solar | 관찰 확인 |
| step2 · radio «음력» | log#partB | e09 · 윤달 Checkbox 출현 | related/form-step2-lunar | 관찰 확인 |
| step2(음력) · Checkbox 윤달 click | log#partB | checked true | related/form-step2-lunar | 관찰 확인(해제는 미조작 · nit) |
| step2(음력·윤달) · radio «양력» | log#partB | 윤달 숨김 | related/form-step2-solar | 관찰 확인 |
| step2 · 이전 | log#partB | step1 값 유지 | related/register-step1 | 관찰 확인 |
| step1(복귀) · 다음 | log#partB | step2 값 유지 | related/form-step2-solar | 관찰 확인 |
| step2 완료 · 다음 | log#partB | progress 3 · 컨트롤 | related/form-step3 | 관찰 확인 |
| step2 · 스크림 / Escape | 없음 | 없음 | — | 미관찰(스크림은 step4에서 동일 함수 `formCancel` 관찰 · Escape는 코드상 무반응 · 저심각) |
| step3 빈값 · 다음 | log#partB | 22 · related-form-error-hour-trace | related/form-error-hour | 관찰 확인 |
| step3 · 태어난 시 Select 열기 | log#partB | 20 · related-step3-hour-menu-trace(menuitem 12 + description) | related/step3-hour-menu | 관찰 확인 |
| 메뉴 · «유시» pick | log#partB | 값 · errors [] | 동상 | 관찰 확인 |
| step3 · Checkbox 몰라요 click | log#partB | 21 · related-step3-hour-unknown-trace(Select disabled true · placeholder) | related/step3-hour-unknown | 관찰 확인 |
| 몰라요 체크 · 해제(활성화 경로) | log#partB | disabled false · 값 빈(미복원) | 동상 | 관찰 확인 |
| step3(몰라요 · Select disabled) · 다음 통과 | log#partC(박도윤 프리필) · log#partE | progress 4 | related/step3-hour-unknown→form-step4 | 관찰 확인 |
| step3 · 스크림 / Escape | 없음 | 없음 | — | 미관찰(저심각 · 동상) |
| step4 빈값 · 등록하기 | log#partB | 28 · related-form-error-region-trace | related/form-error-region | 관찰 확인 |
| step4 · 시·도 Select 열기 | log#partB | 23 · related-step4-region-menu-trace(menuitem 17) | related/step4-region-menu | 관찰 확인 |
| 시·도 메뉴 · «경기» pick(시·군 활성화 경로) | log#partB | 24 · related-step4-city-enabled-trace(시·군 disabled false) | related/step4-city-enabled | 관찰 확인 |
| step4(경기 · 시·군 빈) · 등록하기 | log#partB | 29 · related-form-error-city-trace | related/form-error-city | 관찰 확인 |
| step4 · 시·군 Select 열기 | log#partB | 25 · related-step4-city-menu-trace(menuitem 31) | related/step4-city-menu | 관찰 확인 |
| 시·군 메뉴 · «고양시» pick | log#partB | 값 · errors [] | 동상 | 관찰 확인 |
| step4(경기 고양시) · 시·도 → «서울» | log#partB | e10 · 시·군 disabled «시·도까지만 받아요» · 값 소거 | related/form-step4 | 관찰 확인 |
| step4(서울) · Checkbox 못려요 click | log#partB | 26 · related-step4-place-unknown-trace(시·도 disabled 값 «서울» 유지 · 시·군 disabled «태어난 곳은 물지 않을게요») | related/step4-place-unknown | 관찰 확인 |
| 못려요 체크 · 해제(활성화 경로) | log#partB | 시·도 활성 · 시·군 «시·도까지만 받아요» | 동상 | 관찰 확인 |
| step4 · 못려요 단독(시·도 없음) → 등록하기 | log#partE | 통과 · toast «미상님을 등록했어요» · 새 행 «기타 · 2000. 01. 01. · 시간 모름» | related/detail-unknown-place | 관찰 확인 |
| step4 · 메모 click→type | log#partB | 27 · related-step4-note-focus-trace(focused · «6/120») | related/step4-note-focus | 관찰 확인 |
| 메모 · fill 130자 | log#partB | length 120 · 120/120 | 동상 | 관찰 확인 |
| 메모 · Tab | log#partB | active=이전 | 동상 | 관찰 확인 |
| step4 · 스크림 | log#partB | progress 3(이전 단계) | related/form-step4 | 관찰 확인 |
| step3(스크림 복귀) · 다음 | log#partB | step4 값 유지(서울 · 메모) | related/form-step4 | 관찰 확인 |
| step4 완료 · 등록하기 | log#partB | 30 · related-toast-registered-trace(5명 · toast success) | related/toast-registered | 관찰 확인 |
| 등록 직후 · toast 대기 | log#partB | toast 0 · 5명 | related/list | 관찰 확인 |
| step4 · Escape | 없음 | 없음 | — | 미관찰(저심각) |

### 2-3. 수정 폼

| 진입 상태·조작 대상 | 실제 조작 기록 위치·동작 | 결과 근거 위치 | 연결 case | 판정·보완 |
|---|---|---|---|---|
| 수정 step1(김서연) · 다음 | log#partC | 04 · related-form-step2-solar-trace(«1992.07.04» · 양력 · 윤달 숨김) | related/form-step2-solar | 관찰 확인 |
| 수정 step2 · 다음 | log#partC | 05 · related-form-step3-trace(«유시» 활성) | related/form-step3 | 관찰 확인 |
| 수정 step3 · 다음 | log#partC | 09 · related-form-step4-trace(서울 · 시·군 disabled · 24/120 · 저장하기) | related/form-step4 | 관찰 확인 |
| 수정 step4 · 저장하기 | log#partC | 31 · related-toast-saved-trace(4명 · toast success) | related/toast-saved | 관찰 확인 — 단 값 무변경 저장. **변경 값이 목록 행/상세에 반영되는 결과는 미관찰**(보완 권고) |
| 상세(이하람)→수정하기→다음 | log#partC | 04b · related-form-step2-lunar-trace(음력 checked · 윤달 checked) | related/form-step2-lunar | 관찰 확인 |
| 수정(이하람) step3→다음 | log#partC | e12(경남 · 진주시 활성 프리필) | related/step4-city-enabled(변이) | 관찰 확인 |
| 수정 step4 · 이전 ×3 → 닫기 | log#partC 2 step(«이전» progress 3 인시 유지 · «닫기» 목록 복귀) | 저장 없음 · 이하람 무변 | related/edit-step1 | 관찰 확인 |
| 상세(박도윤)→수정하기→다음 ×2 | log#partC | e13(몰라요 checked · Select disabled) | related/step3-hour-unknown(변이) | 관찰 확인 |
| 수정 폼 · 스크림(step1=닫기 · step≥2=이전) | 없음(수정 경로) | 등록 경로 동일 함수 관찰 | — | 조건부 확인(nit) |

## 3. 원본 렌더 확인 결과

- **캡처 46장 직접 열람**(원본 33 + evidence 13): 전부 390×844 프레임 clip(trace `content_crop` x85 y72.84 w390 h844 · 브라우저 viewport 560×1040을 별도 기록 → 계약의 "canvas ≠ viewport 구별" 충족). 각 캡처의 화면·상태가 case `state`와 일치. 특기: 15/20/23/25 메뉴가 카드 하단 버튼 위로 넘침 · 14/30/31 toast가 등록 버튼 상단과 겹침 · 16/18/27 포커스 accent 테두리 · 21/26 disabled 흐림 · 10 danger Dialog(인주 원반·danger 버튼) · 11 빈 상태 · 설정 캡처에 «관계인 보기» 행+subtitle.
- **원본 URL·버전**: 모든 trace `url` = `http://127.0.0.1:57232/{관계인,설정}.dc.html` · `frozen_version` v5 · source_observation `archive_sha256 bddc54ec…` · entrypoint sha가 design-input/manifest와 일치. 서버 바이트 == design-ref는 visual-check ②-1 curl sha 기록으로 확인(내가 직접 재계산할 도구는 없음).
- **폰트 fallback**: 모든 trace에 Pretendard Variable loaded · lucide 400 loaded. Gowun Batang 400 unloaded / 700 → 설정 trace에서 `error` + woff2 404. 관계인 화면의 범위 안 요소는 전부 sans 토큰(AppBar 제목 `--type-title-3` 2628행 · Dialog h2 `--type-title-2` 1126행 · 본문 caption/body-sm) → fallback 영향 0. **다만 설정 화면 Avatar 이니셜 «유»는 번들 44행 `var(--font-serif)`(=Gowun Batang) → fallback 서체로 렌더**됨. 프로필 카드는 범위 밖(«설정 나머지 무변»)이라 case 판정에는 무영향이나, visual-check ①의 «이 두 화면 미사용 · 렌더 영향 0» 서술은 설정 Avatar에 한해 부정확(정정 필요).
- **런타임 전용 자원**: React/ReactDOM 18.3.1 UMD(unpkg · support.js 동적 로드) · Pretendard woff2 · lucide css/woff2 — trace `resources.runtime`/`fonts`로 관찰 해소. archive external 6건 중 실제 미로드는 Gowun Batang뿐(위 항목).
- **이미지 자산**: asset-manifest images=[] · 원본 소스 `<img>` 0 · 아이콘 전부 lucide 글리프 → 정합.
- **trace 도구 한계(기록 해석 주의 · nit)**: `dialogs` 카운트가 danger Dialog(dialogFit 미적용)에서 0(related-delete-confirm-trace) · `errors` 배열에 Select placeholder 문구가 섞임(22·20·23·24·25·28·29). 상태는 캡처·h2·controls로 증명되므로 판정에 영향 없음.

## 4. 범위변경 근거 대조

- **v5-r1(12) → r2(33)**: 삭제 0 · viewport 축소 0(390×844 유지) · 21 case 추가(관찰 승격). 범위변경 아님.
- **v2/v3/v4(13) → v5-r1(12)**: `related/hour-picker` 삭제. v5 원본 `관계인.dc.html` step3는 `Select`이며 BottomSheet 정의가 없음(135행) → 원본 소스 자체가 삭제 근거. 단 scope.md «확정 이탈» 절은 재동결 **v2**까지만 사용자 출처를 적고, v3/v4/v5 재동결의 사용자 출처(누가·언제 시안을 갱신했는지)는 미기재 → 보완 권고(1줄).
- `_history/v1`의 `related-1440x900-list-original.png`는 case였던 적 없음(v1~v5 design-input.json에 1440 없음) → viewport 축소 아님. 현재 `captures/*-1440x900-*-impl.png`·`480x768-impl`은 G2 stale 산출물이며 case 아님.
- 확정 이탈 6항(relation-kind-8 · birthplace-structured · note-max-500 · settings-row-no-subtitle · list-default-variant-only · PD-2/form-4-step)은 scope에 사용자/발주자 승인 출처가 기재됨. 원본 관찰(관계 8 옵션 · 4-step · Select 피커 · 메모 120)과 이탈 표가 서로 일관.
- 캔버스 knob 4종 미조작은 «list-default-variant-only» 사용자 결정으로 근거 있음.

## 5. 현재 판정

**입력 부족.**

요청 범위 안에서 조작 기록·결과 근거가 둘 다 없는 행이 남는다:

1. **삭제 확인 Dialog · 스크림 click**(§2-1) — 확정 이탈 PD-2가 «시안대로»를 요구하는 삭제 흐름의 조작 대상. 원본 코드는 `cancelDelete`(상세 복귀)이나 관찰 0. visual-check ④에만 «미조작»으로 적히고 «미관찰·한계» 표에 없음(조용한 생략에 해당).
2. **Select 메뉴 열림 상태의 부품 정의 이벤트**(§2-2) — 메뉴 밖 mousedown 닫힘 · Escape 닫힘 · ArrowUp/Down 포커스 이동 · trigger 재클릭. 4개 Select(관계·태어난 시·시·도·시·군)의 공통 부품(`_ds_bundle.js` 2733–2757행)이며 폼 컨트롤 조작의 일부. visual-check 한계 표는 «번들 소스 미열람 · 실제 조작 결과로만 확인»이라 적었으나 실제 조작 기록이 없음.

그 외(삭제 확인·폼 step2~4 Escape 무반응 · 수정 저장 시 변경 값 반영 · 빈 상태 등록 클릭 · 윤달/성별 재토글)는 코드 근거로 예측 가능하거나 같은 핸들러 관찰이 있어 단독으로는 부족 사유가 아니지만, 같은 회차에 함께 해소하기를 권고한다.

## 6. 보완에 필요한 사실

- **필수 관찰(같은 원본 · 원본 컨트롤만)**:
  - 상세(아무 행) → trash-2 → 삭제 확인 Dialog에서 **스크림 click** 1회 → 결과(상세 복귀 예상) 캡처+log step+trace(`related-delete-confirm-trace.json` 갱신 또는 evidence 추가).
  - Select 메뉴(부품 공통이므로 최소 1개, 가능하면 관계+시·군) 열림 상태에서 **메뉴 밖 mousedown → 닫힘**, **Escape → 닫힘**, **ArrowDown → menuitem 포커스 이동**, **trigger 재클릭** 각 1회 → log step + evidence 캡처(`aria-expanded`·listbox 0 확인).
- **권고 관찰**: 삭제 확인·폼 step2/3/4에서 Escape(무반응 확인) · 수정 폼에서 값 1개(예: 이름) 변경 후 저장 → 목록 행/상세 반영 · 빈 목록에서 «관계인 등록하기» click.
- **문서 정정**: visual-check «미관찰·한계» 표에 위 항목을 해소 또는 명시 · ① 폰트 서술을 «설정 Avatar 이니셜은 `--font-serif`(Gowun Batang 700 404) fallback · 범위 밖 요소»로 정정 · trace `dialogs`/`errors` 필드의 selector 한계 1줄 · scope.md에 v3/v4/v5 재동결의 사용자 출처 1줄.
- **재검토 절차**: 보완 후 `check_design_evidence.py --phase prepare` 재실행 → 새 review_digest로 같은 입력범위 재검토. 현재 digest `23908d43…`는 이번 입력에 대한 fail 판정과 짝지어 보존.
- 통과 수준으로 확인된 사실(재관찰 불요): 33 case 전부 조작 기록·결과 근거·캡처 정합 · viewport 일치 · 원본 URL/버전 정합 · disabled 3종(시·군·태어난 시·시·도/시·군)의 비활성 조건과 활성화 경로 관찰 · 입력칸 3종의 click/type/blur 관찰 · 되돌아가기(닫기·이전·스크림·뒤로→설정) 관찰 · 삭제/등록/수정 전이의 데이터 항목(카운트·행 텍스트·toast 문구·tone) 각각 근거 확인.

---

(도구 메모: 이 워크트리에 Serena/Graphify opt-in 표식을 확인하지 않았고 읽기 전용 검토라 두 도구는 사용하지 않았다. Read/Grep/Glob만 사용.)