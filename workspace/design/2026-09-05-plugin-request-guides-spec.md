# dddjango · dddjango-web 작업 요청 가이드 설계 명세

- 날짜: 2026-09-05
- 상태: 구현 기준선
- 범위: 사용자 작업 요청 가이드, 저장소 진입 문서, 배포 미러 검증
- 비범위: Coordinator·agent·skill의 런타임 규범 변경, 온톨로지 규칙 변경, 기존 파이프라인 결함 수정

## 1. 목적

두 플러그인의 긴 실행 시간과 높은 판단 비용을 사용자의 입력 품질로 줄이되, 질문을 없애거나
파이프라인을 축약하는 것이 아니라 각 플러그인이 가장 잘 판단할 수 있는 **증거와 완료 기준**을
처음부터 제공하게 한다.

- `dddjango`: 비즈니스 규칙·불변식·현행 계약을 정확히 받아 DDD 설계와 TDD 구현 품질을 높인다.
- `dddjango-web`: 권위 있는 시안·상태·화면 폭·상호작용·실물 API 계약을 정확히 받아 시안 충실도와
  표현계층 코드 품질을 함께 높인다.

가이드의 성공은 요청의 길이가 아니라 아래 네 가지로 판단한다.

1. 사실, 필수 제약, 선호, 미확정을 구분한다.
2. 사용자가 결과와 관찰 가능한 규칙을 설명하고 내부 설계를 미리 결정하지 않는다.
3. 플러그인이 보호해야 할 기존 계약과 비교해야 할 증거를 찾을 수 있다.
4. G0·G1·G2에서 사용자가 무엇을 검토하고 승인할지 안다.

## 2. 조사 근거

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
  homepage를 각 정본 가이드의 공개 GitHub URL로 바꾸고 repository는 저장소 루트로 유지한다.
  README 발견 경로와 manifest 발견 경로를 모두 제공하되 자동 노출을 과장하지 않는다.

### 2.2 dddjango 파이프라인이 요구하는 입력

- 기존 Django 프로젝트의 한 기능을 대상으로 G0 요구·경계, G1 설계·독립 리뷰·영구 테스트 입장표,
  G2 승인된 테스트와 코드 구현 순서로 진행한다.
- DDD 리뷰는 항상, 외부 API 계약이 바뀌면 API 리뷰, 스키마·인덱스·제약·트랜잭션·마이그레이션이
  바뀌면 DB 리뷰가 활성화된다.
- 테스트는 개수나 커버리지 목표가 아니라 승인된 계약, 그 테스트만 검출하는 production failure,
  기존 권위 테스트와의 중복 여부로 입장을 정한다.
- 현재 코드·문서·기존 테스트는 계약을 찾는 조사 증거이지 그 자체로 계약 정본이 아니다. 제품이
  현재 지원하기로 승인한 요구·소비자·wire/data/event 의미와 기존 coverage를 분리해 받아야 한다.
- 선택적 강건성(idempotency 등)은 사용자의 비즈니스 필수 규칙인지, 설계 제안인지 구분해야 한다.
- `.dddjango/<날짜>-<기능-slug>/`에 한 기능의 스코프와 설계 기록을 남기며, 기존 작업을 이어갈 때는
  해당 폴더, 마지막 승인 위치, 이후 코드·계약·스키마·dependency 변경을 알려 줘야 한다. 마지막
  승인은 현재 작업의 재사용 가능한 허가가 아니며 Coordinator가 현행 증거와 모든 관련 test
  admission의 `pending=0`을 다시 확인한 뒤에만 G1′ 생략 여부를 판단한다.

### 2.3 dddjango-web 파이프라인이 요구하는 입력

- 기존 Django 프로젝트의 web 표현계층 한 화면 요구를 대상으로 한다. 백엔드를 구현하지 않고
  실제 URL+JSON API 계약을 외부 클라이언트처럼 소비한다.
