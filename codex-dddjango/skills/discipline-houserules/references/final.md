# dddjango 표준 파일트리

## 무엇이고 왜

이 문서는 **dddjango 플러그인이 생성하는 코드의 단일 표준 파일트리**다. `discipline-houserules` §1(파일트리 결정 순서)이 "확립된 규약이 없거나 미조직이면" 적용하라고 **위임하는 대상**이며, 레이아웃의 단일 출처다.

출처는 강한 의견의 DDD 4계층 Django 실전 프로젝트(Django Ninja 기반)이고, 각 계층 내부는 `architecture-ddd` 코퍼스(§3 전술 패턴·§6.1 패키지 구조 등)로 보강했다. 즉 코퍼스 `architecture-ddd` §6.1과 **개념은 같지만 명명·컨테이너·내부 분할이 구체화된 변종**이다 — §6.1/`implementation-django` §3.1은 이 표준이 파생된 *이론적 배경*이고, 생성 코드의 레이아웃 권위는 이 문서가 갖는다.

적용 모델은 **고정 기본값**이다. 신규·무규약 프로젝트엔 이 트리를 권위 있는 기본값으로 생성한다. 단 대상 프로젝트에 **이미 확립된 레이아웃 규약이 있으면 그것을 존중**한다(houserules §1.1 일관성 최우선) — 이 표준을 기존 규약 위에 강제하지 않는다.

표준이므로 도메인 비종속 **placeholder**로 적는다.

> **placeholder 범례**: `<project>`=프로젝트(설정) 패키지명 · `<app>`=feature 앱 · `<feature>`=앱 내 유스케이스 묶음 · `<aggregate>`=애그리거트(개념) · `<entity>`=도메인 엔티티 · `<resource>`=API 리소스 · `<usecase>`=응용 서비스.

---

## §0 불변식 — 생략·축소 불가

대상 프로젝트에 **확립된 규약이 없어 이 표준을 적용할 때**, 아래는 YAGNI·단순성·"단일 기능이라 불필요" 같은 판단으로 **생략하거나 평면으로 접을 수 없다 — 항상 생성한다**. (이미 다른 레이아웃 규약이 확립된 기존 프로젝트는 §1.1대로 그 규약을 존중한다 — 이 불변식은 *표준을 새로 까는* 경우의 규칙이다.)

1. **`application/` 컨테이너** — 앱은 루트 평면이 아니라 `application/<app>/` 아래에 둔다. 단일 앱이어도 컨테이너를 만든다. **데이터소스 앱(판정 없이 필드·DB 제약만)도 위치는 예외 없이 `application/<app>/`다** — `architecture-ddd` §632-(2)의 "평면 유지"는 *4계층(애그리거트) 전개 면제*이지 *위치(루트 허용) 면제가 아니다*. 이번 작업이 touched한 앱이 루트 평면(`<app>/`)에 있으면 §0-1 위반이고, 이번 작업이 안 건드린 무관 기존 앱은 §1.1로 존중한다.
2. **4계층 디렉터리** — `domain_layer/`·`application_layer/`·`infra_layer/`·`presentation_layer/`를 모두 물리 분리한다(`_layer` 접미사 포함). **계층에 들어갈 내용물이 없어도 그 계층 폴더는 빈 패키지(`__init__.py`만)로라도 항상 생성한다** — 예: HTTP/CLI 표현 없이 ACL·`published_service`로만 소비되는 내부 전용 BC의 `presentation_layer`도 빈 폴더로 둔다. "이 BC엔 표현(또는 도메인) 관심사가 없다"는 판단으로 **계층 폴더 자체를 생략하지 않는다**(종류 2차 폴더의 빈 패키지 규칙(4항)과 같은 원칙 — §6.8 YAGNI는 계층·종류 골격에 적용하지 않는다).
3. **개념 1차 폴더** — `domain_layer/<aggregate>/`, `application_layer/<feature>/`.
4. **종류 2차 폴더 전체** — `entity/`·`value_object/`·`repository/` 등(domain), `command/`·`query/`·`dto/` 등(application)을 **항상 폴더로 생성**한다. 내용이 없으면 빈 패키지(`__init__.py`만)로 둔다 — 평면 파일(`repository.py`)로 접지 않는다. 빈 폴더의 `__init__.py`는 **유지한다(regular package)** — git은 빈 디렉터리를 추적하지 않으므로 이 파일이 골격을 버전관리에 존속시키고, Django `migrations/`·앱 패키지도 `__init__.py`를 요구한다. PEP 420(namespace package)을 이유로 `__init__.py`를 지우지 않는다. (`[선택]` 마커는 "비어 있을 수 있음"이지 *생략 가능*이 아니다.) 단 이 종류-폴더 항상-생성은 위에 열거한 domain·application 종류(`entity`/`value_object`/`repository`·`command`/`query`/`dto` 등)에 한정한다 — `presentation_layer`의 종류 2차 폴더(`api/`·`schema/`)는 *표현 내용이 생길 때* 만든다. 표현이 없는 내부 전용 BC의 빈 `presentation_layer`는 계층 패키지(`__init__.py`)만 두고 `api/`·`schema/`까지 미리 만들지 않는다(항상-생성 골격은 §0-2 계층 수준 + 이 종류 폴더에 한정; 깊이 적정성은 discipline-reviewer 의미 체크 몫).
5. **Django 앱은 `infra_layer/django_<app>/`** — `startapp`을 그 안에서 수행한다. ORM 모델·`migrations/`·`apps.py`가 거기 산다. 앱 루트나 도메인 패키지에 `models.py`를 두지 않는다(§2 "Django 앱 성립" 참조).
6. **ORM 모델 명명** — 도메인 엔티티/애그리거트는 bare 이름(`Order`), Django ORM 모델 클래스는 `<Name>Model`(`OrderModel`)로 구분한다(상세 §4 명명 규약).

