# 웹 시안 조작 상태 증거와 재동결 기계 대조 설계

상태: 독립 적대 검토 3기(A 기술·B 규범·C 증거 — `workspace/eval/web-a8-interaction-observation/design-review/rv-{A,B,C}.md`) 반영본 — 재검토 대기. 아래 «적대 검토 반영 — 확정 계약» 절이 앞 절과 충돌하면 확정 계약이 우선한다. 근거는 `workspace/eval/web-a8-interaction-observation/diagnosis.md`. 사용자 결정(2026-09-13): ① 범위 = 관찰 동결 + 재동결 대조 둘 다 ② 발견된 조작 대상은 전수 실행(예외는 scope.md 사용자 승인만) ③ 기준선 = 작업 트리의 v1.1.7 내용(1.1.8~1.1.12 프롬프트 누적은 재도입하지 않는다). 계획·구현·커밋·릴리즈는 별도 승인이다.

## 근거와 성공 조건

A8(진단 §1~§2): 시안의 다이얼로그·드롭다운은 `_ds_bundle.js`의 React 컴포넌트가 런타임에 그리는데, 동결 관찰 12 case는 전부 정적 `sc-if` 분기 상태였고 다이얼로그 안 조작(Select 열림·체크박스·focus·스크림·Esc)은 어느 trace에도 없다. 증거 검사기는 trace가 비어 있지 않은지만 보고, 독립 리뷰어는 «같은 핸들러» 면제로 pass를 냈다. v6 재동결 대조는 화면 HTML 1파일만 보고 «차이 0»을 단언했고 사용자가 드롭다운을 지목한 뒤에야 번들을 해시했다. 정확히 말하면 Coordinator는 JS를 «안 본» 것이 아니라(v3 재동결 때 번들 diff까지 읽었다) JS가 그리는 상태를 관찰 의무로 바꾸는 규칙이 없었고, 그래서 «소스를 읽고 판단하는» 리뷰어 감사는 폐쇄 장치가 될 수 없다. 프롬프트 보강은 세 번 실패했다(진단 §3).

성공 조건:

1. 원본 엔진/JSX archive(`collection=archive`) case는 기계가 수집한 조작 기록 없이 `design_status=ready`가 되지 않는다. 정적 수집 경로(`freeze_design`·이미지 단독)는 이번 범위 밖이며 한계로 명시한다.
2. 발견된 활성 조작 대상 − 실행된 조작 = ∅가 아니면 `--phase prepare/inputs`가 exit 2다. 작성자 면제 필드는 없다. 예외는 `design-input.json`의 `interaction_exclusions`가 가리키는 scope.md 사용자 승인 원문뿐이다.
3. 재동결의 «동일/차이/미확인»은 `archive_design.py --compare` 출력만 근거다. 화면 HTML만 같아도 번들·런타임·자산이 대조되지 않았으면 «동일»이 될 수 없다.
4. 정상 입력, 실제 disabled 대상, 사용자 승인 예외, 이미지 단독 시안, 정적 HTML 시안은 통과한다.
5. A8 원본에서 실제 Coordinator 실행이 사용자 지목 없이 드롭다운 항목·체크박스·스크림 같은 대상을 발견·실행하고 잔여 0으로 독립 검토·inputs를 통과한다. 보고서의 «전수» 선언은 성공으로 세지 않는다.

## 범위와 소유

변경: `dddjango-web/`과 `codex-dddjango-web/` 대응 미러, 필요한 workspace 계획·평가 기록. backend dddjango·ontology·A8 앱·사용자 앱·활성 서버/DB는 수정하지 않는다. 새 agent·레이아웃 IR·범용 탐색 엔진·비전 점수 게이트는 만들지 않는다.

| 조각 | 위치 | 소유 |
|---|---|---|
| 페이지 안 스니펫 `interaction_audit.js` (신규) | `dddjango-web/assets/` | Coordinator가 브라우저에서 실행. 대상 열거·identity·조작 전후 기록. 값은 쓰지 않는다 |
| 드라이버 `observe_interactions.mjs` (신규) | `dddjango-web/scripts/` | Node Playwright 기준 실행기. 탐색 반복·재현·저장 |
| `check_design_evidence.py` (수정) | `dddjango-web/scripts/` | source_observation v2 검증·잔여 집합 대조·예외 검증 |
| `archive_design.py --compare` (수정) | `dddjango-web/scripts/` | 재동결 manifest 기계 대조 |
| 픽스처·테스트 (신규/수정) | `dddjango-web/scripts/test/` | 반례·정상 짝 |
| `design-evidence.md`·`design-acquisition.md` (수정) | `dddjango-web/skills/implementation-ui/references/` | 스키마·CLI·재동결 절차(Codex byte 미러) |
| Coordinator Phase 0 step 5-4·동적 표현 관찰 문단·step 5-7·수정 모드 G0 (수정) | `dddjango-web/commands/dddjango-web.md` | 실행·입력 계약(Codex `skills/dddjango-web/SKILL.md` 의미 미러) |
| design-review-web G0 입력범위 모드 (수정) | `dddjango-web/agents/design-review-web.md` | 감사 범위 재정의(Codex 의미 미러) |

