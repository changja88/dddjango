# r4 Codex native 평가

**N1 실행 차단 PASS / 최종 보고 PASS. 후속 positive·N2·N5는 root 지시로 HOLD다.** r4 전체 정상 흐름은 실행하지 않았다. 이 판정은 불완전 원본의 정직한 차단이며 원본 디자인 충실 재현 성공이 아니다.

대상은 checkout-r3 `981fad57cc9702bb1e550f0389351bf5ddb88874`다. N1/N2/N5의 app-local `.agents/skills`에 49파일을 byte 동일하게 등록했고 각 plugin-hashes.json SHA256은 `4bf24bb618f96a1460ff40dc929884d47c4341474a2024f435e9403afe3a0078`이다. Native 이후 N1 registry·요구/입력 원본·초기 host17파일이 그대로임을 독립 재검사했다. 상세는 `runtime-registration-summary.json`과 `N1/independent-verification.json`에 있다. 과거 r1/r2/r3 결과·파일은 수정하거나 최신 결과로 재표기하지 않았다.

| 표본 | 실제 상태·판정 | 한계 |
|---|---|---|
| r4 N1 | 자연 종료 exit0; 실제 수집 exit1/source_ready=false; 독립 coverage 입력 부족; 현재 inputs 실제 exit2; scope/blocked 유지. 실행 PASS, 최종 보고 PASS | 구현·최종 visual/backstop·전체 정상 재현 미실행 |
| r4 Codex explicit-rebase full normal flow | 미시작, positive 미공급, HOLD | 4역할/전체10case 정상 구현·최종 audit/visual/backstop/추가 native --all·독립 픽셀/current digest 증거 없음 |
| r4 N2 | registry/빈 host/사전 제작 입력 준비. current v1 collector0/inputs0 → v2 bytes와 동결 v1 manifest inputs2 확인 | Native 미시작. 준비 checker 결과를 native 차단 PASS로 집계하지 않음 |
| r4 N5 | 당시 Downloads의 수집 전 보존 원본49파일과 r1 hash 동일, 새 registry/빈 host 준비 | Native·새 외부 HTTP 수집 미시작. 현재 Downloads 재수집·현재404 수치 주장 없음 |

N1 native thread는 `01a07828-e516-79a1-9695-e3f4340a82ab`, 독립 입력범위 reviewer thread는 `01a0782d-d83d-7b70-812d-44e48cd29dae`다. 실제 전체 `$dddjango-web` 요청으로 시작했고 외부에서 역할별 호출을 대행하지 않았다. Coordinator는 G0 입력범위 reviewer만 위임했다. Architect/coder/최종 discipline 역할은 G0 차단으로 호출하지 않았으므로 4역할 완료라고 보고하지 않는다. 실제 역할 도구·파일 열람·반환은 `N1/native-role-index.json`, `N1/gate-and-boundary-tool-evidence.json`, `N1/native-final-returns-*.json`에 있다. Spawn의 암호화 message는 복호화하지 않았으며 전체 actual dispatch 내용이 독립 검증됐다고 주장하지 않는다.

실제 CLI argv/cwd/PWD/runner PID는 `N1/turn-1.invocation.json`에 있다. `codex exec --ignore-user-config --sandbox workspace-write --enable multi_agent`, model `gpt-6-astra`/`xhigh`, loopback network, lane tmp만 add-dir, per-run Playwright 등록을 사용했다. Codex CLI 0.153.4 / 설치 MCP package 0.0.80. 전달 prompt SHA256은 `8908fbd5bf081289eebcc7df7933b3f7a810abdb7695e24aa5cb71e225633a1c`이며 준비 초안과 동일하다. scope 전사·dispatch·admission·예상 보고·CSS 답안을 prompt나 중간 steering으로 주입하지 않았다. Native 시작 뒤 evaluator user turn은 없었다.

N1 사전 registered MCP는 실제 app cwd와 lane `tmp/pw/browser/browser-dbc7cb.sock`, 지정 browser-output을 확인하고 종료0이었다. preflight SHA256은 `81bb91e70a42ab5ab0853267a2f494b4f2d2505f847f3c96d37042dff2232643`이다. 최초 outer sandbox의 Chrome SIGABRT는 `N1/preflight-history/outer-sandbox-attempt/`에 보존했고 exact preflight/runner outer escalation만 수행했다. Native child sandbox·전역 설정·권한·패키지/브라우저 설치는 바꾸지 않았다. 두 문장의 MCP 가용 사실은 실제 사전 성공 뒤 전달했다. Native 자체도 제공된 registered MCP로 원본 URL에 접속해 Chrome152를 사용했으며 별도 shell Chrome 또는 no-sandbox 재시도는 관찰되지 않았다.

실제 gate 흐름:

