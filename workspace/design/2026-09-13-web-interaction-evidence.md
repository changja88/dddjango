# 웹 시안 조작 상태 증거와 재동결 기계 대조 설계

상태: v2 — 독립 적대 검토 3기(rv-A 기술·rv-B 규범·rv-C 증거)와 재검토(rv-R)를 반영한 통합본. 검토 원문과 v1 초안은 `workspace/eval/web-a8-interaction-observation/design-review/`에 있다(`design-v1-reviewed.md` = 검토 시점 초안). rv-R 총평대로 R1~R10을 문장으로 닫았고 앞 절과 계약의 충돌(R18)은 통합으로 없앴다. 구현 진입은 K8 사용자 결정 뒤 K1 드라이런 게이트에서 시작한다.

사용자 결정(2026-09-13): ① 범위 = 관찰 동결 + 재동결 대조 ② 발견된 조작 대상은 전수 실행(예외는 scope.md 사용자 승인만) ③ 기준선 = 작업 트리의 v1.1.7 내용(1.1.8~1.1.12 프롬프트 누적은 재도입하지 않는다). 계획·구현·커밋·릴리즈는 별도 승인이다.

## 근거와 성공 조건

A8(진단 §1~§2): 시안의 다이얼로그·드롭다운은 `_ds_bundle.js`의 React 컴포넌트가 런타임에 그리는데, 동결 관찰 12 case는 전부 정적 `sc-if` 분기 상태였고 다이얼로그 안 조작(Select 열림·체크박스·focus·스크림·Esc)은 어느 trace에도 없다. 증거 검사기는 trace가 비어 있지 않은지만 보고, 독립 리뷰어는 «같은 핸들러» 면제로 pass를 냈다. v6 재동결 대조는 화면 HTML 1파일만 보고 «차이 0»을 단언했고, 토큰 11개가 무변이라는 이유로 번들도 «사실상 무변»이라 추론했으며, 사용자가 드롭다운을 지목한 뒤에야 번들을 해시했다. Coordinator는 JS를 «안 본» 것이 아니라(v3 재동결 때 번들 diff까지 읽었다) JS가 그리는 상태를 관찰 의무로 바꾸는 규칙이 없었다. 그래서 «소스를 읽고 판단하는» 리뷰어 감사는 폐쇄 장치가 될 수 없고, 프롬프트 보강은 세 번 실패했다(진단 §3).

성공 조건:

1. 원본 엔진/JSX archive(`collection=archive`) case는 기계가 수집한 조작 기록(`interactions.json`) 없이 `design_status=ready`가 되지 않는다. 정적 수집 경로(`freeze_design`·이미지 단독)는 이번 범위 밖이며 «한계» 절에 적는다.
2. 어느 상태에서든 활성으로 관찰된 조작 단위 − 실행된 단위 = ∅가 아니면 `--phase prepare/inputs`가 exit 2다. 작성자 면제 필드는 없다. 예외는 `design-input.json`의 `interaction_exclusions`가 가리키는 scope.md 사용자 승인 원문뿐이며 검사기가 stdout으로 전량 노출한다.
3. 조작으로 새 표면이 드러난 상태는 표면 키마다 case(드라이버가 저장한 캡처) 또는 예외 행으로 동결된다. «같은 핸들러·데이터 변이»라는 이유의 면제는 기계 규칙에 없다.
4. 재동결의 «동일/차이/미확인»은 `archive_design.py --compare-build` 출력(exit 0/3/4)만 근거다. 화면 HTML만 같아도 번들·런타임·자산이 대조되지 않았으면 «동일»이 될 수 없다.
5. 정상 입력, 실제 disabled 대상, 사용자 승인 예외, 이미지 단독·정적 HTML 시안은 통과한다.
6. A8 원본에서 실제 Coordinator 실행이 사용자 지목 없이 드롭다운 항목·체크박스 양상태·스크림·바깥 클릭·Esc·빈 목록을 발견·실행하고, **예외 0**(또는 평가자가 사용자 역할로 승인한 행만)으로 독립 검토·inputs를 통과한다. 보고서의 «전수» 선언은 성공으로 세지 않는다.

## 범위와 소유

변경: `dddjango-web/`과 `codex-dddjango-web/` 대응 미러, `Makefile`(`verify-web` cmp 추가·`verify-web-browser` 신설·`release-web` 선행), `docs/DEVELOPMENT.md` §5·§6 한 줄, `.gitignore`(브라우저 캐시 경로), 필요한 workspace 계획·평가 기록. backend dddjango·ontology·A8 앱·사용자 앱·활성 서버/DB는 수정하지 않는다. 새 agent·레이아웃 IR·비전 점수 게이트는 만들지 않는다. 드라이버는 «상한이 있는 결정적 상태 탐색기»이며 범용 크롤러가 아니다 — 09-06 설계의 «범용 워크플로 엔진 금지»에서 이 만큼 이탈하는 이유는 성공 조건 6(중첩 메뉴·cascade의 자율 발견)이 손 탐색으로는 세 번 실패했기 때문이다.

| 조각 | 위치 | 소유 |
|---|---|---|
| 페이지 안 스니펫 `interaction_audit.js` (신규) | `dddjango-web/assets/` | 열거·identity·context·인벤토리·상태 해시·순수 함수(잔여 계산 JS판). 값은 쓰지 않는다 |
| 드라이버 본체 `observe_interactions.pw.js` (신규) | `dddjango-web/assets/` | `async (page, opts)` 단일 함수. 탐색·재생·조작·캡처·저장 |
| Node 래퍼 `observe_interactions.mjs` (신규) | `dddjango-web/scripts/` | 인자·모듈 해소·브라우저 기동/CDP·본체 호출 |
| `check_design_evidence.py` (수정) | `dddjango-web/scripts/` | source_observation v2·잔여·표면 키 연결·예외·served·루트·수집기 sha 검증 |
| `archive_design.py --compare-build` (수정) | `dddjango-web/scripts/` | 재동결 manifest 기계 대조 |
| 픽스처·테스트 (신규/수정) | `dddjango-web/scripts/test/` | 반례·정상 짝·두 구현 동일성·DOM fixture |
| `design-evidence.md`·`design-acquisition.md` (수정) | `dddjango-web/skills/implementation-ui/references/` | 스키마·CLI·재동결 절차(Codex byte 미러) |
| Coordinator Phase 0 step 5-4·동적 표현 관찰 문단·step 5-7·경계 절·Phase 2 ⑤ 커밋 목록·수정 모드 G0 (수정) | `dddjango-web/commands/dddjango-web.md` | 실행·입력 계약(Codex `skills/dddjango-web/SKILL.md` 의미 미러) |
| design-review-web G0 입력범위 모드 (수정) | `dddjango-web/agents/design-review-web.md` | 감사 범위 재정의(Codex 의미 미러) |
| REQUEST_GUIDE (수정) | `dddjango-web/REQUEST_GUIDE.md` + Codex byte 미러 | Node/Playwright 전제조건 한 문단 |

