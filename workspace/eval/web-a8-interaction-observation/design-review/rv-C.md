# 설계 초안 적대 검토 C — 증거·표본 외 렌즈

대상: `workspace/design/2026-09-13-web-interaction-evidence.md`(이하 «설계», 행 번호는 그 파일). 대조 자료: 진단 `workspace/eval/web-a8-interaction-observation/diagnosis.md`, 선행 계획 `workspace/plan/2026-09-13-web-a8-interaction-observation.md`, `/tmp/dddjango-web-a8-interactions-20260913/**`(읽기 전용), 평가자 oracle `/tmp/a8-interaction-evaluator-20260913/oracle.json`(sha `274e8da6…` 일치 확인), A8 표본 `~/.herdr/worktrees/spring_dream_server/a8/.dddjango-web/20260912-1640-web-related-persons/**`(읽기 전용), A8 native transcript `54754273-….jsonl` L2495~L2515·L4489~L5010(행 번호·요지만 인용), 현행 검사기·규범(`dddjango-web/scripts/check_design_evidence.py`·`archive_design.py`·`agents/design-review-web.md`·`skills/implementation-ui/references/design-evidence.md`·`design-acquisition.md`·`commands/dddjango-web.md`), 다른 시안 표본(`workspace/eval/web-design-source-integrity/`·`web-a8-visual-fidelity/`·`web-refreeze-resume/`). 작업 트리 `dddjango-web/`가 태그 `dddjango-web--v1.1.7`과 `plugin.json` 1파일만 다름을 `git diff --stat`으로 확인했다(진단 §5 정합). Serena·Graphify는 opt-in 표식이 없어 사용하지 않았다.

심각도: BLOCKER / MAJOR / MINOR / 검증됨. 3축: **정합**(코퍼스·현행 검사기와의 정합) · **일반화**(A8 밖 시안·엔진) · **무손실**(정상 경로·기존 빌드 보존). «추측»은 명기한다.

---

## 1. 전제 공격

### 1-1. 진단 §1 «봄/안 봄» 표

