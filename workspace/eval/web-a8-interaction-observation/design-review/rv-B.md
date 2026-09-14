# 독립 리뷰 B(규범 렌즈) — 웹 시안 조작 상태 증거·재동결 기계 대조 설계

대상: `workspace/design/2026-09-13-web-interaction-evidence.md`(이하 «설계», 행 번호는 그 파일). 진단 `workspace/eval/web-a8-interaction-observation/diagnosis.md`(«진단»), 선행 계획 `workspace/plan/2026-09-13-web-a8-interaction-observation.md`(«계획»), 기준선 규범 = 작업 트리(v1.1.7 내용), 되돌려진 변경 = `git diff dddjango-web--v1.1.7 HEAD -- dddjango-web/`(«되돌린 diff»). A8 빌드(`~/.herdr/worktrees/spring_dream_server/a8/.dddjango-web/20260912-1640-web-related-persons`)는 읽기만 했다.

3축 표기: **코퍼스 정합**(기존 규범·결정·미러 계약과의 정합) · **일반화**(A8 밖 시안·엔진·환경에서 성립) · **무손실**(기존 보장·증거·상태의 손실 없음). ✗ 위반/손상 · △ 부분 · ✓ 무해. «추측»이라 적은 것은 파일로 확인하지 못한 판단이다.

---

## 1. 전제 공격 — 진단 §4와 설계 «근거와 성공 조건»이 틀렸을 가능성

**P1. 성공 조건이 «실행»을 요구하고 «동결»을 요구하지 않는다 — 사용자 보고 원문과 어긋난다.** 진단 L3 사용자 원문은 «다이얼로그가 디자인 안에서 js로 완성이 되는데 이걸 **동결하지 않아**»이고, 진단 §1 L16의 결함 행은 «보지 않음 → **동결 없음**»이다. 그런데 설계 성공 조건(L11~15)은 ① 조작 기록 없이 ready 불가 ② 잔여 0 ③ 재동결 대조 ⑤ «발견·실행하고 잔여 0으로 … 통과»까지다. `interactions.json`(L76~91)은 인벤토리 id·`state_hash`·값 변화를 기록할 뿐 조작 후 상태의 캡처(바이트)를 남기지 않고, 그 상태가 `design-input` case로 동결되는지는 리뷰어 재량에 맡긴다(L121 «독립 렌더가 필요한 상태만 case 추가를 요구»). 즉 설계는 «조작했다»는 증거를 기계화했고 «조작 결과가 구현 대조 기준으로 동결됐다»는 증거는 기계화하지 않았다. A8에서 실제로 없었던 것은 «열린 메뉴 캡처 0장»(진단 L16)이다. 성공 조건 자체가 사용자 보고보다 좁다 — 발견 B2로 이어진다.

**P2. 진단 §4-1 «증거 계약에 조작 대상이 없다»는 맞다. 그러나 §4-2 «리뷰어 재량이 메운다»의 처방이 설계에서 반만 이행됐다.** 설계 L32는 «리뷰어는 … 상태↔case 연결만 감사한다»고 해 case 연결을 여전히 리뷰어 재량에 둔다. 계획 L85의 결론은 «독립 reviewer의 의미 판정만으로 누락 항목이 면제된다»였고 이것이 기각 사유였다. 실행 면제는 막았지만 동결 면제는 같은 자리(리뷰어)에 남아 있다.

**P3. «프롬프트 보강 3회 실패»(진단 §3)의 교훈이 MCP 대체 경로에서 무효화된다.** 설계 L93은 MCP Playwright로 «같은 스니펫을 evaluate로 실행해 같은 형식을 내야» 한다고 하나, 탐색 루프(L57~60: 새로고침→경로 재생→조작→안정 대기→인벤토리→큐)는 스니펫이 아니라 드라이버의 몫이다. MCP 경로에서 그 루프는 LLM이 도구 호출을 손으로 반복하는 것 = 실패한 프롬프트 접근이다. 발견 M2.

**P4. 성공 조건 5의 «스크림»은 설계된 스니펫으로는 발견되지 않는다(A8 원본 확인).** 발견 B1 — 설계가 자기 성공 조건을 구조적으로 못 만족한다.

**P5. 기준선 결정 ③(v1.1.7·1.1.8~12 미재도입)의 적용이 불완전하다.** 설계 L124는 재도입 금지를 선언하지만, L121은 1.1.11에서 되돌린 design-review-web G0 문장을 의미 그대로 옮겼고(B2), L114 «_history/vN 기존 절차»는 v1.1.7에 없는 절차다(M5).

