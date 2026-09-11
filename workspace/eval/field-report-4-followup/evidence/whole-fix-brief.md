# Whole review combined fix wave — Task7 Step2

Read this first. Worktree /Users/hyun/.cache/dddjango-field4-followup-20260911. Fix only the confirmed whole-review findings within the12 approved issue directions. Complete reports are workspace/eval/field-report-4-followup/implementation-A-detection.md (A-M1..M4) and implementation-B-norms.md (B-M1,m1). C evidence review has no findings. Read both full finding sections for exact reproductions and expected counterexamples. No user policy choice is required.

## Findings to close

1. A-M1/F4-1: direct module pytestmark method mutation calls (append/pop) survive marker replacement. Unsupported dynamic/incremental state must be S5 with originalbytes preserved and no false materialization claim. Retain static empty/replacement/omission behavior, prior ordering/subscript-mutation fixes, generated-method final line ranges and actual CLI/report boundaries. Do not simulate arbitrary user test modules.
2. A-M2/F4-9: framework fixed **kwargs:Any slot bypasses actual business consumption. Known business read/comparison/call must receive ordinary #645 treatment; unknown escape stays candidate; ordinary framework forwarding and generated bodyless slots keep their scoped behavior. Independent #646/#650 and other rules remain. Carry binding through bounded existing flow or equivalent narrow veto, not blanket removal of native slot support.
3. A-M3/F4-10: module FunctionDef/AsyncFunctionDef/ClassDef replacing an imported composition builder leaves stale proof. Rebinding must invalidate old origin, producing unknown #153 candidate where appropriate; preserve real standard builder+execute control and uncalled nested-scope boundary.
4. A-M4/F4-14: module ClassDef replacing imported UoW leaves old origin and improperly certifies split regions. Unknown boundary must remain #546 candidate; preserve known sequential UoWs, nested/shared and type-count controls. No global/instance-identity solver.
5. B-M1/F4-1: supported alias U=StrangeUnitOfWork erases named-UoW unresolved candidate under explicit read-only uow=none. Preserve underlying named-UoW unresolved evidence across supported aliases; direct andalias yield same #197 candidate. Do not infer unrelated unknown P is a UoW; proven non-UoW andwrite controls stay clean. No confirmed violation from suffix alone.
6. B-m1/F4-16: four current check-layer-skeleton descriptions retain #638~#643. Align only those to #638~#641·#643 and mirror; no behavior/tests needed for docstring change.

## Ownership and implementation protocol

Allowed product/test paths:
- dddjango/scripts/design_pregate.py
- codex-dddjango/skills/dddjango/scripts/design_pregate.py
- dddjango/scripts/check-public-surface-annotation.py
- codex-dddjango/skills/dddjango/scripts/check-public-surface-annotation.py
- dddjango/scripts/check-context-isolation.py
- codex-dddjango/skills/dddjango/scripts/check-context-isolation.py
- dddjango/scripts/check-domain-model.py
- codex-dddjango/skills/dddjango/scripts/check-domain-model.py
- dddjango/scripts/check-layer-skeleton.py
- codex-dddjango/skills/dddjango/scripts/check-layer-skeleton.py
- workspace/tools/pregate_field_report_smoke.py
- workspace/tools/field_report_checker_smoke.py

Snapshot whole-fix-before/manifest.json covers all54 frozen paths; own12 listed above. Preserve allother53-or-fewer earlier source/normfiles and prior testmethodbodies. Need another path only if directlynecessary: send exactpath/reason before editing so coordinator snapshots it. No TTL/metadata changes expected; allnorms already state desired behavior.

Use systematic debugging/receiving review/TDD. Reproduce each actual failure before implementation with targeted behavior tests in existing two smoke harnesses. Then minimal corrections and byte mirrors. Run the two full covering smoke suites after finalsource change, relevant existing fixture lanes and pregate_fixture_run because parser/materialization/report surfaces change. Do not repeat other green suites without named reason. Preserve original fixture/source bytes; probes only scratch copies. No source-like generation inference, weakened raw record join, broad exemption or test golden relaxation.

Self-review complete fixdiff and scope/hash preservation; report commands/rawlogpaths/REDtoGREEN, final sourcehashes, allfindings addressed/remaining andlimits to whole-fix-report.md beside thisbrief. Sourcefreeze then shortDONE orissue. No subagents, Git mutations/commit/release, seal/fullmakeverify, originalreportcleanup, primary/master/F20 edits. Coordinator dispatches independent scoped reviewer after frozenreport.

## Global Constraints (verbatim)

- 사용자가 승인한 범위는 문제 검증 → 계획 적대 리뷰 → 결정 필요 없으면 구현 → 구현 독립 리뷰 3인 → 독립 최종 감사·필수 검증이다. 새로운 정책·범위 선택이 필요하면 계획 리뷰 후 보고한다.
- 현재 변경과 직접 관계없는 사용자 프로젝트, `docs/master.html`, 과거 완료 계획·리뷰는 변경하지 않는다. 보고서는 실제 검증 완료 항목만 제거한다. 커밋·릴리즈는 이 계획의 실행 단계에 넣지 않는다.
- `docs/DEVELOPMENT.md`가 개발 절차 정본이다. graph-owned md 직접 수정 금지. TTL → 저작 게이트 → render → rulepack → corpus/byte/의미 미러를 따른다. NAR 변경 시와 기존 render-sync가 요구하는 개정 graph 절의 기준선에만 LEDGER append, 새 Work가 실제 필요할 때만 ISSUED 채번.
- 설치본 의존성은 표준 라이브러리만. 검사기와 공용 스크립트는 `dddjango/scripts/`와 `codex-dddjango/skills/dddjango/scripts/` byte 동일. reference는 corpus mirror, 역할·SKILL은 플랫폼 형식을 유지한 의미 미러.
- Serena·Graphify opt-in 없음. 검색·로드·초기화하지 않는다. 실사용 spring_dream_server는 읽기만 하며 검사/테스트는 임시 사본에서 실행한다.
- 실제 확인한 출처와 추정을 구분한다. 이름·폴더·except 구문만으로 의미를 확정하지 않는다. 지원 밖 동작은 후보 또는 명시 사각이며 통과 증명이 아니다.
- 먼저 실패하는 동작 테스트를 확인한다. 기존 미러·소성·형식 검사만으로 새 검출 동작을 증명하지 않는다. 전체 검출 집합 보존을 요구하지 않고 아래 항목별 삭제·보존 집합을 검증한다.
- 각 작업의 구현을 검토해 중대한 결함을 닫고 다음 작업으로 간다. 세 작업이 같은 공용 파일을 병렬 편집하지 않는다. 구현 담당자와 리뷰 담당자는 분리한다.

