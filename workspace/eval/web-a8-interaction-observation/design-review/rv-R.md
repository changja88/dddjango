# rv-R — «적대 검토 반영 — 확정 계약»(K1~K8) 독립 재검토

- 대상: `workspace/design/2026-09-13-web-interaction-evidence.md`(이하 «D», 행 번호는 이 파일 — K1 L153~159 · K2 L161~171 · K3 L173~183 · K4 L185~192 · K5 L194~199 · K6 L201~208 · K7 L210~217 · K8 L219~226). 앞 절과 충돌하면 확정 계약이 우선한다는 규칙(D L3·L151)을 적용했다.
- 대조: `rv-A.md`·`rv-B.md`·`rv-C.md` · 진단 `diagnosis.md`(정정본) · 현행 검사기(`dddjango-web/scripts/check_design_evidence.py` = «C»·`archive_design.py` = «AD»·`backstop.py` = «BS») · `commands/dddjango-web.md`(«CMD», 작업 트리 = v1.1.7 본문) · `agents/design-review-web.md` · `skills/implementation-ui/references/design-evidence.md`(«DE»)·`design-acquisition.md`(«DA») · `Makefile`·`docs/DEVELOPMENT.md` §6 · 되돌린 diff `git diff dddjango-web--v1.1.7 HEAD -- dddjango-web/`(작업 트리는 v1.1.7과 `plugin.json` 1파일만 다름을 `git diff --stat`으로 확인) · A8 원본(읽기 전용 · 경로 접두 `A8/` = `~/.herdr/worktrees/spring_dream_server/a8/.dddjango-web/20260912-1640-web-related-persons/`): `design-ref/관계인.dc.html`(«H») · `design-ref/_ds/…/_ds_bundle.js`(«BJ», 3,403행) · `design-ref/support.js` · `source-manifest.json` · `design-input.json` · `screen-meta.json` · `build-state.json` · `captures/*-trace.json`.
- 방법: 정적 읽기(python3 텍스트 검색). 서버·브라우저·`make verify` 미실행. A8 산출물 무수정(git 조회는 `status`·`ls-files`만). Serena·Graphify는 워크트리에 opt-in 표식이 없어 사용하지 않았다.
- 표기: 심각도 BLOCKER / MAJOR / MINOR / 검증됨. 3축 **정합**(현행 검사기·규범·미러) · **일반화**(A8 밖) · **무손실**(거짓 통과·기존 보장 손실 없음). «추측»은 파일로 확인하지 못한 판단이다.

---

## ① 해소 표

판정: **해소** = K 문장이 원 발견을 닫고 새 문제를 만들지 않음 · **부분** = 방향은 맞으나 정의·범위가 부족하거나 K 반영이 새 결함을 만듦(④의 번호로 연결) · **미해소** = K에 대응 문장이 없음.

### rv-A

| 발견 | 판정 | 닫는 문장 / 부족한 이유 |
|---|---|---|
| A-B1 탐색 종결+identity 미도달 | **부분** | K1 L155 큐 키 `(identity, action, option, context)`·L156 잔여 단위·L159 드라이런 게이트가 방향을 닫는다. 그러나 context에 «select 트리거별 face»를 넣은 정의가 A8에서 자기 face N² 재큐잉을 만들어 `--max-depth 12`·`--max-steps 6000`·45분을 넘긴다(②·④-R1). 게이트가 잡겠지만 «미달 상태로 규범을 바꾸지 않는다»가 곧 «설계 문장으로는 A8 미통과»다. |
| A-B2 실행 환경·MCP 비동등 | **해소** | K5 L196 단일 함수 파일·Node/MCP 같은 바이트·`driver_sha256`·L197 blocked enum. 남는 것은 `filename` 경로의 `opts` 전달 불명(④-R14, MINOR). |
| A-M1 스크림 leaf 제외/거짓 실행 | **해소** | K2 L163 «핸들러 보유=대상, 후손 유무 무관»·L164 클릭 지점·`unclickable`. A8 스크림(BJ L1080~1093 `onClick: onCancel`, 카드 L1095 `stopPropagation`)이 대상이 된다. |
| A-M2 role 의존 오버레이·owner | **해소** | K2 L165 구조 오버레이(루트 80%·absolute/fixed·핸들러/z-index)·L167 owner에 구조 오버레이 추가. A8 Dialog(role 0건, BJ L1065~1095)가 잡힌다. |
| A-M3 checked 미관찰·인벤토리 스키마 | **부분** | K2 L166 `surface` sha·K1 context의 checked/face·K3 L179 state_hash 항목은 있다. 그러나 앞 절 L84~88의 `interactions.json` 스키마(`targets[id].enabled` 단일값·`inventory` = id 목록)는 갱신되지 않았다 — K1 L156 «어느 context에서든 활성으로 관찰된 단위»를 계산하려면 인벤토리 항목별 `enabled·checked|face·value_empty`가 필요하다(A-M3 권고의 핵심). 확정 계약에 스키마 v1 재정의가 없다(④-R17). |
| A-M4 cursor 상속 오탐 | **해소** | K2 L163 «CDP 없을 때만·자기 computed cursor가 부모와 다른 요소 한정»·`aria-hidden` 제외. |
| A-M5 잔여·exact-field·접미·state_hash 미정의 | **부분** | K1 L156 잔여 단위 표·K3 L179 state_hash·L180 exact-field 재귀+반례 목록은 닫힌다. **순번 접미**(앞 절 L45)는 K에 언급이 없다 — «충돌 시에만 dom_path» 권고 미반영. A8에서는 행 이름이 달라 발동하지 않으나(A V5) 일반화 축 미해소. |
| A-M6 스니펫·root 미검증 | **해소**(단 ④-R7) | K3 L175 byte 대조·L176 root 규칙·`outside_root`·`excluded_regions`. 다중 entrypoint build에서 root 규칙이 오작동한다(④-R7). |
| A-M7 v1 허용의 build-state 결합 | **부분** | K3 L183 «prepare/inputs는 예외 없이 v2·backstop 순회에서만 git 무변경 시 legacy» — build-state 결합은 끊겼다. 그러나 «`--diff-base` 대비»만 허용해 A-M7 권고의 «또는 HEAD»가 빠졌고, `--diff-base` 없는 전역 퇴화 실행(BS L197~200·DE L25~27)에서 과거 build 전부가 exit 2가 된다(④-R9). |
| A-M8 approval_quote 자기 인용 | **해소** | K3 L181 stdout 전량·G0 배너 1급·NFC/공백 정규화·앵커 실존·10% 상한. |
| A-M9 compare 출처·carried-only exit 3 | **부분** | K4 L187 exit 4 분리·L189 자동 carried·`carried_from`·mtime 표. 그러나 «source 경로가 BUILD 하위면 자동 carried»가 A8의 실제 staging 관행(`source-manifest.json` `source_root` = `A8/_raw-export`, BUILD 안)과 충돌해 전 파일 carried가 되고(④-R5), `carried_from` 행 필드가 현행 검사기의 exact-row 규칙(C L304~306)에 걸린다(④-R6). |
| A-M10 navigation 미정의 | **해소** | K2 L169 터미널 step·loopback 기본. |
| A-M11 SKIP 정책 | **해소** | K5 L198 순수 함수 항상·DOM fixture env 게이트·`release-web` 선행(SKIP=실패). |
| A-m1 unpkg 런타임 | 미해소(MINOR) | K에 외부 스크립트 로드 실패의 오류 코드가 없다. served 대조(K3 L177)는 same-origin에 한정돼 충돌은 없다. |
| A-m2 digest 중복·`--declared` 미포함 | 미해소(MINOR) | K에 언급 없음. 선언은 대상을 늘리기만 하고 결과는 `interactions.json`(digest 포함)에 반영되므로 거짓 통과 통로는 아니다. |
| A-m3 viewport | **부분** | K3 L178 «= case viewport»로 답했으나 A8 캔버스 관찰 관행·DE L174~176과 충돌(④-R8). |
| A-m4 fill 표본 | **해소** | K2 L170. |
| A-m5 면제 금지 문장 | **해소** | K6 L203. |
| A-m6 비용 상한 | **해소**(수치는 ②) | K1 L158 `--max-minutes`·결정적 최적화 1종. |