**P6. 정적 HTML 경로(freeze_design·`source_ready=true`)의 JS 조작 상태는 범위 밖이다.** 설계 성공 조건 4가 «정적 HTML 시안은 통과한다»고만 적었는데, 카피 대상 웹페이지의 JS 드롭다운은 archive 경로가 아니어서 `source_observation` 자체가 없다(check_design_evidence.py L380~392 — archive entrypoint에서만 `_source_observation`). 사용자 결정 ①의 범위 안이므로 결함은 아니나 «한계»로 명시돼야 한다(m9).

---

## 2. 발견 목록 (심각도 높은 순)

### BLOCKER

**B1. 스니펫의 «클릭 핸들러가 붙은 leaf만 대상» 규칙이 A8 다이얼로그 스크림을 구조적으로 놓친다 — 성공 조건 5 자기 위반.** [코퍼스 정합 ✓ · 일반화 ✗ · 무손실 ✗]

- 설계 L39: «클릭 핸들러가 붙은 leaf(React `__reactProps$*`의 onClick/…, `onclick` 속성, computed `cursor:pointer`이면서 **하위에 다른 대상이 없는 요소**)». L38 오버레이 판정: «`role` = dialog·alertdialog·menu·listbox 또는 `aria-modal`».
- A8 원본 `_ds_bundle.js`의 `function Dialog`(읽기 전용 확인): 스크림은 `React.createElement("div", {style:{position:'absolute', inset:0, … background:'var(--scrim)'}, onClick: onCancel}, React.createElement("div", {onClick: e => e.stopPropagation(), …}, … 버튼들))` — 즉 **스크림 div가 패널·버튼의 부모**다. 하위에 버튼(대상)이 있으므로 leaf가 아니고, 번들 전체의 role 어휘는 `status·radiogroup·radio·progressbar·menu·menuitem`뿐이며 `aria-modal`·`role="dialog"`는 0건이라 오버레이로도 등록되지 않는다.
- 결과: 성공 조건 L15 «실제 Coordinator 실행이 **사용자 지목 없이** 드롭다운 항목·체크박스·**스크림** 같은 대상을 발견·실행»이 설계된 열거 규칙으로는 불가능하고, `--declared`(L41)나 리뷰어 소스 감사(L121)로만 닫힌다. 그 경로는 «사용자 지목 없이»는 맞지만 «기계 발견»은 아니며, 진단 L36의 실패 형태(지목 뒤에야 확인)를 Coordinator 지목으로 바꾼 것에 가깝다.
- 권고: (a) 자기 요소에 핸들러가 있으면 후손 유무와 무관하게 대상으로 등록하고, 클릭 지점은 «요소 rect − 후손 대상 rect들»의 한 점으로 잡는다(없으면 `unclickable` 기록·잔여로 남긴다). (b) 오버레이 판정에 «루트를 덮는 absolute/fixed + 자기 핸들러» 휴리스틱을 추가한다(Esc 의무는 핸들러가 있을 때만 — A8 Dialog는 Escape 처리가 없고 Dropdown만 있다: 번들 `Escape` 1건). (c) 설계 «검증 및 순서» L128의 fixture 페이지에 «부모 스크림 + stopPropagation 패널» 짝을 넣어 회귀로 고정한다. (d) A8 실증 2(L135)의 oracle 대조에서 스크림·바깥 클릭이 «스니펫 발견»으로 잡혔는지를 «선언으로 닫힘»과 구별해 집계한다.

**B2. «case 내 변이 vs 독립 case» 판정을 리뷰어에게 남긴 것은 1.1.11에서 되돌린 문장의 재도입이며, A8 거짓 통과(«같은 핸들러 변이 면제»)를 «동결» 축에서 그대로 허용한다.** [코퍼스 정합 ✗ · 일반화 ✗ · 무손실 ✗]

- 설계 L121: «각 step의 결과 상태(추가/제거 대상·값 변화)가 design-input case 또는 «case 내 변이»로 연결되는지 대조하고, **독립 렌더가 필요한 상태만 case 추가를 요구한다**.»
- 되돌린 diff(design-review-web.md, 1.1.11 도입분): «focus 같은 부품 내부 상태는 해당 case 안에 두고, **독립 렌더가 필요한 화면·상태만 기존 case 절차로 추가한다**. 모든 CSS pseudo-state를 별도 case로 늘리지 않는다.» — 사용자 결정 ③(설계 L3 «1.1.8~1.1.12 프롬프트 누적은 재도입하지 않는다») 위반.
- 진단 L50: r3 거짓 통과 = «선택하지 않은 관계/지역 항목을 같은 핸들러의 데이터 변이로 제외». 계획 L85: «독립 reviewer의 의미 판정만으로 누락 항목이 면제된다. 프롬프트 순서 변경만으로 해결됐다는 가설은 기각». 설계는 실행 면제를 기계로 막았지만, «열린 메뉴 상태를 case(=캡처·구현 대조 기준)로 동결하느냐»는 정확히 같은 재량 자리에 남는다. 전제 공격 P1과 결합하면 사용자 보고(동결 없음)는 이 설계로 닫히지 않는다.
- 권고(기계 규칙 — 왜 없으면 깨지는가: 성공 조건이 사용자 보고와 어긋나므로 성공 조건 자체를 «조작 결과 상태의 동결»까지로 정정해야 하고, 그 판정에 재량이 남으면 진단 §3의 실패가 반복된다):
  1. 각 step에 `after.capture`(PNG 포인터·sha)를 남긴다 — 결과 상태가 case가 되든 안 되든 바이트로 동결된다(무손실). 캡처는 드라이버가 저장하며 Coordinator는 값을 쓰지 않는다(render-audit 선례와 동형).
  2. `changes.added ≠ ∅`(새 UI 표면이 나타남) 또는 `changes.url ≠ null`인 step은 **반드시** design-input의 어느 case가 `reached_by: <step n>`으로 참조하거나 `interaction_exclusions` 행이 가리켜야 한다 — 검사기가 대조한다. 값만 바뀐 step(체크 토글·입력값)은 참조 의무가 없다. 이것이 «case 내 변이»의 기계 정의다.
  3. 리뷰어 문장 L121의 «독립 렌더가 필요한 상태만»을 삭제하고, 리뷰어는 «reached_by 매핑의 의미 타당성»만 감사한다.

