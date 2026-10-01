결론(2026-10-01): 속도 개선 C1⑴·⑵ 를 설계 v2 대로 구현했다(⑶ 은 보류 그대로). 검사기 둘은 «후보·신호가 있는 파일에만» git 을 묻고, registry_gate 는 검사기 27종을 빈 코어 수(최대 8)만큼 동시에 돌리며 앵커·현재 두 벌도 동시에 돈다. **옛 코드와 직접 대조해 출력이 byte 같다** — 새 스모크 두 벌(경계 시나리오 30종 × 호출 3 = 90쌍 · 옛 직렬 게이트 대조 9행)이 전부 일치하고, 설계자 재생 입력(pre-gate 3판 · 격리 사본 registry_gate 레코드 3,511건)과 현장 스냅숏(field-clone) A/B 9/9 도 같다(§3). 시간은 ⑴ 이 부하와 무관하게 크다(field 검사기 둘 684 → 28초). ⑵ 는 빈 코어에 달렸다 — 부하 4~5 에서 registry_gate −45%, pre-gate −52~−63%(부하 12 전후 시작). 부하 20 이상에서 시작하면 옛과 같다(field +1.6% · 구현 리뷰의 같은 부하 교차 측정: 자동 +3.0% 편차 안 · 워커 8 고정 −68%). 새가 옛보다 느린 판은 없었다(run02 +32% 는 서로 다른 부하에서 잰 한 판 — §3). 구현 리뷰 판정 **승인**(minor 2 · nit 3 처리 — §6). 고친 곳을 일부러 되돌린 변이 6종은 모두 스모크를 red 로 만든다. 검증 클론에서 봉인 재발행 뒤 `make verify` **green 5/5**(445초). 봉인은 scorer · pipeline · packs · protocol 네 그룹과 실행 트리 digest 가 바뀐다 — 커밋 뒤 봉인 chore 가 필요하다. 설계와 다른 곳은 다섯이고 모두 품질 쪽(§5)이다. 규범(graph-owned) 변경은 없다.

# 속도 개선 C1 구현 기록 — 검사기 git 질의 순서(⑴) · registry_gate 병렬(⑵)

- 작성: 2026-10-01 · 격리 워크트리 `.claude/worktrees/agent-a41c137cc184384e9`(브랜치 `worktree-agent-a41c137cc184384e9`). **커밋 0 · push 0** — 변경은 `git add` 로 스테이징만 했다.
  - 워크트리는 `acbfffda`(main 보다 32커밋 뒤 · `behavior_guard.py`·`refactor_audit.py` 없음)에서 시작했다. 자기 커밋이 없어 `git merge --ff-only main` 으로 `86fc3c24` 에 맞췄다(새 커밋 없음). 아래 «옛» = `86fc3c24`.
  - 패치: scratch `impl-C1/c1.patch`(스테이징 전체 · 이 기록 포함).
- 입력: 설계 `design-tier1.md` v2 §3 C1(메인 체크아웃 · 미추적) · 도구 검토 `review-t1-tool/review.md`·`rereview.md`(N5 · N7 구속) · 절차 검토 `review-t1-proc/review.md`·`rereview.md` 의 C1 몫(K1a/K1b hunk · 릴리즈 창) · 설계자 프로토 `speed-t1/proto2`(참고만 — 코드는 저장소 문체로 다시 썼다).
- Serena·Graphify 는 쓰지 않았다(지시). `spring_dream_server` · herdr 워크트리 · `~/.codex`·`~/.claude` 는 쓰지 않았다(`manifest_seal.py --write` 가 검증 클론에서 설치본을 **읽기만** 한다). 현장 재료는 scratch 사본에서만 돌렸다 — 다만 사본을 뜨기 전 `problem-lanes/field-clone` 에 `git status` 를 한 번 돌려 git 이 그 인덱스의 stat 캐시를 갱신했다(내용 변경 0 · 기록해 둔다).

## 1. 바꾼 것

