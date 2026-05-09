# Source Coverage Crosswalk: architecture-db

## Status

- Skill: `architecture-db`
- Runtime target: `dddjango/skills/architecture-db/`
- Source status: ready
- Runtime reference split: follows `workspace/docs/plugin-structure.md` without deviation
- Runtime references: `schema-modeling.md`, `constraints-indexes.md`, `transactions-locking.md`, `rollout-constraints.md`
- Rubric status: opened only after source self-review, skill-creator review, and independent subagent review; source-backed runtime issues fixed

## Sources Used

- `workspace/develop/skill_goal_instructions.md`
- `workspace/docs/spec.md`
- `workspace/docs/plugin-structure.md`
- `workspace/docs/skill-contracts.md`
- `workspace/docs/skill-hierarchy.md`
- `workspace/docs/skill-authoring.md`
- `workspace/docs/reference-index.md`
- `workspace/docs/ddd-implementation-standard.md`
- `workspace/docs/workflow.md`
- `workspace/docs/validation-plan.md`
- `workspace/reference/architecture-db/reference/final.md`

## Authoring And Product Docs

| Source heading | Status | Runtime location | Reason |
|---|---|---|---|
| `skill_goal_instructions.md` `## 범위` | included | runtime path, this crosswalk | Plugin-bundled target and crosswalk location followed. |
| `## 실행 규칙` | included | this workflow | One skill at a time; rubrics not used during draft. |
| `## 구현 순서` | included | plan order | This follows `architecture-implementation-patterns`. |
| `## Skill별 작성 루프` | included | this crosswalk, review notes | Source scope, draft, review, and rubric sequencing tracked. |
| `## Source Coverage Crosswalk` | included | this file | Source headings and runtime treatment tracked. |
| `## SKILL.md 작성 규칙` | included | `SKILL.md` | Frontmatter has only name/description; body is concise and procedural. |
| `## Runtime Reference 작성 규칙` | included | `references/*.md` | Four one-level references summarize source. |
| `## Agents Metadata 작성 규칙` | included | `agents/openai.yaml` | Metadata aligns with source and runtime skill. |
| `## 한국어 사용자 기준` | included | `SKILL.md` description | Korean triggers for ERD, 정규화, 인덱스, constraint, transaction, locking, 동시성, migration risk included. |
| `## Provisional Skill 처리` | omitted | n/a | This skill has dedicated source reference and is not provisional. |
| `## Cross-Skill Routing 기준` | included | `SKILL.md` Routing | Adjacent workflow, DDD, API, Django implementation, and test boundaries included. |
| `## Review 기준` | included | Review Notes | Review types and findings tracked. |
| `## Completed 조건` | included | Review Notes, validation report | Completion requires zero remaining blocking/major/minor findings. |
| `## 검증` | included | validation commands | Only executed validation will be reported. |
| `## 완료 보고` | included | final report | Required report fields will be included. |
| `## Goal Objective Template` | omitted | n/a | Goal prompt authoring content is not runtime behavior. |
| `spec.md` `## 관련 문서` | included | Sources Used | Linked product docs are covered. |
| `## 1. 목표` | included | `SKILL.md`, references | DB decisions map domain invariants to relational design. |
| `## 2. 설계 원칙` | included | `SKILL.md`, references | Aggregate consistency, transaction, and outbox handoff reflected. |
| `## 3. 스킬 종류` | included | `SKILL.md` Routing | DB responsibility and adjacent skill boundaries included. |
| `## 4. 산출물 기준` | included | `SKILL.md`, references | Data constraints, transaction, and rollout artifacts included. |
| `plugin-structure.md` `## 1. 개발 위치` | included | runtime path | Runtime files live under plugin artifact because plugin runtime requires it. |
| `## 2. 목표 구조` / `## 2.1 Runtime 동기화 기준` | included | `dddjango/skills/architecture-db/` | Plugin-bundled structure used; no cache edits. |
| `## 3. Skill 파일 기준` | included | `SKILL.md` | Trigger, routing, references, and runtime rules only. |
| `## 4. Reference 파일 기준` | included | `references/*.md` | One-level references directly linked. |
| `## 5. Claude Code와 Codex 공통성` | included | `SKILL.md`, references | Shared skill name and responsibility preserved. |
| `## 6. 작성 순서` | included | this workflow | Docs/reference read before rubric review. |
| `## 7. Runtime Reference Split Plan` | included | four reference files | Exact split for `architecture-db` used. |
| `## 8. 금지 사항` | included | file tree, `SKILL.md` | No auxiliary docs; no false validation claim. |
| `skill-authoring.md` `## 1. 작성 원칙` | included | `SKILL.md` | Trigger/routing and boundaries are in description/body. |
| `## 2. Frontmatter 입력 표` | included | `SKILL.md` description | DB signals and anti-routes included. |
| `## 3. Cross-Skill Precedence` | included | `SKILL.md` Routing | DDD precedes DB when invariants are unclear; implementation routes away. |
| `## 4. Agents Metadata Inputs` | included | `agents/openai.yaml` | Display name, short description, and default prompt align. |
| `reference-index.md` `## Architecture` | included | references | DB source reference used. |
| `## Implementation` | delegated-to-other-skill | implementation skills | Concrete Django/Python/test mechanics route away. |
| `## Reference 사용 원칙` | included | references | Runtime references summarize source and avoid copying `final.md`. |
| `## Reference Gap` | omitted | n/a | This skill has dedicated source reference. |
| `## DRF Guardrail` | delegated-to-other-skill | `implementation-django-ninja` | API framework choice outside DB design. |
| `## Reference에서 도출한 제품 결정` | included | `SKILL.md`, references | Relational DB supports domain invariants; tests and implementation handoffs reflected. |

