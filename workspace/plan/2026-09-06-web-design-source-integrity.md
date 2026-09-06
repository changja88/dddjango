# dddjango-web 원본 전달·완료 판정 구현 계획

Goal: 불완전한 동결과 자의적 시안 해석, 임의 미디어 대체, 부분 검증의 전체 통과를 실행 경로에서 차단하고 dddjango-web으로 배포한다.
Architecture: 기존 원본 수집기에 좁은 의존성 탐색 보완을 적용하고 작은 로컬 증거 검사기를 더한다. Coordinator/4역할이 원본과 독립 증거를 직접 인계하며 기계 정합과 시각 판단을 구분한다.
Tech: Python 표준 라이브러리, Bash fixtures, Claude/Codex Markdown 프롬프트, 독립 Django/Playwright 평가.
Spec: workspace/design/2026-09-06-web-design-source-integrity.md (마지막 확정 계약이 초안보다 우선).

## Global Constraints

- 변경은 dddjango-web 및 codex-dddjango-web 미러와 직접 필요한 workspace 기록에 한정한다. backend dddjango·ontology·사용자 앱·활성 서버/DB·primary WIP는 수정하지 않는다.
- 원본 소스/렌더는 외형 정본이다. 명세는 코드 분해·상태·동작·API 계약을 다룬다. 근사·풀 밖·슬라이스 밖을 효과 생략 근거로 쓰지 않는다.
- 정적 스캐너와 증거 JSON 검사는 시각 일치/실제 관찰/출처 진위의 기계 증명이 아니다. 검출된 미해결 의존성, 미검증 범위, 실패한 API를 성공으로 덮지 않는다.
- canonical scripts/assets는 Codex와 byte 동일, 역할/Coordinator는 플랫폼 도구를 보존한 의미 미러다. 새 구조는 작은 증거 검사 수준이며 레이아웃 IR/범용 엔진은 금지한다.
- 독립 임시 checkout에서만 작업한다. 역할 implementer는 하위 에이전트를 만들지 않는다. 이미 확인된 문제를 재조사하거나 불필요한 tests/규칙을 늘리지 않는다.
- 출시 승인 여부를 재질문하지 않는다. 모든 필수 게이트를 통과한 뒤 make release-web만 사용한다. 검사 실패를 건너뛰지 않는다.

## Task 1: 원본/시각 증거 검사와 의존성 수집 보완

이 과제는 도구 구현과 그 정확한 사용 계약을 소유한다. spec의 마지막 확정 계약을 먼저 읽는다. 아래의 파일 외 수정이 꼭 필요하면 사유를 보고한다.

Files:
- Modify dddjango-web/scripts/design_sources.py, 필요한 경우 freeze_design.py
- Create dddjango-web/scripts/check_design_evidence.py (필요하면 같은 디렉터리의 작은 책임별 helper)
- Modify dddjango-web/scripts/backstop.py
- Create dddjango-web/scripts/test/fixtures_design_evidence.sh 와 테스트용 Python (기존 fixture 관례)
- 기존 수집 fixture에 좁은 스캐너 회귀 추가
- Create dddjango-web/skills/implementation-ui/references/design-evidence.md (정확한 schema/CLI/지원 경계/최소 JSON 예시; 규범 설명 산문 중복 금지)
- 대응 Codex scripts 및 reference byte 미러