- 자동 동결·추출이 연결되는 일급 출처는 Claude Design `.dc.html` 또는 접근 가능한 참조 HTML이다.
  다만 `.dc.html`은 원본 브라우저 render audit이 불가하고, 참조 HTML도 실제 브라우저에서 접근·실행할
  수 있을 때만 audit할 수 있다. 독립 이미지·스크린샷은 현재 수동 시각 증거다.
  시안이 있으나 접근할 수 없는 경우와 애초에 시안이 없는 경우도 서로 다르다.
- 화면 형상은 동결된 디자인 증거가 기준이고, 코드는 view/view_model/state·HTMX·design system
  규율로 재구축한다. 원본 HTML/CSS를 그대로 가져오는 방식이 아니다.
- OpenAPI 전체를 고정한 뒤 승인된 exact path만 구현 슬라이스에 제공한다. 필요한 API가 없으면
  `dddjango` 백엔드 발주가 먼저다.
- 자동 비교와 백스톱은 일부 측정축과 구조 규율만 증명한다. 전체 스크롤·상태·반응형·동작의
  최종 시각 오라클은 접근 권한이 있는 사용자의 육안 확인이다.

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

두 가이드의 용어와 독법을 맞춘다.

### 4.1 입력 라벨

요청자는 중요한 문장을 필요할 때 다음 라벨로 구분한다.

- `사실`: 현재 시스템·사용자·시안·계약에서 관찰하거나 확인한 내용
- `필수 제약`: 결과가 반드시 지켜야 하는 비즈니스·운영·호환 조건
- `선호`: 합리적인 이유가 있으면 플러그인이 다른 선택을 제안해도 되는 방향
- `미확정`: 확인되지 않았고 추측해서는 안 되는 내용

모든 줄에 라벨을 강제하지 않는다. 충돌 가능성이나 추측 위험이 있는 핵심 항목에만 사용한다.
빈칸을 억지로 채우지 말고 `미확정`이라고 적는 것을 품질 높은 입력으로 명시한다.

### 4.2 입력 수준

각 가이드는 세 수준을 제공한다.

1. **30초 최소 요청**: 바로 붙여 넣을 수 있는 한 문단형 템플릿
2. **권장 요청서**: 복잡한 기능·화면을 위한 구조화 템플릿
3. **조건부 보충**: API, DB·동시성, 외부 연동 또는 반응형·모션·백엔드 handoff처럼 해당할 때만 작성

필수 항목을 지나치게 늘려 사용자가 모든 것을 알아야 시작할 수 있다는 인상을 주지 않는다.

### 4.3 게이트 사용법

가이드는 승인 게이트를 단순 절차가 아니라 품질 제어점으로 설명한다.

- G0: 문제·범위뿐 아니라 적용 lens, 기존 작업 폴더, 배치, 선행 위반·부채, 시안·계약 증거와
  접근 가능성을 확인한다. 최소 템플릿은 시작점이지 G0 질문과 검사를 없애지 않는다.
- G1: 내부 이름보다 규칙, 계약, 실패·상태, 테스트 오라클, 시안 증거 처리가 정확한지 확인한다.
- G2: 승인한 설계와 범위를 코드·검증·육안 결과가 실제로 충족하는지 확인한다.

`질문 없이 끝내기`, `승인 없이 진행`, `백스톱 green이면 완벽` 같은 약속은 하지 않는다.

## 5. dddjango 가이드 설계

### 5.1 가이드의 품질 명제

좋은 요청은 클래스·레이어·패턴을 지시하는 문서가 아니라, 설계자가 올바른 도메인 경계와 계약을
판정할 수 있는 **비즈니스 사례집 + 보존 계약 목록**이다.

### 5.2 섹션 구조

1. 언제 쓰는가 / 쓰지 않는가
2. 가장 빠른 시작: Claude와 Codex 호출 예시
3. 30초 최소 요청 템플릿
4. 품질을 높이는 네 가지 작성 원칙
5. 권장 요청서 템플릿
6. 규칙·상태 전이·실패 원자성 작성법
7. 조건부 보충: 공개 API, DB·동시성·재시도, 외부 연동, brownfield 수정
8. 플러그인에 맡길 결정
9. G0·G1·G2 검토 체크리스트
10. 부분 수정·중단 후 재개법
11. 나쁜 요청을 좋은 요청으로 바꾸는 예시
12. 완료 시 받게 되는 것과 증명의 한계

