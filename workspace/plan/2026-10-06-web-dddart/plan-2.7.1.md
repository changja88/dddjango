# dddjango-web 2.7.1 — 시험 멈추기는 묶음 SIGINT 먼저 (시험 · 게이트 자원 정리의 web 몫)

## 문제
- 낡은 시험 실행을 TaskStop · `kill -9` 로 멈추면 시험이 정리 단계(DB 서버 · 브라우저 닫기)를 돌지 못해 프로세스와 임시 자원이 남는다.
- `switch-check` 는 시험 명령을 새 세션(프로세스 묶음)으로 띄운다. 도구가 끊기면(ctrl+c · 묶음 SIGINT) 그 신호가 시험 묶음에 닿지 않아, 반례를 되돌린 뒤에도 시험이 남아 돈다(고아).
- 시간 초과는 곧바로 SIGKILL 이라 정리 단계가 돌지 않고, SIGKILL 뒤 출력 관 기다림에 끝이 없어 묶음 밖으로 나간 자손이 관을 쥐면 도구가 그 자손이 끝날 때까지 멈춘다.

## 고침
- `scripts/src/switch_check.py`(+ Codex byte 미러): 시간 초과 · 끊김(KeyboardInterrupt) 때 `stop_group` — 묶음에 SIGINT → `STOP_GRACE_SECONDS`(30초) 기다림 → 묶음에 남은 프로세스 SIGKILL(지도자가 먼저 끝나도 같은 묶음 자손까지) → `KILL_WAIT_SECONDS`(30초) 뒤 관을 닫고 wait. 기다림 중 다시 끊겨도 SIGKILL 단계는 돈다. 끊김은 묶음을 멈춘 뒤 다시 올리고, 반례 · 옛 시험 임시 파일 되돌림은 기존 `verify_rows` 의 finally 가 그 뒤에 한다(순서 그대로). 출력 · exit · 판정 문구(«시간 초과 n초»)는 그대로.
- 조정자 새 문단 «돌고 있는 시험 멈추기» · coder-web «작업 방식» 한 줄: 긴 시험은 명령 맨 앞에 `echo "PGID=$$" >&2;` · 멈출 때는 TaskStop · `kill` · `kill -9` 대신 끝 알림 전에 배경 명령 하나로 `kill -INT -- -<PGID>` 를 보내고 묶음이 끝날 때까지 최대 2분 `kill -0` 으로 확인(역할에게 2분을 셀 다른 시계가 없다 — 그 명령의 끝 알림이 «끝남» 또는 «2분 지남») → 2분 뒤에도 남으면 `kill -TERM` · 그래도면 조정자는 TaskStop · coder-web 은 `kill -KILL -- -<PGID>`(coder-web 도구 목록에 TaskStop 이 없다) · 곧 끝날 실행은 그대로. 조정자 문단은 `switch-check` 가 묶음을 멈춘 뒤 반례를 되돌리고 끝난다는 것과 `kill -TERM` · TaskStop 으로 끝난 `switch-check` 의 반례는 다음 호출이 먼저 되돌린다는 것을 덧붙인다.
- Codex 미러(조정자 · coder-web)는 «Codex 셸에서는 돌고 있는 시험에 신호를 보내지 않는다 — 끝날 때까지 기다린 뒤 다시 돌린다». 두 문단은 일부러 다르므로 `Makefile` verify-web 문단 대조 표지에 넣지 않는다.
- dddjango 2.25.0 의 같은 고침(시험 지원 도구의 묶음 멈춤 · 조정자 · coder 새 규범)과 짝이다.

## 시험
- `scripts/test/fixtures_patch231_switch.py` K 묶음(모두 도구 임시 폴더를 시험 폴더로 돌린다 · 시험 명령은 가짜 실행기):
  - K1 반례 실행 중 시간 초과 → 정리 표식 있음 · 같은 묶음 자손 끝남 · 반례 되돌림 · 도구 임시 폴더 없음 · exit 1.
  - K2 반례 실행 중 도구에 SIGINT → 같은 셋 · 끊김을 다시 올림(KeyboardInterrupt).
  - K3 SIGINT 를 무시하는 시험 · 자손 → 줄인 기다림(1초) 뒤 SIGKILL · 고아 0 · exit 1.
  - K4 묶음 밖(새 세션) 자손이 출력 관을 쥠 → SIGKILL 뒤 관 기다림(1초)에 끝 — 도구가 끝났을 때 그 자손은 아직 산다.
  - K5 멈춤 신호 뒤 기다림(8초) 중 두 번째 SIGINT → 곧 SIGKILL 단계 · 고아 0 · 반례 되돌림.
  - K6 시험은 SIGINT 로 정리하고 먼저 끝나지만 같은 묶음 자손은 SIGINT 를 무시하고 출력 관도 쥐지 않음 → 기다림 뒤 묶음 SIGKILL · 고아 0.
  - 기다림 두 상수는 작은 입구 스크립트가 모듈 상수를 줄여 띄운다(제품 코드에 시험용 손잡이 없음).
- 붉음 확인: 고치기 전 판(배포된 2.7.0 scripts 를 사본 밖에 푼 것)에서 K1(표식 없음) · K2(표식 없음 · 고아) · K4(관 기다림에 끝 없음) · K5(고아) 붉음. K3 는 두 판 모두 green(회귀 막이). K6 은 «정리 단계 안에 지도자가 끝나면 SIGKILL 을 건너뛰는» 판에서 붉음(고아).
- N6(`--timeout 2`)은 문구 · exit 1 · 작업 트리 그대로 — 기대 무변.
- `make verify-web`.

## 한계
- 도구가 `kill -TERM` · TaskStop 으로 끝나면 finally 가 돌지 않는다 — 남은 반례는 다음 `switch-check` 호출이 복구 상태대로 되돌리지만, 새 세션 시험 묶음은 남을 수 있다(사다리의 마지막 칸).
- web inflow · switch-check 작업 폴더의 «끊긴 실행 사본 쓸기»는 이번 판 밖(core 만).
- Codex 실행 확인은 하지 않았다(글만 맞춤).