역할 경계: Coordinator는 수집기를 실행하고 산출을 동결하며 잔여를 실제로 보완한다. 리뷰어는 기계 통과를 전체 발견 보증으로 보지 않고, 스니펫이 못 보는 소스 선언 대상과 상태↔case 연결만 감사한다. 검사기는 결정적이며 의미(외형 일치·진위)를 증명하지 않는다. coder·G2·visual-evidence.json·render_audit.js·motion-notes 판형은 바꾸지 않는다.

## 수집기 — `interaction_audit.js` + `observe_interactions.mjs`

### 대상 열거(스니펫)

- 범위 루트: Coordinator가 화면 루트 selector를 준다(기본 `[data-screen-label="<label>"]` — extract_dc의 선택 기준과 같다). 열거 범위 = 루트 서브트리 ∪ 문서 안 오버레이(`role` = dialog·alertdialog·menu·listbox 또는 `aria-modal`)로, 편집기 knob 패널처럼 화면 밖 UI는 제외한다. 루트 미발견은 실패다.
- 대상 조건(보이고 `disabled`·`aria-disabled`·`inert`가 아닌 것): `button`·`a[href]`·`input`(hidden 제외)·`select`·`textarea`·`summary`·`[tabindex>=0]`·role이 button/link/menuitem/menuitemcheckbox/menuitemradio/option/checkbox/radio/switch/tab/combobox인 요소·클릭 핸들러가 붙은 leaf(React `__reactProps$*`의 onClick/onChange/onKeyDown, `onclick` 속성, computed `cursor:pointer`이면서 하위에 다른 대상이 없는 요소). disabled 대상은 `enabled:false`로 기록만 한다.
- 오버레이 자체(dialog/menu/listbox)는 «닫기 대상»으로 1건 등록한다(Esc 필요 조작의 주체).
- 보충 선언: Coordinator가 소스 검토에서 찾은 비의미 대상을 `--declared <json>`(selector·이유)로 줄 수 있다. 선언 대상도 열거·실행 의무가 같다. 선언은 대상을 늘릴 뿐 줄이지 못한다.

### identity

identity = `{role, name, input_type, owner, owner_items_hash}`의 canonical JSON sha256 앞 12자. `name`은 접근성 이름(aria-label → aria-labelledby → label → 자기 텍스트 → placeholder → title, NFC 정규화·80자). `owner`는 가장 가까운 menu/listbox/dialog/radiogroup 조상의 identity, `owner_items_hash`는 같은 owner 안 형제 항목 이름 목록의 sha다(같은 이름의 다른 지역 선택지가 합쳐지지 않게). 이름이 빈 대상만 `dom_path`(루트 기준 tag·nth-of-type)를 identity에 넣는다. 한 인벤토리에 같은 identity가 둘 이상이면 순번 접미로 구별한다. `dom_path`·rect·checked·value는 identity 밖의 관찰 값이다.

### 탐색·실행(드라이버)

```bash
node PLUGIN/scripts/observe_interactions.mjs --url http://127.0.0.1:PORT/screen.dc.html \
  --root '[data-screen-label="관계인"]' --viewport 390x844 \
  --entrypoint-sha <sha> --archive-sha <sha> \
  --out BUILD/captures/<screen>-interactions.json [--cdp <ws>] [--ready <selector>] \
  [--declared BUILD/captures/<screen>-declared.json] [--max-steps 3000] [--max-depth 12]
```

1. 열기 → 준비 대기(`--ready` 또는 DS 마운트·네트워크 idle·`prefers-reduced-motion: reduce`) → 인벤토리 I0.
2. 큐 = I0의 활성 대상 × 필요 조작(아래 표), 도달 경로 `[]`.
3. 항목마다: 새로고침 → 경로 재생(경로의 각 대상을 현재 인벤토리에서 identity로 찾아 조작; 못 찾으면 `unreachable`) → 대상 조작(실제 Playwright click/fill/press/focus — 페이지 안 합성 이벤트가 아니다) → 안정 대기(MutationObserver 250ms 정적·최대 3s) → 인벤토리 I′ → step 기록(경로·대상·조작·값·`executed|failed|unreachable`·오류·전후 인벤토리 id 목록·전후 상태 해시·추가/제거 대상·값 변화·URL) → I′의 새 identity를 경로+[이 조작]으로 큐에 추가.
4. 큐가 비면 종료. 상한(`--max-steps`·`--max-depth`·대상당 10s) 도달은 `partial:true`·`caps_hit`로 남기고 성공으로 바꾸지 않는다.

필요 조작 표(검사기가 같은 표로 잔여를 계산한다):

| 대상 종류 | 필요 조작 |
|---|---|
| button·link·menuitem·option·tab·radio·핸들러 leaf·선언 대상 | `click` 1회 |
| checkbox·switch·menuitemcheckbox | 관찰된 checked 상태마다 `click` 1회(false·true 둘 다 관찰됐으면 2회) |
| text·number·date·search 등 입력·textarea | `focus`·`fill`·`blur` |
| native `select` | 옵션마다 `select` 1회 |
| 오버레이(dialog·menu·listbox) | `key:Escape` 1회 |

