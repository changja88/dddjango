판정: blocker 2 · major 9 · minor 16 — 수정 후 재검토

# 적대 검토 W1 — 설계 v1 «dddjango-web 기능 요청의 G0 빚 처리» (2026-09-27)

- 대상: `workspace/eval/web-g0-debt/design-v1.md`(이하 `D:행`) · 진단 `diagnosis.md` · 결정 기록 `evening-report.md` §5 · 브리프 `morning-briefs-2026-09-27.md` 로드맵 6a.
- 실물: `dddjango-web/commands/dddjango-web.md`(이하 `W:행`) · `dddjango/commands/dddjango.md`(이하 `J:행`) · `dddjango-web/scripts/**` · houserules SKILL/final · Makefile.
- 실행: 현장 저장소는 `git log/show/grep/ls-tree` 만. 러너는 스크래치 `diag6a/` 안에서 **in-process(파일 생성 없음)**로만 돌렸다. Serena·Graphify·모델 실행 없음.

## 한 줄 결론

방향(1-d·B1 의 요소 대부분 이식)은 맞다. 그러나 새 장치 두 개가 그대로는 판정기가 못 된다. `--debt-scan`(«all_mode 를 스코프에»)은 구조적으로 거짓 빚을 내고, G2 «G2 키 ∖ G0 키»는 정상 흐름(승인 머지·스코프 확장·개명)에서 거짓 red, 키 붕괴·스냅샷 앞 변경에서 거짓 green 을 낸다. G0 안의 위치·실행 판정·정지 폴더·Phase 3 합치기가 web 구조와 부딪힌다.

### (할 일 1) 1-d·B1 이식 판정

| 구분 | 내용 |
|---|---|
| 옮김 | 모드 지정 불인정 · 스캔 증거·blocker · 미룰 수 없음 · ⓐ/ⓑ/ⓐ′ · 결정 출처 · 충돌 · 재상정 · 슬라이스 0 선행·계수 제외 · 오탐 STOP · 잔존 M · 수정 모드 R1 · 트리비얼(R1 해석) · 정리 요청 → 리팩토링 커맨드 |
| 빠짐 | G0 질문 순서(`J:86`) · 잇기 새 빚에서 귀속 제외(`J:85`) · 결정 5(실행 줄 없는 폴더 = 끝남) · 승인 머지 provenance·귀속 1차 처방 철회(`J:123`) · 루트 전체 실행 후 경로 선별(`J:79`) · houserules **SKILL.md** 의 «면제 아닌 빚»(dddjango SKILL `:61` 대응) |
| 과함 | «대가 한 줄»을 web 전 게이트(`W:113`)로 확대 · «실행»을 build-state 와 `refactor-scope.md` 두 곳에 둠 · `빚 기준 SHA` 는 쓰는 장치가 없다 |

## Blocker

### B-1 G2 판정(잔존 M·귀속)이 결정적 판정기가 아니고, 정상 흐름에서 거짓 red/green 을 낸다

