# dddjango — Claude Code · Codex

**Django 프로젝트에 DDD(도메인 주도 설계)를 제대로 입히는 Claude Code·Codex 플러그인.**

Claude Code의 `/dddjango <기능>` 또는 Codex의 `dddjango를 사용해 <기능>` 요청으로 시작하면, 한 기능을 **요구 정리 → 설계 → 구현(TDD)** 까지 전문 에이전트들이 협업해 깔끔한 4계층 DDD 구조로 완성한다. 매 단계 당신의 승인을 받고 진행한다.

---

## 왜 dddjango인가

기본 Django는 빠르게 시작하기 좋지만, 기능이 커질수록 비즈니스 규칙이 흩어진다.

- 도메인 규칙이 `models.py`(fat model)와 `views.py`에 뒤섞이고,
- ORM 모델이 곧 도메인 모델이라 DB 스키마와 비즈니스 로직이 한 덩어리가 되며,
- 결국 "한 줄 고치면 어디가 깨지는지 모르는" 코드가 된다.

**dddjango는 한 기능을 추가할 때마다 이걸 4계층 DDD로 정돈한다:**

| 계층 | 책임 | 예 |
|---|---|---|
| **domain** | 순수 비즈니스 규칙·불변식 (프레임워크 무관) | `Order` 엔티티, `Quantity` 값 객체 |
| **application** | 유스케이스 흐름 (무엇을 언제) | `PlaceOrder` 커맨드 |
| **infra** | ORM·외부 연동 등 세부 구현 | `OrderModel`(Django ORM), `DjangoOrderRepository` |
| **presentation** | 바깥 계약 (API 등) | django-ninja 엔드포인트 |

도메인 모델(`Order`)과 ORM 모델(`OrderModel`)을 **분리**하고, 다른 바운디드 컨텍스트는 **ACL/OHS로 번역**해 연결한다. 즉, Django 위에서 교과서적인 DDD 구조를 강제로 지켜 준다 — 이게 핵심이다.

> 이건 프로젝트를 새로 만드는 도구가 아니라, **이미 있는 Django 프로젝트에 한 기능을 DDD로 더하는** 도구다.

---

## 설치

**Claude Code** — 슬래시 커맨드로:

```
/plugin marketplace add changja88/dddjango
/plugin install dddjango@changja88-dddjango
```

**Codex** — CLI로:

```
codex plugin marketplace add changja88/dddjango --ref main
codex plugin add dddjango@changja88-dddjango
```

> 두 마켓 모두 같은 GitHub 레포(`changja88/dddjango`)에서 받습니다. 설치 후 세션을 재시작하세요.

화면(웹 표현계층)까지 만들려면 자매 플러그인 **dddjango-web**을 함께 설치한다:

```
/plugin install dddjango-web@changja88-dddjango          # Claude Code
codex plugin add dddjango-web@changja88-dddjango         # Codex
```

---

## 작업 요청 가이드

설치한 각 플러그인 루트의 `REQUEST_GUIDE.md`가 해당 runtime의 권위 있는 가이드 사본이다. 아래 링크는 저장소에서 최신 가이드를 찾는 진입점이다.

| 플러그인 | 요청에 담을 핵심 입력 | 이어서 넘기는 조건 | 가이드 |
|---|---|---|---|
| **dddjango** | 비즈니스 규칙·상태 전이·실패 원자성·보존할 현행 계약·조사 evidence·범위와 미확정 | backend 계약을 준비한 뒤 화면 구현이 필요하면 `dddjango-web`으로 넘긴다. | [dddjango 작업 요청 가이드](dddjango/REQUEST_GUIDE.md) |
| **dddjango-web** | 정확한 시안·viewport·상태·interaction·실제 URL+JSON API 계약·사람이 비교할 완료 기준 | 필요한 endpoint가 없거나 인증·권한·업무 규칙·데이터 변경이 필요하면 먼저 `dddjango`로 넘긴다. | [dddjango-web 작업 요청 가이드](dddjango-web/REQUEST_GUIDE.md) |

