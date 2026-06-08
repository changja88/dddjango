# django-ninja 클래스 기반 뷰(컨트롤러) 도입 — 설계 문서

- **날짜**: 2026-06-08
- **상태**: v3 — 적대 7리뷰 반영(v1 BLOCKER 2 + v2 MAJOR 7 해소). 구현 계획 진입
- **범위**: dddjango 플러그인 표준 변경 (Claude·Codex 양 런타임 미러)

---

## 1. 목적

ninja API operation을 **함수형에서 ninja-extra 클래스 기반 컨트롤러로 강제**한다. **이번 작업이 touched(신규 생성·수정)한 operation 표면은 무조건 클래스**로 만든다 — 아무리 작아도(예외: §3.7 외부 공개 415). 미관여 기존 함수형은 grandfather(§9). 새 operation은 해당 애그리거트 컨트롤러를 탐색해 있으면 메서드로 포함, 없으면 새로 만든다(§6).

> "무조건 클래스"의 판정 술어 = **touched**(houserules 어휘). touched 표면에 함수형 operation 잔존 = 위반(reviewer **important** 1차·결정적 차단은 3차 백스톱), untouched 기존 함수형 = 면제(grandfather). §9와 교차.

---

## 2. 핵심 사실 (조사·소스로 확정)

1. **순수 django-ninja엔 클래스 기반 뷰가 없다.** `@router.path(...)` CBV는 *proposal·미구현*, `ninja/router.py`에 `path` 부재 → `AttributeError`.
2. **클래스 컨트롤러 = `django-ninja-extra`(별도 확장).** `@api_controller` + `route` + `register_controllers`.
3. **신뢰성**: 활발(★587·MIT)하나 1인·0.31.x → 수용하되 의존 표면을 "컨트롤러 라우팅"으로 최소화(blast radius 축소).
4. **호환성**(소스 검증):
   - 인증: ninja `auth=` 그대로, permission opt-in.
   - 예외: `NinjaExtraAPI(NinjaAPI)` 상속 → `@api.exception_handler` 그대로 동작. **§6.2 중앙화 보존, NJ-7 catch-all 집행(reviewer + `check-catch-all-handler` 백스톱) 보존** — 단 §6.2 표준 *텍스트*엔 catch-all 레시피가 없고, NJ-7은 RUBRIC 차원·reviewer·백스톱으로만 존재(분석단위가 인스턴스라 `NinjaExtraAPI`에서 불변).
   - 415: 컨트롤러는 `add_decorator(mode="view")`가 구조적으로 없다 → §3.7로 처리.
5. **추가 배선 요구**:
   - `INSTALLED_APPS`에 `'ninja_extra'` 등록.
   - 컨트롤러 테스트 = `ninja_extra.testing.TestClient(Controller)`.
   - `@api_controller`는 `use_unique_op_id=True`로 **OpenAPI operationId 규칙을 바꾼다**(§9에서 `False` 옵션 검토).
   - `@api_controller`가 `__init__`에 DI 자동 적용 — 무인자 인터랙터라 현재 무해.
   - 함수형 Router와 컨트롤러는 같은 `NinjaExtraAPI` 인스턴스에 공존 지원(소스 확인).
6. **정정**: `architecture-api`는 415/406을 *의미*만 정의하고 적용을 강제하지 않으며(재량) 프레임워크 비종속(P1) → **건드리지 않는다**.

---

## 3. 설계 결정 (확정)

### 3.1 ninja-extra 최소 사용
클래스 라우팅(`@api_controller` + `route`)**만**. 제외: permission·throttling·pagination·ModelController·ninja-extra 예외(`APIException`). 나머지는 순수 ninja.

### 3.2 진입점 = NinjaExtraAPI + 앱 등록
API 인스턴스를 `NinjaExtraAPI`로(상위호환). **`INSTALLED_APPS += ['ninja_extra']`.**

### 3.3 컨트롤러 단위 = 애그리거트
한 컨트롤러 = 한 애그리거트(앱). 크면 리소스(prefix)별 분할 허용. 기본 단일, 분배는 §6 탐색 규칙이 결정화.