### rv-B

| 발견 | 판정 | 닫는 문장 / 부족한 이유 |
|---|---|---|
| B-B1 스크림 leaf | **해소** | K2 L163~165 + K5 L198 fixture(부모 스크림+stopPropagation 패널) + K7-1 «스니펫 발견 vs 선언으로 닫힘» 구별 집계. |
| B-B2 «case 내 변이» 재량 = 1.1.11 재도입 | **부분** | K6 L203이 문장을 삭제하고 K3 L182가 기계 규칙(`reached_by`·`after.capture` 일치·added/removed/navigated step의 연결 의무)을 둔다 — 의도는 닫혔다. 그러나 B-B2 권고 2의 `added ≠ ∅ ∨ url`에 설계가 `removed ≠ ∅`를 **추가**해 A8에서 메뉴 항목 선택 190건 전부가 연결 의무 step이 되고(항목 pick = 메뉴 removed), K1 context 재실행과 곱해져 수백~수천 건이 된다. 12 case + 예외 ≤ 10%로는 영구 exit 2다(④-R2, BLOCKER). 또한 앞 절 L121의 «독립 렌더가 필요한 상태만 case 추가» 문장이 본문에 그대로 남아 있다(⑤). |
| B-M1 v1 완료 이력 허용 | **부분** | A-M7과 동일(④-R9). |
| B-M2 MCP 대체 = LLM 루프 | **해소** | K5 L196 «LLM이 탐색 루프를 도구 호출로 흉내 내는 경로는 없다»·같은 파일 실행·sha 대조. B는 삭제를 권했으나 «같은 코드»면 B의 근거(P3)는 해소된다. Codex 비대칭은 K6 L205 경로 표기로 처리. |
| B-M3 매 수정 모드 원격 전량 수신 | **해소** | K4 L190 «사용자가 요청했을 때만·step 4 질문은 v1.1.7 그대로». |
| B-M4 `--carried` 완화·처분 공백 | **부분** | B의 «부득이 유지 시 ①②③»(closure 밖 한정·`carried_from`·carried-only exit/후속 표)이 K4 L187~191에 전부 있고 K8-3으로 결정 게이트에 올렸다. 구현 정합은 ④-R5·R6에서 깨진다. |
| B-M5 `_history` 절차 출처 | **해소** | K4 L192 «규범으로 두지 않는다·git 보존» + K8-2. 단 앞 절 L114 «기존 절차대로 `_history/vN` 보존»이 남아 독자가 헷갈린다(⑤·④-R18). |
| B-M6 큐 vs 잔여 어긋남 | **해소** | K1 L155~157 «한 표·두 구현» + fixture 동일성 테스트. |
| B-M7 선언 미매칭 교착 | **부분** | K1 L156 «기계가 발견하지 못한 대상은 잔여가 아니다»로 교착의 논리적 근거는 사라진다(미매칭 선언은 관찰된 적이 없어 잔여 밖). 그러나 앞 절 L41 «선언 대상도 열거·실행 의무가 같다»가 그대로이고, B가 요구한 `declared_unmatched` 기록과 리뷰어 대조(K6 ②는 «사유»만)가 명시되지 않았다(④-R16). |
| B-M8 Node/Playwright 정책 | **해소** | K5 L197 + K8-1 + REQUEST_GUIDE 문단(단 범위표 L21~30에 REQUEST_GUIDE·Makefile·DEVELOPMENT.md가 없다 — ④-R15). |
| B-M9 hover 제외 | **해소** | K2 L168 발견 조작 + K8-4. |
| B-M10 미러·배포 빈칸 | **해소** | K6 L204~206 (a) `node_modules` 금지 (b) references cmp (c) 경계 절·커밋 목록 (d) `${CLAUDE_PLUGIN_ROOT}`/`${SKILL_DIR}`·`import.meta.url` (e) K7-6 validate. `_staging-ref`·`_staging-manifest.json`의 위치·정리·커밋 여부는 여전히 없다(④-R12). |
| B-m1 금지문 누적 | 미해소(MINOR) | 앞 절 L114 금지문 그대로. |
| B-m2 «범용 탐색 엔진 안 만든다» vs BFS 드라이버 | 미해소(MINOR) | 앞 절 L19 그대로 — 이탈 사유 미기재. |
| B-m3 이중 기록 | **해소** | K3 L182 `reached_by`. |
| B-m4 바깥 클릭 | **부분** | K2 L165 `click:outside` 추가. 정의가 스크림형에만 맞고 메뉴형(role=menu, 스크림 없음)에는 닫힘 전이를 만들지 못한다(④-R10). |
| B-m5 SKIP 로그 | **해소** | K5 L198. |
| B-m6 focus 이중 소유 | 미해소(MINOR) | K에 한 줄 없음. |
| B-m7 exit 3 문서화 | **해소** | K4 L187·앞 절 L123(design-evidence.md에 exit 기재). |
| B-m8 compare-only | 채택 안 함(허용) | K4는 보관 후 대조 유지. |
| B-m9 정적 경로 한계 | **해소** | K6 L207 + K8-6. |

