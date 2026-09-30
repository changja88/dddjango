# 수리 R8e 구현 기록 — web 치환 확인 ④ 를 레인 편집으로 한정 (로드맵 8e)

> **최종 상태는 3차(재검토 반영) 판이다.** 2차 판의 재검토는 «승인»(처분 20/20 · 회귀 0)이었고, 남은 minor 1 · nit 3 을 커밋 전에 닫았다(§10). 2차 산출물은 scratch `impl-R8e/v2/` 에 옮겼다. 아래 §0~§9 는 2차 판 서술이고, 3차가 바꾼 수치는 §10 에 모았다.
>
> 2차 머리: **최종 상태는 2차(구현 리뷰 반영) 판이었다.** 1차 판 뒤 구현 리뷰 두 건(도구 · 문면 — 둘 다 «수정 후 승인» · 사용자 쟁점 없음)이 돌아왔다. 운영 세션 처분은 전건 채택이다. 처분 표는 §9 에 있다. 1차 트리·패치·로그는 scratch `impl-R8e/v1/` 에 옮겨 두었다.

- 작성: 2026-09-30 · 격리 워크트리 `.claude/worktrees/agent-a1b474e9bb020c59e`(브랜치 `worktree-agent-a1b474e9bb020c59e`). **커밋 0 · push 0** 이다.
  - 워크트리는 `acbfffda` 에서 시작했다. 작업 트리가 깨끗해서(변경 0) `git reset --hard 3555f5fc` 로 포인터만 설계 기준으로 옮겼다(새 커밋 없음).
  - 커밋 대신 `git add -A`(이 기록 제외) → `git write-tree` 로 트리 id 를 남겼다. 인덱스는 2차 트리가 스테이징된 상태다.
    - 기준 트리 `e8c54ce5b442f050e60a31df399fbe5ee94b5c0f`(HEAD `3555f5fc`)
    - 1차 트리 `f368d2c78a427d685fbe3ddfb48a61f410741325`(15파일 +1,487/−101)
    - 2차 트리 `58786ca3cc3c27164ee88a6781c6b026c3b3f676` — 17파일 +1,695/−105(1차 대비 15파일 +265/−61)
    - **3차 트리 `1f22b19ed21e6ca245f41430aee18d3321d5117b`** — 17파일 +1,727/−105(2차 대비 8파일 +52/−20)
    - 3차 패치: scratch `impl-R8e/p1-web-subst.patch`(기준 → 3차) · 2차 대비 증분 `impl-R8e/v2-to-v3.patch` · 2차 패치 `impl-R8e/v2/p1-web-subst.patch`
    - 패치: scratch `impl-R8e/p1-web-subst.patch`(`git diff --binary <기준 트리> <2차 트리>`) · 1차 대비 증분 `impl-R8e/v1-to-v2.patch` · 1차 패치 `impl-R8e/v1/p1-web-subst.patch`
  - 이 기록 파일은 미추적이고 트리·패치에 없다(설계 §4 커밋 2 몫).
- 입력
  - 설계 정본: 메인 체크아웃 `design-R8e.md`(미추적). §2(판정식·코드·fail-closed·문면·처분) · §3 · §4 · §5 · §8 · §9 를 따랐다.
  - 설계 리뷰: scratch `review-R8e-tool/review-R8e-tool.md`(+ `fix3-subst.diff`) · `review-R8e-proc/review-R8e-proc.md`.
  - 구현 리뷰: scratch `review-R8e-impl-tool/review-R8e-impl-tool.md`(minor 3 · nit 3 · `fix-subst.diff` · `fixtures-add.sh`) · `review-R8e-impl-proc/review-R8e-impl-proc.md`(major 1 · minor 3 · nit 8).
  - 프로토타입: scratch `r8e/proto4`(설계 판). 도구 세 파일을 한 줄씩 읽고 설계 §2.1 식·§2.3 표·§2.4 표와 대조한 뒤 옮겼다. 1차 문면은 `r8e/apply_r8e.py` 를 워크트리에 그대로 돌려 넣고, ④ 원문·§2.7 표의 인용 구절 16개가 C·X 에 한 번씩 있는지 기계로 대조했다(`check_text.py`). 2차 문면은 `impl-R8e/apply_r8e_v2.py` 로 넣었다(자리마다 한 번만 맞는지 확인하고 C·X 같은 문장).
- Serena·Graphify 는 쓰지 않았다(지시). `/Users/hyun/Desktop/spring_dream_server` · herdr 워크트리 · `~/.codex` 는 읽지도 쓰지도 않았다. 현장 측정은 scratch `problem-lanes/field-clone` 을 `git clone --shared` 로 복제한 사본(`impl-R8e/syn` · `beh` · `p2restore`)과, 읽기만 하는 `field-p1end`·`field-p2end` 에서 했다.
- core 파일(`dddjango/`·`codex-dddjango/`·`ontology/`)은 건드리지 않았다. `.venv` 는 필요 없었다(`make verify-web` 은 `python3` 만 쓴다).
- scratch 루트: `/private/tmp/claude-501/-Users-hyun-Desktop-dddjango/ed01792c-e467-4a58-a794-ed16237ffb9e/scratchpad/impl-R8e/`
- 표기: **[실측]** = 이번에 돌려 확인함 · **[추정]** = 코드를 읽어 추론함.

