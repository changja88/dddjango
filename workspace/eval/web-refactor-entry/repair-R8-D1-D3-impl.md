# 구현 기록 — R8-D1 · R8-D3 수리 (dddjango-web · 2026-09-28~29)

- 정본 명세: `workspace/plan/2026-09-26-refactor-path-repair/diag-R8-D1-D3-web.md`(주 체크아웃 · 미커밋)
- 권고안대로 구현했다: **D1 = (c) 커밋별 개명 사슬**, **D3 = (A) Coordinator 갈래 추가(스크립트 무변)**.
- 독립 검토 두 차례를 반영했다. 처분은 §7 에 있다.
  - 구현 리뷰(scratch `review-D1/review-web-repair.md` · «수정 후 승인» · major 1 · minor 6)
  - 재검토(`review-D1/rereview-web-repair.md` · «승인» · minor 4)
- 판 이름: V1 = 리뷰 전 수리본, V2 = 리뷰 반영본, V3 = 재검토 반영본(최종).
- 작업 위치는 격리 worktree `.claude/worktrees/agent-abf314ccc4aba3b2c` 다. 커밋·push 하지 않았다(미커밋 diff).
- Serena·Graphify 는 쓰지 않았다(지시).

## 0. 작업 전 정렬

- worktree 는 `acbfffda`(main 보다 10 커밋 뒤)에서 시작해 `subst.py` 가 없었다.
- `git merge --ff-only main` 으로 `1d712d87`(main 과 같은 커밋)까지 앞당겼다. 새 커밋은 만들지 않았다.
- 주 체크아웃의 미커밋 변경은 docs·workspace 뿐이고, 플러그인 파일은 main HEAD 와 같다. 그래서 이 diff 는 주 작업 트리에 그대로 옮겨진다.

## 1. D1 — `--subst-check` 개명 쌍 소실

### 변경

`dddjango-web/scripts/src/subst.py`:
- **`_renames` → `_web_changes`.** 반환을 `(개명 쌍, 새로 생긴 web/ 경로)` 로 넓혔다.
  - 새로 생긴 경로는 `A` 상태다. web/ 밖에서 들어온 것도 여기에 든다.
  - 누적 쌍은 `[0]` 만 쓴다. 누적 계산은 무변이다.
- **`_history_renames` 신설.** 쌍은 누적 `git diff -M` 1회에 커밋별 개명 사슬을 합친 것이다.
  - `rev-list --reverse --first-parent --parents base..target` 의 커밋마다 `git diff -M <첫 부모> <커밋>` 을 돈다. **뿌리 커밋은 빈 트리(`git hash-object -t tree /dev/null`)를 부모로 삼는다**(재검토 n-1).
  - 개명은 `origin[new] = origin.pop(old, old)` 로 사슬 합성한다.
  - 새로 생긴 경로는 `origin[path] = None` 으로 계보를 끊는다(리뷰 m-1). 뿌리 커밋이 들인 경로도 여기에 든다.
  - 합성 쌍은 누적 R 과 같은 트리 조건을 채울 때만 더한다. 조건은 옛 ∈ 기준 · 옛 ∉ 대상 · 새 ∉ 기준 · 새 ∈ 대상이다. 누적 쌍이 우선한다(`setdefault`).
- **`build_pairs`.** `_tree_files` 를 한 번만 구해 넘긴다. 폴더 쌍 규칙(X2 M3)은 무변이다.
- **머리 주석.** 다음을 적었다.
  - 쌍 출처와 사슬 쌍의 트리 조건
  - A 경로(뿌리 포함)의 계보 끊기
  - **fail-closed 한계 셋** — 쌍이 없는 경우들이다.
    1. 곁가지 안에서 개명과 대폭 교체를 함께 한 뒤 머지
    2. 한 커밋 안에서 개명과 대폭 교정을 함께 함
    3. 개명된 경로를 한 커밋이 지우고 뒤 커밋이 다시 만듦(재검토 n-2)
- CLI·출력 문면·Coordinator ④ 문면·houserules §7 은 무변이다.