### MAJOR

**M1. v1 observation의 «완료 이력 허용»은 Coordinator 자기 기록(`build-state.json`)을 열쇠로 쓰는 작성자 면제 통로다.** [코퍼스 정합 ✗ · 일반화 △ · 무손실 ✗]

- 설계 L97: «v1은 그 build의 `build-state.json`이 `phase: finalize`이고 `g2_approved: true`인 완료 이력에서만 허용».
- `check_design_evidence.py`는 현재 `build-state.json`을 전혀 읽지 않는다(L241~416). design-evidence.md L43~45: «Explicit build selection … does not infer or authenticate the user's current scope from a folder name». build-state는 Coordinator가 «직접 쓰는 것»(dddjango-web.md L9·L231)이라 자기 기록이다. 진행 중 빌드의 build-state에 두 값을 적으면 v1이 통과한다 — 성공 조건 L12 «작성자 면제 필드는 없다»와 충돌한다.
- 이력 처리의 정당한 자리는 이미 있다: `backstop.py` L95~133 `current_nondesign_scope`는 같은 build-state 값을 보되 **git으로 `.dddjango-web/` 무변경을 검증**한 뒤에만 건너뛴다. 재개 빌드의 처리도 이미 있다: dddjango-web.md L127 «기존 폴더에 아직 없는 채널 산출물 … «신규 동결» 선택지로 같은 질문에 합류».
- 권고: `validate_inputs`에서 archive case의 v2를 무조건 요구한다. 과거 완료 빌드가 비시안 작업의 backstop에서 blocker가 되는 문제는 backstop의 git-검증 skip으로만 다루고(필요하면 skip 조건에 «v1 observation인 빌드»를 명시), 재개 시에는 step 4의 «신규 동결» 질문으로 수집기를 돌린다. 열린 질문 L144의 «대안»이 정답이다.

**M2. MCP Playwright 대체 경로는 탐색 루프를 LLM이 손으로 수행하는 경로이며, 드라이버 이름은 자기 신고다 — 실패한 프롬프트 접근의 재현.** [코퍼스 정합 △ · 일반화 ✗ · 무손실 △]

- 설계 L93: «MCP Playwright로 대체 실행해도 같은 스니펫을 `evaluate`로 실행해 같은 형식을 내야 하며, 드라이버 이름을 기록한다.» 스니펫이 하는 일은 열거·identity·전후 기록(L23)이고, 탐색(새로고침·경로 재생·큐·상한)은 드라이버(L24·L57~60)다. MCP에서는 그 루프를 Coordinator가 도구 호출로 반복해야 하고, 무엇을 클릭할지(큐)도 LLM이 관리한다 — 진단 §3·계획 L85가 기각한 방식이다. 잔여 검사는 «관찰된 대상»만 세므로(L99) 열지 않은 메뉴의 항목은 잔여에도 안 잡힌다.
- Codex 미러: `codex-dddjango-web/skills/dddjango-web/SKILL.md`는 `${SKILL_DIR}/scripts/*.py`·`assets/render_audit.js` CLI 실행만 쓰고 MCP 도구 가정이 없다(L157~206). MCP 경로는 Claude 전용 의미가 되어 의미 미러가 비대칭해진다(«추측»: Codex 런타임의 MCP Playwright 가용성은 확인하지 못했다).
- 권고: Node 드라이버를 단일 실행 경로로 하고 MCP 대체 문장을 삭제한다. 드라이버 실행 불가는 render-audit 생략 enum(dddjango-web.md L140 «실측 생략이 합법인 사유는 enum이다»)과 같은 형식으로 `design_status=blocked` + 사유 enum(Node 부재·Playwright 미설치·브라우저 실행 불가)으로 닫고 G0 배너에 표면화한다. «대체 실행»이 정말 필요하면 드라이버가 `--cdp <ws>`로 붙는 경로(이미 L53에 있음)만 남긴다.

