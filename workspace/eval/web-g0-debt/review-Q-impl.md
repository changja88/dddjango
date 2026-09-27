판정: 수정 후 승인 — blocker 1 · major 3 · minor 10 — 러너·문면 골격은 설계 v5·계획 v2대로 섰고 검증도 전부 green이다. 다만 web/ 우주가 비는 경계 입력에서 fail-open이 난다. 그 밖에 첫 실행(web/ 부재) G0 봉쇄, 재승인 절의 `요구 키` 누적 누락, ⑤ add 범위의 config 제외로 결정 16이 무력화되는 문제를 고친 뒤 승인한다

# 로드맵 6a 구현 독립 리뷰 Q (2026-09-27)

- 대상: HEAD `75645801` 기준 미커밋 변경 중 6a 몫이다 — `dddjango-web/**` · `codex-dddjango-web/**`(새 `src/debt.py`·`test/fixtures_debt.sh` 양쪽 포함) · `Makefile` · `AGENTS.md`. 사용자 파일은 읽지 않았다.
- 근거 문서: `design-v5.md` · `plan-v2.md` · `impl-log.md` · `behavior-tests.md`. 행동 시험 원 기록은 `scratchpad/6a-impl/bt/*.jsonl`과 `sds-*/` 사본을 읽기만 했다.
- 실험 위치: scratch `review-Q/exp/`(합성 프로젝트)와 `review-Q/sds/`(현장 `git clone --shared` · `7541aa507`). 현장 원본에는 쓰지 않았다. Serena·Graphify는 쓰지 않았다(지시).
- 저장소 쓰기는 이 파일 하나다. `git status --porcelain` 대조 결과는 리뷰 전과 리뷰 중간이 같다(끝의 확인은 §4).

## §0 검증 실행 결과

| 검증 | 결과 |
|---|---|
| `bash dddjango-web/scripts/test/fixtures_debt.sh` | [실측] PASS 43 · FAIL 0 · exit 0 · 13초 |
| `bash dddjango-web/scripts/test/run_fixtures.sh` | [실측] 픽스처 14파일 실패 0 · exit 0 · 84초(`test_design_evidence` 33 OK 포함) |
| `make verify-web` | [실측] exit 0 · 86초. 픽스처 14 · scripts/assets `diff -rq` · references `cmp` 5종(houserules final 새 행 포함) · REQUEST_GUIDE `cmp` · request-guide 계약 PASS |
| `claude plugin validate dddjango-web --strict` | [실측] ✔ Validation passed(셸 초기화 경고 1줄 `_dotsync_agent_should_manage_launch` — 환경 잡음) |
| byte 미러 | [실측] `scripts/`·`assets/` `diff -rq` 차이 0 · houserules `final.md`·`design-evidence.md`·`REQUEST_GUIDE.md` `cmp` 0 |
| 의미 미러 | [실측] 두 Coordinator에서 6a가 새로 넣은 문장을 플랫폼 표기(`${SKILL_DIR}`·네이티브 셸·`request_user_input`·`$dddjango-web-refactor`)로 정규화해 대조했다. 기존 플랫폼 문형 차이 외에는 0이다. 역할 SKILL 4는 에이전트 추가 문장과 글자 그대로 같다. houserules SKILL은 frontmatter만 다르다. 토큰 13종(`--debt-scan`… `ⓐ′`) 수가 양쪽 일치한다 |
| 현장 사본 `--debt-scan` | [실측] 키 3(WN8 `static/images/` 3건) · 스캔 파일 358 · `dirty` False(미추적 `.dddjango-web/rq` 제외) · 0.7초. `--all`의 구조 발견 3건과 같다 |
| 현장 사본 결정 16 | [실측] 비시안 현재 폴더 + `--diff-base HEAD` → «과거 시안 빌드 17개의 visual 검사 생략(판정 입력 아님)» · exit 0 |
| `make verify` | 돌리지 않았다(지시 범위 밖). core가 봉인 드리프트로 red인 것은 봉인 write 전 예상 red다 |

## §1 설계·계획 커버리지