| 갈래 | 사례 | 근거 |
|---|---|---|
| 판정 주체 없음 | §5-2 는 집합 연산만 적는다. 도구는 `--debt-scan` 출력뿐(§8)이고 G0 키 원본은 `refactor-scope.md` 의 md 표다(`D:42`). Coordinator 가 md 표와 JSON 을 손으로 대조한다 — `J:123` «귀속 목록을 경로 필터로 나눈 서술은 게이트 증거가 아니다»의 반례 | [실측] `D:42·82-83` · §8 |
| 거짓 red ① 승인 머지 | 현장 web 폴더 2곳이 `approved-merges.txt` 를 쓴다(settings-nickname · settings-birth-change). 레인 머지 실재(`4e5378e10` «main → lane/web_consultation … web/employee_choice·web/client/fortune_employee 신설»). 머지로 들어온 legacy 가 G2∖G0 = 귀속 blocker | [실측] `git ls-tree`·`git log --merges` |
| 거짓 red ② G1 뒤 스코프 확장 | 재스캔은 G1 배너 직전뿐(`D:40`). 반송·슬라이스 재개봉·⑤ 자산 번들(`W:180`)·G0 직후 base 배선(`W:131`)이 새 단위를 건드리면 그 단위 legacy 전부가 귀속 | [실측] 문면 |
| 거짓 red ③ 개명 + 잔존 | 슬라이스 0 이 WN 교정으로 파일을 개명했는데 같은 파일의 다른 발견이 ⓑ·재상정으로 남으면 경로가 바뀌어 새 키가 된다 → 귀속. `J:113` «슬라이스 0 에서 빼고 진행(… 잔존은 legacy 보고)»과 충돌 | [실측] `D:31` 키 정의 · 빈도 [추정] |
| 거짓 red ④ 메시지 가변 | WP2 reason 은 조건 우선순위로 갈린다(`check_purity.py:212-231`). 같은 태그가 무관 편집으로 다른 메시지를 내면 새 키(귀속)와 옛 키 소멸(M 감소)이 동시에 난다 | [실측] 코드 |
| 거짓 green ① 키 붕괴 | WI/WP 키에서 행을 빼면 같은 파일·같은 메시지 다건이 1키가 된다(WI3·WP6 메시지 고정 — `check_imports.py:46` · `check_purity.py:194`). ⓑ 키가 있는 파일에 같은 종류가 더 들어와도 G2∖G0 = ∅. diff 게이트는 스냅샷 **뒤** 줄만 잡으므로 스냅샷 **앞** 변경(⑤ 커밋 · G0 직후 base 배선)은 두 게이트 모두 못 본다 | [실측] 코드 · `W:131·180` |
| 거짓 green ② 단위 교차 | WN3 은 모든 영역의 view 이름으로 design_system component 를 판정한다(`check_naming.py:105-112`). 새 화면 이름이 스코프 밖 단위에 발견을 만들면 G2 스캔 범위 밖이라 안 보인다 | [실측] 코드 · 빈도 [추정] |
| 거짓 green ③ 잇기 세탁 | → M-3 | — |

### B-2 `--debt-scan` = «all_mode 를 스코프에»가 구조적 거짓 빚을 낸다

| 갈래 | 사실 | 근거 |
|---|---|---|
| 파일 우주 | `BackstopContext.build` 는 `os.walk` 로 ignored·untracked 까지 센다(`common.py:407-416`). `.DS_Store` 하나가 WN8 과 함께 위치별 WS1/WS2/WS3/WS6 을 낸다. 현장 `.gitignore:72` 는 `.DS_Store` 를 무시하므로 gated 경로에는 안 보이지만 all_mode 에는 보인다. 증거 검사기는 이미 `.DS_Store` 를 뺀다(`check_design_evidence.py:25`) | [실측] 가상 ctx 실험: `('WN8','static/images/.DS_Store')` `('WS1','.DS_Store')` `('WS2','auth/.DS_Store')` · 현장 작업 트리에 실재하는지는 [추정] |
| 진단 수치의 이전성 | 진단의 «3건»은 `git show` 재구성 트리와 복제 트리에서 잰 값이다. 실제 작업 트리 값이 아니다 | [실측] 진단 §3-1 |
| legacy 허용 기준점 | all_mode 에서 WP1 은 legacy HTMX 설치(`static/js/htmx.min.js`)를 «신설»로 낸다(`check_purity.py:145-153`). WP2 는 `base_files` 가 비어 legacy 로드 태그를 red 로 낸다(`:126-131`). B1 이 이것을 ⓐ(이동)로 밀면 `W:131` «기존 `web/static/js/htmx.min.js`·`htmx.js` 는 브라운필드 설치로 그대로 소비 … 조용한 이동/업그레이드를 하지 않는다»와 정면충돌 | [실측] 가상 ctx: `('WP1','static/js/htmx.min.js','HTMX legacy core 예약 이름 … 신설')` |
| WS5 | `--all` + diff-base 없음 → WS5 무음 생략(notice만) → «26종»이 실제로는 25종. diff-base 를 주면 모든 단위를 신규로 보고 골격을 검사한다. legacy 화면에 빈 종류 폴더가 없는 것이 빚인지는 규범 결정이다(houserules SKILL `:29` «레거시 화면 내부 추가에 표준 폴더 신설을 강제하지 않고»). 설계는 이것을 정하지 않았다 | [실측] sds 복제 in-process: `WS5(골격 완비) 생략` |
| dirty 트리 | `W:131` «그대로 진행»이면 사용자 WIP 가 빚 키가 된다 | → m-14 |

