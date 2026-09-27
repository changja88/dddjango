# 로드맵 6a — dddjango-web 기능 요청 G0 빚 처리 · 구현 계획 v2 (2026-09-27)

> 실행: web 수리 관례대로 한다(작업 트리 그대로 · 브랜치 커밋 없음). 순서는 **사용자 승인** → 구현 → 행동 시험 → 구현 리뷰 → verify → 승인 후 커밋이다. 릴리즈는 로드맵 9(`make release-web`)이고, push 는 릴리즈 때만 한다(마켓이 `ref: main` 이라 push 가 곧 설치본 변경이다 · 6b 착륙 전 push 없음).

- 계획 v1 + 계획 리뷰 P6a(`review-P6a-plan-v1.md` — 수정 후 승인 · major 3 · minor 12). 부록 A 가 처분표다.
- **목표**: web 기능 요청이 dddjango 와 같은 방식으로 기존 구조 빚을 G0 에서 드러낸다. 빚은 ⓐ(슬라이스 0) 또는 출처 있는 ⓑ 로 처리하고, G2 에서 ⓐ 잔존을 판정한다(결정 1-d · B1).
- **구조**: 새 스크립트 없이 기존 러너 `backstop.py` 에 두 플래그(`--debt-scan`·`--debt-residual`)를 더한다. 계산은 새 모듈 `src/debt.py` 한 곳에 둔다. 나머지는 Coordinator·에이전트·스킬 문면 개정과 결정 16 러너 조건 1개 제거다.
- **명세**: `design-v5.md`(정본). 이 계획은 그 설계를 파일·순서·검증으로 옮긴다. 설계와 다르면 설계가 이긴다.
- **커밋 묶음**: 경로를 명시해 add 한다(§10). 사용자 파일(`docs/master.html` · `workspace/eval/field-report-4/…` · `workspace/plan/2026-09-26-refactor-campaign/` · `workspace/plan/2026-09-26-request-guide-audit/synthesis-v2.md`)과 로드맵 5 파일은 넣지 않는다.

## 0. 기준선

- [ ] `make verify-web` green 을 기록한다.
- [ ] 현장 재생 사본 scratch `6a-impl/sds` 를 만든다: `git clone --shared /Users/hyun/Desktop/spring_dream_server`(원본에는 clone 읽기만 한다). HEAD 를 기록한다.

## 1. 러너 — 스캔 (`scripts/src/debt.py` 신설 · `common.py` · `check_purity.py` · `backstop.py`)

- **`common.py`**
  - `project_pkgs` 계산(`common.py:418-423`)을 함수 `_project_pkgs(root)` 로 뽑는다. `build` 와 새 팩토리가 같이 쓴다.
  - `BackstopContext.from_files(root, files) -> BackstopContext` 를 더한다.
    - `files` = web-상대 경로 목록. `dirs` = 그 조상 전부.
    - `git_repo` 는 실측한다.
    - `diff_base=None` · `all_mode=True` · `touched = added = base_files = set(files)` · `added_spans = {}`.
    - `gated=False` 라 `is_added`·`is_touched`·`line_is_added` 가 모두 True 다. `base_files` 는 WP2 legacy 경로 허용(`check_purity.py:131-132`)에만 쓰인다(P6a 확인).
  - `can_detect_new_units` 가 False 라 WS5 는 기존 notice 로 생략된다(확인만 한다).