**M3. «수정 모드 G0의 재동결 질문은 `--compare` 결과로 답한다»는 매 수정 모드마다 원격 전량 수신을 뜻하며, v1.1.7의 «PROJECT 타입은 자동 staleness 감지를 쓰지 않는다»와 충돌한다.** [코퍼스 정합 ✗ · 일반화 ✓ · 무손실 ✓]

- 설계 L122; L114 «재동결·«시안이 바뀌었나» 요청은 원격 파일 전부를 새 staging에 받은 뒤 이 명령을 실행».
- dddjango-web.md L132: «PROJECT 타입은 자동 staleness 감지를 쓰지 않는다 — 디자인 변경 반영은 **사용자가 "다시 적용"을 명시 요청할 때만** 재동결·재추출한다(트리거 = 산출물 폴더 재사용 절의 "외부 진실 재동결?" 질문·별도 폴링 없음)». L127의 질문은 «재동결 여부»를 **사용자에게 묻는** 것이지 «바뀌었나»를 기계가 답하는 것이 아니다.
- 권고: `--compare`는 사용자가 재동결 또는 차이 조사를 요청한 경우에만 실행하고, step 4의 질문 자체는 v1.1.7 그대로 둔다. L122 문장은 «재동결을 선택했으면 그 결과는 `--compare` 출력으로만 보고한다»로 좁힌다.

**M4. `--carried`는 v1.1.7이 «실패»로 규정한 절단 파일을 «미확인»으로 통과시키는 완화이고, carried-only 결과의 처분이 비어 있다.** [코퍼스 정합 ✗ · 일반화 △ · 무손실 ✗]

- 설계 L112: «`--carried`는 원격에서 받을 수 없어 이전 보관본을 그대로 옮긴 파일(예: 256KiB 한도 PNG)이며 «미확인»으로만 분류». L137 A8 실증 기대 «same 18·carried 4·exit 3».
- dddjango-web.md L134: «`truncated=true`, base64 절단, 빈 본문, 이미지 대신 HTML 응답은 **실패**다. 전송이 잘렸으면 … 재수집한다. 그런 수단이 없으면 해당 원본 파일 제공을 요청한다. 내용을 손으로 재작성하거나 잘린 base64를 성공 파일로 쓰지 않는다.» 이전 보관본을 옮기는 것은 «재수집»도 «제공 요청»도 아니다.
- 설치 후 손실: 새 archive는 carried 파일을 `status: ok`·정상 sha로 기록하므로(`archive_design.py` L151~153) «미확인» 표식이 manifest에 남지 않고, 다음 `validate_inputs`는 바이트 일치만 본다(L328~331). 의존성 교차 검사(L113)는 entrypoint가 참조하지 않는 파일에만 효력이 있어 프로젝트 제공 렌더 PNG(design-acquisition.md L15~16이 «목록에서 확인»하라는 파일)는 걸러지지 않는다.
- carried-only(same 전부 + carried 몇)이면 exit 3인데, «차이가 있으면 `_history/vN` 보존 → … 재관찰·수집·독립 검토·inputs»(L114)를 전량 다시 하는지, «동일 아님이지만 재관찰 불요»인지가 없다 — 그 빈칸을 Coordinator 산문이 채우게 된다(진단 §2의 «차이 0» 형태).
- 권고: `--carried`를 제거하고 v1.1.7대로 재수집/사용자 제공을 요구한다. 부득이 유지하면 ① entrypoint 의존성 밖 파일에 한정(이미 있음) ② manifest 행에 `carried_from: <이전 manifest sha>`를 남겨 미확인이 설치 뒤에도 보이게 ③ carried-only의 exit와 후속(재관찰 범위)을 표로 못 박는다 — 이 결정은 사용자 결정 ②·③ 어디에도 없으므로 숨은 결정으로 상정한다.

**M5. «기존 절차대로 `_history/vN` 보존»은 기준선에 없는 절차다 — A8 임의 관행 또는 되돌린 1.1.12 문단의 암묵 재도입.** [코퍼스 정합 ✗ · 일반화 △ · 무손실 △]

