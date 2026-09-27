# 로드맵 6b 구현 기록 (2026-09-27 ~)

- 계획: `plan-v2.md` · 설계 `design-v5.md`. 사용자 구현 승인(09-27 «승인 — 구현 시작»).
- scratch: `/private/tmp/claude-501/-Users-hyun-Desktop-dddjango/ed01792c-e467-4a58-a794-ed16237ffb9e/scratchpad/6b-impl/`.

## §0 기준선

- HEAD `c9fcadff` · `make verify-web` green · `fixtures_debt.sh` 55/55 · `claude plugin validate dddjango-web --strict` 통과.
- 현장 사본 `6b-impl/sds`(`git clone --shared`) HEAD `1dd1f09f8`. 현장 python `/Users/hyun/Desktop/spring_dream_server/.venv/bin/python`.
- `make -n testp`:
  - `uv run --no-env-file pytest -c pyproject.toml --postgresql-exec /opt/homebrew/opt/postgresql@18/bin/pg_ctl -rF -n0 --maxfail=1 --strict-markers -m postgresql && \`
  - `uv run --no-env-file pytest -c pyproject.toml -p no:pytest_postgresql -rF -n auto --maxfail=1 --strict-markers -m "not postgresql"`

## §1 구현 진행

| 단계 | 상태 | 비고 |
|---|---|---|
| §7 전수 분류 | 완료 | `phrase-classification.md`(161줄 분류 · 닫힌 목록 32어구 · 술어 적중 33문장 · `할 수 있다` 적용 문서 9 · F1~F9) |
| §1 입구 · §2 일반 절 · §3 끝 절 | 완료 | `commands/refactor.md` · Coordinator 일반 절 27곳(스크립트 scratch `6b-impl/coord_edit.py`) · 끝 절 «리팩토링 모드» 14문단 · Codex 입구 스킬 · Codex Coordinator 25곳 + 끝 절(`coord_edit_codex.py`) |
| §6 에이전트 | 완료 | 에이전트 4(`agent_edit.py`) · Codex 역할 SKILL 4(`agent_edit_codex.py`) |
| §8 문서 · §9 Makefile | 완료 | REQUEST_GUIDE §6·§7(+Codex byte) · README · AGENTS(검사 26종) · plugin.json 2 · houserules §7(+Codex byte) · 6a `behavior-tests.md` 정정 메모 · verify-web self-test 2행 |
| verify | green | `make verify-web` 전부 green(픽스처 16파일 · self-test 양 플랫폼 red 0 · byte 미러 · 가이드 계약) · `claude plugin validate dddjango-web --strict` 통과 |
| §5 도구 | 완료 | `scripts/refactor_audit.py`(약 1,200행 · plan · `--against` · `--names` · check · check-verdict · residual · self-test) · `fixtures_refactor_audit.sh` 55(A~J · 합성 플러그인 루트로 판정 문장 고정) · self-test = 점검 절 62 실재 · 극성 표본 10 |
| §4 러너 | 완료 | `debt.py`(`--refactor` 스캔 · WP1 조건부 · `mode` · M 행 · `residual_m_sets` · `parse_spec_pairs` · `module_of`·`tail_of`·`reference_lines`·`is_test_path` · `REF_PATHSPEC`·`SPEC_SLICE0_HEAD` 상수) · `check_structure.run_skeleton` · `src/subst.py`(새 모듈) · `backstop.py` 인자·배타 · `fixtures_debt.sh` 55 → 80(D24~D29) · `fixtures_subst.sh` 29(S1~S13) · 현장 사본 리팩토링 스캔 = 기본 스캔과 같은 3키 |

## §2 계획 대비 편차

1. **`--subst-check` 는 `debt.py` 가 아니라 새 모듈 `src/subst.py`** 에 둔다. 빚 스캔·잔존(키 동결·접기)과 치환 확인(쌍·ast 대조)은 바뀌는 이유가 다르다. 공통 함수(`parse_spec_pairs`·`tail_of`·`module_of`·`is_test_path`)는 `debt.py` 한 곳에 두고 import 한다.
2. **경로 맞바꿈(두 파일 이름 교환)은 쌍이 생기지 않는다.** git 은 두 경로가 모두 남는 교환을 개명으로 보지 않는다(`-M`·`-B -M` 모두 `M` 둘 — scratch 실측). 그래서 교환 치환은 red 로 떨어진다(fail-closed). 설계 W6-T8 «교환 쌍 green»은 `이름:` 쌍 교환(동시 치환)으로 확인하고(S5a), 경로 교환 red 를 S5b 로 고정했다.
3. **`reference_lines` 는 `--untracked -I` 로 돈다.** 미추적·비무시 파일의 참조도 소유 판정에 넣고(fail-closed — 경계 교차가 늘 뿐), 이진 파일 적중 줄은 뺀다. pathspec 은 `REF_PATHSPEC`(Coordinator 문면의 명령과 같은 문자열)이다.
4. **리팩토링 스캔의 WS5 메시지는 «신규 … 골격 미완비»** 문구를 그대로 쓴다(`check_structure` 메시지 무변 — 게이트 모드와 같은 문자열). 키·판정에는 영향이 없다.
5. **적용 한정 어구는 도구 상수가 아니라 설치본 Coordinator 문면에서 읽는다.** 계획 §5 는 상수 + self-test 대조였다. web 은 산문 정본이라 원문이 Coordinator 적용 범위 규범 문단 한 곳이고, 실행 때 그 문단의 «…» 목록을 읽으면 드리프트가 생길 자리가 없다. 목록이 비거나 문단이 없으면 실행 불능(exit 1 · fail-closed)이다. self-test 는 목록 존재와 맨 낱말(«기존»·«신규»·«새»·«레거시») 금지를 본다. 긍정 술어·부정형은 상수 + 극성 표본 그대로다.
6. **리뷰어 표·판정 표의 키 문자열은 `\|` 로 이스케이프한다**(`WN8\|static/images/a.png`). 마크다운 표 칸 구분자와 키의 `|` 가 겹친다 — 표 파서는 `\|` 를 칸 안 문자로 읽는다. 에이전트 문면(단위 점검 산출 표 · 판정 표)에 이 표기를 적는다.
7. **REQUEST_GUIDE §7 에 대리 요청 표지 문장을 둔다.** 설계 §10 7행은 «dddjango 배포 가이드 §7 에 없다»며 두지 않기로 했는데, 현재 dddjango 가이드 §7(`dddjango/REQUEST_GUIDE.md:202-205`)에는 같은 문장이 있다. 전제가 틀렸으므로 결정 1-d(dddjango 와 같은 방식)대로 web 에도 둔다.
8. **§7 분류 발견 처분**(`phrase-classification.md` §7):
   - F1(major — 에이전트 문면이 슬라이스 0 을 `C` ⓐ 로만 읽음): 적용 범위 규범 문단에 «슬라이스 0 ⓐ = `C<n>` ⓐ ∪ `M<n>` ⓐ · 그 이동·개명은 승인 목록» 1문장(파견 원문으로 닿는다).
   - F2: ⑵ 문장을 web 판(감사 범위·구현 코드·구현 표기·«설계만 본다»)으로 · design-review-web `## 입력` 의 «구현 코드를 보지 않는다» 에도 ⑵ 1구.
   - F3: 긍정 술어 5개(`위반이 아니(다|며)`·`정당하다`·`강제하지 않는다`·`충분하다`·`허용 목록`) · 술어 앞 «만» 무효 규칙 · 극성 표본 6개 추가.
   - F4: 도구는 처음부터 공백 없는 정규화 본문에 공백 없는 술어를 걸어 같은 효과다(변경 없음).
   - F5: `(쓸|둘|할) 수 있다` 적용 문서 9개(cleancode 제외) = `CAN_DOCS`.
   - F7: 끝 절 G0 에 «미룰 수 없음의 해로움 = 대상 단위의 현재 동작·안전» 1구 · 머리 문단 «바꾸는 곳»에 추가.
   - F6(WP1·WP2 legacy 쌍을 겨누는 의미 항목의 이중 질문 — fail-closed · 현장 0) · F8(생성 금지 조항의 오탐 해석 — 기계 관문 밖) · F9(dddjango 목록의 같은 공백 — 범위 밖): 기록만 한다. 구현 리뷰 관찰 항목.

