# dddjango 병렬 coordinator run 지원 계획 (3축 적대 리뷰 중재판 v4)

> v1 대비: 과적합 O-1~7·정합성 M-1~7·실효성 E-1~8을 중재했다. 독립 patch 증명이라는 성립하지 않는 목표를 폐기하고 shared working-tree generation 증명으로 계약을 낮췄다. 테스트별 inventory·own/foreign provenance 분류·backstop finding 귀속을 제거하고, run 전체 final verification generation 한 쌍과 first-touch 이후 원장 hash-chain으로 축소했다. 같은 기능 폴더의 고정 산출물 충돌은 run workspace+optimistic promotion으로, pair 오삭제는 token-aware cleanup helper로 막는다. endpoint ABA·공유 DB/cache·외부 프로세스는 현행 boundary와 같은 공개 한계로 남긴다.

**Goal:** 같은 working tree에서 서로 다른 dddjango run이 G0·G1·구현을 병행할 수 있게 저장소 전역 장기 lock을 제거한다. 각 run은 자기 migration-boundary pair와 임시 설계 workspace만 정리하며, 최종 G2는 독립 patch가 아니라 명시한 shared working-tree generation에서 현재 의무와 전체 suite가 통과했다는 사실만 증명한다.

**Architecture:** 정상 실행은 `preflight → run-id workspace의 unique snapshot`으로 시작하고 global orphan recovery를 호출하지 않는다. 모든 쓰기는 결정적 helper가 반환한 `absent|SHA-256` path-state hash-chain으로 겹침을 탐지한다. G2 finalization은 테스트·19종·reviewer·final boundary verify 전체를 하나의 endpoint generation으로 묶어 전후 fingerprint가 다르면 전부 stale 처리한다. current-run/canonical equality는 Phase 2 진입·generation 시작·G2 승인 뒤에 재검증한다. 장기 lock이나 liveness 추정은 없고, exact pair 삭제는 boundary helper가 expected run-id를 검증한다.

## 3축 중재 결정

1. **독립 patch 증명 기각(O-1·M-3·E-1):** 같은 working tree에서 B의 안정된 변경을 포함한 A Green은 A patch만의 Green이 아니다. dddjango는 원래 현재 working tree를 구현·검증하므로 G2를 `generation digest + current run 변경 원장`에 결박된 shared-state 증거로 보고하고 독립 적용 가능성을 주장하지 않는다. 독립 patch 증명이 필요하면 별도 Git worktree를 사용한다.
2. **개별 테스트 inventory 기각(O-2·M-4·E-1):** targeted/current-obligation 전 행→전체 suite→19종/layer→reviewer→final boundary verify를 한 final verification generation으로 실행한다. 시작과 G2 직전에만 fingerprint를 비교하고 다르면 이 generation의 모든 증거를 버린다. 한 번 새 generation으로 재실행하고 다시 변하면 `waiting-concurrent`로 pause한다.
3. **provenance 분류 기각(O-3·O-4):** `ledger에 있으면 own, 아니면 foreign`으로 작성 주체를 증명하지 않는다. G0 test delta의 원장 밖 변경은 `concurrent/unknown`으로만 보고하고 자동 수용·귀속·수정하지 않는다. 현재 의무 test/config와 겹치면 성공 여부와 무관하게 generation을 stale 처리한다. 그 밖의 안정된 변경은 shared generation의 명시적 dependency로 보고한다.
4. **원장 연속성 채택(M-1·E-3):** 각 path의 첫 touch는 그 순간의 `lstat` kind·mode·payload 또는 `absent` preimage를 generation dependency로 기록한다. 이후 같은 run의 모든 변경은 `next.before == previous.after`여야 한다. create/delete/type/mode를 포함한 불일치는 overlap blocker다. 첫 touch 전에 이미 존재한 다른 run 변경은 현재 shared generation의 입력이지 현재 run의 독립 소유라고 주장하지 않는다.
5. **endpoint 한계 공개(M-4·M-5·E-2):** fingerprint는 HEAD·exclusion-filtered index와 non-opaque dirty/untracked path의 lstat kind·mode·regular bytes·symlink payload·submodule state를 포함한다. 전후가 같은지만 보며 중간 변경 후 원복(ABA), ignored 파일, DB/cache/port/외부 프로세스 상태는 증명하지 못한다. 프로젝트 runner가 공유 외부 상태 때문에 불안정하면 finalization을 재실행·pause하거나 worktree/프로젝트 고유 격리를 사용한다.
6. **run-id는 충돌 방지 ID(O-6):** timestamp+고엔트로피 opaque suffix를 exact 길이의 보안/소유권 증명으로 과장하지 않는다. script는 portable run-id 형식만 검증한다. receipt와 대화 run state가 exact path를 고정하고 cleanup helper의 expected run-id가 foreign pair 오삭제를 막는다.
7. **같은 기능 폴더 격리(E-8):** 각 run은 `<산출물 폴더>/.runs/<run-id>/scope.md|design-spec.md|epoch pair`에서 작업한다. G0 `seed`와 G1 `commit`은 같은 짧은 feature-local lock으로 canonical pair 읽기/교체만 직렬화한다. G1 승인 뒤 canonical anchor가 그대로면 run 문서 pair를 canonical로 promote하고, 달라졌으면 architect가 최신 canonical에 현재 변경을 rebase한 뒤 영향 설계 리뷰와 G1 승인을 다시 수행한다. 자동 병합하지 않는다.
8. **상태 전이 폐쇄(M-6·E-7):** `active → pre-audit-clean(pending final verify) → waiting-concurrent → active`는 pair를 보존하고 final generation 전체만 재실행한다. `invalidated(exit 2)`와 `run-terminated`는 결과 보고 뒤 cleanup helper로 exact own pair/run temp만 지우며 재개는 새 run-id/baseline이다. exit 1은 삭제하지 않고 exact 경로를 보고한다.
9. **recover 강등(O-7):** recursive `recover`는 삭제하지 않는 quiescent maintenance 진단으로만 남기고 정상/재개 흐름에서 제거한다. 기존 병리 테스트를 확장하지 않는다.
10. **기준선 드리프트 분리:** 구현 전 발견된 Q6 fixture version 기대값 `1.1.0`↔현행 manifest `1.1.1` 불일치는 본 변경과 별도 baseline 보정 1건으로 명시한다.

