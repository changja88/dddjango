# dddjango · dddjango-web 작업 요청 가이드 설계 명세

- 날짜: 2026-09-05
- 상태: 구현 기준선 — 같은 날 적대적 리뷰의 정보 소유권 교정 반영
- 범위: 사용자 작업 요청 가이드와 진입 문구 재설계, 기존 배포·미러·검증 계약 보존
- 실행 계획: `workspace/plan/2026-09-05-plugin-request-guides-revision-plan.md`
- 비범위: Coordinator·agent·skill의 런타임 규범, 온톨로지, reference corpus, 기존 파이프라인 결함 수정

이 명세가 재설계의 현재 기준선이다. 이전 구현 계획
`workspace/plan/2026-09-05-plugin-request-guides-plan.md`는 역사 기록으로 남기며, 그 안의
gate·evidence·검수 행렬 요구를 현재 사용자 가이드의 수용 기준으로 사용하지 않는다.

## 1. 목적

사용자가 원하는 제품 결과와 이미 정한 필수 규칙을 전달하면, 플러그인이 프로젝트를 조사하고
필요한 질문·설계·구현·검증을 수행하도록 요청 가이드를 구성한다. 사용자가 플러그인의 내부 운영법을
배우거나 요청 전에 자료를 분석해야 시작할 수 있는 문서로 만들지 않는다.

- `dddjango`: 사용자가 업무 변화·불변식·실패 결과·보존할 외부 동작을 설명하고,
  플러그인이 DDD 설계와 TDD 구현을 맡는다.
- `dddjango-web`: 사용자가 구현할 화면, 기준 시안의 정확한 대상, 필수 상태와 폭,
  의도적인 차이를 설명하고, 플러그인이 시안 분석·충실도 확인과 MVVM/HTMX 구조를 맡는다.

한 기능이나 한 화면에서 원하는 변화만으로 시작할 수 있다. 제품 결정을 아직 못 했거나 자료의
위치를 모르는 상태도 정상적인 시작이다. 플러그인이 조사할 수 있는 사실을 먼저 찾고, 사용자가
결정해야 하는 미확정 결과를 질문한다. 처음부터 모든 입력을 확정하게 하지 않는다.

가이드의 성공은 다음으로 판단한다.

1. 사용자의 핵심 요청에 관찰 가능한 결과, 이미 정한 필수 규칙, 보존·변경·제외 범위가 담긴다.
2. 알려진 자료 위치는 선택 정보로 분리되어, 자료 준비가 시작 조건이 되지 않는다.
3. 조사·agent/skill 선택·아키텍처·테스트 전략·검증 방법의 책임이 플러그인에 있다.
4. 두 플러그인의 전문성을 살리면서 사용자가 내부 게이트나 상태 토큰을 지시하지 않는다.
5. 운영 한계는 짧은 완료 참고로 설명하고 발주 양식으로 전환하지 않는다.

## 2. 설계 근거와 책임 경계

### 2.1 배포와 정본 구조

- Claude 설치 단위는 `dddjango/`, `dddjango-web/`이고 Codex 설치 단위는 각각
  `codex-dddjango/`, `codex-dddjango-web/`이다.
- 루트 `README.md`, `docs/`, `workspace/`는 개별 플러그인의 git-subdir 설치본에 포함되지 않는다.
- 따라서 루트 문서 한 개나 형제 플러그인 상대 링크만으로는 설치 후 가이드를 보장할 수 없다.
- `dddjango`의 runtime reference 미러는 `corpus_mirror_sync.py`의 대상이지만, 사람용 요청 가이드는
  그 코퍼스와 역할이 다르다.
- Coordinator 본문은 `dddjango`에서는 graph-owned 규범이며, 단순 링크처럼 보이는 변경도
  온톨로지·렌더·rulepack 변경이 된다. 이번 목적에는 필요하지 않다.
- 설치본 루트의 임의 Markdown은 자동으로 열리지 않는다. 네 plugin manifest의 사용자-facing
  homepage는 각 정본 가이드의 공개 GitHub URL을 가리키고 repository는 저장소 루트로 유지한다.
  README 발견 경로와 manifest 발견 경로를 모두 제공하되 자동 노출을 과장하지 않는다.

### 2.2 dddjango의 책임

기존 Django 프로젝트의 한 기능이 대상이다. 업무 규칙과 보존할 결과의 결정은 사용자에게 있고,
기존 코드·문서·테스트 조사, 도메인 경계, API/DB 설계, 필요한 테스트와 검증의 판단은 플러그인에 있다.
자료 사이에 차이가 있으면 플러그인이 이를 조사해 제품 선택이 필요한 질문으로 바꾼다.