## Major

| # | 지적 | 근거 |
|---|---|---|
| M-1 | **스캔 범위 모순·좁히기.** ① `D:38` 은 단위를 `web/static/` 한 칸으로 두는데, `D:96`·W-T1/W-T2(`D:124`)는 `static/images/` 칸 단위로 결과를 예측한다. ② 현장 화면 CSS 13개가 전부 `web/static/css/` 에 있다 → 단위가 static 이면 거의 모든 레인이 static 빚을 상속한다. ③ `--scope` 로 러너를 좁히면 `D:41` «미룰 수 없음은 경로 무관 잔류»를 산출할 수 없고, 기록된 command 자체가 좁아진다(`J:79` 는 루트 전체 실행 후 경로 선별). ④ Coordinator 직접 쓰기(base 배선 `W:131` · htmx·motion.js `W:180` · 자산 번들 `W:150·180`)는 «명세 파일 목록» 확인(`D:40`)에 안 잡힌다 | [실측] ls-tree · 문면 |
| M-2 | **Phase 0 안의 위치·질문 순서 부재.** web G0 는 step 5 에서 `web/static/images/` 에 쓰고(`W:148·150`), 시안 archive·브라우저 관찰·독립 입력범위 검토(`W:155`)를 마친 **뒤** step 6 배너를 낸다(`W:163`). 스캔이 step 5 뒤면 이번 실행의 쓰기가 «빚»으로 세탁되고, 빚 정지가 step 6 이면 비싼 산출을 버린다. `J:86` 질문 순서의 web 대응이 없다(web 에는 계약 없음 `:137` · 폴더 `:139` · 디자인 포인터 `:144` · 입력 차단 `:157` · 배선·dirty `:131` · 배치 `:163` 질문이 더 있다 — 진단 #11 이 지적). `D:58` «빚 기준 <G0 스캔 HEAD SHA>»는 작업 트리를 스캔한 사실과 다르다 | [실측] 문면 |
| M-3 | **실행 판정 이중 출처·잇기.** ① `D:58-59` 는 실행 줄과 build-state 판정을 둘 다 둔다. ② build-state 에는 실행별 리셋이 없다(`W:85` 갱신 목록 · 재사용은 «생성 대신 복원» `W:139`) → 끝난 폴더를 재사용한 새 실행이 도중에 죽으면 `g2_approved=true` 가 남아 «새 실행»으로 오판된다. ③ 현장 착륙 폴더 16개 중 3개가 `g2_approved=false`(web-auth-screens `phase=design` · web-chat-spine · ai-character-chat) → 설계 규칙대로면 자동 «잇기»가 되고 옛 `git_snapshot`(`cef4c3f7` 등)으로 diff 게이트·귀속이 폭주한다. 결정 5 가 이식되지 않았다. ④ «재스캔의 새 키만 묻는다»(`D:59`)는 귀속을 빼지 않는다(`J:85` 는 뺀다) → 이번 실행 자신의 위반이 ⓐ/ⓑ 빚으로 세탁된다. ⑤ 잇기를 묻지 않고 자동 적용한다(`J:85` 는 대가와 함께 묻는다) | [실측] `git show` build-state ×16 · 문면 |
| M-4 | **G0 정지 폴더 보존의 충돌.** ① `D:60` 은 `W:163` 폐기 규칙의 예외만 적고 커밋 주체·시점이 없다(web 커밋은 Phase 2 ⑤ 뿐 `W:180`) → 미추적 정지 폴더가 남는다. ② 러너 `current_nondesign_scope` 는 `.dddjango-web/` 안 다른 폴더에 미추적·변경이 하나라도 있으면 과거 시안 검사 생략을 끈다(`backstop.py:123-132`) → 다음 비시안 레인 G2 가 과거 빌드 전수 검사(현장 red 14)로 떨어진다. ③ scope.md·동결 산출을 폐기하면 재개 입구(`W:27` «기존 scope.md 에 기록»)의 근거가 사라진다. `fetch_images` 가 쓴 `web/static/images/` 파일은 폴더 밖이라 폐기 대상도 아니다 | [실측] 코드 · 문면 |
| M-5 | **Phase 3 합치기가 슬라이스 0 커밋 분리를 지운다.** `W:204-206` `git reset --soft <pre_run_head>` 가 파이프라인 커밋 전부를 미커밋 1덩어리로 만든다. `D:71` «커밋 분리(`:188` 그대로)»는 런 중에만 성립한다. `J:113` «커밋하지 않는 실행이면 G2 배너에 슬라이스 0 파일 목록…»의 대응 문면이 없고, 판정 기록의 SHA 수명도 정하지 않았다 | [실측] |
| M-6 | **houserules SKILL.md 누락(§8).** `SKILL.md:15` «표준은 새로 만드는 코드부터 … 기존 코드의 수정·개명·이동을 요구하지 않는다»(§1 1순위) · `:29` 경계 규칙 · `:49` «레거시에는 불발화». Codex 는 `:14·28·48`. 이 스킬은 design-architect-web·coder-web·discipline-reviewer-web 가 frontmatter 로 적재한다(`agents/*.md:7·9·8`) → 슬라이스 0 을 설계·구현·감사하는 주체가 «개명 요구 안 함»을 1순위 원칙으로 읽는다. dddjango SKILL 은 반대다(`:61` «빚은 면제가 아니다») | [실측] |
| M-7 | **«미룰 수 없음» × 동작 불변 불가 교착.** 설계가 든 예 WP6(주석 노출)·WP1(core 중복)은 고치면 응답·로드 코어가 바뀐다. 그러면 `J:106` 이식 문면상 선택지가 «동작 변경 별도 요청 먼저(정지) / 중단» 둘뿐이다. 그 별도 요청도 G0 스캔이 같은 항목을 «미룰 수 없음» ⓐ → 슬라이스 0(동작 불변) → 같은 STOP 으로 보낸다. 요청 자체가 그 항목의 수정일 때의 규칙이 없다 | [실측] 문면 · 순환은 [추정] |
| M-8 | **검증·미러 경로.** `make release-web` 은 `make verify` 만 부른다(`Makefile:385`). verify-web(수동 `:23-26`)의 픽스처와 scripts/Codex byte 대조는 배포 게이트에서 돌지 않는다 → 새 판정 장치(`--debt-scan`·G2 비교·slice0_guard)의 회귀와 Codex byte 드리프트를 배포 전에 잡는 자동 경로가 0이다. Codex SKILL(274줄)·에이전트 SKILL 4의 의미 미러도 자동 대조가 없다. 라벨 교체만으로 Codex 14행(`139·153·159·161·166·174·186·213·219·228·238·240·260·264`)을 봐야 한다 | [실측] |
| M-9 | **작업량 과소.** 진단 2.5~4일은 «스크립트 모드 1 + 문면»을 전제로 한다. 실제로 필요한 것: 스캔 의미론(우주·legacy 기준점·WS5·키)+픽스처 1~1.5 · 결정적 G2 비교기(기준 커밋 스캔·개명 추적·승인 머지)+픽스처 1~1.5 · 커맨드 문면(G0 재배열·실행 판정·정지·Phase 3·수정·트리비얼·경계) 1~1.5 · 에이전트 3 + SKILL·final·가이드 0.5 · Codex 의미 미러 0.5~1 · 행동 시험 8건(web G0 가 시안 수집 뒤라 1건이 무겁다)과 리뷰 2회 1~2. 합계 **5~8일**, 결정 17 (가)면 +1~1.5. 선례: dddjango 로드맵 4(가드 1개) 검토자 추정 4.5~5일·단순화 3일(`evening-report.md:133`) — web 은 가드에 스캔 모드와 G2 비교기가 더 붙는다 | [추정] |

## Minor

| # | 지적 | 근거 |
|---|---|---|
| m-1 | 라벨 정리 목록(`D:48`)에 폴더 ⓐ/ⓑ 교차 참조 5곳이 빠졌다: `W:86` «폴더 ⓐ 재사용» · `:163` «ⓑ로 신규 생성한 폴더» · `:215` «ⓐ/ⓑ 선택 … 보통 ⓐ» · `:217` «폴더 ⓑ 신규» · `:240`. 그대로 두면 dangling 이 된다 | [실측] grep |
| m-2 | Coordinator 직접 쓰기 **닫힌 목록**(`W:9` «다음뿐이다» · `W:244`)과 산출물 위치(`W:33-45`)에 `refactor-scope.md`·스캔 JSON 이 없다 → 넣지 않으면 자기 경계 위반 | [실측] |
| m-3 | `D:34` 사실 오류: houserules `:205` 는 조건문(«래칫형 검사가 도입되면»)이지 유령이 아니다. 유령은 커맨드 `:44·68·195` 와 Codex `:97·121·218` 이다 | [실측] |
| m-4 | `D:83` 사실 오류: «부수 발견 4 = 현장 3건 유입 경로». 실제로 `5b4c47a40` 은 git_snapshot `a04ff751` 의 20커밋 **뒤**다(sips 수작업 파생본). `fetch_images`·`extract_dc` 는 snake_case + 해시 파일명을 만든다(`fetch_images.py:58-66·106`) → ⑤ 자산 번들은 WN8 유입로가 아니다 | [실측] `git show`·`rev-list --count` |
| m-5 | `D:95-96` 사실·대가: 시안 대상 트리비얼은 기존 폴더를 쓴다(`W:226`). 승격 대가에서 «승인 명세 없는 화면 = G1′ 필수(`W:217`)»가 빠졌다. 승격을 빚 결정 **전**에 해서, 출처 있는 ⓑ 로 끝나도 수정 모드 비용을 치른다 | [실측] |
| m-6 | 트리비얼(시안 없음)에는 스캔 증거 기록처가 없다(폴더 없음 `W:13·227`) → «증거 없는 빚 0 = blocker»를 집행할 자리가 없다 | [실측] |
| m-7 | «대가 한 줄»을 `W:113` 전 게이트로 넓히면 빚 밖 게이트(G1 Y/Z · 입력 차단 5-8)가 전부 바뀐다. 영향 목록이 없다 | [실측] |
| m-8 | web 은 모드를 G0 배너 1급 승인 항목으로 둔다(`W:127`). «모드 지정 불인정»(`D:24`)을 «빚 스캔 생략·상속 지시 불인정»으로 한정하는 문면이 필요하다 | [실측] |
| m-9 | 섞인 요청의 비검사기 정리 항목(의미 정리)이 «정리는 G0 빚으로»(`D:23`)에 흡수돼 조용히 사라진다. 리팩토링 커맨드 안내 1행이 없다 | [추정] |
| m-10 | Phase 1 discipline-reviewer-web 명세 점검은 선택이다(`W:173`). 그런데 `J:106` 이동 STOP 트리거가 이 리뷰어의 발견에 기댄다. 슬라이스 0 이 있을 때 필수로 할지 정하지 않았고, `design-review-web.md` 는 §8 에 없다 | [실측] |
| m-11 | 귀속 1차 처방 = 철회(`J:123` 라운드 2 교훈)가 이식되지 않았다 | [실측] |
| m-12 | Phase 3 재실행(`W:200`)은 diff 게이트뿐이다. 감사 반영 뒤 `--debt-scan`·M 재계산 규정이 없다 | [실측] |
| m-13 | REQUEST_GUIDE §4 에 «정리 미룸·검사 범위 좁히기 지시를 적지 않는다»(dddjango 가이드 `:119-120`)가 없다. §8 은 §6·§7 만 고친다 | [실측] |
| m-14 | dirty 진행 + ⓐ 이면 슬라이스 0 커밋이 사용자 WIP 를 함께 커밋한다(`W:131` «무단 커밋·파괴하지 않는다»와 충돌) | [실측] 문면 · 빈도 [추정] |
| m-15 | 재개 입구의 수집·검증 전용 요청(코드 무변)과, 정체 감사 exit 2 로 수정에 진입하는 경로(`W:29`)의 스캔 적용 여부가 미정이다 | [실측] |
| m-16 | ⓐ′·정리 안내의 목적지인 6b 의 계약이 없다(«검사기 빚·단위 한정» 요청을 받는가). dddjango 결정 11 미결과 짝이다 | [추정] |

## 결정 갈래별 빈틈 (권고 없음)

### 결정 15 — 빚으로 셀 검사기

| 갈래 | 빈틈 |
|---|---|
| (가) 26종 | clip 기저 차분(현장 5-1-1 «clip 14 = anchor 같은 집합» 수작업)은 여전히 수작업으로 남는다. G2 clip 은 전체 트리 판단 자료라 legacy/신규를 가르지 않는다 [실측 진단 §3-6] |
| (나) + clip·focus | ① 키 `CLIP\|경로\|선택자` 에 클리핑 조상·«확정/경미» 등급 중 무엇이 빚인지 정하지 않았다. ② clip·focus 교정은 padding/overflow/링 추가 = 외형 변화 → 슬라이스 0 «동작 불변»과 충돌해 항목마다 `J:106` STOP 이 날 수 있다(현장 18건) [추정]. ③ 두 도구는 web 루트 전체만 받는다(스코프 필터·JSON 없음 — `W:196·229` 호출형) → +0.5일에 포함되지 않은 개조다 [실측]. ④ 화면 CSS 가 전부 `static/css/` 라 단위 귀속이 static 한 칸에 몰린다 [실측] |

### 결정 16 — 과거 시안 빌드 증거 red

| 갈래 | 빈틈 |
|---|---|
| (가) 빚 밖 | **(major 급)** `D:86` «G2 는 지금처럼 `--design-build <현재 폴더>`만»은 비시안 레인에서 거짓이다. 비시안은 `--design-build` 를 생략하고(`W:195`), 러너는 과거 빌드를 전수 검사하며 생략은 `current_nondesign_scope` 조건을 모두 충족할 때만이다(`backstop.py:95-133`). 비시안 폴더를 `--design-build` 로 주면 사용 오류다(`:224-231`). 러너·`design-evidence.md` 개정이 필요한데 §8 에 없다 [실측] |
| (나) 빚 안 | ① 증거 갱신은 코드가 아니라 관찰이라 슬라이스 0(coder·동작 불변)에 담을 자리가 없다. ② 다른 빌드 폴더의 `visual-evidence.json` 을 누가 쓰는지(«한 화면 = 한 폴더» `W:49`) 정하지 않았다. ③ digest 가 web/ 전체라(`check_design_evidence.py:430-449`) 이 레인의 기능 슬라이스가 갱신한 과거 증거를 다시 만료시킨다 → 레인 안에서 자기 무효화. ④ NFC 8건은 재관찰로 못 고친다 → 수리 전에는 매 레인 «플러그인 결함» STOP [실측/추정] |

### 결정 17 — 슬라이스 0 동작 보존 근거

| 갈래 | 빈틈 |
|---|---|
| (가) slice0_guard | ① **참조 완전성을 판정하지 않는다** — 누락 참조가 있어도 «치환 줄만»이면 green 이다. 현장 3건의 참조는 web/ 5줄 밖에도 있다: `.dddjango-web/20260924-1858-teller-content-price/teller_price_fixture.py:592`(`/static/web/images/gold-blossom.png`) · `.dddjango-web/20260905-2018-web-auth-screens/asset-manifest.login.json:5` local_path [실측 git grep] → «개명 판정만으로 닫힌다»(`D:75`)는 과장이다. ② 참조 형식 사상이 미정이다: 파일 경로 `web/static/images/x` ↔ `{% static 'web/images/x' %}`(프리픽스 `W:131` ⓒ) ↔ 템플릿 이름(DIRS=web/) ↔ 점 모듈 경로 ↔ CSS `url()` 상대. ③ 제외 경로(현재 폴더 기록물 vs 다른 빌드 기록)가 미정이다. ④ 창 안 머지 처리가 미정이다(`J:114` behavior_guard 는 다룬다). ⑤ 렌더 전후 대조의 조건이 미정이다: «전» 실측 시점, 영향 화면 선정 주체, 인증 화면, `has_render_audit=false`·비시안 빌드. render audit 은 상호작용(WP3 JS 이관)과 URL(WI3/WI4)을 보지 않는다(`W:196` 축 목록). ⑥ Phase 3 soft reset 뒤 SHA 가 소멸한다 → 판정 기록 시점을 정해야 한다 |
| (나) tests/web 고정 | ① 현장 tests/ 의 개명 대상 참조는 0이다(진단 §3-3) → 개명 파손을 못 잡는다. ② behavior_guard 를 이식하려 해도 입력(실행 줄·build_anchor)과 제외 경로(`.dddjango/`)가 web 에 없다 → +0.5일 밖이다. ③ tests/web 이 없는 프로젝트의 대체 규칙이 없다 [실측/추정] |
| (다) 장치 없음 | G2 시각 대조·visual 게이트는 이번 빌드 case 만 본다. 슬라이스 0 이 건드린 다른 화면(현장: 로그인 · 사용자 정보 `user_info_step.html:174`)은 대조 대상 밖이라 «사람·LLM 판정»조차 영향 화면에 닿지 않는다 [실측 진단 §3-3 · `W:191`] |
| 공통 | G2 «동작 보존» 1행이 (가)에만 정의돼 있다(`D:85`). (나)·(다)의 배너 행과 차단 조건이 없다 |

## 실측 / 추정

| 항목 | 방법 | 결과 |
|---|---|---|
| all_mode 거짓 빚 | 스크래치에서 `BackstopContext(...)` 가상 인스턴스(파일 생성 없음) + `run_purity/naming/structure` | WP1 legacy htmx «신설» · `.DS_Store` → WN8×3 · WS1 · WS2 |
| WS5 생략 | `diag6a/sds` in-process `all_mode=True, diff_base=None` | notice `WS5(골격 완비) 생략` |
| 현장 무시 규칙 | `git show main:.gitignore` | `:72 .DS_Store` |
| 현장 폴더 상태 | `git show main:.dddjango-web/*/build-state.json` ×16 | g2_approved=false 3(착륙 폴더) |
| 승인 머지 | `git ls-tree` · `git log --merges -- web` | approved-merges.txt 2 · web 머지 커밋 실재 |
| 유입 경로 | `git show --stat 5b4c47a40` · `rev-list --count a04ff751..5b4c47a40` | 스냅샷 뒤 20커밋 · 수작업 파생본 |
| 참조 범위 | `git grep` kebab 3이름 | web/ 5줄 + `.dddjango-web/` fixture 1 · asset-manifest 1(+ 기록물 다수) |
| 화면 CSS 위치 | `git ls-tree web/static/css/` | 13파일 전부 static/css |
| 배포 게이트 | `Makefile:385` | `$(MAKE) verify` 만 — verify-web 없음 |
| SKILL 원칙 | `houserules SKILL.md:15·29·49` · Codex `:14·28·48` | «개명·이동 요구 안 함» · «레거시 불발화» |
| 추정 | 작업량 5~8일 · 교착 순환(M-7) · `.DS_Store` 현장 실재 · clip 교정의 외형 변화 | 근거는 각 행 |

## v2 최소 수정 목록

1. **G2 판정기를 결정적으로**: 비교 스크립트(또는 `--debt-scan --against <G0 json>`)를 두고, G0 키 원본을 JSON 파일로 둔다. 귀속 = «G2 스캔» − «같은 단위 집합을 기준 커밋에서 돌린 스캔»(스코프 확장 흡수). 개명 추적(`-M`) · 승인 머지 provenance(`approved-merges.txt`) · 귀속 1차 처방 = 철회를 넣는다. (B-1 · m-11)
2. **스캔 의미론을 정한다**: 파일 우주(`git ls-files -co --exclude-standard` 등) · legacy 허용 검사(WP1/WP2)의 기준점 = 스캔 HEAD · WS5 처리 · 키에 발생 수(또는 행 무관 지문 + 빈도)를 넣는다. 거짓 빚 픽스처 3종(`.DS_Store` · legacy htmx · WS5)을 둔다. (B-2)
3. **스캔 = web/ 전체 1회 기록 + 단위 선별**로 바꾼다. 단위 정의를 하나로 정하고(static 을 칸 단위로 볼지), Coordinator 직접 쓰기의 단위도 포함한다. (M-1)
4. **Phase 0 위치와 질문 순서표**: 스캔·빚 질문을 step 5(web 쓰기·시안 수집) 앞에 둔다. (M-2)
5. **실행 판정 출처를 하나로**(refactor-scope 실행 줄)로 정한다. 결정 5(실행 줄 없는 폴더 = 끝남)를 이식하고, 잇기/승인됨/폐기를 대가와 함께 묻고, 잇기 새 빚에서 귀속을 뺀다. (M-3)
6. **G0 정지 기록**: 커밋 주체·시점 또는 폴더 밖 기록처를 정하고, `current_nondesign_scope` 상호작용을 해소한다. (M-4)
7. **Phase 3 합치기와 슬라이스 0 분리의 관계**를 명시한다(합치기 예외, 또는 G2 배너·보고의 슬라이스 0 파일 목록). (M-5)
8. **§8 추가**: houserules SKILL.md(Claude·Codex) · `W:9·244` 직접 쓰기 목록 · 산출물 위치 · build-state/재개 입구 · Phase 3 · design-review-web.md · REQUEST_GUIDE §4 · 라벨 교차 참조 5곳 · (결정 16 (가)라면) 러너·design-evidence.md. (M-6 · m-1·2·10·13)
9. **«미룰 수 없음» 항목이 요청의 대상 자체일 때의 규칙**을 둔다. (M-7)
10. **배포 전 verify-web 실행 기록 의무** 또는 새 장치 픽스처의 자동 경로 편입 여부를 계획의 결정 항목으로 올린다. (M-8)
11. **사실 정정**: `D:83` 유입 경로 · `D:34` houserules `:205` · `D:95` 트리비얼 폴더. (m-3·4·5)
12. **작업량 재추정**과 결정 갈래별 증분을 다시 적는다. (M-9)
