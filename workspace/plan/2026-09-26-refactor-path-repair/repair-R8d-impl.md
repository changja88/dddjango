# 수리 R8d 구현 기록 — ① core verdict-final · ②-A web 경계 교차 소비자 · D web 꼬리 묶음 grep · web 고아 병합 (로드맵 8d)

> **최종 상태는 2차(구현 리뷰 반영) 판이다.** 1차 판 뒤 구현 리뷰 두 건(core · web — 둘 다 코드 결함 0 · 시험 보강)이 돌아왔다. 운영 세션 처분대로 반영하고 단계 스냅숏을 다시 떴다. 처분 표는 §7 에 있다. 1차 트리·패치는 scratch `impl-R8d/v1/` 과 §0 끝 줄에 남겼다.

- 작성: 2026-09-30 · 격리 워크트리 `.claude/worktrees/agent-a6019ce18bc25e914`(브랜치 `worktree-agent-a6019ce18bc25e914`). **커밋 0 · push 0** 이다.
  - 워크트리는 `acbfffda` 에서 시작했다. 작업 트리가 깨끗해서(변경 0) `git reset --hard a1d97bc3` 로 포인터만 설계 기준으로 옮겼다(새 커밋 없음).
  - 커밋 대신 단계마다 `git add -A`(`.venv` 심링크·이 기록 제외) → `git write-tree` 로 트리 id 를 남겼다. 인덱스는 지금 tree4 가 스테이징된 상태다.
  - 2차는 `git checkout <tree1> -- .` 로 1차 tree1 에 되돌린 뒤 단계마다 다시 쌓았다. web 단계 판은 scratch `stage/s2~s4` 에서 먼저 조립·시험하고 워크트리에 놓았다(`build_stages.py` · `web_edits.py` · `place_stage.py`).
  - 이 기록 파일은 미추적이고 어느 트리·패치에도 없다(8c 처럼 별 docs 커밋 몫).
- 입력
  - 설계 정본: `design-R8d.md`(메인 체크아웃 · 미추적). §0~§8 을 따랐다.
  - 진단: `diag-R8d-1-verdict-final.md` · `diag-R8d-2-plan-consumer.md`.
  - 설계 리뷰: scratch `review-R8d-core/review-R8d-core.md` · `review-R8d-web/review-R8d-web.md`(+ `extra_block_final.sh`).
  - 구현 리뷰: scratch `review-R8d-impl-core/review-R8d-impl-core.md`(minor 1 · nit 1) · `review-R8d-impl-web/review-R8d-impl-web.md`(minor 2 · nit 5).
  - 프로토타입: scratch `r8d/`. 한 줄씩 읽었고, `r8d-all.patch` 와 같은 내용인지 대조한 뒤 옮겼다(§5).
- Serena·Graphify 는 쓰지 않았다(지시). `/Users/hyun/Desktop/spring_dream_server` 는 읽지 않았다. 현장 측정은 scratch `r8d/field` 를 APFS 로 복제한 `impl-R8d/field` 에서 했다.
- `make verify` 용 `.venv` 심링크(→ 메인 `.venv`)를 두었고, 검증 뒤 지웠다. 트리에는 들어가지 않았다.
- scratch 루트: `/private/tmp/claude-501/-Users-hyun-Desktop-dddjango/ed01792c-e467-4a58-a794-ed16237ffb9e/scratchpad/impl-R8d/`
  - 패치(2차): `p1-core.patch` · `p2-web-consumer.patch` · `p3-web-grep.patch` · `p4-web-orphan.patch` · `all.patch`(tree0↔tree4)
  - 로그: `logs/`(2차는 `p1b-*` · `p2b-*` · `p3b-*` · `p4b-*`) · 실험 도구: `mut_core.py` · `mut_web.py` · `field_time.py` · `core_tail.sh` · `f12_repro.py` · `onto_r3517.py` · `ledger_r8d.py`
