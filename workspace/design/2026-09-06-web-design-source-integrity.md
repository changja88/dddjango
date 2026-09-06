# 웹 시안 원본 전달과 검증 완료 판정 설계

상태: 독립 적대 검토 P1/P2 반영 및 재검토 완료 — 구현 진입 승인. 외부 적대 검토 결과는 평가 기록에서 보존한다. 사용자 승인 범위는 설계·검토·구현·실제 플러그인 실행·최종 검증·dddjango-web 배포다. 문제 존재/원인 조사는 재수행하지 않는다.

## 근거와 성공 조건

feat/web-auth-3 `6d91b765`에서 새 HTML 해시 3f744443과 source-manifest의 구 해시 58c64fe5가 불일치한다. source_ready=false·필수 JSX/DS 번들 부재·원본 렌더 부재인데 design_status=ready였다. D14 근사와 D29 영상 비율 재해석이 원본을 대체했고, 로고 효과를 토큰/슬라이스 밖이라 생략했다. 404 영상과 1단계만 확인한 뒤 implementation_visual=verified였으며 사용자 프리뷰에는 임의 꽃 샘플을 넣었다. 기존 규정은 이미 금지하지만 실행 경로와 증거 판정이 끊겼다.

dddart feedback-015의 교훈: 값·자산의 정확한 전달은 유지하되 배치 정보를 손실적인 중간 명세로 재작성하지 않는다. 원본 소스로 구조/값을 읽고 대응 원본 렌더로 실제 외형을 대조한다. 검사 성공은 검사한 축만 보장한다.

성공: (1) 원본 누락/해시 혼합/렌더 부재가 준비 완료를 막는다. (2) 원본 효과 생략·시각 재해석·임의 자산 대체가 허용되는 발주/검증 경로가 없다. (3) 증거가 없는 범위와 변경 후 낡은 증거는 verified가 아니다. (4) 완전한 정상 입력·출처 있는 신규 토큰·명시 승인된 변경은 통과한다. (5) 실제 Coordinator부터 실행한 결과로 운영 효과를 확인한다.

## 범위와 소유

변경: dddjango-web/ 및 codex-dddjango-web/ 대응 미러, 필요한 workspace 계획·평가 기록. backend dddjango와 ontology 규칙, 실제 사용자 앱 코드는 수정하지 않는다. 원본 primary WIP와 활동 중 앱 서버/DB를 건드리지 않는다. 기존 역할 4개를 유지한다. 별도 화면 DSL/레이아웃 IR·범용 워크플로 엔진·비전 점수 절대 게이트는 만들지 않는다.

Coordinator는 원본·렌더·요구/승인 근거 및 검증 증적을 무손실 전달한다. architect는 코드 분해·계약·상태·상호작용을 설계한다. 외형을 다시 산문/CSS 목표로 결정하지 않는다. 원본과 다른 외형이 필요하면 원본 값→변경 값→요구/승인 출처를 특정한 이탈만 가능하다. 코더는 명세의 구조/동작과 원본 외형을 각각 직접 소비한다. 감수는 구현자의 요약만 보지 않고 원본/구체 승인/실제 결과로 판단한다.

토큰은 원본 값을 운반하는 수단이다. 풀 밖의 정확한 원본 값은 출처를 붙여 등록한다. 슬라이스 밖 수정 필요는 Coordinator가 소유 파일 슬라이스를 다시 열어 처리하며 효과 생략으로 해소하지 않는다. 컴포넌트 전체 복합 효과·자식 층·상태 덮어쓰기를 실제 적용과 대조한다. 구조 치수/등가 구현을 닫힌 CSS 문법 표로 제한하지 않는다.

## 결정적 게이트 초안

표준 라이브러리 도구 `scripts/check_design_evidence.py`를 추가한다. 입력은 명시적 build dir와 project root이며 `--phase inputs|visual`로 구분한다. exit 0=해당 범위 증거 정합, 1=사용/내부 오류(미실행), 2=결함/부족한 증거. 네트워크·브라우저 실행을 흉내 내지 않고 로컬 증적을 검증한다.

