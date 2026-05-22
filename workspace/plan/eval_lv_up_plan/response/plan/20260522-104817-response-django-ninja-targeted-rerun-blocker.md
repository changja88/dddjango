수정 대상: report

# implementation-django-ninja P4 targeted 재평가 차단 계획

## 목표

현재 targeted eval 재시도 결과를 기록하고, pass evidence가 없는 상태를 완료로 오판하지 않는다.

## 작업

1. 새 sandbox run id와 실패 원인을 inventory에 기록한다.
2. approval reviewer가 거부한 unsandboxed eval은 우회하지 않는다.
3. repo-side validator 통과와 review 결과를 별도 evidence로 유지한다.
4. pass run이 없는 한 P4 complete로 표시하지 않는다.

## 필요 외부 검증

아래 명령은 sandbox 밖에서 명시 승인된 환경에서 실행되어야 한다.

```bash
make eval-one BUCKET=response CASE=case-response-django-ninja-endpoint TRY_NUMBER=1 SCOPE=targeted TOPIC=implementation-django-ninja-p4 EXTRA_ARGS=--rerun JOBS=1
make eval-one BUCKET=response CASE=case-response-drf-ninja TRY_NUMBER=1 SCOPE=targeted TOPIC=implementation-django-ninja-p4 EXTRA_ARGS=--rerun JOBS=1
```

## 완료 기준

- 두 case 중 추가/수정된 모든 case에 pass targeted run id/status가 생긴다.
- run artifact에 public prompt, baseline/with output, command, event stream, stderr, exit status, baseline isolation, prompt-input, answer-oracle evaluation JSON이 남는다.
