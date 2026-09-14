# rv-A — 웹 시안 조작 상태 증거 설계 초안 적대 검토(기술 렌즈)

- 검토 대상: `workspace/design/2026-09-13-web-interaction-evidence.md`(초안) · 진단 `workspace/eval/web-a8-interaction-observation/diagnosis.md`
- 검토 방법: 정적 읽기만(python3 텍스트 검색). 서버·브라우저·`make verify` 미실행. A8 산출물·`/tmp`는 읽기 전용. Serena·Graphify는 워크트리에 opt-in 표식(`.serena/project.yml`·`graphify-out/graph.json`)이 없어 사용하지 않았다.
- 실제 표본 근거 파일(경로 접두 `A8/` = `/Users/hyun/.herdr/worktrees/spring_dream_server/a8/.dddjango-web/20260912-1640-web-related-persons/`): `design-ref/관계인.dc.html`(479행) · `design-ref/_ds/chunmong-design-system-9ad494f0-e78e-410b-b52f-e515367f30e9/_ds_bundle.js`(3,402행 — 이하 «번들 N행») · `design-ref/support.js` · `captures/*-trace.json` 12 · `source-manifest.json` · `design-input.json` · `scope.md` · `build-state.json` · `screen-meta.json`.
- 3축 표기: **정합** = 현행 검사기·스키마·프롬프트 코퍼스와의 정합 / **일반화** = A8 밖 시안·엔진에서도 성립 / **무손실** = 커버리지·증거가 새거나 거짓 통과가 생기지 않음.

## 1. 전제 공격 — 진단 §4 원인 판정이 틀렸을 가능성

진단 §4의 원인 1~3(조작 집합 미정의 · 리뷰어 재량 · 재동결 기계 대조 부재)은 소스로 확인된다(`check_design_evidence.py` 234~238행은 trace가 «비어 있지 않은 바이트»인지만 보고, `archive_design.py`는 이전 manifest를 읽는 코드가 없다). 그러나 원인 목록이 **불완전**해서, 초안대로 구현하면 같은 거짓 통과가 기계 형식으로 재생산된다.

1. **누락 원인 A — «같은 이름·다른 문맥» 병합.** 진단은 «무엇을 조작했어야 하는지의 집합이 없다»고 했지만, 집합을 정의해도 집합의 **원소 동일성**이 잘못되면 같은 결과다. A8 원본은 «닫기»(관계인.dc.html 86행 상세 Dialog · 421행 폼 step1)·«다음»(422행, step1~3 공용)·«삭제하기»(89행 IconButton aria-label · 103행 위험 확인 버튼)를 문맥만 다르게 재사용한다. 초안의 identity(role·name·owner)는 이 셋을 각각 한 원소로 접는다. 결과는 §2 B1 — 폼 step 2~4·삭제 확인·시·군 153이 «전수 실행·잔여 0»으로 통과하면서 실제로는 한 번도 도달하지 않는다. 진단 §3의 «같은 핸들러의 데이터 변이로 제외»한 리뷰어 판정이 검사기의 identity 규칙으로 옮겨 앉는 셈이다.
2. **누락 원인 B — 신뢰 경계가 여전히 Coordinator 손에 있다.** 초안은 «기계 통과가 유일 근거»로 삼지만, 기계에 들어가는 입력 4가지가 전부 Coordinator가 정한다: `--root` selector(좁히면 대상이 0~1개), 스니펫 바이트(검사기가 대조하지 않음), `--compare`의 staging 내용(이전 보관본을 복사해 넣으면 전부 `same`), `scope.md`의 승인 인용문(스코프 메모는 Coordinator 직접 쓰기 목록 — `commands/dddjango-web.md` 9행·231행). v6 실패(진단 §2)의 직접 원인은 «부분 수집 뒤 단언»인데 `--compare`도 staging에 무엇이 들어왔는지는 모른다. §2 M6·M8·M9.
3. **진단 §1 «포털 없음»·«React가 런타임에 그린다»는 사실은 검증됨**(번들 전체에 `createPortal` 0회 · Dialog 1065~1090행이 `position:absolute; inset:0` div). 따라서 «루트 서브트리 ∪ 오버레이» 범위 규칙은 A8에서는 충분하다(§3 V3).
4. **진단 §3의 결론(프롬프트 순서 변경만으로는 불충분)은 타당하나, 프롬프트 규범을 버릴 근거는 아니다.** 초안 자체가 리뷰어에게 소스 핸들러 감사와 예외 진위 감사를 남긴다(초안 121행). 그러면 «같은 핸들러 면제 금지»는 여전히 프롬프트 문장으로 있어야 하는데 초안 §규범 연결에는 «기계 통과를 보증으로 해석하지 않는다»만 있고 면제 금지 문구가 없다(§2 m6).

## 2. 발견 목록(심각도 높은 순)

### B1. [BLOCKER · 무손실·일반화] 탐색 종결 규칙 + identity 규칙의 조합이 A8 폼 step 2~4·삭제 확인·시·군 153에 구조적으로 도달하지 못한다

