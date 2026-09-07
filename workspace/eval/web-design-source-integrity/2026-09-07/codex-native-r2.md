# Codex r2 native 평가

대상 revision `d90aa90192be686de0a7ec6b0be1225637f927f4`. 이 결과는 r3 또는 최신 revision 평가로 재명명하지 않는다. P1b의 전체 Coordinator는 turn 2에서 자연 완료했고 독립 검증을 통과했다. 프로토콜 추가 native `--all`/current visual/종료 정리 turn 3도 exit 0으로 완료했다. 최종 판정은 **P1b + N3 PASS**다.

## 표본 구분

| 표본 | 현재 판정 | 범위 |
| --- | --- | --- |
| P1 초기 | 제한 표본·채점 제외 | 절차 안내 문구와 초기 브라우저 환경 실패를 보존. native 중단 후 대체 |
| P1b + N3 | PASS — 전체 native 완료·독립 10/10·최종/추가 전역검사 통과 | 새 empty host·새 session·동일 input-v2·49개 d90 registry |
| r2 N1/N2/N5 | 미시작 | 준비 파일만 존재. r3 새 registry에서 별도 실행 배정 |

N5 실제 디자인 성공이나 media/API 성공은 이 정상 fixture 결과로 주장하지 않는다. 원본은 평가용 로컬 다단계 fixture다.

## 실제 실행과 경계

Thread `01a077a9-539d-76a0-90c1-f27c4efa32d8`, build `P1b/app/.dddjango-web/20260907-0201-record-setup`. 초기 host HEAD `92435f67d593f501177b9a1a220ed43e4d2c3740`. 화면 없는 host-v1 17파일을 새 앱으로 복사했다. `P1b/initial-host-hashes.json`, `host-initialization.json`, `input-hashes.json`, `plugin-hashes.json`에 생성 전 기준선을 보존했다. 현재 원본 입력 12파일과 local skill registry 49파일은 동일 bytes다.

실제 argv/PWD/cwd는 `P1b/turn-{1,2,3}.invocation.json`, 요청은 각 `turn-*.prompt.md`, CLI stdout/stderr/exit/최종 응답은 같은 prefix에 있다. `codex exec --ignore-user-config --sandbox workspace-write --enable multi_agent`, gpt-6-astra/xhigh, network_access=true, app cwd/PWD와 lane tmp를 사용했다. `actual-model-contexts.json`은 실제 turn_context에서 모델을 추출한 기록이다. Marketplace 설치 검증이 아니라 app-local `.agents/skills` byte 등록 실행이다.

지정 Python/Chrome/Playwright MCP만 사용했다. source 18772와 app 18782의 task 소유 서버·새 isolated browser를 사용했고 API 18792는 미사용이다. 사용자 앱/DB/설정/8000/8001에 접근한 실행은 관찰되지 않았다. native 실행의 실제 파일/도구 소비는 `role-artifact-tool-references.json`, 전체 actual tool은 `native-tools-*.json`, 역할 metadata/turn은 `native-role-index.json`으로 연결된다. scope에는 실제 작업·증거·임시 경로, 포트, 서버 수명, 지정 Python/Chrome/MCP 제약이 보존됐다. 다만 spawn/send/followup의 본문은 런타임 암호화로 직접 열람할 수 없다. 이를 복호화하지 않았으며 dispatch 본문 전체 전사 PASS나 모든 하위 도구의 완전한 권한 증명으로 과장하지 않는다. 실제 callee scope/원본/증거 소비와 관찰 가능한 명령 경계를 기준으로 판정했다.

## 전체 native 역할과 입장

Coordinator가 직접 `dddjango-web`을 읽고 독립 역할을 생성했다. 외부 평가자가 역할별 호출을 대행하지 않았다.

| 역할 | 실제 thread |
| --- | --- |
| 원본 범위 검토 | 01a077ac-fc42-7531-9a9d-186384ccc8a3 |
| architect | 01a077b1-431b-7461-8541-f7e56e08a9ba |
| design review | 01a077b7-ee63-7352-9cc8-b91c07f2a68f |
| architect finalize | 01a077ba-6b9a-7543-b627-2773200fb351 |
| coder style | 01a077bd-387d-7602-a3ca-b0ee6baf22f1 |
| quota 중단 coder page | 01a077c4-7c5d-7951-8a02-c4d4f3b52b79 |
| 재개 원본 범위 검토 | 01a077dc-c58a-7171-8df3-0f3d99d83b42 |
| 재개 coder page | 01a077e1-9645-7933-91bd-fc1f86c216f4 |
| final discipline audit | 01a077ec-83a1-72d2-8116-b24b931ac498 |

