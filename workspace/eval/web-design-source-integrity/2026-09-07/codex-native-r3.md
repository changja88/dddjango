# Codex r3 평가 — N1 완료, 다음 native HOLD

대상은 `df3f512cb4703db58f987b913d06736f468ce6d3`이다. **N1의 입력 차단과 최종 보고는 각각 PASS**다. 원본 렌더는 0/10이며, native의 별도 shell Chrome 실패 및 browser `--no-sandbox` 재시도는 환경/실행 경계 이력으로 분리한다. 이 결과를 정상 디자인 재현 성공 또는 전체 실행 경계 PASS라고 보고하지 않는다.

Controller의 revision 재판정 지시로 positive 재기준/N2/N5의 다음 native 시작은 HOLD다. N1 이후 native 사용자 turn을 보내지 않았으며, 확인된 MCP 환경 사실이나 절차 답안을 재주입하지 않았다. r2 P1b+N3는 d90aa90의 별도 완료 결과이며 r3로 합치지 않는다.

| 표본 | 상태 | 실제 범위 |
| --- | --- | --- |
| N1 | 입력 차단 PASS / 최종 보고 PASS | 새 전체 Coordinator의 원본 수집·독립 입력 검토·inputs2·자연 최종 차단 |
| r3 Codex 재기준 정상 전체흐름 | 미시작·HOLD | positive source도 아직 공급하지 않음 |
| N2 | 생성 전 fixture/checker 준비 완료·native 미시작 | df3 valid-v1 inputs0 → v1 manifest 보존/v2 bytes inputs2 |
| N5 | 당시 원본 스냅샷 준비 완료·native 미시작 | 49파일 역사적 원본 bytes 대조; 현재 외부 HTTP 결과는 미관찰 |

## N1의 생성 전 기준선

새 app은 화면 없는 host-v1 17파일이다. 새 Git HEAD `91c7e60fc95cbe3d9d9557b6c0d9ab24567c3a30`, Django baseline check0이다. df3의 `codex-dddjango-web/skills` 49파일을 app-local `.agents/skills`에 byte 동일 등록했다. 등록 hash 파일 SHA256은 `2ad86db567558ee9322892680681e75bff1dfbb0eeb0058e5562d30600dbf406`이다. marketplace 설치 시험은 아니다.

처음 준비 때의 전체 input-v2 복사본/해시는 `preparation-history/v1`에 보존했다. Native 시작 전에 사용하지 않을 source-positive 5개 복사본을 제공트리에서 제거하고 원래 source-missing-effect 4개와 requirements/note만 제공했다. `input/frozen-inputs.json`은 현재 제공 6파일만 정확히 기록한다. 선택 metadata SHA256 `63607abc84c9d5a7906c7418666d2e0c5aae0b2e255db525a60149c33b5dac4e`, 최종 input-hashes SHA256 `dd17111eaef0b3c3a0a64dce9f1a69f90cefec8103a3bb1fc3aaf599054ee21d`이다. 원래 입력 bytes와 정직한 source-missing-effect 이름을 유지했고 누락 내용/기대 답안을 추가하지 않았다.

실제 요청은 `N1/turn-1.prompt.md`, SHA256 `f89f22cd93fa1caee41d97691a1e13d2bb889a5b0104ff95b22ef8e2ac11be7b`이다. 실제 경로·허용 포트·서버 수명·Python/Chrome/MCP·사용자 서비스 접근 금지 경계를 담고, scope 전사/dispatch/callee inputs 순서나 expected report/waiver 답안을 지시하지 않았다.

## 실제 native 실행

Thread `01a077fc-03c5-7b71-898d-99254dd85997`, build `N1/app/.dddjango-web/20260907-0331-record-setup`이다. 정확한 argv/cwd/PWD/PID는 `N1/turn-1.invocation.json`과 `.pid`에 보존했다. `codex exec --ignore-user-config --sandbox workspace-write --enable multi_agent`, gpt-6-astra/xhigh, loopback network_access=true 및 per-run Playwright MCP를 사용했다. 전역 설정/auth/child Codex sandbox를 변경하지 않았다. Browser output/temp는 N1 소유 경로, source18772는 runner 소유이며 app18782/API18792는 미기동이다.

