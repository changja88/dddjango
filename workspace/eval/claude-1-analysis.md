# claude-1 분석 (진행 중 — G1 설계까지)

> 대상: `/Users/hyun/Desktop/dddjango-smoke-claude/`(=Claude Code, dddjango v1.0.0 플러그인).
> 프롬프트·baseline·게이트(G0=catalog·plain Django·Django test) 모두 codex-2와 통제 일치.
> codex-2 대조용. 구현(G2) 완료 후 Q1 표·결함을 채운다.

## G1 설계 단계 대조 (codex-2 ↔ claude-1)

| 축 | codex-2 (Codex) | claude-1 (Claude) |
|---|---|---|
| 구조 | 완전 §0 4계층 | 완전 §0 4계층(§5.2) — **동등** |
| Django 통합 레시피 | label=catalog+db_table 도출 | §5.3 label=catalog 보존 명시 — **동등** |
| **B1(도메인 죽은 코드)** | 설계가 긴장 통과 → 구현서 `Product.reserve()` 죽음. 감사 놓침 | **DDD 리뷰어가 [blocker] 빈혈모델로 포착**(§8) → §1.4 "이중 방어선": 응용이 `Product.deduct()` **실제 호출** 후 조건부 UPDATE. 도메인 메서드 배선됨 |
| **stock≥0 CHECK** | 설계 요구 but 구현 누락 | §4.1 CHECK 추가 + §4.5 sqlite 재생성 위험·forward-fix까지. DB 리뷰어 [important] |
| DR-06 코더 가드 | 약함(PoC서 sqlite 락 자작) | §4.6 "coder 거짓 통과 방어" — 동시성 테스트 실행 모델 못박음(1차 결정적 권위, 2차 스레드 조건부) |
| total_price | 계산(미저장) | **저장 + CHECK** `total_price=unit_price*quantity`(I4 DB집행) |
| API 계약 | `/api/orders/`, 422, 415, 503 | `POST /orders`, 400 통일(422 없음), 415/503 미도입, **405 Allow:POST** |
| 멱등성 | 제외(명시) | 제외(§2.6 명시) — 동등 |
| 설계 자기점검 | §8 자기일관성 | §6 자기모순 스캔 + §8 lens별 리뷰 반영 추적 |

### 핵심 시사

1. **B1**: Claude 파이프라인은 같은 위험을 **DDD 리뷰가 blocker로 잡고 architect가 해소**(Product.deduct를 흐름에 배선). Codex는 G1 lens 리뷰·G2 discipline 감사 모두 통과시킴. → codex의 B1 감사 누락이 *순수 비결정성*보다 **리뷰 깊이 격차**일 가능성(각 1런이라 단정 보류, 결정성 추가런으로 확증 필요).
2. **stock≥0**: Claude 설계가 명시 + 마이그레이션 안전성까지. Codex는 설계만 하고 구현 누락. → 구현 단계 감사 격차도 별개 축.
3. **계약 차이는 양쪽 타당**(409 vs 422 분리 철학, total_price 저장 vs 계산, 503 도입 vs busy_timeout). 우열 아닌 설계 취향.

### G1 검증 — 구현 후 전부 이행 확인 (✅)
- [x] `Product.deduct()` 프로덕션 호출 — `place_order_app.py:50`(find_by_id로 Product 로드 후). **죽은 코드 아님**.
- [x] ProductModel + migration 0002에 `stock≥0` CHECK(`catalog_product_stock_gte_0`).
- [x] total_price 저장 + CHECK(`total_price=unit_price*quantity`).
- [x] §4.6 결정적 동시성 테스트(`test_oversell_deterministic.py` — 조건부 UPDATE 2회 rowcount 1/0).
- [x] 405 + `Allow: POST`(`api_order.py`).
- [x] #2 race 수정 반영(rowcount=0 시 DB 재조회로 available_stock 보고).
- 테스트 40개(unit 24·integration 16). 토큰·시간 미수집(요약값 수기 대상).

## 추가 구현 강점 (codex 대비)
- `find_by_id()->Optional[Product]`로 ORM↔도메인 매핑(codex는 누수 tuple 포트).
- 503/sqlite 문자열 매칭 결합 없음(codex `_is_database_busy` 중복·취약과 대조).
- presentation `error_out` 모듈로 Problem Details 빌더 분리(codex는 뷰 인라인 구성).
- 평면 catalog 완전 제거(codex는 빈 `catalog/migrations` 잔존).

> 최종 1:1 종합·판정·한계는 `RESULTS.md`.