| 파일(미러 포함) | 내용 |
|---|---|
| `dddjango/scripts/check-composition-root.py` | `_filtered_di_findings`: BC 마다 후보(`composition_root.py` 이름 · 실재 파일 · `composition/` 밖)를 먼저 모은다. git 저장소에서 **후보 0 이면 BC 단위 트리 질의 1회만** 하고 넘어간다(옛 코드가 BC 마다 늘 하던 질의 — 저장소 결손이 옛처럼 `UsageError` → exit 1). 후보가 있으면 옛 코드와 똑같이 파일별 질의 → 트리 질의. git 명령·pathspec·에러 처리는 무변 |
| `dddjango/scripts/check-idempotency-scope-creep.py` | `_idempotency_artifacts`: 신호(이름 → 본문)를 먼저 보고 신호가 있는 파일에만 `_is_new_or_modified`. 신호 판정은 작은 함수 `_has_idempotency_signal` 로 뺐다. 결과 원소·순서 무변 |
| `dddjango/scripts/registry_gate.py` | `_run_registry`: 작업을 공용 풀(`_checker_pool`)에 **모두 submit → `wait` → REGISTRY 순서로 `result()`**(첫 예외 = REGISTRY 순서 첫 실패 · 실행 중 작업이 임시 폴더 정리와 겹치지 않음). sink 는 작업마다 `<sink>.<REGISTRY 인덱스:02d>.part` 를 주고 REGISTRY 순서로 **바이트 그대로** 이어 붙인다(`_merge_sink_parts` · 디코드 0). `main`: 앵커·현재 두 벌을 2-스레드로 동시에(같은 공용 풀 — 검사기 동시 실행 한도는 두 벌 합). 워커 수 `_registry_workers`: `DJR_REGISTRY_WORKERS`(양의 정수)면 그 값, 아니면 `max(1, min(8, int(cpu − 1분 부하)))` · `os.getloadavg` 부재·실패(`OSError`·`AttributeError`)는 부하 미상으로 보고 CPU 수 상한(N7). 모듈 docstring 에 환경 변수 한 줄 |
| `dddjango/scripts/pregate_symbol_kinds.json` | 검사기 소스 sha 두 줄 재소성(`gen_pregate_symbol_kinds.py` — 검사기를 고치면 함께 재소성하는 소성물 · 종류 목록 무변) |
| `codex-dddjango/skills/dddjango/scripts/` 위 넷 | byte 미러(`diff -rq` 0) |
| `workspace/tools/git_touched_smoke.py`(새) · `workspace/eval/fixtures/git_touched/expected.json`(새 골든) | ⑴ 스모크(§2-1) |
| `workspace/tools/registry_gate_smoke.py` | ⑵ 옛 게이트 직접 대조 R1~R6(§2-2) · `_pre_repair_gate` 를 일반화한 `_gate_copy`(P0′ 는 그대로 이 함수를 부른다) · `_mask_sidecar` 가 `candidate_records` 의 휘발 필드도 지운다(ⓓ 후보가 있는 픽스처에서 런마다 다른 `ts` 를 비교하지 않게) |
| `Makefile` | `verify-base-core` 에 `git_touched_smoke.py` 한 줄 + 세트 이름 목록 |

- 커밋 묶음은 설계 §4 대로 파일이 깔끔히 갈린다: **K1a** = 검사기 둘(+미러) · `pregate_symbol_kinds.json`(+미러) · `git_touched_smoke.py` · 골든 · `Makefile` / **K1b** = `registry_gate.py`(+미러) · `registry_gate_smoke.py` / 봉인 chore. K1a 의 `Makefile` hunk 는 verify-base-core 뿐이다(8e 의 verify-web hunk 와 겹침 0).

## 2. 픽스처(`make verify` 등재)

### 2-1. `git_touched_smoke.py` — verify-base-core · 90쌍

