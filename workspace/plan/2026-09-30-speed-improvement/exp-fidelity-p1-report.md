# P1 만세력 G2 첫 제출 시안 충실도 분석

## 1. 결론

- T 35묶음의 **최초로 빠지거나 잘못된 요소↔값 연결**을 주원인으로 세면 **A 명세 손실 34, B 코드 손실 1, C·D·E·F 각 0**이다. A는 코더의 원본 확인 책임을 면제한다는 뜻이 아니다.
- 가설 ①은 이 표본에서 지지된다. 첫 제출에 배치·재질·장식·색의 차이가 남았다. 다만 dddart와의 통제 비교가 없어 두 플러그인의 일반적인 성공률 차이까지 증명하지는 못한다.
- 가설 ②의 **표현력 부족 주장은 기각**한다. D는 0이다. 라이브러리 허용만으로 예방이 보장되는 것은 0묶음이며, 동결 시안 부품·토큰·호출 인자까지 직접 재사용하는 별도 조건에서는 25묶음의 예방 경로가 확인된다.
- 운영자 가설은 일부 지지된다. 숫자 자체의 반복 복사 오류보다 **요소에 붙일 토큰·variant·자식 효과·부모 배치의 연결 손실**이 뚜렷하다. 올바른 선언이 CSS 환경만으로 변한 것을 주원인으로 하는 사례는 확인하지 못했다.
- 처방은 **G0 요소별 정확값·효과 구성·부모 배치 입력 + G2 전 같은 상태의 W8 대조**다. 입력 표는 예 23/부분 12, W8은 이 표본의 T 35/35를 제출 전에 막을 수 있다. 입력 표만으로 이행까지 보장되지는 않는다.

## 2. 분석 기준과 증거 표

### 2.1 범위와 집계 규칙

분석 대상은 `p1`의 G2#1 커밋 `507c12cc3aa42fe742d175b6d76cd9e8481ca213`이다. 체크아웃은 바꾸지 않았다. 현재 명세는 그 커밋의 `design-spec.md`이며, `_history`의 과거 명세나 G2#2·마지막 커밋의 보강 내용을 첫 제출에 소급하지 않았다.

렌더 근거는 [W8 비교 JSON](../design-W8/run/cmp-dv4decl-p1-g2_6311.json)의 `groups[id]`와 `examples`다. `m390-known`, `m390-known-sheet`, `m390-empty`, `m390-info`, `m390-layer`의 다섯 경우를 다룬다. [독립 라벨](../design-W8/judge-p1g2/labels.tsv)의 T 35개가 모두 이 JSON의 id와 연결되고 모두 `blocking=true`임을 확인했다. 전체 JSON은 122묶음이며, 그중 차단 84묶음에 T 35·데이터 D 35·짝짓기 F 8·무관 H 6의 라벨이 있다. **독립 라벨의 D/F와 이 보고서 원인 분류의 D/F는 서로 다른 뜻**이다.

비교 JSON과 라벨·요약은 `frozen-v4-run/`의 동명 자료와 바이트가 같다. 비교 JSON SHA-256은 `ba23e8f5f106a8ac799015df5589328849a0fade1376e46f41ebca958bc667c6`이다. 판정자 요약의 첫 줄은 `dv3decl`이라고 되어 있지만, 여기서는 이름으로 버전을 추정하지 않고 지시된 v4 JSON과 id 전수를 직접 연결했다.

주원인은 다음과 같이 정했다.

- **A**: 현행 명세에 해당 요소·상태에 적용할 값이나 구조가 없거나 틀렸다. 단순 원본 파일 링크, “시안대로”, 모든 토큰의 후보 채택은 요소별 연결의 대체로 세지 않았다. 이는 지시서의 “시안에 있는데 명세가 빠뜨렸다”를 적용한 기준이다.
- **B**: 현행 명세에 해당 요소의 정확값이 있고 구현이 그것과 다르다. 12신살 일반 칸의 색이 명확한 사례다.
- **C**: 올바른 요소에 올바른 값이 선언되어 있는데 환경·상속·덮어쓰기 때문에 최종값만 달라진 경우에 한한다. 잘못된 공용 기본값을 선택한 경우를 자동으로 C로 옮기지 않았다.
- **D/E/F**: 각각 기술상 표현 불가, 정본을 결정할 수 없는 시안 모호성, 규칙을 준수하면 잘못될 수밖에 없는 경우다. “직수입하면 편하다”, “부품 이름이 같다”, “없는 토큰이라 대체했다”는 이유만으로 D/F를 부여하지 않았다.

따라서 A 34는 **최초 정보 손실 위치의 집계**다. architect만이 실제 원인이라는 인과 실험 결과는 아니다. 당시 규칙은 코더에게도 원본 부품 정의를 직접 읽도록 요구한다. 그 의무를 지켰다면 A에서 빠진 내용을 구현 단계에서 회복할 수 있었다. 원본 참조만으로 명세가 완전하다고 보는 다른 집계 기준을 쓰면 A/B 분포가 달라진다.

표는 35묶음을 19개 판정 단위로 모았다. 이 19개를 독립 수리 19건으로 해석하면 안 된다. R6은 R1–R3에서 파생되고, R9–R11은 같은 패널 재질 수정에 함께 들어가며, R4의 두 id는 같은 연필 아이콘이 missing/extra로 갈린 것이다. 집계의 분모는 언제나 **묶음 35개**다.

**예방 판정**: (가)의 ‘예’는 해당 측정값을 요소·상태와 연결하여 준수한다면 필요한 시각 사실이 입력에 생긴다는 뜻이다. ‘부분’은 부모·형제 구조나 상태별 배치가 더 필요하거나, 이미 정확값을 받았는데도 어긴 경우다. (나)의 ‘예’는 차이를 생성하지 않는다는 뜻이 아니라, 발견된 차이를 고치기 전 **G2 제출을 차단**할 수 있다는 뜻이다. 두 장치 모두 지시 불이행까지 자동으로 없앤다는 주장은 하지 않는다.

