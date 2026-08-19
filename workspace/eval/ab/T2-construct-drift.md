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

### check-composition-root.py — 구판 `e245b1e` (exit 2→2)

stdout **byte 무변**.

### check-context-isolation.py — 구판 `36bd09c` (exit 2→2)

stdout **byte 무변**.

### check-domain-model.py — 구판 `f164dd9` (exit 2→2)

stdout **byte 무변**.

### check-error-centralization.py — 구판 `1e887e3` (exit 2→2)

stdout **byte 무변**.

### check-openapi-error-declaration.py — 구판 `faea9d3` (exit 2→2)

stdout **byte 무변**.

### check-response-schema-bypass.py — 구판 `f164dd9` (exit 2→2)

변경 2행:

```diff
--- check-response-schema-bypass.py@f164dd9
+++ check-response-schema-bypass.py@신판
@@ -2 +2 @@
-  - application/orders/driving_layer/api/order/order_controller.py: operation 'get_order@11' (:13 direct raw 200-203 response)
+  - application/orders/driving_layer/api/order/order_controller.py:13: operation 'get_order@11' — declared 200-203 schema bypassed by raw Django response
```