- 설계 L114. `dddjango-web/`·`codex-dddjango-web/` 전 파일 grep에 `_history` 0건(테스트 함수명 제외). A8 빌드에는 `_history/v1..v4/{captures,source-manifest.json,design-ref,…}`가 있다 — 실행 중 만들어진 관행이다. 되돌린 diff(design-acquisition.md 1.1.12분): «새 기준으로 전환하기 전에 기존 원본·manifest·관련 관찰/캡처를 함께 보존하고 … 이전 묶음은 같은 산출물 폴더 안에서 **활성 reference_root 밖**에 두며».
- 기계적 안전성은 확인했다: `validate_inputs`는 `reference_root` 트리만 inventory 대조하고(L334~338) `backstop.project_design_builds`는 `parts[2]`만 marker로 보므로(L65~77) `_history/v1/design-ref`는 빌드로 오인되지 않는다. 그러나 «어디에·무엇을·언제» 보존하는지가 규범에 없으면 Coordinator 재량이다.
- 권고: 절차를 설계에 명시하고(폴더명·포함 파일·`visual-check.md` 연결), 그것이 1.1.12 문단의 재도입인지 새 규범인지를 사용자에게 결정 게이트로 올린다(결정 ③의 예외가 되므로). 또는 «이전 묶음 보존» 없이 `--compare-out` JSON만 보존하는 최소안을 대안으로 제시한다.

**M6. 드라이버 큐(identity 신규 기준)와 검사기 잔여(대상·조작·상태 기준)가 어긋나 체크박스·native select에서 체계적 exit 2가 난다.** [코퍼스 정합 ✓ · 일반화 ✗ · 무손실 ✓]

- 설계 L59: «I′의 **새 identity**를 경로+[이 조작]으로 큐에 추가». L67: «checkbox·switch … 관찰된 checked 상태마다 `click` 1회(false·true 둘 다 관찰됐으면 2회)». L99: 잔여 = «필요 조작(위 표) − `status=executed`인 step의 (대상, 조작[, 옵션/상태])».
- 체크박스를 한 번 클릭하면 I′에 같은 identity가 `checked=true`로 관찰된다(identity는 checked를 제외 — L45). 큐는 새 identity만 넣으므로 두 번째 click(state=true)은 실행되지 않고, 검사기는 요구한다 → 잔여. native `select`의 «옵션마다 select 1회»도 옵션은 대상이 아니라 큐 생성 규칙이 없다.
- 권고: 큐 키를 `(identity, action, option/state)`로 정의하고 인벤토리마다 «필요 조작 − 실행/대기 중 조작»을 큐에 넣는다. 검사기 표와 드라이버 표를 한 파일(스니펫의 순수 함수)에서 공유해 Node 단위 테스트로 고정한다.

**M7. 리뷰어 소스 감사 → `--declared` → 미매칭 `unreachable` → 잔여 → 출구가 사용자 승인뿐 = 리뷰어 오탐이 사용자 결정으로 전가되는 교착.** [코퍼스 정합 △ · 일반화 ✗ · 무손실 ✓]

- 설계 L41 «선언 대상도 열거·실행 의무가 같다», L99 «`failed`·`unreachable`은 실행으로 세지 않는다», L100 «예외는 scope.md 사용자 승인만». L121 리뷰어는 «핸들러·prop(onClick·onCancel·onConfirm 등)을 읽어 `targets`에 없는 대상을 찾으면 입력 부족».
- A8 번들의 `onClick`은 29건이고 `onConfirm`·`onCancel`은 컴포넌트 prop이라 화면에 렌더되지 않는 조합이 있다. 리뷰어가 렌더되지 않는 prop을 대상으로 요구하면 Coordinator는 매칭 불가한 selector를 선언하고, 드라이버는 `unreachable`, 검사기는 잔여를 낸다. 닫는 길은 «사용자가 존재하지 않는 대상의 면제를 승인»뿐이다 — 결정 게이트 원칙(10줄 브리프·수치 기반)과도 맞지 않는 질문이다.
- 권고: 어느 인벤토리에서도 매칭되지 않은 선언은 `declared_unmatched`로 기록하고 잔여 계산에서 제외하되, 리뷰어 재검토 원문에 «미매칭 선언 N건: <selector·사유> 확인» 행을 필수로 두어 검사기가 `coverage-review.md`에서 그 행 수를 대조한다(선언 수 == 확인 수). 재량은 남지만 «보이는 재량»이 된다.

**M8. Node·Playwright 실행 의존성의 설치·버전·위치·동의·안내가 규범과 사람용 가이드에 없다 — 숨은 사용자 결정.** [코퍼스 정합 ✗ · 일반화 △ · 무손실 ✓]