### 3.4 ControllerBase 미상속
`@api_controller`가 자동 주입(`if not issubclass(cls, ControllerBase): cls = type(...)`)하므로 런타임 안전. 헬퍼는 안 쓴다. **트레이드오프**: 명시 상속은 IDE/mypy 지원을 주나 미사용 헬퍼 노이즈가 늘어 **미상속 채택(YAGNI)**. 필요 시 명시 상속 허용.

### 3.5 데코레이터 = `route.*`
`@route.get/post/...`. ninja operation 파라미터 그대로.

### 3.6 명명·배치
- 클래스: `<Aggregate>Controller`(단수), `OrderController`.
- 메서드: 동사구 — `create_order`.
- **파일: `<aggregate>_controller.py`(예 `order_controller.py`)** — houserules "파일명=주 클래스명 snake_case" 정합(기존 `api_<resource>.py`에서 변경).
- houserules §4 명명에 **`Controller` presentation 역할 접미사 신설**.

### 3.7 415/406 = C 정책 + 외부공개 격리
- **기본 내부 전용** → 415/406 기본 비적용 + reviewer 약한 권고. 415 비적용 스코프에서 reviewer는 415 부재를 지적하지 않는다.
- **외부 공개 분류 = design-architect가 G단계에서 명시 기록.** 침묵 시 기본 내부전용(격리 안 함) — DR-31식 음성경계로 박제(매번 묻지 않음).
- 외부 공개로 415가 필요한 표면만 **함수형 `Router`로 격리**(클래스 강제의 명시적 예외). 그 Router에 §6.3 `add_decorator(mode="view")` 유지.
- 각주: 컨트롤러 permission 훅으로 content-type 거부는 *가능하나 403*이며 §3.1 최소사용 위배라 비채택 — 415가 정말 필요하면 함수형 Router 격리가 유일하게 깔끔.
- 약화 범주는 협상(415/406) 한정. 멱등성·problem+json·인증·BC 격리는 유지.

### 3.8 등록 위치 = 단일 인스턴스 · BC 로컬 등록
- **`config`가 단일 `NinjaExtraAPI` 인스턴스를 소유**(`@api.exception_handler`·NJ-7 catch-all이 이 한 인스턴스에 등록 → 중앙 변환점 보존).
- 각 앱의 `<app>_api_router.py`가 **그 `api`를 import해 `api.register_controllers(<Aggregate>Controller)`** 호출(BC 로컬 등록). 415 격리 함수형 Router도 같은 `api`에 `api.add_router(...)`.
- 이 import는 **presentation/wiring 계층의 config 참조**이지 domain/application 계층이 아니므로 BC 격리 불변(OHS bridge=도메인 공개계약 허브 금지와 *다른 축*).
- **BC별 인스턴스 분열은 기각** — catch-all·중앙 핸들러가 쪼개져 NJ-7/§6.2가 깨진다.

---

## 4. 레시피 (before / after)

**BEFORE (함수형)**
```python
# presentation_layer/api/order/api_order.py
router = Router()

@router.post("/orders", response={201: OrderOut, 409: ErrorOut}, tags=["orders"])
def create_order(request, payload: OrderIn) -> Status[OrderOut]:
    order = place_order_command.execute(...)
    return Status(201, OrderOut(...))
```

**AFTER (클래스 컨트롤러)**
```python
# presentation_layer/api/order/order_controller.py   ← 파일명 = 클래스명 snake_case
from ninja import Status                              # Status·Schema는 ninja 소관
from ninja_extra import api_controller, route

@api_controller("/orders", tags=["orders"])
class OrderController:                       # ControllerBase 미상속(자동 주입)
    @route.post("", response={201: OrderOut, 409: ErrorOut})
    def create_order(self, request, payload: OrderIn) -> Status[OrderOut]:
        order = place_order_command.execute(...)
        return Status(201, OrderOut(...))
```