| 계획 항목 | 구현 위치 | 판정 |
|---|---|---|
| §1 `_project_pkgs` 추출 · `BackstopContext.from_files` | `scripts/src/common.py:506-530` | ✓ `dirs`=조상 · `base_files`=목록 · `added_spans={}` · WS5는 기존 notice로 생략 |
| §1 WP1 중복·WP2 async/defer 사유 상수 + 사유 끝 ` — <src 경로>` | `check_purity.py:52-56·167·231-235` | ✓ |
| §1 우주(`ls-files -co --exclude-standard` − 부재·gitlink·바이트코드) | `debt.py:46-64` | ✓. 단 빈 우주 가드가 없다 → **B1** |
| §1 `DEBT_EXEMPT` 3종(WP1 legacy · WP2 base 로드 태그 · WP5 · core 중복이면 면제 없음) | `debt.py:67-88`(함수 `_exempt` · 규범 인용 docstring) | ✓ 픽스처 D3a/b |
| §1 키·`C<n>`(키 정렬) · JSON 8필드 · exit 0/2/1 | `debt.py:96-158` | ✓ D6·D7 |
| §1 플래그 배타(`--debt-scan`/`--debt-residual` 서로 + `--diff-base`·`--all`·`--only`·`--design-build`, `--json`은 scan 전용) | `backstop.py:163-196` | ✓ D17a–e |
| §2 절 파서(머리 네 형식 · 다른 `## G0`/`## ⓐ` exit 1 · 정형 행 한 번씩) | `debt.py:33-35·173-192·204-218` | ✓ D13a–c. 코드 펜스 안의 머리 오인은 → m1 |
| §2 M = (마지막 G0/재승인 절 ⓐ∪요구) − 그 뒤 재상정 | `debt.py:195-219·256-261` | ✓ 설계대로다. 단 `요구 키` 누적 규칙이 없어 → **M2** |
| §2 전이(둘 다 없음 exit 0 · `debt-g0.json`만 exit 1) · 없는 ID exit 1 · 경로 안전 | `debt.py:222-255` | ✓ D13d–f·D14. 심링크 탈출 exit 1 [실측] |
| §3 결정 16(과거 빌드 상태 루프 삭제 · config 조건만 · 알림 문구) | `backstop.py:102-127·249-253` | ✓ 식별 fail-closed 유지(`:620` 4변이 · `:581` 무수정 통과) |
| §3 `:646` 반전 + `stopped-folder` | `test_design_evidence.py:646-670` | ✓ |
| §4 픽스처 1~17 (+D18 · D1b/c · D13f) | `fixtures_debt.sh` D1–D18 | ✓ 43 단언 |
| §5 Coordinator(모드 판별 · 순서 · step 1 · 4′ 전 항목 · step 6 빚 행 · Phase 1 입력·DR 필수·STOP·단위 확인 · ⑤ · 슬라이스 0 · 잔존 · G2 3행 · Phase 3 · 수정 · 트리비얼 ⓪ · 재개 입구 · 경계 · 라벨 14행 · baseline 3곳 · 산출물·직접 쓰기) | `commands/dddjango-web.md:9·29·31·36·64·68-69·128·134·136·146-156·160·179·187·189·191·193·200·205·211·217-218·222·229·237-241·251·262·266·272` | ✓ 전 항목이 있다. 문면 틈은 → **M1·M3**·m2–m10 |
| §6 에이전트 4 | `coder-web.md:33·57·68` · `design-architect-web.md:31·55` · `design-review-web.md:50` · `discipline-reviewer-web.md:36` | ✓. 입력 배선은 → m8 · coder 문구는 → m6 |
| §7 houserules SKILL(§1 1번·§2·§4) · final §7·§8 · design-evidence · REQUEST_GUIDE §4·§6·§7·§8 | 각 파일 diff | ✓ «이동» 정의(SKILL §1 1번)가 Coordinator `:191`·DR `:36`의 인용과 맞는다 |
| §8 Codex byte·의미 미러 · Makefile `cmp` · AGENTS.md | §0 참조 | ✓ |

- **impl-log §2 편차**: 설계 의도를 깨는 것은 없다.
  - 편차 목록: `스캔 파일 f` 표기 · 트리비얼 `--json` 미사용(트리비얼은 폴더를 만들지 않으니 설계와 같은 뜻) · `ⓕ→(6)` · REQUEST_GUIDE §6 예시 제거 · AGENTS 문장 · D18.
  - 행동 시험 뒤 문면 수정 2건(step 5 착수 금지·평문 폴백 · ⓐ′ 조건)도 설계 안이다. 충분한지는 §3에서 판정한다.