근거:
- 초안 59행: «I′의 **새 identity**를 경로+[이 조작]으로 큐에 추가» — 큐의 키가 identity뿐이다. 45행: name은 «aria-label → aria-labelledby → label → 자기 텍스트», owner는 «가장 가까운 menu/listbox/dialog/radiogroup 조상».
- A8 Dialog는 role·aria-modal이 없다(번들 1065~1090행: 스크림 div는 `style`+`onClick: onCancel`, 카드 div는 `onClick: e => e.stopPropagation()`+`rest`; 관계인.dc.html 86·103·107행의 x-import도 role을 넘기지 않는다). 따라서 A8의 모든 다이얼로그 안 대상은 owner가 비어 있다.
- Select의 트리거 button은 `<label htmlFor={uid}>`와 `id: uid`로 묶인다(번들 2960~3000행·Dropdown 2780~2787행 `_extends({...}, rest)`). 초안 규칙상 label이 자기 텍스트보다 우선이므로 «관계»·«태어난 시»·«시 · 도»·«시 · 군» 트리거의 name은 선택값과 무관하게 **상수**다.
- BFS 추적(DOM 순): I0 = [뒤로, 행 김서연·이하람·박도윤·정우재, 관계인 등록하기]. 행 김서연 → 상세: 새 대상 {삭제하기(IconButton), 닫기, 수정하기} 큐 추가. 나머지 행 → 같은 identity라 추가 없음. 등록하기 → step1: {관계 트리거, 이름, 여자, 남자, **다음**} 추가(«닫기»는 상세의 것과 같은 identity라 미추가). 수정하기(경로 [행 김서연]) → 편집 step1: 전부 이미 본 identity → **추가 없음**. «다음»(경로 [등록하기]) → 빈 폼이라 오류 문구(대상 아님) → 추가 없음. 삭제하기(IconButton, 경로 [행 김서연]) → 위험 확인 Dialog: «취소»만 새 identity, 확인 버튼 «삭제하기»는 IconButton과 role=button·name «삭제하기»로 **같은 identity** → 미추가. 큐 소진 → 종료.
- 결과: step 2~4(생년월일·역법·윤달·태어난 시 12·시·도 17·시·군 153)·실제 삭제·토스트가 한 번도 실행되지 않은 채 잔여 0. 초안의 성공 조건 5(«드롭다운 항목·체크박스·스크림을 발견·실행하고 잔여 0»)와 A8 실증 2(oracle 30/8/12/17/153 대조)는 그대로 구현하면 성립하지 않는다. 검사기 잔여 집합도 같은 identity 단위라 이 누락을 볼 수 없다 — «전수 실행»이 기계 판정으로 거짓 통과한다.
- 반대로 단순히 «상태마다 다시 실행»으로 바꾸면 값 조합(관계 8×이름 2×성별 2×…×시·도 17×시·군 153)이 큐를 키운다(초안이 «identity가 값에 독립»이라 전제한 이유). 두 극단 사이의 실행 키가 초안에 없다.

권고(구현 전 필수):
- 실행 키를 `(identity, action[, option], context)`로 정의하고 `context`를 명시한다. A8를 통과하면서 폭발하지 않는 후보: context = 현재 인벤토리의 **정렬된 identity 집합 + 각 select/combobox 트리거의 face 텍스트 + 각 checkbox/radio의 checked + 각 텍스트 입력의 «비어 있음/아님» 2값**(자유 텍스트 값 자체는 제외). 이 키로 등록 step1(이름 빈값)과 편집 step1(이름 채움)이 갈라져 «다음»이 편집 경로에서 실행되고, 시·도 17 선택마다 «시 · 군» 트리거가 별개로 열린다. 자유 텍스트를 제외하므로 fill 값 조합은 열거되지 않는다.
- 검사기의 잔여 집합도 같은 키로 계산한다(«어느 context에서든 enabled로 관찰된 (대상, 조작)» − executed). 단 잔여의 단위를 (identity, action)으로 두면 B1이 그대로 남으므로 context를 잔여 단위에 넣을지, 아니면 «관찰된 모든 context에서 최소 1회»로 둘지를 초안이 결정해야 한다.
- 초안 §검증 순서 앞에 «A8 원본에 대한 큐 시뮬레이션(드라이런) 결과 표(발견 대상 수·실행 수·도달 상태)»를 넣고, 30/8/12/17/153에 못 미치면 구현에 들어가지 않는다.

### B2. [BLOCKER · 정합·일반화] 실행 환경 계약이 성립하지 않고, MCP 대체 경로는 «같은 형식»을 보장하지 못한다

