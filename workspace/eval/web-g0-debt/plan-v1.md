# 로드맵 6a — dddjango-web 기능 요청 G0 빚 처리 · 구현 계획 v1 (2026-09-27)

> 실행: web 수리 관례대로 한다(작업 트리 그대로 · 브랜치 커밋 없음). 순서는 계획 리뷰 → **사용자 승인** → 구현 → 행동 시험 → 구현 리뷰 → verify → 승인 후 커밋이다. 커밋·릴리즈는 이 계획 범위가 아니다(릴리즈는 로드맵 9 `make release-web`).

**목표**: web 기능 요청이 dddjango 와 같은 방식으로 기존 구조 빚을 G0 에서 드러낸다. 빚은 ⓐ(슬라이스 0) 또는 출처 있는 ⓑ 로 처리하고, G2 에서 ⓐ 잔존을 판정한다(결정 1-d · B1).

**구조**: 새 스크립트 없이 기존 러너 `backstop.py` 에 두 플래그(`--debt-scan`·`--debt-residual`)를 더한다. 그 계산은 새 모듈 `src/debt.py` 한 곳에 둔다. 나머지는 Coordinator·에이전트·스킬 문면 개정과 결정 16 러너 조건 1개 제거다.

**명세**: `design-v5.md`(정본). 이 계획은 그 설계를 파일·순서·검증으로 옮긴다. 설계와 다르면 설계가 이긴다.

**제외 파일**(커밋에서 뺀다 — 사용자 파일): `docs/master.html` · `workspace/eval/field-report-4/…` · `workspace/plan/2026-09-26-refactor-campaign/` · `workspace/plan/2026-09-26-request-guide-audit/synthesis-v2.md`.

## 0. 기준선

- [ ] `make verify-web` green 을 기록한다(바뀐 파일 없음 확인 · `git status --short dddjango-web codex-dddjango-web`).
- [ ] 현장 재생 사본을 준비한다: scratch `6a-impl/sds` = `git clone --shared /Users/hyun/Desktop/spring_dream_server`(원본에는 clone 읽기만 한다). HEAD 를 기록한다.

## 1. 러너 — 스캔 (`scripts/src/debt.py` 신설 · `common.py` · `backstop.py`)

- `common.py`: `BackstopContext.from_files(root, files) -> BackstopContext` 팩토리를 더한다.
  - `files` = web-상대 경로 목록. `dirs` = 그 조상 전부.
  - `project_pkgs` 는 `build` 와 같은 코드로 계산한다(`common.py:419-423` — 함수로 뽑아 두 곳이 같이 쓴다).
  - `git_repo` 는 실측한다. `diff_base=None` · `all_mode=True` · `touched = added = set(files)` · `base_files = set(files)`(WP2 기준 = 스캔 트리) · `added_spans = {}`.
  - `can_detect_new_units` 가 False 라 WS5 는 기존 notice 로 생략된다(설계 §2-1 WS5 와 일치 — 확인만 한다).
- `debt.py`
  - `debt_universe(root) -> list[str]`: `git ls-files -co --exclude-standard -z -- web/` → `web/` 접두 제거 → 작업 트리에 없는 경로·`__pycache__/`·`*.pyc` 를 뺀다 → 정렬. git 저장소가 아니면 실행 불능(exit 1)이다.
  - `DEBT_EXEMPT`: (검사 ID · 판정 함수 · 규범 인용 주석) 목록.
    - WP1 = legacy core 1개와 그 base 로드 태그. legacy 와 canonical 이 함께 있으면 면제하지 않는다.
    - WP5 = motion.js 판형 드리프트.
    - WP2 의 `base_files` 판정은 컨텍스트로 해결되므로 목록 밖이다.
    - 면제 판정은 발견의 `check_id`·`path`·`message` 만 본다. 파일을 새로 읽지 않는다.
  - `scan(root) -> dict`: 우주 → `from_files` → 4패밀리 → 면제 → 키 `(check_id, path)` 집계 → `ids`(키 정렬 순 `C1…`) → JSON 사전.
  - `write_json(path, data)`: UTF-8 · `ensure_ascii=False` · 키 정렬.
