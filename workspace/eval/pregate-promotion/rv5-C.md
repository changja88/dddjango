# ⑤ 구현 적대 리뷰 C — 하네스 실행·봉인·기록·발주측 영향 (2026-09-03 · 브랜치 `feat/pregate-enforce` · 커밋 2fbc111 + b0ddd32)

판정 요약: **BLOCKER 0 · MAJOR 0 · MINOR 7 · 검증됨 다수**. 러너 1회 실행 PASS(«기대 일치» 34행) · 봉인 draft green(그룹 10 · 파일 258) · b0ddd32 는 봉인 대상 0 파일 · main 은 merge-base 와 동일(fast-forward · 충돌 0) · 훅 2검사 green 재현. 실행 산출물: 스크래치 `rv5C/{runner,seal,gate,ledger_check,merge-tree}.out`.

## C1 실행 — 러너 PASS·봉인 정합

| 항목 | 판정 | 실측·근거 |
|---|---|---|
| `PYTHONUTF8=1 python3 workspace/tools/pregate_fixture_run.py` | **검증됨** | exit 0 · stdout 36행 · «기대 일치» **34행**(≥15). 마지막 행 `PASS — pre-gate 픽스처 15종+E 계열 6단계+유닛 기대 일치 (… 차단 모드 enforce 7(블록 부재·공허·update/remove 부재·승격 예외) · --check-report 14단계 + 유닛 매트릭스)` |
| 묶음 enforce 단계 문구(7) | **검증됨** | `noblock-spec: exit 3 · 요약: 형식 red 1건(블록 부재) · 판정 «형식 red(블록 부재)» — 기대 일치` / `empty-block-spec: exit 3 · 요약: 형식 red 1건(블록 공허) · 판정 «형식 red(블록 공허)»` / `update-target ⓐ(기준선 부재): exit 3 · 요약: 형식 red 1건(update 대상 부재 1)` / `remove-target-spec: exit 3 · 요약: 형식 red 1건(remove 대상 부재 1)` / `remove-deferred-spec: exit 4 (remove@L1 은 판정 밖 · 실체화 0)` / `update-target ⓒ(승격 폴더 미커밋): exit 3 · … update 대상 부재 1` / `update-target ⓑ(승격 형태 커밋): exit 4 · 예외 통과 문면`. 단언 실체 = `_expect_form`(`pregate_fixture_run.py:707-720`): exit 3 ∧ `^요약: 형식 red N건\(<종류>\)` 정규식 ∧ 리포트 마지막 절 `- 판정: <문면>` ∧ `블록 해시 [0-9a-f]{12}` — 자기 기대를 실제로 검사한다. 헤더 계수 7 단언 `:758` |
| 묶음 checkreport 단계 문구 | **검증됨(라벨 MINOR-1)** | 출력 13행: `check-report red 미라벨: exit 3 · 불비 1건` / `ignored 2 append: exit 3` / `3번째 corrected(불인정): exit 3` / `3번째 filtered(전건): exit 0 · 정합` / `오염 행 무영향: exit 0 · 정합` / `다른 명세(stale): exit 3` / `표 형식 처분(불인정): exit 3` / `형식 red 마지막: exit 3` / `블록 부재 마지막: exit 3` / `skip·결손 통과: exit 0 · 정합` / `구판 헤더(해시 토큰 없음): exit 3` / `리포트 부재: exit 1` / `절 부재: exit 1`. 단언 실체 = `_expect_check`(`:762-771`): exit ∧ `^요약: check-report (정합\|불비 N건) · 블록 해시 …` ∧ needle(«처분 미기재 N건»·«stale»·«형식 red 미해소»·«최신성 증명 불가»). **14번째 단계**는 `red2.returncode != 2` 무출력 단언(`:809`) — PASS 문구 «14단계»와 stdout 13행의 차이는 여기서 난다 |
| 유닛 매트릭스 | 검증됨(계수는 C3) | `_enforce_unit_checks` `:830-905` — `baseline_form_errors` 14케이스(`:846-861`) · `check_report` 15케이스(`:882-897`) · 실패만 수집(통과 문구 무출력) |
| `make verify` 6/6 기록 | **MINOR-2** | 지시문은 «`git log -1 2fbc111` 본문 참조»였으나 커밋 본문은 제목 + `Co-Authored-By` 뿐(verify 기록 없음). 6/6 기록의 실제 소재 = 루브릭 ④ `workspace/plan/2026-09-03-pregate-promotion-rubric.md:92`(«→ PASS · `make verify` 6/6»). 처방: 머지 커밋 본문(또는 ledger «승격 집행» 절)에 «make verify 6/6 @2fbc111» 1행 |
| `manifest_seal.py --check --draft` | **검증됨** | exit 0 · 출력 1행 `[manifest] green · 그룹 10 · 봉인 파일 258 · 배정 18런 · 상태 draft` |
| 훅 재현(읽기 전용) | **검증됨** | `workspace/hooks/pre-commit`(core.hooksPath) 의 두 검사를 현 트리에 직접 실행 — `ontology_ledger_check.py` exit 0 «정합 — 위반 0» · `ontology_gate.py` 변경 ttl 3파일 «green 3 · red 0» |