근거:
- 저장소·플러그인 설치본 어디에도 `playwright` 모듈이 없다(`/Users/hyun/Desktop/dddjango/node_modules`·`package.json` 부재 확인). 이 머신에서 유일한 모듈은 `~/.npm/_npx/9833c18b2d85bc59/node_modules/{playwright,playwright-core}` — MCP 플러그인의 `.mcp.json`(`npx @playwright/mcp@latest`)이 만든 npx 캐시로, 버전이 바뀌면 경로가 바뀐다. 초안 130행의 «프로젝트 로컬 설치 또는 `npx playwright`»에서 `npx playwright`는 CLI 실행이지 `observe_interactions.mjs`의 `import 'playwright'`를 해결해 주지 않는다. 사용자 프로젝트(A8)에 npm 설치를 요구하는 것은 «사용자 앱은 수정하지 않는다»(초안 19행)와 충돌한다.
- 초안 93행: «MCP Playwright로 대체 실행해도 같은 스니펫을 `evaluate`로 실행해 같은 형식을 내야». 그러나 탐색 루프(새로고침·경로 재생·실제 click/fill/press·안정 대기·저장)는 스니펫이 아니라 **드라이버**에 있다(초안 57~60행). MCP `browser_evaluate`로는 페이지 안 스니펫만 돌릴 수 있어, 수백 step의 루프를 Coordinator(LLM)가 tool call로 흉내 내고 `interactions.json`을 손으로 조립하게 된다 — 초안 93행이 금지한 «산문 로그 → 구조화 기록» 경로가 그대로 열린다.

권고:
- 드라이버를 `async (page, options) => {...}` **단일 함수 파일**(예: `assets/observe_interactions.pw.js`)로 쓰고, ① Node 경로 `observe_interactions.mjs`는 이 파일을 import해 실행, ② MCP 경로는 `browser_run_code_unsafe`의 `filename` 인자로 **같은 파일**을 실행한다(이 도구는 `page`를 인자로 Playwright 코드를 실행하며 파일 로드를 지원한다 — 스키마 확인). `collector.driver`에 두 경로 모두 이 파일의 sha256을 기록하고 검사기가 플러그인 자산과 대조한다(M6).
- Node 경로의 모듈 해결은 `--playwright-module <dir>` 또는 `NODE_PATH`를 규범에 명시하고, 실패 시 «SKIP이 아니라 exit 1 + 필요한 설치 명령»을 출력한다.

### M1. [MAJOR · 무손실·일반화] leaf 규칙이 사용자가 지목한 «스크림»을 열거에서 빼고, 완화하면 «executed·무변화» 거짓 실행을 만든다

근거:
- 초안 39행: «클릭 핸들러가 붙은 leaf(… 하위에 다른 대상이 없는 요소)». A8 스크림 = Dialog 최외곽 div(`onClick: onCancel`, 번들 1080행)로 하위에 버튼·입력 등 대상이 다수 → leaf가 아니라 제외된다. 진단 §1이 «보지 않음»으로 꼽은 스크림 클릭이 초안에서도 열거되지 않는다.
- leaf 조건을 «핸들러 있으면 대상»으로 완화하면 카드 div(`onClick: e => e.stopPropagation()`, 1082행)도 대상이 된다. 더 큰 문제는 클릭 지점이다: Playwright의 기본 클릭은 요소 rect 중심이며, 스크림 중심은 카드(자손)가 덮고 있다. 자손이 hit target이면 Playwright는 클릭을 진행한다(추측 — actionability의 hit-target 규칙) → 카드가 전파를 끊어 `onCancel`은 호출되지 않는데 step은 `executed`·변화 없음으로 기록된다.

권고: 핸들러 보유 요소는 하위 대상 유무와 무관하게 대상으로 등록하고, 클릭 지점 규칙을 둔다 — 요소 rect에서 하위 대상 rect에 덮이지 않는 점(A8 스크림은 카드 maxWidth 320 밖 좌우 35px 여백이 있다)을 고르고, 그런 점이 없으면 `status: unreachable-point`로 기록해 실행으로 세지 않는다. 오버레이 인식은 M2와 함께 구조 규칙으로.

### M2. [MAJOR · 일반화·무손실] 오버레이 인식·«닫기 대상(Esc)»·owner가 전부 role에 의존하는데 A8 Dialog에는 role이 없다

근거: 번들 안 `role:` 부여는 progressbar·status·radiogroup·radio·menu·menuitem뿐(1212·1265·1309·1402·1571·1610·1827·1840·1889·2831·2889행). Dialog(1065행)·BottomSheet(982행)·Toast 컨테이너에는 dialog/alertdialog/aria-modal이 없다. 따라서 초안 38·40·45행의 오버레이 열거·Esc 대상 등록·owner 산출이 A8 다이얼로그에서 전부 빈값이다. Dropdown 메뉴만 role=menu(2831행)라 Esc 대상이 된다. 참고로 A8 Dialog는 Escape 처리 자체가 없어(번들·HTML 어디에도 keydown 없음) Esc를 눌러도 아무 일이 없다 — 그 «무변화»가 기록되는 것은 정상이지만, 대상 자체가 열거되지 않으면 기록도 없다.