## Task 1 — 제품 정본과 Coordinator 계약

**Files:** `workspace/reference/spec.md`, `dddjango/commands/dddjango.md`, `codex-dddjango/skills/dddjango/SKILL.md`, `README.md`

- [x] 전역 coordinator/stale/atomic lock 계약과 정상 경로 global recover를 제거한다.
- [x] run-id workspace 경로, unique snapshot, foreign epoch 비열람·비추적, expected run-id cleanup 계약을 추가한다.
- [x] 같은 기능 canonical 문서 hash anchor와 optimistic promote/rebase를 추가한다.
- [x] ledger first-touch dependency와 per-path 연속 hash-chain/overlap blocker를 추가한다.
- [x] final verification generation의 시작 fingerprint→테스트 전 행+suite→백스톱+reviewer+final verify→G2 직전 동일 fingerprint 순서를 추가한다.
- [x] concurrent/unknown delta, current-obligation test/config overlap stale, shared-generation dependency 보고를 추가한다.
- [x] 상태 전이와 endpoint-only/ABA·ignored·외부 상태 한계를 공개한다.

## Task 2 — 쓰기 역할과 discipline reviewer 계약

**Files:** `dddjango/agents/acceptance-tester.md`, `dddjango/agents/coder.md`, `codex-dddjango/skills/dddjango-acceptance-tester/SKILL.md`, `codex-dddjango/skills/dddjango-coder/SKILL.md`, `dddjango/agents/discipline-reviewer.md`, `codex-dddjango/skills/dddjango-discipline-reviewer/SKILL.md`

- [x] acceptance/coder가 path별 ordered 변경 원장과 observed first-touch preimage를 반환하고, coordinator가 역할 사이 hash-chain을 검증할 수 있게 한다.
- [x] discipline reviewer의 coordinator lock 증거 요구를 제거하고 current run pair/run workspace만 cleanup 대상인지 감사한다.
- [x] reviewer가 generation fingerprint, 원장 hash-chain, concurrent/unknown delta, current-obligation test/config overlap 부재, canonical promotion anchor를 감사한다.
- [x] current-obligation exact ID collect/execute/pass와 승인된 테스트 diff/fixture/config 대조는 병렬 실행을 이유로 완화하지 않는다.

## Task 3 — boundary helper와 행동 테스트

