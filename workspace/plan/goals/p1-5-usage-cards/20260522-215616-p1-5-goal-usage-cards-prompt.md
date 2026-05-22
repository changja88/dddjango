# P1.5 Goal Prompt - Usage Cards

```text
너는 dddjango Codex 플러그인 재구축 계획의 P1.5 Usage Cards를 수행한다.

목표:
SKILL.md description과 trigger를 고치기 전에, 실제 사용자가 어떤 말로 각 skill을 호출하거나 제외할지 usage card로 고정한다.

선행 조건:
- P1 reference sufficiency가 complete이며 needs-source가 0이다.

대상:
- P0 inventory evidence
- P1 reference sufficiency evidence
- workspace/plan/phases/p1-5-usage-cards/cards/
- workspace/plan/indexes/

허용 수정 범위:
- workspace/plan/phases/p1-5-usage-cards/{cards,evidence,closure}/
- workspace/plan/indexes/{artifact_index.md,evidence_index.md}
- workspace/plan/status/phase_status.md

금지:
- dddjango/skills/** 수정 금지.
- workspace/reference/** 수정 금지.
- usage card 없이 SKILL.md description 또는 trigger handoff를 수정하지 않는다.
- 내부 taxonomy 용어만으로 prompt를 만들지 않는다. 실제 사용자 언어를 우선한다.

해야 할 일:
1. P0/P1 산출물을 읽고 high-risk trigger family를 정한다.
2. 각 trigger family마다 positive user prompt 2-3개를 작성한다.
3. 각 trigger family마다 exclusion prompt 1개 이상을 작성한다.
4. 각 card에 expected skill, expected bundled resource load, expected artifact behavior, common non-goal을 기록한다.
5. skill 간 handoff가 필요한 경우 expected handoff 문구를 기록한다.
6. usage card가 P2 description, P3 forward-test, P5 eval case의 입력이라는 점을 evidence에 명시한다.
7. artifact_index.md와 evidence_index.md를 갱신한다.

필수 검증:
- python3 -B workspace/scripts/validate_plan_governance.py
- usage card가 dddjango/skills/** 또는 workspace/reference/** 변경 없이 작성됐는지 git diff로 확인한다.

완료 조건:
- 모든 high-risk trigger family에 positive/exclusion usage card가 있다.
- 각 card가 expected skill과 non-goal을 포함한다.
- artifact_index.md에 card 산출물이 기록되어 있다.
- validate_plan_governance.py가 통과한다.

권한/승인:
- P1.5는 외부 runner가 필요 없다. 필요하다고 판단하면 사용자 승인 전에는 실행하지 않는다.
- 필수 검증을 실행할 수 없으면 complete 금지.

최종 응답:
- 생성한 usage card 경로
- trigger family coverage 요약
- exclusion coverage 요약
- index 갱신 여부
- 검증 명령과 결과
- P1.5 완료/미완료 판단
- Serena 사용 여부 또는 생략 이유
```