- 설계 L24·L130: «Node Playwright 기준 실행기» · «실행 조건(프로젝트 로컬 설치 또는 `npx playwright`)을 규범에 명시». web 규범 전체에 `node`·`npx`·`playwright` 언급 0건(grep). DEVELOPMENT.md L56 «설치본은 **표준 라이브러리만** 쓴다». 기존 외부 의존 선례는 둘뿐이다 — htmx(dddjango-web.md L120: 고정 버전 URL로 `curl`·경로·버전·출처를 배너와 scope.md에 기록·네트워크 불가면 사용자 파일 요청)와 motion.js(플러그인 자산 복사). 둘 다 산출 앱의 자산이지 «게이트 실행기»가 아니다.
- 실행 경계(dddjango-web.md L121)는 «대체/설치/외부 DB 제한»을 scope.md에 적도록 하므로 Playwright·브라우저 바이너리 설치는 사용자 승인 사항이고, coder-web.md L73(«새 의존성의 버전 값은 훈련 기억으로 적지 않는다»)의 취지상 버전은 resolve 실제값이어야 한다. 사람용 계약(REQUEST_GUIDE — DEVELOPMENT.md L58~65: Claude 정본 + Codex byte 미러·`request_guide_contract.py` 검사)에는 Codex `multi_agent` 같은 전제조건을 적는 선례가 있다.
- 권고: 규범에 ① 설치 위치(사용자 `web/`·`.dddjango-web/` 밖 — backstop WP는 `static/js/`의 `.mjs`를 금지하므로[check_purity.py L156~158] 산출 트리에 절대 들어가지 않게) ② 버전 고정의 출처 ③ scope.md 실행 경계 승인 뒤에만 설치 ④ 불가 시 blocked + 사유 enum(M2와 합류) ⑤ REQUEST_GUIDE §에 «HTML/JSX 시안은 Node ≥ N·Playwright가 필요하다» 1문단 + Codex byte 미러. 이 정책 자체를 사용자 결정으로 상정한다(설계 L3의 3건에 없다).

**M9. hover를 interactions에서 제외한 것은 사용자 결정 ②(«발견된 조작 대상은 전수 실행»)와 충돌하는 숨은 범위 결정이다.** [코퍼스 정합 △ · 일반화 ✗ · 무손실 ✗]

- 설계 L72: «hover는 motion-notes 채널이 맡고 여기서 요구하지 않는다». motion-notes의 출처는 dddjango-web.md L140 «ⓐ 동결본 정적 스캔 … ⓑ 원본 브라우저 관찰과 필요한 보충 문답» — 실행 기록이 아니라 서기의 표이고, 진단 L19는 A8 motion-notes m5가 «실측 없이 실측이라 기록됨»이었음을 보여 준다. hover로만 드러나는 메뉴(설계 열린 질문 L145)는 어느 채널에서도 실행·동결되지 않는다.
- 권고: 표(L64~70)에 «hover 1회(핸들러·`:hover` 규칙 보유 대상)»를 넣고, hover 후 인벤토리 변화가 있으면 큐에 추가한다. 시각 효과(색·그림자)의 처분은 motion-notes에 남긴다 — 소유 중복이 아니라 «실행 vs 처분»으로 가른다. 넣지 않기로 하면 그 결정을 사용자 결정으로 명시한다.

**M10. 미러·배포 계약의 빈칸.** [코퍼스 정합 ✗ · 일반화 ✓ · 무손실 ✓]

- (a) `Makefile` L96~97 `diff -rq --exclude=__pycache__ dddjango-web/scripts codex-…/scripts`·`assets` — 새 `.mjs`·`.js`는 자동 포함된다(검증됨 V4). 그러나 Node 픽스처를 `scripts/test/`에서 실행하면 `node_modules`·Playwright 캐시가 한쪽에만 생겨 `diff -rq`가 red가 된다. `.gitignore`에는 `.playwright-mcp/`만 있다(L11). 설계 L130은 실행 조건만 말하고 위치·ignore 규정이 없다.
- (b) 설계 L123 «references는 byte 미러»라 하나 `verify-web`은 references를 대조하지 않는다(L91~101 — scripts·assets·REQUEST_GUIDE만). 현재는 우연히 동일(cmp 확인). 검증 목록(L138)에 `cmp` 3종을 넣거나 verify-web에 추가하는 결정을 적어야 한다.
- (c) dddjango-web.md L231 «네가 직접 쓰는 것은 … 뿐이다» 목록 갱신이 규범 연결(L118~124)에 없다. `interactions.json`은 render-audit와 같은 «기계 관찰 산출물 — 너는 값을 쓰지 않는다» 지위로, `<screen>-declared.json`은 서기 산출(motion-notes 정적 스캔과 동형)로 명기해야 한다. Phase 2 ⑤ 커밋 목록(L168)은 «원본 captures[있는 것 전부]»로 덮이지만 `refreeze-diff.json`·`_staging-manifest.json`은 어디 두고 커밋하는지가 없다.
- (d) 명령 예시가 `PLUGIN/scripts/…`인데 Claude는 `${CLAUDE_PLUGIN_ROOT}`, Codex는 `${SKILL_DIR}`(SKILL.md L157~206 관례)다. 드라이버가 스니펫을 `--snippet` 인자 없이 자기 위치(`import.meta.url`) 기준으로 찾아야 두 미러에서 인자 표기가 같아진다 — 명시 필요.
- (e) `claude plugin validate --strict`가 `scripts/*.mjs`를 문제 삼는지는 확인하지 못했다(«추측»: scripts/는 매니페스트 컴포넌트가 아니라 무관할 것). 검증 순서(L138)에 이미 있으니 결과만 기록하면 된다.