권고: 오버레이를 구조로도 인식한다 — «루트 rect의 80% 이상을 덮는 `position: absolute|fixed` 요소로서 핸들러를 갖거나 z-index가 형제보다 큰 것». 인식 실패는 `--declared`로 닫되, 초안 41행의 «선언은 대상을 늘릴 뿐» 원칙을 유지한다. 리뷰어 G0의 소스 감사 대상 목록에 «role 없는 오버레이 컴포넌트(Dialog·Sheet)»를 명시한다.

### M3. [MAJOR · 무손실·정합] Checkbox·Switch·Radio의 checked 상태를 관찰할 수 없어 «관찰된 checked 상태마다 click» 규칙이 1회로 퇴화하고, 인벤토리 스키마가 상태별 enabled/checked를 담지 못한다

근거:
- 번들 Checkbox(1454~1520행)·Switch(1923행~)·Radio(1752행~)는 `<label onClick>` + 장식 span으로, `input`·role·aria-checked가 없다. 상태는 배경색·check 아이콘 자식뿐이다. 초안 67행의 «false·true 둘 다 관찰됐으면 2회»는 계산 불가 → «윤달에 태어났어요»·«태어난 시간을 몰라요»·«태어난 곳을 못려요»는 1회 클릭으로 끝나고 역방향 토글(진단 §3이 누락으로 지적한 항목)이 실행되지 않는다. ChoicePair만 `role=radio`·`aria-checked`가 있다(1610~1614행).
- 초안 84행 스키마는 `targets[id].enabled` 단일값이고 `steps[].before/after.inventory`는 id 목록이다. «어느 인벤토리에서든 `enabled:true`로 관찰된 대상»(99행)은 인벤토리에 per-entry enabled가 없으면 계산할 수 없다. A8에서 «태어난 시» Select 트리거는 몰라요 체크 뒤 같은 identity로 disabled가 된다(관계인.dc.html 135행 `disabled="{{ fHourUnknown }}`).

권고: 인벤토리 항목을 `{id, enabled, checked|null, face|null, value_empty|null}`로 바꾼다. checked를 읽을 수 없는 토글형 대상(label/div 핸들러)은 «click 뒤 state_hash가 바뀌고 인벤토리 identity 집합이 같으면 같은 대상을 새 context로 1회 더 enqueue(왕복 탐침)»를 규칙으로 두고, 그래도 부족하면 `--declared`에 `states: 2`를 선언하게 한다. B1의 context 정의에 checked/face가 들어가면 이 규칙과 자연히 합쳐진다.

### M4. [MAJOR · 무손실·일반화] `cursor:pointer` leaf 규칙은 상속 때문에 대상을 2~3배 부풀리고 이름 없는 아이콘을 dom_path identity로 만든다

근거: `cursor`는 CSS 상속 속성이다. Button(번들 500행대)·IconButton(650행대)·ListRow(«cursor: tappable ? 'pointer' : 'default'»)·Checkbox label·menuitem 전부 pointer이므로 그 안의 텍스트 span·`<i class="icon-…">` leaf의 computed cursor도 pointer다. 초안 39행 규칙대로면 «다음» 버튼 안 텍스트 span, 행 안 이름·부제 span, 아이콘 i가 각각 대상이 된다. 텍스트 leaf는 이름이 같아 identity가 부모 버튼과 다르게(role 빈값) 잡히고, 아이콘은 이름이 비어 dom_path가 identity에 들어간다(45행) — 렌더 순서·조건부 아이콘(선택 표시 check 아이콘, 번들 2925행)이 바뀌면 nth-of-type이 밀려 `unreachable`이 난다.

권고: 요소 자신의 cursor가 부모의 computed cursor와 다를 때만 leaf 후보로 삼고, 이미 대상인 조상을 가진 요소는 제외한다. `aria-hidden` 자손은 열거하지 않는다.

### M5. [MAJOR · 정합] 잔여 집합·exact-field·순번 접미·state_hash가 결정적으로 코드화될 만큼 정의되지 않았다

근거·구멍:
- 잔여 원소의 키가 «(대상, 조작[, 옵션/상태])»(99행)로만 적혀 있다. native select의 옵션 키(value? label?), checkbox의 «상태»(before checked), 오버레이 Escape의 대상 id가 무엇인지, 선언 대상의 action이 무엇인지 미정.
- exact-field(98행)가 `targets[*]`·`steps[*]`·`before/after`·`changes`·`changes.values[*]`까지 재귀하는지 미정. 반례 목록(128행)의 «알 수 없는 필드(`exempt` 등)»는 어느 깊이인지 없다 — `steps[i].exempt`가 통과하면 작성자 면제 필드 차단이 무의미하다.
- 순번 접미(45행)를 인벤토리마다 다시 매기면 앞 항목이 사라진 인벤토리에서 뒤 항목이 `#1`로 이동해 identity가 바뀐다 → 재생 실패·중복 대상.
- `state_hash`(59·86행)의 입력이 정의되지 않았다(DOM 직렬화? 텍스트? 스타일?). 정의에 따라 토스트(2.6초 타이머, 관계인.dc.html 255행)나 hover 상태가 해시를 흔든다.
- 검사 항목에 없는 모순 케이스: `partial:false`인데 `caps_hit≠[]` · `status:executed`인데 `error≠null` · `steps[].path`가 가리키는 대상이 이전 step에서 실행된 적이 없음 · `targets[id].enabled:false`인 대상에 executed step · 같은 `n` 중복 · `observed_at`이 archive 파일 mtime보다 앞섬(참고용) · `viewport`가 case viewport와 다름(m3).