### rv-C

| 발견 | 판정 | 닫는 문장 / 부족한 이유 |
|---|---|---|
| C#1 identity-novelty BFS·예산 | **부분** | A-B1과 동일. C#1 권고 4의 «`--resume` 분할» 대신 K1 L158은 상한 도달 = `partial:true`뿐이라 상한 초과가 영구 red다(②). |
| C#2 role 없는 부품 | **해소**(fixture는 부분) | K2 L163~167(surface·기하·토글 관찰). C#2-5가 요구한 A8 패턴 fixture 중 «label htmlFor 트리거·같은 이름 «다음» 위저드·cascading select»가 K5 L198 fixture 목록에 없다 — K1 context 분기의 회귀 고정이 순수 함수 테스트에만 기댄다(④-R19). |
| C#3 정적 경로 script kind | **해소**(범위 결정) | K6 L207 후속 후보·한계 명시. |
| C#4 서빙 바이트 | **해소** | K3 L177. percent-decode·404 처리 미기재(④-R20). |
| C#5 root 좁히기 | **해소**(④-R7) | K3 L176. |
| C#6 «case 내 변이» | **부분** | B-B2와 동일(④-R2). |
| C#7 v1 면제 | **부분** | A-M7과 동일(④-R9). |
| C#8 compare exit·출처·기준 manifest | **부분** | K4 L187~189 exit 4·`--compare-out` 필수·`manifests[0]` 고정·자동 carried. 정합 결함 ④-R5·R6·R11. |
| C#9 비React·hover·가상화 | **해소** | K2 L163 CDP·L168 hover/스크롤 발견·`discovery_limits`·L171 한계. |
| C#10 fill 표본 | **해소** | K2 L170. |
| C#11 state_hash·재생 대조 | **해소** | K3 L179. |
| C#12 approval_quote 배너 | **해소** | K3 L181. |
| C#13 메뉴 밖 mousedown·trigger 재클릭 | **부분** | trigger 재클릭은 K1 context(메뉴 열림 상태)로 자연 발생. 메뉴 밖 mousedown은 ④-R10. |
| C#14 pass 선기입 금지 | **해소** | K6 L203. |
| C#15 이탈·비 loopback | **해소** | K2 L169. |
| C#16 native select owner | **해소** | K2 L167. |
| C#17 인증·iframe | **해소**(④-R21 모순) | K2 L171. `--cdp` 로그인 경로는 원격 URL인데 L169가 원격을 기본 거부한다. |
| C#18 motion-notes 인용 | **해소** | K6 L208 권고. |
| C#19 검증 계획 | **해소** | K7 L212~216 전 항목(r3 fixture·평가 폴더 미접근·예외 0·대조군 2종·A8 밖 표본). |
| C#20 근거 문장 정정 | **해소** | D L7 «JS를 «안 본» 것이 아니라 … 규칙이 없었다». |

집계: 해소 33 · 부분 15 · 미해소(전부 MINOR) 6.

---

## ② K1 실효성 — A8 소스로 큐 추적

전제: K1 L155 큐 키 = `(identity, action, option, context)`, context = 활성 대상 identity 정렬 목록 + checked + **select/combobox 트리거별 face** + 텍스트 입력 비어 있음 + surface. K2 L163 «핸들러 보유=대상», K2 L165 구조 오버레이, K2 L166 surface 토글. 소스 사실: Select 트리거 이름은 `<label htmlFor>`(BJ L2990~2991) → 값과 무관하게 «관계»·«시 · 도»·«시 · 군»; 항목 pick은 `onSelect` 뒤 `closeOnSelect`로 메뉴를 닫고(BJ L2763~2767) face가 `current.label`로 바뀐다(BJ L2761); 위저드는 sc-if로 이전 step의 대상을 DOM에서 제거한다(H L112~151); 삭제는 행→IconButton 삭제하기(H L89)→확인 삭제하기(H L103) 3조작(H L273~279).

### 2-1. 도달 여부(도달 자체는 성립)

| 대상 | K1/K2로 큐에 들어가는가 | 근거 |
|---|---|---|
| 등록 위저드 step 2~4 | **들어간다** | 등록 step1(이름 비어 있음·관계 face=placeholder)과 편집 step1(이름 채움·face=배우자)의 context가 달라 «다음»이 두 context에서 실행된다. 등록 경로는 `fill`(K2 L170 표본: 이름 «검증 입력», 생년월일 placeholder `1992.07.04` 숫자열 — H L123·L447 필터 통과) + 관계 pick 뒤 «다음»이 step2를 연다. 편집 경로는 값이 차 있어 «다음»×3으로 step4까지. |
| 도별 시·군 153 | **들어간다** | 시·도 항목 pick 뒤 `cityDisabled`가 풀려(H L438) 시·군 트리거가 활성 목록에 새로 들어오고 face(시·도)도 바뀌므로 새 context → 시·군 트리거 재실행 → 도별 항목(owner_items_hash 상이) 발견. 9개 도 합 153(H L200~209 합산 31+18+11+15+14+22+22+18+2). |
| 삭제 확인 스크림·바깥 클릭·Esc | **들어간다** | K2 L165 구조 오버레이(BJ L1080~1093 `position:absolute; inset:0` + onClick) → `click:outside`·`key:Escape` 각 1회. 확인 «삭제하기»는 owner(확인 오버레이 identity)가 IconButton(상세 오버레이)과 달라 별개 identity — A-B1의 병합이 풀린다. |
| 체크박스 2상태 | **들어간다** | BJ L1472~1473 `label onClick`·input 없음 → K2 L166 surface sha; 1회 클릭 뒤 surface(check 아이콘 추가, BJ L1497)가 바뀌어 새 context → 같은 대상이 option=이전 surface로 재실행. 몰라요 체크 시 Select disabled(H L135)도 context에 반영. |
| 빈 목록(전 항목 삭제) | **경로는 존재하나 상한에 걸린다** | 4명(H L167~179)×3조작 = 경로 길이 12. 12번째 step은 실행되지만 빈 상태에서 새로 큐에 들어가는 «관계인 등록하기»(빈 context)·«뒤로»는 경로 13 → `--max-depth 12`(K1 L158) 초과 → `caps_hit` → `partial:true` → 검사기 exit 2. **산술이며 추측이 아니다**(④-R3). |

