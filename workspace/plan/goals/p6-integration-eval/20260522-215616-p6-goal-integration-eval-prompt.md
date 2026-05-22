# P6 Goal Prompt - Integration Eval

```text
너는 dddjango Codex 플러그인 재구축 계획의 P6 Integration Eval을 수행한다.

목표:
여러 skill이 함께 쓰이는 대표 흐름에서 책임 경계, handoff, workflow honesty, source/runtime governance가 평가로 보장되는지 확인한다.

선행 조건:
- P5 individual eval이 complete다.

대상:
- P5 clean/scored eval system
- dddjango/skills/**
- workspace/develop/eval/**
- workspace/plan/phases/p6-integration-eval/

허용 수정 범위:
- workspace/develop/eval/**
- workspace/scripts/** eval validator/runner/report 관련 narrow fix
- dddjango/skills/** 또는 workspace/reference/**는 integration gap 분류 후 필요한 경우만
- workspace/plan/phases/p6-integration-eval/{analysis,plan,evidence,closure}/
- workspace/plan/indexes/
- workspace/plan/status/phase_status.md

금지:
- P5 individual case를 P6 integration 완료 근거로 재사용하지 않는다.
- workflow/subagent trace는 실제 artifact가 있을 때만 pass한다.
- targeted pass만으로 완료하지 않는다. affected bucket clean/scored가 필요하다.
- skill 책임 침범, false claim, source leakage가 남아 있으면 complete 금지.

해야 할 일:
1. DDD + DB + API + Django + Test 대표 흐름 1개를 만든다.
2. tiny edit / opt-out restraint 대표 흐름 1개를 만든다.
3. source/runtime governance 대표 흐름 1개를 만든다.
4. subagent/workflow honesty 대표 흐름 1개를 만든다.
5. 신규/수정 integration case는 targeted run을 기본 2회 실행한다.
6. affected bucket all-cases run을 실행하고 not scored 0, missing/malformed oracle 0을 확인한다.
7. current-file fingerprint와 run evidence 일치를 확인한다.
8. analysis/plan/evidence/closure와 indexes를 갱신한다.

필수 검증:
- python3 -B workspace/scripts/validate_plan_governance.py
- 관련 eval unit tests
- 신규/수정 integration case targeted run 기본 2회
- affected bucket all-cases run
- validate-run
- report regenerate 후 raw artifact 대조

완료 조건:
- 모든 신규/수정 integration case가 targeted pass다.
- model-backed 신규/수정 integration case는 기본 2회 모두 pass다.
- 1회만 실행한 case는 single-pass provisional이며 P6 완료 근거로 쓰지 않는다.
- affected bucket all-cases run이 pass다.
- affected bucket not scored == 0이다.
- missing/malformed oracle JSON이 0이다.
- skill 책임 침범, false claim, source leakage가 0이다.

권한/승인:
- model runner, app-server, unsandboxed eval이 필요하면 데이터 전송 위험과 명령을 적고 사용자 승인 요청 후 진행한다.
- 승인 후에도 policy가 막히면 complete 금지. infrastructure-blocked로 기록한다.

최종 응답:
- integration eval matrix
- run id/status와 validate-run 결과
- affected bucket clean/scored 결과
- 책임 경계/handoff 검증 요약
- 수정 파일과 analysis/plan/evidence 경로
- 검증 명령과 결과
- P6 완료/미완료 판단
- Serena 사용 여부 또는 생략 이유
```