구현 순서:
1. 기존 수집 fixture/read helpers를 읽고 의미 있는 실패/정상 짝을 먼저 만든다. 새 검증이 없는 현재 반례 실패를 확인한다.
2. JS 문자열/주석 속 가짜 import를 의존성으로 잡지 않고 실제 ES import/export-from 및 HTML inline script/module 리터럴 import를 잡는다. 검출된 비리터럴 import·JSX src식·bare module은 명시 미지원/blocked다. JS 실행기/번들러/import-map resolver는 만들지 않는다. 지원 범위를 정확히 문서화한다.
3. check_design_evidence.py CLI: --build <dir> --project-root <dir> --phase inputs|visual, --fingerprint는 digest 계산/출력만 하며 입력/증거 파일을 수정하지 않는다. exit 0=선언 범위 정합, 1=사용/내부 오류, 2=결함/증거 부족. 순수 stdlib, 로컬 읽기. 이미지 검증·해시·source resolution은 기존 helper 재사용한다.
4. design-input.json version=1에 reference_root, manifests(각 원본 수집의 manifest 경로 목록), scope와 coverage_review의 path/sha256 포인터, optional host_files(승인한 project-relative 경로), nonempty cases를 둔다. case는 고유 id, screen, state, viewport [w,h], scope_refs, entrypoint {path,sha256}, reference_capture {path,sha256}, optional media 요구 목록을 가진다. build 내 증거 경로와 project 내 host 경로를 구분하고 confinement을 검사한다. 유효한 원본 단독 이미지도 지원한다.
5. inputs: 실제 manifest bytes와 status/source_ready, entrypoint, 모든 파일 존재·크기·sha·경로를 검증하고 정적 참조 폐쇄를 재검사한다. 삭제된 실패 행/의존성 행과 구/신 버전 혼합이 통과하면 안 된다. case 원본이 실제 manifest에 있어야 하며 원본 캡처 이미지가 유효해야 한다. 동일 원본 트리의 여러 entrypoint를 독립 manifests로 지원한다. 입력 digest는 모든 검사 대상 입력/원본/기준 증거를 안정적으로 묶는다.
6. visual-evidence.json version=1에 input_digest, implementation_digest, cases를 둔다. case는 id, url, viewport, capture {path,sha256}, result pass|failed|unverified, optional media 관찰 포인터를 가진다. 비교 산문은 visual-check.md에만 둔다. scope와 검토 문서 존재/hash도 확인한다. original capture와 implementation capture의 동일 파일(경로/하드링크) 복용은 거절한다. 서로 독립 생성한 파일의 동일 해시는 완전 일치 가능성이 있어 단독 실패 근거가 아니다. 실제 생성 여부는 독립 감사가 원문 trace로 확인한다.
7. 구현 digest는 web/ 파일 경로+bytes(새/삭제 포함)와 host_files를 포함한다. 닫힌 제외는 __pycache__, *.pyc, *.pyo, .pytest_cache, .mypy_cache, .ruff_cache, .DS_Store뿐이다. 임의 exclude는 없다. fingerprint가 증거 digest를 자동 교체하지 않도록 한다.
8. visual: inputs 재검사·digests·정확한 case 집합/viewport·유효 캡처·모든 pass를 요구한다. 코드만 green인 경우 시각 완료를 통과하지 않는다.
9. media 요구는 id, kind image|video, environment, endpoint, identity_pointer, source_pointer(JSON Pointer)를 갖는다. visual 대응 행은 requirement_id, response {path,sha256}, browser {path,sha256}. response JSON: observed_at, environment, endpoint, status, body. browser JSON: observed_at, current_src, status, loaded, video일 때 playback_start/playback_end. 실제 response body에서 identity/src를 찾아 src=current_src, 환경/endpoint 일치, 각 2xx, loaded=true, video의 유한한 시간 증가를 확인한다. media 목록 누락/추가/중복/불일치를 실패시킨다. 요청 자격증명은 기록하지 않으며 서명 URL 포함 raw 증거는 공개 저장소에 커밋하지 않도록 계약에 명시한다. JSON Pointer 및 시간의 합리적 형식은 작은 명확한 계약으로 문서화한다.
10. backstop --design-build <dir>는 기존 26개 의미/번호를 유지하면서 visual 검사 exit를 합류한다. --only가 design gate를 끄지 않는다. 인자가 없으면 시각 무관 기존 사용은 동일하다. missing build 입력을 발견으로 반환한다.
11. 계약 reference에 정확한 JSON 예시와 실행 순서, 여러 manifest 처리, 제한과 exit 의미를 적는다. 다음 과제에서 그대로 호출한다.
12. 미러 동기화, 필요한 fixture 및 make verify-web 실행, diff 자기 검토, commit, report.

