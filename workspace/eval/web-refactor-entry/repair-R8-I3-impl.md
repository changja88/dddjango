# 수리 기록 — R8 후속 2건: Codex step 6 기존 차이 · 미실행 정지 기록 (dddjango-web · 2026-09-29)

- 출처: `repair-R8-D1-D3-impl.md` §3-4 · §7 처분표 o-3 두 줄(구현 리뷰 o-3 «Codex step 6 기존 차이» · 재검토 o-3 «미실행 정지가 한 줄 상태로만 남는다»).
- 작업 위치: 격리 worktree `.claude/worktrees/agent-acd60c09333360921`. 커밋·push 하지 않는다(미커밋 diff).
- worktree 는 `acbfffda`(main 보다 13 커밋 뒤)에서 시작했다. `git merge --ff-only main` 으로 `fcf051fd`(main 과 같음)까지 앞당겼고 새 커밋은 없다.
- 판 이름:
  - **1차** = 첫 구현
  - **2차** = 독립 리뷰(`review-I3/review-I3.md` · «수정 후 승인» · blocker 0 · major 3 · minor 4 · nit 4)와 주 세션 처분을 반영한 판
  - **3차** = 재검토(`review-I3/rereview-I3.md` · «수정 후 승인» · major 0 · minor 4 · nit 4)를 반영한 최종본(§7)
- 3차 뒤 이 diff 를 스냅샷으로 떴다(§7-4). 이어지는 1.1.8~1.1.12 되살림 걷기는 별도 단위 I4(`repair-R8-I4-impl.md`)다.
- Serena·Graphify 는 쓰지 않았다(지시).
- 표기: **[실측]** = 파일·명령 결과로 확인 · **[추정]** = 확인하지 않은 판단.

## 1. 항목 1 — Codex step 6 기존 차이

### 1-1. 차이 목록 [실측]

플랫폼 토큰(`${SKILL_DIR}`↔`${CLAUDE_PLUGIN_ROOT}` · «네이티브 셸로»↔«Bash로»)을 맞춘 뒤 Claude 와 Codex 의 Phase 1 step 6 을 문자 단위로 대조했다. 차이는 **둘**이다.

| # | Claude | Codex(수리 전) |
|---|---|---|
| S1 | «동결본이 없으면(정적 화면 한정 진행) **계약 절단만** 생략한다 — 아래 두 기계 점검(모션 처분 표 · 토큰 처분 집행)은 각자의 발동 조건으로 따로 판단한다.» | «동결본이 없으면(정적 화면 한정 진행) 이 단계를 생략한다.» |
| S2 | «**같은 시점 — 토큰 처분 집행 점검** … `check_token_disposition.py --spec-only` … 1줄.» | 없음 |

### 1-2. 원인 — 이력 [실측]

- `05cbf18e`(09-15)가 S1·S2 를 양 런타임에 같이 넣었다. clip 호출 2곳과 architect·design-review 의 토큰 처분 문장도 같은 커밋이다.
- `c627d8f6`(09-16)은 Codex SKILL 3개와 Coordinator 를 v1.1.12 로 리셋했다. 설계 기록(`workspace/design/2026-09-16-web-strip-observation-subsystem.md:34`)에는 «clip·토큰 처분 호출 3곳 재적용»이라고 적었다. 그러나 재적용은 **Claude Coordinator 에만** 됐다.
- 그래서 Codex 런타임 안에 모순이 생겼다. byte 미러 reference `architecture-web/references/final.md:142` 는 G1 직후 토큰 처분 검사를 약속하는데, Codex Coordinator 는 그 검사를 돌리지 않는다.

### 1-3. 정렬 방향 — Codex 를 Claude 에 맞춘다

- **S1: Claude 가 맞다.** 계약 절단은 이미 step 제목의 «(openapi 동결본이 있을 때)»로 자기 조건을 갖는다. Codex 문장처럼 step 전체를 생략하면 openapi 와 무관한 모션·토큰 점검까지 `static_only` 시안 빌드에서 빠진다. 그래서 Claude 에 반영할 것은 없다.
- **S2: Claude 문장을 Codex 에 넣는다.** 경로는 `${SKILL_DIR}`, 실행은 «네이티브 셸로»로 바꾼다.

### 1-4. 같은 원인의 나머지 차이 (2차 정정 — 리뷰 M-3)

1차 기록은 «같은 원인은 E1~E4 넷뿐 · Codex 전용 보강 문장은 `c627d8f6` 누락이 아니다»라고 썼다. **틀렸다.** `c627d8f6` 리셋은 차이를 두 방향으로 남겼다.

**(가) Codex 에서 빠진 것 — 정렬함(1차).** 모두 Claude 정본 문장을 옮긴 삽입이다.