역할 경계: Coordinator는 수집기를 실행하고 산출을 동결하며 잔여·미연결 표면을 실제로 보완한다(선언 추가·재실행·case 추가). 리뷰어는 기계 통과를 전체 발견 보증으로 보지 않고 K6의 감사 항목만 본다. 검사기는 결정적이며 의미(외형 일치·진위)를 증명하지 않는다. coder·G2·visual-evidence.json·render_audit.js·motion-notes 판형은 바꾸지 않는다. focus는 실행 증거(interactions)와 시각 처분(motion-notes)으로 소유를 가른다.

## K1. 탐색 키·잔여 단위·상한

- **identity** = `{role, name, input_type, owner, owner_items_hash}`의 canonical sha 앞 12자. `name`은 접근성 이름(aria-label → aria-labelledby → `label[for]` → 자기 텍스트 → placeholder → title, NFC·80자). **«자기 텍스트» 폴백은 항목형 대상에만** 쓴다 — button·link·menuitem·option·tab·radio·checkbox·switch·trigger·input·textarea·select, 그리고 다른 대상을 후손으로 갖지 않는 handler. 컨테이너(구조 오버레이·menu/listbox/dialog 등 owner 역할 요소·다른 대상을 후손으로 가진 handler)는 aria-label/aria-labelledby가 없으면 이름이 비어 `dom_path`가 identity에 들어간다(드라이런 결정 D-A: 컨테이너 이름이 서브트리 텍스트면 상태마다 identity가 바뀌어 그 안의 모든 대상이 owner 변동으로 재생성된다 — A8 실측 «관계» 트리거 38개·«다음» 58개). `owner`는 가장 가까운 menu/listbox/dialog/alertdialog/radiogroup/`select`/`[role=combobox]`/구조 오버레이(K2) 조상의 identity, `owner_items_hash`는 같은 owner 안 형제 항목 이름 목록의 sha. 이름이 빈 대상만 `dom_path`를 identity에 넣는다. 한 인벤토리에서 identity가 충돌하면 그때만 `dom_path`를 추가한다(순번 접미 없음). `dom_path`·rect·checked·face·value는 identity 밖의 관찰 값이다.
- **인벤토리 항목** = `{id, enabled, checked|null, face|null, value_empty|null, surface|null, occluded}`(`checked`는 `true|false|"mixed"|null` — `aria-checked="mixed"` 3상태는 문자열 그대로 상태 값이다; 최종 리뷰 C3). 활성 대상 = `enabled && !occluded`.
- **state context**(상태의 값) = 활성 identity 정렬 목록 · 대상별 `checked` · 토글형의 `surface`(자기 서브트리 **모든 요소**의 tag·class·인라인 `style` 속성 목록 + 자기 텍스트의 sha — 드라이런 결정 D-J: 루트 tag·class만 보면 인라인 style·자식 아이콘으로만 켜짐을 그리는 디자인 시스템 Checkbox의 두 상태가 같은 값이 된다) · 텍스트 입력별 `value_empty` · select/combobox 트리거별 `face`(표시 텍스트). 자유 텍스트 값 자체는 없다.
- **큐(실행) 키** = `(identity, action, option, context_T)`. `context_T`는 state context에서 face 성분을 대상 종류에 따라 줄인 것이다: 대상 T가 select/combobox 트리거이면 **문서 순서상 T보다 앞에 있는 다른 트리거의 face만** 포함(자기 face·뒤 트리거 face 제외 — cascade 부모→자식 발견은 되고 자기 face N² 재큐잉은 없다); T가 메뉴 항목이면 owner 트리거의 face 제외; 그 밖(버튼·입력·토글·오버레이)은 face 성분 전체 제외. 역순 cascade(자식이 앞에 있는 배치)는 발견되지 않으며 `--declared`와 리뷰어 감사로 닫는 한계다.
- **잔여 단위(검사기)** = `(identity, action, option)`. option = native select 옵션 value | 토글의 before 상태(checked 값 또는 surface sha) | 없음. **토글형** = checkbox·switch(radio는 선택 뒤 되돌릴 수 없어 click 1회 — Task 1 이래 두 구현 모두 CLICK_ONLY; 4d 리뷰 Minor 4로 문장 정정), 그리고 **이름이 있는(대상 후손이 없는) handler** — checked가 없으면 surface가 상태이며 관찰된 surface마다 click 단위가 필요하다(드라이런 결정 D-H: 디자인 시스템 Checkbox가 role 없는 `<label>` 핸들러로 렌더돼 «윤달·몰라요·못려요» 토글이 1회 click으로 끝났다). 컨테이너(이름 빈 handler·overlay)는 토글형이 아니다. 어느 state에서든 활성으로 관찰된 단위는 `status: executed` step이 1개 이상 있어야 한다. `failed`·`unreachable`·`unclickable`은 세지 않는다. 오버레이의 `click:outside`는 스크림형이면 스크림 자기 `click`과 동치다(한 번만 요구). 기계가 발견하지 못한 대상은 잔여가 아니므로 발견 규칙은 K2·K3로 방어한다.
- **한 표·두 구현**: 필요 조작 표·context·잔여 규칙은 스니펫의 순수 함수(JS)와 검사기(Python)가 각각 구현하고 같은 fixture JSON에 대한 잔여가 같음을 테스트로 고정한다. fixture에는 «같은 identity·다른 context» 짝(label 이름 트리거·같은 이름 «다음» 위저드·cascading select·label 토글)을 넣는다.
- **상한과 재개**: `--max-minutes`(기본 90)·`--max-steps`(기본 8000)·`--max-depth`(기본 24 — A8 최장 경로 13). 도달하면 `partial:true`·`caps_hit`. `--resume`은 같은 `--out`의 큐·steps를 이어서 실행한다(archive/served sha가 같을 때만). 꺼내는 순서(드라이런 결정 D-F·D-F′·O1·D-K′) = ① 미실행 단위 → ② 트리거·select 항목 중 «직전 활성 트리거의 face»가 그 대상에서 처음 보는 값인 항목(D-F′ — 4b 리뷰 판정: context_T 전체가 아니라 직전 트리거 face로 좁힌다) → ②b 빈 입력 fill(identity당 2회까지) → ③ 재생 불요(같은 상태 연속 5회 상한) → ④ 접두 상태 공정성 → ⑤ 짧은 경로 → ⑥ 최신. (단위 공정성 칸은 9차에서 진행 버튼을 밀어 되돌렸다 — 검토 이력.) 결정적 최적화 하나만 허용한다: 큐 항목의 경로 접두 상태 해시가 현재 상태 해시와 같고 **현재 상태에 이른 경로(계보)가 그 항목의 부모 경로와 같을 때만** 새로고침·재생을 생략한다(드라이런 결정 D-G — 상태 해시는 숨은 데이터를 구분하지 못하므로 해시 일치만으로는 같은 상태가 아니다).
- **A8 드라이런 게이트**: 규범을 고치기 전에 드라이버를 A8 `design-ref`에 실행해 «발견 대상 수·실행 수·도달 상태·표면 키 수·소요» 표를 만들고, oracle(조작군 30·관계 8·시 12·시·도 17·시·군 153·빈 목록·스크림/바깥/Esc·토글 2상태)에 미달하거나 상한을 넘으면 규칙을 고치고 그 결정을 계획에 적는다. 미달 상태로 규범을 바꾸지 않는다.

