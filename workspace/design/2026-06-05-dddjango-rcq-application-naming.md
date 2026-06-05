# R/C/Q 응용 계층 명명 — Request / Command / Query 인터랙터 (DR-43) · v2

## 상태
설계 확정(D1–D5) + **적대 리뷰 4렌즈 반영(v2)**. 전 렌즈 FIX-THEN-SHIP(NO-GO 0). 구현 전 사용자 승인 대기. 표준 편집·커밋 금지. 미러: references = claude↔codex **byte-identical**(검증됨), 에이전트 = **의미-동등**(byte 아님, 아래 §5).

## v1 → v2 (적대 리뷰가 고친 것)
- **B1(렌즈2)**: 에이전트는 byte-identical 미러가 **아님**(diff 검증: frontmatter·`Coordinator`/`코디네이터`·codex 헤더+지식스킬 절·+1 오프셋). §5를 "의미-동등 미러"로 정정, body-diff 게이트 삭제, 삽입 앵커 명시.
- **B2(렌즈1·2·3)**: selector "함수" 사이트가 변경 목록 밖에 실재 — ninja `:260/:285`·impl-django HackSoft `:1432/:1450`. D1 스코프를 "application_layer 유스케이스 읽기"로 명확화하고, ninja read 예제는 Query로 갱신, HackSoft selectors는 *참조 관용*으로 경계 노트. "selector 잔존0" 게이트를 houserules application_layer로 한정.
- **B3(렌즈1)**: Command=메시지 어휘가 §3.6 넘어 다수(`:1603` domain `commands.py`·`:1609` `services.py`=유스케이스·렌즈1 보고 §428 Event Storming·§1789 애그리거트 메서드). 어휘 노트를 *열거+경계*로 확장.
- **B4(렌즈3)**: §3 ninja 예제가 미정의 `order_repository`/`stock_port`(정의 0건 검증) → 실행불가 + presentation→infra 직접조립 조장. placeholder 금지문 + reviewer 레드플래그.
- **B5(렌즈4)**: ⑫가 평문 `…Command`/`…Query` 클래스상수에 발화(면제 로직 검증). 연산 클래스 상수 어노테이트(=§4 정합) 노트 + Request=@dataclass + 게이트는 *생성 코드* 프로브.
- **중간**: execute 반환 계약·생성자 arity 규칙·RUBRIC SH-3 오타깃 정정·소급채점 versioning·§5.4 경계 포인터·§20.5 산문 2곳·trivial 비용 정직 고지·§3.6 포인터 채택.

## 배경 — 왜
DR-41이 헥사고날 포트/어댑터는 정합했으나 `command/dto/query` 거주객체 어긋남을 백로그로 남김. 현재 "쓰기 응용 유스케이스"가 **3곳에서 다름**: houserules `final.md:187` `class PlaceOrderService` / `implementation-test:2619` `ReserveStockApp`(`App`=`:238` `_app` 폐기 위반) / `implementation-django-ninja:151` `place_order(...)` 자유함수. R/C/Q가 인터랙터 연산 객체로 통일.

