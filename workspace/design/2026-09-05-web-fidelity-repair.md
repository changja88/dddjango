# dddjango-web 시안 재현·파일 수집 수정 계약

범위: `dddjango-web/`와 `codex-dddjango-web/`, 이 검증 기록. 백엔드 플러그인·온톨로지·실제 web-auth 앱은 변경하지 않는다. 릴리즈는 별도다.

기준선: `2026-09-05-web-auth-run-issues.md`, Claude web-auth 런의 공개 대화·도구 실행·산출물. 해당 런에서는 extract_dc/fetch_images 실행 없이 수집 실패가 대체 이미지 결정으로 넘어갔고, 화면 경계 재해석·근접 토큰 대체·검토 입력 누락이 겹쳤다. G2 사용자 승인은 완료되지 않았다. 기존 `make verify-web`은 수정 전 통과한다.

| 실패 | 수정 계약 | 소유·검증 |
|---|---|---|
| 새 dc 형식 미지원 | legacy `.screen`과 `data-screen-label` 구별, 다중 후보 자동 오선택 차단, 원본 경계·hash 기록 | extract_dc, 다른 이름·비율 정상/실패 픽스처 |
| 잘린 이미지·누락 의존성·다운로드 미실행 | 실제 바이트 수집과 크기/hash/실패 사유 기록, HTML/CSS 의존성 해소, 성공 여부와 존재 여부 분리 | 수집 CLI·manifest, local/HTTP/오류본문/잘린 PNG 회귀 |
| 미수집을 시안 없음으로 처리 | 출처 수집→렌더 확인→설계 순서. unresolved는 입력 차단이며 사용자 대체 결정은 항목별 기록 | Coordinator, 읽기 전용 행동 시나리오 |
| 레이아웃 재해석·근접 값 대체 | 렌더 기준 화면 경계·상태·요소 대응; 원본 exact 값 신규 토큰 허용; 같은 값/같은 형상일 때 재사용 | architecture/implementation + 역할, 원본/별도 시안 검토 |
| 시안에 없는 기능·기술제약에 따른 삭제 | 원본→변경→근거→결정 주체·응답을 별도 이탈 행으로 보존; noJS는 자동 삭제 승인이 아님 | architect/reviewer/Coordinator, 압력 시나리오 |
| 명세만으로 구현 감사 | 원본·수집 manifest·이탈표·coder 보고·실제 렌더 증적을 같은 감사 입력으로 전달 | 모든 handoff, 독립 코퍼스 리뷰 |
| compile/check만 green | 실제 Django 렌더 출력과 브라우저 이미지·폰트·상태·전 구간 대조 기록; 미실행은 미검증 | coder/Coordinator, 임시 smoke 실행·증적 보존 |
| 템플릿 주석 누출 | 단일줄 `{# #}`와 다중줄 comment 블록 구별, 추가된 잘못된 주석은 백스톱 차단 | WP6, 정상 주석·브라운필드 대조 |

검증 순서: 실패 픽스처 확인 → 구현 → 해당 픽스처 green → Claude/Codex 미러 대조 → 정상/변형 행동 시나리오 → 독립 모순·실효성·과적합 검토 → `make verify-web` → `make verify`.

실효성 판정의 한계: 의존성 수집 성공은 JSX 런타임 재현 성공이 아니며, 토큰 항목 수 일치는 요소 배치 일치가 아니다. 정적 검사·에이전트 시나리오·실제 브라우저 검증을 구별해 결과를 아래에 기록한다. 미실행을 성공으로 보고하지 않는다.

## 실행 결과

- 기준선 `make verify-web`: PASS (기존 픽스처 파일 5개).
- 수정 후 `make verify-web`: PASS (픽스처 파일 7개). 자산 CLI 통합 21건, dc 추출 31건, 템플릿 9건, backstop 62건을 포함한다.
- `make verify`: PASS — ontology·base-core·base-cross·base-backstop·base-regen·web 6/6, 192초. 원시 로그: `/tmp/dddjango-web-repair-full-verify.log`.
- `claude plugin validate dddjango-web --strict`: PASS. Claude/Codex script·asset·knowledge reference byte mirror 검증 PASS.
- 독립 코퍼스 재검: 이번에 발견한 blocker/important 잔존 0. 동결 경로와 원본 식별 분리, 확장자 없는 문서, 이미지 `_hash` 명명과 WN8, fonts/files 허용과 무관한 폴더 차단, WP6 정상 verbatim 대조까지 직접 재검했다.

### 행동 검증과 과적합 점검

수정 전·1차 수정·최종 본문을 별도 context에서 읽는 역할 판단 호출을 Claude 13회·Codex 13회, 총 26회 수행했다. 각 플랫폼·시나리오 조합당 1개 응답이므로 반복 성공률을 뜻하지 않는다. 이 호출에는 앱 구현과 브라우저 실행이 포함되지 않는다.

| 대조 | 관찰 결과 |
|---|---|
| 수집한 이미지가 전부 실패 | 기존 Claude의 실패 manifest 후속 전달 누락을 재현. 수정 후 실패 행을 보존·전달하고 재수집하도록 판정 |
| 원본 22/26px·1.62 값이 기존 토큰에 없음 | 기존 Codex의 불필요한 토큰 이름 승인 반송을 관찰. 수정 후 정확값 신규 토큰 등록으로 판정 |
| noJS로 삭제한 원본 기능 복원 | 1차 수정의 과도한 재승인 요구를 추가 수정. 최종 양 런타임 모두 승인된 원본 복원은 새 이탈 승인이 불필요하다고 판정 |
| 원본·근사 보고가 빠진 감사 | 누락된 근거를 복구하여 감사하고 포괄적인 accepted 표시로 불일치를 억제하지 않음 |
| 정상 대조 | 시안 없음·이미지 단독·데이터 슬라이스·브라우저 부재를 구별. 해당하지 않는 증적을 강제하지 않고, 실제 브라우저 미실행은 미검증으로 유지 |