| # | 위치(Codex) | 정본(Claude) | 내용 |
|---|---|---|---|
| E1 | `skills/dddjango-web/SKILL.md` G2 배너 | Coordinator G2 배너 | 절단 여유 정적 검사 문단 |
| E2 | 같은 파일 트리비얼 ③ | 트리비얼 ③ | `check_clip_clearance.py` 호출 1구 |
| E3 | `dddjango-web-design-architect-web/SKILL.md:52` | `agents/design-architect-web.md:50` | 토큰 처분 표 판형 · 기각 사유 사실성 · 검사기 · 컨테이너 지목 |
| E4 | `dddjango-web-design-review-web/SKILL.md:62` ⓑ | `agents/design-review-web.md:59` | 기각 사유 사실성 점검 1구 |

**(나) Codex 에 되살아난 것 — 걷음(2차).**
- 이 문장들은 `5a716c6f`·`b971583b`·`da76eecd`(09-08~13)가 양 런타임에 넣었다. `54e91e93`(09-14)이 사용자 결정으로 양쪽에서 걷었다. 결정 원문은 «되돌린 문단(특히 design-review-web의 «독립 렌더가 필요한 화면·상태만 … 추가»)은 재도입하지 않는다»이다.
- 그런데 `c627d8f6` 이 Codex 역할 SKILL 을 v1.1.12 로 리셋하면서 Codex 에만 되살렸다.
- 줄마다 «Codex→Claude 차이»를 «그 줄의 `54e91e93^`→`54e91e93` 차이»와 대조한 뒤 걷었다(scratch `i3/m3_check.py` · `i3/apply_round2.py`).

| 위치(Codex) | 걷은 문장 | 54e91e93 대조 |
|---|---|---|
| review `:28` | «원본과 실제 참조 부품에서 확인한 관련 상태는 … 독립 렌더가 필요한 화면·상태만 기존 case 절차로 추가한다. 모든 CSS pseudo-state를 별도 case로 늘리지 않는다.» | 조각까지 같음 |
| review `:30` | «·관련 상태/실제 조작·관찰 위치» · «. case별 반환에는 상태의 원본/부품 정의 위치, … 후속 구현·검증에 넘긴다» | 조각까지 같음 |
| review `:63` | «`등가`·`N/A/해소` 처분은 … 역대조한다. …» 5문 · «architecture-web §1의 기본 요구·추가 기능 기준으로 Y 목록과 기본안을 역대조한다. …» 4문 | 조각 대조(2순위)로 확인. 지운 조각은 모두 `54e91e93^` 판에 있고 `54e91e93` 판에는 없다. 정렬 경계만 달라 조각 단위 일치는 아니다 |
| architect `:54` | «case·» · «·관찰» · «관련 부모 » · «구성»(←«구조») · «·관련 부모 배치/여백/overflow» · «다. G0의 case별 관련 상태와 motion-notes의 해당 항목을 잇고 … 만들지 않는» · (복원) « 양쪽» | 조각까지 같음(7 ops) |
| architect `:94` | «중 architecture-web §1의 추가 기능 기준에 맞는 항목만» → «은» · «목록을 임의로 늘리지 않으며, 기본 요구의 생략·대체가 Y에 섞여 있으면 … 반영한» → «— 네가 'Y감이냐'를 판정하지 않고 스코프의 그 목록을 앵커로 쓴» | 조각까지 같음. 결과가 `54e91e93` 판 Codex 줄, 곧 Claude `:92` 와 같다 |

- 걷은 뒤 다섯 줄은 Claude 대응 줄과 byte 가 같다. Codex 두 파일에서 «독립 렌더가 필요한»·«N/A/해소» 는 0 건이다.
- **걷지 않은 것:**
  - **architect `:93`** — 차이는 «코디네이터»↔«Coordinator» 하나다. 플랫폼 표기이고 `54e91e93` 과 무관하다.
  - **Codex Coordinator `:30`** — «현재 호출에서 적용 설치본의 온전한 SKILL 본문을 … 필요한 절이 유실됐으면 그 절만 다시 읽는다.»
    - **(3차 정정)** 2차 기록은 «Claude 대응 없는 플랫폼 문장이라 유지»라고 적었다. **틀렸다.**
    - 이 자리는 `54e91e93` 이 1.1.7 문장(«이 SKILL 본문은 세션 시작에 이미 로드돼 있다 — **본문 파일을 다시 읽지 마라** …»)으로 바꿔 둔 곳이다. 되살아난 1.1.12 문장이므로 걷을 대상이다(재검토 조사 4 A5).
    - 이 문장은 I3 가 아니라 I4 의 A군에서 걷는다(`repair-R8-I4-impl.md`).

### 1-5. 같은 원인이 양쪽에 대칭으로 남긴 손실 — 고치지 않음 · 후속 후보 [실측]

**① `check_focus_ring.py` Coordinator 호출 소실**

