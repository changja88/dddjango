# 진단 — dddjango-web 기능 요청의 G0 빚 처리 (결정 1-d · 로드맵 6a) (2026-09-27)

사용자 결정 1-d(`workspace/plan/2026-09-26-refactor-path-repair/evening-report.md:69`): «dddjango-web 기능 요청도 dddjango 와 같은 방식으로 한다. 검사기 빚은 항상 처리하고(B1·R1·R2 를 web 에 적용), 정리 요청은 리팩토링 커맨드로 안내한다.» 이 문서는 진단만 한다. 설계·적대 검토·계획·계획 리뷰·사용자 승인·구현은 web 수리 관례에 따라 이어서 한다.

기준 트리: 플러그인 = 이 저장소 작업 트리(dddjango-web v1.1.25 · `b5774ed5`). 현장 = spring_dream_server main `495128e26`(09-27 02:31 — `git show` 로 web/ 를 스크래치에 재구성) · 스크래치 복제 `12d876dcc`(09-26 04:41 — `bt/sds-main` 의 `--shared` 복제). 원본 저장소에는 `log`·`show`·`grep`·`ls-tree` 만 썼다.

## 결론 (5줄)

1. **현행**: web 커맨드에는 빚 조사 단계가 없다(«빚» 0회 · Codex 미러도 0회). 백스톱은 G2 직전과 마무리 직전에만 돈다. 인자는 `--diff-base <git_snapshot>` 이고, 새로 만든 파일·추가된 줄·새 단위만 검사한다(입력을 거르는 게이트다). 하우스룰 §7 은 «레거시에는 불발화»를, §8 은 «기존 파일의 개명·이동을 요구하지 않는다»를 규범으로 적고 있어 B1 과 정반대다. 전체 실행 옵션(`--all`)은 있지만 «게이트 용도 아님»으로 적혀 있다. 앵커 차분·legacy 잔존 보고·원장은 없다(`ledger.py` 는 1.1.20 에서 철거됐고, `backstop-baseline.json` 은 문서에만 있고 러너에는 없다).
2. **이식 가능 비율**: dddjango 의 빚 처리 요소 19개 가운데 그대로 옮길 수 있는 것이 4, 바꿔야 하는 것이 13, 옮길 수 없는 것이 2다. 옮길 수 없는 둘은 «정리할 것이 없으면 정지»(1-d 때문에 대상이 사라진다)와 `behavior_guard.py` 를 그대로 쓰는 것(플러그인에 테스트가 없어 전제가 서지 않는다)이다.
3. **필요한 새 장치**: ① 구조 4패밀리만 도는 전체 범위 스캔과 기계가독 출력. 지금 `--all` 에는 과거 시안 빌드 검사가 섞여 있어서, 코드 빚이 0 이어도 exit 2 가 난다. ② G2 의 «ⓐ 잔존 M» 계산. ③ web 산출물 폴더 안에 실행 기록 자리(실행 줄·결정 줄·G0 정지). 현 규칙은 G0 를 거부하면 새 폴더를 지운다. ④ 슬라이스 0 의 동작 보존 근거(사용자 결정이 필요하다).
4. **현장 빚 규모(실측)**: 현장 main web/ 는 358파일·8영역·12화면이다. 여기서 백스톱 구조 빚은 **3건**이다. 모두 WN8(`web/static/images/` 의 kebab 파일명 3개)이고, 참조하는 템플릿은 2개, 영역 안 빚은 0이다. 비차단 전체 트리 검사로는 clip 17건, focus 1건이 나온다. 과거 시안 빌드 15개 중 14개가 red 지만 이는 코드 빚이 아니다. 11개는 digest 만료다(digest 가 web/ 전체의 해시라서 새 레인이 올 때마다 전부 만료된다). 8개는 manifest 대조 단계에서 먼저 막힌다(유니코드 정규화 검사기 결함).
5. **추정 작업량(추정)**: 2.5~4 작업일. 산문 정본이라 온톨로지 비용은 0이다. 할 일은 스크립트 모드 1개와 픽스처, 커맨드·에이전트 3·가이드·하우스룰 수정, Codex 의미 미러, 행동 시험이다. 상한은 슬라이스 0 동작 보존 장치를 새로 만들 때다. 1-c(web 리팩토링 커맨드)와 함께 배포해야 한다. 정리 요청 안내와 ⓐ′ 가 그 커맨드로 가기 때문이다.

---

## 1. 현행 web 파이프라인 (실측)

### 1-1 단계·게이트·모드