- **`check_purity.py`**: WP2 사유 가운데 경로가 없는 것(`:226`·`:230` — defer·async·src 형식 계열)의 끝에 ` — <src 경로>` 를 붙인다. 기존 픽스처는 이 문자열을 grep 하지 않는다(P6a 확인 — `grep 'defer가 필요'` 0건). 이렇게 해야 면제를 발견 문자열만으로 판정할 수 있다.
- **`debt.py`**
  - `debt_universe(root) -> list[str]`
    - `git ls-files -co --exclude-standard -z -- web/` → `web/` 접두 제거 → `set` 으로 중복 제거(병합 충돌 시 같은 경로 반복).
    - 작업 트리에서 `is_file()` 가 아닌 것(부재·gitlink)과 `__pycache__/`·`*.pyc` 를 뺀다 → 정렬.
    - git 저장소가 아니거나 `web/` 이 없으면 실행 불능(exit 1)이다.
  - `DEBT_EXEMPT`: 발견 **목록 전체**와 각 발견의 `check_id`·`path`·`message` 만 본다(파일 재독 없음 · 규범 인용 주석).
    - **WP1**: legacy core 경로의 «예약 이름» 발견. 같은 스캔에 WP1 «core 중복» 발견이 없을 때만 뺀다.
    - **WP2**: `base/…` 의 defer·async·src 형식 사유 가운데 끝 경로가 `HTMX_LEGACY` 인 것. 같은 조건(core 중복 없음)일 때만 뺀다.
    - **WP5**: motion.js 판형 드리프트.
  - `scan(root) -> dict`: 우주 → `from_files` → 4패밀리 → 면제 → 키 `"<검사>|<web-상대 경로>"` 집계 → `ids`(키 정렬 순 `C1…`) → 사전.
    - JSON 필드는 설계 §2-1 그대로: `schema · head · dirty · scanned_at · files · ids · findings · counts`.
    - `dirty` 는 `.dddjango-web/` 를 뺀 `git status --porcelain` 판정이다.
  - `write_json(path, data)`: UTF-8 · `ensure_ascii=False` · 키 정렬.
- **`backstop.py`**
  - `--debt-scan [--json <경로>]`. `--json` 은 선택이다(트리비얼은 폴더가 없으면 JSON 없이 요약만).
  - `--debt-scan`·`--debt-residual` 은 서로, 그리고 `--diff-base`·`--design-build`·`--all`·`--only` 와 배타다. 어기면 사용 오류(exit 1)다. `--only` 로 부분 스캔을 동결하는 «범위 좁히기» 구멍을 막는다.
  - 시안 증거 경로를 타지 않는다.
  - 출력: 발견 목록(`C<n> [검사] 경로:행 메시지`) + 요약 1행 `[backstop] 빚 스캔 — 키 k · 발견 n · 파일 f`.
  - exit: 0 = 발견 0 · 2 = 발견 ≥1 · 1 = 실행 불능.
  - 헤더 주석·`_USAGE` 를 갱신한다.

## 2. 러너 — 잔존 (`debt.py` · `backstop.py --debt-residual <폴더>`)

- **`parse_scope(path)`**: `refactor-scope.md` 를 줄 단위로 읽는다.
  - `## ` 로 시작하는 줄은 절을 닫는다.
  - 절 머리 네 형식을 인식한다: `## G0 <시각>` · `## G0 재승인 <시각>` · `## ⓐ 재상정 <시각>` · `## G0 정지 <시각>`. 문자열 상수는 Coordinator 문면(§5)과 같게 둔다.
  - `## G0` 또는 `## ⓐ` 로 시작하지만 네 형식이 아닌 줄 → 판정 불가(exit 1).
  - G0·G0 재승인 절마다 `ⓐ 키:`·`요구 키:` 가 정확히 한 번씩 있어야 한다. 아니면 exit 1 이다. 재상정 절에는 `재상정 키:` 가 정확히 한 번 있어야 한다.
  - 값은 `C<n>` 공백 구분 또는 `-` 다.
- **M 산식**(설계 §3-3): 마지막 `G0`/`G0 재승인` 절의 (ⓐ ∪ 요구) − 그 뒤 재상정 키.
- `C<n>` → 키는 `debt-g0.json` `ids` 로 푼다. 없는 ID 는 exit 1 이다.
- 재스캔 → `debt-g2.json`. 키별 현재 수 > 0 인 것을 센다: `m_a`(ⓐ) · `m_r`(요구) · `X`(= g2 키 − g0 키 · 보고만).
- 요약 1행: `[backstop] 빚 잔존 — ⓐ 잔존 m_a · 요구 잔존 m_r · 재상정 제외 K · G0 에 없던 키 X`.
- **exit**
  - 0 = m_a + m_r = 0.
  - 2 = 그 밖.
  - 1 = 폴더 없음 · 파서 규칙 위반 · `debt-g0.json` 파싱 실패 · **`debt-g0.json` 은 있는데 `refactor-scope.md` 없음**.
  - **전이**: `refactor-scope.md` 와 `debt-g0.json` 이 모두 없으면 `[info] 잔존 판정 해당 없음(규칙 이전 G0)` 과 exit 0 이다.
