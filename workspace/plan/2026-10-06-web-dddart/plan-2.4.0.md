# dddjango-web 2.4.0 — 지속 탭 셸: 하단 탭 막대는 남고 가운데만 바뀐다 · ‹뒤로›도 막대 그대로 (10-11 · 설계 v7 구현판)

## 바탕
- 바탕: R main `abe90e37`(dddjango-web 2.3.4). 2.4.0 은 마이너다 — 새 규약(지속 셸)과 새 검사 패밀리 SH(SH1~SH5 · 검사 86 → 91종 · 슬라이스 끝 79 → 84종)가 든다. 빚 스캔 지문은 그대로다(SH 는 빚 패밀리 밖). 매니페스트 판은 `make release-web` 이 올린다.
- 사본: `<S>/web-f81`. `<S>` = `/private/tmp/claude-501/-Users-hyun-Desktop-dddjango/ed01792c-e467-4a58-a794-ed16237ffb9e/scratchpad`. 정본 설계 `<S>/f81/design-v7.md`(sha256 `9003198116c2…94713fc9` · 수정 10-11 20:58:36 · 종이 점검 마지막 판) · 점검 기록 `<S>/f81/check-v1 ~ v6-{codex,claude}.md` · 브라우저 시험장 `<S>/f81/bench/`(`bench-report-v7.md` · `out/report7.txt` · `out/verdict-v7.json` · `results-v7-meta.json`). 구현자 둘이 같은 사본에서 나눠 고쳤다 — 규칙 글 · 역할 · Coordinator · 가이드 · 저장소 문서 · 기록 / 검사기 · 픽스처. 커밋은 운영자가 검토 뒤 한다.
- 출발: 현장 보고 F4-81(`workspace/eval/field-report-4/2026-09-10-spring-dream-overhaul-lanes.md` — 6-3-35). 문서 이동 셸은 탭을 누를 때마다 새 문서를 열어 하단 탭 막대가 다시 그려진다 — 앱(iOS 탭 바 · Android 하단 내비 · dddart `StatefulShellRoute`)과 다르다.
- 사용자 결정:
  - 10-11 13:43:46 «가. 플러그인 수정하고 진행하자» · «이식이 잘못된거니깐 이건 수리 진행해줘».
  - 10-11 «일반적인 앱에서는 어떻게 동작해? 앱동작을 기준으로 하면 될거 같아.» → ‹뒤로›도 (나) 사본 없는 서버 복원 · 막대 유지가 목표다. (가) 문서 새로 열기는 (나)가 시험을 끝내 못 넘을 때만 쓰는 대비책이고, 그때는 운영자가 보고한다(먼저 (가)로 가지 않는다).
- 운영자 방향(다시 묻지 않음): 새로 짓는 탭 셸은 처음부터 지속 셸 · 이미 지은 셸은 G1 에서 켤지 정함 · 화면 HTML 사본을 브라우저 저장소에 남기지 않음 · 판 2.4.0 · 셸 전환은 기능 슬라이스(동작이 바뀌므로 슬라이스 0 · 리팩토링 아님).

## 판정과 넣은 것
| 뿌리 | 넣은 것 | 자리 |
|---|---|---|
| 탭 이동이 문서 이동이라 막대가 새 문서와 함께 다시 그려짐 | 지속 셸 — 탭 막대 `<nav>` 하나에 `hx-boost` · 부스트 응답에 처리기가 `HX-Retarget: #root-content` · `HX-Reswap` · `HX-Reselect` 를 달아 `<main>` 안만 바꿈 · 탭 목록은 `<main>` 안 template OOB · 고정 꼴 ①~⑬ | implementation-django §2 «지속 셸» |
| ‹뒤로›·‹앞으로› 가 막대를 다시 그림 | (나) 사본 없는 서버 복원 — `htmx-config` `historyCacheSize` 0 · `root_shell.js` 가 복원 요청에 셸 표지 · 이동 번호를 실어 처리기가 같은 셸이면 `<main>` 안만 · 아니면 409 → 새로 엶 | 같은 절 · 처리기 표 |
| 이동이 겹칠 때 늦은 응답이 화면을 덮음 | 이동 하나만(누름 시작 철회 · 철회 구간 · 적용 직전 지킴 · 문서 떠남) · 떠난 화면의 조각 요청 끊기(시작한 화면 세대) · 화면 밖 요청 요소의 지연 교체 없앰 · 맨 위 보이기 · history state 보전 · 재탭 ② | `root_shell.js`(표준 글 그대로) |
| 탭 기록이 늦게 끝난 옛 요청에 되돌려짐 | 세션 저장 직전 한 자리(`_record_page`) — 저장소를 다시 읽어 이 요청의 쓰기(자기 탭 · root 처분 `write_tab`)를 순서대로 다시 놓음 · 세션 키 없음 · 종료 지킴 · 기준 «문서 이동 셸보다 나빠지지 않음» | 처리기 예시(두 셸 공통) |
| «화면 = 문서» 에 기대던 기능 JS 가 깨짐 | P1~P11 · H1~H5 · discipline 감수 §11 | implementation-javascript §3 «지속 셸의 수명» |
| 셸 꼴 · 공유 머리 · 자산 자리의 기계 강제 | SH1~SH5 · PU2 지속 셸 갈래 · 승인 유입 가름 제외 | 검사기(다른 구현자 몫) |
| 켜는 절차 | G0 `tab_shell` · core 2.0.10 확인 · 세션 엔진 기록 · «지속 셸 점검(빚 밖)» · G1 «탭 셸 방식 행» | Coordinator 두 벌 |