## 0. 요약 (2차)

| 항목 | 결과 [실측] |
|---|---|
| `fixtures_subst` | **126 PASS**(Claude·Codex 둘 다 · FAIL 0). 설계 107 + 1차 구현 2(S17o · S14n″) + 구현 리뷰 도구 7(S18 6사례) + 문면·n1 몫 10(S18v×4 · S18c · S18a×2 · S18b×2 · S18n) |
| 기존 web 픽스처 | 16파일 실패 0 — refactor_audit 190 · debt 80 · backstop 62 · extract 31 · motion 25 · clip 24 · audit 22 · token 21 · focus 19 · ui_js 17 · contract 13 |
| 변이 | 45개를 돌려 **잡아야 할 42개를 모두 잡음** — 설계 V1~V30(V11 제외) · 1차 구현 V31·V32 · 구현 리뷰 R1~R5 · 2차 V33~V38. V11 은 2차 코드에서 살아남아 도달 불가를 확인하고 대상 코드를 지웠다(§2 D6). MN·MT 는 설계 결정대로 생존 |
| 두 레인 끝 | 실제 도구 exit 1(«slices[0] 기록 없음») · 측정 판 A·C 는 설계 §3.4 와 같다 · B·D 는 새 병합 줄·지침 파일 몫만 늘었다(§4) · p2 복원 커밋 → exit 0 |
| 현장 16사례 | 설계 §1.4 표 세 열과 **모두 같다** |
| `make verify-web` | exit 0 · PASS 줄 553 → **631** · Claude·Codex 문단 대조 6종 통과 |
| `claude plugin validate dddjango-web --strict` | 통과 |
| 문면 증가(HEAD 대비) | C · X 각 **+3,707B**(+2.20% · +2.12%) — 1차 +2,967 · 2차 +740 |
| 행동 시험 §3.5 | B1~B4 + **B1′**(처분 키 겹침) — 모두 문면 처분대로 풀림 · 잘못된 복원은 red 로 남음 |
| **봉인** | 설계 §4 «봉인 없음»은 틀렸다 — `Makefile` 이 `manifest_seal.py` `protocol` 글롭 안이다. 커밋 1 뒤 별 chore 봉인 재발행이 필요하다(§6) |

## 1. 바뀐 파일 (기준 트리 → 2차 트리)

| 파일 | 바이트 | +/− | 내용 |
|---|---|---|---|
| `dddjango-web/scripts/src/subst.py` | 19,057 → 43,051 | +404/−23 | 설계 §2.3(프로토 v4) + §2 의 차이(D1·D2 · 2차 D5~D8) |
| `dddjango-web/scripts/backstop.py` | 15,953 → 16,331 | +12/−8 | `--build` · 단독 모드 배타 · 사용 문구 · 머리 주석 |
| `dddjango-web/scripts/src/debt.py` | 25,766 → 25,836 | +2/−1 | `is_test_path` docstring 정정(«behavior_guard 와 같게» → «다르다» — 문면 리뷰 범위 밖 관찰 2) |
| `dddjango-web/scripts/test/fixtures_subst.sh` | 25,343 → 63,376 | +403/−0 | S15·S16·S17(설계 59) + S17o · S14n″ + S18(19단언) |
| `dddjango-web/commands/dddjango-web.md`(C) | 168,771 → 172,478 | +15/−15 | 설계 §2.7 15자리 + 2차 7자리(§9) |
| `codex-dddjango-web/skills/dddjango-web/SKILL.md`(X) | 175,235 → 178,942 | +15/−15 | C 와 같은 문장(플랫폼 토큰만 다름) |
| coder-web Claude · Codex | 20,668 → 21,096 · 20,822 → 21,250 | +2/−2 씩 | `:39` · `:76`(+ 2차 우선 관계 구절) |
| houserules `references/final.md` + Codex | 29,992 → 31,442 | +2/−2 씩 | `:200` 사용 줄 `[--build]` · `:208` 치환 확인 문단(+ 2차 mode·지침 파일·병합 유입·exit 1) |
| `REQUEST_GUIDE.md` + Codex | 21,807 → 22,558 | +7/−1 씩 | §4 · §7(2차 문구 정정) · §8 |
| `Makefile` | 28,674 → 28,797 | +1/−1 | Claude·Codex 문단 대조 3종(1차) + 1종(2차 n3) |
| Codex `scripts/` 네 파일 | 같음 | 같음 | byte 미러(`diff -rq` 무차이) |

- **크기 정정**: 1차 기록의 `subst.py` «19,057 → 40,737»은 틀렸다. 1차 트리의 실제 크기는 **40,875B** 다(`git cat-file -s` — 바이트를 잰 뒤 머리 주석 한 줄을 더했다. 문면 리뷰 지적).
- 바꾸지 않은 곳(설계 «바꾸지 않는 곳»): discipline-reviewer-web · architect 슬라이스 0 절 · README · AGENTS · 설계 v5.

## 2. 설계와 다른 점 (모두 도구 쪽 · 최소)

