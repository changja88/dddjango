수정 대상: skill

# workflow-dddjango-subagents P5 public wording 계획

## 수정 범위

- `dddjango/skills/workflow-dddjango-subagents/SKILL.md`
- `dddjango/skills/workflow-dddjango-subagents/references/integration-checklist.md`
- runtime cache sync가 필요하면 같은 두 파일을 plugin cache에 동기화한다.

## 절차

1. 내부 eval 용어를 public-facing validation evidence/review coverage/completion proof/run evidence wording으로 대체한다.
2. source-reference-audit handoff와 owning follow-up 원칙은 유지한다.
3. skill docs validator와 workflow bucket validator를 재실행한다.
4. runtime cache를 동기화한 경우 source/cache diff를 확인한다.

## 완료 조건

- runtime-facing workflow guidance가 내부 eval schema/scoring/report wording을 직접 노출하지 않는다.
- workflow skill과 source-reference-audit 책임 경계가 유지된다.
- 관련 validator가 통과한다.
