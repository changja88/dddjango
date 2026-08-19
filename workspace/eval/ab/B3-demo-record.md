# B3 재생성 루프 시제품 — 1왕복 데모 기록 (2026-08-19, T0 B3)

> 기준(T0 계획 §3 B3): «폐루프 1왕복이 기계 산출물로 재현된다». 성능 수치가 아니다 — 수치는 §6 A/B 전용(§1 측정원 배정표).
> 규율: 주입 재료 = **번호+검사기 산출 발췌만**(동결 E8 — 규범 본문 정본 미동봉). 그래프 미경유(rule-owner-map T0 스냅숏 조인).

## 파이프라인

```
fixture 사본(domain_model/bad_rules) → check-domain-model.py(재저작본, DJR_FINDINGS_JSON 채널)
  → findings/0 레코드 61건 → regen_loop_prototype.py(스냅숏 조인 + 프롬프트 조립, 범위=order_pricing_service)
  → headless claude 1회(acceptEdits · 대상 파일만 수정 지시) → 같은 검사기 재실행
```

## before

- 레코드 61건 = violation 48 · info(ⓓ 후보) 13. 데모 범위(`domain_service/order_pricing_service.py`) violation **7건**.
- 조인: 범위 7건 전건 스냅숏 조인 성공(#302·#303·#304·#305·#307·#308·#310 → ⓒ scripts/check-domain-model.py).
- 조인 공백(선행 계약): 범위 내 0건. 별도 실증 — check-common-container 레코드는 rule=null+contract_ref로 방출되어 조인이 성립하지 않음(findings_smoke «CC-red rule=null+contract_ref 2건» 단언 ✓ — T2 이월: 선행 계약 7종의 IRI 처분).

## 주입 프롬프트 실물 (조립 출력 verbatim)

```
다음은 결정적 검사기가 잡은 규칙 위반 목록이다. 각 항목의 검사기 산출 발췌(번호·위치·사유)만이
수정 기준이다 — 규범 본문은 재주입하지 않는다. 위반이 난 파일만 수정하고, 무관한 코드는 건드리지 않는다.

- [#310] application/orders/domain_layer/domain_service/order_pricing_service.py — 공개 정의 6개 — 무상태 규칙 하나 = 파일 하나다  (담당: scripts/check-domain-model.py (신설))
- [#303] application/orders/domain_layer/domain_service/order_pricing_service.py:3 — `application.orders.domain_layer.order.entity.receipt` import — domain_service 는 루트·value_object·exception·형제 서비스만 import 한다  (담당: scripts/check-domain-model.py (신설))
- [#307] application/orders/domain_layer/domain_service/order_pricing_service.py:13 — `compute` 의 인자가 전부 원시 타입 — 그건 도메인 서비스가 아니라 계산 함수다(amount: Money 처럼 값 객체가 온다)  (담당: scripts/check-domain-model.py (신설))
- [#308] application/orders/domain_layer/domain_service/order_pricing_service.py:17 — `can_refund` 이 bool 을 돌려준다 — 규칙 위반의 알림은 «도메인 예외»다  (담당: scripts/check-domain-model.py (신설))
- [#304] application/orders/domain_layer/domain_service/order_pricing_service.py:21 — `repository` 가 리포지토리다 — 불러오거나 저장하면 그건 유스케이스다(Vernon 의 실례도 이 트리에선 유스케이스로 간다 — 3차 T24)  (담당: scripts/check-domain-model.py (신설))
- [#305] application/orders/domain_layer/domain_service/order_pricing_service.py:25 — `port` 가 포트다 — 재료는 유스케이스가 모아 «값으로» 넘긴다  (담당: scripts/check-domain-model.py (신설))
- [#302] application/orders/domain_layer/domain_service/order_pricing_service.py:6 — 모듈 레벨 가변 전역 — 도메인 서비스는 무상태다  (담당: scripts/check-domain-model.py (신설))

수정 후 같은 검사기를 재실행해 위 항목이 0이 되는지 확인한다.```

## 재생성·재검사 (after)

- 재생성: headless `claude -p` 1회, 대상 파일 한정 수정 지시.
- 재검사(같은 검사기): **범위 violation 7 → 0** · 전체 violation 48 → 41(범위 밖 41건 불변 — «무관한 코드는 건드리지 않는다» 준수 확인).
- 재생성 결과 파일(7행 — 원본 31행):

```python
from __future__ import annotations

from application.orders.domain_layer.order.value_object.money import Money, Rate


def compute(rate: Rate, amount: Money) -> Money:
    return Money(money_id=amount.money_id, amount=rate.value * amount.amount)
```

## 판정

1왕복(위반 레코드 → 조인 → 발췌 주입 → 재생성 → 재검사 green)이 기계 산출물로 재현됨 — B3 완료 기준 충족.
자동화 배선(coder 편입·수리 루프 회전 계상)은 T2 몫.