권고: 잔여 키를 표로 고정(대상 id · action ∈ {click, fill, focus, blur, select, key:Escape} · option = select 옵션 value / checkbox before-checked / 없음). exact-field는 «모든 객체 재귀». 순번 접미 대신 충돌 시에만 dom_path를 identity에 포함. state_hash = 루트 서브트리의 (tag, role, name, enabled, checked, face, value_empty) 목록 sha — `role=status`·`aria-live` 서브트리 제외. 위 모순 케이스를 반례 테스트에 추가.

### M6. [MAJOR · 무손실·정합] 검사기가 스니펫·드라이버 바이트와 `--root`를 검증하지 않아 두 개의 손쉬운 거짓 통과 통로가 남는다

근거:
- 초안 93행: «수집기 hash는 버전·동일성 표시이며 인증이 아니다». 검사기가 `collector.snippet_sha256`을 자기 `assets/interaction_audit.js`와 대조하지 않으면, 스니펫을 고쳐(대상 조건 축소) 실행한 결과가 그대로 통과한다. 플러그인은 자기 자산 경로를 안다(`check_design_evidence.py`는 `Path(__file__)` 기준 형제 스크립트를 import한다, 19~22행) — 대조 비용은 0이다.
- `root.selector`는 Coordinator 인자다(초안 38행). `--root '[data-screen-label="관계인"] > span:first-child'` 같은 좁은 루트를 주면 대상 0~1개·steps 1건·잔여 0으로 통과한다. 검사기는 `root.found`만 본다(98행).

권고: 검사기가 ① `collector.snippet_sha256`·드라이버 sha를 플러그인 자산 바이트와 byte 대조(불일치 exit 2), ② `root.selector`가 `[data-screen-label="<label>"]` 형식이고 `<label>`이 case entrypoint 바이트에 실제로 존재하며 `screen-meta.json.screen_label`(A8: «관계인»)과 같은지 대조한다(extract_dc의 선택 기준과 동일 — `extract_dc.py` 110·131행). data-screen-label이 없는 원본은 `--root`를 `--declared`처럼 리뷰어 감사 대상으로 명시한다.

### M7. [MAJOR · 정합·무손실] v1 허용 조건(`build-state.json`의 `phase: finalize`·`g2_approved`)은 Coordinator가 쓰는 파일에 결합돼 우회 가능하고, 실제로는 거의 만족되지 않아 모든 과거 build를 깨뜨린다

근거:
- `build-state.json`은 Coordinator 직접 쓰기 목록에 있다(`commands/dddjango-web.md` 9행·231행). 두 필드를 써 넣는 것만으로 v2 의무가 풀린다.
- `phase: finalize`는 스키마 주석(같은 파일 50행 «scope | design | implement | finalize»)에만 있고 갱신 시점 목록(74행)에는 `phase=scope·design·implement`만 있다 — finalize를 기록하라는 시점이 없다. A8 실측: G2 시각 검증·visual-evidence까지 끝난 상태에서 `phase=implement`·`g2_approved=false`·`design_status=ready`(build-state.json 상단 값). 즉 «완료 이력의 v1 허용»이 실무에서는 거의 발동하지 않는다.
- `backstop.py`는 `--design-build` 없이 실행되면 프로젝트의 **모든** source-bearing build를 `validate_inputs`로 검사한다(54~87행·220~247행). v2를 검사기에 넣는 순간, 사용자 프로젝트의 과거 build(A8의 `_history/v1~v4` 형제 폴더 포함 — `.dddjango-web/*/design-input.json` 마커로 발견)가 전부 exit 2가 된다. `current_nondesign_scope`(95~130행)의 예외도 같은 finalize 조건이라 구제하지 못한다.

권고: 이력 인정을 Coordinator 필드가 아니라 **git**에 앵커한다 — 예: «v1 observation은 그 build의 `design-input.json`·observation 바이트가 `--diff-base`(또는 HEAD) 조상 커밋에 동일하게 존재할 때만 허용」(backstop은 이미 `git show`·`ls-tree`로 이력을 읽는다, 39~52행). 최소한 «현재 build» 판정을 phase가 아니라 «`--phase prepare`를 실행하는 build»로 두고, backstop의 과거 build 검사에서는 v1을 warning으로 통과시킨다. 어느 쪽이든 «과거 build 전부 재관찰 강제»가 아님을 테스트로 고정한다.

### M8. [MAJOR · 무손실] `interaction_exclusions.approval_quote`의 «scope.md 원문 대조»는 Coordinator 자기 인용이라 검증력이 없다