가이드에는 30초 최소 요청과 복잡한 작업용 권장 요청서가 있다. 모르는 내용은 추측하지 말고 `미확정`으로 남기며, 템플릿을 채워도 G0·G1·G2의 질문과 승인은 생략되지 않는다.

---

## 업데이트

**Claude Code** — 슬래시 커맨드로 (마켓 메타 갱신 → 플러그인 갱신 순서):

```
/plugin marketplace update changja88-dddjango
/plugin update dddjango@changja88-dddjango
```

**Codex** — CLI로. Codex에는 별도 `plugin update` 커맨드가 없다 — 설치된 플러그인이 마켓플레이스 스냅샷 디렉터리에서 직접 로드되므로, **스냅샷을 갱신하면 그게 곧 플러그인 업데이트**다:

```
codex plugin marketplace upgrade changja88-dddjango
```

설치된 상태와 현재 버전 확인은 `codex plugin list`로 할 수 있다:

```
$ codex plugin list
```

> 업데이트 후 세션을 재시작하세요. `upgrade`에서 마켓 이름을 생략하면 설정된 모든 Git 마켓플레이스를 한 번에 갱신합니다.

---

## 빠른 시작

기존 Django 프로젝트 루트에서 사용하는 플랫폼에 맞게 시작한다.

| Claude Code | Codex |
|---|---|
| `/dddjango 재고가 있을 때만 주문을 생성하고 재고를 차감하는 기능` | `dddjango를 사용해 재고가 있을 때만 주문을 생성하고 재고를 차감하는 기능을 만들어 줘.` |
| `/dddjango-web "주문 목록 화면을 시안과 실제 API 계약에 맞춰 만들어 줘" <OpenAPI 3.x JSON URL 또는 로컬 경로>` | `dddjango-web을 사용해 주문 목록 화면을 시안과 실제 URL+JSON API 계약에 맞춰 만들어 줘.` |

`dddjango`는 요구 정리부터 테스트까지, `dddjango-web`은 화면 요구 정리부터 시안·계약 검증까지 단계별로 진행하며 각 게이트에서 당신이 승인한다.

---

## 어떻게 동작하나

### 전문가 팀처럼 일한다

`/dddjango`를 실행하면 **Coordinator**(프로젝트 매니저 역할)가 붙어, 각 전문 에이전트에게 일을 나눠 주고 결과를 모은다. 당신은 코드를 직접 받아쓰는 게 아니라, **팀을 지휘하며 단계마다 승인**한다.

| 역할 | 하는 일 |
|---|---|
| **Coordinator** | 전체 진행·게이트·산출물 통합 (직접 코드는 안 씀) |
| **design-architect** | 통합 설계 명세 작성 (계층 배치·파일 구조 결정 포함) |
| **design-review-ddd / api / db** | 설계를 각자의 관점에서 **병렬 독립 리뷰** |
| **acceptance-tester** | 승인된 외부 계약 테스트만 조정하고 필요한 Red 작성 |
| **coder** | 승인된 내부 계약만 TDD로 구현하고 기존 검증 anchor를 통과시킴 |
| **discipline-reviewer** | 구조·타입·클린코드 규율 감수 |

> 리뷰어는 기능에 따라 활성화된다 — **ddd는 항상**, API 계약이 바뀌면 **api**, 스키마·트랜잭션이 바뀌면 **db**가 붙는다.

### 세 개의 승인 게이트 — 운전석은 당신

진행은 **3개의 게이트**로 끊긴다. 각 게이트에서 요약을 보고 "승인 / 수정 요청"을 고른다. 승인 전에는 절대 다음으로 넘어가지 않는다.

- **G0 · 요구·경계** — 무엇을 만들지, 어디에 둘지(새 영역 vs 기존 영역 확장), 어떤 리뷰 관점을 켤지 확정한다.
- **G1 · 설계** — architect의 설계 명세 + 리뷰 반영 결과와 **영구 테스트 입장표**를 승인한다. 이 명세가 이후 테스트·코드의 **단일 근거**가 된다.
- **G2 · 구현** — 구현 코드 + 승인된 테스트 결정별 결과 + 테스트 diff 감수 + **27종 결정적 백스톱** 통과를 승인한다.