`dddjango-web/scripts/test/fixtures_subst.sh`: S14 를 16건 더했다(32 → **48**). 초안은 scratch `diag-D1/proposed_s14.sh` 와 리뷰 `edge.sh`·`edge3.sh` 다.

| 사례 | 내용 | 기대 | 유일하게 지키는 것 |
|---|---|---|---|
| S14a | 이미지 개명(R100) → 다른 커밋이 같은 경로 바이트 교체(D1 본형) | green | 수리 자체 |
| S14b | `.py` 모듈 개명 → 다른 커밋이 본문 재작성 | green | 수리 자체 |
| S14c | 사슬 old→mid→last + 교체 · 테스트 old→last | green | 사슬 합성(M5) |
| S14d | 대조: 사슬 중간 이름으로 치환 | red | — |
| S14e | 대조: 개명 뒤 옛 경로가 대상에 되살아남 | red | `옛 ∉ 대상`(M2) |
| S14f | 대조: 커밋에 걸친 경로 맞바꿈 | red | — |
| S14g | 대조(E4 선형 · 사례 전용 기준): 구간에서 만든 ghost.png → ghost_2 · 기준 web/ 에 ghost 없음 | red | A 끊기와 `옛 ∈ 기준` 이중 보호 |
| S14h | 대조(X2 M3 커밋 분리판): 폴더 거짓 쌍 없음 | red | 폴더 규칙(M9) |
| S14i | 대조(E1): old→keep 뒤 빈 old 자리에 새 파일 → r · 테스트 old→r | red | A 끊기(MA) |
| S14j | 대조(E2): 개명 뒤 삭제 | red | `새 ∈ 대상`(M3) |
| S14k | 대조(E3): other 삭제 뒤 old→other | red | `새 ∉ 기준`(M4) |
| S14l | 곁가지 개명 → `--no-ff` 머지 → 본선 교체 | green | 머지 첫 부모 diff |
| S14m | 곁가지 안 개명+교체 → 머지(E5) | red | fail-closed 한계 기록(S5b 판례) |
| S14n | 대조(무관 이력): 뿌리 파일 ghost(기준에 없음) → ghost_2 | red(실행 불능 아님) | 뿌리 부모 처리(MR) |
| S14n′ | 대조(L9): 무관 이력의 뿌리가 기준과 같은 경로 old.png 를 다른 내용으로 들인 뒤 old → x | red | 뿌리 경로의 A 끊기(MS · 재검토 n-1) |
| S14o | 대조: 기준이 대상의 첫 부모 줄기 밖(곁가지 커밋 · `-s ours` 머지) · 기준에서 지운 경로 other → other_2 | red | `옛 ∈ 기준`(M1) |

- Codex byte 미러는 `codex-dddjango-web/skills/dddjango-web/scripts/src/subst.py` · `…/scripts/test/fixtures_subst.sh` 다. `diff -rq` 차이가 없다.

### 전·후 [실측]

| 확인 | HEAD(수리 전) | V1 | V2 | **V3(최종)** |
|---|---|---|---|---|
| `fixtures_subst.sh` 48건 | 44 — S14a·b·c·l red | 46 — S14i·S14n′ 거짓 green | 47 — S14n′ 거짓 green | **48/48** |
| `diag-D1/repro_d1.sh` [2](리허설 실바이트) | 쌍 0 · exit 2 | 쌍 1 · exit 0 | 쌍 1 · exit 0 | **쌍 1 · exit 0** |
| `diag-D1/proposed_s14.sh` 8건 | 5/8 | 8/8 | 8/8 | **8/8** |
| 변종 V1 · V2 · V3(진단) | 2 · 쌍 4 · 2 | 0 · 쌍 7 · 2 | 0 · 쌍 7 · 2 | **0 · 쌍 7 · 2**(V3 = 한계) |

리뷰 `edge2.sh`(E1~E12 · L1~L8)와 `edge3.sh`(L9)를 사본 `r8-d1d3-impl/edge2_review.sh`·`edge3_review.sh` 로 돌렸다. exit 뒤 괄호는 쌍 수다.