## 바꾼 자리(이 구현자 몫 · Claude 정본 → Codex 미러)
| 묶음 | Claude | Codex | 미러 | 설계 항목 |
|---|---|---|---|---|
| 규칙 글 | `skills/implementation-django/references/final.md` | `skills/dddjango-web-implementation-django/references/final.md` | byte | D-1 ~ D-15 |
| 〃 | `skills/implementation-htmx/references/final.md` | 〃 | byte | H-1 ~ H-10 |
| 〃 | `skills/implementation-javascript/references/final.md` | 〃 | byte | J-1 ~ J-6 |
| 〃 | `architecture-ui` · `architecture-state` · `discipline-houserules` · `implementation-test` references | 〃 | byte | U-1 · U-2 · S-1 · R-1 ~ R-8 · T-1 ~ T-3 |
| 요약 | `skills/implementation-{django,htmx,javascript,test}/SKILL.md` | `skills/dddjango-web-<스킬>/SKILL.md` | 의미(접두) | K-1 ~ K-12 |
| 역할 | `agents/{design-architect-web,design-review-ui-web,coder-web,discipline-reviewer-web}.md` | `skills/dddjango-web-<역할>/SKILL.md` | 의미(접두) | A-1 ~ A-9 |
| Coordinator | `commands/dddjango-web.md` | `skills/dddjango-web/SKILL.md` | 의미(치환 셋) | O-1 ~ O-8 |
| 가이드 | `REQUEST_GUIDE.md` | `codex-dddjango-web/REQUEST_GUIDE.md` | byte | G-1 · G-2 |
| verify-web | 루트 `Makefile` `:97` · `:107` | — | — | «검사 91종» · 문단 표지 14 → 16(`'**탭 셸 방식 행**'` · `'**지속 셸 점검(빚 밖)**'`) |
| 저장소 문서 | `AGENTS.md` · `README.md` · `docs/DEVELOPMENT.md` · `docs/file_tree_web.html` · `docs/work_flow_web.html` | — | — | 2.4.0 문장 · 86 → 91 · 슬라이스 끝 79 → 84 · 패밀리 표에 SH 행 |
| 기록 | 이 계획 · `build-log-2.4.0.md` | — | — | — |
- 검사기 · 픽스처(`scripts/backstop.py` · `src/{common,check_project,products,check_purity,inflow,debt}.py` · 새 `src/check_shell.py` · `scripts/test/**`)는 다른 구현자의 몫이다 — 그 기록은 그 구현자 보고에 둔다.

## 최종 판(표준 글) — `root_shell.js` · 처리기는 시험장 판과 코드가 같다(주석만 정리) · 템플릿 · CSS · root 상태 · root_initializer 는 설계 블록 기준
규칙 글의 코드 블록은 호스트 코드로 그대로 옮겨 적히는 글이라, 설계 판의 주석에 있던 설계 메타(점검 번호 · 판 꼬리 · htmx 글자 위치 · 시험장 손잡이 이름 · 호스트 줄)를 걷고 뜻(왜 이 코드가 있는지)은 쉬운 말로 남겼다. 코드 토큰은 그대로다.

| 표준 글 블록 | 실린 자리 | 규칙 글 판 sha(주석 정리) | 시험 판 sha | 주석 걷은 비교 |
|---|---|---|---|---|
| `root_shell.js` | implementation-django §2 «지속 셸» | `288e252753ad8df71764bd7117be4dd70485c99e97b0d56261805c93cd018754` | NA3 `root_shell_v7.js` `feb92d24ef966274ab980b19f10d281694a1d52a2be9d01c722971132bcc48e8`(meta 와 같음) | 같음(`//` 주석 걷고 공백 정규화) |
| 처리기 `root_request_handler.py` | implementation-django §2 게이트 | `a56438f8b67b03d96aa2b70b05863fa0898e042a034a937073fb933cea0514a7` | NA3 `root_request_handler_v7.py` `f77d292c29f37436010cc466a5af860f8409cae3ff8eb72e9c360c485944afb0`(meta 와 같음 · 비교는 머리 import 뒤 블록 부분 `fa86ba9d950e…`) | 같음(`#` 주석 · docstring 걷은 토큰 · AST 둘 다) |
| 탭 막대 틀 CSS | implementation-django §2 | `948d9eb6a5cd13839a8dc5eff8c9982d60f385c7ed49ce2a531cb1b0e506ab72` | 설계 v7 블록 = 시험장 `css_v7.src.css`(시험장 파일은 배치용 `bottom` 을 더함) | 주석 무변 — 바이트 같음 |
| 셸 템플릿 | implementation-django §2 | `e3b469ed3296f16ae0bb6755a052ce334b8ceb3d6678339d55251658aa856144` | 설계 v7 §2.2 블록 | 주석 무변 — 바이트 같음 |
| `root_initializer.py` | implementation-django §3 «지속 셸이면» | `7ead3edc…37ae7d4` | 설계 v7 §2.4 블록 | 주석 무변 — 바이트 같음 |
| `root_tab_state.py` · `root_state.py` | 〃 | (구현 검토 뒤 고침) | 설계 v7 §2.4 블록(`root_state.py` 한 파일에 `RootTab` · `RootState`) | **설계와 다름** — 탭 한 칸 레코드를 `root_tab_state.py` 의 `RootTabState` 로 나눔(한 파일 한 클래스 — 백스톱 NM3 · `state/` 는 `_state.py` 만 — NM1). 필드 · 꼴은 설계 블록과 같다(아래 «구현 검토와 보완» I2) |
- **시험장이 돌린 것**: `root_shell.js` · 처리기는 표준 글과 같은 코드다. 셸 템플릿 · 틀 CSS · root 상태 · `root_initializer` 는 시험장이 계측 판을 돌렸다 — 머리 자산의 `?v=` 를 템플릿 글자가 아니라 static 저장소 클래스가 붙임 · `shell_rev` 가 `root_vm.py` 에 있음(본문은 같음) · 시험 전용 필드 · 배치 속성. 표준 템플릿 글자 그대로는 브라우저 시험장을 지나지 않았고, 검사기 픽스처 «표준 글 그대로 칸»(규칙 글에서 블록을 읽어 그대로 넣음)이 SH · NM 통과를 잰다.
- 증명: `<S>/f81/verify_comment_strip.py` → `<S>/f81/verify_comment_strip.txt`(구현 때 판정 «모두 같음 · 메타 0» — 그 판은 `verify_comment_strip.before-i2.txt` · 검토 보완 뒤 10-12 02:19 다시 돌린 판은 root 상태 블록만 의도대로 다름(«어긋남 있음» — I2) · 블록 안 설계 메타 잔존 0 줄). 토큰 하나를 바꾸면 비교가 어긋남도 확인했다. 블록 자르기는 시험장 `v7/extract_v7.py` 와 같다(여는 줄 다음 ~ 닫는 줄 앞 · 마지막 줄바꿈 포함). Codex 짝은 references byte 미러라 같다.
- 시험이 고른 손잡이: **없음**(S40 · SYNCP · SCR 모두 쓰지 않음). 손잡이 글은 규칙 글에 넣지 않았다.