근거: `scope.md`는 Coordinator가 쓰는 스코프 메모다(9행). 초안 100행의 «리뷰어가 실제 사용자 승인인지 감사한다»는 리뷰어가 transcript를 보지 못하므로 수행 불가 — A8 `coverage-review.md`도 «해시 재계산 도구가 없어 기록값 상호 대조로 판정」했다고 스스로 적는다. 와일드카드 금지는 유효하지만, 행 단위 예외를 Coordinator가 승인문까지 써서 채우는 것을 막는 장치가 없다.

권고: 예외를 없앨 수 없다면 노출을 강제한다 — 검사기가 `prepare/inputs` 성공 출력에 예외 전량(대상 name·action·인용문)을 stdout으로 출력하고, Coordinator 규범이 그 출력을 G0 배너 항목으로 사용자에게 재확인시키며, `visual-check.md` ①에 예외 수를 적게 한다. 인용문은 NFC·공백 정규화 뒤 비교, `scope_ref` 앵커 실존 검사, 예외 수 상한(예: 대상 수의 10%).

### M9. [MAJOR · 무손실·정합] `--compare`는 staging 출처를 모르고, carried-only 라운드가 영구 exit 3이라 «carried뿐이니 동일» 해석 통로가 생긴다

근거:
- 초안 112행: `--carried`는 «이전 보관본을 그대로 옮긴 파일». 즉 staging에 이전 바이트를 넣는 절차가 이미 규범 안에 있다. 이전 보관본 **전체**를 staging에 복사하고 `--carried`를 생략하면 sha가 전부 같아 `same`·exit 0 — 원격 확인 0으로 «동일»이 나온다. 이것이 v6(진단 §2 10:27~12:22)의 «일부만 받고 동일 단언»의 도구판이다. 도구는 바이트만 보므로 이를 막을 수 없다.
- A8의 정상 결과가 «same 18·carried 4·exit 3»(초안 137행)이다. 4개 PNG(`assets/logo.png` 1.3MB 등, source-manifest.json files 행)는 DesignSync 256KiB 한도로 매번 carried다 → 재동결할 때마다 exit 3. 초안 114행은 «차이가 있으면 … 재관찰」이라 하는데 carried-only가 «차이»인지 미정 → Coordinator가 «carried는 미확인일 뿐이니 동일」로 읽으면 exit 3의 의미가 사라진다.
- 현행 흐름과의 충돌은 없다(§3 V7).

권고: exit를 분리한다 — 0 = 전부 same / 3 = changed·added·removed 있음 / 4 = changed 없음·carried 있음(미확인). 4의 처분(재관찰 불요·보고에 «미확인 N파일» 명시·«동일» 단어 금지)을 규범에 쓴다. 출처 문제는 도구가 증명할 수 없음을 초안에 명시하고 최소 방어만 둔다: staging 파일 mtime이 실행 시각−N시간보다 오래되면 `--carried`에 없는 한 exit 1, 출력에 파일별 크기·sha 앞 12자·mtime을 표로 남겨 transcript에서 대조 가능하게 한다.

### M10. [MAJOR · 무손실·일반화] 문서 이탈(navigation)이 정의되지 않아 «루트 미발견은 실패» 규칙과 충돌하거나 범위가 다른 화면으로 번진다

근거: «뒤로» IconButton은 `history.back()` 또는 `location.assign('설정.dc.html')`(관계인.dc.html 258~261행), 설정.dc.html의 행 4개는 `location.assign(...)`으로 다른 .dc.html로 간다. 초안 38행 «루트 미발견은 실패», 59행은 URL 변화를 기록만 한다. 이탈 뒤 인벤토리를 뜨면 (a) 새 문서에 `[data-screen-label="관계인"]`이 없어 실패하거나 (b) 있을 경우(설정→관계인) 다른 화면의 대상이 큐에 들어가 범위가 번진다.

권고: step 실행 뒤 document/URL이 바뀌면 그 step은 `after: null`·`navigated: <url>`로 기록하고 enqueue하지 않는 «터미널 step»으로 정의한다. Playwright 새 컨텍스트에서 `history.back()`은 about:blank로 가므로(추측) 같은 규칙에 걸린다.

### M11. [MAJOR · 정합] Playwright 부재 시 «SKIP + exit 0» 정책은 저장소 검증에서 DOM 탐색 코드를 영구 미실행으로 만든다

근거: `run_fixtures.sh`는 fixture 스크립트의 exit만 집계한다(14~16행). 새 `fixtures_interactions.sh`가 SKIP을 exit 0으로 내면 `make verify-web`은 green이다. 현재 저장소에는 Playwright가 없으므로(B2) 열거·탐색 로직은 어떤 검증에서도 돌지 않는다. 초안 130행은 이를 «실패로 세지 않는다»로 굳힌다.

권고: 순수 함수(이름 정규화·identity·context·잔여 계산의 JS판)는 node만으로 항상 실행. DOM fixture 테스트는 `DDDJANGO_WEB_PLAYWRIGHT_MODULE`이 잡히면 실행·아니면 «SKIP + 사유 + exit 0»이되, `make release-web` 직전 단계에서는 SKIP을 실패로 취급한다(릴리즈 머신에서 최소 1회 실행 보장). 검사기(Python) 쪽 반례는 Playwright 없이 고정 JSON으로 전부 돌게 한다.