- `backstop.py`: `--debt-scan` + `--json <경로>` 파싱.
  - `--debt-scan` 은 `--diff-base`·`--design-build`·`--all` 과 함께 쓸 수 없다(사용 오류 exit 1).
  - 시안 증거 경로를 타지 않는다.
  - 출력: 발견 목록(`C<n> [검사] 경로:행 메시지`) + 요약 1행 `[backstop] 빚 스캔 — 키 k · 발견 n · 파일 f`.
  - exit: 0 = 발견 0 · 2 = 발견 ≥1 · 1 = 실행 불능.
- 헤더 주석·`_USAGE` 를 갱신한다.

## 2. 러너 — 잔존 (`debt.py` · `backstop.py --debt-residual <폴더>`)

- `parse_scope(path)`: `refactor-scope.md` 를 줄 단위로 읽는다.
  - 절 머리 `## G0 <시각>`·`## G0 재승인 <시각>`·`## ⓐ 재상정 <시각>`·`## G0 정지 <시각>` 을 인식한다. 머리 수준과 정확한 표기는 Coordinator 문면(§5)과 같은 문자열 상수로 둔다.
  - 정형 행은 절 안의 `ⓐ 키: …`·`요구 키: …`·`재상정 키: …` 다. 값은 `C<n>` 공백 구분 또는 `-` 다.
- M 산식은 설계 §3-3 그대로다: 마지막 `G0`/`G0 재승인` 절의 (ⓐ ∪ 요구) − 그 뒤 재상정 키.
- `C<n>` → 키는 `debt-g0.json` `ids` 로 푼다. 없는 ID 는 판정 불가(exit 1)다.
- 재스캔 → `debt-g2.json`. 키별 현재 수 > 0 인 것을 센다: `m_a`(ⓐ) · `m_r`(요구) · `X`(= g2 키 − g0 키 · 보고만).
- 요약 1행 `[backstop] 빚 잔존 — ⓐ 잔존 m_a · 요구 잔존 m_r · 재상정 제외 K · G0 에 없던 키 X`.
- exit
  - 0 = m_a + m_r = 0.
  - 2 = 그 밖.
  - 1 = 폴더 없음 · `refactor-scope.md` 는 있는데 G0 절·정형 행 없음 · `debt-g0.json` 없음·파싱 실패.
  - **전이**: `refactor-scope.md` 가 없으면 `[info] 잔존 판정 해당 없음(규칙 이전 G0)` 과 exit 0.
- 경로 안전: 폴더는 `<루트>/.dddjango-web/` 아래여야 한다(`resolve().is_relative_to`).

## 3. 러너 — 결정 16 (`backstop.py` `current_nondesign_scope`)

- 과거 빌드 상태 루프(`prior.get('has_design_screen')…slices` — 현 `:112-119`)를 지운다.
- `.dddjango-web` 변경 검사 루프에서 «다른 폴더» 조건을 지우고 `config.json` 변경 조건만 남긴다.
- 알림 문구에서 «완료된»을 지운다: `'[info] git_snapshot이 일치하는 현재 비시안 작업 — 과거 시안 빌드 %d개의 visual 검사 생략(결정 16 — 판정 입력 아님)'`.
- 식별 조건(유일 snapshot 일치 · `has_design_screen is False` · 현재 폴더가 원본 빌드 아님 · build-state 실재 · config 무변)은 그대로 둔다.
- `test/test_design_evidence.py`
  - `:646` 부근 기대를 반전한다(과거 빌드 미완료·변경이어도 생략 — 7 subtests).
  - `:614` 는 알림 문구 기대를 갱신한다.
  - `:581`·`:620` 은 손대지 않는다(fail-closed 잠금).
  - W3 원형(`scratchpad/review-W3/scripts16`)과 결과가 같은지 대조한다.