## 시험 결과(시험장 v7 · 운영자 측정 21:24 ~ 22:12 · 시작 전 고정 21:23:55 — 설계 수정 시각 뒤)
- 갈래: **§8.4 ① — (나) 채택 · 구현**. 손잡이 단계 없음 · 전제 붕괴 없음.
- 출발점: OLD(2.3.x 문서 이동 셸)에서 V3 TRANS 0/20(두 엔진) 재현.

| 기준 | Chromium | WebKit | 비고 |
|---|---|---|---|
| NA3 필수 16(V1 · V5 · V7 · V8 · V9 · V10 · V11 · V12 · V13 · V14 · V15 · V16 · V17 · V18 · V19 · V20) | 16/16 | 16/16 | V1 은 ‹뒤로› · ‹앞으로› · 별칭 셸 · 화면 안 이동 포함 · V9 H-g 인계까지 |
| V2 막대 깨짐 · 사라짐 | 0(탭 20 · 화면 안 10 · ‹뒤로› 10 · ‹앞으로› 10) | 0 | 화면 기준 |
| V3 막대 전환 | 20/20 | 20/20 | 〃 |
| V4 탭 링크 안 움직임 | 20/20 | 20/20 | 〃 |
| V6 옛 스크롤 프레임 | 최대 0 | 최대 0 | 〃 |
| V8 스크롤 어긋남(> 50px) | 0/10 | 0/10 | 〃 |
| GA3(대비 · 참고) | 필수 · 화면 수치 ○ · ‹뒤로› 완성 25ms · ‹앞으로› 26ms | ○ · ‹뒤로› 81ms · ‹앞으로› 101ms · 막대 깨짐 ‹뒤로› 2/10 · ‹앞으로› 1/10 | NA3 ‹뒤로› · ‹앞으로› 15 · 12ms(Chromium) · 19 · 16ms(WebKit) |

- OLD 대조(V13 — 칸마다 «틀린 비율 ≤ OLD»):
  - 브라우저 ⑴pre · ⑵pre: NA3 0/10(두 엔진 · 두 세션 조건) · OLD 10/10(WebKit ⑴pre 는 경합이 선 8 회 중 8). ⑴post · ⑵post · ⑶ 은 OLD 와 같거나 낮음(Django 공통 경합 — 다시 읽기 ~ 저장 창 · 같은 세션의 다른 키). 경합이 서지 않은 회차(OLD 에서 엔진이 앞 이동을 보내기 전에 거둠)는 세지 않았다.
  - 처리기(HTTP) ⑸⑹ ⓐ ⓑ · ⓒ 의 R 처분 · ⑹ⓔ · ⑺ ⓐ ⓑ1 ⓑ2 ⓒ ⓓ ⓔ: NA3 0/10. OLD 가 틀린 칸(⑸ⓑ · ⑹ⓑ 10/10 · S-def ⑺ⓒ 10/10)에서 NA3 는 0. ⑸⑹ⓒ 의 B 기록 OLD 10 · NA3 10(≤ OLD). ⑸⑹ⓓ(지연 없는 동시)는 관찰값.
- 관찰값(판정 아님): ‹뒤로› 뒤 입력 글(V8 ⓑ) — OLD Chromium bfcache 켬 3/3 남음 · 끔 0/3 · OLD WebKit 0/3 · NA3 · GA3 0/3(설계대로 L6). «옛 화면 @ 새 주소 ms»(V8 ⓐ) — NA3 Chromium 0 · WebKit 0~16 · GA3 Chromium 17 · WebKit 64~88 · OLD 0. ⒦③ⓑ(알림 없는 `assign` · Navigation API 끈 조건) Chromium 끼어듦 10/10(P11 이 막는 자리) · WebKit 0/10.