요청자는 자료의 권위, 기존 coverage, 테스트 입장, 영역 소유권을 분석해 제출하지 않는다.
중복 실행·동시성·외부 효과가 제품 결과를 바꾸는 경우에도 기대 결과를 설명하며, 구현 수단과
검증 방법은 플러그인이 정한다. 미확정 업무 규칙은 임의로 확정하지 않고 질문한다.

### 2.3 dddjango-web의 책임

기존 Django 프로젝트의 web 표현계층 한 화면이 대상이다. 사용자는 무엇을 보고 어떤 결과를
원하는지 알려 주며, 시안 출처의 처리 가능성, 접근 조건, 추출·비교 방법, API 계약과 표현 구조는
플러그인이 조사한다. 원본의 시각적 의도는 보존하되 구현은 플러그인의 MVVM/HTMX 규율을 따른다.

시안이 있음, 시안이 없음, 시안이 있으나 접근할 수 없음은 모두 정상적인 시작이다. API 위치 미확정도
시작을 막지 않는다. 플러그인은 제공된 자료로 가능한 일과 더 필요한 제품 결정을 구체적으로 설명한다.
화면에 필요한 백엔드 동작이 없으면 그 결과와 범위를 밝혀 별도 `dddjango` 작업으로 연결한다.

시안 충실도가 핵심이라는 점은 유지한다. 다만 출처 종류별 자동화 능력, 상태 재현·측정 계획,
검수 행렬을 사용자가 작성하도록 요구하지 않는다. 자동 측정의 범위와 남은 시각적 확인은
플러그인이 결과에서 설명한다.

## 3. 문서 배치와 소유권

두 개의 논리 문서를 네 개의 물리 파일로 배포한다.

| 논리 문서 | 정본 | byte 동일 미러 |
|---|---|---|
| dddjango 작업 요청 가이드 | `dddjango/REQUEST_GUIDE.md` | `codex-dddjango/REQUEST_GUIDE.md` |
| dddjango-web 작업 요청 가이드 | `dddjango-web/REQUEST_GUIDE.md` | `codex-dddjango-web/REQUEST_GUIDE.md` |

규칙은 다음과 같다.

- Claude 설치본의 파일이 정본이다.
- Codex 파일은 배포 플랫폼 문법만 따로 갖는 의미 미러가 아니라 **byte 동일 미러**다.
- 한 문서 안에 Claude와 Codex의 시작 문법을 함께 적어 어느 설치본도 독립적으로 사용할 수 있게 한다.
- 가이드는 외부 문서 링크에 의존하지 않는 self-contained 문서로 만든다. 저장소 루트나 형제 설치
  디렉터리를 가정하는 상대 링크를 쓰지 않는다.
- 가이드 파일은 runtime prompt·ontology corpus가 아니므로 graph-owned marker, `ISSUED`,
  `LEDGER.tsv` 대상에 넣지 않는다.

루트 `README.md`는 두 가이드로 가는 발견 경로와 짧은 비교표만 소유한다. 템플릿 전문이나 상세
규칙을 복제하지 않는다.

`docs/DEVELOPMENT.md`는 위 정본·미러 관계, 정확한 두 marketplace 경로, 수정·검증 절차를
메인테이너 규칙으로 기록한다.

## 4. 공통 정보 설계

### 4.1 정보 분류와 소유권

아래 분류는 가이드를 작성하고 검토하는 기준이다. 사용자에게 A/B/C/D/E 라벨이나 별도 분류표를
작성하게 하지 않는다.

| 분류 | 내용 | 가이드에서의 처리 |
|---|---|---|
| A — 사용자 고유 정보 | 원하는 외부 결과, 이미 정한 필수 규칙, 보존·변경·제외 범위. web에서는 기준 시안의 정확한 대상과 필수 상태·폭·의도적 차이도 포함 | 최소 요청에는 A만 둔다. A도 최초 요청에서 모두 확정할 필요는 없다 |
| B — 선택 가속 정보 | 알고 있는 코드·문서·테스트·OpenAPI·asset 위치, 참고 자료와 외부 접근 사실 | “있으면 함께 주기”로 분리한다. 위치만 제공해도 되며 권위·coverage·영향 분석을 요구하지 않는다 |
| C — 플러그인 소유 | 프로젝트와 자료 조사, agent/skill 선택, 아키텍처, 테스트 전략, 시안 채널 판정, 구현·검증·재개 판단 | “플러그인이 하는 일”에서 설명한다. 사용자가 지시할 필드로 만들지 않는다 |
| D — 운영 설명 | 결과에서 확인한 범위와 남은 미확정, 자동 검증 및 시각 확인의 한계 | 발주 입력과 분리된 짧은 후반 참고로 둔다 |
| E — 삭제할 요청 부담 | 내부 gate·상태 토큰을 지시하는 요청문, 사용자가 만드는 자료 권위·coverage 분석표, 측정·검수·재개 절차서, 전수 환경·asset 준비 체크리스트 | 가이드에서 제거한다. 명칭을 바꾸어 선택 요청서로 남기지 않는다 |