- 판형: 임시 git 저장소 시나리오 × 호출 셋(composition-root · composition-root `--error-profile auto` · idempotency). 기대값은 **바꾸기 전 코드로 기록한 골든**이다 — `--emit --from-commit 86fc3c24` 가 그 커밋의 `dddjango/scripts` 를 `git archive` 로 꺼내 돌린 결과다(골든의 `emitted_from` 에 커밋). 현행이 골든과 같으면 «옛 == 새».
- 비교: exit · stdout · 레코드(`DJR_FINDINGS_JSON` · 휘발 `run_id`·`ts`·`record_id`·`experiment_run_id` 제외)는 전부, stderr 는 ⑧·⑳ 밖에서만. 임시 경로는 `<TMP>`. git 은 전역·시스템 설정을 끄고(`GIT_CONFIG_GLOBAL=/dev/null` · `GIT_CONFIG_NOSYSTEM=1` — 사용자 전역 gitignore 가 `ls-files --exclude-standard` 를 흔들지 않게) 시각을 고정한다.
- 시나리오 30종(설계 ①~⑳ = 검토 ab1 27종 + 셋 — 멱등 채택 배너 · 하위 트리 결손 둘): clean · 미추적 후보 · 커밋 후보+같은 BC 다른 파일 수정 · staged 삭제 · 미스테이징 삭제 후보 · BC 를 넘는 staged rename(멱등 산출물 포함) · 커밋 후보를 다른 BC 로 `git mv` · HEAD 없음(스테이징 유/무) · 하위 폴더 TARGET · 글롭 메타문자·공백·한글·`*.py` 이름 · 글롭이 인벤토리 밖 시험 파일만 잡는 경우 · 비-git · 서브모듈 다섯(BC 자체 · BC 안 · 서브모듈 안 수정·미추적 후보 · `application/` 자체 후보 유/무) · 심볼릭 링크 BC·링크 후보 · `.gitignore` 된 후보·산출물 · 대소문자만 바꾼 후보 · linked worktree · staged 뒤 재수정 · off-tree `composition/` · **멱등 G1 채택 배너 면제(추가)** · 저장소 결손 다섯(아래).
- **⑳ 은 N5 대로 «옛 == 새»만 단언한다**(설계 v2 문구 «하위 트리 결손 → exit 1 기대»는 틀렸다):

| 결손 시나리오 | 옛 exit(composition-root 둘 / idempotency) | 새 |
|---|---|---|
| `corrupt_root_tree` 루트 트리 결손 · 후보 0 | 1 · 1 / 0 | 같음 |
| `corrupt_root_tree_mixed` 같은 결손 + 다른 BC 후보 | 1 · 1 / 0 | 같음 |
| `corrupt_subtree_nocand` 하위 트리 결손 · cache-tree 유효 | 0 · 0 / 0 | 같음 |
| `corrupt_subtree_cand` 하위 트리 결손 + 후보 · cache-tree 유효 | 0 · 0 / 0 | 같음 |
| `corrupt_subtree_staged` 하위 트리 결손 + 같은 폴더 스테이징(cache-tree 무효) | 1 · 1 / 0 | 같음 |

- 결과: **90/90 일치**(exit·stdout·레코드 90/90, 비교 대상 stderr 69/69). 옛 코드를 두 번 기록한 골든끼리도 byte 같다(결정성). 비교하지 않은 stderr 가 실제로 다른 곳은 8쌍 — 루트 트리 결손 둘 × 셋(«touched source 비교 불능: <파일>» → «touched directory 비교 불능: <BC>» · idempotency git 잡음 2·4행 → 0행) · `corrupt_subtree_staged` idempotency(잡음 행 수) · HEAD 없음+스테이징 idempotency(`fatal: bad revision 'HEAD'` 10행 → 2행). 검토 81쌍 결과와 같은 묶음이다.
- 골든 출처 가드(구현 리뷰 minor 1): 대조 전에 단위 시험 `GoldenSourceGuard` 2건이 돌고, `emitted_from` 이 커밋 SHA 가 아닌 골든은 재료 결손(exit 1)이다(§6).
- 레코드 46건 · exit 0 48쌍 · exit 2 36쌍 · exit 1 6쌍 — 판정이 실제로 갈리는 경로를 덮는다. 소요 약 40초(부하 9~20).

### 2-2. `registry_gate_smoke.py` R1~R6 — verify-base-cross · 9행

옛(직렬) 게이트 = `86fc3c24` 의 `registry_gate.py` 를 **현행 검사기 트리**에 덮어쓴 사본(P0′ `_pre_repair_gate` 판형). 새 게이트 실행마다 `$TMPDIR` 를 빈 전용 폴더로 줘 임시 폴더 누수를 센다. 비교 = exit · stdout(툴체인 행 마스킹) · stderr · `introduced.json` · `contract.json`(휘발 필드 마스킹).

