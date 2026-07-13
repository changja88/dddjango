# dddjango

**Django 프로젝트에 DDD(도메인 주도 설계)를 제대로 입히는 Claude Code 플러그인.**

`/dddjango <기능>` 한 줄이면, 한 기능을 **요구 정리 → 설계 → 구현(TDD)** 까지 전문 에이전트들이 협업해 현재 승인된 애플리케이션 계약으로 완성한다. 매 단계 당신의 승인을 받고 진행한다. Django DB migration lifecycle은 프로젝트의 별도 release/deployment 절차에 맡긴다.

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

설치된 버전 확인은 `codex plugin list` — 마켓플레이스별로 플러그인 상태·버전·경로가 표로 나온다:

```
$ codex plugin list
PLUGIN                       STATUS              VERSION  PATH
dddjango@changja88-dddjango  installed, enabled  1.1.0    ~/.codex/.tmp/marketplaces/changja88-dddjango/codex-dddjango
```

> 업데이트 후 세션을 재시작하세요. `upgrade`에서 마켓 이름을 생략하면 설정된 모든 Git 마켓플레이스를 한 번에 갱신합니다.

---

## 빠른 시작

기존 Django 프로젝트 루트에서 Claude Code를 실행하고:

```
/dddjango 재고가 있을 때만 주문을 생성하고 재고를 차감하는 기능
```

그러면 요구 정리부터 테스트까지 단계별로 진행되며, 각 단계마다 당신이 승인한다.

---

## 어떻게 동작하나

### 전문가 팀처럼 일한다

`/dddjango`를 실행하면 **Coordinator**(프로젝트 매니저 역할)가 붙어, 각 전문 에이전트에게 일을 나눠 주고 결과를 모은다. 당신은 코드를 직접 받아쓰는 게 아니라, **팀을 지휘하며 단계마다 승인**한다.

| 역할 | 하는 일 |
|---|---|
| **Coordinator** | 전체 진행·게이트·산출물 통합 (직접 코드는 안 씀) |
| **design-architect** | 통합 설계 명세 작성 (계층 배치·파일 구조 결정 포함) |
| **design-review-ddd / api / db** | 설계를 각자의 관점에서 **병렬 독립 리뷰** |
| **acceptance-tester** | 실패하는 인수 테스트 작성 (구현 전 기준 고정) |
| **coder** | TDD로 구현, 인수 테스트를 통과시킴 |
| **discipline-reviewer** | 구조·타입·클린코드 규율 감수 |

> 리뷰어는 기능에 따라 활성화된다 — **ddd는 항상**, API 계약이 바뀌면 **api**, 스키마·트랜잭션이 바뀌면 **db**가 붙는다.

### 세 개의 승인 게이트 — 운전석은 당신

진행은 **3개의 게이트**로 끊긴다. 각 게이트에서 요약을 보고 "승인 / 수정 요청"을 고른다. 승인 전에는 절대 다음으로 넘어가지 않는다.

- **G0 · 요구·경계** — 프로젝트를 의미적으로 읽기 전에 read-only preflight로 exact `migration_roots`·`migration_alias_targets`·`external_owned_opaque_paths`를 확정해 모든 탐색에서 먼저 제외한다. 그 밖의 영역에서 무엇을 만들지, 어디에 둘지(새 영역 vs 기존 영역 확장), 어떤 리뷰 관점을 켤지 정하고 현재 지원·영속·보안 의무의 근거를 수집한 뒤, migration 자산에 손대지 않았음을 확인할 단일 write-once G0 기준선을 잡는다.
- **G1 · 설계** — architect의 설계 명세 + 리뷰 반영 결과를 승인한다. 현재 의무의 근거·지원 종료·관찰 가능한 부재 여부를 여기서 확정하며, `unknown`은 남길 수 없다. 이 명세가 이후 테스트·코드의 **단일 근거**가 된다.
- **G2 · 구현** — 구현 코드 + 현재 계약에 맞춘 테스트 + 감수 리포트 + **19종 결정적 백스톱** 통과를 승인한다. `retain/update/add` 테스트와 프로젝트 전체 suite를 실제 실행하고, 스키마 영향이 있으면 애플리케이션 구현 완료와 배포 준비 상태를 분리해 보고한다.

