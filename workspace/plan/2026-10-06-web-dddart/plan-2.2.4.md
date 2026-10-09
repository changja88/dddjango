# dddjango-web 2.2.4 — 브라우저 시험은 샌드박스 밖에서 (운영자 · 10-10 · 설계 점검 · 구현 · 작은 끝까지 시험 반영판)

## 바탕
- 바탕: R main `c9016872`(배포된 dddjango-web 2.2.3 + dddjango 2.19.2). 2.2.4 는 패치다(산문만 — 검사기 · 도구 · 픽스처 · 매니페스트 구조 무변).
- 사본 `<S>/web-224`(가지 `web-224`). `<S>` = `/private/tmp/claude-501/-Users-hyun-Desktop-dddjango/ed01792c-e467-4a58-a794-ed16237ffb9e/scratchpad`. 근거 기록 `<S>/web-224-notes/`(진단 `diagnose.md` · 계획 `plan.md` · 설계 점검 `check-1.md` · 구현 diff · 작은 끝까지 시험 `e2e-*`).
- 사용자 보고(10-10 02:49 스크린샷): «Google Chrome for Testing 응용 프로그램이 예기치 않게 종료되었습니다» — «web 플러그인 같은데 계속 크롬을 쓰는데 문제가 있는 것 같다 · 원인 파악해서 수정해줘».
- 사용자 결정(글자 그대로): «완료되면 배포까지 진행해줘»(10-10 03:11:01 date 뒤 · 03:11:45 date 앞) = **결정 10 — 2.2.4 는 다 되면 배포까지**.

## 판정 — 뿌리
- macOS 충돌 기록 79건(10-03 ~ 10-10)이 모두 크롬이 뜨는 순간 죽은 두 꼴이다 — 전체 Chrome(Chrome for Testing 151 · Google Chrome 154)은 `TransformProcessType → _RegisterApplication → abort()`(앱 묶음이라 macOS 대화상자), headless shell 은 V8 `SIGTRAP`(대화상자 없음).
- 같은 실행 파일이 셸에서는 정상이고 `codex sandbox -c sandbox_mode="workspace-write"` 안에서는 두 꼴 그대로 죽는다(전체 Chrome exit 134 · headless shell exit 133 + `bootstrap_check_in org.chromium.Chromium.MachPortRendezvousServer…: Permission denied`). **Codex 의 macOS 샌드박스가 Chrome 시작에 필요한 시스템 서비스를 막는다.**
- 02:49 대화상자의 크롬(pid 4235)은 lane-6-3-21 Codex 가 돌린 브라우저 시험이다(레인 출력 `[pid=4235] <process did exit: exitCode=null, signal=SIGABRT>`). lane-6-3-29 · 6-3-26 도 같은 때 같은 실패(`BrowserType.launch: Target page, context or browser has been closed`).
- 플러그인 결함: dddjango-web 은 브라우저 시험을 쓰라고 하면서 어디서 돌릴지 말하지 않는다 → 레인이 시험 명령을 샌드박스 안에서 먼저 돌린다. 시작 실패를 시험 실패와 가르는 문장도 없어 «미통과는 환경 면제 없이 반송» 아래에서 같은 시험을 거듭 돌린다(반복 몰림이 이 문장 때문이라는 것은 추론).

## 넣은 것
- Coordinator 두 벌에 «**브라우저 실행 환경**(모든 모드 공통)» 문단 — 셸에서 브라우저를 띄우는 실행(브라우저 테스트가 섞인 테스트 단계 · SDK 후보 열거 · 경계 확인 · 골격 · 렌더 확인 스크립트)은 macOS 샌드박스 안에서 먼저 돌리지 않는다(그 밖 환경은 정책이 허용하는 환경에서 — 구현 검토 보완 ①).
  - Codex: 승격 요청이 허용되면(승인 정책 `never` 아님 · 도구 지원) 첫 실행부터 `sandbox_permissions: "require_escalated"` + 사유. `never` · 미지원이면 요청하지 않는다. Claude: Bash 샌드박스가 켜져 있으면 정책이 허용하는 샌드박스 밖 Bash 실행.
  - 범위는 브라우저를 띄우는 단계뿐 — `make` · 래퍼는 단계를 펼쳐 그 단계만(설치 · 마이그레이션은 함께 내보내지 않음).
  - 샌드박스 안에서 브라우저가 시작하지 못한 결과는 실패 노드 · 기준선 · green 어디에도 세지 않고 밖에서 다시 돈 결과로 정한다(밖에서도 실패하면 실제 실패). 같은 실행의 브라우저 없는 테스트 결과는 그대로.
  - 밖 실행 불가 · 거절 → 되풀이 · 범위 넓힘 없이 «브라우저 시험 미실행 — <사유>»를 G2 배너에(green 도 실패도 아님 · 판정 불가). coder-web 의 미실행 보고는 코드 반송이 아니다 — Coordinator 가 돌 수 있으면 대신 돌려 합치고, 못 돌면 미실행 · 검증 대기(슬라이스 완료 · green 으로 적지 않음).
  - 브라우저 도구(MCP)는 그 도구의 권한을 따르고, 사용자 브라우저 확인은 기존 안내 그대로.
