수정 이유: `SKILL.md` body의 일부 routing/exclusion이 frontmatter description보다 구체적이고, `agents/openai.yaml` default prompt가 architecture-db의 전체 범위를 조금 좁게 표현한다. Bundled `transactions-locking.md`는 source final의 idempotency storage 결정 중 request fingerprint, replay result, retention/cleanup 항목을 빠뜨린다. 또한 source final은 partitioning strategy 기준을 제공하지 않는데 runtime skill이 physical partitioning choice를 언급한다.

작업 ID: 20260521-222104-architecture-db-p2-skill

## 수정 범위

- `dddjango/skills/architecture-db/SKILL.md` frontmatter `description`만 보강한다.
- `dddjango/skills/architecture-db/agents/openai.yaml`의 `short_description`과 `default_prompt`만 보강한다.
- `dddjango/skills/architecture-db/references/transactions-locking.md`의 risky-write idempotency storage 항목만 source final과 맞춘다.
- `dddjango/skills/architecture-db/references/schema-modeling.md`와 `SKILL.md` runtime rule에서 partitioning overclaim을 제거한다.

## 수정하지 말아야 할 범위

- source reference는 P2에서 직접 수정하지 않고, 새 source gap은 reference follow-up analysis로 분류한다.
- `SKILL.md` body의 runtime guidance는 현재 source final과 맞으므로 불필요하게 재작성하지 않는다.
- 명시 요청 없는 optional interface field는 추가하지 않는다.
- runtime cache는 source 수정 후 별도 runtime-sync 분석/계획으로 처리한다.

## 작업 체크리스트

- [x] frontmatter description에 subagent/role-decomposed workflow routing 제외 조건을 명시한다.
- [x] frontmatter description에 Django model/migration implementation과 pytest/concurrency test implementation routing 제외 조건을 명시한다.
- [x] frontmatter description에 source final의 NoSQL/connection pooling 제외 조건을 명시한다.
- [x] `agents/openai.yaml` default prompt가 idempotency storage, duplicate prevention, query performance, rollout/migration safety까지 드러내도록 보강한다.
- [x] `transactions-locking.md` risky-write idempotency storage 항목에 request fingerprint, stored result/replay reference, retention/cleanup 결정을 포함한다.
- [x] partitioning strategy는 runtime claim에서 제거하고 reference follow-up analysis로 분류한다.
- [x] optional interface field가 추가되지 않았는지 확인한다.
- [x] source 수정 후 runtime cache drift를 별도 runtime-sync로 닫는다.

## 검증 명령

- `.venv/bin/python -B workspace/scripts/validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/test_validate_plan_constraints.py`
- `.venv/bin/python -B workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`
- `diff -qr dddjango/skills/architecture-db /Users/hyun/.codex/plugins/cache/dddjango-local/dddjango/0.1.10/skills/architecture-db`

## 완료 조건

- `SKILL.md` frontmatter와 body routing이 충돌하지 않는다.
- 본문에만 숨은 P2 trigger/exclusion 규칙이 남지 않는다.
- `agents/openai.yaml`은 `display_name`, `short_description`, `default_prompt`만 포함하고 `SKILL.md` 범위와 일치한다.
- source/runtime cache parity가 다시 확인된다.
- 리뷰 결과가 Blocker 0, Major 0, 열린 Minor 0으로 닫힌다.

## 완료 판정

완료. Runtime sync plan을 별도로 작성 및 실행했고, 최종 read-only subagent 재평가와 validator 결과 기준으로 P2 skill 수정의 Blocker, Major, 열린 Minor는 0이다.