> G2 직전에는 **19종의 결정적 백스톱**(파이썬 검사 스크립트)이 자동으로 돌아 구조·계약 회귀를 차단한다 — 4계층 골격, 컴포지션 루트, API 오류 선언/중앙화와 migration 트리 무변경 등을 고정밀로 검사해, 에이전트의 의미 감수가 놓칠 수 있는 위반을 마지막 안전망으로 잡는다.

> migration-boundary v11은 migration의 의미나 배포 안전성을 판단하지 않는 **무개입 자기감사**다. 첫 semantic read와 `.dddjango` 쓰기 전에 read-only preflight를 실행하고, manifest의 exact `migration_roots`·opaque hasher가 따라간 repo-internal `migration_alias_targets`·프로젝트/사용자가 미리 선언한 `external_owned_opaque_paths`를 이후 모든 탐색과 백스톱에서 먼저 prune한다. external 목록은 `TARGET_DIR` 기준으로 이미 존재하는 non-symlink regular exact file만 허용하며 portable 문자(`[A-Za-z0-9_./@+-]`)를 쓰고 Django settings·entrypoint·AppConfig 같은 구조 발견 source와 겹치지 않아야 한다. 선언이 없을 때의 `[]`는 “없다고 선언됨”이지 미발견 자산이 없다는 증명이 아니다.
>
> migration tree와 external exact file은 decode·parse·요약·LLM 입력 없이 path/type/byte SHA-256만 비교한다. repo-internal migration symlink target은 target byte와 canonical alias를 함께 기록해 prune하지만, repo-external target 내용은 읽지 않고 repo 쪽 link와 `outside-root` marker만 동결한다. opaque regular file의 hardlink는 alias를 안전하게 제외할 수 없어 fail-closed한다. bind mount처럼 symlink/hardlink가 아닌 별칭은 탐지하지 못하며, permission·owner·xattr·DB-only side effect·중간 생성 후 원복·마지막 scan 직후 race도 보장 범위 밖이다. 최초 preflight와 Phase 0 snapshot 사이의 의미 조사 중 외부 owner가 새 migration root나 lifecycle test를 동시에 만들면 최초 prune 집합에 없을 수 있으므로, 이 구간의 외부 동시 변경·quiescence도 보장하지 않는다.

> settings에서 흔한 literal 목록과 `DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS` 같은 fresh 정적 합성은 해석한다. 반면 direct mutable alias, method/subscript·alias-container mutation, 조건부/중첩 대입, 함수 호출 값, structural source의 syntax/encoding 오류·symlink·hardlink는 범위를 안전하게 확정할 수 없어 preflight exit 1로 중단한다. import side effect, 같은 모듈 함수 내부의 global/container mutation, 별도 모듈 내부 mutation까지 임의 Python 실행 의미를 완전 증명하는 도구는 아니다. 따라서 이 경계는 지원하는 제한된 정적 문법 안의 자기 비개입 감사이지, 임의 Django 설정에 대한 절대적 no-touch 증명이 아니다.
>
> 한 내부 작업 사이클은 baseline 절대 경로와 SHA-256을 canonical receipt로 고정한 **단일 write-once G0 pair**를 일반 감사 전과 모든 read-only 감사 후에 그대로 비교한다. 내부 반송·수정 때문에 새 snapshot을 만들지 않는다. 새 lifecycle file을 처음 발견하거나 boundary가 exit 2면 그 사이클의 설계·테스트·감사 증거를 전부 stale 처리하고, 사용자가 외부 작업 완료와 quiescence를 명시 확인한 뒤에만 Phase 0 preflight부터 새 사이클을 시작한다. 최종 non-migration diff도 변경 원장의 exact file 중 세 opaque 집합과 alias를 미리 제외한 allowlist로만 `git diff -- <allowlisted paths>`를 실행해 만들며, 전역 diff를 만든 뒤 내용을 필터링하지 않는다. 테스트 source inventory의 fallback은 `test/`·`tests/`와 `test_*.py`·`*_test.py`·`tests.py`다. 기계 검사가 clean이어도 결과는 항상 `migration verification=범위 밖·미검증`이다.