> G2 직전에는 **27종의 결정적 백스톱**(파이썬 검사 스크립트)이 자동으로 돌아 측정 대상인 구조·계약 회귀를 차단한다 — 컨테이너 위치, 표준 트리 골격(140행), 컴포지션 루트, 컨텍스트 격리, 명명·업무 어휘, API 오류 Schema·controller 직접 반환·OpenAPI 선언 등을 검사한다. 통과 결과는 이 검사 범위의 신규 위반이 없다는 뜻이며, 설계 의미의 정답이나 저장소 전체가 clean임을 증명하지 않는다.

### 테스트는 현행 계약만 보고, 입장 심사 후 만든다

dddjango가 만드는 영구 테스트의 기준은 현재 구현이나 과거 이력이 아니라 **G1/G1′에서 승인된 현행 요구·설계·지원 계약**이다. Architect는 테스트 후보마다 `보호할 계약과 근거`, `그 테스트만 잡는 production failure`, `기존 권위 테스트의 중복 보호`, `결정`, `소유자와 경로`를 적는다. 결정은 `add/update/reuse/retain/remove/reject/pending` 중 하나이며, `pending`은 G1을 막고 `reuse/reject`에서는 새 테스트 파일·case·assertion·helper를 만들지 않는다.

Python·Django·Pydantic의 기본 동작, private helper나 validator 배치, import 성공, coverage 비율은 그 자체로 제품 테스트가 아니다. 반대로 도메인 불변식, application 원자성, 독자적인 DB race/constraint, adapter 변환, 승인된 HTTP·이벤트·공개 consumer 계약은 각자 놓칠 production failure가 있으면 유효하다. migration 파일·과거 model state·forward/reverse 자체를 검증하는 새 테스트나 시나리오는 만들지 않되, 지원 중인 구 API·기존 데이터·발행 이벤트·현재 회귀 불변식을 보호하는 기존 테스트는 보존한다. migration 구현·rollout/backfill 검토도 계속 수행한다.

### 워크스루: "재고 있을 때만 주문 생성" 기능

```
/dddjango 재고가 있을 때만 주문을 생성하고 재고를 차감하는 기능
```

**1) G0 — 요구·경계 확정**
Coordinator가 스코프를 정리해 보여준다: "주문 생성 시 재고를 확인·차감. 재고 부족이면 거부." 그리고 묻는다 — 이 기능을 *새 `orders` 영역*으로 둘까, 기존 영역에 넣을까? 리뷰는 ddd + api(엔드포인트 생김) + db(재고 차감=트랜잭션)로 켤까? → 당신이 승인.

**2) 설계 → G1**
design-architect가 설계 명세를 쓴다 — `Order` 애그리거트, 재고는 다른 컨텍스트라 `ProductStockPort`로 협력, 동시성 안전한 차감 방식, 4계층 파일 배치와 테스트 후보별 입장 결정까지. 동시에 ddd·api·db 리뷰어가 **병렬로** 계약 근거·독자 실패·중복 여부를 비평하고, architect가 이를 반영·중재한다. → 최종 설계 명세와 테스트 입장표를 당신이 승인.

**3) 구현(TDD) → G2**
`add/update`로 승인된 외부 계약이 있으면 acceptance-tester가 먼저 실패하는 인수 테스트를 쓴다(예: "재고 3개일 때 5개 주문 → 409, 재고 그대로"). coder는 승인된 도메인·application·DB·adapter 결정만 슬라이스 단위 Red→Green→Refactor로 구현한다. `reuse`는 기존 테스트를 검증 anchor로만 쓰고, `reject`는 테스트 역할에 보내지 않는다. discipline-reviewer가 각 test diff를 G1 결정과 대조한다. → 코드·테스트·감수 결과를 당신이 승인.

**4) 마무리**
실제로 돌린 검증만 보고한다 — 테스트 결과, 마이그레이션, `manage.py check`, (구성돼 있으면) mypy strict.

---

## 무엇이 만들어지나

