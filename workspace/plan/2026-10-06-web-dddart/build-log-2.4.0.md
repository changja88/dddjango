# 2.4.0 짓기 기록 — dddjango-web 2.4.0 (지속 탭 셸: 하단 탭 막대는 남고 가운데만 바뀐다 · ‹뒤로›도 막대 그대로)

- 시작 10-11 22:16(지시 파일 시각 · KST) · 구현자 둘 — Claude(규칙 글 · 역할 · Coordinator · 가이드 · 저장소 문서 · 기록) · 검사기 · 픽스처 구현자(그 기록은 그 보고에) · 바탕 R main `abe90e37`(web 2.3.4) · 사본 `<S>/web-f81` · 결정 · 판정 · 시험 결과: `plan-2.4.0.md` · 정본 설계 `<S>/f81/design-v7.md` · 시험장 `<S>/f81/bench/`(읽기만).
- `<S>` = `/private/tmp/claude-501/-Users-hyun-Desktop-dddjango/ed01792c-e467-4a58-a794-ed16237ffb9e/scratchpad`.
- 목적: 새로 짓는 탭 셸을 앱처럼 «막대는 남고 가운데만 바뀜» 으로 짓게 하고(‹뒤로› · ‹앞으로› 포함), 이미 지은 문서 이동 셸은 G1 결정으로만 바꾸게 한다.

## 진행
- 설계 v7 를 읽고(§0 · §1 · §2 · §4 · §5 · §6.6 · §8.4 · §10 · §12), 시험장 v7 결과(`bench-report-v7.md` · `out/report7.txt` · `out/verdict-v7.json` · `results-v7-meta.json`)로 갈래 ① — (나) 채택 · 손잡이 없음을 확인했다.
- 바탕 확인: 사본 HEAD `abe90e3741c5`(2.3.4). 설계 §0.2 끝 행대로 Codex Coordinator 줄은 18 줄째 뒤 +1(예: build-state `htmx_core_static` `:74` · G0 `:149` · 4′ 끝 `:202` · G1 SDK 행 `:220` · 백스톱 `:262` · 전수 테스트 `:263` · 리팩토링 `:325` · `:343` — 넣은 줄만큼 더 밀림) · AGENTS 는 `plan-2.3.4.md` 줄 뒤. references · Claude 쪽 · Makefile · REQUEST_GUIDE 줄은 설계 줄과 같았다.
- 규칙 글: implementation-django(D-1 ~ D-15) · implementation-htmx(H-1 ~ H-10) · implementation-javascript(J-1 ~ J-6) · architecture-ui(U-1 · U-2) · architecture-state(S-1) · discipline-houserules(R-1 ~ R-8) · implementation-test(T-1 ~ T-3)을 Claude 정본에 Edit 로 넣고, 지식 스킬 references 를 Codex 로 파일째 복사해 byte 미러를 맞췄다.
- 코드 예시 블록(셸 템플릿 · 틀 CSS · `root_shell.js` · 처리기 · `root_state.py` · `root_initializer.py`)은 설계 v7 블록을 옮긴 뒤(시험장 NA3 판이 그 글자로 지어 통과했다), 조정자 지시로 `root_shell.js` · 처리기의 주석 · docstring 에서 설계 메타(점검 번호 · 판 꼬리 · `@글자위치` · 손잡이 이름 · `OLD` · 호스트 줄)를 걷고 뜻은 쉬운 말로 남겼다 — 코드 토큰은 그대로다(«검증» 의 주석 걷은 비교).
- SKILL.md(K-1 ~ K-12) · 역할(A-1 ~ A-9) · Coordinator(O-1 ~ O-8)는 두 플랫폼에 같은 Edit 를 하고, Codex 쪽은 기존 관례(스킬 이름 `dddjango-web-` 접두 · `${SKILL_DIR}` · `네이티브 셸로`)대로 적었다.
- 가이드(G-1 · G-2) · `Makefile`(`:97` · `:107`) · `AGENTS.md` · `README.md` · `docs/DEVELOPMENT.md` · `docs/file_tree_web.html` · `docs/work_flow_web.html` 을 고치고 계획 · 이 기록을 썼다.

