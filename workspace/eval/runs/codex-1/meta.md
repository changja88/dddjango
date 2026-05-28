# codex-1 meta (PoC 보존본 — 참고용)

- 런타임/모델: Codex CLI 0.134.0 (GPT-5.5), `[features] multi_agent = true`
- 성격: **PoC 런**. 빌드 도중 역할 스킬을 증분 생성·재설치(16→19개)한 이력이 있어 *깨끗한 비교/결정성 표본 아님*. 구조·산출의 대략적 참고용으로만 사용.
- 입력: "재고가 있을 때만 주문을 생성하고 재고를 차감하는 기능."
- G0 배치: 옵션 1(기존 catalog, 최소 변경). 렌즈 ddd+db, api off.
- 산출 구조: **평면 catalog**(`catalog/{models,services,exceptions}.py` + `tests/{unit,integration}/`). application/ 4계층 아님.
  - `Product.deduct_stock(quantity)`, `Order.for_product(...)` classmethod, services.py, CheckConstraint 다수.
- 빌드 결과: migrate OK / check OK / test OK (16 tests).
- 알려진 관찰(DR-12): (1) 평면 catalog = `catalog 미정합`(§1 vs §0). (2) coder가 동시성 문제를 설계 반송 없이 sqlite 락 우회 자작(DR-06 축 재발) — 가드레일 Codex에서 약함.
- 토큰·시간: 미기록(요약값 미수집).

> 깨끗한 비교는 `codex-2`,`codex-3`(PROTOCOL.md 절차) 우선.
