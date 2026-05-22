# P1 Goal Prompt - Reference Sufficiency

```text
너는 dddjango Codex 플러그인 재구축 계획의 P1 Reference Sufficiency를 수행한다.

목표:
skill을 고치기 전에 workspace/reference/*/reference/final.md가 각 skill을 만들 만큼 충분한지 검증하고, 부족한 source reference만 좁게 보강한다.

선행 조건:
- P0 inventory가 complete이며 phase_status.md에 current evidence가 있다.

대상:
- workspace/reference/*/reference/final.md
- workspace/plan/phases/p1-reference-sufficiency/
- workspace/plan/indexes/
- 필요 시 공식/primary source 문서

허용 수정 범위:
- workspace/reference/**/reference/final.md
- workspace/plan/phases/p1-reference-sufficiency/{analysis,plan,evidence,closure}/
- workspace/plan/indexes/{artifact_index.md,evidence_index.md}
- workspace/plan/status/phase_status.md

금지:
- dddjango/skills/** 수정 금지.
- eval runner/case/answer 수정 금지.
- source가 부족한데 skill을 추측으로 고치지 않는다.
- OpenAPI를 DDD, DB transaction, Django ORM, pytest/TDD 기준으로 쓰지 않는다.

해야 할 일:
1. P0 inventory를 읽고 reference 목록과 skill-reference 관계를 확인한다.
2. 각 reference가 목적, 사용 조건, 제외 조건, 핵심 판단 기준, source provenance를 포함하는지 평가한다.
3. 각 reference를 sufficient / needs-source / provisional로 분류한다.
4. needs-source가 있으면 analysis와 plan을 작성한 뒤 reference만 수정한다.
5. source 우선순위를 기록한다: 공식 문서/표준, primary project docs, 신뢰 가능한 engineering article, unsupported blog/기억 기반.
6. OpenAI/Codex 관련 source는 공식 OpenAI 문서만 사용하고, 필요 시 OpenAI docs MCP 또는 공식 docs를 확인한다.
7. 모든 수정에 대해 evidence 파일을 작성하고 indexes를 갱신한다.

필수 검증:
- python3 -B workspace/scripts/validate_plan_governance.py
- reference 변경이 있으면 git diff로 skill/eval 수정이 섞이지 않았는지 확인한다.

완료 조건:
- 모든 reference가 sufficient / provisional 중 하나이며 needs-source가 0이다.
- provisional 항목은 P5/P6/P8 완료 근거로 쓰지 말라는 제한이 evidence에 기록되어 있다.
- reference 수정마다 analysis/plan/evidence가 있다.
- artifact_index.md와 evidence_index.md가 현재 산출물을 가리킨다.
- validate_plan_governance.py가 통과한다.

권한/승인:
- 공식 문서 확인에 network가 필요하면 사용자 승인 요청 후 진행한다.
- network 또는 policy 차단으로 source 확인이 불가하면 complete 금지. phase_status.md에 infrastructure-blocked 또는 blocked와 사유를 기록한다.

최종 응답:
- reference 분류표
- 수정한 reference와 사유
- 남은 provisional 요약
- evidence/index 경로
- 검증 명령과 결과
- P1 완료/미완료 판단
- Serena 사용 여부 또는 생략 이유
```
