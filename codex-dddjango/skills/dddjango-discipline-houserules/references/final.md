# dddjango 표준 파일트리
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

> **단일 출처.** 이 문서가 dddjango 플러그인이 만드는 코드의 파일트리 «값»의 정본이다 — SKILL.md·에이전트 문서는 여기를 가리키기만 하고 값을 복제하지 않는다. 트리 블록(§1)과 기계 사본(`scripts/standard_tree.py`)의 동기는 메인테이너 도구 `tree_mirror_check` 가 지킨다. 규칙 문면 끝의 `#N` 은 설계 명세(트리 개정 명세 538규칙)의 규칙 번호다.
>
> **편입 상태(2026-08-11).** 이 판은 새 표준 트리(140행)의 첫 배포판이다 — §0 제1원칙 · §1 트리 · §2 골격 규칙 · §4 이관이 정본이고, 층·칸별 상세 규칙과 명명 전수는 매핑표(`rule-owner-map`) 순서로 이 문서에 편입된다. 옛 판(4계층 `infra_layer`/`presentation_layer` 세대)의 상세 절은 이 판에서 걷혔다 — 옛 이름은 §4 이관 절이 다룬다.

## 무엇이고 왜
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

dddjango 는 **DDD · 클린 아키텍처 · 헥사고날** 셋을 조합해 Django 프로젝트를 조직한다. 그 조합의 물리적 표현이 이 표준 파일트리다 — 바운디드 컨텍스트(BC)마다 같은 골격, 입구(driving)와 출구(driven)의 물리 분리, 계약(`port`)과 구현(`adapter`)의 분리, 프레임워크 소유물(`framework/`)의 격리.