### 2-2. 폭발(값 조합)이 다시 생기는가 — **생긴다(자기 face N²)**

- 관계 트리거를 열어 «배우자»를 pick하면 메뉴가 닫히고 트리거 face가 «배우자»가 된다. context에 face가 들어 있으므로 step1의 **모든** 대상(트리거·이름·여자·남자·닫기·다음·스크림)이 새 키로 다시 큐에 들어가고, 그중 관계 트리거를 다시 열면 8항목이 «face=배우자» context의 새 키로 들어간다 → «연인» pick → face=연인 → 또 전부 재큐. 즉 항목 N개 메뉴 하나가 N×N 항목 실행 + N회 재열기를 만든다.
- A8 규모: 관계 8²=64 · 시 12²=144 · 시·도 17²=289 · 시·군 Σnᵢ² = 31²+18²+11²+15²+14²+22²+22²+18²+2² = 3,123 → 항목 실행만 ≈ 3,620, 재열기·동반 대상 재큐(context당 6~8건)를 더하면 ≈ 7,000 키(**추측** — 알고리즘 추적 기반). `--max-steps 6000` 초과.
- 깊이: 시·군 항목 최단 경로 [행, 수정하기, 다음, 다음, 다음, 시·도T, 시·도항목, 시·군T] + 항목 = 9. 재열기 사슬은 2씩 늘어(항목→트리거→항목) 11·13 → `--max-depth 12` 초과.
- 시간: step당 새로고침 + 경로 재생 8~11조작(각 ≈ 0.2~0.4s + 250ms 정적 대기) ≈ 4~6s → 7,000 step ≈ 8~11시간(**추측**). K1 L158의 결정적 최적화(접두 상태 해시 일치 시 재생 생략)는 형제 항목이 상태를 바꾸므로 메뉴 항목에서 거의 발동하지 않는다.
- 자유 텍스트는 제외돼 있고(K1 L155), step 간 select face는 sc-if로 DOM에서 사라져 곱해지지 않는다. 폭발은 «cross-product»가 아니라 **트리거 자기 face의 재귀 재큐잉**이다. 처방: context의 face에서 «방금 pick한 항목의 owner 트리거 자신»을 제외하거나, face를 «다른 트리거의 face»로 한정한다(cascading 발견은 시·군 트리거의 enabled 전이만으로도 성립 — H L438). 이 수정은 잔여 단위(K1 L156)에 영향이 없다.

### 2-3. 가림(occlusion)이 실행 시간을 곱한다(④-R4)

다이얼로그가 열려도 뒤의 행 4개·«뒤로»는 DOM에 남고 `aria-hidden`·`inert`가 없다(BJ L1080~1095에 형제 처리 없음). K2 대상 조건 «보이고 disabled가 아닌 것»에 가림 규칙이 없으므로 이들이 모든 다이얼로그 context의 활성 대상으로 열거·큐잉된다. 실제 Playwright click은 클릭 지점의 hit target이 다른 요소(스크림)면 재시도 뒤 타임아웃한다(**추측** — actionability 규칙) → 대상당 10s(앞 절 L60) × 5 × 다이얼로그 context 수(수십~수백) = 수십 분~수 시간이 `failed`로 소모된다. 잔여에는 영향이 없지만(같은 identity가 목록 context에서 executed) 45분 상한을 잡아먹는다.

### 2-4. 45분 상한 추정

- 설계 문장 그대로: 통과 불가(2-2·2-3·2-1 빈 목록). 드라이런 게이트(K1 L159)가 이를 잡고 «context 구성을 바꾸고 계획에 적는다»고 하나, 바뀌는 것은 K3 동결 연결의 step 수에도 직결되므로(③) 설계 수준에서 정해야 한다.
- 자기 face 제외 + 가림 제외 + `--max-depth ≥ 14` 적용 시: 큐 ≈ 메뉴 항목 190 + 트리거·버튼·토글·입력 ≈ 100 + context 재실행(성별 2·이름 2·역법 2·윤달 2·몰라요 2·삭제 부분집합 ≤ 15 등) ≈ 500~1,200 → step당 4~6s → **35~120분**(**추측**). 45분 기본값은 A8에 부족할 가능성이 높다. 상한 도달이 `partial`=영구 red로만 처리되므로 `--resume` 또는 기본값 상향이 필요하다.

---

## ③ K3 동결 연결의 부작용