| # | 판 | 무엇 | 왜 | 시험 |
|---|---|---|---|---|
| D1 | 1차 | 사슬에 걸음이 없는 테스트 경로를 기준 판 대비로 대조 | 기준이 첫 부모 사슬 밖이면 기준 쪽에서만 바뀐 경로가 대조 없이 통과했다(HEAD 는 red). 2차 D5(m1) 뒤에는 `--build` 없는 판에서만 선다 | S17o · V31 |
| D2 | 1차 | 뿌리 커밋 표지 «(뿌리)» | «(미승인 병합)»이면 등재 요청 갈래로 잘못 읽힌다 | S14n″ · V32 |
| D3 | 1차 | `backstop.py` 머리 주석 한 낱말 | 리뷰 M2 뒤 사실과 다름 | 주석 |
| D4 | 1차 | 봉인 영향 정정 | `Makefile` 이 봉인 글롭 안(§6) | [실측] |
| D5 | 2차 | **미등재 병합 유입 표지**: `--build` 에서 승인 목록 밖 병합이 바꾼 비테스트 줄을 «`<경로>` 승인 목록 밖 병합 유입(<상태>) — 레인 커밋 … — 등재 먼저(복원하지 않는다)»로 낸다(«테스트 밖 web/ 밖 파일 변경» 줄이 아니다). 병합마다 «병합 `<SHA>`(미승인 병합) 승인 목록 밖 병합이 비테스트 n경로를 들였다(…) — 등재 먼저 · 되돌려도 이 줄은 남는다» 한 줄을 더한다 | 문면 리뷰 major 1 + 운영 지시(«도구 출력에서도 두 키가 헷갈리지 않게 · 복원 처분을 따르면 exit 0 이 나지 않게»). 문면 권고만으로는 복원을 막지 못하고, 복원하면 줄이 사라져 exit 0 이 되기 때문이다(리뷰 X2r 재현). 병합 줄은 경로를 되돌려도 남아서 등재 전에는 green 이 서지 않는다. 등재 뒤에는 복원 커밋이 상류 판 대비 어긋남으로 잡히고, 상류 판 복원으로 풀린다 | S18v·v′·v″·v‴ · V36 · V37 · 1차 도구에서 S18v′ exit 0 [실측 `fx-on-v1tool.log`] |
| D6 | 2차 | `_approved_merges` 의 «기준이 사슬 위» 확인과 `target` 인자 삭제 | 도구 m1 확인(호출 쪽 · `--build` 전부)이 먼저 선다. 사슬이 비면 `_records` 가 먼저 exit 1 이다. 그래서 도달 불가였다(변이 V11 생존으로 확인). 리뷰는 «둬도 된다»였지만, 죽은 코드와 대상 첫 부모 전체 `rev-list` 를 걷었다 | V33 → S16d·S18o |
| D7 | 2차 | n1 의 «뿌리·접목 기록 — 버림» 분기는 넣지 않았다 | m1 뒤에는 `--build` 사슬에 부모 없는 커밋이 올 수 없다(뿌리는 사슬 맨 앞뿐이고 m1 이 막는다). `merges` 정의만 `>= 2` 로 고쳤다 | — |
| D8 | 2차 | 행동·픽스처 보강: S18n(버린 기록 사유가 exit 1 에 실림 — n1) · S18a(`(A)` 는 `git rm` 복원 — minor 3) · S18b(병합 안 되돌림 기록 자리 — minor 2) | 문면이 새로 약속한 처분이 도구와 맞물리는지 고정 | V38 → S18n |

- 픽스처 수: 설계 107 → 126. 기존 48 과 설계 59 의 기대는 바꾸지 않았다.
- 도구 동작 차이는 D1·D5(fail-closed 쪽)와 D2(표지 문자열)뿐이다. 설계 §3.4 등재·기록 판 · 현장 16사례의 exit 는 설계 표와 같다.

## 3. 시험 [실측]

### 3.1 픽스처

- `fixtures_subst.sh`: Claude **126 PASS** · Codex **126 PASS**(`fx-claude.log` · `fx-codex.log`).
- 새 픽스처를 1차 도구(`v1/scripts` — 1차 트리 `git archive`)로 돌리면 **5 FAIL**: S18o(exit 0) · S18r(0) · S18v(표지) · S18v′(**exit 0** — 리뷰 X2r) · S18c(0)(`fx-on-v1tool.log`). 나머지 S18 은 1차에서도 PASS(코드는 옳았고 시험 공백이었다).
- `make verify-web` exit 0(`verify-web.log`): 픽스처 16파일 실패 0 · refactor_audit self-test 두 런타임 · 적용 범위·상시 답 대조 · 문단 대조 6종(1차 3종 추가 + 2차 `그 커밋을 만든 파견 슬라이스의`) · byte 미러(scripts·assets·references 3종·REQUEST_GUIDE) · 요청 가이드 계약 PASS · PASS 줄 631.
- `claude plugin validate dddjango-web --strict`: «✔ Validation passed».

### 3.2 변이 — `mutate2.sh` · `mutation.txt`(사본마다 `fixtures_subst.sh` 전체 · 4개씩 병렬) · D6 뒤 V1·V33 재실행 `mutate3.sh` · `mutation-rerun.txt`