### 워크스루: "재고 있을 때만 주문 생성" 기능

```
/dddjango 재고가 있을 때만 주문을 생성하고 재고를 차감하는 기능
```

**1) G0 — 요구·경계 확정**
Coordinator가 스코프를 정리해 보여준다: "주문 생성 시 재고를 확인·차감. 재고 부족이면 거부." 그리고 묻는다 — 이 기능을 *새 `orders` 영역*으로 둘까, 기존 영역에 넣을까? 리뷰는 ddd + api(엔드포인트 생김) + db(재고 차감=트랜잭션)로 켤까? → 당신이 승인.

**2) 설계 → G1**
design-architect가 설계 명세를 쓴다 — `Order` 애그리거트, 재고는 다른 컨텍스트라 `ProductStockPort`로 협력, 동시성 안전한 차감 방식, 4계층 파일 배치까지. 동시에 ddd·api·db 리뷰어가 **병렬로** 독립 비평하고, architect가 이를 반영·중재한다. → 최종 설계 명세를 당신이 승인.

**3) 구현(TDD) → G2**
acceptance-tester가 먼저 **실패하는** 인수 테스트를 쓴다(예: "재고 3개일 때 5개 주문 → 409, 재고 그대로"). coder가 슬라이스 단위로 Red→Green→Refactor를 돌려 테스트를 통과시키고, discipline-reviewer가 구조·타입을 감수한다. → 코드·테스트·감수 결과를 당신이 승인.

**4) 마무리**
실제로 돌린 검증만 보고한다 — 테스트 결과, `manage.py check`, (구성돼 있으면) mypy strict. 모델 선언이 스키마에 영향을 주면 migration 검증은 `범위 밖·미검증`, 배포 준비는 `외부 절차 대기`로 분리해 표시한다.

---

## 무엇이 만들어지나

기존 Django라면 보통 `models.py`·`views.py`에 다 욱여넣지만, dddjango는 한 기능을 이렇게 정돈해 만든다:

```
your_project/
└── application/                # 신규 feature 앱의 기본 컨테이너
    └── orders/
        ├── composition_root.py             # DI 배선 — build_place_order_command() 매요청 팩토리
        ├── orders_api_router.py            # HTTP 진입점 등록
        ├── domain_layer/                   # 순수 비즈니스 규칙 (프레임워크 무관)
        │   └── order/                       # 애그리거트(개념) 1차
        │       ├── order.py                 # 애그리거트 루트 — class Order
        │       ├── entity/  value_object/   # 종속 엔티티·값 객체 (종류 2차 폴더)
        │       ├── repository/order_repository.py   # OrderRepository (추상 인터페이스)
        │       ├── port/product_stock_port.py       # 다른 컨텍스트 협력 포트
        │       └── exception.py
        ├── application_layer/              # 유스케이스 흐름 (무엇을 언제)
        │   └── place_order/
        │       ├── command/place_order_command.py   # PlaceOrderCommand.execute(request)
        │       └── dto/place_order_request.py
        ├── infra_layer/                    # ORM·외부 연동 등 세부 구현
        │   ├── django_orders/               # 신규 Django app 패키지
        │   │   ├── apps.py
        │   │   ├── models.py                 # class OrderModel(models.Model)
        │   │   └── migrations/              # 존재한다면 framework/external lifecycle 소유
        │   ├── repository/django_order_repository.py  # DjangoOrderRepository (구현)
        │   └── acl/product_stock_adapter.py           # 다른 BC를 번역해 소비
        ├── presentation_layer/             # 바깥 계약 (종류 1차: api/ · schema/)
        │   ├── api/order_controller.py       # django-ninja 컨트롤러 (얇은 어댑터)
        │   └── schema/                       # 입출력 계약 schema_in·schema_out·error_out
        └── test/                           # 의미군 분리
            └── unit/  integration/  e2e/
```