## Contracts, Workflow, And Standard Coverage

| Source heading | Status | Runtime location | Reason |
|---|---|---|---|
| `skill-contracts.md` `## architecture-ddd` | delegated-to-other-skill | `SKILL.md` Routing | Unclear invariants route to DDD first. |
| `## architecture-implementation-patterns` | delegated-to-other-skill | `SKILL.md` Routing | Repository/UoW/outbox/CQRS/hexagonal/dependency direction pattern selection routes away unless DB design detail is needed. |
| `## architecture-db` | included | `SKILL.md`, references | ERD/schema/constraints/indexes/transactions/isolation/rollout covered. |
| `## architecture-api` | delegated-to-other-skill | `SKILL.md` Routing | API contract and idempotency header behavior route away; storage implications remain here. |
| `## implementation-django` | delegated-to-other-skill | `SKILL.md` Routing | Django model/migration code routes away after DB design. |
| `## implementation-django-ninja` / `## implementation-django-web` | delegated-to-other-skill | implementation skills | API router/web template implementation is outside DB architecture. |
| `## implementation-python` / `## implementation-cleancode` | delegated-to-other-skill | implementation/quality skills | Python typing and refactoring quality route away unless they affect DB design assumptions. |
| `## implementation-test` / `## implementation-tdd` | delegated-to-other-skill | test skills | Test design consumes DB criteria; mechanics route away. |
| `## workflow-dddjango-subagents` | delegated-to-other-skill | `SKILL.md` Routing | Composite/risky/subagent Django work routes to workflow. |
| `## 공통 필수 출력` / `### Risky Write Consistency Block` | included | `SKILL.md`, `transactions-locking.md` | Risky write consistency items included. |
| `skill-hierarchy.md` `## Skill Hierarchy` | included | `SKILL.md` Routing | DB skill sits after DDD/pattern decisions when invariants or architecture are unclear and before Django migration implementation. |
| `workflow.md` `## 1. 기본 흐름` | merged | `SKILL.md` Routing | DB follows DDD and informs implementation/test. |
| `## 2. 작업 유형별 흐름` | included | `SKILL.md` Routing | Simple work direct; composite/subagent work routes to workflow. |
| `## 3. 역할 분해` | delegated-to-other-skill | `workflow-dddjango-subagents` | DB Agent role belongs to workflow skill. |
| `## 4. Sequential Fallback` / `## 5. Handoff Contract` | delegated-to-other-skill | `workflow-dddjango-subagents` | Workflow orchestration belongs elsewhere. |
| `## 6. 통합 우선순위` / `## 7. Integration Checklist` | merged | `SKILL.md`, references | DB invariants and transaction criteria feed implementation/test handoffs. |
| `## 8. Reference Loading` | included | `SKILL.md` Reference Loading | Runtime references directly linked. |
| `## 9. 검증 방식` | included | `SKILL.md` Runtime Rules | Only actual validation may be claimed. |
| `ddd-implementation-standard.md` `## 1. 판단 순서` | included | `SKILL.md` Routing | Domain invariants precede schema design. |
| `## 4. 애그리거트와 불변식` | included | `SKILL.md`, `transactions-locking.md` | Aggregate consistency and transaction boundary reflected. |
| `## 7. Django ORM 매핑` | delegated-to-other-skill | `implementation-django` | ORM code and model implementation route away. |
| `## 8. Repository와 Transaction` | included | `transactions-locking.md`, `rollout-constraints.md` | Transaction, concurrency, and consistency block included. |
| `## 9. API 매핑` | delegated-to-other-skill | `architecture-api` | API contract routes away; idempotency storage remains DB handoff. |
| `## 11. 테스트 매핑` | delegated-to-other-skill | `implementation-test` | DB integration/concurrency test criteria are output; pytest mechanics route away. |
| `validation-plan.md` `## 1. 검증 원칙` | included | `SKILL.md`, validation report | Real validation only and over-application checks reflected. |
| `## 2. 대표 시나리오` / `### 운영 마이그레이션` | included | `rollout-constraints.md` | Expand/backfill/contract and rollout safety included. |
| `### 트랜잭션과 동시성` | included | `transactions-locking.md` | Isolation, locking, uniqueness/idempotency, and test criteria included. |
| `### Negative Case: 단순 필드 rename` / `### Negative Case: 짧은 설명` | included | `SKILL.md` Routing | Simple cases avoid full DB ceremony. |
| `## 3. 평가 항목` | merged | `SKILL.md`, references | Data/API consistency, test/verification, and pragmatism reflected. |
| `## 4. Skill Folder 검증` | included | validation commands | Generated skill folder will be checked. |