## 4. 픽스처 (`scripts/test/fixtures_debt.sh` 신설 · `run_fixtures.sh` 글롭이 자동 포함)

- `fixtures_backstop.sh` 의 `assert`·`mkproj`·`commit_all` 판형을 복제한다(파일 사이 공유 헬퍼를 새로 만들지 않는다 — 기존 관례).
- 사례. 각 red 에는 양성 대조 짝을 둔다.
  1. 깨끗한 표준 골격 → exit 0 · 키 0.
  2. `.DS_Store`(`.gitignore` 무시) → 키 0.
  3. legacy htmx core 1개 + base 로드 태그(defer 없음) → 키 0. legacy + canonical 공존 → WP 키 ≥1.
  4. 기존 단위 골격 미비(WS5 대상) → 키 0.
  5. 인덱스 전용 삭제(`git rm --cached` 없이 작업 트리에서만 삭제) → 유령 키 0 · 오류 0.
  6. 같은 파일 2건 → 키 1 · 수 2.
  7. 파일명 위반 3건(WN8 현장형) → `C1..C3` 결정적(두 번 실행 동일).
  8. 잔존: ⓐ 1 미해소 → exit 2 · 해소 → exit 0.
  9. 재승인 누적(재승인 절에 앞 ⓐ 포함) → 앞 ⓐ 미해소면 exit 2 · 해소되면 exit 0. 러너는 마지막 절만 보므로 누적 의무는 Coordinator 문면이 진다.
  10. 재상정 키 → 제외되어 exit 0.
  11. 요구 키 미해소 → exit 2.
  12. `ⓐ 키: -` · `요구 키: -` → exit 0.
  13. G0 절 없음 → exit 1 · `refactor-scope.md` 없음 → exit 0 + 알림.
  14. 없는 `C<n>` → exit 1.
  15. 개명 뒤 잔존 해소 + `--diff-base` 가 새 경로 발견 red(두 게이트 짝).
  16. 참조 줄 WP4 + 개명 → `--diff-base` red(묶음 규칙이 필요한 이유 고정).
  17. `--debt-scan` 과 `--diff-base` 동시 → exit 1.
  18. 정지 폴더(`G0 정지` 절만 있는 미추적 폴더)가 있어도 비시안 레인 생략이 유지된다.
- 참조 완전성 `git grep` 명령은 러너 밖이라 픽스처가 아니라 행동 시험 W-T9 와 현장 재생(§9)에서 확인한다.

## 5. Coordinator `dddjango-web/commands/dddjango-web.md`

설계 §7 첫 행을 절 단위로 적용한다. 행 번호는 편집 직전에 다시 확인한다.

- 모드 판별(`:119-127`): 정리 요청 입구 정지 · 섞인 요청 배너 1행 · 불인정 지시 2종.
- Phase 0(`:129-166`)
  - step 4′ 삽입과 질문 순서표. step 4′ 는 언제나 새로 스캔한다.
  - dirty 판정에서 `.dddjango-web/` 를 뺀다(`:67`·`:180`). 스태시·커밋 명령을 적는다.
  - 빚 질문(ⓐ/ⓑ/ⓐ′ · 대가 줄)과 결정 출처(dddjango `:82`·`:83` 이식)를 넣는다.
  - 개명·이동 묶음(검사 ID 목록 — 파일·폴더 이름 검사와 배치 검사를 계획 리뷰에서 확정)을 넣는다.
  - 기록 정형(G0 절 · `ⓐ 키`·`요구 키` · 재상정 절 `재상정 키`)을 넣는다.
  - G0 정지(4′·재승인)와 요구=기능 조건 셋을 넣는다.