| 사례 | HEAD | V1 | V2 | V3 |
|---|---|---|---|---|
| E1 거짓 계보 | 2(1) | 0(2) | 2(1) | **2(1)** |
| E1b · L2 삭제 커밋 → 재생성 커밋 | 2(0) | 0(1) | 2(0) | 2(0) — 한계 ③ |
| E7b · L3 D1 본형 | 2 | 0 | 0 | **0** |
| E12 폴더 파일별 이동+교체 | 2(1) | 0(4) | 0(4) | 0(4) |
| L5 한 커밋 (q→r + 새 q) · 테스트 p→r | 0(1) | 0(2) | 0(2) | 0(2) |
| L6 L5 트리 · 테스트 p→q | 2 | 0 | 0 | 0 — 리뷰 o-1(D1 본형 + 복사본, 설계가 받아들인 의미론) |
| L7 web/ 밖 유입 → 개명 | 2 | 0 | 2 | 2 |
| **L9** 무관 이력 뿌리가 같은 경로를 다른 내용으로 | 2(0) | 0(1) | 0(1) | **2(0)** |
| 나머지 E2~E6 · E7a · E8 · E8b · E9~E11 · L1 · L4 · L8 | 모든 판 같음 | | | |

- 모든 사례에서 «HEAD green → V3 red» 회귀는 0건이다.

### 변이 시험 [실측 — scratch `r8-d1d3-impl/mutate.py` · 48건]

| 변이 | 결과 | 잡은 사례 |
|---|---|---|
| M1 `옛 ∈ 기준` 제거 | 47/48 | S14o |
| M2 `옛 ∉ 대상` 제거 | 47/48 | S14e |
| M3 `새 ∈ 대상` 제거 | 47/48 | S14j |
| M4 `새 ∉ 기준` 제거 | 47/48 | S14k |
| M5 사슬 없이 개명마다 저장 | 45/48 | S14c · S14i · S14n′ |
| MA A 끊기 제거 | 46/48 | S14i · S14n′ |
| MR 뿌리 부모 `commit^`(시제품) | 46/48 | S14n · S14n′(exit 1) |
| MS 뿌리 건너뛰기(V2) | 47/48 | S14n′ |
| M9 폴더 쌍 조건 제거 | 46/48 | S6b · S14h |
| M7 `--first-parent` 제거 | **48/48 생존** | — |

- **M7 은 생존 변이다.** 머지의 첫 부모 diff 가 곁가지의 개명+교체를 `A` 로 내면, A 끊기가 곁가지 사슬을 지운다. 그래서 시험한 모양에서 결과가 같다.
  - `--first-parent` 는 머지 diff 와 곁가지 커밋이 같은 변경을 두 번 세지 않게 하는 선택이다. 이것을 가르는 자연스러운 모양은 찾지 못했다.
  - 재검토가 찾은 동치 변이 M6(`pop`→`get`) · MA2(A 끊기 순서) · MC(`R/C → added` 갈래)도 생존이고, 동치다(재검토 o-2).
- **`옛 ∈ 기준` 이 필요한 곳.** 뿌리 커밋까지 A 로 끊으면, 사슬 시작 트리가 기준일 때 A 끊기가 `옛 ∈ 기준` 을 함의한다.
  - 그래서 이 조건이 혼자 막는 모양은 기준이 대상의 첫 부모 줄기 밖에 있어 사슬이 기준이 아닌 트리에서 시작하는 경우다.
  - S14o 가 이것을 고정한다. 재검토 n-1 을 반영하면 S14n 만으로는 M1 이 살아남으므로 S14o 를 더했다(§3-5).

## 2. D3 — 명세 인용 0 과 `extract_contract.py` exit 1

### 변경 (스크립트·F10 무변)

Coordinator `dddjango-web/commands/dddjango-web.md`(Codex `skills/dddjango-web/SKILL.md` 같은 자리 · 같은 문장):