### m1. [MINOR · 일반화] React 런타임이 archive 밖(unpkg)이라 수집 실행이 네트워크에 의존하고 `--compare`가 런타임 drift를 못 본다

근거: `support.js`의 `REACT_URL = "https://unpkg.com/react@18.3.1/..."`·`loadReactUmd()`. trace 12건도 «unpkg UMD, auto-loaded»로 기록. 오프라인·차단 환경에서는 «DS 마운트» 대기가 타임아웃한다. 권고: 드라이버가 외부 스크립트 로드 실패를 별도 오류 코드로 기록하고, 검사기는 `partial`과 구별해 «환경 오류»로 exit 1을 내게 한다.

### m2. [MINOR · 정합] digest 항목 중복·`--declared` 누락

여러 case가 같은 `interactions.json`을 가리키면(초안 97행) `canonical_digest`에 같은 (name, bytes)가 여러 번 들어간다 — 결정적이긴 하나 명시하고 dedupe하는 편이 낫다. `--declared` JSON은 digest에 넣는다는 문장이 없다 — 선언 목록이 바뀌어도 독립 검토가 무효화되지 않는다.

### m3. [MINOR · 무손실] `interactions.viewport`와 case viewport의 관계가 미정

AppFrame은 `useIsDesktop`으로 반응형 분기를 한다(번들 AppFrame 도입부). viewport가 다르면 대상 집합이 다르다. 검사기는 `viewport == case.viewport`를 요구하거나, 여러 viewport case는 viewport별 파일을 요구해야 한다.

### m4. [MINOR · 무손실] fill 표본 «검증 입력»은 숫자 전용 입력에서 무효 값이다

`onDate`는 비숫자를 제거한다(관계인.dc.html 447행) → 생년월일 fill은 빈값으로 남고 등록 경로의 step2 «다음»은 항상 오류다. 커버리지용 fill이라 허용되지만, «값 변화 없음»도 executed로 세는 점을 규범에 적고, `inputmode=numeric`·`type=number`는 숫자 표본을 쓰게 한다.

### m5. [MINOR · 정합] 리뷰어 프롬프트에 «같은 핸들러 면제 금지» 문장이 없다

초안 121행은 «기계 통과를 보증으로 해석하지 않는다»뿐이다. 진단 §3의 실패 형태(«같은 핸들러의 데이터 변이로 제외»)를 직접 금지하지 않으면 리뷰어 감사 부분에서 재발한다. 현행 `agents/design-review-web.md` 21~25행에도 해당 문장이 없다.

### m6. [MINOR · 무손실] 비용·상한 추정(추측)

초안 규칙대로면 큐 ≈ 30건에서 종료(B1). B1 권고 키로 바꾸면 A8 추정: 메뉴 항목 8+12+17+153 = 190 · 트리거·버튼·토글·입력 ≈ 100 · context별 «다음/저장하기» 재실행 ≈ 150~200 → 큐 ≈ 450~500건, 평균 경로 깊이 5~9 → 브라우저 조작 ≈ 4,000회. 조작당 클릭+250ms 정적 대기 ≈ 0.4s, 새로고침당 0.5~1s → 총 25~40분. `--max-steps 3000`·`--max-depth 12`(A8 최장 경로 9)는 충분하지만 **총 소요 상한이 없다**(대상당 10s × 500 = 83분까지 가능). 총 wall-clock 상한을 `caps_hit`에 추가하고, 재생 비용은 «현재 상태의 state_hash가 기록된 경로 접두 상태와 같으면 새로고침 생략» 정도의 결정적 최적화만 허용한다.

## 3. 검증됨(공격했으나 견딘 항목)