## 결정 (locked)
- **D1 = Way 2 (인터랙터)** — 쓰기 `…Command`·읽기 `…Query`(클래스, repository 의존, `execute(request)`). **스코프 = `application_layer` 유스케이스 읽기/쓰기.** presentation read 엔드포인트는 이 Query를 호출한다. 근거: 사용자 통일성 최우선. **비용(정직 고지)**: trivial 단건 조회도 `…Query` 클래스 + `…Request` + repository를 강제 → 보일러플레이트. DR-39 §4.1 선례대로 "실익은 버그예방이 아니라 *결정성·일관성*(런간 '함수냐 클래스냐' 비결정 제거, P4③ 회피)"임을 표준이 정직하게 명시. trivial 탈출구는 두지 않는다(혼재 → reviewer 판정부담 → 비결정 재유입).
- **D2 = (c) 하이브리드 + 어휘 노트 확장** — 코퍼스 Command=메시지 어휘(§3.6 입력 DTO·§428 Event Storming·§1603 domain `commands.py`·§1789 애그리거트 커맨드 메서드)와 `services.py`=유스케이스(§1609)는 **이론/모델링 어휘라 보존**. houserules 어휘 노트가 *열거+경계*로 봉합. 우리 소유 예제(implementation-test §20.5·ninja)는 R/C/Q로 재작성. `architecture-ddd §3.6` 충돌 코드 옆 포인터 **채택**(이름 충돌 `PlaceOrderCommand` 정반대 의미라 노트만으론 부족).
- **D3 = service/ 유지** — `…Service`(여러 Command/Query 오케스트레이션)는 폴더=클래스 일치. 단 코퍼스 `services.py`=*단일 유스케이스 파사드*와 어휘가 갈리므로 노트에 매핑 1줄.
- **D4 = defer(단 예제 함정 차단)** — 컴포지션 루트(인프라 주입)는 *배선* 축이라 별도 DR. **그러나 §3 예제는 실행 코드라** placeholder를 금지문으로 박고 reviewer 레드플래그로 "operation 본문 `Django…()` 직접 생성" 차단.
- **D5 = Request 의무(@dataclass)** — operation은 `…Request` 입력, presentation이 ninja `…In`→`…Request` 빌드(경계 번역 자리). `…Request`는 **`@dataclass`**(또는 pydantic)로 — ⑫ 면제 + 어노테이션 관용.

## 매핑
| 슬롯 | 현재 (HEAD=DR-42) | 타깃 (R/C/Q) |
|---|---|---|
| `command/` | `_service.py` → `class PlaceOrderService` | `_command.py` → `class PlaceOrderCommand` · `execute(request)` · domain repository/port 의존 |
| `query/` | `_query.py` → `def list_orders(...)` 함수 | `_query.py` → `class ListOrdersQuery` · `execute(request)` · repository 의존 |
| `dto/` | `_command.py` → `class PlaceOrderCommand`(입력) | `_request.py` → `@dataclass class PlaceOrderRequest`(입력) |
| `service/` | `_service.py` → `class CheckoutService` | **불변** (노트에 코퍼스 `services.py` 매핑) |
| `handler/` | `class OrderPlacedHandler` | **불변** |

**연산 객체 계약(통일)**: 생성자는 **도메인 repository·port 인터페이스를 유스케이스 의존만큼 주입**받는다(arity 가변은 규칙). `execute(request)`는 **도메인 결과(애그리거트 또는 식별자)**를 반환하고 HTTP/표현 타입을 반환하지 않는다(§3.6 대칭). CAS 재시도의 outcome(`.success`) 형태는 특수 케이스로 일반 규칙과 구분 표기.

---

## 구체 변경 (from → to)

### 1. `discipline-houserules/references/final.md` [양본 byte-identical]

**트리 주석(`:85`–`:87`)**
```
- command/ #   쓰기 유스케이스(응용 서비스): <usecase>_service.py — domain repository 인터페이스 의존
+ command/ #   쓰기 유스케이스 연산: <usecase>_command.py → class …Command.execute(request) — domain repository/port 의존
- query/   #   조회: <usecase>_query.py — selector 함수/QuerySet (CQRS는 필요 컨텍스트만, §5.4)
+ query/   #   조회 유스케이스 연산: <usecase>_query.py → class …Query.execute(request) — repository 의존 (별도 읽기모델 CQRS는 §5.4 선택)
- dto/     #   입력 DTO(command 객체): <usecase>_command.py
+ dto/     #   유스케이스 입력 DTO: <usecase>_request.py → @dataclass class …Request
```

**명명 표(`:187`–`:189`)**
```
- | command/ | 쓰기 유스케이스 … | `<usecase>_service.py` → `class PlaceOrderService` | 코어 |
+ | command/ | 쓰기 유스케이스 **연산** — 도메인 위임, repository/port 의존(DIP) | `<usecase>_command.py` → `class PlaceOrderCommand`(`execute(request)`) | 코어 |
- | query/ | 조회 — selector/QuerySet | `<usecase>_query.py` → `def list_orders(...)` selector 함수 | CQRS 적용 시; 아니면 command와 합쳐도 됨 |
+ | query/ | 조회 유스케이스 **연산** — repository 의존 | `<usecase>_query.py` → `class ListOrdersQuery`(`execute(request)`) | 코어 (별도 읽기모델 CQRS는 §5.4 선택) |
- | dto/ | 유스케이스 **입력** command 객체(DTO) | `<usecase>_command.py` → `class PlaceOrderCommand` … | 입력 검증 있으면 코어 |
+ | dto/ | 유스케이스 **입력** 요청 객체(DTO) | `<usecase>_request.py` → `@dataclass class PlaceOrderRequest` ※응답 DTO 아님 | 코어 |
```