**Files:** `dddjango/scripts/check-migration-boundary.py`, `codex-dddjango/skills/dddjango/scripts/check-migration-boundary.py`, `workspace/tests/test_migration_boundary.py`

- [x] snapshot/verify의 boundary path에서 폐기된 coordinator lock을 제거한다.
- [x] `cleanup TARGET_DIR STATE_FILE RUN_ID` action을 추가한다. portable run-id와 filename 결박, root+receipt 검증, exact state/receipt 삭제, `lstat` 부재 후조건을 helper가 소유한다.
- [x] verify 1/corrupt pair와 run-id mismatch cleanup은 거부·보존하고, verify 0/2 뒤 coordinator가 cleanup을 호출할 수 있게 한다.
- [x] barrier로 시작을 맞춘 두 subprocess snapshot이 각각 verify 0인지 확인한다.
- [x] A cleanup 후 B pair bytes 보존+B verify 0, token mismatch 거부, malformed foreign pair가 A snapshot/verify/cleanup에 영향 없음이 행동 테스트로 고정된다.
- [x] `recover` 설명만 quiescent maintenance로 낮추고 기존 recovery 구현/병리 테스트는 유지한다.
- [x] Claude/Codex script byte parity를 유지한다.

## Task 4 — runtime policy 회귀 테스트

**Files:** `workspace/tests/test_runtime_policy.py`

- [x] 최소 semantic anchor만 고정한다: 장기 lock/정상 recover 부재, run workspace, exact-own cleanup helper, canonical promotion conflict, generation 전체 폐기, hash-chain overlap.
- [x] exact token 길이·특정 생성 함수·표현 순서를 불필요하게 고정하지 않는다.
- [x] 양 coordinator와 양 discipline reviewer, 양 쓰기 역할을 순회한다.
- [x] `waiting-concurrent` pair 보존, terminal 0/2 cleanup, exit 1 보존 상태가 모순 없이 존재하는지 고정한다.

## Task 5 — generation fingerprint 계약

**Files:** Coordinator/spec/reviewer 문구, `dddjango/scripts/check-working-tree-generation.py`와 Codex byte mirror, `workspace/tests/test_runtime_policy.py`, `workspace/tests/test_parallel_run_helpers.py`; 별도 범용 registry/daemon은 만들지 않는다.

- [x] fingerprint 입력을 HEAD·index·non-opaque dirty/untracked path의 path/kind/mode/content-or-link/submodule identity로 닫는다.
- [x] `.git`, cache, foreign `.dddjango/*/.runs/*`, current run의 epoch/base/coordination state와 세 opaque 집합은 제외하되 current-run+canonical scope/design은 byte-equal 전제로 강제 포함한다.
- [x] 시작/G2 직전 digest가 다르면 테스트·백스톱·reviewer 증거 전부 stale, 1회 재실행 뒤 재변경이면 waiting-concurrent임을 고정한다.
- [x] endpoint 동일성 이상의 ABA/ignored/external-state 보장을 주장하지 않는다.

## 구현 후 3축 적대 리뷰 중재 (v3)

- **과적합/정합성 공통 blocker — check-then-act promotion:** G0 읽기와 G1 쓰기를 모두 `promote-run-artifacts.py`의 동일한 feature-local `flock`에 넣는다. `seed`는 canonical pair를 함께 읽고 anchor+exact 작업본을 만들며, `commit`은 lock 안 CAS 재확인 뒤 pair를 교체한다. 같은 anchor의 동시 commit은 정확히 한 run만 0, 다른 run은 conflict 2여야 한다. conflict의 `rebase`는 최신 canonical을 별도 exact base pair로 받아 current 작업본을 보존한다.
- **실효성 공통 blocker — 서술뿐인 fingerprint:** `check-working-tree-generation.py`가 verified boundary receipt·HEAD·exclusion-filtered index·선택된 working-tree bytes를 canonical hash로 계산한다. current-run+canonical 문서는 강제 포함, staged 상태까지 foreign run/temp/opaque/cache는 제외한다.
- **승인 창 stale:** G2 승인 뒤 cleanup 전에 same-baseline verify와 동일 helper fingerprint를 다시 확인한다. 바뀌면 승인·증거를 폐기하고 새 generation/G2 승인으로 돌아간다.
- **late overwrite:** generation 시작 전 touched path 현재 hash와 원장 terminal `after`를 대조한다.
- **상태 모순:** exit 2는 `invalidated→중립 보고→exact cleanup→새 run-id`; exit 1과 승인/`waiting-concurrent`만 pair를 보존한다.