핵심 규약이 일관되게 강제된다 — `application/` 컨테이너, 4계층 물리 분리, **개념 1차·종류 2차** 폴더(단 `presentation_layer`는 `api/`·`schema/`가 고정 종류 폴더), ORM은 `<Name>Model`·도메인은 bare 이름, 추상/구현 명명 규칙(`OrderRepository` ↔ `DjangoOrderRepository`), DI 배선은 BC 루트의 `composition_root.py`, 테스트 unit/integration/e2e 분리. **19종의 결정적 백스톱은 고정밀 직접 형태를 자동 검사하고, 명명 의미·기존 규약 판단과 저-recall 사각은 독립 감수자가 함께 검토**한다.

> 대상 프로젝트에 **이미 확립된 구조 규약이 있으면 그것을 우선**한다. 위 표준은 신규·미조직 영역의 기본값이다. 기존 brownfield Django persistence app과 `migrations/`는 작업 대상이 되어도 물리적으로 옮기지 않고, 새 도메인·응용 코드를 adapter/repository 경계로 연결한다.

진행 메모와 설계 명세는 `.dddjango/<날짜>-<기능-slug>/`(`scope.md`, `design-spec.md`)에 남는다 — 한 기능 = 한 폴더이고, 코드와 함께 커밋해 설계 결정 기록으로 남긴다.

---

## 신규 기능 vs 부분 수정

dddjango는 작업 규모를 보고 알맞게 움직인다.

- **신규 기능** — 풀 파이프라인(요구 → 설계 → 구현)을 모두 거친다.
- **부분 수정** — 전체를 다시 돌지 않는다. 영향 범위만 확인하고, 바뀐 설계 부분과 영향받는 테스트를 `retain/update/delete/add`로 조정한다. 계약 변경이 없으면 설계 게이트를 건너뛸 수 있지만, 계약이 바뀌면 인수 테스트 조정과 의미 감수를 생략하지 않는다.

영구 테스트는 과거 구현 기록이 아니라 **현재 승인된 의무**만 검증한다. 명세가 바뀌면 현재 지원·영속 데이터/이벤트·보안/개인정보/규제·명시적 부재 의무를 근거로 기존 테스트를 함께 `retain/update/delete/add`하며, 종료된 스펙만 증명하는 stale/history test는 같은 변경에서 update하거나 delete한다. 반대로 지원 중인 구버전이나 현재 읽어야 하는 과거 데이터·이벤트를 단지 오래됐다는 이유로 지우지는 않는다.

---

## 요구 사항

- **Claude Code**
- **기존 Django 프로젝트** — 이 플러그인은 한 기능을 빌드하는 도구이지, 프로젝트를 새로 부트스트랩하지 않는다.
- **스택**: 테스트는 프로젝트의 기존 명령과 설정을 존중한다. 새 pytest 테스트가 필요한 프로젝트에서는 **pytest**(pytest-django) 관용구를 사용한다. API는 **django-ninja**가 기본이며, 프로젝트에 DRF·plain Django 관례가 확립돼 있으면 설계자가 그것을 존중한다. mypy strict는 구성돼 있으면 함께 검증한다. `--no-migrations` 같은 전역 우회 설정은 강제하지 않는다. 변경하지 않은 runner가 test DB 준비나 외부 소유 테스트를 통해 migration 동작을 간접 수행할 수 있지만 이를 외부 소유 부수 실행으로만 보고 migration 검증으로 해석하지 않는다.

---

## 구성 요소

- **커맨드 1개**: `/dddjango`
- **에이전트 7개**: `design-architect`, `design-review-ddd`, `design-review-api`, `design-review-db`, `acceptance-tester`, `coder`, `discipline-reviewer`
- **스킬 11개**: 아키텍처(`architecture-ddd`/`-api`/`-db`), 규율(`discipline-houserules`/`-cleancode`/`-tdd`), 구현(`implementation-django`/`-django-ninja`/`-django-web`/`-python`/`-test`)
- **결정적 백스톱 19종**: 구조·계약 회귀와 migration 트리 변경을 G2 직전에 자동 차단하는 파이썬 검사 스크립트

---

## 라이선스

[MIT](LICENSE)
