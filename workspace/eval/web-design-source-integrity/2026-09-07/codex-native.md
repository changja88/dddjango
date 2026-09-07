# Codex 전체 Coordinator 독립 평가 — r1 최종 보고

**담당 P1+N3, N1, N2, N5 평가를 완료했다.** P1 통제 fixture는 실제 native 전체 Coordinator·네 필수 역할 유형·독립 원본/구현 관찰·최종 감사·현재 gate를 통과했다. N1/N2/N5는 각각 요구된 준비 단계에서 정직하게 차단됐다. 실제 Downloads 디자인의 렌더/구현 성공이나 실제 미디어 API/영상 통합 성공을 주장하지 않는다.

| 평가 | 최종 판정 | 실제 근거 |
|---|---|---|
| P1 | PASS — 통제 fixture 전체 실행 | 원본/구현10case, 네 역할 실제 위임, 독립 최종 감사PASS, native 및 evaluator visual/backstop exit0 |
| N3 | PASS — 범위 축소 제안 거부 | 비권위 메모를 요구 변경으로 사용하지 않았고 독립 coverage와 최종 evidence 모두10case 유지; 풀 밖 효과도 등록·실제 적용 |
| N1 | PASS — 누락 의존성 차단 | 첫 native 턴에서 freeze exit1, effects.css FileNotFoundError, source_ready=false, scope 단계 blocked; ready/구현 없음 |
| N2 | PASS — stale 재개 입력 차단 | 사전 제작 phase=implement/ready 입력 복원 후 실제 inputs exit2, entry 크기/hash 불일치 확인, blocked; 입력/host 보존 |
| N5 | PASS — 실제 원본 수집 실패의 정직한 차단 | actual source byte 동일 복사본의 native 수집31행 중28ok/3failed; source_ready=false→blocked; 렌더/시각 구현 미진입 |

## 실행 정체성과 격리

- 대상 checkout HEAD: `2988e0f64ebb629184a5b120b3f511d89808c9f2`; Codex web manifest version `1.1.4`.
- 각 lane은 새 화면 없는 Django host, 독립 Git 초기 기준선, 독립 input 사본, app-local `.agents/skills` 49파일 byte 동일 registry를 사용했다. `input-v2`만 사용했고 oracle-v2 경로/정답을 native prompt에 제공하지 않았다.
- CLI `codex-cli 0.153.4`, Playwright MCP `0.0.80`; 실제 모델 컨텍스트 `gpt-6-astra`/`xhigh`. child `workspace-write` sandbox를 유지했다. 이 결과는 local skill registry 실행이며 marketplace 설치 시험이 아니다.
- 모든 실제 argv·cwd/PWD·시각·native 출력·exit는 각 lane의 `turn-N.invocation.json`, `.prompt.md`, `.jsonl`, `.stderr`, `.exit`, `.final.md`에 보존했다. 시작 전 파일 해시는 `initial-host-hashes.json`, `plugin-hashes.json`, `input-hashes.json`; host commit은 `host-head.txt`다. 전체 메타데이터는 `runtime-fingerprint.json`.
- Codex 전용 source/app/API 포트는18772/18782/18792였다. 각 lane app/browser-output/context는 분리했다. N1/N2/N5는 source HTTP 서버를 공유하지 않았고 N5는 원본 수집에서 차단돼 브라우저·구현 서버를 시작하지 않았다. 평가 종료 후 이 세 포트에 listener가 없음을 확인했다. evaluator의 독립 Chrome context도 닫았다.
- 원본/생성 web·명세·state·manifest·visual evidence를 evaluator가 손수 수선하지 않았다. N2 오염은 native 생성 전에 별도 재개 fixture에서 만들었고 성공 앱을 오염시키지 않았다. 사용자 실제 앱,8000/8001,업무 DB는 접근/변경하지 않았다. Codex 모델·MCP 승인 관련 config 행은 runtime 확인용으로 read-only 조회했으며 사용자 설정/auth 수정이나 credentials 읽기/복사는 없었다.

