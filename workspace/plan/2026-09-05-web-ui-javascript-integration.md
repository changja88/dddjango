# dddjango-web UI JavaScript Integration Plan

> For agentic workers: use subagent-driven-development for bounded implementation/review tasks; execute sequentially with evidence. This user approved planning **and execution** of the integration. No additional approval checkpoint, commit, release, or backend change is part of this task.

**Goal:** 기존 4개 agent가 새 implementation-javascript를 올바르게 설계·구현·감수하도록 Claude/Codex 코퍼스·파일트리·배선·검사를 함께 전환한다.

**Architecture:** 서버 판정은 Django/VM, 구조는 HTML, 서버 요청·HTML 교체는 HTMX, 시각 값은 CSS, 브라우저의 임시 UI 상호작용은 JS가 소유한다. 설계 agent는 architecture 규범을 소비하고 coder-web·discipline-reviewer-web은 JS 스킬을 직접 소비한다. 결정적 검사기는 경로·실행 채널·판형을 검사하며 업무 의미와 UI 수명은 감수 및 실제 동작 검증으로 확인한다.

**Tech Stack:** 산문 Markdown/YAML 코퍼스, Python 표준 라이브러리 검사기, Django 5.2, HTMX 2.x, 외부 vanilla JS, 기존 브라우저 평가 환경.

**Spec:** 사용자가 승인한 직전 통합 범위; `docs/master.html`에서 연결한 `docs/file_tree_web.html`; 신규 `implementation-javascript`; `workspace/reference/implementation-javascript/reference/review.md`의 알려진 통합 지점. 기존 웹 빌드 스펙 중 이번 결정과 무관한 부분은 유지한다.

## Global Constraints

- dddjango-web와 codex-dddjango-web만 실행 규범 변경. backend dddjango·ontology·매니페스트 버전·배포 변경 없음.
- 기존 사용자 변경 보존. 현재 workspace에 승인된 미커밋 정본이 있어 이 경로에서 작업하며 `/tmp/dddjango-web-js-integration-20260905/before`에 작업 전 파일을 보존한다. 커밋/스태시/브랜치 전환으로 사용자 작업을 수용하지 않는다.
- 신규 agent 없음. JS 스킬 직접 주입 대상은 coder-web과 discipline-reviewer-web 2개다.
- JS는 승인된 UI 기능만. 업무 권한·금액·저장 판정·별도 업무 API 호출·SPA 상태 계층은 금지. native HTML/CSS로 충분하면 JS 파일 없음.
- 신규 static 골격은 css/·js/·htmx/·images/ 네 폴더. 검증된 fonts/·files/는 기존 조건 생성 규칙 유지.
- JS는 `static/js/<기능>.js`, HTMX 선언 조각은 `static/htmx/<기능>.html`: 각각 기능당 한 파일, snake_case, 평면. 내부 함수당 분할하지 않는다.
- 신규 HTMX core는 `static/htmx/htmx.min.js` 하나. 기존 `static/js/htmx.min.js` 또는 `htmx.js`는 브라운필드 기존 설치로만 소비하고 새 이중 설치·조용한 이동/업그레이드 없음. 누락 시 공식 2.0.10 고정 배포 파일을 설치하고 버전·출처 기록.
- motion.js는 `static/js/motion.js`의 기존 조건 설치·byte 고정 러너를 유지한다. 일반 기능 이름으로 덮어쓰지 않는다.
- 기능 JS 실행 태그는 base의 공통 로드 또는 페이지의 범용 script block에 외부 static 참조로 한 번만 둔다. fragment에는 실행 스크립트 없음. classic은 defer, 기존 module 방식도 허용하되 async로 순서를 깨지 않는다.
- inline 실행 JS·on* handler·hx-on·js:·hx-trigger 조건식은 계속 차단. 데이터는 Django json_script 또는 escape된 data 속성으로 전달하며 수동 executable source 보간 금지.
- HTMX 선언 조각은 Django include로 렌더한다. 공개 static 원문에는 비밀·사용자별 렌더 결과를 저장하지 않으며 static URL을 업무 fragment endpoint로 쓰지 않는다. 데이터/권한/CSRF/fragment 응답은 view와 section이 계속 소유한다. 이 전환을 위해 새 finder·middleware·템플릿 엔진을 만들지 않는다.
- Claude/Codex reference와 scripts/assets는 byte 미러. 역할·Coordinator는 플랫폼 형식의 의미 미러. 플랫폼 명령을 서로 복제하지 않는다.
- 검사기에 업무 로직 부재·기능 일대일 의미·JS 모션 전수 검출 능력이 있다고 과장하지 않는다.

## Rulings and preflight

