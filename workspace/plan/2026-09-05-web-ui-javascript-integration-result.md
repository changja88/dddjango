# dddjango-web UI JavaScript 통합 결과

상태: 완료. Task 1–4와 최종 독립 리뷰를 통과했다. 저장소 소스에 통합했으며 커밋·배포는 수행하지 않았다.

승인 범위는 새 `implementation-javascript`를 기존 dddjango-web 역할 체인에 연결하는 작업이다. Claude 정본과 Codex 미러, 관련 백스톱, master가 연결하는 웹 문서를 함께 갱신했다. 기존 사용자 변경을 보존했고 backend dddjango·온톨로지·버전·설치 캐시는 변경하지 않았다.

## 최종 책임과 협력 계약

| 기술·역할 | 책임 |
|---|---|
| Python / Django / VM | 권한·금액·저장 등 업무 판정과 서버 표시 데이터 조립 |
| HTML | 의미 구조, 기본 제어, native disclosure 등 기본 상호작용 |
| HTMX | 서버 요청과 응답 HTML의 부분 교체 |
| CSS | 시각 값과 표현 |
| JavaScript | 승인된 브라우저 임시 UI 상태와 브라우저 자원 관리 |
| 설계자·설계 리뷰어 | 기존 명세 안의 UI 동작 계약으로 기술·소유·교체·검증 경계 확정 |
| coder-web | JS 스킬을 직접 읽고 승인된 기능 구현 |
| discipline-reviewer-web | 같은 JS 스킬로 의미·수명·실제 검증 증거 감수 |
| Coordinator | 호스트 배선과 역할 간 산출물·검증 증거 전달 |

새 agent는 만들지 않았다. 새 스킬의 직접 주입 대상은 coder-web과 discipline-reviewer-web 두 역할이다. 설계 역할의 추가 자료 열람은 허용되며 직접 주입과 구분한다. HTML/CSS로 충족되는 기능에 JS 파일을 추가하지 않는다.

`static/css/`, `static/js/`, `static/htmx/`, `static/images/`를 기본 폴더로 사용하고, 검증된 폰트·일반 파일의 `fonts/`·`files/` 조건 생성 규칙을 유지한다. 기능 JS는 평면 `static/js/<기능>.js`, HTMX 선언 조각은 평면 `static/htmx/<기능>.html`에 기능당 하나씩 둔다. HTMX 선언은 Django include로 렌더하며 업무 fragment 응답은 계속 view/section이 소유한다.

신규 HTMX core는 `static/htmx/htmx.min.js`에 둔다. 기존 `static/js/htmx.min.js`·`htmx.js`는 확인된 기존 설치로만 소비하며 조용히 이동·업그레이드하거나 중복 설치하지 않는다. `static/js/motion.js`는 기존 고정 러너 규칙을 유지한다.

기능 스크립트는 base 또는 페이지의 범용 scripts block에서 실제 로컬 static 파일로 한 번 로드한다. classic `defer`와 기존 module 방식은 허용하며 fragment의 실행 태그, inline 실행·이벤트 속성·HTMX 실행 표현식은 계속 차단한다. 데이터는 Django `json_script` 또는 escape된 data 속성으로 전달한다.

## 규범·검사 정합성

Task 1에서 역할·스킬·Coordinator의 광범위 JS 금지와 새 UI JS 허용 규칙을 함께 전환했다. 설계 명세에는 요구 근거, 담당 기술, 파일/root, 서버 요청·swap 경계, 임시 상태·자원, 키보드·실패·정리, 검증 행위를 담는 UI 동작 계약을 연결했다.

Task 2에서는 경로·파일 형태·실행 태그·기존 inline 차단·고정 러너 판형과 `ui-js` 모션 좌표를 검사하도록 백스톱을 갱신했다. 테스트를 먼저 실행한 RED를 기록했고, 독립 리뷰에서 발견한 quoted `>` 태그 경계, 앞에 추가된 중복 로드, template interpolation 주석의 가짜 root 세 결함을 수정한 뒤 재리뷰 승인을 받았다.

검사기는 구조 근거를 확인한다. 업무 로직 부재, 기능과 파일의 의미상 일대일 대응, 모든 JS 모션, 실제 브라우저 수명을 자동으로 증명한다고 주장하지 않는다. 이 부분은 명세·독립 의미 감수·실제 동작 검증이 담당한다. 같은 파일 안의 중복 로드 검사는 문법적 계수이며 전체 템플릿 분기·상속의 실행 의미를 재구성하지 않는다.

## 검증 결과