| 구분 | 현행 | 근거 |
|---|---|---|
| 모드 | 풀 / 수정 / 트리비얼 3종이다. 파일 수가 아니라 구조 단위로 판별하고, G0 배너의 1급 항목으로 승인받는다. 정리 요청을 가르는 규칙과 «모드 이름 지시는 판별 입력이 아니다» 규칙은 없다. | `dddjango-web/commands/dddjango-web.md:119-127` |
| 재개 입구 | 수정·재동결·검증 재요청과 세션 복구를 받는다. 요청 복원, 비교 범위, 정체 순응 감사(`--phase identity`)를 거친다. | 같은 파일 `:22-31` |
| Phase 0 (G0) | 전제조건(git·청결·배선 6종) → 스코프 → 계약 출처(없으면 ⓐ정적/ⓑ발주) → **G0 배너 전에 산출물 폴더 확정** → 디자인 출처 해소(수집·동결·독립 입력범위 검토·inputs) → G0 배너(모드·배선·출처·폴더·배치 질문). 배너를 거부하면 새로 만든 폴더를 폐기한다. | `:129-165` · 폐기 `:163` |
| Phase 1 (G1) | architect → design-review-web(+discipline-reviewer-web 명세 점검) → 반영·중재 → G1 → 계약 절단. **pre-gate 는 없다.** | `:167-176` |
| Phase 2 (G2) | 진입 준비: ⑤ 산출물·시안 자산 번들·골격·배선을 커밋한 **뒤** ⑥ `git_snapshot` 을 기록한다. 슬라이스는 정수 임계로 도출한다(풀 7/8 · 수정 5/6). coder-web 을 순차 호출하고, 구현 화면 검증 → 감사 → 백스톱 → G2 배너(렌더 실측·모션·clip 은 판단 자료)로 간다. | `:180-196` |
| Phase 3 | 시안 대상이면 백스톱을 다시 돌린다. 이어서 보고하고, 미커밋 합치기(soft reset)를 한다. | `:198-209` |
| 수정 모드 | G0 에서 영향 파일 목록을 만든다. G1′ 은 조건부다. 감사는 touched 한정이다. 백스톱은 «무관한 기존 코드엔 발화하지 않는다». | `:211-220` · `:219` |
| 트리비얼 | Coordinator 가 직접 편집한다. 폴더·build-state 를 만들지 않는다. touched 백스톱 + check + clip 을 돌린다. | `:222-229` |
| 테스트 | 플러그인은 영구 테스트를 만들지 않는다. green 판정은 `py_compile` 과 `manage.py check` 베이스라인 대비다. | `dddjango-web/agents/coder-web.md:37` · `:51` |
| «빚» 등장 | 커맨드 0 · Codex `SKILL.md` 0 · 에이전트 4개 0 · REQUEST_GUIDE 0 | grep 실측 |

### 1-2 백스톱의 호출 방식과 범위

| 항목 | 실측 | 근거 |
|---|---|---|
| 호출 지점 | G2 직전(`:195`), 마무리 직전(시안 대상 `:200`), 수정 모드 G2 직전(`:219`), 트리비얼 편집 뒤(`:229`). **Phase 0 에는 없다.** | 커맨드 |
| 인자 | `--diff-base <build-state git_snapshot>`(트리비얼은 편집 직전 HEAD), 시안 대상은 `--design-build <폴더>` | `:195` · `:229` |
| 검사 수 | **26종**(WS8 + WI4 + WN8 + WP6). 출력도 «검사 26종»이다. AGENTS.md 의 «24종»은 낡은 값이다. | `dddjango-web/scripts/backstop.py:32` |
| «touched 한정»의 정의 | 게이트 입력은 네 가지다: `git diff --name-status <base>`(작업 트리 대 base, 미커밋 포함) + `git status --porcelain -uall`(미추적) + `git ls-tree -r <base>` + `git diff -U0` hunk. **구조(WS)·명명(WN)** 은 added 파일·디렉터리만 본다(rename·copy 는 새 경로가 added, D 는 제외). **격리(WI)·순수성(WP)** 은 touched 파일의 added 줄만 본다(새 파일은 전 줄). **골격(WS5)** 은 base 에 하위 파일이 0개인 신규 단위(영역·화면 개념·client BC·web/ 자체)만 본다. | `scripts/src/common.py:338-370` · `:444-506` · `scripts/src/check_structure.py:175-252` |
| 게이트의 성격 | **입력 거르기**다. 발견을 앵커 전후로 비교하는 «판정 차분»(dddjango `registry_gate.py` 의 N∖L)이 아니다. 그래서 legacy 잔존을 볼 수 없고, 슬라이스 0 이 고치지 않은 기존 위반은 G2 에 나타나지 않는다. | 같은 곳 |
| 전체 범위 실행 | `--all` 이 있다(`backstop.py:152`). 게이트를 무시하는 전역 검사이고, 규범은 «레거시 프로젝트에서 발견 폭주가 정상이며 파이프라인 게이트 용도가 아니다»로 적는다. `--diff-base` 가 없거나 비git 이면 «전역 퇴화» notice 가 붙는다. | `houserules final.md:204` · `backstop.py:193-200` |
| 섞이는 검사 | 시안 증거 검사(`validate_inputs`·`validate_visual`)는 **`--only` 와 무관하게 늘 돈다.** `--design-build` 가 없으면 발견된 과거 빌드 전부를 본다. 생략되는 것은 비시안 예외 조건이 모두 충족될 때뿐이다. | `backstop.py:220-250` · `:95-133` |
| exit | 0 = clean · 1 = 사용·내부 오류(미실행 — 통과가 아니다) · 2 = blocker | `backstop.py:10-11` · houserules §7 |
| 출력 | `[Wxx] BLOCKER — web/<path>[:line]` 텍스트와 요약 1행뿐이다. JSON 도, 안정 키도 없다. | `src/common.py:35-42` |
| 기준선·원장 | `backstop-baseline.json` 은 커맨드 `:44`·`:68`·`:195` 와 houserules `:205` 에 «러너가 브라운필드 첫 실행에 생성»으로 적혀 있다. 그러나 **러너에는 생성 코드가 없다**(scripts 전체 grep 0). `ledger.py` 는 1.1.20 에서 철거됐다(`Makefile:288-289`). 현재의 legacy 면제는 입력 게이트 그 자체다. | grep 실측 |
| 그 밖의 전체 트리 검사 | `check_clip_clearance.py <web>`: web 전체를 보고, G2 에서 «판단 자료(비차단)»다(`:196`). 트리비얼에서도 돈다(`:229`). `check_motion_spec.py`: G2 역스윕이 web 전체의 `@keyframes` 를 본다. `check_focus_ring.py`: **커맨드 호출이 0이다**(감수자 의무로만 남아 있다 — `discipline-reviewer-web.md:63`). | 커맨드 grep |