| 쟁점 | 결정과 근거 | 검증 |
|---|---|---|
| 계획만 vs 실행 | 최신 사용자 요청은 계획 후 실행 승인. 이전에 완료한 스킬 작성과 구분해 통합을 이번 단일 작업으로 집행 | 아래 4단계 완료 전 종료하지 않음 |
| 스킬의 추가 승인/격리/커밋 기본값 | 현재 요청·개발 지침의 권한을 우선. 미커밋 정본이 있는 현재 경로의 한정 변경과 사전 사본을 사용 | 변경 파일을 사전 hash와 대조 |
| static/htmx와 section | 기능별 요청 선언은 static/htmx에 한 번, 응답의 화면 구조·서버 데이터 소유는 section/view. include로 조합 | Django 렌더 및 실제 HTTP 교체 |
| 표시 상태 소유 | 서버 표시 데이터 판정과 password visibility·clipboard pending 같은 임시 UI 상태 구분 | 정상 UI 통과/업무 판정 반송 사례 |
| 동적 표현 검사 | 기존 CSS/러너 검사 유지, `ui-js` 분류 및 파일/root 좌표 추가. JS 내부 모션의 전수 역추적은 의미 감수 | 유효 ui-js/유령 파일·root/기존 CSS·러너 회귀 |
| 플랫폼 실제 실행 | 동일 소규모 UI 요구로 실제 역할·스킬 로딩 증거와 산출물을 확보. CLI 실행 제약과 브라우저 검증을 별개로 기록 | 로딩 trace, 역할 산출, 실제 Django/HTMX 확인 |

| 단계 쌍 | 생산 → 소비 | 충돌 점검 |
|---|---|---|
| 1→2 | 허용 경로·로드·motion 분류 → 결정적 검사 | 규범을 먼저 확정, 검사는 이를 좁게 집행 |
| 1→3 | agent 주입·Coordinator handoff → 실제 역할 실행 | JS 직접 주입 2개, 설계자는 책임 명세 |
| 2→3 | 정상 경로 통과·위반 반송 → 생성 산출 검증 | 검사기 기대값을 생성 코드에 맞춰 낮추지 않음 |
| 1/2/3→4 | 검증된 현재 구성 → master 연결 문서·미러·완료 증거 | 과거 스킬 단독 평가 기록은 역사로 보존 |

## Task 1: 실행 코퍼스와 역할 계약

**Files:** dddjango-web의 commands/dddjango-web.md, agents 4개, skills/architecture-web·discipline-web-houserules·implementation-ui의 SKILL/reference, undecidable-web.md, implementation-javascript의 적용 완료 문구; 대응 Codex 파일. 범용 discipline-cleancode 본문은 관련 충돌이 실제 있지 않으면 손대지 않는다.

**Interfaces:** 설계 명세에 기존 문서 안의 `UI 동작 계약`을 추가한다. 행은 `기능 | 요구 근거 | 담당 기술 | JS/HTMX 파일 | root·대상 | 서버 요청·swap 경계 | 임시 상태·자원 | 키보드·실패·정리 | 검증 행위`를 소유한다. JS가 없으면 필요 없음과 이유를 적는다. 별도 명세 파일은 만들지 않는다.

- [x] 현행 백스톱 기준선 `make verify-web` 결과 확인.
- [x] Python/HTML/HTMX/CSS/JS 책임, 기능 파일·조각 포함 관계, 로드 위치를 위 constraints대로 소유 문서에 반영.
- [x] coder-web·discipline-reviewer-web에 JS 스킬 주입. 설계/리뷰/구현/감수가 같은 UI 동작 계약을 소비하고 실제 증거를 넘기도록 연결.
- [x] Coordinator는 기존 승인 게이트와 배선 소유를 유지하면서 host 상태·core 버전·공통 scripts block과 JS 증적 전달을 연결. static_only는 서버 업무 계약 없음이며 로컬 UI JS 금지 신호가 아님을 구분.
- [x] 모션 처분 분류 `ui-js`, 좌표 `static/js/<기능>.js :: [data-<root>]`, 값은 필요 CSS 토큰, 근거 및 실제 동작 검증을 명세. 구현 불가능을 이유 없이 CSS 한계로 자동 분류하지 않음.
- [x] 플랫폼 미러와 기존 광범위 JS 금지 표현·VM 유일 판정 표현의 잔재를 점검. 독립 리뷰에서 규범 충돌·과잉 의무·동작 예제 누락을 판정하고 중요 발견 수정.

## Task 2: 백스톱·모션 검사와 회귀

**Files:** dddjango-web/scripts/src/common.py·check_structure.py·check_purity.py·check_naming.py(필요 부분), scripts/check_motion_spec.py, scripts/test/fixtures_backstop.sh·fixtures_motion_spec.sh 및 전용 UI JS fixture. 대응 Codex scripts byte 미러.