## DB Reference Heading Coverage

| Source heading | Status | Runtime location | Reason |
|---|---|---|---|
| `architecture-db/final.md` `## 목차` | omitted | n/a | Navigation only. |
| `## 1. 데이터베이스 모델링 프로세스` | included | `schema-modeling.md` | Modeling flow included. |
| `### 1.1 작업 순서` | included | `schema-modeling.md` | Business -> conceptual -> logical -> physical sequence included. |
| `### 1.2 업무 파악 원칙` | included | `schema-modeling.md` | Business/process understanding before modeling reflected. |
| `## 2. 개념적 데이터 모델링 (ERD)` | included | `schema-modeling.md` | Entity/attribute/relation, ERD decisions included. |
| `### 2.1 ERD 구성 요소` | included | `schema-modeling.md` | Attribute/entity/relation mapping included. |
| `### 2.2 ERD 작성 원칙` | included | `schema-modeling.md` | Cohesive information groups and joins reflected. |
| `### 2.3 식별자` | included | `schema-modeling.md` | Candidate/primary/surrogate key decision included. |
| `### 2.4 Cardinality` | included | `schema-modeling.md` | 1:1, 1:N, N:M included. |
| `### 2.5 Optionality` | included | `schema-modeling.md`, `constraints-indexes.md` | Nullability and relationship optionality included. |
| `## 3. 정규화` | included | `schema-modeling.md` | 1NF-BCNF and anomaly removal included. |
| `### 3.1 함수적 종속` / `### 3.2 정규형 정의` / `### 3.3 정규형 위반 예시` | merged | `schema-modeling.md` | Functional dependency and normal forms summarized. |
| `### 3.4 정규화 핵심 원칙` | included | `schema-modeling.md` | Normalize first, denormalize deliberately included. |
| `## 4. 역정규화` | included | `schema-modeling.md`, `rollout-constraints.md` | Denormalization trade-offs and performance order included. |
| `### 4.1`-`### 4.3 역정규화` | merged | `schema-modeling.md` | Techniques and consistency costs summarized. |
| `## 5. 성능 최적화 순서` | included | `rollout-constraints.md` | Slow queries, indexes, cache, denormalization order included. |
| `## 6. 인덱스 아키텍처: B+Tree` | included | `constraints-indexes.md` | B+Tree read/write trade-off included. |
| `### 6.1`-`### 6.4 B+Tree` | merged | `constraints-indexes.md` | Structure and write/read cost summarized. |
| `## 7. 인덱스 설계 베스트 프랙티스` | included | `constraints-indexes.md` | Composite, covering, partial, and general index rules included. |
| `### 7.1 복합 인덱스 컬럼 순서` | included | `constraints-indexes.md` | Leftmost prefix and equality-before-range included. |
| `### 7.2 커버링 인덱스` | included | `constraints-indexes.md` | Covering/index-only use included. |
| `### 7.3 부분 인덱스` | included | `constraints-indexes.md` | Partial and partial unique indexes included. |
| `### 7.4 인덱스 설계 일반 원칙` | included | `constraints-indexes.md` | Cardinality, read/write ratio, unused indexes, benchmark included. |
| `## 8. 트랜잭션과 격리 수준` | included | `transactions-locking.md` | ACID, anomalies, isolation and selection guidance included. |
| `### 8.1 ACID` / `### 8.2 이상 현상` / `### 8.3 격리 수준` | included | `transactions-locking.md` | Transaction fundamentals included. |
| `### 8.4 실전 선택 가이드` | included | `transactions-locking.md` | Lowest safe isolation and retry caveat included. |
| `## 9. 쿼리 최적화` | included | `rollout-constraints.md` | EXPLAIN, scan types, joins, N+1, general rules included. |
| `### 9.1 EXPLAIN ANALYZE 읽기` | included | `rollout-constraints.md` | Actual vs estimated rows, time, buffers included. |
| `### 9.2 스캔 유형` | included | `rollout-constraints.md` | Seq/index/bitmap/index-only scan included. |
| `### 9.3 조인 유형` | included | `rollout-constraints.md` | Nested loop, hash join, merge join, and JOIN/subquery plan verification included. |
| `### 9.4 N+1 문제` | included | `rollout-constraints.md` | N+1 lazy-loading warning included. |
| `### 9.5 쿼리 최적화 일반 원칙` | included | `rollout-constraints.md` | SELECT columns, DB filtering, LIMIT included. |
| `## 10. 데이터 모델링 패턴: 계층 구조` | included | `schema-modeling.md` | Hierarchy pattern options included. |
| `### 10.1`-`### 10.4 계층 구조` | included | `schema-modeling.md` | Adjacency, closure, nested set, materialized path selection included. |
| `## 11. 데이터 모델링 패턴: 상속과 다형성` | included | `schema-modeling.md` | STI/CTI/TPC/polymorphic association trade-offs included. |
| `### 11.1`-`### 11.5 상속과 다형성` | included | `schema-modeling.md` | Pattern comparison and selection included. |
| `## 12. 참고 문헌` | omitted | n/a | Bibliography is source provenance, not runtime behavior. |

## Review Notes

- Source self-review: local review found 1 minor crosswalk completeness issue: some `skill-contracts.md` implementation headings and `skill-hierarchy.md` were not explicitly classified; fixed. Independent review later found 0 blocking, 5 major, and 1 minor; fixes applied for composite/risky workflow routing, implementation-patterns boundary, Django `transaction.on_commit()` side-effect wording, join optimization coverage, review-note status, and Korean rollout triggers.
- Skill-creator/writing-skills review: no extraneous files, direct reference links, concise `SKILL.md`, one-level references, and frontmatter length under 1024; remaining blocking/major/minor findings 0 by local review.
- Independent subagent review: Cicero re-review returned blocking 0, major 0, minor 0; no remaining source-backed findings.
- Rubric review: found 2 source-backed runtime issues after draft (`Risky Write Consistency Block` naming and idempotency storage detail); both fixed. Eval-only/private rubric material was not copied. Final remaining blocking/major/minor findings 0.
