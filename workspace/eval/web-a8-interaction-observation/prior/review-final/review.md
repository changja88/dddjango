지금까지 12장 PNG·12 trace·12 observation·manifest·scope·render-audit·motion-notes·asset-manifest·이력(v1~v4)·lane 문서를 모두 열어 대조를 마쳤습니다. 이 세션에는 Playwright MCP 도구가 노출되지 않아 실브라우저 관찰은 하지 않았고(진단 산출물 0), 동결 바이트와 제공된 관찰 증거만으로 판정합니다. 추가로 필요한 입력은 없으므로 검토 원문을 냅니다.

---

# 입력범위(coverage) 독립 검토 — A8 web 관계인 · 재동결 v5

## 0. 검토한 scope·원본·case 버전

| 항목 | 확인 값 |
|---|---|
| scope.md | design-input `scope.sha256 11d2c382…`(v4 design-input과 동일 값 → v2 내용 그대로). 본문 §디자인 case 표는 **v2 스냅샷**(관계인 sha `1262827593a997bd` · `related/hour-picker` 행 포함 · 13 case). |
| 원본 entrypoint | `design-ref/관계인.dc.html` = source-manifest row sha `cf2fe348…`(34,922B) = screen-meta `source_sha256` = 11개 관계인 case `entrypoint.sha256` 전부 일치. `설정.dc.html` `b88e995b…`(v1~v5 무변) = settings case 일치. |
| manifest | `collection=archive` · `archive_ready=true` · `source_ready=false`(정상) · 22 files 전부 `ok`(0 missing) · dependencies 외부 6(Gowun Batang css/woff2×2 · Pretendard woff2 · lucide css/woff2 = 런타임 관찰 대상). |
| design-input | 12 case · 전부 viewport 390×844 · `scope_refs` = `scope.md#related_persons`/`#preferences`. |
| observation 12 | `archive_sha256` 12/12 = `bddc54ec…`(서로 일치 · 이 환경엔 해시 도구가 없어 manifest 바이트 재계산은 못 함 — `--phase prepare` 기계 검사 소관). entrypoint·case_id·screen·state·viewport·capture sha 12/12 design-input과 정확 일치(아래 (c)). |
| 이력 | `_history/v1~v4` 보존. 현재 `captures/`의 12 original PNG sha는 v4 값과 전부 다름(재관찰 사실 확인). trace `frozen_version` 12/12 "v5". |
| v5 범위변경 출처 | lane `REPORT-web-related-persons-a8.md` §재동결 표(v2→v3 CH-1 Select화 · v3→v4 V4-2 몰라요 · v4→v5 개정 13·14 사용자 결정 5) · `GATE-…-refreeze-v4.md` · `GATE-…-a8-4.md`. **scope.md에는 미반영.** |

## (a) 상태 → case 커버리지 표 (관계인.dc.html v5 sc-if를 직접 열거)

| 원본 분기(소스 줄) | 상태 | case | 판정 |
|---|---|---|---|
| `hasPeople`(L48) | 목록 4명 · 관계 accent 첫머리 | related/list | 관찰 확인 |
| └ `g.hasLabel`(L58) | 관계별 묶음 knob variant | — | 요청 밖(scope 이탈 list-default-variant-only) |
| `isEmpty`(L74) | 빈 목록 | related/empty | **미관찰(동결 바이트 기준)** — 아래 (c)-1 |
| `hasDetail`(L85) | 상세 Dialog + trash-2 | related/detail | 관찰 확인(김서연) |
| `hasDeleteAsk`(L102) | danger 확인 Dialog | related/delete-confirm | 관찰 확인 |
| `hasForm`·`isStep1`(L112) | step1 빈값 / 값채움 | register-step1 / edit-step1 | 관찰 확인 |
| `isStep2`(L120) · `isLunar`(L125) | 양력 / 음력·윤달 | form-step2-solar / -lunar | 관찰 확인 |
| `isStep3`(L132) | 태어난 시 Select + 몰라요 | form-step3 | 관찰 확인(몰라요 **미체크** 상태만 — 체크→Select disabled 미관찰) |
| `isStep4`(L141) | 시·도/시·군 Select + 몰라요 + 메모 | form-step4 | 관찰 확인(서울=시·군 disabled 변형만 — 시·군 **활성**(예: 이하람 경남·진주시)·몰라요 체크 미관찰) |
| `hasErr`(L153) | 인주색 오류 1줄 | form-error | 관찰 확인(step1 문구 · 나머지 문구는 동일 분기, 소스 L382-387 확정) |
| `state.toast`(L358·L473 · sc-if 아님) | Toast(삭제 «…님을 삭제했어요» / 등록·저장 success) | **없음** | **미관찰** — scope PD-2가 toast 문구까지 요구 |
| Select `on-open-change`→`bodyScroll off`(L135·L408·L411) | 드롭다운 열림(태어난 시 12지시+시간범위 description · 종이 surface · maxHeight 264) | **없음** | **미관찰** — v2 hour-picker case를 폐기하면서 v5 대체 시각(열린 Select)이 case로 추가되지 않음 |
| BottomSheet(hour-picker) | — | 없음 | **정상** — v5 소스에 시트 import·분기 없음(step3=Select L135). case 부재는 갭 아님 |
| `설정.dc.html` L55 ListRow contact-round «관계인 보기» | 설정 관계인 행 | settings/related-row | 관찰 확인 |

