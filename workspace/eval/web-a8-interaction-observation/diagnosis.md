# A8 다이얼로그 JS 조작 상태 미동결 — 진단

작성: 2026-09-13. 사용자 보고 원문: «dddjango-web이 정상 동작하지 않아. a8 워크트리를 보면 다이얼로그가 디자인 안에서 js로 완성이 되는데 이걸 동결하지 않아. 내가 명시적으로 확인하라고 하니깐 그제서야 했어.»

- 대상 build: `/Users/hyun/.herdr/worktrees/spring_dream_server/a8/.dddjango-web/20260912-1640-web-related-persons` (커밋 cc37b540 · 읽기 전용).
- 실행 플러그인: Phase 0 v1~v5와 09-13 10:22~10:33 KST의 첫 v6 대조는 dddjango-web 1.1.10(transcript 요약 명시). 11:41 KST에 1.1.12 설치·reload 후 12:00·12:20 KST의 `/dddjango-web` 재호출은 1.1.12.
- native transcript: `~/.claude/projects/-Users-hyun--herdr-worktrees-spring-dream-server-a8/54754273-a334-4a58-bdd0-88a043c4010c.jsonl` (5,012행). 아래 `L…`은 이 파일의 행 번호다.
- 같은 날 다른 세션의 교정 시도 기록: `workspace/plan/2026-09-13-web-a8-interaction-observation.md`. 그 실행 자료는 `/tmp/dddjango-web-a8-interactions-20260913/`·`/tmp/a8-interaction-evaluator-20260913/`에만 있고 `workspace/eval/`에는 아직 없다.

## 1. Phase 0 관찰·동결(v1~v5)에서 본 것과 보지 않은 것

| 항목 | 본/동결 여부 | 근거 |
|---|---|---|
| 디자인 JS 파일 바이트(`_ds_bundle.js` 115,341B sha `3d86061b…`, `support.js`) | 동결함 | `source-manifest.json` archive 행 · v3 재동결 때는 번들 diff까지 읽어 BottomSheet 조각을 추출하고 «관계인 무관» 판정(L2503·L2508) |
| JS가 그린 다이얼로그 자체(상세·삭제확인·폼 step1~4) | 실제 렌더·캡처·case 동결함 | 12 case `captures/*-original.png` · trace `state_transition_actions` = «navigate → wait mount → tap 행 → tap 수정하기 → tap 다음» |
| 다이얼로그 안에서 한 번 더 조작해야 JS가 만드는 상태(관계·태어난 시·시·도 Select 열린 메뉴, 체크박스 토글, 입력 focus, 스크림 클릭, Esc) | 보지 않음 → 동결 없음 | 12개 trace에 해당 조작 0건 · 열린 메뉴 캡처 0장 · step3 trace는 «열면 시간범위 description … 자리에서 여는 Select 드롭다운»이라 적고도 열지 않음 |
| 렌더 실측 `render-audit.json` | 목록 상태 텍스트 15개만 | 다이얼로그 상태 실측 0 |
| 독립 입력범위 검토 `coverage-review.md`(v5) | pass | «내부 토글 sub-state(step3 몰라요-체크 시 Select disabled 등)는 별도 동결 case로 잡지 않았다 — 커버리지 갭 아님» |
| `motion-notes.md` m5(Select open) | 출처 «스캔·실측» 표기 | 실측을 뒷받침할 trace·캡처 없음 — 실측 없이 실측이라 기록됨 |
| 컴포넌트 코드 열람(`Select.jsx f2d928ea774e`·`Dropdown.jsx ca82523d622c`·`Dialog.jsx 0622410245c1`) | 봤으나 관찰 의무로 이어지지 않음 | v3 재동결(09-13 00:24 KST · L2503~L2512)에서 번들 diff·BottomSheet 조각을 읽고 «관계인 무관»으로 닫음. 헤더 해시맵으로 컴포넌트 단위 대조를 한 첫 시점은 09-13 12:25 KST(L4778). 정확한 명제는 «JS를 안 봤다»가 아니라 «JS를 보고도 그것이 그리는 상태를 관찰 의무로 바꾸는 규칙이 없었다» — 그래서 «소스를 읽고 판단하는» 리뷰어 감사는 폐쇄 장치가 되지 못한다 |

시안 구조 사실: `관계인.dc.html`은 `sc-if` 분기 안에 `x-import component-from-global-scope="ChunmongDesignSystem_9ad494.Dialog"`·`Select` 등을 선언하고, 실제 DOM은 `_ds_bundle.js`의 React 컴포넌트(`function Dialog`, Select→Dropdown, role=menu/menuitem)가 런타임에 그린다. 포털(`createPortal`) 사용은 없어 오버레이도 화면 루트 안에 렌더된다.

## 2. 09-13 v6 재동결 대조 시간표(KST)

