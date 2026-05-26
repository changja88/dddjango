# dddjango 표준 파일트리

## 무엇이고 왜

이 문서는 **dddjango 플러그인이 생성하는 코드의 단일 표준 파일트리**다. `discipline-houserules` §1(파일트리 결정 순서)이 "확립된 규약이 없거나 미조직이면" 적용하라고 **위임하는 대상**이며, 레이아웃의 단일 출처다.

출처는 강한 의견의 DDD 4계층 Django 실전 프로젝트(Django Ninja 기반)이고, 각 계층 내부는 `architecture-ddd` 코퍼스(§3 전술 패턴·§6.1 패키지 구조 등)로 보강했다. 즉 코퍼스 `architecture-ddd` §6.1과 **개념은 같지만 명명·컨테이너·내부 분할이 구체화된 변종**이다 — §6.1/`implementation-django` §3.1은 이 표준이 파생된 *이론적 배경*이고, 생성 코드의 레이아웃 권위는 이 문서가 갖는다.

적용 모델은 **고정 기본값**이다. 신규·무규약 프로젝트엔 이 트리를 권위 있는 기본값으로 생성한다. 단 대상 프로젝트에 **이미 확립된 레이아웃 규약이 있으면 그것을 존중**한다(houserules §1.1 일관성 최우선) — 이 표준을 기존 규약 위에 강제하지 않는다.

표준이므로 도메인 비종속 **placeholder**로 적는다.

> **placeholder 범례**: `<project>`=프로젝트(설정) 패키지명 · `<app>`=feature 앱 · `<feature>`=앱 내 유스케이스 묶음 · `<aggregate>`=애그리거트(개념) · `<entity>`=도메인 엔티티 · `<resource>`=API 리소스 · `<usecase>`=응용 서비스.

---

## §1 공통 골격 (코드 조직 디렉터리)

> 루트의 인프라·툴 파일은 표준 트리에서 **생략**한다 — `docker-compose.*`·`docker/`·`Makefile`·`pyproject.toml`·`poetry.lock`/`uv.lock`·`ruff.toml`·`conftest.py`(pytest 루트)·`manage.py`(Django 진입점) 등은 프로젝트당 1개, 루트에 놓이는 게 자명하고 코드 조직과 무관하다.

```
<project_root>/
├── <project>/                  # 프로젝트(설정) 패키지
│   ├── settings/               # 환경별 분할
│   │   └── {env, dev, local, prod, test}.py
│   ├── urls.py  asgi.py  wsgi.py  celery.py
│   ├── views/                  # 프로젝트 레벨 뷰(헬스체크·랜딩 등)
│   └── static/  templates/
│
├── application/                # 모든 feature 앱의 컨테이너
│   └── <app>/  <app>/  ...     # 컨텍스트 간 통신은 각 앱의 published_service/ OHS로 (§2)
│
└── common/                     # 앱 횡단 공용
    ├── enum/                   # 도메인별 enum 집중화 (<domain>_enum.py)
    ├── django/                 # Django 의존 유틸 (task, timezone, model_util …)
    ├── ninja/                  # Django Ninja 의존 확장 (authentication, custom_type, response …)
    └── <project>/              # 프레임워크 비종속 공용 = shared kernel 대응
```

- 앱들은 루트 평면이 아니라 **`application/` 한 디렉터리 아래**로 묶인다.
- 설정 패키지(`<project>/`)는 **환경별로 분할**(`env`/`dev`/`local`/`prod`/`test`).
- 횡단 관심사는 `common/`에 모으고, 그 안을 기술축(enum·django·ninja)으로 다시 나눈다. 프레임워크에 의존하면 `common/django`·`common/ninja`로, 비종속이면 `common/<project>`로 둔다.

---

## §2 앱 4계층 전개 — `application/<app>/`

각 앱은 **4계층을 디렉터리로 물리 분리**하고, 계층 이름에 `_layer` 접미사를 쓴다. 접미사는 앱 컨테이너 `application/`과 응용 계층 `application_layer`의 이름 충돌을 해소한다.