### 5.3 30초 최소 요청 필드

- 사용자/행위자와 목적
- 시작 사건 또는 명령
- 성공 결과
- 반드시 지킬 규칙 2~5개
- 실패 시 남아야 하는 상태
- 보존할 기존 동작·API·데이터(있다면)
- 핵심 용어와 그 사실을 소유하는 기존 영역(알면)
- 관련 코드·문서·테스트 경로(알면)
- 범위 안 / 범위 밖
- 미확정 항목

### 5.4 권장 요청서 필드

```text
[작업]
기능명 / 신규·수정 / 사용자와 사업 목적

[성공 시나리오]
사전 상태 → 행동 → 결과 상태

[규칙과 경계값]
허용/금지 규칙, 같음 포함 여부, 최소·최대·0·null 사례

[실패와 원자성]
실패 조건 / 사용자에게 보일 결과 / 변경돼야 할 것 / 그대로여야 할 것

[중복·재시도·동시성]
업무상 중요한 경우에만 기대 결과를 서술

[도메인 언어와 소유권]
핵심 용어와 정의 / 어떤 영역·팀이 어떤 사실을 소유하는지 / 알려진 기존 영역과 협력 / 미확정

[외부 효과와 일관성]
응답 전에 끝나야 하는 효과 / 지연 허용 효과 / 중복 전달 결과 / 실패 뒤 보상·잔존 상태

[보존·변경·종료할 제품 계약]
승인 요구와 지원 소비자 / API·데이터·이벤트 의미 / 호환·deprecation·rollout 근거

[조사 증거와 기존 coverage]
관련 코드·OpenAPI·문서·배포 consumer·기존 테스트 경로

[범위]
포함 / 제외

[제약과 미확정]
필수 제약 / 선호 / 미확정
```

### 5.5 작성법의 초점

- 자연어 규칙은 `이전 상태 → 명령 → 다음 상태`와 허용/금지 예로 바꾼다.
- `잔액보다 큰 금액`처럼 경계가 있는 규칙은 같을 때의 결과까지 적는다.
- 실패 시 주문, 재고, 결제, 이벤트 중 무엇이 생성·변경되지 않아야 하는지 적는다.
- 중복 요청과 동시 실행은 기술 수단이 아니라 업무 결과를 적는다.
- 즉시 일관성이 필요한 외부 효과와 지연되어도 되는 효과를 제품 의미로 구분한다.
- 기존 API·DB·이벤트의 exact shape를 안다면 evidence path와 함께 적고, 모르면 추측하지 않는다.
- 현재 코드와 기존 테스트는 계약 후보를 찾는 증거다. 승인된 제품 계약과 기존 coverage를 같은 것으로
  취급하지 않고, 계약의 삭제·약화에는 지원 종료·rollout·저장 데이터·발행 이벤트 처리 근거를 적는다.

### 5.6 플러그인에 맡길 결정

요청서에서 다음을 정답처럼 고정하지 않도록 설명한다.

- bounded context·aggregate·entity/value object 경계
- repository·port·service·use case의 클래스명과 파일 트리
- CQRS·event sourcing·saga·outbox 같은 패턴 채택
- `select_for_update` 같은 구체적인 락·트랜잭션 수단
- 테스트 파일 수·case 수·coverage quota

기술 선택이 실제 필수 제약이면 이유와 검증 가능한 결과를 적는다. 단순 선호라면 `선호`로 둔다.

### 5.7 게이트와 증명의 의미

- G0에서는 범위와 ddd/api/db lens, 새 영역·기존 영역 배치 또는 architect 위임, 기존 작업 폴더,
  대상 영역의 선행 위반을 지금 정리할지 연기할지를 확인한다.
- G1에서는 도메인 언어·소유권·불변식·계약과 영구 테스트 입장표의 근거·고유 failure·중복·`pending=0`을
  검토한다. 초기 요청에 적은 신규·변경 오류 shape는 승인 자체가 아니며 별도 명시 승인될 수 있다.