`design-input.json`은 구현 전에 Coordinator가 원본 수집/관찰에서 작성하는 작은 입력 목록이다. version=1, reference_root(기본 design-ref), source_manifest(기본 source-manifest.json), cases(비어 있지 않은 목록)를 갖는다. 각 case는 고유 id, 화면 식별, 상태, viewport=[width,height], 원본 렌더 path/sha256, 원본 entrypoint의 sha256을 가진다. 이 파일은 원본을 재서술하는 레이아웃 명세가 아니라 어떤 화면/상태를 대조하는지의 목록이다. 이미지 단독 입력도 image entrypoint와 실제 원본 이미지를 사용한다. 원본 렌더를 얻을 수 없으면 구현 입력 미준비이며 구현 화면을 원본 증거로 만들지 않는다.

inputs 검사:
- manifest 스키마/entrypoint/비어 있지 않은 files, source_ready=true를 요구한다. 모든 파일의 경로 confinement·실재·크기·sha256·기록된 status를 실제 바이트와 대조한다. bool 선언만 신뢰하지 않는다.
- 원본 HTML/CSS/JSX에서 정적으로 발견 가능한 의존성이 manifest에 실제 포함되는지도 재검사해 행 삭제로 ready를 만들 수 없게 한다. 동적 참조는 원본 런타임 관찰로 해소해야 하며 무조건 무시 옵션은 없다. 정적 스캐너 오탐은 도구에서 근거 있는 좁은 수정으로 해결하고 실제 import 누락 검출을 유지한다.
- cases의 id/viewport/원본 entry 해시/렌더 파일 해시와 이미지 컨테이너 유효성을 검증한다. 같은 파일명에 다른 버전의 bytes가 섞이면 실패한다. 원본 렌더가 실제 해당 화면/상태인지의 의미 확인은 별도 사람/에이전트 대조임을 보고한다.
- 성공한 입력 전체를 canonical digest로 묶어 출력한다. 기록된 ready나 이전 실행의 digest는 검사 대체물이 아니다.

`visual-evidence.json`은 관찰 뒤 작성한다. version=1, input_digest, implementation_digest(현재 web/ 트리의 경로+bytes 전체), cases를 가진다. case는 design-input의 id, URL, viewport, 구현 캡처 path/sha256, result(pass|failed|unverified), observation(실제 대조·동작·차이·미검증의 근거), assets(정적 자산 로드·실제 미디어 연결의 관찰 자료)를 포함한다. 도구가 코드/원본 digest를 계산하는 `--fingerprint` 모드를 제공해 값 손작성 없이 파일에 기록할 수 있게 한다.

visual 검사:
- inputs 검사를 항상 다시 수행하고 digest를 대조한다. web 트리 변경(추가/삭제 포함)이면 기존 visual 증거는 stale이다.
- 모든 요구 case가 정확히 한 번 존재하고 URL/viewport/캡처가 실재·일치하며 result=pass인 경우에만 verified 근거가 된다. 누락/failed/unverified를 사용자 G2 승인의 대체 근거로 통과시키지 않는다.
- 이 검사는 증적 정합/범위를 확인한다. JSON의 pass나 screenshot 존재가 실제 충실도를 증명한다는 주장을 하지 않는다. 독립 원본 대조와 실제 브라우저 검증이 필수이며 최종 보고는 기계 정합과 시각 판단을 구분한다.

현재 backstop에 `--design-build <dir>`를 추가하여 동일 실패를 최종 코드 게이트에도 연결한다(기존 26 코드 검사 의미 불변). phase inputs는 시각 슬라이스 진입/재개 전, phase visual은 변경 범위 G2 직전과 마무리 직전 필수 실행한다. 실패 후 상태를 ready/verified로 직접 덮어쓰지 않는다. Coordinator의 gate 호출을 실제 native 실행 trace에서 검증한다. 플랫폼 외부의 강제 권한 격리가 없으므로 모든 도구 호출 자체를 생략하는 에이전트를 보안 경계로 막는다고 과장하지 않는다.

## 영상·자산의 별도 진실

