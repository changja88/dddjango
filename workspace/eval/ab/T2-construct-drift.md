# T2 construct drift 리포트 — 대표 8종 구판(이행 직전) ↔ 신판 stdout (D11·T9)

> 생성: `python3 workspace/tools/construct_drift_report.py --emit-report`(수기 편집 금지 — 재생성으로만 갱신).
> 구판 = 검사기별 «이행 직전» 봉인 커밋(아래 표)·신판 = 생성 시점 워킹트리. 기본 red 레인 한정
> (위험 레인 diff 는 각 이행 커밋 메시지가 소유). 의도 변경 열거표(포매터 계약 v2 §2)의 기계 실측 대응물.

## 이관 고지 — 설치본 빚 목록(--legacy-debt-file)

debt 매칭은 `[#N]` 태그 + 부분문자열이다(`anchor_diff.debt_match`). B형 콜론 정형화로
`…:{lineno} {msg}` → `…:{lineno}: {msg}` 가 된 라인에 대해, **부분문자열이 lineno-msg 경계를
가로지르는 빚 엔트리만** 매치가 깨진다(msg 내부·경로 내부 부분문자열은 무사). 설치본
프로젝트의 빚 파일은 해당 엔트리에 콜론을 삽입해 개정한다. 저장소 내 실물 빚 파일 0건·
테스트 자산(스모크 합성 빚)은 신판 기준 상시 green(2026-08-20 실측).

## 검사기별 diff

### check-api-error-controller-contract.py — 구판 `77691d8` (exit 2→2)

변경 12행:

```diff
--- check-api-error-controller-contract.py@77691d8
+++ check-api-error-controller-contract.py@신판
@@ -6,5 +6,5 @@
-  [#126] application/orders/driving_layer/api/order/order_controller.py:31 handler 등록 decorator — 도메인 예외→ErrorSchema 매핑은 컨트롤러 메서드 «안»에 직접 쓴다(helper·factory·global mapper 금지)
-  [#124] application/orders/driving_layer/api/order/order_controller.py:10 `get_or_touch()` 에 라우트 데코가 2개 — 요청 하나당 메서드 하나다
-  [#474] application/orders/driving_layer/api/order/order_controller.py:25 도메인 예외를 `as e` 로 묶어 참조했다 — 입구 파일은 도메인 예외를 «타입»으로만 쓴다
-  [#62] application/orders/driving_layer/api/order/order_controller.py:26 `except Exception`/bare — 폴백은 도메인·응용 base 단위 catch 로 한정한다(base 는 상한이다 — code-json managed controller 는 concrete/구체 tuple 만 catch 한다: ninja §6.2)
-  [#132] application/orders/driving_layer/api/order/routes.py:7 라우트 데코레이터가 컨트롤러 파일 밖에 있다 — 라우트·인증·상태 코드는 `<area>_controller.py` 에 온다
+  [#126] application/orders/driving_layer/api/order/order_controller.py:31: handler 등록 decorator — 도메인 예외→ErrorSchema 매핑은 컨트롤러 메서드 «안»에 직접 쓴다(helper·factory·global mapper 금지)
+  [#124] application/orders/driving_layer/api/order/order_controller.py:10: `get_or_touch()` 에 라우트 데코가 2개 — 요청 하나당 메서드 하나다
+  [#474] application/orders/driving_layer/api/order/order_controller.py:25: 도메인 예외를 `as e` 로 묶어 참조했다 — 입구 파일은 도메인 예외를 «타입»으로만 쓴다
+  [#62] application/orders/driving_layer/api/order/order_controller.py:26: `except Exception`/bare — 폴백은 도메인·응용 base 단위 catch 로 한정한다(base 는 상한이다 — code-json managed controller 는 concrete/구체 tuple 만 catch 한다: ninja §6.2)
+  [#132] application/orders/driving_layer/api/order/routes.py:7: 라우트 데코레이터가 컨트롤러 파일 밖에 있다 — 라우트·인증·상태 코드는 `<area>_controller.py` 에 온다
@@ -12 +12 @@
-  [ⓓ#125] application/orders/driving_layer/api/order/order_controller.py:16 라우트 메서드 안 루프 — 물음: 입구가 변환·1회 호출을 넘어 로직을 갖는가(그러면 유스케이스로 내린다)?
+  [ⓓ#125] application/orders/driving_layer/api/order/order_controller.py:16: 라우트 메서드 안 루프 — 물음: 입구가 변환·1회 호출을 넘어 로직을 갖는가(그러면 유스케이스로 내린다)?
```