- G1 pre-gate green은 일부 구조·계약 계획 위반을 예보하지 않았다는 뜻이지 설계 의미의 정답 보장이
  아니다.
- G2 registry green은 고정 anchor 이후 이번 스코프에 귀속된 신규 위반이 0이라는 뜻이지 저장소 전체가
  clean이라는 뜻이 아니다. legacy 잔존·승인 유입·미측정 사각은 별도 보고될 수 있다.
- 통과한 테스트는 입장 심사를 거친 현행 계약을 보호하지만 모든 가능한 결함을 증명하지 않는다.
  관련 검증과 전체 suite 결과를 구분하며 baseline의 무관 실패가 있으면 전체 green이라고 말하지 않는다.

### 5.8 수정·재개와 예시 세트

- 재개 요청자는 기존 폴더를 알려 주고, Coordinator는 그 폴더의 기존 `build_anchor`를 읽어 유지한다.
  사용자에게 새 anchor를 선택·제공하게 하지 않는다. 마지막 승인 위치는 탐색 힌트로만 제공한다.
- 승인 뒤 바뀐 코드·스키마·dependency·merge, expected result·지원 계약의 삭제·약화·이름 변경 여부를
  알려 준다. Coordinator가 현행 design-spec·계약 evidence·관련 테스트 입장을 재검증해 G1′ 생략을
  결정한다.

- 한 줄짜리 모호한 주문 요청 → 규칙·원자성·현행 계약이 있는 요청
- 구현 클래스를 미리 나눈 요청 → 도메인 사실과 범위 중심 요청
- `테스트 100개/100%` 요청 → 보호 계약과 실패 오라클 중심 요청
- 기존 기능 수정 → 보존할 계약과 바꿀 규칙을 분리한 요청
- API·동시성·외부 이벤트가 있는 고위험 요청

## 6. dddjango-web 가이드 설계

### 6.1 가이드의 품질 명제

좋은 요청은 `이 이미지처럼`이라는 한 문장이 아니라, 어떤 디자인 증거를 어느 화면·폭·상태의
정본으로 볼지와 의도적인 차이를 명시하는 **시각 계약 + 상태 계약 + API 계약**이다.

`최대한 충실한 구현`은 목표이고, 결과 상태는 다음 세 가지로 분리한다.

- **구현 완료**: 승인한 코드 슬라이스와 결정적 구조 검증이 끝남
- **자동 측정 완료**: 지정한 한 쌍의 화면 상태·viewport에 지원되는 측정축을 실행함
- **시각 수용 완료**: 승인한 `state × viewport` 행렬의 전체 스크롤과 interaction을 사람이 대조함

필수 행렬을 검수하지 못하면 `충실도 미검증` 또는 `조건부 인계`로 남긴다. 접근 불가·미측정·
미검증을 정직하게 기록하는 것은 필수지만 시안 충실도가 입증됐다는 뜻은 아니다.

### 6.2 섹션 구조

1. 언제 쓰는가 / 언제 `dddjango`가 먼저인가
2. 가장 빠른 시작: Claude와 Codex 호출 예시
3. 30초 최소 요청 템플릿
4. 시안 정본과 정확한 대상 지정법
5. 권장 요청서 템플릿
6. 상태표·반응형·interaction 작성법
7. asset·font·motion·pinned·scroll 준비법
8. 실물 API 계약과 backend handoff
9. 플러그인에 맡길 결정
10. G0·G1·G2 및 최종 육안 검토 체크리스트
11. 부분 수정·trivial 수정·중단 후 재개법
12. 나쁜 요청을 좋은 요청으로 바꾸는 예시
13. 자동 검증이 증명하는 것과 못하는 것

### 6.3 30초 최소 요청 필드

- 정확한 화면과 작업 범위
- 디자인 정본과 그 안의 정확한 대상
- 자동 채널 가능한 `.dc.html`·참조 HTML인지, 수동 증거인 screenshot/image-only인지
- 기준 viewport·검수 환경 또는 반응형 참고 증거
- 반드시 구현할 상태·interaction
- asset·font 출처
- 사용할 실제 API 계약 또는 static-only/미확정
- 의도적인 시안 차이
- 최종 비교를 수행할 사람과 접근 가능 여부