| 항목 | 사실 |
|---|---|
| 도입 | `90a59f46`(09-15 · 「게이트 하드월 철거」 수리 C «링 중첩 정적 검사»). G2 배너에 «이중 링 정적 검사» 문단을 넣었다. 절단 여유와 한 항목 «링 정적 검사: 절단 N건 · 이중 링 M건»으로 표기했고, 트리비얼 ③ 에도 호출이 있었다. 양 런타임이다 |
| 소실 | `c627d8f6` 이 양쪽에서 걷었다. 문자열 수는 `c627d8f6^` 2·2 → 0·0 이다. 리셋 기준 v1.1.12 가 90a59f46 보다 앞서기 때문이다 |
| 의도였나 | **아니다 [추정 — 문서 근거 둘].** 설계 기록 `:27` 은 «그 뒤 나온 정적 수리(절단 충실도 1.1.16·주석 오탐 1.1.18·**포커스 링**)만 보존한다»이고, `:38` 은 «보존: … clip·**focus**·motion·token 검사 4»이다. 그런데 재적용 목록(`:34`)은 «clip·토큰 처분 호출 3곳»뿐이다. 검사기(`check_focus_ring.py`)와 픽스처(19건 green)는 남았고 호출만 사라졌다 |
| 낡은 참조 | `agents/discipline-reviewer-web.md:77` 5번(Codex 미러 같음)은 «`check_focus_ring.py <web 루트>` 가 정적 선검하고, … 기계가 안 보므로 네가 본다»라고 적는다. 아무도 돌리지 않는 선검을 전제하므로 낡았다 |
| 후속 후보 | (a) 양 런타임 Coordinator 에 `c627d8f6^` 판의 G2 «이중 링 정적 검사» 문단과 트리비얼 ③ 호출을 되돌린다(설계 기록의 보존 의도와 맞다). 또는 (b) discipline-reviewer 5번에서 «정적 선검» 구를 걷는다. (a)가 기록된 의도에 가깝다 |

**② clip «인벤토리 줄은 발견이 아니다» 문장 소실**
- `05cbf18e` 의 G2 절단 여유 문단에는 «인벤토리 줄(링 보유 요소 없음·조인 실패)은 발견이 아니며 조인 한계(include/extends 밖·동적 클래스)는 그대로 고지한다»가 있었다.
- `c627d8f6` 재적용에서 양쪽 모두 빠졌다(inv 1→0).
- 검사기는 `[inventory]` 줄을 계속 출력한다(`check_clip_clearance.py:394-395`). 그래서 배너 작성자가 인벤토리 줄을 발견으로 셀 여지가 있다.
- 재적용이 문장 하나를 빠뜨린 것으로 보인다 [추정]. 후속 후보는 ①(a)와 함께 되돌리는 것이다.

## 2. 항목 2 — 미실행 정지 기록 (2차: 기록처를 build-state 로 옮김)

### 2-1. 갈래별 판단 — 기록이 필요한 것은 «미실행» 하나 (1차와 같음)

| 갈래(step 6 exit 1 과 대조) | 흐름 | 기록 필요 |
|---|---|---|
| «인용 path가 동결본에 없음» | 설계 반송 → 재절단 | 아니다 |
| 내용 결함(«파싱 실패» 비JSON·비객체 · «Swagger 2.0») | G0 계약 출처 재해소. 재동결하거나 정적 한정 결정을 스코프 메모·`static_only` 에 적는다 | 아니다(가는 단계가 자기 기록을 가진다) |
| «인용 path 0개» · 계수 불일치(전사 누락) | step 6 안에서 재절단한다 | 아니다 |
| [warn] | 배너나 한 줄 상태에 표면화한다 | 아니다 |
| **그 밖(사용 오류 · `[Errno …]` · paths-file · 산출 쓰기 실패) — 고칠 수 없음** | **진입을 멈춘다** | **그렇다** |

### 2-2. 기록처 — (B) build-state `contract_cut` [리뷰 M-1 권장안 · 성립 확인]

**1차의 문제 [실측 · 리뷰 재현].**
- 1차는 D3 행처럼 `scope.md` 에 적고, Phase 1 머리 포인터 문장(C1)을 넓혔다.
- 정적 manifest 에서는 포인터 갱신으로 풀린다.
- 그러나 시안 빌드의 주 경로인 archive(Claude Design `.dc.html`)에서는 풀리지 않는다. `review_digest` 에 scope 바이트가 들어가므로, 포인터만 갱신해도 inputs 가 exit 2(`reviewed-input does not match`)다.
- 1차 탐침은 정적 경로만 봤다.

**(B)가 성립하는 근거.**
- **digest 밖.** `check_design_evidence.py` 의 digest 입력은 `design-input.json` · scope · coverage_review · manifests · case 포인터 · `web/` 트리다. `build-state.json` 은 어느 digest 에도 들지 않는다(스크립트에 `build-state` 문자열 0).
- **원칙.** Coordinator `:36` 은 «`scope.md`는 사람이 정한 범위, 이 파일은 기계가 낸 빚이라 섞지 않는다»이다. 계약 절단 결과는 기계 상태이고, build-state 는 기계 상태의 재개 앵커다. 형제 필드 `static_only` 도 여기 있다.
- **읽는 쪽 전수.**

  | 읽는 쪽 | 경로 | 처리 |
  |---|---|---|
  | 세션 재개 | 스키마 절 재개 규칙(`:89`) · Phase 2 재개(`:271`) | `contract_cut`이 `미실행 — …`이면 Phase 2 진입·재개봉 전에 step 6 계약 절단부터 다시 돈다 |
  | 재사용 폴더(새 요청) | `:149` 복원 | 복원해도 새 요청은 step 6 을 다시 돌며 덮어쓴다. step 6 없이 코드로 가는 수정 모드에서 앞 요청의 미실행이 남아 있으면, 위 재개 규칙이 계약 절단부터 돌게 한다 |
  | coder 입력 | Phase 2 step 3(`:215`) | «없음 — 인용 0»의 근거로 `contract_cut` 을 가리킨다 |
  | 감사 | 산출물 목록(`:39`) · 스키마 | 경량본 부재의 사유가 `contract_cut` 에 있다고 적는다 |
  | 기계 | `backstop.py`·`refactor_audit.py` 는 build-state 의 `has_design_screen`·`git_snapshot` 만 읽는다 | 새 키는 무해하다. 옛 파일에 키가 없으면 빈 값으로 읽는다 |
  | 문자열 소비자 | `계약 절단:` 을 읽는 스크립트·도구는 0 이다 | — |