| 행 | 재료 | 단언 | 결과 |
|---|---|---|---|
| R1 ×4 | good_bc + bad_rules 15종(절반 앵커 · 절반 작업 트리) — 레코드 463 | 새 워커 1 · 3 · 8 · 기본이 옛과 다섯 항목 모두 같음 · 누수 0 | ✓ |
| R2 | 같은 저장소 · REGISTRY 0번 검사기에 2초 지연 주입 · 워커 8 | 첫 작업이 늦게 끝나도 옛과 같음(병합 = REGISTRY 순서) | ✓ |
| R3 | 작은 저장소 · `check-naming` 이 sink 에 깨진 바이트 줄 | 옛·새 exit 2 · 다섯 항목 같음 | ✓ |
| R4 | 레코드 수백 건 저장소 · `check-mechanism-ownership` stdout 비-UTF-8(게이트 작업 예외) | 옛·새 traceback 1 · 마지막 줄(예외) 같음 · «Directory not empty» 0 · 누수 0 | ✓ |
| R5 | 작은 저장소 · `check-naming` 실행 시 예외(crash) | 옛·새 exit 2 · 합성 fail-closed 귀속 같음 | ✓ |
| R6 | 작은 저장소 · `DJR_REGISTRY_WORKERS=0` | stderr 주의 1행 · 나머지 옛과 같음 | ✓ |

- «timeout» 주입: 게이트에는 검사기별 timeout 이 없다(옛·새 같다). 느린 검사기는 R2 의 지연 주입이 덮는다.
- 소요: R 절 단독 98.6초(부하 22 실측 — 게이트 14회 · 옛 R1 14.6초 · 새 워커 8 7.0초 · «기본» 15.4초). 부하 20 넘어서는 «기본» 워커가 1 이라 옛과 같은 시간이 걸린다(설계 의도).

### 2-3. 변이 시험(scratch `impl-C1/mutate.py` · 상시 verify 밖)

| 변이 | 기대 | 결과 |
|---|---|---|
| composition-root 후보 필터를 «항상 건너뜀» | ⑴ 스모크 red | red 24쌍(미추적 후보 · 다른 파일 수정 · rename · HEAD 없음 · linked worktree …) |
| 후보 0 BC 트리 질의 생략(v1 프로토) | ⑳ red | red 2쌍(`corrupt_root_tree` exit 1→0) |
| idempotency git 질의 생략 | red | red 18쌍 |
| sink 조각 순서 뒤집기 | R red | R1×4 · R2 · R3 · R5 · R6 red |
| 바이트 병합 → strict 텍스트 | R3 red | R3 red(traceback · exit 1) |
| submit+wait → `map` | R4 red | R4 red(2/2회) |

## 3. A/B — 옛(`86fc3c24` scripts) ↔ 새(이 워크트리 scripts) 직접 대조

- 도구: scratch `impl-C1/ab_driver.py`(결과 `ab/ab.jsonl` · 원 출력 `ab/*`) · 사후 재대조 `ab_recheck.py`. 실행은 한 번에 하나(동시 프로세스 ≤ 8) · 전체 95분(11:14~12:50). 도중에 작성 세션이 API 한도로 끊겼지만 운전기 프로세스는 살아서 끝까지 돌았다(재실행 없음 · 로그 `ab-run.log` `EXIT=0`). 시간 옆 괄호는 실행 전→후 1분 부하(20코어 기계 · 현장 레인이 함께 돌았다).
- 재료: E4·E5 = 설계자 재생 입력(`speed-t1/replay/sd` 의 `--shared` 클론 `impl-C1/sd` · 8-C-0 명세 판) · F = 현장 스냅숏 `problem-lanes/field-clone` 의 APFS 사본(`impl-C1/field` · HEAD `3b4e37ab2` · 깨끗한 트리). F 의 앵커 `3d1154f23` = 6-2-2 레인 acceptance Red 커밋 바로 앞(`application/` 265파일 차이).
- 정규화: E4 는 설계자 E4 정규화 그대로(시각 · 임시 경로 · 플러그인 버전 · 실행 트리 digest · 격리 사본 `git init` 커밋 SHA · 레코드 휘발 필드). 운전기 첫 판은 `introduced.json` 의 `anchor`(= 격리 사본 `git init` 커밋 SHA — 런마다 시각이 달라 늘 다르다)를 빼지 않아 E4 세 판에 `introduced_same false` 를 적었다. `ab_recheck.py` 로 그 키만 빼고 다시 대조해 세 판 모두 같음을 확인했다(레코드·귀속·ⓓ 후보 전부 동일). E5·F 의 registry_gate 직접 실행은 사이드카 경로를 고정해 stdout 도 툴체인 행만 마스킹한다.