- 경로 안전: 폴더는 `<루트>/.dddjango-web/` 아래여야 한다(`resolve().is_relative_to`).

## 3. 러너 — 결정 16 (`backstop.py` `current_nondesign_scope`)

- 과거 빌드 상태 루프(`backstop.py:114-122`)를 지운다.
- `.dddjango-web` 변경 검사 루프(`:123-132`)에서 «다른 폴더» 조건을 지우고 `config.json` 변경 조건만 남긴다.
- docstring(`:97` «completed, unchanged history»)을 고친다.
- 알림 문구: `'[info] git_snapshot이 일치하는 현재 비시안 작업 — 과거 시안 빌드 %d개의 visual 검사 생략(판정 입력 아님)'`(결정 번호를 넣지 않는다).
- 식별 조건(유일 snapshot 일치 · `has_design_screen is False` · 현재 폴더가 원본 빌드 아님 · build-state 실재 · config 무변)은 그대로 둔다.
- `test/test_design_evidence.py`
  - `:646` 부근 기대를 반전한다(7 subtests).
  - 반전된 `:646` 에 8번째 시나리오 `stopped-folder`(다른 폴더에 `G0 정지` 절만 있는 미추적 기록 → 생략 유지)를 더한다.
  - `:581`·`:614`·`:620` 은 손대지 않는다(무수정 통과 — P6a 실측 · `:581`·`:620` 은 fail-closed 잠금).
  - W3 원형(`scratchpad/review-W3/scripts16`)과 대조한다: 실패가 `:646` 7 subtests 뿐이어야 한다.

## 4. 픽스처 (`scripts/test/fixtures_debt.sh` 신설 · `run_fixtures.sh` 글롭이 자동 포함)

- `fixtures_backstop.sh` 의 `assert`·`mkproj`·`commit_all` 판형을 복제한다(파일 사이 공유 헬퍼를 새로 만들지 않는다 — 기존 관례).
- 사례. 각 red 에는 양성 대조 짝을 둔다.
  1. 깨끗한 표준 골격 → exit 0 · 키 0.
  2. `.DS_Store`(`.gitignore` 무시) → 키 0.
  3. legacy htmx core 1개 + base 로드 태그(defer 없음) → 키 0. legacy + canonical 공존 → WP1 2키 + WP2 1키.
  4. 기존 단위 골격 미비(WS5 대상) → 키 0.
  5. 인덱스 전용 삭제(작업 트리에서만 삭제) → 유령 키 0 · 오류 0.
  6. 같은 파일 2건 → 키 1 · 수 2.
  7. 파일명 위반 3건(WN8 현장형) → `C1..C3` 결정적(두 번 실행 동일).
  8. 잔존: ⓐ 1 미해소 → exit 2 · 해소 → exit 0.
  9. 재승인 누적(재승인 절에 앞 ⓐ 포함) → 앞 ⓐ 미해소면 exit 2 · 해소되면 exit 0. 러너는 마지막 절만 보므로 누적 의무는 Coordinator 문면이 진다.
  10. 재상정 키 → 제외되어 exit 0.
  11. 요구 키 미해소 → exit 2.
  12. `ⓐ 키: -` · `요구 키: -` → exit 0.
  13. 판정 불가와 전이
      - G0 절 없음 → exit 1.
      - G0 절은 있는데 정형 행 없음 → exit 1.
      - 변형 머리(`## G0 재승인(G1) …`) → exit 1.
      - `debt-g0.json` 만 있음 → exit 1.
      - 둘 다 없음 → exit 0 + 알림.
  14. 없는 `C<n>` → exit 1.
  15. 개명 뒤 잔존 해소 + `--diff-base` 가 새 경로 발견 red(두 게이트 짝).
  16. 참조 줄 WP4 + 개명 → `--diff-base` red(묶음 규칙이 필요한 이유 고정 · 설계 §7 행).
  17. 플래그 배타: `--debt-scan` 과 `--diff-base` · `--only` 동시 → exit 1.