- 표기: **[실측]** = 이번에 돌려 확인함 · **[추정]** = 코드를 읽어 추론함.

## 0. 요약

| 단계 | 트리(2차) | 픽스처 [실측] | 변이 [실측] |
|---|---|---|---|
| tree0 (`a1d97bc3`) | `75854616299f720c6fb3756a5b5a7eecba0c91c5` | core 199 · web 151 | — |
| ① core | `42eddc8f135b9cb59c61d4798e8e00adb6fd2978` | core **215 ✓** | V1~V12 12/12 · HEAD 도구 16 red |
| ②-A web | `ca81f6d3a085dd60f58f1d4b211e934f4315a269` | web **178 PASS** | VA 15 · MNL 1 · X3 2 red · HEAD 도구 15 red |
| D web | `966139c83b63603d5ffff35086d54a18e4371ee5` | web **186 PASS** | VD1·VD2·VD3·MDa·MDb·X1·X2 모두 red · ②-A 도구 5 red · 쌍 묶음 전 D 도구 1 red(R5) |
| web 고아 병합 | `9835e6791667830753cc547b5d7f58d6012c77cb` | web **190 PASS** | VO 3 · VOG 1 · X6 1 red · D 도구 3 red · 최종 판 web 변이 15/15 |

- 1차 트리(참고): tree1 `e17c1732` · tree2 `f79b88c0` · tree3 `88b870f7` · tree4 `c1205e8e`(core 213 · web 177/184/186).
- verify
  - ① 뒤(2차 tree1)와 최종(2차 tree4) `make verify`: ontology · cross · backstop · regen 네 묶음 green. base-core RED 는 봉인 드리프트 14건뿐이다(모두 ① 파일). 봉인 대조 뒤 단계는 따로 돌려 green 이다(§4.3).
  - 구현 리뷰 core 는 1차 p1 + 재봉인 복제본에서 `make verify` 5묶음 green · exit 0 을 실측했다(`review-R8d-impl-core/verify.log`). 2차 p1 은 시험 사례와 재분류 문구만 더했다.
  - `make verify-web`: ②-A · D · 고아 병합 세 단계 모두 EXIT 0.
  - `claude plugin validate dddjango --strict` · `claude plugin validate dddjango-web --strict`: 둘 다 통과.
- **core F12 재현됨** [실측]: 번호 중복으로 병합 대상 M 이 제외로 남으면, HEAD 도구와 변이 V11(`adopted_m` = 확정 표 모든 M)은 병합 항목을 제외 항목에 붙인다. 수리 판은 채택으로 돌린다(§4.1).
- 현장 사본(D): plan 52~60초 → 1.2~1.5초 · `--names` 1.1~3.0초 · plan.md·plan-names.md 는 ②-A 판과 ②-A+D 판이 byte 같다(§4.4 · 1차 실측 — 2차는 도구 동작 무변).
- 설계와 다른 점: 동작은 같다. 다른 것은 문자열과 시험 보강이다(§5).

## 1. ① core — 바뀐 파일 (tree0 → tree1)