### 1-3 B1 과 부딪히는 현행 문면

| 위치 | 현행 문면 | B1 적용 시 |
|---|---|---|
| houserules §7 `final.md:203` | «레거시(기존 drift)에는 불발화 — "새 코드부터 표준" 원칙의 기계 집행» | G2 판정 게이트로는 유지할 수 있다. 그러나 «새 코드부터 표준» 원칙 문장은 반대가 된다. |
| houserules §7 `:204` | `--all` 은 «파이프라인 게이트 용도가 아니다» | G0 스캔에 쓰려면 고쳐야 한다. |
| houserules §8 `:214` | «기존 파일의 개명·이동을 요구하지 않는다» | 검사기 빚에 한해서는 반대다. 나머지 관행 교정(`views.py` 분해 등)은 결정 1-a 에 따라 리팩토링 커맨드 몫이다. |
| 커맨드 `:219` | «무관한 기존 코드엔 발화하지 않는다» | 반대다(R1). |
| REQUEST_GUIDE `:198-205` | web 으로 «동작 유지 + 코드 정리» 요청을 받는다. | 1-d 의 «리팩토링 커맨드로 안내»와 반대다. |
| (dddjango 대응) `dddjango/skills/discipline-houserules/references/final.md:279` | «brownfield 는 면제가 아니라 아직 안 갚은 빚» | web 에는 대응 문장이 없다. |

---

## 2. 이식 매핑표

판정 기호: (a) 문면을 거의 그대로 옮긴다 · (b) web 구조에 맞춰 바꿔야 한다 · (c) web 기능 요청 커맨드에서는 성립하지 않는다. dddjango 근거는 `dddjango/commands/dddjango.md` 의 행 번호다.

