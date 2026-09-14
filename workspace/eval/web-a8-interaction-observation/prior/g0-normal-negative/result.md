필요한 원본·관찰·이력 대조를 마쳤습니다. 아래는 G0 입력범위 모드의 독립 검토 원문입니다.

---

# G0 입력범위 검토 — A8 web 관계인 (`.dddjango-web/20260912-1640-web-related-persons`)

## 1. 검토한 scope·원본·case 버전

| 항목 | 현재 입력(루트) | 비고 |
|---|---|---|
| `scope.md` | sha `11d2c382…` (design-input.json이 가리키는 바이트) | 본문은 **"재동결 v2 · 관계인 entrypoint sha `1262827593a997bd` · 13 case(hour-picker 포함)"** 를 명시 |
| `source-manifest.json` | `collection=archive` · `archive_ready=true` · `source_ready=false` · 22파일 · `dependencies` external 6건(Google Fonts css·Gowun Batang woff2 ×2·Pretendard woff2·lucide css·lucide woff2) | 정상 archive 형태. `design-ref/` 실제 inventory 22파일과 일치 |
| 원본 entrypoint | `design-ref/관계인.dc.html` sha `cf2fe348…`(**v5**) · `설정.dc.html` sha `b88e995b…` | screen-meta `source_sha256`=cf2fe348 일치 |
| `design-input.json` | **12 case** · 전부 390×844 · 전 case `source_observation` 포함 · `coverage_review` sha `46f0f0aa…` 이미 기재 | `related/hour-picker` 없음 |
| 직전 case 목록 (`_history/v4/design-input.json`) | **13 case** · entrypoint sha `1262827593…`(v2) · `related/hour-picker`(태어난시 BottomSheet) 포함 | v4 `source-manifest`/`screen-meta`는 sha `92376312…` → v3·v4 재동결 때 case·관찰이 원본과 불일치한 채 보존됨 |
| 원본 버전 사슬 | v1 `11db59d9` → v2 `1262827593`(BottomSheet 3회 등장) → v3 `a4ccca75` → v4 `92376312` → **v5 `cf2fe348`**(BottomSheet 0회 · 태어난 시 `Select`) | scope.md 승인 기록은 v2까지 |
| `visual-check.md` | ①·② 절은 v2(13 case·`1262827593`) 서술, §②′ 하단만 v5(12 case·`cf2fe348`·"hour-picker 폐기") 서술 | 같은 문서 안에서 현재 입력 설명이 상충 |
| `asset-manifest.json` | images=[] · unresolved=[] | 이미지 0 = scope.md 기재와 일치 |
| 원본 캡처 | `captures/*-original.png` 12장 + `*-trace.json`/`*-source-observation.json` 12쌍 | 12 observation의 `archive_sha256` 동일(`bddc54ec…`) · `observed_at` **12건 전부 `2026-09-12T17:17:13Z` 동일** |

## 2. 대상별 근거표

원본 `관계인.dc.html`(렌더 + `renderVals`/DS 부품 정의 `_ds_bundle.js`)에서 독립적으로 찾은 조작 대상 전수. Dialog 부품은 overlay `onClick=onCancel`(scrim 탭 = 취소/닫기/이전), Dropdown(Select)은 `Escape`·바깥 mousedown 닫힘·`onOpenChange`를 가진다.