**등록(BC 로컬, 단일 인스턴스) + §6.2 예외 중앙화(보존)**
```python
# config/api.py — 단일 NinjaExtraAPI 소유, INSTALLED_APPS += ['ninja_extra']
api = NinjaExtraAPI()

@api.exception_handler(ProductNotFound)     # 순수 ninja와 동일하게 동작
def on_product_not_found(request, exc):
    return problem(404, ...)

# <app>_api_router.py — config.api를 import해 BC 로컬 등록
from config.api import api
api.register_controllers(OrderController)
# (외부공개 415 격리 시) api.add_router(public_router)   ← 같은 api 인스턴스, 별도 NinjaAPI() 금지
```

**테스트**
```python
from ninja_extra.testing import TestClient
client = TestClient(OrderController)        # 함수형 TestClient(router) 불가
```

---

## 5. 보존 / 변경 매트릭스

| 바뀜 | 그대로 (보존) |
|---|---|
| `router = Router()` → `@api_controller(...)` 클래스 | `response={...}` 선언·`Status` 반환 |
| `@router.post` 함수 → `@route.post` 메서드(+`self`) | `OrderIn`/`OrderOut`/`ErrorOut` 스키마 |
| 파일 `api_<resource>.py` → `<aggregate>_controller.py` | 도메인 예외 `raise` → 중앙 핸들러(§6.2) |
| 등록 `register_controllers`(BC 로컬·단일 api)·`NinjaExtraAPI` | operation 얇음(NJ-2)·command/query 호출 |
| TestClient: `ninja_extra.testing` | NJ-7 catch-all 집행·인증·problem+json |

---

## 6. 탐색 → 포함/생성 (결정적 규칙)

새 operation 추가 시:
1. 해당 앱 `presentation_layer/api/`에서 **`@api_controller` 데코 클래스를 grep**.
2. **단일 컨트롤러** → 거기 메서드로 포함.
3. **분할(여럿)** → **리소스(URL prefix) 일치** 컨트롤러에 포함, 없으면 새 리소스 컨트롤러.
4. **컨트롤러 없음** → 새 `<Aggregate>Controller` 생성.

(침묵 빈틈 즉흥 판단 금지 — P4③ 회피.)

---

## 7. 반영 범위 (양 런타임 미러)

> 미러 단위 표기: 각 스킬 = **정본**(`workspace/reference/.../reference/final.md`) + **Claude**(`dddjango/skills/.../references/final.md` + `SKILL.md`) + **Codex**(`codex-dddjango/skills/.../references/final.md` + `SKILL.md`). = final.md 3사본 + SKILL.md 2벌.

### 표준 스킬
| 스킬 | 변경 |
|---|---|
| `implementation-django-ninja`(3+2) | **클래스 컨트롤러 레시피 절 신설**(함수형은 레거시 위계)·§6.2 `NinjaExtraAPI`·**§6.3 415 함수형/클래스 분기**(`:466` "협상 소유" 문장에 컨트롤러 격리 단서)·§2.1 설치(`ninja_extra`+`INSTALLED_APPS`+핀)·§9.1 컨트롤러 TestClient |
| `discipline-houserules`(3+2) | §4 **`Controller` 접미사** + **파일명 `<aggregate>_controller.py`** + 트리/표(`:104,:212`) "Router"→"Router/`@api_controller`" + `<app>_api_router.py`(`:68,:216`) "config.api import + register_controllers"로 갱신 + **SKILL.md 2벌 명명 bullet(`:35-36`/`:34-35`)에 `Controller` 동기** + carve-out 예시(`:76`/`:75`)에 `NinjaExtraAPI()` + **버전-핀 정본 위치 확정**(깨진 `§6.2` 앵커 복구: houserules 신설 또는 ninja §2.1 흡수 후 참조 정정 — 구현 계획서 택일) |
| `implementation-test`(3+2) | **§19(19.1~19.3)** TestClient 6곳을 `ninja_extra.testing.TestClient(Controller)`로 갱신(SKILL.md는 §19 포인터라 갱신 불요, Codex `final.md`는 대상) |
| `architecture-api` | **무변경**(415 의미만·강제 안 함·프레임워크 비종속) |
| `architecture-ddd`·`implementation-django(-web)` | **무영향 확인됨**(함수형 operation 예시 0, grep 전수) — 주석 박제 |

