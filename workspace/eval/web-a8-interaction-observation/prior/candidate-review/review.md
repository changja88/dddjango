브라우저·해시 도구가 이 세션에 노출되지 않아 정적 증거(원본 HTML·JSON 포인터·PNG 육안)로 대조를 마쳤다. 발주서 a8 사본의 «개정 이력»은 작성 1건뿐(개정 9~15 원문 부재)임을 확인했고, 더 요청할 항목은 없다. 아래가 검토 원문 전체다.

---

# coverage-review — A8 web 관계인 · 재동결 v5 입력범위 독립 검토

## 0. 검토한 scope·원본·case 버전

- build: `.dddjango-web/20260912-1640-web-related-persons/` · project `~/.herdr/worktrees/spring_dream_server/a8`
- 직접 연 파일: `scope.md` · `design-input.json`(12 case) · `source-manifest.json`(archive · 22 files · 0 missing · 관계인 row `cf2fe348…` · 설정 `b88e995b…`) · `screen-meta.json`(`source_sha256 cf2fe348…`) · `design-ref/관계인.dc.html`(v5 · 480행) · `design-ref/설정.dc.html` · `captures/*-original.png` 12장 전부 · `*-trace.json` 12 · `*-source-observation.json` 12 · `render-audit.json`(audit_version 2 · texts 15 · pinned 0) · `motion-notes.md`(v5) · `asset-manifest.json`(images [] · unresolved []) · `visual-check.md` · `build-state.json` · 발주서 a8 사본 · lane GATE/REPORT 요약(grep) · implementation-ui `references/design-evidence.md`.
- 미열람(의도): 이전 `coverage-review.md`(v2~v5) · `design-spec.md` · `design-review.md` · 구현 코드. build-state/visual-check에 적힌 «coverage pass 25b5b078» 결론은 판정 입력에서 배제했다.
- 실행 한계: Playwright MCP·sha256 계산 도구가 이 세션의 호출 가능 목록에 노출되지 않았다 → 브라우저 재관찰 0 · 바이트 재해시 0. sha 대조는 JSON 포인터 문자열의 상호 일치로만 수행했고, `design-input.scope.sha256(11d2c382…)`↔현재 scope.md 바이트 일치는 미검증이다.

## (a) 원본 분기 → case 커버리지 표

`관계인.dc.html`(v5)의 `sc-if`를 직접 열거했다(줄 번호 = design-ref 파일).

| 원본 분기 (줄) | 조건 | case | 캡처 | 판정 |
|---|---|---|---|---|
| `hasPeople` (48–72) | people.length>0 | related/list | 01-list | ✓ |
| `isEmpty` (74–80) | people.length==0 | related/empty | 11-empty | ✓ 상태 일치 · **출처 결손(c-3)** |
| `hasDetail` (85–100) | openId && !confirmId | related/detail | 02-detail | ✓ |
| `hasDeleteAsk` (102–104) | confirmId | related/delete-confirm | 10-deleteconfirm | ✓ |
| `hasForm`+`isStep1` (106–118) · draft 빈값 | 등록 | related/register-step1 | 06 | ✓ |
| `hasForm`+`isStep1` · draft 프리필 | 수정 | related/edit-step1 | 03 | ✓ |
| `isStep2` (120–130) · solar | 윤달 미표시 | related/form-step2-solar | 04 | ✓ |
| `isStep2`+`isLunar` (125–127) | 윤달 Checkbox | related/form-step2-lunar | 04b | ✓(체크됨) |
| `isStep3` (132–139) | Select 닫힘·몰라요 미체크 | related/form-step3 | 05 | ✓ 휴지 상태만 — **열림·체크 상태 미관찰(a′-15·16)** |
| `isStep4` (141–151) | 서울·시·군 disabled·못려요 미체크 | related/form-step4 | 09 | ✓ 휴지 상태만 — **등록 빈값·도 지역·체크 상태 미관찰(a′-18·19·23)** |
| `hasErr` (153–155) | step1 '관계를 선택해주세요' | related/form-error | 07 | ✓ |
| `g.hasLabel` (58–60) | 관계별 묶음 knob | — | — | case 불요 ✓ (scope «list-default-variant-only» 확정) |
| Toast (358·473) | 삭제/등록/저장 후 | **없음** | — | ✗ (a′-8·21) |
| BottomSheet/hour-picker | **v5 소스에 없음**(135행 = `Select`) | 없음 | — | case 없음 = 정상. 단 **대체 상태(Select 메뉴 열림)가 미관찰** → a′-15 |
| `설정.dc.html` 55행 «관계인 보기» 행 | — | settings/related-row | settings | ✓ |