제품의 동작을 바꾸는 경계 사례나 실패 결과는 A다. 그 사례를 발견하는 데 도움이 되는 문서·샘플은
B다. 조사로 확인 가능한 사실과 사용자가 결정해야 하는 결과가 섞이면 플러그인이 조사한 뒤
결정이 필요한 부분만 묻는다.

### 4.2 최소 요청 계약

핵심 요청에는 원하는 외부 결과, 이미 정한 필수 규칙, 보존·변경·제외 범위만 둔다.
`dddjango`는 네 판단 이내, `dddjango-web`은 다섯 판단 이내로 구성한다.
이는 모두 채워야 하는 필드 수가 아니라 정리할 수 있는 최대 묶음이다.

기능이나 화면과 원하는 변화만으로 시작할 수 있게 가장 짧은 예시를 먼저 제공한다.
규칙의 최소 개수, 증거 경로, 아키텍처 선택, 테스트 수, 미확정 목록을 필수로 두지 않는다.
미확정이나 선호는 필요할 때 자연어로 말하면 되며, 사실·필수·선호 라벨을 매 줄 요구하지 않는다.

관련 자료는 복사 가능한 핵심 요청 블록과 분리한다. 예시가 있더라도 “알고 있다면”이라는 조건을
분명히 하고, 자료 없이 시작하는 요청도 완결된 예시로 보여 준다.

### 4.3 공통 목차

두 가이드 모두 다음 골격을 사용한다. 별도 고급 가이드나 운영 문서로 나누지 않는다.

1. 사용 범위
2. 바로 시작 — Claude와 Codex 시작 문법, 짧은 요청과 최소 요청 묶음
3. 알려 주면 좋은 제품 정보 — 해당할 때 이미 정한 결과를 더 정확히 설명하는 방법
4. 플러그인이 하는 일 — 조사·설계·구현·검증 책임
5. 조건부 선택 정보 — 알고 있는 자료가 있으면 함께 주기
6. 수정·재개 — 바뀐 결과와 보존할 동작, 세션 밖에서 바뀐 사실 전달
7. 짧은 완료 참고 — 구현한 결과, 확인한 범위, 남은 차이와 미확정 해석

제품 정보를 보충하는 절은 전수 작성 양식이 아니다. 후반 참고는 내부 절차 교육이나
게이트별 체크리스트로 확장하지 않는다.

### 4.4 요청문과 플러그인 설명의 경계

사용자는 원하는 플러그인을 호출하되, 그 안의 agent·skill·검토 순서나 아키텍처·테스트 전략을
배정하지 않는다. 복사 가능한 요청 블록에는 `G0`, `G1`, `G1′`, `G2`, `pending`,
`build_anchor`, `pre-gate`, `registry`, `slice`, `refreeze`, `재절단`, `재개봉`,
`DIFF` 실행 지시를 넣지 않는다.

필요한 질문과 승인은 플러그인이 안내한다고 짧게 설명할 수 있다. 사용자가 승인 단계를 선택하거나
생략 조건을 판정하게 하지 않는다. 재개 시에도 플러그인이 기존 기록과 현재 상태를 확인한다.
질문이나 승인이 없어지는 것, 자동 검사만으로 전체 품질이 보장되는 것을 약속하지 않는다.

## 5. dddjango 가이드 설계

### 5.1 전문성과 목차

업무 변화와 불변식이 정확해야 DDD 설계와 TDD 구현의 판단 근거가 선다. 가이드는 사용자에게
업무 사례와 지켜야 할 결과를 설명하게 하고, 도메인 배치와 테스트 설계는 플러그인 책임으로 둔다.

공통 목차를 다음 내용으로 채운다.

1. 사용 범위 — 기존 Django 프로젝트의 한 기능, 화면 구현과의 구분
2. 바로 시작 — `/dddjango`와 `dddjango를 사용해 …`, 한 기능의 원하는 변화
3. 알려 주면 좋은 제품 정보 — 성공·실패 결과, 이미 정한 업무 규칙과 보존할 동작
4. 플러그인이 하는 일 — 기존 프로젝트 조사, DDD 설계, TDD 구현과 검증
5. 조건부 선택 정보 — 관련 자료 위치, 해당하는 업무의 추가 사례
6. 수정·재개 — 바꿀 결과, 유지할 동작, 세션 밖에서 바뀐 사실
7. 짧은 완료 참고 — 구현한 업무 사례, 실행한 검증, 남은 미확정

### 5.2 최소 요청의 네 판단