- **D3 기록처도 함께 바뀐다.** `810041b9` 의 인용 0 행이 `scope.md` → `contract_cut` 로 옮겨 간다. D3 는 아직 릴리즈 전이다(9 배포 대기). 그래서 필드 호환 부담은 없고, 리허설 폴더만 옛 행을 가진다.

### 2-3. 수명 1규칙 · 미실행 정지 [리뷰 m-1·m-2·n-1]

- **덮어쓰기 규칙(step 6 머리).** «절단 결과는 돌 때마다(G1′·설계 반송 재진입 포함) build-state `contract_cut`에 덮어쓴다(절단 성공·동결본 없음 = 빈 값)». 인용 0 행과 미실행 행이 서로 남는 모순이 사라진다.
  - 1차 모순 1: 인용 0 → 1 이상이 됐는데 «생략» 행이 남음
  - 1차 모순 2: 미실행 뒤 인용 0 으로 가면 두 행이 함께 남음
- **미실행 정지.** 인용 0 갈래와 같이 이전 절단본(`contract-paths.txt`·`server-contract.json`)을 지운다. 그러면 재사용 폴더에 남은 옛 경량본을 입력으로 쓸 길이 없다. 재절단은 동결본에서 다시 만들므로 잃는 것이 없다.
- **철자.** 값은 `미실행 — <stderr 첫 줄>`, 상태 줄은 «계약 절단: 미실행 — <stderr 첫 줄>»로 한 문자열이다. «첫 줄»로 1행을 보장한다.

### 2-4. `scope.md` 에 남는 기록 — (A) 일반형 규칙 [리뷰 M-1 (A) · M-2 · m-3]

- 계약 절단 기록이 빠져도 inputs 게이트 뒤의 `scope.md` 쓰기는 남는다. `54e91e93` 이전부터 있던 공백이다(G0 승인 기록 갈래 · `e39ceeb1`).
- 그래서 Phase 1 머리에 열거가 아닌 일반형 규칙 **«scope 바이트 변경»**을 둔다(C1 대체).
  - 대상: Phase 0 «ready 직전 입력 게이트» 뒤 `scope.md` 바이트를 바꾸는 기록 **모두**
  - 시점·주체: 다음 coder 호출의 inputs 전에 네가 한다
  - 명령: `design-input.json` 의 `scope.sha256` 을 현재 `scope.md` SHA-256 으로 바꾼다
  - archive 는 포인터 갱신 → `--phase prepare` → 입력범위 모드 재검토 → inputs 다
  - 끝에 «기계가 낸 상태는 `scope.md`에 쓰지 않고 build-state에 둔다»를 붙여 (B)를 일반화한다
- G1 override 문장(«hash 포인터도 갱신하고 같은 절차»)은 원래대로 둔다. 일반형 규칙은 «그 밖에도»로 나머지를 덮는다.
- 쓰기 자리에 붙인 참조(리뷰 M-2 표):

  | 자리 | 쓰기 | 처리 |
  |---|---|---|
  | `:195` step 4 — Y 분류 충돌 → scope 정정 | scope.md | 참조 «(Phase 1 머리 «scope 바이트 변경»)» |
  | `:196` 비위반 이동 STOP 답 — «범위 아님에 한 줄» | scope.md | 참조 |
  | `:198` 스캔 단위 확인 → G0 재승인 새 ⓐ | 스코프 메모 슬라이스 0 줄(`:160` 일반 규칙) | 참조(«스코프 메모의 슬라이스 0 줄 기록은 …») |
  | `:221` 반송 처리 (나) — 범위 합의 | 기록처가 명시되지 않았다 | 조건 참조 «합의를 `scope.md`에 적으면 …». 새 기록 의무는 만들지 않았다 |
  | `:270` 설계 반송 재진입 — 인용 0 | (B)로 build-state | 규칙 대상이 아니다. 대신 «`contract_cut` 기록» 참조를 붙였다(m-4) |
  | G0 계열(`:147` 정적 한정 · `:160` 슬라이스 0 줄 · `:184` 영역 배치) | scope.md | 일반형 규칙 본문의 예시로 덮는다 |
  | G1 override(`:202`) · 수정 모드 G1′(`:247` «절차는 G1과 동일») | scope.md | 기존 G1 override 문장이 덮는다 |