**어휘 노트(NEW — 표 머리 직전). 확장판:**
```
> **어휘(인터랙터 채택)** — 이 표준의 *생성 코드*는 유스케이스를 연산 객체로 표현한다:
> 입력 `…Request`, 쓰기 `…Command`, 읽기 `…Query`, 모두 `execute(request)`.
> ⚠️ 코퍼스는 `…Command`/`…Query`를 **다른 의미로 쓴다 — 이는 이론/모델링 어휘라 보존**한다:
>   · `architecture-ddd §3.6:1008` `…Command`=응용 서비스 *입력 DTO*  · §428 Event Storming `Command`=*의도적 행동*
>   · §1603 domain `commands.py`=*도메인 커맨드 정의*  · §1789 애그리거트 *커맨드 메서드*  · §1609 `services.py`=*유스케이스 파사드*
> 경계: **생성 코드 어휘 권위는 이 문서**(§6.1 위임). 도메인/Event Storming *모델링* 어휘는 코퍼스가 권위.
> 이 표준 `service/`=여러 유스케이스 *오케스트레이션*(코퍼스 `services.py`=단일 유스케이스 파사드와 구분).
> HackSoft `selectors.py`/`services.py`(`implementation-django §16`)는 *평면 함수 관용*의 참조이고, 이 표준은
> 그것을 `application_layer/{command,query}` 인터랙터로 **구체화**한다.
```

**프로즈(`:121`–`:122`)**
```
+ 유스케이스는 연산 객체(쓰기 `…Command`·읽기 `…Query`)로 표현하고 입력은 `…Request` DTO로 받아 `execute(request)`로 실행한다. command/query 연산은 구체 리포지토리를 직접 생성하지 말고 domain repository/port 인터페이스에 의존·주입(DIP).
+ **읽기는 `…Query` 연산으로 통일하되, *별도 읽기 모델*(CQRS)은 선택적**(§5.4): 모든 읽기는 `…Query` 인터랙터(통일성·결정성)지만, 읽기 전용 *모델/프로젝션* 분리는 강제 안 함 — 공유 모델을 repository로 읽으면 충분, 읽기/쓰기 모델이 실제로 갈릴 때만 분리. (trivial 단건 조회도 `…Query`인 보일러플레이트 비용은 통일성·런간 결정성을 위해 수용 — 실익은 버그예방이 아니라 일관성이다.)
```

**파일명 규칙(`:238`, `:242`)**
```
+ **유스케이스 연산 명명** — 쓰기 `<usecase>_command.py`→`class …Command`, 읽기 `<usecase>_query.py`→`class …Query`, 입력 `<usecase>_request.py`→`@dataclass class …Request`. 모두 `execute(request)`·repository/port 의존. (`_app`·`_service` 안 씀; `_service.py`는 오케스트레이션 `service/`에만.)
+ **조회(읽기)**: `…_query.py`→`class …Query`(인터랙터 — `execute(request)`, repository 의존). 별도 읽기 *모델*(CQRS §5.4)은 선택.
```

### 2. `implementation-test/references/final.md` [양본] — §20.5
`:2618`–`:2621`:
```python
-    app = ReserveStockApp(ConflictOnceRepository())
-    result = app.execute(ReserveStockCommand(product_id=product.id, quantity=2))
+    reserve_stock = ReserveStockCommand(ConflictOnceRepository())          # 쓰기 연산 객체
+    result = reserve_stock.execute(ReserveStockRequest(product_id=product.id, quantity=2))
```
+ 산문 "응용 서비스" → "쓰기 연산(`…Command`)" **§20.5 전 범위**: **`:2597`·`:2627` 둘 다**(B5 검증: grep 2곳). `App` stale 동시 해소.