- **«계약 인용 0 확인(G1 배너 직전 · openapi 동결본이 있을 때)» 문단 신설**(`:199` / Codex `:222` · 재검토 n-4). 명세 인용이 0이면 두 조건을 모두 확인한다.
  - 명세가 `계약 소비: 없음(인용 0)` 을 명시했다.
  - 명세 **기능** 파일 목록에 `client/` 아래 **신규·수정** 파일이 0개다(삭제와 슬라이스 0 절은 셈하지 않는다 · 재검토 n-3).

  하나라도 빠지면 매핑 누락이므로 **G1 배너를 내기 전에** architect 로 반송한다. 통과한 인용 0은 step 6에서 계약 절단을 생략한다.
- **Phase 1 step 6(`:202` / `:225`).** «명세가 인용한 엔드포인트가 0이면(G1 배너 직전 «계약 인용 0 확인»을 통과한 명세다) 계약 절단을 생략한다». 생략할 때는 셋을 한다(m-5).
  - `contract-paths.txt`·`server-contract.json` 을 만들지 않는다.
  - 재사용 폴더의 이전 절단본을 지운다.
  - `scope.md` 에 `계약 절단: 명세 인용 0 — 생략(동결본 유지)` 1행을 적는다.

  coder-web 입력은 «없음 — 인용 0»이다.
- **exit 1 갈래(같은 문단 · m-3).**
  - "인용 path 가 동결본에 없음" → 설계 반송.
  - 동결본 내용 불량("파싱 실패" — 비JSON·최상위 비객체 · "Swagger 2.0 문서") → G0 계약 출처 재해소. 단 "파싱 실패: [Errno …]"는 읽기 실패다.
  - "인용 path 0개" → 전사 누락이므로 재절단한다.
  - 그 밖(사용 오류 · 동결본 읽기 실패 `[Errno …]` · paths-file 읽기 실패 · 산출 쓰기 실패) → 미실행(통과 간주 금지)이다. 고쳐서 다시 돈다. 고칠 수 없으면 «계약 절단 미실행 — <stderr 원인>»을 G1 직후 상태 줄로 보고하고, 다음 진입(Phase 2·재개봉)을 멈춘다. 경량본 없이 coder-web 을 부르지 않는다.
- **Phase 2 coder-web 입력(`:214` / `:237`).** «step 6에서 인용 0으로 절단을 생략했으면 «없음 — 인용 0»을 명시».
- **수정 모드 G1′(`:246` / `:269`).** «G1' 배너 직전에 Phase 1 «스캔 단위 확인»·«계약 인용 0 확인»을 같은 방식으로 한다 … 엔드포인트 인용이 바뀌면 계약 재절단 — 인용이 0이 되면 Phase 1 step 6의 인용 0 규칙».
- **설계 반송 재진입(`:269` / `:292`).** «인용이 0이 되면 재개봉 전에 Phase 1 «계약 인용 0 확인»을 하고(빠지면 architect 반송) step 6의 인용 0 규칙(이전 절단본 삭제)대로 절단을 생략하며 coder-web 입력의 계약을 «없음 — 인용 0»으로 바꾼다».
- **산출물 목록(`:39` / `:92`).** «… `contract-paths.txt` 동봉 · 명세 인용 0으로 생략하면 둘 다 없음».

역할 파일(양 런타임):
- **architect** `dddjango-web/agents/design-architect-web.md:45` · Codex `dddjango-web-design-architect-web/SKILL.md:47` 의 «계약 소비 매핑» 끝에 더한 문장: «소비할 엔드포인트가 없으면 이 절에 `계약 소비: 없음(인용 0)` 1행을 명시하고 `client/` 파일을 새로 만들거나 고치지 않는다(소비가 끊겨 쓰지 않게 된 client 의 삭제는 예외)»(m-4 · n-3).
- **coder-web** `:27`: «정적 화면 한정 승인이거나 명세가 `계약 소비: 없음(인용 0)`을 명시했으면 '없음' 명시 입력».

### 확인