- 쓰기 자리의 줄 번호는 2차 판 Claude 기준이다. Codex 는 +23 전후다.

## 3. 바꾼 문장 — 2차 최종 (양 런타임 같은 문장)

| # | 자리(Claude · Codex) | 변경 |
|---|---|---|
| R1 | 산출물 목록 `:39` · `:92` | «명세 인용 0으로 생략하면 둘 다 없음» → «… 생략하거나 절단 미실행으로 멈추면 둘 다 없음 — 사유는 build-state `contract_cut`» |
| R2 | 스키마 `:83` · `:136` (신규 키) | `"contract_cut": "<Phase 1 step 6 계약 절단 결과 — 빈 값(절단 성공·동결본 없음) \| 명세 인용 0 — 생략(동결본 유지) \| 미실행 — <stderr 첫 줄>. 절단을 돌 때마다(G1′·설계 반송 재진입 포함) 이번 결과로 덮어쓴다. 키가 없으면 빈 값으로 읽는다>"` |
| R3 | 갱신 시점 `:88` · `:141` | «G1 승인 시(g1_approved) → **계약 절단 뒤(contract_cut)** → Phase 2 진입 시» |
| R4 | 스키마 재개 `:89` · `:142` | «…스냅샷 ref**·계약 절단 상태**를 복원하고 … (`contract_cut`이 `미실행 — …`이면 Phase 2 진입·재개봉 전에 Phase 1 step 6의 계약 절단부터 다시 돈다)» |
| R5 | Phase 1 머리 `:190` · `:213` | 1차 C1 문장을 **«scope 바이트 변경»** 일반형 규칙으로 바꿨다(§2-4) |
| R6 | step 4 `:195` · `:218` | «scope를 정정하고(Phase 1 머리 «scope 바이트 변경»)» |
| R7 | STOP `:196` · `:219` | «(답은 `scope.md` 범위 아님에 한 줄로 기록한다 — «scope 바이트 변경»)» |
| R8 | 스캔 단위 확인 `:198` · `:221` | «재승인에서 새 ⓐ가 생기면(스코프 메모의 슬라이스 0 줄 기록은 «scope 바이트 변경»)» |
| R9 | step 6 `:203` · `:226` | 머리에 덮어쓰기 규칙을 더했다. 인용 0 기록처: «`scope.md`에 `계약 절단: …` 1행» → «build-state `contract_cut`에 `명세 인용 0 — 생략(동결본 유지)`» |
| R10 | step 6 미실행 | «고칠 수 없으면 이전 절단본(`contract-paths.txt`·`server-contract.json`)을 지우고 build-state `contract_cut`에 `미실행 — <stderr 첫 줄>`을 적은 뒤 «계약 절단: 미실행 — <stderr 첫 줄>»을 G1 직후 상태 줄로 보고하고 다음 진입(Phase 2·재개봉)을 멈춘다(…)» |
| R11 | coder 입력 `:215` · `:238` | «인용 0으로 절단을 생략했으면(build-state `contract_cut`)» |
| R12 | 반송 처리 (나) `:221` · `:244` | «(… · 합의를 `scope.md`에 적으면 Phase 1 머리 «scope 바이트 변경»)» |
| R13 | 재진입 `:270` · `:293` | «step 6의 인용 0 규칙(이전 절단본 삭제 · `contract_cut` 기록)대로» |
| R14 | Phase 2 재개 `:271` · `:295` | «…스냅샷 ref·계약 절단 상태를 복원한다(`contract_cut`이 미실행이면 재개봉 전에 계약 절단부터 — 스키마 절)» |
| S1·S2·E1·E2 | Codex Coordinator | §1 (1차 그대로) |
| E3·E4 | Codex architect `:52` · review `:62` | §1-4 (1차 그대로) |
| M3 | Codex review `:28`·`:30`·`:63` · architect `:54`·`:94` | §1-4 (나) — `54e91e93` 문장을 걷었다 |
| N3 | Codex Coordinator `:82` identity 단계 | «`--phase identity`를 Bash로» → «네이티브 셸로» (리뷰 n-3 · HEAD 부터 있던 플랫폼 누수) |

- 1차의 C1(포인터 문장에 step 6 행 추가)·C2(`scope.md` 미실행 행)는 R5·R9·R10 으로 대체돼 남지 않는다.
- n-2(정본에서 옮겨 온 이력형 구절)는 손대지 않았다. 양 런타임을 함께 따로 정리할 일이다.

## 4. 검증 결과 [실측]

### 4-1. 첫 coder inputs 재현 — 2차 문면 절차 (scratch `i3/probe_i3.py` · `.out`)

리뷰 `probe_c1.py` 와 같은 하네스(워크트리 `test_design_evidence.EvidenceTests` · `test_design_archive.ArchiveTests` · tempdir)를 썼다. 절차는 2차 문면대로다.
- step 6 은 build-state 에 쓴다.
- 미실행 정지는 절단본을 지우고 기록한다.
- `scope.md` 기록은 «scope 바이트 변경» 규칙을 따른다.