| 파일 | +/− | 내용 |
|---|---|---|
| `dddjango/scripts/refactor_audit.py` | +42/−13 | 설계 §1.1 그대로다. 사용 문구 · `VERDICT_FINAL` · `_load_verdicts(name=)` · `_write_final` · `_final_verdicts`(조건부 안내) · `_finalize_verdicts` 고아 병합 5행(재분류 문구 «병합 대상 Mx 이 확정 기록의 채택 항목이 아니다 → 채택») · `cmd_check_verdict` exit 0 에서 확정 표 쓰기 · `_scope` 한 곳 판독 · `_origins` 메시지 · `cmd_resolution`·`cmd_residual` 가 `_final_verdicts` 를 읽음 |
| `codex-dddjango/skills/dddjango/scripts/refactor_audit.py` | +42/−13 | byte 미러(`diff -rq` 무차이) |
| `workspace/tools/refactor_audit_fixture_run.py` | +163/−14 | `_res_folder(confirm=)` · E2 계열 4곳 `confirm=False` · E2-0·x3 기대 반전 · `final_cases`(F1~F12 · F9 짝 · F9′ · F10b) · `main` 에 등록 |
| `ontology/rules/command-dddjango.ttl` | +9/−3 | R-3517 rev2(`revision-amendment` · `R-3517@2026-09-30` wasRevisionOf `@2026-09-27`) · prefLabel «verdict-final 동결» · 블록 s012/b2 문구 |
| `dddjango/commands/dddjango.md` | +1/−1 | `ontology_render.py --apply command-dddjango` 재투영(:227 한 줄) |
| `ontology/LEDGER.tsv` | +1 | `command-dddjango s012 63f5e53c…9592 graph … rebaseline:2026-09-30 로드맵 8d ① — R-3517 rev2 잇기 M 목록 동결 대상 verdict.md → verdict-final.md` |
| `workspace/eval/fixtures/ontology_gate/target-counts.json` | +1/−1 | ExpressionShape 3811 → 3812 |
| `dddjango/scripts/rulepack.json` · Codex 미러 | +4/−4 씩 | `make rulepack` 재소성. 두 파일 byte 같음 |
| `codex-dddjango/skills/dddjango/SKILL.md` | +1/−1 | :243 에 같은 치환(의미 미러). core :227 과 줄이 같다 [실측 diff 0] |

- 문면 절차 [실측]: rdflib 왕복 byte 동일 → `ontology_gate.py` 90/90 green → 재투영(command-dddjango 한 문서) → LEDGER(sha 가 프로토타입과 같음) → 계수표 → rulepack. q4 골든은 verify-ontology 가 green 이라 `--emit` 하지 않았다.
- 바꾸지 않은 것: «상시 답 인식 블록»(:159-193) · `_previous` · R3(:237) · G0(:241) · G0 정지 재개(:229) · `design-architect.md:122` · ISSUED(새 채번 없음).
- 봉인(`workspace/eval/ab/T2-0b-manifest.json`)은 쓰지 않았다(지시). 프로토타입 `r8d-all.patch` 에는 봉인이 들어 있지만 이 패치들에는 없다.

## 2. ②-A web — 바뀐 파일 (tree1 → tree2)

| 파일 | +/− | 내용 |
|---|---|---|
| `dddjango-web/scripts/refactor_audit.py` | +4/−3 | `compute_plan`: `load = LOAD_LINE…` · `CONSUMER_LINE.search(text) or not load` → 소비자 · `load` → (가) · 절 주석 |
| `dddjango-web/scripts/test/fixtures_refactor_audit.sh` | +71 | A′ 절(`PSEC` · A12·A12′ · 모양 표본 프로젝트 Q · AQ0~AQ8 · **AQ2″**) · R 절(R1·R1′·R2) |
| Codex 미러 둘 | 같음 | byte 미러 |

- 문면은 바꾸지 않았다(설계 §2.2).

## 3. D web · 고아 병합 — 바뀐 파일

### 3.1 D (tree2 → tree3)

| 파일 | +/− | 내용 |
|---|---|---|
| `dddjango-web/scripts/refactor_audit.py` | +48/−18 | `_WORD_EDGE` · `_Refs`(`warm` 두 grep · ASCII 경계 분배 · 자기 제외 · 메모) · `_owners(refs, …)` · `compute_plan` 의 `warm` 두 곳 · 지역 변수 `refs` → `lines` · `_plan_names` 경로 쌍마다 -F 한 번 · -F -w 한 번 |
| `dddjango-web/scripts/test/fixtures_refactor_audit.sh` | +52/−1 | Q 형제 표본 · AQ0 `소비자 13` · A″ 절(AD2·AD2′·AD3·AD4) · R′ 절(R3 + 판별 줄 셋 · R4 · **R5 exit·하한** · **R6**) |
| Codex 미러 둘 | 같음 | byte 미러 |

