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

1. **`application/` 컨테이너** — 새로 만드는 앱·바운디드 컨텍스트는 루트 평면이 아니라 `application/<app>/` 아래에 둔다. 단일 앱이어도 컨테이너를 만든다. **기존 Django persistence 앱은 touched 여부와 무관하게 grandfather**하므로 루트 평면이어도 옮기지 않는다. 새 domain/application 코드는 repository/adapter를 통해 그 ORM을 감싼다.
2. **4계층 디렉터리** — `domain_layer/`·`application_layer/`·`infra_layer/`·`presentation_layer/`를 모두 물리 분리한다(`_layer` 접미사 포함). **계층에 들어갈 내용물이 없어도 그 계층 폴더는 빈 패키지(`__init__.py`만)로라도 항상 생성한다** — 예: HTTP/CLI 표현 없이 ACL·`published_service`로만 소비되는 내부 전용 BC의 `presentation_layer`도 빈 폴더로 둔다. "이 BC엔 표현(또는 도메인) 관심사가 없다"는 판단으로 **계층 폴더 자체를 생략하지 않는다**(종류 2차 폴더의 빈 패키지 규칙(4항)과 같은 원칙 — §6.8 YAGNI는 계층·종류 골격에 적용하지 않는다).
3. **개념 1차 폴더** — `domain_layer/<aggregate>/`, `application_layer/<feature>/`.
4. **종류 2차 폴더 전체** — `entity/`·`value_object/`·`repository/` 등(domain), `command/`·`query/`·`dto/` 등(application)을 **항상 폴더로 생성**한다. 내용이 없으면 빈 regular package(`__init__.py`만)로 두고 평면 파일(`repository.py`)로 접지 않는다. git이 빈 디렉터리를 추적하지 않으므로 이 파일이 골격을 버전관리에 존속시킨다. PEP 420을 이유로 `__init__.py`를 지우지 않는다. (`[선택]`은 "비어 있을 수 있음"이지 *생략 가능*이 아니다.) 이 규칙은 domain·application 종류와 `presentation_layer`의 `api/`·`schema/`에 적용한다. migration 경로는 이 골격 생성 규칙의 대상이 아니다(5항).
5. **확립된 기존 규약이 없어 이 표준을 적용하는 신규 Django 앱은 `infra_layer/django_<app>/`** — ORM 모델·`apps.py`를 그 안에 두고 신규 앱 루트나 도메인 패키지에 `models.py`를 두지 않는다(§2 "Django 앱 성립" 참조). dddjango는 `startapp`이 생성하는 `migrations/__init__.py`를 포함해 migration 경로를 스캐폴딩하지 않는다. G0 전에 framework/external owner가 만든 `migrations/`가 이미 있을 수는 있으나, dddjango는 그 경로를 추가·수정·삭제·이동하지 않는다.
6. **ORM 모델 명명·테이블명** — 도메인 엔티티/애그리거트는 bare 이름(`Order`), Django ORM 모델 클래스는 `<Name>Model`(`OrderModel`)로 구분하고, **신규 모델은 `Meta.db_table`을 `<app_label>_<entity_snake>`**(`Model` 접미 제거·snake; `abstract`/`proxy`/`managed=False` 면제)로 명시한다(상세 §4 명명 규약).
7. **Brownfield 보존** — 기존 Django persistence 앱을 `infra_layer/django_<app>/`로 물리적으로 이주하지 않는다. 옛 루트·`INSTALLED_APPS`·`AppConfig`·`migrations/`·`MIGRATION_MODULES`를 현위치에 보존한다. 새 domain/application 패키지가 따로 존재하는 것은 repository/adapter 경계를 갖춘 합법적 공존이지 미완 이주가 아니다.

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
├── application/                # 새 feature 앱·domain/application 코드의 컨테이너
│   └── <app>/  <app>/  ...     # 컨텍스트 간 통신은 각 앱의 published_service/ OHS로 (§2)
│
└── common/                     # 앱 횡단 공용
    ├── enum/                   # 도메인별 enum 집중화 (<domain>_enum.py)
    ├── django/                 # Django 의존 유틸 (task, timezone, model_util …)
    ├── ninja/                  # Django Ninja 의존 확장 (authentication, custom_type, response …)
    └── <project>/              # 프레임워크 비종속 공용 = shared kernel 대응
```

- 이 표준으로 새로 만드는 앱들은 루트 평면이 아니라 **`application/` 한 디렉터리 아래**로 묶는다. 기존 persistence 앱은 §0-1의 grandfather 예외다.
- 설정 패키지(`<project>/`)는 **환경별로 분할**(`env`/`dev`/`local`/`prod`/`test`).
- 횡단 관심사는 `common/`에 모으고, 그 안을 기술축(enum·django·ninja)으로 다시 나눈다. 프레임워크에 의존하면 `common/django`·`common/ninja`로, 비종속이면 `common/<project>`로 둔다.
- **`common/`은 *프로젝트 루트*에 둔다(= `application/`의 형제) — `application/common/`처럼 `application/`(feature 앱 컨테이너) *안*에 넣지 않는다.** 단일 BC 전용 헬퍼(problem 등)는 그 BC `application/<app>/presentation_layer/`에 두고, 2개 이상 BC가 *실제로* 공유할 때만 루트 `common/`으로 승격한다(YAGNI — 횡단이 생기기 전 조기 승격 금지; `implementation-django-ninja` §6.2·§6.3).
- **`common/enum/` 승격은 공유 커널 결정이다** — 같은 철자를 넘어 같은 *지식*이고, 두 BC가 같은 변경 사유로 함께 수정된다는 근거가 명세에 있을 때만(`architecture-ddd` §2.5 공유 커널 — 공유 범위 최소화 필수). BC 내부 enum은 그 BC `domain_layer` 소유이고 다른 BC가 직접 import하지 않는다 — 같은 wire 값의 BC별 각자 선언은 중복이 아니라 published language 수용이다. **승격된 공유 커널(`common/enum/`·`common/<project>/`)은 도메인의 일부로 취급되어 domain_layer가 의존할 수 있는 유일한 외부다**(§2 "domain은 아무것도 의존하지 않는다"의 명시 예외 — 프레임워크 비종속이 조건).

---

## §2 앱 4계층 전개 — `application/<app>/`

이 표준으로 새로 만드는 각 앱은 **4계층을 디렉터리로 물리 분리**하고, 계층 이름에 `_layer` 접미사를 쓴다. 기존 persistence 앱은 물리 분리 대상이 아니다. 접미사는 앱 컨테이너 `application/`과 응용 계층 `application_layer`의 이름 충돌을 해소한다.

```
application/<app>/
├── <app>_api_router.py                 # 외부 HTTP 진입점: config의 NinjaExtraAPI를 import해 register_controllers로 BC 로컬 등록 (루트 urls.py 포함은 함수형 Router 경로)
├── composition_root.py                 # DI 조립 배선: build_<usecase>_command() 팩토리로 구체 infra를 use-case에 매요청 주입(presentation은 호출만=Q-7 짝). application 로직(command/query/service) 가진 BC는 반드시 둔다·데이터소스 BC 생략
├── published_service/                  # 컨텍스트 간 OHS — 서비스(개념) 1차·contract 계약 패키지 (아래 "컨텍스트 간 통신")
│
├── domain_layer/                       # ① 도메인 — 의존 없음, 순수 비즈니스 (§3 전술 패턴 / §6.1)
│   └── <aggregate>/                    #   애그리거트(개념) 1차 — 예: member/  (종류 폴더는 항상 생성, 비어도 둠 §0)
│       ├── <aggregate>.py              #     애그리거트 루트 — 일관성 경계 (§3.3)
│       ├── entity/                     #     종속 엔티티 (§3.2): <entity>.py
│       ├── value_object/               #     값 객체 (§3.1): <value_object>.py
│       ├── repository/                 #     리포지토리 인터페이스(ABC) — DIP 포트 (§3.4). 구현은 infra
│       ├── port/                       #     외부 컨텍스트 협력 포트(ACL 포트) — 폴더 항상·코드는 소비 시  [선택]
│       ├── domain_service/             #     stateless 도메인 로직 (§3.5)   [선택]
│       ├── event/                      #     도메인 이벤트 정의 (§3.7); 발행 discriminator enum = event_type.py (birth-enum, `architecture-ddd` §3.7) [선택]
│       ├── specification/              #     Specification (§3.8)          [선택]
│       └── exception.py                #     도메인 예외
│
├── application_layer/                  # ② 응용 — 유스케이스 (§3.6). domain에만 의존, 로직은 도메인 위임
│   ├── <feature>/
│   │   ├── command/                    #   쓰기 유스케이스 연산: <usecase>_command.py → class …Command.execute(request) — domain repository/port 의존
│   │   ├── query/                      #   조회 유스케이스 연산: <usecase>_query.py → class …Query.execute(request) — repository 의존 (별도 읽기모델 CQRS는 §5.4 선택)
│   │   ├── dto/                        #   유스케이스 입력 DTO: <usecase>_request.py → @dataclass class …Request
│   │   ├── handler/                    #   도메인 이벤트 핸들러 (§6.1)                    [선택]
│   │   └── service/                    #   다중 유스케이스 오케스트레이션: <flow>_service.py  [선택]
│   └── unit_of_work.py                 #   UoW 인터페이스 — 트랜잭션 경계 (§6.3)          [선택]
│
├── infra_layer/                        # ③ 인프라 — ORM·외부 I/O·컨텍스트 어댑터
│   ├── django_<app>/                   #   Django 영속성 (도메인 엔티티와 별개의 ORM 모델)
│   │   ├── apps.py
│   │   ├── models/                     #     <entity>_model.py
│   │   ├── migrations/                      # G0 전에 외부가 만든 경우만 존재; framework/external-owned
│   │   └── admin/                      #     <entity>_admin.py (+ templates/)
│   ├── repository/                     #   domain repository 인터페이스(ABC) 구현 — ORM↔도메인 변환 (DIP). 자기 애그리거트 전용
│   ├── acl/                            #   외부 컨텍스트 ACL 어댑터(domain port/ 구현) — 폴더 항상·코드는 통합 시  [선택]
│   └── adapter/                        #   외부 서비스 어댑터: stripe_payment_gateway.py (인증·푸시·결제 등)
│
├── presentation_layer/                 # ④ 표현 — 입력 어댑터 (§6.1 interface)
│   ├── api/
│   │   └── <feature>/                  #   <aggregate>_controller.py(@api_controller 클래스, 함수형 레거시 api_<resource>.py) — 얇은 어댑터(요청 파싱 → 응용 호출 → 응답·예외 변환)
│   └── schema/                         #   입출력 계약(DTO): schema_in.py / schema_out.py / error_out.py
│
└── test/                               # 앱별 테스트 — 의미군 분리 (implementation-test §4.2)
    ├── unit/                           #   순수 단위: 도메인·응용 (mock/stub)
    ├── integration/                    #   DB·리포지토리·API 어댑터 (실제 DB) — HTTP 엔드포인트 테스트는 여기
    ├── e2e/                            #   엔드투엔드 흐름                               [선택]
    └── factories/                      #   factory_boy 팩토리 (ORM 영속 픽스처)            [선택]