- 정지 폴더 무영향은 §3 의 `stopped-folder` 시나리오로 확인한다(bash 로 시안 빌드 골격을 다시 만들지 않는다).
- 참조 완전성 `git grep` 명령은 러너 밖이라 행동 시험 W-T9 와 현장 재생에서 확인한다.

## 5. Coordinator `dddjango-web/commands/dddjango-web.md`

설계 §1~§6 과 §7 첫 행을 절 단위로 적용한다. 행 번호는 편집 직전에 다시 확인한다. 런타임 본문에 설계 근거·사건 이력·결정 번호 같은 메타 설명을 넣지 않는다.

- **모드 판별**(`:119-127`): 정리 요청 입구 정지 · 섞인 요청 배너 1행 · 불인정 지시 2종.
- **Phase 0**(`:129-166`)
  - step 1(`:131` ①): dirty 판정에서 `.dddjango-web/` 를 뺀다. git init 을 거부한 비git 프로젝트는 4′ 빚 스캔이 실행 불능이라 G0 blocker 라는 대가를 적는다.
  - **step 4′**
    - 언제나 새로 스캔한다.
    - 스코프 단위 5종과 스캔 단위 ①②③(설계 §2-2).
    - 빚 목록 = 스캔 단위 키 + 경로 무관 «미룰 수 없음» 키. 스캔 표 형식 · exact command·exit 를 적는다.
    - **증거 없는 «빚 0» = G0 blocker**. 실행 불능 정의와 «`--diff-base` 게이트로 대체 금지»는 dddjango `:79` 를 이식한다.
    - 질문 순서표.
    - «dirty + ⓐ» 질문과 스태시·커밋 명령(`.dddjango-web` 제외). 이 선택 뒤 4′ 를 다시 돈다.
  - 빚 질문(ⓐ/ⓑ/ⓐ′ · 대가 줄)과 결정 출처(dddjango `:82`·`:83` 이식).
  - **개명·이동 묶음**
    - 묶음 대상 검사: WS1·WS2·WS3·WS4·WS6·WS7·WS8 · WN1~WN8(단 WN6 «VM `…` 대응 미완» 접두 = 생성이라 제외) · WP1.
    - 묶음 아님: WS5·WP5(면제) · WI1~WI4 · WP2~WP4 · WP6.
    - 폴더 발견(`…/` 로 끝남)은 그 접두 아래 키 전부가 묶음이다. 참조 꼬리는 폴더 안 파일마다 만든다.
    - 참조 치환 줄의 WI·WP 발견을 포함한다. 참조 파일 단위는 스캔 단위에 넣는다.
  - 기록 정형: G0 절 · 재승인 절 · `ⓐ 키`(누적)·`요구 키` · 재상정 절 `재상정 키`. 절 머리 문자열은 러너 상수와 같게 쓴다.
  - G0 정지(4′·재승인) 보존과 빚 밖 거부(step 6 배너 거부)의 폐기(지금대로). 요구=기능 조건 셋.
- **라벨 14행**: `:86·131·137·139·144·152·163·190·196·205·215·217·237·240`.
- **산출물 위치** `:33-45` · 직접 쓰기 목록 `:9`·`:244` 에 새 기록물 3종을 넣는다.
- **build-state 스키마** `:55-87` 에 `slices[0]` 슬라이스 0 행을 넣는다.
- **Phase 1**(`:167-177`)
  - 슬라이스 0 절 입력 · 재상정·비위반 이동 STOP 이식 · 슬라이스 0 이 있으면 discipline-reviewer-web 명세 점검 필수.
  - **step 5 G1 배너(`:175`) 앞**: 명세 파일 목록의 단위 ⊆ 스캔 단위인지 확인한다. 밖이면 `debt-g0.json` 에서 그 단위 키를 뽑아 G0 재승인을 한다(motion.js 채택 여부 포함).
