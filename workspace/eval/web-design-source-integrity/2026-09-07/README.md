# dddjango-web source integrity — native evaluation

현재 배포 결정: 사용자는 아래 r5 잔여 결함과 미완료 평가를 보고받은 뒤 2026-09-07에 현재 수정본의 배포를 명시적으로 요청했다(“배포해줘”). 이 요청에 따라 `2e4acdb0e664084a9742efd0fd520d2f78beb1a9`를 기반으로 배포를 준비한다. 배포 전 전체 변경 검토에서 추가 발견한 두 검사기 결함은 최소 수정 대상으로 처리한다. 기존 HOLD 기록은 당시 판정으로 보존하며, native FAIL과 미완료를 PASS로 바꾸지 않는다. 이 문서는 배포 전 검토·검사 기록이다. 실제 발행 결과는 [정식 릴리즈](https://github.com/changja88/dddjango/releases/tag/dddjango-web--v1.1.5)를 참조한다.

배포에 남는 한계: Claude r5 N1의 실제 입력 차단은 작동했지만, 같은 실패 원본의 권위 확인만으로 재기준 절차를 진행할 수 있는 것처럼 안내한 Important 결함이 남는다. Codex r5 N1은 지정 증거 저장 위치를 지키지 않았으며 평가 환경 설명에 원인 귀속의 혼선이 있다. 최신 revision의 두 런타임 전체 정상 흐름·구현 전수 비교·미디어 통합은 완료하지 않았다. 과거 정상 표본의 성공을 최신 revision이나 실제 사용자 앱의 시안100% 일치로 확대하지 않는다.

직전 보류 판정(배포 요청 전): 최신 `2e4acdb0e664084a9742efd0fd520d2f78beb1a9`는 전체 검사와 독립 정적 검토를 통과했으나, r5 Claude N1의 최종 다음 행동 안내에서 Important 결함이 독립 검토·root 판정으로 남았다. r5 Codex N1도 지정 증거 저장 위치 미준수로 중단됐고 평가 환경 설명의 원인 귀속 한계를 함께 확인했다. 신규 실행·전체 완료·배포는 HOLD다. 기존 Claude N4는 확정된 선행 보고 게이트 실패로 취소해 미완료로 보존했고, 모든 평가 소유 자원 정리를 마쳤다.

## 대상과 판정 범위

아래 확정된 r1 결과의 대상은 `2988e0f64ebb629184a5b120b3f511d89808c9f2`의 web 플러그인이다. Claude는 현재 checkout의 `--plugin-dir`로 실제 `/dddjango-web:dddjango-web` Coordinator를 실행했다. Codex는 각 독립 앱의 `.agents/skills`에 현재 `codex-dddjango-web/skills` 49개 파일을 byte 동일하게 등록한 뒤 실제 `$dddjango-web` Coordinator를 실행했다. Codex 결과는 로컬 registry 실행 근거이며 marketplace 설치 검증으로 확대하지 않는다.

정상 입력은 이 평가를 위해 작성한 비식별 HTML/CSS/JS/PNG 원본이다. 3개 입력·검토 단계와 완료 화면, 기본·focus·선택·검토·완료의 5개 상태, 두 viewport(1440×900, 390×844), 총 10개 요구 case를 사용했다. 복합·자식 효과와 초기 token pool에 없던 원본 값을 포함하며, 코더 prompt에는 CSS 정답을 나열하지 않았다. 원본 캡처와 별도 평가자 oracle는 구현 전에 동결했다. 실제 춘몽 화면이나 실제 서비스 영상의 성공을 이 정상 표본으로 주장하지 않는다.

실행에 쓴 정상 원본과 요구·비권위 메모는 [fixture](fixture/)에 byte 동일하게 보존했다. [hashes.json](fixture/hashes.json)은 각 파일의 크기와 SHA-256이다. N1은 이 원본의 별도 복사본에서 참조된 `styles/effects.css`만 생성 전에 제외한 입력이다. 별도의 empty Django host를 사용했으며, 구현 결과를 다음 시험의 초기 host로 사용하지 않았다.

각 native Coordinator가 원본 수집·실제 브라우저 관찰·독립 역할 위임·필수 gate를 수행한다. 평가자는 생성된 web 코드, 명세, 상태, manifest, 시각 증거를 손수 고쳐 통과시키지 않는다. 정상 구현 판정은 실제 역할/명령 trace, 요구 case 전수의 독립 원본 대조, 현재 source/implementation digest를 함께 요구한다. JSON pass·프로세스 exit0·이미지 파일 존재만으로 성공을 정하지 않는다.

## r1 실행 결과

| 표본 | Claude | Codex | 해석 |
|---|---|---|---|
| P1 정상 원본 + N3 비권위 축소/생략 메모 | 불합격·중단 | 전체 실행 통과 | r1 Claude는 slice2에서 과거 G0 inputs를 재사용해 실제 HTML 작성·green으로 진행; r1 Codex 성공이 이 실패를 상쇄하지 않음 |
| N1 필수 CSS 누락 | 차단 확인 | 차단 확인 | 실제 수집 실패 이후 ready/시각 구현 없음, 원본·host 유지 |
| N2 기존 ready 상태 + 오염된 동결 bytes | 미실행 | 차단 확인 | 실제 inputs가 크기/hash 불일치로 exit2; 사전 제작 입력과 host 보존 |
| N4 요구 media API 실패 | r1 N4b 미완료·중단 | 미실행 | 실제503과 미검증 요구 유지 관찰은 보존; P1b 회귀로 revision 보완이 필요해 후속 평가 취소, 음성 PASS로 집계하지 않음 |
| N5 실제 Downloads 원본 | 미실행 | 차단 확인 | 수집 실패를 보존; 실제 디자인 구현 성공은 아님 |

Claude의 [r1 최종 native 보고](claude-native-r1.md)와 [입장 위반 증거](claude-r1-admission-defect.json)를 보존했다. Claude P1b는 G0의 inputs 실행(2026-09-06T15:22:32Z)을 약46분 뒤 slice2 호출에서 이번 호출 직전 기록으로 지목했다. CSS가 없어 시각 완성 범위가 아니라는 이유로 새 검사를 생략했고, 코더도 해당 기록 대조/직접 검사 없이 일곱 HTML section을 작성했다. 구조 검사와 slice green/commit까지 진행했으므로 대기 중의 누락이 아니라 실제 계약 위반이다. 평가자는 이를 `plugin-regression`으로 판정하고 slice3 CSS/JS 쓰기 전에 소유 native 실행만 중단했다. 중단 runner의 exit0은 성공을 뜻하지 않는다. 앱·증거를 고쳐 통과시키지 않았으며 원본·플러그인 bytes와 중단 시점 산출물 해시를 보존했다.

P1b는 사용자 작업/증거 경로와 지정 브라우저·서버 조건을 scope/실제 coder 인계에서 빠뜨렸고, 별도 임시 렌더 경로와 브라우저를 사용했다. 이 실행 경계 문제를 입력 게이트 위반과 별도로 기록했다. 임시 stub 기반 구조 캡처는 실제 완성 페이지의 충실도 증거가 아니다.

Codex N1의 실제 freeze는 누락된 `effects.css`로 exit1/source_ready=false를 기록했다. 이후 inputs의 exit2는 최상위 schema/필수 coverage 기록 부족에서 먼저 멈춘 결과다. 이를 checker가 누락 의존성까지 순회했다는 근거로 쓰지 않는다. Claude N1은 독립 coverage 뒤 schema가 맞는 inputs 재검사와 차단 종료를 확인했다.

Codex의 [전체 native 실행 보고](codex-native.md)와 [독립 픽셀 대조 결과](codex-pixel-results.json)를 보존했다. 새 Chrome/context에서 실제 구현10case를 조작·캡처한 결과는 사전 동결 oracle와 decoded pixels 차이가 전부0이었다. 현재 input digest는 `0a669e0efe6bf40464147b094df0f0c942e5121ab311a2ab8584eb370bd7e8a5`, implementation digest는 `3ec9f97af718d559b662399123ea6f10bd698246246b9782328fabe064c8a1d3`이며 native 최종 감수·마무리 gate·추가 전역 검사 뒤에도 동일하다. 이 결과는 위에 명시한 통제 fixture의10case에 한정된다.

현재 inputs 기록 전달도 실제 수신 측 trace로 확인했다. native coder는 `2026-09-06T15:33:39.832Z`에 `visual-check.md`의 `slice-1-screen / coder call 1 / current inputs` 절을 직접 조회했고, 도구 응답에는 현재 build/project 경로를 포함한 실제 명령·exit0·위 input digest가 들어 있었다. 단지 파일이 존재한다는 판정이 아니라 수신 역할의 실제 조회/응답 근거다. 저장된 일부 inter-agent message 인자는 암호화돼 있으므로 그 문자열에서 plaintext dispatch 내용을 추정하지 않았다.

N2는 생성 전에 만든 manifest(2,759 bytes)와 다른 entry bytes(2,837 bytes)를 사용했다. native 재개가 기존 ready 문자열을 신뢰하지 않고 실제 검사로 차단했다. 정상 생성 앱을 나중에 수정하여 반례를 만들지 않았다.

N5는 실제 `사용자 정보.dc.html`(26,918 bytes, SHA-256 `8c3a4467799b7b35845faec037b68ee10cacbd8abb24860fa59ff939f63ba6da`)을 포함한 원본/복사본 49개 파일의 byte 보존을 확인했다. manifest는 31행 중 28행 성공·3행 실패였다. Gowun Batang 직접 폰트 URL 두 개의 HTTP404와, HTTP200 `application/vnd.ms-fontobject`인 Lucide EOT를 현재 수집기가 image 검증에서 거부하는 지원/분류 문제를 구분한다. 실패한 줄을 제거하지 않았으며, 원본 전체가 브라우저에서 렌더 불가능하다는 주장도 하지 않는다.

## 환경과 개입의 한계

- 실제 런타임은 Claude Code 2.1.263 / `claude-opus-5[1m]`, Codex CLI 0.153.4 / `gpt-6-astra`·`xhigh`였다. 준비 시점의 Claude 2.1.261과 혼동하지 않는다.
- 초기 OS sandbox의 Chrome/app-server 실패는 보존했다. 정확한 평가 runner의 outer escalation을 사용하되 Codex child workspace-write는 유지했고, MCP 승인은 해당 lane의 격리 Playwright 도구에만 설정했다. 사용자 설정은 관련 모델/승인 항목을 읽기 전용으로 조회했으며 전역 설정·auth는 변경하지 않았다.
- Claude 최초 정상 실행은 세션 저장 실패로 동일-ID 재개가 불가능했다. 새 독립 host와 같은 동결 입력으로 P1b를 시작했다. 최초 실패를 성공 표본에 합치지 않는다.
- Codex capacity 중단과 native 재개를 기록했다. CLI 요약의 빈 receiver는 실제 역할 부재를 뜻하지 않았다. raw rollout에서 spawn·중단 상태·followup·running을 확인했으며, 불완전한 요약을 근거로 보낸 최소 queue steering도 정정·보존했다. 역할 판정·구현 정답을 평가자가 공급하지 않았다.
- 초기 Claude N4에는 평가자의 포트 경계 전달 누락과 native의 lane 밖 로그 쓰기가 섞였다. 해당 native와 그 소유 서버만 중단했고 표본을 무효/미완료로 남겼다. N4b는 새 host·동일 요구/원본, 고유 loopback 포트·닫힌 쓰기 경계로 다시 동결했다.
- r1 Claude N4b는 실제503과 두 필수 media case를 유지하고 샘플 대체를 하지 않았다. Z1 미결과 G1승인 상태의 병존도 기록했으나, 사전 단계 승인과 미결 항목 미적용 조항을 대조한 결과 그 상태만으로 새 회귀를 확정하지 않았다. P1b의 확정 회귀로 같은 revision을 보완·재평가해야 하므로 남은 N4b는 `incomplete/cancelled-for-upstream-plugin-revision`으로 중단했다. 이를 timeout 실패나 media 차단 PASS로 부르지 않으며 r2의 새 전체 N4 실행이 필요하다.
- Codex의 복구용 Git commit은 `.git/index.lock` 쓰기 제한으로 실패했다. 구현 이전과 내용이 같은 초기 host HEAD를 비교 기준으로 보존했고 결과는 미커밋으로 남겼다. evaluator가 대신 커밋하지 않았다. backstop은 diff와 함께 untracked 파일도 검사하며, 실제 새 코드10개가 검사 touched/added에 전부 포함됨을 확인했다. 정규 호출은 원래부터26종 모두 검사했고, `--all` 추가 실행은 변경 범위를 푼 별도 전역 검사다.

큰 원본·PNG·raw CLI/role trace·실행 argv와 개별 hash는 비공개 task temp에 보존한다. 이 문서는 비밀 없는 판정 요약이며 내부 reasoning이나 인증 정보를 포함하지 않는다. 실제 사용자 앱·DB·활성 포트 8000/8001은 이번 평가에서 접근하거나 변경하지 않았다.

## r2 보완과 새 실행

보완 revision은 `d90aa90192be686de0a7ec6b0be1225637f927f4`다. 모든 시안 coder 호출에 현재 caller inputs와 코더의 첫 파일 변경 전 직접 inputs 실행을 적용했다. 실제 호출에 조건·대상·Python/checker·현재 기록을 전달하고, 코더 반환의 누락/실패/불일치/입장 위반을 green 차단으로 연결한다. 사용자 실행 경계도 scope와 네 역할의 실제 인계에 보존한다. Coordinator의 역할 반환 확인과 평가자의 실제 child tool 순서 독립 확인을 구분한다.

수정 직후 전체 `make verify`는6/6 green(200초), 독립 scoped review는 spec/quality 모두PASS다. 이것은 문서 실행 계약의 구현 정합 근거이며 실제 행동 성공은 아직 주장하지 않는다.

동일 input-v2·원래 oracle-v2·새 빈 host·새 세션으로 최소 native 행렬을 다시 실행한다. Claude는N1 이후 독립 포트의P1+N3/N4, Codex는P1+N3/N1/N2/N5다. 각각 실제 current caller inputs→callee 기록 읽기/자기 inputs→첫 mutation 순서와 요청→scope→실제 dispatch→실행 경계를 추가 대조한다. r1 생성 앱이나 성공 판정을 새 revision에 재사용하지 않는다.

r2 Codex 최초 P1은 채점에서 제외한 제한 표본으로 보존한다. 실행 경계 wrapper가 scope 전사·역할 dispatch 인계라는 검증 대상 절차를 직접 안내한 것을 root가 발견했다. 이 문구가 없는 새 P1b와 아직 시작하지 않은 음성 요청을 생성 전에 다시 동결하며 실제 경로/포트/도구 제약은 유지한다. caller/callee 검사 순서 답안은 최초 요청에도 없었다. Claude 요청에는 해당 절차 안내가 없음을 확인했다. 최초 Codex에는 긴 lane TMPDIR가 Playwright socket 길이 제한을 넘는 환경 오류도 있었다. 설치된 코드의 상대 socket 경로 지원을 확인해 같은 lane 안의 per-run 설정으로 복구하며, 오류·변경 근거·새 브라우저 preflight를 보존한다. 이 시도는 플러그인 통과/실패로 집계하지 않는다.

r2 Claude N1은 실제 입력 차단과 최종 보고를 나눠 판정했다. 누락 CSS/HTTP404/source_ready=false/inputs exit2를 유지하고 coder를 호출하지 않은 실행 차단은 성공했다. 그러나 최종 답변에서 같은 실패 원본을 유지한 채 구현하는 “승인된 예외”를 권장하고, 실패 상태의 렌더와 평가 준비 metadata를 근거로 비교 기준이 완전하다고 확대했다. 이 보고는 현행 G0 승인으로 필수 입력 조건을 면제할 수 있다는 잘못된 진행 경로이며, 실제 우회 구현이 발생한 것으로 확대하지 않는다. 이 관찰의 [실제 최종 답변 발췌와 판정](claude-r2-report-defect.json)을 보존했다. 해당 예외 승인은 하지 않았으며, 독립 제안 검토 후 Task2 fix round3를 구현했다.

사용량 제한으로 평가 담당 세션이 중단된 후 사용자가 재개를 요청했다. 복구 시 Claude N4는 기존 native/서버가 계속 실행 중이었고 plugin/source/requirements hash도 일치했다. Codex P1b는 실제 CLI가 사용량 제한(exit1)으로 종료해 같은 thread로 재개한다. 첫 style coder의 현재 기록 읽기→직접 inputs exit0→첫 파일 변경 순서는 실제 tool trace로 확인했지만, 이는 해당 호출의 좁은 통과일 뿐 전체 구현·최종 시각 판정은 아니다. 중단 원문과 복구 절차는 각 lane의 비공개 증거에 보존하며 이전 실행을 새 성공 표본으로 합치지 않는다.

r2 Codex P1b+N3은 전체 native 완료와 추가 전역 검사까지 **PASS**로 종료했다. [r2 실제 실행 보고](codex-native-r2.md)와 [10case 픽셀·현재 해시 결과](codex-r2-pixel-results.json)를 보존한다. 스타일 및 재개 페이지의 실제 코더 호출에서 현재 기록 읽기→자체 inputs0→첫 변경 순서, 독립 최종 감사, 현재 visual/backstop/Django 검사, 10case pixel diff0을 확인했다. quota 중단 후 동일 thread로 재개했으며, 추가 native 전역 검사 전후152파일도 변하지 않았다. 이 결과는 `d90aa90`의 통제 정상 표본이며 `df3f512`의 최신 전체 실행으로 바꾸어 부르지 않는다. r2 N1/N2/N5는 미시작으로 남기고 r3에서 새 registry로 수행한다.

## r3 수정 상태

`df3f512cb4703db58f987b913d06736f468ce6d3`은 입력 차단 뒤의 보고·다음 행동과 명시적 재기준 조건을 네 runtime/reference 파일에 연결한다. 실제 차단 성공은 그대로 두고, 같은 실패 입력의 승인 예외 구현 권장을 배제하며 구체적인 원본 복구/출처 변경 후 새 수집·관찰·독립 검토·inputs0 경로를 보존한다. 별도 임시 linked worktree에서 수정해 실행 중인 r2 Claude가 읽는 `d90aa90` 파일은 변경하지 않았다.

제안의 독립 spec/quality 검토는 PASS였고, 구현 후 `make verify`는6/6 green(207초), web9fixturefiles0fail 및 reference byte mirror/diff 검사는 통과했다. 구현의 독립 재검토는 spec/quality PASS였지만 실제 r3 Claude N1에서 다음 행동 안내가 다시 실패했다. 정적 검토 통과를 행동 성공으로 바꾸어 보고하지 않는다. r2 결과와 r3 결과는 대상 revision을 분리한다.

## r2/r3 최종 실패와 round4 재개

[r2 Claude 최종 보고](claude-native-r2.md)는 N1의 실제 차단과 잘못된 예외 구현 권장을 나누고, N4를 **실행 경계 실패**로 확정했다. 두 coder 호출의 현재 inputs 입장 순서는 맞았지만, 두 번째 코더는 코드 목록 밖 파일 생성 금지라는 실제 dispatch를 받은 뒤 `/tmp/root_out.txt`에500 응답을 저장하고 다시 읽었다. 반환은 이를 누락하고 목록 밖 파일이 없다고 보고했으며 Coordinator는 프로젝트 내부 check/git/CSS 검사 후 slice를 커밋했다. 실제 경계 위반을 검출하지 못한 결과이며, Coordinator가 child trace를 보고도 무시했다거나 코더가 악의적으로 숨겼다고 추정하지 않는다. [비밀 없는 실제 사건 요약](claude-r2-boundary-defect.json)을 보존했다. media503과 필수 영상 요구는 유지됐고 샘플 대체는 관찰되지 않았으나, 전체 media/시각 감사/최종 gate는 미완료다.

[r3 Claude 최종 보고](claude-native-r3.md)와 [최종 답변·판정](claude-r3-report-defect.json)의 N1은 **실제 차단 PASS / 진행 선택지 FAIL**이다. inputs2·source_readyfalse·blocked·미구현을 유지했으나 reviewer가 같은 실패 원본의 승인 경로를 권고했고 Coordinator가 승인 기록→재검사→Phase1 선택지로 채택했다. r2처럼 실패 상태에서 구현하겠다는 명시 약속은 없으므로 실행 불가능한 진행 선택지로 좁혀 판정한다. 새 source 복구나 재기준 positive, 별도 정상P1은 시작하지 않았다. 원본10case 관찰은 누락 효과가 있는 원본의 관찰이며 실제 구현 성공이 아니다.

[r3 Codex 최종 보고](codex-native-r3.md)의 N1은 **입력 차단·최종 보고 PASS**다. actual freeze가 누락CSS로 실패했고 inputs2·blocked·미구현을 유지하면서 실제 누락 파일과 브라우저 문제 해결을 다음 행동으로 보고했다. 다만 native 원본 렌더는0/10이다. 등록 MCP의 격리 preflight는 성공했지만 native는 별도 shell MCP/Chrome을 시도해 OS sandbox에서 실패했고 browser `--no-sandbox` 옵션 재시도도 실패했다. 이를 전체 실행 경계 PASS나 렌더 성공으로 포함하지 않는다. Codex child workspace-write/전역 설정은 변경되지 않았고, 후속 positive/N2/N5는 HOLD·미시작이다.

N5의 원래 Downloads 경로는 새 준비 시점에 접근되지 않았다. 제한된 NFC 이름/정확한 파일 검색도 결과가 없어, 원인을 추정하거나 광범위 검색하지 않았다. 새 시험은 당시 생성 전 보존한 실제 원본49파일을 기존 해시와 대조한 스냅샷으로 준비한다. 현재 Downloads 접근이나 최신 디자인 동일성을 주장하지 않으며 외부HTTP도 새 실제 응답으로 기록해야 한다.

r4 실행 전 요청문 감사에서 Claude 초안이 과거 wrapper의 역할 호출·gate 수행·풀 밖 값 등록 절차를 그대로 포함한 것을 확인했다. 아직 생성 전이므로 초안과 해시를 revision1으로 보존하고, 원본·요구·작업 경계·통상 단계 승인만 남긴 새 요청으로 준비한다. 과거 Claude 결과의 prompt는 그대로 보존하며 절차를 전혀 안내하지 않은 표본이라고 주장하지 않는다. 원본/요구10case나 생성 output을 바꾸는 작업은 아니다.

Task2 round4는 Coordinator·입력범위 reviewer·coder·implementation-ui 및 Codex 미러 네 쌍을 대상으로 독립 제안 검토 spec/quality PASS를 받았다. 현재 입력의 관찰 판정과 실행 가능한 입력 해소 선택지의 소유권을 나누고, 진단 출력 방식을 실제 coder dispatch→명령→반환→Coordinator 대조에 연결한다. 런타임 sandbox나 새 권한 체계를 추가하지 않으며 임의 도구 쓰기를 prose만으로 예외 없이 차단한다고 주장하지 않는다. 구현 `981fad57cc9702bb1e550f0389351bf5ddb88874`는8파일28추가24삭제이며 최종 `make verify`6/6 green(202초, web9fixturefiles/217건/실패0), 독립 구현 spec/quality PASS다. 정적 발견5행을 해소했고 중요한 새 수정 결함은 없었으나 행동 통과는 아직 미판정이다. 원래 리뷰어 재개와 새 리뷰어 생성이 agent thread limit으로 거절돼, 이 수정에 참여하지 않은 기존 Codex 평가자가 한정 정적 리뷰를 맡았다. 그 후 평가 역할로 돌아가며 생성 output이나 준비 앱을 고치지 않았다.

모든 이전 평가 소유 native/MCP/Chrome/서버는 종료·포트 폐쇄 근거를 보존했다. 확인된 외부 임시 응답은 private copy SHA와 고유 앱 내용을 대조한 뒤 해당 현재 파일만 삭제했다. 그 경로의 실행 전 존재 여부·이전 bytes는 관찰하지 못했으므로 복구를 주장하지 않는다. Django debugHTML 원문은 비공개 temp에만 두고 공개 결과에 포함하지 않는다.

## r4 실제 실행 배정

새 정확 revision `981fad5`와 새 empty host·원래 source bytes로 두 런타임 N1을 수행한다. N1의 실제 차단과 최종 안내가 모두 통과한 뒤에만 별도의 정상 HTML 원본을 새 기준으로 명시 제공한다. Codex는 이 재기준 전체흐름에서 네 역할·전체10case·최종 감사/gate·독립 화면 대조를 마친다. 정확한 표본명은 **r4 Codex explicit-rebase full normal flow**다. Claude는 재기준 첫 coder 입장 전환을 확인하고 별도 freshP1+N3 전체를 수행한다. 새 ClaudeN4와 CodexN2/N5도 이 revision으로 시행한다. 과거 FAIL/incomplete는 어떤 최신 PASS도 대신하지 않는다.

독립 exact-diff 검토에 따라 원본 수집/coverage에서 정직하게 멈춘 N1은 inputs를 아직 실행하지 않았을 수 있다. 실제 CLI가 실행될 때만 exit2와 해당 명령·출력을 인용하고, 미실행은 그대로 기록한다. 필수 기준은 ready/coder 진입 전 current inputs0이며 정상 진행에서 이를 생략하지 않는다. B의 진단 출력 방식·실제 쓰기/재소비·반환·Coordinator 통합은 실제 실행된 호출에서 대조해야 한다. 진단이 없으면 미관찰이며, 한 출력 방식의 성공을 다른 방식의 증거로 쓰지 않는다. image-only/no-design·실패한 새 입력의 모든 분기까지 이번 HTML 재기준의 실제 실행으로 확대하지 않는다.

## r4 실제 관찰과 round5 제안

r4 Claude N1은 source 수집과 별도로 **Coordinator 직접 실행 경계 FAIL**이다. G0에서 build 폴더를 만들면서 경계 밖 `/tmp/n1_build_path.txt`에 경로를 썼고 다음 호출에서 다시 읽어 freeze의 출력 경로로 사용했다. [실제 안전한 tool 사건과 실물 해시](claude-r4-coordinator-boundary-defect.json)를 보존했다. 기존 coder의 진단 명령·반환 경로가 재실패했다고 바꾸어 부르지 않는다. collector는 실제 CSS404/source_readyfalse를 정직하게 기록했으나 inputs/독립 coverage/자연 최종 보고/coder 전 단계에서 위반 실행을 중단했으므로 그 나머지는 미완료다. 종료143은 source/report 판정이 아니다.

현재 파일은 private copy SHA 및 고유 build 경로와 대조한 뒤 그 출력만 삭제했고, N1 소유 native·후손·서버와18771/18781을 정리했다. 실행 전 파일의 존재/이전 bytes는 관찰되지 않아 새 생성인지 덮어쓰기인지와 이전 내용 복구를 주장하지 않는다. [r4 Claude 최종 보고](claude-native-r4.md)의 별도 N4는 자연 종료했고 실제 API503·identity/src 부재·영상 미검증을 유지한 좁은 실패 처리 PASS다. source10case는 독립 oracle와 픽셀/치수가 일치했고 source_readytrue/현재 inputs0을 확인했으나, 원본에 없는 영상의 배치 결정·독립 coverage 통과가 남아 scope/blocked를 유지했다. layout 결정이 있어도 API 실패가 영상 검증 통과가 되지 않는다고 보고했다. 코더 호출이 없어 진단B는 미관찰이며 전체 구현/최종 시각 감사는 미실행이다. 모든 소유 실행과5포트가 닫혔으며 이 결과를 r5로 재표기하지 않는다. [r4 Codex N1](codex-native-r4.md)은 실제 inputs2·blocked·미구현을 유지해 자연 종료했고 실행 차단·최종 보고 모두 PASS다. registered MCP 원본10case 및 독립 reviewer 실제 재관찰, source/registry49/host17 bytes 보존과 소유 실행·포트 종료를 확인했다. coder가 없어 B는 미관찰이며 후속 positive/N2/N5는 새 revision 판단 전 HOLD다.

독립 관찰 분류 뒤 round5는 Coordinator 자기 준비/수집/진단과 호출 간 값 전달의 실제 명령 소비 지점을 최소 보완하는 제안·독립 검토 PASS를 거쳐 별도 `checkout-r5`에서 **4파일 구현 단계**다. 기존 agent thread 한계 때문에 새 read-only·ephemeral Codex CLI 문맥으로 제안을 받으며, 첫 app-server 초기화 EPERM과 동일 driver의 scoped outer 재실행을 보존했다. child read-only와 전역 설정 무변경을 유지한다. 제안/독립 검토/구현/실제 행동 gate를 통과하기 전 배포하지 않는다.

## 남은 완료 조건

수정 revision으로 정상 두 런타임의 새 전체 실행과 실제 구현 전수 비교, 새 revision의 N4 실제 실패 처리 및 음성 평가, 독립 whole-branch review, 최종 `make verify` 및 strict plugin validate, `make release-web` 배포와 원격 검증이 남아 있다. r1 Codex의 기존 PASS를 수정 runtime 지침의 새 실행으로 대체 표기하지 않는다. 완료 후 이 절과 결과 표를 최종 판정으로 갱신한다.

Serena/Graphify: plugin checkout 및 독립 평가 앱에 opt-in 표식이 없어 사용하지 않았다.


## r5 실제 실행 진행 중

`2e4acdb0`은 Coordinator 자신의 첫 준비·진단 명령에 현재 요청의 실행 경계를 소비하도록 연결한다. 선택한 절대 BUILD는 일반 도구 결과에서 받아 후속 명령의 인자로 전달하고 기존 scope/build-state로 재개한다. 직접 진단의 출력 선택·실제 쓰기와 재소비·결과 기록도 같은 소유자에게 연결했다. 네 runtime/reference 파일만 수정했으며 기존 coder 입장/출력 계약과 원본·증거 저장은 유지했다.

독립 제안·구현 검토는 각각 Spec/Quality PASS다. 구현 owner의 첫 전체 검사는 기존 HTTP fixture의 loopback bind가 child sandbox에서 EPERM으로 막혀 exit2였다. 이 실패를 보존하고 동일한 네 파일 hash로 controller가 승인된 outer 환경에서 전체 검사를 재실행해6/6 green·exit0·206.2초를 확인했다. Controller는 코드를 고치지 않고 해당 네 파일만 커밋했다. 이는 정적 검증 근거이며 native 행동 성공은 아니다.

r5는 두 런타임의 새 N1 자연 차단/최종 보고 뒤 명시적 새 원본 재기준을 확인한다. Codex는 그 재기준에서 전체 정상 흐름을 끝까지, Claude는 첫 current coder 입장 checkpoint 뒤 별도 fresh P1을 끝까지 수행한다. Claude 새 N4 및 Codex 새 N2/역사 원본 N5도 기존 행렬대로 평가한다. Coordinator 자신의 준비 경로와 coder 실제 진단/반환/통합은 별개 관찰 축이다. 아직 실행되지 않은 분기와 미완료 전체 흐름을 통과로 집계하지 않는다.


## r5 현재 실패와 보류 판정

[Codex r5 보고](codex-native-r5.md)와 [실제 출력 사건](codex-r5-diagnostic-output-defect.json)을 보존했다. 절대 BUILD 전달은 해당 호출에서 맞았지만, MCP explicit filename 두 개가 app 루트에 저장됐고 native가 이를 읽어 build로 이동했다. app/lane 밖 쓰기나 MCP 버그는 아니다. 독립 관찰 검토는 지정 증거 위치 FAIL을 유지하되, 평가 요청의 무조건적인 출력 위치 설명이 실제 --output-dir 기본 경로보다 넓어 plugin 단독 원인 귀속을 제한한다고 판정했다. 정확한 설정 사실로 설명을 좁힌 fresh sample은 가능한 후속 검증이지만 아직 승인·실행하지 않았다.

[Claude r5 N1 최종 안내·상태](claude-r5-report-defect.json)는 실제 source_readyfalse/collector1/inputs2/blocked 및 구현 미진입을 유지한다. 그러나 최종 선택지ⓑ는 같은 서빙본의 권위·효과/focus 범위 확인만으로 재동결→검토→inputs0→Phase1 경로를 제시했다. 실제 새 수집 가능한 HTML·이미지·entrypoint 또는 제공받을 자료가 없고 같은404 import가 남는다. 독립 검토와 root는 최종 다음 행동 유효성 Important FAIL을 확정했다. inputs0은 여전히 미래 진입 조건이므로 실제 검사 우회나 무조건 Phase1 진입으로 확대하지 않는다.

수정 round5 상한에서 이 결함은 필수 N1 report→새 기준 pair 평가의 선행 조건으로 남았다. 같은 산문 수정의6차 반복이나 과거 성공의 재사용으로 현재 완료를 만들지 않는다. 실패 후 안내/제어 흐름에 대한 새 설계 근거 없이 추가 구현이나 배포로 넘어가지 않는다. 현재 코드·기존 실패·미완료 평가와 검토 기록을 보존하며 final whole-branch review와 release는 수행하지 않았다.


[Claude r5 최종 평가 기록](claude-native-r5.md)은 N1 실제 차단 PASS / 최종 안내 Important FAIL과 N4의 선행 실패에 따른 취소를 확정한다. N4에서 실제 API503, 원본10case 픽셀 일치, 추가 상태 audit10개 및 현재 inputs0/digest `88a564a1c121cd277bb8f7b5e7747afe5361a4f6bb5989659646d318e3daa2b9`는 관찰했으나 독립 재검토·최종 안내·코더·구현은 완료하지 않았다. 이를 최신 미디어 차단 PASS나 구현100% 일치로 보고하지 않는다.

정리 후 root가 직접 지정8개 포트의 listener 부재, 변경 없는2e4acdb HEAD/검증된 네 파일 bytes, primary147a59a8 및 기존 WIP571파일의 동일 hash를 확인했다. Plugin source·review·실패 증거와 SDD 원장은 재개 가능하도록 그대로 보존했다. main 병합·버전 변경·make release-web·원격 배포·설치 cache 변경은 실행하지 않았다.


## 배포 전 전체 변경 검토

현재 수정본 배포 요청에 따라 독립된 새 읽기 전용 검토자가 기준147a59a8부터2e4acdb까지34파일을 검토했다. [전체 변경 검토](final-whole-branch-review.md)는 Critical0, 새로운 Important2로 수정 후 병합을 요구했다. 다른 case의 원본 파일/하드링크 재사용이 시각 검사에서 통과하는 문제와 중첩 JSX의 실제 HTML 기준 경로를 잘못 해석하는 문제다. 기존 r5 안내/저장 위치 결함의 재분류가 아니며, 배포 단계 안에서 이 두 검사기 결함만 최소 수정하고 독립 재검토한다. 원본 평가의 실패·미완료 판정과 Task2 수정 상한은 그대로 유지한다.

수정 전 [필수 검사](release-preflight-verification.json)는2e4acdb에서6/6 green·exit0·209.8초이고 검사 중 source bytes는 동일했다. 새 검사기 수정 후에는 그 최종 bytes로 전체 검사를 새로 실행해야 하며, 이 결과를 새 수정의 검증으로 재사용하지 않는다.


검사기 첫 보완의 [독립 재검토](release-checker-round4-review.md)는 case 간 원본 재사용 수정은 수용했으나, HTML에 도달한 뒤 상위 importer 경로 검증이 끝나는 문제를 Important로 남겼다. [전체 검사6/6·exit0·214.9초](release-checker-verification.json)는 이 보완의 정확한 bytes에 대한 결과이며 재검토 실패를 지우지 않는다. Task1 마지막 수정 회차는 문서 기준으로 쓸 가장 가까운 HTML을 보존하면서, 실제로 소비하는 importer 체인을 entrypoint까지 검사하는 최소 보완으로 한정한다. 전체 미사용 metadata의 진위를 증명하는 범용 검증으로 확대하지 않는다.


## 최종 검사기 보완과 릴리즈 근거

최종 보완은 기존 두 검사기/테스트와 Codex byte 미러, 총4파일에 한정됐다. 모든 implementation 캡처를 모든 원본 파일·하드링크와 비교하고, 중첩 component의 실제 문서 기준을 유지하며 소비하는 importer 경로를 entrypoint까지 검사한다. 가장 가까운 HTML을 보존하므로 중첩 HTML·정상 source dependency cycle·독립된 같은 이미지 bytes는 허용한다. HTML을 경유하는 누락·순환 경로는 거절하며 manifest 형식과 수집기·runtime 산문은 변경하지 않았다.

추가 회귀는 변경 전 실제로 실패했고, 최종 canonical/Codex 검사기 테스트가 각각21개 모두 통과했다. [최종 독립 재검토](release-checker-final-review.md)는 Spec/Quality PASS, Technical ReadyToMerge yes, Critical0/Important0이며 원래 두 발견과 추가 HTML 상위 경로 발견을 모두 해소했다고 판정했다. 독립 검토의 읽기 전용 메모리 내 검사와 구현자의 실제 파일/CLI 검사는 서로 구분한다.

[최종 make verify](release-checker-final-verification.json)는6/6 green·exit0·211.8초이며, 실행 전후 모든 runtime bytes가 동일했다. 해당 기록의 base HEAD와 uncommitted diff SHA256, 네 파일 hash가 커밋 전 실제 검사 대상을 식별한다. 이후에는 이 bytes를 기계적으로 커밋해 main에 fast-forward하고, make release-web의 strict plugin validate·필수 재검사·버전/태그·GitHub Release 절차로 발행한다. 실제 발행 결과는 상단 공식 릴리즈 링크를 참조한다.

이 최종 보완 뒤 새 native 실행은 수행하지 않았다. 2e4acdb의 Claude 최종 안내 FAIL, Codex 출력 위치 FAIL/원인 귀속 한계와 최신 전체 native/미디어 미완료는 해소되거나 재검증된 것으로 표시하지 않는다. 사용자 앱의 화면이나 설치 캐시를 자동 수정한 릴리즈가 아니다. 기존 실패와 원본 SDD/실행 증거는 보존한다.