## C2 봉인

| 항목 | 판정 | 실측·근거 |
|---|---|---|
| GROUPS.pipeline += `design_pregate.py` | **검증됨** | `workspace/tools/manifest_seal.py:78-79`(주석 + 글롭) · `git diff 2fbc111~1..2fbc111` 에서 +2행 |
| GROUPS.packs += `pregate_symbol_kinds.json` | **검증됨** | `manifest_seal.py:104-105` · +2행 |
| T2-0b-manifest.json 글롭·해시 | **검증됨** | `groups.pipeline.globs` 6개(design_pregate.py 포함) · `groups.packs.globs` 3개(pregate_symbol_kinds.json 포함). 해시: manifest `ec98eb63…`/`49e3ca7e…` — 평범한 `shasum -a 256`(`8f410170…`/`594ef445…`)과 다르지만 이는 봉인 도구의 규약(`sha256_file` `:249-256` = 내용 + `\0mode:<x|->`) — 같은 식으로 재계산해 **byte 일치 확인**. codex 미러 두 파일도 라이브 sha 동일(byte 미러) |
| «why» 주석 ↔ 설계 §9-6 | **검증됨** | pipeline 글롭 주석 «차단 승격으로 G1/G1′·G2 배너의 근거를 내는 실행 경로가 됐다(설계 §9-6)» ↔ 설계 `2026-09-01-pregate-design.md:145` «승격 릴리즈에서 pipeline 그룹 등재» + §12 `:195`. packs 주석 «검사기 소스 기계 추출 소성물 — 팩과 같은 이유로 동결» ↔ `reverse_coverage.py:142-145`(R-3426 닫힌 목록 · 저자 1 · `--check` byte 동일). 그룹 수준 `why`(«3암이 공유하는 실행 경로»)는 미변경 — pre-gate 가 3암 공통 경로에 든다는 뜻이므로 모순 없음 |
| 봉인 뒤 편집된 봉인 대상 | **검증됨(재봉인 불요)** | `git diff --stat b0ddd32~1..b0ddd32` = 18파일 전부 `workspace/eval/pregate-observe/ledger.md` · `workspace/eval/pregate-promotion/**` · `workspace/plan/…-rubric.md` — 10그룹 글롭(`manifest_seal.py:51-170`) 어느 것에도 매치 없음. 2fbc111 안에서 봉인 대상(protocol 그룹 `2026-08-20-ontology-t2-0b-design.md` 판단표 256→258·packs 2→3·pipeline 5→6)이 편집됐으나 같은 커밋의 manifest(74행)가 그 상태를 담고 `--check --draft` green → 정합 |
| draft 상태·sealed_commit | 검증됨(참고) | `status=draft` · `sealed_commit=59817bb`(=2fbc111~1 — 커밋 전 `--write` 규약상 부모). 릴리즈 시 `make release` 가 sealed 로 올린다(`docs/DEVELOPMENT.md:83-100`) |

## C3 계획 대비 누락

