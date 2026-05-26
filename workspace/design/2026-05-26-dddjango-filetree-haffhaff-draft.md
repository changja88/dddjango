# dddjango 표준 파일트리 — HaffHaff 기반 초안

## 출처 · 목적 · 상태

- **출처**: `~/Desktop/HaffHaff-Server-main` — 사용자의 실전 프로젝트(강한 의견의 DDD 4계층 Django, Django Ninja 기반).
- **목적**: dddjango 플러그인이 생성하는 코드의 **단일 표준 파일트리**를 정한다. HaffHaff 골격을 베이스로 삼되, 계층 내부는 코퍼스(`architecture-ddd` 등)로 보강해 발전시킨다. 스킬에 들어갈 표준이므로 **도메인 비종속(일반화) 표현**으로 적는다.
- **상태**: **초안(draft)**.
  - **도메인 일반화 적용** — 특정 도메인명(`member`·`chat` 등)·프로젝트명(`HaffHaff`)을 placeholder(`<app>`·`<entity>` 등)로 표기한다. 원문 오타 `presentaion_layer`는 `presentation_layer`로 교정해 적는다.
  - **domain_layer DDD 보강** (2026-05-26) — HaffHaff의 간소화된 도메인(`entity`/`value_object`/`form`)을 코퍼스(`architecture-ddd` §3 전술 패턴·§6.1 패키지 구조)의 빌딩블록 전체로 확장했다. `form`은 도메인에서 **제거**(도메인 불변식은 값객체/엔티티 자체검증, 유스케이스 입력은 응용 계층으로 — 응용 계층 정비는 다음 단계).
  - **bridge → OHS 분산** (2026-05-26) — HaffHaff의 중앙 `application/bridge/`를 해체하고, 컨텍스트 간 통신을 각 앱이 소유하는 `published_service/`(OHS, 오픈 호스트 서비스)로 분산했다(코퍼스 §2.5/§6.7). "무조건 경유"는 "OHS만 import" 규약으로 보존. 도메인 엔티티 노출(누수) → Published Language(DTO) 전환은 다음 단계.
  - **application_layer DDD 보강** (2026-05-26) — 코퍼스(§3.6 응용 서비스·§5.4 CQRS·§6.1/§6.3 UoW) 대조 리뷰 반영. 입력 **DTO**(`dto/`, form 귀착지)·이벤트 **handler**[선택]·**UoW**[선택] 자리 신설, **DIP**(구체 리포지토리 직접 생성 → domain repository 인터페이스 의존)로 교정, **CQRS는 전면 강제 대신 선택적**(§5.4)으로 명시.
  - **infra_layer DDD 보강** (2026-05-26) — Data Mapper 방향(ORM→도메인 변환, 도메인은 ORM 모름)은 충실(§6.2). repository를 domain `repository/` 인터페이스의 **구현**으로(DIP) 명시. 도메인 이벤트는 **발생=domain 애그리거트 / 디스패치 타이밍=UoW / 발행=`transaction.on_commit()` 기본**으로 정리하고, 별도 `event_publisher/` 디렉터리는 두지 않음(발행·outbox 구체는 `implementation-django` §16.5·`architecture-db` §9.7 소유). 구체 매핑·UoW도 django §16 위임.
  - **presentation_layer DDD 보강** (2026-05-26) — 구조(`api/<feature>` + `schema`)는 코퍼스 interface(§6.1)와 정합이라 트리 유지. 규약만 보강: api는 **얇은 어댑터**(비즈니스 로직 금지, 오케스트레이션은 application), **응답은 `schema_out`(DTO)로 — 도메인 엔티티 직접 노출 금지**(OHS 누수와 동일한 Published Language 경계). HTTP 계약·Ninja 구체는 `architecture-api`·`implementation-django-ninja` 소유.
  - **조직 규칙 — 개념 1차 + 종류 2차** (2026-05-26) — 종류 폴더(`entity`/`value_object`/`command`…)에 여러 애그리거트/feature 파일이 평면 누적되는 것을 막기 위해, **개념(애그리거트/feature)을 조직 1차 축, 종류를 2차**로 확정. `domain_layer`를 `<aggregate>/{entity,value_object,…}`로 재편(application `<feature>/`와 대칭). 단일·소규모 평면 허용, 커지면 분할(§6.8). `discipline-houserules` 평면 금지의 2차 레벨. infra는 기술 묶음 1차 유지.
  - **적용 방식 미정** — 이 표준을 "고정 강제"할지 "적응형 유지 + 표준 권장"할지는 **아직 결정하지 않았다**.
  - **구조 명명 정제 미정** — `_layer` 접미사, `application/` 컨테이너, command/query 분리 등 HaffHaff 고유 *구조 명명*을 그대로 표준화할지는 다음 단계에서 정한다(일반화는 했지만 명명 규칙 자체는 원본을 따른다).
  - 이 단계에서 `discipline-houserules`·코퍼스(ddd §6.1 / django §3.1 / test §4.2)·에이전트·커맨드는 **건드리지 않았다**.