```
--- static manifest path (EvidenceTests) ---
[S1] inputs 기준선                                              exit=0
[S2] step 6 인용 0 → contract_cut 기록 · 첫 coder inputs          exit=0
[S3] 미실행 정지(이전 절단본 삭제 ok) · inputs                     exit=0
[S4] 재개 → 재절단 성공(contract_cut 빈 값) · 첫 coder inputs      exit=0
     scope.md 바이트 S1 과 같음: True
[S5] (A) scope 기록(STOP 답) 뒤 · 포인터 갱신 전                   exit=2 'scope: sha256 mismatch'
[S6] (A) scope.sha256 갱신 → 첫 coder inputs                      exit=0
--- archive path (ArchiveTests; collection=archive) ---
[A1] prepare+review+inputs 기준선                                exit=0
[A2] step 6 인용 0 → contract_cut 기록 · 첫 coder inputs          exit=0
[A3] 미실행 정지(이전 절단본 삭제 · contract_cut) · inputs         exit=0
[A4] 재개 → 재절단 성공(contract_cut 빈 값) · 첫 coder inputs      exit=0
     scope.md 바이트 A1 과 같음: True
[A5] (A) scope 기록 뒤 포인터만 갱신(archive 갈래 생략 시)          exit=2 'coverage_review: reviewed-input does not match …'
[A6] (A) prepare → 입력범위 재검토 → 첫 coder inputs               exit=0
```

- **(B):** 두 경로 모두 step 6 기록(인용 0 · 미실행 · 재개 성공) 뒤 첫 coder inputs 가 exit 0 이다. scope 바이트가 바뀌지 않았다.
- **(A):** scope 기록 뒤 정적은 포인터 갱신으로 0 이고(S6), archive 는 prepare → 재검토까지 해야 0 이다(A6). A5 는 archive 갈래가 왜 필요한지 보인다.
- 대조로 리뷰 `probe_c1.py` 를 같은 워크트리에서 그대로 다시 돌렸다. S1~A7 이 리뷰 기록과 같았다(하네스 동일성 확인).

### 4-2. 도구

| 확인 | 결과 |
|---|---|
| `make verify-web` | **EXIT 0** |
| `claude plugin validate dddjango-web --strict` | `✔ Validation passed` |
| `python3 workspace/tools/manifest_seal.py --check --draft` | green(그룹 10 · 봉인 파일 266). dddjango-web 은 봉인 밖이다. `--write` 는 돌리지 않았다 |
| 스키마 JSON 블록 파싱(양 런타임) | ok · 키 21 · `contract_cut` 있음 |
| 정렬 대조: 바뀐 Coordinator 줄 15개(Claude `:39`·`:83`·`:88`·`:89`·`:190`·`:195`·`:196`·`:198`·`:203`·`:215`·`:221`·`:227`·`:260`·`:270`·`:271`) | 플랫폼 표기(spawn_agent 등) 말고 차이 0 |
| 정렬 대조: Codex review `:28`·`:30`·`:63` · architect `:54`·`:94` ↔ Claude `:25`·`:27`·`:60`·`:52`·`:92` | byte 같음 |
| Codex Coordinator 의 «Bash로» · Codex diff 추가 줄의 Claude 표기 | 0 · 0 |
| `scope.md`에 `계약 절단` 을 적는 문장 · `contract_cut` · «scope 바이트 변경» | 0 · 8 · 5 (양 런타임 같음) |

`make verify-web` 세부:
- run_fixtures 16 파일, 실패 0이다.
  - 스크립트 픽스처: subst 48 · debt 80 · refactor_audit 77 · backstop 62 · extract 31 · motion_spec 25 · clip_clearance 24 · audit 22 · token_disposition 21 · focus_ring 19 · ui_javascript 17 · contract 13
  - 파이썬 테스트: 26 · 33 · 32 · 9 · 8 모두 OK
- refactor_audit self-test 는 두 런타임 모두 점검 절 62 · 어구 32 · 극성 표본 18 · red 0 이다.
- 적용 범위 규범 byte 대조, scripts·assets·references·REQUEST_GUIDE byte 미러, 요청 가이드 계약이 모두 PASS 다.
- `make verify` 전체는 돌리지 않았다. 바뀐 파일이 dddjango·ontology·봉인 대상 밖이다.

### 4-3. 바뀐 파일 · `git diff --stat` (2차 최종 · 1차 포함 누적)

```
 .../dddjango-web-design-architect-web/SKILL.md     |  6 ++---
 .../skills/dddjango-web-design-review-web/SKILL.md |  8 +++---
 codex-dddjango-web/skills/dddjango-web/SKILL.md    | 31 +++++++++++-----------
 dddjango-web/commands/dddjango-web.md              | 25 ++++++++---------
 4 files changed, 36 insertions(+), 34 deletions(-)
```

- 신규: `workspace/eval/web-refactor-entry/repair-R8-I3-impl.md`(이 기록)
- 스크립트·reference·REQUEST_GUIDE 는 무변이다.