## 바꾼 자리
| 묶음 | 파일 | 내용 |
|---|---|---|
| D | implementation-django references 두 벌 | §2 이동 의미론에 부스트 이동 · 문서 셸 두 꼴 · **«지속 셸» 문단**(템플릿 · 고정 꼴 ①~⑬ · 틀 CSS · 공유 머리 · `?v=` · `root_shell.js` 전문과 지킴의 근거 · own 셸 · 셸 전환 · 앱과 다른 점 · 후보 표지 · 되돌리기) · 처리기 계약 표 · 판별 · 캐시 분리 · **탭 기록 — 세션 저장 직전 한 자리** · 처리기 전문 · 변환 · 미들웨어 · Vary · 전환 · §3 탭 기록 자리 · 재탭 ② · «지속 셸이면» RootState · `shell_rev` · 탭 링크 규칙 · root 시험 · §10 · §11 셸 `<head>` 자리 |
| H | implementation-htmx references 두 벌 | core 2.0.10 전제 · `root_shell.js` 줄 · `historyCacheSize` 0 · hx-* 일곱 + 지속 셸 넷 · 부스트 · 복원 응답 계약 · 페이지 view 는 부스트를 모름 · 막대 움직임 채널 · `hx-boost` 를 «지속 셸에서만» 으로 · PU2 행 · SH1~SH5 행 |
| J | implementation-javascript references 두 벌 | 지속 셸 로드 자리 · `htmx:load` 연결 · 화면 진입 행 · **«지속 셸의 수명» P1~P11 · «history 를 쓰는 기능» H1~H5** · `root_shell.js` 몫 · 문서 스크롤 대가 · 검증 표 두 행 · SDK 로드 자리 |
| U · S · R · T | architecture-ui · architecture-state · discipline-houserules · implementation-test references 두 벌 | root 소유 · 막대 전환 · 지속 셸 탭 기록 · 고정 파일 · 고정 id · 91 · 84 · SH 는 빚 밖 · SDK 자리 · root 브라우저 시험 · root 처리기 시험 |
| K | implementation-{django,htmx,javascript,test} SKILL.md 두 벌 | 요약 줄 |
| A | design-architect-web · design-review-ui-web · coder-web · discipline-reviewer-web 두 벌 | 탭 셸 방식 · 셸 전환 절 · 셸 머리 배선 · root 시험 필수 · 91종 · **감수 §11 지속 셸** |
| O | Coordinator 두 벌 | build-state `tab_shell` · G0 host 상태(탭 셸 방식 · 세션 엔진 · CSP · (5) 미들웨어 · `?` 꼬리 · (7) core 2.0.10) · 빚 스캔 SH 밖 · **4′ «지속 셸 점검(빚 밖)»** · **G1 «탭 셸 방식 행»** · 백스톱 91종 · 전수 테스트에 root 시험 · 리팩토링 모드(셸 바꾸기는 하지 않음 · (가) 줄 자리) |
| G | REQUEST_GUIDE 두 벌 byte | «2.4.0 기준» · 막대 유지 요청 한 줄 |
| 검증 | `Makefile` | `:97` «검사 91종» · `:107` 문단 표지 16 |
| 문서 | `AGENTS.md` · `README.md` · `docs/DEVELOPMENT.md` · `docs/file_tree_web.html` · `docs/work_flow_web.html` | 2.4.0 문장 · 정본 목록 · 86 → 91 · 79 → 84 · 패밀리 표 SH 행 |
| 기록 | `plan-2.4.0.md` · 이 기록 | — |