### 독립 발견한 조작 대상 → 관찰 근거 대조

| # | 대상(소스) | 결과 | 판정 |
|---|---|---|---|
| 1 | AppBar chevron-left «뒤로»(L466 `back`) | history.back / 설정.dc.html 이동 | 미관찰(조작 기록 없음 · 도착 화면 자체는 settings case에 있음) |
| 2 | ListRow tap(L334) | 상세 Dialog | 관찰 확인(detail·lunar trace "tap 김서연/이하람 행") |
| 3 | «관계인 등록하기»(L352) | 등록 step1 | 관찰 확인 |
| 4 | 상세 trash-2(L89) | 삭제 확인 | 관찰 확인 |
| 5 | 상세 «닫기»(L403) | 목록 복귀 | 미관찰(조작 기록 없음) |
| 6 | 상세 «수정하기»(L404) | 수정 step1 | 관찰 확인 |
| 7 | 삭제 확인 «취소»(L274) | **상세 Dialog로 복귀**(confirmId null · openId 유지) | 미관찰 — visual-check ③-이월 #4가 구현은 «닫힘»으로 갔다고 적고 있어 원본 관찰이 특히 필요 |
| 8 | 삭제 확인 «삭제하기»(L275) | 목록 + toast | 미관찰(trace는 결과를 서술만, 액션 목록에 없음) |
| 9 | 관계 Select 열기/선택(L114) | 8종 메뉴 | 미관찰(열림 상태) |
| 10 | 이름 Input 입력·포커스(L115) | 값·focus-visible | 미관찰(DS `:focus-visible` 규칙은 render-audit에 존재 · 캡처 0) |
| 11 | 성별 ChoicePair 토글(L116) | 선택 이동 | 미관찰(선택/비선택 외형은 한 캡처에 공존) |
| 12 | 생년월일 Input 타이핑(L123 · `faceOf` 점 자동 삽입) | 1992.07.04 꼴 | 미관찰(프리필 값만) |
| 13 | 역법 토글 → 윤달 Checkbox 출현(L124-126) | 양력/음력 | 관찰 확인(두 case로 양 상태) |
| 14 | 태어난 시 Select 열기 · 몰라요 체크(L135-136) | 메뉴 / disabled | 미관찰 |
| 15 | 시·도 변경 → 시·군 활성·옵션(L144-145) · 몰라요 체크 | 활성/disabled | 미관찰(서울 disabled 변형만) |
| 16 | 메모 Textarea 입력·카운터(L149) | 24/120 | 관찰 확인(카운터 보임) |
| 17 | 폼 «닫기»/«이전»(L421-423) | 닫힘 / 이전 단계 | 미관찰(조작 기록 없음) |
| 18 | 폼 «다음»(L424-426) | 다음 단계 / 오류 | 관찰 확인 |
| 19 | «등록하기»/«저장하기»(L427 `saveForm`) | 목록 + toast | 미관찰 |
| 20 | 설정 «관계인 보기» tap(설정 L149) | 관계인.dc.html 이동 | 미관찰(조작 기록 없음 · 도착 화면=list case) |
| 21 | 설정 나머지 행·로그아웃·탈퇴 | — | 요청 밖(scope «설정 나머지 무변») |