## 5. 리뷰 처분표 (`review-I3/review-I3.md`)

| 항목 | 처분 | 내용 |
|---|---|---|
| **M-1** C1 이 archive 에서 안 풀림(재현 A3) | **수용 — (B) + (A)** | 계약 절단 기록을 build-state `contract_cut` 으로 옮겼다(§2-2). 읽는 쪽을 전수로 맞췄다(재개 2곳 · coder 입력 · 산출물 목록 · 스키마). `scope.md` 에 남는 기록에는 (A) 일반형 규칙과 archive 갈래를 뒀다(§2-4). 재현: S2~S4·A2~A4 exit 0 · S6·A6 exit 0 |
| **M-2** C1 이 열거식 | **수용** | «scope 바이트 변경» 일반형 규칙을 두고 `:195`·`:196`·`:198`·`:221` 에 참조를 붙였다. `:270` 은 (B)로 대상 밖이라 `contract_cut` 참조를 붙였다. 양 런타임이다 |
| **M-3** «같은 원인 = E1~E4» 불완전 | **수용 — 기록 정정 + 일부 수리** | §1-4 를 정정했다. `54e91e93` 사용자 결정 역행 문장 5줄을 Codex 에서 걷었고 줄마다 `54e91e93` diff 와 대조했다. architect `:93`(플랫폼 표기)·Codex Coordinator `:30`(플랫폼 전용 문장)은 걷지 않고 기록했다. focus_ring 호출 소실·discipline-reviewer 낡은 참조·clip 인벤토리 문장은 이력만 조사해 후속 후보로 올렸다(§1-5) |
| **m-1** 수명 짝 | **수용** | «돌 때마다 덮어쓴다(성공·동결본 없음 = 빈 값)» 1규칙(step 6 머리 · 스키마) |
| **m-2** 옛 `server-contract.json` | **수용** | 미실행 정지 때 이전 절단본을 지운다. 재개 때 `contract_cut` 을 읽는 규칙(`:89`·`:271`) |
| **m-3** 포인터 갱신 주체·명령·시점 | **수용** | «다음 coder 호출의 inputs 전에 네가 · `design-input.json`의 `scope.sha256`을 현재 `scope.md` SHA-256으로» |
| **m-4** 규칙 위치 | **수용** | 재진입 `:270` 에 «`contract_cut` 기록» 참조를 붙였다. (B)로 포인터 대상이 아니다 |
| n-1 두 철자 · 여러 줄 원인 | **수용** | 한 문자열 «계약 절단: 미실행 — <stderr 첫 줄>» |
| n-2 이력형 구절 | 유지 | 정본에 원래 있는 문장이다. 양 런타임을 따로 함께 정리한다 |
| n-3 Codex «Bash로» 누수 | **수용** | 1어 교체(N3) |
| n-4 노출 예시 | **수용 — 기록 정정** | 1차 §2-3 의 «이미지 교체·문구·스타일»은 대개 트리비얼로 간다. 실제 노출은 수정 모드 G1′ 에서 인용이 0 이 되는 경우와 openapi 프로젝트의 새 정적 화면이다. 결함 판정은 그대로다 |

## 6. 남긴 것 · 관찰

1. **후속 후보 — focus_ring 호출 복원과 clip 인벤토리 문장**(§1-5). 설계 기록의 «포커스 링 보존» 의도로 보아 복원 쪽이 맞아 보인다 [추정]. 복원하면 discipline-reviewer 5번의 «정적 선검»이 다시 참이 된다.
2. **재검토 o-4**(«G1 직후 상태 줄» ↔ 정의어 «한 줄 상태»)는 그대로 둔다. 표현만의 문제다.
3. **(3차 갱신) `c627d8f6` 은 Coordinator 양쪽의 `54e91e93` 문단을 전면으로 되살렸다 [실측 — 재검토 조사 4].**
   - `54e91e93` 이 걷은 조각(15자 이상) 가운데 지금 살아 있는 수: Claude Coordinator 32/34 · Codex Coordinator 34/36 · `design-acquisition.md` 양쪽 1/1.
   - `git diff dddjango-web--v1.1.12 c627d8f6` 는 Codex Coordinator 0줄 · Claude Coordinator 6줄(clip·토큰 재적용)이다. 곧 통째 리셋이다.
   - **짝이 끊긴 인용(dangling).** references·agents 에 다음이 0건이다.
     - implementation-ui §2 «필수 반환 판형» · «수정 작업의 대조 범위» · «수정 전후 비교 3종»
     - architecture-web §1 «기본 요구와 선택적 향상»
     - architect «충돌을 Coordinator에 반환»
     - design-review-web «case별 관련 상태/실제 조작·관찰 위치» 반환
     - Coordinator 는 «비교 3종»을 7곳, «필수 반환 판형»을 2곳에서 인용한다.
   - 사용자 결정(09-13 · `workspace/design/2026-09-13-web-interaction-evidence.md:5` «1.1.8~1.1.12 프롬프트 누적은 재도입하지 않는다»)은 번복 기록이 없다. 그래서 별도 단위 I4 에서 걷는다.