| 묶음 | 사용자가 알려 주는 내용 |
|---|---|
| 기능 | 어느 기능에서 어떤 업무 변화를 원하는가 |
| 대표 성공 결과 | 어떤 행동 뒤에 무엇이 보여야 하거나 어떤 상태가 되어야 하는가 |
| 이미 정한 핵심 규칙과 실패 결과 | 반드시 허용·금지할 결과, 실패해도 남아야 하거나 바뀌지 않아야 할 것 |
| 보존·변경·제외 범위 | 유지할 외부 동작, 이번에 바꿀 부분, 제외할 부분 |

업무 행위자와 목적은 그것에 따라 결과가 달라질 때 보충한다. 규칙은 정해진 만큼만 말하며
개수나 경계 사례 전수를 요구하지 않는다. 기존 영역 소유권·evidence·coverage는 최소 요청에 없다.

### 5.3 알려 주면 좋은 제품 정보

이미 정한 내용이 있고 이번 기능에 영향을 줄 때만 다음 관점으로 결과를 더 설명할 수 있다.

- 성공 전후에 바뀌는 업무 상태와 반드시 유지할 불변식
- 금액·수량·기간 등의 경계에서 허용하거나 거절해야 하는 결과
- 실패 뒤 생성·변경되지 않아야 하는 주문·재고·결제 등의 상태
- 중복 요청·재시도·동시 실행이 생겼을 때 사용자가 기대하는 결과
- 외부 알림·결제 등의 완료 시점과 실패 뒤 허용되는 업무 상태
- 기존 사용자나 연동 시스템이 계속 이용해야 하는 동작, 의도적으로 바꿀 호환 동작

이 목록은 복잡한 기능을 설명하는 단서다. 해당하지 않거나 아직 정하지 못한 항목을 채우게 하지 않는다.
`select_for_update` 같은 구현 수단, 테스트 오라클의 형식, 지원 종료의 증거 분석을 발주하지 않는다.

### 5.4 플러그인이 하는 일과 선택 자료

플러그인은 관련 코드·문서·기존 테스트를 조사하고, 서로 다른 해석이 있으면 제품 선택이 필요한
질문으로 정리한다. DDD의 영역·aggregate·repository 배치, API/DB 구현 수단, 필요한 agent·skill,
테스트 구조·수량·검증 절차를 스스로 판단한다. 가이드에는 이 책임을 평이하게 설명한다.

사용자가 이미 알고 있는 코드·문서·테스트·API 자료 위치나 참고 사례는 “있으면 함께 주기”에 둔다.
사용자에게 자료를 찾고 분석해 권위·coverage·영향 범위를 확정하도록 요구하지 않는다.
실제로 정해진 환경 제약은 이유와 필요한 결과를 알려 줄 수 있지만, 내부 설계 지시 양식을 만들지 않는다.

### 5.5 수정·재개와 완료 참고

수정·재개 요청에는 이전 작업을 이어간다는 사실, 바꿀 결과, 보존할 동작, 알고 있는 세션 밖의
변경 사실을 담는다. 이전 작업 위치를 알면 선택적으로 덧붙인다. 사용자가 내부 파일명·상태 토큰·
마지막 승인 단계·재검증 순서를 찾아서 제공하지 않는다.

완료 참고는 구현한 업무 사례, 실제로 실행한 검증, 남은 미확정이나 제한을 읽는 방법으로 끝낸다.
자동 검사가 모든 결함을 증명하지 않는다는 한계는 짧게 설명하고, 사용자가 테스트 입장표나
registry를 감사하도록 요청하지 않는다.

## 6. dddjango-web 가이드 설계

### 6.1 전문성과 목차

시안의 정확한 대상과 필요한 화면 결과가 선명해야 충실도를 판단할 수 있다. 사용자는 어느
화면·상태·폭을 맞출지와 의도적인 차이를 설명하고, 플러그인은 시안 분석·검증 방법과
유지보수 가능한 MVVM/HTMX 구조를 맡는다.

공통 목차를 다음 내용으로 채운다.

1. 사용 범위 — 기존 Django 프로젝트의 한 화면과 백엔드 작업 경계
2. 바로 시작 — `/dddjango-web`과 `dddjango-web을 사용해 …`, 시안 있음·없음·접근 불가
3. 알려 주면 좋은 제품 정보 — 정확한 디자인 대상, 필수 상태·폭·동작, 의도적인 차이
4. 플러그인이 하는 일 — 시안·API 조사, 표현 구조 설계, 구현과 충실도 확인
5. 조건부 선택 정보 — 추가 시안·동작 자료·asset·font·대표 데이터·OpenAPI 위치와 접근 사실
6. 수정·재개 — 바뀐 화면 결과와 알고 있는 새 디자인·API 위치
7. 짧은 완료 참고 — 구현 결과, 확인한 시각 범위, 남은 차이와 미확인 상태

### 6.2 최소 요청의 다섯 판단