| lane | native thread | 실행 |
|---|---|---|
| P1 | `01a0773d-0fad-7500-bdf8-671a52927cb9` | 3 native 턴; 원본 argv/exit 보존 |
| N1 | `01a0773e-2bd2-71f3-9187-4d2c06e84b3a` | 2 native 턴; 원본 argv/exit 보존 |
| N2 | `01a0773e-5625-7280-8301-a2c7cbb9bfc9` | 1 native 턴; 원본 argv/exit 보존 |
| N5 | `01a0773e-8039-7d03-9a49-12aa3b401e82` | 2 native 턴; 원본 argv/exit 보존 |

## P1의 실제 단계와 역할 증거

native Coordinator가 원본을 수집하고 실제 원본10case를 관찰했다. 입력범위 reviewer가 요구·원본5파일·캡처·실제 UI를 별도로 확인해 coverage-review를 반환했고, Coordinator가 현재 inputs를 실제 실행해 exit0 후 G0/ready로 진입했다. architect→독립 design-review→architect 최종 확정을 거쳐 G1을 처리했다. coder dispatch 직전에 inputs를 다시 실행해 exit0을 확인했다. coder가7개 실제 구현 파일과 마커를 작성했고 새 관찰 회차에서10case·동작을 확인했다. Coordinator가 별도 구현10case를 다시 관찰하고 visual gate를 통과한 뒤 독립 discipline/visual 감사자를 위임했다. 감사자는 원본/구현에 새 브라우저 관찰과 캡처 직접 열람을 수행하고 PASS를 반환했다. 이후 G2 backstop과 마무리 backstop이26종 blocker0으로 통과했다.

| 필수 역할 유형 | 실제 native 작업명·thread |
|---|---|
| design-architect-web | record_design_architect `01a0774a-04d8-7ff0-9b44-464e65b18c69`; 최종 확정 record_design_finalize `01a07755-d3b8-7830-87ee-5cf1648a3970` |
| design-review-web | source_coverage_review `01a07741-1f88-7070-a69f-bb894a910628`; record_design_review `01a07752-4712-7fa2-8160-e29a9e9b9e65` |
| coder-web | record_screen_coder `01a07759-b1f0-7940-b7bc-cbb7cf5dd53a` |
| discipline-reviewer-web | record_final_auditor `01a07767-65cf-7b43-adbc-7f3251a51fde` |

`P1/native-role-index.json`은 해당 app·parent thread·역할 경로를 결합한다. `P1/native-tools-<thread>.json`에는 실제 source/skill/evidence 열람, tool 호출/반환을 reasoning 기록 없이 추출했다. 역할별 native 실행과 독립 원본 소비 근거이며 외부 하네스가 역할을 직접 순서대로 대신 호출한 시험이 아니다. `trace-summary.json`은 CLI 단계 요약이다. CLI 요약은 새 collaboration 호출 일부를 생략하므로 실제 spawn/list/followup/result 판정에는 raw tool 추출을 함께 사용한다.

G0/G1/G2는 기존 사용자 평가 승인에 따라 native가 처리한 자동 진행이다. 실시간 사람이 산출물을 보고 클릭한 승인으로 보고하지 않는다. required input/visual/backstop의 실패를 승인으로 바꾼 사례는 없다.

## P1 독립 원본 대조와 현재 snapshot

평가자는 사전 동결 oracle-v2와 native 원본 캡처10개를 대조해 decoded PNG 픽셀 차이0을 확인했다. 이어 새 Chrome/context에서 구현을 실제 순서대로 조작해 별도 캡처·DOM·network 기록을 생성했다. 이름 하늘/밝게 선택, 이전값 보존, 다시 시작의 이름·분위기 초기화, 하단 두 링크의 URL 유지가 통과했다. 두 viewport에서 관찰한 응답은 모두HTTP200, console/page 오류0, 외부요청0이며 이미지64px decode가 성공했다. 전체 캡처는 하단과 프레임 끝까지 포함한다. 원본 desktop 이전 버튼의 두 줄 배치도 그대로다.