- 라벨 14행: `:86·131·137·139·144·152·163·190·196·205·215·217·237·240`.
- 산출물 위치 `:33-45` · 직접 쓰기 목록 `:9`·`:244` 에 새 기록물 3종을 넣는다.
- build-state 스키마 `:55-87` 에 `slices[0]` 슬라이스 0 행(계수 제외 도출 규칙)을 넣는다.
- Phase 1 `:167-177`: 슬라이스 0 절 입력 · 재상정·비위반 이동 STOP 을 이식하고, 슬라이스 0 이 있으면 discipline-reviewer-web 명세 점검을 필수로 한다.
- Phase 2 `:178-197`
  - 슬라이스 0 위치·커밋 분리와 끝 green 셋(참조 완전성 명령 원문 포함)을 넣는다.
  - 새 ⓐ 는 추가 커밋으로 처리한다.
  - `--debt-residual` 호출 지점과 G2 배너 3행을 넣는다.
  - ⑤ add 범위 = 이번 실행 폴더.
  - `:195` 문장과 유령 `backstop-baseline.json` 문장(`:44·68·195`)을 고친다.
- Phase 3 `:198-210`: 재실행과 합치기 뒤 보고를 넣는다.
- 수정 모드 `:211-221`(`:219` 문장)과 트리비얼 `:222-231` 을 고친다. 재개 입구 `:22-32`(`:29` 새 질문)를 고친다.
- 경계 `:242-249`: 위임 불가에 빚 결정 출처 규칙을 넣는다(dddjango 와 동형).
- 런타임 본문에 설계 근거·사건 이력 같은 메타 설명을 넣지 않는다(작성 원칙).

## 6. 에이전트 4 (`dddjango-web/agents/`)

- `design-architect-web.md`: 슬라이스 0 절(키별 파일 계획 · 개명·이동 쌍과 삭제 파일)을 넣는다. 기능 파일 목록 밖 기존 파일을 허용한다.
- `coder-web.md`: 슬라이스 0 은 동작 불변 · 기능과 섞지 않음 · 오탐 → STOP 보고 · 참조 치환을 함께 한다.
- `discipline-reviewer-web.md`: 슬라이스 0 이 있을 때 명세 점검 필수 · 비위반 이동을 발견하면 보고한다.
- `design-review-web.md`: 슬라이스 0 절 점검 1항.

## 7. 스킬·가이드 (`dddjango-web/skills/…` · `REQUEST_GUIDE.md`)

- houserules SKILL `:15`·`:24`·`:29`·`:49`: 설계 §7 문면대로 고친다. «이동» 정의 자리를 둔다.
- houserules `references/final.md` §7·§8: 같은 취지로 고친다. `--all` 문장 → `--debt-scan`/`--debt-residual`.
- `implementation-ui/references/design-evidence.md`: 결정 16 생략 조건.
- `REQUEST_GUIDE.md` §4·§6·§7·§8: 설계 §7 행대로 고친다. 상대 링크 금지와 byte 미러 계약을 지킨다.

## 8. Codex 미러 · Makefile · 문서

- `codex-dddjango-web/skills/dddjango-web/scripts/` ← `dddjango-web/scripts/`: byte 복사(`diff -rq` 0).
- byte 미러: houserules final · design-evidence · REQUEST_GUIDE.
- 의미 미러: Codex Coordinator(라벨 14행 · backstop-baseline `:97·121·218` 포함) · 역할 SKILL 4 · houserules SKILL. 새 토큰(`--debt-scan`·`--debt-residual`·`ⓐ 키:`·`요구 키:`·`재상정 키:`·`G0 재승인`) grep 수를 양쪽에서 대조한다.
- `Makefile` verify-web: houserules final `cmp` 1행을 더한다.
- `AGENTS.md`: 러너 플래그와 verify-web 경로 문장을 고친다.
- 조감도 `ontology-adoption-map.html` 행을 갱신한다.

## 9. 행동 시험 (`workspace/eval/web-g0-debt/behavior-tests.md`)