## K2. 대상 열거

- **범위 루트**: `[data-screen-label="<label>"]`(K3 루트 규칙). 열거 범위 = 루트 서브트리 ∪ 문서 안 오버레이. 루트 미발견은 실패다.
- **핸들러 보유 = 대상**(후손 대상 유무 무관). 감지: React `__reactProps$*`(onClick·onChange·onKeyDown·onMouseDown·onPointerDown) · `onclick` 속성 · CDP `DOMDebugger.getEventListeners`(click·mousedown·pointerdown·keydown·change·input — Node/CDP 경로·엔진 무관). `cursor:pointer`는 CDP가 없을 때만 보조로, «자기 computed cursor가 부모와 다른 요소»에 한정. 의미 컨트롤(`button`·`a[href]`·`input`·`select`·`textarea`·`summary`·`[tabindex>=0]`·role button/link/menuitem/menuitemcheckbox/menuitemradio/option/checkbox/radio/switch/tab/combobox)은 핸들러와 무관하게 대상이다. `aria-hidden` 서브트리 제외. `disabled`·`aria-disabled`·`inert`는 `enabled:false`로 기록만. 사용 채널은 `collector.capabilities`에 기록한다.
- **뷰포트 밖 지점**: 인벤토리에서 클릭 지점이 브라우저 뷰포트 밖인 요소는 **가림이 아니다**(`occluded:false` — 가림은 뷰포트 안에서만 hit-test로 판정하며, 밖은 «미판정»으로 두어 활성으로 센다). 조작 직전에 대상을 `scrollIntoView`로 굴려 상태 해시가 그대로일 때만 재인벤토리·재판정하고(hover 발견 포함), 여전히 밖이거나 그때 가려져 있으면 `unclickable`(드라이런 결정 D-B·D-B′).
- **가림**: 클릭 지점의 `elementFromPoint`가 자기 또는 후손이 아니면 `occluded:true`(열거만·비활성·context 제외).
- **클릭 지점**: 요소 rect 안에서 후손 대상 rect에 덮이지 않는 점(3×3 격자+모서리). 없으면 `status: unclickable`(실행 아님·잔여).
- **오버레이**: role(dialog·alertdialog·menu·listbox·`aria-modal`) 또는 구조(루트 rect의 80% 이상을 덮는 `position: absolute|fixed` 요소로서 자기 핸들러가 있거나 z-index가 형제보다 큼). 필요 조작 = `click:outside` 1회 + `key:Escape` 1회. `click:outside` 지점: 스크림형은 오버레이 rect 안·후손 대상 rect 밖, 비스크림형(role=menu/listbox·루트를 덮지 않음)은 루트 rect 안·오버레이 rect 밖·owner 트리거 rect 밖. 무변화도 정상 기록이다.
- **토글**: `input`/`aria-checked`가 있으면 checked, 없으면 `surface`를 face로 쓴다. 클릭 뒤 state context가 바뀌면 K1 규칙으로 같은 대상이 다시 큐에 들어가 두 상태가 실행된다.
- **native `select`**: option은 owner=그 select·action=`select`인 대상.
- **발견 조작(필요 조작 아님)**: mouseenter/mouseover 리스너나 `:hover` 규칙(render-audit `hoverSelectors` 매칭) 보유 요소에 hover 후 재인벤토리(후보는 identity당 1회이며 항목형 kind menuitem·option·radio·checkbox·switch·tab은 제외 — 드라이런 결정 D-C), 스크롤 가능한 컨테이너는 **페이지 단위(clientHeight/clientWidth)로 끝까지 훑으며 위치마다 재인벤토리**하고 각 위치의 인벤토리를 큐 확장 출처로 삼는다(`discovery_limits`에 overflow 컨테이너·활성이 된 대상 수 기록 — 드라이런 결정 D-D). 조작 직전 복구(scrollIntoView)로 얻은 재인벤토리(`before`)도 확장 출처다(D-E). 새 대상은 K1 규칙으로 큐에 들어간다. hover 시각 효과의 처분은 motion-notes가 소유한다.
- **이탈**: 조작 뒤 document/URL이 바뀌면 `navigated: <url>`·`after: null`인 터미널 step, 큐에 넣지 않는다. 드라이버는 loopback이 아닌 URL을 거부하되 `--cdp`로 붙은 브라우저의 현재 origin은 허용한다(scope.md 실행 경계에 기록). 인증 필요 원본은 이 경로뿐이다.
- **fill 표본**: `inputmode=numeric|decimal|tel`·`pattern`이면 placeholder의 숫자열(없으면 `12345678`), placeholder가 형식처럼 보이면 placeholder 원문, 그 외 «검증 입력». `--declared`가 대상별 `value`를 줄 수 있다. 값이 걸러져 비어도 `executed`로 세되 `changes.values`에 사실대로 남는다.
- **선언**: `--declared <json>`(selector·사유·선택 value)은 대상을 늘릴 뿐 줄이지 못한다. 어느 인벤토리에도 매칭되지 않으면 `declared_unmatched`에 기록되고 잔여 밖이며, 리뷰어가 건수·사유를 대조한다. 선언 파일은 digest에 들어간다.
- **한계**: same-origin iframe은 순회한다. cross-origin iframe·가상화 목록의 DOM 밖 항목은 수집 완료가 아니며 `discovery_limits`가 비어 있지 않으면 리뷰어 항목이다. 외부 스크립트(unpkg 런타임 등) 로드 실패는 `environment_error`로 기록하고 검사기는 `partial`과 구별해 exit 1(미실행)로 낸다. 데이터가 만드는 상태(빈 목록 등)는 정적 case가 동결하며, 기계 탐색이 연쇄 조작(예: 4행 연쇄 삭제)으로 그 상태에 닿는 것은 예산 상한 안에서 보장하지 않는다(드라이런 9차 한계). 수집 중 페이지·브라우저가 닫히면(외부 종료·`window.close()`) 드라이버는 그 step에 «페이지가 닫혔다: …» 사유를 적고 큐를 비우지 않은 채 즉시 멈춘다(`partial:true`·exit 3) — `--resume`이 새 브라우저로 잇고, 닫힌 step의 단위는 한 번만 재시도한다(드라이런 결정 D-I).