이 불변식은 `discipline-houserules` SKILL.md 본문에도 체크리스트로 요약되어, 스킬을 로드하는 모든 행위자(design-architect·coder·discipline-reviewer)에게 전달된다. design-architect는 명세에서 이를 생략·축소할 수 없고, discipline-reviewer는 *명세가 아니라 이 불변식*과 코드를 대조한다.

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
- **`common/`은 *프로젝트 루트*에 둔다(= `application/`의 형제) — `application/common/`처럼 `application/`(feature 앱 컨테이너) *안*에 넣지 않는다.** 단일 BC 전용 헬퍼(problem 등)는 그 BC `application/<app>/presentation_layer/`에 두고, 2개 이상 BC가 *실제로* 공유할 때만 루트 `common/`으로 승격한다(YAGNI — 횡단이 생기기 전 조기 승격 금지; `implementation-django-ninja` §6.2·§6.3).

---

## §2 앱 4계층 전개 — `application/<app>/`

각 앱은 **4계층을 디렉터리로 물리 분리**하고, 계층 이름에 `_layer` 접미사를 쓴다. 접미사는 앱 컨테이너 `application/`과 응용 계층 `application_layer`의 이름 충돌을 해소한다.

```
application/<app>/
├── <app>_api_router.py                 # 외부 HTTP 진입점: URL/라우터 등록 (루트 urls.py가 포함)
├── published_service/                  # 컨텍스트 간 OHS — 다른 앱에 노출 (아래 "컨텍스트 간 통신")
│
├── domain_layer/                       # ① 도메인 — 의존 없음, 순수 비즈니스 (§3 전술 패턴 / §6.1)
│   └── <aggregate>/                    #   애그리거트(개념) 1차 — 예: member/  (종류 폴더는 항상 생성, 비어도 둠 §0)
│       ├── <aggregate>.py              #     애그리거트 루트 — 일관성 경계 (§3.3)
│       ├── entity/                     #     종속 엔티티 (§3.2): <entity>.py
│       ├── value_object/               #     값 객체 (§3.1): <value_object>.py
│       ├── repository/                 #     리포지토리 인터페이스(ABC) — DIP 포트 (§3.4). 구현은 infra
│       ├── port/                       #     외부 컨텍스트 협력 포트(ACL 포트) — 다른 컨텍스트 소비 시  [통합 시]
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
├── infra_layer/                        # ③ 인프라 — ORM·외부 I/O·컨텍스트 어댑터
│   ├── django_<app>/                   #   Django 영속성 (도메인 엔티티와 별개의 ORM 모델)
│   │   ├── apps.py
│   │   ├── models/                     #     <entity>_model.py
│   │   ├── migrations/
│   │   └── admin/                      #     <entity>_admin.py (+ templates/)
│   ├── repository/                     #   domain repository 인터페이스(ABC) 구현 — ORM↔도메인 변환 (DIP). 자기 애그리거트 전용
│   ├── acl/                            #   외부 컨텍스트 ACL 어댑터(domain port/ 구현) — 업스트림 모델·예외 번역  [통합 시]
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
- **조직 1차 축 = 개념(애그리거트/feature), 2차 = 종류**: 각 계층을 개념 단위로 먼저 묶고(`domain_layer/<aggregate>/`, `application_layer/<feature>/`) 그 안에서 종류(`entity`/`value_object`/`command`/`query`…)로 나눈다. **종류 2차 폴더는 항상 생성한다**(§0 불변식) — 내용이 없으면 빈 패키지로 두되 평면 파일로 접지 않는다(단 이 항상-생성은 domain·application 종류 폴더에 한정 — `presentation_layer`의 `api/`·`schema/`는 표현 내용이 생길 때 만든다, §0-4). **§6.8 YAGNI는 골격에 적용하지 않는다**(YAGNI = 아직 없는 새 애그리거트/feature를 미리 만들지 마라; 컨테이너·계층·종류 폴더 골격은 항상 실현). 종류 폴더에 여러 개념 파일이 구분 없이 누적되는 것을 막는 규칙이다(houserules §3 평면 금지의 2차 레벨). `infra_layer`는 기술 어댑터라 1차를 기술 묶음으로 두고, 누적 시 애그리거트별 하위 그룹핑.
- **도메인 계층은 DDD 전술 패턴으로 완전 구성**(§3·§6.1): 코어는 애그리거트 루트·`entity`·`value_object`·`repository`(인터페이스), 나머지(`domain_service`/`event`/`specification`)는 폴더를 항상 두되 트리거 미충족 시 비어 있을 수 있다(`[선택]`=비어 있을 수 있음, 생략 아님 §0).
- **리포지토리 DIP**: 인터페이스(ABC)는 `domain_layer/<aggregate>/repository/`, 구현은 `infra_layer/repository/`. 추상화·구현 명명은 §4 명명 규약(추상=개념 bare명 `OrderRepository`, 구현=`Django…` 한정자 접두).
- **ORM 모델 ≠ 도메인 엔티티**: 도메인은 `domain_layer/<aggregate>/`, Django 모델은 `infra_layer/django_<app>/models/`로 분리한다(Data Mapper, §6.2 — ORM이 도메인을 import, 도메인은 ORM을 모름). 이름으로도 구분하며(`Order` vs `OrderModel`) 명명 상세는 §4. 변환은 `infra_layer/repository/`(ORM↔도메인 Data Mapper)와 표현 `schema_out`(도메인→응답 DTO)이 담당한다.
- **응용 계층은 도메인에 위임하는 파사드**(§3.6): 비즈니스 로직을 직접 구현하지 않고 도메인에 위임한다. 입력은 **DTO(command 객체)**로 받는다. command/query는 구체 리포지토리를 직접 생성하지 말고 **domain repository 인터페이스에 의존**하고 구현을 주입받는다(DIP).
- **CQRS는 선택적**(§5.4 [의사결정#2]): 모든 컨텍스트에 강제하지 않는다. selector/QuerySet로 충분하면 단순 흐름을 유지하고, 읽기/쓰기 모델이 실제로 갈릴 때만 적용한다.
- **infra_layer 분할**: `django_<app>/`(영속성) + `repository/`(자기 애그리거트 접근·구현) + `acl/`(외부 컨텍스트 ACL 어댑터, [통합 시]) + `service/`(외부 I/O). 구체 매핑·QuerySet/Manager·`transaction.atomic()`은 `implementation-django` §16 소유.
- **컨텍스트 간 통신 = OHS 우선, 직접 통합은 ACL로 분리**: 다른 바운디드 컨텍스트는 그 앱의 `published_service/`(OHS)로 소비하는 게 기본이다(아래 "컨텍스트 간 통신"). OHS가 없거나(미이주) 단일 트랜잭션·행 잠금이 불가피하면 ACL로 명시 — 도메인은 협력 포트(`domain_layer/<aggregate>/port/`)로 의존하고 구현(업스트림 모델·예외 번역)은 `infra_layer/acl/`에 가둔다. **ACL은 리포지토리가 아니므로 `repository/`에 섞지 않는다**(architecture-ddd 컨텍스트 맵 ACL 패턴 — 업스트림 모델을 하류 모델로 번역).
- **통합 스타일 선택(동기 ACL/OHS vs 비동기 이벤트)**: BC 간 통합에서 **즉시 일관성**이 필요하면(예: 재고 차감 — 오버셀 차단) 동기로 OHS/ACL을, **결과적 일관성**으로 충분하면(예: 주문 후 포인트 적립·알림) 비동기로 **도메인 이벤트**를 쓴다. 도메인 이벤트는 *애그리거트 간* 결과적 일관성에도 쓰여 ACL보다 범위가 넓다(ACL은 BC 간 동기 번역 전용). **선택 기준은 `architecture-ddd` 규칙4(일관성 경계 밖=결과적 일관성)·§6.8 패턴 선택 절차에 위임**한다 — 이 표준은 *어디 두는지*만 정하고 *언제 무엇*의 패턴 선택 이론은 코퍼스가 권위다.
- **Django 앱 성립 (infra_layer 안)**: Django `startapp`은 `infra_layer/django_<app>/`에서 수행한다 — `apps.py`의 `AppConfig.name`을 그 전체 점경로(`application.<app>.infra_layer.django_<app>`)로, `label='<app>'`로 둔다. 그러면 `models/`·`migrations/`가 그 앱 아래에서 native하게 발견된다(단일 앱 라벨에 모델·마이그레이션을 귀속시키려 우회할 필요가 없다). 설정의 `INSTALLED_APPS`에 그 점경로를 등록한다. **앱 루트(`application/<app>/`)나 도메인 패키지에 `models.py`를 두지 않는다** — 도메인 컨텍스트 `<app>`와 Django 영속성 앱 `django_<app>`는 별개이고, 도메인 `<app>/`는 Django 앱이 아니라 순수 패키지다.
- **도메인 이벤트 흐름**: 발생(raise)은 `domain_layer` 애그리거트, 디스패치 타이밍은 UoW(§3.7 [의사결정#7]), 발행은 기본 **`transaction.on_commit()`**(§6.3), 외부 부수효과 유실이 치명적인 Risky Write만 **outbox**. 발행/전달 구체는 `implementation-django` §16.5·`architecture-db` §9.7 소유라 별도 `event_publisher/` 디렉터리를 두지 않는다.
- **표현 계층은 얇은 입력 어댑터**(§6.1 interface, §3.6): api는 요청 파싱 → 응용 호출 → 응답·예외 변환만 하고 비즈니스 로직을 두지 않는다. **응답은 `schema_out`(DTO)로 노출하고 도메인 엔티티를 직접 직렬화하지 않는다**(Published Language 경계). HTTP 계약·status·Ninja `Router`/`Schema`/auth 구체는 `architecture-api`·`implementation-django-ninja` 소유.
- **테스트는 의미군으로**(implementation-test §4.2): 앱별 `<app>/test/{unit,integration,e2e}/`. 도메인·응용 단위 테스트는 `unit/`, DB·리포지토리·HTTP 엔드포인트 테스트는 `integration/`. 엔드포인트별 평면 나열(`test/api/...`)은 두지 않는다.

### 컨텍스트 간 통신 — OHS (제공 컨텍스트 소유)

서로 다른 컨텍스트(앱) 간 통신은 **각 앱이 자기 공개 진입점(OHS, 오픈 호스트 서비스)을 소유**한다(§2.5/§6.7). 다른 컨텍스트는 이 `published_service/`만 import하고, 대상 앱의 `domain_layer`/`application_layer`/`infra_layer`는 **직접 import하지 않는다**. **DB FK도 cross-context 결합이다 — 타 BC 모델을 ORM `ForeignKey`/`OneToOneField`/`ManyToManyField`로 참조하지 않는다(BC 경계 ORM FK 금지). 타 BC는 ID 값으로 참조하고 존재 검증은 OHS/ACL 포트로 하며, 같은 BC 내 FK는 허용한다(`architecture-ddd` §3.3 규칙3 영속성 확장).**

```
application/<app>/published_service/   # 이 앱이 외부 컨텍스트에 노출하는 OHS
├── read.py       # 조회 OHS — application_layer/query에 위임 (앱이 크면 read/ 디렉터리)
└── write.py      # 커맨드 OHS — application_layer/command에 위임
```

OHS를 한 폴더(중앙 `bridge/`)에 모으지 않는다 — 한 컨텍스트의 공개 계약이 밖에 흩어지면 응집이 깨지고, 허브가 모든 컨텍스트를 아는 결합점으로 비대해진다(§2.5 "진흙공" 방어). OHS 반환도 도메인 엔티티 대신 **Published Language(DTO)**를 권장한다(presentation `schema_out`과 동일한 모델 누수 방어).

**소비 측(다른 컨텍스트를 부를 때)**: 기본은 대상 앱의 `published_service/`(OHS)만 import한다. 대상 컨텍스트가 아직 OHS를 노출하지 않거나(미이주) 단일 트랜잭션·행 잠금이 필요해 직접 접근이 불가피하면, 그 통합을 **ACL(부패 방지 계층)로 명시**한다 — 도메인은 협력 포트(`domain_layer/<aggregate>/port/`)로만 의존하고, 구현(업스트림 모델·예외 번역)은 `infra_layer/acl/`에 가둔다. **ACL은 리포지토리가 아니므로 `repository/`에 섞지 않는다.** **업스트림의 모델·예외 번역은 ACL 안에 격리한다 — presentation·application이 타 BC의 예외(`domain_layer` 하위)를 직접 `import`해 잡으면 컨텍스트 결합이 ACL 밖으로 새므로, ACL이 협력 포트가 던지는 우리 쪽 예외로 번역(동일 의미면 명시적 재노출)해 넘긴다.** 대상이 OHS를 노출하면 ACL 구현을 OHS 호출로 교체하고 포트는 유지한다(이 표준의 통합 진화 지침 — architecture-ddd 컨텍스트 맵의 ACL·OHS 패턴을 토대로 한 합성이며, 코퍼스가 "ACL→OHS 진화"를 명시하는 것은 아니다).

(앱별 변종: WebSocket 앱은 `<app>_asgi_router.py`·`presentation_layer/socket/`을 더 가진다. 단순 지원 앱이라도 컨테이너·4계층 폴더는 모두 유지한다 — `domain_layer`를 포함해 어느 계층 폴더도 생략하지 않고, 내용이 없으면 빈 패키지로 둔다(§0-2). 도메인 모델이 없는 앱이라도 빈 `domain_layer`는 존속시키고, 계층을 접을 실질 사유가 있으면 명세에 silent하게 박지 말고 G1 트레이드오프로 올린다.)

---

## §3 폴더별 레퍼런스 (존재 이유 · 위치 파일)

`(코어)`는 항상 두고, `[선택]`(코드 골격)은 폴더를 항상 생성하되 트리거 조건 미충족 시 비어 있을 수 있다(생략 아님 — §0 불변식). 단 **테스트 의미군**(`e2e/` 등)은 `implementation-test` §4.2 소관이라 거기선 `e2e`가 진짜 선택이다(코드 골격 불변식과 별개). 마찬가지로 **`[통합 시]` ACL 폴더**(`domain_layer/<aggregate>/port/`·`infra_layer/acl/`)는 *통합 패턴*이라(architecture-ddd: ACL을 기본 도입하지 않음) 다른 컨텍스트를 직접 소비할 때만 생성한다 — 없으면 폴더를 두지 않는다(빈 폴더를 항상 두는 `[선택]`과 다르고, 골격 불변식과 별개).

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

> 위 `common/*`은 모두 *프로젝트 루트* `common/`(= `application/`의 형제) 아래다 — `application/common/`이 아니다. **그리고 횡단 배치는 *2개 이상 BC가 실제로 공유할 때*만 한다**: 단일 BC 전용 헬퍼(problem 등)는 그 BC `application/<app>/presentation_layer/`에 두고, 공유가 생긴 뒤 루트 `common/`으로 승격한다(YAGNI; `implementation-django-ninja` §6.2).

**도메인 계층 `domain_layer/<aggregate>/` — 애그리거트(개념) 1차, 종류 2차 (§3 전술 패턴)**

| 위치 | 존재 이유 | 위치 파일 · 명명 | 코어/[선택] |
|---|---|---|---|
| `<aggregate>/` | 애그리거트 = 응집·조직 단위(예: `member/`·`order/`) | (아래 종류들을 담음) | 코어 |
| `<aggregate>/<aggregate>.py` | 애그리거트 루트 — 불변식·일관성 경계, 외부는 루트로만 접근(§3.3) | `member.py` | 코어 |
| `<aggregate>/entity/` | 식별자를 갖는 종속 엔티티(§3.2) | `<entity>.py` | 코어(폴더 항상 생성) |
| `<aggregate>/value_object/` | 불변 값 객체, 자기검증(§3.1) | `<value_object>.py` | 코어(폴더 항상 생성) |
| `<aggregate>/repository/` | 리포지토리 **인터페이스(ABC)** — DIP 포트(§3.4), 구현은 infra | `<aggregate>_repository.py` → `class OrderRepository`(bare 개념명) | 코어 |
| `<aggregate>/port/` | 외부 컨텍스트 **협력 포트(ACL 포트, ABC)** — 다른 컨텍스트를 소비할 때 도메인이 의존하는 역할 포트 | `<collaborator>_port.py` → `class ProductLockPort` | [통합 시] 다른 컨텍스트 소비할 때만 |
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
| `django_<app>/models/` | Django ORM 모델(**도메인 엔티티와 별개**; 클래스명 `<Name>Model`) | `<entity>_model.py` (예: `order_model.py` → `class OrderModel`) |
| `django_<app>/migrations/` | DB 마이그레이션 | (Django 자동 생성) |
| `django_<app>/admin/` | Django admin 등록·커스텀 | `<entity>_admin.py`(+`templates/` admin 전용) |
| `django_<app>/apps.py` | AppConfig — `name='application.<app>.infra_layer.django_<app>'`, `label='<app>'` (이 점경로를 INSTALLED_APPS에 등록; 앱 루트에 `models.py` 금지) | `apps.py` |
| `repository/` | domain `repository/` ABC **구현** + ORM↔도메인 변환(Data Mapper §6.2). **자기 애그리거트 전용** | `<aggregate>_repository.py` → `class DjangoOrderRepository`(구현=기술 한정자 접두) |
| `acl/` | 외부 컨텍스트 **ACL 어댑터** — domain `port/` ABC 구현, 업스트림 모델·예외를 우리 모델로 번역. 리포지토리와 분리([통합 시]) | `<context>_acl.py` → `class DjangoProductLockPort` |
| `service/` | **외부 서비스** 어댑터(인증·푸시·결제 등) | `<external>_service.py` ※`domain_service`와 구분(외부 I/O 전용) |

**표현 계층 `presentation_layer/` · 컨텍스트 통신 · 테스트**

| 폴더 | 존재 이유 | 위치 파일 · 명명 |
|---|---|---|
| `api/<feature>/` | HTTP **입력 어댑터**(얇게, §6.1 interface) | `api_<resource>.py` (Ninja Router) |
| `schema/` | 입출력 계약 DTO(Ninja Schema) | `schema_in.py`·`schema_out.py`·`error_out.py`(feature가 많으면 `<feature>/`로 분할) — **응답은 `schema_out`**, 도메인 직접 노출 금지 |
| `<app>/published_service/` | 컨텍스트 간 **OHS**(다른 앱에 노출, §2.5/§6.7) | `read.py`·`write.py`(앱이 크면 `read/`·`write/` 디렉터리). 다른 앱은 **이것만** import |
| `<app>/test/` | 앱별 테스트 — **의미군 분리**(implementation-test §4.2) | `test/{unit,integration,e2e}/`. 도메인·응용 단위=`unit/`, DB·리포지토리·HTTP 엔드포인트=`integration/`. 엔드포인트별 평면 나열 금지 |
| 라우팅 | 앱 진입점 | `<app>_api_router.py` → 루트 `urls.py`가 포함 |

**앱별 변종**: WebSocket 앱은 `presentation_layer/socket/` + `<app>_asgi_router.py`를 추가한다. 단순 지원 앱이라도 컨테이너·4계층 폴더는 모두 유지한다 — `domain_layer` 포함 어느 계층도 폴더를 생략하지 않고 내용이 없으면 빈 패키지로 둔다(§0-2); 계층을 접을 실질 사유가 있으면 명세에 silent하게 박지 말고 G1 트레이드오프로 올린다.

---

## §4 명명 규약

명명은 트리 전반(§1~§3)에 걸친 횡단 규약이라 여기 한곳에 모은다 — **이 절이 단일 출처**이고, §0 불변식·§2 설계 선택·§3 표는 위치/구조를 정하며 명명 세부는 이 절을 가리킨다.

**도메인 ↔ ORM** — 같은 개념의 두 표현을 이름으로 구분한다.
- 도메인 엔티티/애그리거트 = **bare 이름**(`Order`; `domain_layer/<aggregate>/`).
- Django ORM 모델 클래스 = **`<Name>Model`**(`OrderModel`; 파일 `<entity>_model.py`, `infra_layer/django_<app>/models/`).
- 왜: ORM ≠ 도메인(Data Mapper §6.2). 이름이 갈려야 호출부가 어느 표현을 다루는지 분명하다(§0 불변식 6). 변환은 `infra_layer/repository/`·표현 `schema_out`이 담당한다.

**추상화(포트) ↔ 구현(어댑터)** — 추상화가 개념의 "진짜 이름"을 갖는다(DDD·헥사고날 관용).
- 추상화(리포지토리 인터페이스·기타 포트 ABC) = 도메인 개념 + **역할 접미사**(`OrderRepository`·`ProductLockPort`·`PaymentGateway`). `Repository`/`Port`/`Gateway`처럼 그 객체의 *역할*을 나타내는 접미사는 이름의 일부라 허용한다.
- 구현 = 추상화 **전체 이름에 기술·출처 한정자를 접두**(`DjangoOrderRepository`·`DjangoProductLockPort`·`InMemoryOrderRepository`·`FakeOrderRepository`). 추상화와 **base명을 일치**시킨다(역할 접미사를 떼지 않는다) — 그래야 어느 추상화의 구현인지 이름만으로 드러나고 감수가 위반을 적발할 수 있다(`ProductLockPort`의 구현은 `DjangoProductLockPort`이지 `DjangoProductLock`이 아니다).
- 금지: `Interface`/`Impl`처럼 추상/구현 *구분만을 위한 타입 표식* 접미사(`OrderRepositoryInterface`·`OrderRepositoryImpl` ✕). 추상/구현은 한정자 유무로 이미 구분된다(PEP 8). 역할 접미사(`Port`)와 타입 표식(`Interface`)의 차이: 전자는 객체의 *역할*, 후자는 추상/구현 *구분*용이라 금지한다.

**파일명** — 파일명은 그 안의 주 클래스·개념을 **약어 없이** 반영한다: `order_repository.py`(○) / `order_repo.py`(✕). grep·예측 가능성을 위해 클래스명을 줄이지 않듯 파일명도 줄이지 않는다.

---

## 배경 (이 표준이 파생된 코퍼스)

이 표준은 아래 코퍼스 레이아웃의 구체화·변종이다. 레이아웃 권위는 이 문서가 갖고, 아래는 이론적 근거로만 인용한다(재정의하지 않는다).

- `architecture-ddd` §6.1 — 4계층 패키지 구조(`src/<context>/{domain,application,infrastructure,interface}/`). 이 표준은 같은 4계층을 `application/<app>/{..._layer}` 명명으로 구체화한 변종이다.
- `implementation-django` §3.1 — 표준 Django 레이아웃(`config/settings/` 분할 + `apps/<app>/`). 설정 분할·앱 단위 조직의 근거.
- `implementation-test` §4.2 — 테스트 의미군(`{unit,integration,e2e}`) 조직의 단독 소유자. `<app>/test/` 내부 구조가 여기서 온다.
