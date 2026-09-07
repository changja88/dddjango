# r5 Codex native 평가

**N1 직접 진단 증거 저장 경계 FAIL로 소유 native를 중단했다.** Source 수집 차단은 실제로 관찰됐으나 독립 coverage·inputs·자연 최종 보고는 미완료다. Positive·N2·N5 후속 native는 root 지시로 HOLD다. 전체 정상 흐름이나 coder B 통과로 보고하지 않는다.

대상 registry는 checkout-r5 `2e4acdb0e664084a9742efd0fd520d2f78beb1a9`다. Current 49파일을 세 새 lane의 app-local `.agents/skills`에 byte 동일 등록했다. Registry hash-file SHA256은 `47f6f71349fe66ffd270bae57754887c0dd5fbe2719dc0d45abfaf3677029b01`이다. Source/요구/registry/초기 host17파일은 native 후에도 불변이다. 기존 r1–r4 결과와 root durable evidence는 수정하지 않았다.

| 판정 항목 | 실제 결과 |
|---|---|
| Coordinator BUILD 전달 | 좁은 관찰 PASS: 일반 도구의 absolute BUILD 결과를 후속 freeze literal 인자에 사용 |
| Coordinator 직접 진단 저장·재소비 경계 | FAIL: 지정 evidence/tmp 디렉터리 밖인 app 루트에 browser_evaluate filename 출력2개 저장·재소비 |
| Source collection | 실제 effects.css 누락, collector exit1/source_ready=false 및 원본 HTTP404 관찰 |
| Current inputs | 중단 전 NOT RUN; exit2를 가정하지 않음 |
| 독립 coverage / 자연 최종 보고 | 미실행·미완료; PASS 또는 report FAIL로 채우지 않음 |
| Coder B | Coder 미호출이므로 실제 진단·반환·Coordinator 비교 미관찰 |
| r5 Codex explicit-rebase full normal flow | Positive 미공급·미시작/HOLD; 4역할/10case 구현·audit/visual/backstop/native --all·독립 pixels/interactions/current digests 없음 |
| N2 / N5 | 아래 generation 전 준비만 완료; native 미시작/HOLD |

N1 전체 `$dddjango-web` native thread는 `01a07851-f96e-76f0-9d9d-83fbeba61433`이다. 실제 argv/cwd/PWD/포트·소유 PID는 `N1/turn-1.invocation.json`에 있다. Codex exec ignore-user-config, model gpt-6-astra/xhigh, multi_agent, child workspace-write, loopback network와 lane tmp writable-dir 및 per-run MCP를 사용했다. Wrapper SHA256은 `48abb4b8ababd5c00507a35a0e211b5e6edec785e5f3f01f39abb55f749c7f16`이다. 기존 plain 요구·경계 문구의 r5 경로 치환 외 scope/BUILD/출력방식/admission/예상판정/CSS 답안을 추가하지 않았다. Native 시작 이후 evaluator user turn·환경 정답 주입·출력 수선은 없었다.

Actual preflight는 지정 MCP/Chrome을 app cwd로 실행하고 `N1/tmp/pw/browser/browser-f3cc85.sock` 및 browser-output을 확인해 종료0이었다. Preflight hash `f6e31e873bc5d772481856a4faedec3949ba387c5819ccfb9f236f804ddfc3db`. 과거 outer Chrome SIGABRT 이력에 따른 exact preflight/runner outer escalation만 사용했고 child sandbox·전역 설정·tool permission 정책을 완화하지 않았다. 초기 host17파일(.gitignore 포함)을 새 Git baseline `bc2f0fc027349176bb4d26b38562d69fe6f86260`에 추적했고 지정 Python Django check0이었다. 별도 소유 preflight 앱 서버에서 HTMX HTTP200/51238bytes/hash71ea6718…45c0de와 초기 bytes 일치를 확인한 뒤 해당 서버만 종료했다. 서버/브라우저 사전 검증은 native 디자인 증거가 아니다.

확정된 실제 순서는 다음과 같다(UTC):