| 변이 | 떨어진 사례 |
|---|---|
| V1 승인 목록 무시 | 35(D6 뒤 재실행 같은 수) |
| V2 목록 밖 병합도 상류로 | 6(S14l·m · S15i·p · S17j · S18v) |
| V3 기능 기록 무시 | 8 |
| V4 모든 비병합 커밋을 기능으로 | 99 |
| V5 · V6 · V7 | 3 · 1(S16k) · 1(S15g) |
| V8 병합 안 몫 늘 목록(M1) | 13 |
| V9 · V10 · V12 · V13 | 2 · 2 · 2 · 1 |
| V11 기준 사슬 확인 제거 | 2차 코드에서 생존 → 도달 불가 확인 → 대상 코드 삭제(D6) |
| V14 비테스트 기준을 늘 `git_snapshot` | 12 |
| V15 · V16(M2) · V17 · V18 · V19 | 2 · 4 · 1 · 1 · 4 |
| V20 MJ · V21 MF · V22 MW · V23 · V24 | 각 1 |
| V25 · V26 · V27 · V28 · V29 · V30 | 2 · 1 · 3 · 3 · 2 · 2 |
| V31(D1) · V32(D2) | 1(S17o) · 1(S14n″) |
| **R1 겹침 재분류를 비상류에도** | 1(S18d) |
| **R2 문서 자리를 한 단 폴더로** | 1(S18m) |
| **R3 최상위 `docs/` 조건 누락** | 2(S18m · S18m′) |
| **R4 비테스트를 blob 만 비교** | 1(S18x) |
| **R5 앞선 아무 걸음이나 기능으로** | 1(S18u) |
| **V33 `--build` 기준 사슬 확인 제거(m1)** | 2(S16d · S18o — D6 뒤) |
| **V34 refactor mode 무시(m2)** | 1(S18r) |
| **V35 루트 지침 파일 제외(n2)** | 1(S18c) |
| **V36 병합 유입 줄 표지 제거(문면 major)** | 1(S18v) |
| **V37 병합 줄 제거(문면 major)** | 1(S18v′) |
| **V38 exit 1 버림 사유 제거(n1)** | 1(S18n) |
| MN `slice-0*` 이름 규칙 제거 · MT 태그 제외 제거 | 0 · 0 — 생존(설계 §3.3 «중복 안전망이라 싣지 않았다») |

## 4. 현장 [실측]

### 4.1 두 레인 끝 — `lanes.sh` · `lanes.txt` · `lanes/*.out|.time`

재료는 설계 판 `r8e/lanes/p{1,2}-{A,B,C,D}` 를 읽기만 했다. 측정 판은 2차 트리 사본에서 `slices[0]` 기록 요구만 끈 것이다(`lanemeas/`).

| 판 | p1 6-3-11 exit · 어긋남(파일) · 유입 제외 · 목록 · 문서 | p2 8-B-3 |
|---|---|---|
| 실제 도구 | 1 · «slices[0] 에 … 슬라이스 0 커밋 기록이 없다» | 1 · 같음 |
| A 등재·기록 | 2 · **1**(1) · 272 · 9 · 1 · 3.7초 | 2 · **1**(1) · 9,132 · 11 · 1 · 2.5초 |
| B 미등재·기록 | 2 · 255(239) · 0 · 9 · 36 | 2 · 9,079(9,031) · 0 · 11 · 104 |
| C 등재·미기록 | 2 · 17(10) · 272 · 0 · 1 | 2 · 20(12) · 9,132 · 0 · 1 |
| D 미등재·미기록 | 2 · 270(247) · 0 · 0 · 36 | 2 · 9,097(9,041) · 0 · 0 · 104 |

- A·C 는 설계 §3.4 와 칸마다 같다. A 에 남는 1 은 두 레인 모두 `rag/service/sources/ui/snapshot.py` 다.
- B·D 가 설계와 다른 몫은 2차 변경 둘뿐이다.
  - 미등재 병합 줄: p1 +1 · p2 +2.
  - 루트 `AGENTS.md`(p1) · `AGENTS.md`·`CLAUDE.md`(p2)가 문서 제외에서 빠져 어긋남으로 옮겼다(n2).
  - 미등재 판에서 «테스트 밖 web/ 밖 파일 변경» 줄은 **0** 이다. 병합이 들인 비테스트는 모두 «승인 목록 밖 병합 유입» 줄이다(p1 196 · p2 8,937).
- p2 복원(§2.6 처분): `--shared` 복제에서 `git revert 9f47a77d0` 는 exit 1(충돌). `git checkout cc504cfb9a03 -- rag/service/sources/ui/snapshot.py` 복원 커밋 뒤 측정 판 **exit 0**(유입 제외 9,133 · 목록 11).
- HEAD 도구(참고): p1 exit 2 · 305(283) · p2 exit 2 · 9,199(9,145).

### 4.2 현장 사본 16사례 — `scenarios.sh` · `scenarios.txt` · `scen/`