| 진입 상태·조작 대상 | 실제 조작 기록 위치·동작 | 결과 근거 위치 | 연결 case | 판정·보완 |
|---|---|---|---|---|
| 목록 진입(navigate·mount) | `related-list-trace.json` actions[0..1] | `01-list-original.png` · trace dom_observations | related/list | 관찰 확인 |
| 목록 · AppBar «뒤로»(chevron-left → `back()` = history.back/설정.dc.html) | 없음 | 없음 | — | **미관찰** (scope §필수 동작 "뒤로 가기 = 설정으로") |
| 목록 · ListRow 김서연 탭 → 상세 | `related-detail-trace.json` actions[2] "tap 김서연 행" | `02-detail-original.png` | related/detail | 관찰 확인 |
| 목록 · ListRow 이하람 탭 → 상세(음력·윤달·진주시 값) | `related-form-step2-lunar-trace.json` actions[2] (경유) | 없음(이하람 상세 캡처 없음) | related/form-step2-lunar | 조작 확인 · 결과(상세) **미관찰** |
| 목록 · ListRow 박도윤 탭 → 상세(`birth_time_unknown` 분기: "모른다고 하셨어요") | 없음 | 없음 | — | **미관찰** (원본 분기 상태) |
| 목록 · ListRow 정우재 탭 | 없음 | 없음 | — | 미관찰 (김서연과 동일 분기 · 낮은 우선) |
| 목록 · «관계인 등록하기» 탭 | `related-register-step1-trace.json` actions[2] | `06-registerform-step1-original.png` | related/register-step1 | 관찰 확인 |
| 빈 목록 상태 | 없음(원본 URL이 아닌 `_empty-variant.dc.html` navigate) | `11-empty-original.png` | related/empty | 결과만 · **원본 URL/버전 불일치**(§4) |
| 상세 · trash-2 «삭제하기» → 삭제 확인 | `related-delete-confirm-trace.json` actions[3] | `10-deleteconfirm-original.png` | related/delete-confirm | 관찰 확인 |
| 상세 · «수정하기» → 수정 폼 step1 | `related-edit-step1-trace.json` actions[3] | `03-editform-step1-original.png` | related/edit-step1 | 관찰 확인 |
| 상세 · «닫기» → 목록 복귀 | 없음 | 없음 | — | **미관찰** |
| 상세 · scrim 탭(Dialog overlay → `closeDetail`) | 없음 | 없음 | — | **미관찰** |
| 삭제 확인 · «취소» → 상세 복귀(`cancelDelete`) | 없음 | 없음(trace 서술 "확인 시 …"만) | — | **미관찰** |
| 삭제 확인 · «삭제하기» → 목록(3명) + toast «김서연님을 삭제했어요» | 없음 | 없음 | — | **미관찰** (scope 확정 이탈 PD-2 "확인 시 삭제 + 목록 복귀 + toast") |
| 삭제 확인 · scrim 탭 → `cancelDelete` | 없음 | 없음 | — | **미관찰** |
| 폼 step1 · 관계 Select 열기(`onMenu`→`bodyScroll off`·`menuSurface`)·8종 옵션 선택 | 없음 | 없음 | — | **미관찰** (scope 확정 이탈 relation-kind-8의 옵션 목록 렌더 미관찰) |
| 폼 step1 · 이름 Input 클릭·입력·포커스 해제 | 없음 | 없음 | — | **미관찰** |
| 폼 step1 · 성별 ChoicePair «남자» 선택 | 없음 | 없음 | — | **미관찰** |
| 폼 step1(등록) · «다음»(빈값) → 오류 «관계를 선택해주세요» | `related-form-error-trace.json` actions[3] | `07-formerror-original.png` | related/form-error | 관찰 확인 |
| 폼 step1 · «다음»(관계만·이름 빈값) → «이름을 입력해주세요» | 없음 | 없음 | — | **미관찰** |
| 폼 step1 · «닫기» → 목록(`closeForm`) | 없음 | 없음 | — | **미관찰** |
| 폼 · scrim 탭 → `formCancel`(step1=닫기 / step≥2=**이전 단계**) | 없음 | 없음 | — | **미관찰** (원본 특유 동작) |
| 폼 step1(수정·김서연) · «다음» → step2 양력 | `related-form-step2-solar-trace.json` actions[4] | `04-form-step2-solar-original.png` | related/form-step2-solar | 관찰 확인 |
| 폼 step1(수정·이하람) · «다음» → step2 음력·윤달 | `related-form-step2-lunar-trace.json` actions[4] | `04b-form-step2-lunar-original.png` | related/form-step2-lunar | 관찰 확인 |
| 폼 step2 · 생년월일 Input 입력(숫자→`1992.07.04` 점 포맷)·포커스 해제 | 없음(프리필 값만) | 없음 | — | **미관찰** |
| 폼 step2 · 역법 ChoicePair 양력→음력 토글(윤달 Checkbox 출현) | 없음 | `04b`(프리필 상태만) | related/form-step2-lunar | 조작 없음 · 결과만 |
| 폼 step2 · 윤달 Checkbox 토글 | 없음 | 없음 | — | **미관찰** |
| 폼 step2 · «이전» → step1 | 없음 | 없음 | — | **미관찰** |
| 폼 step2 · «다음»(8자리 아님) → «생년월일을 여덟 자리로 입력해주세요» | 없음 | 없음 | — | **미관찰** |
| 폼 step2 · «다음» → step3 | `related-form-step3-trace.json` actions[5] | `05-form-step3-hour-original.png` | related/form-step3 | 관찰 확인 |
| 폼 step3 · 태어난 시 Select 열기(12지시 + `description` 시간범위·`menuSurface`) | 없음(dom_observations의 "열면 …"은 서술) | 없음 | — | **미관찰** (v5에서 BottomSheet를 대체한 핵심 상태) |
| 폼 step3 · «태어난 시간을 몰라요» 체크 → Select `disabled` | 없음 | 없음 | — | **미관찰** |
| 폼 step3 · «다음»(빈값) → «태어난 시를 선택하거나 모른다고 알려주세요» | 없음 | 없음 | — | **미관찰** |
| 폼 step3 · «이전» → step2 | 없음 | 없음 | — | **미관찰** |
| 폼 step3 · «다음» → step4 | `related-form-step4-trace.json` actions[6] | `09-form-step4-original.png` | related/form-step4 | 관찰 확인 |
| 폼 step4 · 시·도 Select 열기/도 단위 선택 → 시·군 활성·옵션 갱신 | 없음(서울 프리필 → 시·군 disabled 상태만) | 없음 | — | **미관찰** (이하람 경남·진주시 프리필로 관찰 가능했으나 미실행) |
| 폼 step4 · 시·군 Select 활성 상태·선택 | 없음 | 없음 | — | **미관찰** |
| 폼 step4 · «태어난 곳을 못려요» 체크 → 시·도/시·군 disabled + placeholder «태어난 곳은 물지 않을게요» | 없음 | 없음 | — | **미관찰** (PD-3 구조 피커·`BirthPlaceIn.kind=UNKNOWN`과 맞물리는 상태) |
| 폼 step4 · 메모 Textarea 입력·카운터 갱신·포커스 해제 | 없음(프리필 24/120만) | `09`(상태) | related/form-step4 | 조작 없음 · 결과만 |
| 폼 step4(수정) · «저장하기» → 목록 복귀 + toast «…님 정보를 저장했어요» | 없음 | 없음 | — | **미관찰** (scope §필수 동작 "성공 뒤 목록 복귀") |
| 폼 step4(등록) · «등록하기» → 목록 5명 + toast «…님을 등록했어요» | 없음 | 없음 | — | **미관찰** (등록 흐름은 step1만 관찰) |
| 폼 step4 · «저장/등록»(시·도 또는 시·군 미선택) → «시 · 도를 선택해주세요»/«시 · 군을 선택해주세요» | 없음 | 없음 | — | **미관찰** |
| 폼 step4 · «이전» → step3 | 없음 | 없음 | — | **미관찰** |
| Toast(등록/저장/삭제 · `ns.Toast` floating) 외형 | 없음 | 없음 | — | **미관찰** |
| 설정 진입(navigate·mount) | `settings-related-row-trace.json` actions | `settings-390x844-related-row-original.png` | settings/related-row | 관찰 확인 |
| 설정 · «관계인 보기» 행 탭 → `goRelations` → 관계인.dc.html 이동 | 없음 | 없음 | — | **미관찰** (요청 범위의 진입 경로) |
| 설정 · 나머지 행/탭바/로그아웃/탈퇴 | — | — | — | 요청 밖(scope "설정 나머지 무변") |