### 6.4 권장 요청서 필드

```text
[화면]
화면명 / 신규·수정 / route·진입·이탈 / 범위 포함·제외

[디자인 정본]
종류와 위치 / exact screen·frame / 접근 가능 여부 / 자동·수동 증거 / 정본 우선순위 / 의도적 차이

[검수 환경과 반응형]
OS·browser/version / width×height·zoom·DPR / locale·theme·reduced-motion / 폭별 기대 동작

[상태표]
상태명 / 진입 조건 / 표시 내용 / 가능한 행동 / 디자인·계약 근거

[상태 재현]
full URL(query/hash 포함) / role·인증 준비 방식 / fixture·seed·record / loading·error 유발 / ready 조건

[interaction과 부분 갱신]
필수·선호 / trigger / 전→후 결과 / duration·easing·반복 / scroll container·pinned anchor / 허용 근사

[asset·font·motion]
원본 위치·라이선스 / font family·weight / animation·transition·감속 / 관찰 못 한 항목

[API 계약]
OpenAPI 3.x JSON 위치 / servers·endpoint·method / auth·role / request·success·empty·error·null·긴 문자열

[완료 확인]
state × viewport × design evidence × 재현 절차 × 검수자 × 자동·육안 행렬 / 허용된 차이
```

### 6.5 시안과 상태의 초점

- URL이나 파일만 주지 말고 정확한 screen/frame/route를 지정한다.
- 여러 증거가 있으면 무엇이 우선인지 적는다. screenshot과 live service의 차이를 방치하지 않는다.
- 출처 능력을 구분한다.

  | 출처 | 동결·추출 | render audit |
  |---|---|---|
  | Claude Design `.dc.html` bundle | DesignSync, token/meta/image, 동봉 render PNG | 원본 브라우저 audit 불가 |
  | 접근 가능한 live reference page | HTML/token/image | 실행자·접근 조건이 맞을 때 가능 |
  | local/static reference HTML | HTML/token/image | 브라우저에서 원본을 실행할 수 있는지 별도 확인 |
  | image/screenshot-only | 수동 시각 증거 | 불가 |

  image/screenshot-only면 자동 충실도 채널 비대상임을 알고 조건부 인계 기준을 정한다.
- desktop 한 장으로 mobile, loading, empty, error, modal, hover, focus, sticky를 추측하게 하지 않는다.
- `동작 없음`과 `관찰하지 못함`을 구분한다.
- 긴 제목, 빈 목록, null image, 권한별 차이처럼 레이아웃을 흔드는 대표 데이터를 준다.
- 상태를 이름만 적지 않고 비밀정보를 붙이지 않는 role 준비, fixture/seed, query/hash, loading/error 유발,
  font·data ready 조건을 함께 적는다. web 플러그인은 browser·functional·accessibility 자동 테스트를
  새로 작성하지 않으므로 재현 가능한 육안 절차가 필요하다.

### 6.6 backend handoff

다음 경우 `dddjango` 작업을 먼저 요청하도록 한다.

- 화면에 필요한 endpoint가 없다.
- OpenAPI와 실제 응답 또는 승인한 화면 상태가 충돌한다.
- 인증·권한·업무 규칙·데이터 변경처럼 web 표현계층 밖의 동작이 필요하다.

OpenAPI 입력은 **OpenAPI 3.x JSON**이어야 하며 비대화형 fetch가 가능한 URL 또는 로컬 파일을 준다.
YAML·Swagger 2.0은 사전에 변환한다. 문서와 실제 응답 일치는 자동 증명되지 않는다.

backend 계약이 준비되면 기존 `.dddjango-web/.../build-state.json` 폴더, 마지막 승인, 이전·신규 OpenAPI,
변경 method/path/shape, 완료된 슬라이스 중 영향 후보를 알린다. 단순 resume의 자동 감지를 기대하지 않고
G0 재동결 → 계약·설계 변경 시 G1′ 재승인 → contract 재절단 → 영향 data/UI slice 명시 재개봉을
요청한다. 프로젝트 route/template/static wiring과 실제 backend 기능을 혼동하지 않는다.