```

의존 방향(단방향): `presentation_layer → application_layer → (domain_layer + infra_layer)`, `domain_layer`는 아무것도 의존하지 않는다.

설계 선택:
- **조직 1차 축 = 개념(애그리거트/feature), 2차 = 종류**: 각 계층을 개념 단위로 먼저 묶고(`domain_layer/<aggregate>/`, `application_layer/<feature>/`) 그 안에서 종류(`entity`/`value_object`/`command`/`query`…)로 나눈다. **종류 2차 폴더는 항상 생성한다**(§0 불변식) — 내용이 없으면 빈 패키지로 두되 평면 파일로 접지 않는다(이 항상-생성은 domain·application 종류 폴더에 더해 `presentation_layer`의 `api/`·`schema/`도 포함한다 — 표현이 없어도 빈 패키지로 항상, §0-4 개정). **§6.8 YAGNI는 골격에 적용하지 않는다**(YAGNI = 아직 없는 새 애그리거트/feature를 미리 만들지 마라; 컨테이너·계층·종류 폴더 골격은 항상 실현). 종류 폴더에 여러 개념 파일이 구분 없이 누적되는 것을 막는 규칙이다(houserules §3 평면 금지의 2차 레벨). `infra_layer`는 기술 어댑터라 1차를 기술 묶음으로 두고, 누적 시 애그리거트별 하위 그룹핑.
- **도메인 계층은 DDD 전술 패턴으로 완전 구성**(§3·§6.1): 코어는 애그리거트 루트·`entity`·`value_object`·`repository`(인터페이스), 나머지(`domain_service`/`event`/`specification`)는 폴더를 항상 두되 트리거 미충족 시 비어 있을 수 있다(`[선택]`=비어 있을 수 있음, 생략 아님 §0).
- **리포지토리 DIP**: 인터페이스(ABC)는 `domain_layer/<aggregate>/repository/`, 구현은 `infra_layer/repository/`. 추상화·구현 명명은 §4 명명 규약(추상=개념 bare명 `OrderRepository`, 구현=`Django…` 한정자 접두).
- **ORM 모델 ≠ 도메인 엔티티**: 도메인은 `domain_layer/<aggregate>/`, Django 모델은 `infra_layer/django_<app>/models/`로 분리한다(Data Mapper, §6.2 — ORM이 도메인을 import, 도메인은 ORM을 모름). 이름으로도 구분하며(`Order` vs `OrderModel`) 명명 상세는 §4. 변환은 `infra_layer/repository/`(ORM↔도메인 Data Mapper)와 표현 `schema_out`(도메인→응답 DTO)이 담당한다.
- **응용 계층은 도메인에 위임하는 파사드**(§3.6): 비즈니스 로직을 직접 구현하지 않고 도메인에 위임한다. 유스케이스는 연산 객체(쓰기 `…Command`·읽기 `…Query`)로 표현하고 입력은 **`…Request` DTO**로 받아 `execute(request)`로 실행한다. command/query 연산은 구체 리포지토리를 직접 생성하지 말고 **domain repository/port 인터페이스에 의존**하고 구현을 주입받는다(DIP).
- **읽기는 `…Query` 연산으로 통일하되, *별도 읽기 모델*(CQRS)은 선택적**(§5.4 [의사결정#2]): 모든 읽기는 `…Query` 인터랙터(통일성·런간 결정성)지만, 읽기 전용 *모델/프로젝션* 분리는 강제하지 않는다 — 공유 모델을 repository로 읽으면 충분하고, 읽기/쓰기 모델이 실제로 갈릴 때만 분리한다. (trivial 단건 조회도 `…Query`인 보일러플레이트 비용은 통일성·결정성을 위해 수용한다 — 실익은 버그 예방이 아니라 일관성이다.)
- **infra_layer 분할**: `django_<app>/`(영속성) + `repository/`(자기 애그리거트 접근·구현) + `acl/`(외부 컨텍스트 ACL 어댑터, [선택] 폴더 항상·코드는 통합 시) + `adapter/`(외부 I/O 서비스 어댑터). 구체 매핑·QuerySet/Manager·`transaction.atomic()`은 `implementation-django` §16 소유.
- **컨텍스트 간 통신 = OHS 우선, 직접 통합은 ACL로 분리**: 다른 바운디드 컨텍스트는 그 앱의 `published_service/`(OHS)로 소비하는 게 기본이다(아래 "컨텍스트 간 통신"). OHS가 없거나(미이주) 단일 트랜잭션·행 잠금이 불가피하면 ACL로 명시 — 도메인은 협력 포트(`domain_layer/<aggregate>/port/`)로 의존하고 구현(업스트림 모델·예외 번역)은 `infra_layer/acl/`에 가둔다. **ACL은 리포지토리가 아니므로 `repository/`에 섞지 않는다**(architecture-ddd 컨텍스트 맵 ACL 패턴 — 업스트림 모델을 하류 모델로 번역).
- **통합 스타일 선택(동기 ACL/OHS vs 비동기 이벤트)**: BC 간 통합에서 **즉시 일관성**이 필요하면(예: 재고 차감 — 오버셀 차단) 동기로 OHS/ACL을, **결과적 일관성**으로 충분하면(예: 주문 후 포인트 적립·알림) 비동기로 **도메인 이벤트**를 쓴다. 도메인 이벤트는 *애그리거트 간* 결과적 일관성에도 쓰여 ACL보다 범위가 넓다(ACL은 BC 간 동기 번역 전용). **선택 기준은 `architecture-ddd` 규칙4(일관성 경계 밖=결과적 일관성)·§6.8 패턴 선택 절차에 위임**한다 — 이 표준은 *어디 두는지*만 정하고 *언제 무엇*의 패턴 선택 이론은 코퍼스가 권위다.
- **표준 신규 Django 앱 성립 (infra_layer 안)**: 확립된 기존 규약이 없어 이 표준을 적용할 때 `apps.py`의 `AppConfig.name`을 전체 점경로(`application.<app>.infra_layer.django_<app>`)로, `label='<app>'`로 두고 설정의 `INSTALLED_APPS`에 그 점경로를 등록한다. **앱 루트(`application/<app>/`)나 도메인 패키지에 `models.py`를 두지 않는다.** dddjango는 `startapp`으로 `migrations/__init__.py`를 만들지 않는다. G0 전에 외부 소유자가 만든 migration 경로가 이미 있으면 그대로 보존할 뿐이다.
- **도메인 이벤트 흐름**: 발생(raise)은 `domain_layer` 애그리거트, 디스패치 타이밍은 UoW(§3.7 [의사결정#7]), 발행은 기본 **`transaction.on_commit()`**(§6.3), 외부 부수효과 유실이 치명적인 Risky Write만 **outbox**. 발행/전달 구체는 `implementation-django` §16.5·`architecture-db` §9.7 소유라 별도 `event_publisher/` 디렉터리를 두지 않는다.
- **표현 계층은 얇은 입력 어댑터**(§6.1 interface, §3.6): api는 요청 파싱 → 응용 호출 → 응답·예외 변환만 하고 비즈니스 로직을 두지 않는다. **응답은 `schema_out`(DTO)로 노출하고 도메인 엔티티를 직접 직렬화하지 않는다**(Published Language 경계). HTTP 계약·status·Ninja `Router`/`Schema`/auth 구체는 `architecture-api`·`implementation-django-ninja` 소유.
- **테스트는 의미군으로**(implementation-test §4.2): 앱별 `<app>/test/{unit,integration,e2e}/`. 도메인·응용 단위 테스트는 `unit/`, DB·리포지토리·HTTP 엔드포인트 테스트는 `integration/`. 엔드포인트별 평면 나열(`test/api/...`)은 두지 않는다.

### 컨텍스트 간 통신 — OHS (제공 컨텍스트 소유)

서로 다른 컨텍스트(앱) 간 통신은 **각 앱이 자기 공개 진입점(OHS, 오픈 호스트 서비스)을 소유**한다(§2.5/§6.7). 다른 컨텍스트는 이 `published_service/`만 import하고, 대상 앱의 `domain_layer`/`application_layer`/`infra_layer`는 **직접 import하지 않는다**. **DB FK도 cross-context 결합이다 — 타 BC 모델을 ORM `ForeignKey`/`OneToOneField`/`ManyToManyField`로 참조하지 않는다(BC 경계 ORM FK 금지). 타 BC는 ID 값으로 참조하고 존재 검증은 OHS/ACL 포트로 하며, 같은 BC 내 FK는 허용한다(`architecture-ddd` §3.3 규칙3 영속성 확장).**

```
application/<app>/published_service/     # 이 앱이 외부 컨텍스트에 노출하는 OHS
└── <service>_service/                   # 서비스(개념) 1차 — 무조건 폴더 (예: sms_service/)
    ├── <service>_service.py             # 행위 — 공개 모듈 함수만 (application_layer command/query에 위임)
    └── contract/                        # 계약 — 소비자가 타입으로 결합하는 전부 (3패키지 고정 — folder-from-birth)
        ├── request_contract/            # 입력 DTO — 공개 함수(연산)당 1파일 (+공유 값 타입 bare명 모듈)
        │   └── <operation>_request_contract.py
        ├── response_contract/           # 결과 DTO — 반환 있는 연산당 1파일 (+공유 값 타입 bare명 모듈)
        │   └── <operation>_response_contract.py
        └── exception_contract/          # published 예외 — 서비스 스코프 (도메인 예외 번역 타깃)
            ├── <service>_published_error.py   # published base — 예외 노출 서비스는 필수
            └── <published_exception>.py       # 구체 예외 — 예외 클래스당 1모듈