- `fixtures_contract.sh` 는 PASS 13 으로 무변이다. F10(빈 paths-file = exit 1)의 전사 누락 기계 가드를 유지한다.
- 새 문장은 모두 같은 치환 문자열로 양 런타임에 1회씩 들어갔다(각 치환이 파일마다 정확히 1회 일치했다). 적용 범위 규범 byte 대조는 green 이다.
- architecture-web `final.md:118` 표는 모순이 아니다(인용 0 이면 대상이 빈다). byte 미러 reference 라 무변이다.
- 행동 확인은 다음 리허설 몫이다. 인용 0 요청에서 명시 1행 → G1 배너 직전 확인 통과 → step 6 생략 → coder 입력 «없음 — 인용 0».

## 3. 명세·시제품과 다른 점

1. **뿌리 커밋 처리.**
   - 시제품 `commit + '^'` 는 무관 이력 구간에서 exit 1 을 낸다.
   - V2 는 뿌리를 건너뛰었다. 그러면 뿌리가 들인 경로의 계보가 안 끊겨 L9 거짓 green 이 났다.
   - V3 는 빈 트리를 부모로 diff 한다(재검토 n-1). S14n·S14n′ 이 고정한다.
2. **픽스처를 공용 기준 저장소에 맞춤.**
   - S14b 는 S7b 방식의 좁힌 치환이다.
   - S14g·S14h·S14n 은 사례 전용 기준 커밋을 쓴다. 기존 계수(S6b «쌍 2» 등)는 무변이다.
   - 교체 내용은 고정 표지라 결정적이다.
3. **리뷰 m-1 반영의 부수 효과: E1b·L2 가 red 가 됐다.** 삭제 커밋 뒤 재생성 커밋으로 교체한 경우다.
   - V1 대비 더 엄격하고, HEAD 대비로는 같은 결과(red)다.
   - 한계 ③으로 머리 주석과 §6 에 적었다(재검토 n-2).
   - 파이프라인의 교체는 제자리 수정(M)이다(L3·S14a green). 한 커밋 안 «옮기고 같은 자리에 새로 만들기»도 green 이다(L5).
4. **Codex step 6 의 기존 차이는 관찰만 했다**(리뷰 o-3 · 이번 수리와 무관). 별도로 정렬해야 한다.
5. **S14o 는 요청 목록 밖에서 더했다.** 재검토 n-1 을 반영하면 `옛 ∈ 기준` 을 지우는 변이(M1)가 기존 46건+S14n′ 에서 살아남는다.
   - 리뷰 M-1 의 요구(조건마다 떨어지는 픽스처)를 유지하려고 1건을 더했다.
   - 모양은 기준이 곁가지 커밋이고 `-s ours` 머지로 대상의 첫 부모 줄기 밖에 있는 경우다.

## 4. 검증 명령과 결과 (최종 V3)

| 명령 | 결과 |
|---|---|
| `bash dddjango-web/scripts/test/fixtures_subst.sh` | `PASS=48 FAIL=0` |
| 같은 48건 → HEAD · V1 · V2 사본 | 44 · 46 · 47(§1) |
| `python3 r8-d1d3-impl/mutate.py` | §1 변이 표. M7 만 생존 |
| `bash diag-D1/repro_d1.sh <worktree backstop.py>` | [1]·[2]·[6] exit 0 · 쌍 1 |
| `bash diag-D1/proposed_s14.sh` · `repro_d1_variants.sh` | 8/8 · V1 0 · V2 쌍 7 · V3 exit 2 |
| `bash r8-d1d3-impl/edge2_review.sh` · `edge3_review.sh` | §1 표(L9 V3 exit 2) |
| `make verify-web` | **exit 0**. 세부는 아래 |
| `diff -rq --exclude=__pycache__ dddjango-web/scripts codex-…/scripts` · assets | 차이 0 |
| `claude plugin validate dddjango-web --strict` | `✔ Validation passed` |
| `python3 workspace/tools/manifest_seal.py --check --draft` | green(dddjango-web 은 봉인 밖) |