## §2 지적

### blocker

**B1. web/ 우주가 git에 안 보이면 `--debt-scan`이 «빚 0»(exit 0)을 낸다 — fail-open** [실측]

- 위치: `dddjango-web/scripts/src/debt.py:46-64` (+ Codex byte 사본).
- `debt_universe`는 `git ls-files` 결과가 비어도 오류로 보지 않는다. 그래서 web/에 파일이 있는데 git이 그것을 못 보는 경계 입력에서 빈 우주로 «발견 0»을 낸다.
  - E3: 프로젝트가 비git이고, 상위 저장소가 그 폴더를 `.gitignore` 한다. `git rev-parse --is-inside-work-tree`는 `true`라 step 1도 git으로 읽는다.
  - E4: `web`이 심볼릭 링크다(git은 링크 파일 하나로 추적한다).
- 두 경우 모두 결과가 같다.
  ```
  [backstop] 빚 스캔 — 키 0 · 발견 0 · 스캔 파일 0
  exit=0
  ```
  같은 트리를 `--all --only wn8`으로 돌리면 `blocker 1건` · exit 2다.
- 판정 불가인데 exit 0이다. Coordinator `:147`은 이것을 «증거 있는 빚 0»으로 받는다.
  - 발동 조건은 드물다. diff 게이트도 같은 배치에서 눈이 멀어 있다(기존 문제).
  - 그래도 G0의 «빚 0 증거» 자체가 거짓이 되는 경로다.
- 고칠 곳: `debt_universe`. 새 장치 없이 기존 `DebtError`(exit 1) 경로를 쓴다.
  - `(root / 'web').is_symlink()`이면 `DebtError('web/ 가 심볼릭 링크 — git 우주로 스캔할 수 없다')`.
  - `names`가 비었는데 `web/` 아래 실재 일반 파일(`__pycache__`·`.pyc` 제외)이 하나라도 있으면 `DebtError('git 우주가 비었는데 web/ 에 파일이 있다 — web/ 가 git 밖이거나 무시됨')`.
  - 새 러너 계약 픽스처로 E3·E4 두 사례를 exit 1로 고정한다.

### major

**M1. 첫 실행(web/ 부재)이 step 4′에서 G0 blocker로 막힌다 — 지원 경로와 문면이 모순된다** [실측(러너)·문면]

- 러너: 프로젝트에 web/이 없으면 `--debt-scan`이 `빚 스캔 실행 불능 — web/ 없음` · exit 1이다(`debt.py:48-49` · 계획 §1).
- Coordinator가 이 exit 1을 받는 방식이 첫 실행 경로와 부딪힌다.
  - step 4′ `:147`: «증거 없는 «빚 0»은 G0 blocker 다 — «실행 불능»이란 … exit 1 — 비git 포함».
  - 그런데 첫 실행은 정식 경로다: step 1 `:136` (나) «첫 실행(web/ 부재)이면 Phase 2 진입 준비에서 …» · Phase 2 ② `:200`.
  - 첫 실행을 빼 주는 문장이 4′에 없다. 문면대로면 greenfield 요청은 G0를 통과할 수 없다(설계 §7이 G0 blocker로 정한 것은 비git뿐이다).
- 고칠 곳(권고): 러너 쪽이 기록 경로를 한 가지로 유지한다.
  - `debt_universe`: git 저장소 확인(`ls-files` 성공) 뒤 `web/`이 없으면 빈 우주를 돌려준다. `cli_scan`은 `[info] web/ 없음 — 첫 실행(기존 web 코드 없음 = 빚 0)`을 찍고 exit 0.
  - 기존 코드가 없다는 것은 판정 불가가 아니라 확정된 0이다(B1의 «있는데 안 보임»과 다르다).
  - Coordinator `:147`(Codex `:169`)에 «첫 실행(web/ 부재)은 러너가 빚 0(exit 0)을 낸다» 한 구절을 더한다.
  - 그러면 G2 `--debt-residual`도 빈 동결본 + `ⓐ 키: -`로 정상 동작하고, 새 코드의 키는 «G0 에 없던 키»로 보고된다.
  - 픽스처: D18 옆에 «git · web/ 부재 → exit 0 · 키 0» 1건(새 러너 계약).