## 설계와 다르게 한 것(까닭)
- 규칙 글의 산문은 설계의 판 꼬리표(v5 · v6 · v7) · 점검 번호(X6-B1 등) · htmx 글자 위치(`@숫자`) · 시험장 수치 · 호스트 파일 줄을 빼고 적었다 — 런타임 글에 설계 근거 메타를 남기지 않는다(AGENTS «플러그인 작성 원칙»). `root_shell.js` 의 «성립 근거» 도 «지킴의 근거 — htmx 2.0.10 이벤트 계약(지속 셸은 core 2.0.10 이 전제)» 으로 줄였다(D-3 지시대로). 코드 블록 안 주석 · docstring 의 같은 메타도 걷었다(조정자 후속 지시 — 호스트 코드로 그대로 옮겨 적히는 글) — 그래서 `root_shell.js` · 처리기 블록의 sha 는 시험 판과 다르고, 주석 걷은 비교로 같음을 보였다.
- D-3: 설계가 이름 붙인 줄 밖에 §2.2 의 나머지 해설(첫 문서 · 부스트 응답 · 복원 응답 · 탭 목록 두 벌 · 페이지 extends) · §2.9 의 JS 제품 소속 · SH5 겹침 한 줄 · §2.11 의 «OOB 로 새로 놓인 탭 링크는 정착 뒤 부스트» · «내비를 숨기는 화면은 다른 셸» 을 함께 넣었다 — 코더가 같은 셸 꼴을 지을 때 필요한 설명이다.
- D-5: 탭 기록 세 문단은 §2.5 를 줄여 적고, OLD · v4 · v5 · v6 대조표(설계 이력)는 넣지 않았다. D-6 의 넷째 줄은 D-5 문단과 겹쳐 «위 탭 기록» 을 가리키는 짧은 줄로 적었다(같은 규칙 두 벌을 피함).
- D-9: §2.4 의 `root_state.py` 블록도 넣고, RootVM 두 줄 차이는 코드가 아니라 글로 적었다(설계 글에 그 두 줄의 코드 블록이 없다 — 새 코드를 지어내지 않음).
- D-10: 탭 링크 주석을 `{# 지속 셸이면 탭 링크에 id root-tab-<탭 키> · class 수식 — §2 «지속 셸» #}` 로 — 주석 안 백틱 · `{{ }}` 를 피했다.
- D-14: 조각 CSS 줄(`:510`)에 SH5 한 마디를 더했다 — H-9 의 «SH5 → implementation-django §10» 행이 가리킬 글이 §10 에 있게.
- S-1: 같은 줄의 «`RootRequestHandler.process_view` 가 … 적어 두므로» 를 «`RootRequestHandler` 가» 로, 재탭 괄호에 «지속 셸은 요청 없이 맨 위로» 를 더했다 — 새 문장(기록은 응답 뒤)과 같은 줄에서 어긋나지 않게.
- R(설계 밖 한 줄): houserules 러너 사용 줄의 `--only …,pu,wv` 에 `sh` 를 넣었다 — 검사기 구현자가 러너 `_USAGE` 에 `sh` 를 더했다.
- T-3: 두 새 문단을 `:104`(브라우저 예시 코드 끝) 바로 뒤가 아니라 그 예시의 해설 줄들 뒤(«영구 시험 재현성» 앞)에 두었다 — 해설 줄이 예시와 떨어지지 않게. 탭 기록 칸은 하위 목록으로 나눴다.
- A-3: 새 문장을 «근거 `architecture-ui` §6.» 뒤가 아니라 앞에 넣었다(근거가 줄 끝에 남게).
- A-8: «표준 글과 같음(채택한 손잡이 글 포함)» 에서 손잡이 구를 뺐다(고른 손잡이 없음 · 손잡이 글은 규칙 글에 없음). 항목은 §10 처럼 줄마다 하나로 적었다.
- O-4: «G0 «지속 셸 점검» 에서 «둠» …» 구의 굵은 표시를 풀었다 — 문단 대조 표지(`**지속 셸 점검(빚 밖)**`)와 헷갈리지 않게(표지 대조는 표지 문단 한 줄씩만 잡힌다 — «검증»).
- byte 미러(references 12 · REQUEST_GUIDE)는 Claude 정본을 Edit 로 고친 뒤 Codex 로 파일째 복사(`cp`)하고 `cmp` · `diff -rq` 로 확인했다 — 내용 편집은 모두 Edit 로만 했다.
- `docs/file_tree_web.html`: 지정 줄 셋 밖에 같은 파일의 «79종» 둘(lede · 슬라이스 끝 행)을 84 로 고치고 패밀리 표에 SH 행(5 · 합계 91)을 더했다(설계 «+ 같은 파일 86 표기 전수 · 패밀리 목록에 SH»).