## 음성 대조 재현 표(결함 하나씩 뺀 판 — 재현해야 그 시험의 «통과» 를 믿는다)
| 음성 판 | 가르는 시험 | Chromium | WebKit |
|---|---|---|---|
| `NA3-NOCANCEL` · `NA3-NOQGUARD` | V15 ㄷ′ ㅅ′(복원 1.5 s 걸음 — ‹뒤로› 뒤 다시 열린 요청 1) | 재현 | 재현 |
| `NA3-NOAPPLY` · `NA3-NOSWALLOW` | V15 ㄹ | 재현 | 재현 |
| `NA3-NOHS` · `GA3-NOHS` | V9 H-g(0/3 같음) | 재현 | 재현 |
| `NA3-NOVQ` · `NA3-NORETAP` · `NA3-NOGATE` | V17 · V20 ② · V20 ③ | 재현 | 재현 |
| `NA3-SETTLESCROLL` | V6(최대 2 프레임) · V15 ㅊ 넓힌 판 | 재현 | 재현 |
| `NA3-NOSTALE` · `NA3-STALEELT` | V10 ⒧①~④ · ④ 만(①~③ 통과) | 재현 | 재현 |
| `NA3-NOFRAGDEPTH` | V10 ⒧④ⓒ(④ⓐⓑ 통과) | 재현 | 재현 |
| `NA3-NOZERODELAY` | V10 ⒧⑤ⓑ(ⓐ 통과) | 재현 | 재현 |
| `NA3-NOLASTWIN` | V10 ⒨ | 재현 9/9 | m3(재탭)만 재현 · m1 · m2 는 **재현 안 됨(엔진 — 링크 문서 이동을 엔진이 거둠)** |
| `NA3-NOLEAVE` | V10 ⒦①② | 재현 20/20 | **재현 안 됨(엔진 — 미리 적은 칸)** |
| `NA3-NOTELL` | V10 ⒦③ⓐ · ⒦④(Navigation API 끈 조건) | 재현 6/6 | **재현 안 됨(엔진 — 문서 이동 시작 때 엔진이 XHR 을 끊음)** |
| `NA3-NODETACHLEAVE` | V10 ⒦⑤ | 끈 조건 재현 6/6 · 기본 조건 **재현 안 됨(엔진 — `navigate` 가 지킴 · 미리 적은 칸)** | **재현 안 됨(엔진 — 미리 적은 칸)** |
| `NA3-NOPH` | V10 ⒣⒤⒥ · V16 · V13 S-def ⑴pre | 재현 | ⒣⒤ · V13 재현 · ⒥ 은 **재현 안 됨(엔진 — 미리 적은 칸)** |
| `NA3-NOCARRY` · `NA3-NODISPOSE` · `NA3-DISPOSEALL` · `NA3-COPYONLY` · `NA3-NOEND` · `NA3-NOGONE` · `NA3-V5END` · `NA3-NOALIAS` | V13 ⑴pre · ⑸⑹⑺ · V16 ⒬⒭ · V16 ⒧(HTTP · Django Client) | 재현(엔진 무관) | 〃 |
- 설계 표에 없는 칸이라 세지 않은 것: `NA3-NOLEAVE` 의 V15 ㅂ(두 엔진 0/6).

## 손잡이 · 한계 · 대가
- **손잡이**: 없음.
- **알려진 한계**(규칙 글 implementation-django §2 «앱과 다른 점» 에 적음 — 설계 §2.0 L1~L7 · §2.11):
  - L1 탭별 화면 상태 · 스크롤 기억 없음(주소만 기억 · 서버가 다시 그림 · 맨 위).
  - L2 ‹뒤로› 순서는 브라우저 기록 하나(탭을 넘나듦 — 막대를 다시 그리지 않는 것만 앱과 같음).
  - L3 재탭 ①(중첩 화면에서 같은 탭)은 첫 화면으로의 push — 기록에 중첩 화면이 남음.
  - L4 첫 반응은 서버 왕복 뒤 — 누른 탭의 눌림 표시만 즉시.
  - L5 본문 교체를 넘어 살아야 하는 전역 알림(토스트) 자리가 셸에 없음.
  - L6 ‹뒤로›로 돌아간 화면은 서버가 다시 그림 — 입력 글 · 펼침 · 기능 JS 상태 없음.
  - L7 화면 읽기 프로그램에 «새 화면» 알림 없음.
  - §2.11: OOB 로 새로 놓인 탭 링크는 정착(20ms) 뒤에야 부스트 — 그 사이 누름은 문서 이동(시험장 §6.1 에서도 확인) · Shift-클릭은 htmx 가 부스트로 가로챔 · 첫 문서의 CSP 가 계속 쓰임 · 롤링 배포 창의 판 다름 → 전체 이동 되풀이 · 정적 주소에 이미 `?` 가 붙는 저장소는 `?v=` 꼴을 못 씀 · 남는 경합 창(다시 읽기 ~ 저장 · 서명 쿠키 엔진 · 같은 세션의 다른 키)은 문서 이동 셸과 같은 수준 · `root:leave` 를 빠뜨린 JS 이동과 브라우저 UI 이동은 판정 밖.
- **알려진 대가**(설계 §0.3 «기록» 행):
  - 새로 짓는 탭 셸(지속 셸)은 root 브라우저 시험 1 이 필수 — `pytest-playwright` + Chromium 설치 · 브라우저 실행 환경 규칙.
  - 탭 기록 쓰기가 있는 페이지 요청마다 세션 저장소를 한 번 더 읽음(DB 세션이면 SELECT 한 번 · 호스트처럼 처분이 조각 · POST 에도 나면 그 요청마다).
  - 기능 JS 의 JS 문서 이동 앞 알림 한 줄(P11 `root:leave`).
  - 화면 밖 요청 요소(`body` 등 — `HX-Location` 후속 · `source` 없는 `htmx.ajax`)의 조각 응답은 전환 연출 없음(지연 교체를 없앰).