트리는 「무엇이 **있어야** 하나」를 정하고, 스킬은 「그것을 **어떻게 쓰나**」를 정한다 — 트리에 조건을 적어 두 채널로 만들지 않는다(#492).

## §0 제1원칙 — 골격은 내용과 무관하다
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

**모든 검사보다 먼저 서는 원칙이다**(#487 — 골격이 어긋나면 나머지 검사를 돌릴 이유가 없다).

- **#486** — 어느 BC 를 열어도 이 트리의 골격이 «그대로» 있다 — 내용이 있든 없든 상관없다. 파일트리를 지키지 않는 구현·설계는 «반환»이다.
- **#488** — 고정 이름의 칸은 «부모가 있으면» 반드시 있다 — 폴더는 비어도 `__init__.py` 로, 파일도 비면 «빈 파일»로 만든다.
- **#489** — `<…>` 가 붙은 자리표시자 칸만 그 개념이 실제로 생길 때 생긴다 — 그 외에 「이 BC 엔 없으니 뺀다」는 축소가 아니라 위반이다.
- **#490** — `application/<bounded_context>/**` 안에 트리에 없는 경로가 하나라도 있으면 위반이다(`utils/`·`common/`·`helpers/`). 폐쇄는 **칸**(폴더 + 트리가 이름을 준 파일)에만 걸리고, 트리가 리프로 닫은 폴더 «안»의 추가 모듈은 작성자 재량이다(#15). `framework/`·`<project>/` 는 이 원칙의 주어가 아니다.
- **#491** — 칸의 유형은 셋뿐이고 «조건부»는 없다 — ① 고정 이름 ② `<>` 첫 등장 ③ `<>` 재등장(조상이 이미 연 낱말이라 값이 이미 채워져 있어 ①과 같다).
- **#492** — 「그 파일이 있어야 하나」는 트리가 정하고 「그것을 어떻게 쓰나」는 스킬이 정한다.

골격의 실현 주체는 **coder** 다 — 승인 스코프의 BC 를 새로 만들거나 touched 하면(touched = G0 스코프의 그 BC — §4 와 같은 자 · 명세가 골격 실현을 지시한 데이터소스 BC 포함) 고정·재등장 칸을 빈 채로라도 실현한다. 위반은 `check-layer-skeleton` 이 잡는다.

## §1 표준 트리 — 140행
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

행 번호는 정본의 행 번호이고, 규칙·검사기·명세가 「트리 N행」으로 이 번호를 가리킨다. `<…>` 는 자리표시자(§0 유형 ②③)다.

<!-- TREE:BEGIN — tree_mirror_check 가 쓴다 · 손으로 고치지 않는다 -->
```text
  1 application/<bounded_context>/
  2   composition_root/
  3     dependency_wiring.py
  4     event_wiring.py
  5   published_event/
  6     <event>.py
  7   driving_layer/
  8     api/
  9       api_router.py
 10       bc_error_schema.py
 11       <area>/
 12         <area>_controller.py
 13         schema/
 14           schema_in.py
 15           schema_out.py
 16       webhook/
 17         <provider>/
 18           <provider>_controller.py
 19           schema/
 20             schema_in.py
 21             schema_out.py
 22     open_host_service/
 23       <service>/
 24         <service>_service.py
 25         contract/
 26           request/
 27             <request>_request.py
 28           response/
 29             <response>_response.py
 30           exception/
 31             <service>_published_error.py
 32             <exception>_exception.py
 33     cron_job/
 34       <job>_cron_job.py
 35     event_subscription/
 36       event_router.py
 37       <event>_subscription.py
 38   application_layer/
 39     <area>/
 40       <use_case>/
 41         <use_case>_use_case.py
 42         <use_case>_command.py
 43         <use_case>_query.py
 44         <use_case>_result.py
 45     port/
 46       <capability>/
 47         <capability>_port.py
 48         exception.py
 49         <data>_out.py
 50         <data>_in.py
 51       domain_bypass_query/
 52         <capability>/
 53           <capability>_query.py
 54           <data>_out.py
 55           <data>_in.py
 56           exception.py
 57       unit_of_work/
 58         <boundary>_unit_of_work.py
 59   domain_layer/
 60     <aggregate>/
 61       <aggregate>.py
 62       entity/
 63         <entity>.py
 64       value_object/
 65         <value_object>.py
 66       event/
 67         <event>.py
 68       <aggregate>_repository.py
 69       exception/
 70         <exception>.py
 71     shared_value_object/
 72       <value_object>.py
 73     domain_service/
 74       <domain_service>.py
 75   driven_layer/
 76     django_<bounded_context>/
 77       apps.py
 78       models/
 79         <entity>_model.py
 80       migrations/
 81         <migration>.py
 82       admin/
 83         <entity>/
 84           panel.py
 85           form/<form>_form.py
 86           feature/<feature>.py
 87       templates/admin/<bounded_context>/<page>.html
 88       templates/<bounded_context>/<capability>/<template>.html
 89     adapter/
 90       persistence/
 91         repository/
 92           <aggregate>_repository.py
 93         domain_bypass_query/
 94           <capability>_query.py
 95         unit_of_work/
 96           <boundary>_unit_of_work.py
 97       anticorruption_layer/
 98         <other_bounded_context>/
 99           <capability>_adapter.py
100       external_system/
101         <system>/
102           <capability>_adapter.py
103       <capability>/
104         <technology>_adapter.py
105   test/
106     unit/
107     integration/
108     e2e/
109     factories/
110     fake/
111       <declaration>.py
112 framework/
113   broker/
114     internal/
115       internal_broker_port.py
116       internal_broker.py
117     external/
118       external_broker_port.py
119       external_broker.py
120   <capability>/
121     <capability>_port.py
122     exception.py
123     <data>_out.py
124     <data>_in.py
125     <technology>_adapter.py
126   <technology>/
127     <module>.py
128   pure/
129     <module>.py
130   test/
131     <module>.py
132     fake/
133       <declaration>.py
134     unit/
135 <project>/
136   api.py
137   urls.py
138   celery.py
139   settings/
140     <environment>.py
```
<!-- TREE:END -->

읽는 법:

- 최상위는 셋이다 — `application/<bounded_context>/`(BC 마다 하나) · `framework/`(저장소에 하나) · `<project>/`(Django 프로젝트 패키지).
- 폴더 이름이 끝에 `/` 를 달고, `admin/`·`templates/` 아래처럼 한 행이 하위 경로를 품기도 한다.
- 기계 사본은 `scripts/standard_tree.py` — 검사기들이 import 하는 유일한 트리 데이터다.

## §2 골격 규칙

### BC 직계 — 일곱뿐
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

- **#81** — `application/<bounded_context>/` 바로 아래에는 일곱 가지만 온다 — 층 폴더 넷(`driving_layer/` · `application_layer/` · `domain_layer/` · `driven_layer/`) · `test/` · `composition_root/` · `published_event/`. 여덟째는 없다.
- **#82** — BC 폴더 이름은 장고 앱 이름이 아니라 업무 경계의 이름이다(accounts · billing · ai_chat).
- **#10** — 네 칸을 모두 아는 것은 `composition_root` 하나뿐이다.
- **#628** — 이 BC 의 «업무 어휘»는 `domain_layer/**` 아래 공개 심볼(모듈·클래스·함수·Enum 값) 이름의 토큰 집합이다 — 폴더 이름만이 아니다. 별도의 «용어집 파일»은 두지 않는다. 불용어 목록(`Id`·`Status`·`Name`·`Item`·`Type`·`Value` …)도 저장소가 유지하는 데이터다.

### 입구 — `driving_layer/`
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

- **#88** — BC 의 입구 계층 폴더 이름은 `driving_layer/` 다 — `presentation_layer/` 를 쓰지 않는다.
- **#89** — 바깥 행위자가 BC 를 부르는 통로는 `driving_layer/` 뿐이다 — 다른 층에 입구를 두지 않는다.
- **#90** — `driving_layer/` 의 자식은 `api/` · `open_host_service/` · `cron_job/` · `event_subscription/` 넷뿐이고 «어떤 전송으로 오나»로만 갈린다 — HTTP · 같은 프로세스 함수 호출 · celery · 브로커. 「누가 부르나」(행위자)로 가르지 않는다.
- **#91** — 새 **전송**이 실제로 생기기 전에는 `driving_layer/` 의 자식을 늘리지 않는다 — 「새 행위자」로는 늘리지 않는다(웹훅이 그 반례다: 결제사라는 새 행위자가 왔지만 전송이 HTTP 라 2차 축 `webhook/<provider>/` 로 들어갔다). **늘리는 주체는 «정본 트리»다** — 개정되면 #486 에 따라 그 전송을 안 쓰는 BC 도 그 칸을 «빈 채로» 갖는다.
- **#92** — `driving_layer/` 의 잎은 `application_layer/<area>/` 아래만 의존한다 — 예외는 넷: 도메인 exception·값 객체(#95) · `composition_root` 의 `build_`(#97) · 남의 `published_event/`(#507) · `framework/<technology>/`·`framework/<capability>/` 의 계약·스키마(브로커 포트는 여기 없다 — `application_layer` 쪽만 #7 이 연다: `framework/broker/{internal,external}/*_broker_port.py` import 허용).
- **#178** — 소비 task 가 껍데기를 넘어 조율을 시작하면 새 칸을 여는 것이 아니라 입구 로직 금지 위반을 고친다.

### 만들지 않는 칸
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

- **#20** — 값이 하나뿐인 축으로는 폴더를 만들지 않는다. **#21** — 어떤 종류가 하나뿐이면 폴더가 아니라 파일로 둔다. (트리의 파일 칸들이 이 원리의 산물이다 — 예: `<aggregate>_repository.py`.)
- **#58** — `application/**/management/commands/` 를 만들지 않는다.
- **#187** — 포트 선언에 BC 최상위 칸을 만들지 않는다 — 애그리거트에 안 붙는 포트는 `application_layer/port/` 에만 산다.
- **#314** — `domain_layer/` 에 `specification/` 폴더를 두지 않는다.

### `migrations/` — 생성물만
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

- **#336~#338·#593** — `driven_layer/django_<bounded_context>/migrations/` 에는 `makemigrations` 가 «생성한 것»만 둔다 — 사람이 손으로 데이터를 채우는 파일(`RunPython`·`RunSQL`)을 넣지 않는다. 마이그레이션은 「돌았다 / 안 돌았다」 두 상태뿐이라 배치 크기·부분 재실행·진행률이 구조적으로 안 된다. 대량 채우기는 파일이 아니라 **배포 절차의 한 «단계»** 다(Expand → Backfill → Contract — 그 코드는 트리 밖 `scripts/`, 규정하지 않는다). 허용 목록(#593)은 도구 산출물의 모양이 정한다 — 그 밖의 함수·분기·도메인 import·데코레이터는 위반이다. 덤 — `elidable` 을 안 달면 그 자리에서 squash 최적화가 끊긴다.

### `<project>/`
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

- **#429** — `<project>/` 에는 프레임워크가 «전역에 딱 하나»를 요구하는 것만 온다 — `api.py` · `urls.py` · `celery.py` · `settings/`. `celery.py` 항목의 «celery 채택» 전제는 **정본 트리(표준) 수준**의 채택이다 — 개별 프로젝트의 채택 여부가 아니다. celery 를 안 쓰는 프로젝트도 이 칸을 «빈 파일»로 갖는다(#488 — 빈 `celery.py` 가 규범 준수의 정상 상태이고, 뒤에 celery 가 필요해지면 그 빈 파일이 착지 자리다). 표준이 celery 를 버리는 개정에서만 이 목록이 다시 선다(#491 «조건부 없음»의 자리는 트리 1행 `application/**` 이라 여기 걸리지 않는다 — `<project>/` 파트는 이 목록이 관할한다).
- **#430** — `<project>/` 는 `application/` 을 «등록»만 하고 «타입»으로 알지 않는다 — 문자열 경로는 등록이고 import 는 앎이다.
- **#432** — `<project>/` 는 BC 가 늘어도 커지지 않는다 — 판정 물음은 「BC 하나를 통째로 지웠을 때 이 파일이 바뀌나」다.
- **#436** — `<project>/` 의 `health.py`·`home.py`·`asgi.py`·`wsgi.py` 는 표준 트리의 관할 밖이라 칸을 만들지 않는다(면제).

## §3 명명
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

- BC 이름은 업무 경계의 이름(#82 — §2). 파일·클래스 명명 규약 전수(창구 `_command`/`_query` · 계약 `…Request`/`…Response` · 어댑터 `<technology>_adapter.py` · ORM `<entity>_model.py` 등)는 정본의 각 칸 «이름» 줄이 소유하며, 매핑표 순서로 이 절에 편입된다.
- **BC(앱)명↔애그리거트명 유사 변형 금지(권장 — 기계 검사기 없음·reviewer 점검)**: `ordering` vs `order` 같은 한 글자·복수형 차이로 헷갈리게 두지 않는다 — 같게 하거나 명확히 다른 컨텍스트명으로 한다(#82 물음에 딸린 점검 · 08-12 삭제분 감사에서 복원).

## §4 이관 — 종료 기록과 빚

### 이관 종료 (2026-08-12)
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

옛 이름(`presentation_layer/`→`driving_layer/` · `infra_layer/`→`driven_layer/` · `published_service/`→`open_host_service/` · `acl/`→`anticorruption_layer/` · 루트 `common/`→`framework/`)의 이중 수용은 **2026-08-12 에 끝났다** — 검사기는 옛 이름을 더 알아보지 않는다. 옛 이름 재등장은 이제 별도 진단이 아니라 트리 밖 칸 위반(#81·#490 — 층 이름 위장은 #324)이다.

### brownfield 는 «면제»가 아니라 «아직 안 갚은 빚»이다
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

brownfield 는 코드의 속성이 아니라 규칙 변경의 그림자다 — 코드는 안 바뀌었는데 규칙이 바뀌어 위반이 됐다. 「리팩터링 대상」을 따로 정의하지 않는다 — **백스톱이 내는 위반이 곧 그것이다.** BC 를 작업하면(작업하는 BC = G0 스코프의 그 BC — 파일을 건드렸다는 사실이 그 BC 를 '작업 대상'으로 만들지 않는다) 그 BC 의 백스톱 위반을 «먼저» 정리하고 시작하며, 「가만 있어도 해로운」 위반은 그것을 기다리지 않는다. 미루기는 사용자에게 물어서만 가능하고 `.dddjango/` 에 기록된다.

### 검사기의 가드 계약
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

저장소가 표준을 채택한 신호(둘 이상의 신호원)가 있는데 검사 대상이 0건이면 검사기는 통과가 아니라 `exit 2` 로 막는다(#74) — 개명·경로 변화로 검사가 «조용히 무동작»이 되는 것을 막는 가드다.

### 규칙 개정의 이행 순서
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

- **#72** — 규칙을 바꾸는 개정은 플러그인 셋 — 검사 스크립트·리뷰어 지침·표준 문서 — 을 **한 커밋에서 먼저** 고치고, 코드(대상 저장소)는 그 «다음»에 옮긴다. 순서가 뒤집히면 코드가 아직 없는 규칙에 맞아 거짓 위반이 나거나, 규칙이 아직 없는 코드가 거짓 통과한다.

## 배경 (이 표준이 파생된 곳)
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

Evans(바운디드 컨텍스트·애그리거트·유비쿼터스 언어) · Vernon(애그리거트=트랜잭션 경계) · Martin(의존 규칙·Humble Object) · Cockburn(포트와 어댑터 — «who triggers or is in charge of the conversation»). 각 칸의 결정 근거·기각 대안은 저장소 정본의 결정 카드 57장에 있다 — 이 문서는 «값»만 싣는다.