- `src/debt.py` 는 바꾸지 않았다.

### 3.2 web 고아 병합 (tree3 → tree4)

| 파일 | +/− | 내용 |
|---|---|---|
| `dddjango-web/scripts/refactor_audit.py` | +5 | `_finalize_verdicts` 끝 5행 — 대상 판별 `re.fullmatch(r"M\d+", v.merge_to)` · 재분류 문구는 core 와 같음 |
| `dddjango-web/scripts/test/fixtures_refactor_audit.sh` | +10 | K 절 끝 K6 · K6b · **K6c** · **K7**(새 audit 폴더 `20260930-150000`) |
| Codex 미러 둘 | 같음 | byte 미러 |

## 4. 시험·변이·시간 [실측]

### 4.1 core 픽스처 (`logs/p1b-core.log` · `logs/p1b-mut/` · `logs/p1b-mut-summary.txt` · `logs/f12-repro.log`)

- tree1: **215 ✓ · ✗0** (199 → 215 · 새 16 · 적응 2).
- HEAD 도구를 같은 러너로 돌리면 ✓199 · ✗16 이고 끝까지 돈다. red 는 E2-0 · x3 · F1(2) · F2~F8 · F9 · F9′ · F10 · F10b · F12 다.
  - F10b 는 HEAD 에서 행동 차이가 아니라 확정 표 부재로 red 다(HEAD 는 `verdict-final.md` 를 쓰지 않는다). 행동으로는 가드 수호 시험이다.
- **F12 재현** [실측 `f12_repro.py`]
  - 입력: 원 행 #1(V_IMPL8 · C) · #2(V_B9 · P) · #3(V_B9 · C). 판정 `M1 #1 제외(유효)` · `M1 #2 채택`(번호 중복) · `M3 #3 병합 → M1`.
  - `check-verdict` 는 exit 2 다(구조 red «M 번호 중복» — `red_ids` 밖). `_judge` 는 `kinds[M1]` 이 마지막 행(채택)이라 M3 병합에 red 를 내지 않는다.
  - `--final` 은 exit 0 이다(재분류 «M1 M 번호 중복 → M4»).

  | 도구 | M3 결과 |
  |---|---|
  | 수리 판 | `| M3 | ddd-01#3 | 채택 |` · 재분류 «M3 병합 대상 M1 이 확정 기록의 채택 항목이 아니다 → 채택» |
  | HEAD | 로그 요약 `병합→M 1` — 제외 항목 M1 에 붙는다 |
  | 변이(`adopted_m` = 확정 표 모든 M) | `| M3 | ddd-01#3 | 병합 → M1 |` — 제외 항목 M1 에 붙는다 |

  - 공백이 맞다. 그래서 F12 를 넣었다.
- 변이(작업 트리 사본 병렬 · V1~V9 는 설계 §1.7 · V10~V12 는 구현 리뷰 보강)

| 변이 | red | 사례 |
|---|---|---|
| V1 소비자가 verdict.md 를 읽음 | 8 | x3 · F1(2) · F2 · F3 · F4 · F5 · F6 |
| V2 확정 표에 원 판정을 씀 | 10 | F1(2) · F2~F7 · F10 · F12 |
| V3 exit 2 에서도 씀 | 1 | F8 |
| V4 확정 표 없으면 verdict.md 로 대체 | 3 | E2-0 · F9 · F9′ |
| V5 `_scope` 8c 이중 판독 | 1 | x3 |
| V6 대상 조건 제거 | 3 | x4 · x5 · mi-B |
| V7 칸 이스케이프 제거 | 1 | F11 |
| V8 고아 병합 5행 제거 | 2 | F10 · F12 |
| V9 안내문 무조건 재실행 | 1 | F9′ |
| V10 고아 교정 «대상 M» 가드 삭제(리뷰 X13) | 1 | F10b |
| V11 `adopted_m` = 확정 표 모든 M(리뷰 web X6 의 core 짝) | 1 | F12 |
| V12 `--final` 이면 확정 표를 쓰지 않음(리뷰 X30) | 13 | E2-6 · E2-7(2) · F1(2) · F2~F6 · F10(n1 반영으로 새로 red) · F10b · F12 |

