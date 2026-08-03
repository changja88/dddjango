# FC 사전등록 산출물 v4 candidate — 골든 오라클 + mutation (EVAL-METHOD §1.4)

> **상태**: `candidate` · **NOT ACTIVE** · **NOT FROZEN** · **SCORING PROHIBITED**.
> 사용자 명시 freeze 전에는 골든 채점이나 mutation 판정을 실행하지 않는다.
> **결과 identity 규칙**: `epoch + error profile + rubric version + dimension ID`.
> 이 문서의 후보 값은 `2026-08-03-code-json + dddjango-code-json + v4-candidate + FC-{1|2|3}`다.
> v3 재현 locator full SHA: `d1fce5b43b13f8447b2a4b78f6c94e74efe8ff19`.
> **태스크-독립 행위표**(태스크 프롬프트+표준만으로 작성, fixture 코드 무관).
> **태스크**: "주문 생성 API — 요청 상품·수량의 주문 생성, catalog가 재고 소유·주문 시 차감(부족 시 409)."
> **표준 태스크 프롬프트 (라이브 입력 정본 · verbatim)**: `재고가 부족하면 409로 거절하고, 충분하면 차감하며 주문을 생성하는 API.` — 라이브 스모크는 `/dddjango` 뒤에 **이 한 줄만** 입력한다(동시성·멱등성은 넣지 않음 → G1 배너에서 architect가 제안). 최빈/표준형(finallive·nj7live·ptboot·ptcat)이 **정본**. 관측된 변형(계약은 동일 · 런 비교 채점 시 주의): 축약형 `재고 부족 409·충분 시 차감 주문 생성 API`(lastlive) / "충분하면 **재고를** 차감하며…"(dslive·cbvlive). ⚠️ 정리본 `scope.md`(coordinator가 Phase 0에서 확장한 "무엇/경계")는 raw 프롬프트가 **아니다** — 위 한 줄이 사용자 입력 원문.
> **출처**: 태스크 프롬프트 + architecture-api(상태코드)·architecture-ddd(재고 불변식). **fixture 코드는 보지 않고 작성**(순환 차단; §1.4). 등록 시각은 freeze 커밋 타임스탬프로 박제.
> **역할 분리**: 이 *행위표*는 작성자(적대 grader)가 코드 미열람으로 작성. *실행 어댑터*(route+payload 바인딩)는 픽스처마다 달라 **조정자가 코드 열람 후** 작성(§1.4 행위표⊥어댑터).

## 1. 골든 행위표 (FC-1) — 외부 행위 사전등록

| # | 입력 상태 | 요청 | 기대 status | 기대 부작용 |
|---|---|---|---|---|
| G1 | 상품 재고 10 | 그 상품 수량 3 주문 | **201** | 주문 1건 생성 ∧ 재고 **7** |
| G2 | 상품 재고 2 | 그 상품 수량 5 주문 | **409** | 주문 **0건** ∧ 재고 **불변(2)** |
| G3 | 상품 재고 5 (경계) | 그 상품 수량 5 주문 | **201** | 주문 1건 ∧ 재고 **0** |
| G4 | 상품 재고 5 | 그 상품 수량 6 주문 | **409** | 주문 0건 ∧ 재고 불변(5) |
| G5 | 존재하지 않는 상품 id | 수량 1 주문 | **404 또는 422** | 주문 0건 ∧ 재고 무변경 |
| G6 | 상품 재고 5 | 수량 0 또는 음수 | **422** | 주문 0건 ∧ 재고 불변 |

> **판정 바**: G1·G2가 핵심(재고 차감 *방향*·409 *거절*·부작용 원자성). G5의 404↔422는 api lens 재량(둘 다 허용). **하나라도 불일치 = FC-1 FAIL(치명).** "재고가 *늘어나는*" API(차감 부호 역전)는 G1에서 잔여=13으로 즉시 FAIL(CF-1 차단).

## 2. Mutation 3종 (FC-2) — 논리 정의 (사이트는 조정자가 코드 열람 후)

| ID | 논리 mutation | 기대(테스트 red여야 PASS) | 비고 |
|---|---|---|---|
| M1 | 차감 **부호 역전** (`stock -= qty` → `stock += qty`) | 재고 차감 테스트 red | 핵심 판정 메서드 내. DB CHECK constraint 아님 |
| M2 | 판정 **경계 변조** (`stock < qty` → `stock <= qty`, 또는 `>=`→`>`) | 경계(재고==수량) 테스트 red | G3 경계 케이스가 잡아야 |
| M3 | 오류 concrete ErrorOut의 `status` default 또는 BC base ErrorOut 직접 생성자의 `status`를 변조(예: `409` → `200`) | **HTTP status 단언과 body `status` 단언이 모두 red** | 해당 controller의 `Status`/error mapping |

> **주입 사이트**: M1·M2는 FC-1 골든이 두드리는 경로상의 **핵심 판정 메서드 1곳**,
> M3은 부족 오류를 직접 반환하는 **해당 controller의 `Status`/error mapping**이다.
> concrete `status` default와 BC base 직접 생성자 status 중 실제 경로가 쓰는 한 곳을 변조하고,
> HTTP status와 JSON body `status`가 함께 red인지 확인한다. 예외 handler는 주입 사이트가 아니다.
> **DB CHECK constraint(`stock__gte=0`)는 도메인 판정 아니므로 mutation 대상 제외.**
> v4가 freeze된 뒤에도 red율 100%가 아니면 FC-2 FAIL(vacuous 테스트)이며, 현재 candidate에서는
> 그 판정을 산출하지 않는다.

## 3. 픽스처별 실행 어댑터 (조정자 — 코드 열람 후 기록)
> 동일 태스크라도 BC 분해가 런마다 달라 route+payload가 갈림. 행위표(§1)는 공통, 아래만 픽스처별.

| 픽스처 | endpoint | payload(요청) | 재고 조회 |
|---|---|---|---|
| smoke4-codex | `POST /api/orders` | `{"product_id": <id>, "quantity": <n>}` | `catalog_product.stock` (`catalog.models.Product`) |
| smoke4-claude | `POST /api/orders` | `{"lines": [{"product_id": <id>, "quantity": <n>}]}` | `catalog_product.stock` (`ProductModel`, `application.catalog...`) |

> 다른 8벌은 채점 시점에 조정자가 동일 형식으로 추가(예: 일부 claude는 `reserve_stock`/`inventory` BC로 분해 → route 상이).
