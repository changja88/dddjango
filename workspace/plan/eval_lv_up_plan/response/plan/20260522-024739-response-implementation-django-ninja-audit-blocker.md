수정 대상: report

# implementation-django-ninja P4 완료 감사 차단 계획

## 목표

현재 case/answer/evaluator 수정은 보존하고, targeted eval pass evidence가 없는 상태를 완료로 오판하지 않는다.

## 실행 계획

1. 기존 run artifact로 두 case의 실패 원인을 `sandbox/authorization`으로 기록한다.
2. 승인 거부 이후 같은 unsandboxed targeted eval 요청을 반복하지 않는다.
3. 로컬 validator를 실행해 case/answer/evaluator 구조 결함이 없는지 확인한다.
4. subagent limit으로 fresh subagent review가 불가능하면 fallback review를 파일 증거 기반으로 남긴다.
5. 최종 응답에는 미실행 targeted eval과 사용자 실행 명령을 명확히 남기고 완료 판정을 하지 않는다.

## 사용자 실행 명령

```bash
make eval-one BUCKET=response CASE=case-response-django-ninja-endpoint TRY_NUMBER=1 SCOPE=targeted TOPIC=implementation-django-ninja-p4 EXTRA_ARGS=--rerun JOBS=1
make eval-one BUCKET=response CASE=case-response-drf-ninja TRY_NUMBER=1 SCOPE=targeted TOPIC=implementation-django-ninja-p4 EXTRA_ARGS=--rerun JOBS=1
```

## 종료 기준

- 두 case의 targeted eval pass run id/status가 확보되기 전까지 P4 completion audit은 미완료다.
- pass evidence가 확보되면 현재 case별 검증표를 갱신하고 completion audit을 다시 수행한다.
