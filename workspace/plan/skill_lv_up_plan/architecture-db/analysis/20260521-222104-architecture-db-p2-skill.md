수정 대상: skill
원인 분류: metadata trigger alignment
작업 ID: 20260521-222104-architecture-db-p2-skill

## 평가 범위

- source reference: `workspace/reference/architecture-db/reference/final.md`
- skill body: `dddjango/skills/architecture-db/SKILL.md`
- bundled references: `dddjango/skills/architecture-db/references/*.md`
- metadata: `dddjango/skills/architecture-db/agents/openai.yaml`
- metadata 기준: `/Users/hyun/.codex/skills/.system/skill-creator/references/openai_yaml.md`
- runtime cache: `/Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/architecture-db/`

## P2 평가

`SKILL.md` 목적은 관계형 DB architecture, schema modeling, constraints, indexes, transactions/locking, idempotency storage, query performance, rollout/backfill/migration safety로 명확하다. Source final도 같은 축을 판단할 수 있고 bundled references는 세부 guidance를 과도하게 중복하지 않는다.

남은 P2 gap은 frontmatter와 UI metadata의 semantic completeness다.

| 기준 | 현재 상태 | 판단 |
|---|---|---|
| 실제 사용자 표현/사용 예시 | frontmatter가 DB 설계, 스키마, 락, 멱등성, 백필 등 주요 한국어/영어 표현을 포함한다. | 충족 |
| frontmatter 사용 조건/trigger/제외 조건 | 사용 조건과 일부 제외 조건은 있으나, body의 `subagents/역할 분해`, `pytest concurrency tests`, `Django models.py/RunPython/sqlmigrate` routing과 source final의 NoSQL/connection pooling 제외가 frontmatter에는 충분히 드러나지 않는다. | Minor |
| 본문에만 숨은 trigger 규칙 | body line 13, 18, 19의 routing이 description보다 구체적이다. | Minor |
| `agents/openai.yaml` alignment | display/short/default_prompt는 대체로 맞지만 default prompt가 idempotency storage, query performance, migration safety를 빠뜨려 skill 범위보다 좁다. | Minor |
| openai_yaml 기준 | 필수 string quote와 `$architecture-db` mention은 충족한다. optional interface field는 추가되지 않았다. | 충족 |
| source/runtime parity | 수정 전 `diff -qr` 출력 없음. source 수정 후 runtime-sync가 필요하다. | 후속 필요 |
| bundled reference parity | `transactions-locking.md`의 risky write idempotency storage 항목이 source final의 request fingerprint, response snapshot/stable result reference, retention/cleanup 결정을 충분히 싣지 않는다. | Major |
| partitioning source gap | source review가 partitioning strategy를 gap으로 기록하고, final은 상세 기준을 제공하지 않는데 runtime이 physical partitioning choice를 언급한다. | Major |

## 수정 판단

P2는 source reference를 새로 보강할 문제가 아니다. `SKILL.md` body와 source final의 routing boundary를 frontmatter description에 올리고, `agents/openai.yaml` default prompt를 skill 범위와 맞춘다. Source final에 이미 있는 idempotency storage 결정이 bundled reference에서 누락되지 않도록 `transactions-locking.md`를 좁게 보강한다. 반대로 partitioning strategy는 source final이 충분하지 않으므로 runtime claim을 축소하고 `reference_lv_up_plan`에 follow-up analysis를 남긴다.

## 리뷰 방식

리뷰 방식: real-subagent

Subagent 리뷰/순차 fallback: P2 점검용 real subagent 2개를 read-only로 실행했다. 첫 번째 subagent는 `transactions-locking.md` idempotency storage parity gap을 Major로, NoSQL/connection pooling과 role-decomposed trigger frontmatter 누락을 Minor로 제기했다. 두 번째 subagent는 partitioning source gap을 Major로, `openai.yaml` scope narrowness와 body-only negative trigger vocabulary를 Minor로 제기했다.

리뷰 결과: Blocker 0, Major 0, 열린 Minor 0

skill-creator 리뷰: 순차 fallback 기준으로는 frontmatter/body trigger alignment와 default prompt 범위 보강이 필요했다. Real subagent의 bundled reference parity 지적은 source final과 대조해 타당하다고 판단했다. Partitioning은 source gap으로 분류하고 runtime overclaim을 줄였다. 최종 read-only subagent 재평가(agent `019e4aba-332a-7372-b751-b4bdb1a87078`)에서 hidden body-only trigger, `openai.yaml` scope, idempotency storage parity, partitioning overclaim, source/runtime parity가 모두 닫혔다고 확인했다.

## 수정 대상

- `dddjango/skills/architecture-db/SKILL.md`
- `dddjango/skills/architecture-db/agents/openai.yaml`
- `dddjango/skills/architecture-db/references/transactions-locking.md`
- `dddjango/skills/architecture-db/references/schema-modeling.md`

수정하지 말아야 할 범위:

- `workspace/reference/architecture-db/reference/final.md`는 P2에서 새 source gap이 확인되지 않았으므로 수정하지 않는다.
- bundled references 상세 내용을 frontmatter에 장황하게 복사하지 않는다.
- optional interface fields(`icon_small`, `icon_large`, `brand_color`, dependencies, policy)는 명시 요청이 없으므로 추가하지 않는다.

## 재평가

`SKILL.md` frontmatter는 body의 role-decomposed workflow, Django implementation, pytest/concurrency test routing을 노출하고 NoSQL, detailed partitioning without source/project criteria, ORM code, tool-specific migrations, connection pooling, simple field rename/local CRUD 제외 조건을 포함한다. `agents/openai.yaml`은 optional interface field 없이 `display_name`, `short_description`, `default_prompt`만 포함하며 default prompt가 idempotency storage, duplicate prevention, EXPLAIN ANALYZE, rollout/migration safety를 포함한다. `transactions-locking.md`는 idempotency storage key scope, owner/location, unique constraint, request fingerprint, stored result/replay reference, retention/cleanup rule을 포함한다. Partitioning은 runtime guidance에서 상세 claim을 제거하고 reference follow-up으로 분류했다.

최종 리뷰 결과는 Blocker 0, Major 0, 열린 Minor 0이다.