| # | dddjango 요소 (근거) | 판정 | web 에서 걸리는 것 (사실) |
|---|---|---|---|
| 1 | 모드 판별: 정리 요청 → 풀, 모드 이름 지시는 판별 입력이 아니다, G0·빚 스캔 생략 지시는 따르지 않는다 (`:67`) | (b) | web 은 모드가 3개다(트리비얼 포함). 1-d 에 따라 정리 요청은 **리팩토링 커맨드로 안내하고 멈춘다** — dddjango 의 «정리 요청 → 풀»과 다르다. 안내할 목적지(1-c)가 아직 없다. «모드 이름 지시 불인정»은 (a)다. |
| 2 | 빚 스캔: registry 27종을 루트에서 실행, exact command·exit 기록, 증거 없는 «빚 0» = G0 blocker, «실행 불능» 정의, 차분 도구로 대체 금지 (`:79`) | (b) | web 은 러너가 1개라서 «27종 각각의 command»가 아니라 «1 command · exit · 발견 목록»이 된다. `--all` 은 있지만 시안 증거 검사가 섞여 exit 2 가 코드 빚과 무관하게 난다(§3-5). 기계가독 출력이 없다. |
| 3 | 스캔 범위: 대상 BC(`application/<bc>/`) + «미룰 수 없음»은 경로와 무관, 설계가 스캔 밖 BC 를 건드리면 추가 스캔 (`:79`) | (b) | web 의 단위는 영역(`web/<area>/`)과 공용 칸(`client/<bc>/`·`design_system/`·`static/`·`base/`)이다. 현장 빚 3건은 모두 공용 칸(`static/images/`)에 있다. 그래서 «영역만» 스캔하면 한 번도 드러나지 않는다(설계 사안). |
| 4 | «미룰 수 없음» 판정 물음(손대지 않아도 해로운가) (`:79`) | (a) | 물음은 그대로 옮긴다. web 에서 해당할 만한 예(추정): WP6(닫히지 않은 Django 주석 — 응답에 노출)과 WP1(HTMX core 중복). |
| 5 | G0 빚 질문 ⓐ/ⓑ + 규모 1행(항목·단위·파일 수) (`:80`) | (b) | web 커맨드는 이미 ⓐ/ⓑ 를 선택지 4곳에서 쓴다: 계약 없음(`:137`), 폴더(`:139`), 디자인 포인터 ⓐ/ⓑ/ⓒ(`:144`), 엔드포인트 없음(`:237`). dddjango 는 09-26 에 ⓐ/ⓑ/ⓐ′ 를 빚 결정 전용으로 정했다(`:80`·`:86`). 따라서 web 쪽 라벨 4곳을 바꿔야 한다. 규모 1행의 «BC 수»는 «영역·칸 수»가 된다. |
| 6 | ⓐ′: BC별 정리 요청을 먼저 따로 진행 (`:80`) | (b) | 1-d 에 따라 web 의 «따로 하는 정리 요청»은 리팩토링 커맨드(1-c)다. 그래서 1-c 가 있어야 선택지가 성립한다. |
| 7 | 결정 출처: ⓑ 는 본인 직접이나 사용자 원문 파일:행·시각이 있어야 한다, 출처 없는 ⓑ → STOP, 세 번째 질문은 없다 (`:82`) | (a) | 문면을 그대로 옮긴다. web REQUEST_GUIDE §7 에는 «미룸 원문» 규칙이 없다. dddjango `REQUEST_GUIDE.md:119-127`·`:188-190` 을 대응해 넣어야 한다. |
| 8 | 충돌: 정리를 막는 환경 사실은 ⓑ 가 아니다 (`:83`) | (a) | 그대로다. 현장 발주서는 web 레인에도 허용 경로를 적는다(예: `orders/2026-09-08-web-chart-screen.md:84`). |
| 9 | 정리할 것이 없으면 G0 정지 (`:84`) | (c) | 정리 요청에만 걸리는 규칙인데, 1-d 로 web 정리 요청은 리팩토링 커맨드로 간다. 그래서 web 기능 커맨드에서는 대상이 없다(리팩토링 커맨드 쪽으로 옮겨 간다). |
| 10 | 실행과 앵커: `refactor-scope.md` 실행 줄, `build_anchor`, ⑴⑵⑶ 판정, 잇기/승인됨/폐기, `pregate-report` 행 (`:85`) | (b) | web 에는 build-state(phase·g2_approved·git_snapshot)가 있지만 «실행» 개념이 없다. 규범은 같은 화면이면 폴더를 재사용하라고 한다(`:49`). 그런데 현장 발주는 수정 모드도 **새 run 폴더**를 만든다(6-3-3 발주서 §2-7). `git_snapshot`(Phase 2 진입 · 산출물 커밋 뒤)은 `build_anchor` 와 시점이 거의 같다. pre-gate 행은 (c)다(web 에 pre-gate 가 없다). |
| 11 | G0 질문 순서와 정지 기록(`G0 정지` 절을 폴더에 append) (`:86`) | (b) | web G0 에는 질문이 더 있다(계약 없음·폴더·디자인 포인터·입력 차단·배선·배치). 또 web 은 G0 배너 **전에** 폴더를 만들고, 거부·중단하면 새 폴더를 **폐기**한다(`:163`). «정지를 폴더에 기록»과 정면으로 충돌한다. |
| 12 | Phase 1 «슬라이스 0 과 비위반 이동의 STOP» · `ⓐ 재상정` 절 (`:106`) | (b) | 문면 대부분은 옮길 수 있다. 다만 리뷰어 구성이 다르고(design-review-web 1 + discipline-reviewer-web 명세 점검), 슬라이스 0 은 **이번 명세 파일 목록 밖의 기존 파일**을 건드린다. «pre-gate 재발화 판형» 참조는 빠진다. |
| 13 | Phase 2 슬라이스 0: 선행, 혼합 금지, 커밋 분리, 슬라이스 0 뒤 관련 테스트 green, 검사기 오탐 → STOP(플러그인 결함) (`:113`) | (b) | web 슬라이스 도출은 명세 파일 목록의 정수 임계(`:181`)다. 슬라이스 0 을 계수에서 빼고 맨 앞에 두는 규칙을 새로 써야 한다. «관련 테스트 green»은 플러그인에 테스트가 없어 대응물이 없다(§2-1). 슬라이스마다 커밋하는 규칙은 이미 있다(`:188`). |
| 14 | 0T/0C 동작 보존 창(`behavior_guard.py open/close/verify`) (`:114`) | (c) 그대로는 불가 | `behavior_guard.py` 의 두 전제(테스트가 창 전과 같다 · 테스트가 동작을 덮는다)는 플러그인 관점에서 web 에 없다. 입력 파일(`refactor-scope.md` 실행 줄 · `build_anchor`)도 web 폴더에 없다. 제외 경로는 `.dddjango/` 뿐이다(`behavior_guard.py` 의 `EXCLUDED_PREFIXES`). 마이그레이션 축은 web 과 무관하다. 대체 근거는 §2-1 과 열린 질문 Q3 에 적었다. |
| 15 | registry_gate 판정 차분(앵커 N∖L) · legacy 잔존 보고 · 승인 유입 provenance (`:123`) | (b) | 귀속(새 위반)은 현 입력 게이트가 이미 막는다. 없는 것은 legacy 잔존 보고와 ⓐ 잔존 판정이다. 승인 유입(`approved-merges.txt`)은 현장 발주가 web 폴더에 이미 쓰고 있지만(6-3-3 폴더 실재) 플러그인은 모른다. |
| 16 | G2 «G0 ⓐ N건 중 잔존 M» + 재상정 제외 K + «동작 보존» 1행 + 차단 (`:174`) | (b) | G2 에 전체 스캔(구조만)을 한 번 더 돌리고 ⓐ 목록과 교집합을 내야 한다. 키는 WS/WN 이 `검사ID+경로`(행 없음), WI/WP 가 행 번호가 흔들리므로 `검사ID+경로+메시지` 정규화가 필요하다. |
| 17 | 수정 모드 R1: G0 3·4번을 그대로 수행, ⓐ 가 있으면 G1′ 생략 금지 (`:190`·`:194`) | (a) | 문면은 옮긴다. 대신 커맨드 `:219` 의 반대 문장을 지우고, 수정 모드 임계(5/6)에 슬라이스 0 을 반영해야 한다. |
| 18 | 경계: 위임되지 않는 것(출처 없는 ⓑ·폐기·사후 개정), 게이트 질문의 «대가 한 줄», AskUserQuestion 채널 (`:218` 이하) | (b) | web 게이트 질문 규칙은 «권고 후보 선택지 + 기타 자유입력»뿐이다(`:113`). 대가 한 줄·STOP 기록 형식·위임 한계 문장이 없다. Codex 쪽은 `request_user_input` + 평문 fallback 절(Codex `SKILL.md:62-74`)에 합쳐야 한다. |
| 19 | (web 전용) 트리비얼 패스트트랙 | (b) 신규 | dddjango 에는 트리비얼이 없다. B1 «예외 없이»와 R1 «작은 수정도 전부 정리»를 문면대로 읽으면, 스캔 범위에 빚이 있을 때 트리비얼을 수정 모드로 올려야 한다(트리비얼은 폴더·build-state·coder 가 없어 슬라이스 0 을 담을 곳이 없다). 이것은 해석이므로 사용자에게 알려야 한다. |