> **placeholder 범례**: `<project>`=프로젝트(설정) 패키지명 · `<app>`=feature 앱 · `<feature>`=앱 내 유스케이스 묶음 · `<entity>`=도메인 엔티티 · `<resource>`=API 리소스 · `<usecase>`=응용 서비스.

---

## 1. 공통 골격 (코드 조직 디렉터리)

> 루트의 인프라·툴 파일은 **표준 트리에서 생략**한다 — `docker-compose.*`·`docker/`·`Makefile`·`pyproject.toml`·`poetry.lock`/`uv.lock`·`ruff.toml`·`conftest.py`(pytest 루트)·`manage.py`(Django 진입점)·firebase 키 등은 프로젝트당 1개, 루트에 놓이는 게 자명하고 코드 조직과 무관하다.

```
<project_root>/
├── <project>/                  # 프로젝트(설정) 패키지
│   ├── settings/               # 환경별 분할
│   │   └── {env, dev, local, prod, test}.py
│   ├── urls.py  asgi.py  wsgi.py  celery.py
│   ├── views/                  # 프로젝트 레벨 뷰
│   └── static/  templates/
│
├── application/                # 모든 feature 앱의 컨테이너
│   └── <app>/  <app>/  ...     # 컨텍스트 간 통신은 각 앱의 published_service/ OHS로 (아래 §2)
│
└── common/                     # 앱 횡단 공용
    ├── enum/                   # 도메인별 enum 집중화 (<domain>_enum.py)
    ├── django/                 # Django 유틸 (task, timezone, model_util …)
    ├── ninja/                  # Django Ninja 확장 (authentication, custom_type, response …)
    └── <project>/              # 프로젝트 고유 커스텀 타입·공용 (HaffHaff의 haffhaff/)
```

핵심:
- 앱들은 루트 평면이 아니라 **`application/` 한 디렉터리 아래**로 묶인다.
- 설정 패키지(`<project>/`)는 **환경별로 분할**(`env`/`dev`/`local`/`prod`/`test`).
- 횡단 관심사는 `common/`에 모으고, 그 안을 기술축(enum·django·ninja)으로 다시 나눈다.

---

## 2. 대표 앱 — `<app>` 4계층 전개

각 앱은 **4계층을 디렉터리로 물리 분리**한다. 계층 이름에 `_layer` 접미사를 쓴다(HaffHaff 원본 규칙).