기존 Django라면 보통 `models.py`·`views.py`에 다 욱여넣지만, dddjango는 한 기능을 이렇게 정돈해 만든다:

```
your_project/
├── framework/                              # 저장소 횡단 공용 — BC를 모른다
│   └── ninja/
│       ├── __init__.py
│       └── framework_error_schema.py       # contract scope의 공통 FrameworkErrorSchema 하나
└── application/                # 모든 feature 앱(BC)의 컨테이너 (루트 평면 금지)
    └── orders/
        ├── composition_root/               # DI 배선 «폴더» — BC 루트
        │   ├── dependency_wiring.py         # build_place_order_command() 매요청 팩토리
        │   └── event_wiring.py              # 사실(이벤트) 구독 결선
        ├── published_event/                 # 밖에 공개하는 사실
        ├── driving_layer/                  # 입구 — 전송(transport) 1차
        │   ├── api/
        │   │   ├── api_router.py            # register_orders_api(api); 자기 controller만 등록
        │   │   ├── bc_error_schema.py       # OrderErrorCode·OrderErrorSchema·prepared concrete
        │   │   └── order/                   # <area>
        │   │       ├── order_controller.py  # 구체 예외를 catch하고 오류 schema를 직접 반환
        │   │       └── schema/              # schema_in.py · schema_out.py
        │   ├── open_host_service/           # 다른 BC가 부르는 창구 — 같은 프로세스 함수 호출
        │   ├── cron_job/
        │   └── event_subscription/
        ├── application_layer/              # 유스케이스 흐름 (무엇을 언제)
        │   ├── order/                       # <area>
        │   │   └── place_order/
        │   │       ├── place_order_use_case.py   # 유스케이스 본문 — execute 규약
        │   │       ├── place_order_command.py    # 들어가는 자료 (안 쓰는 쪽은 빈 파일)
        │   │       ├── place_order_query.py
        │   │       └── place_order_result.py
        │   └── port/                        # 능력·협력 포트 선언
        │       └── product_stock/product_stock_port.py   # 다른 컨텍스트 협력 포트
        ├── domain_layer/                   # 순수 비즈니스 규칙 (프레임워크 무관)
        │   └── order/                       # 애그리거트(개념) 1차
        │       ├── order.py                 # 애그리거트 루트 — class Order
        │       ├── entity/  value_object/  event/
        │       ├── order_repository.py      # OrderRepository (추상 — 도메인 소유)
        │       └── exception/
        ├── driven_layer/                   # 밖으로 나가는 세부 구현
        │   ├── django_orders/               # 여기서 startapp
        │   │   ├── apps.py
        │   │   ├── models/order_model.py    # class OrderModel(models.Model)
        │   │   └── migrations/              # 생성물만 — 사람이 손대지 않는다
        │   └── adapter/
        │       ├── persistence/repository/order_repository.py    # DjangoOrderRepository (구현)
        │       └── anticorruption_layer/products/product_stock_adapter.py  # 다른 BC를 번역해 소비
        └── test/                           # 승인된 테스트가 있을 때만 다섯 자식
            └── unit/  integration/  e2e/  factories/  fake/
```

핵심 규약이 일관되게 강제된다 — `application/` 컨테이너, 표준 트리 골격(모든 BC가 내용과 무관하게 같은 140행 트리 — 빈 칸도 빈 패키지로 실현), 4계층(driving·application·domain·driven) 물리 분리, 입구는 전송 1차·도메인은 개념 1차, ORM은 `<Name>Model`·도메인은 bare 이름, 추상/구현 명명 규칙(`OrderRepository` ↔ `DjangoOrderRepository`), DI 배선은 BC 루트 «폴더» `composition_root/`(결선은 `dependency_wiring.py`). 테스트가 실제 승인된 경우에만 다섯 자식(unit/integration/e2e/factories/fake)으로 배치한다. **이 가운데 자동 검사 대상 규율은 27종의 결정적 백스톱이 구현 게이트(G2) 직전에 검증**한다.