### 3. `implementation-django-ninja/references/final.md` [양본]
**쓰기(`:150`–`:151`)** — 미정의 이름 금지문:
```python
 def create_order(request: HttpRequest, payload: OrderIn) -> Status[OrderOut]:
-    order = place_order(product_id=payload.product_id, quantity=payload.quantity)  # service 호출
+    # place_order_command 는 컴포지션 루트가 주입(D4 별도). ⚠️ operation 본문에서 `Django…Repository()`/`…Adapter()`를 직접 생성하지 말 것 — presentation→infra 직접 결합(Q-7) 금지.
+    order = place_order_command.execute(PlaceOrderRequest(product_id=payload.product_id, quantity=payload.quantity))
```
**읽기(`:260`–`:261`, `:285`–`:286`)** — selector→Query 인터랙터:
```python
- def list_orders(request, filters: Query[OrderFilter]):
-     return select_orders(filters=filters)
+ def list_orders(request, filters: Query[OrderFilter]):
+     return list_orders_query.execute(ListOrdersRequest(filters=filters))   # 읽기 연산 객체(배선=D4)
```
(둘째 사이트도 동형. `list_orders_query`도 컴포지션 루트 주입.)

### 4. `architecture-ddd/references/final.md` [양본] — §3.6 (`:1009`) **채택**
이론 코드 불변. docstring 옆 1줄(이름 충돌 봉합 — 양본 동일 삽입):
```
+ # ※ 이 메시지-어휘(…Command=입력 DTO)는 CQRS 이론 *교육*이다. 이 플러그인 *생성 코드*는 입력을 …Request로, 쓰기 *실행*을 …Command 인터랙터로 명명한다(houserules 권위). 두 어휘를 섞지 말 것.
```

### 5. 에이전트 [양본 **의미-동등** — byte-identical 아님]
**미러 모델 정정**: 각 런타임 컨벤션을 따른다 — claude `Coordinator`/`Read·Grep·Glob`, codex `코디네이터`/`spawn_agent`/네이티브 도구 + codex 헤더·`## 로드할 지식 스킬` 절. 추가 문구는 *의미 동일*, byte 비교 불가.
- **design-architect** (claude `agents/design-architect.md` ↔ codex `skills/dddjango-design-architect/SKILL.md`): §4 명명 블록(`:38`) **끝에** 추가 — "응용 유스케이스는 R/C/Q 인터랙터로 명세 — command/=`…Command`(쓰기)·query/=`…Query`(읽기)·dto/=`@dataclass …Request`(입력), 모두 `execute(request)`·repository/port 의존. `…Command`를 입력 DTO로 쓰지 않는다."
- **discipline-reviewer** (claude `:41` ↔ codex `:42`, +1 오프셋): 구조 레드플래그 블록 **끝 불릿**으로 추가 — "command/에 `…Service`/자유함수 · query/에 selector 함수(`…Query` 클래스 기대) · dto/가 `…Command`(입력=`…Request`) · 연산이 `execute(request)` 아님 · **operation 본문이 `Django…Repository()`/`…Adapter()`를 직접 생성**(presentation→infra)."
- 삽입 앵커를 양본에 동일 위치로 박아 의미-동등 유지.

### 6. `discipline-houserules/SKILL.md` [양본, `user-invocable` 줄차 유의] — 명명 요약 1줄
"응용 유스케이스 R/C/Q: command/=`…Command`·query/=`…Query`·dto/=`@dataclass …Request`, `execute(request)`."

### 7. `RUBRIC.md` + `rubric-metrix.md` [단일] — **SH-3 확장 반영 (2026-06-05 후속 보정)**
~~원안: SH-3 주입 금지~~ — RUBRIC 응용명명 참조 0건·차원 동결(`:3`,`:151`)이라 SH-3 본문 불변·reviewer 위임이었음. **번복 사유**: 평가지에 채점 앵커가 없으면 다음 라이브런에서 R/C/Q 검증 불가(grader가 적을 칸 없음)·백스톱 보류 로직의 드리프트 증거도 수집 불가. **소급 위반 우려는 §7b 시점 규칙이 이미 해소** → '불변'은 과보수. **반영**: `SH-3`을 "종류 폴더+거주 명명"으로 확장(RUBRIC.md:37 + rubric-metrix.md:42) — command/=`…Command`·query/=`…Query`·dto/=`@dataclass …Request`, FAIL=command/`…Service`·selector 함수·비-`@dataclass`, §근거 `§0-3·§0-4·§4`, 레인 `결정(폴더)+의미(명명)`, 비치명, 시점 `≥1.4.0`. 새 SH 코드 0=차원 동결 유지. discipline-reviewer 레드플래그(§5)는 생성측 예방으로 병존.