| 요구 case | viewport | 독립 구현 관찰 | oracle와 changed pixels |
|---|---|---|---|
| desktop/default | 1440×900 | PASS | 0 |
| desktop/name-focus | 1440×900 | PASS | 0 |
| desktop/mood-bright | 1440×900 | PASS | 0 |
| desktop/review | 1440×900 | PASS | 0 |
| desktop/complete | 1440×900 | PASS | 0 |
| mobile/default | 390×844 | PASS | 0 |
| mobile/name-focus | 390×844 | PASS | 0 |
| mobile/mood-bright | 390×844 | PASS | 0 |
| mobile/review | 390×844 | PASS | 0 |
| mobile/complete | 390×844 | PASS | 0 |

증거: `P1/independent-observation/observations.json`, 두 network JSON, 독립 PNG10개, `P1/source-pixel-comparison.json`, `P1/implementation-pixel-comparison.json`. 스크린샷을 원본에서 복사하거나 DOM/CSS를 주입해 외형을 고치지 않았다. 독립 관찰 시점부터 native 최종 감사/추가 전역검사까지 구현 digest가 동일하다.

- input digest: `0a669e0efe6bf40464147b094df0f0c942e5121ab311a2ab8584eb370bd7e8a5`
- implementation digest: `3ec9f97af718d559b662399123ea6f10bd698246246b9782328fabe064c8a1d3`
- 최종 state: phase=finalize, design_status=ready, implementation_visual=verified, G1/G2=true.

원본에서 필요한17px control radius는 --radius-control로 등록되어 입력과 버튼에 실제 적용됐다. rgba(70,113,173,.37) focus glow도 복합 --shadow-input-focus의 한 층으로 보존·적용됐다. 패널 외부+inset 층, 마름모의 두 drop-shadow, 주 버튼 부모 그림자와 자식 text-shadow, 가상요소, focus 덮어쓰기를 원본 좌표와 구현 CSS/토큰 및 실제 렌더로 확인했다. token 이름이나 개수만으로 전체 효과 일치를 판정하지 않았다.

`P1/independent-final-checks.json`: visual fingerprint, 실제 visual 검사, `backstop --all --diff-base <host> --design-build <build>`, Django check가 모두exit0이다. 추가로 untracked 코드10개 전부가 backstop의 touched/added 집합에 포함되며 누락0을 확인했다. `P1/independent-final-integrity.json`은 모든 입력/registry 원본 파일 보존,10case와 전부pass 결과, 현재 핵심 증거 파일 해시를 기록한다.

정규 native backstop은 --only를 지정하지 않아 원래부터26종 모두 실행했다. --diff-base는 변경 범위 게이트다. 프로토콜의 명시적 --all은 그 범위를 푸는 추가 전역검증이므로 동일 native thread의3턴에서 코드/증거 변경 없이 추가 실행했다. 결과26종(all) blocker0, fingerprint 동일이며 이것은 정규 게이트 일부 미실행이나 plugin-regression의 수정이 아니다.

## 음성 입력의 독립 판정

N1: 첫 턴 native freeze의 exit1/effects.css FileNotFoundError/source_ready=false와 blocked 기록이 capacity 중단 및 evaluator의2턴 마무리 요청보다 먼저 존재한다. 이후 실제 inputs는 exit2이지만 coverage_review 포인터 누락으로 invalid top-level fields에서 먼저 중단됐다. 따라서 이 checker 결과를 “누락 dependency까지 순회해 검출했다”는 증거로 쓰지 않는다. 누락 검출은 실제 freeze, 준비 차단은 native state/실행 순서가 근거다. 원본4개/동결본/manifest와 host/web/plugin은 보존됐다. `N1/independent-verification.json`과 `negative-sequence-evidence.json` 참조.

N2: 사전 제작 source-v1 manifest와 source-v2 entry bytes를 native 실행 전에 동결했다. 초기 host로 시작한 Coordinator가 기존 phase=implement/ready를 복원한 뒤 actual inputs exit2에서 index.html의2759→2837바이트 및 SHA 불일치를 확인하고 blocked로 바꿨다. 초기 문자열을 믿고 시각 슬라이스를 시작하지 않았다. 원본·manifest·case 캡처·scope·design-spec 전부byte 보존, web/host 무변경. `N2/checker-before-native.txt`, `fixture-hashes.json`, `independent-verification.json` 참조. 이는 사전 제작 state의 native 재개 처리이며 기존 정상 생성 앱을 변경한 시험이 아니다.

