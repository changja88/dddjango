# dddjango-web 시각 충실도 축 개정 — 수정 계획 v2 (적대 리뷰 반영 확정본)

- 상태: **v2 구현 완료** (2026-08-24. v1 → 3인 패널[P1 기술·P2 코퍼스·P3 목적] 발견 blocker 3·major 14·minor 15 → 처분 반영(§7) → 전량 구현 → 계획 대조 리뷰 «계획대로 구현됐다» 판정·잔여 minor 3건[G0 배너 표면화 문면·ⓓ/ⓔ 라벨·pinned 부분 소실 키 차집합] 즉시 수리. 검증: fixtures_audit 12 PASS·run_fixtures 총 116 양측·plugin validate --strict·make verify green)
- 원인 정본: `workspace/design/2026-08-24-web-fidelity-defects-analysis.md` v2 ([A] A1~A5 / [B] B1~B3)
- 수정 대상: dddjango-web(산문 정본) + codex 미러. kkebi-server 재빌드는 범위 밖(사용자 확정 스코프 «dddjango-web 수정» — P3 검증 통과). 트리 v3.2 무변경(신규 파일 전부 플러그인·산출물 폴더 소속 — P2 B2 검증).

## 1. D-α. 렌더 실측 채널 (A1·A2 봉합)

**`dddjango-web/assets/render_audit.js`** — 사용자 브라우저 콘솔용 관찰 스니펫(거처는 assets/ — «사용자에게 건네지는 고정 판형물» 판형, P2 A12). IIFE·의존 0·`try/finally` 스크롤 복원·실패 시 `partial: true` 필드(P3-4).

- **수집**: `audit_version: 1` · url · viewport{w,h} · 앱 컬럼 후보{width,x}(중앙 정렬 컨테이너 휴리스틱) · **texts[]**(가시 텍스트 리프·정규화 후 길이 ≥2·상한 ~200·결정론 정렬): `{key, text, fontSize, weight, lineHeight, textAlign, color, fontFamily, rect}` · **pinned[]** · scroll{mode, height}.
- **조인 키 정규화(P1 blocker①)**: NFC·NBSP→공백·연속 공백 접기·콤마 제거·**숫자 런→`#` 접기**·40자 절단 — 키에만 적용, 표시 텍스트는 원문(실측: 목표 하단 바 카운터가 페치마다 변동 «2,380»→«2,479» — 정규화 없인 채널의 존재 이유인 그 요소들이 조인 실패).
- **effectiveWeight**: fontFamily에서 `_([1-9]00)` 비앵커 매치(100 단위 검증 — `Pretendard_700`·`Pretendard_700Bold` 모두 포섭·무관 숫자 차단, P1) 우선, 없으면 computed weight.
- **pinned 2점 샘플링(P1 major 재설계)**: 스크롤 주체 판정 — 문서가 스크롤 가능하면 문서, 아니면 **자격 있는 내부 스크롤러**(가시·`overflow-y ∈ {auto,scroll}`·`scrollHeight−clientHeight` 최대 — hidden 셸을 굴리는 오선택 차단). 표본은 **maxScroll의 1/3·2/3 내부 2점**(0점 기준이면 중간 진입 sticky-top 미검출) · `scrollTo({behavior:'instant'})` · 측정은 대입과 **동기 같은 task**(IO/lazy-load 개입 차단). pinned = 두 점에서 rect 불변(±1px)·가시 · **스크롤러 자신과 그 조상 제외**(내부 모드 래퍼 오염 차단) · 중첩은 최외곽만·상한 20. 스크롤 여지 없으면 mode:'none'. 목표=내부 스크롤러·구현=문서 스크롤로 **두 실측의 스크롤 주체가 다른 게 정상**임을 명기.
- **수거(P1 major)**: `copy(JSON.stringify(...))` 시도 + `console.log` 문자열 병행. Coordinator 안내에 **«allow pasting» 타이핑 절차 1줄**(Chrome·Firefox self-XSS 가드)과 **파일 저장이 1차 경로**(40~80KB — 대화 붙여넣기는 소형만, P3-4) 명시. CSP·TrustedTypes는 콘솔 평가에 무적용(P1 검증 — 폴백 불요·실패 시 미실측 경로).
- **동결·의무(P2 A7·P3-5 — 기준 단일화)**: 커맨드 Phase 0 step 5-5에서 motion-notes와 나란히 — `<산출물 폴더>/render-audit.json`. 의무 기준은 **«원본 브라우저 열람 성립» 단일 축**(실서비스 원본이면 제공 형식 무관 — 이미지만 제공이어도 열람이 성립하면 의무·`.dc.html`/자체 설계는 해당 없음·**static_only도 의무 동일**). **동결 직후 `compare_render_audit.py --validate`로 파싱·스키마 즉시 검증**(P3-4 — 깨진 동결이 G2에서야 발각되는 왕복 차단).
- **미실측 처우(P2 A3 — motion-notes와 의미론이 다름을 명시)**: 실측 생략 시 파일 없음·`has_render_audit=false`, **사유는 scope.md에 1줄 기록**(산문 거처) + G0 배너 표면화 — 스텁 JSON으로 true를 만들지 않는다(compare 오발동 차단). 조용한 생략 금지는 동일.
- **플래그**: build-state `has_render_audit` 신설(:55-58 플래그 판형·:64 설정 시점 목록 합류).
- **채널 겹침 우선순위(P3-8)**: 같은 사실이 motion-notes(문답 산문)와 pinned 실측(기계)에 둘 다 있으면 **실측 우선·문답은 실측 부재 시 폴백** — architect 처분 불릿에 1줄.