### MINOR

**m1.** 재동결 규범 문장(L114) «일부 파일 손대조·«차이 0» 단언·이전 sha 암기 대조는 결과로 쓰지 않는다»는 계획 L94 «기존의 실패한 장문 금지문을 더 누적하지 않고 실행/입력 계약으로 교체한다»에 어긋나는 금지문 누적이다. «출력이 유일한 근거다» 한 문장이면 족하다. 같은 문장의 «원격 파일 전부를 … 받은 뒤»는 `--carried`(못 받은 파일)와 자기모순이다. [코퍼스 정합 △]

**m2.** 범위 절 L19 «범용 탐색 엔진 … 만들지 않는다»와 실제 산출(BFS·경로 재생·상한을 가진 드라이버)이 어긋난다. 계획 L90은 «이미 연결된 Playwright page를 인자로 받는 작은 수집기 … 브라우저 설치/실행·원본 변경·임의 탐색은 하지 않는다»였다. 이탈 자체는 성공 조건 5(중첩 메뉴 자율 발견)로 정당화되지만, 설계가 그 이탈과 사유를 밝혀야 한다(09-06 설계 L15의 «범용 워크플로 엔진 금지» 문구를 그대로 옮긴 흔적). [코퍼스 정합 △]

**m3.** v1 trace의 `state_transition_actions`(산문 — A8 예: «tap 김서연 행»)와 v2 `steps[].path`(identity)가 이중 기록이다. case 도달 경로를 어느 step 경로의 접두사로 앵커하는 규칙이 없어 리뷰어의 «상태↔case 연결» 감사(L32)에 기계 근거가 없다. B2 권고 2의 `reached_by`가 이를 대체한다. [무손실 △]

**m4.** 오버레이 닫힘 경로 중 «바깥 클릭»이 표에 없다. A8 Dropdown은 `document.addEventListener('mousedown', away)`로 닫힌다(번들 확인) — Escape만 요구하면 그 전이는 관찰되지 않는다. 표에 «overlay: `click:outside` 1회»를 추가한다. [일반화 △]

**m5.** Playwright 부재 시 «SKIP + 사유»(L130)면 `make verify`에서 드라이버 열거·탐색 로직이 영구 미검증이다. 검사기(Python) 반례는 손으로 쓴 `interactions.json` 픽스처로 브라우저 없이 고정되므로 문제없지만, 드라이버는 A8 실증(L135)이 유일한 시험이 된다 — 릴리즈 전 필수임을 검증 순서에 명시하고 SKIP이 verify 로그에 남게 한다. [일반화 △]

**m6.** `focus` 채널 이중 소유: motion-notes 트리거 enum에 `focus`가 있고(dddjango-web.md L140) interactions는 입력에 `focus·fill·blur`를 요구한다(L68). 시각 효과 처분은 architect 처분 표, 실행 증거는 interactions로 가른다는 한 줄이 필요하다. [코퍼스 정합 △]

**m7.** exit 3 신설: 기존 계약은 check_design_evidence 0/1/2(design-evidence.md L22~23)·archive_design 0/1(L164~181)이다. «차이 ≠ 결함»이라 2를 쓸 수 없는 논리는 타당하나, design-evidence.md의 exit 표에 «3은 `archive_design.py --compare` 전용»을 적고 backstop이 이 exit를 소비하지 않음을 명시한다. [코퍼스 정합 △]

**m8.** `--compare`가 `--out BUILD/_staging-ref` 보관을 전제한다(L107~109) — 대조만을 위해 전량(최대 4096파일·파일당 32MiB)을 두 번째로 복사한다. STAGING을 직접 해시해 이전 manifest와 대조하는 `--compare-only` 모드가 더 작다. 보관이 꼭 필요한 이유(의존성 보고로 carried 교차 검사)는 `archive_dependencies(STAGING, …)`로도 얻는다. [YAGNI]

**m9.** 정적 HTML(freeze_design) 경로의 JS 조작 상태는 범위 밖이다(전제 공격 P6). 성공 조건 4의 «통과»를 «한계: 정적 경로는 조작 수집 비적용(사용자 결정 ① 범위 밖)»으로 바꿔 적는다. [일반화 △]

---

## 3. 검증됨 목록 (공격했으나 견딤)

**V1. `--declared`는 면제 필드가 아니다.** 설계 L41 «선언은 대상을 늘릴 뿐 줄이지 못한다» — 선언 대상의 identity는 매칭된 DOM에서 계산되고(L45) 실행 의무가 같다. 자기 초안 승인 경로가 아니다(단 M7의 교착은 별개).