- step 6 전수 테스트 · 수정 모드 step 5: «미통과는 환경 면제 없이 coder-web 반송» → «유효하게 돈 테스트의 미통과는 …» + 시작 불능 · 승격 불가 · 거절은 위 문단을 따른다.
- 끝 green ⑤ 실행 규칙 끝: 기준선 · 비교 · 요동 재실행도 같은 규칙 · 시작 못 한 테스트는 실패 노드로 세지 않는다.
- coder-web 두 벌 «층별 green 래칫» 끝: 같은 규칙(자기 완결) · 승격 불가 · 거절이면 명령 · 사유 · 이미 돈 결과를 «브라우저 시험 미실행»으로 보고 · 샌드박스 안 시작 불능 · 밖 실행 불가 · 거절은 수정 시도 한도에 세지 않는다(밖에서도 재현된 실패는 실제 실패 — 기존 수정 시도 · 보고 규율 · 구현 검토 보완 ②) · 테스트 · 하니스 · 브라우저 판을 바꿔 우회하지 않는다.
- `implementation-test/references/final.md` §4 «샌드박스 안 브라우저» 한 항목(두 벌 byte 동일).

## 점검과 다르게 정한 곳
- 설계 점검은 «권한 거절 근거가 있으면 미실행 · `TargetClosedError`·`SIGABRT`·`SIGTRAP` 만으로 원인 확정 금지»를 권했다. 구현은 원인을 표지로 가르지 않고 **샌드박스 밖에서 다시 돈 결과로 정한다**(밖 실행 불가 · 거절일 때만 미실행). 까닭: 전체 Chrome for Testing 은 샌드박스 안에서 stderr 없이 SIGABRT 로 죽어 권한 거절 문구가 남지 않는다(운영자 재현). 밖 재실행은 진짜 Chrome · 하니스 결함을 실제 실패로 남긴다.
- 구현 검토(Codex)는 이 선택을 «통과»로 봤다 — 이 처분은 브라우저 **시작** 단계의 실패에만 쓰고, 시작 뒤 단언 실패나 실행 중 충돌로 넓혀 읽지 않는다.

## 넣지 않은 것
- 브라우저 실행 파일을 headless shell 로 고정하라는 규칙 — 대화상자만 줄고 샌드박스 안 실패는 그대로라 뿌리가 아니다(프로젝트 하니스가 `chromium.executablePath()` = 전체 Chrome 을 고르는 것은 프로젝트 쪽).
- Codex 설정 · 실행 정책 변경 — 사용자 설정이라 플러그인이 낼 수 없다.
- 검사기 강제 — 실행 위치는 정적 검사 대상이 아니다.

## 멈출 기준과 결과
| 기준 | 결과 |
|---|---|
| S1 `make verify-web`(사본) | 구현 뒤 exit 0(03:10:52 ~ 03:18:17) · 구현 검토 보완 뒤 exit 0(03:21:39 ~ 03:29:16) — 픽스처 FAIL 0 · 문단 대조 · references byte 미러 통과 |
| S2 작은 끝까지 시험(scratch · headless shell 로 data: 문서 글자를 확인하는 브라우저 시험 1개 · 레인과 같은 정책 workspace-write + on-request) — 원본 도구 호출의 승격 인자로 판정 | 옛 판(2.2.3 문구): `./run_tests.sh` 를 샌드박스 안에서 먼저 돌려 `browserType.launch: Target page, context or browser has been closed` → 승격해 통과. **새 판(사본의 고친 coder-web 파일을 읽힘): 첫 실행부터 `require_escalated` · 사유 «브라우저 테스트 단계 — Codex 샌드박스 안에서 Chrome이 시작하지 못함» · 통과 · 새 크롬 충돌 0** |
| S3 검사기 · 도구 · 픽스처 무변 | 바뀐 파일 6(산문) |

## 알려진 한계
- 실제 레인에서 다시 본 것은 아니다 — 첫 실전은 2.2.4 를 받은 다음 web 레인.
- 승격 심사(`auto_review`)가 거절하면 «브라우저 시험 미실행»으로 G2 에 올라간다(지금 레인 설정에서는 브라우저 시험 승격이 통과해 왔다).
- 진행 중인 레인은 설치본을 새로 받아야 이 문구를 읽는다 — 그 전에는 발주자가 «브라우저 시험이 섞인 명령은 처음부터 샌드박스 밖(require_escalated)으로»를 알려 줄 수 있다.