## 지문 무변(검사기 구현자 실측 — 운영자가 채움)
| 항목 | 기대 | 실측 | 근거 |
|---|---|---|---|
| `debt.CHECK_IDS` 지문(2.3.3 · 2.4.0) | `e49c83776ff9faf6` 같음 | `e49c83776ff9faf6`(두 벌) | 운영자 10-12 03:25 — `sha256(','.join(debt.CHECK_IDS))[:16]` · 픽스처 Z0 «빚 지문 실측» 단언 |
| `--debt-scan`(+`--refactor`) 출력 · JSON(`scanned_at` · `scanner.plugin` 빼고) | 바탕 러너와 같음 | 같음 | 픽스처 Z0 «빚 출력 · JSON 동일»(바탕 `a73dfadc` 러너와 대조 · 두 갈래 × 선언 없음 · 있음) — `make verify-web` 의 2.4.0 지속 셸 픽스처 432 / 0 안 |
| 2.3.x 동결본으로 `--debt-residual` | 판 경계 없음 · 판 글자 알림 한 줄 | 잔존 0 · 판 경계 0 · 알림 한 줄 | 픽스처 Z0 «옛 G0 동결본 잔존 0 · 판 경계 0 · 판 글자 알림만» — 같은 432 / 0 안 |
| `TOTAL_CHECKS` · 슬라이스 끝 | 91 · 84 | 91 · 84(두 벌) | 운영자 10-12 03:25 — `backstop.TOTAL_CHECKS` · `SLICE_END_DEFERRED` |

## 실기기 확인(§8.4 ⑤ — 배포 전에 사용자에게 권함)
- iPhone 가장자리 쓸기 ‹뒤로›는 Playwright 가 흉내 내지 못한다. 갈래 ① 이라 운영자가 배포 전에 사용자에게 한 번 권한다 — 시험 대상은 시험장 NA3 판(지속 셸 표지가 달린 후보 셸).
- 권하는 문안(쉬운 말): «아래 탭 막대를 ‹뒤로› 때도 그대로 두는 방식을 시험 화면에서 다 확인했습니다. 다만 iPhone 의 화면 왼쪽 끝을 쓸어 ‹뒤로› 가는 몸짓은 컴퓨터 시험으로 흉내 낼 수 없어 직접 봐 주시면 좋겠습니다. 휴대폰 Safari 로 <주소> 를 열고 → 아래 탭 둘을 차례로 누른 뒤 → 화면 왼쪽 끝을 오른쪽으로 쓸어 ‹뒤로› 를 두 번 해 주세요(5 분쯤). 떠나던 화면이 다시 보이거나 아래 탭 막대가 사라지거나 깨지는지만 봐 주시면 됩니다.»(접속 방법 — 같은 망 · 주소 — 은 운영자가 그때 적는다)
- 갈래: 봤고 OLD 보다 눈에 띄게 나쁘지 않음 → 배포 / 눈에 띄게 나쁨 → 배포 멈춤 · 보고(설계 §10 문안 · V8 ⓐ OLD 대비 표 · GA3 수치) / 사용자가 미룸 → 배포는 하고 보고에 «iPhone 쓸기 ‹뒤로› 실기기 확인 전 — 2.4.0 으로 새로 짓는 탭 셸은 처음부터 지속 셸이라 그 확인 전에 지은 프로젝트가 영향 범위에 든다 · 이미 지은 문서 이동 셸은 G1 에서 켜지 않으면 영향 없음» 한 줄 · 6-3-35 셸 전환 마지막 슬라이스의 G2 전에 다시 권함.

| 항목 | 결과 |
|---|---|
| 권한 시각 | 2026-10-11 23:28:51(사용자 23:28:40 «아이폰 확인은 뭐야?» 에 무엇인지 설명 — 시험장 NA3 · OLD 판을 Mac 와이파이 주소로 여는 안내 `<S>/f81/bench/iphone-guide.md`) |
| 사용자 확인 결과(봄 · 나쁘지 않음 / 나쁨 / 미룸) | 미룸 — 사용자 2026-10-11 23:29:05 «건너뛰어» |
| 처분 | 배포는 진행 · 배포 보고에 영향 범위 한 줄 · 6-3-35 셸 전환 마지막 슬라이스의 G2 전에 다시 권함 |

## 구현 검토와 보완(10-11 23:15 ~ 10-12)
독립 구현 검토 둘(Codex · Claude — 읽기 전용 · 지시 `<S>/f81/prompt-review-impl.txt`)이 커밋 전 작업 트리를 봤다. 화면 동작 코드(`root_shell.js` · 처리기)는 두 검토 모두 시험장 판과 같다고 확인했고, 지적은 검사기와 «표준 글 ↔ 검사기» 어긋남에 모였다.

