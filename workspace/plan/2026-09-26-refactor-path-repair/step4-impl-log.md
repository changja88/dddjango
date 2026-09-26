# 로드맵 4 — 동작 보존 장치(최소판) 구현 기록 (2026-09-27)

설계: `step4-behavior-guard-design-v4.md`(v3 + 검토 G3 필수 수정 + §5 단순화 8 + 결정 9 이름 치환 허용). 검토: G(v1) · G2(v2) · G3(v3).

## 1. 구현 완료 (작업 트리 · 미커밋 · Codex byte 미러 아직)

- `dddjango/scripts/behavior_guard.py`(새) — `open <폴더> --kind test|code` · `close <폴더>`(다음 파견 전까지 반복 · 이력 배열) · `verify <폴더>` · `--repo` · `--python`(동적 마이그레이션 인터프리터 — 기본은 저장소 `.venv`/`venv` 만, 환경을 만들지 않는다).
  - 분류: 테스트 쪽 = `.py` 규칙(test/tests/factories/fake/fakes/fixtures 조각 · test_*.py · *_test.py · conftest.py) ∪ `test_*.py` 를 품은 test/tests 디렉터리 아래 모든 파일 ∪ pytest 설정 절.
  - 0C: 대응표(import 뺀 AST 같은 모듈 쌍 · 정의 이동 · 후속 모듈(옛 파일이 사라진 모듈만) + 파일 경로 · 이름 대응(이름·자기 참조 뺀 AST 같음 — 결정 9)) → 테스트는 import 바인딩 집합 + 본문 AST(docstring 제외 · 보고) 비교 · 옛 판에만 한 번 치환 · 비 `.py` 테스트 파일은 경로 치환만이면 green · 빈 파일 추가는 판정 밖 · pytest 설정 변경 red.
  - 0T: 제품 쪽 변경 red(이동 쌍 새 자리는 분류 중립) · 케이스 이름 다중집합 동일(G1 입장 표 `| remove |` 행의 `path::test` 만 감소 허용).
  - 마이그레이션: 정적 `(apps.py label(Assign·AnnAssign) | 폴더 이름, 파일)` 해시 · 동적 `makemigrations --check --dry-run --skip-checks` 변경 목록 비교(open 미측정 ∧ close No changes = green).
  - 창: `build_anchor` 선행 · 열린 창 있으면 open 거부 · 산출 `<폴더>/behavior/<G0 값>/w<n>-{open,close}.json` · 창 안 first-parent 머지 경로 제외 · 레인 편집과 겹치면 exit 1 · verify = `결정 = ⓐ`(ⓐ′ 제외) 있는데 창 0 이고 `ⓐ 재상정` 없으면 red «창 누락» · 열린 창 red.
  - git diff 는 `--no-renames`(이름 변경 감지가 옛 경로를 숨긴다 — 재생에서 발견).
- `workspace/tools/behavior_guard_fixture_run.py`(새) — 20사례(0C 음성 7 · 0C 양성 7 · 앱 재배치 · 0T 5) + 창 절차(앵커 선행 · 창 누락 · 재open 거부 · 열린 창 · close 재실행 · 두 번째 창 · 재상정 · 머지 제외 · 머지 겹침) **전부 PASS**.
- **현장 재생**(scratch `bg-replay/replay.sh <commit> code` — `bt/sds-main` 의 `--shared` 복제 · 원본 무접촉): 순수 이동 `51374b5e1`·`c4c609c5e`·`e3a26f666`·`902bcd4fc` **green**(테스트 13파일) · `ddf3f260b` 치환 green 28 + red 2(그 커밋에 섞인 새 기능 — 새 테스트·JS 단언 추가 → 옳다) · 계약 변경 `339bc7f17`·`75e3672ab`·`390f57db1`·`543170693`·`62b467b19`·`d6b0fc570`·`839af8a0a` **전부 red**(마이그레이션 정적 red 3건 포함).

## 2. 남은 일 (순서)

1. Codex byte 미러: `cp dddjango/scripts/behavior_guard.py codex-dddjango/skills/dddjango/scripts/`.
2. 봉인·검증 등재: `workspace/tools/manifest_seal.py` 글롭에 새 스크립트·러너가 들어가는지 확인 · `Makefile` verify 세트(아마 verify-base-regen 또는 core)에 `behavior_guard_fixture_run.py` 추가.
3. graph-owned 규범(매핑표 먼저 — 설계 v4 §3):
   - Coordinator(`command-dddjango.ttl`): Phase 2 3번 0T/0C 분할(분류 중립 이동 · 0T 먼저) · 창 절차 3문장(앵커 기록 → `behavior_guard.py open --kind` · 마지막 슬라이스 보고 → close → red 면 철회 → close 재실행 → 다음 파견 · G2 배너 `동작 보존:` 행 = verify `요약:` · exit≠0 이면 G2 금지(7번 목록)) · 병렬 배차는 창 안에서만 · 잇기 재개 때 verify 1회 · 수정 모드 3번 상속 목록 · 경계 절 기계 기록 열거에 `behavior/` · 장치 오탐 = 기존 `ⓐ 재상정` «플러그인 결함».
   - coder(`agent-coder.ttl`): 0C 치환 편집은 소유 무관 coder · 0T 는 ⓐ 수리 테스트 편집(새 case 불가) · 반대쪽 본문 필요 시 편집 말고 보고.
   - discipline-reviewer(`agent-discipline-reviewer.ttl`): close green 치환 hunk 는 «일반 retain 무편집» 예외 · 0T 편집 hunk 대조 · close 보고는 기존 감사(홀리스틱) 입력.
   - 신설/개정 판정 → ISSUED(R-3502~) · render · LEDGER · target-counts · q4 · rulepack · Codex 의미 미러(SKILL · coder · DR).