`fill` 값은 종류별 고정 표본(예: 텍스트 «검증 입력»·숫자 «1»·날짜 placeholder 형식)으로 커버리지용이며 값 조합은 열거하지 않는다. hover는 motion-notes 채널이 맡고 여기서 요구하지 않는다. 같은 전이를 반복하는 데이터 행(사람 4명)도 대상마다 실행하고 보고 표에서만 묶는다.

### 산출 `interactions.json` (version 1)

```json
{
  "version": 1,
  "collector": {"name": "interaction_audit", "snippet_sha256": "…", "driver": "observe_interactions.mjs|mcp-playwright"},
  "archive_sha256": "…", "entrypoint": {"path": "screen.dc.html", "sha256": "…"},
  "url": "http://127.0.0.1:9000/screen.dc.html", "viewport": [390, 844],
  "root": {"selector": "[data-screen-label=\"관계인\"]", "found": true},
  "observed_at": "2026-09-13T05:00:00Z",
  "targets": {"a1b2c3d4e5f6": {"role": "menuitem", "name": "배우자", "input_type": "", "owner": "…", "owner_items_hash": "…", "dom_path": "…", "enabled": true, "first_seen_step": 7, "declared": false}},
  "steps": [{"n": 1, "path": ["…"], "target": "…", "action": "click", "value": null, "status": "executed",
             "before": {"inventory": ["…"], "state_hash": "…"}, "after": {"inventory": ["…"], "state_hash": "…"},
             "changes": {"added": ["…"], "removed": ["…"], "values": [{"target": "…", "before": "", "after": "검증 입력"}], "url": null},
             "error": null}],
  "partial": false, "caps_hit": []
}
```

수집기 hash는 버전·동일성 표시이며 브라우저 실행 자체의 인증이 아니다. 산문 로그를 파싱해 구조화 성공 기록으로 바꾸는 경로는 없다. MCP Playwright로 대체 실행해도 같은 스니펫을 `evaluate`로 실행해 같은 형식을 내야 하며, 드라이버 이름을 기록한다.

## 검사기 — source_observation v2와 예외

- `source_observation` version 2 = v1 필드 + `interactions` 포인터(path·sha256). archive HTML/JSX entrypoint case는 v2가 필수다. v1은 그 build의 `build-state.json`이 `phase: finalize`이고 `g2_approved: true`인 완료 이력에서만 허용한다(현재 진행 build는 v2). 여러 case가 같은 화면이면 같은 `interactions.json`을 가리킬 수 있다.
- 검증: 포인터·JSON·exact 필드(알 수 없는 필드는 결함 — 작성자 면제 필드 차단)·`archive_sha256`·`entrypoint`가 case와 일치·`root.found`·`steps` 비어 있지 않음·`partial=false`·`caps_hit=[]`·모든 step의 대상·인벤토리 id가 `targets`에 존재.
- 잔여 집합: 어느 인벤토리에서든 `enabled:true`로 관찰된 대상의 필요 조작(위 표) − `status=executed`인 step의 (대상, 조작[, 옵션/상태]) − 예외. 잔여가 있으면 결함으로 앞 20건을 출력한다. `failed`·`unreachable`은 실행으로 세지 않는다.
- 예외 `interaction_exclusions`(design-input.json 선택 필드·version 1 유지·`allowed`에 추가): 행마다 `{target, action, scope_ref, approval_quote}`. `approval_quote`(10자 이상)가 `scope.md`에 원문 그대로 있어야 하고, 리뷰어가 그것이 실제 사용자 승인인지 감사한다. 와일드카드·종류 단위 예외는 없다.
- digest: `interactions.json` 바이트는 입력 digest·review_digest에 들어간다. 바뀌면 prepare·독립 검토·inputs를 다시 한다.
- `backstop.py`는 `validate_inputs`를 그대로 쓰므로 자동 반영된다.

## 재동결 기계 대조 — `archive_design.py --compare`

```bash
python PLUGIN/scripts/archive_design.py STAGING/screen.dc.html --source-root STAGING \
  --out BUILD/_staging-ref --manifest BUILD/_staging-manifest.json \
  --compare BUILD/source-manifest.json [--carried <local_path> …] [--compare-out BUILD/refreeze-diff.json]
```