1. **BLOCKER — 연결 의무 폭발(④-R2).** K3 L182 «`changes.added ≠ ∅` 또는 `removed ≠ ∅` 또는 `navigated`인 step은 어느 case의 `reached_by` 또는 예외 행이 가리켜야 한다». 메뉴 항목 pick은 메뉴를 닫으므로(BJ L2767) 항상 `removed ≠ ∅` → A8에서 항목 pick 190건이 각각 case 또는 예외를 요구한다. 다이얼로그 닫기(닫기·취소·스크림·Esc), 위저드 이전/다음, Esc/바깥 클릭 닫힘도 전부 added/removed다. K1 context로 같은 전이가 context마다 별개 step이 되면 수백~수천 건. A8 case는 12(`design-input.json`), 예외 상한은 활성 대상(≈235)의 10% ≈ 23. 산술적으로 닫을 수 없다 → prepare/inputs 영구 exit 2. B-B2 권고 2·C#6 권고는 `added ≠ ∅ ∨ url`이었고 C#6은 «20건 안팎»을 identity-novelty BFS(각 표면 1회) 기준으로 셌다. 설계가 `removed`를 더하고 K1이 재실행을 곱해 전제가 무너졌다. 처방: 의무 단위를 step이 아니라 **표면 키**(after 상태의 활성 identity 집합에서 face·checked·value·owner_items_hash를 뺀 canonical sha)로 두고 `added ≠ ∅`인 표면 키마다 case 1개 또는 예외 1행(어느 step이든 1개 연결)으로 정의한다. `removed`만 있는 step(닫힘·pick)은 의무 밖.
2. **MAJOR — 참조 캡처 = 드라이버 바이트 + viewport 동일 강제가 A8 관찰 관행과 충돌(④-R8).** K3 L182 «원본 캡처는 전부 드라이버가 저장한 바이트», L178 «`interactions.viewport` = case viewport». A8 12 case의 trace는 «rendered at 560x1040 viewport, clipped to frame 390x844»(`captures/related-form-step3-trace.json` `canvas`)이고 DE L174~176은 엔진 캔버스에서 브라우저 viewport와 콘텐츠 크롭을 따로 기록하라고 한다. 390x844 viewport로 열면 바깥 `padding: 40px`(H L35)과 AppFrame `padding: 24`·`maxWidth: 100%`·`maxHeight: 100vh`(BJ L2189·L2205~2208, `fit` 기본 `device` L2163)로 프레임이 310px 폭으로 줄어 기존 캡처와 다른 렌더가 된다. 결과: (a) 기존 12 case 캡처 전부 폐기·재캡처(사용자 결정 미표기 — ⑥) (b) 드라이버에 «루트 rect 크롭 + 별도 브라우저 viewport» 옵션이 없으면 A8은 K3를 만족하는 캡처를 만들 수 없다. `interactions.json`에 `browser_viewport`·`content_crop`을 두고 검사기는 `content_crop == case.viewport`를 요구하는 형태가 DE와 정합이다.
3. **MAJOR — 빈 목록 도달이 `--max-depth 12`에 정확히 걸린다(④-R3).** ②-1 표 참조. K3 L182 «빈 목록 같은 데이터 의존 상태도 UI 조작(전 항목 삭제)으로 도달해 동결»과 `_empty-variant` 금지(A8 `related-empty-trace.json` url `_empty-variant.dc.html`이 정확히 이 통로였다)는 옳다. 기본 깊이를 올리거나 «데이터 행 n개 × 삭제 3조작»을 상한 산정에 넣어야 한다.
4. **수용된 한계의 범위(명시 권고).** «값만 바뀐 step은 연결 의무 없음»(K3 L182)이라 체크박스 토글(surface 변화 = 대상 추가/제거 없음)·«몰라요» 체크로 Select가 disabled 되는 상태(인벤토리에 `enabled:false`로 남으면 removed가 아님)는 동결 의무가 없다. 진단 §1이 «보지 않음»으로 꼽은 «체크박스 토글»의 캡처는 여전히 리뷰어 재량이다 — 설계가 스스로 «수용된 한계»라 적었으나 어느 A8 상태가 여기 해당하는지(윤달 체크 상태·몰라요 체크 상태 2×3)를 D에 적어야 한다.
5. **예외 10% 상한과의 상호작용.** 상한(K3 L181)은 잔여 예외와 연결 예외를 합쳐 센다. 1의 처방 없이는 상한이 먼저 소진되고, 처방 뒤에도 표면 키 수(A8 ≈ 메뉴 열림 4종 + 도별 시·군 9 + 다이얼로그 3 + 위저드 step 4 + 오류 + 빈 목록 ≈ 25~35)가 12 case를 넘으므로 Coordinator가 case를 20~25개 추가해야 한다 — 사용자 결정 ①(관찰 동결)의 취지에 맞으나 비용을 K8에 적어야 한다(⑥).
6. **`step 0` 초기 캡처의 스키마 부재(MINOR).** K3 L182 «초기 상태는 step 0»인데 앞 절 L85 `steps[].n`은 1부터다. `initial: {inventory, state_hash, capture}` 같은 자리가 스키마에 없다.

---

## ④ 새 발견(심각도순)

### R1. [BLOCKER · 무손실·일반화] K1 context의 «트리거 자기 face»가 A8에서 N² 재큐잉을 만들어 모든 상한을 넘긴다
근거·수치는 ②-2. 설계의 드라이런 게이트가 잡더라도 «context 구성 변경»은 K3 연결 step 수와 K7 집계에 직결되므로 계획이 아니라 설계 문장으로 확정해야 한다. 처방: face를 «pick 대상의 owner 트리거를 제외한 다른 트리거의 face»로 정의하거나, «메뉴 항목 pick 뒤에는 그 owner 트리거의 face 변화만으로는 재큐하지 않는다»는 규칙을 K1에 넣는다. 잔여 단위는 불변.

### R2. [BLOCKER · 정합·무손실] K3 동결 연결 의무가 `removed ≠ ∅`까지 포함해 A8에서 산술적으로 충족 불가
근거·수치·처방은 ③-1. 이 상태로 구현하면 성공 조건 5의 «inputs exit 0»이 A8에서 나올 수 없다.

### R3. [MAJOR · 무손실] `--max-depth 12` 기본값이 «전 항목 삭제로 빈 목록 도달»(4명 × 3조작 = 12, 이후 탐색 13)과 충돌
③-3. A8 `PEOPLE` 4명(H L167~179)·삭제 3조작(H L273~279·L89·L103). 기본값 ≥ 14 또는 «데이터 행 수 기반 산정»을 K1에 명시.

### R4. [MAJOR · 무손실·일반화] 가림(occlusion) 규칙이 없어 오버레이 뒤 대상이 모든 다이얼로그 context에서 열거·실패(10s)된다
②-3. 처방: 대상 조건에 «선택한 클릭 지점의 `elementFromPoint`가 자기 또는 후손일 것»을 넣고, 아니면 `occluded`로 열거만 한다(활성 대상·context에서 제외). 이 규칙이 없으면 K1 context가 «뒤의 목록 부분집합»까지 포함해 위저드 전체가 목록 상태 수(2⁴)만큼 재탐색된다(**추측** — context 정의 문장에 따른 귀결).

### R5. [MAJOR · 정합·무손실] K4 «staging 파일의 source 경로가 BUILD 하위면 자동 carried»가 A8 staging 관행과 충돌해 전 파일이 carried가 된다
`A8/source-manifest.json` `source_root` = `…/20260912-1640-web-related-persons/_raw-export`(BUILD 안). CMD L134는 «`design-ref/`와 겹치지 않는 허용 staging»만 요구하고 BUILD 밖을 요구하지 않는다. 이대로면 K7-4의 기대 «same 18·carried 4·exit 4»가 아니라 «carried 22·exit 4»가 되고, 사용자는 매번 «미확인 22 수용»을 묻는 배너를 본다. 처방: 자동 carried 조건을 «source가 `reference_root`·이전 `_staging-ref`·이력 폴더 하위»로 좁히고, staging 위치를 «BUILD 밖 또는 BUILD 안 `_staging-*`»으로 명시.