| 단계 | 재료 | 옛 → 새(초) · 부하 | exit | 대조(정규화 뒤) | 내용 규모 |
|---|---|---|---|---|---|
| E4 | pre-gate run02(개정 1 `39df528b9` · `--base HEAD`) | 491.4(21.8→15.8) → **646.4**(15.2→**34.7**) | 2 · 2 | stdout · stderr · 리포트 본문 · introduced **동일** | 귀속 20 · 레코드 20 · ⓓ 후보 17 · 리포트 447행 |
| E4 | pre-gate run11(개정 9 `6b76b8425`) | 812.5(32.9→12.3) → 300.7(12.0→43.9) | 2 · 2 | 동일 | 귀속 1 · 레코드 1 · ⓓ 15 · 431행 |
| E4 | pre-gate run13(개정 10 `85eeaf98f` · `--base 9b09a43df`) | 709.0(40.0→12.7) → 338.2(12.5→17.9) | 2 · 2 | 동일 | 귀속 1 · 레코드 1 · ⓓ 15 · 433행 |
| E5 | run13 격리 사본에서 registry_gate 만(`--anchor HEAD`) | 143.1(5.0→3.8) → 자동 **78.1**(3.8→5.5) · 워커 2 91.6(5.5→4.7) | 2 · 2 · 2 | stdout · stderr · introduced · contract **동일**(둘 다) | 레코드 **3,511** · 귀속 3,009 · ⓓ 후보 레코드 1,849 · stdout 4,658행 |
| F⑴ | field 사본(git 워크트리) · composition-root 직접 | 347.3(4.7→27.8) → **23.2**(27.8→31.6) | 0 · 0 | exit · stdout · stderr · 레코드 동일 | 레코드 0 |
| F⑴ | field 사본 · idempotency 직접 | 336.8(31.6→19.6) → **4.5**(19.6→20.6) | 0 · 0 | 동일 | 레코드 0 |
| F⑵ | field 사본 registry_gate(`--anchor 3d1154f23`) | 418.4(20.6→22.0) → 425.2(22.0→21.8) | 0 · 0 | stdout · stderr · introduced · contract 동일 | legacy 잔존 4,215 · 해소 1 · ⓓ 신규 26 · legacy 1,769 · stdout 88행 |

- **byte 동일: 9/9 대조 전부**(exit 포함). 다른 곳은 정규화 대상 휘발 값뿐이다.
- 시간 읽기:
  - ⑴ 은 부하와 무관하게 크게 준다 — field 에서 검사기 둘 합 684초 → 28초(빚 스캔·G2 직접 실행 몫 · 설계 E2 «260~467초 → 3~33초»와 같은 크기).
  - ⑵ 는 빈 코어에 달렸다 — 부하 4~5(E5) 에서 registry_gate −45%(자동) · −36%(워커 2), pre-gate run11 −63% · run13 −52%. **부하 20 이상에서 시작하면 자동 워커가 1 이라 옛과 같은 속도다**(F⑵ +1.6% · 설계 «꽉 참 0~−10%»와 맞음).
  - run02 의 옛 491.4 → 새 646.4초는 **서로 다른 부하에서 잰 한 판**이다(옛 실행 21.8→15.8 · 새 실행 15.2→34.7). 병렬이 느리게 만든 값이 아니다. 구현 리뷰(scratch `review-t1-tool/impl-C1/review.md` §2)가 같은 부하에서 번갈아 쟀다(현장 부분 복제 · 1분 부하 114~149). 옛 평균 227.8초 · 자동(시작 때 워커 1) 234.6초(+3.0% — 옛 두 판 사이 편차 17% 안) · 워커 8 고정 72.5초(−68%). «시작 뒤 부하 급증» 판형에서도 새가 옛보다 느린 판은 없었다(옛 300.6·307.1초 · 새 159.2·201.2초 · 출력 해시 모두 같음). 기제상 새 게이트가 옛보다 느려질 길은 메모리·디스크 경합뿐이다(리뷰 §2-1).

## 4. 검증