4. 구현 리뷰(독립 — B-1 비교 규칙 재검토 포함 · 재생 하네스 재사용) → 조감도 행 → `make verify` · `make verify-mutation` → 봉인 write → 커밋 → 봉인 chore.

## 3. 진행 (2026-09-27 · compact 뒤)

- §2-1 Codex byte 미러 완료 · §2-2 봉인 `pipeline` 그룹에 `behavior_guard.py`(design_pregate 옆 — G2 배너 근거) · `verify-base-regen` 에 러너 등재(러너는 pregate_fixture_run 선례대로 봉인 밖).
- §2-3 graph 일괄(`step4-norm-map.md`): 신설 R-3502~R-3508(Coordinator 3 · coder 2 · DR 2) · 제자리 R-3493·R-3494(라벨)·R-3498(문면) · 새 블록 coder s006/b6 · 새 검사기 개체 `c/behavior_guard.py` → gate 90/90 → render 3 → LEDGER 6행 → 계수표(Block 2928 · Expression 3721 · Norm/Work 3517) → q4 → rulepack → Codex 의미 미러 3 · 연쇄 도구 2(`rulepack_smoke` 명부 · `reverse_coverage` 설명 — 새 스크립트 «미설명» red 를 선제 차단).
- 조감도 행 추가. 독립 구현 리뷰 J 진행.

## 4. 구현 리뷰 J 처분 (2026-09-27 · `review-J-step4-impl.md` — blocker 1 · major 7 · minor 13)

| ID | 처분 | 확인 |
|---|---|---|
| J-B1 디렉터리·패키지 이동 거짓 red | **수용** — 전체 경로 정규형 + 되풀이 대응표(구조 쌍·정의·후속·디렉터리·디렉터리+이름) · 설계 v4 §5 | #429 재연(사본 `12d876dcc` · 98경로) **green**(쌍 49 · 디렉터리 4) · 러너 FR1·FR2·FR4·RN1·RN2 green |
| J-M1 이름 문자열 세탁 | **수용** — 짧은 이름 치환 제거 · 이름 뺀 해시는 상수 유지 · `patch.object` 류만 위치 치환 | 러너 `type(e).__name__` red · 무관 "create" green |
| J-M2 수집 밖 이동 | **수용** — 수집 가능성 + 0C 케이스 이름 불변 | 러너 red |
| J-M3 머지 세탁·거짓 red·rebase | **수용(변형)** — 권고의 «곁가지 후손 판별»은 상류가 창 기준에서 갈라진 경우 오판이라, 기존 발주자 승인 머지 목록(`approved-merges.txt` — registry_gate 와 같은 채널)을 쓴다 · 끼운 편집·겹침·조상 아님 | 러너 미승인 red · 승인 green · 곁가지 세탁 red · reset exit 1 · 겹침 exit 1 |
| J-M4 pytest 설정 ⓐ | **수용** — 0T 에서 pytest 절 밖이 같으면 허용(보고) | 러너 green |
| J-M5 remove 칸 | **수용** — owner/path 칸 · `(경로, 이름)` | 러너 red |
| J-M6 unittest 클래스 | **수용** | 러너 red |
| J-M7 감사 반영 창 밖 | **수용** — 규범 «같은 종류 창 재open» | 규범 R-3503 |
| J-m1·m2·m3·m4·m5·m6·m7·m11·m12·m13 | **수용** | 반례 스크립트 재실행 · 규범 구절 |
| J-m8 0T 케이스 개명 | **수용(규범)** — coder «케이스 이름을 바꾸지 않는다» | R-3506 |
| J-m9 사각 목록 | **수용** — docstring 사각 목록 확장 | — |
| J-m10 0T 소유 | **수용** — coder 0T «테스트 소유와 무관» | R-3506 |

- 현장 재생(개정 뒤): 순수 이동 5커밋 green(`51374b5e1` 9 · `c4c609c5e` 1 · `e3a26f666` 2 · `902bcd4fc` 1 · `ddf3f260b` 치환 28 + 섞인 새 기능 red 3) · 계약 변경 7커밋 + 기준 밖 3커밋 전부 red. 한 번 회귀(`e3a26f666` red — 후속 모듈 과반에 상수가 끼어 대응이 상수 모듈로 감)를 잡고 def·class 만 세도록 고쳤다.
- 러너 32사례 + 창 절차(미승인·승인 머지 · 곁가지 세탁 · reset) PASS. 반례 스크립트(리뷰 J 의 거짓 red 11 · 거짓 green 9 · 실패 경로 · 동적 D1~D5) 기대대로 — 남은 green 은 사각(FG6 conftest 범위 · FG7 테스트 settings · FG9 parametrize · D5 open 미측정).