**M2. 재승인 절의 `요구 키` 누적 규칙이 없어 G0의 요구 키가 잔존 판정에서 빠진다** [실측(러너)·문면]

- 위치: 기록 정형 `:155`(Codex `:177`).
  - `ⓐ 키`에만 «이 요청의 ⓐ 누적 전체 — 재승인 절도 앞 ⓐ를 포함해 다시 적는다»가 있다. `요구 키`는 누적 규칙 없이 `<C<n> 공백 구분 | ->`이다.
  - 러너는 마지막 G0 계열 절만 본다(`debt.py:198-210`).
  - 그래서 G1·Phase 2 재승인 절을 문면대로 쓰면 앞 요구 키가 사라진다. 재승인은 새 단위의 빚 결정이라 `요구 키: -`로 쓰기 쉽다.
- 실험:
  - 절: `## G0 … 요구 키: C1` → `## G0 재승인 … ⓐ 키: C2 · 요구 키: -`. C1(a-b.png)은 미해소, C2는 해소.
  - 결과: `ⓐ 잔존 0 · 요구 잔존 0` · exit 0.
  - 대조(재승인 절 없음): `요구 잔존 1` · exit 2.
- 요구 키는 «G2에서 0이어야 한다»(`:149` (3))인데 G2가 통과한다. 같은 모양으로 ⓐ 누적을 빠뜨려도 exit 0이다(E2 · 설계가 받아들인 Coordinator 의무).
- 고칠 곳(권고): 기존 러너 로직만 바꾼다.
  - `residual_sets`가 마지막 `## G0` 절부터 끝까지의 `G0 재승인` 절을 합집합한다: ⓐ∪요구 = ⋃.
  - 재상정은 마지막 `## G0` 뒤의 모든 `재상정 키`를 뺀다.
  - 한 요청에는 `## G0`가 하나이므로 요청 경계가 유지된다. D9(누적 기록)는 그대로 통과한다.
  - 문면 `:155`의 «누적 전체» 의무는 «앞 절을 다시 적지 않아도 된다»로 풀거나 그대로 둔다.
- 최소 대안: `:155`에 «`요구 키`도 누적 전체»를 더한다.
- 어느 쪽이든 요구 키 탈락 픽스처 1건을 둔다(새 러너 계약).

**M3. ⑤ add 범위가 `.dddjango-web/config.json`을 빼서, config를 바꾼 비시안 레인의 결정 16 생략이 꺼진다(G2 거짓 red)** [실측(러너)·문면]

- 위치: `:200`(Codex `:223`) «`.dddjango-web/` 쪽 add 범위는 이번 실행 폴더뿐이다(`git add -- <산출물 폴더>` …)».
- step 3-1 `:140`은 인자 OpenAPI URL을 `config.json`에 «저장/갱신»한다. 그 변경이 이제 확정적으로 미커밋으로 남는다.
- 결정 16 식별은 `git diff <git_snapshot> -- .dddjango-web/config.json`이 비어야 선다(`backstop.py:121-126`).
- 현장 사본 실험: 비시안 현재 폴더에서 config의 `openapi_url`만 바꾸고(미커밋) `--diff-base HEAD`를 돌렸다.
  - 결과: `blocker 16건 (구조 0 · 시안 16)` · exit 2.
  - config 무변이면 exit 0 + 생략 알림이다.
- 코더가 고칠 수 없는 과거 빌드 증거로 반송 루프에 빠진다. 결정 16의 목적이 이 경로에서 무너진다.
- 같은 괄호의 `git add -- <산출물 폴더>`는 같은 문장의 «민감 raw 증거는 공개 커밋 제외»와도 충돌한다(폴더 통째 add).
- 고칠 말(`:200` · Codex `:223`):
  > `.dddjango-web/` 쪽 add 대상은 이번 실행 폴더의 위 산출물과, 이번 실행이 step 3·5에서 바꾼 `.dddjango-web/config.json`이다 — 경로를 명시해 add 하고(민감 raw 증거 제외), 다른 폴더의 정지 기록·build-state 갱신을 섞지 않는다.