- **`make verify`(검증 클론 · 구현 리뷰 전 판 — 그 뒤 바뀐 것은 봉인 밖 `workspace/tools` 스모크 둘과 이 기록뿐)**: scratch `impl-C1/vnew` = 워크트리 클론 → 스테이징 패치 적용 → 커밋 → `.venv/bin/python workspace/tools/manifest_seal.py --write` → 커밋 → `make verify` — **green 5/5 · 445초**(부하 24→16). 그룹: ontology 109 · core 165 · backstop 165 · cross 432 · regen 445초. 로그 scratch `impl-C1/verify-new2.log` · `verify-new2-logs/`. 스모크 줄: git_touched 90/90 · registry_gate 42/42 · `[manifest] green`.
  - 같은 날 기준선(`86fc3c24` 그대로 · scratch `vbase`): green 5/5 · 429초(부하 28→15) — core 93 · cross 300 · regen 429초. 늘어난 몫은 core +72초(git_touched 단독 약 40초 + 부하) · cross +132초(R 절 + 부하)이고, 전체 벽시계는 regen 이 정해 +16초다.
  - 첫 실행(scratch `verify-new.log`)은 regen 이 red 였다 — `pregate_symbol_kinds.json` 소성물 드리프트(검사기 소스 sha). 재소성해 스테이징에 넣고, 클론을 기준에서 다시 만들어 봉인부터 다시 돌렸다(`docs/DEVELOPMENT.md` §4 «봉인은 마지막 단계»).
- **워크트리 자체(구현 리뷰 처분 뒤 · 봉인 재발행 없이 · 마지막 실행)**: `make verify` → ontology · backstop · cross(registry_gate 42/42) · regen green, core 만 red 다. core 의 red 는 `manifest_seal.py --check --draft` 의 봉인 드리프트 11건뿐이다(scorer · pipeline · packs · protocol + `script_trees` 둘). 그 앞 단계는 다 green 이다(git_touched 가드 시험 2 + 90/90 포함). 452초 · 부하 27→15 · 로그 scratch `impl-C1/verify-worktree.log`·`verify-worktree-logs/`. `set -e` 로 멈춘 core 뒤 단계는 손으로 돌렸다. `ab_score --self-test` · 미러 `diff -rq` · REQUEST_GUIDE `cmp` · `request_guide_contract` self-test·계약은 rc 0 이다. `manifest_seal.py --self-test` 는 M1~M8 red · **M0(무변이 대조) 위양성**으로 rc 2 다. M0 은 커밋된 봉인본을 워크트리 실물과 대조하므로 같은 봉인 드리프트다(재발행한 검증 클론에서는 이 단계를 포함한 core 가 green).
- **봉인 영향**: scorer(검사기 둘) · pipeline(`registry_gate.py`) · packs(`pregate_symbol_kinds.json`) · protocol(`Makefile`) 네 그룹 + `script_trees[source-claude|codex]`. 커밋 뒤 봉인 chore 커밋이 필요하다. 실행 트리 digest 도 바뀐다 → 설계 §2 릴리즈 창(진행 중 레인 마지막 예보가 «툴체인 stale» — core 릴리즈는 8-C-0 G2 착륙 뒤).
- 미러: `diff -rq dddjango/scripts codex-dddjango/skills/dddjango/scripts` 0.

## 5. 설계와 다른 점(까닭)