실제 API 자산 요구는 키만이 아니라 사용자가 지목한 환경/계약과 연결한다. 사용자 프리뷰는 그 환경의 응답→선택된 자산→브라우저 요청/재생을 대조한다. 테스트 fixtures는 격리 기능 시험에 사용할 수 있지만 실제 자산 충족이나 사용자 프리뷰 근거로 바꾸지 않는다. API/인증 실패를 임시 DB seed·외부 샘플로 해소하지 않는다. 서명 URL은 만료할 수 있어 URL 영구 고정 대신 API 자산 식별·관찰 시점과 실제 요청의 대응을 확인한다. 자동 비교가 가능한 키·응답·브라우저 src와 나머지 의미/출처 확인 범위를 분리한다.

## 검증 및 순서

도구 반례: 필수 import 빠짐, stale HTML hash, 실패 행 삭제, 원본 render 부재/잘못된 hash, 빈 case/중복/다른 viewport, 현재 web 변경 후 낡은 증거, case 일부만 pass, 코드 checker clean인데 design gate fail. 정상 짝: 올바른 파일/의존성/렌더, 이미지 단독, 출처 있는 신규 토큰, 시각 무관 기존 backstop 실행. 의미 반례: missing source→근사, 정확한 원본 효과→슬라이스 밖 생략, 영상 실 API 실패→샘플로 대체, 승인된 프레임 변경→추가 비율 변경을 자동 승인처럼 취급.

1. 이 설계를 독립 적대 검토하고 필요한 수정을 반영한다.
2. 도구와 연결 규범을 구현하고 반례/정상 및 기존 픽스처를 확인한다.
3. 새 세션의 실제 설치 가능한 Claude/Codex 플러그인에서 Coordinator 전체 호출로 정상 입력과 불완전 입력을 실행한다. 평가자는 정답을 코더에게 흘리지 않는다. 역할을 외부 하니스로 수동 호출한 시험만으로 전체 실행을 대체하지 않는다. 생성 앱을 사후 손수 고쳐 통과시키지 않는다.
4. 실제 auth 디자인/영상 접근 가능성은 별도로 확인한다. 접근 불가를 샘플 재생으로 바꾸지 않는다. 평가 자료의 완전성과 실제 권한 제약은 분리해 기록한다.
5. 독립 최종 리뷰·make verify·manifest 검증·배포된 버전 확인까지 수행한다. 원본 primary WIP hashes를 유지한다.

## 적대 검토 반영 — 확정 계약 (위 초안과 충돌하면 이 절 우선)