### 2.2 파일 약칭

아래 약칭 뒤의 숫자는 실제 파일의 줄 번호다. `X:10–20`은 그 파일의 해당 구간이며, 명세는 절도 함께 적었다. `_ds`의 독립 JSX 원본 대신 동결 번들에 남은 `components/.../*.jsx` 정의와 실제 번들 줄 번호를 인용한다. 표에서 짧게 적은 `chart_*.html`은 모두 `p1/web/chart/chart/section/` 아래 파일이며, `설정.dc.html`은 같은 빌드의 `design-ref/` 아래 파일이다.

| 약칭 | 실제 파일 |
|---|---|
| S | [design-spec.md](p1/.dddjango-web/20260908-1534-web-chart/design-spec.md) |
| M | [design-ref/만세력.dc.html](p1/.dddjango-web/20260908-1534-web-chart/design-ref/만세력.dc.html) |
| V | [design-ref/만세력 화면.dc.html](<p1/.dddjango-web/20260908-1534-web-chart/design-ref/만세력 화면.dc.html>) |
| DS | [design-ref/_ds/chunmong-design-system-9ad494f0-e78e-410b-b52f-e515367f30e9/_ds_bundle.js](p1/.dddjango-web/20260908-1534-web-chart/design-ref/_ds/chunmong-design-system-9ad494f0-e78e-410b-b52f-e515367f30e9/_ds_bundle.js) |
| DC / DG / DR | 위 `_ds`의 [tokens/colors.css](p1/.dddjango-web/20260908-1534-web-chart/design-ref/_ds/chunmong-design-system-9ad494f0-e78e-410b-b52f-e515367f30e9/tokens/colors.css) / [tokens/glass.css](p1/.dddjango-web/20260908-1534-web-chart/design-ref/_ds/chunmong-design-system-9ad494f0-e78e-410b-b52f-e515367f30e9/tokens/glass.css) / [tokens/radius.css](p1/.dddjango-web/20260908-1534-web-chart/design-ref/_ds/chunmong-design-system-9ad494f0-e78e-410b-b52f-e515367f30e9/tokens/radius.css) |
| C / U / T | [web/static/css/chart.css](p1/web/static/css/chart.css) / [web/static/css/components.css](p1/web/static/css/components.css) / [web/design_system/foundation/tokens.css](p1/web/design_system/foundation/tokens.css) |
| B / E / P | [chart_build_prompt.html](p1/web/chart/chart/section/chart_build_prompt.html) / [chart_empty.html](p1/web/chart/chart/section/chart_empty.html) / [chart_screen.html](p1/web/chart/chart/section/chart_screen.html) |
| BG / SET | [chart_background.html](p1/web/chart/chart/section/chart_background.html) / [web/static/css/settings.css](p1/web/static/css/settings.css) |
| H0 / H1 | [_history/pre-lunar-20260928/design-spec.md](p1/.dddjango-web/20260908-1534-web-chart/_history/pre-lunar-20260928/design-spec.md) / [_history/pre-6-3-11-20260929/design-spec.md](p1/.dddjango-web/20260908-1534-web-chart/_history/pre-6-3-11-20260929/design-spec.md) |

렌더 값은 아래에서 모두 **시안 → 구현** 순서로 적는다. 그룹 대표값의 반올림 때문에 정밀한 수치가 필요한 곳은 JSON의 `examples` 값을 사용했다.

### 2.3 배치·크기