> 승인 스코프가 새로 만드는 파일과 기존 파일에 추가·변경하는 코드에는 위 규율을 적용한다. 현행 계약과 artifact evidence는 보존하며, 스코프 밖 기존 배치의 이동·개명·재배선은 별도 G0 결정 없이 하지 않는다.

Django Ninja의 신규 `dddjango-code-json` 오류 계약은 contract scope당 공통
`FrameworkErrorSchema` 하나(`framework/ninja/framework_error_schema.py`)를
두지만 **그 property 목록은 플러그인이 정하지 않는다**. 기존 프로젝트의 exact shape를
보존하거나, 신규 shape의 field/type/required/default/nullable/Field metadata/model config·validator/serializer/computed field/Pydantic hook inventory와 effective semantics·wire 결과를
별도로 보여 주고 명시 승인받는다. 이후 shape 변경도 일반 기능 승인과 분리해 다시 승인받는다.
각 BC의 단일 `driving_layer/api/bc_error_schema.py`는 `<Bc>ErrorCode` StrEnum 하나,
slot 6이 지정한 식별자 field 하나를 그 Enum으로 좁힌 `<Bc>ErrorSchema` 하나, 인자 없이 생성할
수 있는 prepared concrete 오류를 필요한 만큼 소유한다. BC base는 식별자 타입만
`str`에서 자기 Enum으로 바꾸고 공통 annotation의 nullable 구조·required/default·`Field(...)`
metadata를 보존한다. concrete는 새 필드·validator·`model_config`를 추가하지 않고, 필드를
재선언할 때 annotation/nullability와 `Field(...)` metadata를 그대로 반복한 채 승인된 공통
필드의 사건별 기본값만 고정한다.

```python
class OrderErrorCode(StrEnum):
    OUT_OF_STOCK = "order_out_of_stock"


class OrderErrorSchema(FrameworkErrorSchema):
    error_type: OrderErrorCode


class OutOfStockError(OrderErrorSchema):
    error_type: OrderErrorCode = OrderErrorCode.OUT_OF_STOCK
    msg: str = "The requested quantity is not available."
    is_show: bool = True
```

위 `error_type/msg/is_show`도 한 프로젝트가 승인할 수 있는 shape 예시일 뿐 dddjango의
기본값이 아니다. body에 HTTP `status` property가 없어도 controller가 HTTP status를 직접
선택하므로 문제없다.
오류 schema의 exact property/type/required/default/nullable/Field metadata/config/validator/serializer/computed field/Pydantic hook inventory와 effective semantics/wire 의미는 기존 계약을 보존하거나
신규 G1에서 별도로 명시 승인받는다. controller는 application 호출 한 문장만 좁은 `try`에
두고 알려진 구체 예외만 catch한다. 준비된 concrete 오류를 인자 없이 직접 생성해
`Status(<승인된 HTTP status 표현>, error)`로 반환하며,
`response={409: OrderErrorSchema}`처럼 BC base를 OpenAPI에 선언한다. 고정값을 채우는 factory,
오류 schema를 HTTP 응답으로 직렬화하는 helper, BC/custom exception handler, broad catch는 만들지
않는다.

```python
try:
    order = command.execute(request_dto)
except OutOfStockException:
    error = OutOfStockError()
    return Status(status.HTTP_409_CONFLICT, error)
```

인증·인가·요청 validation·route 404·throttle·일반 `HttpError`·미식별 500은 BC
오류 schema로 바꾸지 않고 Django Ninja/Django 기본 처리를 그대로 쓴다. project `api.py`는
API 인스턴스와 API 자체 설정만, BC `driving_layer/api/api_router.py`는 전달받은 API에 자기 controller 등록만,
project `urls.py`는 모든 registrar 호출과 API mount만 소유한다. 독립
public/internal·version·core profile scope를 새로 나눈다면 G1에서 별도 계약으로 승인한다.
이미 배포된 brownfield 오류 표면은 승인 없이 새 profile로 이주하지 않는다.

진행 메모와 설계 명세는 `.dddjango/<날짜>-<기능-slug>/`(`scope.md`, `design-spec.md`)에 남는다 — 한 기능 = 한 폴더이고, 코드와 함께 커밋해 설계 결정 기록으로 남긴다.