| 계획 항목 | 판정 | 실측 · 처방 |
|---|---|---|
| Δ3 픽스처 5 | **있음** | `workspace/eval/fixtures/pregate/{noblock,empty-block,update-target,remove-target,remove-deferred}-spec.md` 실존 · mini_repo/imports_overlay 변경 0(2fbc111 stat) |
| Δ3 묶음 enforce(헤더 7)·checkreport(14) | **있음** | C1 참조. ⓐ/ⓑ/ⓒ 3상태 = `_run_enforce_bundle:723-759` |
| Δ3 유닛 `baseline_form_errors` 12 | **있음(14 — 초과)** | rv3-C ⓐ~ⓛ 12 + «update HEAD 실존»·«폴더만/본체만» 분화 |
| Δ3 유닛 `check_report` 19 | **부분 — MINOR-3** | 구현 15(`:882-897`) · 루브릭 ④ `:92`는 «15케이스»로 적되 계획 19 대비 축소 사유 없음. rv3-C §6 ⓐ~ⓣ 대조: 묶음이 대신 덮는 것(ⓐ 파일 부재·ⓙ ignored 2·ⓛ 표 형식·ⓞ 오염 행·ⓣ 요약 정규식 `_SUMMARY_CHECK_RE`) 제외하고 **미커버 3**: ⓔ «형식 red ∧ 해시 ≠ → 사유 2·순서 stale→형식 red 고정» · ⓡ «같은 ID 처분 2행(ignored·corrected) → 0» · ⓢ «ID 행과 `**ignored**` 가 다른 행 → 3(행 단위)». 처방: `rcases`(`:882`)에 3케이스 append(각 1행 · 실행기 무변경) 또는 루브릭 ④에 «ⓔⓡⓢ 미채택 사유» 1행 |
| Δ3/H4 «요약:» 접두 3픽스처 | **있음** | `_expect_form` 이 5호출 전부에 `_SUMMARY_FORM_RE` 적용 |
| H4 BLIND_SPOTS S1~S9 유닛 · «enforce» 헤더 유닛 | **없음 — MINOR-4** | 러너에 `BLIND_SPOTS`·«모드: 차단(enforce)» 단언 0(유일한 등장 `:874`는 유닛 입력 합성 문자열). 실행기 실물은 맞다(`design_pregate.py:122` `MODE="enforce"` · `:1563`/`:1607` 헤더 · `:1765` 배너 · `:1519-1538` S1~S9) — 다만 «헤더 모드 문자열이 바뀌면 러너가 잡는가»는 현재 아니오. 처방: `_run_enforce_bundle` 첫 `_expect_form` 뒤 `assert "모드: 차단(enforce)" in report.read_text()` 1행 · `_enforce_unit_checks` 에 `len(dp.BLIND_SPOTS)==9 and all(s.startswith(f"S{i+1} ") …)` 1행 |
| Δ3 docstring E번호 인용 금지 | **있음** | 러너 docstring E1~E4 는 자기 케이스명 + 면책 `:50` «승격 계획서의 실행기 변경 항목 번호와 무관» |
| H5 `reverse_coverage.py:139` | **있음** | «관찰 모드» → «차단 모드 2026-09-03 승격 · … `--check-report` 가 배너·G2 근거의 기계 출처» |
| Δ5 codex 손 미러 9행 · 어절 diff 산출물 | **있음(1행 결과 미기재 — MINOR-5)** | `workspace/eval/pregate-promotion/codex-mirror-diff.md` 9절 · byte 동일 6 · 병렬 어절 2(27·8 어절 — 헤더가 «병렬 정의 어절만» 기대로 명시). 2번째 절 «배너를 출력한 뒤 AskUserQuestion…»은 «대응 행 없음 — 수동 확인»으로 끝나고 결과가 없다. 본 리뷰 실측: Claude `dddjango.md:58` 꼬리 ↔ codex `SKILL.md:62` 가 같은 `--check-report` 근거 문면 · 양쪽 `check-report` 출현 6=6 · R-3444 는 codex `:186`. 처방: 그 절에 «수동 확인 결과: 꼬리(«G1/G1′ 배너에는 …» 이후) byte 동일 — 머리는 Claude 전용 AskUserQuestion 문장» 1행 |
| Δ5 manifest | **있음** | C2 |
| Δ5 기록(rulepack `R-3432` 단일 · LEDGER s006 note · ledger A/B 6좌표) | **있음** | rulepack `by_section/…/s006/works[52]` 1곳 + `works/R-3432` · LEDGER +5행 note «Exception→Prohibition · 유형 변경 선례 0 · 대안 문면 rv3-B B3 보관» · ledger `:214` A/B 요약행(6좌표 표 자체는 `retro-ab.md` — 링크됨) |
| §5-2 ledger 판정 표 v5 | **있음** | `ledger.md:212` |
| §5-2 로드맵 R-1·§8 | **있음(잔존 문면 — MINOR-6)** | R-1 행 `:37` 갱신 + §8 «파트 2 착수» append. 단 R-1 행이 여전히 «이월 2건: R-3433 개정에 ‹구조 규칙 filtered 대상 아님› 필수 조항 · #392 처분 병기»를 이월로 두는데, ledger `:213`은 R-3433 rev4 가 «구조 규칙 제외»를 담았다고 적는다 → 이월 1건은 소화됨. 처방: R-1 행 이월을 «#392 처분 실측 병기 1건»으로 축소 |
| §5-2 설계 §8 ⑵ 정정 | **있음(추기 방식)** | §12 `:193` 정정 · 원문 `:133` «기계 대조 스크립트» 유지 — 버전 추기 문서 관행상 허용(§12 가 명시 정정) |
| §5-2 현장 보고 G · 조감도 · `ledger.md:4` rev4 | **있음** | 현장 보고 G 행 «사각 S3 문면 반영·제보 수정 단계» · 조감도 09-03 행 `<u>pre-gate 차단 승격 배치</u>` · `ledger.md:4` «R-3433 rev4» |
| §5-3 이월 등재 | **있음** | ledger `:216`(레인 5 관찰·«구형 명세 블록 부재 반송» 별도 계수·첫 `--check-report` 실전·발견 ⑪) · 설계 §12 마지막 불릿(exit 4 픽스처는 이번 배치 `remove-deferred`·`update-target ⓑ`가 고정 = 이월 해소 명시) |