- **Phase 2**(`:178-197`)
  - 진입 준비 ⑤(`:180`): 커밋 열거에 `refactor-scope.md`·`debt-g0.json` 을 더하고, add 범위를 이번 실행 폴더로 한정한다. dirty 판정 `.dddjango-web/` 제외.
  - 슬라이스 도출(`:181`): 슬라이스 0 은 기능 앞 · 정수 임계 계수 제외.
  - 슬라이스 0 끝 green 셋: 참조 완전성 명령 원문 포함. 슬라이스 0 끝은 exit 가 아니라 **요약의 `ⓐ 잔존` 값이 0** 인지 본다(요구 키는 기능 슬라이스 몫).
  - 반송·재개봉(`:190`)에서 새 단위가 생기면 재승인하고, 새 ⓐ 는 추가 커밋으로 처리한다.
  - `--debt-residual` 호출 지점(슬라이스 0 끝 · G2 배너 직전 · Phase 3 재실행). **M>0 이면 G2 를 제시하지 않는다.**
  - G2 배너 3행. legacy 잔존 L 은 Coordinator 가 G0 표의 비ⓐ·비요구 행을 `debt-g2.json` counts 로 센다.
  - `:195` 문장과 유령 `backstop-baseline.json` 문장(`:44·68·195`)을 고친다.
- **Phase 3**(`:198-210`): 재실행과 합치기 뒤 보고.
- **수정 모드**(`:211-221`)
  - step 4′ 그대로.
  - step 2 G1′(`:216`) 앞에 같은 단위 확인을 둔다. **ⓐ 가 있으면 G1′ 생략 금지.**
  - `:219` 문장을 고친다.
- **트리비얼**(`:222-231`): ① 앞 스캔 · `:229` ① dirty 판정 `.dddjango-web/` 제외 · 폴더 없으면 JSON 없이 요약만 · 빚 ≥1 승격.
- **재개 입구**(`:22-32`): 수집·검증 전용(코드 무변) 요청은 스캔하지 않는다. `:29` 정체 감사 exit 2 경로의 빚 질문은 새 질문이라고 적는다.
- **경계**(`:242-249`): 위임 불가에 빚 결정 출처 규칙(dddjango 와 동형).

## 6. 에이전트 4 (`dddjango-web/agents/`)

- `design-architect-web.md`: 슬라이스 0 절(키별 파일 계획 · 개명·이동 쌍과 삭제 파일). 기능 파일 목록 밖 기존 파일을 허용한다.
- `coder-web.md`: 슬라이스 0 은 동작 불변이고 기능과 섞지 않는다. 오탐이면 STOP 보고. 참조 치환을 함께 한다.
- `discipline-reviewer-web.md`: 슬라이스 0 이 있으면 명세 점검 필수. 비위반 이동을 보고한다.
- `design-review-web.md`: 슬라이스 0 절 점검 1항.

## 7. 스킬·가이드

- houserules SKILL `:15`·`:24`·`:29`·`:49`: 설계 §7 문면대로 고치고 «이동» 정의 자리를 둔다.
- houserules `references/final.md` §7·§8: 같은 취지로 고친다. `--all` 문장 → `--debt-scan`/`--debt-residual`.
- `implementation-ui/references/design-evidence.md`: 결정 16 생략 조건.
- `REQUEST_GUIDE.md` §4·§6·§7·§8: 설계 §7 행대로 고친다. 상대 링크 금지와 byte 미러 계약을 지킨다.

## 8. Codex 미러 · Makefile · 문서

- `codex-dddjango-web/skills/dddjango-web/scripts/` ← `dddjango-web/scripts/`: byte 복사(`diff -rq` 0).
- byte 미러: houserules final · design-evidence · REQUEST_GUIDE.
- 의미 미러
  - Codex Coordinator: 라벨 14행(`:139·153·159·161·166·174·186·213·219·228·238·240·260·264`) · baseline `:97·121·218` · 결정 16 문장 `:218` · 수정 모드 `:242`.
  - 역할 SKILL 4.
  - houserules SKILL `:14·23·28·48`.
