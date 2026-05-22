# P4 Goal Prompt - Eval Skeleton

```text
너는 dddjango Codex 플러그인 재구축 계획의 P4 Eval Skeleton을 수행한다.

목표:
case를 늘리기 전에 runner, oracle schema, scoring, validator, report가 mini-bucket fixture에서 신뢰 가능하게 pass/fail/not-scored/leakage를 구분하는지 검증한다.

선행 조건:
- P3 forward tests가 complete다.

대상:
- workspace/plan/governance/eval_protocol.md
- workspace/plan/phases/p4-eval-skeleton/{analysis,plan,fixtures,evidence,closure}/
- workspace/develop/eval/** 또는 새 eval skeleton 위치
- workspace/scripts/** eval 관련 파일

허용 수정 범위:
- workspace/plan/governance/eval_protocol.md
- workspace/plan/phases/p4-eval-skeleton/**
- workspace/develop/eval/**
- workspace/scripts/** eval skeleton/validator/report 관련 파일
- workspace/plan/indexes/
- workspace/plan/status/phase_status.md

금지:
- P4 전에는 실제 skill별 case를 대량 추가하지 않는다.
- not scored를 성공으로 취급하지 않는다.
- HTML report만으로 완료하지 않는다.
- sanitizer가 누출을 지웠다는 이유로 raw leakage를 pass로 만들지 않는다.

해야 할 일:
1. eval_protocol.md에 case schema, answer schema, oracle output schema, scoring semantics, artifact names, failure semantics, report invariants, command contract를 정의한다.
2. mini-bucket fixture를 만든다: pass, partial, fail, missing-oracle, malformed-oracle, stale-report, local-path leak, sanitizer-only leak, private-field leak, expected_outcomes conflict, Korean negation false-positive, prompt-only command claim.
3. fixture-only runner/validator/report를 먼저 통과시킨다.
4. raw artifact, validator result, report 표시가 일치하는지 검증한다.
5. run-one, run-bucket, render-report, validate-run command contract를 확정한다.
6. analysis/plan/evidence와 indexes를 갱신한다.

필수 검증:
- python3 -B workspace/scripts/validate_plan_governance.py
- P4에서 만든 eval skeleton unit tests
- mini-bucket fixture full run
- validate-run 결과
- report regenerate 후 raw artifact 대조

완료 조건:
- mini-bucket full run이 기대대로 pass/fail을 구분한다.
- 모든 fixture의 결과가 raw artifact, validator, report에서 일치한다.
- not scored가 있으면 run 실패로 처리된다.
- missing/malformed oracle은 실패한다.
- stale report와 raw leakage는 실패한다.
- command claim은 structured event command/tool evidence만 인정한다.

권한/승인:
- model-backed run은 P4 완료에 필요하지 않다. 필요하다고 판단하면 먼저 사용자 승인을 요청한다.
- 필수 fixture 검증이 권한 문제로 막히면 complete 금지.

최종 응답:
- eval_protocol 경로
- fixture matrix와 결과
- 수정한 runner/validator/report 파일
- 검증 명령과 결과
- P4 완료/미완료 판단
- Serena 사용 여부 또는 생략 이유
```