| 시각 | 발화·행동 | 근거 |
|---|---|---|
| 10:22 | 사용자: 공유 URL의 관계인 시안 «재동결하고 차이점 재동결해서 다시해» | L4426·L4489 |
| 10:27~10:33 | Coordinator: DesignSync로 `관계인.dc.html` 1파일만 수신·sha 대조 → «현재 저장된 관계인.dc.html은 동결된 v5와 동일합니다(차이 0)» | L4521~L4549 |
| 12:00 | 사용자: `/dddjango-web 시안이 변경되었어. 변경된 부분 재동결해` | L4624 |
| 12:20 | 사용자: «관계인 페이지랑 지금 동결해 놓은 것이랑 완벽히 동일하다는거야?» | L4747 |
| 12:13 | Coordinator: «토큰 파일 11개가 무변이므로 같은 폴더의 `_ds_bundle.js`·`_ds_manifest.json`도 사실상 무변» — 미확인을 추론으로 동일로 격상 | L4733 |
| 12:22 | Coordinator: 22파일 중 13파일 해시 동일, 9파일 미확인(`_ds_bundle.js`·`_ds_manifest.json`·`support.js`·oxlintrc·readme·PNG 4) 인정. 그래도 «재동결/재구현할 변경분은 0» | L4757 |
| 12:24 | 사용자: «진짜? 다이얼로그에서 관계를 클릭하면 나오는 드롭다운도 똑같아?» | L4759 |
| 12:25~12:31 | Coordinator: 그제서야 `_ds_bundle.js` 수신·전체 sha 대조(동일) · Select/Dropdown 소스 해시 대조(동일) · 나머지 파일도 해시 | L4768~L4841 |
| 13:46 | 사용자: «내가 직접 명령하지 않고도 드롭다운 같은 것을 dddjango-web 플러그인이 찾는지 확인을 해야 하니깐. 동결본을 드롭박스 찾아내기 전으로 롤백 가능해?» | L4980 |
| 13:49 | Coordinator: «v5에서 플러그인은 드롭다운 열림 상태를 자율적으로 커버하지 못했습니다. 이번에 확인된 건 사용자님이 직접 지목했기 때문» | L4994 |
| 16:09~16:10 | 사용자 «1번만해» → `build-state.json`을 cc37b540으로 롤백. v6 대조 기록은 산출물에 남지 않고 transcript에만 있음 | L4996~L5010 |

대조 결과 자체는 번들까지 동일이라 놓친 디자인 변경은 없다. 결함은 검증하지 않고 «차이 0»을 단언한 절차와, 조작으로만 드러나는 상태를 동결 대상에 넣지 않은 규범이다.

## 3. 같은 날 선행 교정 시도와 결과

`workspace/plan/2026-09-13-web-a8-interaction-observation.md` 기록: 프롬프트 개정 3회(발견 목록 우선 → G0/G1 진입 분리 → 발견 목록을 먼저 만드는 순서)와 행동 평가.

- 평가자 oracle(`/tmp/a8-interaction-evaluator-20260913/oracle.json`, sha `274e8da6…`): A8 원본 조작군 30 · 관계 8 · 시 12 · 시·도 17 · 시·군 153.
- `baseline/review.md`: fail(다른 사유 — 변형본 관찰·scope 구형·Toast 누락). Select 열림 누락은 nit로 강등.
- `g0-normal-negative/result.md`: fail이지만 여자 재선택·역방향 토글·메뉴 닫힘 등 발견 누락.
- `coordinator-live/result.md`: 실제 Chrome에서 case 12→33 · 조작 로그 86건. 전 항목 선택·삭제 확인 scrim 등 미관찰 잔존.
- `g0-observed-review/result.md`: fail이나 여자 재선택·윤달 해제 등을 같은 핸들러 nit로 낮춤.
- `coordinator-repair/native-review-r3.md`: **pass = 거짓 통과** — 선택하지 않은 관계/지역 항목을 같은 핸들러의 데이터 변이로 제외. 기존 `--phase inputs`도 exit 0.
- 메모의 결론: «프롬프트 순서 변경만으로 해결됐다는 가설은 기각 … 기계 대조 설계(구현 전 적대 검토)».

## 4. 원인

1. 증거 계약에 조작 대상이 없다. `check_design_evidence.py` `_source_observation`은 trace가 «비어 있지 않은 바이트»인지만 본다. 무엇을 조작했어야 하는지, 실제로 했는지의 집합이 정의돼 있지 않다.
2. 그 빈자리를 리뷰어 재량이 메운다. design-review-web G0는 `sc-if` 분기 전수성만 대조하고, «같은 핸들러» 면제를 막는 기계 규칙이 없다.
3. 재동결에 기계 대조 단계가 없다. `archive_design.py`는 파일별 sha manifest를 만들지만 이전 manifest와 대조하지 않아 Coordinator가 일부 파일만 손대조하고 «차이 0»을 말했다. 1.1.12가 넣은 산문 규칙(«한 화면 파일만 비교했으면 그 파일만 동일»)은 12:22 답변 형식에는 반영됐으나 결론은 그대로였다.
4. 프롬프트 보강은 세 번 실패했다(§3).

## 5. 저장소 상태(2026-09-13 확인)

- 작업 트리의 `dddjango-web/`·`codex-dddjango-web/`는 v1.1.7 태그 내용과 동일하고 plugin.json 버전 표기(1.1.12)만 다르다. 즉 1.1.8~1.1.12 규범 변경이 미커밋 상태로 되돌려져 있다. 사용자가 09-13에 «v1.1.7 되돌림 유지»를 기준선으로 확정했다.
- 선행 시도의 프롬프트 후보는 `/tmp/…/{final-plugin,discovery-first-plugin,mode-split-plugin}` 스냅샷에만 있고 저장소에는 없다.

## 6. 한계

- transcript의 Coordinator 발화는 자기 보고다. 도구 호출 기록(DesignSync `get_file` 대상 경로·Bash 설명·Read 대상)으로 교차 확인했다.
- 독립 검토 C(1-1)의 정정을 반영했다: §1의 «컴포넌트 코드 열람» 행은 처음에 «Phase 0에서 없음»이었으나 v3 번들 diff 열람 사실과 모순이라 «봤으나 관찰 의무로 이어지지 않음»으로 고쳤다. 원인 판정 §4는 그대로다.
- 기계 열거가 React 핸들러(`__reactProps$*`)에 기대는 부분은 이 시안 엔진의 사실이며 다른 엔진에는 다른 보충이 필요하다.
- Serena·Graphify는 워크트리에 opt-in 표식이 없어 사용하지 않았다.