### 6.7 플러그인에 맡길 결정

- DOM·HTML tag·CSS selector와 Grid/Flex 선택
- view/view_model/state의 구체 클래스·필드와 component 분해
- HTMX attribute와 partial 구조
- design token 명명과 파일 배치

요청자는 시각 결과와 동작·계약을 적고, 유지보수 가능한 표현 구조는 플러그인이 설계하게 한다.
원본 HTML/CSS 직수입은 선택지가 아니라 금지다. custom JS가 필요한 gesture·parallax 같은 동작은
G1에서 지원 한계나 범위 조정 대상으로 드러내고, 요청에는 기술 대신 관찰 가능한 결과와 허용 근사를 쓴다.

### 6.8 자동화 한계 표기

가이드에는 판정력을 네 종류로 나눈 표를 둔다.

| 종류 | 실제 의미 |
|---|---|
| DIFF / exit 2 | 조인된 text의 font size·effective weight·line height·alignment·color, center-x 비율, 수직 순서, column width 등 일부 축. G2의 1급 판단 자료지만 자동 차단은 아님 |
| warn/info | viewport 폭 불일치, 한쪽에만 있어 조인되지 않은 text 등; 성공 exit를 막지 않을 수 있음 |
| 수집만 | font family, motion count 등; 수집됐다고 동일성을 판정한 것은 아님 |
| 미수집·수동 | viewport 높이, 정확한 y 간격·block size, image/background, border/radius/shadow/opacity, 실제 animation, 정확한 pinned anchor 등 |

한 번의 비교는 현재 DOM의 단일 상태·단일 viewport pair이고 text 200·pinned 20 상한이 있다. query/hash는
기록에서 빠지고 lazy/scroll 상태가 완전히 포착되지 않을 수 있다. 이미지 수집도 모든 CSS background·
`srcset`·동적 asset을 보장하지 않는다. 접근 권한을 가진 사용자의 전체 스크롤·상태·폭별 검수가
`시각 수용 완료`의 필수 조건이다. 구조 백스톱의 blocker와 render comparator의 DIFF를 같은 것으로
취급하지 않는다.

## 7. 저장소 진입면 정합성

### 7.1 README 변경

루트 README에는 다음 최소 변경만 한다.

- 제목과 첫 설명을 Claude Code 전용에서 Claude Code·Codex 지원으로 바로잡는다.
- 설치 직후 찾을 수 있도록 두 작업 요청 가이드 링크와 용도 비교를 빠른 시작보다 앞에 둔다.
- Claude slash command와 Codex 자연어 시작 예시를 모두 제공한다.
- 하드코딩된 과거 Codex 버전 예시는 제거하거나 현재와 무관한 형태로 바꾼다.
- 기존 구조가 표준 규약을 항상 대체한다는 표현을 제거한다. 현행 계약·artifact evidence는 보존하되,
  승인 스코프가 새로 만드는 파일과 기존 파일에 추가·변경하는 코드에 규율을 적용하고 스코프 밖
  기존 배치의 이동·개명·재배선은 별도 G0 결정 없이 하지 않는다고 고친다.
- 부분 수정의 G1 생략은 승인된 현행 설계·계약과 미결 테스트 입장이 없고 lifecycle 변경도 없는
  경우에만 가능하다고 한정한다.
- pytest 설정을 항상 자동 설치한다는 표현을 없애고, 새 설정은 승인된 `add/update`일 때만,
  `reuse`면 기존 runner를 검증 anchor로 사용한다고 고친다.
- web 플러그인이 `dddjango가 만든 API만` 소비한다는 표현을 실제 URL+JSON 계약 소비로 고친다.
- web 백스톱의 낡은 개수 표기를 없애고 결정적 백스톱으로 표현한다.
- 자동 백스톱이 전체 품질이나 픽셀 동일을 증명한다는 인상을 피한다.

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