```

OHS를 한 폴더(중앙 `bridge/`)에 모으지 않는다 — 한 컨텍스트의 공개 계약이 밖에 흩어지면 응집이 깨지고, 허브가 모든 컨텍스트를 아는 결합점으로 비대해진다(§2.5 "진흙공" 방어). OHS 반환도 도메인 엔티티 대신 **Published Language(DTO)**로 한다 — 반환 계약은 아래 OHS 시그니처 계약(3연조)이 규정한다(presentation `schema_out`과 동일한 모델 누수 방어).

**OHS 내부 구조 — 서비스(개념) 1차·계약 3패키지 (2026-07-08 개정: 계약 3파일→3패키지 folder-from-birth·비대화-시 승격 조문 폐지; 2026-07-07 개정: 구 `read.py`/`write.py` 종류 1차 폐지).** `published_service/` 바로 아래에는 서비스 폴더(`<service>_service/`)만 온다 — 평면 `.py` 모듈을 두지 않는다(`__init__.py`와 아래 이주 조문의 deprecation 호환 심은 예외). 각 서비스는 행위 모듈(`<service>_service.py`)과 계약 패키지(`contract/`)로 구성하고, contract 안은 `request_contract/`·`response_contract/`·`exception_contract/` **3패키지**로 고정한다 — 작은 서비스라도 파일로 접지 않는다(folder-from-birth: 확장-시점 승격은 판단형 규칙이라 표류하고 — 3연조가 계약 객체에 쓴 birth-enum 동형 논리를 계약 컨테이너 자신에 적용 — published 표면의 파일→패키지 승격은 재노출 금지 하에서 소비자 import를 깨는 파괴적 변경이라 신생 표면에서 승격 이벤트 자체를 제거한다; 기존 3파일형의 잔존 승격은 아래 이주 조문 ⒝ 심이 비파괴화한다). 이 3패키지 고정은 §0 골격 불변식(폴더·`__init__.py` 규율)의 연장이 아니라 **OHS 고유 규칙**이다(형태·평면 나열 방지 논리가 §0와 겹치더라도 귀속과 집행 경로는 이 절과 discipline-reviewer OHS 불릿이다 — §0 목록에 추가하지 않는다) — 계약 표면을 결정적 형태로 고정해 presence 점검과 소비자의 예측 가능한 import를 성립시키고, 빈 `exception_contract/`는 "선언된 예외만 던진다"(아래 3연조)와 결합해 도메인 예외 무번역 전파를 형태로 막는다. **내부 파일 규율**: `request_contract/`는 공개 함수(연산)당 `<operation>_request_contract.py` 1파일(`<operation>`은 그 공개 함수명 — 0-인자 Query 위임 연산은 파일 없음), `response_contract/`는 반환 있는 연산당 `<operation>_response_contract.py` 1파일(`None` 반환 연산은 파일 없음) — 3연조 ①②의 함수↔계약 대응이 파일 축까지 이어져 연산의 추가·변경·폐지가 파일 단위로 격리된다. 여러 연산이 공유하는 계약 값 타입은 같은 kind 패키지 안 공유 모듈에 두고 연산 파일이 import한다(파일명은 §4 일반 규칙 — 주 클래스명 snake_case — 이고 `_contract` 접미를 쓰지 않는다: 접미는 연산 파일 전용 표지다; request·response 양쪽 필드에 쓰이는 타입은 response_contract가 소유하고 request 연산 파일이 import한다 — 아래 단방향과 정합). 여러 연산이 같은 response를 반환하면 각 연산 파일은 공유 모듈 타입의 명시적 별칭 1줄(`GetOrderResponseV1 = OrderReceiptV1` 류)로 존재시키고 재선언(복제)하지 않는다 — 별칭은 연산 축의 안정 경로 제공(공유 타입이 나중에 연산별로 분화해도 소비자 경로 불변)이지 `__init__` 재노출 큐레이션이 아니다. `exception_contract/`는 연산 축이 아니라 서비스 스코프다 — published base는 `<service>_published_error.py`(published 예외를 노출하는 서비스는 필수; 파일명은 §4 파일명 규칙의 기계적 귀결), 그 외 published 예외는 중간층 base 포함 예외 클래스당 1모듈(§4 파일명 규칙)로 둔다. 서비스 폴더를 만들 때 3패키지를 함께 생성하며 내용 없는 kind는 빈 패키지로 둔다. 구 read/write 축은 위임 대상(application_layer의 command/query)이 이미 표현하므로 표면에서 중복하지 않는다. 서비스 폴더 자체는 개념이므로 실제 노출할 서비스가 있을 때만 만든다(§0-3 '개념 1차는 개념 식별 시'와 동형). `__init__.py`는 전부 빈 패키지로 유지하고 재노출 큐레이션을 하지 않는다(아래 이주 조문 ⒝형 호환 심만 한시 예외) — 공개 표면의 단일 출처는 각 모듈 자신이다(소비자는 `…published_service.<service>_service.<service>_service`의 함수와 `contract/` 하위 각 모듈 — 연산 계약 `…<kind>_contract.<operation>_<kind>_contract`, 공유 값 타입 모듈(필드 타입 결합용 — 연산의 반환 타입 결합은 그 연산 계약 모듈 경로를 쓴다: 위 별칭이 그 안정 경로다), published 예외 `…exception_contract.<service>_published_error` 등 — 을 모듈 경로로 직접 import). 비동기 통합(이벤트 구독·outbox)은 이 규약 밖이다 — 통합 스타일 선택(§2 설계 선택)대로 도메인 이벤트 채널로 라우팅한다.

**OHS 시그니처 계약(3연조).** `<service>_service.py`의 공개 표면은 모듈 수준 함수만이다(공개 클래스 금지 — 조립은 composition_root 위임이라 상태가 없다). 각 공개 함수는 ① 인자로 그 연산의 request contract **1개**만 받고(0개는 위임 대상이 입력 없는 Query 인터랙터일 때만 — 커맨드 위임은 항상 1개; 맨 스칼라·다중 인자 금지, 앞선 호출의 response contract가 후속 입력에 필요하면 request contract의 필드로 품는다) ② response contract(또는 `None`)만 반환하며 ③ exception_contract에 선언된 예외만 던진다(transient 인프라 예외·프로그래밍 오류의 raw 전파는 예외 — 아래 번역 조문). 단일-요청-객체 형태는 인터랙터 `execute(request)` 규약(§2 설계 선택·§3 표)의 OHS 판이다 — published 경계는 진화 압력이 가장 큰 표면이라 필드 추가로 흡수 가능한 계약 객체를 1개째부터 강제한다(확장-시점 승격은 판단형 규칙이라 표류 — birth-enum과 동형 논리). 함수 본문은 composition_root 팩토리를 호출해 application_layer 인터랙터에 위임하고 계약↔응용 DTO 변환(경계 언랩)만 한다 — 판정·비즈니스 로직·ORM 직접 질의 금지. **published 계약 타입을 application_layer 안으로 관통시키지 않는다**(응용 계층은 domain에만 의존 — §3 표 응용 계층 헤더·`architecture-ddd` §6.1). OHS가 필드 단위로 언랩·재조립하며, 응용의 반환 DTO는 `<feature>/dto/<usecase>_result.py`에 둔다(§3 표 dto/ 항목 참조). 데이터소스 BC가 OHS를 노출하면 그 연산은 이 BC가 소유하는 조회 유스케이스가 된 것이다 — 그 시점에 Query 인터랙터와 composition_root를 만든다(§0-3 '개념 1차는 개념 식별 시'·조립 규칙 'application 로직 가진 BC는 반드시'의 적용이지 면제 신설이 아니다). 공개 함수 docstring은 그 함수가 던질 수 있는 exception_contract 예외 전수 목록의 앵커다(`discipline-cleancode` §4.2 공개 API 독스트링 필수의 OHS 적용 — ACL 협력 포트 앵커(아래 소비 측)와 대칭).

**제공 측 예외 번역 — exception_contract가 단일 출처.** OHS 함수는 도메인·응용 예외를 exception_contract에 선언된 published 예외로 번역해 던진다 — 도메인 예외의 raw 전파·재노출(`__all__` 포함) 금지. 재노출하면 소비 BC가 우리 `domain_layer` 타입 정체성에 결합해 §2.5 published language 경계가 무력화된다(소비 측 ACL 조문의 "동일 의미면 명시적 재노출"은 소비 측 ACL이 *업스트림 예외*를 포트 선언에 명시하고 그대로 통과시키는 허용이지, 제공 측이 자기 도메인 타입을 공개 계약에 올리는 면허가 아니다). exception_contract의 모든 예외는 서비스당 1개의 published base 예외를 상속한다(base 자신 제외·중간층 경유 전이 상속 허용 — `implementation-python` §15.2 최상위 예외, 소비자의 가족 단위 catch). 번역은 알려진 구체 예외의 전수 명시 매핑으로 하고, 폴백을 둘 경우 도메인·응용 예외 base 단위 catch에 한정하며(`except Exception` 광범위 포괄 금지 — 프로그래밍 오류는 published로 위장하지 않고 raw 전파가 정상) 폴백 published 타입은 retryable 의미로 위장하지 않는 중립 타입으로 정한다(`implementation-django-ninja` §6.2 동방향). **transient 짝 조항**: transient 인프라 예외(`OperationalError` 등 재시도성 변종)는 published 예외로 감싸지 않는다 — raw 통과시켜 소비 측 경계의 단일 변환점(recognizer)이 처리하게 한다(위 소비 측 ACL의 transient 위장 금지와 동형; published로 감싸면 실 메시지·`__cause__` recognizer 사각 → 영구장애 오분류·500 누수). 재시도 소진을 스스로 판정한 경우의 규율(도메인 transient-마커 타입·`raise … from` 보존)은 소비 측 조문을 따른다.

**contract 무의존 — import 방향.** contract 모듈은 domain·application·infra 어느 계층도 import하지 않는다(표준 라이브러리·같은 서비스 contract만) — 소비 BC의 계약 import가 무거운 그래프(Django 앱 로딩)를 끌고 오지 않게 하는 격리이고, 도메인 enum을 계약 필드 타입으로 노출하면 소비 BC가 우리 내부 enum에 결합한다(`architecture-ddd` §2.5 — BC 간 연결은 계약 타입 또는 wire value). **birth-enum 짝**: 우리 BC가 발행하는 이벤트 봉투를 OHS 계약으로도 노출할 때의 discriminator 자리는 이 격리가 우선한다 — domain enum 파생(`Literal[EventType.X]`) 대신 wire `Literal["…"]`을 유지하고 union-enum 동기 테스트(`implementation-test` §15.5)로 드리프트를 방어한다(`discipline-cleancode` §2.14 허용 목록 짝 조항의 명시 예외 — cleancode 쪽 카브아웃과 세트). contract 내부는 패키지 granularity로 `request_contract/* → response_contract/*` 단방향만 허용하고(영수증류 response를 후속 request가 필드로 품는 경우), 같은 kind 안에서는 연산 파일→공유 모듈 방향만 허용한다(연산 파일 간 직접 import 금지 — 공유가 생기면 공유 모듈로 내린다). `exception_contract/*`는 다른 kind 패키지의 모듈을 import하지 않고(자기 패키지 안 base 모듈 — published base·중간층 base — import는 상속 배선이라 허용) 계약 타입을 예외 필드에 싣지 않는다 — 멱등 재생이 기존 결과를 알려야 하면 예외에 결과 객체를 싣지 말고 response contract의 재생 표기(`replayed` 류)로 반환한다. 같은 격리 이유로 `<service>_service.py`의 composition_root import는 함수 내부 지연 import를 허용한다(사유 주석 1줄).

**이주 — 구 read/write·평면 OHS·구 3파일형 contract.** 구 구조는 '확립된 규약'으로서 신 규약 적용을 영구 면제하지 않는다: **새 서비스·새 공개 함수는 신 구조로만 추가한다**(구 `read.py`/`write.py`·구 3파일형 계약 모듈(2026-07-07형 `request_contract.py` 등)에 표면을 늘리지 않는다). 기존 함수의 국소 수정은 미이주로 허용한다 — OHS 이주는 타 BC 소비자의 import 경로를 깨는 파괴적 변경이므로 전면 이주는 별도 스코프(G1 트레이드오프)로 올린다. 3파일형 서비스에 새 연산을 추가할 때는 같은 이름의 모듈과 패키지가 공존할 수 없으므로 **그 kind만 패키지로 승격**하고 ⒝ 심으로 구 import 경로를 한시 유지한다(부분 이주 — 전면 이주 G1과 구분). kind를 승격하면 그 kind 안의 *기존* 계약 클래스도 연산당 1파일·공유 모듈로 재배치한다(소비자 경로는 ⒝ 심이 보존하므로 비파괴) — '기존 함수 국소 수정 미이주 허용'은 미승격 kind·구형 모듈에 한정한다. 이주 호환 심은 2형이다(재노출 금지 조문의 한시 예외 2형): ⒜ 구 read/write 평면 모듈이 신 구조를 재노출 ⒝ 3파일형→3패키지형 전환 시 `<kind>_contract/__init__.py`가 연산·공유 모듈을 재노출 — 둘 다 deprecation 주석을 명기하고 소비자 갱신과 함께 제거한다.

**소비 측(다른 컨텍스트를 부를 때)**: 기본은 대상 앱의 `published_service/`(OHS)만 import한다. 대상 컨텍스트가 아직 OHS를 노출하지 않거나(미이주) 단일 트랜잭션·행 잠금이 필요해 직접 접근이 불가피하면, 그 통합을 **ACL(부패 방지 계층)로 명시**한다 — 도메인은 협력 포트(`domain_layer/<aggregate>/port/`)로만 의존하고, 구현(업스트림 모델·예외 번역)은 `infra_layer/acl/`에 가둔다. **ACL은 리포지토리가 아니므로 `repository/`에 섞지 않는다.** **업스트림의 모델·예외 번역은 ACL 안에 격리한다 — presentation·application이 타 BC의 예외(`domain_layer`/`application_layer` 하위)를 직접 `import`해 잡으면 컨텍스트 결합이 ACL 밖으로 새므로, ACL이 협력 포트가 던지는 우리 쪽 예외로 번역(동일 의미면 명시적 재노출)해 넘긴다. 이 번역은 *전수*다 — ACL이 구동하는 업스트림 동작이 그 포트 경로에서 던질 수 있는 예외를 (`domain_layer`·`application_layer` 층 무관) 빠짐없이 잡아 협력 포트가 선언한 우리 쪽 예외로 번역한다. catch되지 않은 업스트림 예외가 ACL을 그대로 통과해 우리 쪽 application·presentation으로 raw 전파되면 포트 계약 위반이다. 협력 포트(`domain_layer/<aggregate>/port/`)의 ABC·docstring이 *이 통합이 노출하는 우리 쪽 예외 전수 목록*의 단일 출처(앵커)이며 ACL은 그 목록을 채운다 — 업스트림에 새 예외가 생기면 포트 선언과 ACL 번역을 함께 갱신한다. 단 '전수'는 *알려진 구체 예외 집합을 빠짐없이 덮으라*는 것이지 `except Exception` 광범위 포괄 catch가 아니다 — 각 구체 예외를 명시 번역한다(`discipline-cleancode` 구체적 예외 처리). **또한 transient 인프라 예외(`OperationalError` 중 DB 락·deadlock·serialization failure 같은 재시도성 변종)는 협력 포트가 선언하는 우리 쪽 *도메인* 예외 집합이 아니다 — ACL은 이를 도메인 예외로 위장 번역하지 않고(포트에 인프라 누수 금지), presentation 경계의 단일 변환점이 retryable(503/409) problem으로 매핑한다(`implementation-django-ninja` §6.2). 단 이 '위장 번역 금지'는 드라이버가 *실제로 던진* transient(`OperationalError`)에 한정한다 — ACL·앱이 낙관락·CAS 재시도 루프를 *스스로 소진 판정*한 경우(드라이버 예외 부재)는 인프라 예외를 *합성*해 신호하지 말고(합성 예외는 실 메시지·`__cause__`가 없어 presentation recognizer 사각→영구장애 오분류·500 누수=과소매핑), 협력 포트가 선언한 도메인 transient-마커 예외 *타입*(`StockContention` 등 retryable 의미)으로 raise해 핸들러가 *타입*으로 매핑하게 한다. 실 드라이버 락 예외를 잡아 재시도하다 소진했다면 원본을 `raise … from driver_exc`로 보존하면 recognizer가 `__cause__`로 인식한다(결정적 백스톱 `check-synthetic-infra-exc`가 `infra_layer`의 `from` 없는 인프라 예외 합성을 차단).**** 대상이 OHS를 노출하면 ACL 구현을 OHS 호출로 교체하고 포트는 유지한다(이 표준의 통합 진화 지침 — architecture-ddd 컨텍스트 맵의 ACL·OHS 패턴을 토대로 한 합성이며, 코퍼스가 "ACL→OHS 진화"를 명시하는 것은 아니다).

(신규 앱별 변종: WebSocket 앱은 `<app>_asgi_router.py`·`presentation_layer/socket/`을 더 가진다. 이 표준으로 새로 만드는 단순 지원 앱도 컨테이너·4계층 폴더를 유지한다. 기존 persistence 앱에는 소급 적용하지 않는다.)

---

## §3 폴더별 레퍼런스 (존재 이유 · 위치 파일)

`(코어)`는 항상 두고, `[선택]`(코드 골격)은 폴더를 항상 생성하되 트리거 조건 미충족 시 비어 있을 수 있다(생략 아님 — §0 불변식). 단 **테스트 의미군**(`e2e/` 등)은 `implementation-test` §4.2 소관이라 거기선 `e2e`가 진짜 선택이다(코드 골격 불변식과 별개). **`[통합 시]` 폴더**(`domain_layer/<aggregate>/port/`·`infra_layer/acl/`)도 2026-06-08 개정으로 **`[선택]`과 동일하게 폴더를 항상 빈 패키지로 생성한다** — 이전엔 '소비할 때만 생성·없으면 폴더 미생성'이었으나, 모든 BC가 동일 트리 골격을 갖도록 *폴더는 무조건 두고 ACL 어댑터·협력 포트 코드는 다른 컨텍스트를 실제 소비할 때만 채운다*(폴더=골격 불변식, 코드=통합 트리거).

**최상위 · 공용**

| 폴더 | 존재 이유 | 위치 파일 · 명명 |
|---|---|---|
| `<project>/` | 프로젝트 설정 패키지(앱 아님) | `settings/{env,dev,local,prod,test}.py`, `urls.py`·`asgi.py`·`wsgi.py`·`celery.py`(비동기 큐 쓸 때) |
| `<project>/views/` | 어느 앱에도 속하지 않는 루트/관리 뷰(헬스체크·랜딩) | 루트 뷰 모듈 |
| `<project>/{static,templates}/` | 프로젝트 레벨 정적·서버렌더 자원 | 정적 파일·템플릿 |
| `application/` | 새 feature 앱·domain/application 코드의 컨테이너 | 앱 디렉터리 `<app>/` |
| `common/enum/` | 공유 커널로 승격된 enum(승격 기준: 같은 지식 + 같은 변경 사유 근거 — §1; BC 내부 enum은 그 BC `domain_layer` 소유) | `<domain>_enum.py` |
| `common/django/` | **Django 의존** 공용 유틸 | `task.py`·`timezone.py`·`model_util.py` |
| `common/ninja/` | **Django Ninja 의존** 공용 확장 | `authentication.py`·`custom_type.py`·`response/` |
| `common/<project>/` | **프레임워크 비종속** 공용 = shared kernel(공유 값객체·커스텀 타입) | 공유 VO·타입. ※Django/Ninja 의존 시 위 두 폴더로 |

> 위 `common/*`은 모두 *프로젝트 루트* `common/`(= `application/`의 형제) 아래다 — `application/common/`이 아니다. **그리고 횡단 배치는 *2개 이상 BC가 실제로 공유할 때*만 한다**: 단일 BC 전용 헬퍼(problem 등)는 그 BC `application/<app>/presentation_layer/`에 두고, 공유가 생긴 뒤 루트 `common/`으로 승격한다(YAGNI; `implementation-django-ninja` §6.2). enum은 추가로 공유 커널 기준을 통과해야 한다(같은 지식 + 같은 변경 사유 근거 — §1) — 같은 wire 값을 BC마다 각자 선언하는 것은 정상(published language 수용)이지 승격 사유가 아니다.

**도메인 계층 `domain_layer/<aggregate>/` — 애그리거트(개념) 1차, 종류 2차 (§3 전술 패턴)**

| 위치 | 존재 이유 | 위치 파일 · 명명 | 코어/[선택] |
|---|---|---|---|
| `<aggregate>/` | 애그리거트 = 응집·조직 단위(예: `member/`·`order/`) | (아래 종류들을 담음) | 코어 |
| `<aggregate>/<aggregate>.py` | 애그리거트 루트 — 불변식·일관성 경계, 외부는 루트로만 접근(§3.3) | `member.py` | 코어 |
| `<aggregate>/entity/` | 식별자를 갖는 종속 엔티티(§3.2) | `<entity>.py` | 코어(폴더 항상 생성) |
| `<aggregate>/value_object/` | 불변 값 객체, 자기검증(§3.1) | `<value_object>.py` | 코어(폴더 항상 생성) |
| `<aggregate>/repository/` | 리포지토리 **인터페이스(ABC)** — DIP 포트(§3.4), 구현은 infra | `<aggregate>_repository.py` → `class OrderRepository`(bare 개념명) | 코어 |
| `<aggregate>/port/` | 외부 컨텍스트 **협력 포트(ABC)** — 다른 컨텍스트를 소비할 때 도메인이 의존하는 역할 포트(**호출자가 application 유스케이스(command)여도 소유·위치는 도메인이다** — 'use-case dependency'로 재분류해 `application_layer`에 두지 않는다; command가 domain-owned port에 의존하는 것이 DIP) | 일반: `<collaborator>_port.py` → `class ProductLockPort` · 외부서비스(Gateway 패턴): `payment_gateway.py` → `class PaymentGateway` | [선택] 폴더 항상·코드는 소비할 때만 |
| `<aggregate>/domain_service/` | 그 애그리거트 중심의 stateless 도메인 로직(§3.5) | `<name>_service.py` → `class PricingService` | [선택]; 여러 애그리거트에 걸치면 `domain_layer/` 공용 위치로 |
| `<aggregate>/event/` | 도메인 이벤트 **정의**(§3.7) | `<event>_event.py` → `class OrderPlacedEvent`(과거형) | [선택] 결과적 일관성·외부 통지 필요 시 |
| `<aggregate>/specification/` | 재사용 가능한 규칙/조회 명세(§3.8) | `<name>_specification.py` → `class OrderActiveSpecification`(풀네임) | [선택] 복합 규칙을 조합·재사용할 때 |
| `<aggregate>/exception.py` | 도메인 예외 | 단일 파일(커지면 `exception/` 패키지) | 코어 |

**응용 계층 `application_layer/` — 유스케이스 파사드, domain에만 의존 (§3.6)**

> **어휘(인터랙터 채택)** — 이 표준의 *생성 코드*는 유스케이스를 연산 객체로 표현한다: 입력 `…Request`, 쓰기 `…Command`, 읽기 `…Query`, 모두 `execute(request)`. ⚠️ 코퍼스는 `…Command`/`…Query`를 **다른 의미로 쓰며 이는 이론/모델링 어휘라 보존**한다: `architecture-ddd §3.6`의 `…Command`=응용 서비스 *입력 DTO*, Event Storming 색상표의 `Command`=*의도적 행동*, CQRS/ES 패키지 구조의 domain `commands.py`=*도메인 커맨드 정의*, 애그리거트의 *커맨드 메서드*, `services.py`=*유스케이스 파사드*. 경계: **생성 코드 어휘 권위는 이 문서**(§6.1 위임)이고, 도메인·Event Storming *모델링* 어휘는 코퍼스가 권위다. 이 표준 `service/`는 여러 유스케이스 *오케스트레이션*(코퍼스 `services.py`=단일 유스케이스 파사드와 구분)이고, HackSoft `selectors.py`/`services.py`(`implementation-django §16`)의 평면 함수 관용은 이 표준이 `application_layer/{command,query}` 인터랙터로 구체화한다.

| 폴더 | 존재 이유 | 위치 파일 · 명명 | 코어/[선택] 트리거 |
|---|---|---|---|
| `<feature>/command/` | 쓰기 유스케이스 **연산** — 도메인에 위임, domain `repository/`·`port/` 인터페이스 의존(DIP) | `<usecase>_command.py` → `class PlaceOrderCommand`(`execute(request)`) | 코어 |
| `<feature>/query/` | 조회 유스케이스 **연산** — repository 의존 | `<usecase>_query.py` → `class ListOrdersQuery`(`execute(request)`) | 코어 (별도 읽기모델 CQRS는 §5.4 선택) |
| `<feature>/dto/` | 유스케이스 **입력·반환** 데이터 계약(DTO) | 입력 `<usecase>_request.py` → `@dataclass class PlaceOrderRequest` · 반환 `<usecase>_result.py` → `@dataclass class …Result` — **소비처 불문**(HTTP-소비든 OHS 등 presentation 밖 소비든) 유스케이스 반환 DTO는 여기 둔다(§2 OHS 시그니처 계약이 이 슬롯을 참조). ※HTTP 응답 노출은 여전히 presentation `schema_out` 경유(도메인·DTO 직접 직렬화 금지). **연산 모듈(`command/`·`query/`)에 공개 dataclass를 인라인 정의하지 않는다 — 연산 모듈의 공개 표면은 연산 클래스뿐이다**(`_` 사설 dataclass의 내부 스테이징(비반환·비수출) 인라인은 정당 — `execute`가 반환하면 공개 계약이라 동일 위반; 결정적 백스톱 `check-usecase-dto-placement`가 인라인 직접형을 집행) | 코어 |
| `<feature>/handler/` | 도메인 이벤트/커맨드 핸들러(§6.1) | `<event>_handler.py` → `class OrderPlacedHandler` | domain `event/` 도입 시 |
| `<feature>/service/` | 다중 유스케이스 오케스트레이션 | `<flow>_service.py` → `class CheckoutService` | 여러 command/query를 한 흐름으로 묶을 때 |
| `unit_of_work.py` | UoW **인터페이스** — 트랜잭션 경계(§6.3) | 앱당 1개 | 구현은 `transaction.atomic()`(django §16.4)으로 충분; 커스텀 UoW 필요할 때만 |

**인프라 계층 `infra_layer/` — ORM·외부 I/O (Django 구체는 `implementation-django` §16 소유)**

| 폴더 | 존재 이유 | 위치 파일 · 명명 |
|---|---|---|
| `django_<app>/models/` | Django ORM 모델(**도메인 엔티티와 별개**; 클래스명 `<Name>Model`) | `<entity>_model.py` (예: `order_model.py` → `class OrderModel`) |
| `django_<app>/migrations/` | DB migration lifecycle — dddjango 비소유 | G0 전에 framework/external owner가 만든 경우만 보존; 생성·수정·삭제·이동 금지 |
| `django_<app>/admin/` | Django admin 등록·커스텀 | `<entity>_admin.py`(+`templates/` admin 전용) |
| `django_<app>/apps.py` | AppConfig — `name='application.<app>.infra_layer.django_<app>'`, `label='<app>'` (이 점경로를 INSTALLED_APPS에 등록; 앱 루트에 `models.py` 금지) | `apps.py` |
| `repository/` | domain `repository/` ABC **구현** + ORM↔도메인 변환(Data Mapper §6.2). **자기 애그리거트 전용** | `<aggregate>_repository.py` → `class DjangoOrderRepository`(구현=기술 한정자 접두) |
| `acl/` | 외부 컨텍스트 **ACL 어댑터** — domain `port/` ABC 구현, 업스트림 모델·예외를 우리 모델로 번역(*전수* — 포트 경로의 모든 업스트림 예외를 포트-선언 예외로 빠짐없이). 리포지토리와 분리([선택] 폴더 항상·코드는 통합 시) | `product_lock_adapter.py` → `class DjangoProductLockAdapter`(일반 포트 구현=`Adapter`) |
| `adapter/` | **외부 서비스** 어댑터(인증·푸시·결제 등) | Gateway 패턴이면 `stripe_payment_gateway.py` → `class StripePaymentGateway`, 일반이면 `<external>_adapter.py` → `class …Adapter` ※`domain_service`·app `service/`와 구분(외부 I/O 전용) |

**표현 계층 `presentation_layer/` · 컨텍스트 통신 · 테스트**

| 폴더 | 존재 이유 | 위치 파일 · 명명 |
|---|---|---|
| `api/<feature>/` | HTTP **입력 어댑터**(얇게, §6.1 interface) | `<aggregate>_controller.py` → `class OrderController`(`@api_controller`); 함수형 레거시는 `api_<resource>.py` (Ninja Router 또는 `@api_controller` 클래스) |
| `schema/` | 입출력 계약 DTO(Ninja Schema) | `schema_in.py`·`schema_out.py`·`error_out.py`(feature가 많으면 `<feature>/`로 분할) — **응답은 `schema_out`**, 도메인 직접 노출 금지 |
| `<app>/published_service/` | 컨텍스트 간 **OHS**(다른 앱에 노출, §2.5/§6.7) | `<service>_service/`(서비스 1차) → `<service>_service.py`(공개 함수)·`contract/{request,response,exception}_contract/`(3패키지 — request/response는 연산당 1파일 `<operation>_<kind>_contract.py`, exception은 base `<service>_published_error.py`+예외 클래스당 1모듈; §2 OHS 내부 구조). 다른 앱은 **이것만** import(모듈 경로 직접 — `__init__` 재노출 없음) |
| `<app>/test/` | 앱별 테스트 — **의미군 분리**(implementation-test §4.2) | `test/{unit,integration,e2e,factories}/`. 도메인·응용 단위=`unit/`, DB·리포지토리·HTTP 엔드포인트=`integration/`, factory_boy 팩토리=`factories/`. 엔드포인트별 평면 나열 금지 |
| 라우팅 | 앱 진입점 | `<app>_api_router.py` → config의 `NinjaExtraAPI`를 import해 `register_controllers`로 BC 로컬 등록(루트 `urls.py` 포함은 함수형 Router 경로) |
| 조립(배선) | DI 컴포지션 루트 — use-case·application 로직(command/query/service 등) 가진 BC는 **반드시 둔다**(데이터소스 BC=빈 `application_layer`는 생략) | `composition_root.py`를 **만들어** `build_<usecase>_command()`/`build_<usecase>_query()` 팩토리로 구체 infra를 use-case에 매요청 주입하고, presentation은 그 팩토리를 **매요청 호출만** 한다(operation·application service 본문에서 `Django…Repository()`/`…Adapter()` 직접 생성 금지=Q-7의 짝). 결정적 백스톱 `check-composition-root`이 정본 부재·off-tree·오배치를 집행 |

**신규 앱별 변종**: WebSocket 앱은 `presentation_layer/socket/` + `<app>_asgi_router.py`를 추가한다. 이 표준으로 새로 만드는 단순 지원 앱도 컨테이너·4계층 폴더를 유지한다. 기존 persistence 앱에는 소급 적용하지 않는다.

---

## §4 명명 규약

명명은 트리 전반(§1~§3)에 걸친 횡단 규약이라 여기 한곳에 모은다 — **이 절이 단일 출처**이고, §0 불변식·§2 설계 선택·§3 표는 위치/구조를 정하며 명명 세부는 이 절을 가리킨다.

**도메인 ↔ ORM** — 같은 개념의 두 표현을 이름으로 구분한다.
- 도메인 엔티티/애그리거트 = **bare 이름**(`Order`; `domain_layer/<aggregate>/`).
- Django ORM 모델 클래스 = **`<Name>Model`**(`OrderModel`; 파일 `<entity>_model.py`, `infra_layer/django_<app>/models/`).
- 왜: ORM ≠ 도메인(Data Mapper §6.2). 이름이 갈려야 호출부가 어느 표현을 다루는지 분명하다(§0 불변식 6). 변환은 `infra_layer/repository/`·표현 `schema_out`이 담당한다.

**테이블명(`db_table`)** — 신규 ORM 모델은 `Meta.db_table = "<app_label>_<entity_snake>"`를 명시한다. `<entity_snake>`는 클래스명 `<Name>Model`에서 **`Model` 접미를 떼고** snake_case로 바꾼 도메인 개념명이다(`ProductModel`→`catalog_product`, `ProductImageModel`→`catalog_product_image`).
- 왜: `Model` 접미는 *코드측* ORM↔도메인 구분 표식(위 항)이지 DB 개념이 아니다 — 테이블은 도메인 개념을 반영한다. Django 기본값 `<app_label>_<modelname>`(= `<app_label>_<name>model`)을 그대로 두면 `model` 군더더기가 테이블명에 새고(`catalog_productmodel`) 다단어는 언더스코어 없이 붙는다(`catalog_productimagemodel`). 명시로 둘 다 해소한다.
- `app_label` 접두는 **유지**한다(교차 앱 테이블 충돌 방지·DB 소유 식별). 앱명과 애그리거트명이 같아 `order_order`처럼 반복돼 보여도 줄이지 않는다(규칙의 결정성·백스톱).
- 면제: `abstract = True`·`proxy = True`(자체 테이블 없음)·`managed = False`(외부 소유 테이블 매핑)는 `db_table`을 두지 않는다.
- 적용 범위는 **신규 모델만**이다. 이미 생성·적용된 모델의 테이블명은 소급 변경하지 않는다. 기존 persistence 앱은 물리 이주하지 않으며 기존 테이블명을 보존한다.
- 집행(2층): 결정적 백스톱 `check-db-table.py`는 신규 추가 모델의 `db_table` **존재(작성)** 만 잡는다(값 형태 미검사 → 거짓 양성 ≈0 유지). **값 형태**(`<app_label>_<entity_snake>` 일치)는 discipline-reviewer가 현행 명세와 대조한다. migration 명령이나 DDL 검토를 이 확인에 사용하지 않는다.

**추상화(포트) ↔ 구현(어댑터)** — 추상화가 개념의 "진짜 이름"을 갖고, 구현 접미사는 그 포트가 *확립 패턴명*인지로 갈린다(헥사고날 정석 — DR-05/37 번복: 옛 규약은 모든 포트 구현에 `Port`를 보존했으나 이는 위치 표식을 구현에 남기는 오류였다).
- 추상화(리포지토리 인터페이스·기타 포트 ABC) = 도메인 개념 + **역할 접미사**(`OrderRepository`·`ProductLockPort`·`PaymentGateway`). `Repository`/`Port`/`Gateway`처럼 그 객체의 *역할*을 나타내는 접미사는 이름의 일부라 허용한다.
- 구현 접미사 = **ⓑ 기준**(확립 패턴명 예외)으로 정한다:
  - **확립 패턴명(PoEAA/GoF 등재명 — `Repository`·`Gateway`·`Mapper` 등)**: 추상·구현 **동일 접미사 유지**. 구현은 base 전체 이름에 기술·출처 한정자를 접두한다(`OrderRepository`→`DjangoOrderRepository`·`InMemoryOrderRepository`·`FakeOrderRepository`, `PaymentGateway`→`StripePaymentGateway`). 이들은 *패턴명*이라 구현에서도 떼지 않는다.
  - **일반 협력 포트(위 패턴명에 없는 헥사고날 포트 — 다른 BC 협력/ACL 등)**: 추상 `...Port` ↔ 구현 **`...Adapter`** 쌍. `Port`는 헥사고날 *위치 표식*이라 구현에 남기지 않는다(`ProductLockPort`의 구현은 `DjangoProductLockAdapter`이지 `Django`+`ProductLockPort`가 아니다 — 구현에서 `Port` 접미사를 떼고 `Adapter`로 바꾼다). base 개념명(`ProductLock`)은 공유해 쌍 추적을 유지한다.
  - 판정: 외부 시스템·인프라 자원 관문(결제·푸시·SMS·인증)은 PoEAA `Gateway` 패턴이고, 다른 BC 협력(ACL)·도메인 역할 추상은 일반 `Port`다. `Repository`/`Gateway`는 *확립 패턴명*(구현 유지)이고 `Port`는 *헥사고날 위치 표식*(구현은 `Adapter`)이라, 셋을 "역할 접미사" 한 묶음으로 보지 않는다.
- 금지: `Interface`/`Impl`처럼 추상/구현 *구분만을 위한 타입 표식* 접미사(`OrderRepositoryInterface`·`OrderRepositoryImpl` ✕). 추상/구현은 한정자 유무로 이미 구분된다(PEP 8). 역할 접미사(`Port`)와 타입 표식(`Interface`)의 차이: 전자는 객체의 *역할*, 후자는 추상/구현 *구분*용이라 금지한다. 같은 이유로 **`Port`도 *구현*에선 위치 표식이라 쓰지 않는다 — 일반 포트 구현은 `Adapter`다**(확립 패턴명 `Repository`/`Gateway`는 예외).

**표현(presentation) 컨트롤러** — HTTP 입력 어댑터는 ninja-extra 클래스 컨트롤러로 두고 **`<Aggregate>Controller`**(`OrderController`; `presentation_layer/api/`)로 명명한다. 애그리거트 개념명 + **역할 접미사 `Controller`**(`Repository`/`Gateway`처럼 객체의 *역할*을 나타내는 접미사)다. 함수형 Ninja `Router`는 레거시로 병기 가능하나, 신규 표현 어댑터는 컨트롤러를 기본으로 한다.

**파일명** — 파일명은 **그 안 주 클래스명의 snake_case**이며 그 클래스·개념을 **약어 없이** 반영한다: `order_repository.py`(○) / `order_repo.py`(✕). grep·예측 가능성을 위해 클래스명을 줄이지 않듯 파일명도 줄이지 않는다. 폴더는 종류 그룹일 뿐 파일 접미사를 좌우하지 않는다. 종류별 규칙:
- **유스케이스 연산 명명** — 쓰기 `<usecase>_command.py` → `class …Command`, 읽기 `<usecase>_query.py` → `class …Query`, 입력 `<usecase>_request.py` → `@dataclass class …Request`. 모두 `execute(request)`·repository/port 의존. (`_app`·`_service` 접미사 안 씀 — 위치 폴더가 종류를 표시; `_service.py`는 오케스트레이션 `service/`와 published_service의 서비스 모듈(`<service>_service.py`)에만.)
- **도메인 이벤트**: 파일·클래스 모두 **과거형** — `order_placed_event.py` → `class OrderPlacedEvent`.
- **명세(Specification)**: 약어 없이 **풀네임** — `order_active_specification.py` → `class OrderActiveSpecification`(`_spec` ✕).
- **표현 컨트롤러**: `<aggregate>_controller.py` → `class <Aggregate>Controller`(`@api_controller`) — 주 클래스명 snake_case 규약 정합(예 `order_controller.py` → `class OrderController`). 함수형 Ninja `Router` 레거시는 `api_<resource>.py`로 병기 가능.
- **스키마**: 입력 `schema_in.py` → `OrderIn`, 출력 `schema_out.py` → `OrderOut`, 에러 `error_out.py` → `ErrorOut`(In/Out 접미사).
- **조회(읽기)**: `<usecase>_query.py` → `class …Query`(인터랙터 연산 — `execute(request)`, repository 의존). 별도 읽기 *모델*(CQRS §5.4)은 선택이고, 공유 모델 repository 읽기로 충분하면 그대로 둔다.
- **OHS(published_service)**: 서비스 폴더 `<service>_service/` → 행위 모듈 `<service>_service.py`(공개 모듈 함수), 계약 3패키지 고정명 `request_contract/`·`response_contract/`·`exception_contract/` — request/response는 연산당 1파일 `<operation>_request_contract.py`/`<operation>_response_contract.py`(`<operation>`=공개 함수명), exception은 published base 모듈 `<service>_published_error.py`(파일명=주 클래스명 snake_case 규칙의 귀결)+예외 클래스당 1모듈, 공유 값 타입 모듈은 `_contract` 접미 없이 주 클래스명 snake_case. published base 예외 `<Service>PublishedError`(§2 OHS 내부 구조). 계약 클래스의 버전 접미(`V1` 등)는 프로젝트 재량이다(표준 비강제).

**폴더명(앱·애그리거트·feature)** — 위 파일·클래스 명명과 달리 폴더 도메인명은 **의미 판정이 필요해 권장 수위**다(백스톱 없음, discipline-reviewer 점검 — 클래스/파일 명명처럼 결정적으로 집행하지 않는다).
- **앱 `<app>`** = 핵심 애그리거트명과 **동일**하게 둔다(단일 BC·단일 애그리거트). 여러 애그리거트를 담으면 대표/컨텍스트명. snake_case. (placeholder `<app>`·`<aggregate>`는 §0-1 범례상 별개 슬롯이고, "동일 권장"은 단일 BC에 한정한다.)
- **애그리거트 `<aggregate>`** = **단수** 개념명. snake_case(`order/`·`member/`, `orders/` ✕).
- **feature `<feature>`** = 유스케이스 단위. 보통 앱당 1개(앱·애그리거트명과 같아도 됨)이고, 여러 유스케이스 그룹이면 분리한다.
- **금지: 앱명과 애그리거트명의 유사 변형**(`ordering` vs `order`) — 같게 하거나 명확히 다른 컨텍스트명으로 한다. 한 글자·복수형 차이로 헷갈리게 두지 않는다.

---

## 배경 (이 표준이 파생된 코퍼스)

이 표준은 아래 코퍼스 레이아웃의 구체화·변종이다. 레이아웃 권위는 이 문서가 갖고, 아래는 이론적 근거로만 인용한다(재정의하지 않는다).

- `architecture-ddd` §6.1 — 4계층 패키지 구조(`src/<context>/{domain,application,infrastructure,interface}/`). 이 표준은 같은 4계층을 `application/<app>/{..._layer}` 명명으로 구체화한 변종이다.
- `implementation-django` §3.1 — 표준 Django 레이아웃(`config/settings/` 분할 + `apps/<app>/`). 설정 분할·앱 단위 조직의 근거.
- `implementation-test` §4.2 — 테스트 의미군(`{unit,integration,e2e}`) 조직의 단독 소유자. `<app>/test/` 내부 구조가 여기서 온다.