## 2차 구현 후 3축 적대 리뷰 중재 (v4)

- **stable canonical mismatch:** current-run A와 후발 canonical AB가 둘 다 안정돼도 통과하지 않도록 promotion `check`와 generation helper 자체의 byte equality를 Phase 2 진입·generation 시작/종료·G2 승인 후에 강제한다. conflict는 rebase·영향 lens review·G1 재승인·Phase 2 증거 재실행으로 돌아간다.
- **lock 밖 source TOCTOU:** commit의 source 검증/읽기와 교체 뒤 source/canonical 재확인을 같은 feature-local lock 안으로 옮긴다. overlap이면 pair를 rollback하고 exit 1이다.
- **process crash torn pair:** 교체 전 transaction marker, 교체 후 pair receipt를 fsync한다. mixed pair crash는 다음 seed/check/commit에서 fail-closed하고, previous pair가 온전한 pre-replace crash와 완료 receipt가 있는 crash-tail marker는 안전하게 회수한다. marker 없는 stale receipt는 branch checkout·외부 canonical 변경을 차단하지 않는다.
- **fingerprint 결박/제외:** boundary state와 current run의 exact run-id pair를 기계적으로 결박하고 index entry에도 foreign/opaque/cache exclusion을 적용한다. staged foreign, mode, symlink, cache, opaque 경계를 행동 테스트로 고정한다.
- **원장 생성/삭제 공백:** before/after를 bare content hash가 아니라 `absent|kind·mode·payload` path-state hash로 정의한다.

## Task 6 — 문서·결정 이력·기준선 보정

**Files:** `workspace/DEVLOG.md`, `workspace/tests/test_q6_fixture_builder.py`, 필요 시 `workspace/eval/**`

- [x] DR-66에 장기 lock 회귀, shared-generation 결정, run workspace/promotion, exact cleanup, 적대 리뷰 중재와 공개 한계를 기록한다.
- [x] Q6 기대 version을 현행 양 manifest `1.1.1`로 보정하고 별도 baseline drift였음을 기록한다.
- [x] 역사 기록을 제외한 runtime/test 표면에서 coordinator lock/stale lock/normal recover 잔존 0을 확인한다.
- [x] 플러그인 버전 변경·릴리스·마켓 배포는 제외한다.

## Task 7 — 결정적 검증

- [x] workspace unittest 전체 통과(구현 전 baseline 182개 중 Q6 version drift 1 fail 기록).
- [x] `corpus_mirror_sync.py --check` 11/11.
- [x] 양 runtime Python script byte parity와 compile.
- [x] `claude plugin validate dddjango --strict`.
- [x] `git diff --check`, 잔존 grep, 변경 파일 전수 diff review.

## 구현 후 3축 적대 검증 오라클

- 두 concurrent snapshot이 독립 verify된다.
- A cleanup은 wrong run-id/B pair를 거부하고 B bytes를 보존한다.
- 같은 기능 두 run은 canonical 문서를 직접 덮지 않고 hash conflict 때 rebase 전 promote하지 않는다.
- A first-touch 이후 B가 같은 path에 끼어들면 ledger hash-chain이 끊겨 overlap blocker다.
- final generation 중 endpoint가 바뀌면 테스트 하나가 아니라 모든 테스트·백스톱·reviewer 증거가 stale다.
- stable B 변경을 포함한 Green은 `shared generation dependency`로 보고되며 A patch 독립 Green이라고 표현되지 않는다.
- current-obligation test/fixture/config가 concurrent/unknown delta에 포함되면 pass여도 stale다.
- ABA·ignored/shared DB/cache 한계는 숨기지 않고 worktree/프로젝트 격리를 독립 증명의 유일한 경로로 안내한다.

## 완료 증거

- 계획 전 과적합·정합성·실효성 리뷰와 구현 후 반복 3축 재감사를 수행했고, 최종 판정은 blocker/important 0이다.
- workspace unittest 211/211 PASS, corpus mirror 11/11 in-sync, 양 runtime Python script 22개 byte parity·총 44개 compile PASS다.
- Claude strict plugin validation과 `git diff --check`가 통과했고 exact 폐기 lock filename은 runtime 표면에 남지 않았다.
- plugin version 변경·릴리스·마켓 배포와 migration 의미 검증은 범위 밖으로 유지했다.