| 단위·묶음 id | 요약 | 시안 근거 | 명세 근거 | 코드 근거 | 렌더 시안 → 구현 | 주 판정·부 원인 | (가) 입력 표 | (나) W8 |
|---|---|---|---|---|---|---|---|---|
| R1 · `6203429197`, `5ad919a4d3` | 원국 없음 두 상태의 본문 세로 배치 | M:51,114: 본문 `flex:1; min-height:0; overflow-y:auto; display:flex; flex-direction:column; justify-content:center; gap:20px; padding:4px 24px 24px` | **정확한 중앙 정렬·본문 여유 공간 계약 없음**. §5 S:82는 프레임 분리, §8 S:125는 주로 생성된 chart의 스크롤을 서술 | C:87–108: 본문 `gap:32px; padding:8px 24px 52px`, 정보 있음은 `padding-bottom`·`margin-block:auto`만 추가. C:252–256 빈 상태에 `justify-content:center` 없음; B:1의 section에는 자식 세로 flex/gap 없음 | empty: placeholder y **121.11 → 74**, 앞 간격 **63.11 → 16**. info: y **61.86 → 73.36**, 앞 간격 **3.86 → 15.36** | **A**. 부: 부모와 자식의 flex·여유 공간 관계를 보존하지 않음 | **부분** — 한 viewport의 틈은 드러나지만 가운데 배치의 부모 높이·flex 계약이 더 필요 | **예** — 두 id 모두 gap 차이로 차단 |
| R2 · `1dab32af8a` | 정보 설명과 요약판 사이 20px 간격 누락 | M:114의 세로 flex `gap:20px`; 설명 블록 M:130–133과 판 M:135가 형제 | **없음**. §5 S:82의 정보 있음 구성 설명에는 간격·형제 배치가 없음 | B:11–15는 설명 다음 판을 배치하나 C:107–109 `.chart-build`는 margin만 있음. 자식 사이 flex/gap 선언 **없음** | 문단 다음 판의 측정 간격 **23.26 → 3.26px**, 판 y **486.33 → 457.83** | **A**. 부: 본문 조립에서 형제 gap 소실 | **부분** — 차이 20px는 입력되지만 이를 어느 부모의 gap으로 둘지 연결 필요 | **예** — `region.gap-top` 차단 |
| R3 · `cfb108b795`, `04bdaa7db9`, `295f65fd21`, `f8af45d200` | 정보 요약판 padding·행 구성이 바뀜 | M:135 `padding:4px 14px`; M:137–139 **세 행 모두 divider=true**; M:140 편집 행 `padding:6px 0 4px`; DS:3132–3137 ListRow 기본 높이·padding·divider | §2 S:18·§5 S:82는 **앞 두 divider**라고 적어 원본과 다름. 판 padding·편집 행 padding은 **없음** | B:15–23에 요약판·편집 행 클래스는 있으나 해당 padding 규칙 없음. U:443 `padding:var(--card-pad)`, T:156 `20px`; B:19 셋째 divider 없음. U:188 ghost 높이 36px | 판 높이 **261.83 → 282.83**; 행 왼쪽 inset **15 → 21**, 첫 행 위 inset **5 → 21**, 행 폭 **312 → 300px** | **A**. 부: 기존 판 기본 padding 적용. 높이 차이는 padding뿐 아니라 편집 행 padding·셋째 divider도 함께 관여 | **부분** — 크기 오차는 모두 보이나 자식·divider 구성까지 값과 연결해야 함 | **예** — 높이·inset·폭 네 id 차단 |
| R4 · `0f69f74897`, `d66b8419b7` | 정보 고치기가 왼쪽으로 가고 연필이 커짐 | M:140 `display:flex; justify-content:flex-end`; M:141 Button ghost/sm; DS:475–482 sm icon **15px** | **오른쪽 정렬·15px 없음**. §5 S:82는 “정보 고치기” 기능만 적음 | B:20–21 편집 행과 ghost/sm; 편집 행 정렬 CSS **없음**. U:190 `font-size:var(--icon-size-sm)`, T:160 **16px** | 같은 연필이 시안 **x=254.57, y=713.66, 15×15** → 구현 **x=60.94, y=693.66, 16×16**로 이동. 비교기는 missing/extra 두 묶음으로 분리 | **A**. 부: generic 아이콘 토큰을 sm Button 내부 치수로 사용 | **부분** — 15px는 확정되나 오른쪽 정렬의 부모 규칙도 필요 | **예** — missing/extra를 같은 대상의 위치·크기 차이로 확인 가능 |
| R5 · `fd0d10a6cf` | empty CTA가 본문을 따라 올라감 | M:89–93: 스크롤 본문 **밖** footer, `flex:0 0 auto; padding:0 24px 20px`; Button lg 높이 56 | **empty CTA의 footer 분리·하단 배치 계약 없음**. §5 S:82의 “아래 CTA”만 있음 | E:43–46 CTA가 `.chart-empty` section **안**. P:24–30 footer는 `input_complete`에만 존재 | CTA y **768 → 661.77**, 앞 판 뒤 간격 **79.12 → 20px**; 높이는 둘 다 56px | **A**. 부: empty와 info 상태의 footer 구조 불일치 | **부분** — 같은 화면의 목표 위치는 주지만 footer/본문 분리를 대신하지 못함 | **예** — `region.gap-top` 차단 |
| R6 · `b26ec0f9c6` | info CTA 앞 간격의 파생 차이 | M:114,135–149 본문·요약판·footer 결합 | 요약판과 본문 배치의 정확값 **없음**(R1–R3); “아래 CTA”는 S:82 | P:24–29와 C:111–113의 하단 footer 자체는 존재. 앞 판의 위치·크기가 다름(B:15–24, U:443) | CTA는 양쪽 **y=768**로 같음. 앞 판 뒤 간격만 **19.84 → 27.34px** | **A(파생)**. 버튼 고정 실패로 판정하지 않음; R1–R3의 선행 배치에서 파생 | **부분** — CTA에 margin을 더하는 식의 오수리를 피하려면 앞 판과 함께 해석해야 함 | **예** — 차이는 차단하되 선행 판 배치와 묶어 수리 |
| R7 · `c5575094c2`, `27e4db6647` | 원국 세우기 아이콘과 글자 gap 누락 | M:149 Button primary/lg; DS:492–498 `gap:10`, icon 20; DS:542 `gap:s.gap` | **lg 버튼 내부 10px gap 없음**. §5 S:82의 Button 정체와 CTA만 있음 | P:26–27 아이콘+라벨을 직접 조립. U:87–100 flex 중앙 정렬에 gap **없음**. C:349–350의 10px는 `.chart-empty__cta`에만 적용되고 `.chart-build__submit`에는 없음 | 아이콘 왼쪽 inset **120 → 125px**; 글자 앞 gap **9.92 → -0.08px**(그룹 정규화값 10 → 0) | **A**. 부: 같은 lg Button을 상태별로 다르게 조립 | **예** — 해당 버튼의 10px 내부 gap을 직접 입력 | **예** — icon inset와 text gap 모두 차단 |

### 2.4 배경·패널 재질

