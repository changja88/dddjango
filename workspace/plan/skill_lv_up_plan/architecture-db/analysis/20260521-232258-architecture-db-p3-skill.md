수정 대상: skill
원인 분류: responsibility-boundary
작업 ID: 20260521-232258-architecture-db-p3-skill
리뷰 결과: Blocker 0, Major 0, 열린 Minor 0

## 평가 범위

- source reference: `workspace/reference/architecture-db/reference/final.md`
- skill body: `dddjango/skills/architecture-db/SKILL.md`
- metadata: `dddjango/skills/architecture-db/agents/openai.yaml`
- bundled references: `dddjango/skills/architecture-db/references/*.md`
- adjacent skills: `architecture-ddd`, `architecture-implementation-patterns`, `architecture-api`, `implementation-django`, `implementation-test`, `source-reference-audit`, `workflow-dddjango-subagents`
- runtime cache: `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/architecture-db/`

## P3 평가

`architecture-db`의 기본 책임은 관계형 DB 설계, 제약조건, 인덱스, 트랜잭션/락/격리, 멱등성 저장소, 쿼리 성능, staged rollout/backfill 위험으로 명확하다. `SKILL.md`는 40줄로 500줄 미만이고, bundled reference 4개는 모두 `SKILL.md`에서 1단계 직접 링크로 발견 가능하다. 세부 규칙은 `references/*.md`로 분리되어 있어 progressive disclosure 구조는 대체로 적절하다.

P3에서 남은 gap은 risky-write handoff 경계다.

| 기준 | 현재 상태 | 판단 |
|---|---|---|
| 직접 책임 | schema, constraints, indexes, locking, isolation, idempotency storage, rollout risk는 명확하다. | 충족 |
| handoff 기준 | DDD, API, Django 구현, pytest 구현, workflow routing은 `SKILL.md`에 있다. | 충족 |
| architecture role 충돌 | `architecture-implementation-patterns`가 transaction owner, side-effect timing, outbox/saga/ACL pattern decision을 소유하는데 `architecture-db`도 risky write block에서 같은 항목을 직접 기록하라고 한다. DB 관점 기록인지 pattern 결정인지 구분이 약하다. | Major |
| implementation/test 침범 | migration file 구현과 pytest mechanics는 handoff가 명확하다. 다만 risky-write 문구가 integration/concurrency test criteria를 DB skill이 직접 결정하는 것처럼 읽힐 수 있다. | Minor |
| source audit/workflow 침범 | runtime/source provenance나 role-map 변경은 하지 않는다. Workflow는 multi-role 요청에서 선행하도록 routing되어 있다. | 충족 |
| progressive disclosure | `SKILL.md`가 핵심 절차와 routing만 담고, 세부 규칙은 직접 링크된 bundled references에 있다. | 충족 |
| 중복/불일치 | source final의 side-effect 원칙은 DB 트랜잭션 내부 외부 호출 금지와 post-commit handoff를 말한다. bundled `transactions-locking.md`가 `outbox`를 DB skill에서 선택하는 듯 읽힐 여지가 있다. | Minor |
| reference depth | 깊은 reference 연결이나 숨겨진 자료는 없다. | 충족 |

## 수정 판단

Source reference 자체의 P3 경계 기준은 충분하다. `final.md`는 DB architecture가 migration file 구현이 아니며, 외부 side effect는 DB transaction 안에서 실행하지 말고 commit 이후 handoff를 사용한다고 설명한다. 문제는 runtime wording이 adjacent skill의 pattern decision과 test mechanics를 같은 책임처럼 보이게 하는 점이다.

따라서 source reference는 수정하지 않는다. `SKILL.md`와 `transactions-locking.md`를 좁게 고쳐 DB-owned 결정과 handoff-only 결정을 분리한다. `agents/openai.yaml`은 concrete migration file handoff가 UI prompt에서도 보이도록 한 문장만 보강한다.

## 수정 대상

- `dddjango/skills/architecture-db/SKILL.md`
- `dddjango/skills/architecture-db/agents/openai.yaml`
- `dddjango/skills/architecture-db/references/transactions-locking.md`

수정하지 말아야 할 범위:

- `workspace/reference/architecture-db/reference/final.md`
- adjacent skill files
- eval materials
- `agents/openai.yaml` optional metadata와 새 optional interface field
- unrelated bundled references

## 리뷰 방식

리뷰 방식: real-subagent

Subagent 리뷰/순차 fallback: P3 점검용 real subagent 2개를 read-only로 실행했다. 첫 번째 리뷰는 수정 직후 중간 상태의 runtime cache drift와 열린 분석/계획 문서를 Blocker/Major로 지적했고, 이는 runtime sync와 문서 closure로 해결했다. 두 번째 리뷰는 risky-write ownership 경계를 Major로, `architecture-db` metadata의 migration-file negative boundary 부족을 Minor로 지적했고, 이는 `SKILL.md`, `transactions-locking.md`, `agents/openai.yaml` 수정으로 해결했다. 두 번째 리뷰의 workflow role-map 및 `implementation-django` risky-write wording 지적은 adjacent skill P3 범위의 후속 검토 대상이며, 이번 architecture-db source는 owning skill handoff를 명시해 더 이상 같은 결정을 직접 소유하지 않는다.

리뷰 결과: Blocker 0, Major 0, 열린 Minor 0

skill-creator 리뷰: `/Users/hyun/.codex/skills/.system/skill-creator/SKILL.md` 기준으로 `SKILL.md` concision, direct references, duplication, validation integrity를 확인했다. `SKILL.md`는 40줄로 500줄 미만이고, bundled reference 4개는 모두 1단계 직접 링크다. 세부 risky-write guidance는 `transactions-locking.md`에 있고 `SKILL.md`에는 routing과 핵심 판단만 남겼다.

## 재평가

수정 후 같은 기준으로 재평가했다.

- risky-write block에서 DB-owned 항목과 adjacent skill handoff 항목이 분리됐다.
- `architecture-implementation-patterns`의 outbox/saga/ACL pattern decision은 handoff로 명시되어 `architecture-db`가 직접 선택하지 않는다.
- `architecture-api`의 `Idempotency-Key` contract, `implementation-django`의 concrete migration/transaction code, `implementation-test`의 pytest mechanics를 handoff로 명시했다.
- `agents/openai.yaml` default prompt는 rollout/backfill safety와 concrete Django migration file handoff를 함께 드러낸다.
- bundled references는 여전히 `SKILL.md`에서 1단계 직접 링크로 발견 가능하다.
- source skill과 runtime cache는 `diff -qr dddjango/skills/architecture-db /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/architecture-db` 기준 출력 없음으로 동기화됐다.