---

## 신규 기능 vs 부분 수정

dddjango는 작업 규모를 보고 알맞게 움직인다.

- **신규 기능** — 풀 파이프라인(요구 → 설계 → 구현)을 모두 거친다.
- **부분 수정** — 전체를 다시 돌지 않고 영향 범위를 확인해 바뀐 설계 부분과 영향받는 테스트를 재실행한다. G1 생략은 승인된 현행 설계·계약이 유효하고, 관련 테스트 입장에 `pending`이 없으며, expected result나 지원 계약의 삭제·약화·이름 변경 같은 lifecycle 변경도 없음을 Coordinator가 재검증한 경우에만 가능하다.

---

## 요구 사항

- **Claude Code 또는 Codex**
- **기존 Django 프로젝트** — 이 플러그인은 한 기능을 빌드하는 도구이지, 프로젝트를 새로 부트스트랩하지 않는다.
- **스택**: 테스트는 **pytest**(pytest-django)를 기준으로 하며, 새 설정은 승인된 테스트 입장 `add/update`일 때만 추가·변경한다. `reuse`이면 기존 runner를 검증 anchor로 사용한다. API는 **django-ninja**가 기본이며, 프로젝트에 DRF·plain Django 관례가 확립돼 있으면 설계자가 그것을 존중한다. mypy strict는 구성돼 있으면 함께 검증한다.

---

## 구성 요소

- **커맨드 1개**: `/dddjango`
- **에이전트 7개**: `design-architect`, `design-review-ddd`, `design-review-api`, `design-review-db`, `acceptance-tester`, `coder`, `discipline-reviewer`
- **스킬 11개**: 아키텍처(`architecture-ddd`/`-api`/`-db`), 규율(`discipline-houserules`/`-cleancode`/`-tdd`), 구현(`implementation-django`/`-django-ninja`/`-django-web`/`-python`/`-test`)
- **결정적 백스톱 27종**: 구조·계약 회귀를 G2 직전에 자동 차단하는 파이썬 검사 스크립트

---

## 자매 플러그인: dddjango-web

`/dddjango-web <화면 요구>` — **실제 URL+JSON API 계약을 외부 클라이언트처럼 소비**해 화면(웹 표현계층)을 빌드하는 **독립 플러그인**이다. API를 만든 도구가 반드시 dddjango일 필요는 없다.

- **시나리오 3종**: 클로드 디자인 시안 반영 · 기존 웹페이지 카피(외형은 같게, HTML 구조는 표준으로 재구축) · 기존 화면 수정
- **표준**: 순수 HTML + HTMX + CSS(커스텀 JS 없음) · 요청 구동 MVVM(view/view_model/state + 템플릿) · design_system 토큰
- **경계**: `web/` 트리는 «내부의 외부 클라이언트» — 백엔드 코드를 import하지 않고(백스톱이 차단) in-process HTTP로 계약만 소비한다. 필요한 API가 없으면 `/dddjango`로 발주를 안내한다.
- **구성**: 커맨드 1(`/dddjango-web`) · 에이전트 4(`design-architect-web`·`design-review-web`·`coder-web`·`discipline-reviewer-web`) · 스킬 4(`architecture-web`·`implementation-ui`·`discipline-web-houserules`·`discipline-cleancode`) · 결정적 백스톱(구조·격리·명명·순수성) + 시안 절단 도구
- **검증**: 결정적 백스톱은 측정 대상인 구조 규율만 확인하며 전체 품질이나 픽셀 동일을 증명하지 않는다. 자동 측정 결과와 규율 감사를 함께 보고, 승인한 상태·viewport의 전체 스크롤과 동작은 게이트에서 **사용자가 육안 확인**한다.

---

## 개발 (메인테이너)

이 저장소를 직접 고치려면 [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)를 본다 — 규범 정본(온톨로지 그래프)과 투영물의 관계, 수정 절차, 검증·릴리즈 방법을 담고 있다.

---

## 라이선스

[MIT](LICENSE)
