# P3 Goal Prompt - Forward Tests

```text
너는 dddjango Codex 플러그인 재구축 계획의 P3 Forward Tests를 수행한다.

목표:
평가 시스템을 만들기 전에 실제 사용자 요청에 대해 각 skill이 의도대로 로드되고, 엉뚱한 trigger/overclaim이 없는지 최소 사용 시나리오로 검증한다.

P3 split:
- P3a static/user-prompt matrix: usage card 기반 prompt set과 expected routing/non-goal을 고정한다.
- P3b runtime forward-test: approved external Codex/OpenAI runtime 또는 실행 가능한 local/offline provider에서 actual skill loaded, final answer, routing, overclaim, leakage를 관찰한다.
- P3a만으로 P3 전체 complete 금지. P3b가 infrastructure-blocked이면 ADR을 남기고 P4 진입 여부를 별도 결정한다.

선행 조건:
- P2 skill structure가 complete다.

대상:
- P1.5 usage cards
- dddjango/skills/**
- workspace/plan/phases/p3-forward-tests/{prompts,evidence,closure}/

허용 수정 범위:
- workspace/plan/phases/p3-forward-tests/{prompts,evidence,closure}/
- workspace/plan/phases/p3-forward-tests 관련 analysis/plan이 필요하면 기존 phase 구조에 맞춰 작성
- narrow fix가 꼭 필요할 때만 dddjango/skills/**
- workspace/plan/indexes/
- workspace/plan/status/phase_status.md

금지:
- 평가 runner, oracle, HTML report를 만들지 않는다.
- forward-test prompt에 기대 답, 의도한 수정, 이전 결론, suspected bug를 넘기지 않는다.
- 실패 원인 분류 없이 skill/reference를 수정하지 않는다.
- P3 결과를 P5/P6 eval pass로 주장하지 않는다.

해야 할 일:
1. usage card에서 high-risk happy/exclusion prompt를 뽑아 P3 prompt 파일로 고정한다.
2. fresh isolated context 또는 사용자-like forward-test를 실행한다.
3. raw output, loaded skill/routing observation, final answer, overclaim 여부를 evidence에 저장한다.
4. 실패가 있으면 수정 대상 none/reference/skill/trigger/runtime-sync 중 하나로 분류한다.
5. skill 수정이 필요하면 analysis/plan을 먼저 작성하고 좁게 수정한 뒤 동일 forward-test를 재실행한다.
6. runtime forward-test가 infrastructure-blocked이면 P3b blocked evidence를 기록하고, P3 전체를 complete로 표시하지 않는다.
7. P4 진입을 허용하려면 accepted ADR이 있어야 하며, P7/P8 전 P3b 또는 동등한 installed-runtime evidence가 필요하다고 기록한다.
8. indexes와 phase_status.md를 갱신한다.

필수 검증:
- python3 -B workspace/scripts/validate_plan_governance.py
- P2 validator가 있다면 관련 skill에 재실행
- forward-test raw artifact 경로와 결과가 evidence에 기록됐는지 확인

완료 조건:
- P3a: 모든 high-risk skill 또는 trigger family에 happy/exclusion prompt matrix가 있다.
- P3b: fresh isolated forward-test가 최소 1개 이상 있고 actual skill loaded/final answer/routing/overclaim/leakage가 관찰됐다.
- wrong routing, overclaim, leakage가 열린 상태로 남아 있지 않다.
- 실행 불가한 forward-test가 있으면 P3 전체 complete 금지. P3b infrastructure-blocked로 기록한다.
- validate_plan_governance.py가 통과한다.

권한/승인:
- Codex runtime, app-server, external model runner가 필요하면 사용자 승인 요청 후 진행한다.
- 승인 후에도 policy가 막으면 우회하지 말고 infrastructure-blocked로 기록한다.

최종 응답:
- forward-test matrix
- raw artifact/evidence 경로
- 수정한 skill이 있으면 analysis/plan 경로
- 검증 명령과 결과
- P3 완료/미완료 판단
- Serena 사용 여부 또는 생략 이유
```