| 검토 | 지적 | 처분 |
|---|---|---|
| Codex 1차 `<S>/f81/review-impl-codex.md`(«배포 멈춤») | 차단 — SH1 이 화면 부스트 링크의 `hx-boost` · `data-hx-boost` 별칭 값 충돌을 통과시킴 | 보완 1차: SH1 에 별칭 값 충돌 검사(이미 읽던 `hx-history` · `hx-history-elt` · `hx-swap-oob` · 부스트 링크 요청 속성 포함) · 표지 없는 호스트의 일반 요청 속성은 그대로 침묵 |
| 〃 | 차단 — SH3 가 `{% verbatim %}` 안 글자 include 를 렌더 연결로 읽음 | 보완 1차: SH 전용 간선 · block 판독에서 verbatim 안 Django 지시문 제외(이름 붙은 verbatim 포함 · SH2 title · block · `persistent_scope` 도) · verbatim 안 HTML 태그는 계속 검사 · `parse_template_edges()` 무변 |
| 〃 | 중요 — implementation-django SKILL 요약 «복원 실패는 409» 가 5xx 예외를 지움 | 두 벌 «복원 실패는 409 — 5xx 는 그 상태 그대로» |
| 〃 | 사소 — 이 계획의 실측 칸 · 증거 칸 `〃` | 아래 표에 채움 |
| Claude 1차 `<S>/f81/review-impl-claude.md`(«보완 후 배포») | 차단 B1 — 규칙 글의 표준 셸 템플릿 그대로가 SH2 꼴 ⑨ 에서 붉음(두 탭 목록의 들여쓰기가 달라 공백 정규화가 못 맞춤) | 보완 2차: 비교 전에 공백 줄을 접음 · 규칙 글 ⑨ 문구 «들여쓰기 · 줄바꿈 차이는 무시» |
| 〃 | 차단 B2 — 기준점 없는 `--all`(G0 «지속 셸 점검» · G2 직전 확인)에서 옛 자리 htmx core 가 SH4 거짓 blocker 셋 | 보완 2차: 기준점 트리가 없으면 파일로 있는 옛 자리 core 를 core 로 봄(기준점이 있는 게이트는 그대로) |
| 〃 | 중요 I1 — SH4 가 foundation 일곱을 알파벳 순으로 강제(규칙 글 · 관례는 color 먼저) | 보완 2차: `FOUNDATION_TOKENS` 순(color · typography · spacing · radius · shadow · duration · asset) · 규칙 글 공유 머리 문장에 그 순서를 적음 |
| 〃 | 중요 I2 — 표준 `root_state.py` 블록(`RootTab` + `RootState` 한 파일)이 NM3 «한 파일 한 클래스» 에 걸림 | 규칙 글: 탭 한 칸 레코드를 `root/scaffold/state/root_tab_state.py` 의 `RootTabState` 로 나눔(RootVM 예시 · 문장 같이) — **설계 블록과 다름**(이름 · 파일) |
| 〃 | 중요 I3 — 새 픽스처가 임시 프로젝트를 저장소 뿌리 안에 만듦 | 보완 2차: 시스템 임시 폴더로 옮김 · `GIT_CEILING_DIRECTORIES` 걷음 |
| 〃 | 중요 I4 — 이 계획의 «시험장 판과 코드가 같다» 범위 | 위 «최종 판» 제목 · 표 · «시험장이 돌린 것» 문단으로 고침 |
| 〃 | 사소 1 — include 인자에 `%` 가 있으면 간선이 빠짐 | 보완 2차: `%}` 까지 읽음 |
| 〃 | 사소 3 — `hx-history-elt="true"` 문구가 까닭을 안 알림 | 보완 2차: 문구에 «값 없이 쓴다» |
| 〃 | 사소 4 — Python 3.9 에서 파서 예외가 러너를 죽임(표지 없는 호스트에도 닿음) | 보완 2차: 예외를 잡아 «판독 불가»(SH2 · SH4 는 blocker · 그 밖은 `[info]`) · `/usr/bin/python3` 3.9.6 확인 |
| 〃 | 사소 5 — 새로 추가된 지속 셸에 «기준점 본문 없음» 알림 | 보완 2차: 게이트의 새 파일에는 안 냄 |
| 〃 | 사소 7 «이번 판이 택한» · 사소 8 `root_initializer` 문장과 `shell_rev` | 규칙 글 두 곳 고침(«지속 셸이 택한» · `shell_rev()` 는 시동 질문이 아님 한 문장) |
| 〃 | 사소 10 — 권한 시각 | 위 실기기 표를 `date` 꼴로 |
| 〃 | 사소 2(시작 태그 안 `{% if a > b %}` 뒤 속성 미탐) · 6 · 9 · 11 | 둠 — 사소 2 는 알려진 미탐(드문 꼴 · SH1) · 9 는 무해한 문구 · 6 · 11 은 정보 |

- **보완 1차**(Codex · 검사기 · 픽스처 — 보고 `<S>/f81/fix1-checker.md`): 새 단언 109(붉음 56 → 0) · 전체 3,639 / 0.
- **보완 2차**(Claude · 검사기 · 픽스처 — 지시 `<S>/f81/prompt-fix2-checker.txt` · 보고 `<S>/f81/fix2-checker.md`): 새 묶음 다섯(`standard` · `z2_tabs` · `z4_legacy` · `z4_order` · `minor` — 32 단언 · 붉음 22 → 0) · 2.4.0 셸 픽스처 412 / 0 · 전체 16 묶음 3,671 / 0 · 검사 91 · 슬라이스 끝 84 · 빚 지문 `e49c83776ff9faf6`.
- **«표준 글 그대로 칸»**(`standard`): 규칙 글 파일에서 지속 셸 `root_view.html` · `root_tab_state.py` · `root_state.py` 블록을 읽어 글자 그대로 넣은 프로젝트가 `--all` · 게이트에서 SH · NM blocker 0(픽스처 단언은 `--only sh,nm` — 구현자가 따로 전 패밀리 · `--slice-end` 로도 돌려 0 을 봤고, Claude 2차 검토가 표준 블록 전체를 SH · NM · IM · MD · PU 로 메모리에서 돌려 0 을 봤다). 규칙 글 블록이 없어지거나 둘이 되면 픽스처가 실패한다 — 표준 글과 검사기가 다시 어긋나면 `make verify-web` 이 잡는다.
- **보완 중 사고(1차)**: Codex 구현자가 붉음 수치를 재려고 만든 임시 사본에 플러그인 폴더를 심볼릭 링크로 걸어, 리팩토링 픽스처의 문서 변이 시험이 실제 `dddjango-web/commands/dddjango-web.md` 를 비웠다. 구현자가 2.3.4 본(HEAD)과 Codex 짝의 2.4.0 변경으로 복구했고, 운영자가 대조했다(`<S>/f81/coord_check.py` — 2.3.4 대비 바뀐 줄 Claude 6 → 9 · Codex 6 → 9 · 낱말 차이는 기존 플랫폼 관례뿐 · 그 시각 뒤 바뀐 파일은 예상 목록뿐). 2차 검토에 따로 확인을 맡겼다.
- **2차 검토**(지시 `<S>/f81/prompt-review-impl2.txt`):
  - Codex `<S>/f81/review-impl2-codex.md` «배포 멈춤» — 차단 2: 보완 1차의 verbatim 필터가 ① HTML 주석 · `{# #}` · `{{ }}` 토큰 안의 글자를 verbatim 경계로 읽고 ② 이름 붙은 endverbatim 의 안쪽 공백을 접어 견줌(유효한 Django 템플릿에서 SH3 미탐 · 오탐). 1차 지적은 그 밖에 모두 닫힘 · Coordinator 복구 · 미러 손상 없음.
  - Claude `<S>/f81/review-impl2-claude.md` «그대로 커밋 · 배포 가능» — 차단 0 · 중요 2 · 사소 7(보완 3차 뒤 판을 봄 · 고친 verbatim 필터를 Django Lexer 흉내와 유효 템플릿 26,116 건으로 대조해 include · block 판독이 모두 같음을 확인 · Coordinator 복구 덩이 8 대 8 같음).