### 4.2 web 픽스처 (`logs/p{2,3,4}b-web.log` · `logs/p{2,3,4}b-mut/` · `logs/p{2,3,4}b-mut-summary.txt`)

| 단계 | 판 | 결과 |
|---|---|---|
| ②-A | 작업 트리 | **178 PASS** |
| | HEAD 도구 | 15 FAIL(A12 · AQ0 · AQ1×9 · AQ6 · AQ7 · AQ8 · R2). **AQ2″ 는 HEAD 에서도 green**(include 는 HEAD 도 소비자 — 수호 시험) |
| | VA(분류 되돌림) | 15 FAIL |
| | MNL(로드 제외 삭제) | 1 FAIL(R1′) |
| | X3(include 줄 소비자 탈락) | 2 FAIL(AQ0 · **AQ2″**) |
| D | 작업 트리 | **186 PASS** |
| | ②-A 도구 | 5 FAIL(AD2 · AD2′ · AD3 · R3 · R5) · **R6 green**(동등성 수호 시험 — ②-A·HEAD 도 `-w`) |
| | 쌍 묶음 전 D 도구(`r8d/tools-AD`) | 1 FAIL(R5) |
| | HEAD 도구 | 20 FAIL · R6 green |
| | VD1 `\w` 경계 · VD2 경계 없는 부분 문자열 | 각 2 FAIL(AD2 · R3) |
| | VD3 메모 무효 | 2 FAIL(AD3 · R5) |
| | MDa .py 경로 꼬리 적중 버림 · MDb 자기 제외 삭제 | 각 1 FAIL(R3) |
| | X1(경로 꼬리 분배에 ASCII 경계) | 1 FAIL(R3 — 판별 줄 `old_home/…` 덕) |
| | X2(`_plan_names` 점 경로 `-w` 탈락) | 1 FAIL(**R6**) |
| 고아 병합 | 작업 트리 | **190 PASS** |
| | D 도구 | 3 FAIL(K6 · K6b · K7) · **K6c green**(가드 수호 시험) |
| | HEAD 도구 | 23 FAIL · K6c green |
| | VO(5행 무효) | 3 FAIL(K6 · K6b · K7) |
| | VOG(«대상 M» 가드 삭제 — 리뷰 core m1 의 web 짝) | 1 FAIL(**K6c**) |
| | X6(`adopted_m` = 확정 표 모든 M) | 1 FAIL(**K7**) |
| | 최종 판 변이 15종 | VO 3 · VOG 1 · X6 1 · VA 15 · MNL 1 · X3 2 · VD1 2 · VD2 2 · VD3 2 · MDa 1 · MDb 1 · X1 1 · X2 1 — 15/15 red |

### 4.3 verify (`logs/p1b-verify.log` · `p1b-core-tail.log` · `p4b-verify.log` · `p4b-core-tail.log` · `p{2,3,4}b-verify-web.log`)