### R6. [MAJOR · 정합] `carried_from` 행 필드가 현행 검사기의 exact-row 규칙에 걸린다
C L304~306: `required_row` + `requested_source` 외 필드는 «invalid source-manifest row fields» → exit 2. K4 L189가 새 manifest 행에 `carried_from`을 넣으라 하지만 D의 변경 목록(L25·K3 L180 exact-field)에 manifest 행 스키마 완화가 없다. 처방: `validate_inputs`에 `carried_from`(64 hex) 선택 필드를 허용하고 DE «archive manifest» 절에 기재.

### R7. [MAJOR · 정합] K3 root 규칙이 다중 entrypoint build에서 오작동한다
K3 L176 «`screen-meta.json`에 `screen_label`이 있으면 `root.selector`는 정확히 `[data-screen-label="<그 값>"]`». A8 `screen-meta.json`은 `screen_label: 관계인`·`source_sha256: cf2fe348…`(관계인) 하나뿐인데 `design-input.json` case `settings/related-row`의 entrypoint는 `설정.dc.html`(label «설정», `A8/design-ref/설정.dc.html` `data-screen-label="설정"`)이다. 규칙대로면 설정 case의 `interactions.json`이 «관계인» 루트를 요구받아 결함. 처방: «`screen-meta.source_sha256 == case.entrypoint.sha256`일 때만» 대조, 그 외 entrypoint는 «선언 입력·리뷰어 감사»(같은 문장의 label 없는 원본 취급).

### R8. [MAJOR · 정합·무손실] `interactions.viewport = case viewport` + «캡처는 드라이버 바이트»가 A8 캔버스 관찰·DE L174~176과 충돌
③-2. 기존 12 캡처 폐기·재캡처가 강제되고, 드라이버에 크롭 옵션이 없으면 A8은 만족 불가.