- **보완 3차**(운영자 — `<S>/f81/fix3-verbatim.md`): SH 지시문 뷰(`products.shell_directives`)를 Django Lexer 와 같은 토큰 경계로 새로 씀 — 원문에서 `{% %}` · `{{ }}` · `{# #}` 토큰을 줄 안에서 읽고, verbatim 은 내용이 `end` + 시작 내용과 글자까지 같은 태그에서만 끝나며, 실제 지시문의 시작이 아닌 `{%` 는 뷰에서 가린다. 픽스처 «Lexer 경계» 칸 18 단언(붉음 16 → 0) · 2.4.0 셸 픽스처 430 / 0.
- **2차 Claude 중요 · 사소의 처분**: I-2(파서가 못 읽은 지속 셸 화면은 SH1 · SH3 태그 검사를 건너뛰고 `[info]` 한 줄) → 감수 글 두 벌에 «`[info] SH 판독 불가` 파일도 열어 손으로 본다» 한 구절(검사기 판정은 그대로) · 사소 2 → 하우스룰 트리 · 표와 `docs/file_tree_web.html` 에 `root_tab_state.py` · 사소 3 · 4 · 5 → 이 계획 · 기록. I-1 · 사소 1 은 아래 «닫지 않은 것».
- **3차 검토**(지시 `<S>/f81/prompt-review-impl3.txt` · Codex `<S>/f81/review-impl3-codex.md` «배포 멈춤» — 2차 차단 둘은 닫힘 · 새 차단 3): ㉠ SH 의 바탕인 공용 주석 판독(`mask_html()`)이 Django 토큰 경계를 몰라, Django 태그 글자를 변수 값 안에 찍거나(`{{ "{% comment %}" }}…{{ "{% endcomment %}" }}` 사이 실제 include) verbatim 안에 가짜 comment 를 둔 화면에서 SH3 가 실제 include 를 놓치거나 렌더되지 않는 include 를 읽고, 셸 head 의 같은 꼴에서 SH2 가 금지 block 을 놓침 ㉡ 공용 `VERBATIM_RE` 가 `{# {% endverbatim %} #}` 안 글자에서 verbatim 을 끝내 verbatim 안에 글자로 출력되는 `{# <script> #}` · `{# <form hx-boost> #}` 를 주석으로 지워 SH3 · SH1 이 놓침 ㉢ 보완 3차가 실제 지시문 토큰 안의 `{%` 글자(템플릿 이름 `legacy/{%/widget.html`)까지 가려 include 대상을 바꿈(3차가 새로 연 미탐). ㉠ ㉡ 은 2.3.x 부터의 공용 판독에서 온 것이고, 유효하지만 드문 꼴이다 — spring_dream_server 화면 템플릿 246 개 중 verbatim · 변수 속 태그 글자를 쓰는 것 0.
- **결정 34**(사용자 2026-10-12 03:22:06 전 · 03:00 물음에 «가.»): 3차 차단 ㉢ 만 고치고 배포 · ㉠ ㉡ 은 알려진 한계로 적고 2.4.1 에서 고침(설계 초안 `<S>/f81/design-sh-lexer-view.md` — SH 전용 Lexer 뷰). 운영자가 «3차에도 차단이 남으면 멈추고 묻는다» 규칙대로 03:00 에 멈추고 물었다.
- **보완 4차**(운영자 — ㉢): `shell_directives` 가 실제 지시문 토큰의 범위 전체를 보존(토큰 안의 `{%` 글자는 가리지 않음) · 픽스처 «실제 include 인자 안의 `{%` 글자 보존» 2 단언(붉음 2 → 0) · `z3_verbatim` 88 / 0 · 고치기 전 판 `<S>/f81/products.before-fix4.py`. 감수 두 벌에 «Django 태그 글자를 verbatim · 변수 값 안에 찍은 지속 셸 제품 화면은 그 줄 둘레의 include · 실행 태그를 손으로 본다» 한 구절(㉠ ㉡ 의 사람 쪽 그물).
- **이번 판에서 닫지 않은 것**(①~③ 은 2.3.x 부터 있던 것 · 다음 판 후보):
  - ① `check_naming.py:166` 의 `ast.MatchAs` 가 Python 3.9 에 없어 view `.py` 가 있는 프로젝트의 러너가 3.9 에서 내부 오류로 죽는다(2.3.4 도 같음).
  - ② 옛 자리 htmx core 호스트를 기준점 없이 `--only` 없이 돌리면 PU1 · PU2 의 기존 판정 두 줄이 난다(«지속 셸 점검» `--all --only sh` 는 0).
  - ③ 저장소 뿌리가 아닌 하위 폴더가 프로젝트 뿌리인 호스트는 `common.py` 의 `ls-tree` 에 `--full-name` 이 없어 기준점 파일 목록이 빈다(2.2.5 부터 알려진 결함). 그런 호스트가 옛 자리 htmx core 로 지속 셸을 지으면 diff 게이트의 SH4 가 거짓 blocker 셋을 내고, 조각 CSS 삭제만 한 diff 는 SH4 가 서지 않는다. spring_dream_server 는 해당 없음.
  - ④ `static/js/htmx.js` 가 다른 core(`htmx.min.js`)와 함께 남아 있는 호스트는 SH4 가 그 파일을 기능 JS 로 요구한다(설계 문장 «`static/js/*.js` 전부에서 htmx core · `root_shell.js` 를 뺀 것» 그대로) — 쓰지 않는 사본은 지우는 것이 맞는 처치다.
  - ⑤ 파서가 못 읽는 글자(`<![foo]>` 류 · 구판 Python)가 있는 지속 셸 화면은 SH1 · SH3 가 `[info]` 로만 알린다(SH2 · SH4 는 blocker) — 감수가 손으로 본다.
  - ⑥ 시작 태그 안 `{% if a > b %}` 뒤의 속성은 SH1 이 읽지 못한다(1차 사소 2 · 드문 꼴).
  - ⑦ 3차 검토 ㉠ ㉡ — Django 태그 글자를 변수 값 · verbatim 안에 글자로 찍은 지속 셸 화면에서 SH1 · SH2 · SH3 의 판정이 Django 와 다를 수 있다(공용 주석 · verbatim 판독). 결정 34 로 2.4.1 에서 SH 전용 Lexer 뷰로 고친다 · 그때까지 감수가 손으로 본다. 같은 자리의 관례: HTML 주석 안의 실제 include 는 SH 렌더 간선에서 뺀다(대상 파일이 `-->` 로 시작하는 꼴은 미탐).