## (b) 캡처별 대응 판정 (12장 전부 Read 로 육안 확인)

| PNG | 육안 확인 | 판정 |
|---|---|---|
| 01-list | 4행 · 관계 «배우자/부모/자녀/친구»가 이름 아래 첫머리 **도화 accent**(render-audit rgb(185,90,100)) · 이하람 «음력» 접두 · 박도윤 «시간 모름» · heart/users-round/user-round/chevron 실제 글리프 · «등록한 사람 4명»/«눌러서 수정할 수 있어요» · 하단 안내문 · 떠있는 «관계인 등록하기»(user-round-plus) · 9:41 상태바~홈 인디케이터 390×844 프레임 crop | v5 일치 |
| 11-empty | contact-round(32px tertiary) · «아직 등록한 관계인이 없어요» · 안내문 · 헤더 캡션 없음 · 떠있는 등록 버튼 | 화면 내용은 v5 `isEmpty` 분기와 일치 — **출처는 변형본**((c)-1) |
| 02-detail | «김서연» + trash-2 danger 색 · 관계 배우자 / 성별 여자 / **생년월일 «양력 1992. 07. 04.»**(접두) / 태어난 시 «유시 (17:30–19:29)» / **태어난 곳 «서울»**(축약) / 메모 · 닫기/수정하기 · 스크림 뒤 등록 버튼 없음 | v5 일치 |
| 10-deleteconfirm | danger tone · trash-2 원반 · «김서연님을 삭제할까요?» · 설명 문구 · 취소(ghost)/삭제하기(danger) · 상세 Dialog는 숨김(`hasDetail: open && !del`) | v5 일치 |
| 06-registerform-step1 | «관계인 등록» · ProgressBar **세그먼트 4 중 1(카운트 라벨 없음)** · 관계 placeholder · 이름(user-round) · 성별 여자 기본 · 닫기/다음 | v5 일치 |
| 03-editform-step1 | «관계인 수정» · 배우자 · 김서연 · 여자 | v5 일치 |
| 04-form-step2-solar | 2/4 · calendar 아이콘 «1992.07.04» · 양력 선택 · 윤달 없음 · 이전/다음 | v5 일치 |
| 04b-form-step2-lunar | «1963.05.30» · 음력 선택 · «윤달에 태어났어요» 체크 | v5 일치 |
| 05-form-step3-hour | 3/4 · «태어난 시» 라벨 · **Select «유시» + chevron-down**(시트 아님) · «태어난 시간을 몰라요» 미체크 | v5 일치 |
| 09-form-step4 | 4/4 · 시·도 «서울» · 시·군 disabled «시·도까지만 받아요» · «태어난 곳을 못려요»(mock 오타 원본 그대로) · 메모 + «24/120» · 이전/저장하기 | v5 일치 |
| 07-formerror | 등록 step1 빈값 · «관계를 선택해주세요» 인주색 1줄 · 닫기/다음 유지 | v5 일치 |
| settings-related-row | 설정 · 프로필 카드 · 사주 그룹 4행(생년월일시 변경·만세력·기질·**관계인 보기** contact-round + «등록한 사람 4명») · 결제·계정 · TabBar 4탭 설정 활성 | 일치(설정 무변) |

lucide 글리프: 12장 전부 실제 아이콘(tofu 0). 폰트: 측정 텍스트 전부 Pretendard(render-audit `fontFamily` 15/15) — 설정 trace만 Gowun Batang woff2 실패를 기록하나 두 화면 모두 표시 텍스트는 sans라 가시 영향 없음(관계인 trace 11개엔 같은 항목이 없어 세션 간 네트워크 상태 불일치 — 기록 정합성 nit).

## (c) 정합 / 갭 / 오캡처