### minor

- **m1. 잔존 파서의 기록 정합 경화 2건** [실측(러너)·추정(발동)]
  - (가) 재사용 폴더에서 새 요청이 G0 절을 빠뜨리면, 앞 요청의 절(다른 `C<n>` 매핑)로 판정한다.
    - E1: `## G0 2026-09-01 …`(`ⓐ 키: -`)가 남은 채 새 스캔(`scanned_at` 09-27 · 새 키 C1)이 들어왔다 → `ⓐ 잔존 0 …` exit 0.
    - 세션 복구가 4′를 다시 돌려 동결본을 바꿔도 같은 틈이 생긴다.
    - 고칠 곳: `cli_residual`이 «마지막 G0 계열 절 시각 ≥ `debt-g0.json` `scanned_at`(분 단위)»을 확인하고, 아니면 exit 1 «이번 요청의 G0 절 없음».
  - (나) 코드 펜스(```) 안에 머리 모양 줄이 있으면 절로 인식된다. 예시로 넣은 `## G0 … ⓐ 키: -`가 앞 절을 덮어 exit 0이 난다.
    - 고칠 곳: `parse_scope`가 펜스 안 줄을 건너뛴다.
- **m2. step 4′ 기록 시점과 G0 배너 «exact command» 문면 정렬** [실측(시험 기록)]
  - `:147` «exact command·exit을 `refactor-scope.md`에 기록한다»에 시점이 없다.
    - W-T2는 4′에 단위만 적었다(원문은 G0 절에서 적음).
    - W-T8은 4′에 `refactor-scope.md`를 전혀 쓰지 않았다. 파일이 준비본 7행 그대로이고 mtime은 준비 시각 15:19다. 옛 `## G0 정지`의 `C1 · ⓐ′` 줄만 새 동결본과 어긋난 채 남았다.
    - G0 정지 절 정형(`:156`)에는 command·exit가 없다. 그래서 4′에서 멈추는 경로는 스캔 증거를 잃는다.
  - `:179`의 배너 `<exact command>`는 W-T1·T2·T5·T8 모두 `…/backstop.py <루트>`로 줄였다.
  - 고칠 말:
    - `:147`: «스캔 직후·빚 질문 전에 스캔 command 원문·exit·스캔 단위·표를 `refactor-scope.md`에 먼저 적는다(`## G0`·`## ⓐ`로 시작하지 않는 머리 — 예: `## 빚 스캔 <시각>`)».
    - `:179`: «`빚: … — --debt-scan exit <값>(명령 원문: refactor-scope.md)`».
    - Codex `:169`·`:202` 같게.
- **m3. 평문 폴백과 대가 정의** [실측(Codex 시험)]
  - `:151`의 폴백은 «같은 선택지와 대가를 평문으로»라서 배너 1행이 열거에 없다. Codex는 배너 1행을 생략했다(편차 ②).
  - «선택지마다 대가 한 줄(ⓐ에는 슬라이스 0 규모)»은 ⓑ·ⓐ′의 대가를 정의하지 않는다. Codex는 ⓑ 대가를 생략했다(편차 ③). Claude는 매번 대가를 지어 냈다.
  - 고칠 말(`:151` · Codex `:173`):
    > 질문 도구를 쓸 수 없으면 같은 배너 1행·선택지·대가 줄을 평문으로 내고 … — 대가: ⓐ 슬라이스 0 규모 / ⓑ 사유·결정 출처가 필요하고 위반은 G2 `legacy 잔존`으로 남아 다음 요청 스캔이 다시 묻는다 / ⓐ′ 이 요청은 G0 정지·정리 착륙 뒤 다시 시작
- **m4. ⓐ′ 조건 문장** [실측(Codex 시험)·추정(재발)]
  - 수정 문장 «… 개명·이동 참조 파일 단위와 슬라이스 0 규모의 단위 수는 세지 않는다»(`:151`)는 원인(규모 단위 수 혼동)을 직접 막는다. 다만 두 가지가 걸린다.
    - 부정형이라 «규모의 단위 수를 세지 말라»로도 읽힌다.
    - 참조 파일 단위 안에 빚 키가 있으면(참조 줄의 WI·WP 발견) 앞 절(«키의 경로가 속한 단위»)과 부딪힌다.
  - Codex 재시험은 하지 않았다.
  - 고칠 말:
    > ⓐ′는 빚 목록 키들의 경로가 2개 이상의 단위에 걸칠 때만 낸다(슬라이스 0 규모의 단위 수로 판정하지 않는다)
  - 스캔 표 아래 `빚 단위 수 n → ⓐ′ 대상/비대상` 한 줄을 적게 한다. W-T1이 이미 자발적으로 이렇게 적었다.
- **m5. 묶음 항목 단위** [실측(시험 기록)]
  - `:150` «그 파일(폴더 발견이면 그 아래 파일 전부)에 걸린 키 전부»는 파일마다 한 항목이다. W-T8(항목 3)이 문면대로였고, W-T1·W-T4(항목 1)는 셋을 한 묶음으로 셌다.
  - 결정 입력은 아니지만, «묶음 안에 하나라도 ⓑ … 이면 그 개명·이동도 뺀다»의 폭과 항목별 미룸 단위가 달라진다.
  - 고칠 말: «개명·이동 대상 파일(폴더 발견이면 그 폴더)마다 한 항목이다».
- **m6. coder-web 슬라이스 0 «URL이 바뀌지 않는다»** [문면·추정]
  - 위치: `agents/coder-web.md:57`(Codex SKILL `:57`). 정적 자산 개명(현장 WN8 3건)은 `/static/…` URL을 바꾼다. 곧이곧대로 읽는 코더는 이를 «동작 불변 불가»로 보고해 재상정으로 보낼 수 있다.
  - 고칠 말: «페이지·fragment 라우트 URL이 바뀌지 않는다 — 정적 자산 경로는 참조를 함께 치환하면 바뀌어도 된다».
- **m7. «첫 슬라이스» 중의** [문면]
  - 위치: `:206`(Codex `:229`). 잔여 범주 귀속의 «첫 슬라이스 선두»가 바로 위 슬라이스 0 줄 뒤에 있어 `slices[0]`로 읽힐 수 있다. 그러면 기능 파일이 빚 슬라이스에 섞인다.
  - 고칠 말: «첫 기능 슬라이스 선두».
- **m8. 리뷰어 입력에 ⓐ 목록이 없다** [문면]
  - design-review-web 점검 11(«G0 ⓐ 키마다 파일 계획이 있는가»)과 DR 경량(«G0 ⓐ 키 밖의 기존 파일 이동»)은 ⓐ 목록이 있어야 판정된다.
  - 그런데 `:188`·`:189`(Codex `:211`·`:212`) 입력에는 architect에게만 준 «`refactor-scope.md` 경로와 스코프 메모의 슬라이스 0 줄»이 없다. 이동 STOP 트리거가 이 리뷰에 기댄다.
  - 고칠 곳: 두 입력 열거에 «(G0 ⓐ가 있으면) 스코프 메모의 슬라이스 0 줄·`refactor-scope.md` 경로»를 더한다.
- **m9. 빚 모드 WS5 notice 문구** [실측(시험 기록)]
  - 빚 스캔 출력의 `[info] WS5(골격 완비) 생략 — git 기준점 없음`(`check_structure.py:165`)은 빚 모드에서는 설계상 정상이다.
  - 그런데 Codex는 이를 이상 징후로 기록했다(W-TC `refactor-scope.md` «실제 git HEAD는 있으므로 이 출력은 향후 백스톱에서 확인한다»).
  - 고칠 곳: `debt.py:scan`이 이 notice를 «기존 단위 골격 미비는 빚 아님(브라운필드 허용)»으로 바꿔 싣는다.
- **m10. 문면 틈 3건** [문면]
  - (가) G1 배너 직전 재승인(`:193`)에서 새 ⓐ가 생겼을 때, 명세 슬라이스 0 절에 더하는 경로(architect 재호출)가 없다. Phase 2는 «추가 커밋»이 있다. 슬라이스 0 끝 잔존이 안전망이긴 하다 → «새 ⓐ는 architect 재호출로 슬라이스 0 절에 더한 뒤 G1 배너를 낸다».
  - (나) 슬라이스 0 끝 `:211` «exit가 아니라 이 값을 본다»에 exit 1의 처리가 없다 → «(exit 1이면 판정 불가 — green 아님)».
  - (다) G2 빚 3행 `:218`에 전이 사례 표기가 없다 → «`빚: 해당 없음(규칙 이전 G0)`». 그래야 4′ 누락이 조용히 지나가지 않는다.

## §3 행동 시험 관찰 판정

- **«규모 항목 수 1 vs 3»**: 비결함 판정은 부분만 맞다.
  - 문면(`:150` 파일마다)대로 센 것은 W-T8(3)이고, W-T1·W-T4(1)가 이탈했다.
  - 결정 입력은 아니지만 재상정 범위와 항목별 미룸 단위에 닿는다 → m5 문면 한 줄 명확화.
- **«배너 빚 1행 명령 축약»**: 비결함 판정은 «원문이 `refactor-scope.md`에 있을 때»만 성립한다.
  - W-T1·T2·T5·T8 모두 축약했으니 `<exact command>` 규칙은 지켜지지 않는 문면이다.
  - W-T8은 파일에도 원문이 없었다 → m2(배너는 exit·기록 경로, 원문은 4′ 기록).
- **«step 4′ 시점 command·exit 기록 유무 차이»**: 결함으로 올린다(m2).
  - W-T2는 단위만 적었고, W-T8은 아무것도 적지 않았다(`sds-W-T8/.dddjango-web/20260927-1000-home-today-card/refactor-scope.md` 7행 준비본 그대로).
  - G0 승인 경로(W-T2b)에서는 G0 절이 결국 담는다. 그러나 4′에서 정지하면 정지 절 정형에 command·exit가 없어 증거가 남지 않는다.
  - W-T8의 «합격»은 «새 스캔» 기준으로는 맞지만 4′ 기록 누락을 함께 적어야 한다.
- **Codex 편차 3건**:
  - ① ⓐ′ 오제시: impl-log §2 끝의 조건 명시는 원인을 직접 막아 대체로 충분하다[추정 — Codex 재시험 없음]. 부정형 문장과 참조 단위 안 빚 키의 충돌이 남아 m4로 재문장하고, `빚 단위 수` 기록 행을 권고한다.
  - ② 배너 1행 생략: 문면 수정이 필요하다. 평문 폴백 문장(`:151`)이 «선택지와 대가»만 열거해 배너 1행을 빠뜨리게 만든다 → m3.
  - ③ ⓑ 대가 줄 생략: 문면 수정이 필요하다. ⓑ·ⓐ′의 대가가 문면에 정의돼 있지 않다(ⓐ만 «슬라이스 0 규모») → m3. Codex는 ⓐ 대가에도 규모를 싣지 않았다(«이미지 3개와 참조 템플릿 2개»뿐).
- **기타 관찰(6a 밖·지적 아님)**:
  - Claude 시험 전부가 `python` 부재로 exit 127을 한 번 겪고 `python3`로 재실행했다(W-T1·T5·T8 기록). Coordinator 전체의 `python …` 관례 문제다. 4′의 «실행 불능 = G0 blocker»와 맞물리지만 모델이 올바르게 재실행했다.
  - `/dddjango-web:refactor`·`$dddjango-web-refactor`는 8개 파일이 참조하는데 아직 없다(6b 몫). 계획 머리의 «6b 착륙 전 push 없음» 조건이 이 커밋에도 그대로 필요하다.

## §4 리뷰 전후 `git status`

- 리뷰 시작 시 `git status --porcelain` 사본(scratch `review-Q/status-before.txt`)과 리뷰 중간 사본이 같다(`diff` 0).
- [실측] 이 파일을 쓴 뒤에도 기본 `git status --porcelain`은 리뷰 전과 같다(`diff` 0). `-uall -- workspace/eval/web-g0-debt` 목록은 14행에서 15행으로 늘었고, 늘어난 행은 `?? workspace/eval/web-g0-debt/review-Q-impl.md` 하나다(디렉터리가 이미 미추적이라 기본 목록에는 안 보인다).
- 대상 변경의 `git diff --stat`도 리뷰 전후가 같다(28 files · +361 · −183). 픽스처·verify-web 실행이 저장소 파일을 바꾸지 않았다.