### 7b. 평가 연속성 [단일] — `EVAL-METHOD.md`
"fixture 채점은 **그 산출 시점 표준 버전 기준**; 1.4.0 이전 산출분에 R/C/Q 소급 FAIL 금지" 1줄(현재 방법론에 시점 고정 규칙 부재 — `EVAL-METHOD.md:74` 런 diff 정의뿐). 소급 위험 fixture 예: `nj2live-codex`·`fklive-codex`(`…App`+`…Command`=입력 DTO)·`pytestlive-codex`(`PlaceOrderService`=도메인 서비스).

### 8. `plugin.json` [양본] — 1.3.0 → **1.4.0** (minor; 선례 DR-41=1.2.0·DR-42=1.3.0 생성규약 변경=minor와 일관). codex 경로 `codex-dddjango/.codex-plugin/plugin.json`.

### 9. workspace [단일] — DEVLOG DR-43 · 이 spec · DR-41 backlog 해소.

---

## ⑫(공개표면 어노테이션) 상호작용 — 명시
`check-public-surface-annotation.py`는 `@dataclass`/선언적 base/`Meta·Config`만 면제(검증: `:59-69`,`:113-121`). 따라서:
- `@dataclass class …Request` → **면제(안전)**. D5가 `@dataclass` 의무화하므로 거짓양성 0.
- 평문 `class …Command`/`…Query`의 **클래스상수 bare 리터럴**(`MAX_RETRIES = 3`) → **⑫ 발화**(정상 — `name: T = literal`로 어노테이트하면 통과 = §4 공개표면 규칙 정합, 회귀 아님). 예제는 연산 클래스에 bare 상수를 두지 말거나 어노테이트.
- 백스톱 **무변경**(보류 유지) — N=0 live, 프로젝트 일관(DR-32/37/39: 관측된 라이브 실패만 결정적 집행), §120 라이브 N≥2 트리거.

## 적대 리뷰 표적 (잔여 — v3 리뷰 시)
1. D1 스코프 명확화(application_layer 한정) 후에도 ninja read 예제↔HackSoft selectors 경계가 깔끔한가?
2. 연산 객체 생성자 arity 가변 규칙 + execute 반환 계약이 coder 비결정을 충분히 줄이나?
3. 어휘 노트 확장판이 Command 4중 의미를 실제로 봉합하나?

## 검증 게이트 (구현 시)
- **references diff**: houserules·implementation-test·implementation-django-ninja·architecture-ddd 4종 양본 **diff 0**(byte-identical 확인됨).
- **에이전트**: byte-diff **검사 안 함**(의미-동등). 대신 추가 레드플래그/지시가 양본에 의미상 존재하는지 수동 확인.
- **자기모순 grep(스코프 한정)**: houserules application_layer 문맥의 `_service.py`/`PlaceOrderService` 잔존 0 · houserules `query/`의 selector "함수" 명문 잔존 0(impl-django HackSoft `selectors.py`는 *참조 관용*이라 제외) · `dto/`+`_command.py` 잔존 0. **architecture-ddd §3.6 `PlaceOrderCommand`(D2 보존)는 grep 예외**.
- **§20.5 산문**: "응용 서비스" 잔존 0(§20.5 본문 한정).
- **⑫ 프로브**: 임시 git 디렉터리에 R/C/Q 예제 `.py`를 add 후 ⑫ 실행 → 어노테이트된 형태가 exit0 확인(플러그인 레포 재실행만으론 생성코드를 못 봄).
- **백스톱 13종**: 플러그인 레포 무변경 재실행 exit0.

## 정본
이 spec(v2) · 적대 4렌즈 리포트(a9e6b1·adcdeb·a522f3·a71ee2) · DEVLOG DR-43 · 커밋·push는 사용자 명시 승인 시만.