**V2. `interaction_exclusions`의 `approval_quote` 신뢰 모델은 기존 `scope_refs`와 동일하다.** scope.md는 v1.1.7에서도 Coordinator가 «사용자 요구·구체 승인 원문과 출처를 보존»하는 서기 산출(L142)이고, 리뷰어가 감사하며, scope.md 바이트는 입력 digest·review_digest에 들어가(check_design_evidence.py L263~269·L195~201) 예외 행 추가 = design-input 변경 = 재검토 강제다. «자기가 쓰고 자기가 승인»이 아니라 «자기가 옮겨 적고 독립 리뷰어가 원문인지 감사»로, 기존 구조와 같다.

**V3. backstop 자동 반영.** `backstop.py` L243이 `validate_inputs(build, root)`를 그대로 호출한다 — v2 규칙이 G2·마무리 백스톱에 자동 편입된다(설계 L102 사실).

**V4. 새 `.mjs`·`.js`의 byte 미러 자동 포함.** Makefile L96~97의 `diff -rq`는 디렉터리 재귀라 확장자 무관(M10(a) 조건부).

**V5. `interactions.json`의 지위.** «Coordinator가 브라우저에서 실행 … 값은 쓰지 않는다»(L23)는 render-audit의 «기계 관찰 산출물 — 너는 값을 쓰지 않는다 — 동결·검증·대조 실행만»(dddjango-web.md L9·L231)과 동형이다. 경계 절 명기만 남는다(M10(c)).

**V6. 리뷰어의 읽기 전용·명세 미수정.** 소스 핸들러 감사는 `Read, Grep, Glob`(design-review-web.md L4) 범위이고 반환은 «입력 부족»뿐이다(L25·L57). 계획 L22·L94 항목 5와 일치한다. 되돌린 1.1.11 G0 문장(관련 상태를 case 확인 항목으로)은 재도입되지 않았다 — B2의 «독립 렌더» 문장만 문제다.

**V7. coder·G2·discipline-reviewer 무접촉의 기계적 성립.** coder 입장은 `--phase inputs` 실행(coder-web.md L44~45)이라 파일 변경 없이 v2 규칙을 상속한다. discipline-reviewer의 «raw API 응답/브라우저 관찰·캡처 생성 trace»(dddjango-web.md L181) 입력에 interactions가 자연히 포함된다. 다만 무접촉의 대가로 G2 대조 자체는 강화되지 않으며(B2·P1), 그 한계는 설계가 스스로 밝혀야 한다.

**V8. 사용자 결정 3건의 본문 반영.** ① 관찰 동결(§수집기)+재동결 대조(§`--compare`) ② 전수 실행·예외는 scope 승인만(L12·L100) ③ v1.1.7 기준선·미재도입 선언(L3·L124) — 모두 있다. 숨은 결정은 M4·M5·M8·M9로 별도 열거했다.

**V9. 1.1.12 «기존 화면 재개 입구»·1.1.11 «필수 반환 판형»·coder/architect/discipline 변경분은 재도입되지 않았다.** 설계 본문에 해당 문단이 없고 대상 파일 목록(L23~30)에도 없다.

**V10. 백스톱 WP의 `.mjs` 금지와 무충돌.** check_purity.py L156~158은 사용자 `web/static/js/` 대상이고 플러그인 `scripts/`는 그 검사 밖이다.

**V11. digest 편입 규칙.** interactions 바이트를 `observation/…` 항목으로 넣으면 기존 `_source_observation`의 trace 편입(L209·L238)과 같은 패턴으로 «바뀌면 prepare·독립 검토·inputs 재실행»(design-evidence.md L195~197)이 자동 성립한다.

**V12. archive 경로의 «manifest 하나·case 다수» 관례와 «여러 case가 같은 interactions.json을 가리킴»(L97)의 정합.** validate_inputs L288~289가 archive manifest 1개를 강제하고 case는 각자 포인터를 가지므로 공유 포인터는 스키마상 자연스럽다.

---

## 4. 한 줄 총평

**구현 진입 불가** — B1(스니펫 대상 규칙이 A8 스크림을 구조적으로 놓쳐 성공 조건 5 자기 위반)·B2(«case 내 변이» 리뷰어 재량 = 1.1.11 재도입이자 동결 축의 거짓 통과 통로)를 기계 규칙으로 바꾸고, M1(v1 이력 허용 폐기)·M2(MCP 대체 경로 삭제)·M3(`--compare`는 요청 시에만)·M4(`--carried` 폐기 또는 표식 보존)·M5(`_history` 절차의 출처 결정)·M8(Node/Playwright 정책 = 사용자 결정)을 «적대 검토 반영 — 확정 계약» 절에 채운 뒤 재검토하면 진입 가능하다.