## 경계 · 넣지 않은 것
- (가) 대비책 글(§2.7)은 규칙 글에 넣지 않았다 — (나) 채택이라 쓰이지 않는 갈래다. (가)로 바뀌는 일은 사용자 결정 · 다시 점검을 거친 다음 판의 일이다.
- 고침 손잡이(S40 · SYNCP · SCR) 글도 넣지 않았다(시험이 고르지 않음).
- 이미 지은 호스트 코드(6-3-35 spring_dream_server)는 바꾸지 않는다 — 규칙 글의 예시만 바뀐다. 호스트 이관 메모는 설계 §12.
- 온톨로지 · LEDGER 영향 0(web 은 산문 정본). `docs/work_flow_web.spec.json` 의 «84종» 은 2.2.5 관례대로 둔다.

## 멈출 기준과 결과
| 기준 | 결과 | 증거 |
|---|---|---|
| 시험장 v7 · NA3 필수 16/16 · 화면 기준 두 엔진 · 음성 대조 재현 | 갈래 ① | 위 «시험 결과» · `<S>/f81/bench/bench-report-v7.md` |
| 표준 글 블록 = 시험장 판(주석 걷은 비교) | `root_shell.js` · 처리기 같음 · 셸 템플릿 · 틀 CSS · `root_initializer.py` 는 설계 블록과 바이트 같음 · root 상태 블록만 검토 뒤 고침으로 다름(의도 — I2) | `<S>/f81/verify_comment_strip.txt`(검토 보완 뒤 10-12 02:19 다시 돌림 · 고침 앞 판 `verify_comment_strip.before-i2.txt` = «모두 같음») |
| references byte 미러(지식 스킬 12) · REQUEST_GUIDE byte 미러 · `request_guide_contract.py` | 같음 · PASS | `make verify-web` 의 references byte 미러 대조 · `make verify`(그 안의 `request_guide_contract.py` — 아래 verify 행 로그) |
| Makefile 문단 대조 16 · 역할 7 · 0T 줄 | 같음 | `make verify-web` 로그의 «문단 Claude·Codex 대조» · «역할 7 판 확인 지문 경계 줄» 단계(아래 verify-web 행) |
| `make verify-web`(기능 커밋 전 · 후) · `make verify` · `claude plugin validate dddjango-web --strict` | verify-web 커밋 전 rc 0 · 커밋 뒤 rc 0(둘 다 16 묶음 3,691 / 0) · `make verify` green 6/6(봉인 chore 뒤) · validate 통과 | `<S>/f81/verify/verify-web-pre5.log` · `verify-web-post.log` · `verify-post.log` |
| 독립 구현 검토 | 3차 — 1 · 2차 차단 모두 닫힘 · 3차 잔여 ㉠ ㉡ 은 결정 34 로 2.4.1(위 «구현 검토와 보완») | `<S>/f81/review-impl{,2,3}-*.md` |
| 실기기 확인(§8.4 ⑤) | 미룸(사용자 «건너뛰어») — 배포 진행 | 위 표 |

## 운영자가 할 일
1. 두 구현자 몫을 합친 사본에서 `make verify-web`(기능 커밋 전) · `make verify` 를 돌리고 위 칸을 채운다. 브라우저 시험은 샌드박스 밖.
2. 기능 커밋 → `make verify-web`(기능 커밋 뒤 · 봉인 앞) → 봉인 chore(Makefile — `manifest_seal.py --write`) → 장부 다시 읽기(배포 직전 F4 새 항목).
3. 사용자에게 실기기 확인을 권하고(§8.4 ⑤) 결과대로 처분한 뒤 `make release-web` · 배포 뒤 보고. 보고 문장(설계 §0.4 9): «진행 중 web 레인 — 지문 무변이라 G2 잔존 판정 그대로(판 글자 알림 한 줄) · 문서 이동 셸은 화면 동작이 바뀌지 않음(탭 기록 자리만 응답 뒤로 — 같은 결과) · 단 이미 `hx-boost` · `hx-history*` 를 쓴 호스트는 `--all` · 비git 게이트에서 SH1 을 새로 만난다(2.0 부터 산문 금지 — 맞는 판정) · 6-3-35 는 이 판으로 셸 전환 요청을 낸다(G1 결정 · 표지는 마지막 슬라이스)».