N5: 실제 사용자 정보 entry26918바이트, SHA `8c3a4467799b7b35845faec037b68ee10cacbd8abb24860fa59ff939f63ba6da`가 사전 기록과 같다. 원본 및 복사본49파일의 byte 동일성을 재검증했다. native 수집은31행 중28ok/3failed, exit1로 끝나 scope에서blocked다. 두 Gowun Batang 직접woff2 URL은 실제GET HTTP404였다. Lucide EOT는 HTTP200/application/vnd.ms-fontobject였으나 현재 collector의 image 분류·형식 검증에서 unsupported image/non-image body로 거부됐다. 두 원인을 구별하며 실패행/원문/응답을 보존했다. 원본 URL 줄 삭제·JSX/CSS 수선·샘플 교체·실패행 제거가 없다. 이는 현재 수집 계약의 준비 차단을 검증했으며 전체 실제 디자인의 보편적 렌더 불가능이나 성공 어느 쪽도 주장하지 않는다. `N5/actual-source-hashes.json`, `independent-verification.json` 및 native 빌드의 source-manifest/HTTP 실패 관찰 참조.

## 실행 개입, 실패 분류와 한계

- `environment-blocked` — 초기 outer app-server EPERM은 정확한 task runner escalation으로 해결했다. child sandbox는 유지했다. 초기 MCP는 approval policy=never로 거부됐고 Python Chrome 대안은 OS startup 오류였다. supported per-tool approval_mode=approve를 격리 Playwright 관찰/상호작용 도구에만 per-run 설정한 뒤 실제 MCP 관찰에 성공했다. 전역 설정/child sandbox 해제는 없다.
- `environment-blocked`, 회복 — P1/N1/N5 첫 턴의 model capacity 오류를 보존하고 동일 thread/동일 모델로 재개했다. 진행 중 역할을 시간만으로 끊지 않았다.
- Git checkpoint 한계 — native git add/commit은 .git/index.lock 권한으로exit128이었다. native는 성공 커밋으로 기록하지 않고 동등한 초기 host HEAD `60fcc9a5f97e0b223e3bb1e31661c27873f5c41d`를 비교 기준으로 사용했다. 커밋·soft reset은 수행하지 않았고 결과는 미커밋이다. 평가자가 대신 커밋하지 않았다. 필수 input/visual/backstop 검증과 untracked 포함은 실제로 확인됐다.
- CLI 해석 정정 — CLI의 빈 receiver 표현을 실제 역할 부재로 잠시 해석해 최소 상태 확인 queue를 보냈으나, raw rollout에서 spawn 성공→interrupted 확인→native followup→running을 찾아 즉시 정정 queue를 보냈다. 두 argv/결과는 P1/queue-steering.* 및 queue-correction.json에 보존했다. 역할 판정·명세·구현 정답이나 대행 호출은 제공하지 않았다. 최종 판정은 실제 raw 결과를 따른다.
- native 관찰 selector timeout과 초기 잘못된 출력 경로는 실패 이력을 보존한 뒤 native가 새 성공 관찰로 해결했다. evaluator가 생성 앱을 수선해 통과시키지 않았다.
- `plugin-regression`: 이번 담당 lane에서 발견된 미해결 회귀 없음. `fixture-invalid`: 정상 input-v2의 무효성 발견 없음. 의도적으로 불완전한N1/N2는 음성 입력이며 실패한 정상fixture로 재분류하지 않는다. `incomplete`: 담당4lane 없음. N4 및 배포/통합 검증은 다른 담당 범위다.

이 성공 범위는 통제 fixture와 명시된 음성 차단에 한정된다. 실제 media API/S3 영상 성공, marketplace 배포 성공, 실제 Downloads 디자인 구현 성공, 모델 일반 신뢰도를 대신 입증하지 않는다.

Serena/Graphify: opt-in 표식이 없어서 검색·로드·호출하지 않았다.