최종 추가 호출 6건은 모두 목표 판정을 충족했다. Codex는 기본 전역 skill 목록의 영향을 받을 수 있어 완전한 격리 실험이라고 주장하지 않는다. 최종/1차 수정 Codex 호출의 command·MCP·file·web tool 호출은 0건으로 확인했다. 원시 입력·응답·파일 hash·실행 결과는 `/tmp/dddjango-web-behavior-1788580827240694000/`에 보관했다.

### 실제 자산 수집·구현·브라우저 검증

원본 로그인과 이름·화면 비율·내용·상태가 다른 `Visit brief`를 검증용 임시 Django 앱에 구현했다. 수정된 역할과 reference, 승인 명세를 제공한 Claude coder fresh 실행 2회(첫 구현, manifest 파일명 변경에 따른 참조 수정)다. 전체 G0→G2 실행과는 구별한다.

- 실제 로컬 HTTP에서 HTML·CSS·SVG·font·txt 5개 파일을 동결하고 크기·hash를 기록했다. `source_ready=true`를 확인한 뒤 이미지가 `web/static/images/`에 착지했으며, coder가 font와 txt를 각각 `web/static/fonts/`, `web/static/files/`에 반영했다.
- coder가 원본 PNG·manifest·실측을 읽고 구현했다. 실제 Django 응답 HTML을 보존한 임시 검증은 초기 72 PASS/0 FAIL, 최종 수정 후 실패 0이었다. Django check와 backstop도 통과했다. 임시 앱이 비git 디렉터리여서 WS5 신규 골격 판정은 생략됐으며, 저장소 fixture에서 별도로 검증했다.
- 외부 Coordinator가 Playwright로 720×520과 390×844를 직접 비교했다. 두 크기 모두 audit diff 0, 텍스트 미조인 0이며, 원본/구현 PNG 파일도 각각 SHA-256이 동일했다. desktop 카드 좌표·크기·24/22/26px padding·본문 행간·작은 링크·구분선의 실측 JSON이 정확히 같았다.
- 이미지 naturalWidth 44/complete, `Visit Sans` font loaded 및 font check 성공. 요구 HTML·CSS·SVG·font 요청 모두 HTTP 200이었다.
- 실제 다운로드 이벤트로 `visit_notes.txt`를 받았고 오류 없이 HTTP 200, 본문이 원본과 같았다. native details의 닫힘→펼침→닫힘, 펼침 시 시간 안내 표시를 확인했다. 취소 상태 문구 노출·템플릿 주석 누출·가로 넘침은 없었다.
- 브라우저 console의 유일한 오류는 시안에 요구되지 않은 `favicon.ico` 404였다. 요구 자산 오류와 구별하여 기록한다.

| 증적 | 원본 | 구현 |
|---|---|---|
| 720×520 화면 | [PNG](assets/2026-09-05-web-fidelity-repair/holdout-source.png) | [PNG](assets/2026-09-05-web-fidelity-repair/holdout-implementation.png) |
| 390×844 화면 | [PNG](assets/2026-09-05-web-fidelity-repair/holdout-source-narrow.png) | [PNG](assets/2026-09-05-web-fidelity-repair/holdout-implementation-narrow.png) |
| 720×520 audit | [JSON](assets/2026-09-05-web-fidelity-repair/holdout-source-audit.json) | [JSON](assets/2026-09-05-web-fidelity-repair/holdout-implementation-audit.json) |
| 390×844 audit | [JSON](assets/2026-09-05-web-fidelity-repair/holdout-source-narrow-audit.json) | [JSON](assets/2026-09-05-web-fidelity-repair/holdout-implementation-narrow-audit.json) |
| 세부 실측 | [JSON](assets/2026-09-05-web-fidelity-repair/holdout-source-geometry.json) | [JSON](assets/2026-09-05-web-fidelity-repair/holdout-implementation-geometry.json) |

PNG SHA-256: 720×520은 `1be16b98d6e5684571c278a42b83d9a1dc06735c9dcc0fbd34c4b5c61665ac85`, 390×844는 `cef69d90e2f02a3be6e153bdc1ac21ddb498b05ce18e0d0900655ede6d717e39`다.

원본 사건의 dc 파일도 읽기 전용으로 재검했다. 화면 미지정은 후보 3개로 명시적으로 실패하며, 로그인 선택 시 480×768 경계와 누락 PNG·JSX 의존성이 기록되어 `source_ready=false`가 된다. 실제 web-auth 앱의 5개 화면을 고쳐 전체 파이프라인을 다시 실행한 결과는 아니다. 동적 의존성·JSX 실행·모든 외부 사이트 다운로드를 이 정적 holdout 하나로 보증하지 않는다.

이 기록은 플러그인 수정과 위 검증을 마친 시점의 결과다. 실제 web-auth 워크트리, 백엔드 플러그인과 온톨로지는 변경하지 않았다. 커밋·버전 변경·릴리즈·설치 캐시 갱신은 이 구현 검증 이후의 별도 절차다.