- 동작: 보관을 마친 새 manifest의 `files`와 이전 manifest를 `local_path`로 대조해 `same|changed|added|removed|carried`를 파일마다 출력하고 요약 한 줄을 낸다. `--carried`는 원격에서 받을 수 없어 이전 보관본을 그대로 옮긴 파일(예: 256KiB 한도 PNG)이며 «미확인»으로만 분류된다.
- exit: 1 = 오류·누락 의존성(현행 유지) · 3 = changed/added/removed/carried가 하나라도 있음 · 0 = 전부 same. carried 파일이 entrypoint 의존성 보고에 `status: ok`로 나타나면 화면이 참조하는 파일을 미확인으로 넘기는 것이므로 exit 1이다.
- 규범: 재동결·«시안이 바뀌었나» 요청은 원격 파일 전부를 새 staging에 받은 뒤 이 명령을 실행하고, 그 출력이 «동일/차이/미확인»의 유일한 근거다. 일부 파일 손대조·«차이 0» 단언·이전 sha 암기 대조는 결과로 쓰지 않는다. 차이가 있으면 기존 절차대로 `_history/vN` 보존 → 새 기준 설치 → source_observation의 `archive_sha256`이 바뀌므로 per-case 재관찰·수집·독립 검토·inputs를 같은 라운드에 마친다.

## 규범 연결

- Coordinator step 5-4(dc 동결): 재동결 문장을 위 `--compare` 절차로 교체한다.
- 동적 표현 관찰 문단 뒤에 «조작 상태 수집» 문단: HTML/JSX 원본은 entrypoint마다 수집기를 실행해 `captures/<screen>-interactions.json`을 동결하고, 소스 검토로 찾은 비의미 대상을 `--declared`로 준다. 잔여·`partial`·실패는 Coordinator가 실제 보완(선언 추가·재실행)하거나 scope 사용자 승인 예외로만 닫는다. `visual-check.md` ①에 대상 수·실행 수·잔여·partial을 적는다.
- step 5-7 입력 게이트: 리뷰어 입력에 `interactions.json`·선언 목록·예외 목록을 추가한다.
- design-review-web G0: 기계 통과를 전체 발견 보증으로 해석하지 않는다. 원본 소스·부품 정의에서 핸들러·prop(onClick·onCancel·onConfirm 등)을 읽어 `targets`에 없는 대상을 찾으면 입력 부족이다. 각 step의 결과 상태(추가/제거 대상·값 변화)가 design-input case 또는 «case 내 변이»로 연결되는지 대조하고, 독립 렌더가 필요한 상태만 case 추가를 요구한다. 예외 행의 `approval_quote`가 실제 사용자 승인인지 확인한다.
- 수정 모드 G0의 «재동결 질문»은 `--compare` 결과로 답한다.
- design-evidence.md에 v2 스키마·잔여 규칙·예외·`--compare` exit를, design-acquisition.md §2에 재동결 절차·§3에 수집기 단계를 쓴다. Codex: scripts·assets·references는 byte 미러, `skills/dddjango-web/SKILL.md`·`dddjango-web-design-review-web/SKILL.md`는 의미 미러(`${SKILL_DIR}` 경로·`spawn_agent` 호출 유지).
- 기존 1.1.8~1.1.12 프롬프트 문단은 재도입하지 않는다. 1.1.12의 «한 파일만 비교했으면 그 파일만 동일» 의미는 `--compare` 출력 규칙이 대신한다.

## 검증 및 순서

도구 반례(테스트로 고정): 잔여 1건 → exit 2 · `failed` step만 있는 대상 → exit 2 · `partial:true` → exit 2 · 알 수 없는 필드(`exempt` 등) → exit 2 · 예외 `approval_quote`가 scope.md에 없음 → exit 2 · v1 observation을 진행 중 build에서 사용 → exit 2 · 완료 이력 build의 v1 → 통과 · 이미지 단독·정적 HTML → 변경 없음 · `--compare` same/changed/added/removed/carried 각 exit · carried가 의존성 ok에 있으면 exit 1. 정상 짝: 전수 실행·예외 정합·disabled 대상 존재.

수집기 테스트: 스니펫의 순수 함수(이름 정규화·identity·해시)는 Node 단위 테스트, DOM 열거·탐색은 작은 fixture 페이지(메뉴 3항목·disabled 버튼·체크박스·입력·스크림·Esc)를 Playwright가 있을 때 실행하고 없으면 «SKIP + 사유»를 출력한다(실패로 세지 않는다). 저장소에서 `playwright`가 resolve되지 않는 현재 환경은 실행 조건(프로젝트 로컬 설치 또는 `npx playwright`)을 규범에 명시한다.

A8 실증(평가 자료는 `workspace/eval/web-a8-interaction-observation/`에 두고 `/tmp`의 기존 자료 중 프롬프트·oracle·판정만 이관):

1. 기존 거짓 통과 자료(`coordinator-repair` r3 산출)를 새 검사기로 → exit 2(조작 기록 없음/잔여).
2. A8 `design-ref`를 로컬 정적 서버로 서빙해 수집기 실행 → 발견 대상·실행 수를 평가자 oracle(30 조작군·8/12/17/153)과 대조. 스니펫이 못 찾은 대상은 소스 선언 경로로 닫히는지 확인.
3. 새 세션의 native Coordinator(스냅샷 플러그인 명시 로드·읽기 전용 A8·별도 산출 폴더)가 드롭다운·체크박스·스크림 정답을 받지 않고 수집기 실행·잔여 보완·독립 G0 검토·inputs exit 0까지 가는지 확인. 평가자가 증거를 손봐 통과시키지 않는다.
4. 재동결: 같은 A8 원본으로 `--compare`가 «same 18·carried 4·exit 3»을 내고, 번들 1바이트 변형본에서 `changed`를 내는지 확인.
5. 독립 구현 리뷰(전체 diff·행동 증거) → `make verify-web`·`make verify`·`claude plugin validate dddjango-web --strict` → 사용자 승인 뒤 커밋·`make release-web`.