- ① 뒤(2차 tree1) `VERBOSE=1 make verify` → EXIT 2
  - verify-ontology · verify-base-cross · verify-base-backstop · verify-base-regen: **green**. regen 안 `refactor_audit 픽스처 기대 일치` PASS.
  - verify-base-core: **RED**. 원인은 `manifest_seal.py --check --draft` 의 봉인 드리프트 14건뿐이다. 대상은 SKILL.md · dddjango.md · refactor_audit.py · rulepack.json · LEDGER · ttl 이다.
    - 1차와 줄마다 같다. 다른 것은 `script_trees` 실측 해시뿐이다(재분류 문구 변경).
    - 앞 단계(corpus_mirror_sync … ontology_rulepack --check)는 `set -e` 아래 모두 통과했다.
  - 봉인 대조 뒤 단계는 `set -e` 에 가려지므로 `core_tail.sh` 로 따로 돌렸다.
    - ab_score self-test · scripts byte 미러 · REQUEST_GUIDE cmp · request_guide_contract self-test·실제 계약: 모두 exit 0.
    - `manifest_seal.py --self-test` 는 exit 2 다. 실패는 M0(무변이 대조) 1건뿐이다. M0 은 실물에 `--check --draft` 를 다시 돌리므로 같은 봉인 드리프트다. M1~M8 변이 탐지는 모두 red 로 잡혔다.
  - 재봉인 복제본에서의 green 은 구현 리뷰 core 가 실측했다(1차 p1 + 재봉인 → 5묶음 green · exit 0).
- 최종(2차 tree4) `VERBOSE=1 make verify` → EXIT 2 · ① 뒤와 같은 모양이다.
  - ontology · cross · backstop · regen green(regen 안 refactor_audit 픽스처 PASS).
  - base-core RED 는 봉인 지적 14건이고, 2차 ① 뒤 14건과 줄마다 같다(`cmp` 동일). web 파일은 봉인 글롭 밖이라 늘지 않았다.
  - `core_tail.sh` 도 같다. seal self-test M0 만 red 이고 나머지는 exit 0 이다.
- `make verify-web`: ②-A 178 · D 186 · 고아 병합 190 모두 EXIT 0 · codex 미러 byte 대조 무차이.
- plugin validate(`--strict`): dddjango · dddjango-web 둘 다 `✔ Validation passed`(2차 tree4).

### 4.4 현장 사본 (1차 실측 · `logs/field-{head,A,AD,AD-nopair}.txt` · 출력 `out/`)

2차는 web 도구의 동작을 바꾸지 않았다. 바뀐 것은 고아 병합 재분류 문구뿐이고 plan 경로 밖이다. 그래서 다시 재지 않았다.

단독 순차 · `GIT_OPTIONAL_LOCKS=0` · 사본 = `r8d/field` APFS 복제. 레인 폴더는 `.dddjango-web/20260929-1645-refactor-home` 이다.

| 실행 | HEAD | ②-A | ②-A+D | 산출 동일(②-A ↔ ②-A+D) |
|---|---|---|---|---|
| `plan web/home` | 54.3초 | 52.4초 | **1.5초** | plan.md sha `e2add8de…` 같음 |
| `plan web/employee_choice` | — | 60.3초 | **1.2초** | plan.md sha `8334bf9c…` 같음 |
| `--names` 레인 명세(쌍 0) | — | 60.3초 | **1.1초** | 같음(머리 시각 줄 제외) |
| `--names` `home/home/` + `이름:` 1 | — | 67.9초 | **2.8초** | 같음 |
| `--names` `consultation/conversation/`(구성원 28) | — | 80.7초 | **2.1초** | 같음 |
| `--names` `consultation/` + `home/home/`(구성원 56) | — | 100.6초 | **3.0초** | 같음 |

- HEAD 도구의 `plan web/home` plan.md 는 레인 plan.md(`audit/20260929-164538/plan.md`)와 byte 같다(sha `63caa8b3…`).
- ②-A 뒤 소비자 절만 바뀐다. `web/home` 은 `web/auth/login/view/login_view.py:18` · `web/urls.py:7` 이다. `web/employee_choice` 는 영역 VM 6줄 + `web/urls.py:13` 이다. 설계 §2.5 와 같다.
- ②-A 판 `--names` 시간에는 `compute_plan` 전체(약 55초)가 들어 있다. 쌍 묶음 전 D 판(`r8d/tools-AD`)도 쟀다.
  - `home/home/`+`이름:` 12.5초 · `consultation/conversation/` 18.4초 · `consultation/`+`home/home/` 48.7초 → 쌍 묶음 뒤 2.8 · 2.1 · 3.0초.
  - 산출 sha 는 세 판(②-A · 쌍 묶음 전 · 쌍 묶음 뒤) 모두 같다.