두 Codex manifest의 `interface.defaultPrompt`만 가이드의 최소 입력 구조를 보여 주는 짧은 예로
교체한다. 모든 예를 장문 템플릿으로 만들지 않고, 각각 다른 핵심 신호를 담는다.

- dddjango: 상태 전이·실패 원자성, 현행 계약 보존, 미확정 표시
- dddjango-web: 시안 정본·viewport·상태, 실물 API, 접근 불가 또는 의도적 차이

`agents/openai.yaml`은 내부 coordinator 역할을 시작하는 generic prompt이므로 이번에는 바꾸지 않는다.
Claude manifest에는 같은 추천 prompt 표면이 없어 억지로 새 필드를 만들지 않는다.

### 7.4 독립 릴리즈 경계

두 marketplace가 모두 `ref: main`을 바라보지만 dddjango와 dddjango-web의 버전·태그·Release는
독립이다. 두 payload를 함께 바꾸는 이번 구현은 feature branch에 유지하고 push·release하지 않는다.
후속 릴리즈에서는 두 버전을 모두 실제 payload에 맞게 올리고 두 태그·Release를 main의 같은 공개
시점에 맞추는 절차를 별도로 승인하거나, plugin별 landing과 release를 분리해야 한다. 단일 plugin
release target으로 이 합본 branch를 그대로 push해 다른 plugin의 변경을 이전 버전으로 노출하면 안 된다.

## 8. 영구 검증

작은 표준 라이브러리 validator `workspace/tools/request_guide_contract.py`가 다음 배포 계약을 한곳에서
검증하고 기존 `Makefile` 흐름에서 실행된다.

- 두 guide pair의 존재와 byte 동일
- README의 두 canonical 상대 링크와 guide 내부 외부 상대 링크 부재
- `.claude-plugin/marketplace.json`, `.agents/plugins/marketplace.json`의 네 name/path/ref 매핑
- 각 marketplace subdir 안의 guide와 manifest 존재
- 네 manifest의 canonical guide homepage와 repository 분리, 두 Codex `interface.websiteURL`의 exact URL
- Codex `defaultPrompt`가 비어 있지 않은 문자열 배열이며 해당 plugin 이름을 포함
- 두 guide 상단의 “설치된 사본이 해당 runtime의 권위 있는 가이드” 문구

validator는 `--self-test`에서 임시 fixture를 만들고 정상 case와 mirror 1바이트 drift, guide 누락,
README link 오타, marketplace path/ref 오염, subdir manifest 누락, homepage/repository 혼동,
Codex websiteURL 오염, guide 권위 문구 삭제, `defaultPrompt`의 잘못된 타입·빈 문자열·plugin 이름 누락이
각각 RED가 되는지 검사한다.

새 framework나 네트워크 검사는 만들지 않는다. 위 validator는 이 작업의 배포·링크 계약만 결정적으로
검사한다. `verify-base-core`는 dddjango pair `cmp`, validator self-test, 실제 저장소 검사를 실행하고
`verify-web`은 web pair `cmp`와 실제 저장소 검사를 실행한다. validator는 중복 실행돼도 외부 상태를
쓰지 않는다. `Makefile`은 manifest 봉인 대상이므로 모든 변경이 끝난 뒤
`manifest_seal.py --write`로 **draft manifest**를 재발행하고 전체 `make verify`를 다시 실행한다.
이는 run-ready seal이 아니며 이후 릴리즈가 manifest version을 바꾸면 다시 재발행해야 한다.

추가 검증은 다음과 같다.

- request guide contract validator
- 네 JSON manifest와 두 marketplace JSON이 파싱되는지 확인
- `claude plugin validate dddjango --strict`
- `claude plugin validate dddjango-web --strict`
- 두 guide mirror의 byte 동일 확인
- 금지된 과장 문구와 낡은 사실(`질문 없이`, `픽셀 완벽 보장`, web 검사 24종 등) 검색
- 템플릿 필수 신호와 backend handoff 문구 검색
- `git diff --check`
- `make verify`

## 9. 수용 기준