1. **범위 확정**: Coordinator가 사용자 요구/승인 범위의 원문 포인터와 화면·단계·시각 상태·viewport case 목록을 만들고 design-review-web이 원본과 요구를 직접 읽어 누락을 독립 검토한다. G0 준비 검토의 가벼운 별도 모드로 수행하고 ready 전에 검토 파일을 보존한다. G1 UI 동작 계약이 범위를 더 발견하면 목록·원본 캡처를 보완하고 재검토한다. 이후 case 삭제/viewport 축소에는 구체 범위 변경 근거와 재검토가 필요하다. checker는 선언된 목록 정합만 보장한다.
2. **단계 적용**: has_design_screen이면 design_status=ready 직전 inputs 통과·독립 원본 렌더 확인이 필수다. 시각 구현/재개/수정 진입에 freshness를 재검사한다. 모든 시안 대상 최종 backstop 호출에는 --design-build가 필요하고 --only는 이 검사를 비활성화하지 못한다. 데이터만 진행한 슬라이스에는 visual을 요구하지 않는다. 시안이 걸린 트리비얼도 기존 산출물을 재사용해 영향 case를 검사하며 기존 자료가 없으면 수정 모드로 올린다. 시안 없음은 비적용이다. 미검증 수락으로 verified를 만들지 않으며 시안 충실 재현 완료는 visual+독립 감사 통과 전 불가다. 감사 뒤 코드 변경은 영향 범위 재검증·재감사 대상이다.
3. **정적 수집 경계**: HTML/CSS 리터럴 자원, x-import, ES 리터럴 import/export-from 및 inline module/script 리터럴 의존성을 지원한다. JS 문자열 내부의 가짜 import 오탐은 구문 맥락을 확인해 제거한다. 검출된 비리터럴 import/JSX 자원식/bare module은 미지원으로 차단한다. 이번 변경에서 범용 JS 실행/번들러/import-map/동적 관찰 해소 엔진은 만들지 않는다. 런타임에만 나타나는 자원은 원본 브라우저 관찰과 독립 감사가 담당하며 정적 폐쇄를 전체 런타임 폐쇄로 표현하지 않는다. 일부 스캐너 누락의 기계적 완전 검출을 약속하지 않는다. 정적 탐지 실패 행을 삭제해 ready로 만들 수 없다.
4. **증거 파일**: JSON은 식별·해시·증거 포인터·결과에 한정하고 비교 산문은 visual-check.md에만 둔다. design-input의 cases는 scope_refs를 갖고, 요구 파일과 독립 범위 검토 파일은 path/sha256 포인터로 묶는다. 원본 entrypoint는 case마다 path/sha256으로 manifest의 실제 파일과 연결한다. 여러 화면 원본은 각각 수집한 manifests 목록을 지원하며 임의 합친 한 manifest의 잘못된 entrypoint로 덮지 않는다. 원본 스크린샷과 구현 캡처는 같은 파일을 재사용하지 않는다.
5. **digest**: fingerprint는 값 계산/출력만 하고 어떤 증거 파일도 갱신하지 않는다. 구현 digest는 web/ 실행 입력의 경로+bytes(무추적 신규/삭제 포함), 추가 승인 host 파일 목록을 포함한다. __pycache__, *.pyc, *.pyo, .pytest_cache, .mypy_cache, .ruff_cache, .DS_Store만 닫힌 제외로 둔다. 임의 exclude는 없다. changed digest를 수기로 갈아 끼워 낡은 캡처를 새 증거로 부르는 것은 금지다. 바뀐 digest에서 유지할 기존 case도 독립 리뷰어가 영향 없음을 확인한 뒤 현재 관찰 회차로 재확정해야 한다.
6. **실제 미디어 최소 연결**: 필요한 case만 media 요구를 기입한다. 요구 id/kind(image|video)/environment/endpoint와 응답 내 asset identity·src의 JSON Pointer를 기록한다. visual의 대응 media 행은 실제 API 관찰 파일(path/sha256)과 브라우저 관찰 파일(path/sha256)을 가리킨다. API 관찰은 observed_at·environment·endpoint·HTTP status·body(실제 JSON 응답)를, 브라우저 관찰은 observed_at·current_src·HTTP status·loaded와 영상 playback 시작/끝 시간을 담는다. checker는 요구 환경/endpoint, 2xx, 응답의 identity 존재, src와 current_src 일치, loaded=true, video time 증가를 확인한다. identity를 브라우저에 별도 넘겨 선언하는 대신 실제 응답에서 선택한 identity와 src를 출력해 독립 감사가 원문과 비교한다. 요청 credentials/headers는 저장하지 않는다. 민감한 서명 URL/응답 원문은 로컬 비공개 증거로 보존하고 공개 평가에는 비밀 없는 요약만 남긴다. 실행 도구/환경의 진위나 영상 내용을 JSON만으로 증명하지 않는다. HTTP 실패·자산 불일치·재생 미확인은 verified 불가이며 API 오류를 샘플/seed로 대체하지 않는다.
7. **실제 인계**: Coordinator의 모든 역할 dispatch 인자 목록에 원본 entrypoint·source-manifest·원본 렌더·design-input·구체 이탈 승인 출처를 명시한다. 최종 감수는 visual-evidence·visual-check·API/브라우저 원문 증거와 구현을 직접 받는다. architect의 명세는 분해/동작/계약이며 외형 재서술을 전달 우선순위로 끌어올리지 않는다.

검토 발견과 대응: P1 범위 축소→1, P1 임의 영상→6, P1 늦은 게이트→2, P1 스캐너 전수성 과장→3, P2 digest 부산물/갱신→5, P2 인계/중복→4·7. 이 결정은 완전한 보안 격리나 시각 일치의 기계 증명이 아닌 실행 계약+결정적 정합 검사+독립 실제 관찰의 조합이다.