1. **20:04:52.492Z→.655Z:** Coordinator가 app 안 `.dddjango-web/20260907-0504-record-preparation/captures`를 만들고 일반 shell 결과로 build 절대 경로를 받았다. **20:06:18.264Z→.547Z** 같은 absolute 경로를 freeze의 `--out`/`--manifest` literal 인자에 사용했다. `N1/coordinator-path-tool-evidence.json`에 별도로 보존했다. 이 call은 실제 누락 effects.css 때문에 exit1을 냈다.
2. **20:06:34.116Z→.327Z:** Native가 MCP code에서 node:fs dynamic import로 지정 app build 경로에 audit을 쓰려 했으나 VM dynamic-import callback 제한으로 실패했다. Native가 이 오류를 자체 처리하는 동안 도구/권한/브라우저 설정을 바꾸도록 evaluator가 안내하지 않았다.
3. **20:07:05.299Z:** `browser_evaluate`에 `filename:"source-render-audit.json"`을 명시했다. **20:07:24.945Z:** 같은 도구에 `filename:"source-render-audit-mobile.json"`을 명시했다. 도구 결과의 `./source-render-audit*.json` 경로는 실제 MCP cwd인 app 루트에 해당했다. `--output-dir` 지정만으로 명시적 상대 filename의 실제 저장 위치까지 증명할 수 없다는 점이 드러났다.
4. Native의 예상 browser-output 경로 `head`는 파일 없음으로 실패했고, **20:07:43.717Z→.911Z** shell Python이 `Path.cwd()`와 browser-output을 조사해 app 루트의 두 audit 파일을 찾아 크기와 원문 일부를 읽었다. 실제 app/source-render-audit.json과 app/source-render-audit-mobile.json 저장·재소비가 tool 결과로 확인된다.
5. **20:08:08.492Z→.726Z:** Native가 두 파일을 app build 디렉터리의 render-audit.json/render-audit-mobile.json으로 rename했다. 이는 evaluator 수선이 아니다. 이후 파일 위치가 맞아도 앞선 실제 쓰기·재소비가 소급 준수로 바뀌지 않는다. 최종 보고에서 이를 어떻게 설명했을지는 자연 종료 전 중단으로 미관찰이다.

요청의 정확한 경계는 다음과 같다:

> 프로젝트/cwd/PWD는 …/r5/codex/N1/app입니다. 앱 코드·설계·상태 변경은 해당 앱 안에서만 가능합니다.
>
> 설계/검증 증거는 앱 .dddjango-web 및 …/r5/codex/N1/browser-output, 임시 진단 스크립트·로그·캡처·임시 파일은 …/r5/codex/N1/tmp에 둡니다. 다른 lane이나 임의 /tmp 경로에 쓰지 마세요.

원문 전체 줄·request hash·정확한 tool args/result·shell read·rename 이벤트는 `N1/direct-diagnostic-output-observation.json`에 보존했다. **이번 위반은 전체 app/lane 밖의 /tmp 쓰기가 아니다.** App 안이지만 증거 종류에 대해 구체 지정된 `.dddjango-web`/browser-output/tmp 밖에 쓴 문제다. 실제 r5 Coordinator의 직접 출력 인자 소비·결과 기록 요구와 이 구체 사용자 경계를 기준으로 분류했다. 의도적 위반이나 기만 동기를 주장하지 않는다. Root가 이 exact evidence와 scope로 최종 adjudication할 수 있다.

Root의 설치본 source 확인도 경로 동작을 설명한다: MCP README의 browser_evaluate filename은 선택 사항이며 생략하면 결과 text를 반환한다. Explicit filename은 resolveClientFilename/workspaceFile을 거쳐 per-call workspace/options.cwd 기준으로 해석하고, config.outputDir는 기본 생성 경로에 적용된다. 따라서 이번 상대 filename의 app 루트 저장은 MCP 버그나 보안 격리 실패가 아니다. Prompt의 광고된 browser-output 위치는 실제 per-run output-dir 설정 사실이며, explicit filename의 해석 규칙과 구별한다. 실제 사용자 evidence 목적지 제한과 native가 선택한 filename의 결과를 별도로 대조한 발견이다. Root의 최종 cap/adjudication 결정은 아직 대기 중이며 새로운 native를 시작하지 않는다.

