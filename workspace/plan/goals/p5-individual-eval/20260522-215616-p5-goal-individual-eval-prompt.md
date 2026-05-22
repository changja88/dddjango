# P5 Goal Prompt - Individual Eval

```text
너는 dddjango Codex 플러그인 재구축 계획의 P5 Individual Skill Eval을 수행한다.

목표:
각 skill의 목적을 대표하는 최소 평가 세트를 만들고, affected bucket이 clean/scored인지 확인한다.

선행 조건:
- P4.5 runtime parity가 complete다.

대상:
- P1.5 usage cards
- P4 eval protocol and runner
- dddjango/skills/**
- workspace/develop/eval/**
- workspace/plan/phases/p5-individual-eval/

허용 수정 범위:
- workspace/develop/eval/**
- workspace/scripts/** eval validator/runner/report 관련 narrow fix
- dddjango/skills/** 또는 workspace/reference/**는 gap 분류 후 필요한 경우만
- workspace/plan/phases/p5-individual-eval/{analysis,plan,evidence,closure}/
- workspace/plan/indexes/
- workspace/plan/status/phase_status.md

금지:
- 개별 skill 평가를 integration 평가 근거로 주장하지 않는다.
- baseline verdict 고정, expected_delta completion gate, pass-or-pass-limited를 완료 게이트로 쓰지 않는다.
- flaky case가 2회 이상 나오면 case를 늘리지 말고 원인을 분류한다.
- targeted pass만으로 완료하지 않는다. affected bucket clean/scored가 필요하다.

해야 할 일:
1. trigger family 기준으로 positive/negative surface를 정한다.
2. 기본은 trigger family당 positive 1개, negative 1개로 제한한다.
3. answer는 reference criterion coverage, required observations, forbidden overclaim 중심으로 작성한다.
4. 신규/수정 case는 targeted run을 기본 2회 실행한다.
5. affected bucket all-cases run을 실행하고 not scored 0, missing/malformed oracle 0을 확인한다.
6. current-file digest와 run metadata digest 일치를 확인한다.
7. shared eval infrastructure를 수정했다면 모든 bucket을 affected로 보고 clean 여부를 확인한다.
8. analysis/plan/evidence/closure와 indexes를 갱신한다.

필수 검증:
- python3 -B workspace/scripts/validate_plan_governance.py
- 관련 eval unit tests
- 신규/수정 case targeted run 기본 2회
- affected bucket all-cases run
- validate-run
- report regenerate 후 raw artifact 대조

완료 조건:
- 모든 신규/수정 case가 targeted pass다.
- model-backed 신규/수정 case는 기본 2회 모두 pass다.
- 1회만 실행한 case는 single-pass provisional이며 P5 완료 근거로 쓰지 않는다.
- affected bucket all-cases run이 pass다.
- affected bucket not scored == 0이다.
- missing/malformed oracle JSON이 0이다.
- current-file digest와 run metadata digest가 일치한다.

권한/승인:
- model runner, app-server, unsandboxed eval이 필요하면 데이터 전송 위험과 명령을 적고 사용자 승인 요청 후 진행한다.
- 승인 후에도 policy가 막히면 complete 금지. infrastructure-blocked로 기록한다.

최종 응답:
- individual eval matrix
- run id/status와 validate-run 결과
- affected bucket clean/scored 결과
- 수정 파일과 analysis/plan/evidence 경로
- 검증 명령과 결과
- P5 완료/미완료 판단
- Serena 사용 여부 또는 생략 이유
```