### 에이전트 (양판)
- `design-architect`: 컨트롤러=애그리거트 생산자 규칙 + "함수형 잔존 금지(touched)" + 415 외부공개 분류 명시 기록 + "operation/Router" 표현이 컨트롤러 포괄
- `discipline-reviewer`: "operation 본문"에 `@route.*` 메서드 포함 1회 정의 + 레드플래그 `@router.*/@api.*` 열거 교체 + **"무조건 클래스" 렌즈 신설**(술어=**touched 표면 함수형 잔존=important(1차 reviewer) / untouched=면제**, DR-21 강등 방지·결정적 차단은 3차 백스톱) + 415 비적용 시 415-부재 비지적 + `:41` "우회 방어불가"를 컨트롤러 분기 보정(컨트롤러는 add_decorator 부재이나 `payload: Schema` 바인딩 강제·raw json.loads는 여전히 blocker) + "presentation에 `NinjaAPI()` 2개 이상" 레드플래그
- `design-review-api`: 컨트롤러 prefix 합성·`register_controllers` 인지(신규 추가, 경량)
- `acceptance-tester`: 최종 URL = prefix 합성 + 컨트롤러 TestClient + operationId 규칙차 인지
- `coder`: implementation-django-ninja 클래스 레시피 참조

### 백스톱·게이트 (양판 byte-identical)
- **1차 회귀 봉합(즉시) — 대상 3종**: `check-response-schema-bypass.py`·`check-openapi-error-declaration.py`·**`check-error-centralization.py`**의 `NINJA_IMPORT_RE`를 **정확히** `r"^\s*(?:from\s+ninja(?:_extra)?(?:\.\w+)*\s+import|import\s+ninja(?:_extra)?)\b"`로 교체(과매치 0·FN 0 실측 확인). 양판 6파일 + 패치 후 `cmp` 재검증. `workspace/eval/tools/check-structure.py:251` NJ-1 토큰에 `NinjaExtraAPI`/`api_controller` 추가(미러 없음, 단일본).
- **무영향 확인됨(실측)**: `check-catch-all-handler`·`check-transient-overmapping`·`check-synthetic-infra-exc`·`check-idempotency-scope-creep`·`check-anemic-sql-guard` — 클래스 픽스처에서 정상 exit2(레이어/인스턴스 기준). `check-response-schema-bypass`·`check-openapi-error-declaration` 탐지 *로직*은 `@route.post(response=...)` 메서드에 정상 발화(import 게이트만 결함).
- **3차 신설(라이브 N≥2 후)**: "무조건 클래스" 백스톱 — 신호를 **"신규/추가된 presentation 파일이 함수형 operation 정의 AND 같은 디렉토리 컨트롤러 부재"**(부재+신규 신호, 추가-라인 기준)로 좁힌다. 거짓음성(같은 앱 미끼 컨트롤러)·거짓양성(grandfather 무관 편집)은 **구조적 한계 → reviewer 렌즈와 2중화**(§9·§8).
- `commands/dddjango.md`·`codex .../SKILL.md`: 스크립트 설명문 함수형 예시를 클래스 포함으로 정합(배선 무변경).

### 평가지 (차원 신설 0 · 측정 항목 수 불변)
| 항목 | 변경 |
|---|---|
| **NJ-1 판정기준 개정** | RUBRIC `:55` + EVAL-METHOD `:66` 결정 레인 술어 `NinjaAPI`+`Router` → `NinjaAPI`/`NinjaExtraAPI` + (`Router` ∨ `@api_controller`/`register_controllers`). **DR-47식 명시 동결-해제 항목으로 기록**(기준 변경이므로·차원 수 불변이어도) |
| NJ-2·SD-6·NJ-7 | "operation"에 "컨트롤러 메서드 포함" 1회 정의 |
| Q-1 앵커(`:143`) | 415/406을 C 정책으로 재서술(앵커=freeze 밖, 재서술 정당) |
| NJ-1/2/5 앵커 | 클래스 메서드 형태(`self`) 병기 또는 단서 |
| §4.3.1 EP 매트릭스 | **무변경**(415 EP 항목 부재 → C 정책 무충돌, 명기만) |