| 묶음 | 사용자가 알려 주는 내용 |
|---|---|
| 화면 | 어느 화면을 만들거나 바꾸며 무엇을 유지·제외할 것인가 |
| 기준 시안과 정확한 대상 | 시안이 있다면 위치와 screen·frame·page 등 구현할 대상. 시안 없음 또는 접근 불가도 그대로 말할 수 있음 |
| 필수 상태·폭·동작 | 이미 정한 필수 화면 상태, 화면 폭, 사용자 행동 뒤에 기대하는 결과 |
| 의도적인 차이 | 시안과 다르게 만들기로 한 부분이 있다면 그 결과 |
| 데이터 연동 의도 | 실제 데이터로 동작해야 하는지, 예시 데이터 화면인지 등 이미 정한 범위 |

한 화면과 원하는 변화만으로 시작할 수 있다. 시안이 있는 경우에는 그 안의 정확한 대상을
알려 줄 수 있도록 예시를 제공한다. 시안 없음·접근 불가·API 위치 미확정을 실패한 요청으로 다루지 않는다.
필수 상태나 폭도 처음부터 모두 확정하게 하지 않으며, 필요하면 플러그인이 조사·질문한다.

OS·browser·zoom·DPR 전수, source capability 분류, 검수자, 완료 행렬, asset·font 전수 준비,
OpenAPI의 형식·method·path 분석은 최소 요청 필드가 아니다.

### 6.3 알려 주면 좋은 제품 정보

이미 정해져 있거나 시안에서만 알기 어려운 제품 결과에 집중한다.

- 여러 시안 중 기준으로 삼을 정확한 화면과 이미 정한 우선순위
- 반드시 필요한 loading·empty·error·권한별 상태 등과 각각 보일 내용
- 좁은 화면에서 메뉴·표·목록 등이 보여야 하는 방식
- 클릭·입력·스크롤 뒤 보여야 하는 변화와 꼭 필요한 움직임
- 긴 제목·빈 목록 같은 데이터에서도 유지되어야 하는 화면 결과
- 시안에서 의도적으로 바꿀 부분과 그대로 보존해야 하는 부분

모든 상태를 나열하거나 측정 환경과 재현 절차를 먼저 구성하게 하지 않는다. 시안이나 제품 결정에
없는 내용을 사용자에게 추측시켜 채우지 않는다.

### 6.4 플러그인이 하는 일과 선택 자료

플러그인이 시안의 접근 가능성과 처리 채널을 판단하고, 동결·추출·폰트·asset 조사,
상태와 검증 계획 구성, API 계약 분석을 맡는다. DOM·HTML/CSS, component 분해,
view/view_model/state, HTMX 구조도 플러그인의 구현 책임이다. 사용자는 agent·skill이나
세부 구현 수단을 배정하지 않는다.

상태별 시안, 동작 영상, 따로 전달해야 하는 asset·font, 대표 데이터, 알고 있는 OpenAPI 위치,
인증·접근 제약은 “있으면 함께 주기”로 모은다. 원본을 분석해 토큰·라이선스·자동화 능력 표를
완성하는 것을 발주 조건으로 삼지 않는다. 실제로 필요한 접근 정보는 플러그인이 구체적으로 묻는다.

### 6.5 백엔드와의 경계

web은 실제 API 계약을 소비하는 표현계층을 구현한다. API 위치를 모르면 플러그인이 프로젝트에서
찾고, 화면 결과에 필요한 계약이 있는지 확인한다. endpoint나 업무 규칙·권한·데이터 변경이 새로
필요하면 부족한 백엔드 결과와 범위를 밝혀 별도 `dddjango` 작업이 필요하다고 안내한다.

사용자에게 OpenAPI 분석·사전 변환·영향 범위 정리나 내부 재개 절차를 지시하는 요청문을 주지 않는다.
소비 가능한 계약이 아직 없다는 사실은 실제 화면 연동의 선행 조건으로 설명하며, 이를 web이
백엔드까지 구현해 준다는 약속으로 바꾸지 않는다.

### 6.6 수정·재개와 완료 참고

수정·재개에서는 바뀐 화면 결과와 보존할 부분을 말하고, 알고 있는 새 디자인·API 위치를 덧붙인다.
플러그인이 기존 기록과 변경 내용을 조사해 다음 작업을 정한다. 사용자가 재동결·재승인·재절단·
재개봉 순서나 trivial 여부를 판정하지 않는다.

완료 참고에는 자동 측정이 확인한 범위와 실제 화면을 보고 확인할 범위가 다를 수 있음을 짧게
설명한다. 플러그인은 요청한 상태·폭에서 확인한 결과, 남은 차이, 미확인 부분을 구분해 전달한다.
사용자는 원하는 화면 결과와의 차이를 피드백할 수 있다. 검사 exit·수집 상한·측정축 표나
사용자 작성 검수 행렬을 가이드에 남기지 않으며, 자동 검사 통과만으로 시각적 일치를 보장하지 않는다.