```
application/<app>/
├── <app>_api_router.py                 # 외부 HTTP 진입점: URL/라우터 등록 (루트 urls.py가 포함)
├── published_service/                  # 컨텍스트 간 OHS — 다른 앱에 노출 (아래 "컨텍스트 간 통신")
│
├── domain_layer/                       # ① 도메인 — 의존 없음, 순수 비즈니스 (§3 전술 패턴 / §6.1)
│   └── <aggregate>/                    #   애그리거트(개념) 1차 — 예: member/  (작으면 평면, 커지면 종류 폴더)
│       ├── <aggregate>.py              #     애그리거트 루트 — 일관성 경계 (§3.3)
│       ├── entity/                     #     종속 엔티티 (§3.2): <entity>.py
│       ├── value_object/               #     값 객체 (§3.1): <value_object>.py
│       ├── repository/                 #     리포지토리 인터페이스(ABC) — DIP 포트 (§3.4). 구현은 infra
│       ├── domain_service/             #     stateless 도메인 로직 (§3.5)   [선택]
│       ├── event/                      #     도메인 이벤트 정의 (§3.7)       [선택]
│       ├── specification/              #     Specification (§3.8)          [선택]
│       └── exception.py                #     도메인 예외
│
├── application_layer/                  # ② 응용 — 유스케이스 (§3.6). domain에만 의존, 로직은 도메인 위임
│   ├── <feature>/
│   │   ├── command/                    #   쓰기 유스케이스(응용 서비스): <usecase>_app.py — domain repository 인터페이스 의존
│   │   ├── query/                      #   조회: <usecase>_query_app.py — selector/QuerySet (CQRS는 필요 컨텍스트만, §5.4)
│   │   ├── dto/                        #   입력 DTO(command 객체): <usecase>_command.py
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
├── presentation_layer/                 # ④ 표현 — 입력 어댑터 (§6.1 interface)
│   ├── api/
│   │   └── <feature>/                  #   api_<resource>.py — 얇은 어댑터(요청 파싱 → 응용 호출 → 응답·예외 변환)
│   └── schema/                         #   입출력 계약(DTO): schema_in.py / schema_out.py / error_out.py
│
└── test/                               # 앱별 테스트 — 의미군 분리 (implementation-test §4.2)
    ├── unit/                           #   순수 단위: 도메인·응용 (mock/stub)
    ├── integration/                    #   DB·리포지토리·API 어댑터 (실제 DB) — HTTP 엔드포인트 테스트는 여기
    └── e2e/                            #   엔드투엔드 흐름                               [선택]
```

의존 방향(단방향): `presentation_layer → application_layer → (domain_layer + infra_layer)`, `domain_layer`는 아무것도 의존하지 않는다.