관찰 확인 12행 / 조작 없음·결과만 3행 / 미관찰 30행+. **요청 범위 안의 미관찰 행이 남는다.**

## 3. 원본 렌더 확인 결과

- 12장 모두 390×844 AppFrame 크롭이며 캡처 내용이 case `state`와 일치한다(목록 4명·관계 accent·빈 목록·상세 trash-2·danger 확인·등록/수정 step1·step2 양력/음력+윤달·step3 Select «유시»·step4 시·도 서울/시·군 disabled/«못려요»/메모 24/120·오류 인주색·설정 «관계인 보기»+subtitle «등록한 사람 4명»).
- 아이콘: lucide 글리프(heart·users-round·user-round·chevron·trash-2·calendar·contact-round·user-round-plus) 정상 표시 → lucide CDN css/woff2 로드 성공으로 추정되나 **trace에 그 응답 기록이 없다**.
- 폰트: 본문은 산세리프 렌더. Pretendard(jsDelivr) 실제 로드 여부는 trace에 성공/실패 어느 쪽도 기록 없음(`fonts:` 항목은 토큰 이름 기재일 뿐). 관계인 화면은 `--font-serif` 사용처(display/quote/Avatar/Wordmark)가 없어 Gowun Batang 실패의 영향이 없다. 설정 화면 Avatar «유»만 serif 토큰이며 설정 trace에 Gowun Batang 실패가 기록돼 fallback 렌더(범위 밖 요소 · nit). 같은 `fonts.css`를 로드하는 관계인 11 case에는 동일 요청 실패가 기록되지 않아 기록 일관성이 없다.
- 장식: DS 배경 그라디언트·글래스 패널·스크림 블러·상태바 "9:41"·홈 인디케이터(AppFrame 장식) 렌더됨. 이미지 자산 0 = asset-manifest 일치.
- trace 형식 문제: (a) `canvas` 서술은 "rendered at **560×1040** viewport, clipped to frame"인데 `browser_viewport`는 390×844로 기록 — 실제 브라우저 viewport와 content crop을 분리 기록하지 않고 동일시함. (b) `observed_at` 12건 동일 초 → 실제 관찰 시각이 아닌 일괄 값(visual-check.md는 재관찰을 2026-09-13이라 함). (c) `dom_observations`에 D1·D7·V4-1·CH-1 등 구현 해석 코드가 섞여 있고 요청 로그·DOM/style 실측이 없어 "실제 브라우저 출력"보다 Coordinator 요약에 가깝다. (d) unpkg React/ReactDOM/**Babel standalone**(support.js:1143–1147) 로드 응답 미기재.
- 빈 목록 case: `source_observation.url`이 `_empty-variant.dc.html`(관찰 후 삭제된 변형본)이고 entrypoint는 `관계인.dc.html`로 기록 → **원본 URL이 해당 archive 버전을 제공한 사실을 확인할 수 없다.** 원본 자체가 `$preview` knob `listState: '비어 있음'`을 제공하므로 변형본 없이 관찰 가능했다.

## 4. 범위변경 근거 대조

- **hour-picker case 삭제·원본 교체(v2→v5)의 구체 사용자 범위변경 출처가 없다.** scope.md(현재 digest에 묶인 바이트)는 "재동결 v2 · sha `1262827593` · 13 case"를 사용자 요구 범위로 적고 있고 "확정 이탈" 절의 승인 기록도 v2(PD-2 삭제 흐름·form-4-step)까지다. 현재 동결본 v5(`cf2fe348`)와 12 case는 이와 다르며, visual-check.md §②′의 "hour-picker 폐기(v5 부재) · scope.md는 v2 스냅샷으로 남음 · design-input이 정본"은 Coordinator 서술이지 사용자 결정 출처가 아니다. design-input.json은 case 목록의 기계 정본이지 사용자 범위의 출처가 될 수 없다.
- v5가 원본에 새로 넣은 항목(visual-check.md §②′ 기재: 태어난 시 Select·태어난 곳 몰라요·목록 accent·상세 접두·태어난 곳 축약·중앙정렬·DS tokens 값)은 scope.md "디자인 출처"·"확정 이탈" 어디에도 없다. 특히 «태어난 곳을 못려요»(원본 오타 그대로)는 PD-3와 맞물리는 새 상태인데 case로도 없다.
- `scope_refs` 앵커 `scope.md#related_persons`·`scope.md#preferences`는 scope.md에 존재하지 않는 절이다(실제 헤딩: 모드 판별/영역 배치/실행 경계/디자인 출처/…/디자인 case 표).
- 이력 정합: `_history/v4/design-input.json`은 v2 sha를 가리키는데 같은 폴더의 manifest/screen-meta는 v4 sha `92376312` → v3·v4 재동결에서 case·관찰이 갱신되지 않은 채 보존됐다. "이전 case 목록"으로 제시된 v4는 실제로는 v2 관찰이다.
- viewport 축소 없음(전 case 390×844 유지) — 이 축은 이상 없음.

## 5. 현재 판정

**입력 부족.** 근거: (1) scope.md가 지목하는 원본·case 범위(v2·13 case)와 현재 동결 입력(v5·12 case)이 다르고 그 변경의 사용자 출처가 없다. (2) 요청 범위 안 조작 대상(삭제 확정→목록+toast, 저장/등록→목록+toast, 뒤로 가기→설정, 설정 행→관계인 진입, Select 열림, 몰라요/못려요 체크 상태, 시·군 활성, step2~4 오류, 닫기/취소/이전/scrim)의 실제 조작·결과 관찰이 없다. (3) 빈 목록 case가 archive 밖 URL로 관찰됐고 trace가 실제 브라우저 viewport·요청 로그를 담지 않는다.

`archive_ready=true`·`source_ready=false`는 정상 보관 상태로 보며 이것 자체는 반송 사유가 아니다. "승인되면 통과"는 현재 입력의 판정이 아니다.

## 6. 보완에 필요한 사실

1. **사용자 결정 필요**: 원본을 v2(`1262827593` · 태어난 시 BottomSheet · 13 case)로 되돌릴지, v5(`cf2fe348` · Select · 12 case)로 확정할지. v5 확정이면 scope.md에 v3~v5 변경 항목(Select 전환·못려요 체크·accent·접두·축약·중앙정렬·토큰 값)과 hour-picker case 삭제의 승인 출처(발주서 개정 번호·일시·원문)를 기록해야 한다. 이 결정은 case 목록(hour-picker 삭제/유지)과 폼 step3의 대상 외형을 바꾼다.
2. 미관찰 30행에 대한 실제 브라우저 조작·결과 관찰. 최소한 scope 필수 동작 6건(삭제 확정+toast·저장+toast·등록+toast·뒤로 가기·설정 행 진입·오류 4종)과 v5 특유 상태 4건(태어난 시 Select 열림·몰라요 disabled·못려요 disabled+placeholder·도 단위 시·군 활성). 새 case 후보: `related/hour-select-open`·`related/hour-unknown`·`related/place-unknown`·`related/place-city-enabled`·`related/form-error-step2|3|4`·`related/toast-register|save|delete`·`related/detail-time-unknown`(박도윤). 채택 여부는 Coordinator·사용자 소유.
3. 빈 목록: 동결 원본 URL + `listState='비어 있음'` knob으로 재관찰하거나, 변형본 바이트를 archive에 보관하고 그 행을 case entrypoint로 등록.
4. trace를 실제 브라우저 출력으로: 실제 viewport(560×1040)와 crop(390×844) 분리 기록, 요청 로그(unpkg React/ReactDOM/Babel·Pretendard woff2·lucide css/woff2·Google Fonts 상태코드), 실제 `observed_at`, 해석 코드(D1·D7·V4-1·CH-1)는 관찰과 분리.
5. `scope_refs`를 scope.md에 실재하는 절로 고정. visual-check.md ①·② 절을 현재 입력(v5·12 case)과 일치시킬 것(현재 v2 서술과 §②′ v5 서술이 상충).
6. `_history/v3`·`v4`의 design-input/관찰이 해당 원본 sha와 불일치한 상태로 보존된 사실을 이력 메모로 남길 것(판정과 무관 · 추적성).

reviewed-input: 25b5b07800613c1c7593ca5f53af6235840b3b1300e62433a6a58488c9962719
review-result: fail

---

(Serena·Graphify 생략 — 코드가 아닌 동결 증거·문서 대조 작업이라 심볼 도구 불필요.)