s0·c·d2 = 0/0/0 · a = 2/**0**/0 · b·e = 2/**0**/2 · d·g2·l = 2/**0**/2 · g·i = 2/**0**/2 · f·h·j·k = 2/2/2 · fR = 2/**2**. 설계 §1.4 표와 칸마다 같다(1차와도 같다).

## 5. 행동 시험 (§3.5 · 모델 호출 없는 책상 재생) — `behavior.sh` · `behavior.txt` · `beh-*.out` · `b4.sh` · `b4.txt`

현장 사본의 `--shared` 복제(`beh`)에서 p1 `git_snapshot` `14873bc14` + 합성 슬라이스 0 `c3cae076d` 위에 Coordinator 절차를 따라 쌓았다. 산출물 폴더는 실제 자리(`.dddjango-web/2026-09-30-beh/` · 미커밋)다. build-state 기록은 «커밋 지점»(C:212) 규칙대로 커밋마다 그 파견 슬라이스의 `commits` 에 적었다. ④ 는 문면 원문 명령으로 돌렸다. 처분 구절은 스크립트가 C 의 ④ 문단에서 표지로 찾아 인용한다(2차 문면).

| 시점·시험 | 입력 | ④ | 처분(문면 인용) → 결과 |
|---|---|---|---|
| **시점 1** 슬라이스 0 끝 | `slices[0]=[S0]` | exit 0 | — |
| **시점 2** 끝 green 뒤 재확인 | 감사 반영이 슬라이스 0 을 다시 엶(명세 치환 테스트에 단언 편집 · `slices[0]` 기록) | exit 2 · «(slices[0])» 2 · 목록 1 | «`(slices[0])` 만 → 슬라이스 0 반송» → 되돌림(`slices[0]`) → **exit 0** |
| **시점 3** G2 직전 | 발주 문서 · main 받기(미등재) · G2 반송 재작업(기록 누락) | exit 2 · «(미승인 병합)» 255 · «(기록 없음)» 1 | — |
| **B2** | 위 | — | «`(기록 없음)` → … `commits` 에 적고 다시(슬라이스 0 파견 커밋은 기능으로 적지 않는다)» → slice-1 기록 → «(기록 없음)» 0 |
| **B1′**(2차 · 문면 major 1) | 위 | «테스트 밖 web/ 밖 파일 변경» 줄 가운데 «(미승인 병합)» 이 붙은 줄 **0** · 병합 유입 줄 196 · 병합 줄 1 | 문면 «`(미승인 병합)` 이 먼저다 … 이 표지가 붙은 줄은 어떤 줄이든 복원하지 않는다». 잘못된 길을 모의로 밟아(`AGENTS.md` 를 `git_snapshot` 판으로 복원 커밋) 돌리면 그 경로 줄은 사라지지만 병합 줄이 남아 **exit 2** 다. 모의 커밋은 되돌렸다 |
| **B1** | 위 | — | «`(미승인 병합)` 인 main 받기 → … 적어 달라 하고 멈춤» → 절대 경로·SHA·^2 조건(^2 를 담은 ref `origin/main`)을 담은 요청 → 모의 등재 → **exit 0**(유입 274 · 문서 제외 1 · 목록 1) |
| **B3** 사례 j | 기능 슬라이스가 백엔드 `rag/…/snapshot.py` 편집(기록) | exit 2 · «(slice-1-screen) · 기준 = 상류 판 0b7c21ab43b3» | «`테스트 밖 web/ 밖 파일 변경`(`(미승인 병합)` 이 없는 줄 …) → … `git checkout <판> -- <경로>`(판에 없는 `(A)` 경로면 `git rm -- <경로>`) 해 네가 커밋한다 …» → 복원 커밋 → **exit 0** |
| **B4** 슬라이스 0 없는 레인(p1 끝) | — | 문면상 돌지 않는다 · 어기고 돌리면 exit 1 | 배너 행 «(슬라이스 0 이 있으면 ④ 목록 · 없으면 coder-web 보고를 모은다)» + coder-web 새 문장 → 보고 모의로 행 9파일 — 측정 판 A 목록 9 와 같다 |

G2 배너 두 행(최종 출력으로 채움):
- `web/ 밖 치환(14873bc14357..07d155b71ac4): 파일 1 · 승인 병합 유입 제외 274 · 문서 제외 1(docs/superpowers/orders/lane/GATE-web-beh.md) · 제외(배선 적용) 0 · --subst-check exit 0`
- `web/ 밖 테스트 편집 1: tests/web/chart/chart/test_chart_view.py(M) — 커밋 a060e43336a7(slice-1-screen) b3791b0ea1cf(slice-1-screen) — <coder-web 보고 이유>`

한계: 책상 재생은 문면 처분이 도구 표지와 맞물리는지를 본다. 실제 Coordinator(모델)가 커밋 지점마다 `commits` 를 적는지, 등재 요청에서 멈추는지는 현장 레인에서 처음 확인된다.

## 6. 봉인·릴리즈

- **봉인 영향 [실측 `seal_probe.py`]**: `workspace/eval/ab/T2-0b-manifest.json` 의 `protocol` 그룹이 `Makefile` 을 봉인한다. 봉인값 `0b7df0ce62ab…` 는 HEAD `Makefile` 과 같고, 2차 트리 `Makefile` 은 `89f2b9ef4e4d…` 다. 커밋 1 뒤 별 chore 커밋으로 `python3 workspace/tools/manifest_seal.py --write` 봉인 재발행이 필요하다(8b `0981fd85` → `03907b6f` 선례 · 같은 커밋에 넣으면 strict `--check` RED). 구현 리뷰 도구가 복제본에서 두 커밋 순서로 재현해 `make verify` 5묶음 green 을 확인했다. 바뀐 파일 가운데 봉인 글롭에 든 것은 `Makefile` 하나다(web 파일은 글롭 밖).
- 봉인 파일은 쓰지 않았다(커밋 금지 · 봉인은 커밋 뒤 순서).
- 릴리즈는 `make release-web`(8b~8e 배포 창) — 설계 §4 그대로.
- 메인 작업 트리의 미커밋 파일과 이 17파일은 겹치지 않는다.

## 7. 남은 위험

1. **봉인 재발행 누락** — §6. 커밋 1 만 넣고 봉인을 빠뜨리면 `make verify` 봉인 대조가 RED 다.
2. **기능 기록 자기 보증**(설계 §5-7) — 슬라이스 0 커밋을 `slices[0]` 에 빠뜨리고 기능에만 적으면 그 테스트 편집이 목록으로 샌다. 리팩토링 입구는 2차에서 닫았다(`mode: refactor` 면 모든 기록이 슬라이스 0).
3. **MN·MT 생존** — `slice-0*` 이름 규칙과 태그 제외는 시험이 없다(설계 결정).
4. **진행 중 폴더** — `commits`·`approved-merges.txt` 가 없는 폴더는 첫 ④ 에서 exit 1 또는 «(기록 없음)»으로 멈춘다. 설계 §4 대로 한 번 채우면 풀린다. exit 1 은 이제 버린 기록의 사유를 함께 싣는다(n1).
5. **미등재 병합 줄의 폭**(D5) — `--build` 에서 승인 목록 밖 병합이 비테스트를 들이면, 그 경로를 나중에 되돌려도 병합 줄이 남는다. 레인 곁가지 병합(등재 대상 아님)이 비테스트를 바꿨다 되돌린 경우도 red 다. 이것은 «풀리지 않는 어긋남 → 사용자에게 묻는다» 갈래로 간다(설계 사례 h 와 같은 처분). 두 레인 끝·현장 16사례의 등재 판 결과는 바뀌지 않았다.
6. **슬라이스 0 없는 레인에서 ④ 를 잘못 돌리면** `slices[0]` 이 기능 슬라이스라 그 기록이 슬라이스 0 으로 대조된다(fail-closed). 문면은 슬라이스 0 이 있을 때만 ④ 를 부른다.
7. **설계 §5 범위 밖** 그대로 — 백스톱 `--diff-base` 상류 web/ 혼입 · ⑤ 기준선과 상류 병합 · 테스트가 읽는 문서 자리 `.md` · 겹침 테스트의 상류 개명 거짓 red(«플러그인 결함» STOP 이 받는다). 문면 리뷰 범위 밖 관찰 1(배너 HEAD 규칙과 ⑤ 제한 문장 — 8e 이전 문면)도 그대로다.
8. 행동 시험은 책상 재생이다(§5 한계).

## 8. 산출물 (scratch `impl-R8e/`)

- 패치 `p1-web-subst.patch`(2차) · `v1-to-v2.patch` · 1차 `v1/p1-web-subst.patch` · 문면 적용 `apply-text.txt`(1차) · `apply_r8e_v2.py` · `apply-text-v2.txt` · 바이트 `bytes.txt`
- 픽스처 `fx-claude.log` · `fx-codex.log` · 1차 도구 대조 `fx-on-v1tool.log` · 추가 사례 `s18-own.sh` · `insert_s18.py`
- 변이 `mutate2.sh` · `mutation.txt` · `mutate3.sh` · `mutation-rerun.txt` · 사본 `mut2/` · `mut3/`(1차 `mutate.sh` · `v1/mutation.txt`)
- 현장 `lanes.sh` · `lanes.txt` · `lanes/` · `lanemeas/` · `p2restore/` · `scenarios.sh` · `scenarios.txt` · `scen/` · `syn/`
- 행동 시험 `behavior.sh` · `behavior.txt` · `beh-*.out` · `beh/` · `b4.sh` · `b4.txt`
- verify `verify-web.log` · 봉인 탐침 `seal_probe.py`
- 1차 로그 `v1/`(verify · 레인 · 사례 · 행동 · 기록)
- 이 기록의 사본 `repair-R8e-impl.md`

## 9. 구현 리뷰 처분 (09-30 · 운영 세션 · 전건 채택)

| 리뷰 | 항목 | 등급 | 처분 | 반영 |
|---|---|---|---|---|
| 문면 | 1 ④ 처분 키 겹침(커밋 표지 ↔ «테스트 밖» 줄) — 미등재 main 받기 비테스트를 복원하면 main 변경을 되돌린 채 green | major | **채택 + 도구 표지(D5)** — C·X ④: «`(미승인 병합)` 이 먼저다 … 이 표지가 붙은 줄은 어떤 줄이든 복원하지 않는다» · «`테스트 밖 web/ 밖 파일 변경`(`(미승인 병합)` 이 없는 줄 — 다른 표지와 무관)». 도구: 병합 유입 줄은 «테스트 밖» 문자열을 쓰지 않고, 병합 줄이 되돌림 뒤에도 남는다 | S18v~v‴ · V36·V37 · 행동 B1′ · 1차 도구 S18v′ exit 0 재현 |
| 문면 | 2 `(승인 병합 안)` 되돌림 커밋의 주체·기록 자리 | minor | **채택** — «`(승인 병합 안)` 테스트 줄 → 슬라이스 0 반송으로 되돌린 커밋(`slices[0]` 기록 — 기능 기록이면 구간이 닫히지 않는다) 뒤 필요하면 기능 슬라이스 커밋으로» | S18b · S18b′ |
| 문면 | 3 `(A)` 줄 복원 명령 | minor | **채택** — «`git checkout <판> -- <경로>`(판에 없는 `(A)` 경로면 `git rm -- <경로>`)». 선택 권고(비 `.md` 발주 문서는 묻기)는 넣지 않았다 | S18a · S18a′ |
| 문면 | 4 coder-web `:67` ↔ `:76` 우선 관계 | minor | **채택** — «기능 슬라이스에서는(이번 슬라이스 파일 목록 밖이어도) …»(두 런타임) | 문면 |
| 문면 | nit 1 수정 모드 재진술 | nit | 채택 — «커밋마다 `last_commit` 과 그 파견 슬라이스의 `commits` 를 갱신하며» | C:246 · X:269 |
| 문면 | nit 2 배너 확인 HEAD 지시 대상 | nit | 채택 — «기존 테스트·치환 두 행의 확인 HEAD» | C:222 · X:245 |
| 문면 | nit 3 알림 대상 | nit | 채택 — «알림 <역방향/합성 의심 · 기록 거부·버림 · 기준 이전 불참 줄>» | C:222 · X:245 |
| 문면 | nit 4 REQUEST_GUIDE §7 약속 범위·폴더 이름 | nit | 채택 — «작업 폴더(`.dddjango-web/<날짜시각>-<화면>/`)» · «기존 코드 정리를 먼저 하는 작업은 적히지 않은 병합이 있으면 멈춰 경로를 알립니다» | 두 판 byte 같음 · 요청 가이드 계약 PASS |
| 문면 | nit 5 «플러그인 결함» 답의 자리 | nit | 채택 — «답은 `refactor-scope.md` `## ⓐ 재상정 <시각>` 절 — 항목은 ④ 줄 원문 · `재상정 키: -`»(`-` 는 러너가 받는 값 — C:156 · 상시 답 선례) | C:214 · X:237 |
| 문면 | nit 6 exit 1 부류 | nit | 채택 — «얕은 이력·기준이 첫 부모 사슬 밖(rebase)은 사용자에게 알리고 멈춘다» | C:214 · X:237 |
| 문면 | nit 7 괄호 연속 | nit | 채택 — 한 괄호로 | C:304 · X:329 |
| 문면 | nit 8 옛 커밋 가림 | nit | 채택 — `(기록 없음)` 처분 끝 «(슬라이스 0 파견 커밋은 기능으로 적지 않는다)» | C:214 · X:237 |
| 문면 | 범위 밖 관찰 2 `is_test_path` docstring | — | 정정(주석 한 줄 · byte 미러) | `debt.py` |
| 문면 | 사실 오류 — `subst.py` 크기 | — | 정정 — 1차 트리 40,875B(§1) | 이 기록 |
| 도구 | m1 `--build` 인데 기준이 첫 부모 사슬 밖 · 첫 걸음이 기능 → 목록 흡수 | minor | **채택**(권고 2줄) — `--build` 면 `chain[0]` 의 첫 부모가 기준이어야 한다. 덧붙여 도달 불가가 된 `_approved_merges` 확인을 걷었다(D6) | S18o · V33 |
| 도구 | m2 리팩토링 입구 `mode: refactor` 미확인 | minor | **채택**(권고 3줄) — 모든 기록을 슬라이스 0 으로 · 알림 | S18r · V34 · houserules |
| 도구 | m3 생존 변이 R1~R5 | minor | **채택** — `fixtures-add.sh` S18 6사례·7단언을 그대로 넣었다 | R1~R5 모두 잡힘 |
| 도구 | n1 exit 1 이 버린 기록 사유를 숨김 · 부모 없는 커밋을 병합이라 부름 | nit | 채택 — exit 1 메시지에 알림을 싣는다 · `merges` = 부모 2 이상. 뿌리·접목 분기는 m1 뒤 도달 불가라 넣지 않았다(D7) | S18n · V38 |
| 도구 | n2 루트 `CLAUDE.md`·`AGENTS.md` | nit | 채택 — 문서 자리에서 뺀다 | S18c · V35 · 현장 B·D 판 수치 |
| 도구 | n3 Makefile 문단 대조 범위 | nit | 채택 — `'그 커밋을 만든 파견 슬라이스의'` 추가(C·X 두 줄씩 토큰 치환 뒤 같음 — verify-web PASS) | Makefile +46B |

## 10. 재검토 처분 (09-30 · 판정 «승인» · 남은 지적을 커밋 전에 닫음 — 3차)

재검토 원문: scratch `rereview-R8e/rereview-R8e.md`(minor 1 · nit 3 · 회귀 0).

| 항목 | 등급 | 처분 | 반영 | 시험 [실측] |
|---|---|---|---|---|
| 테스트만 들인 미등재 main 받기를 문면을 어겨 되돌리면 exit 0(X2t) | minor | **채택** — 병합 줄의 `brought` 에서 `not is_test_path(p) and` 를 지웠다(문서 자리만 뺀다). 문구 «비테스트 n경로» → «n경로». 머리·코드 주석과 houserules §7 문장을 같게 고쳤다 | `subst.py` · houserules(byte 미러) | **S18t**: 2차 도구 **exit 0** → 3차 **exit 2**(병합 줄)(`fx-on-v2tool.log`) · 변이 V50(조건 복원) → S18t |
| 생존 변이 V44 · V47 · V48 | nit | **채택** — 등가 변이가 아니라 시험 공백이었다. 셋 다 잡는 단언을 더했다 | `fixtures_subst.sh` | V44 → **S18c′**(루트 `AGENTS.md` = red) · V47 → **S18w**(미등재 병합 유입 경로를 레인 기능 커밋도 고침 → 두 표지를 단 유입 줄 · «테스트 밖» 줄 아님) · V48 → **S18r′**(`mode=refactor` 재분류 알림) |
| G2 배너 알림 목록에 재분류 알림이 없음 | nit | **채택** — «알림 <역방향/합성 의심 · 기록 거부·버림·재분류 · 기준 이전 불참 줄>» | C:222 · X:245 (+11B 씩) | 문면(verify-web 문단 대조 6종 통과) |
| 루트 지침 이름 대조가 대소문자를 가림 | nit | **채택** — `path.upper() not in ('CLAUDE.MD', 'AGENTS.MD')` · docstring·houserules «대소문자와 무관하게» | `subst.py` · houserules | **S18c″**(루트 `claude.md` = red) · 변이 V49(대소문자 구분) → S18c′·S18c″ |

### 10.1 3차 수치 [실측]

- `fixtures_subst`: Claude **131 PASS** · Codex **131 PASS**(2차 126 + S18t · S18w · S18r′ · S18c′ · S18c″). 새 픽스처를 2차 도구로 돌리면 4 FAIL: S18t(**exit 0**) · S18c′·S18c″(대소문자·문서 제외) · S18v′(문구 «비테스트» 변경 몫)(`fx-on-v2tool.log`).
- 기존 web 픽스처 16파일 실패 0(refactor_audit 190 등).
- 변이(`mutate4.sh` · `mutation.txt` · 사본 `mut4/`): **51개 가운데 잡아야 할 49개를 모두 잡음** — 설계 V1~V30(V11 제외 — 2차에서 대상 코드 삭제) · V31~V38 · 구현 리뷰 R1~R5 · 재검토 V39·V41·V44·V47·V48 · 3차 V49·V50. MN·MT 는 설계 결정대로 생존.
- 두 레인 끝(`lanes.txt`): 모든 칸이 2차와 같다(실제 도구 exit 1 · A 1/272/9/1 · 1/9,132/11/1 · p2 복원 exit 0). B·D 의 병합 줄은 두 레인 병합이 이미 비테스트를 들였으므로 수가 같다.
- 현장 16사례(`scenarios.txt`): exit 세 열이 설계 §1.4 · 2차와 같다. 등재·기록 판 사례 h(레인 곁가지 `--no-ff` · 테스트만)는 어긋남 1 → 2(병합 줄) — exit 무변.
- 행동 재생(`behavior.txt` · `b4.txt`): 2차와 같은 결과(B1′ «테스트 밖» 줄 가운데 «(미승인 병합)» 0 · 잘못된 복원 → exit 2 · 등재 → exit 0 · B3 복원 → exit 0 · B4 행 9).
- `make verify-web` exit 0 · PASS 줄 **636** · `claude plugin validate dddjango-web --strict` 통과.
- 문면 증가(HEAD 대비): C · X 각 **+3,718B**(+2.20% · +2.12%) · houserules +1,497 · `subst.py` 19,057 → 43,036B · `fixtures_subst.sh` 25,343 → 65,339B.
- 봉인: 변동 없음 — `Makefile` 은 2차와 같고(`89f2b9ef4e4d…`), 커밋 1 뒤 별 chore 봉인 재발행이 필요하다(§6).

### 10.2 남은 위험 갱신

- §7-5 의 폭이 넓어졌다: 이제 `--build` 에서 승인 목록 밖 병합이 **문서 자리 밖 경로를 하나라도** 들이면(테스트만이어도) 병합 줄이 남는다. 레인 곁가지 병합(등재 대상 아님)이 슬라이스 0 치환만 담았어도 red 이고, «풀리지 않는 어긋남 → 사용자에게 묻는다» 갈래로 간다(사례 h 어긋남 1 → 2). 등재 판·두 레인 끝의 exit 는 바뀌지 않았다.
- 그 밖(§7-1~4 · 6~8)은 그대로다.

### 10.3 산출물 (3차)

- 적용 `apply_v3.py` · `apply-text-v3.txt` · 변이 `mk_mutate4.py` · `mutate4.sh` · `mutation.txt` · 2차 도구 대조 `fx-on-v2tool.log`(2차 도구 사본 `v2/scripts/`) · 이 기록 갱신 `record_v3.py`
- 2차 산출물 `v2/`(패치 · 기록 · 변이 · 픽스처 · verify · 레인 · 사례 · 행동)