```
application/<app>/
├── <app>_api_router.py                 # 외부 HTTP 진입점: URL/라우터 등록 (루트 urls.py가 포함)
├── published_service/                  # 컨텍스트 간 OHS — 다른 앱에 노출 (상세는 아래 "컨텍스트 간 통신")
│
├── domain_layer/                       # ① 도메인 — 의존 없음, 순수 비즈니스 (§3 전술 패턴 / §6.1)
│   └── <aggregate>/                    #   애그리거트(개념) 1차 — 예: member/  (작으면 평면, 커지면 종류 폴더 §6.8)
│       ├── <aggregate>.py              #     애그리거트 루트 — 일관성 경계 (§3.3)
│       ├── entity/                     #     종속 엔티티 (§3.2): <entity>.py
│       ├── value_object/               #     값 객체 (§3.1): <value_object>.py
│       ├── repository/                 #     리포지토리 인터페이스(ABC) — DIP 포트 (§3.4). 구현은 infra
│       ├── domain_service/             #     stateless 도메인 로직 (§3.5)   [선택]
│       ├── event/                      #     도메인 이벤트 (§3.7)           [선택]
│       ├── specification/              #     Specification (§3.8)          [선택]
│       └── exception.py                #     도메인 예외
│
├── application_layer/                  # ② 응용 — 유스케이스 (§3.6). domain에만 의존, 비즈니스 로직은 도메인 위임
│   ├── <feature>/
│   │   ├── command/                    #   쓰기 유스케이스(응용 서비스): <usecase>_app.py — domain repository 인터페이스에 의존
│   │   ├── query/                      #   조회: <usecase>_query_app.py — selector/QuerySet (CQRS는 필요 컨텍스트만, §5.4)
│   │   ├── dto/                        #   입력 DTO(command 객체): <usecase>_command.py — form 제거분 흡수
│   │   ├── handler/                    #   도메인 이벤트 핸들러 (§6.1)                    [선택]
│   │   └── service/                    #   다중 유스케이스 오케스트레이션: <usecase>_service_app.py  [선택]
│   └── unit_of_work.py                 #   UoW 인터페이스 — 트랜잭션 경계 (§6.3)          [선택]
│
├── infra_layer/                        # ③ 인프라 — ORM·외부 I/O. 세 갈래로 분리
│   ├── django_<app>/                   #   Django 영속성 (도메인 엔티티와 별개의 ORM 모델)
│   │   ├── apps.py
│   │   ├── models/                     #     <entity>_model.py
│   │   ├── migrations/
│   │   └── admin/                      #     <entity>_admin.py (+ templates/)
│   ├── repository/                     #   domain repository 인터페이스(ABC) 구현 — ORM↔도메인 변환 (DIP)
│   └── service/                        #   외부 서비스 어댑터: <external>_service.py (인증·푸시 등)
│
├── presentation_layer/                 # ④ 표현 — 입력 어댑터 (§6.1 interface)  (원문 오타 presentaion → 교정)
│   ├── api/
│   │   └── <feature>/                  #   api_<resource>.py — 얇은 어댑터(요청 파싱 → 응용 호출 → 응답·예외 변환)
│   └── schema/                         #   입출력 계약(DTO): schema_in.py / schema_out.py / error_out.py
│
└── test/                               # 앱별 테스트
    └── api/
        └── <feature>/                  #   엔드포인트별로 묶음 → test_api_<resource>.py
```

의존 방향(단방향): `presentation_layer → application_layer → (domain_layer + infra_layer)`, `domain_layer`는 아무것도 의존하지 않는다.