| 검증 | 결과 |
|---|---|
| Task 1 코퍼스 독립 리뷰 | APPROVE, 중요 미해결 사항 없음 |
| Task 2 백스톱 수정 재리뷰 | APPROVE, P2 세 건 해소 |
| UI JS / motion / 기존 backstop fixture | 각각 17/17, 25/25, 62/62 통과 |
| Task 2 `make verify-web` | fixture 8개 suite와 scripts/assets/요청 가이드 미러 통과 |
| 역할 주입·SKILL YAML·reference 사전 점검 | 직접 JS 주입 2개 역할, YAML 15개 정상, reference 5쌍 byte 일치 |
| Claude manifest strict 검증 | 통과 |
| Task 3 실제 native 역할 실행 | Claude·Codex 모두 설계 승인 → 구현 → 최종 감수 APPROVED |
| 실제 Django/HTMX 브라우저 검증 | 양쪽 I1–I12 통과; Codex 실제 200 교체 31건, Claude 16건 |
| 의미 반례 | 필요한 로컬 UI JS 수용, native disclosure 유지, JS 업무 최종 판정 제안 거부 |
| 평가 앱 canonical backstop | 실제 empty-tree 기준 신규 파일 검사, 양쪽 blocker 0, 생략 없음 |
| 보존 앱의 별도 폴더 재현 | 모델 재생성 없이 양쪽 브라우저·backstop 통과 |
| Task 3 독립 증거 리뷰 | APPROVE, blocker 0 / important 0 / 신규 nit 0 |
| Task 4 문서·archify·최종 미러 검증 | showcase 9/9, 오류·경고 0; 4 viewport 넘침 없음; light/dark 캡처 4개 직접 확인; reference 6쌍·workspace JS byte 일치; SKILL YAML 15개·reference 표기 23개 정상 |
| 전체 `make verify` | 6/6 통과, 197초; 전체 로그 `/tmp/djr-verify.16Semr` |
| 최종 변경 독립 리뷰 | APPROVE, blocker 0 / important 0; 최종 파일 56개 hash·크기 및 적용 상태 확인 |

브라우저 통과를 위해 생성된 web 코드를 사후 수정하지 않았다. 코드·명세·스킬 로딩 기록·실제 HTTP 및 자원 기록·스크린샷·재현 절차를 [평가 요약](../eval/web-ui-javascript-integration/2026-09-05/summary.md)과 [재현 안내](../eval/web-ui-javascript-integration/2026-09-05/README.md)에 보존했다.

## 평가 범위와 한계

각 런타임의 통제된 생성 표본 하나를 실제 역할별 호출로 평가했다. 외부 하니스가 Coordinator의 산출물 전달을 수행했다. 마켓 설치, 전체 slash-command G0→G2, 모든 모델·브라우저 또는 실제 제품 적용까지 검증한 결과는 아니다.

Codex는 동일 preview owner 아래의 종속 제어 교체를, Claude는 유지된 외곽 패널 안의 preview owner 교체를 구현했다. 두 경계를 구분해 보고했으며 양쪽 모두 독립 자식 교체와 이웃 보존을 확인했다. 지연 완료와 실패 HTTP 주입은 실제 서버 교체·정상 콘솔 결과와 구분했다.

Claude의 첫 기본 Fable 실행은 시간 제한 내 설계를 만들지 못했다. 성공한 체인은 per-invocation 설정을 분리한 Opus medium 실행이며, 초기 hook 권한 오류·PWD·출력 경로 이탈도 기록했다. 기본 사용자 설정이나 모델 자체의 신뢰성을 입증하지 않는다. Codex 모델 표기는 관찰된 CLI 설정이며 서버 응답의 모델 식별자는 제공되지 않았다.

평가 중 호스트의 static prefix·favicon과 HTMX 완료 대기 조건을 보완했고 원래 실패를 보존했다. 최종 Claude 감수의 비차단 nit 네 건은 기록만 남겼다. 검사 통과를 위해 코퍼스 규칙을 완화하거나 선택적 코드 정리를 추가하지 않았다.

## 정본 연결과 작업 범위 확인

[계획](2026-09-05-web-ui-javascript-integration.md), [master](../../docs/master.html), [웹 파일 트리](../../docs/file_tree_web.html), [웹 동작 흐름](../../docs/work_flow_web_guide.html)이 이번 작업의 진입점이다. master의 기존 연결은 올바르므로 유지했다. 파일 트리·흐름 가이드·archify 명세/산출물·전달 기록은 실제 적용 상태를 가리킨다. workspace JS reference를 현행 배포 본문에 동기화했고, Codex의 browser 실행자 단락 한 곳을 Claude의 사용자 승인 범위 안 읽기 전용 관찰 규범과 맞췄다. 최종 독립 리뷰에서 역할·검사·문서의 책임 일치와 사용자 변경 보존을 확인했다. 작업 전 사본 96개의 해시가 유지됐고 master의 기존 사용자 WIP도 byte 그대로다. HEAD는 `4231997`이며 커밋·배포는 실행하지 않았다.

Serena / graphify: skipped — opt-in 표식이 없어 기본 도구를 사용했다.