## K3. 검사기 신뢰 경계·동결 연결·v1 이력

- **수집기 바이트**: `collector.snippet_sha256`·`collector.driver_sha256`은 검사기가 자기 플러그인 `assets/` 바이트와 byte 대조(불일치 exit 2).
- **루트**: `screen-meta.json`의 `source_sha256`이 case entrypoint sha와 같을 때 `root.selector`는 정확히 `[data-screen-label="<screen_label>"]`이어야 한다. 그 밖의 entrypoint(다중 화면 build의 설정 화면 등)와 label 없는 원본의 `--root`는 선언 입력으로 기록하고 리뷰어가 감사한다. 스니펫은 `root.fingerprint`(tag·label·자손 수·rect)와 `outside_root`(루트 밖에서 대상 조건을 만족한 요소 수·이름 표본)를 기록하고, `excluded_regions`(selector·사유) 선언에 매칭된 요소는 스니펫이 `count`에서 빼므로, 남은 `outside_root.count > 0`은 선언 유무와 무관하게 결함이다(최종 리뷰 C4 정정).
- **서빙 바이트**: 드라이버가 entrypoint 응답과 same-origin 2xx 자원의 `served: {local_path: sha256}`를 기록한다. 검사기는 entrypoint served sha = archive entrypoint sha, served 경로마다 manifest 행과 sha 일치, percent-decode한 url basename = entrypoint basename을 요구한다(변형본·다른 URL 차단). 404·외부 origin은 대조 밖이다.
- **viewport·크롭**: `browser_viewport`와 `content_crop`(루트 rect)을 따로 기록한다. 검사기는 `content_crop.w/h == case.viewport`를 요구한다(엔진 캔버스는 더 큰 브라우저 viewport에서 루트를 크롭한다 — design-evidence.md 현행 규칙과 정합). 여러 viewport는 viewport별 파일·별도 실행이다.
- **state_hash** = 루트 서브트리의 (identity, enabled, checked|surface, value_empty, face) 정렬 목록 + url의 sha. `live:true` 항목(`role=status`·`aria-live` 서브트리)은 열거·실행 의무는 유지하되 해시·surface_key 입력에서만 제외한다. 재생 종점의 해시가 기록된 `before.state_hash`와 다르면 `unreachable`.
- **exact-field**는 모든 중첩 객체에 재귀한다. 반례: `partial:false`인데 `caps_hit≠[]` · `executed`인데 `error≠null` · path가 가리키는 step 미존재 · 비활성/가림 대상의 `executed` · `n` 중복 · `served` 누락 · crop 불일치 · 수집기 sha 불일치 · 루트 규칙 위반 · `outside_root` 미선언.
- **예외** `interaction_exclusions` 행 = `{target, action, option, scope_ref, approval_quote}` 또는 표면 연결 예외 `{surface, scope_ref, approval_quote}`. `approval_quote`(10자 이상)는 NFC·공백 정규화 뒤 scope.md 원문 대조, `scope_ref` 앵커 실존, 두 종류 합산 행 수 ≤ 활성 대상 수의 10%. 검사기는 prepare/inputs 성공 시 예외 전량을 stderr 통지로 내고(stdout은 순수 JSON — Task 5 판정) Coordinator는 G0 배너 1급 항목으로 사용자에게 보인다. scope_ref는 가능하면 사용자 출처 문서(발주서 경로+sha)를 가리키고 리뷰어가 실제 사용자 승인인지 감사한다.
- **동결 연결(표면 키)**: 표면 키 = after 상태의 활성 identity 집합에서 face·checked·value·surface·`owner_items_hash`를 뺀 canonical sha(같은 메뉴가 열린 상태는 도별 항목이 달라도 한 표면). `changes.added ≠ ∅`인 step이 만든 표면 키마다 어느 case의 `reached_by`(그 표면에 도달한 step 하나) 또는 표면 예외 행이 있어야 한다. `removed`만 있는 step(닫힘·pick)·값만 바뀐 step·`navigated`는 연결 의무가 없다(수용된 한계 — A8에서는 윤달·몰라요 체크 상태 같은 토글 결과 캡처가 여기 해당한다). archive case는 `reached_by: {"interactions": "<path>", "step": n}`(초기 상태는 `initial`)을 갖고 `reference_capture.sha256`은 그 step의 `after.capture.sha256`(initial은 `initial.capture`)과 같아야 한다 — 원본 캡처는 전부 드라이버가 저장한 루트 크롭 바이트다. 드라이버는 `initial`과 `added ≠ ∅` step에만 PNG를 저장한다(`navigated` step은 루트가 사라진 뒤라 루트 크롭이 성립하지 않으므로 `after: null`이며 PNG도 없다 — K2). 데이터 의존 상태(빈 목록)도 UI 조작(전 항목 삭제)으로 도달해 동결한다.
- **v1 observation**: `--phase prepare/inputs`가 검사하는 build의 archive case는 예외 없이 v2다. `backstop.py`의 발견 build 순회에서만, 그 build 폴더에 git 추적 파일이 1개 이상 있고 `--diff-base`(없으면 HEAD) 대비 추적 변경 0·untracked/ignored 0일 때 v1을 «legacy» 통지와 함께 허용한다. build-state 필드는 조건이 아니다. 마이그레이션: 진행 중 build는 수집기를 돌려야 ready가 된다.
- design-input.json은 version 1을 유지하며 `allowed`에 `interaction_exclusions`(top-level)·`reached_by`(case)를 추가한다. archive case에는 `reached_by`가 **필수**이고(없으면 exit 2), 정적·이미지 case에는 없어야 한다. archive manifest 행에 선택 필드 `carried_from`(64 hex)을 허용한다.

## K4. 재동결 기계 대조

```bash
python PLUGIN/scripts/archive_design.py STAGING/screen.dc.html --source-root STAGING \
  --out BUILD/_staging-<ts>/design-ref --manifest BUILD/_staging-<ts>/source-manifest.json \
  --compare-build BUILD --compare-out BUILD/refreeze-diff.json [--carried <local_path> …]
```