hour-picker 폐기 자체는 원본 바이트로 확인된다(`관계인.dc.html`에 BottomSheet·`hasHourSheet` 류 분기 0 · `HOUR_OPTIONS`가 Select `options`로만 소비). 그러나 v2에서 hour-picker case가 덮던 «12지시 옵션 + 시간범위 한눈에 보이는 상태»는 v5에서 Select 메뉴 열림 상태로 옮겨갔고, 그 상태의 case·관찰이 없다 → v2 대비 커버리지 순손실.

## (a′) 독립 열거한 조작 대상 → 관찰 근거 → case

| # | 대상(원본 줄) | 조작 → 드러나는 결과 | trace 관찰 | case | 판정 |
|---|---|---|---|---|---|
| 1 | ListRow (63) | tap → 상세 | detail «tap 김서연 행» | detail | ✓ |
| 2 | «관계인 등록하기» (352–356) | tap → 등록 폼 | register «tap 관계인 등록하기» | register-step1 | ✓ |
| 3 | AppBar chevron-left (466·258–261) | tap → history.back/설정 이동 | 미관찰 | — | 화면 이탈 · 관찰 불요 |
| 4 | 상세 trash-2 (89) | tap → 삭제 확인 | «tap trash-2» | delete-confirm | ✓ |
| 5 | 상세 «닫기» (86) | → 목록 | 미관찰 | (list와 동일 결과) | 허용 |
| 6 | 상세 «수정하기» | → 폼 프리필 | «tap 수정하기» | edit-step1 | ✓ |
| 7 | 삭제 확인 «취소» (103·274) | → **상세 복귀**(openId 유지) | 미관찰 | (detail과 동일 결과) | 허용 · 원본 거동은 소스로만 확정 |
| 8 | 삭제 확인 «삭제하기» (275–279) | → 목록 + Toast «김서연님을 삭제했어요»(neutral) | **미관찰**(trace는 서술) | **없음** | ✗ important |
| 9 | 관계 Select (114) | 열기 → 8옵션 드롭다운 · `menuSurface`(surface-solid · maxHeight 264) | 미관찰 | 없음 | ✗ important |
| 10 | 이름 Input (115) | 포커스·입력 | 미관찰 | — | ✗ nit(DS 소유 시각) |
| 11 | 성별 ChoicePair 남자 (116) | 선택 | 미관찰 | 대칭 | 허용 |
| 12 | step1 «다음» 검증 실패 (425) | → hasErr | «tap 다음(빈 step1)» | form-error | ✓ |
| 13 | 생년월일 Input (123·218·447) | 입력 중 점 자동삽입 | 값 채움만 관찰 | — | nit |
| 14 | 역법 음력 (124–127) | → 윤달 Checkbox 출현 | 이하람 프리필 경유 | step2-lunar | ✓ |
| 15 | **태어난 시 Select (135)** | 열기 → 12지시 + `description` 시간범위 + 종이 surface + `bodyScroll off`(408) | **미관찰**(trace 괄호 서술 «열면 시간범위 description»만) | **없음** | ✗ **blocker** |
| 16 | **«태어난 시간을 몰라요» (136·456)** | 체크 → Select `disabled` · 값 비움 | **미관찰** | 없음 | ✗ **blocker** |
| 17 | 시·도 Select (144) | 열기 → 17 지역 | 미관찰 | 없음 | ✗ important |
| 18 | 시·도 = 도(예 경남) (145·436·438) | → 시·군 enabled + 목록 + 값(진주시) | 미관찰(서울 disabled만) | 없음 | ✗ important(D7 «도의 시·군» 원본 표시 부재 · 상세 이하람도 미관찰) |
| 19 | **«태어난 곳을 못려요» (146·462)** | 체크 → 두 Select disabled + placeholder «태어난 곳은 물지 않을게요»(437·439) | **미관찰** | 없음 | ✗ **blocker** |
| 20 | 메모 Textarea (149) | 입력·카운터 | 24/120 캡처 | step4 | 허용 |
| 21 | «저장하기/등록하기» (281–303) | → 목록 + Toast success | 미관찰 | 없음 | ✗ important |
| 22 | step2~4 «다음» 실패 문구 (384–386) | 인주색 한 줄 3종 | step1만 | 동일 span | 허용(문구는 소스 확정) |
| 23 | 등록 흐름 step4 빈값 | placeholder «지역을 선택해주세요» · «시·도를 먼지 골라주세요» | 미관찰 | 없음 | ✗ important |
| 24 | 설정 «관계인 보기» tap (149) | → 관계인.dc.html | 미관찰 | — | 화면 이탈 · 관찰 불요 |

## (b) 캡처별 대응 판정 (12 PNG 실제 열람 · 390×844 프레임 · lucide 전부 실글리프 · tofu 0)