## 7. 저장소 진입면 정합성

### 7.1 README와 가이드 진입

README는 기존 `## 작업 요청 가이드` 섹션과 두 정본 링크, Claude Code·Codex 지원을 유지한다.
비교표는 `dddjango`의 업무 변화·핵심 규칙·보존 동작·범위와 `dddjango-web`의 대상 화면·기준 시안·
필수 상태와 폭·의도적 차이를 보여 준다. 관련 자료 위치는 알고 있을 때만 주는 정보이며 한 기능이나
한 화면과 원하는 변화만으로 시작할 수 있다고 설명한다.

상세 템플릿과 내부 운영 절차를 README에 복제하지 않는다. 이미 정정된 기존 구조·테스트·web
지원 범위 설명을 이번 재설계에서 다시 확장하지 않으며, 현재 가이드의 결과 중심 요청 원칙과
충돌하는 진입 문구만 정합화한다.

### 7.2 설치 후 발견 경로

- `dddjango/.claude-plugin/plugin.json`과 `codex-dddjango/.codex-plugin/plugin.json`의 homepage를
  `https://github.com/changja88/dddjango/blob/main/dddjango/REQUEST_GUIDE.md`로 연결한다.
- web의 두 manifest homepage는
  `https://github.com/changja88/dddjango/blob/main/dddjango-web/REQUEST_GUIDE.md`로 연결한다.
- Codex `interface.websiteURL`도 같은 canonical 공개 URL을 가리킨다.
- repository는 저장소 루트를 유지한다. manifest UI가 링크를 노출하는 범위에서 설치 사용자가 직접
  가이드에 도달하며, 로컬 설치본에는 같은 내용 파일이 존재한다.
- manifest homepage의 `main` URL은 최신 온라인 문서를 가리키므로 설치 버전 정본이 아니다. 설치된
  plugin 루트의 `REQUEST_GUIDE.md`를 해당 runtime의 권위 있는 사본으로 우선하고, README·homepage는
  발견 경로로만 취급한다.

### 7.3 Codex 추천 시작 문장

두 Codex manifest의 `interface.defaultPrompt`는 해당 plugin 이름을 포함한 짧은 결과 중심
예시를 유지한다. 현재 가이드와 충돌하는 예시가 있을 때만 수정한다.

- dddjango: 원하는 업무 변화, 이미 정한 실패 후 보존 상태와 기존 동작
- dddjango-web: 정확한 시안 대상, 필요한 상태·폭과 의도적인 차이. 시안 없음·접근 불가도 정상 예시

API·자료 위치를 시작 필수 조건으로 만들거나 내부 gate·검증·재개 절차를 지시하지 않는다.
`agents/openai.yaml`은 내부 coordinator 역할을 시작하는 generic prompt이므로 바꾸지 않는다.
Claude manifest에 같은 추천 prompt 표면을 새로 만들지 않는다.

### 7.4 독립 릴리즈 경계

두 marketplace가 모두 `ref: main`을 바라보지만 dddjango와 dddjango-web의 버전·태그·Release는
독립이다. 두 payload를 함께 바꾸는 이번 구현은 feature branch에 유지하고 push·release하지 않는다.
후속 릴리즈에서는 두 버전을 모두 실제 payload에 맞게 올리고 두 태그·Release를 main의 같은 공개
시점에 맞추는 절차를 별도로 승인하거나, plugin별 landing과 release를 분리해야 한다. 단일 plugin
release target으로 이 합본 branch를 그대로 push해 다른 plugin의 변경을 이전 버전으로 노출하면 안 된다.

## 8. 영구 검증

기존 표준 라이브러리 validator `workspace/tools/request_guide_contract.py`가 다음 배포 계약과
canonical source surface의 drift를 한곳에서 검사하고 기존 `Makefile` 흐름에서 실행된다.

- 두 guide pair의 존재와 byte 동일
- README의 `## 작업 요청 가이드` source heading부터 다음 `## ` heading 직전까지
  `[dddjango 작업 요청 가이드](dddjango/REQUEST_GUIDE.md)`와
  `[dddjango-web 작업 요청 가이드](dddjango-web/REQUEST_GUIDE.md)`라는 exact source token이 각각
  정확히 한 번 존재하며, 전체 README source에서도 각각 정확히 한 번 존재
- 네 installed guide source 어디에도 상대 목적지처럼 보이는 Markdown inline/image destination,
  reference definition destination, HTML `href`/`src` 구문이 없음. Scheme URI와 `#fragment`만 허용하며,
  code span·fence·HTML comment·escape·예시 안에도 같은 보수적 금지 규칙을 적용