**Interfaces:** backstop exit 0/1/2, WS/WI/WN/WP 기존 ID·diff gate 유지. WP1은 신규 JS 경로/형태, WP2는 실행 script 로드 계약, WP3 inline 채널, WP5 motion byte 판형. ui-js motion 검사는 파일 및 literal root가 소스와 HTML에 존재하는 좁은 구조 근거다.

- [x] 새 계약 fixture를 먼저 실행해 현행 red를 기록: 정상 기능 JS+페이지 defer load; HTMX 4폴더 골격; 기능별 HTMX include; json_script 데이터 소비; ui-js motion 좌표.
- [x] 반례를 각각 검사: JS 잘못된 폴더/중첩/라이브러리 위장, 존재하지 않는 JS src, CDN/data/javascript/path suffix 위장, fragment script, inline/hx-on/js: 유지, core 중복, motion 변경, 기존 줄에 시작된 script의 변경된 속성, ui-js 유령 파일/root.
- [x] 표준 라이브러리로 필요한 최소 검사 구현. 기존 파일 전체를 새 규칙으로 이관하는 강제 수정은 하지 않는다. 파일·태그의 의미는 감수자가 판단한다.
- [x] 기존 fixture를 새 계약이 바뀐 사례만 갱신. 과거 커스텀 JS 금지 fixture를 삭제만 하지 않고 잘못된 경로 반례로 대체하고 정상 짝을 추가.
- [x] targeted fixture 및 `make verify-web` 통과 후 독립 코드·계약 리뷰. 문서와 검사가 다르면 같은 단계에서 해결.

## Task 3: 역할 파이프라인과 브라우저 평가

**Files:** 임시 평가 앱·프롬프트·실행 trace는 `/tmp/dddjango-web-js-integration-20260905/`; 재현 가능한 요약·검사 코드·결과는 `workspace/eval/web-ui-javascript-integration/2026-09-05/`.

**Interfaces:** 원문 요구→architect 명세→독립 설계 리뷰→coder 코드→독립 감수→backstop→브라우저 결과. 평가 프롬프트는 동작 요구를 주며 올바른 구현을 미리 제공하지 않는다.

- [x] 동일 요구의 소규모 Django 평가 앱 준비: 비밀번호 표시와 로컬 파일 미리보기, 서버가 렌더한 HTMX 교체, 기본 HTML disclosure. 사용자 승인·시안 부재·static_only를 평가 범위로 명확히 제공. 업무 API를 발명하지 않음.
- [x] Claude 로컬 plugin-dir 및 Codex의 실제 role/skill 로딩 경로에서 역할 입력·출력과 새 스킬 읽기 증거 확보. CLI의 가용성·권한·모델 실행 실패는 정상 완료로 기록하지 않음.
- [x] 필요 없는 JS를 생성하지 않는지, 업무 판정을 JS로 옮기는 제안을 반송하는지, 이전 동작·이웃 UI를 지우지 않는지 독립 감수 확인.
- [x] 실제 Django 렌더·HTMX HTTP 교체·외부 JS 1회 로드·여러 인스턴스·반복 처리·삭제/정리·키보드·콘솔 오류를 브라우저에서 검사. 평가용 이벤트 조작을 실제 HTTP 교체 증거로 사용하지 않음.
- [x] 발생한 규범/검사/실행 결함을 소유 단계에서 고치고 영향 검사 재실행. 전체 제품 적용이나 모든 브라우저 검증을 했다고 과장하지 않음.

## Task 4: 정본 연결·최종 검증

**Files:** docs/master.html의 기존 연결 및 file_tree_web.html, work_flow_web 관련 원본/투영물 중 이번 역할·상태·트리와 관련된 부분; 새 통합 결과 보고서. 기존 web-auth 이슈 및 이전 스킬 평가 기록은 불변.

- [x] master가 가리키는 웹 트리·동작 흐름의 미적용 표시를 실제 최종 구성과 맞춤. 파일트리에서 fonts/files·HTMX include/section 경계·motion 예외 등 실행 규범과의 모순을 없앰. 다이어그램 변경은 archify 생성/검증 방식 소비.
- [x] scripts/assets/reference byte 비교, Claude/Codex 역할 주입 대조, SKILL YAML·참조 링크 확인, `claude plugin validate dddjango-web --strict`.
- [x] `make verify-web`, 전체 `make verify`, 변경 diff 및 독립 최종 리뷰. 관련 없는 기존 실패는 분리해 원인·범위를 보고하고 통과로 표시하지 않음.
- [x] 계획 체크박스와 최종 보고서를 실제 증거로 갱신. JS 허용 통합 상태·검증 범위·남은 제한을 보고. 커밋·배포 없음.