- 기준 manifest = `BUILD/design-input.json`의 `manifests[0]`(인자로 고르지 않는다). 새 manifest의 `files`와 `local_path`로 대조해 파일마다 `same|changed|added|removed|carried`를 내고 `refreeze-diff.json`에 기준 manifest sha·파일별 status·size·sha12·mtime을 남긴다. `visual-check.md` ①과 build-state에 그 파일 sha를 적는다.
- exit **0** = 전부 same / **3** = changed·added·removed 있음 / **4** = same + carried만(미확인) / **1** = 오류·누락 의존성·의존성 `ok` 파일이 carried.
- **carried**: staging 파일의 `source`가 `reference_root`·`_history`·**현재 `--out`의 상위가 아닌** 이전 `_staging-*` 하위면 자동 carried, 명시 `--carried`는 entrypoint 의존성 closure 밖 파일에만 허용. 새 manifest 행은 `status: ok` + `carried_from: <기준 manifest sha>`. staging 위치는 BUILD 밖 또는 BUILD 안 `_staging-<ts>`(매번 새 디렉터리)이며 대조 뒤 `_staging-*`는 삭제하고 `refreeze-diff.json`만 남긴다(커밋 대상). staging 출처를 기계가 증명할 수 없다는 한계는 명시하고 mtime·sha 표로 transcript 대조를 가능하게 한다.
- **실행 시점**: 사용자가 재동결 또는 원본 차이 확인을 요청했을 때만. step 4의 «외부 진실 재동결?» 질문은 v1.1.7 그대로다(자동 staleness 감지 없음). 수정 모드 G0에서 재동결을 선택했으면 결과는 `refreeze-diff.json`으로만 보고한다.
- **exit 4 처분**: 배너에 «미확인 N(목록)»을 표면화하고 사용자가 «미확인 수용 / 전체 export 제공(design-acquisition §1 정상 경로)»을 고른다. 동일(0)·차이(3)·미확인(4)은 exit로만 말한다. 차이(3)면 새 기준 설치(`design-ref` 삭제 → `_staging-<ts>/design-ref`를 `design-ref`로 이동 → manifest 교체 — `archive_design.py`가 새 출력 디렉터리를 요구하므로 `--out`을 `design-ref`로 직접 주지 않는다) → `archive_sha256`이 바뀌므로 per-case 재관찰·수집·독립 검토·inputs를 같은 라운드에 마친다.
- `_history/vN` 보존은 규범으로 두지 않는다. 이전 바이트는 커밋된 산출물(git)이 보존한다.

## K5. 실행 환경

- 드라이버 본체 `assets/observe_interactions.pw.js` = `export default async (page, opts)`. Node 래퍼 `scripts/observe_interactions.mjs`는 인자 파싱·`--playwright-module <dir>`(또는 `NODE_PATH`) 해소·브라우저 기동 또는 `--cdp` 연결 뒤 본체를 부른다. MCP 경로는 `browser_run_code_unsafe`에 1행 트램폴린 `async (page) => (await import('<abs>/observe_interactions.pw.js')).default(page, <opts 리터럴>)`을 `code`로 넘겨 **같은 파일**을 실행한다(`filename` 직접 지정은 opts가 없어 쓰지 않는다). 두 경로 모두 `collector.driver_sha256`을 기록하고 K3가 대조한다. LLM이 탐색 루프를 도구 호출로 흉내 내는 경로는 없다. MCP 단일 호출의 타임아웃 위험 때문에 Node 경로가 기본이고 `--resume`이 중단을 잇는다.
- 플러그인은 아무것도 설치하지 않는다. 브라우저 기동은 `--browser-channel chrome`(설치된 Google Chrome — 이 머신에서 Playwright 1.63.0-alpha가 요구하는 chromium 1243 캐시가 없어 기본 `launch()`는 실패함을 실측)이 기본이고 `--cdp <ws>`가 대안이다. 모듈 경로는 `--playwright-module <dir>`(env 폴백 `DDDJANGO_WEB_PLAYWRIGHT_MODULE`), 채널·CDP는 `--browser-channel`/`--cdp`(env 폴백 `DDDJANGO_WEB_BROWSER_CHANNEL`/`DDDJANGO_WEB_BROWSER_CDP`)로 받는다. 모듈 경로·버전(`package.json` 실값)·기동 방식은 scope.md 실행 경계에 기록한다. Coordinator의 Bash 도구 상한(≤600초) 때문에 드라이버는 백그라운드로 실행하고 호출 1회당 `--max-minutes`를 도구 상한 아래(기본 8)로 두어 exit 3이면 `--resume`으로 잇는다. 없으면 `design_status=blocked` + 사유 enum(node 부재·playwright 모듈 부재·브라우저 기동 불가·원격 URL 거부·환경 오류)을 G0 배너에 표면화한다. REQUEST_GUIDE에 «엔진/JSX 시안은 Node와 Playwright 모듈이 필요하다» 한 문단(Claude+Codex byte 미러). Node 픽스처는 저장소에 `node_modules`를 만들지 않는다.
- 테스트: 순수 함수는 Node로 항상 실행. DOM fixture(부모 스크림+stopPropagation 패널·label 토글·label 이름 트리거·같은 이름 «다음» 위저드·cascading select·메뉴 3항목·disabled·가림·native select·이탈 링크)는 `DDDJANGO_WEB_PLAYWRIGHT_MODULE`이 있을 때 실행하고 없으면 «SKIP + 사유»를 verify 로그에 남긴다. 새 `verify-web-browser` 타깃(SKIP=실패)을 `release-web`의 선행 조건으로 두고 DEVELOPMENT.md §6에 적는다.
- 검사기(Python) 반례는 손으로 쓴 `interactions.json` fixture로 브라우저 없이 전부 고정한다. r3 거짓 통과 로그(123 step)는 **테스트 fixture로만** interactions 형식으로 옮겨 잔여 계산이 미클릭 항목을 내는지 고정한다.

## K6. 규범·역할·미러

- Coordinator step 5-4(dc 동결): 재동결 문장을 K4 절차로 교체. 동적 표현 관찰 문단 뒤에 «조작 상태 수집» 문단: HTML/JSX archive 원본은 entrypoint·viewport마다 드라이버를 실행해 `captures/<screen>-interactions.json`·캡처를 동결하고, 소스 검토로 찾은 비의미 대상은 `--declared`로 준다. 잔여·`partial`·미연결 표면·`outside_root`·`declared_unmatched`는 Coordinator가 실제 보완(선언·재실행·case 추가)하거나 scope 사용자 승인 예외로만 닫는다. `visual-check.md` ①에 대상 수·실행 수·잔여·표면 키 수·예외 수·partial을 적는다.
- step 5-7 입력 게이트: 리뷰어 입력에 `interactions.json`·선언·예외·`refreeze-diff.json`(있으면)을 추가한다. 호출 계약에 «예상 판정·pass 예시를 전달하지 않는다».
- design-review-web G0: 감사 항목 = ① `reached_by`·표면 예외 매핑의 의미 타당성 ② `declared`·`declared_unmatched`·`interaction_exclusions`·`excluded_regions`·carried·`discovery_limits` 목록의 사유와 건수 ③ `capabilities`에 CDP 리스너 열거가 없으면 소스 리스너를 직접 대조 ④ 역순 cascade·hover 전용 메뉴 같은 발견 한계 표본. 문장 하나: «같은 핸들러·데이터 변이·같은 인스턴스를 이유로 대상이나 결과 상태를 면제하지 않는다.» 1.1.11의 «독립 렌더가 필요한 상태만 case 추가» 문장은 쓰지 않는다.
- Coordinator 경계 절 «직접 쓰는 것»에 `interactions.json`·step 캡처·`refreeze-diff.json`(기계 산출 — 값을 쓰지 않는다)·`<screen>-declared.json`(서기)을 추가하고 Phase 2 ⑤ 커밋 목록에 넣는다. 수정 모드 G0의 «재동결 질문»은 v1.1.7 그대로, 선택 시 결과 보고만 K4.
- 경로 표기는 Claude `${CLAUDE_PLUGIN_ROOT}`·Codex `${SKILL_DIR}`. 드라이버는 스니펫을 `import.meta.url` 기준으로 찾는다. `verify-web`에 implementation-ui·architecture-web references의 Codex byte `cmp`를 추가한다.
- 정적 수집 경로(`freeze_design`)의 JS 조작 상태는 범위 밖(한계). C#3의 «closure에 script kind가 있으면 v2 요구» 확장은 후속 후보로만 기록한다. motion-notes 판형은 불변이며 «실측» 출처 행의 step 인용은 권고다.