4. **행동 확인**은 다음 리허설 몫이다. 볼 것은 셋이다.
   - Codex 레인에서 G1 직후 토큰 처분 점검이 도는가
   - 인용 0 · 미실행이 build-state 에 기록되고 첫 coder inputs 가 그대로 통과하는가
   - `scope.md` 기록 뒤 archive 재검토를 거치는가
5. 릴리즈(`make release-web`)와 조감도 HTML 갱신은 주 세션 몫이다.

## 7. 3차 — 재검토 반영 (`review-I3/rereview-I3.md`)

### 7-1. 처분

| 항목 | 처분 | 변경(양 런타임 같은 문장) |
|---|---|---|
| **r-1** 일반화 문장이 host 상태·htmx 설치 기록·렌더 실측 생략 사유의 `scope.md` 기록 지시와 충돌 | **수용 · 필수** | Phase 1 머리 끝 «기계가 낸 상태(계약 절단 결과 등)는 …» → «계약 절단 결과는 `scope.md`에 쓰지 않고 build-state `contract_cut`에 둔다(step 6).» |
| **r-2** 미실행 소비 지점이 재개 절뿐 | **수용** | coder 입력(Claude `:215` · Codex `:238`)에 «`contract_cut`이 `미실행 — …`이면 coder-web을 부르지 않고 step 6 계약 절단부터 다시 돈다» 1구. 이 지점은 모든 경로가 지난다(수정 모드 G1' 생략 포함) |
| **r-3** 시점이 coder 호출에만 묶임 | **수용** | «다음 inputs 실행 전에(coder 호출 직전 · 트리비얼 편집 전)» |
| **r-4** 예시 «step 4의 scope 정정»·R6 이 고아 문장에 붙음 | **I4 로 넘김** | C군(Y·기본 요구)을 걷을 때 함께 걷는다 |
| q-1 G1′/G1' | **수용** | 새 문장 2곳(스키마·step 6 머리)을 파일 다수 표기 «G1'» 로 맞췄다. 파일 안 «G1′» 0건 |
| q-2 빈 값이 재개 마커 구실을 못 함 | **수용** | 성공 값 `절단 — paths <N>`(계수 대조 통과)을 뒀다. 빈 값은 «동결본 없음·아직 절단 전»만 뜻한다(스키마 · step 6 머리 규칙) |
| q-3 `:39` 가 커밋되지 않는 build-state 만 가리킴 | **수용** | «사유는 명세 `계약 소비: 없음(인용 0)`·build-state `contract_cut`» 병기 |
| q-4 목적어 빠진 문장 | **수용** | «…기록(…)이 생기면 다음 inputs 실행 전에(…) 네가 입력 게이트를 다시 통과한다» |
| 구현 기록 정정 | **수용** | §1-4 Codex `:30` 을 «걷을 대상(I4 A군)»으로 고쳤다. §6-3 은 전면 부활 수치와 dangling 목록으로 갱신했다 |

### 7-2. 재현 [실측 — `i3/probe_i3.py` 성공 값 반영 · `i3/probe_i3_r3.out`]

- 정적: S1~S4 exit 0(S4 = 재개 → `절단 — paths 1`) · S5 exit 2(`scope: sha256 mismatch`) · S6 exit 0
- archive: A1~A4 exit 0 · A5 exit 2(`reviewed-input does not match`) · A6 exit 0
- 2차와 같다. build-state 는 digest 밖이라 성공 값 변경이 inputs 에 영향이 없다.

### 7-3. 검증 [실측]

| 확인 | 결과 |
|---|---|
| `make verify-web` | **EXIT 0**. run_fixtures 16 파일 실패 0. refactor_audit self-test 양 런타임 red 0. byte 미러·요청 가이드 계약 PASS |
| `claude plugin validate dddjango-web --strict` | `✔ Validation passed` |
| 스키마 JSON 블록(양 런타임) | 파싱 ok · 키 21 |
| 바뀐 Coordinator 줄(Claude `:39`·`:83`·`:190`·`:203`·`:215`) ↔ Codex 대응 줄 | 플랫폼 표기 말고 차이 0 |

### 7-4. I3 스냅샷

- 경로: `/private/tmp/claude-501/-Users-hyun-Desktop-dddjango/ed01792c-e467-4a58-a794-ed16237ffb9e/scratchpad/i3/I3-final.patch`
  - 내용: `git diff`(추적 4파일) + `git diff --no-index /dev/null <이 기록>`
  - 파일 사본: 같은 폴더 `I3-final-tree/`(I4 만의 stat 기준)
- 이 시점 `git diff --stat`:

```
 .../dddjango-web-design-architect-web/SKILL.md     |  6 ++---
 .../skills/dddjango-web-design-review-web/SKILL.md |  8 +++---
 codex-dddjango-web/skills/dddjango-web/SKILL.md    | 31 +++++++++++-----------
 dddjango-web/commands/dddjango-web.md              | 25 ++++++++---------
 4 files changed, 36 insertions(+), 34 deletions(-)
```

- 신규(추적 밖): `workspace/eval/web-refactor-entry/repair-R8-I3-impl.md`