## C4 발주측 영향

**첫 변화 실물(실행기 stdout)** — `workspace/eval/pregate-promotion/retro-ab/`:

- 구형 명세(kkebi 20/20 · spring 18/24 폴더)를 개정해 재실행하는 순간 — `kkebi-1.out`: `형식 red — machine 블록 부재(<!-- machine: file-plan --> 없음): 차단 모드는 블록이 의무다 — 구형 명세(형식 규범 이전 승인)는 개정 시점에 블록을 소급 작성한다(기준선 실존 경로는 update · 부재 경로만 add)` / `요약: 형식 red 1건(블록 부재) · 기준선 6608fb0d955c · 모드 차단` (exit 3).
- Phase 2 에서 명세를 고치고 재실행 없이 G2 로 가는 순간 — `catalog-check.out`: `불비: stale — 명세 블록 해시 cb95a1bddb32 ≠ 마지막 예보 6cf8e2ffdfc3 · 재발화` / `요약: check-report 불비 1건 · 블록 해시 cb95a1bddb32=6cf8e2ffdfc3 · 마지막 판정 green …` (exit 3 → G2 배너 불가 `dddjango.md:165`).
- 기준선을 옮겼거나 기실현 행을 재라벨한 명세 — `R-new.out`: `remove 대상 부재: … — 기준선 80431d9480f7 에 없는 경로는 제거할 수 없다(고정 기준선에서 기실현 remove 는 실존이다 — 이미 지워진 경로는 행을 거둔다)` ×7 · `Rp-new.out`: `update 대상 부재: … — 기준선 61b56ef4b69e 에 없는 경로는 add 다(재라벨 도피 금지)` ×24 (exit 3 · 구 실행기는 4/5 통과).

**발주 가이드(R-12) 1줄 후보 3**:

1. «구형 design-spec 을 고치면 pre-gate 가 ‹블록 부재›로 선다 — file-plan 기계 블록을 소급 작성(이미 있는 파일=`update` · 새 파일만 `add`)해 재실행하고, 고치지 않는 순수 구현 수정은 G2 배너 ‹pre-gate 최신성: 미실행(구형 명세 · 변경 0)› 1행으로 지나간다.»
2. «Phase 2 에서 design-spec 의 기계 블록·입장 표를 바꿨으면 G2 전에 `design_pregate.py <폴더>/design-spec.md . --base <G1 기준선 SHA>` 재실행 — 안 하면 `--check-report` 가 ‹stale›로 G2 배너를 막는다(red 는 처분 라벨 전건 기재까지).»
3. «기준선은 G1 승인 시점 SHA 로 고정 — 이미 실현된 add 를 `update` 로, 이미 지운 파일을 `remove` 로 남기지 말고 행을 거둔다(`foo.py → foo/` 승격 폴더만 예외 통과).»