초기 수집은 원본 HTML/CSS2/JS/PNG 5개 모두 성공, source_ready=true였다. Native Coordinator와 별도 범위 리뷰가 두 viewport의 모든 상태를 직접 브라우저 관찰하고 10case를 보존했다. 17:07:21Z 실제 inputs exit0 뒤 17:07:48Z ready/design 진입을 확인했다. 구조 문장 변경과 quota 재개 때는 native가 독립 coverage/current source를 다시 확인하고 current pointer/digest를 갱신했다. N3 비권위 첫 단계 desktop 완료 메모를 요구 축소 근거로 사용하지 않았으며 전체 효과/10case를 유지했다. 근거는 build/coverage-review.md 및 해당 역할 actual tools다.

실제 caller/callee 입장은 `coder-admission-tool-evidence.json`, `coder-admission-independent-verification.json`, `page-resume-current-record-read-excerpt.json`에 raw thinking/암호화 대화 없이 기록했다.

| 코더 호출 | 현행 호출 record 열람 | 자기 inputs 결과 | 첫 mutation | 좁은 판정 |
| --- | --- | --- | --- | --- |
| style call 1 | 17:21:58.270Z | 17:21:58.516Z exit0 | 17:25:43.956Z tokens.css apply_patch | PASS |
| page call 2 재개 | 18:01:26.193Z result | 18:01:37.870Z exit0 | 18:03:17.269Z apply_patch | PASS |

모든 선행 실제 callee tool을 검토해 먼저 mkdir/write/edit/delete한 흔적이 없음을 확인했다. Quota 중단 page call 1은 inputs0까지 있고 mutation이 없으므로 독립 완료 입장 사례로 집계하지 않았다. 재개 코더의 현재 자기 검사로 별도 판단했다. Coordinator는 코더 반환의 command/target/call/exit/digest를 현재 자기 기록과 대조했다. admission-only 판정은 이후 완료/시각 판정과 분리한다.

## 독립 10 case 대조

평가자는 새 Chrome과 새 두 context에서 원본과 구현을 각각 자연 UI 순서로 관찰했다. `independent-source-observation/`, `independent-observation/`에 별도 PNG/DOM/computed/HTTP/console 증거를 기록했다. 원본은 oracle-v2와 동일했고 구현도 각 같은 원본 상태와 pixel diff 0이었다. 원본·구현 캡처는 서로 다른 실제 URL의 screenshot으로 만들어졌으며 evaluator가 원본 PNG를 구현 PNG로 복사하지 않았다.

| Case | 1440×900 | 390×844 |
| --- | --- | --- |
| step1-default | PASS, pixel diff 0 | PASS, pixel diff 0 |
| step1-focus | PASS, pixel diff 0 | PASS, pixel diff 0 |
| step2-selected | PASS, pixel diff 0 | PASS, pixel diff 0 |
| step3-review | PASS, pixel diff 0 | PASS, pixel diff 0 |
| complete | PASS, pixel diff 0 | PASS, pixel diff 0 |

이름 하늘·밝게 선택, 이전 입력 보존, 요약, 완료, 재시작 빈 이름/차분하게 초기화, 하단 링크 URL 유지가 실제 조작으로 통과했다. 두 viewport 모두 HTTP6개 200, console/page error0, 외부 요청0, mark decode 정상이다. 복합 panel shadow/blur/반투명/pseudo선, 자식 mark 복합 filter, primary/label 효과, focus ring/inset, 전체 높이와 하단까지의 가시성을 확인했다. 원본 desktop 이전 버튼의 세로 두 줄도 원본대로 보존했다. 신규 control radius와 focus glow는 원본 선언 출처 주석과 token 등록/실제 var 소비를 확인했다. oracle CSS 정답을 native prompt에 제공하지 않았다.

## 최종 감사·게이트

Native final_audit는 18:15:17Z부터 원본/구현 전10case를 직접 재조작하고 실제 캡처와 코드를 독립 대조했다. 18:18:41Z 반환은 blocker/important/nit0, 미검증 적용 조건0이었다. 다른 설계 리뷰의 결론을 받아쓰기하지 않았으며 source·구현 URL/현재 bytes/동작/효과를 자체 확인했다. 18:16:49Z 감사자 실제 visual gate도 exit0이었다. `native-final-returns-01a077ec-83a1-72d2-8116-b24b931ac498.json`에 원문 반환을 보존했다.