### R9. [MAJOR · 무손실] v1 legacy 허용이 `--diff-base`에만 묶여 전역 퇴화 실행(diff-base 없음)에서 과거 build 전부가 red가 된다
K3 L183 «`--diff-base` 대비 그 build 폴더가 git으로 무변경일 때 v1 허용». BS L197~200은 `--diff-base` 없는 실행을 «전역 퇴화»로 허용하고 DE L25~27은 그 모드에서 모든 source-bearing build를 검사한다고 문서화한다. A8 프로젝트는 build 9개(archive 8 — rv-C #7)라 이 모드에서 전부 exit 2. A-M7 권고의 «`--diff-base`(또는 HEAD)» 중 HEAD 앵커가 빠졌다. 처방: diff-base 부재 시 «HEAD 대비 추적 변경 0·untracked 0»으로 같은 판정. (A8 현재 build는 402파일 전부 추적·untracked 0·`_history` 307파일 추적 — `git ls-files`·`status --porcelain` 확인 — 이므로 diff-base가 있으면 legacy 조건은 성립한다.)

### R10. [MAJOR · 무손실] K2 `click:outside` 정의가 메뉴형 오버레이에서 «바깥 클릭 닫힘» 전이를 만들지 못한다
K2 L165 «오버레이 rect 안·후손 대상 rect 밖의 점». Dropdown 메뉴(role=menu, BJ L2829~2843)는 스크림이 없고 `document mousedown`이 `wrap`(트리거+메뉴) 밖일 때만 닫힌다(BJ L2735~2736). 메뉴 rect 안 padding(L2843 `var(--space-2)`) 지점은 «안»이라 닫히지 않는다 → «무변화도 정상 기록»(L165)으로 통과하면서 진단 §1이 «보지 않음»으로 꼽은 바깥 클릭 닫힘은 영원히 관찰되지 않는다. 처방: 스크림형(루트 80% 덮음)은 현행 정의, 비스크림형(role=menu/listbox)은 «루트 rect 안·오버레이 rect·owner 트리거 rect 밖의 점».

### R11. [MINOR · 정합] `--compare` CLI가 앞 절과 K4에서 다르다
앞 절 L107~109 `--compare BUILD/source-manifest.json` vs K4 L188 «기준 manifest는 인자로 고르지 않는다·`design-input.json` `manifests[0]` 고정». `archive_design.py`(AD L164~170)는 BUILD를 모른다 — `--build BUILD` 인자가 필요하다. 확정 계약 우선이나 CLI 블록을 고쳐야 구현자가 헷갈리지 않는다.

### R12. [MINOR · 정합] `_staging-ref`의 신선 디렉터리 요구·정리·커밋 처분이 없다
AD L155~156 «output inventory differs; use a fresh output directory» → 두 번째 재동결부터 `--out BUILD/_staging-ref` 재사용 불가. K6 L204는 `refreeze-diff.json`만 커밋 목록에 넣고 `_staging-ref`(archive 전체 복사본)·`_staging-manifest.json`의 삭제/보존을 말하지 않는다. 남기면 BUILD가 두 배로 커지고, 지우면 `refreeze-diff.json`의 mtime·sha 표만 남는다 — 후자를 명시하면 된다.

### R13. [MINOR · 정합] served 대조의 404·percent-encoding 처리 미기재
K3 L177 «served 경로마다 manifest 행과 sha 일치·url basename = entrypoint basename». A8 trace는 매번 `GET /favicon.ico -> 404`이고 url은 `%EA%B4%80%EA%B3%84%EC%9D%B8.dc.html`이다. «2xx same-origin 응답만·basename은 percent-decode 뒤 비교»를 적지 않으면 A8에서 항상 결함.

### R14. [MINOR · 정합] MCP `filename` 경로의 `opts` 전달이 정의되지 않았다
K5 L196 «`browser_run_code_unsafe`의 `filename`/1행 트램폴린». 트램폴린은 `opts`를 리터럴로 넣을 수 있지만 `filename`으로 `observe_interactions.pw.js`를 직접 주면 `(page, opts)`의 `opts`가 없다. 트램폴린만 유효하다고 적거나 sidecar 옵션 파일을 정의해야 한다. 또 단일 도구 호출이 45분+ 지속되는 것을 MCP 클라이언트가 허용하는지는 저장소 밖(**추측** — 타임아웃 위험). `--resume`이 없어 끊기면 처음부터다.

### R15. [MINOR · 정합] 변경 범위 표에 Makefile·DEVELOPMENT.md·REQUEST_GUIDE·`.gitignore`가 없다
K5 L198 `verify-web-browser`를 `release-web` 선행으로 두려면 `Makefile` L274~278(`release-web: _release`)에 prerequisite 추가와 `_release`의 DRY 안내([1]~[7])·`docs/DEVELOPMENT.md` §6 L128~136 갱신이 필요하다. K5 L197 REQUEST_GUIDE 문단은 `request_guide_contract.py`(Makefile L100~101) 대상이다. D L21~30 범위 표에 없다. 실제 절차와의 맞물림 자체는 가능하다(`make verify`는 `verify-web`을 이미 포함하므로 브라우저 픽스처만 별도 타깃으로 선행하면 된다).

### R16. [MINOR · 정합] `declared_unmatched`가 정의되지 않았고 앞 절 L41과 K1 L156이 충돌
B-M7 행 참조. «선언이 어느 인벤토리에도 매칭되지 않으면 `declared_unmatched`로 기록·잔여 밖·리뷰어 항목 ②에서 건수 대조» 한 줄이면 닫힌다.

### R17. [MINOR · 정합] `interactions.json` 스키마 블록(앞 절 L76~91)이 K1~K3의 새 필드를 반영하지 않는다
`context`·`option`·`after.capture`·`served`·`capabilities`·`discovery_limits`·`navigated`·`unclickable`·`driver_sha256`·`root.fingerprint`·`outside_root`·`excluded_regions`·인벤토리 항목별 `enabled/checked/face/value_empty`·`initial`이 없다. exact-field 검사기(K3 L180)를 구현하려면 스키마가 단일 출처여야 한다.

### R18. [MINOR · 정합] 앞 절과 확정 계약의 충돌이 남아 독자가 헷갈리는 자리
L19(범용 탐색 엔진 금지 vs BFS 드라이버) · L39~40(leaf·role-only 오버레이 vs K2) · L45(순번 접미) · L59(«새 identity» 큐 vs K1) · L67(checked 2회 vs surface) · L72(hover 미요구 vs K2 발견) · L97(v1 build-state 조건 vs K3) · L107~109·L113(exit 3에 carried 포함 vs K4 exit 4) · L114(`_history/vN` vs K4) · **L121(«독립 렌더가 필요한 상태만 case 추가» vs K6 삭제 — 1.1.11 문장이 본문에 그대로)** · L130(SKIP 무실패 vs K5) · L137(«exit 3» vs K7-4 «exit 4»). 확정 계약 우선 규칙으로 규범상 문제는 없으나 L121은 ⑤의 재도입 위험 자체다 — 앞 절에서 지워야 한다.

### R19. [MINOR · 일반화] K5 DOM fixture에 K1의 핵심 패턴(label 이름 트리거·같은 이름 «다음» 위저드·cascading select)이 없다
C#2-5 요구. context 분기의 회귀는 순수 함수 fixture JSON으로 고정할 수 있으니 그 fixture에 «같은 identity·다른 context» 짝을 명시하면 된다.

### R20. [MINOR · 무손실] 스크림이 «핸들러 보유 대상 click»과 «오버레이 click:outside» 두 의무를 받는다
같은 지점의 같은 클릭이 2회 요구된다. 잔여 표에서 오버레이의 `click:outside`를 자기 핸들러 `click`과 동치로 두면 된다.

### R21. [MINOR · 일반화] K2 «원격 URL 기본 거부(`--allow-remote` 없음)»와 «인증 필요 원본은 `--cdp`로 로그인된 브라우저에 붙는 경로만»이 모순
로그인 원본은 loopback이 아니다. `--cdp` 연결 시에만 원격 origin을 허용한다고 적거나 인증 경로를 «범위 밖»으로 명시.

### 검증됨(공격했으나 견딘 항목)
- V1 K2 구조 오버레이 조건이 A8 Dialog에 실제로 맞는다: `position:absolute; inset:0`(BJ L1082~1083)·onClick(L1093), 루트 `[data-screen-label]`(H L37) 안 AppFrame 390x844를 거의 전부 덮는다. 포털 0건(`createPortal` 검색 0).
- V2 `__reactProps$*`·CDP 채널 병기는 타당하다 — React 18은 루트 위임이라 CDP `getEventListeners`는 React 핸들러를 보지 못하고, `__reactProps`는 A8 host element 전부에 붙는다(A V1).
- V3 K1 잔여 단위 `(identity, action, option)`은 시·군 동명 항목(강원·경남 «고성군», 경기 «광주시» vs 시·도 «광주»)을 `owner_items_hash`로 구별한다(H L200~209).
- V4 K3 state_hash가 `role=status`를 제외해 Toast(BJ L1402 `role: "status"`, H L255 2.6s 타이머)가 재생 대조·최적화를 흔들지 않는다.
- V5 K3 served 대조는 same-origin 한정이라 unpkg React(`support.js` L1143~1146)와 충돌하지 않는다(런타임 drift 미탐지는 A-m1대로 한계).
- V6 K3 legacy 조건은 A8 현재 build에 대해 성립한다(추적 402·`_history` 307·untracked 0·`status --porcelain` 빈 출력) — diff-base가 있는 실행 한정(R9).
- V7 K4 exit 4는 A8 PNG 4장(`source-manifest.json` files 행 image 4·dependencies에 image 행 0 → closure 밖)에 대해 성립한다 — staging이 BUILD 밖일 때(R5).
- V8 `make release-web` 선행 게이트는 Makefile 구조상 가능하다(`release-web:` 타깃별 변수 + `_release` 공통, L274~278) — 문서 갱신은 R15.
- V9 K3 v1 규칙이 A8 진행 중 build(`build-state.json` `phase: implement`·`g2_approved: false`·`design_status: ready`)를 v2 의무로 되돌린다 — «진행 중 build는 수집기를 돌려야 ready»(K3 L183)와 정합. 비용은 ⑥.
- V10 K1 «한 표·두 구현» + fixture 동일성 테스트는 B-M6의 어긋남을 구조적으로 막는다.

---

## ⑤ 재도입 검사 — 1.1.8~1.1.12 되돌린 문단 vs 확정 계약

되돌린 diff(`git diff dddjango-web--v1.1.7 HEAD -- dddjango-web/`, 10파일 +110/−39)의 문단별 대조:

| 되돌린 문단(1.1.8~1.1.12) | 확정 계약에 재도입됐는가 |
|---|---|
| `design-review-web.md` +L108 «관련 상태는 소속 case의 확인 항목으로 연결 … focus 같은 부품 내부 상태는 해당 case 안에 두고, **독립 렌더가 필요한 화면·상태만** 기존 case 절차로 추가 … CSS pseudo-state를 별도 case로 늘리지 않는다» | **아니오** — K6 L203이 명시적으로 쓰지 않는다. 단 앞 절 L121이 같은 문장을 아직 담고 있다(R18). K3 «값만 바뀐 step은 연결 의무 없음»은 의미가 근접하지만 리뷰어 재량이 아닌 기계 규칙이고 B-B2·C#6 권고 원문이므로 재도입으로 보지 않는다. |
| `design-review-web.md` +L111 «case별 반환에는 상태의 원본/부품 정의 위치, 발동할 조작과 대상, 실제 관찰 근거 …» | 아니오 — K6 감사 항목 ①~③은 `reached_by`·선언/예외 사유·리스너 대조로 다르다. |
| `commands/dddjango-web.md` +«기존 화면 재개 입구»(적용 지침 확인·요청 복원·현재 비교로 연결) | 아니오. |
| `commands` +«재동결 결과 … **한 화면 파일만 비교했으면 그 파일만 동일한 것이며, 미확보 의존성은 미확인**» | 아니오 — K4 exit 0/3/4와 `refreeze-diff.json`이 대신한다(D L124 선언과 일치). |
| `commands` +«시안 대조 범위 — 구·신 diff는 보조 자료 …»·«수정 모드 G0 … 새 시안 반영은 완전한 현재 원본 묶음 …» | 아니오. |
| `commands` +step 5-2 «PROJECT … 새 시안 제공·디자인 변경 반영 요청이 있으면 그 요청의 원본 묶음을 재동결» | 아니오 — K4 L190은 v1.1.7 L132 문장(«사용자가 "다시 적용"을 명시 요청할 때만») 그대로를 지시한다. |
| `design-acquisition.md` +L15~28 «수정 시 원본 기준 … 번들 하나의 hash 일치로 나머지까지 같은 판이라고 판정하지 않는다» · «새 기준으로 전환하기 전에 기존 원본·manifest·관찰/캡처를 함께 보존 … **활성 reference_root 밖**» | 아니오 — K4 L192 «`_history/vN` 보존은 규범으로 두지 않는다(1.1.12 문단 미재도입)». 앞 절 L114의 «기존 절차대로 `_history/vN` 보존»은 K4가 뒤집었으므로 문장 삭제만 남는다. «번들 hash 하나로 판정 금지»의 의미는 `--compare` 전량 대조가 기계로 대신한다. |
| `implementation-ui/final.md` +«수정 작업의 대조 범위·비교 3종·필수 반환 판형», `coder-web.md`·`design-architect-web.md`·`discipline-reviewer-web.md` 판형 변경, `architecture-web/final.md` «형상 공리·기본 요구/Y·기술 책임» | 아니오 — D L32 «coder·G2·visual-evidence.json·render_audit.js·motion-notes 판형은 바꾸지 않는다»와 K 어디에도 해당 문단 없음. |
| `REQUEST_GUIDE.md` +§6 재동결 요청 문구 예시 | 아니오 — K5 L197의 REQUEST_GUIDE 문단은 Node/Playwright 전제조건이라 내용이 다르다. |

결론: **재도입 없음.** 위험은 앞 절 L121·L114가 본문에 남아 있는 것뿐이다(R18).

---

## ⑥ K8 완전성 — 확정 계약 안의 숨은 결정

K8(6건) 외에 사용자 확인이 필요한 결정:

1. **기존 원본 캡처 전량 폐기·재캡처** — K3 L182 «원본 캡처는 전부 드라이버가 저장한 바이트»·`reference_capture.sha256 == after.capture.sha256`. A8 12 case의 수동 캡처가 전부 무효가 되고 DA §3-4 «캡처를 에이전트가 저장»의 주체가 바뀐다.
2. **viewport 동일 강제 = 캔버스 관찰 관행 폐기** — K3 L178. A8은 560x1040→390x844 크롭(R8). DE L174~176 규칙 개정이 따라온다.
3. **변형본(`_empty-variant`) 금지·데이터 상태는 UI 조작으로만 도달** — K3 L182. 도달 불가한 데이터 상태(예: 서버 데이터에만 있는 빈 상태)는 동결 불가가 된다.
4. **진행 중 build(A8 포함)의 재관찰 의무** — K3 L183 «진행 중 build는 수집기를 돌려야 ready». A8은 G2 직전(`g2_complete_pending_orchestrator: true`)인데 12 case 재관찰 + interactions + 독립 검토를 다시 한다. 릴리즈 노트 기재만으로는 결정이 아니다.
5. **예외 상한 10%** — K3 L181. 수치 정책.
6. **`--max-minutes 45`·`--max-steps 6000`·`--max-depth 12` 기본값과 «상한 도달 = partial = 영구 red(resume 없음)»** — K1 L158. A8은 초과 가능(②-4·R3).
7. **원격 URL 기본 거부** — K2 L169. 실서비스 URL 원본(성공 조건 4의 «정상 입력»에 포함될 수 있음)은 관찰 불가 = 범위 축소.
8. **case 수 증가** — K3 연결 의무를 R2 처방으로 고쳐도 A8은 case 12→약 30~40으로 늘어난다(③-5). 사용자 결정 ①의 취지이나 G0 배너·검토 비용이 커진다.
9. **`_staging-ref` 전량 복사 방식(compare-only 미채택)** — B-m8. BUILD 크기·정리 정책(R12).
10. **다중 viewport = viewport별 전체 재실행** — K3 L178. 1440x900 case를 두면 탐색이 두 배다(`_history/v1`에는 1440 캡처가 있었다).

---

## ⑦ 한 줄 총평

**구현 진입 불가(설계 문장 2곳 수정 후 재검토 없이 진입 가능)** — K1의 «트리거 자기 face» context(R1)와 K3의 «`removed ≠ ∅`까지 step 단위 연결 의무»(R2)는 A8에서 산술적으로 통과 불가라 원 BLOCKER(A-B1·C#1·B-B2·C#6)가 «부분»에 머문다; 여기에 R3(`--max-depth` 12 vs 13)·R4(가림)·R5/R6(자동 carried·`carried_from` 정합)·R7(다중 entrypoint root)·R8(viewport·드라이버 캡처)·R9(전역 퇴화 legacy)·R10(메뉴 `click:outside`)를 확정 계약에 문장으로 고치고, 앞 절 L121·L114를 지우고, ⑥ 1·2·4·6·7을 K8에 올리면 드라이런 게이트로 진입할 수 있다.