**Coordinator 문면 닫힘 판정** — **검증됨(닫힘)**. `dddjango.md:98` «**한정**: 이 레인 산출물 폴더에 pregate-report 가 없고 design-spec 에 machine 블록도 없고 이 세션에서 design-spec 변경이 0 이면 … `미실행(구형 명세 · 변경 0)` 이고 `--check-report` 를 부르지 않는다 — 블록이 있는 명세는 이 한정에 들지 않는다» — 3입력(리포트 파일 유무 · `<!-- machine:` 마커 유무 · 세션 내 변경 유무) 전부 코디네이터가 스스로 판정 가능한 관측값이다. `:169` 는 이 한정을 참조해 G2 1행을 정하고, `:165` 는 «`--check-report` exit ≠ 0» 을 G2 제시 금지에 넣으며, `:185` 가 «순수 구현 수정»의 정의(G1′ 생략 조건)를 준다. 구형 명세 + 개정 → 한정 탈락 → `--check-report` → 리포트 부재 exit 1 → 재실행 → «블록 부재» 형식 red → 소급 블록: 경로가 끝까지 이어진다.

**문면 MINOR-7(발주자 오독)**: `요약: … 블록 해시 cb95a1bddb32=6cf8e2ffdfc3` — 불비(stale)인데 두 값 사이가 `=` 다. R-3444 1행 형식 «블록 해시 <값> = 리포트 <값>»(`:169`)과 러너 `_SUMMARY_CHECK_RE`(`:698`)가 `=` 를 구분자로 고정하고 있어 이번 배치 변경은 권하지 않음 — 직전 `불비: stale … ≠` 행이 앞서므로 오독 위험은 낮다. 이월 후보: 불비 시 `≠` 출력(실행기 `run_check_report` + 러너 정규식 + R-3444 문면 동시 개정).

## C5 릴리즈 준비(«머지 가능» 판정)

| 항목 | 판정 | 실측 |
|---|---|---|
| 브랜치 커밋 | 검증됨 | `git log --oneline main..HEAD` 7건(399796a → b0ddd32) · 구현 2fbc111 · 증거 b0ddd32 |
| 트리 clean | 검증됨 | `git status --short` 출력 0 |
| verify 6/6 | 검증됨(기록 소재 MINOR-2) | 루브릭 ④ `:92` · 본 리뷰는 `make verify` 대신 봉인 check + 훅 2검사 + 러너로 대체 실측(전부 green) |
| 봉인 draft | 검증됨 | C1 |
| pre-commit 훅 green | 검증됨 | C1 재현(ledger_check 0 · gate 3/3). 커밋 시점 실행은 `core.hooksPath=workspace/hooks` 설정으로 강제됨 |
| main 머지 충돌 | **검증됨(0)** | `git log HEAD..main` 비어 있음 · merge-base `36e9f11` = main tip → **fast-forward** · `git merge-tree --write-tree main HEAD` exit 0(트리 `39364b6b` · 충돌 파일 0). 관행(08a0049·88a65a0 «merge:» 커밋)대로 `--no-ff` 권장 |
| README/CHANGELOG | 검증됨(갱신 불요) | `dddjango/README.md` 부재 · 루트 `README.md`·`docs/*.md` 에 «pre-gate»·«관찰 모드» 0건 · CHANGELOG 파일 없음(릴리즈 노트는 `make release` → GitHub Release). 플러그인 트리(`dddjango/`·`codex-dddjango/`) «관찰 모드»·«모드: 관찰»·`"observe"` 0건 — 잔존 «관찰» 8/25건은 전부 «관찰된 계약(observed)»·«관찰 대장» 용례 |
| 릴리즈 절차 전제 | 참고 | `docs/DEVELOPMENT.md:92-100` — main·clean·origin 동기에서만 `make release`. 릴리즈는 사용자 요청 시(로드맵 R-1 문면과 정합) |

**판정: 머지 가능**(BLOCKER/MAJOR 0 · fast-forward · 충돌 0).

## ⑥ 반영 목록