- **V1 `__reactProps$*` 휴리스틱이 A8 핸들러에 실제로 걸린다.** 스크림 div `onClick: onCancel`(번들 1080행) · 카드 div `onClick: stopPropagation`(1082행) · ListRow div `onClick`(3030행대) · Checkbox/Switch/Radio `label onClick`(1470·1940·1762행) · ChoicePair `button role=radio aria-checked onClick`(1610~1614행) · Dropdown 트리거 `button onClick`(2780~2787행)·`menuitem button onClick`(2889~2892행) · Toast action `button onClick`(1430행) — 전부 host element prop이라 DOM 노드에 붙는다. (`__reactProps$` 키 이름 자체는 archive 밖 React 18.3.1 UMD의 관례 — 추측 표기.)
- **V2 루트 selector.** `[data-screen-label="관계인"]`은 원본 37행에 있고 `screen-meta.json.screen_label`과 같다. `support.js`는 dom 요소의 `data-*`를 보존하며(kebab→camel 변환은 x-import 한정) `<x-dc>`를 `#dc-root`로 치환해 인스턴스가 하나다 → 검사기 대조(M6 권고)가 가능하다.
- **V3 포털 없음.** 번들 전체 `createPortal` 0회. Dialog·메뉴는 루트 서브트리 안에 그려진다 → «루트 서브트리 ∪ 오버레이» 범위는 A8에서 충분(오버레이 합집합은 다른 엔진용).
- **V4 재생 결정성.** 원본·번들에 `Math.random`·`setInterval`(DS 마운트 폴링 80ms만)·타이머(토스트 2.6s만) 외 비결정 요소가 없고 `Date.now()`는 저장 id 생성 1곳(관계인.dc.html 284행 — identity에 안 들어감). `motion.css`는 `prefers-reduced-motion: reduce`에서 전 duration 0ms → 안정 대기가 짧다. 따라서 «비결정 원본의 unreachable 양산」 질문은 A8에서는 발생하지 않는다.
- **V5 데이터 행 삭제 뒤 identity 이동 없음.** 행 이름은 사람 이름+부제 텍스트라 서로 다르고 순번 접미가 필요 없다.
- **V6 메뉴 Esc·바깥 클릭.** Dropdown은 document `keydown Escape`·`mousedown away`를 처리한다(번들 2731~2755행). 표의 «오버레이 Esc 1회»는 메뉴에 유효하고, Playwright click은 mousedown이 선행하므로 바깥 클릭 닫힘은 별도 조작 없이 다음 step에서 자연 발생한다(한 step에 두 효과 — 기록은 changes로 남는다).
- **V7 `--compare`와 현행 `archive_design` 흐름의 충돌 없음.** compare는 새 `--out`에 보관을 마친 뒤의 manifest 대조이므로 `output inventory differs`(155~156행)·`destination collision`(asset_io 170~172행)·missing exit 1(176~181행)과 독립이다.
- **V8 review_digest 순환 없음·backstop 자동 반영.** `review_digest`는 `design-input.json`과 coverage_review 파일만 제외한다(195~201행); `interactions.json`을 `observation/…` 항목으로 넣어도 순환이 없다. backstop은 `validate_inputs`를 그대로 호출한다(30·243행) — 단 M7의 이력 문제를 같이 끌고 온다.
- **V9 depth 상한.** A8 최장 경로 = [행, 수정하기, 다음, 다음, 다음, 시·도 트리거, 시·도 항목, 시·군 트리거] + 항목 = 9 < 12. B1 권고 키로 바꿔도 깊이는 같다.
- **V10 이미지 단독·정적 HTML 무영향.** v2 의무는 `archive_entries`로 판별된 case에만 붙는다(`validate_inputs` 380~392행 분기) — 정적 manifest·이미지 case는 `_source_observation`에 들어오지 않는다.
- **V11 identity 값 독립.** label 우선 name 규칙 덕에 Select 트리거·Input은 값이 바뀌어도 identity가 같다 — 값 조합 폭발은 막힌다(그 대가가 B1).

## 4. 총평

**현재 초안으로는 구현 진입 불가.** B1(실행 키가 identity뿐이라 A8 폼 step 2~4·삭제 확인·시·군 153에 도달하지 못하면서 잔여 0으로 통과)과 B2(드라이버가 resolve 안 되는 모듈에 기대고 MCP 대체가 같은 코드가 아님)는 성공 조건 2·5를 그대로 깨뜨린다. 진입 조건: ① B1의 실행 키·context 정의를 확정하고 A8 드라이런 표(발견·실행·도달 상태 ≥ 30/8/12/17/153)를 초안 §확정 계약에 넣는다, ② 드라이버를 `(page, opts)` 단일 파일로 두어 Node·MCP가 같은 바이트를 실행하게 하고 검사기가 그 sha와 `--root`를 대조한다(B2·M6), ③ M1~M3(스크림·role 없는 오버레이·checked 미관찰)을 열거 규칙에 반영한다, ④ M7의 v1 이력 인정을 git 앵커로 바꿔 과거 build 전멸을 막는다, ⑤ M9의 exit 분리와 carried-only 처분을 규범에 쓴다. 나머지 MAJOR(M4·M5·M8·M10·M11)는 구현 착수 전 명세 문장으로 닫을 수 있다.

## 요약

- 발견 20건: BLOCKER 2 · MAJOR 11 · MINOR 6 · 검증됨 11(별도).
- BLOCKER: B1 탐색 종결 규칙+identity 조합의 구조적 미도달(폼 step 2~4·삭제 확인·시·군 153) · B2 실행 환경 계약 부재와 MCP 대체 경로의 비동등.
- MAJOR: M1 스크림 leaf 제외/거짓 실행 · M2 role 의존 오버레이·owner · M3 checked 미관찰·인벤토리 스키마 · M4 cursor 상속 오탐 · M5 잔여·exact-field·접미·state_hash 미정의 · M6 스니펫·root 미검증 통로 · M7 v1 허용의 build-state 결합(finalize 미기록·과거 build 전멸) · M8 approval_quote 자기 인용 · M9 `--compare` 출처·carried-only exit 3 · M10 navigation 미정의 · M11 SKIP 정책.