### 9.1 dddjango

- 사용자가 최소 템플릿만으로 행위자, 성공 상태, 규칙, 실패 원자성, 보존 계약, 범위, 미확정을
  전달할 수 있다.
- 핵심 용어·사실 소유 영역·즉시/지연 외부 효과와 제품 계약을 기존 coverage와 구분할 수 있다.
- 고위험 기능은 API·동시성·재시도·외부 연동 정보를 결과 중심으로 보충할 수 있다.
- 내부 설계와 테스트 개수를 미리 지정하지 않아 DDD architect와 테스트 입장표가 판단할 공간이 있다.
- 신규·수정·재개의 입력 차이와 세 게이트의 검토 책임이 명확하다.

### 9.2 dddjango-web

- 사용자가 시안의 위치뿐 아니라 정확한 화면, 증거 우선순위, viewport, 상태, interaction, asset,
  motion, API, 완료 비교 계획을 전달할 수 있다.
- 구현 완료·자동 측정 완료·시각 수용 완료를 분리하고, 필수 행렬 미검수는 충실도 미검증으로 남긴다.
- backend 부재를 web 구현으로 덮지 않고 `dddjango` handoff와 같은 작업 폴더 재개 흐름을 안다.
- 사용자가 HTML/CSS 구현을 미리 설계하지 않아 시안 충실도와 코드 규율을 동시에 지킬 수 있다.

### 9.3 배포와 유지보수

- 각 설치본 안에 해당 `REQUEST_GUIDE.md`가 존재한다.
- 각 Claude/Codex 쌍은 byte 동일하며 전체 verify에서 drift가 차단된다.
- README와 네 manifest의 latest-online homepage에서 두 가이드를 발견할 수 있고, 설치된
  `REQUEST_GUIDE.md`가 해당 runtime의 권위 있는 사본임을 문서가 밝힌다.
- runtime prompt·ontology·rulepack·LEDGER는 변경하지 않는다.

## 10. 명시적 비범위와 잔여 위험

조사 중 다음 기존 불일치를 발견했지만, 사용자 요청 가이드 작업과 분리한다.

- dddjango Claude/Codex 역할 문서 사이 migration-only 테스트 처리 표현 차이
- dddjango-web OpenAPI 동결 시점에 대한 coordinator와 reference의 표현 차이
- dddjango-web `extract_dc`의 설명과 실제 script 능력 차이
- 이미지·motion·render audit가 모든 시안 증거를 자동 포괄하지 못하는 한계

이번 가이드는 어느 한쪽의 모순된 동작도 보장으로 문서화하지 않는다. 런타임 규범을 고치려면 별도
설계·온톨로지 절차와 평가가 필요하다.

## 11. 변경 파일 목록

신규:

- `dddjango/REQUEST_GUIDE.md`
- `codex-dddjango/REQUEST_GUIDE.md`
- `dddjango-web/REQUEST_GUIDE.md`
- `codex-dddjango-web/REQUEST_GUIDE.md`
- `workspace/design/2026-09-05-plugin-request-guides-spec.md`
- `workspace/plan/2026-09-05-plugin-request-guides-plan.md`
- `workspace/tools/request_guide_contract.py`

수정:

- `README.md`
- `docs/DEVELOPMENT.md`
- `Makefile`
- `dddjango/.claude-plugin/plugin.json`
- `dddjango-web/.claude-plugin/plugin.json`
- `codex-dddjango/.codex-plugin/plugin.json`
- `codex-dddjango-web/.codex-plugin/plugin.json`
- `workspace/eval/ab/T2-0b-manifest.json` (manifest 봉인 재발행 결과)

변경하지 않음:

- `dddjango/commands/**`, `dddjango/agents/**`, `dddjango/skills/**`
- `codex-dddjango/skills/dddjango/**`
- `dddjango-web/commands/**`, `dddjango-web/agents/**`, `dddjango-web/skills/**`
- `codex-dddjango-web/skills/dddjango-web/**`
- `ontology/**`, `dddjango/scripts/rulepack.json`, `ontology/LEDGER.tsv`