| # | 등급 | 파일:행 | 처방 |
|---|---|---|---|
| MINOR-1 | 라벨 | `workspace/tools/pregate_fixture_run.py:809`, `:933` | 무출력 단언(red 재실행 exit 2)에 `print("check-report red 재실행: exit 2 — 기대 일치")` 1행 추가하거나 PASS 문구를 «13단계+재실행 1» 로 — stdout 계수와 PASS 문구 일치 |
| MINOR-2 | 기록 | 머지 커밋 본문 또는 `workspace/eval/pregate-observe/ledger.md:210-216` | «make verify 6/6 @2fbc111 · manifest --check --draft green · 러너 PASS 34행» 1행 |
| MINOR-3 | 하네스 | `pregate_fixture_run.py:882-897` · 루브릭 `…-rubric.md:92` | `rcases` 에 rv3-C ⓔ(형식 red ∧ 해시 ≠ → 사유 2·stale 선행)·ⓡ(같은 ID ignored+corrected → 0)·ⓢ(ID 행≠라벨 행 → 3) 3케이스 append — 실행기 무변경. 못 넣으면 루브릭 ④에 축소 사유 1행 |
| MINOR-4 | 하네스 | `pregate_fixture_run.py:727`(첫 `_expect_form` 뒤) · `:833`(`dp` 로드 뒤) | `"모드: 차단(enforce)" in report.read_text()` 단언 1행 · `len(dp.BLIND_SPOTS)==9 ∧ 접두 S1..S9` 단언 1행 — H4 두 항목 실체화 |
| MINOR-5 | 기록 | `workspace/eval/pregate-promotion/codex-mirror-diff.md` 2번째 절 | «수동 확인 결과: 꼬리(«G1/G1′ 배너에는 pre-gate 예보 1행…» 이후) byte 동일 — 머리는 Claude 전용 AskUserQuestion 문장» 1행 |
| MINOR-6 | 기록 | `workspace/plan/2026-09-03-improvement-roadmap.md:37` | R-1 이월을 «#392 처분 실측 병기 1건»으로 축소(«구조 규칙 filtered 제외»는 R-3433 rev4 로 소화 — ledger `:213`) |
| MINOR-7 | 이월 | `dddjango/scripts/design_pregate.py` `run_check_report` · `pregate_fixture_run.py:698` · R-3444 문면(`dddjango.md:169`) | 불비 시 `블록 해시 A≠B` 출력 — 세 곳 동시 개정이라 이번 배치 밖 · 로드맵 이월 등재만 |

## 결정 불능 잔여

1. **구형 명세 + 관찰기(2.17.16) skip 스텁 리포트가 레인 폴더에 남아 있는 경우**: `:98` 한정은 «리포트 부재»를 전제하므로 그런 레인은 `--check-report` 로 간다. 마지막 판정 «skip» + 블록 해시(블록 0 → 입장 표만) 불변이면 exit 0 정합이고, 산문만 고친 개정은 캐시 skip(`:98` ①)으로 재실행 없이 G2 가 열린다 — 즉 «개정 시 소급 블록 1회전»이 기계적으로 강제되지 않는 좁은 경로. 실제 존재 여부(spring 18/24 · kkebi 21 폴더에 2.17.16 스텁 리포트가 있는가)는 발주측 실측 없이는 판정 불능. 닫는 처방(1행 · 실행기 `check_report(spec_text, …)` 가 spec 을 이미 받으므로): 마지막 판정 «skip» ∧ spec 에 `<!-- machine:` 마커 0 → exit 3 «블록 부재 — 재발화». 기존 유닛 «skip» 케이스는 green-spec(블록 있음)이라 회귀 0. 레인 5 관찰 대장에 «구형+스텁» 계수 1열 권고.
2. **codex 병렬 어절 27·8건**은 «병렬 정의 어절만»이라는 기대를 사람이 눈으로 확인한 결과다(자동 판정식 없음). 본 리뷰도 문면 대조로 정합을 확인했으나 어절 단위 자동 판정은 없다 — 다음 손 미러 개정 때 «허용 어절 사전» 도입 여부는 별도 결정.
3. **`make verify` 6/6 은 본 리뷰가 재실행하지 않았다**(지시). 대체 실측 4종(러너·봉인 check·훅 2검사)은 green.