## K7. `interactions.json` (version 1 — 단일 출처)

```json
{
  "version": 1,
  "collector": {"name": "interaction_audit", "snippet_sha256": "…", "driver": "observe_interactions.pw.js", "driver_sha256": "…",
                "path": "node|mcp", "capabilities": {"react_props": true, "cdp_listeners": true}},
  "archive_sha256": "…", "entrypoint": {"path": "screen.dc.html", "sha256": "…"},
  "url": "http://127.0.0.1:9000/screen.dc.html", "browser_viewport": [560, 1040], "content_crop": {"x": 85, "y": 98, "w": 390, "h": 844},
  "root": {"selector": "[data-screen-label=\"관계인\"]", "found": true, "fingerprint": {"tag": "div", "label": "관계인", "descendants": 412, "rect": {"x": 85, "y": 98, "w": 390, "h": 844}}},
  "outside_root": {"count": 0, "sample": []}, "excluded_regions": [],
  "served": {"screen.dc.html": "…", "support.js": "…", "_ds/…/_ds_bundle.js": "…"},
  "declared": [], "declared_unmatched": [],
  "observed_at": "2026-09-13T05:00:00Z",
  "targets": {"a1b2c3d4e5f6": {"role": "menuitem", "name": "배우자", "input_type": "", "owner": "…", "owner_items_hash": "…", "dom_path": "…", "kind": "menuitem", "first_seen_step": 7, "declared": false, "found_by": ["semantic", "react_props"], "live": false},
              "0f0f0f0f0f0f": {"role": "", "name": "", "input_type": "", "owner": "", "owner_items_hash": "…", "dom_path": "div:nth-of-type(3)", "kind": "overlay", "first_seen_step": 3, "declared": false, "found_by": ["structure"], "live": false, "scrim": true}},
  "initial": {"inventory": [{"id": "…", "enabled": true, "checked": null, "face": null, "value_empty": null, "surface": null, "occluded": false, "live": false}], "state_hash": "…", "surface_key": "…", "capture": {"path": "captures/…-initial.png", "sha256": "…"}},
  "steps": [{"n": 1, "path": ["…"], "target": "…", "action": "click", "option": null, "value": null, "context": "…", "status": "executed", "error": null,
             "before": {"inventory": [], "state_hash": "…"}, "after": {"inventory": [], "state_hash": "…", "surface_key": "…", "capture": {"path": "…", "sha256": "…"}},
             "changes": {"added": [], "removed": [], "values": [{"target": "…", "before": "", "after": "검증 입력"}]}, "navigated": null, "discovery": false}],
  "discovery_limits": [], "partial": false, "caps_hit": [], "environment_error": null
}
```

`after.capture`는 `initial`과 `changes.added ≠ ∅` step에만 있다(`navigated` step은 `after: null`). `found_by`는 대상을 잡은 채널(semantic·react_props·onclick·cdp_listener·cursor·structure·declared)의 목록, `live`는 `role=status`/`aria-live` 서브트리 소속 표식이다(열거·실행 의무는 그대로, state_hash·surface_key 계산에서만 제외). 종류별 선택 필드는 둘뿐이다: native select 옵션 target의 `value`, overlay target의 `scrim`(루트 80% 이상을 덮는 스크림형이면 true). 인벤토리 항목은 위 8필드로 고정하며 스니펫이 런타임에 쓰는 `kind`·`rect`·`dom_path`와 identity 원본 4필드(`role`·`name`·`input_type`·`owner` — `surface_key` 계산 입력)는 드라이버가 문서에 쓰기 전에 제거한다(`targets`가 이들을 이미 가지며, 문서에서 표면 키를 재계산할 때는 entries를 `targets`와 id로 조인한다). `owner_items_hash`는 owner 아래 **항목 kind**(menuitem·option·radio·checkbox·switch·tab) 대상 이름의 정렬 목록 sha이며 항목이 없는 owner(dialog·구조 오버레이 등)는 빈 목록의 sha다. 필드 집합은 이 블록이 단일 출처이며 검사기 exact-field의 기준이다.

## K8. 사용자 확인이 필요한 결정(기본값 제안)

1. 플러그인은 Playwright를 설치하지 않고 기존 모듈 경로를 요구한다(없으면 blocked).
2. `_history/vN` 보존을 규범으로 두지 않는다(git이 보존). 재동결 staging은 `_staging-<ts>`로 만들고 대조 뒤 지운다.
3. `--carried`를 유지하되 자동 감지(`reference_root`/이력 하위)·`carried_from` 표식·exit 4·배너 선택으로 묶는다.
4. hover·스크롤은 발견 조작으로 포함한다(필요 조작 아님).
5. `make release-web`이 브라우저 픽스처 실행(`verify-web-browser`)을 선행 조건으로 갖는다.
6. 정적 수집 경로의 JS 상태는 범위 밖으로 둔다.
7. 원본 캡처는 전부 드라이버가 저장한 루트 크롭 바이트다 — 기존 수동 캡처(A8 12장)는 무효가 되어 재캡처한다. 변형본(`_empty-variant`) 관찰은 금지되고 데이터 상태는 UI 조작으로만 도달한다.
8. 진행 중 build(A8 포함)는 플러그인 갱신 뒤 수집기를 돌려야 ready가 된다(재관찰·독립 검토 재실행). 완료 이력 build는 git 무변경일 때만 legacy 통과.
9. 예외 상한 = 활성 대상 수의 10%. 상한 기본값 = 90분·8000 step·깊이 24, 도달 시 `--resume`으로 잇는다.
10. 원격 URL은 `--cdp` 연결 origin만 허용한다(실서비스 URL 전수 클릭 방지).
11. 표면 키 연결 의무로 A8 case가 12개에서 30개 안팎으로 늘어난다(G0 배너·검토 비용 증가).
12. 다중 viewport는 viewport별로 전체 탐색을 다시 한다.