**정합 확인(통과)**
- sha 사슬: design-input 12 case entrypoint = manifest row = screen-meta = observation entrypoint(12/12). observation `capture.sha256` = design-input `reference_capture.sha256` 12/12(6ced2769·8105ed5a·f3b56529·2d691543·4ea0f28b·d298ee31·242566c0·ef926df6·9dafa12e·d2079dc9·1d9d453a·68d593d7). `archive_sha256` 12/12 동일값.
- v1~v4 누출: design-input·captures(original)·trace·observation·render-audit(url 8731 · accent 실측)·motion-notes(m5 시트→Select)·asset-manifest(images [] — 소스에 `<img>` 0, 정합) 전부 v5. `_ds` colors/glass sha는 v3 이후 무변(bc25c6ba·3486a5e7)이라 Coordinator 항목 6(DS 값 변경)은 v2 대비 서술로 정합.
- 외부/런타임 자원: manifest 외부 6 + support.js가 런타임 로드하는 unpkg React 18.3.1(manifest `dependencies`엔 runtime 행 없음)이 12 trace에 로드·mount로 기록되고 PNG가 글리프·폰트를 보여줌 → 런타임 자원 관찰 해소.

**갭·오캡처(판정을 바꾸는 항목)**

1. **`related/empty` 관찰 출처가 동결 바이트가 아님.** observation `url` = `http://127.0.0.1:8731/_empty-variant.dc.html`, trace 액션 = «PEOPLE=[] 변형본 … 관찰 후 변형본 삭제». 변형본은 archive에 없고(manifest 22 files·design-ref 3 top-level에 부재) 삭제되어 바이트 검증이 불가능한데 observation은 entrypoint sha `cf2fe348`을 주장한다. 즉 «원본 URL이 해당 archive 버전을 제공한 사실»이 이 case에서 성립하지 않는다. «PEOPLE만 비운 같은 화면»이라는 것은 소스 추론이며 관찰 확인 근거로 쓸 수 없다. 동결 원본은 자체 UI로 빈 상태에 도달한다(상세→trash-2→삭제하기 ×4 → `people=[]` → `isEmpty`) — 바이트 무변 관찰 경로가 있음에도 쓰지 않았다. (v4 trace도 같은 방식 — 이전 라운드부터 이어진 결함.)
2. **v5 시안 상태 case 누락**: ⓐ Toast(삭제 «{이름}님을 삭제했어요» — scope §확정 이탈 PD-2 명시 · 등록/저장 success) ⓑ Select 열림(태어난 시 12지시 + 시간범위 description · `menuSurface` 종이 surface · maxHeight 264 — 폐기된 hour-picker case의 v5 대체 시각인데 후속 case 없음) ⓒ step3 «몰라요» 체크(Select disabled · 박도윤 수정 진입으로 프리필 도달 가능) ⓓ step4 시·군 활성(이하람 경남·진주시) · «몰라요» 체크(양 Select disabled + placeholder «태어난 곳은 물지 않을게요»). 요청 범위(관계인 화면 전체 상태) 안의 미관찰 행이다.
3. **조작 기록 부재**: 뒤로 · 상세 닫기 · 삭제 취소(원본은 **상세로 복귀**) · 삭제 확정 · 저장/등록 확정 · 폼 닫기/이전 · 설정 «관계인 보기» tap이 어느 trace의 `state_transition_actions`에도 없다(결과 화면이 다른 case에 있어도 조작 근거는 별도).

**정합 결함(단독으로는 판정을 바꾸지 않음)**
4. trace 내부 모순: `browser_viewport` 390×844 vs `canvas` «rendered at 560x1040 viewport, clipped to frame». 계약은 실제 브라우저 viewport와 crop을 따로 적으라고 한다 — 필드가 case viewport와 동치로 적혀 있음(주석으로 드러나므로 '침묵'은 아님).
5. `observed_at` 12/12 = `2026-09-12T17:17:13Z` 초 단위까지 동일(다단계 조작 case 포함) → 관찰 시각이 아닌 일괄 기입값.
6. **scope.md ↔ v5 부정합**: §디자인 case 표가 v2(sha `1262827593a997bd` · hour-picker 행 · 13 case), §확정 이탈 form-4-step «N / 4단계» 라벨(v5는 제거), PD-1 «시안 6개»/PD-3 «시안 자유 텍스트»(v5 시안은 8종·구조 Select라 더 이상 이탈이 아님), «태어난 곳 몰라요»·D1 접두·D7 축약·v5 출처(개정 13·14)가 없음. `scope_refs`의 `#related_persons`/`#preferences` 앵커도 scope.md에 해당 제목이 없다. 범위변경 근거 자체는 lane REPORT/GATE에 있으므로 hour-picker 폐기는 정당하나, digest에 고정된 scope 문서가 case 집합과 어긋난 채 남아 있다(visual-check가 «digest 파손이라 미편집»이라고 스스로 적음 — 다음 re-prepare 라운드에서 함께 갱신해야 함).