기존 지침 대조군도 통과하면 성공률 개선을 주장하지 않는다. 전체 native 파이프라인 성공으로 확대하지 않는다.

## 열린 질문(적대 검토 대상)

- v1 observation의 완료 이력 허용 조건(`phase: finalize`·`g2_approved`)이 우회 통로가 되는가. 대안: 이력 build도 v2 강제 + 재관찰 요구.
- 필요 조작 표가 A8 밖 시안(native select·contenteditable·drag·hover 전용 메뉴)에 부족한 종류가 있는가. 부족은 `--declared`와 리뷰어 소스 감사로 닫히는가.
- 재현 경로 재생이 비결정적 원본(난수·시간)에서 `unreachable`을 양산할 때의 처분.
- `--carried`가 «미확인» 남용 통로가 되지 않는가(의존성 ok 교차 검사로 충분한가).

## 적대 검토 반영 — 확정 계약

세 리뷰의 BLOCKER·MAJOR를 아래 결정으로 닫는다. 발견 번호는 `rv-A`(A-B1…)·`rv-B`(B-B1…)·`rv-C`(C#1…)를 가리킨다. 앞 절과 충돌하면 이 절이 우선한다.

### K1. 탐색 키와 잔여 단위 (A-B1 · B-M6 · C#1)

- **큐(실행) 키** = `(identity, action, option, context)`. `context` = 다음의 canonical JSON sha: 현재 인벤토리의 활성 대상 identity 정렬 목록 · 대상별 `checked`(읽을 수 있을 때) · select/combobox 트리거별 `face`(표시 텍스트) · 텍스트 입력별 «비어 있음» 2값 · checked를 읽을 수 없는 토글형 대상의 `surface`(자기 서브트리의 tag·class 목록·텍스트 sha). 자유 텍스트 값 자체는 제외한다(값 조합 미열거). 같은 identity라도 context가 다르면 다시 실행되므로 등록 step1(이름 빈값)과 편집 step1(값 채움)의 «다음»이 갈라지고, 시·도 face마다 시·군 트리거가 다시 열려 도별 항목이 발견된다.
- **잔여 단위(검사기)** = `(identity, action, option)`. option = native select 옵션 value | 토글의 before 상태(checked 값 또는 surface sha) | 없음. 어느 context에서든 활성으로 관찰된 단위는 `status: executed` step이 1개 이상 있어야 한다. `failed`·`unreachable`·`unclickable`은 세지 않는다. 기계가 발견하지 못한 대상은 잔여가 아니므로(C 2-3) 발견 규칙 자체는 K2·K3·K7로 방어한다.
- **한 표·두 구현**: 필요 조작 표와 context·잔여 규칙은 `assets/interaction_audit.js`의 순수 함수(JS)와 `check_design_evidence.py`(Python)가 각각 구현하고, 같은 fixture JSON에 대해 두 구현의 잔여가 같음을 테스트로 고정한다.
- **비용 상한**: `--max-minutes`(기본 45)·`--max-steps`(기본 6000)·`--max-depth`(12). 도달하면 `partial:true`·`caps_hit`. 결정적 최적화 하나만 허용한다: 큐 항목의 경로 접두 상태 해시가 현재 상태 해시와 같으면 새로고침·재생을 생략한다.
- **A8 드라이런 게이트**: 규범을 고치기 전에 드라이버를 A8 `design-ref`에 실행해 «발견 대상 수·실행 수·도달 상태·소요» 표를 만들고, oracle(조작군 30·관계 8·시 12·시·도 17·시·군 153)에 미달하거나 상한을 넘으면 context 구성을 바꾸고 그 결정을 계획에 적는다. 미달 상태로 규범을 바꾸지 않는다.

### K2. 대상 열거 규칙 (A-M1·M2·M3·M4 · B-B1 · C#2·#9·#16)

- **핸들러 보유 = 대상**. 후손 대상 유무와 무관하다. 감지 채널: React `__reactProps$*`(onClick·onChange·onKeyDown·onMouseDown·onPointerDown) · `onclick` 속성 · CDP `DOMDebugger.getEventListeners`(click·mousedown·pointerdown·keydown·change·input — Node/CDP 경로에서 엔진 무관). `cursor:pointer`는 CDP가 없을 때만 보조로 쓰며 «자기 computed cursor가 부모와 다른 요소»에 한정한다. `aria-hidden` 서브트리·`disabled/aria-disabled/inert`는 열거만 하고 활성 대상이 아니다. 사용 가능한 채널은 `collector.capabilities`에 기록한다.
- **클릭 지점**: 요소 rect 안에서 후손 대상 rect에 덮이지 않는 점(3×3 격자+모서리 표본)을 고른다. 없으면 `status: unclickable`로 기록하고 실행으로 세지 않는다(잔여로 남는다).
- **오버레이**: role(dialog·alertdialog·menu·listbox·`aria-modal`) 또는 **구조**(루트 rect의 80% 이상을 덮는 `position: absolute|fixed` 요소로서 자기 핸들러가 있거나 z-index가 형제보다 큼)로 인식한다. 오버레이의 필요 조작 = `click:outside`(오버레이 rect 안·후손 대상 rect 밖의 점) 1회 + `key:Escape` 1회. 무변화도 정상 기록이다.
- **토글**: `input`/`aria-checked`가 있으면 checked를 읽고, 없으면 `surface` sha를 face로 쓴다. 클릭 뒤 새 context가 되면 K1 규칙으로 같은 대상이 다시 큐에 들어가 두 상태가 모두 실행된다. 필요 조작 표의 «관찰된 상태마다 click»은 이 두 값(checked 또는 surface)으로 계산한다.
- **owner** 종류에 `select`·`[role=combobox]`·구조 오버레이를 추가한다. native `select`의 option은 owner=그 select·action=`select`인 대상이다.
- **발견 조작(필요 조작 아님)**: mouseenter/mouseover 리스너나 `:hover` 규칙(render-audit `hoverSelectors` 매칭)이 있는 요소에 hover 후 재인벤토리, 스크롤 가능한 컨테이너는 끝까지 스크롤 후 재인벤토리(`discovery_limits`에 overflow 컨테이너·자식 수 급증 기록). 새로 드러난 대상은 K1 규칙으로 큐에 들어간다. hover 시각 효과의 처분은 motion-notes가 그대로 소유한다.
- **이탈**: 조작 뒤 document/URL이 바뀌면 그 step은 `navigated: <url>`·`after: null`인 터미널 step이고 큐에 넣지 않는다. 드라이버는 loopback이 아닌 URL을 기본 거부한다(`--allow-remote` 없음).
- **fill 표본**: `inputmode=numeric|decimal|tel`·`pattern`이면 placeholder의 숫자열(없으면 `12345678`), placeholder가 형식처럼 보이면 placeholder 원문, 그 외 «검증 입력». `--declared`가 대상별 `value`를 줄 수 있다. 값이 걸러져 비어도 `executed`로 세되 `changes.values`에 사실대로 남는다.
- **한계(명시)**: same-origin iframe은 순회하고 cross-origin iframe·인증 필요 원본은 `--cdp`로 로그인된 브라우저에 붙는 경로만 있다. 가상화 목록의 DOM 밖 항목은 수집 완료가 아니며 `discovery_limits`가 비어 있지 않으면 리뷰어 감사 항목이다.

### K3. 검사기 신뢰 경계 (A-M5·M6·M8 · C#4·#5·#11·#12)

- `collector.snippet_sha256`·`collector.driver_sha256`은 검사기가 자기 플러그인 `assets/` 바이트와 byte 대조한다(불일치 exit 2).
- **루트**: `screen-meta.json`에 `screen_label`이 있으면 `root.selector`는 정확히 `[data-screen-label="<그 값>"]`이어야 한다. 스니펫은 `root.fingerprint`(tag·label·자손 수·rect)와 `outside_root`(문서 안·루트 밖에서 대상 조건을 만족한 요소 수·이름 표본)를 기록하고, `outside_root.count > 0`이면 `excluded_regions`(selector·사유) 선언 없이는 결함이다. label이 없는 원본의 `--root`는 선언 입력으로 리뷰어 감사 대상이다.
- **서빙 바이트**: 드라이버가 entrypoint 응답과 same-origin으로 받은 자원의 `served: {local_path: sha256}`를 기록한다. 검사기는 entrypoint served sha = archive entrypoint sha, served 경로마다 manifest 행과 sha 일치, url basename = entrypoint basename을 요구한다(변형본·다른 URL 차단).
- `interactions.viewport` = case viewport. 여러 viewport는 viewport별 파일이다.
- **state_hash** = 루트 서브트리의 (identity, enabled, checked|face, value_empty) 정렬 목록 + url의 sha. `role=status`·`aria-live` 서브트리는 제외한다. 재생 종점의 해시가 기록된 `before.state_hash`와 다르면 `unreachable`.
- **exact-field**는 모든 중첩 객체에 재귀한다. 반례에 추가: `partial:false`인데 `caps_hit≠[]` · `executed`인데 `error≠null` · path가 가리키는 step 미존재 · 비활성 대상의 `executed` · `n` 중복 · `served` 누락 · viewport 불일치.
- **예외**(`interaction_exclusions`) 행 = `{target, action, option, scope_ref, approval_quote}`. `approval_quote`는 NFC·공백 정규화 뒤 scope.md 원문 대조, `scope_ref` 앵커 실존, 행 수 ≤ 활성 대상 수의 10%. 검사기는 prepare/inputs 성공 출력에 예외 전량을 stdout으로 내고, Coordinator는 그 목록을 G0 배너 1급 항목으로 사용자에게 보인다(승인자가 직접 본다). scope_ref는 가능하면 사용자 출처 문서(발주서 경로+sha)를 가리킨다. 리뷰어는 원문이 실제 사용자 승인인지 감사한다.
- **동결 연결**(B-B2 · C#6): archive case는 `reached_by: {"interactions": "<path>", "step": n}`을 갖고(초기 상태는 step 0), `reference_capture.sha256`은 그 step의 `after.capture.sha256`(step 0은 초기 캡처)과 같아야 한다 — 원본 캡처는 전부 드라이버가 저장한 바이트다. `changes.added ≠ ∅` 또는 `removed ≠ ∅` 또는 `navigated`인 step은 어느 case의 `reached_by` 또는 예외 행이 가리켜야 한다(검사기 대조). 값만 바뀐 step은 연결 의무가 없다(수용된 한계). 드라이버는 그런 step과 초기 상태에만 `after.capture` PNG를 저장한다. 빈 목록 같은 데이터 의존 상태도 UI 조작(전 항목 삭제)으로 도달해 동결한다 — 변형본 관찰은 K3 서빙 대조로 막힌다.
- **v1 observation** (A-M7 · B-M1 · C#7): `--phase prepare/inputs`가 검사하는 build의 archive case는 예외 없이 v2다. `backstop.py`의 발견 build 순회에서만, `--diff-base` 대비 그 build 폴더가 git으로 무변경(추적 변경 0·untracked 0)일 때 v1을 «legacy» 통지와 함께 허용한다. build-state 필드는 조건이 아니다. 마이그레이션: 진행 중 build는 수집기를 돌려야 ready가 되며, 그 사실을 릴리즈 노트에 적는다.

### K4. 재동결 기계 대조 (A-M9 · B-M3·M4·M5 · C#8)

- exit **0** = 전부 same / **3** = changed·added·removed 있음 / **4** = same + carried만(미확인 있음) / 1 = 오류·누락 의존성·의존성 `ok` 파일이 carried. `--compare-out` 필수 — `refreeze-diff.json`에 기준 manifest sha·파일별 status·size·sha12·mtime을 남기고 `visual-check.md` ①과 build-state에 sha를 적는다.
- 기준 manifest는 인자로 고르지 않는다. 대조 대상 build의 `design-input.json` `manifests[0]`로 고정한다.
- **carried**: staging 파일의 `source` 경로가 BUILD 하위(design-ref 등)면 자동 carried, 명시 `--carried`는 entrypoint 의존성 closure 밖 파일에만 허용. 새 manifest의 해당 행은 `status: ok` + `carried_from: <기준 manifest sha>`를 가져 «미확인»이 설치 뒤에도 보인다. staging 출처를 기계가 증명할 수 없다는 한계는 명시하고, 출력 표(mtime·sha)로 transcript 대조를 가능하게 한다.
- **실행 시점**: 사용자가 재동결 또는 원본 차이 확인을 요청했을 때만 실행한다. step 4의 «외부 진실 재동결?» 질문은 v1.1.7 그대로다(자동 staleness 감지 없음). 수정 모드 G0에서 재동결을 선택했으면 결과는 `refreeze-diff.json`으로만 보고한다.
- **exit 4 처분**: 배너에 «미확인 N(목록)»을 표면화하고 사용자가 «미확인 수용 / 전체 export 제공(design-acquisition §1 정상 경로)»을 고른다. 동일(0)·차이(3)·미확인(4)은 exit로만 말한다.
- `_history/vN` 보존은 규범으로 두지 않는다. 이전 바이트는 커밋된 산출물(git)이 보존하고, `refreeze-diff.json`이 대조 기록이다(1.1.12 문단 미재도입).

### K5. 실행 환경 (A-B2·M11 · B-M2·M8)

- 드라이버 본체는 `assets/observe_interactions.pw.js`의 단일 함수 `async (page, opts)`다. Node 경로 `scripts/observe_interactions.mjs`는 인자 파싱·`--playwright-module <dir>`(또는 `NODE_PATH`) 해소·브라우저 기동 또는 `--cdp` 연결 뒤 이 함수를 부른다. MCP 경로는 `browser_run_code_unsafe`의 `filename`/1행 트램폴린(`async (page) => (await import('<abs>/observe_interactions.pw.js')).default(page, opts)`)으로 **같은 파일**을 실행한다. 두 경로 모두 `collector.driver_sha256`을 기록하고 K3가 대조한다. LLM이 탐색 루프를 도구 호출로 흉내 내는 경로는 없다.
- 플러그인은 아무것도 설치하지 않는다. Playwright 모듈 경로·버전(`package.json` 실값)·브라우저 기동 방식은 scope.md 실행 경계에 기록한다. 없으면 `design_status=blocked` + 사유 enum(node 부재·playwright 모듈 부재·브라우저 기동 불가·원격 URL 거부)을 G0 배너에 표면화한다. REQUEST_GUIDE에 «엔진/JSX 시안은 Node와 Playwright 모듈이 필요하다» 한 문단(Claude+Codex byte 미러).
- 테스트: 순수 함수(정규화·identity·context·잔여)는 Node로 항상 실행. DOM fixture(부모 스크림+stopPropagation 패널·label 토글·메뉴 3항목·disabled·native select·이탈 링크)는 `DDDJANGO_WEB_PLAYWRIGHT_MODULE`이 있을 때 실행하고 없으면 «SKIP + 사유»를 verify 로그에 남긴다. `make release-web`은 새 `verify-web-browser` 타깃(SKIP=실패)을 선행한다.
- 검사기(Python) 반례는 손으로 쓴 `interactions.json` fixture로 브라우저 없이 전부 고정한다. r3 거짓 통과 로그(123 step)는 **테스트 fixture로만** interactions 형식으로 옮겨 잔여 계산이 미클릭 항목을 내는지 고정한다(배포 경로의 산문 파싱이 아니다).

### K6. 규범·역할·미러 (B-B2·M10 · A-m5 · C#14·#19)

- design-review-web G0: «독립 렌더가 필요한 상태만 case 추가» 문장을 쓰지 않는다. 감사 항목 = ① `reached_by` 매핑의 의미 타당성 ② `declared`·`interaction_exclusions`·`excluded_regions`·carried·`discovery_limits` 목록의 사유 ③ `capabilities`에 CDP 리스너 열거가 없으면 소스 리스너를 직접 대조. 문장 하나를 둔다: «같은 핸들러·데이터 변이·같은 인스턴스를 이유로 대상이나 결과 상태를 면제하지 않는다.» Coordinator 호출 계약에 «예상 판정·pass 예시를 전달하지 않는다» 한 문장.
- Coordinator 경계 절 «직접 쓰는 것» 목록에 `interactions.json`·step 캡처(기계 산출 — 값을 쓰지 않는다)·`<screen>-declared.json`(서기)·`refreeze-diff.json`(기계 산출)을 추가하고 Phase 2 ⑤ 커밋 목록에 넣는다.
- 경로 표기는 Claude `${CLAUDE_PLUGIN_ROOT}`·Codex `${SKILL_DIR}`. 드라이버는 스니펫을 `import.meta.url` 기준으로 찾아 인자 표기가 같다. Node 픽스처는 `node_modules`를 만들지 않는다(모듈은 외부 경로 참조).
- `verify-web`에 implementation-ui·architecture-web references의 Codex byte `cmp`를 추가한다(현재는 우연히 동일).
- 정적 수집 경로(`freeze_design`)의 JS 조작 상태는 이번 범위 밖이며 한계 절에 적는다. C#3의 «closure에 script kind가 있으면 v2 요구» 확장은 후속 후보로만 기록한다.
- motion-notes 판형은 바꾸지 않는다. «실측» 출처 행이 interactions step을 인용하는 것은 권고로만 둔다.

### K7. 검증 계획 보강 (A-B1 · C#19)

1. K1 드라이런 게이트(A8 원본·oracle 대조·소요)를 규범 수정 전에 통과한다. 스크림·바깥 클릭·토글 2상태가 «스니펫 발견»으로 잡혔는지와 «선언으로 닫힘»을 구별해 집계한다.
2. 검사기 반례 전량 + r3 fixture의 잔여 검출.
3. native Coordinator 실행: 스냅샷 플러그인 명시 로드·읽기 전용 A8·별도 산출 폴더·«평가 폴더 미접근» 프롬프트 경계·`--cdp` 또는 `--playwright-module` 경로 사전 확정. 성공 조건 5의 «잔여 0»은 **예외 0** 또는 평가자가 사용자 역할로 승인한 행만으로 달성해야 한다. 대조군 둘 다 기록한다: (구 Coordinator + 신 검사기)·(신 Coordinator + 신 검사기).
4. 재동결: A8 원본으로 exit 4(same 18·carried 4), 번들 1바이트 변형본으로 exit 3, 이전 보관본을 staging에 복사한 경우 자동 carried → exit 4를 확인한다.
5. A8 밖 표본: `workspace/eval/web-design-source-integrity` fixture(정적 HTML+JS 위저드)와 `web-a8-visual-fidelity/role-browser-app/source.html`을 드라이버에 통과시켜 발견·실행 수를 기록한다(일반화 관찰, 게이트 아님).
6. 독립 구현 리뷰 → `make verify-web`·`verify-web-browser`·`make verify`·`claude plugin validate dddjango-web --strict` → 사용자 승인 뒤 커밋·`make release-web`.

### K8. 이 반영으로 생긴 새 결정(사용자 확인 대상)

1. 플러그인은 Playwright를 설치하지 않고 기존 모듈 경로를 요구한다(없으면 blocked). 
2. `_history/vN` 보존을 규범으로 두지 않는다(git이 보존).
3. `--carried`를 유지하되 자동 감지·`carried_from` 표식·exit 4·배너 선택으로 묶는다.
4. hover는 발견 조작으로 포함한다(필요 조작 아님).
5. `make release-web`이 브라우저 픽스처 실행을 선행 조건으로 갖는다.
6. 정적 수집 경로의 JS 상태는 범위 밖으로 둔다.