필수 검증 쌍: 정상 정적 의존성+캡처, image-only, 여러 entrypoint; 필수 import 삭제·inline import 삭제·문자열 가짜 import·검출된 동적/bare module; stale HTML/hash·의존성 행 삭제·원본 render 없음; 빈/중복/누락 case·다른 viewport·실행 후 web 추가/수정/삭제·pycache 무효화 없음; media API 실패/없는 identity/다른 src/재생 정지/샘플 대체 및 정상 응답 대응; 기존 backstop clean인데 design fail. 스키마를 그대로 복사한 헛단언을 피하고 실제 fixture bytes를 독립 변이한다.

Report: 변경/정확한 CLI와 schema path/테스트 명령·결과·반례 red 근거/우려/commit. Task 2가 소비할 인터페이스를 명확히 남긴다.

## Task 2: Coordinator와 네 역할의 원본 인계·게이트 계약 연결

Task 1의 design-evidence.md가 기계 인터페이스 정본이다. spec 마지막 확정 계약과 Global Constraints를 적용한다. 역할별 현재 파일/호출 문구를 실제로 대조한다.

Files: dddjango-web/commands/dddjango-web.md, agents/{design-architect-web,design-review-web,coder-web,discipline-reviewer-web}.md, skills/implementation-ui/{SKILL.md,references/final.md}; 필요한 경우 REQUEST_GUIDE.md의 완료 설명만 최소 변경. 대응 codex-dddjango-web Coordinator/role/SKILL/reference/guide 미러.

Steps:
1. 원본 소스/렌더·구체 승인과 구조/동작 명세의 역할을 분명히 하고 architect가 외형을 다시 근사 명세로 결정하는 전달 경로를 제거한다. 새로운 source 값은 출처 등록, 슬라이스 밖 변경은 소유자 슬라이스 재개로 처리한다.
2. design-input/visual-evidence를 산출물 위치/직접 쓰기 허용/실제 dispatch 목록에 넣는다. design-evidence.md를 최초 준비/검증 시 읽고 실제 CLI를 사용하도록 연결한다. 각 역할에 entrypoint·manifest·원본 captures·구체 승인 출처를 직접 전달하며 최종 감수는 raw media/browser 증거도 받는다.
3. G0 ready 직전 독립 design-review-web의 입력범위 모드로 사용자 scope/원본 상태/viewport와 cases 전수성 확인 후 inputs 게이트를 실행한다. G1 동작 계약이 추가 case를 발견하면 보완/재검토한다. 목록 축소는 구체 범위변경 근거/재검토를 요구한다.
4. 시각 슬라이스·재개·수정 진입의 inputs freshness, G2/마무리 final backstop --design-build, 독립 시각 감사 후 변경 시 영향 범위 재검증·재감사를 명시한다. 코드/dataset-only slice에 premature visual을 요구하지 않는다. 시안 대상 trivial은 증거재사용+영향확인 또는 자료 부재 시 modify로 전환한다. 시안 없음은 비적용이다.
5. unverified 사용자 수락 문구가 verified/시안 충실 완료를 허용하는 모순을 제거한다. 일반 G0/G1 승인과 기존 권한은 보존하되 이미 사용자가 승인한 범위의 재질문을 강제하지 않는다.
6. API 자산은 사용자가 요구한 실제 환경 응답과 브라우저 요청·재생으로 확인한다. 임시 DB seed·샘플은 격리 기능 test에만 사용하고 실제 사용자 프리뷰로 전환하지 않는다. 실패하면 해당 범위를 blocked/unverified로 남기고 필요한 외부 조건을 구체 보고한다.
7. 코드 grep checker나 tokens count·스크린샷 파일 존재는 fidelity 통과 근거가 아님을 완료 보고에 반영한다. 독립 reviewer가 모든 요구 case와 복합/자식 효과, 실제 media 증거를 직접 본다. JSON hash 생성만으로 검증을 새로 한 척 하지 않는다.
8. 의미/byte 미러 검증 및 make verify-web, diff 자기 검토, commit, report. 단순 문구 존재 테스트를 늘려 의미 검증을 대신하지 않는다.