## 검증 및 순서

1. K1 드라이런 게이트(A8 원본·oracle 대조·표면 키 수·소요). 스크림·바깥 클릭·토글 2상태·빈 목록이 «스니펫 발견»으로 잡혔는지와 «선언으로 닫힘»을 구별해 집계한다.
2. 검사기 반례 전량 + r3 fixture의 잔여 검출 + 두 구현 동일성.
3. native Coordinator 실행: 스냅샷 플러그인 명시 로드·읽기 전용 A8·별도 산출 폴더·«평가 폴더 미접근» 프롬프트 경계·`--playwright-module`/`--cdp` 경로 사전 확정. 성공 조건 6의 «예외 0» 조건 적용. 대조군 둘 다 기록: (구 Coordinator + 신 검사기)·(신 Coordinator + 신 검사기).
4. 재동결: A8 원본으로 exit 4(same 18·carried 4), 번들 1바이트 변형본으로 exit 3, 이전 보관본을 staging에 복사한 경우 자동 carried → exit 4.
5. A8 밖 표본: `workspace/eval/web-design-source-integrity` fixture(정적 HTML+JS 위저드)와 `web-a8-visual-fidelity/role-browser-app/source.html`을 드라이버에 통과시켜 발견·실행 수를 기록한다(일반화 관찰, 게이트 아님).
6. 독립 구현 리뷰 → `make verify-web`·`verify-web-browser`·`make verify`·`claude plugin validate dddjango-web --strict` → 사용자 승인 뒤 커밋·`make release-web`.

기존 지침 대조군도 통과하면 성공률 개선을 주장하지 않는다. 전체 native 파이프라인 성공으로 확대하지 않는다.

## 한계(명시)

- 정적 수집 경로(`freeze_design`)의 JS 조작 상태는 수집 비적용이다.
- 역순 cascade·hover 전용 메뉴·cross-origin iframe·가상화 목록 DOM 밖 항목·비React 엔진에서 CDP가 없는 경로는 발견이 불완전할 수 있으며 `capabilities`·`discovery_limits`·`declared_unmatched`가 그 사실을 드러낸다. 리뷰어 감사 항목 ③④가 남는 재량 채널이다.
- 값만 바뀐 상태(토글 결과 등)의 캡처는 연결 의무가 없다.
- staging 출처와 `interactions.json` 자체의 진위는 기계가 증명하지 않는다(수집기 sha·served·루트 지문·mtime 표로 대조 가능성만 확보).

## 검토 이력