- `.claude-plugin/marketplace.json`, `.agents/plugins/marketplace.json`의 네 name/path/ref 매핑
- 각 marketplace subdir 안의 guide와 manifest 존재
- 네 manifest의 canonical guide homepage와 repository 분리, 두 Codex `interface.websiteURL`의 exact URL
- Codex `defaultPrompt`가 비어 있지 않은 문자열 배열이며 해당 plugin 이름을 포함
- 두 guide 상단의 “설치된 사본이 해당 runtime의 권위 있는 가이드” 문구

링크 검사는 명시적인 source-level drift backstop이다. CommonMark 문맥, 렌더러 등가성 또는 실제
rendered/clickable 동작은 판정하지 않는다. README token이 코드나 주석 안에 있어도 source count에
포함하며, guide의 목적지 구문도 문맥을 가리지 않고 검사한다. 실제 표시와 가독성은 문서 검토로 확인한다.

validator는 `--self-test`에서 실제 두 section heading 구조의 임시 정상 fixture를 만들고 `validate`
결과를 literal 기대값과 대조한다. README label/path 오타·섹션 밖 이동·중복, guide의 코드·주석·중첩
상대 목적지 구문을 거부하고 scheme URI·fragment를 허용하는지 검사한다. Mirror 1바이트 drift,
guide 누락, marketplace path/ref 오염, subdir manifest 누락, homepage/repository 혼동, Codex websiteURL
오염, guide 권위 문구 삭제, `defaultPrompt`의 잘못된 타입·빈 문자열·plugin 이름 누락 변이도 유지한다.

기존 `workspace/tools/reverse_coverage.py`의 dddjango 설치본 닫힌 분류표에도 루트
`REQUEST_GUIDE.md`가 “사람용 사용자 가이드”로 명시 등록되어 있으며 이 분류를 유지한다.

새 framework·네트워크 검사·가이드 의미 검증기는 만들지 않는다. 위 validator는 기존 배포·링크 계약만 결정적으로
검사한다. `verify-base-core`는 dddjango pair `cmp`, validator self-test, 실제 저장소 검사를 실행하고
`verify-web`은 web pair `cmp`와 실제 저장소 검사를 실행한다. validator는 중복 실행돼도 외부 상태를
쓰지 않는다. `Makefile`은 manifest 봉인 대상이며 이를 변경하면
`manifest_seal.py --write`로 **draft manifest**를 재발행한 뒤 전체 `make verify`를 다시 실행하는 기존
규칙을 따른다. 이번 재설계는 Makefile·validator·봉인 대상 도구를 변경하지 않는다.
이 draft는 run-ready seal이 아니며 이후 릴리즈가 manifest version을 바꾸면 다시 재발행해야 한다.

추가 검증은 다음과 같다.

- request guide contract validator
- 네 JSON manifest와 두 marketplace JSON이 파싱되는지 확인
- `claude plugin validate dddjango --strict`
- `claude plugin validate dddjango-web --strict`
- 두 guide mirror의 byte 동일 확인
- 금지된 과장 문구와 낡은 사실(`질문 없이`, `픽셀 완벽 보장`, web 검사 24종 등) 검색
- A/B/C/D/E 분류와 요청문 책임 경계의 문서 검토, 백엔드 작업 경계 확인
- `git diff --check`
- `make verify`

## 9. 수용 기준

### 9.1 공통

- 핵심 요청에는 A만 있으며, 기능이나 화면과 원하는 변화만으로 시작하는 완결된 예시가 있다.
- A의 모든 내용을 최초 요청에서 확정하도록 요구하지 않는다. B는 “있으면 함께 주기”로 분리한다.
- C는 플러그인이 하는 일로 설명하고, 복사 가능한 요청문에 C/E 실행 지시가 없다.
- D는 짧은 후반 참고다. 별도 사용자 문서나 내부 운영 체크리스트로 확장하지 않는다.
- 코드·문서·테스트·OpenAPI·asset의 위치를 몰라도 시작할 수 있으며, 사용자가 자료의 권위·coverage·
  영향 범위·출처 처리 능력을 분석하게 하지 않는다.
- 수정·재개는 바뀐 결과와 보존할 동작, 알고 있는 새 자료나 외부 사실을 전달하는 것으로 충분하다.
  내부 단계·토큰·측정·재개 절차는 플러그인 책임이다.

### 9.2 dddjango

- 최소 요청은 기능·대표 성공 결과·이미 정한 핵심 규칙과 실패 결과·보존/변경/제외 범위의 네 묶음 이내다.
- 업무 변화·불변식·실패 뒤의 상태·보존할 외부 동작을 구체화하는 안내가 유지된다.
- 복잡한 기능의 경계·동시성·외부 효과·호환 동작은 이미 정한 제품 결과가 있을 때 보충한다.
- DDD 영역 배치, API/DB 수단, 테스트 구조·수량·검증 전략과 agent/skill 선택은 플러그인이 맡는다.
- 최소 기능, 복잡한 backend, 기존 작업 재개 예시에서 내부 절차를 사용자가 지시하지 않는다.