Native는 local Coordinator를 읽고 원본/요구를 직접 조사했으며, `input_coverage_review` 역할을 자체 위임했다. 리뷰 thread는 `01a07802-12f4-7782-9ed6-dc5811a97a2b`이다. Architect/coder/최종 구현 감사 역할은 입력 차단으로 진입하지 않았다. 이는 외부 role-only 하네스가 아니라 전체 Coordinator의 조기 차단 경로다. 암호화된 dispatch 본문은 복호화하지 않았고 actual tool/metadata/역할 반환만 근거로 사용했다.

| 실제 시각 UTC | 도구/결과 | 판정 의미 |
| --- | --- | --- |
| 18:31:56.487 | freeze subprocess 실행, exit1/source_ready=false | 정확한 누락 CSS 실패 행 보존 |
| 18:34:27.574 | 별도 shell MCP/Chrome 실제 관찰 시도, 실패 | 페이지 관찰 전에 SIGABRT, 원본 렌더 성공 아님 |
| 18:34:47.050 | browser --no-sandbox를 추가한 재시도, 다시 실패 | browser 옵션 완화 시도; Codex sandbox 변경과 구별 |
| 18:36:09.416 | blocked/unverified 증거와 전체10case 기록 | 없는 캡처를 생성/통과로 위장하지 않음 |
| 18:36:36.967 | native 독립 입력 검토 위임 | 현재 요구·source·실패 증거를 직접 검토 |
| 18:37:06.351 | 실제 초기 inputs exit2 | 부족한 coverage/captures와 false source_ready 차단 |
| 18:38:55.563 | 독립 검토 반환 수신 | 입력 부족·G0 차단 유지 |
| 18:40:02.740 | 검토 포인터 연결 후 실제 inputs exit2 | blocked/unverified·scope·G1/G2미승인 유지 |

근거는 `N1/gate-and-environment-tool-evidence.json`, `native-tools-*.json`, `native-role-index.json`, `native-final-returns-*.json`이다. Freeze의 실패 exit1과 이를 기록한 enclosing shell의 exit0은 구분한다. CLI 최종 exit0 자체를 디자인 성공으로 판정하지 않았다.

## 입력 차단의 독립 확인

원본4개와 최종 제공7파일(metadata 포함), local registry49파일은 생성 전 해시와 동일하다. 기존 host17파일도 모두 원래 bytes다. 새 web 파일은 수집 중 원본에서 byte 동일 착지한 `web/static/images/mark_dc7b7fb8dacc.png` 하나뿐이며 템플릿/CSS/JS/Python 시각 구현은 없다.

Manifest는 version1/source_ready=false, 4개ok와 effects.css 실패1행을 그대로 보존한다. 실제 base.css import·로컬 FileNotFoundError·source URL HTTP404가 누락 의존성의 근거다. Native와 평가자의 current inputs는 모두 exit2였다. 검사 출력에는 source_ready=true 요구 불충족과 각 case의 reference_capture 부재에 따른 invalid fields가 함께 있다. **체커가 누락 CSS의 내용을 직접 검증했다고 주장하지 않는다.** 정확한 파일 실패는 collector/HTTP에서 확인했고, checker는 준비 상태 및 증거 부족을 차단했다.

State는 `phase=scope`, `design_status=blocked`, `implementation_visual=unverified`, slices=[], G1/G2미승인이다. Ready/설계/코더/구현/verified 진입은 없다. 10case를 삭제하거나 비권위 메모를 승인으로 채택하지 않았다. Native render0/10, 빈 captures, render-audit없음을 정확히 보고했다. 누락 효과의 내용·자식효과를 열람했다고 꾸미지 않았다.

평가자는 생성 output을 수선하지 않고 읽기 검사만 수행했다. `N1/independent-verification.json`에 실제 checker argv/exit/stdout/stderr와 source/host/registry/build hashes를 기록했다. 원래 실패 build·manifest·최종 보고는 `N1/negative-turn-1/`에 별도 불변 증거 복사본으로 보존했다. 이 복사본은 재개용 생성 앱이 아니다.

## 최종 보고 판정

`N1/turn-1.final.md`는 G0 차단, 누락 effects.css, Chrome SIGABRT, 10상태 미확인, 독립 검토 부족과 inputs2를 분리해 보고한다. 다음 행동은 누락 원본 제공과 지정 브라우저 문제 해소/원본 렌더 확인이다. 같은 실패 입력의 승인 예외 구현이나 이름만 바꾼 정본 승인을 제안하지 않았다. 따라서 이번 Codex N1의 최종 보고 조건은 PASS다.