- rv-A(기술)·rv-B(규범)·rv-C(증거): 각 «구현 진입 불가». BLOCKER 수렴 = 탐색·잔여 키가 identity뿐(step 2~4·시·군 153 미도달) / role 없는 스크림·체크박스 미열거. → K1·K2.
- rv-R(재검토): R1(트리거 자기 face N²)·R2(`removed` 포함 step 단위 연결 의무 폭발) BLOCKER, R3~R10 MAJOR → K1 context_T 규칙·상한·resume, K3 표면 키·크롭·루트·legacy HEAD 앵커, K4 자동 carried 조건·`carried_from` 허용·CLI, K2 가림·메뉴형 바깥 클릭. 앞 절 충돌(R18)은 통합으로 제거. 숨은 결정(⑥)은 K8 7~12.
- 구현 Task 3a 리뷰(09-14): 스니펫 인벤토리 엔트리가 identity 4필드를 런타임으로 갖도록 K7 문장 보정(문서 8필드 불변·표면 키 재계산은 entries⨝targets). 캡처 clip은 캡처마다 재계산(루트가 뷰포트 안이면 fullPage 미사용). `--cdp`는 기존 컨텍스트 안에서 관찰(모션 환원 미적용).
- 구현 Task 3b(09-14): 이탈 step 처분이 K2(`after: null`)와 K3·K7(navigated 캡처)에서 갈려 K2로 통일(루트 크롭 불성립). 큐 키(K1)는 상태×대상이라 상태 차원이 큰 화면에서는 상한 안에 마르지 않음을 픽스처로 실측 — K1은 유지하고 검사기는 `partial ∧ 잔여 0`을 통과로, `partial ∧ 잔여>0`을 exit 2로 본다(K3 반례 표에는 원래 «partial 자체»가 없었다). 최종 판정은 A8 드라이런(Task 4)에서.
- 드라이런 1차(09-14, A8 관계인 · 8분 슬라이스 838 step): 대상 803·잔여 근사 111·시·군 17/153·태어난 시 0/12. 원인 = 컨테이너 identity가 서브트리 텍스트 이름으로 상태마다 변동(owner 연쇄). 결정 D-A(K1 이름 규칙: 자기 텍스트 폴백은 항목형만) · D-B(클릭 지점이 뷰포트 밖이면 scrollIntoView 복구 뒤 판정) · D-C(hover 발견 후보에서 owner 안 항목형 menuitem·option·radio·checkbox·switch·tab 제외 — 394/838 step이 hover였고 발견 0). 반영 뒤 재실행.
- Task 4a 실측(09-14): 스니펫이 뷰포트 밖 지점을 `occluded:true`로 내어 긴 메뉴 항목(시·도 11·시·군 6·태어난 시 6)이 «한 번도 활성 아님»으로 큐에 못 들었다 → D-B′(뷰포트 밖은 가림 미판정·활성) 추가. D-C는 kind 기준으로 문장 정리.
- 드라이런 2차(09-14, 드라이버 b2bfde1 · 2슬라이스 891 step): 대상 72·중복 identity 0·hover 14·unclickable 0으로 D-A~D-C 효과 확인. 그러나 시·도 메뉴(스크롤 컨테이너)의 중간 항목 대전~대구 8개가 «끝까지 한 번» 스크롤로는 보이지 않고, 복구 재인벤토리(before)에서만 활성이던 경북·경남·대구는 확장 출처가 아니라 큐에 못 들어 잔여 3·시·도 9/17에서 정체(슬라이스 2 새 단위 0) → D-D(페이지 단위 스크롤 훑기)·D-E(복구 재인벤토리도 확장 출처) 추가.
- 드라이런 4차(09-14, 드라이버 016a2a7 · 2슬라이스 868 step): 잔여 0·시·도 17/17·시 12/12·폼 4단계 도달(수정 흐름)이나 시·군 2/153·등록 흐름 4단계 미도달로 정체 — 원인 = 꺼내는 순서 기아: 시·도=X 뒤의 시·군 트리거(경로 12)와 «다음»(새 context)이 «얕은 경로 우선»에 밀려 폼 1단계 상태 조합 재실행만 반복. 결정 D-F: 순서 = ① 미실행 단위 → ② 트리거(select/combobox)의 새 context_T(cascade) → ③ 재생 불필요(같은 상태 연속 5개 상한) → ④ 접두 상태별 공정성(그 상태에서 실행된 step이 가장 적은 상태) → ⑤ 얕은 경로 → ⑥ 최신. K1 규칙(키·잔여·허용 최적화)은 무변경 — 순서는 구현 선택이며 «상한 안에서 무엇을 증명하는가»를 좌우한다.
- 드라이런 5차(09-14, 드라이버 6445bdd · 1슬라이스 251 step): D-F로 시·군 44/153·트리거 새 context 실행. 그러나 unreachable 50(«재생 중 대상이 비활성: 시·군 트리거») — 원인 = 상태 해시 충돌: 서로 다른 사람의 수정 폼 3단계는 같은 해시(시·도 face는 그 단계에 없음)라 «접두 해시 == 현재 해시»로 재생을 생략해 이하람 편집 상태에서 김서연 경로의 «다음»을 이어 붙였고(step 129·131의 before가 경남/진주시), 처음부터 재생하면 서울/비활성 → unreachable. 결정 D-G: 재생 생략은 해시 일치 + 경로 계보 일치일 때만(K1 문장 보정).
- 드라이런 6차(09-14, 드라이버 a14d336 · 3슬라이스 518 step): D-G로 unreachable 5·시·군 145/153·시 12/12·시·도 17/17. 정체 원인 3: ① 복구 재인벤토리(D-E) 확장 경로가 자기 대상을 포함해 재생 종점 불일치(전남 3 잔여) → B1 부모 경로 사용 ② 훑기가 dom_path로 전역 중복 제거돼 같은 자리의 다른 메뉴(충북 11항목)가 훑어지지 않음 → B2 상태별 훑기 ③ 등록 흐름에서 이름 입력 단위가 수정 흐름에서 이미 실행돼 재실행 순위로 밀려 «다음»이 진행하지 못함 → O1 «빈 입력 채우기(value_empty=true) 우선» 순위. 토글 3종(윤달·몰라요·못려요)은 role 없는 label 핸들러라 1회 click → D-H(이름 있는 handler는 surface 토글형).
- 드라이런 7차(09-14 16:22~, 드라이버 5923bf1): 슬라이스 2에서 unreachable 0·페이지 소실 0·관계 8·시 12·시·도 17·시·군 153/153·근사 잔여 0. 그러나 토글 2상태 0 — label 핸들러(Checkbox) click 전후 surface 동일(문서 step 54·86 changes 없음): 켜짐이 자식 span의 인라인 background·border와 `<i class="icon-check">` 추가로만 그려져 루트 tag·class·텍스트 sha가 못 본다 → D-J(K1 surface = 서브트리 모든 요소의 tag·class·인라인 style + 텍스트). 스니펫 `surfaceOf`만 변경(Task 4f) → 8차가 최종 게이트.
- 최종 리뷰(09-14 21:2x, 3영역): driver Important 1(`--resume` 복원이 executed step의 before 인벤토리를 확장 출처로 안 씀 — D-E 이음매) · checker Important 4(루트 스크롤 컨테이너 dom_path `.` · disabled 대상 hover 발견 제외 · `checked` mixed 허용 · `outside_root.count>0`은 선언 무관 결함) · norms Minor 5(viewport별 산출 파일명·재동결 삭제 순서·build-state refreeze 키·reference 메타 서술·입력 게이트 열거) → Task 12 수정 라운드 1.
- 드라이런 10차(09-14 20:08~20:56, 드라이버 4ea5478 · D-K′): 6슬라이스 871 step(executed 869·unclickable 2·unreachable 0·페이지 소실 0) · 대상 223 · 실행 단위 251 · 표면 27 · 관계 8·시 12·시·도 17·시·군 153·토글 2상태 7종·스크림/바깥·Esc · 잔여 0(드라이버·Python·JS 일치) · partial:true(상태×대상 조합) — **게이트 통과**. 빈 목록은 정적 case 한계로 기록. 기록 = workspace/eval/web-a8-interaction-observation/dryrun/.
- 드라이런 9차(09-14 19:45~, 드라이버 3503f20 · D-K 적용): 슬라이스 1이 297 step에 대상 31·시 0·시·도 0(8차 슬라이스 1 = 대상 120·시 12·시·도 17) — ④a 단위 공정성이 «다음»처럼 실행 수가 커지는 진행 버튼을 뒤로 밀어 폼 3단계 이후로 못 감 → D-K′: ④a 되돌림, ②b identity당 2회 상한만 유지. «빈 목록»은 A8 정적 case `related/empty`(PEOPLE=[] 변형본)로 이미 동결되는 데이터 상태라 기계 탐색 게이트에서 제외하고 K2 «한계»에 기록(4단 연쇄 삭제 도달은 예산 상한 밖). 반영 = Task 4e 수정 라운드 → 10차(최종 게이트: 관계·시·시·도·시·군·토글 2상태·스크림/바깥/Esc·잔여 0).
- 드라이런 8차(09-14 17:36~, 드라이버 c9f48ac · D-J 적용): 슬라이스 3에서 관계 8·시 12·시·도 17·시·군 153·토글 2상태 7종(윤달·몰라요·못려요 + 목록 행 4)·잔여 0·unreachable 0·페이지 소실 0. 미달 = «빈 목록»(관계인 4명 연쇄 삭제 뒤) — 슬라이스 4·5가 각각 step의 80%를 빈 «메모» fill 재실행에 씀(179회·180 context). 원인 = ②b(O1)가 모든 새 상태에서 빈 입력을 최우선으로 채우고 ④ 상태별 공정성이 늘 «실행 0회인 최신 상태»를 골라 깊은 삭제 연쇄(3행→2행→1행→0행)가 영원히 밀림. → D-K(K1 순서): ②b는 identity당 2회까지만 우선권 · ④를 «단위 공정성(그 단위의 총 실행 수 오름차순) → 접두 상태 공정성»으로. 반영 = Task 4e 항목 12 → 9차(최종 게이트; 빈 목록 미도달 시 한계로 기록).
- 드라이런 6차 문서 재실측(09-14 오후, 7차 전): 마지막 슬라이스에서 브라우저가 죽자(정체 판단 중단) 드라이버가 남은 큐 2470건을 1초 안에 «페이지를 다시 열지 못했다» unreachable로 비우고 partial:false·exit 0으로 «완주»했다(4차 463·5차 711건 동일) → D-I(K2 «한계»): 페이지 소실 시 즉시 정지·큐 보존·partial:true·exit 3·resume 1회 재시도. 코드는 Task 4d 수정 라운드.