주목할 설계 선택:
- **조직 1차 축 = 개념(애그리거트/feature), 2차 = 종류**: 각 계층을 개념 단위로 먼저 묶고(`domain_layer/<aggregate>/`, `application_layer/<feature>/`) 그 안에서 종류(`entity`/`value_object`/`command`/`query`…)로 나눈다. **단일·소규모는 평면 허용, 한 폴더에 둘 이상 개념이 섞이거나 커지면 분할**(§6.8 YAGNI). 종류 폴더에 여러 개념의 파일이 구분 없이 누적되는 것을 막는 규칙 — `discipline-houserules` 평면 금지의 **2차 레벨**(계층 안 카테고리까지)이다. `infra_layer`는 기술 어댑터라 1차를 기술 묶음으로 두고, 그 안에서 누적 시 애그리거트별 하위 그룹핑.
- **도메인 계층은 DDD 전술 패턴으로 완전 구성** (코퍼스 §3·§6.1): HaffHaff의 `entity`/`value_object`/`form` 간소화 대신 애그리거트 루트·도메인 서비스·리포지토리 인터페이스·도메인 이벤트·Specification을 갖춘다. 코어는 애그리거트 루트·`entity`·`value_object`·`repository`(인터페이스), 나머지는 필요한 앱만(`[선택]`).
- **리포지토리 DIP**: 인터페이스(ABC)는 `domain_layer/repository/`, 구현은 `infra_layer/repository/`. HaffHaff는 구현만 있어 포트가 비었으므로 포트를 추가한다.
- **ORM 모델 ≠ 도메인 엔티티**: 도메인은 `domain_layer/<aggregate>/`(루트·엔티티·VO), Django 모델은 `infra_layer/django_<app>/models/`로 **분리**한다.
- **응용 계층은 도메인에 위임하는 파사드** (§3.6): 비즈니스 로직을 직접 구현하지 않고 도메인 객체에 위임한다. 입력은 **DTO(command 객체)**로 받는다(primitive 인자 지양).
- **응용 계층 DIP**: command/query는 구체 리포지토리를 직접 생성하지 말고 **`domain_layer/repository/` 인터페이스에 의존**하고 구현을 주입받는다(HaffHaff는 `MemberCompoundRepo()`를 직접 생성 — DIP 위반이라 교정).
- **CQRS는 선택적** (§5.4 [의사결정#2]): command/query 분리를 모든 컨텍스트에 강제하지 않는다. selector/QuerySet로 충분하면 단순 흐름을 유지하고, 읽기/쓰기 모델이 실제로 갈릴 때만 적용한다.
- **트랜잭션 경계는 UoW**(§6.3, 선택), **도메인 이벤트 처리는 handler**(§6.1, 선택)로 둔다.
- **infra_layer 3분할**: `django_<app>/`(영속성) + `repository/`(접근·구현) + `service/`(외부 I/O). repository는 `domain_layer/repository/`의 ABC를 **구현**하고 ORM↔도메인 변환을 맡는다(Data Mapper, §6.2 — ORM이 도메인을 import, 도메인은 ORM을 모름). 구체 매핑·QuerySet/Manager·`transaction.atomic()` UoW는 `implementation-django` §16 소유.
- **도메인 이벤트 흐름**: 발생(raise)은 `domain_layer` 애그리거트, 디스패치 타이밍은 UoW가 명시(§3.7 [의사결정#7]). 발행은 기본 **`transaction.on_commit()`**(Django의 UoW 실현, §6.3), 외부 부수효과 유실이 치명적인 Risky Write만 **outbox**. 발행/전달 구체는 `implementation-django`(§16.5)·`architecture-db`(§9.7) 소유라, **표준 트리에 별도 `event_publisher/` 디렉터리를 두지 않는다**.
- **표현 계층은 얇은 입력 어댑터** (§6.1 interface, §3.6): api는 요청 파싱 → 응용 호출 → 응답·예외 변환만 하고 비즈니스 로직을 두지 않는다(오케스트레이션은 application). **응답은 `schema_out`(DTO)로 노출하고 도메인 엔티티를 직접 직렬화하지 않는다** — `published_service` OHS 누수와 동일한 *Published Language 경계* 원칙. HTTP 계약·status·Ninja `Router`/`Schema`/auth 구체는 `architecture-api`·`implementation-django-ninja` 소유.

### 컨텍스트 간 통신 — OHS (제공 컨텍스트 소유)

서로 다른 컨텍스트(앱) 간 통신은 **각 앱이 자기 공개 진입점(OHS, 오픈 호스트 서비스)을 소유**한다(코퍼스 §2.5/§6.7). 다른 컨텍스트는 이 `published_service/`만 import하고, 대상 앱의 `domain_layer`/`application_layer`/`infra_layer`는 **직접 import하지 않는다** — 사용자의 "무조건 경유" 게이트를 *직접 결합 금지* 규약으로 보존한 것이다.

```
application/<app>/published_service/   # 이 앱이 외부 컨텍스트에 노출하는 OHS
├── read.py       # 조회 OHS — application_layer/query에 위임 (앱이 크면 read/ 디렉터리)
└── write.py      # 커맨드 OHS — application_layer/command에 위임
```

HaffHaff의 중앙 `application/bridge/{read,write}/`(모든 앱의 OHS를 한 폴더에 모은 구조)는 **해체**한다 — 한 컨텍스트의 공개 계약이 그 컨텍스트 밖에 흩어지면 응집이 깨지고, `bridge`가 모든 컨텍스트를 아는 결합 허브로 비대해지기 때문이다(코퍼스: OHS는 제공 컨텍스트가 소유, §2.5 "진흙공" 방어).

- **[후속]** OHS 반환을 도메인 엔티티(현행) 대신 **Published Language(DTO)**로 노출해 모델 누수를 막을지는 다음 단계(코퍼스 §6.8 가벼운 패턴 우선 원칙 + §2.5/§6.7 ACL 경계 함께 고려).

(앱별 변종: WebSocket 앱은 `<app>_asgi_router.py`·`presentation_layer/socket/`을 더 가진다. 단순 앱은 `domain_layer` 없이 둘 수 있다 — 원본도 모든 앱이 4계층을 빠짐없이 채우진 않는다.)

---

## 3. 폴더별 레퍼런스 (존재 이유 · 위치 파일)

> **개요**: 앱은 `application/<app>/` 아래 4계층(`_layer` 접미사)으로 물리 분리한다. 의존 방향은 `presentation → application → (domain + infra)`이고 `domain`은 아무것도 의존하지 않는다. **각 계층 내부는 개념(애그리거트/feature) 1차 + 종류 2차로 조직**하고, 단일·소규모면 평면, 커지면 분할한다(§6.8). 아래 표가 각 폴더의 **존재 이유**와 **위치할 파일·명명 규칙**의 단일 레퍼런스다. `(코어)`는 항상 두고, `[선택]`은 트리거 조건이 맞을 때만 만든다.

**최상위 · 공용**

| 폴더 | 존재 이유 | 위치 파일 · 명명 |
|---|---|---|
| `<project>/` | 프로젝트 설정 패키지(앱 아님) | `settings/{env,dev,local,prod,test}.py`, `urls.py`·`asgi.py`·`wsgi.py`·`celery.py`(비동기 큐 쓸 때) |
| `<project>/views/` | 어느 앱에도 속하지 않는 루트/관리 뷰(헬스체크·랜딩 등) | 루트 뷰 모듈 |
| `<project>/{static,templates}/` | 프로젝트 레벨 정적·서버렌더 자원(앱·admin 자원과 구분) | 정적 파일·템플릿 |
| `application/` | 모든 feature 앱의 컨테이너 | 앱 디렉터리 `<app>/` |
| `common/enum/` | 앱 횡단 enum 집중화 | `<domain>_enum.py` |
| `common/django/` | **Django 의존** 공용 유틸 | `task.py`·`timezone.py`·`model_util.py` |
| `common/ninja/` | **Django Ninja 의존** 공용 확장 | `authentication.py`·`custom_type.py`·`response/` |
| `common/<project>/` | **프레임워크 비종속** 공용 = shared kernel 대응(공유 값객체·커스텀 타입) | 공유 VO·타입. ※Django/Ninja에 의존하면 위 두 폴더로 |

**도메인 계층 `domain_layer/<aggregate>/` — 애그리거트(개념) 1차, 그 안에서 종류 2차 (코퍼스 §3 전술 패턴)**

| 위치 | 존재 이유 | 위치 파일 · 명명 | 코어/[선택] |
|---|---|---|---|
| `<aggregate>/` | 애그리거트 = 응집·조직 단위(예: `member/`·`order/`) — 같은 애그리거트의 도메인 객체를 한 폴더에 | (아래 종류들을 담음) | 코어 |
| `<aggregate>/<aggregate>.py` | 애그리거트 루트 — 불변식·일관성 경계, 외부는 루트로만 접근(§3.3) | `member.py` | 코어 |
| `<aggregate>/entity/` | 식별자를 갖는 종속 엔티티(§3.2) | `<entity>.py` | 코어(작으면 루트 옆 평면) |
| `<aggregate>/value_object/` | 불변 값 객체, 자기검증(§3.1) | `<value_object>.py` | 코어(작으면 평면) |
| `<aggregate>/repository/` | 리포지토리 **인터페이스(ABC)** — DIP 포트(§3.4), 구현은 infra | `<aggregate>_repository.py` | 코어 |
| `<aggregate>/domain_service/` | 그 애그리거트 중심의 stateless 도메인 로직(§3.5) | `<name>_service.py` | [선택]; 여러 애그리거트에 걸치면 `domain_layer/` 공용 위치로 |
| `<aggregate>/event/` | 도메인 이벤트 **정의**(§3.7) | `<event>.py` | [선택] 결과적 일관성·외부 통지가 필요할 때 |
| `<aggregate>/specification/` | 재사용 가능한 규칙/조회 명세(§3.8) | `<name>_spec.py` | [선택] 복합 비즈니스 규칙을 조합·재사용할 때 |
| `<aggregate>/exception.py` | 도메인 예외 | 단일 파일(커지면 `exception/` 패키지) | 코어 |

**응용 계층 `application_layer/` — 유스케이스 파사드, domain에만 의존 (§3.6)**

| 폴더 | 존재 이유 | 위치 파일 · 명명 | 코어/[선택] 트리거 |
|---|---|---|---|
| `<feature>/command/` | 쓰기 유스케이스(응용 서비스) — 도메인에 위임, domain `repository/` 인터페이스에 의존(DIP) | `<usecase>_app.py` | 코어 |
| `<feature>/query/` | 조회 — selector/QuerySet | `<usecase>_query_app.py` | CQRS 적용 시(§5.4); 아니면 command와 합쳐도 됨 |
| `<feature>/dto/` | 유스케이스 **입력** command 객체(DTO) — `form` 귀착지 | `<usecase>_command.py` ※**응답 DTO 아님**(응답=presentation `schema_out`) | 입력 검증이 있으면 코어 |
| `<feature>/handler/` | 도메인 이벤트/커맨드 핸들러(§6.1) | `<event>_handler.py` | domain `event/` 도입 시 |
| `<feature>/service/` | 다중 유스케이스 오케스트레이션 | `<usecase>_service_app.py` | 여러 command/query를 한 흐름으로 묶을 때(단일 유스케이스면 command로 충분) |
| `unit_of_work.py` | UoW **인터페이스** — 트랜잭션 경계(§6.3) | 앱당 1개 | 구현은 `transaction.atomic()`(django §16.4)으로 충분; 커스텀 UoW가 필요할 때만 |

**인프라 계층 `infra_layer/` — ORM·외부 I/O (Django 구체는 `implementation-django` §16 소유)**

| 폴더 | 존재 이유 | 위치 파일 · 명명 |
|---|---|---|
| `django_<app>/models/` | Django ORM 모델(**도메인 엔티티와 별개**) | `<entity>_model.py` |
| `django_<app>/migrations/` | DB 마이그레이션 | (Django 자동 생성) |
| `django_<app>/admin/` | Django admin 등록·커스텀 | `<entity>_admin.py`(+`templates/` admin 전용) |
| `django_<app>/apps.py` | AppConfig(앱 등록) | `apps.py` |
| `repository/` | domain `repository/` ABC **구현** + ORM↔도메인 변환(Data Mapper §6.2) | `<aggregate>_repo.py` |
| `service/` | **외부 서비스** 어댑터(인증·푸시·결제 등) | `<external>_service.py` ※`domain_service`와 구분(외부 I/O 전용) |

**표현 계층 `presentation_layer/` · 컨텍스트 통신 · 테스트**

| 폴더 | 존재 이유 | 위치 파일 · 명명 |
|---|---|---|
| `api/<feature>/` | HTTP **입력 어댑터**(얇게, §6.1 interface) | `api_<resource>.py` (Ninja Router) |
| `schema/` | 입출력 계약 DTO(Ninja Schema) | `schema_in.py`·`schema_out.py`·`error_out.py`(feature가 많으면 `<feature>/`로 분할) — **응답은 `schema_out`**, 도메인 직접 노출 금지 |
| `<app>/published_service/` | 컨텍스트 간 **OHS**(다른 앱에 노출, §2.5/§6.7) | `read.py`·`write.py`(앱이 크면 `read/`·`write/` 디렉터리). 다른 앱은 **이것만** import |
| `<app>/test/` | 앱별 테스트 | 현행 `test/api/<feature>/test_api_<resource>.py`(엔드포인트 중심). ⚠ **계층별 단위 테스트(domain/application/infra) 조직은 `implementation-test` §4.2 정합과 함께 다음 단계 미결** |
| 라우팅 | 앱 진입점 | `<app>_api_router.py` → 루트 `urls.py`가 포함 |

**앱별 변종**: WebSocket 앱은 `presentation_layer/socket/` + `<app>_asgi_router.py`를 추가한다. 단순 지원 앱은 `domain_layer`를 생략할 수 있다(원본도 모든 앱이 4계층을 빠짐없이 채우지 않음).

---

## 4. 현 코퍼스 레이아웃과의 대비 (서술만 — 채택 결정 아님)

세 출처가 서로 다른 트리를 제시한다. HaffHaff가 어디서 갈리는지만 기록한다. **어느 것을 표준으로 채택/정제할지는 다음 단계.**

| 차원 | architecture-ddd §6.1 | implementation-django §3.1 | **HaffHaff (이 초안)** |
|---|---|---|---|
| 앱/모듈 컨테이너 | `src/<context>/` | `apps/<app>/` | `application/<app>/` |
| 계층 단위 | 바운디드 컨텍스트 | Django 앱 | feature 앱 |
| 계층 표현 | `{domain,application,infrastructure,interface}/` | 평면 모듈(`models.py`·`views.py`·`services.py`·`selectors.py`) | `{domain_layer,application_layer,infra_layer,presentation_layer}/` (접미사) |
| 응용 계층 내부 | `application/` 평면 | (services/selectors 모듈) | `<feature>/{command, query, dto}` + `handler`·`service`·`unit_of_work`(선택) — CQRS는 선택 |
| 인프라 내부 | `infrastructure/` 평면 | (models.py에 ORM) | `django_<app>` + `repository` + `service` 3분할 |
| 도메인/ORM 분리 | 분리(엔티티 vs 영속성) | 보통 미분리(Django 모델 중심) | 분리 |
| 테스트 위치 | 최상위 `tests/` | 앱별 `apps/<app>/tests/` | 앱별 `application/<app>/test/` |
| 테스트 조직 | `{unit,integration,e2e}` 의미군 | `{unit,integration}` 의미군 | `api/<feature>/` (엔드포인트 중심, 의미군 명시 X) |
| 설정 분할 | (명시 없음) | `config/settings/{base,local,production,test}` | `<project>/settings/{env,dev,local,prod,test}` |

눈에 띄는 긴장점(다음 단계 논의용):
- HaffHaff는 ddd §6.1의 4계층과 **개념은 같지만 명명·컨테이너·내부 분할이 다른 변종**이다(동일하지 않음). 표준화 시 `_layer` 접미사·`application/` 컨테이너를 유지할지 정제할지 결정 필요.
- HaffHaff 테스트는 코퍼스 test §4.2의 `unit/integration/e2e` 의미군이 **아니라** `api/` 엔드포인트 중심이다 — 표준화하려면 그대로 둘지 §4.2 의미군에 맞출지 갈린다. (원본도 일부 앱은 `test`가 비어 있어 일관성이 완전하진 않다.)

---

## 다음 단계 (이번 범위 아님)

1. 이 초안을 함께 검토 → 표준으로 **확정·정제**(구조 명명 유지/정제, 테스트 조직 정합 등).
2. **적용 방식 결정**: 고정 강제 vs 적응형 유지 + 표준 권장(+ 향후 `init`이 신규 프로젝트에 표준 부트스트랩).
3. 확정 표준을 **단일 출처 + 위임** 방식으로 스킬에 반영(복붙 아님, "한 주제 한 소유자" 유지).