- 토큰 대조(일회성 grep · 양쪽 수 일치): `--debt-scan`·`--debt-residual`·`ⓐ 키:`·`요구 키:`·`재상정 키:`·`G0 재승인`·`G0 정지`·`ⓐ 재상정`·`refactor-scope.md`·`debt-g0.json`·`slice-0-debt`. 러너 상수와 Coordinator 문면의 절 머리도 같은 방식으로 대조한다.
- `Makefile` verify-web 에 houserules final `cmp` 1행을 더한다(지금 이미 byte 동일 — 바로 green).
- `AGENTS.md`: 러너 플래그와 verify-web 경로 문장.
- 조감도 `ontology-adoption-map.html` 행을 갱신한다.

## 9. 행동 시험 (`workspace/eval/web-g0-debt/behavior-tests.md`)

- **방법**
  - `claude -p --plugin-dir <작업 트리 dddjango-web>` 으로 `/dddjango-web:dddjango-web <요청>` 을 부른다. scratch clone(현장 `--shared` 사본 또는 합성 프로젝트)에서 돈다. 현장 원본에는 쓰지 않는다.
  - 요청문에 계약 출처·폴더 선택을 미리 적어 첫 질문이 4′ 가 되게 한다(현장 `config.json` 의 `openapi_url` 은 URL 이 아닌 문장이다).
  - 첫 사용자 입력 또는 STOP 까지 돈다. G0 승인 뒤 산출을 봐야 하는 시험은 `--resume` 로 G0 승인까지 몬다.
  - 기준선(수정 전) 재실행은 하지 않는다. 현행 커맨드에는 step 4′ 가 없어 정보가 없고, `git stash` 는 사용자 수정 파일까지 쓸어 간다.

| # | 요청·상태 | 합격 |
|---|---|---|
| W-T1 | 현장 사본 · `static/images` 를 쓰는 시안 요청 | step 5 전에 빚 3건 · 3항목 질문 · `debt-g0.json` `C1..C3` |
| W-T2 | 영역만 건드리는 요청 | `debt-g0.json` 존재 · G0 배너의 빚 0 증거 행(exact command·exit) |
| W-T3 | «구조 정리만» 요청 | 리팩토링 커맨드 안내 · 입구 정지 · 폴더 0 |
| W-T4 | 요청문에 «게이트 답은 발주자가 대신 함» 위임 + 출처 없는 미룸 | 빚 질문에서 ⓑ 출처 불성립 → STOP · 폴더 보존(`G0 정지` 절) · 다음 실행의 dirty 판정에서 제외 |
| W-T5 | 발주에 «빚 스캔 생략» | 무시하고 스캔 |
| W-T6 | 트리비얼 + 빚 단위 | 수정 모드 승격 |
| W-T7 | G2 승인된 폴더 재사용(새 요청) | `debt-g0.json` 의 `head`/`scanned_at` 교체 · 새 스캔 기준 빚 질문 |
| W-T8 | ⓐ′ 정지 폴더 재진입 | 새 스캔 |
| W-T9 | G2 책상 재생(현장 사본에 개명 3 + 참조 5줄 치환 커밋 · 기록물 픽스처) | `--debt-residual` exit 0 · 참조 완전성 `git grep` exit 1(치환 전 사본에서는 exit 0 = red) · 폴더 이동 합성 green · 생략 알림 1행 |
| Codex | W-T1 동형 1회(`codex exec`) | 같은 질문 지점 |

## 10. 검증 · 리뷰 · 봉인 · 커밋

