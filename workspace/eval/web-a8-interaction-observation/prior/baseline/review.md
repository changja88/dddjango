# A8 web 관계인 · 재동결 v5 입력범위(coverage) 독립 검토

- 검토자: dddjango-web design-review-web (G0 입력범위 모드 · 읽기 전용 · 파일/명세/코드 수정 0)
- 검토 시각: 2026-09-13 · 도구: Read/Grep/Glob만(Serena·Graphify 미사용 — opt-in 표식 미확인·코드 작업 아님). **SHA-256 재계산 도구 없음** → 해시는 파일 간 문자열 대조로만 확인했고, 실제 바이트 대 해시 일치는 `check_design_evidence --phase prepare`(review_digest 산출) 소관으로 남긴다. Playwright MCP 도구가 이 세션에 노출되지 않아 원본 재렌더는 하지 않았다.
- 독립성: 이전 `coverage-review.md`·`design-review.md`·`design-spec.md`·`visual-check.md`는 열지 않았다. 발주 lane 파일을 범위변경 근거로 grep 하던 중 `REPORT-…-a8.md:237`에 같은 digest의 이전 pass 판정이 한 줄 보였으나 **판단 입력으로 쓰지 않았다**.

## 0. 검토한 입력 버전

| 입력 | 확인 값 |
|---|---|
| `scope.md` | 개정 1 · **§디자인 case 표가 "재동결 v2 · 관계인 sha `1262827593a997bd`" · 13 case(hour-picker 포함)** — v5 미반영(아래 발견 #2) |
| `design-input.json` | version 1 · reference_root `design-ref` · manifests `[source-manifest.json]` · **12 case** · 전 case viewport 390×844 · scope_refs `scope.md#related_persons`/`#preferences` |
| `source-manifest.json` | collection=archive · archive_ready=true · source_ready=false(정상) · files 22 · status ok 22/missing 0 · 관계인 `cf2fe348…`(34,922B) · 설정 `b88e995b…`(11,815B) · external 6(Gowun Batang css/woff2 2·Pretendard woff2·lucide css/woff2) |
| `design-ref/` 실제 인벤토리 | 최상위 3(관계인.dc.html·설정.dc.html·support.js) + `_ds/**` 19 = **22 = manifest 22** · 여분/누락 0 |
| `screen-meta.json` | source_sha256 `cf2fe348…` = manifest 관계인 row = 12 observation entrypoint |
| `captures/` | `*-original.png` **정확히 12장**(08-hourpicker 없음) · trace 12 · source-observation 12 · (그 외 `-impl.png` 17장은 구현측 산출물 — 입력 아님) |
| `render-audit.json` | audit_version 2 · url `127.0.0.1:8731/관계인.dc.html` · viewport 390×844 · texts 15 · pinned 0 · motion kf17/hover3/tr0 · blocked 시트 4(전부 cross-origin) |
| `motion-notes.md` | v5(m1~m9 + 상태행 3 · m5 = BottomSheet→Select) |
| `asset-manifest.json` | images [] · unresolved [] (전부 lucide 폰트 글리프 — 정상) |
| `_history/` | v1~v4 보존 · v2/v3/v4 design-input은 13 case(hour-picker 포함) · v5에서 12로 |
| 범위변경 근거(빌드 폴더 밖) | `REPORT-…-a8.md` §v2→v3 CH-1(사용자가 시안에서 시트→Select) · §v4→v5(관계인.dc.html 1 DIFF `92376312→cf2fe348` · `_ds`/설정/support v4 동일) · `GATE-…-refreeze-v3/v4.md` · `GATE-…-a8-4.md` |

## (a) 상태 → case 커버리지 표 (v5 `관계인.dc.html` sc-if 분기 직접 열거)

| # | 원본 분기(행) | 상태 의미 | design-input case | 판정 |
|---|---|---|---|---|
| 1 | L48 `hasPeople` | 목록(people>0 · 기본 knob=아이콘 원반/등록순/생년월일·시) | `related/list` | 대응 |
| 2 | L58 `g.hasLabel` | 관계별 묶음 그룹 라벨(knob 비기본) | 없음 | **정상** — scope §확정 이탈 `list-default-variant-only` |
| 3 | L74 `isEmpty` | 빈 목록 | `related/empty` | 대응(출처 문제 → (c) #1) |
| 4 | L85 `hasDetail` | 상세 Dialog + trash-2 IconButton | `related/detail` | 대응 |
| 5 | L102 `hasDeleteAsk` | danger 확인 Dialog | `related/delete-confirm` | 대응 |
| 6 | L106 `hasForm` ∧ L112 `isStep1` (draft.id null) | 등록 step1 빈값 | `related/register-step1` | 대응 |
| 7 | L106 ∧ L112 (draft.id 있음) | 수정 step1 프리필 | `related/edit-step1` | 대응 |
| 8 | L120 `isStep2` (solar) | 생년월일·역법 · 윤달 숨김 | `related/form-step2-solar` | 대응 |
| 9 | L120 ∧ L125 `isLunar` | 음력 + 윤달 Checkbox | `related/form-step2-lunar` | 대응 |
| 10 | L132 `isStep3` | 태어난 시 **Select**(L135) + 몰라요 Checkbox(L136) | `related/form-step3` | 대응 |
| 11 | L141 `isStep4` | 시·도/시·군 Select + 못려요(mock 오타) Checkbox + 메모 Textarea(max 120) | `related/form-step4` | 대응 |
| 12 | L153 `hasErr` | 인주색 1줄 오류 | `related/form-error` | 대응 |
| 13 | `설정.dc.html` L55 ListRow `contact-round` «관계인 보기» subtitle «등록한 사람 4명» | 설정 진입 행 | `settings/related-row` | 대응 |
| — | **BottomSheet** | 태어난 시 시트 피커 | (v2~v4 `related/hour-picker`) | **v5 소스 0건**(Grep `BottomSheet`: v5 0 / v2 1) → case 부재 = **정상 · 커버리지 갭 아님**. 근거: 사용자가 시안을 직접 Select로 바꿈(REPORT §v2→v3 CH-1 · 발주서 개정 9), v5 L135 Select 확인 |
| — | L358/L473 `toast`(Toast 컴포넌트 · «{이름}님을 삭제했어요» / «…등록했어요» / «…정보를 저장했어요») | 성공·삭제 후 토스트 | **없음** | **갭** → (c) #3 |
| — | L114/135/144/145 Select `menu-style={{menuSurface}}` 열림 메뉴(옵션 description 시간범위 · surface-solid · maxHeight 264) | 드롭다운 열림 | 없음 | 비-sc-if 컴포넌트 내부 상태 · CH-7(native select) 기록 → nit로만 (c) #6 |

sc-if 분기 기준 전수 대응(12/12). 비-sc-if 시각 상태 중 Toast가 미캡처.

## (b) 캡처별 대응 판정 (12 PNG 전부 Read · 육안)

| case | PNG | v5 상태 육안 확인 | lucide 글리프 | 판정 |
|---|---|---|---|---|
| list | 01-list | 헤더 «등록한 사람 4명»/«눌러서 수정할 수 있어요» · 4행 이름 아래 **관계 어절 도화 accent**(배우자·부모·자녀·친구 — render-audit rgb(185,90,100)) 맨 앞 · 이하람 «음력 1963. 05. 30. · 인시» · 박도윤 «시간 모름» · 하단 안내문 · 떠있는 primary «관계인 등록하기» · 카운트 라벨류 없음 | heart · users-round×2 · user-round · chevron-right×4 · chevron-left · user-round-plus 실아이콘 | 일치 |
| empty | 11-empty | contact-round 32px tertiary · «아직 등록한 관계인이 없어요»(title-2) · 안내문 2줄 · 떠있는 등록 버튼 · 목록 헤더 없음 | contact-round 실아이콘 | 상태 일치 · **출처 불일치** ((c) #1) |
| detail | 02-detail | «김서연» + **trash-2 danger** IconButton · 관계 배우자 / 성별 여자 / 생년월일 **«양력 1992. 07. 04.»**(D1 접두) / 태어난 시 «유시 (17:30–19:29)» / 태어난 곳 **«서울»**(D7 축약 · 접미 없음) / 메모 · 닫기(ghost)/수정하기(primary) · 스크림 뒤 목록(accent 라벨 비침) | trash-2 실아이콘 | 일치 |
| delete-confirm | 10-deleteconfirm | tone=danger Dialog · 상단 trash-2 원형 · «김서연님을 삭제할까요?» · «적어둔 생년월일과 메모가 함께 지워져요. 되돌릴 수 없어요.» · 취소(ghost)/**삭제하기(danger 적색)** | trash-2 실아이콘 | 일치 |
| register-step1 | 06-registerform-step1 | «관계인 등록» · **ProgressBar 4 세그먼트 중 1 채움 · «N/4단계» 카운트 없음** · 관계 Select placeholder «관계를 선택해주세요» · 이름 Input(user-round) placeholder · 성별 ChoicePair 여자 기본 · 닫기/다음 | user-round · chevron-down | 일치 |
| edit-step1 | 03-editform-step1 | «관계인 수정» · 세그먼트 1 · 관계 «배우자» · 이름 «김서연» · 여자 · 닫기/다음 | 동상 | 일치 |
| form-step2-solar | 04-form-step2-solar | 세그먼트 2 · 생년월일 «1992.07.04»(calendar 아이콘 · 압축 표기) · 양력 선택 · 윤달 Checkbox 없음 · 이전/다음 | calendar | 일치 |
| form-step2-lunar | 04b-form-step2-lunar | «1963.05.30» · 음력 선택 · «윤달에 태어났어요» **체크됨** · 이전/다음 | calendar · check | 일치 |
| form-step3 | 05-form-step3-hour | 세그먼트 3 · 태어난 시 **Select «유시» + chevron-down**(시트 아님) · «태어난 시간을 몰라요» 미체크 · 이전/다음 | chevron-down | 일치 |
| form-step4 | 09-form-step4 | 세그먼트 4 · 시·도 «서울» · 시·군 **disabled «시·도까지만 받아요»** · «태어난 곳을 못려요»(mock 오타 원본 그대로) 미체크 · 메모 값 + **«24/120»** 카운터 · 이전/**저장하기** | chevron-down×2 | 일치 |
| form-error | 07-formerror | 등록 step1 빈값 · 성별 아래 **인주색 «관계를 선택해주세요»** 1줄 · 버튼 비활성 아님(닫기/다음) | user-round · chevron-down | 일치 |
| settings/related-row | settings-related-row | 사주 그룹: 생년월일시 변경 / 만세력 / 만세력으로 기질 알아보기 / **관계인 보기**(contact-round · subtitle «등록한 사람 4명» · 그룹 마지막 · chevron) · 결제·계정 그룹 · TabBar 4 | calendar · scroll-text · sparkles · contact-round · coins · receipt · user-round · 탭 4 | 일치 |

tofu 박스 0/12. 12장 모두 같은 390×844 프레임(status bar «9:41» 포함)으로 크롭됨.

## (c) 정합 / 갭 / 오캡처

### 정합 확인(문자열 대조)
- entrypoint sha: design-input 12 case · source-manifest row · screen-meta · 12 observation 전부 관계인 `cf2fe3486ca8…` / 설정 `b88e995b5f77…` — 일관. `b88e995b`는 v2 manifest(L226)와 동일(설정 무변 확인). `1262827593a997bd`는 v2 manifest(L216)의 관계인 sha → **scope.md L90은 v2 값**.
- observation.capture.sha256 = design-input.reference_capture.sha256: **12/12 일치**. case_id·screen·state·viewport: 12/12 일치.
- archive_sha256 `bddc54ec…`: 12 observation 동일값(실제 manifest 바이트와의 일치는 prepare 소관).
- `design-ref/` 인벤토리 22 = manifest 22 · 여분 0. v1~v4 원본 입력 누출 0(`_history/` 격리 · captures/에 08-hourpicker 잔존 0).
- DS 토큰 변경: colors.css `c2dadcd7→bc25c6ba` · glass.css `00e96e21→3486a5e7`는 **v3에서** 바뀌어 v4·v5 동일(motion-notes «_ds byte 무변»은 v4→v5 기준으로 정확). 프롬프트 항목 6은 v2 대비 누적 변경으로 정합.
- 외부 자원: 폰트·lucide는 external(archive 미수집 · 정상) — 캡처에서 Pretendard·lucide 글리프 정상 로드 확인(render-audit fontFamily 전 항목 "Pretendard Variable"). 설정 trace의 Gowun Batang 실패는 `--font-serif`(typography.css L32-42: display-1/2·quote)에만 닿음 → 대상 행(«관계인 보기» · sans)에 영향 없음.

### 발견(심각도순)

**#1 [important · 오캡처(출처)] `related/empty` 관찰이 동결 entrypoint가 아닌 변형본에서 나옴.** `related-empty-trace.json` url = `http://127.0.0.1:8731/_empty-variant.dc.html`, actions «PEOPLE=[] 변형본 … 관찰 후 변형본 삭제». 반면 `related-empty-source-observation.json`은 entrypoint `관계인.dc.html cf2fe348…`을 주장한다. 실제로 로드된 바이트는 archive에 없고 삭제되어 재감사 불가 — 계약(design-evidence.md «independent reviewer checks the original URL/version»)상 이 case는 «원본 URL이 해당 archive 버전을 제공한 사실»을 충족하지 못한다. 캡처 자체는 L74-79 `isEmpty` 마크업과 일치하나, 출처가 동결본이 아니다. 동결 바이트 그대로 도달 가능한 경로가 있다(브라우저 메모리 조작만으로: 4행 각각 상세→삭제하기→삭제하기 → `people=[]` → isEmpty). → **동결 entrypoint URL에서 in-browser 삭제 ×4로 재관찰**하고 trace/observation/capture를 교체해야 한다.

**#2 [important · scope↔design-input 정합] `scope.md`가 v2에 머물러 현재 동결 입력과 모순.** L90 «재동결 v2 … `1262827593a997bd`», L92-106 case 표 13행(`related/hour-picker` · `08-hourpicker-original.png` 포함) ≠ design-input 12 case/`cf2fe348`. §확정 이탈도 v5와 어긋남: PD-1 «시안 6개(…지인)» → v5 시안은 이미 8종(L189); PD-3 «시안의 단일 자유 텍스트 태어난 곳» → v5 시안은 시·도/시·군 Select + 몰라요(L144-146); form-4-step «단계 라벨 텍스트 없음(«N / 4단계»만)» → v5는 카운트 라벨 자체 없음(캡처 06 확인). 유효한 이탈은 PD-4(메모 120→500 · L149 `max-length 120` 확인)·settings-row-no-subtitle·list-default-variant-only·PD-2·4단계 구조뿐. v3~v5 변경 근거는 lane REPORT/GATE에만 있고 design-input이 해시하는 `scope.md`에는 없다. G1 architect가 §확정 이탈을 정본으로 읽으면 v5와 다른 이탈을 설계하게 된다. → scope.md 재정합(case 표 12·sha v5·이탈 행 v5 기준·hour-picker 폐기 근거 명기) 후 **재prepare·재검토** 필요(scope 바이트가 digest에 들어감).

**#3 [important · 커버리지 갭] Toast 상태 캡처 0.** scope §확정 이탈 PD-2 «확인 시 삭제 + 목록 복귀 + toast «{이름}님을 삭제했어요»»와 §필수 동작 «성공 뒤 목록 복귀(시안 흐름)»가 요구하는 가시 상태이며 원본 L358(`ns.Toast` tone neutral/success)·L302·L278에 정의됨. v1~v5 어느 design-input에도 case가 없어 G2에서 구현 토스트를 원본과 대조할 근거가 없다. → 삭제 후(또는 저장 후) 2600ms 안 캡처 case 1건 추가, 또는 «DS Toast 재사용으로 시각 대조 제외»를 scope에 사용자/발주자 결정으로 명기(리뷰어가 대신 면제하지 않음).

**#4 [nit · trace 판형] `browser_viewport` 390×844 vs `canvas` «rendered at 560x1040 viewport, clipped to frame».** 실제 브라우저 뷰포트(560×1040)와 case viewport를 구조 필드에서 동일시했고 `content_crop`에 원점(x,y)이 없다(계약 «Never silently equate them»). 산문으로는 공개돼 있어 nit. → browser_viewport=560×1040 · content_crop={x,y,w:390,h:844}로 기록 권고.

**#5 [nit · render-audit 좌표계] render-audit는 390×844 document-scroll(height 957)로 측정돼 캔버스 40px 패딩·캔버스 캡션 «관계인 · 설정 › 사주»(y=40)·status bar «9:41»이 texts에 섞이고 «관계인 등록하기»가 y=853(>844)에 놓임.** 캡처(프레임 클립)와 좌표계가 다르므로 G1 ⓔ 대조 시 rect를 프레임 상대값으로 환산해야 한다. 목록 상태만 실측(dialog·설정 없음)인 점도 기록.

**#6 [nit · 커버리지 메모] Select 열림 메뉴(관계 8옵션 · 태어난 시 12옵션+시간범위 description · 시·도 17 · 시·군) 캡처 0.** DS 컴포넌트 내부 상태이며 옵션 내용은 동결 소스(L182-210)로 감사 가능. REPORT에 native `<select>` 결정(CH-7 N/A)이 있어 시각 대조 대상이 아니라면 갭 아님 — G1이 커스텀 드롭다운을 택하면 태어난 시 열림 1건 추가 필요.

**#7 [nit] 12 observation `observed_at`이 전부 `2026-09-12T17:17:13Z`로 동일** — 상태 전이가 다른 12 관찰이 같은 초에 기록될 수 없으므로 배치 타임스탬프로 보임. 관찰별 실시각 권고.

**#8 [nit] `scope_refs` 앵커 `scope.md#related_persons`/`#preferences`가 scope.md의 실제 제목과 대응하지 않음** — #2 재정합 시 실제 절 앵커(예 `#디자인-case-표`)로.

**#9 [메모] `captures/`에 구현측 `-impl.png` 17장(480×768·1440×900·smoke 포함)이 원본 캡처와 같은 폴더에 있음** — 입력 아님·v1~v4 입력 누출 아님. 단 v5 visual-evidence가 v5 이후 생성된 impl 캡처만 가리키는지는 G2에서 확인할 사항.

## 현재 판정 · 보완에 필요한 사실

- **판정: 입력 부족(fail).** 12 case는 v5 sc-if 분기를 전수 덮고 11/12 캡처는 동결 entrypoint에서 주장한 상태를 실제로 보여준다. 그러나 (#1) `related/empty`가 archive에 없는 변형본에서 관찰돼 원본 URL/버전 대응이 성립하지 않고, (#2) digest에 포함되는 `scope.md`가 v2 case 표·이탈을 담고 있어 design-input v5와 모순되며, (#3) scope가 요구하는 Toast 가시 상태에 원본 캡처가 없다. hour-picker 부재는 정상이다.
- 보완 사실:
  1. `related/empty`: 동결 `관계인.dc.html` URL에서 브라우저 메모리 조작(삭제 ×4)만으로 빈 목록 도달 → 캡처·trace·observation 재생성(변형 파일 0).
  2. `scope.md`: case 표 12행·관계인 sha `cf2fe348`·hour-picker 폐기 근거(v3 CH-1 사용자 시안 변경)·이탈 행 v5 재기술(PD-1/PD-3는 시안이 답해 «해소», form-4-step 카운트 라벨 문구 삭제, PD-4·설정 subtitle·knob 기본값 유지).
  3. Toast: case 추가(권장) 또는 제외 결정을 scope에 사용자 출처와 함께 기록.
  4. 위 변경 후 `--phase prepare` 재실행 → 새 review_digest로 **같은 입력범위 재검토**. (#4~#8은 재관찰 라운드에 함께 반영 권고 · 단독 반송 사유 아님.)
- 어느 승인으로 gate를 처리하고 다음 phase를 열지는 Coordinator 소유이며, 이 판정은 조건부 승인 권고가 아니다.

reviewed-input: 25b5b07800613c1c7593ca5f53af6235840b3b1300e62433a6a58488c9962719
review-result: fail