### check-common-container.py — 구판 `e245b1e` (exit 2→2)

변경 4행:

```diff
--- check-common-container.py@e245b1e
+++ check-common-container.py@신판
@@ -2,2 +2,2 @@
-  [컨테이너] application/framework/  (내용: clock.py)
-  [컨테이너] application/common/  (내용: util.py)
+  - application/framework: 횡단 버킷이 application/ 안에 있다 (내용: clock.py)
+  - application/common: 횡단 버킷이 application/ 안에 있다 (내용: util.py)
```

### check-composition-root.py — 구판 `faea9d3` (exit 2→2)

변경 28행:

```diff
--- check-composition-root.py@faea9d3
+++ check-composition-root.py@신판
@@ -5,4 +5,4 @@
-  [#498] application/orders/composition_root/event_wiring.py:3 event_wiring.py 에서 표(dict)를 만들었다 — 표는 event_subscription/event_router.py 소유, 여기는 브로커에 «꽂는» 것만 한다
-  [#500] application/orders/composition_root/event_wiring.py:8 구독으로 람다를 넘겼다 — 모듈 최상단 이름 있는 함수만(매번 다른 객체라 멱등이 깨진다)
-  [#501] application/orders/composition_root/event_wiring.py:9 event_wiring.py 에서 DB 를 만졌다 — 모든 관리 명령에서 도는 자리다
-  [#101] application/orders/application_layer/order/place_order/place_order_use_case.py:1 `application.orders.driving_layer.api.order.schema.schema_out` — BC 안쪽과 composition_root 은 driving 층을 import 하지 않는다(예외 없음 · rd-2)
+  [#498] application/orders/composition_root/event_wiring.py:3: event_wiring.py 에서 표(dict)를 만들었다 — 표는 event_subscription/event_router.py 소유, 여기는 브로커에 «꽂는» 것만 한다
+  [#500] application/orders/composition_root/event_wiring.py:8: 구독으로 람다를 넘겼다 — 모듈 최상단 이름 있는 함수만(매번 다른 객체라 멱등이 깨진다)
+  [#501] application/orders/composition_root/event_wiring.py:9: event_wiring.py 에서 DB 를 만졌다 — 모든 관리 명령에서 도는 자리다
+  [#101] application/orders/application_layer/order/place_order/place_order_use_case.py:1: `application.orders.driving_layer.api.order.schema.schema_out` — BC 안쪽과 composition_root 은 driving 층을 import 하지 않는다(예외 없음 · rd-2)
@@ -12,8 +12,8 @@
-  [#111] application/orders/driving_layer/api/api_router.py:4 api_router.py 에 등록 밖 정의가 있다 — 컨트롤러 import 와 등록 함수만 둔다
-  [#109] application/orders/driving_layer/api/api_router.py:15 module top-level 등록 호출 — 등록은 `register_<bc>_api(api)` 함수 «안»에서만 한다(부작용 등록 금지)
-  [#108] application/orders/driving_layer/api/api_router.py:1 `config.api` import — 전역 API 객체는 import 하지 않고 인자로 받는다(BC 가 프로젝트를 import 하지 않는다)
-  [#437] config/api.py:2 `application.orders.domain_layer.order.exception.order_not_found` import — `<project>/api.py` 에는 전역 API 객체 하나와 프레임워크 오류 핸들러만 온다(BC import 금지)
-  [#437] config/api.py:7 `ErrorSchema` 정의 — ErrorSchema·예외 목록·매핑은 전부 위반이다(닫힌 허용 목록)
-  [#437] config/api.py:11 `map_order_errors()` — 프레임워크 오류 핸들러 밖의 함수는 이 파일에 오지 않는다
-  [#441] config/urls.py:3 `application.orders.driving_layer.api.order.order_controller.OrderController` import — urls.py 가 BC 심볼을 쓰는 예외는 `register_<bc>_api` 명시 호출 하나뿐이다
-  [#440] config/urls.py:2 `register_orders_api` 을 import 하고 부르지 않았다 — urls.py 는 각 BC 의 `register_<bc>_api(api)` 를 «명시적으로 부른다»
+  [#111] application/orders/driving_layer/api/api_router.py:4: api_router.py 에 등록 밖 정의가 있다 — 컨트롤러 import 와 등록 함수만 둔다
+  [#109] application/orders/driving_layer/api/api_router.py:15: module top-level 등록 호출 — 등록은 `register_<bc>_api(api)` 함수 «안»에서만 한다(부작용 등록 금지)
+  [#108] application/orders/driving_layer/api/api_router.py:1: `config.api` import — 전역 API 객체는 import 하지 않고 인자로 받는다(BC 가 프로젝트를 import 하지 않는다)
+  [#437] config/api.py:2: `application.orders.domain_layer.order.exception.order_not_found` import — `<project>/api.py` 에는 전역 API 객체 하나와 프레임워크 오류 핸들러만 온다(BC import 금지)
+  [#437] config/api.py:7: `ErrorSchema` 정의 — ErrorSchema·예외 목록·매핑은 전부 위반이다(닫힌 허용 목록)
+  [#437] config/api.py:11: `map_order_errors()` — 프레임워크 오류 핸들러 밖의 함수는 이 파일에 오지 않는다
+  [#441] config/urls.py:3: `application.orders.driving_layer.api.order.order_controller.OrderController` import — urls.py 가 BC 심볼을 쓰는 예외는 `register_<bc>_api` 명시 호출 하나뿐이다
+  [#440] config/urls.py:2: `register_orders_api` 을 import 하고 부르지 않았다 — urls.py 는 각 BC 의 `register_<bc>_api(api)` 를 «명시적으로 부른다»
@@ -21,2 +21,2 @@
-  [ⓓ#86] application/orders/composition_root/dependency_wiring.py:5 결선 함수 안 조건문 — 물음: 이 분기는 업무를 가르는가(그렇다면 유스케이스로 내린다)?
-  [ⓓ#511] application/orders/driving_layer/api/oauth/ — 물음: 이 입구의 계약을 바깥이 소유하는가(OAuth 콜백 포함)? 그러면 `webhook/<provider>/` 자리다
+  [ⓓ#86] application/orders/composition_root/dependency_wiring.py:5: 결선 함수 안 조건문 — 물음: 이 분기는 업무를 가르는가(그렇다면 유스케이스로 내린다)?
+  [ⓓ#511] application/orders/driving_layer/api/oauth/: 외부 소유 계약 입구 후보(provider 성 디렉터리) — 물음: 이 입구의 계약을 바깥이 소유하는가(OAuth 콜백 포함)? 그러면 `webhook/<provider>/` 자리다
```