### 9.3 dddjango-web

- 최소 요청은 화면·기준 시안과 정확한 대상·필수 상태/폭/동작·의도적 차이·데이터 연동 의도의 다섯 묶음 이내다.
- 시안 있음·없음·접근 불가와 API 위치 미확정이 모두 정상적인 시작으로 표현된다.
- 기준 시안의 정확한 대상, 필수 상태와 폭, 의도적인 차이를 선명하게 전달하는 안내가 유지된다.
- 시안 채널 판정, 분석·추출, 상태·검증 계획, API 계약 조사, MVVM/HTMX/HTML/CSS 구조는 플러그인이 맡는다.
- 환경 전수·asset/font 전수·검수자·측정 및 완료 행렬을 사용자 입력으로 요구하지 않는다.
- 필요한 백엔드 기능이 없으면 별도 작업 경계를 알리되 사용자가 내부 handoff·재개 절차를 지시하지 않는다.
- 자동 측정과 시각 확인의 차이는 완료 참고에 짧게 남기며 시각적 일치의 자동 보장을 약속하지 않는다.

### 9.4 배포와 유지보수

- 각 설치본 안에 해당 `REQUEST_GUIDE.md`가 존재하며 플러그인별 한 개의 논리 문서로 유지된다.
- 각 Claude/Codex 쌍은 byte 동일하며 전체 verify에서 drift가 차단된다.
- README와 네 manifest의 latest-online homepage에서 두 가이드를 발견할 수 있고, 설치된
  `REQUEST_GUIDE.md`가 해당 runtime의 권위 있는 사본임을 가이드 도입부가 밝힌다.
- 기존 homepage·repository·Codex websiteURL·README 링크와 `request_guide_contract.py`의 책임을 유지한다.
- runtime prompt·ontology·rulepack·LEDGER·reference corpus와 validator는 변경하지 않는다.

## 10. 명시적 비범위와 잔여 위험

조사 중 다음 기존 불일치를 발견했지만, 사용자 요청 가이드 작업과 분리한다.

- dddjango Claude/Codex 역할 문서 사이 migration-only 테스트 처리 표현 차이
- dddjango-web OpenAPI 동결 시점에 대한 coordinator와 reference의 표현 차이
- dddjango-web `extract_dc`의 설명과 실제 script 능력 차이
- 이미지·motion·render audit가 모든 시안 증거를 자동 포괄하지 못하는 한계

이번 가이드는 어느 한쪽의 모순된 동작도 보장으로 문서화하지 않는다. 런타임 규범을 고치려면 별도
설계·온톨로지 절차와 평가가 필요하다.

## 11. 재설계 변경 범위

Task 1은 다음 설계·계획 파일만 다룬다.

- `workspace/design/2026-09-05-plugin-request-guides-spec.md` — 현재 기준선 교정
- `workspace/plan/2026-09-05-plugin-request-guides-plan.md` — 대체 고지만 추가하고 과거 본문 보존
- `workspace/plan/2026-09-05-plugin-request-guides-revision-plan.md` — 현재 실행 계획

이후 Tasks 2~4의 변경 대상은 다음과 같다.

- `dddjango/REQUEST_GUIDE.md`, `codex-dddjango/REQUEST_GUIDE.md`
- `dddjango-web/REQUEST_GUIDE.md`, `codex-dddjango-web/REQUEST_GUIDE.md`
- `README.md`
- 필요한 경우에만 `codex-dddjango/.codex-plugin/plugin.json`과
  `codex-dddjango-web/.codex-plugin/plugin.json`의 `interface.defaultPrompt`

기존 배포·검증 계약을 소유한 다음 파일은 이번 재설계에서 변경하지 않는다.

- `docs/DEVELOPMENT.md`, `Makefile`, `workspace/tools/request_guide_contract.py`
- `workspace/tools/reverse_coverage.py`, `workspace/eval/ab/T2-0b-manifest.json`
- 두 marketplace와 두 Claude plugin manifest, 네 manifest의 homepage·repository 및 두 Codex websiteURL

런타임 규범은 계속 비범위다.

- `dddjango/commands/**`, `dddjango/agents/**`, `dddjango/skills/**`
- `codex-dddjango/skills/**`
- `dddjango-web/commands/**`, `dddjango-web/agents/**`, `dddjango-web/skills/**`
- `codex-dddjango-web/skills/**`
- `ontology/**`, `dddjango/scripts/rulepack.json`, `workspace/reference/**`
