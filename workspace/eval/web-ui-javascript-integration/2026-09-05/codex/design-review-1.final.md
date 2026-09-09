**APPROVED — 화면 관점 이상 없음.** [design.md](/private/tmp/dddjango-web-js-integration-20260905/codex/app/design.md)의 요구·화면 분해·라우트·UI 수명·파일 목록이 동결 요구사항과 현재 배포본 규율에 부합합니다. Blocker, important, nit 발견 모두 0건입니다. 이 판정은 **설계 승인**이며 구현 및 브라우저 검증 통과를 뜻하지 않습니다.

검토 기준은 앱 내부의 지정된 `dddjango-web-design-review-web/SKILL.md`, `architecture-web` 본문 및 `references/final.md`, `discipline-web-houserules` 본문 및 `references/final.md`, `references/undecidable-web.md`입니다. 설치된 플러그인 캐시나 다른 리뷰 결과는 사용하지 않았습니다. `evaluation-requirements.md`, `evaluation-oracle.md`, 현재 호스트·base·design_system을 직접 대조했습니다.

| 검토 항목 | 판정 및 근거 |
|---|---|
| 화면 분해·영역 귀속 | 명세 §§1–3은 승인된 새 `lab` 영역에 `ui_lab` 하나를 배치합니다. 서버 revision·표시값 조립이 VM의 실제 책임이고, 다섯 section은 같은 화면의 fixture 맥락과 전달된 state를 렌더합니다. 로컬 UI 상태 때문에 별도 VM을 만들거나 조각을 view로 과승격하지 않습니다. `architecture-web` §§2–5, `undecidable-web` §§1–4에 부합합니다. |
| view 수동성·state | §3의 view는 고정된 페이지/fragment 진입점 선택, VM 호출, render만 담당합니다. revision과 패널 표시값은 VM에서 조립하고 frozen dataclass로 전달합니다. URL 기본값에 따른 렌더 진입점 선택은 업무·표시 판정의 이전이 아닙니다. `architecture-web` §3에 부합합니다. |
| 라우팅·계약·격리 | §3의 페이지 1개와 fragment 3개는 실제 Django GET HTML 렌더 경로이며 영역 `urls.py`가 path/name을 소유합니다. 선언은 이름으로 역참조하고 static HTML을 endpoint로 사용하지 않습니다. 업무 API·client·response model은 0개로, 승인된 OpenAPI/server-contract 부재와 일치합니다. BC 내부 import나 가정한 업무 endpoint가 없습니다. `architecture-web` §§1,4,6,7에 부합합니다. |
| 파일 목록·골격 | §9의 **신규 20개, 수정 1개** 목록이 내부적으로 일치합니다. 새 영역의 `urls.py`·빈 `widget/`, 화면의 네 종류 폴더와 필요한 패키지 마커, 삼총사·페이지 및 section 접두가 갖춰져 있습니다. 제출 없는 로컬 입력에 form/client/test 파일을 만들지 않는 결정도 일관됩니다. 하우스룰 §§1–5에 부합합니다. |
| design_system·시안 조건 | 실제 component 디렉터리는 `.gitkeep`만 있어 재사용 누락이 없습니다. §8은 기존 토큰 9개를 정확히 연결하고 새 토큰·component·asset·motion runner를 요구하지 않습니다. 시안·motion notes·render audit가 없는 승인된 자체 설계이므로 관련 충실도 대조는 해당 없음입니다. `architecture-web` §8에 부합합니다. |
| 행위·검증 연결 | §§5,10은 요구 1–6 및 I1–I12를 담당 기능, 대상, 자원, 실패·키보드·정리 조건과 연결합니다. 실제 HTTP와 응답 revision, 반복 swap, 양방향 인스턴스 격리, 실제 URL 생성·해제 계측, decode 실패·지연, script load 횟수를 요구합니다. 정적 검사나 합성 이벤트를 브라우저 성공 증거로 대체하지 않습니다. |

수명 계약은 다음 세 경우를 명확히 구분하므로 승인합니다.

- **전체 root 교체:** 명세 §§4,6은 제거되는 패널의 preview owner만 폐기하고 URL을 한 번 해제하며, 진행 중 decode를 무효화합니다. 새 root는 다시 활성화하고 이웃 패널은 보존합니다.
- **종속 child 교체:** preview owner는 유지하지만 실제 body/input/output 의존성이 제거되므로 기존 자원을 해제하고 새 body에 연결합니다. 유지되는 password와 note는 건드리지 않습니다.
- **독립 child 교체:** note는 의존성 목록에 없습니다. 제거 요소가 owner 또는 실제 의존 노드를 포함하는지 확인하는 정리 조건 때문에 note 교체는 URL 해제·세대 변경·preview 초기화를 일으키지 않습니다. 진행 중인 유효 decode도 보존됩니다.

§6의 반복 활성화, 현재 자식 조회, WeakMap record·generation·노드 동일성 검사는 중복 효과와 오래된 비동기 완료를 막는 설계 근거로 충분합니다. 이는 `architecture-web` §1의 UI 동작 계약 및 하우스룰 §5⑤의 승인된 UI 실행 경계와 일치합니다.

**S1: ACCEPTED.** `password_visibility.js`와 `image_preview.js`는 명시적으로 요구된 로컬 UI 동작입니다. 값·파일을 전송하거나 업무 판정을 수행하지 않으며, 기능당 한 파일로 제한됩니다.

**S3: ACCEPTED.** 도움말은 native `details`/`summary`에 배정되어 있고 disclosure JS가 없습니다. 커스텀 기능 스크립트를 차단한 상태에서 키보드 동작을 확인하는 I10 계약도 유지됩니다.

**S2: REJECTED.** 제안된 추가 JS의 사용자 저장 권한 판정, 최종 결제금액 계산, 발명한 업무 저장 API 호출은 모두 허용되지 않습니다. 권한·최종 금액·저장 결정의 소유자는 서버 업무 계층이며, 브라우저 임시 UI 상태의 책임이 아닙니다. 실제 업무 계약이 필요해지면 서버 계약을 먼저 마련해야 하고, web의 계약 소비는 `client/` 경계를 따라야 합니다. 근거는 `architecture-web` §§1,6 및 하우스룰 §5①②⑤입니다. 이 반례는 평가만 했으며 설계에 추가하거나 파일을 변경하지 않았습니다.

호스트 교정 이력도 보존되어 있습니다. 명세 §1은 초기 prefix 설정 이후 Coordinator가 교정한 현재 `STATICFILES_DIRS`를 기록하고, §7은 실제 base와 일치하는 `web/htmx/htmx.min.js`, `web/js/...`, `web/css/...`, `design_system/foundation/tokens.css`를 사용합니다. 페이지 전용 외부 classic defer 스크립트는 페이지의 범용 `scripts` block에서 한 번 로드하며 fragment에는 실행 태그가 없습니다.

이번 역할은 읽기 전용 검토만 수행했습니다. 파일 작성·수정, Git 조작, 에이전트 생성, Django check·backstop·HTTP·브라우저 실행은 하지 않았습니다. 공급된 baseline과 HTMX 출처/hash는 Coordinator 증적으로 구분했으며 독립 실행 결과로 주장하지 않습니다.

Serena: skipped — 명세와 호스트 파일의 읽기 전용 대조에 기본 도구를 사용했습니다.