## 범위변경 근거 대조

- 13→12(hour-picker 폐기): v3 시안 변경 CH-1(사용자가 시안 수정 · 발주서 개정 9) → v5 소스에 시트 분기 없음(직접 확인). **근거 있음.** 다만 대체 상태(열린 Select)가 case로 보강되지 않음((c)-2ⓑ).
- v4→v5 변경(관계 8종 라벨·D1·D7·중앙정렬): REPORT §v4→v5(개정 13·14 사용자 결정 5). **근거 있음** · scope.md 미반영((c)-6).
- viewport 축소·삭제: 없음(12 case 전부 390×844 유지).

## 현재 판정

**입력 부족(fail).** 사유 = (c)-1 빈 목록 case의 관찰이 동결 원본이 아닌 미보관·삭제 변형본에서 나옴 + (c)-2 요청 범위 안 시각 상태(Toast·Select 열림·몰라요 체크·시·군 활성)의 미관찰 행 잔존 + (c)-3 조작 근거 누락. 12장 PNG의 내용 자체는 전부 v5 상태와 일치하며 sha 사슬도 12/12 정합이므로, 보완은 재관찰·case 추가 중심이다.

## 보완에 필요한 사실 (같은 입력범위 재검토 전제 · 전부 한 라운드에서)

1. `related/empty`: 동결 `관계인.dc.html`(cf2fe348)에서 삭제 흐름 ×4로 빈 상태 도달 후 재캡처 · observation `url`을 entrypoint로 · trace 액션에 4회 삭제와 toast 소멸 대기 기록. (변형본 방식을 유지하려면 그 파일을 archive에 포함하고 case entrypoint로 선언해야 하나 inventory=reference_root 규칙상 재archive가 필요 — 권하지 않음.)
2. case 추가 후보(각 390×844 · trace·observation 동반): `related/toast-deleted`(삭제 확정 직후) · `related/form-step3-hour-open`(Select 열림) · `related/form-step3-unknown`(몰라요 체크 · 박도윤 수정) · `related/form-step4-city`(이하람 · 시·군 활성) · `related/form-step4-unknown`(몰라요 체크). 제외하려면 각 항목에 구체 결정 출처(예: Select 메뉴는 native 처리라 비교 대상 아님)를 scope에 기록.
3. 조작 근거: 뒤로/상세 닫기/삭제 취소(상세 복귀 확인)/삭제 확정/저장·등록 확정/폼 닫기·이전/설정 행 tap을 해당 trace `state_transition_actions`에 실제 실행으로 기록.
4. trace `browser_viewport`를 실제 값(560×1040)으로, `content_crop` 390×844 유지 · `observed_at`은 case별 실제 시각.
5. scope.md §디자인 case 표를 v5(12+추가 case · sha cf2fe348)로, §확정 이탈에서 v5 시안이 해소한 PD-1/PD-3 서술·«N / 4단계» 문구를 정리하고 v5 출처(개정 13·14)와 `scope_refs` 앵커 제목을 추가 — scope 바이트가 digest에 들어가므로 1~4와 같은 prepare 라운드에서.
6. 이 검토는 브라우저 미실행(세션에 Playwright MCP 미노출 · `/tmp/dddjango-web-a8-interactions-20260913/review-final/browser` 산출 0)이며 해시 재계산 도구가 없어 `archive_sha256`·review_digest는 구조 대조만 했다.

reviewed-input: 25b5b07800613c1c7593ca5f53af6235840b3b1300e62433a6a58488c9962719
review-result: fail