1. **⑳ 기대값** — 설계 «루트·하위 트리 결손(후보 유/무) → exit 1 기대» 대신 «옛 == 새»(골든)로 고정하고, 하위 트리는 cache-tree 유효(둘 다 0) · 무효(같은 폴더 스테이징 · 둘 다 1)를 갈라 넣었다. 검토 N5(구속).
2. **부하 측정 불능 폴백** — 프로토의 `except OSError: cpu // 2` 대신 `except (OSError, AttributeError): 부하 미상 → CPU 수 상한`(최대 8). 검토 N7(구속) · 지시 «cpu count bound».
3. **잘못된 `DJR_REGISTRY_WORKERS`** — 프로토는 조용히 자동으로 갔다. 자동으로 가되 stderr 에 주의 1행을 낸다(값을 적은 사람이 무시된 줄 모르는 일을 막는다). 출력·판정은 무변(R6).
4. **골든 기록 방법** — «바꾸기 전 코드로 `--emit`» 을 `--emit --from-commit 86fc3c24` 로 기계화했다(골든에 출처 커밋이 남고 다시 만들 수 있다). 시나리오에 «멱등 G1 채택 배너 면제»를 더했다(설계 ⑲ 의 면제 갈래).
5. **소성물 재소성** — 설계 표에 없던 `pregate_symbol_kinds.json`(검사기 소스 sha 소성물)을 함께 고쳤다. 검사기를 고치면 따라가야 하는 파일이라 빠지면 regen 이 red 다(실측). 봉인 packs 그룹이 그래서 더 바뀐다.
- 그 밖: 프로토의 모듈 공용 풀·`part_of` 클로저·`import concurrent.futures as _cf` 는 저장소 문체로 다시 썼다(`_checker_pool` · `_run_checker` · `_merge_sink_parts` · 주석·타입 표기). 동작은 프로토 v2 와 같다.
- 설계 검증 계획의 «8-C-0 pre-gate 21판 전부 재생»은 하지 않았다 — 설계자 재생 입력 3판(E4) · 같은 격리 사본 registry_gate(E5) · 현장 스냅숏(field-clone)으로 대신했다(§3 · 시간). 21판 재생은 남은 일이다(§6).

## 6. 남은 위험

- **이득은 부하에 달렸다** — 자동 워커는 1분 부하 평균으로 정해져 늦게 반영된다(두 게이트가 동시에 시작하면 잠깐 겹칠 수 있다 · 프로세스당 상한 8). 부하 20 근처면 워커 1 이라 옛과 같은 속도다(F⑵ · R 절 · verify 실측). 다음 레인 측정에 `uptime` 을 같이 적어야 비율을 읽을 수 있다.
- **워커 수는 게이트 시작 때 한 번 정한다**(구현 리뷰 nit 3 — 지금 판형 유지). 시작 뒤 다른 레인이 코어를 채워도 줄지 않는다. 이것은 게이트를 느리게 하지 않는다. k 워커는 공정 분배에서 옛 직렬보다 큰 몫을 받는다(§3 교차 측정 · 리뷰 §2). 걸리는 것은 다른 레인에 대한 «예의»뿐이다. 재측정·재상한은 게이트를 더 느리게만 만든다. 같은 기계 레인 둘이 동시에 시작하는 최악이 16 프로세스이고, 몫은 `DJR_REGISTRY_WORKERS` 로 고정할 수 있다. 그래서 바꾸지 않는다.
- **verify 시간** — core +72초 · cross +132초(부하 15~28). 지금은 regen 이 최장이라 전체 +16초였지만, 부하가 더 높으면 cross 가 최장이 될 수 있다.
- **골든의 환경 가정** — ⑮(대소문자만 바꾼 후보)는 대소문자 무시 파일 시스템(macOS 기본), ⑳ 하위 트리 결손은 git 의 cache-tree 최적화(기록 시 git 2.54.0 · Python 3.14.7)에 기대는 값이다. git 이 이 최적화를 바꾸면 옛·새가 함께 바뀌므로 그때는 골든을 `--emit --from-commit 86fc3c24` 로 다시 뜬다(옛 코드를 다시 돌리므로 여전히 «옛 == 새»다).
- **기준 커밋 고정**(구현 리뷰 minor 2 — 처리) — R 절의 `_SERIAL_GATE_COMMIT = 86fc3c24`, 골든의 `emitted_from = 86fc3c24`. 뒤에 `registry_gate.py` 나 두 검사기가 다른 이유로 바뀌면 이 대조가 그 변경을 «차이»로 잡는다. 유지 규칙을 각 스모크 docstring 에 한 줄씩 적었다. 게이트 출력 판형을 바꾸는 개정은 같은 변경을 직렬 판형 사본에도 적용해 대조를 유지하거나, R 을 워커 1 대조로 낮추는 결정을 커밋 메시지에 적는다. 두 검사기 출력을 바꾸는 개정은 `--emit --from-commit <그 커밋>` 으로 골든을 다시 뜨고 «회귀 골든»이 됐음을 적는다.
- **골든 드리프트**(구현 리뷰 minor 1 — 처리) — `--emit` 을 `--from-commit` 없이 부르면 현행 결과가 골든을 덮어쓸 수 있었다. 비교 모드가 `_load_golden` 으로 `emitted_from` 이 커밋 SHA(`[0-9a-f]{7,40}`)가 아닌 골든을 재료 결손(exit 1)으로 거절하게 했다(두 안 가운데 단순한 쪽 — 손편집도 덮는다). 대조 전에 단위 시험 `GoldenSourceGuard` 2건이 돈다(«working-tree»·«HEAD»·빈 값·없음 → 거절 · SHA → 통과 · 커밋된 골든 → 통과). 출처 검사를 무력화한 변이(정규식 `.*`)에서 그 시험이 red 임을 확인했다(scratch `impl-C1/guard_mutation.py`).
- **푸시 시점**(구현 리뷰 §5) — 마켓 등재가 `ref: main` 이라 main push 가 곧 설치본 변경이다. 커밋은 지금 해도 되지만, push 는 릴리즈 창(8-C-0 G2 착륙 뒤)까지 미룬다. 그 전에 push 하면 그동안 사용자가 `/plugin` 갱신을 하지 않는다는 전제가 필요하다.
- **봉인 manifest 겹침**(구현 리뷰 §6) — 규칙 묶음 워크트리(`agent-a8f8a7589a3afe3d9`)와 파일이 겹치는 곳은 `workspace/eval/ab/T2-0b-manifest.json` 하나다. 나중에 착륙하는 쪽은 앞 쪽 봉인을 손으로 합치지 않는다. 합친 트리에서 `manifest_seal.py --write` 를 다시 돌려 봉인 chore 하나로 정리한다. 내용 상호작용은 0 이다(두 검사기·`registry_gate.py` 는 `rulepack.json` 을 읽지 않는다 — 리뷰 실측).
- **crash 경로 시간** — 한쪽 벌이 예외로 죽어도 다른 벌이 끝날 때까지 기다린 뒤 예외를 올린다(임시 폴더 경합을 막는 값 · 결과·exit 는 옛과 같다).
- 설계 밖 발견 §7-2(a)(registry_gate·pre-gate 안 idempotency 무발화)는 그대로다 — ⑴ 은 그 검사기의 git 질의 순서만 바꿨다.
- ⑶(G0 빚 스캔 병렬 러너)은 보류 그대로.