9. **편차 기록 누락 3건(리뷰 R m8)**:
   - (가) 계획 §3-5 의 «네 판정 이름 · 이중 범위 · 키 소속 1~4(폴더·빈 경로 키)»는 끝 절 문면이 아니라 도구 산출 `plan.md` 에만 있다. Coordinator 는 `plan.md` 를 읽어 쓰므로 문면에 되풀이하지 않는다.
   - (나) 계획 §6 «모두» 1행이 `coder-web.md:34`·`design-architect-web.md:32` 에서 «(리팩토링 모드면)» 조건 불릿 안에 있다(효과 같음).
   - (다) Codex Coordinator 조사 «`dddjango-web` 스킬 으로» 2곳 → «스킬로»(리뷰 R 뒤 고침).
10. **F4 처분 정정**: §2 8 의 «F4: 공백 없는 정규화 본문에 공백 없는 술어를 걸어 같은 효과»는 사실이 아니었다(리뷰 R m6 — «예외 다른»이 `예외다` 로 붙는 낱말 경계 넘는 적중 · «무방하지 않다» 유효). 분류 표 F4 의 원래 처분대로 술어·부정형·무효 접미·«만» 판정을 공백 한 칸 접은 문장에 건다(§3 m6).
11. **G0 정지 재개 조건 ①~③ 을 `plan --against` 안으로**(행동 시험 W6-T10b): 설계 §3-4 는 네 조건을 Coordinator 셸 명령으로 적었는데, 실하네스에서 ② `git diff --quiet <HEAD> -- <범위 파일…>` 의 셸 조립이 두 번 잘못된 exit 0 을 냈다(경로에 괄호 · zsh 무분할 → pathspec 무적중 = fail-open). 같은 조건을 기존 도구 `--against` 가 git 인자 목록으로 본다(① 기록 plan `범위 미커밋 변경 0` · ② 기록 HEAD 이후 범위 파일 무변(작업 트리 포함) · ③ 단위·범위 미추적 0 · ④ 여섯 목록). 새 장치가 아니라 셸에 맡기던 조건을 이미 부르는 도구로 옮긴 것이다. 픽스처 B3(목록 같고 내용만 바뀜 — ② 만 잡음 · 변이 red)·B4·B5·B6 · 재확인 W6-T10b2.

