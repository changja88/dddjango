# 코퍼스 경계 검토와 후속 통합 항목

2026-09-05. 이번 결과는 신규 `implementation-javascript`의 작성·검증이다.
기존 Coordinator·agent·스킬 금지 조항·백스톱·매니페스트·master 문서는 수정하지 않았다.

## 이번 스킬의 소유권

| 관점 | 판정 |
|---|---|
| 분류 | implementation: 브라우저 이벤트·DOM·자원·비동기 표기와 검수 기준 |
| architecture와의 관계 | 서버/브라우저 책임 결정·화면 분해·swap 계약을 새로 소유하지 않음 |
| discipline과의 관계 | 기능 파일 단위는 승인된 프로젝트 결정을 소비; 파일 트리·일반 클린코드의 정본을 대체하지 않음 |
| implementation-ui와의 관계 | Django/HTML/HTMX/CSS의 표기를 복제하지 않고 UI JS 메커니즘만 담당 |
| agent와의 관계 | 향후 coder-web이 구현, discipline-reviewer-web이 감수할 지식. 신규 agent 없음. 이번에는 주입 변경 없음 |
| 현행 금지와 공존 | SKILL 진입 조건이 기존 규칙의 예외를 만들지 않음. 승인 명세·프로젝트 규칙에 충돌이 있으면 해당 구현 보류 |

## 후속 통합 때 함께 바꿔야 할 항목 — 이번에는 미적용

| 대상 | 현재 확인한 사실 | 필요한 통합과 완료 기준 |
|---|---|---|
| `skills/architecture-web` | HTML+HTMX+CSS만 허용, JS는 vendored 2종. 표시 판정은 VM 유일 | 서버가 결정하는 표시 데이터와 브라우저의 임시 UI 상태를 구분. 설계자가 JS 필요성·root·swap 경계를 명세할 수 있어야 함 |
| `skills/implementation-ui` | 커스텀 JS·inline script·새 JS 금지, 기존 vendored 경로 | 외부 기능 JS 로드와 HTML/JS 데이터 전달을 허용된 계약으로 표기. HTMX 속성·CSS·서버 코드는 계속 여기서 소유 |
| `skills/discipline-web-houserules` | 현행 파일트리·JS 닫힌 목록 | master에서 연결한 새 웹 트리와 기능당 한 파일을 실제 규범으로 정합화. 기존 fonts/files 착지·motion 러너 위치까지 빠짐없이 판정 |
| `agents/coder-web.md` | 메커니즘 유지 규칙 안에 모든 커스텀 JS 금지 명시 | 승인 UI JS를 새 스킬로 구현할 수 있도록 기술 범위를 좁혀 수정. 기존 메커니즘 임의 변경 금지는 유지 |
| `agents/discipline-reviewer-web.md` | D12 우회 감수, 새 JS 스킬 미주입 | 새 스킬 주입 후 UI 수명·안전한 DOM·서버 책임 침범을 감수. 정상 최소 위임 구현을 프레임워크 부재로 반송하지 않음 |
| 설계 agent 2종 | 기존 architecture 스킬을 통해 기술 제약 소비 | 설계·리뷰 입력에서 JS 동작 근거와 교체 경계가 빠지지 않게 확인. 코드 작성 책임은 넘기지 않음 |
| Coordinator | 기존 htmx vendoring·host 배선 담당. unpkg 설치 URL은 버전 미고정이며 해소 버전을 기록 | 기능 스크립트 로드 위치·의존 순서·벤더 경로 및 실제 버전 계약 정합화. 자동 업그레이드나 새 loader 발명은 별도 요구 없이 하지 않음 |
| `scripts/src/common.py`, `check_structure.py`, `check_purity.py`, `check_naming.py` | STATIC_DIRS에 htmx 없음, vendor는 static/js, WP1 새 JS 금지, WP2 vendor 외 script 금지 | 허용 경로·외부 기능 script와 금지할 실행 채널을 명시적으로 구분. 정상 UI JS 통과/inline 우회 차단/업무 경계 감수 사례를 검증. 검사 강도만 낮춰서는 안 됨 |
| 백스톱의 능력 경계 | 파일/태그/경로 검사는 결정적이나 모든 JS 업무 의미를 증명하지 못함 | 기계 검사 가능한 구조와 agent가 검토할 의미를 구분. 단순 키워드 탐지를 업무 로직 부재의 완전한 증명으로 쓰지 않음 |
| `json_script`와 동적 HTMX 조각 | 비실행 데이터 script도 현재 WP2와 충돌할 수 있음. 새 트리는 static/htmx에 HTML 조각을 둠 | JSON 데이터 블록 허용 여부를 실행 script와 구분. 동적 HTML은 Django 렌더·권한·CSRF·context·기존 section 소유와 정합해야 함. 파일이 static에 있다고 브라우저가 미렌더 템플릿을 직접 가져오게 하지 않음 |
| Codex 미러·검증·배포 | 신규 스킬만 양쪽 작성, 기존 실행 계약 그대로 | 향후 변경한 소유 문서·검사기를 양 런타임에 반영하고 실제 파이프라인 평가. 릴리즈 요청 시 make release-web 사용 |

위 항목은 충돌이 없다는 선언이 아니라, 런타임 전환에 필요한 알려진 연결 지점이다.
현재 설치 플러그인에서 새 UI JS가 통과한다고 주장하지 않는다.

## 독립 검토와 과적합 점검

- 독립 검토자 `js_skill_review`는 신규 본문·reference·조사와 기존 4개 스킬·4개 agent·Coordinator의 관련 부분을 읽었다. 적용 조건에 의한 권한 보존과 책임 분리는 통과로 판정했다.
- 중요 발견 1건: 비밀번호 예제의 root 내부 교체 뒤 새 버튼 활성화/input 상태 동기화 누락. 실제 브라우저 P5·P6에서 재현했다. 전달 노드의 현재 소유 root도 수집하도록 수정했고, 동일 검사와 독립 재검토에서 해소됐다.
- 파일 미리보기만 정답 예제로 복제하지 않았다. 레퍼런스 예제는 비밀번호 표시이며 별도 적용 과제는 복사 안내다. 자원 없는 기능에 cleanup 틀을 강제하지 않는다.
- 기본 HTML로 충분한 사례, 서버 업무·권한 판정, 기존 JS 금지와의 충돌은 별도 적용자의 판단으로 확인했다. 기능마다 새 UI·공통 프레임워크·서브에이전트를 만드는 지시는 없다.
- 참고 문헌의 표준 사실과 master/플러그인의 정책을 구분했다. 한 기능 파일·UI JS 범위는 프로젝트 결정이며 전 세계 JS 작성법으로 보편화하지 않았다.

실행 결과와 한계는 [평가 보고서](../../../eval/implementation-javascript/2026-09-05/report.md)에 기록한다.