## 7. 문서·규범 점검

- `registry_gate` 의 직렬 실행을 말하는 문서·규범은 없다. Coordinator `D` :132 «정확한 checker registry와 소유권(순서 고정)»과 :198 «정확한 27-registry 순서»는 **로스터·보고 순서**(registry_gate 표·레코드도 REGISTRY 순서 그대로 — R1 이 byte 로 확인)이고, 6번 직접 실행(«`Bash`로 정확히 1회 실행»)은 registry_gate 밖이라 이번 변경과 무관하다. **graph-owned 절 변경 필요 0**.
- `DJR_REGISTRY_WORKERS` 는 선택 변수라 규범·발주 템플릿에 넣지 않았다(설계 «플러그인 규범은 이 변수를 요구하지 않는다»). 발주 템플릿(`workspace/plan/templates/request-template.md` — 봉인 protocol 그룹)에는 «실행 환경» 줄이 없다. 변수 설명은 `registry_gate.py` 모듈 docstring 한 줄로 두었다. `docs/DEVELOPMENT.md` 는 개별 스모크를 나열하지 않아 고칠 곳이 없다.

## 8. 자료(scratch `impl-C1/`)

- `old/`(옛 scripts `git archive 86fc3c24`) · `c1.patch`(최종) · `mutate.py`·`mutate.log`·`mutate-map.log`(변이) · `vbase/`·`verify-baseline.log`·`verify-baseline-logs/`(기준선 verify) · `vnew/`·`verify-new.log`(첫 실행 red)·`verify-new2.log`·`verify-new2-logs/`(최종 verify) · `seal-drift.txt` · `gt-old-1.json`·`gt-old-2.json`·`gt-new-1.json`(⑴ 옛·새 전체 기록 — stderr 포함) · `size_probe.py`(R 픽스처 크기) · `ab_driver.py`·`ab_recheck.py`·`ab/`·`ab-run.log`(A/B) · `sd/`(설계자 `replay/sd` 의 `--shared` 클론) · `field/`(field-clone APFS 사본)