`make verify-web` 세부(run_fixtures 16 파일 · 실패 0):
- 스크립트 픽스처: subst **48** · debt 80 · refactor_audit 77 · backstop 62 · extract 31 · motion_spec 25 · clip_clearance 24 · audit 22 · token_disposition 21 · focus_ring 19 · ui_javascript 17 · contract 13
- 파이썬 테스트: assets 26 · design_evidence 33+32 · templates 9 · component_identity 8
- refactor_audit self-test: claude·codex 모두 red 0
- byte 미러(scripts·assets·references·REQUEST_GUIDE) 모두 green. 요청 가이드 계약 PASS
- `make verify` 전체는 돌리지 않았다. 바뀐 파일이 dddjango·ontology·봉인 대상 밖이다.

## 5. 변경 파일

- `dddjango-web/scripts/src/subst.py` · `dddjango-web/scripts/test/fixtures_subst.sh`
- `codex-dddjango-web/skills/dddjango-web/scripts/src/subst.py` · `…/scripts/test/fixtures_subst.sh`(byte 미러)
- `dddjango-web/commands/dddjango-web.md`(`:39`·`:199` 신설 문단·`:202`·`:214`·`:246`·`:269`)
- `codex-dddjango-web/skills/dddjango-web/SKILL.md`(`:92`·`:222` 신설 문단·`:225`·`:237`·`:269`·`:292`)
- `dddjango-web/agents/design-architect-web.md`(`:45`) · `codex-dddjango-web/skills/dddjango-web-design-architect-web/SKILL.md`(`:47`)
- `dddjango-web/agents/coder-web.md`(`:27`) · `codex-dddjango-web/skills/dddjango-web-coder-web/SKILL.md`(`:27`)
- (신규) `workspace/eval/web-refactor-entry/repair-R8-D1-D3-impl.md`(이 기록)

## 6. 남은 위험

- **fail-closed 한계 셋.** 거짓 green 이 아니다. exit 2 → 오탐 보고 → `ⓐ 재상정` «플러그인 결함»으로 드러난다. 머리 주석에 적었다.
  1. V3·E6: 한 커밋 안에서 개명과 유사도 50% 미만 교정을 함께 한 경우
  2. E5·S14m: 곁가지 안에서 개명과 교체를 함께 한 뒤 머지한 경우. `--first-parent` 밖이고 머지 diff 는 D+A 다. 파이프라인 슬라이스 커밋은 선형이다 [추정]
  3. E1b·L2: 개명된 경로를 한 커밋이 지우고 뒤 커밋이 다시 만든 경우. 트리는 D1 본형과 같다. 재개봉·반송 재작업이 삭제와 재생성을 커밋으로 나눌 때만 닿는다
- **합치기 뒤 ④ 재실행은 실제 위험이 아니다**(리뷰 m-6 · `squash.sh` 실측).
  - 합치기(`reset --soft`) 직후 ④는 «미커밋 web/ 밖 변경»으로 exit 1 이다.
  - 사용자가 커밋한 뒤 옛 git_snapshot 으로 돌리면 수리 전과 같이 red 다.
  - 파이프라인의 ④ 재실행은 모두 합치기 전이고(`:219`·`:230`·`:234`), 새 요청·수정 모드는 git_snapshot 을 다시 잡는다(`:250`).
- **쌍의 증거가 바뀌었다**(리뷰 o-2). 전에는 «기준↔대상 내용 유사도», 이제는 «구간 안 첫 부모 커밋에서 git 이 본 개명»이다.
  - 순수 «삭제 + 무관 추가»는 red 다(E7a).
  - `git mv` 커밋 + 제자리 덮어쓰기는 green 이다(E7b·L6 = D1 본형, 의도).
- **생존 변이**: M7 · M6 · MA2 · MC 는 §1 에 기록했다.
- **이번에 하지 않은 것**: 재검토 반영분의 다음 검토와 릴리즈(`make release-web`)는 주 세션 몫이다.

## 7. 검토 처분표

### 구현 리뷰 (`review-D1/review-web-repair.md`)