### check-context-isolation.py — 구판 `36bd09c` (exit 2→2)

stdout **byte 무변**.

### check-domain-model.py — 구판 `f164dd9` (exit 2→2)

stdout **byte 무변**.

### check-error-centralization.py — 구판 `1e887e3` (exit 2→2)

stdout **byte 무변**.

### check-openapi-error-declaration.py — 구판 `ee62c5c` (exit 2→2)

변경 6행:

```diff
--- check-openapi-error-declaration.py@ee62c5c
+++ check-openapi-error-declaration.py@신판
@@ -2,3 +2,3 @@
-  [#63] application/orders/driving_layer/api/order/order_controller.py:15 `openapi_extra` 의 responses 보충 — 오류 응답은 `response={status: <Bc>ErrorSchema}` 로 직접 선언한다
-  [#63] application/orders/driving_layer/api/order/order_controller.py:19 `get_openapi_schema` override — 오류 응답은 operation 의 `response=` 직접 선언으로만 문서화한다
-  [#63] application/orders/driving_layer/api/order/order_controller.py:23 `openapi_schema` monkeypatch — OpenAPI 를 사후 변형하지 않는다
+  [#63] application/orders/driving_layer/api/order/order_controller.py:15: `openapi_extra` 의 responses 보충 — 오류 응답은 `response={status: <Bc>ErrorSchema}` 로 직접 선언한다
+  [#63] application/orders/driving_layer/api/order/order_controller.py:19: `get_openapi_schema` override — 오류 응답은 operation 의 `response=` 직접 선언으로만 문서화한다
+  [#63] application/orders/driving_layer/api/order/order_controller.py:23: `openapi_schema` monkeypatch — OpenAPI 를 사후 변형하지 않는다
```

### check-response-schema-bypass.py — 구판 `f164dd9` (exit 2→2)

변경 2행:

```diff
--- check-response-schema-bypass.py@f164dd9
+++ check-response-schema-bypass.py@신판
@@ -2 +2 @@
-  - application/orders/driving_layer/api/order/order_controller.py: operation 'get_order@11' (:13 direct raw 200-203 response)
+  - application/orders/driving_layer/api/order/order_controller.py:13: operation 'get_order@11' — declared 200-203 schema bypassed by raw Django response
```