설계 선택:
- **조직 1차 축 = 개념(애그리거트/feature), 2차 = 종류**: 각 계층을 개념 단위로 먼저 묶고(`domain_layer/<aggregate>/`, `application_layer/<feature>/`) 그 안에서 종류(`entity`/`value_object`/`command`/`query`…)로 나눈다. **단일·소규모는 평면 허용, 한 폴더에 둘 이상 개념이 섞이거나 커지면 분할**(§6.8 YAGNI). 종류 폴더에 여러 개념 파일이 구분 없이 누적되는 것을 막는 규칙이다(houserules §3 평면 금지의 2차 레벨). `infra_layer`는 기술 어댑터라 1차를 기술 묶음으로 두고, 누적 시 애그리거트별 하위 그룹핑.
- **도메인 계층은 DDD 전술 패턴으로 완전 구성**(§3·§6.1): 코어는 애그리거트 루트·`entity`·`value_object`·`repository`(인터페이스), 나머지(`domain_service`/`event`/`specification`)는 필요한 앱만(`[선택]`).
- **리포지토리 DIP**: 인터페이스(ABC)는 `domain_layer/<aggregate>/repository/`, 구현은 `infra_layer/repository/`.
- **ORM 모델 ≠ 도메인 엔티티**: 도메인은 `domain_layer/<aggregate>/`, Django 모델은 `infra_layer/django_<app>/models/`로 분리한다(Data Mapper, §6.2 — ORM이 도메인을 import, 도메인은 ORM을 모름).
- **응용 계층은 도메인에 위임하는 파사드**(§3.6): 비즈니스 로직을 직접 구현하지 않고 도메인에 위임한다. 입력은 **DTO(command 객체)**로 받는다. command/query는 구체 리포지토리를 직접 생성하지 말고 **domain repository 인터페이스에 의존**하고 구현을 주입받는다(DIP).
- **CQRS는 선택적**(§5.4 [의사결정#2]): 모든 컨텍스트에 강제하지 않는다. selector/QuerySet로 충분하면 단순 흐름을 유지하고, 읽기/쓰기 모델이 실제로 갈릴 때만 적용한다.
- **infra_layer 3분할**: `django_<app>/`(영속성) + `repository/`(접근·구현) + `service/`(외부 I/O). 구체 매핑·QuerySet/Manager·`transaction.atomic()`은 `implementation-django` §16 소유.
- **도메인 이벤트 흐름**: 발생(raise)은 `domain_layer` 애그리거트, 디스패치 타이밍은 UoW(§3.7 [의사결정#7]), 발행은 기본 **`transaction.on_commit()`**(§6.3), 외부 부수효과 유실이 치명적인 Risky Write만 **outbox**. 발행/전달 구체는 `implementation-django` §16.5·`architecture-db` §9.7 소유라 별도 `event_publisher/` 디렉터리를 두지 않는다.
- **표현 계층은 얇은 입력 어댑터**(§6.1 interface, §3.6): api는 요청 파싱 → 응용 호출 → 응답·예외 변환만 하고 비즈니스 로직을 두지 않는다. **응답은 `schema_out`(DTO)로 노출하고 도메인 엔티티를 직접 직렬화하지 않는다**(Published Language 경계). HTTP 계약·status·Ninja `Router`/`Schema`/auth 구체는 `architecture-api`·`implementation-django-ninja` 소유.
- **테스트는 의미군으로**(implementation-test §4.2): 앱별 `<app>/test/{unit,integration,e2e}/`. 도메인·응용 단위 테스트는 `unit/`, DB·리포지토리·HTTP 엔드포인트 테스트는 `integration/`. 엔드포인트별 평면 나열(`test/api/...`)은 두지 않는다.

### 컨텍스트 간 통신 — OHS (제공 컨텍스트 소유)

서로 다른 컨텍스트(앱) 간 통신은 **각 앱이 자기 공개 진입점(OHS, 오픈 호스트 서비스)을 소유**한다(§2.5/§6.7). 다른 컨텍스트는 이 `published_service/`만 import하고, 대상 앱의 `domain_layer`/`application_layer`/`infra_layer`는 **직접 import하지 않는다**.

```
application/<app>/published_service/   # 이 앱이 외부 컨텍스트에 노출하는 OHS
├── read.py       # 조회 OHS — application_layer/query에 위임 (앱이 크면 read/ 디렉터리)
└── write.py      # 커맨드 OHS — application_layer/command에 위임
```

OHS를 한 폴더(중앙 `bridge/`)에 모으지 않는다 — 한 컨텍스트의 공개 계약이 밖에 흩어지면 응집이 깨지고, 허브가 모든 컨텍스트를 아는 결합점으로 비대해진다(§2.5 "진흙공" 방어). OHS 반환도 도메인 엔티티 대신 **Published Language(DTO)**를 권장한다(presentation `schema_out`과 동일한 모델 누수 방어).

(앱별 변종: WebSocket 앱은 `<app>_asgi_router.py`·`presentation_layer/socket/`을 더 가진다. 단순 지원 앱은 `domain_layer`를 생략할 수 있다.)

---

## §3 폴더별 레퍼런스 (존재 이유 · 위치 파일)

`(코어)`는 항상 두고, `[선택]`은 트리거 조건이 맞을 때만 만든다.

**최상위 · 공용**

| 폴더 | 존재 이유 | 위치 파일 · 명명 |
|---|---|---|
| `<project>/` | 프로젝트 설정 패키지(앱 아님) | `settings/{env,dev,local,prod,test}.py`, `urls.py`·`asgi.py`·`wsgi.py`·`celery.py`(비동기 큐 쓸 때) |
| `<project>/views/` | 어느 앱에도 속하지 않는 루트/관리 뷰(헬스체크·랜딩) | 루트 뷰 모듈 |
| `<project>/{static,templates}/` | 프로젝트 레벨 정적·서버렌더 자원 | 정적 파일·템플릿 |
| `application/` | 모든 feature 앱의 컨테이너 | 앱 디렉터리 `<app>/` |
| `common/enum/` | 앱 횡단 enum 집중화 | `<domain>_enum.py` |
| `common/django/` | **Django 의존** 공용 유틸 | `task.py`·`timezone.py`·`model_util.py` |
| `common/ninja/` | **Django Ninja 의존** 공용 확장 | `authentication.py`·`custom_type.py`·`response/` |
| `common/<project>/` | **프레임워크 비종속** 공용 = shared kernel(공유 값객체·커스텀 타입) | 공유 VO·타입. ※Django/Ninja 의존 시 위 두 폴더로 |

**도메인 계층 `domain_layer/<aggregate>/` — 애그리거트(개념) 1차, 종류 2차 (§3 전술 패턴)**

| 위치 | 존재 이유 | 위치 파일 · 명명 | 코어/[선택] |
|---|---|---|---|
| `<aggregate>/` | 애그리거트 = 응집·조직 단위(예: `member/`·`order/`) | (아래 종류들을 담음) | 코어 |
| `<aggregate>/<aggregate>.py` | 애그리거트 루트 — 불변식·일관성 경계, 외부는 루트로만 접근(§3.3) | `member.py` | 코어 |
| `<aggregate>/entity/` | 식별자를 갖는 종속 엔티티(§3.2) | `<entity>.py` | 코어(작으면 루트 옆 평면) |
| `<aggregate>/value_object/` | 불변 값 객체, 자기검증(§3.1) | `<value_object>.py` | 코어(작으면 평면) |
| `<aggregate>/repository/` | 리포지토리 **인터페이스(ABC)** — DIP 포트(§3.4), 구현은 infra | `<aggregate>_repository.py` | 코어 |
| `<aggregate>/domain_service/` | 그 애그리거트 중심의 stateless 도메인 로직(§3.5) | `<name>_service.py` | [선택]; 여러 애그리거트에 걸치면 `domain_layer/` 공용 위치로 |
| `<aggregate>/event/` | 도메인 이벤트 **정의**(§3.7) | `<event>.py` | [선택] 결과적 일관성·외부 통지 필요 시 |
| `<aggregate>/specification/` | 재사용 가능한 규칙/조회 명세(§3.8) | `<name>_spec.py` | [선택] 복합 규칙을 조합·재사용할 때 |
| `<aggregate>/exception.py` | 도메인 예외 | 단일 파일(커지면 `exception/` 패키지) | 코어 |

**응용 계층 `application_layer/` — 유스케이스 파사드, domain에만 의존 (§3.6)**

| 폴더 | 존재 이유 | 위치 파일 · 명명 | 코어/[선택] 트리거 |
|---|---|---|---|
| `<feature>/command/` | 쓰기 유스케이스 — 도메인에 위임, domain `repository/` 인터페이스 의존(DIP) | `<usecase>_app.py` | 코어 |
| `<feature>/query/` | 조회 — selector/QuerySet | `<usecase>_query_app.py` | CQRS 적용 시(§5.4); 아니면 command와 합쳐도 됨 |
| `<feature>/dto/` | 유스케이스 **입력** command 객체(DTO) | `<usecase>_command.py` ※응답 DTO 아님(응답=presentation `schema_out`) | 입력 검증이 있으면 코어 |
| `<feature>/handler/` | 도메인 이벤트/커맨드 핸들러(§6.1) | `<event>_handler.py` | domain `event/` 도입 시 |
| `<feature>/service/` | 다중 유스케이스 오케스트레이션 | `<usecase>_service_app.py` | 여러 command/query를 한 흐름으로 묶을 때 |
| `unit_of_work.py` | UoW **인터페이스** — 트랜잭션 경계(§6.3) | 앱당 1개 | 구현은 `transaction.atomic()`(django §16.4)으로 충분; 커스텀 UoW 필요할 때만 |

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
| `<app>/test/` | 앱별 테스트 — **의미군 분리**(implementation-test §4.2) | `test/{unit,integration,e2e}/`. 도메인·응용 단위=`unit/`, DB·리포지토리·HTTP 엔드포인트=`integration/`. 엔드포인트별 평면 나열 금지 |
| 라우팅 | 앱 진입점 | `<app>_api_router.py` → 루트 `urls.py`가 포함 |

**앱별 변종**: WebSocket 앱은 `presentation_layer/socket/` + `<app>_asgi_router.py`를 추가한다. 단순 지원 앱은 `domain_layer`를 생략할 수 있다.

---

## 배경 (이 표준이 파생된 코퍼스)

이 표준은 아래 코퍼스 레이아웃의 구체화·변종이다. 레이아웃 권위는 이 문서가 갖고, 아래는 이론적 근거로만 인용한다(재정의하지 않는다).

- `architecture-ddd` §6.1 — 4계층 패키지 구조(`src/<context>/{domain,application,infrastructure,interface}/`). 이 표준은 같은 4계층을 `application/<app>/{..._layer}` 명명으로 구체화한 변종이다.
- `implementation-django` §3.1 — 표준 Django 레이아웃(`config/settings/` 분할 + `apps/<app>/`). 설정 분할·앱 단위 조직의 근거.
- `implementation-test` §4.2 — 테스트 의미군(`{unit,integration,e2e}`) 조직의 단독 소유자. `<app>/test/` 내부 구조가 여기서 온다.