| 캡처 | 육안 확인 | 판정 |
|---|---|---|
| 01-list | 4행 · 관계가 **도화 accent**로 부제 맨 앞(«배우자 · 1992. 07. 04. · 유시» / «부모 · 음력 1963. 05. 30. · 인시» / «자녀 · 2019. 11. 21. · 시간 모름» / «친구 · 1988. 03. 09. · 술시») · heart/users-round/user-round 아이콘 · «등록한 사람 4명»/«눌러서 수정할 수 있어요» · 안내문 · 떠있는 «관계인 등록하기»(user-round-plus) | ✓ v5 |
| 11-empty | contact-round 32px · «아직 등록한 관계인이 없어요» · 안내 2줄 · 등록 버튼 · 카운트 헤더 없음 | ✓ isEmpty 마크업과 일치(출처는 c-3) |
| 02-detail | «김서연» + trash-2 danger · 관계 배우자 / 성별 여자 / **생년월일 «양력 1992. 07. 04.»(D1 접두)** / 태어난 시 «유시 (17:30–19:29)» / **태어난 곳 «서울»(D7 축약)** / 메모 · 닫기/수정하기 · 등록 버튼 숨김 | ✓ v5 |
| 10-deleteconfirm | danger Dialog · trash-2 원반 · «김서연님을 삭제할까요?» · 설명 문구 · 취소(ghost)/삭제하기(danger) | ✓ |
| 06-registerform-step1 | «관계인 등록» · **ProgressBar 세그먼트 1/4 · 카운트 라벨 없음** · 관계 placeholder · 이름(user-round) · 성별 여자 기본 · 닫기/다음 | ✓ v5 |
| 03-editform-step1 | «관계인 수정» · 배우자/김서연/여자 프리필 | ✓ |
| 04-form-step2-solar | 세그먼트 2 · «1992.07.04»(calendar) · 양력 선택 · 윤달 미표시 · 이전/다음 | ✓ |
| 04b-form-step2-lunar | «1963.05.30» · 음력 선택 · «윤달에 태어났어요» 체크됨 | ✓ |
| 05-form-step3-hour | 세그먼트 3 · **태어난 시 Select «유시» chevron-down(닫힘)** · «태어난 시간을 몰라요» 미체크 · 이전/다음 | ✓ 휴지 상태(열림·체크 미캡처) |
| 09-form-step4 | 세그먼트 4 · 시·도 «서울» · 시·군 disabled «시·도까지만 받아요» · **«태어난 곳을 못려요»(mock 오타 원본 그대로)** 미체크 · 메모 + 24/120 · 이전/저장하기 | ✓ 휴지 상태 |
| 07-formerror | 등록 step1 + 인주색 «관계를 선택해주세요» | ✓ |
| settings | 사주 그룹 4행(생년월일시 변경·만세력·만세력으로 기질 알아보기·**관계인 보기**[contact-round · subtitle «등록한 사람 4명»]) · 탭바 | ✓ (trace 서술은 만세력 행을 빠뜨렸으나 PNG엔 있음 — 서술 nit) |

오캡처(주장 상태 ≠ 실제 그림) = 0.

## (c) 정합 / 갭 / 오캡처

**c-1 sha 일관성 ✓** — 12 case 전부 `entrypoint.sha256 = cf2fe348…`(설정 `b88e995b…`) = source-manifest 해당 row = screen-meta `source_sha256`. 12 source-observation 전부 `archive_sha256 = bddc54ec…`(단일 값 · build-state가 source-manifest 파일 sha로 기록) · `capture.sha256`이 design-input `reference_capture.sha256`과 12/12 일치 · case_id/screen/state/viewport 일치. viewport 12/12 = [390,844] · trace `browser_viewport` 390×844 · `content_crop` 390×844.
**c-2 v1~v4 누출 0 ✓** — `_history/v1~v4/`에 격리(각 design-input 존재) · 루트 captures에 hourpicker 파일 없음 · design-input 12 case · `-impl.png`는 G2 구현 캡처(원본 아님). asset-manifest images [] = 이미지 자산 없음 정상(전부 lucide 글리프 · 캡처로 확인).
**c-3 related/empty 출처 결손 (important)** — 관찰 URL이 `_empty-variant.dc.html`(PEOPLE=[] 변형본 · archive 밖 · 관찰 후 삭제). source-observation의 entrypoint 포인터(`cf2fe348`)와 브라우저가 실제 로드한 문서가 다르며 변형본 바이트가 보존되지 않아 «PEOPLE만 비움»은 검증 불가한 Coordinator 서술이다. 캡처 그림은 isEmpty 분기 마크업과 일치하므로 오캡처는 아니나, 동일 상태는 원본 무변 경로(4명 전부 삭제 흐름 또는 `listState` knob)로 도달 가능하므로 그 경로로 재관찰해야 출처 사슬이 닫힌다.
**c-4 scope↔이탈 정합 · 범위변경 근거 (important)** — `scope.md` §디자인 case 표는 **v2 스냅샷**(13 case · `related/hour-picker` · sha `1262827593a997bd` · `_history/v1`만) · §확정 이탈 form-4-step «N / 4단계» 라벨은 v5(세그먼트만)와 모순 · v5 결정(CH-1 Select · V4-2 몰라요 · D1 접두 · D7 축약 · D3~5 중앙 · DS 값)이 scope.md에 없다. design-input `scope_refs = scope.md#related_persons`가 가리키는 문서가 현재 case 집합과 어긋난다. 범위변경의 **사용자 출처**: 발주서 a8 사본의 «개정 이력»은 작성 1건뿐(개정 9·11·13·14·15 원문 부재 — primary main 소재로 추정) → 이 워크트리에서 확인 가능한 1차 출처는 v5 시안 바이트 자체(사용자 편집물)뿐이고, 승인 기록은 Coordinator 작성 REPORT/GATE-a8-4/build-state로만 간접 확인된다. hour-picker 삭제·ProgressBar 라벨 삭제는 시안 바이트로 뒷받침되므로 임의 축소는 아니다.
**c-5 nit** — `visual-check.md` 제목·§①이 «재동결 v2 · 13 case» 잔존(§②′만 v5). `render-audit.json` texts에 목록 부제 나머지(« · 1992. 07. 04. · 유시»)·«등록한 사람 » 리프 부재(G1 ⓔ 소관 · G0 갭 아님). 발주서 §1-4 «세 뷰포트(390/480/1440)»는 구현 검증 산출 요구이며 원본 case viewport 390 단일은 캔버스 고정 프레임이라 정당.