> 동결: **차원 신설 0**·측정 항목 수 불변(현 33+NJ-7=34). **단 NJ-1은 *판정기준* 변경이므로 DR-47식 명시 동결-해제 항목으로 기록**(앵커 재서술과 구분 — 앵커는 freeze 밖). RUBRIC 헤더는 아직 "동결됨" 미선언이라 개정 가능하나, 사일런트 드리프트 금지(EVAL-METHOD 기준 사전등록).

### 의존성
`django-ninja-extra` 설치 + `INSTALLED_APPS += ['ninja_extra']` + 핀(ninja-extra↔ninja 호환은 설치 해석기에 위임). plugin.json(양판) minor 업.

---

## 8. 집행 전략 — (a) 단계적

0. **회귀 봉합(즉시)**: 백스톱 3종 import 게이트 `ninja_extra` 확장(정확한 정규식·양판 6파일) + check-structure 토큰 — *변경이 유발하는* 거짓음성 차단.
1. **1차**: 표준 텍스트 + discipline-reviewer 렌즈(important·touched 술어; 결정적 차단은 3차 백스톱).
2. **2차**: 라이브 dual `/dddjango` — 클래스 생성·reviewer 집행력 + 기존 백스톱 16종 회귀 매트릭스(DR-29식).
3. **3차**: 라이브 결과로 "무조건 클래스" 백스톱(부재+신규 신호) 설계·신설. reviewer와 2중화(백스톱 단독으론 거짓음성 못 닫음).

> DR-21/22: 텍스트·reviewer만으론 약함. (a)는 라이브로 정밀 설계하는 순서. 단 0차 회귀 봉합은 즉시.

---

## 9. 리스크 · 미해결

- **신뢰성**: ninja-extra 1인·0.x. 수용(표면 최소화).
- **신설 백스톱 정밀도 한계**: 부재 신호는 (i)같은 앱 미끼 컨트롤러 존재 시 게으른 함수형 **거짓음성** (ii)grandfather 파일 무관 편집 시 **거짓양성** — 백스톱 단독으론 못 닫고 **reviewer 렌즈와 2중화** 필수. 추가-라인/신규-파일 기준으로 완화하되 저-recall 명시.
- **NinjaExtraAPI 기본 핸들러 ↔ NJ-7 catch-all 우선순위**: NinjaExtraAPI가 `exceptions.APIException` 핸들러를 자체 등록(§3.1이 ninja-extra 예외 *사용*은 배제하나 기본 핸들러는 자동) → 우리 catch-all과 MRO/등록순 충돌 가능, 라이브 확인.
- **OpenAPI operationId 변경**(`use_unique_op_id=True`): operationId 규칙이 함수형과 달라 계약 diff·NJ-5 영향. **`use_unique_op_id=False` 옵션이 함수형↔클래스 안정성에 유리한지 라이브 비교 후 결정**.
- **마이그레이션**: greenfield(ninja-extra 흔적 0). 신규/touched만 적용, untouched 함수형 grandfather.
- **함수형/클래스 공존**(415 격리·grandfather): 등록 순서·URL 충돌·성능 라이브 N≥2 전 미보증.
- **버전 핀**: 저장소에 고정 ninja 핀 부재(설치시점 resolve) — "충돌" 대상 없음. 설치 해석기에 위임.
- **라이브 미검증·N=1**: 효과·우열 결론 금지.

---

## 10. 다음 단계

구현 계획(writing-plans) → 0차 회귀 봉합 → 1차(표준+reviewer) → 라이브 → 3차 백스톱.