## 구현 검토 보완(운영자 · 10-11 23:40 ~ 10-12 — 지적 · 처분 표는 `plan-2.4.0.md` «구현 검토와 보완»)
- 독립 구현 검토 둘(`<S>/f81/review-impl-codex.md` «배포 멈춤» 차단 2 · `<S>/f81/review-impl-claude.md` «보완 후 배포» 차단 2 · 중요 4 · 사소 11)을 받아 고쳤다.
- 검사기 · 픽스처: 보완 1차(Codex — `<S>/f81/fix1-checker.md`) · 보완 2차(Claude — `<S>/f81/fix2-checker.md`). 고친 파일은 `scripts/src/check_shell.py` · `scripts/src/products.py`(두 벌 byte) · `scripts/test/fixtures_patch240_shell.py`. 2.4.0 셸 픽스처 271 → 412 · 전체 3,530 → 3,671(FAIL 0).
- 규칙 글(운영자 Edit · 두 벌 같은 Edit 뒤 `cmp`): implementation-django references — 탭 한 칸 레코드 `RootTab` 을 `root/scaffold/state/root_tab_state.py` 의 `RootTabState` 로 나눔(RootVM 예시 두 줄 · 문장 셋 · «지속 셸이면» 블록 둘로) · 공유 머리 문장에 foundation 순서 · 꼴 ⑨ «들여쓰기 · 줄바꿈 차이는 무시» · «지속 셸이 택한 미지원 범위» / architecture-state references — `shell_rev()` 는 시동 질문이 아님 한 문장 / implementation-django SKILL 두 벌 — «복원 실패는 409 — 5xx 는 그 상태 그대로».
- **설계와 다르게 한 것(검토 뒤)**: ① `RootTab` → `RootTabState` · 파일 나눔(설계 §2.4 블록은 `root_state.py` 한 파일 — 검사기 NM3 · NM1 이 받는 꼴로) ② SH2 꼴 ⑨ 의 정규화를 «태그 사이 공백» 에서 «공백 줄 접기» 로 넓힘 ③ SH4 foundation 묶음은 경로 순이 아니라 관례 순(`FOUNDATION_TOKENS`) ④ SH4 는 기준점 트리가 없으면 파일로 있는 옛 자리 htmx core 를 core 로 봄 ⑤ 파서 예외는 «판독 불가»(설계에 없던 자리 — SH2 · SH4 blocker · 그 밖 `[info]`) ⑥ 새 픽스처 임시 폴더는 시스템 임시 폴더. 까닭은 모두 «규칙 글의 표준 코드를 그대로 옮긴 셸이 검사기를 통과해야 한다» 와 «표지 없는 호스트 · 지원한다고 적은 구성에 거짓 blocker 를 내지 않는다» 다.
- 2차 검토(`<S>/f81/review-impl2-codex.md` «배포 멈춤» 차단 2 — verbatim 필터의 토큰 경계 · 안쪽 공백 / `<S>/f81/review-impl2-claude.md` «그대로 커밋 · 배포 가능» 차단 0 · 중요 2 · 사소 7) → 보완 3차(운영자 — `<S>/f81/fix3-verbatim.md`): `products.shell_directives` 를 Django Lexer 토큰 경계로 새로 씀(호출 세 곳 · 두 벌 byte) · 픽스처 «Lexer 경계» 18 단언 · 2.4.0 셸 픽스처 412 → 430. 글: 감수 두 벌에 «`[info] SH 판독 불가` 파일도 손으로 본다» · 하우스룰 트리 · 표와 `docs/file_tree_web.html` 에 `root_tab_state.py`.
- 3차 검토(Codex `<S>/f81/review-impl3-codex.md` «배포 멈춤» 차단 3) → 운영자가 규칙대로 멈추고 물음(03:00) → 결정 34(사용자 «가.» · 03:22:06 전): 3차가 새로 연 ㉢(실제 include 인자 안 `{%` 글자 가림)만 고치고 배포 · 공용 주석 · verbatim 판독에서 온 ㉠ ㉡ 은 알려진 한계(계획 «닫지 않은 것» ⑦ · 2.4.1). 보완 4차: `shell_directives` 가 실제 토큰 범위 보존 · 픽스처 2 단언 · 감수 두 벌 한 구절.
- **설계와 다르게 한 것(2차 검토 뒤)**: ⑦ SH 지시문(extends · include · block)은 주석 가린 뷰의 정규식이 아니라 Django Lexer 와 같은 토큰 경계로 읽는다 — 변수 · 주석 토큰 안이나 여러 줄에 걸친 `{% %}` 글자, verbatim 안의 지시문은 글자다(IM · 빚 쪽 `parse_template_edges()` 는 그대로).
- 사고: 보완 1차 중 실제 `dddjango-web/commands/dddjango-web.md` 가 비워졌다가 복구됐다(경위 · 대조는 계획의 같은 절).
- 아래 «검증» 표의 `verify_comment_strip.txt` 값 가운데 `root_state.py` 행(`b0595de6…` — 설계 블록과 바이트 같음)은 위 ① 고침 앞의 값이다(지금 규칙 글은 블록 둘 · `RootTabState`). `root_shell.js` · 처리기 · 틀 CSS · 셸 템플릿 · `root_initializer.py` 블록은 그 뒤 바뀌지 않았다.