## 5. 설계·프로토타입과 다른 점

동작은 설계와 같다. 다른 것은 아래 문자열과 구현 리뷰의 시험 보강(§7)이다.

1. core `_final_verdicts` docstring. 프로토타입은 «수리 전 audit 은 check-verdict 를 다시 돌려 만든다»였다. 리뷰 core m1 1안(조건부 안내)과 어긋나서 «재실행 안내는 대상 BC 무변일 때만 · 바뀌었으면 멈춤»으로 고쳤다.
2. 러너 `e2_cases` docstring · «E2 준비» 사례 이름 · mi1 주석. 8c 문구(«verdict-log 마지막 exit 0 판» · «로그 없으면 빼지 않는다» · «verdict-log 에만 남는다» · «로그 병합 ∩ verdict.md 병합»)가 남아 있어 확정 표 한 곳 판독(§1.2)에 맞게 고쳤다. 기대 문자열은 바꾸지 않았다.
3. LEDGER 사유. 프로토타입 스크립트 `ledger_r8d.py` 의 사유 문자열 끝에 8c 사유 꼬리가 붙어 있었다. 실제 행은 프로토타입 패치 행과 같게 꼬리 없이 썼다. sha 는 같다.
4. 고아 병합 재분류 문구(core·web 같은 문자열 · 구현 리뷰 web n4). 설계·프로토타입의 «병합 대상 Mx 이 확정 기록에 없다 → 채택»을 «병합 대상 Mx 이 확정 기록의 채택 항목이 아니다 → 채택»으로 바꿨다. 대상이 제외로 남는 경우(F12 · K7)에도 맞는 문장이다. F10 · F12 · K6 기대 문자열도 함께 바꿨다.
5. web `compute_plan` 주석(구현 리뷰 web n5). 설계 §2.1 코드 조각보다 길다. 절 주석에 «(소비자 = 정적 로드만 하는 줄 밖 전부)», 줄 주석에 «— import·render·문자열 포함»이 붙어 있다. 프로토타입 `tools-A` 와 byte 같고, 설계 조각은 요약본이다. 동작 차이는 없다.
6. 봉인 파일은 넣지 않았다(지시 — 운영 세션이 main 커밋 뒤 재발행).

그 밖의 파일은 프로토타입과 같다 [실측].
- web 단계 판(`r8d/tools-A` · `tools-ADN` · `tools-ADNO` · `fx-web-A2.sh` · `fx-web-D2.sh` · `fx-web-O.sh`)을 1차에 그대로 옮겼다. 2차에서는 그 위에 §7 시험과 문구만 더했다.
- 옮기기 전에 두 가지를 확인했다. `tools-ADNO` 와 `fx-web-O.sh` 는 HEAD 에 `r8d-all.patch` 의 web 몫을 적용한 결과와 byte 같다. 단계 사이 diff 는 설계 §2.1 · §3.1 · §3′ 과 같다.
- core 문면 산출(ttl · md · rulepack)은 내 절차로 다시 만들었다. 결과 diff 가 프로토타입과 같다.

## 6. 남은 위험