- **«컴포넌트 코드 열람 — Phase 0에서 없음 · 첫 열람 09-13 12:25(L4778)»는 부정확하다.** v3 재동결(09-12 15:24 UTC)에서 Coordinator는 `_ds_bundle.js` 동결본과 staging본의 크기·헤더 해시맵·문자 단위 diff를 직접 읽었고(transcript L2503~L2512: BottomSheet 해시 `9916f4a1→db1d734f`, `scrim = true` prop 추가 조각 추출) «관계인 무관»으로 닫았다. 진단 §1 첫 행 근거 칸에도 같은 사실(L2503·L2508)이 적혀 있어 표 안에서 자기모순이다. 정확한 명제는 **«JS를 안 봤다»가 아니라 «JS를 보고도 그것이 그리는 상태를 관찰 의무로 바꾸는 규칙이 없었다»**다.
- 이 정정은 설계에 직접 영향을 준다. 설계 §역할 경계(L32)와 G0 규범(L121)은 «리뷰어가 원본 소스·부품 정의에서 핸들러·prop을 읽어 `targets`에 없는 대상을 찾는다»를 스니펫이 못 보는 대상의 폐쇄 장치로 둔다. 그런데 «소스를 읽고 판단한다»는 바로 v3에서 실패한 메커니즘이다. 설계 §근거(L7)는 이 차이를 다루지 않는다(→ 발견 #2와 결합).
- «motion-notes m5 실측 표기 — 실측 없음»(§1 6행)은 표본으로 확인된다: `motion-notes.md` m5 출처 «스캔·실측», 12 trace 어디에도 Select open 조작 없음(`related-form-step3-trace.json` `state_transition_actions`는 «tap 다음(2→3)»까지). 설계는 motion-notes 판형을 바꾸지 않으므로(L32) 같은 «실측» 무근거 표기가 재발할 수 있다(→ #18, 선택).
- «포털 없음 → 오버레이가 화면 루트 안»은 검증됨(`_ds_bundle.js` 전문에 `createPortal` 0건, Dialog는 `position:absolute; inset:0` L1080~L1092).

### 1-2. 진단 §2 시간표·§4 원인

- 시간표는 transcript와 일치한다(L4521~L4526 1파일 수신·L4549 «차이 0»·L4550 질문·L4556 거부·L4584 재발화·L4618~L4622 1파일 바이트 증명·L4634 1.1.12 규칙 인지 후 18파일 확대·L4653 «PNG 4 256KiB 한도 대조 불가·미확인»·L4733 **«토큰 파일 11개가 무변이므로 같은 폴더의 `_ds_bundle.js`·`_ds_manifest.json`도 사실상 무변»(추론으로 미확인을 동일로 격상)**·L4757 13 동일/9 미확인·«변경분 0»·L4759 사용자 드롭다운 지목·L4768~L4795 번들 수신·해시·L4831 18/18·L4980 사용자 롤백 요청·L4994 자백·L4996 «1번만해»·L5000~L5010 `git checkout` 롤백). 진단이 놓친 결정적 발화는 **L4733의 «사실상 무변» 추론**이다 — `--compare`가 막아야 할 정확한 문장이며, 설계 L113 «carried 파일이 의존성 `ok`에 나타나면 exit 1»이 이를 막는다(→ 검증됨 목록).
- §4 원인 1(«trace가 비어 있지 않은 바이트인지만 본다»)은 `check_design_evidence.py` L236~L237로 확인된다. 원인 2(«같은 핸들러 면제를 막는 기계 규칙 없음»)는 `native-review-r3.md` L64·L105·L139(«동일 핸들러 onRel → 데이터 변이 비확장»·«도 有/無 두 분기 관찰 → 비확장»·«같은 Dialog 인스턴스 → 비확장»)로 확인된다. 원인 3(«archive_design가 이전 manifest와 대조하지 않는다»)은 `archive_design.py` 전문(L120~L161)에 compare 경로가 없음으로 확인된다.

### 1-3. 설계 §근거·성공 조건의 전제

- 성공 조건 1(L11) «원본이 HTML/JSX인 case는 기계 조작 기록 없이 ready 불가»와 §검사기(L97) «**archive** HTML/JSX entrypoint case는 v2 필수»는 범위가 다르다. 정적 경로(`freeze_design`·`collection=static`)의 HTML은 현행 검사기에서 `source_observation` 자체가 허용되지 않고(`check_design_evidence.py` L391), 설계는 «정적 HTML 시안은 통과»(L14·L128 «변경 없음»)라고 한다. 즉 성공 조건 1은 문장대로 성립하지 않는다(→ #3).
- 성공 조건 5(L15)의 «드롭다운 항목·체크박스·스크림 발견·실행»과 oracle 규모(30 조작군·8/12/17/153)는 설계의 수집기 규칙으로는 도달 불가다(→ #1·#2). 설계 §검증 2(L135)가 그 대조를 계획하고 있으니 구현 뒤에 드러나겠지만, 설계 단계에서 이미 판정 가능한 불성립이다.

---

## 2. A8 두 층위 재구성

### 2-1. 층위 1 — 관찰 동결(v5 산출물에 설계를 적용)

step-by-step(설계 규칙 → A8 표본):

| 단계 | 설계 규칙 | v5 표본에 적용한 결과 |
|---|---|---|
| ① `--phase prepare` | v2 필수·v1은 `phase: finalize`∧`g2_approved`에서만(L97) | A8 `build-state.json`은 `phase: implement`·`g2_approved: false` → 12 case 전부 `source_observation` v1 → **exit 2**. 단 이것은 **스키마 red**다(조작을 검사한 결과가 아니다). |
| ② Coordinator가 수집기 실행 — I0 | 루트 `[data-screen-label="관계인"]`(관계인.dc.html L37) · 대상 조건(L39) | I0 = «뒤로»(IconButton `<button aria-label>` 번들 L628~L631) · ListRow 4행(`div onClick` L3072~L3073 · 하위 대상 없음 → 핸들러 leaf) · «관계인 등록하기»(Button `<button>`). 6대상 × click. |
| ③ 행 click → I′ | 새 identity를 경로+[조작]으로 큐 추가(L59) | 상세 Dialog: «삭제하기»(IconButton)·«닫기»·«수정하기» 추가. **Dialog 스크림(L1080~L1093 `div onClick: onCancel`, role 없음, 하위에 버튼 있음)은 leaf도 role-overlay도 아니라 미열거.** Dialog Esc(L70)는 role dialog 전제라 미등록. |
| ④ 등록하기 click → I′ | 동상 | 폼 step1: «관계» trigger(`<button aria-haspopup>` L2782~L2787, 접근성 이름 = `<label htmlFor>` «관계» L2990~L2998) · «이름» `<input>` · 여자/남자(`role=radio aria-checked` L1607~L1613) · 닫기 · **«다음»**. |
| ⑤ «다음» click(경로 [등록하기]) | (identity, 조작)당 1회 실행 | 빈 폼 → err «관계를 선택해주세요»(L425·L383) 관찰. **«다음» identity `{button, "다음"}`는 step1~4에서 동일**(L422 `formConfirmLabel`) → 다시 큐에 들어가지 않음. |
| ⑥ 관계 trigger → 메뉴 | 오버레이 `role=menu`(L2831) 등록·menuitem 8(L2889) click 1회씩 | 8항목 click·Esc 1회 실행. «메뉴 밖 mousedown»(L2735)·«trigger 재클릭»(L2787)은 필요 조작 표에 없음. |
| ⑦ step2 도달 | — | **등록 경로로는 도달 불가**(⑤). 수정 경로(김서연→수정하기→다음)는 «다음»이 이미 실행된 identity라 큐에 없음. 큐 순서가 반대여도 step2에서 «다음»이 같은 identity → **step3·step4 영구 미도달**. |
| ⑧ 체크박스 | «관찰된 checked 상태마다 click 1회»(L67) | Checkbox는 `<label onClick>`(L1472~L1473) — `input`·`role`·`aria-checked` 없음 → «핸들러 leaf → click 1회»로 분류. checked 상태 관찰 불가 → **해제(off) 미요구**. |
| ⑨ 잔여 계산 | enabled 관찰 대상 − executed(L99) | ⑦·⑧·③에서 **기계가 못 본 대상은 잔여가 아니다** → 시·군 trigger(L438·`disabled` 속성)는 관찰조차 안 됨 → 잔여 0. |
| ⑩ `--phase inputs` | 잔여 0·partial false → exit 0 | Coordinator가 포인터를 쓰면 **exit 0**. 시 12·시·도 17·시·군 153·스크림·체크박스 해제·수정 폼 전체가 미관찰인 채 통과. 남는 방어선 = 리뷰어 소스 감사(1-1의 실패 메커니즘). |

**결론: 설계대로면 v5 산출물은 ①에서 스키마 red가 되지만, 수집기를 돌린 뒤의 산출물은 oracle 대비 거짓 통과다.**

### 2-2. 층위 1 — `native-review-r3` 거짓 통과가 어디서 차단되는가

| r3 면제 문장(native-review-r3.md) | 설계의 차단 문장 | 차단 여부 |
|---|---|---|
| L64 «자녀·형제자매·친구·동료 pick — 동일 핸들러 onRel(441) → 비확장» | L99 «어느 인벤토리에서든 enabled 관찰 대상의 필요 조작 − executed»; L66 «menuitem → click 1회» | **차단** — 메뉴가 열려 8항목이 관찰됐으므로 미클릭 4건 = 잔여 → exit 2. |
| L105 «시·도 나머지 15 항목 pick — 도 有/無 두 분기 관찰 → 비확장» | 동상 | **차단**(17 관찰·2 실행 → 잔여 15). |
| (r2·r3) 시·군: 경기 31만 관찰 | 동상 | **부분** — 경기 31 중 미클릭 30은 잔여. 다른 16개 도의 시·군 목록은 관찰된 적이 없어 잔여 0 → oracle 153 대비 거짓 통과. |
| L139 «수정 폼 스크림/Escape — 등록 폼과 같은 Dialog 인스턴스·같은 onCancel → 비확장» | L38~L40 오버레이 = role dialog/menu/listbox 또는 aria-modal | **미차단** — A8 Dialog는 role 없음 → 스크림·Esc가 대상이 아님 → 잔여 없음 → 리뷰어 재량 그대로. |
| L147 «상세 음력(윤달 아님) 접두 — 독립 값 조합 → 비확장» | 설계는 값 조합 비열거(L72) | **수용된 한계**(설계가 명시). |
| L189 «조작 없이 남긴 행은 … 조용한 생략 아님 → pass» | L121 «독립 렌더가 필요한 상태만 case 추가를 요구» | **미차단** — 캡처(case) 층위의 «변이» 재량은 그대로 남는다(→ #6). |

### 2-3. 층위 1 — 잔여 거짓 통과 경로 표

| 경로 | 설계에서의 처지 | 분류 | 설계가 명시했는가 |
|---|---|---|---|
| 탐색이 못 미친 상태(위저드 step2~4·도별 시·군) | 발견 규칙이 identity-novelty 단일 프론티어라 구조적으로 미도달·잔여 0 | **거짓 통과** | 아니오(→ #1) |
| role 없는 부품(스크림·label 체크박스·Dialog Esc) | 열거 규칙 밖 → `--declared`에 의존 | **거짓 통과**(declared 누락 시) | 부분(리뷰어 소스 감사) (→ #2) |
| `--declared` 미제출 | 기계 감지 없음 | 수용된 한계 | 예(L121) |
| «case 내 변이» 판정 | 리뷰어 재량 | 수용된 한계(캡처 층위) | 아니오(→ #6) |
| exclusions에 Coordinator 자작 문장 | `approval_quote`가 scope.md에 있으면 통과·리뷰어 «실제 승인» 감사 | 수용된 한계 | 부분(→ #12) |
| MCP 드라이버 자기 신고·손 작성 interactions.json·`partial=false` 위조 | 기계 구별 불가 | 수용된 한계 | 예(L93) |
| fill 표본값 | 실행으로 세지만 커버리지 무의미(생년월일 digits 필터 L447) | 거짓 통과(step2 유효 상태 불가) | 아니오(→ #10) |
| Esc 1회 규칙 | 메뉴엔 충분; Dialog엔 미발동(role 없음) | #2에 종속 | — |
| root selector 좁히기 | `root.found`만 검사 | **거짓 통과** | 아니오(→ #5) |
| 서빙 바이트 ≠ archive(변형본·다른 URL) | `entrypoint.sha256` 자기 신고 | **거짓 통과**(baseline #1의 `_empty-variant` 재현 가능) | 아니오(→ #4) |
| 이력 build 위장(`phase: finalize`·`g2_approved` 손 기입) | build-state는 Coordinator 소유·digest 밖 | 거짓 통과(v1 면제 진입) | 열린 질문으로만(→ #7) |
| 리뷰어 pass 선기입 | 설계 무언급 | 재량 채널 오염 | 아니오(→ #14) |

### 2-4. 층위 2 — 재동결 대조에 `--compare`를 적용

- **10:33(L4549)**: 관계인.dc.html 1파일만 수신. 설계 L114 «원격 파일 전부를 새 staging에 받은 뒤 실행» + L113 «carried가 의존성 `ok`에 있으면 exit 1». staging에 1파일뿐이면 `archive_design.py`는 22파일이 아닌 1파일 archive를 만들고 `--compare`는 21 removed → exit 3; `--carried`로 21을 넘기면 `support.js`·`_ds_bundle.js`·tokens 11이 entrypoint 의존성 `ok`(source-manifest dependencies 24 ok) → **exit 1**. «차이 0» 단언 불가. ✔
- **12:22(L4757)**: 13 동일·9 미확인(번들·manifest·support.js·oxlintrc·readme·PNG 4). 번들·support.js가 carried → 의존성 ok → **exit 1**. «변경분 0» 불가. L4733 «사실상 무변» 추론이 설 자리가 없다. ✔
- **PNG 4장(256KiB 한도)**: 의존성 보고에 없음(entrypoint deps에 이미지 행 0) → carried 허용 → exit 3(L113 «carried가 하나라도 있으면 3»). 즉 **이 프로젝트에서는 재동결이 영원히 exit 3**이고, 설계는 carried-only 결과를 어떻게 닫는지(사용자 미확인 수용? export 제공 요청?) 말하지 않는다(→ #8).
- **이전 보관본을 staging에 복사해 «same» 만들기**: `archive_design.py`는 파일 출처를 모른다(L135~L153, `source: str(source)`만 기록). `--carried`는 자발 신고다. staging에 `design-ref/_ds/…/_ds_bundle.js`를 `cp`하면 same → exit 0 → «동일». **차단되지 않는다**(→ #8 권고: `source` 경로가 BUILD 하위면 자동 carried·staging 출처 비검증 명시).
- **대조 기준 manifest 선택**: `--compare BUILD/source-manifest.json`의 경로를 Coordinator가 고른다. `_history/v4/source-manifest.json`을 주면 다른 답이 나오고 검사기는 모른다(→ #8).

---

## 3. 발견 목록(심각도 높은 순)

### #1 BLOCKER — 탐색·잔여 의미론이 «identity-novelty 단일 프론티어 BFS»라 성공 조건 2·5가 구조적으로 불성립 [정합·일반화·무손실]

**근거**
- 설계 L58 «큐 = I0의 활성 대상 × 필요 조작», L59 «I′의 **새 identity**를 경로+[이 조작]으로 큐에 추가», L45 identity = `{role, name, input_type, owner, owner_items_hash}`(상태 정보 없음), L99 잔여 = «어느 인벤토리에서든 enabled 관찰 대상의 필요 조작 − executed».
- A8: «다음» 버튼은 step1~4에서 같은 identity(관계인.dc.html L107·L422). (identity, click) 1회 실행 규칙상 step2 이후는 어느 큐 순서로도 미도달(2-1 ⑤·⑦). 시·군 trigger는 처음 `disabled`(L438)로 관찰되고 경기 선택 후 enabled가 되지만 «새 identity»가 아니라 큐에 안 들어간다 — 반면 L99는 enabled 관찰 대상의 click을 요구 → **드라이버가 못 하는 것을 검사기가 요구**(영구 red 또는 exclusions 강제). 도별 시·군 목록(L436 `cityOptions`)은 상태(어느 도를 골랐나)에 종속인데 상태 키가 없다. L67 «checked 상태마다 click 1회»도 novelty 규칙으로는 두 번째 click이 큐에 들어갈 수 없다(표와 알고리즘의 모순).
- 결과: 기계가 못 본 대상은 잔여가 아니므로 «잔여 0»은 발견 규칙의 약함을 그대로 통과로 바꾼다. oracle 30/8/12/17/153은 도달 불가.
- 실행 예산도 미정의: A8 규모(대상당 새로고침+경로 재생, 시·군 153 × 경로 길이 ~12)의 소요를 추정하지 않았고 `--max-steps 3000`이 A8에서 충분한지 근거가 없다.

**권고**(범위 확대가 아니라 정의 보완)
1. 탐색을 상태 그래프로 정의한다: 노드 = 상태 키(인벤토리 identity 집합 + enabled/checked 플래그 + url 경로), 간선 = (상태, 대상, 조작). novelty는 (상태, 대상, 조작) 단위. 큐에는 새 상태에서 발견된 모든 활성 대상이 들어간다(같은 identity라도 상태가 다르면 재실행).
2. 종속 목록(cascading select)은 명시 규칙으로 처리한다: 메뉴 항목 pick 뒤 같은 오버레이/다이얼로그 안의 다른 trigger를 열어 항목 집합을 인벤토리에 넣는다(`owner_items_hash`가 달라지면 새 대상). 이렇게 해야 153이 «관찰»되고 L99가 그것을 요구한다.
3. 검사기 잔여를 «발견 간선 − executed 간선»으로 재정의하고 `interactions.json`에 `states`(상태 키·인벤토리)와 `edges`를 넣는다. 필요 조작 표는 «조작 규칙»이고 «발견 규칙»(1·2)을 같은 절에 성문화해 검사기·드라이버·리뷰어가 같은 정의를 읽게 한다.
4. A8 수치를 설계에 적는다: 예상 상태 수·간선 수·소요 시간·`--max-steps` 근거. 예산 초과 시 `partial:true`가 «영구 red»로 이어지지 않게, 초과분을 사용자 승인 예외가 아닌 «재실행 분할(`--resume`)»로 닫는 경로를 둔다(도구 한계를 사용자 승인으로 닫는 구조는 잘못된 소유자다).

### #2 BLOCKER — A8 DS 부품이 role/ARIA 없이 그려져 열거 규칙이 핵심 대상(스크림·체크박스 상태·Dialog Esc)을 못 잡는다 [정합·일반화]

**근거**
- Dialog 스크림: `_ds_bundle.js` L1080~L1093 — `div`에 `onClick: onCancel`, `role`·`aria-modal` 없음, 카드(L1094~) 안에 버튼들이 있어 «하위에 다른 대상이 없는 요소»(설계 L39)가 아니다. L38·L40 «오버레이 = role dialog/alertdialog/menu/listbox 또는 aria-modal»에도 걸리지 않는다. → 스크림 click(g0-observed-review §5 #1의 필수 항목)·Dialog Esc(L70) 미요구.
- Checkbox: L1472~L1473 `label onClick: toggle`, `input`·`role=checkbox`·`aria-checked` 없음 → «핸들러 leaf → click 1회». L67의 2상태 규칙은 종류를 모르니 발동 불가 → 몰라요/못려요/윤달 **해제** 미요구(r3 권고 항목·oracle «toggle on/off»).
- 설계 §근거는 «시안의 다이얼로그·드롭다운은 `_ds_bundle.js`의 React 컴포넌트가 런타임에 그린다»고 인식하면서도(L7) 그 컴포넌트가 어떤 마크업을 내는지 확인하지 않았다. Select trigger·menu·menuitem·radio·IconButton은 ARIA가 있어 잡히지만(L2782~L2787·L2831·L2889·L1607~L1613·L628~L631) **성공 조건 5가 이름 붙인 «스크림·체크박스»는 정확히 ARIA가 없는 두 부품**이다.
- 폐쇄 장치로 남는 `--declared`(L41)는 «Coordinator의 소스 검토»이고, 1-1에서 본 대로 소스를 읽고도 «무관»으로 닫은 실패 메커니즘과 같다. 게다가 declared는 `selector`를 요구하는데 스크림 div는 class·id·role이 없어 안정 selector가 없다.

**권고**
1. 열거 규칙에 «핸들러 보유 조상(surface)»을 추가한다: React props/`onclick`/CDP 리스너가 붙은 비-leaf 요소도 대상이며, 조작은 «하위 대상 rect 밖의 한 점 click». identity에는 `surface:true`와 커버 비율을 넣는다.
2. 오버레이 판정을 기하로 보강한다: 루트 영역의 ≥80%를 덮는 `position: absolute|fixed` 요소(z-index 유무 무관)는 role이 없어도 오버레이로 등록해 Esc 1회·surface click 1회를 요구한다.
3. 토글 판정을 관찰로 한다: 어떤 대상을 click한 뒤 **그 요소 자신의 서브트리(아이콘 추가·배경 변화)만 바뀌고 다른 대상 추가/제거가 없으면** toggle 후보로 분류하고, #1의 상태 그래프에서 후속 상태의 같은 대상 click을 요구한다(2상태 규칙을 role 없이 구현).
4. 스니펫이 `discovery_stats`(role로 잡힌 대상 수 / 핸들러 휴리스틱으로 잡힌 수 / 핸들러 보유 비-leaf 수)를 기록하고, 검사기는 «핸들러 보유 비-leaf ≠ 0인데 surface 대상 0»을 결함으로 낸다.
5. §검증의 fixture 페이지(L130)는 반드시 A8 패턴(role 없는 스크림·`label onClick` 체크박스·label로 이름 붙은 trigger·같은 이름 «다음» 위저드)을 담아야 한다. ARIA가 완비된 fixture로만 통과하면 A8에서 실패한다.
6. `--declared`에 selector 대신 identity 기술자(`{role|surface, name, owner}`)와 «도달 경로 힌트»를 허용한다.

### #3 MAJOR — 정적 경로(`freeze_design`)의 HTML(JS 포함)·정적으로 동결된 `.dc.html`이 요구 밖이라 성공 조건 1이 문장대로 성립하지 않는다 [정합·일반화]

**근거**: 설계 L11 vs L97·L128; `check_design_evidence.py` L391(`source_observation`은 archive entrypoint에서만 허용); `design-acquisition.md` L20~L22는 `.dc.html`/JSX를 archive로 안내하지만 검사기는 `.dc.html`을 static collection으로 동결하는 것을 막지 않는다(A8 프로젝트 `20260905-2018-web-auth-screens`는 `로그인.dc.html`을 static으로 동결했다 — 구판 실패 빌드지만 경로 자체가 열려 있음을 보여준다). `workspace/eval/web-design-source-integrity/2026-09-07/fixture/requirements.md`의 정상 표본은 정적 HTML/CSS/**JS** 3단계 위저드(focus·선택·검토 상태)다 — JS가 만드는 상태가 있는데 설계상 조작 기록 의무가 없다.

**권고**: v2 요구의 트리거를 collection이 아니라 «entrypoint 또는 그 closure에 `script`/`component` kind 행이 있거나 인라인 `<script>`가 있음»으로 정의한다(`design_sources.resource_kind` L12~L17로 계산 가능). 스크립트가 전혀 없는 정적 HTML·이미지 단독만 «해당 없음». 그렇지 않으면 성공 조건 1을 «archive case에 한해»로 고쳐 쓰고 한계로 명시한다.

### #4 MAJOR — 서빙 바이트 ≠ archive 바이트를 기계가 못 잡는다(변형본·다른 URL) [정합·일반화]

**근거**: baseline/review.md #1 — `related-empty-trace.json` url `…/_empty-variant.dc.html`(PEOPLE=[] 변형본, 관찰 후 삭제)인데 `related-empty-source-observation.json`은 entrypoint `관계인.dc.html cf2fe348…`을 주장. 현행 검사기는 url을 `^https?://`로만 본다(L226). 설계 v2의 `entrypoint.sha256`·`url`도 자기 신고다. 같은 URL 경로에 수정본(예: 메뉴를 제거한 번들)을 서빙해도 탐지 불가.

**권고**: 드라이버가 `--url`의 응답 바이트와 manifest `dependencies`의 `status: ok` 행 전부를 fetch해 `served: {local_path: sha256}`로 기록하고, 검사기는 manifest 행과 대조한다(22회 fetch·비용 미미). url 마지막 세그먼트(percent-decode) = `entrypoint.path` basename 검사도 v1/v2 observation에 추가한다.

### #5 MAJOR — root selector를 좁혀 대상을 줄여도 감지되지 않는다 [정합]

**근거**: 설계 L38 루트는 Coordinator가 준다·L98 검사는 `root.found`뿐. `--root '[data-screen-label="관계인"] [data-cm-scroll]'`이면 Dialog(스크롤 상자 밖 형제)·addBar가 빠지고, role-overlay 합집합도 Dialog(role 없음)를 못 넣는다 → 행 4·뒤로만 실행 → 잔여 0 → 통과.

**권고**: 스니펫이 루트 요소 지문(tag·`data-screen-label`·자손 요소 수·rect)과 **`outside_root`**(문서 안·루트 밖에서 대상 조건을 만족한 요소 수·이름 표본)를 기록한다. 검사기는 `screen-meta.json`의 `screen_label`이 있으면 `root.selector`가 그것을 참조해야 하고, `outside_root.count > 0`이면 `excluded_regions`(knob 패널 등 selector·사유) 선언 없이는 결함으로 낸다.

### #6 MAJOR — «case 내 변이» 리뷰어 재량이 남아 r3 거짓 통과가 캡처 층위에서 재현된다 [정합]

**근거**: 설계 L121 «각 step의 결과 상태가 design-input case 또는 «case 내 변이»로 연결되는지 대조하고, 독립 렌더가 필요한 상태만 case 추가를 요구»; `native-review-r3.md` L64·L105·L139·L189의 논법은 정확히 «변이라 case 불요»다. 설계는 실행 전수(성공 조건 2)만 기계화하고 캡처 전수는 정의하지 않는다. 사용자 보고 원문은 «동결하지 않아»(=캡처)다.

**권고**: 기계 최소 규칙을 둔다 — `changes.added ≠ ∅`인 step(새 표면이 드러난 상태)마다 case id 또는 exclusion 행이 연결돼야 한다(`interactions.json`에 `case_links` 또는 별도 `state-cases.json`, 검사기 대조). A8에서 added≠∅는 메뉴 열림·다이얼로그 열림·단계 전이·윤달 출현·시·군 활성 등 20건 안팎이라 폭발하지 않는다. 그 밖(값만 바뀐 상태)의 캡처 여부는 리뷰어 재량임을 «수용된 한계»로 명시한다.

### #7 MAJOR — v1 면제 조건(`phase: finalize`·`g2_approved`)이 위조 가능하고 기존 프로젝트를 즉시 red로 만든다 [무손실·정합]

**근거**: `build-state.json`은 Coordinator가 쓰고 digest 밖이다(설계 L97 조건은 손 기입으로 만족). 호환성: A8 프로젝트 `.dddjango-web/` 9 빌드 중 archive 8 — `20260908-0143-web-chat-spine`(implement·g2 false)·`20260908-1534-web-chart`(implement·g2 **true**)·`20260912-1640-web-related-persons`(implement·g2 false)는 면제 밖 → 플러그인 갱신 즉시 inputs exit 2. `backstop.py`는 `--design-build` 없이 프로젝트의 모든 source-bearing build를 검사한다(`design-evidence.md` L25~L27·`backstop.py` L222~L243) → **프로젝트 전체 backstop red**. 또 `design-evidence.md` L36~L47의 이력 조건(`implementation_visual=verified`·`design_status=ready`·슬라이스 done)과 설계 L97 조건이 다르다.

**권고**: 면제 키를 기계 검증 가능한 G2 완료로 바꾼다 — `visual-evidence.json`이 존재하고 그 `input_digest`가 현재 입력 digest와, `implementation_digest`가 현재 `web/` 트리와 일치할 때(= `--phase visual` exit 0)만 v1 허용. 그 외는 v2 필수. 마이그레이션 영향(어떤 빌드가 red가 되는가·`_history`로 보내는 절차)을 설계와 릴리즈 노트에 명시한다. `check_design_evidence.py`가 build-state를 읽게 되면 «local bytes only» 계약 변경도 명시한다.

### #8 MAJOR — `--compare`의 exit·출력·기준 manifest·staging 출처가 느슨해 «미확인»을 닫는 길이 없거나 우회된다 [정합·무손실]

**근거**: 설계 L112~L114. (a) exit 3이 changed/added/removed/**carried**를 합친다 — A8은 PNG 4가 영구 carried(transcript L4653)라 재동결이 항상 3이고, «carried-only»를 어떻게 보고·종결하는지 없다. (b) `--compare-out`이 선택이라 «출력만이 근거»인 출력이 보존·digest되지 않는다. (c) 기준 manifest 경로를 Coordinator가 고른다(`_history/v4` 대조 가능). (d) `archive_design.py`는 출처를 모르므로 이전 보관본 복사 = same(2-4).

**권고**: exit 0 same / 3 changed·added·removed / **4 same-with-carried**로 분리; `--compare-out` 필수 + sha를 build-state·visual-check에 기록하고 수정 모드 G0 답변은 그 파일을 인용; 기준은 `design-input.json.manifests[0]`로 고정하고 `refreeze-diff.json`에 기준 sha를 기록해 리뷰어가 `archive_sha256`과 대조; `source` 경로가 BUILD 하위(design-ref·_history)면 자동 carried; «staging 출처는 기계가 검증하지 않는다 — fetch 도구 기록으로 리뷰어/사용자가 확인»을 한계로 명시; carried-only는 G0/수정 모드 배너에 «미확인 N(목록)»으로 표면화하고 사용자가 «미확인 수용 / export 제공»을 고른다(전체 export 제공은 `design-acquisition.md` §1의 정상 경로).

### #9 MAJOR — 비React 엔진·hover 메뉴·가상화/무한 스크롤에서 발견 실패가 잔여 0으로 통과한다 [일반화]

**근거**: 설계 L39 핸들러 감지는 `__reactProps$*`·`onclick`·`cursor:pointer`뿐(Vue/Svelte/vanilla `addEventListener`는 안 보임); L72 «hover는 motion-notes 채널» — hover로만 드러나는 **대상**은 모션이 아니다; 선행 계획의 «DOM에 없는 가상 목록은 source 보완 대상이며 수집 완료로 보지 않는다»(계획 기계 대조 설계 2)가 설계에서 사라졌다. 진단 §6도 «다른 엔진에는 다른 보충이 필요»라고만 적었다.

**권고**: Node 드라이버는 CDP `DOMDebugger.getEventListeners`로 엔진 무관 리스너를 열거한다(MCP 경로는 불가 → `collector.capabilities`에 기록·리뷰어 항목); hover는 «발견 조작»으로 추가한다(mouseenter 리스너/`:hover` 규칙 보유 요소에 hover 후 재인벤토리, 필요 조작으로는 요구하지 않음); 스크롤 가능한 컨테이너는 끝까지 스크롤 후 재인벤토리하고 `discovery_limits`(overflow 컨테이너·`aria-rowcount`·자식 수 급증)를 기록한다. 구현하지 않는 항목은 «해당 없음이 아니라 거짓 통과 가능»으로 한계에 적는다.

### #10 MAJOR — fill 표본이 inputmode/placeholder를 무시해 A8 등록 경로의 유효 상태를 만들 수 없다 [일반화]

**근거**: 관계인.dc.html L123 `input-mode="numeric" placeholder="1992.07.04"`·L447 `onDate`가 비숫자를 제거 → 설계 L72 표본 «검증 입력»은 빈 값이 된다. `fill`은 executed로 세지만 step2 유효(8자리) 상태에 도달할 수 없다(#1이 해결돼도 이 표본으로는 등록 경로의 step3·4를 못 연다).

**권고**: 표본 선택 규칙 — `inputmode=numeric|decimal|tel` 또는 `pattern`이면 placeholder의 숫자열(없으면 «12345678»), placeholder가 형식처럼 보이면 placeholder 원문, 그 외 «검증 입력». `--declared`에 대상별 `value`를 허용한다.

### #11 MINOR — `state_hash` 미정의·경로 재생 시 `before.state_hash` 대조 없음 [정합]

설계 L59는 «전후 상태 해시»를 기록하지만 정의가 없고, 재생 후 «대상 identity를 찾으면 조작»한다 — 다른 상태에서 같은 identity를 조작해도 executed가 된다. 권고: state_hash = canonical JSON(identity 집합·enabled·checked·value·url)의 sha; 재생 종점의 해시가 기록된 `before.state_hash`와 다르면 `unreachable`.

### #12 MINOR — exclusions의 `approval_quote`는 Coordinator가 쓰는 scope.md에 있으면 통과한다 [정합]

리뷰어가 «실제 사용자 승인인지» 감사(L100·L121)하지만 리뷰어는 transcript·발주서에 접근하지 않는다(A8의 실제 승인은 발주서 개정·transcript L3190에만 있었고 `existing-approval.md`로 복원됐다). 권고: 예외 목록을 **G0 배너 1급 항목**으로 표면화해 승인자인 사용자가 직접 본다(값싼 폐쇄); `scope_ref`는 가능하면 사용자 출처 문서(발주서 경로+sha)를 가리킨다.

### #13 MINOR — 필요 조작 표에 «메뉴 밖 mousedown»·«trigger 재클릭»이 없다 [정합]

r2 fail #2가 요구한 4항목 중 Esc·ArrowDown만 표에 있다(Arrow는 없음). 번들 L2735·L2787. 권고: 오버레이에 «밖 click 1회» 추가(항목 스크롤 밖의 점), trigger 재클릭은 #1 상태 그래프에서 자연 발생(메뉴 열린 상태의 trigger click).

### #14 MINOR — 리뷰어 호출 시 예상 판정 선기입 금지 문장이 없다 [정합]

선행 계획은 native 호출(L3741)의 pass 선기입을 문제로 짚고 후보 프롬프트에서 제거했으나 설계는 1.1.8~12 문단을 재도입하지 않는다(L124). 기계 잔여는 리뷰어와 무관하지만 남는 재량 채널(#2·#6·#12)은 선기입에 오염된다. 권고: step 5-7 입력 계약에 한 문장(«예상 판정·pass 예시를 전달하지 않는다»)만 넣는다.

### #15 MINOR — 조작 후 루트 소실(페이지 이탈)·비-loopback URL 처리가 미정의 [일반화]

설정 화면 행은 다른 `.dc.html`로 `location.assign`(설정.dc.html L145~L149), 뒤로는 `history.back`(관계인 L258~L260 → about:blank). 설계 L38 «루트 미발견은 실패»가 탐색 중 이탈에도 적용되면 스퓨리어스 실패. 권고: 이탈 step은 `url` 변화+빈 인벤토리로 기록하고 큐에 넣지 않는다; 드라이버는 loopback 외 URL을 기본 거부한다(실서비스 원본 전수 클릭 방지 — 성공 조건 4의 «정상 입력»에 실서비스 URL이 포함되면 부작용 때문에 실행 불가 = 통과 불가).

### #16 MINOR — native `select`·combobox가 owner 종류에 없다 [일반화]

L45 owner = menu/listbox/dialog/radiogroup. native select의 option은 owner 없이 이름만으로 identity가 되어 두 select의 같은 옵션(«서울»)이 순번 접미로만 구별된다(재생 불안정). 권고: `select`·`[role=combobox]`를 owner에 추가.

### #17 MINOR — 인증 필요 원본·iframe 렌더의 처지 미명시 [일반화]

인증은 로그인 페이지 → 루트 미발견 → 정직한 실패(단 `--storage-state` 옵션 부재). iframe: 루트가 메인 프레임에 일부만 있으면 부분 인벤토리로 잔여 0(거짓 통과). 권고: same-origin iframe 순회 또는 `--frame`; 인증은 옵션 명시.

### #18 MINOR(선택) — motion-notes «실측» 행이 interactions step을 인용하도록 [정합]

진단 §1 6행의 무근거 «실측»(m5) 재발 방지에 한 칸이면 된다. 설계가 motion-notes 판형 불변을 택했으므로 강제하지 않는다.

### #19 MINOR — 검증 계획이 성공 조건 5를 입증하기에 약하다 [정합]

- §검증 1(L134) «r3 산출 → exit 2»는 스키마 red라 검출력 증명이 아니다. 권고: r3의 123-step 로그를 **테스트 fixture로만** interactions 형식으로 변환해(규범상 금지된 «산문 파싱»은 배포 경로가 아니라 테스트 입력으로 한정) 잔여 계산이 미클릭 4·15·30건을 내는지 고정한다.
- §검증 3(L136) native 실행: oracle 독립성은 «/tmp 평가 폴더 미접근»을 프롬프트 경계로 명시해야 한다(coordinator-repair/prompt.txt의 «다른 실행·평가 기록을 찾아 읽지 마라» 선례). 환경 한계는 실측됐다(coordinator-live/result.md: Playwright MCP `EPERM ~/Library/Caches/ms-playwright`, CDP 50234 우회; OOM은 transcript L4976). 설계 L130 «저장소에서 playwright가 resolve되지 않는다» → native 실행 전 `--cdp` 경로와 브라우저 기동 주체를 확정해야 한다.
- 성공 조건 5의 «잔여 0»에 **«exclusions 0 또는 평가자가 사용자 역할로 승인한 행만»**을 더해야 한다. 그렇지 않으면 예외로 잔여를 지운 통과가 성공으로 집계된다.
- 대조군: 기존 지침 + 새 검사기는 interactions.json을 못 만들어 exit 2가 되므로 «기존도 통과하면 개선 주장 금지» 원칙이 자동 만족된다 — 검사기가 바뀌었을 때 대조군 정의를 명시하라(«구 Coordinator + 신 검사기»와 «신 Coordinator + 신 검사기» 둘 다 기록).
- A8 밖 표본이 없다. `web-design-source-integrity` fixture(정적 HTML+JS 위저드)와 `web-a8-visual-fidelity/role-browser-app/source.html`(focus 상태)을 수집기에 통과시켜 발견·실행 수를 기록하는 항목을 추가한다(#3·#9의 일반화 주장을 검증하는 유일한 길).

### #20 MINOR — 설계 §근거 문장 정정 [정합]

1-1대로 «JS를 안 봤다» 계열 서술을 «JS 조각을 봤으나 관찰 의무로 변환하는 규칙이 없었다(v3 L2503~L2512·v6 L4768~L4795)»로 고치고, 그래서 «리뷰어 소스 감사»가 폐쇄 장치가 될 수 없음을 §역할 경계에 반영한다(#2와 연결).

---

## 4. 검증됨 목록(공격했으나 견딤 — 근거 병기)

1. **층위 1 스키마 red**: A8 v5 12 case의 v1 observation은 `phase: implement`·`g2_approved: false`라 면제 밖 → prepare exit 2. (단 #7의 위조·호환성 문제는 별개.)
2. **층위 2 «차이 0»·«변경분 0» 차단**: `_ds_bundle.js`·`support.js`·tokens 11이 entrypoint 의존성 `ok`(source-manifest dependencies 24 ok) → carried면 exit 1(L113) → 1파일·13파일 대조로는 «동일» 불가. L4733의 «사실상 무변» 추론도 설 자리가 없다. (staging 출처 비검증은 #8.)
3. **작성자 면제 필드 차단**: «알 수 없는 필드는 결함»(L98)은 현행 exact-field 스타일(`check_design_evidence.py` L62·L217·L305)과 일관.
4. **`failed`·`unreachable` 미계수**(L99): 실행 실패를 성공으로 바꾸는 경로 없음.
5. **archive_sha256 변경 → per-case 재관찰 강제**: 현행 L220이 이미 하며 설계 L114가 이를 인용. r5 «offline 갱신 후 코더 반송» 사고(A8 build-state `coder_round_1_blocked`)의 재발 방지가 유지된다.
6. **backstop 자동 반영**: `backstop.py` L243이 `validate_inputs`를 호출 → 설계 L102 정합.
7. **이미지 단독 → 해당 없음**: L391 경로대로 archive가 아니면 observation 자체가 없다.
8. **identity가 값에 오염되지 않음**: Select trigger의 접근성 이름은 `<label htmlFor>`(번들 L2990~L2998)라 «관계»·«시 · 군»으로 고정 — 값 선택마다 새 trigger identity가 생기는 폭발이 없다. (부작용: 값 있는 Select 재열기 상태(r3 신규 case 34)는 #1 상태 그래프에서만 발견된다.)
9. **`interactions.json` 바이트가 digest에 포함**(L101): 수정 시 prepare·독립 검토·inputs 재실행이 강제된다(현행 review_digest L195~L201 방식과 정합).
10. **실제 Playwright 이벤트 요구**(L59): Dropdown의 «밖 click 닫힘»은 `document` mousedown 리스너(L2751)라 페이지 안 합성 click으로는 발동하지 않는다 — 실제 입력 요구가 근거 있음.
11. **오버레이가 루트 안**: `createPortal` 0건 → 루트 서브트리 열거로 Dialog 내부 대상은 잡힌다(스크림 자체는 #2).
12. **v6 대조가 산출물에 남지 않았다는 진단 §2**: transcript L5000~L5010 `git checkout -- build-state.json`으로 확인.

---

## 5. 한 줄 총평

**구현 진입 불가.** 재동결 대조(층위 2)는 `--compare`로 실제 실패 두 발화를 막지만(#8 보완 필요), 관찰 동결(층위 1)은 탐색·잔여 의미론(#1)과 role 없는 A8 DS 부품(#2) 때문에 설계 그대로면 A8에서 «잔여 0 = 거짓 통과»가 구조적으로 재현되고 성공 조건 5(스크림·체크박스·8/12/17/153)에 도달할 수 없다. 조건: #1(상태 그래프 탐색·발견 규칙 성문화·A8 예산)·#2(surface/기하 오버레이/토글 관찰·A8 패턴 fixture)를 «확정 계약» 절에 반영하고, #3~#8(정적 경로 범위·서빙 바이트 대조·root 지문·added≠∅ case 연결·v1 면제 키·compare exit/출처)을 결정한 뒤 재검토.