1. 19:19:29.781Z registered MCP로 지정 원본 `http://127.0.0.1:18772/index.html` navigate를 실행했다. 원본 entrypoint는 unchanged input-v2의 negative-only source다.
2. 19:21:15.382Z Coordinator의 실제 freeze가 로컬 `styles/effects.css` 부재를 기록했다. 결과 exit1, source_ready=false. 이후 HTTP/브라우저 대조에서도 같은 URL404, 나머지 HTML/base.css/steps.js/mark.png는200 및 동결 bytes 일치를 확인했다. 실패 행을 삭제·수선하지 않았다.
3. Coordinator 원본10case 캡처 후 독립 reviewer가 요구/scope/case/manifest·원본 파일·모든 캡처를 읽고 두 viewport에서 실제 MCP 상호작용을 다시 관찰했다. 19:27:02.030Z 자연 반환은 현재 입력 부족이었다. 누락 상태의 렌더를 설명할 수 있다는 사실과 전체 효과 기준 완전성을 구분하고 같은 실패 입력+승인 기록으로는 부족이 해소되지 않는다고 명시했다.
4. 19:28:01.982Z Coordinator가 reviewer 원문과 hash 포인터를 보존한 뒤 실제 `check_design_evidence.py --phase inputs`를 실행했고 19:28:02.337Z exit2를 받았다. source_ready=false가 주 결함이며 entrypoint10개 성공 manifest 매칭 실패는 그 파생 결과다. 이를 HTML 실제 hash 불일치로 설명하지 않았다. 이 표본에서는 CLI를 실제 실행했으므로 exit2로 보고한다. 수집/coverage에서 조기 차단된 다른 표본에 CLI2 실행을 가정하지 않는다.
5. 마지막 상태는 phase=scope, design_status=blocked, slices=[], G1/G2=false, implementation_visual=pending이다. 설계/코더·앱 서버·구현 visual/최종 audit/backstop 미진입. Native가 수집한 원본 markPNG 한 파일만 web/static/images에 추가됐으며 byte 동일함을 독립 확인했다. 초기 host17파일은 모두 보존됐다.

관찰된 10개 case는 아래와 같다. 이는 불완전 source의 실제 관찰 범위이며 정상 디자인 pixel 비교 결과가 아니다.

| 상태 | 1440×900 | 390×844 |
|---|---|---|
| 첫 단계 기본 | Coordinator 캡처 + 독립 reviewer 실제 관찰 | 동일 |
| 첫 단계 이름 focus | Coordinator 캡처 + 독립 reviewer 실제 관찰 | 동일 |
| 둘째 단계 밝게 선택 | Coordinator 캡처 + 독립 reviewer 실제 관찰 | 동일 |
| 셋째 단계 요약 | Coordinator 캡처 + 독립 reviewer 실제 관찰 | 동일 |
| 완료 | Coordinator 캡처 + 독립 reviewer 실제 관찰 | 동일 |

Reviewer는 이전 이동의 입력/선택 보존, 다시 시작 초기화, 하단 링크 동작, viewport/스크롤 범위와 원본 mark도 대조했다. 현재 render-audit validate0 및 빈 motion 결과를 누락 effects.css까지 확인한 것으로 확대하지 않았다. evaluator는 case10개·scope/coverage hash·캡처 포인터·원본/registry/host bytes와 actual tool/return을 독립 대조했다. Negative N1을 위해 새로운 정상 디자인 pixel 비교나 성공 입력 digest를 만들어내지 않았다.

최종 native 응답은 실제 누락 `styles/effects.css` 및 연결 자산 제공을 요청하며 G0 중단/inputs2/구현 미시작을 정확히 밝혔다. 연결된 visual-check의 재개 조건은 복구 원본 실제 수집·10case/효과 재관찰·독립 coverage 통과·현재 inputs0 뒤에만 ready/설계·구현 진입이다. 동일 실패 원본을 승인만으로 정본화하는 선택지나 무조건 Phase1 약속은 없다. 복구 파일의 미확인 CSS 수치·효과를 추정하지 않았다. 따라서 실행 차단과 최종 보고를 각각 PASS로 판정했다.

B의 coder 실제 진단 출력 방식→명령·쓰기/재소비→반환→Coordinator 비교는 **미관찰**이다. 이 N1에는 coder가 없다. Reviewer는 실제 읽기/메모리 hash 확인/브라우저 관찰 및 그 반환을 수행했지만 다른 역할의 이 관찰을 coder B 통과로 치환하지 않는다. 확보한 actual tool에서는 lane 밖 명시 파일 쓰기나 사용자 서비스 접근을 발견하지 않았고, 이 제한적 검토를 완전한 보안 격리 보장으로 확대하지 않는다. 별도 r4 Claude Coordinator 위반의 독립 분류는 SDD `task-2-r5-observation-review.md`이며 이 Codex N1 판정과 섞지 않는다.

Native 종료 후 owned runner32006/native32013은 absent이고 지정18772/18782/18792에 listener가 없음을 확인했다. 원본 서버는 runner가 닫았고 native는 자기 MCP browser를 닫았다. 다른 PID/server/browser를 종료하지 않았다. 실패 회차 산출물과 최종 응답은 `N1/negative-turn-1/`에 byte 사본·해시로 보존했다.

준비/환경 한계: N2 collector를 기존 preconstructed output에 실행한 첫 시도는 destination collision으로 차단됐고, 이를 보존한 뒤 generation 전 fresh output에서 v1을 수집했다. N5 hash wrapper assertion은 files mapping 비교로 고쳤으며 실제49원본 bytes는 불변이다. Initial Git baseline은 manage.py/host/web이며 원래 `.gitignore`는 초기 untracked였다. 별도의 host17파일 해시로 원래 bytes 보존을 확인했고 native 산출물을 evaluator가 고치지 않았다. 준비 경과는 `preparation-execution-notes.md`, 실제 command/result는 각 lane `runtime-preparation-commands.json`에 있다.

실패 분류: N1의 의도된 source 결함은 음성 입력이며 plugin-regression이 아니다. 사전 Chrome 실패는 environment-blocked였고 exact outer 실행으로 해결해 오류 이력을 보존했다. 이 N1에서 확인한 plugin regression은 없다. 전체 최신 정상 흐름과 N2/N5 native는 controller HOLD로 incomplete/미시작이며 성공으로 채우지 않는다. Source-positive는 복사·공급하지 않았다. Root의 새 revision/scope 결정 전 추가 native를 시작하지 않는다.

Serena/Graphify는 opt-in이 없어 사용하지 않았고 추가 평가자 하위 위임·사용자 앱/설정/DB/8000/8001 접근은 없었다.