| 단위·묶음 id | 요약 | 시안 근거 | 명세 근거 | 코드 근거 | 렌더 시안 → 구현 | 주 판정·부 원인 | (가) 입력 표 | (나) W8 |
|---|---|---|---|---|---|---|---|---|
| R8 · `b0ac19d022`, `162e299e54`, `cba69f7979`, `c8af1b03cd`, `9f36a2ee06`, `6274ba7ce0`, `bf0957d01e` | chart 직접 화면과 설정 층에서 aura 네 번짐 누락 | M:46,109 / V:35 AppFrame. DS:2213 **aura=true**; DS:2156–2175 네 blob의 위치·크기, DS:2276–2295 span/radial-gradient. DC:119–122 blob 색 | **aura의 존재·네 자식·프레임별 소유 명세 없음**. §5 S:88은 AppFrame 동일 정체 재현, §9 S:143은 blob 토큰을 후보 채택할 뿐. §8 S:125에도 aura 없음 | BG:5 빈 div 하나; C:5–8 평평한 `linear-gradient(180deg,paper-300,surface-sunken)`. P:2–52 chart root에도 blob 자식 없음. SET:687–689 chart 층도 종이 gradient를 bg-app 위에 얹음. 설정 쪽 blob 토큰은 T:344–347,406–421에 이미 존재 | 단독: mist **300×300**, blossom/rose **320×320**, gold **340×340** region → 없음. gradient 색은 각각 **#6c829875 / #df909547 / #98444e24 / #d3b87f66 → 없음**. 층 4개는 같은 gradient **A ; A → A**로 집계(상세 주의 아래) | **A**. 부: 올바른 `--bg-app` 위 종이 gradient 덮음은 CSS 합성 문제도 동반하지만, 이 7개 id의 핵심은 aura 자식 부재 | **예** — 프레임별 장식 요소 목록과 각 배경·크기가 입력에 있으면 누락을 드러냄. 뒤 설정과 앞 chart의 소유 구분이 전제 | **예** — 단독 3개와 층 4개 차단. 층의 중복 병합은 원본 소스로 판독 필요 |
| R9 · `6da7ced604`, `9962fa1a2d` | 패널 윤광 자식 누락 | V:83,145,183,228,260,316,359,408의 GlassPanel; M:72,135의 solid도 기본 sheen=true. DS:184,204–212 윤광 span; DG:66 `--glass-sheen` 148deg, 흰색 alpha .78/.34/.06/0/0/.22 | **어느 패널에 sheen 자식을 붙일지 없음**. §5 S:80–88은 부품 이름·구조 보존 일반문, §9 S:143은 토큰 후보 채택. H1:19,75,78은 이전 범위에서 윤광을 명시적으로 제외했던 흔적 | `chart_pillars.html:9–10`, `chart_elements.html:14–15`, `chart_twelve_shinsal.html:12–13`, `chart_relations.html:15–16`, `chart_spirits.html:15–16`, `chart_void_nayin.html:12–13`, `chart_major_fortunes.html:6–7`, `chart_annual_fortunes.html:6–7`, B:15–16, E:26–27 모두 루트+content만 직접 조립. 윤광 자식 **없음**. T:33 토큰 및 U:459–465 규칙은 존재 | **linear-gradient(148deg, #ffffffc7 0%, #ffffff57 14%, #ffffff0f 32%, #ffffff00 54%, #ffffff00 82%, #ffffff38 100%) → none** | **A**. 부: 공용 부품의 자식 효과를 뺀 직접 마크업과 과거 제외의 잔존 | **예** — 윤광을 독립 층으로 수록하면 토큰 존재와 실제 사용을 구별 | **예** — 두 id의 `paint.bgi` 차단 |
| R10 · `1bc3d22eb5`, `aa3231f5d4` | 패널 반경이 8px 커짐 | DS:181,197 GlassPanel 기본 `radius-card`; DR:7 **26px**. V:83 등 호출은 radius 재지정 없음; M:72,135도 동일 | **패널→radius-card 연결 없음**. §9 S:146에서 radius-card와 radius-panel을 모두 후보 채택 | U:445 **radius-panel** 선택; T:183 card=26, T:184 panel=34. 토큰 두 값 자체는 정확 | 네 모서리 모두 **26 → 34px** | **A**. 부: 같은 “panel” 이름을 근거로 다른 의미 토큰의 기본값 재사용 | **예** — 패널 요소의 26px를 확정하므로 이름 추론 불필요 | **예** — 두 `paint.radius` id 차단 |
| R11 · `183ff52438`, `0b7cbaade6` | 패널 외부 그림자 단계가 무거워짐 | V:83 등 `elevation=2`; DS:171,183,201 shadow-2 + glass-edge. DG:77 shadow-2 | **대상 패널의 elevation=2·그림자 조합 없음**. §5 S:80–81 strong만 적고 §9 S:147은 shadow-2와 shadow-3 모두 채택 | U:447 **glass-edge + shadow-3**. T:191 shadow-2, T:192 shadow-3 정의는 각각 정확 | 외부 그림자 **0 2px 6px #1f1c1812 + 0 10px 28px #1f1c181a → 0 4px 12px #1f1c1814 + 0 22px 50px #1f1c1824**. 공통 여섯 inset은 동일 | **A**. 부: 공용 판의 elevation=3 재질을 검증 없이 사용 | **예** — 전체 shadow 목록·조합을 입력하면 단계 선택 소실을 막음 | **예** — 두 `paint.sh` id 차단 |
| R14 · `36b066cf10`, `547e1ca2a1` | empty/info의 solid 판을 strong 유리로 바꿈 | M:72,135 `tone=solid`; DS:162–165 surface-solid와 `1px solid border-hairline` | **현행 solid 지정 없음**(§5 S:82). H0 §9.1:291에는 **solid→glass-panel--strong 재사용**이라는 잘못된 이전 매핑이 실제로 있음 | E:4,26 / B:15 strong 선택; C:313에 옛 매핑 주석. U:444,454와 T:40,243으로 52% 틴트·72% 흰 테두리. T:79의 정확한 solid 색은 존재 | 배경 **#fffdf9ff → #fffdf985**; 4면 테두리 **1px solid #1f1c181a → 1px solid #ffffffb8** | **A**. 부: 과거 명세의 명시적 잘못된 variant 매핑을 현재 화면으로 이월 | **예** — 불투명도와 테두리를 포함한 정확값이 variant 오인을 막음 | **예** — bg/border 두 id 차단 |

### 2.5 텍스트·버튼·배지

| 단위·묶음 id | 요약 | 시안 근거 | 명세 근거 | 코드 근거 | 렌더 시안 → 구현 | 주 판정·부 원인 | (가) 입력 표 | (나) W8 |
|---|---|---|---|---|---|---|---|---|
| R12 · `4f44105e1d` | 12신살의 기준 아닌 칸이 너무 옅음 | V:949–951 일반 칸 `ink-700`; DC:13 **#423D36** | **맞게 있음**. §9 S:228–229 년살, 304–305 월살, 311–312 육해살을 모두 **rgb(66,61,54)**로 채택 | `chart_twelve_shinsal.html:27`의 일반 셀, C:708–716 기본 **text-secondary**, 기준 칸만 blossom-700; T:113 **#5C554C**. 필요한 ink-700은 T:53에 있음 | **#423d36ff → #5c554cff**, 18개 member | **B**. 부: 정확한 실측 명세와 실제 CSS 매핑 대조 누락 | **부분** — 이미 정확값이 명세에 있었으므로 같은 입력을 추가하는 것만으로 이행을 보장 못함 | **예** — 같은 문구의 `text.c` 차단 |
| R13 · `95218b652c` | 공망 아닌 점의 색이 너무 진함 | V:974–975 `voidLabel='·'`, `voidColor=ink-300`; DC:14 **#C4BCB0** | **점 요소의 색 명세 없음**. §9 S:143 ink-300은 후보일 뿐. S:209–211은 “공망” 라벨·제목·설명이며 점의 행이 아님. texts 200개 표에 해당 점 행 없음 | `chart_void_nayin.html:23`; C:1128–1136 기본 **text-tertiary**, 공망만 text-gold. T:114 **#A29A8E**; 올바른 ink-300은 T:49에 있음 | **#c4bcb0ff → #a29a8eff**, 12개 member | **A**. 부: 의미가 비슷한 tertiary를 선택, 요소별 색 확인 누락 | **예** — 점도 별도 텍스트 요소로 수록하면 필요한 색이 입력에 생김 | **예** — 같은 `·`의 `text.c` 차단 |
| R15 · `28e78bc109` | empty CTA 달력 아이콘 2px 작음 | M:92 Button lg/calendar; DS:492–498 lg icon **20px** | **lg 내부 아이콘 20px 없음**. §5 S:82 Button/CTA 일반 연결만 있음 | E:43–45 + C:353–355에서 **18px**를 직접 지정 | **20 → 18px** | **A**. 부: md급 치수를 lg 버튼에 선택 | **예** — 아이콘 요소의 20px 직접 입력 | **예** — `icon.size` 차단 |
| R16 · `c5ddcef104` | primary 버튼 밝은 테두리 누락 | DS:361–367 primary `on-fill-border`; DC:111–112 **1px solid rgba(255,255,255,.26)** | **primary→테두리 연결 없음**. §9 S:143 on-fill-border는 후보 채택 | U:93 **border:none**. 일반 on-fill-border 토큰은 없음; 같은 정확값의 settings 전용 토큰은 T:355에만 있음 | 4면 **1px solid #ffffff42 → none** | **A**. 부: 근사로 만들어진 기존 PrimaryButton 재질을 그대로 재사용(U:83–85) | **예** — 버튼 4면의 실제 border 입력 | **예** — `paint.bd` 차단 |
| R17 · `8471befd13` | primary 버튼 안쪽 윗빛 누락 | DS:367 `shadow-accent, on-fill-highlight`; DC:113 **inset 0 1px 0 rgba(255,255,255,.22)** | **primary의 두 그림자 합성 연결 없음**. §9 S:143,147은 두 토큰을 각각 후보 채택 | U:97 **shadow-accent만**. 일반 on-fill-highlight 토큰은 없음; 같은 settings 전용 값은 T:356 | **0 6px 18px #b95a644c + inset 0 1px 0 #ffffff38 → 첫 외부 그림자만** | **A**. 부: 하나의 shadow 토큰 사용을 전체 효과 재현으로 간주 | **예** — 다중 shadow 목록을 그대로 입력 | **예** — `paint.sh` 차단 |
| R18 · `5dd8fd3006` | jade soft 배지가 회색 바탕으로 바뀜 | V:197,279 Badge soft; DS:270–273 jade soft=`success-soft`; DC:82 jade-500 **14%** | **Badge jade→success-soft 연결 없음**. §9 S:143 후보에는 success-soft가 있으나 S:137 “이번 범위의 누락”은 text-info/z-toast/z-modal 세 개만 지목. H0:294–300은 신규 0·나머지 미사용이라는 과거 처분 | C:616–620에 **“성공 soft 배경 토큰 부재 → surface-sunken, 신규 토큰 0”** 주석과 실제 대체가 함께 남음. T:80 sunken **rgba(31,28,24,.045)**; 일반 success-soft 없음 | **#4f8a6c24 → #1f1c180b**, 18개 member | **A**. 부: 토큰 부재를 정확값 신규 등록 대신 근접 대체 사유로 사용. 당시 규칙을 준수한 결과는 아니므로 F 아님 | **예** — 요소의 녹색 14%를 입력하면 회색 4.5% 대체를 허용할 근거가 없어짐 | **예** — `paint.bg` 차단 |
| R19 · `784f9bafb6` | neutral soft 배지 alpha가 낮음 | V:58–59 및 동적 neutral Badge; DS:282–285 soft=`surface-muted`; DC:92 ink-900 **6%** | **neutral Badge→surface-muted 연결 없음**. §9 S:143 후보 채택만 있고 H0:294–300의 신규 0 처분을 해소하는 실제 요소 매핑 없음 | C:219–237 **“surface-muted 부재 → surface-sunken”** 주석과 대체; T:80 **4.5%**. 일반 surface-muted 없음; 정확한 settings 전용 6% 값은 T:359에 있음 | **#1f1c180f → #1f1c180b**, 32개 member(차단 30, blur-covered 비차단 2) | **A**. 부: 투명도를 근접값으로 치환. F 아님 | **예** — 같은 먹색이어도 alpha까지 입력하면 6%와 4.5%를 구별 | **예** — 가리지 않은 member들이 차단; 흐림 뒤 2개만으로 차단한 것은 아님 |

### 2.6 표를 읽을 때 필요한 보충

**R3의 높이 21px는 padding 하나로 전부 설명되지 않는다.** 원본 판은 상하 padding 8px, 세 ListRow, 편집 버튼 36px, 편집 행 padding 10px, 판 테두리 2px로 구성된다. 구현은 판 상하 padding이 40px로 32px 늘고, 편집 행 padding 10px와 셋째 divider 1px가 빠져 순증가가 **32−10−1=21px**다. 이 구성이 측정 높이 261.83→282.83과 맞는다. “카드 높이를 262px로 고정”하는 처방보다 요소 관계를 복원하는 처방이 근거에 부합한다.

**R8의 층 네 묶음은 중복 집계 신호다.** 시안의 설정 blob과 앞 chart blob이 같은 위치라 비교기가 `A ; A`로 합쳤고, 구현에는 뒤 설정 blob 하나만 있다. 이를 “chart gradient 문자열에 같은 gradient를 두 번 써야 한다”로 읽으면 잘못이다. DS의 AppFrame 기본 aura와 `설정.dc.html:141–146`의 chart 하위 화면, 구현 P의 자식 부재를 교차 확인해 **앞 chart 배경의 누락**으로 판정했다. 이 네 묶음의 확신은 중간이며 독립 결함 네 개가 아니다.

**정확한 토큰이 있어도 잘못 붙일 수 있다.** T:183·184에는 26px와 34px가, T:191·192에는 shadow-2와 shadow-3가 모두 정확하게 있다. T:33의 윤광도 정확하다. 손실은 이 값들의 숫자를 tokens.css에 복사하면서 바꾼 것이 아니라 **어느 요소·자식에 어떤 조합을 써야 하는지**에서 발생했다. 또 공용 `glass_panel.html:12`에는 윤광 span이 있으나 chart는 그 템플릿을 호출하지 않고 마크업 일부만 펼쳤다. U:465의 기존 윤광 opacity .55도 원본 기본 1과 다르므로, 그 클래스에 span만 추가하는 수리만으로 완전 일치를 주장할 수 없다. 이 opacity는 현재 T 묶음 밖의 별도 신규 발견으로 집계하지 않았다.

## 3. 집계와 가설 판정

### 3.1 원인·예방 집계

| 주원인 | A 명세 손실 | B 코드 손실 | C CSS 환경 | D 표현 불가 | E 시안 해석 | F 규칙 강제 | 합계 |
|---|---:|---:|---:|---:|---:|---:|---:|
| 묶음 수 | 34 | 1 | 0 | 0 | 0 | 0 | 35 |

| 예방 장치 | 예 | 부분 | 아니오 | 합계 |
|---|---:|---:|---:|---:|
| (가) 입력 정확값 표 | 23 | 12 | 0 | 35 |
| (나) G2 전 W8 대조 | 35 | 0 | 0 | 35 |

(가) ‘부분’ 12묶음은 R1–R6의 배치 관련 11묶음과, 이미 정확한 명세를 어긴 R12 1묶음이다. 나머지 23묶음은 ‘예’다. 모든 차이가 CSS와 관계있다는 이유로 C에 넣지 않았으며, A의 부수적인 코드 확인 실패도 B에 중복 가산하지 않았다. 원인 표의 숫자는 코드의 잘못된 CSS 선언 수나 작업시간 비중을 뜻하지 않는다.

**W8의 35/35는 이 자료에서의 포착률이지, 새로운 화면의 정확도 100%가 아니다.** 차단 84묶음 중 T는 35개로 약 41.7%다. 데이터·짝짓기·무관 판정까지 무조건 수정하게 하면 과잉 반송이 된다. 따라서 같은 데이터·같은 상태·앱 내부 프레임을 맞추고, T/D/F/H 판독 또는 그에 상응하는 원본 근거 확인을 남겨야 한다. 이 보고서의 차단 판정은 이미 확인된 T 35개에 대한 것이다.

### 3.2 라이브러리 가설: 표현 가능성과 재사용 효과를 분리

**D 표현 불가 = 0/35.** 실제 시안 코드 자체가 필요한 표현을 표준 DOM과 CSS로 만든다. 가운데 배치와 footer는 flex, 판 재질은 background/border/border-radius/box-shadow와 자식 span, aura는 absolute span과 radial-gradient, 아이콘·배지는 font-size/gap/color다. DS의 React 코드는 이 경우 DOM·스타일을 생성하는 역할이다. 이 35개 정적 차이를 표현하는 데 React 런타임이나 Tailwind가 필수인 항목은 없다. 새로운 브라우저 실행 없이 동결 소스의 표현 구성을 확인한 판정이다.

“라이브러리가 있었으면 몇 건을 막았는가”는 아래와 같이 조건을 고정해야 셀 수 있다.

| 반사실 조건 | 완전 예방 경로 | 부분 | 예방 근거 없음 | 의미 |
|---|---:|---:|---:|---|
| React 또는 Tailwind 사용을 **허용·설치만** 하고 현재 명세·조립·값 선택을 유지 | **0** | 별도 정량화하지 않음 | 35 | 라이브러리는 26px, solid, gap 10px를 자동으로 결정하지 않는다. 미실험 효과를 확정 건수로 만들지 않음 |
| 동결 DS의 **AppFrame·GlassPanel·Button·Badge·ListRow 구현과 토큰 CSS를 그대로 사용**, 화면이 원본에서 넘긴 tone/size/elevation/padding/divider 인자도 보존. 교체한 부품에 기존의 다른 재질 CSS를 다시 씌우지 않음. 부품 밖 화면 배치와 텍스트 색 결정은 현행대로 둠 | **25** | **4** | **6** | 아래 id별 정적 예방 경로. 실험으로 측정한 성공률이 아니라 조건부 분석 |
| 위 재사용에 더해 화면의 부모 flex·footer·편집 행·텍스트 색까지 원본대로 보존 | 35개 모두의 수정 근거 존재 | — | — | 이는 라이브러리만의 효과가 아니라 **시안 표현 전체를 보존**한다는 조건. 일반 HTML/CSS로도 같은 조건을 만족할 수 있음 |

조건부 **완전 예방 25묶음**의 내역은 다음과 같다.

| 직접 재사용하는 내용 | 해당 묶음 | 수 |
|---|---|---:|
| AppFrame의 aura·자식·기본 바탕을 각 chart 프레임에 보존 | R8의 7개 | 7 |
| GlassPanel의 sheen·radius-card·elevation=2·solid 재질 | R9·R10·R11·R14의 각 2개 | 8 |
| GlassPanel 원본 padding=4px 14px와 ListRow를 보존 | `04bdaa7db9`, `295f65fd21`, `f8af45d200` | 3 |
| Button lg의 gap·icon·border·highlight | R7의 2개, R15·R16·R17의 각 1개 | 5 |
| Badge soft의 jade·neutral 토큰 | R18·R19 | 2 |
| 합계 | 중복 id 없음 | **25** |

**부분 4묶음**은 정보 판 높이 `cfb108b795`(부품 밖 편집 행 padding이 여전히 필요), 연필 missing/extra `0f69f74897`, `d66b8419b7`(아이콘은 맞아도 부모의 오른쪽 정렬은 별개), 파생 간격 `b26ec0f9c6`(판·본문·footer 관계를 함께 고쳐야 함)이다. **예방 근거 없음 6묶음**은 R1 두 개, R2·R5·R12·R13 각 한 개다. 이들은 화면이 정한 배치 또는 텍스트 색이라 DS 부품만 가져오는 것으로는 복원되지 않는다.

따라서 **부품 직접 재사용은 전사할 표면을 줄여 유용할 수 있다.** 그러나 그것을 “HTML/CSS/htmx로 그릴 수 없어서 실패했다”의 근거로 사용할 수는 없다. Tailwind의 유틸리티나 임의값 문법을 허용해도 원본 수치·효과·부모 관계를 선택하는 일은 남는다.

### 3.3 F 규칙 강제 여부와 버전 확인

규칙 판정은 `/Users/hyun/Desktop/dddjango`에서 태그 `dddjango-web--v1.1.25`의 파일을 `git show`로 읽어 확인했다. `architecture-web/references/final.md`와 `implementation-ui/references/final.md`는 현재 파일과 바이트가 같았다. `discipline-web-houserules/references/final.md`는 현재와 달라 **태그의 줄 번호**를 사용했다. 아래는 파이프라인을 새로 실행하기 위한 지시가 아니라 당시 결함의 판정 근거다.

| 1.1.25 규칙 위치 | 실제 규정 | 이번 표본의 귀결 |
|---|---|---|
| `dddjango-web/skills/architecture-web/references/final.md:139–140` | 시각 값은 foundation 토큰만. **“풀 밖 원본 값은 출처를 붙여 새 토큰으로 등록한다. 같은 값이 아닌 근접 토큰으로 대체하지 않는다.”** | success-soft·surface-muted 부재는 대체 사유가 아니다. R18·R19는 규칙이 강제한 차이가 아니라 잘못된 매핑 |
| 같은 파일 `:141–143` | 재사용 우선과 함께 토큰의 요소 결합·암묵값·실측 확인을 요구 | 토큰 230개를 후보 채택했다고 panel=26·elevation=2 연결이 생기는 것은 아님 |
| `dddjango-web/skills/implementation-ui/references/final.md:35,40–42` | DOM 관계·CSS 선언/값/효과 조합 보존. 부품 정의까지 읽고, 기존 부품은 대상 variant·자식 효과·상태 외형이 같을 때 재사용 | 다른 재질인 solid→strong, 윤광 없는 판, 불완전한 PrimaryButton을 그대로 써야 한다는 규칙은 없음 |
| 같은 파일 `:45–47,184` | 효과의 각 층·자식을 확인하고 풀 밖 값 등록. 필요한 파일이 슬라이스 밖이면 재개하도록 반송. 근접 대체 금지 | “공용 부품이라 그대로”, “새 토큰 0”, “범위 밖이라 효과 생략”을 이 규칙의 강제로 볼 수 없음 |
| `dddjango-web/agents/design-architect-web.md:50` / `agents/coder-web.md:52` | 설계자는 호출부와 부품 정의를 연결, 코더는 원본 정의·실제 적용 스타일에서 외형을 가져옴 | 명세 누락과 별도로 코더의 직접 원본 확인도 실패 방지 장치였음 |
| `dddjango-web/skills/discipline-web-houserules/references/final.md:163` | native HTML/CSS로 충분하면 JS 파일 없음. 새 JS 프레임워크/라이브러리 금지 | 제한은 실제 존재하지만 T 35개에 필요한 CSS 표현을 막지 않음 |

**F 주원인 0**은 “플러그인에 개선할 점이 없다”는 뜻이 아니다. 규칙의 요구와 실제 검증 수단이 다르다. 1.1.25 `dddjango-web/commands/dddjango-web.md:196`은 기계 대조 축 밖의 **블록 유무·비텍스트 구성은 육안 소관**이라고 한다. Codex판 `codex-dddjango-web/skills/dddjango-web/assets/render_audit.js:8,24`도 텍스트 리프와 `TEXT_CAP=200`을 명시한다. P1의 원본·구현 `render-audit*.json` 모두 texts 200, `textsTruncated=true`였고, [visual-check.md:57](p1/.dddjango-web/20260908-1534-web-chart/visual-check.md)은 diff 11을 표본/데이터·기존 폭 차이로 정리했다. 이 검증 구성은 패널 재질·자식 효과·누락 장식의 전수 확인을 보장하지 못했다.

### 3.4 후속 판을 첫 제출과 섞지 않은 확인

`44cfb2a14:.../design-spec.md:84,102,130`에는 중앙 정렬·gap 20·solid·padding 4px 14px·오른쪽 편집 버튼·aura가 구체적으로 보강되어 있다. 첫 제출 S에는 그 내용이 없었다. [problem1-time-analysis.md §4](../problem-lanes/problem1-time-analysis.md)의 “명세 §6·§8에 있는데 aura 미구현”은 **G2#2 시점**을 가리키므로 첫 제출 R8을 그대로 B로 소급하는 근거가 아니다.

마지막 `ab97d0964:.../design-spec.md:153,155`에는 윤광·shadow-2·배지 두 바탕과 radius-card 26px 보강이 따로 남아 있다. 이는 차이가 시안 값·부품 재질 매핑의 문제였다는 후속 정황과 일치한다. 이 보고서는 마지막 판을 새로 렌더하거나 최종 충실도를 검증한 것은 아니다.

## 4. 근거에 따른 처방 제안

1. **토큰 목록 대신 요소별 적용 계약을 입력의 중심에 둔다.** G0 실측에 case·상태·요소 식별자·원본 파일/줄·계산값·적용 토큰·부품 인자·효과 자식을 연결한다. `GlassPanel: radius 26, elevation 2, sheen 1, solid/strong 분리`처럼 조합을 보존한다. R8–R11·R14–R19가 근거다. 후보 토큰 전량을 명세에 나열하는 일은 이 연결을 대신하지 못한다.
2. **배치에는 측정값과 함께 부모 관계를 준다.** 가운데 정렬의 여유 공간 소유자, 스크롤 본문과 footer의 형제 관계, 정보 요약판의 세 divider·편집 행 padding을 명시한다. R1–R6처럼 좌표 하나만 맞추면 다른 높이·데이터에서 다시 틀어질 수 있는 항목은 원본 DOM 관계와 CSS 선언을 함께 옮긴다. 390px의 y좌표를 고정하는 처방은 하지 않는다.
3. **공용 부품 재사용을 이름이 아니라 렌더 계약으로 확인한다.** 원본의 tone/size/elevation/default/자식 층을 기존 구현과 대조하고 차이가 있으면 필요한 variant·정확 토큰을 반영하도록 한다. 재사용한 것은 공용 CSS뿐인지 실제 마크업도 같은지 구별한다. R9의 윤광 누락, R10의 26→34, R14의 solid→strong이 이를 요구한다. 기존 규칙도 이 방향이므로 이번 자료만으로 규칙 폐기나 프레임워크 전환을 처방할 이유는 없다.
4. **명세 갱신 시 과거 매핑의 소비처까지 대조한다.** “신규 토큰 0”, “토큰 부재→sunken”, “이번 범위에서 sheen 제외”가 현재 기준에서도 유효한지 코드 주석·선택자·실제 참조와 연결해 확인한다. S:143의 후보 채택만 바꾸고 C:221·616의 대체가 남는 상태를 완료로 보지 않는다. R9·R14·R18·R19가 근거다.
5. **G2 전에는 입력 표와 같은 대상·축으로 출력도 전수 대조한다.** 텍스트 200개·pinned 중심 검사에서 배경·선·radius·shadow·blur·자식 장식·아이콘·간격까지 넓힌다. W8의 차이를 원인별로 묶어 한 번에 검토하고, 수정 후 해당 case에서 확인한다. R12처럼 정확값이 이미 있어도 코드에서 어긴 차이는 출력 검사 없이는 남는다. 데이터가 다른 행·가짜 상태바·뒤 설정 페이지를 그대로 차단하는 과잉 수리는 피한다.

입력 정확값 표는 “처음부터” 필요한 정보를 주고, 출력 대조는 그 정보가 실제로 적용되었는지 확인한다. 이 자료에서 둘 중 하나만 고르면 사후 누락을 확실히 드러낸 쪽은 W8이지만, 재작업을 줄이는 목적에는 요소별 입력과 출력 검사를 연결하는 것이 더 적합하다.

## 5. 확신이 낮은 판정과 자료 한계

- **A/B 분류의 해석 한계**: 이 보고서는 요소에 대한 구체적 적용값·구조가 없으면 A로 셌다. 원본을 직접 받은 코더의 책임을 포함한 조직적 책임 배분이나 실제 사고 과정을 측정한 것은 아니다. 코더가 무엇을 읽고 왜 선택했는지는 세션 전량을 재구성하지 않았으므로 단정하지 않는다.
- **중간 확신**: R8의 층 네 묶음은 비교기의 겹친 region 병합을 포함한다. R6은 앞 판 배치의 파생 차이다. 같은 원인이라고 확인했지만 이를 독립 결함이나 독립 예방 효과로 해석하면 과장된다. R3의 높이는 복합 원인이므로 padding만의 문제로 축약하지 않았다.
- **관찰 범위**: 다섯 390×844 case의 동결 측정과 소스를 분석했다. 준비 화면·버튼·판 모서리는 저장된 `sbs-info.png`, `sbs-empty.png`, `known-pillars-corner.png`도 열어 확인했다. 화면 아래쪽 항목은 측정 JSON·소스 근거이며 이번에 스크롤 캡처를 새로 만들지 않았다. desktop·새 데이터·다른 브라우저에서의 예방률은 주장하지 않는다.
- **측정 표와 효과**: (가)의 23/12는 입력 계약의 정적 충족 가능성, React 직접 재사용의 25/4/6은 명시된 조건의 반사실 분석이다. 실제 재구현 A/B 실험 결과가 아니다. 일반 라이브러리 허용만으로 발생할 정확한 성공률은 이 자료로 식별할 수 없다.
- **T 이외의 차이**: 지장간 한글/한자에서 파생한 15개 데이터 라벨 묶음 등을 재분류하지 않았다. 이를 제품 결함으로 보는 다른 기준이라면 모집단부터 달라진다. 선택 항목인 발주자 반송 18건의 A–F 전수 재분류는 수행하지 않았으며, 그 18건과 T 35개를 같은 분모로 합치지 않았다.
- **자매 플러그인 비교**: dddart의 약 99%는 지시서가 제공한 사용자 체감 배경이다. 동일 시안·상태·데이터·개발자·측정 절차로 비교한 자료가 없어 Flutter 우월성이나 토큰 정책의 무해성을 실증했다고 쓰지 않는다.
- **실행 범위 준수**: 자료 읽기와 report.md 작성·검산만 수행했다. 제품 코드·동결 자료·p1 체크아웃을 변경하지 않았고, 서버·DB·네트워크·다른 프로세스를 사용하거나 건드리지 않았다. 파일 출력은 이 폴더의 report.md 하나다. 금지된 경로에서 `git status`를 실행하지 않았다.
- **도구 선택**: 정확한 문자열·문서 원문·CSS 값 대조였으므로 기본 파일 검색·읽기를 사용했다. Serena는 심볼 조사·편집이 필요하지 않아 사용하지 않았다. Graphify는 현재 폴더와 p1 모두 opt-in 그래프가 없어 사용하지 않았다.

REPORT-DONE