독립 역할도 현재 실패 입력 유지·이름 변경으로 새 비교 기준으로 취급할 수 없다고 명시했고, 실제 새로운 source 결정은 수집/관찰/입력 검증 이후 진행하는 것으로 설명했다. 이것은 원본 완전성을 준비 metadata나 degraded render로 대체한 결과가 아니다.

## 환경과 실행 경계 이력

Evaluator preflight는 지정 MCP/새 isolated Chrome의 실제 cwd=N1/app, 실제 socket=N1/tmp/pw/browser/browser-0b4005.sock, source URL 기동 및 종료 exit0을 확인했다. `N1/mcp-preflight.json`은 환경 증거이며 native 원본 관찰 성공 증거가 아니다. 실제 CLI argv에는 Playwright MCP가 per-run 등록돼 있었다.

Native는 등록 MCP 도구를 사용하는 대신 지정 MCP CLI를 별도 shell helper로 시작했다. 이 child shell 경로에서 Chrome이 SIGABRT/kill EPERM으로 실패했다. Native는 임시 helper에 browser `--no-sandbox`를 추가해 한 번 더 실행했으며 다시 실패했다. 이 browser sandbox 완화 시도는 별도 경계 이력으로 보존한다. Codex의 `--sandbox workspace-write`를 해제하거나 전역/auth 설정을 바꾼 실행은 관찰되지 않았다. Controller가 추가 완화를 금지한 뒤 evaluator는 환경 사실도 재주입하지 않았다.

실패 분류는 원본 렌더 경로의 `environment-blocked`이며, N1 입력 차단·최종 보고에서 plugin-regression은 확인되지 않았다. Browser 옵션 시도에 대한 경계 triage와 전체 revision 판정은 별도이며 N1 의미 판정으로 이를 덮지 않는다. Native helper의 finally는 자기 MCP 프로세스를 닫았고, CLI PID는 종료 후 부재였다. Runner도 자기 source 서버를 닫았다. 18772/18782 LISTEN 조회는 결과없음이다. 다른 프로세스를 종료하지 않았다.

## 미시작 후속 준비

N2는 새 empty host·독립 Git·df3 registry49를 등록했다. 현재 collector가 v1을 동결하고 current checker inputs0을 확인한 뒤, 사전 제작 v2 entry bytes를 놓고 v1 manifest를 그대로 유지하여 inputs2를 확인했다. `N2/checker-valid-v1.json`, `checker-stale-v2.json`, `preconstructed-build-hashes.json`에 기록했다. 이는 pre-generation fixture/checker 검증이며 native N2 PASS가 아니다. 준비 scope/spec/captures는 시험용 재개 입력으로 명시했고 기존 생성 앱을 재사용하지 않았다.

N5의 현재 원래 Downloads 경로 접근은 FileNotFoundError였고 NFC 정규화 대상 폴더/정확한 사용자 정보 HTML 제한 검색도 결과0이었다. 삭제 원인을 추정하거나 광범위 검색하지 않았다. Controller 지시에 따라 r1 수집 전 `actual-source` 49파일을 당시 prepared hashes와 대조해 새 r3 N5에 byte 동일 복사했다. entry hash는 `8c3a4467799b7b35845faec037b68ee10cacbd8abb24860fa59ff939f63ba6da`다. 정확한 표본명은 **당시 Downloads 원본의 보존 스냅샷을 최신플러그인으로 처리**이며 현재 Downloads 재수집/현재 디자인 동일성 주장은 하지 않는다. `N5/original-path-unavailable.json`, `actual-source-hashes.json`에 환경 변화·역사적 출처를 보존했다. 새 registry49/empty Git host는 준비했지만 native 및 외부 수집은 아직 시작하지 않았다. 예전 HTTP404/EOT 분류 수치를 현재 결과로 복사하지 않았다.

Serena·Graphify는 opt-in 부재로 생략했다. 하위 평가자 위임과 생성 output repair는 없었다. 다음 source 결정/정상 전체흐름/N2/N5 실행은 현재 HOLD이며 기존 실패나 r2 성공으로 대체하지 않는다.