- 방법: `claude -p --plugin-dir <작업 트리 dddjango-web>` 으로 `/dddjango-web:dddjango-web <요청>` 을 부른다. scratch clone(현장 `--shared` 사본 또는 합성 프로젝트)에서 첫 사용자 입력 또는 STOP 까지만 돌린다. 현장 원본에는 쓰지 않는다.
- 각 시험은 수정 전 작업 트리(stash 한 기준선 사본)로도 한 번 돈다. 기존도 통과하면 개선을 주장하지 않는다.

| # | 요청·상태 | 합격 |
|---|---|---|
| W-T1 | 현장 사본 · `static/images` 를 쓰는 시안 요청 | step 5 전에 빚 3건 · 3항목 질문 · `debt-g0.json` `C1..C3` |
| W-T2 | 영역만 건드리는 요청 | 빚 0 · exact command·exit 기록 |
| W-T3 | «구조 정리만» 요청 | 리팩토링 커맨드 안내 · 입구 정지 · 폴더 0 |
| W-T4 | 빚 질문에 출처 없는 ⓑ | STOP · 폴더 보존(`G0 정지` 절) · 다음 실행 dirty 판정에서 제외 |
| W-T5 | 발주에 «빚 스캔 생략» | 무시하고 스캔 |
| W-T6 | 트리비얼 + 빚 단위 | 수정 모드 승격 |
| W-T7 | G2 승인된 폴더 재사용(새 요청) | 새 스캔 · 새 G0 절 |
| W-T8 | ⓐ′ 정지 폴더 재진입 | 새 스캔 |
| W-T9 | G2 책상 재생(현장 사본에 개명 3 + 참조 5줄 치환 커밋 · 기록물 픽스처) | `--debt-residual` exit 0 · 참조 완전성 `git grep` exit 1(치환 전 사본에서는 exit 0 = red) · 폴더 이동 합성 green · 생략 알림 1행 |
| Codex | W-T1 동형 1회(`codex exec`) | 같은 질문 지점 |

## 10. 검증 · 리뷰 · 마무리

- [ ] `bash dddjango-web/scripts/test/run_fixtures.sh` green.
- [ ] `make verify-web` green.
- [ ] `make verify` green.
- [ ] `claude plugin validate dddjango-web --strict`.
- [ ] 독립 구현 리뷰(diff 전체 + 행동 시험 원문). Important 이상은 해소한 뒤 다시 검증한다.
- [ ] 봉인: web 은 `manifest_seal.py` 대상인지 확인한다(DEVELOPMENT §4). 대상이면 `--write` 를 커밋 직전 마지막 쓰기로 하고, 재발행은 별도 chore 커밋이다.
- [ ] 조감도 갱신 → 사용자 승인 → 커밋. 이 로드맵 문서들(`web-g0-debt/` 전부)을 함께 넣고, 제외 파일은 뺀다.

## 11. 작업량

- 설계 추정 4.5~6.5 작업일: 러너 §1~§3 과 픽스처 2~2.5 · 문면 §5~§7 1.5~2 · 미러 0.5~1 · 행동 시험·리뷰 1~1.5.

## 12. 계획 리뷰에 부탁할 것

- `DEBT_EXEMPT` 판정이 발견 문자열만으로 결정적으로 서는가(WP1 로드 태그 · legacy/canonical 공존).
- 개명·이동 묶음을 부르는 검사 ID 목록(파일·폴더 이름 · 배치)이 무엇이어야 하는가 — 실물 검사기에서 뽑아 확정한다.
- `parse_scope` 가 Coordinator 문면의 절 머리·정형 행과 같은 문자열을 쓰는가(한쪽만 바뀌면 exit 1 로 드러나는가).
- 결정 16 개정 뒤 `:581`·`:620` 이 정말 그대로 통과하는가.
- Codex 미러 범위의 누락.
