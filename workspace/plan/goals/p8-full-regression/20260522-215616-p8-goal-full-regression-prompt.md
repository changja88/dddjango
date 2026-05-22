# P8 Goal Prompt - Full Regression

```text
너는 dddjango Codex 플러그인 재구축 계획의 P8 Full Regression을 수행한다.

목표:
최종 full run과 설치 runtime evidence만으로 dddjango Codex plugin 완료 여부를 판정한다.

선행 조건:
- P7 install packaging이 complete다.

대상:
- 전체 eval bucket
- P7 installed-runtime evidence
- workspace/develop/eval/**
- workspace/scripts/** eval runner/validator/report
- workspace/plan/phases/p8-full-regression/
- workspace/plan/reviews/

허용 수정 범위:
- workspace/develop/eval/**
- workspace/scripts/** eval validator/runner/report 관련 final narrow fix
- dddjango/skills/** 또는 workspace/reference/**는 failure 분류 후 필요한 경우만
- workspace/plan/phases/p8-full-regression/{analysis,plan,evidence,closure}/
- workspace/plan/reviews/{raw,summaries,closures}/
- workspace/plan/indexes/
- workspace/plan/status/phase_status.md

금지:
- targeted pass만으로 완료하지 않는다.
- HTML latest만으로 완료하지 않는다.
- not scored, missing oracle, malformed oracle, stale report, fingerprint mismatch, leakage가 하나라도 있으면 complete 금지.
- P7 이후 skill/manifest/cache가 바뀌었는데 P7 installed-runtime task를 재실행하지 않으면 complete 금지.

해야 할 일:
1. 전체 bucket full run을 실행한다.
2. 모든 case x variant가 raw artifact 기준 scored인지 확인한다.
3. missing/malformed oracle JSON 0, expected outcome conflict 0, validator false positive 0을 확인한다.
4. local path/private leakage가 raw/report 전체에서 0인지 확인한다.
5. HTML latest가 최종 run을 가리키는지 확인하되, raw artifact를 primary truth로 둔다.
6. P7 installed-runtime evidence가 현재 skill/manifest/cache 기준인지 확인한다.
7. unresolved flaky history가 0인지 확인한다.
8. 독립 리뷰를 수행하고 raw/summary를 workspace/plan/reviews/에 저장한다.
9. analysis/plan/evidence/closure와 indexes를 갱신한다.

필수 검증:
- python3 -B workspace/scripts/validate_plan_governance.py
- full run
- validate-run for full run
- report regenerate and raw artifact cross-check
- leakage scan raw/report
- current-file fingerprint check
- final independent review: Blocker 0, Major 0, 열린 Minor 0

완료 조건:
- full run pass다.
- not scored 0이다.
- missing/malformed oracle 0이다.
- local path/private leakage 0이다.
- report stale 0이다.
- current-file fingerprint mismatch 0이다.
- unresolved flaky history 0이다.
- installed-runtime user-like task evidence가 현재 파일 기준이고 high-risk trigger family coverage를 만족한다.
- 마지막 독립 리뷰 evidence가 Blocker 0, Major 0, 열린 Minor 0이다.

권한/승인:
- model runner, app-server, unsandboxed eval, GUI/browser 접근이 필요하면 데이터 전송 위험과 명령을 적고 사용자 승인 요청 후 진행한다.
- 승인 후에도 policy가 막히면 complete 금지. infrastructure-blocked로 기록한다.

최종 응답:
- full run id/status
- not scored/missing oracle/leakage/fingerprint/flaky 요약
- report/latest 검증 결과
- P7 evidence current 여부
- review evidence 경로와 finding count
- 검증 명령과 결과
- P8 완료/미완료 판단
- Serena 사용 여부 또는 생략 이유
```