| 항목 | 처분 | 내용·사유 |
|---|---|---|
| **M-1** S14g 빈 대조 · 트리 조건 3개 무보호 | **수용** | S14g 를 E4 형태로 바꾸고 S14j(E2)·S14k(E3)를 더했다. 조건마다 떨어지는 픽스처가 있다. 최종 대응은 M1 → S14o · M2 → S14e · M3 → S14j · M4 → S14k(§1 변이 표) |
| **m-1** 거짓 계보(E1) | **수용 · 코드** | A 경로 계보 끊기. S14i 추가. 부수 효과 E1b red(§3-3) |
| **m-2** 머지·뿌리 픽스처 · E5 | **수용(E5 는 한계 기록)** | S14l · S14n · S14m 을 더했다. E5 는 DAG 사슬(곁가지 순회 + evil merge A 판정)이 필요한데 파이프라인 커밋은 선형이라 고치지 않았다(원칙 05). 머리 주석과 §6 에 적었다 |
| **m-3** `[Errno]` 오분류 · 끝 상태 | **수용** | 읽기 실패는 미실행이다. 고칠 수 없으면 상태 줄로 보고하고 진입을 멈춘다. 스크립트 독스트링은 무변이다(D3 (A) 유지) |
| **m-4** 매핑 누락의 소리 없는 생략 | **수용** | 명시 ∧ client 조건. architect 명시 의무와 coder-web 문구를 맞췄다(재검토 n-3·n-4 로 다듬음) |
| **m-5** 재사용 폴더 옛 경량본 · `:39` | **수용** | 이전 절단본 삭제 · G1′·재진입 연결 · 산출물 목록 문구 |
| **m-6** 합치기 뒤 ④ 문장 | **수용** | §6 을 실측대로 고쳤다 |
| o-1 V3 싼 보강 | 보류 | 범위 밖. 현장에서 V3 가 나오면 첫 후보다 |
| o-2 세탁 경계 이동 | 기록 | §6 |
| o-3 Codex step 6 기존 차이 | 기록 | §3-4. 별도 정렬 |
| o-4 리팩토링 모드 계약 입력 공백 | 보류 | 기존 공백이다. D3 회귀가 아니다 |

### 재검토 (`review-D1/rereview-web-repair.md`)

| 항목 | 처분 | 내용·사유 |
|---|---|---|
| **n-1** 뿌리 건너뛰기가 A 끊기를 빠뜨림(L9) | **수용 · 코드** | 뿌리 커밋은 빈 트리를 부모로 diff 한다(`parent` 1문). S14n′(L9 형태 → red)을 더했다. L9 결과: V2 exit 0 → V3 exit 2. 그 결과 M1 이 기존 픽스처에서 살아남아 S14o 를 더했다(§3-5) |
| **n-2** E1b·L2 한계 목록 누락 | **수용** | 머리 주석 한계를 셋으로 늘렸다. §1 머리 주석 목록과 §6 한계 ③에 적었다 |
| **n-3** `client/` 0 조건과 client 삭제의 충돌 | **수용** | Coordinator: «명세 기능 파일 목록에 `client/` 아래 신규·수정 파일 0개(삭제와 슬라이스 0 절은 셈하지 않는다)». architect: «새로 만들거나 고치지 않는다(소비가 끊겨 쓰지 않게 된 client 의 삭제는 예외)». 양 런타임 |
| **n-4** 명시 누락 반송이 G1 승인 뒤 | **수용** | «계약 인용 0 확인»을 G1 배너 직전 문단으로 신설했다. step 6 에는 생략 실행만 남는다. 수정 모드 G1′ 도 같은 확인을 한다. 게이트가 없는 설계 반송 재진입은 재개봉 전에 확인한다. 양 런타임 |
| o-1 L6 은 D1 본형 + 복사본 | 기록 | §1 표 · 설계가 받아들인 의미론 |
| o-2 동치 변이 MA2·MC(+M6) | 기록 | §1. `elif new.startswith('web/')` 갈래는 기본 설정에서 닿지 않는 방어 코드로 둔다 |
| o-3 미실행 정지 때 `scope.md` 기록 | 보류 | 반영 목록 밖이다. 드문 경로다. 필요하면 `계약 절단: 미실행 — <원인>` 1행을 더하는 것이 후보다 |
| o-4 «G1 직후 상태 줄» 용어 | 보류 | 표현만의 문제다(의미 같음) |
| o-5 생존 변이 M6·M7 | 기록 | §1 |