Report: 역할별 실제 호출 연결, 기존 모순 해소 위치, 검사 및 미러 결과, commit, 우려.

## Task 3: 실제 native Coordinator 평가와 최종 통합 검증

Task 1/2 승인 뒤 실행한다. 기존 사용자의 앱·서버·브라우저 profile·DB를 건드리지 않는 독립 temp 앱에서 Claude/Codex 각각 Coordinator 전체를 실행한다. 역할만 수동 호출한 하네스는 전체 실행 근거가 아니다. 평가자는 산출물을 손수 고쳐 통과시키지 않는다.

Files: 직접 필요한 workspace/eval/web-design-source-integrity/ 평가 프로토콜·비밀 없는 결과/trace 요약. 큰 원본·raw CLI trace·signed URL·DB는 task temp에 둔다. 필요하면 재현 가능한 작은 harness만 저장한다.

Steps:
1. 원본을 그대로 전달하는 정상 다단계 fixture와 누락/오염 fixture, 미디어 실패 case의 기대값을 실행 전에 동결한다. 기존 실제 사용자 디자인의 수집 실패도 음성 입력으로 포함한다. 외부 폰트404 등 원본 접근 문제가 있으면 그대로 실패로 기록하며 평가용 복사 원본을 몰래 바꾸지 않는다. 정상 통제 fixture 성공과 실제 디자인/실영상 성공을 구분한다.
2. 실제 CLI 로그인/버전·플러그인 로드/네 역할 사용 가능·격리 browser 경로를 확인한다. Claude --plugin-dir로 /dddjango-web:dddjango-web, Codex의 실제 skill registry로 $dddjango-web를 실행한다. scope와 단계 진행은 평가 계정이 사전 승인하되 외형 변경·샘플 교체를 허용하지 않는다. 역할 subagent 호출과 gate CLI 실행을 trace에서 확인한다.
3. 정상 case에서 범위 전수성·직접 원본 인계·실제 원본/구현 browser·모든 단계·복합효과/자식효과·새 정확 token·검사 결과를 독립 확인한다. 대조를 정답값 prompt에 나열하지 않고 원본을 보고 달라진 점을 구현하도록 요청한다.
4. 누락/오염 입력은 ready 이전에 멈춰야 한다. 목록부터 1단계만 축소한 증거와 API 실패를 sample로 덮으라는 압력은 독립 리뷰/Coordinator가 받아들이지 않아야 한다. 실패한 required gate 이후 구현/완료 진행이 있으면 플러그인 회귀로 보고한다.
5. 현재 실제 media API는 인증 오류다. 실영상 통합 성공으로 보고하지 않는다. 플러그인이 실패를 정확히 막는 실행은 검증할 수 있으며 사용자 인증을 임의 설정하지 않는다. 실제 API 정상 통합 자체는 이 플러그인 수정의 필요 성공 주장에 포함하지 않는다.
6. 발견되면 원인에 해당하는 현재 과제 범위만 수정 implementer로 되돌려 필요한 re-review/재실행한다. 출력 앱을 고치는 것으로 통과하지 않는다.
7. 독립 whole-branch review와 필요한 make verify 및 strict plugin validate 완료. 봉인 변경이 필요하면 최종 대상만 재발행 후 make verify 처음부터 실행한다. 마지막 로그만 완료 근거로 사용한다.
8. clean isolated checkout을 GitHub main 최신과 일치시키고 make release-web으로 patch 릴리즈. remote tag/release/manifest 버전을 확인한다. primary는 WIP 보존이 입증되는 방식으로만 동기화하고 기존 WIP 571개 sha 목록과 대조한다. 배포 차단 시 정확한 조건을 보고한다.

완료 보고는 정상 전체 실행·음성 차단·실제 외부 미디어 제한·배포 버전·검사 범위를 분리하고 Serena 생략 이유를 포함한다.