## 현재 판정: **입력 부족(fail)**

12 case의 캡처는 전부 주장 상태를 실제로 보여주며(오캡처 0) sha 사슬도 일관된다. 그러나 v5가 새로 도입한 상호작용 상태 — **태어난 시 Select 메뉴 열림(12지시+시간범위 · 종이 surface)**, **«태어난 시간을 몰라요» 체크(Select disabled)**, **«태어난 곳을 못려요» 체크(두 Select disabled + placeholder 교체)** — 에 관찰·case가 없고(a′-15·16·19), 삭제/저장 후 **Toast**(scope PD-2 명시)·관계/시·도/시·군 메뉴·도 지역 시·군 enabled·등록 step4 빈값도 미관찰이다(a′-8·9·17·18·21·23). trace의 괄호 서술은 관찰이 아니다. «구현 부품(DS Select) 채택»은 원본 상태 관찰 제외 근거가 아니며, v2 hour-picker case가 덮던 옵션 목록 상태가 대체 없이 사라져 커버리지가 순감했다. 여기에 related/empty 출처 결손(c-3)과 scope.md v2 잔존(c-4)이 더해진다.

## 보완에 필요한 사실

1. 원본 무변 경로로 **추가 관찰 + case**(각 -original.png·trace·source-observation): ⓐ step3 태어난 시 Select **열림**(옵션 12 + description · 메뉴 surface · 스크롤 상자) ⓑ step3 몰라요 **체크**(Select disabled) ⓒ step4 못려요 **체크**(두 Select disabled · placeholder «태어난 곳은 물지 않을게요») ⓓ 삭제 확정 후 **목록+Toast** ⓔ 등록/저장 후 Toast(success) ⓕ 관계 Select 열림(8종) ⓖ step4 도 지역(이하람 경남 → 시·군 enabled «진주시») + 상세 이하람(«음력 윤달 …» · «경남 진주시» D7 표시) ⓗ 등록 흐름 step4 빈값 placeholder. ⓕ~ⓗ는 important, ⓐ~ⓒ는 blocker.
2. related/empty를 동결 entrypoint URL에서 재관찰(4명 삭제 흐름 또는 knob)하거나 변형본을 archive에 보존해 포인터와 실제 로드 문서를 일치시킨다.
3. `scope.md` §디자인 case 표·§확정 이탈을 v5로 갱신(12+추가 case · sha `cf2fe348` · 세그먼트만 · CH-1/V4-2/D1/D7/D3~5/DS 결정 반영)하고, 발주서 개정 9~15 원문 또는 그 사본을 이 워크트리에서 참조 가능하게 둔다(사용자 결정 원문 대조용).
4. 위 변경은 design-input·captures·scope 바이트를 바꾸므로 `--phase prepare` 재실행 → **새 review_digest로 같은 입력범위 재검토**가 필요하다(아래 digest는 이번에 검토한 입력의 식별자이며 통과 기록이 아니다). `visual-check.md` 제목/§① v5 정정은 cosmetic.

reviewed-input: 25b5b07800613c1c7593ca5f53af6235840b3b1300e62433a6a58488c9962719
review-result: fail