**합계**: (a) 4(#4·#7·#8·#17) · (b) 13 · (c) 2(#9·#14). #14 는 «장치를 그대로 쓰는 것»이 불가라는 뜻이고, 동작 보존 요구 자체는 결정 2 Q1(가)에 따라 남는다.

### 2-1 슬라이스 0 의 동작 보존 근거가 될 수 있는 기존 장치 (사실만)

| 장치 | 무엇을 보나 | 동작 보존 근거로서의 성질 | 근거 |
|---|---|---|---|
| 플러그인 테스트 | 없다. coder-web 은 영구 테스트 파일을 만들지 않는다. | 해당 없음 | `coder-web.md:37` |
| green 래칫 | `py_compile` + `manage.py check` 베이스라인 대비 신규 0 | 문법·시스템 검사일 뿐이다 | `coder-web.md:51` |
| 현장 `tests/web` | 79파일 · `def test_` 927개(실측). **플러그인이 아니라 발주 계약이 요구한다**(예: 6-3-3 발주서 `:61` «커밋마다 tests/web 무-DB · DB 단계»). 6-3-3 레인 실적: 무-DB 1381 passed, DB 217 passed. | 현장에서는 0C 식 «테스트 고정» 판정의 재료가 될 수 있다. 다만 플러그인은 소유하지 않고, 템플릿·CSS·JS 를 얼마나 덮는지는 측정하지 않았다. | `git ls-tree`·`git grep` 실측 · 6-3-3 `visual-check.md:745-746` |
| `implementation_digest` | **web/ 전체 트리**의 해시(+host_files) | «바뀌었다»만 알 수 있고 «같다»는 알 수 없다. 한 바이트만 바뀌어도 모든 빌드의 visual 증거가 만료된다. | `check_design_evidence.py:430-449` |
| 렌더 실측 대조 | `render_audit.js` → `compare_render_audit.py`: 글자 크기·유효 웨이트·행간·정렬·색·상대 위치·pinned·컬럼 폭 | 두 JSON 의 축별 diff 다. 전후 두 실측을 비교하는 데도 쓸 수 있다(도구는 입력의 출처를 묻지 않는다). 조건: 브라우저, 같은 실행자·같은 창폭, `has_render_audit` 빌드, 측정한 페이지 한 장. | 커맨드 `:196` |
| 구현 화면 검증·캡처 | case 별 재관찰, `visual-evidence.json`, `captures/` | 사람·LLM 의 판정이다. 현장 5-1-1 은 «case 둘 재촬영 픽셀 차이 0»을 손으로 적었다(커밋 `6de371734` 메시지). | 커맨드 `:191-193` |
| 백스톱·clip·focus·motion | 구조·CSS 정적 검사 | 동작을 판정하지 않는다 | §1-2 |
| git 이름 바꾸기 판정 | `git diff -M` 유사도 + 참조 치환 | 현장 빚 3건(파일명 3개 바꾸기 + 템플릿 2개의 참조 5줄)에 딱 맞는 판정이다. 이를 수행하는 web 장치는 **없다**. | §3-3 |

---

## 3. 현장 규모 (실측)

### 3-1 측정 방법

- 구조 4패밀리: 스크래치 스크립트(`scratchpad/diag6a/measure.py`)가 러너 모듈(`src/check_*`)을 import 해 `all_mode=True`(= `--all` 의미)로 돌렸다. 시안 증거 검사는 섞지 않았다. 대상은 두 트리다: ⓐ 현장 main `495128e26` 의 web/ 358파일을 `git show` 로 재구성한 트리(`scratchpad/diag6a/live/`), ⓑ 복제 `12d876dcc`(`scratchpad/diag6a/sds/`).
- 실제 CLI: `backstop.py <복제> --all` → exit 2 · «검사 26종(all) — blocker 17건 (구조 3 · 시안 14)»(원문 `scratchpad/diag6a/cli-all.out`).
- 비차단 전체 트리 검사: `check_clip_clearance.py <live>/web` · `check_focus_ring.py <live>/web`.

### 3-2 검사별 위반 (백스톱 26종 · 전체 범위)

| 패밀리 | 위반 | 내역 |
|---|---|---|
| WS 구조·골격 (8) | 0 | 신규 단위 조건 없이 전 단위 골격을 봐도 0이다. |
| WI 격리 (4) | 0 | — |
| WN 명명 (8) | **3** | WN8 파일명 snake_case: `web/static/images/chunmong-logo-v2.png` · `cloud-ornament.png` · `gold-blossom.png` |
| WP 순수성 (6) | 0 | — |
| **합계** | **3** | 두 트리(`495128e26` · `12d876dcc`)가 같다 |

### 3-3 파일·화면·템플릿

| 항목 | 값 |
|---|---|
| 현장 web/ 규모 | 358파일(html 114 · py 189 · css 15 · js 22 · 그 밖 18) · 영역 8 · 화면 개념 12(auth/login·password_reset·signup · chart/chart · consultation/conversation·record_detail · employee_choice · home · intake/user_info · preferences · related_persons/editor·list) |
| 빚이 있는 파일 | 3 (모두 `web/static/images/` — 공용 칸 · **영역 안 0**) |
| 참조 | 템플릿 2개의 5줄: `web/auth/login/view/login.html:18·23·25`, `web/design_system/component/button/special_button.html:12·14`. `tests/` 참조는 0. |
| 영향 화면 | 로그인(직접), 사용자 정보(`user_info_step.html:174` 가 special_button 을 include) |
| 유입 | `5b4c47a40`(09-06 13:48 · web-auth-2 «시안 이미지 3종 landing»). 그 폴더의 `git_snapshot` `a04ff751` 보다 20커밋 뒤다. 이 커밋을 덮는 G2 백스톱 기록은 찾지 못했다(미확인). 이후 런은 diff-base `c68cbe11`(이미지 커밋 뒤)을 썼기 때문에 그 뒤로 계속 legacy 다. |
| 슬라이스 0 규모(추정) | 파일 3개 이름 바꾸기 + 참조 5줄 치환 · 1칸 · 템플릿 2 |

### 3-4 비차단 전체 트리 검사 (빚 포함 여부는 Q1)

| 검사 | 결과 (`495128e26`) | 현 지위 |
|---|---|---|
| `check_clip_clearance` | exit 2 · 발견 17(모두 «확정» 포함) · 인벤토리 35. 파일별: conversation.css 6 · settings.css 4 · app_shell.css 3 · user_info.css 2 · chart.css 1 · home.css 1 | G2 «판단 자료(비차단)» (`:196`) |
| `check_focus_ring` | exit 2 · 발견 1(`components.css .choice-pair` 안 `<input>`) | 커맨드 호출 0 |
| `check_motion_spec` 역스윕 | 이번 측정에서는 돌리지 않았다(명세가 필요하다). 5-1-1 레인 G2 에서는 발견 14 = «다른 빌드 keyframes · 이 run 0». | G2 판단 자료 |

### 3-5 시안 증거 검사 (코드 빚이 아니다 — Q2)

복제 `12d876dcc` 의 빌드 15개를 첫 실패 단계 기준으로 본 결과다:

| 원인 | 빌드 수 | 성질 |
|---|---|---|
| `manifests[0]: archive inventory differs from frozen tree` | 8 | **검사기 결함**. manifest 는 한글 파일명을 NFD 로 적었고, checkout(`core.precomposeunicode=true`)은 NFC 로 만든다. NFC 로 정규화하면 두 집합은 같다(실측). 새 워크트리에서 도는 레인마다 재현된다(5-1-1·6-3-3 기저 기록에도 같은 8개가 있다). |
| `implementation_digest: stale or incorrect` | 5 | digest 가 web/ 전체의 해시라서, 뒤 레인이 web/ 를 건드리면 만료된다(설계상 필연). |
| `design-input.json` 없음 | 1 | 증거 체제 이전 빌드(auth · 발주서 §6 «구조적 waiver»). |
| 통과 | 1 | 가장 최근 빌드(settings-nickname) |

digest 만 따로 계산하면 증거가 있는 빌드 12개 중 **11개가 만료**됐다(최신 1개만 fresh). NFC 문제를 고쳐도 8개는 digest 단계에서 다시 red 가 된다.

### 3-6 레인 기록의 legacy/touched 분리

| 레인 | 기록 | touched(gated) | 전체·기저 | 처리 |
|---|---|---|---|---|
| home-bottom-nav (09-07) | `backstop.txt`·`-g2`·`-final` | 0 · 0 · 0 | — | — |
| user-info-input (09-08) | `backstop-g2.txt` | 0 | — | — |
| web-auth-screens (09-05~) | `compact-handoff.md:37·56` | 슬라이스마다 0 | — | 기록만 있다 |
| 5-1-1 room-open-signal (09-25 · `lane/5-1-1`) | `baseline/`·`g2/` 7파일 | `--design-build` 0 | 앵커 `7634d52e` 기저: 백스톱 시안 14 · clip 14. G2 전 빌드 14 = 기저 · clip 14 = «anchor 같은 집합» · motion 14 = 다른 빌드 | **손으로 한 앵커 기저 차분** |
| 6-3-3 settings-birth-change (09-25~26) | `backstop-anchor-baseline.txt` · `visual-check.md:750-765` | `--design-build` 0 | 앵커 `4daf2313` 시안 14. G2 전 빌드 15(14 기저 + 예고 1). 무인자(전역 퇴화) 18 = **구조 3 · 시안 15**. 구조 3 은 «main tip 에도 있고 레인 편집 0 → 레인 귀속 0» | legacy 로 분류만 하고 정리하지 않았다 |

관찰(실측): 현장 발주는 web 레인에 dddjango 의 차분 개념을 이미 **손으로** 적용하고 있다. 6-3-3 발주서 §2-7 «과거 시안 빌드의 시안 게이트 red = anchor 기저 · 새 red 0 만 판정», `approved-merges.txt`, dddjango `registry_gate --anchor` «web 귀속 0»이 그 예다. 구조 빚 3건은 레인들이 보고도 «legacy»로 넘겼다. web 에 B1 이 없기 때문이다.

---

## 4. Codex 미러 · 검증

### 4-1 바뀔 파일과 미러 방식

| 정본 (`dddjango-web/`) | Codex (`codex-dddjango-web/`) | 미러 방식 | 새 단계에서의 변경(추정) |
|---|---|---|---|
| `commands/dddjango-web.md` (249줄) | `skills/dddjango-web/SKILL.md` (274줄) | 의미 미러(수동) | Phase 0 스캔·질문·결정 출처·실행 기록, 모드 판별(정리 요청 안내), Phase 1 재상정, Phase 2 슬라이스 0·잔존 M, 수정 모드, 트리비얼, 경계. Codex 는 `request_user_input`·평문 fallback 판형으로 쓴다(dddjango Codex `SKILL.md:58` 에 선례가 있다). |
| `agents/design-architect-web.md` · `coder-web.md` · `discipline-reviewer-web.md` | `skills/dddjango-web-*/SKILL.md` | 의미 미러 | 슬라이스 0 입력·동작 불변 불가 STOP·오탐 STOP. coder-web 의 «영구 테스트 없음»과 동작 보존 근거가 맞물린다. |
| `skills/discipline-web-houserules/references/final.md` §7·§8 | 같은 경로 | byte 동일(현재 SAME). **verify-web 은 대조하지 않는다.** | 레거시 불발화·`--all` 용도·개명 요구 문장 |
| `REQUEST_GUIDE.md` §6·§7 | 같은 경로 | byte 미러(verify-web `cmp`) | 정리 요청 → 리팩토링 커맨드 안내 · 미룸 원문 규칙 |
| `scripts/backstop.py`(+`src/`) · `scripts/test/fixtures_backstop.sh` | `skills/dddjango-web/scripts/` | byte 미러(verify-web `diff -rq` — 현재 동일) | 구조 전용 전체 스캔 + 기계가독 출력 + 잔존 계산 |

### 4-2 `make verify-web` 이 하는 일과 새 단계에 요구할 것

- 현재 내용(`Makefile:94-109`): `run_fixtures.sh`(fixtures_*.sh 13파일) · scripts/assets `diff -rq` · references 4개 `cmp`(implementation-ui 3 · architecture-web 1) · REQUEST_GUIDE `cmp` · `request_guide_contract.py`(배포·발견 계약 — 본문은 보지 않는다).
- **자동 경로 밖이다**: 09-16 지시로 `make verify` 에서 빠졌고 수동 전용이다(`Makefile:23-26`). AGENTS.md 의 «`make verify`의 `verify-web`이 실행»은 낡은 문장이다.
- 새 단계가 요구할 것(추정):
  1. 스캔 모드 픽스처: legacy 만 있는 프로젝트에서 발견이 전부 나와야 한다. 시안 빌드가 있어도 스캔 exit·목록이 흔들리지 않아야 한다. 안정 키도 확인한다. 기존 `mkproj`·`assert_count` 판형을 재사용한다.
  2. 잔존 M 픽스처: ⓐ 를 고쳤으면 M=0, 안 고쳤으면 M>0, 행 이동이 있으면 WI/WP 키를 정규화하는지 본다. 각각 positive control 과 짝을 맞춘다.
  3. houserules `cmp` 를 verify-web 에 추가한다(지금은 사각이다).
  4. Coordinator 산문 규칙은 픽스처로 못 잡는다. web 수리 관례의 **행동 시험**(dddjango 로드맵 1 의 T1~T11 판형 · 호출 `/dddjango-web:dddjango-web`)으로 확인해야 한다.
  5. Codex 의미 미러는 web 에 자동 대조가 없다(dddjango 는 온톨로지 parity 가 있다). 수동 검토 항목이다.
- 배포: `make release-web`. 결정 6 에 따라 dddjango 와 한 번에 배포한다. 릴리즈 창 규칙(진행 중 레인 G0~G2 사이 0)도 web 레인에 적용할지 설계에서 정해야 한다.

---

## 5. 열린 질문 (사용자 결정 — 브리프)

- **Q1 빚으로 셀 검사기** — (가) 백스톱 26종만(현장 3건 · G2 차단 검사와 같은 집합) / (나) + 비차단 전체 트리 검사 clip·focus(현장 +18 · 지금은 «판단 자료»). (나)의 대가: 레인마다 CSS 여유 정리가 앞에 붙는다.
- **Q2 과거 시안 빌드의 증거 red(15 중 14)** — (가) 빚 밖: 현재 빌드만 검사하고 과거 빌드는 기저 차분(현장이 손으로 하는 방식을 규칙으로) / (나) 빚 안. (나)의 대가: digest 가 web/ 전체 해시라 레인마다 과거 화면 11~14개를 브라우저로 다시 관찰해야 한다. 어느 쪽이든 NFC 결함 8건은 플러그인 수리 몫이다.
- **Q3 슬라이스 0 동작 보존 근거(플러그인 테스트 없음)** — (가) 기계 확인: 이름 바꾸기·참조 치환만 허용하는 확인 + 렌더 실측 전후 대조 / (나) 현장 `tests/web`(발주 계약 · 927개)을 고정 대상으로 채택 — 플러그인 규범을 바꾸는 일이다 / (다) 장치 없이 G2 시각 대조와 감사. 결정 2(가)·8(마)가 web 에도 그대로 미치는지를 묻는 질문이다.
- 진단 권고(결정 아님): Q1 (가) · Q2 (가) · Q3 (가). 근거는 §3-2·§3-5·§2-1 의 수치다.

---

## 부수 발견 (별건 이관 — 이 진단에서는 기록만 한다)

1. **유니코드 정규화 결함**: `check_design_evidence.py:346-349` 는 archive inventory 를 정규화 없이 대조한다. 그래서 과거 빌드 8개가 새 워크트리마다 red 다(§3-5). 현장 레인은 이것을 «anchor 기저»로 흡수하고 있다.
2. **유령 기준선**: `backstop-baseline.json` 과 «러너가 베이스라인 생성을 보고하면 커밋»(커맨드 `:44`·`:68`·`:195` · houserules `:205`)에 대응하는 러너 코드가 없다.
3. **AGENTS.md 낡은 값**: «검사 24종»(실제 26) · «스킬 4»(추적 5) · «`make verify`의 `verify-web`»(자동 경로에서 빠짐).
4. **Phase 2 진입 준비의 사각(추론)**: ⑤ 에서 커밋되는 시안 자산 번들·골격·배선(`:180`)은 ⑥ `git_snapshot` 보다 앞선다. 그래서 그 레인의 입력 게이트는 이 파일들을 영원히 보지 않는다(예: 자산 파일명 WN8). 실제로 그렇게 들어온 사례는 확인하지 않았다.
5. `check_focus_ring.py` 는 커맨드 호출이 0이고, `check_motion_spec.py` 역스윕은 다른 빌드의 keyframes 까지 발견으로 낸다(5-1-1 에서 14).