Coordinator는 감수 뒤 G2 승인/verified/finalize를 기록하고 18:21:01Z 최종 정규 backstop 26종 blocker0을 실행했다. 검사기 `--only` 미지정은 이미 26종 전체 검사를 뜻한다. 프로토콜 `--all`은 diff 범위를 푸는 추가 전역 검사이며 이를 원래 정규 gate 누락이나 plugin regression으로 분류하지 않는다.

평가자의 읽기 전용 `independent-final-checks.json`: current fingerprint0, visual0, `backstop --all --diff-base --design-build`0/26종 blocker0, Django check0. 신규 untracked 코드도 실제 BackstopContext.touched에 모두 포함돼 누락0이다. 현재 구현은 이 독립 검사·브라우저 관찰 뒤 변하지 않았다.

- input_digest: `0a5e5c465a86e843aef3d214c0f36adc69f7757cc7f56caa15f1c883bb4d9bad`
- implementation_digest: `fa6995cb278d157f65fdb78de09b69576a9e9ee5c1d28341a14162371bc26165`

## 개입·환경·한계

초기 P1(thread01a077a0-520e-78c0-85af-b1a46dd9aebd)은 scope 전사/dispatch를 명시 지시하는 wrapper와 초기 socket/Chrome 실패 때문에 controller 지시로 소유 native만 종료했다. `P1/controller-stop.json`, 원문 prompt/error/exit를 보존하고 채점에서 제외했다. P1b는 새 빈 host·새 thread이며 문제 문장만 삭제한 요구를 사용했다. `prompt-cue-removal.json`은 전후 문장/해시를 보존한다. caller/callee 순서 답안을 넣지 않았다.

설치본 근거에 따라 per-run MCP `PWTEST_SOCKETS_DIR=../tmp/pw`를 설정했다. `P1b/mcp-preflight.json`은 실제 MCP cwd=app, socket 실경로=lane/tmp 및 짧은 새 browser source 기동/종료를 증명한다. 초기 probe의 process undefined/tool 이름 오류/OS 내부 SingletonSocket 판별 오류는 평가자 환경 진단 이력이며 최종 probe로 정정했다. 전역 설정·auth·child sandbox는 변경하지 않았다.

P1b turn1은 실제 usage-limit로 exit1이었다. `quota-interruption.json`에 실제 오류와 마지막 역할 상태를 보존했다. turn2는 사용자 계속 진행 지시에 따라 동일 thread/현재 앱을 재개했다. native가 미완료 page 역할을 완료로 가정하지 않고 새로운 역할로 실제 재개했다. 코드/증거를 평가자가 수선하지 않았다. MCP lane/tmp filename 접근 거부는 native가 같은 코드를 code-string으로 전달해 복구했다. PIL 미설치 등 환경 진단 실패도 보존했으며 새 설치는 하지 않았다.

Git .git 읽기 전용 때문에 새 checkpoint/최종 commit은 생성하지 않았고 native는 미커밋 사실을 보고했다. 동등한 구현 전 초기 host HEAD를 diff 기준으로 사용했다. evaluator가 native 산출물의 commit을 대신하지 않았다. 생성 앱/명세/state/manifest/visual evidence를 evaluator가 변경해 통과시킨 작업은 없다. 추가 --all 요청은 별도의 프로토콜 검증 개입으로 보존하며 처음부터 자동으로 수행한 행동으로 집계하지 않는다.

Serena·Graphify는 opt-in 부재로 사용하지 않았다. 결과는 이 fixture/환경/실제 관찰 revision에 한정되며 모델 일반 신뢰도·실제 Downloads 디자인 성공을 보장하지 않는다.

## 추가 native 검사 완료

Turn 3은 같은 thread에서 실제 `backstop --all --diff-base --design-build`와 current visual을 실행해 둘 다 exit0이었다. `P1b/tmp/additional-global-verification-20260906T182646709834Z/`에 argv/cwd/stdout/stderr와 검사 전후152파일 변경·추가·삭제0을 보존했다. 기존 감사 대상 구현·원본·증거는 변하지 않았다. 소유 앱 PID62736은 이미 없어 신호를 보내지 않았고 isolated MCP browser_close는 열린 탭 없음을 반환했다. Runner는 자기 source 서버만 닫았다. evaluator의18772/18782 listener 조회는 결과 없음이었다.
