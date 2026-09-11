# Whole implementation review brief — Tasks1–6

Execution root: /Users/hyun/.cache/dddjango-field4-followup-20260911. Base HEAD3355710dcbaf023a16856cb2f307aa2a03fc0996. No commit was authorized; working bytes are the reviewed state.

Authority: workspace/eval/field-report-4-followup/brief.md preserves the12 approved issue directions (F4-1,F4-9..19). The current implementation plan is workspace/plan/2026-09-11-field-report-4-followup.md. Task7 requires3 independent whole implementation reviews, then independent evidence audit and final required validation. F4-20 was appended to primary report during work and is outside these12; preserve it.

Read the relevant full final package, not just implementer claims. Canonical and Codex meaning-mirror diffs are separated from byte duplicates; the inventory lists every changed tracked file and SHA pair. Review exact byte copies through inventory/evidence, and meaning mirrors semantically. Task-N-report.md contains final appendices and paths to raw logs, Task-N-review.md has independent local verdicts. No final full make verify success is claimed yet; Task7 runs after final source/seal.

A: actual detection and missed/opposite cases across changed AST/pregate/snapshot boundaries. B: normative instructions versus supported source/input/report behavior and mirrored meanings. C: evidence, supported scope, old true positives and source preservation. Each review is independent within its lens. Raise concrete B/M findings with file:line and evidence; separate inferred risk from actual scratch reproduction. No need to repeat all already-green suites. Focused scratch checks only for named unresolved doubts. No production/test/Git changes, no subagents or real-user-project execution. Only assigned review report may be written.

Metadata procedure rulings in progress.md: existing render-sync requires graphsection rebaseline despite earlier NAR-only shorthand (9appendrows); corpus frozen-source addressing needed2 further rows where migrated hash wasmissing, independently checked against unchanged source snapshot. Evaluate their evidence, not merely controller approval. No normative policy was changed by these metadata choices.

Norm scenario tables are manual application/text-contract checks, not fresh-agent role execution evidence. S1 is unverified, not proven behavior. Unknown origins/regions/multiplicity remain candidates. Whole review must not turn those limits into an unsupported success claim.

## Global Constraints (verbatim)

- 사용자가 승인한 범위는 문제 검증 → 계획 적대 리뷰 → 결정 필요 없으면 구현 → 구현 독립 리뷰 3인 → 독립 최종 감사·필수 검증이다. 새로운 정책·범위 선택이 필요하면 계획 리뷰 후 보고한다.
- 현재 변경과 직접 관계없는 사용자 프로젝트, `docs/master.html`, 과거 완료 계획·리뷰는 변경하지 않는다. 보고서는 실제 검증 완료 항목만 제거한다. 커밋·릴리즈는 이 계획의 실행 단계에 넣지 않는다.
- `docs/DEVELOPMENT.md`가 개발 절차 정본이다. graph-owned md 직접 수정 금지. TTL → 저작 게이트 → render → rulepack → corpus/byte/의미 미러를 따른다. NAR 변경 시와 기존 render-sync가 요구하는 개정 graph 절의 기준선에만 LEDGER append, 새 Work가 실제 필요할 때만 ISSUED 채번.
- 설치본 의존성은 표준 라이브러리만. 검사기와 공용 스크립트는 `dddjango/scripts/`와 `codex-dddjango/skills/dddjango/scripts/` byte 동일. reference는 corpus mirror, 역할·SKILL은 플랫폼 형식을 유지한 의미 미러.
- Serena·Graphify opt-in 없음. 검색·로드·초기화하지 않는다. 실사용 spring_dream_server는 읽기만 하며 검사/테스트는 임시 사본에서 실행한다.
- 실제 확인한 출처와 추정을 구분한다. 이름·폴더·except 구문만으로 의미를 확정하지 않는다. 지원 밖 동작은 후보 또는 명시 사각이며 통과 증명이 아니다.
- 먼저 실패하는 동작 테스트를 확인한다. 기존 미러·소성·형식 검사만으로 새 검출 동작을 증명하지 않는다. 전체 검출 집합 보존을 요구하지 않고 아래 항목별 삭제·보존 집합을 검증한다.
- 각 작업의 구현을 검토해 중대한 결함을 닫고 다음 작업으로 간다. 세 작업이 같은 공용 파일을 병렬 편집하지 않는다. 구현 담당자와 리뷰 담당자는 분리한다.