- **봉인**: 트리에 봉인이 없다. ① 커밋 뒤 `manifest_seal.py --write` 봉인 커밋이 있어야 verify-base-core 가 green 이 된다(설계 §4 — 8c `a34e93db`→`ea0526f9` 와 같은 순서). web 파일은 봉인 글롭 밖이다.
- **릴리즈 창**(설계 §5-11): ① 은 `dddjango/scripts/` 를 바꿔 pre-gate digest 를 낡게 한다. 진행 중 G1~G2 레인이 착륙한 뒤 `make release` 를 한다. web 은 `make release-web` 이다.
- **옛 audit 폴더**: 확정 표가 없는 폴더(scratch 리허설 R8-R · R8-R2 산출)는 `resolution`·`residual` 이 조건부 안내와 함께 exit 1 이다. 설치본에는 도구가 없어 현장 영향은 0 이다(설계 §1.4 [실측 태그 61개]).
- **②-A 과잉**: 컨테이너 단위는 루트 꼬리 `web` 로 사실상 전 파일이 소비자가 된다(현장 353줄). 화면 없는 소비자(`web/urls.py` · DS 컴포넌트 · CSS/JS 주석)도 있다. 비용만 드는 fail-safe 라 관찰 대상이다(설계 §5-4).
- **D 규모 한계**: `warm` 은 바늘을 나눠 돌리지 않는다. 정적 파일 약 2.5만 개부터 E2BIG → exit 1(fail-closed)이다 [추정 — 리뷰 계산](설계 §5-8).
- 설계 §5 의 나머지(`--final` 뒤 G0 정지 재개 불가 · 손으로 고친 확정 표 미검출 · 상대 import·동적 include·URL 이름 미탐 · `--against` 민감도 · 파일 이름 `:` 파서 결함)는 그대로다.
- AD3 의 `grep -c … || echo 0` 는 적중 0 이면 `0\n0` 이 되어 비교가 실패한다. 결과는 red(9)라 fail-closed 이고, 프로토타입 그대로 두었다. R5 는 2차에서 exit 과 하한을 보게 고쳤다.
- 구현 리뷰 web 의 X5(`refs.warm(sorted(targets))` 삭제)는 동등 변이라 생존한다. 대상이 범위 안 파일이라 거의 늘 no-op 이다(결함 아님 · 리뷰 판정).

## 7. 구현 리뷰 처분 (09-30 · 운영 세션 처분 → 2차 반영)

| 리뷰 | 항목 | 등급 | 처분 | 반영 단계 · 결과 [실측] |
|---|---|---|---|---|
| core | m1 고아 교정 «대상이 M 일 때만» 가드 무시험 | minor | 채택 — F10b(정당한 `병합 → C1` 유지) + 짝 변이 V10 | ① · V10 → F10b red |
| core | n1 F10 이 확정 표를 직접 보지 않음 | nit | 채택 — 판정식에 `"| M4 | ddd-01#4 | 채택 |" in vf10` | ① · V12(`--final` 확정 표 안 씀)에서 F10 red |
| web | m1 대상이 비채택으로 남는 갈래 무시험 | minor | 채택 — web K7 + 변이 X6. core 짝은 먼저 재현 → **재현됨** → F12 + 변이 V11 | ① F12(V11 red) · ④ K7(X6 red) |
| core | m1 의 web 짝 | — | 채택 — K6c(검사기 키 병합 M8 유지) + 변이 VOG | ④ · VOG → K6c red |
| web | m2 `_plan_names` 경로 쌍 점 경로 `-w` 무시험 | minor | 채택 — R6(`경로:` 파일 쌍) | ③ · X2 → R6 red · ②-A·HEAD 도구 green(수호 시험) |
| web | n1 R3 판별 표본에 경로 꼬리 앞 낱말 문자 줄 없음 | nit | 채택 — `s_q_pathcomment.py` 에 `old_home/…` 줄 | ③ · X1 → R3 red |
| web | n2 include 소비자 절 단위 시험 없음 | nit | 채택 — AQ2″ | ② · X3 → AQ0·AQ2″ red · HEAD 도구 green(수호 시험) |
| web | n3 R5 하한·exit 미확인 | nit | 채택 — `E = 0` · `NG ≥ 1` · `NG ≤ 6` | ③ |
| web | n4 재분류 문구가 비채택 대상에 안 맞음 | nit | 채택 — core·web 같은 문구로 바꾸고 기대 문자열(F10 · F12 · K6)도 함께 | ① core · ④ web |
| web | n5 설계 조각과 주석 문자열 차이 기록 누락 | nit | 채택 — §5-5 | 기록 |