## 검증(이 구현자가 돌린 읽기 전용 확인)
| 실행 | 결과 |
|---|---|
| 규칙 글 펜스 블록 ↔ 시험 판(`<S>/f81/verify_comment_strip.py` → `.txt`) | `root_shell.js` 규칙 글 `288e2527…` · 시험 판 `feb92d24…` — `//` 주석 걷고 공백 정규화 같음 · 처리기 규칙 글 `a56438f8…` · 시험 판 `f77d292c…`(블록 부분 `fa86ba9d…`) — `#` 주석 · docstring 걷은 토큰 · AST 같음 · 틀 CSS `948d9eb6…` · 셸 템플릿 `e3b469ed…` · `root_state.py` `b0595de6…` · `root_initializer.py` `7ead3edc…` 는 설계 v7 블록과 바이트 같음 · 블록 안 설계 메타 잔존 0 · 토큰 하나 바꾸면 어긋남 확인 |
| references byte 미러(`diff -rq` — 지식 스킬 12) | 12/12 같음 |
| REQUEST_GUIDE byte 미러(`cmp`) · `python3 workspace/tools/request_guide_contract.py` | 같음 · PASS |
| SKILL.md 4쌍 — Codex 를 접두 관례로 되돌려 `diff` | 4/4 차이 0 |
| 역할 4쌍 · Coordinator — 바뀐 줄(낱말 단위)을 치환 셋 · 접두 관례로 맞춰 대조 | 같음(역할 5 · 2 · 6 · 19 줄 · Coordinator 17 조각) |
| Makefile `verify-web` 문단 대조 고리 흉내(표지 16 · 역할 7 · 0T 1) | 모두 같음 · 새 표지 둘은 각 한 줄 |
| `git grep -n -e '86종' -e '79종' -- ':!workspace'`(web 쪽) | 남은 것은 픽스처의 정규화 글자뿐 |
- 돌리지 않은 것(운영자 몫): `make verify-web`(기능 커밋 전 · 후) · `make verify` · `claude plugin validate dddjango-web --strict` · 브라우저 · 네트워크 · git 커밋 · 봉인.

| 운영자 실행 | 결과 | 증거 |
|---|---|---|
| `make verify-web`(기능 커밋 전) | | |
| `make verify-web`(기능 커밋 뒤 · 봉인 앞) | | |
| `make verify` | | |
| `claude plugin validate dddjango-web --strict`(판 올림 뒤) | | |
| 독립 구현 검토 | | |
| 지문 무변 실측(`plan-2.4.0.md` 표) | | |
| 실기기 확인(§8.4 ⑤) | | |

## 커밋
| 커밋 | 내용 |
|---|---|
| | 기능 — 규칙 글 · SKILL.md · 역할 · Coordinator · 가이드 · 검사기 · 픽스처 · Makefile · 저장소 문서 |
| | 봉인 chore(Makefile) |
| | 계획 · 이 기록 |
| `make release-web` | 판 올림 · 태그 · Release |

## 안 한 것 · 남은 것
- 검사기(`scripts/**`) · 픽스처 · 매니페스트는 고치지 않았다(다른 구현자 몫 · 판은 `make release-web`). git 쓰기 · `manifest_seal` · 릴리즈 · 브라우저 · 네트워크를 실행하지 않았다.
- `refactor_audit.py` 의 discipline 렌즈는 «`agents/discipline-reviewer-web.md` §점검 항목» 전체를 배정하므로 새 §11 이 자동으로 든다 — self-test(`make verify-web` 안)로 확인할 것.
- 실기기 확인 권함(§8.4 ⑤)과 그 결과 · 처분, 지문 무변 실측, 독립 검토는 위 칸에 운영자가 채운다.