## §3 구현 리뷰 R 처분 (09-27 · `review-R-impl.md` — 수정 후 승인 · blocker 1 · major 4 · minor 12)

- 지적마다 코드·문면을 읽어 재현한 뒤 처분했다. 고친 코드는 해당 픽스처를 더하고 **고침을 되돌린 사본으로 변이 시험**을 해 그 픽스처가 떨어지는지 확인했다(scratch `6b-impl/mut/`).

| ID | 처분 | 고친 곳 · 확인 |
|---|---|---|
| B1 | 수용 | `refactor_audit.py` `_carried` 는 같은 `의미 audit`·`git_snapshot` 판의 `result.json` 만 잇는다(`result.json` 에 `audit`·`snapshot` 기록 · 옛 판형은 잇지 않음 = fail-closed). 픽스처 K1(재사용 폴더 새 점검 → 결정적 잔존 exit 2). 변이(결속 끔) → K1 red |
| M1 | 수용 | `check-verdict` exit 0 판마다 확정 표를 `verdict-final.md` 로 쓴다(`--final` 재분류 포함 · red 판은 쓰지 않음). `residual` 은 그 파일을 읽는다(없으면 exit 1). Coordinator 양 플랫폼: 도구 산출 목록 · 잇기 · R3 문단 1문장. 픽스처 G16b · G20 · G20b · G21 · G21b · K2 · K3. 변이(`verdict.md` 읽기) → K2 red |
| M2 | 수용 | `src/subst.py` `--except` 값은 기준·대상 트리 어느 쪽에 있는 파일(blob)이어야 한다(폴더·글롭 exit 1) · pathspec `:(exclude,literal)`. 픽스처 S10e·f·g. 변이 → S10e(exit 0 — 폴더 누수 재현)·f·g red |
| M3 | 수용 | `_load_rows` 는 `web/…:<행>` 위치 토큰이 있는 짧은 행을 버리지 않고 «칸 부족» 인용 불일치로 올린다(보조 표만 건너뜀). 픽스처 F3·F3b. 변이 → red |
| M4 | 수용 | 줄 편집 (라) «(가)·(나)·(다)·참조 치환 줄 위의 G0 승인 `M<n>` ⓐ 항목 — 판정 표 `파일:행 목록` 의 그 줄만, 그 항목의 교정만» · (나) 괄호에 (라) 지시 · G1 스캔 단위 확인 ② 목록 · DR 9번(양 플랫폼). T0b 실하네스에서 실재(M4 `special_button.html:12` 주석 단서 삭제 — Coordinator 가 문면 밖 범주를 지어 통과시켰다) |
| m1 | 변경 없음 | 첫 호출 요약이 «M_m 미정 — --finalize <시각>»을 적고 Coordinator G2 문단이 `--finalize` 로 확정한다고 정한다. T0b 실하네스도 그대로 `--finalize` 까지 갔다 |
| m2 | 수용(제외만) | 제외 근거 문서를 규칙 문서(`skills/`·`agents/`)로 한정한다 — Coordinator 절차 문장·요청 가이드·스크립트 주석 불가(설계 §5-2 «제외는 허용 문장만» · dddjango Permission/Exception 대응). 검사는 ③ 규범 문단 검사 뒤에 둔다(G8 뜻 유지). 사용자 판단(반대 방향 규칙)은 사용자에게 묻는 쪽이라 한정하지 않는다. 픽스처 G18. 변이 → red |
| m3 | 수용 | 오탐 근거 인용이 위반 인용 구간과 겹치면 red. 픽스처 G19. 변이 → red |
| m4 | 수용 | `refactor_audit._git` · `debt.reference_lines` 에 `-c core.quotePath=false`(`subst.py` 는 전부 `-z` 라 해당 없음). 픽스처 H7(비 ASCII 파일 이름). 변이 → red |
| m5 | 수용 | `plan` 참조 치환 대상에서 WN6 «대응 미완»(생성)만 있는 키를 뺀다(같은 키에 접두 불일치가 있으면 대상 유지). 픽스처 L1·L1b(대응 미완 → 참조 치환 줄 0) · L2(접두 불일치 대조 짝 → 1). 변이 → L1 red |
| m6 | 수용(F4 처분대로) | `normalize_spaced` + `DocIndex.spaced`·`n2s`(정규화 위치 → 공백 한 칸 본문 위치) · 술어는 띄어 쓸 수 있는 자리만 `\s?` · `(?<!널 )` · «만» 은 앞 공백을 건너 본다 · 부정형 `무방하지않` · 극성 표본 16 → 18(«무방하지 않다» · «예외 다른 경로는 금지다»). 확인: 플러그인 md 전 문서 위치 사상 정합(불일치 0) · **코퍼스 6,135문장 옛·새 판정 차이 0**(실판정 무변 — 낱말 경계 넘는 적중만 막힘) |
| m7 | 수용 | `make verify-web` 에 두 Coordinator `**적용 범위 규범**:` 문단 `cmp` 1행 |
| m8 | 기록 | §2 9 · 10 |
| m9 | 수용(문면) | DR 9번에 «테스트 파일(web/ 아래 포함)의 판정·단언이 바뀌지 않았는가». 기계 대조는 늘리지 않는다(현장 web/ 아래 테스트 0) |
| m10 | 수용 | R0 표기 괄호에 «명령 인자로는 셸이 펼치지 않게 `'web/*.py'` 로 감싼다»(양 플랫폼) |
| m11 | 한계 기록 | `plan --names` 는 옛 모듈 점 경로 문자열로 importer 를 고른다 — 부모 패키지 import(`from web.a.b import mod as m` → `m.name`)·상대 import 소비자는 (나) 에서 빠진다. fail-closed(G1 ② architect 반송 · 경계 교차)이고 현장 모양(T5)은 해당 없음 |
| m12 | 수용 | 이번 고침 회귀(위 각 행) + 계획 약속분: 소유자 전이 A11 · 제외 구간 겹침 G17 · residual 재승인 되살림 K4 · `의미 ⓐ 키:` 값 형식 어긋남 K5(러너 D28 은 6a `--debt-residual` 쪽이라 `residual_m_sets` 를 덮지 않는다 — K4·K5 로 채움 · K4 변이 red). refactor_audit 55 → 73 · subst 29 → 32 |
| T0b 문면 결함 | 수용 | G2 배너 기존 테스트 행 `기존 테스트(확인 HEAD <⑤ 를 돌린 HEAD> · 기준선 HEAD <해시>[ · 재기준선 HEAD <해시>])` · 재확인 조건 «두 행의 확인 HEAD(⑤ 를 돌린 HEAD · 치환 행의 `<HEAD>`)»(양 플랫폼). 실하네스 재확인은 하지 않았다(T0b 재실행 약 80분 · 약 $18) |
| dddjango 판 같은 모양 | 후속 | dddjango `refactor_audit.py` `_carried`(B1 모양 — 리뷰 R 추정) · F9 — 로드맵 7(통합)에서 확인할 후속 과제 |

- 검증: `make verify-web` exit 0(픽스처 16파일 실패 0 · self-test 양 플랫폼 점검 절 62 · 어구 32 · 극성 표본 18 · red 0 · 새 `cmp` 1행) · `claude plugin validate dddjango-web --strict` 통과 · scripts byte 미러 `diff -rq` 0.
