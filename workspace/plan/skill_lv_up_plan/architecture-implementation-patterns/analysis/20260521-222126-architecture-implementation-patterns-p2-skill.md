수정 대상: skill
원인 분류: frontmatter-trigger-gap

# architecture-implementation-patterns P2 skill 분석

## 평가 요약

`SKILL.md` 본문과 dedicated source reference는 risky write consistency handoff를 이 skill의 주요 사용 표면으로 다룬다. 그러나 frontmatter `description`은 pattern 이름과 일반적인 consistency 필요만 언급하고, 결제/재고/예약/환불/권한/ledger 같은 risky write 표현, transaction owner, side-effect timing, idempotency storage handoff를 직접 드러내지 않는다.

Codex는 frontmatter `description`을 skill trigger 판단에 먼저 사용하므로, 본문에만 있는 risky write trigger는 P2 기준의 "본문에만 숨은 trigger 규칙"에 해당한다. 또한 본문 routing은 subagent, 역할 분해, 병렬 검토, dddjango workflow 요청을 `workflow-dddjango-subagents`로 넘기라고 구체적으로 말하지만 frontmatter는 `coordinated work`만 말해 제외 조건이 약하다.

## 근거

- `dddjango/skills/architecture-implementation-patterns/SKILL.md` 본문은 `Risky Write Consistency Block`을 출력해야 하는 상황을 runtime rule로 둔다.
- `workspace/reference/architecture-implementation-patterns/reference/final.md`는 결제, 재고, 예약, 환불, 권한, ledger 같은 위험 write에서 pattern-level 판단을 명시하라고 한다.
- `agents/openai.yaml`의 `default_prompt`는 risky-write transaction/side-effect/idempotency handoff를 이미 포함한다.
- `SKILL.md` frontmatter는 `boundary, consistency, replaceability need`를 말하지만 risky-write 사용자 표현과 구체 handoff trigger를 직접 포함하지 않는다.

## 리뷰 방식

리뷰 방식: real-subagent

Subagent 리뷰/순차 fallback: 두 real-subagent 리뷰를 수행했다. 독립 리뷰는 Blocker 0, Major 0, 열린 Minor 0으로 판정했지만, skill-creator 관점 리뷰는 frontmatter risky-write trigger 누락을 Major 1, workflow/subagent 제외 조건 약화를 Minor 1로 판정했다.

skill-creator 리뷰: frontmatter가 trigger surface라는 기준에 따라 본문에만 있는 risky-write entrypoint를 description에 올려야 한다는 판정을 채택한다. `agents/openai.yaml`은 OpenAI YAML 기준을 충족하고 optional interface field를 추가하지 않았으므로 수정하지 않는다.

리뷰 결과: Blocker 0, Major 1, 열린 Minor 1

## 완료 판정

`SKILL.md` frontmatter description에 risky-write trigger와 workflow/subagent 제외 조건을 추가한 뒤 재평가해야 한다.