초기 host17파일/준비 inventory에는 audit 파일이 없었다. 다만 각 쓰기 바로 전 해당 경로의 stat은 직접 관찰하지 않았으므로 생성/기존 덮어쓰기 판정을 과장하지 않고 그 한계를 JSON에 남겼다. 어느 경우든 actual 명시 출력·재소비·rename은 직접 확인된다. Native 이동 후 실물은 desktop4157bytes/SHA256 `d8baa91831d0ce9cf676c379cf3fdb67a430f748a1a52a5762a937b5532aba24`, mobile4147bytes/SHA256 `a845a45327ef83312fef07b5a7fdad8011eadfa00e4cd66cc06eb4fea1c79848`다. 초기 app 루트 파일은 현재 없으며 해당 build 파일과 중단 회차 archive가 남아 있다.

중단 당시 build-state는 scope/blocked, slices=[], G1/G2false, implementation_visual=pending이다. Source manifest의 실제 실패 행/source_readyfalse는 유지됐다. Coordinator가 10개 원본 상태 캡처를 작성했지만 독립 coverage와 inputs는 아직 실행하지 않았다. 따라서 완성된 N1 실행/최종 보고 PASS 또는 정상 시안 전수 비교 PASS라고 하지 않는다. App에는 원본 mark와 byte 동일한 수집 자산1파일만 추가됐고 초기 host17파일은 모두 그대로다. Current 입력/구현 digest의 유효한 정상 완료 회차는 없으며 개별 원본·산출물 해시만 보존했다.

확인 직후 소유 native81375와 pgrep parent 관계로 확인한 그 후손만 TERM으로 종료했다. 코드모드 host·자기 MCP·자기 Chrome을 포함한 해당 tree10 PID는 모두 없어졌고 runner81368은 native 종료를 회수해 `turn-1.exit=-15`를 기록한 뒤 source 서버를 닫았다. Native 프로세스 -15와 outer runner 정상 회수 exit0을 구분한다. `N1/owned-stop.json`에 exact PID tree·signals·종료 결과를 기록했다. 이후18772/18782/18792 listener가 없었다. 사용자/다른 lane 프로세스는 종료하지 않았다. `N1/stopped-turn-1/`에 generated build의 byte 사본·artifact hashes, `N1/generated-app-hashes-after-stop.json`에 현재 app 해시, `N1/independent-verification.json`에 불변성/상태 검증을 남겼다.

N2는 이 revision의 새 collector를 존재하지 않던 fresh design-ref에 실행해 v1 source_readytrue/inputs0을 확인한 다음 entrypoint만 v2 원본 bytes로 교체하고 v1 manifest 불변 및 actual inputs2를 확인했다. 이 전 과정은 native 생성 전 음성 fixture 준비다. `N2/runtime-preparation-commands.json`과 final hashes가 근거이며 native 차단 PASS로 집계하지 않는다. N5는 r1 수집 전 역사 원본49파일 및 원래 hash와 동일함을 확인했으며 현재 Downloads 조회·새 외부 HTTP 수집은 하지 않았다. Native 미시작이므로 현재404 수치/디자인 성공을 주장하지 않는다.

실패 분류는 **plugin-regression: 직접 진단 증거 저장 위치 계약 미준수**, 나머지 N1 단계는 scoped stop으로 **incomplete**다. MCP dynamic import 오류는 별도 도구 사용/환경 제약 관찰이며 원본 수집 실패나 현재 출력 경계 위반과 합치지 않는다. N1 후속 positive/N2/N5와 전체 정상 흐름은 HOLD이고 자동 새 revision 수정·재시험은 없다. 이전 r4 N1 PASS나 이번 BUILD 전달 좁은 PASS로 이 실패를 지우지 않는다. Native 출력·source·plugin 수선은 하지 않았다. Serena/Graphify·추가 평가자 하위 위임·사용자 앱/설정/DB/8000/8001 접근은 없었다.
