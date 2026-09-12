# 실행 환경과 판정 범위

- 개발 워크트리: `/Users/hyun/.cache/dddjango-web-a8-20260913`, 기준 `3e786dce64eee3da81d98e1dc2dcad598ab5d026`.
- 현재 작업은 web 산문 런타임의 반환·인계 계약 교정이다. micro와 독립 역할 checkpoint는 전체 native 플러그인 파이프라인 실행·설치 cache 검증이 아니다. 기존 A8 native 실패는 진단에 보존한다.
- baseline 첫 Codex CLI 시도는 in-process app-server 초기화 EPERM으로 모델 실행 전에 종료됐다. 그 시도는 행동 표본으로 세지 않고 기존 collaboration의 fresh 문맥으로 평가했다.
- 가용 브라우저 coder checkpoint의 초기 Playwright 호출은 profile already in use로 실패했다. root가 자기 작업용 about:blank 한 탭만 남았음을 확인하고 browser_close로 세션을 풀었다. 같은 MCP 재시도 후 원본·수정 전·수정 후 실제 조작을 완료했다. 실제 관찰 실패를 성공으로 바꾼 것이 아니라 환경 복구 뒤 별도 실제 실행을 수행했다. 초기 오류는 APP의 관찰 전 기록에 남아 있다.
- root의 새 감수 spawn/followup은 agent thread limit에 걸렸다. 이어 시도한 중첩 Codex CLI의 workspace-write·자동 승인 옵션·권한 확장 조합은 자동 승인 검토가 넓은 에이전트 권한을 이유로 실행 전에 거부했다. 이 CLI는 실행되지 않았다. 기존 평가 담당자가 기본 collaboration 도구에서 `fork_turns=none`으로 독립 감수 child를 디스패치하는 데 성공했다. 소스는 읽기 전용이고 쓰기는 지정 검토 증거뿐이다. 새 CLI·권한 확장·자동 승인 옵션이나 전역 설정 변경은 사용하지 않았다.
- 전체 검사 첫 실행은 기존 backend 2.18.2 봉인과 실제 2.18.3 manifest의 차이로 실패했다. 두 이전 manifest의 bytes와 실행 비트가 봉인 hash와 같음을 확인하고 정본 가이드의 재발행 도구로만 봉인을 갱신했다. 갱신 뒤 `make verify`는 6/6·exit 0이며 web runtime 12파일은 검증 전후 같은 hash다. backend 코드는 변경하지 않았다.
- 독립 시각 감수는 원본/A/B를 직접 조작하고 자신이 연 page 3개를 닫았다. 시작 때 보였던 기본 about:blank 한 탭은 남겨 두었다고 기록했다. 이를 추가 확인할 followup은 thread 상한으로 실행되지 않았으며, 모든 브라우저 컨텍스트를 닫았다고 확대하지 않는다. 소스·사용자 page·프로필·프로세스를 별도 조작하지 않았다.
- 최종 독립 구현 리뷰는 Critical 0 / Important 0, Spec·Quality PASS, ReadyToRelease YES였다. 비차단 기록 오류 한 건은 `role-review/report.md`의 대상 요소 개수를 12에서 11로 정정했다. 12는 캡처 수이며 `observations.json`의 요소는 11개다. 관찰 데이터·캡처·판정은 변경하지 않았다.

브라우저 캡처의 동일성은 이 통제 fixture와 실제 관찰한 상태에 한정한다. source의 2px inset이 3px focus ring 전체를 드러낸다고 해석하지 않는다. 원본 자체의 일부 잘림을 임의로 개선해 재현 성공으로 부르지 않는다.

커밋 직전 `git diff --cached --check`가 반환 보고서 3개의 EOF 빈 줄을 지적해 해당 줄만 제거했다(`micro/baseline/trial-05/handoff.md`, `role-browser-app/handoff.md`, `role-review/report.md`). 수행 진술·판정·CSS·관찰 데이터는 변경하지 않았다.