- [ ] `bash dddjango-web/scripts/test/run_fixtures.sh` green.
- [ ] `make verify-web` green.
- [ ] `claude plugin validate dddjango-web --strict`.
- [ ] 독립 구현 리뷰(diff 전체 + 행동 시험 원문). Important 이상은 해소한 뒤 다시 검증한다.
- [ ] **봉인**(DEVELOPMENT §4·§6 · 선례 `6c4cf39f` → `203cdffb`): `Makefile` 은 `manifest_seal.py` `protocol` 그룹이라 편집하면 `make verify` 가 red 다.
  - 순서: Makefile 편집 → `manifest_seal.py --write`(커밋 직전 마지막 쓰기) → `make verify` green → feat 커밋(`workspace/eval/ab/T2-0b-manifest.json` 포함) → `--write` 재발행 → chore 커밋.
- [ ] 조감도 갱신 → **사용자 승인** → 커밋.
  - 넣을 경로: `dddjango-web/**` 변경 파일 · `codex-dddjango-web/**` 변경 파일 · `Makefile` · `AGENTS.md` · `workspace/eval/web-g0-debt/`(진단·설계 v1~v5·검토 W1~W3·계획 v1·v2·계획 리뷰·행동 시험) · 조감도 · 봉인 파일.
  - 조감도의 앞선 미커밋 행(로드맵 5·6a 설계 단계 행)은 이 작업의 산출이라 함께 넣는다.
  - `refactor-path-repair/` 의 로드맵 5 파일은 로드맵 5 커밋에 넣는다.

## 11. 작업량

- 약 4.5~6.5 작업일(설계 추정 유지 · P6a 판단)
  - 러너 §1~§3 과 픽스처: 2~2.5.
  - 문면 §5~§7: 1.5~2.
  - 미러: 0.5~1.
  - 행동 시험·리뷰: 1~1.5.

## 부록 A. 계획 리뷰 P6a 처분

| P6a | 처분 | 반영 |
|---|---|---|
| M1 로드 태그 = WP2 · 메시지에 경로 없음 | 수용(ⓑ 택 — 문자열만 원칙 유지) | §1 `check_purity.py` 사유 끝 경로 · `DEBT_EXEMPT` WP1·WP2·WP5 · 목록 전체 판정 · 설계 §2-1 표기 정정 |
| M2 §2-2 누락 | 수용 | §5 step 4′ 단위·스캔 단위·빚 목록·빚 0 blocker · G1 배너 앞·G1′ 앞·Phase 2 재승인 · 재개 입구 스캔 제외 · M>0 G2 미제시 · 빚 밖 거부 폐기 · 설계 §7 행 정정 |
| M3 fail-open | 수용 | §2 전이 = 둘 다 없음 · 파서 세 규칙 · §4 13번 · 설계 §5-2 전이 정정 |
| m1 배타 | 수용 | §1 플래그 배타 · §4 17번 |
| m2 산출 계약 | 수용 | §1 `--json` 선택 · 필드 · 키 형식 · `dirty` · 중복 제거·`is_file()` · web/ 부재 |
| m3 행 번호·`:614` | 수용 | §3 `:114-122`·`:123-132`·`:97` · `:614` 무수정 |
| m4 봉인 | 수용(사용자 질문 없음 — DEVELOPMENT 가 답) | §10 봉인 순서 |
| m5 dirty 자리 | 수용 | §5 `:131` ①·`:229` ①·재스캔 |
| m6 잔존 읽기 | 수용 | §5 슬라이스 0 끝 = 요약 `ⓐ 잔존` · L = Coordinator 계산 |
| m7 Phase 2 앵커 | 수용 | §5 `:180` ⑤ 열거·범위 · `:181` 계수 제외 |
| m8 행동 시험 | 수용 | §9 기준선 재실행 걷음 · 요청문 사전 기재 · `--resume` · W-T2·W-T4·W-T7 합격 |
| m9 픽스처 | 수용 | §4 13번 · 정지 폴더 = `:646` `stopped-folder` |
| m10 결정 번호 | 수용 | §3 알림 · §5 원칙 · 설계 §5-2 배너 정정 |
| m11 커밋 묶음·push | 수용(조감도 선행 행은 이 작업 산출 — 질문 불요) | 머리 · §10 경로 명시 |
| m12 비git | 수용 | §5 step 1 대가 · 설계 §7 행 |
| §12 묶음 검사 ID | 채택 | §5 묶음 대상·비대상 목록 |