## 2. D-β. G2 결정적 대조 (A2 봉합)

**`dddjango-web/scripts/compare_render_audit.py`** — 결정론 diff. exit 0=일치/1=사용법·파싱·스키마(**fail-loud** — `audit_version` 부재·필드 결손 시 exit 1, P1)/2=diff.

- **축**: fontSize(**float 파싱+ε 0.05px** — 문자열 비교 금지·±1 확대 금지[rem 유래 소수 차는 진짜 결함], P1) · effectiveWeight(정확) · textAlign · color(`rgb()/rgba()`→**hex8 정규화**[알파 포함]·비-legacy 직렬화는 warn+문자열 폴백) · lineHeight(**양쪽 normal=일치·한쪽 normal=diff·둘 다 px면 ±1px**, P1 major) · **상대 위치(P3-1 major — 신설)**: 조인 쌍 rect를 앱 컬럼 박스로 정규화해 **Δcenter-x > 컬럼 폭 5% → diff·수직 순서 역전 → diff**(이번 신고의 배지 위치·제목 중앙 정렬을 기계 검출 — textAlign 단독은 flex 부모 중앙화를 놓친다) · **pinned 인벤토리**(목표에 있는데 구현에 없으면 diff) · 앱 컬럼 폭.
- **중복 키(P1 blocker① 후속)**: 숫자 접기로 같은 키가 된 그룹(«#%»·«+#» 류)은 **그룹 단위 다중집합 비교**(축 값 분포 대조) — 개별 짝짓기 안 한다.
- **뷰포트 가드(P3-7)**: 두 JSON의 viewport 폭 불일치 시 경고 헤더(전 축 허위 diff 방지).
- **미조인**: 정보 표기만 — diff 0이면 exit 0(데이터 차이는 결함이 아니다).
- **G2 절차(:154 ⓑ 확장)**: `has_render_audit`이면 — 같은 스니펫을 구현 페이지(runserver)에서 실행(**목표 실측과 같은 브라우저·같은 창폭** 지시, P1) → `<산출물 폴더>/render-audit-impl.json` 저장 → Coordinator가 compare Bash 실행. **배너 1급 의무 표기(P3-3 major)**: 수행 시 «실측 대조: 축별 diff N건 요약» / 미수행 시 «실측 대조: 미수행 + 사유» — 모드 판별·디자인 출처와 같은 «항상 표시» 급(승인 차단은 아니다 — 대면 강제만). **exit 1은 백스톱 판형 준용**: 미실행 취급·통과 간주 금지(:153 준용 명시, P2 A10). diff는 **판단 자료**(반송 강제 아님 — 시각 최종 오라클은 사용자·의도한 이탈은 수락 가능. P1·P2·P3 전원이 이 의미론 유지 판정). 결과·방식은 `g2_visual`에 합류 기록(:60 문면 갱신).
- **관찰 항목**: ⓑ 안내에 «고정 오버레이는 **스크롤 중간에** 유지되는지 확인(끝까지 내려서가 아니라)» — 채널 유무 무관 항상.
- **정직한 한계 병기**: 자동 대조가 커버하는 축을 배너에 명시(«기계 통과=전부 통과» 오독 방지) — 블록 유무(프로모 패널 류)·비텍스트 요소 구성은 육안+시안 소관 유지.
- **산출물 처우(P2 A8)**: render-audit-impl.json은 G2 산출물로 산출물 폴더에 남는다(마무리 합치기·사용자 커밋 대상 — 별도 커밋 단계 불요 1줄).

## 3. D-γ. 배치 거동 규범 (A3·A5 봉합 — P1 blocker② 문면 교체 + P2 A4 소유 분할)

**결정 수준(architecture-web §8 — architect·review-web 도달)**: «배치 거동(고정 오버레이) 결정(설계자 소유)» — pinned 실측·시안 근거로 고정 요소의 존재·앵커(top/bottom)·스크롤 스킴(문서 스크롤 vs 내부 스크롤 패널)을 명세에 확정한다. 재현 스킴 등가 원칙(목표가 absolute+내부 스크롤러여도 sticky+문서 스크롤 재현은 등가 — 원인 정본 §4) 포함.

**표기 수준(implementation-ui §7 — coder 도달·P1 대안 문면 채택)**:

> 스크롤 중 화면에 붙는 바·헤더는 `position: sticky`(+`top`/`bottom` 명시)를 기본으로 한다. sticky는 **가장 가까운 스크롤 컨테이너**에 고정된다 — 따라서 sticky 요소와 그것이 붙어야 할 스크롤포트(문서 스크롤이면 뷰포트, 내부 스크롤 패널이면 그 패널) **사이의 중간 조상**에는 스크롤 컨테이너를 만드는 overflow 값(`hidden`·`auto`·`scroll` — 어느 축이든)을 두지 않는다. 의도한 스크롤 컨테이너 자체의 `overflow: auto|scroll`은 정당하다(그 안에 고정하려는 sticky의 기준이 바로 그것이다). 래퍼·셸의 가로 삐짐 클립이 필요하면 `overflow-x: clip`(스크롤 컨테이너를 만들지 않는 유일한 클립 — 단 hidden과 달리 BFC 비생성이니 필요 시 `display: flow-root`, 단일 축 clip에 `overflow-clip-margin` 무적용). 문서 흐름 밖 전역 오버레이(모달 류)만 `fixed`로 하되, **fixed 조상 사슬의 transform·filter·backdrop-filter·will-change: transform은 containing block을 빼앗아 무력화한다** — 진입 모션의 transform이 조상에 남지 않게 한다. 말줄임 `overflow:hidden`+`text-overflow` 리프·카드 이미지 클립처럼 사슬 밖 사용은 그대로 정당하다. sticky 바는 불투명 배경 토큰 필수.

- v1 문면(«조상 사슬 전체 금지»)은 내부 스크롤 패널 sticky·목표 구조 재현을 불법화하는 결함으로 **교체**(P1 blocker②). 루트(html/body 단독) overflow-x:hidden은 뷰포트 전파로 무해하나 일관성 위해 clip 각주 1줄(P1 minor).
- **discipline-reviewer-web 단서(트리거 결정화, P3-9)**: «`position: sticky|fixed` **grep 히트 시** 조상 사슬 overflow·transform 대조 의무»(발견 재량 제거).
- **houserules 무수정 = 의식적 기각 기록(P2 A4·P3-8)**: 원인 정본 §5-3의 «houserules 성문» 지시에서 이탈 — houserules 헌장(파일·명명·import·JS 순수성)에 CSS 내용 규범의 칸이 없고, 도달 공백은 위 소유 분할(결정=architecture-web·표기=implementation-ui)이 해소한다.

## 4. D-δ·D-ε·D-ζ (B1·B3·A4·배선)

- **D-δ 사실 교정(B1)**: architecture-web §8:129 + 커맨드 :121 — «computed 명시화» → 실능력(스타일 블록 명시값의 **후보 절단 5축**[색·크기·간격·radius·그림자] — 요소↔값 결합·웨이트·정렬·행간 부재·CSR는 결합·데이터 콘텐츠 자체 부재)으로 정정, 결합 실측은 render-audit 채널 소유.
- **관찰 판형 확장(B3 — 전방 보강·원인 수리 아님 명기)**: motion-notes 문답 트리거에 «스크롤 고정(화면에 붙어 따라오는 요소)» 명시·sticky는 재현 분류 CSS 칸 수납 예시.
- **D-ε 백스톱 불신설 판정 유지**: CSS 단독으론 DOM 조상 불가지·«셸 격» 판별은 의미 판단(#462 판례). 대체 3겹 = D-γ 성문(예방)+리뷰어 단서(문면)+D-β pinned(증상 기계 검출) — P3-9 «충분» 판정.
- **D-ζ 에이전트 배선**: design-architect-web — 입력에 render-audit.json + **«렌더 실측 전수» 처분 불릿**(동적 표현 전수와 동일 판형: 실측 표 요소를 전수 채택/기각·빈칸 0·`has_render_audit`이면 크기·웨이트·정렬은 실측 인용 의무·눈대중 근사 금지·pinned→배치 거동 결정·실측 우선/문답 폴백). design-review-web — 대조 입력 + «실측값 대비 명세 어긋남·pinned 미반영» 점검. coder-web — **무수정**(implementation-ui 로드로 충분 — «필요 시» 갈래 삭제, P2 A13).

## 5. 파일 목록 (P2 A5·A6 반영 완전판)

**claude측** — 신설 3: `dddjango-web/assets/render_audit.js` · `scripts/compare_render_audit.py` · `scripts/test/fixtures_audit.sh`(신규 파일 — 러너 auto-glob 무수정 합류·extract 파일 확장은 소관 명세 위반, P1·P2 일치 판정). 수정 9: `commands/dddjango-web.md`(앵커 15곳 — 아래) · `skills/architecture-web/references/final.md`(§8 교정+불릿 2) · `skills/architecture-web/SKILL.md` · `skills/implementation-ui/references/final.md`(§7 배치 거동 항) · `skills/implementation-ui/SKILL.md` · `agents/design-architect-web.md` · `agents/design-review-web.md` · `agents/discipline-reviewer-web.md` · `workspace/design/2026-08-23-web-presentation-layer-spec.md`(결정 대장 **D13 신설** — 트리 무변경·D12 무충돌[관찰 도구는 web/ 밖] 병기).

**커맨드 앵커 15곳(P2 누락 앵커 전량 합류)**: :9·:194(직접 쓰기 닫힌 목록 2곳 — render-audit 2종 합류) · :24(산출물 위치) · :55-60(스키마 — has_render_audit·g2_visual 문면) · :64(플래그 설정 시점) · **:115(재동결 열거 합류 + 기존 폴더에 채널 부재 시 «초동결» 질문 — P2 A1 blocker·P3-2)** · :121(실측 채널 본문·의무 기준·검증·수거 판형·사실 교정·문답 트리거 확장) · :132·:133(Phase 1 입력 2곳) · :141(⑤ 커밋 열거 — render-audit.json 합류·**motion-notes.md 잠복 누락도 함께 정리**, P2 A8) · :154(G2 ⓑ 전체) · :156-158(Phase 3 보고 — compare 결과[수행 시]를 실행 검증 목록에·«시각 정합 전체가 아니라 측정 축 일치»로 정밀화, P2 A11) · **:171-176(수정 모드 — 재사용 폴더에 render-audit 없으면 G0에서 초동결 질문 의무 — 실전 검증 3호 성립 조건)** · :180(트리비얼 — 재실측·compare 불촉발 면제 명문, P2 A9).

**codex측(P2 A5 완전 열거)**: byte 5 — `render_audit.js`·`compare_render_audit.py`·`fixtures_audit.sh`(codex 스크립트 트리 대응 위치) + `skills/architecture-web/references/final.md`·`skills/implementation-ui/references/final.md`. 의미 치환 4 — 커맨드 대응 `skills/dddjango-web/SKILL.md` + 에이전트 대응 SKILL.md 3종(design-architect-web·design-review-web·discipline-reviewer-web). `agents/openai.yaml` 무수정.

## 6. 실행 사슬·검증·비변경

S1 도구: render_audit.js + compare + fixtures_audit.sh(케이스: green 일치 / red 크기 diff / red pinned 소실 / red 상대 위치 / exit 1 스키마·사용법 / **결정론**(2회 byte 동일 — G2 증적이므로 필수급) / 미조인-정보만 exit 0 / negative마다 positive-control 짝 — fixtures_extract.sh 판형 준용) → `run_fixtures.sh` 전건 green(**현행 실측 104** + 신규 — v1의 105는 오기, P1) → S2 커맨드 앵커 15곳 → S3 references·SKILL·agents → S4 spec D13 + codex 미러(byte cmp 검증 — verify-web은 미러 동일성을 안 보므로 수동 cmp 의무, P2 A5) → S5 `claude plugin validate dddjango-web --strict` + `make verify` → S6 계획 대조 리뷰(사용자 판형 «계획대로 구현됐는지») → 조감도·메모리·커밋.

- **비변경**: w2 WIP 무접촉 · dddjango 본체·온톨로지 무접촉 · houserules(의식적 기각 — §3) · extract_design.py(P3 ⓐ 판정: 축 추가는 배정 근거를 못 주는 중복 투자 — 실측 채널이 상위 호환) · backstop 검사기 · coder-web.md.
- **알려진 잔차 병기(P3-6)**: ① 스킴 등가의 가장자리 3건(스크롤바 위치·모바일 URL바 수축 추적·iOS 러버밴드 — 신고 무관) ② 실서비스 원본인데 사용자가 실측을 생략한 경로(배너 1급 대면으로 완화 — §2) ③ 프로모 패널류 블록 유무·비텍스트 구성은 육안 소관.
- **마무리 보고 의무(P3-5 판정)**: 설치본 v0.1.0(08-22)·갱신 0회 사실 + 갱신 방법 + 두 화면의 수정 모드 재실행이 실전 검증 3호이며 그 성립 조건이 :115/:171 배선임을 안내.

## 7. 처분 대장 (blocker 3·major 14·minor 15 → 채택 29 · 기각 0 · 반증 실패 확인 12군)

- **채택(blocker)**: P1① 조인 숫자 정규화+중복 키 그룹 비교(§1·§2) · P1② D-γ 문면 교체 — «중간 조상» 한정+대안 문면 채택(§3) · P2 A1=P3-2 수정 모드·재사용 초동결 배선(:115·:171 — §5).
- **채택(major)**: P3-1 상대 위치 축(§2) · P3-3=P2 A10 배너 1급 의무+exit 1 준용(§2) · P3-4 여정 3종 — copy/파일 1차·즉시 --validate·try/finally+partial(§1·§2) · P1 pinned 내부 2점·필터·스크롤러 자격·instant·동기 측정(§1) · P1 lineHeight normal 특례(§2) · P1 audit_version fail-loud+픽스처(§2·§6) · P1 allow-pasting 안내(§1) · P1 fixed×transform 금칙(§3) · P2 A2 닫힌 목록 2곳 · A3 미실측 거처(scope.md·스텁 금지) · A4 소유 분할(결정/표기) · A5 codex 완전 열거 · A6 SKILL 4파일 · A7=P3-5 의무 기준 단일화+static_only.
- **채택(minor)**: P1 float+ε·hex8·비anchored `_NNN`·같은 브라우저/창폭·104 교정·NBSP · P2 A8(:141+motion-notes 정리·impl.json 처우)·A9 트리비얼·A11 Phase 3·A12 assets/ 거처·A13 coder-web 갈래 삭제 · P3-6 잔차 병기·P3-7 중복 키/뷰포트 가드·P3-8 기각 기록+실측/문답 우선순위·P3-9 단서 트리거.
- **기각**: 0건(v1 자문 §5-7 «나란히 표기 대체»는 P1·P3가 공히 기각 — compare 유지).
- **반증 실패 확인(설계 유지)**: 콘솔 CSP/TT 실행성(P1) · fontSize 정확 일치(P1) · pinned 콘텐츠 변동 강건성(P1) · compare 도구 필요성(P1·P3) · G2 판단 자료 의미론(P1·P2·P3) · D12v2 무충돌·WP 표면 밖(P2 B1) · D13 신설 판형·트리 무변경(P2 B2) · 신규 픽스처 파일(P2 B3) · «렌더 실측 전수» 불릿 대칭(P2 B5) · 교정 앵커 실재(P2 B6) · extract_design 무수정(P3 ⓐ) · 파일 분리 유지(P3 ③)·범위 밖 처리(P3 ⑤)·A5 3겹 충분(P3-9).
